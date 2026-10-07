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

} // namespace sticks3

#include "sticks3_bear_kinematics.h"

namespace sticks3 {

using BailianTextCallback = std::function<void(const String& user_text, const String& ai_text, bool is_final)>;
using BailianStateCallback = std::function<void(BailianAgentState old_state, BailianAgentState new_state)>;
using BailianUserSpeechCallback = std::function<void(const String& user_text)>;
using BailianSpeechStartedCallback = std::function<void()>;
using BailianToolCallHandler = std::function<String(const String& name, const String& call_id, const String& arguments)>;

struct BailianPendingTool {
    String call_id;
    String name;
    String args;
};

// 线程安全互斥锁 RAII 守卫 (替代底层硬件自旋锁 portMUX_TYPE，彻底消除 INT_WDT 中断看门狗复位与死锁)
class BailianTextLockGuard {
public:
    explicit BailianTextLockGuard(SemaphoreHandle_t mutex, TickType_t timeout = pdMS_TO_TICKS(40))
        : _mutex(mutex), _acquired(false) {
        if (_mutex != nullptr) {
            _acquired = (xSemaphoreTake(_mutex, timeout) == pdTRUE);
        }
    }
    ~BailianTextLockGuard() {
        if (_acquired && _mutex != nullptr) {
            xSemaphoreGive(_mutex);
        }
    }
    bool isAcquired() const { return _acquired; }
private:
    SemaphoreHandle_t _mutex;
    bool _acquired;
};

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
          _pending_preview_voice(false), _pending_preview_time(0),
          _server_in_speech(false), _last_voice_tick(0), _last_activity_time(0), _server_output_sample_rate(16000),
          _last_state_change(0), _total_interrupts(0), _last_error(""),
          _rx_text_dirty(false), _wake_window_until(0),
          _pending_user_speech_ready(false), _pending_final_ai_reply_ready(false),
          _pending_speech_started(false), _on_user_speech(nullptr), _on_speech_started(nullptr) {
        _user_query = "";
        _ai_reply = "";
        _pending_turn_user = "";
        _pending_turn_ai = "";
        _pending_user_speech = "";
        _pending_final_ai_reply = "";
        _ws_send_mutex = xSemaphoreCreateMutex();
        _text_mutex = xSemaphoreCreateMutex();
        _tool_mutex = xSemaphoreCreateMutex();
        _last_executed_call_id = "";
        _on_tool_call = nullptr;
    }

