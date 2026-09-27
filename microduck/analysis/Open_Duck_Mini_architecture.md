# Architectural Analysis & Learning Guide: Open_Duck_Mini

> 自动化生成的开源项目架构全景图、多语言符号契约与递进式学习路线图。

## 1. 核心技术栈与外部依赖
- **源码模块总数**: 86
- **外部第三方库**: FramesViewer, argparse, bam, cv2, datetime, glob, gymnasium, h5py, imitation, inputs, ischedule, json, math, matplotlib, mini_bdx_runtime, mujoco, mujoco_viewer, numpy, os, pickle, placo, placo_record_amp, placo_utils, pprint, pygame, pypot, queue, sb3_contrib, scipy, stable_baselines3, threading, time, typing, utils, warnings

## 2. 系统架构调用拓扑图 (Mermaid Topology)
```mermaid
graph TD
    experiments_LeRobot_new_record_episodes_hdf5_NOT_WORKING_py["experiments/LeRobot/new_record_episodes_hdf5_NOT_WORKING.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_LeRobot_new_record_episodes_hdf5_NOT_WORKING_py["experiments/LeRobot/new_record_episodes_hdf5_NOT_WORKING.py"] --> mini_bdx_mini_bdx_old_walk_engine_walk_engine_py["mini_bdx/mini_bdx/old_walk_engine/walk_engine.py"]
    experiments_LeRobot_record_episodes_hdf5_py["experiments/LeRobot/record_episodes_hdf5.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_LeRobot_record_episodes_hdf5_py["experiments/LeRobot/record_episodes_hdf5.py"] --> mini_bdx_mini_bdx_utils_xbox_controller_py["mini_bdx/mini_bdx/utils/xbox_controller.py"]
    experiments_LeRobot_record_episodes_hdf5_py["experiments/LeRobot/record_episodes_hdf5.py"] --> mini_bdx_mini_bdx_old_walk_engine_walk_engine_py["mini_bdx/mini_bdx/old_walk_engine/walk_engine.py"]
    experiments_RL_env_py["experiments/RL/env.py"] --> mini_bdx_mini_bdx_old_walk_engine_walk_engine_py["mini_bdx/mini_bdx/old_walk_engine/walk_engine.py"]
    experiments_RL_env_humanoid_py["experiments/RL/env_humanoid.py"] --> mini_bdx_mini_bdx_old_walk_engine_walk_engine_py["mini_bdx/mini_bdx/old_walk_engine/walk_engine.py"]
    experiments_RL_new_footsteps_env_py["experiments/RL/new/footsteps_env.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_RL_new_footsteps_env_py["experiments/RL/new/footsteps_env.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_RL_new_placo_imitate_env_py["experiments/RL/new/placo_imitate_env.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_RL_new_placo_imitate_env_py["experiments/RL/new/placo_imitate_env.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_RL_new_record_episodes_py["experiments/RL/new/record_episodes.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_RL_new_record_episodes_amp_py["experiments/RL/new/record_episodes_amp.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_RL_new_record_episodes_amp_py["experiments/RL/new/record_episodes_amp.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_RL_new_record_episodes_amp_py["experiments/RL/new/record_episodes_amp.py"] --> mini_bdx_mini_bdx_utils_rl_utils_py["mini_bdx/mini_bdx/utils/rl_utils.py"]
    experiments_RL_new_record_episodes_amp_old_py["experiments/RL/new/record_episodes_amp_old.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_RL_new_record_episodes_amp_old_py["experiments/RL/new/record_episodes_amp_old.py"] --> mini_bdx_mini_bdx_utils_rl_utils_py["mini_bdx/mini_bdx/utils/rl_utils.py"]
    experiments_RL_new_simple_env_py["experiments/RL/new/simple_env.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_RL_play_policy_py["experiments/RL/play_policy.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_RL_record_episodes_py["experiments/RL/record_episodes.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_RL_record_episodes_py["experiments/RL/record_episodes.py"] --> mini_bdx_mini_bdx_old_walk_engine_walk_engine_py["mini_bdx/mini_bdx/old_walk_engine/walk_engine.py"]
    experiments_mujoco_mujoco_placo_walk_engine_demo_py["experiments/mujoco/mujoco_placo_walk_engine_demo.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_mujoco_mujoco_placo_walk_engine_demo_py["experiments/mujoco/mujoco_placo_walk_engine_demo.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_mujoco_mujoco_placo_walk_engine_demo_py["experiments/mujoco/mujoco_placo_walk_engine_demo.py"] --> mini_bdx_mini_bdx_utils_rl_utils_py["mini_bdx/mini_bdx/utils/rl_utils.py"]
    experiments_mujoco_mujoco_placo_walk_engine_demo_py["experiments/mujoco/mujoco_placo_walk_engine_demo.py"] --> mini_bdx_mini_bdx_utils_xbox_controller_py["mini_bdx/mini_bdx/utils/xbox_controller.py"]
    experiments_mujoco_mujoco_record_amp_py["experiments/mujoco/mujoco_record_amp.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_mujoco_mujoco_record_amp_py["experiments/mujoco/mujoco_record_amp.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_mujoco_mujoco_record_amp_py["experiments/mujoco/mujoco_record_amp.py"] --> mini_bdx_mini_bdx_utils_rl_utils_py["mini_bdx/mini_bdx/utils/rl_utils.py"]
    experiments_mujoco_mujoco_walk_engine_py["experiments/mujoco/mujoco_walk_engine.py"] --> mini_bdx_mini_bdx_utils_mujoco_utils_py["mini_bdx/mini_bdx/utils/mujoco_utils.py"]
    experiments_mujoco_mujoco_walk_engine_py["experiments/mujoco/mujoco_walk_engine.py"] --> mini_bdx_mini_bdx_utils_xbox_controller_py["mini_bdx/mini_bdx/utils/xbox_controller.py"]
    experiments_mujoco_mujoco_walk_engine_py["experiments/mujoco/mujoco_walk_engine.py"] --> mini_bdx_mini_bdx_old_walk_engine_walk_engine_py["mini_bdx/mini_bdx/old_walk_engine/walk_engine.py"]
    experiments_mujoco_onnx_AMP_for_hardware_mujoco_py["experiments/mujoco/onnx_AMP_for_hardware_mujoco.py"] --> mini_bdx_mini_bdx_utils_rl_utils_py["mini_bdx/mini_bdx/utils/rl_utils.py"]
    experiments_mujoco_onnx_AMP_mujoco_py["experiments/mujoco/onnx_AMP_mujoco.py"] --> mini_bdx_mini_bdx_utils_rl_utils_py["mini_bdx/mini_bdx/utils/rl_utils.py"]
    experiments_placo_auto_placo_record_amp_py["experiments/placo/auto_placo_record_amp.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
    experiments_placo_placo_record_amp_py["experiments/placo/placo_record_amp.py"] --> mini_bdx_mini_bdx_placo_walk_engine_placo_walk_engine_py["mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py"]
```

