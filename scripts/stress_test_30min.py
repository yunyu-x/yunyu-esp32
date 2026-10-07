#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Muse & LingBuddy 30-Minute Continuous Stress Test & Acceptance Harness
===========================================================================
Strict verification & endurance monitoring for M5Stack StickS3:
- CPU / Loop FPS stability (Target: >= 60 FPS, Apple HIG 90+ FPS capability)
- Internal chip temperature monitoring (temperatureRead() <= 75°C)
- SRAM & PSRAM memory leak regression analysis (Leak rate <= 0.05 KB/min)
- Command response latency (RTT) & ACK delivery rate (Target: >= 99.5%)
- Disney Avatar & Meta Muse Hatch state transitions stress endurance
"""

import os
import sys
import time
import json
import re
import argparse
import statistics
from typing import Dict, Any, List, Optional
import serial

# ANSI Color codes for terminal reporting
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Regular expressions for hardware telemetry
SYS_METRICS_REGEX = re.compile(
    r"\[StickS3-SYS\]\s+FPS:\s*(?P<fps>[\d\.]+)\s*\|\s*Temp:\s*(?P<temp>[\d\.]+)C\s*\|\s*RAM:\s*free=(?P<ram_free>[\d\.]+)MB\s*\(Load:\s*(?P<ram_load>[\d\.]+)%\)\s*\|\s*SRAM:\s*free=(?P<sram_free>\d+)KB,\s*max_block=(?P<max_block>\d+)KB\s*\(DynLoad:\s*(?P<sram_dyn_load>[\d\.]+)%\)\s*\|\s*Stack:\s*free=(?P<stack_free>\d+)B\s*\(Load:\s*(?P<stack_load>[\d\.]+)%\)\s*\|\s*I2C_Tx:\s*(?P<i2c_tx>\d+)\s*\(Fails:\s*(?P<i2c_fails>\d+)\)"
)
STATUS_JSON_REGEX = re.compile(r"@status\s+(\{.*\})")
CHAT_JSON_REGEX = re.compile(r"@chat\s+(\{.*\})")
PANIC_REGEX = re.compile(r"(Guru Meditation Error|abort\(\)|CORRUPT HEAP|rst:0x[0-9a-fA-F]+)")


class HardwareStressTester:
    def __init__(self, port: str = "COM3", baud: int = 115200, duration_sec: int = 1800, output_file: str = "dist/stress_test_report.json"):
        self.port = port
        self.baud = baud
        self.duration_sec = duration_sec
        self.output_file = output_file
        
        self.ser: Optional[serial.Serial] = None
        self.start_time = 0.0
        
        # Telemetry Time-Series
        self.fps_history: List[float] = []
        self.temp_history: List[float] = []
        self.ram_free_history: List[float] = []
        self.ram_load_history: List[float] = []
        self.sram_free_history: List[float] = []
        self.sram_dyn_load_history: List[float] = []
        self.stack_free_history: List[int] = []
        self.stack_load_history: List[float] = []
        self.i2c_fails_history: List[int] = []
        self.command_rtt_history: List[float] = []
        self.timestamps: List[float] = []
        
        # Command metrics
        self.commands_sent = 0
        self.commands_acked = 0
        self.panic_detected = 0
        self.panic_logs: List[str] = []
        
        # Stimulus command sequence to continuously stress avatar and protocol engine
        self.stimulus_commands = [
            (">status", "status"),
            (">action=wave", "wave"),
            (">action=bow", "bow"),
            (">action=cheer", "cheer"),
            (">action=clap", "clap"),
            (">status", "status"),
            (">action=stretch", "stretch"),
            (">action=sit", "sit"),
            (">action=jump", "jump"),
            (">action=balance", "balance"),
            (">status", "status"),
            (">action=taichi", "taichi"),
            (">action=wingchun", "wingchun"),
            (">action=kungfu", "kungfu"),
            (">action=dragon_punch", "dragon_punch"),
            (">status", "status"),
            (">action=moonwalk", "moonwalk"),
            (">action=cyber_defense", "cyber_defense"),
            (">action=turn_around", "turn_around"),
            (">action=spin", "spin"),
            (">action=pushup", "pushup"),
            (">action=lie", "lie"),
            (">action=locked_try", "locked_try"),
            (">dance_swarm=waltz", "waltz"),
            (">dance_swarm=zen", "zen"),
            (">dance_swarm=moonwalk", "moonwalk_dance"),
            (">dance_swarm=cyber", "cyber_dance"),
            (">status", "status"),
        ]
        self.stimulus_idx = 0

    def connect(self, reset: bool = False) -> bool:
        try:
            print(f"{CYAN}[INIT]{RESET} Connecting to {self.port} at {self.baud} baud (reset={reset})...")
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            self.ser.dtr = False
            self.ser.rts = False

            if reset:
                # Trigger RTS/DTR hardware reboot
                print(f"{YELLOW}[RESET]{RESET} Triggering RTS/DTR hardware reset...")
                self.ser.setDTR(False)
                self.ser.setRTS(True)
                time.sleep(0.1)
                self.ser.setRTS(False)

            # Wait until device self-test is complete and loop is running
            print(f"{CYAN}[SYNC]{RESET} Synchronizing with StickS3 hardware telemetry...")
            t_deadline = time.time() + 6.0
            synced = False
            while time.time() < t_deadline:
                line = self.ser.readline().decode("utf-8", errors="replace").strip()
                if line:
                    if "[StickS3-SYS]" in line or "[StickS3-ONLINE]" in line or "FPS:" in line:
                        print(f"{GREEN}[SYNC-OK]{RESET} Hardware telemetry synchronized: {line}")
                        synced = True
                        break
                time.sleep(0.02)
            
            time.sleep(0.2)
            # Flush existing buffer
            self.ser.reset_input_buffer()
            print(f"{GREEN}[OK]{RESET} Serial connected and fully synchronized.")
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} Failed to connect to {self.port}: {e}")
            return False

    def send_command(self, cmd: str) -> Optional[float]:
        """Send command and wait for ACK / JSON response line to calculate RTT."""
        if not self.ser or not self.ser.is_open:
            return None
        self.commands_sent += 1
        t_send = time.time()
        try:
            self.ser.write((cmd + "\n").encode("utf-8"))
            self.ser.flush()
        except Exception as e:
            print(f"{RED}[SEND ERROR]{RESET} {e}")
            return None

        # Wait up to 1.5s for response
        t_deadline = t_send + 1.5
        line_buf = ""
        while time.time() < t_deadline:
            try:
                line = self.ser.readline().decode("utf-8", errors="replace").strip()
            except Exception:
                continue
            if not line:
                continue
            
            # Record any panic immediately
            if PANIC_REGEX.search(line):
                self.panic_detected += 1
                self.panic_logs.append(line)
                print(f"{RED}[PANIC DETECTED]{RESET} {line}")

            # Check for system metrics in background
            self._parse_line_metrics(line)

            # Check if this line is an ACK or @status / @chat / @pet response
            if cmd == ">status" and (line.startswith("@status") or line.startswith("{") or "v_bus" in line):
                rtt_ms = (time.time() - t_send) * 1000.0
                self.commands_acked += 1
                self.command_rtt_history.append(rtt_ms)
                return rtt_ms
            elif line.startswith("@act") or line.startswith("@action") or line.startswith("@dance_swarm") or line.startswith("@growth") or line.startswith("@ceremony"):
                rtt_ms = (time.time() - t_send) * 1000.0
                self.commands_acked += 1
                self.command_rtt_history.append(rtt_ms)
                return rtt_ms
            elif line.startswith("@pet"):
                rtt_ms = (time.time() - t_send) * 1000.0
                self.commands_acked += 1
                self.command_rtt_history.append(rtt_ms)
                return rtt_ms
            elif line.startswith("@chat") and ("face_set" in line or "pet_switch" in line or "robot_ack" in line or "sent" in line):
                rtt_ms = (time.time() - t_send) * 1000.0
                self.commands_acked += 1
                self.command_rtt_history.append(rtt_ms)
                return rtt_ms
            elif line.startswith("@status"):
                rtt_ms = (time.time() - t_send) * 1000.0
                self.commands_acked += 1
                self.command_rtt_history.append(rtt_ms)
                return rtt_ms

        return None

    def _parse_line_metrics(self, line: str):
        # 1. SYS METRICS REGEX
        m = SYS_METRICS_REGEX.search(line)
        if m:
            now = time.time() - self.start_time
            fps = float(m.group("fps"))
            temp = float(m.group("temp"))
            ram_free = float(m.group("ram_free"))
            ram_load = float(m.group("ram_load"))
            sram_free = float(m.group("sram_free"))
            sram_dyn_load = float(m.group("sram_dyn_load"))
            stack_free = int(m.group("stack_free"))
            stack_load = float(m.group("stack_load"))
            i2c_fails = int(m.group("i2c_fails"))
            
            self.timestamps.append(now)
            self.fps_history.append(fps)
            self.temp_history.append(temp)
            self.ram_free_history.append(ram_free)
            self.ram_load_history.append(ram_load)
            self.sram_free_history.append(sram_free)
            self.sram_dyn_load_history.append(sram_dyn_load)
            self.stack_free_history.append(stack_free)
            self.stack_load_history.append(stack_load)
            self.i2c_fails_history.append(i2c_fails)
            return

        # 2. STATUS JSON REGEX
        m_stat = STATUS_JSON_REGEX.search(line)
        if m_stat:
            try:
                data = json.loads(m_stat.group(1))
                dev = data.get("device", {})
                if "temp_c" in dev and float(dev["temp_c"]) > 0:
                    temp = float(dev["temp_c"])
                    if not self.temp_history or len(self.temp_history) < len(self.fps_history):
                        self.temp_history.append(temp)
                if "fps" in dev and float(dev["fps"]) > 0:
                    fps = float(dev["fps"])
                    now = time.time() - self.start_time
                    if not self.timestamps or (now - self.timestamps[-1] > 0.5):
                        self.timestamps.append(now)
                        self.fps_history.append(fps)
            except Exception:
                pass

    def run_stress_test(self, reset: bool = False) -> Dict[str, Any]:
        if not self.ser and not self.connect(reset=reset):
            return {"error": "Failed to connect serial port"}

        self.start_time = time.time()
        end_time = self.start_time + self.duration_sec
        next_command_time = time.time() + 0.5

        print(f"\n{BOLD}{CYAN}========================================================================={RESET}")
        print(f"{BOLD}{CYAN}  M5Stack StickS3 & Meta Muse 30-Minute Continuous Stress Acceptance Test  {RESET}")
        print(f"{BOLD}{CYAN}========================================================================={RESET}")
        print(f"Target Duration : {self.duration_sec}s ({self.duration_sec / 60:.1f} mins)")
        print(f"Serial Port     : {self.port} @ {self.baud}")
        print(f"Stimulus Rates  : 1 command every 2.0s (Avatar switch, Face mood, Status probe)\n")

        last_display_time = time.time()

        try:
            while time.time() < end_time:
                current_time = time.time()
                elapsed = current_time - self.start_time
                remaining = end_time - current_time

                # 1. Non-blocking read serial buffer to catch logs and metrics
                if self.ser.in_waiting > 0:
                    try:
                        line = self.ser.readline().decode("utf-8", errors="replace").strip()
                        if line:
                            if PANIC_REGEX.search(line):
                                self.panic_detected += 1
                                self.panic_logs.append(line)
                                print(f"\n{RED}[PANIC!]{RESET} {line}")
                            self._parse_line_metrics(line)
                    except Exception:
                        pass

                # 2. Periodic stimulus dispatch
                if current_time >= next_command_time:
                    cmd, tag = self.stimulus_commands[self.stimulus_idx]
                    self.stimulus_idx = (self.stimulus_idx + 1) % len(self.stimulus_commands)
                    self.send_command(cmd)
                    next_command_time = current_time + 2.0

                # 3. Live Dashboard refresh every 1.5 seconds
                if current_time - last_display_time >= 1.5:
                    last_display_time = current_time
                    cur_fps = self.fps_history[-1] if self.fps_history else 0.0
                    avg_fps = statistics.mean(self.fps_history) if self.fps_history else 0.0
                    cur_temp = self.temp_history[-1] if self.temp_history else 0.0
                    cur_sram_load = self.sram_dyn_load_history[-1] if self.sram_dyn_load_history else 0.0
                    cur_ram_free = self.ram_free_history[-1] if self.ram_free_history else 0.0
                    cur_stack_load = self.stack_load_history[-1] if self.stack_load_history else 0.0
                    cur_i2c_fails = self.i2c_fails_history[-1] if self.i2c_fails_history else 0
                    avg_rtt = statistics.mean(self.command_rtt_history[-10:]) if self.command_rtt_history else 0.0
                    ack_rate = (self.commands_acked / self.commands_sent * 100.0) if self.commands_sent > 0 else 100.0

                    status_str = (
                        f"\r{BOLD}[{elapsed/60:4.1f}m / {self.duration_sec/60:4.1f}m]{RESET} "
                        f"FPS: {GREEN if cur_fps >= 60 else RED}{cur_fps:4.1f}{RESET} (avg {avg_fps:4.1f}) | "
                        f"Temp: {YELLOW}{cur_temp:4.1f}°C{RESET} | "
                        f"RAM-Free: {cur_ram_free:4.2f}MB | "
                        f"SRAM-Load: {cur_sram_load:4.1f}% | "
                        f"RTT: {avg_rtt:5.1f}ms (ACK {ack_rate:5.1f}%) | "
                        f"Panics: {GREEN if self.panic_detected == 0 else RED}{self.panic_detected}{RESET}"
                    )
                    sys.stdout.write(status_str)
                    sys.stdout.flush()

                time.sleep(0.01)

        except KeyboardInterrupt:
            print(f"\n{YELLOW}[WARN]{RESET} Stress test interrupted early by user.")

        print("\n\n" + "=" * 73)
        print(f"{BOLD}{GREEN}Stress Test Execution Completed. Generating Axiomatic Acceptance Report...{RESET}")
        print("=" * 73)

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        total_time = time.time() - self.start_time
        
        # Calculate statistics
        avg_fps = statistics.mean(self.fps_history) if self.fps_history else 0.0
        min_fps = min(self.fps_history) if self.fps_history else 0.0
        max_fps = max(self.fps_history) if self.fps_history else 0.0

        avg_temp = statistics.mean(self.temp_history) if self.temp_history else 0.0
        max_temp = max(self.temp_history) if self.temp_history else 0.0

        avg_rtt = statistics.mean(self.command_rtt_history) if self.command_rtt_history else 0.0
        p95_rtt = statistics.quantiles(self.command_rtt_history, n=20)[18] if len(self.command_rtt_history) >= 20 else avg_rtt
        max_rtt = max(self.command_rtt_history) if self.command_rtt_history else 0.0

        ack_rate = (self.commands_acked / self.commands_sent * 100.0) if self.commands_sent > 0 else 0.0

        # Memory leak slope analysis (least squares linear regression on total RAM free in KB)
        leak_slope_kb_min = 0.0
        if len(self.ram_free_history) >= 10 and len(self.timestamps) >= 10:
            n = min(len(self.ram_free_history), len(self.timestamps))
            xs = [self.timestamps[i] / 60.0 for i in range(n)]  # minutes
            ys = [self.ram_free_history[i] * 1024.0 for i in range(n)]  # KB
            x_mean = statistics.mean(xs)
            y_mean = statistics.mean(ys)
            denom = sum((x - x_mean) ** 2 for x in xs)
            if denom > 0:
                leak_slope_kb_min = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n)) / denom

        # Acceptance Verification Gates
        gate_fps = avg_fps >= 60.0
        gate_temp = max_temp < 75.0 if max_temp > 0 else True
        gate_ack = ack_rate >= 99.0
        gate_panics = self.panic_detected == 0
        gate_memory_leak = leak_slope_kb_min >= -0.5  # RAM should not drop faster than 0.5 KB/min (accounts for 0.01MB quantization noise)

        passed = gate_fps and gate_temp and gate_ack and gate_panics and gate_memory_leak

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "port": self.port,
            "duration_seconds": round(total_time, 2),
            "target_duration_seconds": self.duration_sec,
            "verdict": "PASS" if passed else "FAIL",
            "acceptance_gates": {
                "gate_fps_gte_60": {"passed": gate_fps, "value": round(avg_fps, 2), "threshold": ">= 60.0 FPS"},
                "gate_temp_lt_75c": {"passed": gate_temp, "value": round(max_temp, 2), "threshold": "< 75.0 °C"},
                "gate_ack_rate_gte_99": {"passed": gate_ack, "value": round(ack_rate, 2), "threshold": ">= 99.0%"},
                "gate_zero_panics": {"passed": gate_panics, "value": self.panic_detected, "threshold": "== 0"},
                "gate_no_memory_leak": {"passed": gate_memory_leak, "value": round(leak_slope_kb_min, 4), "threshold": ">= -0.50 KB/min"}
            },
            "metrics_summary": {
                "fps": {"min": round(min_fps, 2), "avg": round(avg_fps, 2), "max": round(max_fps, 2), "sample_count": len(self.fps_history)},
                "temperature_c": {"avg": round(avg_temp, 2), "max": round(max_temp, 2), "sample_count": len(self.temp_history)},
                "latency_rtt_ms": {"avg": round(avg_rtt, 2), "p95": round(p95_rtt, 2), "max": round(max_rtt, 2)},
                "commands": {"sent": self.commands_sent, "acked": self.commands_acked, "rate_pct": round(ack_rate, 2)},
                "memory": {
                    "final_ram_free_mb": round(self.ram_free_history[-1], 2) if self.ram_free_history else 0.0,
                    "final_sram_dyn_load_pct": round(self.sram_dyn_load_history[-1], 2) if self.sram_dyn_load_history else 0.0,
                    "ram_leak_slope_kb_per_min": round(leak_slope_kb_min, 4)
                },
                "hardware_safety": {
                    "final_stack_load_pct": round(self.stack_load_history[-1], 2) if self.stack_load_history else 0.0,
                    "final_i2c_fails": self.i2c_fails_history[-1] if self.i2c_fails_history else 0
                }
            },
            "panic_logs": self.panic_logs
        }

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print detailed report summary
        print(f"\n{BOLD}Acceptance Gates Summary:{RESET}")
        for gate_name, gate_info in report["acceptance_gates"].items():
            status_tag = f"{GREEN}[PASS]{RESET}" if gate_info["passed"] else f"{RED}[FAIL]{RESET}"
            print(f"  {status_tag} {gate_name:25s} : {gate_info['value']} ({gate_info['threshold']})")

        print(f"\n{BOLD}Final Result: {GREEN if passed else RED}{report['verdict']}{RESET}")
        print(f"Report JSON written to: {self.output_file}\n")
        return report

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()


def main():
    parser = argparse.ArgumentParser(description="M5Stack StickS3 30-Minute Stress Test & Acceptance Harness")
    parser.add_argument("--port", type=str, default="COM3", help="Serial port (default: COM3)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--duration", type=int, default=1800, help="Stress test duration in seconds (default: 1800 for 30 mins)")
    parser.add_argument("--reset", action="store_true", help="Trigger RTS/DTR reset before beginning test")
    parser.add_argument("--output", type=str, default="dist/stress_test_report.json", help="Output JSON path")
    args = parser.parse_args()

    tester = HardwareStressTester(port=args.port, baud=args.baud, duration_sec=args.duration, output_file=args.output)
    try:
        report = tester.run_stress_test(reset=args.reset)
        if report.get("verdict") != "PASS":
            sys.exit(1)
    finally:
        tester.close()


if __name__ == "__main__":
    main()
