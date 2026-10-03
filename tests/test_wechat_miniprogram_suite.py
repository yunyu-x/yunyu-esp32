"""
tests/test_wechat_miniprogram_suite.py
--------------------------------------
微信小程序全量配置、资源、页面组件与 JavaScript 工具库端到端工程验证
- 验证 app.json, project.config.json, project.private.config.json, sitemap.json 合规性
- 验证 TabBar 4 大导航栏及高保真 PNG 图标存在性与图片头格式
- 验证四大页面 (index, feed, diary, settings) 及 avatar-canvas 组件文件四件套
- 验证 utils 核心模块 (BLE, Wi-Fi, 渲染器, 存储, 加密, 触觉反馈) 的契约与导出
- 验证 Node.js 编译/语法无报错 (node -c)
- 验证 miniprogram-ci 自动化上传脚本逻辑
"""

import os
import json
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MP_DIR = os.path.join(ROOT_DIR, "wechat_miniprogram")


def test_miniprogram_json_configs():
    """验证微信小程序核心配置文件格式与结构完整性"""
    # 1. app.json
    app_json_path = os.path.join(MP_DIR, "app.json")
    assert os.path.exists(app_json_path), "必须存在 app.json"
    with open(app_json_path, "r", encoding="utf-8") as f:
        app_cfg = json.load(f)

    assert "pages" in app_cfg, "app.json 必须定义 pages"
    expected_pages = [
        "pages/index/index",
        "pages/feed/feed",
        "pages/diary/diary",
        "pages/settings/settings"
    ]
    for p in expected_pages:
        assert p in app_cfg["pages"], f"app.json 缺少页面定义: {p}"

    assert "window" in app_cfg
    assert app_cfg["window"].get("navigationBarTextStyle") in ("white", "black")

    assert "tabBar" in app_cfg
    tab_list = app_cfg["tabBar"].get("list", [])
    assert len(tab_list) == 4, f"TabBar 必须包含 4 个标签页，当前为 {len(tab_list)}"

    # 2. project.config.json
    proj_json_path = os.path.join(MP_DIR, "project.config.json")
    assert os.path.exists(proj_json_path), "必须存在 project.config.json"
    with open(proj_json_path, "r", encoding="utf-8") as f:
        proj_cfg = json.load(f)
    assert "appid" in proj_cfg, "project.config.json 必须配置 appid"
    assert proj_cfg.get("compileType") == "miniprogram", "compileType 必须为 miniprogram"
    assert proj_cfg.get("setting", {}).get("es6") is True, "必须开启 ES6 转 ES5"

    # 3. sitemap.json
    sitemap_path = os.path.join(MP_DIR, "sitemap.json")
    assert os.path.exists(sitemap_path), "必须存在 sitemap.json"
    with open(sitemap_path, "r", encoding="utf-8") as f:
        sitemap_cfg = json.load(f)
    assert "rules" in sitemap_cfg, "sitemap.json 必须包含 rules 规则"


def test_miniprogram_tabbar_assets():
    """验证 TabBar 4 大图标及选中图标的物理文件与 PNG 签名完整性"""
    app_json_path = os.path.join(MP_DIR, "app.json")
    with open(app_json_path, "r", encoding="utf-8") as f:
        app_cfg = json.load(f)

    tab_list = app_cfg["tabBar"]["list"]
    png_signature = b"\x89PNG\r\n\x1a\n"

    for tab in tab_list:
        icon_path = os.path.join(MP_DIR, tab["iconPath"])
        selected_icon_path = os.path.join(MP_DIR, tab["selectedIconPath"])

        assert os.path.exists(icon_path), f"TabBar 默认图标文件缺失: {tab['iconPath']}"
        assert os.path.exists(selected_icon_path), f"TabBar 激活图标文件缺失: {tab['selectedIconPath']}"

        with open(icon_path, "rb") as f:
            header = f.read(8)
            assert header == png_signature, f"图标文件 {tab['iconPath']} 不是有效的 PNG 图像"

        with open(selected_icon_path, "rb") as f:
            header = f.read(8)
            assert header == png_signature, f"图标文件 {tab['selectedIconPath']} 不是有效的 PNG 图像"


