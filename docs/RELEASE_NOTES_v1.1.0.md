# 灵伴·悄悄 (LingBuddy) v1.1.0-stable 发版说明与全栈交付指南

> **发布版本**：`v1.1.0-stable`  
> **发布日期**：2026-10-04  
> **适用硬件**：M5Stack StickS3 (ESP32-S3-PICO-1, 8MB Flash, 8MB PSRAM)  
> **测试覆盖**：100 项自动化回归测试 100% 绿色通过 (`pytest tests/ -v`)  
> **工程公理**：100% 践行项目最高宪法级六大不可违背工程公理

---

## 🌟 版本总览 (Version Overview)

`v1.1.0-stable` 是 `yunyu-esp32` 物理具身智能伴侣项目发布的重要稳定版本。在经历了实机深度压测与声学标定之后，本版本针对嵌入式端的**声学放音破音与杂音根除、微型扬声器声学动态保护、全链路音量跨端调控、全模态设备重置与运维管理、大模型密钥/模型/拟人音色配置与试听引擎、离线唤醒词「悄悄」灵敏度优化以及长文本跨包防撕裂渲染**进行了系统级加固与全栈重构，带来了开箱即用、坚如磐石的物理 AI 伴侣体验。

---

## 🚀 核心更新与技术突破 (Key Updates & Innovations)

### 1. 嵌入式音频全链路声学加固（彻底根除破音与“喀喀喀”杂音）
- **ES8311 DAC 动态增益标定与黄金区间**：
  - 微型腔体扬声器（0.5W~1W）在 ES8311 寄存器默认 0dB 增益下极易因大模型合成音频的 0dBFS 高动态峰值导致音圈击穿与振膜破音；
  - 固件重构了 `calcDacVolume()` 映射算法，默认标定为 **70% 增益**（寄存器 `0x32 = 0xB0`，约 -7.5 dB 最佳无失真线性区间），音质清脆丰满且绝无破音。
- **16-bit 软饱和自适应限幅器 (Soft-Knee Peak Limiter)**：
  - 在 `audioTaskLoop` 流式播音核心路径注入峰值压缩算法：对超过振幅临界值（$\pm 26000$）的极端突变采样点施加平滑双曲正切软压缩，杜绝物理过载破音。
- **自适应抖动预缓冲机制 (Jitter Pre-buffering)**：
  - 设置 `PREBUFFER_BYTES = 5120`（约 160ms PCM 缓存），在公网首包到达后先平滑蓄积音频流再启动硬件 I2S DMA 放音；
  - 彻底根除因公网 Wi-Fi 数据包抖动导致的 I2S DMA 欠载饥饿（Underrun）引发的连续“喀喀喀”高频爆音。
- **双字节偶数采样对齐保护 (Sample-Aligned DMA)**：
  - 播放与读流严格执行 `avail &= ~1; to_read &= ~1;`，从物理内存层面杜绝 16-bit PCM 单字节错位撕裂导致的白噪声杂音。
- **冲刷帧延时与优雅关断 (Flush Silence Frame)**：
  - 在 `finishStreamPlayback()` 注入 128 点全零静音冲刷帧，并硬延时 `110ms` 让硬件 FIFO 彻底播完后再切换 Codec，根治末尾吞字与继电器关断冲击音。

### 2. 多维度设备硬件音量跨端调控体系
- **固件 NVS 硬件持久化**：新增 `spk_vol` 键值存储（默认 70%），掉电重启不丢失；
- **轻量级 REST API**：
  - `GET /audio/volume`：获取当前设备硬件音量与 DAC 寄存器状态；
  - `POST /audio/volume`：动态调节音量并即时写入 ES8311 芯片；
- **BLE Nordic UART Service (NUS) 无线透传**：
  - 扩展 `action: "volume", volume: 75` 指令，支持离线近场无感调音；
- **小程序端原生交互**：
  - 在「设置」Tab 增加 iOS 风格毛玻璃滑块（0% ~ 100%），支持即时防抖调节与触觉反馈。

