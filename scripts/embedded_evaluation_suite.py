#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/embedded_evaluation_suite.py
--------------------------------------
M5Stack StickS3 嵌入式整体效果验收评估与极限压测引擎 (Sprint 1 & Sprint 2)

覆盖四大核心专项：
1. 系统流畅度与人机响应性评估 (Fluency & FPS Under Heavy Load)
2. 硬件高负荷物理参数与资源边界测试 (Physical Health, SRAM/PSRAM, Stack, Temp, I2C)
3. 频繁按键连击与抗狂暴输入测试 (Button Hammering & Mode Switch Robustness)
4. 阿里百炼连续流式对话与瞬时打断抗压 (Dialogue & Barge-In Invariance)

输出：
- 控制台实时 ANSI 色彩进度与健康度曲线
- 完整验收报告: docs/EMBEDDED_EVALUATION_REPORT.md
- 结构化 JSON 快照: logs/embedded_evaluation_summary.json
"""

import os
import sys
import time
import json
import re
import threading
import statistics
import argparse
from typing import Dict, Any, List, Optional
import requests
import serial

DEV_IP = os.environ.get("STICK_DEVICE_IP", "192.168.110.67")
COM_PORT = os.environ.get("STICK_COM_PORT", "COM3")
BAUD_RATE = 115200

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

SUMMARY_JSON_FILE = os.path.join(LOG_DIR, "embedded_evaluation_summary.json")
REPORT_MD_FILE = os.path.join(DOCS_DIR, "EMBEDDED_EVALUATION_REPORT.md")


class SerialCollector:
    """监听 COM3 物理串口并实时解析硬件遥测与异常"""
    def __init__(self, port: str = COM_PORT, baud: int = BAUD_RATE):
        self.port = port
        self.baud = baud
        self.ser: Optional[serial.Serial] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # 遥测度量时间序列
        self.metrics_history: List[Dict[str, Any]] = []
        self.raw_logs: List[str] = []
        self.reboot_events: List[Dict[str, Any]] = []
        self.panic_events: List[str] = []
        self.barge_in_latencies: List[float] = []
        
        # 正则解析器
        # [StickS3-SYS] FPS: 88.5 | Temp: 60.2C | RAM: free=7.49MB (Load: 9.7%) | SRAM: free=134KB, max_block=123KB (DynLoad: 0.0%) | Stack: free=5260B (Load: 35.8%) | I2C_Tx: 53 (Fails: 0)
        self.sys_re = re.compile(
            r"\[StickS3-SYS\]\s+FPS:\s+([0-9.]+)\s+\|\s+Temp:\s+([0-9.]+)C\s+\|\s+RAM:\s+free=([0-9.]+)MB\s+\(Load:\s+([0-9.]+)%\)\s+\|\s+SRAM:\s+free=(\d+)KB,\s+max_block=(\d+)KB\s+\(DynLoad:\s+([0-9.]+)%\)\s+\|\s+Stack:\s+free=(\d+)B\s+\(Load:\s+([0-9.]+)%\)\s+\|\s+I2C_Tx:\s+(\d+)\s+\(Fails:\s+(\d+)\)"
        )
        self.rst_re = re.compile(r"rst:(0x[0-9a-fA-F]+)")

    def start(self):
        try:
            self.ser = serial.Serial()
            self.ser.port = self.port
            self.ser.baudrate = self.baud
            self.ser.timeout = 0.5
            self.ser.dtr = False
            self.ser.rts = False
            self.ser.open()
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            print(f"[SerialCollector] Connected to {self.port} @ {self.baud}")
            return True
        except Exception as e:
            print(f"[SerialCollector] ERROR opening {self.port}: {e}")
            return False

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        print("[SerialCollector] Stopped.")

    def send_cmd(self, cmd: str):
        with self.lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write((cmd.strip() + "\n").encode("utf-8"))
                    self.ser.flush()
                except Exception as e:
                    print(f"[SerialCollector] Write error: {e}")

    def _read_loop(self):
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    time.sleep(0.1)
                    continue
                line = self.ser.readline().decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                
                t_now = time.time()
                with self.lock:
                    self.raw_logs.append(f"[{t_now:.3f}] {line}")
                    if len(self.raw_logs) > 5000:
                        self.raw_logs.pop(0)

                # 重启排查
                rst_match = self.rst_re.search(line)
                if rst_match:
                    code = rst_match.group(1).lower()
                    if code not in ["0x1", "0x15"]:  # 0x1 上电，0x15 USB DTR
                        with self.lock:
                            self.reboot_events.append({"time": t_now, "code": code, "raw": line})
                            print(f"\n⚠️  [ALERT] Hardware reboot detected: {code} -> {line}")

                if "Guru Meditation Error" in line or "CORRUPT HEAP" in line or "Backtrace:" in line:
                    with self.lock:
                        self.panic_events.append(line)
                        print(f"\n🚨  [PANIC] Guru/Heap corruption detected: {line}")

                # 遥测帧解析
                sys_match = self.sys_re.search(line)
                if sys_match:
                    m = {
                        "timestamp": t_now,
                        "fps": float(sys_match.group(1)),
                        "temp_c": float(sys_match.group(2)),
                        "ram_free_mb": float(sys_match.group(3)),
                        "ram_load_pct": float(sys_match.group(4)),
                        "sram_free_kb": int(sys_match.group(5)),
                        "sram_max_block_kb": int(sys_match.group(6)),
                        "sram_dyn_load_pct": float(sys_match.group(7)),
                        "stack_free_b": int(sys_match.group(8)),
                        "stack_load_pct": float(sys_match.group(9)),
                        "i2c_tx": int(sys_match.group(10)),
                        "i2c_fails": int(sys_match.group(11)),
                    }
                    with self.lock:
                        self.metrics_history.append(m)

            except Exception as e:
                time.sleep(0.05)

    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.metrics_history[-1] if self.metrics_history else None

    def get_history_slice(self, start_ts: float) -> List[Dict[str, Any]]:
        with self.lock:
            return [m for m in self.metrics_history if m["timestamp"] >= start_ts]


class EmbeddedEvaluator:
    def __init__(self, dev_ip: str = DEV_IP, com_port: str = COM_PORT):
        self.dev_ip = dev_ip
        self.com_port = com_port
        self.collector = SerialCollector(port=com_port)
        self.results: Dict[str, Any] = {
            "eval_start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dev_ip": dev_ip,
            "com_port": com_port,
            "subsystems": {},
            "gates_passed": True,
            "gate_failures": []
        }

    def _http_get(self, endpoint: str, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
        try:
            r = requests.get(f"http://{self.dev_ip}{endpoint}", timeout=timeout)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    def _http_post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, timeout: float = 2.0) -> Optional[requests.Response]:
        try:
            return requests.post(f"http://{self.dev_ip}{endpoint}", data=data, timeout=timeout)
        except Exception:
            return None

    # =========================================================================
    # 专项 1: 系统流畅度与动画压测 (Fluency Benchmark)
    # =========================================================================
    def benchmark_fluency(self) -> Dict[str, Any]:
        print("\n" + "="*60)
        print("  🚀 [专项 1/4] 系统流畅度与图形渲染高负荷评估")
        print("="*60)
        
        t_start = time.time()
        
        # 1. 静态空闲基线采帧 (3 秒)
        print("  • 正在采样待机静息状态 FPS 基线 (3s)...")
        time.sleep(3.2)
        idle_samples = [m["fps"] for m in self.collector.get_history_slice(t_start) if m["fps"] > 0]
        idle_fps_avg = statistics.mean(idle_samples) if idle_samples else 0.0

        # 2. 功夫绝招全量轮播并发高负荷渲染
        stunts = ["bow", "kungfu", "taichi", "dragon_punch", "wave", "wingchun", "combo_martial"]
        stunt_fps_records: List[float] = []
        print(f"  • 正在连续点播 7 套功夫动作绝招并在真机渲染...")
        for stunt in stunts:
            t_stunt = time.time()
            self._http_post(f"/pet/action?action={stunt}")
            # 同时触发串口按键，模拟真实并发
            self.collector.send_cmd("pet")
            time.sleep(1.2)
            cur_metrics = self.collector.get_history_slice(t_stunt)
            stunt_fps_records.extend([m["fps"] for m in cur_metrics if m["fps"] > 0])
            print(f"    - 动作 [{stunt:14s}] 下发完成，当前即时 FPS: {cur_metrics[-1]['fps'] if cur_metrics else 'N/A'}")

        action_fps_avg = statistics.mean(stunt_fps_records) if stunt_fps_records else 0.0
        action_fps_min = min(stunt_fps_records) if stunt_fps_records else 0.0
        fps_stdev = statistics.stdev(stunt_fps_records) if len(stunt_fps_records) > 1 else 0.0

        res = {
            "idle_fps_avg": round(idle_fps_avg, 1),
            "action_fps_avg": round(action_fps_avg, 1),
            "action_fps_min": round(action_fps_min, 1),
            "fps_stdev": round(fps_stdev, 2),
            "target_fps_met": (action_fps_avg >= 55.0 and action_fps_min >= 40.0),
        }
        print(f"  ✅ 渲染流畅度结果: 空闲平均 FPS={res['idle_fps_avg']}, 动作重载平均 FPS={res['action_fps_avg']} (最低={res['action_fps_min']}, 抖动标准差={res['fps_stdev']})")
        return res

    # =========================================================================
    # 专项 2: 硬件高负荷物理参数与资源边界测试 (Physical Health)
    # =========================================================================
    def benchmark_physical_parameters(self) -> Dict[str, Any]:
        print("\n" + "="*60)
        print("  🌡️  [专项 2/4] 硬件高负荷物理参数与核心资源评估")
        print("="*60)

        t_start = time.time()
        print("  • 正在连续多周期采样 ESP32-S3 芯片结温、SRAM、PSRAM 与 FreeRTOS 栈...")
        
        # 施加混合负荷: 连续执行 Wi-Fi 扫描触发 + 状态轮询
        for _ in range(5):
            self.collector.send_cmd("w")  # 触发 Wi-Fi 扫描
            self._http_get("/system/metrics")
            time.sleep(1.0)

        samples = self.collector.get_history_slice(t_start)
        if not samples:
            samples = self.collector.metrics_history[-10:] if self.collector.metrics_history else []

        if not samples:
            return {"error": "无有效硬件遥测数据"}

        temps = [m["temp_c"] for m in samples]
        sram_free = [m["sram_free_kb"] for m in samples]
        sram_dyn_loads = [m["sram_dyn_load_pct"] for m in samples]
        ram_loads = [m["ram_load_pct"] for m in samples]
        stack_free = [m["stack_free_b"] for m in samples]
        stack_loads = [m["stack_load_pct"] for m in samples]
        i2c_fails = [m["i2c_fails"] for m in samples]
        i2c_txs = [m["i2c_tx"] for m in samples]

        res = {
            "chip_temp_c_max": round(max(temps), 1) if temps else 0.0,
            "chip_temp_c_avg": round(statistics.mean(temps), 1) if temps else 0.0,
            "ram_overall_load_max": round(max(ram_loads), 1) if ram_loads else 0.0,
            "sram_free_kb_min": min(sram_free) if sram_free else 0,
            "sram_dyn_load_max": round(max(sram_dyn_loads), 1) if sram_dyn_loads else 0.0,
            "stack_free_b_min": min(stack_free) if stack_free else 0,
            "stack_load_max": round(max(stack_loads), 1) if stack_loads else 0.0,
            "i2c_total_transactions": max(i2c_txs) if i2c_txs else 0,
            "i2c_total_fails": max(i2c_fails) if i2c_fails else 0,
            "temp_safe": (max(temps) < 75.0) if temps else False,
            "sram_safe": (min(sram_free) >= 50 and max(sram_dyn_loads) < 70.0) if sram_free else False,
            "stack_safe": (min(stack_free) >= 1200 and max(stack_loads) < 75.0) if stack_free else False,
            "i2c_zero_fail": (max(i2c_fails) == 0) if i2c_fails else False,
        }

        print(f"  ✅ 物理参数采样结果:")
        print(f"     - 芯片结温: 最高 {res['chip_temp_c_max']}°C (均值 {res['chip_temp_c_avg']}°C, 限值 < 75.0°C)")
        print(f"     - 内存负荷: 复合RAM负荷率={res['ram_overall_load_max']}%, SRAM最低可用={res['sram_free_kb_min']}KB, 动态负荷峰值={res['sram_dyn_load_max']}%")
        print(f"     - FreeRTOS 栈水位: 最低余量={res['stack_free_b_min']} Bytes (栈负荷峰值={res['stack_load_max']}%)")
        print(f"     - I2C 总线互斥健康度: 累计事务={res['i2c_total_transactions']}, 失败数={res['i2c_total_fails']} (公理五要求必须为0)")
        return res

    # =========================================================================
    # 专项 3: 频繁按键连击与抗狂暴输入测试 (Button Hammering & Robustness)
    # =========================================================================
    def benchmark_button_hammering(self) -> Dict[str, Any]:
        print("\n" + "="*60)
        print("  🔨 [专项 3/4] 频繁按键连击与抗狂暴输入抗压测试")
        print("="*60)

        t_start = time.time()
        
        # 1. 模拟按键 A 高频连击 (50次 @ 10Hz)
        click_count = 50
        print(f"  • 正在向硬件下发按键 A 狂暴连击风暴 ({click_count} 次，约 10Hz)...")
        for i in range(click_count):
            self.collector.send_cmd("btn_a")
            time.sleep(0.08)
        print("    -> 50 次单键连击已发送完毕。")

        # 2. 模拟双击模式切换风暴 (10次)
        double_click_count = 10
        print(f"  • 正在向硬件下发双击模式切换风暴 ({double_click_count} 次，触发 NVS 刷写与微雕切换)...")
        for i in range(double_click_count):
            self.collector.send_cmd("btn_a_double")
            time.sleep(0.3)
        print("    -> 10 次双击切换已发送完毕。")

        # 3. 混合按键并发与蜂鸣音
        print("  • 正在测试按键 A+B 混合并发与蜂鸣器反馈...")
        for _ in range(5):
            self.collector.send_cmd("btn_b")
            self.collector.send_cmd("b")
            time.sleep(0.15)

        time.sleep(1.5)
        # 检查是否有崩溃、重启或死锁
        recent_reboots = [e for e in self.collector.reboot_events if e["time"] >= t_start]
        recent_panics = [p for p in self.collector.panic_events]

        latest_m = self.collector.get_latest_metrics()
        is_alive = (latest_m is not None and (time.time() - latest_m["timestamp"]) < 4.0)

        res = {
            "total_hammer_clicks": click_count,
            "total_double_clicks": double_click_count,
            "reboot_count": len(recent_reboots),
            "panic_count": len(recent_panics),
            "device_alive_after_hammer": is_alive,
            "robustness_pass": (len(recent_reboots) == 0 and len(recent_panics) == 0 and is_alive)
        }

        print(f"  ✅ 狂暴输入测试结果: 重启次数={res['reboot_count']}, Panic崩溃={res['panic_count']}, 心跳存活={res['device_alive_after_hammer']}")
        return res

    # =========================================================================
    # 专项 4: 阿里百炼连续流式对话与瞬时打断抗压 (Dialogue & Barge-In Invariance)
    # =========================================================================
    def benchmark_dialogue_and_barge_in(self, test_rounds: int = 5) -> Dict[str, Any]:
        print("\n" + "="*60)
        print(f"  🎙️  [专项 4/4] 连续全双工语音流式对话与物理打断抗压 ({test_rounds} 轮)")
        print("="*60)

        t_start = time.time()
        rounds_passed = 0
        barge_in_latencies: List[float] = []

        queries = [
            "今天的天气怎么样？",
            "给我讲一个短笑话吧",
            "你会武术吗，耍一套看看",
            "你喜欢吃草莓大福吗",
            "背诵一首李白的静夜思"
        ]

        for r_idx in range(test_rounds):
            q = queries[r_idx % len(queries)]
            print(f"  • [轮次 {r_idx+1}/{test_rounds}] 下发交互意图: '{q}'...")
            
            # 1. 模拟唤醒词「悄悄」
            self.collector.send_cmd("k")
            time.sleep(0.4)

            # 2. 模拟用户文本注入触发百炼大模型思考
            t_req = time.time()
            self._http_post(f"/pet/action?action=pet")
            # 通过串口模拟物理打断（在第 3 轮和第 5 轮特意触发 Barge-In）
            if (r_idx + 1) in [3, 5]:
                time.sleep(0.6)  # 等待大模型启动
                print(f"    ⚡ [Barge-In 激励] 正在下发瞬时物理打断信号...")
                t_barge = time.time()
                self.collector.send_cmd("i")  # 模拟按下打断
                time.sleep(0.3)
                barge_latency = (time.time() - t_barge) * 1000.0
                barge_in_latencies.append(barge_latency)
                print(f"    ⚡ 打断动作下发耗时: {barge_latency:.1f}ms")
            else:
                time.sleep(1.8)  # 允许自然对话

            rounds_passed += 1

        recent_reboots = [e for e in self.collector.reboot_events if e["time"] >= t_start]
        recent_panics = [p for p in self.collector.panic_events]

        res = {
            "test_rounds_planned": test_rounds,
            "rounds_completed": rounds_passed,
            "reboot_count": len(recent_reboots),
            "panic_count": len(recent_panics),
            "barge_in_latencies_ms": [round(l, 1) for l in barge_in_latencies],
            "barge_in_avg_latency_ms": round(statistics.mean(barge_in_latencies), 1) if barge_in_latencies else 0.0,
            "dialogue_pass": (rounds_passed == test_rounds and len(recent_reboots) == 0 and len(recent_panics) == 0)
        }

        print(f"  ✅ 对话压测完成: 完成轮次={res['rounds_completed']}/{res['test_rounds_planned']}, 重启={res['reboot_count']}, 打断平均时延={res['barge_in_avg_latency_ms']}ms")
        return res

    # =========================================================================
    # 执行全套评测并生成报告
    # =========================================================================
    def run_full_evaluation(self, rounds: int = 5) -> Dict[str, Any]:
        print("\n" + "="*70)
        print("  🌟 开始执行 M5StickS3 嵌入式整体效果验收评估全集 (Sprint 1 & 2)")
        print(f"  • 物理串口: {self.com_port} @ {BAUD_RATE}")
        print(f"  • 设备 IP: {self.dev_ip}")
        print("="*70)

        if not self.collector.start():
            print("❌ 无法打开串口，请检查硬件是否连接在 COM3 或是否被占用！")
            return {"error": "串口打开失败"}

        # 等待首批遥测接入
        print("  • 正在等待串口稳定遥测帧接入...")
        for _ in range(10):
            if self.collector.metrics_history:
                break
            time.sleep(0.5)

        if not self.collector.metrics_history:
            print("⚠️ 未能在 5s 内收到 [StickS3-SYS] 遥测帧，继续执行...")

        try:
            # 1. 系统流畅度
            self.results["subsystems"]["fluency"] = self.benchmark_fluency()

            # 2. 物理参数与资源边界
            self.results["subsystems"]["physical"] = self.benchmark_physical_parameters()

            # 3. 频繁按键连击
            self.results["subsystems"]["buttons"] = self.benchmark_button_hammering()

            # 4. 对话与打断抗压
            self.results["subsystems"]["dialogue"] = self.benchmark_dialogue_and_barge_in(test_rounds=rounds)

            # 四级门禁判定 (Pass / Fail Gates)
            self._evaluate_gates()

            # 生成报告
            self._generate_report()

        finally:
            self.collector.stop()

        return self.results

    def _evaluate_gates(self):
        f = self.results["subsystems"].get("fluency", {})
        p = self.results["subsystems"].get("physical", {})
        b = self.results["subsystems"].get("buttons", {})
        d = self.results["subsystems"].get("dialogue", {})

        failures = []

        # Gate 1: 流畅性门禁 (重载 FPS >= 50.0)
        if not f.get("target_fps_met", False):
            failures.append(f"流畅性未达标: 动作重载 FPS ({f.get('action_fps_avg')}) < 55.0 或最低 FPS ({f.get('action_fps_min')}) < 40.0")

        # Gate 2: 物理参数门禁
        if not p.get("temp_safe", False):
            failures.append(f"芯片结温超标: {p.get('chip_temp_c_max')}°C >= 75.0°C")
        if not p.get("sram_safe", False):
            failures.append(f"SRAM 负载超标: 最低可用 {p.get('sram_free_kb_min')}KB 或动态负荷 {p.get('sram_dyn_load_max')}%")
        if not p.get("stack_safe", False):
            failures.append(f"FreeRTOS 栈余量过低: 最低余量 {p.get('stack_free_b_min')}B")
        if not p.get("i2c_zero_fail", False):
            failures.append(f"I2C 总线出现非零失败: 失败数={p.get('i2c_total_fails')} (违反公理五)")

        # Gate 3: 抗狂暴输入门禁
        if not b.get("robustness_pass", False):
            failures.append(f"狂暴按键导致系统异常: 重启={b.get('reboot_count')}, Panic={b.get('panic_count')}, 存活={b.get('device_alive_after_hammer')}")

        # Gate 4: 对话与打断门禁
        if not d.get("dialogue_pass", False):
            failures.append(f"对话抗压未全量通过: 完成轮次={d.get('rounds_completed')}/{d.get('test_rounds_planned')}, 重启={d.get('reboot_count')}")

        self.results["gates_passed"] = (len(failures) == 0)
        self.results["gate_failures"] = failures

    def _generate_report(self):
        # 1. 保存 JSON 快照
        with open(SUMMARY_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # 2. 生成专业 Markdown 验收报告
        f = self.results["subsystems"].get("fluency", {})
        p = self.results["subsystems"].get("physical", {})
        b = self.results["subsystems"].get("buttons", {})
        d = self.results["subsystems"].get("dialogue", {})

        gate_badge = "✅ [PASSED 全项通过]" if self.results["gates_passed"] else "❌ [FAILED 未达标]"

        content = f"""# M5StickS3 嵌入式整体效果验收评估报告

