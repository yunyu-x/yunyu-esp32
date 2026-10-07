/**
 * @file sticks3_bear_kinematics.h
 * @brief Meta Muse Jollybot Full-Body Skeletal Kinematics, IMU Posture Fusion & RPG Growth System
 * 
 * 1. 全身四肢骨骼学 (Full-Body & Limbs Kinematics): 头部、双耳、躯干胸腹、肘膝双段关节弯曲、左右手爪、左右脚掌
 * 2. 生物力学校同身法动力学 (Biomechanical Coordinated Motion): 脊椎对消、腰胯回旋、预备蓄力(Anticipation)、缓入缓出平滑过渡
 * 3. 连续姿态阻尼插值器 (Continuous Pose Damping): 消除动作切换生硬顿挫与撕裂，带来丝滑迪士尼物理质感
 * 4. 6 轴 IMU 动态姿态解算 (BMI270 Posture Fusion): 倾斜重心平衡、滑步踉跄、失重惊吓、跳跃与碰撞弹性缓冲
 * 5. 灵宠养成系统 (Tamagotchi / RPG Growth System): 5级成长 (Lv.1 萌新 ~ Lv.5 机甲元尊)、技能树解锁矩阵、未解锁萌态反馈
 * 6. 自然语言动作与组合控制 (Macro Combo & Limb Control): 挥手、鼓掌、跳舞、功夫、太极、咏春、俯卧撑、升龙拳、太空漫步等宏序列
 */

#pragma once

#include <Arduino.h>
#include <Preferences.h>
#include <cmath>
#include <vector>
#include <string>
#include <M5GFX.h>
#include "sticks3_avatar.h"
#include "sticks3_system_metrics.h"

namespace sticks3 {

// 肢体宏动作枚举 (按 5 级技能树递进组织)
enum BearAction {
    BEAR_ACT_IDLE = 0,
    // Lv.1 幼幼萌熊 基础初生动作
    BEAR_ACT_WAVE,        // 挥手打招呼
    BEAR_ACT_BOW,         // 礼貌微鞠躬
    BEAR_ACT_SIT,         // 乖巧坐下
    BEAR_ACT_STRETCH,     // 伸懒腰打哈欠
    // Lv.2 灵动小熊 情感互动与弹跳动作
    BEAR_ACT_CLAP,        // 鼓掌拍手
    BEAR_ACT_CHEER,       // 举手欢呼
    BEAR_ACT_JUMP,        // 雀跃跳起
    BEAR_ACT_HANDS_UP,    // 举双手投降
    // Lv.3 体能健将 律动与核心平衡动作
    BEAR_ACT_DANCE,       // 摇摆跳舞
    BEAR_ACT_BALANCE,     // 金鸡独立单脚平衡
    BEAR_ACT_LIE,         // 趴下休息
    BEAR_ACT_PUSHUP,      // 俯卧撑锻炼
    // Lv.4 功夫大师 东方传统武学
    BEAR_ACT_KUNGFU,      // 中国功夫推掌站架
    BEAR_ACT_TAICHI,      // 太极行云流水云手
    BEAR_ACT_WINGCHUN,    // 咏春日字冲拳连击
    // Lv.5 机甲元尊 终极多关节身法与科幻微动作
    BEAR_ACT_DRAGON_PUNCH,// 升龙拳飞天暴扣
    BEAR_ACT_MOONWALK,    // 太空漫步滑步后撤
    BEAR_ACT_CYBER_DEFENSE,// 机甲能量盾张开防守
    // 3D 偏航与空间旋转动作 (3D Yaw Turning & Rotation)
    BEAR_ACT_TURN_AROUND, // 180° 萌态转身露尾巴再转回
    BEAR_ACT_SPIN,        // 360° 华丽芭蕾自旋旋转
    // 特殊交互动作：未解锁技能时的萌态抓头困惑反馈
    BEAR_ACT_LOCKED_TRY   // 挠头抓耳困惑歪头
};

inline BearAction stringToBearAction(const std::string& str) {
    if (str == "wave" || str == "wave_right" || str == "wave_left" || str == "hi") return BEAR_ACT_WAVE;
    if (str == "bow" || str == "polite" || str == "salute") return BEAR_ACT_BOW;
    if (str == "sit" || str == "sit_down") return BEAR_ACT_SIT;
    if (str == "stretch" || str == "yawn" || str == "relax") return BEAR_ACT_STRETCH;
    if (str == "clap" || str == "applause") return BEAR_ACT_CLAP;
    if (str == "cheer" || str == "hurray" || str == "win" || str == "victory") return BEAR_ACT_CHEER;
    if (str == "jump" || str == "hop" || str == "bounce") return BEAR_ACT_JUMP;
    if (str == "hands_up" || str == "surrender") return BEAR_ACT_HANDS_UP;
    if (str == "dance" || str == "twist") return BEAR_ACT_DANCE;
    if (str == "balance" || str == "stand_one_leg") return BEAR_ACT_BALANCE;
    if (str == "lie" || str == "crawl" || str == "rest") return BEAR_ACT_LIE;
    if (str == "pushup" || str == "fitness" || str == "workout") return BEAR_ACT_PUSHUP;
    if (str == "kungfu" || str == "martial" || str == "fight") return BEAR_ACT_KUNGFU;
    if (str == "taichi" || str == "zen") return BEAR_ACT_TAICHI;
    if (str == "wingchun" || str == "punch" || str == "boxing") return BEAR_ACT_WINGCHUN;
    if (str == "dragon_punch" || str == "shoryuken" || str == "uppercut") return BEAR_ACT_DRAGON_PUNCH;
    if (str == "moonwalk" || str == "glide" || str == "mj") return BEAR_ACT_MOONWALK;
    if (str == "cyber_defense" || str == "shield" || str == "defense") return BEAR_ACT_CYBER_DEFENSE;
    if (str == "turn" || str == "turn_around" || str == "turn_back" || str == "back") return BEAR_ACT_TURN_AROUND;
    if (str == "spin" || str == "rotate" || str == "pirouette") return BEAR_ACT_SPIN;
    if (str == "locked_try" || str == "scratch_head" || str == "puzzled") return BEAR_ACT_LOCKED_TRY;
    return BEAR_ACT_IDLE;
}

inline const char* bearActionToString(BearAction act) {
    switch (act) {
        case BEAR_ACT_WAVE: return "wave";
        case BEAR_ACT_BOW: return "bow";
        case BEAR_ACT_SIT: return "sit";
        case BEAR_ACT_STRETCH: return "stretch";
        case BEAR_ACT_CLAP: return "clap";
        case BEAR_ACT_CHEER: return "cheer";
        case BEAR_ACT_JUMP: return "jump";
        case BEAR_ACT_HANDS_UP: return "hands_up";
        case BEAR_ACT_DANCE: return "dance";
        case BEAR_ACT_BALANCE: return "balance";
        case BEAR_ACT_LIE: return "lie";
        case BEAR_ACT_PUSHUP: return "pushup";
        case BEAR_ACT_KUNGFU: return "kungfu";
        case BEAR_ACT_TAICHI: return "taichi";
        case BEAR_ACT_WINGCHUN: return "wingchun";
        case BEAR_ACT_DRAGON_PUNCH: return "dragon_punch";
        case BEAR_ACT_MOONWALK: return "moonwalk";
        case BEAR_ACT_CYBER_DEFENSE: return "cyber_defense";
        case BEAR_ACT_TURN_AROUND: return "turn_around";
        case BEAR_ACT_SPIN: return "spin";
        case BEAR_ACT_LOCKED_TRY: return "locked_try";
        default: return "idle";
    }
}

// 灵宠成长管理器与技能树系统 (Tamagotchi / RPG Growth System)
class BearGrowthManager {
public:
    static BearGrowthManager& getInstance() {
        static BearGrowthManager instance;
        return instance;
    }

