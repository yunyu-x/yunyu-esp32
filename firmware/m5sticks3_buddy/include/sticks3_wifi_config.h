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
};

class StickS3ConfigManager {
public:
    static constexpr const char* NVS_NAMESPACE = "stick_cfg";

    StickS3ConfigManager()
        : _sta_state(STA_STATE_IDLE), _conn_start_time(0),
          _conn_timeout_ms(15000), _last_reconnect_attempt(0),
          _auto_reconnect(true), _sta_ip("0.0.0.0"), _sta_rssi(0) {
        _cfg.bailian_model = "qwen3.8-omni-flash-realtime";
        _cfg.bailian_voice = "Tina";
        _cfg.bailian_ws_url = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime";
        _cfg.bailian_prompt = "你是StickS3智能语音伴侣，请用简明生动的口语回答，每次回答控制在两句话以内。";
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
                voice == "Raymond" || voice == "Cherry" || voice == "Chelsie" ||
                voice == "Ethan");
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

        prefs.end();

        Serial.printf("[NVS] Loaded config: SSID=\"%s\", BailianKey=%s, Model=\"%s\", Voice=\"%s\"\n",
                      _cfg.wifi_ssid.c_str(),
                      _cfg.bailian_key.length() > 6 ? (_cfg.bailian_key.substring(0, 4) + "****").c_str() : "NotSet",
                      _cfg.bailian_model.c_str(),
                      _cfg.bailian_voice.c_str());
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
        
        // 保证 AP+STA 模式
        WiFi.mode(WIFI_AP_STA);
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
            // 掉线后每 30 秒自动重连一次
            if (millis() - _last_reconnect_attempt > 30000) {
                _last_reconnect_attempt = millis();
                Serial.println("[WIFI-STA] Auto-reconnecting to saved network...");
                startConnectSTA(_cfg.wifi_ssid, _cfg.wifi_pass);
            }
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
};

} // namespace sticks3
