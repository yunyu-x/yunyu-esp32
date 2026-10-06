#!/usr/bin/env python3
"""
scripts/bailian_muse_cloud_agent.py
-----------------------------------
Local Bailian Cloud Agent Server Entry Point for yunyu-esp32.
Replaces Meta Muse Secure VM with Alibaba Cloud Bailian (Qwen2.5 / DashScope) intelligence.

Features:
1. Meta Muse Protocol Compatible Endpoints:
   - GET /health, GET /fetch_vms, GET /api/device/info, GET /api/robot/telemetry
   - POST /api/chat, POST /chat/stream, GET /chat/subscribe (SSE)
   - POST /api/voice/dictation (Push-to-Talk 16kHz PCM transcription)
   - POST /api/robot/roll, /api/robot/epm, /api/robot/morphology, /api/robot/reflex, /api/robot/avatar_face
   - GET/POST /rpc/<skill_name>.<method_name>
2. Alibaba Cloud Bailian Integration:
   - Reads DASHSCOPE_API_KEY from environment or command line.
   - Embodied Function Calling tools (LingCube dynamics + StickS3 Avatar expressions).
   - Seamless degradation to Intelligent Mock mode when offline or without API key.
3. StickS3 Serial Hatch Protocol Bus:
   - Real-time bidirectional console on COM3 (115200bps).
4. Automatic Public Tunneling:
   - Cloudflare Quick Tunnel (zero-login) / ngrok failover.
   - Automatically writes endpoints to dist/public_agent_url.json and dist/public_preview_url.txt.
   - Exposes GET /api/tunnel/info.
"""

import os
import sys
import time
import signal
import argparse
import logging

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from simulation.bridge.bailian_muse_cloud_agent import BailianMuseCloudAgent

logger = logging.getLogger("bailian-cloud-entry")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s")


def print_banner(agent: BailianMuseCloudAgent):
    sep = "=" * 76
    print("\n" + sep)
    print("  🤖 阿里云百炼云端 Agent 宿主服务已启动 (Bailian Muse Cloud Agent Online)")
    print(sep)
    print(f"  ▶ 本地服务地址:   http://127.0.0.1:{agent.port}")
    print(f"  ▶ 实时语音双工:   ws://127.0.0.1:{agent.port}/ws/v1/realtime")
    print(f"  ▶ Meta VM 发现:   http://127.0.0.1:{agent.port}/fetch_vms")
    print(f"  ▶ 设备遥测状态:   http://127.0.0.1:{agent.port}/api/robot/telemetry")
    print(f"  ▶ 串口 Hatch 总线: {'COM3 监听中' if agent.enable_serial else '已禁用 (--no-serial)'}")
    print(f"  ▶ 大模型推理引擎: {'阿里云百炼 Qwen (DashScope 在线)' if agent.engine.is_online() else '智能 Mock 模式 (离线高保真平替)'}")
    print(f"  ▶ 公网穿透模式:   {agent.tunnel_mode.upper()}")
    print(f"  ▶ 地址记录文件:   {os.path.join(WORKSPACE_ROOT, 'dist', 'public_agent_url.json')}")
    print(sep + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="阿里云百炼 Cloud Agent 本地替代服务 (Meta Muse Alternative Server)"
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="HTTP 监听地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP 监听端口 (默认: 8000)")
    parser.add_argument("--serial-port", type=str, default="COM3", help="StickS3 物理串口端口 (默认: COM3)")
    parser.add_argument("--enable-serial", action="store_true", help="显式启用串口 Hatch 监听 (默认不启动物理串口)")
    parser.add_argument("--no-serial", action="store_true", help="禁用串口 Hatch 监听")
    parser.add_argument(
        "--tunnel",
        choices=["auto", "cloudflare", "ngrok", "none"],
        default="none",
        help="公网穿透模式: auto (自动探测与降级), cloudflare, ngrok, none (默认: none)"
    )
    parser.add_argument("--api-key", type=str, default=None, help="阿里云 DashScope API Key (默认从环境变量 DASHSCOPE_API_KEY 读取)")
    parser.add_argument("--mock-llm", action="store_true", help="强制启用智能 Mock LLM 模式")

    args = parser.parse_args()

    enable_serial = args.enable_serial and not args.no_serial

    agent = BailianMuseCloudAgent(
        host=args.host,
        port=args.port,
        serial_port=args.serial_port,
        enable_serial=enable_serial,
        tunnel_mode=args.tunnel,
        api_key=args.api_key,
        force_mock_llm=args.mock_llm
    )

    print_banner(agent)

    # Clean signal handling
    def sig_handler(sig, frame):
        print("\n[i] 接收到退出信号，正在优雅关闭 Bailian Cloud Agent...")
        agent.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    try:
        agent.start(blocking=True)
    except KeyboardInterrupt:
        print("\n[i] 用户中断，正在关闭服务...")
        agent.stop()


if __name__ == "__main__":
    main()