    void init() {
        Preferences p;
        if (p.begin("sticks3_cfg", true)) {
            _exp = p.getUInt("bear_exp", 25);
            _level = p.getUChar("bear_lvl", 1);
            p.end();
        } else {
            _exp = 25;
            _level = 1;
        }
        if (_level < 1) _level = 1;
        if (_level > 5) _level = 5;
    }

    uint8_t getLevel() const { return _level; }
    uint32_t getExp() const { return _exp; }

    uint32_t getNextLevelExp() const {
        switch (_level) {
            case 1: return 100;
            case 2: return 250;
            case 3: return 500;
            case 4: return 800;
            default: return 1200;
        }
    }

    uint32_t getCurrentLevelBaseExp() const {
        switch (_level) {
            case 1: return 0;
            case 2: return 100;
            case 3: return 250;
            case 4: return 500;
            default: return 800;
        }
    }

    const char* getLevelTitle() const {
        switch (_level) {
            case 1: return "幼幼萌熊";
            case 2: return "灵动小熊";
            case 3: return "体能健将";
            case 4: return "功夫大师";
            case 5: return "机甲元尊";
            default: return "灵动小熊";
        }
    }

    // 动作解锁门槛查询 (Action Unlock Level Matrix)
    uint8_t getRequiredLevel(BearAction act) const {
        switch (act) {
            case BEAR_ACT_IDLE:
            case BEAR_ACT_WAVE:
            case BEAR_ACT_BOW:
            case BEAR_ACT_SIT:
            case BEAR_ACT_STRETCH:
            case BEAR_ACT_LOCKED_TRY:
                return 1;
            case BEAR_ACT_CLAP:
            case BEAR_ACT_CHEER:
            case BEAR_ACT_JUMP:
            case BEAR_ACT_HANDS_UP:
            case BEAR_ACT_TURN_AROUND:
                return 2;
            case BEAR_ACT_DANCE:
            case BEAR_ACT_BALANCE:
            case BEAR_ACT_LIE:
            case BEAR_ACT_PUSHUP:
            case BEAR_ACT_SPIN:
                return 3;
            case BEAR_ACT_KUNGFU:
            case BEAR_ACT_TAICHI:
            case BEAR_ACT_WINGCHUN:
                return 4;
            case BEAR_ACT_DRAGON_PUNCH:
            case BEAR_ACT_MOONWALK:
            case BEAR_ACT_CYBER_DEFENSE:
                return 5;
            default:
                return 1;
        }
    }

    bool isActionUnlocked(BearAction act) const {
        return _level >= getRequiredLevel(act);
    }

    // 组合技解锁门槛查询 (Combo Unlock Matrix)
    uint8_t getComboRequiredLevel(const std::string& combo_name) const {
        if (combo_name == "greeting") return 2;
        if (combo_name == "fitness") return 3;
        if (combo_name == "martial") return 4;
        if (combo_name == "cyber_supreme") return 5;
        return 1;
    }

    bool isComboUnlocked(const std::string& combo_name) const {
        return _level >= getComboRequiredLevel(combo_name);
    }

    std::vector<BearAction> getComboActions(const std::string& combo_name) const {
        if (combo_name == "greeting") {
            return {BEAR_ACT_WAVE, BEAR_ACT_BOW, BEAR_ACT_CHEER};
        }
        if (combo_name == "fitness") {
            return {BEAR_ACT_STRETCH, BEAR_ACT_JUMP, BEAR_ACT_BALANCE, BEAR_ACT_CLAP};
        }
        if (combo_name == "martial") {
            return {BEAR_ACT_TAICHI, BEAR_ACT_WINGCHUN, BEAR_ACT_KUNGFU, BEAR_ACT_BOW};
        }
        if (combo_name == "cyber_supreme") {
            return {BEAR_ACT_MOONWALK, BEAR_ACT_WINGCHUN, BEAR_ACT_DRAGON_PUNCH, BEAR_ACT_CYBER_DEFENSE};
        }
        return {BEAR_ACT_WAVE};
    }

    // 肢体活动度 (ROM: Range of Motion) 乘数: 等级越高，动作张力与幅度越舒展
    float getRomMultiplier() const {
        return 0.65f + 0.10f * (float)(_level - 1); // 0.65 -> 0.75 -> 0.85 -> 0.95 -> 1.05
    }

    // 动作敏捷度 (过渡阻尼与弹簧速度乘数)
    float getAgilityMultiplier() const {
        return 0.85f + 0.12f * (float)(_level - 1);
    }

    // 胸前专属徽章色彩
    uint16_t getBadgeColor() const {
        switch (_level) {
            case 1: return 0xD440; // 焦糖青铜
            case 2: return 0x07E0; // 翡翠翠绿
            case 3: return 0xFFE0; // 耀金星芒
            case 4: return 0xF800; // 绯红赤霞
            case 5: return 0x07FF; // 苍穹青霓
            default: return 0xFFE0;
        }
    }

    // 累积互动经验值 (声音对话+10, 抚摸+5, 动作训练+15, 组合技+25)
    bool addExp(uint16_t gain, const char* reason = "") {
        _exp += gain;
        bool level_up = false;
        uint32_t threshold = getNextLevelExp();
        if (_exp >= threshold && _level < 5) {
            _level++;
            level_up = true;
            Serial.printf("[GROWTH-UP] ★ Congratulation! Bear Leveled Up to Lv.%u (%s)! %s\n",
                          _level, getLevelTitle(), reason);
        } else {
            Serial.printf("[GROWTH] +%u EXP (%s). Level: %u, Total EXP: %u/%u\n",
                          gain, reason, _level, _exp, threshold);
        }
        save();
        return level_up;
    }

    void setLevel(uint8_t lvl) {
        if (lvl >= 1 && lvl <= 5) {
            _level = lvl;
            save();
        }
    }

    void save() {
        Preferences p;
        if (p.begin("sticks3_cfg", false)) {
            p.putUInt("bear_exp", _exp);
            p.putUChar("bear_lvl", _level);
            p.end();
        }
    }

private:
    BearGrowthManager() : _exp(25), _level(1) {}
    uint32_t _exp;
    uint8_t _level;
};

// 肢体末端执行器姿态 (含肘/膝关节屈曲解算参数)
struct LimbJoint {
    float angle_deg;   // 旋转角 (0 为垂直向下，90 为外展水平，180 为举高过头)
    float flex_x;      // 末端水平位移
    float flex_y;      // 末端垂直位移
    float elbow_flex;  // 肘关节/膝关节弯曲内敛量 (用于计算自然圆弧双段屈伸)
};

// 3D 浮点三维向量 (3D Cartesian Coordinates)
struct Vec3f {
    float x;
    float y;
    float z;

