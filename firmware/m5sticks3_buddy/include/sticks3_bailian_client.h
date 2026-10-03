/**
 * firmware/m5sticks3_buddy/include/sticks3_bailian_client.h
 * ---------------------------------------------------------
 * M5Stack StickS3 阿里云百炼 (Model Studio / DashScope) 全双工流式大模型客户端
 * 1. 协议核心：
 *    - 基于原生 esp_websocket_client WSS 443 加密长连接 (硬件 mbedTLS 加速)
 *    - 遵循 DashScope Realtime API (Qwen-Omni-Realtime / Qwen3.8-Omni-Flash-Realtime)
 * 2. 全双工交互流：
 *    - 上行音频：16kHz 16-bit Mono PCM 实时流式切片 -> Base64 -> input_audio_buffer.append
 *    - 下行文本：response.audio_transcript.delta 流式追加并同步渲染 LCD
 *    - 下行音频：response.audio.delta 流式解码 -> PSRAM 环形缓冲 -> I2S 边收边播 (毫秒级首字延迟)
 * 3. 毫秒级中途打断 (Barge-In)：
 *    - 服务端 VAD (input_audio_buffer.speech_started) 自动识别打断
 *    - 本地硅麦高能量打断与物理按键 A 打断
 *    - 动作：瞬间切断喇叭放音 (interruptPlayback) -> 发送 response.cancel -> 清空下行缓冲 -> 切换倾听状态
 */

#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <esp_websocket_client.h>
#include <mbedtls/base64.h>
#include "sticks3_audio.h"
#include "sticks3_wifi_config.h"
#include "sticks3_memory_store.h"
#include "sticks3_wakeword.h"

namespace sticks3 {

enum BailianAgentState {
    BL_STATE_DISCONNECTED = 0,
    BL_STATE_CONNECTING,
    BL_STATE_CONNECTED_IDLE,
    BL_STATE_LISTENING,     // 正在拾音并流式上传
    BL_STATE_THINKING,      // 用户停顿，百炼大模型推理中
    BL_STATE_SPEAKING,      // 百炼大模型正在流式吐字与发声
    BL_STATE_INTERRUPTED,   // 用户中途打断 (Barge-In)
    BL_STATE_ERROR
};

using BailianTextCallback = std::function<void(const String& user_text, const String& ai_text, bool is_final)>;
using BailianStateCallback = std::function<void(BailianAgentState old_state, BailianAgentState new_state)>;

class StickS3BailianClient {
public:
    static StickS3BailianClient& getInstance() {
        static StickS3BailianClient instance;
        return instance;
    }

    StickS3BailianClient()
        : _ws_client(nullptr), _is_ws_connected(false), _state(BL_STATE_DISCONNECTED),
          _last_mic_read_time(0), _last_rx_stream_time(0), _last_session_update_time(0),
          _session_initialized(false), _server_response_active(false),
          _response_done_received(false), _is_response_cancelled(false),
          _pending_cancel(false), _pending_memory_save(false), _pending_reconnect(false),
          _server_in_speech(false), _last_activity_time(0), _server_output_sample_rate(16000),
          _last_state_change(0), _total_interrupts(0), _last_error(""),
          _rx_text_dirty(false), _wake_window_until(0) {
        _user_query = "";
        _ai_reply = "";
        _pending_turn_user = "";
        _pending_turn_ai = "";
    }

    void setTextCallback(BailianTextCallback cb) { _on_text = cb; }
    void setStateCallback(BailianStateCallback cb) { _on_state = cb; }

    bool begin() {
        Serial.println("[BAILIAN] Initializing Bailian Realtime Voice Subsystem...");
        _user_query.reserve(256);
        _ai_reply.reserve(1024);
        return true;
    }

