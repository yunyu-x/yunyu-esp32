---
name: wechat-miniprogram-companion
description: >-
  WeChat Mini-Program development, Apple HIG design audit, BLE Nordic UART Service multi-chunk
  streaming, dual-channel network provisioning (broadband Wi-Fi + mobile hotspot with quota cutoff),
  and WeChat release/audit management for LingBuddy.
---

# WeChat Mini-Program Companion Skill

Use this skill when developing, testing, auditing, or releasing the LingBuddy companion WeChat Mini-Program located at `wechat_miniprogram/`.

---

## 1. Product Structure & Apple HIG Design System

The Mini-Program is organized into 4 primary tabs following Apple Human Interface Guidelines:

| Tab | Page Path | Core Features & Architecture |
| :--- | :--- | :--- |
| **首页 (Home)** | `pages/index/` | Dynamic `<avatar-canvas>` DPR rendering, 12 Disney emotions, inner thoughts carousel, quick status badges (HOT/WiFi/!NET), Taptic pet feedback. |
| **投喂 (Feed)** | `pages/feed/` | App Store style dessert shelf cards, intimacy heart progression, BLE inject command (`feed` / `snack`), interactive feeding animations. |
| **日记 (Diary)** | `pages/diary/` | Apple Notes aesthetic typography, emotional reflections stream, long-term memory sync via BLE multi-chunk stream. |
| **设置 (Settings)** | `pages/settings/` | iOS Grouped table layout, BLE scanner & connection manager, dual-channel provisioning wizard (WiFi & Hotspot), data traffic quota & cutoff protection. |

### Visual Design Tokens
- Background: Pure OLED Black `#000000`
- Grouped Card Layers: `#1C1C1E` (Level 1), `#2C2C2E` (Level 2), `#3A3A3C` (Level 3)
- Typography: SF Pro Text / Display & PingFang SC, standard system font sizes (11pt ~ 28pt)
- Borders: 0.5px subtle hairline dividers (`rgba(255, 255, 255, 0.12)`)
- Accents: System Blue (`#007AFF`), System Green (`#34C759`), System Orange (`#FF9500`), System Red (`#FF3B30`)

---

## 2. Communication Protocols & Utilities

### BLE NUS Service Definition
- **Service UUID**: `6E400001-B5A3-F393-E0A9-E50E24DCCA9E`
- **RX Characteristic** (Write): `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` (or `0xFFB4`)
- **TX Characteristic** (Notify): `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` (or `0xFFB3`)

### Multi-Chunk Reassembly
BLE MTU varies between devices (typically 20 ~ 512 bytes). When receiving long JSON payloads (e.g. dialogue memories), `sticks3_ble.js` automatically reassembles multi-packet fragments:
- Headers: `CHUNK_START`, `CHUNK_DATA`, `CHUNK_END`
- Unicode Boundary Guard: Uses UTF-8 character boundary checking to prevent partial multi-byte decoding errors.

### Mobile Hotspot Traffic Quota Protection
- Real-time data accumulation via background telemetry.
- Soft Warning: Notifies user when usage reaches 80% of configured quota.
- Hard Cutoff: Issues hardware cutoff command to disconnect Wi-Fi and stop Bailian audio stream when quota is exceeded, preventing unexpected mobile carrier charges.

---

## 3. WeChat Release & Review Best Practices

1. **Permission Hygiene**:
   - `app.json` contains ZERO unnecessary permissions (e.g. removed `scope.userLocation` to prevent error `80058`).
   - Only declare Bluetooth privacy permissions in the WeChat MP Admin Console (`__wxConfig__.privacyContract`).
2. **Demo Mode for App Reviewers**:
   - Includes a standalone simulation/mock mode enabling review team members without physical M5StickS3 hardware to test all 4 tabs, avatar animations, and mock dialogue flows.
3. **Automated Upload Tooling**:
   - `upload.js` uses `miniprogram-ci` with private keys stored in `project.private.config.json` for one-click continuous integration.

---

## 4. Key Source Files Reference

- [`app.json`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/app.json): TabBar configuration, subpackages, window styling.
- [`avatar-canvas.js`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/components/avatar-canvas/avatar-canvas.js): High-DPR Canvas 2D Disney parametric renderer.
- [`buddy_service.js`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/utils/buddy_service.js): Unified data service with local HTTP fallback.
- [`sticks3_ble.js`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/utils/sticks3_ble.js): BLE NUS connection management & multi-chunk parser.
- [`sticks3_wifi.js`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/utils/sticks3_wifi.js): Dual-channel Wi-Fi provisioning and quota tracking.
- [`storage_manager.js`](file:///d:/workspace/code/yunyu-esp32/wechat_miniprogram/utils/storage_manager.js): Persistent caching and offline memory storage.
