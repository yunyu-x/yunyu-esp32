# M5Stack StickS3 Voice Buddy OS v1.0.0-stable 官方发布说明书 (Release Notes)

> **发布版本 (Release Version)**: `v1.0.0-stable`  
> **发布日期 (Release Date)**: 2026-09-27  
> **目标硬件平台 (Target Hardware)**: M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)  
> **代码仓库分支**: `main` @ Tag `v1.0.0-stable`  
> **发布包位置**: `dist/release_v1.0.0/`

---

## 1. 版本概述 (Overview)

`v1.0.0-stable` 是 **M5Stack StickS3 Voice Buddy** 首个经严苛物理在环验证与全量单元测试覆盖的**官方稳定基线版本 (Production-Ready Release)**。
本版本专注于构建坚如磐石的**全双工低时延云端大模型流式语音交互、端侧超轻量离线唤醒词声学引擎、毫秒级物理/声学打断机制与全生命周期资源自愈系统**。

---

## 2. 核心功能与技术规格 (Feature Highlights)

### 2.1 阿里云百炼 (DashScope) 全双工流式问答
* **通信协议**: 原生 WebSocket Secure (WSS) 直连 `dashscope.aliyuncs.com` 全双工通道；
* **音频流水线**: 16kHz 16-bit 单声道 PCM 流式全双工推拉，ES8311 I2S DMA 硬件双通道；
* **低等待焦虑**: 配合屏幕汉字即时渲染与和弦提示音，网络往返延迟控制在 350ms 以内。

### 2.2 本地离线语音唤醒词「悄悄」(qiāo qiāo)
* **声学特征处理**: 20ms 帧步长，时频 3 子带滤波（Low: 150-900Hz, Mid: 900-2800Hz, High: >2800Hz）、过零率 (ZCR) 与高低频比 ($hl\_ratio$) 提取；
* **五阶段叠词状态机**: 追踪识别清塞擦音 [q] $\to$ [iao] $\to$ [GAP] $\to$ [q] $\to$ [iao]，并进行时域持续时间与能量对称性综合评分；
* **资源开销**: 单核 CPU 占用率 $< 2.5\%$，环形特征缓冲区常驻 PSRAM，帧循环内 **0 堆碎片 (Zero Heap Fragmentation)**；
* **智能推流节流**: 未唤醒时待命挂起推流节省 Token，唤醒后即刻播放升调和弦并拉起 8~10 秒流式问答窗口。

### 2.3 毫秒级中途打断 (Barge-In)
* **多维触发通道**: 服务端 VAD 响应事件、端侧麦克风能量检测、呼叫唤醒词「悄悄」声学打断、正面按键 Btn A 物理急停；
* **瞬时静音与终止**: 硬件 PA (AW8737) 瞬间静音，清空 DMA 环形缓冲，向云端下发 `response.cancel` 终止服务端未完成的文本与音频生成。

### 2.4 双级长程记忆压缩与安全截断
* **两级存储架构**: PSRAM 静态平铺环形数组 (`MAX_TURNS_IN_MEMORY=8`)，第 9 轮触发滑动窗口压缩为 `[前期摘要]`，核心 5 轮存入 Flash NVS 持久化；
* **Unicode 安全截断 (`safeTruncateUtf8`)**: 严格按 UTF-8 变长字节边界（1~4 字节）截断，彻底杜绝 RFC 6455 1007 协议违规。

### 2.5 智能 Web 配网与远程运维 (Captive Portal)
* **SoftAP 热点**: 设备未配置或连接失败时，秒级拉起 `StickS3-Buddy` 开放热点；
* **Web 控制台 (`http://192.168.4.1`)**: 扫描周边 2.4GHz Wi-Fi、填密存入 NVS；在线配置百炼 API-Key、模型参数与唤醒词灵敏度；
* **REST API 运维矩阵**:
  - `GET /system/metrics`: 实时 CPU 刷新帧率、Free SRAM、Free PSRAM、I2C 错误计数；
  - `GET /wakeword/status`: 离线唤醒词激活状态、灵敏度、倒计时与历史触发计数；
  - `POST /wakeword/config`: 动态热重载灵敏度与超时时间并持久化。

### 2.6 双模显示看板与汉字转码
* **ST7789v2 1.14" LCD**: SPI3 40MHz 极限 77 FPS 硬件驱动，局部刷新双缓冲仅占 4.5% CPU；
* **全集 GBK-to-Unicode 映射**: 固化 23,940 条目字库表，手机 BLE NUS 发送中文彻底消除乱码方块；
* **双模一键切换**: 单击侧键 Btn B，随时在“中文字幕全双工聊天视窗”与“多维工程诊断仪表盘”之间切换。

---

## 3. 固件内存与闪存布局 (Memory & Flash Layout)

| 分区 / 镜像 | 烧录基地址 | 标称大小 | 实际使用大小 | 使用率 / 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **Bootloader** | `0x00000000` | 32 KB | 15,104 字节 | [OK] Verified |
| **Partition Table** | `0x00008000` | 4 KB | 3,072 字节 | [OK] Verified |
| **App Binary (`firmware.bin`)** | `0x00010000` | 3,342,336 字节 | 2,432,525 字节 | **72.8%** (低于 75% 门限) |
| **Internal SRAM** | 运行时数据 | 327,680 字节 | 75,960 字节 | **23.2%** (远低于 25% 警戒线) |
| **PSRAM (Octal)** | 堆与缓存 | 8,388,608 字节 | ~7.3 MB 剩余 | 极为充裕 |

---

## 4. 自动化测试与质量检验 (Quality Assurance)

基线分支在 Python 3.12 环境下通过全量单元测试：
* `pytest tests/test_wakeword_engine.py -v`: 7 项测试全部 **PASSED**
* `pytest tests/test_wifi_and_bailian_pipeline.py -v`: 12 项测试全部 **PASSED**
* `pytest tests/test_audio_stream_pipeline.py -v`: 5 项测试全部 **PASSED**
* `pytest tests/test_firmware_driver_suite.py -v`: 7 项测试全部 **PASSED**
* `pytest tests/test_sticks3_three_schemes.py -v`: 7 项测试全部 **PASSED**
* **总计 38 项核心测试 100% 通过**，零告警、零断言失效。

---

## 5. 打包发布物清单 (Distribution Bundle)

发布包目录：`dist/release_v1.0.0/`
```text
dist/release_v1.0.0/
├── bootloader.bin         # ESP32-S3 引导程序
├── partitions.bin         # 8MB Flash 分区表
├── firmware.bin           # v1.0.0-stable 主固件二进制 (2.4MB)
├── flash.bat              # Windows 一键自动烧录批处理脚本
├── flash.ps1              # PowerShell 一键极速烧录脚本
├── flash.sh               # macOS / Linux 终端烧录脚本
├── manifest.json          # ESP Web Tools / WebSerial 标准清单
└── README.md              # 终端用户简易烧录与配网说明
```