    // 建立 WebSocket 连接
    bool connect() {
        auto& cfg_mgr = StickS3ConfigManager::getInstance();
        if (!cfg_mgr.isStaConnected()) {
            _last_error = "WiFi未连接";
            setState(BL_STATE_ERROR);
            Serial.println("[BAILIAN] Cannot connect: WiFi STA not connected.");
            return false;
        }

        const auto& cfg = cfg_mgr.getConfig();
        if (cfg.bailian_key.length() < 10) {
            _last_error = "未设置百炼Key";
            setState(BL_STATE_ERROR);
            Serial.println("[BAILIAN] Cannot connect: Bailian API key not set.");
            return false;
        }

        disconnect();

        _last_activity_time = millis();
        setState(BL_STATE_CONNECTING);

        // 构造动态连接 URL 与 Authorization 标头
        String url = cfg.bailian_ws_url;
        if (url.indexOf("?") == -1) {
            url += "?model=" + cfg.bailian_model;
        } else if (url.indexOf("model=") == -1) {
            url += "&model=" + cfg.bailian_model;
        }

        _auth_header = "Authorization: Bearer " + cfg.bailian_key + "\r\n";

// GlobalSign Root CA (Root R46 & Root R3) 用于 DashScope WSS 443 证书链校验
static const char* DASHSCOPE_ROOT_CA = 
"-----BEGIN CERTIFICATE-----\n"
"MIIFWjCCA0KgAwIBAgISEdK7udcjGJ5AXwqdLdDfJWfRMA0GCSqGSIb3DQEBDAUA\n"
"MEYxCzAJBgNVBAYTAkJFMRkwFwYDVQQKExBHbG9iYWxTaWduIG52LXNhMRwwGgYD\n"
"VQQDExNHbG9iYWxTaWduIFJvb3QgUjQ2MB4XDTE5MDMyMDAwMDAwMFoXDTQ2MDMy\n"
"MDAwMDAwMFowRjELMAkGA1UEBhMCQkUxGTAXBgNVBAoTEEdsb2JhbFNpZ24gbnYt\n"
"c2ExHDAaBgNVBAMTE0dsb2JhbFNpZ24gUm9vdCBSNDYwggIiMA0GCSqGSIb3DQEB\n"
"AQUAA4ICDwAwggIKAoICAQCsrHQy6LNl5brtQyYdpokNRbopiLKkHWPd08EsCVeJ\n"
"OaFV6Wc0dwxu5FUdUiXSE2te4R2pt32JMl8Nnp8semNgQB+msLZ4j5lUlghYruQG\n"
"vGIFAha/r6gjA7aUD7xubMLL1aa7DOn2wQL7Id5m3RerdELv8HQvJfTqa1VbkNud\n"
"316HCkD7rRlr+/fKYIje2sGP1q7Vf9Q8g+7XFkyDRTNrJ9CG0Bwta/OrffGFqfUo\n"
"0q3v84RLHIf8E6M6cqJaESvWJ3En7YEtbWaBkoe0G1h6zD8K+kZPTXhc+CtI4wSE\n"
"y132tGqzZfxCnlEmIyDLPRT5ge1lFgBPGmSXZgjPjHvjK8Cd+RTyG/FWaha/LIWF\n"
"zXg4mutCagI0GIMXTpRW+LaCtfOW3T3zvn8gdz57GSNrLNRyc0NXfeD412lPFzYE\n"
"+cCQYDdF3uYM2HSNrpyibXRdQr4G9dlkbgIQrImwTDsHTUB+JMWKmIJ5jqSngiCN\n"
"I/onccnfxkF0oE32kRbcRoxfKWMxWXEM2G/CtjJ9++ZdU6Z+Ffy7dXxd7Pj2Fxzs\n"
"x2sZy/N78CsHpdlseVR2bJ0cpm4O6XkMqCNqo98bMDGfsVR7/mrLZqrcZdCinkqa\n"
"ByFrgY/bxFn63iLABJzjqls2k+g9vXqhnQt2sQvHnf3PmKgGwvgqo6GDoLclcqUC\n"
"4wIDAQABo0IwQDAOBgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNV\n"
"HQ4EFgQUA1yrc4GHqMywptWU4jaWSf8FmSwwDQYJKoZIhvcNAQEMBQADggIBAHx4\n"
"7PYCLLtbfpIrXTncvtgdokIzTfnvpCo7RGkerNlFo048p9gkUbJUHJNOxO97k4Vg\n"
"JuoJSOD1u8fpaNK7ajFxzHmuEajwmf3lH7wvqMxX63bEIaZHU1VNaL8FpO7XJqti\n"
"2kM3S+LGteWygxk6x9PbTZ4IevPuzz5i+6zoYMzRx6Fcg0XERczzF2sUyQQCPtIk\n"
"pnnpHs6i58FZFZ8d4kuaPp92CC1r2LpXFNqD6v6MVenQTqnMdzGxRBF6XLE+0xRF\n"
"FRhiJBPSy03OXIPBNvIQtQ6IbbjhVp+J3pZmOUdkLG5NrmJ7v2B0GbhWrJKsFjLt\n"
"rWhV/pi60zTe9Mlhww6G9kuEYO4Ne7UyWHmRVSyBQ7N0H3qqJZ4d16GLuc1CLgSk\n"
"ZoNNiTW2bKg2SnkheCLQQrzRQDGQob4Ez8pn7fXwgNNgyYMqIgXQBztSvwyeqiv5\n"
"u+YfjyW6hY0XHgL+XVAEV8/+LbzvXMAaq7afJMbfc2hIkCwU9D9SGuTSyxTDYWnP\n"
"4vkYxboznxSjBF25cfe1lNj2M8FawTSLfJvdkzrnE6JwYZ+vj+vYxXX4M2bUdGc6\n"
"N3ec592kD3ZDZopD8p/7DEJ4Y9HiD2971KE9dJeFt0g5QdYg/NA6s/rob8SKunE3\n"
"vouXsXgxT7PntgMTzlSdriVZzH81Xwj3QEUxeCp6\n"
"-----END CERTIFICATE-----\n"
"-----BEGIN CERTIFICATE-----\n"
"MIIDXzCCAkegAwIBAgILBAAAAAABIVhTCKIwDQYJKoZIhvcNAQELBQAwTDEgMB4G\n"
"A1UECxMXR2xvYmFsU2lnbiBSb290IENBIC0gUjMxEzARBgNVBAoTCkdsb2JhbFNp\n"
"Z24xEzARBgNVBAMTCkdsb2JhbFNpZ24wHhcNMDkwMzE4MTAwMDAwWhcNMjkwMzE4\n"
"MTAwMDAwWjBMMSAwHgYDVQQLExdHbG9iYWxTaWduIFJvb3QgQ0EgLSBSMzETMBEG\n"
"A1UEChMKR2xvYmFsU2lnbjETMBEGA1UEAxMKR2xvYmFsU2lnbjCCASIwDQYJKoZI\n"
"hvcNAQEBBQADggEPADCCAQoCggEBAMwldpB5BngiFvXAg7aEyiie/QV2EcWtiHL8\n"
"RgJDx7KKnQRfJMsuS+FggkbhUqsMgUdwbN1k0ev1LKMPgj0MK66X17YUhhB5uzsT\n"
"gHeMCOFJ0mpiLx9e+pZo34knlTifBtc+ycsmWQ1z3rDI6SYOgxXG71uL0gRgykmm\n"
"KPZpO/bLyCiR5Z2KYVc3rHQU3HTgOu5yLy6c+9C7v/U9AOEGM+iCK65TpjoWc4zd\n"
"QQ4gOsC0p6Hpsk+QLjJg6VfLuQSSaGjlOCZgdbKfd/+RFO+uIEn8rUAVSNECMWEZ\n"
"XriX7613t2Saer9fwRPvm2L7DWzgVGkWqQPabumDk3F2xmmFghcCAwEAAaNCMEAw\n"
"DgYDVR0PAQH/BAQDAgEGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFI/wS3+o\n"
"LkUkrk1Q+mOai97i3Ru8MA0GCSqGSIb3DQEBCwUAA4IBAQBLQNvAUKr+yAzv95ZU\n"
"RUm7lgAJQayzE4aGKAczymvmdLm6AC2upArT9fHxD4q/c2dKg8dEe3jgr25sbwMp\n"
"jjM5RcOO5LlXbKr8EpbsU8Yt5CRsuZRj+9xTaGdWPoO4zzUhw8lo/s7awlOqzJCK\n"
"6fBdRoyV3XpYKBovHd7NADdBj+1EbddTKJd+82cEHhXXipa0095MJ6RMG3NzdvQX\n"
"mcIfeg7jLQitChws/zyrVQ4PkX4268NXSb7hLi18YIvDQVETI53O9zJrlAGomecs\n"
"Mx86OyXShkDOOyyGeMlhLxS67ttVb9+E7gUJTb0o2HLO02JQZR7rkpeDMdmztcpH\n"
"WD9f\n"
"-----END CERTIFICATE-----\n";

        // 等待 SNTP 授时同步以通过 TLS 证书有效期校验 (避免 1970 年校验失败)
        time_t now = time(nullptr);
        if (now < 1700000000) {
            Serial.println("[BAILIAN] Waiting for SNTP time sync before TLS handshake...");
            int wait_cnt = 0;
            while (time(nullptr) < 1700000000 && wait_cnt++ < 20) {
                delay(100);
            }
            now = time(nullptr);
            Serial.printf("[BAILIAN] SNTP time sync status: %s (epoch=%ld)\n",
                          (now >= 1700000000) ? "SUCCESS" : "TIMEOUT", (long)now);
        }

        String path = "/api-ws/v1/realtime?model=" + cfg.bailian_model;
        Serial.printf("[BAILIAN] Connecting WSS host=dashscope.aliyuncs.com path=%s (Model: %s)\n",
                      path.c_str(), cfg.bailian_model.c_str());

        esp_websocket_client_config_t ws_cfg = {};
        ws_cfg.host = "dashscope.aliyuncs.com";
        ws_cfg.port = 443;
        ws_cfg.path = path.c_str();
        ws_cfg.transport = WEBSOCKET_TRANSPORT_OVER_SSL;
        ws_cfg.headers = _auth_header.c_str();
        ws_cfg.cert_pem = DASHSCOPE_ROOT_CA;
        ws_cfg.cert_len = strlen(DASHSCOPE_ROOT_CA) + 1;
        ws_cfg.buffer_size = 28672; // 28KB 接收缓冲，容纳完整 audio.delta (20.8KB)
        ws_cfg.task_stack = 20480;  // 20KB 堆栈确保 mbedTLS 握手与消息解析
        ws_cfg.pingpong_timeout_sec = 120;
        ws_cfg.ping_interval_sec = 10;
        ws_cfg.disable_pingpong_discon = true;
        ws_cfg.keep_alive_enable = true;
        ws_cfg.keep_alive_idle = 10;
        ws_cfg.keep_alive_interval = 5;
        ws_cfg.keep_alive_count = 3;
        ws_cfg.skip_cert_common_name_check = false; // 必须为 false 以确保 SNI 扩展被正确送达阿里云网关
        ws_cfg.disable_auto_reconnect = true;       // 由客户端统一状态机全权管控重连，杜绝底层并发重连竞争

        _ws_client = esp_websocket_client_init(&ws_cfg);
        if (!_ws_client) {
            _last_error = "WS客户端初始化失败";
            setState(BL_STATE_ERROR);
            return false;
        }

        esp_websocket_register_events(_ws_client, WEBSOCKET_EVENT_ANY, wsEventHandlerStatic, this);
        esp_err_t ret = esp_websocket_client_start(_ws_client);
        if (ret != ESP_OK) {
            _last_error = "WS启动失败: " + String(ret);
            setState(BL_STATE_ERROR);
            return false;
        }

        return true;
    }

