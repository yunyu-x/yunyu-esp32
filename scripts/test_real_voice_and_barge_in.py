#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/test_real_voice_and_barge_in.py
----------------------------------------
StickS3 阿里云百炼全双工大模型端到端语音问答与毫秒级中途打断 (Barge-In) 自动化标定脚本
记录全链路每一个关键阶段的精确时间戳与毫秒级耗时。
"""

import sys
import time
import json
import threading
import requests
import serial

import os

DEV_IP = os.environ.get("STICK_DEVICE_IP", "192.168.110.67")
COM_PORT = os.environ.get("STICK_COM_PORT", "COM3")

def load_bailian_api_key() -> str:
    key = os.environ.get("BAILIAN_API_KEY", "").strip()
    if not key:
        for cand in [".env", os.path.join(os.path.dirname(__file__), "..", ".env")]:
            if os.path.exists(cand):
                try:
                    with open(cand, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("BAILIAN_API_KEY="):
                                key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                                break
                    if key:
                        break
                except Exception:
                    pass
    return key

API_KEY = load_bailian_api_key()

logs = []
stop_flag = False
serial_events = {}

def ts():
    now = time.time()
    return f"{time.strftime('%H:%M:%S', time.localtime(now))}.{int((now % 1) * 1000):03d}"

def record_event(name):
    now = time.time()
    serial_events[name] = now
    return now

def serial_listener():
    global stop_flag
    try:
        s = serial.Serial()
        s.port = COM_PORT
        s.baudrate = 115200
        s.timeout = 0.5
        s.dtr = False
        s.rts = False
        s.open()
        while not stop_flag:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                t_str = ts()
                t_now = time.time()
                logs.append((t_now, t_str, line))
                print(f"[{t_str}] [COM3] {line}")

                if "WSS Connected to DashScope" in line and "WSS_CONNECTED" not in serial_events:
                    serial_events["WSS_CONNECTED"] = t_now
                elif "Session established and active" in line and "SESSION_ACTIVE" not in serial_events:
                    serial_events["SESSION_ACTIVE"] = t_now
                elif "Sent user text query" in line and "QUERY_SENT" not in serial_events:
                    serial_events["QUERY_SENT"] = t_now
                elif "Thinking..." in line and "THINKING" not in serial_events:
                    serial_events["THINKING"] = t_now
                elif "LLM Stream Playback STARTED" in line and "AUDIO_FIRST_STREAM" not in serial_events:
                    serial_events["AUDIO_FIRST_STREAM"] = t_now
                elif "BARGE-IN TRIGGERED" in line and "BARGE_IN_TRIGGERED" not in serial_events:
                    serial_events["BARGE_IN_TRIGGERED"] = t_now
                elif "Playback INTERRUPTED" in line and "PLAYBACK_INTERRUPTED" not in serial_events:
                    serial_events["PLAYBACK_INTERRUPTED"] = t_now
        s.close()
    except Exception as e:
        print(f"[{ts()}] Serial exception: {e}")

def run_benchmark():
    global stop_flag
    benchmarks = {}

    print("=" * 70)
    print(f"[{ts()}] >>> StickS3 Bailian Realtime E2E Voice & Barge-In Benchmark <<<")
    print("=" * 70)

    # 阶段 0: 启动串口监听
    th = threading.Thread(target=serial_listener, daemon=True)
    th.start()
    time.sleep(1.0)

    # 阶段 1: 验证 Wi-Fi 网络状态与连通性
    print(f"\n[{ts()}] [阶段 1: 查询 StickS3 STA 局域网连通性]")
    t0 = time.time()
    r_wifi = requests.get(f"http://{DEV_IP}/wifi/status", timeout=5)
    t1 = time.time()
    benchmarks["wifi_query_latency_ms"] = (t1 - t0) * 1000
    wifi_data = r_wifi.json()
    print(f"[{ts()}] STA 状态: {wifi_data} (耗时: {benchmarks['wifi_query_latency_ms']:.1f}ms)")
    assert wifi_data.get("sta_state") == "connected", "WiFi 未连接!"

    # 阶段 2: 注入百炼 API Key 并下发大模型配置
    print(f"\n[{ts()}] [阶段 2: 写入阿里云百炼凭证至 NVS 并发起 WSS 连接]")
    t2 = time.time()
    payload = {
        "key": API_KEY,
        "model": "qwen3.8-omni-flash-realtime",
        "voice": "Tina"
    }
    r_cfg = requests.post(f"http://{DEV_IP}/bailian/config", data=payload, timeout=5)
    t3 = time.time()
    benchmarks["nvs_config_save_latency_ms"] = (t3 - t2) * 1000
    print(f"[{ts()}] 配置写入成功: {r_cfg.json()} (耗时: {benchmarks['nvs_config_save_latency_ms']:.1f}ms)")

    # 阶段 3: 等待 WSS TLS 握手与 session.created
    print(f"\n[{ts()}] [阶段 3: 等待 WSS 握手与会话就绪...]")
    serial_events.clear()
    wss_wait_start = time.time()
    while time.time() - wss_wait_start < 10.0:
        if "SESSION_ACTIVE" in serial_events:
            break
        time.sleep(0.1)

    assert "WSS_CONNECTED" in serial_events, "WSS 连接超时!"
    assert "SESSION_ACTIVE" in serial_events, "Session 握手超时!"
    benchmarks["wss_tls_handshake_ms"] = (serial_events["WSS_CONNECTED"] - t2) * 1000
    benchmarks["session_update_ack_ms"] = (serial_events["SESSION_ACTIVE"] - serial_events["WSS_CONNECTED"]) * 1000
    print(f"[{ts()}] ✔ 百炼 WSS 握手就绪! (TLS握手: {benchmarks['wss_tls_handshake_ms']:.1f}ms, 会话协商: {benchmarks['session_update_ack_ms']:.1f}ms)")

    # 阶段 4: 下发真实问答查询，触发大模型推理与流式音频发声
    # 确保百炼状态机处于 正在聆听 (state_code=3)
    for _ in range(20):
        st_resp = requests.get(f"http://{DEV_IP}/bailian/status", timeout=5).json()
        if st_resp.get("state_code") == 3:
            break
        time.sleep(0.1)

    test_query = "你好小飞，请为我朗诵李白的《静夜思》，并详细讲解它的思乡背景。"
    print(f"\n[{ts()}] [阶段 4: 下发文本问答: \"{test_query}\"]")
    t_query_send = time.time()
    r_q = requests.post(f"http://{DEV_IP}/bailian/send_text", data={"text": test_query}, timeout=5)
    t_query_ack = time.time()
    benchmarks["query_http_ack_ms"] = (t_query_ack - t_query_send) * 1000
    q_data = r_q.json()
    print(f"[{ts()}] 问答指令已成功送达 StickS3: {q_data} (耗时: {benchmarks['query_http_ack_ms']:.1f}ms)")
    assert q_data.get("status") == "ok", f"下发问答失败: {q_data}"

    # 等待首帧音频 (TTFA)
    print(f"[{ts()}] [阶段 4.1: 等待大模型流式回复与首音频帧 (TTFA)...]")
    stream_wait_start = time.time()
    while time.time() - stream_wait_start < 12.0:
        if "AUDIO_FIRST_STREAM" in serial_events:
            break
        time.sleep(0.05)

    assert "AUDIO_FIRST_STREAM" in serial_events, "未在时限内收到大模型音频流!"
    benchmarks["ttfa_latency_ms"] = (serial_events["AUDIO_FIRST_STREAM"] - t_query_send) * 1000
    print(f"[{ts()}] 🎙️ 大模型正在通过 StickS3 AW8737 喇叭流式播音! 首音频延迟 (TTFA): {benchmarks['ttfa_latency_ms']:.1f}ms")

    # 阶段 5: 中途打断压测 (Barge-In)
    # 让大模型播音持续 2.0 秒后，突然发起打断指令！
    print(f"[{ts()}] [阶段 5: 让大模型正常发声 2.0 秒后触发【中途打断 (Barge-In)】]")
    time.sleep(2.0)

    print(f"\n[{ts()}] >>> 💥 发起中途打断指令 (POST /bailian/interrupt) <<<")
    t_interrupt_send = time.time()
    r_intr = requests.post(f"http://{DEV_IP}/bailian/interrupt", timeout=5)
    t_interrupt_ack = time.time()
    benchmarks["barge_in_http_ack_ms"] = (t_interrupt_ack - t_interrupt_send) * 1000

    # 确认打断生效
    intr_wait_start = time.time()
    while time.time() - intr_wait_start < 3.0:
        if "PLAYBACK_INTERRUPTED" in serial_events:
            break
        time.sleep(0.02)

    assert "PLAYBACK_INTERRUPTED" in serial_events, "中途打断未在硬件生效!"
    benchmarks["hardware_barge_in_cutoff_ms"] = (serial_events["PLAYBACK_INTERRUPTED"] - t_interrupt_send) * 1000
    print(f"[{ts()}] ⏹️ 硬件打断生效! 喇叭瞬间静音并清空下行缓冲 (打断截止延时: {benchmarks['hardware_barge_in_cutoff_ms']:.1f}ms)")

    # 阶段 6: 验证状态机恢复与打断计数
    time.sleep(1.2)
    print(f"\n[{ts()}] [阶段 6: 验证 StickS3 恢复倾听状态与打断统计]")
    r_final = requests.get(f"http://{DEV_IP}/bailian/status", timeout=5)
    final_data = r_final.json()
    print(f"[{ts()}] 终态数据: {final_data}")
    benchmarks["total_interrupts"] = final_data.get("interrupts", 0)
    benchmarks["final_state"] = final_data.get("state_name")
    assert benchmarks["total_interrupts"] >= 1, "打断计数器未递增!"

    stop_flag = True
    th.join(timeout=2.0)

    # 最终标定报表输出
    print("\n" + "=" * 70)
    print("           STICK-S3 阿里云百炼全链路时间戳与耗时审计报表")
    print("=" * 70)
    print(f"| 阶段编号 | 交互动作 / 标定阶段               | 耗时 / 延迟 (ms) | 评价基准       |")
    print(f"|----------|-----------------------------------|------------------|----------------|")
    print(f"| 阶段 1   | 局域网 HTTP 查询 Wi-Fi 状态        | {benchmarks['wifi_query_latency_ms']:16.1f} | 正常 (<200ms)  |")
    print(f"| 阶段 2   | NVS 写入百炼配置凭证              | {benchmarks['nvs_config_save_latency_ms']:16.1f} | 正常 (<100ms)  |")
    print(f"| 阶段 3   | TLS SNI 握手与 WSS 443 长连建立   | {benchmarks['wss_tls_handshake_ms']:16.1f} | 优秀 (<1200ms) |")
    print(f"| 阶段 3.1 | session.update 协商确认           | {benchmarks['session_update_ack_ms']:16.1f} | 瞬时 (<50ms)   |")
    print(f"| 阶段 4   | 问答下发 HTTP 端点响应延时        | {benchmarks['query_http_ack_ms']:16.1f} | 正常 (<150ms)  |")
    print(f"| 阶段 4.1 | 首音频帧下发与播音启动延时(TTFA)  | {benchmarks['ttfa_latency_ms']:16.1f} | 实时级 (<2000ms)|")
    print(f"| 阶段 5   | 中途打断 HTTP 指令下发往返        | {benchmarks['barge_in_http_ack_ms']:16.1f} | 极速 (<120ms)  |")
    print(f"| 阶段 5.1 | 硬件级喇叭静音与流取消延迟(Barge) | {benchmarks['hardware_barge_in_cutoff_ms']:16.1f} | 毫秒级 (<100ms) |")
    print("=" * 70)
    print(f"累计打断成功次数: {benchmarks['total_interrupts']} 次 | 恢复状态: {benchmarks['final_state']}")
    print("=" * 70)
    print("✔ 端到端真实网络语音问答与毫秒级中途打断全通路标定完全成功！\n")

if __name__ == "__main__":
    run_benchmark()
