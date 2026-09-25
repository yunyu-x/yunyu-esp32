"""
tests/test_firmware_driver_suite.py
-----------------------------------
Automated pytest test suite for microUnit embedded device drivers:
- Verifies DriverHub & dynamic hot-pluggable face slots.
- Verifies DRV8833 motor driver soft-start ramp & dynamic braking.
- Verifies EPM electropermanent magnet pulse timing & thermal watchdog.
- Verifies MPU-6050 6-DOF IMU & Q4 PMOS hardware cold-reset deadlock self-healing.
- Verifies Power & BMS 12-bit ADC, EMA filtering, LiPo SOC estimation, and sag protection.
- Verifies 6-Face Optical Mesh transceiver, COBS framing, and CRC16 validation.
- Verifies full system Power-On Self-Test (POST) and fault isolation.
"""

import os
import subprocess
import pytest

TEST_DIR = os.path.dirname(__file__)
FW_TEST_DIR = os.path.join(TEST_DIR, "firmware_drivers")


def run_binary(exe_name: str):
    exe_path = os.path.join(FW_TEST_DIR, exe_name)
    assert os.path.exists(exe_path), f"Test executable not found: {exe_path}"
    res = subprocess.run([exe_path], capture_output=True, text=True)
    assert res.returncode == 0, f"{exe_name} failed with code {res.returncode}:\n{res.stdout}\n{res.stderr}"
    return res.stdout


def test_driver_hub_and_hotplug():
    """验证 DriverHub 驱动中枢、热插拔与卡槽扩缩容"""
    output = run_binary("test_driver_hub.exe")
    assert "ALL HUB TESTS PASSED SUCCESSFULLY" in output


def test_motor_driver():
    """验证 DRV8833 动力驱动、软启动斜坡、急刹短路制动与 nFAULT 故障捕获"""
    output = run_binary("test_motor_driver.exe")
    assert "ALL MOTOR TESTS PASSED SUCCESSFULLY" in output


def test_epm_driver():
    """验证 EPM 双稳态电永磁 5.0ms 充退磁脉宽、热节流限制与硬件 RC 看门狗"""
    output = run_binary("test_epm_driver.exe")
    assert "ALL EPM TESTS PASSED SUCCESSFULLY" in output


def test_imu_mpu6050_and_cold_reset():
    """验证 MPU-6050 姿态传感器 500Hz 采集与 Q4 PMOS 硬件冷复位断电自愈"""
    output = run_binary("test_imu_driver.exe")
    assert "ALL IMU TESTS PASSED SUCCESSFULLY" in output


def test_power_bms_driver():
    """验证 DW01A/TP4056/ADC 电源驱动、12位过采样、SOC 非线性估算与欠压告警"""
    output = run_binary("test_power_bms.exe")
    assert "ALL BMS TESTS PASSED SUCCESSFULLY" in output


def test_optical_mesh_driver():
    """验证 6 面红外光通信驱动、COBS 封包、CRC16 校验与拓扑邻接感知"""
    output = run_binary("test_optical_driver.exe")
    assert "ALL OPTICAL TESTS PASSED SUCCESSFULLY" in output


def test_system_driver_suite_master():
    """验证全系统所有 6 大驱动集成 POST 自检、协同运行与故障隔离"""
    output = run_binary("test_all_drivers_main.exe")
    assert "[100% ACCEPTANCE] ALL DRIVERS FULLY VERIFIED" in output
