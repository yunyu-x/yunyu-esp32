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
1. 项目最高公理与全栈交接：`docs/30_PROJECT_AXIOMS_AND_HANDOVER.md` (必读！严格遵守六大不可违背公理)
2. 移动端与小程序交接：`docs/29_微信小程序与移动端研发交接指南_HANDOVER_MOBILE.md`
3. 提示词标准库：`docs/AGENT_CONTINUATION_PROMPTS.md`
4. 固件核心源码：`firmware/m5sticks3_buddy/src/main.cpp` 与 `include/sticks3_ble_sync.h`

【本项目六大不可违背公理 (Project Constitutional Axioms)】：
- 公理一【真实硬件烧录验证】：固件改动必须烧录真实硬件 (COM3) 并 RTS/DTR 硬重启，串口实测 10~15 秒验证通过，拒绝空谈。
- 公理二【中断通讯异步解耦】：严禁在底层任务 (如 BTC_TASK) 中执行 Flash 读写或 WiFi 重连，必须经队列解耦至 loopTask。
- 公理三【显存零撕裂双缓冲】：物理屏严禁直接擦写，必须经 PSRAM LGFX_Sprite (135x240) 离线合成后 DMA 原子推送，消灭频闪。
- 公理四【网络显式区分一致】：手机热点 (橙色 HOT / 流量熔断) 与宽带 WiFi (绿色 WiFi) 强区分，小程序主页与设置页数据 100% 一致。
- 公理五【零功能回退渐进加固】：离线唤醒词「悄悄」、阿里百炼流式语音、12种微表情、记忆存储与物理打断绝对不容劣化。
- 公理六【自适应协议与防截断】：跨端分包重组，中文截断必须使用 safeTruncateUtf8 字符级保护器，杜绝非法字节崩溃。

【当前硬件与工程基线】：
- 硬件平台：M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)，已连接在本地串口 `COM3`，局域网 IP `192.168.110.67`。
- 固件状态：Anti-Flicker Double-Buffer Canvas (135x240 in PSRAM) 稳定运行，主循环 FPS: 96.8 ~ 98.0，SRAM: 64KB free，PSRAM: 7.22MB free，I2C 零失败，长程运行零重启。
- 自动化流水线：
  - 编译固件：`python -m platformio run -e m5sticks3_buddy`
  - 烧录固件：`python -m platformio run -e m5sticks3_buddy -t upload`
  - 验证运行：`python -c "import serial, time; ser = serial.Serial('COM3', 115200, timeout=1); ser.setDTR(False); ser.setRTS(True); time.sleep(0.1); ser.setRTS(False); time.sleep(0.2); start = time.time(); [print(ser.readline().decode('utf-8', errors='replace').strip()) for _ in iter(lambda: ser.readline() if time.time()-start < 10 else None, None)]; ser.close()"`

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
3. 自定义唤醒词扩展支持：在 Web 控制台增加“自定义唤醒词拼音序列”配置项，支持动态切换类似“你好悄悄”、“灵方灵方”等叠词或四字声学状态机模板；
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

### 方向 11：LingBuddy 跨平台 Web Bluetooth 伴侣中枢与长程知识库沉淀 (已落地就绪 Baseline)

```markdown
【已就绪伴侣中枢与知识库能力】：
- 移动端响应式布局与 Web Bluetooth 自动重连：
  - `web/lingbuddy_companion.html` 全面适配 iOS/Android 刘海屏、折叠屏与 Safe Area (`viewport-fit=cover`)，双栏自适应网格。
  - 实现基于指数退避 (1s~16s) 的断线自动监听与静默重连机制，重连后自动恢复 GATT 通知与状态快照。
  - 内置 Web Audio API 拟真 8-Bit/FM 和弦合成器，本地仿真与蓝牙联调均可享受清脆水滴音、咀嚼音与击掌音效。
- 双轨长程对话向量知识库沉淀：
  - 前端基于 IndexedDB 实现轻量语义向量化与余弦相似度 Top-K 检索 (`BrowserVectorKnowledgeBase`)，支持一键备份导出；
  - Python 端落地产能级 SQLite 持久化向量知识库 (`scripts/lingbuddy_vector_store.py`)，支持 N-gram TF-IDF 嵌入与 RAG 上下文拼装。
- 拓麻歌子具身互动与彩蛋全链路闭环：
  - 设备固件新增投喂小点心 (`feed` -> `MOOD_EAT`)、梳理毛发 (`groom` -> `MOOD_GROOM`) 与默契击掌 (`play` -> `MOOD_WINK`)；
  - 屏幕动态呈现节奏咀嚼开合、周身星芒浮动与眨眼放电虎牙笑，第一人称日记自动生成并推流至手机。
```

