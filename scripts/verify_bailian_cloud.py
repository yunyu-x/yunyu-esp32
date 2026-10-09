import asyncio
import json
import os
import time
import websockets

def load_bailian_api_key() -> str:
    key = os.environ.get("BAILIAN_API_KEY", "").strip()
    if not key:
        for cand in [".env", os.path.join(os.path.dirname(__file__), "..", ".env")]:
            if os.path.exists(cand):
                try:
                    with open(cand, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("BAILIAN_API_KEY="):
                                key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                                break
                    if key:
                        break
                except Exception:
                    pass
    return key

API_KEY = load_bailian_api_key()
URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen-omni-turbo-realtime"

def ts():
    now = time.time()
    return f"{time.strftime('%H:%M:%S', time.localtime(now))}.{int((now % 1) * 1000):03d}"

async def main():
    print(f"[{ts()}] [STAGE 1: DNS & Socket Open] Target: {URL}")
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    t0 = time.time()
    try:
        async with websockets.connect(URL, additional_headers=headers) as ws:
            t1 = time.time()
            print(f"[{ts()}] [STAGE 2: WSS Handshake OK] TLS + HTTP 101 Handshake latency: {(t1 - t0)*1000:.2f} ms")
            
            # 1. Wait for session.created from server
            msg1 = await asyncio.wait_for(ws.recv(), timeout=5.0)
            t_created = time.time()
            data1 = json.loads(msg1)
            print(f"[{ts()}] [STAGE 3: Session Created RX] Model={data1['session']['model']}, Voice={data1['session']['voice']}")

            import base64, math, struct
            # Synthesize 1.5 seconds of 16kHz 16-bit Mono audio (simulated user voice)
            sample_rate = 16000
            duration = 1.5
            samples = []
            for i in range(int(sample_rate * duration)):
                # Harmonic tone with envelope simulating speech formant
                t = i / sample_rate
                env = math.sin(math.pi * t / duration)
                v = (math.sin(2 * math.pi * 300 * t) * 0.5 + math.sin(2 * math.pi * 600 * t) * 0.5) * env
                samples.append(int(v * 16000))
            raw_pcm = struct.pack(f"<{len(samples)}h", *samples)
            b64_audio = base64.b64encode(raw_pcm).decode("ascii")

            t4 = time.time()
            print(f"[{ts()}] [STAGE 4: Send Audio Chunks] Sending 1.5s PCM16 audio ({len(raw_pcm)} bytes) via input_audio_buffer.append...")
            await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": b64_audio}))
            await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
            print(f"[{ts()}] [STAGE 5: Audio Committed] Sent input_audio_buffer.commit")

            # Listen for server VAD or response events
            create_resp = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            t5 = time.time()
            await ws.send(json.dumps(create_resp))
            print(f"[{ts()}] [STAGE 6: Trigger Response Create] Waiting for streaming audio and text...")

            # 5. Receive streaming deltas & measure first token latency
            first_text_time = None
            first_audio_time = None
            full_text = ""
            total_audio_bytes = 0

            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
                ev = json.loads(raw)
                ev_type = ev.get("type")
                
                if ev_type == "response.audio_transcript.delta":
                    if first_text_time is None:
                        first_text_time = time.time()
                        print(f"[{ts()}] [STAGE 8A: First Text Token TTFT] Latency: {(first_text_time - t5)*1000:.2f} ms | Char: '{ev.get('delta')}'")
                    full_text += ev.get("delta", "")
                elif ev_type == "response.audio.delta":
                    if first_audio_time is None:
                        first_audio_time = time.time()
                        print(f"[{ts()}] [STAGE 8B: First Audio Chunk TTFA] Latency: {(first_audio_time - t5)*1000:.2f} ms")
                    total_audio_bytes += len(ev.get("delta", ""))
                elif ev_type == "response.done":
                    t_done = time.time()
                    print(f"[{ts()}] [STAGE 9: Response Done] Total duration: {(t_done - t5)*1000:.2f} ms")
                    print(f"       AI Full Reply: \"{full_text}\"")
                    print(f"       Total Audio Chunks Base64 Size: {total_audio_bytes} bytes")
                    break
                elif ev_type == "error":
                    print(f"[{ts()}] [ERROR RX] {json.dumps(ev, ensure_ascii=False)}")
                    break
                    
    except Exception as e:
        print(f"[{ts()}] [EXCEPTION] {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