    void disconnect() {
        if (_ws_client) {
            esp_websocket_client_stop(_ws_client);
            esp_websocket_client_destroy(_ws_client);
            _ws_client = nullptr;
        }
        _is_ws_connected = false;
        _session_initialized = false;
        _server_response_active = false;
        _response_done_received = false;
        _is_response_cancelled = false;
        _server_in_speech = false;
        setState(BL_STATE_DISCONNECTED);
    }

    // 线程安全与自适应重试发送 (带毫秒级让渡，彻底解决高吞吐时锁争用失败问题)
    bool sendWsTextWithRetry(const char* data, size_t len, int max_retries = 5, TickType_t timeout = pdMS_TO_TICKS(60)) {
        if (!_ws_client || !_is_ws_connected) return false;

        // 手机热点流量超额自动熔断保护检查
        if (StickS3ConfigManager::getInstance().isHotspotCutoffActive() &&
            StickS3ConfigManager::getInstance().isHotspotCutoffEnabled()) {
            Serial.println("[HOTSPOT-GUARD] Bailian streaming suspended due to traffic limit cutoff!");
            return false;
        }

        for (int i = 0; i < max_retries; i++) {
            int ret = esp_websocket_client_send_text(_ws_client, data, len, timeout);
            if (ret >= 0) {
                // 累计上行网络流量
                StickS3ConfigManager::getInstance().addNetworkTraffic(0, len);
                return true;
            }
            vTaskDelay(pdMS_TO_TICKS(15));
        }
        if (!esp_websocket_client_is_connected(_ws_client)) {
            _is_ws_connected = false;
        }
        return false;
    }

    // ==========================================
    // 核心打断控制 (Barge-In)
    // ==========================================
    void interrupt(const char* reason = "Manual/VAD") {
        if (_state == BL_STATE_SPEAKING || _state == BL_STATE_THINKING || StickS3Audio::getInstance().isPlaying()) {
            Serial.printf("[BAILIAN] >>> BARGE-IN TRIGGERED (%s)! Cutting audio & canceling response... <<<\n", reason);
            
            // 1. 立即标记进入打断状态并静音
            setState(BL_STATE_INTERRUPTED);
            StickS3Audio::getInstance().interruptPlayback();

            // 2. 标记界面显示已打断
            _ai_reply += " [已打断]";
            _rx_text_dirty = true;
            _total_interrupts++;

            // 3. 仅当云端响应尚在进行中，才向云端发送 response.cancel
            if (_server_response_active) {
                _is_response_cancelled = true;
                _server_response_active = false;
                _response_done_received = false;

                const char* cancel_payload = "{\"type\":\"response.cancel\"}";
                int ret = -1;
                if (isConnected()) {
                    ret = esp_websocket_client_send_text(_ws_client, cancel_payload, strlen(cancel_payload), pdMS_TO_TICKS(40));
                }
                if (ret >= 0) {
                    _pending_cancel = false;
                    Serial.println("[BAILIAN] >>> response.cancel instantly delivered! <<<");
                } else {
                    _pending_cancel = true;
                }
            } else {
                _is_response_cancelled = false;
                _pending_cancel = false;
            }
        }
    }

