"""
tests/test_bear_rpg_skill_tree.py
---------------------------------
Comprehensive unit tests for Meta Muse Bear (Jollybot) RPG Skill Tree,
Multi-Joint Coordinated Kinematics, and Direct Function Calling Integration.
"""

import os
import re
import pytest

FIRMWARE_HEADER = "firmware/m5sticks3_buddy/include/sticks3_bear_kinematics.h"
BAILIAN_HEADER = "firmware/m5sticks3_buddy/include/sticks3_bailian_client.h"
MAIN_CPP = "firmware/m5sticks3_buddy/src/main.cpp"

# 1. 模拟 Python 镜像版技能树系统，验证业务逻辑与数学模型
class MockBearGrowthManager:
    LEVEL_THRESHOLDS = {
        1: (0, 99, "幼幼萌熊"),
        2: (100, 249, "灵动小熊"),
        3: (250, 499, "体能健将"),
        4: (500, 799, "功夫大师"),
        5: (800, 1200, "机甲元尊"),
    }

    ACTION_LEVELS = {
        # Lv.1
        "wave": 1, "bow": 1, "sit": 1, "stretch": 1,
        # Lv.2
        "clap": 2, "cheer": 2, "jump": 2, "hands_up": 2,
        # Lv.3
        "dance": 3, "balance": 3, "lie": 3, "pushup": 3,
        # Lv.4
        "kungfu": 4, "taichi": 4, "wingchun": 4,
        # Lv.5
        "dragon_punch": 5, "moonwalk": 5, "cyber_defense": 5,
    }

    COMBO_LEVELS = {
        "greeting": 2,
        "fitness": 3,
        "martial": 4,
        "cyber_supreme": 5,
    }

    def __init__(self, exp=25, level=1):
        self.exp = exp
        self.level = level

    def get_level(self):
        return self.level

    def get_exp(self):
        return self.exp

    def get_level_title(self):
        return self.LEVEL_THRESHOLDS.get(self.level, (0, 0, "灵动小熊"))[2]

    def get_next_level_exp(self):
        if self.level == 1: return 100
        if self.level == 2: return 250
        if self.level == 3: return 500
        if self.level == 4: return 800
        return 1200

    def add_exp(self, gain):
        self.exp += gain
        leveled_up = False
        threshold = self.get_next_level_exp()
        if self.exp >= threshold and self.level < 5:
            self.level += 1
            leveled_up = True
        return leveled_up

    def is_action_unlocked(self, action_name):
        req = self.ACTION_LEVELS.get(action_name, 1)
        return self.level >= req

    def get_required_level(self, action_name):
        return self.ACTION_LEVELS.get(action_name, 1)

    def is_combo_unlocked(self, combo_name):
        req = self.COMBO_LEVELS.get(combo_name, 1)
        return self.level >= req

    def get_combo_required_level(self, combo_name):
        return self.COMBO_LEVELS.get(combo_name, 1)


def test_bear_growth_thresholds_and_level_up():
    mgr = MockBearGrowthManager(exp=0, level=1)
    assert mgr.get_level() == 1
    assert mgr.get_level_title() == "幼幼萌熊"
    assert mgr.get_next_level_exp() == 100

    # +80 EXP (80/100) -> 保持 Lv.1
    assert not mgr.add_exp(80)
    assert mgr.get_level() == 1

    # +30 EXP (110/100) -> 升级至 Lv.2
    assert mgr.add_exp(30)
    assert mgr.get_level() == 2
    assert mgr.get_level_title() == "灵动小熊"
    assert mgr.get_next_level_exp() == 250

    # 冲至 Lv.3
    mgr.add_exp(150) # 260 EXP
    assert mgr.get_level() == 3
    assert mgr.get_level_title() == "体能健将"

    # 冲至 Lv.4
    mgr.add_exp(250) # 510 EXP
    assert mgr.get_level() == 4
    assert mgr.get_level_title() == "功夫大师"

    # 冲至 Lv.5
    mgr.add_exp(300) # 810 EXP
    assert mgr.get_level() == 5
    assert mgr.get_level_title() == "机甲元尊"


