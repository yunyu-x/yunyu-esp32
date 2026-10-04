/**
 * firmware/m5sticks3_buddy/include/sticks3_wifi_config.h
 * ------------------------------------------------------
 * M5Stack StickS3 业界标准 WiFi Web 配网与系统参数 NVS 持久化管理器
 * 1. NVS 持久化 (Preferences):
 *    - 存储 Wi-Fi AP 凭据 (SSID, Password)
 *    - 存储阿里云百炼 API-Key, 实时语音大模型名称, 音色与自定义 WebSocket URL
 * 2. STA 异步连接状态机:
 *    - 非阻塞轮询与掉线自动重连
 *    - 与 SoftAP ("StickS3-Buddy" 192.168.4.1) 保持 AP+STA 双模共存
 */

#pragma once

#include <Arduino.h>
#include <WiFi.h>
#include <Preferences.h>
#include <esp_wifi.h>
#include "sticks3_audio.h"

namespace sticks3 {

enum WiFiStaState {
    STA_STATE_IDLE = 0,
    STA_STATE_CONNECTING,
    STA_STATE_CONNECTED,
    STA_STATE_FAILED
};

struct StickS3Config {
    String wifi_ssid;
    String wifi_pass;
    String bailian_key;
    String bailian_model;
    String bailian_voice;
    String bailian_ws_url;
    String bailian_prompt;
    uint8_t speaker_volume;          // 播音音量 (0~100%, 默认 70% 黄金防破音)
    bool wakeword_enabled;
    uint8_t wakeword_sensitivity;
    uint16_t wakeword_timeout_sec;
    // 手机共享热点数据与流量限制管理
    bool is_hotspot;                 // 是否为手机移动热点
    uint32_t hotspot_limit_mb;       // 流量上限 (MB)，0 表示无限制
    uint32_t hotspot_used_kb;        // 当前已用流量 (KB)
    bool hotspot_cutoff_enabled;     // 达到 100% 流量上限是否自动熔断大模型连接保护流量
    bool hotspot_warning_issued;     // 80% 警戒通知是否已下发
    bool hotspot_cutoff_active;      // 是否正处于流量熔断保护状态
};

class StickS3ConfigManager {
public:
    static constexpr const char* NVS_NAMESPACE = "stick_cfg";

    StickS3ConfigManager()
        : _sta_state(STA_STATE_IDLE), _conn_start_time(0),
          _conn_timeout_ms(15000), _last_reconnect_attempt(0),
          _auto_reconnect(true), _sta_ip("0.0.0.0"), _sta_rssi(0),
          _traffic_byte_accumulator(0), _last_nvs_flush_kb(0),
          _pending_traffic_nvs_flush(false) {
        _cfg.bailian_model = "qwen3.8-omni-flash-realtime";
        _cfg.bailian_voice = "Tina";
        _cfg.bailian_ws_url = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime";
        _cfg.bailian_prompt = "你是StickS3智能语音伴侣，请用简明生动的口语回答，每次回答控制在两句话以内。";
        _cfg.speaker_volume = 70;
        _cfg.wakeword_enabled = true;
        _cfg.wakeword_sensitivity = 75;
        _cfg.wakeword_timeout_sec = 8;
        // 手机热点默认策略
        _cfg.is_hotspot = false;
        _cfg.hotspot_limit_mb = 100;
        _cfg.hotspot_used_kb = 0;
        _cfg.hotspot_cutoff_enabled = true;
        _cfg.hotspot_warning_issued = false;
        _cfg.hotspot_cutoff_active = false;
    }

    static StickS3ConfigManager& getInstance() {
        static StickS3ConfigManager instance;
        return instance;
    }

    void begin() {
        loadConfig();

        // 若 NVS 中已有保存的 WiFi 凭据，开机自动尝试连接真实可用网络
        if (_cfg.wifi_ssid.length() > 0) {
            Serial.printf("[WIFI-CFG] Auto-connecting saved Wi-Fi SSID: \"%s\"...\n", _cfg.wifi_ssid.c_str());
            startConnectSTA(_cfg.wifi_ssid, _cfg.wifi_pass);
        } else {
            Serial.println("[WIFI-CFG] No saved Wi-Fi credentials in NVS. Waiting for Web config.");
        }
    }