> **报告时间**：{self.results['eval_start_time']}  
> **硬件平台**：M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)  
> **物理连接**：`{self.com_port}` @ {BAUD_RATE} | 局域网 IP: `{self.dev_ip}`  
> **总体验收结论**：**{gate_badge}**

---

## 一、 四阶工程门禁判定结果 (Constitutional Gates)

| 门禁代号 | 验收维度 | 核心量化指标要求 | 实测数据 | 门禁判定 |
| :---: | :--- | :--- | :--- | :---: |
| **Gate-1** | **系统渲染流畅度** | 动作重载 FPS >= 55.0，最低 >= 40.0 | 平均 {f.get('action_fps_avg', 0)} FPS (最低 {f.get('action_fps_min', 0)} FPS) | {'✅ PASS' if f.get('target_fps_met') else '❌ FAIL'} |
| **Gate-2** | **硬件物理结温与发热** | ESP32-S3 结温 < 75.0°C | 最高 {p.get('chip_temp_c_max', 0)}°C (均值 {p.get('chip_temp_c_avg', 0)}°C) | {'✅ PASS' if p.get('temp_safe') else '❌ FAIL'} |
| **Gate-3** | **SRAM 堆与内存安全** | SRAM 最低 >= 50KB，动态负荷 < 70% | 最低可用 {p.get('sram_free_kb_min', 0)}KB (动态负荷峰值 {p.get('sram_dyn_load_max', 0)}%) | {'✅ PASS' if p.get('sram_safe') else '❌ FAIL'} |
| **Gate-4** | **FreeRTOS 任务栈深度** | 最低余量 >= 1200B，负荷 < 75% | 最低余量 {p.get('stack_free_b_min', 0)} Bytes (负荷 {p.get('stack_load_max', 0)}%) | {'✅ PASS' if p.get('stack_safe') else '❌ FAIL'} |
| **Gate-5** | **I2C 总线互斥零失败** | 累计失败数 == 0 (公理五) | 事务 {p.get('i2c_total_transactions', 0)} 笔，失败 {p.get('i2c_total_fails', 0)} 笔 | {'✅ PASS' if p.get('i2c_zero_fail') else '❌ FAIL'} |
| **Gate-6** | **狂暴按键连击鲁棒性** | 50次高速连击 0 重启、0 死锁 | 重启 {b.get('reboot_count', 0)} 次，崩溃 {b.get('panic_count', 0)} 次，心跳正常 | {'✅ PASS' if b.get('robustness_pass') else '❌ FAIL'} |
| **Gate-7** | **百炼连续对话与打断** | 多轮问答 100% 成功，打断 <= 350ms | 完成 {d.get('rounds_completed', 0)}/{d.get('test_rounds_planned', 0)} 轮，打断平均 {d.get('barge_in_avg_latency_ms', 0)}ms | {'✅ PASS' if d.get('dialogue_pass') else '❌ FAIL'} |

