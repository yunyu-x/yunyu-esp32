#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <time.h>
#include <esp_heap_caps.h>

namespace sticks3 {

struct DialogueTurn {
    uint32_t turn_id;
    uint32_t timestamp; // Unix epoch or millis
    char time_str[16];
    char user_text[128];
    char ai_text[256];
    char voice[16];
    uint16_t duration_ms;
};

class StickS3MemoryStore {
public:
    static constexpr const char* NVS_MEM_NAMESPACE = "stick_mem";
    static constexpr size_t MAX_TURNS_IN_MEMORY = 8;
    static constexpr size_t MAX_TURNS_IN_FLASH = 5;

    static StickS3MemoryStore& getInstance() {
        static StickS3MemoryStore instance;
        return instance;
    }

    bool begin() {
        Serial.println("[MEMORY] Initializing Real-time Dialogue Memory Subsystem (PSRAM-backed)...");
        if (!_turns) {
            _turns = (DialogueTurn*)ps_malloc(MAX_TURNS_IN_MEMORY * sizeof(DialogueTurn));
            if (!_turns) {
                Serial.println("[MEMORY-WARN] PSRAM alloc failed, fallback to internal heap!");
                _turns = (DialogueTurn*)malloc(MAX_TURNS_IN_MEMORY * sizeof(DialogueTurn));
            }
        }
        if (_turns) {
            memset(_turns, 0, MAX_TURNS_IN_MEMORY * sizeof(DialogueTurn));
        }
        loadFromNVS();
        Serial.printf("[MEMORY] Loaded %u dialogue turns from persistent storage.\n", (unsigned)_turn_count);
        return true;
    }

    // 安全截断 UTF-8 字符串至指定字数 (按 Unicode 字符/汉字计数，永不切断多字节，确保 100% 合法 UTF-8)
    static String safeTruncateUtf8(const char* str, size_t max_chars) {
        if (!str || *str == '\0' || max_chars == 0) return "";
        String result;
        result.reserve(max_chars * 3 + 4);
        size_t count = 0;
        const unsigned char* p = (const unsigned char*)str;
        while (*p && count < max_chars) {
            size_t char_len = 1;
            if ((*p & 0x80) == 0x00) {
                char_len = 1;
            } else if ((*p & 0xE0) == 0xC0) {
                char_len = 2;
            } else if ((*p & 0xF0) == 0xE0) {
                char_len = 3;
            } else if ((*p & 0xF8) == 0xF0) {
                char_len = 4;
            } else {
                p++;
                continue;
            }

            bool valid = true;
            for (size_t i = 1; i < char_len; ++i) {
                if (p[i] == '\0' || (p[i] & 0xC0) != 0x80) {
                    valid = false;
                    break;
                }
            }
            if (!valid) break;

            for (size_t i = 0; i < char_len; ++i) {
                result += (char)p[i];
            }
            p += char_len;
            count++;
        }
        if (*p != '\0') {
            result += "...";
        }
        return result;
    }

    // 内存超限时归纳合并最早的对话，保持记忆连贯并释放存储槽位
    void compressMemory() {
        if (_turn_count < 2 || !_turns) return;
        Serial.printf("[MEMORY] Compressing dialogue turns (current count: %u)...\n", (unsigned)_turn_count);
        
        // 将最早的 turn 0 和 1 合并为前期摘要存储在 turn 0 (安全截断避免破坏 UTF-8 编码)
        String u_short = safeTruncateUtf8(_turns[0].user_text, 14);
        String a_short = safeTruncateUtf8(_turns[0].ai_text, 18);
        char digest_ai[256];
        snprintf(digest_ai, sizeof(digest_ai), "[前期摘要] 曾讨论: %s -> %s", 
                 u_short.c_str(), a_short.c_str());
        
        _turns[0].turn_id = _turns[1].turn_id;
        strncpy(_turns[0].user_text, "前期关键历史", sizeof(_turns[0].user_text) - 1);
        _turns[0].user_text[sizeof(_turns[0].user_text) - 1] = '\0';
        strncpy(_turns[0].ai_text, digest_ai, sizeof(_turns[0].ai_text) - 1);
        _turns[0].ai_text[sizeof(_turns[0].ai_text) - 1] = '\0';

        // 剩余轮次整体前移 1 格
        if (_turn_count > 2) {
            memmove(&_turns[1], &_turns[2], sizeof(DialogueTurn) * (_turn_count - 2));
        }
        _turn_count--;
        Serial.printf("[MEMORY] Compaction complete. New turn count: %u\n", (unsigned)_turn_count);
    }