> ℹ️ *已截取前 35 条关键依赖边以保证前端 Mermaid 渲染稳定性。*

## 3. 递进式学习与精读路线图 (Progressive Learning Roadmap)

### 📍 Stage 1: Core Primitives & Foundation Models (核心实体与基础数据模型)
*Start here to understand data schemas, interfaces, and atomic utilities.*

- [x] `experiments/RL/new/pretrain_bc.py`
- [x] `experiments/RL/new/pretrain_gail.py`
- [x] `experiments/RL/new/record_episodes_amp_old.py`
- [x] `experiments/RL/pretrain_bc.py`
- [x] `experiments/RL/pretrain_gail.py`
- [x] `experiments/RL/view_hdf5.py`
- [x] `experiments/identification/check_speed.py`
- [x] `experiments/identification/get_data.py`
- [x] `experiments/identification/plot.py`
- [x] `experiments/identification/plot_action_obs.py`
- [x] `experiments/identification/plot_obs.py`
- [x] `experiments/identification/plot_speeds.py`
- [x] `experiments/identification/utils.py`
- [x] `experiments/mujoco/plot_latent.py`
- [x] `experiments/placo/auto_placo_record_amp.py`
- [x] `experiments/placo/bdx_walk.py`
- [x] `experiments/placo/generate_orientations_amp.py`
- [x] `experiments/placo/replay_amp.py`
- [x] `experiments/placo/test_bdx.py`
- [x] `experiments/placo/test_placo_hwi_tmp.py`
- [x] `experiments/real_robot/imu_gyro.py`
- [x] `experiments/real_robot/move_test.py`
- [x] `experiments/real_robot/new_run.py`
- [x] `experiments/real_robot/plot.py`
- [x] `experiments/real_robot/plot_imu.py`
- [x] `experiments/real_robot/pressure_test.py`
- [x] `experiments/real_robot/raw_imu_gyro.py`
- [x] `experiments/v2/bench_com_time.py`

