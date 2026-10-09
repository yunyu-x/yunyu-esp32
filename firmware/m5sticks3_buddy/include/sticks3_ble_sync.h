#pragma once
/**
 * firmware/m5sticks3_buddy/include/sticks3_ble_sync.h
 * ---------------------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 手机端 BLE 伴侣数据同步与离线记忆转储服务
 * - Service UUID: 0000FFB0-0000-1000-8000-00805F9B34FB
 * - Characteristic 0xFFB1: Memory Sync Stream (Read / Notify)
 * - Characteristic 0xFFB2: Pet Status & Intimacy (Read / Write)
 * - Characteristic 0xFFB3: Pet Diary & Moments (Notify)
 * - Characteristic 0xFFB4: Control & Inject (Write)
 */

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>
#include "sticks3_memory_store.h"
#include "sticks3_avatar.h"
#include "sticks3_wifi_config.h"
#include "sticks3_audio.h"
#include "sticks3_bailian_client.h"
#include "sticks3_wakeword.h"
#include "sticks3_bear_kinematics.h"
#include "sticks3_cadet_bitmaps.h"

namespace sticks3 {

#define BLE_BUDDY_SERVICE_UUID        "0000FFB0-0000-1000-8000-00805F9B34FB"
#define BLE_CHAR_MEMORY_STREAM_UUID   "0000FFB1-0000-1000-8000-00805F9B34FB"
#define BLE_CHAR_PET_STATUS_UUID      "0000FFB2-0000-1000-8000-00805F9B34FB"
#define BLE_CHAR_PET_DIARY_UUID       "0000FFB3-0000-1000-8000-00805F9B34FB"
#define BLE_CHAR_CONTROL_INJECT_UUID  "0000FFB4-0000-1000-8000-00805F9B34FB"

class StickS3BLESync;

class StickS3BLEInjectCallbacks : public BLECharacteristicCallbacks {
public:
    void onWrite(BLECharacteristic* pChar) override;
};

class StickS3BLESync {
public:
    static StickS3BLESync& getInstance() {
        static StickS3BLESync instance;
        return instance;
    }

    void registerService(BLEServer* pServer) {
        if (!pServer) return;

        BLEService* pService = pServer->createService(BLE_BUDDY_SERVICE_UUID);

        // 1. 记忆同步流
        _pCharMemory = pService->createCharacteristic(
            BLE_CHAR_MEMORY_STREAM_UUID,
            BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
        );
        _pCharMemory->addDescriptor(new BLE2902());

        // 2. 灵宠状态与好感度
        _pCharStatus = pService->createCharacteristic(
            BLE_CHAR_PET_STATUS_UUID,
            BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
        );
        _pCharStatus->addDescriptor(new BLE2902());

        // 3. 灵宠观察日记
        _pCharDiary = pService->createCharacteristic(
            BLE_CHAR_PET_DIARY_UUID,
            BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
        );
        _pCharDiary->addDescriptor(new BLE2902());

        // 4. 手机控制与外部注入
        _pCharInject = pService->createCharacteristic(
            BLE_CHAR_CONTROL_INJECT_UUID,
            BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
        );
        _pCharInject->setCallbacks(new StickS3BLEInjectCallbacks());

        pService->start();
        Serial.println("[BLE-SYNC] LingBuddy Sync Service (0xFFB0) ONLINE with Bidir Control!");
    }

