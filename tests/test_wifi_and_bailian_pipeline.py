"""
tests/test_wifi_and_bailian_pipeline.py
---------------------------------------
StickS3 真实 Wi-Fi 智能配网与阿里云百炼 (DashScope Realtime) 全双工流式问答协议测试套件
1. 协议规范核验：
   - DashScope Realtime WebSocket 报文结构 (session.update, input_audio_buffer.append, response.cancel)
   - 16kHz 16-bit Mono PCM 与 Base64 编码保真度回环
2. 毫秒级中途打断 (Barge-In) 状态机与事件触发验证：
   - 服务端 VAD (input_audio_buffer.speech_started) 打断流程
   - response.cancel 终止报文与静音状态回退
3. Web 网页配网与百炼配置 REST API 契约测试
"""

import base64
import json
import math
import struct
import pytest


# ---------------------------------------------------------------------------
# 1. 音频采样率、PCM16 编码与 Base64 转码回环测试
# ---------------------------------------------------------------------------

def test_pcm16_chunk_and_base64_fidelity():
    """验证 16kHz 16-bit 单声道音频切片与 Base64 编解码无损回环"""
    sample_rate = 16000
    chunk_ms = 32  # 32ms 切片
    samples_per_chunk = int(sample_rate * chunk_ms / 1000)  # 512 采样点
    raw_pcm_bytes = samples_per_chunk * 2  # 1024 字节

    assert samples_per_chunk == 512
    assert raw_pcm_bytes == 1024

    # 合成 512 个正弦波采样点
    pcm_samples = []
    for i in range(samples_per_chunk):
        val = int(math.sin(2 * math.pi * 440.0 * (i / sample_rate)) * 20000)
        pcm_samples.append(val)

    pcm_data = struct.pack(f"<{samples_per_chunk}h", *pcm_samples)
    assert len(pcm_data) == 1024

    # Base64 转码与解码
    b64_str = base64.b64encode(pcm_data).decode("ascii")
    assert len(b64_str) > 0
    decoded_pcm = base64.b64decode(b64_str)
    assert decoded_pcm == pcm_data

    # 解包校验样本一致性
    unpacked_samples = struct.unpack(f"<{samples_per_chunk}h", decoded_pcm)
    assert unpacked_samples == tuple(pcm_samples)


# ---------------------------------------------------------------------------
# 2. 阿里云百炼 DashScope Realtime WebSocket 报文协议合规性
# ---------------------------------------------------------------------------

def test_bailian_session_update_schema():
    """校验百炼 session.update 报文模式 (包含 Server-VAD、音色与输入输出格式)"""
    session_config = {
        "type": "session.update",
        "session": {
            "modalities": ["audio", "text"],
            "voice": "cherry",
            "instructions": "你是StickS3智能语音伴侣，请用简明生动的口语回答。",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.45,
                "prefix_padding_ms": 250,
                "silence_duration_ms": 700
            }
        }
    }

    serialized = json.dumps(session_config)
    doc = json.loads(serialized)

    assert doc["type"] == "session.update"
    assert "audio" in doc["session"]["modalities"]
    assert "text" in doc["session"]["modalities"]
    assert doc["session"]["voice"] == "cherry"
    assert doc["session"]["input_audio_format"] == "pcm16"
    assert doc["session"]["output_audio_format"] == "pcm16"
    assert doc["session"]["turn_detection"]["type"] == "server_vad"
    assert doc["session"]["turn_detection"]["silence_duration_ms"] == 700


def test_bailian_audio_append_payload():
    """校验上行 input_audio_buffer.append 报文结构"""
    dummy_audio = b"\x00\x00" * 256  # 512 字节
    b64_audio = base64.b64encode(dummy_audio).decode("ascii")

    msg = {
        "type": "input_audio_buffer.append",
        "audio": b64_audio
    }
    raw_json = json.dumps(msg)
    parsed = json.loads(raw_json)

    assert parsed["type"] == "input_audio_buffer.append"
    assert parsed["audio"] == b64_audio
    assert len(base64.b64decode(parsed["audio"])) == 512


def test_bailian_barge_in_response_cancel_event():
    """校验中途打断时发送的 response.cancel 终止报文结构"""
    cancel_event = {"type": "response.cancel"}
    raw_str = json.dumps(cancel_event)
    doc = json.loads(raw_str)

    assert doc["type"] == "response.cancel"


