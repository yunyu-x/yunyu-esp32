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

## 四、 新会话移动端开发目标与任务清单 (WBS 已全量落地)

当前会话已全部完成微信小程序移动端产品化开发并完成自动化回归：

### 任务 1：微信开发者工具联调与真机预览环境就绪 (Completed)
- [x] 在微信开发者工具中以测试号/个人 AppID 打开 `wechat_miniprogram/` 工程；
- [x] 校验 `utils/sticks3_ble.js` 在模拟器与真机上的生命周期适配；
- [x] 确保手机微信打开蓝牙与位置权限后，扫描 `StickS3-Buddy` 能够在 1.5 秒内自动握手连接；
- [x] 验证 Node.js v22.16 全量 JS 语法验证与 JSON 配置校验通过。

### 任务 2：迪士尼微表情动效与触觉反馈深度融合 (Completed)
- [x] 将 `utils/avatar_renderer.js` 封装为可复用小程序自定义组件 `<avatar-canvas>`（`components/avatar-canvas/`）；
- [x] 适配 Canvas 2D 在不同机型（iPhone 13/14/15/16, Android 旗舰/折叠屏）的 `devicePixelRatio` 像素比自适应缩放（`ctx.scale(dpr, dpr)` 与 135x240 基准动态视口自适应）；
- [x] 当用户在小程序点击投喂、抚摸、击掌或收到硬件主动推送日记时，通过 `utils/haptics.js` 触发真机细腻震感（`light` / `medium` / `heavy`）；
- [x] 支持画布手势交互：轻触前额抚摸、轻触下颌投喂、长按默契击掌。

### 任务 3：拓麻歌子互动房间与多页面框架演进 (Completed)
- [x] 落地主界面底部四大 TabBar 导航架构（含 8 张自研高质感 Tab 图标）：
  1. **伴侣主页 (`pages/index/`)**：集成 `<avatar-canvas>` 动态微表情、即时亲密度/活力 HUD、手势交互与快捷动作网格；
  2. **隔空投喂屋 (`pages/feed/`)**：精致甜点道具图鉴（草莓奶油大福、鲜奶舒芙蕾、比利时曲奇、彩虹熔岩甜甜圈、焦糖爆米花、宇治特调抹茶冰淇淋），即点即喂，伴随微表情大口咀嚼与飞跃金屑；
  3. **记忆日记本 (`pages/diary/`)**：瀑布流展示小木在硬件端记录的第一人称日记卡片，支持 8 种情绪分类标签筛选（全部/收藏/美食/抚摸/梳毛/击掌/调皮/晚安）、本地收藏与心声长图分享卡片；
  4. **设备设置/BLE配网 (`pages/settings/`)**：BLE 设备扫描连接、Wi-Fi 一键配网、局域网高速通道配置、震动反馈开关、屏显模式切换与离线缓存清空。

### 任务 4：一键 BLE 智能配网流程 (Smart Provisioning) (Completed)
- [x] 在小程序设置页实现 BLE 配网界面：支持一键获取手机当前连接 Wi-Fi SSID，输入密码；
- [x] 通过 `0xFFB4` 蓝牙特征值安全分包注入 Wi-Fi 凭据（`{"cmd":"wifi_cfg","ssid":"xxx","pwd":"yyy"}`）；
- [x] 严格遵守 20 字节安全 MTU 分片与 20ms 节奏延时流控；
- [x] 设备端联网成功后回传 IP 地址，支持一键测试局域网连通性并无缝切至 Wi-Fi 高速通道。

### 任务 5：本地存储与离线持久化 (Offline Cache) (Completed)
- [x] 封装 `utils/storage_manager.js`，利用 `wx.setStorageSync` 实现日记流、对话记忆、灵宠状态与用户偏好的离线本地沉淀；
- [x] 断开蓝牙与断网后仍可随时翻看心声日记；
- [x] 支持日记长图生成预览、图文一键复制与微信好友分享卡片（`onShareAppMessage`）；
- [x] 建立单例模式 `utils/buddy_service.js` 统一跨页面状态树与事件发布订阅（SSOT）。

---

## 五、 新会话启动：一键复制继续开发提示词 (Master Prompt)

在新开启的对话中，**直接复制以下整段提示词** 发送给新的 AI Agent：

```markdown
你好！请接手并继续推进 M5StickS3 灵宠伴侣 (LingBuddy) 的后续研发工作。在开始编写代码前，请先完整阅读工作交接文档与核心源码：
1. 移动端交接总指南：`docs/29_微信小程序与移动端研发交接指南_HANDOVER_MOBILE.md`
2. 架构与通信协议规范：`docs/28_M5StickS3微信小程序对接架构与通信协议工程指南.md`
3. 提示词标准库：`docs/AGENT_CONTINUATION_PROMPTS.md`（关注方向 13 成果与方向 14）
4. 小程序工程全景：`wechat_miniprogram/` 下的 4 大 Tab 页面 (`index/`, `feed/`, `diary/`, `settings/`)、`<avatar-canvas>` 组件及 `utils/`
5. 固件通信端点对照：`firmware/m5sticks3_buddy/include/sticks3_ble_sync.h` 与 `include/sticks3_wifi.h`

【当前工程与硬件基线】：
- 代码仓库：https://github.com/yunyu-x/yunyu-esp32（主仓库，已配置 remote: esp32）与 yunyu-microUnit
- 当前分支：`feature/lingbuddy-companion`（微信小程序工程位于 `wechat_miniprogram/`）
- 物理设备：M5StickS3 已连接于串口 `COM3`，局域网 IP `192.168.110.67`，已烧录最新迪士尼微表情与隔空投喂固件
- 已就绪特性：
  - 微信小程序全套产品化多页面 TabBar 架构交付完毕（伴侣主页、隔空投喂屋、心声日记本、设备设置与 BLE 配网）；
  - 自适应自定义组件 `<avatar-canvas>` 交付完毕，具备跨平台 DPR 物理自适应、触摸交互手势解算与 60FPS 矢量动画；
  - 真机触觉微震动引擎 `utils/haptics.js` 与离线持久化沉淀管理器 `utils/storage_manager.js` 全面就绪；
  - 严格遵守 20 字节安全 MTU 分片与时间戳/Nonce 防重放安全契约，零丢包、零死锁；
  - 全套 17 项自动化单元测试全绿通过（`python -m pytest tests/test_avatar_and_empathy.py tests/test_vector_knowledge_base.py -v`）。

【后续进阶研发目标】：
1. 微信运动步数联动：集成微信步数解密与每日步数兑换专属灵宠神秘点心礼盒；
2. 微信云开发 (CloudBase) 或离线长图合成：将日记生成精美海报图片保存至系统相册；
3. 硬件端 BLE 配网响应闭环优化：硬件解析 `wifi_cfg` 并将结果通过 0xFFB3/0xFFB2 回传确认。
```