### 📍 Stage 2: Business Logic & Processing Pipelines (核心算法与逻辑处理)
*Understand core domain state machines, algorithms, and orchestration logic.*

- [x] `experiments/v2/configure_motors.py`
- [x] `experiments/v2/identification.py`
- [x] `experiments/v2/placo_walk_real_robot.py`
- [x] `experiments/v2/plot.py`
- [x] `experiments/v2/plot_adaptation_module_latent.py`
- [x] `experiments/v2/test.py`
- [x] `experiments/v2/walk_test.py`
- [x] `mini_bdx/__init__.py`
- [x] `mini_bdx/mini_bdx/__init__.py`
- [x] `mini_bdx/mini_bdx/old_walk_engine/__init__.py`
- [x] `mini_bdx/mini_bdx/placo_walk_engine/__init__.py`
- [x] `mini_bdx/mini_bdx/utils/__init__.py`
- [x] `experiments/RL/new/record_episodes_amp.py`
- [x] `experiments/RL/pretrain_dbrm.py`
- [x] `experiments/RL/replay_episodes.py`
- [x] `experiments/mujoco/mujoco_record_amp.py`
- [x] `experiments/placo/placo_record_amp_moves.py`
- [x] `experiments/placo/placo_walk_engine_test.py`
- [x] `experiments/real_robot/replay_imu_data.py`
- [x] `experiments/v2/mujoco_placo_walk.py`
- [x] `experiments/v2/placo_fun_moves.py`
- [x] `experiments/RL/new/train.py`
- [x] `experiments/RL/train.py`
- [x] `experiments/v2/test_understand_isaac_mujoco_transfer.py`
- [x] `experiments/placo/placo_walk_engine_mujoco.py`
- [x] `experiments/real_robot/rl_walk.py`
- [x] `experiments/real_robot/utils.py`
- [x] `experiments/v2/test_understand_isaac_mujoco_transfer_motor_control.py`
- [x] `mini_bdx/mini_bdx/utils/rl_utils.py`

### 📍 Stage 3: Entrypoints & Client Interfaces (系统入口与外部接口)
*Trace main application lifecycles, CLI runners, and consumer API surfaces.*

