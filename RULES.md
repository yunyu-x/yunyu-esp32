# yunyu-esp32 Repository Rules & Development Standards

## 1. 架构定位
`yunyu-esp32` 是独立完整的具身 AI 伴侣与开源硬件生态工程：
- 核心物理实体：M5Stack StickS3（代号「悄悄」）
- 移动端：微信小程序（Apple HIG 美学设计）
- 桌面端：Web Bluetooth 伴侣与向量记忆库
- 代理生态：Meta Muse Gadgets 框架与 Noise_XX 隧道
- 开源硬件：MicroDuck 双足机器人与灵方 PCBA v2.0

## 2. 核心公理与开发准则
- 遵守六大不可违背工程公理（详见 `docs/30_PROJECT_AXIOMS_AND_HANDOVER.md`）
- 严禁未经物理硬件（COM3）验证即宣称交付
- 严禁在 Bluedroid 中断/底层任务中执行阻塞式或大内存操作
- 严禁物理屏直写，必须使用 PSRAM 双缓冲显存画布（`LGFX_Sprite`）
- 严禁破坏现有基线（离线唤醒、百炼双工语音、物理打断、12种微表情、记忆压缩）

## 3. 提交与测试标准
- 提交前必须全绿通过自动化回归测试：`pytest tests/ -v`
- 固件修改必须编译通过：`python -m platformio run -e m5sticks3_buddy`
- 遵循 Conventional Commits 提交信息规范（如 `feat(...)`, `fix(...)`, `docs(...)`）