    // 更新特征值快照
    void updateSnapshots() {
        if (!_pCharStatus) return;

        // 1. 刷新状态特征
        const auto& stats = StickS3Avatar::getInstance().getStats();
        JsonDocument doc_status;
        doc_status["name"] = stats.pet_name;
        doc_status["level"] = stats.intimacy_level;
        doc_status["xp"] = stats.intimacy_xp;
        doc_status["energy"] = stats.energy;
        doc_status["feeds"] = stats.total_feeds;
        doc_status["grooms"] = stats.total_grooms;
        doc_status["pets"] = stats.total_pets;
        doc_status["shakes"] = stats.total_shakes;
        doc_status["mood"] = (int)StickS3Avatar::getInstance().getMood();

        // 手机共享热点状态与网络状态遥测 (精简适配 BLE MTU)
        const auto& cfg = StickS3ConfigManager::getInstance();
        doc_status["volume"] = (int)cfg.getSpeakerVolume();
        doc_status["speaker_volume"] = (int)cfg.getSpeakerVolume();
        doc_status["is_hotspot"] = cfg.isHotspot();
        doc_status["hs_used_mb"] = (float)((int)(cfg.getHotspotUsedMB() * 100)) / 100.0f;
        doc_status["hs_limit_mb"] = cfg.getHotspotLimitMB();
        doc_status["hs_cutoff"] = cfg.isHotspotCutoffActive();
        doc_status["sta_connected"] = cfg.isStaConnected();
        doc_status["sta_state"] = cfg.isStaConnected() ? "connected" : 
            (cfg.getStaState() == STA_STATE_CONNECTING ? "connecting" : 
            (cfg.getStaState() == STA_STATE_FAILED ? "failed" : "idle"));
        doc_status["sta_ip"] = cfg.getStaIP();
        doc_status["sta_ssid"] = cfg.getConfig().wifi_ssid;
        doc_status["sta_rssi"] = cfg.getStaRSSI();

        // 灵宠小熊技能树等级、经验与盛典状态
        const auto& bear_gm = BearGrowthManager::getInstance();
        doc_status["bear_level"] = bear_gm.getLevel();
        doc_status["bear_title"] = bear_gm.getLevelTitle();
        doc_status["bear_exp"] = bear_gm.getExp();
        doc_status["bear_next_exp"] = bear_gm.getNextLevelExp();
        doc_status["ceremony_active"] = bear_gm.isCeremonyActive(millis());
        doc_status["swarm_dancing"] = SwarmDanceController::getInstance().isDancing();
        doc_status["swarm_theme"] = SwarmDanceController::getInstance().getThemeName();

        String json_status;
        serializeJson(doc_status, json_status);
        _pCharStatus->setValue((uint8_t*)json_status.c_str(), json_status.length());
        _pCharStatus->notify();

        // 2. 刷新日记特征
        if (_pCharDiary && stats.current_diary.length() > 0) {
            JsonDocument doc_diary;
            doc_diary["time"] = millis() / 1000;
            doc_diary["diary"] = stats.current_diary;
            String json_diary;
            serializeJson(doc_diary, json_diary);
            _pCharDiary->setValue((uint8_t*)json_diary.c_str(), json_diary.length());
        }

        // 3. 刷新对话记忆特征 (单帧快照保证结构 100% 完整合法，全量历史通过 streamMemoryChunked 流式分片拉取)
        if (_pCharMemory) {
            String mem_json = StickS3MemoryStore::getInstance().getLatestTurnJSON();
            if (mem_json.length() > 0) {
                _pCharMemory->setValue((uint8_t*)mem_json.c_str(), mem_json.length());
            }
        }
    }

    // 分包向手机推送全量对话历史 (64字节分块流式传输)
    void streamMemoryChunked() {
        if (!_pCharMemory) return;
        String full_json = StickS3MemoryStore::getInstance().getHistoryJSON();
        if (full_json.length() == 0) return;

        const size_t CHUNK_SIZE = 48; // 保守适配 23~64 字节 MTU
        size_t total_len = full_json.length();
        size_t total_chunks = (total_len + CHUNK_SIZE - 1) / CHUNK_SIZE;

        for (size_t i = 0; i < total_chunks; i++) {
            size_t start = i * CHUNK_SIZE;
            size_t len = min(CHUNK_SIZE, total_len - start);
            String chunk = String("[C:") + String(i + 1) + "/" + String(total_chunks) + "]" + full_json.substring(start, start + len);
            _pCharMemory->setValue((uint8_t*)chunk.c_str(), chunk.length());
            _pCharMemory->notify();
            delay(15); // 微小延时保障 BLE 协议栈缓冲区不溢出
        }
        Serial.printf("[BLE-SYNC] Streamed memory in %u chunks (%u bytes)\n", (unsigned)total_chunks, (unsigned)total_len);
    }

    // 向手机客户端主动推送日记
    void notifyDiary(const String& diary_text) {
        if (_pCharDiary && diary_text.length() > 0) {
            JsonDocument doc;
            doc["time"] = millis() / 1000;
            doc["diary"] = diary_text;
            String out;
            serializeJson(doc, out);
            _pCharDiary->setValue((uint8_t*)out.c_str(), out.length());
            _pCharDiary->notify();
            Serial.printf("[BLE-SYNC] Notified Diary to Phone: %s\n", diary_text.c_str());
        }
    }

    // 解析任意 JSON 变体的布尔值 (支持 bool, int, string)
    static bool parseJsonBool(JsonVariantConst v, bool def_val = false) {
        if (v.isNull()) return def_val;
        if (v.is<bool>()) return v.as<bool>();
        if (v.is<int>()) return v.as<int>() != 0;
        if (v.is<const char*>()) {
            const char* s = v.as<const char*>();
            if (!s) return def_val;
            return (strcmp(s, "true") == 0 || strcmp(s, "1") == 0 || strcmp(s, "yes") == 0 || strcmp(s, "hotspot") == 0);
        }
        return def_val;
    }

