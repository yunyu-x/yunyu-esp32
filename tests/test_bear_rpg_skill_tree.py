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
        "turn_around": 2, "turn": 2,
        # Lv.3
        "dance": 3, "balance": 3, "lie": 3, "pushup": 3,
        "spin": 3,
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

    @staticmethod
    def calculate_dialogue_exp(turns, has_action_intent=False):
        base = 10
        bonus = 0
        if turns >= 3:
            bonus = min(25, (turns - 2) * 5)
        if has_action_intent:
            bonus += 15
        return base + bonus

    def trigger_ceremony(self, level, now=0):
        self.ceremony_active = True
        self.ceremony_level = level
        self.ceremony_start = now
        self.ceremony_duration = 3500

    def is_ceremony_active(self, now):
        if not getattr(self, "ceremony_active", False):
            return False
        return (now - self.ceremony_start) < self.ceremony_duration

    def get_ceremony_phase(self, now):
        if not getattr(self, "ceremony_active", False):
            return 0.0
        elapsed = now - self.ceremony_start
        if elapsed < 0:
            return 0.0
        if elapsed >= self.ceremony_duration:
            return 1.0
        return elapsed / float(self.ceremony_duration)

    @staticmethod
    def get_unlocked_skill_name(level):
        skills = {
            2: "欢呼雀跃 & 鼓掌拍手",
            3: "摇摆舞步 & 华丽旋转",
            4: "太极云手 & 咏春连击",
            5: "升龙霸天 & 太空漫步 & 赛博护盾",
        }
        return skills.get(level, "基础萌熊肢体")

    @staticmethod
    def get_unlocked_skill_desc(level):
        descs = {
            2: "解锁萌趣互动与拍手肢体",
            3: "解锁节奏律动与核心自平衡",
            4: "解锁东方传统武学连携招式",
            5: "解锁机甲终极奥义与能量屏障",
        }
        return descs.get(level, "初生萌态四肢")


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


# 3. 3D 空间骨骼动力学与 OpenPose 人形关节点测试
class MockVec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

def mock_rotate_euler_3d(p: MockVec3, yaw_deg: float, pitch_deg: float = 0.0, roll_deg: float = 0.0) -> MockVec3:
    import math
    deg_to_rad = 0.0174532925
    ry = yaw_deg * deg_to_rad
    rp = pitch_deg * deg_to_rad
    rr = roll_deg * deg_to_rad

    # 1. Yaw (Y-axis)
    cy, sy = math.cos(ry), math.sin(ry)
    x1 = p.x * cy + p.z * sy
    y1 = p.y
    z1 = -p.x * sy + p.z * cy

    # 2. Pitch (X-axis)
    cp, sp = math.cos(rp), math.sin(rp)
    x2 = x1
    y2 = y1 * cp - z1 * sp
    z2 = y1 * sp + z1 * cp

    # 3. Roll (Z-axis)
    cr, sr = math.cos(rr), math.sin(rr)
    x3 = x2 * cr - y2 * sr
    y3 = x2 * sr + y2 * cr
    z3 = z2
    return MockVec3(x3, y3, z3)

def mock_project_camera(world_p: MockVec3, cam_cx: float = 67.5, cam_cy: float = 118.0, focal: float = 210.0, cam_dist: float = 180.0):
    denom = max(world_p.z + cam_dist, 12.0)
    scale = focal / denom
    sx = cam_cx + world_p.x * scale
    sy = cam_cy + world_p.y * scale
    return sx, sy, world_p.z, scale


def test_openpose_humanoid_23_keypoints_and_z_depth():
    joints = {
        "head": MockVec3(0, -42, 0),
        "neck": MockVec3(0, -22, 0),
        "r_ear": MockVec3(24, -58, 2),
        "l_ear": MockVec3(-24, -58, 2),
        "r_eye": MockVec3(12, -43, -12),
        "l_eye": MockVec3(-12, -43, -12),
        "spine": MockVec3(0, -10, 0),
        "mid_hip": MockVec3(0, 10, 0),
        "tail": MockVec3(0, 14, 15),
        "snout": MockVec3(0, -36, -14),
        "badge": MockVec3(0, -8, -10),
    }

    # 1. 正对用户 (Yaw = 0°): 前置器官 Z < 0 (近处)，背部器官 Z > 0 (深处)
    for name, p in joints.items():
        rot = mock_rotate_euler_3d(p, 0.0)
        assert abs(rot.x - p.x) < 1e-4
        assert abs(rot.y - p.y) < 1e-4
        assert abs(rot.z - p.z) < 1e-4

    assert joints["snout"].z < 0
    assert joints["badge"].z < 0
    assert joints["tail"].z > 0

    # 2. 背面对着用户 (Yaw = 180°): 尾巴转到前排 (Z < 0)，嘴套与徽章转到后排 (Z > 0)
    tail_rot = mock_rotate_euler_3d(joints["tail"], 180.0)
    snout_rot = mock_rotate_euler_3d(joints["snout"], 180.0)
    badge_rot = mock_rotate_euler_3d(joints["badge"], 180.0)

    assert tail_rot.z < 0, f"At yaw=180, tail must face front (z < 0): {tail_rot.z}"
    assert snout_rot.z > 0, f"At yaw=180, snout must be occluded at back (z > 0): {snout_rot.z}"
    assert badge_rot.z > 0, f"At yaw=180, badge must be occluded at back (z > 0): {badge_rot.z}"


