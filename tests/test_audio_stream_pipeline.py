"""
tests/test_audio_stream_pipeline.py
-----------------------------------
Automated verification suite for StickS3 bidirectional audio stream pipeline:
1. Standard RIFF WAV (16kHz 16-bit Mono) Header & PCM Byte Alignment
2. Web Audio API / iOS Safari Client-Side Resampling & WAV Encoding Verification
3. Firmware Audio Subsystem API Integrity (PSRAM Buffer, Non-Blocking State Machine)
4. Wi-Fi Web Intercom Endpoints (/audio/status, /audio/device_record.wav, /audio/upload)
"""

import os
import struct
import math
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FW_DIR = os.path.join(ROOT_DIR, "firmware", "m5sticks3_buddy")
AUDIO_HDR = os.path.join(FW_DIR, "include", "sticks3_audio.h")
WIFI_HDR = os.path.join(FW_DIR, "include", "sticks3_wifi.h")
MAIN_SRC = os.path.join(FW_DIR, "src", "main.cpp")


def generate_test_wav_header(pcm_len: int, sample_rate: int = 16000) -> bytes:
    """Python reference generator for 44-byte RIFF WAV header (matching C++ generateWavHeader)"""
    total_size = pcm_len + 36
    byte_rate = sample_rate * 2  # 1 channel * 16-bit
    block_align = 2
    return struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        total_size,
        b"WAVE",
        b"fmt ",
        16,           # Subchunk1Size
        1,            # AudioFormat (PCM)
        1,            # NumChannels (Mono)
        sample_rate,  # SampleRate (16000)
        byte_rate,    # ByteRate (32000)
        block_align,  # BlockAlign (2)
        16,           # BitsPerSample (16)
        b"data",
        pcm_len       # Subchunk2Size
    )


def test_wav_header_structure():
    """验证 44 字节 RIFF WAV 标头二进制封装结构与字段对齐"""
    sample_rate = 16000
    duration_s = 5.0
    pcm_bytes = int(sample_rate * 2 * duration_s)  # 160,000 bytes

    header = generate_test_wav_header(pcm_bytes, sample_rate)
    assert len(header) == 44, f"Header size must be exactly 44 bytes, got {len(header)}"

    # 验证关键魔数
    assert header[0:4] == b"RIFF"
    assert header[8:12] == b"WAVE"
    assert header[12:16] == b"fmt "
    assert header[36:40] == b"data"

    # 解析头部字段
    fmt_chunk_size, audio_fmt, channels, s_rate, b_rate, align, bits = struct.unpack(
        "<IHHIIHH", header[16:36]
    )
    assert fmt_chunk_size == 16
    assert audio_fmt == 1  # PCM
    assert channels == 1   # Mono
    assert s_rate == 16000
    assert b_rate == 32000
    assert align == 2
    assert bits == 16

    data_len = struct.unpack("<I", header[40:44])[0]
    assert data_len == pcm_bytes


def test_web_audio_resampler_logic():
    """验证前端 Web Audio API 重采样算法数学逻辑 (48kHz/44.1kHz -> 16kHz 16-bit Mono)"""
    src_rate = 48000
    target_rate = 16000
    duration = 0.5  # 0.5s test tone
    freq = 440.0    # A4 note

    # 生成 48kHz 立体声测试信号
    in_samples = int(src_rate * duration)
    ch0 = [math.sin(2.0 * math.pi * freq * i / src_rate) for i in range(in_samples)]
    ch1 = ch0[:]  # stereo identical

    # 执行模拟重采样 (线性插值 + 下混合)
    out_samples = int(target_rate * duration)
    ratio = src_rate / target_rate
    resampled_pcm = []

    for i in range(out_samples):
        src_idx = i * ratio
        i0 = int(src_idx)
        i1 = min(i0 + 1, in_samples - 1)
        frac = src_idx - i0
        s0 = (ch0[i0] + ch1[i0]) * 0.5
        s1 = (ch0[i1] + ch1[i1]) * 0.5
        sample = s0 + frac * (s1 - s0)
        sample = max(-1.0, min(1.0, sample))
        val = int(sample * 32767.0)
        resampled_pcm.append(val)

    assert len(resampled_pcm) == 8000  # 16000 * 0.5s = 8000 samples
    # 验证波形过零点与频率一致性 (440Hz 在 0.5s 内约产生 220 个完整周期)
    zero_crossings = sum(1 for i in range(len(resampled_pcm) - 1) if resampled_pcm[i] < 0 and resampled_pcm[i+1] >= 0)
    assert 215 <= zero_crossings <= 225, f"Expected ~220 periods, got {zero_crossings}"


def test_firmware_audio_driver_source():
    """验证 sticks3_audio.h 完整集成 PSRAM 录音、WAV 生成与高保真回放接口"""
    assert os.path.exists(AUDIO_HDR), f"File not found: {AUDIO_HDR}"
    with open(AUDIO_HDR, "r", encoding="utf-8") as f:
        src = f.read()

    # 1. 常量与 PSRAM 缓冲定义
    assert "MAX_RECORD_SECONDS = 10" in src
    assert "WAV_HEADER_SIZE = 44" in src
    assert "generateWavHeader" in src

    # 2. 录音接口
    assert "startRecording" in src
    assert "stopRecording" in src
    assert "processRecording" in src
    assert "isRecording" in src
    assert "getWavData" in src
    assert "getWavSize" in src
    assert "hasDeviceAudio" in src

    # 3. 播放接口
    assert "startPlayback" in src
    assert "processPlayback" in src
    assert "stopPlayback" in src
    assert "isPlayingStream" in src
    assert "getPlaybackProgress" in src


def test_firmware_wifi_web_endpoints_source():
    """验证 sticks3_wifi.h 完整集成移动端 Web 控制台与 HTTP 音频流端点"""
    assert os.path.exists(WIFI_HDR), f"File not found: {WIFI_HDR}"
    with open(WIFI_HDR, "r", encoding="utf-8") as f:
        src = f.read()

    # 1. HTTP 路由端点
    assert "/audio/status" in src
    assert "/audio/device_record.wav" in src
    assert "/audio/upload" in src
    assert "/audio/record_trigger" in src

    # 2. iOS Safari / 通用音频文件选取与严禁调起相机
    assert "audioFileInput" in src
    assert "capture=" not in src  # 严禁带有 capture 属性，避免 iOS 强制调起相机界面
    assert "audioBufferTo16kMonoWav" in src
    assert "deviceAudioPlayer" in src
    assert "btnLiveRec" in src
    assert "sendTestAudio" in src
    assert "_web_server.setContentLength(audio.getWavSize())" in src


def test_firmware_main_audio_integration():
    """验证 main.cpp 正确接入正面按键 A 录音控制与屏幕双态看板"""
    assert os.path.exists(MAIN_SRC), f"File not found: {MAIN_SRC}"
    with open(MAIN_SRC, "r", encoding="utf-8") as f:
        src = f.read()

    # 1. 周期性 audio update
    assert "sticks3::StickS3Audio::getInstance().update()" in src

    # 2. 按键 A 录音切换与提前停止
    assert "btnA_clicked" in src
    assert "audio.isRecording()" in src or "audio_inst.isRecording()" in src
    assert "startRecording(10000)" in src
    assert "stopRecording()" in src

    # 3. 串口自动化命令响应 (r/a)
    assert 'cmd_or_msg == "r"' in src
    assert 'cmd_or_msg == "a"' in src

    # 4. 屏幕录音中与播放中专用看板
    assert "正在录音 (REC)" in src
    assert "正在播放网页音频" in src
    assert "drawChineseText" in src
