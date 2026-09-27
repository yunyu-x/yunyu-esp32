# M5Stack StickS3 Voice Buddy OS v1.0.0-stable 官方独立发布包

欢迎使用 **M5Stack StickS3 Voice Buddy OS (v1.0.0-stable)**！
本发布包为纯净、高稳定性的全双工语音交互与离线唤醒词基础系统，无需安装 PlatformIO 或配置 C++ 编译环境，支持一键极速烧录与 Web 配网使用。

---

## 一、 快速烧录 (1-Click Flashing)

### 1. 硬件准备
* 将 **M5Stack StickS3** 通过 USB-C 数据线插入电脑。
* 确保已安装通用 USB 串口驱动（设备管理器可见串口，如 `COM3` 或 `/dev/ttyACM0`）。

### 2. 执行烧录脚本
* **Windows 系统**：
  双击运行 `flash.bat`（或在 PowerShell 中运行 `.\flash.ps1`）。
* **macOS / Linux 系统**：
  打开终端，赋予执行权限后运行：
  ```bash
  chmod +x flash.sh
  ./flash.sh
  ```
* 脚本将自动扫描设备端口，并以 1,500,000 Baud 写入以下核心分区：
  - `0x00000`: `bootloader.bin` (ESP32-S3 Bootloader)
  - `0x08000`: `partitions.bin` (分区表：8MB Flash 划分)
  - `0x10000`: `firmware.bin` (主程序二进制，约 2.4MB)

---

## 二、 初始配置与智能 Web 配网

1. **连接热点**：烧录完成并重启后，设备若未联网将自动开启 SoftAP 热点：
   - **SSID**：`StickS3-Buddy`（无密码）
2. **打开控制台**：用手机或电脑浏览器访问：
   - **网址**：`http://192.168.4.1`
3. **完成配置**：
   - 在页面中扫描并选择您的家庭或办公 2.4GHz Wi-Fi，输入 Wi-Fi 密码；
   - 填写您的**阿里云百炼 (DashScope) API-Key**；
   - 可选微调音色（知燕、知雅等）与唤醒词灵敏度（默认 75%）；
   - 点击保存，设备将自动写入 Flash NVS 并秒级重启联网。

---

## 三、 核心操作与交互指南

* **语音唤醒**：在 1~3 米范围内呼叫唤醒词「**悄悄**」，设备播放提示和弦并点亮屏幕问答窗口，进入流式对话。
* **物理点按即说 (Push-to-Talk)**：单击正面主按键 **Btn A (G11)** 立即进入录音并向云端发送提问。
* **双模看板切换**：单击侧面按键 **Btn B (G12)** 在中文字幕聊天视窗与工程诊断看板间切换。
* **物理中途打断 (Barge-In)**：AI 播音时，呼叫「悄悄」或再次轻触 **Btn A** 即可瞬间静音打断，下发 `response.cancel` 终止服务端生成。
* **REST API 运维**：
  - `GET /system/metrics`: 查看系统堆内存、PSRAM 与屏幕刷新帧率
  - `GET /wakeword/status`: 查询唤醒词状态与统计
  - `POST /wakeword/config`: 动态调整唤醒词灵敏度与超时时间
