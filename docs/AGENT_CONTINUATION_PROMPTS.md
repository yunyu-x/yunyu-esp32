# 模块化继续开发 Agent 专属提示词规范与模板库 (Agent Continuation Prompt Guidelines)

> [!IMPORTANT]
> **全局工程规范 (Repository Engineering Standard)**：
> 依据项目工程规范，**后续任何 Agent 提交代码后，均必须在交付总结与交接文档中给出对应模块继续开发的标准化提示词描述**。
> 本规范旨在让跨会话、跨生命周期的后续 AI Agents 能够在 0 上下文漂移、0 硬件试错的严苛要求下，无缝承接研发任务并保持最高工程质量。

---

## 一、 新会话继续开发通用母版 (Universal Master Prompt)

开启新对话时，可直接复制此通用母版并填入具体任务：

```markdown
你好！请接手并继续推进本项目开发。在开始编写代码前，请先完整阅读工作交接文档与核心源码：
1. 核心交接文档：`docs/01_StickS3_Hardware_and_Bringup_Guide.md`
2. 提示词标准库：`docs/AGENT_CONTINUATION_PROMPTS.md`
3. 固件核心源码：`firmware/m5sticks3_buddy/src/main.cpp` 与 `include/sticks3_bailian_client.h`

【当前硬件与工程基线】：
- 硬件平台：M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)，已连接在本地串口 `COM3`，局域网 IP `192.168.110.67`。
- 核心参考文档：
  - `docs/01_StickS3_Hardware_and_Bringup_Guide.md` (全栈硬件与固件指南)
  - `docs/HANDOVER_VOICE_DIALOGUE_AND_RESOURCE_MANAGEMENT.md` (全双工语音大模型与长程记忆压缩交接文档)
- 底层已就绪：
  - M5PM1 电源门控（GPIO2 点亮 LCD 3.3V 供电，GPIO3 开启功放）已标定。
  - 按键引脚已修正为 G11 (Btn A) 与 G12 (Btn B)。
  - BMI270 姿态传感器、ES8311 音频和弦与麦克风 VU、ST7789v2 1.14" 屏幕均已点亮。
  - BLE Nordic UART (30字节广播合规包) 与 2.4GHz Wi-Fi (SoftAP/TCP/UDP/Web) 全互通。
  - 全集 23,940 条目 GBK-to-Unicode Flash 映射表已落地，手机端发送汉字已无方格子。
  - 智能 Web 配网：网页端 (`http://192.168.4.1`) 扫描周边 AP、填密入网并持久化存入 NVS，掉电开机秒级自连。
  - 阿里云百炼大模型：DashScope Realtime WebSocket (WSS) 16kHz PCM 全双工流式对话已调通，网页端自由配置 API Key、音色与模型。
  - **离线语音唤醒词「悄悄」(qiāo qiāo)**：时频 3 子带滤波 + ZCR + 叠词对称度综合评分声学引擎 (`sticks3_wakeword.h`)，零动态堆碎片，未唤醒时待命挂起推流省 Token，唤醒后即刻和弦播音并拉起 8~10 秒问答窗口；AI 发声时说「悄悄」可瞬间 Barge-In 物理打断。
  - 毫秒级中途打断 (Barge-In)：支持服务端 VAD 识别、本地硅麦能量检测、唤醒词打断与正面主键 A 物理打断，瞬间静音并发送 `response.cancel` 终止服务端生成。
  - **双级记忆压缩 (Two-Tier Compaction)**：PSRAM 平铺静态数组 (`MAX_TURNS_IN_MEMORY=8`)，零 Internal SRAM 碎片；第 9 轮触发滑动窗口自动提炼为 `[前期摘要]`；Flash NVS 持久化核心 5 轮。
  - **Unicode 字符级安全截断 (`safeTruncateUtf8`)**：彻底杜绝 UTF-8 变长多字节中文字符截断撕裂导致的 RFC 6455 1007 协议违规断连。
  - **I2C 全局互斥锁 (`g_i2c_mutex`)**：彻底隔离 BMI270/M5PM1 与 ES8311 跨核心并发冲突。
