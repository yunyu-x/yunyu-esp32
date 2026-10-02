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
            BLECharacteristic::PROPERTY_WRITE
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
        doc_status["mood"] = (int)StickS3Avatar::getInstance().getMood();

        // 手机共享热点状态与网络状态遥测 (精简适配 BLE MTU)
        const auto& cfg = StickS3ConfigManager::getInstance();
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

        // 3. 刷新对话记忆特征
        if (_pCharMemory) {
            String mem_json = StickS3MemoryStore::getInstance().getHistoryJSON();
            if (mem_json.length() > 0) {
                String safe_mem = StickS3MemoryStore::safeTruncateUtf8(mem_json.c_str(), 120);
                _pCharMemory->setValue((uint8_t*)safe_mem.c_str(), safe_mem.length());
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

    // 内部处理手机回写控制指令
    void handleInjectCommand(const String& json_cmd) {
        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, json_cmd);
        if (err) {
            Serial.printf("[BLE-INJECT] Parse error: %s\n", err.c_str());
            return;
        }
        String action = doc["action"] | "";
        if (action == "pet") {
            StickS3Avatar::getInstance().setMood(MOOD_HAPPY);
            StickS3Avatar::getInstance().addIntimacy(3);
            StickS3Avatar::getInstance().generateDiaryEntry("手机端主人刚刚隔空摸了摸我的小脑瓜，好幸福！");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "feed") {
            String snack = doc["snack"] | (doc["value"] | "香甜小蛋糕");
            StickS3Avatar::getInstance().feed(snack);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "groom") {
            StickS3Avatar::getInstance().groom();
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "play") {
            StickS3Avatar::getInstance().play();
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "shake") {
            StickS3Avatar::getInstance().setMood(MOOD_DIZZY);
            StickS3Avatar::getInstance().generateDiaryEntry("手机端发来摇晃指令，眼睛里全都是小星星！");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "sleep") {
            StickS3Avatar::getInstance().setMood(MOOD_SLEEP);
        } else if (action == "wake") {
            StickS3Avatar::getInstance().setMood(MOOD_LISTEN);
        } else if (action == "set_name") {
            String new_name = doc["value"] | "小木";
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
                StickS3MemoryStore::getInstance().addTurn("[手机备忘] " + note, "好哒，小木已把这条生活备忘记在心里啦！", "Tina");
                StickS3Avatar::getInstance().generateDiaryEntry("主人从手机同步了一条新的生活备忘给我。");
                notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
            }
        } else if (action == "wifi_cfg") {
            String ssid = "";
            String pwd = "";
            bool is_hs = false;
            uint32_t limit_mb = 100;
            bool cutoff = true;

            // 支持嵌套在 value 字段中的 JSON 字符串
            String val_str = doc["value"] | "";
            if (val_str.startsWith("{")) {
                JsonDocument sub;
                if (!deserializeJson(sub, val_str)) {
                    ssid = sub["ssid"] | "";
                    pwd = sub["pwd"] | (sub["pass"] | "");
                    is_hs = sub["is_hotspot"] | false;
                    limit_mb = sub["data_limit_mb"] | 100;
                    cutoff = sub["cutoff_enabled"] | true;
                }
            }
            if (ssid.length() == 0) {
                ssid = doc["ssid"] | "";
                pwd = doc["pwd"] | (doc["pass"] | "");
                is_hs = doc["is_hotspot"] | false;
                limit_mb = doc["data_limit_mb"] | 100;
                cutoff = doc["cutoff_enabled"] | true;
            }

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
            bool is_hs = doc["is_hotspot"] | true;
            uint32_t limit_mb = doc["data_limit_mb"] | (doc["value"] | 100);
            bool cutoff = doc["cutoff_enabled"] | true;
            StickS3ConfigManager::getInstance().saveHotspotConfig(is_hs, limit_mb, cutoff);
            String msg = "已更新手机热点流量策略：上限 " + String(limit_mb) + "MB，自动熔断保护 " + (cutoff ? "开启" : "关闭");
            StickS3Avatar::getInstance().generateDiaryEntry(msg);
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "reset_traffic") {
            StickS3ConfigManager::getInstance().resetHotspotTraffic();
            StickS3Avatar::getInstance().generateDiaryEntry("手机热点流量统计已重置为 0 MB。");
            notifyDiary(StickS3Avatar::getInstance().getStats().current_diary);
        } else if (action == "query_wifi_status" || action == "get_status") {
            // 立即刷新并推送特征值
            updateSnapshots();
        }
        Serial.printf("[BLE-INJECT] Processed action: %s\n", action.c_str());
        updateSnapshots();
    }

private:
    StickS3BLESync()
        : _pCharMemory(nullptr), _pCharStatus(nullptr),
          _pCharDiary(nullptr), _pCharInject(nullptr) {}

    BLECharacteristic* _pCharMemory;
    BLECharacteristic* _pCharStatus;
    BLECharacteristic* _pCharDiary;
    BLECharacteristic* _pCharInject;
};

inline void StickS3BLEInjectCallbacks::onWrite(BLECharacteristic* pChar) {
    if (!pChar) return;
    std::string val = pChar->getValue();
    if (!val.empty()) {
        StickS3BLESync::getInstance().handleInjectCommand(String(val.c_str()));
    }
}

} // namespace sticks3