    // 分片安全写入流累积接收器 (支持 20 字节切片半包重组与 \n 帧定界)
    void feedInjectBytes(const uint8_t* data, size_t len) {
        if (!data || len == 0) return;

        // 若前次分片超过 1200ms 未成帧，自动清空残留碎片防止死锁
        if (_inject_accum_buf.length() > 0 && millis() - _last_inject_rx_time > 1200) {
            Serial.printf("[BLE-INJECT] Buffer timeout, dropped %u bytes dangling data\n", (unsigned)_inject_accum_buf.length());
            _inject_accum_buf = "";
        }
        _last_inject_rx_time = millis();

        for (size_t i = 0; i < len; i++) {
            char c = (char)data[i];
            if (c == '\r') continue;
            if (c == '\n') {
                if (_inject_accum_buf.length() > 0) {
                    _inject_accum_buf.trim();
                    if (_inject_accum_buf.startsWith("{") && _inject_accum_buf.endsWith("}")) {
                        JsonDocument doc;
                        DeserializationError err = deserializeJson(doc, _inject_accum_buf);
                        if (!err) {
                            handleInjectDocument(doc);
                        } else {
                            Serial.printf("[BLE-INJECT] JSON line parse error: %s\n", err.c_str());
                        }
                    }
                    _inject_accum_buf = "";
                }
            } else {
                _inject_accum_buf += c;
            }
        }

        // 尝试解析：若含有完整 JSON 对象
        String candidate = _inject_accum_buf;
        candidate.trim();
        if (candidate.length() >= 2 && candidate.startsWith("{") && candidate.endsWith("}")) {
            JsonDocument doc;
            DeserializationError err = deserializeJson(doc, candidate);
            if (!err) {
                _inject_accum_buf = ""; // 成功成帧，清空累积缓冲区
                handleInjectDocument(doc);
                return;
            }
        }

        // 防止异常恶意超长分片爆内存
        if (_inject_accum_buf.length() > 2048) {
            Serial.println("[BLE-INJECT] Buffer overflow (>2048 bytes), resetting");
            _inject_accum_buf = "";
        }
    }

    // 内部处理手机回写控制指令
    void handleInjectCommand(const String& json_cmd) {
        feedInjectBytes((const uint8_t*)json_cmd.c_str(), json_cmd.length());
    }

