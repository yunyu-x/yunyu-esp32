#!/usr/bin/env python3
"""
tests/test_avatar_and_empathy.py
---------------------------------
M5StickS3 灵宠伴侣 (LingBuddy / StickCharm) 微表情引擎、具身动力学与 BLE 记忆同步测试套件
- 覆盖维度：
  1. 12 种程序化微表情状态机转换逻辑仿真
  2. 麦克风 VU 音量与瞳孔动态缩放映射公式检验
  3. 下行流式音频 RMS 与嘴型开合高度解算校验
  4. BMI270 物理体感检测 (剧烈晃动晕眩、温和轻摇抚摸、静止超时入睡)
  5. BLE 伴侣 GATT 同步服务 (0xFFB0) 契约与特征值定义断言
  6. 固件源码静态契约与 API 路由完整性断言
"""

import math
import os
import re
import pytest

FW_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy"))
AVATAR_H = os.path.join(FW_ROOT, "include", "sticks3_avatar.h")
BLE_SYNC_H = os.path.join(FW_ROOT, "include", "sticks3_ble_sync.h")
MAIN_CPP = os.path.join(FW_ROOT, "src", "main.cpp")


class MockAvatarPhysics:
    """Python 镜像仿真 Avatar 物理与情感动力学引擎"""
    def __init__(self):
        self.intimacy_level = 1
        self.intimacy_xp = 15
        self.total_pets = 0
        self.total_shakes = 0
        self.current_mood = "MOOD_IDLE"
        self.target_mood = "MOOD_IDLE"
        self.dizzy_until = 0
        self.happy_until = 0
        self.last_interaction = 0
        self.pupil_r = 7.0
        self.mouth_h = 2.0

    def set_mood(self, mood: str):
        self.target_mood = mood
        self.current_mood = mood

    def add_intimacy(self, xp: int):
        self.intimacy_xp += xp
        if self.intimacy_xp >= 100 and self.intimacy_level < 10:
            self.intimacy_level += 1
            self.intimacy_xp = 0

    def update(self, now: int, ax: float, ay: float, az: float, roll: float, pitch: float, mic_rms: int, spk_rms: int):
        a_mag = math.sqrt(ax * ax + ay * ay + az * az)

        # 剧烈摇晃检测 (a_mag > 2.3g)
        if a_mag > 2.3:
            self.total_shakes += 1
            self.dizzy_until = now + 3500
            self.current_mood = "MOOD_DIZZY"
            self.last_interaction = now
        elif self.dizzy_until > now:
            self.current_mood = "MOOD_DIZZY"
        else:
            # 轻抚检测
            delta_a = abs(a_mag - 1.0)
            if 0.18 < delta_a < 0.65 and self.current_mood in ("MOOD_IDLE", "MOOD_SLEEP"):
                self.total_pets += 1
                self.add_intimacy(1)
                self.happy_until = now + 2500
                self.current_mood = "MOOD_HAPPY"
                self.last_interaction = now
            elif self.happy_until > now:
                self.current_mood = "MOOD_HAPPY"
            else:
                # 平放静止入睡检测 (>90s)
                is_flat = (abs(roll) < 18.0 and abs(pitch) < 18.0 and abs(a_mag - 1.0) < 0.15)
                if is_flat and (now - self.last_interaction > 90000):
                    self.current_mood = "MOOD_SLEEP"
                elif self.target_mood != "MOOD_IDLE":
                    self.current_mood = self.target_mood
                else:
                    self.current_mood = "MOOD_IDLE"

        # 瞳孔动态收缩
        if self.current_mood == "MOOD_LISTEN":
            target_r = min(14.0, 7.0 + mic_rms * 0.08)
            self.pupil_r = self.pupil_r * 0.65 + target_r * 0.35
        else:
            self.pupil_r = self.pupil_r * 0.8 + 7.0 * 0.2

        # 嘴唇开合高度
        if self.current_mood == "MOOD_SPEAK":
            target_mouth = min(18.0, 2.0 + spk_rms * 0.18)
            self.mouth_h = self.mouth_h * 0.6 + target_mouth * 0.4
        else:
            self.mouth_h = 2.0


