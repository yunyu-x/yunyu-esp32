# Repository Context Package: microduck_rl

> 纯确定性打包生成，严格按 POSIX 路径字典序排列以优化 LLM Prompt Caching 命中率。

## 1. 仓库全景指标
- **文件总数**: 13
- **代码总行数**: 6930
- **预估 Token 数**: ~80,580
- **脱敏凭据数**: 0

## 2. 目录拓扑结构
```text
microduck_rl/
  └── .gitignore (0.5 KB)
  └── AGENTS.md (17.6 KB)
  └── CLAUDE.md (0.0 KB)
  └── LICENSE (11.3 KB)
  └── README.md (13.2 KB)
  ├── docs/
    └── roller_standup_policy_summary.md (12.5 KB)
    ├── superpowers/
      ├── plans/
        └── 2026-07-17-roller-crouch-glide.md (36.7 KB)
        └── 2026-07-22-roller-slope.md (28.5 KB)
        └── 2026-07-24-ground-pick-pose-following.md (25.1 KB)
        └── 2026-07-24-shoot-pose-following.md (30.4 KB)
        └── 2026-07-27-swizzle-head-control.md (10.1 KB)
        └── 2026-08-04-roller-standup.md (59.4 KB)
        └── 2026-08-04-spin-env.md (65.6 KB)
      ├── specs/
        └── 2026-07-17-roller-crouch-glide-design.md (8.2 KB)
        └── 2026-07-22-roller-slope-design.md (6.4 KB)
        └── 2026-07-23-swizzle-env-design.md (5.2 KB)
        └── 2026-07-24-ground-pick-pose-following-design.md (7.9 KB)
        └── 2026-07-24-shoot-pose-following-design.md (10.8 KB)
        └── 2026-07-27-swizzle-head-control-design.md (4.7 KB)
        └── 2026-08-04-roller-standup-design.md (20.0 KB)
        └── 2026-08-04-spin-env-design.md (23.2 KB)
  └── pyproject.toml (5.2 KB)
  ├── scripts/
    └── crouch_pose_editor.py (3.5 KB)
    └── export.py (0.4 KB)
    ├── hf/
      └── README.md (3.2 KB)
      └── train_hf.py (0.4 KB)
      └── uploader.py (2.5 KB)
    └── infer_policy.py (91.6 KB)
    └── odom_anchor_points.py (11.8 KB)
    └── odom_anchor_sets.json (4.7 KB)
    └── play_latest.py (2.0 KB)
    └── plot_observations_comparison_plotly.py (10.6 KB)
    └── testbench_sim2real.py (24.4 KB)
    └── validate_bam_testbench.py (9.1 KB)
    └── view_slope_terrain.py (4.1 KB)
    └── wandb_utils.py (5.1 KB)
  ├── src/
    ├── mjlab_microduck/
      └── __init__.py (0.0 KB)
      ├── actuator/
        └── __init__.py (0.3 KB)
        └── friction_dr_bam.py (5.1 KB)
      └── export.py (12.4 KB)
      └── hf_jobs.py (20.5 KB)
      ├── publish/
        └── __init__.py (0.3 KB)
        └── cli.py (9.4 KB)
        └── manifest.py (16.0 KB)
      ├── robot/
        └── __init__.py (0.0 KB)
        ├── microduck/
          └── add_backlash.py (5.9 KB)
          └── additional.xml (0.6 KB)
          └── allcollisions_contacts.xml (0.6 KB)
          └── apartment.xml (25.9 KB)
          ├── assets/
            └── ankle_l_v1.part (0.4 KB)
            └── ankle_l_v1.stl (230.5 KB)
            └── ankle_left.part (0.4 KB)
            └── ankle_left.stl (243.1 KB)
            └── ankle_r_v1.part (0.4 KB)
            └── ankle_r_v1.stl (230.3 KB)
            └── ankle_right.part (0.4 KB)
            └── ankle_right.stl (243.1 KB)
            └── banana_pcb_locker.part (0.4 KB)
            └── banana_pcb_locker.stl (67.9 KB)
            └── bearing_roll.part (0.4 KB)
            └── bearing_roll.stl (118.2 KB)
            └── bottom_head_shell.part (0.4 KB)
            └── elec_rpi_robot_hat_pcb.part (0.4 KB)
            └── face_part.part (0.4 KB)
            └── foot_left.part (0.4 KB)
            └── foot_right.part (0.4 KB)
            └── hip_l.part (0.4 KB)
            └── jaw.part (0.4 KB)
            └── jaw_soft.part (0.4 KB)
            └── left_shell.part (0.4 KB)
            └── leg.part (0.4 KB)
            └── lens.part (0.4 KB)
            └── lens.stl (91.5 KB)
            └── m12_lens_holder.part (0.4 KB)
            └── motor_support.part (0.4 KB)
            └── motor_support.stl (176.6 KB)
            └── neck.part (0.4 KB)
            └── neck.stl (71.8 KB)
            └── neck_pitch.part (0.4 KB)
            └── noenoeil.part (0.4 KB)
            └── noenoeil.stl (48.1 KB)
            └── np_f970.part (0.4 KB)
            └── pcb__raspberry_pi_zero_2_w.part (0.4 KB)
            └── power_support.part (0.4 KB)
            └── right_shell.part (0.4 KB)
            └── rim.part (0.4 KB)
            └── rim.stl (112.6 KB)
            └── roller_blade.part (0.4 KB)
            └── seeed_bearing__configuration__22x16x4.part (0.4 KB)
            └── seeed_bearing__configuration_default.part (0.4 KB)
            └── soft_mouth_top.part (0.4 KB)
            └── sole_left.part (0.4 KB)
            └── sole_right.part (0.4 KB)
            └── speaker.part (0.4 KB)
            └── speaker.stl (0.7 KB)
            └── tire.part (0.4 KB)
            └── top_head_shell.part (0.4 KB)
            └── trunk_base.part (0.4 KB)
            └── trunk_base.stl (180.6 KB)
            └── upper_leg_left.part (0.4 KB)
            └── upper_leg_right.part (0.4 KB)
            └── upper_leg_rigidity_plate.part (0.4 KB)
            └── upper_leg_rigidity_plate.stl (175.9 KB)
            └── xl330.part (0.4 KB)
            └── xl330.stl (201.5 KB)
            └── yaw2roll.part (0.4 KB)
            └── yaw_roll_motion.part (0.4 KB)
            └── yaw_roll_motion.stl (284.0 KB)
          └── ball.xml (0.7 KB)
          └── config_mjcf_allcollisions.json (1.5 KB)
          └── config_mjcf_groundcontact.json (2.0 KB)
          └── config_mjcf_groundcontact_backlash.json (2.1 KB)
          └── config_mjcf_groundcontact_rollers.json (2.1 KB)
          └── config_mjcf_groundcontact_rollers_backlash.json (2.2 KB)
          └── config_mjcf_walk.json (1.8 KB)
          └── config_mjcf_walk_backlash.json (2.0 KB)
          └── joints_properties.xml (1.8 KB)
          └── robot_allcollisions.xml (42.5 KB)
          └── robot_allcollisions_backlash.xml (44.6 KB)
          └── robot_groundcontact.xml (32.6 KB)
          └── robot_groundcontact_backlash.xml (34.6 KB)
          └── robot_groundcontact_rollers.xml (35.3 KB)
          └── robot_groundcontact_rollers_backlash.xml (37.4 KB)
          └── robot_walk.xml (31.7 KB)
          └── robot_walk_backlash.xml (33.8 KB)
          └── scene.xml (2.4 KB)
          └── scene_allcollisions.xml (2.4 KB)
          └── scene_apartment.xml (2.5 KB)
          └── scene_backlash.xml (2.6 KB)
          └── scene_ball.xml (1.2 KB)
          └── scene_rollers.xml (2.4 KB)
          └── scene_vslam.xml (2.5 KB)
          └── scene_walk.xml (2.3 KB)
          └── scene_walk_backlash.xml (2.6 KB)
          └── sensors.xml (0.4 KB)
          └── vslam_room.xml (4.1 KB)
        └── microduck_constants.py (13.5 KB)
        └── testbench_constants.py (1.8 KB)
        ├── xl330_test_bench/
          ├── assets/
            └── arm.part (0.4 KB)
            └── arm.stl (147.7 KB)
            └── axis.part (0.4 KB)
            └── axis.stl (14.1 KB)
            └── bench_holder.part (0.4 KB)
            └── bench_holder.stl (58.9 KB)
            └── part_1.part (0.4 KB)
            └── part_1.stl (147.7 KB)
            └── part_2.part (0.4 KB)
            └── part_2.stl (28.2 KB)
            └── part_3.part (0.4 KB)
            └── part_3.stl (58.9 KB)
            └── part_4.part (0.4 KB)
            └── part_4.stl (28.2 KB)
            └── part_5.part (0.4 KB)
            └── part_5.stl (14.1 KB)
            └── spacer.part (0.4 KB)
            └── spacer.stl (28.2 KB)
            └── weight.part (0.4 KB)
            └── weight.stl (28.2 KB)
            └── xl330.part (0.4 KB)
            └── xl330.stl (201.5 KB)
          └── config.json (0.5 KB)
          └── joints_properties.xml (0.9 KB)
          └── scene.xml (0.9 KB)
          └── xl330_test_bench.xml (4.6 KB)
      ├── sim/
        └── __init__.py (0.3 KB)
        └── body_server.py (27.3 KB)
        └── camera.py (7.0 KB)
        └── tof.py (4.5 KB)
      ├── tasks/
        └── __init__.py (11.9 KB)
        └── backlash.py (4.3 KB)
        └── distill.py (10.9 KB)
        └── microduck_ball_kick_env_cfg.py (29.6 KB)
        └── microduck_ground_pick_env_cfg.py (32.8 KB)
        └── microduck_roller_crouch_env_cfg.py (19.5 KB)
        └── microduck_roller_slope_env_cfg.py (12.1 KB)
        └── microduck_roller_standup_env_cfg.py (27.6 KB)
        └── microduck_roulade_env_cfg.py (35.0 KB)
        └── microduck_sitstand_env_cfg.py (43.8 KB)
        └── microduck_spin_env_cfg.py (19.9 KB)
        └── microduck_standup_env_cfg.py (58.4 KB)
        └── microduck_velocity_env_cfg.py (44.8 KB)
        └── microduck_velocity_rollers_env_cfg.py (30.1 KB)
        └── microduck_velocity_swizzle_env_cfg.py (9.5 KB)
        └── microduck_velstand_env_cfg.py (40.3 KB)
        └── slope_terrain.py (5.0 KB)
        └── symmetry.py (7.3 KB)
        └── testbench_env_cfg.py (9.5 KB)
      └── train_cli.py (1.5 KB)
      └── train_hook.py (2.5 KB)
  ├── tests/
    └── test_aarch64_cuda_torch.py (5.3 KB)
    └── test_crouch_glide.py (3.9 KB)
    └── test_descent_speed.py (1.3 KB)
    └── test_ground_pick_cfg.py (2.4 KB)
    └── test_ground_pick_pose.py (4.6 KB)
    └── test_head_pose_bias.py (6.2 KB)
    └── test_hf_jobs_flag.py (7.7 KB)
    └── test_infer_policy_bam.py (4.2 KB)
    └── test_nan_guard.py (1.9 KB)
    └── test_obs_nan_guard.py (4.6 KB)
    └── test_publish_manifest.py (10.9 KB)
    └── test_roller_crouch_cfg.py (2.3 KB)
    └── test_roller_slope_cfg.py (4.5 KB)
    └── test_roller_standup_cfg.py (24.9 KB)
    └── test_slope_curriculum.py (1.4 KB)
    └── test_slope_terrain.py (4.0 KB)
    └── test_spin.py (15.9 KB)
    └── test_spin_cfg.py (4.5 KB)
    └── test_swizzle_head_cfg.py (1.8 KB)
    └── test_velstand_cfg.py (18.9 KB)
    └── test_wheel_glide.py (2.0 KB)
```

## 3. 源文件代码包

### File: `.gitignore` (40 lines, ~115 tokens)
```text
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info
.python-version
# uv.lock



# Virtual environments
.venv

# Logs and databases
wandb
logs
agents

*.pch
nohup.out
*.onnx
beyondmimic_motions/
artifacts/
*.npz

src/mjlab_microduck/robot/microduck.bak/*
src/mjlab_microduck/robot/microduck_test/*
data/
*.pt

claude_experiments/

backup_onnx/


logdir/.claude/
logdir/
logdir/.claude/worktrees/

```

### File: `AGENTS.md` (268 lines, ~4466 tokens)
```md
# AGENTS.md

RL training environments for Microduck — a ~800 g, ~25 cm tall bipedal
robot with 14 Dynamixel XL330 servos — built on [mjlab](https://github.com/mujocolab/mjlab)
(MuJoCo Warp) with PPO (rsl_rl). Policies are trained here at 50 Hz, exported to
ONNX, and deployed by the runtime in the `pollen-robotics/microduck` repo on
the real robot. Sim2real transfer
is the whole point: every convention below exists because breaking it produced a
policy that worked in the viewer and failed on hardware.

## Commands

```bash
uv run list-envs                                    # live task registry
uv run train <TASK_ID> --env.scene.num-envs 4096    # train (add --hf-jobs for Hugging Face Jobs)
uv run train <TASK_ID> --env.scene.num-envs 64 --agent.max_iterations 5   # SMOKE TEST — always run first
uv run play <TASK_ID> --wandb-run-path <entity/project/run_id>
uv run scripts/export.py <TASK_ID> --wandb-run-path <...>   # → ONNX (bakes obs normalizer — mandatory path)
uv run publish --task <TASK_ID> --wandb-run-path <...> --checkpoint N --repo <user>/microduck-<name> --kind episodic --duration-s 4.0
                                                    # → HF Hub repo (policy.onnx + schema-2 manifest.json + README) the daemon loads via `robotctl policy add`
uv run scripts/infer_policy.py --walking out.onnx   # CPU MuJoCo deployment rehearsal (BAM M6 actuators as in training; --no-bam = XML PD)
uv run --with pytest pytest tests/
```

A 5-iteration smoke test at 64 envs catches ~95% of config errors for cents.
Never launch a long run without one.

## Repo map

- `src/mjlab_microduck/tasks/mdp.py` — ALL custom MDP functions (rewards, events,
  observations, commands, curricula). Add new functions here, grouped by task.
- `src/mjlab_microduck/tasks/microduck_*_env_cfg.py` — one cfg module per task
  family. `microduck_velocity_env_cfg.py` is the main walking recipe AND the
  shared base (robot, DR, obs, commands) other envs build on or mirror.
- `src/mjlab_microduck/tasks/__init__.py` — task registration (base + `-Backlash-` variants).
- `src/mjlab_microduck/tasks/backlash.py` — wraps any env cfg into its backlash twin.
- `src/mjlab_microduck/robot/microduck_constants.py` — robot cfgs, HOME frame, BAM actuator cfg.
- `src/mjlab_microduck/robot/microduck/` — MJCF exports from Onshape
  (onshape-to-robot, one `config_mjcf_*.json` per model) + scenes + `add_backlash.py`.
  Collision families: `walk` (feet only), `groundcontact` (curated floor set),
  `allcollisions` (every part; XL330 housings named `*_servo_collision` by
  `name_servo_collision_geoms` → VelStand's servo-impact sensor). Each has a
  `_backlash` twin generated by `add_backlash.py <xml> --backlash-deg 2.0`.
- `src/mjlab_microduck/actuator/friction_dr_bam.py` — BAM actuator + friction DR + backlash encoder.
- `src/mjlab_microduck/export.py` — the ONNX export (normalizer baked in); `scripts/export.py` wraps it.
- `src/mjlab_microduck/publish/` — `uv run publish`: schema-2 manifest builder + ONNX shape/smoke
  gate + Hub upload. Contract = `docs/policy-manifest.md` in the `microduck` repo; only
  constant-command episodic/perpetual policies are publishable (phase/posture-flag are the set's).
- `scripts/` — export wrapper, infer, sim2real comparison, wandb helpers.
- `tests/` — cfg-invariant and mdp-function regression tests (CPU, no GPU needed).

## Invariants — do not break these

- **Obs layout is 61D (actor) and shared across the whole policy family** so
  policies are hot-swappable in the runtime: 48 base proprioception +
  13D command block `[twist(3), head_pose(4), body_pose(6)]`, in that order.
  An env that doesn't use a command slot ZERO-PADS it (keep the obs term,
  sample tiny ranges) — never delete a slot.
- **Joint layout** (14 servos, ctrl idx = joint idx on walk/groundcontact
  models): 0–4 left leg (hip_yaw, hip_roll, hip_pitch, knee, ankle), 5–8
  neck/head (neck_pitch, head_pitch, head_yaw, head_roll), 9–13 right leg.
  On roller/backlash models, passive joints INTERLEAVE — never hardcode joint
  indices in mdp functions; use the `_servo_joint_ids` / `_servo_joint_pos`
  helpers in mdp.py (identity on plain models, correct everywhere else).
- **Unactuated joints are all named `passive_*`** (wheels, backlash hinges).
  Every actuator/obs/reward selector uses `^(?!passive_).*` — keep the prefix
  convention when adding joints, and new `passive_` regexes must not
  accidentally match backlash joints (`^passive_.*wheel`, not `^passive_.*`).
- **Actuators are BAM** (voltage-controlled XL330 model, friction computed by
  the actuator). Two consequences: any STANDALONE env cfg must register the
  `expand_bam_friction_fields` startup event, and joint-friction DR must scale
  the actuator's `friction_scale` — `dof_frictionloss` is zeroed under BAM, so
  randomizing it is a silent no-op.
- **Obs normalization is ON** → the normalizer must be baked into the ONNX.
  `scripts/export.py` does this; in-sim play hides the bug (it applies the
  normalizer anyway), so never hand-convert a checkpoint.
- **Policies are UNFILTERED** (no action low-pass in training). Don't add EMA
  filtering without a matched runtime flag and a transfer test — trained-with /
  deployed-without (either direction) breaks transfer.
- **Domain randomization must not accumulate across resets.** mjlab 1.3.0's
  `dr.*` ops with `operation="add"/"scale"` are natively non-accumulating (they
  re-read compile-time defaults); custom DR functions must restore-then-apply.
  An accumulating CoM randomizer once degraded every long run for months.
- If an obs is remapped to a sensor view (backlash encoder, bias), any tracking
  REWARD on the same quantity must measure the same view — otherwise the policy
  is punished for correcting what it sees.
- `-Backlash-` task variants must mirror their base task's robot model
  (walk / groundcontact / rollers) so backlash A/B comparisons are unconfounded.

## Building a new env — the workflow

1. **Pick the closest template** and build on it, don't start from scratch:
   locomotion → the velocity recipe; episodic trick ending in a pose →
   standup; commanded two-state → sitstand; dynamic maneuver → roulade
   (read its cfg docstring — it encodes a 5-run lesson arc). Building on
   `make_microduck_velocity*_env_cfg` keeps DR / obs / noise / delays in sync
   for free; if you build standalone from mjlab's base template, you must port
   the whole DR + obs-noise + NaN-guard stack yourself (grep for what velocity
   wires: `_safe` critic obs terms, `nan_state` termination with sensor_names,
   `expand_bam_friction_fields`, encoder bias, IMU misalignment).
2. **Verify physics assumptions in sim BEFORE training** — this is the single
   biggest time-saver:
   - A target/rest pose must be a stable equilibrium: hold its ctrl for 3 s
     from noisy inits and check TILT, not just height (a settle test that only
     records z reports fallen states as "resting fine").
   - Measure target heights off the actual robot in sim (e.g. trunk z under a
     standing policy), never carry them across model revisions. A 5 mm-wrong
     STAND_Z once turned the goal into an impossible target for days.
3. **Config conventions**: `ENABLE_*` toggles + tuned constants at the top of
   the cfg file; factory `make_..._env_cfg(play: bool, rough: bool)`; register
   in `tasks/__init__.py` (+ the `_BACKLASH_TASKS` table if applicable); own
   `RslRl...RunnerCfg` with a distinct `experiment_name`. Symmetry mirror-loss
   is available (61D table in `symmetry.py`) — OFF by default, never for
   asymmetric tasks.
4. **Write cfg tests** (see `tests/test_*_cfg.py`): joint indices resolve on
   the actual model, reward weights have the intended sign, gates open/closed
   where expected. These run on CPU and lock in the invariants.
5. **Smoke test** (64 envs, 5 iters): builds, steps NaN-free, obs is 61D,
   every reward term computes, ONNX exports.
6. Train, watch the log (below), and expect 2–5 iterations of reward-hacking
   whack-a-mole — that's normal, the lessons below shortcut most of it.

## Reward design — rules that were each learned the hard way

- **Sign convention (bit four envs):** mdp.py has two penalty styles. mjlab-base
  cost functions return ≥ 0 → negative weight. Self-negating microduck functions
  (`*_penalty`, `*_l1` returning ≤ 0) → POSITIVE weight. A negative weight on a
  self-negating penalty double-negates into a reward for the violation, and the
  policy will farm it (butt-hopping, crash-sits). **The infallible check: on
  every run, every `Episode_Reward/<penalty>` in wandb must be ≤ 0.**
- **RL optimizes the letter of the reward.** Every under-specified degree of
  freedom will be exploited (ballistic whip instead of a roll, shoulder-roll
  instead of sagittal, head-tripod instead of standing). Encode what counts as
  the maneuver in hard state-based gates (support contact, orientation-axis
  checks, latches), not in small penalty nudges.
- **No jackpots:** any "reach X" reward must be rate-limited or slewed.
  Arriving early at a goal state that then pays per-step is a jackpot that
  buys arbitrary violence. For commanded transitions, track a slewed internal
  target (constant-rate blend) — being ahead of the ramp pays zero, so slow IS
  the argmax. Speed-cap penalties alone integrate to a bounded cost and lose.
- **Never gate a positive reward on being in a bad state** (fallen, low) — the
  policy parks in the cheapest qualifying pose and farms it. Use
  potential-based shaping instead (pay Δprogress, e.g. Δcos(tilt): rising pays,
  holding pays zero, unfarmable). For rest tasks, audit each positive term
  against every stable flop (on back / face / side): if flopping keeps most of
  the stack, the policy will flop.
- **Episodic pose-landing tasks:** single fixed target from t=0 (Gaussian + L1
  on joints and height, generous std) + |a_z| impact penalty + two-layer
  upright — NOT keyframe/waypoint trajectories (the policy camps at
  waypoints). The path is what RL is supposed to discover.
- **Regularizers come in two kinds.** Motion-blockers (body_ang_vel,
  angular_momentum, pose std) penalize what a dynamic motion physically
  requires — keep them LOW for dynamic tasks. Smoothness (action_rate,
  joint_torque_rate) damps jitter without blocking slow big motions — safe to
  weight, but introduce it AFTER skill discovery (curriculum from ~0): any
  attempt-tax active while a hard skill is being explored makes "do nothing"
  win. Slow careful tasks (reaching) want heavier smoothness than walking.
- **Compare reward mass, not weights, when copying regularizers between envs.**
  PPO sees relative advantage: the same action_rate weight is 4× weaker under a
  4×-larger positive task stack.
- **Tracking Gaussian std:** ≈ the error you still care about, not the max
  error — too loose has no gradient at small errors. BUT before tightening,
  ask whether the error is escapable by the policy or inherent to the behavior
  you want (a 38%-of-body-mass head MUST oscillate while walking; a tight
  instantaneous head-tracking std taxed walking so hard the policy stood
  still). Price only the escapable part — e.g. L1 on a 1 s EMA charges DC bias
  and lets oscillation cancel.
- **Multiplicative composites beat additive sums at goal states:** when an
  additive stack has a compromise basin (80% of every term via a lean), a
  product of Gaussians collapses on any single deficient factor — but pick stds
  wide enough that the CURRENT policy scores visibly, or the gradient is
  invisible and nothing changes.
- **Joints parking on hard limits:** fix with a qpos-side limit-proximity
  penalty on the offending joints; the stock `dof_pos_limits` only fires in the
  last ~7.5% of range, and command-side penalties don't work (wide ctrlrange is
  intentional — low-kp servos need overshoot).

## Commands, observations, dead weights

- **A command input that is never non-zero has dead weights forever.** Every
  command slot keeps a small non-zero sampling range from step 0 (even at
  reward weight 0) so its input neurons stay alive for later curricula.
- **Zero-command behavior must be explicitly trained** (`zero_command_prob`-style
  exact-zero sampling): uniform sampling essentially never produces the all-zero
  command, which is exactly the deployment idle state.
- Rare-but-important command regions need explicit buckets — e.g. turn-in-place
  (`rel_turn_in_place_envs`): independent uniform sampling made spinning ~2% of
  experience and it never trained.

## Curricula

- Steps are env steps: `iteration × 24` (`NUM_STEPS_PER_ENV = 24`).
- Use the proven split: `microduck_mdp.reward_weight` for weight schedules, a
  dedicated params-curriculum for command/event ranges. `mdp.reward_weight` is
  a step function, not an interpolation — discretize ramps into stages.
- Mutate term cfgs via the managers (`env.event_manager.get_term_cfg(...)`),
  never `env.cfg.events[...]` — managers deepcopy their cfg at init, so writes
  to `env.cfg` are silent no-ops (this also bites eval scripts that force
  spawn states).
- **Phase-align every stage with what the policy has actually learned**: don't
  harden spawn mixes before the current slice consolidates; don't introduce
  taxes before the skill exists. When a wandb metric steps DOWN exactly at
  curriculum stage boundaries, the pacing is wrong — stretch stages or move
  the introduction later, never earlier.
- Reverse-curriculum spawns (starting episodes partway through the maneuver,
  including nearly-done) are the reliable fix for "learns the start, never the
  last mile" — the frontier otherwise gets no on-policy data.

## Training ops & reading a run

- wandb project `mjlab_microduck`; logs in `logs/<experiment_name>/`; resume
  with `--agent.load-checkpoint model_XXXX.pt --agent.resume True`.
- **Warm start ≠ resume.** mjlab's runner stores `common_step_counter` in the
  checkpoint and restores it (plus the iteration) on load, so loading another
  task's checkpoint jumps every step-based curriculum to its final stage in
  iteration 1. Prefix `MICRODUCK_WARM_START=1` (mdp.py Patch 5, forwarded to HF
  Jobs) to restart both at 0 while keeping weights/normalizer/optimizer. Also
  collapse the inherited curricula of the SOURCE task to their final stage in
  the target cfg (see `_collapse_curricula_to_final` in velstand) — the loaded
  policy was trained under those conditions. Only warm-start across tasks with
  compatible normalizers (the stand expert's twist std is 0.005: never seed a
  walking env from it).
- Deployed-policy provenance: Hub ONNX files carry `run_path=None`; find the run
  by exact last-layer weight match against wandb checkpoints (2026-09: walk =
  441tzs6d@3750, stand = 69u48n8l@9750).
- Watch per-iteration: mean reward rising AND episode length behaving as the
  task demands; every penalty term ≤ 0; the MAIN task term actually growing
  (total reward can rise purely on regularizers while the trick never happens).
  `Episode_Reward/<term>` logs the WEIGHTED value — a term at weight 0 reads 0
  regardless of behavior, so interpret against the weight schedule.
- Budgets: simple episodic tricks ≈ 1000 iters at 4096 envs; gaits and
  curriculum-heavy recovery need 4000–6000.
- **Measure before theorizing.** When a run "fails", run a headless eval of the
  actual checkpoint (per-spawn-type batteries, end-state clusters, angular-rate
  profiles) before changing rewards: past "failures" turned out to be early
  checkpoints, a success criterion splitting one behavior cluster in half, and
  a pay cap fighting measured physics. Sim metrics can pass while the video
  fails the human eye — watch the video AND check which geom/axis touches.
- Report what rollouts actually show ("rolls but face-plants 1 in 3"), not
  "it works!". The user decides when it's good enough.

## Sim2real footguns (cost real debugging weeks)

- A fresh `uv sync` is the ground truth (HF Jobs run one): anything that only
  works via manually-installed local packages will die remotely. Keep
  `pyproject.toml` honest.
- **Wheels are per-architecture.** On linux-`aarch64` (DGX Spark / GB10) PyPI's
  torch wheel is CPU-ONLY (`2.9.1+cpu`, `torch.version.cuda is None`), so
  `torch.cuda.device_count() == 0` and mjlab's `select_gpus()` indexes an empty
  list → `IndexError` before iteration 0. `[tool.uv.sources]` routes torch to
  the cu129 index for `aarch64` only (cu129 matches the CUDA toolkit warp
  bundles; x86_64/HF Jobs stay on PyPI). Two silent break points, both locked
  by `tests/test_aarch64_cuda_torch.py`: torch must stay a DIRECT dependency
  (uv applies `[tool.uv.sources]` to direct deps only — deleting the
  redundant-looking `torch==` pin makes the routing a no-op), and the pin must
  stay `==`, since the CUDA index carries newer builds than PyPI (a `>=`
  silently dragged torch 2.9.1 → 2.13.0).
- Physics-aligned limits: a 25 cm robot tumbles at 3.5–5.5 rad/s NATURALLY —
  don't impose human-scale speed intuitions via caps; put anti-violence
  pressure on impacts and thrash (|a_z|, action_rate, support gates), not on
  rotation speed.
- IMU DR is zero-centered — it trains tolerance to misalignment magnitude, and
  CANNOT compensate a systematic mounting bias (that's a runtime calibration).
- Real deployments hot-swap ONNX policies (walk / stand / trick) with a shared
  obs contract — rehearse in `scripts/infer_policy.py` before touching the
  robot, with the correct command-slot writes (a posture flag lives in the
  twist vx slot; feeding all-zeros means "stand", which looks like "policy
  ignores the button").

```

### File: `CLAUDE.md` (1 lines, ~3 tokens)
```md
@AGENTS.md

```

### File: `LICENSE` (202 lines, ~2888 tokens)
```text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this
      License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2026 Pollen Robotics

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

```

### File: `README.md` (261 lines, ~3348 tokens)
```md
# Microduck RL

<img width="2215" height="884" alt="image" src="https://github.com/user-attachments/assets/5db7cc83-b3ce-4f7c-83f0-0572a63baed7" />


RL training environments for [Microduck](https://github.com/pollen-robotics/microduck) —
a ~800 g, ~25 cm tall bipedal robot — built on
[mjlab](https://github.com/mujocolab/mjlab) (MuJoCo Warp) with PPO.
Policies are trained here at 50 Hz, exported to ONNX, and deployed on the real
robot by the runtime in [pollen-robotics/microduck](https://github.com/pollen-robotics/microduck).

<!-- HERO VIDEO — real robot montage: walking, standup, roulade, roller skating.
     Keep it short (~30 s) and real-robot-first: this is the "why should I care" shot. -->

https://github.com/user-attachments/assets/50c3d537-8db2-4005-9d9c-3472faeec4d0

The repo encodes the full sim2real recipe: [BAM](https://github.com/Rhoban/bam)
actuator physics, domain randomization, backlash simulation, and the
reward-design lessons that made it work
(see [AGENTS.md](AGENTS.md) for the distilled playbook).

## Quickstart

Requires a CUDA GPU (training runs through MuJoCo Warp) and [uv](https://docs.astral.sh/uv/).

> **On ARM boxes (DGX Spark / GB10, Jetson):** `uv sync` pulls ~2 GB of CUDA
> wheels on first run and uv's default 30 s HTTP timeout can abort mid-download.
> Export `UV_HTTP_TIMEOUT=600` for the first sync. 

```bash
git clone https://github.com/pollen-robotics/microduck_rl
cd microduck_rl

# train the walking policy (uses your GPU; ~1-2 h for a usable gait at 4096 envs)
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096

# watch a trained policy in the viewer
uv run play Mjlab-Velocity-Flat-MicroDuck --wandb-run-path <entity/project/run_id>

# export to ONNX for deployment
uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck --wandb-run-path <...>
uv run publish --onnx output.onnx --repo <user>/microduck-<name> --kind episodic --duration-s 4.0   # share it (see "Publishing a policy")

# drive the exported policy in CPU MuJoCo with the keyboard
uv run scripts/infer_policy.py --walking output.onnx
```

Resume from a checkpoint:

```bash
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096 \
    --agent.run-name resume --agent.load-checkpoint model_29999.pt --agent.resume True
```

No GPU? Add `--hf-jobs` to any train command to run it on Hugging Face Jobs
instead of locally (see [scripts/hf/README.md](scripts/hf/README.md)).

## Tasks

`uv run list-envs` prints the live registry. Flat/Rough variants exist where noted.

<!-- SHOWCASE GRID — one short GIF per task family (sim or real), 3 per row.
     Priority order if you only record a few: Velocity, VelStand (fall+recover),
     Roulade, SitStand, Rollers/Swizzle, BallKick. -->

| Task id | Terrain | Description |
|---|---|---|
| `Mjlab-Velocity-{Flat,Rough}-MicroDuck` | flat/rough | **The main task**: walking with velocity commands + head-pose commands |
| `Mjlab-VelStand-{Flat,Rough}-MicroDuck` | flat/rough | Walking + fall recovery in one policy |
| `Mjlab-StandUp-{Flat,Rough}-MicroDuck` | flat/rough | Stand up from face-down/face-up/sitting, then hold the stand + body-pose control |
| `Mjlab-SitStand-{Flat,Rough}-MicroDuck` | flat/rough | Commanded sit ↔ stand in one policy, gently, head commandable |
| `Mjlab-GroundPick-{Flat,Rough}-MicroDuck` | flat/rough | Crouch and touch the ground with the mouth tip, return to stand |
| `Mjlab-BallKick-Flat-MicroDuck` | flat | Kick a 70 mm / 15 g ball forward (actor is ball-blind) |
| `Mjlab-Roulade-Flat-MicroDuck` | flat | Forward roll over the head, land back on the feet |
| `Mjlab-Velocity-Flat-MicroDuck-Rollers` | flat | Roller-skate velocity tracking (passive wheels under the feet) |
| `Mjlab-Velocity-Swizzle-MicroDuck` | flat | Classic symmetric swizzle skating |
| `Mjlab-RollerCrouch-Flat-MicroDuck` | flat | Crouch while gliding on rollers |
| `Mjlab-RollerSlope-Flat-MicroDuck` | slope | Glide down slopes on rollers |
| `Mjlab-RollerStandUp-Flat-MicroDuck` | flat | Stand up from the ground onto the wheels |
| `Mjlab-Spin-Flat-MicroDuck` | flat | Fast spin in place on rollers |

At deployment the runtime hot-swaps these policies (walk / recover / trick)
behind a shared 61-dimensional observation contract, so any of them can take
over the robot at any moment. `scripts/infer_policy.py` rehearses exactly that:

```bash
uv run scripts/infer_policy.py --walking walk.onnx --standing stand.onnx \
    --sitstand sitstand.onnx --roulade roulade.onnx --new-cmd-obs
```

Keyboard-driven (velocity commands, `G` ground pick, `Y` sit/stand, `R` roulade,
`K`/`L` kicks); `--debug`, `--save-csv`, `--record` support sim2real comparisons.
The servos are simulated with the same BAM M6 XL330 model the policies are
trained against (voltage control + load-dependent friction, via
`bam.mujoco.MujocoController`); `--vin` / `--vin-drop-gain` / `--kp-fw` pin the
training DR ranges to one value, `--no-bam` falls back to the XML PD actuators.

### Backlash variants

Every main task has a **Backlash** twin that trains on a model with ±1° of gear
play (2° total) in series with each of the 14 servo joints: insert `-Backlash`
before `MicroDuck` in the task id, e.g. `Mjlab-Velocity-Flat-Backlash-MicroDuck`.

The backlash is modeled properly for sim2real: each servo gets an unactuated
`passive_<joint>_backlash` hinge, and because the real encoder sits on the
output side of the play, both the firmware PD emulation
(`BacklashEncoderBamActuator`) and the `joint_pos`/`joint_vel` observations
read *through* the backlash (`qpos[servo] + qpos[backlash]`). Observation and
action dims are unchanged, so ONNX export and the runtime need no changes.
See `src/mjlab_microduck/tasks/backlash.py`.

## Actuator model

All tasks use the [BAM](https://github.com/Rhoban/bam) M6 actuator model for
the Dynamixel XL330 (voltage control law, back-EMF, Coulomb/Stribeck/load-dependent
friction), with per-env domain randomization on battery voltage, voltage sag
under load, command delay, and friction magnitude
(`FrictionDRBamActuator` in `src/mjlab_microduck/actuator/`).

At this scale — tiny servos driving a ~800 g biped — actuator fidelity is most
of the sim2real gap, which is why the actuator is modeled down to its voltage
control law instead of an ideal PD.

## Robot models

MJCF models live in `src/mjlab_microduck/robot/microduck/` and are exported
from Onshape with [onshape-to-robot](https://github.com/Rhoban/onshape-to-robot),
one `config_mjcf_*.json` per model:

| XML | Used by |
|---|---|
| `robot_walk.xml` | Velocity (stripped trunk/head contacts — falling is cheap) |
| `robot_groundcontact.xml` | VelStand, StandUp, SitStand, GroundPick, BallKick, Roulade (curated collision set for the parts that touch the floor — body can physically lie on the ground; formerly `robot_allcollisions.xml`) |
| `robot_groundcontact_rollers.xml` | Roller tasks (passive wheels) |
| `robot_allcollisions.xml` | True full-collision model — every part has a collision geom. No task uses it yet |
| `robot_*_backlash.xml` | Backlash task variants (generated by `add_backlash.py`) |

`scene*.xml` files wrap the robots with a floor + keyframes (STAND/SIT/FOLD)
for quick viewing and for `infer_policy.py`.

<!-- IMAGE — side-by-side render: walk model vs rollers model (or a collision-geom
     visualization). One image here makes the model-variant story instant. -->

## Project structure

```
src/mjlab_microduck/
├── robot/
│   ├── microduck/                    # MJCF exports, export configs, scenes, add_backlash.py
│   └── microduck_constants.py        # robot cfgs, HOME frame, BAM actuator cfg
├── actuator/friction_dr_bam.py       # BAM + friction DR + backlash encoder feedback
├── tasks/
│   ├── __init__.py                   # task registration (base + backlash variants)
│   ├── mdp.py                        # rewards, events, observations, custom classes
│   ├── backlash.py                   # make_backlash_variant() env-cfg wrapper
│   └── microduck_*_env_cfg.py        # one cfg module per task family
├── train_cli.py                      # `train` script (identical to mjlab's)
├── train_hook.py                     # intercepts `train ... --hf-jobs`
└── hf_jobs.py                        # Hugging Face Jobs submission
```

Conventions worth knowing:

- The observation layout is shared across every policy (61-dim actor obs:
  48 proprioception + commands `[twist(3), head_pose(4), body_pose(6)]`), which
  is what makes runtime policy hot-swapping possible. Envs that don't use a
  command slot zero-pad it rather than dropping it.
- Unactuated joints are all named `passive_*` (roller wheels, backlash
  hinges); actuators, joint observations and pose rewards select servo joints
  with `^(?!passive_).*`.
- Domain-randomization toggles are `ENABLE_*` booleans at the top of each
  env cfg file.
- Joint layout (14 servos): 0–4 left leg (hip_yaw, hip_roll, hip_pitch, knee,
  ankle), 5–8 neck/head (neck_pitch, head_pitch, head_yaw, head_roll),
  9–13 right leg.
- The exporter bakes the observation normalizer into the ONNX graph — always
  deploy ONNX produced by `scripts/export.py`, never a hand-converted
  checkpoint, or the policy sees unnormalized observations at runtime.

[AGENTS.md](AGENTS.md) documents the env-building workflow and the reward-design
rules learned across the project (also aimed at AI coding agents working in
this repo).

## Publishing a policy

`uv run publish` puts a policy on the Hugging Face Hub in the shape the robot's
daemon loads: one `policy.onnx` with the observation normalizer baked in, a
`manifest.json` following schema 2 of the
[microduck policy manifest](https://github.com/pollen-robotics/microduck/blob/main/docs/policy-manifest.md),
and a README saying how to run it. Anyone with a microduck can then install it
with one command, no daemon release needed.

```bash
# From a wandb run — exports through the one safe path, then uploads
uv run publish --task Mjlab-PoliteBow-Flat-MicroDuck \
    --wandb-run-path <entity/project/run_id> --checkpoint 3000 \
    --repo <user>/microduck-polite-bow --kind episodic --duration-s 4.0 \
    --description "Bows from a two-foot stand and comes back up."

# From an ONNX you already exported (validated, not re-exported)
uv run publish --onnx output.onnx --repo <user>/microduck-flamingo \
    --kind perpetual --unwind-s 1.5 --twist-help "[flag, side, 0]"

# A new gait for a slot
uv run publish --onnx output.onnx --repo <user>/microduck-my-walk --kind perpetual --slot walk

# See what would be uploaded without touching the Hub
uv run publish --onnx output.onnx --repo <user>/microduck-bow --kind episodic --duration-s 4.0 --dry-run
```

Then on a robot:

```bash
sudo robotctl policy add polite-bow <user>/microduck-polite-bow   # episodic: length comes from the manifest
sudo robotctl policy add flamingo <user>/microduck-flamingo --hold 5   # held pose: you pick how long
sudo robotctl policy load walk <user>/microduck-my-walk                # gait: into the walk slot
robotctl robot do polite-bow
```

What `--kind` means, and what each needs:

- **episodic** — runs for `--duration-s` and returns itself to a standing pose
  (kicks, roulade, a bow). Add `--chain` if holding the button should repeat it.
- **perpetual** — runs until told otherwise. Two shapes:
  - a **gait** (a new walk or stand): add `--slot walk` (or `stand`) and
    nothing else; the owner installs it with `robotctl policy load walk <repo>`.
  - a **held pose** (the flamingo): give `--unwind-s`, how long the daemon
    drives the idle twist (`--idle`, zeros by default) before handing back to
    the gait, so the robot is not let go of on one foot. The owner runs it as a
    one-shot with `policy add ... --hold <seconds>`.

Before anything is uploaded, `publish` checks the graph is `[1,61] -> [1,14]`
(a 51-D legacy policy is refused with a message), runs it on plausible inputs
and refuses NaNs or a constant output, fills the `training` block from git and
wandb (task, commit, branch, dirty flag, run, checkpoint), and refuses to
overwrite an existing `.onnx` in the repo without `--force`. Repos are created
private; `--no-private` for public, `--tag v1` to tag the revision.

Only constant-command policies are publishable this way. Phase-driven moves
(the ground pick) and the posture-flag sit↔stand are driven by the daemon
itself and live in the official set, `pollen-robotics/microduck-policies`.

## Tests

```bash
uv run --with pytest pytest tests/
```

CPU-only config-invariant and reward-function regression tests — they lock in
joint-index mappings, reward sign conventions, and NaN guards.

## Related projects

- [microduck](https://github.com/pollen-robotics/microduck) — the Microduck project home, including the onboard runtime that runs the exported policies
- [mjlab](https://github.com/mujocolab/mjlab) — the training framework (MuJoCo Warp + rsl_rl)
- [BAM](https://github.com/Rhoban/bam) — better actuator models, by Rhoban

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
3D model files are licensed under Creative Commons BY-SA-NC.

```

### File: `docs/roller_standup_policy_summary.md` (195 lines, ~3098 tokens)
```md
# Policy `roller_standup` — se relever sur rollers

**But** : le microduck (sur rollers) part du sol — à plat ventre ou à plat dos — et se remet **debout sur ses roues**, puis **tient** la station.

- **Tâche** : `Mjlab-RollerStandUp-Flat-MicroDuck`
- **Fichier** : `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`
- **Base** : dérivée de l'env roller (`velocity_rollers`) → même robot, même physique/DR, **même observation 61D** (interchangeable au runtime, chargeable via `--new-cmd-obs`).
- **Spec** : `docs/superpowers/specs/2026-08-04-roller-standup-design.md`
- **Politique aveugle** : pas de scan de terrain ; proprioception + `projected_gravity`.

## Hauteurs (mesurées, pas devinées)

| pose | modèle pieds | modèle rollers |
|---|---|---|
| debout | 0.1172 → `STAND_Z=0.115` sous charge | 0.1407 → **`ROLLER_STAND_Z=0.138`** |
| à plat ventre (repos) | 0.075 | 0.075 |
| à plat dos (repos) | 0.048 | 0.048 |

Les hauteurs de repos au sol sont identiques aux deux modèles : c'est la coque du tronc qui touche, pas les pieds.

## ⚠️ Indices de joints — les roues sont INTERCALÉES

```
0-4   jambe gauche      5-6   roues gauches
7-10  cou / tête       11-15  jambe droite      16-17  roues droites
```
`_LEG_JOINTS = [0-4, 11-15]`. Les indices du `standup` (`[0-4, 9-13]`) valent pour le modèle **sans** roues et pointeraient sur des roues ici. Verrouillé par `tests/test_roller_standup_cfg.py::test_joint_indices_match_actual_roller_model`.

## Reset — départ au sol

`set_random_ground_state` : ventre (`prone_z` 0.076–0.09, plancher relevé car le ventre ne décolle du sol qu'à 0.0752) / dos / **déjà debout** (`standing_z` 0.134–0.144), ± 10° de bruit en pitch/roll. Pas de bucket « assis ». Le bucket « debout » est nécessaire : sans lui la policy monte mais ne tient pas.

**Curriculum `ground_state_mix`** (easy → hard, le dos en dernier) :

| iter | debout | ventre | dos |
|---|---|---|---|
| 0 | 0.50 | 0.50 | 0.00 |
| 600 | 0.35 | 0.45 | 0.20 |
| 1500 | 0.25 | 0.40 | 0.35 |
| 2500 | 0.20 | 0.40 | 0.40 |

## Récompenses

Dix termes repris du `standup` avec leurs poids déjà réglés : `pose_stand_legs` (+8), `pose_stand_l1` (+5), `height_stand` (+4, std 0.04), `height_stand_sharp` (+4, std 0.015), `height_stand_l1` (+30), `com_upward_velocity` (+3), `gentle_rise` (−0.02), `upright_linear` (+6), `upright_sharp` (+6), `standing_composite` (+15). Plus `joint_torque_rate_l2` (−2e-3), l'anti-jitter qui n'empêche pas le retournement.

Régularisateurs hérités : `body_ang_vel` **−0.05** (bloqueur de mouvement, à garder LÉGER), `angular_momentum` −0.02, `action_rate_l2` (rampe −0.4 → −1.0, **pas** le −2.0 du roller), `neck_action_rate_l2` −0.5, `neck_joint_pos_l2` −0.5 (tête droite), `joint_torques_l2` −1e-3, `action_over_limit` −0.5, `self_collisions` −1.0.

Retirées : toutes les récompenses de patinage, plus `feet_flat` (les lames ne sont pas à plat pendant la montée) et `hip_roll_neutral` (se relever demande d'écarter les jambes).

## ⚠️ Le point dur : les roues roulent

Aucune adhérence longitudinale pour pousser sur le sol. Le **curriculum de friction de roulement est INVERSÉ** (l'env roller la fait monter, ici elle descend) :

| iter | frictionloss | |
|---|---|---|
| 0 | 0.05 | roues quasi bloquées → se relève comme avec des pieds |
| 1000 | 0.02 | |
| 2000 | 0.008 | |
| 3000 | 0.003 | |
| 4000 | 0.0015 | la vraie valeur du roulement |

**Surveiller `Episode_Reward/standing_composite` aux paliers.** S'il s'écroule, le geste « pieds adhérents » ne transfère pas aux roues libres → il faudra guider une technique de patineur (appui genou intermédiaire, un patin à la fois). C'est un résultat, pas un échec.

**Surveiller AUSSI la dérive horizontale du robot en play**, à chaque palier de friction. `standing_composite` ne voit ni `root_link_pos_w[:2]` ni la vitesse horizontale : une policy qui se relève en glissant loin de son point de départ collecte exactement le même score qu'une qui se relève et s'arrête. Tant que cette dérive n'a pas été mesurée visuellement, le résultat du curriculum de friction (la question même que cet env existe pour trancher) n'est pas fiable.

**Sim2real** : seuls les checkpoints d'après iter 4000 sont candidats au déploiement. Avant, la policy s'appuie sur une friction qui n'existe pas sur le vrai robot.

## Commande

Slot `twist` neutralisé : `lin_vel_x`/`lin_vel_y` ± 0.01, `ang_vel_z` **± 0.05** (5× plus large — même
choix que le `standup`). Slots `head_pose` / `body_pose` **zero-paddés** (convention roller). Déploiement visé : en `--standing` face à la policy roller en `--walking`, avec la bascule automatique sur la magnitude de la commande (`infer_policy.py:262`, seuil 0.05) ; le slot twist y est laissé à zéro (`infer_policy.py:239`).

**Réserve** : `infer_policy.py` est le script de sim/clavier local. Le runtime robot est le binaire Rust `microduck_runtime`, absent du repo — il n'est pas vérifié qu'il expose un équivalent `--standing`. Le doc de passation du crouch ne liste que `--model`, `--ground-pick`, `--fold-policy`. À confirmer.

## Terminaisons

`fell_over` **supprimée** (le robot démarre tombé). `nan_state` héritée. `nan_policy="sanitize"` sur les obs actor/critic.

## Réseau / PPO

Actor et critic `(512, 256, 128)` elu, `obs_normalization=True`. PPO `lr=1e-3` adaptive, `desired_kl=0.01`, `gamma=0.99`, `lam=0.95`, `num_steps_per_env=24`, épisode 6 s, `max_iterations=15000`. **Symétrie OFF** (`SYMMETRY_CFG` est câblé pour le layout 51D).

## Commandes

```bash
uv run train Mjlab-RollerStandUp-Flat-MicroDuck --env.scene.num-envs 4096 --agent.max_iterations 15000
uv run scripts/play_latest.py        # alias md-play
uv run scripts/export_latest.py      # alias md-export
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```

### ⚠️ Voir les départs sur le dos au play

Un play ne montre **jamais** de départ sur le dos par défaut : l'env de play est
reconstruit à neuf, donc `common_step_counter` repart à 0 et le curriculum applique son
palier 0, où `face_up_prob = 0`. On ne voit que 50 % ventre / 50 % debout, quelle que soit
la maturité du checkpoint chargé. Or le dos est le cas le plus dur, celui qu'on veut
justement inspecter.

`STANDUP_PLAY_FACE_UP` force le mélange (même motif que `SLOPE_PLAY_DIFFICULTY` dans
`roller_slope`), **uniquement sur le chemin `play=True`** — l'entraînement et son
curriculum easy → hard sont intouchés :

```bash
STANDUP_PLAY_FACE_UP=1.0 md-play    # 100 % de départs sur le dos
STANDUP_PLAY_FACE_UP=0.4 md-play    # le mélange du dernier palier du curriculum
STANDUP_PLAY_FACE_UP=none md-play   # défaut (palier 0, pas de dos)
```

Le reste (`1 - face_up`) est réparti ventre:debout dans le rapport 2:1 du dernier palier,
si bien que `0.4` reproduit exactement le mélange de fin d'entraînement (0.40 / 0.20 / 0.40).

## 🔧 Correction anti-violence (après premier test robot)

**Symptômes** sur un checkpoint 4000+ : mouvements très brusques, la tête tape le sol,
échec du relevé depuis le dos sur le robot. **Présents en simu aussi** → ce n'était donc
ni du sim2real, ni un checkpoint trop jeune, mais la conception des récompenses.

**Root cause : `gentle_rise` récompensait la violence.** `trunk_vertical_accel_penalty`
renvoie déjà `-|a_z|` (`mdp.py:2171`) ; multiplié par le poids **−0.02** hérité du
`standup`, ça faisait un double négatif, donc `+0.02·|a_z|` — **plus le tronc accélérait
brutalement, plus la policy était payée**. Confirmé par le log : `Episode_Reward/gentle_rise
= +0.0118` sur le run `vweolw91`, seul terme de pénalité loggé positif.

`mdp.py` mélange deux conventions de signe, et c'est le piège :

| terme | la fonction renvoie | poids correct |
|---|---|---|
| `height_stand_l1`, `pose_stand_l1`, `gentle_rise` | `-abs(...)`, déjà négatif | **positif** |
| `joint_torques_l2`, `joint_torque_rate_l2`, `action_rate_l2`, `body_impact_cost` | magnitude positive | **négatif** |

Verrouillé par `test_already_negative_penalties_use_positive_weights`.

⚠️ **Le `standup` du marcheur a exactement le même bug** (même fonction, même poids −0.02).
Ça explique la série de tentatives d'amortissement infructueuses documentées dans ses
commentaires (« *violent / shaky / overshoot-tip-repeat on the real robot* ») : elles
combattaient un terme qui poussait activement dans l'autre sens. **Non corrigé ici** — c'est
un autre env, à trancher séparément.

**Problème structurel associé.** À convergence les récompenses de tâche totalisaient **≈ +41.6**
saturées à 95–99 %, contre **≈ −1.2** pour tous les amortisseurs réunis — dont
`joint_torque_rate_l2` à **−0.0002/pas** et `joint_torques_l2` à **−0.0001/pas**, soit rien.
Rapport ~35:1 : aucune raison d'être doux.

**État actuel des corrections :**

| | avant | maintenant | pourquoi |
|---|---|---|---|
| `gentle_rise` | −0.02 (récompense) | **+0.02** (pénalité) | signe corrigé ; magnitude gardée PETITE exprès — `\|a_z\|` est forcément élevé pendant un retournement, un gros poids serait un bloqueur de mouvement |
| `joint_torque_rate_l2` | −2e-3 | **−0.2** | le levier SÛR : pénalise la variation de couple, pas le mouvement |
| `head_impact_penalty` | absent | **toujours absent** | essayé à −1.0, a gelé la policy — voir ci-dessous |

### ⚠️ La pénalité d'impact tête a gelé la policy — ne pas la remettre telle quelle

Tentative avec les valeurs de `velstand` (`body_impact_cost`, sous-arbre `neck`, −1.0,
seuil 2.0) : **la policy a convergé vers rester couchée, inerte.** Mesuré (run `d8rnko6p`) :

| terme | avant (violent) | avec head_impact (gelé) |
|---|---|---|
| `standing_composite` | +14.32 | **+3.26** |
| `upright_sharp` | +5.76 | +1.06 |
| `head_impact_penalty` | — | **−1.01** ← plus gros terme négatif |
| `joint_torque_rate_l2` | −0.0002 | −0.255 (donc **pas** le coupable) |

L'erreur de raisonnement : croire qu'une pénalité « ciblée » ne bride pas le mouvement.
**Faux ici — pour se relever du dos, ce robot pivote sur sa tête et ses épaules.** La tête
est le point d'appui du retournement, pas un dégât collatéral ; la pénaliser bloque le seul
mécanisme disponible, et le dos était déjà le cas qui échouait.

**L'optimum paresseux qui rend ce gel possible** : `pose_stand_legs` restait à **+7.72 sur 8**
alors que le robot était allongé — les jambes sont à HOME en position couchée, donc cette
récompense est encaissée quasi gratuitement. C'est `height_stand_l1` (poids +30) qui doit
rendre « rester au sol » net négatif ; il ne faut pas l'affaiblir.

**Hypothèse en cours de test** : taper la tête était un *symptôme* de la violence (le bug de
signe payait la brutalité, et une montée brutale finit sur la tête), pas un défaut séparé.
Si le slam revient maintenant que le signe est corrigé, la reprise doit être une pénalité
**gatée en hauteur** (comme `upright_sharp` l'est), qui épargne la phase de retournement au sol.

**Leçon de méthode** : les trois corrections ont été appliquées d'un coup, donc le gel n'a pas
pu être attribué avec certitude — seul le suspect le plus probable a pu être désigné. Une
correction à la fois, à l'avenir.

**Recalibrage si c'est encore violent** : `|Δτ|²` vaut ~0.1 à convergence, donc la
contribution de `joint_torque_rate_l2` ≈ `0.1 × |poids|`. Monter **ce** terme, **pas**
`body_ang_vel` (−0.05) ni `action_rate_l2` (rampe → −1.0) : ceux-là sont des bloqueurs de
mouvement et le `standup` documente qu'à −0.15 et −1.2 respectivement, ils **gelaient** le
relevé depuis le dos. Si au contraire le dos cesse de fonctionner, **baisser**
`joint_torque_rate_l2` en premier.

## Hors périmètre

Intégrer le relevé dans la policy de roulage (recette `velstand`) ; buckets de départ sur le côté ; variante rough ; pénalités d'impact tronc/tête.

Aucune récompense ne pénalise la vitesse horizontale du tronc (`root_link_lin_vel_w[:, :2]`) : « se relever en roulant loin » est un résultat non pénalisé et qui score à plein. Décision volontaire (pas un oubli) : une récompense d'immobilité qui ne serait pas gatée en hauteur pénaliserait aussi la translation que le relevé depuis le sol exige physiquement — le mode d'échec « bloqueur de mouvement » que le `standup` documente. Candidat si le problème se confirme : une immobilité gatée en hauteur (proche de `ROLLER_STAND_Z` seulement).

```

### File: `docs/superpowers/plans/2026-07-17-roller-crouch-glide.md` (899 lines, ~9311 tokens)
```md
# Roller Crouch-Glide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajouter un geste « s'accroupir en glissant puis se relever » déclenché au bouton A, sans modifier le runtime Rust, en entraînant une policy mjlab chargée dans le slot `--ground-pick`.

**Architecture:** Nouvelle tâche mjlab entraînée sur le robot rollers, pilotée par la commande de phase `GroundPickPhaseCommand` (celle qu'envoie le slot ground-pick du runtime). Une nouvelle reward suit une cible de hauteur du tronc « en trapèze » (haut → bas → palier 1 s → haut) le long de la phase. Le même layout d'obs 61D que la policy roller → interchangeable au runtime. Export ONNX, chargé via `--ground-pick`.

**Tech Stack:** Python, PyTorch, mjlab 1.3.0, MuJoCo, uv, ONNX. Runtime cible : `apirrone/microduck_runtime` (Rust, binaire — NON modifié).

## Global Constraints

- **Aucune modification du runtime Rust.** Le geste réutilise le slot `--ground-pick` existant (bouton A, one-shot).
- **Layout d'obs unifié 61D** obligatoire (`--new-cmd-obs`) : `[twist(3), head(4), body(6)]`, head/body zero-paddés. Toute nouvelle policy DOIT conserver ce layout.
- **14 joints actifs** (roues passives exclues via `SceneEntityCfg("robot", joint_names=(r"^(?!passive_).*",))`), `action.scale = 1.0`, `kp_fw = 200`.
- **Parité entraînement/déploiement (sim2real) :** au déploiement, forcer `--ground-pick-kp-ratio 1.0` (défaut 0.6), `--ground-pick-action-scale` = action_scale runtime, `--ground-pick-period 5.0`.
- **Phase encoding (imposé par le runtime) :** `command = [cos(2π·φ), sin(2π·φ), 0]`, période 4 s. Palier de glisse = 1 s → `hold_lo=0.375`, `hold_hi=0.625`.
- **Commits simples** (pas de `Co-Authored-By`).
- Lancer les tests via `uv run --with pytest pytest` (pas de dépendance pytest ajoutée au projet).
- Spec de référence : `docs/superpowers/specs/2026-07-17-roller-crouch-glide-design.md`.

---

## File Structure

| Fichier | Responsabilité |
|---|---|
| `src/mjlab_microduck/tasks/mdp.py` | **Modifier.** Ajouter 3 fonctions : `crouch_height_target` (pure), `crouch_glide_reward_from_values` (pure), `crouch_glide_height_by_phase` (wrapper env) et `forward_speed_reward`. |
| `tests/test_crouch_glide.py` | **Créer.** Tests unitaires des fonctions pures. |
| `src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py` | **Créer.** L'env (hybride roller + phase) + `MicroduckRollerCrouchRlCfg`. |
| `src/mjlab_microduck/tasks/__init__.py` | **Modifier.** Importer + enregistrer `Mjlab-RollerCrouch-Flat-MicroDuck`. |
| `tests/test_roller_crouch_cfg.py` | **Créer.** Smoke test : l'env se construit avec la bonne commande/rewards. |

---

## Task 1: Cible de hauteur « en trapèze » (fonction pure)

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (ajouter la fonction, après `com_height_target` vers la ligne 737)
- Test: `tests/test_crouch_glide.py`

**Interfaces:**
- Produces: `crouch_height_target(phase: torch.Tensor, height_low: float, height_high: float, hold_lo: float = 0.375, hold_hi: float = 0.625) -> torch.Tensor` — prend la phase (B,) ∈ [0,1) et retourne la hauteur-cible (B,).

- [ ] **Step 1: Écrire le test qui échoue**

Créer `tests/test_crouch_glide.py` :

```python
import math
import torch
from mjlab_microduck.tasks import mdp


def test_crouch_height_target_endpoints_are_high():
    # phase 0 (début) et phase ~1 (fin) → hauteur haute (debout)
    phase = torch.tensor([0.0, 0.999])
    t = mdp.crouch_height_target(phase, height_low=0.075, height_high=0.11)
    assert torch.allclose(t, torch.tensor([0.11, 0.11]), atol=2e-3)


def test_crouch_height_target_plateau_is_low():
    # tout le palier [0.375, 0.625] → hauteur basse constante
    phase = torch.tensor([0.375, 0.5, 0.624])
    t = mdp.crouch_height_target(phase, height_low=0.075, height_high=0.11)
    assert torch.allclose(t, torch.full((3,), 0.075), atol=1e-6)


def test_crouch_height_target_descent_midpoint():
    # milieu de la descente (phase = hold_lo/2 = 0.1875) → milieu des deux hauteurs
    phase = torch.tensor([0.1875])
    t = mdp.crouch_height_target(phase, height_low=0.075, height_high=0.11)
    assert torch.allclose(t, torch.tensor([(0.11 + 0.075) / 2]), atol=1e-6)


def test_crouch_height_target_rise_midpoint():
    # milieu de la remontée (phase = 0.8125) → milieu des deux hauteurs
    phase = torch.tensor([0.8125])
    t = mdp.crouch_height_target(phase, height_low=0.075, height_high=0.11)
    assert torch.allclose(t, torch.tensor([(0.11 + 0.075) / 2]), atol=1e-6)
```

- [ ] **Step 2: Lancer le test pour vérifier qu'il échoue**

Run: `uv run --with pytest pytest tests/test_crouch_glide.py -v`
Expected: FAIL — `AttributeError: module ... has no attribute 'crouch_height_target'`

- [ ] **Step 3: Implémenter la fonction**

Dans `src/mjlab_microduck/tasks/mdp.py`, juste après `com_height_target` (après la ligne 737) :

```python
def crouch_height_target(
    phase: torch.Tensor,
    height_low: float,
    height_high: float,
    hold_lo: float = 0.375,
    hold_hi: float = 0.625,
) -> torch.Tensor:
    """Cible de hauteur du tronc « en trapèze » le long de la phase [0,1).

    phase ∈ [0, hold_lo)      : descente   height_high -> height_low
    phase ∈ [hold_lo, hold_hi): palier      height_low   (la glisse accroupie)
    phase ∈ [hold_hi, 1.0)    : remontée    height_low  -> height_high

    Args:
        phase: (B,) phase par env, dans [0, 1).
        height_low: hauteur du tronc accroupi (m).
        height_high: hauteur du tronc debout (m).
        hold_lo, hold_hi: bornes du palier bas en fraction de phase.
    Returns:
        (B,) hauteur-cible en mètres.
    """
    descend = phase < hold_lo
    hold = (phase >= hold_lo) & (phase < hold_hi)

    frac_d = phase / hold_lo
    t_descend = height_high + (height_low - height_high) * frac_d

    t_hold = torch.full_like(phase, height_low)

    frac_r = (phase - hold_hi) / (1.0 - hold_hi)
    t_rise = height_low + (height_high - height_low) * frac_r

    return torch.where(descend, t_descend, torch.where(hold, t_hold, t_rise))
```

- [ ] **Step 4: Lancer le test pour vérifier qu'il passe**

Run: `uv run --with pytest pytest tests/test_crouch_glide.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_crouch_glide.py
git commit -m "roller-crouch: cible de hauteur en trapezoide (fonction pure + tests)"
```

---

## Task 2: Rewards crouch-glide et forward-speed

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py`
- Test: `tests/test_crouch_glide.py` (ajouts)

**Interfaces:**
- Consumes: `crouch_height_target` (Task 1).
- Produces:
  - `crouch_glide_reward_from_values(com_height, cmd_cos, cmd_sin, height_low, height_high, hold_lo=0.375, hold_hi=0.625, std=0.02) -> torch.Tensor` (pure).
  - `crouch_glide_height_by_phase(env, command_name="twist", height_low=0.075, height_high=0.11, hold_lo=0.375, hold_hi=0.625, std=0.02, asset_cfg=_DEFAULT_ASSET_CFG) -> torch.Tensor` (wrapper env).
  - `forward_speed_reward(env, vel_ref=0.2, asset_cfg=_DEFAULT_ASSET_CFG) -> torch.Tensor` — récompense la vitesse avant (élan), indépendante de la commande.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `tests/test_crouch_glide.py` :

```python
def test_reward_is_one_when_height_matches_target():
    # phase 0.5 (plein palier) → cible = height_low ; si com_height == height_low → reward 1
    cmd_cos = torch.tensor([math.cos(2 * math.pi * 0.5)])  # -1
    cmd_sin = torch.tensor([math.sin(2 * math.pi * 0.5)])  # ~0
    com_height = torch.tensor([0.075])
    r = mdp.crouch_glide_reward_from_values(
        com_height, cmd_cos, cmd_sin, height_low=0.075, height_high=0.11, std=0.02
    )
    assert torch.allclose(r, torch.tensor([1.0]), atol=1e-3)


def test_reward_decays_when_off_by_one_std():
    # à height_low + std de la cible → exp(-1) ≈ 0.368
    cmd_cos = torch.tensor([math.cos(2 * math.pi * 0.5)])
    cmd_sin = torch.tensor([math.sin(2 * math.pi * 0.5)])
    com_height = torch.tensor([0.075 + 0.02])
    r = mdp.crouch_glide_reward_from_values(
        com_height, cmd_cos, cmd_sin, height_low=0.075, height_high=0.11, std=0.02
    )
    assert torch.allclose(r, torch.tensor([math.exp(-1.0)]), atol=1e-3)


def test_reward_at_phase_zero_expects_high_stance():
    # phase 0 → cible = height_high ; rester debout est récompensé, être accroupi non
    cmd_cos = torch.tensor([1.0, 1.0])   # cos(0)
    cmd_sin = torch.tensor([0.0, 0.0])   # sin(0)
    com_height = torch.tensor([0.11, 0.075])  # debout vs accroupi
    r = mdp.crouch_glide_reward_from_values(
        com_height, cmd_cos, cmd_sin, height_low=0.075, height_high=0.11, std=0.02
    )
    assert r[0] > 0.99          # debout à phase 0 → ~1
    assert r[1] < 0.2           # accroupi à phase 0 → faible
```

- [ ] **Step 2: Vérifier l'échec**

Run: `uv run --with pytest pytest tests/test_crouch_glide.py -v`
Expected: FAIL — `crouch_glide_reward_from_values` n'existe pas.

- [ ] **Step 3: Implémenter les trois fonctions**

Dans `src/mjlab_microduck/tasks/mdp.py`, à la suite de `crouch_height_target` :

```python
def crouch_glide_reward_from_values(
    com_height: torch.Tensor,
    cmd_cos: torch.Tensor,
    cmd_sin: torch.Tensor,
    height_low: float,
    height_high: float,
    hold_lo: float = 0.375,
    hold_hi: float = 0.625,
    std: float = 0.02,
) -> torch.Tensor:
    """Récompense gaussienne du suivi de la cible de hauteur (fonction pure).

    Décode la phase depuis [cos, sin] puis compare la hauteur mesurée à la
    cible-trapèze. Retourne exp(-((h - cible)/std)^2) ∈ (0, 1].
    """
    phase = (torch.atan2(cmd_sin, cmd_cos) / (2 * torch.pi)) % 1.0
    target = crouch_height_target(phase, height_low, height_high, hold_lo, hold_hi)
    return torch.exp(-((com_height - target) / std) ** 2)


def crouch_glide_height_by_phase(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    height_low: float = 0.075,
    height_high: float = 0.11,
    hold_lo: float = 0.375,
    hold_hi: float = 0.625,
    std: float = 0.02,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Reward principale : suit la cible de hauteur du tronc le long de la phase.

    La hauteur du CoM est calculée comme dans `com_height_target` (world z moins
    l'origine du terrain, nan->0). La phase provient de la commande GroundPick.
    """
    asset: Entity = env.scene[asset_cfg.name]
    com_height = torch.nan_to_num(
        asset.data.root_link_pos_w[:, 2] - env.scene.terrain.env_origins[:, 2], nan=0.0
    )
    cmd = env.command_manager.get_command(command_name)
    return crouch_glide_reward_from_values(
        com_height, cmd[:, 0], cmd[:, 1],
        height_low, height_high, hold_lo, hold_hi, std,
    )


def forward_speed_reward(
    env: ManagerBasedRlEnv,
    vel_ref: float = 0.2,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Récompense la vitesse avant du tronc (conserver l'élan / ne pas freiner).

    Indépendante de la commande (la commande porte la phase, pas la vitesse).
    tanh(clamp(vx, 0)/vel_ref) → sature à ~1, ne récompense jamais reculer.
    """
    asset: Entity = env.scene[asset_cfg.name]
    vx = asset.data.root_link_lin_vel_b[:, 0]
    return torch.tanh(torch.clamp(vx, min=0.0) / vel_ref)
```

- [ ] **Step 4: Vérifier le passage**

Run: `uv run --with pytest pytest tests/test_crouch_glide.py -v`
Expected: PASS (7 tests au total)

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_crouch_glide.py
git commit -m "roller-crouch: rewards crouch-glide-height et forward-speed"
```

---

## Task 3: L'environnement + enregistrement de la tâche

**Files:**
- Create: `src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py`
- Modify: `src/mjlab_microduck/tasks/__init__.py`
- Test: `tests/test_roller_crouch_cfg.py`

**Interfaces:**
- Consumes: `crouch_glide_height_by_phase`, `forward_speed_reward`, `ground_pick_return_pose` (Task 2 + existant), `GroundPickPhaseCommandCfg`, `GroundPickPhaseCommand`, `MICRODUCK_WALK_ROLLERS_ROBOT_CFG`.
- Produces: `make_microduck_roller_crouch_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg`, `MicroduckRollerCrouchRlCfg`, tâche `Mjlab-RollerCrouch-Flat-MicroDuck`.

- [ ] **Step 1: Écrire le smoke test qui échoue**

Créer `tests/test_roller_crouch_cfg.py` :

```python
from mjlab_microduck.tasks.microduck_roller_crouch_env_cfg import (
    make_microduck_roller_crouch_env_cfg,
)
from mjlab_microduck.tasks import mdp as microduck_mdp


def test_cfg_uses_phase_command():
    cfg = make_microduck_roller_crouch_env_cfg()
    assert isinstance(
        cfg.commands["twist"], microduck_mdp.GroundPickPhaseCommandCfg
    )
    assert cfg.commands["twist"].period == 4.0


def test_cfg_has_crouch_and_forward_rewards():
    cfg = make_microduck_roller_crouch_env_cfg()
    assert "crouch_glide_height" in cfg.rewards
    assert "forward_speed" in cfg.rewards
    # rewards de patinage actif retirées (pas de stride pendant le trick)
    for gone in ("braking", "skating_air_time", "single_support", "glide", "wheel_speed"):
        assert gone not in cfg.rewards


def test_cfg_has_entry_velocity_event():
    cfg = make_microduck_roller_crouch_env_cfg()
    assert "entry_velocity" in cfg.events
```

- [ ] **Step 2: Vérifier l'échec**

Run: `uv run --with pytest pytest tests/test_roller_crouch_cfg.py -v`
Expected: FAIL — `ModuleNotFoundError: ...microduck_roller_crouch_env_cfg`

- [ ] **Step 3: Créer le fichier d'environnement**

Créer `src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py` :

```python
"""Microduck roller crouch-glide task.

Geste one-shot déclenché au bouton A via le slot --ground-pick du runtime :
le robot s'accroupit et glisse sur son élan (palier ~1 s), puis se relève et
rend la main à la policy roller.

Hybride :
  - physique / robot roller  ← microduck_velocity_rollers_env_cfg.py
  - machinerie phase one-shot ← microduck_ground_pick_env_cfg.py
    (commande GroundPickPhaseCommand : [cos(2πφ), sin(2πφ), 0], période 4 s)

Cible de hauteur « en trapèze » (haut→bas→palier 1 s→haut) via
crouch_glide_height_by_phase. Obs 61D unifié → interchangeable au runtime.
"""

import math
from copy import deepcopy

ENABLE_SYMMETRY = False

# DR — repris du roller env
ENABLE_COM_RANDOMIZATION             = True
ENABLE_HEAD_COM_RANDOMIZATION        = True
ENABLE_MASS_INERTIA_RANDOMIZATION    = True
ENABLE_JOINT_FRICTION_RANDOMIZATION  = True
ENABLE_ARMATURE_RANDOMIZATION        = True
ENABLE_WHEEL_FRICTION_RANDOMIZATION  = True
ENABLE_VELOCITY_PUSHES               = True
ENABLE_IMU_ORIENTATION_RANDOMIZATION = True
ENABLE_ENCODER_BIAS                  = True

COM_RANDOMIZATION_RANGE          = 0.003
HEAD_COM_RANDOMIZATION_RANGE     = 0.003
MASS_INERTIA_RANDOMIZATION_RANGE = (0.95, 1.05)
JOINT_FRICTION_RANDOMIZATION_RANGE = (0.9, 1.1)
ARMATURE_RANDOMIZATION_RANGE     = (0.9, 1.1)
VELOCITY_PUSH_INTERVAL_S         = (3.0, 6.0)
VELOCITY_PUSH_RANGE              = (-0.2, 0.2)
IMU_ORIENTATION_RANDOMIZATION_ANGLE = 6.0
ENCODER_BIAS_RANGE               = (-0.015, 0.015)

# Geste : hauteurs cibles (m) et vitesse d'entrée (élan)
CROUCH_HEIGHT_HIGH = 0.11    # tronc debout
CROUCH_HEIGHT_LOW  = 0.075   # tronc accroupi (à affiner en play)
CROUCH_STD         = 0.02
ENTRY_VELOCITY_X   = (0.2, 0.5)  # m/s : le robot arrive en roulant

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers import (
    CurriculumTermCfg,
    EventTermCfg,
    ObservationTermCfg,
    RewardTermCfg,
    TerminationTermCfg,
)
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.rl import RslRlOnPolicyRunnerCfg, RslRlModelCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.tasks.velocity import mdp
from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
from mjlab.tasks.velocity.velocity_env_cfg import make_velocity_env_cfg
from mjlab.utils.noise import UniformNoiseCfg as Unoise

from mjlab_microduck.robot.microduck_constants import MICRODUCK_WALK_ROLLERS_ROBOT_CFG
from mjlab_microduck.tasks import mdp as microduck_mdp
from mjlab_microduck.tasks.microduck_velocity_env_cfg import HEAD_BODY_NAMES
from mjlab_microduck.tasks.symmetry import PpoWithSymmetryCfg, SYMMETRY_CFG


def make_microduck_roller_crouch_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
    """Env crouch-glide sur rollers, piloté par la phase du slot ground-pick."""

    feet_ground_cfg = ContactSensorCfg(
        name="feet_ground_contact",
        primary=ContactMatch(
            mode="subtree",
            pattern=r"^(roller_blade|roller_blade_2)$",
            entity="robot",
        ),
        secondary=ContactMatch(mode="body", pattern="terrain"),
        fields=("found", "force"),
        reduce="netforce",
        num_slots=1,
        track_air_time=True,
    )
    self_collision_cfg = ContactSensorCfg(
        name="self_collision",
        primary=ContactMatch(mode="subtree", pattern="trunk_base", entity="robot"),
        secondary=ContactMatch(mode="subtree", pattern="trunk_base", entity="robot"),
        fields=("found",),
        reduce="none",
        num_slots=1,
    )

    cfg = make_velocity_env_cfg()
    cfg.scene.entities = {"robot": MICRODUCK_WALK_ROLLERS_ROBOT_CFG}
    cfg.scene.sensors = (feet_ground_cfg, self_collision_cfg)
    cfg.viewer.body_name = "trunk_base"

    joint_pos_action = cfg.actions["joint_pos"]
    assert isinstance(joint_pos_action, JointPositionActionCfg)
    joint_pos_action.scale = 1.0

    # === REWARDS ===
    keep = {"upright", "body_ang_vel", "angular_momentum", "action_rate_l2"}
    for name in list(cfg.rewards.keys()):
        if name not in keep:
            del cfg.rewards[name]

    cfg.rewards["upright"].params["asset_cfg"].body_names = ("trunk_base",)
    cfg.rewards["upright"].weight = 2.0
    cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("trunk_base",)
    cfg.rewards["body_ang_vel"].weight = -0.05
    cfg.rewards["angular_momentum"].weight = -0.02
    cfg.rewards["action_rate_l2"].weight = -1.0

    # Reward principale : cible de hauteur trapèze le long de la phase
    cfg.rewards["crouch_glide_height"] = RewardTermCfg(
        func=microduck_mdp.crouch_glide_height_by_phase,
        weight=4.0,
        params={
            "command_name": "twist",
            "height_low": CROUCH_HEIGHT_LOW,
            "height_high": CROUCH_HEIGHT_HIGH,
            "hold_lo": 0.375,
            "hold_hi": 0.625,
            "std": CROUCH_STD,
        },
    )
    # Conserver l'élan (ne pas freiner) — indépendant de la commande
    cfg.rewards["forward_speed"] = RewardTermCfg(
        func=microduck_mdp.forward_speed_reward,
        weight=2.0,
        params={"vel_ref": 0.2},
    )
    # Fin de phase : converger vers la pose roller debout pour rendre la main proprement
    _LEG_JOINTS = [0, 1, 2, 3, 4, 9, 10, 11, 12, 13]
    _NECK_JOINTS = [5, 6, 7, 8]
    cfg.rewards["return_pose_legs"] = RewardTermCfg(
        func=microduck_mdp.ground_pick_return_pose,
        weight=3.0,
        params={"std": 0.3, "command_name": "twist", "joint_indices": _LEG_JOINTS},
    )
    cfg.rewards["return_pose_neck"] = RewardTermCfg(
        func=microduck_mdp.ground_pick_return_pose,
        weight=3.0,
        params={"std": 0.15, "command_name": "twist", "joint_indices": _NECK_JOINTS},
    )
    # Stabilité de glisse
    cfg.rewards["feet_flat"] = RewardTermCfg(
        func=microduck_mdp.feet_flat_penalty,
        weight=-2.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", site_names=("left_foot", "right_foot")),
            "sensor_name": "feet_ground_contact",
        },
    )
    cfg.rewards["self_collisions"] = RewardTermCfg(
        func=mdp.self_collision_cost,
        weight=-1.0,
        params={"sensor_name": "self_collision"},
    )
    cfg.rewards["neck_action_rate_l2"] = RewardTermCfg(
        func=microduck_mdp.neck_action_rate_l2, weight=-0.5
    )
    cfg.rewards["joint_torques_l2"] = RewardTermCfg(
        func=microduck_mdp.joint_torques_l2, weight=-1e-3
    )

    # === TERMINATIONS ===
    cfg.terminations["nan_state"] = TerminationTermCfg(
        func=microduck_mdp.robot_state_is_nan, time_out=False,
    )

    # === EVENTS ===
    cfg.events["reset_action_history"] = EventTermCfg(
        func=microduck_mdp.reset_action_history, mode="reset",
    )
    del cfg.events["foot_friction"]

    # Vitesse d'entrée : le robot démarre en roulant vers l'avant (élan à conserver)
    cfg.events["entry_velocity"] = EventTermCfg(
        func=mdp.push_by_setting_velocity,
        mode="reset",
        params={
            "velocity_range": {"x": ENTRY_VELOCITY_X, "y": (0.0, 0.0)},
            "asset_cfg": SceneEntityCfg("robot"),
        },
    )

    if ENABLE_VELOCITY_PUSHES:
        cfg.events["push_robot"] = EventTermCfg(
            func=mdp.push_by_setting_velocity,
            mode="interval",
            interval_range_s=VELOCITY_PUSH_INTERVAL_S,
            params={
                "velocity_range": {"x": VELOCITY_PUSH_RANGE, "y": VELOCITY_PUSH_RANGE},
                "asset_cfg": SceneEntityCfg("robot"),
            },
        )

    cfg.events["reset_base"].params["pose_range"]["z"] = (0.1335, 0.1435)

    if ENABLE_WHEEL_FRICTION_RANDOMIZATION:
        cfg.events["randomize_wheel_friction"] = EventTermCfg(
            func=dr.dof_frictionloss,
            mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", joint_names=(r"^passive_.*",)),
                "operation": "abs",
                "ranges": (0.000, 0.000),
            },
        )
    if ENABLE_COM_RANDOMIZATION:
        cfg.events["randomize_com"] = EventTermCfg(
            func=dr.body_ipos, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
                "operation": "add",
                "ranges": (-COM_RANDOMIZATION_RANGE, COM_RANDOMIZATION_RANGE),
            },
        )
    if ENABLE_HEAD_COM_RANDOMIZATION:
        cfg.events["randomize_head_com"] = EventTermCfg(
            func=dr.body_ipos, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=HEAD_BODY_NAMES),
                "operation": "add",
                "ranges": (-HEAD_COM_RANDOMIZATION_RANGE, HEAD_COM_RANDOMIZATION_RANGE),
            },
        )
    if ENABLE_MASS_INERTIA_RANDOMIZATION:
        _mi_lo, _mi_hi = MASS_INERTIA_RANDOMIZATION_RANGE
        cfg.events["randomize_mass_inertia"] = EventTermCfg(
            func=dr.pseudo_inertia, mode="startup",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
                "alpha_range": (math.log(_mi_lo) / 2.0, math.log(_mi_hi) / 2.0),
            },
        )
    if ENABLE_JOINT_FRICTION_RANDOMIZATION:
        cfg.events["randomize_joint_friction"] = EventTermCfg(
            func=microduck_mdp.randomize_bam_friction, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot"),
                "scale_range": JOINT_FRICTION_RANDOMIZATION_RANGE,
            },
        )
    if ENABLE_ARMATURE_RANDOMIZATION:
        cfg.events["randomize_armature"] = EventTermCfg(
            func=dr.joint_armature, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", joint_names=(r"^(?!passive_).*",)),
                "operation": "scale",
                "ranges": ARMATURE_RANDOMIZATION_RANGE,
            },
        )

    # === OBSERVATIONS (unified 61D layout) ===
    del cfg.observations["actor"].terms["base_lin_vel"]
    del cfg.observations["critic"].terms["foot_height"]
    del cfg.observations["actor"].terms["height_scan"]
    del cfg.observations["critic"].terms["height_scan"]
    cfg.observations["critic"].terms["base_lin_vel"] = ObservationTermCfg(
        func=mdp.base_lin_vel, scale=1.0,
    )

    gravity_term_name = "projected_gravity"
    cfg.observations["actor"].terms[gravity_term_name] = deepcopy(
        cfg.observations["actor"].terms[gravity_term_name]
    )
    cfg.observations["actor"].terms["base_ang_vel"] = deepcopy(
        cfg.observations["actor"].terms["base_ang_vel"]
    )
    cfg.observations["actor"].terms["base_ang_vel"].delay_min_lag = 0
    cfg.observations["actor"].terms["base_ang_vel"].delay_max_lag = 1
    cfg.observations["actor"].terms["base_ang_vel"].delay_update_period = 64
    cfg.observations["actor"].terms[gravity_term_name].delay_min_lag = 0
    cfg.observations["actor"].terms[gravity_term_name].delay_max_lag = 1
    cfg.observations["actor"].terms[gravity_term_name].delay_update_period = 64
    cfg.observations["actor"].terms["base_ang_vel"].noise = Unoise(n_min=-0.03, n_max=0.03)
    cfg.observations["actor"].terms[gravity_term_name].noise = Unoise(n_min=-0.01, n_max=0.01)
    cfg.observations["actor"].terms["joint_pos"].noise = Unoise(n_min=-0.001, n_max=0.001)
    cfg.observations["actor"].terms["joint_vel"].noise = Unoise(n_min=-0.25, n_max=0.25)

    if ENABLE_IMU_ORIENTATION_RANDOMIZATION:
        av = cfg.observations["actor"].terms["base_ang_vel"]
        av.func = microduck_mdp.base_ang_vel_imu_misaligned
        av.params = {"max_angle_deg": IMU_ORIENTATION_RANDOMIZATION_ANGLE}
        g = cfg.observations["actor"].terms[gravity_term_name]
        g.func = microduck_mdp.projected_gravity_imu_misaligned
        g.params = {"max_angle_deg": IMU_ORIENTATION_RANDOMIZATION_ANGLE}

    cfg.observations["actor"].terms["joint_vel"] = deepcopy(
        cfg.observations["actor"].terms["joint_vel"]
    )
    cfg.observations["actor"].terms["joint_vel"].delay_min_lag = 1
    cfg.observations["actor"].terms["joint_vel"].delay_max_lag = 1
    cfg.observations["actor"].terms["joint_vel"].delay_update_period = 0

    passive_excluded = SceneEntityCfg("robot", joint_names=(r"^(?!passive_).*",))
    for grp in ("actor", "critic"):
        for term in ("joint_pos", "joint_vel"):
            cfg.observations[grp].terms[term] = deepcopy(cfg.observations[grp].terms[term])
            cfg.observations[grp].terms[term].params["asset_cfg"] = deepcopy(passive_excluded)

    if ENABLE_ENCODER_BIAS:
        cfg.events["encoder_bias"].params["bias_range"] = ENCODER_BIAS_RANGE
        cfg.observations["actor"].terms["joint_pos"].params["biased"] = True
        cfg.observations["critic"].terms["joint_pos"].params["biased"] = False
    else:
        cfg.events.pop("encoder_bias", None)

    wheel_cfg = SceneEntityCfg("robot", joint_names=(r"^passive_.*",))
    cfg.observations["critic"].terms["wheel_vel"] = ObservationTermCfg(
        func=mdp.joint_vel_rel, scale=1.0, params={"asset_cfg": wheel_cfg},
    )

    for group in ("actor", "critic"):
        cfg.observations[group].terms["head_command"] = ObservationTermCfg(
            func=microduck_mdp.zero_command_padding, params={"dim": 4},
        )
        cfg.observations[group].terms["body_command"] = ObservationTermCfg(
            func=microduck_mdp.zero_command_padding, params={"dim": 6},
        )

    # === COMMAND: phase (comme ground_pick) ===
    command: UniformVelocityCommandCfg = cfg.commands["twist"]
    command.rel_standing_envs = 0.0
    command.rel_heading_envs = 0.0
    cfg.commands["twist"] = microduck_mdp.GroundPickPhaseCommandCfg(
        **{**vars(command), "class_type": microduck_mdp.GroundPickPhaseCommand, "period": 4.0}
    )

    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None

    # === CURRICULUM ===
    del cfg.curriculum["terrain_levels"]
    del cfg.curriculum["command_vel"]
    cfg.curriculum["action_rate_weight"] = CurriculumTermCfg(
        func=microduck_mdp.reward_weight,
        params={
            "reward_name": "action_rate_l2",
            "weight_stages": [
                {"step": 0, "weight": -0.5},
                {"step": 250 * 24, "weight": -0.8},
                {"step": 500 * 24, "weight": -1.0},
            ],
        },
    )
    if ENABLE_COM_RANDOMIZATION:
        cfg.curriculum["com_range"] = CurriculumTermCfg(
            func=microduck_mdp.com_range_curriculum,
            params={
                "event_name": "randomize_com",
                "range_stages": [
                    {"step": 0, "range": 0.003},
                    {"step": 500 * 24, "range": 0.005},
                    {"step": 1000 * 24, "range": 0.01},
                ],
            },
        )
    if ENABLE_HEAD_COM_RANDOMIZATION:
        cfg.curriculum["head_com_range"] = CurriculumTermCfg(
            func=microduck_mdp.com_range_curriculum,
            params={
                "event_name": "randomize_head_com",
                "range_stages": [
                    {"step": 0, "range": 0.003},
                    {"step": 500 * 24, "range": 0.005},
                    {"step": 1000 * 24, "range": 0.01},
                ],
            },
        )

    return cfg


MicroduckRollerCrouchRlCfg = RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,
        distribution_cfg={
            "class_name": "GaussianDistribution",
            "init_std": 1.0,
            "std_type": "scalar",
        },
    ),
    critic=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,
    ),
    algorithm=PpoWithSymmetryCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
        symmetry_cfg=SYMMETRY_CFG if ENABLE_SYMMETRY else None,
    ),
    wandb_project="mjlab_microduck",
    experiment_name="roller_crouch",
    run_name="roller_crouch",
    save_interval=250,
    num_steps_per_env=24,
    max_iterations=8_000,
)
```

- [ ] **Step 4: Enregistrer la tâche**

Dans `src/mjlab_microduck/tasks/__init__.py`, ajouter l'import après le bloc rollers (après la ligne 54) :

```python
from .microduck_roller_crouch_env_cfg import (
    make_microduck_roller_crouch_env_cfg,
    MicroduckRollerCrouchRlCfg,
)
```

et l'enregistrement après le bloc rollers (après la ligne 175) :

```python
register_mjlab_task(
    task_id="Mjlab-RollerCrouch-Flat-MicroDuck",
    env_cfg=make_microduck_roller_crouch_env_cfg(),
    play_env_cfg=make_microduck_roller_crouch_env_cfg(play=True),
    rl_cfg=MicroduckRollerCrouchRlCfg,
    runner_cls=MicroduckOnPolicyRunner,
)
print("✓ RollerCrouch task registered: Mjlab-RollerCrouch-Flat-MicroDuck")
```

- [ ] **Step 5: Vérifier le passage du smoke test**

Run: `uv run --with pytest pytest tests/test_roller_crouch_cfg.py -v`
Expected: PASS (3 tests). (Ce test construit l'env — il compile le spec MuJoCo, donc il est plus lent ; c'est normal.)

- [ ] **Step 6: Vérifier que la tâche est bien enregistrée**

Run: `uv run python -c "import mjlab_microduck.tasks"`
Expected: la ligne `✓ RollerCrouch task registered: Mjlab-RollerCrouch-Flat-MicroDuck` s'affiche sans erreur.

- [ ] **Step 7: Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py \
        src/mjlab_microduck/tasks/__init__.py tests/test_roller_crouch_cfg.py
git commit -m "roller-crouch: env crouch-glide + enregistrement de la tache"
```

---

## Task 4: Smoke run d'entraînement (vérification runtime)

**Files:** aucun (vérification observationnelle).

**Interfaces:**
- Consumes: la tâche `Mjlab-RollerCrouch-Flat-MicroDuck` (Task 3).

- [ ] **Step 1: Lancer un entraînement très court**

Run:
```bash
uv run train Mjlab-RollerCrouch-Flat-MicroDuck \
  --env.scene.num-envs 64 --agent.max_iterations 5
```
Expected: l'entraînement démarre, log les rewards (dont `crouch_glide_height`, `forward_speed`), 5 itérations sans crash, un checkpoint est écrit.

- [ ] **Step 2: Vérifier l'absence d'erreur de forme d'obs**

Inspecter le log de démarrage : l'obs actor doit être **61D** (comme les autres policies de la famille). Si la dim diffère, le padding head/body ou l'exclusion des roues est mal câblé — corriger avant de continuer.

- [ ] **Step 3: Commit (si un fichier de conf a dû être ajusté)**

```bash
git add -A && git commit -m "roller-crouch: ajustement post smoke-run"
```
(S'il n'y a rien à committer, sauter cette étape.)

---

## Task 5: Entraînement complet + vérification en play

**Files:** itérations possibles sur `microduck_roller_crouch_env_cfg.py` (poids de reward, `CROUCH_HEIGHT_LOW`).

- [ ] **Step 1: Lancer l'entraînement complet**

Run:
```bash
uv run train Mjlab-RollerCrouch-Flat-MicroDuck \
  --env.scene.num-envs 4096 --agent.max_iterations 8000
```

- [ ] **Step 2: Visualiser en play**

Run: `uv run scripts/play_latest.py` (ou l'entrée play du projet pour cette tâche).
Observer le cycle : le robot **descend**, **glisse ~1 s** avec les roues qui continuent de tourner (il ne freine pas), puis **se relève** et la pose finale rejoint la pose roller debout. Il ne doit pas tomber.

- [ ] **Step 3: Itérer si nécessaire**

Réglages typiques (dans `microduck_roller_crouch_env_cfg.py`) :
- Il ne descend pas assez → baisser `CROUCH_HEIGHT_LOW` (ex. 0.07) et/ou monter le poids de `crouch_glide_height`.
- Il freine pendant l'accroupi → monter le poids de `forward_speed`.
- Il tombe en position basse → monter `upright`, baisser la vitesse d'entrée `ENTRY_VELOCITY_X`, ou raccourcir le palier (rapprocher `hold_lo`/`hold_hi`).
- La remontée est brutale → monter `return_pose_*` et/ou `action_rate_l2`.

Après chaque changement, relancer un entraînement et re-visualiser. Committer chaque réglage retenu :
```bash
git add src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py
git commit -m "roller-crouch: reglage <ce qui a change>"
```

---

## Task 6: Export ONNX + déploiement sur le robot

**Files:** aucun (manuel / matériel).

- [ ] **Step 1: Exporter la policy en ONNX**

Run: `uv run scripts/export_latest.py` (le normaliseur d'obs est baké dans le graphe par `scripts/export.py`).
Récupérer le fichier `.onnx`, le renommer `roller_crouch.onnx`, le copier sur le robot (ex. `~/microduck/policies/roller_crouch.onnx`).

- [ ] **Step 2: Lancer le runtime avec le slot ground-pick**

Sur le robot :
```bash
microduck_runtime --variant pre-alpha --new-cmd-obs --roller \
  --model output.onnx \
  --new-dxl-imu --kp 200 --action-scale 0.8 \
  --max-linear-vel 0.6 --max-linear-vel-backward 0.5 --max-angular-vel 0.0 \
  --ground-pick ~/microduck/policies/roller_crouch.onnx \
  --ground-pick-period 5.0 \
  --ground-pick-kp-ratio 1.0 \
  --ground-pick-action-scale 0.8
```

**Paramètres critiques (parité sim2real) :**
- `--ground-pick-kp-ratio 1.0` — le défaut 0.6 baisserait kp à 120 alors qu'on entraîne à 200.
- `--ground-pick-action-scale 0.8` — doit matcher l'`action_scale` d'entraînement.
- `--ground-pick-period 5.0` — doit matcher la période entraînée.

- [ ] **Step 3: Tester le geste**

Lancer le robot à petite vitesse en avant, appuyer sur **A**. Vérifier : il s'accroupit, glisse ~1 s, se relève, et la policy roller reprend la main proprement. Si instable, revenir à la Task 5 (itérer sur les poids / la hauteur / la vitesse d'entrée).

---

## Notes de vérification (self-review)

- **Couverture spec :** cible trapèze 1 s (Task 1) ; rewards crouch + anti-freinage + return-pose (Task 2/3) ; robot rollers + phase + obs 61D + DR (Task 3) ; vitesse d'entrée (Task 3, event `entry_velocity`) ; flags de déploiement dont le piège `kp-ratio` (Task 6). ✅
- **Piège phase vs vitesse :** `wheel_speed_reward`/`braking`/`coasting_reward` du roller env utilisent `command[:,0]` comme *vitesse* — invalide ici où `command[:,0]=cos(2πφ)`. Elles sont donc **retirées** et remplacées par `forward_speed_reward` (indépendante de la commande). Testé par `test_cfg_has_crouch_and_forward_rewards`.
- **Cohérence des noms :** `crouch_glide_height` (clé reward) vs `crouch_glide_height_by_phase` (fonction) — voulu : la clé est le nom du terme, la fonction est `func=`.
```

```

### File: `docs/superpowers/plans/2026-07-22-roller-slope.md` (671 lines, ~7224 tokens)
```md
# Mode pente `roller_slope` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entraîner une politique dédiée où microduck (rollers) démarre sur du plat avec une impulsion, roule sur une rampe descendante, et se laisse glisser jusqu'en bas en restant debout — sans aucun pilotage.

**Architecture:** Nouvelle tâche isolée clonée de `velocity_rollers` (même robot, même obs 61D → interchangeable au runtime). Terrain custom « plat + rampe » à angle interpolé par difficulté, curriculum de raideur maison, commande neutralisée, récompenses d'équilibre + posture debout nominale. Bouton `Y` de bascule dans `infer_policy.py`.

**Tech Stack:** Python, mjlab 1.3.x, MuJoCo (MjSpec terrains), rsl_rl (PPO), PyTorch, onnxruntime (déploiement), pytest.

## Global Constraints

- **Observation unifiée 61D** : twist (3D) + head_command (4D) + body_command (6D) en zéro-padding. Ne jamais changer ce layout — la politique doit charger via `--new-cmd-obs`.
- **Résolution des joints par NOM**, jamais par index (roues passives intercalées).
- **Vitesse d'entrée via `reset_root_state_uniform` (velocity_range)**, JAMAIS via `push_by_setting_velocity` en mode reset (accumule sur l'état racine → free-joint diverge → NaN). Leçon `roller_crouch`.
- **Angles en radians** dans le code physique ; les constantes de raideur sont exprimées en degrés (`RAMP_DEG_MIN=2.0`, `RAMP_DEG_MAX=20.0`) et converties.
- **Commits simples**, style du dépôt (pas de `Co-authored-by`).
- Tests dans `tests/`, lancés avec `uv run pytest`.

---

## File Structure

- **Create** `src/mjlab_microduck/tasks/slope_terrain.py` — `ramp_angle_by_difficulty()` + `FlatRampTerrainCfg` (géométrie du terrain plat+rampe). Responsabilité unique : le terrain.
- **Modify** `src/mjlab_microduck/tasks/mdp.py` — ajouter `slope_move_masks()` (pur) + `terrain_levels_slope()` (curriculum de raideur).
- **Create** `src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py` — `make_microduck_roller_slope_env_cfg()` + `MicroduckRollerSlopeRlCfg`.
- **Modify** `src/mjlab_microduck/tasks/__init__.py` — enregistrer la tâche.
- **Modify** `scripts/infer_policy.py` — flag `--slope` + touche `Y`.
- **Create** `tests/test_slope_terrain.py`, `tests/test_slope_curriculum.py`, `tests/test_roller_slope_cfg.py`.

---

## Task 1 : angle de rampe par difficulté (fonction pure)

**Files:**
- Create: `src/mjlab_microduck/tasks/slope_terrain.py`
- Test: `tests/test_slope_terrain.py`

**Interfaces:**
- Produces: `ramp_angle_by_difficulty(difficulty: float, deg_min: float = 2.0, deg_max: float = 20.0) -> float` (retourne des **radians**). Constantes module `RAMP_DEG_MIN = 2.0`, `RAMP_DEG_MAX = 20.0`.

- [ ] **Step 1: Écrire le test qui échoue**

```python
# tests/test_slope_terrain.py
import math
from mjlab_microduck.tasks.slope_terrain import (
    ramp_angle_by_difficulty,
    RAMP_DEG_MIN,
    RAMP_DEG_MAX,
)


def test_ramp_angle_endpoints():
    assert math.isclose(ramp_angle_by_difficulty(0.0), math.radians(RAMP_DEG_MIN), abs_tol=1e-9)
    assert math.isclose(ramp_angle_by_difficulty(1.0), math.radians(RAMP_DEG_MAX), abs_tol=1e-9)


def test_ramp_angle_midpoint():
    mid_deg = (RAMP_DEG_MIN + RAMP_DEG_MAX) / 2.0
    assert math.isclose(ramp_angle_by_difficulty(0.5), math.radians(mid_deg), abs_tol=1e-9)


def test_ramp_angle_clamps_out_of_range():
    assert math.isclose(ramp_angle_by_difficulty(-1.0), math.radians(RAMP_DEG_MIN), abs_tol=1e-9)
    assert math.isclose(ramp_angle_by_difficulty(2.0), math.radians(RAMP_DEG_MAX), abs_tol=1e-9)
```

- [ ] **Step 2: Lancer le test — il doit échouer**

Run: `uv run pytest tests/test_slope_terrain.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'mjlab_microduck.tasks.slope_terrain'`

- [ ] **Step 3: Implémentation minimale**

```python
# src/mjlab_microduck/tasks/slope_terrain.py
"""Terrain custom « plat + rampe descendante » pour la tâche roller_slope.

Le robot spawne sur une zone plate, reçoit une impulsion vers +x, roule
jusqu'à la rampe et se laisse glisser. L'angle de la rampe est interpolé par
la difficulté (curriculum) sur [RAMP_DEG_MIN, RAMP_DEG_MAX] degrés.
"""

from __future__ import annotations

import math

import numpy as np

RAMP_DEG_MIN = 2.0
RAMP_DEG_MAX = 20.0


def ramp_angle_by_difficulty(
    difficulty: float, deg_min: float = RAMP_DEG_MIN, deg_max: float = RAMP_DEG_MAX
) -> float:
    """Angle de rampe (radians) interpolé linéairement par la difficulté [0,1]."""
    d = float(np.clip(difficulty, 0.0, 1.0))
    return math.radians(deg_min + d * (deg_max - deg_min))
```

- [ ] **Step 4: Lancer le test — il doit passer**

Run: `uv run pytest tests/test_slope_terrain.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/slope_terrain.py tests/test_slope_terrain.py
git commit -m "roller-slope: angle de rampe par difficulte (fonction pure + tests)"
```

---

## Task 2 : terrain custom `FlatRampTerrainCfg`

**Files:**
- Modify: `src/mjlab_microduck/tasks/slope_terrain.py`
- Test: `tests/test_slope_terrain.py`

**Interfaces:**
- Consumes: `ramp_angle_by_difficulty` (Task 1), `SubTerrainCfg`, `TerrainGeometry`, `TerrainOutput` de `mjlab.terrains.terrain_generator`.
- Produces: `FlatRampTerrainCfg(SubTerrainCfg)` avec champs `flat_length: float = 2.0`, `ramp_length: float = 5.0`, `deg_min: float = 2.0`, `deg_max: float = 20.0`, `thickness: float = 0.5` ; méthode `function(difficulty, spec, rng) -> TerrainOutput`. L'origine de spawn est sur le plat.

**Notes géométrie (à retenir) :** la surface du plat est à `z=0` local. La rampe est un box tourné autour de `+y` par un quaternion `[cos(a/2), 0, sin(a/2), 0]` — une rotation `+a` autour de `+y` abaisse le bord `+x` (la rampe descend quand `x` augmente). L'assemblage exact plat/rampe (pas de marche, pas de trou) **doit être vérifié dans le viewer** (Step 6) car le `z` du centre de la rampe est sensible.

- [ ] **Step 1: Écrire le test qui échoue**

```python
# tests/test_slope_terrain.py  (ajouter)
import mujoco
import numpy as np
from mjlab_microduck.tasks.slope_terrain import FlatRampTerrainCfg


def _empty_terrain_spec():
    spec = mujoco.MjSpec()
    spec.worldbody.add_body(name="terrain")
    return spec


def test_flat_ramp_builds_geoms_and_origin_on_flat():
    cfg = FlatRampTerrainCfg(flat_length=2.0, ramp_length=5.0)
    cfg.size = (8.0, 4.0)  # posé normalement par le générateur
    spec = _empty_terrain_spec()
    out = cfg.function(difficulty=0.5, spec=spec, rng=np.random.default_rng(0))
    # deux géométries : plat + rampe
    assert len(out.geometries) == 2
    # origine sur le plat (x dans [0, flat_length], z ~ 0)
    assert 0.0 <= out.origin[0] <= 2.0
    assert abs(out.origin[2]) < 1e-6


def test_flat_ramp_steeper_at_higher_difficulty():
    # à difficulté plus haute, le bout de rampe descend plus bas
    cfg = FlatRampTerrainCfg()
    cfg.size = (8.0, 4.0)
    easy = cfg.function(0.0, _empty_terrain_spec(), np.random.default_rng(0))
    hard = cfg.function(1.0, _empty_terrain_spec(), np.random.default_rng(0))
    # la rampe (2e géométrie) est plus basse (centre z plus négatif) en difficile
    assert hard.geometries[1].geom.pos[2] < easy.geometries[1].geom.pos[2]
```

- [ ] **Step 2: Lancer le test — il doit échouer**

Run: `uv run pytest tests/test_slope_terrain.py -k flat_ramp -v`
Expected: FAIL — `ImportError: cannot import name 'FlatRampTerrainCfg'`

- [ ] **Step 3: Implémentation minimale**

```python
# src/mjlab_microduck/tasks/slope_terrain.py  (ajouter en tête)
from dataclasses import dataclass

import mujoco

from mjlab.terrains.terrain_generator import (
    SubTerrainCfg,
    TerrainGeometry,
    TerrainOutput,
)


@dataclass(kw_only=True)
class FlatRampTerrainCfg(SubTerrainCfg):
    """Zone plate de départ suivie d'une rampe descendante (angle par difficulté)."""

    flat_length: float = 2.0   # longueur du plat de départ le long de +x (m)
    ramp_length: float = 5.0   # longueur horizontale de la rampe le long de +x (m)
    deg_min: float = RAMP_DEG_MIN
    deg_max: float = RAMP_DEG_MAX
    thickness: float = 0.5     # épaisseur des box (m)

    def function(
        self, difficulty: float, spec: mujoco.MjSpec, rng
    ) -> TerrainOutput:
        del rng  # non utilisé
        body = spec.body("terrain")
        angle = ramp_angle_by_difficulty(difficulty, self.deg_min, self.deg_max)
        width = self.size[1]
        t = self.thickness

        # Plat : box dont la surface supérieure est à z=0, x dans [0, flat_length].
        flat = body.add_geom(
            type=mujoco.mjtGeom.mjGEOM_BOX,
            size=(self.flat_length / 2.0, width / 2.0, t / 2.0),
            pos=(self.flat_length / 2.0, 0.0, -t / 2.0),
        )

        # Rampe : box tourné de +angle autour de +y (le bord +x descend).
        # Longueur de surface = ramp_length / cos(angle).
        surf_len = self.ramp_length / math.cos(angle)
        ramp_cx = self.flat_length + self.ramp_length / 2.0
        # Centre z : mi-descente de la surface, moins la demi-épaisseur projetée.
        ramp_cz = -(self.ramp_length * math.tan(angle) / 2.0) - (t / 2.0) * math.cos(angle)
        half = angle / 2.0
        ramp = body.add_geom(
            type=mujoco.mjtGeom.mjGEOM_BOX,
            size=(surf_len / 2.0, width / 2.0, t / 2.0),
            pos=(ramp_cx, 0.0, ramp_cz),
            quat=(math.cos(half), 0.0, math.sin(half), 0.0),
        )

        origin = np.array([self.flat_length * 0.4, 0.0, 0.0])
        return TerrainOutput(
            origin=origin,
            geometries=[
                TerrainGeometry(geom=flat, color=(0.5, 0.5, 0.5, 1.0)),
                TerrainGeometry(geom=ramp, color=(0.45, 0.55, 0.75, 1.0)),
            ],
        )
```

- [ ] **Step 4: Lancer les tests — ils doivent passer**

Run: `uv run pytest tests/test_slope_terrain.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/slope_terrain.py tests/test_slope_terrain.py
git commit -m "roller-slope: terrain custom plat+rampe (FlatRampTerrainCfg + tests)"
```

- [ ] **Step 6: Vérification visuelle (checkpoint humain)**

La géométrie (surtout `ramp_cz` et le signe du quaternion) doit être confirmée à l'œil.
Après la Task 4 (env assemblé), lancer le viewer play (voir Task 4 Step 6) et vérifier :
la zone plate rejoint la rampe **sans marche ni trou**, et la rampe **descend** dans
la direction `+x` (devant le robot). Si un décalage vertical apparaît, ajuster `ramp_cz` ;
si la rampe monte au lieu de descendre, inverser le signe (`-half`) du quaternion.

---

## Task 3 : curriculum de raideur `terrain_levels_slope`

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py`
- Test: `tests/test_slope_curriculum.py`

**Interfaces:**
- Produces:
  - `slope_move_masks(distance: torch.Tensor, size_x: float) -> tuple[torch.Tensor, torch.Tensor]` — helper pur. `move_up = distance > size_x * 0.5` (a atteint le bas → rampe plus raide) ; `move_down = (distance < size_x * 0.2) & ~move_up` (chute/blocage tôt → rampe plus douce). Retourne `(move_up, move_down)` en `bool`.
  - `terrain_levels_slope(env, env_ids) -> torch.Tensor` — signature curriculum mjlab ; calcule la distance parcourue en `x` depuis l'origine, applique `slope_move_masks`, appelle `terrain.update_env_origins`, retourne le niveau moyen.

- [ ] **Step 1: Écrire le test qui échoue**

```python
# tests/test_slope_curriculum.py
import torch
from mjlab_microduck.tasks.mdp import slope_move_masks


def test_move_up_when_reached_bottom():
    # distance > size_x/2 → monte en difficulté
    dist = torch.tensor([5.0, 4.1])
    up, down = slope_move_masks(dist, size_x=8.0)
    assert bool(up[0]) and bool(up[1])
    assert not bool(down[0]) and not bool(down[1])


def test_move_down_when_stuck_early():
    # distance < size_x*0.2 (=1.6) → descend en difficulté
    dist = torch.tensor([0.5, 1.0])
    up, down = slope_move_masks(dist, size_x=8.0)
    assert not bool(up[0]) and not bool(up[1])
    assert bool(down[0]) and bool(down[1])


def test_stay_in_middle_band():
    # entre 1.6 et 4.0 → ni haut ni bas
    dist = torch.tensor([2.5])
    up, down = slope_move_masks(dist, size_x=8.0)
    assert not bool(up[0]) and not bool(down[0])
```

- [ ] **Step 2: Lancer le test — il doit échouer**

Run: `uv run pytest tests/test_slope_curriculum.py -v`
Expected: FAIL — `ImportError: cannot import name 'slope_move_masks'`

- [ ] **Step 3: Implémentation minimale**

Ajouter dans `src/mjlab_microduck/tasks/mdp.py` (près des autres curriculums, ex. après `com_range_curriculum`). Vérifier en tête de fichier que `torch` est importé (il l'est).

```python
def slope_move_masks(distance: "torch.Tensor", size_x: float):
    """Masques de promotion/rétrogradation du curriculum de pente.

    move_up   : a parcouru plus de la moitié de la tuile → il a dévalé la rampe,
                on la rend plus raide.
    move_down : a à peine avancé (< 20% de la tuile) → chute/blocage précoce,
                on adoucit la rampe.
    """
    move_up = distance > size_x * 0.5
    move_down = (distance < size_x * 0.2) & (~move_up)
    return move_up, move_down


def terrain_levels_slope(env, env_ids):
    """Curriculum de raideur pour roller_slope (pas de vitesse commandée).

    Progression basée sur la distance en x parcourue depuis l'origine de spawn.
    """
    asset = env.scene["robot"]
    terrain = env.scene.terrain
    assert terrain is not None
    terrain_generator = terrain.cfg.terrain_generator
    assert terrain_generator is not None

    distance = (
        asset.data.root_link_pos_w[env_ids, 0] - env.scene.env_origins[env_ids, 0]
    )
    move_up, move_down = slope_move_masks(distance, terrain_generator.size[0])
    terrain.update_env_origins(env_ids, move_up, move_down)
    return torch.mean(terrain.terrain_levels.float())
```

- [ ] **Step 4: Lancer le test — il doit passer**

Run: `uv run pytest tests/test_slope_curriculum.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_slope_curriculum.py
git commit -m "roller-slope: curriculum de raideur terrain_levels_slope (+ helper pur teste)"
```

---

## Task 4 : env cfg `roller_slope` + enregistrement

**Files:**
- Create: `src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py`
- Modify: `src/mjlab_microduck/tasks/__init__.py`
- Test: `tests/test_roller_slope_cfg.py`

**Interfaces:**
- Consumes: `make_microduck_velocity_rollers_env_cfg` (base physique/DR/obs), `FlatRampTerrainCfg` (Task 2), `terrain_levels_slope` (Task 3), fonctions mdp existantes : `body_upright_gaussian`, `is_alive`, `pose_target_match`, `pose_l1_penalty`, `feet_flat_penalty`, `neck_action_rate_l2`, `joint_torques_l2`, `robot_state_is_nan`, `reset_action_history`, `zero_command_padding`.
- Produces: `make_microduck_roller_slope_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg` et `MicroduckRollerSlopeRlCfg` (`RslRlOnPolicyRunnerCfg`, `experiment_name="roller_slope"`).

> Réutiliser les blocs DR/obs/reset du roller env : on **part** de `make_microduck_velocity_rollers_env_cfg()` et on ne modifie QUE terrain, commande, récompenses, terminaisons, curriculum. Ne pas réécrire la DR.

- [ ] **Step 1: Écrire le test qui échoue**

```python
# tests/test_roller_slope_cfg.py
from mjlab_microduck.tasks.microduck_roller_slope_env_cfg import (
    make_microduck_roller_slope_env_cfg,
)
from mjlab_microduck.tasks.slope_terrain import FlatRampTerrainCfg


def test_terrain_is_flat_ramp_generator():
    cfg = make_microduck_roller_slope_env_cfg()
    assert cfg.scene.terrain.terrain_type == "generator"
    gen = cfg.scene.terrain.terrain_generator
    assert gen is not None and gen.curriculum is True
    assert any(isinstance(st, FlatRampTerrainCfg) for st in gen.sub_terrains.values())


def test_command_is_neutralised():
    cfg = make_microduck_roller_slope_env_cfg()
    cmd = cfg.commands["twist"]
    assert cmd.rel_standing_envs == 1.0
    assert cmd.rel_heading_envs == 0.0


def test_entry_velocity_set_on_reset_base():
    cfg = make_microduck_roller_slope_env_cfg()
    vr = cfg.events["reset_base"].params["velocity_range"]
    assert vr["x"][0] > 0.0  # impulsion vers l'avant


def test_has_upright_and_pose_rewards():
    cfg = make_microduck_roller_slope_env_cfg()
    for name in ("upright", "alive", "standing_pose", "feet_flat"):
        assert name in cfg.rewards
```

- [ ] **Step 2: Lancer le test — il doit échouer**

Run: `uv run pytest tests/test_roller_slope_cfg.py -v`
Expected: FAIL — `ModuleNotFoundError` (module env cfg absent)

- [ ] **Step 3: Implémentation**

```python
# src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py
"""Microduck roller slope — descente passive équilibrée.

Le robot spawne sur du plat (impulsion vers l'avant), roule sur une rampe
descendante et se laisse glisser en restant debout. Aucun pilotage : la
commande twist est neutralisée (rel_standing_envs=1.0). Terrain custom
plat+rampe (FlatRampTerrainCfg), curriculum de raideur (terrain_levels_slope).
Obs 61D unifié → interchangeable au runtime (--new-cmd-obs).
"""

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers import CurriculumTermCfg, EventTermCfg, RewardTermCfg, TerminationTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.rl import RslRlOnPolicyRunnerCfg, RslRlModelCfg
from mjlab.terrains import TerrainEntityCfg
from mjlab.terrains.terrain_generator import TerrainGeneratorCfg
from mjlab.tasks.velocity import mdp
from mjlab.envs import mdp as base_mdp

from mjlab_microduck.tasks import mdp as microduck_mdp
from mjlab_microduck.tasks.slope_terrain import FlatRampTerrainCfg
from mjlab_microduck.tasks.microduck_velocity_rollers_env_cfg import (
    make_microduck_velocity_rollers_env_cfg,
)
from mjlab_microduck.tasks.symmetry import PpoWithSymmetryCfg

ENTRY_VELOCITY_X = (0.2, 0.5)  # impulsion vers l'avant au reset (m/s)


def make_microduck_roller_slope_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
    cfg = make_microduck_velocity_rollers_env_cfg(play=play)

    # === TERRAIN : plat + rampe, curriculum de raideur ===
    cfg.scene.terrain = TerrainEntityCfg(
        terrain_type="generator",
        terrain_generator=TerrainGeneratorCfg(
            size=(8.0, 4.0),
            curriculum=True,
            num_rows=10,          # 10 niveaux de raideur
            num_cols=1,
            difficulty_range=(0.0, 1.0),
            sub_terrains={"flat_ramp": FlatRampTerrainCfg(flat_length=2.0, ramp_length=5.0)},
        ),
        max_init_terrain_level=0,  # démarrer sur la rampe la plus douce
    )

    # === COMMANDE neutralisée (équilibre pur) ===
    command = cfg.commands["twist"]
    command.rel_standing_envs = 1.0
    command.rel_heading_envs = 0.0
    command.ranges.lin_vel_x = (0.0, 0.0)
    command.ranges.lin_vel_y = (0.0, 0.0)
    if getattr(command.ranges, "ang_vel_z", None) is not None:
        command.ranges.ang_vel_z = (0.0, 0.0)

    # === RESET : impulsion vers l'avant sur le plat ===
    cfg.events["reset_base"].params["velocity_range"] = {"x": ENTRY_VELOCITY_X}

    # === RÉCOMPENSES : équilibre + posture debout nominale ===
    keep = {"action_rate_l2"}
    for name in list(cfg.rewards.keys()):
        if name not in keep:
            del cfg.rewards[name]

    cfg.rewards["upright"] = RewardTermCfg(
        func=microduck_mdp.body_upright_gaussian,
        weight=3.0,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)), "std": 0.2},
    )
    cfg.rewards["alive"] = RewardTermCfg(func=microduck_mdp.is_alive, weight=1.0)
    # posture debout nominale (cible fixe = default_joint_pos, aucun override)
    cfg.rewards["standing_pose"] = RewardTermCfg(
        func=microduck_mdp.pose_target_match, weight=3.0, params={"std": 0.4},
    )
    cfg.rewards["standing_pose_l1"] = RewardTermCfg(
        func=microduck_mdp.pose_l1_penalty, weight=1.0,
    )
    cfg.rewards["feet_flat"] = RewardTermCfg(
        func=microduck_mdp.feet_flat_penalty,
        weight=-2.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", site_names=("left_foot", "right_foot")),
            "sensor_name": "feet_ground_contact",
        },
    )
    cfg.rewards["neck_action_rate_l2"] = RewardTermCfg(
        func=microduck_mdp.neck_action_rate_l2, weight=-0.5,
    )
    cfg.rewards["joint_torques_l2"] = RewardTermCfg(
        func=microduck_mdp.joint_torques_l2, weight=-1e-3,
    )
    cfg.rewards["action_rate_l2"].weight = -1.0

    # === TERMINATIONS : chute + bas atteint ===
    cfg.terminations["fell_over"] = TerminationTermCfg(
        func=base_mdp.bad_orientation,
        params={"limit_angle": 1.0, "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",))},
    )
    cfg.terminations["out_of_bounds"] = TerminationTermCfg(func=mdp.out_of_terrain_bounds)
    cfg.terminations["nan_state"] = TerminationTermCfg(
        func=microduck_mdp.robot_state_is_nan, time_out=False,
    )

    # === EVENTS ===
    cfg.events["reset_action_history"] = EventTermCfg(
        func=microduck_mdp.reset_action_history, mode="reset",
    )

    # === CURRICULUM : raideur de la rampe ===
    for name in list(cfg.curriculum.keys()):
        del cfg.curriculum[name]
    cfg.curriculum["terrain_levels"] = CurriculumTermCfg(func=microduck_mdp.terrain_levels_slope)

    return cfg


MicroduckRollerSlopeRlCfg = RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,
        distribution_cfg={"class_name": "GaussianDistribution", "init_std": 1.0, "std_type": "scalar"},
    ),
    critic=RslRlModelCfg(hidden_dims=(512, 256, 128), activation="elu", obs_normalization=True),
    algorithm=PpoWithSymmetryCfg(
        value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2,
        entropy_coef=0.01, num_learning_epochs=5, num_mini_batches=4,
        learning_rate=1.0e-3, schedule="adaptive", gamma=0.99, lam=0.95,
        desired_kl=0.01, max_grad_norm=1.0, symmetry_cfg=None,
    ),
    wandb_project="mjlab_microduck",
    experiment_name="roller_slope",
    run_name="roller_slope",
    save_interval=250,
    num_steps_per_env=24,
    max_iterations=8_000,
)
```

Puis enregistrer dans `src/mjlab_microduck/tasks/__init__.py`, en suivant EXACTEMENT le pattern d'enregistrement de `roller_crouch` déjà présent (import de `make_...` + `Microduck...RlCfg`, puis `register_mjlab_task(...)` avec un id du style `"Microduck-Roller-Slope"`). Copier le bloc `roller_crouch` et remplacer `crouch`→`slope`.

- [ ] **Step 4: Lancer les tests — ils doivent passer**

Run: `uv run pytest tests/test_roller_slope_cfg.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Vérifier l'enregistrement de la tâche + build complet**

Run:
```bash
uv run python -c "import gymnasium as gym; import mjlab_microduck.tasks; print([e for e in gym.registry if 'Slope' in e])"
```
Expected: la liste contient l'id `Microduck-Roller-Slope` (ou variante enregistrée).

- [ ] **Step 6: Vérification visuelle du terrain + descente (checkpoint humain — clôt Task 2 Step 6)**

Lancer un court entraînement puis le play (ou `scripts/play_latest.py` selon l'usage du dépôt) et observer :
1. Plat + rampe assemblés sans marche/trou ; la rampe **descend** devant le robot.
2. Le robot spawne sur le plat, part vers l'avant, atteint la rampe.
Si la géométrie est fausse, corriger `slope_terrain.py` (voir Task 2 Step 6) et re-commit.

- [ ] **Step 7: Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py src/mjlab_microduck/tasks/__init__.py tests/test_roller_slope_cfg.py
git commit -m "roller-slope: env descente passive (terrain plat+rampe, cmd nulle, rewards equilibre) + enregistrement"
```

---

## Task 5 : déploiement — flag `--slope` + touche `Y`

**Files:**
- Modify: `scripts/infer_policy.py`

**Interfaces:**
- Consumes: le `.onnx` exporté de la politique `roller_slope`.
- Produces: argument CLI `--slope <path>` ; attribut `self.slope_session` + flag `self.slope_mode` ; méthode `toggle_slope_mode()` ; touche `GLFW_KEY_Y = 89` câblée.

> La politique pente tourne avec commande twist nulle (comme le mode standing). En slope mode, la bascule automatique walking/standing doit être neutralisée.

- [ ] **Step 1: Ajouter l'argument CLI et charger la session**

Dans `main()` (près des autres `add_argument`, ~ligne 471) :
```python
    parser.add_argument("--slope", type=str, default=None, help="Path to slope policy ONNX file (press Y to toggle)")
```
Passer `slope_onnx_path=args.slope` au constructeur du contrôleur (ajouter le paramètre `slope_onnx_path=None` à `__init__`, ~ligne 51-57, et charger comme les autres) :
```python
        self.slope_session = None
        self.slope_mode = False
        if slope_onnx_path:
            print(f"\nLoading slope policy from: {slope_onnx_path}")
            self.slope_session = ort.InferenceSession(slope_onnx_path)
```

- [ ] **Step 2: Ajouter `toggle_slope_mode` et neutraliser la bascule auto**

Après `toggle_body_pose_mode` (~ligne 285) :
```python
    def toggle_slope_mode(self):
        """Bascule vers/depuis la politique pente (descente passive)."""
        if self.slope_session is None:
            print("Slope unavailable: no --slope policy loaded")
            return
        self.slope_mode = not self.slope_mode
        if self.slope_mode:
            self.ort_session = self.slope_session
            self.current_policy = "slope"
            self.set_vel_cmd(0.0, 0.0, 0.0)  # descente passive : commande nulle
            print("Slope mode: ON (descente passive)")
        else:
            self.ort_session = self.walking_session or self.standing_session
            self.current_policy = "walking" if self.walking_session else "standing"
            print("Slope mode: OFF")
```
Dans `_update_policy_session` (~ligne 250), ajouter le garde en tête (après le garde `ground_pick_mode`) :
```python
        if self.slope_mode:
            return  # Ne pas basculer pendant le mode pente
```

- [ ] **Step 3: Câbler la touche `Y`**

Ajouter le code de touche près des autres (~ligne 680) :
```python
    GLFW_KEY_Y = 89
```
Dans `key_callback`, ajouter une branche (ex. après la branche `GLFW_KEY_B`) :
```python
            elif key == GLFW_KEY_Y:
                policy.toggle_slope_mode()
```
Ajouter la ligne d'aide clavier (près des `print` ~ligne 821) :
```python
    print("  Y:                toggle slope mode (requires --slope, descente passive)")
```

- [ ] **Step 4: Vérifier que le script se charge sans erreur**

Run: `uv run python scripts/infer_policy.py --help`
Expected: l'aide s'affiche et liste `--slope`.

- [ ] **Step 5: Commit**

```bash
git add scripts/infer_policy.py
git commit -m "roller-slope: deploiement --slope + touche Y (bascule mode pente)"
```

---

## Self-Review (fait par l'auteur du plan)

- **Couverture spec** : tâche dédiée (Task 4) ✓ ; terrain plat+rampe custom (Task 2) ✓ ; départ plat + impulsion (Task 4 reset velocity_range) ✓ ; commande nulle (Task 4) ✓ ; récompenses équilibre + pose debout + anti-écrasement (Task 4) ✓ ; terminaisons chute/bas/nan (Task 4) ✓ ; curriculum 0→20° (Task 1 angle + Task 3 promotion) ✓ ; obs 61D interchangeable (hérité du roller env, non modifié) ✓ ; bouton Y (Task 5) ✓.
- **Placeholders** : aucun « TBD/TODO » ; les deux checkpoints humains (géométrie viewer) sont des vérifications explicites, pas des trous d'implémentation.
- **Cohérence des types** : `ramp_angle_by_difficulty` (Task 1) réutilisé par `FlatRampTerrainCfg` (Task 2) ; `slope_move_masks` (Task 3) consommé par `terrain_levels_slope` (Task 3) ; noms de récompenses testés en Task 4 (`upright`, `alive`, `standing_pose`, `feet_flat`) alignés sur l'implémentation.
- **Risques signalés** : géométrie de la rampe (`ramp_cz`, signe du quaternion) à confirmer au viewer ; noms exacts d'API mjlab (`terrain.terrain_levels`, `TerrainEntityCfg`, id d'enregistrement) à valider contre le pattern `roller_crouch` existant lors de l'implémentation.

```

### File: `docs/superpowers/plans/2026-07-24-ground-pick-pose-following.md` (618 lines, ~6344 tokens)
```md
# Ground-pick par suivi de pose — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Réécrire la tâche `Mjlab-GroundPick-Flat-MicroDuck` pour piloter le geste par un suivi de pose articulaire interpolé par la phase (STAND→DOWN→STAND) au lieu de l'objectif espace-tâche actuel (proximité bouche-sol + retour de pose).

**Architecture:** On ajoute trois fonctions mdp pures/quasi-pures (`phase_pose_blend`, `phase_pose_track`, `phase_pose_track_l1`) qui calculent une cible articulaire interpolée entre HOME (STAND) et un dict `DOWN_POSE` selon un profil de phase à 4 segments, résolue **par nom**. On ajoute un flag `randomize_phase` à la commande de phase existante. On réécrit ensuite le bloc rewards de `microduck_ground_pick_env_cfg.py` en gardant tout le reste (DR, obs 61D, curricula, RlCfg).

**Tech Stack:** Python, PyTorch, mjlab 1.3.0, MuJoCo, uv, pytest (via `uv run --with pytest`).

## Global Constraints

- Résolution des joints **PAR NOM** (`asset.find_joints([name])[0][0]`), jamais par index en dur.
- Obs 61D unifié **inchangé** (padding head/body zéro) → policy interchangeable dans le slot runtime.
- Task id inchangé : `Mjlab-GroundPick-Flat-MicroDuck` (+ variante `-Rough-`).
- Période de phase = **4.0 s** (défaut du slot `--ground-pick-period`).
- Profil de phase (fractions) : `DESCENT_END=0.15`, `HOLD_END=0.50`, `RISE_END=0.65`.
- `randomize_phase=False` pour la tâche ground_pick (parité déploiement bouton A à φ=0) ; défaut `True` de la cfg pour ne pas casser sit/stand.
- STAND = HOME (`asset.data.default_joint_pos`, ne pas redéfinir). DOWN = dict `DOWN_POSE` par nom.
- 14 joints actifs (mouth exclu). Robot `MICRODUCK_GROUND_PICK_ROBOT_CFG` (pas de roues → indices 0-4 jambe G, 5-8 cou/tête, 9-13 jambe D, mais on résout quand même par nom).
- Fichiers mdp : imports déjà présents (`torch`, `Optional`, `Entity`, `SceneEntityCfg`, `ManagerBasedRlEnv`, `_DEFAULT_ASSET_CFG`).

---

### Task 1: Fonction `phase_pose_blend` (blend 4 segments, pure)

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (ajout d'une fonction ; l'insérer juste avant `phase_pose_match` ~ligne 2041)
- Test: `tests/test_ground_pick_pose.py` (create)

**Interfaces:**
- Produces: `phase_pose_blend(phase: torch.Tensor, descent_end: float, hold_end: float, rise_end: float) -> torch.Tensor` — renvoie un blend ∈ [0,1] de même shape que `phase` (0 = STAND, 1 = DOWN).

- [ ] **Step 1: Write the failing test**

Créer `tests/test_ground_pick_pose.py` :

```python
import torch
from mjlab_microduck.tasks.mdp import phase_pose_blend

DESCENT_END, HOLD_END, RISE_END = 0.15, 0.50, 0.65


def test_phase_pose_blend_keypoints():
    phase = torch.tensor([0.0, 0.075, 0.15, 0.30, 0.50, 0.575, 0.65, 0.80])
    b = phase_pose_blend(phase, DESCENT_END, HOLD_END, RISE_END)
    expected = torch.tensor([0.0, 0.5, 1.0, 1.0, 1.0, 0.5, 0.0, 0.0])
    assert torch.allclose(b, expected, atol=1e-6), b


def test_phase_pose_blend_range():
    phase = torch.linspace(0.0, 1.0, 101)
    b = phase_pose_blend(phase, DESCENT_END, HOLD_END, RISE_END)
    assert b.min() >= 0.0 and b.max() <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest pytest tests/test_ground_pick_pose.py -q`
Expected: FAIL — `ImportError: cannot import name 'phase_pose_blend'`

- [ ] **Step 3: Write minimal implementation**

Dans `src/mjlab_microduck/tasks/mdp.py`, juste avant `def phase_pose_match(` (~ligne 2041) :

```python
def phase_pose_blend(
    phase: torch.Tensor,
    descent_end: float,
    hold_end: float,
    rise_end: float,
) -> torch.Tensor:
    """Blend 0..1 le long de la phase [0,1) — 0 = pose STAND, 1 = pose DOWN.

    [0, descent_end)       : 0 -> 1  (se baisser)
    [descent_end, hold_end): 1       (bas)
    [hold_end, rise_end)   : 1 -> 0  (se lever)
    [rise_end, 1.0)        : 0       (haut / repos)
    """
    b = torch.zeros_like(phase)
    descend = phase < descent_end
    b = torch.where(descend, phase / descent_end, b)
    low = (phase >= descent_end) & (phase < hold_end)
    b = torch.where(low, torch.ones_like(phase), b)
    rise = (phase >= hold_end) & (phase < rise_end)
    b = torch.where(rise, 1.0 - (phase - hold_end) / (rise_end - hold_end), b)
    return b
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest pytest tests/test_ground_pick_pose.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add tests/test_ground_pick_pose.py src/mjlab_microduck/tasks/mdp.py
git commit -m "feat(mdp): phase_pose_blend — blend 4 segments STAND<->DOWN par la phase"
```

---

### Task 2: Rewards `phase_pose_track` / `phase_pose_track_l1` (+ helper `_phase_pose_error`)

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (ajout juste après `phase_pose_blend`)
- Test: `tests/test_ground_pick_pose.py` (append)

**Interfaces:**
- Consumes: `phase_pose_blend` (Task 1).
- Produces:
  - `_phase_pose_error(env, asset_cfg, command_name, target_pose: dict, descent_end, hold_end, rise_end, source_pose: dict | None = None) -> (cur: Tensor, target: Tensor)` — tenseurs (B, k) résolus par nom.
  - `phase_pose_track(env, command_name="twist", target_pose: dict | None = None, source_pose: dict | None = None, std=0.3, descent_end=0.15, hold_end=0.50, rise_end=0.65, asset_cfg=_DEFAULT_ASSET_CFG) -> Tensor` — gaussienne `exp(-((cur-target)/std)²).mean(-1)`.
  - `phase_pose_track_l1(env, command_name="twist", target_pose=None, source_pose=None, descent_end=0.15, hold_end=0.50, rise_end=0.65, asset_cfg=_DEFAULT_ASSET_CFG) -> Tensor` — `-(cur-target).abs().mean(-1)`.

- [ ] **Step 1: Write the failing test**

Ajouter à `tests/test_ground_pick_pose.py` un faux env léger + les assertions :

```python
from mjlab_microduck.tasks.mdp import phase_pose_track, phase_pose_track_l1


class _FakeData:
    def __init__(self, joint_pos, default_pos):
        self.joint_pos = joint_pos
        self.default_joint_pos = default_pos


class _FakeAsset:
    def __init__(self, names, joint_pos, default_pos):
        self._ids = {n: i for i, n in enumerate(names)}
        self.data = _FakeData(joint_pos, default_pos)

    def find_joints(self, query):
        # mjlab renvoie (ids, names) ; on ne gère que la requête [name]
        (name,) = query
        return ([self._ids[name]], [name])


class _FakeCmdMgr:
    def __init__(self, cmd):
        self._cmd = cmd

    def get_command(self, _name):
        return self._cmd


class _FakeEnv:
    def __init__(self, names, joint_pos, default_pos, phase):
        import math
        self.device = "cpu"
        self.scene = {"robot": _FakeAsset(names, joint_pos, default_pos)}
        ang = 2 * math.pi * phase
        cmd = torch.tensor([[math.cos(ang), math.sin(ang), 0.0]])
        self.command_manager = _FakeCmdMgr(cmd)


NAMES = ["j0", "j1"]
DOWN = {"j0": 1.0, "j1": -1.0}
# HOME (STAND source) = 0 pour les deux joints
HOME = torch.tensor([[0.0, 0.0]])


def _env(cur, phase):
    return _FakeEnv(NAMES, torch.tensor([cur]), HOME.clone(), phase)


def test_phase_pose_track_perfect_at_down():
    # phase 0.30 -> blend 1 -> cible = DOWN ; cur == DOWN -> gaussienne 1, l1 0
    from mjlab.managers.scene_entity_config import SceneEntityCfg
    cfg = SceneEntityCfg("robot")
    env = _env([1.0, -1.0], phase=0.30)
    r = phase_pose_track(env, target_pose=DOWN, asset_cfg=cfg)
    assert torch.allclose(r, torch.tensor([1.0]), atol=1e-6), r
    env2 = _env([1.0, -1.0], phase=0.30)
    l1 = phase_pose_track_l1(env2, target_pose=DOWN, asset_cfg=cfg)
    assert torch.allclose(l1, torch.tensor([0.0]), atol=1e-6), l1


def test_phase_pose_track_l1_at_home_when_down_target():
    # phase 0.30 -> cible DOWN=[1,-1] ; cur=HOME=[0,0] -> l1 = -mean(|1|,|1|) = -1
    from mjlab.managers.scene_entity_config import SceneEntityCfg
    cfg = SceneEntityCfg("robot")
    env = _env([0.0, 0.0], phase=0.30)
    l1 = phase_pose_track_l1(env, target_pose=DOWN, asset_cfg=cfg)
    assert torch.allclose(l1, torch.tensor([-1.0]), atol=1e-6), l1


def test_phase_pose_track_returns_to_stand():
    # phase 0.80 -> blend 0 -> cible = HOME ; cur=HOME -> gaussienne 1
    from mjlab.managers.scene_entity_config import SceneEntityCfg
    cfg = SceneEntityCfg("robot")
    env = _env([0.0, 0.0], phase=0.80)
    r = phase_pose_track(env, target_pose=DOWN, asset_cfg=cfg)
    assert torch.allclose(r, torch.tensor([1.0]), atol=1e-6), r
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest pytest tests/test_ground_pick_pose.py -q`
Expected: FAIL — `ImportError: cannot import name 'phase_pose_track'`

- [ ] **Step 3: Write minimal implementation**

Dans `src/mjlab_microduck/tasks/mdp.py`, juste après `phase_pose_blend` :

```python
def _phase_pose_error(
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg,
    command_name: str,
    target_pose: dict,
    descent_end: float,
    hold_end: float,
    rise_end: float,
    source_pose: Optional[dict] = None,
):
    """(cur, target) pour la pose interpolée par la phase, résolue PAR NOM.

    Cible = source + blend(phase)·(target_pose - source), source = STAND
    (`source_pose` si fourni, sinon le DEFAULT/HOME du modèle). blend ∈ [0,1]
    (0 = STAND, 1 = target_pose) via `phase_pose_blend`.
    """
    asset: Entity = env.scene[asset_cfg.name]
    cmd = env.command_manager.get_command(command_name)
    phase = (torch.atan2(cmd[:, 1], cmd[:, 0]) / (2 * torch.pi)) % 1.0  # (B,)
    blend = phase_pose_blend(phase, descent_end, hold_end, rise_end)     # (B,)

    names = list(target_pose.keys())
    ids = [int(asset.find_joints([n])[0][0]) for n in names]
    default = asset.data.default_joint_pos[:, ids]                       # (B,k)

    source = default.clone()
    if source_pose:
        for j, n in enumerate(names):
            if n in source_pose:
                source[:, j] = source_pose[n]
    target_vec = torch.tensor(
        [target_pose[n] for n in names], device=env.device, dtype=default.dtype
    ).unsqueeze(0)                                                       # (1,k)

    target = source + blend.unsqueeze(-1) * (target_vec - source)        # (B,k)
    cur = asset.data.joint_pos[:, ids]                                   # (B,k)
    return cur, target


def phase_pose_track(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    target_pose: Optional[dict] = None,
    source_pose: Optional[dict] = None,
    std: float = 0.3,
    descent_end: float = 0.15,
    hold_end: float = 0.50,
    rise_end: float = 0.65,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Gaussienne sur la pose articulaire vs cible interpolée STAND<->DOWN.

    Reward directif : indique la config articulaire exacte à chaque phase. Se
    relever (cible → STAND) est récompensé exactement comme se baisser (cible →
    DOWN) — symétrique par construction. Résolution PAR NOM.
    """
    cur, target = _phase_pose_error(
        env, asset_cfg, command_name, target_pose or {},
        descent_end, hold_end, rise_end, source_pose,
    )
    return torch.exp(-((cur - target) / std) ** 2).mean(dim=-1)


def phase_pose_track_l1(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    target_pose: Optional[dict] = None,
    source_pose: Optional[dict] = None,
    descent_end: float = 0.15,
    hold_end: float = 0.50,
    rise_end: float = 0.65,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Bootstrap L1 vers la cible interpolée (pénalité négative).

    Gradient constant partout — donne une direction vers la cible même quand la
    gaussienne ci-dessus a saturé à ~0 loin de la cible.
    """
    cur, target = _phase_pose_error(
        env, asset_cfg, command_name, target_pose or {},
        descent_end, hold_end, rise_end, source_pose,
    )
    return -(cur - target).abs().mean(dim=-1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest pytest tests/test_ground_pick_pose.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add tests/test_ground_pick_pose.py src/mjlab_microduck/tasks/mdp.py
git commit -m "feat(mdp): phase_pose_track/_l1 — suivi de pose interpolée par la phase (par nom)"
```

---

### Task 3: Flag `randomize_phase` sur `GroundPickPhaseCommandCfg`

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (classe `GroundPickPhaseCommand` ~3611/3626, cfg ~3644)
- Test: `tests/test_ground_pick_pose.py` (append)

**Interfaces:**
- Produces: `GroundPickPhaseCommandCfg.randomize_phase: bool = True` ; `GroundPickPhaseCommand.reset()` met la phase à 0 quand `randomize_phase=False`, sinon `torch.rand`.

- [ ] **Step 1: Write the failing test**

Ajouter à `tests/test_ground_pick_pose.py` :

```python
def test_ground_pick_cmd_cfg_has_randomize_phase_default_true():
    from mjlab_microduck.tasks.mdp import GroundPickPhaseCommandCfg
    from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
    # construit une cfg minimale en copiant une cfg velocity par défaut
    base = UniformVelocityCommandCfg(
        asset_name="robot", resampling_time_range=(10.0, 10.0),
        ranges=UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(0.0, 0.0), lin_vel_y=(0.0, 0.0), ang_vel_z=(0.0, 0.0),
        ),
    )
    cfg = GroundPickPhaseCommandCfg(**{**vars(base)})
    assert cfg.randomize_phase is True
    assert cfg.period == 4.0
```

Note : si la signature de `UniformVelocityCommandCfg.Ranges` diffère localement, adapter les champs — l'assertion clé est `cfg.randomize_phase is True`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest pytest tests/test_ground_pick_pose.py::test_ground_pick_cmd_cfg_has_randomize_phase_default_true -q`
Expected: FAIL — `AttributeError: 'GroundPickPhaseCommandCfg' object has no attribute 'randomize_phase'`

- [ ] **Step 3: Write minimal implementation**

Dans `src/mjlab_microduck/tasks/mdp.py`, classe `GroundPickPhaseCommand`, modifier `__init__` et `reset` :

Remplacer (dans `__init__`, ~ligne 3614) :
```python
        self._period = float(getattr(cfg, "period", self.PERIOD))
```
par :
```python
        self._period = float(getattr(cfg, "period", self.PERIOD))
        self._randomize_phase = bool(getattr(cfg, "randomize_phase", True))
```

Remplacer la méthode `reset` (~ligne 3626) :
```python
    def reset(self, env_ids: torch.Tensor | None) -> dict:
        if env_ids is not None and len(env_ids) > 0:
            self._gp_phase[env_ids] = torch.rand(len(env_ids), device=self.device)
        return {}
```
par :
```python
    def reset(self, env_ids: torch.Tensor | None) -> dict:
        if env_ids is not None and len(env_ids) > 0:
            if self._randomize_phase:
                self._gp_phase[env_ids] = torch.rand(len(env_ids), device=self.device)
            else:
                self._gp_phase[env_ids] = 0.0
        return {}
```

Dans la cfg `GroundPickPhaseCommandCfg` (~ligne 3644), ajouter le champ après `period` :
```python
@_dataclass(kw_only=True)
class GroundPickPhaseCommandCfg(UniformVelocityCommandCfg):
    class_type: type = GroundPickPhaseCommand
    period: float = 4.0  # cycle length in seconds; sitstand uses 8.0
    randomize_phase: bool = True  # False = chaque épisode démarre à φ=0 (parité slot bouton A)

    def build(self, env: ManagerBasedRlEnv) -> "GroundPickPhaseCommand":
        return GroundPickPhaseCommand(self, env)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest pytest tests/test_ground_pick_pose.py::test_ground_pick_cmd_cfg_has_randomize_phase_default_true -q`
Expected: PASS. Si la construction de `UniformVelocityCommandCfg` échoue pour une raison d'API locale, ajuster les champs du `base` dans le test (l'implémentation, elle, est correcte).

- [ ] **Step 5: Commit**

```bash
git add tests/test_ground_pick_pose.py src/mjlab_microduck/tasks/mdp.py
git commit -m "feat(mdp): flag randomize_phase sur GroundPickPhaseCommandCfg (défaut True)"
```

---

### Task 4: Réécriture du bloc rewards + poses dans l'env cfg

**Files:**
- Modify: `src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py`
- Test: `tests/test_ground_pick_cfg.py` (create)

**Interfaces:**
- Consumes: `phase_pose_track`, `phase_pose_track_l1` (Task 2) ; `randomize_phase` (Task 3).
- Produces: `make_microduck_ground_pick_env_cfg(play=False, rough=False)` renvoie une cfg dont : commande `GroundPickPhaseCommand` avec `randomize_phase=False`, `period=4.0` ; rewards contiennent `phase_pose_track` (6.0) et `phase_pose_track_l1` (2.0), `mouth_ground_proximity` (1.0) ; ne contiennent plus `mouth_perpendicular_to_ground`, `ground_pick_return_pose_legs`, `ground_pick_return_pose_neck`.

- [ ] **Step 1: Write the failing test**

Créer `tests/test_ground_pick_cfg.py` :

```python
from mjlab_microduck.tasks.microduck_ground_pick_env_cfg import (
    make_microduck_ground_pick_env_cfg,
)
from mjlab_microduck.tasks.mdp import GroundPickPhaseCommand


def test_ground_pick_cfg_builds_with_pose_rewards():
    cfg = make_microduck_ground_pick_env_cfg()
    rewards = cfg.rewards
    assert "phase_pose_track" in rewards
    assert "phase_pose_track_l1" in rewards
    assert rewards["phase_pose_track"].weight == 6.0
    assert rewards["phase_pose_track_l1"].weight == 2.0
    # filet bouche-sol conservé mais allégé
    assert "mouth_ground_proximity" in rewards
    assert rewards["mouth_ground_proximity"].weight == 1.0
    # anciennes mécaniques retirées
    assert "mouth_perpendicular_to_ground" not in rewards
    assert "ground_pick_return_pose_legs" not in rewards
    assert "ground_pick_return_pose_neck" not in rewards


def test_ground_pick_cfg_command_is_phase_no_randomize():
    cfg = make_microduck_ground_pick_env_cfg()
    cmd = cfg.commands["twist"]
    assert cmd.class_type is GroundPickPhaseCommand
    assert cmd.period == 4.0
    assert cmd.randomize_phase is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest pytest tests/test_ground_pick_cfg.py -q`
Expected: FAIL — `assert 'phase_pose_track' in rewards` (KeyError/False).

- [ ] **Step 3: Write minimal implementation**

Dans `src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py` :

(a) Ajouter les constantes de poses/phase juste avant `def make_microduck_ground_pick_env_cfg(` :

```python
# ── Poses cibles du geste (rad, par NOM) ──────────────────────────────────────
# STAND = HOME (default_joint_pos du modèle) — ne pas redéfinir ici : source du
# blend. DOWN = pli avant profond (bouche vers le sol), valeurs initiales tirées
# du keyframe FOLD de scene_walk.xml. ⚠️ REMPLAÇABLE par une lecture read_pose.py
# du vrai robot posé bouche-au-sol quand disponible.
DOWN_POSE = {
    "left_hip_yaw": 0.0, "left_hip_roll": 0.0, "left_hip_pitch": 1.57,
    "left_knee": 1.57, "left_ankle": 0.0,
    "neck_pitch": 1.0, "head_pitch": 1.0, "head_yaw": 0.0, "head_roll": 0.0,
    "right_hip_yaw": 0.0, "right_hip_roll": 0.0, "right_hip_pitch": -1.57,
    "right_knee": -1.57, "right_ankle": 0.0,
}

# Timing du cycle (fractions de phase), période 4 s :
#   descente [0, DESCENT_END) ~0.6s / bas [DESCENT_END, HOLD_END) ~1.4s /
#   remontée [HOLD_END, RISE_END) ~0.6s / repos [RISE_END, 1) ~1.4s
GP_PERIOD    = 4.0
DESCENT_END  = 0.15
HOLD_END     = 0.50
RISE_END     = 0.65
POSE_STD     = 0.3
```

(b) Dans la boucle de suppression des rewards (~ligne 145-155), remplacer le contenu du geste. **Retirer** les deux blocs `mouth_perpendicular_to_ground` (~176-183) et les deux `ground_pick_return_pose_*` (~189-212), et **retuner** `mouth_ground_proximity` à `weight=1.0` (~163-172, changer `weight=2.0` → `weight=1.0`).

Concrètement :
- Éditer le bloc `cfg.rewards["mouth_ground_proximity"]` : `weight=2.0` → `weight=1.0`.
- Supprimer entièrement le bloc `cfg.rewards["mouth_perpendicular_to_ground"] = RewardTermCfg(...)`.
- Supprimer les blocs `_LEG_JOINTS = [...]` / `cfg.rewards["ground_pick_return_pose_legs"]` et `_NECK_JOINTS = [...]` / `cfg.rewards["ground_pick_return_pose_neck"]`.
- Retirer `"pose"` de la liste de suppression de rewards si présent (inchangé) — mais **retirer** aussi la ligne de commentaire `# replaced by phase-conditioned ground_pick_return_pose` devenue obsolète (optionnel).

(c) Ajouter les deux nouveaux rewards de suivi de pose (à la place des blocs retirés, dans la section « main ground pick objectives ») :

```python
    # Suivi de pose interpolée par la phase (STAND<->DOWN<->STAND). Directif et
    # symétrique : le retour debout est récompensé exactement comme la descente.
    cfg.rewards["phase_pose_track"] = RewardTermCfg(
        func=microduck_mdp.phase_pose_track,
        weight=6.0,
        params={
            "command_name": "twist",
            "target_pose": DOWN_POSE,
            "std": POSE_STD,
            "descent_end": DESCENT_END,
            "hold_end": HOLD_END,
            "rise_end": RISE_END,
            "asset_cfg": SceneEntityCfg("robot"),
        },
    )
    cfg.rewards["phase_pose_track_l1"] = RewardTermCfg(
        func=microduck_mdp.phase_pose_track_l1,
        weight=2.0,
        params={
            "command_name": "twist",
            "target_pose": DOWN_POSE,
            "descent_end": DESCENT_END,
            "hold_end": HOLD_END,
            "rise_end": RISE_END,
            "asset_cfg": SceneEntityCfg("robot"),
        },
    )
```

(d) Dans le bloc « Command » (~ligne 368), passer la période et désactiver la randomisation de phase :

Remplacer :
```python
    cfg.commands["twist"] = microduck_mdp.GroundPickPhaseCommandCfg(
        **{**vars(command), "class_type": microduck_mdp.GroundPickPhaseCommand}
    )
```
par :
```python
    cfg.commands["twist"] = microduck_mdp.GroundPickPhaseCommandCfg(
        **{
            **vars(command),
            "class_type": microduck_mdp.GroundPickPhaseCommand,
            "period": GP_PERIOD,
            "randomize_phase": False,
        }
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --with pytest pytest tests/test_ground_pick_cfg.py -q`
Expected: PASS (2 passed).

Puis vérifier que l'ensemble de la suite passe :
Run: `uv run --with pytest pytest tests/ -q`
Expected: PASS (tous).

- [ ] **Step 5: Commit**

```bash
git add tests/test_ground_pick_cfg.py src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py
git commit -m "feat(ground_pick): suivi de pose interpolée par la phase (STAND->DOWN->STAND)"
```

---

### Task 5: Vérification de bout en bout (construction runtime de la tâche)

**Files:**
- Test: `tests/test_ground_pick_cfg.py` (append)

**Interfaces:**
- Consumes: tout ce qui précède.

- [ ] **Step 1: Write the failing/uncovered test**

Ajouter à `tests/test_ground_pick_cfg.py` :

```python
def test_ground_pick_rough_variant_builds():
    cfg = make_microduck_ground_pick_env_cfg(rough=True)
    assert "phase_pose_track" in cfg.rewards


def test_ground_pick_play_variant_builds():
    cfg = make_microduck_ground_pick_env_cfg(play=True)
    assert cfg.commands["twist"].randomize_phase is False
```

- [ ] **Step 2: Run to verify**

Run: `uv run --with pytest pytest tests/test_ground_pick_cfg.py -q`
Expected: PASS.

- [ ] **Step 3: Vérifier l'enregistrement de la tâche (import du package)**

Run: `uv run python -c "import mjlab_microduck.tasks; print('ok')"`
Expected: affiche les lignes `✓ ... registered` dont `GroundPick`, puis `ok`, sans exception.

- [ ] **Step 4: Commit**

```bash
git add tests/test_ground_pick_cfg.py
git commit -m "test(ground_pick): variantes rough/play + import du package"
```

---

## Self-Review

**1. Spec coverage :**
- §1 objectif directif par pose → Tasks 1,2,4. ✓
- §2 poses (STAND=HOME source, DOWN=FOLD par nom) → Task 4 (a), Task 2 (`source_pose=None`→default). ✓
- §3 profil 4 segments période 4 s + `randomize_phase=False` → Task 1, Task 3, Task 4 (a,d). ✓
- §4 fonctions mdp `phase_pose_blend/track/_l1` par nom → Tasks 1,2. ✓
- §5 rewards (ajouts + retraits + retune mouth 1.0) → Task 4 (b,c), test Task 4. ✓
- §6 déploiement (période 4, kp-ratio 1.0) → documenté dans spec ; period=4 vérifié en test Task 4. ✓
- §7 tests (fonctions pures + construction env) → Tasks 1,2,4,5. ✓
- §9 doublon `pose_target_match` hors scope → non modifié (conforme). ✓

**2. Placeholder scan :** aucun TODO/TBD ; tout le code est fourni. ✓

**3. Type consistency :** `phase_pose_track(target_pose=..., std=..., asset_cfg=...)` et `phase_pose_track_l1(target_pose=..., asset_cfg=...)` identiques entre Task 2 (def), Task 4 (appel) et tests. `randomize_phase` cohérent entre Task 3 (def) et Task 4/tests (usage). `GroundPickPhaseCommand`/`GroundPickPhaseCommandCfg` noms inchangés. ✓

```

### File: `docs/superpowers/plans/2026-07-24-shoot-pose-following.md` (774 lines, ~7637 tokens)
```md
# Tâche shoot par suivi de poses — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajouter une tâche RL `Mjlab-Shoot-Flat-MicroDuck` qui apprend un geste de shoot one-shot (jambe droite) par suivi d'une trajectoire de poses à 4 keyframes (STAND → PIED_ARRIÈRE → PIED_AVANT → STAND) interpolée par la phase.

**Architecture:** Même moule que la tâche `ground_pick` de cette branche. Une commande de phase (`GroundPickPhaseCommand`, `[cos,sin,0]`) pilote une cible articulaire interpolée entre 3 poses ; des rewards gaussien + L1 récompensent le suivi ; obs 61D unifiée pour déploiement dans un slot bouton du runtime. Aucune balle simulée.

**Tech Stack:** Python, PyTorch, mjlab 1.3.0, MuJoCo, uv, pytest.

## Global Constraints

- Obs **61D unifiée** identique aux autres policies microduck (`[gyro(3), projected_gravity(3), joint_pos(14), joint_vel(14), last_action(14), command(13)]`, head+body command zero-paddés). Ne pas casser cette forme.
- Résolution des joints **PAR NOM** (`asset.find_joints([name])`), jamais par index en dur.
- **14 joints** actifs (mouth exclu). Robot `MICRODUCK_WALK_ROBOT_CFG`.
- Ne pas modifier le runtime Rust ni la classe de commande de façon cassante : le flag `randomize_phase` ajouté DOIT défaut à `True` pour préserver `ground_pick`.
- Jambe **droite** frappe, **gauche** en appui.
- Tests : `uv run --with pytest pytest tests/ -q`.
- Convention commits : messages en français, style `feat:`/`docs:`/`test:`.

---

## File Structure

- `src/mjlab_microduck/tasks/mdp.py` — MODIFIER : ajouter `kick_pose_target` (pure), `_kick_pose_error`, `kick_pose_track`, `kick_pose_track_l1` ; ajouter le flag `randomize_phase` à `GroundPickPhaseCommand` / `GroundPickPhaseCommandCfg`.
- `src/mjlab_microduck/tasks/microduck_shoot_env_cfg.py` — CRÉER : `make_microduck_shoot_env_cfg`, `MicroduckShootRlCfg`, `STAND_POSE`/`KICK_BACK_POSE`/`KICK_FWD_POSE`, timings.
- `src/mjlab_microduck/tasks/__init__.py` — MODIFIER : import + `register_mjlab_task("Mjlab-Shoot-Flat-MicroDuck", …)`.
- `tests/test_shoot.py` — CRÉER : tests des fonctions pures (`kick_pose_target`) + rewards via stub-env.
- `tests/test_shoot_cfg.py` — CRÉER : test d'intégration (l'env se construit, bonne commande/rewards).

---

### Task 1: Flag `randomize_phase` sur la commande de phase

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py:3618-3672` (`GroundPickPhaseCommand` + `GroundPickPhaseCommandCfg`)
- Test: `tests/test_shoot.py`

**Interfaces:**
- Produces: `GroundPickPhaseCommandCfg(randomize_phase: bool = True, period: float = 4.0, …)` ; à l'exécution `reset()` met φ=0 quand `randomize_phase=False`, sinon `rand()`.

- [ ] **Step 1: Écrire le test qui échoue**

Créer `tests/test_shoot.py` avec :

```python
from mjlab_microduck.tasks.mdp import GroundPickPhaseCommandCfg


def test_phase_cmd_randomize_flag_default_true():
    cfg = GroundPickPhaseCommandCfg()
    assert cfg.randomize_phase is True


def test_phase_cmd_randomize_flag_settable_false():
    cfg = GroundPickPhaseCommandCfg(randomize_phase=False)
    assert cfg.randomize_phase is False
```

- [ ] **Step 2: Lancer le test, vérifier l'échec**

Run: `uv run --with pytest pytest tests/test_shoot.py -q`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'randomize_phase'`.

- [ ] **Step 3: Ajouter le champ au cfg + threading dans la classe**

Dans `GroundPickPhaseCommandCfg` (dataclass, ~ligne 3667) ajouter le champ :

```python
@_dataclass(kw_only=True)
class GroundPickPhaseCommandCfg(UniformVelocityCommandCfg):
    class_type: type = GroundPickPhaseCommand
    period: float = 4.0  # cycle length in seconds; sitstand uses 8.0
    randomize_phase: bool = True  # False -> chaque épisode démarre à φ=0 (STAND)

    def build(self, env: ManagerBasedRlEnv) -> "GroundPickPhaseCommand":
        return GroundPickPhaseCommand(self, env)
```

Dans `GroundPickPhaseCommand.__init__` (~ligne 3634) lire le flag :

```python
    def __init__(self, cfg, env: ManagerBasedRlEnv):
        super().__init__(cfg, env)
        self._gp_phase = torch.zeros(self.num_envs, device=self.device)
        self._period = float(getattr(cfg, "period", self.PERIOD))
        self._randomize_phase = bool(getattr(cfg, "randomize_phase", True))
```

Dans `GroundPickPhaseCommand.reset` (~ligne 3649) respecter le flag :

```python
    def reset(self, env_ids: torch.Tensor | None) -> dict:
        if env_ids is not None and len(env_ids) > 0:
            if self._randomize_phase:
                self._gp_phase[env_ids] = torch.rand(len(env_ids), device=self.device)
            else:
                self._gp_phase[env_ids] = 0.0
        return {}
```

- [ ] **Step 4: Lancer le test, vérifier le succès**

Run: `uv run --with pytest pytest tests/test_shoot.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_shoot.py
git commit -m "feat: flag randomize_phase sur GroundPickPhaseCommand (défaut True)"
```

---

### Task 2: Fonction pure `kick_pose_target`

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (ajouter près de `phase_pose_blend`, ~ligne 2062)
- Test: `tests/test_shoot.py`

**Interfaces:**
- Produces: `kick_pose_target(phase: Tensor(B,), stand, back, forward, windup_end: float, kick_end: float, return_end: float) -> Tensor(B,k)`. `stand/back/forward` sont des tenseurs `(k,)` ou `(1,k)`. Segments : [0,windup_end) STAND→BACK, [windup_end,kick_end) BACK→FORWARD, [kick_end,return_end) FORWARD→STAND, [return_end,1) STAND.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `tests/test_shoot.py` :

```python
import torch
from mjlab_microduck.tasks.mdp import kick_pose_target

W, K, R = 0.35, 0.45, 0.75  # windup_end, kick_end, return_end
STAND = torch.tensor([0.0, 0.0])
BACK = torch.tensor([1.0, -1.0])
FWD = torch.tensor([-1.0, 2.0])


def _t(phase):
    return kick_pose_target(torch.tensor([phase]), STAND, BACK, FWD, W, K, R)[0]


def test_kick_target_keypoints():
    assert torch.allclose(_t(0.0), STAND)          # début: STAND
    assert torch.allclose(_t(W), BACK)             # fin armement: BACK
    assert torch.allclose(_t(K), FWD)              # fin frappe: FORWARD
    assert torch.allclose(_t(R), STAND)            # fin retour: STAND
    assert torch.allclose(_t(0.9), STAND)          # repos: STAND


def test_kick_target_midsegments():
    assert torch.allclose(_t(W / 2), 0.5 * BACK)                    # mi-armement
    assert torch.allclose(_t((W + K) / 2), 0.5 * (BACK + FWD))      # mi-frappe
    assert torch.allclose(_t((K + R) / 2), 0.5 * FWD)              # mi-retour


def test_kick_target_batch_shape():
    phase = torch.linspace(0.0, 1.0, 50)
    out = kick_pose_target(phase, STAND, BACK, FWD, W, K, R)
    assert out.shape == (50, 2)
    # chaque composante reste dans l'enveloppe des 3 poses
    lo = torch.minimum(torch.minimum(STAND, BACK), FWD)
    hi = torch.maximum(torch.maximum(STAND, BACK), FWD)
    assert (out >= lo - 1e-6).all() and (out <= hi + 1e-6).all()
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `uv run --with pytest pytest tests/test_shoot.py -q`
Expected: FAIL — `ImportError: cannot import name 'kick_pose_target'`.

- [ ] **Step 3: Implémenter la fonction pure**

Ajouter dans `mdp.py` juste après `phase_pose_blend` (~ligne 2062) :

```python
def kick_pose_target(
    phase: torch.Tensor,
    stand: torch.Tensor,
    back: torch.Tensor,
    forward: torch.Tensor,
    windup_end: float,
    kick_end: float,
    return_end: float,
) -> torch.Tensor:
    """Cible articulaire interpolée d'un geste de shoot à 4 keyframes.

    phase (B,) ∈ [0,1). stand/back/forward (k,) ou (1,k). Retour (B,k).

    [0, windup_end)        STAND   -> BACK     (armement)
    [windup_end, kick_end) BACK    -> FORWARD  (frappe sèche)
    [kick_end, return_end) FORWARD -> STAND    (retour)
    [return_end, 1.0)      STAND             (repos)
    """
    p = phase.unsqueeze(-1)  # (B,1)

    def interp(a, b, s):
        return a + s * (b - a)

    s1 = (p / windup_end).clamp(0.0, 1.0)
    s2 = ((p - windup_end) / (kick_end - windup_end)).clamp(0.0, 1.0)
    s3 = ((p - kick_end) / (return_end - kick_end)).clamp(0.0, 1.0)

    seg1 = interp(stand, back, s1)
    seg2 = interp(back, forward, s2)
    seg3 = interp(forward, stand, s3)  # à s3=1 (phase>=return_end) => STAND

    out = seg1
    out = torch.where(p >= windup_end, seg2, out)
    out = torch.where(p >= kick_end, seg3, out)
    return out
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `uv run --with pytest pytest tests/test_shoot.py -q`
Expected: PASS (tous les tests kick_target).

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_shoot.py
git commit -m "feat: kick_pose_target — cible interpolée du geste de shoot (4 keyframes)"
```

---

### Task 3: Rewards de suivi `kick_pose_track` / `kick_pose_track_l1`

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (ajouter après `kick_pose_target`)
- Test: `tests/test_shoot.py`

**Interfaces:**
- Consumes: `kick_pose_target` (Task 2).
- Produces:
  - `kick_pose_track(env, command_name="twist", stand_pose=None, back_pose=None, forward_pose=None, std=0.4, windup_end=0.35, kick_end=0.45, return_end=0.75, asset_cfg=_DEFAULT_ASSET_CFG) -> Tensor(B,)` — gaussienne `exp(-((q-cible)/std)²).mean`.
  - `kick_pose_track_l1(env, …mêmes args sauf std) -> Tensor(B,)` — `-(|q-cible|).mean`.
  - Helper `_kick_pose_error(env, asset_cfg, command_name, stand_pose, back_pose, forward_pose, windup_end, kick_end, return_end) -> (cur, target)`.

- [ ] **Step 1: Écrire le test qui échoue (stub-env)**

Ajouter à `tests/test_shoot.py` :

```python
from mjlab_microduck.tasks.mdp import kick_pose_track, kick_pose_track_l1

STAND_D = {"a": 0.0, "b": 0.0}
BACK_D = {"a": 1.0, "b": -1.0}
FWD_D = {"a": -1.0, "b": 2.0}
_IDX = {"a": 0, "b": 1}


class _FakeData:
    def __init__(self, joint_pos):
        self.joint_pos = joint_pos
        self.default_joint_pos = torch.zeros_like(joint_pos)


class _FakeAsset:
    def __init__(self, joint_pos):
        self.data = _FakeData(joint_pos)

    def find_joints(self, names):
        return ([_IDX[names[0]]], names)


class _FakeScene:
    def __init__(self, asset):
        self._a = asset

    def __getitem__(self, name):
        return self._a


class _FakeCmdMgr:
    def __init__(self, cmd):
        self._cmd = cmd

    def get_command(self, name):
        return self._cmd


class _FakeEnv:
    def __init__(self, joint_pos, phase):
        self.scene = _FakeScene(_FakeAsset(joint_pos))
        # cmd = [cos, sin, 0]
        cmd = torch.stack(
            [torch.cos(2 * torch.pi * phase), torch.sin(2 * torch.pi * phase),
             torch.zeros_like(phase)], dim=-1)
        self.command_manager = _FakeCmdMgr(cmd)
        self.device = "cpu"
        self.num_envs = joint_pos.shape[0]


def test_kick_track_perfect_at_stand_phase():
    # phase=0 -> cible STAND=[0,0] ; joint_pos exactement STAND -> reward ~1
    env = _FakeEnv(torch.tensor([[0.0, 0.0]]), torch.tensor([0.0]))
    r = kick_pose_track(env, stand_pose=STAND_D, back_pose=BACK_D, forward_pose=FWD_D)
    assert torch.allclose(r, torch.tensor([1.0]), atol=1e-4)


def test_kick_track_lower_when_off_target():
    # phase=0.45 (kick_end) -> cible FORWARD=[-1,2] ; joint_pos=STAND -> reward < 0.5
    env = _FakeEnv(torch.tensor([[0.0, 0.0]]), torch.tensor([0.45]))
    r = kick_pose_track(env, stand_pose=STAND_D, back_pose=BACK_D, forward_pose=FWD_D)
    assert (r < 0.5).all()


def test_kick_track_l1_zero_when_perfect():
    env = _FakeEnv(torch.tensor([[0.0, 0.0]]), torch.tensor([0.0]))
    r = kick_pose_track_l1(env, stand_pose=STAND_D, back_pose=BACK_D, forward_pose=FWD_D)
    assert torch.allclose(r, torch.tensor([0.0]), atol=1e-6)
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `uv run --with pytest pytest tests/test_shoot.py -q`
Expected: FAIL — `ImportError: cannot import name 'kick_pose_track'`.

- [ ] **Step 3: Implémenter helper + rewards**

Ajouter dans `mdp.py` après `kick_pose_target` :

```python
def _kick_pose_error(
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg,
    command_name: str,
    stand_pose: dict,
    back_pose: dict,
    forward_pose: dict,
    windup_end: float,
    kick_end: float,
    return_end: float,
):
    """(cur, target) pour le geste de shoot, joints résolus PAR NOM.

    Les 3 poses partagent les mêmes clés (14 joints). L'ordre des noms est
    donné par `stand_pose`.
    """
    if not stand_pose:
        raise ValueError("_kick_pose_error requires a non-empty stand_pose dict")
    asset: Entity = env.scene[asset_cfg.name]
    names = list(stand_pose.keys())
    ids = [int(asset.find_joints([n])[0][0]) for n in names]

    def vec(d):
        return torch.tensor([d[n] for n in names], device=env.device,
                            dtype=asset.data.joint_pos.dtype)

    stand_v, back_v, fwd_v = vec(stand_pose), vec(back_pose), vec(forward_pose)

    cmd = env.command_manager.get_command(command_name)
    phase = (torch.atan2(cmd[:, 1], cmd[:, 0]) / (2 * torch.pi)) % 1.0  # (B,)
    target = kick_pose_target(phase, stand_v, back_v, fwd_v,
                              windup_end, kick_end, return_end)          # (B,k)
    cur = asset.data.joint_pos[:, ids]                                   # (B,k)
    return cur, target


def kick_pose_track(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    stand_pose: Optional[dict] = None,
    back_pose: Optional[dict] = None,
    forward_pose: Optional[dict] = None,
    std: float = 0.4,
    windup_end: float = 0.35,
    kick_end: float = 0.45,
    return_end: float = 0.75,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Gaussienne sur la pose articulaire vs cible interpolée du shoot.

    Reward directif et symétrique : chaque phase impose la config articulaire
    exacte. Résolution PAR NOM.
    """
    cur, target = _kick_pose_error(
        env, asset_cfg, command_name, stand_pose or {}, back_pose or {},
        forward_pose or {}, windup_end, kick_end, return_end,
    )
    return torch.exp(-((cur - target) / std) ** 2).mean(dim=-1)


def kick_pose_track_l1(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    stand_pose: Optional[dict] = None,
    back_pose: Optional[dict] = None,
    forward_pose: Optional[dict] = None,
    windup_end: float = 0.35,
    kick_end: float = 0.45,
    return_end: float = 0.75,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Bootstrap L1 vers la cible interpolée (gradient constant, pénalité<=0)."""
    cur, target = _kick_pose_error(
        env, asset_cfg, command_name, stand_pose or {}, back_pose or {},
        forward_pose or {}, windup_end, kick_end, return_end,
    )
    return -(cur - target).abs().mean(dim=-1)
```

- [ ] **Step 4: Lancer, vérifier le succès**

Run: `uv run --with pytest pytest tests/test_shoot.py -q`
Expected: PASS (tous les tests, y compris les 3 nouveaux).

- [ ] **Step 5: Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_shoot.py
git commit -m "feat: rewards kick_pose_track + kick_pose_track_l1 (suivi du geste de shoot)"
```

---

### Task 4: Env config `microduck_shoot_env_cfg.py`

**Files:**
- Create: `src/mjlab_microduck/tasks/microduck_shoot_env_cfg.py`
- Test: (via Task 5)

**Interfaces:**
- Consumes: `kick_pose_track`, `kick_pose_track_l1` (Task 3) ; `GroundPickPhaseCommandCfg(randomize_phase=…)` (Task 1) ; `feet_grounded_reward`, `feet_flat_penalty`, `neck_action_rate_l2`, `joint_torques_l2`, `zero_command_padding`, `robot_state_is_nan`, DR events (existants dans `mdp.py`).
- Produces: `make_microduck_shoot_env_cfg(play=False, rough=False) -> ManagerBasedRlEnvCfg` ; `MicroduckShootRlCfg` ; constantes `SHOOT_PERIOD`, `WINDUP_END`, `KICK_END`, `RETURN_END`, `STAND_POSE`, `KICK_BACK_POSE`, `KICK_FWD_POSE`.

- [ ] **Step 1: Partir du fichier ground_pick comme base**

```bash
cp src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py \
   src/mjlab_microduck/tasks/microduck_shoot_env_cfg.py
```

Ce fichier fournit déjà TOUT le boilerplate sim2real à conserver tel quel : DR (CoM, head CoM, mass/inertia, friction BAM, armature, IMU misalignment obs-level, encoder-bias, pushes), le bloc obs 61D (`del base_lin_vel` actor, critic base_lin_vel, suppression `foot_height`/`height_scan`, delays/noise, `head_command`/`body_command` zero-padding), la terminaison `nan_state`, les events `expand_bam_friction_fields` / `reset_action_history`, le curriculum action_rate/CoM. On ne modifie que : robot cfg, capteurs, commande, et le bloc rewards.

- [ ] **Step 2: Adapter l'en-tête, le nom de fonction et les constantes**

Remplacer le docstring de tête par une description shoot, et juste avant `def make_microduck_ground_pick_env_cfg`, ajouter les constantes + poses (placeholders — à remplacer par lecture `read_pose.py`). Renommer la fonction en `make_microduck_shoot_env_cfg`.

```python
# ── Timings du geste (phase normalisée [0,1)) ────────────────────────────────
SHOOT_PERIOD = 2.5   # s — durée d'un cycle (doit matcher --ground-pick-period au déploiement)
WINDUP_END = 0.35    # STAND -> BACK
KICK_END = 0.45      # BACK -> FORWARD (segment court = frappe sèche)
RETURN_END = 0.75    # FORWARD -> STAND, puis repos jusqu'à 1.0

# ── Poses (rad, 14 joints, mouth exclu) ──────────────────────────────────────
# Convention: jambe droite frappe (hanche/genou droit actifs), gauche en appui.
# STAND_POSE = pose HOME du sim (HOME_FRAME / default_joint_pos) pour que φ=0
# coïncide avec la config de reset (invariant randomize_phase=False). BACK/FWD
# sont des PLACEHOLDERS jambe droite, à affiner via read_pose.py.
STAND_POSE = {
    "left_hip_yaw": 0.0, "left_hip_roll": -0.0873, "left_hip_pitch": -0.4579,
    "left_knee": -0.0049, "left_ankle": 0.4530,
    "neck_pitch": 0.3491, "head_pitch": 0.3491, "head_yaw": 0.0, "head_roll": 0.0,
    "right_hip_yaw": 0.0, "right_hip_roll": 0.0873, "right_hip_pitch": 0.4579,
    "right_knee": 0.0049, "right_ankle": -0.4530,
}
KICK_BACK_POSE = {  # armement: hanche droite en extension arrière + genou fléchi
    **STAND_POSE,
    "right_hip_pitch": -0.6,
    "right_knee": 0.8,
    "right_ankle": -0.2,
}
KICK_FWD_POSE = {  # frappe: hanche droite fléchie avant + genou tendu
    **STAND_POSE,
    "right_hip_pitch": 0.7,
    "right_knee": -0.1,
    "right_ankle": 0.1,
}
```

> NOTE au releveur de poses : remplacer ces valeurs par des lectures `read_pose.py` (couple coupé, robot posé à la main dans chaque position). Garder les 14 clés identiques dans les 3 dicts.

- [ ] **Step 3: Robot cfg et import**

Dans les imports, remplacer `MICRODUCK_GROUND_PICK_ROBOT_CFG` par `MICRODUCK_WALK_ROBOT_CFG` :

```python
from mjlab_microduck.robot.microduck_constants import MICRODUCK_WALK_ROBOT_CFG
```

Dans la fonction, la ligne d'entités :

```python
    cfg.scene.entities = {"robot": MICRODUCK_WALK_ROBOT_CFG}
```

- [ ] **Step 4: Capteurs — garder self_collision, remplacer les capteurs pied**

Remplacer la définition du capteur `feet_ground_contact` (2 pieds) par un capteur **pied gauche seul** (appui), et SUPPRIMER le capteur `head_impact_cfg` (inutile ici). Le capteur `self_collision_cfg` reste.

```python
    left_foot_ground_cfg = ContactSensorCfg(
        name="left_foot_ground_contact",
        primary=ContactMatch(
            mode="geom",
            pattern=r"^left_foot_collision$",
            entity="robot",
        ),
        secondary=ContactMatch(mode="body", pattern="terrain"),
        fields=("found", "force"),
        reduce="netforce",
        num_slots=1,
        track_air_time=True,
    )
```

Et la ligne des capteurs de scène :

```python
    cfg.scene.sensors = (left_foot_ground_cfg, self_collision_cfg)
```

Supprimer la définition de `head_impact_cfg` et toute référence (le reward `head_impact_penalty` est retiré au Step 6).

- [ ] **Step 5: Commande de phase (randomize_phase=False, période shoot)**

Remplacer le bloc commande (celui qui crée `GroundPickPhaseCommandCfg`) par :

```python
    command: UniformVelocityCommandCfg = cfg.commands["twist"]
    command.rel_standing_envs = 0.0
    command.rel_heading_envs = 0.0
    cfg.commands["twist"] = microduck_mdp.GroundPickPhaseCommandCfg(
        **{**vars(command), "class_type": microduck_mdp.GroundPickPhaseCommand}
    )
    cfg.commands["twist"].period = SHOOT_PERIOD
    cfg.commands["twist"].randomize_phase = False
```

- [ ] **Step 6: Rewards — retirer ground_pick, ajouter shoot**

Supprimer les rewards spécifiques ground_pick : `mouth_ground_proximity`, `mouth_perpendicular_to_ground`, `ground_pick_return_pose_legs`, `ground_pick_return_pose_neck`, `feet_grounded` (les 2 pieds), `head_impact_penalty`. Remplacer par le bloc shoot :

```python
    # ── Objectif : suivi de la pose interpolée du shoot ───────────────────────
    _pose_params = {
        "command_name": "twist",
        "stand_pose": STAND_POSE,
        "back_pose": KICK_BACK_POSE,
        "forward_pose": KICK_FWD_POSE,
        "windup_end": WINDUP_END,
        "kick_end": KICK_END,
        "return_end": RETURN_END,
    }
    cfg.rewards["kick_pose_track"] = RewardTermCfg(
        func=microduck_mdp.kick_pose_track,
        weight=6.0,
        params={**_pose_params, "std": 0.4},
    )
    cfg.rewards["kick_pose_l1"] = RewardTermCfg(
        func=microduck_mdp.kick_pose_track_l1,
        weight=2.0,
        params=dict(_pose_params),
    )

    # ── Équilibre / appui (jambe unique) ──────────────────────────────────────
    cfg.rewards["upright"].params["asset_cfg"].body_names = ("trunk_base",)
    cfg.rewards["upright"].weight = 2.0
    cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("trunk_base",)
    cfg.rewards["body_ang_vel"].weight = -0.05

    # Pied GAUCHE planté (appui). feet_grounded_reward avec un capteur mono-pied
    # -> found ∈ {0,1} -> reward ∈ {0,0.5} ; poids 6.0 => contribution max ~3.0.
    cfg.rewards["support_foot_grounded"] = RewardTermCfg(
        func=microduck_mdp.feet_grounded_reward,
        weight=6.0,
        params={"sensor_name": left_foot_ground_cfg.name},
    )

    # Pied gauche à plat.
    cfg.rewards["feet_flat_left"] = RewardTermCfg(
        func=microduck_mdp.feet_flat_penalty,
        weight=-1.0,
        params={"asset_cfg": SceneEntityCfg("robot", site_names=("left_foot",))},
    )

    cfg.rewards["self_collisions"] = RewardTermCfg(
        func=mdp.self_collision_cost,
        weight=-1.0,
        params={"sensor_name": self_collision_cfg.name},
    )
```

- [ ] **Step 7: Régularisation allégée (laisser passer le snap)**

Le fichier ground_pick met `action_rate_l2=-2.0`, `neck_action_rate_l2=-1.0`, `joint_torques_l2=-5e-3` + un curriculum action_rate qui finit à -2.0. Pour le shoot on allège. Remplacer ces 3 blocs par :

```python
    cfg.rewards["action_rate_l2"] = RewardTermCfg(
        func=mdp.action_rate_l2, weight=-0.5
    )
    cfg.rewards["neck_action_rate_l2"] = RewardTermCfg(
        func=microduck_mdp.neck_action_rate_l2, weight=-0.5
    )
    cfg.rewards["joint_torques_l2"] = RewardTermCfg(
        func=microduck_mdp.joint_torques_l2, weight=-1e-3
    )
```

Et alléger le curriculum action_rate (garder la structure, viser -0.5) :

```python
    cfg.curriculum["action_rate_weight"] = CurriculumTermCfg(
        func=microduck_mdp.reward_weight,
        params={
            "reward_name": "action_rate_l2",
            "weight_stages": [
                {"step": 0,        "weight": -0.2},
                {"step": 250 * 24, "weight": -0.4},
                {"step": 500 * 24, "weight": -0.5},
            ],
        },
    )
```

- [ ] **Step 8: Reset — hauteur de station debout**

Garder la **hauteur debout** `(0.12, 0.13)` — c'est la valeur de l'env velocity
(marche) ET de ground_pick. ⚠️ Ce n'est PAS un offset additif « station accroupie » :
le `pos` racine par défaut de `InitialStateCfg` est (0,0,0), donc la hauteur de reset
est z ∈ [0.12, 0.13] m **absolue** = debout (aucune chute). Vérifier/mettre :

```python
    cfg.events["reset_base"].params["pose_range"]["z"] = (0.12, 0.13)
```

(Ne PAS injecter de vitesse d'entrée — c'est un shoot debout, pas de glisse.)

- [ ] **Step 9: Renommer la RlCfg**

En bas du fichier, renommer `MicroduckGroundPickRlCfg` en `MicroduckShootRlCfg` et changer les noms d'expérience :

```python
MicroduckShootRlCfg = RslRlOnPolicyRunnerCfg(
    # … (garder actor/critic/algorithm identiques) …
    wandb_project="mjlab_microduck",
    experiment_name="shoot",
    run_name="shoot",
    save_interval=250,
    num_steps_per_env=24,
    max_iterations=20_000,
)
```

- [ ] **Step 10: Vérifier que le module s'importe**

Run: `uv run python -c "from mjlab_microduck.tasks.microduck_shoot_env_cfg import make_microduck_shoot_env_cfg, MicroduckShootRlCfg; print('ok')"`
Expected: `ok` (pas d'ImportError / NameError — en particulier plus aucune référence à `head_impact_cfg`, `MICRODUCK_GROUND_PICK_ROBOT_CFG`, ni aux rewards ground_pick supprimés).

- [ ] **Step 11: Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_shoot_env_cfg.py
git commit -m "feat: env config Mjlab-Shoot (geste de shoot par suivi de poses)"
```

---

### Task 5: Enregistrement + test d'intégration

**Files:**
- Modify: `src/mjlab_microduck/tasks/__init__.py`
- Test: `tests/test_shoot_cfg.py`

**Interfaces:**
- Consumes: `make_microduck_shoot_env_cfg`, `MicroduckShootRlCfg` (Task 4).
- Produces: tâche enregistrée `Mjlab-Shoot-Flat-MicroDuck`.

- [ ] **Step 1: Écrire le test d'intégration qui échoue**

Créer `tests/test_shoot_cfg.py` :

```python
from mjlab_microduck.tasks.microduck_shoot_env_cfg import (
    make_microduck_shoot_env_cfg,
    STAND_POSE, KICK_BACK_POSE, KICK_FWD_POSE, SHOOT_PERIOD,
)
from mjlab_microduck.tasks import mdp as microduck_mdp


def test_poses_have_same_14_keys():
    assert set(STAND_POSE) == set(KICK_BACK_POSE) == set(KICK_FWD_POSE)
    assert len(STAND_POSE) == 14
    assert "mouth" not in STAND_POSE


def test_shoot_cfg_builds_with_phase_command():
    cfg = make_microduck_shoot_env_cfg()
    twist = cfg.commands["twist"]
    assert isinstance(twist, microduck_mdp.GroundPickPhaseCommandCfg)
    assert twist.randomize_phase is False
    assert twist.period == SHOOT_PERIOD


def test_shoot_cfg_has_kick_rewards_and_no_walking():
    cfg = make_microduck_shoot_env_cfg()
    assert "kick_pose_track" in cfg.rewards
    assert "kick_pose_l1" in cfg.rewards
    assert "support_foot_grounded" in cfg.rewards
    for gone in ("track_linear_velocity", "track_angular_velocity",
                 "mouth_ground_proximity", "ground_pick_return_pose_legs"):
        assert gone not in cfg.rewards
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `uv run --with pytest pytest tests/test_shoot_cfg.py -q`
Expected: PASS possible sur les tests de poses, mais l'ensemble doit être vert seulement une fois l'env construit sans erreur ; si `make_...` lève, FAIL. (À ce stade l'import du fichier fonctionne déjà via Task 4.)

- [ ] **Step 3: Enregistrer la tâche**

Dans `src/mjlab_microduck/tasks/__init__.py`, après le bloc d'import ground_pick (~ligne 50), ajouter :

```python
from .microduck_shoot_env_cfg import (
    make_microduck_shoot_env_cfg,
    MicroduckShootRlCfg,
)
```

Après le bloc `register_mjlab_task` de GroundPick-Rough (~ligne 161), ajouter :

```python
register_mjlab_task(
    task_id="Mjlab-Shoot-Flat-MicroDuck",
    env_cfg=make_microduck_shoot_env_cfg(),
    play_env_cfg=make_microduck_shoot_env_cfg(play=True),
    rl_cfg=MicroduckShootRlCfg,
    runner_cls=MicroduckOnPolicyRunner,
)
print("✓ Shoot task registered: Mjlab-Shoot-Flat-MicroDuck")
```

- [ ] **Step 4: Lancer tout, vérifier le succès**

Run: `uv run --with pytest pytest tests/ -q`
Expected: PASS (test_shoot.py + test_shoot_cfg.py + tests existants).

- [ ] **Step 5: Vérifier l'enregistrement de la tâche**

Run: `uv run python -c "import mjlab_microduck.tasks"`
Expected: la sortie contient `✓ Shoot task registered: Mjlab-Shoot-Flat-MicroDuck`.

- [ ] **Step 6: Commit**

```bash
git add src/mjlab_microduck/tasks/__init__.py tests/test_shoot_cfg.py
git commit -m "feat: enregistre Mjlab-Shoot-Flat-MicroDuck + test d'intégration"
```

---

## Après implémentation (hors plan TDD)

1. **Relever les vraies poses** avec `read_pose.py` (STAND, PIED_ARRIÈRE, PIED_AVANT), remplacer les placeholders dans `microduck_shoot_env_cfg.py`.
2. **Entraîner** : `uv run train Mjlab-Shoot-Flat-MicroDuck --env.scene.num-envs 4096 --agent.max_iterations 8000`. Surveiller `Episode_Reward/kick_pose_track` (doit monter).
3. **Play** : script play_latest ; vérifier l'équilibre sur le pied gauche pendant la frappe.
4. **Export ONNX** + déploiement dans un slot phase (`--ground-pick shoot.onnx --ground-pick-period 2.5 --ground-pick-kp-ratio 1.0`).
5. **Réglages probables** : période/timings (snap), poids `action_rate`, et éventuel reward « vitesse pied vers l'avant » (segment frappe) si le suivi manque de punch.

## Self-review — couverture de la spec

- Fichier & enregistrement → Tasks 4, 5. ✅
- Poses placeholders 14 joints → Task 4 Step 2, testé Task 5. ✅
- Commande de phase + `randomize_phase=False` + période → Tasks 1, 4 Step 5, testé Task 5. ✅
- `kick_pose_target` + `kick_pose_track` + `kick_pose_track_l1` → Tasks 2, 3. ✅
- Équilibre/appui (upright, pied gauche planté, feet_flat gauche, self_collisions, body_ang_vel) → Task 4 Step 6. ✅
- Régularisation allégée → Task 4 Step 7. ✅
- Obs 61D parité (hérité ground_pick, conservé) → Task 4 Step 1. ✅
- Tests pures + cfg → Tasks 2, 3, 5. ✅

```

### File: `docs/superpowers/plans/2026-07-27-swizzle-head-control.md` (204 lines, ~2581 tokens)
```md
# Swizzle Head Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add operator head-pose control (Y button) to the swizzle roller task so the policy moves its head to commanded poses while staying balanced.

**Architecture:** Policy-managed head via the observation command (matches the walking `--new-cmd-obs` path). The swizzle env currently zero-pads the `head_command` obs slot; we feed a real `head_pose` command into it, reward `head_pose_tracking`, remove the two reward terms that pull the neck/head to HOME (which would fight the command), and ramp the head in LATE via a curriculum so the already-working swizzle isn't disturbed. Config-only change to one file; requires retraining.

**Tech Stack:** mjlab / mjlab_microduck task configs (Python), rsl_rl PPO. Reuses machinery already in `microduck_velocity_env_cfg.py` (`UniformPoseCommandCfg`, `head_pose_tracking`, `pose_command_range_curriculum`, `reward_weight`).

## Global Constraints

- Only the swizzle task changes: `src/mjlab_microduck/tasks/microduck_velocity_swizzle_env_cfg.py`. The stride, velocity, standup, roller-slope/crouch tasks and `mdp.py` are NOT modified.
- Keep the 61D obs layout `[twist(3), head(4), body(6)]`: replace the `head_command` slot's contents (zero-pad → real command) but keep `body_command` zero-padded (no body-pose control here).
- No new mdp functions — all reward/command/curriculum functions already exist in `microduck_mdp`.
- Runtime unchanged: the `microduck_runtime` Y button already drives the `head_command` obs slot.

---

### Task 1: Wire head-pose control into the swizzle env

**Files:**
- Modify: `src/mjlab_microduck/tasks/microduck_velocity_swizzle_env_cfg.py`
- Test: `tests/test_swizzle_head_cfg.py` (create)

**Interfaces:**
- Consumes (already exist, do not redefine):
  - `microduck_mdp.UniformPoseCommandCfg(resampling_time_range, ranges)` — head-pose command term.
  - `mdp.generated_commands` (from `mjlab.tasks.velocity`) — obs func reading a command by name; used as `params={"command_name": "head_pose"}`.
  - `microduck_mdp.head_pose_tracking` — reward `func`, params `{"command_name": "head_pose", "std": 0.5}`.
  - `microduck_mdp.reward_weight` — curriculum func, params `{"reward_name", "weight_stages": [{"step","weight"}, ...]}`.
  - `microduck_mdp.pose_command_range_curriculum` — curriculum func, params `{"command_name", "range_stages": [{"step","ranges"}, ...]}`.
- Produces: the swizzle env cfg with a `head_pose` command, a real `head_command` obs, a `head_pose_tracking` reward, `neck_joint_pos_l2` removed, the `pose` reward scoped to leg joints, and two head curricula.

- [ ] **Step 1: Write the failing test**

Create `tests/test_swizzle_head_cfg.py`:

```python
from mjlab.tasks.velocity import mdp
from mjlab_microduck.tasks.microduck_velocity_swizzle_env_cfg import (
    make_microduck_velocity_swizzle_env_cfg,
)


def test_swizzle_head_control_wired():
    cfg = make_microduck_velocity_swizzle_env_cfg()

    # Head-pose command term exists.
    assert "head_pose" in cfg.commands

    # head_command obs is the REAL command (not zero-padded) on both groups.
    for group in ("actor", "critic"):
        term = cfg.observations[group].terms["head_command"]
        assert term.func is mdp.generated_commands
        assert term.params["command_name"] == "head_pose"

    # head_pose_tracking reward exists.
    assert "head_pose_tracking" in cfg.rewards

    # The two HOME-pullers that would fight the head command are handled:
    #  - neck_joint_pos_l2 removed
    assert "neck_joint_pos_l2" not in cfg.rewards
    #  - pose reward scoped to leg joints via a negative-lookahead regex that
    #    excludes neck/head (and passive wheels)
    pose_joints = cfg.rewards["pose"].params["asset_cfg"].joint_names
    assert any(
        "(?!" in j and "neck" in j and "head" in j for j in pose_joints
    ), f"pose reward not scoped away from neck/head: {pose_joints}"

    # Late head curricula exist.
    assert "head_pose_tracking_weight" in cfg.curriculum
    assert "head_pose_range" in cfg.curriculum
```

- [ ] **Step 2: Run test to verify it fails**

Run: `MUJOCO_GL=egl uv run pytest tests/test_swizzle_head_cfg.py -v`
Expected: FAIL (head_pose command / head_pose_tracking reward absent; head_command obs is still `zero_command_padding`).

- [ ] **Step 3: Add imports to the swizzle env cfg**

In `microduck_velocity_swizzle_env_cfg.py`, extend the imports (currently `from mjlab.managers import CurriculumTermCfg, RewardTermCfg`) to add `ObservationTermCfg`, and import the velocity mdp for `generated_commands`:

```python
from mjlab.managers import CurriculumTermCfg, ObservationTermCfg, RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.velocity import mdp
```

- [ ] **Step 4: Add the head_pose command + real head_command obs + head_pose_tracking reward + neck reconciliation**

Inside `make_microduck_velocity_swizzle_env_cfg`, AFTER the existing reward/heading setup and BEFORE `return cfg`, add:

```python
    # --- Head-pose control (Y button): the policy produces the head pose ---------
    # Head-pose command (4D deltas from HOME: [neck_pitch, head_pitch, head_yaw,
    # head_roll]). Ported from the velocity env; ranges start small (widened by the
    # curriculum below). Resample every 2-5 s.
    cfg.commands["head_pose"] = microduck_mdp.UniformPoseCommandCfg(
        resampling_time_range=(2.0, 5.0),
        ranges=(
            (-0.05, 0.05),    # neck_pitch
            (-0.05, 0.05),    # head_pitch
            (-0.07, 0.07),    # head_yaw
            (-0.015, 0.015),  # head_roll (tighter — small mechanical range)
        ),
    )

    # Feed the REAL head command into the obs (replaces zero_command_padding) on
    # both groups. body_command stays zero-padded (no body-pose control here).
    for group in ("actor", "critic"):
        cfg.observations[group].terms["head_command"] = ObservationTermCfg(
            func=mdp.generated_commands,
            params={"command_name": "head_pose"},
        )

    # Reward the head tracking its command. Weight 0 here — ramped in LATE by the
    # curriculum so it doesn't disturb the swizzle before it's solid.
    cfg.rewards["head_pose_tracking"] = RewardTermCfg(
        func=microduck_mdp.head_pose_tracking,
        weight=0.0,
        params={"command_name": "head_pose", "std": 0.5},
    )

    # Reconcile the two HOME-pullers that would fight head_pose_tracking:
    #  1) neck_joint_pos_l2 pulls the neck/head joints to HOME -> remove it.
    if "neck_joint_pos_l2" in cfg.rewards:
        del cfg.rewards["neck_joint_pos_l2"]
    #  2) the pose reward includes neck/head -> scope it to LEG joints only.
    cfg.rewards["pose"].params["asset_cfg"] = SceneEntityCfg(
        "robot", joint_names=(r"^(?!passive_|.*neck.*|.*head.*).*",)
    )
```

- [ ] **Step 5: Add the late head curricula**

Immediately after the block from Step 4 (still before `return cfg`):

```python
    # head_pose_tracking ramps 0 -> 4.0, staying 0 until ~1500 it. (swizzle solid),
    # so head control is added on top of a stable swizzle.
    cfg.curriculum["head_pose_tracking_weight"] = CurriculumTermCfg(
        func=microduck_mdp.reward_weight,
        params={
            "reward_name": "head_pose_tracking",
            "weight_stages": [
                {"step": 0,          "weight": 0.0},   # must match initial weight
                {"step": 1500 * 24,  "weight": 0.0},   # head off while swizzle solidifies
                {"step": 2250 * 24,  "weight": 2.0},
                {"step": 3000 * 24,  "weight": 4.0},
            ],
        },
    )
    # Head-command range widens over the SAME window (tiny until 1500, full by 3000),
    # so the commanded head barely moves early and reaches full range once the policy
    # can handle it.
    cfg.curriculum["head_pose_range"] = CurriculumTermCfg(
        func=microduck_mdp.pose_command_range_curriculum,
        params={
            "command_name": "head_pose",
            "range_stages": [
                # step,               ((neck_pitch), (head_pitch), (head_yaw),  (head_roll))
                {"step": 0,          "ranges": ((-0.05, 0.05), (-0.05, 0.05), (-0.07, 0.07), (-0.015, 0.015))},
                {"step": 1500 * 24,  "ranges": ((-0.05, 0.05), (-0.05, 0.05), (-0.07, 0.07), (-0.015, 0.015))},
                {"step": 2250 * 24,  "ranges": ((-0.55, 0.55), (-0.55, 0.55), (-0.70, 0.70), (-0.15, 0.15))},
                {"step": 3000 * 24,  "ranges": ((-1.10, 1.10), (-1.10, 1.10), (-1.40, 1.40), (-0.31, 0.31))},
            ],
        },
    )
```

- [ ] **Step 6: Run the cfg test to verify it passes**

Run: `MUJOCO_GL=egl uv run pytest tests/test_swizzle_head_cfg.py -v`
Expected: PASS.

- [ ] **Step 7: Smoke test the env end-to-end**

Run: `MUJOCO_GL=egl uv run train Mjlab-Velocity-Swizzle-MicroDuck --env.scene.num-envs 16 --agent.max-iterations 2`
Expected: no error; the reward log lists `head_pose_tracking` and no longer lists `neck_joint_pos_l2`; a `Curriculum/head_pose_tracking_weight` line appears at value 0.0.

- [ ] **Step 8: Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_velocity_swizzle_env_cfg.py tests/test_swizzle_head_cfg.py
git commit -m "swizzle: add head-pose control (Y button, policy-managed, late curriculum)"
```

---

## Notes for the full training run (not part of the task)

Because the head curriculum only finishes at ~3000 iters, train longer than the
2500 used before:

```bash
uv run train Mjlab-Velocity-Swizzle-MicroDuck --env.scene.num-envs 4096 --agent.max-iterations 3500
```

Watch: `head_pose_tracking` rises after ~1500 it.; the swizzle fall rate does NOT
spike when it kicks in. If the head disturbs the swizzle → push the kick-in later /
widen the range more slowly. If the head doesn't follow → raise the final weight.
Deploy unchanged (`--roller --new-cmd-obs`, Y button moves the head).

```

### File: `docs/superpowers/plans/2026-08-04-roller-standup.md` (1233 lines, ~14815 tokens)
```md
# Roller StandUp — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Une policy dédiée `Mjlab-RollerStandUp-Flat-MicroDuck` qui remet le microduck debout sur ses rollers après une chute (à plat ventre ou à plat dos) et qui sait tenir la station sur roues.

**Architecture:** Un seul fichier d'env nouveau, dérivé de `make_microduck_velocity_rollers_env_cfg()` — il hérite ainsi du robot rollers, des capteurs, de toute la domain randomization et de l'observation 61D (condition dure pour l'interchangeabilité au runtime). On retire les récompenses de patinage, on greffe les dix récompenses de relevé du `standup` (remappées sur les indices de joints du modèle rollers, où les roues passives sont intercalées), on remplace le reset par un départ au sol, et on inverse le curriculum de friction de roulement (roues freinées → libres) pour bootstrapper le geste avant d'imposer la physique réelle des roues.

**Tech Stack:** Python 3.12, mjlab 1.3.0, MuJoCo / mujoco-warp, rsl_rl (PPO), uv, pytest.

Spec de référence : `docs/superpowers/specs/2026-08-04-roller-standup-design.md`

## Global Constraints

- **Aucune modification** de `src/mjlab_microduck/tasks/mdp.py`, ni des envs `roller`, `roller_crouch`, `roller_slope`, `standup`, `velstand`. Toutes les fonctions mdp nécessaires existent déjà.
- **Parité d'observation 61D obligatoire** avec `make_microduck_velocity_rollers_env_cfg()` : `[gyro(3), projected_gravity(3), joint_pos(14), joint_vel(14), last_action(14), command(13)]`. Les slots `head_pose` (4) et `body_pose` (6) restent **zero-paddés**. Sans cette parité l'ONNX ne se charge pas dans un slot du runtime.
- **Indices de joints du modèle rollers** (roues passives intercalées ; vérifiés dans MuJoCo) :
  `_LEG_JOINTS = [0, 1, 2, 3, 4, 11, 12, 13, 14, 15]`, `_NECK_JOINTS = [7, 8, 9, 10]`, `_WHEEL_JOINTS = [5, 6, 16, 17]`.
  Ne **jamais** réutiliser les indices du `standup` (`[0-4, 9-13]` / `[5-8]`), qui valent pour le modèle sans roues.
- **Hauteurs mesurées** : `ROLLER_STAND_Z = 0.138`, `ROLLER_PRONE_Z = 0.075`. Ne pas les remplacer par les valeurs du `standup` (0.115 / 0.07).
- `EPISODE_LENGTH_S = 6.0`, `NUM_STEPS_PER_ENV = 24`. Les `step` des curricula s'expriment en `iters × NUM_STEPS_PER_ENV`.
- **Symétrie OFF** : `symmetry_cfg=None`. `SYMMETRY_CFG` est câblé pour l'ancien layout 51D et casse sur le 61D.
- Style du repo : commentaires en français dans les envs roller, indentation 4 espaces, `SceneEntityCfg` **reconstruit à chaque terme** (jamais un objet partagé — mjlab résout et mute ces objets en place).
- Commits simples, sans `Co-Authored-By`.
- **Pré-existant, hors périmètre** : `tests/test_wheel_glide.py` a 4 tests en échec avant ce travail (faux asset avec une regex obsolète `passive_LF_?wheel`). Ne pas les corriger, ne pas s'en alarmer. Le reste de la suite passe (46 tests).

---

## Structure des fichiers

| Fichier | Responsabilité |
|---|---|
| `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py` (créer) | Toute la config de l'env + `MicroduckRollerStandUpRlCfg`. Un seul fichier, comme tous les autres envs du repo. |
| `src/mjlab_microduck/tasks/__init__.py` (modifier) | Import + `register_mjlab_task` de la nouvelle tâche. |
| `tests/test_roller_standup_cfg.py` (créer) | Tests de construction de config + verrou des indices de joints. Pas de sim, pas de GPU (comme `test_roller_slope_cfg.py`). |
| `docs/roller_standup_policy_summary.md` (créer, Task 5) | Résumé de passation, sur le modèle de `docs/roller_slope_policy_summary.md`. |

---

## Task 1 : Squelette de l'env — dérivation, commande neutralisée, patinage retiré, enregistrement

**Files:**
- Create: `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`
- Modify: `src/mjlab_microduck/tasks/__init__.py`
- Test: `tests/test_roller_standup_cfg.py`

**Interfaces:**
- Consumes: `make_microduck_velocity_rollers_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg` (existant), `microduck_mdp.VelocityCommandCommandOnlyCfg` (existant).
- Produces: `make_microduck_roller_standup_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg` ; `MicroduckRollerStandUpRlCfg: RslRlOnPolicyRunnerCfg` ; les constantes de module `ROLLER_STAND_Z: float`, `ROLLER_PRONE_Z: float`, `EPISODE_LENGTH_S: float`, `NUM_STEPS_PER_ENV: int`, `_LEG_JOINTS: list[int]`, `_NECK_JOINTS: list[int]`, `_WHEEL_JOINTS: list[int]` ; la tâche enregistrée `"Mjlab-RollerStandUp-Flat-MicroDuck"`.

- [ ] **Step 1 : Écrire les tests qui échouent**

Créer `tests/test_roller_standup_cfg.py` :

```python
from mjlab_microduck.tasks.microduck_roller_standup_env_cfg import (
    EPISODE_LENGTH_S,
    make_microduck_roller_standup_env_cfg,
)
from mjlab_microduck.tasks.microduck_velocity_rollers_env_cfg import (
    make_microduck_velocity_rollers_env_cfg,
)

# Récompenses de PATINAGE : elles ne doivent pas survivre dans un env de relevé.
SKATING_REWARDS = (
    "wheel_speed",
    "braking",
    "skating_air_time",
    "glide",
    "single_support",
    "gait_symmetry",
    "forward_lean",
    "heading_hold",
    "feet_flat",
    "hip_roll_neutral",
    "pose",
    "com_height_target",
    "upright",
)


def test_env_builds_train_and_play():
    assert make_microduck_roller_standup_env_cfg() is not None
    assert make_microduck_roller_standup_env_cfg(play=True) is not None


def test_episode_is_short():
    # Épisode court : monter puis stabiliser, comme standup (6 s).
    cfg = make_microduck_roller_standup_env_cfg()
    assert cfg.episode_length_s == EPISODE_LENGTH_S == 6.0


def test_no_skating_rewards_survive():
    cfg = make_microduck_roller_standup_env_cfg()
    for name in SKATING_REWARDS:
        assert name not in cfg.rewards, f"reward de patinage survivante : {name}"


def test_smoothness_regularisers_kept():
    # Gardées de l'héritage roller : le relevé a besoin de douceur sim2real, mais
    # body_ang_vel doit rester LÉGER (standup documente qu'à -0.15 il gelait).
    cfg = make_microduck_roller_standup_env_cfg()
    for name in (
        "action_over_limit",
        "self_collisions",
        "body_ang_vel",
        "angular_momentum",
        "action_rate_l2",
        "neck_action_rate_l2",
        "neck_joint_pos_l2",
        "joint_torques_l2",
    ):
        assert name in cfg.rewards, f"régularisateur perdu : {name}"
    assert cfg.rewards["body_ang_vel"].weight == -0.05


def test_twist_command_is_neutralised():
    # Pas de pilotage : la policy se déploie en --standing, où le runtime laisse
    # le slot twist à zéro (cf. infer_policy.py:239).
    cfg = make_microduck_roller_standup_env_cfg()
    cmd = cfg.commands["twist"]
    assert cmd.ranges.lin_vel_x == (-0.01, 0.01)
    assert cmd.ranges.lin_vel_y == (-0.01, 0.01)
    assert cmd.ranges.ang_vel_z == (-0.05, 0.05)
    assert cmd.heading_command is False
    assert cmd.ranges.heading is None
    assert cmd.rel_standing_envs == 0.0


def test_twist_command_is_not_heading_relative():
    # L'env roller installe un RelativeHeadingVelocityCommandCfg (cmd[2] = erreur
    # de cap, calculée en interne). Ici cmd[2] doit être un vrai zéro bruité.
    from mjlab_microduck.tasks import mdp as microduck_mdp

    cfg = make_microduck_roller_standup_env_cfg()
    cmd = cfg.commands["twist"]
    assert isinstance(cmd, microduck_mdp.VelocityCommandCommandOnlyCfg)
    assert not isinstance(cmd, microduck_mdp.RelativeHeadingVelocityCommandCfg)


def test_obs_nan_policy_sanitize():
    # Un contact rare fait diverger le free-joint en NaN : on assainit l'obs
    # plutôt que de tuer l'entraînement (même choix que roller_slope).
    cfg = make_microduck_roller_standup_env_cfg()
    assert cfg.observations["actor"].nan_policy == "sanitize"
    assert cfg.observations["critic"].nan_policy == "sanitize"


def test_obs_parity_with_roller_env():
    # Parité 61D obligatoire : sinon l'ONNX ne se charge pas dans un slot runtime.
    standup = make_microduck_roller_standup_env_cfg()
    roller = make_microduck_velocity_rollers_env_cfg()
    for grp in ("actor", "critic"):
        assert list(standup.observations[grp].terms.keys()) == list(
            roller.observations[grp].terms.keys()
        ), f"layout d'observation divergent sur le groupe {grp}"


def test_terrain_is_plain_plane():
    # Hérité de l'env roller : sol plat, pas de générateur. Pas de variante rough
    # pour cette v1.
    cfg = make_microduck_roller_standup_env_cfg()
    assert cfg.scene.terrain.terrain_type == "plane"
    assert cfg.scene.terrain.terrain_generator is None


def test_task_is_registered():
    from mjlab.tasks.registry import list_tasks

    import mjlab_microduck.tasks  # noqa: F401  (l'import déclenche l'enregistrement)

    assert "Mjlab-RollerStandUp-Flat-MicroDuck" in list_tasks()
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : erreur de collecte, `ModuleNotFoundError: No module named 'mjlab_microduck.tasks.microduck_roller_standup_env_cfg'`.

- [ ] **Step 3 : Créer le fichier d'env**

Créer `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py` :

```python
"""Microduck roller standup — se relever sur rollers.

Policy DÉDIÉE épisodique : le robot démarre au sol (à plat ventre, à plat dos) ou
déjà debout, et doit se remettre debout sur ses rollers puis TENIR la station.
Portage de la recette `standup` (canard marcheur) vers le modèle rollers.

Dérive de l'env roller (`make_microduck_velocity_rollers_env_cfg`) → hérite tel
quel le robot rollers, les capteurs, toute la DR et l'observation 61D, donc
interchangeable au runtime (--new-cmd-obs). C'est le pattern de roller_slope.

Deux différences structurelles avec `standup` :
  - les roues passives sont INTERCALÉES dans l'ordre des joints → indices
    remappés (_LEG_JOINTS ci-dessous), verrouillés par
    tests/test_roller_standup_cfg.py ;
  - pas de commande head_pose : les slots head/body restent zero-paddés
    (convention de la famille roller) et la tête est tenue droite par
    neck_joint_pos_l2, qui résout par NOM.

La pièce nouvelle est le curriculum de friction de roulement, INVERSÉ (roues
freinées → libres) : les roues roulent, donc il n'y a aucune adhérence pour
pousser sur le sol. On bootstrappe avec des roues quasi bloquées puis on rampe
vers la vraie valeur. Si `standing_composite` s'écroule à un palier, le geste
« pieds adhérents » ne transfère pas et il faudra guider une technique de
patineur (appui genou, un patin à la fois).

Déploiement visé : en `--standing` face à la policy roller en `--walking`, avec
la bascule automatique sur la magnitude de la commande de vitesse
(infer_policy.py:262, seuil 0.05) ; le slot twist y est laissé à zéro
(infer_policy.py:239).
"""

import math

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.managers import (
    CurriculumTermCfg,
    EventTermCfg,
    RewardTermCfg,
)
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.rl import RslRlModelCfg, RslRlOnPolicyRunnerCfg

from mjlab_microduck.tasks import mdp as microduck_mdp
from mjlab_microduck.tasks.microduck_velocity_rollers_env_cfg import (
    make_microduck_velocity_rollers_env_cfg,
)
from mjlab_microduck.tasks.symmetry import PpoWithSymmetryCfg

# ── Hauteurs de tronc (m) ─────────────────────────────────────────────────────
# Mesurées par cinématique exacte (minimum des sommets de maillage des géoms
# collidantes, pose STAND, tronc ramené au contact) sur scene_rollers.xml :
# debout 0.1407, repos à plat ventre 0.0752, repos à plat dos 0.0475.
# Contrôle : le modèle SANS roues donne 0.1172 en cinématique contre STAND_Z=0.115
# mesuré sous charge par standup → ~2 mm d'affaissement, appliqué ici aussi.
# 0.138 tombe dans le reset_base z (0.1335–0.1435) déjà utilisé par l'env roller.
ROLLER_STAND_Z = 0.138
ROLLER_PRONE_Z = 0.075

EPISODE_LENGTH_S  = 6.0   # monter + stabiliser, comme standup
NUM_STEPS_PER_ENV = 24

# ── Indices de joints — les roues passives sont INTERCALÉES ───────────────────
# Ordre réel du modèle rollers (18 joints après le free-joint), vérifié dans
# MuJoCo via get_walk_rollers_spec().compile() :
#   0-4   left_hip_yaw, left_hip_roll, left_hip_pitch, left_knee, left_ankle
#   5-6   passive_LF_wheel, passive_LR_wheel
#   7-10  neck_pitch, head_pitch, head_yaw, head_roll
#   11-15 right_hip_yaw, right_hip_roll, right_hip_pitch, right_knee, right_ankle
#   16-17 passive_RF_wheel, passive_RR_wheel
# Le standup utilise [0-4, 9-13] / [5-8] : ce sont les indices du modèle SANS
# roues, ils ne valent PAS ici. Verrouillé par tests/test_roller_standup_cfg.py.
#
# Seul _LEG_JOINTS est consommé (par les récompenses de pose). _NECK_JOINTS et
# _WHEEL_JOINTS servent à la documentation et au test d'indices : le cou est
# résolu par NOM (neck_joint_pos_l2 appelle find_joints(r".*(neck|head).*") à
# chaque pas) et les roues par la regex ^passive_.*.
_LEG_JOINTS   = [0, 1, 2, 3, 4, 11, 12, 13, 14, 15]
_NECK_JOINTS  = [7, 8, 9, 10]
_WHEEL_JOINTS = [5, 6, 16, 17]

# Récompenses de PATINAGE de l'env roller : aucun sens quand on est par terre.
# feet_flat : les lames ne sont PAS à plat pendant la montée → combattrait le geste.
# hip_roll_neutral : se relever demande d'écarter les jambes.
# pose / com_height_target : remplacés par les cibles pose/hauteur du relevé.
# upright (gaussienne de base) : remplacée par upright_linear + upright_sharp.
_SKATING_REWARDS = (
    "wheel_speed",
    "braking",
    "skating_air_time",
    "glide",
    "single_support",
    "gait_symmetry",
    "forward_lean",
    "heading_hold",
    "feet_flat",
    "hip_roll_neutral",
    "pose",
    "com_height_target",
    "upright",
)


def make_microduck_roller_standup_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
    """Env « se relever sur rollers » : départ au sol, cible = debout sur roues."""
    cfg = make_microduck_velocity_rollers_env_cfg(play=play)

    cfg.episode_length_s = EPISODE_LENGTH_S

    # ── Récompenses de patinage retirées ─────────────────────────────────────
    for name in _SKATING_REWARDS:
        cfg.rewards.pop(name, None)

    # ── Commande : slot twist neutralisé (≈ 0) ───────────────────────────────
    # L'env roller installe un RelativeHeadingVelocityCommandCfg (cmd[2] = erreur
    # de cap calculée en interne). Ici on ne pilote rien : on repasse au
    # command-only neutralisé, comme standup. Les slots head_pose (4) et
    # body_pose (6) restent zero-paddés → parité d'obs 61D préservée.
    command = cfg.commands["twist"]
    command.rel_standing_envs = 0.0
    command.rel_heading_envs  = 0.0
    command.heading_command   = False
    command.ranges.heading    = None
    command.resampling_time_range = (EPISODE_LENGTH_S, EPISODE_LENGTH_S * 2)
    command.debug_vis = False
    command.ranges.lin_vel_x = (-0.01, 0.01)
    command.ranges.lin_vel_y = (-0.01, 0.01)
    command.ranges.ang_vel_z = (-0.05, 0.05)
    cfg.commands["twist"] = microduck_mdp.VelocityCommandCommandOnlyCfg(**vars(command))

    # ── Robustesse numérique (même choix que roller_slope) ───────────────────
    # Un contact rare (~1/25M pas) fait diverger le free-joint en NaN : on
    # assainit l'obs (→ 0) pour ne pas tuer l'entraînement, l'env fautif se reset
    # au pas suivant.
    for grp in ("actor", "critic"):
        cfg.observations[grp].nan_policy = "sanitize"

    return cfg


# ── Config du runner RL — identique à standup ─────────────────────────────────
MicroduckRollerStandUpRlCfg = RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,  # le normaliseur DOIT être baké dans l'ONNX par export.py
        distribution_cfg={
            "class_name": "GaussianDistribution",
            "init_std": 1.0,
            "std_type": "scalar",
        },
    ),
    critic=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,
    ),
    algorithm=PpoWithSymmetryCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
        # Symétrie OFF : SYMMETRY_CFG est câblé pour l'ancien layout 51D et casse
        # sur le 61D (même situation que tous les envs v1.5+).
        symmetry_cfg=None,
    ),
    wandb_project="mjlab_microduck",
    experiment_name="roller_standup",
    run_name="roller_standup",
    save_interval=250,
    num_steps_per_env=NUM_STEPS_PER_ENV,
    max_iterations=15_000,
)
```

- [ ] **Step 4 : Enregistrer la tâche**

Dans `src/mjlab_microduck/tasks/__init__.py`, ajouter l'import **après** le bloc d'import de `microduck_roller_slope_env_cfg` :

```python
from .microduck_roller_standup_env_cfg import (
    make_microduck_roller_standup_env_cfg,
    MicroduckRollerStandUpRlCfg,
)
```

Puis, tout à la fin du fichier (après l'enregistrement de `Mjlab-RollerSlope-Flat-MicroDuck`) :

```python
# Roller STANDUP — se relever sur rollers (policy dédiée, départ au sol).
register_mjlab_task(
    task_id="Mjlab-RollerStandUp-Flat-MicroDuck",
    env_cfg=make_microduck_roller_standup_env_cfg(),
    play_env_cfg=make_microduck_roller_standup_env_cfg(play=True),
    rl_cfg=MicroduckRollerStandUpRlCfg,
    runner_cls=MicroduckOnPolicyRunner,
)
print("✓ RollerStandUp task registered: Mjlab-RollerStandUp-Flat-MicroDuck")
```

- [ ] **Step 5 : Lancer les tests pour vérifier qu'ils passent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : 10 passed.

Si `test_obs_parity_with_roller_env` échoue, c'est que quelque chose a touché aux observations — le corriger avant de continuer, c'est la contrainte dure du projet.

- [ ] **Step 6 : Vérifier qu'aucun autre test ne régresse**

```bash
uv run --with pytest pytest tests/ -q
```
Attendu : `4 failed, 56 passed` — les 4 échecs sont ceux, pré-existants, de `tests/test_wheel_glide.py` (la suite était à `4 failed, 46 passed` avant ce travail). Aucun autre échec.

- [ ] **Step 7 : Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py \
        src/mjlab_microduck/tasks/__init__.py \
        tests/test_roller_standup_cfg.py
git commit -m "roller-standup: squelette de l'env (dérivé roller, twist neutralisé)"
```

---

## Task 2 : Récompenses de relevé + verrou des indices de joints

**Files:**
- Modify: `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`
- Test: `tests/test_roller_standup_cfg.py`

**Interfaces:**
- Consumes: de la Task 1 — `make_microduck_roller_standup_env_cfg`, `ROLLER_STAND_Z`, `ROLLER_PRONE_Z`, `_LEG_JOINTS`, `_NECK_JOINTS`, `_WHEEL_JOINTS`. De `mdp.py` (existant, non modifié) : `pose_target_match(target_overrides, asset_cfg, std, joint_indices)`, `pose_l1_penalty(target_overrides, asset_cfg, joint_indices)`, `height_target_gaussian(target_height, asset_cfg, std)`, `height_l1_penalty(target_height, asset_cfg)`, `com_upward_velocity(asset_cfg, max_height)`, `trunk_vertical_accel_penalty(asset_cfg)`, `body_upright_linear(asset_cfg)`, `upright_gaussian_at_height(std, height_low, height_high, asset_cfg)`, `standing_composite_score(target_height, height_std, upright_std, pose_std, joint_indices, target_overrides, asset_cfg)`, `joint_torque_rate_l2()`.
- Produces: les termes de récompense `pose_stand_legs`, `pose_stand_l1`, `height_stand`, `height_stand_sharp`, `height_stand_l1`, `com_upward_velocity`, `gentle_rise`, `upright_linear`, `upright_sharp`, `standing_composite`, `joint_torque_rate_l2` dans `cfg.rewards`.

- [ ] **Step 1 : Écrire les tests qui échouent**

Ajouter à la fin de `tests/test_roller_standup_cfg.py` :

```python
def test_joint_indices_match_actual_roller_model():
    """Verrou : les roues passives sont intercalées dans l'ordre des joints.

    Réutiliser les indices du standup ([0-4, 9-13]) donnerait des récompenses
    qui pointent sur des roues. Ce test compile le vrai MjSpec du robot rollers
    et vérifie les noms aux indices utilisés. Pur CPU, pas de sim.
    """
    import mujoco

    from mjlab_microduck.robot.microduck_constants import get_walk_rollers_spec
    from mjlab_microduck.tasks.microduck_roller_standup_env_cfg import (
        _LEG_JOINTS,
        _NECK_JOINTS,
        _WHEEL_JOINTS,
    )

    model = get_walk_rollers_spec().compile()
    articulated = [
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)
        for j in range(model.njnt)
        if model.jnt_type[j] != mujoco.mjtJoint.mjJNT_FREE
    ]

    assert [articulated[i] for i in _LEG_JOINTS] == [
        "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
        "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
    ]
    assert [articulated[i] for i in _NECK_JOINTS] == [
        "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    ]
    assert [articulated[i] for i in _WHEEL_JOINTS] == [
        "passive_LF_wheel", "passive_LR_wheel", "passive_RF_wheel", "passive_RR_wheel",
    ]
    # Aucun recouvrement, et les trois listes couvrent tous les joints.
    assert len(set(_LEG_JOINTS) | set(_NECK_JOINTS) | set(_WHEEL_JOINTS)) == len(articulated)


def test_recovery_rewards_present_with_expected_weights():
    cfg = make_microduck_roller_standup_env_cfg()
    expected = {
        "pose_stand_legs":      8.0,
        "pose_stand_l1":        5.0,
        "height_stand":         4.0,
        "height_stand_sharp":   4.0,
        "height_stand_l1":     30.0,
        "com_upward_velocity":  3.0,
        "gentle_rise":         -0.02,
        "upright_linear":       6.0,
        "upright_sharp":        6.0,
        "standing_composite":  15.0,
        "joint_torque_rate_l2": -2e-3,
    }
    for name, weight in expected.items():
        assert name in cfg.rewards, f"récompense de relevé manquante : {name}"
        assert cfg.rewards[name].weight == weight, f"poids inattendu sur {name}"


def test_recovery_rewards_use_roller_heights_not_walker_heights():
    from mjlab_microduck.tasks.microduck_roller_standup_env_cfg import (
        ROLLER_PRONE_Z,
        ROLLER_STAND_Z,
    )

    cfg = make_microduck_roller_standup_env_cfg()
    assert ROLLER_STAND_Z == 0.138  # PAS le 0.115 du modèle sans roues
    for name in ("height_stand", "height_stand_sharp", "height_stand_l1"):
        assert cfg.rewards[name].params["target_height"] == ROLLER_STAND_Z
    assert cfg.rewards["standing_composite"].params["target_height"] == ROLLER_STAND_Z
    # com_upward_velocity se coupe juste AU-DESSUS de la cible (10 mm de marge),
    # sinon la policy se gare à l'altitude de coupure sans finir la montée.
    assert cfg.rewards["com_upward_velocity"].params["max_height"] == ROLLER_STAND_Z + 0.010
    # upright_sharp est gatée entre le repos au sol et la station debout.
    assert cfg.rewards["upright_sharp"].params["height_low"] == ROLLER_PRONE_Z
    assert cfg.rewards["upright_sharp"].params["height_high"] == ROLLER_STAND_Z


def test_pose_rewards_target_legs_only_at_roller_indices():
    from mjlab_microduck.tasks.microduck_roller_standup_env_cfg import _LEG_JOINTS

    cfg = make_microduck_roller_standup_env_cfg()
    for name in ("pose_stand_legs", "pose_stand_l1", "standing_composite"):
        assert cfg.rewards[name].params["joint_indices"] == _LEG_JOINTS
        # target_overrides=None → la cible est HOME (default_joint_pos).
        assert cfg.rewards[name].params["target_overrides"] is None


def test_trunk_asset_cfgs_are_distinct_objects():
    """mjlab résout et MUTE les SceneEntityCfg en place : un objet partagé entre
    plusieurs termes provoque des indices périmés. Chaque terme doit avoir le sien.
    """
    cfg = make_microduck_roller_standup_env_cfg()
    names = (
        "height_stand", "height_stand_sharp", "height_stand_l1",
        "com_upward_velocity", "gentle_rise", "upright_linear",
        "upright_sharp", "standing_composite",
    )
    seen = [id(cfg.rewards[n].params["asset_cfg"]) for n in names]
    assert len(set(seen)) == len(seen), "asset_cfg partagé entre plusieurs termes"
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : `test_joint_indices_match_actual_roller_model` **passe** (les constantes de la Task 1 sont déjà correctes — c'est un verrou de régression, pas un test rouge) ; les 4 autres échouent avec `KeyError: 'pose_stand_legs'` ou `assert 'pose_stand_legs' in cfg.rewards`.

- [ ] **Step 3 : Ajouter les récompenses de relevé**

Dans `microduck_roller_standup_env_cfg.py`, insérer ce bloc **après** le bloc « Robustesse numérique » et **avant** le `return cfg` :

```python
    # ── Récompenses de relevé — transplant du standup, remappé ───────────────
    # Les poids viennent des itérations documentées dans
    # microduck_standup_env_cfg.py : ne les retoucher qu'avec une raison. Seuls
    # les indices de joints et les deux hauteurs changent ici.
    # NB : un SceneEntityCfg NEUF par terme — mjlab les résout et les mute en
    # place, un objet partagé donne des indices périmés.

    # Pose cible = HOME (target_overrides=None), JAMBES seulement : le cou et la
    # tête sont tenus par neck_joint_pos_l2 (hérité), qui résout par NOM.
    cfg.rewards["pose_stand_legs"] = RewardTermCfg(
        func=microduck_mdp.pose_target_match,
        weight=8.0,
        params={
            "std": 0.5,
            "joint_indices": _LEG_JOINTS,
            "target_overrides": None,
        },
    )
    # Bootstrap L1 : gradient constant même loin de HOME (la gaussienne sature).
    cfg.rewards["pose_stand_l1"] = RewardTermCfg(
        func=microduck_mdp.pose_l1_penalty,
        weight=5.0,
        params={
            "joint_indices": _LEG_JOINTS,
            "target_overrides": None,
        },
    )

    # Hauteur en trois couches : gaussienne large (tire depuis le sol),
    # gaussienne étroite (force les derniers cm, là où la large est saturée),
    # et L1 fort qui rend « rester par terre » net NÉGATIF — sans lui, la policy
    # se contente de l'optimum paresseux « immobile au sol ».
    cfg.rewards["height_stand"] = RewardTermCfg(
        func=microduck_mdp.height_target_gaussian,
        weight=4.0,
        params={
            "std": 0.04,
            "target_height": ROLLER_STAND_Z,
            "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
        },
    )
    cfg.rewards["height_stand_sharp"] = RewardTermCfg(
        func=microduck_mdp.height_target_gaussian,
        weight=4.0,
        params={
            "std": 0.015,
            "target_height": ROLLER_STAND_Z,
            "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
        },
    )
    cfg.rewards["height_stand_l1"] = RewardTermCfg(
        func=microduck_mdp.height_l1_penalty,
        weight=30.0,
        params={
            "target_height": ROLLER_STAND_Z,
            "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
        },
    )

    # Paye le MOUVEMENT de montée, pas seulement la destination : sans ça,
    # « rester assis en collectant la pose partielle » domine. La coupure est
    # 10 mm AU-DESSUS de la cible, sinon la policy se gare à l'altitude de
    # coupure et ne finit pas la montée.
    cfg.rewards["com_upward_velocity"] = RewardTermCfg(
        func=microduck_mdp.com_upward_velocity,
        weight=3.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
            "max_height": ROLLER_STAND_Z + 0.010,
        },
    )
    # Montée douce : pénalise |a_z|. Compatible avec com_upward_velocity — une
    # vitesse verticale constante collecte l'une ET a a_z = 0 → les deux
    # pressions sélectionnent ensemble une montée lisse à vitesse constante.
    cfg.rewards["gentle_rise"] = RewardTermCfg(
        func=microduck_mdp.trunk_vertical_accel_penalty,
        weight=-0.02,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",))},
    )

    # Tronc vertical en deux couches : cos(tilt) a un fort gradient quand on est
    # couché mais s'essouffle près de la verticale ; la gaussienne serrée gatée
    # en hauteur prend le relais et tue le penché-arrière (mode d'échec du
    # standup : basculer en arrière en tendant les jambes).
    cfg.rewards["upright_linear"] = RewardTermCfg(
        func=microduck_mdp.body_upright_linear,
        weight=6.0,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",))},
    )
    cfg.rewards["upright_sharp"] = RewardTermCfg(
        func=microduck_mdp.upright_gaussian_at_height,
        weight=6.0,
        params={
            "std": 0.3,
            "height_low": ROLLER_PRONE_Z,
            "height_high": ROLLER_STAND_Z,
            "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
        },
    )

    # Score MULTIPLICATIF hauteur × verticalité × pose : comme les facteurs se
    # multiplient, être bon sur 2 critères sur 3 ne rapporte rien → casse les
    # compromis « penché à la bonne hauteur » que les récompenses additives
    # laissent passer. Stds volontairement LARGES pour rester visible pendant la
    # montée (des stds serrées donnaient un score ~5e-5, donc zéro gradient).
    cfg.rewards["standing_composite"] = RewardTermCfg(
        func=microduck_mdp.standing_composite_score,
        weight=15.0,
        params={
            "target_height": ROLLER_STAND_Z,
            "height_std": 0.04,
            "upright_std": 0.40,
            "pose_std": 0.40,
            "joint_indices": _LEG_JOINTS,
            "target_overrides": None,
            "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
        },
    )

    # Anti-jitter : pénalise la VARIATION de couple, pas son amplitude ni la
    # rotation du tronc → amortit la tremblote sans bloquer le retournement.
    # Le standup l'a identifié comme le seul amortisseur qui ne tue pas le
    # relevé depuis le dos.
    cfg.rewards["joint_torque_rate_l2"] = RewardTermCfg(
        func=microduck_mdp.joint_torque_rate_l2,
        weight=-2e-3,
    )
```

- [ ] **Step 4 : Lancer les tests pour vérifier qu'ils passent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : 15 passed.

- [ ] **Step 5 : Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py \
        tests/test_roller_standup_cfg.py
git commit -m "roller-standup: recompenses de relevé + verrou des indices de joints"
```

---

## Task 3 : Départ au sol — reset, suppression de `fell_over`, curriculum des poses

**Files:**
- Modify: `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`
- Test: `tests/test_roller_standup_cfg.py`

**Interfaces:**
- Consumes: `microduck_mdp.set_random_ground_state(env, env_ids, asset_cfg, face_down_prob, face_up_prob, sitting_prob, standing_prob, prone_z_min, prone_z_max, sitting_z_min, sitting_z_max, standing_z_min, standing_z_max, sitting_joint_overrides, sitting_joint_noise_std, sitting_tilt_max)` et `microduck_mdp.event_param_curriculum(env, env_ids, event_name, param_stages)` — existants, non modifiés.
- Produces: l'événement `cfg.events["set_ground_state"]` et le curriculum `cfg.curriculum["ground_state_mix"]` ; `cfg.terminations` sans `fell_over`.

- [ ] **Step 1 : Écrire les tests qui échouent**

Ajouter à la fin de `tests/test_roller_standup_cfg.py` :

```python
def test_starts_from_ground_states():
    # Ventre + dos + debout. Pas de bucket "assis" : il n'existait dans standup
    # que pour le hand-off depuis la policy sit, dont il n'y a pas d'équivalent
    # roller — et ses sitting_joint_overrides sont des indices du modèle SANS roues.
    cfg = make_microduck_roller_standup_env_cfg()
    assert "set_ground_state" in cfg.events
    params = cfg.events["set_ground_state"].params
    assert params["sitting_prob"] == 0.0
    assert params["sitting_joint_overrides"] is None
    assert params["face_down_prob"] > 0.0
    assert params["standing_prob"] > 0.0
    # face_up (le dos) démarre à 0 : introduit tard par le curriculum.
    assert params["face_up_prob"] == 0.0


def test_ground_state_heights_are_roller_specific():
    cfg = make_microduck_roller_standup_env_cfg()
    params = cfg.events["set_ground_state"].params
    # Repos au sol : géométrie identique aux deux modèles (c'est la coque du
    # tronc qui touche, pas les pieds) → plages du standup réutilisées.
    assert (params["prone_z_min"], params["prone_z_max"]) == (0.05, 0.09)
    # [Corrigé à 0.076 après la revue finale — voir docs/superpowers/specs/2026-08-04-roller-standup-design.md]
    # Debout : hauteur ROLLER (+23 mm vs le modèle sans roues, qui est à 0.11–0.12).
    assert params["standing_z_min"] == 0.134
    assert params["standing_z_max"] == 0.144
    assert params["standing_z_min"] < 0.138 < params["standing_z_max"]


def test_ground_state_event_runs_after_base_reset():
    # set_ground_state écrase la pose posée par reset_base / reset_robot_joints :
    # l'ordre des événements suit l'ordre d'insertion, il doit donc venir APRÈS.
    cfg = make_microduck_roller_standup_env_cfg()
    order = list(cfg.events.keys())
    assert order.index("set_ground_state") > order.index("reset_base")
    assert order.index("set_ground_state") > order.index("reset_robot_joints")


def test_no_fall_termination():
    # Le robot DÉMARRE tombé : une terminaison sur inclinaison tuerait l'épisode
    # au premier pas. nan_state (hérité) reste, lui.
    cfg = make_microduck_roller_standup_env_cfg()
    assert "fell_over" not in cfg.terminations
    assert "nan_state" in cfg.terminations


def test_ground_state_curriculum_ramps_easy_to_hard():
    cfg = make_microduck_roller_standup_env_cfg()
    assert "ground_state_mix" in cfg.curriculum
    stages = cfg.curriculum["ground_state_mix"].params["param_stages"]
    assert cfg.curriculum["ground_state_mix"].params["event_name"] == "set_ground_state"
    # Les steps sont croissants et démarrent à 0.
    steps = [s["step"] for s in stages]
    assert steps[0] == 0 and steps == sorted(steps) and len(set(steps)) == len(steps)
    # Le dos (face_up) est introduit tard puis croît de façon monotone.
    face_up = [s["params"]["face_up_prob"] for s in stages]
    assert face_up[0] == 0.0
    assert face_up == sorted(face_up)
    assert face_up[-1] >= 0.35
    # Chaque palier est une distribution valide, et le "déjà debout" ne disparaît
    # jamais (sinon la policy se relève puis retombe faute d'apprendre à tenir).
    for stage in stages:
        p = stage["params"]
        total = (
            p["standing_prob"] + p["sitting_prob"]
            + p["face_down_prob"] + p["face_up_prob"]
        )
        assert abs(total - 1.0) < 1e-9
        assert p["sitting_prob"] == 0.0
        assert p["standing_prob"] > 0.0
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : les 5 nouveaux échouent — `assert 'set_ground_state' in cfg.events` (KeyError / AssertionError), `assert 'fell_over' not in cfg.terminations`, `assert 'ground_state_mix' in cfg.curriculum`.

- [ ] **Step 3 : Ajouter le reset au sol, la suppression de `fell_over` et le curriculum**

Dans `microduck_roller_standup_env_cfg.py`, insérer ce bloc **après** les récompenses de relevé et **avant** le `return cfg` :

```python
    # ── Départ AU SOL : à plat ventre / à plat dos / déjà debout ─────────────
    # Ajouté en DERNIER dans cfg.events : l'ordre d'exécution suit l'ordre
    # d'insertion, et ce terme doit écraser la pose posée par reset_base /
    # reset_robot_joints.
    # Le bucket « déjà debout » n'est pas décoratif : sans lui la policy apprend
    # à monter mais pas à TENIR, et elle retombe juste après s'être relevée.
    # Pas de bucket « assis » → aucun sitting_joint_overrides à remapper (ceux du
    # standup sont des indices du modèle SANS roues).
    # Les probabilités ci-dessous = palier 0 du curriculum ground_state_mix.
    cfg.events["set_ground_state"] = EventTermCfg(
        func=microduck_mdp.set_random_ground_state,
        mode="reset",
        params={
            "face_down_prob": 0.50,   # ventre (+90° de pitch)
            "face_up_prob":   0.00,   # dos — le plus dur, introduit tard
            "sitting_prob":   0.00,
            "standing_prob":  0.50,
            "sitting_joint_overrides": None,
            # Repos au sol : mesuré à 0.075 (ventre) / 0.048 (dos), identique aux
            # deux modèles — c'est la coque du tronc qui touche, pas les pieds.
            "prone_z_min":    0.05,
            # [Corrigé à 0.076 après la revue finale — voir docs/superpowers/specs/2026-08-04-roller-standup-design.md]
            "prone_z_max":    0.09,
            # Debout sur roues : ROLLER_STAND_Z = 0.138 (contre 0.11–0.12 sans roues).
            "standing_z_min": 0.134,
            "standing_z_max": 0.144,
            # Bruit de pitch/roll au départ. Attention : dans
            # set_random_ground_state le bucket « debout » réutilise le quaternion
            # du bucket « assis », donc ce bruit s'applique AUSSI aux départs
            # debout — c'est voulu (pas de sur-apprentissage du parfaitement droit).
            "sitting_tilt_max": math.radians(10),
        },
    )

    # Le robot DÉMARRE tombé → la terminaison sur inclinaison n'a aucun sens ici
    # (elle tuerait l'épisode au premier pas). nan_state, hérité, reste.
    cfg.terminations.pop("fell_over", None)

    # Curriculum des poses de départ, easy → hard. Avec un mélange plat dès le
    # départ, la policy optimise la majorité facile et laisse le dos sous-entraîné
    # (leçon du standup : il gelait en « ne rien faire » sur cette pose). On
    # introduit donc debout+ventre d'abord, le dos tard, et on biaise vers les
    # poses dures à la fin pour qu'elles reçoivent le plus d'entraînement.
    cfg.curriculum["ground_state_mix"] = CurriculumTermCfg(
        func=microduck_mdp.event_param_curriculum,
        params={
            "event_name": "set_ground_state",
            "param_stages": [
                {"step": 0, "params": {
                    "standing_prob": 0.50, "sitting_prob": 0.00,
                    "face_down_prob": 0.50, "face_up_prob": 0.00}},
                {"step": 600 * NUM_STEPS_PER_ENV, "params": {
                    "standing_prob": 0.35, "sitting_prob": 0.00,
                    "face_down_prob": 0.45, "face_up_prob": 0.20}},
                {"step": 1500 * NUM_STEPS_PER_ENV, "params": {
                    "standing_prob": 0.25, "sitting_prob": 0.00,
                    "face_down_prob": 0.40, "face_up_prob": 0.35}},
                {"step": 2500 * NUM_STEPS_PER_ENV, "params": {
                    "standing_prob": 0.20, "sitting_prob": 0.00,
                    "face_down_prob": 0.40, "face_up_prob": 0.40}},
            ],
        },
    )
```

- [ ] **Step 4 : Lancer les tests pour vérifier qu'ils passent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : 20 passed.

- [ ] **Step 5 : Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py \
        tests/test_roller_standup_cfg.py
git commit -m "roller-standup: depart au sol (ventre/dos/debout) + curriculum des poses"
```

---

## Task 4 : Curricula — friction de roulement inversée, poussées, action_rate

**Files:**
- Modify: `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`
- Test: `tests/test_roller_standup_cfg.py`

**Interfaces:**
- Consumes: `microduck_mdp.wheel_friction_curriculum(env, env_ids, event_name, ranges_stages)`, `microduck_mdp.push_curriculum(env, env_ids, event_name, push_stages)`, `microduck_mdp.reward_weight(env, env_ids, reward_name, weight_stages)` — existants, non modifiés. Événements hérités de l'env roller : `randomize_wheel_friction`, `push_robot`.
- Produces: `cfg.curriculum["wheel_friction"]` (décroissant), `cfg.curriculum["push_magnitude"]`, `cfg.curriculum["action_rate_weight"]` (remplacé).

- [ ] **Step 1 : Écrire les tests qui échouent**

Ajouter à la fin de `tests/test_roller_standup_cfg.py` :

```python
def test_wheel_friction_curriculum_is_decreasing():
    """La pièce nouvelle : roues FREINÉES → LIBRES.

    Les roues roulent, donc il n'y a aucune adhérence longitudinale pour pousser
    sur le sol. On bootstrappe avec des roulements quasi bloqués (le relevé se
    fait comme avec des pieds) puis on rampe vers la vraie valeur. L'env roller,
    lui, fait MONTER cette friction (0 → 0.0015) : le sens est bien inversé ici.
    """
    cfg = make_microduck_roller_standup_env_cfg()
    stages = cfg.curriculum["wheel_friction"].params["ranges_stages"]
    assert cfg.curriculum["wheel_friction"].params["event_name"] == "randomize_wheel_friction"

    steps = [s["step"] for s in stages]
    assert steps[0] == 0 and steps == sorted(steps) and len(set(steps)) == len(steps)

    lows = [s["ranges"][0] for s in stages]
    assert lows == sorted(lows, reverse=True), "la friction doit DÉCROÎTRE"
    assert lows[0] >= 0.02, "départ franchement freiné pour bootstrapper le geste"
    # Arrivée sur la vraie valeur du roulement (celle de l'env roller).
    assert stages[-1]["ranges"] == (0.0015, 0.0015)
    for stage in stages:
        assert stage["ranges"][0] == stage["ranges"][1]


def test_wheel_friction_event_starts_at_stage_zero():
    # Le curriculum n'est évalué qu'à partir du premier pas : sans ça les tout
    # premiers resets utiliseraient la valeur (0, 0) héritée de l'env roller,
    # soit des roues LIBRES pendant le bootstrap — exactement l'inverse du but.
    cfg = make_microduck_roller_standup_env_cfg()
    stage0 = cfg.curriculum["wheel_friction"].params["ranges_stages"][0]["ranges"]
    assert cfg.events["randomize_wheel_friction"].params["ranges"] == stage0


def test_action_rate_ramp_is_the_standup_one_not_the_roller_one():
    # L'env roller monte à -2.0 (gait calme) : c'est un bloqueur de mouvement,
    # il ralentit l'action rapide dont le relevé depuis le dos a besoin. On
    # reprend la rampe du standup, qui plafonne à -1.0.
    cfg = make_microduck_roller_standup_env_cfg()
    weights = [
        s["weight"] for s in cfg.curriculum["action_rate_weight"].params["weight_stages"]
    ]
    assert weights == [-0.4, -0.8, -1.0]
    assert cfg.rewards["action_rate_l2"].weight == -0.6


def test_push_curriculum_ramps_from_zero():
    # Poussées héritées (±0.2 m/s), mais rampées : une bourrade dès le pas 0
    # parasite le bootstrap du relevé.
    cfg = make_microduck_roller_standup_env_cfg()
    assert "push_robot" in cfg.events
    stages = cfg.curriculum["push_magnitude"].params["push_stages"]
    assert cfg.curriculum["push_magnitude"].params["event_name"] == "push_robot"
    assert stages[0]["velocity_range"]["x"] == (0.0, 0.0)
    assert stages[-1]["velocity_range"]["x"] == (-0.2, 0.2)
    highs = [s["velocity_range"]["x"][1] for s in stages]
    assert highs == sorted(highs), "la poussée doit CROÎTRE"


def test_inherited_dr_curricula_survive():
    # La DR héritée de l'env roller ne doit pas avoir été perdue en chemin.
    cfg = make_microduck_roller_standup_env_cfg()
    for name in ("com_range", "head_com_range"):
        assert name in cfg.curriculum, f"curriculum de DR perdu : {name}"
    for name in (
        "randomize_com",
        "randomize_head_com",
        "randomize_armature",
        "randomize_joint_friction",
        "randomize_mass_inertia",
        "randomize_wheel_friction",
        "encoder_bias",
    ):
        assert name in cfg.events, f"événement de DR perdu : {name}"
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : `test_wheel_friction_curriculum_is_decreasing` échoue sur `assert lows == sorted(lows, reverse=True)` (l'env roller monte 0 → 0.0015), `test_wheel_friction_event_starts_at_stage_zero` échoue, `test_action_rate_ramp_is_the_standup_one_not_the_roller_one` échoue sur `[-1.0, -1.5, -2.0] != [-0.4, -0.8, -1.0]`, `test_push_curriculum_ramps_from_zero` échoue sur `KeyError: 'push_magnitude'`. `test_inherited_dr_curricula_survive` passe déjà (vérification de non-régression).

- [ ] **Step 3 : Remplacer les curricula**

Dans `microduck_roller_standup_env_cfg.py`, insérer ce bloc **après** le curriculum `ground_state_mix` et **avant** le `return cfg` :

```python
    # ── Friction de roulement INVERSÉE : freinées → libres ───────────────────
    # C'est la seule pièce vraiment nouvelle de cet env, et le cœur de la
    # difficulté : les roues roulent, donc il n'y a AUCUNE adhérence
    # longitudinale pour pousser sur le sol. L'env roller fait MONTER cette
    # friction (0 → 0.0015) ; ici on la fait DESCENDRE, pour bootstrapper le
    # geste sur un problème facile (roues quasi bloquées ≈ des pieds) avant
    # d'imposer la physique réelle du roulement.
    #
    # DIAGNOSTIC à surveiller : si Episode_Reward/standing_composite s'écroule à
    # un palier, le geste « pieds adhérents » ne transfère pas aux roues libres
    # → il faudra guider une technique de patineur (appui genou intermédiaire,
    # un patin à la fois). C'est un résultat exploitable, pas un échec.
    #
    # ATTENTION sim2real : seuls les checkpoints d'APRÈS le dernier palier
    # (iter 4000+) sont candidats au déploiement. Avant, la policy s'appuie sur
    # une friction de roulement qui n'existe pas sur le vrai robot.
    _WHEEL_FRICTION_STAGE0 = (0.0500, 0.0500)
    cfg.curriculum["wheel_friction"] = CurriculumTermCfg(
        func=microduck_mdp.wheel_friction_curriculum,
        params={
            "event_name": "randomize_wheel_friction",
            "ranges_stages": [
                {"step": 0,                        "ranges": _WHEEL_FRICTION_STAGE0},
                {"step": 1000 * NUM_STEPS_PER_ENV, "ranges": (0.0200, 0.0200)},
                {"step": 2000 * NUM_STEPS_PER_ENV, "ranges": (0.0080, 0.0080)},
                {"step": 3000 * NUM_STEPS_PER_ENV, "ranges": (0.0030, 0.0030)},
                {"step": 4000 * NUM_STEPS_PER_ENV, "ranges": (0.0015, 0.0015)},
            ],
        },
    )
    # La valeur de DÉPART de l'événement doit matcher le palier 0 : le curriculum
    # n'est évalué qu'à partir du premier pas, sinon les tout premiers resets
    # utiliseraient le (0, 0) hérité de l'env roller — des roues LIBRES pendant
    # le bootstrap, soit exactement l'inverse du but.
    cfg.events["randomize_wheel_friction"].params["ranges"] = _WHEEL_FRICTION_STAGE0

    # ── action_rate : la rampe du standup, pas celle du roller ───────────────
    # L'env roller monte à -2.0 pour un gait calme. C'est un bloqueur de
    # mouvement : il ralentit l'action rapide dont le relevé depuis le dos a
    # besoin (le standup documente qu'un action_rate trop fort tuait cette
    # récupération). La douceur est portée ici par joint_torque_rate_l2.
    cfg.rewards["action_rate_l2"].weight = -0.6
    cfg.curriculum["action_rate_weight"] = CurriculumTermCfg(
        func=microduck_mdp.reward_weight,
        params={
            "reward_name": "action_rate_l2",
            "weight_stages": [
                {"step": 0,                       "weight": -0.4},
                {"step": 250 * NUM_STEPS_PER_ENV, "weight": -0.8},
                {"step": 500 * NUM_STEPS_PER_ENV, "weight": -1.0},
            ],
        },
    )

    # ── Poussées rampées ────────────────────────────────────────────────────
    # push_robot est hérité de l'env roller (±0.2 m/s, toutes les 3–6 s) mais
    # sans curriculum. Une bourrade dès le pas 0 parasite le bootstrap du
    # relevé : on la fait monter comme le standup.
    cfg.curriculum["push_magnitude"] = CurriculumTermCfg(
        func=microduck_mdp.push_curriculum,
        params={
            "event_name": "push_robot",
            "push_stages": [
                {"step": 0, "velocity_range": {
                    "x": (0.0, 0.0), "y": (0.0, 0.0)}},
                {"step": 500 * NUM_STEPS_PER_ENV, "velocity_range": {
                    "x": (-0.08, 0.08), "y": (-0.08, 0.08)}},
                {"step": 1000 * NUM_STEPS_PER_ENV, "velocity_range": {
                    "x": (-0.2, 0.2), "y": (-0.2, 0.2)}},
            ],
        },
    )
```

- [ ] **Step 4 : Lancer les tests pour vérifier qu'ils passent**

```bash
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```
Attendu : 25 passed.

- [ ] **Step 5 : Vérifier qu'aucun autre test ne régresse**

```bash
uv run --with pytest pytest tests/ -q
```
Attendu : `4 failed, 71 passed` — uniquement les 4 échecs pré-existants de `tests/test_wheel_glide.py`.

- [ ] **Step 6 : Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py \
        tests/test_roller_standup_cfg.py
git commit -m "roller-standup: curriculum de friction de roulement inverse + pousses rampees"
```

---

## Task 5 : Vérification bout-en-bout sur GPU + doc de passation

Les tests des Tasks 1–4 sont **statiques** : ils vérifient la config, pas l'exécution. Ils ne peuvent pas attraper un `joint_indices` hors bornes, un nom de paramètre erroné passé à une fonction mdp, ou un capteur manquant. Cette tâche est le seul endroit où l'env tourne réellement.

**Files:**
- Create: `docs/roller_standup_policy_summary.md`
- (aucune modification de code attendue si tout passe)

**Interfaces:**
- Consumes: la tâche enregistrée `Mjlab-RollerStandUp-Flat-MicroDuck` (Task 1) et l'env complet (Tasks 2–4).
- Produces: rien de programmatique — un doc de passation et la confirmation que l'env tourne.

- [ ] **Step 1 : Lancer un entraînement très court**

```bash
uv run train Mjlab-RollerStandUp-Flat-MicroDuck \
  --env.scene.num-envs 64 \
  --agent.max_iterations 3 \
  --agent.logger tensorboard
```

`--agent.logger tensorboard` évite de polluer wandb avec un run jetable.

Attendu : `✓ RollerStandUp task registered: Mjlab-RollerStandUp-Flat-MicroDuck`, puis 3 itérations qui s'exécutent sans exception, avec un tableau de récompenses affichant les termes `pose_stand_legs`, `height_stand`, `standing_composite`, etc.

Erreurs plausibles et leur cause :
- `IndexError` sur `joint_pos[:, joint_indices]` → les indices de `_LEG_JOINTS` dépassent le nombre de joints ; relire Task 2.
- `TypeError: ... unexpected keyword argument` → un nom de paramètre ne correspond pas à la signature de la fonction mdp ; comparer avec le bloc **Interfaces** de la Task 2.
- `KeyError` sur un nom de capteur → une récompense retirée était la seule à utiliser un capteur, ou une récompense gardée en réclame un absent.

- [ ] **Step 2 : Vérifier que les récompenses de relevé ne sont pas toutes nulles**

Dans la sortie de l'étape précédente, vérifier que `Episode_Reward/standing_composite` et `Episode_Reward/height_stand` sont **non nuls**. Une valeur exactement 0.0 sur les trois itérations signale une récompense qui ne se déclenche jamais (mauvais `asset_cfg`, mauvaise hauteur cible).

- [ ] **Step 3 : Vérifier visuellement le départ au sol**

```bash
uv run play Mjlab-RollerStandUp-Flat-MicroDuck --env.scene.num-envs 16
```

Attendu : les robots apparaissent **au sol** (à plat ventre) ou **debout sur leurs roues**, jamais en l'air ni traversant le sol. Aucun robot à plat dos à ce stade — c'est normal, `face_up_prob = 0` au palier 0 du curriculum, et en play le curriculum ne tourne pas.

Si des robots tombent de haut, les plages `prone_z` sont mal réglées ; si un robot traverse le sol, la pose de départ le fait spawner sous le plan.

- [ ] **Step 4 : Écrire le doc de passation**

Créer `docs/roller_standup_policy_summary.md`, sur le modèle de `docs/roller_slope_policy_summary.md` :

```markdown
# Policy `roller_standup` — se relever sur rollers

**But** : le microduck (sur rollers) part du sol — à plat ventre ou à plat dos — et se remet **debout sur ses roues**, puis **tient** la station.

- **Tâche** : `Mjlab-RollerStandUp-Flat-MicroDuck`
- **Fichier** : `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`
- **Base** : dérivée de l'env roller (`velocity_rollers`) → même robot, même physique/DR, **même observation 61D** (interchangeable au runtime, chargeable via `--new-cmd-obs`).
- **Spec** : `docs/superpowers/specs/2026-08-04-roller-standup-design.md`
- **Politique aveugle** : pas de scan de terrain ; proprioception + `projected_gravity`.

## Hauteurs (mesurées, pas devinées)

| pose | modèle pieds | modèle rollers |
|---|---|---|
| debout | 0.1172 → `STAND_Z=0.115` sous charge | 0.1407 → **`ROLLER_STAND_Z=0.138`** |
| à plat ventre (repos) | 0.075 | 0.075 |
| à plat dos (repos) | 0.048 | 0.048 |

Les hauteurs de repos au sol sont identiques aux deux modèles : c'est la coque du tronc qui touche, pas les pieds.

## ⚠️ Indices de joints — les roues sont INTERCALÉES

```
0-4   jambe gauche      5-6   roues gauches
7-10  cou / tête       11-15  jambe droite      16-17  roues droites
```
`_LEG_JOINTS = [0-4, 11-15]`. Les indices du `standup` (`[0-4, 9-13]`) valent pour le modèle **sans** roues et pointeraient sur des roues ici. Verrouillé par `tests/test_roller_standup_cfg.py::test_joint_indices_match_actual_roller_model`.

## Reset — départ au sol

`set_random_ground_state` : ventre (`prone_z` 0.05–0.09) / dos / **déjà debout** (`standing_z` 0.134–0.144), ± 10° de bruit en pitch/roll. Pas de bucket « assis ». Le bucket « debout » est nécessaire : sans lui la policy monte mais ne tient pas.

**Curriculum `ground_state_mix`** (easy → hard, le dos en dernier) :

| iter | debout | ventre | dos |
|---|---|---|---|
| 0 | 0.50 | 0.50 | 0.00 |
| 600 | 0.35 | 0.45 | 0.20 |
| 1500 | 0.25 | 0.40 | 0.35 |
| 2500 | 0.20 | 0.40 | 0.40 |

## Récompenses

Dix termes repris du `standup` avec leurs poids déjà réglés : `pose_stand_legs` (+8), `pose_stand_l1` (+5), `height_stand` (+4, std 0.04), `height_stand_sharp` (+4, std 0.015), `height_stand_l1` (+30), `com_upward_velocity` (+3), `gentle_rise` (−0.02), `upright_linear` (+6), `upright_sharp` (+6), `standing_composite` (+15). Plus `joint_torque_rate_l2` (−2e-3), l'anti-jitter qui n'empêche pas le retournement.

Régularisateurs hérités : `body_ang_vel` **−0.05** (bloqueur de mouvement, à garder LÉGER), `angular_momentum` −0.02, `action_rate_l2` (rampe −0.4 → −1.0, **pas** le −2.0 du roller), `neck_action_rate_l2` −0.5, `neck_joint_pos_l2` −0.5 (tête droite), `joint_torques_l2` −1e-3, `action_over_limit` −0.5, `self_collisions` −1.0.

Retirées : toutes les récompenses de patinage, plus `feet_flat` (les lames ne sont pas à plat pendant la montée) et `hip_roll_neutral` (se relever demande d'écarter les jambes).

## ⚠️ Le point dur : les roues roulent

Aucune adhérence longitudinale pour pousser sur le sol. Le **curriculum de friction de roulement est INVERSÉ** (l'env roller la fait monter, ici elle descend) :

| iter | frictionloss | |
|---|---|---|
| 0 | 0.05 | roues quasi bloquées → se relève comme avec des pieds |
| 1000 | 0.02 | |
| 2000 | 0.008 | |
| 3000 | 0.003 | |
| 4000 | 0.0015 | la vraie valeur du roulement |

**Surveiller `Episode_Reward/standing_composite` aux paliers.** S'il s'écroule, le geste « pieds adhérents » ne transfère pas aux roues libres → il faudra guider une technique de patineur (appui genou intermédiaire, un patin à la fois). C'est un résultat, pas un échec.

**Sim2real** : seuls les checkpoints d'après iter 4000 sont candidats au déploiement. Avant, la policy s'appuie sur une friction qui n'existe pas sur le vrai robot.

## Commande

Slot `twist` neutralisé (± 0.01), slots `head_pose` / `body_pose` **zero-paddés** (convention roller). Déploiement visé : en `--standing` face à la policy roller en `--walking`, avec la bascule automatique sur la magnitude de la commande (`infer_policy.py:262`, seuil 0.05) ; le slot twist y est laissé à zéro (`infer_policy.py:239`).

**Réserve** : `infer_policy.py` est le script de sim/clavier local. Le runtime robot est le binaire Rust `microduck_runtime`, absent du repo — il n'est pas vérifié qu'il expose un équivalent `--standing`. Le doc de passation du crouch ne liste que `--model`, `--ground-pick`, `--fold-policy`. À confirmer.

## Terminaisons

`fell_over` **supprimée** (le robot démarre tombé). `nan_state` héritée. `nan_policy="sanitize"` sur les obs actor/critic.

## Réseau / PPO

Actor et critic `(512, 256, 128)` elu, `obs_normalization=True`. PPO `lr=1e-3` adaptive, `desired_kl=0.01`, `gamma=0.99`, `lam=0.95`, `num_steps_per_env=24`, épisode 6 s, `max_iterations=15000`. **Symétrie OFF** (`SYMMETRY_CFG` est câblé pour le layout 51D).

## Commandes

```bash
uv run train Mjlab-RollerStandUp-Flat-MicroDuck --env.scene.num-envs 4096 --agent.max_iterations 15000
uv run scripts/play_latest.py        # alias md-play
uv run scripts/export_latest.py      # alias md-export
uv run --with pytest pytest tests/test_roller_standup_cfg.py -q
```

## Hors périmètre

Intégrer le relevé dans la policy de roulage (recette `velstand`) ; buckets de départ sur le côté ; variante rough ; pénalités d'impact tronc/tête.
```

- [ ] **Step 5 : Commit**

```bash
git add docs/roller_standup_policy_summary.md
git commit -m "roller-standup: doc de passation"
```

---

## Après le plan

Lancer un vrai entraînement :

```bash
uv run train Mjlab-RollerStandUp-Flat-MicroDuck --env.scene.num-envs 4096 --agent.max_iterations 15000
```

**Le signal à lire** : `Episode_Reward/standing_composite` doit monter, et surtout **son comportement aux iters 1000 / 2000 / 3000 / 4000** (les paliers de friction de roulement) répond à la question qui a motivé tout ce design — est-ce que se relever sur des roues libres est faisable avec le geste « pieds adhérents », ou faut-il enseigner une technique de patineur ?

```

### File: `docs/superpowers/plans/2026-08-04-spin-env.md` (1564 lines, ~16441 tokens)
```md
# Spin Env Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajouter une tâche RL `Mjlab-Spin-Flat-MicroDuck` qui apprend au microduck sur rollers à faire ~2 tours anti-horaire sur place à ~6 rad/s puis à s'arrêter, geste cyclique piloté par la phase du slot bouton du runtime.

**Architecture :** Nouvel env cfg qui clone la structure de `microduck_roller_crouch_env_cfg.py` (robot rollers, obs 61D, DR complète, `GroundPickPhaseCommand`) mais remplace les rewards de pose par des rewards de **résultat** (suivi d'une vitesse de lacet cible en trapèze sur la phase), plus deux amorces de *shaping* décroissantes qui poussent vers le roulement différentiel. Toutes les nouvelles fonctions de reward vont dans `src/mjlab_microduck/tasks/mdp.py`, chacune découpée en une **fonction pure sur valeurs** (testable sans simulateur) + un **wrapper env** — c'est l'idiome déjà présent dans le repo (`crouch_glide_reward_from_values`).

**Tech Stack :** Python 3.12, mjlab 1.3.0, MuJoCo / mujoco-warp, torch, rsl_rl, pytest, uv.

**Spec de référence :** `docs/superpowers/specs/2026-08-04-spin-env-design.md`

## Global Constraints

- Toutes les valeurs numériques de l'enveloppe sont fixées par le spec : `SPIN_PERIOD = 4.0` s, `SPIN_RATE_MAX = 6.0` rad/s, `SPIN_ACCEL_END = 0.125`, `SPIN_HOLD_END = 0.525`, `SPIN_BRAKE_END = 0.650`. Ne pas les changer sans changer le spec.
- Sens de rotation : **anti-horaire uniquement**, ω_z cible **positive**.
- `ENABLE_SYMMETRY = False` et `symmetry_cfg=None` : l'augmentation de symétrie G/D détruirait un spin à sens unique.
- La reward `angular_momentum` (norme 3D du moment angulaire) doit être **absente** de l'env : elle combattrait le spin.
- L'obs actor doit rester à **61 dimensions** (layout identique à roller / ground_pick / crouch), sinon l'ONNX ne charge pas dans le slot du runtime.
- Les joints sont **toujours** résolus par nom / regex via `asset.find_joints(...)`, jamais par index en dur : les 4 roues passives sont intercalées dans l'ordre des joints du modèle rollers.
- La vitesse d'entrée est injectée via `cfg.events["reset_base"].params["velocity_range"]`, **jamais** via un `push_by_setting_velocity` en `mode="reset"` (régression NaN connue).
- Style du repo : commentaires en français dans les env cfg, docstrings des fonctions `mdp.py` en anglais ou français selon le voisinage, pas de `Co-Authored-By` dans les commits.
- Lancer les tests avec `uv run --with pytest pytest tests/ -q`.

---

### Task 1 : Enveloppe de phase (fonctions pures)

Les deux fonctions purement mathématiques qui portent toute la définition du geste : le profil de vitesse de lacet cible et la porte de shaping qui s'en déduit.

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (ajouter à la fin du fichier, après `RelativeHeadingVelocityCommandCfg` et les rewards de patinage)
- Test: `tests/test_spin.py` (créer)

**Interfaces:**
- Consumes: rien (fonctions pures sur `torch.Tensor`)
- Produces:
  - `SPIN_PERIOD: float = 4.0`, `SPIN_RATE_MAX: float = 6.0`, `SPIN_ACCEL_END: float = 0.125`, `SPIN_HOLD_END: float = 0.525`, `SPIN_BRAKE_END: float = 0.650`
  - `spin_rate_by_phase(phase: torch.Tensor, rate_max: float = 6.0, accel_end: float = 0.125, hold_end: float = 0.525, brake_end: float = 0.650) -> torch.Tensor`
  - `spin_gate_by_phase(phase: torch.Tensor, rate_max: float = 6.0, accel_end: float = 0.125, hold_end: float = 0.525, brake_end: float = 0.650) -> torch.Tensor`

- [ ] **Step 1 : Écrire les tests qui échouent**

Créer `tests/test_spin.py` :

```python
import math

import torch

from mjlab_microduck.tasks import mdp

# Enveloppe du spec : accel 0.5s / régime 1.6s / freinage 0.5s / repos 1.4s sur 4s.
_ENV = dict(rate_max=6.0, accel_end=0.125, hold_end=0.525, brake_end=0.650)


def test_spin_rate_segment_boundaries():
    # bornes des 4 segments : 0 au départ, plein régime sur [accel_end, hold_end],
    # encore plein régime au tout début du freinage, 0 dès le segment de repos.
    phase = torch.tensor([0.0, 0.125, 0.30, 0.525, 0.650, 0.80, 0.999])
    w = mdp.spin_rate_by_phase(phase, **_ENV)
    expected = torch.tensor([0.0, 6.0, 6.0, 6.0, 0.0, 0.0, 0.0])
    assert torch.allclose(w, expected, atol=1e-6)


def test_spin_rate_accel_ramp_is_increasing():
    phase = torch.linspace(0.0, 0.125, 20)
    w = mdp.spin_rate_by_phase(phase, **_ENV)
    assert torch.all(w[1:] >= w[:-1])
    # milieu de la rampe de lancement -> moitié de la cible
    mid = mdp.spin_rate_by_phase(torch.tensor([0.0625]), **_ENV)
    assert torch.allclose(mid, torch.tensor([3.0]), atol=1e-6)


def test_spin_rate_brake_ramp_is_decreasing():
    phase = torch.linspace(0.525, 0.6499, 20)
    w = mdp.spin_rate_by_phase(phase, **_ENV)
    assert torch.all(w[1:] <= w[:-1])
    # milieu du freinage -> moitié de la cible
    mid = mdp.spin_rate_by_phase(torch.tensor([0.5875]), **_ENV)
    assert torch.allclose(mid, torch.tensor([3.0]), atol=1e-6)


def test_spin_rate_integral_is_two_turns():
    # LE test qui protège la cible du spec : l'aire sous l'enveloppe sur un cycle
    # de 4 s doit valoir ~4*pi rad = 2 tours. Enveloppe exacte = 12.6 rad,
    # 4*pi = 12.566 -> tolérance 1 %.
    n = 100_000
    phase = (torch.arange(n, dtype=torch.float64) + 0.5) / n
    w = mdp.spin_rate_by_phase(phase, **_ENV)
    integral = float(w.mean()) * 4.0
    assert abs(integral - 4 * math.pi) / (4 * math.pi) < 0.01


def test_spin_gate_is_normalized_rate():
    phase = torch.tensor([0.0, 0.0625, 0.30, 0.5875, 0.80])
    gate = mdp.spin_gate_by_phase(phase, **_ENV)
    rate = mdp.spin_rate_by_phase(phase, **_ENV)
    assert torch.allclose(gate, rate / 6.0, atol=1e-6)
    assert torch.all(gate >= 0.0) and torch.all(gate <= 1.0)


def test_spin_gate_is_zero_over_the_whole_rest_segment():
    # pendant le repos aucune amorce ne doit pousser au ciseau -> porte nulle,
    # c'est ce qui donne une sortie de trick propre vers la policy roller.
    phase = torch.linspace(0.650, 0.999, 50)
    gate = mdp.spin_gate_by_phase(phase, **_ENV)
    assert torch.allclose(gate, torch.zeros_like(gate), atol=1e-6)
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: FAIL avec `AttributeError: module 'mjlab_microduck.tasks.mdp' has no attribute 'spin_rate_by_phase'`

- [ ] **Step 3 : Implémenter les deux fonctions**

Ajouter à la fin de `src/mjlab_microduck/tasks/mdp.py` :

```python
# --------------------------------------------------------------------------- #
# Tâche SPIN — rotation rapide sur place sur rollers                            #
# --------------------------------------------------------------------------- #
# Enveloppe de phase : la commande du slot bouton porte une phase, qui pilote
# une VITESSE DE LACET cible en trapèze (et non une pose comme le crouch).
#   [0, accel_end)        0.5 s   0 -> rate_max    (lancement)
#   [accel_end, hold_end) 1.6 s   rate_max         (régime)
#   [hold_end, brake_end) 0.5 s   rate_max -> 0    (freinage)
#   [brake_end, 1.0)      1.4 s   0                (repos debout)
# Aire sous l'enveloppe sur un cycle de 4 s = 12.6 rad ~ 2 tours.
SPIN_PERIOD = 4.0
SPIN_RATE_MAX = 6.0
SPIN_ACCEL_END = 0.125
SPIN_HOLD_END = 0.525
SPIN_BRAKE_END = 0.650


def spin_rate_by_phase(
    phase: torch.Tensor,
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
) -> torch.Tensor:
    """Vitesse de lacet cible (rad/s, positive = anti-horaire) le long de la phase."""
    w = torch.zeros_like(phase)
    accel = phase < accel_end
    w = torch.where(accel, rate_max * phase / accel_end, w)
    hold = (phase >= accel_end) & (phase < hold_end)
    w = torch.where(hold, torch.full_like(phase, rate_max), w)
    brake = (phase >= hold_end) & (phase < brake_end)
    w = torch.where(
        brake, rate_max * (1.0 - (phase - hold_end) / (brake_end - hold_end)), w
    )
    return w


def spin_gate_by_phase(
    phase: torch.Tensor,
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
) -> torch.Tensor:
    """Porte de shaping dans [0,1] = enveloppe normalisée.

    Vaut 0 sur tout le segment de repos : les amorces (ciseau des jambes,
    différentiel des roues) ne s'appliquent que pendant lancement + régime, donc
    le robot revient en station neutre avant de rendre la main à la policy roller.
    """
    return spin_rate_by_phase(phase, rate_max, accel_end, hold_end, brake_end) / rate_max
```

- [ ] **Step 4 : Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: PASS (6 tests)

- [ ] **Step 5 : Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_spin.py
git commit -m "spin: enveloppe de phase (vitesse de lacet cible + porte de shaping)"
```

---

### Task 2 : Rewards de suivi de lacet et « sur place »

L'objectif principal (`spin_rate_track`), son bootstrap L1, et la pénalité qui garde le robot sur place. Cette tâche introduit aussi le **faux env** partagé par les tests des tâches 2 à 4, ce qui permet de tester les wrappers env sans lancer MuJoCo.

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (à la suite de la Task 1)
- Modify: `tests/test_spin.py`

**Interfaces:**
- Consumes: `spin_rate_by_phase`, `spin_gate_by_phase`, `SPIN_*` (Task 1)
- Produces:
  - `spin_phase_from_command(cmd: torch.Tensor) -> torch.Tensor`
  - `spin_rate_reward_from_values(omega_z: torch.Tensor, omega_target: torch.Tensor, std: float) -> torch.Tensor`
  - `spin_rate_track(env, command_name="twist", std=1.5, rate_max=..., accel_end=..., hold_end=..., brake_end=..., asset_cfg=_DEFAULT_ASSET_CFG) -> torch.Tensor`
  - `spin_rate_l1(env, command_name="twist", rate_max=..., accel_end=..., hold_end=..., brake_end=..., asset_cfg=_DEFAULT_ASSET_CFG) -> torch.Tensor`
  - `spin_stay_in_place(env, asset_cfg=_DEFAULT_ASSET_CFG) -> torch.Tensor`

- [ ] **Step 1 : Écrire les tests qui échouent**

Ajouter à `tests/test_spin.py` (le faux env sert aussi aux tâches 3 et 4) :

```python
# ── faux env minimal : permet de tester les wrappers de reward sans MuJoCo ────
class _FakeData:
    def __init__(self, ang_vel_b=None, lin_vel_b=None, joint_pos=None, joint_vel=None):
        self.root_link_ang_vel_b = ang_vel_b
        self.root_link_lin_vel_b = lin_vel_b
        self.joint_pos = joint_pos
        self.joint_vel = joint_vel


class _FakeEntity:
    """Entity minimale : find_joints() résout par nom depuis un dict {nom: index}."""

    def __init__(self, data, joint_ids=None):
        self.data = data
        self._joint_ids = joint_ids or {}

    def find_joints(self, pattern):
        import re

        names = list(self._joint_ids.keys())
        if isinstance(pattern, (list, tuple)):
            matched = [n for n in names if n in pattern]
        else:
            matched = [n for n in names if re.fullmatch(pattern, n)]
        assert matched, f"aucun joint ne matche {pattern!r} parmi {names}"
        return [self._joint_ids[n] for n in matched], matched


class _FakeCommandManager:
    def __init__(self, cmd):
        self._cmd = cmd

    def get_command(self, name):
        return self._cmd


class _FakeSensorData:
    def __init__(self, current_contact_time):
        self.current_contact_time = current_contact_time


class _FakeSensor:
    def __init__(self, current_contact_time):
        self.data = _FakeSensorData(current_contact_time)


class _FakeEnv:
    def __init__(self, entity, cmd=None, sensors=None):
        self.scene = {"robot": entity, **(sensors or {})}
        self.command_manager = _FakeCommandManager(cmd)
        self.device = "cpu"


def _phase_cmd(phases):
    """Commande du slot telle que la voit la policy : [cos(2*pi*phi), sin(...), 0]."""
    p = torch.as_tensor(phases, dtype=torch.float32)
    return torch.stack(
        [torch.cos(2 * math.pi * p), torch.sin(2 * math.pi * p), torch.zeros_like(p)],
        dim=-1,
    )


# ── phase recover ────────────────────────────────────────────────────────────
def test_spin_phase_from_command_roundtrip():
    phases = torch.tensor([0.0, 0.125, 0.4, 0.65, 0.9])
    got = mdp.spin_phase_from_command(_phase_cmd(phases))
    assert torch.allclose(got, phases, atol=1e-5)


# ── spin_rate_track ──────────────────────────────────────────────────────────
def test_spin_rate_reward_peaks_on_exact_match():
    w = torch.tensor([6.0, 6.0])
    target = torch.tensor([6.0, 4.5])
    r = mdp.spin_rate_reward_from_values(w, target, std=1.5)
    # erreur nulle -> 1.0 ; erreur = 1 std -> exp(-1)
    assert torch.allclose(r, torch.tensor([1.0, math.exp(-1.0)]), atol=1e-6)


def test_spin_rate_track_uses_yaw_and_phase():
    # phase 0.30 = plein régime -> cible 6 rad/s. Un robot qui tourne à 6 rad/s
    # doit toucher 1.0 ; un robot immobile doit être largement en dessous.
    ang = torch.tensor([[0.0, 0.0, 6.0], [0.0, 0.0, 0.0]])
    env = _FakeEnv(
        _FakeEntity(_FakeData(ang_vel_b=ang)), cmd=_phase_cmd([0.30, 0.30])
    )
    r = mdp.spin_rate_track(env, std=1.5)
    assert r[0] > 0.99
    assert r[1] < 0.01


def test_spin_rate_track_wants_stillness_during_rest():
    # phase 0.80 = repos -> cible 0 : tourner encore est puni, être immobile payé.
    ang = torch.tensor([[0.0, 0.0, 0.0], [0.0, 0.0, 6.0]])
    env = _FakeEnv(
        _FakeEntity(_FakeData(ang_vel_b=ang)), cmd=_phase_cmd([0.80, 0.80])
    )
    r = mdp.spin_rate_track(env, std=1.5)
    assert r[0] > 0.99
    assert r[1] < 0.01


def test_spin_rate_track_penalizes_wrong_direction():
    # tourner à -6 rad/s (horaire) quand on demande +6 doit être pire qu'immobile
    ang = torch.tensor([[0.0, 0.0, -6.0], [0.0, 0.0, 0.0]])
    env = _FakeEnv(
        _FakeEntity(_FakeData(ang_vel_b=ang)), cmd=_phase_cmd([0.30, 0.30])
    )
    r = mdp.spin_rate_track(env, std=1.5)
    assert r[0] < r[1]


# ── spin_rate_l1 ─────────────────────────────────────────────────────────────
def test_spin_rate_l1_is_negative_absolute_error():
    ang = torch.tensor([[0.0, 0.0, 6.0], [0.0, 0.0, 2.0]])
    env = _FakeEnv(
        _FakeEntity(_FakeData(ang_vel_b=ang)), cmd=_phase_cmd([0.30, 0.30])
    )
    r = mdp.spin_rate_l1(env)
    assert torch.allclose(r, torch.tensor([0.0, -4.0]), atol=1e-5)


# ── spin_stay_in_place ───────────────────────────────────────────────────────
def test_spin_stay_in_place_is_squared_planar_speed():
    lin = torch.tensor([[0.0, 0.0, 0.0], [0.3, 0.4, 9.0]])
    env = _FakeEnv(_FakeEntity(_FakeData(lin_vel_b=lin)))
    c = mdp.spin_stay_in_place(env)
    # 0.3^2 + 0.4^2 = 0.25 ; la composante z est ignorée
    assert torch.allclose(c, torch.tensor([0.0, 0.25]), atol=1e-6)
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'spin_phase_from_command'` (les 6 tests de la Task 1 continuent de passer)

- [ ] **Step 3 : Implémenter les rewards**

Ajouter à la suite dans `src/mjlab_microduck/tasks/mdp.py` :

```python
def spin_phase_from_command(cmd: torch.Tensor) -> torch.Tensor:
    """Récupère la phase [0,1) depuis la commande [cos(2πφ), sin(2πφ), 0] du slot."""
    return (torch.atan2(cmd[:, 1], cmd[:, 0]) / (2 * torch.pi)) % 1.0


def _spin_target_rate(
    env: ManagerBasedRlEnv,
    command_name: str,
    rate_max: float,
    accel_end: float,
    hold_end: float,
    brake_end: float,
) -> torch.Tensor:
    phase = spin_phase_from_command(env.command_manager.get_command(command_name))
    return spin_rate_by_phase(phase, rate_max, accel_end, hold_end, brake_end)


def _spin_gate(
    env: ManagerBasedRlEnv,
    command_name: str,
    rate_max: float,
    accel_end: float,
    hold_end: float,
    brake_end: float,
) -> torch.Tensor:
    phase = spin_phase_from_command(env.command_manager.get_command(command_name))
    return spin_gate_by_phase(phase, rate_max, accel_end, hold_end, brake_end)


def spin_rate_reward_from_values(
    omega_z: torch.Tensor, omega_target: torch.Tensor, std: float
) -> torch.Tensor:
    """Gaussienne sur l'erreur de vitesse de lacet (fonction pure, testable)."""
    return torch.exp(-(((omega_z - omega_target) / std) ** 2))


def spin_rate_track(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    std: float = 1.5,
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Objectif principal du spin : suivre la vitesse de lacet cible ω*(φ).

    ω_z est pris en repère corps (c'est ce que voit le gyro de l'IMU, donc ce que
    la policy observe). Une rotation dans le mauvais sens est plus punie que
    l'immobilité, la gaussienne étant centrée sur une cible positive.
    """
    asset: Entity = env.scene[asset_cfg.name]
    omega_z = asset.data.root_link_ang_vel_b[:, 2]
    target = _spin_target_rate(env, command_name, rate_max, accel_end, hold_end, brake_end)
    return spin_rate_reward_from_values(omega_z, target, std)


def spin_rate_l1(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
) -> torch.Tensor:
    """Bootstrap L1 : gradient constant vers la cible même quand la gaussienne
    de `spin_rate_track` sature loin de la cible. À utiliser avec un poids
    POSITIF (la valeur retournée est déjà négative)."""
    asset: Entity = env.scene[asset_cfg.name]
    omega_z = asset.data.root_link_ang_vel_b[:, 2]
    target = _spin_target_rate(env, command_name, rate_max, accel_end, hold_end, brake_end)
    return -torch.abs(omega_z - target)


def spin_stay_in_place(
    env: ManagerBasedRlEnv, asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG
) -> torch.Tensor:
    """Coût ‖v_xy‖² du tronc : tourner SUR PLACE, et tuer l'élan d'entrée.

    Pas d'état de référence (contrairement à une dérive mesurée depuis le reset),
    donc reste valide sur les 5 cycles d'un épisode. À utiliser avec un poids
    NÉGATIF."""
    asset: Entity = env.scene[asset_cfg.name]
    v_xy = asset.data.root_link_lin_vel_b[:, :2]
    return torch.sum(torch.square(v_xy), dim=1)
```

- [ ] **Step 4 : Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: PASS (13 tests)

- [ ] **Step 5 : Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_spin.py
git commit -m "spin: rewards de suivi de lacet (gaussienne + L1) et sur-place"
```

---

### Task 3 : Amorces du roulement différentiel

Les deux rewards qui injectent la physique connue : les patins roulent en sens opposés (`spin_wheel_differential`) et les deux lames restent au sol (`spin_grounded`). Toutes deux portées par la porte `gate(φ)`.

**Rappel des signes** (dérivé dans le spec) : pour une rotation anti-horaire, le patin gauche va vers l'**arrière** et le droit vers l'**avant** ; les 4 roues tournent positif en marche avant, donc **`ω_D − ω_G > 0`**.

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (à la suite de la Task 2)
- Modify: `tests/test_spin.py`

**Interfaces:**
- Consumes: `_spin_gate`, `SPIN_*` (Tasks 1-2), `_FakeEntity` / `_FakeSensor` / `_FakeEnv` (Task 2)
- Produces:
  - `spin_wheel_differential_from_values(diff: torch.Tensor, gate: torch.Tensor, omega_scale: float) -> torch.Tensor`
  - `spin_wheel_differential(env, command_name="twist", omega_scale=20.0, rate_max=..., accel_end=..., hold_end=..., brake_end=...) -> torch.Tensor`
  - `spin_grounded(env, sensor_name: str, command_name="twist", rate_max=..., accel_end=..., hold_end=..., brake_end=...) -> torch.Tensor`

- [ ] **Step 1 : Écrire les tests qui échouent**

Ajouter à `tests/test_spin.py` :

```python
# ── spin_wheel_differential ──────────────────────────────────────────────────
_WHEEL_IDS = {
    "passive_LF_wheel": 0,
    "passive_LR_wheel": 1,
    "passive_RF_wheel": 2,
    "passive_RR_wheel": 3,
}


def _wheel_env(vel_rows, phases):
    vel = torch.tensor(vel_rows, dtype=torch.float32)
    entity = _FakeEntity(_FakeData(joint_vel=vel), joint_ids=_WHEEL_IDS)
    return _FakeEnv(entity, cmd=_phase_cmd(phases))


def test_wheel_differential_rewards_counter_rolling_wheels():
    # anti-horaire : roues GAUCHE négatives (patin part en arrière), DROITE
    # positives -> omega_D - omega_G > 0 -> récompensé.
    env = _wheel_env(
        [
            [-10.0, -10.0, 10.0, 10.0],  # bon différentiel
            [10.0, 10.0, 10.0, 10.0],    # tout droit : différentiel nul
            [10.0, 10.0, -10.0, -10.0],  # différentiel inversé (horaire)
        ],
        [0.30, 0.30, 0.30],
    )
    r = mdp.spin_wheel_differential(env, omega_scale=20.0)
    assert r[0] > 0.5
    assert torch.allclose(r[1], torch.tensor(0.0), atol=1e-6)
    assert torch.allclose(r[2], torch.tensor(0.0), atol=1e-6)


def test_wheel_differential_is_gated_off_during_rest():
    # même bon différentiel, mais en phase de repos -> porte nulle -> pas payé.
    env = _wheel_env([[-10.0, -10.0, 10.0, 10.0]], [0.80])
    r = mdp.spin_wheel_differential(env, omega_scale=20.0)
    assert torch.allclose(r, torch.zeros(1), atol=1e-6)


def test_wheel_differential_saturates():
    # tanh : au-delà de omega_scale la reward sature, pas de course à la vitesse.
    env = _wheel_env(
        [[-10.0, -10.0, 10.0, 10.0], [-100.0, -100.0, 100.0, 100.0]], [0.30, 0.30]
    )
    r = mdp.spin_wheel_differential(env, omega_scale=20.0)
    assert r[1] > r[0]
    assert r[1] <= 1.0


def test_wheel_differential_from_values_is_pure():
    diff = torch.tensor([20.0, 0.0, -20.0])
    gate = torch.ones(3)
    r = mdp.spin_wheel_differential_from_values(diff, gate, omega_scale=20.0)
    expected = torch.tensor([math.tanh(1.0), 0.0, 0.0])
    assert torch.allclose(r, expected, atol=1e-6)


# ── spin_grounded ────────────────────────────────────────────────────────────
def test_spin_grounded_rewards_both_blades_down_and_is_gated():
    contact = torch.tensor([[0.2, 0.3], [0.2, 0.0], [0.0, 0.0], [0.2, 0.3]])
    entity = _FakeEntity(_FakeData())
    env = _FakeEnv(
        entity,
        cmd=_phase_cmd([0.30, 0.30, 0.30, 0.80]),
        sensors={"feet_ground_contact": _FakeSensor(contact)},
    )
    r = mdp.spin_grounded(env, sensor_name="feet_ground_contact")
    # deux lames au sol en régime -> porte 1.0 ; une seule ou zéro -> 0 ;
    # deux lames au sol mais en repos -> porte 0.
    assert torch.allclose(r, torch.tensor([1.0, 0.0, 0.0, 0.0]), atol=1e-6)
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'spin_wheel_differential'`

- [ ] **Step 3 : Implémenter les deux rewards**

Ajouter à la suite dans `src/mjlab_microduck/tasks/mdp.py` :

```python
SPIN_WHEEL_OMEGA_SCALE = 20.0  # rad/s ; voir le calibrage dans le spec


def spin_wheel_differential_from_values(
    diff: torch.Tensor, gate: torch.Tensor, omega_scale: float
) -> torch.Tensor:
    """Fonction pure : tanh du différentiel de roues, portée par gate, clampée ≥ 0."""
    return gate * torch.tanh(torch.clamp(diff, min=0.0) / omega_scale)


def spin_wheel_differential(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    omega_scale: float = SPIN_WHEEL_OMEGA_SCALE,
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
) -> torch.Tensor:
    """Récompense la rotation EN ROULEMENT (et non en patinage).

    Pour un spin anti-horaire, le patin gauche recule et le droit avance ; les 4
    roues tournant positif en marche avant, cela donne ω_D − ω_G > 0. Le tanh
    sature à `omega_scale` pour éviter la course à la vitesse de roue.
    """
    asset: Entity = env.scene["robot"]
    lf_ids, _ = asset.find_joints("passive_LF_?wheel")
    lr_ids, _ = asset.find_joints("passive_LR_?wheel")
    rf_ids, _ = asset.find_joints("passive_RF_?wheel")
    rr_ids, _ = asset.find_joints("passive_RR_?wheel")

    vel = asset.data.joint_vel
    omega_left = (vel[:, lf_ids[0]] + vel[:, lr_ids[0]]) / 2.0
    omega_right = (vel[:, rf_ids[0]] + vel[:, rr_ids[0]]) / 2.0
    gate = _spin_gate(env, command_name, rate_max, accel_end, hold_end, brake_end)
    return spin_wheel_differential_from_values(
        omega_right - omega_left, gate, omega_scale
    )


def spin_grounded(
    env: ManagerBasedRlEnv,
    sensor_name: str,
    command_name: str = "twist",
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
) -> torch.Tensor:
    """Les deux lames au sol pendant le spin — empêche « je saute et je vrille ».

    Variante de `grounded_reward` du swizzle, qui n'est pas réutilisable ici :
    elle se pondère par cmd_x, qui vaut cos(2πφ) sur la commande de phase.
    """
    from mjlab.sensor import ContactSensor

    sensor: ContactSensor = env.scene[sensor_name]
    contact_time = sensor.data.current_contact_time  # (num_envs, num_feet)
    assert contact_time is not None
    n_contact = torch.sum((contact_time > 0.0).float(), dim=1)
    grounded = (n_contact >= 2).float()
    gate = _spin_gate(env, command_name, rate_max, accel_end, hold_end, brake_end)
    return grounded * gate
```

- [ ] **Step 4 : Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: PASS (18 tests)

- [ ] **Step 5 : Mesurer la demi-voie réelle et ajuster `omega_scale`**

Le spec fixe `omega_scale = 20.0` sur une demi-voie **estimée** à 0.03 m. Mesurer la vraie valeur sur le modèle rollers, à la pose HOME :

```bash
uv run python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('src/mjlab_microduck/robot/microduck/robot_allcollisions_rollers.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
ys = {}
for name in ('left_foot', 'right_foot'):
    sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, name)
    ys[name] = d.site_xpos[sid][1]
half = abs(ys['left_foot'] - ys['right_foot']) / 2.0
print('sites y =', ys)
print('demi-voie =', round(half, 4), 'm')
print('differentiel attendu a 6 rad/s =', round(2 * 6.0 * half / 0.0175, 1), 'rad/s')
"
```

Si le différentiel attendu diffère de plus de 30 % de 20.0, mettre `SPIN_WHEEL_OMEGA_SCALE` à la valeur mesurée (arrondie à l'entier) et noter la mesure en commentaire au-dessus de la constante. Sinon laisser 20.0 et noter la mesure en commentaire. Dans les deux cas, le commentaire doit contenir la demi-voie mesurée.

- [ ] **Step 6 : Relancer les tests**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: PASS (18 tests — les tests passent `omega_scale=20.0` explicitement, donc ils sont indépendants de la constante)

- [ ] **Step 7 : Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_spin.py
git commit -m "spin: amorces du roulement differentiel (roues opposees + lames au sol)"
```

---

### Task 4 : Ciseau des jambes et tête partiellement libre

L'amorce de pose (`leg_antisymmetry`) et l'ajustement de `neck_joint_pos_l2` pour laisser `head_yaw` libre de servir de volant d'inertie.

**Piège de convention** : le robot a des conventions de signe **miroir** gauche/droite. Une pose *symétrique* satisfait `q_G + q_D ≈ 0` (c'est ce que mesure `leg_symmetry_reward`). Donc le **ciseau** (une jambe vers l'avant, l'autre vers l'arrière) satisfait `q_G ≈ q_D`, et se mesure par `−|q_G − q_D|`.

**Files:**
- Modify: `src/mjlab_microduck/tasks/mdp.py` (`neck_joint_pos_l2` à la ligne ~1237, puis ajout à la suite de la Task 3)
- Modify: `tests/test_spin.py`

**Interfaces:**
- Consumes: `_spin_gate`, `SPIN_*`, `_FakeEntity` / `_FakeEnv`
- Produces:
  - `leg_antisymmetry(env, command_name="twist", asset_cfg=_DEFAULT_ASSET_CFG, joint_bases=("hip_pitch", "knee"), rate_max=..., accel_end=..., hold_end=..., brake_end=...) -> torch.Tensor`
  - `neck_joint_pos_l2(env, asset_cfg=_NECK_JOINT_CFG, pattern: str = r".*(neck|head).*") -> torch.Tensor` (signature **élargie**, comportement par défaut inchangé)

- [ ] **Step 1 : Écrire les tests qui échouent**

Ajouter à `tests/test_spin.py` :

```python
# ── leg_antisymmetry ─────────────────────────────────────────────────────────
_LEG_IDS = {
    "left_hip_pitch": 0,
    "left_knee": 1,
    "right_hip_pitch": 2,
    "right_knee": 3,
}


def _leg_env(pos_rows, phases):
    pos = torch.tensor(pos_rows, dtype=torch.float32)
    entity = _FakeEntity(_FakeData(joint_pos=pos), joint_ids=_LEG_IDS)
    return _FakeEnv(entity, cmd=_phase_cmd(phases))


def test_leg_antisymmetry_prefers_scissor_over_mirror():
    # convention miroir : q_G = -q_D est une pose SYMÉTRIQUE (mauvais ici),
    # q_G = q_D est le CISEAU (bon ici). Valeur = -mean|q_G - q_D|, donc <= 0.
    env = _leg_env(
        [
            [0.4, 0.3, 0.4, 0.3],    # ciseau parfait : q_G == q_D -> 0.0
            [0.4, 0.3, -0.4, -0.3],  # miroir : écart 0.8 et 0.6 -> -0.7
        ],
        [0.30, 0.30],
    )
    r = mdp.leg_antisymmetry(env)
    assert torch.allclose(r, torch.tensor([0.0, -0.7]), atol=1e-6)
    assert r[0] > r[1]


def test_leg_antisymmetry_is_gated_off_during_rest():
    # en repos la porte est nulle : rien ne pousse au ciseau, station neutre libre.
    env = _leg_env([[0.4, 0.3, -0.4, -0.3]], [0.80])
    r = mdp.leg_antisymmetry(env)
    assert torch.allclose(r, torch.zeros(1), atol=1e-6)


# ── neck_joint_pos_l2 : paramètre pattern ────────────────────────────────────
_NECK_IDS = {
    "neck_pitch": 0,
    "head_pitch": 1,
    "head_roll": 2,
    "head_yaw": 3,
}


def test_neck_joint_pos_l2_pattern_can_exclude_head_yaw():
    class _NeckData(_FakeData):
        def __init__(self, joint_pos, default_joint_pos):
            super().__init__(joint_pos=joint_pos)
            self.default_joint_pos = default_joint_pos

    pos = torch.tensor([[0.0, 0.0, 0.0, 1.0]])  # seul head_yaw dévie, de 1 rad
    default = torch.zeros(1, 4)
    entity = _FakeEntity(_NeckData(pos, default), joint_ids=_NECK_IDS)
    env = _FakeEnv(entity)

    # motif par défaut : head_yaw compté -> coût 1.0
    assert torch.allclose(
        mdp.neck_joint_pos_l2(env), torch.tensor([1.0]), atol=1e-6
    )
    # motif du spin : head_yaw exclu -> coût 0.0 (tête libre en lacet)
    assert torch.allclose(
        mdp.neck_joint_pos_l2(env, pattern=r"^(neck_pitch|head_pitch|head_roll)$"),
        torch.tensor([0.0]),
        atol=1e-6,
    )
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'leg_antisymmetry'`

- [ ] **Step 3 : Ajouter le paramètre `pattern` à `neck_joint_pos_l2`**

Dans `src/mjlab_microduck/tasks/mdp.py`, remplacer la fonction existante (vers la ligne 1237) par :

```python
def neck_joint_pos_l2(
    env: ManagerBasedRlEnv,
    asset_cfg: SceneEntityCfg = _NECK_JOINT_CFG,
    pattern: str = r".*(neck|head).*",
) -> torch.Tensor:
    """Penalize neck/head joint position deviation from default (L2 squared).

    Uses find_joints() every call to avoid stale cached indices when the same
    SceneEntityCfg singleton is reused across robots with different joint layouts
    (e.g. walk robot vs rollers robot where passive wheels shift neck indices).

    ``pattern`` sélectionne les joints comptés (défaut : toute la nuque + la tête).
    La tâche spin passe un motif qui EXCLUT `head_yaw`, pour laisser la tête servir
    de volant d'inertie au lancement de la rotation.
    """
    asset: Entity = env.scene[asset_cfg.name]
    joint_ids, _ = asset.find_joints(pattern)
    error = asset.data.joint_pos[:, joint_ids] - asset.data.default_joint_pos[:, joint_ids]
    return torch.sum(torch.square(error), dim=1)
```

- [ ] **Step 4 : Implémenter `leg_antisymmetry`**

Ajouter à la suite de la Task 3 dans `src/mjlab_microduck/tasks/mdp.py` :

```python
def leg_antisymmetry(
    env: ManagerBasedRlEnv,
    command_name: str = "twist",
    asset_cfg: SceneEntityCfg = _DEFAULT_ASSET_CFG,
    joint_bases: tuple = ("hip_pitch", "knee"),
    rate_max: float = SPIN_RATE_MAX,
    accel_end: float = SPIN_ACCEL_END,
    hold_end: float = SPIN_HOLD_END,
    brake_end: float = SPIN_BRAKE_END,
) -> torch.Tensor:
    """Amorce le CISEAU des jambes (une avant / une arrière) pendant le spin.

    Le robot a des conventions de signe MIROIR gauche/droite : une pose
    symétrique satisfait q_G + q_D ≈ 0 (cf. `leg_symmetry_reward`), donc le
    ciseau satisfait q_G ≈ q_D. On retourne `gate(φ) · (−mean|q_G − q_D|)` — à
    utiliser avec un poids POSITIF, décroissant par curriculum : l'amorce
    s'efface pour laisser la policy affiner son propre geste.
    """
    asset: Entity = env.scene[asset_cfg.name]
    left, right = [], []
    for base in joint_bases:
        li, _ = asset.find_joints([f"left_{base}"])
        ri, _ = asset.find_joints([f"right_{base}"])
        left.append(li[0])
        right.append(ri[0])
    lids = torch.tensor(left, device=env.device)
    rids = torch.tensor(right, device=env.device)

    q = asset.data.joint_pos
    scissor = -torch.abs(q[:, lids] - q[:, rids]).mean(dim=-1)
    gate = _spin_gate(env, command_name, rate_max, accel_end, hold_end, brake_end)
    return gate * scissor
```

- [ ] **Step 5 : Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pytest pytest tests/test_spin.py -q`
Expected: PASS (21 tests)

- [ ] **Step 6 : Vérifier la non-régression des autres tests**

`neck_joint_pos_l2` est utilisée par les envs roller / slope / swizzle ; sa signature a changé (ajout d'un paramètre avec défaut, donc compatible).

Run: `uv run --with pytest pytest tests/ -q`
Expected: PASS — aucun test existant cassé

- [ ] **Step 7 : Commit**

```bash
git add src/mjlab_microduck/tasks/mdp.py tests/test_spin.py
git commit -m "spin: amorce ciseau des jambes + head_yaw libre (pattern sur neck_joint_pos_l2)"
```

---

### Task 5 : Env cfg et enregistrement de la tâche

Le fichier d'environnement complet et son enregistrement, avec les tests de configuration.

**Files:**
- Create: `src/mjlab_microduck/tasks/microduck_spin_env_cfg.py`
- Modify: `src/mjlab_microduck/tasks/__init__.py`
- Test: `tests/test_spin_cfg.py` (créer)

**Interfaces:**
- Consumes: `spin_rate_track`, `spin_rate_l1`, `spin_stay_in_place`, `spin_wheel_differential`, `spin_grounded`, `leg_antisymmetry`, `neck_joint_pos_l2(pattern=...)`, `SPIN_PERIOD`, `SPIN_RATE_MAX`, `SPIN_ACCEL_END`, `SPIN_HOLD_END`, `SPIN_BRAKE_END` (Tasks 1-4)
- Produces:
  - `make_microduck_spin_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg`
  - `MicroduckSpinRlCfg: RslRlOnPolicyRunnerCfg`
  - task id `Mjlab-Spin-Flat-MicroDuck`

- [ ] **Step 1 : Écrire les tests qui échouent**

Créer `tests/test_spin_cfg.py` :

```python
from mjlab_microduck.tasks import mdp as microduck_mdp
from mjlab_microduck.tasks.microduck_spin_env_cfg import (
    make_microduck_spin_env_cfg,
    MicroduckSpinRlCfg,
)


def test_cfg_uses_phase_command_with_runtime_default_period():
    cfg = make_microduck_spin_env_cfg()
    cmd = cfg.commands["twist"]
    assert isinstance(cmd, microduck_mdp.GroundPickPhaseCommandCfg)
    # 4.0 s = le défaut de --ground-pick-period : rien à passer au runtime
    assert cmd.period == 4.0
    # chaque épisode démarre à phase 0 (debout), comme le bouton au déploiement
    assert cmd.randomize_phase is False


def test_cfg_has_the_spin_rewards():
    cfg = make_microduck_spin_env_cfg()
    for name in (
        "spin_rate_track",
        "spin_rate_l1",
        "spin_stay_in_place",
        "spin_wheel_differential",
        "spin_grounded",
        "leg_antisymmetry",
    ):
        assert name in cfg.rewards, name
    # objectif principal avec un poids dominant
    assert cfg.rewards["spin_rate_track"].weight == 6.0
    # sur-place est un COÛT
    assert cfg.rewards["spin_stay_in_place"].weight < 0.0
    # cible positive = anti-horaire (le sens est porté par l'enveloppe)
    assert microduck_mdp.SPIN_RATE_MAX > 0.0


def test_angular_momentum_reward_is_removed():
    # Régression : angular_momentum_penalty pénalise la NORME 3D du moment
    # angulaire, elle combattrait directement le spin. Elle doit être absente.
    cfg = make_microduck_spin_env_cfg()
    assert "angular_momentum" not in cfg.rewards
    # body_ang_vel ne pénalise que x/y -> elle reste, elle mate le ballant
    assert "body_ang_vel" in cfg.rewards


def test_head_yaw_is_free_to_act_as_a_flywheel():
    cfg = make_microduck_spin_env_cfg()
    pattern = cfg.rewards["neck_joint_pos_l2"].params["pattern"]
    assert "head_yaw" not in pattern


def test_entry_velocity_allows_standstill_and_slow_roll():
    cfg = make_microduck_spin_env_cfg()
    # jamais via un push en mode reset (régression NaN du crouch)
    assert "entry_velocity" not in cfg.events
    lo, hi = cfg.events["reset_base"].params["velocity_range"]["x"]
    assert lo == 0.0 and hi > 0.0


def test_symmetry_augmentation_is_disabled():
    # la symétrie G/D transformerait un spin à gauche en spin à droite
    assert MicroduckSpinRlCfg.algorithm.symmetry_cfg is None


def test_leg_antisymmetry_shaping_decays():
    cfg = make_microduck_spin_env_cfg()
    stages = cfg.curriculum["leg_antisym_weight"].params["weight_stages"]
    weights = [s["weight"] for s in stages]
    assert weights[0] == cfg.rewards["leg_antisymmetry"].weight
    assert weights == sorted(weights, reverse=True)
    assert weights[-1] < weights[0]


def test_actor_observation_keeps_the_61d_slot_layout():
    # condition pour que l'ONNX charge dans le slot du runtime. L'égalité exacte
    # des dimensions avec le crouch est vérifiée en Task 6 Step 1 (il faut
    # construire l'env pour compter les dims ; ici on vérifie la structure).
    cfg = make_microduck_spin_env_cfg()
    terms = cfg.observations["actor"].terms
    assert "base_lin_vel" not in terms
    assert "height_scan" not in terms
    for padded in ("head_command", "body_command"):
        assert padded in terms
    assert terms["head_command"].params["dim"] == 4
    assert terms["body_command"].params["dim"] == 6
```

- [ ] **Step 2 : Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pytest pytest tests/test_spin_cfg.py -q`
Expected: FAIL avec `ModuleNotFoundError: No module named 'mjlab_microduck.tasks.microduck_spin_env_cfg'`

- [ ] **Step 3 : Créer le fichier d'environnement**

Créer `src/mjlab_microduck/tasks/microduck_spin_env_cfg.py` :

```python
"""Microduck SPIN task — rotation rapide sur place, sur rollers.

Geste cyclique déclenché au bouton A via le slot --ground-pick du runtime :
~2 tours anti-horaire à ~6 rad/s puis arrêt propre debout.

Hybride :
  - physique / robot roller  ← microduck_velocity_rollers_env_cfg.py
  - machinerie phase cyclique ← microduck_roller_crouch_env_cfg.py
    (commande GroundPickPhaseCommand : [cos(2πφ), sin(2πφ), 0], période 4 s)

Différence de fond avec le crouch : la phase pilote une VITESSE DE LACET cible
(objectif de résultat) et non une pose articulaire. Deux amorces décroissantes
poussent vers le roulement différentiel — le seul mécanisme physique certain sur
4 roues passives : patin gauche vers l'arrière, patin droit vers l'avant.

Obs 61D unifié → interchangeable au runtime avec roller / ground_pick / crouch.
Voir docs/superpowers/specs/2026-08-04-spin-env-design.md.
"""

import math
from copy import deepcopy

# La symétrie G/D transformerait un spin à gauche en spin à droite : interdit ici.
ENABLE_SYMMETRY = False

# DR — repris du roller env
ENABLE_COM_RANDOMIZATION             = True
ENABLE_HEAD_COM_RANDOMIZATION        = True
ENABLE_MASS_INERTIA_RANDOMIZATION    = True
ENABLE_JOINT_FRICTION_RANDOMIZATION  = True
ENABLE_ARMATURE_RANDOMIZATION        = True
ENABLE_WHEEL_FRICTION_RANDOMIZATION  = True
ENABLE_VELOCITY_PUSHES               = True
ENABLE_IMU_ORIENTATION_RANDOMIZATION = True
ENABLE_ENCODER_BIAS                  = True

COM_RANDOMIZATION_RANGE          = 0.003
HEAD_COM_RANDOMIZATION_RANGE     = 0.003
MASS_INERTIA_RANDOMIZATION_RANGE = (0.95, 1.05)
JOINT_FRICTION_RANDOMIZATION_RANGE = (0.9, 1.1)
ARMATURE_RANDOMIZATION_RANGE     = (0.9, 1.1)
VELOCITY_PUSH_INTERVAL_S         = (3.0, 6.0)
VELOCITY_PUSH_RANGE              = (-0.2, 0.2)
IMU_ORIENTATION_RANDOMIZATION_ANGLE = 6.0
ENCODER_BIAS_RANGE               = (-0.015, 0.015)

# Le bouton peut être pressé à l'arrêt OU en roulement lent : la policy apprend
# à tuer l'élan résiduel avant/pendant le lancement de la rotation.
ENTRY_VELOCITY_X = (0.0, 0.3)

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers import (
    CurriculumTermCfg,
    EventTermCfg,
    ObservationTermCfg,
    RewardTermCfg,
    TerminationTermCfg,
)
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.rl import RslRlOnPolicyRunnerCfg, RslRlModelCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.tasks.velocity import mdp
from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
from mjlab.tasks.velocity.velocity_env_cfg import make_velocity_env_cfg
from mjlab.utils.noise import UniformNoiseCfg as Unoise

from mjlab_microduck.robot.microduck_constants import MICRODUCK_WALK_ROLLERS_ROBOT_CFG
from mjlab_microduck.tasks import mdp as microduck_mdp
from mjlab_microduck.tasks.microduck_velocity_env_cfg import HEAD_BODY_NAMES
from mjlab_microduck.tasks.symmetry import PpoWithSymmetryCfg, SYMMETRY_CFG

# Enveloppe de phase : constantes canoniques définies dans mdp.py.
SPIN_PERIOD = microduck_mdp.SPIN_PERIOD
_ENVELOPE = {
    "rate_max": microduck_mdp.SPIN_RATE_MAX,
    "accel_end": microduck_mdp.SPIN_ACCEL_END,
    "hold_end": microduck_mdp.SPIN_HOLD_END,
    "brake_end": microduck_mdp.SPIN_BRAKE_END,
}
# Nuque/tête tenues près du neutre SAUF head_yaw, laissé libre : il peut servir
# de volant d'inertie pour lancer la rotation.
NECK_PATTERN_NO_YAW = r"^(neck_pitch|head_pitch|head_roll)$"


def make_microduck_spin_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
    """Env spin sur rollers, piloté par la phase du slot ground-pick."""

    feet_ground_cfg = ContactSensorCfg(
        name="feet_ground_contact",
        primary=ContactMatch(
            mode="subtree",
            pattern=r"^(ankle_l_v1|ankle_r_v1)$",
            entity="robot",
        ),
        secondary=ContactMatch(mode="body", pattern="terrain"),
        fields=("found", "force"),
        reduce="netforce",
        num_slots=1,
        track_air_time=True,
    )
    self_collision_cfg = ContactSensorCfg(
        name="self_collision",
        primary=ContactMatch(mode="subtree", pattern="trunk_base", entity="robot"),
        secondary=ContactMatch(mode="subtree", pattern="trunk_base", entity="robot"),
        fields=("found",),
        reduce="none",
        num_slots=1,
    )

    cfg = make_velocity_env_cfg()
    cfg.scene.entities = {"robot": MICRODUCK_WALK_ROLLERS_ROBOT_CFG}
    cfg.scene.sensors = (feet_ground_cfg, self_collision_cfg)
    cfg.viewer.body_name = "trunk_base"

    joint_pos_action = cfg.actions["joint_pos"]
    assert isinstance(joint_pos_action, JointPositionActionCfg)
    joint_pos_action.scale = 1.0

    # === REWARDS ===
    # ⚠️ angular_momentum n'est PAS gardée : elle pénalise la norme 3D du moment
    # angulaire, donc elle combattrait directement le spin. body_ang_vel, elle,
    # ne pénalise que x/y (« Don't penalize z-angular velocity » dans mjlab) →
    # gardée, elle mate le ballant roulis/tangage sans gêner la rotation.
    keep = {"upright", "body_ang_vel", "action_rate_l2"}
    for name in list(cfg.rewards.keys()):
        if name not in keep:
            del cfg.rewards[name]

    cfg.rewards["upright"].params["asset_cfg"].body_names = ("trunk_base",)
    cfg.rewards["upright"].weight = 2.0
    cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("trunk_base",)
    cfg.rewards["body_ang_vel"].weight = -0.05
    cfg.rewards["action_rate_l2"].weight = -1.0

    # Objectif principal : suivre la vitesse de lacet cible ω*(φ) (trapèze).
    cfg.rewards["spin_rate_track"] = RewardTermCfg(
        func=microduck_mdp.spin_rate_track,
        weight=6.0,
        params={"command_name": "twist", "std": 1.5, **_ENVELOPE},
    )
    # Bootstrap L1 : gradient constant quand la gaussienne sature loin de la cible.
    cfg.rewards["spin_rate_l1"] = RewardTermCfg(
        func=microduck_mdp.spin_rate_l1,
        weight=0.5,
        params={"command_name": "twist", **_ENVELOPE},
    )
    # Tourner SUR PLACE, et tuer l'élan d'entrée.
    cfg.rewards["spin_stay_in_place"] = RewardTermCfg(
        func=microduck_mdp.spin_stay_in_place,
        weight=-1.0,
        params={},
    )
    # Amorce 1 : tourner EN ROULEMENT (patins en sens opposés), pas en patinage.
    cfg.rewards["spin_wheel_differential"] = RewardTermCfg(
        func=microduck_mdp.spin_wheel_differential,
        weight=1.0,
        params={
            "command_name": "twist",
            "omega_scale": microduck_mdp.SPIN_WHEEL_OMEGA_SCALE,
            **_ENVELOPE,
        },
    )
    # Amorce 2 : ciseau des jambes (décroît par curriculum, voir plus bas).
    cfg.rewards["leg_antisymmetry"] = RewardTermCfg(
        func=microduck_mdp.leg_antisymmetry,
        weight=1.0,
        params={
            "command_name": "twist",
            "joint_bases": ("hip_pitch", "knee"),
            **_ENVELOPE,
        },
    )
    # Les deux lames au sol pendant le spin (pas de vrille en l'air).
    cfg.rewards["spin_grounded"] = RewardTermCfg(
        func=microduck_mdp.spin_grounded,
        weight=0.5,
        params={
            "sensor_name": "feet_ground_contact",
            "command_name": "twist",
            **_ENVELOPE,
        },
    )
    # Stabilité / sim2real
    cfg.rewards["feet_flat"] = RewardTermCfg(
        func=microduck_mdp.feet_flat_penalty,
        weight=-2.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", site_names=("left_foot", "right_foot")),
            "sensor_name": "feet_ground_contact",
        },
    )
    cfg.rewards["self_collisions"] = RewardTermCfg(
        func=mdp.self_collision_cost,
        weight=-1.0,
        params={"sensor_name": "self_collision"},
    )
    cfg.rewards["neck_action_rate_l2"] = RewardTermCfg(
        func=microduck_mdp.neck_action_rate_l2, weight=-0.5
    )
    cfg.rewards["neck_joint_pos_l2"] = RewardTermCfg(
        func=microduck_mdp.neck_joint_pos_l2,
        weight=-0.2,
        params={"pattern": NECK_PATTERN_NO_YAW},
    )
    cfg.rewards["joint_torques_l2"] = RewardTermCfg(
        func=microduck_mdp.joint_torques_l2, weight=-1e-3
    )

    # === TERMINATIONS ===
    cfg.terminations["nan_state"] = TerminationTermCfg(
        func=microduck_mdp.robot_state_is_nan, time_out=False,
    )

    # === EVENTS ===
    cfg.events["reset_action_history"] = EventTermCfg(
        func=microduck_mdp.reset_action_history, mode="reset",
    )
    del cfg.events["foot_friction"]

    if ENABLE_VELOCITY_PUSHES:
        cfg.events["push_robot"] = EventTermCfg(
            func=mdp.push_by_setting_velocity,
            mode="interval",
            interval_range_s=VELOCITY_PUSH_INTERVAL_S,
            params={
                "velocity_range": {"x": VELOCITY_PUSH_RANGE, "y": VELOCITY_PUSH_RANGE},
                "asset_cfg": SceneEntityCfg("robot"),
            },
        )

    cfg.events["reset_base"].params["pose_range"]["z"] = (0.1335, 0.1435)
    # Élan d'entrée : injecté via reset_root_state_uniform (état par défaut PROPRE
    # + range), et NON via push_by_setting_velocity en mode reset, qui additionne à
    # une vitesse racine potentiellement divergente et fait exploser le free-joint
    # de la base -> NaN. Régression connue du roller_crouch.
    cfg.events["reset_base"].params["velocity_range"] = {"x": ENTRY_VELOCITY_X}

    if ENABLE_WHEEL_FRICTION_RANDOMIZATION:
        cfg.events["randomize_wheel_friction"] = EventTermCfg(
            func=dr.dof_frictionloss,
            mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", joint_names=(r"^passive_.*",)),
                "operation": "abs",
                "ranges": (0.000, 0.000),
            },
        )
    if ENABLE_COM_RANDOMIZATION:
        cfg.events["randomize_com"] = EventTermCfg(
            func=dr.body_ipos, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
                "operation": "add",
                "ranges": (-COM_RANDOMIZATION_RANGE, COM_RANDOMIZATION_RANGE),
            },
        )
    if ENABLE_HEAD_COM_RANDOMIZATION:
        cfg.events["randomize_head_com"] = EventTermCfg(
            func=dr.body_ipos, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=HEAD_BODY_NAMES),
                "operation": "add",
                "ranges": (-HEAD_COM_RANDOMIZATION_RANGE, HEAD_COM_RANDOMIZATION_RANGE),
            },
        )
    if ENABLE_MASS_INERTIA_RANDOMIZATION:
        _mi_lo, _mi_hi = MASS_INERTIA_RANDOMIZATION_RANGE
        cfg.events["randomize_mass_inertia"] = EventTermCfg(
            func=dr.pseudo_inertia, mode="startup",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=("trunk_base",)),
                "alpha_range": (math.log(_mi_lo) / 2.0, math.log(_mi_hi) / 2.0),
            },
        )
    if ENABLE_JOINT_FRICTION_RANDOMIZATION:
        cfg.events["randomize_joint_friction"] = EventTermCfg(
            func=microduck_mdp.randomize_bam_friction, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot"),
                "scale_range": JOINT_FRICTION_RANDOMIZATION_RANGE,
            },
        )
    if ENABLE_ARMATURE_RANDOMIZATION:
        cfg.events["randomize_armature"] = EventTermCfg(
            func=dr.joint_armature, mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot", joint_names=(r"^(?!passive_).*",)),
                "operation": "scale",
                "ranges": ARMATURE_RANDOMIZATION_RANGE,
            },
        )

    # === OBSERVATIONS (unified 61D layout) ===
    del cfg.observations["actor"].terms["base_lin_vel"]
    del cfg.observations["critic"].terms["foot_height"]
    del cfg.observations["actor"].terms["height_scan"]
    del cfg.observations["critic"].terms["height_scan"]
    cfg.observations["critic"].terms["base_lin_vel"] = ObservationTermCfg(
        func=mdp.base_lin_vel, scale=1.0,
    )

    gravity_term_name = "projected_gravity"
    cfg.observations["actor"].terms[gravity_term_name] = deepcopy(
        cfg.observations["actor"].terms[gravity_term_name]
    )
    cfg.observations["actor"].terms["base_ang_vel"] = deepcopy(
        cfg.observations["actor"].terms["base_ang_vel"]
    )
    cfg.observations["actor"].terms["base_ang_vel"].delay_min_lag = 0
    cfg.observations["actor"].terms["base_ang_vel"].delay_max_lag = 1
    cfg.observations["actor"].terms["base_ang_vel"].delay_update_period = 64
    cfg.observations["actor"].terms[gravity_term_name].delay_min_lag = 0
    cfg.observations["actor"].terms[gravity_term_name].delay_max_lag = 1
    cfg.observations["actor"].terms[gravity_term_name].delay_update_period = 64
    cfg.observations["actor"].terms["base_ang_vel"].noise = Unoise(n_min=-0.03, n_max=0.03)
    cfg.observations["actor"].terms[gravity_term_name].noise = Unoise(n_min=-0.01, n_max=0.01)
    cfg.observations["actor"].terms["joint_pos"].noise = Unoise(n_min=-0.001, n_max=0.001)
    cfg.observations["actor"].terms["joint_vel"].noise = Unoise(n_min=-0.25, n_max=0.25)

    if ENABLE_IMU_ORIENTATION_RANDOMIZATION:
        av = cfg.observations["actor"].terms["base_ang_vel"]
        av.func = microduck_mdp.base_ang_vel_imu_misaligned
        av.params = {"max_angle_deg": IMU_ORIENTATION_RANDOMIZATION_ANGLE}
        g = cfg.observations["actor"].terms[gravity_term_name]
        g.func = microduck_mdp.projected_gravity_imu_misaligned
        g.params = {"max_angle_deg": IMU_ORIENTATION_RANDOMIZATION_ANGLE}

    cfg.observations["actor"].terms["joint_vel"] = deepcopy(
        cfg.observations["actor"].terms["joint_vel"]
    )
    cfg.observations["actor"].terms["joint_vel"].delay_min_lag = 1
    cfg.observations["actor"].terms["joint_vel"].delay_max_lag = 1
    cfg.observations["actor"].terms["joint_vel"].delay_update_period = 0

    passive_excluded = SceneEntityCfg("robot", joint_names=(r"^(?!passive_).*",))
    for grp in ("actor", "critic"):
        for term in ("joint_pos", "joint_vel"):
            cfg.observations[grp].terms[term] = deepcopy(cfg.observations[grp].terms[term])
            cfg.observations[grp].terms[term].params["asset_cfg"] = deepcopy(passive_excluded)

    if ENABLE_ENCODER_BIAS:
        cfg.events["encoder_bias"].params["bias_range"] = ENCODER_BIAS_RANGE
        cfg.observations["actor"].terms["joint_pos"].params["biased"] = True
        cfg.observations["critic"].terms["joint_pos"].params["biased"] = False
    else:
        cfg.events.pop("encoder_bias", None)

    wheel_cfg = SceneEntityCfg("robot", joint_names=(r"^passive_.*",))
    cfg.observations["critic"].terms["wheel_vel"] = ObservationTermCfg(
        func=mdp.joint_vel_rel, scale=1.0, params={"asset_cfg": wheel_cfg},
    )

    for group in ("actor", "critic"):
        cfg.observations[group].terms["head_command"] = ObservationTermCfg(
            func=microduck_mdp.zero_command_padding, params={"dim": 4},
        )
        cfg.observations[group].terms["body_command"] = ObservationTermCfg(
            func=microduck_mdp.zero_command_padding, params={"dim": 6},
        )

    # === COMMAND: phase (comme ground_pick / roller_crouch) ===
    command: UniformVelocityCommandCfg = cfg.commands["twist"]
    command.rel_standing_envs = 0.0
    command.rel_heading_envs = 0.0
    # period=4.0 = défaut de --ground-pick-period (rien à passer au runtime) ;
    # randomize_phase=False -> chaque épisode démarre debout à phase 0, comme le
    # bouton au déploiement. Épisode 20 s = 5 cycles complets du geste.
    cfg.commands["twist"] = microduck_mdp.GroundPickPhaseCommandCfg(
        **{
            **vars(command),
            "class_type": microduck_mdp.GroundPickPhaseCommand,
            "period": SPIN_PERIOD,
            "randomize_phase": False,
        }
    )

    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None

    # === CURRICULUM ===
    del cfg.curriculum["terrain_levels"]
    del cfg.curriculum["command_vel"]
    cfg.curriculum["action_rate_weight"] = CurriculumTermCfg(
        func=microduck_mdp.reward_weight,
        params={
            "reward_name": "action_rate_l2",
            "weight_stages": [
                {"step": 0, "weight": -0.5},
                {"step": 250 * 24, "weight": -0.8},
                {"step": 500 * 24, "weight": -1.0},
            ],
        },
    )
    # L'amorce ciseau s'efface : elle lance le bon mécanisme puis laisse la policy
    # affiner son propre geste (fréquence de pompage libre).
    cfg.curriculum["leg_antisym_weight"] = CurriculumTermCfg(
        func=microduck_mdp.reward_weight,
        params={
            "reward_name": "leg_antisymmetry",
            "weight_stages": [
                {"step": 0, "weight": 1.0},
                {"step": 1500 * 24, "weight": 0.5},
                {"step": 3000 * 24, "weight": 0.25},
            ],
        },
    )
    if ENABLE_COM_RANDOMIZATION:
        cfg.curriculum["com_range"] = CurriculumTermCfg(
            func=microduck_mdp.com_range_curriculum,
            params={
                "event_name": "randomize_com",
                "range_stages": [
                    {"step": 0, "range": 0.003},
                    {"step": 500 * 24, "range": 0.005},
                    {"step": 1000 * 24, "range": 0.01},
                ],
            },
        )
    if ENABLE_HEAD_COM_RANDOMIZATION:
        cfg.curriculum["head_com_range"] = CurriculumTermCfg(
            func=microduck_mdp.com_range_curriculum,
            params={
                "event_name": "randomize_head_com",
                "range_stages": [
                    {"step": 0, "range": 0.003},
                    {"step": 500 * 24, "range": 0.005},
                    {"step": 1000 * 24, "range": 0.01},
                ],
            },
        )

    return cfg


MicroduckSpinRlCfg = RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,
        distribution_cfg={
            "class_name": "GaussianDistribution",
            "init_std": 1.0,
            "std_type": "scalar",
        },
    ),
    critic=RslRlModelCfg(
        hidden_dims=(512, 256, 128),
        activation="elu",
        obs_normalization=True,
    ),
    algorithm=PpoWithSymmetryCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
        symmetry_cfg=SYMMETRY_CFG if ENABLE_SYMMETRY else None,
    ),
    wandb_project="mjlab_microduck",
    experiment_name="spin",
    run_name="spin",
    save_interval=250,
    num_steps_per_env=24,
    max_iterations=8_000,
)
```

- [ ] **Step 4 : Enregistrer la tâche**

Dans `src/mjlab_microduck/tasks/__init__.py`, ajouter l'import après le bloc `microduck_roller_slope_env_cfg` (vers la ligne 66) :

```python
from .microduck_spin_env_cfg import (
    make_microduck_spin_env_cfg,
    MicroduckSpinRlCfg,
)
```

Puis l'enregistrement à la fin du fichier, après le bloc `Mjlab-RollerSlope-Flat-MicroDuck` :

```python
register_mjlab_task(
    task_id="Mjlab-Spin-Flat-MicroDuck",
    env_cfg=make_microduck_spin_env_cfg(),
    play_env_cfg=make_microduck_spin_env_cfg(play=True),
    rl_cfg=MicroduckSpinRlCfg,
    runner_cls=MicroduckOnPolicyRunner,
)
print("✓ Spin task registered: Mjlab-Spin-Flat-MicroDuck")
```

- [ ] **Step 5 : Lancer les tests de config**

Run: `uv run --with pytest pytest tests/test_spin_cfg.py -q`
Expected: PASS (8 tests)

- [ ] **Step 6 : Vérifier que la tâche est bien enregistrée**

Run: `uv run python -c "import mjlab_microduck.tasks"`
Expected: la sortie contient `✓ Spin task registered: Mjlab-Spin-Flat-MicroDuck`, sans exception

- [ ] **Step 7 : Vérifier la non-régression de toute la suite**

Run: `uv run --with pytest pytest tests/ -q`
Expected: PASS

- [ ] **Step 8 : Commit**

```bash
git add src/mjlab_microduck/tasks/microduck_spin_env_cfg.py src/mjlab_microduck/tasks/__init__.py tests/test_spin_cfg.py
git commit -m "spin: env cfg Mjlab-Spin-Flat-MicroDuck + enregistrement"
```

---

### Task 6 : Vérification en simulation (smoke run)

Les tests unitaires ne prouvent pas que l'env tourne réellement : les 61D de l'obs, les capteurs de contact, les résolutions de joints et l'absence de NaN ne se voient qu'en lançant le simulateur. Cette tâche est la porte de sortie du plan.

**Files:**
- Modify: `docs/superpowers/specs/2026-08-04-spin-env-design.md` (noter la mesure de demi-voie et le résultat du smoke run)

**Interfaces:**
- Consumes: la tâche enregistrée `Mjlab-Spin-Flat-MicroDuck` (Task 5)
- Produces: rien de code — une vérification et une note

- [ ] **Step 1 : Vérifier la dimension réelle de l'obs actor**

Run:
```bash
uv run python -c "
import mjlab_microduck.tasks  # enregistre les tâches
from mjlab_microduck.tasks.microduck_spin_env_cfg import make_microduck_spin_env_cfg
from mjlab_microduck.tasks.microduck_roller_crouch_env_cfg import make_microduck_roller_crouch_env_cfg
spin = make_microduck_spin_env_cfg()
crouch = make_microduck_roller_crouch_env_cfg()
print('spin  actor terms:', list(spin.observations['actor'].terms.keys()))
print('crouch actor terms:', list(crouch.observations['actor'].terms.keys()))
assert list(spin.observations['actor'].terms.keys()) == list(crouch.observations['actor'].terms.keys()), 'layout obs != crouch -> ONNX ne chargera pas dans le slot'
print('OK: layout obs actor identique au crouch')
"
```
Expected: `OK: layout obs actor identique au crouch`. Si les listes diffèrent, corriger le bloc OBSERVATIONS de l'env cfg avant de continuer — c'est la condition pour que l'ONNX charge dans le slot du runtime.

- [ ] **Step 2 : Lancer un entraînement très court avec garde NaN**

Run:
```bash
uv run train Mjlab-Spin-Flat-MicroDuck \
  --env.scene.num-envs 64 \
  --agent.max_iterations 5 \
  --enable-nan-guard
```
Expected: 5 itérations sans exception, sans NaN, et les logs `Episode_Reward/` listent bien `spin_rate_track`, `spin_rate_l1`, `spin_stay_in_place`, `spin_wheel_differential`, `spin_grounded`, `leg_antisymmetry`.

Si des NaN apparaissent : les dumps sont dans `/tmp/mjlab/nan_dumps/`. Le suspect n°1 est la vitesse d'entrée — vérifier qu'elle passe bien par `reset_base.velocity_range` et pas par un push en `mode="reset"`.

- [ ] **Step 3 : Lancer un entraînement de calibrage (500 itérations)**

Run:
```bash
uv run train Mjlab-Spin-Flat-MicroDuck --env.scene.num-envs 4096 --agent.max_iterations 500
```
Expected: `Episode_Reward/spin_rate_track` **monte** sur les 500 itérations. C'est le signal que l'objectif est apprenable. Noter la valeur atteinte.

Si la courbe reste plate, appliquer le « Plan B » du spec dans l'ordre : (1) curriculum de vitesse 3 → 6 rad/s, (2) monter `spin_wheel_differential` et retarder la décroissance de `leg_antisymmetry`, (3) élargir `std` de 1.5 à 2.5.

- [ ] **Step 4 : Regarder le geste**

Run: `uv run scripts/play_latest.py`
Expected: le robot tente une rotation anti-horaire sur place. À 500 itérations le geste sera brut ; ce qu'on vérifie c'est qu'il tourne **dans le bon sens**, qu'il ne part pas en translation, et qu'il ne finit pas systématiquement par tomber.

- [ ] **Step 5 : Noter les mesures dans le spec**

Ajouter une section `## Résultats de la vérification initiale` à la fin de `docs/superpowers/specs/2026-08-04-spin-env-design.md`, contenant : la demi-voie mesurée (Task 3 Step 5), la valeur retenue pour `omega_scale`, le résultat du smoke run 5 itérations, et la valeur de `Episode_Reward/spin_rate_track` à 500 itérations.

- [ ] **Step 6 : Commit**

```bash
git add docs/superpowers/specs/2026-08-04-spin-env-design.md
git commit -m "spin: notes de verification initiale (demi-voie, smoke run, 500 it.)"
```

---

## Notes pour l'implémenteur

- **Ordre obligatoire** : Task 1 → 2 → 3 → 4 → 5 → 6. Les tâches 2 à 4 dépendent du faux env créé dans la Task 2 ; la Task 5 consomme toutes les fonctions des tâches 1 à 4.
- **Le piège n°1 de cette tâche** est la reward `angular_momentum` : si elle reste dans l'env, elle pénalise la norme 3D du moment angulaire et le spin ne décollera jamais. Le test `test_angular_momentum_reward_is_removed` la garde.
- **Le piège n°2** est la convention de signe miroir gauche/droite du robot : le ciseau se mesure par `|q_G − q_D|`, pas par `|q_G + q_D|`. Comparer avec `leg_symmetry_reward` (ligne ~3769 de `mdp.py`) en cas de doute.
- **Le piège n°3** est la parité d'obs 61D : toute divergence par rapport au layout du crouch rend l'ONNX inutilisable dans le slot du runtime. La Task 6 Step 1 la vérifie explicitement.
- Ne pas activer la symétrie PPO, quelle que soit la tentation d'accélérer l'apprentissage.
- **Hors périmètre de ce plan** : l'entraînement complet (8000 itérations), l'export ONNX et le déploiement dans le slot du runtime. Les commandes sont dans le spec ; le plan s'arrête quand l'env est vérifié apprenable (Task 6).

```