    Vec3f() : x(0.0f), y(0.0f), z(0.0f) {}
    Vec3f(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}
};

// 屏幕透视投影点 (Projected 2D Screen Point with Depth & Perspective Scale)
struct ProjectedPoint {
    float sx;     // 屏幕像素坐标 X
    float sy;     // 屏幕像素坐标 Y
    float sz;     // 深度 Z (用于 Z-Sorting 绘制排序)
    float scale;  // 透视缩放系数
    bool visible; // 是否在视野内
};

// OpenPose 人形 23 骨骼关节点枚举 (OpenPose Humanoid Keypoint IDs)
enum OpenPoseJointId {
    OP_HEAD = 0,         // 头部中枢 (Nose/Head Center)
    OP_NECK = 1,         // 颈部基座 (Neck Base)
    OP_R_EAR = 2,        // 右耳 (R_Ear)
    OP_L_EAR = 3,        // 左耳 (L_Ear)
    OP_R_EYE = 4,        // 右眼 (R_Eye)
    OP_L_EYE = 5,        // 左眼 (L_Eye)
    OP_SPINE = 6,        // 脊柱胸腔 (Spine / MidChest)
    OP_MID_HIP = 7,      // 骨盆中髋 (Pelvis / MidHip Root)
    OP_R_SHOULDER = 8,   // 右肩关节 (R_Shoulder)
    OP_R_ELBOW = 9,      // 右肘关节 (R_Elbow)
    OP_R_WRIST = 10,     // 右腕/前爪 (R_Wrist / Paw)
    OP_L_SHOULDER = 11,  // 左肩关节 (L_Shoulder)
    OP_L_ELBOW = 12,     // 左肘关节 (L_Elbow)
    OP_L_WRIST = 13,     // 左腕/前爪 (L_Wrist / Paw)
    OP_R_HIP = 14,       // 右髋关节 (R_Hip)
    OP_R_KNEE = 15,      // 右膝关节 (R_Knee)
    OP_R_ANKLE = 16,     // 右踝/脚掌 (R_Ankle / Foot)
    OP_L_HIP = 17,       // 左髋关节 (L_Hip)
    OP_L_KNEE = 18,      // 左膝关节 (L_Knee)
    OP_L_ANKLE = 19,     // 左踝/脚掌 (L_Ankle / Foot)
    OP_TAIL = 20,        // 毛茸茸小球尾巴 (Tail)
    OP_SNOUT = 21,       // 奶白立体嘴套与鼻 (Snout)
    OP_BADGE = 22,       // 胸前成长星芒徽章 (Growth Badge)
    OP_JOINT_COUNT = 23
};

// 单关节动力学覆盖配置 (用于单独控制任一关节)
struct JointManualConfig {
    float pitch_deg;
    float roll_deg;
    float yaw_deg;
    bool active;
};

// 3D 欧拉旋转辅助函数 (Yaw -> Pitch -> Roll)
static inline Vec3f rotateEuler3D(const Vec3f& p, float yaw_deg, float pitch_deg, float roll_deg) {
    const float kDegToRad = 0.0174532925f;
    float ry = yaw_deg * kDegToRad;
    float rp = pitch_deg * kDegToRad;
    float rr = roll_deg * kDegToRad;

    // 1. Yaw (Y 轴旋转: 水平左右偏航)
    float cos_y = std::cos(ry);
    float sin_y = std::sin(ry);
    float x1 = p.x * cos_y + p.z * sin_y;
    float y1 = p.y;
    float z1 = -p.x * sin_y + p.z * cos_y;

    // 2. Pitch (X 轴旋转: 前俯后仰)
    float cos_p = std::cos(rp);
    float sin_p = std::sin(rp);
    float x2 = x1;
    float y2 = y1 * cos_p - z1 * sin_p;
    float z2 = y1 * sin_p + z1 * cos_p;

    // 3. Roll (Z 轴旋转: 左右侧倾)
    float cos_r = std::cos(rr);
    float sin_r = std::sin(rr);
    float x3 = x2 * cos_r - y2 * sin_r;
    float y3 = x2 * sin_r + y2 * cos_r;
    float z3 = z2;

    return Vec3f(x3, y3, z3);
}

// 针孔透视相机投影 (Pinhole Perspective Camera Projection)
static inline ProjectedPoint projectCamera(const Vec3f& world_p, float cam_cx = 67.5f, float cam_cy = 118.0f, float focal = 210.0f, float cam_dist = 180.0f) {
    ProjectedPoint proj;
    float denom = world_p.z + cam_dist;
    if (denom < 12.0f) denom = 12.0f; // 防近裁剪面除零
    proj.scale = focal / denom;
    proj.sx = cam_cx + world_p.x * proj.scale;
    proj.sy = cam_cy + world_p.y * proj.scale;
    proj.sz = world_p.z;
    proj.visible = (proj.sx >= -30.0f && proj.sx <= 165.0f && proj.sy >= -30.0f && proj.sy <= 270.0f);
    return proj;
}

// 小熊全身骨骼学数据 (Full-Body Biomechanical Skeleton)
struct BearFullBodySkeleton {
    // 躯干中心锚点 (Center of Mass)
    float body_x;
    float body_y;
    float body_w;
    float body_h;
    float body_tilt;
    float squash_x;
    float squash_y;

    // 头部中心锚点与颈部协同
    float head_x;
    float head_y;
    float head_tilt;
    float head_scale_x;
    float head_scale_y;

    // 四肢末端
    LimbJoint left_arm;
    LimbJoint right_arm;
    LimbJoint left_leg;
    LimbJoint right_leg;

    // 关键多段关节中点 (Elbow & Knee Articulation Midpoints)
    float elbow_lx, elbow_ly;
    float elbow_rx, elbow_ry;
    float knee_lx, knee_ly;
    float knee_rx, knee_ry;

    // 3D OpenPose 人形骨骼空间数据 (3D Humanoid OpenPose Kinematics)
    Vec3f joints_local[OP_JOINT_COUNT];       // 局部骨骼关键点 (以骨盆为局部原点)
    Vec3f joints_world[OP_JOINT_COUNT];       // 3D 旋转后世界坐标
    ProjectedPoint joints_screen[OP_JOINT_COUNT]; // 2D 针孔透视投影屏幕坐标

    float current_yaw_deg;    // 当前水平偏航角 (0° 正面, 180° 背面朝向, 360° 自旋)
    float current_pitch_deg;  // 当前俯仰角
    float current_roll_deg;   // 当前侧倾角
    bool is_back_view;        // 是否背对用户 (背影模式)

    // 特殊姿态标志
    bool is_sitting;
    bool is_lying;
    bool is_jumping;
    bool is_balance_one_leg;
    bool is_pushup;
    bool is_dragon_punch;
    bool is_cyber_defense;
    bool is_locked_try;
    float effect_phase; // 特效脉冲相位
};

// 肢体动力学与骨骼控制器 (整合生物力学校同身法与平滑插值阻尼)
class BearKinematicsController {
public:
    static BearKinematicsController& getInstance() {
        static BearKinematicsController instance;
        return instance;
    }

    void init() {
        BearGrowthManager::getInstance().init();
        _current_action = BEAR_ACT_IDLE;
        _action_start_time = 0;
        _action_duration_ms = 0;
        _combo_queue.clear();
        _combo_idx = 0;
        _last_update_time = millis();

        // 初始化连续姿态阻尼插值状态 (Continuous Pose Damping)
        _smooth_left_arm_deg = 15.0f;
        _smooth_right_arm_deg = 15.0f;
        _smooth_left_arm_fx = 0.0f;
        _smooth_left_arm_fy = 0.0f;
        _smooth_right_arm_fx = 0.0f;
        _smooth_right_arm_fy = 0.0f;
        _smooth_left_arm_ef = 0.0f;
        _smooth_right_arm_ef = 0.0f;

        _smooth_left_leg_deg = 8.0f;
        _smooth_right_leg_deg = 8.0f;
        _smooth_left_leg_fx = 0.0f;
        _smooth_left_leg_fy = 0.0f;
        _smooth_right_leg_fx = 0.0f;
        _smooth_right_leg_fy = 0.0f;

        _smooth_body_tilt = 0.0f;
        _smooth_head_tilt = 0.0f;
        _smooth_body_shift_x = 0.0f;
        _smooth_body_shift_y = 0.0f;

        // 3D 偏航与转身状态初始化
        _target_yaw_deg = 0.0f;
        _smooth_yaw_deg = 0.0f;
        _turn_start_time = 0;
        _turn_duration_ms = 0;
        _is_turning_around = false;
        _is_spinning = false;
        for (int i = 0; i < OP_JOINT_COUNT; i++) {
            _manual_joints[i] = {0.0f, 0.0f, 0.0f, false};
        }
    }

