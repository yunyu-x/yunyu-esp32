# Microduck 机器人技术资料库与工程资产枢纽

> **工程定位**: 专为 `yunyu-esp32` 项目打造的 Microduck（Open Duck Mini）双足/双轮自适应机器人全生命周期技术储备中心。
> **产品化标准**: 严格遵循工业级产品化考虑（“大脑”与“小脑”解耦、1Mbps 舵机抗扰总线、硬实时 50Hz 闭环、非对称强化学习、行为树语义规划、DFM 可制造性与产线 EOL 测试）。
> **分析工具链**: 基于 `open-source-repo-analyzer`（多语言 AST 拓扑提取、三阶沙箱探活、代码打包与跨项目隔离适配器生成）。

---

## 📂 目录全景与资产清单 (Repository Map)

```text
D:\workspace\code\yunyu-esp32\microduck\
├── README.md                                 # 本枢纽导航总览
├── .gitignore                                # 物理隔离规则 (防止上万个外部文件污染主仓)
│
├── docs/                                     # 核心技术文档体系 (共 10 份硬核技术规范)
│   ├── 【基础系统架构与物理总线】
│   ├── 01_Microduck_Full_Ecosystem_Architecture.md # 7大守护进程解耦、Unix Socket IPC
│   ├── 02_Microduck_Hardware_Actuation_and_Bus_Spec.md # 15舵机矩阵、1Mbps半双工UART时序
│   ├── 03_Microduck_RL_Training_and_Sim2Real_Pipeline.md # 61维观测、14维动作、ONNX导出
│   ├── 04_ESP32_Adaptation_and_Porting_Feasibility.md # ESP32-S3算力测算、双核任务分配路线
│   ├── 05_BOM_and_3D_Printing_Replication_Guide.md # 全量物料清单、3D打印参数、组装校准
│   │
│   ├── 【严格产品化与前瞻设计 (Productization & Production Standard)】
│   ├── 06_Productization_Brain_Cerebellum_Architecture.md # 大脑-小脑架构、BCP二进制协议、时延补偿与容灾
│   ├── 07_Actuator_Bus_and_Motor_Driver_Engineering.md # 舵机驱动与总线工程、电气抗扰、堵转与热保护阶梯
│   ├── 08_RL_Locomotion_and_Sim2Real_Production_Guide.md # 强化学习非对称训练、奖励工程、域随机化与端侧量化
│   ├── 09_Cognitive_Planning_and_Multimodal_Interaction.md # 行为树规划、多模态语义理解、声动协同与视线追踪
│   ├── 10_Product_Reliability_DFM_and_Quality_Standard.md # 注塑模具 DFM、BMS 软启动电源管理与产线测试治具
│   ├── 11_Multi_Skill_ESP32_Edge_RL_Scientific_Validation.md # 多技能全局交叉论证：ESP32-S3 端侧强化学习运动控制可行性科学白皮书
│   └── 12_M5StickS3_Microduck_Turnkey_Build_Guide.md # 【手搓全案】M5StickS3 专版淘宝采购、仿真装配与自主行走落地指南
│
├── adapters/                                 # 跨项目安全隔离调用适配器与强类型协议头
│   ├── m5sticks3_servo_tool.ino              # M5StickS3 屏幕交互式飞特舵机编址、零位标定与电压巡检固件
│   ├── m5sticks3_cpg_walk.ino                # M5StickS3 50Hz 律动自主行走控制与动态眼球表情交互固件
│   ├── benchmark_esp32_rl_feasibility.py     # 科学基准仿真脚本 (周期精确/INT8量化误差/奈奎斯特/总线时序)
│   ├── brain_cerebellum_protocol.py          # Python 完整 BCP 二进制协议栈 (CRC16/序列号/心跳)
│   ├── brain_cerebellum_protocol.h           # C/C++ 强类型头文件 (直接供 ESP32 PlatformIO 引入)
│   ├── actuator_bus_manager.py               # 舵机总线状态机、热降额、堵转检测与一阶丢包外推
│   ├── behavior_tree_planner.py              # 轻量级行为树规划引擎 (语义抽取/安全打断/声动包络)
│   ├── microduck_observation_adapter.py      # 61维观测向量组装与 14维动作反解参考实现
│   ├── duck_config_adapter.py                # 动态加载器 (避免 sys.path 污染)
│   └── robotctl_adapter.py                   # polyglot CLI 进程间适配器
│
├── analysis/                                 # 由 repo_analyze / repo_pack 自动化分析产物
│   ├── microduck_architecture.md             # 官方 microduck 源码拓扑与 176 模块依赖图
│   ├── microduck_context.xml                 # 官方仓 XML 格式 LLM 上下文打包 (150k tokens)
│   ├── microduck_skeleton.md                 # 官方仓 AST 骨架化摘要 (84k tokens)
│   ├── microduck_simulation_audit.md         # 官方仓沙箱编译与入口 Dry-run 探活审计台账
│   ├── microduck_rl_architecture.md          # 训练仓 mjlab 架构与 71 模块拓扑图
│   ├── microduck_rl_context.xml              # 训练仓 XML 格式打包 (154k tokens)
│   ├── microduck_rl_skeleton.md              # 训练仓 AST 骨架化摘要 (80k tokens)
│   ├── Open_Duck_Mini_architecture.md        # 结构与硬件仓 86 模块依赖图
│   ├── Open_Duck_Mini_Runtime_architecture.md# 嵌入式 Python 运行时 35 模块依赖图
│   ├── Open_Duck_Playground_architecture.md  # MuJoCo 仿真游乐场 23 模块依赖图
│   └── Open_Duck_reference_motion_generator_architecture.md # 步态发生器架构分析
│
└── [已克隆的开源项目源码区 (受 .gitignore 保护，独立完整)]
    ├── microduck/                            # Pollen Robotics 官方 Rust 核心守护进程栈
    ├── microduck_rl/                         # 官方强化学习训练框架 (MuJoCo Warp + PPO)
    ├── microduck-gst-plugins/                # 硬件加速 GStreamer 插件与 WebRTC
    ├── duck_detector/                        # 端侧 NPU 视觉目标检测模型
    ├── Open_Duck_Blender/                    # 3D 骨骼绑定、FK/IK 动画与 RL 参考记录器
    ├── Open_Duck_Mini/                       # 硬件 CAD、3D 打印 STL、BOM、BEST_WALK_ONNX 权重
    ├── Open_Duck_Mini_Runtime/               # 嵌入式轻量级 Python/C 运行环境
    ├── Open_Duck_Playground/                 # MuJoCo 仿真基准与任务环境
    └── Open_Duck_reference_motion_generator/ # 多项式拟合参考步态生成器
```