    void handleInjectDocument(JsonDocument& doc) {
        String action = doc["action"] | "";
        if (action == "pet") {
            StickS3Avatar::getInstance().pet();
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "feed") {
            String snack = doc["snack"] | (doc["value"] | "草莓奶油大福");
            StickS3Avatar::getInstance().feed(snack);
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "groom") {
            StickS3Avatar::getInstance().groom();
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "play") {
            StickS3Avatar::getInstance().play();
            StickS3Audio::getInstance().playTone(1800, 40, 0.45f);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "shake") {
            StickS3Avatar::getInstance().shake();
            StickS3Audio::getInstance().playTone(800, 60, 0.35f);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "sleep") {
            StickS3Avatar::getInstance().sleep();
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "wake") {
            StickS3Avatar::getInstance().wake();
            StickS3Audio::getInstance().playTone(1200, 50, 0.45f);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "toggle_mode" || action == "mode") {
            StickS3Avatar::getInstance().toggleAvatarMode();
            StickS3Audio::getInstance().playTone(1500, 25, 0.40f);
        } else if (action == "set_name") {
            String new_name = doc["value"] | "悄悄";
            StickS3Avatar::getInstance().setPetName(new_name);
        } else if (action == "add_xp") {
            int xp = doc["value"] | 10;
            StickS3Avatar::getInstance().addIntimacy(xp);
        } else if (action == "set_mood") {
            String m = doc["value"] | "";
            if (m == "happy") StickS3Avatar::getInstance().setMood(MOOD_HAPPY);
            else if (m == "listen") StickS3Avatar::getInstance().setMood(MOOD_LISTEN);
            else if (m == "think") StickS3Avatar::getInstance().setMood(MOOD_THINK);
            else if (m == "sleep") StickS3Avatar::getInstance().setMood(MOOD_SLEEP);
            else if (m == "curious") StickS3Avatar::getInstance().setMood(MOOD_CURIOUS);
            else if (m == "proud") StickS3Avatar::getInstance().setMood(MOOD_PROUD);
            else if (m == "eat") StickS3Avatar::getInstance().setMood(MOOD_EAT);
            else if (m == "groom") StickS3Avatar::getInstance().setMood(MOOD_GROOM);
            else if (m == "wink") StickS3Avatar::getInstance().setMood(MOOD_WINK);
        } else if (action == "sync_memory") {
            streamMemoryChunked();
        } else if (action == "inject_memory") {
            String note = doc["value"] | "";
            if (note.length() > 0) {
                StickS3MemoryStore::getInstance().addTurn("[手机备忘] " + note, "好哒，悄悄已把这条生活备忘记在心里啦！", "Tina");
                StickS3Avatar::getInstance().generateDiaryEntry("主人从手机同步了一条新的生活备忘给我。");
                notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
            }
        } else if (action == "dance_swarm" || action == "swarm_dance") {
            String theme_str = doc["theme"] | "waltz";
            SwarmDanceTheme theme = SWARM_DANCE_WALTZ;
            if (theme_str == "zen" || theme_str == "taichi") theme = SWARM_DANCE_ZEN;
            else if (theme_str == "moonwalk") theme = SWARM_DANCE_MOONWALK;
            else if (theme_str == "cyber") theme = SWARM_DANCE_CYBER;
            SwarmDanceController::getInstance().startTheme(theme, millis());
            SwarmDanceStep step = SwarmDanceController::getInstance().getCurrentStep();
            BearKinematicsController::getInstance().triggerAction(step.buddy_action, step.duration_ms);
            StickS3Audio::getInstance().playTone(1900, 40, 0.45f);
        } else if (action == "ceremony" || action == "levelup") {
            uint8_t lvl = doc["level"] | (BearGrowthManager::getInstance().getLevel() + 1);
            if (lvl > 5) lvl = 5;
            BearGrowthManager::getInstance().setLevel(lvl);
            BearGrowthManager::getInstance().triggerCeremony(lvl, millis());
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            BearKinematicsController::getInstance().triggerAction(BEAR_ACT_CHEER, 3500);
        } else if (action == "demo_showcase" || action == "demo") {
            bool en = true;
            if (!doc["enable"].isNull()) en = parseJsonBool(doc["enable"], true);
            else if (!doc["value"].isNull()) en = parseJsonBool(doc["value"], true);
            else en = !BearKinematicsController::getInstance().isShowcaseMode();
            BearKinematicsController::getInstance().setShowcaseMode(en);
            if (en) StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            else StickS3Audio::getInstance().playTone(800, 40, 0.3f);
        } else if (action == "step_action" || action == "step") {
            BearKinematicsController::getInstance().stepShowcase();
            StickS3Audio::getInstance().playTone(1800, 25, 0.35f);
        } else if (action == "wifi_cfg") {
            String ssid = "";
            String pwd = "";
            bool is_hs = false;
            uint32_t limit_mb = 100;
            bool cutoff = true;

            // 1. 优先直接从根节点取值
            if (!doc["ssid"].isNull()) ssid = doc["ssid"].as<String>();
            if (!doc["pwd"].isNull()) pwd = doc["pwd"].as<String>();
            if (!doc["pass"].isNull()) pwd = doc["pass"].as<String>();
            if (!doc["is_hotspot"].isNull()) is_hs = parseJsonBool(doc["is_hotspot"], false);
            if (!doc["data_limit_mb"].isNull()) limit_mb = doc["data_limit_mb"].as<uint32_t>();
            if (!doc["limit_mb"].isNull()) limit_mb = doc["limit_mb"].as<uint32_t>();
            if (!doc["cutoff_enabled"].isNull()) cutoff = parseJsonBool(doc["cutoff_enabled"], true);

            // 2. 兼容嵌套在 value 字段中的 JSON 字符串或嵌套对象
            if (doc["value"].is<String>()) {
                String val_str = doc["value"].as<String>();
                if (val_str.startsWith("{")) {
                    JsonDocument sub;
                    if (!deserializeJson(sub, val_str)) {
                        if (!sub["ssid"].isNull()) ssid = sub["ssid"].as<String>();
                        if (!sub["pwd"].isNull()) pwd = sub["pwd"].as<String>();
                        if (!sub["pass"].isNull()) pwd = sub["pass"].as<String>();
                        if (!sub["is_hotspot"].isNull()) is_hs = parseJsonBool(sub["is_hotspot"], is_hs);
                        if (!sub["data_limit_mb"].isNull()) limit_mb = sub["data_limit_mb"].as<uint32_t>();
                        if (!sub["limit_mb"].isNull()) limit_mb = sub["limit_mb"].as<uint32_t>();
                        if (!sub["cutoff_enabled"].isNull()) cutoff = parseJsonBool(sub["cutoff_enabled"], cutoff);
                    }
                }
            } else if (doc["value"].is<JsonObjectConst>()) {
                JsonObjectConst sub = doc["value"].as<JsonObjectConst>();
                if (!sub["ssid"].isNull()) ssid = sub["ssid"].as<String>();
                if (!sub["pwd"].isNull()) pwd = sub["pwd"].as<String>();
                if (!sub["pass"].isNull()) pwd = sub["pass"].as<String>();
                if (!sub["is_hotspot"].isNull()) is_hs = parseJsonBool(sub["is_hotspot"], is_hs);
                if (!sub["data_limit_mb"].isNull()) limit_mb = sub["data_limit_mb"].as<uint32_t>();
                if (!sub["limit_mb"].isNull()) limit_mb = sub["limit_mb"].as<uint32_t>();
                if (!sub["cutoff_enabled"].isNull()) cutoff = parseJsonBool(sub["cutoff_enabled"], cutoff);
            }

            Serial.printf("[BLE-INJECT] wifi_cfg received: SSID='%s', is_hotspot=%s, limit=%uMB, cutoff=%s\n",
                          ssid.c_str(), is_hs ? "YES (HOT)" : "NO (WIFI)", (unsigned)limit_mb, cutoff ? "YES" : "NO");

            if (ssid.length() > 0) {
                auto& cfg_mgr = StickS3ConfigManager::getInstance();
                cfg_mgr.saveWiFiConfig(ssid, pwd);
                cfg_mgr.saveHotspotConfig(is_hs, limit_mb, cutoff);
                cfg_mgr.startConnectSTA(ssid, pwd);

                String diary_msg = String("主人通过蓝牙配网连接了 ") + (is_hs ? "手机移动热点[" : "Wi-Fi网络[") + ssid + "]";
                if (is_hs && limit_mb > 0) {
                    diary_msg += "，并设置了 " + String(limit_mb) + "MB 流量保护上限！";
                }
                StickS3Avatar::getInstance().generateDiaryEntry(diary_msg);
                notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
            }
        } else if (action == "hotspot_cfg" || action == "set_traffic_limit") {
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            bool is_hs = cfg_mgr.isHotspot();
            uint32_t limit_mb = cfg_mgr.getHotspotLimitMB();
            bool cutoff = cfg_mgr.isHotspotCutoffEnabled();

            if (!doc["is_hotspot"].isNull()) is_hs = parseJsonBool(doc["is_hotspot"], is_hs);
            if (!doc["data_limit_mb"].isNull()) limit_mb = doc["data_limit_mb"].as<uint32_t>();
            else if (!doc["limit_mb"].isNull()) limit_mb = doc["limit_mb"].as<uint32_t>();
            else if (doc["value"].is<int>()) limit_mb = doc["value"].as<uint32_t>();
            if (!doc["cutoff_enabled"].isNull()) cutoff = parseJsonBool(doc["cutoff_enabled"], true);

            // 兼容嵌套 value
            if (doc["value"].is<String>()) {
                String val_str = doc["value"].as<String>();
                if (val_str.startsWith("{")) {
                    JsonDocument sub;
                    if (!deserializeJson(sub, val_str)) {
                        if (!sub["is_hotspot"].isNull()) is_hs = parseJsonBool(sub["is_hotspot"], is_hs);
                        if (!sub["data_limit_mb"].isNull()) limit_mb = sub["data_limit_mb"].as<uint32_t>();
                        if (!sub["limit_mb"].isNull()) limit_mb = sub["limit_mb"].as<uint32_t>();
                        if (!sub["cutoff_enabled"].isNull()) cutoff = parseJsonBool(sub["cutoff_enabled"], cutoff);
                    }
                }
            } else if (doc["value"].is<JsonObjectConst>()) {
                JsonObjectConst sub = doc["value"].as<JsonObjectConst>();
                if (!sub["is_hotspot"].isNull()) is_hs = parseJsonBool(sub["is_hotspot"], is_hs);
                if (!sub["data_limit_mb"].isNull()) limit_mb = sub["data_limit_mb"].as<uint32_t>();
                if (!sub["limit_mb"].isNull()) limit_mb = sub["limit_mb"].as<uint32_t>();
                if (!sub["cutoff_enabled"].isNull()) cutoff = parseJsonBool(sub["cutoff_enabled"], cutoff);
            }

            StickS3ConfigManager::getInstance().saveHotspotConfig(is_hs, limit_mb, cutoff);
            Serial.printf("[BLE-INJECT] hotspot_cfg applied: is_hotspot=%s, limit=%uMB, cutoff=%s\n",
                          is_hs ? "YES (HOT)" : "NO (WIFI)", (unsigned)limit_mb, cutoff ? "YES" : "NO");

            String msg = is_hs 
                ? ("已切换为手机热点模式：上限 " + String(limit_mb) + "MB，自动熔断 " + (cutoff ? "开启" : "关闭"))
                : "已切换为常规Wi-Fi宽带模式。";
            StickS3Avatar::getInstance().generateDiaryEntry(msg);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "reset_traffic") {
            StickS3ConfigManager::getInstance().resetHotspotTraffic();
            StickS3Avatar::getInstance().generateDiaryEntry("手机热点流量统计已重置为 0 MB。");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "volume" || action == "set_volume") {
            int vol = -1;
            if (!doc["volume"].isNull()) vol = doc["volume"].as<int>();
            else if (!doc["value"].isNull()) {
                if (doc["value"].is<int>()) vol = doc["value"].as<int>();
                else if (doc["value"].is<String>()) vol = doc["value"].as<String>().toInt();
            }
            if (vol >= 0 && vol <= 100) {
                StickS3ConfigManager::getInstance().saveSpeakerVolume((uint8_t)vol);
                StickS3Audio::getInstance().playTone(1200, 70, 0.50f);
                updateSnapshots();
                Serial.printf("[BLE-INJECT] Volume adjusted to %d%% via BLE.\n", vol);
            }
        } else if (action == "test_volume") {
            if (doc["volume"].is<int>()) {
                int vol = doc["volume"].as<int>();
                if (vol >= 0 && vol <= 100) {
                    StickS3ConfigManager::getInstance().saveSpeakerVolume((uint8_t)vol);
                }
            }
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            updateSnapshots();
            Serial.println("[BLE-INJECT] Volume test chime played via BLE.");
        } else if (action == "clear_memory") {
            StickS3BailianClient::getInstance().clearMemory();
            StickS3Audio::getInstance().playTone(1500, 50, 0.4f);
            StickS3Avatar::getInstance().generateDiaryEntry("主人清空了全部历史对话记忆。");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
            Serial.println("[BLE-INJECT] Conversation memory cleared via BLE.");
        } else if (action == "reboot") {
            StickS3Audio::getInstance().playTone(1200, 60, 0.4f);
            Serial.println("[BLE-INJECT] Reboot triggered via BLE! Rebooting in 300ms...");
            delay(300);
            esp_restart();
        } else if (action == "factory_reset") {
            StickS3Audio::getInstance().playTone(1000, 100, 0.5f);
            StickS3ConfigManager::getInstance().clearAllConfig();
            StickS3MemoryStore::getInstance().clearMemory();
            Serial.println("[BLE-INJECT] Factory reset triggered via BLE! Rebooting in 400ms...");
            delay(400);
            esp_restart();
        } else if (action == "bailian_cfg") {
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            auto& bl = StickS3BailianClient::getInstance();
            String key = "";
            String model = "";
            String voice = "";
            String prompt = "";

            if (!doc["key"].isNull()) key = doc["key"].as<String>();
            if (!doc["api_key"].isNull()) key = doc["api_key"].as<String>();
            if (!doc["model"].isNull()) model = doc["model"].as<String>();
            if (!doc["voice"].isNull()) voice = doc["voice"].as<String>();
            if (!doc["prompt"].isNull()) prompt = doc["prompt"].as<String>();
            int vol = -1;
            if (!doc["volume"].isNull()) vol = doc["volume"].as<int>();
            else if (!doc["speaker_volume"].isNull()) vol = doc["speaker_volume"].as<int>();

            // 兼容 value 嵌套对象
            if (doc["value"].is<JsonObjectConst>()) {
                JsonObjectConst sub = doc["value"].as<JsonObjectConst>();
                if (!sub["key"].isNull()) key = sub["key"].as<String>();
                if (!sub["api_key"].isNull()) key = sub["api_key"].as<String>();
                if (!sub["model"].isNull()) model = sub["model"].as<String>();
                if (!sub["voice"].isNull()) voice = sub["voice"].as<String>();
                if (!sub["prompt"].isNull()) prompt = sub["prompt"].as<String>();
                if (!sub["volume"].isNull()) vol = sub["volume"].as<int>();
                else if (!sub["speaker_volume"].isNull()) vol = sub["speaker_volume"].as<int>();
            }

            if (vol >= 10 && vol <= 100) {
                cfg_mgr.saveSpeakerVolume((uint8_t)vol);
                updateSnapshots();
                Serial.printf("[BLE-INJECT] Volume adjusted via bailian_cfg to %d%%\n", vol);
            }

            if (key.length() == 0) {
                key = cfg_mgr.getConfig().bailian_key;
            }
            if (model.length() == 0) {
                model = cfg_mgr.getConfig().bailian_model;
            }
            if (voice.length() == 0) {
                voice = cfg_mgr.getConfig().bailian_voice;
            }

            bool need_reconnect = false;
            if (key.length() > 0 && key != cfg_mgr.getConfig().bailian_key) need_reconnect = true;
            if (model.length() > 0 && model != cfg_mgr.getConfig().bailian_model) need_reconnect = true;

            cfg_mgr.saveBailianConfig(key, model, voice, "", prompt);
            if (need_reconnect || !bl.isConnected()) {
                if (cfg_mgr.isStaConnected() && cfg_mgr.hasBailianKey()) {
                    bl.connect();
                }
            } else if (bl.isConnected()) {
                bl.switchVoice(voice, false);
            }
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            StickS3Avatar::getInstance().generateDiaryEntry(String("主人通过蓝牙更新了阿里云百炼配置：模型[") + model + "]，音色[" + voice + "]。");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
            Serial.printf("[BLE-INJECT] bailian_cfg applied: model='%s', voice='%s'\n", model.c_str(), voice.c_str());
        } else if (action == "preview_voice") {
            String voice = doc["voice"] | (doc["value"] | "");
            if (voice.length() > 0 && StickS3ConfigManager::isVoiceSupported(voice)) {
                StickS3BailianClient::getInstance().switchVoice(voice, true);
                Serial.printf("[BLE-INJECT] preview_voice triggered: %s\n", voice.c_str());
            }
        } else if (action == "wakeword_cfg") {
            auto& ww = StickS3WakeWordEngine::getInstance();
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            auto& cfg = cfg_mgr.getConfig();

            bool enabled = cfg.wakeword_enabled;
            if (!doc["enabled"].isNull()) enabled = parseJsonBool(doc["enabled"], enabled);
            uint8_t sens = cfg.wakeword_sensitivity;
            if (!doc["sensitivity"].isNull()) sens = (uint8_t)doc["sensitivity"].as<int>();
            uint16_t tout = cfg.wakeword_timeout_sec;
            if (!doc["timeout_sec"].isNull()) tout = (uint16_t)doc["timeout_sec"].as<int>();

            // 兼容 value 嵌套对象
            if (doc["value"].is<JsonObjectConst>()) {
                JsonObjectConst sub = doc["value"].as<JsonObjectConst>();
                if (!sub["enabled"].isNull()) enabled = parseJsonBool(sub["enabled"], enabled);
                if (!sub["sensitivity"].isNull()) sens = (uint8_t)sub["sensitivity"].as<int>();
                if (!sub["timeout_sec"].isNull()) tout = (uint16_t)sub["timeout_sec"].as<int>();
            }

            ww.setEnabled(enabled);
            ww.setSensitivity(sens);
            cfg_mgr.saveWakeWordConfig(enabled, sens, tout);
            StickS3Audio::getInstance().playTone(1600, 40, 0.4f);
            StickS3Avatar::getInstance().generateDiaryEntry(String("主人通过蓝牙配置了离线唤醒词：") + (enabled ? "开启" : "关闭") + "，灵敏度 " + String(sens) + "%");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
            Serial.printf("[BLE-INJECT] wakeword_cfg applied: enabled=%d, sens=%d, tout=%d\n", enabled, sens, tout);
        } else if (action == "trigger_wake") {
            float conf = 98.0f;
            if (!doc["confidence"].isNull()) conf = doc["confidence"].as<float>();
            StickS3WakeWordEngine::getInstance().forceTrigger(conf);
            StickS3BailianClient::getInstance().onWakeWordDetected(conf, 650);
            Serial.println("[BLE-INJECT] Wake simulated via BLE.");
        } else if (action == "bear_balance" || action == "balance" || action == "imu_balance") {
            bool en = true;
            if (!doc["enabled"].isNull()) en = parseJsonBool(doc["enabled"], true);
            else if (!doc["value"].isNull()) en = parseJsonBool(doc["value"], true);
            BearKinematicsController::getInstance().setImuBalanceEnabled(en);
            Serial.printf("[BLE-INJECT] Bear IMU Balance set to %s\n", en ? "ON" : "OFF");
        } else if (action == "bear_yaw" || action == "yaw") {
            float y_val = 0.0f;
            if (!doc["yaw"].isNull()) y_val = doc["yaw"].as<float>();
            else if (!doc["value"].isNull()) y_val = doc["value"].as<float>();
            BearKinematicsController::getInstance().setTargetYaw(y_val);
            Serial.printf("[BLE-INJECT] Bear Yaw set to %.1f deg\n", y_val);
        } else if (action == "bear_turn" || action == "turn") {
            float deg = 180.0f;
            if (!doc["deg"].isNull()) deg = doc["deg"].as<float>();
            else if (!doc["value"].isNull()) deg = doc["value"].as<float>();
            if (deg >= 300.0f) {
                BearKinematicsController::getInstance().triggerSpinPirouette(1800);
            } else {
                BearKinematicsController::getInstance().triggerTurnAround(1400);
            }
            Serial.printf("[BLE-INJECT] Bear Turn triggered (%.0f deg)\n", deg);
        } else if (action == "bear_spin" || action == "spin") {
            BearKinematicsController::getInstance().triggerSpinPirouette(1800);
            Serial.println("[BLE-INJECT] Bear Spin triggered");
        } else if (action == "bear_joint" || action == "joint") {
            uint8_t j_id = doc["id"] | (doc["joint_id"] | 0);
            float j_ang = doc["angle"] | (doc["val"] | (doc["value"] | 0.0f));
            BearKinematicsController::getInstance().setJointAngle(j_id, j_ang, 0.0f, 0.0f);
            Serial.printf("[BLE-INJECT] Bear Joint #%u angle set to %.1f deg\n", (unsigned)j_id, j_ang);
        } else if (action == "bear_joint_clear" || action == "joint_clear" || action == "joints_reset") {
            BearKinematicsController::getInstance().clearJointOverrides();
            Serial.println("[BLE-INJECT] Bear Joint overrides cleared");
        } else if (action == "bear_act" || action == "act") {
            String act_str = doc["act"] | (doc["action"] | "wave");
            uint32_t dur = doc["duration"] | 2800;
            BearAction act = stringToBearAction(act_str.c_str());
            BearKinematicsController::getInstance().triggerAction(act, dur);
            StickS3Audio::getInstance().playTone(1700, 30, 0.40f);
            Serial.printf("[BLE-INJECT] Bear Action triggered: %s (duration %u ms)\n", act_str.c_str(), (unsigned)dur);
        } else if (action == "bear_combo" || action == "combo") {
            String c_name = doc["combo"] | "martial";
            BearKinematicsController::getInstance().triggerComboByName(c_name.c_str());
            StickS3Audio::getInstance().playTone(1800, 40, 0.45f);
            Serial.printf("[BLE-INJECT] Bear Combo triggered: %s\n", c_name.c_str());
        } else if (action == "cadet_mode" || action == "set_cadet_mode") {
            String m_val = doc["mode"] | (doc["value"] | "toggle");
            m_val.toLowerCase();
            if (m_val == "lineart" || m_val == "line_art" || m_val == "0") {
                setCadetRenderMode(CADET_MODE_LINEART);
            } else if (m_val == "fullcolor" || m_val == "full_color" || m_val == "1") {
                setCadetRenderMode(CADET_MODE_FULLCOLOR);
            } else {
                toggleCadetRenderMode();
            }
            Preferences p;
            if (p.begin("sticks3_cfg", false)) {
                p.putUChar("cadet_mode", (uint8_t)getCadetRenderMode());
                p.end();
            }
            StickS3Audio::getInstance().playTone(1900, 35, 0.40f);
            Serial.printf("[BLE-INJECT] Cadet Render Mode switched to: %s\n",
                          getCadetRenderMode() == CADET_MODE_FULLCOLOR ? "Full-Color" : "Line-Art");
        } else if (action == "query_wifi_status" || action == "get_status") {
            // 立即刷新并推送特征值
            updateSnapshots();
        }
        Serial.printf("[BLE-INJECT] Processed action: %s\n", action.c_str());
        updateSnapshots();
    }