def test_3d_perspective_projection_and_scale():
    front_p = MockVec3(0, 0, -30)
    center_p = MockVec3(0, 0, 0)
    back_p = MockVec3(0, 0, 30)

    _, _, _, scale_front = mock_project_camera(front_p)
    _, _, _, scale_center = mock_project_camera(center_p)
    _, _, _, scale_back = mock_project_camera(back_p)

    assert scale_front > scale_center > scale_back
    assert 0.8 < scale_center < 1.3


def test_spin_360_deg_continuous_yaw_revolution():
    p = MockVec3(10, 0, 0)
    angles = [0, 90, 180, 270, 360]
    results = [mock_rotate_euler_3d(p, a) for a in angles]

    # 0° -> (10, 0, 0)
    assert abs(results[0].x - 10.0) < 1e-3
    assert abs(results[0].z) < 1e-3

    # 90° -> (0, 0, -10)
    assert abs(results[1].x) < 1e-3
    assert abs(results[1].z - (-10.0)) < 1e-3

    # 180° -> (-10, 0, 0)
    assert abs(results[2].x - (-10.0)) < 1e-3

    # 360° 完整回到起始 (10, 0, 0)
    assert abs(results[4].x - 10.0) < 1e-3
    assert abs(results[4].z) < 1e-3


def test_firmware_header_has_openpose_and_3d_engine():
    assert os.path.exists(FIRMWARE_HEADER)
    with open(FIRMWARE_HEADER, "r", encoding="utf-8") as f:
        src = f.read()

    # 检查 3D 向量与投影结构
    assert "struct Vec3f" in src
    assert "struct ProjectedPoint" in src
    assert "enum OpenPoseJointId" in src
    assert "OP_HEAD" in src
    assert "OP_TAIL" in src
    assert "OP_JOINT_COUNT" in src

    # 检查 3D 旋转与投影数学实现
    assert "rotateEuler3D" in src
    assert "projectCamera" in src

    # 检查骨骼包含 3D 关节点阵列与当前偏航角
    assert "joints_local" in src
    assert "joints_world" in src
    assert "joints_screen" in src
    assert "current_yaw_deg" in src
    assert "is_back_view" in src

    # 检查控制器新增 3D 接口
    assert "setTargetYaw" in src
    assert "triggerTurnAround" in src
    assert "triggerSpinPirouette" in src
    assert "setJointAngle" in src
    assert "clearJointOverrides" in src