---

### 方向 12：灵宠主动搭话、端侧轻量意图路由与 PWA 桌面小组件 (Proactive Embodiment & Offline Intelligence)

```markdown
【本次开发目标】：灵宠主动搭话、端侧轻量意图路由与 PWA 桌面小组件
基于已就绪的 12 种程序化微表情、全双工百炼语音交互、长程向量知识库与拓麻歌子互动体系：
1. 晨起唤醒与主动搭话 (Proactive Wake & Greeting)：
   - 利用 RTC 时钟与 BMI270 拿起事件，在早晨 7:00~9:00 第一次被主人拿起时，悄悄主动打哈欠 (`MOOD_SLEEP` -> `MOOD_LISTEN`) 并播放清晨问候和弦：“早安主人！今天也要元气满满哦！”；
2. 离线意图离散匹配与本地生活管家：
   - 在未联网或离线状态下，利用轻量级状态机匹配常用指令（如“倒计时 5 分钟”、“当前电量”、“现在几点”），无需连接百炼大模型即可离线应答与震动/和弦提醒；
3. Web 伴侣 PWA 离线化与桌面安装：
   - 为 `web/lingbuddy_companion.html` 添加 `manifest.json` 与 Service Worker 离线缓存，支持在 iOS Safari（添加到主屏幕）与 Android Chrome 上以全屏原生 App 形式运行；
4. Grove 接口外设多模态扩展 (可选)：
   - 通过 Grove (G1/G2) 接口接入 Unit-Cam 或 PIR 人体红外传感器，实现悄悄在感知到有人走近时好奇探头打量 (`MOOD_CURIOUS`)。
```

---

### 方向 13：微信小程序与移动端灵宠伴侣产品化演进 (已落地就绪 Baseline)

```markdown
【已就绪微信小程序移动端产品化能力】：
- 全套 4-Tab 移动端原生交互架构：
  - 伴侣主页 (`pages/index/`)：自适应 `<avatar-canvas>` 迪士尼灵动微表情、即时亲密/活力 HUD、手势解算、快捷互动网格与热点熔断脉冲告警；
  - 隔空投喂屋 (`pages/feed/`)：精致甜点道具图鉴（草莓大福、舒芙蕾、比利时曲奇、熔岩甜甜圈、爆米花、抹茶冰淇淋），伴随微表情大口咀嚼与飞跃金屑；
  - 心声日记本 (`pages/diary/`)：瀑布流心声日记卡片、8 种情绪分类标签筛选（全部/收藏/美食/抚摸/梳毛/击掌/调皮/晚安）、本地收藏与日记卡片朋友圈分享；
  - 设备设置/BLE配网 (`pages/settings/`)：BLE 扫描连接、常规 Wi-Fi 与手机共享移动热点双模式配置、50MB/100MB/200MB/500MB/自定义多档配额设定、超额自动熔断保护开关、实时流量进度条看板、追加 50MB 与重置清零。
- 触觉与视觉高保真联觉：
  - `<avatar-canvas>` 自定义组件完美自适应各类 iPhone / Android 屏幕像素比 (DPR)，避免视网膜屏模糊；
  - 轻触抚摸 (light)、隔空投喂 (medium)、默契击掌 (heavy) 具身触觉微震动反馈 (`utils/haptics.js`)；
  - 离线持久化沉淀管理器 (`utils/storage_manager.js`) 与跨页面统一状态服务 (`utils/buddy_service.js`)。
- 固件级流量保护与大模型熔断：
  - 硬件级双向流量计量与 256KB 批量写盘防 Flash 磨损机制；
  - 80% 临界预警（心声日记播报）与 100% 自动熔断保护（切断百炼 16kHz PCM 音频推流，保持 BLE 畅通）。
```