- [x] `experiments/LeRobot/new_record_episodes_hdf5_NOT_WORKING.py`
- [x] `experiments/RL/new/record_episodes.py`
- [x] `experiments/real_robot/run.py`
- [x] `experiments/mujoco/mujoco_placo_walk_engine_demo.py`
- [x] `experiments/RL/old_test.py`
- [x] `experiments/anti_gravity_leg/anti_gravity.py`
- [x] `experiments/mujoco/onnx_AMP_mujoco.py`
- [x] `experiments/v2/pwm_control_test.py`
- [x] `experiments/v2/onnx_AWD_mujoco.py`
- [x] `experiments/LeRobot/record_episodes_hdf5.py`
- [x] `experiments/RL/new/eval.py`
- [x] `experiments/RL/play_policy.py`
- [x] `experiments/RL/new/eval_simple.py`
- [x] `experiments/RL/record_episodes.py`
- [x] `experiments/mujoco/onnx_AMP_for_hardware_mujoco.py`
- [x] `experiments/v2/onnx_AWD_mujoco_motor_control.py`
- [x] `experiments/placo/placo_record_amp.py`
- [x] `mini_bdx/mini_bdx/utils/mujoco_utils.py`
- [x] `experiments/RL/new/placo_imitate_env.py`
- [x] `experiments/RL/env_humanoid.py`
- [x] `experiments/mujoco/mujoco_walk_engine.py`
- [x] `experiments/RL/env.py`
- [x] `experiments/RL/new/simple_env.py`
- [x] `experiments/RL/new/env.py`
- [x] `experiments/RL/new/footsteps_env.py`
- [x] `mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py`
- [x] `mini_bdx/mini_bdx/utils/xbox_controller.py`
- [x] `mini_bdx/mini_bdx/old_walk_engine/walk_engine.py`
- [x] `mini_bdx/mini_bdx/utils/poly_spline.py`

## 4. 关键导出符号与公共 API 矩阵 (Universal Symbols & Complexity)

