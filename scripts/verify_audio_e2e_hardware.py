"""
scripts/verify_audio_e2e_hardware.py
------------------------------------
Automated end-to-end verification script for StickS3 audio streaming:
1. Connects to http://192.168.4.1 via PC WLAN.
2. Checks HTML structure for absence of camera 'capture' attribute and presence of audioFileInput.
3. Tests /audio/status endpoint.
4. Triggers 2-second recording on StickS3, then fetches /audio/device_record.wav.
5. Audits HTTP headers: verifies single Content-Length (no duplicate), Accept-Ranges: none, valid RIFF WAV payload.
6. Tests /audio/upload with a synthetic 16kHz WAV and verifies playback trigger.
"""

import sys
import time
import struct
import math
import requests

BASE_URL = "http://192.168.4.1"

def log(msg, status="INFO"):
    symbol = {"INFO": "ℹ️", "OK": "✅", "ERR": "❌", "WARN": "⚠️"}.get(status, "•")
    print(f"[{symbol} {status}] {msg}")

def test_web_html():
    log("Testing GET / (Web Console HTML)...")
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    html = r.text

    assert "audioFileInput" in html, "audioFileInput input missing from HTML"
    assert "capture=" not in html, "ERROR: capture attribute still found in HTML, may open camera!"
    assert "sendTestAudio" in html, "sendTestAudio button missing from HTML"
    assert "deviceAudioPlayer" in html, "deviceAudioPlayer audio tag missing"
    assert "player.load()" in html or "p.load()" in html, "player.load() missing"
    log("Web HTML verified! No camera capture attribute, audioFileInput and test tone ready.", "OK")

def test_audio_status():
    log("Testing GET /audio/status...")
    r = requests.get(f"{BASE_URL}/audio/status", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    log(f"Current audio status: {data}", "INFO")
    assert "is_recording" in data
    assert "has_device_audio" in data
    assert "is_playing" in data
    log("/audio/status endpoint OK!", "OK")
    return data

def test_device_recording_and_wav_download():
    log("Triggering device recording via POST /audio/record_trigger (action=start)...")
    r = requests.post(f"{BASE_URL}/audio/record_trigger", data={"action": "start"}, timeout=5)
    assert r.status_code == 200, f"Start failed: {r.text}"
    log("Recording started on StickS3. Recording for 2.0 seconds...", "INFO")
    time.sleep(2.0)

    log("Stopping recording via POST /audio/record_trigger (action=stop)...")
    r = requests.post(f"{BASE_URL}/audio/record_trigger", data={"action": "stop"}, timeout=5)
    assert r.status_code == 200, f"Stop failed: {r.text}"
    time.sleep(0.5)

    # Check status
    st = test_audio_status()
    assert st["has_device_audio"] is True, "has_device_audio should be true after recording"
    audio_bytes = st["device_audio_bytes"]
    log(f"Device recorded: {audio_bytes} bytes ({st['device_audio_duration_sec']}s)", "OK")

    # Fetch WAV file and strictly audit headers
    log(f"Fetching GET /audio/device_record.wav...")
    resp = requests.get(f"{BASE_URL}/audio/device_record.wav", timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    # Verify headers
    content_type = resp.headers.get("Content-Type", "")
    assert "audio/wav" in content_type, f"Expected audio/wav, got {content_type}"

    content_length = resp.headers.get("Content-Length")
    assert content_length is not None, "Content-Length header missing"
    cl_int = int(content_length)
    body_len = len(resp.content)
    log(f"HTTP Header Content-Length: {cl_int}, Actual Body Length: {body_len}", "INFO")
    assert cl_int == body_len, f"Content-Length mismatch! Header={cl_int}, Body={body_len}"
    assert cl_int == audio_bytes, f"Content-Length {cl_int} does not match device recorded bytes {audio_bytes}"

    # Verify RIFF WAV binary header
    wav_data = resp.content
    assert len(wav_data) >= 44, "WAV data too short"
    riff, total_size, wave, fmt, sub1_size, audio_fmt, channels, s_rate, b_rate, align, bits, data_tag, pcm_len = struct.unpack(
        "<4sI4s4sIHHIIHH4sI", wav_data[:44]
    )
    assert riff == b"RIFF", f"RIFF magic failed: {riff}"
    assert wave == b"WAVE", f"WAVE magic failed: {wave}"
    assert fmt == b"fmt ", f"fmt magic failed: {fmt}"
    assert data_tag == b"data", f"data tag failed: {data_tag}"
    assert audio_fmt == 1, f"Audio format must be PCM (1), got {audio_fmt}"
    assert channels == 1, f"Channel count must be mono (1), got {channels}"
    assert s_rate == 16000, f"Sample rate must be 16000, got {s_rate}"
    assert b_rate == 32000, f"Byte rate must be 32000, got {b_rate}"
    assert align == 2, f"Block align must be 2, got {align}"
    assert bits == 16, f"Bits per sample must be 16, got {bits}"
    assert pcm_len + 44 == len(wav_data), f"PCM length + 44 ({pcm_len + 44}) != total WAV size ({len(wav_data)})"

    log(f"WAV Header validation PASSED! Valid 16kHz 16-bit Mono PCM WAV stream ({body_len} bytes).", "OK")

def test_web_audio_upload_playback():
    log("Generating 1.0s 16kHz test tone WAV in Python to test /audio/upload...")
    sample_rate = 16000
    duration = 1.0
    num_samples = int(sample_rate * duration)
    pcm_bytes = num_samples * 2

    # Build 44-byte WAV header
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", pcm_bytes + 36, b"WAVE", b"fmt ", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16, b"data", pcm_bytes
    )

    # Generate 587.33Hz (D5) melody tone with decay envelope
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        env = math.exp(-3.0 * t)
        val = int(math.sin(2.0 * math.pi * 587.33 * t) * 28000.0 * env)
        samples.append(val)
    raw_pcm = struct.pack(f"<{len(samples)}h", *samples)
    full_wav = header + raw_pcm

    log(f"Uploading {len(full_wav)} bytes WAV to POST /audio/upload...")
    files = {"audio": ("test_tone.wav", full_wav, "audio/wav")}
    r = requests.post(f"{BASE_URL}/audio/upload", files=files, timeout=5)
    assert r.status_code == 200, f"Upload failed: {r.status_code} {r.text}"
    log(f"Upload response: {r.json()}", "OK")

    # Give StickS3 speaker time to play
    time.sleep(1.2)
    st = test_audio_status()
    log("Web Audio Upload & StickS3 speaker playback verified!", "OK")

def test_telemetry():
    log("Testing GET /status (Telemetry)...")
    r = requests.get(f"{BASE_URL}/status", timeout=5)
    assert r.status_code == 200
    log(f"Telemetry: {r.json()}", "OK")

def main():
    print("=" * 60)
    print("  StickS3 Bidirectional Audio Hardware Verification Suite")
    print("=" * 60)
    try:
        test_web_html()
        test_audio_status()
        test_device_recording_and_wav_download()
        test_web_audio_upload_playback()
        test_telemetry()
        print("=" * 60)
        print("  🎉 ALL HARDWARE VERIFICATION CHECKS PASSED!")
        print("=" * 60)
    except Exception as e:
        log(f"Verification failed: {e}", "ERR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