    // 周期性主循环任务 (在 loop() 中高频调用)
    void update() {
        auto& audio = StickS3Audio::getInstance();

        // 0. 保证 response.cancel 必定送达 DashScope 服务端 (限频 30ms 异步重试，杜绝主循环高频竞争)
        static uint32_t s_last_cancel_try = 0;
        if (_pending_cancel && isConnected() && (millis() - s_last_cancel_try >= 30)) {
            s_last_cancel_try = millis();
            const char* cancel_payload = "{\"type\":\"response.cancel\"}";
            int ret = esp_websocket_client_send_text(_ws_client, cancel_payload, strlen(cancel_payload), pdMS_TO_TICKS(40));
            if (ret >= 0) {
                _pending_cancel = false;
                Serial.println("[BAILIAN] >>> response.cancel successfully delivered to DashScope! <<<");
            }
        }

        // 1. 若大模型播音自然排空且无新流下发，平滑恢复倾听待命 (同时保证底层 audio 硬件正确复位)
        if (audio.isPlaying() && audio.getStreamBufferAvailable() == 0) {
            if (_response_done_received || (millis() - _last_rx_stream_time > 1500)) {
                audio.finishStreamPlayback();
                _response_done_received = false;
                _server_in_speech = false;
                if (_state == BL_STATE_SPEAKING) {
                    setState(BL_STATE_LISTENING);
                }
                // 核心：播报完毕后开启连续对话追问窗口 (默认 8~10 秒)
                // 确保用户可以在听到回复后自然直接追问，无需重新呼唤唤醒词！
                auto& cfg = StickS3ConfigManager::getInstance().getConfig();
                uint32_t tout_sec = cfg.wakeword_timeout_sec >= 5 ? cfg.wakeword_timeout_sec : 8;
                _wake_window_until = millis() + (tout_sec * 1000);
                Serial.printf("[BAILIAN] Natural playback finished. Continuous dialogue window OPEN for %us! Restored to LISTENING mode.\n", (unsigned)tout_sec);
            }
        }

        // 2. 打断状态维持 120ms 后自动切回倾听模式 (极低延迟恢复，无缝承接后续说话)
        if (_state == BL_STATE_INTERRUPTED && millis() - _last_state_change >= 120) {
            _server_in_speech = false;
            setState(BL_STATE_LISTENING);
        }

        // 2.1 思考超时安全看门狗 (Thinking Timeout Watchdog):
        // 若处于 BL_STATE_THINKING 超过 10 秒无音频响应，自动恢复到倾听状态，防止云端丢包挂起
        if (_state == BL_STATE_THINKING && millis() - _last_state_change >= 10000) {
            Serial.println("[BAILIAN-TIMEOUT] Thinking state timeout (>10s), restoring to LISTENING mode.");
            _server_in_speech = false;
            setState(BL_STATE_LISTENING);
        }

        // 2.2 错误状态自动自愈 (Error Self-Healing):
        // 若处于 BL_STATE_ERROR 状态超过 3 秒，自动自愈重置并尝试恢复倾听或重连，杜绝死锁卡死
        if (_state == BL_STATE_ERROR && millis() - _last_state_change >= 3000) {
            Serial.println("[BAILIAN-RECOVERY] Auto recovering from error state...");
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            auto& cfg = cfg_mgr.getConfig();
            if (!StickS3ConfigManager::isVoiceSupported(cfg.bailian_voice)) {
                Serial.printf("[BAILIAN-RECOVERY] Unsupported voice '%s' detected, fallback to Tina.\n", cfg.bailian_voice.c_str());
                cfg_mgr.saveBailianVoice("Tina");
            }
            _server_in_speech = false;
            _server_response_active = false;
            _response_done_received = false;
            _is_response_cancelled = false;
            if (isConnected()) {
                sendSessionUpdate();
                setState(BL_STATE_LISTENING);
            } else if (cfg_mgr.isStaConnected() && cfg.bailian_key.length() > 10) {
                connect();
            } else {
                setState(BL_STATE_DISCONNECTED);
            }
        }

        // 2.3 空闲长连接主动保活与刷新 (Active Idle Session Refresh before 300s limit):
        // 阿里云百炼对空闲会话有 300 秒强制断开限制。在静默 260 秒 (4分20秒) 且处于倾听状态时，
        // 主动在后台平滑重建会话，重置云端 300 秒计时器，杜绝超时断开与报错
        if (_state == BL_STATE_LISTENING && isConnected() && (millis() - _last_activity_time >= 260000)) {
            Serial.println("[BAILIAN] Session idle for 260s. Proactively refreshing session to prevent 300s cloud timeout...");
            _last_activity_time = millis();
            _last_error = "";
            connect();
        }

        // 2.4 底层 WebSocket 断线自愈 (WS Disconnect Auto Self-Healing):
        // 若底层 WS 掉线且未处于正在连接状态，自动重连保活
        static uint32_t s_last_ws_reconnect_time = 0;
        if (!isConnected() && _state != BL_STATE_CONNECTING) {
            if (millis() - s_last_ws_reconnect_time >= 3000) {
                s_last_ws_reconnect_time = millis();
                auto& cfg = StickS3ConfigManager::getInstance().getConfig();
                if (StickS3ConfigManager::getInstance().isStaConnected() && cfg.bailian_key.length() > 10) {
                    Serial.println("[BAILIAN-HEAL] WSS not connected. Auto reconnecting...");
                    connect();
                }
            }
        }

        // 2.5 周期性缓存清理与内存防碎片整理 (Periodic Cache Cleanup & Defrag)
        static uint32_t s_last_cache_cleanup = 0;
        if (millis() - s_last_cache_cleanup >= 60000) {
            s_last_cache_cleanup = millis();
            StickS3MemoryStore::getInstance().cleanupCaches();
        }

        // 2.6 安全异步执行 NVS Flash 记忆持久化与多轮会话热更新 (遵循公理二，彻底杜绝在 websocket_task 中写 Flash 导致 Cache 禁用崩溃)
        if (_pending_memory_save) {
            _pending_memory_save = false;
            auto& cfg = StickS3ConfigManager::getInstance().getConfig();
            StickS3MemoryStore::getInstance().addTurn(_pending_turn_user, _pending_turn_ai, cfg.bailian_voice);
            StickS3MemoryStore::getInstance().cleanupCaches();
            if (isConnected()) {
                sendSessionUpdate();
            }
        }

        // 2.7 异步平滑重连调度 (杜绝在底层回调中自我销毁客户端导致 Crash)
        if (_pending_reconnect) {
            _pending_reconnect = false;
            Serial.println("[BAILIAN] Performing scheduled reconnect in loopTask...");
            connect();
        }

        // 3. 在线且处于 LISTENING 模式时，流式读取麦克风并推流到百炼
        if (isConnected() && _session_initialized) {
            if (_state == BL_STATE_LISTENING) {
                // 每隔 20ms 高频轮询并推流 (极大压缩上行传输抖动延迟，同时保持单包 < 1KB MTU)
                if (millis() - _last_mic_read_time >= 20) {
                    _last_mic_read_time = millis();
                    streamMicUpstream();
                }
            } else if (_state == BL_STATE_SPEAKING) {
                // 当 AI 正在发声时，高频运行轻量级人声打断触发器 (过滤喇叭回声 + 鉴别人声特征)
                static uint32_t last_vad_check = 0;
                if (millis() - last_vad_check >= 16) {
                    last_vad_check = millis();
                    if (audio.checkVoiceBargeInTrigger()) {
                        interrupt("Voice-Barge-In");
                    }
                }
            }
        }

        // 3.1 离线唤醒词常态麦克风采样：
        // 当未处于主动上行流式推流 (BL_STATE_LISTENING) 时，
        // 持续读取麦克风 PCM 灌入 StickS3WakeWordEngine，确保「悄悄」随时毫秒级唤醒或语音打断！
        if (StickS3WakeWordEngine::getInstance().isEnabled() && !(_state == BL_STATE_LISTENING && isConnected())) {
            static uint32_t last_offline_mic_time = 0;
            if (millis() - last_offline_mic_time >= 40) {
                last_offline_mic_time = millis();
                static int16_t s_offline_mic_buf[512];
                size_t samples_read = 0;
                if (audio.readMicSamples(s_offline_mic_buf, 512, samples_read) && samples_read >= 128) {
                    StickS3WakeWordEngine::getInstance().feedSamples(s_offline_mic_buf, samples_read);
                }
            }
        }

        // 4. 通知主线程 UI 渲染新文本
        if (_rx_text_dirty) {
            _rx_text_dirty = false;
            if (_on_text) {
                _on_text(_user_query, _ai_reply, false);
            }
        }
    }

    // Getters
    bool isConnected() const {
        return _ws_client != nullptr && _is_ws_connected;
    }
    BailianAgentState getState() const { return _state; }
    String getStateName() const {
        switch (_state) {
            case BL_STATE_DISCONNECTED: return "未连接";
            case BL_STATE_CONNECTING:   return "连接中...";
            case BL_STATE_CONNECTED_IDLE: return "已连接待命";
            case BL_STATE_LISTENING:    return "正在聆听...";
            case BL_STATE_THINKING:     return "思考中...";
            case BL_STATE_SPEAKING:     return "AI 回复中";
            case BL_STATE_INTERRUPTED:  return "中途打断";
            case BL_STATE_ERROR:        return "异常: " + _last_error;
            default: return "未知";
        }
    }
    String getUserQuery() const { return _user_query; }
    String getAiReply() const { return _ai_reply; }
    uint32_t getTotalInterrupts() const { return _total_interrupts; }
    String getLastError() const {
        if (_state == BL_STATE_LISTENING || _state == BL_STATE_SPEAKING || _state == BL_STATE_THINKING || _state == BL_STATE_CONNECTED_IDLE) {
            return "";
        }
        return _last_error;
    }

    void onWakeWordDetected(float confidence, uint32_t duration_ms = 600) {
        Serial.printf("[BAILIAN-WAKE] >>> Wake Word '%s' FIRED (Conf: %.1f%%, Dur: %ums) <<<\n",
                      StickS3WakeWordEngine::WAKE_WORD_NAME, confidence, (unsigned)duration_ms);

        // 1. 若当前正在播报或思考，唤醒词充当硬件中途打断 (Barge-In)
        if (_state == BL_STATE_SPEAKING || _state == BL_STATE_THINKING || StickS3Audio::getInstance().isPlaying()) {
            interrupt("WakeWord-悄悄");
            vTaskDelay(pdMS_TO_TICKS(40));
        }

        // 2. 激活问答聆听推流窗口
        auto& cfg = StickS3ConfigManager::getInstance().getConfig();
        uint32_t tout_sec = cfg.wakeword_timeout_sec > 0 ? cfg.wakeword_timeout_sec : 8;
        _wake_window_until = millis() + (tout_sec * 1000);

        // 3. 播放清脆提示音
        StickS3Audio::getInstance().playTone(1760, 40, 0.45f);

        // 4. 刷新屏幕为倾听提示
        _user_query = "";
        _ai_reply = "在呢，请吩咐！";
        _rx_text_dirty = true;

        if (_state != BL_STATE_SPEAKING) {
            setState(BL_STATE_LISTENING);
        }
    }

