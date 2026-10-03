"""
tests/test_public_service_tunnel_skill.py
-----------------------------------------
测试 public-service-tunnel 通用技能与工具套件的完整性与功能闭环
"""

import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(ROOT_DIR, "skills", "public-service-tunnel")
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")

sys.path.insert(0, SCRIPTS_DIR)


def test_skill_manifest_and_docs():
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    assert os.path.exists(skill_md), "SKILL.md 必须存在"
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.startswith("---"), "SKILL.md 必须包含 YAML frontmatter 起始标志"
    assert "name: public-service-tunnel" in content
    assert "description:" in content
    assert "ERR_NGROK_334" in content
    assert "Cloudflare" in content


def test_install_tools_module():
    from install_tools import get_system_info, get_binary_name, DOWNLOAD_MATRIX, check_tool_installed

    system, machine = get_system_info()
    assert system in ("windows", "linux", "darwin")
    bin_name = get_binary_name("ngrok", system)
    assert bin_name.endswith(".exe") if system == "windows" else not bin_name.endswith(".exe")

    # 检查下载矩阵完整性
    assert "windows" in DOWNLOAD_MATRIX["ngrok"]
    assert "linux" in DOWNLOAD_MATRIX["ngrok"]
    assert "darwin" in DOWNLOAD_MATRIX["ngrok"]
    assert "windows" in DOWNLOAD_MATRIX["cloudflared"]


def test_service_probe_module():
    from service_probe import probe_endpoint

    # 测试无法访问的无效端口应返回 alive=False 且不抛未捕获异常
    res = probe_endpoint("http://127.0.0.1:59999", timeout=0.5)
    assert res["alive"] is False
    assert res["status_code"] == 0
    assert res["error"] is not None


def test_tunnel_manager_helpers():
    from tunnel_manager import get_binary_path, is_port_listening, DEFAULT_TOOLS_DIR

    ngrok_path = get_binary_path("ngrok", DEFAULT_TOOLS_DIR)
    assert ngrok_path is not None

    # 未开启端口的监听状态检测
    assert is_port_listening(59998) is False


def test_examples_and_templates():
    example_cfg = os.path.join(SKILL_DIR, "examples", "config.example.json")
    quick_start = os.path.join(SKILL_DIR, "examples", "quick_start.py")

    assert os.path.exists(example_cfg), "配置样例文档必须存在"
    assert os.path.exists(quick_start), "快速入门示例脚本必须存在"
