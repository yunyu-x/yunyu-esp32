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
    assert "class StickS3Avatar" in src
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
        }
        return tag_map.get(tag, "MOOD_IDLE"), clean

    mood, clean = parse_emotion_tag("[E:happy] 哇！今天天气真棒！")
    assert mood == "MOOD_HAPPY"
    assert clean == "哇！今天天气真棒！"

    mood, clean = parse_emotion_tag("[E:curious] 为什么天是蓝色的呢？")
    assert mood == "MOOD_CURIOUS"
    assert clean == "为什么天是蓝色的呢？"

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