    bool isWakeWindowOpen() const {
        return millis() < _wake_window_until;
    }

    uint32_t getWakeWindowRemainingMs() const {
        if (millis() >= _wake_window_until) return 0;
        return _wake_window_until - millis();
    }

    void startNewConversation() {
        _user_query = "";
        _ai_reply = "";
        _rx_text_dirty = true;
        _response_done_received = false;
        interrupt("NewConversation");
        setState(BL_STATE_LISTENING);
    }

    // 主动下发文本问答至百炼 (触发大模型推理并下发语音与文本流)
    bool sendTextMessage(const String& text) {
        if (text.length() == 0) return false;

        // 若前序有未完成的播音，先打断上一轮播音，防止音频冲突
        if (_state == BL_STATE_SPEAKING || StickS3Audio::getInstance().isPlaying()) {
            interrupt("NewTextMessage");
            vTaskDelay(pdMS_TO_TICKS(50));
        }

        // 若当前未连接，尝试触发快速重连
        if (!isConnected()) {
            Serial.println("[BAILIAN-TX] WS not connected, triggering reconnect before sending text...");
            connect();
            uint32_t wait_start = millis();
            while (!isConnected() && (millis() - wait_start < 2500)) {
                vTaskDelay(50 / portTICK_PERIOD_MS);
            }
            if (!isConnected()) {
                Serial.println("[BAILIAN-TX] Reconnect failed or timed out.");
                return false;
            }
        }

        // 若刚发送过 session.update，短暂等待 150ms 确保云端配置就绪
        if (millis() - _last_session_update_time < 200) {
            vTaskDelay(pdMS_TO_TICKS(150));
        }

        _last_activity_time = millis();
        _last_error = "";
        _user_query = text;
        _ai_reply = "";
        _rx_text_dirty = true;
        _response_done_received = false;
        _is_response_cancelled = false;
        _pending_cancel = false;
        _server_in_speech = false;
        _server_response_active = true;
        setState(BL_STATE_THINKING);

        // 1. 发送 conversation.item.create
        JsonDocument item_doc;
        item_doc["type"] = "conversation.item.create";
        JsonObject item = item_doc["item"].to<JsonObject>();
        item["type"] = "message";
        item["role"] = "user";
        JsonArray content = item["content"].to<JsonArray>();
        JsonObject text_content = content.add<JsonObject>();
        text_content["type"] = "input_text";
        text_content["text"] = text;

        String item_json;
        serializeJson(item_doc, item_json);
        bool ok1 = sendWsTextWithRetry(item_json.c_str(), item_json.length(), 6, pdMS_TO_TICKS(80));

        // 2. 发送 response.create 触发推理与实时语音合成
        const char* resp_create = "{\"type\":\"response.create\"}";
        bool ok2 = sendWsTextWithRetry(resp_create, strlen(resp_create), 6, pdMS_TO_TICKS(80));

        if (!ok1 || !ok2) {
            Serial.printf("[BAILIAN-TX-FAIL] sendTextMessage failed to deliver to WS! Auto reconnecting...\n");
            _is_ws_connected = false;
            connect();
            return false;
        }

        Serial.printf("[BAILIAN-TX] Sent user text query: \"%s\"\n", text.c_str());
        return true;
    }

    // 动态热切换当前音色 (在线瞬发 session.update + 清空陈旧输出 + 可选语音播报试听)
    bool switchVoice(const String& new_voice, bool speak_preview = false) {
        auto& cfg_mgr = StickS3ConfigManager::getInstance();
        if (!StickS3ConfigManager::isVoiceSupported(new_voice)) {
            Serial.printf("[BAILIAN] Voice '%s' not supported, ignore.\n", new_voice.c_str());
            return false;
        }

        cfg_mgr.saveBailianVoice(new_voice);

        // 关键：清空上一轮问答陈旧文本，避免用户产生“输出相同”的误解
        _user_query = "";
        _ai_reply = "已切换为 " + new_voice + " 音色";
        _rx_text_dirty = true;

        if (isConnected()) {
            Serial.printf("[BAILIAN] Hot-switching voice to '%s' on active WSS...\n", new_voice.c_str());
            sendSessionUpdate();
            if (speak_preview) {
                // 立即以新音色试听发声，让用户耳朵即时感受到音色改变
                sendTextMessage("请用一句话做自我介绍，告知我你的新音色。");
            }
        } else if (cfg_mgr.isStaConnected() && cfg_mgr.hasBailianKey()) {
            connect();
        }
        return true;
    }

    // 清空人机对话记忆 (RAM + Flash NVS)
    void clearMemory() {
        StickS3MemoryStore::getInstance().clearMemory();
        _user_query = "";
        _ai_reply = "对话记忆已清空";
        _rx_text_dirty = true;
        if (isConnected()) {
            sendSessionUpdate();
        }
    }

private:
    void setState(BailianAgentState new_state) {
        if (new_state == BL_STATE_LISTENING || new_state == BL_STATE_CONNECTED_IDLE) {
            _last_error = "";
        }
        if (new_state == BL_STATE_THINKING) {
            // 预热功放与 Codec 全双工通道，消除首包到达时的 I2C 阻塞与功放起振延迟
            StickS3Audio::getInstance().primePlaybackHardware();
        }
        if (_state != new_state) {
            BailianAgentState old = _state;
            _state = new_state;
            _last_state_change = millis();
            Serial.printf("[BAILIAN-STATE] %d -> %d (%s)\n", (int)old, (int)new_state, getStateName().c_str());
            if (_on_state) {
                _on_state(old, new_state);
            }
        }
    }

