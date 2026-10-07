#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for 30-Minute Continuous Stress Test Script & Telemetry Parsers
=====================================================================
Validates telemetry parsing, metric bounds checking, acceptance gate logic,
and JSON reporting functions of scripts/stress_test_30min.py.
"""

import os
import sys
import json
import pytest

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from scripts.stress_test_30min import HardwareStressTester, SYS_METRICS_REGEX, STATUS_JSON_REGEX, CHAT_JSON_REGEX, PANIC_REGEX


def test_regex_sys_metrics_parsing():
    sample_log = "[StickS3-SYS] FPS: 89.8 | Temp: 54.2C | RAM: free=7.30MB (Load: 12.0%) | SRAM: free=67KB, max_block=49KB (DynLoad: 51.9%) | Stack: free=5164B (Load: 37.0%) | I2C_Tx: 730 (Fails: 0)"
    m = SYS_METRICS_REGEX.search(sample_log)
    assert m is not None
    assert float(m.group("fps")) == pytest.approx(89.8)
    assert float(m.group("temp")) == pytest.approx(54.2)
    assert float(m.group("ram_free")) == pytest.approx(7.30)
    assert float(m.group("ram_load")) == pytest.approx(12.0)
    assert int(m.group("sram_free")) == 67
    assert float(m.group("sram_dyn_load")) == pytest.approx(51.9)
    assert int(m.group("stack_free")) == 5164
    assert float(m.group("stack_load")) == pytest.approx(37.0)
    assert int(m.group("i2c_tx")) == 730
    assert int(m.group("i2c_fails")) == 0


def test_regex_status_json_parsing():
    sample_status = '@status {"board":"M5Stack StickS3","chat":true,"device":{"wifi":{"state":"connected","mode":"WiFi","ip":"192.168.110.67"},"hatch":{"state":"connected"},"v_bus":4.12,"fps":95.5,"temp_c":50.8,"face":"active"}}'
    m = STATUS_JSON_REGEX.search(sample_status)
    assert m is not None
    data = json.loads(m.group(1))
    assert data["board"] == "M5Stack StickS3"
    assert data["device"]["v_bus"] == pytest.approx(4.12)
    assert data["device"]["fps"] == pytest.approx(95.5)
    assert data["device"]["temp_c"] == pytest.approx(50.8)


def test_regex_panic_detection():
    assert PANIC_REGEX.search("Guru Meditation Error: Core 0 panic'ed") is not None
    assert PANIC_REGEX.search("abort() was called at PC 0x400551") is not None
    assert PANIC_REGEX.search("CORRUPT HEAP: multi_heap.c") is not None
    assert PANIC_REGEX.search("rst:0x1 (POWERON_RESET)") is not None
    assert PANIC_REGEX.search("[StickS3-SYS] FPS: 95.8 | Temp: 51.4C") is None


def test_acceptance_gate_logic():
    out_file = os.path.join(WORKSPACE_ROOT, "dist", "test_report_temp.json")
    try:
        tester = HardwareStressTester(port="COM3", duration_sec=60, output_file=out_file)
        tester.start_time = 1000.0
        
        # Simulate healthy telemetry history
        for i in range(20):
            tester.timestamps.append(i * 3.0)
            tester.fps_history.append(94.5 + (i % 3) * 0.5)
            tester.temp_history.append(50.0 + (i % 2) * 0.2)
            tester.ram_free_history.append(7.30)
            tester.ram_load_history.append(12.0)
            tester.sram_dyn_load_history.append(51.9)
            tester.stack_load_history.append(37.0)
            tester.i2c_fails_history.append(0)
            tester.command_rtt_history.append(25.0 + (i % 5))
            tester.commands_sent += 1
            tester.commands_acked += 1

        report = tester.generate_report()
        assert report["verdict"] == "PASS"
        assert report["acceptance_gates"]["gate_fps_gte_60"]["passed"] is True
        assert report["acceptance_gates"]["gate_temp_lt_75c"]["passed"] is True
        assert report["acceptance_gates"]["gate_ack_rate_gte_99"]["passed"] is True
        assert report["acceptance_gates"]["gate_zero_panics"]["passed"] is True
        assert report["acceptance_gates"]["gate_no_memory_leak"]["passed"] is True
        assert os.path.exists(out_file)
    finally:
        if os.path.exists(out_file):
            try:
                os.remove(out_file)
            except Exception:
                pass
