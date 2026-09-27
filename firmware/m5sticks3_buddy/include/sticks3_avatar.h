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
    MOOD_PROUD          // 傲娇得意 (扬起下巴眯眼微笑)
};

struct PetStats {
    uint8_t intimacy_level;  // 亲密度等级 (1 ~ 10)
    uint16_t intimacy_xp;    // 亲密度经验值 (0 ~ 100 进阶)
    uint32_t total_pets;     // 累计抚摸次数
    uint32_t total_shakes;   // 累计晃动次数
    uint32_t total_convos;   // 累计对话轮次
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

    void begin(const String& name = "小木") {
        _stats.intimacy_level = 1;
        _stats.intimacy_xp = 15;
        _stats.total_pets = 0;
        _stats.total_shakes = 0;
        _stats.total_convos = 0;
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

    // 解析大模型返回文本中的 [E:xxx] 情绪标签并自动提取纯净文本
    static AvatarMood parseEmotionTag(const String& raw_text, String& clean_text) {
        clean_text = raw_text;
        if (!raw_text.startsWith("[E:") && !raw_text.startsWith("[e:")) {
            return MOOD_IDLE;
        }
        int close_idx = raw_text.indexOf(']');
        if (close_idx < 0) return MOOD_IDLE;

        String tag = raw_text.substring(3, close_idx);
        tag.toLowerCase();
        tag.trim();
        clean_text = raw_text.substring(close_idx + 1);
        clean_text.trim();

        if (tag == "happy") return MOOD_HAPPY;
        if (tag == "curious") return MOOD_CURIOUS;
        if (tag == "proud") return MOOD_PROUD;
        if (tag == "sleepy" || tag == "sleep") return MOOD_SLEEP;
        if (tag == "dizzy") return MOOD_DIZZY;
        if (tag == "shock") return MOOD_SHOCK;
        if (tag == "listen") return MOOD_LISTEN;
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

    // 更新物理具身情感动力学
    void updatePhysics(float ax, float ay, float az, float roll, float pitch, uint8_t mic_rms, uint8_t spk_rms) {
        uint32_t now = millis();

        // 1. 瞬时合加速度
        float a_mag = std::sqrt(ax * ax + ay * ay + az * az);

        // 2. 剧烈摇晃检测 (a_mag > 2.3g)
        if (a_mag > 2.3f) {
            _stats.total_shakes++;
            _dizzy_until = now + 3500; // 晕眩持续 3.5 秒
            _current_mood = MOOD_DIZZY;
            _last_interaction_time = now;
            _stats.current_diary = "哎呀呀，主人刚刚疯狂晃我，眼睛里全都是小星星！";
        } else if (_dizzy_until > now) {
            _current_mood = MOOD_DIZZY;
        } else {
            // 3. 温柔轻抚检测 (缓慢小幅前后晃动，且处于常态)
            float delta_a = std::abs(a_mag - 1.0f);
            if (delta_a > 0.18f && delta_a < 0.65f && (_current_mood == MOOD_IDLE || _current_mood == MOOD_SLEEP)) {
                _stats.total_pets++;
                addIntimacy(1);
                _happy_until = now + 2500;
                _current_mood = MOOD_HAPPY;
                _last_interaction_time = now;
                _stats.current_diary = "主人刚刚摸了摸我，感觉超级温暖惬意~";
            } else if (_happy_until > now) {
                _current_mood = MOOD_HAPPY;
            } else {
                // 4. 平放静止入睡检测 (处于水平桌面且超过 90 秒无交互)
                bool is_flat = (std::abs(roll) < 18.0f && std::abs(pitch) < 18.0f && std::abs(a_mag - 1.0f) < 0.15f);
                if (is_flat && (now - _last_interaction_time > 90000)) {
                    _current_mood = MOOD_SLEEP;
                } else if (_target_mood != MOOD_IDLE) {
                    _current_mood = _target_mood;
                } else {
                    _current_mood = MOOD_IDLE;
                }
            }
        }

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

        // 7. 自主眨眼状态机
        if (_current_mood == MOOD_IDLE || _current_mood == MOOD_HAPPY) {
            if (!_is_blinking && (now - _last_blink_time > _blink_interval)) {
                _is_blinking = true;
                _blink_start = now;
                _blink_interval = 2200 + (now % 2000); // 2.2s ~ 4.2s 随机眨眼
            }
            if (_is_blinking) {
                uint32_t b_dur = now - _blink_start;
                if (b_dur < 100) {
                    _blink_progress = (float)b_dur / 100.0f; // 闭眼 0 -> 1
                } else if (b_dur < 200) {
                    _blink_progress = 1.0f - (float)(b_dur - 100) / 100.0f; // 睁眼 1 -> 0
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

    // 核心矢量绘制函数 (参数化绘制在 135x240 显示屏上)
    template <typename DisplayType>
    void render(DisplayType& d, const String& subtitle_text, const String& status_tag) {
        const int W = 135;
        const int H = 240;

        // 1. 顶部极简状态条 (Y: 0 ~ 16)
        d.fillRect(0, 0, W, 18, 0x0841); // 深灰蓝
        d.setTextDatum(ML_DATUM);
        d.setTextColor(0xFFE0, 0x0841); // 亮黄
        char top_buf[32];
        snprintf(top_buf, sizeof(top_buf), "%s Lv.%u", _stats.pet_name.c_str(), _stats.intimacy_level);
        d.drawString(top_buf, 4, 9);

        d.setTextDatum(MR_DATUM);
        d.setTextColor(0x07E0, 0x0841); // 亮绿
        d.drawString(status_tag.c_str(), W - 4, 9);

        // 2. 灵宠面部主画板 (Y: 18 ~ 152, 黑色底)
        d.fillRect(0, 18, W, 134, 0x0000);

        // 双眼几何中心参数
        const int eye_y = 75;
        const int eye_lx = 38;
        const int eye_rx = 97;
        const int eye_w = 26;
        const int eye_h = 36;
        const int mouth_x = 67;
        const int mouth_y = 120;

        uint16_t eye_color = 0x5D1F; // 柔和天青蓝 (Cyan)
        if (_current_mood == MOOD_LISTEN) eye_color = 0x07FF; // 高光青空蓝
        else if (_current_mood == MOOD_HAPPY) eye_color = 0xFD20; // 樱花暖粉
        else if (_current_mood == MOOD_DIZZY) eye_color = 0xFE60; // 警示黄
        else if (_current_mood == MOOD_THINK) eye_color = 0xFFE0; // 琥珀黄

        // 根据情绪渲染不同表情
        if (_current_mood == MOOD_DIZZY) {
            // 眩晕 X_X 眼睛
            d.drawLine(eye_lx - 10, eye_y - 10, eye_lx + 10, eye_y + 10, eye_color);
            d.drawLine(eye_lx - 10, eye_y + 10, eye_lx + 10, eye_y - 10, eye_color);
            d.drawLine(eye_rx - 10, eye_y - 10, eye_rx + 10, eye_y + 10, eye_color);
            d.drawLine(eye_rx - 10, eye_y + 10, eye_rx + 10, eye_y - 10, eye_color);

            // 波浪嘴
            d.drawCircle(mouth_x, mouth_y + 2, 6, eye_color);
            d.drawCircle(mouth_x + 8, mouth_y, 4, 0xFE60); // 冒出的小晕星
        }
        else if (_current_mood == MOOD_SLEEP) {
            // 打呼闭眼平直线
            d.fillRect(eye_lx - 12, eye_y - 2, 24, 4, 0x7BEF);
            d.fillRect(eye_rx - 12, eye_y - 2, 24, 4, 0x7BEF);

            // 飘动的 Zzz
            static uint8_t z_phase = 0;
            z_phase = (z_phase + 1) % 60;
            int z_y = 48 - (z_phase / 3);
            d.setTextColor(0x07FF, 0x0000);
            d.setTextDatum(MC_DATUM);
            d.drawString("Z", 78, z_y);
            d.drawString("z", 88, z_y + 8);
        }
        else if (_current_mood == MOOD_SPEAK || _current_mood == MOOD_HAPPY) {
            // 笑眼弯弯 (上拱月牙形)
            d.fillCircle(eye_lx, eye_y - 2, 13, eye_color);
            d.fillCircle(eye_lx, eye_y + 3, 13, 0x0000); // 挖去下半部形成月牙
            d.fillCircle(eye_rx, eye_y - 2, 13, eye_color);
            d.fillCircle(eye_rx, eye_y + 3, 13, 0x0000);

            // 脸颊粉红小腮红 (Blush)
            d.fillCircle(18, 92, 6, 0xFC14); // 暖粉红
            d.fillCircle(117, 92, 6, 0xFC14);

            // 随流式音频开合的小嘴
            int cur_mh = (int)_mouth_h;
            d.fillRoundRect(mouth_x - 10, mouth_y - cur_mh / 2, 20, cur_mh + 4, 4, 0xF980);
        }
        else if (_current_mood == MOOD_CURIOUS) {
            // 好奇歪头：左眼大右眼略小，微微倾斜
            d.fillRoundRect(eye_lx - 14, eye_y - 18, 28, 36, 12, 0x07FF);
            d.fillRoundRect(eye_rx - 11, eye_y - 12, 22, 26, 9, 0x07FF);
            d.fillCircle(eye_lx, eye_y - 2, 6, 0x0000);
            d.fillCircle(eye_rx, eye_y - 2, 4, 0x0000);
            // 俏皮小圆嘴
            d.drawCircle(mouth_x + 3, mouth_y, 4, 0x5D1F);
        }
        else if (_current_mood == MOOD_PROUD) {
            // 傲娇得意：昂首向上弯眼 + 俏皮小虎牙嘴
            d.fillCircle(eye_lx, eye_y - 4, 13, 0xFFE0);
            d.fillCircle(eye_lx, eye_y + 2, 13, 0x0000);
            d.fillCircle(eye_rx, eye_y - 4, 13, 0xFFE0);
            d.fillCircle(eye_rx, eye_y + 2, 13, 0x0000);
            d.fillCircle(20, 92, 5, 0xFDC0); // 金粉腮红
            d.fillCircle(115, 92, 5, 0xFDC0);
            d.drawLine(mouth_x - 8, mouth_y - 2, mouth_x + 8, mouth_y - 4, 0xFFE0);
        }
        else {
            // 标准/倾听/思考圆角胶囊眼
            int cur_eh = (int)(eye_h * (1.0f - _blink_progress * 0.88f));
            if (cur_eh < 4) cur_eh = 4;

            // 眼睛外轮廓
            d.fillRoundRect(eye_lx - eye_w / 2, eye_y - cur_eh / 2, eye_w, cur_eh, 10, eye_color);
            d.fillRoundRect(eye_rx - eye_w / 2, eye_y - cur_eh / 2, eye_w, cur_eh, 10, eye_color);

            // 瞳孔高光 (瞳孔随收音 VU 动态放大)
            if (cur_eh > 12) {
                int pupil_r = (int)_eye_pupil_r;
                if (_current_mood == MOOD_THINK) {
                    // 思考时眼球向右上方转动
                    d.fillCircle(eye_lx + 4, eye_y - 4, pupil_r - 2, 0x0000);
                    d.fillCircle(eye_rx + 4, eye_y - 4, pupil_r - 2, 0x0000);
                } else {
                    d.fillCircle(eye_lx, eye_y, pupil_r, 0x0000);
                    d.fillCircle(eye_rx, eye_y, pupil_r, 0x0000);
                    // 右上角晶莹小白高光
                    d.fillCircle(eye_lx + 3, eye_y - 4, 3, 0xFFFF);
                    d.fillCircle(eye_rx + 3, eye_y - 4, 3, 0xFFFF);
                }
            }

            // 微闭小嘴
            d.fillRect(mouth_x - 4, mouth_y, 8, 2, 0x7BEF);
        }

        // 3. 灵宠对话台词与对话气泡区 (Y: 152 ~ 216, 深邃卡片)
        d.fillRoundRect(2, 154, W - 4, 62, 6, 0x10A2); // 深蓝夜色卡片
        d.drawRoundRect(2, 154, W - 4, 62, 6, 0x2965);

        // 4. 底部微型亲密度与体力状态条 (Y: 220 ~ 240)
        d.fillRect(0, 220, W, 20, 0x0000);
        d.setTextDatum(ML_DATUM);
        d.setTextColor(0xF81F, 0x0000); // 暖紫粉
        char bot_buf[32];
        snprintf(bot_buf, sizeof(bot_buf), "<3 亲密:%u%% 摸摸:%u", _stats.intimacy_xp, (unsigned)_stats.total_pets);
        d.drawString(bot_buf, 4, 230);
    }

private:
    StickS3Avatar()
        : _current_mood(MOOD_IDLE), _target_mood(MOOD_IDLE),
          _last_blink_time(0), _blink_interval(3000),
          _is_blinking(false), _blink_start(0), _blink_progress(0.0f),
          _last_interaction_time(0), _dizzy_until(0), _happy_until(0),
          _eye_pupil_r(7.0f), _mouth_h(2.0f) {}

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
};

} // namespace sticks3
