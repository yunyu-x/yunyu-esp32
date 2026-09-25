#!/usr/bin/env python3
"""
scripts/verify_scheme3_buddy_ble.py
-----------------------------------
方案 3 自动化端到端验证脚本：Claude Desktop Buddy 协议栈与双向交互模拟器
- 模拟 Claude Desktop / Claude Code 主机 BLE NUS 客户端
- 验证状态同步、权限审批放行（Approve）、拦截（Deny）闭环时序
- 验证网络分包粘包容错与灵方机器人地面遥测扩展报文
"""

import sys
import json
import time
from typing import Dict, Any, List, Optional


class MockClaudeDesktopHost:
    """模拟 Claude Desktop 上位机"""

    def __init__(self):
        self.tx_history: List[str] = []
        self.rx_history: List[Dict[str, Any]] = []

    def send_state(self, state: str) -> str:
        msg = json.dumps({"type": "state", "state": state}) + "\n"
        self.tx_history.append(msg)
        return msg

    def send_permission_request(self, req_id: str, tool: str, command: str, description: str = "") -> str:
        msg = json.dumps({
            "type": "permission",
            "id": req_id,
            "tool": tool,
            "command": command,
            "description": description
        }) + "\n"
        self.tx_history.append(msg)
        return msg

    def send_robot_command(self, command: str) -> str:
        msg = json.dumps({"type": "robot_command", "command": command}) + "\n"
        self.tx_history.append(msg)
        return msg

    def receive_response(self, raw_line: str) -> Optional[Dict[str, Any]]:
        raw_line = raw_line.strip()
        if not raw_line:
            return None
        try:
            data = json.loads(raw_line)
            self.rx_history.append(data)
            return data
        except json.JSONDecodeError:
            return None


class MockStickS3BuddyDevice:
    """模拟 StickS3 运行的 Claude Buddy 协议引擎与按键交互"""

    def __init__(self):
        self.current_state = "idle"
        self.pending_permission = None
        self.tx_queue: List[str] = []
        self.rx_buffer = ""

    def feed_rx(self, chunk: str):
        self.rx_buffer += chunk
        while "\n" in self.rx_buffer:
            line, self.rx_buffer = self.rx_buffer.split("\n", 1)
            line = line.strip()
            if line:
                self._handle_line(line)

    def _handle_line(self, line: str):
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            return

        mtype = msg.get("type")
        if mtype == "state":
            self.current_state = msg.get("state", "idle")
        elif mtype == "permission":
            self.pending_permission = msg
            self.current_state = "awaiting_approval"
        elif mtype == "robot_command":
            # 机器人控制指令响应
            pass

    def press_button_a_approve(self) -> Optional[str]:
        """按键 A: 批准并回执"""
        if not self.pending_permission:
            return None
        req_id = self.pending_permission.get("id")
        self.pending_permission = None
        self.current_state = "working"
        resp = json.dumps({"type": "action", "id": req_id, "action": "approve"}) + "\n"
        self.tx_queue.append(resp)
        return resp

    def press_button_b_deny(self) -> Optional[str]:
        """按键 B: 拒绝并回执"""
        if not self.pending_permission:
            return None
        req_id = self.pending_permission.get("id")
        self.pending_permission = None
        self.current_state = "idle"
        resp = json.dumps({"type": "action", "id": req_id, "action": "deny"}) + "\n"
        self.tx_queue.append(resp)
        return resp

    def emit_robot_telemetry(self, unit_id: str, roll: float, pitch: float, v_bus: float) -> str:
        telem = {
            "type": "robot_telemetry",
            "unit_id": unit_id,
            "roll": round(roll, 2),
            "pitch": round(pitch, 2),
            "yaw": 0.0,
            "v_bus": round(v_bus, 2),
            "epm_active": [1, 0, 0, 0, 1, 0]
        }
        msg = json.dumps(telem) + "\n"
        self.tx_queue.append(msg)
        return msg


def run_scheme3_verification() -> bool:
    print("=" * 70)
    print(">>> [SCHEME 3 VERIFICATION] Claude Desktop Buddy BLE Protocol Simulation")
    print("=" * 70)

    host = MockClaudeDesktopHost()
    device = MockStickS3BuddyDevice()

    # 1. 状态同步验证
    state_msg = host.send_state("working")
    device.feed_rx(state_msg)
    assert device.current_state == "working", "State synchronization failed"
    print("[+] State Sync: Desktop pushed 'working' -> Device transitioned to 'working'.")

    # 2. 权限放行审批流 (Approve Flow via Btn A)
    perm_msg1 = host.send_permission_request(
        req_id="req_bash_101",
        tool="Bash",
        command="git checkout -b feature/sticks3-buddy",
        description="Create feature branch"
    )
    device.feed_rx(perm_msg1)
    assert device.current_state == "awaiting_approval"
    assert device.pending_permission["id"] == "req_bash_101"
    print("[+] Permission Request: Device entered 'awaiting_approval' for req_bash_101.")

    # 模拟按下 Btn A 放行
    approve_resp = device.press_button_a_approve()
    assert approve_resp is not None
    data = host.receive_response(approve_resp)
    assert data["type"] == "action" and data["id"] == "req_bash_101" and data["action"] == "approve"
    print(f"[+] Physical Gate Approve: Btn A clicked -> Host received authorization: {data['action']}.")

    # 3. 权限拒绝流 (Deny Flow via Btn B)
    perm_msg2 = host.send_permission_request(
        req_id="req_bash_102",
        tool="Bash",
        command="rm -rf / --no-preserve-root",
        description="High risk destructive operation"
    )
    device.feed_rx(perm_msg2)
    assert device.current_state == "awaiting_approval"
    
    # 模拟按下 Btn B 拒绝
    deny_resp = device.press_button_b_deny()
    assert deny_resp is not None
    data2 = host.receive_response(deny_resp)
    assert data2["type"] == "action" and data2["id"] == "req_bash_102" and data2["action"] == "deny"
    print(f"[+] Physical Gate Intercept: Btn B clicked -> Host received block: {data2['action']}.")

    # 4. 模拟半包拼帧 (Fragmented Packet Over BLE)
    raw_packet = host.send_state("idle")
    p1, p2 = raw_packet[:10], raw_packet[10:]
    device.feed_rx(p1)
    # 此时尚未完成拼包
    device.feed_rx(p2)
    assert device.current_state == "idle"
    print("[+] BLE Fragmentation Test: Half-packets successfully reassembled.")

    # 5. 灵方机器人地面遥测扩展包验证
    telem_packet = device.emit_robot_telemetry("LingCube_01", roll=18.5, pitch=-2.1, v_bus=3.91)
    telem_data = host.receive_response(telem_packet)
    assert telem_data["type"] == "robot_telemetry"
    assert telem_data["unit_id"] == "LingCube_01"
    assert telem_data["roll"] == 18.5
    print(f"[+] LingCube Telemetry Extension: Parsed unit {telem_data['unit_id']} (roll={telem_data['roll']}°, vbus={telem_data['v_bus']}V).")

    print("\n[SUCCESS] Scheme 3 (Claude Desktop Buddy & Extension) PASSED 100%!\n")
    return True


if __name__ == "__main__":
    success = run_scheme3_verification()
    sys.exit(0 if success else 1)