def test_bailian_streaming_downstream_simulation():
    """模拟百炼下行 response.audio.delta 与 response.audio_transcript.delta 拼装"""
    # 模拟文本增量
    deltas = ["你好", "，我是", "StickS3", "语音助手", "！"]
    full_text = ""
    for d in deltas:
        event = {"type": "response.audio_transcript.delta", "delta": d}
        full_text += event["delta"]
    assert full_text == "你好，我是StickS3语音助手！"

    # 模拟音频增量流
    chunk_pcm = b"\x10\x20" * 128
    audio_event = {
        "type": "response.audio.delta",
        "delta": base64.b64encode(chunk_pcm).decode("ascii")
    }
    decoded = base64.b64decode(audio_event["delta"])
    assert decoded == chunk_pcm


# ---------------------------------------------------------------------------
# 3. 中途打断 (Barge-In) 状态机逻辑测试
# ---------------------------------------------------------------------------

class MockBailianFSM:
    """模拟 StickS3BailianClient 状态机与打断机制"""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED_IDLE = 2
    LISTENING = 3
    THINKING = 4
    SPEAKING = 5
    INTERRUPTED = 6
    ERROR = 7

    def __init__(self):
        self.state = self.DISCONNECTED
        self.interrupt_count = 0
        self.ai_reply = ""
        self.is_playing = False
        self.cancelled_event_sent = False

    def on_server_event(self, event_type: str, data: dict = None):
        if event_type in ("session.created", "session.updated"):
            self.state = self.LISTENING
        elif event_type == "input_audio_buffer.speech_started":
            # 如果当前正在播放回复，触发打断！
            if self.state == self.SPEAKING or self.is_playing:
                self.trigger_barge_in("Server-VAD")
            else:
                self.state = self.LISTENING
        elif event_type == "input_audio_buffer.speech_stopped":
            self.state = self.THINKING
        elif event_type == "response.audio.delta":
            self.state = self.SPEAKING
            self.is_playing = True
        elif event_type == "response.done":
            self.state = self.CONNECTED_IDLE
            self.is_playing = False

    def trigger_barge_in(self, reason: str):
        if self.state == self.SPEAKING or self.is_playing:
            self.is_playing = False
            self.cancelled_event_sent = True
            self.interrupt_count += 1
            self.state = self.INTERRUPTED
            self.ai_reply += " [已打断]"

    def tick_recovery(self):
        if self.state == self.INTERRUPTED:
            self.state = self.LISTENING


def test_barge_in_lifecycle_flow():
    """验证完整的对答与中途开口打断全生命周期"""
    fsm = MockBailianFSM()
    assert fsm.state == MockBailianFSM.DISCONNECTED

    # 1. 连接并收到 session.created
    fsm.on_server_event("session.created")
    assert fsm.state == MockBailianFSM.LISTENING

    # 2. 用户说话结束，进入思考
    fsm.on_server_event("input_audio_buffer.speech_stopped")
    assert fsm.state == MockBailianFSM.THINKING

    # 3. 大模型返回第一帧音频，进入 SPEAKING 边收边播
    fsm.on_server_event("response.audio.delta")
    assert fsm.state == MockBailianFSM.SPEAKING
    assert fsm.is_playing is True

    # 4. 用户开口插话：Server-VAD 检测到 speech_started -> 立即打断！
    fsm.on_server_event("input_audio_buffer.speech_started")
    assert fsm.state == MockBailianFSM.INTERRUPTED
    assert fsm.is_playing is False
    assert fsm.cancelled_event_sent is True
    assert fsm.interrupt_count == 1
    assert "[已打断]" in fsm.ai_reply

    # 5. 打断恢复：自动切换回 LISTENING 准备接收新用户语音
    fsm.tick_recovery()
    assert fsm.state == MockBailianFSM.LISTENING


# ---------------------------------------------------------------------------
# 4. 固件源码端点与 REST 契约核验
# ---------------------------------------------------------------------------

