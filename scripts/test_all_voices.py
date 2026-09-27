import asyncio
import json
import websockets

API_KEY = "sk-ws-H.EPHMIMH.PqIK.MEQCIHgyLDXLvnwi_PGoocOu5C-Azgxc8ISga2Mrz3n-DTdxAiBsI8cGPSo2p6JA4WbyHX0YWN8KeBoDZ86Puoqt7YVLug"
URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3.8-omni-flash-realtime"

async def check(voice):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with websockets.connect(URL, additional_headers=headers) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "session.update", "session": {"voice": voice, "modalities": ["text", "audio"]}}))
        upd = await ws.recv()
        await ws.send(json.dumps({"type": "conversation.item.create", "item": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "你好"}]}}))
        await ws.send(json.dumps({"type": "response.create"}))
        
        while True:
            ev = json.loads(await ws.recv())
            t = ev.get("type")
            if t == "response.done":
                print(f"{voice:12s}: SUCCESS")
                break
            elif t == "error":
                msg = ev.get("error", {}).get("message")
                print(f"{voice:12s}: ERROR -> {msg}")
                break

async def main():
    voices = ["Tina", "Serena", "Cindy", "Raymond", "Zane", "Katerina", "Mia", "Chloe", "Chelsie", "Cherry", "Ethan"]
    for v in voices:
        try:
            await check(v)
        except Exception as e:
            print(f"{v}: exception {e}")

if __name__ == "__main__":
    asyncio.run(main())
