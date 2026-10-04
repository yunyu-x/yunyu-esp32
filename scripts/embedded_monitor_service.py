#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/embedded_monitor_service.py
-----------------------------------
M5Stack StickS3 嵌入式实时监控与卡顿/重启深度诊断服务 (Embedded Diagnostic Monitor)

功能：
1. 监听物理 COM3 串口流 (115200 波特率)
2. 毫秒级时间戳记录全部串口原始报文至 logs/embedded_diagnostics.log
3. 实时分析三大核心诊断场景：
   - 【收到音后卡住不输出 (STUCK/FREEZE)】：
     跟踪语音开始 -> 停止 -> 进入 THINKING 状态 -> 首音频帧 (TTFA) 时间。
     若在 THINKING 状态超过 3 秒未出声，触发 [DIAG-ALERT: STUCK] 告警；
     若触发 10 秒看门狗超时，详细记录丢包/取消标记上下文。
   - 【系统异常重启 (REBOOT/PANIC)】：
     捕获 rst:0x.. 重启原因、Guru Meditation Error、Stack Backtrace、Assert Failed，
     分析导致复位的确切调用栈与寄存器上下文。
   - 【硬件负荷率越界 (OVERLOAD)】：
     实时解析 RAM Load、SRAM DynLoad、Stack Load、I2C Fails，凡是超出 70% 立即触发告警。