- 自动化流水线：编译与烧录自愈请统一使用 `python scripts/autonomous_bringup_agent.py` 或 `python -m platformio run -d firmware/m5sticks3_buddy`。
- 回归测试：全套 46 项自动化单元测试已就绪 (`pytest tests/ -v`)，实机 9 轮长程记忆压测使用 `python scripts/test_voice_dialogue_and_memory_compression.py`，唤醒词测试使用 `pytest tests/test_wakeword_engine.py -v`。

【本次开发目标】：
[在这里填入您的具体需求，可直接选用下方第二章节的细分方向]
```

---

## 二、 StickS3 终端细分演进方向提示词库 (StickS3 Continuation Prompts)

### 方向 1：联动 Claude Desktop 物理安全审批终端 (Claude Buddy)

```markdown
【本次开发目标】：联动 Claude Desktop 物理安全审批终端
我们需要实现 StickS3 与上位机 Claude Desktop / Claude Code 的物理审批联动。
1. 协议实现：上位机向设备发送权限请求帧（例如执行危险 bash 命令），设备解析后在屏幕上展示红色 APPROVAL 警报卡片，居中显示工具名与待执行命令；
2. 物理确认：用户在设备正面按下按键 A 执行 Approve 放行，按侧面按键 B 执行 Deny 拒绝；设备通过 BLE NUS 向电脑回传对应的确认/拦截 JSON 动作帧；
3. 上位机桥接：编写上位机守护脚本（如 `scripts/claude_buddy_host.py`），监听本地命令请求并通过 Python Bleak 自动连接 `StickS3-Buddy` 维持长连接；
4. 约束：所有蓝牙交互必须保持非阻塞临界区缓冲机制，不得在蓝牙中断上下文中执行阻塞延时或 I2C 操作。
```

---

### 方向 2：灵方 (LingCube) 微型机器人地面调测遥控台 (Ground HIL)

```markdown
【本次开发目标】：灵方微型自重构机器人地面调测遥控台
我们需要将 StickS3 扩展为灵方机器人的便携式地面无线调试终端。
1. 状态监听：通过 Wi-Fi UDP 广播 (Port 8080) 或 BLE 实时捕获环境中多个灵方机器人单体（PCBA v2.0）上报的电量、6面光通信连通状态与 MPU6050 姿态角；
2. 指令下发：利用 StickS3 的按键 A/B 短按与长按组合，向指定机器人下发动作指令（如：驱动电机转动、EPM电磁铁脉冲退磁/充磁、触发集群编队自组织步态）；
3. 界面展示：在 ST7789 屏幕上绘制微型机器人单体拓扑状态图，并沿用 `drawChineseText()` 进行清晰的中文参数标注。
```

---

### 方向 3：多页面交互与状态菜单系统 (Multi-Page UI)

```markdown
【本次开发目标】：轻量级多页面交互与状态菜单系统
我们需要为 StickS3 设计一套高响应、无闪烁的多页面切换框架。
1. 页面规划：
   - 页面 1（Default）：实时仪表盘与双轴 IMU 动态姿态水准仪；
   - 页面 2：大模型语音对话瀑布流（实时查看上下文问答历史）；
   - 页面 3：周边 2.4GHz Wi-Fi AP 深度嗅探列表（展示热点名、信道与 RSSI 信号强弱条）；
   - 页面 4：硬件底层硬件健康度看板（电池电压、CPU温度、I2C总线状态、RAM剩余）。
