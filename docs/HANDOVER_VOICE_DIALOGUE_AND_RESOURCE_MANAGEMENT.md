# M5StickS3 全双工大模型语音问答、长程记忆压缩与硬件资源看门狗交接文档
# (StickS3 Realtime LLM Voice Companion & Memory Compaction Handover Document)

> **发布版本**：v1.2.0-realtime  
> **更新时间**：2026-09-27  
> **适用硬件**：M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)  
> **物理串口**：`COM3` (默认波特率 115200 / 极速烧录 1500000)  
> **局域网默认 IP**：`192.168.110.67` (STA 模式) / `192.168.4.1` (SoftAP 模式 `StickS3-Buddy`)  

---

## 1. 工程背景与交付概览 (Executive Summary)

本项目实现了基于 **M5Stack StickS3** 掌上微型终端的**全双工大模型流式语音伴侣系统**。系统通过 Wi-Fi 直连阿里云百炼 DashScope Realtime 官方 WebSocket (WSS) 协议，打通 16kHz PCM 全双工音频采集与流式播音、打断唤醒、两级长期多轮记忆压缩与全维度硬件性能看门狗监控。

本交接文档旨在为后续接手开发的所有 AI Agents 与人类工程师提供 100% 透明、0 试错成本的完整交接依据。

---

## 2. 硬件资源分配与 GPIO 物理映射表 (Hardware Spec & Pinout)

| 外设模块 | 核心芯片 / 器件 | 接口类型 / GPIO | 说明与关键配置 |
| :--- | :--- | :--- | :--- |
| **主控芯片** | ESP32-S3-PICO-1 | 240MHz 双核 Xtensa | 8MB Octal SPI Flash, 8MB PSRAM (QIO) |
| **电源与门控** | M5PM1 PMIC | I2C (SDA=G13, SCL=G15) | GPIO2 门控屏幕背光+3.3V；GPIO3 门控功放 5V 升压 |
| **彩色屏幕** | ST7789v2 1.14" 135x240 | SPI (MOSI=G5, CLK=G6, CS=G7, DC=G4, RST=-1) | 支持 GBK/UTF-8 双字体引擎，60+ FPS |
| **音频编解码** | Everest ES8311 Codec | I2C (SDA=G13, SCL=G15) + I2S (MCLK=G9, BCLK=G8, WS=G10, DIN=G14, DOUT=G16) | 16kHz 16-bit Mono，支持全双工麦克风采集与 DAC 播放 |
| **音频功放** | AW8737 (Awinic) | 模拟音频驱动 + PMIC GPIO3 供电 | 独立扬声器驱动，具备毫秒级硬件静音与抗破音算法 |
| **板载硅麦** | MEMS PDM/I2S 硅麦 | ES8311 ADC 模拟前端 | 采样率 16000Hz，支持硬件增益调节与底噪自适应门限 |
| **姿态传感器** | Bosch BMI270 6-Axis IMU | I2C (SDA=G13, SCL=G15, ADDR=0x68) | 支持 Roll/Pitch 姿态角解算与自由落体/碰撞检测 |
| **实体按键** | Btn A (正面) & Btn B (侧面) | GPIO11 (Btn A), GPIO12 (Btn B) | 内部上拉输入；A 键主打断/问答，B 键切换 5V 升压/Wi-Fi 扫描 |

---

## 3. 核心根因定位与攻坚记录 (Resolved Critical Bugs)

在系统联调与连续压力测试中，排查并彻底攻克了以下关键缺陷：

### 3.1 UTF-8 变长字节截断撕裂 (RFC 6455 Code 1007 协议违规)
* **故障现象**：设备在前 1~2 轮语音对话正常，当多轮历史累积到第 3 轮之后，下发对话突然失去响应，WebSocket 频繁报错重连。
* **深层根因**：
  在 `buildMemoryContextPrompt()` 拼接提示词及 `compressMemory()` 生成摘要时，使用了简单的字节切片 `String::substring(0, 32)`。中文字符在 UTF-8 编码下占 3 个字节（$32 \pmod 3 = 2$），强行字节切片直接在中文字符的第 2 字节切断，导致发送的 JSON 文本帧包含非法 UTF-8 序列。阿里云 DashScope Realtime 服务端依据 RFC 6455 规范静默关闭连接（Close Code 1007）。重连后再次读取损坏的记忆，造成**无限重连死循环**。