    // 追加一轮新的人机对话记忆并异步持久化至 NVS Flash (全流程 PSRAM 操作，零内部 SRAM 堆碎片)
    void addTurn(const String& user, const String& ai, const String& voice, uint16_t duration_ms = 0) {
        if (!_turns) {
            begin();
            if (!_turns) return;
        }

        String clean_user = user;
        clean_user.trim();
        String clean_ai = ai;
        clean_ai.trim();

        if (clean_user.length() == 0 || clean_ai.length() == 0) return;

        // 防止重复追加相同记录
        if (_turn_count > 0) {
            const auto& last = _turns[_turn_count - 1];
            if (strcmp(last.user_text, clean_user.c_str()) == 0 && strcmp(last.ai_text, clean_ai.c_str()) == 0) {
                return;
            }
        }

        // 维护 PSRAM 环形工作区容量
        if (_turn_count >= MAX_TURNS_IN_MEMORY) {
            compressMemory();
        }

        DialogueTurn& turn = _turns[_turn_count];
        memset(&turn, 0, sizeof(DialogueTurn));
        turn.turn_id = _next_turn_id++;
        time_t now = time(nullptr);
        turn.timestamp = (now > 1700000000) ? (uint32_t)now : millis();
        
        if (now > 1700000000) {
            struct tm timeinfo;
            localtime_r(&now, &timeinfo);
            strftime(turn.time_str, sizeof(turn.time_str), "%H:%M:%S", &timeinfo);
        } else {
            snprintf(turn.time_str, sizeof(turn.time_str), "+%lus", (unsigned long)(millis() / 1000));
        }

        strncpy(turn.user_text, clean_user.c_str(), sizeof(turn.user_text) - 1);
        turn.user_text[sizeof(turn.user_text) - 1] = '\0';
        strncpy(turn.ai_text, clean_ai.c_str(), sizeof(turn.ai_text) - 1);
        turn.ai_text[sizeof(turn.ai_text) - 1] = '\0';
        const char* v = voice.length() > 0 ? voice.c_str() : "Tina";
        strncpy(turn.voice, v, sizeof(turn.voice) - 1);
        turn.voice[sizeof(turn.voice) - 1] = '\0';
        turn.duration_ms = duration_ms;

        _turn_count++;

        Serial.printf("[MEMORY] Turn #%u recorded: User=\"%s\" | AI=\"%.30s...\" (Voice: %s)\n",
                      turn.turn_id, turn.user_text, turn.ai_text, turn.voice);

        // 持久化保存至 NVS
        saveToNVS();
    }

    // 构建注入大模型 Session Instructions 的多轮上下文记忆 (两级动态压缩，防止 Token 膨胀)
    String buildMemoryContextPrompt(const String& base_prompt) {
        if (_turn_count == 0 || !_turns) {
            return base_prompt;
        }

        String prompt;
        prompt.reserve(1600);
        prompt = base_prompt;
        if (!prompt.endsWith("\n")) prompt += "\n";
        
        prompt += "\n[历史对话上下文记忆]\n";
        
        // 两级动态压缩策略：最近 2 轮保持完整细节；更早轮次紧凑摘要 (限制在 14~18 字以内，安全 UTF-8)
        size_t recent_threshold = (_turn_count > 2) ? (_turn_count - 2) : 0;
        for (size_t i = 0; i < _turn_count; ++i) {
            const auto& t = _turns[i];
            if (i < recent_threshold) {
                // 早期历史概要化 (紧凑呈现)
                prompt += "- (历史) 用户: ";
                prompt += safeTruncateUtf8(t.user_text, 14);
                prompt += " | AI: ";
                prompt += safeTruncateUtf8(t.ai_text, 18);
                prompt += "\n";
            } else {
                // 最近 2 轮完整保留
                prompt += "- 用户: ";
                prompt += t.user_text;
                prompt += "\n- AI(";
                prompt += t.voice;
                prompt += "): ";
                prompt += t.ai_text;
                prompt += "\n";
            }
        }
        prompt += "[回答要求]\n请严格基于上述历史对话记忆进行连贯自然的问答，对于用户询问先前提到过的信息(如姓名、喜好、话题)予以准确呼应。\n";
        return prompt;
    }

    // 硬件看门狗触发的缓存清理与内存碎片整理
    void cleanupCaches() {
        uint32_t max_block = heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
        if (max_block < 35 * 1024 && _turn_count > 4) {
            Serial.printf("[MEMORY-GUARD] Low internal SRAM block (%u bytes)! Initiating proactive compaction...\n", (unsigned)max_block);
            compressMemory();
        }
    }

