# 贡献指南 (Contributing to yunyu-esp32)

感谢您对 **yunyu-esp32** 开源项目的关注与支持！本项目致力于为微型自重构机器人与智能硬件伴侣提供高度可靠、工业级标准的嵌入式硬件与固件生态。

---

## 1. 行为准则 (Code of Conduct)
我们倡导友好、开放、包容与互相尊重的技术交流环境。在参与讨论、提交 Issue 或提交 PR 时，请保持礼貌与客观。

---

## 2. 参与流程 (Workflow)

1. **Fork 本仓库** 到个人 GitHub 账号；
2. **克隆分支并创建特性分支**：
   ```bash
   git clone https://github.com/<your-username>/yunyu-esp32.git
   git checkout -b feature/my-new-feature
   ```
3. **本地开发与构建验证**：
   - 依赖安装：`pip install -r requirements.txt`
   - 固件编译：`python -m platformio run -d firmware/m5sticks3_buddy`
   - 单元测试：`pytest tests/ -v`
4. **提交代码 (Commit Guidelines)**：
   提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
   - `feat(...)`: 新功能引入
   - `fix(...)`: 缺陷修复
   - `docs(...)`: 文档补充与调整
   - `test(...)`: 测试用例补充
   - `refactor(...)`: 代码重构
5. **发起 Pull Request**：
   将特性分支推送到个人 Fork 仓库，并在 GitHub 上向 `main` 分支发起 Pull Request，等待 CI 自动化测试通过与 Maintainer Review。

---

## 3. 硬件与固件开发规范

1. **临界区安全**：严禁在中断回调或 BLE 回调中执行阻塞式 I2C 读写或大屏全刷新；
2. **内存规范**：对于大体积音频流、图像帧或中文字库，优先使用板载 8MB PSRAM（`ps_malloc`），严禁挤占内部 SRAM；
3. **代码整洁**：头文件保护必须使用 `#pragma once`，遵循 C++14/C++17 现代标准。
