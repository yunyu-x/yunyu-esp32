#!/usr/bin/env python3
"""
tests/firmware_drivers/build_test_binaries.py
Compiles native C++ test binaries using g++ for local pytest test suites.
"""

import os
import subprocess
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEST_DIR = os.path.join(ROOT_DIR, "tests", "firmware_drivers")
FW_MSRR_INC = os.path.join(ROOT_DIR, "firmware", "esp32_msrr_firmware", "include")
FW_MSRR_SRC = os.path.join(ROOT_DIR, "firmware", "esp32_msrr_firmware", "src")
FW_BUDDY_INC = os.path.join(ROOT_DIR, "firmware", "m5sticks3_buddy", "include")
FW_BUDDY_SRC = os.path.join(ROOT_DIR, "firmware", "m5sticks3_buddy", "src")

BUILD_CONFIGS = [
    {
        "output": "test_sticks3_hal.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_sticks3_hal.cpp"),
            os.path.join(FW_BUDDY_SRC, "sticks3_hal.cpp"),
        ],
        "includes": [FW_BUDDY_INC],
    },
    {
        "output": "test_buddy_protocol.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_buddy_protocol.cpp"),
            os.path.join(FW_BUDDY_SRC, "buddy_protocol.cpp"),
        ],
        "includes": [FW_BUDDY_INC],
    },
    {
        "output": "test_driver_hub.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_driver_hub.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "driver_hub.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
    {
        "output": "test_motor_driver.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_motor_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "motor_driver.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
    {
        "output": "test_epm_driver.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_epm_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "epm_driver.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
    {
        "output": "test_imu_driver.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_imu_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "imu_mpu6050.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
    {
        "output": "test_power_bms.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_power_bms.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "power_bms.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
    {
        "output": "test_optical_driver.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_optical_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "optical_mesh_driver.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
    {
        "output": "test_all_drivers_main.exe",
        "sources": [
            os.path.join(TEST_DIR, "test_all_drivers_main.cpp"),
            os.path.join(FW_MSRR_SRC, "hal", "mock_hal.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "driver_hub.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "motor_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "epm_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "imu_mpu6050.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "power_bms.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "optical_mesh_driver.cpp"),
            os.path.join(FW_MSRR_SRC, "drivers", "led_driver.cpp"),
        ],
        "includes": [FW_MSRR_INC],
    },
]

def build_all():
    print("Building all C++ native test binaries using g++...")
    success = True
    for cfg in BUILD_CONFIGS:
        out_path = os.path.join(TEST_DIR, cfg["output"])
        cmd = ["g++", "-std=c++17"]
        for inc in cfg["includes"]:
            cmd.extend(["-I", inc])
        cmd.extend(cfg["sources"])
        cmd.extend(["-o", out_path])
        
        print(f"  -> Compiling {cfg['output']}...", end=" ", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("[OK]")
        else:
            print("[FAILED]")
            print(res.stderr)
            success = False
    return success

if __name__ == "__main__":
    if not build_all():
        sys.exit(1)
    print("All test binaries compiled successfully!")
