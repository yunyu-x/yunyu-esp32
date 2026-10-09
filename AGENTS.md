# yunyu-esp32 Autonomous Agent Guidelines & Engineering Handbook

> **适用范围**：所有接手 `yunyu-esp32` 项目的自主 AI Coding Agent (包括 Antigravity、Claude Code、Cursor、Copilot 等)。  
> **核心原则**：严格遵守六大不可违背工程公理，杜绝上下文漂移，确保 0 硬件试错成本。

---

## 1. 必读交接文档清单 (Mandatory Pre-Flight Reading)

在开始任何代码修改前，Agent **必须首先完整阅读**以下核心交接文件：

1. **项目最高工程公理**：[`docs/30_PROJECT_AXIOMS_AND_HANDOVER.md`](./docs/30_PROJECT_AXIOMS_AND_HANDOVER.md)  
   *规定了六大不可违背公理与实机监控基线。*
2. **Agent 提示词标准库**：[`docs/AGENT_CONTINUATION_PROMPTS.md`](./docs/AGENT_CONTINUATION_PROMPTS.md)  
   *提供了新会话继续开发通用母版与细分方向提示词。*
3. **移动端与小程序交接**：[`docs/29_微信小程序与移动端研发交接指南_HANDOVER_MOBILE.md`](./docs/29_微信小程序与移动端研发交接指南_HANDOVER_MOBILE.md)  
   *涵盖 Apple HIG 规范、双通道配网与发布配置。*
4. **Meta Muse 接入详案**：[`docs/31_Meta_Muse_Gadgets微型自重构机器人与物理伴侣全栈接入方案与工程实施详案.md`](./docs/31_Meta_Muse_Gadgets微型自重构机器人与物理伴侣全栈接入方案与工程实施详案.md)  
   *Meta Muse Gadgets 生态与三层协同架构。*
5. **迪士尼影院级动作与小程序导播**：[`docs/32_JOLLYBOT_17_CINEMATIC_POSES_AND_MINIPROGRAM_GUIDE.md`](./docs/32_JOLLYBOT_17_CINEMATIC_POSES_AND_MINIPROGRAM_GUIDE.md)  
   *17 套影院级动作姿态、自动阅兵巡礼、双重 30 分钟压测与导播台指南。*

---

## 2. 六大不可违背工程公理速记表 (The 6 Constitutional Axioms)

| 公理代号 | 核心公理法则 | 严禁行为 (Negative Invariants) | 必须执行动作 (Positive Invariants) |
| :---: | :--- | :--- | :--- |
| **公理一** | **真实硬件烧录验证公理**<br/>(Real Hardware Law) | 严禁仅凭编译通过即宣称交付，严禁跳过实机串口诊断。 | 固件修改必烧录物理 `COM3`，触发 RTS/DTR 硬重启，实测 10~15 秒日志确认自检全过。 |
| **公理二** | **中断与协议异步解耦公理**<br/>(Async Decoupling Law) | 严禁在 Bluedroid `BTC_TASK`（仅 ~3KB 栈）中执行 Flash 读写、WiFi 重连或动态 JSON 反序列化。 | 仅在自旋锁内向微栈队列入队字节（< 32B），在 `loopTask` 中异步消费。 |
| **公理三** | **显存零撕裂双缓冲物理公理**<br/>(Zero-Tear Double Buffer Law) | 严禁在 ST7789 物理屏幕上分步清屏或直接绘制控件（会导致 15Hz 剧烈频闪）。 | 在 8MB PSRAM 中开辟 135×240 精灵画布（`LGFX_Sprite`），离线合成后 DMA 单次原子推送。 |
| **公理四** | **网络显式区分与一致性公理**<br/>(Explicit Network Coherence Law) | 严禁混淆手机热点与宽带 Wi-Fi；严禁小程序主页与设置页数据源出现逻辑分歧。 | 手机热点显式亮橙底 "HOT" 并开启流量熔断保护；宽带显式亮绿底 "WiFi"；断网亮红底 "!NET"。 |
| **公理五** | **零功能回退与渐进加固公理**<br/>(Non-Regression Law) | 严禁无进度无超时运行黑盒测试，严禁因新增特性导致已有核心基线劣化。 | 每次提交前必须全绿通过具备**实时逐项进度展示**与**超时熔断守护**（默认 120s，单测防卡死 25s）的自动化回归测试 (`python -u scripts/run_tests.py --timeout 120`)。 |
| **公理六** | **自适应协议与防截断编码公理**<br/>(Adaptive Encoding Law) | 严禁跨字节撕裂截断多字节 UTF-8 中文字符（会导致 WebSocket 1007 协议崩溃）。 | 长文本支持自适应分包拼帧；截断必须调用 `safeTruncateUtf8` 字符级边界保护器。 |