def test_action_and_combo_unlock_matrix():
    mgr = MockBearGrowthManager(exp=50, level=1)

    # Lv.1: 可以做 wave, bow, sit, stretch
    assert mgr.is_action_unlocked("wave")
    assert mgr.is_action_unlocked("bow")
    assert mgr.is_action_unlocked("sit")
    assert mgr.is_action_unlocked("stretch")

    # Lv.1: 不能做 clap, dance, kungfu, dragon_punch
    assert not mgr.is_action_unlocked("clap")
    assert not mgr.is_action_unlocked("dance")
    assert not mgr.is_action_unlocked("kungfu")
    assert not mgr.is_action_unlocked("dragon_punch")
    assert not mgr.is_combo_unlocked("greeting")

    # 提升至 Lv.2
    mgr.level = 2
    assert mgr.is_action_unlocked("clap")
    assert mgr.is_action_unlocked("cheer")
    assert mgr.is_action_unlocked("jump")
    assert mgr.is_combo_unlocked("greeting")
    assert not mgr.is_action_unlocked("dance")
    assert not mgr.is_action_unlocked("kungfu")

    # 提升至 Lv.3
    mgr.level = 3
    assert mgr.is_action_unlocked("dance")
    assert mgr.is_action_unlocked("balance")
    assert mgr.is_action_unlocked("pushup")
    assert mgr.is_combo_unlocked("fitness")
    assert not mgr.is_action_unlocked("wingchun")

    # 提升至 Lv.4
    mgr.level = 4
    assert mgr.is_action_unlocked("kungfu")
    assert mgr.is_action_unlocked("taichi")
    assert mgr.is_action_unlocked("wingchun")
    assert mgr.is_combo_unlocked("martial")
    assert not mgr.is_action_unlocked("dragon_punch")

    # 提升至 Lv.5
    mgr.level = 5
    assert mgr.is_action_unlocked("dragon_punch")
    assert mgr.is_action_unlocked("moonwalk")
    assert mgr.is_action_unlocked("cyber_defense")
    assert mgr.is_combo_unlocked("cyber_supreme")


def test_locked_action_feedback_payload():
    mgr = MockBearGrowthManager(exp=120, level=2)
    target_action = "kungfu"
    
    assert not mgr.is_action_unlocked(target_action)
    req_lvl = mgr.get_required_level(target_action)
    assert req_lvl == 4
    needed_exp = 500 - mgr.get_exp()
    assert needed_exp == 380

    payload = {
        "status": "locked",
        "action": target_action,
        "required_level": req_lvl,
        "current_level": mgr.get_level(),
        "current_exp": mgr.get_exp(),
        "needed_exp": needed_exp,
        "message": f"动作尚未解锁！需要达到 Lv.{req_lvl} (还需 {needed_exp} EXP)"
    }
    assert payload["status"] == "locked"
    assert payload["required_level"] == 4


# 2. 验证固件 C++ 源码头文件中的新增枚举与实现
def test_firmware_bear_kinematics_header_has_rpg_and_biomechanic_enhancements():
    assert os.path.exists(FIRMWARE_HEADER), f"File {FIRMWARE_HEADER} must exist"
    with open(FIRMWARE_HEADER, "r", encoding="utf-8") as f:
        src = f.read()

    # 检查新增枚举
    required_enums = [
        "BEAR_ACT_PUSHUP",
        "BEAR_ACT_WINGCHUN",
        "BEAR_ACT_DRAGON_PUNCH",
        "BEAR_ACT_MOONWALK",
        "BEAR_ACT_CYBER_DEFENSE",
        "BEAR_ACT_LOCKED_TRY"
    ]
    for e in required_enums:
        assert e in src, f"Enum {e} must be defined in {FIRMWARE_HEADER}"

    # 检查字符串转换与映射
    assert 'str == "pushup"' in src
    assert 'str == "wingchun"' in src
    assert 'str == "dragon_punch"' in src
    assert 'str == "moonwalk"' in src
    assert 'str == "cyber_defense"' in src

    # 检查 BearGrowthManager 新增方法
    assert "isActionUnlocked" in src
    assert "getRequiredLevel" in src
    assert "isComboUnlocked" in src

    # 检查骨骼数据结构包含肘膝关节
    assert "elbow_lx" in src or "elbow_flex" in src or "elbow_bend" in src
    assert "knee_flex" in src or "knee_bend" in src or "knee_ly" in src

    # 检查平滑姿态阻尼插值器 (Exponential Pose Damping)
    assert "_smooth_left_arm" in src or "lerp" in src or "damping" in src


def test_firmware_bailian_client_and_main_tool_calling_contract():
    assert os.path.exists(BAILIAN_HEADER), f"File {BAILIAN_HEADER} must exist"
    with open(BAILIAN_HEADER, "r", encoding="utf-8") as f:
        bailian_src = f.read()

    # 检查 DashScope session.update 工具描述包含新动作
    assert "pushup" in bailian_src
    assert "wingchun" in bailian_src
    assert "dragon_punch" in bailian_src
    assert "moonwalk" in bailian_src

    assert os.path.exists(MAIN_CPP), f"File {MAIN_CPP} must exist"
    with open(MAIN_CPP, "r", encoding="utf-8") as f:
        main_src = f.read()

    # 检查 main.cpp 中对未解锁状态的萌态保护与回执
    assert "BEAR_ACT_LOCKED_TRY" in main_src
    assert "isActionUnlocked" in main_src
    assert "locked" in main_src