---

### 方向 14：微信运动步数联动、朋友圈回忆海报合成与云开发长程记忆同步 (WeRun & Cloud Moments)

```markdown
【本次开发目标】：微信运动步数联动、朋友圈回忆海报合成与云开发长程记忆同步
基于已就绪的 4-Tab 小程序产品化架构与 20 字节安全 BLE 驱动：
1. 微信运动步数兑换 (WeRun Steps Integration)：
   - 接入微信运动开放接口，每日走满 6000 步自动解锁灵宠专属“限定甜点盲盒”；
2. 朋友圈回忆海报 Canvas 合成与导出：
   - 离线利用 Canvas 2D 动态生成 9:16 唯美《灵宠陪伴周报》，一键保存至手机系统相册或分享朋友圈；
3. 微信云开发 (CloudBase) 或 SQLite 端云多端同步：
   - 历史心声日记与重要记忆切片安全上传云端，支持多手机/多终端登录查看灵宠同一成长历程。
```

---

### 方向 15：结合离线声学唤醒词「悄悄」的低功耗待机与全双工打断能效比优化 (Low-Power Standby & High-Efficiency Barge-In)

```markdown
【本次开发目标】：结合离线声学唤醒词「悄悄」的低功耗待机与全双工打断能效比优化
在小熊 5 级 RPG 成长技能树与生物力学校同身法动力学 (FPS 88+、双段屈伸、组合技) 已全面就绪的基础上：
1. 离线待机动态降频与轻度睡眠 (DFS & Light Sleep)：
   - 当百炼会话处于空闲待命且开启唤醒词引擎时，动态将 ESP32-S3 主频由 240MHz 降频至 80MHz 或使能自动轻度睡眠 (Automatic Light Sleep)，整机待机功耗降低 60%+；
2. 麦克风流式 VAD 占空比动态调度 (Adaptive Duty-Cycled VAD)：
   - 在宁静环境下，降低环境底噪采样轮询开销；当拾取到微弱人声起始特征时，瞬时恢复 240MHz 全速时钟推流；
3. 声学全双工打断能效模型 (Barge-In Energy Optimization)：
   - 优化 ES8311 喇叭回声自适应消除与硬件 DSP 运算链路，减少双核频繁上下文切换与总线负载；
4. 约束：
   - 严禁影响「悄悄」离线唤醒的毫秒级触发召回率，自全双工打断恢复倾听时间严格维持在 120ms 以内，遵守六大工程公理。
```

---

### 方向 16：迪士尼 17 套影院级动作、全套阅兵与微信小程序全方位导播演进 (Cinematic Poses & Mini-Program Director)

```markdown
【本次开发目标】：迪士尼 17 套影院级动作、全套阅兵与微信小程序全方位导播演进
在 JollyBot 元气小熊 17 套迪士尼影院级姿态、1800 秒真机/小程序双重连续压测全绿通过的基础上：
1. 动作姿态与音频音效深度绑定：
   - 为 17 套动作（挥手、作揖、弹跳、功夫、太极、升龙霸天等）匹配专属 I2S WAV 萌趣音效与音频共振粒子；
2. 微信小程序 3D 骨骼逆运动学 (IK) 可视化拖拽：
   - 在小程序首页 3D 控制舱中引入 Three.js / WebGL 交互骨骼，支持手指拖拽小熊手脚直接反解关节角并实时同步至 StickS3 真机；
3. 多设备编队舞步音乐节拍同步：
   - 结合 LingCube 微型自重构机器人与多个 StickS3，通过 BLE 广播时钟同频跳起华尔兹编队舞步；
4. 约束：
   - 必须严格遵守显存零撕裂双缓冲公理与真机烧录验证公理，维持 85+ FPS 高速刷新与零内存泄漏。
```

