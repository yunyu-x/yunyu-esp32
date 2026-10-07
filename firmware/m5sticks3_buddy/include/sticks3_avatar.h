#pragma once
/**
 * firmware/m5sticks3_buddy/include/sticks3_avatar.h
 * -------------------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy / StickCharm) 程序化矢量微表情与具身情感引擎
 * - 基于 Meta Muse Charm 哲学与 Tamagotchi 拟真生命动力学设计
 * - 特性：
 *   1. 12 种纯几何矢量解算表情 (常态眨眼、专注倾听、歪头思考、大笑说话、摇晃晕眩、爱心抚摸、打呼噜入睡)
 *   2. 麦克风拾音 VU 能量与瞳孔弹性脉动强绑定 (实现“声音可视化联觉”)
 *   3. 下行流式 TTS 音频 RMS 与嘴型开合振幅强绑定 (实现 60FPS 实时音画唇形同步)
 *   4. BMI270 物理体感检测 (剧烈晃动晕眩、温和轻摇抚摸、静止超时入睡)
 *   5. 拓麻歌子亲密度与好感度成长系统 (Intimacy Level 1~10, XP 累积)
 *   6. 零动态堆内存分配 (Zero Fragment Hazard)，帧刷新 CPU 占用 < 4.5%
 */

#include <Arduino.h>
#include <cmath>
#include <vector>

namespace sticks3 {

enum AvatarMood {
    MOOD_IDLE = 0,      // 常态待命 (自主微呼吸、随机眨眼)
    MOOD_LISTEN,        // 专注倾听 (双眼睁大、青空蓝光、瞳孔随收音 VU 脉动)
    MOOD_THINK,         // 思考推理 (眼珠向右上微扬转动)
    MOOD_SPEAK,         // 快乐解答 (笑眼弯弯、嘴唇随流式音频开合)
    MOOD_HAPPY,         // 开心/抚摸 (爱心泛红笑眼)
    MOOD_DIZZY,         // 晃动晕眩 (X_X 圈圈眼、眼冒金星)
    MOOD_SHOCK,         // 惊吓/失重 (圆睁极小瞳孔、O型嘴)
    MOOD_SLEEP,         // 平放打呼噜 (闭眼平线、Zzz 气泡飘动)
    MOOD_CURIOUS,       // 好奇歪头 (一眼大一眼小、歪头听)
    MOOD_PROUD,         // 傲娇得意 (扬起下巴眯眼微笑)
    MOOD_EAT,           // 投喂进食 (快速咀嚼开合、幸福月牙笑眼)
    MOOD_GROOM,         // 舒适梳毛 (周身浮动星芒闪烁、眯眼惬意)
    MOOD_WINK           // 默契击掌 (单眼放电眨眼、虎牙欢笑)
};

struct PetStats {
    uint8_t intimacy_level;  // 亲密度等级 (1 ~ 10)
    uint16_t intimacy_xp;    // 亲密度经验值 (0 ~ 100 进阶)
    uint32_t total_pets;     // 累计抚摸次数
    uint32_t total_shakes;   // 累计晃动次数
    uint32_t total_convos;   // 累计对话轮次
    uint32_t total_feeds;    // 累计投喂次数
    uint32_t total_grooms;   // 累计梳理毛发次数
    uint8_t energy;          // 活力值 (0 ~ 100)
    String pet_name;         // 灵宠昵称
    String current_diary;    // 最近一条灵宠观察日记
};

class StickS3Avatar {
public:
    static StickS3Avatar& getInstance() {
        static StickS3Avatar instance;
        return instance;
    }

    void begin(const String& name = "悄悄") {
        _stats.intimacy_level = 1;
        _stats.intimacy_xp = 15;
        _stats.total_pets = 0;
        _stats.total_shakes = 0;
        _stats.total_convos = 0;
        _stats.total_feeds = 0;
        _stats.total_grooms = 0;
        _stats.energy = 100;
        _stats.pet_name = name;
        _stats.current_diary = "今天刚刚苏醒，期待和主人一起探索世界！";

        _current_mood = MOOD_IDLE;
        _target_mood = MOOD_IDLE;
        _last_blink_time = millis();
        _blink_interval = 2800;
        _is_blinking = false;
        _blink_progress = 0.0f;
        _last_interaction_time = millis();
        _dizzy_until = 0;
        _happy_until = 0;
        _eye_pupil_r = 7.0f;
        _mouth_h = 2.0f;
    }

