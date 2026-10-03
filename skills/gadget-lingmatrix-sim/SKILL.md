---
name: gadget-lingmatrix-sim
description: >-
  Control, monitor, and query the LingMatrix MuJoCo multi-physics digital twin simulation
  and hardware-in-the-loop (HIL) testbench via Meta Muse Home Link. Supports running 1000Hz
  contact dynamic simulations, spawning cube assemblies, executing regression test suites,
  and retrieving virtual telemetry curves.
---

# LingMatrix Digital Twin & Simulation Platform

Use this skill when the user asks Meta Muse to run virtual simulations, verify kinematics before physical actuation, spawn modular configurations in MuJoCo, or run automated verification tests.

## Identify the Service

- Endpoint responds to `GET /health` with `service: "LingMatrix-Simulation-Platform"`.
- Supports 4-stage physics solver (SingleUnit, DualUnit, MultiUnit, NeuromorphicSwarm).

## Prerequisites

- Python simulation server (`simulation/server.py`) is running locally on port `8000` or accessible through a public preview tunnel.
- MuJoCo 3.x runtime and NumPy/SciPy are loaded.

## Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health & active scenario check |
| `POST` | `/api/simulate/stage1` | Run Single-Unit 45° barrier climb simulation |
| `POST` | `/api/simulate/stage2` | Run Dual-Unit edge-hinge cooperative climb simulation |
| `POST` | `/api/simulate/stage3` | Run Multi-Unit crawl wave & morphology deformation |
| `POST` | `/api/simulate/stage4` | Run Neuromorphic swarm lattice assembly & obstacle avoidance |
| `GET` | `/api/simulate/telemetry` | Retrieve the latest simulation run telemetry JSON & curve summary |
| `POST` | `/api/simulate/run_tests` | Run the complete automated regression test suite (`pytest tests/`) |

## Workflow

1. **Pre-flight Digital Twin Validation**:
   - Before commanding a physical LingCube to execute a risky maneuver, ask Muse to simulate it first.
   - Call `POST /api/simulate/stage1` with user-specified target RPM ($18,000$) and brake torque ($0.25\text{ N}\cdot\text{m}$).
   - Parse telemetry result: if `success == true` and kinetic energy transfer $\ge 0.052\text{ J}$, proceed to physical execution.

2. **Swarm Assembly Simulation**:
   - When user designs a new structure, call `POST /api/simulate/stage4` with target morphology.
   - Verify spring-damper lattice convergence without collision interference.

3. **Continuous Engineering Quality Gate**:
   - Muse can trigger automated regression tests via `POST /api/simulate/run_tests`.
   - Returns structured test pass rate (e.g. $156/157$ passed).

## Safety & Resource Limits

- Simulation runs are constrained to $1.0\sim 5.0$ seconds of simulated physics time to conserve host CPU.
- Headless execution avoids graphics card memory locks.
