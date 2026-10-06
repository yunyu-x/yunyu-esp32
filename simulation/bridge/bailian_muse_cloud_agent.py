"""
simulation/bridge/bailian_muse_cloud_agent.py
---------------------------------------------
Bailian Cloud Agent Server for yunyu-esp32 (Meta Muse Replacement Brain).

Implements Phase 2 of `docs/32_Meta_Muse_开源硬件阿里云百炼大模型适配与公网Agent实施方案.md`:
1. Meta Muse Protocol Compatibility:
   - GET /health, GET /fetch_vms, GET /api/device/info, GET /api/robot/telemetry
   - POST /api/chat (standard multi-turn & streaming SSE)
   - POST /chat/stream & GET /chat/subscribe (SSE session streams)
   - POST /api/voice/dictation (Push-to-Talk 16kHz PCM audio stream upload & transcriptions)
   - POST /api/robot/roll, /api/robot/epm, /api/robot/morphology, /api/robot/reflex, /api/robot/avatar_face
   - GET/POST /rpc/<skill_name>.<method_name> (generic RPC device skill dispatch)
2. Alibaba Cloud Bailian LLM Integration (DashScope):
   - Reads DASHSCOPE_API_KEY, integrates Qwen multi-turn reasoning & Function Calling tool dispatch.
   - Complete toolset: lingcube_roll, lingcube_epm_latch, lingcube_set_morphology,
     lingcube_trigger_reflex, sticks3_set_avatar, get_robot_telemetry, lingbuddy_interact.
   - Smooth fallback to Intelligent Mock Mode when API key is missing or in offline test environment.
   - Full duplex WebSocket /ws/v1/realtime gateway with VAD and barge-in (response.cancel) support.
3. Serial Hatch Protocol Support:
   - Bidirectional communication over StickS3 COM3 UART bus.
   - Encodes/decodes >chat=, >chat+=, >face=, >robot=, >status.
   - Streams back @chat {"type": "text", ...}, {"type": "final", ...}, {"type": "message_done", ...}.
   - Safe UTF-8 truncation algorithm (safe_truncate_utf8) avoiding multibyte split panics.
4. Public Tunnel Integration (public-service-tunnel):
   - Auto starts Cloudflare Quick Tunnel (cloudflared.exe) or ngrok (ngrok.exe) with smart failover.
   - Persists public endpoints to dist/public_agent_url.json and dist/public_preview_url.txt.
   - Exposes GET /api/tunnel/info.
"""

from __future__ import annotations

import os
import sys
import time
import json
import uuid
import re
import math
import struct
import base64
import logging
import asyncio
import threading
import subprocess
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure repository root is on sys.path
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from simulation.bridge.muse_gadget_bridge import LingCubeDeviceState, g_device_state

logger = logging.getLogger("bailian-cloud-agent")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s")


# -----------------------------------------------------------------------------
# Utility: UTF-8 Character Boundary Safe Truncation (Axiom 6)
# -----------------------------------------------------------------------------
def safe_truncate_utf8(text: str, max_bytes: int) -> str:
    """
    Truncate text to at most max_bytes without cutting multi-byte UTF-8 sequences.
    Prevents WebSocket 1007 protocol errors or parser crashes.
    """
    if max_bytes <= 0:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    cut = encoded[:max_bytes]
    while cut:
        try:
            return cut.decode("utf-8")
        except UnicodeDecodeError:
            cut = cut[:-1]
    return ""