def test_avatar_mood_transitions_and_physics():
    engine = MockAvatarPhysics()
    assert engine.current_mood == "MOOD_IDLE"
    assert engine.intimacy_level == 1

    # 1. 模拟静止状态，瞳孔保持基础半径 7.0px
    engine.update(now=1000, ax=0.0, ay=0.0, az=1.0, roll=0.0, pitch=0.0, mic_rms=0, spk_rms=0)
    assert engine.current_mood == "MOOD_IDLE"
    assert abs(engine.pupil_r - 7.0) < 0.5

    # 2. 模拟轻抚机身 (合加速度小幅波动 1.35g)
    engine.update(now=2000, ax=0.2, ay=0.2, az=1.3, roll=5.0, pitch=5.0, mic_rms=0, spk_rms=0)
    assert engine.current_mood == "MOOD_HAPPY"
    assert engine.total_pets == 1
    assert engine.intimacy_xp == 16

    # 3. 模拟剧烈摇晃机身 (合加速度 2.8g)
    engine.update(now=5000, ax=1.8, ay=1.8, az=1.2, roll=30.0, pitch=45.0, mic_rms=0, spk_rms=0)
    assert engine.current_mood == "MOOD_DIZZY"
    assert engine.total_shakes == 1

    # 摇晃晕眩状态持续 3.5 秒
    engine.update(now=7000, ax=0.0, ay=0.0, az=1.0, roll=0.0, pitch=0.0, mic_rms=0, spk_rms=0)
    assert engine.current_mood == "MOOD_DIZZY"

    # 3.5 秒后自然恢复常态
    engine.update(now=9000, ax=0.0, ay=0.0, az=1.0, roll=0.0, pitch=0.0, mic_rms=0, spk_rms=0)
    assert engine.current_mood == "MOOD_IDLE"

    # 4. 模拟平放超过 90 秒无交互 -> 自动入睡
    engine.last_interaction = 10000
    engine.update(now=110000, ax=0.0, ay=0.0, az=1.0, roll=2.0, pitch=-3.0, mic_rms=0, spk_rms=0)
    assert engine.current_mood == "MOOD_SLEEP"


def test_avatar_audio_reactive_pupil_and_mouth():
    engine = MockAvatarPhysics()

    # 1. 聆听态下，麦克风音量越大，瞳孔放大越多
    engine.set_mood("MOOD_LISTEN")
    for _ in range(5):
        engine.update(now=2000, ax=0.0, ay=0.0, az=1.0, roll=0.0, pitch=0.0, mic_rms=80, spk_rms=0)
    assert engine.pupil_r > 10.0, "大音量拾音时瞳孔应明显放大"

    # 2. 说话态下，播音音量驱动嘴型开合
    engine.set_mood("MOOD_SPEAK")
    for _ in range(5):
        engine.update(now=3000, ax=0.0, ay=0.0, az=1.0, roll=0.0, pitch=0.0, mic_rms=0, spk_rms=75)
    assert engine.mouth_h > 8.0, "播音时嘴巴高度应随音频能量显著张开"


def test_intimacy_level_progression():
    engine = MockAvatarPhysics()
    assert engine.intimacy_level == 1
    # 注入经验值
    engine.add_intimacy(85)
    assert engine.intimacy_level == 2
    assert engine.intimacy_xp == 0


def test_firmware_avatar_header_contract():
    assert os.path.exists(AVATAR_H), f"{AVATAR_H} 必须存在"
    with open(AVATAR_H, "r", encoding="utf-8") as f:
        src = f.read()

    assert "enum AvatarMood" in src
    assert "MOOD_IDLE" in src
    assert "MOOD_LISTEN" in src
    assert "MOOD_THINK" in src
    assert "MOOD_SPEAK" in src
    assert "MOOD_HAPPY" in src
    assert "MOOD_DIZZY" in src
    assert "MOOD_SLEEP" in src
    assert "MOOD_EAT" in src
    assert "MOOD_GROOM" in src
    assert "MOOD_WINK" in src
    assert "total_feeds" in src
    assert "total_grooms" in src
    assert "class StickS3Avatar" in src
    assert "void feed" in src
    assert "void groom" in src
    assert "void play" in src
    assert "updatePhysics" in src
    assert "render" in src