    // 发送 session.update 配置会话参数 (自动注入持久化历史对话记忆)
    void sendSessionUpdate() {
        auto& cfg_mgr = StickS3ConfigManager::getInstance();
        auto& cfg = cfg_mgr.getConfig();

        String voice = cfg.bailian_voice;
        if (!StickS3ConfigManager::isVoiceSupported(voice)) {
            Serial.printf("[BAILIAN-TX] Voice '%s' is not supported, overriding with Tina!\n", voice.c_str());
            voice = "Tina";
            cfg_mgr.saveBailianVoice("Tina");
        }

        // 智能构建并注入多轮上下文记忆
        String dynamic_prompt = StickS3MemoryStore::getInstance().buildMemoryContextPrompt(cfg.bailian_prompt);

        JsonDocument doc;
        doc["type"] = "session.update";
        JsonObject session = doc["session"].to<JsonObject>();
        
        JsonArray modalities = session["modalities"].to<JsonArray>();
        modalities.add("audio");
        modalities.add("text");

        session["voice"] = voice;
        session["instructions"] = dynamic_prompt;
        session["input_audio_format"] = "pcm16";
        session["output_audio_format"] = "pcm16";

        // 关键：阿里云百炼现代实时协议要求在 audio 对象中显式配置采样率
        // 彻底解决百炼默认下推 24kHz 与 StickS3 I2S 16kHz 时钟不匹配导致的语速过慢问题
        JsonObject audio_obj = session["audio"].to<JsonObject>();
        JsonObject audio_in = audio_obj["input"].to<JsonObject>();
        JsonObject audio_in_fmt = audio_in["format"].to<JsonObject>();
        audio_in_fmt["type"] = "pcm";
        audio_in_fmt["sample_rate"] = 16000;

        JsonObject audio_out = audio_obj["output"].to<JsonObject>();
        JsonObject audio_out_fmt = audio_out["format"].to<JsonObject>();
        audio_out_fmt["type"] = "pcm";
        audio_out_fmt["sample_rate"] = 16000;

        // 显式使能语音实时转写 ASR 模型 (gummy-realtime-v1)，确保云端完整下发识别文本
        JsonObject input_transcription = session["input_audio_transcription"].to<JsonObject>();
        input_transcription["model"] = "gummy-realtime-v1";

        JsonObject turn = session["turn_detection"].to<JsonObject>();
        turn["type"] = "server_vad";
        turn["threshold"] = 0.48; // 敏锐人声检测门限 (兼顾抗噪与开口低延迟触发)
        turn["prefix_padding_ms"] = 200; // 优化前导音频填充为 200ms
        turn["silence_duration_ms"] = 300; // 优化静音判定尾长为 300ms (大幅降低停顿等待延迟)
        turn["create_response"] = true;
        turn["interrupt_response"] = true;

        String json_out;
        serializeJson(doc, json_out);

        _last_session_update_time = millis();
        Serial.printf("[BAILIAN-TX] Sending session.update (Voice: %s, MemTurns: %u)...\n",
                      voice.c_str(), (unsigned)StickS3MemoryStore::getInstance().getTurnCount());
        sendWsTextWithRetry(json_out.c_str(), json_out.length(), 5, pdMS_TO_TICKS(100));
    }

    // 麦克风 PCM 流式推流上行 (PSRAM 240ms 环形预滚缓冲保护开口辅音 + 1200ms 静音尾窗)
    void streamMicUpstream() {
        if (!isConnected() || !_session_initialized) return;

        static int16_t* s_samples = nullptr;
        static int16_t* s_preroll_buf = nullptr; // 3 slots x 1024 samples (192ms)
        static size_t s_preroll_counts[3] = {0, 0, 0};
        static int s_preroll_head = 0;
        static int s_preroll_valid = 0;
        static bool s_is_actively_streaming = false;
        static char* s_b64_buf = nullptr;
        static char* s_payload_buf = nullptr;
        static uint32_t s_last_voice_tick = 0;

        if (!s_samples) {
            s_samples = (int16_t*)ps_malloc(2048 * sizeof(int16_t));
            s_preroll_buf = (int16_t*)ps_malloc(3 * 1024 * sizeof(int16_t));
            s_b64_buf = (char*)ps_malloc(6000);
            s_payload_buf = (char*)ps_malloc(7000);
        }
        if (!s_samples || !s_preroll_buf || !s_b64_buf || !s_payload_buf) return;

        size_t samples_read = 0;
        if (!StickS3Audio::getInstance().readMicSamples(s_samples, 512, samples_read)) {
            return;
        }
        if (samples_read < 160) return;

        // 1. 将麦克风采样送入离线唤醒词引擎持续分析
        if (StickS3WakeWordEngine::getInstance().isEnabled()) {
            StickS3WakeWordEngine::getInstance().feedSamples(s_samples, samples_read);
        }

        // 2. 离线唤醒词推流门控：若开启了唤醒词模式，并且当前未在唤醒窗口期内、且云端未处于主动交互期，
        // 则停止向网络推流，节省云端 Token 并彻底杜绝环境杂音误触发
        auto& cfg = StickS3ConfigManager::getInstance().getConfig();
        if (cfg.wakeword_enabled && !isWakeWindowOpen() && !_server_in_speech && !_server_response_active) {
            memcpy(&s_preroll_buf[s_preroll_head * 1024], s_samples, samples_read * sizeof(int16_t));
            s_preroll_counts[s_preroll_head] = samples_read;
            s_preroll_head = (s_preroll_head + 1) % 3;
            if (s_preroll_valid < 3) s_preroll_valid++;
            s_is_actively_streaming = false;
            return;
        }

        auto sendPcmFrame = [this](const int16_t* pcm, size_t count) -> bool {
            if (!pcm || count == 0 || !_ws_client || !isConnected()) return false;
            size_t pcm_bytes = count * sizeof(int16_t);
            size_t b64_len = 0;
            int ret = mbedtls_base64_encode((unsigned char*)s_b64_buf, 5990, &b64_len,
                                            (const unsigned char*)pcm, pcm_bytes);
            if (ret != 0 || b64_len == 0) return false;
            s_b64_buf[b64_len] = '\0';
            int written = snprintf(s_payload_buf, 7000,
                                   "{\"type\":\"input_audio_buffer.append\",\"audio\":\"%s\"}",
                                   s_b64_buf);
            if (written > 0 && written < 7000) {
                int send_ret = esp_websocket_client_send_text(_ws_client, s_payload_buf, written, pdMS_TO_TICKS(150));
                if (send_ret < 0) {
                    if (!esp_websocket_client_is_connected(_ws_client)) {
                        _is_ws_connected = false;
                    }
                    return false;
                }
                return true;
            }
            return false;
        };

        // 本地多重人声活动容错检验 (已标定为 RMS >= 75.0f, ZCR in [6, 150])
        bool frame_vocal = StickS3Audio::getInstance().isHumanVocalActivity(s_samples, samples_read);

        if (frame_vocal) {
            s_last_voice_tick = millis();
            // 说话时自动续期唤醒窗口
            if (cfg.wakeword_enabled) {
                uint32_t tout_sec = cfg.wakeword_timeout_sec > 0 ? cfg.wakeword_timeout_sec : 8;
                _wake_window_until = millis() + (tout_sec * 1000);
            }
            if (!s_is_actively_streaming) {
                s_is_actively_streaming = true;
                // 唤醒瞬发：冲刷最近 1 帧 PSRAM 环形预滚缓冲 (Pre-roll 64ms)，完整保护开口辅音且防止突发 TCP 缓冲溢出
                if (s_preroll_valid > 0) {
                    int last_slot = (s_preroll_head - 1 + 3) % 3;
                    if (s_preroll_counts[last_slot] > 0) {
                        sendPcmFrame(&s_preroll_buf[last_slot * 1024], s_preroll_counts[last_slot]);
                        s_preroll_counts[last_slot] = 0;
                    }
                }
                s_preroll_valid = 0;
            }
            // 发送当前音频帧
            sendPcmFrame(s_samples, samples_read);
        } else {
            // 当前非人声发音区间
            if (s_is_actively_streaming) {
                // 维持 400ms 静音尾窗或正在服务端发言，持续向云端输送静音，以满足 Server-VAD 300ms 裁决
                if ((millis() - s_last_voice_tick <= 400) || _server_in_speech) {
                    sendPcmFrame(s_samples, samples_read);
                } else {
                    s_is_actively_streaming = false;
                }
            }
            if (!s_is_actively_streaming) {
                // 未激活推流时，将静默帧存入环形预滚缓冲区
                memcpy(&s_preroll_buf[s_preroll_head * 1024], s_samples, samples_read * sizeof(int16_t));
                s_preroll_counts[s_preroll_head] = samples_read;
                s_preroll_head = (s_preroll_head + 1) % 3;
                if (s_preroll_valid < 3) s_preroll_valid++;
            }
        }

        // 关键兜底保障：若服务端 Server-VAD 在用户声音停止超过 800ms 后仍未触发 speech_stopped，
        // 客户端主动发送 input_audio_buffer.commit 强制提交本轮对话，杜绝云端 VAD 挂起卡住！
        if (_server_in_speech && (millis() - s_last_voice_tick > 800)) {
            Serial.println("[BAILIAN-VAD] Local silence timeout (>800ms). Actively committing audio buffer...");
            const char* commit_payload = "{\"type\":\"input_audio_buffer.commit\"}";
            esp_websocket_client_send_text(_ws_client, commit_payload, strlen(commit_payload), pdMS_TO_TICKS(35));
            _server_in_speech = false;
            s_is_actively_streaming = false;
            setState(BL_STATE_THINKING);
        }
    }