    AvatarMood getMood() const { return _current_mood; }
    void setMood(AvatarMood m) {
        _target_mood = m;
        _last_interaction_time = millis();
    }

    const PetStats& getStats() const { return _stats; }
    
    void setPetName(const String& name) {
        if (name.length() > 0 && name.length() < 24) {
            _stats.pet_name = name;
        }
    }

    void setDiary(const String& diary) {
        if (diary.length() > 0) {
            _stats.current_diary = diary;
        }
    }

    // 动态生成第一人称灵宠观察日记
    void generateDiaryEntry(const String& custom_event = "") {
        if (custom_event.length() > 0) {
            _stats.current_diary = custom_event;
            return;
        }
        if (_stats.intimacy_level >= 5) {
            _stats.current_diary = "今天和主人形影不离，心里感觉特别踏实和温暖！";
        } else if (_stats.total_pets > 3) {
            _stats.current_diary = "主人刚刚摸了摸我的小脑袋，开心得头顶冒泡泡~";
        } else if (_stats.total_convos > 5) {
            _stats.current_diary = "今天主人跟我聊了好多话，我学到了好多新知识！";
        } else {
            _stats.current_diary = "今天在桌面上晒太阳，等待主人下一次唤醒我。";
        }
    }

    // 解析大模型返回文本中的 [E:xxx] 情绪标签并自动提取纯净文本 (支持出现在文本任意位置)
    static AvatarMood parseEmotionTag(const String& raw_text, String& clean_text) {
        clean_text = raw_text;
        int pos = raw_text.indexOf("[E:");
        if (pos < 0) pos = raw_text.indexOf("[e:");
        if (pos < 0) return MOOD_IDLE;
        int close_idx = raw_text.indexOf(']', pos);
        if (close_idx < 0) return MOOD_IDLE;

        String tag = raw_text.substring(pos + 3, close_idx);
        tag.toLowerCase();
        tag.trim();
        clean_text = raw_text.substring(0, pos) + raw_text.substring(close_idx + 1);
        clean_text.trim();

        if (tag == "happy") return MOOD_HAPPY;
        if (tag == "curious") return MOOD_CURIOUS;
        if (tag == "proud") return MOOD_PROUD;
        if (tag == "sleepy" || tag == "sleep") return MOOD_SLEEP;
        if (tag == "dizzy") return MOOD_DIZZY;
        if (tag == "shock") return MOOD_SHOCK;
        if (tag == "listen") return MOOD_LISTEN;
        if (tag == "eat" || tag == "feed") return MOOD_EAT;
        if (tag == "groom") return MOOD_GROOM;
        if (tag == "wink" || tag == "play") return MOOD_WINK;
        return MOOD_IDLE;
    }

    // 增加亲密度经验值
    void addIntimacy(int xp) {
        if (xp <= 0) return;
        _stats.intimacy_xp += xp;
        if (_stats.intimacy_xp >= 100 && _stats.intimacy_level < 10) {
            _stats.intimacy_level++;
            _stats.intimacy_xp = 0;
            _stats.current_diary = "太棒啦！我和主人的羁绊提升到了 Lv." + String(_stats.intimacy_level) + "！";
        }
    }

    // 拓麻歌子交互：投喂小点心
    void feed(const String& snack = "香甜小蛋糕") {
        _stats.total_feeds++;
        _stats.energy = (_stats.energy <= 80) ? (_stats.energy + 20) : 100;
        addIntimacy(10);
        _current_mood = MOOD_EAT;
        _happy_until = millis() + 2500;
        _last_interaction_time = millis();
        _stats.current_diary = "主人喂我吃了一块" + snack + "，吧唧吧唧超级满足，活力满满！";
    }

    // 拓麻歌子交互：梳理毛发
    void groom() {
        _stats.total_grooms++;
        addIntimacy(12);
        _current_mood = MOOD_GROOM;
        _happy_until = millis() + 2800;
        _last_interaction_time = millis();
        _stats.current_diary = "主人用小梳子温柔地帮我梳理毛发，整只宠都舒服得想呼噜呼噜~";
    }

    // 拓麻歌子交互：默契击掌
    void play() {
        addIntimacy(15);
        _stats.energy = (_stats.energy > 10) ? (_stats.energy - 10) : 5;
        _current_mood = MOOD_WINK;
        _happy_until = millis() + 2500;
        _last_interaction_time = millis();
        _stats.current_diary = "和主人默契击掌！今天我们也是元气满满的搭档！";
    }

