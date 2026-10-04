"""
tests/test_embedded_device_inspector_skill.py
---------------------------------------------
测试 embedded-device-inspector 独立技能规范与嵌入式实时诊断解析引擎的完整性
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(ROOT_DIR, "skills", "embedded-device-inspector")
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")

sys.path.insert(0, SCRIPTS_DIR)


def test_skill_manifest_and_docs():
    """验证 SKILL.md 文档的 YAML frontmatter 规范与技术指南完整性"""
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    assert os.path.exists(skill_md), "SKILL.md 必须存在"

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    assert content.startswith("---"), "SKILL.md 必须包含 YAML frontmatter 起始标志"
    assert "name: embedded-device-inspector" in content
    assert "description:" in content
    assert "M5Stack StickS3" in content
    assert "rst:0x" in content
    assert "Guru Meditation" in content
    assert "TTFA" in content
    assert "70%" in content


def test_skill_wrapper_script_exists():
    """验证技能专属脚本 monitor_service.py 存在且语法正常"""
    script_path = os.path.join(SKILL_DIR, "scripts", "monitor_service.py")
    assert os.path.exists(script_path), "monitor_service.py 必须存在"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "EmbeddedMonitor" in content


def test_monitor_telemetry_and_metrics_parsing():
    """验证监控诊断引擎对 [StickS3-SYS] 遥测数据的正则表达式精准解析"""
    from embedded_monitor_service import EmbeddedMonitor

    # 使用虚拟实例（不打开真实串口）
    monitor = EmbeddedMonitor.__new__(EmbeddedMonitor)
    monitor.total_lines = 0
    monitor.start_time = 1000.0
    monitor.last_seen_time = 1000.0
    monitor.bailian_state = "UNKNOWN"
    monitor.speech_start_time = None
    monitor.thinking_start_time = None
    monitor.last_user_query = ""
    monitor.last_ai_reply = ""
    monitor.stuck_events = []
    monitor.reboot_count = 0
    monitor.reboot_events = []
    monitor.last_backtrace = []
    monitor.overload_alerts = []
    monitor.last_metrics = {
        "fps": 0.0,
        "ram_load": 0.0,
        "ram_free_mb": 0.0,
        "sram_dyn_load": 0.0,
        "sram_free_kb": 0,
        "stack_load": 0.0,
        "stack_free_b": 0,
        "i2c_fails": 0
    }

    # 模拟喂入标准的硬件遥测行
    telemetry_line = "[StickS3-SYS] FPS: 93.4 | RAM: free=7.30MB (Load: 12.0%) | SRAM: free=74KB, max_block=59KB (DynLoad: 47.1%) | Stack: free=5192B (Load: 36.6%) | I2C_Tx: 1049 (Fails: 0)"
    monitor.process_line(telemetry_line)

    assert monitor.last_metrics["fps"] == pytest.approx(93.4, 0.1)
    assert monitor.last_metrics["ram_load"] == pytest.approx(12.0, 0.1)
    assert monitor.last_metrics["ram_free_mb"] == pytest.approx(7.30, 0.1)
    assert monitor.last_metrics["sram_dyn_load"] == pytest.approx(47.1, 0.1)
    assert monitor.last_metrics["sram_free_kb"] == 74
    assert monitor.last_metrics["stack_load"] == pytest.approx(36.6, 0.1)
    assert monitor.last_metrics["stack_free_b"] == 5192
    assert monitor.last_metrics["i2c_fails"] == 0
    assert len(monitor.overload_alerts) == 0


def test_monitor_reboot_and_panic_detection():
    """验证对 rst:0xc、rst:0x4 与 Guru Meditation Panic 重启的识别捕获"""
    from embedded_monitor_service import EmbeddedMonitor

    monitor = EmbeddedMonitor.__new__(EmbeddedMonitor)
    monitor.total_lines = 0
    monitor.start_time = 1000.0
    monitor.last_seen_time = 1000.0
    monitor.bailian_state = "UNKNOWN"
    monitor.speech_start_time = None
    monitor.thinking_start_time = None
    monitor.last_user_query = ""
    monitor.last_ai_reply = ""
    monitor.stuck_events = []
    monitor.reboot_count = 0
    monitor.reboot_events = []
    monitor.last_backtrace = []
    monitor.overload_alerts = []
    monitor.last_metrics = {}

    # 1. 喂入崩溃行
    monitor.process_line("CORRUPT HEAP: Bad tail at 0x3fcd7e24. Expected 0xbaad5678 got 0x3fcd7d70")
    monitor.process_line("assert failed: multi_heap_free multi_heap_poisoning.c:259 (head != NULL)")
    monitor.process_line("Backtrace: 0x40378226:0x3fcce8f0 0x40380f71:0x3fcce910")
    
    # 2. 喂入复位行
    monitor.process_line("rst:0xc (RTC_SW_CPU_RST),boot:0x28 (SPI_FAST_FLASH_BOOT)")

    assert monitor.reboot_count == 1
    assert len(monitor.reboot_events) == 1
    assert monitor.reboot_events[0]["code"] == "0xc"


def test_monitor_stuck_and_freeze_detection():
    """验证对大模型思考中途直接跳回 Listening (未出声) 的卡顿判定机制"""
    import time
    from embedded_monitor_service import EmbeddedMonitor

    monitor = EmbeddedMonitor.__new__(EmbeddedMonitor)
    monitor.total_lines = 0
    monitor.start_time = time.time()
    monitor.last_seen_time = time.time()
    monitor.bailian_state = "UNKNOWN"
    monitor.speech_start_time = None
    monitor.thinking_start_time = None
    monitor.last_user_query = ""
    monitor.last_ai_reply = ""
    monitor.stuck_events = []
    monitor.reboot_count = 0
    monitor.reboot_events = []
    monitor.last_backtrace = []
    monitor.overload_alerts = []
    monitor.last_metrics = {}

    # 模拟进入思考
    monitor.process_line("[BAILIAN-STATE] 3 -> 4 (思考中...)")
    assert monitor.thinking_start_time is not None

    time.sleep(0.05)

    # 模拟无音频直接切回倾听 (卡顿事件)
    monitor.process_line("[BAILIAN-STATE] 4 -> 3 (正在聆听...)")
    assert len(monitor.stuck_events) == 1
    assert "未产出任何音频" in monitor.stuck_events[0]["reason"]
