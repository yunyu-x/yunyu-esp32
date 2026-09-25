#include "buddy_protocol.h"
#include <sstream>
#include <iomanip>
#include <iostream>

namespace sticks3 {
namespace protocol {

BuddyProtocolEngine::BuddyProtocolEngine()
    : _current_state("idle"),
      _has_pending_perm(false),
      _processed_frames(0),
      _malformed_frames(0) {}

std::string BuddyProtocolEngine::extractJsonString(const std::string& json, const std::string& key) {
    std::string pattern = "\"" + key + "\"";
    size_t search_pos = 0;
    while (true) {
        size_t pos = json.find(pattern, search_pos);
        if (pos == std::string::npos) return "";

        size_t after_key = pos + pattern.length();
        while (after_key < json.length() && (json[after_key] == ' ' || json[after_key] == '\t')) {
            after_key++;
        }
        if (after_key < json.length() && json[after_key] == ':') {
            after_key++; // 跳过冒号
            while (after_key < json.length() && (json[after_key] == ' ' || json[after_key] == '\t')) {
                after_key++;
            }
            if (after_key < json.length() && json[after_key] == '"') {
                after_key++;
                size_t end_pos = json.find('"', after_key);
                if (end_pos == std::string::npos) return "";
                return json.substr(after_key, end_pos - after_key);
            }
            return "";
        }
        search_pos = pos + 1;
    }
}

float BuddyProtocolEngine::extractJsonFloat(const std::string& json, const std::string& key, float default_val) {
    std::string pattern = "\"" + key + "\"";
    size_t search_pos = 0;
    while (true) {
        size_t pos = json.find(pattern, search_pos);
        if (pos == std::string::npos) return default_val;

        size_t after_key = pos + pattern.length();
        while (after_key < json.length() && (json[after_key] == ' ' || json[after_key] == '\t')) {
            after_key++;
        }
        if (after_key < json.length() && json[after_key] == ':') {
            after_key++; // 跳过冒号
            while (after_key < json.length() && (json[after_key] == ' ' || json[after_key] == '\t')) {
                after_key++;
            }
            if (after_key >= json.length()) return default_val;
            try {
                return std::stof(json.substr(after_key));
            } catch (...) {
                return default_val;
            }
        }
        search_pos = pos + 1;
    }
}

void BuddyProtocolEngine::feedBytes(const char* data, size_t length) {
    if (!data || length == 0) return;

    for (size_t i = 0; i < length; ++i) {
        char c = data[i];
        if (c == '\n') {
            if (!_rx_buffer.empty()) {
                parseJsonLine(_rx_buffer);
                _rx_buffer.clear();
            }
        } else if (c != '\r') {
            _rx_buffer.push_back(c);
            // 溢出防护 (> 2048 字节重置缓冲区，防止内存耗尽)
            if (_rx_buffer.length() > 2048) {
                _rx_buffer.clear();
                _malformed_frames++;
            }
        }
    }
}

bool BuddyProtocolEngine::parseJsonLine(const std::string& line) {
    if (line.empty()) return false;

    std::string type = extractJsonString(line, "type");
    if (type.empty()) {
        _malformed_frames++;
        return false;
    }

    if (type == "state") {
        StatePayload payload;
        payload.state = extractJsonString(line, "state");
        if (!payload.state.empty()) {
            _current_state = payload.state;
            _processed_frames++;
            if (onStateReceived) onStateReceived(payload);
            return true;
        }
    } else if (type == "permission") {
        PermissionPayload payload;
        payload.id = extractJsonString(line, "id");
        payload.tool = extractJsonString(line, "tool");
        payload.command = extractJsonString(line, "command");
        payload.description = extractJsonString(line, "description");
        if (!payload.id.empty()) {
            _pending_perm = payload;
            _has_pending_perm = true;
            _current_state = "awaiting_approval";
            _processed_frames++;
            if (onPermissionReceived) onPermissionReceived(payload);
            return true;
        }
    } else if (type == "notification") {
        std::string msg = extractJsonString(line, "message");
        _processed_frames++;
        if (onNotificationReceived) onNotificationReceived(msg);
        return true;
    } else if (type == "robot_command") {
        std::string cmd = extractJsonString(line, "command");
        _processed_frames++;
        if (onRobotCommandReceived) onRobotCommandReceived(cmd);
        return true;
    }

    _malformed_frames++;
    return false;
}

std::string BuddyProtocolEngine::serializeAction(const std::string& id, bool approve) {
    std::ostringstream ss;
    ss << "{\"type\":\"action\",\"id\":\"" << id << "\",\"action\":\""
       << (approve ? "approve" : "deny") << "\"}\n";
    return ss.str();
}

std::string BuddyProtocolEngine::serializeTelemetry(const RobotTelemetryPayload& telem) {
    std::ostringstream ss;
    ss << "{\"type\":\"robot_telemetry\",\"unit_id\":\"" << telem.unit_id << "\""
       << ",\"roll\":" << std::fixed << std::setprecision(2) << telem.roll
       << ",\"pitch\":" << telem.pitch
       << ",\"yaw\":" << telem.yaw
       << ",\"v_bus\":" << telem.v_bus
       << ",\"epm_active\":[";
    for (int i = 0; i < 6; ++i) {
        ss << (telem.epm_active[i] ? "1" : "0");
        if (i < 5) ss << ",";
    }
    ss << "]}\n";
    return ss.str();
}

std::string BuddyProtocolEngine::serializeStatus(const std::string& current_state, uint8_t bat_pct) {
    std::ostringstream ss;
    ss << "{\"type\":\"status_report\",\"state\":\"" << current_state
       << "\",\"battery\":" << static_cast<int>(bat_pct) << "}\n";
    return ss.str();
}

} // namespace protocol
} // namespace sticks3
