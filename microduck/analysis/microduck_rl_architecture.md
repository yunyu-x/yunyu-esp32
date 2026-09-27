# Architectural Analysis & Learning Guide: microduck_rl

> 自动化生成的开源项目架构全景图、多语言符号契约与递进式学习路线图。

## 1. 核心技术栈与外部依赖
- **源码模块总数**: 71
- **外部第三方库**: __future__, argparse, bam, copy, csv, dataclasses, datetime, huggingface_hub, importlib, json, math, mjlab, mjlab_microduck, mujoco, netrc, numpy, onnx, onnxruntime, os, pathlib, pickle, platform, plotly, pytest, queue, re, rsl_rl, select, shlex, shutil, socket, socketserver, struct, subprocess, sys, tarfile, tempfile, tensordict, termios, threading, time, tomllib, torch, tty, typing, tyro, wandb, wandb_utils

## 2. 系统架构调用拓扑图 (Mermaid Topology)
```mermaid
graph TD
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_backlash_py["src/mjlab_microduck/tasks/backlash.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_ball_kick_env_cfg_py["src/mjlab_microduck/tasks/microduck_ball_kick_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_ground_pick_env_cfg_py["src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_roller_crouch_env_cfg_py["src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_roller_slope_env_cfg_py["src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_roller_standup_env_cfg_py["src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_roulade_env_cfg_py["src/mjlab_microduck/tasks/microduck_roulade_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_sitstand_env_cfg_py["src/mjlab_microduck/tasks/microduck_sitstand_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_spin_env_cfg_py["src/mjlab_microduck/tasks/microduck_spin_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_standup_env_cfg_py["src/mjlab_microduck/tasks/microduck_standup_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_velocity_env_cfg_py["src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_velocity_rollers_env_cfg_py["src/mjlab_microduck/tasks/microduck_velocity_rollers_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_velocity_swizzle_env_cfg_py["src/mjlab_microduck/tasks/microduck_velocity_swizzle_env_cfg.py"]
    src_mjlab_microduck_tasks___init___py["src/mjlab_microduck/tasks/__init__.py"] --> src_mjlab_microduck_tasks_microduck_velstand_env_cfg_py["src/mjlab_microduck/tasks/microduck_velstand_env_cfg.py"]
```

## 3. 递进式学习与精读路线图 (Progressive Learning Roadmap)

### 📍 Stage 1: Core Primitives & Foundation Models (核心实体与基础数据模型)
*Start here to understand data schemas, interfaces, and atomic utilities.*

- [x] `scripts/export.py`
- [x] `scripts/hf/train_hf.py`
- [x] `src/mjlab_microduck/__init__.py`
- [x] `src/mjlab_microduck/actuator/__init__.py`
- [x] `src/mjlab_microduck/publish/__init__.py`
- [x] `src/mjlab_microduck/robot/__init__.py`
- [x] `src/mjlab_microduck/sim/__init__.py`
- [x] `src/mjlab_microduck/train_cli.py`
- [x] `scripts/play_latest.py`
- [x] `scripts/crouch_pose_editor.py`
- [x] `src/mjlab_microduck/tasks/slope_terrain.py`
- [x] `scripts/view_slope_terrain.py`
- [x] `tests/test_swizzle_head_cfg.py`
- [x] `src/mjlab_microduck/robot/testbench_constants.py`
- [x] `src/mjlab_microduck/train_hook.py`
- [x] `src/mjlab_microduck/tasks/__init__.py`
- [x] `src/mjlab_microduck/tasks/symmetry.py`
- [x] `tests/test_infer_policy_bam.py`
- [x] `tests/test_roller_crouch_cfg.py`
- [x] `tests/test_ground_pick_cfg.py`
- [x] `scripts/hf/uploader.py`
- [x] `src/mjlab_microduck/tasks/backlash.py`
- [x] `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py`

### 📍 Stage 2: Business Logic & Processing Pipelines (核心算法与逻辑处理)
*Understand core domain state machines, algorithms, and orchestration logic.*

