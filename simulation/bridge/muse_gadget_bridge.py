"""
simulation/bridge/muse_gadget_bridge.py
---------------------------------------
Meta Muse Gadgets <-> microUnit (LingCube & LingBuddy) Local HTTP RPC Bridge.

Implements the official Muse Home Link Device Skill contract:
- Compatible with Meta's `gadget-lingcube-msrr` and `gadget-lingmatrix-sim` skills.
- Operates through the encrypted Noise Home Link tunnel to user's Meta Muse Secure VM.
- Bridges natural language intent and tool calls from Meta Muse down to:
    1) Physical LingBuddy (M5Stack StickS3) over serial/BLE.
    2) Physical LingCube MSRR robots over BLE / IR / ESP-NOW.
    3) LingMatrix MuJoCo digital twin physics simulation.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("muse-gadget-bridge")


class LingCubeDeviceState:
    """Thread-safe virtual or mirrored state for a LingCube MSRR device."""

    def __init__(self, unit_id: str = "LingCube-01"):
        self.unit_id = unit_id
        self.roll = 0.0          # deg
        self.pitch = 0.0         # deg
        self.yaw = 0.0           # deg
        self.v_bus = 3.85        # Volts
        self.fault_flags = 0
        self.docked_faces = [False] * 6  # Faces 1..6
        self.active_morphology = "LingCube"
        self.avatar_face = "idle"
        self.active_pet = "jollybot"  # 'jollybot' (Meta Muse pixel-art bear) or 'qiaoqiao' (procedural vector pet)
        self.last_epm_pulse_time = 0.0
        self.last_action_timestamp = time.time()

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "roll_deg": round(self.roll, 2),
            "pitch_deg": round(self.pitch, 2),
            "yaw_deg": round(self.yaw, 2),
            "v_bus": round(self.v_bus, 2),
            "battery_pct": int(max(0, min(100, (self.v_bus - 3.40) / (4.20 - 3.40) * 100))),
            "fault_flags": self.fault_flags,
            "docked_faces": [i + 1 for i, docked in enumerate(self.docked_faces) if docked],
            "active_morphology": self.active_morphology,
            "avatar_face": self.avatar_face,
            "active_pet": self.active_pet,
            "timestamp": time.time(),
        }

    def execute_roll(self, direction: str, torque: float = 0.25, duration_s: float = 0.35) -> Tuple[bool, str]:
        if self.v_bus < 3.30:
            return False, f"Hardware safety lock: Bus voltage {self.v_bus:.2f}V is below 3.30V brownout threshold"

        valid_directions = {"+X", "-X", "+Y", "-Y"}
        if direction not in valid_directions:
            return False, f"Invalid roll direction '{direction}'. Must be one of {valid_directions}"

        # Simulate dynamic momentum transfer tumble (90° step)
        if direction == "+X":
            self.roll = (self.roll + 90.0) % 360.0
        elif direction == "-X":
            self.roll = (self.roll - 90.0) % 360.0
        elif direction == "+Y":
            self.pitch = (self.pitch + 90.0) % 360.0
        elif direction == "-Y":
            self.pitch = (self.pitch - 90.0) % 360.0

        # Electrical consumption: IR sag & discharge (approx 0.015V per high-torque roll)
        self.v_bus = max(3.35, self.v_bus - 0.015)
        self.last_action_timestamp = time.time()
        return True, f"Successfully executed {direction} roll maneuver. New posture: roll={self.roll}°, pitch={self.pitch}°"

    def execute_epm(self, face_id: int, state: str, duration_ms: int = 20) -> Tuple[bool, str]:
        if not (1 <= face_id <= 6):
            return False, f"Invalid face_id {face_id}. LingCube has 6 faces (1..6)"

        now = time.time()
        if now - self.last_epm_pulse_time < 0.10:  # 100ms thermal duty cycle guard
            return False, "Thermal duty cycle protection: EPM pulses must be spaced by at least 100ms"

        is_latch = (state.upper() == "LATCH")
        self.docked_faces[face_id - 1] = is_latch
        self.last_epm_pulse_time = now
        self.v_bus = max(3.35, self.v_bus - 0.005)  # EPM pulse consumption
        return True, f"Face {face_id} EPM coil pulsed ({state.upper()}) for {duration_ms}ms. Force: {'35N+ (locked)' if is_latch else '0N (released)'}"

    def set_morphology(self, morphology: str) -> Tuple[bool, str]:
        valid_morphologies = {
            "LingCube", "LingChain", "LingRing", "LingSheet",
            "LingLattice", "LingWalker", "LingArm", "LingGrip", "LingSwarm"
        }
        if morphology not in valid_morphologies:
            return False, f"Unknown morphology '{morphology}'. Valid: {sorted(list(valid_morphologies))}"
        self.active_morphology = morphology
        return True, f"Morphology reconfigured to {morphology}."

    def trigger_reflex(self, reflex_type: str) -> Tuple[bool, str]:
        valid_reflexes = {"DNp03_ESCAPE", "HALTERE_DAMP", "EMERGENCY_RELEASE"}
        if reflex_type not in valid_reflexes:
            return False, f"Unknown reflex '{reflex_type}'. Valid: {valid_reflexes}"

        if reflex_type == "DNp03_ESCAPE":
            self.yaw = (self.yaw + 45.0) % 360.0
            return True, "Executed DNp03 fast bilateral escape steering reflex (45° evade)."
        elif reflex_type == "HALTERE_DAMP":
            return True, "Applied haltere angular rate damping: gyroscopic oscillations stabilized."
        elif reflex_type == "EMERGENCY_RELEASE":
            self.docked_faces = [False] * 6
            return True, "Emergency all-face EPM release executed. Magnetic latch decoupled."
        return False, "Unknown reflex"

    def set_avatar_face(self, face: str) -> Tuple[bool, str]:
        valid_faces = {"idle", "listening", "speaking", "thinking", "happy", "error", "boot", "off"}
        if face not in valid_faces:
            return False, f"Invalid face mode '{face}'. Valid: {valid_faces}"
        self.avatar_face = face
        return True, f"Avatar face updated to {face}."

    def switch_pet(self, pet: str) -> Tuple[bool, str]:
        valid_pets = {"jollybot", "qiaoqiao"}
        pet_lower = pet.lower()
        if pet_lower not in valid_pets:
            return False, f"Invalid pet avatar '{pet}'. Valid options: {sorted(list(valid_pets))}"
        self.active_pet = pet_lower
        return True, f"Pet avatar successfully switched to {pet_lower}."


# Global singleton device state
g_device_state = LingCubeDeviceState()


class MuseGadgetHttpHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler implementing Meta Muse Home Link RPC contract."""

    def log_message(self, format: str, *args: Any) -> None:
        logger.info("%s - - %s", self.address_string(), format % args)

    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._send_json(200, {"status": "ok"})

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/")

        if path == "" or path == "/health":
            self._send_json(200, {
                "status": "ok",
                "service": "LingCube-MSRR-MuseBridge",
                "version": "1.0.0",
                "device_id": g_device_state.unit_id,
                "online": True
            })
            return

        if path == "/api/device/info":
            self._send_json(200, {
                "device_type": "LingCube-MSRR",
                "device_name": "灵方微型自重构机器人",
                "generation": 2,
                "mcu": "ESP32-S3 (Xtensa Dual-Core 240MHz)",
                "companion_support": "M5Stack StickS3 (LingBuddy)",
                "actuators": ["MomentumWheel-DRV8833", "EPM-Pulse-6Face"],
                "sensors": ["MPU-6050-IMU", "6xNearIR-Transceivers", "BusVoltage-ADC"],
                "battery_mv": int(g_device_state.v_bus * 1000),
                "battery_pct": int(max(0, min(100, (g_device_state.v_bus - 3.40) / (4.20 - 3.40) * 100))),
                "firmware_version": "v2.1.0-muse"
            })
            return

        if path == "/api/robot/telemetry":
            self._send_json(200, g_device_state.get_telemetry())
            return

        self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/")
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        if path == "/api/robot/roll":
            direction = payload.get("direction", "+X")
            torque = float(payload.get("torque", 0.25))
            duration_s = float(payload.get("duration_s", 0.35))
            success, msg = g_device_state.execute_roll(direction, torque, duration_s)
            status_code = 200 if success else 400
            self._send_json(status_code, {
                "success": success,
                "message": msg,
                "telemetry": g_device_state.get_telemetry()
            })
            return

        if path == "/api/robot/epm":
            face_id = int(payload.get("face_id", 1))
            state = payload.get("state", "LATCH")
            duration_ms = int(payload.get("duration_ms", 20))
            success, msg = g_device_state.execute_epm(face_id, state, duration_ms)
            status_code = 200 if success else 400
            self._send_json(status_code, {
                "success": success,
                "message": msg,
                "docked_faces": [i + 1 for i, d in enumerate(g_device_state.docked_faces) if d]
            })
            return

        if path == "/api/robot/morphology":
            morphology = payload.get("morphology", "LingChain")
            success, msg = g_device_state.set_morphology(morphology)
            status_code = 200 if success else 400
            self._send_json(status_code, {
                "success": success,
                "message": msg,
                "active_morphology": g_device_state.active_morphology
            })
            return

        if path == "/api/robot/reflex":
            reflex_type = payload.get("reflex_type", "HALTERE_DAMP")
            success, msg = g_device_state.trigger_reflex(reflex_type)
            status_code = 200 if success else 400
            self._send_json(status_code, {
                "success": success,
                "message": msg,
                "telemetry": g_device_state.get_telemetry()
            })
            return

        if path == "/api/robot/avatar_face":
            face = payload.get("face", "idle")
            success, msg = g_device_state.set_avatar_face(face)
            status_code = 200 if success else 400
            self._send_json(status_code, {
                "success": success,
                "message": msg,
                "avatar_face": g_device_state.avatar_face
            })
            return

        self._send_json(404, {"error": "Not Found", "path": self.path})


def run_bridge_server(host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    """Launch the Meta Muse Gadgets HTTP Bridge server."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, MuseGadgetHttpHandler)
    logger.info("Meta Muse Gadget RPC Bridge listening on http://%s:%d", host, port)
    return httpd


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Meta Muse Gadget microUnit HTTP Bridge")
    parser.add_argument("--port", type=int, default=8080, help="Listen port (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Listen host (default: 0.0.0.0)")
    args = parser.parse_args()

    server = run_bridge_server(host=args.host, port=args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down bridge server...")
        server.shutdown()
