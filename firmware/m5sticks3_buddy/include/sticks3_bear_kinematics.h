/**
 * @file sticks3_bear_kinematics.h
 * @brief Meta Muse Jollybot Full-Body Skeletal Kinematics, IMU Posture Fusion & RPG Growth System
 * 
 * 1. 全身四肢骨骼学 (Full-Body & Limbs Kinematics): 头部、双耳、躯干胸腹、左右手臂手爪、左右腿脚脚掌
 * 2. 6 轴 IMU 动态姿态解算 (BMI270 Posture Fusion): 倾斜重心平衡、滑步踉跄、失重惊吓、跳跃与碰撞弹性缓冲
 * 3. 情绪状态机联动 (Mood State Machine): 12 种情绪驱动四肢姿态 (鼓掌、垂臂、抱头、抚腮、舞蹈、打坐等)
 * 4. 灵宠养成系统 (Tamagotchi / RPG Growth System): 互动升级 (Lv.1 萌新 ~ Lv.5 机甲元尊)、肢体活动度 (ROM) 随等级成长
 * 5. 自然语言动作与组合控制 (Macro Combo & Limb Control): 挥手、鼓掌、跳舞、功夫、太极、伸懒腰、鞠躬等宏序列
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

// 肢体宏动作枚举
enum BearAction {
    BEAR_ACT_IDLE = 0,
    BEAR_ACT_WAVE,        // 挥手打招呼
    BEAR_ACT_CLAP,        // 鼓掌拍手
    BEAR_ACT_DANCE,       // 摇摆跳舞
    BEAR_ACT_KUNGFU,      // 中国功夫站架
    BEAR_ACT_STRETCH,     // 伸懒腰打哈欠
    BEAR_ACT_BOW,         // 礼貌鞠躬
    BEAR_ACT_JUMP,        // 雀跃跳起
    BEAR_ACT_SIT,         // 乖巧坐下
    BEAR_ACT_LIE,         // 趴下休息
    BEAR_ACT_CHEER,       // 举手欢呼
    BEAR_ACT_TAICHI,      // 太极行云流水
    BEAR_ACT_HANDS_UP,    // 举双手投降
    BEAR_ACT_BALANCE      // 金鸡独立单脚平衡
};

inline BearAction stringToBearAction(const std::string& str) {
    if (str == "wave" || str == "wave_right" || str == "wave_left" || str == "hi") return BEAR_ACT_WAVE;
    if (str == "clap" || str == "applause") return BEAR_ACT_CLAP;
    if (str == "dance" || str == "twist") return BEAR_ACT_DANCE;
    if (str == "kungfu" || str == "martial" || str == "fight") return BEAR_ACT_KUNGFU;
    if (str == "stretch" || str == "yawn") return BEAR_ACT_STRETCH;
    if (str == "bow" || str == "polite") return BEAR_ACT_BOW;
    if (str == "jump" || str == "hop") return BEAR_ACT_JUMP;
    if (str == "sit" || str == "sit_down") return BEAR_ACT_SIT;
    if (str == "lie" || str == "crawl" || str == "rest") return BEAR_ACT_LIE;
    if (str == "cheer" || str == "hurray" || str == "win") return BEAR_ACT_CHEER;
    if (str == "taichi" || str == "zen") return BEAR_ACT_TAICHI;
    if (str == "hands_up" || str == "surrender") return BEAR_ACT_HANDS_UP;
    if (str == "balance" || str == "stand_one_leg") return BEAR_ACT_BALANCE;
    return BEAR_ACT_IDLE;
}

inline const char* bearActionToString(BearAction act) {
    switch (act) {
        case BEAR_ACT_WAVE: return "wave";
        case BEAR_ACT_CLAP: return "clap";
        case BEAR_ACT_DANCE: return "dance";
        case BEAR_ACT_KUNGFU: return "kungfu";
        case BEAR_ACT_STRETCH: return "stretch";
        case BEAR_ACT_BOW: return "bow";
        case BEAR_ACT_JUMP: return "jump";
        case BEAR_ACT_SIT: return "sit";
        case BEAR_ACT_LIE: return "lie";
        case BEAR_ACT_CHEER: return "cheer";
        case BEAR_ACT_TAICHI: return "taichi";
        case BEAR_ACT_HANDS_UP: return "hands_up";
        case BEAR_ACT_BALANCE: return "balance";
        default: return "idle";
    }
}

// 灵宠成长管理器 (Tamagotchi / RPG Growth System)
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

    // 肢体活动度 (ROM: Range of Motion) 乘数: 等级越高，动作幅度越自如张弛
    float getRomMultiplier() const {
        return 0.55f + 0.12f * (float)(_level - 1); // 0.55 -> 0.67 -> 0.79 -> 0.91 -> 1.03
    }

    // 动作敏捷度 (过渡速度乘数)
    float getAgilityMultiplier() const {
        return 0.80f + 0.15f * (float)(_level - 1);
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

    // 累积互动经验值 (声音对话+10, 抚摸+5, 动作训练+15, 运动玩耍+8)
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

// 肢体末端执行器姿态
struct LimbJoint {
    float angle_deg;   // 旋转角 (0 为垂直向下，90 为外展水平，180 为举高过头)
    float flex_x;      // 屈伸微调 X
    float flex_y;      // 屈伸微调 Y
};

// 小熊全身骨骼学数据 (Full-Body Skeleton)
struct BearFullBodySkeleton {
    // 躯干中心锚点 (Center of Mass)
    float body_x;
    float body_y;
    float body_w;
    float body_h;
    float body_tilt;
    float squash_x;
    float squash_y;

    // 头部中心锚点
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

    // 特殊姿态标志
    bool is_sitting;
    bool is_lying;
    bool is_jumping;
    bool is_balance_one_leg;
};

// 肢体动力学与骨骼控制器
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
    }

    // 触发单个动作
    void triggerAction(BearAction act, uint32_t duration_ms = 2800) {
        _combo_queue.clear();
        _combo_idx = 0;
        _current_action = act;
        _action_start_time = millis();
        _action_duration_ms = duration_ms;
        // 增加肢体锻炼成长值
        BearGrowthManager::getInstance().addExp(15, bearActionToString(act));
    }

    // 触发宏组合动作序列 (例如: ["bow", "kungfu", "cheer"])
    void triggerCombo(const std::vector<BearAction>& combo) {
        if (combo.empty()) return;
        _combo_queue = combo;
        _combo_idx = 0;
        _current_action = _combo_queue[0];
        _action_start_time = millis();
        _action_duration_ms = 2200;
        BearGrowthManager::getInstance().addExp(20, "Combo Execution");
    }

    BearAction getCurrentAction() const { return _current_action; }

    // 姿态解算核心引擎
    void solveSkeleton(uint32_t now, float roll, float pitch, float a_mag, float diff_a,
                       sticks3::AvatarMood mood, sticks3::BailianAgentState bl_state, uint8_t mic_vu,
                       BearFullBodySkeleton& out_skel) {
        auto& growth = BearGrowthManager::getInstance();
        float rom = growth.getRomMultiplier();
        float t = (float)now * 0.001f;

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

        // 2. 有机呼吸浮沉与弹性果冻形变 (Squash & Stretch)
        float breath = std::sin(t * 2.5f) * 1.5f;
        float belly_breath = std::cos(t * 2.5f) * 1.2f;

        out_skel.squash_x = 1.0f + 0.02f * std::cos(t * 2.5f);
        out_skel.squash_y = 1.0f - 0.02f * std::cos(t * 2.5f);

        if (diff_a > 0.40f) {
            float bump_osc = std::sin(t * 20.0f) * 0.18f;
            out_skel.squash_x += bump_osc;
            out_skel.squash_y -= bump_osc;
        }

        // 3. 基础躯干与重心解算 (Center of Mass & Balance)
        float tilt_dx = constrain(roll * 0.30f, -18.0f, 18.0f);
        float tilt_dy = constrain(pitch * 0.22f, -14.0f, 14.0f);

        out_skel.body_x = 67.0f + tilt_dx * 0.7f;
        out_skel.body_y = 120.0f + tilt_dy * 0.5f + breath * 0.6f;
        out_skel.body_w = 46.0f * out_skel.squash_x;
        out_skel.body_h = 50.0f * out_skel.squash_y + belly_breath;
        out_skel.body_tilt = constrain(roll * 0.18f, -15.0f, 15.0f);

        out_skel.is_sitting = (_current_action == BEAR_ACT_SIT || mood == sticks3::MOOD_SLEEP);
        out_skel.is_lying = (_current_action == BEAR_ACT_LIE);
        out_skel.is_jumping = (_current_action == BEAR_ACT_JUMP);
        out_skel.is_balance_one_leg = (_current_action == BEAR_ACT_BALANCE);

        // 姿态高度与形态适配
        if (out_skel.is_sitting) {
            out_skel.body_y += 14.0f;
            out_skel.body_h -= 8.0f;
            out_skel.body_w += 6.0f;
        } else if (out_skel.is_lying) {
            out_skel.body_y += 24.0f;
            out_skel.body_h -= 18.0f;
            out_skel.body_w += 16.0f;
        } else if (out_skel.is_jumping) {
            float jump_phase = ((float)(now - _action_start_time) / (float)_action_duration_ms);
            float jump_h = std::sin(jump_phase * 3.14159f) * 22.0f;
            out_skel.body_y -= jump_h;
        }

        // 4. 头部锚点解算 (Head Rigging)
        out_skel.head_x = out_skel.body_x + tilt_dx * 0.35f;
        out_skel.head_y = out_skel.body_y - 42.0f + breath * 0.4f;
        out_skel.head_tilt = constrain(roll * 0.12f, -12.0f, 12.0f);
        out_skel.head_scale_x = out_skel.squash_x;
        out_skel.head_scale_y = out_skel.squash_y;

        // 5. 四肢基础姿态初始值
        // 臂部基线: 微外展 15 度
        out_skel.left_arm.angle_deg = 15.0f + roll * 0.35f;   // 倾斜时逆向外展平衡
        out_skel.right_arm.angle_deg = 15.0f - roll * 0.35f;
        out_skel.left_arm.flex_x = 0;
        out_skel.left_arm.flex_y = 0;
        out_skel.right_arm.flex_x = 0;
        out_skel.right_arm.flex_y = 0;

        // 腿部基线: 垂直站立 8 度微外八
        out_skel.left_leg.angle_deg = 8.0f;
        out_skel.right_leg.angle_deg = 8.0f;
        out_skel.left_leg.flex_x = 0;
        out_skel.left_leg.flex_y = 0;
        out_skel.right_leg.flex_x = 0;
        out_skel.right_leg.flex_y = 0;

        // 6. 动作状态机姿态插值与合成 (Action Inverse Kinematics)
        switch (_current_action) {
            case BEAR_ACT_WAVE: {
                // 右臂高举挥手 (140° ~ 170° 快速正弦挥动)
                out_skel.right_arm.angle_deg = (145.0f + 25.0f * std::sin(t * 11.0f)) * rom;
                out_skel.left_arm.angle_deg = 20.0f;
                out_skel.head_tilt += 8.0f * std::sin(t * 5.0f);
                break;
            }
            case BEAR_ACT_CLAP: {
                // 双臂在胸前对拍 (向前屈曲 75°，向内相对合拢振动)
                float clap_ang = 65.0f + 20.0f * std::sin(t * 14.0f) * rom;
                out_skel.left_arm.angle_deg = clap_ang;
                out_skel.right_arm.angle_deg = clap_ang;
                out_skel.left_arm.flex_x = 6.0f;
                out_skel.right_arm.flex_x = -6.0f;
                break;
            }
            case BEAR_ACT_DANCE: {
                // 身体左右律动摆臀，双臂交替上下摆动
                float sway = std::sin(t * 6.0f);
                out_skel.body_x += sway * 8.0f;
                out_skel.body_tilt += sway * 12.0f;
                out_skel.left_arm.angle_deg = (90.0f + 60.0f * sway) * rom;
                out_skel.right_arm.angle_deg = (90.0f - 60.0f * sway) * rom;
                out_skel.left_leg.flex_y = (sway > 0) ? -5.0f : 0.0f;
                out_skel.right_leg.flex_y = (sway < 0) ? -5.0f : 0.0f;
                break;
            }
            case BEAR_ACT_KUNGFU: {
                // 中国功夫站桩: 右前推掌 (100°)，左侧后护腰握拳 (35°)，深蹲马步
                out_skel.body_y += 6.0f;
                out_skel.right_arm.angle_deg = 105.0f * rom;
                out_skel.right_arm.flex_x = 10.0f;
                out_skel.left_arm.angle_deg = 40.0f;
                out_skel.left_arm.flex_x = -6.0f;
                out_skel.left_leg.angle_deg = 24.0f;
                out_skel.right_leg.angle_deg = 24.0f;
                break;
            }
            case BEAR_ACT_TAICHI: {
                // 太极云手: 双臂缓和圆周运动，重心平滑移位
                out_skel.left_arm.angle_deg = (80.0f + 40.0f * std::sin(t * 2.2f)) * rom;
                out_skel.right_arm.angle_deg = (80.0f + 40.0f * std::cos(t * 2.2f)) * rom;
                out_skel.body_x += std::sin(t * 2.2f) * 6.0f;
                break;
            }
            case BEAR_ACT_STRETCH: {
                // 伸懒腰: 双手伸直向天 (175°)，身体纵向拉伸
                out_skel.left_arm.angle_deg = 175.0f * rom;
                out_skel.right_arm.angle_deg = 175.0f * rom;
                out_skel.body_h += 6.0f;
                out_skel.body_y -= 4.0f;
                break;
            }
            case BEAR_ACT_BOW: {
                // 礼貌鞠躬: 上身前倾 25°，双臂自然贴于体侧
                out_skel.body_tilt = 24.0f;
                out_skel.head_y += 8.0f;
                out_skel.left_arm.angle_deg = 10.0f;
                out_skel.right_arm.angle_deg = 10.0f;
                break;
            }
            case BEAR_ACT_JUMP: {
                // 雀跃跳起: 双手高举 (140°)，双腿收缩跳离地面
                out_skel.left_arm.angle_deg = 145.0f * rom;
                out_skel.right_arm.angle_deg = 145.0f * rom;
                out_skel.left_leg.angle_deg = 18.0f;
                out_skel.right_leg.angle_deg = 18.0f;
                break;
            }
            case BEAR_ACT_CHEER:
            case BEAR_ACT_HANDS_UP: {
                // 举起双手欢呼胜利 V 字型
                out_skel.left_arm.angle_deg = 150.0f * rom;
                out_skel.right_arm.angle_deg = 150.0f * rom;
                break;
            }
            case BEAR_ACT_BALANCE: {
                // 金鸡独立单脚平衡: 右腿立地，左腿弯折提起，双臂大展维持平衡
                out_skel.left_leg.flex_y = -12.0f;
                out_skel.left_leg.angle_deg = 35.0f;
                out_skel.left_arm.angle_deg = (80.0f + 15.0f * std::sin(t * 8.0f)) * rom;
                out_skel.right_arm.angle_deg = (80.0f - 15.0f * std::sin(t * 8.0f)) * rom;
                break;
            }
            case BEAR_ACT_SIT: {
                // 乖巧坐下: 双腿平伸外展向前，双爪置于膝盖
                out_skel.left_leg.angle_deg = 65.0f;
                out_skel.right_leg.angle_deg = 65.0f;
                out_skel.left_arm.angle_deg = 35.0f;
                out_skel.right_arm.angle_deg = 35.0f;
                break;
            }
            case BEAR_ACT_LIE: {
                // 趴下: 四肢摊开平放
                out_skel.left_leg.angle_deg = 80.0f;
                out_skel.right_leg.angle_deg = 80.0f;
                out_skel.left_arm.angle_deg = 80.0f;
                out_skel.right_arm.angle_deg = 80.0f;
                break;
            }
            default: {
                // 7. 闲置与情绪状态微动力学 (Idle & Emotion Micro-Expressions)
                if (bl_state == sticks3::BL_STATE_SPEAKING) {
                    // 大模型说话时双手生动辅助手势交流
                    float speak_g = std::sin(t * 8.0f) * 20.0f * rom;
                    out_skel.left_arm.angle_deg = 30.0f + speak_g;
                    out_skel.right_arm.angle_deg = 35.0f - speak_g;
                } else if (bl_state == sticks3::BL_STATE_LISTENING || mic_vu > 15) {
                    // 倾听时一只小爪轻托耳侧，身体微前倾
                    out_skel.left_arm.angle_deg = 85.0f * rom;
                    out_skel.left_arm.flex_x = -4.0f;
                    out_skel.right_arm.angle_deg = 20.0f;
                    out_skel.head_y += 3.0f;
                } else if (bl_state == sticks3::BL_STATE_THINKING || mood == sticks3::MOOD_THINK) {
                    // 思考时右爪轻点下巴
                    out_skel.right_arm.angle_deg = 80.0f * rom;
                    out_skel.right_arm.flex_x = 4.0f;
                    out_skel.left_arm.angle_deg = 30.0f;
                    out_skel.head_tilt = -10.0f;
                } else if (mood == sticks3::MOOD_HAPPY) {
                    // 开心轻微拍手微动
                    float clap_h = 35.0f + 15.0f * std::sin(t * 8.0f);
                    out_skel.left_arm.angle_deg = clap_h;
                    out_skel.right_arm.angle_deg = clap_h;
                } else if (mood == sticks3::MOOD_DIZZY || std::abs(roll) > 40.0f) {
                    // 眩晕踉跄跌撞
                    float diz = std::sin(t * 12.0f);
                    out_skel.body_tilt = diz * 18.0f;
                    out_skel.left_arm.angle_deg = 70.0f + diz * 30.0f;
                    out_skel.right_arm.angle_deg = 70.0f - diz * 30.0f;
                } else if (mood == sticks3::MOOD_SLEEP) {
                    // 睡眠安详双爪抱腹
                    out_skel.left_arm.angle_deg = 45.0f;
                    out_skel.right_arm.angle_deg = 45.0f;
                }
                break;
            }
        }
    }

private:
    BearKinematicsController()
        : _current_action(BEAR_ACT_IDLE), _action_start_time(0), _action_duration_ms(0), _combo_idx(0) {}
    BearAction _current_action;
    uint32_t _action_start_time;
    uint32_t _action_duration_ms;
    std::vector<BearAction> _combo_queue;
    size_t _combo_idx;
};

} // namespace sticks3