    static bool isVoiceSupported(const String& voice) {
        return (voice == "Tina" || voice == "Serena" || voice == "Cindy" ||
                voice == "Raymond" || voice == "Zane" || voice == "Katerina" ||
                voice == "Mia" || voice == "Chloe");
    }

    void loadConfig() {
        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, true)) { // Read-only mode
            Serial.println("[NVS] No existing config found or partition uninitialized.");
            return;
        }

        _cfg.wifi_ssid = prefs.getString("ssid", "");
        _cfg.wifi_pass = prefs.getString("pass", "");
        _cfg.bailian_key = prefs.getString("bl_key", "");

        String m = prefs.getString("bl_model", "");
        if (m.length() > 0) _cfg.bailian_model = m;

        String v = prefs.getString("bl_voice", "");
        if (v.length() > 0) {
            if (isVoiceSupported(v)) {
                _cfg.bailian_voice = v;
            } else {
                Serial.printf("[NVS] Unsupported voice '%s' in NVS, resetting to default 'Tina'\n", v.c_str());
                _cfg.bailian_voice = "Tina";
            }
        }

        String u = prefs.getString("bl_ws", "");
        if (u.length() > 0) _cfg.bailian_ws_url = u;

        String p = prefs.getString("bl_prompt", "");
        if (p.length() > 0) _cfg.bailian_prompt = p;

        _cfg.speaker_volume = (uint8_t)prefs.getUChar("spk_vol", 70);
        if (_cfg.speaker_volume < 10 || _cfg.speaker_volume > 100) _cfg.speaker_volume = 70;
        StickS3Audio::getInstance().setSpeakerVolume(_cfg.speaker_volume);

        _cfg.wakeword_enabled = prefs.getBool("ww_en", true);
        _cfg.wakeword_sensitivity = (uint8_t)prefs.getUChar("ww_sens", 75);
        _cfg.wakeword_timeout_sec = prefs.getUShort("ww_tout", 8);

        // 加载手机共享热点策略与流量累计
        _cfg.is_hotspot = prefs.getBool("is_hs", false);
        _cfg.hotspot_limit_mb = prefs.getUInt("hs_limit", 100);
        _cfg.hotspot_used_kb = prefs.getUInt("hs_kb", 0);
        _cfg.hotspot_cutoff_enabled = prefs.getBool("hs_cutoff", true);
        _cfg.hotspot_warning_issued = false;
        _cfg.hotspot_cutoff_active = (_cfg.is_hotspot && _cfg.hotspot_limit_mb > 0 && (_cfg.hotspot_used_kb / 1024) >= _cfg.hotspot_limit_mb);

        prefs.end();