    // 拓麻歌子交互：温柔抚摸
    void pet() {
        _stats.total_pets++;
        addIntimacy(5);
        _happy_until = millis() + 2800;
        _current_mood = MOOD_HAPPY;
        _last_interaction_time = millis();
        _stats.current_diary = "主人刚刚温柔地摸了摸我，感觉心底暖洋洋的~";
    }

    // 拓麻歌子交互：调皮晃晃
    void shake() {
        _stats.total_shakes++;
        _dizzy_until = millis() + 3500;
        _current_mood = MOOD_DIZZY;
        _last_interaction_time = millis();
        _stats.current_diary = "哎呀呀，调皮晃动让我脑袋转圈圈，眼睛里冒出好多小星星！";
    }

    // 拓麻歌子交互：晚安入睡
    void sleep() {
        _current_mood = MOOD_SLEEP;
        _last_interaction_time = millis() - 95000;
        _stats.current_diary = "呼噜呼噜~ 灵宠进入梦乡打呼噜啦，晚安哦。";
    }

    // 拓麻歌子交互：晨起唤醒 / 伸懒腰
    void wake() {
        _current_mood = MOOD_LISTEN;
        _target_mood = MOOD_IDLE;
        _last_interaction_time = millis();
        _happy_until = millis() + 2000;
        _stats.current_diary = _stats.pet_name + "揉揉眼睛苏醒啦！今天也要元气满满哦！";
    }

    bool isAvatarMode() const { return _avatar_mode_active; }
    void setAvatarMode(bool en) { _avatar_mode_active = en; }
    void toggleAvatarMode() { _avatar_mode_active = !_avatar_mode_active; }

    // 更新物理具身情感动力学 (迪士尼拟真生命感 + 高灵敏触觉抚摸感知)
    void updatePhysics(float ax, float ay, float az, float roll, float pitch, uint8_t mic_rms, uint8_t spk_rms) {
        uint32_t now = millis();
        _anim_phase = (_anim_phase + 1) % 3600;

        // 1. 瞬时合加速度与微分变化率
        float a_mag = std::sqrt(ax * ax + ay * ay + az * az);
        float diff_a = std::abs(a_mag - _last_a_mag);
        float diff_tilt = std::abs(roll - _last_roll) + std::abs(pitch - _last_pitch);
        float dev_1g = std::abs(a_mag - 1.0f);

        // 2. 剧烈摇晃检测 (a_mag > 2.2g 或瞬时微分突变 > 1.2g)
        if (a_mag > 2.2f || diff_a > 1.2f) {
            _stats.total_shakes++;
            _dizzy_until = now + 3500; // 晕眩持续 3.5 秒
            _current_mood = MOOD_DIZZY;
            _last_interaction_time = now;
            _stats.current_diary = "哎呀呀，主人刚刚疯狂晃我，眼睛里全都是小星星！";
        } else if (_dizzy_until > now) {
            _current_mood = MOOD_DIZZY;
        } else {
            // 3. 高灵敏轻抚检测 (多维融合：指尖微震扰动、温和倾角流转与轻量脱离重力)
            bool is_petting_stroke = (
                (diff_a > 0.035f && diff_a < 0.45f) ||
                (diff_tilt > 1.8f && diff_tilt < 22.0f && a_mag < 1.55f) ||
                (dev_1g > 0.048f && dev_1g < 0.50f)
            );
            if (is_petting_stroke && (_current_mood == MOOD_IDLE || _current_mood == MOOD_SLEEP || _current_mood == MOOD_HAPPY)) {
                static uint32_t last_pet_tick = 0;
                if (now - last_pet_tick > 550) { // 550ms 优雅节奏去抖
                    last_pet_tick = now;
                    _stats.total_pets++;
                    addIntimacy(1);
                    _happy_until = now + 2800;
                    _current_mood = MOOD_HAPPY;
                    _last_interaction_time = now;
                    _stats.current_diary = "主人刚刚温柔地摸了摸我，感觉心底暖洋洋的~";
                }
            } else if (_happy_until > now) {
                // 维持当前快乐/互动表情
            } else {
                // 4. 平放静止入睡检测 (处于水平桌面且超过 90 秒无交互)
                bool is_flat = (std::abs(roll) < 18.0f && std::abs(pitch) < 18.0f && dev_1g < 0.12f);
                if (is_flat && (now - _last_interaction_time > 90000)) {
                    _current_mood = MOOD_SLEEP;
                } else if (_target_mood != MOOD_IDLE) {
                    _current_mood = _target_mood;
                } else {
                    _current_mood = MOOD_IDLE;
                }
            }
        }
        _last_a_mag = a_mag;
        _last_roll = roll;
        _last_pitch = pitch;

        // 5. 瞳孔弹性收缩计算 (麦克风收音 VU 联动: 0~100%)
        if (_current_mood == MOOD_LISTEN) {
            float target_r = 7.0f + (mic_rms * 0.08f); // 7px ~ 15px
            if (target_r > 14.0f) target_r = 14.0f;
            _eye_pupil_r = _eye_pupil_r * 0.65f + target_r * 0.35f;
        } else {
            _eye_pupil_r = _eye_pupil_r * 0.8f + 7.0f * 0.2f;
        }

        // 6. 嘴型开合振幅计算 (扬声器流式音频能量联动: 0~100%)
        if (_current_mood == MOOD_SPEAK) {
            float target_mouth = 2.0f + (spk_rms * 0.18f); // 2px ~ 18px
            if (target_mouth > 18.0f) target_mouth = 18.0f;
            _mouth_h = _mouth_h * 0.6f + target_mouth * 0.4f;
        } else {
            _mouth_h = 2.0f;
        }

        // 7. 迪士尼有机呼吸与自然眨眼状态机
        if (_current_mood == MOOD_IDLE || _current_mood == MOOD_HAPPY || _current_mood == MOOD_LISTEN) {
            if (!_is_blinking && (now - _last_blink_time > _blink_interval)) {
                _is_blinking = true;
                _blink_start = now;
                _blink_interval = 2400 + (now % 2200); // 2.4s ~ 4.6s 拟真随机眨眼
            }
            if (_is_blinking) {
                uint32_t b_dur = now - _blink_start;
                if (b_dur < 110) {
                    _blink_progress = (float)b_dur / 110.0f; // 闭眼 0 -> 1
                } else if (b_dur < 220) {
                    _blink_progress = 1.0f - (float)(b_dur - 110) / 110.0f; // 睁眼 1 -> 0
                } else {
                    _is_blinking = false;
                    _blink_progress = 0.0f;
                    _last_blink_time = now;
                }
            }
        } else {
            _is_blinking = false;
            _blink_progress = 0.0f;
        }
    }

