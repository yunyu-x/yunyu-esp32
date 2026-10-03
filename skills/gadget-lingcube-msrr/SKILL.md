---
name: gadget-lingcube-msrr
description: >-
  Discover, monitor telemetry, and actuate LingCube (microUnit) modular self-reconfigurable
  robots through Meta Muse Home Link. Supports momentum-wheel tumbling, electro-permanent
  magnet (EPM) face latching, bio-neuromorphic reflexes, and multi-cube morphology reconfiguration.
---

# LingCube (microUnit): Modular Self-Reconfigurable Robot (MSRR)

Use this skill when Meta Muse detects a local `LingCube` or `LingBuddy` bridge and the user requests physical robotic locomotion, docking, posture querying, or swarm reconfiguration.

## Identify the Device

- Match mDNS service `_lingcube._tcp` or HTTP `/api/device/info` returning `device_type: "LingCube-MSRR"` or `"LingBuddy-Companion"`.
- Validate hardware generation: `gen: 2` (ESP32-S3 4-layer PCBA with DRV8833 and EPM pulse H-bridge).
- Confirm unique unit identifier (e.g., `LingCube-01`, `LingCluster-Alpha`).

## Prerequisites

- Device is powered on, Wi-Fi connected, and reachable via the Muse Home Link local tunnel or LingBuddy BLE gateway.
- Battery bus voltage must be $\ge 3.40\text{V}$ before executing dynamic impulse tumbles or multi-face EPM discharge pulses.
- Operational safety envelope: clearance of at least $100\text{ mm}$ around the unit for single-edge roll maneuvers.

## REST / RPC API Endpoints

The gadget exposes the following standard HTTP endpoints on its local port (default: `8000` or `8080`):

| Method | Endpoint | Description | Payload / Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health probe & tunnel liveness | None |
| `GET` | `/api/device/info` | Hardware info & battery state | None |
| `GET` | `/api/robot/telemetry` | 6-DOF IMU, bus voltage, docking status | None |
| `POST` | `/api/robot/roll` | Execute dynamic momentum wheel impulse tumble | `{"direction": "+X"\|"-X"\|"+Y"\|"-Y", "torque": float, "duration_s": float}` |
| `POST` | `/api/robot/epm` | Pulse EPM coil on target face (1~6) | `{"face_id": 1..6, "state": "LATCH"\|"UNLATCH", "duration_ms": 20}` |
| `POST` | `/api/robot/morphology` | Reconfigure multi-cube cluster | `{"morphology": "LingChain"\|"LingRing"\|"LingSheet"\|"LingLattice"\|"LingWalker"}` |
| `POST` | `/api/robot/reflex` | Trigger neuromorphic bio-reflex | `{"reflex_type": "DNp03_ESCAPE"\|"HALTERE_DAMP"\|"EMERGENCY_RELEASE"}` |

## Workflow

1. **Telemetry Check**:
   - Query `GET /api/robot/telemetry`.
   - Verify `v_bus >= 3.4V` and `fault_flags == 0`.
   - Report current posture (pitch $\theta$, roll $\phi$) and battery percentage to the user.

2. **Single-Cube Motion (Impulse Tumble)**:
   - For a user request like *"Roll LingCube forward"*:
   - Ensure target direction is clear.
   - Send `POST /api/robot/roll` with `{"direction": "+X", "torque": 0.25, "duration_s": 0.35}`.
   - Query telemetry post-motion to confirm the $90^\circ$ rotation milestone was attained.

3. **Docking & Inter-Unit Attachment**:
   - For attaching to another cube or base dock:
   - Send `POST /api/robot/epm` with `{"face_id": <face>, "state": "LATCH"}`.
   - EPM dual-state magnet draws zero static current once switched, providing $35\text{N}+$ holding force.

4. **Cluster Reconfiguration (LingMorphologies)**:
   - For requests like *"Assemble cubes into a crawler chain"*:
   - Send `POST /api/robot/morphology` with `{"morphology": "LingChain"}`.
   - Monitor distributed lease token negotiation and assembly sequence.

5. **Bio-Reflex Safety Override**:
   - If an unexpected collision, freefall, or overcurrent is detected:
   - Trigger `POST /api/robot/reflex` with `{"reflex_type": "HALTERE_DAMP"}` or `"EMERGENCY_RELEASE"`.

## Safety Limits & Murphy Defense

- **Thermal Duty Cycle**: EPM discharge pulses must be spaced by at least $100\text{ ms}$ to prevent coil overheating and RC watchdog timeout.
- **Battery Low Voltage Cutoff**: If $V_{\text{bus}} < 3.30\text{V}$, all high-current actuators (DRV8833 and EPM) are hardware-locked; notify user to charge the unit.
- **No Blind Retries**: If a roll motion fails to change the IMU posture by $>30^\circ$, do not retry blindly; query obstacle sensors or prompt the user.

## Sources

- [LingCube Engineering Knowledge Base](file:///d:/workspace/code/microUnit/README.md)
- [PCBA v2 Hardware Spec](file:///d:/workspace/code/microUnit/doc/20_灵方微型自重构机器人工业级PCBA全流程设计与工程验证详案.md)
- [Embedded DriverHub Architecture](file:///d:/workspace/code/microUnit/doc/24_灵方微型自重构机器人专业嵌入式驱动架构与自愈体系开发详案.md)
