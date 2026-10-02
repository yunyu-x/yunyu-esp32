# M5StickS3 微信小程序与移动端研发交接指南 (Mobile Companion Handover Guide)

> **版本**：v1.0.0-mobile  
> **适用分支**：`feature/lingbuddy-companion`  
> **目标仓库**：`https://github.com/yunyu-x/yunyu-esp32`（主仓库）与 `https://github.com/yunyu-x/yunyu-microUnit`（协同仿真仓库）  
> **交接目标**：在新会话中无缝承接 M5StickS3 灵宠伴侣（LingBuddy）**微信小程序与移动端（iOS / Android）伴侣系统**的全链路产品化开发。

---

## 一、 项目背景与硬件基线

### 1. 硬件平台与物理连接
- **核心主控**：M5Stack StickS3 (ESP32-S3-PICO-1, 双核 240MHz, 8MB Flash, 8MB PSRAM)；
- **显示屏**：1.14 英寸 135x240 ST7789v2 彩屏；
- **六轴姿态**：BMI270 IMU（支持高敏抚摸微分解算、晃动晕眩检测、平放睡眠判定）；
- **音频架构**：ES8311 I2S Codec + AW8737 功放 + 离线唤醒词「悄悄」+ 阿里云百炼 16kHz PCM 全双工 WebSocket；
- **物理调试地址**：串口 `COM3`（波特率 115200），Wi-Fi 局域网分配 IP `192.168.110.67`。

### 2. 代码仓库分支拓扑
- **稳定主线**：`main` @ `v1.0.0-stable`（含独立免编译固件烧录包 `dist/release_v1.0.0/`）；
- **灵宠研发分支**：`feature/lingbuddy-companion`（**本次移动端开发所在分支**，承载微信小程序全套工程、微表情体系与 BLE 同步通信）。

---

## 二、 移动端已就绪资产全景 (Ready Assets)

当前工程已完成多角色架构委员会（Eng / CSO / Design / QA / Academic）论证并交付了开箱即用的微信小程序工程脚手架（位于仓库根目录 `wechat_miniprogram/`）：

```
wechat_miniprogram/
├── project.config.json       # 微信开发者工具配置 (AppID: touristor / 开启 ES6 / 增强编译)
├── sitemap.json              # 页面索引索引配置
├── app.json                  # 全局路由、深色赛博拓麻歌子样式与 scope.bluetooth 权限
├── app.js                    # 小程序全局生命周期与状态共享
├── app.wxss                  # 全局高质感深色毛玻璃 CSS 规范
├── pages/
│   └── index/                # 灵宠伴侣主控制台页面
│       ├── index.wxml        # 响应式布局：状态栏 + Disney 视窗 + 投喂/互动动作网格 + 日记流
│       ├── index.wxss        # 现代赛博微拟物与霓虹发光样式
│       ├── index.js          # 主页面逻辑：蓝牙自动连接、心跳巡检、乐观 UI 响应
│       └── index.json        # 页面配置
└── utils/
    ├── sticks3_ble.js        # BLE 0xFFB0 驱动：20 字节流控分包、帧重组拼装、断网自愈
    ├── sticks3_wifi.js       # Wi-Fi REST 驱动：/pet/status 与 /pet/action 局域网通信与 mDNS
    ├── avatar_renderer.js    # 微信 Canvas 2D 迪士尼微表情渲染引擎 (高光/咀嚼/金星/星尘)
    └── crypto_guard.js       # 16 字节随机 Nonce 与毫秒时间戳防重放安全加签器
```

### 辅助工程参考：
- **架构设计全案**：`docs/28_M5StickS3微信小程序对接架构与通信协议工程指南.md`（必读，详细定义了全部协议格式与辩论结论）；
- **Web 端参考基准**：`web/lingbuddy_companion.html`（已实现 Web Bluetooth 与 Wi-Fi 双模直连，可作为 UI/UX 对齐标杆）；
- **自动化测试合约**：`tests/test_avatar_and_empathy.py::test_wechat_miniprogram_suite_contract`（16 项测试全部绿灯通过）。

---

## 三、 通信协议与数据格式核心规范

微信小程序与 StickS3 支持 **BLE GATT**（近场低功耗直连）与 **局域网 Wi-Fi HTTP**（高吞吐同步）双通道协同工作：