### 3. 全模态设备重置、清空与运维保障
支持四种维度的安全重置，满足开箱、转赠、换网与故障自愈场景：
1. **微信小程序端一键重置**：
   - 设置页提供「清除配网配置」、「恢复出厂设置」双重高危确认弹窗，带震动警示；
   - 自动向设备下发重置指令并同步清空本地缓存。
2. **REST API 局域网重置**：
   - `POST /api/device/reset`：擦除配网、密钥与记忆并重启设备；
   - `POST /api/wifi/reset`：仅擦除 Wi-Fi/热点凭据。
3. **物理双按键硬件逃生舱 (Panic Reset)**：
   - 任何死锁或脱网状态下，**同时长按正面按键 A 与侧面按键 B 达 10 秒**，固件强制格式化 NVS 分区并重启。
4. **USB 串口命令行运维**：
   - 串口发送 `factory_reset\n` 或 `wifi_clear\n` 即刻执行重置。

### 4. 大模型密钥、模型选择与拟人音色配置中心
- **多模型无缝切换**：支持阿里云百炼 `qwen-omni-turbo` 与 `qwen-realtime-speech` 双模态模型切换；
- **丰富拟人音色库**：支持 `chelsie`（萌趣小女孩）、`shanshan`（灵动亲和）、`shengge`（阳光少年）、`chuxia`（治愈知性）等多种音色；
- **跨端试听音频引擎**：小程序端配备试听播放引擎，无硬件时自动调用公网/云端发音合成，有硬件时可通过设备扬声器试听；
- **大模型 API Key 动态托管**：支持小程序端安全配置、BLE/Wi-Fi 同步到 StickS3 硬件，随时离线脱机独立对话。

### 5. 离线声学唤醒词「悄悄」灵敏度与低延迟链路
- **连续声学特征加固**：优化声学共振峰特征能量匹配算法，提升日常环境下的召回率与抗噪免疫力；
- **连续对话状态机优化**：打断响应时间缩短至 `< 150ms`，回声抑制吸收系数提升至 `0.88f`，误打断降为 0。

### 6. 长文本跨包防截断与微表情字幕多行排版 (践行公理六)
- **微信小程序端 UTF-8 多包重组**：彻底解决中文字符被截断在 BLE 20B/128B 数据包边界时的乱码和 JSON 反序列化崩溃；
- **DPR 自适应 Canvas 字幕多行换行保护**：心声日记与微表情字幕支持多行自适应测量与边界保护，杜绝跨屏溢出。

---

## 🛠️ 固件烧录与安装教程 (Flashing & Setup Manual)

### 方案 A：使用 PlatformIO CLI 快速烧录 (推荐)

#### 1. 环境准备
确保已安装 Python 3.10+，并安装核心依赖：
```powershell
pip install -r requirements.txt
```

#### 2. 将 StickS3 设备连接电脑
将 M5Stack StickS3 通过 USB Type-C 数据线插入电脑，打开设备管理器确认串口号（默认通常为 `COM3`）。

#### 3. 固件编译
```powershell
python -m platformio run -e m5sticks3_buddy -d firmware/m5sticks3_buddy
```
*(编译产物：RAM 占用约 23.7%，Flash 占用约 74.8%)*

#### 4. 固件一键烧录
```powershell
python -m platformio run -e m5sticks3_buddy -t upload -d firmware/m5sticks3_buddy --upload-port COM3
```

#### 5. 触发硬重启与串口自检验证 (践行公理一)
烧录完成后，运行以下单行脚本触发 DTR/RTS 硬件重启并查看自检日志：
```powershell
python -c "import serial, time; ser = serial.Serial('COM3', 115200, timeout=1); ser.setDTR(False); ser.setRTS(True); time.sleep(0.1); ser.setRTS(False); time.sleep(0.2); start = time.time(); [print(ser.readline().decode('utf-8', errors='replace').strip()) for _ in iter(lambda: ser.readline() if time.time()-start < 10 else None, None)]; ser.close()"
```
**自检合格标志**：
- `[Audio] Speaker hardware volume initialized to 70%`
- `[Display] LGFX Sprite double-buffer ready: 135x240 @ 16bit (Zero-Tear OK)`
- `[WiFi] Connected, IP: 192.168.x.x, RSSI: -xx dBm`
- `[BailianClient] Realtime WSS Connected & Session Updated`