def test_firmware_ble_sync_header_contract():
    assert os.path.exists(BLE_SYNC_H), f"{BLE_SYNC_H} 必须存在"
    with open(BLE_SYNC_H, "r", encoding="utf-8") as f:
        src = f.read()

    assert "BLE_BUDDY_SERVICE_UUID" in src
    assert "0000FFB0" in src
    assert "0000FFB1" in src
    assert "0000FFB2" in src
    assert "0000FFB3" in src
    assert "0000FFB4" in src
    assert "feeds" in src
    assert "grooms" in src
    assert "energy" in src
    assert 'action == "feed"' in src
    assert 'action == "groom"' in src
    assert 'action == "play"' in src
    assert "class StickS3BLESync" in src
    assert "registerService" in src
    assert "updateSnapshots" in src


def test_firmware_main_avatar_integration():
    assert os.path.exists(MAIN_CPP), f"{MAIN_CPP} 必须存在"
    with open(MAIN_CPP, "r", encoding="utf-8") as f:
        src = f.read()

    assert 'sticks3_avatar.h' in src
    assert 'sticks3_ble_sync.h' in src
    assert 'g_pet_avatar_mode' in src
    assert 'StickS3Avatar::getInstance().begin' in src
    assert 'StickS3BLESync::getInstance().registerService' in src
    assert 'StickS3Avatar::getInstance().updatePhysics' in src
    assert 'StickS3Avatar::getInstance().render' in src


def test_avatar_emotion_tag_extraction():
    """验证大模型首包 [E:xxx] 情绪标签提取与纯净文本剥离契约"""
    def parse_emotion_tag(raw_text: str):
        if not raw_text.startswith(("[E:", "[e:")):
            return "MOOD_IDLE", raw_text
        close_idx = raw_text.find("]")
        if close_idx < 0:
            return "MOOD_IDLE", raw_text
        tag = raw_text[3:close_idx].lower().strip()
        clean = raw_text[close_idx + 1:].strip()
        tag_map = {
            "happy": "MOOD_HAPPY",
            "curious": "MOOD_CURIOUS",
            "proud": "MOOD_PROUD",
            "sleepy": "MOOD_SLEEP",
            "sleep": "MOOD_SLEEP",
            "dizzy": "MOOD_DIZZY",
            "shock": "MOOD_SHOCK",
            "listen": "MOOD_LISTEN",
            "eat": "MOOD_EAT",
            "groom": "MOOD_GROOM",
            "wink": "MOOD_WINK",
            "play": "MOOD_WINK",
        }
        return tag_map.get(tag, "MOOD_IDLE"), clean

    mood, clean = parse_emotion_tag("[E:happy] 哇！今天天气真棒！")
    assert mood == "MOOD_HAPPY"
    assert clean == "哇！今天天气真棒！"

    mood, clean = parse_emotion_tag("[E:curious] 为什么天是蓝色的呢？")
    assert mood == "MOOD_CURIOUS"
    assert clean == "为什么天是蓝色的呢？"

    mood, clean = parse_emotion_tag("[E:eat] 这块小蛋糕太好吃啦！")
    assert mood == "MOOD_EAT"

    mood, clean = parse_emotion_tag("[E:groom] 梳毛毛好舒服呀~")
    assert mood == "MOOD_GROOM"

    mood, clean = parse_emotion_tag("普通日常回答，无标签")
    assert mood == "MOOD_IDLE"
    assert clean == "普通日常回答，无标签"