### 1. BLE GATT 专属服务 (`0xFFB0`) 核心契约

微信小程序底层广播过滤：
- **Service UUID**：`0000FFB0-0000-1000-8000-00805F9B34FB`（短 UUID `0xFFB0`）
- **设备广播名**：`StickS3-Buddy`

| 特征值 UUID | 权限 | 作用与格式 | 核心流控准则 |
| :--- | :---: | :--- | :--- |
| **`0xFFB1`** | Notify | **分块长程记忆流**：硬件主动向小程序推送压缩的历史对话轮次 | 首包头 `[M:idx/total]`，后跟 UTF-8 分片数据 |
| **`0xFFB2`** | Read | **实时状态快照**：读取设备亲密度 Lv、经验 XP、电量、当前表情代码 | JSON 格式，单次直读 |
| **`0xFFB3`** | Notify | **灵宠心声日记**：硬件主动推送第一人称日记流水 | 字符串流，接收即触发日记卡片渲染 |
| **`0xFFB4`** | Write | **双向指令注入**：小程序向硬件发送控制动作与心跳 | **严守 20 字节安全 MTU 分片**，`sticks3_ble.js` 已实现分包步进写入 |

#### 20 字节安全分包写入准则 (Crucial MTU Constraint)
> [!WARNING]
> 微信小程序在 iOS 与 Android 各机型上，默认 BLE MTU 握手协商各异（普遍受限于 23 字节 ATT，净荷 20 字节）。  
> **严禁直接调用 `wx.writeBLECharacteristicValue` 发送大于 20 字节的 Buffer**，否则部分 Android 机型会静默丢包截断。必须统一调用 `sticks3_ble.writeInChunks()` 进行 20 字节切片和 20ms 延时流水线写入。

### 2. Wi-Fi 局域网 RESTful 接口

当手机与 StickS3 处于同一局域网（例如 `192.168.110.67` 或设备热点 `192.168.4.1`）时：
- **`GET /pet/status`**：获取实时灵宠数据
  ```json
  {"name":"小木","mood_id":1,"mood_name":"聆听中","level":1,"xp":25,"energy":100,"feeds":1,"grooms":0,"pets":0,"shakes":0,"convos":0,"diary":"主人喂我吃了一块草莓奶油大福，吧唧吧唧超级满足，活力满满！","avatar_mode":true}
  ```
- **`POST /pet/action`**：下发拓麻歌子互动
  - 请求载荷：`action=feed&item=草莓奶油大福`、`action=groom`、`action=play`、`action=pet`
  - 响应：返回更新后的状态与好感度，硬件同步播放和弦声效并切换迪士尼表情。

---

## 四、 新会话移动端开发目标与任务清单 (WBS)

在新会话中，重点推进微信小程序的产品化深度开发：

### 任务 1：微信开发者工具联调与真机预览环境就绪
- [ ] 在微信开发者工具中以测试号/个人 AppID 打开 `wechat_miniprogram/` 工程；
- [ ] 校验 `utils/sticks3_ble.js` 在模拟器与真机上的生命周期适配；
- [ ] 确保手机微信打开蓝牙与位置权限后，扫描 `StickS3-Buddy` 能够在 1.5 秒内自动握手连接。

### 任务 2：迪士尼微表情动效与触觉反馈深度融合
- [ ] 将 `utils/avatar_renderer.js` 封装为可复用小程序自定义组件 `<avatar-canvas>`；
- [ ] 适配 Canvas 2D 在不同机型（iPhone 13/14/15, Android 旗舰/折叠屏）的 `devicePixelRatio` 像素比自适应缩放；
- [ ] 当用户在小程序点击投喂、抚摸、击掌或收到硬件主动推送日记时，触发 `wx.vibrateShort({ type: 'medium' })` 细腻震感。

### 任务 3：拓麻歌子互动房间与多页面框架演进
- [ ] 扩展主界面底部 Tab 导航：
  1. **伴侣主页**：实时微表情动画、即时亲密度条、快捷动作面板；
  2. **隔空投喂屋**：精致甜点道具图鉴（草莓大福、鲜奶舒芙蕾、比利时曲奇、甜甜圈、爆米花），带有解锁与消耗动效；
  3. **记忆日记本**：瀑布流展示小木在硬件端记录的第一人称日记卡片，支持按情绪分类筛选与本地收藏；
  4. **设备设置**：Wi-Fi 一键配网、音量调节、音色切换、蓝牙重连与固件诊断。