---

## 🎯 严格产品化核心技术结论 (Productization Architecture Highlights)

### 1. “大脑”与“小脑”硬实时分工与协议契约
- **小脑 (Cerebellum, ESP32-S3)**: 专职负责 50Hz 硬实时控制闭环（20.0ms 周期，控制抖动 $< 50\mu\text{s}$）。利用 Core 1 运行 `task_locomotion_loop`，执行 1Mbps 舵机读写、IMU 状态估计、61 维观测组装、19.7 万参数 MLP 策略推理（耗时 $< 1.5\text{ms}$）与多级安全自愈门禁；
- **大脑 (Forebrain, SBC / 云端百炼)**: 负责非抢占式高带宽任务（多模态感知、320x320 目标检测、8x8 ToF 避障、阿里云百炼实时拟人语音对话、行为树调度）；
- **BCP 二进制协议**: 废除 ASCII 串口，采用 `0xAA 0x55` 帧头 + 36 字节下行意图 / 20 字节上行遥测 + CRC16-CCITT 校验。具备心跳保活与 4 级阶梯式降级自愈（100ms 速度衰减 -> 300ms 阻尼下蹲入安全休眠）。

### 2. 舵机总线抗扰、热保护与零位齿隙消除
- **硬件收发器**: 废弃高误码率的开漏电路，采用工业级三态逻辑芯片（74LVC2G241），搭配 ESP32 硬件自动 RS-485 方向流控；
- **总线时序分解**: Fast Sync Read (0x8A) 在 3.5ms 内完成 16 设备读取，Sync Write (0x83) 耗时 0.85ms，20ms 控制周期内留存高达 **68.2% 的安全裕量**；
- **多级热保护与堵转检测**: 设定 55°C (轻度限速) -> 65°C (扭矩削减 50%) -> 75°C (紧急热断电) 保护曲线；持续 400ms 电流 $> 1.4\text{A}$ 判定为堵转并削减扭矩；
- **BAM 齿隙补偿**: 针对减速箱 0.5°~1.2° 反向齿隙，在速度反向时注入前馈死区脉冲，彻底消除足端晃动。