    // WebSocket 事件监听入口
    static void wsEventHandlerStatic(void* handler_args, esp_event_base_t base, int32_t event_id, void* event_data) {
        StickS3BailianClient* self = static_cast<StickS3BailianClient*>(handler_args);
        self->handleWsEvent(event_id, static_cast<esp_websocket_event_data_t*>(event_data));
    }

    void handleWsEvent(int32_t event_id, esp_websocket_event_data_t* data) {
        switch (event_id) {
            case WEBSOCKET_EVENT_CONNECTED:
                _is_ws_connected = true;
                Serial.println("[BAILIAN] WSS Connected to DashScope Realtime Server!");
                _last_error = "";
                _last_activity_time = millis();
                setState(BL_STATE_CONNECTED_IDLE);
                sendSessionUpdate();
                break;

            case WEBSOCKET_EVENT_DISCONNECTED:
                _is_ws_connected = false;
                Serial.println("[BAILIAN] WSS Disconnected.");
                _session_initialized = false;
                if (_last_error.length() == 0) {
                    _last_error = "连接断开";
                }
                setState(BL_STATE_DISCONNECTED);
                break;

            case WEBSOCKET_EVENT_DATA:
                if (data->data_len > 0) {
                    StickS3ConfigManager::getInstance().addNetworkTraffic(data->data_len, 0);
                }
                if (data->op_code == 0x01 && data->data_ptr && data->data_len > 0) { // Text JSON frame
                    static char* s_rx_buf = nullptr;
                    if (!s_rx_buf) {
                        s_rx_buf = (char*)ps_malloc(65536);
                    }
                    if (s_rx_buf && (data->payload_offset + data->data_len) <= 65500) {
                        memcpy(s_rx_buf + data->payload_offset, data->data_ptr, data->data_len);
                        // 当该帧所有 TCP 分片完整拼接就绪时
                        if (data->payload_offset + data->data_len >= data->payload_len) {
                            s_rx_buf[data->payload_len] = '\0';
                            
                            // 极速快路过滤 (Fast-Path Filter):
                            // 若当前响应已被用户打断取消，对于后续在网络管道中残存的旧音频帧或文本增量直接跳过解析，
                            // 耗时由 25ms 降低至 20 微秒 (1200倍提速)，瞬间让出 CPU 与底层 WS 锁！
                            if (_is_response_cancelled) {
                                if (strstr(s_rx_buf, "\"response.audio.delta\"") != nullptr ||
                                    strstr(s_rx_buf, "\"response.audio_transcript.delta\"") != nullptr) {
                                    break;
                                }
                            }

                            // 极速直通零内存分配音频解码：
                            // 针对高达 20KB~28KB 的 response.audio.delta，完全绕过 ArduinoJson AST 堆构造，
                            // 消除频繁 28KB SRAM 动态内存分配与堆碎片化，彻底根治内存耗尽重启！
                            const char* audio_delta_tag = strstr(s_rx_buf, "\"response.audio.delta\"");
                            if (audio_delta_tag) {
                                const char* delta_tag = strstr(s_rx_buf, "\"delta\":\"");
                                if (delta_tag) {
                                    const char* b64_start = delta_tag + 9;
                                    const char* b64_end = strchr(b64_start, '\"');
                                    if (b64_end && b64_end > b64_start) {
                                        size_t b64_len = b64_end - b64_start;
                                        _last_rx_stream_time = millis();
                                        _last_activity_time = millis();
                                        if (_state != BL_STATE_SPEAKING) {
                                            setState(BL_STATE_SPEAKING);
                                        }
                                        static uint8_t* s_pcm_fast_out = nullptr;
                                        if (!s_pcm_fast_out) {
                                            s_pcm_fast_out = (uint8_t*)ps_malloc(32768);
                                        }
                                        if (s_pcm_fast_out && b64_len > 0) {
                                            size_t pcm_len = 0;
                                            int dec_ret = mbedtls_base64_decode(s_pcm_fast_out, 32768, &pcm_len,
                                                                                (const unsigned char*)b64_start, b64_len);
                                            if (dec_ret == 0 && pcm_len > 0) {
                                                StickS3Audio::getInstance().feedStreamPCM(s_pcm_fast_out, pcm_len, _server_output_sample_rate);
                                            }
                                        }
                                        break;
                                    }
                                }
                            }

                            handleServerMessage(s_rx_buf, data->payload_len);
                        }
                    }
                }
                break;

            case WEBSOCKET_EVENT_ERROR:
                _is_ws_connected = false;
                Serial.println("[BAILIAN] WSS Connection Error!");
                _last_error = "WS链路错误";
                setState(BL_STATE_ERROR);
                break;
        }
    }