    // 触发单个动作 (支持等级检查与未解锁萌态回退保护)
    bool triggerAction(BearAction act, uint32_t duration_ms = 2800) {
        auto& gm = BearGrowthManager::getInstance();
        if (!gm.isActionUnlocked(act)) {
            // 动作未解锁：触发萌态抓头困惑反馈
            Serial.printf("[KINEMATICS] Action '%s' LOCKED! (Required Lv.%u, Current Lv.%u). Triggering locked try fallback.\n",
                          bearActionToString(act), gm.getRequiredLevel(act), gm.getLevel());
            _combo_queue.clear();
            _combo_idx = 0;
            _current_action = BEAR_ACT_LOCKED_TRY;
            _action_start_time = millis();
            _action_duration_ms = 2400;
            return false;
        }

        if (act == BEAR_ACT_TURN_AROUND) {
            triggerTurnAround(duration_ms);
            gm.addExp(15, "turn_around");
            return true;
        } else if (act == BEAR_ACT_SPIN) {
            triggerSpinPirouette(duration_ms);
            gm.addExp(15, "spin");
            return true;
        }

        _combo_queue.clear();
        _combo_idx = 0;
        _current_action = act;
        _action_start_time = millis();
        _action_duration_ms = duration_ms;
        // 增加肢体锻炼成长值
        gm.addExp(15, bearActionToString(act));
        return true;
    }

    // 3D 偏航与转身控制接口 (Yaw Turn & 3D Control)
    void setTargetYaw(float yaw_deg) {
        _target_yaw_deg = yaw_deg;
        _is_turning_around = false;
        _is_spinning = false;
    }

    void triggerTurnAround(uint32_t duration_ms = 1400) {
        _is_turning_around = true;
        _is_spinning = false;
        _turn_start_time = millis();
        _turn_duration_ms = duration_ms;
        _current_action = BEAR_ACT_TURN_AROUND;
        _action_start_time = millis();
        _action_duration_ms = duration_ms;
    }

    void triggerSpinPirouette(uint32_t duration_ms = 1800) {
        _is_spinning = true;
        _is_turning_around = false;
        _turn_start_time = millis();
        _turn_duration_ms = duration_ms;
        _current_action = BEAR_ACT_SPIN;
        _action_start_time = millis();
        _action_duration_ms = duration_ms;
    }

    // 独立控制指定关节点 (OpenPose Humanoid Keypoint Control)
    void setJointAngle(uint8_t joint_id, float pitch, float roll, float yaw) {
        if (joint_id < OP_JOINT_COUNT) {
            _manual_joints[joint_id].pitch_deg = pitch;
            _manual_joints[joint_id].roll_deg = roll;
            _manual_joints[joint_id].yaw_deg = yaw;
            _manual_joints[joint_id].active = true;
        }
    }

    void clearJointOverrides() {
        for (int i = 0; i < OP_JOINT_COUNT; i++) {
            _manual_joints[i].active = false;
        }
    }

    float getYaw() const { return _smooth_yaw_deg; }
    bool isTurnAround() const { return _is_turning_around; }
    bool isSpinning() const { return _is_spinning; }

    // 触发宏组合动作序列
    bool triggerCombo(const std::vector<BearAction>& combo) {
        if (combo.empty()) return false;
        _combo_queue = combo;
        _combo_idx = 0;
        _current_action = _combo_queue[0];
        _action_start_time = millis();
        _action_duration_ms = 2200;
        BearGrowthManager::getInstance().addExp(25, "Combo Execution");
        return true;
    }

    // 通过组合技名称触发
    bool triggerComboByName(const std::string& combo_name) {
        auto& gm = BearGrowthManager::getInstance();
        if (!gm.isComboUnlocked(combo_name)) {
            Serial.printf("[KINEMATICS] Combo '%s' LOCKED! (Required Lv.%u, Current Lv.%u).\n",
                          combo_name.c_str(), gm.getComboRequiredLevel(combo_name), gm.getLevel());
            _combo_queue.clear();
            _combo_idx = 0;
            _current_action = BEAR_ACT_LOCKED_TRY;
            _action_start_time = millis();
            _action_duration_ms = 2400;
            return false;
        }
        return triggerCombo(gm.getComboActions(combo_name));
    }

    BearAction getCurrentAction() const { return _current_action; }

