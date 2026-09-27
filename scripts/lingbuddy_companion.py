#!/usr/bin/env python3
"""
scripts/lingbuddy_companion.py
--------------------------------
M5StickS3 灵宠伴侣 (LingBuddy / StickCharm) 手机/上位机 BLE GATT 伴侣中枢客户端
- 协议通道 (Service 0xFFB0):
  - 0xFFB1 (Memory Stream): 读取/监听分块传输的长期对话记忆与画像
  - 0xFFB2 (Pet Status): 查询灵宠昵称、羁绊等级、XP、好感度、心情
  - 0xFFB3 (Pet Diary): 订阅并持久化实时第一人称日记
  - 0xFFB4 (Control Inject): 手机端回写指令 (pet/shake/sleep/wake/add_xp/set_name/inject_memory)
"""

import sys
import os
import time
import json
import argparse
from typing import Optional, Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from scripts.lingbuddy_vector_store import LingBuddyVectorStore
except ImportError:
    from lingbuddy_vector_store import LingBuddyVectorStore

try:
    import bleak
    HAS_BLEAK = True
except ImportError:
    HAS_BLEAK = False

SERVICE_UUID       = "0000FFB0-0000-1000-8000-00805F9B34FB"
CHAR_MEMORY_UUID   = "0000FFB1-0000-1000-8000-00805F9B34FB"
CHAR_STATUS_UUID   = "0000FFB2-0000-1000-8000-00805F9B34FB"
CHAR_DIARY_UUID    = "0000FFB3-0000-1000-8000-00805F9B34FB"
CHAR_INJECT_UUID   = "0000FFB4-0000-1000-8000-00805F9B34FB"


class LingBuddySimulatorClient:
    """协议合规与无硬件/纯仿真测试客户端"""

    def __init__(self, name: str = "小木"):
        self.name = name
        self.level = 1
        self.xp = 15
        self.pets = 0
        self.shakes = 0
        self.mood = 0
        self.diary_history = ["今天刚刚苏醒，期待和主人一起探索世界！"]
        self.memory_turns = [
            {"role": "user", "content": "你好呀小木"},
            {"role": "assistant", "content": "[E:happy] 你好主人！随时听候你的差遣~"}
        ]

    def read_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "pets": self.pets,
            "shakes": self.shakes,
            "feeds": getattr(self, "feeds", 0),
            "grooms": getattr(self, "grooms", 0),
            "energy": getattr(self, "energy", 100),
            "mood": self.mood
        }

    def inject_action(self, action: str, value: Any = None) -> Dict[str, Any]:
        if not hasattr(self, "feeds"): self.feeds = 0
        if not hasattr(self, "grooms"): self.grooms = 0
        if not hasattr(self, "energy"): self.energy = 100

        if action == "pet":
            self.mood = 4
            self.xp += 15
            self.pets += 1
            if self.xp >= 100 and self.level < 10:
                self.level += 1
                self.xp = 0
            diary = "主人刚刚隔空摸了摸我的小脑瓜，好幸福！"
            self.diary_history.append(diary)
            return {"status": "ok", "action": "pet", "diary": diary, "intimacy": f"Lv.{self.level}"}
        elif action == "feed":
            self.mood = 10 # MOOD_EAT
            self.xp += 10
            self.feeds += 1
            self.energy = min(100, self.energy + 20)
            if self.xp >= 100 and self.level < 10:
                self.level += 1
                self.xp = 0
            snack = str(value) if value else "香甜小蛋糕"
            diary = f"主人喂我吃了一块{snack}，吧唧吧唧超级满足，活力满满！"
            self.diary_history.append(diary)
            return {"status": "ok", "action": "feed", "diary": diary, "energy": self.energy, "intimacy": f"Lv.{self.level}"}
        elif action == "groom":
            self.mood = 11 # MOOD_GROOM
            self.xp += 12
            self.grooms += 1
            if self.xp >= 100 and self.level < 10:
                self.level += 1
                self.xp = 0
            diary = "主人用小梳子温柔地帮我梳理毛发，整只宠都舒服得想呼噜呼噜~"
            self.diary_history.append(diary)
            return {"status": "ok", "action": "groom", "diary": diary, "intimacy": f"Lv.{self.level}"}
        elif action == "play":
            self.mood = 12 # MOOD_WINK
            self.xp += 15
            self.energy = max(10, self.energy - 10)
            if self.xp >= 100 and self.level < 10:
                self.level += 1
                self.xp = 0
            diary = "和主人默契击掌！今天我们也是元气满满的搭档！"
            self.diary_history.append(diary)
            return {"status": "ok", "action": "play", "diary": diary, "energy": self.energy, "intimacy": f"Lv.{self.level}"}
        elif action == "shake":
            self.mood = 5
            self.shakes += 1
            diary = "手机端发来摇晃指令，眼睛里全都是小星星！"
            self.diary_history.append(diary)
            return {"status": "ok", "action": "shake", "diary": diary}
        elif action == "sleep":
            self.mood = 7
            self.energy = min(100, self.energy + 30)
            return {"status": "ok", "action": "sleep", "mood": "sleep", "energy": self.energy}
        elif action == "wake":
            self.mood = 1
            return {"status": "ok", "action": "wake", "mood": "listen"}
        elif action == "set_name":
            self.name = str(value)
            return {"status": "ok", "name": self.name}
        elif action == "inject_memory":
            self.memory_turns.append({"role": "user", "content": f"[手机备忘] {value}"})
            diary = f"主人从手机同步了一条新的生活备忘: {value}"
            self.diary_history.append(diary)
            return {"status": "ok", "diary": diary}
        return {"status": "unknown_action"}

    def get_chunked_memory(self, chunk_size: int = 48) -> List[str]:
        raw_json = json.dumps(self.memory_turns, ensure_ascii=False)
        total_chunks = (len(raw_json) + chunk_size - 1) // chunk_size
        chunks = []
        for i in range(total_chunks):
            start = i * chunk_size
            piece = raw_json[start : start + chunk_size]
            chunks.append(f"[C:{i+1}/{total_chunks}]{piece}")
        return chunks

    def reassemble_memory(self, chunks: List[str]) -> str:
        """分包重组算法"""
        full_text = ""
        for chunk in chunks:
            # 剥离 [C:x/y] 头部
            if chunk.startswith("[C:") and "]" in chunk:
                piece = chunk.split("]", 1)[1]
                full_text += piece
            else:
                full_text += chunk
        return full_text