- [x] `src/mjlab_microduck/tasks/microduck_velocity_swizzle_env_cfg.py`
- [x] `src/mjlab_microduck/tasks/testbench_env_cfg.py`
- [x] `tests/test_crouch_glide.py`
- [x] `tests/test_slope_curriculum.py`
- [x] `tests/test_slope_terrain.py`
- [x] `tests/test_descent_speed.py`
- [x] `src/mjlab_microduck/robot/microduck/add_backlash.py`
- [x] `src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py`
- [x] `tests/test_nan_guard.py`
- [x] `tests/test_wheel_glide.py`
- [x] `src/mjlab_microduck/actuator/friction_dr_bam.py`
- [x] `tests/test_spin_cfg.py`
- [x] `src/mjlab_microduck/robot/microduck_constants.py`
- [x] `tests/test_hf_jobs_flag.py`
- [x] `tests/test_roller_slope_cfg.py`
- [x] `src/mjlab_microduck/sim/tof.py`
- [x] `src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py`
- [x] `src/mjlab_microduck/tasks/microduck_spin_env_cfg.py`
- [x] `src/mjlab_microduck/tasks/microduck_velstand_env_cfg.py`
- [x] `src/mjlab_microduck/sim/camera.py`
- [x] `src/mjlab_microduck/tasks/microduck_velocity_rollers_env_cfg.py`
- [x] `tests/test_aarch64_cuda_torch.py`
- [x] `tests/test_ground_pick_pose.py`
- [x] `scripts/validate_bam_testbench.py`

### 📍 Stage 3: Entrypoints & Client Interfaces (系统入口与外部接口)
*Trace main application lifecycles, CLI runners, and consumer API surfaces.*

- [x] `src/mjlab_microduck/tasks/microduck_ball_kick_env_cfg.py`
- [x] `scripts/wandb_utils.py`
- [x] `src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py`
- [x] `src/mjlab_microduck/tasks/microduck_roulade_env_cfg.py`
- [x] `tests/test_publish_manifest.py`
- [x] `src/mjlab_microduck/tasks/microduck_sitstand_env_cfg.py`
- [x] `tests/test_obs_nan_guard.py`
- [x] `tests/test_head_pose_bias.py`
- [x] `src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py`
- [x] `src/mjlab_microduck/publish/cli.py`
- [x] `src/mjlab_microduck/tasks/microduck_standup_env_cfg.py`
- [x] `src/mjlab_microduck/tasks/distill.py`
- [x] `scripts/plot_observations_comparison_plotly.py`
- [x] `scripts/testbench_sim2real.py`
- [x] `scripts/odom_anchor_points.py`
- [x] `src/mjlab_microduck/export.py`
- [x] `tests/test_spin.py`
- [x] `tests/test_roller_standup_cfg.py`
- [x] `src/mjlab_microduck/hf_jobs.py`
- [x] `tests/test_velstand_cfg.py`
- [x] `src/mjlab_microduck/publish/manifest.py`
- [x] `src/mjlab_microduck/sim/body_server.py`
- [x] `scripts/infer_policy.py`
- [x] `src/mjlab_microduck/tasks/mdp.py`

## 4. 关键导出符号与公共 API 矩阵 (Universal Symbols & Complexity)