2. 交互逻辑：长按侧键 B（>800ms）轮询切页，短按正面按键 A 在当前页面内确认/操作；
3. 约束：所有汉字渲染必须经由 `drawChineseText()` 自动归一化，严禁出现方格子乱码。
```

---

### 方向 4：板载 MEMS 麦克风录音回传与双向音频网关 (已落地就绪 Baseline)

```markdown
【已就绪硬件能力与基线】：
- 板载 MEMS 硅麦 + ES8311 芯片已标定 16kHz 16-bit Mono 采集。
- 按键 A 单击控制 10 秒内录音，PSRAM 缓冲 320KB，自动封包 44 字节 RIFF WAV。
- Wi-Fi 网页端 (`http://192.168.4.1`) 自动探测并拉取 `/audio/device_record.wav` 原生播放。
- 网页端支持 iOS Safari 原生调起录音并重采样为 16kHz WAV POST 上传，StickS3 AW8737 功放高保真回放。
```

---

### 方向 5：阿里云百炼实时语音大模型与多轮连续对话 (已落地就绪 Baseline)

```markdown
【已就绪大模型能力与基线】：
- 网页端智能配网与 NVS 凭据持久化：AP+STA 双模运行，配置脏检查加速，开机秒级自连。
- 阿里云百炼 DashScope Realtime WSS 长连接：支持 Qwen3.8-Omni-Flash-Realtime，全双工流式 16kHz PCM 传输。
- FreeRTOS 音频任务独立解耦：Core 1 独立 `audioTask` (Prio 3)，单次写后主动 yield，环形缓冲分块 `memcpy`，主循环帧率稳定在 65~74 FPS。
- I2C 总线线程安全互斥锁 (`g_i2c_mutex`)：全面杜绝主线程与网络任务并发写 Codec/PMIC 导致的底层总线中断挂起死锁。
- 麦克风语音活动门限 (VAG)：`mic_rms >= 12%` 带 500ms 尾随缓冲，彻底解决环境底噪推流并发互斥与自激发幻觉。
- 全维度监控端点：`GET /system/metrics` 实时暴露 CPU FPS、SRAM 堆可用与最大连续块、PSRAM、I2C 锁状态；串口每 2s 打印 `[StickS3-SYS]` 诊断流。
- 毫秒级中途打断 (Barge-In) 与自然播报闭环：支持自然播放完毕自动切回 `Listening` (`finishStreamPlayback`)；中途打断 160ms 级瞬时物理静音清空缓冲并下发 `response.cancel`。
- 长程多轮极限压测已通过：实测连续 5 轮全双工问答 (`python scripts/monitor_and_stress_continuous_dialogue.py`)，0 死锁卡死、0 内存碎片耗尽、0 线程饥饿。
```

---

### 方向 6：灵方机器人语音具身控制与大模型 Agent 动作执行 (Embodied Voice AI)

```markdown
【本次开发目标】：灵方机器人语音具身控制与大模型 Agent 动作执行
我们将 StickS3 的全双工语音大模型问答能力升级为具身智能实体控制终端。
1. Function Calling / Tool Use 扩展：在百炼大模型中注册灵方机器人动作函数（例如：`move_robot(direction, speed)`、`epm_magnetize(face, pulse_ms)`、`query_robot_status()`）；
2. 语音指令意图识别：当用户对准 StickS3 说“向前翻滚两圈”或“吸附左侧机器人”，大模型识别意图并下发工具调用事件；
3. 无线控制下发：StickS3 解析工具调用后，通过 2.4GHz Wi-Fi UDP 广播 (Port 8080) 或 Grove UART 向灵方机器人单体发送执行帧，并将执行结果语音反馈给用户；
4. 屏幕反馈：在 ST7789 屏幕上高亮展示被调用的工具名称与执行状态。
```

### 方向 7：全双工长期记忆图谱与多模态情感陪伴终端 (Emotional Memory & Multimodal Companion)

```markdown
【本次开发目标】：全双工长期记忆图谱与多模态情感陪伴终端
基于已落地的 StickS3MemoryStore 两级记忆缓存与音色热切换能力，进一步演进长期记忆图谱与情感交互：
1. 实体与关系提取：在对话结束时，通过后台异步任务从对话历史中抽取用户画像（姓名、偏好、习惯、提醒事项）并结构化保存至 Flash；
2. 动态情感状态机：结合 BMI270 姿态（摇晃、抚摸、翻转）与声学情感特征，动态调节 DashScope prompt 语气与 LCD 动态表情眼睛（M5GFX 眨眼/微笑/思考）；
3. 定时主动提醒与主动搭话：利用 RTC 定时器，在特定时间或设备被拿起时，主动唤醒并用设定音色开口搭话。
```

### 方向 8：全双工声学回声自适应校准与环境降噪 (Adaptive Acoustic Echo Calibration & Streaming VAD)

```markdown
【本次开发目标】：全双工声学回声自适应校准与环境降噪
在现已落地的 ES8311 全双工时钟 (Reg 0x01=0xBF)、喇叭参考动态解耦过滤 (Coupling 0.38) 与轻量级人声触发器的基础上：
1. 声学耦合因子自适应在线估计 (Online Echo Coupling Estimation)：通过 LMS 最小均方误差算法在后台微调喇叭到麦克风的声学传递函数，自适应不同音量大小与贴近距离；
2. 频域双频段谱减降噪 (Dual-Band Spectral Subtraction)：利用 ESP32-S3 双核矢量指令 (ESP-DSP) 在麦克风采集流中快速抑制风噪与风扇底噪，提升高信噪比识别率；
3. 物理手势与晃动打断联动：结合 BMI270 六轴传感器，支持轻拍机身或摇晃手势即刻触发物理打断。
```

### 方向 9：离线语音唤醒词「悄悄」演进与声学自适应调优 (Offline Wake Word Baseline & Expansion)

```markdown
【本次开发目标】：离线语音唤醒词「悄悄」演进与声学自适应调优
基于已就绪的 Sticks3WakeWordEngine「悄悄」时频声学引擎 (3 子带滤波 + ZCR + 叠词对称度综合评分)：
1. 声学模型增强：在现有 3 子带滤波基础上，引入 6 子带能量包络或简易 MFCC-8 倒谱距离匹配，提升不同语速、方言口音与童声的唤醒召回率；
2. 动态环境噪声底噪跟踪：在 `IDLE` 状态下使用指数加权移动平均 (EMA) 动态校准环境底噪，动态浮动 `min_rms_q` 与 `min_rms_iao`，保证喧闹环境下不漏唤醒、宁静环境下不误触发；
3. 自定义唤醒词扩展支持：在 Web 控制台增加“自定义唤醒词拼音序列”配置项，支持动态切换类似“你好小木”、“灵方灵方”等叠词或四字声学状态机模板；
4. 约束：特征提取严禁在 `feedSamples()` 中调用 `malloc`，CPU 占用率控制在 3% 以内，确保与 60+ FPS ST7789 屏幕及 16kHz I2S 播放并行不卡顿。
### 方向 10：基于 Muse Charm 哲学的灵宠伴侣 (LingBuddy) 拟人化微表情、物理具身与 BLE 手机记忆同步

