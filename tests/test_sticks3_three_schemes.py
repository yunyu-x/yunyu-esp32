"""
tests/test_sticks3_three_schemes.py
-----------------------------------
Automated pytest suite for M5Stack StickS3 three development schemes:
- Scheme 1: M5Burner Zero-Code Flashing & Hardware Probe Pipeline
- Scheme 2: VS Code + PlatformIO Embedded Driver Stack & C++ SIL Tests
- Scheme 3: Claude Desktop Buddy BLE Protocol & Robot Telemetry Extension
"""

import os
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
FW_TESTS_DIR = os.path.join(ROOT_DIR, "tests", "firmware_drivers")
FW_DIR = os.path.join(ROOT_DIR, "firmware", "m5sticks3_buddy")


# ==========================================
# 方案 1 自动化验证 (Scheme 1 Verification)
# ==========================================

def test_scheme1_m5burner_and_probe():
    """验证方案 1：M5Burner 工具链、硬件端口探测与固件元数据校验"""
    script_path = os.path.join(SCRIPTS_DIR, "verify_scheme1_m5burner.py")
    assert os.path.exists(script_path), f"Script not found: {script_path}"

    res = subprocess.run([os.sys.executable, script_path], capture_output=True, text=True)
    assert res.returncode == 0, f"Scheme 1 failed:\n{res.stdout}\n{res.stderr}"
    assert "Scheme 1 (M5Burner Zero-Code Verification) PASSED" in res.stdout
    assert "ESP32-S3 native USB-CDC signature" in res.stdout
    assert "Bootloader Sequence Timing" in res.stdout


# ==========================================
# 方案 2 自动化验证 (Scheme 2 Verification)
# ==========================================

def test_scheme2_platformio_config():
    """验证方案 2：PlatformIO 工程配置基线合法性"""
    ini_path = os.path.join(FW_DIR, "platformio.ini")
    assert os.path.exists(ini_path), f"platformio.ini not found: {ini_path}"

    with open(ini_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "board = esp32-s3-devkitc-1" in content
    assert "board_build.mcu = esp32s3" in content
    assert "ARDUINO_USB_CDC_ON_BOOT=1" in content
    assert "BOARD_HAS_PSRAM" in content
    assert "M5Unified" in content
    assert "M5GFX" in content


def test_scheme2_cxx_driver_suite():
    """验证方案 2：StickS3 HAL 驱动、按键防抖状态机、M5PM1 电源门控原生 C++ SIL 测试"""
    exe_path = os.path.join(FW_TESTS_DIR, "test_sticks3_hal.exe")
    assert os.path.exists(exe_path), f"Binary not found: {exe_path}"

    res = subprocess.run([exe_path], capture_output=True, text=True)
    assert res.returncode == 0, f"Scheme 2 C++ tests failed:\n{res.stdout}\n{res.stderr}"
    assert "Scheme 2 (PlatformIO & Driver Suite) PASSED" in res.stdout
    assert "Button debounce, click, and long-press verified" in res.stdout
    assert "PowerManager M5PM1 5V gate & battery SOC verified" in res.stdout
    assert "DisplayEngine ST7789 screen contexts and frame synthesis verified" in res.stdout


# ==========================================
# 方案 3 自动化验证 (Scheme 3 Verification)
# ==========================================

def test_scheme3_cxx_protocol_engine():
    """验证方案 3：Claude Desktop Buddy C++ 协议引擎单元测试"""
    exe_path = os.path.join(FW_TESTS_DIR, "test_buddy_protocol.exe")
    assert os.path.exists(exe_path), f"Binary not found: {exe_path}"

    res = subprocess.run([exe_path], capture_output=True, text=True)
    assert res.returncode == 0, f"Scheme 3 C++ tests failed:\n{res.stdout}\n{res.stderr}"
    assert "Scheme 3 (Claude Desktop Buddy Protocol) PASSED" in res.stdout
    assert "State message parsed successfully" in res.stdout
    assert "Permission parsing, approval & deny serialization verified" in res.stdout
    assert "Fragmented BLE packet stream concatenation verified" in res.stdout
    assert "Robot telemetry extension serialization verified" in res.stdout


def test_scheme3_python_ble_simulation():
    """验证方案 3：Claude Desktop 与 StickS3 双向交互端到端仿真闭环"""
    script_path = os.path.join(SCRIPTS_DIR, "verify_scheme3_buddy_ble.py")
    assert os.path.exists(script_path), f"Script not found: {script_path}"

    res = subprocess.run([os.sys.executable, script_path], capture_output=True, text=True)
    assert res.returncode == 0, f"Scheme 3 simulation failed:\n{res.stdout}\n{res.stderr}"
    assert "Scheme 3 (Claude Desktop Buddy & Extension) PASSED" in res.stdout
    assert "Physical Gate Approve" in res.stdout
    assert "Physical Gate Intercept" in res.stdout
    assert "LingCube Telemetry Extension" in res.stdout


# ==========================================
# 硬件实机点亮全生命周期自动化验证 (Bring-Up Suite)
# ==========================================

def test_bringup_firmware_sources_exist():
    """验证实机点亮固件源码与头文件完整性"""
    main_src = os.path.join(FW_DIR, "src", "main.cpp")
    hal_src = os.path.join(FW_DIR, "src", "sticks3_hal.cpp")
    proto_src = os.path.join(FW_DIR, "src", "buddy_protocol.cpp")
    gbk_hdr = os.path.join(FW_DIR, "include", "gbk_to_utf8.h")

    assert os.path.exists(main_src), f"main.cpp not found at {main_src}"
    assert os.path.exists(hal_src), f"sticks3_hal.cpp not found at {hal_src}"
    assert os.path.exists(proto_src), f"buddy_protocol.cpp not found at {proto_src}"
    assert os.path.exists(gbk_hdr), f"gbk_to_utf8.h not found at {gbk_hdr}"

    # 验证 main.cpp 包含双模仪表盘、姿态水准仪、BLE NUS 与审批弹窗融合逻辑
    with open(main_src, "r", encoding="utf-8") as f:
        content = f.read()
    assert "M5StickS3" in content
    assert "fillCircle(ball_x, ball_y" in content
    assert "6e400001-b5a3-f393-e0a9-e50e24dcca9e" in content
    assert "APPROVAL" in content
    assert "serializeAction" in content
    assert "drawChineseText" in content
    assert "sanitizeAndConvertToUtf8" in content


def test_bringup_manager_cli_all():
    """验证统一点亮调度器 CLI --all 全套自动化执行"""
    mgr_script = os.path.join(SCRIPTS_DIR, "sticks3_bringup_manager.py")
    assert os.path.exists(mgr_script), f"Manager script not found at {mgr_script}"

    res = subprocess.run([os.sys.executable, mgr_script, "--all"], capture_output=True, text=True)
    assert res.returncode == 0, f"Bring-up manager failed:\n{res.stdout}\n{res.stderr}"
    assert "BRING-UP 方案 1" in res.stdout
    assert "BRING-UP 方案 2" in res.stdout
    assert "BRING-UP 方案 3" in res.stdout
    assert "三大方案硬件点亮工作全部顺利完成" in res.stdout