4. 实时持久化诊断快照至 logs/diagnostic_summary.json，支持异步随时读取。
"""

import os
import sys
import time
import json
import re
import signal
import serial

COM_PORT = "COM3"
BAUD_RATE = 115200

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
RAW_LOG_FILE = os.path.join(LOG_DIR, "embedded_diagnostics.log")
SUMMARY_JSON_FILE = os.path.join(LOG_DIR, "diagnostic_summary.json")

os.makedirs(LOG_DIR, exist_ok=True)

RESET_REASONS = {
    "0x1": "POWERON_RESET (Vbat/USB 上电复位)",
    "0x3": "SW_RESET (软件主动调用 esp_restart)",
    "0x4": "OWDT_RESET / ESP_RST_PANIC (硬件异常崩溃/Panic复位)",
    "0x5": "DEEPSLEEP_RESET (深度休眠唤醒)",
    "0x6": "SDIO_RESET (SDIO复位)",
    "0x7": "TG0WDT_SYS_RESET (TimerGroup0 看门狗超时复位)",
    "0x8": "TG1WDT_SYS_RESET (TimerGroup1 看门狗超时复位)",
    "0x9": "RTCWDT_SYS_RESET (RTC看门狗超时复位)",
    "0x10": "INTRUSION_RESET (入侵检测复位)",
    "0x11": "TGWDT_CPU_RESET (CPU 看门狗复位)",
    "0x12": "SW_CPU_RESET (CPU 软件复位)",
    "0x13": "RTCWDT_CPU_RESET (RTC CPU 看门狗复位)",
    "0x14": "EXT_CPU_RESET (外部引脚复位)",
    "0x15": "USB_UART_CHIP_RESET (USB DTR/RTS 硬件触发硬复位)"
}

class EmbeddedMonitor:
    def __init__(self, port=COM_PORT, baud=BAUD_RATE):
        self.port = port
        self.baud = baud
        self.running = True
        
        # 统计指标
        self.total_lines = 0
        self.start_time = time.time()
        self.last_seen_time = time.time()
        
        # 状态机与卡顿跟踪
        self.bailian_state = "UNKNOWN"
        self.speech_start_time = None
        self.thinking_start_time = None
        self.last_user_query = ""
        self.last_ai_reply = ""
        self.stuck_events = []
        
        # 重启跟踪
        self.reboot_count = 0
        self.reboot_events = []
        self.last_backtrace = []
        
        # 硬件指标
        self.last_metrics = {
            "fps": 0.0,
            "ram_load": 0.0,
            "ram_free_mb": 0.0,
            "sram_dyn_load": 0.0,
            "sram_free_kb": 0,
            "stack_load": 0.0,
            "stack_free_b": 0,
            "i2c_fails": 0
        }
        self.overload_alerts = []
        
        # 初始化日志文件
        with open(RAW_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n[{self.ts()}] [SERVICE-START] Embedded Monitor Service started on {self.port} @ {self.baud}\n{'='*70}\n")
        self.save_summary()

    def ts(self):
        t = time.time()
        return f"{time.strftime('%H:%M:%S', time.localtime(t))}.{int((t % 1) * 1000):03d}"

    def log(self, tag, msg, alert=False):
        formatted = f"[{self.ts()}] [{tag}] {msg}"
        print(formatted)
        sys.stdout.flush()
        try:
            with open(RAW_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception:
            pass

    def save_summary(self):
        data = {
            "monitor_uptime_sec": round(time.time() - self.start_time, 1),
            "total_lines_parsed": self.total_lines,
            "current_bailian_state": self.bailian_state,
            "last_user_query": self.last_user_query,
            "last_ai_reply": self.last_ai_reply,
            "reboot_count": self.reboot_count,
            "reboot_events": self.reboot_events[-10:],
            "stuck_events": self.stuck_events[-10:],
            "overload_alerts": self.overload_alerts[-10:],
            "last_hardware_metrics": self.last_metrics
        }
        try:
            with open(SUMMARY_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def process_line(self, line):
        self.total_lines += 1
        self.last_seen_time = time.time()
        now = time.time()

        # 写入原始全量日志
        try:
            with open(RAW_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{self.ts()}] [RAW] {line}\n")
        except Exception:
            pass

        # -------------------------------------------------------------
        # 1. 监测系统重启与崩溃 Panic / Guru Meditation
        # -------------------------------------------------------------
        if "rst:0x" in line:
            self.reboot_count += 1
            rst_code = "UNKNOWN"
            m = re.search(r'rst:(0x[0-9a-fA-F]+)', line)
            if m:
                rst_code = m.group(1).lower()
            reason_str = RESET_REASONS.get(rst_code, f"未知复位码 {rst_code}")
            
            event = {
                "timestamp": self.ts(),
                "raw": line,
                "code": rst_code,
                "reason": reason_str,
                "backtrace": list(self.last_backtrace)
            }
            self.reboot_events.append(event)
            self.log("REBOOT-ALERT", f"⚠️ 发现系统重启! 复位码: {rst_code} -> {reason_str}", alert=True)
            self.last_backtrace.clear()
            self.save_summary()
            return

        if "Guru Meditation" in line or "PANIC" in line or "abort()" in line or "LoadProhibited" in line or "StoreProhibited" in line:
            self.log("CRASH-ALERT", f"💥 捕获致命硬件崩溃 Panic: {line}", alert=True)
            self.last_backtrace.append(line)
            self.save_summary()
            return

        if "Backtrace:" in line:
            self.last_backtrace.append(line)
            self.log("CRASH-STACK", f"堆栈追踪: {line}", alert=True)
            self.save_summary()
            return

        # -------------------------------------------------------------
        # 2. 监测百炼大模型交互状态机与卡顿事件
        # -------------------------------------------------------------
        if "[BAILIAN-STATE]" in line:
            m = re.search(r'\[BAILIAN-STATE\]\s*(\d+)\s*->\s*(\d+)\s*\((.*?)\)', line)
            if m:
                old_st, new_st, name = m.group(1), m.group(2), m.group(3)
                self.bailian_state = f"{new_st} ({name})"
                self.log("STATE-CHANGE", f"百炼状态跃迁: {old_st} -> {new_st} ({name})")
                
                # 进入 THINKING 状态
                if new_st == "4": # THINKING
                    self.thinking_start_time = now
                    self.log("DIAG-FLOW", "用户发言完毕，系统转入思考状态 (THINKING)...")
                # 恢复 SPEAKING 状态 (开始出声)
                elif new_st == "5": # SPEAKING
                    if self.thinking_start_time:
                        ttfa = (now - self.thinking_start_time) * 1000.0
                        self.log("DIAG-FLOW", f"🎙️ AI 开始出声回复! 首音频延迟 (TTFA): {ttfa:.1f}ms")
                        self.thinking_start_time = None
                elif new_st == "3": # LISTENING
                    if self.thinking_start_time:
                        # 思考中直接恢复倾听，说明没有出声回复！
                        dur = now - self.thinking_start_time
                        stuck_info = {
                            "timestamp": self.ts(),
                            "duration_sec": round(dur, 2),
                            "reason": "思考中途直接跳回 LISTENING，未产出任何音频",
                            "user_query": self.last_user_query
                        }
                        self.stuck_events.append(stuck_info)
                        self.log("STUCK-ALERT", f"❌ 收到声音后卡住且未出声回复就恢复倾听! 思考耗时: {dur:.2f}s", alert=True)
                        self.thinking_start_time = None
                        self.save_summary()
            return

        # 监测用户开始讲话 / 结束讲话
        if "Server-VAD: User started speaking" in line:
            self.speech_start_time = now
            self.log("VOICE-IN", "🗣️ 云端 VAD 捕获用户开始讲话...")
            return

        if "Server-VAD: User stopped speaking" in line:
            self.log("VOICE-STOP", "云端 VAD 确认用户发言结束，等待生成回复...")
            if not self.thinking_start_time:
                self.thinking_start_time = now
            return

        # 监测本地静音超时主动 commit
        if "Local silence timeout (>800ms). Actively committing audio buffer" in line:
            self.log("VAD-TIMEOUT", "⚠️ 本地静音超过 800ms，客户端主动 commit 音频缓冲...")
            if not self.thinking_start_time:
                self.thinking_start_time = now
            return

        # 监测 10 秒思考超时看门狗触发
        if "[BAILIAN-TIMEOUT]" in line or "Thinking state timeout" in line:
            stuck_info = {
                "timestamp": self.ts(),
                "duration_sec": round(now - (self.thinking_start_time or now), 2),
                "reason": "10s 看门狗超时 (Thinking state timeout)，云端未下发音频流或响应被丢弃",
                "user_query": self.last_user_query
            }
            self.stuck_events.append(stuck_info)
            self.log("STUCK-ALERT", f"🚨 诊断确认：收到音后卡死卡住！触发 10 秒看门狗强制恢复！", alert=True)
            self.thinking_start_time = None
            self.save_summary()
            return

        # 监测用户转写文本
        if "conversation.item.input_audio_transcription.completed" in line or "[CHAT-RX]" in line:
            self.log("TRANSCRIPT", f"收到转写/提问: {line}")
            return

        # 监测 response.created 与 response.cancel
        if "response.created received" in line:
            self.log("CLOUD-RES", "云端已创建 response 回复帧，准备推流...")
            return

        if "response.cancel" in line:
            self.log("CANCEL-EVT", f"⚠️ 触发 response.cancel 取消回复: {line}")
            return

        # 监测音频播放启动与结束
        if ">>> LLM Full-Duplex Stream Playback STARTED" in line:
            self.log("AUDIO-PLAY", f"🔊 喇叭全双工流式播放已启动: {line}")
            if self.thinking_start_time:
                ttfa = (now - self.thinking_start_time) * 1000.0
                self.log("AUDIO-TTFA", f"首音频响应耗时 (TTFA): {ttfa:.1f}ms")
                self.thinking_start_time = None
            return

        if ">>> LLM Stream Playback FINISHED" in line:
            self.log("AUDIO-PLAY", "喇叭播放完毕，音频 Codec 恢复麦克风录音模式。")
            return

        # -------------------------------------------------------------
        # 3. 监测硬件负荷率指标 [StickS3-SYS]
        # -------------------------------------------------------------
        if "[StickS3-SYS]" in line:
            # FPS: 61.0 | RAM: free=7.30MB (Load: 12.0%) | SRAM: free=74KB, max_block=59KB (DynLoad: 47.1%) | Stack: free=5192B (Load: 36.6%) | I2C_Tx: 1049 (Fails: 0)
            try:
                m_fps = re.search(r'FPS:\s*([\d\.]+)', line)
                m_ram = re.search(r'Load:\s*([\d\.]+)%', line)
                m_ram_free = re.search(r'free=([\d\.]+)MB', line)
                m_sram_load = re.search(r'DynLoad:\s*([\d\.]+)%', line)
                m_sram_free = re.search(r'SRAM:\s*free=(\d+)KB', line)
                m_stack_load = re.search(r'Stack:.*?Load:\s*([\d\.]+)%', line)
                m_stack_free = re.search(r'Stack:\s*free=(\d+)B', line)
                m_i2c_fails = re.search(r'Fails:\s*(\d+)', line)

                if m_fps: self.last_metrics["fps"] = float(m_fps.group(1))
                if m_ram: self.last_metrics["ram_load"] = float(m_ram.group(1))
                if m_ram_free: self.last_metrics["ram_free_mb"] = float(m_ram_free.group(1))
                if m_sram_load: self.last_metrics["sram_dyn_load"] = float(m_sram_load.group(1))
                if m_sram_free: self.last_metrics["sram_free_kb"] = int(m_sram_free.group(1))
                if m_stack_load: self.last_metrics["stack_load"] = float(m_stack_load.group(1))
                if m_stack_free: self.last_metrics["stack_free_b"] = int(m_stack_free.group(1))
                if m_i2c_fails: self.last_metrics["i2c_fails"] = int(m_i2c_fails.group(1))

                # 检查负荷越界 (> 70%)
                for metric, val in [("RAM Load", self.last_metrics["ram_load"]),
                                    ("SRAM DynLoad", self.last_metrics["sram_dyn_load"]),
                                    ("Stack Load", self.last_metrics["stack_load"])]:
                    if val > 70.0:
                        alert_msg = f"硬件指标 {metric} 超过 70% 硬性限额! 当前值: {val:.1f}%"
                        self.overload_alerts.append({"timestamp": self.ts(), "alert": alert_msg})
                        self.log("LOAD-ALERT", alert_msg, alert=True)

                # 每 10 次更新一次概要
                if self.total_lines % 10 == 0:
                    self.save_summary()
            except Exception as e:
                pass
            return

        # 其他关键事件上屏
        if any(k in line for k in ["[WIFI", "[BOOT", "[MEMORY", "[AUDIO-EVENT", "[PHYSICAL-INTERRUPT", "WSS"]):
            self.log("SYS-EVENT", line)

    def check_watchdogs(self):
        """定期检查是否在思考状态挂起卡顿"""
        now = time.time()
        if self.thinking_start_time and (now - self.thinking_start_time > 3.5):
            stuck_dur = now - self.thinking_start_time
            # 限频提醒
            if int(stuck_dur) % 3 == 0:
                self.log("STUCK-WARN", f"⚠️ 诊断警报：大模型进入 THINKING 状态已持续 {stuck_dur:.1f}s 仍无音频下发！", alert=True)

    def run(self):
        self.log("INIT", f"正在打开物理串口 {self.port} (波特率: {self.baud})...")
        try:
            s = serial.Serial()
            s.port = self.port
            s.baudrate = self.baud
            s.timeout = 0.2
            # 保持 DTR/RTS 处于低电平，不主动触发设备复位，保持当前连续交互状态
            s.dtr = False
            s.rts = False
            s.open()
            self.log("INIT", f"物理串口 {self.port} 连接成功！正在监听实机串口遥测与对话流...")
        except Exception as e:
            self.log("ERROR", f"打开串口 {self.port} 失败: {e}", alert=True)
            return

        last_status_tick = time.time()

        try:
            while self.running:
                try:
                    raw = s.readline()
                    if raw:
                        line = raw.decode('utf-8', errors='replace').strip()
                        if line:
                            self.process_line(line)
                    else:
                        time.sleep(0.01)
                except Exception as e:
                    self.log("READ-ERR", f"串口读取异常: {e}")
                    time.sleep(0.1)

                self.check_watchdogs()

                # 每 10 秒刷新一次运行状态心跳
                if time.time() - last_status_tick >= 10.0:
                    last_status_tick = time.time()
                    m = self.last_metrics
                    self.log("HEARTBEAT", f"监控正常 | 状态: {self.bailian_state} | 重启: {self.reboot_count}次 | 卡顿: {len(self.stuck_events)}次 | RAM: {m['ram_load']:.1f}% | SRAM Dyn: {m['sram_dyn_load']:.1f}% | Stack: {m['stack_load']:.1f}%")
                    self.save_summary()

        except KeyboardInterrupt:
            self.log("STOP", "收到退出指令，正在停止监控服务...")
        finally:
            if s.is_open:
                s.close()
            self.log("STOP", f"监控服务已终止。全部日志已归档至 {RAW_LOG_FILE}")
            self.save_summary()

if __name__ == "__main__":
    monitor = EmbeddedMonitor()
    def sig_handler(sig, frame):
        monitor.running = False
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    monitor.run()
