import asyncio
import json
import websockets
import base64

API_KEY = "sk-ws-H.EPHMIMH.PqIK.MEQCIHgyLDXLvnwi_PGoocOu5C-Azgxc8ISga2Mrz3n-DTdxAiBsI8cGPSo2p6JA4WbyHX0YWN8KeBoDZ86Puoqt7YVLug"
URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3.8-omni-flash-realtime"

async def test_voice(voice):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with websockets.connect(URL, additional_headers=headers) as ws:
        c_msg = await ws.recv()
        # session.update
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "voice": voice,
                "modalities": ["text", "audio"]
            }
        }))
        u_msg = await ws.recv()
        u_data = json.loads(u_msg)
        effective_voice = u_data.get("session", {}).get("voice")
        
        # Ask question
        await ws.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "你好，请用一句话做自我介绍。"}]
            }
        }))
        await ws.send(json.dumps({"type": "response.create"}))
        
        audio_deltas = []
        text = ""
        while True:
            ev = json.loads(await ws.recv())
            t = ev.get("type")
            if t == "response.audio.delta":
                audio_deltas.append(ev.get("delta", ""))
            elif t == "response.audio_transcript.delta":
                text += ev.get("delta", "")
            elif t == "response.done":
                break
            elif t == "error":
                print(f"[{voice}] ERROR: {ev}")
                break
        
        raw_pcm = base64.b64decode("".join(audio_deltas))
        print(f"Voice={voice:10s} | AckVoice={effective_voice} | Text='{text}' | PCM bytes={len(raw_pcm)}")
        with open(f"scripts/out_{voice}.pcm", "wb") as f:
            f.write(raw_pcm)

async def main():
    for v in ["Tina", "Chelsie", "Cherry", "Serena", "Cindy", "Raymond"]:
        try:
            await test_voice(v)
        except Exception as e:
            print(f"Failed {v}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