def test_avatar_ble_inject_command_processing():
    """验证手机端通过 0xFFB4 注入控制指令的响应契约"""
    from scripts.lingbuddy_companion import LingBuddySimulatorClient
    client = LingBuddySimulatorClient()
    
    res = client.inject_action("pet")
    assert res["status"] == "ok"
    assert client.mood == 4  # HAPPY
    assert client.pets == 1
    assert "摸了摸" in res["diary"]

    res_mem = client.inject_action("inject_memory", "备忘测试")
    assert res_mem["status"] == "ok"
    assert any("备忘测试" in turn["content"] for turn in client.memory_turns)


def test_tamagotchi_virtual_interactions():
    """验证拓麻歌子新增互动 (feed, groom, play) 的状态变更与羁绊成长"""
    from scripts.lingbuddy_companion import LingBuddySimulatorClient
    client = LingBuddySimulatorClient()

    # 1. 投喂测试
    res_feed = client.inject_action("feed", "抹茶大福")
    assert res_feed["status"] == "ok"
    assert client.mood == 10  # MOOD_EAT
    assert client.feeds == 1
    assert "抹茶大福" in res_feed["diary"]

    # 2. 梳毛测试
    res_groom = client.inject_action("groom")
    assert res_groom["status"] == "ok"
    assert client.mood == 11  # MOOD_GROOM
    assert client.grooms == 1
    assert "梳理毛发" in res_groom["diary"]

    # 3. 击掌测试
    res_play = client.inject_action("play")
    assert res_play["status"] == "ok"
    assert client.mood == 12  # MOOD_WINK
    assert "默契击掌" in res_play["diary"]


def test_avatar_chunked_memory_stream():
    """验证 0xFFB1 记忆分块传输与手机端切片重组还原算法"""
    import json
    from scripts.lingbuddy_companion import LingBuddySimulatorClient
    client = LingBuddySimulatorClient()
    
    chunks = client.get_chunked_memory(chunk_size=32)
    assert len(chunks) >= 2, "长文本必须分包切片"
    for c in chunks:
        assert c.startswith("[C:")
        assert "]" in c
    
    assembled = client.reassemble_memory(chunks)
    data = json.loads(assembled)
    assert len(data) >= 2
    assert data[0]["role"] == "user"


def test_firmware_wifi_tamagotchi_portal_contract():
    """验证 sticks3_wifi.h 中拓麻歌子「隔空投喂」与 REST 端点契约完整性"""
    wifi_h = os.path.join(FW_ROOT, "include", "sticks3_wifi.h")
    assert os.path.exists(wifi_h), f"{wifi_h} 必须存在"
    with open(wifi_h, "r", encoding="utf-8") as f:
        src = f.read()

    assert "/pet/status" in src, "必须包含 /pet/status 查询路由"
    assert "/pet/action" in src, "必须包含 /pet/action 控制路由"
    assert "pet-card" in src, "必须包含拓麻歌子专用高保真卡片样式"
    assert "隔空投喂" in src, "必须包含隔空投喂功能入口"
    assert "triggerPetFeed" in src, "前端必须具备投喂触发逻辑"
    assert "triggerPetAction" in src, "前端必须具备动作下发逻辑"
    assert "sticks3_avatar.h" in src, "Wi-Fi 头文件必须引用 Avatar 引擎"


def test_web_companion_disney_rendering_contract():
    """验证 Web 伴侣页面中迪士尼艺术审美微表情与双模连接契约"""
    companion_html = os.path.abspath(os.path.join(FW_ROOT, "..", "..", "web", "lingbuddy_companion.html"))
    assert os.path.exists(companion_html), f"{companion_html} 必须存在"
    with open(companion_html, "r", encoding="utf-8") as f:
        html = f.read()

    assert "drawDisneyEye" in html, "Canvas 必须使用迪士尼双高光水灵大眼解算"
    assert "drawDisneyDMouth" in html, "必须支持迪士尼 D 型皓齿粉舌微表情"
    assert "drawDisneyCheeks" in html, "必须支持弹弹粉嫩腮红"
    assert "drawStar" in html, "必须支持晕眩轨道金星与 Pixie Dust 闪烁"
    assert "toggleConnectWifi" in html, "必须支持 Wi-Fi 局域网即时直连"
    assert "/pet/action" in html, "必须支持向硬件下发 /pet/action"


