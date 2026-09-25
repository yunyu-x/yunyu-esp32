#include "../../firmware/m5sticks3_buddy/include/buddy_protocol.h"
#include <iostream>
#include <cassert>
#include <string>

using namespace sticks3::protocol;

void test_state_message_parsing() {
    std::cout << "[RUNNING] test_state_message_parsing..." << std::endl;
    BuddyProtocolEngine engine;

    std::string received_state = "";
    engine.onStateReceived = [&](const StatePayload& payload) {
        received_state = payload.state;
    };

    std::string msg = "{\"type\": \"state\", \"state\": \"working\"}\n";
    engine.feedBytes(msg.c_str(), msg.length());

    assert(received_state == "working");
    assert(engine.getCurrentState() == "working");
    assert(engine.getProcessedFrameCount() == 1);
    assert(engine.getMalformedFrameCount() == 0);
    std::cout << "  -> State message parsed successfully!" << std::endl;
}

void test_permission_approval_flow() {
    std::cout << "[RUNNING] test_permission_approval_flow..." << std::endl;
    BuddyProtocolEngine engine;

    std::string perm_id = "";
    std::string perm_cmd = "";
    engine.onPermissionReceived = [&](const PermissionPayload& p) {
        perm_id = p.id;
        perm_cmd = p.command;
    };

    std::string msg = "{\"type\": \"permission\", \"id\": \"perm_9981\", \"tool\": \"Bash\", \"command\": \"git push origin main --force\"}\n";
    engine.feedBytes(msg.c_str(), msg.length());

    assert(perm_id == "perm_9981");
    assert(perm_cmd == "git push origin main --force");
    assert(engine.hasPendingPermission());
    assert(engine.getCurrentState() == "awaiting_approval");

    // 模拟硬件端按下 Btn A (Approve) 生成回执
    std::string approve_resp = BuddyProtocolEngine::serializeAction(engine.getPendingPermission().id, true);
    assert(approve_resp.find("\"action\":\"approve\"") != std::string::npos);
    assert(approve_resp.find("\"id\":\"perm_9981\"") != std::string::npos);
    assert(approve_resp.back() == '\n');

    // 模拟硬件端按下 Btn B (Deny) 生成回执
    std::string deny_resp = BuddyProtocolEngine::serializeAction(engine.getPendingPermission().id, false);
    assert(deny_resp.find("\"action\":\"deny\"") != std::string::npos);

    engine.clearPendingPermission();
    assert(!engine.hasPendingPermission());
    std::cout << "  -> Permission parsing, approval & deny serialization verified!" << std::endl;
}

void test_fragmented_packet_stream() {
    std::cout << "[RUNNING] test_fragmented_packet_stream..." << std::endl;
    BuddyProtocolEngine engine;

    std::string received_notif = "";
    engine.onNotificationReceived = [&](const std::string& n) {
        received_notif = n;
    };

    // 模拟由于 BLE MTU 限制分 3 个切片传输
    // 原始报文: {"type":"notification","message":"Build completed in 1.4s"}\n
    std::string chunk1 = "{\"type\":\"notifica";
    std::string chunk2 = "tion\",\"message\":\"Build completed ";
    std::string chunk3 = "in 1.4s\"}\n";

    engine.feedBytes(chunk1.c_str(), chunk1.length());
    assert(engine.getProcessedFrameCount() == 0); // 尚未到达 \n

    engine.feedBytes(chunk2.c_str(), chunk2.length());
    assert(engine.getProcessedFrameCount() == 0); // 仍未到达 \n

    engine.feedBytes(chunk3.c_str(), chunk3.length());
    assert(engine.getProcessedFrameCount() == 1);
    assert(received_notif == "Build completed in 1.4s");

    std::cout << "  -> Fragmented BLE packet stream concatenation verified!" << std::endl;
}

void test_robot_telemetry_extension() {
    std::cout << "[RUNNING] test_robot_telemetry_extension..." << std::endl;
    RobotTelemetryPayload telem;
    telem.unit_id = "LingCube_01";
    telem.roll = 14.50f;
    telem.pitch = -3.20f;
    telem.yaw = 180.00f;
    telem.v_bus = 3.95f;
    telem.epm_active[0] = true;
    telem.epm_active[1] = false;
    telem.epm_active[2] = true;
    telem.epm_active[3] = false;
    telem.epm_active[4] = false;
    telem.epm_active[5] = false;

    std::string telem_line = BuddyProtocolEngine::serializeTelemetry(telem);
    assert(telem_line.find("\"type\":\"robot_telemetry\"") != std::string::npos);
    assert(telem_line.find("\"unit_id\":\"LingCube_01\"") != std::string::npos);
    assert(telem_line.find("\"roll\":14.50") != std::string::npos);
    assert(telem_line.find("\"epm_active\":[1,0,1,0,0,0]") != std::string::npos);
    assert(telem_line.back() == '\n');

    std::cout << "  -> Robot telemetry extension serialization verified!" << std::endl;
}

void test_malformed_json_recovery() {
    std::cout << "[RUNNING] test_malformed_json_recovery..." << std::endl;
    BuddyProtocolEngine engine;

    // 注入非法 JSON 帧
    std::string bad_frame = "This is not a JSON frame\n";
    engine.feedBytes(bad_frame.c_str(), bad_frame.length());
    assert(engine.getMalformedFrameCount() == 1);

    // 紧接着注入合法帧，验证引擎无死锁且正常恢复
    std::string good_frame = "{\"type\": \"state\", \"state\": \"idle\"}\n";
    engine.feedBytes(good_frame.c_str(), good_frame.length());
    assert(engine.getCurrentState() == "idle");
    assert(engine.getProcessedFrameCount() == 1);

    std::cout << "  -> Malformed JSON error rejection and recovery verified!" << std::endl;
}

int main() {
    std::cout << "==========================================================" << std::endl;
    std::cout << ">>> [SCHEME 3 VERIFICATION] Claude Desktop Buddy Protocol" << std::endl;
    std::cout << "==========================================================" << std::endl;

    test_state_message_parsing();
    test_permission_approval_flow();
    test_fragmented_packet_stream();
    test_robot_telemetry_extension();
    test_malformed_json_recovery();

    std::cout << "\n[SUCCESS] Scheme 3 (Claude Desktop Buddy Protocol) PASSED 100%!\n" << std::endl;
    return 0;
}