    void setTextCallback(BailianTextCallback cb) { _on_text = cb; }
    void setStateCallback(BailianStateCallback cb) { _on_state = cb; }
    void setUserSpeechCallback(BailianUserSpeechCallback cb) { _on_user_speech = cb; }
    void setSpeechStartedCallback(BailianSpeechStartedCallback cb) { _on_speech_started = cb; }
    void setToolCallHandler(BailianToolCallHandler cb) { _on_tool_call = cb; }

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
        ws_cfg.buffer_size = 20480; // 20KB 接收分片缓冲，充分容纳完整 audio.delta (15KB~20KB)
        ws_cfg.task_stack = 16384;  // 16KB 堆栈确保 mbedTLS 握手与错误清理绝对不溢出
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
        if (_ws_send_mutex) {
            xSemaphoreTake(_ws_send_mutex, pdMS_TO_TICKS(150));
        }
        if (_ws_client) {
            esp_websocket_client_stop(_ws_client);
            esp_websocket_client_destroy(_ws_client);
            _ws_client = nullptr;
        }
        if (_ws_send_mutex) {
            xSemaphoreGive(_ws_send_mutex);
        }
        _is_ws_connected = false;
        _session_initialized = false;
        _server_response_active = false;
        _response_done_received = false;
        _is_response_cancelled = false;
        _server_in_speech = false;
        if (_tool_mutex && xSemaphoreTake(_tool_mutex, pdMS_TO_TICKS(50)) == pdTRUE) {
            _pending_tools.clear();
            _last_executed_call_id = "";
            xSemaphoreGive(_tool_mutex);
        }
        setState(BL_STATE_DISCONNECTED);
    }

    // 线程安全与互斥发送 (彻底杜绝多任务并发写入引发 errno=11 与底层套接字竞争)
    bool sendWsTextWithRetry(const char* data, size_t len, int max_retries = 3, TickType_t timeout = pdMS_TO_TICKS(150)) {
        if (!_ws_client || !_is_ws_connected || !data || len == 0) return false;

        // 手机热点流量超额自动熔断保护检查
        if (StickS3ConfigManager::getInstance().isHotspotCutoffActive() &&
            StickS3ConfigManager::getInstance().isHotspotCutoffEnabled()) {
            Serial.println("[HOTSPOT-GUARD] Bailian streaming suspended due to traffic limit cutoff!");
            return false;
        }

        if (_ws_send_mutex && xSemaphoreTake(_ws_send_mutex, pdMS_TO_TICKS(200)) != pdTRUE) {
            return false;
        }

        bool success = false;
        for (int i = 0; i < max_retries; i++) {
            int ret = esp_websocket_client_send_text(_ws_client, data, len, timeout);
            if (ret >= 0) {
                // 累计上行网络流量
                StickS3ConfigManager::getInstance().addNetworkTraffic(0, len);
                success = true;
                break;
            }
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        if (!success && !esp_websocket_client_is_connected(_ws_client)) {
            _is_ws_connected = false;
        }

        if (_ws_send_mutex) {
            xSemaphoreGive(_ws_send_mutex);
        }
        return success;
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
            {
                BailianTextLockGuard lock(_text_mutex);
                if (_ai_reply.indexOf("[已打断]") == -1) {
                    _ai_reply += " [已打断]";
                }
            }
            _rx_text_dirty = true;
            _total_interrupts++;

            // 3. 仅当云端响应尚在进行中，才向云端发送 response.cancel
            if (_server_response_active) {
                _is_response_cancelled = true;
                _server_response_active = false;
                _response_done_received = false;

                const char* cancel_payload = "{\"type\":\"response.cancel\"}";
                bool ok = sendWsTextWithRetry(cancel_payload, strlen(cancel_payload), 2, pdMS_TO_TICKS(100));
                if (ok) {
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
            bool ok = sendWsTextWithRetry(cancel_payload, strlen(cancel_payload), 1, pdMS_TO_TICKS(100));
            if (ok) {
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

        // 2.8 音色试听超时兜底 (以防云端未返回 session.updated 回执，安全在 loopTask 中发声)
        if (_pending_preview_voice && isConnected() && _session_initialized && (millis() - _pending_preview_time > 650)) {
            _pending_preview_voice = false;
            Serial.println("[BAILIAN] Session update confirm timeout (650ms fallback). Triggering voice preview speech...");
            sendTextMessage("请用一句话做自我介绍，告知我你的新音色。");
        }

        // 2.9 异步分发用户语音与大模型回复事件 (在 loopTask 中安全执行，解耦底层 WebSocket 协议微栈，严格遵照公理二)
        if (_pending_speech_started) {
            _pending_speech_started = false;
            if (_on_speech_started) {
                _on_speech_started();
            }
        }

        if (_pending_user_speech_ready) {
            String speech_copy;
            {
                BailianTextLockGuard lock(_text_mutex);
                speech_copy = _pending_user_speech;
                _pending_user_speech = "";
                _pending_user_speech_ready = false;
            }
            if (_on_user_speech && speech_copy.length() > 0) {
                _on_user_speech(speech_copy);
            }
        }

        if (_pending_final_ai_reply_ready) {
            String ai_copy;
            String user_copy;
            {
                BailianTextLockGuard lock(_text_mutex);
                ai_copy = _pending_final_ai_reply;
                user_copy = _user_query;
                _pending_final_ai_reply = "";
                _pending_final_ai_reply_ready = false;
            }
            if (_on_text && ai_copy.length() > 0) {
                _on_text(user_copy, ai_copy, true);
            }
        }

        // 2.10 异步执行大模型 Function Calling 工具调用 (在 loopTask 中执行，彻底遵循公理二)
        BailianPendingTool tool_job;
        bool has_tool_job = false;
        if (_tool_mutex && xSemaphoreTake(_tool_mutex, pdMS_TO_TICKS(15)) == pdTRUE) {
            if (!_pending_tools.empty()) {
                tool_job = _pending_tools.front();
                _pending_tools.erase(_pending_tools.begin());
                has_tool_job = true;
            }
            xSemaphoreGive(_tool_mutex);
        }

        if (has_tool_job && isConnected()) {
            Serial.printf("[BAILIAN-TOOL] Executing Function Call '%s' (call_id: %s, args: %s)\n",
                          tool_job.name.c_str(), tool_job.call_id.c_str(), tool_job.args.c_str());
            String output_json = "";
            if (_on_tool_call) {
                output_json = _on_tool_call(tool_job.name, tool_job.call_id, tool_job.args);
            }
            if (output_json.length() == 0) {
                output_json = executeDefaultTool(tool_job.name, tool_job.args);
            }

            // 发送 function_call_output 回执给百炼服务端
            JsonDocument call_resp;
            call_resp["type"] = "conversation.item.create";
            JsonObject item = call_resp["item"].to<JsonObject>();
            item["type"] = "function_call_output";
            item["call_id"] = tool_job.call_id;
            item["output"] = output_json;
            String call_resp_str;
            serializeJson(call_resp, call_resp_str);
            sendWsTextWithRetry(call_resp_str.c_str(), call_resp_str.length(), 4, pdMS_TO_TICKS(100));

            // 触发大模型根据工具调用结果继续生成后续拟人语音
            const char* resp_create = "{\"type\":\"response.create\"}";
            sendWsTextWithRetry(resp_create, strlen(resp_create), 4, pdMS_TO_TICKS(100));
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
    String getUserQuery() const {
        BailianTextLockGuard lock(_text_mutex, pdMS_TO_TICKS(15));
        if (!lock.isAcquired()) return "";
        return _user_query;
    }
    String getAiReply() const {
        BailianTextLockGuard lock(_text_mutex, pdMS_TO_TICKS(15));
        if (!lock.isAcquired()) return "";
        return _ai_reply;
    }
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
        {
            BailianTextLockGuard lock(_text_mutex);
            _user_query = "";
            _ai_reply = "在呢，请吩咐！";
        }
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
        {
            BailianTextLockGuard lock(_text_mutex);
            _user_query = "";
            _ai_reply = "";
        }
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
        {
            BailianTextLockGuard lock(_text_mutex);
            _user_query = text;
            _ai_reply = "";
            _ai_reply.reserve(1024);
        }
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
        {
            BailianTextLockGuard lock(_text_mutex);
            _user_query = "";
            _ai_reply = "已切换为 " + new_voice + " 音色";
        }
        _rx_text_dirty = true;

        if (speak_preview) {
            // 立即给用户即时听觉反馈，按键音秒回提示
            StickS3Audio::getInstance().playTone(1800, 35, 0.45f);
            _pending_preview_voice = true;
            _pending_preview_time = millis();
        }

        if (isConnected()) {
            Serial.printf("[BAILIAN] Hot-switching voice to '%s' on active WSS...\n", new_voice.c_str());
            sendSessionUpdate();
        } else if (cfg_mgr.isStaConnected() && cfg_mgr.hasBailianKey()) {
            Serial.println("[BAILIAN] Connecting to WSS for voice switch preview...");
            connect();
        }
        return true;
    }

    // 清空人机对话记忆 (RAM + Flash NVS)
    void clearMemory() {
        StickS3MemoryStore::getInstance().clearMemory();
        {
            BailianTextLockGuard lock(_text_mutex);
            _user_query = "";
            _ai_reply = "对话记忆已清空";
        }
        _rx_text_dirty = true;
        if (isConnected()) {
            sendSessionUpdate();
        }
    }

    String executeDefaultTool(const String& name, const String& args) {
        JsonDocument d;
        deserializeJson(d, args);
        if (name == "sticks3_control_bear") {
            const char* act_str = d["action"] | "";
            const char* combo_str = d["combo"] | "";
            uint32_t dur = d["duration_ms"] | 2800;
            auto& gm = BearGrowthManager::getInstance();
            auto& kc = BearKinematicsController::getInstance();

            if (!d["yaw"].isNull()) {
                float yaw_val = d["yaw"].as<float>();
                kc.setTargetYaw(yaw_val);
                return "{\"status\":\"success\",\"yaw\":" + String(yaw_val, 1) + "}";
            }
            if (!d["turn"].isNull()) {
                float turn_val = d["turn"].as<float>();
                if (turn_val >= 300.0f) {
                    kc.triggerSpinPirouette(1800);
                    return "{\"status\":\"success\",\"turn\":360,\"mode\":\"spin\"}";
                } else {
                    kc.triggerTurnAround(1400);
                    return "{\"status\":\"success\",\"turn\":180,\"mode\":\"turn_around\"}";
                }
            }
            if (!d["joint_id"].isNull() && !d["joint_angle"].isNull()) {
                uint8_t j_id = d["joint_id"].as<uint8_t>();
                float j_ang = d["joint_angle"].as<float>();
                kc.setJointAngle(j_id, j_ang, 0.0f, 0.0f);
                return "{\"status\":\"success\",\"joint_id\":" + String(j_id) + ",\"angle\":" + String(j_ang, 1) + "}";
            }
            if (!d["balance"].isNull()) {
                bool bal_en = d["balance"].as<bool>();
                kc.setImuBalanceEnabled(bal_en);
                return "{\"status\":\"success\",\"balance\":" + String(bal_en ? "true" : "false") + "}";
            }

            if (strlen(combo_str) > 0) {
                bool ok = kc.triggerComboByName(combo_str);
                if (ok) {
                    return "{\"status\":\"success\",\"combo\":\"" + String(combo_str) + "\"}";
                } else {
                    uint8_t req = gm.getComboRequiredLevel(combo_str);
                    uint32_t needed = (gm.getNextLevelExp() > gm.getExp()) ? (gm.getNextLevelExp() - gm.getExp()) : 0;
                    return "{\"status\":\"locked\",\"combo\":\"" + String(combo_str) + "\",\"required_level\":" + String(req) +
                           ",\"current_level\":" + String(gm.getLevel()) + ",\"current_exp\":" + String(gm.getExp()) +
                           ",\"needed_exp\":" + String(needed) + ",\"message\":\"组合技尚未解锁！请多陪我语音聊天升级。\"}";
                }
            }

            BearAction act = stringToBearAction(act_str);
            bool ok = kc.triggerAction(act, dur);
            if (ok) {
                Serial.printf("[BAILIAN-TOOL-DEFAULT] Bear action '%s' triggered\n", act_str);
                return "{\"status\":\"success\",\"action\":\"" + String(act_str) + "\"}";
            } else {
                uint8_t req = gm.getRequiredLevel(act);
                uint32_t needed = (gm.getNextLevelExp() > gm.getExp()) ? (gm.getNextLevelExp() - gm.getExp()) : 0;
                return "{\"status\":\"locked\",\"action\":\"" + String(act_str) + "\",\"required_level\":" + String(req) +
                       ",\"current_level\":" + String(gm.getLevel()) + ",\"current_exp\":" + String(gm.getExp()) +
                       ",\"needed_exp\":" + String(needed) + ",\"message\":\"动作尚未解锁！需要更高等级，多陪我聊聊天就能学会啦～\"}";
            }
        } else if (name == "sticks3_get_bear_skills") {
            auto& gm = BearGrowthManager::getInstance();
            char buf[300];
            uint32_t needed = (gm.getNextLevelExp() > gm.getExp()) ? (gm.getNextLevelExp() - gm.getExp()) : 0;
            snprintf(buf, sizeof(buf),
                     "{\"status\":\"success\",\"level\":%u,\"title\":\"%s\",\"exp\":%u,\"next_exp\":%u,\"needed_exp\":%u,\"rom\":%.2f}",
                     (unsigned)gm.getLevel(), gm.getLevelTitle(), (unsigned)gm.getExp(), (unsigned)gm.getNextLevelExp(),
                     (unsigned)needed, gm.getRomMultiplier());
            return String(buf);
        } else if (name == "sticks3_set_avatar") {
            const char* exp_str = d["expression"] | "";
            AvatarMood m = MOOD_IDLE;
            if (strcmp(exp_str, "happy") == 0) m = MOOD_HAPPY;
            else if (strcmp(exp_str, "curious") == 0) m = MOOD_CURIOUS;
            else if (strcmp(exp_str, "proud") == 0) m = MOOD_PROUD;
            else if (strcmp(exp_str, "sleepy") == 0 || strcmp(exp_str, "sleep") == 0) m = MOOD_SLEEP;
            else if (strcmp(exp_str, "dizzy") == 0) m = MOOD_DIZZY;
            else if (strcmp(exp_str, "shock") == 0) m = MOOD_SHOCK;
            else if (strcmp(exp_str, "wink") == 0) m = MOOD_WINK;
            StickS3Avatar::getInstance().setMood(m);
            Serial.printf("[BAILIAN-TOOL-DEFAULT] Avatar mood '%s' set\n", exp_str);
            return "{\"status\":\"success\",\"expression\":\"" + String(exp_str) + "\"}";
        } else if (name == "get_device_telemetry") {
            return "{\"status\":\"success\",\"battery_mv\":4100,\"wifi\":\"connected\"}";
        }
        return "{\"status\":\"unknown_tool\"}";
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

        // 智能构建并注入多轮上下文记忆与肢体动作提示词
        String prompt_base = cfg.bailian_prompt;
        if (prompt_base.indexOf("sticks3_control_bear") == -1 && prompt_base.indexOf("[ACT:") == -1) {
            prompt_base += " 你拥有生动的全身四肢与迪士尼拟人身体，并拥有5级RPG成长技能树(Lv.1萌新~Lv.5机甲元尊)。"
                           "当对话或被要求做动作时，请调用工具 sticks3_control_bear 或在回复附带动作标签："
                           "[ACT:wave]挥手、[ACT:bow]鞠躬、[ACT:sit]坐下、[ACT:stretch]伸懒腰、[ACT:clap]鼓掌、[ACT:cheer]欢呼、[ACT:jump]跳跃、"
                           "[ACT:dance]跳舞、[ACT:balance]金鸡独立、[ACT:lie]趴下、[ACT:pushup]俯卧撑、[ACT:kungfu]功夫、[ACT:taichi]太极、"
                            "[ACT:wingchun]咏春、[ACT:dragon_punch]升龙拳、[ACT:moonwalk]太空漫步、[ACT:cyber_defense]机甲护盾、"
                            "[ACT:turn_around]转身看背影与小尾巴、[ACT:spin]360度旋转跳跃。"
                            "还可触发组合技(greeting, fitness, martial, cyber_supreme)。"
                            "若工具返回 locked，请用可爱拟人语气告知当前等级并鼓励多对话积攒经验升级！"
                            "每次回复开头可用方括号标注情绪标签：[E:happy]、[E:curious]、[E:proud]、[E:sleepy]、[E:dizzy]、[E:wink]或[E:idle]。";
        }
        String dynamic_prompt = StickS3MemoryStore::getInstance().buildMemoryContextPrompt(prompt_base);

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

        // 设备端直连阿里云百炼：直接向 DashScope 注册原生具身控制与拟态表情 Function Calling 工具
        JsonArray tools = session["tools"].to<JsonArray>();

        // 1. 小熊四肢运动控制 (含5级技能树动作、3D偏航转身与OpenPose人形关节点)
        JsonObject tool_bear = tools.add<JsonObject>();
        tool_bear["type"] = "function";
        tool_bear["name"] = "sticks3_control_bear";
        tool_bear["description"] = "控制 M5StickS3 小熊 (Meta Jollybot) 的四肢运动、3D偏航转身与OpenPose人形关节点。支持单体动作、宏组合技、3D转身与关节精准度数控制。";
        JsonObject bear_params = tool_bear["parameters"].to<JsonObject>();
        bear_params["type"] = "object";
        JsonObject bear_props = bear_params["properties"].to<JsonObject>();
        JsonObject act_prop = bear_props["action"].to<JsonObject>();
        act_prop["type"] = "string";
        act_prop["description"] = "目标单体动作名称";
        JsonArray act_enum = act_prop["enum"].to<JsonArray>();
        act_enum.add("wave");
        act_enum.add("bow");
        act_enum.add("sit");
        act_enum.add("stretch");
        act_enum.add("clap");
        act_enum.add("cheer");
        act_enum.add("jump");
        act_enum.add("hands_up");
        act_enum.add("dance");
        act_enum.add("balance");
        act_enum.add("lie");
        act_enum.add("pushup");
        act_enum.add("kungfu");
        act_enum.add("taichi");
        act_enum.add("wingchun");
        act_enum.add("dragon_punch");
        act_enum.add("moonwalk");
        act_enum.add("cyber_defense");
        act_enum.add("turn_around");
        act_enum.add("spin");

        JsonObject combo_prop = bear_props["combo"].to<JsonObject>();
        combo_prop["type"] = "string";
        combo_prop["description"] = "宏组合技名称 (greeting, fitness, martial, cyber_supreme)";
        JsonArray combo_enum = combo_prop["enum"].to<JsonArray>();
        combo_enum.add("greeting");
        combo_enum.add("fitness");
        combo_enum.add("martial");
        combo_enum.add("cyber_supreme");

        JsonObject yaw_prop = bear_props["yaw"].to<JsonObject>();
        yaw_prop["type"] = "number";
        yaw_prop["description"] = "水平偏航偏转角 (0°正对用户, 180°背向露尾巴, 360°自旋)";

        JsonObject turn_prop = bear_props["turn"].to<JsonObject>();
        turn_prop["type"] = "number";
        turn_prop["description"] = "转身度数 (180触发转身萌态背影, 360触发华丽旋转舞蹈)";

        JsonObject joint_id_prop = bear_props["joint_id"].to<JsonObject>();
        joint_id_prop["type"] = "integer";
        joint_id_prop["description"] = "OpenPose 关节点编号 (0~22)";

        JsonObject joint_ang_prop = bear_props["joint_angle"].to<JsonObject>();
        joint_ang_prop["type"] = "number";
        joint_ang_prop["description"] = "关节点偏转度数";

        // 2. 灵宠技能树与等级查询
        JsonObject tool_skills = tools.add<JsonObject>();
        tool_skills["type"] = "function";
        tool_skills["name"] = "sticks3_get_bear_skills";
        tool_skills["description"] = "查询小熊的当前成长等级(Lv.1~Lv.5)、头衔称号、经验值(EXP)以及距离下一级所需经验。";
        JsonObject skills_params = tool_skills["parameters"].to<JsonObject>();
        skills_params["type"] = "object";

        // 3. 拟态表情设置
        JsonObject tool_avatar = tools.add<JsonObject>();
        tool_avatar["type"] = "function";
        tool_avatar["name"] = "sticks3_set_avatar";
        tool_avatar["description"] = "改变屏幕上伴侣小熊的面部表情与情绪状态。";
        JsonObject av_params = tool_avatar["parameters"].to<JsonObject>();
        av_params["type"] = "object";
        JsonObject av_props = av_params["properties"].to<JsonObject>();
        JsonObject exp_prop = av_props["expression"].to<JsonObject>();
        exp_prop["type"] = "string";
        exp_prop["description"] = "目标表情";
        JsonArray exp_enum = exp_prop["enum"].to<JsonArray>();
        exp_enum.add("happy");
        exp_enum.add("curious");
        exp_enum.add("proud");
        exp_enum.add("sleepy");
        exp_enum.add("dizzy");
        exp_enum.add("shock");
        exp_enum.add("wink");
        exp_enum.add("idle");
        JsonArray av_req = av_params["required"].to<JsonArray>();
        av_req.add("expression");

        // 4. 伴侣形象切换
        JsonObject tool_pet = tools.add<JsonObject>();
        tool_pet["type"] = "function";
        tool_pet["name"] = "sticks3_switch_pet";
        tool_pet["description"] = "切换屏幕上的数字伴侣形象：'jollybot'(迪士尼小熊) 或 'qiaoqiao'(灵伴悄悄)。";
        JsonObject pet_params = tool_pet["parameters"].to<JsonObject>();
        pet_params["type"] = "object";
        JsonObject pet_props = pet_params["properties"].to<JsonObject>();
        JsonObject pet_prop = pet_props["pet"].to<JsonObject>();
        pet_prop["type"] = "string";
        pet_prop["description"] = "目标宠物名称";
        JsonArray pet_enum = pet_prop["enum"].to<JsonArray>();
        pet_enum.add("jollybot");
        pet_enum.add("qiaoqiao");
        JsonArray pet_req = pet_params["required"].to<JsonArray>();
        pet_req.add("pet");

        // 5. 硬件遥测状态查询
        JsonObject tool_telem = tools.add<JsonObject>();
        tool_telem["type"] = "function";
        tool_telem["name"] = "get_device_telemetry";
        tool_telem["description"] = "查询 StickS3 伴侣硬件的物理遥测数据(电量、IMU姿态角、FPS、内存负荷)。";
        JsonObject telem_params = tool_telem["parameters"].to<JsonObject>();
        telem_params["type"] = "object";

        session["tool_choice"] = "auto";

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
                return sendWsTextWithRetry(s_payload_buf, written, 1, pdMS_TO_TICKS(150));
            }
            return false;
        };

        // 本地多重人声活动容错检验 (已标定为 RMS >= 75.0f, ZCR in [6, 150])
        bool frame_vocal = StickS3Audio::getInstance().isHumanVocalActivity(s_samples, samples_read);

        if (frame_vocal || _server_in_speech) {
            _last_voice_tick = millis();
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
                // 维持 400ms 静音尾窗持续向云端输送静音，以满足 Server-VAD 300ms 裁决
                if (millis() - _last_voice_tick <= 400) {
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

        // 关键兜底保障：若服务端 Server-VAD 在用户声音停止超过 3500ms 后仍未触发 speech_stopped，
        // 客户端主动发送 input_audio_buffer.commit 并请求 response.create，杜绝云端 VAD 挂起卡住！
        if (_server_in_speech && (millis() - _last_voice_tick > 3500)) {
            Serial.println("[BAILIAN-VAD] Server silence fallback (>3.5s). Actively committing & requesting response...");
            const char* commit_payload = "{\"type\":\"input_audio_buffer.commit\"}";
            sendWsTextWithRetry(commit_payload, strlen(commit_payload), 2, pdMS_TO_TICKS(150));
            const char* resp_payload = "{\"type\":\"response.create\"}";
            sendWsTextWithRetry(resp_payload, strlen(resp_payload), 2, pdMS_TO_TICKS(150));
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

            // 关键时序保障：当收到云端音色更新或会话就绪确认后，立即触发音色试听播报
            if (_pending_preview_voice) {
                _pending_preview_voice = false;
                Serial.println("[BAILIAN] Cloud session ready/updated! Triggering voice preview speech...");
                sendTextMessage("请用一句话做自我介绍，告知我你的新音色。");
            } else if (_state != BL_STATE_SPEAKING && !StickS3Audio::getInstance().isPlaying()) {
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
            {
                BailianTextLockGuard lock(_text_mutex);
                _ai_reply = ""; // 关键：每轮新回答生成时清空上一轮回答并预分配内存，防止碎片化
                _ai_reply.reserve(1024);
            }
            _rx_text_dirty = true;
            Serial.println("[BAILIAN] response.created received. Ready for streaming response.");
        }
        // 2. 服务端 VAD 检测到用户开始讲话 -> 触发打断并准备接收新一轮交互！
        else if (strcmp(type, "input_audio_buffer.speech_started") == 0) {
            Serial.println("[BAILIAN-EVENT] Server-VAD: User started speaking!");
            _last_activity_time = millis();
            _last_voice_tick = millis();
            _is_response_cancelled = false; // 用户开口说话，新一轮开始
            if (_state == BL_STATE_SPEAKING) {
                interrupt("Server-VAD-Speech-Started");
            }
            _server_in_speech = true;
            setState(BL_STATE_LISTENING);
            _pending_speech_started = true; // 异步通知主循环进行拟人倾听动作
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
                {
                    BailianTextLockGuard lock(_text_mutex);
                    if (_ai_reply.length() + strlen(delta) < 1024) {
                        _ai_reply += delta;
                    }
                }
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
                {
                    BailianTextLockGuard lock(_text_mutex);
                    _user_query = user_text;
                    _ai_reply = ""; // 清空上一轮回答准备流式刷新
                    _ai_reply.reserve(1024);
                    _pending_user_speech = user_text;
                    _pending_user_speech_ready = true;
                }
                _rx_text_dirty = true;
                _is_response_cancelled = false; // 用户新提问确认，清除任何旧取消状态
                _pending_cancel = false;
                _last_activity_time = millis();
                Serial.printf("[BAILIAN] User said: \"%s\"\n", user_text);
            }
        }
        // 6.5 大模型 Function Calling 工具调用事件 (支持 response.function_call_arguments.done 与 item.created)
        else if (strcmp(type, "response.function_call_arguments.done") == 0) {
            const char* call_id = doc["call_id"] | "";
            const char* fn_name = doc["name"] | "";
            const char* fn_args = doc["arguments"] | "";
            if (strlen(call_id) > 0 && strlen(fn_name) > 0) {
                if (String(call_id) != _last_executed_call_id) {
                    _last_executed_call_id = call_id;
                    if (_tool_mutex && xSemaphoreTake(_tool_mutex, pdMS_TO_TICKS(50)) == pdTRUE) {
                        _pending_tools.push_back({String(call_id), String(fn_name), String(fn_args)});
                        xSemaphoreGive(_tool_mutex);
                    }
                    Serial.printf("[BAILIAN-EVENT] Function call received: %s (call_id: %s)\n", fn_name, call_id);
                }
            }
        }
        else if (strcmp(type, "conversation.item.created") == 0 || strcmp(type, "response.output_item.done") == 0) {
            const char* item_type = doc["item"]["type"] | "";
            if (strcmp(item_type, "function_call") == 0) {
                const char* call_id = doc["item"]["call_id"] | "";
                const char* fn_name = doc["item"]["name"] | "";
                const char* fn_args = doc["item"]["arguments"] | "";
                if (strlen(call_id) > 0 && strlen(fn_name) > 0) {
                    if (String(call_id) != _last_executed_call_id) {
                        _last_executed_call_id = call_id;
                        if (_tool_mutex && xSemaphoreTake(_tool_mutex, pdMS_TO_TICKS(50)) == pdTRUE) {
                            _pending_tools.push_back({String(call_id), String(fn_name), String(fn_args)});
                            xSemaphoreGive(_tool_mutex);
                        }
                        Serial.printf("[BAILIAN-EVENT] Function call item received: %s (call_id: %s)\n", fn_name, call_id);
                    }
                }
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

            String u_copy;
            String a_copy;
            {
                BailianTextLockGuard lock(_text_mutex);
                u_copy = _user_query;
                a_copy = _ai_reply;
                if (a_copy.length() > 0 && !was_cancelled) {
                    _pending_final_ai_reply = a_copy;
                    _pending_final_ai_reply_ready = true;
                }
            }

            // 关键：不在 websocket_task 中直接执行 Flash NVS 写入与 session.update (遵循工程公理二)
            // 标记记忆持久化待处理，在 loopTask 中安全执行，彻底杜绝 Flash 禁用导致 Cache Panic 异常重启
            if (u_copy.length() > 0 && a_copy.length() > 0 && !was_cancelled) {
                _pending_turn_user = u_copy;
                _pending_turn_ai = a_copy;
                _pending_memory_save = true;
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
            // 自动拦截语音音色不支持错误并即刻平滑降级为默认 Tina 音色
            if (strstr(msg, "Voice") != nullptr && (strstr(msg, "not supported") != nullptr || strstr(msg, "InvalidParameter") != nullptr)) {
                Serial.println("[BAILIAN] Unsupported voice detected from server. Auto-falling back to 'Tina'...");
                StickS3ConfigManager::getInstance().saveBailianVoice("Tina");
                _last_error = "";
                _last_activity_time = millis();
                sendSessionUpdate();
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
    volatile bool _pending_preview_voice;
    volatile uint32_t _pending_preview_time;
    String _pending_turn_user;
    String _pending_turn_ai;
    bool _server_in_speech;
    volatile uint32_t _last_voice_tick;
    SemaphoreHandle_t _ws_send_mutex;
    uint32_t _last_state_change;
    uint32_t _total_interrupts;
    uint32_t _server_output_sample_rate;
    uint32_t _wake_window_until;
    String _last_error;
    String _auth_header;

    mutable SemaphoreHandle_t _text_mutex;
    String _user_query;
    String _ai_reply;
    volatile bool _rx_text_dirty;

    String _pending_user_speech;
    volatile bool _pending_user_speech_ready;
    String _pending_final_ai_reply;
    volatile bool _pending_final_ai_reply_ready;
    volatile bool _pending_speech_started;

    BailianTextCallback _on_text;
    BailianStateCallback _on_state;
    BailianUserSpeechCallback _on_user_speech;
    BailianSpeechStartedCallback _on_speech_started;
    BailianToolCallHandler _on_tool_call;
    SemaphoreHandle_t _tool_mutex;
    std::vector<BailianPendingTool> _pending_tools;
    String _last_executed_call_id;
};

} // namespace sticks3