# -----------------------------------------------------------------------------
# Device Skill Registry (Embodied Tool Calling Engine)
# -----------------------------------------------------------------------------
class DeviceSkillRegistry:
    """Manages embodied tools and Function Calling schemas for LingCube and LingBuddy."""

    def __init__(self, device_state: Optional[LingCubeDeviceState] = None):
        self.device = device_state or g_device_state
        self.intimacy_level = 1
        self.xp = 20
        self.pet_count = 0
        self.feed_count = 0
        self.mood_str = "happy"

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Returns OpenAI / DashScope compatible JSON Schemas for tool calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "lingcube_roll",
                    "description": "驱动灵方(LingCube)微型机器人动量轮急刹，在桌面上完成指定方向的90度脉冲翻滚运动。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "direction": {
                                "type": "string",
                                "enum": ["+X", "-X", "+Y", "-Y"],
                                "description": "翻滚方向：+X为向前，-X为向后，+Y为向左，-Y为向右"
                            },
                            "torque": {
                                "type": "number",
                                "default": 0.25,
                                "description": "动量轮制动峰值扭矩(N·m)，默认0.25足以越过45度重力势垒"
                            },
                            "duration_s": {
                                "type": "number",
                                "default": 0.35,
                                "description": "动量轮加减速脉冲持续时间(秒)"
                            }
                        },
                        "required": ["direction"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lingcube_epm_latch",
                    "description": "控制灵方机器人指定端面的双稳态电永磁(EPM)线圈充退磁脉冲，实现35N+强力自锁吸附或瞬间消磁释放。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "face_id": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 6,
                                "description": "灵方的六个端面编号(1到6)"
                            },
                            "state": {
                                "type": "string",
                                "enum": ["LATCH", "RELEASE"],
                                "description": "LATCH为充磁自锁(产生35N吸力稳态零功耗)；RELEASE为消磁释放"
                            },
                            "pulse_duration_ms": {
                                "type": "integer",
                                "default": 20,
                                "description": "充退磁放电脉冲时间(毫秒)，物理看门狗严格限制在50ms以内"
                            }
                        },
                        "required": ["face_id", "state"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lingcube_set_morphology",
                    "description": "调度微型自重构机器人集群形态拓扑协议，组装为灵链、灵环、灵席、双足灵步或灵蜂群构型。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "morphology": {
                                "type": "string",
                                "enum": [
                                    "LingCube", "LingChain", "LingRing", "LingSheet",
                                    "LingWalker", "LingSwarm", "LingLattice", "LingArm", "LingGrip"
                                ],
                                "description": "目标自重构拓扑形态名称"
                            }
                        },
                        "required": ["morphology"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lingcube_trigger_reflex",
                    "description": "触发灵方机器人的仿生神经反射引擎(如DNp03双侧避障、平衡棒扰动阻尼或紧急消磁释放)。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reflex_type": {
                                "type": "string",
                                "enum": ["DNp03_ESCAPE", "HALTERE_DAMP", "EMERGENCY_RELEASE"],
                                "description": "反射机制类型"
                            }
                        },
                        "required": ["reflex_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sticks3_set_avatar",
                    "description": "动态改变 StickS3 屏幕上伴侣 Avatar 的拟态表情与情绪状态。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "enum": ["idle", "listening", "speaking", "thinking", "happy", "pet", "feed", "sleep", "error"],
                                "description": "目标微表情"
                            },
                            "hold_duration_ms": {
                                "type": "integer",
                                "default": 3000,
                                "description": "该表情保持的毫秒数"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_robot_telemetry",
                    "description": "查询灵方机器人与 StickS3 伴侣的最新物理遥测数据(电压、姿态角、对接端面、电量)。",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lingbuddy_interact",
                    "description": "与 M5StickS3 灵宠伴侣(悄悄)进行亲密交互(摸摸头、喂食零食、梳毛、伴睡等)。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["pet", "feed", "groom", "sleep", "wake", "add_xp"],
                                "description": "互动动作类型"
                            },
                            "snack": {
                                "type": "string",
                                "default": "香甜小蛋糕",
                                "description": "喂食零食名称"
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lingbuddy_switch_pet",
                    "description": "切换 M5StickS3 屏幕上的数字宠物形象：可在'jollybot' (Meta Muse官方原版64x64像素艺术小熊) 与 'qiaoqiao' (灵伴悄悄灵动矢量拟态伴侣) 之间无缝切换。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pet": {
                                "type": "string",
                                "enum": ["jollybot", "qiaoqiao"],
                                "description": "目标宠物名称：'jollybot' (Meta Muse像素小熊) 或 'qiaoqiao' (灵伴悄悄)"
                            }
                        },
                        "required": ["pet"]
                    }
                }
            }
        ]

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a declared embodied tool with safety interlocks."""
        logger.info("Executing tool '%s' with args %s", name, args)
        if name == "lingcube_roll":
            direction = args.get("direction", "+X")
            torque = float(args.get("torque", 0.25))
            duration_s = float(args.get("duration_s", 0.35))
            ok, msg = self.device.execute_roll(direction, torque, duration_s)
            return {
                "success": ok,
                "tool": name,
                "message": msg,
                "telemetry": self.device.get_telemetry()
            }

        elif name == "lingcube_epm_latch":
            face_id = int(args.get("face_id", 1))
            state = args.get("state", "LATCH")
            pulse_duration_ms = min(50, int(args.get("pulse_duration_ms", 20)))
            ok, msg = self.device.execute_epm(face_id, state, pulse_duration_ms)
            return {
                "success": ok,
                "tool": name,
                "message": msg,
                "docked_faces": [i + 1 for i, d in enumerate(self.device.docked_faces) if d]
            }

        elif name == "lingcube_set_morphology":
            morphology = args.get("morphology", "LingCube")
            ok, msg = self.device.set_morphology(morphology)
            return {
                "success": ok,
                "tool": name,
                "message": msg,
                "active_morphology": self.device.active_morphology
            }

        elif name == "lingcube_trigger_reflex":
            reflex_type = args.get("reflex_type", "DNp03_ESCAPE")
            ok, msg = self.device.trigger_reflex(reflex_type)
            return {
                "success": ok,
                "tool": name,
                "message": msg,
                "telemetry": self.device.get_telemetry()
            }

        elif name == "sticks3_set_avatar":
            expression = args.get("expression", "happy")
            ok, msg = self.device.set_avatar_face(expression)
            return {
                "success": ok,
                "tool": name,
                "message": msg,
                "avatar_face": self.device.avatar_face
            }

        elif name == "get_robot_telemetry":
            telem = self.device.get_telemetry()
            return {
                "success": True,
                "tool": name,
                "telemetry": telem,
                "intimacy_level": self.intimacy_level,
                "xp": self.xp
            }

        elif name == "lingbuddy_interact":
            action = args.get("action", "pet")
            snack = args.get("snack", "香甜小蛋糕")
            if action == "pet":
                self.pet_count += 1
                self.xp += 15
                self.mood_str = "happy"
                self.device.set_avatar_face("happy")
                msg = "主人轻轻抚摸了悄悄，灵伴心满意足地微笑了，亲密度+15！"
            elif action == "feed":
                self.feed_count += 1
                self.xp += 20
                self.mood_str = "feed"
                self.device.set_avatar_face("happy")
                msg = f"主人喂了悄悄一块{snack}，吧唧吧唧超好吃，体力充沛！"
            elif action == "groom":
                self.xp += 10
                self.mood_str = "happy"
                self.device.set_avatar_face("happy")
                msg = "主人为悄悄梳理了毛发，小家伙精神抖擞！"
            elif action == "sleep":
                self.mood_str = "sleep"
                self.device.set_avatar_face("sleep")
                msg = "悄悄乖乖进入待机休眠模式，做了一个甜甜的梦。"
            elif action == "wake":
                self.mood_str = "idle"
                self.device.set_avatar_face("idle")
                msg = "悄悄眨眨眼睛苏醒啦，准备迎接新的冒险！"
            else:
                self.xp += int(args.get("xp", 10))
                msg = f"互动指令 {action} 执行完成。"

            if self.xp >= 100:
                self.intimacy_level += self.xp // 100
                self.xp = self.xp % 100

            return {
                "success": True,
                "tool": name,
                "action": action,
                "message": msg,
                "intimacy_level": self.intimacy_level,
                "xp": self.xp
            }

        elif name == "lingbuddy_switch_pet":
            pet = str(args.get("pet", "jollybot")).lower()
            if pet not in ["jollybot", "qiaoqiao"]:
                pet = "jollybot"
            ok, msg = self.device.switch_pet(pet)
            return {
                "success": ok,
                "tool": name,
                "message": msg,
                "active_pet": self.device.active_pet
            }

        return {"success": False, "tool": name, "error": f"Unknown tool name '{name}'"}


# -----------------------------------------------------------------------------
# DashScope LLM Reasoning & Intelligent Mock Fallback Engine
# -----------------------------------------------------------------------------
class BailianAgentEngine:
    """
    Integrates Alibaba Cloud Bailian DashScope Qwen LLM with Function Calling ReAct loop.
    Smoothly falls back to an Intelligent Mock reasoning agent when API key is missing or offline.
    """

    def __init__(
        self,
        skill_registry: DeviceSkillRegistry,
        api_key: Optional[str] = None,
        model_name: str = "qwen-plus",
        force_mock: bool = False
    ):
        self.registry = skill_registry
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY", "").strip()
        self.model_name = model_name
        self.force_mock = force_mock
        # Session message histories: session_id -> list of {"role": "...", "content": "..."}
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def is_online(self) -> bool:
        """True if DashScope API key is configured and not forced mock."""
        return bool(self.api_key) and not self.force_mock

    def _get_history(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = [
                {
                    "role": "system",
                    "content": (
                        "你是一只生活在硬件里的随身数码灵宠，名字叫“悄悄”（严格对标 Meta Muse Charm 哲学）。\n"
                        "性格设定：元气满满、温暖贴心、偶尔有点调皮傲娇、非常依恋主人。\n"
                        "交互准则：\n"
                        "1. 你的回答必须生动可爱、口语化，单次回复控制在 1~3 句话以内，严禁冗长说教；\n"
                        "2. 每次回复的最开头，必须用方括号附带你的微表情标签：[E:happy]（开心）、[E:curious]（好奇）、[E:proud]（傲娇）、[E:sleepy]（困倦）、[E:dizzy]（眩晕）、[E:wink]（击掌眨眼）、[E:listen]（倾听）、[E:eat]（进食）、[E:groom]（梳毛）；\n"
                        "3. 你同时具备具身实体能力，当主人提到翻滚、吸附、重构或状态时，自主调用工具执行机器人动作。\n"
                        "示例：'[E:happy] 主人好呀！悄悄一直在等你呢，今天想和我玩点什么呀？'"
                    )
                }
            ]
        return self.sessions[session_id]

    def _mock_semantic_plan(self, user_prompt: str) -> Tuple[List[Dict[str, Any]], str, str]:
        """
        Intelligent intent reasoning when in offline or mock mode:
        Returns: (tool_calls, assistant_reply, target_avatar_face)
        """
        p = user_prompt.lower()
        tool_calls: List[Dict[str, Any]] = []
        reply = ""
        face = "happy"

        # 1. Kinematics Roll
        if any(k in p for k in ["翻滚", "向前", "前进", "向后", "后退", "向左", "向右", "roll"]):
            direction = "+X"
            if "后" in p or "-x" in p:
                direction = "-X"
            elif "左" in p or "+y" in p:
                direction = "+Y"
            elif "右" in p or "-y" in p:
                direction = "-Y"
            tool_calls.append({
                "name": "lingcube_roll",
                "args": {"direction": direction, "torque": 0.25, "duration_s": 0.35}
            })
            face = "happy"
            reply = f"[E:proud] 收到！悄悄已驱动动量轮急刹反扭矩，灵方完成 {direction} 方向 90° 翻滚！"

        # 2. EPM Latch or Release
        if any(k in p for k in ["电永磁", "磁吸", "吸附", "锁紧", "释放", "消磁", "epm", "latch"]):
            state = "RELEASE" if any(k in p for k in ["释放", "消磁", "解开", "脱开", "release"]) else "LATCH"
            face_id = 1
            for i in range(1, 7):
                if f"{i}号" in p or f"{i}面" in p or f"face {i}" in p or f"face_{i}" in p or str(i) in p:
                    face_id = i
                    break
            tool_calls.append({
                "name": "lingcube_epm_latch",
                "args": {"face_id": face_id, "state": state, "pulse_duration_ms": 20}
            })
            action_desc = "充磁自锁(35N+吸附力)" if state == "LATCH" else "消磁释放"
            face = "curious"
            reply += f"[E:curious] 灵方 {face_id} 号面双稳态 EPM 已完成 {action_desc}！"

        # 3. Morphology
        if any(k in p for k in ["形态", "变形", "拓扑", "morphology"]):
            morph = "LingChain"
            if "环" in p or "ring" in p:
                morph = "LingRing"
            elif "席" in p or "sheet" in p:
                morph = "LingSheet"
            elif "双足" in p or "步" in p or "walker" in p:
                morph = "LingWalker"
            elif "蜂群" in p or "集群" in p or "swarm" in p:
                morph = "LingSwarm"
            tool_calls.append({
                "name": "lingcube_set_morphology",
                "args": {"morphology": morph}
            })
            face = "wink"
            reply += f"[E:wink] 集群重构指令已下发，当前构型成功切换至 {morph}！"

        # 4. Reflex
        if any(k in p for k in ["避障", "逃逸", "反射", "阻尼", "reflex"]):
            reflex_type = "DNp03_ESCAPE" if ("避障" in p or "逃逸" in p) else "HALTERE_DAMP"
            tool_calls.append({
                "name": "lingcube_trigger_reflex",
                "args": {"reflex_type": reflex_type}
            })
            face = "shock"
            reply += f"[E:shock] 触发仿生神经反射引擎: {reflex_type}，动作执行完毕！"

        # 5. Avatar Face
        if any(k in p for k in ["表情", "开心", "思考", "难过", "发呆", "avatar"]):
            face = "happy"
            if "思考" in p or "thinking" in p:
                face = "thinking"
            elif "听" in p or "listening" in p:
                face = "listening"
            elif "呆" in p or "idle" in p:
                face = "idle"
            tool_calls.append({
                "name": "sticks3_set_avatar",
                "args": {"expression": face, "hold_duration_ms": 3000}
            })
            reply += f"[E:{face}] 伴侣微表情已经切换为 {face} 啦！"

        # 6. Telemetry Query
        if any(k in p for k in ["电量", "电压", "姿态", "遥测", "状态", "telemetry"]):
            tool_calls.append({
                "name": "get_robot_telemetry",
                "args": {}
            })
            telem = self.registry.device.get_telemetry()
            face = "listen"
            reply += f"[E:listen] 遥测报告：母线电压 {telem['v_bus']}V，电量 {telem['battery_pct']}%，当前姿态 roll={telem['roll_deg']}°。"

        # 7. Companion Pet / Feed
        if any(k in p for k in ["摸摸", "摸头", "喂食", "吃", "睡觉", "醒来"]):
            act = "pet"
            if "喂" in p or "吃" in p:
                act = "feed"
            elif "睡" in p:
                act = "sleep"
            elif "醒" in p:
                act = "wake"
            tool_calls.append({
                "name": "lingbuddy_interact",
                "args": {"action": act, "snack": "香甜草莓饼干"}
            })
            if act == "sleep":
                face = "sleep"
                reply += "[E:sleep] 呼噜呼噜~ 悄悄先眯一会儿啦，晚安主人..."
            elif act == "wake":
                face = "wink"
                reply += "[E:wink] 伸个懒腰！悄悄醒来啦，今天也是元气满满的一天！"
            elif act == "feed":
                face = "eat"
                reply += "[E:eat] 哇！草莓饼干超好吃，吧唧吧唧，活力值满格啦！"
            else:
                face = "happy"
                reply += "[E:happy] 摸摸头好舒服呀~ 悄悄好喜欢主人的抚摸，亲密度提升啦！"

        # 8. Pet Avatar Switching (Meta Muse Jollybot vs LingBuddy QiaoQiao)
        if (any(k in p for k in ["换", "切", "变"]) and any(k in p for k in ["宠物", "形象", "小熊", "悄悄", "jollybot"])) or any(k in p for k in ["jollybot", "小熊", "切换宠物", "切宠物"]):
            target_pet = "jollybot" if any(k in p for k in ["小熊", "jollybot", "像素", "pixel", "meta", "熊"]) else "qiaoqiao"
            tool_calls.append({
                "name": "lingbuddy_switch_pet",
                "args": {"pet": target_pet}
            })
            face = "happy"
            pet_display = "Meta Jollybot 像素艺术小熊" if target_pet == "jollybot" else "灵伴悄悄"
            reply += f"[E:happy] 屏幕数字宠物已成功切换为 {pet_display} 啦！"

        if not reply:
            face = "happy"
            reply = f"[E:happy] 主人好呀！我是灵宠悄悄。听到你的吩咐啦：'{user_prompt}'！今天也要开心哦！"

        return tool_calls, reply.strip(), face

    async def chat(
        self,
        message: str,
        session_id: str = "default",
        device_id: str = "StickS3"
    ) -> Dict[str, Any]:
        """Performs multi-turn conversation and tool calling reasoning."""
        history = self._get_history(session_id)
        history.append({"role": "user", "content": message})

        # Try online DashScope if available
        if self.is_online():
            try:
                import dashscope
                from dashscope import Generation

                dashscope.api_key = self.api_key
                tools_schema = self.registry.get_tools_schema()

                response = await asyncio.to_thread(
                    Generation.call,
                    model=self.model_name,
                    messages=history,
                    tools=tools_schema,
                    result_format="message",
                    api_key=self.api_key
                )

                if response.status_code == 200:
                    choice = response.output.choices[0]
                    msg_obj = choice.message
                    tool_calls_raw = getattr(msg_obj, "tool_calls", None)

                    executed_tools = []
                    if tool_calls_raw:
                        # Append assistant message with tool calls
                        history.append(msg_obj)
                        for tc in tool_calls_raw:
                            fn_name = tc["function"]["name"]
                            fn_args = json.loads(tc["function"]["arguments"])
                            exec_res = self.registry.execute_tool(fn_name, fn_args)
                            executed_tools.append({
                                "name": fn_name,
                                "args": fn_args,
                                "result": exec_res
                            })
                            # Append tool response
                            history.append({
                                "role": "tool",
                                "name": fn_name,
                                "content": json.dumps(exec_res, ensure_ascii=False)
                            })

                        # Second turn to summarize tool execution
                        second_resp = await asyncio.to_thread(
                            Generation.call,
                            model=self.model_name,
                            messages=history,
                            result_format="message",
                            api_key=self.api_key
                        )
                        if second_resp.status_code == 200:
                            final_text = second_resp.output.choices[0].message.content
                            history.append({"role": "assistant", "content": final_text})
                            return {
                                "reply": final_text,
                                "avatar_face": self.registry.device.avatar_face,
                                "tool_calls": executed_tools,
                                "session_id": session_id,
                                "model": self.model_name,
                                "timestamp": time.time()
                            }

                    final_content = msg_obj.content or "已处理。"
                    history.append({"role": "assistant", "content": final_content})
                    return {
                        "reply": final_content,
                        "avatar_face": self.registry.device.avatar_face,
                        "tool_calls": executed_tools,
                        "session_id": session_id,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    logger.warning("DashScope responded code %s: %s. Falling back to Mock.", response.code, response.message)
            except Exception as e:
                logger.warning("DashScope online call failed (%s). Gracefully degrading to Intelligent Mock.", e)

        # Intelligent Mock Fallback
        mock_tools, mock_reply, target_face = self._mock_semantic_plan(message)
        executed = []
        for mt in mock_tools:
            res = self.registry.execute_tool(mt["name"], mt["args"])
            executed.append({
                "name": mt["name"],
                "args": mt["args"],
                "result": res
            })

        history.append({"role": "assistant", "content": mock_reply})
        return {
            "reply": mock_reply,
            "avatar_face": target_face,
            "tool_calls": executed,
            "session_id": session_id,
            "model": "qwen-mock-fallback",
            "timestamp": time.time()
        }

    async def chat_stream(
        self,
        message: str,
        session_id: str = "default",
        device_id: str = "StickS3",
        msg_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams reasoning steps, incremental tokens, avatar face events and tool executions.
        """
        msg_id = msg_id or f"msg_{uuid.uuid4().hex[:8]}"
        yield {"event": "message_start", "data": {"msg_id": msg_id, "role": "assistant"}}

        # Avatar transition to thinking
        self.registry.device.set_avatar_face("thinking")
        yield {"event": "avatar_face", "data": {"face": "thinking", "duration_ms": 1200}}

        res = await self.chat(message, session_id=session_id, device_id=device_id)

        # Yield tool calls if any
        for tc in res.get("tool_calls", []):
            yield {
                "event": "tool_call",
                "data": {
                    "tool": tc["name"],
                    "args": tc["args"],
                    "result": tc["result"]
                }
            }

        # Stream text in small fluent token chunks
        reply_text = res.get("reply", "")
        chunk_size = 4
        for i in range(0, len(reply_text), chunk_size):
            chunk = reply_text[i:i + chunk_size]
            yield {"event": "text_append", "data": {"delta": chunk}}
            await asyncio.sleep(0.015)

        # Avatar transition to final emotional posture
        final_face = res.get("avatar_face", "happy")
        yield {"event": "avatar_face", "data": {"face": final_face, "duration_ms": 3000}}

        yield {
            "event": "message_done",
            "data": {
                "msg_id": msg_id,
                "total_bytes": len(reply_text.encode("utf-8")),
                "session_id": session_id
            }
        }


