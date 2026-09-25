#ifndef BUDDY_PROTOCOL_H
#define BUDDY_PROTOCOL_H

#include <string>
#include <vector>
#include <functional>
#include <stdint.h>

namespace sticks3 {
namespace protocol {

// 协议服务与特征 UUID (Nordic UART Service)
constexpr const char* NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
constexpr const char* NUS_RX_UUID      = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"; // Desktop -> Device
constexpr const char* NUS_TX_UUID      = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"; // Device -> Desktop

enum class InboundType {
    UNKNOWN = 0,
    STATE,
    PERMISSION,
    NOTIFICATION,
    ROBOT_COMMAND
};

enum class OutboundType {
    ACTION = 0,
    STATUS_REPORT,
    ROBOT_TELEMETRY
};

// 状态同步载荷
struct StatePayload {
    std::string state; // "idle", "working", "awaiting_approval"
};

// 审批授权载荷
struct PermissionPayload {
    std::string id;
    std::string tool;
    std::string command;
    std::string description;
};

// 灵方机器人地面遥测载荷 (扩展协议)
struct RobotTelemetryPayload {
    std::string unit_id;
    float roll;
    float pitch;
    float yaw;
    float v_bus;
    bool epm_active[6];
};

// 协议解析与事件回调引擎
class BuddyProtocolEngine {
public:
    BuddyProtocolEngine();

    // 喂入字节流 (模拟 BLE NUS RX 分包写入，支持半包/粘包拼帧)
    void feedBytes(const char* data, size_t length);

    // 解析单行完整 JSON 帧
    bool parseJsonLine(const std::string& line);

    // 序列化输出帧
    static std::string serializeAction(const std::string& id, bool approve);
    static std::string serializeTelemetry(const RobotTelemetryPayload& telem);
    static std::string serializeStatus(const std::string& current_state, uint8_t bat_pct);

    // 回调事件注册
    std::function<void(const StatePayload&)> onStateReceived;
    std::function<void(const PermissionPayload&)> onPermissionReceived;
    std::function<void(const std::string&)> onNotificationReceived;
    std::function<void(const std::string& cmd)> onRobotCommandReceived;

    // 状态查询
    const std::string& getCurrentState() const { return _current_state; }
    const PermissionPayload& getPendingPermission() const { return _pending_perm; }
    bool hasPendingPermission() const { return _has_pending_perm; }
    void clearPendingPermission() { _has_pending_perm = false; }

    uint32_t getProcessedFrameCount() const { return _processed_frames; }
    uint32_t getMalformedFrameCount() const { return _malformed_frames; }

private:
    std::string _rx_buffer;
    std::string _current_state;
    PermissionPayload _pending_perm;
    bool _has_pending_perm;
    uint32_t _processed_frames;
    uint32_t _malformed_frames;

    // 轻量级非依赖 JSON 键值提取辅助函数
    static std::string extractJsonString(const std::string& json, const std::string& key);
    static float extractJsonFloat(const std::string& json, const std::string& key, float default_val = 0.0f);
};

} // namespace protocol
} // namespace sticks3

#endif // BUDDY_PROTOCOL_H