        Serial.printf("[NVS] Loaded config: SSID=\"%s\", Hotspot=%s(Limit:%uMB, Used:%.2fMB), BailianKey=%s, Model=\"%s\", Voice=\"%s\", Volume=%u%%, WakeWord=%s(%u%%)\n",
                      _cfg.wifi_ssid.c_str(),
                      _cfg.is_hotspot ? "YES" : "NO",
                      (unsigned)_cfg.hotspot_limit_mb,
                      (float)_cfg.hotspot_used_kb / 1024.0f,
                      _cfg.bailian_key.length() > 6 ? (_cfg.bailian_key.substring(0, 4) + "****").c_str() : "NotSet",
                      _cfg.bailian_model.c_str(),
                      _cfg.bailian_voice.c_str(),
                      (unsigned)_cfg.speaker_volume,
                      _cfg.wakeword_enabled ? "ON" : "OFF",
                      (unsigned)_cfg.wakeword_sensitivity);
    }

    bool saveSpeakerVolume(uint8_t vol) {
        if (vol < 10) vol = 10;
        if (vol > 100) vol = 100;
        _cfg.speaker_volume = vol;
        Preferences prefs;
        if (prefs.begin(NVS_NAMESPACE, false)) {
            prefs.putUChar("spk_vol", vol);
            prefs.end();
        }
        StickS3Audio::getInstance().setSpeakerVolume(vol);
        Serial.printf("[NVS] Saved speaker volume: %u%%\n", (unsigned)vol);
        return true;
    }

    uint8_t getSpeakerVolume() const { return _cfg.speaker_volume; }

    bool saveHotspotConfig(bool is_hotspot, uint32_t limit_mb, bool cutoff_enabled = true) {
        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, false)) return false;

        _cfg.is_hotspot = is_hotspot;
        _cfg.hotspot_limit_mb = limit_mb;
        _cfg.hotspot_cutoff_enabled = cutoff_enabled;
        if (!_cfg.is_hotspot) {
            _cfg.hotspot_cutoff_active = false;
            _cfg.hotspot_warning_issued = false;
        } else if (_cfg.hotspot_limit_mb > 0) {
            _cfg.hotspot_cutoff_active = ((_cfg.hotspot_used_kb / 1024) >= _cfg.hotspot_limit_mb);
        }

        prefs.putBool("is_hs", is_hotspot);
        prefs.putUInt("hs_limit", limit_mb);
        prefs.putBool("hs_cutoff", cutoff_enabled);
        prefs.end();

        Serial.printf("[NVS] Saved Hotspot config: is_hotspot=%s, limit=%uMB, cutoff=%s\n",
                      is_hotspot ? "true" : "false", (unsigned)limit_mb, cutoff_enabled ? "true" : "false");
        return true;
    }

    void addNetworkTraffic(size_t rx_bytes, size_t tx_bytes) {
        if (!_cfg.is_hotspot) return;

        _traffic_byte_accumulator += (rx_bytes + tx_bytes);
        if (_traffic_byte_accumulator >= 1024) {
            uint32_t kb_delta = _traffic_byte_accumulator / 1024;
            _traffic_byte_accumulator %= 1024;
            _cfg.hotspot_used_kb += kb_delta;

            // 检查 80% 警戒阈值
            if (_cfg.hotspot_limit_mb > 0) {
                uint32_t limit_kb = _cfg.hotspot_limit_mb * 1024;
                if (_cfg.hotspot_used_kb >= (limit_kb * 8 / 10) && !_cfg.hotspot_warning_issued) {
                    _cfg.hotspot_warning_issued = true;
                    Serial.printf("[TRAFFIC-WARN] Hotspot traffic reached 80%% (%u KB / %u KB)\n",
                                  (unsigned)_cfg.hotspot_used_kb, (unsigned)limit_kb);
                }

                // 检查 100% 熔断阈值
                if (_cfg.hotspot_used_kb >= limit_kb) {
                    _cfg.hotspot_cutoff_active = true;
                    Serial.printf("[TRAFFIC-CUTOFF] Hotspot limit %u MB exceeded! Cloud streaming protected.\n",
                                  (unsigned)_cfg.hotspot_limit_mb);
                }
            }

            // 遵循工程公理二：严禁在 websocket_task (Core 0) 或网络数据接收回调中直接写 Flash
            // 标记待沉淀标记，由 loopTask (Core 1) 异步安全写入，彻底消除 Cache 禁用引发的 Panic 重启
            if (_cfg.hotspot_used_kb - _last_nvs_flush_kb >= 256) {
                _pending_traffic_nvs_flush = true;
            }
        }
    }

    void flushTrafficToNVS() {
        Preferences prefs;
        if (prefs.begin(NVS_NAMESPACE, false)) {
            prefs.putUInt("hs_kb", _cfg.hotspot_used_kb);
            prefs.end();
            _last_nvs_flush_kb = _cfg.hotspot_used_kb;
        }
    }

    void resetHotspotTraffic() {
        _cfg.hotspot_used_kb = 0;
        _traffic_byte_accumulator = 0;
        _last_nvs_flush_kb = 0;
        _cfg.hotspot_warning_issued = false;
        _cfg.hotspot_cutoff_active = false;
        flushTrafficToNVS();
        Serial.println("[TRAFFIC] Hotspot usage reset to 0 KB.");
    }

    // 抹除 NVS 中所有系统与网络配置，恢复出厂默认值
    void clearAllConfig() {
        Preferences prefs;
        if (prefs.begin(NVS_NAMESPACE, false)) {
            prefs.clear();
            prefs.end();
        }
        _cfg = StickS3Config();
        _cfg.bailian_model = "qwen3.8-omni-flash-realtime";
        _cfg.bailian_voice = "Tina";
        _cfg.bailian_prompt = "你是StickS3智能语音伴侣，请用简明生动的口语回答，每次回答控制在两句话以内。";
        _cfg.wakeword_enabled = true;
        _cfg.wakeword_sensitivity = 75;
        _cfg.wakeword_timeout_sec = 8;
        _cfg.is_hotspot = false;
        _cfg.hotspot_limit_mb = 100;
        _cfg.hotspot_used_kb = 0;
        _cfg.hotspot_cutoff_enabled = true;
        _cfg.hotspot_warning_issued = false;
        _cfg.hotspot_cutoff_active = false;
        Serial.println("[NVS] All StickS3 configuration cleared from Flash.");
    }

    float getHotspotUsedMB() const {
        return (float)_cfg.hotspot_used_kb / 1024.0f;
    }

    uint32_t getHotspotLimitMB() const {
        return _cfg.hotspot_limit_mb;
    }

    float getHotspotRemainingMB() const {
        if (!_cfg.is_hotspot || _cfg.hotspot_limit_mb == 0) return 9999.0f;
        float used = getHotspotUsedMB();
        if (used >= (float)_cfg.hotspot_limit_mb) return 0.0f;
        return (float)_cfg.hotspot_limit_mb - used;
    }

    bool isHotspot() const { return _cfg.is_hotspot; }
    bool isHotspotCutoffActive() const { return _cfg.hotspot_cutoff_active; }
    bool isHotspotCutoffEnabled() const { return _cfg.hotspot_cutoff_enabled; }
    bool isHotspotWarningIssued() const { return _cfg.hotspot_warning_issued; }

    bool saveWakeWordConfig(bool enabled, uint8_t sensitivity, uint16_t timeout_sec = 8) {
        if (sensitivity > 100) sensitivity = 100;
        if (sensitivity < 10) sensitivity = 10;
        if (timeout_sec < 3) timeout_sec = 3;
        if (timeout_sec > 60) timeout_sec = 60;

        if (enabled == _cfg.wakeword_enabled && sensitivity == _cfg.wakeword_sensitivity && timeout_sec == _cfg.wakeword_timeout_sec) {
            Serial.println("[NVS] Wake word config unchanged. Skipping Flash write.");
            return true;
        }

        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, false)) return false;

        _cfg.wakeword_enabled = enabled;
        _cfg.wakeword_sensitivity = sensitivity;
        _cfg.wakeword_timeout_sec = timeout_sec;

        prefs.putBool("ww_en", enabled);
        prefs.putUChar("ww_sens", sensitivity);
        prefs.putUShort("ww_tout", timeout_sec);
        prefs.end();

        Serial.printf("[NVS] Saved Wake Word config: Enabled=%s, Sens=%u%%, Timeout=%us\n",
                      enabled ? "true" : "false", (unsigned)sensitivity, (unsigned)timeout_sec);
        return true;
    }

    bool saveWiFiConfig(const String& ssid, const String& pass) {
        if (ssid == _cfg.wifi_ssid && pass == _cfg.wifi_pass) {
            Serial.println("[NVS] Wi-Fi config unchanged. Skipping Flash write.");
            return true;
        }

        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, false)) return false;

        _cfg.wifi_ssid = ssid;
        _cfg.wifi_pass = pass;

        prefs.putString("ssid", ssid);
        prefs.putString("pass", pass);
        prefs.end();

        Serial.printf("[NVS] Saved Wi-Fi credentials for SSID: \"%s\"\n", ssid.c_str());
        return true;
    }

    bool saveBailianVoice(const String& voice) {
        String validated_voice = isVoiceSupported(voice) ? voice : "Tina";
        if (validated_voice == _cfg.bailian_voice) return true;

        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, false)) return false;
        _cfg.bailian_voice = validated_voice;
        prefs.putString("bl_voice", validated_voice);
        prefs.end();
        Serial.printf("[NVS] Updated Bailian Voice to: %s\n", validated_voice.c_str());
        return true;
    }

    bool saveBailianConfig(const String& key, const String& model = "",
                           const String& voice = "", const String& ws_url = "",
                           const String& prompt = "") {
        String validated_voice = voice;
        if (validated_voice.length() > 0 && !isVoiceSupported(validated_voice)) {
            Serial.printf("[NVS] Voice '%s' is not supported, fallback to 'Tina'\n", validated_voice.c_str());
            validated_voice = "Tina";
        }

        bool dirty = false;
        if (key.length() > 0 && key != _cfg.bailian_key) dirty = true;
        if (model.length() > 0 && model != _cfg.bailian_model) dirty = true;
        if (validated_voice.length() > 0 && validated_voice != _cfg.bailian_voice) dirty = true;
        if (ws_url.length() > 0 && ws_url != _cfg.bailian_ws_url) dirty = true;
        if (prompt.length() > 0 && prompt != _cfg.bailian_prompt) dirty = true;

        if (!dirty) {
            Serial.println("[NVS] Bailian config unchanged. Skipping Flash write.");
            return true;
        }

        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, false)) return false;

        if (key.length() > 0 && key != _cfg.bailian_key) {
            _cfg.bailian_key = key;
            prefs.putString("bl_key", key);
        }
        if (model.length() > 0 && model != _cfg.bailian_model) {
            _cfg.bailian_model = model;
            prefs.putString("bl_model", model);
        }
        if (validated_voice.length() > 0 && validated_voice != _cfg.bailian_voice) {
            _cfg.bailian_voice = validated_voice;
            prefs.putString("bl_voice", validated_voice);
        }
        if (ws_url.length() > 0 && ws_url != _cfg.bailian_ws_url) {
            _cfg.bailian_ws_url = ws_url;
            prefs.putString("bl_ws", ws_url);
        }
        if (prompt.length() > 0 && prompt != _cfg.bailian_prompt) {
            _cfg.bailian_prompt = prompt;
            prefs.putString("bl_prompt", prompt);
        }
        prefs.end();

        Serial.println("[NVS] Saved Alibaba Cloud Bailian configuration.");
        return true;
    }

    // 触发连接指定 Wi-Fi
    void startConnectSTA(const String& ssid, const String& pass) {
        if (ssid.length() == 0) return;

        Serial.printf("[WIFI-STA] Initiating connection to \"%s\"...\n", ssid.c_str());
        
        // 保证 AP+STA 模式，设置抗饱和稳定发射功率 (+17dBm)，避免过高射频脉冲导致电源塌陷与破音
        WiFi.mode(WIFI_AP_STA);
        WiFi.setTxPower(WIFI_POWER_17dBm);
        WiFi.setAutoReconnect(false); // 统一由 StickS3ConfigManager 状态机调度，杜绝并发竞争崩溃
        WiFi.disconnect(false, false);
        delay(20);

        WiFi.begin(ssid.c_str(), pass.c_str());
        _sta_state = STA_STATE_CONNECTING;
        _conn_start_time = millis();
    }

    // 周期性轮询（非阻塞，在 loop() 中高频调用）
    void update() {
        if (_sta_state == STA_STATE_CONNECTING) {
            if (WiFi.status() == WL_CONNECTED) {
                _sta_state = STA_STATE_CONNECTED;
                _sta_ip = WiFi.localIP().toString();
                _sta_rssi = WiFi.RSSI();
                Serial.printf("\n[WIFI-STA] Successfully CONNECTED! IP: %s | Gateway: %s | RSSI: %ddBm\n",
                              _sta_ip.c_str(), WiFi.gatewayIP().toString().c_str(), _sta_rssi);

                // ESP32 硬件底层在 STA 连接时已自动将 SoftAP 物理信道同步对齐，无需且严禁重复调用 softAP() 以免重置 netif 导致 Panic
                int sta_ch = WiFi.channel();
                Serial.printf("[WIFI] STA active on Channel %d (SoftAP hardware-aligned)\n", sta_ch);

                configTime(8 * 3600, 0, "ntp.aliyun.com", "pool.ntp.org", "time.asia.apple.com");
                Serial.println("[NTP] Initialized SNTP time sync with ntp.aliyun.com");
            } else if (millis() - _conn_start_time >= _conn_timeout_ms) {
                _sta_state = STA_STATE_FAILED;
                Serial.println("\n[WIFI-STA] Connection TIMEOUT or FAILED. Reverting to idle.");
            }
        } else if (_sta_state == STA_STATE_CONNECTED) {
            if (WiFi.status() != WL_CONNECTED) {
                _sta_state = STA_STATE_FAILED;
                _sta_ip = "0.0.0.0";
                _last_reconnect_attempt = millis();
                Serial.println("[WIFI-STA] Wi-Fi connection lost!");
            } else {
                _sta_rssi = WiFi.RSSI();
            }
        } else if (_sta_state == STA_STATE_FAILED && _auto_reconnect && _cfg.wifi_ssid.length() > 0) {
            // 掉线后每 15 秒自动重连一次 (缩短重连等待期，提升热点切网响应度)
            if (millis() - _last_reconnect_attempt > 15000) {
                _last_reconnect_attempt = millis();
                Serial.println("[WIFI-STA] Auto-reconnecting to saved network...");
                startConnectSTA(_cfg.wifi_ssid, _cfg.wifi_pass);
            }
        }

        // 遵循工程公理二：在 loopTask 主循环中安全异步沉淀热点流量至 NVS Flash (杜绝在中断/ws_task中写Flash)
        static uint32_t s_last_traffic_flush_tick = 0;
        if (_pending_traffic_nvs_flush || 
            (_cfg.is_hotspot && (_cfg.hotspot_used_kb != _last_nvs_flush_kb) && (millis() - s_last_traffic_flush_tick >= 15000))) {
            _pending_traffic_nvs_flush = false;
            s_last_traffic_flush_tick = millis();
            flushTrafficToNVS();
        }
    }

    // Getters
    bool isStaConnected() const { return (_sta_state == STA_STATE_CONNECTED && WiFi.status() == WL_CONNECTED); }
    WiFiStaState getStaState() const { return _sta_state; }
    String getStaIP() const { return _sta_ip; }
    int getStaRSSI() const { return _sta_rssi; }
    const StickS3Config& getConfig() const { return _cfg; }
    bool hasBailianKey() const { return _cfg.bailian_key.length() > 10; }
    String getMaskedBailianKey() const {
        if (_cfg.bailian_key.length() <= 8) return _cfg.bailian_key;
        return _cfg.bailian_key.substring(0, 4) + "..." + _cfg.bailian_key.substring(_cfg.bailian_key.length() - 4);
    }

private:
    StickS3Config _cfg;
    WiFiStaState _sta_state;
    uint32_t _conn_start_time;
    uint32_t _conn_timeout_ms;
    uint32_t _last_reconnect_attempt;
    bool _auto_reconnect;
    String _sta_ip;
    int _sta_rssi;
    uint32_t _traffic_byte_accumulator;
    uint32_t _last_nvs_flush_kb;
    volatile bool _pending_traffic_nvs_flush;
};

} // namespace sticks3
