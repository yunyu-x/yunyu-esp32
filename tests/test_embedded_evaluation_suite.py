"""
tests/test_embedded_evaluation_suite.py
----------------------------------------
验证 M5StickS3 嵌入式整体效果验收评估套件 (embedded_evaluation_suite.py) 的逻辑完备性与门禁契约
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from embedded_evaluation_suite import SerialCollector, EmbeddedEvaluator


def test_serial_collector_telemetry_regex():
    """验证串口遥测帧的精准正则捕获与字段解包"""
    collector = SerialCollector()
    
    line = "[StickS3-SYS] FPS: 85.3 | Temp: 61.5C | RAM: free=7.45MB (Load: 10.2%) | SRAM: free=128KB, max_block=110KB (DynLoad: 4.5%) | Stack: free=5200B (Load: 36.5%) | I2C_Tx: 1250 (Fails: 0)"
    m = collector.sys_re.search(line)
    assert m is not None, "必须成功匹配 [StickS3-SYS] 遥测帧"
    
    fps = float(m.group(1))
    temp = float(m.group(2))
    ram_mb = float(m.group(3))
    ram_load = float(m.group(4))
    sram_kb = int(m.group(5))
    max_block = int(m.group(6))
    dyn_load = float(m.group(7))
    stack_free = int(m.group(8))
    stack_load = float(m.group(9))
    i2c_tx = int(m.group(10))
    i2c_fails = int(m.group(11))
    
    assert fps == pytest.approx(85.3, 0.1)
    assert temp == pytest.approx(61.5, 0.1)
    assert ram_mb == pytest.approx(7.45, 0.01)
    assert ram_load == pytest.approx(10.2, 0.1)
    assert sram_kb == 128
    assert max_block == 110
    assert dyn_load == pytest.approx(4.5, 0.1)
    assert stack_free == 5200
    assert stack_load == pytest.approx(36.5, 0.1)
    assert i2c_tx == 1250
    assert i2c_fails == 0


def test_serial_collector_rst_detection():
    """验证对异常重启复位码的捕获"""
    collector = SerialCollector()
    
    # 常规复位
    assert collector.rst_re.search("rst:0x15 (USB_UART_CHIP_RESET)").group(1) == "0x15"
    # 异常复位
    m_panic = collector.rst_re.search("rst:0x4 (OWDT_RESET / ESP_RST_PANIC)")
    assert m_panic is not None
    assert m_panic.group(1).lower() == "0x4"


def test_evaluator_gate_evaluation_passing():
    """验证四阶门禁判定在合格数据下的全绿判定"""
    evaluator = EmbeddedEvaluator.__new__(EmbeddedEvaluator)
    evaluator.results = {
        "subsystems": {
            "fluency": {
                "target_fps_met": True,
                "action_fps_avg": 72.5,
                "action_fps_min": 58.0
            },
            "physical": {
                "temp_safe": True,
                "chip_temp_c_max": 62.0,
                "sram_safe": True,
                "sram_free_kb_min": 115,
                "sram_dyn_load_max": 12.0,
                "stack_safe": True,
                "stack_free_b_min": 4800,
                "stack_load_max": 41.5,
                "i2c_zero_fail": True,
                "i2c_total_fails": 0
            },
            "buttons": {
                "robustness_pass": True,
                "reboot_count": 0,
                "panic_count": 0,
                "device_alive_after_hammer": True
            },
            "dialogue": {
                "dialogue_pass": True,
                "rounds_completed": 5,
                "test_rounds_planned": 5,
                "reboot_count": 0,
                "barge_in_avg_latency_ms": 145.0
            }
        },
        "gates_passed": False,
        "gate_failures": []
    }

    evaluator._evaluate_gates()
    assert evaluator.results["gates_passed"] is True
    assert len(evaluator.results["gate_failures"]) == 0


def test_evaluator_gate_evaluation_failing_on_i2c():
    """验证一票否决：I2C 失败时门禁必须判 Fail (公理五)"""
    evaluator = EmbeddedEvaluator.__new__(EmbeddedEvaluator)
    evaluator.results = {
        "subsystems": {
            "fluency": {"target_fps_met": True},
            "physical": {
                "temp_safe": True,
                "sram_safe": True,
                "stack_safe": True,
                "i2c_zero_fail": False,
                "i2c_total_fails": 2  # 出现 I2C 失败
            },
            "buttons": {"robustness_pass": True},
            "dialogue": {"dialogue_pass": True}
        },
        "gates_passed": True,
        "gate_failures": []
    }

    evaluator._evaluate_gates()
    assert evaluator.results["gates_passed"] is False
    assert any("I2C" in f for f in evaluator.results["gate_failures"])