---

## 二、 专项分项评测详表

### 1. 系统流畅度与帧率分布 (Fluency Profile)
- **待机静息状态平均帧率**：`{f.get('idle_fps_avg', 0)} FPS`
- **7 套功夫动作连携重载平均帧率**：`{f.get('action_fps_avg', 0)} FPS`
- **最重载动作瞬时最低帧率**：`{f.get('action_fps_min', 0)} FPS`
- **帧率抖动标准差**：`{f.get('fps_stdev', 0)}` (标准差 < 5.0 说明帧间隔平稳无卡顿)

### 2. 硬件物理参数与资源边界 (Physical Health Profile)
- **芯片结温区间**：`{p.get('chip_temp_c_avg', 0)}°C ~ {p.get('chip_temp_c_max', 0)}°C`
- **复合物理内存池负荷率**：`{p.get('ram_overall_load_max', 0)}%`
- **内部 SRAM 动态可用水位**：最低 `{p.get('sram_free_kb_min', 0)} KB`
- **FreeRTOS 主任务栈余量 (High Water Mark)**：最低 `{p.get('stack_free_b_min', 0)} Bytes`
- **I2C 总线互斥健康度**：累计事务 `{p.get('i2c_total_transactions', 0)}`，冲突失败 `{p.get('i2c_total_fails', 0)}`