* **架构解法**：
  在 [`sticks3_memory_store.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/sticks3_memory_store.h) 中实现了遵循 Unicode 规范的 `safeTruncateUtf8(const String& input, size_t max_bytes)`，解析变长字节序列头（1/2/3/4 字节），严格在整字边界裁切并添加 `...`，彻底杜绝非法 UTF-8 报文。

### 3.2 播放生命周期状态机不同步 (Playback Lifecycle Desync)
* **故障现象**：音频播放完成后，屏幕或状态机偶尔卡在“正在回复中”或“思考推理中”，后续对麦讲话无反应。
* **深层根因**：
  服务端下发 `session.updated` 事件时，原逻辑无条件将状态强行置为 `BL_STATE_LISTENING`，绕过了 FreeRTOS 音频任务的自然排空与 `finishStreamPlayback()` 方法，导致 `_is_streaming_llm == true` 标志残留，麦克风 ADC 模式未能切换回来。
* **架构解法**：
  在 `update()` 主轮询中引入双重终态检测：当 `audio.isPlaying() && audio.getStreamBufferAvailable() == 0` 时，可靠触发 `finishStreamPlayback()`；在 `session.updated` 中若音频仍在播放则维持 `BL_STATE_SPEAKING`，由音频流自然结束驱动平滑切回。

### 3.3 无活跃上下文时误发 `response.cancel`
* **故障现象**：发送文本或新一轮提问时，服务端报 `Conversation has none active response` 并取消了新发起的 `response.create`。
* **深层根因**：
  `sendTextMessage` 与按键触发打断时，未判断当前服务端是否真正处于输出阶段，直接向 WSS 灌注 `response.cancel` 报文。
* **架构解法**：
  增加 `_server_response_active` 状态守卫，仅在服务端生成流活跃期允许向网络发送取消帧。

### 3.4 腔体结构自激与回声打断误触发
* **故障现象**：设备播放大音量古诗（如《长歌行》）时，刚读出第一句就瞬间自我打断并卡住。
* **深层根因**：
  StickS3 喇叭与 MEMS 硅麦同处于 1cm 极小腔体内，喇叭发声的结构共振回传硅麦，导致本地 RMS 计算达到 35%~50%，触发了本地能量打断。
* **架构解法**：
  在播放期间将本地打断门限由 18% 动态提升至 35%，并加入 300ms 播放启动声学屏蔽窗口（Acoustic Blanking Window），彻底隔离自激。

### 3.5 I2C 跨核心并发争抢与硬件锁死
* **故障现象**：长程多轮对话时，ESP32 偶尔直接死锁，串口停止输出。
* **深层根因**：
  Core 1 的主线程 `loopTask`（读取 BMI270 姿态与 M5PM1 电池）与 Core 0 的后台 `websocket_task`（异步调用 ES8311 Codec 静音与音量调节）无保护并发操作 `Wire1`，致使底层 I2C 硬件中断挂起。
* **架构解法**：
  引入全局互斥锁 `g_i2c_mutex` (`sticks3_i2c_mutex.h`) 与 RAII 守卫 `I2CLockGuard(50)`，所有总线事务均受互斥保护，实测 15,000+ 次事务 **0 失败**。

---

## 4. 两级长程记忆压缩与 PSRAM 零碎片架构 (Memory Compaction Architecture)

为了保证长期对话（数十乃至上百轮）下硬件永不耗尽内存、不产生堆内存碎片，系统设计了双级记忆管理：

```
                    ┌──────────────────────────────────────────────┐
                    │            用户多轮流式语音问答交互            │
                    └──────────────────────┬───────────────────────┘
                                           │
                        新轮次写入 (turn_count 增加)
                                           ▼
             ┌───────────────────────────────────────────────────────────┐
             │         一级：PSRAM 长期记忆工作区 (MAX_RAM_TURNS = 8)      │
             │   - 平铺静态数组: DialogueTurn _turns[8]                    │
             │   - 零 Internal SRAM 堆内存分配 (Zero Fragment Hazard)       │
             │   - 占用 PSRAM 内存: 3.4 KB (极低开销)                       │
             └─────────────────────────────┬─────────────────────────────┘
                                           │
                         超过 8 轮 (触发自动压缩算法)
                                           ▼
             ┌───────────────────────────────────────────────────────────┐
             │         自动滑动窗口提炼压缩 (safeTruncateUtf8 保护)          │
             │   - 将 Turn 0 与 Turn 1 提炼合并为:                        │
             │     "[前期摘要] 曾讨论: <安全截断前文> -> <安全截断回答>"      │
             │   - 保持有效历史轮数恒定 <= 8 轮                             │
             └─────────────────────────────┬─────────────────────────────┘
                                           │
                                  持久化沉降 (断电保护)
                                           ▼
             ┌───────────────────────────────────────────────────────────┐
             │         二级：Flash NVS 核心断电记忆区 (MAX_NVS_TURNS = 5)  │
             │   - 仅持久化关键的 5 轮核心记忆 (降低 Flash 磨损)             │
             │   - 开机秒级自愈加载                                        │
             └───────────────────────────────────────────────────────────┘
```

### 关键数据结构与方法：
- **`DialogueTurn`**：平铺结构体，内含 `turn_id`, `timestamp`, `time_str[16]`, `user_text[128]`, `ai_text[256]`, `voice[16]`, `duration_ms`；
- **`safeTruncateUtf8`**：严格按 Unicode 完整字符边界截断，杜绝乱码；
- **`buildMemoryContextPrompt`**：自动组装结构化记忆提示词注入大模型 `instructions`。

---

## 5. 本地离线语音唤醒词「悄悄」(Offline Wake Word Engine & Barge-In Synergy)

为了彻底降低待机功耗、杜绝无意义的网络流量与云端 Token 消耗，系统集成了专为 ESP32-S3 定制的**超轻量级本地离线语音唤醒词「悄悄」(qiāo qiāo) 声学引擎** (`sticks3_wakeword.h`)：

```
           麦克风 16kHz PCM (20ms / 320 采样点)
                         │
                         ▼
        ┌───────────────────────────────────┐
        │  时频多子带特征提取 (extractFrameFeatures)
        │  - RMS 能量 (0~32767)
        │  - 过零率 ZCR (0~160)
        │  - 3-Band 能量: Low/Mid/High 
        │  - 高低频比 (hl_ratio = e_high / e_low)
        └─────────────────┬─────────────────┘
                          │
                          ▼
        ┌───────────────────────────────────┐
        │   五阶段叠词声学状态机 (processFeatureFrame)
        │   [IDLE] 待命
        │     │  清塞擦 [q] (高 ZCR > 48, hl_ratio > 0.85)
        │     ▼
        │   [Q1]  (持续 40~140ms)
        │     │  共振双元音 [iao] (低 ZCR < 42, 能量激增)
        │     ▼
        │   [IAO1] (持续 60~320ms)
        │     │  能量回落 / 静音间隙 (跌破 45% 或进入背景)
        │     ▼
        │   [GAP] (持续 20~240ms, 支持连读直转 Q2)
        │     │  清塞擦 [q] (再次出现高频与高 ZCR)
        │     ▼
        │   [Q2]  (持续 40~140ms)
        │     │  共振双元音 [iao] (低 ZCR, 谐波起振)
        │     ▼
        │   [IAO2] (持续 80~320ms)
        │     │  综合对称度评估 (evaluateConfidence >= 门限)
        │     ▼
        │   [TRIGGERED] 触发唤醒回调并在 20ms 后重置
        └───────────────────────────────────┘
```

### 5.1 核心声学特性与设计亮点
1. **零动态堆分配 (Zero Heap Overhead)**：全部特征环形历史与 FIFO 缓冲区直接常驻 PSRAM/静态内存，`feedSamples()` 每帧处理耗时 $< 0.4\text{ms}$，单核 CPU 占用率 $< 2.5\%$。
2. **双音节对称度打分模型 (Syllable Symmetry Scoring)**：
   - 时域持续时间对称性：$S_{\text{dur}} = 35 \times \min(T_1, T_2) / \max(T_1, T_2)$；
   - 能量均衡度：$S_{\text{eng}} = 25 \times \min(E_1, E_2) / \max(E_1, E_2)$；
   - 状态完整性奖励：$S_{\text{fsm}} = 40$；
   - 综合置信度得分 $Conf = S_{\text{dur}} + S_{\text{eng}} + S_{\text{fsm}}$ (0~100%)。
3. **灵敏度门限自适应动态缩放**：
   - 灵敏度范围 10%~100%（默认 75%），触发要求置信度公式：$Conf_{\text{req}} = \max(45.0, 85.0 - 0.35 \times \text{Sensitivity})$。
4. **全双工流式状态机联动**：
   - **待命节流**：未被唤醒时不向阿里云百炼 WSS 上行推流，大幅节省网络与 Token 成本；
   - **即时响应**：检测到唤醒词后立即触发提示和弦音（E5-G#5-B5-E6 四和弦），拉起 8~10 秒流式问答窗口（发音期间自动动态延期）；
   - **Barge-In 联动**：AI 正在流式播音发声时，用户呼叫「悄悄」同样能可靠触发物理打断并转入新一轮聆听。

---

## 6. 关键 REST API 接口契约 (HTTP Endpoints)

设备连接 Wi-Fi 后，在局域网内提供以下 REST API（可直接由 Python、上位机或 Web 浏览器调用）：

| 端点 (Endpoint) | 方法 | 请求参数 | 响应样例与说明 |
| :--- | :--- | :--- | :--- |
| **`/bailian/status`** | GET | 无 | 获取百炼大模型连接状态、当前问答文本、打断统计、记忆轮数等。<br>`{"state_code":3,"state_name":"正在聆听...","user_query":"...","ai_reply":"...","memory_turns":8}` |
| **`/bailian/send_text`** | POST | `text=<utf8_string>` | 向百炼直接注入用户文本并触发语音推理与流式播音。 |
| **`/bailian/interrupt`** | POST | 无 | 立即硬件级打断当前播音，下发 `response.cancel`。 |
| **`/wakeword/status`** | GET | 无 | 获取离线唤醒词状态、灵敏度、开窗倒计时与触发统计。<br>`{"enabled":true,"word":"悄悄","sensitivity":75,"window_open":true,"window_remaining_ms":5400,"total_wakes":3}` |
| **`/wakeword/config`** | POST | `enabled=1&sensitivity=80&timeout=10` | 动态调整唤醒词使能、灵敏度 (10~100) 与超时时间 (3~30s)，持久化至 NVS。 |
| **`/wakeword/trigger`** | POST | `confidence=98.5` | 手动/软件仿真触发唤醒词事件，拉起问答窗口并播放提示音。 |
| **`/memory/list`** | GET | 无 | 查询当前 PSRAM 中存储的所有历史轮次与摘要记录。<br>`{"total":8,"next_id":10,"turns":[{"id":9,"user":"...","ai":"..."}]}` |
| **`/memory/clear`** | POST | 无 | 清空 PSRAM 与 Flash NVS 中的所有历史记忆。 |
| **`/system/metrics`** | GET | 无 | 实时获取 FPS、SRAM 可用及最大连续块、PSRAM 可用、I2C 事务统计。 |
| **`/wifi/status`** | GET | 无 | 获取 Wi-Fi 连接状态、IP 地址、网关与信号强度。 |
| **`/bailian/config`** | POST | `key`, `model`, `voice` | 动态热更新百炼 API Key、模型与音色配置。 |

---

## 7. 自动化验证脚本与测试矩阵 (Verification Tooling)

| 脚本路径 | 说明 | 执行命令 |
| :--- | :--- | :--- |
| `tests/` | 46 项全功能单元测试（声学唤醒词引擎、WSS 协议、UTF-8 安全、PCM 转码、状态机） | `pytest tests/ -v` |
| `tests/test_wakeword_engine.py` | 离线唤醒词「悄悄」仿真合成检测、抗负样本、灵敏度缩放与固件源码契约测试 | `pytest tests/test_wakeword_engine.py -v` |
| `scripts/test_voice_dialogue_and_memory_compression.py` | 实机 9 轮端到端全双工对话与长程记忆压缩自动化压测 | `python scripts/test_voice_dialogue_and_memory_compression.py` |
| `scripts/monitor_and_stress_continuous_dialogue.py` | 系统硬件资源看板（FPS, SRAM max_block, PSRAM, I2C 冲突）长程监控 | `python scripts/monitor_and_stress_continuous_dialogue.py` |
| `scripts/test_audio_sample_rate_playback.py` | 16kHz I2S 硬件采样率与 7 种音色全集对比验证 | `python scripts/test_audio_sample_rate_playback.py` |
| `scripts/autonomous_bringup_agent.py` | 全自动固件编译、1.5MBaud 极速上传与硬件复位监控流水线 | `python scripts/autonomous_bringup_agent.py` |

---

## 8. 下一位 Agent 接手操作指南 (Onboarding for Next Agent)

若您是接手本工程的后续 Agent，请遵循以下标准流程开展工作：

### 8.1 快速健康检查指令
```powershell
# 1. 验证单元测试通过性 (当前基线: 46 passed in ~1.6s)
pytest tests/ -v

# 2. 检查固件源码编译 (确保 RAM < 25%, Flash < 75%)
python -m platformio run -d firmware/m5sticks3_buddy

# 3. 局域网端点快速探针 (设备已在局域网 192.168.110.67)
python -c "import urllib.request, json; print(json.loads(urllib.request.urlopen('http://192.168.110.67/wakeword/status', timeout=3).read().decode('utf-8')))"
```

### 7.2 研发红线与工程约束 (Engineering Invariants)
1. **禁止在 Internal SRAM 上为对话轮次动态分配堆内存**：任何新的历史记录或文本缓冲必须分配在 PSRAM 中，确保 `sram_max_block >= 50KB`。
2. **所有 I2C 硬件操作必须使用 `I2CLockGuard`**：严禁绕过互斥锁直接操作 `Wire1`。
3. **文本截断必须使用 `safeTruncateUtf8`**：严禁直接调用 `String::substring()` 截断包含中文字符的文本。
4. **保持 AP+STA 双模共存**：配网与正常工作必须同时支持 `192.168.4.1` (SoftAP) 与局域网 STA IP。