    // 姿态解算核心引擎 (含生物力学协调、预备蓄力与阻尼平滑)
    void solveSkeleton(uint32_t now, float roll, float pitch, float a_mag, float diff_a,
                       sticks3::AvatarMood mood, sticks3::BailianAgentState bl_state, uint8_t mic_vu,
                       BearFullBodySkeleton& out_skel) {
        auto& growth = BearGrowthManager::getInstance();
        float rom = growth.getRomMultiplier();
        float agility = growth.getAgilityMultiplier();
        float t = (float)now * 0.001f;

        // 计算每帧增量时间 dt (秒)
        float dt = (now > _last_update_time) ? (float)(now - _last_update_time) * 0.001f : 0.012f;
        _last_update_time = now;
        if (dt > 0.1f) dt = 0.1f; // 防卡顿极限钳位

        // 1. 组合动作自动时序推进
        if (_action_duration_ms > 0 && (now - _action_start_time > _action_duration_ms)) {
            if (!_combo_queue.empty() && (_combo_idx + 1 < _combo_queue.size())) {
                _combo_idx++;
                _current_action = _combo_queue[_combo_idx];
                _action_start_time = now;
                _action_duration_ms = 2200;
            } else {
                _current_action = BEAR_ACT_IDLE;
                _action_duration_ms = 0;
                _combo_queue.clear();
            }
        }

        // 当前动作相对进度相位 (0.0 ~ 1.0)
        float act_phase = 0.0f;
        if (_action_duration_ms > 0) {
            act_phase = constrain((float)(now - _action_start_time) / (float)_action_duration_ms, 0.0f, 1.0f);
        }
        out_skel.effect_phase = act_phase;

        // 1.5 3D 水平偏航与空间转身/旋转状态机更新
        if (_is_turning_around) {
            uint32_t elapsed = now - _turn_start_time;
            if (elapsed < _turn_duration_ms) {
                float p = (float)elapsed / (float)_turn_duration_ms;
                // 缓入缓出 0 -> 180 -> 0 (优雅转身秀尾巴再转回)
                float s = std::sin(p * 3.14159265f);
                _target_yaw_deg = s * 180.0f;
            } else {
                _is_turning_around = false;
                _target_yaw_deg = 0.0f;
            }
        } else if (_is_spinning) {
            uint32_t elapsed = now - _turn_start_time;
            if (elapsed < _turn_duration_ms) {
                float p = (float)elapsed / (float)_turn_duration_ms;
                _target_yaw_deg = p * 360.0f;
            } else {
                _is_spinning = false;
                _target_yaw_deg = 0.0f;
            }
        }

        // 偏航角平滑插值阻尼 (Smooth Yaw Damping)
        float yaw_smooth = constrain(dt * 12.0f * agility, 0.05f, 0.85f);
        _smooth_yaw_deg += (_target_yaw_deg - _smooth_yaw_deg) * yaw_smooth;

        // 2. 有机呼吸浮沉与弹性果冻形变 (Organic Breathing & Squash-Stretch)
        float breath = std::sin(t * 2.4f) * 1.6f;
        float belly_breath = std::cos(t * 2.4f) * 1.3f;

        out_skel.squash_x = 1.0f + 0.025f * std::cos(t * 2.4f);
        out_skel.squash_y = 1.0f - 0.025f * std::cos(t * 2.4f);

        if (diff_a > 0.40f) {
            float bump_osc = std::sin(t * 18.0f) * 0.18f;
            out_skel.squash_x += bump_osc;
            out_skel.squash_y -= bump_osc;
        }

        // 3. 基础重心与躯干解算 (Center of Mass & Balance)
        float tilt_dx = constrain(roll * 0.28f, -16.0f, 16.0f);
        float tilt_dy = constrain(pitch * 0.20f, -12.0f, 12.0f);

        float target_body_x = 67.0f + tilt_dx * 0.7f;
        float target_body_y = 120.0f + tilt_dy * 0.5f + breath * 0.6f;
        float target_body_tilt = constrain(roll * 0.16f, -14.0f, 14.0f);
        float target_head_tilt = constrain(roll * 0.12f, -12.0f, 12.0f);
        float target_body_shift_x = 0.0f;
        float target_body_shift_y = 0.0f;

        out_skel.is_sitting = (_current_action == BEAR_ACT_SIT || mood == sticks3::MOOD_SLEEP);
        out_skel.is_lying = (_current_action == BEAR_ACT_LIE);
        out_skel.is_jumping = (_current_action == BEAR_ACT_JUMP);
        out_skel.is_balance_one_leg = (_current_action == BEAR_ACT_BALANCE);
        out_skel.is_pushup = (_current_action == BEAR_ACT_PUSHUP);
        out_skel.is_dragon_punch = (_current_action == BEAR_ACT_DRAGON_PUNCH);
        out_skel.is_cyber_defense = (_current_action == BEAR_ACT_CYBER_DEFENSE);
        out_skel.is_locked_try = (_current_action == BEAR_ACT_LOCKED_TRY);

        // 4. 生物力学四肢目标姿态目标值 (Target Pose Definition)
        float target_l_arm_deg = 15.0f + roll * 0.32f;
        float target_r_arm_deg = 15.0f - roll * 0.32f;
        float target_l_arm_fx = 0.0f, target_l_arm_fy = 0.0f, target_l_arm_ef = 0.0f;
        float target_r_arm_fx = 0.0f, target_r_arm_fy = 0.0f, target_r_arm_ef = 0.0f;

        float target_l_leg_deg = 8.0f;
        float target_r_leg_deg = 8.0f;
        float target_l_leg_fx = 0.0f, target_l_leg_fy = 0.0f;
        float target_r_leg_fx = 0.0f, target_r_leg_fy = 0.0f;

        // 根据动作类型进行全身协同动力学解算 (Whole-Body Coordinated Motion)
        switch (_current_action) {
            case BEAR_ACT_WAVE: {
                // 挥手动作：右臂高举圆弧挥舞，头部向挥手侧微偏 7°，左臂外展对消平衡
                float wave_sin = std::sin(t * 10.0f);
                target_r_arm_deg = (142.0f + 24.0f * wave_sin) * rom;
                target_r_arm_ef = 4.0f + 2.0f * wave_sin; // 肘部自然微屈
                target_l_arm_deg = 24.0f;
                target_head_tilt += 8.0f * std::sin(t * 4.5f);
                target_body_tilt -= 4.0f; // 躯干反向平衡
                break;
            }
            case BEAR_ACT_BOW: {
                // 鞠躬作揖：上身前倾 26°，双手腹前相抱内敛，头部同步低垂
                target_body_tilt = 26.0f;
                target_head_tilt = 16.0f;
                target_body_shift_y = 6.0f;
                target_l_arm_deg = 28.0f;
                target_r_arm_deg = 28.0f;
                target_l_arm_fx = 5.0f;
                target_r_arm_fx = -5.0f;
                target_l_arm_ef = 6.0f;
                target_r_arm_ef = -6.0f;
                break;
            }
            case BEAR_ACT_SIT: {
                // 乖巧盘坐：双腿前伸外八，双爪轻搭膝盖
                target_body_shift_y = 14.0f;
                target_l_leg_deg = 65.0f;
                target_r_leg_deg = 65.0f;
                target_l_arm_deg = 36.0f;
                target_r_arm_deg = 36.0f;
                target_l_arm_fy = 6.0f;
                target_r_arm_fy = 6.0f;
                break;
            }
            case BEAR_ACT_STRETCH: {
                // 伸懒腰：双手仰天伸展 175°，身躯纵向拉伸，头部后仰惬意
                target_l_arm_deg = 175.0f * rom;
                target_r_arm_deg = 175.0f * rom;
                target_l_arm_ef = -2.0f;
                target_r_arm_ef = 2.0f;
                target_body_shift_y = -5.0f;
                target_head_tilt = -10.0f;
                out_skel.squash_y += 0.08f;
                out_skel.squash_x -= 0.04f;
                break;
            }
            case BEAR_ACT_CLAP: {
                // 鼓掌拍手：双臂在胸前对拍合拢，伴随轻微身体欢快律动
                float clap_osc = std::sin(t * 13.0f);
                float clap_ang = 68.0f + 18.0f * clap_osc * rom;
                target_l_arm_deg = clap_ang;
                target_r_arm_deg = clap_ang;
                target_l_arm_fx = 6.0f + 4.0f * clap_osc;
                target_r_arm_fx = -(6.0f + 4.0f * clap_osc);
                target_l_arm_ef = 8.0f;
                target_r_arm_ef = -8.0f;
                target_body_shift_y = 2.0f * clap_osc;
                break;
            }
            case BEAR_ACT_CHEER:
            case BEAR_ACT_HANDS_UP: {
                // 举手欢呼：V字高举双手，雀跃微晃，欢欣鼓舞
                float cheer_osc = std::sin(t * 8.0f) * 8.0f;
                target_l_arm_deg = (152.0f + cheer_osc) * rom;
                target_r_arm_deg = (152.0f - cheer_osc) * rom;
                target_l_arm_ef = -3.0f;
                target_r_arm_ef = 3.0f;
                target_head_tilt = cheer_osc * 0.5f;
                break;
            }
            case BEAR_ACT_JUMP: {
                // 雀跃跳起：预备蓄力下蹲(0~0.25) -> 爆发起跳腾空(0.25~0.7) -> 落地缓冲(0.7~1.0)
                if (act_phase < 0.25f) {
                    // Anticipation 蓄力深蹲
                    float p = act_phase / 0.25f;
                    target_body_shift_y = 10.0f * p;
                    target_l_leg_deg = 20.0f;
                    target_r_leg_deg = 20.0f;
                    target_l_arm_deg = 30.0f;
                    target_r_arm_deg = 30.0f;
                } else if (act_phase < 0.75f) {
                    // Explosive Stretch 腾空起飞
                    float jump_p = (act_phase - 0.25f) / 0.5f;
                    float jump_h = std::sin(jump_p * 3.14159f) * 26.0f;
                    target_body_shift_y = -jump_h;
                    target_l_arm_deg = 155.0f * rom;
                    target_r_arm_deg = 155.0f * rom;
                    target_l_leg_deg = 16.0f;
                    target_r_leg_deg = 16.0f;
                } else {
                    // Recovery 落地回弹
                    float rec_p = (act_phase - 0.75f) / 0.25f;
                    target_body_shift_y = 6.0f * (1.0f - rec_p);
                }
                break;
            }
            case BEAR_ACT_DANCE: {
                // 摇摆跳舞：节奏摆臀(Sway)、双臂上下律动交替，双脚随拍子轻踩
                float sway = std::sin(t * 6.0f);
                target_body_shift_x = sway * 9.0f;
                target_body_tilt = sway * 14.0f;
                target_head_tilt = -sway * 8.0f;
                target_l_arm_deg = (92.0f + 55.0f * sway) * rom;
                target_r_arm_deg = (92.0f - 55.0f * sway) * rom;
                target_l_arm_ef = 6.0f * sway;
                target_r_arm_ef = -6.0f * sway;
                target_l_leg_fy = (sway > 0) ? -5.0f : 0.0f;
                target_r_leg_fy = (sway < 0) ? -5.0f : 0.0f;
                break;
            }
            case BEAR_ACT_BALANCE: {
                // 金鸡独立：右腿单立，左腿屈膝悬空收起，双臂大鹏展翅微幅振荡平衡
                float bal_wobble = std::sin(t * 7.5f) * 8.0f;
                target_l_leg_deg = 38.0f;
                target_l_leg_fy = -13.0f;
                target_r_leg_deg = 5.0f;
                target_l_arm_deg = (85.0f + bal_wobble) * rom;
                target_r_arm_deg = (85.0f - bal_wobble) * rom;
                target_body_tilt = bal_wobble * 0.6f;
                target_l_arm_ef = 4.0f;
                target_r_arm_ef = -4.0f;
                break;
            }
            case BEAR_ACT_LIE: {
                // 趴下休息：平趴地面，四肢向外舒展
                target_body_shift_y = 22.0f;
                target_l_arm_deg = 78.0f;
                target_r_arm_deg = 78.0f;
                target_l_leg_deg = 78.0f;
                target_r_leg_deg = 78.0f;
                break;
            }
            case BEAR_ACT_PUSHUP: {
                // 俯卧撑锻炼：伏地上下推起，双臂大屈伸，呼哧呼哧
                float pu_cycle = (std::sin(t * 5.0f) + 1.0f) * 0.5f; // 0.0 ~ 1.0
                target_body_shift_y = 16.0f + pu_cycle * 8.0f;
                target_l_leg_deg = 65.0f;
                target_r_leg_deg = 65.0f;
                target_l_arm_deg = 50.0f + pu_cycle * 30.0f;
                target_r_arm_deg = 50.0f + pu_cycle * 30.0f;
                target_l_arm_ef = 12.0f - pu_cycle * 6.0f;
                target_r_arm_ef = -12.0f + pu_cycle * 6.0f;
                break;
            }
            case BEAR_ACT_KUNGFU: {
                // 中国功夫：深蹲马步、右前推掌、左手护腰握拳、躯干侧旋
                target_body_shift_y = 6.0f;
                target_body_tilt = -6.0f;
                target_r_arm_deg = 108.0f * rom;
                target_r_arm_fx = 12.0f;
                target_r_arm_ef = 4.0f;
                target_l_arm_deg = 38.0f;
                target_l_arm_fx = -8.0f;
                target_l_arm_ef = 9.0f;
                target_l_leg_deg = 24.0f;
                target_r_leg_deg = 24.0f;
                target_head_tilt = 8.0f;
                break;
            }
            case BEAR_ACT_TAICHI: {
                // 太极云手：行云流水双手圆周运化，重心柔和游走
                float tc = t * 2.2f;
                target_l_arm_deg = (80.0f + 42.0f * std::sin(tc)) * rom;
                target_r_arm_deg = (80.0f + 42.0f * std::cos(tc)) * rom;
                target_l_arm_ef = 8.0f * std::cos(tc);
                target_r_arm_ef = -8.0f * std::sin(tc);
                target_body_shift_x = std::sin(tc) * 7.0f;
                target_body_tilt = std::sin(tc) * 6.0f;
                break;
            }
            case BEAR_ACT_WINGCHUN: {
                // 咏春日字冲拳连击：左右双拳高速轮番向前冲出，身躯反扭对消
                float punch_speed = t * 14.0f;
                float p_l = std::sin(punch_speed);
                float p_r = std::sin(punch_speed + 3.14159f);
                target_l_arm_deg = (90.0f + 30.0f * p_l) * rom;
                target_r_arm_deg = (90.0f + 30.0f * p_r) * rom;
                target_l_arm_fx = (p_l > 0) ? 14.0f : -2.0f;
                target_r_arm_fx = (p_r > 0) ? -14.0f : 2.0f;
                target_body_tilt = p_l * 5.0f;
                target_l_arm_ef = 5.0f;
                target_r_arm_ef = -5.0f;
                target_body_shift_y = 3.0f;
                break;
            }
            case BEAR_ACT_DRAGON_PUNCH: {
                // 升龙拳飞天暴扣：前摇蓄力下沉 -> 右拳直冲云霄 -> 滞空霸气旋转
                if (act_phase < 0.25f) {
                    target_body_shift_y = 12.0f;
                    target_r_arm_deg = 20.0f;
                    target_l_arm_deg = 35.0f;
                    target_r_arm_ef = 10.0f;
                } else if (act_phase < 0.70f) {
                    float launch_p = (act_phase - 0.25f) / 0.45f;
                    float punch_h = std::sin(launch_p * 3.14159f) * 32.0f;
                    target_body_shift_y = -punch_h;
                    target_r_arm_deg = 180.0f * rom;
                    target_r_arm_fx = 6.0f;
                    target_l_arm_deg = 45.0f;
                    target_body_tilt = 15.0f;
                    target_head_tilt = -14.0f; // 仰头望天
                } else {
                    target_body_shift_y = 4.0f;
                    target_r_arm_deg = 60.0f;
                    target_l_arm_deg = 40.0f;
                }
                break;
            }
            case BEAR_ACT_MOONWALK: {
                // 太空漫步：身体前倾，双脚交替向后滑动，重心向后漂移
                float mw = std::sin(t * 5.0f);
                target_body_shift_x = -mw * 8.0f;
                target_body_tilt = -16.0f; // 身体前倾
                target_head_tilt = 12.0f;
                target_l_arm_deg = 50.0f + mw * 25.0f;
                target_r_arm_deg = 50.0f - mw * 25.0f;
                target_l_leg_fx = mw * 12.0f;
                target_r_leg_fx = -mw * 12.0f;
                target_l_leg_fy = (mw > 0) ? -4.0f : 0.0f;
                target_r_leg_fy = (mw < 0) ? -4.0f : 0.0f;
                break;
            }
            case BEAR_ACT_CYBER_DEFENSE: {
                // 机甲能量盾：双臂合抱胸前交叉，撑开能量屏障，下盘稳固
                target_l_arm_deg = 85.0f;
                target_r_arm_deg = 85.0f;
                target_l_arm_fx = 10.0f;
                target_r_arm_fx = -10.0f;
                target_l_arm_ef = 12.0f;
                target_r_arm_ef = -12.0f;
                target_l_leg_deg = 20.0f;
                target_r_leg_deg = 20.0f;
                target_body_shift_y = 5.0f;
                break;
            }
            case BEAR_ACT_TURN_AROUND: {
                // 180° 萌态转身秀尾巴：双手微抬侧摆，灵动后脑勺与小尾巴
                target_l_arm_deg = 25.0f;
                target_r_arm_deg = 25.0f;
                target_head_tilt = 5.0f * std::sin(t * 4.0f);
                break;
            }
            case BEAR_ACT_SPIN: {
                // 360° 华丽芭蕾自旋：双臂展开呈 T 字平举平衡，旋转飘逸跳跃
                target_l_arm_deg = 75.0f;
                target_r_arm_deg = 75.0f;
                target_body_shift_y = -3.0f;
                break;
            }
            case BEAR_ACT_LOCKED_TRY: {
                // 未解锁抓头困惑反馈：右爪挠耳挠头，身体左右困惑歪斜，萌态可掬
                float scratch = std::sin(t * 11.0f);
                target_r_arm_deg = 150.0f;
                target_r_arm_fx = 6.0f + 3.0f * scratch;
                target_r_arm_fy = -8.0f;
                target_r_arm_ef = 14.0f; // 肘部大屈曲抓头
                target_l_arm_deg = 30.0f;
                target_head_tilt = 16.0f * std::sin(t * 3.5f);
                target_body_tilt = -6.0f * std::sin(t * 3.5f);
                break;
            }
            default: {
                // 闲置与情绪状态微动力学 (Idle & Empathy Gestures)
                if (bl_state == sticks3::BL_STATE_SPEAKING) {
                    float spk = std::sin(t * 7.5f) * 18.0f * rom;
                    target_l_arm_deg = 30.0f + spk;
                    target_r_arm_deg = 35.0f - spk;
                    target_l_arm_ef = 4.0f;
                    target_r_arm_ef = -4.0f;
                } else if (bl_state == sticks3::BL_STATE_LISTENING || mic_vu > 15) {
                    target_l_arm_deg = 85.0f * rom;
                    target_l_arm_fx = -4.0f;
                    target_l_arm_ef = 8.0f;
                    target_r_arm_deg = 20.0f;
                } else if (bl_state == sticks3::BL_STATE_THINKING || mood == sticks3::MOOD_THINK) {
                    target_r_arm_deg = 80.0f * rom;
                    target_r_arm_fx = 4.0f;
                    target_r_arm_ef = 9.0f;
                    target_l_arm_deg = 30.0f;
                    target_head_tilt = -10.0f;
                } else if (mood == sticks3::MOOD_HAPPY) {
                    float cl = 35.0f + 14.0f * std::sin(t * 8.0f);
                    target_l_arm_deg = cl;
                    target_r_arm_deg = cl;
                } else if (mood == sticks3::MOOD_DIZZY || std::abs(roll) > 40.0f) {
                    float diz = std::sin(t * 11.0f);
                    target_body_tilt = diz * 18.0f;
                    target_l_arm_deg = 70.0f + diz * 30.0f;
                    target_r_arm_deg = 70.0f - diz * 30.0f;
                } else if (mood == sticks3::MOOD_SLEEP) {
                    target_l_arm_deg = 45.0f;
                    target_r_arm_deg = 45.0f;
                    target_l_arm_ef = 7.0f;
                    target_r_arm_ef = -7.0f;
                }
                break;
            }
        }

        // 5. 姿态平滑阻尼器计算 (Continuous Exponential Pose Damping)
        // 消除任何动作切换瞬间的生硬折断与跳跃，实现丝滑过渡
        float smooth_factor = constrain(dt * 14.0f * agility, 0.05f, 0.85f);

        _smooth_left_arm_deg += (target_l_arm_deg - _smooth_left_arm_deg) * smooth_factor;
        _smooth_right_arm_deg += (target_r_arm_deg - _smooth_right_arm_deg) * smooth_factor;
        _smooth_left_arm_fx += (target_l_arm_fx - _smooth_left_arm_fx) * smooth_factor;
        _smooth_left_arm_fy += (target_l_arm_fy - _smooth_left_arm_fy) * smooth_factor;
        _smooth_right_arm_fx += (target_r_arm_fx - _smooth_right_arm_fx) * smooth_factor;
        _smooth_right_arm_fy += (target_r_arm_fy - _smooth_right_arm_fy) * smooth_factor;
        _smooth_left_arm_ef += (target_l_arm_ef - _smooth_left_arm_ef) * smooth_factor;
        _smooth_right_arm_ef += (target_r_arm_ef - _smooth_right_arm_ef) * smooth_factor;

        _smooth_left_leg_deg += (target_l_leg_deg - _smooth_left_leg_deg) * smooth_factor;
        _smooth_right_leg_deg += (target_r_leg_deg - _smooth_right_leg_deg) * smooth_factor;
        _smooth_left_leg_fx += (target_l_leg_fx - _smooth_left_leg_fx) * smooth_factor;
        _smooth_left_leg_fy += (target_l_leg_fy - _smooth_left_leg_fy) * smooth_factor;
        _smooth_right_leg_fx += (target_r_leg_fx - _smooth_right_leg_fx) * smooth_factor;
        _smooth_right_leg_fy += (target_r_leg_fy - _smooth_right_leg_fy) * smooth_factor;

        _smooth_body_tilt += (target_body_tilt - _smooth_body_tilt) * smooth_factor;
        _smooth_head_tilt += (target_head_tilt - _smooth_head_tilt) * smooth_factor;
        _smooth_body_shift_x += (target_body_shift_x - _smooth_body_shift_x) * smooth_factor;
        _smooth_body_shift_y += (target_body_shift_y - _smooth_body_shift_y) * smooth_factor;

        // 6. 最终装配骨骼输出 (Assembly into Final Skeleton)
        out_skel.body_x = target_body_x + _smooth_body_shift_x;
        out_skel.body_y = target_body_y + _smooth_body_shift_y;
        out_skel.body_w = 46.0f * out_skel.squash_x;
        out_skel.body_h = 50.0f * out_skel.squash_y + belly_breath;
        out_skel.body_tilt = _smooth_body_tilt;

        if (out_skel.is_sitting) {
            out_skel.body_h -= 8.0f;
            out_skel.body_w += 6.0f;
        } else if (out_skel.is_lying) {
            out_skel.body_h -= 18.0f;
            out_skel.body_w += 16.0f;
        }

        // 头部锚点
        out_skel.head_x = out_skel.body_x + tilt_dx * 0.35f;
        out_skel.head_y = out_skel.body_y - 42.0f + breath * 0.4f;
        out_skel.head_tilt = _smooth_head_tilt;
        out_skel.head_scale_x = out_skel.squash_x;
        out_skel.head_scale_y = out_skel.squash_y;

        // 四肢赋值
        out_skel.left_arm.angle_deg = _smooth_left_arm_deg;
        out_skel.left_arm.flex_x = _smooth_left_arm_fx;
        out_skel.left_arm.flex_y = _smooth_left_arm_fy;
        out_skel.left_arm.elbow_flex = _smooth_left_arm_ef;

        out_skel.right_arm.angle_deg = _smooth_right_arm_deg;
        out_skel.right_arm.flex_x = _smooth_right_arm_fx;
        out_skel.right_arm.flex_y = _smooth_right_arm_fy;
        out_skel.right_arm.elbow_flex = _smooth_right_arm_ef;

        out_skel.left_leg.angle_deg = _smooth_left_leg_deg;
        out_skel.left_leg.flex_x = _smooth_left_leg_fx;
        out_skel.left_leg.flex_y = _smooth_left_leg_fy;
        out_skel.left_leg.elbow_flex = 0.0f;

        out_skel.right_leg.angle_deg = _smooth_right_leg_deg;
        out_skel.right_leg.flex_x = _smooth_right_leg_fx;
        out_skel.right_leg.flex_y = _smooth_right_leg_fy;
        out_skel.right_leg.elbow_flex = 0.0f;

        // 7. 计算肘膝双段关节中点 (Elbow & Knee Articulations)
        float sh_lx = out_skel.body_x - 18.0f;
        float sh_ly = out_skel.body_y - 8.0f;
        float sh_rx = out_skel.body_x + 18.0f;
        float sh_ry = out_skel.body_y - 8.0f;

        float rad_l = out_skel.left_arm.angle_deg * 0.0174533f;
        float rad_r = out_skel.right_arm.angle_deg * 0.0174533f;

        float paw_lx = sh_lx - (22.0f * std::sin(rad_l)) + out_skel.left_arm.flex_x;
        float paw_ly = sh_ly + (22.0f * std::cos(rad_l)) + out_skel.left_arm.flex_y;
        float paw_rx = sh_rx + (22.0f * std::sin(rad_r)) + out_skel.right_arm.flex_x;
        float paw_ry = sh_ry + (22.0f * std::cos(rad_r)) + out_skel.right_arm.flex_y;

        // 肘关节位于肩与爪中点，叠加垂直法向量弯曲偏移 (elbow_flex)
        out_skel.elbow_lx = (sh_lx + paw_lx) * 0.5f - out_skel.left_arm.elbow_flex;
        out_skel.elbow_ly = (sh_ly + paw_ly) * 0.5f + std::abs(out_skel.left_arm.elbow_flex) * 0.4f;

        out_skel.elbow_rx = (sh_rx + paw_rx) * 0.5f + out_skel.right_arm.elbow_flex;
        out_skel.elbow_ry = (sh_ry + paw_ry) * 0.5f + std::abs(out_skel.right_arm.elbow_flex) * 0.4f;

        // 膝关节中点
        float hip_lx = out_skel.body_x - 13.0f;
        float hip_ly = out_skel.body_y + 14.0f;
        float hip_rx = out_skel.body_x + 13.0f;
        float hip_ry = out_skel.body_y + 14.0f;

        float foot_lx = out_skel.body_x - 14.0f + out_skel.left_leg.flex_x;
        float foot_ly = out_skel.body_y + 36.0f + out_skel.left_leg.flex_y;
        float foot_rx = out_skel.body_x + 14.0f + out_skel.right_leg.flex_x;
        float foot_ry = out_skel.body_y + 36.0f + out_skel.right_leg.flex_y;

        out_skel.knee_lx = (hip_lx + foot_lx) * 0.5f - 2.0f;
        out_skel.knee_ly = (hip_ly + foot_ly) * 0.5f;
        out_skel.knee_rx = (hip_rx + foot_rx) * 0.5f + 2.0f;
        out_skel.knee_ry = (hip_ry + foot_ry) * 0.5f;

        // 8. OpenPose 人形 23 关节点 3D 空间装配与透视相机投影 (3D Pose Assembly & Projection)
        out_skel.current_yaw_deg = _smooth_yaw_deg;
        out_skel.current_pitch_deg = _smooth_body_tilt;
        out_skel.current_roll_deg = roll;
        float rad_yaw = _smooth_yaw_deg * 0.0174533f;
        out_skel.is_back_view = (std::cos(rad_yaw) < 0.0f);

        // 局部 3D 关节点位置设置 (以中心骨盆 MidHip 为局部基准)
        out_skel.joints_local[OP_HEAD] = Vec3f(tilt_dx * 0.35f, -42.0f + breath * 0.4f, 0.0f);
        out_skel.joints_local[OP_NECK] = Vec3f(tilt_dx * 0.20f, -22.0f, 0.0f);
        out_skel.joints_local[OP_R_EAR] = Vec3f(out_skel.joints_local[OP_HEAD].x + 24.0f, out_skel.joints_local[OP_HEAD].y - 16.0f, 2.0f);
        out_skel.joints_local[OP_L_EAR] = Vec3f(out_skel.joints_local[OP_HEAD].x - 24.0f, out_skel.joints_local[OP_HEAD].y - 16.0f, 2.0f);
        out_skel.joints_local[OP_R_EYE] = Vec3f(out_skel.joints_local[OP_HEAD].x + 12.0f, out_skel.joints_local[OP_HEAD].y - 1.0f, -12.0f);
        out_skel.joints_local[OP_L_EYE] = Vec3f(out_skel.joints_local[OP_HEAD].x - 12.0f, out_skel.joints_local[OP_HEAD].y - 1.0f, -12.0f);
        out_skel.joints_local[OP_SPINE] = Vec3f(0.0f, -10.0f + belly_breath * 0.5f, 0.0f);
        out_skel.joints_local[OP_MID_HIP] = Vec3f(0.0f, 10.0f, 0.0f);
        out_skel.joints_local[OP_R_SHOULDER] = Vec3f(18.0f, -8.0f, 0.0f);
        out_skel.joints_local[OP_R_ELBOW] = Vec3f(out_skel.elbow_rx - out_skel.body_x, out_skel.elbow_ry - out_skel.body_y, 4.0f);
        out_skel.joints_local[OP_R_WRIST] = Vec3f(paw_rx - out_skel.body_x, paw_ry - out_skel.body_y, -2.0f);
        out_skel.joints_local[OP_L_SHOULDER] = Vec3f(-18.0f, -8.0f, 0.0f);
        out_skel.joints_local[OP_L_ELBOW] = Vec3f(out_skel.elbow_lx - out_skel.body_x, out_skel.elbow_ly - out_skel.body_y, 4.0f);
        out_skel.joints_local[OP_L_WRIST] = Vec3f(paw_lx - out_skel.body_x, paw_ly - out_skel.body_y, -2.0f);
        out_skel.joints_local[OP_R_HIP] = Vec3f(13.0f, 14.0f, 0.0f);
        out_skel.joints_local[OP_R_KNEE] = Vec3f(out_skel.knee_rx - out_skel.body_x, out_skel.knee_ry - out_skel.body_y, 3.0f);
        out_skel.joints_local[OP_R_ANKLE] = Vec3f(foot_rx - out_skel.body_x, foot_ry - out_skel.body_y, 0.0f);
        out_skel.joints_local[OP_L_HIP] = Vec3f(-13.0f, 14.0f, 0.0f);
        out_skel.joints_local[OP_L_KNEE] = Vec3f(out_skel.knee_lx - out_skel.body_x, out_skel.knee_ly - out_skel.body_y, 3.0f);
        out_skel.joints_local[OP_L_ANKLE] = Vec3f(foot_lx - out_skel.body_x, foot_ly - out_skel.body_y, 0.0f);
        out_skel.joints_local[OP_TAIL] = Vec3f(std::sin(t * 7.0f) * 3.0f, 14.0f, 15.0f);
        out_skel.joints_local[OP_SNOUT] = Vec3f(out_skel.joints_local[OP_HEAD].x, out_skel.joints_local[OP_HEAD].y + 6.0f, -14.0f);
        out_skel.joints_local[OP_BADGE] = Vec3f(0.0f, -8.0f, -10.0f);

        // 叠加关节点手动覆盖微调 (Manual Override)
        for (int i = 0; i < OP_JOINT_COUNT; i++) {
            if (_manual_joints[i].active) {
                out_skel.joints_local[i].x += _manual_joints[i].roll_deg * 0.15f;
                out_skel.joints_local[i].y += _manual_joints[i].pitch_deg * 0.15f;
                out_skel.joints_local[i].z += _manual_joints[i].yaw_deg * 0.15f;
            }
        }

        // 执行 3D 欧拉旋转与透视相机投影计算
        for (int i = 0; i < OP_JOINT_COUNT; i++) {
            Vec3f rot = rotateEuler3D(out_skel.joints_local[i], _smooth_yaw_deg, _smooth_body_tilt, 0.0f);
            rot.x += (out_skel.body_x - 67.5f);
            rot.y += (out_skel.body_y - 118.0f);
            out_skel.joints_world[i] = rot;
            out_skel.joints_screen[i] = projectCamera(rot, 67.5f, 118.0f, 210.0f, 180.0f);
        }
    }

private:
    BearKinematicsController()
        : _current_action(BEAR_ACT_IDLE), _action_start_time(0), _action_duration_ms(0),
          _combo_idx(0), _last_update_time(0),
          _smooth_left_arm_deg(15.0f), _smooth_right_arm_deg(15.0f),
          _smooth_left_arm_fx(0.0f), _smooth_left_arm_fy(0.0f),
          _smooth_right_arm_fx(0.0f), _smooth_right_arm_fy(0.0f),
          _smooth_left_arm_ef(0.0f), _smooth_right_arm_ef(0.0f),
          _smooth_left_leg_deg(8.0f), _smooth_right_leg_deg(8.0f),
          _smooth_left_leg_fx(0.0f), _smooth_left_leg_fy(0.0f),
          _smooth_right_leg_fx(0.0f), _smooth_right_leg_fy(0.0f),
          _smooth_body_tilt(0.0f), _smooth_head_tilt(0.0f),
          _smooth_body_shift_x(0.0f), _smooth_body_shift_y(0.0f),
          _target_yaw_deg(0.0f), _smooth_yaw_deg(0.0f),
          _turn_start_time(0), _turn_duration_ms(0),
          _is_turning_around(false), _is_spinning(false) {
        for (int i = 0; i < OP_JOINT_COUNT; i++) {
            _manual_joints[i] = {0.0f, 0.0f, 0.0f, false};
        }
    }