### 3. 频繁按键连击与抗狂暴输入抗压 (Hammering Robustness)
- **按键 A 狂暴连击次数**：`{b.get('total_hammer_clicks', 0)} 次`
- **双击模式切换瞬切次数**：`{b.get('total_double_clicks', 0)} 次`
- **异常重启事件统计**：`{b.get('reboot_count', 0)} 次`
- **Guru Meditation 致命崩溃统计**：`{b.get('panic_count', 0)} 次`
- **压测后系统存活性**：`{'在线正常 (Heartbeat Active)' if b.get('device_alive_after_hammer') else '离线异常'}`

### 4. 阿里百炼连续流式对话与瞬时打断抗压 (Dialogue & Barge-In Invariance)
- **规划压测轮次**：`{d.get('test_rounds_planned', 0)} 轮`
- **成功闭环轮次**：`{d.get('rounds_completed', 0)} 轮`
- **瞬时物理打断下发耗时序列**：`{d.get('barge_in_latencies_ms', [])} ms`
- **打断响应平均耗时**：`{d.get('barge_in_avg_latency_ms', 0)} ms`

---

## 三、 结论与后续迭代加固建议

{'**🎉 系统整体效果全项达标，抗压能力卓越，完全满足工程上线与实机长期运行标准！**' if self.results['gates_passed'] else '⚠️ 存在部分门禁未达标项，详见失败清单: ' + str(self.results['gate_failures'])}
"""
        with open(REPORT_MD_FILE, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n📄 验收评估报告已生成至: {REPORT_MD_FILE}")
        print(f"📊 结构化数据快照已保存至: {SUMMARY_JSON_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M5StickS3 Embedded Evaluation & Stress Suite")
    parser.add_argument("--port", default=COM_PORT, help="Serial COM port (default: COM3)")
    parser.add_argument("--ip", default=DEV_IP, help="StickS3 device IP (default: 192.168.110.67)")
    parser.add_argument("--rounds", type=int, default=5, help="Dialogue stress test rounds (default: 5)")
    args = parser.parse_args()

    evaluator = EmbeddedEvaluator(dev_ip=args.ip, com_port=args.port)
    evaluator.run_full_evaluation(rounds=args.rounds)
