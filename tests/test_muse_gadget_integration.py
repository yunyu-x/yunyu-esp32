"""
tests/test_muse_gadget_integration.py
-------------------------------------
Automated test suite verifying the Meta Muse Gadgets integration for microUnit:
1. Meta Muse Device Skill markdown descriptors validation (gadget-lingcube-msrr & gadget-lingmatrix-sim).
2. LingCubeDeviceState kinematics, EPM latching, and safety duty cycle invariants.
3. Muse Home Link HTTP REST/RPC bridge live endpoints and response contracts.
4. Console serial hatch protocol parsing and avatar face mapping.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import threading
import pytest

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.bridge.muse_gadget_bridge import (
    LingCubeDeviceState,
    MuseGadgetHttpHandler,
    run_bridge_server,
    g_device_state
)


def test_muse_skill_descriptors():
    """Verify that Meta Muse Skill definitions exist and conform to Meta catalog conventions."""
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 1. LingCube MSRR Skill
    msrr_skill_path = os.path.join(workspace_root, "skills", "gadget-lingcube-msrr", "SKILL.md")
    assert os.path.exists(msrr_skill_path), "gadget-lingcube-msrr/SKILL.md must exist"
    with open(msrr_skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "name: gadget-lingcube-msrr" in content
    assert "description:" in content
    assert "Identify the Device" in content
    assert "REST / RPC API Endpoints" in content
    assert "Safety Limits & Murphy Defense" in content

    # 2. LingMatrix Simulation Skill
    sim_skill_path = os.path.join(workspace_root, "skills", "gadget-lingmatrix-sim", "SKILL.md")
    assert os.path.exists(sim_skill_path), "gadget-lingmatrix-sim/SKILL.md must exist"
    with open(sim_skill_path, "r", encoding="utf-8") as f:
        content_sim = f.read()
    assert "name: gadget-lingmatrix-sim" in content_sim
    assert "MuJoCo" in content_sim


def test_lingcube_device_state_kinematics():
    """Verify state transitions, kinematics roll, EPM latching, and battery safety constraints."""
    device = LingCubeDeviceState(unit_id="LingCube-Test")
    assert device.unit_id == "LingCube-Test"

    # Initial telemetry
    telem = device.get_telemetry()
    assert telem["roll_deg"] == 0.0
    assert telem["pitch_deg"] == 0.0
    assert telem["v_bus"] == 3.85
    assert telem["battery_pct"] > 50
    assert telem["docked_faces"] == []

    # Roll kinematics (+X direction)
    ok, msg = device.execute_roll("+X", torque=0.25, duration_s=0.35)
    assert ok is True
    assert "roll=90.0°" in msg
    assert device.roll == 90.0

    # Roll kinematics (+Y direction)
    ok, msg = device.execute_roll("+Y", torque=0.25, duration_s=0.35)
    assert ok is True
    assert "pitch=90.0°" in msg
    assert device.pitch == 90.0

    # Invalid roll direction
    ok, msg = device.execute_roll("+Z")
    assert ok is False
    assert "Invalid roll direction" in msg

    # Brownout protection lock
    device.v_bus = 3.25
    ok, msg = device.execute_roll("+X")
    assert ok is False
    assert "brownout threshold" in msg
    device.v_bus = 3.80  # Restore


def test_lingcube_device_state_epm_and_safety():
    """Verify EPM magnet state and thermal duty cycle guards."""
    device = LingCubeDeviceState(unit_id="LingCube-EPM")

    # Latch Face 1
    ok, msg = device.execute_epm(face_id=1, state="LATCH", duration_ms=20)
    assert ok is True
    assert 1 in device.get_telemetry()["docked_faces"]

    # Thermal duty cycle guard (<100ms)
    ok_rapid, msg_rapid = device.execute_epm(face_id=2, state="LATCH", duration_ms=20)
    assert ok_rapid is False
    assert "Thermal duty cycle" in msg_rapid

    # Wait for thermal window
    time.sleep(0.12)
    ok_after, _ = device.execute_epm(face_id=2, state="LATCH", duration_ms=20)
    assert ok_after is True
    assert 2 in device.get_telemetry()["docked_faces"]

    # Invalid face ID
    time.sleep(0.12)
    ok_inv, msg_inv = device.execute_epm(face_id=7, state="LATCH")
    assert ok_inv is False
    assert "Invalid face_id" in msg_inv


def test_morphology_and_reflexes():
    """Verify taxonomy morphology reconfiguration and neuromorphic bio-reflex execution."""
    device = LingCubeDeviceState(unit_id="LingCube-Swarm")

    # Morphology configuration
    ok, msg = device.set_morphology("LingChain")
    assert ok is True
    assert device.active_morphology == "LingChain"

    ok_invalid, msg_inv = device.set_morphology("LingUnknown")
    assert ok_invalid is False
    assert "Unknown morphology" in msg_inv

    # Reflex execution (DNp03 bilateral escape)
    ok_ref, msg_ref = device.trigger_reflex("DNp03_ESCAPE")
    assert ok_ref is True
    assert "DNp03" in msg_ref
    assert device.yaw == 45.0

    # Emergency release
    device.docked_faces[0] = True
    ok_rel, _ = device.trigger_reflex("EMERGENCY_RELEASE")
    assert ok_rel is True
    assert not any(device.docked_faces)

    # Avatar face modes
    ok_face, _ = device.set_avatar_face("thinking")
    assert ok_face is True
    assert device.avatar_face == "thinking"


@pytest.fixture(scope="module")
def bridge_server():
    """Start the HTTP bridge server on a test port and terminate upon completion."""
    test_port = 8765
    server = run_bridge_server(host="127.0.0.1", port=test_port)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.2)  # Allow socket to bind
    yield f"http://127.0.0.1:{test_port}"
    server.shutdown()
    server.server_close()


def test_http_bridge_endpoints(bridge_server):
    """Verify live HTTP endpoints over Meta Home Link RPC tunnel contract."""
    base_url = bridge_server

    # 1. Health check
    with urllib.request.urlopen(f"{base_url}/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert "LingCube-MSRR-MuseBridge" in data["service"]

    # 2. Device info
    with urllib.request.urlopen(f"{base_url}/api/device/info") as resp:
        assert resp.status == 200
        info = json.loads(resp.read().decode("utf-8"))
        assert info["device_type"] == "LingCube-MSRR"
        assert info["generation"] == 2
        assert "MomentumWheel-DRV8833" in info["actuators"]

    # 3. Telemetry query
    with urllib.request.urlopen(f"{base_url}/api/robot/telemetry") as resp:
        assert resp.status == 200
        telem = json.loads(resp.read().decode("utf-8"))
        assert "roll_deg" in telem
        assert "v_bus" in telem

    # 4. Roll action POST
    roll_payload = json.dumps({"direction": "-X", "torque": 0.25, "duration_s": 0.35}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/robot/roll",
        data=roll_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode("utf-8"))
        assert res["success"] is True

    # 5. Morphology POST
    morph_payload = json.dumps({"morphology": "LingRing"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/robot/morphology",
        data=morph_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode("utf-8"))
        assert res["active_morphology"] == "LingRing"

    # 6. Avatar Face POST
    face_payload = json.dumps({"face": "happy"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/robot/avatar_face",
        data=face_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode("utf-8"))
        assert res["avatar_face"] == "happy"

    # 7. 404 test
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(f"{base_url}/api/unknown")
    assert exc_info.value.code == 404