---

### 方向 17：精致动漫原型服饰挂件与高保真动态光影定制 (Exquisite Costumes & Dynamic Cel-Shading)

```markdown
【本次开发目标】：精致动漫原型服饰挂件与高保真动态光影定制
在 JollyBot 融合《疯狂动物城》探险战术马甲与《功夫熊猫》武僧双弧编织护腕/护踝（85+ FPS 零撕裂稳定运行）的基础上：
1. 探险巡警多套动态可换服饰系统 (Dynamic Costume Switcher)：
   - 支持通过小程序与百炼自然语言下发服饰换装（如：[COSTUME:police_vest] 经典战术马甲、[COSTUME:kungfu_robe] 东方云纹道袍、[COSTUME:cyber_armor] 赛博高光合金机甲）；
2. 动态光照投影与边缘逆光着色器 (Dynamic Cel-Shading & Rim-Light Shifter)：
   - 根据 BMI270 重力与当前偏航角度动态计算光源矢量，实时将边缘金光高光 (`ANIME_COL_RIMLIGHT`) 与接触阴影平滑移动；
3. 四肢布料微物理飘带解算 (Ribbon & Tassel Micro-Physics)：
   - 为功夫腰封和马甲领口增加两根具备重力与角加速度阻尼的飘逸流苏，伴随招式挥舞产生二次跟随动作；
4. 约束：
   - 必须严格遵守六大不可违背工程公理，PSRAM 135x240 双缓冲原子推送，严禁产生内存泄漏与掉帧。
```

---

## 三、 代码提交与交接执行准则 (Commit SOP for Agents)

所有后续 Agent 在完成任何阶段性功能开发并准备提交代码时，必须执行以下标准化闭环：

1. **双分支隔离研发准则**：
   - 稳定功能发布基线锁定在 `main`（打标 `v1.0.0-stable`，含 `dist/release_v1.0.0/` 独立免编译发布包）；
   - 灵宠伴侣与仿生微表情全部在 `feature/lingbuddy-companion` 分支进行研发，严禁未经全量测试将未经验证代码合并回 `main`。
2. **自动化校验先行**：
   - 运行灵宠表情、具身动力学与向量知识库测试：`pytest tests/test_avatar_and_empathy.py tests/test_vector_knowledge_base.py -v`（13 项全绿）。
   - 运行核心全套回归测试：`pytest tests/test_avatar_and_empathy.py tests/test_vector_knowledge_base.py tests/test_wakeword_engine.py tests/test_wifi_and_bailian_pipeline.py tests/test_audio_stream_pipeline.py tests/test_firmware_driver_suite.py tests/test_sticks3_three_schemes.py -v`（51 项全绿）。
   - 运行硬件在环与真机端到端验证：`python scripts/lingbuddy_companion.py` 与 PlatformIO 固件编译 (`python -m platformio run -d firmware/m5sticks3_buddy`)。
3. **更新交接文档与续写提示词**：
   - 在对应模块的文档（如 `docs/HANDOVER_VOICE_DIALOGUE_AND_RESOURCE_MANAGEMENT.md` 与 `docs/27_基于MuseCharm哲学的M5StickS3灵宠伴侣软硬件架构与工程论证大案.md`）中记录最新演进、根因与方案。
   - 在本文件（`docs/AGENT_CONTINUATION_PROMPTS.md`）中登记新增功能方向的续写提示词。
4. **提交信息规范**：
   Commit Message 遵循 Conventional Commits 规范，必须附带说明核心交付物与交接指引。
5. **向用户输出交接描述**：
   在向用户的对话总结中，**必须明确附带下一步开发的继续开发提示词描述**，以便用户直接复制开启下一轮会话。