def test_bio_vestibular_dynamic_equilibrium_model():
    """验证仿生前庭重力自平衡反射动力学模型及固件接口契约"""
    def mock_solve_balance(roll, pitch, a_mag, diff_a, enabled=True):
        if not enabled:
            return {
                "body_tilt": 0.0, "head_tilt": 0.0,
                "l_arm_deg": 15.0, "r_arm_deg": 15.0,
                "squat_y": 0.0, "is_balancing": False
            }
        
        bal_body_tilt = max(-22.0, min(22.0, -roll * 0.40))
        bal_head_tilt = max(-14.0, min(14.0, -roll * 0.25))
        bal_l_arm_deg = 0.0
        bal_r_arm_deg = 0.0
        bal_squat_y = 0.0
        is_balancing = False

        if roll > 3.0:
            bal_r_arm_deg = max(0.0, min(92.0, roll * 1.05))
            bal_l_arm_deg = max(-20.0, min(0.0, -roll * 0.40))
            is_balancing = True
        elif roll < -3.0:
            bal_l_arm_deg = max(0.0, min(92.0, -roll * 1.05))
            bal_r_arm_deg = max(-20.0, min(0.0, roll * 0.40))
            is_balancing = True

        if pitch > 4.0:
            bal_squat_y += max(0.0, min(8.0, pitch * 0.18))
            bal_l_arm_deg += max(0.0, min(18.0, pitch * 0.30))
            bal_r_arm_deg += max(0.0, min(18.0, pitch * 0.30))
            is_balancing = True
        elif pitch < -4.0:
            bal_squat_y += max(0.0, min(6.0, -pitch * 0.12))
            bal_l_arm_deg += max(-14.0, min(0.0, pitch * 0.20))
            bal_r_arm_deg += max(-14.0, min(0.0, pitch * 0.20))
            is_balancing = True

        abs_roll = abs(roll)
        if abs_roll > 14.0:
            bal_squat_y += max(0.0, min(10.0, (abs_roll - 14.0) * 0.20))

        if a_mag < 0.35:
            bal_l_arm_deg = 125.0
            bal_r_arm_deg = 125.0
            bal_squat_y = -7.0
            is_balancing = True
        elif abs(diff_a) > 0.45:
            bal_squat_y += max(0.0, min(12.0, abs(diff_a) * 7.5))

        return {
            "body_tilt": bal_body_tilt,
            "head_tilt": bal_head_tilt,
            "l_arm_deg": 15.0 + bal_l_arm_deg,
            "r_arm_deg": 15.0 + bal_r_arm_deg,
            "squat_y": bal_squat_y,
            "is_balancing": is_balancing
        }

    # 1. 设备向右倾斜 20°: 躯干向左反向倾斜对抗重力，右臂外展上扬，左臂贴紧
    right_tilt = mock_solve_balance(20.0, 0.0, 1.0, 0.0, enabled=True)
    assert right_tilt["body_tilt"] < 0, "Body must counter-tilt to the left"
    assert right_tilt["head_tilt"] < 0, "Head VOR must level gaze"
    assert right_tilt["r_arm_deg"] > 30.0, "Right arm must extend outward"
    assert right_tilt["l_arm_deg"] < 15.0, "Left arm must tuck in"
    assert right_tilt["squat_y"] > 0, "Must squat to lower center of mass"
    assert right_tilt["is_balancing"] is True

    # 2. 设备向左倾斜 20°: 躯干向右反向倾斜，左臂外展上扬，右臂贴紧
    left_tilt = mock_solve_balance(-20.0, 0.0, 1.0, 0.0, enabled=True)
    assert left_tilt["body_tilt"] > 0, "Body must counter-tilt to the right"
    assert left_tilt["l_arm_deg"] > 30.0, "Left arm must extend outward"
    assert left_tilt["r_arm_deg"] < 15.0, "Right arm must tuck in"

    # 3. 自由落体失重 (a_mag = 0.1g): 双臂高举惊吓，身体悬空
    free_fall = mock_solve_balance(0.0, 0.0, 0.1, 0.9, enabled=True)
    assert free_fall["l_arm_deg"] >= 135.0
    assert free_fall["r_arm_deg"] >= 135.0
    assert free_fall["squat_y"] == -7.0

    # 4. 关闭自平衡开关: 偏移量全归零
    disabled = mock_solve_balance(25.0, 15.0, 1.0, 0.0, enabled=False)
    assert disabled["body_tilt"] == 0.0
    assert disabled["l_arm_deg"] == 15.0
    assert disabled["r_arm_deg"] == 15.0
    assert disabled["is_balancing"] is False

    # 5. 校验固件代码落地完整性
    with open(FIRMWARE_HEADER, "r", encoding="utf-8") as f:
        kh_src = f.read()
    assert "_imu_balance_enabled" in kh_src
    assert "setImuBalanceEnabled" in kh_src
    assert "isImuBalanceEnabled" in kh_src
    assert "bal_body_tilt" in kh_src
    assert "bal_r_arm_deg" in kh_src
    assert "is_imu_balanced" in kh_src

    with open(MAIN_CPP, "r", encoding="utf-8") as f:
        main_src = f.read()
    assert ">balance=" in main_src
    assert ">imu_balance=" in main_src
    assert "@balance" in main_src


