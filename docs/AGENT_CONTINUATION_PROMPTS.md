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
1. 核心交接文档：`doc/26_StickS3物理伴侣与双模调测终端全链路开发总结与Agent工作交接文档.md`
2. 提示词标准库：`doc/AGENT_CONTINUATION_PROMPTS.md`
3. 固件核心源码：`firmware/m5sticks3_buddy/src/main.cpp` 与 `include/gbk_to_utf8.h`

【当前硬件与工程基线】：
- 硬件平台：M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)，已连接在本地串口 `COM3`。
- 底层已就绪：
  - M5PM1 电源门控（GPIO2 点亮 LCD 3.3V 供电，GPIO3 开启功放）已标定。
  - 按键引脚已修正为 G11 (Btn A) 与 G12 (Btn B)。
  - BMI270 姿态传感器、ES8311 音频和弦与麦克风 VU、ST7789v2 1.14" 屏幕均已点亮。
  - BLE Nordic UART (30字节广播合规包) 与 2.4GHz Wi-Fi (SoftAP/TCP/UDP/Web) 全互通。
  - 全集 23,940 条目 GBK-to-Unicode Flash 映射表已落地，手机端发送汉字已无方格子。
  - 双向音频：按键 A 触发 10 秒 16kHz WAV 录音 (PSRAM 缓冲 320KB)，网页端 (`http://192.168.4.1`) 原生拉取回放与下发播放，iOS Safari 语音备忘录/音频上传与 16kHz 和弦合成试听已全调通。
- 自动化流水线：编译与烧录自愈请统一使用 `python scripts/autonomous_bringup_agent.py`。
- 回归测试：真机测试使用 `python scripts/verify_audio_e2e_hardware.py` 与 `python scripts/test_ble_encoding.py`。

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
   - 页面 2：手机端/蓝牙聊天文本历史瀑布流（支持查看最近 5 条历史消息）；
   - 页面 3：周边 2.4GHz Wi-Fi AP 深度嗅探列表（展示热点名、信道与 RSSI 信号强弱条）；
   - 页面 4：硬件底层硬件健康度看板（电池电压、CPU温度、I2C总线状态、RAM剩余）。
2. 交互逻辑：长按正面按键 A（>800ms）轮询切页，短按侧键 B 在当前页面内翻页/确认；
3. 约束：所有汉字渲染必须经由 `sanitizeAndConvertToUtf8()` 自动归一化，严禁出现方格子乱码。
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

### 方向 5：智能语音问答与 Claude Desktop 语音大模型伴侣 (Voice AI Agent & Whisper/TTS)

```markdown
【本次开发目标】：智能语音问答与 Claude Desktop 语音大模型网关
我们希望将 StickS3 的双向音频流能力与大模型（如 Whisper ASR + Claude 3.7 / GPT-4o + Edge TTS）打通。
1. 上位机桥接服务：编写 Python 网关脚本（如 `scripts/voice_ai_gateway.py`），监听 SoftAP 或局域网中的 StickS3 音频事件；
2. ASR 语音转文字：当 StickS3 录音完成后，网关自动获取 `/audio/device_record.wav` 并送入 Whisper 进行中文语音识别；
3. 大模型交互与 TTS 回传：将识别结果输入 Claude Desktop / API，生成的回复文本通过 Edge TTS 合成为 16kHz WAV 流，自动 POST 到 `/audio/upload`，由 StickS3 喇叭即时回放；
4. 屏幕联动：在 ST7789 屏幕上使用 `drawChineseText()` 同步流式渲染 ASR 识别出的用户问话与 AI 回复摘要。
```

---

## 三、 代码提交与交接执行准则 (Commit SOP for Agents)

所有后续 Agent 在完成任何阶段性功能开发并准备提交代码时，必须执行以下标准化闭环：

1. **自动化校验先行**：
   - 运行 `pytest tests/test_sticks3_three_schemes.py tests/test_firmware_driver_suite.py tests/test_audio_stream_pipeline.py` 确保全套 19 项单元测试通过。
   - 运行真机回归脚本 `python scripts/test_ble_encoding.py` 验证实际硬件功能。
2. **更新交接文档**：
   - 在对应模块的文档（如 `doc/26_...md`）中记录最新修复的根因与方案。
   - 在本文件（`doc/AGENT_CONTINUATION_PROMPTS.md`）中登记新增功能方向的续写提示词。
3. **提交信息规范**：
   Commit Message 遵循 Conventional Commits 规范，必须附带说明核心交付物与交接指引。
4. **向用户输出交接描述**：
   在向用户的对话总结中，**必须明确附带下一步开发的继续开发提示词描述**，以便用户直接复制开启下一轮会话。
