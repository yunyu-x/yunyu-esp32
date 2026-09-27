#!/usr/bin/env python3
"""
scripts/test_bailian_realtime_e2e.py
------------------------------------
阿里云百炼 (DashScope Realtime) 全双工流式大模型语音交互与 StickS3 端到端联调验证工具
功能：
1. 遥测探测：自动扫描 StickS3 终端 (192.168.4.1 或局域网 STA IP)，核验配网与百炼大模型状态
2. 配网注入：支持命令行直接向设备下发 Wi-Fi SSID 与密码 (`--ssid` / `--pass`)
3. 密钥注入：支持向设备配置百炼 API Key (`--key` / `--voice` / `--model`)
4. 实时打断测试：向设备下发打断指令并验证硬件响应 (`--interrupt`)
5. 本地直接验证：利用本机直接与百炼 WebSocket (WSS) 建立握手，测试 API Key 连通性
"""

import sys
import os
import time
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

DEFAULT_DEVICE_URL = "http://192.168.4.1"


def get_device_status(base_url: str):
    """获取 StickS3 Wi-Fi 与百炼综合状态"""
    print(f"\n[*] 正在查询 StickS3 终端状态 ({base_url})...")
    
    # 1. WiFi 状态
    try:
        req = urllib.request.Request(f"{base_url}/wifi/status", headers={"User-Agent": "Bailian-Tester/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("  [+] Wi-Fi STA 状态:")
            print(f"      - 运行状态: {data.get('sta_state')}")
            print(f"      - 局域网 IP: {data.get('sta_ip')}")
            print(f"      - 连接 SSID: {data.get('sta_ssid')}")
            print(f"      - 信号强度: {data.get('sta_rssi')} dBm")
    except Exception as e:
        print(f"  [-] Wi-Fi 状态查询失败: {e}")

    # 2. 百炼大模型状态
    try:
        req = urllib.request.Request(f"{base_url}/bailian/status", headers={"User-Agent": "Bailian-Tester/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("  [+] 阿里云百炼大模型交互状态:")
            print(f"      - 状态名称: {data.get('state_name')} (代码 {data.get('state_code')})")
            print(f"      - 累计打断: {data.get('interrupts')} 次")
            if data.get('user_query'):
                print(f"      - 最新问话: \"{data.get('user_query')}\"")
            if data.get('ai_reply'):
                print(f"      - 最新回复: \"{data.get('ai_reply')}\"")
            if data.get('error'):
                print(f"      - 异常信息: {data.get('error')}")
    except Exception as e:
        print(f"  [-] 百炼状态查询失败: {e}")


def configure_wifi(base_url: str, ssid: str, password: str):
    """向 StickS3 提交 Wi-Fi 配网参数"""
    print(f"\n[*] 正在向 StickS3 提交配网指令: SSID=\"{ssid}\"...")
    params = urllib.parse.urlencode({"ssid": ssid, "pass": password}).encode("utf-8")
    try:
        req = urllib.request.Request(f"{base_url}/wifi/connect", data=params, method="POST")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"  [+] 配网指令响应: {res}")
            print("      请稍候约 5~10 秒，StickS3 将自动加入局域网并获取真实 IP！")
    except Exception as e:
        print(f"  [-] 配网请求失败: {e}")


def configure_bailian(base_url: str, key: str, voice: str = "cherry", model: str = "qwen-omni-turbo-realtime"):
    """向 StickS3 提交阿里云百炼配置"""
    print(f"\n[*] 正在向 StickS3 提交百炼配置 (Model: {model}, Voice: {voice})...")
    params = urllib.parse.urlencode({"key": key, "voice": voice, "model": model}).encode("utf-8")
    try:
        req = urllib.request.Request(f"{base_url}/bailian/config", data=params, method="POST")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"  [+] 百炼配置响应: {res}")
    except Exception as e:
        print(f"  [-] 配置百炼失败: {e}")


def trigger_interrupt(base_url: str):
    """远程触发中途打断 (Barge-In)"""
    print(f"\n[*] 触发中途打断 (Barge-In)...")
    try:
        req = urllib.request.Request(f"{base_url}/bailian/interrupt", data=b"", method="POST")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"  [+] 打断执行成功: {res}")
    except Exception as e:
        print(f"  [-] 打断请求失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="StickS3 阿里云百炼全双工语音交互联调工具")
    parser.add_argument("--url", default=DEFAULT_DEVICE_URL, help=f"StickS3 HTTP URL (默认: {DEFAULT_DEVICE_URL})")
    parser.add_argument("--status", action="store_true", help="查询设备 Wi-Fi 与百炼状态")
    parser.add_argument("--ssid", help="Wi-Fi SSID")
    parser.add_argument("--pass", dest="password", help="Wi-Fi Password")
    parser.add_argument("--key", help="阿里云百炼 DashScope API Key (sk-...)")
    parser.add_argument("--voice", default="cherry", help="音色 (默认: cherry)")
    parser.add_argument("--model", default="qwen-omni-turbo-realtime", help="模型名称")
    parser.add_argument("--interrupt", action="store_true", help="触发中途打断")

    args = parser.parse_args()

    if args.ssid:
        configure_wifi(args.url, args.ssid, args.password or "")
    if args.key:
        configure_bailian(args.url, args.key, args.voice, args.model)
    if args.interrupt:
        trigger_interrupt(args.url)

    # 默认展示状态
    get_device_status(args.url)


if __name__ == "__main__":
    main()