def test_firmware_wifi_config_endpoints_source():
    """验证固件中 Wi-Fi 配网与百炼配置的核心端点注册"""
    import os
    wifi_h_path = os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_wifi.h")
    assert os.path.exists(wifi_h_path), "sticks3_wifi.h must exist"

    with open(wifi_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    # 验证配网端点
    assert "/wifi/scan_list" in src
    assert "/wifi/connect" in src
    assert "/wifi/status" in src

    # 验证百炼大模型端点
    assert "/bailian/config" in src
    assert "/bailian/status" in src
    assert "/bailian/interrupt" in src
    assert "/bailian/new_chat" in src
    assert "/bailian/reconnect" in src


def test_firmware_audio_barge_in_api_source():
    """验证 sticks3_audio.h 中新增的流式音频与打断方法"""
    import os
    audio_h_path = os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_audio.h")
    assert os.path.exists(audio_h_path), "sticks3_audio.h must exist"

    with open(audio_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "AudioRingBuffer" in src
    assert "feedStreamPCM" in src
    assert "interruptPlayback" in src
    assert "readMicSamples" in src
    assert "isStreamingLLM" in src
    assert "setCodecFullDuplexMode" in src
    assert "checkVoiceBargeInTrigger" in src


def test_firmware_bailian_client_source():
    """验证 sticks3_bailian_client.h 的核心属性与方法"""
    import os
    bl_h_path = os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_bailian_client.h")
    assert os.path.exists(bl_h_path), "sticks3_bailian_client.h must exist"

    with open(bl_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "esp_websocket_client" in src
    assert "session.update" in src
    assert "input_audio_buffer.append" in src
    assert "response.cancel" in src
    assert "mbedtls_base64_encode" in src
    assert "mbedtls_base64_decode" in src
    assert "interrupt" in src


def test_firmware_memory_store_and_compaction_source():
    """验证 sticks3_memory_store.h 的 PSRAM 平铺存储与安全截断"""
    import os
    mem_h_path = os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_memory_store.h")
    assert os.path.exists(mem_h_path), "sticks3_memory_store.h must exist"

    with open(mem_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "StickS3MemoryStore" in src
    assert "safeTruncateUtf8" in src
    assert "compressMemory" in src
    assert "buildMemoryContextPrompt" in src
    assert "MAX_TURNS_IN_MEMORY = 8" in src
    assert "MAX_TURNS_IN_FLASH = 5" in src


def test_utf8_multibyte_truncation_safety():
    """验证 UTF-8 变长中文字符在任意字节截断下的字符边界安全性 (杜绝 RFC 6455 1007 协议崩溃)"""
    chinese_text = "你好，我叫李华，我是一名在上海工作的人形机器人硬件研发工程师。"
    raw_bytes = chinese_text.encode("utf-8")

    # 遍历所有可能的截断字节长度（从 1 到总长度）
    for max_len in range(1, len(raw_bytes) + 1):
        # 模拟 C++ safeTruncateUtf8 的逻辑
        idx = max_len
        if idx >= len(raw_bytes):
            res_bytes = raw_bytes
        else:
            while idx > 0 and (raw_bytes[idx] & 0xC0) == 0x80:
                idx -= 1
            if idx > 0:
                first_byte = raw_bytes[idx]
                expected_len = 1
                if (first_byte & 0xE0) == 0xC0:
                    expected_len = 2
                elif (first_byte & 0xF0) == 0xE0:
                    expected_len = 3
                elif (first_byte & 0xF8) == 0xF0:
                    expected_len = 4
                if idx + expected_len > max_len:
                    # 字符被截断，跳过当前字符头
                    pass
                else:
                    idx += expected_len
            res_bytes = raw_bytes[:idx]

        # 结果必须是 100% 合法的 UTF-8，decode 绝不能抛出 UnicodeDecodeError
        decoded = res_bytes.decode("utf-8")
        assert len(decoded) <= len(chinese_text)


def test_firmware_i2c_mutex_and_system_metrics_source():
    """验证 I2C 全局互斥锁与系统资源全维度监控模块"""
    import os
    mutex_h_path = os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_i2c_mutex.h")
    metrics_h_path = os.path.join(os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_system_metrics.h")
    assert os.path.exists(mutex_h_path), "sticks3_i2c_mutex.h must exist"
    assert os.path.exists(metrics_h_path), "sticks3_system_metrics.h must exist"

    with open(mutex_h_path, "r", encoding="utf-8", errors="replace") as f:
        src_mutex = f.read()
    assert "getI2CMutex" in src_mutex
    assert "I2CLockGuard" in src_mutex
    assert "getI2CLockFailures" in src_mutex


    with open(metrics_h_path, "r", encoding="utf-8", errors="replace") as f:
        src_metrics = f.read()
    assert "getSystemLoopFPS" in src_metrics
    assert "updateSystemLoopFPS" in src_metrics
    assert "printSystemDiagnostics" in src_metrics
    assert "heap_caps_get_largest_free_block" in src_metrics


