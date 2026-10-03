---
name: lingbuddy-firmware-ops
description: >-
  M5Stack StickS3 (ESP32-S3) LingBuddy companion firmware operations: building with PlatformIO,
  flashing via COM3, RTS/DTR hardware reset verification, FreeRTOS stack monitoring, and auditing
  compliance with the 6 Constitutional Axioms.
---

# LingBuddy Firmware Operations & Engineering Axioms Skill

Use this skill when developing, building, debugging, or flashing the embedded C++ firmware for the M5Stack StickS3 LingBuddy companion (`firmware/m5sticks3_buddy`).

---

## 1. The 6 Constitutional Invariants (不可违背的六大工程公理)

Every firmware modification MUST strictly comply with these six inviolable axioms:

1. **Axiom 1: Strict Hardware Verification Law (真实硬件烧录验证公理)**
   - NEVER consider a task complete based solely on compilation or tests.
   - Firmware MUST be flashed to physical hardware (`COM3`):
     ```powershell
     python -m platformio run -e m5sticks3_buddy -t upload
     ```
   - Trigger hardware hard-reset via RTS/DTR and capture serial logs for 10~15 seconds:
     ```powershell
     python -c "import serial, time; ser = serial.Serial('COM3', 115200, timeout=1); ser.setDTR(False); ser.setRTS(True); time.sleep(0.1); ser.setRTS(False); time.sleep(0.2); start = time.time(); [print(ser.readline().decode('utf-8', errors='replace').strip()) for _ in iter(lambda: ser.readline() if time.time()-start < 10 else None, None)]; ser.close()"
     ```
   - Confirm: `Tick` increments, `FPS > 90`, I2C fails == 0, zero panic or reboot loop.

2. **Axiom 2: Interrupt & Protocol Task Decoupling Law (中断与协议栈异步解耦公理)**
   - In low-level tasks like `BTC_TASK` (stack only ~3KB), NEVER perform blocking operations, dynamic JSON deserialization, NVS Flash writes, or Wi-Fi reconnects.
   - Micro-queue pattern: incoming bytes on BLE characteristic `0xFFB4` must only enqueue raw bytes into `_rx_queue` inside a spinlock critical section (< 32 bytes stack).
   - All parsing and config changes execute asynchronously in `loopTask` via `StickS3BLESync::getInstance().update()`.

3. **Axiom 3: Zero-Tear Double-Buffering Law (显存零撕裂双缓冲物理公理)**
   - NEVER write directly to ST7789 physical screen.
   - Allocate offscreen sprite canvas in 8MB PSRAM:
     ```cpp
     static LGFX_Sprite canvas(&display); // 135x240 @ 16-bit RGB565, 64.8KB PSRAM
     ```
   - Composite avatar micro-expressions, pupils, Chinese typography, and badges entirely offscreen, then push via SPI DMA in a single atomic frame: `canvas.pushSprite(0, 0)`.

4. **Axiom 4: Explicit Network Mode & Coherence Law (网络显式区分与端到端一致性公理)**
   - Mobile Hotspot: Warm orange `"HOT"` badge, active data quota monitoring and cutoff protection.
   - Broadband Wi-Fi: Bright green `"WiFi"` badge, high-speed LAN portal.
   - Offline / Error: Red `"!NET"` badge.
   - UI status on WeChat Mini-Program must be 100% consistent with physical device state.

5. **Axiom 5: Non-Regression & Progressive Hardening Law (零功能回退与渐进加固公理)**
   - Base features must never degrade: offline wakeword '悄悄', Alibaba Bailian DashScope Realtime full-duplex voice, button A physical barge-in, 12 Disney avatar emotions, 8-turn memory compaction, and I2C mutex (`g_i2c_mutex`).

6. **Axiom 6: Adaptive Multi-Chunk & Robust Encoding Law (自适应协议与防截断编码公理)**
   - BLE payloads exceeding MTU must be chunked and reassembled.
   - String truncation must use character-boundary safe `safeTruncateUtf8` to avoid WebSocket 1007 protocol violations.

---

## 2. Standard Firmware Toolchain Commands

- **Build Only**:
  ```powershell
  python -m platformio run -e m5sticks3_buddy
  ```
- **Build and Flash**:
  ```powershell
  python -m platformio run -e m5sticks3_buddy -t upload
  ```
- **Clean Build**:
  ```powershell
  python -m platformio run -e m5sticks3_buddy -t clean
  ```
- **Regression Tests**:
  ```powershell
  pytest tests/ -v
  ```

---

## 3. Core Source Files Reference

- [`main.cpp`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/src/main.cpp): System initialization, PSRAM canvas, loopTask, network status badges.
- [`sticks3_ble_sync.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/sticks3_ble_sync.h): Spinlock queue, async command processing, chunked memory streaming.
- [`sticks3_avatar.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/sticks3_avatar.h): 12 parametric emotions, gaze tracking, Tamagotchi intimacy engine.
- [`sticks3_audio.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/sticks3_audio.h): ES8311 + AW8737 I2S full-duplex audio task.
- [`sticks3_bailian_client.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/sticks3_bailian_client.h): DashScope Realtime WebSocket pipeline & barge-in.
- [`sticks3_wakeword.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/sticks3_wakeword.h): Offline acoustic wakeword matching.
- [`muse_gadget_client.h`](file:///d:/workspace/code/yunyu-esp32/firmware/m5sticks3_buddy/include/muse_gadget_client.h): Meta Muse Gadgets protocol client & serial hatch parser.