def test_miniprogram_pages_and_components_structure():
    """验证四大页面与自定义组件的四件套 (js, json, wxml, wxss) 完备性"""
    pages = ["index", "feed", "diary", "settings"]
    for p in pages:
        p_dir = os.path.join(MP_DIR, "pages", p)
        for ext in [".js", ".json", ".wxml", ".wxss"]:
            fpath = os.path.join(p_dir, f"{p}{ext}")
            assert os.path.exists(fpath), f"页面 {p} 缺失文件: {p}{ext}"
            assert os.path.getsize(fpath) > 0, f"页面文件不可为空: {fpath}"

    comp_dir = os.path.join(MP_DIR, "components", "avatar-canvas")
    for ext in [".js", ".json", ".wxml", ".wxss"]:
        fpath = os.path.join(comp_dir, f"avatar-canvas{ext}")
        assert os.path.exists(fpath), f"组件 avatar-canvas 缺失文件: avatar-canvas{ext}"
        assert os.path.getsize(fpath) > 0, f"组件文件不可为空: {fpath}"

    # 校验 avatar-canvas.json 声明了 component: true
    with open(os.path.join(comp_dir, "avatar-canvas.json"), "r", encoding="utf-8") as f:
        comp_json = json.load(f)
    assert comp_json.get("component") is True, "avatar-canvas.json 必须设置 component: true"


def test_miniprogram_utils_contracts():
    """验证 utils 目录中全部核心模块的工程实现契约"""
    utils_dir = os.path.join(MP_DIR, "utils")
    expected_utils = [
        "avatar_renderer.js",
        "buddy_service.js",
        "crypto_guard.js",
        "haptics.js",
        "sticks3_ble.js",
        "sticks3_wifi.js",
        "storage_manager.js"
    ]
    for u in expected_utils:
        fpath = os.path.join(utils_dir, u)
        assert os.path.exists(fpath), f"缺失工具库文件: {u}"
        with open(fpath, "r", encoding="utf-8") as f:
            src = f.read()

        # 针对每个模块的特性断言
        if u == "avatar_renderer.js":
            assert "AvatarRenderer" in src
            assert "drawEye" in src or "drawFace" in src or "render" in src
        elif u == "buddy_service.js":
            assert "getPetStatus" in src or "sendPetAction" in src or "BuddyService" in src or "fetch" in src
        elif u == "crypto_guard.js":
            assert "encrypt" in src or "decrypt" in src or "Crypto" in src or "KEY" in src
        elif u == "haptics.js":
            assert "vibrate" in src or "vibrateShort" in src
        elif u == "sticks3_ble.js":
            assert "0000FFB0" in src
            assert "writeInChunks" in src
        elif u == "sticks3_wifi.js":
            assert "provision" in src or "connect" in src or "wifi" in src.lower()
        elif u == "storage_manager.js":
            assert "getStorage" in src or "setStorage" in src or "DEFAULT" in src


def test_miniprogram_js_syntax_via_node():
    """使用 Node.js 对小程序内所有 JavaScript 源文件执行静态语法编译检测 (node -c)"""
    js_files = []
    for root, dirs, files in os.walk(MP_DIR):
        if any(d in root for d in ["node_modules", ".git"]):
            continue
        for f in files:
            if f.endswith(".js"):
                js_files.append(os.path.join(root, f))

    assert len(js_files) >= 10, f"发现的 JS 文件过少 ({len(js_files)} 个)，检查项目完整性"

    syntax_errors = []
    for f in js_files:
        res = subprocess.run(["node", "-c", f], capture_output=True, text=True)
        if res.returncode != 0:
            syntax_errors.append((f, res.stderr))

    assert not syntax_errors, f"发现 JS 语法错误:\n" + "\n".join([f"{p}: {err}" for p, err in syntax_errors])


def test_miniprogram_ci_upload_script():
    """验证 miniprogram-ci 官方自动化上传脚本"""
    upload_script = os.path.join(MP_DIR, "upload.js")
    assert os.path.exists(upload_script), "upload.js 必须存在"
    with open(upload_script, "r", encoding="utf-8") as f:
        src = f.read()

    assert "miniprogram-ci" in src, "upload.js 必须依赖 miniprogram-ci"
    assert "ci.Project" in src
    assert "ci.upload" in src
    assert "wxe41eb3a86da4e4e8" in src, "必须配置合法的 AppID"


