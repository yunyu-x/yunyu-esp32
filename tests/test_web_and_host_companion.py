"""
tests/test_web_and_host_companion.py
------------------------------------
Web 前端控制台、3D 结构爆炸图、开放平台科普指南与上位机伴侣服务全链路自动化测试
- 验证 web/ 与 web_preview/ 下静态 HTML 资源引用 (CSS / JS / Vendor) 的本地完整性
- 验证 create_web_app FastAPI 伴侣服务器路由与页面响应 (/companion, /exploded, /guide, /simulation)
- 验证 REST API (/api/health, /pet/status, /pet/action, /pet/memory, /pet/diary, /pet/rag/search) 交互契约
- 验证 scripts/preview_tunnel.py 穿透工具探测与 URL 持久化逻辑
- 验证 scripts/lingbuddy_vector_store.py 对话与日记的语义嵌入、持久化与 RAG 导出
"""

import os
import re
import json
import tempfile
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEB_DIR = os.path.join(ROOT_DIR, "web")

from scripts.lingbuddy_companion import create_web_app, LingBuddySimulatorClient
from scripts.lingbuddy_vector_store import LingBuddyVectorStore
import scripts.preview_tunnel as pt


def test_web_html_and_assets_integrity():
    """验证 HTML 页面中引用的 CSS、JS、Vendor 脚本与字体等静态资源本地均存在"""
    html_files = [
        os.path.join(WEB_DIR, "lingbuddy_companion.html"),
        os.path.join(WEB_DIR, "exploded_view.html"),
        os.path.join(WEB_DIR, "index.html"),
        os.path.join(WEB_DIR, "open_platform_guide.html"),
    ]

    for h in html_files:
        assert os.path.exists(h), f"HTML 文件不存在: {h}"
        with open(h, "r", encoding="utf-8") as f:
            content = f.read()

        file_dir = os.path.dirname(h)

        # 检查样式表引用
        links = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', content)
        for l in links:
            if l.startswith(("http://", "https://", "data:")):
                continue
            clean_l = l.split("?")[0]
            full_path = os.path.normpath(os.path.join(file_dir, clean_l))
            assert os.path.exists(full_path), f"{os.path.basename(h)} 引用的样式文件缺失: {clean_l} ({full_path})"

        # 检查脚本引用
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
        for s in scripts:
            if s.startswith(("http://", "https://", "data:")):
                continue
            clean_s = s.split("?")[0]
            full_path = os.path.normpath(os.path.join(file_dir, clean_s))
            assert os.path.exists(full_path), f"{os.path.basename(h)} 引用的脚本文件缺失: {clean_s} ({full_path})"

    # 验证关键 vendor 库存在
    for vendor_lib in ["three.min.js", "OrbitControls.js", "chart.umd.min.js"]:
        vp = os.path.join(WEB_DIR, "vendor", vendor_lib)
        assert os.path.exists(vp), f"缺少必要 Vendor 库: {vendor_lib}"
        assert os.path.getsize(vp) > 1000, f"Vendor 库大小异常: {vendor_lib}"


def test_web_companion_server_endpoints():
    """验证 Web 伴侣控制台服务的基础 HTTP 路由与页面渲染"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = tmp.name

    try:
        sim = LingBuddySimulatorClient(name="悄悄")
        vs = LingBuddyVectorStore(db_path=tmp_db)
        app = create_web_app(simulator=sim, vector_store=vs)
        client = TestClient(app)

        # 1. / 根路由与 /companion 伴侣页
        r_root = client.get("/")
        assert r_root.status_code == 200
        assert "LingBuddy" in r_root.text

        r_comp = client.get("/companion")
        assert r_comp.status_code == 200
        assert "LingBuddy" in r_comp.text

        # 2. /exploded 3D 爆炸图
        r_exp = client.get("/exploded")
        assert r_exp.status_code == 200
        assert "3D" in r_exp.text

        # 3. /simulation 多体仿真
        r_sim = client.get("/simulation")
        assert r_sim.status_code == 200

        # 4. /guide 开放平台科普指南
        r_guide = client.get("/guide")
        assert r_guide.status_code == 200
        assert "开放平台" in r_guide.text

        # 5. /api/health 健康探针
        r_health = client.get("/api/health")
        assert r_health.status_code == 200
        data = r_health.json()
        assert data["status"] == "ok"
        assert data["service"] == "lingbuddy_companion"
        assert data["device"] == "M5StickS3"

    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)


def test_web_companion_pet_api_lifecycle():
    """验证 Web 控制台与 StickS3 伴侣状态同步及拓麻歌子互动 API"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = tmp.name

    try:
        sim = LingBuddySimulatorClient(name="悄悄测试版")
        vs = LingBuddyVectorStore(db_path=tmp_db)
        app = create_web_app(simulator=sim, vector_store=vs)
        client = TestClient(app)

        # 1. 初始状态获取
        st = client.get("/pet/status").json()
        assert st["name"] == "悄悄测试版"
        assert st["level"] == 1
        assert st["energy"] == 100
        assert st["feeds"] == 0

        # 2. 注入投喂 (JSON 格式)
        r_feed = client.post("/pet/action", json={"action": "feed", "value": "草莓曲奇"})
        assert r_feed.status_code == 200
        feed_data = r_feed.json()
        assert feed_data["feeds"] == 1
        assert "草莓曲奇" in feed_data["diary"]

        # 3. 注入抚摸 (表单格式，与网页端一致)
        r_pet = client.post("/pet/action", data={"action": "pet"})
        assert r_pet.status_code == 200
        pet_data = r_pet.json()
        assert pet_data["pets"] == 1

        # 4. 注入记忆
        r_mem = client.post("/pet/inject_memory", json={"memory": "下周二在深圳参展交流"})
        assert r_mem.status_code == 200

        # 5. 获取分块记忆
        r_chunks = client.get("/pet/memory").json()
        assert len(r_chunks["turns"]) >= 3
        assert len(r_chunks["chunks"]) > 0

        # 6. 获取日记流
        r_diary = client.get("/pet/diary").json()
        assert len(r_diary["diary"]) >= 3

        # 7. 语义检索 RAG
        r_search = client.get("/pet/rag/search?q=深圳参展").json()
        assert len(r_search["hits"]) >= 1
        assert "深圳" in r_search["hits"][0]["content"]

    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)


def test_preview_tunnel_helpers(monkeypatch):
    """测试 preview_tunnel 模块的辅助方法与服务状态检测"""
    # 探针测试无效端口
    assert pt.is_service_alive(59999) is False

    # 测试持久化 URL
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_txt = os.path.join(tmp_dir, "preview.txt")
        tmp_json = os.path.join(tmp_dir, "preview.json")
        monkeypatch.setattr(pt, "OUTPUT_DIR", tmp_dir)
        monkeypatch.setattr(pt, "URL_FILE_TXT", tmp_txt)
        monkeypatch.setattr(pt, "URL_FILE_JSON", tmp_json)

        pt.save_public_url("https://lingbuddy-test.trycloudflare.com", "cloudflare", 8000)

        assert os.path.exists(tmp_txt)
        assert os.path.exists(tmp_json)

        with open(tmp_txt, "r", encoding="utf-8") as f:
            assert "lingbuddy-test.trycloudflare.com" in f.read()

        with open(tmp_json, "r", encoding="utf-8") as f:
            jdata = json.load(f)
            assert jdata["tool"] == "cloudflare"
            assert jdata["local_port"] == 8000