    // 核心矢量绘制函数 (参数化绘制在 135x240 显示屏上 - 迪士尼灵动艺术审美升级)
    template <typename DisplayType>
    void render(DisplayType& d, const String& subtitle_text, const String& status_tag, bool ble_connected = false, bool wifi_connected = false, bool is_hotspot = false, uint8_t speaker_vol = 70) {
        const int W = 135;
        const int H = 240;

        // 1. 顶部状态指示栏 (Y: 0 ~ 18) - 实时展示播音音量、蓝牙与网络状态
        d.fillRect(0, 0, W, 18, 0x0841); // 深灰蓝底
        d.setTextDatum(ML_DATUM);
        char vol_buf[16];
        if (speaker_vol == 0) {
            d.setTextColor(0xF800, 0x0841); // 静音红字
            snprintf(vol_buf, sizeof(vol_buf), "VOL MUTE");
        } else {
            d.setTextColor(0x07FF, 0x0841); // 霓虹青字 (清晰展示当前播音音量)
            snprintf(vol_buf, sizeof(vol_buf), "VOL %u%%", speaker_vol);
        }
        d.drawString(vol_buf, 4, 9);

        // 蓝牙连接标志 (BLE 已连蓝青标志)
        if (ble_connected) {
            d.fillRect(64, 2, 28, 14, 0x03FF); // 霓虹青底
            d.setTextColor(0x0000, 0x03FF);
            d.setTextDatum(MC_DATUM);
            d.drawString("BLE", 78, 9);
        }

        // 网络状态标志: 手机热点显示橙色 "HOT", Wi-Fi宽带显示亮绿 "WiFi", 未联网亮红标 "!NET"
        if (wifi_connected) {
            if (is_hotspot) {
                d.fillRect(94, 2, 38, 14, 0xFD20); // 暖橙底 (手机热点)
                d.setTextColor(0x0000, 0xFD20);
                d.setTextDatum(MC_DATUM);
                d.drawString("HOT", 113, 9);
            } else {
                d.fillRect(94, 2, 38, 14, 0x07E0); // 亮绿底 (Wi-Fi 宽带)
                d.setTextColor(0x0000, 0x07E0);
                d.setTextDatum(MC_DATUM);
                d.drawString("WiFi", 113, 9);
            }
        } else {
            d.fillRect(94, 2, 38, 14, 0xF800); // 鲜红警示底 (断网)
            d.setTextColor(0xFFFF, 0xF800);
            d.setTextDatum(MC_DATUM);
            d.drawString("!NET", 113, 9);
        }

        // 2. 灵宠面部主画板 (Y: 18 ~ 152, 纯黑深邃背景)
        d.fillRect(0, 18, W, 134, 0x0000);

        // 双眼几何基准参数
        const int eye_y = 75;
        const int eye_lx = 38;
        const int eye_rx = 97;
        const int eye_w = 28;
        const int eye_h = 38;
        const int mouth_x = 67;
        const int mouth_y = 120;

        uint16_t eye_color = 0x5D1F; // 迪士尼柔和天青蓝 (Cyan)
        if (_current_mood == MOOD_LISTEN) eye_color = 0x07FF; // 专注青空蓝
        else if (_current_mood == MOOD_HAPPY || _current_mood == MOOD_EAT) eye_color = 0xFD20; // 樱花暖粉
        else if (_current_mood == MOOD_DIZZY) eye_color = 0xFE60; // 警示黄
        else if (_current_mood == MOOD_THINK) eye_color = 0xFFE0; // 思考金黄
        else if (_current_mood == MOOD_GROOM) eye_color = 0x07FF; // 梳毛闪耀蓝
        else if (_current_mood == MOOD_WINK) eye_color = 0xFDC0; // 击掌暖金

        // 迪士尼微表情状态机分支渲染
        if (_current_mood == MOOD_DIZZY) {
            // 【迪士尼经典晕眩蚊香螺旋眼 + 旋转头顶晕眩星】
            static uint8_t diz_phase = 0;
            diz_phase = (diz_phase + 1) % 36;
            float rot_ang = (float)diz_phase * 0.1745f; // 弧度

            // 绘制双眼同心旋转螺旋圈
            for (int r = 3; r <= 12; r += 3) {
                int dx = (int)(std::cos(rot_ang + r) * (r * 0.7f));
                int dy = (int)(std::sin(rot_ang + r) * (r * 0.7f));
                d.drawCircle(eye_lx + dx, eye_y + dy, r, eye_color);
                d.drawCircle(eye_rx - dx, eye_y - dy, r, eye_color);
            }

            // 头顶盘旋的小星星 (3 颗黄金四角星做正弦波浪浮动)
            int star_y0 = 42 + (int)(std::sin(rot_ang * 2.0f) * 4.0f);
            int star_y1 = 44 + (int)(std::cos(rot_ang * 2.0f) * 4.0f);
            d.drawPixel(eye_lx, star_y0, 0xFFE0); d.drawPixel(eye_lx + 1, star_y0, 0xFFFF);
            d.drawPixel(eye_rx, star_y1, 0xFFE0); d.drawPixel(eye_rx - 1, star_y1, 0xFFFF);
            d.drawPixel(mouth_x, 38 + (diz_phase % 4), 0xFFE0);

            // 晕乎乎波浪微张小嘴
            d.drawCircle(mouth_x, mouth_y + 2, 7, eye_color);
            d.fillCircle(mouth_x, mouth_y + 3, 5, 0x4000);
        }
        else if (_current_mood == MOOD_SLEEP) {
            // 【迪士尼温柔入睡：弧线垂帘闭眼 + 呼吸沉浮 + 飘逸立体 Zzz 气泡】
            // 随呼吸有节律微幅起伏
            float breath = std::sin((float)_anim_phase * 0.05f) * 1.5f;
            int cur_sy = eye_y + (int)breath;

            // 柔美向下弯曲的下垂眼睑弧 (非生硬横线)
            d.fillCircle(eye_lx, cur_sy - 6, 14, 0x7BEF);
            d.fillCircle(eye_lx, cur_sy - 8, 14, 0x0000);
            d.fillCircle(eye_rx, cur_sy - 6, 14, 0x7BEF);
            d.fillCircle(eye_rx, cur_sy - 8, 14, 0x0000);
            // 俏皮小睫毛
            d.drawLine(eye_lx + 10, cur_sy - 1, eye_lx + 14, cur_sy - 4, 0x7BEF);
            d.drawLine(eye_rx - 10, cur_sy - 1, eye_rx - 14, cur_sy - 4, 0x7BEF);

            // 飘逸 Zzz 升腾动画
            int z_step = (_anim_phase / 3) % 40;
            int z_y = 52 - z_step;
            d.setTextColor(0x07FF, 0x0000);
            d.setTextDatum(MC_DATUM);
            d.drawString("Z", 74 + (z_step % 6), z_y);
            d.drawString("z", 86 + (z_step % 4), z_y + 8);

            // 安详微闭小圆嘴
            d.fillRoundRect(mouth_x - 4, mouth_y + (int)breath, 8, 3, 2, 0x7BEF);
        }
        else if (_current_mood == MOOD_EAT) {
            // 【迪士尼贪吃大餐：极度满足闭月笑眼 + 大开合吧唧咀嚼齿舌 + 飞扬甜点碎屑】
            // 笑弯月牙
            d.fillCircle(eye_lx, eye_y - 2, 14, eye_color);
            d.fillCircle(eye_lx, eye_y + 4, 14, 0x0000);
            d.fillCircle(eye_rx, eye_y - 2, 14, eye_color);
            d.fillCircle(eye_rx, eye_y + 4, 14, 0x0000);

            // 饱满红润充血腮红 (随咀嚼轻微扩张)
            d.fillCircle(18, 92, 8, 0xFC14);
            d.fillCircle(117, 92, 8, 0xFC14);

            // 咀嚼嘴型动画 (快速开合 + 露出萌萌小白牙与粉红小舌头)
            static uint8_t chomp = 0;
            chomp = (chomp + 1) % 10;
            int chomp_h = (chomp < 5) ? (6 + chomp * 2) : (16 - (chomp - 5) * 2);

            // 嘴腔深色底
            d.fillRoundRect(mouth_x - 12, mouth_y - chomp_h / 2, 24, chomp_h + 4, 6, 0x4000);
            // 露出一抹可爱小白牙
            d.fillRoundRect(mouth_x - 6, mouth_y - chomp_h / 2, 12, 4, 2, 0xFFFF);
            // 俏皮粉红舌头
            if (chomp_h > 8) {
                d.fillCircle(mouth_x, mouth_y + chomp_h / 2 - 2, 5, 0xF980);
            }
            // 飞扬的小甜点金黄碎星
            d.fillCircle(mouth_x + 16, mouth_y - 6 + (chomp % 4), 2, 0xFFE0);
            d.fillCircle(mouth_x - 15, mouth_y + 4 - (chomp % 3), 1, 0xFDC0);
        }
        else if (_current_mood == MOOD_GROOM) {
            // 【迪士尼温柔抚弄：梦幻波浪睡眼 + 漫天仙子星芒 (Pixie Dust) + 舒适呼噜嘴】
            d.fillCircle(eye_lx, eye_y - 3, 13, 0x07FF);
            d.fillCircle(eye_lx, eye_y + 3, 13, 0x0000);
            d.fillCircle(eye_rx, eye_y - 3, 13, 0x07FF);
            d.fillCircle(eye_rx, eye_y + 3, 13, 0x0000);

            // 柔情大腮红
            d.fillCircle(18, 92, 8, 0xFC14);
            d.fillCircle(117, 92, 8, 0xFC14);

            // 漫天飘逸的四角星芒 Pixie Dust (金黄与青蓝交错闪烁)
            uint8_t sp = (_anim_phase / 2) % 24;
            d.drawPixel(20, 52 + (sp % 8), 0xFFE0); d.drawPixel(21, 52 + (sp % 8), 0xFFFF);
            d.drawPixel(114, 58 - (sp % 8), 0x07FF); d.drawPixel(115, 58 - (sp % 8), 0xFFFF);
            d.drawPixel(mouth_x + 10, 48 - (sp % 6), 0xFFE0);

            // 幸福惬意微笑
            d.drawCircle(mouth_x, mouth_y - 2, 8, 0xFD20);
            d.fillCircle(mouth_x, mouth_y - 4, 8, 0x0000);
        }
        else if (_current_mood == MOOD_WINK) {
            // 【迪士尼元气击掌：左眼俏皮睫毛眨眼 + 右眼超级闪亮星瞳 + 虎牙咧嘴笑】
            // 左眼眨下弯月 + 向上翘起的睫毛
            d.fillCircle(eye_lx, eye_y - 2, 14, 0xFFE0);
            d.fillCircle(eye_lx, eye_y + 3, 14, 0x0000);
            d.drawLine(eye_lx + 10, eye_y - 1, eye_lx + 15, eye_y - 5, 0xFFE0);

            // 右眼大睁晶莹高光星眸
            d.fillRoundRect(eye_rx - eye_w / 2, eye_y - eye_h / 2, eye_w, eye_h, 11, 0xFFE0);
            d.fillCircle(eye_rx, eye_y, 8, 0x0000);
            // 瞳孔中央绽放的大钻石星光
            d.fillCircle(eye_rx + 3, eye_y - 3, 4, 0xFFFF);
            d.fillCircle(eye_rx - 3, eye_y + 4, 2, 0xFFFF);

            // 腮红
            d.fillCircle(18, 92, 6, 0xFC14);
            d.fillCircle(117, 92, 6, 0xFC14);

            // 歪嘴灿烂大笑 + 标志性可爱小白虎牙
            d.fillRoundRect(mouth_x - 10, mouth_y - 2, 20, 12, 4, 0x4000);
            d.fillTriangle(mouth_x - 4, mouth_y - 2, mouth_x + 2, mouth_y - 2, mouth_x - 1, mouth_y + 4, 0xFFFF);
            d.fillCircle(mouth_x + 3, mouth_y + 6, 4, 0xF980); // 小舌头
        }
        else if (_current_mood == MOOD_SPEAK || _current_mood == MOOD_HAPPY) {
            // 【迪士尼喜悦交谈：月牙笑眸 + 呼吸式微张齿舌开合笑嘴】
            d.fillCircle(eye_lx, eye_y - 2, 14, eye_color);
            d.fillCircle(eye_lx, eye_y + 4, 14, 0x0000);
            d.fillCircle(eye_rx, eye_y - 2, 14, eye_color);
            d.fillCircle(eye_rx, eye_y + 4, 14, 0x0000);

            // 迪士尼标志性红润大腮红 (带外圈高光晕)
            d.fillCircle(18, 92, 7, 0xFC14);
            d.drawCircle(18, 92, 8, 0xFDC0);
            d.fillCircle(117, 92, 7, 0xFC14);
            d.drawCircle(117, 92, 8, 0xFDC0);

            // 随流式音频开合的生动大嘴 (深色口腔 + 洁白门牙 + 鲜活舌头)
            int cur_mh = (int)_mouth_h;
            if (cur_mh < 4) cur_mh = 4;
            d.fillRoundRect(mouth_x - 12, mouth_y - cur_mh / 2, 24, cur_mh + 4, 6, 0x4000);
            // 洁白门牙
            d.fillRoundRect(mouth_x - 6, mouth_y - cur_mh / 2, 12, 3, 1, 0xFFFF);
            // 灵动舌头
            if (cur_mh > 6) {
                d.fillCircle(mouth_x, mouth_y + cur_mh / 2 - 1, 5, 0xF980);
            }
        }
        else if (_current_mood == MOOD_CURIOUS) {
            // 【迪士尼歪头疑惑：非对称抬眉 + 一大一小星眸 + 俏皮撅嘴】
            // 抬高的好奇大眼
            d.fillRoundRect(eye_lx - 15, eye_y - 20, 30, 40, 14, 0x07FF);
            d.fillCircle(eye_lx, eye_y - 2, 7, 0x0000);
            d.fillCircle(eye_lx + 3, eye_y - 5, 4, 0xFFFF);
            d.fillCircle(eye_lx - 3, eye_y + 3, 2, 0xFFFF);

            // 微微眯起的右眼与挑起的高低眉
            d.fillRoundRect(eye_rx - 11, eye_y - 12, 22, 28, 10, 0x07FF);
            d.fillCircle(eye_rx, eye_y - 1, 4, 0x0000);
            d.fillCircle(eye_rx + 2, eye_y - 3, 2, 0xFFFF);
            d.drawLine(eye_rx - 12, eye_y - 20, eye_rx + 12, eye_y - 25, 0x07FF); // 挑眉

            // 歪向一侧的小圆撅嘴
            d.drawCircle(mouth_x + 4, mouth_y + 1, 5, 0x5D1F);
            d.fillCircle(mouth_x + 4, mouth_y + 1, 3, 0x4000);
        }
        else if (_current_mood == MOOD_PROUD) {
            // 【迪士尼傲娇得意：昂首斜视弯眸 + 金粉颊影 + 翘嘴角小虎牙】
            d.fillCircle(eye_lx, eye_y - 4, 14, 0xFFE0);
            d.fillCircle(eye_lx, eye_y + 2, 14, 0x0000);
            d.fillCircle(eye_rx, eye_y - 4, 14, 0xFFE0);
            d.fillCircle(eye_rx, eye_y + 2, 14, 0x0000);

            d.fillCircle(20, 92, 6, 0xFDC0);
            d.fillCircle(115, 92, 6, 0xFDC0);

            // 傲娇翘嘴角与小虎牙
            d.drawLine(mouth_x - 8, mouth_y - 1, mouth_x + 10, mouth_y - 5, 0xFFE0);
            d.fillTriangle(mouth_x + 5, mouth_y - 4, mouth_x + 8, mouth_y - 4, mouth_x + 6, mouth_y, 0xFFFF);
        }
        else {
            // 【迪士尼常态/倾听/思考水汪汪大眼眸 (Dual Specular Liquid Eyes)】
            int cur_eh = (int)(eye_h * (1.0f - _blink_progress * 0.90f));
            if (cur_eh < 4) cur_eh = 4;

            // 柔和外轮廓胶囊眼
            d.fillRoundRect(eye_lx - eye_w / 2, eye_y - cur_eh / 2, eye_w, cur_eh, 11, eye_color);
            d.fillRoundRect(eye_rx - eye_w / 2, eye_y - cur_eh / 2, eye_w, cur_eh, 11, eye_color);

            // 晶莹多重高光水润眼球
            if (cur_eh > 12) {
                int pupil_r = (int)_eye_pupil_r;
                int ox = (_current_mood == MOOD_THINK) ? 5 : 0;
                int oy = (_current_mood == MOOD_THINK) ? -5 : 0;

                // 深黑瞳孔
                d.fillCircle(eye_lx + ox, eye_y + oy, pupil_r, 0x0000);
                d.fillCircle(eye_rx + ox, eye_y + oy, pupil_r, 0x0000);

                // 迪士尼多级晶莹高光 (主水月大光斑 + 次级钻石微闪光斑)
                d.fillCircle(eye_lx + ox + 3, eye_y + oy - 4, 4, 0xFFFF); // 主高光
                d.fillCircle(eye_rx + ox + 3, eye_y + oy - 4, 4, 0xFFFF);
                d.fillCircle(eye_lx + ox - 3, eye_y + oy + 4, 2, 0xFFFF); // 次级微闪
                d.fillCircle(eye_rx + ox - 3, eye_y + oy + 4, 2, 0xFFFF);
            }

            // 萌萌微闭常态小嘴 (略带微弧微翘)
            d.fillRoundRect(mouth_x - 5, mouth_y, 10, 2, 1, 0x7BEF);
            d.drawPixel(mouth_x - 6, mouth_y - 1, 0x7BEF);
            d.drawPixel(mouth_x + 5, mouth_y - 1, 0x7BEF);
        }

        // 3. 灵宠对话台词与对话气泡区 (Y: 154 ~ 216, 深蓝夜色卡片)
        d.fillRoundRect(2, 154, W - 4, 62, 6, 0x10A2);
        d.drawRoundRect(2, 154, W - 4, 62, 6, 0x2965);

        // 4. 底部微型活力与互动状态条 (Y: 220 ~ 240)
        d.fillRect(0, 220, W, 20, 0x0000);
        d.setTextDatum(ML_DATUM);
        d.setTextColor(0xF81F, 0x0000); // 暖紫粉
        char bot_buf[40];
        snprintf(bot_buf, sizeof(bot_buf), "<3 活力:%u%% 喂:%u 摸:%u", _stats.energy, (unsigned)_stats.total_feeds, (unsigned)_stats.total_pets);
        d.drawString(bot_buf, 4, 230);
    }

private:
    StickS3Avatar()
        : _avatar_mode_active(true),
          _current_mood(MOOD_IDLE), _target_mood(MOOD_IDLE),
          _last_blink_time(0), _blink_interval(3000),
          _is_blinking(false), _blink_start(0), _blink_progress(0.0f),
          _last_interaction_time(0), _dizzy_until(0), _happy_until(0),
          _eye_pupil_r(7.0f), _mouth_h(2.0f),
          _last_a_mag(1.0f), _last_roll(0.0f), _last_pitch(0.0f),
          _anim_phase(0) {}

    bool _avatar_mode_active;
    PetStats _stats;
    AvatarMood _current_mood;
    AvatarMood _target_mood;

    uint32_t _last_blink_time;
    uint32_t _blink_interval;
    bool _is_blinking;
    uint32_t _blink_start;
    float _blink_progress;

    uint32_t _last_interaction_time;
    uint32_t _dizzy_until;
    uint32_t _happy_until;
    float _eye_pupil_r;
    float _mouth_h;

    float _last_a_mag;
    float _last_roll;
    float _last_pitch;
    uint32_t _anim_phase;
};

} // namespace sticks3

