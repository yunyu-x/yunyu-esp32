"""
tests/test_bailian_muse_cloud_agent.py
--------------------------------------
Automated test suite verifying the Bailian Cloud Agent Server (Meta Muse Replacement):
1. Safe UTF-8 truncation boundary algorithm (Axiom 6).
2. DeviceSkillRegistry embodied tool schemas, execution, and hardware safety limits (Brownout & Thermal).
3. BailianAgentEngine multi-turn conversation and intelligent mock reasoning.
4. AudioDictationBridge 16kHz PCM transcription deltas.
5. SerialHatchManager protocol framing (>chat=, >face=, >robot=, @chat, @status).
6. TunnelSupervisor persistence and metadata endpoints.
7. FastAPI REST & SSE endpoints (/health, /fetch_vms, /api/chat, /chat/stream, /api/voice/dictation, /rpc/*).
8. Full duplex WebSocket /ws/v1/realtime gateway (VAD, speech started, audio delta, barge-in cancel).
"""

import os
import sys
import json
import time
import base64
import struct
import math
import pytest
from fastapi.testclient import TestClient

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from simulation.bridge.bailian_muse_cloud_agent import (
    safe_truncate_utf8,
    DeviceSkillRegistry,
    BailianAgentEngine,
    AudioDictationBridge,
    SerialHatchManager,
    TunnelSupervisor,
    BailianMuseCloudAgent,
    create_bailian_muse_app
)
from simulation.bridge.muse_gadget_bridge import LingCubeDeviceState


# -----------------------------------------------------------------------------
# Test 1: Safe UTF-8 Truncation
# -----------------------------------------------------------------------------
def test_safe_truncate_utf8():
    text = "灵方机器人 LingCube 🤖"
    # Basic bounds
    assert safe_truncate_utf8(text, 0) == ""
    assert safe_truncate_utf8(text, 100) == text

    # Chinese character boundaries (3 bytes per char)
    assert safe_truncate_utf8("灵方", 1) == ""
    assert safe_truncate_utf8("灵方", 2) == ""
    assert safe_truncate_utf8("灵方", 3) == "灵"
    assert safe_truncate_utf8("灵方", 4) == "灵"
    assert safe_truncate_utf8("灵方", 5) == "灵"
    assert safe_truncate_utf8("灵方", 6) == "灵方"

    # Emoji boundaries (4 bytes for 🤖)
    emoji_str = "A🤖B"
    # 'A' is 1 byte, '🤖' is 4 bytes, 'B' is 1 byte
    assert safe_truncate_utf8(emoji_str, 1) == "A"
    assert safe_truncate_utf8(emoji_str, 2) == "A"
    assert safe_truncate_utf8(emoji_str, 4) == "A"
    assert safe_truncate_utf8(emoji_str, 5) == "A🤖"
    assert safe_truncate_utf8(emoji_str, 6) == "A🤖B"