```markdown
【本次开发目标】：基于 Muse Charm 哲学的灵宠伴侣 (LingBuddy) 拟人化微表情、物理具身与 BLE 手机记忆同步
参考架构详案：`doc/27_基于MuseCharm哲学的M5StickS3灵宠伴侣软硬件架构与工程论证大案.md` 与调研报告 `doc/analysis/muse_charm_study_and_teardown.md`：
1. 矢量微表情引擎 (PAE)：
   - 在 ST7789 1.14" 屏幕实现 12 种程序化几何矢量表情（常态眨眼、聆听放大、思考转动、说话大笑、摇晃眩晕、平放打呼噜、摸摸头爱心等）；
   - 采用局部脏矩形 (Dirty Rectangle) 局部重绘机制，确保 60 FPS 丝滑动画，CPU 占用率控制在 5% 以内。
2. 实体点按即说 (Push-to-Talk) 与视听闭环：
   - 按下正面大按键 A (Btn A, G11) 触发毫秒级清脆水滴音，双眼瞬间高亮睁大，瞳孔随麦克风拾音 VU 能量实时弹性缩放；
   - 彻底解决嘈杂环境下的误识别、抢话与感知不确定性痛点。
3. 大模型情绪联动与音视同步：
   - 阿里云百炼 Prompt 注入灵宠性格与 `[E:emotion]` 首包标签协议，设备解析标签瞬间切换面部神态；
   - 提取下行流式 16kHz PCM 音频能量实时驱动嘴型开合。
4. BMI270 物理体感情感动力学：
   - 监测合加速度与冲击力，识别剧烈摇晃（眼冒金星晕眩）、轻拍抚摸（害羞微笑）、自由落体（惊叫大哭）、静置平放（进入打呼入睡模式）；
   - 维护亲密度 (Intimacy) 与能量值 (Energy) 的 Tamagotchi 成长机制。
5. BLE 手机端长程记忆同步与灵宠日记系统：
   - 启动专属 GATT 服务 `0xFFB0`，通过特征值 `0xFFB1` (Memory Stream) 向手机同步压缩的历史对话轮次；
   - 通过特征值 `0xFFB3` (Pet Diary) 向手机推送后台自动生成的“灵宠观察日记”；
   - 手机端承接无限容量的长期向量记忆图谱，彻底突破 ESP32 本地存储极限。
```