    // 获取序列化 JSON 格式供 Web 前端时间线展示
    String getHistoryJSON() const {
        JsonDocument doc;
        doc["total"] = _turn_count;
        doc["next_id"] = _next_turn_id;
        JsonArray arr = doc["turns"].to<JsonArray>();

        if (_turns) {
            // 倒序排列：最新的对话排在最前
            for (int i = (int)_turn_count - 1; i >= 0; --i) {
                const auto& t = _turns[i];
                JsonObject item = arr.add<JsonObject>();
                item["id"] = t.turn_id;
                item["time"] = t.time_str;
                item["user"] = t.user_text;
                item["ai"] = t.ai_text;
                item["voice"] = t.voice;
                item["duration_ms"] = t.duration_ms;
            }
        }

        String output;
        output.reserve(1024);
        serializeJson(doc, output);
        return output;
    }

    // 清空全部内存与持久化历史
    void clearMemory() {
        _turn_count = 0;
        _next_turn_id = 1;
        if (_turns) {
            memset(_turns, 0, MAX_TURNS_IN_MEMORY * sizeof(DialogueTurn));
        }
        Preferences prefs;
        if (prefs.begin(NVS_MEM_NAMESPACE, false)) {
            prefs.clear();
            prefs.end();
        }
        Serial.println("[MEMORY] All dialogue memories cleared from RAM & Flash.");
    }

    size_t getTurnCount() const { return _turn_count; }
    uint32_t getNextTurnId() const { return _next_turn_id; }

private:
    StickS3MemoryStore() : _turns(nullptr), _turn_count(0), _next_turn_id(1) {}

    void saveToNVS() {
        if (!_turns) return;
        Preferences prefs;
        if (!prefs.begin(NVS_MEM_NAMESPACE, false)) return;

        // 存储条目总数与下个ID
        size_t count_to_save = (_turn_count > MAX_TURNS_IN_FLASH) ? MAX_TURNS_IN_FLASH : _turn_count;
        prefs.putUInt("turn_count", (uint32_t)count_to_save);
        prefs.putUInt("next_id", _next_turn_id);

        // 仅持久化最近的 MAX_TURNS_IN_FLASH 轮问答
        size_t start_idx = _turn_count - count_to_save;
        for (size_t i = 0; i < count_to_save; ++i) {
            const auto& t = _turns[start_idx + i];
            String prefix = "t" + String(i) + "_";
            prefs.putUInt((prefix + "id").c_str(), t.turn_id);
            prefs.putUInt((prefix + "ts").c_str(), t.timestamp);
            prefs.putString((prefix + "tm").c_str(), t.time_str);
            prefs.putString((prefix + "u").c_str(), t.user_text);
            prefs.putString((prefix + "a").c_str(), t.ai_text);
            prefs.putString((prefix + "v").c_str(), t.voice);
            prefs.putUShort((prefix + "dur").c_str(), t.duration_ms);
        }
        prefs.end();
    }

    void loadFromNVS() {
        if (!_turns) return;
        Preferences prefs;
        if (!prefs.begin(NVS_MEM_NAMESPACE, true)) return;

        uint32_t count = prefs.getUInt("turn_count", 0);
        _next_turn_id = prefs.getUInt("next_id", 1);
        if (count == 0) {
            prefs.end();
            return;
        }

        if (count > MAX_TURNS_IN_FLASH) count = MAX_TURNS_IN_FLASH;
        _turn_count = 0;
        for (uint32_t i = 0; i < count; ++i) {
            String prefix = "t" + String(i) + "_";
            DialogueTurn& turn = _turns[_turn_count];
            memset(&turn, 0, sizeof(DialogueTurn));
            turn.turn_id = prefs.getUInt((prefix + "id").c_str(), i + 1);
            turn.timestamp = prefs.getUInt((prefix + "ts").c_str(), 0);
            String tm = prefs.getString((prefix + "tm").c_str(), "--:--");
            String u = prefs.getString((prefix + "u").c_str(), "");
            String a = prefs.getString((prefix + "a").c_str(), "");
            String v = prefs.getString((prefix + "v").c_str(), "Tina");
            turn.duration_ms = prefs.getUShort((prefix + "dur").c_str(), 0);

            strncpy(turn.time_str, tm.c_str(), sizeof(turn.time_str) - 1);
            strncpy(turn.user_text, u.c_str(), sizeof(turn.user_text) - 1);
            strncpy(turn.ai_text, a.c_str(), sizeof(turn.ai_text) - 1);
            strncpy(turn.voice, v.c_str(), sizeof(turn.voice) - 1);

            if (strlen(turn.user_text) > 0 && strlen(turn.ai_text) > 0) {
                _turn_count++;
            }
        }
        prefs.end();
    }

    DialogueTurn* _turns;
    size_t _turn_count;
    uint32_t _next_turn_id;
};

} // namespace sticks3