    // 由 BLE 中断任务 (BTC_TASK) 调用：极速存入队列，栈消耗 < 32 字节，杜绝 BTC_TASK 栈溢出
    void queueIncomingBytes(const uint8_t* data, size_t len) {
        if (!data || len == 0) return;
        portENTER_CRITICAL(&_rx_mux);
        if (_rx_queue.size() + len <= 2048) {
            _rx_queue.insert(_rx_queue.end(), data, data + len);
            _rx_pending = true;
        }
        portEXIT_CRITICAL(&_rx_mux);
    }

    // 由 Arduino 主循环 loop() (Core 1, loopTask, 16KB 栈) 周期性调用：安全重组分片并执行
    void update() {
        if (!_rx_pending) return;

        std::vector<uint8_t> batch;
        portENTER_CRITICAL(&_rx_mux);
        if (!_rx_queue.empty()) {
            batch.swap(_rx_queue);
        }
        _rx_pending = false;
        portEXIT_CRITICAL(&_rx_mux);

        if (!batch.empty()) {
            feedInjectBytes(batch.data(), batch.size());
        }
    }

private:
    StickS3BLESync()
        : _pCharMemory(nullptr), _pCharStatus(nullptr),
          _pCharDiary(nullptr), _pCharInject(nullptr),
          _inject_accum_buf(""), _last_inject_rx_time(0),
          _rx_pending(false) {
        portMUX_INITIALIZE(&_rx_mux);
    }

    BLECharacteristic* _pCharMemory;
    BLECharacteristic* _pCharStatus;
    BLECharacteristic* _pCharDiary;
    BLECharacteristic* _pCharInject;
    String _inject_accum_buf;
    uint32_t _last_inject_rx_time;
    portMUX_TYPE _rx_mux;
    std::vector<uint8_t> _rx_queue;
    volatile bool _rx_pending;
};

inline void StickS3BLEInjectCallbacks::onWrite(BLECharacteristic* pChar) {
    if (!pChar) return;
    std::string val = pChar->getValue();
    if (!val.empty()) {
        StickS3BLESync::getInstance().queueIncomingBytes((const uint8_t*)val.data(), val.length());
    }
}

} // namespace sticks3