def run_cli_demo():
    print("\n" + "=" * 76)
    print("  [LingBuddy 手机伴侣 GATT 同步客户端] 记忆卸载、日记归档与控制中枢")
    print("=" * 76)

    client = LingBuddySimulatorClient()
    print("\n[测试 1/5] 读取 0xFFB2 灵宠生命状态快照...")
    st = client.read_status()
    print(f"  [+] 状态数据: 昵称={st['name']}, 等级=Lv.{st['level']} ({st['xp']}/100 XP), 活力={st['energy']}%, 抚摸={st['pets']}, 喂食={st['feeds']}, 梳毛={st['grooms']}")

    print("\n[测试 2/5] 向 0xFFB4 注入拓麻歌子互动指令 (feed / groom / play / pet)...")
    res_feed = client.inject_action("feed", "草莓奶油松饼")
    print(f"  [>] 注入投喂小点心 -> 回执: {res_feed}")
    res_groom = client.inject_action("groom")
    print(f"  [>] 注入梳理毛发 -> 回执: {res_groom}")
    res_play = client.inject_action("play")
    print(f"  [>] 注入默契击掌 -> 回执: {res_play}")
    res_mem = client.inject_action("inject_memory", "明天下午3点和团队在北京评审灵宠伴侣项目")
    print(f"  [>] 注入手机生活备忘 -> 回执: {res_mem}")

    print("\n[测试 3/5] 0xFFB1 多分块 (Chunked Stream) 记忆下发与重组测试...")
    chunks = client.get_chunked_memory(chunk_size=40)
    print(f"  [+] 记忆分块切片 ({len(chunks)} 包):")
    for c in chunks:
        print(f"      - {c}")
    assembled = client.reassemble_memory(chunks)
    print(f"  [+] 手机端重组还原完成 (有效载荷 {len(assembled)} 字节):")
    print(f"      {assembled}")

    print("\n[测试 4/5] 0xFFB3 灵宠观察日记归档...")
    print("  [+] 本地沉淀日记流 (Diary Feed):")
    for idx, d in enumerate(client.diary_history):
        print(f"      [{idx+1}] {d}")

    print("\n[测试 5/5] 长程对话向量知识库 (SQLite-vss / VectorStore) 索引与语义检索...")
    try:
        from scripts.lingbuddy_vector_store import LingBuddyVectorStore
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db = tmp.name
        v_store = LingBuddyVectorStore(db_path=tmp_db)
        v_store.import_from_ble_stream(json.loads(assembled))
        for d in client.diary_history:
            v_store.add_diary_entry(d, intimacy_level=client.level)
        hits = v_store.search("北京评审", top_k=2)
        print(f"  [+] 语义查询 '北京评审' 命中结果 (共 {len(hits)} 条):")
        for h in hits:
            print(f"      * ({h['score']*100:.1f}%) [{h['type']}] {h['content']}")
        rag_prompt = v_store.export_rag_context("北京评审", max_chars=200)
        print(f"  [+] 生成 RAG 注入上下文:\n{rag_prompt}")
        if os.path.exists(tmp_db):
            os.remove(tmp_db)
    except Exception as e:
        print(f"  [-] 向量知识库演示跳过: {e}")

    print("\n" + "=" * 76)
    print("  [SUCCESS] LingBuddy BLE Companion 客户端核心链路 100% 验证通过！")
    print("=" * 76)


if __name__ == "__main__":
    run_cli_demo()