### 任务 4：一键 BLE 智能配网流程 (Smart Provisioning)
- [ ] 在小程序中开发简易配网弹窗：手机搜索附近 Wi-Fi SSID，输入密码；
- [ ] 通过 `0xFFB4` 蓝牙特征值以分片 JSON 注入 Wi-Fi 凭据（`{"cmd":"wifi_cfg","ssid":"xxx","pwd":"yyy"}`）；
- [ ] 设备端联网成功后回传 IP 地址，小程序自动切换至 Wi-Fi 快速通道。

### 任务 5：本地存储与离线持久化 (Offline Cache)
- [ ] 利用 `wx.setStorageSync` 实现日记与记忆历史的离线沉淀，断开蓝牙后仍可随时翻看心声日记；
- [ ] 支持日记长图生成与朋友圈一键分享卡片。

---

## 五、 新会话启动：一键复制继续开发提示词 (Master Prompt)

在新开启的对话中，**直接复制以下整段提示词** 发送给新的 AI Agent：

```markdown
你好！请接手并继续推进 M5StickS3 灵宠伴侣 (LingBuddy) 的【微信小程序移动端产品化开发】。在开始编写代码前，请先完整阅读工作交接文档与核心源码：
1. 移动端交接总指南：`docs/29_微信小程序与移动端研发交接指南_HANDOVER_MOBILE.md`
2. 架构与通信协议规范：`docs/28_M5StickS3微信小程序对接架构与通信协议工程指南.md`
3. 提示词标准库：`docs/AGENT_CONTINUATION_PROMPTS.md`
4. 小程序工程脚手架：`wechat_miniprogram/` 下的 `app.json`、`utils/sticks3_ble.js`、`utils/sticks3_wifi.js`、`utils/avatar_renderer.js` 与 `pages/index/`
5. 固件通信端点对照：`firmware/m5sticks3_buddy/include/sticks3_ble_sync.h` 与 `include/sticks3_wifi.h`

【当前工程与硬件基线】：
- 代码仓库：https://github.com/yunyu-x/yunyu-esp32（主仓库，已配置 remote: esp32）与 yunyu-microUnit
- 当前分支：`feature/lingbuddy-companion`（微信小程序工程位于 `wechat_miniprogram/`）
- 物理设备：M5StickS3 已连接于串口 `COM3`，局域网 IP `192.168.110.67`，已烧录最新迪士尼微表情与隔空投喂固件
- 已就绪特性：
  - 微信小程序 starter SDK 已全部就绪，具备 20 字节安全 MTU 分片流控、断连自动退避重连、16 字节 Nonce 安全加签与 Canvas 2D 迪士尼表情渲染；
  - 硬件端已就绪 BLE GATT `0xFFB0`（0xFFB1 记忆流 / 0xFFB2 状态快照 / 0xFFB3 日记流 / 0xFFB4 指令注入）与局域网 Wi-Fi RESTful API（GET /pet/status, POST /pet/action）；
  - 全套 16 项自动化单元测试全绿通过（`python -m pytest tests/test_avatar_and_empathy.py tests/test_vector_knowledge_base.py -v`）。

【本次移动端开发目标】：
1. 深入完善 `wechat_miniprogram/` 微信小程序：
   - 将 `avatar_renderer.js` 封装为高自适应自定义组件 `<avatar-canvas>`，适配各类机型屏幕像素比；
   - 增加轻触抚摸、隔空投喂、舒适梳毛与默契击掌的真机触觉震动反馈 (`wx.vibrateShort`)；
   - 设计并实现「伴侣主页」、「隔空投喂屋」、「心声日记本」与「设备设置/BLE配网」的多页面或 Tab 交互架构；
   - 利用 `wx.setStorageSync` 实现灵宠日记与记忆历史的离线本地存储；
2. 保持 20 字节安全分片流控协议严格兼容性，确保 iOS 与 Android 手机端体验丝滑、零丢包；
3. 开发完成后，运行自动化契约测试，更新交接文档，并提交推送到远程仓库 `https://github.com/yunyu-x/yunyu-esp32` 的 `feature/lingbuddy-companion` 分支。
```
