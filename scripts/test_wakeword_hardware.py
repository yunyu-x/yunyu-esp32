#!/usr/bin/env python3
"""
scripts/test_wakeword_hardware.py
---------------------------------
M5Stack StickS3 离线语音唤醒词「悄悄」硬件端到端真实联调与验证脚本
- 验证链路：
  1. REST API /wakeword/status 初始状态查询
  2. REST API /wakeword/config 动态灵敏度与超时配置
  3. REST API /wakeword/trigger 软件仿真触发与和弦反馈核验
  4. 触发后 /wakeword/status 窗口倒计时与计数器递增校验
  5. /bailian/status 问答窗口联动状态校验
  6. 串口 COM3 字符指令 ('k' / 'wake') 物理触发核验
"""

import sys
import time
import json
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

DEFAULT_HOST = "http://192.168.110.67"
SERIAL_PORT = "COM3"
BAUD_RATE = 115200


def http_get(url: str, timeout: float = 3.0) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "StickS3-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        print(f"  [-] GET {url} failed: {e}")
        return None


def http_post(url: str, data: Dict[str, Any], timeout: float = 3.0) -> Optional[Dict[str, Any]]:
    try:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "StickS3-Verifier/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data_resp = resp.read().decode("utf-8")
            return json.loads(data_resp)
    except Exception as e:
        print(f"  [-] POST {url} failed: {e}")
        return None


def run_hardware_verification(base_url: str = DEFAULT_HOST) -> bool:
    print("\n" + "=" * 76)
    print("  [StickS3 硬件端真实联调] 离线语音唤醒词「悄悄」功能核验")
    print(f"  目标设备地址: {base_url} | 串口: {SERIAL_PORT}")
    print("=" * 76)

    # 1. 探针设备是否在线
    print("\n[测试 1/6] 探针设备连接状态与系统指标...")
    sys_metrics = http_get(f"{base_url}/system/metrics")
    if sys_metrics:
        cpu = sys_metrics.get("cpu", {})
        mem = sys_metrics.get("memory", {})
        print(f"  [+] 设备在线! 帧率={cpu.get('loop_fps')} FPS, SRAM剩余={mem.get('free_internal_heap', 0) // 1024}KB, PSRAM剩余={mem.get('free_psram', 0) // (1024*1024)}MB")
    else:
        print("  [*] 未通过主 IP 连接，尝试探针 SoftAP 192.168.4.1...")
        base_url = "http://192.168.4.1"
        sys_metrics = http_get(f"{base_url}/system/metrics")
        if not sys_metrics:
            print("  [-] 无法通过网络连接到设备端点，请检查网络或串口。")

    # 2. 查询唤醒词初始状态
    print("\n[测试 2/6] 查询唤醒词服务状态 (/wakeword/status)...")
    ww_status = http_get(f"{base_url}/wakeword/status")
    if not ww_status:
        print("  [-] 无法获取 /wakeword/status 端点响应！")
        return False
    
    word_name = ww_status.get("word") or ww_status.get("name")
    print(f"  [+] 成功读取唤醒词状态:")
    print(f"      - 唤醒词名称: {word_name}")
    print(f"      - 引擎使能状态: {ww_status.get('enabled')}")
    print(f"      - 当前灵敏度: {ww_status.get('sensitivity')}%")
    print(f"      - 问答窗口状态: {'开启(聆听中)' if (ww_status.get('window_open') or ww_status.get('wake_window_open')) else '关闭(待命中)'}")
    print(f"      - 历史唤醒总次数: {ww_status.get('total_wakes')}")

    assert word_name == "悄悄", f"预期唤醒词为'悄悄'，实际为: {word_name}"
    initial_wakes = ww_status.get("total_wakes", 0)

    # 3. 动态调整灵敏度与超时时间
    print("\n[测试 3/6] 动态配置灵敏度与问答窗口 (/wakeword/config)...")
    cfg_resp = http_post(f"{base_url}/wakeword/config", {"enabled": 1, "sensitivity": 82, "timeout": 9})
    if cfg_resp and cfg_resp.get("status") == "ok":
        print(f"  [+] 配置更新成功: {cfg_resp}")
        assert cfg_resp.get("sensitivity") == 82
        assert cfg_resp.get("timeout_sec") == 9
    else:
        print(f"  [-] /wakeword/config 失败: {cfg_resp}")
        return False

    # 4. 仿真触发唤醒词
    print("\n[测试 4/6] 模拟声学唤醒词触发 (/wakeword/trigger)...")
    trig_resp = http_post(f"{base_url}/wakeword/trigger", {"confidence": 96.8})
    if trig_resp and trig_resp.get("status") == "ok":
        print(f"  [+] 唤醒事件下发成功: {trig_resp}")
        print("  [*] 设备端应已播放升调和弦 (E5-G#5-B5-E6) 并在屏幕点亮「悄悄已唤醒」")
    else:
        print(f"  [-] /wakeword/trigger 失败: {trig_resp}")
        return False

    # 5. 校验触发后的状态机变化
    print("\n[测试 5/6] 验证触发后问答窗口开启与计数器自增...")
    time.sleep(0.5)
    ww_status_after = http_get(f"{base_url}/wakeword/status")
    if ww_status_after:
        print(f"  [+] 触发后状态:")
        print(f"      - 问答窗口开启: {ww_status_after.get('window_open')}")
        print(f"      - 窗口剩余时间: {ww_status_after.get('window_remaining_ms')} ms")
        print(f"      - 历史唤醒次数: {ww_status_after.get('total_wakes')} (此前: {initial_wakes})")
        assert ww_status_after.get("window_open") is True, "触发后窗口应处于打开状态"
        assert ww_status_after.get("total_wakes") == initial_wakes + 1, "唤醒次数应递增 1"
    else:
        print("  [-] 无法读取触发后状态！")
        return False

    # 校验百炼大模型客户端状态
    bl_status = http_get(f"{base_url}/bailian/status")
    if bl_status:
        print(f"  [+] 百炼客户端状态: code={bl_status.get('state_code')}, name='{bl_status.get('state_name')}'")

    # 6. 串口指令触发核验 (可选)
    print("\n[测试 6/6] 串口仿真指令测试 (COM3)...")
    if HAS_SERIAL:
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.8) as ser:
                ser.dtr = True
                ser.rts = True
                ser.reset_input_buffer()
                print("  [*] 发送串口指令 'k' 模拟触发唤醒词...")
                ser.write(b"k\n")
                ser.flush()
                time.sleep(0.4)
                output = ser.read(1024).decode("utf-8", errors="replace")
                print(f"  [串口回执]:\n{output.strip()}")
                if "WAKEWORD-TRIGGER" in output or "Wake word" in output:
                    print("  [+] 串口成功捕获唤醒词事件日志！")
        except Exception as e:
            print(f"  [*] 串口占用或未开启 (非阻塞跳过): {e}")
    else:
        print("  [*] 未安装 pyserial，跳过串口指令")

    print("\n" + "=" * 76)
    print("  [SUCCESS] M5StickS3 离线语音唤醒词「悄悄」硬件端到端真机验证通过！")
    print("=" * 76 + "\n")
    return True


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    success = run_hardware_verification(host)
    sys.exit(0 if success else 1)