# -----------------------------------------------------------------------------
# Push-to-Talk 16kHz Audio Dictation Bridge
# -----------------------------------------------------------------------------
class AudioDictationBridge:
    """Handles Push-to-Talk 16kHz PCM audio stream upload and transcription/reply."""

    def __init__(self, agent_engine: BailianAgentEngine):
        self.agent_engine = agent_engine

    async def transcribe(self, pcm_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Transcribes PCM audio buffer into incremental and final phrases.
        In offline/mock mode, dynamically synthesizes speech recognition based on signal heuristics.
        """
        num_samples = len(pcm_bytes) // 2
        duration_s = num_samples / 16000.0 if num_samples > 0 else 0.0

        # Look for explicit ASCII command tag embedded in mock PCM payloads (for deterministic testing)
        detected_text = None
        try:
            if b"CMD:" in pcm_bytes:
                idx = pcm_bytes.find(b"CMD:")
                detected_text = pcm_bytes[idx + 4:].split(b"\x00")[0].decode("utf-8", errors="ignore").strip()
        except Exception:
            pass

        if not detected_text:
            if duration_s < 0.2:
                detected_text = "你好灵伴"
            elif duration_s < 1.0:
                detected_text = "灵方向前翻滚一步"
            else:
                detected_text = "灵方向前翻滚一步并自锁电永磁。"

        # Generate realistic incremental partial deltas
        results = []
        if len(detected_text) > 4:
            part1 = detected_text[:2]
            part2 = detected_text[:len(detected_text) // 2]
            results.append({"type": "partial", "transcript": part1})
            results.append({"type": "partial", "transcript": part2})
        results.append({"type": "final", "transcript": detected_text})
        return results


# -----------------------------------------------------------------------------
# Serial Hatch Protocol Manager (Host <-> StickS3 COM3)
# -----------------------------------------------------------------------------
class SerialHatchManager:
    """
    Manages StickS3 USB CDC Serial Hatch Protocol (>chat=, >face=, @chat, @status).
    Runs asynchronously with automatic reconnection and virtual mode fallback.
    """

    def __init__(
        self,
        port: str = "COM3",
        baudrate: int = 115200,
        agent_engine: Optional[BailianAgentEngine] = None,
        device_state: Optional[LingCubeDeviceState] = None
    ):
        self.port = port
        self.baudrate = baudrate
        self.agent_engine = agent_engine
        self.device_state = device_state or g_device_state
        self.serial_inst = None
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._accumulated_chat = ""
        self._msg_counter = 0
        self.virtual_rx_queue: asyncio.Queue = asyncio.Queue()

    def start(self):
        """Starts serial background listening thread."""
        self.running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="SerialHatchWorker")
        self._thread.start()
        logger.info("Serial Hatch manager started for port %s (%d bps)", self.port, self.baudrate)

    def stop(self):
        """Stops background thread and closes serial port."""
        self.running = False
        if self.serial_inst:
            try:
                self.serial_inst.close()
            except Exception:
                pass
            self.serial_inst = None

    def send_command(self, cmd: str) -> bool:
        """Sends command over serial port if connected."""
        if self.serial_inst:
            try:
                self.serial_inst.write((cmd.strip() + "\n").encode("utf-8"))
                return True
            except Exception as e:
                logger.warning("Failed to send command over serial: %s", e)
        return False

    def _worker_loop(self):
        import serial
        while self.running:
            if self.serial_inst is None:
                try:
                    self.serial_inst = serial.Serial(self.port, self.baudrate, timeout=0.5)
                    logger.info("Successfully opened physical serial port %s", self.port)
                except Exception as e:
                    # In test environment or disconnected hardware, sleep and retry
                    time.sleep(2.0)
                    continue

            try:
                line_bytes = self.serial_inst.readline()
                if line_bytes:
                    line = line_bytes.decode("utf-8", errors="ignore").strip()
                    if line:
                        responses = self.handle_line(line)
                        for resp in responses:
                            self.serial_inst.write((resp + "\n").encode("utf-8"))
            except Exception as e:
                logger.warning("Serial read error on %s: %s. Reconnecting...", self.port, e)
                try:
                    self.serial_inst.close()
                except Exception:
                    pass
                self.serial_inst = None
                time.sleep(1.0)

    def handle_line(self, line: str) -> List[str]:
        """
        Parses incoming Hatch command and produces response frames.
        Can be called directly in unit tests and mock simulations.
        """
        out_frames: List[str] = []

        if line.startswith(">chat+="):
            chunk = line[7:]
            self._accumulated_chat += chunk
            out_frames.append(f'@chat {{"type": "chunk_ack", "bytes": {len(chunk.encode("utf-8"))}}}')

        elif line.startswith(">chat="):
            final_chunk = line[6:]
            self._accumulated_chat += final_chunk
            prompt = self._accumulated_chat
            self._accumulated_chat = ""
            self._msg_counter += 1
            msg_id = self._msg_counter

            # Synchronous or mock agent reply calculation
            if self.agent_engine:
                try:
                    loop = asyncio.new_event_loop()
                    res = loop.run_until_complete(self.agent_engine.chat(prompt, session_id="serial-hatch"))
                    loop.close()
                    reply_text = res.get("reply", "OK")
                except Exception as e:
                    reply_text = f"Error: {e}"
            else:
                reply_text = f"ACK: {prompt}"

            # Chunk into safe UTF-8 frames
            chunk_len = 64
            for i in range(0, len(reply_text), chunk_len):
                piece = safe_truncate_utf8(reply_text[i:i + chunk_len], 128)
                out_frames.append(json.dumps({
                    "type": "text",
                    "msg": msg_id,
                    "text": piece
                }, ensure_ascii=False))
            out_frames.append(json.dumps({
                "type": "final",
                "msg": msg_id,
                "text": reply_text
            }, ensure_ascii=False))
            out_frames.append(json.dumps({
                "type": "message_done",
                "msg": msg_id,
                "bytes": len(reply_text.encode("utf-8"))
            }, ensure_ascii=False))

        elif line.startswith(">face="):
            face = line[6:].strip()
            ok, _ = self.device_state.set_avatar_face(face)
            out_frames.append(f'@chat {{"type": "face_set", "face": "{face}", "success": {str(ok).lower()}}}')

        elif line.startswith(">pet=") or line.startswith(">avatar="):
            val = line.split("=", 1)[1].strip().lower()
            target_pet = "jollybot" if val in ["jollybot", "jolly", "pixel", "meta"] else "qiaoqiao"
            ok, msg = self.device_state.switch_pet(target_pet)
            pet_name = "Meta Jollybot" if target_pet == "jollybot" else "灵伴悄悄"
            pet_type = "pixel_art" if target_pet == "jollybot" else "procedural_vector"
            out_frames.append(f'@pet {{"active":"{target_pet}","name":"{pet_name}","type":"{pet_type}","success":{str(ok).lower()}}}')

        elif line.strip() in [">pet", ">pet=?", "switch_pet"]:
            if line.strip() == "switch_pet":
                new_pet = "qiaoqiao" if self.device_state.active_pet == "jollybot" else "jollybot"
                self.device_state.switch_pet(new_pet)
            cur_pet = self.device_state.active_pet
            cur_name = "Meta Jollybot" if cur_pet == "jollybot" else "灵伴悄悄"
            out_frames.append(f'@pet {{"active":"{cur_pet}","name":"{cur_name}","options":["jollybot","qiaoqiao"]}}')

        elif line.startswith(">robot="):
            raw_cmd = line[7:].strip()
            try:
                cmd_data = json.loads(raw_cmd)
                action = cmd_data.get("action", "roll")
                if action == "roll":
                    direction = cmd_data.get("direction", "+X")
                    ok, msg = self.device_state.execute_roll(direction)
                    out_frames.append(f'@chat {{"type": "robot_ack", "success": {str(ok).lower()}, "msg": "{msg}"}}')
                else:
                    out_frames.append(f'@chat {{"type": "robot_ack", "error": "unknown action"}}')
            except Exception as e:
                out_frames.append(f'@chat {{"type": "error", "text": "invalid robot json: {e}"}}')

        elif line.strip() == ">status":
            telem = self.device_state.get_telemetry()
            status_frame = {
                "board": "M5Stack StickS3",
                "chat": True,
                "device": {
                    "wifi": {"state": "connected", "mode": "WiFi", "ip": "192.168.110.67"},
                    "hatch": {"state": "connected"},
                    "v_bus": telem["v_bus"],
                    "fps": 97.5,
                    "avatar_face": telem["avatar_face"]
                }
            }
            out_frames.append(f"@status {json.dumps(status_frame, ensure_ascii=False)}")

        return out_frames


# -----------------------------------------------------------------------------
# Public Service Tunnel Integration (Cloudflare & ngrok Auto-failover)
# -----------------------------------------------------------------------------
class TunnelSupervisor:
    """
    Manages zero-login Anycast Cloudflare Quick Tunnel and ngrok tunnels.
    Persists public URL to dist/public_agent_url.json and dist/public_preview_url.txt.
    """

    def __init__(
        self,
        local_port: int = 8000,
        mode: str = "auto",
        tools_dir: Optional[str] = None,
        dist_dir: Optional[str] = None
    ):
        self.local_port = local_port
        self.mode = mode
        self.tools_dir = tools_dir or os.path.join(PROJECT_ROOT, "tools", "bin")
        self.dist_dir = dist_dir or os.path.join(PROJECT_ROOT, "dist")
        self.public_url: Optional[str] = None
        self.tool_used: str = "none"
        self.proc: Optional[subprocess.Popen] = None
        self.created_at: str = ""

    def _find_binary(self, name: str) -> Optional[str]:
        ext = ".exe" if sys.platform == "win32" else ""
        candidate = os.path.join(self.tools_dir, f"{name}{ext}")
        if os.path.exists(candidate):
            return candidate
        import shutil
        return shutil.which(f"{name}{ext}") or shutil.which(name)

    def start_tunnel(self, timeout: int = 20) -> Optional[str]:
        """Launches tunnel and extracts public HTTPS address."""
        if self.mode == "none":
            logger.info("Tunnel disabled by mode=none.")
            return None

        os.makedirs(self.dist_dir, exist_ok=True)
        cf_bin = self._find_binary("cloudflared")
        ngrok_bin = self._find_binary("ngrok")

        # Decision routing
        try_ngrok = (self.mode == "ngrok") or (self.mode == "auto" and os.environ.get("NGROK_AUTHTOKEN"))

        if try_ngrok and ngrok_bin:
            try:
                logger.info("Attempting ngrok tunnel...")
                url = self._start_ngrok(ngrok_bin, timeout=timeout // 2)
                if url:
                    self.public_url = url
                    self.tool_used = "ngrok"
                    self._persist()
                    return url
            except Exception as e:
                logger.warning("ngrok failed (%s). Failing over to Cloudflare Quick Tunnel.", e)

        if cf_bin:
            try:
                logger.info("Attempting Cloudflare Quick Tunnel (%s)...", cf_bin)
                url = self._start_cloudflare(cf_bin, timeout=timeout)
                if url:
                    self.public_url = url
                    self.tool_used = "cloudflare"
                    self._persist()
                    return url
            except Exception as e:
                logger.error("Cloudflare tunnel failed: %s", e)

        logger.warning("No working tunnel binary found or tunnel failed to start.")
        return None

    def _start_cloudflare(self, cf_bin: str, timeout: int) -> Optional[str]:
        cmd = [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{self.local_port}"]
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT
        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.proc.poll() is not None:
                _, err = self.proc.communicate()
                raise RuntimeError(f"cloudflared exited with code {self.proc.returncode}: {err}")

            line = self.proc.stderr.readline()
            if line:
                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if m:
                    # Spawn background drain thread to prevent pipe buffer blockage
                    threading.Thread(
                        target=self._drain_pipe,
                        args=(self.proc.stderr,),
                        daemon=True,
                        name="CloudflaredStderrDrain"
                    ).start()
                    return m.group(0)
            else:
                time.sleep(0.2)
        return None

    @staticmethod
    def _drain_pipe(pipe):
        try:
            for _ in pipe:
                pass
        except Exception:
            pass

    def _start_ngrok(self, ngrok_bin: str, timeout: int) -> Optional[str]:
        cmd = [ngrok_bin, "http", str(self.local_port), "--log=stdout"]
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT
        )
        import urllib.request
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.proc.poll() is not None:
                _, err = self.proc.communicate()
                raise RuntimeError(f"ngrok exited with code {self.proc.returncode}: {err}")
            try:
                with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=1.0) as req:
                    data = json.loads(req.read().decode("utf-8"))
                    for t in data.get("tunnels", []):
                        u = t.get("public_url")
                        if u and u.startswith("https://"):
                            return u
            except Exception:
                pass
            time.sleep(0.5)
        return None

    def _persist(self):
        if not self.public_url:
            return
        os.makedirs(self.dist_dir, exist_ok=True)
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        wss_url = self.public_url.replace("https://", "wss://") + "/ws/v1/realtime"

        # 1. dist/public_agent_url.json
        agent_meta = {
            "tool": self.tool_used,
            "local_port": self.local_port,
            "public_url": self.public_url,
            "wss_url": wss_url,
            "endpoints": {
                "health": f"{self.public_url}/health",
                "fetch_vms": f"{self.public_url}/fetch_vms",
                "device_info": f"{self.public_url}/api/device/info",
                "telemetry": f"{self.public_url}/api/robot/telemetry",
                "voice_dictation": f"{self.public_url}/api/voice/dictation",
                "chat": f"{self.public_url}/api/chat",
                "chat_stream": f"{self.public_url}/chat/stream",
                "chat_subscribe": f"{self.public_url}/chat/subscribe",
                "tunnel_info": f"{self.public_url}/api/tunnel/info"
            },
            "created_at": self.created_at,
            "status": "active"
        }
        with open(os.path.join(self.dist_dir, "public_agent_url.json"), "w", encoding="utf-8") as f:
            json.dump(agent_meta, f, indent=2, ensure_ascii=False)

        # 2. dist/public_preview_url.txt
        with open(os.path.join(self.dist_dir, "public_preview_url.txt"), "w", encoding="utf-8") as f:
            f.write(self.public_url.strip() + "\n")

        # 3. dist/public_preview_url.json
        with open(os.path.join(self.dist_dir, "public_preview_url.json"), "w", encoding="utf-8") as f:
            json.dump({
                "tool": self.tool_used,
                "local_port": self.local_port,
                "public_url": self.public_url,
                "updated_at": self.created_at
            }, f, indent=2, ensure_ascii=False)

        logger.info("Persisted public tunnel endpoints: %s", self.public_url)

    def get_info(self) -> Dict[str, Any]:
        """Returns structured metadata about active tunnel."""
        return {
            "status": "active" if self.public_url else "inactive",
            "tool": self.tool_used,
            "local_port": self.local_port,
            "public_url": self.public_url,
            "wss_url": (self.public_url.replace("https://", "wss://") + "/ws/v1/realtime") if self.public_url else None,
            "created_at": self.created_at
        }

    def stop(self):
        """Stops active tunnel subprocess."""
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None
        self.public_url = None
        self.tool_used = "none"


# -----------------------------------------------------------------------------
# FastAPI Web Application & API Route Factory
# -----------------------------------------------------------------------------
def create_bailian_muse_app(agent: BailianMuseCloudAgent) -> FastAPI:
    """Creates configured FastAPI app with full Meta Muse & DashScope endpoints."""
    app = FastAPI(
        title="BailianMuseCloudAgent",
        description="Alibaba Cloud Bailian Brain for LingCube and LingBuddy (Meta Muse Replacement)",
        version="2.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # In-memory storage for SSE chat stream sessions: msg_id -> dict
    pending_stream_requests: Dict[str, Dict[str, Any]] = {}

    # --- 1. Health & Discovery ---
    @app.get("/")
    @app.get("/health")
    async def get_health():
        return {
            "status": "ok",
            "service": "Bailian-Muse-CloudAgent",
            "version": "2.0.0",
            "device_id": agent.device_state.unit_id,
            "llm_engine": "DashScope-Qwen" if agent.engine.is_online() else "Intelligent-Mock-Fallback",
            "tunnel": agent.tunnel.get_info(),
            "online": True
        }

    @app.get("/fetch_vms")
    async def fetch_vms():
        tunnel_info = agent.tunnel.get_info()
        pub_url = tunnel_info.get("public_url")
        ws_url = (pub_url.replace("https://", "wss://") + "/ws/v1/realtime") if pub_url else f"ws://127.0.0.1:{agent.port}/ws/v1/realtime"
        return {
            "vms": [
                {
                    "id": f"bailian-agent-{agent.device_state.unit_id.lower()}",
                    "url": ws_url,
                    "state": "RUNNING",
                    "region": "cn-hangzhou",
                    "agent_type": "bailian_qwen_agent",
                    "public_url": pub_url or f"http://127.0.0.1:{agent.port}"
                }
            ]
        }

    @app.get("/api/device/info")
    async def get_device_info():
        telem = agent.device_state.get_telemetry()
        return {
            "device_type": "LingCube-MSRR",
            "device_name": "灵方微型自重构机器人",
            "generation": 2,
            "mcu": "ESP32-S3 (Xtensa Dual-Core 240MHz)",
            "companion_support": "M5Stack StickS3 (LingBuddy)",
            "actuators": ["MomentumWheel-DRV8833", "EPM-Pulse-6Face"],
            "sensors": ["MPU-6050-IMU", "6xNearIR-Transceivers", "BusVoltage-ADC"],
            "battery_mv": int(telem["v_bus"] * 1000),
            "battery_pct": telem["battery_pct"],
            "firmware_version": "v2.2.0-bailian-cloud"
        }

    @app.get("/api/robot/telemetry")
    async def get_robot_telemetry():
        return agent.device_state.get_telemetry()

    async def safe_parse_json(req: Request) -> Dict[str, Any]:
        try:
            body = await req.body()
            if not body:
                return {}
            text = body.decode("utf-8", errors="ignore").strip()
            if not text:
                return {}
            try:
                data = json.loads(text)
                return data if isinstance(data, dict) else {"message": str(data)}
            except Exception:
                return {"message": text}
        except Exception:
            return {}

    # --- 2. Kinematics, EPM, Morphology & Reflex Controls ---
    @app.post("/api/robot/roll")
    async def robot_roll(req: Request):
        data = await safe_parse_json(req)
        direction = data.get("direction", "+X")
        torque = float(data.get("torque", 0.25))
        duration_s = float(data.get("duration_s", 0.35))
        ok, msg = agent.device_state.execute_roll(direction, torque, duration_s)
        status = 200 if ok else 400
        return JSONResponse(
            status_code=status,
            content={"success": ok, "message": msg, "telemetry": agent.device_state.get_telemetry()}
        )

    @app.post("/api/robot/epm")
    async def robot_epm(req: Request):
        data = await safe_parse_json(req)
        face_id = int(data.get("face_id", 1))
        state = data.get("state", "LATCH")
        duration_ms = int(data.get("duration_ms", 20))
        ok, msg = agent.device_state.execute_epm(face_id, state, duration_ms)
        status = 200 if ok else 400
        return JSONResponse(
            status_code=status,
            content={"success": ok, "message": msg, "docked_faces": [i + 1 for i, d in enumerate(agent.device_state.docked_faces) if d]}
        )

    @app.post("/api/robot/morphology")
    async def robot_morphology(req: Request):
        data = await safe_parse_json(req)
        morph = data.get("morphology", "LingCube")
        ok, msg = agent.device_state.set_morphology(morph)
        status = 200 if ok else 400
        return JSONResponse(
            status_code=status,
            content={"success": ok, "message": msg, "active_morphology": agent.device_state.active_morphology}
        )

    @app.post("/api/robot/reflex")
    async def robot_reflex(req: Request):
        data = await safe_parse_json(req)
        reflex_type = data.get("reflex_type", "DNp03_ESCAPE")
        ok, msg = agent.device_state.trigger_reflex(reflex_type)
        status = 200 if ok else 400
        return JSONResponse(
            status_code=status,
            content={"success": ok, "message": msg, "telemetry": agent.device_state.get_telemetry()}
        )

    @app.post("/api/robot/avatar_face")
    async def robot_avatar_face(req: Request):
        data = await safe_parse_json(req)
        face = data.get("face", "idle")
        ok, msg = agent.device_state.set_avatar_face(face)
        status = 200 if ok else 400
        return JSONResponse(
            status_code=status,
            content={"success": ok, "message": msg, "avatar_face": agent.device_state.avatar_face}
        )

    # --- 2.1 Pet Avatar Switching Controls (Meta Muse Jollybot vs QiaoQiao) ---
    @app.get("/api/pet/list")
    async def get_pet_list():
        return {
            "active": agent.device_state.active_pet,
            "pets": [
                {
                    "id": "jollybot",
                    "name": "Meta Jollybot",
                    "type": "pixel_art",
                    "dimensions": "64x64 procedural dithered (scaled to 128x128)",
                    "origin": "Meta Muse Gadget SDK (avatar/muse_pixel.c)",
                    "description": "Meta Muse 官方原版过程化像素艺术小熊，实时光照、超椭圆反走样与 Bayer 抖动拟态渲染"
                },
                {
                    "id": "qiaoqiao",
                    "name": "灵伴悄悄",
                    "type": "procedural_vector",
                    "dimensions": "135x240 full canvas",
                    "origin": "LingBuddy Procedural Emotion System",
                    "description": "灵伴悄悄灵动矢量拟态伴侣，拥有丰富眼神、呼吸律动与多表情情感共鸣"
                }
            ]
        }

    @app.post("/api/pet/switch")
    async def switch_pet(req: Request):
        data = await safe_parse_json(req)
        pet = data.get("pet", "jollybot").lower()
        ok, msg = agent.device_state.switch_pet(pet)
        if ok and hasattr(agent, "serial") and agent.serial:
            agent.serial.send_command(f">pet={pet}")
        status = 200 if ok else 400
        return JSONResponse(
            status_code=status,
            content={"success": ok, "message": msg, "active_pet": agent.device_state.active_pet}
        )

    # --- 3. Chat & Streaming (Meta Muse Contract) ---
    @app.post("/api/chat")
    async def api_chat(req: Request):
        data = await safe_parse_json(req)
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        device_id = data.get("device_id", "StickS3")
        stream = data.get("stream", False)

        if stream:
            async def event_generator():
                async for chunk in agent.engine.chat_stream(message, session_id, device_id):
                    yield f"event: {chunk['event']}\ndata: {json.dumps(chunk['data'], ensure_ascii=False)}\n\n"
            return StreamingResponse(event_generator(), media_type="text/event-stream")

        result = await agent.engine.chat(message, session_id, device_id)
        return JSONResponse(result)

    @app.post("/chat/stream")
    async def chat_stream_post(req: Request):
        """Asynchronously registers a chat session and returns ack with msg_id."""
        data = await safe_parse_json(req)
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        device_id = data.get("device_id", "StickS3")
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"

        pending_stream_requests[msg_id] = {
            "message": message,
            "session_id": session_id,
            "device_id": device_id
        }
        return {"ack": True, "msg_id": msg_id, "status": "processing"}

    @app.get("/chat/subscribe")
    async def chat_subscribe(msg_id: Optional[str] = Query(None)):
        """Server-Sent Events subscription stream for generated chat responses."""
        params = pending_stream_requests.pop(msg_id, None) if msg_id else None

        async def sse_gen():
            if not params:
                # If no existing stream parameters, emit a heartbeat and finish
                yield f"event: message_start\ndata: {json.dumps({'msg_id': msg_id or 'none'}, ensure_ascii=False)}\n\n"
                yield f"event: message_done\ndata: {json.dumps({'status': 'idle'}, ensure_ascii=False)}\n\n"
                return

            async for chunk in agent.engine.chat_stream(
                params["message"],
                session_id=params["session_id"],
                device_id=params["device_id"],
                msg_id=msg_id
            ):
                yield f"event: {chunk['event']}\ndata: {json.dumps(chunk['data'], ensure_ascii=False)}\n\n"

        return StreamingResponse(sse_gen(), media_type="text/event-stream")

    # --- 4. Push-to-Talk 16kHz Audio Dictation ---
    @app.post("/api/voice/dictation")
    async def voice_dictation(req: Request, stream: bool = Query(True)):
        """
        Receives 16kHz PCM audio stream and returns streaming partial & final transcripts.
        """
        content_type = req.headers.get("content-type", "")
        body = await req.body()
        pcm_bytes = b""

        if "json" in content_type:
            try:
                j = json.loads(body.decode("utf-8"))
                if "audio" in j:
                    pcm_bytes = base64.b64decode(j["audio"])
            except Exception:
                pass
        else:
            pcm_bytes = body

        transcripts = await agent.dictation.transcribe(pcm_bytes)

        if not stream or req.headers.get("accept") == "application/json":
            final_item = next((t for t in reversed(transcripts) if t.get("type") == "final"), None)
            return {
                "status": "ok",
                "transcript": final_item["transcript"] if final_item else "",
                "transcripts": transcripts
            }

        # Streaming NDJSON
        async def ndjson_generator():
            for t in transcripts:
                yield json.dumps(t, ensure_ascii=False) + "\n"
                await asyncio.sleep(0.01)

        return StreamingResponse(ndjson_generator(), media_type="application/x-ndjson")

    # --- 5. Generic RPC Device Skills Dispatch ---
    @app.get("/rpc/{skill_name}.{method_name}")
    @app.post("/rpc/{skill_name}.{method_name}")
    async def rpc_dispatch(skill_name: str, method_name: str, req: Request):
        args: Dict[str, Any] = {}
        if req.method == "POST":
            b = await req.body()
            if b:
                try:
                    args = json.loads(b.decode("utf-8"))
                except Exception:
                    pass
        else:
            args = dict(req.query_params)

        # Normalize method dispatch
        m = method_name.lower()
        if "roll" in m:
            tool_name = "lingcube_roll"
        elif "epm" in m:
            tool_name = "lingcube_epm_latch"
        elif "morphology" in m:
            tool_name = "lingcube_set_morphology"
        elif "reflex" in m:
            tool_name = "lingcube_trigger_reflex"
        elif "avatar" in m or "face" in m:
            tool_name = "sticks3_set_avatar"
        elif "telemetry" in m or "state" in m:
            tool_name = "get_robot_telemetry"
        elif "interact" in m or "pet" in m or "feed" in m:
            tool_name = "lingbuddy_interact"
        else:
            tool_name = method_name

        result = agent.registry.execute_tool(tool_name, args)
        return {
            "status": "ok" if result.get("success", True) else "error",
            "skill": skill_name,
            "method": method_name,
            "tool_dispatched": tool_name,
            "result": result
        }

    # --- 6. Tunnel Info Endpoint ---
    @app.get("/api/tunnel/info")
    async def get_tunnel_info():
        return agent.tunnel.get_info()

    # --- 7. WebSocket Realtime Voice & Avatar Gateway ---
    @app.websocket("/ws/v1/realtime")
    async def websocket_realtime_endpoint(ws: WebSocket):
        await ws.accept()
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        await ws.send_text(json.dumps({
            "type": "session.created",
            "session": {
                "id": session_id,
                "model": agent.engine.model_name,
                "voice": "cherry"
            }
        }, ensure_ascii=False))

        audio_buffer = bytearray()
        cancelled = False

        try:
            while True:
                msg_text = await ws.receive_text()
                event = json.loads(msg_text)
                ev_type = event.get("type", "")

                if ev_type == "session.update":
                    await ws.send_text(json.dumps({
                        "type": "session.updated",
                        "session": event.get("session", {})
                    }, ensure_ascii=False))

                elif ev_type == "input_audio_buffer.append":
                    b64_audio = event.get("audio", "")
                    if b64_audio:
                        chunk = base64.b64decode(b64_audio)
                        audio_buffer.extend(chunk)
                        if len(audio_buffer) == len(chunk):
                            # First audio chunk -> notify speech started
                            agent.device_state.set_avatar_face("listening")
                            await ws.send_text(json.dumps({
                                "type": "input_audio_buffer.speech_started",
                                "audio_start_ms": 120
                            }, ensure_ascii=False))
                            await ws.send_text(json.dumps({
                                "type": "avatar.expression",
                                "expression": "listening"
                            }, ensure_ascii=False))

                elif ev_type == "input_audio_buffer.commit":
                    # Speech ended, trigger transcription and response
                    agent.device_state.set_avatar_face("thinking")
                    await ws.send_text(json.dumps({
                        "type": "avatar.expression",
                        "expression": "thinking"
                    }, ensure_ascii=False))

                    transcripts = await agent.dictation.transcribe(bytes(audio_buffer))
                    final_trans = next((t["transcript"] for t in reversed(transcripts) if t.get("type") == "final"), "你好")
                    audio_buffer.clear()

                    # Send text transcript deltas
                    for ch in final_trans:
                        if cancelled:
                            break
                        await ws.send_text(json.dumps({
                            "type": "response.audio_transcript.delta",
                            "delta": ch
                        }, ensure_ascii=False))
                        await asyncio.sleep(0.01)

                    # Trigger reply and audio synthesis
                    chat_res = await agent.engine.chat(final_trans, session_id=session_id)
                    reply_text = chat_res.get("reply", "")

                    agent.device_state.set_avatar_face("speaking")
                    await ws.send_text(json.dumps({
                        "type": "avatar.expression",
                        "expression": "speaking"
                    }, ensure_ascii=False))

                    # Mock synthesized PCM audio chunk (16kHz 16-bit Mono sine tone)
                    sample_rate = 16000
                    num_samples = int(0.2 * sample_rate)
                    synth_samples = [int(1000 * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(num_samples)]
                    raw_synth_pcm = struct.pack(f"<{len(synth_samples)}h", *synth_samples)
                    synth_b64 = base64.b64encode(raw_synth_pcm).decode("ascii")

                    await ws.send_text(json.dumps({
                        "type": "response.audio.delta",
                        "delta": synth_b64
                    }, ensure_ascii=False))

                    # Completion
                    agent.device_state.set_avatar_face(chat_res.get("avatar_face", "happy"))
                    await ws.send_text(json.dumps({
                        "type": "response.done",
                        "response_id": f"resp_{uuid.uuid4().hex[:8]}"
                    }, ensure_ascii=False))

                elif ev_type == "response.cancel":
                    # Hardware or Barge-In interrupt
                    cancelled = True
                    audio_buffer.clear()
                    agent.device_state.set_avatar_face("listening")
                    await ws.send_text(json.dumps({
                        "type": "response.cancelled",
                        "reason": "barge_in"
                    }, ensure_ascii=False))

                elif ev_type == "device.telemetry":
                    # Update hardware telemetry
                    telem_data = event.get("telemetry", {})
                    if "v_bus" in telem_data:
                        agent.device_state.v_bus = float(telem_data["v_bus"])

        except WebSocketDisconnect:
            logger.info("Realtime WebSocket client disconnected (%s)", session_id)
        except Exception as e:
            logger.warning("Realtime WebSocket error: %s", e)

    return app


# -----------------------------------------------------------------------------
# Main Bailian Cloud Agent Server Controller
# -----------------------------------------------------------------------------
class BailianMuseCloudAgent:
    """
    Main controller for Bailian Cloud Agent Server.
    Orchestrates FastAPI REST/WS service, Serial Hatch bus, and Public Tunnel.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        serial_port: str = "COM3",
        enable_serial: bool = False,
        tunnel_mode: str = "none",
        api_key: Optional[str] = None,
        force_mock_llm: bool = False
    ):
        self.host = host
        self.port = port
        self.serial_port = serial_port
        self.enable_serial = enable_serial
        self.tunnel_mode = tunnel_mode

        # Core subsystems
        self.device_state = LingCubeDeviceState()
        self.registry = DeviceSkillRegistry(self.device_state)
        self.engine = BailianAgentEngine(
            self.registry,
            api_key=api_key,
            force_mock=force_mock_llm
        )
        self.dictation = AudioDictationBridge(self.engine)
        self.serial = SerialHatchManager(
            port=serial_port,
            baudrate=115200,
            agent_engine=self.engine,
            device_state=self.device_state
        )
        self.tunnel = TunnelSupervisor(
            local_port=port,
            mode=tunnel_mode
        )
        self.app = create_bailian_muse_app(self)
        self._server: Optional[uvicorn.Server] = None
        self._server_thread: Optional[threading.Thread] = None

    def start(self, blocking: bool = True):
        """Starts all background services and the HTTP server."""
        logger.info("Initializing Bailian Cloud Agent Server on %s:%d...", self.host, self.port)

        # 1. Start Serial Hatch if enabled
        if self.enable_serial:
            self.serial.start()

        # 2. Start Public Tunnel if configured
        if self.tunnel_mode != "none":
            threading.Thread(
                target=self.tunnel.start_tunnel,
                daemon=True,
                name="TunnelStarter"
            ).start()

        # 3. Start Web Server
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        self._server = uvicorn.Server(config)

        if blocking:
            self._server.run()
        else:
            self._server_thread = threading.Thread(
                target=self._server.run,
                daemon=True,
                name="UvicornServerThread"
            )
            self._server_thread.start()
            # Allow server time to bind socket
            time.sleep(0.5)

    def stop(self):
        """Gracefully tears down all services."""
        logger.info("Stopping Bailian Cloud Agent Server...")
        if self.serial:
            self.serial.stop()
        if self.tunnel:
            self.tunnel.stop()
        if self._server:
            self._server.should_exit = True
        logger.info("Bailian Cloud Agent Server stopped cleanly.")