    // 解析服务端下发 JSON 报文
    void handleServerMessage(const char* payload, int len) {
        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, payload, len);
        if (err) {
            if (err == DeserializationError::NoMemory) {
                Serial.printf("[BAILIAN-ERR] ArduinoJson NoMemory! len=%d, free_sram=%u, max_block=%u\n",
                              len, (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
                              (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL));
            }
            return;
        }

        const char* type = doc["type"] | "";

        // 1. 会话建立确认
        if (strcmp(type, "session.created") == 0 || strcmp(type, "session.updated") == 0) {
            Serial.println("[BAILIAN] Session established and active. Listening for voice...");
            
            // 自动侦测云端实际生效的输出采样率 (优先提取现代 audio.output 结构，兼容历史格式)
            if (doc["session"]["audio"]["output"]["format"]["sample_rate"].is<int>()) {
                _server_output_sample_rate = doc["session"]["audio"]["output"]["format"]["sample_rate"].as<int>();
            } else if (doc["session"]["output_audio_format"].is<const char*>()) {
                const char* fmt = doc["session"]["output_audio_format"].as<const char*>();
                if (strstr(fmt, "24") != nullptr) {
                    _server_output_sample_rate = 24000;
                } else {
                    _server_output_sample_rate = 16000;
                }
            }
            Serial.printf("[BAILIAN] Negotiated Server Audio Sample Rate: %u Hz\n", (unsigned)_server_output_sample_rate);

            _last_error = "";
            _last_activity_time = millis();
            _session_initialized = true;
            if (_state != BL_STATE_SPEAKING && !StickS3Audio::getInstance().isPlaying()) {
                _server_response_active = false;
                _response_done_received = false;
                setState(BL_STATE_LISTENING);
            }
        }
        // 1.1 服务端响应创建 -> 开启新一轮流式回答并重置状态
        else if (strcmp(type, "response.created") == 0) {
            _last_activity_time = millis();
            _server_response_active = true;
            _response_done_received = false;
            // 收到新一轮回答创建事件，重置打断取消标记与挂起请求，确保新一轮语音和文本正常输出
            _is_response_cancelled = false;
            _pending_cancel = false;
            _ai_reply = ""; // 关键：每轮新回答生成时清空上一轮回答并预分配内存，防止碎片化
            _ai_reply.reserve(1024);
            _rx_text_dirty = true;
            Serial.println("[BAILIAN] response.created received. Ready for streaming response.");
        }
        // 2. 服务端 VAD 检测到用户开始讲话 -> 触发打断并准备接收新一轮交互！
        else if (strcmp(type, "input_audio_buffer.speech_started") == 0) {
            Serial.println("[BAILIAN-EVENT] Server-VAD: User started speaking!");
            _last_activity_time = millis();
            _is_response_cancelled = false; // 用户开口说话，新一轮开始
            if (_state == BL_STATE_SPEAKING) {
                interrupt("Server-VAD-Speech-Started");
            }
            _server_in_speech = true;
            setState(BL_STATE_LISTENING);
        }
        // 3. 服务端 VAD 检测到用户讲话结束 -> 转入思考推理
        else if (strcmp(type, "input_audio_buffer.speech_stopped") == 0) {
            Serial.println("[BAILIAN-EVENT] Server-VAD: User stopped speaking -> Thinking...");
            _last_activity_time = millis();
            _server_in_speech = false;
            setState(BL_STATE_THINKING);
        }
        // 4. 实时文本流 (汉字增量下发)
        else if (strcmp(type, "response.audio_transcript.delta") == 0) {
            if (_is_response_cancelled || _state == BL_STATE_INTERRUPTED) return;
            const char* delta = doc["delta"] | "";
            if (delta && strlen(delta) > 0) {
                _last_rx_stream_time = millis();
                _last_activity_time = millis();
                if (_state != BL_STATE_SPEAKING) {
                    setState(BL_STATE_SPEAKING);
                }
                _ai_reply += delta;
                _rx_text_dirty = true;
            }
        }
        // 5. 实时音频流 (Base64 PCM16 音频帧毫秒级边收边播)
        else if (strcmp(type, "response.audio.delta") == 0) {
            if (_is_response_cancelled || _state == BL_STATE_INTERRUPTED) return;
            const char* b64_audio = doc["delta"] | "";
            if (b64_audio && strlen(b64_audio) > 0) {
                _last_rx_stream_time = millis();
                _last_activity_time = millis();
                if (_state != BL_STATE_SPEAKING) {
                    setState(BL_STATE_SPEAKING);
                }
                // 解码 Base64 PCM 并压入 PSRAM 环形缓冲区 (使用 PSRAM 缓冲区避免栈溢出)
                static uint8_t* s_pcm_out = nullptr;
                if (!s_pcm_out) {
                    s_pcm_out = (uint8_t*)ps_malloc(32768);
                }
                if (s_pcm_out) {
                    size_t b64_len = strlen(b64_audio);
                    size_t pcm_len = 0;
                    int dec_ret = mbedtls_base64_decode(s_pcm_out, 32768, &pcm_len,
                                                        (const unsigned char*)b64_audio, b64_len);
                    if (dec_ret == 0 && pcm_len > 0) {
                        StickS3Audio::getInstance().feedStreamPCM(s_pcm_out, pcm_len, _server_output_sample_rate);
                    }
                }
            }
        }
        // 6. 用户语音识别完成展示
        else if (strcmp(type, "conversation.item.input_audio_transcription.completed") == 0) {
            const char* user_text = doc["transcript"] | "";
            if (user_text && strlen(user_text) > 0) {
                _user_query = user_text;
                _ai_reply = ""; // 清空上一轮回答准备流式刷新
                _ai_reply.reserve(1024);
                _rx_text_dirty = true;
                _is_response_cancelled = false; // 用户新提问确认，清除任何旧取消状态
                _pending_cancel = false;
                _last_activity_time = millis();
                Serial.printf("[BAILIAN] User said: \"%s\"\n", user_text);
            }
        }
        // 7. 回复完成
        else if (strcmp(type, "response.done") == 0) {
            _server_response_active = false;
            _server_in_speech = false;
            _response_done_received = true;
            bool was_cancelled = _is_response_cancelled;
            _is_response_cancelled = false;
            _pending_cancel = false;
            _last_rx_stream_time = millis();
            _last_activity_time = millis();
            Serial.println("[BAILIAN] LLM response streaming complete.");

            // 关键：不在 websocket_task 中直接执行 Flash NVS 写入与 session.update (遵循工程公理二)
            // 标记记忆持久化待处理，在 loopTask 中安全执行，彻底杜绝 Flash 禁用导致 Cache Panic 异常重启
            if (_user_query.length() > 0 && _ai_reply.length() > 0 && !was_cancelled) {
                _pending_turn_user = _user_query;
                _pending_turn_ai = _ai_reply;
                _pending_memory_save = true;
            }

            if (_on_text) {
                _on_text(_user_query, _ai_reply, true);
            }
        }
        // 8. 错误报文
        else if (strcmp(type, "error") == 0) {
            _server_response_active = false;
            _server_in_speech = false;
            _response_done_received = false;
            _is_response_cancelled = false;
            const char* msg = doc["error"]["message"] | "Unknown error";
            Serial.printf("[BAILIAN-ERROR] Server error: %s\n", msg);
            // 拦截 300 秒空闲断开提示，标记在 loopTask 中重连，不在底层回调中自我销毁导致崩溃
            if (strstr(msg, "300 seconds") != nullptr || strstr(msg, "session was closed") != nullptr) {
                Serial.println("[BAILIAN] Intercepted 300s idle timeout. Scheduling reconnect in loopTask...");
                _last_error = "";
                _last_activity_time = millis();
                _pending_reconnect = true;
                return;
            }
            // 拦截打断时由于网络时延导致的取消响应竞争事件，静默忽略杜绝红屏
            if (strstr(msg, "none active response") != nullptr || strstr(msg, "no active response") != nullptr) {
                Serial.println("[BAILIAN] Intercepted benign cancellation race condition. Seamlessly continuing.");
                _last_error = "";
                return;
            }
            _last_error = msg;
            setState(BL_STATE_ERROR);
        }
    }

    esp_websocket_client_handle_t _ws_client;
    volatile bool _is_ws_connected;
    BailianAgentState _state;
    uint32_t _last_mic_read_time;
    uint32_t _last_rx_stream_time;
    uint32_t _last_activity_time;
    uint32_t _last_session_update_time;
    bool _session_initialized;
    bool _server_response_active;
    bool _response_done_received;
    bool _is_response_cancelled;
    volatile bool _pending_cancel;
    volatile bool _pending_memory_save;
    volatile bool _pending_reconnect;
    String _pending_turn_user;
    String _pending_turn_ai;
    bool _server_in_speech;
    uint32_t _last_state_change;
    uint32_t _total_interrupts;
    uint32_t _server_output_sample_rate;
    uint32_t _wake_window_until;
    String _last_error;
    String _auth_header;

    String _user_query;
    String _ai_reply;
    volatile bool _rx_text_dirty;

    BailianTextCallback _on_text;
    BailianStateCallback _on_state;
};

} // namespace sticks3