### 3. 非对称强化学习与 Sim-to-Real 闭环
- **非对称 PPO**: 训练期 Critic 输入包含真实接触反力、摩擦锥与地形落差的特权状态（128+ 维），Actor 仅使用端侧可观测物理量（61 维），实现真正的零样本实机盲跑（Zero-Shot Sim2Real）；
- **多目标奖励塑造**: 采用高斯核线速度与角速度跟踪、足端水平滑动严惩、动作二阶加加速度平滑与能耗惩罚；
- **内嵌归一化与端侧量化**: 导出的 ONNX 内嵌 Running Mean/Variance，端侧无需预处理；INT8 向量量化后模型体积仅 **198 KB**，单次推理 **0.6 ms**。

### 4. 认知规划与声动协同 (Bailian + Behavior Tree)
- **行为树抢占调度**: 树结构分层裁决（安全台阶防跌落与倾角防摔 > 用户语音任务执行 > 待机生命感微动）；
- **声动同步 (Beak-Sync)**: 实时提取音频流 20ms RMS 短时能量均方根，动态映射鸟喙开合角度（0°~30°），音画同步；
- **稳像注视 (Gaze Tracking)**: 头部姿态解耦补偿算法消除行走颠簸，保持视线与镜头稳固注视目标。

### 5. 硬件 DFM、BMS 电源管理与产线质检
- **注塑 DFM**: 壁厚均匀 2.0~2.5mm，脱模斜度 $\ge 1.5^\circ$，主承重骨骼采用 PC+ABS 或 PA66+15%GF，脚底双色注塑 50 度硅胶/TPE 缓冲垫；
- **BMS 软启动与瞬态吸收**: P-MOS 缓充电路消除 XT30 插入电弧，SMBJ12A TVS + 1000µF 固态电容钳位舵机急停反电动势尖峰；
- **产线四工位自动化测试 (EOL)**: 1) 电气巡检；2) 工装标定与 NVS 零位固化；3) 10分钟动态步态老化与振动声学质检；4) 工厂锁定出厂。

---

## 🚀 推荐起步阅读顺序

1. [06_Productization_Brain_Cerebellum_Architecture.md](docs/06_Productization_Brain_Cerebellum_Architecture.md)：理解系统全局分层与 BCP 协议
2. [07_Actuator_Bus_and_Motor_Driver_Engineering.md](docs/07_Actuator_Bus_and_Motor_Driver_Engineering.md)：理解舵机总线抗扰、热设计与驱动时序
3. [08_RL_Locomotion_and_Sim2Real_Production_Guide.md](docs/08_RL_Locomotion_and_Sim2Real_Production_Guide.md)：理解强化学习训练与端侧推理量化
4. [09_Cognitive_Planning_and_Multimodal_Interaction.md](docs/09_Cognitive_Planning_and_Multimodal_Interaction.md)：理解语音大模型与行为树交互联动
5. [10_Product_Reliability_DFM_and_Quality_Standard.md](docs/10_Product_Reliability_DFM_and_Quality_Standard.md)：指导量产开模、供电可靠性与产线工装测试
6. [11_Multi_Skill_ESP32_Edge_RL_Scientific_Validation.md](docs/11_Multi_Skill_ESP32_Edge_RL_Scientific_Validation.md)：【核心白皮书】多技能全局交叉论证 ESP32-S3 端侧强化学习 50Hz 闭环可行性科学推导与实测台账