| 模块文件 | 语言 | 类/结构体 | 关键函数/方法 | 圈复杂度总计 |
| :--- | :---: | :--- | :--- | :---: |
| `experiments/LeRobot/new_record_episodes_hdf5_NOT_WORKING.py` | Python | - | `key_callback()`, `start_stop_recording()` | 5 |
| `experiments/LeRobot/record_episodes_hdf5.py` | Python | - | `key_callback()`, `start_stop_recording()`, `xbox_input()` (+2) | 11 |
| `experiments/RL/env.py` | Python | `BDXEnv` | `BDXEnv.__init__()`, `BDXEnv.check_contact()`, `BDXEnv.smoothness_reward()` (+11) | 35 |
| `experiments/RL/env_humanoid.py` | Python | `BDXEnv` | `mass_center()`, `BDXEnv.__init__()`, `BDXEnv.check_contact()` (+6) | 24 |
| `experiments/RL/new/env.py` | Python | `BDXEnv` | `BDXEnv.__init__()`, `BDXEnv.check_contact()`, `BDXEnv.feet_contact_reward()` (+13) | 39 |
| `experiments/RL/new/eval.py` | Python | - | `draw_clock()`, `draw_frame()`, `test()` | 11 |
| `experiments/RL/new/eval_simple.py` | Python | - | `draw_clock()`, `draw_frame()`, `draw_velocities()` (+1) | 12 |
| `experiments/RL/new/footsteps_env.py` | Python | `BDXEnv` | `BDXEnv.__init__()`, `BDXEnv.is_terminated()`, `BDXEnv.gait_reward()` (+12) | 50 |
| `experiments/RL/new/placo_imitate_env.py` | Python | `BDXEnv` | `BDXEnv.__init__()`, `BDXEnv.is_terminated()`, `BDXEnv.get_feet_contact()` (+9) | 23 |
| `experiments/RL/new/pretrain_bc.py` | Python | - | - | 0 |
| `experiments/RL/new/pretrain_gail.py` | Python | - | - | 0 |
| `experiments/RL/new/record_episodes.py` | Python | - | `run()` | 5 |
| `experiments/RL/new/record_episodes_amp.py` | Python | - | `get_feet_contact()` | 1 |
| `experiments/RL/new/record_episodes_amp_old.py` | Python | - | - | 0 |
| `experiments/RL/new/simple_env.py` | Python | `BDXEnv` | `BDXEnv.__init__()`, `BDXEnv.is_terminated()`, `BDXEnv.support_flying_reward()` (+14) | 38 |
| `experiments/RL/new/train.py` | Python | - | `train()` | 3 |
| `experiments/RL/old_test.py` | Python | - | `test()` | 8 |
| `experiments/RL/play_policy.py` | Python | - | `get_observation()`, `key_callback()`, `get_model_from_dir()` (+2) | 11 |
| `experiments/RL/pretrain_bc.py` | Python | - | - | 0 |
| `experiments/RL/pretrain_dbrm.py` | Python | - | `print_stats()` | 1 |
| `experiments/RL/pretrain_gail.py` | Python | - | - | 0 |
| `experiments/RL/record_episodes.py` | Python | - | `xbox_input()`, `key_callback()`, `get_observation()` (+3) | 12 |
| `experiments/RL/replay_episodes.py` | Python | - | `key_callback()` | 1 |
| `experiments/RL/train.py` | Python | - | `train()` | 3 |
| `experiments/RL/view_hdf5.py` | Python | - | - | 0 |
| `experiments/anti_gravity_leg/anti_gravity.py` | Python | - | `current_to_torque()`, `torque_to_current()`, `torque_to_current2()` (+2) | 8 |
| `experiments/identification/check_speed.py` | Python | - | - | 0 |
| `experiments/identification/get_data.py` | Python | - | - | 0 |
| `experiments/identification/plot.py` | Python | - | - | 0 |
| `experiments/identification/plot_action_obs.py` | Python | - | - | 0 |
| `experiments/identification/plot_obs.py` | Python | - | - | 0 |
| `experiments/identification/plot_speeds.py` | Python | - | - | 0 |
| `experiments/identification/utils.py` | Python | - | - | 0 |
| `experiments/mujoco/mujoco_placo_walk_engine_demo.py` | Python | - | `get_feet_contact()`, `xbox_input()`, `keyboard_input()` | 7 |
| `experiments/mujoco/mujoco_record_amp.py` | Python | - | `get_feet_contact()` | 1 |
| `experiments/mujoco/mujoco_walk_engine.py` | Python | - | `xbox_input()`, `key_callback()`, `get_imu()` (+1) | 25 |
| `experiments/mujoco/onnx_AMP_for_hardware_mujoco.py` | Python | `ObsDelaySimulator` | `ObsDelaySimulator.__init__()`, `ObsDelaySimulator.push()`, `ObsDelaySimulator.get()` (+2) | 12 |
| `experiments/mujoco/onnx_AMP_mujoco.py` | Python | `ImuDelaySimulator` | `ImuDelaySimulator.__init__()`, `ImuDelaySimulator.push()`, `ImuDelaySimulator.get()` (+1) | 9 |
| `experiments/mujoco/plot_latent.py` | Python | - | - | 0 |
| `experiments/placo/auto_placo_record_amp.py` | Python | - | - | 0 |
| `experiments/placo/bdx_walk.py` | Python | - | - | 0 |
| `experiments/placo/generate_orientations_amp.py` | Python | - | - | 0 |
| `experiments/placo/placo_record_amp.py` | Python | - | `record()` | 13 |
| `experiments/placo/placo_record_amp_moves.py` | Python | - | `get_angles()` | 1 |
| `experiments/placo/placo_walk_engine_mujoco.py` | Python | - | `xbox_input()`, `key_callback()`, `get_feet_contact()` | 4 |
| `experiments/placo/placo_walk_engine_test.py` | Python | - | `xbox_input()` | 1 |
| `experiments/placo/replay_amp.py` | Python | - | - | 0 |
| `experiments/placo/test_bdx.py` | Python | - | - | 0 |
| `experiments/placo/test_placo_hwi_tmp.py` | Python | - | - | 0 |
| `experiments/real_robot/imu_gyro.py` | Python | - | - | 0 |
| `experiments/real_robot/move_test.py` | Python | - | - | 0 |
| `experiments/real_robot/new_run.py` | Python | - | - | 0 |
| `experiments/real_robot/plot.py` | Python | - | - | 0 |
| `experiments/real_robot/plot_imu.py` | Python | - | - | 0 |
| `experiments/real_robot/pressure_test.py` | Python | - | - | 0 |
| `experiments/real_robot/raw_imu_gyro.py` | Python | - | - | 0 |
| `experiments/real_robot/replay_imu_data.py` | Python | - | `reorient()` | 1 |
| `experiments/real_robot/rl_walk.py` | Python | - | `make_action_dict()`, `get_obs()` | 4 |
| `experiments/real_robot/run.py` | Python | - | `xbox_input()`, `get_imu()` | 5 |
| `experiments/real_robot/utils.py` | Python | `ImuFilter` | `ImuFilter.__init__()`, `ImuFilter.push_data()`, `ImuFilter.get_filtered_data()` | 4 |
| `experiments/v2/bench_com_time.py` | Python | - | - | 0 |
| `experiments/v2/configure_motors.py` | Python | - | - | 0 |
| `experiments/v2/identification.py` | Python | - | - | 0 |
| `experiments/v2/mujoco_placo_walk.py` | Python | - | `get_feet_contact()` | 1 |
| `experiments/v2/onnx_AWD_mujoco.py` | Python | - | `quat_rotate_inverse()`, `get_feet_contact()`, `get_obs()` (+1) | 10 |
| `experiments/v2/onnx_AWD_mujoco_motor_control.py` | Python | - | `pd_control()`, `quat_rotate_inverse()`, `get_obs()` (+3) | 12 |
| `experiments/v2/placo_fun_moves.py` | Python | - | `get_angles()` | 1 |
| `experiments/v2/placo_walk_real_robot.py` | Python | - | - | 0 |
| `experiments/v2/plot.py` | Python | - | - | 0 |
| `experiments/v2/plot_adaptation_module_latent.py` | Python | - | - | 0 |
| `experiments/v2/pwm_control_test.py` | Python | `FeetechPWMControl` | `FeetechPWMControl.__init__()`, `FeetechPWMControl.disable_torque()`, `FeetechPWMControl.enable_torque()` (+1) | 9 |
| `experiments/v2/test.py` | Python | - | - | 0 |
| `experiments/v2/test_understand_isaac_mujoco_transfer.py` | Python | - | `quat_rotate_inverse()`, `get_feet_contact()`, `get_obs()` | 3 |
| `experiments/v2/test_understand_isaac_mujoco_transfer_motor_control.py` | Python | - | `pd_control()`, `quat_rotate_inverse()`, `get_feet_contact()` (+1) | 4 |
| `experiments/v2/walk_test.py` | Python | - | - | 0 |
| `mini_bdx/__init__.py` | Python | - | - | 0 |
| `mini_bdx/mini_bdx/__init__.py` | Python | - | - | 0 |
| `mini_bdx/mini_bdx/old_walk_engine/__init__.py` | Python | - | - | 0 |
| `mini_bdx/mini_bdx/old_walk_engine/walk_engine.py` | Python | `FootPose`, `Foot`, `WalkEngine` | `FootPose.__init__()`, `FootPose.__eq__()`, `FootPose.foot_to_trunk()` (+16) | 56 |
| `mini_bdx/mini_bdx/placo_walk_engine/__init__.py` | Python | - | - | 0 |
| `mini_bdx/mini_bdx/placo_walk_engine/placo_walk_engine.py` | Python | `PlacoWalkEngine` | `PlacoWalkEngine.__init__()`, `PlacoWalkEngine.load_defaults()`, `PlacoWalkEngine.load_parameters()` (+7) | 51 |
| `mini_bdx/mini_bdx/utils/__init__.py` | Python | - | - | 0 |
| `mini_bdx/mini_bdx/utils/mujoco_utils.py` | Python | - | `check_contact()`, `get_contact_force()`, `get_actuator_name()` (+2) | 20 |
| `mini_bdx/mini_bdx/utils/poly_spline.py` | Python | `Point`, `Points`, `Polynom` (+3) | `Point.__init__()`, `Points.__init__()`, `Polynom.__init__()` (+14) | 61 |
| `mini_bdx/mini_bdx/utils/rl_utils.py` | Python | - | `isaac_to_mujoco()`, `mujoco_to_isaac()`, `test()` (+1) | 4 |
| `mini_bdx/mini_bdx/utils/xbox_controller.py` | Python | `XboxController` | `XboxController.__init__()`, `XboxController.deadzone()`, `XboxController.read()` (+1) | 51 |