| 模块文件 | 语言 | 类/结构体 | 关键函数/方法 | 圈复杂度总计 |
| :--- | :---: | :--- | :--- | :---: |
| `scripts/crouch_pose_editor.py` | Python | - | `home_value()` | 3 |
| `scripts/export.py` | Python | - | - | 0 |
| `scripts/hf/train_hf.py` | Python | - | - | 0 |
| `scripts/hf/uploader.py` | Python | - | `main()` | 9 |
| `scripts/infer_policy.py` | Python | `TerminalInput`, `PolicyInference`, `FootFrames` (+3) | `load_bam_model()`, `load_mujoco_with_bam()`, `TerminalInput.__init__()` (+57) | 434 |
| `scripts/odom_anchor_points.py` | Python | `SoleSurface` | `quat2mat()`, `SoleSurface.__init__()`, `SoleSurface.bottom_z()` (+6) | 39 |
| `scripts/play_latest.py` | Python | - | `main()` | 2 |
| `scripts/plot_observations_comparison_plotly.py` | Python | - | `load_observations()`, `plot_comparison()`, `main()` | 36 |
| `scripts/testbench_sim2real.py` | Python | `PolicyRunner` | `make_target_schedule()`, `PolicyRunner.__init__()`, `PolicyRunner.reset()` (+8) | 38 |
| `scripts/validate_bam_testbench.py` | Python | - | `bam_python_rollout()`, `compute_m6_friction()`, `mujoco_rollout()` (+1) | 20 |
| `scripts/view_slope_terrain.py` | Python | - | `build_model()`, `main()` | 4 |
| `scripts/wandb_utils.py` | Python | - | `find_latest_run()`, `find_latest_runs()`, `_format_duration()` (+3) | 21 |
| `src/mjlab_microduck/__init__.py` | Python | - | - | 0 |
| `src/mjlab_microduck/actuator/__init__.py` | Python | - | - | 0 |
| `src/mjlab_microduck/actuator/friction_dr_bam.py` | Python | `FrictionDRBamActuator`, `FrictionDRBamActuatorCfg`, `BacklashEncoderBamActuator` (+1) | `FrictionDRBamActuator.initialize()`, `FrictionDRBamActuator._compute_friction_budget()`, `FrictionDRBamActuator.set_friction_scale()` (+5) | 14 |
| `src/mjlab_microduck/export.py` | Python | `ExportConfig`, `ExportResult` | `_iteration_of()`, `run_export()`, `main()` | 42 |
| `src/mjlab_microduck/hf_jobs.py` | Python | - | `_wandb_api_key()`, `_repo_root()`, `_build_tarball()` (+3) | 65 |
| `src/mjlab_microduck/publish/__init__.py` | Python | - | - | 0 |
| `src/mjlab_microduck/publish/cli.py` | Python | `PublishConfig` | `_fail()`, `_resolve_weights()`, `_default_name()` (+2) | 29 |
| `src/mjlab_microduck/publish/manifest.py` | Python | `ManifestError`, `Provenance`, `OnnxShape` | `Provenance.as_dict()`, `_now_utc()`, `git_provenance()` (+8) | 84 |
| `src/mjlab_microduck/robot/__init__.py` | Python | - | - | 0 |
| `src/mjlab_microduck/robot/microduck/add_backlash.py` | Python | - | `build_backlash_default()`, `main()` | 13 |
| `src/mjlab_microduck/robot/microduck_constants.py` | Python | - | `get_walk_spec()`, `get_standup_spec()`, `get_ground_pick_spec()` (+8) | 15 |
| `src/mjlab_microduck/robot/testbench_constants.py` | Python | - | `_set_arm_mass()`, `get_testbench_spec()` | 5 |
| `src/mjlab_microduck/sim/__init__.py` | Python | - | - | 0 |
| `src/mjlab_microduck/sim/body_server.py` | Python | `World`, `Body`, `Handler` (+1) | `duck_prefix()`, `build_world()`, `pose_table()` (+18) | 100 |
| `src/mjlab_microduck/sim/camera.py` | Python | `Camera`, `FrameHandler`, `FrameServer` | `to_uyvy()`, `Camera.__init__()`, `Camera.render()` (+2) | 18 |
| `src/mjlab_microduck/sim/tof.py` | Python | `Tof` | `Tof.__init__()`, `Tof.frame()` | 17 |
| `src/mjlab_microduck/tasks/__init__.py` | Python | `MicroduckOnPolicyRunner` | `MicroduckOnPolicyRunner.__init__()` | 6 |
| `src/mjlab_microduck/tasks/backlash.py` | Python | - | `make_backlash_variant()` | 9 |
| `src/mjlab_microduck/tasks/distill.py` | Python | `PpoWithExpertBcCfg`, `PpoWithExpertBc` | `default_bc_cfg()`, `fallen_mask_from_obs()`, `expert_input()` (+5) | 34 |
| `src/mjlab_microduck/tasks/mdp.py` | Python | `VelocityCommandCommandOnly`, `VelocityCommandCommandOnlyCfg`, `RelativeHeadingVelocityCommand` (+7) | `_nan_safe_reward_compute()`, `_safe_compute_returns()`, `_get_base_metadata_no_passive()` (+255) | 548 |
| `src/mjlab_microduck/tasks/microduck_ball_kick_env_cfg.py` | Python | - | `make_microduck_ball_kick_env_cfg()` | 20 |
| `src/mjlab_microduck/tasks/microduck_ground_pick_env_cfg.py` | Python | - | `make_microduck_ground_pick_env_cfg()` | 21 |
| `src/mjlab_microduck/tasks/microduck_roller_crouch_env_cfg.py` | Python | - | `make_microduck_roller_crouch_env_cfg()` | 17 |
| `src/mjlab_microduck/tasks/microduck_roller_slope_env_cfg.py` | Python | - | `_resolve_play_difficulty()`, `make_microduck_roller_slope_env_cfg()` | 13 |
| `src/mjlab_microduck/tasks/microduck_roller_standup_env_cfg.py` | Python | - | `_resolve_play_face_up()`, `make_microduck_roller_standup_env_cfg()` | 9 |
| `src/mjlab_microduck/tasks/microduck_roulade_env_cfg.py` | Python | - | `make_microduck_roulade_env_cfg()` | 21 |
| `src/mjlab_microduck/tasks/microduck_sitstand_env_cfg.py` | Python | - | `make_microduck_sitstand_env_cfg()` | 24 |
| `src/mjlab_microduck/tasks/microduck_spin_env_cfg.py` | Python | - | `make_microduck_spin_env_cfg()` | 17 |
| `src/mjlab_microduck/tasks/microduck_standup_env_cfg.py` | Python | - | `make_microduck_standup_env_cfg()` | 30 |
| `src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py` | Python | - | `_soften_terrain_contacts()`, `make_microduck_velocity_env_cfg()` | 28 |
| `src/mjlab_microduck/tasks/microduck_velocity_rollers_env_cfg.py` | Python | - | `make_microduck_velocity_rollers_env_cfg()` | 18 |
| `src/mjlab_microduck/tasks/microduck_velocity_swizzle_env_cfg.py` | Python | - | `make_microduck_velocity_swizzle_env_cfg()` | 10 |
| `src/mjlab_microduck/tasks/microduck_velstand_env_cfg.py` | Python | - | `_collapse_curricula_to_final()`, `make_microduck_velstand_env_cfg()` | 17 |
| `src/mjlab_microduck/tasks/slope_terrain.py` | Python | `FlatRampTerrainCfg` | `ramp_angle_by_difficulty()`, `FlatRampTerrainCfg.function()` | 3 |
| `src/mjlab_microduck/tasks/symmetry.py` | Python | `PpoWithSymmetryCfg` | `_get_tensors()`, `microduck_vel_symmetry()` | 6 |
| `src/mjlab_microduck/tasks/testbench_env_cfg.py` | Python | `TargetAngleCommand`, `TargetAngleCommandCfg` | `TargetAngleCommand.__init__()`, `TargetAngleCommand.command()`, `TargetAngleCommand._resample_command()` (+4) | 10 |
| `src/mjlab_microduck/train_cli.py` | Python | - | `main()` | 1 |
| `src/mjlab_microduck/train_hook.py` | Python | - | `_invoked_as_train()`, `maybe_submit_to_hf_jobs()` | 5 |
| `tests/test_aarch64_cuda_torch.py` | Python | - | `_packages()`, `_registry()`, `_markers()` (+8) | 18 |
| `tests/test_crouch_glide.py` | Python | - | `test_crouch_height_target_endpoints_are_high()`, `test_crouch_height_target_plateau_is_low()`, `test_crouch_height_target_descent_midpoint()` (+7) | 10 |
| `tests/test_descent_speed.py` | Python | `_Data`, `_Asset`, `_Env` | `_Data.__init__()`, `_Asset.__init__()`, `_Env.__init__()` (+5) | 11 |
| `tests/test_ground_pick_cfg.py` | Python | - | `test_ground_pick_cfg_task_space_rewards()`, `test_ground_pick_mouth_payload_wired()`, `test_ground_pick_cfg_command_is_phase()` (+2) | 8 |
| `tests/test_ground_pick_pose.py` | Python | `_FakeData`, `_FakeAsset`, `_FakeCmdMgr` (+1) | `test_phase_pose_blend_keypoints()`, `test_phase_pose_blend_range()`, `_FakeData.__init__()` (+11) | 19 |
| `tests/test_head_pose_bias.py` | Python | `_Data`, `_Asset`, `_Terrain` (+3) | `_Data.__init__()`, `_Asset.__init__()`, `_Terrain.__init__()` (+15) | 26 |
| `tests/test_hf_jobs_flag.py` | Python | - | `_our_scripts()`, `test_train_script_stays_declared()`, `test_our_train_script_only_delegates_to_mjlab()` (+10) | 15 |
| `tests/test_infer_policy_bam.py` | Python | - | `ip()`, `test_cpu_bam_constants_mirror_training_cfg()`, `bam_sim()` (+2) | 7 |
| `tests/test_nan_guard.py` | Python | `_Data`, `_Asset`, `_Scene` (+1) | `_Data.__init__()`, `_Asset.__init__()`, `_Scene.__init__()` (+6) | 13 |
| `tests/test_obs_nan_guard.py` | Python | `_SensorData`, `_Sensor`, `_Scene` (+3) | `_SensorData.__init__()`, `_Sensor.__init__()`, `_Scene.__init__()` (+13) | 25 |
| `tests/test_publish_manifest.py` | Python | - | `_tiny_policy()`, `test_constants_are_the_daemons()`, `test_publish_is_a_declared_script()` (+15) | 23 |
| `tests/test_roller_crouch_cfg.py` | Python | - | `test_cfg_uses_phase_command()`, `test_cfg_has_crouch_and_forward_rewards()`, `test_entry_velocity_applied_safely_via_reset_base()` | 7 |
| `tests/test_roller_slope_cfg.py` | Python | - | `test_terrain_is_flat_ramp_generator()`, `test_command_is_neutralised()`, `test_rolling_entry_no_base_push()` (+9) | 16 |
| `tests/test_roller_standup_cfg.py` | Python | - | `test_env_builds_train_and_play()`, `test_episode_is_short()`, `test_no_skating_rewards_survive()` (+34) | 53 |
| `tests/test_slope_curriculum.py` | Python | - | `test_move_up_when_reached_bottom()`, `test_move_down_when_stuck_early()`, `test_stay_in_middle_band()` (+1) | 10 |
| `tests/test_slope_terrain.py` | Python | - | `test_ramp_angle_endpoints()`, `test_ramp_angle_midpoint()`, `test_ramp_angle_clamps_out_of_range()` (+6) | 10 |
| `tests/test_spin.py` | Python | `_FakeData`, `_FakeEntity`, `_FakeCommandManager` (+3) | `test_spin_rate_segment_boundaries()`, `test_spin_rate_accel_ramp_is_increasing()`, `test_spin_rate_brake_ramp_is_decreasing()` (+32) | 48 |
| `tests/test_spin_cfg.py` | Python | - | `test_cfg_uses_phase_command_with_runtime_default_period()`, `test_cfg_has_the_spin_rewards()`, `test_stay_in_place_is_attenuated_during_the_launch_ramp()` (+7) | 14 |
| `tests/test_swizzle_head_cfg.py` | Python | - | `test_swizzle_head_control_wired()` | 4 |
| `tests/test_velstand_cfg.py` | Python | `_Data`, `_Asset`, `_Env` (+3) | `_geom_names()`, `test_allcollisions_servo_geoms_are_named()`, `test_allcollisions_matches_groundcontact_kinematics()` (+30) | 67 |
| `tests/test_wheel_glide.py` | Python | `_Data`, `_Asset`, `_Env` | `_Data.__init__()`, `_Asset.__init__()`, `_Asset.find_joints()` (+7) | 13 |