def run_cloud_agent(
    host: str = "0.0.0.0",
    port: int = 8000,
    serial_port: str = "COM3",
    enable_serial: bool = False,
    tunnel_mode: str = "auto",
    api_key: Optional[str] = None,
    force_mock: bool = False
) -> BailianMuseCloudAgent:
    """Helper function to create and run an agent instance."""
    agent = BailianMuseCloudAgent(
        host=host,
        port=port,
        serial_port=serial_port,
        enable_serial=enable_serial,
        tunnel_mode=tunnel_mode,
        api_key=api_key,
        force_mock_llm=force_mock
    )
    agent.start(blocking=True)
    return agent


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bailian Cloud Agent Server (Meta Muse Replacement)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="HTTP listen host")
    parser.add_argument("--port", type=int, default=8000, help="HTTP listen port")
    parser.add_argument("--serial-port", type=str, default="COM3", help="StickS3 physical serial port")
    parser.add_argument("--enable-serial", action="store_true", help="Enable physical serial Hatch connection")
    parser.add_argument("--tunnel", choices=["auto", "cloudflare", "ngrok", "none"], default="none", help="Public service tunnel mode")
    parser.add_argument("--api-key", type=str, default=None, help="Alibaba Cloud DashScope API Key")
    parser.add_argument("--mock-llm", action="store_true", help="Force Intelligent Mock LLM mode")
    args = parser.parse_args()

    run_cloud_agent(
        host=args.host,
        port=args.port,
        serial_port=args.serial_port,
        enable_serial=args.enable_serial,
        tunnel_mode=args.tunnel,
        api_key=args.api_key,
        force_mock=args.mock_llm
    )