def test_wechat_miniprogram_suite_contract():
    """验证微信小程序全套架构设计文档、SDK 与前端工程契约完整性"""
    repo_root = os.path.abspath(os.path.join(FW_ROOT, "..", ".."))
    doc_28 = os.path.join(repo_root, "docs", "28_M5StickS3微信小程序对接架构与通信协议工程指南.md")
    assert os.path.exists(doc_28), "必须包含 28 号微信小程序架构与协议指南文档"
    with open(doc_28, "r", encoding="utf-8") as f:
        doc_src = f.read()

    assert "gstack-plan-eng-review" in doc_src, "架构文档必须包含工程总监审查"
    assert "gstack-cso" in doc_src, "架构文档必须包含首席安全官 STRIDE 威胁建模"
    assert "gstack-qa" in doc_src, "架构文档必须包含测试总监极端环境矩阵"
    assert "0000FFB0" in doc_src, "必须详细定义 0xFFB0 BLE 服务"
    assert "20 字节安全 MTU 分包" in doc_src, "必须规定 20 字节分包准则"

    # 微信小程序工程源码完整性
    mp_root = os.path.join(repo_root, "wechat_miniprogram")
    assert os.path.exists(os.path.join(mp_root, "project.config.json")), "必须存在 project.config.json"
    assert os.path.exists(os.path.join(mp_root, "app.json")), "必须存在 app.json"
    assert os.path.exists(os.path.join(mp_root, "utils", "sticks3_ble.js")), "必须存在 sticks3_ble.js"
    assert os.path.exists(os.path.join(mp_root, "utils", "sticks3_wifi.js")), "必须存在 sticks3_wifi.js"
    assert os.path.exists(os.path.join(mp_root, "utils", "avatar_renderer.js")), "必须存在 avatar_renderer.js"
    assert os.path.exists(os.path.join(mp_root, "utils", "crypto_guard.js")), "必须存在 crypto_guard.js"
    assert os.path.exists(os.path.join(mp_root, "pages", "index", "index.wxml")), "必须存在 index.wxml"
    assert os.path.exists(os.path.join(mp_root, "pages", "index", "index.js")), "必须存在 index.js"

    # 驱动关键逻辑断言
    with open(os.path.join(mp_root, "utils", "sticks3_ble.js"), "r", encoding="utf-8") as f:
        ble_src = f.read()
    assert "0000FFB0" in ble_src
    assert "writeInChunks" in ble_src, "BLE 驱动必须包含 20 字节切片写入器"
    assert "handleMemoryChunk" in ble_src, "BLE 驱动必须包含长程记忆还原器"

    # 移动端研发交接指南与续写提示词契约
    doc_29 = os.path.join(repo_root, "docs", "29_微信小程序与移动端研发交接指南_HANDOVER_MOBILE.md")
    assert os.path.exists(doc_29), "必须包含 29 号移动端研发交接指南"
    with open(doc_29, "r", encoding="utf-8") as f:
        doc_29_src = f.read()
    assert "HANDOVER_MOBILE" in doc_29_src
    assert "0xFFB0" in doc_29_src

    agent_prompts = os.path.join(repo_root, "docs", "AGENT_CONTINUATION_PROMPTS.md")
    with open(agent_prompts, "r", encoding="utf-8") as f:
        prompts_src = f.read()
    assert "方向 13" in prompts_src, "提示词标准库必须收录移动端续写方向 13"


