/**
 * @file muse_gadget_client.h
 * @brief Meta Muse Gadgets protocol client & serial hatch parser for M5Stack StickS3.
 *
 * Implements compatibility with:
 * - Meta Muse Gadget SDK (facebookincubator/muse-gadget-sdk)
 * - Serial Hatch Protocol (>chat=..., >face=...)
 * - Avatar mode state machine mapping into sticks3_avatar.h
 * - Axiom 2 (Async protocol task decoupling) & Axiom 3 (PSRAM double-buffering)
 */

#ifndef MUSE_GADGET_CLIENT_H
#define MUSE_GADGET_CLIENT_H

#include <stdint.h>
#include <string>
#include <vector>
#include <functional>

namespace muse_gadget {

// Meta Muse 官方 Avatar 状态定义 (与 components/muse/muse_state.h 一致)
enum class MuseFaceState {
    IDLE = 0,
    LISTENING,
    SPEAKING,
    THINKING,
    HAPPY,
    ERROR_STATE,
    BOOT,
    OFF
};

// 串口 Hatch 指令类型 (与 tools/muse/chat.py 对接)
enum class HatchCommandType {
    NONE = 0,
    CHAT_APPEND,  // >chat+=
    CHAT_SEND,    // >chat=
    FACE_SET,     // >face=
    STATUS_QUERY, // --status
    ROBOT_COMMAND // >robot=
};

struct HatchParsedMessage {
    HatchCommandType type;
    std::string payload;
    bool is_final_chunk;
};

/**
 * @brief Meta Muse 串口控制台 Hatch 协议解析器
 * 遵循 Meta 官方 escape/unescape 规范 (反斜杠、换行符转义)
 */
class MuseConsoleParser {
public:
    MuseConsoleParser() : _accumulated_chat("") {}

    // 解析单行控制台输入 (例如: ">chat=Hello Muse\n" 或 ">face=thinking\n")
    HatchParsedMessage parseLine(const std::string& line) {
        HatchParsedMessage msg;
        msg.type = HatchCommandType::NONE;
        msg.is_final_chunk = true;

        if (line.rfind(">chat+=", 0) == 0) {
            msg.type = HatchCommandType::CHAT_APPEND;
            msg.payload = unescape(line.substr(7));
            msg.is_final_chunk = false;
            if (_accumulated_chat.size() + msg.payload.size() <= 4096) {
                _accumulated_chat += msg.payload;
            }
        } else if (line.rfind(">chat=", 0) == 0) {
            msg.type = HatchCommandType::CHAT_SEND;
            msg.payload = unescape(line.substr(6));
            msg.is_final_chunk = true;
            if (_accumulated_chat.size() + msg.payload.size() <= 4096) {
                _accumulated_chat += msg.payload;
            }
            msg.payload = _accumulated_chat;
            _accumulated_chat.clear(); // 清空分包累积
        } else if (line.rfind(">face=", 0) == 0) {
            msg.type = HatchCommandType::FACE_SET;
            std::string face = line.substr(6);
            while (!face.empty() && (face.back() == '\r' || face.back() == '\n' || face.back() == ' ')) {
                face.pop_back();
            }
            msg.payload = face;
        } else if (line.rfind(">robot=", 0) == 0) {
            msg.type = HatchCommandType::ROBOT_COMMAND;
            msg.payload = line.substr(7);
        } else if (line.rfind(">status", 0) == 0 || line.rfind("--status", 0) == 0) {
            msg.type = HatchCommandType::STATUS_QUERY;
        }

        return msg;
    }

    // 转义反解析: 将字节流恢复为原文字符
    static std::string unescape(const std::string& input) {
        std::string out;
        out.reserve(input.size());
        for (size_t i = 0; i < input.size(); ++i) {
            if (input[i] == '\\' && i + 1 < input.size()) {
                char next = input[++i];
                if (next == 'n') out += '\n';
                else if (next == 'r') out += '\r';
                else if (next == 't') out += '\t';
                else if (next == '\\') out += '\\';
                else out += next;
            } else if (input[i] != '\r' && input[i] != '\n') {
                out += input[i];
            }
        }
        return out;
    }

    // 格式化输出为 @chat JSON 响应行
    static std::string formatChatJson(const std::string& type, const std::string& text, int msg_id = 1) {
        std::string json = "{\"type\": \"" + type + "\", \"msg\": " + std::to_string(msg_id) + ", \"text\": \"" + text + "\"}\n";
        return "@chat " + json;
    }

    // 格式化输出为 @status JSON 响应行
    static std::string formatStatusJson(float v_bus, float fps, bool wifi_connected, const std::string& wifi_mode, const std::string& ip_str, const std::string& face) {
        char buf[280];
        snprintf(buf, sizeof(buf),
            "@status {\"board\":\"M5Stack StickS3\",\"chat\":true,\"device\":{\"wifi\":{\"state\":\"%s\",\"mode\":\"%s\",\"ip\":\"%s\"},\"hatch\":{\"state\":\"connected\"},\"v_bus\":%.2f,\"fps\":%.1f,\"face\":\"%s\"}}\n",
            wifi_connected ? "connected" : "disconnected",
            wifi_mode.c_str(),
            ip_str.c_str(),
            v_bus, fps, face.c_str());
        return std::string(buf);
    }

    void reset() {
        _accumulated_chat.clear();
    }

    const std::string& getAccumulated() const {
        return _accumulated_chat;
    }

private:
    std::string _accumulated_chat;
};

/**
 * @brief 将 Meta Muse Avatar 状态映射到 StickS3 本地表情模式
 */
inline MuseFaceState parseMuseFace(const std::string& face_str) {
    if (face_str == "listening") return MuseFaceState::LISTENING;
    if (face_str == "speaking") return MuseFaceState::SPEAKING;
    if (face_str == "thinking") return MuseFaceState::THINKING;
    if (face_str == "happy") return MuseFaceState::HAPPY;
    if (face_str == "error") return MuseFaceState::ERROR_STATE;
    if (face_str == "boot") return MuseFaceState::BOOT;
    if (face_str == "off") return MuseFaceState::OFF;
    return MuseFaceState::IDLE;
}

/**
 * @brief 将 Meta Muse Avatar 字符串直接映射为 StickS3 内部 AvatarMood
 */
inline uint8_t mapFaceStringToMood(const std::string& face_str) {
    // 对应 sticks3::AvatarMood
    if (face_str == "listening" || face_str == "listen") return 1; // MOOD_LISTEN
    if (face_str == "thinking" || face_str == "think") return 2;   // MOOD_THINK
    if (face_str == "speaking" || face_str == "speak") return 3;   // MOOD_SPEAK
    if (face_str == "happy" || face_str == "pet") return 4;        // MOOD_HAPPY
    if (face_str == "dizzy") return 5;                             // MOOD_DIZZY
    if (face_str == "shock" || face_str == "error") return 6;      // MOOD_SHOCK
    if (face_str == "sleep" || face_str == "sleepy") return 7;     // MOOD_SLEEP
    if (face_str == "curious") return 8;                           // MOOD_CURIOUS
    if (face_str == "proud") return 9;                             // MOOD_PROUD
    if (face_str == "eat" || face_str == "feed") return 10;        // MOOD_EAT
    if (face_str == "groom") return 11;                            // MOOD_GROOM
    if (face_str == "wink") return 12;                             // MOOD_WINK
    return 0; // MOOD_IDLE
}

} // namespace muse_gadget

#endif // MUSE_GADGET_CLIENT_H