# -----------------------------------------------------------------------------
# Test 2: DeviceSkillRegistry & Embodied Tools
# -----------------------------------------------------------------------------
def test_device_skill_registry_tools():
    dev = LingCubeDeviceState(unit_id="LingCube-UnitTest")
    reg = DeviceSkillRegistry(dev)

    # 1. Check schemas
    schemas = reg.get_tools_schema()
    assert len(schemas) >= 7
    names = [s["function"]["name"] for s in schemas]
    assert "lingcube_roll" in names
    assert "lingcube_epm_latch" in names
    assert "lingcube_set_morphology" in names
    assert "lingcube_trigger_reflex" in names
    assert "sticks3_set_avatar" in names
    assert "get_robot_telemetry" in names
    assert "lingbuddy_interact" in names

    # 2. Tool execution: lingcube_roll
    r1 = reg.execute_tool("lingcube_roll", {"direction": "+X"})
    assert r1["success"] is True
    assert dev.roll == 90.0

    # Brownout safety limit
    dev.v_bus = 3.25
    r_bo = reg.execute_tool("lingcube_roll", {"direction": "+X"})
    assert r_bo["success"] is False
    assert "brownout" in r_bo["message"].lower()
    dev.v_bus = 3.85  # Restore

    # 3. Tool execution: lingcube_epm_latch & thermal protection
    r_epm1 = reg.execute_tool("lingcube_epm_latch", {"face_id": 1, "state": "LATCH"})
    assert r_epm1["success"] is True
    assert 1 in r_epm1["docked_faces"]

    # Thermal cooldown
    r_epm2 = reg.execute_tool("lingcube_epm_latch", {"face_id": 2, "state": "LATCH"})
    assert r_epm2["success"] is False
    assert "thermal" in r_epm2["message"].lower()

    # 4. Tool execution: morphology
    r_morph = reg.execute_tool("lingcube_set_morphology", {"morphology": "LingRing"})
    assert r_morph["success"] is True
    assert dev.active_morphology == "LingRing"

    # 5. Tool execution: reflex
    r_ref = reg.execute_tool("lingcube_trigger_reflex", {"reflex_type": "DNp03_ESCAPE"})
    assert r_ref["success"] is True
    assert dev.yaw == 45.0

    # 6. Tool execution: avatar face
    r_face = reg.execute_tool("sticks3_set_avatar", {"expression": "thinking"})
    assert r_face["success"] is True
    assert dev.avatar_face == "thinking"

    # 7. Tool execution: telemetry
    r_telem = reg.execute_tool("get_robot_telemetry", {})
    assert r_telem["success"] is True
    assert "v_bus" in r_telem["telemetry"]

    # 8. Tool execution: lingbuddy_interact
    r_pet = reg.execute_tool("lingbuddy_interact", {"action": "pet"})
    assert r_pet["success"] is True
    assert reg.pet_count == 1
    assert "抚摸" in r_pet["message"]

    r_feed = reg.execute_tool("lingbuddy_interact", {"action": "feed", "snack": "甜甜圈"})
    assert r_feed["success"] is True
    assert "甜甜圈" in r_feed["message"]


# -----------------------------------------------------------------------------
# Test 3: BailianAgentEngine Intelligent Mock & Multi-turn Reasoning
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_bailian_agent_engine_mock():
    dev = LingCubeDeviceState(unit_id="LingCube-MockEngine")
    reg = DeviceSkillRegistry(dev)
    engine = BailianAgentEngine(reg, force_mock=True)

    # 1. Roll intent reasoning
    res_roll = await engine.chat("请控制灵方向前翻滚一步", session_id="test_s1")
    assert "翻滚" in res_roll["reply"]
    assert any(tc["name"] == "lingcube_roll" for tc in res_roll["tool_calls"])
    assert res_roll["avatar_face"] == "happy"

    # 2. EPM magnetic latch intent reasoning
    time.sleep(0.12)  # Wait for EPM thermal cooldown
    res_epm = await engine.chat("把灵方的2号面电永磁充磁锁紧", session_id="test_s1")
    assert any(tc["name"] == "lingcube_epm_latch" for tc in res_epm["tool_calls"])
    assert "2 号面" in res_epm["reply"]

    # 3. Avatar face intent reasoning
    res_face = await engine.chat("灵伴请切换为思考表情", session_id="test_s1")
    assert any(tc["name"] == "sticks3_set_avatar" for tc in res_face["tool_calls"])

    # 4. Telemetry intent
    res_telem = await engine.chat("查询当前的电池电量和遥测状态", session_id="test_s1")
    assert "遥测" in res_telem["reply"]
    assert any(tc["name"] == "get_robot_telemetry" for tc in res_telem["tool_calls"])

    # 5. Streaming chat generator
    stream_events = []
    async for ev in engine.chat_stream("你好呀悄悄", session_id="test_s2"):
        stream_events.append(ev)

    event_names = [e["event"] for e in stream_events]
    assert "message_start" in event_names
    assert "avatar_face" in event_names
    assert "text_append" in event_names
    assert "message_done" in event_names


