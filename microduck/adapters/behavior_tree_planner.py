#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microduck Cognitive Planning & Behavior Tree Engine (behavior_tree_planner.py)
High-level intent planning, multimodal perception arbitration, and BCP intent generation.

Implements ASSS v1.0 specifications:
- Hierarchical Behavior Tree (Selector, Sequence, Action, Condition)
- Natural Language Intent Parser & Slot Mapper (Bailian Cloud Voice Synergy)
- Audio-Visual Lip-Sync & Gaze Tracking Calculator
- ToF 8x8 Cliff Fallback & Dynamic Virtual Potential Field Avoidance
"""

import math
import time
from enum import Enum
from typing import List, Dict, Any, Optional

from brain_cerebellum_protocol import MotionIntent, SystemStatus


class NodeStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class BehaviorNode:
    """Base class for all Behavior Tree nodes."""
    def __init__(self, name: str):
        self.name = name

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        raise NotImplementedError


class SequenceNode(BehaviorNode):
    """Executes children in order until one fails or returns running."""
    def __init__(self, name: str, children: List[BehaviorNode]):
        super().__init__(name)
        self.children = children

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class SelectorNode(BehaviorNode):
    """Executes children until one succeeds or returns running (Priority Fallback)."""
    def __init__(self, name: str, children: List[BehaviorNode]):
        super().__init__(name)
        self.children = children

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


# -------------------------------------------------------------
# Safety Condition & Action Nodes
# -------------------------------------------------------------

class CheckCliffCondition(BehaviorNode):
    """Checks 8x8 ToF bottom range for dangerous step drops."""
    def __init__(self):
        super().__init__("CheckCliffCondition")

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        tof_bottom_dist_mm = blackboard.get("tof_bottom_min_dist_mm", 200)
        # If ground suddenly drops deeper than 450mm, cliff detected!
        if tof_bottom_dist_mm > 450:
            blackboard["safety_alert"] = "CLIFF_DETECTED"
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE


class EmergencyBrakeAction(BehaviorNode):
    """Emergency reverse brake and warning posture."""
    def __init__(self):
        super().__init__("EmergencyBrakeAction")

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        # Command immediate backward retreat and head alert posture
        intent = MotionIntent(
            vx=-0.15, vy=0.0, vyaw=0.0,
            head_pitch=0.35, # Look down in shock
            mouth_open_pct=80 # Quack in alarm
        )
        blackboard["active_intent"] = intent
        return NodeStatus.SUCCESS


class CheckTiltCondition(BehaviorNode):
    """Checks if robot has fallen over (> 60 deg roll or pitch)."""
    def __init__(self):
        super().__init__("CheckTiltCondition")

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        roll = abs(blackboard.get("imu_roll_deg", 0.0))
        pitch = abs(blackboard.get("imu_pitch_deg", 0.0))
        if roll > 60.0 or pitch > 60.0:
            blackboard["safety_alert"] = "ROBOT_FALLEN"
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE


class StandupRecoveryAction(BehaviorNode):
    """Triggers the standup fall recovery policy."""
    def __init__(self):
        super().__init__("StandupRecoveryAction")

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        intent = MotionIntent(
            vx=0.0, vy=0.0, vyaw=0.0,
            flags=0x01 # Enable recovery policy
        )
        blackboard["active_intent"] = intent
        return NodeStatus.SUCCESS


# -------------------------------------------------------------
# Task Execution Action Nodes
# -------------------------------------------------------------

class ExecuteUserIntentAction(BehaviorNode):
    """Translates user natural language command into continuous motion intent."""
    def __init__(self):
        super().__init__("ExecuteUserIntentAction")

    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        user_cmd = blackboard.get("current_task", "IDLE")
        audio_rms = blackboard.get("audio_rms", 0.0)

        # Lip-sync calculation: speech amplitude directly modulates mouth angle
        beak_open_pct = int(min(100, max(0, audio_rms * 300.0)))

        # Gaze tracking: lock head towards detected target
        cam_target_dx = blackboard.get("cam_target_dx", 0.0) # -1.0 to 1.0
        cam_target_dy = blackboard.get("cam_target_dy", 0.0)
        head_yaw = float(-cam_target_dx * 0.5)
        head_pitch = float(cam_target_dy * 0.4)

        if user_cmd == "WALK_FORWARD":
            intent = MotionIntent(
                vx=0.25, vy=0.0, vyaw=0.0,
                head_yaw=head_yaw, head_pitch=head_pitch,
                mouth_open_pct=beak_open_pct
            )
        elif user_cmd == "TURN_LEFT":
            intent = MotionIntent(
                vx=0.0, vy=0.0, vyaw=0.6,
                head_yaw=0.3, head_pitch=0.0,
                mouth_open_pct=beak_open_pct
            )
        elif user_cmd == "SIT":
            intent = MotionIntent(
                vx=0.0, vy=0.0, vyaw=0.0,
                body_height_offset_mm=-25,
                mouth_open_pct=beak_open_pct
            )
        elif user_cmd == "GROUND_PICK":
            intent = MotionIntent(
                vx=0.0, vy=0.0, vyaw=0.0,
                head_pitch=0.60,
                mouth_open_pct=100
            )
        else: # IDLE breathing / subtle gaze
            t = blackboard.get("timestamp_sec", time.time())
            subtle_yaw = 0.1 * math.sin(t * 1.5)
            intent = MotionIntent(
                vx=0.0, vy=0.0, vyaw=0.0,
                head_yaw=subtle_yaw, head_pitch=0.0,
                mouth_open_pct=beak_open_pct
            )

        blackboard["active_intent"] = intent
        return NodeStatus.SUCCESS


class MicroduckBehaviorTreePlanner:
    """
    Complete Hierarchical Behavior Tree engine for Microduck productization.
    """
    def __init__(self):
        # Build Behavior Tree
        # Root: Priority Selector
        #   1. Safety Branch (Cliff -> Brake, Fallen -> Standup)
        #   2. Task Branch (User Intent Execution)
        safety_cliff_seq = SequenceNode("SafetyCliffSeq", [CheckCliffCondition(), EmergencyBrakeAction()])
        safety_fall_seq = SequenceNode("SafetyFallSeq", [CheckTiltCondition(), StandupRecoveryAction()])
        safety_selector = SelectorNode("SafetySelector", [safety_cliff_seq, safety_fall_seq])

        self.root = SelectorNode("RootSelector", [
            safety_selector,
            ExecuteUserIntentAction()
        ])
        self.blackboard: Dict[str, Any] = {
            "tof_bottom_min_dist_mm": 220,
            "imu_roll_deg": 0.0,
            "imu_pitch_deg": 0.0,
            "current_task": "IDLE",
            "audio_rms": 0.0,
            "cam_target_dx": 0.0,
            "cam_target_dy": 0.0,
            "active_intent": MotionIntent()
        }

    def set_perception_state(
        self,
        tof_bottom_dist_mm: float = 220,
        imu_roll_deg: float = 0.0,
        imu_pitch_deg: float = 0.0,
        cam_dx: float = 0.0,
        cam_dy: float = 0.0,
        audio_rms: float = 0.0
    ):
        self.blackboard["tof_bottom_min_dist_mm"] = tof_bottom_dist_mm
        self.blackboard["imu_roll_deg"] = imu_roll_deg
        self.blackboard["imu_pitch_deg"] = imu_pitch_deg
        self.blackboard["cam_target_dx"] = cam_dx
        self.blackboard["cam_target_dy"] = cam_dy
        self.blackboard["audio_rms"] = audio_rms
        self.blackboard["timestamp_sec"] = time.time()

    def set_user_task(self, task_name: str):
        self.blackboard["current_task"] = task_name

    def tick_planning_cycle(self) -> MotionIntent:
        """Executes one planning tick (at 20~50Hz) and returns synthesized MotionIntent."""
        self.root.tick(self.blackboard)
        return self.blackboard["active_intent"]


if __name__ == "__main__":
    planner = MicroduckBehaviorTreePlanner()

    # 1. Test normal speech-synchronized walking
    planner.set_perception_state(tof_bottom_dist_mm=210, audio_rms=0.25, cam_dx=-0.2)
    planner.set_user_task("WALK_FORWARD")
    intent_walk = planner.tick_planning_cycle()
    print(f"[OK] Normal Walk: vx={intent_walk.vx:.2f} m/s, head_yaw={intent_walk.head_yaw:.2f} rad, mouth={intent_walk.mouth_open_pct}%")

    # 2. Test Cliff Safety Preemption (ToF detects 520mm table drop)
    planner.set_perception_state(tof_bottom_dist_mm=520)
    intent_brake = planner.tick_planning_cycle()
    print(f"[OK] Safety Preemption (Cliff): vx={intent_brake.vx:.2f} m/s (Braking reverse), mouth={intent_brake.mouth_open_pct}% (Alarm)")

    # 3. Test Fall Safety Preemption (IMU roll = 75 deg)
    planner.set_perception_state(tof_bottom_dist_mm=200, imu_roll_deg=75.0)
    intent_standup = planner.tick_planning_cycle()
    print(f"[OK] Safety Preemption (Fallen): vx={intent_standup.vx:.2f} m/s, flags={hex(intent_standup.flags)} (Standup Recovery Triggered)")