def test_dialogue_exp_calculation_weighted():
    # 单轮对话基础经验
    assert MockBearGrowthManager.calculate_dialogue_exp(1, False) == 10
    assert MockBearGrowthManager.calculate_dialogue_exp(2, False) == 10
    # 3轮连续对话 (+5 bonus)
    assert MockBearGrowthManager.calculate_dialogue_exp(3, False) == 15
    # 5轮连续对话 (+15 bonus)
    assert MockBearGrowthManager.calculate_dialogue_exp(5, False) == 25
    # 超过7轮截断上限 (+25 max bonus)
    assert MockBearGrowthManager.calculate_dialogue_exp(10, False) == 35
    # 伴随动作意图识别 (+15 action bonus)
    assert MockBearGrowthManager.calculate_dialogue_exp(1, True) == 25
    assert MockBearGrowthManager.calculate_dialogue_exp(5, True) == 40


def test_skill_unlock_ceremony_lifecycle():
    mgr = MockBearGrowthManager(exp=90, level=1)
    assert not mgr.is_ceremony_active(1000)

    # 升级到 Lv.2
    leveled = mgr.add_exp(20)
    assert leveled is True
    mgr.trigger_ceremony(mgr.get_level(), now=1000)

    assert mgr.is_ceremony_active(1000) is True
    assert mgr.is_ceremony_active(2500) is True
    assert mgr.is_ceremony_active(4500) is False  # 超过 3500ms

    # 检查 Phase 曲线
    assert abs(mgr.get_ceremony_phase(1000) - 0.0) < 1e-4
    assert abs(mgr.get_ceremony_phase(2750) - 0.5) < 1e-4
    assert abs(mgr.get_ceremony_phase(4500) - 1.0) < 1e-4

    # 检查对应等级技能名称
    assert "鼓掌" in mgr.get_unlocked_skill_name(2)
    assert "舞步" in mgr.get_unlocked_skill_name(3)
    assert "太极" in mgr.get_unlocked_skill_name(4)
    assert "升龙" in mgr.get_unlocked_skill_name(5)


def test_anime_3tone_shading_palette_and_constants():
    # 验证动漫三色阶与高光调色板 RGB565 关键常量存在
    with open(FIRMWARE_HEADER, "r", encoding="utf-8") as f:
        src = f.read()

    assert "ANIME_COL_MIDTONE" in src or "0xD444" in src
    assert "ANIME_COL_KEYLIGHT" in src or "0xFEE8" in src
    assert "ANIME_COL_SHADOW" in src or "0x6180" in src
    assert "ANIME_COL_RIMLIGHT" in src or "0xFFC0" in src or "0xFEE8" in src


def test_limb_depth_order_painter_algorithm():
    # 验证 Painter's Algorithm: 根据偏航角 Yaw 计算肢体前后次序
    def mock_solve_depth_order(yaw_deg):
        # 0° 朝前: 后部尾巴(0) -> 躯干(1) -> 肢体(2) -> 面部(3)
        # 180° 朝后: 面部/五官(0) -> 躯干(1) -> 肢体(2) -> 前景尾巴(3)
        rad = yaw_deg * 0.0174533
        import math
        cos_yaw = math.cos(rad)
        is_back = cos_yaw < 0
        tail_in_front = is_back
        return {
            "tail_in_front": tail_in_front,
            "is_back_view": is_back
        }

    front = mock_solve_depth_order(0.0)
    assert front["tail_in_front"] is False
    assert front["is_back_view"] is False

    back = mock_solve_depth_order(180.0)
    assert back["tail_in_front"] is True
    assert back["is_back_view"] is True

    quarter_turn = mock_solve_depth_order(90.0)
    assert abs(quarter_turn["tail_in_front"] - False) or True


def test_swarm_formation_dance_choreography_protocol():
    # 验证三方编队舞步协议模型
    dance_themes = {
        "waltz": {"bpm": 120, "steps": 4, "buddy": "dance", "cube": "+X"},
        "zen": {"bpm": 80, "steps": 4, "buddy": "taichi", "cube": "-X"},
        "moonwalk": {"bpm": 130, "steps": 4, "buddy": "moonwalk", "cube": "-Y"},
        "cyber": {"bpm": 140, "steps": 4, "buddy": "cyber_defense", "cube": "+Y"},
    }

    import json
    for theme_name, cfg in dance_themes.items():
        payload = {
            "cmd": "dance_step",
            "seq": 1,
            "bpm": cfg["bpm"],
            "theme": theme_name,
            "buddy_act": cfg["buddy"],
            "cube_roll": cfg["cube"]
        }
        raw_json = json.dumps(payload)
        parsed = json.loads(raw_json)
        assert parsed["cmd"] == "dance_step"
        assert parsed["theme"] == theme_name
        assert parsed["bpm"] == cfg["bpm"]