---

## 2.1 敏感信息防线与工程卫生法则 (Security, Privacy & Repository Hygiene Law)

本法则为全栈研发与代码提交的**不可逾越的安全红线**：

1. **严禁凭证硬编码 (Zero Credential Leakage)**：
   - 严禁在任何代码、测试脚本、文档或配置中明文硬编码真实 API Key（如百炼 `sk-...`、OpenAI、GitHub Token、私钥证书等）。
   - 所有运行时敏感凭据必须通过环境变量（`os.environ` / `process.env`）或受 `.gitignore` 保护的本地 `.env` 文件读取。
   - 仓库仅允许提交无敏感数据的配置模板（如 [`.env.example`](./.env.example)）。
2. **严禁私有与临时资产入库 (Zero Noise & Clutter)**：
   - 严禁将微信开发者工具个人状态（`project.private.config.json`）、IDE 个人配置（`.vscode/`, `.idea/`）提交至仓库。
   - 严禁将调试音频（`*.pcm`, `*.wav`）、临时运行日志（`*.log`, `logs/`）、编译产物（`.pio/`, `__pycache__/`）等非必要产物纳入版本控制。
3. **提交前双重卫生审计 (Pre-Commit Audit)**：
   - 提交任何变更前，必须执行未忽略文件核对与敏感凭证检索：`git status --ignored`，确保只有符合规范的源码、文档与正式测试进入暂存区。

---

## 3. 标准开发流水线与验证命令 (Standard Verification Flow)

```powershell
# 1. 运行全套自动化测试 (必须具备实时进度展示与超时熔断控制，100% 通过)
python -u scripts/run_tests.py --timeout 120

# 2. 检查工作区工程卫生与敏感信息 (严禁泄露密钥与私有文件)
python -c "import os, re; p=re.compile(r'sk-[a-zA-Z0-9]{20,}'); leaks=[f for r,d,fs in os.walk('.') if not any(x in r for x in ['.git','.pio','__pycache__','.env']) for f in fs if p.search(open(os.path.join(r,f),encoding='utf-8',errors='ignore').read())]; print('LEAKS FOUND:', leaks) if leaks else print('ALL CLEAR: 0 leaked secrets!')"

# 3. 编译 StickS3 嵌入式固件
python -m platformio run -e m5sticks3_buddy

# 4. 烧录固件至物理硬件 (COM3)
python -m platformio run -e m5sticks3_buddy -t upload

# 5. 触发 RTS/DTR 硬件硬重启并读取实时串口日志 10~15 秒
python -c "import serial, time; ser = serial.Serial('COM3', 115200, timeout=1); ser.setDTR(False); ser.setRTS(True); time.sleep(0.1); ser.setRTS(False); time.sleep(0.2); start = time.time(); [print(ser.readline().decode('utf-8', errors='replace').strip()) for _ in iter(lambda: ser.readline() if time.time()-start < 10 else None, None)]; ser.close()"

# 6. 启动桌面 Web 伴侣控制台服务
python scripts/lingbuddy_companion.py

# 7. 文档与学术公式公理化交叉审计
python skills/document-content-verifier/scripts/verify_pipeline.py --input docs/30_PROJECT_AXIOMS_AND_HANDOVER.md --mode all
```

---

## 4. 交付与交接规范 (Handoff & Continuation Standard)

依据工程规范，**任何 Agent 完成阶段性开发任务并提交代码时，必须在交付总结中附带标准化继续开发提示词描述**，格式请严格遵循 [`docs/AGENT_CONTINUATION_PROMPTS.md`](./docs/AGENT_CONTINUATION_PROMPTS.md) 中的通用母版。
