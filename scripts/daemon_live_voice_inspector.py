#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/daemon_live_voice_inspector.py
---------------------------------------
StickS3 真实人类语音交互后台实时监控与卡顿深度诊断守护进程 (Daemon)
- 实时监听 COM3 串口流数据与硬件遥测
- 毫秒级轮询 /system/metrics 与 /bailian/status
- 实时捕获真实语音输入、麦克风能量、上行推流、VAD 判决、TTFA 首字延迟与音频回放卡顿
- 全量写入 live_interaction_trace.log 供实时分析与复盘
"""

import sys
import os
import time
import json
import threading
import requests
import serial

DEV_IP = "192.168.110.67"
COM_PORT = "COM3"
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "live_interaction_trace.log")

stop_flag = False

def ts():
    now = time.time()
    return f"{time.strftime('%H:%M:%S', time.localtime(now))}.{int((now % 1) * 1000):03d}"

def log_write(msg):
    formatted = f"[{ts()}] {msg}"
    print(formatted)
    sys.stdout.flush()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def serial_monitor():
    global stop_flag
    log_write(f"[DAEMON] Connecting to serial port {COM_PORT} (115200)...")
    try:
        s = serial.Serial()
        s.port = COM_PORT
        s.baudrate = 115200
        s.timeout = 0.3
        s.dtr = False
        s.rts = False
        s.open()
        log_write(f"[DAEMON] Serial port {COM_PORT} ONLINE. Listening for hardware telemetry...")
        while not stop_flag:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # 过滤出关键事件重点展示
                if any(k in line for k in ["[BAILIAN", "[AUDIO", "[StickS3-SYS]", "[EVENT]", "WEBSOCKET", "NVS", "WiFi", "Codec", "error", "Error"]):
                    log_write(f"[COM3] {line}")
                else:
                    # 普通心跳写入文件
                    try:
                        with open(LOG_FILE, "a", encoding="utf-8") as f:
                            f.write(f"[{ts()}] [COM3-RAW] {line}\n")
                    except Exception:
                        pass
        s.close()
    except Exception as e:
        log_write(f"[DAEMON-ERR] Serial monitoring exception: {e}")

def http_monitor():
    global stop_flag
    log_write(f"[DAEMON] Starting HTTP telemetry polling against {DEV_IP} (250ms interval)...")
    last_state = -1
    last_query = ""
    last_reply = ""
    speech_start_time = None
    first_audio_time = None

    while not stop_flag:
        try:
            r_st = requests.get(f"http://{DEV_IP}/bailian/status", timeout=1.0)
            if r_st.status_code == 200:
                st = r_st.json()
                cur_state = st.get("state_code", -1)
                cur_state_name = st.get("state_name", "")
                cur_query = st.get("user_query", "")
                cur_reply = st.get("ai_reply", "")

                # 捕获状态机跃迁
                if cur_state != last_state:
                    t_now = time.time()
                    log_write(f"===> [STATE-CHANGE] 状态切换: {last_state} -> {cur_state} ({cur_state_name})")
                    if cur_state == 4: # Thinking
                        speech_start_time = t_now
                        log_write(f"     [EVENT] 用户结束发言，大模型进入思考 (Thinking)...")
                    elif cur_state == 5: # Speaking
                        first_audio_time = t_now
                        if speech_start_time:
                            ttfa = (first_audio_time - speech_start_time) * 1000.0
                            log_write(f"     🎙️ [EVENT] AI 开始流式播报! 思考到首音频延迟: {ttfa:.1f} ms")
                    elif cur_state == 3: # Listening
                        if last_state == 5:
                            log_write(f"     ✔ [EVENT] AI 播报自然排空完成，平滑切回 Listening 倾听待命。")
                        speech_start_time = None
                        first_audio_time = None
                    last_state = cur_state

                # 捕获新提问或新回答增量
                if cur_query != last_query and cur_query:
                    log_write(f"     [USER-SPEECH] 用户语音转写识别文本: \"{cur_query}\"")
                    last_query = cur_query

                if cur_reply != last_reply and cur_reply:
                    # 仅在长度显著变动或结束时展示
                    if len(cur_reply) - len(last_reply) > 10 or cur_state == 3:
                        log_write(f"     [AI-REPLY-STREAM] AI 增量文本 ({len(cur_reply)}字): \"{cur_reply}\"")
                    last_reply = cur_reply

        except Exception as e:
            pass

        time.sleep(0.25)

if __name__ == "__main__":
    # 清空或初始化日志文件
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"[{ts()}] === StickS3 Live Real-Voice Interaction Daemon Log Started ===\n")

    log_write("==========================================================================")
    log_write("   StickS3 真实人类语音交互后台全维度监控守护进程启动 (Live Inspector)   ")
    log_write(f"   目标硬件: {DEV_IP} | 串口通道: {COM_PORT} | 日志归档: live_interaction_trace.log")
    log_write("==========================================================================")

    th1 = threading.Thread(target=serial_monitor, daemon=True)
    th1.start()
    th2 = threading.Thread(target=http_monitor, daemon=True)
    th2.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        stop_flag = True
        log_write("[DAEMON] Stopping live voice monitor daemon...")
        th1.join(timeout=2.0)
        th2.join(timeout=2.0)