def test_ble_utf8_cross_chunk_reassembly():
    """公理六验证：测试 BLE 0xFFB1 记忆分片跨包边界撕裂 UTF-8 字符时的二进制组包无乱码还原"""
    node_script = """
    const { StickS3BLEClient } = require('./wechat_miniprogram/utils/sticks3_ble.js');
    const client = new StickS3BLEClient();

    const expectedUser = "你好悄悄，今天北京天气怎么样？";
    const expectedAi = "北京今天晴空万里，温度适宜，微风拂面，很适合外出散步哦！";
    const payloadJson = JSON.stringify({
        total: 1,
        next_id: 2,
        turns: [{
            id: 1,
            time: "+10s",
            user: expectedUser,
            ai: expectedAi,
            voice: "Tina"
        }]
    });

    const fullBytes = Buffer.from(payloadJson, 'utf-8');
    const CHUNK_SIZE = 48; // 模拟硬件 48 字节切片，精准切断 3 字节汉字
    const totalChunks = Math.ceil(fullBytes.length / CHUNK_SIZE);

    let receivedList = null;
    client.onMemoryReceived = (list) => {
        receivedList = list;
    };

    // 逐片推送，故意在汉字多字节内部切割
    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const slice = fullBytes.subarray(start, start + CHUNK_SIZE);
        const header = Buffer.from(`[C:${i + 1}/${totalChunks}]`);
        const packet = Buffer.concat([header, slice]);
        client.handleMemoryChunk(packet);
    }

    if (!receivedList || receivedList.length === 0) {
        console.error("FAIL: No memory turns received");
        process.exit(1);
    }

    const turn = receivedList[0];
    if (turn.user !== expectedUser) {
        console.error(`FAIL: User text mismatch. Got '${turn.user}', expected '${expectedUser}'`);
        process.exit(2);
    }
    if (turn.ai !== expectedAi) {
        console.error(`FAIL: AI text mismatch. Got '${turn.ai}', expected '${expectedAi}'`);
        process.exit(3);
    }

    console.log("SUCCESS: UTF-8 cross-chunk memory reassembly passed with 0 Mojibake!");
    """

    res = subprocess.run(["node", "-e", node_script], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"BLE 分包 UTF-8 组包测试失败: {res.stderr}\n{res.stdout}"
    assert "SUCCESS" in res.stdout


def test_avatar_subtitle_dynamic_rendering():
    """公理三与公理六验证：测试微表情 Canvas 字幕气泡动态解包与中文字符边界折行保护"""
    node_script = """
    const { AvatarRenderer } = require('./wechat_miniprogram/utils/avatar_renderer.js');
    const renderer = new AvatarRenderer();

    const filledLines = [];
    const mockCtx = {
        fillStyle: "",
        font: "",
        strokeStyle: "",
        lineWidth: 1,
        clearRect: () => {},
        fillRect: () => {},
        save: () => {},
        restore: () => {},
        scale: () => {},
        beginPath: () => {},
        arc: () => {},
        fill: () => {},
        stroke: () => {},
        moveTo: () => {},
        lineTo: () => {},
        arcTo: () => {},
        rect: () => {},
        closePath: () => {},
        measureText: (str) => {
            let w = 0;
            for (let c of str) {
                w += c.charCodeAt(0) > 127 ? 10 : 5.5;
            }
            return { width: w };
        },
        fillText: (text, x, y) => {
            filledLines.push({ text, x, y });
        }
    };

    // 1. 测试从 JSON 日记解包并正确折行
    const jsonDiary = JSON.stringify({
        time: 12345,
        diary: "今天在桌面上晒太阳，等待主人下一次唤醒我，心底暖洋洋的~"
    });
    renderer.drawSubtitleText(mockCtx, { diary: jsonDiary });

    if (filledLines.length === 0) {
        console.error("FAIL: No subtitle lines rendered");
        process.exit(1);
    }

    // 校验前导行没有多余的 JSON 花括号
    const firstLine = filledLines[0].text;
    if (firstLine.includes("{") || firstLine.includes("diary")) {
        console.error("FAIL: JSON was not unwrapped properly:", firstLine);
        process.exit(2);
    }

    console.log("SUCCESS: Avatar subtitle dynamic renderer passed!");
    """

    res = subprocess.run(["node", "-e", node_script], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"字幕气泡动态渲染测试失败: {res.stderr}\n{res.stdout}"
    assert "SUCCESS" in res.stdout