    BearAction _current_action;
    uint32_t _action_start_time;
    uint32_t _action_duration_ms;
    std::vector<BearAction> _combo_queue;
    size_t _combo_idx;
    uint32_t _last_update_time;

    // 平滑阻尼插值状态变量
    float _smooth_left_arm_deg;
    float _smooth_right_arm_deg;
    float _smooth_left_arm_fx, _smooth_left_arm_fy;
    float _smooth_right_arm_fx, _smooth_right_arm_fy;
    float _smooth_left_arm_ef, _smooth_right_arm_ef;

    float _smooth_left_leg_deg, _smooth_right_leg_deg;
    float _smooth_left_leg_fx, _smooth_left_leg_fy;
    float _smooth_right_leg_fx, _smooth_right_leg_fy;

    float _smooth_body_tilt;
    float _smooth_head_tilt;
    float _smooth_body_shift_x;
    float _smooth_body_shift_y;

    // 3D 偏航与关节点覆盖状态变量
    float _target_yaw_deg;
    float _smooth_yaw_deg;
    uint32_t _turn_start_time;
    uint32_t _turn_duration_ms;
    bool _is_turning_around;
    bool _is_spinning;
    JointManualConfig _manual_joints[OP_JOINT_COUNT];
};

} // namespace sticks3