# -----------------------------------------------------------------------------
# Test 4: AudioDictationBridge 16kHz PCM Transcription
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_audio_dictation_bridge():
    dev = LingCubeDeviceState()
    reg = DeviceSkillRegistry(dev)
    engine = BailianAgentEngine(reg, force_mock=True)
    dictation = AudioDictationBridge(engine)

    # Generate dummy 16kHz PCM audio buffer
    sample_rate = 16000
    samples = [int(500 * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(sample_rate)]
    raw_pcm = struct.pack(f"<{len(samples)}h", *samples)

    transcripts = await dictation.transcribe(raw_pcm)
    assert len(transcripts) >= 1
    final = next((t for t in transcripts if t["type"] == "final"), None)
    assert final is not None
    assert len(final["transcript"]) > 0

    # Embedded test tag
    tagged_pcm = b"\x00" * 100 + b"CMD:\xe7\x81\xb5\xe6\x96\xb9\xe5\x90\x91\xe5\x89\x8d\xe7\xbf\xbb\xe6\xbb\x9a\x00" + b"\x00" * 100
    res_tagged = await dictation.transcribe(tagged_pcm)
    tagged_final = next((t for t in res_tagged if t["type"] == "final"), None)
    assert tagged_final is not None
    assert "翻滚" in tagged_final["transcript"]


# -----------------------------------------------------------------------------
# Test 5: SerialHatchManager Frame Protocol
# -----------------------------------------------------------------------------
def test_serial_hatch_manager_protocol():
    dev = LingCubeDeviceState()
    reg = DeviceSkillRegistry(dev)
    engine = BailianAgentEngine(reg, force_mock=True)
    serial_mgr = SerialHatchManager(port="COM3", agent_engine=engine, device_state=dev)

    # 1. >face=
    f_res = serial_mgr.handle_line(">face=thinking")
    assert any("thinking" in r for r in f_res)
    assert dev.avatar_face == "thinking"

    # 2. >robot=
    r_res = serial_mgr.handle_line('>robot={"action":"roll","direction":"-X"}')
    assert any("robot_ack" in r for r in r_res)

    # 3. >status
    s_res = serial_mgr.handle_line(">status")
    assert any("@status" in r and "StickS3" in r for r in s_res)

    # 4. >chat+= and >chat=
    c1 = serial_mgr.handle_line(">chat+=灵方")
    assert any("chunk_ack" in r for r in c1)
    c2 = serial_mgr.handle_line(">chat=向前翻滚一步")
    assert any('"type": "text"' in r for r in c2)
    assert any('"type": "final"' in r for r in c2)
    assert any('"type": "message_done"' in r for r in c2)


# -----------------------------------------------------------------------------
# Test 6: TunnelSupervisor
# -----------------------------------------------------------------------------
def test_tunnel_supervisor_metadata():
    import shutil
    dist_dir = os.path.join(WORKSPACE_ROOT, ".tmp_test_dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    try:
        supervisor = TunnelSupervisor(local_port=8000, mode="none", dist_dir=dist_dir)
        assert supervisor.get_info()["status"] == "inactive"

        # Simulate active tunnel state persistence
        supervisor.public_url = "https://unit-test.trycloudflare.com"
        supervisor.tool_used = "cloudflare"
        supervisor._persist()

        info = supervisor.get_info()
        assert info["status"] == "active"
        assert info["public_url"] == "https://unit-test.trycloudflare.com"
        assert info["wss_url"] == "wss://unit-test.trycloudflare.com/ws/v1/realtime"

        # Verify file persistence
        agent_json_path = os.path.join(dist_dir, "public_agent_url.json")
        preview_txt_path = os.path.join(dist_dir, "public_preview_url.txt")
        assert os.path.exists(agent_json_path)
        assert os.path.exists(preview_txt_path)

        with open(agent_json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            assert meta["tool"] == "cloudflare"
            assert meta["endpoints"]["fetch_vms"] == "https://unit-test.trycloudflare.com/fetch_vms"
            assert meta["endpoints"]["chat"] == "https://unit-test.trycloudflare.com/api/chat"

        with open(preview_txt_path, "r", encoding="utf-8") as f:
            assert f.read().strip() == "https://unit-test.trycloudflare.com"
    finally:
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir, ignore_errors=True)


# -----------------------------------------------------------------------------
# Test 7: FastAPI REST Endpoints & RPC Dispatch
# -----------------------------------------------------------------------------
@pytest.fixture
def agent_client():
    agent = BailianMuseCloudAgent(
        host="127.0.0.1",
        port=8000,
        enable_serial=False,
        tunnel_mode="none",
        force_mock_llm=True
    )
    client = TestClient(agent.app)
    return client, agent


def test_api_rest_endpoints(agent_client):
    client, agent = agent_client

    # 1. GET /health
    r_h = client.get("/health")
    assert r_h.status_code == 200
    h_data = r_h.json()
    assert h_data["status"] == "ok"
    assert h_data["service"] == "Bailian-Muse-CloudAgent"

    # 2. GET /fetch_vms
    r_vms = client.get("/fetch_vms")
    assert r_vms.status_code == 200
    vms_data = r_vms.json()
    assert "vms" in vms_data
    assert len(vms_data["vms"]) >= 1
    assert vms_data["vms"][0]["agent_type"] == "bailian_qwen_agent"

    # 3. GET /api/device/info
    r_info = client.get("/api/device/info")
    assert r_info.status_code == 200
    info_data = r_info.json()
    assert info_data["device_type"] == "LingCube-MSRR"
    assert "actuators" in info_data

    # 4. GET /api/robot/telemetry
    r_telem = client.get("/api/robot/telemetry")
    assert r_telem.status_code == 200
    assert "roll_deg" in r_telem.json()

    # 5. POST /api/robot/roll
    r_roll = client.post("/api/robot/roll", json={"direction": "+Y", "torque": 0.25})
    assert r_roll.status_code == 200
    assert r_roll.json()["success"] is True

    # 6. POST /api/robot/epm
    time.sleep(0.12)
    r_epm = client.post("/api/robot/epm", json={"face_id": 3, "state": "LATCH"})
    assert r_epm.status_code == 200
    assert 3 in r_epm.json()["docked_faces"]

    # 7. POST /api/robot/morphology
    r_morph = client.post("/api/robot/morphology", json={"morphology": "LingChain"})
    assert r_morph.status_code == 200
    assert r_morph.json()["active_morphology"] == "LingChain"

    # 8. POST /api/robot/reflex
    r_ref = client.post("/api/robot/reflex", json={"reflex_type": "HALTERE_DAMP"})
    assert r_ref.status_code == 200
    assert r_ref.json()["success"] is True

    # 9. POST /api/robot/avatar_face
    r_face = client.post("/api/robot/avatar_face", json={"face": "happy"})
    assert r_face.status_code == 200
    assert r_face.json()["avatar_face"] == "happy"

    # 10. POST /api/chat (standard)
    r_chat = client.post("/api/chat", json={"message": "向左翻滚一步", "session_id": "api_test"})
    assert r_chat.status_code == 200
    chat_json = r_chat.json()
    assert "reply" in chat_json
    assert len(chat_json["tool_calls"]) > 0

    # 11. POST /api/chat (stream: true)
    r_chat_stream = client.post("/api/chat", json={"message": "你好", "stream": True})
    assert r_chat_stream.status_code == 200
    assert "text/event-stream" in r_chat_stream.headers["content-type"]
    sse_text = r_chat_stream.text
    assert "event: message_start" in sse_text
    assert "event: message_done" in sse_text

    # 12. POST /chat/stream & GET /chat/subscribe
    r_cs = client.post("/chat/stream", json={"message": "灵伴你好", "session_id": "sse_sub"})
    assert r_cs.status_code == 200
    msg_id = r_cs.json()["msg_id"]
    r_sub = client.get(f"/chat/subscribe?msg_id={msg_id}")
    assert r_sub.status_code == 200
    assert "message_done" in r_sub.text

    # 13. POST /api/voice/dictation (stream NDJSON)
    sample_rate = 16000
    dummy_audio = struct.pack(f"<{sample_rate // 2}h", *[0] * (sample_rate // 2))
    r_dict = client.post(
        "/api/voice/dictation",
        content=dummy_audio,
        headers={"Content-Type": "audio/x-raw-pcm; rate=16000; format=s16le"}
    )
    assert r_dict.status_code == 200
    ndjson_lines = [json.loads(line) for line in r_dict.text.strip().split("\n") if line]
    assert any(line["type"] == "final" for line in ndjson_lines)

    # 14. POST /api/voice/dictation (JSON format)
    r_dict_json = client.post(
        "/api/voice/dictation?stream=false",
        json={"audio": base64.b64encode(dummy_audio).decode("ascii")},
        headers={"Content-Type": "application/json"}
    )
    assert r_dict_json.status_code == 200
    assert "transcript" in r_dict_json.json()

    # 15. Generic RPC dispatch: GET & POST
    r_rpc_get = client.get("/rpc/gadget-lingcube-msrr.telemetry")
    assert r_rpc_get.status_code == 200
    assert r_rpc_get.json()["status"] == "ok"

    r_rpc_post = client.post("/rpc/gadget-lingcube-msrr.roll", json={"direction": "+X"})
    assert r_rpc_post.status_code == 200
    assert r_rpc_post.json()["status"] == "ok"

    # 16. GET /api/tunnel/info
    r_tun = client.get("/api/tunnel/info")
    assert r_tun.status_code == 200
    assert "status" in r_tun.json()


# -----------------------------------------------------------------------------
# Test 8: WebSocket Realtime Gateway Duplex Stream
# -----------------------------------------------------------------------------
def test_websocket_realtime_gateway(agent_client):
    client, agent = agent_client

    with client.websocket_connect("/ws/v1/realtime") as ws:
        # 1. session.created event
        first_msg = ws.receive_json()
        assert first_msg["type"] == "session.created"

        # 2. session.update
        ws.send_json({
            "type": "session.update",
            "session": {"voice": "cherry", "modalities": ["audio", "text"]}
        })
        upd_msg = ws.receive_json()
        assert upd_msg["type"] == "session.updated"

        # 3. input_audio_buffer.append -> speech_started
        dummy_chunk = base64.b64encode(b"\x00" * 640).decode("ascii")
        ws.send_json({
            "type": "input_audio_buffer.append",
            "audio": dummy_chunk
        })
        m_start = ws.receive_json()
        assert m_start["type"] == "input_audio_buffer.speech_started"
        m_exp1 = ws.receive_json()
        assert m_exp1["type"] == "avatar.expression"
        assert m_exp1["expression"] == "listening"

        # 4. input_audio_buffer.commit -> response generation
        ws.send_json({"type": "input_audio_buffer.commit"})

        # Collect response frames
        received_types = set()
        for _ in range(30):
            try:
                frame = ws.receive_json()
                t = frame.get("type")
                received_types.add(t)
                if t == "response.done":
                    break
            except Exception:
                break

        assert "avatar.expression" in received_types
        assert "response.audio_transcript.delta" in received_types
        assert "response.audio.delta" in received_types
        assert "response.done" in received_types

        # 5. response.cancel (Barge-In)
        ws.send_json({"type": "response.cancel"})
        m_cancel = ws.receive_json()
        assert m_cancel["type"] == "response.cancelled"
        assert m_cancel["reason"] == "barge_in"