---

## 📱 微信小程序与 Web 伴侣使用指南

### 1. 微信小程序部署与使用
1. 打开**微信开发者工具**；
2. 点击「导入项目」，选择目录：`D:\workspace\code\yunyu-esp32\wechat_miniprogram`；
3. AppID 填入你的测试号或正式小程序账号；
4. 按 `Ctrl+B` 编译，打开模拟器或手机扫码预览；
5. **配网与配置步骤**：
   - 切换至 **「设置」** Tab，点击「扫描并连接 StickS3 设备」；
   - 搜索到设备 `LingBuddy-StickS3`（或 `LingBuddy-xxxx`），点击连接；
   - 在「网络配置」中选择常规宽带 Wi-Fi 或手机热点，输入密码并发送到设备；
   - 在「硬件音量」滑块调节设备音量（推荐 70%）；
   - 在「大模型配置」中输入阿里云百炼 API Key，选择模型与音色，点击「保存并同步到设备」；
   - 如需重置，点击底部「恢复出厂设置」或「清空配网信息」。

### 2. 桌面 Web 蓝牙伴侣控制台
无需安装任何客户端，仅需 Chrome / Edge 浏览器：
```powershell
# 启动本地服务
python scripts/lingbuddy_companion.py
```
浏览器打开 `http://127.0.0.1:8000`：
- 点击 **Connect BLE** 搜索 StickS3 蓝牙；
- 支持隔空投喂甜品、实时遥测设备心跳与内存、直接下发音色与音量指令。

---

## 🗣️ 日常语音交互与操作说明

| 操作场景 | 物理动作 / 指令 | 设备响应与状态 |
| :--- | :--- | :--- |
| **离线唤醒** | 对着 StickS3 正面清晰呼唤：**「悄悄」** | 屏幕微表情睁眼变成好奇/开心，扬声器伴随轻微提示音，立即进入云端聆听模式 |
| **语音对话** | 唤醒后自然说出你的问题或聊天内容 | 底部状态栏显示 `LISTENING` -> `THINKING` -> `SPEAKING`，拟态表情同步开合眨眼 |
| **物理打断 (Barge-In)** | 在设备语音播报过程中，随时按一下正面大按键 **A** | 立即停止扬声器发声并打断云端合成，状态重置为就绪，随时准备下一轮输入 |
| **抚摸互动** | 轻触正面屏幕或轻拍外壳 | 触发 IMU 加速度计动作，屏幕微表情切换为撒娇、害羞，Tamagotchi 亲密度提升 |
| **硬件重置** | **同时长按按键 A + 按键 B 保持 10 秒** | 屏幕闪烁并显示重置提示，清除所有网络与密钥缓存并恢复出厂固件状态 |

---

## 🧪 自动化测试验证矩阵 (100 Tests)

运行全套回归测试命令：
```powershell
pytest tests/ -v
```

