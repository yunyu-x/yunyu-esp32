---
name: embedded-device-inspector
description: >-
  Real-time embedded hardware diagnostic monitoring, voice interaction tracking, and crash analysis
  for M5Stack StickS3 (ESP32-S3) LingBuddy companion. Captures serial telemetry over COM3, detects
  speech freeze/stuck states, diagnoses panic/reset codes (rst:0x..), and monitors hardware load rates.
---

# Embedded Device Diagnostic Inspector Skill

Use this skill when developing, testing, or diagnosing physical embedded devices—especially the M5Stack StickS3 (ESP32-S3) LingBuddy companion running full-duplex voice models (Alibaba Bailian / DashScope Realtime).

---

## 1. Skill Purpose & Core Capabilities

When conducting human-in-the-loop voice interactions or automated stress tests on the physical StickS3, subtle issues such as:
1. **Silent Freezes / Stucks ("收到音后卡住不输出")**: VAD triggers speech detection, but the system gets stuck in `THINKING` state without generating audio output.
2. **Crash & Reboot Loops ("异常重启 / Panic")**: `rst:0x4 (PANIC)`, `rst:0xc (RTC_SW_CPU_RST)`, FreeRTOS stack overflow, mbedTLS heap corruption, or Watchdog timeouts.
3. **Resource Overloads ("硬件负荷率超标 >70%")**: Internal SRAM dynamic load, PSRAM pool exhaustion, or task stack depletion.

This skill provides a daemon monitoring service that connects to the hardware serial port (COM3), analyzes incoming telemetry with millisecond precision, logs full trace history, and continuously updates a structured JSON diagnostic snapshot.

---

## 2. Quick Start & Execution

### Starting the Background Monitoring Service

```powershell
# 启动嵌入式监控守护服务 (默认监听 COM3 @ 115200)
python skills/embedded-device-inspector/scripts/monitor_service.py
```

或者使用项目根目录的统一入口：
```powershell
python scripts/embedded_monitor_service.py
```

### 监控产物与文件路径

* **全量原始流水日志**：`logs/embedded_diagnostics.log`（包含全部串口文本与毫秒时间戳）
* **实时遥测结构化快照**：`logs/diagnostic_summary.json`（可随时被其他自动化脚本或 Agent 读取）

### 查看当前遥测快照

```powershell
python -c "import json; print(json.dumps(json.load(open('logs/diagnostic_summary.json', encoding='utf-8')), ensure_ascii=False, indent=2))"
```

---

## 3. Diagnostic Event Patterns (三大核心诊断模式)

### 3.1 收到声音后卡住不输出 (Freeze / Stuck Detection)
追踪完整的人机语音交互生命周期：
* `[VOICE-IN] Server-VAD: User started speaking!`
* `[VOICE-STOP] Server-VAD: User stopped speaking -> Thinking...`
* `[DIAG-FLOW] 用户发言完毕，系统转入思考状态 (THINKING)...`
* `[AUDIO-TTFA] 首音频响应耗时 (TTFA): <ms>`
* `[AUDIO-PLAY] 🔊 喇叭全双工流式播放已启动`

**诊断判定规则**：
* 若在 `THINKING` 状态停留超过 **3.0 秒** 未收到音频播放事件，触发 `[STUCK-WARN]`。
* 若从 `THINKING` 状态未出声直接跳回 `LISTENING`，判定为严重卡死丢包并记录至 `stuck_events`。
* 若触发 10 秒看门狗超时 (`Thinking state timeout >10s`)，判定为云端响应未下发或被本地丢弃。

### 3.2 异常复位与 Panic 诊断 (Reboot & Crash Analysis)
自动解析硬件复位码：
* `rst:0x1`: `POWERON_RESET`（上电/插拔电源复位）
* `rst:0x3`: `SW_RESET`（软件调用 `esp_restart()`）
* `rst:0x4`: `OWDT_RESET / ESP_RST_PANIC`（Guru Meditation 致命崩溃）
* `rst:0x7 / 0x8`: `TG0WDT_SYS_RESET / TG1WDT`（硬件看门狗超时，说明主循环或协议任务死锁）
* `rst:0xc`: `RTC_SW_CPU_RST`（CPU 断言失败或异常复位，通常由 heap corruption 或 stack overflow 引发）
* `rst:0x15`: `USB_UART_CHIP_RESET`（DTR/RTS 硬件触发硬复位）

当出现 `CORRUPT HEAP` 或 `assert failed` 时，自动捕获堆栈回溯（`Backtrace: 0x40378226:0x3fcce8f0 ...`），并通过 `addr2line` 映射至具体源码行。

### 3.3 硬件负荷率越界报警 (Hardware Load Limits < 70%)
实时解析 `[StickS3-SYS]` 串口遥测帧：
* **全局复合 RAM 负荷率**：`ram_overall_load < 70.0%`
* **内部 SRAM 动态堆负荷率**：`sram_dyn_load < 70.0%`
* **FreeRTOS 主任务栈负荷率**：`stack_load < 70.0%`
* **I2C 物理交互失败率**：`i2c_fails == 0`

任一指标超过 70% 立即写入 `overload_alerts` 并在控制台高亮预警。

---

## 4. 常见排查与手术级修复速查表

| 故障现象 | 串口特征日志 | 根本原因 | 根治修复方案 |
| :--- | :--- | :--- | :--- |
| **收到声音后卡住** | `Local silence timeout (>800ms)` 提前触发，无 `response.created` | 本地静音时钟与 Server-VAD 未对齐，且 commit 缺失 `response.create` | 在 `speech_started` 时同步刷新时钟；移除过早截断，确保 Server-VAD 自然收敛。 |
| **说话中途崩死重启** | `CORRUPT HEAP: Bad tail/head` + `multi_heap_free` assert | mbedTLS 深层异常销毁导致 8KB 栈溢出踩坏相邻堆 Canary | 将 `ws_cfg.task_stack` 扩充至 **16KB**，`buffer_size` 扩至 **20KB**。 |
| **并发写入错误** | `TRANSPORT_WS: Error transport_poll_write errno=11` | Core 1 与 Core 0 同时无锁并发调用 `esp_websocket_client_send_text` | 增加 `_ws_send_mutex` 互斥量，所有发送强制获取锁。 |
| **音频爆破杂音** | 播放声音时伴随爆音或断续 | 动态增益超标导致数字削顶失真，DMA 写入未软限幅 | 将增益映射为 1:1 动态范围，引入平滑软限幅饱和器（Soft-Clipping）。 |