### 方向 11：LingBuddy 跨平台 Web Bluetooth 伴侣中枢与长程知识库沉淀

```markdown
【本次开发目标】：LingBuddy 跨平台 Web Bluetooth 伴侣中枢与长程知识库沉淀
基于已就绪的 Web Bluetooth 仪表盘 (`web/lingbuddy_companion.html`) 与 Python 伴侣中枢 (`scripts/lingbuddy_companion.py`)：
1. 移动端与 Web Bluetooth 离线同步适配：优化移动端 Chrome / Safari (WebBLE) 与微信环境连接握手，实现靠近 StickS3 自动静默配对；
2. 长期记忆向量化归档 (Local Vector DB)：在手机端或电脑端引入轻量向量数据库 (如 SQLite-vss 或 ChromaDB)，自动将 0xFFB1 下发的分块对话转为向量切片，形成个人生活知识库；
3. 双向日程与备忘注入：打通手机日历与待办事项，通过 0xFFB4 向设备下发定时提醒与日程卡片，设备在指定时间切换为 `MOOD_LISTEN` 并在屏幕弹出提醒和弦；
4. 拓麻歌子投喂与彩蛋交互：手机端增加“投喂数字小点心”、“洗澡梳毛”虚拟互动，直接向 0xFFB4 发送指令增加亲密度 XP 并解锁专属彩蛋表情。
```

---

## 三、 代码提交与交接执行准则 (Commit SOP for Agents)

所有后续 Agent 在完成任何阶段性功能开发并准备提交代码时，必须执行以下标准化闭环：

1. **双分支隔离研发准则**：
   - 稳定功能发布基线锁定在 `main`（打标 `v1.0.0-stable`，含 `dist/release_v1.0.0/` 独立免编译发布包）；
   - 灵宠伴侣与仿生微表情全部在 `feature/lingbuddy-companion` 分支进行研发，严禁未经全量测试将未经验证代码合并回 `main`。
2. **自动化校验先行**：
   - 运行灵宠表情与具身动力学测试：`pytest tests/test_avatar_and_empathy.py -v`（9 项全绿）。
   - 运行核心全套测试：`pytest tests/test_avatar_and_empathy.py tests/test_wakeword_engine.py tests/test_wifi_and_bailian_pipeline.py tests/test_audio_stream_pipeline.py tests/test_firmware_driver_suite.py tests/test_sticks3_three_schemes.py -v`（47 项全绿）。
   - 运行硬件在环与真机端到端验证：`python scripts/test_avatar_hardware.py` 与 `python scripts/lingbuddy_companion.py`。
3. **更新交接文档与续写提示词**：
   - 在对应模块的文档（如 `docs/HANDOVER_VOICE_DIALOGUE_AND_RESOURCE_MANAGEMENT.md` 与 `docs/27_基于MuseCharm哲学的M5StickS3灵宠伴侣软硬件架构与工程论证大案.md`）中记录最新演进、根因与方案。
   - 在本文件（`docs/AGENT_CONTINUATION_PROMPTS.md`）中登记新增功能方向的续写提示词。
4. **提交信息规范**：
   Commit Message 遵循 Conventional Commits 规范，必须附带说明核心交付物与交接指引。
5. **向用户输出交接描述**：
   在向用户的对话总结中，**必须明确附带下一步开发的继续开发提示词描述**，以便用户直接复制开启下一轮会话。