def test_wechat_miniprogram_product_architecture_contract():
    """验证微信小程序四大 TabBar 交互、<avatar-canvas> 自定义组件、触觉与离线存储契约"""
    import json
    repo_root = os.path.abspath(os.path.join(FW_ROOT, "..", ".."))
    mp_root = os.path.join(repo_root, "wechat_miniprogram")

    # 1. <avatar-canvas> 自定义组件契约
    comp_dir = os.path.join(mp_root, "components", "avatar-canvas")
    assert os.path.exists(os.path.join(comp_dir, "avatar-canvas.json")), "avatar-canvas.json 必须存在"
    assert os.path.exists(os.path.join(comp_dir, "avatar-canvas.wxml")), "avatar-canvas.wxml 必须存在"
    assert os.path.exists(os.path.join(comp_dir, "avatar-canvas.wxss")), "avatar-canvas.wxss 必须存在"
    assert os.path.exists(os.path.join(comp_dir, "avatar-canvas.js")), "avatar-canvas.js 必须存在"

    with open(os.path.join(comp_dir, "avatar-canvas.js"), "r", encoding="utf-8") as f:
        comp_js = f.read()
    assert "pixelRatio" in comp_js, "自定义组件必须适配多端 DPR 屏幕像素比"
    assert "AvatarRenderer" in comp_js, "自定义组件必须集成迪士尼微表情引擎"
    assert "onCanvasTap" in comp_js, "自定义组件必须支持轻触解算"
    assert "onCanvasLongPress" in comp_js, "自定义组件必须支持长按击掌"

    # 2. 四大 Tab 页面与资源完整性
    pages = ["index", "feed", "diary", "settings"]
    for p in pages:
        p_dir = os.path.join(mp_root, "pages", p)
        assert os.path.exists(os.path.join(p_dir, f"{p}.json")), f"{p}.json 必须存在"
        assert os.path.exists(os.path.join(p_dir, f"{p}.wxml")), f"{p}.wxml 必须存在"
        assert os.path.exists(os.path.join(p_dir, f"{p}.wxss")), f"{p}.wxss 必须存在"
        assert os.path.exists(os.path.join(p_dir, f"{p}.js")), f"{p}.js 必须存在"

    # 3. app.json TabBar 配置契约
    with open(os.path.join(mp_root, "app.json"), "r", encoding="utf-8") as f:
        app_json = json.load(f)
    assert len(app_json.get("pages", [])) == 4, "必须注册全部 4 个主页面"
    assert "tabBar" in app_json, "必须配置全局 TabBar"
    assert len(app_json["tabBar"]["list"]) == 4, "TabBar 必须包含 4 个 Tab"

    tab_icons = [
        "home.png", "home_active.png",
        "feed.png", "feed_active.png",
        "diary.png", "diary_active.png",
        "settings.png", "settings_active.png"
    ]
    for icon in tab_icons:
        icon_path = os.path.join(mp_root, "assets", "tabbar", icon)
        assert os.path.exists(icon_path), f"TabBar 图标 {icon} 必须存在"

    # 4. 触觉微震动与离线持久化 SDK 契约
    haptics_js = os.path.join(mp_root, "utils", "haptics.js")
    assert os.path.exists(haptics_js), "haptics.js 必须存在"
    with open(haptics_js, "r", encoding="utf-8") as f:
        haptics_src = f.read()
    assert "vibrateShort" in haptics_src
    assert "feed" in haptics_src and "pet" in haptics_src and "play" in haptics_src

    storage_js = os.path.join(mp_root, "utils", "storage_manager.js")
    assert os.path.exists(storage_js), "storage_manager.js 必须存在"
    with open(storage_js, "r", encoding="utf-8") as f:
        storage_src = f.read()
    assert "setStorageSync" in storage_src
    assert "getStorageSync" in storage_src
    assert "saveDiaryEntry" in storage_src
    assert "lingbuddy_diaries" in storage_src

    buddy_js = os.path.join(mp_root, "utils", "buddy_service.js")
    assert os.path.exists(buddy_js), "buddy_service.js 必须存在"
    with open(buddy_js, "r", encoding="utf-8") as f:
        buddy_src = f.read()
    assert "provisionWifi" in buddy_src, "必须支持 BLE 一键智能配网"
    assert "dispatchAction" in buddy_src, "必须具备跨页面动作下发调度器"





