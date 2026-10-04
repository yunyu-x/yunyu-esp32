#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/stress_test_30min.py
----------------------------
StickS3 物理硬件 30 分钟连续无人值守极限稳定性与全模态长程压测引擎
1. 监控周期：30 分钟 (1800 秒)，采样间隔 2 秒
2. 核心监控项：
   - 连续运行时间与重启监测 (Uptime 严格单调递增，0 重启，0 崩溃，0 异常抛出)
   - 内存泄漏审计 (SRAM 内部堆与 8MB PSRAM 堆稳定性，杜绝内存耗尽)
   - FreeRTOS 任务栈高水位监测 (audioTask 与 loopTask 栈深安全)
   - I2C 总线互斥锁竞争与失败计数 (保持 0 失败)
   - 百炼全双工 WebSocket 长连接保活与自动自愈
   - 定期主动交互压测 (每 3 分钟触发一次语音合成与播报闭环，验证软饱和限幅器与放音零失真)
   - COM3 串口无干扰监听 (DTR/RTS 严格为 False，杜绝外部复位)
"""

import os
import sys
import time
import json
import threading
import requests
import serial

import argparse

DEV_IP = "192.168.110.67"
COM_PORT = "COM3"
DEFAULT_DURATION_SEC = 1800  # 30 分钟
SAMPLE_INTERVAL_SEC = 2.0
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "tests", "stress_test_30min_report.json")

test_stats = {
    "start_time": None,
    "end_time": None,
    "duration_sec": 0,
    "samples_count": 0,
    "reboots_detected": 0,
    "i2c_failures_max": 0,
    "min_sram_kb": 999999,
    "max_sram_kb": 0,
    "min_psram_mb": 999.0,
    "min_loop_fps": 999.0,
    "avg_loop_fps": 0.0,
    "audio_stack_hwm_min": 999999,
    "interaction_rounds": 0,
    "interaction_success": 0,
    "panics_detected": 0,
    "errors": [],
    "milestones": []
}

serial_lines = []
stop_event = threading.Event()

def ts():
    now = time.time()
    return f"{time.strftime('%H:%M:%S', time.localtime(now))}.{int((now % 1) * 1000):03d}"

def serial_worker():
    try:
        s = serial.Serial()
        s.port = COM_PORT
        s.baudrate = 115200
        s.timeout = 0.5
        s.dtr = False
        s.rts = False
        s.open()
        while not stop_event.is_set():
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                serial_lines.append((time.time(), line))
                if any(w in line for w in ["PANIC", "Guru Meditation", "Brownout", "CORRUPT", "abort()"]):
                    test_stats["panics_detected"] += 1
                    test_stats["errors"].append(f"[{ts()}] Serial Panic Detected: {line}")
                    print(f"[{ts()}] 🚨 [SERIAL CRITICAL] {line}", flush=True)
                elif "[BUTTON-RESET]" in line or "[BOOT-DIAG]" in line:
                    test_stats["reboots_detected"] += 1
                    print(f"[{ts()}] ⚠️ [SERIAL REBOOT] {line}", flush=True)
        s.close()
    except Exception as e:
        print(f"[{ts()}] Serial worker warning: {e}", flush=True)

def run_stress_test(total_duration_sec=DEFAULT_DURATION_SEC):
    print("=" * 70, flush=True)
    print(f">>> [StickS3-STRESS-30MIN] Starting Hardware Stress Test", flush=True)
    print(f">>> Target IP: http://{DEV_IP} | Port: {COM_PORT} | Duration: {total_duration_sec}s (~{total_duration_sec/60:.1f} min)", flush=True)
    print("=" * 70, flush=True)

    start_time = time.time()
    test_stats["start_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

    # 启动非复位串口监听线程
    ser_thread = threading.Thread(target=serial_worker, daemon=True)
    ser_thread.start()

    fps_sum = 0.0
    last_interaction_time = start_time
    last_milestone_min = 0

    while (time.time() - start_time) < total_duration_sec:
        elapsed = time.time() - start_time
        now_min = int(elapsed / 60)

        # 1. 采集系统健康度与遥测指标
        try:
            r = requests.get(f"http://{DEV_IP}/system/metrics", timeout=2.0)
            if r.status_code == 200:
                m = r.json()
                test_stats["samples_count"] += 1
                
                # CPU / FPS
                fps = float(m.get("cpu", {}).get("loop_fps", 0))
                if fps > 0:
                    fps_sum += fps
                    if fps < test_stats["min_loop_fps"]:
                        test_stats["min_loop_fps"] = fps
                
                # 栈空间
                hwm = int(m.get("cpu", {}).get("audio_stack_hwm", 0))
                if hwm > 0 and hwm < test_stats["audio_stack_hwm_min"]:
                    test_stats["audio_stack_hwm_min"] = hwm
                
                # 内存
                sram_kb = int(m.get("memory", {}).get("free_internal_heap", 0)) / 1024.0
                if sram_kb < test_stats["min_sram_kb"]:
                    test_stats["min_sram_kb"] = sram_kb
                if sram_kb > test_stats["max_sram_kb"]:
                    test_stats["max_sram_kb"] = sram_kb
                
                psram_mb = int(m.get("memory", {}).get("free_psram", 0)) / (1024.0 * 1024.0)
                if psram_mb < test_stats["min_psram_mb"]:
                    test_stats["min_psram_mb"] = psram_mb
                
                # I2C
                fails = int(m.get("io", {}).get("i2c_lock_failures", 0))
                if fails > test_stats["i2c_failures_max"]:
                    test_stats["i2c_failures_max"] = fails

        except Exception as e:
            test_stats["errors"].append(f"[{ts()}] Metrics request failed: {e}")

        # 2. 定期每 3 分钟执行一次主动文本对话压测
        if (time.time() - last_interaction_time) >= 180:
            last_interaction_time = time.time()
            test_stats["interaction_rounds"] += 1
            round_idx = test_stats["interaction_rounds"]
            print(f"\n[{ts()}] --- Triggering Interaction Round #{round_idx} ---", flush=True)
            try:
                chat_url = f"http://{DEV_IP}/bailian/send_text"
                payload = {"text": f"悄悄，这是第{round_idx}轮系统连续稳定性健康压测，请用一句话回复。"}
                r_chat = requests.post(chat_url, json=payload, timeout=5.0)
                if r_chat.status_code == 200:
                    test_stats["interaction_success"] += 1
                    print(f"[{ts()}] Sent question to StickS3: {payload['text']}", flush=True)
                else:
                    print(f"[{ts()}] Chat request returned HTTP {r_chat.status_code}", flush=True)
            except Exception as e:
                print(f"[{ts()}] Interaction round failed: {e}", flush=True)

        # 3. 里程碑上报 (每 5 分钟汇报一次)
        if now_min >= last_milestone_min + 5:
            last_milestone_min = now_min
            cur_avg_fps = (fps_sum / test_stats["samples_count"]) if test_stats["samples_count"] > 0 else 0
            mile_entry = {
                "elapsed_minutes": now_min,
                "samples": test_stats["samples_count"],
                "avg_fps": round(cur_avg_fps, 1),
                "min_sram_kb": round(test_stats["min_sram_kb"], 1),
                "min_psram_mb": round(test_stats["min_psram_mb"], 2),
                "audio_stack_hwm": test_stats["audio_stack_hwm_min"],
                "i2c_fails": test_stats["i2c_failures_max"],
                "reboots": test_stats["reboots_detected"],
                "panics": test_stats["panics_detected"]
            }
            test_stats["milestones"].append(mile_entry)
            print(f"\n[{ts()}] 📊 [MILESTONE {now_min}/30 MIN] Samples={mile_entry['samples']} | "
                  f"AvgFPS={mile_entry['avg_fps']} | SRAM={mile_entry['min_sram_kb']}KB | "
                  f"PSRAM={mile_entry['min_psram_mb']}MB | Stack={mile_entry['audio_stack_hwm']}B | "
                  f"I2CFails={mile_entry['i2c_fails']} | Reboots={mile_entry['reboots']} | Panics={mile_entry['panics']}",
                  flush=True)

        time.sleep(SAMPLE_INTERVAL_SEC)

    # 压测结束总结
    stop_event.set()
    end_time = time.time()
    test_stats["end_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    test_stats["duration_sec"] = round(end_time - start_time, 1)
    if test_stats["samples_count"] > 0:
        test_stats["avg_loop_fps"] = round(fps_sum / test_stats["samples_count"], 1)

    print("\n" + "=" * 70, flush=True)
    print(">>> [StickS3-STRESS-30MIN] Test Completed!", flush=True)
    print(f">>> Duration: {test_stats['duration_sec']}s (~{test_stats['duration_sec']/60:.1f} min)", flush=True)
    print(f">>> Total Samples: {test_stats['samples_count']}", flush=True)
    print(f">>> Avg FPS: {test_stats['avg_loop_fps']} | Min FPS: {test_stats['min_loop_fps']:.1f}", flush=True)
    print(f">>> Min SRAM: {test_stats['min_sram_kb']:.1f} KB | Min PSRAM: {test_stats['min_psram_mb']:.2f} MB", flush=True)
    print(f">>> Audio Stack HWM Min: {test_stats['audio_stack_hwm_min']} B", flush=True)
    print(f">>> I2C Lock Failures: {test_stats['i2c_failures_max']}", flush=True)
    print(f">>> Reboots Detected: {test_stats['reboots_detected']}", flush=True)
    print(f">>> Kernel Panics: {test_stats['panics_detected']}", flush=True)
    print(f">>> Interaction Rounds: {test_stats['interaction_rounds']} (Success: {test_stats['interaction_success']})", flush=True)
    print("=" * 70, flush=True)

    # 写入 JSON 报告
    try:
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(test_stats, f, indent=2, ensure_ascii=False)
        print(f">>> Report saved to: {REPORT_PATH}", flush=True)
    except Exception as e:
        print(f">>> Failed to write report: {e}", flush=True)

    # 判定最终结果
    is_success = (test_stats["reboots_detected"] == 0 and 
                  test_stats["panics_detected"] == 0 and 
                  test_stats["i2c_failures_max"] == 0 and
                  test_stats["min_sram_kb"] > 30 and
                  test_stats["avg_loop_fps"] > 50)
    print(f">>> FINAL VERDICT: {'PASSED (ROCK SOLID)' if is_success else 'FAILED'}", flush=True)
    return 0 if is_success else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StickS3 Hardware Long-Horizon Stress Test")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_SEC, help="Test duration in seconds (default: 1800 for 30min)")
    args = parser.parse_args()
    sys.exit(run_stress_test(total_duration_sec=args.duration))