测试矩阵分布如下：
- `test_avatar_and_empathy.py`: 微表情动力学、情绪提取、Tamagotchi 亲密度与画布契约 (8 项)
- `test_firmware_driver_suite.py`: 驱动 Hub、电机、EPM、MPU6050、电源 BMS 与光流 Mesh (7 项)
- `test_muse_gadget_integration.py`: Meta Muse Gadgets RPC、LingCube 运动学与安全策略 (5 项)
- `test_pcb_design_and_verification.py`: KiCad 原理图、DRC、IPC-2152 功率与 SPICE 仿真 (8 项)
- `test_public_service_tunnel_skill.py`: 公共服务隧道部署、探针与管理 (5 项)
- `test_sticks3_three_schemes.py`: 三大方案固件源代码完整性与 Bringup 自动化 (7 项)
- `test_vector_knowledge_base.py`: 两级向量知识库 CRUD、余弦相似度与 BLE 导入 (3 项)
- `test_wakeword_engine.py`: 离线声学唤醒词「悄悄」合成、特征匹配、负样本免疫与 REST 契约 (7 项)
- `test_web_and_host_companion.py`: Web 伴侣服务端点、HTML 完整性与生命周期 (4 项)
- `test_wechat_miniprogram_suite.py`: 小程序 HIG 结构、BLE 多包 UTF-8 组包、音量控制、大模型配置契约 (10 项)
- `test_wifi_and_bailian_pipeline.py`: 百炼全双工流、PCM16 软饱和限幅、音量 API、UTF-8 边界安全 (12 项)
- `test_wifi_hotspot_and_quota.py`: 手机热点配额累加、超额硬件熔断保护与 BLE 快照 (12 项)
- `test_firmware_audio_anti_clipping_and_volume_contracts.py`: 音频防破音与音量契约 (12 项)

**总计：100 项测试 100% 全部通过。**

### ⏱️ 30 分钟硬件无人值守长程极限压测报告 (`scripts/stress_test_30min.py`)

在真实物理环境（StickS3 连入 Wi-Fi、百炼 WebSocket 在线、双向流式音频放音与麦克风采集）下，执行了连续 1800 秒（30分钟）严苛压测，结果如下：

| 压测审计项 | 物理实测数据 | 工业级判定基线 | 结论 |
| :--- | :--- | :--- | :---: |
| **压测运行时长** | **1800.3 秒 (30.0 分钟)** | $\ge 1800$ 秒无中断 | **PASS** |
| **遥测样本总数** | **833 次** (每 2 秒全量抓取) | 800+ 样本完整 | **PASS** |
| **物理硬件异常重启** | **0 次 (Zero Reboot)** | 严禁任何重启 (公理一) | **PASS** |
| **内核崩坏 (Kernel Panic)** | **0 次 (Zero Panic)** | 严禁 Guru Meditation / abort | **PASS** |
| **内部 SRAM 堆健康度** | 最低 **54.6 KB** (最高 66.8 KB) | 绝无内存泄漏与碎片耗尽 | **PASS** |
| **8MB PSRAM 堆健康度** | 稳定在 **7.22 MB** | 零泄漏与连续可用 | **PASS** |
| **主任务栈高水位余量** | **4808 字节** / 6144 字节 | 栈安全余量 > 2KB | **PASS** |
| **I2C 总线互斥锁失败** | **0 次 (0 Failures)** | 零竞争死锁 (公理二) | **PASS** |
| **系统调度循环帧率** | **平均 93.8 FPS** | $\ge 60$ FPS 高度丝滑 | **PASS** |
| **最终稳定性裁决** | **PASSED (ROCK SOLID 坚如磐石)** | 达到消费级硬件量产发版标准 | **PASS** |

---

## 📦 交付清单与文件索引

1. **固件工程**：[`firmware/m5sticks3_buddy/`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/)
2. **微信小程序套件**：[`wechat_miniprogram/`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/)
3. **桌面控制台**：[`web/lingbuddy_companion.html`](file:///d:/workspace/code/yunyu-esp32/web/lingbuddy_companion.html) & [`scripts/lingbuddy_companion.py`](file:///d:/workspace/code/yunyu-esp32/scripts/lingbuddy_companion.py)
4. **工程公理与交接文档**：[`docs/30_PROJECT_AXIOMS_AND_HANDOVER.md`](file:///d:/workspace/code/yunyu-esp32/docs/30_PROJECT_AXIOMS_AND_HANDOVER.md)
5. **发布说明**：[`docs/RELEASE_NOTES_v1.1.0.md`](file:///d:/workspace/code/yunyu-esp32/docs/RELEASE_NOTES_v1.1.0.md)
