# Meta Muse 开源硬件阿里云百炼大模型适配与公网 Agent 实施方案

> **专案编号**：Doc 32  
> **制定时间**：2026-10-04  
> **分支基线**：`feature/meta-muse-gadgets`（演进自 `feature/lingbuddy-companion`）  
> **架构定位**：yunyu-esp32 全栈最高系统架构规范 —— 阿里云百炼（Alibaba Cloud Bailian）全栈替代 Meta Muse 云端大脑，为 M5Stack StickS3 物理伴侣与灵方 LingCube MSRR 提供完全自主可控、极速响应、免账号绑定的个人 AI Agent 与公网穿透系统。
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0001`)
> - **待复核原文**: “> **专案编号**：Doc 32 > **制定时间**：2026-10-04 > **分支基线**：`feature/meta-muse-gadgets`（演进自 `feature/lingbuddy-companion`） > **架构定位**：yunyu-esp32 全栈最高系统架构规范 —— 阿里云百炼（Alibaba Cloud Bailian）全栈替代 Meta Muse 云端大脑，为 M5Stack StickS3 物理伴侣与灵方 LingCube MSRR 提供完全自主可控、极速响应、免账号绑定的个人 AI Agent 与公网穿透系统。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 目录

1. [执行摘要与问题定义](#1-执行摘要与问题定义)
2. [总体架构拓扑设计 (System Architecture)](#2-总体架构拓扑设计-system-architecture)
3. [BailianMuseCloudAgent 本地中枢架构设计](#3-bailianmusecloudagent-本地中枢架构设计)
4. [双轨公网穿透与持久化端点方案设计](#4-双轨公网穿透与持久化端点方案设计)
5. [全栈通信协议与契约规范 (API Contracts)](#5-全栈通信协议与契约规范-api-contracts)
6. [M5Stack StickS3 物理设备适配与六大工程公理贯彻](#6-m5stack-sticks3-物理设备适配与六大工程公理贯彻)
7. [具身协同端到端交互序列设计 (Interaction Sequences)](#7-具身协同端到端交互序列设计-interaction-sequences)
8. [墨菲定律防御与 FMEA 安全失效对策表](#8-墨菲定律防御与-fmea-安全失效对策表)
9. {==[分阶段工程落地路线图 (Phase 1 ~ Phase 5)](#9-分阶段工程落地路线图-phase-1--phase-5)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0002`)
> - **待复核原文**: “[总体架构拓扑设计 (System Architecture)](#2-总体架构拓扑设计-system-architecture) 3.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0003`)
> - **待复核原文**: “[BailianMuseCloudAgent 本地中枢架构设计](#3-bailianmusecloudagent-本地中枢架构设计) 4.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0004`)
> - **待复核原文**: “[双轨公网穿透与持久化端点方案设计](#4-双轨公网穿透与持久化端点方案设计) 5.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0005`)
> - **待复核原文**: “[全栈通信协议与契约规范 (API Contracts)](#5-全栈通信协议与契约规范-api-contracts) 6.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0006`)
> - **待复核原文**: “[M5Stack StickS3 物理设备适配与六大工程公理贯彻](#6-m5stack-sticks3-物理设备适配与六大工程公理贯彻) 7.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0007`)
> - **待复核原文**: “[具身协同端到端交互序列设计 (Interaction Sequences)](#7-具身协同端到端交互序列设计-interaction-sequences) 8.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0008`)
> - **待复核原文**: “[墨菲定律防御与 FMEA 安全失效对策表](#8-墨菲定律防御与-fmea-安全失效对策表) 9.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0009`)
> - **待复核原文**: “[分阶段工程落地路线图 (Phase 1 ~ Phase 5)](#9-分阶段工程落地路线图-phase-1--phase-5)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 1. 执行摘要与问题定义

### 1.1 Meta Muse Gadgets 的生态价值与落地瓶颈

{==2026年10月2日，Meta 官方以 Apache-2.0 协议开源了 **Muse Gadgets**（代码仓：[`facebookincubator/muse-gadget-sdk`](https://github.com/facebookincubator/muse-gadget-sdk)）。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}该项目首次定义了个人 AI 代理（Personal AI Agent）直连开源硬件开发板（特别是原生支持 **M5Stack StickS3**）的工业级工程范式：
- 基于 **Noise Protocol Framework** 的加密穿透隧道（Home Link）；
{==- 极具创意的 **Serial Hatch** 串口控制台交互机制（`>chat=...`, `>face=...`）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- 基于 ESP-IDF v6.0.1 的物理板级支持包与拟态微表情驱动；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- 标准化的 **Community Device Skills** 规范。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0010`)
> - **待复核原文**: “2026年10月2日，Meta 官方以 Apache-2.0 协议开源了 **Muse Gadgets**（代码仓：[`facebookincubator/muse-gadget-sdk`](https://github.com/facebookincubator/muse-gadget-sdk)）。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0011`)
> - **待复核原文**: “该项目首次定义了个人 AI 代理（Personal AI Agent）直连开源硬件开发板（特别是原生支持 **M5Stack StickS3**）的工业级工程范式： - 基于 **Noise Protocol Framework** 的加密穿透隧道（Home Link）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0012`)
> - **待复核原文**: “- 极具创意的 **Serial Hatch** 串口控制台交互机制（`>chat=...`, `>face=...`）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0013`)
> - **待复核原文**: “- 基于 ESP-IDF v6.0.1 的物理板级支持包与拟态微表情驱动；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0014`)
> - **待复核原文**: “- 标准化的 **Community Device Skills** 规范。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


然而，在实际面向全球与国内开发者落地时，Meta 方案暴露出三大致命瓶颈：
1. {==**账号门槛与隔离壁垒**：Meta Muse 云端系统运行于用户专属的 **Muse Secure VM**，依赖定向邀请制且需要绑定 Meta 个人账户获取 `mgst_...` 令牌；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==对于未开放地区或无 Meta 账号的开发者，硬件设备完全沦为“砖块”无法激活；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
2. {==**跨国云端高延迟与网络脆弱性**：Meta VM 与 `api.muse.ai/fetch_vms` 部署于海外，跨国 TLS/Noise 握手延迟通常达 1.5s~3s 以上，网络丢包率高，导致语音对话频繁卡顿甚至隧道断连；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
3. {==**中文语义理解与语音模型缺失**：Muse Spark 模型主要针对英文语境训练，其中文语音转写（ASR）与语音合成（TTS）效果无法满足高质量拟人陪伴要求。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0015`)
> - **待复核原文**: “然而，在实际面向全球与国内开发者落地时，Meta 方案暴露出三大致命瓶颈： 1.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0016`)
> - **待复核原文**: “**账号门槛与隔离壁垒**：Meta Muse 云端系统运行于用户专属的 **Muse Secure VM**，依赖定向邀请制且需要绑定 Meta 个人账户获取 `mgst_...` 令牌；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0017`)
> - **待复核原文**: “对于未开放地区或无 Meta 账号的开发者，硬件设备完全沦为“砖块”无法激活；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0018`)
> - **待复核原文**: “**跨国云端高延迟与网络脆弱性**：Meta VM 与 `api.muse.ai/fetch_vms` 部署于海外，跨国 TLS/Noise 握手延迟通常达 1.5s~3s 以上，网络丢包率高，导致语音对话频繁卡顿甚至隧道断连；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0019`)
> - **待复核原文**: “**中文语义理解与语音模型缺失**：Muse Spark 模型主要针对英文语境训练，其中文语音转写（ASR）与语音合成（TTS）效果无法满足高质量拟人陪伴要求。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 1.2 破局之道：阿里云百炼替代全栈架构

{==本项目提出并实施 **“阿里云百炼（Alibaba Cloud Bailian / DashScope）大模型矩阵 + 本地化 BailianMuseCloudAgent + public-service-tunnel 双轨免登录公网穿透”** 的全栈破局架构：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0020`)
> - **待复核原文**: “本项目提出并实施 **“阿里云百炼（Alibaba Cloud Bailian / DashScope）大模型矩阵 + 本地化 BailianMuseCloudAgent + public-service-tunnel 双轨免登录公网穿透”** 的全栈破局架构：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
graph LR
    subgraph Problem["Meta 原生痛点"]
        M1["海外账号体系<br/>(需 mgst_... 令牌)"]
        {==M2["海外 Secure VM<br/>(高延迟 / 偶发阻断)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        M3["英文专属模型<br/>(缺乏高保真中文语音)"]
    end

    subgraph Solution["百炼全栈替代方案"]
        {==B1["零账号门槛<br/>(本地 Agent 虚拟化鉴权)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==B2["国内百炼直连<br/>(DashScope 毫秒级流式响应)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==B3["Qwen2.5 + CosyVoice<br/>(全双工语音/拟人微表情)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==B4["public-service-tunnel<br/>(Cloudflare免登录/ngrok穿透)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    end

    {==Problem ==>|架构彻底重构| Solution==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0021`)
> - **待复核原文**: “M2["海外 Secure VM<br/>(高延迟 / 偶发阻断)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0022`)
> - **待复核原文**: “B1["零账号门槛<br/>(本地 Agent 虚拟化鉴权)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0023`)
> - **待复核原文**: “B2["国内百炼直连<br/>(DashScope 毫秒级流式响应)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0024`)
> - **待复核原文**: “B3["Qwen2.5 + CosyVoice<br/>(全双工语音/拟人微表情)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0025`)
> - **待复核原文**: “B4["public-service-tunnel<br/>(Cloudflare免登录/ngrok穿透)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0026`)
> - **待复核原文**: “Problem ==>|架构彻底重构| Solution”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


{==- **大脑平替**：将 Meta 云端 Secure VM / Muse Spark 替换为阿里云百炼大模型矩阵（**Qwen2.5-72B-Instruct** 负责复杂语义规划与 Function Calling 工具调用，**DashScope Realtime API** 负责 16kHz PCM 全双工低延迟流式语音问答）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **中枢虚拟化**：开发轻量级、高并发的本地宿主守护服务 **`BailianMuseCloudAgent`**，同时提供 HTTP REST、WebSocket 双工流、USB 串口 Serial Hatch 总线以及 Device Skills RPC 桥接；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **公网自由**：深度集成 `skills/public-service-tunnel` 技能，通过 Cloudflare Quick Tunnel 零配置免登录生成全球 Anycast 公网 HTTPS 端点，彻底解除局域网与路由器 NAT 限制；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **硬件公理**：严格贯彻 **六大工程公理**（`docs/30_PROJECT_AXIOMS_AND_HANDOVER.md`），确保 M5Stack StickS3 显存零撕裂、中断异步解耦与零功能回退。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0027`)
> - **待复核原文**: “- **大脑平替**：将 Meta 云端 Secure VM / Muse Spark 替换为阿里云百炼大模型矩阵（**Qwen2.5-72B-Instruct** 负责复杂语义规划与 Function Calling 工具调用，**DashScope Realtime API** 负责 16kHz PCM 全双工低延迟流式语音问答）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0028`)
> - **待复核原文**: “- **中枢虚拟化**：开发轻量级、高并发的本地宿主守护服务 **`BailianMuseCloudAgent`**，同时提供 HTTP REST、WebSocket 双工流、USB 串口 Serial Hatch 总线以及 Device Skills RPC 桥接；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0029`)
> - **待复核原文**: “- **公网自由**：深度集成 `skills/public-service-tunnel` 技能，通过 Cloudflare Quick Tunnel 零配置免登录生成全球 Anycast 公网 HTTPS 端点，彻底解除局域网与路由器 NAT 限制；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0030`)
> - **待复核原文**: “- **硬件公理**：严格贯彻 **六大工程公理**（`docs/30_PROJECT_AXIOMS_AND_HANDOVER.md`），确保 M5Stack StickS3 显存零撕裂、中断异步解耦与零功能回退。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 2. 总体架构拓扑设计 (System Architecture)

{==系统整体采用**四层解耦拓扑**设计：物理终端层、安全传输与公网穿透层、Cloud Agent 协同调度层、百炼大模型多模态智能层。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0031`)
> - **待复核原文**: “系统整体采用**四层解耦拓扑**设计：物理终端层、安全传输与公网穿透层、Cloud Agent 协同调度层、百炼大模型多模态智能层。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
flowchart TB
    %% 样式定义
    {==classDef device fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff;==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==classDef tunnel fill:#111827,stroke:#f59e0b,stroke-width:2px,color:#fff;==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==classDef agent fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff;==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==classDef cloud fill:#312e81,stroke:#8b5cf6,stroke-width:2px,color:#fff;==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

    %% 1. 物理终端层
    {==subgraph Tier1["【第一层】物理设备终端层 (Physical Hardware Tier)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==subgraph StickS3["M5Stack StickS3 物理伴侣 (LingBuddy)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==UI["Avatar 矢量微表情<br/>(PSRAM 64.8KB 双缓冲显存)"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==Audio["ES8311 Codec + AW8737<br/>(16kHz PCM 全双工麦克/扬声器)"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==Sensors["MPU-6050/BMI270 姿态<br/>+ M5PM1 电源门控"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==PTT["KEY1 (Pin 11) Push-to-Talk<br/>+ KEY2 (Pin 12) 模式切换"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        end

        {==subgraph LingCube["灵方 MSRR 具身自重构微型机器人 (LingCube)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==Motor["动量轮急刹翻滚<br/>(DRV8833 动力刹车)"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==EPM["6 端面双稳态 EPM<br/>(35N+ 脉冲自锁电永磁)"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {==Reflex["仿生神经反射引擎<br/>(DNp03 双侧避障/平衡棒)"]:::device==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        end
    end

    %% 2. 传输穿透层
    {==subgraph Tier2["【第二层】传输与公网穿透层 (Network & Tunnel Tier)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==LocalLink["USB CDC 串口 Hatch (COM3, 115200bps)<br/>+ 局域网 Wi-Fi / 手机热点 (HOT)"]:::tunnel==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==TunnelRouter["public-service-tunnel 智能路由引擎"]:::tunnel==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==CFTunnel["Cloudflare Quick Tunnel<br/>(免注册/免登录/零冲突 Anycast)"]:::tunnel==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==NgrokTunnel["ngrok 专属通道<br/>(静态域名/自动故障降级)"]:::tunnel==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    end

    %% 3. 本地 Cloud Agent 层
    {==subgraph Tier3["【第三层】本地宿主 Agent 中枢 (BailianMuseCloudAgent)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==HttpServer["FastAPI / AsyncIO Web 服务<br/>(端口 8000 / 8080)"]:::agent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==MetaCompat["Meta Muse 协议兼容适配器<br/>(/fetch_vms, /chat/stream, /api/voice/*)"]:::agent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==WSServer["WebSocket 双工流引擎<br/>(音频帧切片 / Server-VAD / 打断事件)"]:::agent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==SerialHatch["Serial Hatch 串口总线驱动器<br/>(>chat= 解析器 & @chat 帧生成器)"]:::agent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==SkillEngine["Device Skills 具身工具执行器<br/>(OpenAI / DashScope FC 桥接)"]:::agent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==TwinBridge["LingMatrix MuJoCo 数字孪生桥接器<br/>(HIL 物理动力学仿真验证)"]:::agent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    end

    %% 4. 云端百炼大模型层
    {==subgraph Tier4["【第四层】阿里云百炼云端大脑 (Alibaba Bailian AI Cloud)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==DashScopeLLM["DashScope Qwen 大模型矩阵<br/>(Qwen2.5-72B-Instruct / Qwen-Max)"]:::cloud==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==RealtimeASR_TTS["DashScope Realtime API (WSS)<br/>(16kHz PCM / CosyVoice / Paraformer)"]:::cloud==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==FunctionCalling["百炼具身工具调用引擎<br/>(JSON Schema Validation & ReAct)"]:::cloud==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    end

    %% 连接关系
    {==StickS3 <== "USB 串口 Hatch / Wi-Fi" ==> LocalLink==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==LingCube <== "BLE NUS 0xFFB4 / 38kHz 红外" ==> StickS3==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==LingCube <== "局域网 REST / UDP 8080" ==> SkillEngine==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

    LocalLink --> TunnelRouter
    TunnelRouter --> CFTunnel
    TunnelRouter --> NgrokTunnel
    {==CFTunnel ==> "持久化公网 HTTPS / WSS" ==> HttpServer==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==NgrokTunnel ==> "持久化公网 HTTPS / WSS" ==> HttpServer==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==LocalLink ==> "本地直连 (127.0.0.1:8000)" ==> HttpServer==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

    HttpServer <--> MetaCompat
    HttpServer <--> WSServer
    HttpServer <--> SerialHatch
    HttpServer <--> SkillEngine

    {==SerialHatch <== "COM3 物理串口" ==> StickS3==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    SkillEngine <--> TwinBridge

    {==MetaCompat <== "OpenAI 兼容协议 / SSE" ==> DashScopeLLM==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==WSServer <== "WSS 16kHz PCM 全双工流" ==> RealtimeASR_TTS==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==SkillEngine <== "Function Calling RPC" ==> FunctionCalling==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==FunctionCalling <--> DashScopeLLM==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0032`)
> - **待复核原文**: “classDef device fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff;”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0033`)
> - **待复核原文**: “classDef tunnel fill:#111827,stroke:#f59e0b,stroke-width:2px,color:#fff;”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0034`)
> - **待复核原文**: “classDef agent fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff;”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0035`)
> - **待复核原文**: “classDef cloud fill:#312e81,stroke:#8b5cf6,stroke-width:2px,color:#fff;”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0036`)
> - **待复核原文**: “subgraph Tier1["【第一层】物理设备终端层 (Physical Hardware Tier)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0037`)
> - **待复核原文**: “subgraph StickS3["M5Stack StickS3 物理伴侣 (LingBuddy)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0038`)
> - **待复核原文**: “UI["Avatar 矢量微表情<br/>(PSRAM 64.8KB 双缓冲显存)"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0039`)
> - **待复核原文**: “Audio["ES8311 Codec + AW8737<br/>(16kHz PCM 全双工麦克/扬声器)"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0040`)
> - **待复核原文**: “Sensors["MPU-6050/BMI270 姿态<br/>+ M5PM1 电源门控"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0041`)
> - **待复核原文**: “PTT["KEY1 (Pin 11) Push-to-Talk<br/>+ KEY2 (Pin 12) 模式切换"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0042`)
> - **待复核原文**: “subgraph LingCube["灵方 MSRR 具身自重构微型机器人 (LingCube)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0043`)
> - **待复核原文**: “Motor["动量轮急刹翻滚<br/>(DRV8833 动力刹车)"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0044`)
> - **待复核原文**: “EPM["6 端面双稳态 EPM<br/>(35N+ 脉冲自锁电永磁)"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0045`)
> - **待复核原文**: “Reflex["仿生神经反射引擎<br/>(DNp03 双侧避障/平衡棒)"]:::device”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0046`)
> - **待复核原文**: “subgraph Tier2["【第二层】传输与公网穿透层 (Network & Tunnel Tier)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0047`)
> - **待复核原文**: “LocalLink["USB CDC 串口 Hatch (COM3, 115200bps)<br/>+ 局域网 Wi-Fi / 手机热点 (HOT)"]:::tunnel”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0048`)
> - **待复核原文**: “TunnelRouter["public-service-tunnel 智能路由引擎"]:::tunnel”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0049`)
> - **待复核原文**: “CFTunnel["Cloudflare Quick Tunnel<br/>(免注册/免登录/零冲突 Anycast)"]:::tunnel”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0050`)
> - **待复核原文**: “NgrokTunnel["ngrok 专属通道<br/>(静态域名/自动故障降级)"]:::tunnel”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0051`)
> - **待复核原文**: “subgraph Tier3["【第三层】本地宿主 Agent 中枢 (BailianMuseCloudAgent)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0052`)
> - **待复核原文**: “HttpServer["FastAPI / AsyncIO Web 服务<br/>(端口 8000 / 8080)"]:::agent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0053`)
> - **待复核原文**: “MetaCompat["Meta Muse 协议兼容适配器<br/>(/fetch_vms, /chat/stream, /api/voice/*)"]:::agent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0054`)
> - **待复核原文**: “WSServer["WebSocket 双工流引擎<br/>(音频帧切片 / Server-VAD / 打断事件)"]:::agent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0055`)
> - **待复核原文**: “SerialHatch["Serial Hatch 串口总线驱动器<br/>(>chat= 解析器 & @chat 帧生成器)"]:::agent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0056`)
> - **待复核原文**: “SkillEngine["Device Skills 具身工具执行器<br/>(OpenAI / DashScope FC 桥接)"]:::agent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0057`)
> - **待复核原文**: “TwinBridge["LingMatrix MuJoCo 数字孪生桥接器<br/>(HIL 物理动力学仿真验证)"]:::agent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0058`)
> - **待复核原文**: “subgraph Tier4["【第四层】阿里云百炼云端大脑 (Alibaba Bailian AI Cloud)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0059`)
> - **待复核原文**: “DashScopeLLM["DashScope Qwen 大模型矩阵<br/>(Qwen2.5-72B-Instruct / Qwen-Max)"]:::cloud”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0060`)
> - **待复核原文**: “RealtimeASR_TTS["DashScope Realtime API (WSS)<br/>(16kHz PCM / CosyVoice / Paraformer)"]:::cloud”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0061`)
> - **待复核原文**: “FunctionCalling["百炼具身工具调用引擎<br/>(JSON Schema Validation & ReAct)"]:::cloud”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0062`)
> - **待复核原文**: “StickS3 <== "USB 串口 Hatch / Wi-Fi" ==> LocalLink”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0063`)
> - **待复核原文**: “LingCube <== "BLE NUS 0xFFB4 / 38kHz 红外" ==> StickS3”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0064`)
> - **待复核原文**: “LingCube <== "局域网 REST / UDP 8080" ==> SkillEngine”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0065`)
> - **待复核原文**: “CFTunnel ==> "持久化公网 HTTPS / WSS" ==> HttpServer”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0066`)
> - **待复核原文**: “NgrokTunnel ==> "持久化公网 HTTPS / WSS" ==> HttpServer”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0067`)
> - **待复核原文**: “LocalLink ==> "本地直连 (127.0.0.1:8000)" ==> HttpServer”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0068`)
> - **待复核原文**: “SerialHatch <== "COM3 物理串口" ==> StickS3”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0069`)
> - **待复核原文**: “MetaCompat <== "OpenAI 兼容协议 / SSE" ==> DashScopeLLM”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0070`)
> - **待复核原文**: “WSServer <== "WSS 16kHz PCM 全双工流" ==> RealtimeASR_TTS”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0071`)
> - **待复核原文**: “SkillEngine <== "Function Calling RPC" ==> FunctionCalling”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0072`)
> - **待复核原文**: “FunctionCalling <--> DashScopeLLM”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 3. BailianMuseCloudAgent 本地中枢架构设计

{==`BailianMuseCloudAgent` 是整个系统的调度中枢，使用 Python 3.10+ 构建，基于 `asyncio` 与 `FastAPI` 高性能异步架构，部署于开发者本地 PC、边缘网关或局域网主机。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0073`)
> - **待复核原文**: “`BailianMuseCloudAgent` 是整个系统的调度中枢，使用 Python 3.10+ 构建，基于 `asyncio` 与 `FastAPI` 高性能异步架构，部署于开发者本地 PC、边缘网关或局域网主机。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 3.1 核心模块拓扑与职责划分

1. **`BailianCompatServer`（协议兼容引擎）**：
   - 模拟 Meta 官方 VM 接口规范，让未修改或原生的 Meta 设备/客户端误以为连接到了官方云端；
   {==- 拦截并处理 `/fetch_vms`、`POST /api/voice/dictation`、`POST /chat/stream`、`GET /chat/subscribe`。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
2. **`DashScopeRealtimeBridge`（百炼实时双工语音桥）**：
   - 管理与阿里云 DashScope Realtime API（`wss://dashscope.aliyuncs.com/api-ws/v1/realtime`）的长连接；
   {==- 负责 16kHz 16-bit Mono PCM 音频流双向收发、Base64 封装/解包、服务端 VAD 静音切片检测、以及毫秒级 `response.cancel` 打断。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
3. **`SerialHatchEngine`（USB 串口双向总线引擎）**：
   - 托管物理串口（默认 `COM3`, 波特率 `115200`），具备防拔插自动重连能力；
   {==- 监听解析硬件发送或接收的 Hatch 转义指令（`>chat+=`, `>chat=`, `>face=`, `>robot=`, `>status`）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
   {==- 将百炼返回的流式文本按 Meta 官方帧规范打包为 `@chat {"type": "text", ...}` 回写串口。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
4. **`DeviceSkillRegistry`（具身技能工具执行器）**：
   - 将 `skills/gadget-lingcube-msrr` 与 `skills/gadget-lingmatrix-sim` 描述的物理指令封装为百炼标准 Function Calling JSON Schema；
   {==- 接收大模型下发的 Tool Calls，执行参数校验（如母线电压防棕变校验、EPM 热占空比冷却校验），并将动作下发至物理灵方或 MuJoCo 仿真器。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0074`)
> - **待复核原文**: “**`BailianCompatServer`（协议兼容引擎）**： - 模拟 Meta 官方 VM 接口规范，让未修改或原生的 Meta 设备/客户端误以为连接到了官方云端；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0075`)
> - **待复核原文**: “- 拦截并处理 `/fetch_vms`、`POST /api/voice/dictation`、`POST /chat/stream`、`GET /chat/subscribe`。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0076`)
> - **待复核原文**: “**`DashScopeRealtimeBridge`（百炼实时双工语音桥）**： - 管理与阿里云 DashScope Realtime API（`wss://dashscope.aliyuncs.com/api-ws/v1/realtime`）的长连接；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0077`)
> - **待复核原文**: “- 负责 16kHz 16-bit Mono PCM 音频流双向收发、Base64 封装/解包、服务端 VAD 静音切片检测、以及毫秒级 `response.cancel` 打断。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0078`)
> - **待复核原文**: “**`SerialHatchEngine`（USB 串口双向总线引擎）**： - 托管物理串口（默认 `COM3`, 波特率 `115200`），具备防拔插自动重连能力；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0079`)
> - **待复核原文**: “- 监听解析硬件发送或接收的 Hatch 转义指令（`>chat+=`, `>chat=`, `>face=`, `>robot=`, `>status`）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0080`)
> - **待复核原文**: “- 将百炼返回的流式文本按 Meta 官方帧规范打包为 `@chat {"type": "text", ...}` 回写串口。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0081`)
> - **待复核原文**: “**`DeviceSkillRegistry`（具身技能工具执行器）**： - 将 `skills/gadget-lingcube-msrr` 与 `skills/gadget-lingmatrix-sim` 描述的物理指令封装为百炼标准 Function Calling JSON Schema；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0082`)
> - **待复核原文**: “- 接收大模型下发的 Tool Calls，执行参数校验（如母线电压防棕变校验、EPM 热占空比冷却校验），并将动作下发至物理灵方或 MuJoCo 仿真器。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
classDiagram
    class BailianMuseCloudAgent {
        +FastAPI app
        {==+DashScopeRealtimeBridge realtime_bridge==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==+SerialHatchEngine serial_engine==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==+DeviceSkillRegistry skill_registry==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        +start(host, port)
        +stop()
    }

    {==class DashScopeRealtimeBridge {==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        -str api_key
        -str ws_url
        -WebSocket client_ws
        +connect_dashscope()
        {==+send_audio_chunk(bytes pcm_data)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        +cancel_response()
        +on_audio_delta(callback)
        +on_text_delta(callback)
    }

    class SerialHatchEngine {
        -Serial ser
        -str port
        -int baudrate
        +open()
        {==+write_chat_frame(str frame_type, str text, int msg_id)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        +write_face(str face)
        +poll_incoming()
        -handle_line(str line)
    }

    class DeviceSkillRegistry {
        -dict registered_tools
        +get_tools_schema() list
        {==+execute_tool(str name, dict args) dict==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==-roll_robot(str direction, float torque)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==-epm_latch(int face, str state)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        -set_avatar(str face)
    }

    {==BailianMuseCloudAgent *-- DashScopeRealtimeBridge==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==BailianMuseCloudAgent *-- SerialHatchEngine==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==BailianMuseCloudAgent *-- DeviceSkillRegistry==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0083`)
> - **待复核原文**: “+DashScopeRealtimeBridge realtime_bridge”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0084`)
> - **待复核原文**: “+SerialHatchEngine serial_engine”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0085`)
> - **待复核原文**: “+DeviceSkillRegistry skill_registry”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0086`)
> - **待复核原文**: “class DashScopeRealtimeBridge {”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0087`)
> - **待复核原文**: “+send_audio_chunk(bytes pcm_data)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0088`)
> - **待复核原文**: “+write_chat_frame(str frame_type, str text, int msg_id)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0089`)
> - **待复核原文**: “+execute_tool(str name, dict args) dict”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0090`)
> - **待复核原文**: “-roll_robot(str direction, float torque)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0091`)
> - **待复核原文**: “-epm_latch(int face, str state)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0092`)
> - **待复核原文**: “BailianMuseCloudAgent *-- DashScopeRealtimeBridge”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0093`)
> - **待复核原文**: “BailianMuseCloudAgent *-- SerialHatchEngine”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0094`)
> - **待复核原文**: “BailianMuseCloudAgent *-- DeviceSkillRegistry”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 4. 双轨公网穿透与持久化端点方案设计

### 4.1 穿透痛点与双轨容灾机制

{==开源硬件设备（M5Stack StickS3）在实际使用中往往脱离宿主机局域网（例如：使用手机 4G/5G 移动热点外出展示、异地实验室远程控制）。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==若 Cloud Agent 仅运行在 `127.0.0.1:8000`，物理设备无法远程回传音频或接收控制指令。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0095`)
> - **待复核原文**: “开源硬件设备（M5Stack StickS3）在实际使用中往往脱离宿主机局域网（例如：使用手机 4G/5G 移动热点外出展示、异地实验室远程控制）。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0096`)
> - **待复核原文**: “若 Cloud Agent 仅运行在 `127.0.0.1:8000`，物理设备无法远程回传音频或接收控制指令。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


{==本项目深度集成 `skills/public-service-tunnel` 技能规范，设计 **“Cloudflare Quick Tunnel (免登录) + ngrok (专属域名) 智能容灾降级”** 方案：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0097`)
> - **待复核原文**: “本项目深度集成 `skills/public-service-tunnel` 技能规范，设计 **“Cloudflare Quick Tunnel (免登录) + ngrok (专属域名) 智能容灾降级”** 方案：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
graph TD
    {==Start["启动 public-service-tunnel 探针"] --> CheckSvc{"检测本地 8000 端口<br/>Cloud Agent 是否就绪?"}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==CheckSvc -->|否| LaunchAgent["自动异步拉起 BailianMuseCloudAgent"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==CheckSvc -->|是| ProbeMode{"路由决策 (--tool auto)"}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    LaunchAgent --> ProbeMode

    {==ProbeMode --> TryNgrok["尝试启动 ngrok 隧道<br/>(读取 NGROK_AUTHTOKEN)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==TryNgrok -->|成功| CaptureNgrok["捕获 127.0.0.1:4040 API<br/>提取 https://*.ngrok-free.dev"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==TryNgrok -->|失败: ERR_NGROK_334<br/>域名已被占用 / 无 Token| AutoFailover["触发智能无缝降级<br/>(Smart Failover)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==AutoFailover --> TryCF["启动 Cloudflare Quick Tunnel<br/>(cloudflared --url http://127.0.0.1:8000)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==TryCF -->|免登录即开即用| CaptureCF["捕获 stdout 日志流<br/>正则提取 https://*.trycloudflare.com"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

    {==CaptureNgrok --> Persist["持久化端点资产至文件<br/>dist/public_preview_url.json"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    CaptureCF --> Persist

    {==Persist --> SyncDevice["端点同步下发机制"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==SyncDevice --> PathA["路径 A: 写入 NVS Flash (BLE 0xFFB4 配网下发)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==SyncDevice --> PathB["路径 B: 串口 Hatch 动态注入 (>endpoint=...)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==SyncDevice --> PathC["路径 C: 微信小程序伴侣云端看板展示"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0098`)
> - **待复核原文**: “Start["启动 public-service-tunnel 探针"] --> CheckSvc{"检测本地 8000 端口<br/>Cloud Agent 是否就绪?"}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0099`)
> - **待复核原文**: “CheckSvc -->|否| LaunchAgent["自动异步拉起 BailianMuseCloudAgent"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0100`)
> - **待复核原文**: “CheckSvc -->|是| ProbeMode{"路由决策 (--tool auto)"}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0101`)
> - **待复核原文**: “ProbeMode --> TryNgrok["尝试启动 ngrok 隧道<br/>(读取 NGROK_AUTHTOKEN)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0102`)
> - **待复核原文**: “TryNgrok -->|成功| CaptureNgrok["捕获 127.0.0.1:4040 API<br/>提取 https://*.ngrok-free.dev"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0103`)
> - **待复核原文**: “TryNgrok -->|失败: ERR_NGROK_334<br/>域名已被占用 / 无 Token| AutoFailover["触发智能无缝降级<br/>(Smart Failover)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0104`)
> - **待复核原文**: “AutoFailover --> TryCF["启动 Cloudflare Quick Tunnel<br/>(cloudflared --url http://127.0.0.1:8000)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0105`)
> - **待复核原文**: “TryCF -->|免登录即开即用| CaptureCF["捕获 stdout 日志流<br/>正则提取 https://*.trycloudflare.com"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0106`)
> - **待复核原文**: “CaptureNgrok --> Persist["持久化端点资产至文件<br/>dist/public_preview_url.json"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0107`)
> - **待复核原文**: “Persist --> SyncDevice["端点同步下发机制"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0108`)
> - **待复核原文**: “SyncDevice --> PathA["路径 A: 写入 NVS Flash (BLE 0xFFB4 配网下发)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0109`)
> - **待复核原文**: “SyncDevice --> PathB["路径 B: 串口 Hatch 动态注入 (>endpoint=...)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0110`)
> - **待复核原文**: “SyncDevice --> PathC["路径 C: 微信小程序伴侣云端看板展示"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 4.2 端点持久化与资产描述规范

{==穿透建立后，隧道守护引擎立即将端点元数据写入 `dist/public_preview_url.json` 与 `dist/public_preview_url.txt`，供全栈自动化工具链读取：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0111`)
> - **待复核原文**: “穿透建立后，隧道守护引擎立即将端点元数据写入 `dist/public_preview_url.json` 与 `dist/public_preview_url.txt`，供全栈自动化工具链读取：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```json
{
  "tool": "cloudflare",
  "local_port": 8000,
  {=="public_url": "https://random-assigned-name.trycloudflare.com",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  {=="wss_url": "wss://random-assigned-name.trycloudflare.com/ws/v1/realtime",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  "endpoints": {
    {=="fetch_vms": "https://random-assigned-name.trycloudflare.com/fetch_vms",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {=="voice_dictation": "https://random-assigned-name.trycloudflare.com/api/voice/dictation",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {=="chat_stream": "https://random-assigned-name.trycloudflare.com/chat/stream",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {=="companion_web": "https://random-assigned-name.trycloudflare.com/"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  },
  {=="created_at": "2026-10-04T15:30:00Z",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  "status": "active"
}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0112`)
> - **待复核原文**: “"public_url": "https://random-assigned-name.trycloudflare.com",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0113`)
> - **待复核原文**: “"wss_url": "wss://random-assigned-name.trycloudflare.com/ws/v1/realtime",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0114`)
> - **待复核原文**: “"fetch_vms": "https://random-assigned-name.trycloudflare.com/fetch_vms",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0115`)
> - **待复核原文**: “"voice_dictation": "https://random-assigned-name.trycloudflare.com/api/voice/dictation",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0116`)
> - **待复核原文**: “"chat_stream": "https://random-assigned-name.trycloudflare.com/chat/stream",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0117`)
> - **待复核原文**: “"companion_web": "https://random-assigned-name.trycloudflare.com/"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0118`)
> - **待复核原文**: “"created_at": "2026-10-04T15:30:00Z",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 5. 全栈通信协议与契约规范 (API Contracts)

### 5.1 RESTful HTTP 接口契约规范

#### 1. 模拟 Meta VM 发现鉴权：`GET /fetch_vms`

{==- **设计初衷**：完全兼容未修改的 Meta 固件（`muse_account_api.c` 会向 `FETCH_URL` 请求 VM 列表）。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **请求头**：`Authorization: Bearer <token>`（支持任意字符串或留空）。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **响应载荷**（HTTP 200 JSON）：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0119`)
> - **待复核原文**: “- **设计初衷**：完全兼容未修改的 Meta 固件（`muse_account_api.c` 会向 `FETCH_URL` 请求 VM 列表）。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0120`)
> - **待复核原文**: “- **请求头**：`Authorization: Bearer <token>`（支持任意字符串或留空）。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```json
{
  "vms": [
    {
      "id": "bailian-agent-01",
      {=="url": "wss://random-assigned-name.trycloudflare.com/v1/noise",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
      "state": "RUNNING",
      "region": "cn-hangzhou",
      {=="agent_type": "bailian_qwen_agent"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    }
  ]
}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0121`)
> - **待复核原文**: “"url": "wss://random-assigned-name.trycloudflare.com/v1/noise",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0122`)
> - **待复核原文**: “"agent_type": "bailian_qwen_agent"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 2. 流式语音转写：`POST /api/voice/dictation`

{==- **功能**：接收 StickS3 发送的 16kHz/24kHz PCM16 单声道音频数据流。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **请求头**：`Content-Type: audio/x-raw-pcm; rate=16000; format=s16le`。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **响应模式**：流式 NDJSON（分块逐行返回增量与最终结果）：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0123`)
> - **待复核原文**: “- **功能**：接收 StickS3 发送的 16kHz/24kHz PCM16 单声道音频数据流。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0124`)
> - **待复核原文**: “- **请求头**：`Content-Type: audio/x-raw-pcm; rate=16000; format=s16le`。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0125`)
> - **待复核原文**: “- **响应模式**：流式 NDJSON（分块逐行返回增量与最终结果）：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```json
{=={"type": "partial", "transcript": "灵方"}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{=={"type": "partial", "transcript": "灵方向前翻滚"}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{=={"type": "final", "transcript": "灵方向前翻滚一步并自锁电永磁。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}"}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0126`)
> - **待复核原文**: “{"type": "partial", "transcript": "灵方"}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0127`)
> - **待复核原文**: “{"type": "partial", "transcript": "灵方向前翻滚"}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0128`)
> - **待复核原文**: “{"type": "final", "transcript": "灵方向前翻滚一步并自锁电永磁。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 3. 消息交互流：`POST /chat/stream`

{==- **功能**：发送用户自然语言指令，触发百炼 Agent 思考、规划与工具调用。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **请求体**（JSON）：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0129`)
> - **待复核原文**: “- **功能**：发送用户自然语言指令，触发百炼 Agent 思考、规划与工具调用。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```json
{
  "message": "让灵方向前翻滚一步",
  {=="session_id": "session-sticks3-001",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  {=="device_id": "M5Stack-StickS3-C3B2"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0130`)
> - **待复核原文**: “"session_id": "session-sticks3-001",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0131`)
> - **待复核原文**: “"device_id": "M5Stack-StickS3-C3B2"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


{==- **响应体**（JSON）：`{"ack": true, "msg_id": "msg_98721", "status": "processing"}`。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0132`)
> - **待复核原文**: “- **响应体**（JSON）：`{"ack": true, "msg_id": "msg_98721", "status": "processing"}`。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 4. 对话增量事件订阅：`GET /chat/subscribe`

{==- **功能**：基于 Server-Sent Events (SSE) 持续下发大模型回复与具身动作状态。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **事件流示例**：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0133`)
> - **待复核原文**: “- **功能**：基于 Server-Sent Events (SSE) 持续下发大模型回复与具身动作状态。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```http
event: message_start
{==data: {"msg_id": "msg_98721", "role": "assistant"}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

event: text_append
data: {"delta": "收到指令，正在规划灵方"}

event: avatar_face
{==data: {"face": "thinking", "duration_ms": 1200}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

event: tool_call
{==data: {"tool": "lingcube_roll", "args": {"direction": "+X", "torque": 0.25}}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

event: text_append
data: {"delta": "。{==已驱动动量轮完成 +X 方向 90 度翻滚！==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}"}

event: avatar_face
{==data: {"face": "happy", "duration_ms": 3000}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

event: message_done
{==data: {"msg_id": "msg_98721", "total_bytes": 86}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0134`)
> - **待复核原文**: “data: {"msg_id": "msg_98721", "role": "assistant"}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0135`)
> - **待复核原文**: “data: {"face": "thinking", "duration_ms": 1200}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0136`)
> - **待复核原文**: “data: {"tool": "lingcube_roll", "args": {"direction": "+X", "torque": 0.25}}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0137`)
> - **待复核原文**: “已驱动动量轮完成 +X 方向 90 度翻滚！”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0138`)
> - **待复核原文**: “data: {"face": "happy", "duration_ms": 3000}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0139`)
> - **待复核原文**: “data: {"msg_id": "msg_98721", "total_bytes": 86}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

### 5.2 WebSocket 实时双工语音协议契约 (`/ws/v1/realtime`)

{==该接口对齐阿里云百炼 DashScope Realtime 协议规范，同时扩展 StickS3 的拟态微表情与硬件遥测事件通道。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0140`)
> - **待复核原文**: “该接口对齐阿里云百炼 DashScope Realtime 协议规范，同时扩展 StickS3 的拟态微表情与硬件遥测事件通道。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 客户端发往服务端 (Client -> Server) 报文规范

{==| 报文类型 (`type`) | 关键字段定义 | 说明 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
| :--- | :--- | :--- |
{==| `session.update` | `modalities`: `["audio", "text"]`<br/>`voice`: `"cherry"` / `"tina"`<br/>`turn_detection`: `{"type": "server_vad", "silence_duration_ms": 700}` | 初始化/更新会话参数与音色设置 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `input_audio_buffer.append` | `audio`: `"<base64_encoded_pcm16>"` (单切片 32ms~64ms) | 上行传输麦克风采集的 16kHz PCM 音频切片 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `input_audio_buffer.commit` | 无附加参数 | 物理按键松开时显式告知拾音结束 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `response.cancel` | 无附加参数 | **物理按键重新按下或检测到打断时发送**，立即中止云端当前播报与生成 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `device.telemetry` | `v_bus`: `3.85`, `battery_pct`: `82`, `btn_state`: `"RELEASED"` | 设备端周期性遥测健康上报 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0141`)
> - **待复核原文**: “| 报文类型 (`type`) | 关键字段定义 | 说明 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0142`)
> - **待复核原文**: “| `session.update` | `modalities`: `["audio", "text"]`<br/>`voice`: `"cherry"` / `"tina"`<br/>`turn_detection`: `{"type": "server_vad", "silence_duration_ms": 700}` | 初始化/更新会话参数与音色设置 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0143`)
> - **待复核原文**: “| `input_audio_buffer.append` | `audio`: `"<base64_encoded_pcm16>"` (单切片 32ms~64ms) | 上行传输麦克风采集的 16kHz PCM 音频切片 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0144`)
> - **待复核原文**: “| `input_audio_buffer.commit` | 无附加参数 | 物理按键松开时显式告知拾音结束 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0145`)
> - **待复核原文**: “| `response.cancel` | 无附加参数 | **物理按键重新按下或检测到打断时发送**，立即中止云端当前播报与生成 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0146`)
> - **待复核原文**: “| `device.telemetry` | `v_bus`: `3.85`, `battery_pct`: `82`, `btn_state`: `"RELEASED"` | 设备端周期性遥测健康上报 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 服务端发往客户端 (Server -> Client) 报文规范

{==| 报文类型 (`type`) | 关键字段定义 | 说明 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
| :--- | :--- | :--- |
{==| `session.created` | `session_id`: `"<uuid>"` | 会话创建成功确认 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `input_audio_buffer.speech_started` | `audio_start_ms`: `120` | Server-VAD 探测到用户开嗓，通知硬件切换表情为 `listening` |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `response.audio_transcript.delta` | `delta`: `"你好，灵伴在听。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{=="` | 文本增量字符，用于 StickS3 屏幕实时滚动显示字幕 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `response.audio.delta` | `delta`: `"<base64_encoded_pcm16>"` | 阿里云 CosyVoice 合成的 16kHz PCM 音频增量块，直推 I2S DAC 播报 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `avatar.expression` | `expression`: `"thinking"` / `"speaking"` / `"happy"` | 联动硬件 Avatar 状态机切换表情 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==| `response.done` | `response_id`: `"<uuid>"` | 当前轮次播报完毕，硬件重置为 `idle` 待机表情 |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0147`)
> - **待复核原文**: “| 报文类型 (`type`) | 关键字段定义 | 说明 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0148`)
> - **待复核原文**: “| `session.created` | `session_id`: `"<uuid>"` | 会话创建成功确认 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0149`)
> - **待复核原文**: “| `input_audio_buffer.speech_started` | `audio_start_ms`: `120` | Server-VAD 探测到用户开嗓，通知硬件切换表情为 `listening` |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0150`)
> - **待复核原文**: “| `response.audio_transcript.delta` | `delta`: `"你好，灵伴在听。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0151`)
> - **待复核原文**: “"` | 文本增量字符，用于 StickS3 屏幕实时滚动显示字幕 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0152`)
> - **待复核原文**: “| `response.audio.delta` | `delta`: `"<base64_encoded_pcm16>"` | 阿里云 CosyVoice 合成的 16kHz PCM 音频增量块，直推 I2S DAC 播报 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0153`)
> - **待复核原文**: “| `avatar.expression` | `expression`: `"thinking"` / `"speaking"` / `"happy"` | 联动硬件 Avatar 状态机切换表情 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0154`)
> - **待复核原文**: “| `response.done` | `response_id`: `"<uuid>"` | 当前轮次播报完毕，硬件重置为 `idle` 待机表情 |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

### 5.3 Serial Hatch 串口总线协议帧结构

{==串口总线协议复用并扩展 Meta 官方 Hatch 规范，波特率固定为 `115200 8-N-1`。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0155`)
> - **待复核原文**: “串口总线协议复用并扩展 Meta 官方 Hatch 规范，波特率固定为 `115200 8-N-1`。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 1. 主机下发指令 (Host -> Board)

{==- **文本连续分片**：`>chat+=<escaped_utf8_chunk>\n`（单包不超过 480 字节）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **文本终止发送**：`>chat=<final_escaped_utf8_chunk>\n`（触发固件合并并进入大模型调用）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **表情动态切换**：`>face=<face_name>\n`（例如 `>face=happy\n`、`>face=thinking\n`）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **具身动作直发**：`>robot={"action":"roll","direction":"+X"}\n`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **状态全量查询**：`>status\n`。
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0156`)
> - **待复核原文**: “- **文本连续分片**：`>chat+=<escaped_utf8_chunk>\n`（单包不超过 480 字节）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0157`)
> - **待复核原文**: “- **文本终止发送**：`>chat=<final_escaped_utf8_chunk>\n`（触发固件合并并进入大模型调用）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0158`)
> - **待复核原文**: “- **表情动态切换**：`>face=<face_name>\n`（例如 `>face=happy\n`、`>face=thinking\n`）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0159`)
> - **待复核原文**: “- **具身动作直发**：`>robot={"action":"roll","direction":"+X"}\n`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


#### 2. 硬件上行回传 (Board -> Host)

{==- **对话帧包装**：`@chat {"type": "text", "msg": 0, "text": "..."}\n`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **对话结束帧**：`@chat {"type": "message_done", "msg": 0, "bytes": 128}\n`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- **错误诊断帧**：`@chat {"type": "error", "text": "WIFI_DISCONNECTED"}\n`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **状态报告帧**：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0160`)
> - **待复核原文**: “- **对话帧包装**：`@chat {"type": "text", "msg": 0, "text": "..."}\n`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0161`)
> - **待复核原文**: “- **对话结束帧**：`@chat {"type": "message_done", "msg": 0, "bytes": 128}\n`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0162`)
> - **待复核原文**: “- **错误诊断帧**：`@chat {"type": "error", "text": "WIFI_DISCONNECTED"}\n`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```json
{==@status {"board": "M5Stack StickS3", "chat": true, "device": {"wifi": {"state": "connected", "mode": "WiFi", "ip": "192.168.110.67"}, "hatch": {"state": "connected"}, "v_bus": 3.84, "fps": 97.5}}==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0163`)
> - **待复核原文**: “@status {"board": "M5Stack StickS3", "chat": true, "device": {"wifi": {"state": "connected", "mode": "WiFi", "ip": "192.168.110.67"}, "hatch": {"state": "connected"}, "v_bus": 3.84, "fps": 97.5}}”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

### 5.4 Device Skills 具身工具声明规范 (OpenAI / DashScope 兼容 JSON Schema)

{==大模型根据自然语言意图自主调用以下工具，控制物理灵方机器人或数字孪生仿真：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0164`)
> - **待复核原文**: “大模型根据自然语言意图自主调用以下工具，控制物理灵方机器人或数字孪生仿真：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```json
[
  {
    "type": "function",
    "function": {
      "name": "lingcube_roll",
      {=="description": "驱动灵方(LingCube)微型机器人动量轮急刹，在桌面上完成指定方向的90度脉冲翻滚运动。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}",
      "parameters": {
        "type": "object",
        "properties": {
          "direction": {
            "type": "string",
            {=="enum": ["+X", "-X", "+Y", "-Y"],==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            {=="description": "翻滚方向：+X为向前，-X为向后，+Y为向左，-Y为向右"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
          },
          "torque": {
            "type": "number",
            "default": 0.25,
            {=="description": "动量轮制动峰值扭矩(N·m)，默认为0.25N·m足以越过45度重力势垒"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
          },
          "duration_s": {
            "type": "number",
            "default": 0.35,
            {=="description": "动量轮加减速脉冲持续时间(秒)"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
          }
        },
        "required": ["direction"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "lingcube_epm_latch",
      {=="description": "控制灵方机器人指定端面的双稳态电永磁(EPM)线圈充退磁脉冲，实现35N+强力自锁吸附或瞬间消磁释放。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}",
      "parameters": {
        "type": "object",
        "properties": {
          "face_id": {
            "type": "integer",
            "minimum": 1,
            "maximum": 6,
            {=="description": "灵方的六个端面编号(1到6)"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
          },
          "state": {
            "type": "string",
            "enum": ["LATCH", "RELEASE"],
            {=="description": "LATCH为充磁自锁(产生35N吸力且稳态零功耗)；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}RELEASE为消磁释放"
          },
          "pulse_duration_ms": {
            "type": "integer",
            "default": 20,
            {=="description": "充退磁放电脉冲时间(毫秒)，物理看门狗严格限制在50ms以内"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
          }
        },
        {=="required": ["face_id", "state"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
      }
    }
  },
  {
    "type": "function",
    "function": {
      {=="name": "lingcube_set_morphology",==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
      {=="description": "调度微型自重构机器人集群形态拓扑协议，组装为灵链、灵环、灵席或双足灵步构型。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}",
      "parameters": {
        "type": "object",
        "properties": {
          "morphology": {
            "type": "string",
            {=="enum": ["LingCube", "LingChain", "LingRing", "LingSheet", "LingWalker", "LingSwarm"],==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            "description": "目标自重构拓扑形态名称"
          }
        },
        "required": ["morphology"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "sticks3_set_avatar",
      {=="description": "动态改变 StickS3 屏幕上伴侣 Avatar 的拟态表情与情绪状态。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}",
      "parameters": {
        "type": "object",
        "properties": {
          "expression": {
            "type": "string",
            {=="enum": ["idle", "listening", "speaking", "thinking", "happy", "pet", "feed", "sleep", "error"],==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
            "description": "目标微表情"
          },
          "hold_duration_ms": {
            "type": "integer",
            "default": 3000,
            "description": "该表情持续保持的最少毫秒数"
          }
        },
        "required": ["expression"]
      }
    }
  }
]
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0165`)
> - **待复核原文**: “"description": "驱动灵方(LingCube)微型机器人动量轮急刹，在桌面上完成指定方向的90度脉冲翻滚运动。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0166`)
> - **待复核原文**: “"enum": ["+X", "-X", "+Y", "-Y"],”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0167`)
> - **待复核原文**: “"description": "翻滚方向：+X为向前，-X为向后，+Y为向左，-Y为向右"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0168`)
> - **待复核原文**: “"description": "动量轮制动峰值扭矩(N·m)，默认为0.25N·m足以越过45度重力势垒"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0169`)
> - **待复核原文**: “"description": "动量轮加减速脉冲持续时间(秒)"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0170`)
> - **待复核原文**: “"description": "控制灵方机器人指定端面的双稳态电永磁(EPM)线圈充退磁脉冲，实现35N+强力自锁吸附或瞬间消磁释放。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0171`)
> - **待复核原文**: “"description": "灵方的六个端面编号(1到6)"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0172`)
> - **待复核原文**: “"description": "LATCH为充磁自锁(产生35N吸力且稳态零功耗)；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0173`)
> - **待复核原文**: “"description": "充退磁放电脉冲时间(毫秒)，物理看门狗严格限制在50ms以内"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0174`)
> - **待复核原文**: “"required": ["face_id", "state"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0175`)
> - **待复核原文**: “"name": "lingcube_set_morphology",”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0176`)
> - **待复核原文**: “"description": "调度微型自重构机器人集群形态拓扑协议，组装为灵链、灵环、灵席或双足灵步构型。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0177`)
> - **待复核原文**: “"enum": ["LingCube", "LingChain", "LingRing", "LingSheet", "LingWalker", "LingSwarm"],”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0178`)
> - **待复核原文**: “"description": "动态改变 StickS3 屏幕上伴侣 Avatar 的拟态表情与情绪状态。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0179`)
> - **待复核原文**: “"enum": ["idle", "listening", "speaking", "thinking", "happy", "pet", "feed", "sleep", "error"],”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 6. M5Stack StickS3 物理设备适配与六大工程公理贯彻

{==在改造与适配 M5Stack StickS3 物理固件（`firmware/m5sticks3_buddy/`）时，**绝不允许破坏已有的核心特性与系统稳定性**。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==必须百分之百贯彻落实 `docs/30_PROJECT_AXIOMS_AND_HANDOVER.md` 确立的最高工程公理：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0180`)
> - **待复核原文**: “在改造与适配 M5Stack StickS3 物理固件（`firmware/m5sticks3_buddy/`）时，**绝不允许破坏已有的核心特性与系统稳定性**。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0181`)
> - **待复核原文**: “必须百分之百贯彻落实 `docs/30_PROJECT_AXIOMS_AND_HANDOVER.md` 确立的最高工程公理：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
graph TD
    subgraph Axioms["六大不可违背工程公理"]
        {==A1["公理一: 固件修改必烧必启<br/>COM3 烧录 / RTS/DTR 硬重启 / 15s 诊断"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==A2["公理二: 中断通讯异步解耦<br/>BTC_TASK / ISR 栈深 < 32B，loopTask 消费"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==A3["公理三: 显存零撕裂双缓冲<br/>8MB PSRAM Sprite 离线合成，单次 DMA 推送"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==A4["公理四: 网络显式区分一致<br/>HOT 橙底 / WiFi 绿底 / !NET 红底"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==A5["公理五: 零功能回退渐进加固<br/>悄悄离线词 / 按键打断 / 12微表情 / I2C互斥"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
        {==A6["公理六: 自适应防截断编码<br/>safeTruncateUtf8 规避 WS 1007 协议崩溃"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    end
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0182`)
> - **待复核原文**: “A1["公理一: 固件修改必烧必启<br/>COM3 烧录 / RTS/DTR 硬重启 / 15s 诊断"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0183`)
> - **待复核原文**: “A2["公理二: 中断通讯异步解耦<br/>BTC_TASK / ISR 栈深 < 32B，loopTask 消费"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0184`)
> - **待复核原文**: “A3["公理三: 显存零撕裂双缓冲<br/>8MB PSRAM Sprite 离线合成，单次 DMA 推送"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0185`)
> - **待复核原文**: “A4["公理四: 网络显式区分一致<br/>HOT 橙底 / WiFi 绿底 / !NET 红底"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0186`)
> - **待复核原文**: “A5["公理五: 零功能回退渐进加固<br/>悄悄离线词 / 按键打断 / 12微表情 / I2C互斥"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0187`)
> - **待复核原文**: “A6["公理六: 自适应防截断编码<br/>safeTruncateUtf8 规避 WS 1007 协议崩溃"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 6.1 显存零撕裂双缓冲物理公理 (贯彻公理三)

{==- **底层物理冲突**：StickS3 屏幕为 135x240 ST7789 LCD，SPI 总线（SPI3_HOST）工作在 40MHz。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==若直接调用 `display.fillRect()` 或分步绘制眼睛、瞳孔、汉字，人眼会观测到剧烈的 15Hz 物理闪烁与水平撕裂。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **PSRAM 显存架构**：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0188`)
> - **待复核原文**: “- **底层物理冲突**：StickS3 屏幕为 135x240 ST7789 LCD，SPI 总线（SPI3_HOST）工作在 40MHz。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0189`)
> - **待复核原文**: “若直接调用 `display.fillRect()` 或分步绘制眼睛、瞳孔、汉字，人眼会观测到剧烈的 15Hz 物理闪烁与水平撕裂。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


  ```cpp
  {==// 在 8MB PSRAM 中开辟双缓冲精灵画布 (仅消耗 64.8KB PSRAM)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  {==static LGFX_Sprite canvas(&display);==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  canvas.setPsram(true);
  canvas.createSprite(135, 240);
  {==canvas.setColorDepth(16); // 16-bit RGB565==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  ```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0190`)
> - **待复核原文**: “// 在 8MB PSRAM 中开辟双缓冲精灵画布 (仅消耗 64.8KB PSRAM)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0191`)
> - **待复核原文**: “static LGFX_Sprite canvas(&display);”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0192`)
> - **待复核原文**: “canvas.setColorDepth(16); // 16-bit RGB565”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


- **离线合成与原子推送流水线**：
  1. 在 `canvas` 离线显存中清屏；
  2. 绘制迪士尼矢量瞳孔（平滑微动与眨眼插值）；
  3. 绘制平滑贝塞尔拟态嘴型（随语音振幅动态张合）；
  4. 渲染多行排版中文汉字字幕（点阵字体引擎）；
  5. {==绘制顶部网络徽章（HOT / WiFi / !NET）与电池姿态水准仪；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  6. {==周期末尾调用 `canvas.pushSprite(0, 0)`，经 SPI DMA **单次原子性全量推送**至物理屏幕。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==实测帧率稳定在 **96.8 ~ 98.9 FPS**，完全消除频闪。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0193`)
> - **待复核原文**: “绘制顶部网络徽章（HOT / WiFi / !NET）与电池姿态水准仪；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0194`)
> - **待复核原文**: “周期末尾调用 `canvas.pushSprite(0, 0)`，经 SPI DMA **单次原子性全量推送**至物理屏幕。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0195`)
> - **待复核原文**: “实测帧率稳定在 **96.8 ~ 98.9 FPS**，完全消除频闪。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 6.2 中断与通信协议栈异步解耦公理 (贯彻公理二)

{==- **底层致命隐患**：Bluedroid 蓝牙控制协议栈任务 `BTC_TASK` 仅分配约 3KB 堆栈；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==USB 串口中断和 Wi-Fi 回调同样运行于中断/内核级上下文。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==若在这些回调中直接进行 JSON 反序列化、NVS Flash 写入或网络发起，会导致致命的 `Stack Overflow Panic`。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- **解耦设计**：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0196`)
> - **待复核原文**: “- **底层致命隐患**：Bluedroid 蓝牙控制协议栈任务 `BTC_TASK` 仅分配约 3KB 堆栈；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0197`)
> - **待复核原文**: “USB 串口中断和 Wi-Fi 回调同样运行于中断/内核级上下文。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0198`)
> - **待复核原文**: “若在这些回调中直接进行 JSON 反序列化、NVS Flash 写入或网络发起，会导致致命的 `Stack Overflow Panic`。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


  ```cpp
  {==// 仅在自旋锁临界区内向静态微队列存入原始字节 (栈开销 < 32 字节)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  {==portENTER_CRITICAL_ISR(&_rx_mux);==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  _rx_queue.push(incoming_byte);
  {==portEXIT_CRITICAL_ISR(&_rx_mux);==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  ```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0199`)
> - **待复核原文**: “// 仅在自旋锁临界区内向静态微队列存入原始字节 (栈开销 < 32 字节)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0200`)
> - **待复核原文**: “portENTER_CRITICAL_ISR(&_rx_mux);”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0201`)
> - **待复核原文**: “portEXIT_CRITICAL_ISR(&_rx_mux);”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


{==- **主线程消费**：在拥有 **16KB+ 充裕堆栈** 的 `loopTask` 中调用 `StickS3BLESync::getInstance().update()` 与 `MuseConsoleParser::parseLine()`，完成指令反序列化与状态机流转。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0202`)
> - **待复核原文**: “- **主线程消费**：在拥有 **16KB+ 充裕堆栈** 的 `loopTask` 中调用 `StickS3BLESync::getInstance().update()` 与 `MuseConsoleParser::parseLine()`，完成指令反序列化与状态机流转。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 6.3 语音/文本双通道与毫秒级打断 (Barge-In) 设计 (贯彻公理五)

{==StickS3 配备原生 ES8311 音频编解码芯片与 AW8737 功放，支持全双工语音回环。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}系统设计双重打断保障机制：
1. **硬件物理打断（Hardware Barge-In）**：
   - 用户在伴侣发声说话期间，短按正面主按键（KEY1 / Button A, GPIO 11）；
   {==- 固件立即执行：停止当前 I2S DMA 音频播放缓冲区、向百炼 WebSocket 发送 `{"type": "response.cancel"}`、将 Avatar 表情切为 `listening`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
   - 响应延迟 `< 15ms`，带来极其清脆爽快的打断手感。
2. **声学与服务端打断（Server-VAD Barge-In）**：
   - 当百炼 Realtime API 监测到用户语音输入能量超过阈值，下发 `input_audio_buffer.speech_started`；
   - StickS3 自动静音扬声器，避免回音自激与自听自答。
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0203`)
> - **待复核原文**: “StickS3 配备原生 ES8311 音频编解码芯片与 AW8737 功放，支持全双工语音回环。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0204`)
> - **待复核原文**: “**硬件物理打断（Hardware Barge-In）**： - 用户在伴侣发声说话期间，短按正面主按键（KEY1 / Button A, GPIO 11）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0205`)
> - **待复核原文**: “- 固件立即执行：停止当前 I2S DMA 音频播放缓冲区、向百炼 WebSocket 发送 `{"type": "response.cancel"}`、将 Avatar 表情切为 `listening`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0206`)
> - **待复核原文**: “**声学与服务端打断（Server-VAD Barge-In）**： - 当百炼 Realtime API 监测到用户语音输入能量超过阈值，下发 `input_audio_buffer.speech_started`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### 6.4 跨端自适应协议与防截断编码 (贯彻公理六)

{==- **UTF-8 字符边界对齐**：长文本或大模型回复分包时，禁止使用朴素的字节 slice。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==固件与 Agent 端统一采用 `safeTruncateUtf8` 算法，严格沿 1~4 字节合法 Unicode 边界切分，防止断字半字符引发的 `cJSON_Parse` 失败或 WebSocket RFC 6455 1007 错误。==}{>>[QUESTIONABLE] [MINOR] 依据: https://www.rfc-editor.org/rfc/rfc6455.html | 【出处核验差异】RFC 6455 format is valid, requires live query against IETF index.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0207`)
> - **待复核原文**: “- **UTF-8 字符边界对齐**：长文本或大模型回复分包时，禁止使用朴素的字节 slice。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0208`)
> - **待复核原文**: “固件与 Agent 端统一采用 `safeTruncateUtf8` 算法，严格沿 1~4 字节合法 Unicode 边界切分，防止断字半字符引发的 `cJSON_Parse` 失败或 WebSocket RFC 6455 1007 错误。”
> - **公理与事实推导**: 【出处核验差异】RFC 6455 format is valid, requires live query against IETF index.
> - **可验证出处与来源**: https://www.rfc-editor.org/rfc/rfc6455.html


---

## 7. 具身协同端到端交互序列设计 (Interaction Sequences)

### 7.1 场景 A：Push-to-Talk 语音控制具身翻滚全流程

{==用户按住 StickS3 按键说出：*“灵方向前翻滚一步，并锁紧2号面电永磁”*。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0209`)
> - **待复核原文**: “用户按住 StickS3 按键说出：*“灵方向前翻滚一步，并锁紧2号面电永磁”*。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
sequenceDiagram
    autonumber
    actor User as 用户
    {==participant Stick as StickS3 (LingBuddy)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==participant Agent as BailianMuseCloudAgent==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==participant Bailian as 阿里云百炼 (Realtime/Qwen)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==participant Cube as 灵方 (LingCube MSRR)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

    {==User->>Stick: 按住 KEY1 (Push-to-Talk)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Stick->>Stick: Avatar 切换为 listening (蓝色微动瞳孔)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Stick->>Agent: WebSocket 上行 input_audio_buffer.append (16kHz PCM)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Agent->>Bailian: 转发 16kHz PCM 音频切片==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    User->>Stick: 松开 KEY1 按键
    {==Stick->>Agent: 发送 input_audio_buffer.commit==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Stick->>Stick: Avatar 切换为 thinking (琥珀色螺旋律动)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==Bailian->>Agent: Paraformer ASR 转写: "灵方向前翻滚一步，并锁紧2号面电永磁"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Bailian->>Bailian: Qwen2.5 意图理解，触发 Function Calling:==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    Note over Bailian: 1. {==lingcube_roll(direction="+X")<br/>2.==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} {==lingcube_epm_latch(face_id=2, state="LATCH")==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==Bailian->>Agent: 下发 Tool Call: lingcube_roll("+X")==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Agent->>Agent: 检查灵方母线电压 (V_bus >= 3.30V?==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} OK)
    {==Agent->>Cube: HTTP POST /api/robot/roll ({"direction": "+X"})==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Cube->>Cube: 动量轮急刹反扭矩冲量释放，完成 90° 翻滚==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Cube-->>Agent: HTTP 200 OK ({"roll_deg": 90.0})==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==Bailian->>Agent: 下发 Tool Call: lingcube_epm_latch(2, "LATCH")==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Agent->>Agent: 检查 EPM 冷却时间窗 (距上次脉冲 > 100ms?==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} OK)
    {==Agent->>Cube: HTTP POST /api/robot/epm ({"face_id": 2, "state": "LATCH"})==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Cube->>Cube: 2号面电永磁线圈 20ms 脉冲充磁自锁 (35N+)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Cube-->>Agent: HTTP 200 OK ({"face_2_latch": true})==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==Agent-->>Bailian: 上报 Tool Output (动作均成功完成)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Bailian->>Agent: 下发 CosyVoice 流式语音 PCM + 增量字幕: "灵方已完成向前翻滚与2号面强力磁吸！==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}"
    {==Agent->>Stick: WebSocket 下发 response.audio.delta + avatar.expression ("speaking")==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Stick->>Stick: Avatar 嘴型随振幅拟态开合，I2S 播报高拟真语音==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    Stick->>User: 视听双感知闭环反馈
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0210`)
> - **待复核原文**: “participant Stick as StickS3 (LingBuddy)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0211`)
> - **待复核原文**: “participant Agent as BailianMuseCloudAgent”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0212`)
> - **待复核原文**: “participant Bailian as 阿里云百炼 (Realtime/Qwen)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0213`)
> - **待复核原文**: “participant Cube as 灵方 (LingCube MSRR)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0214`)
> - **待复核原文**: “User->>Stick: 按住 KEY1 (Push-to-Talk)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0215`)
> - **待复核原文**: “Stick->>Stick: Avatar 切换为 listening (蓝色微动瞳孔)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0216`)
> - **待复核原文**: “Stick->>Agent: WebSocket 上行 input_audio_buffer.append (16kHz PCM)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0217`)
> - **待复核原文**: “Agent->>Bailian: 转发 16kHz PCM 音频切片”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0218`)
> - **待复核原文**: “Stick->>Agent: 发送 input_audio_buffer.commit”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0219`)
> - **待复核原文**: “Stick->>Stick: Avatar 切换为 thinking (琥珀色螺旋律动)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0220`)
> - **待复核原文**: “Bailian->>Agent: Paraformer ASR 转写: "灵方向前翻滚一步，并锁紧2号面电永磁"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0221`)
> - **待复核原文**: “Bailian->>Bailian: Qwen2.5 意图理解，触发 Function Calling:”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0222`)
> - **待复核原文**: “lingcube_roll(direction="+X")<br/>2.”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0223`)
> - **待复核原文**: “lingcube_epm_latch(face_id=2, state="LATCH")”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0224`)
> - **待复核原文**: “Bailian->>Agent: 下发 Tool Call: lingcube_roll("+X")”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0225`)
> - **待复核原文**: “Agent->>Agent: 检查灵方母线电压 (V_bus >= 3.30V?”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0226`)
> - **待复核原文**: “Agent->>Cube: HTTP POST /api/robot/roll ({"direction": "+X"})”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0227`)
> - **待复核原文**: “Cube->>Cube: 动量轮急刹反扭矩冲量释放，完成 90° 翻滚”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0228`)
> - **待复核原文**: “Cube-->>Agent: HTTP 200 OK ({"roll_deg": 90.0})”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0229`)
> - **待复核原文**: “Bailian->>Agent: 下发 Tool Call: lingcube_epm_latch(2, "LATCH")”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0230`)
> - **待复核原文**: “Agent->>Agent: 检查 EPM 冷却时间窗 (距上次脉冲 > 100ms?”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0231`)
> - **待复核原文**: “Agent->>Cube: HTTP POST /api/robot/epm ({"face_id": 2, "state": "LATCH"})”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0232`)
> - **待复核原文**: “Cube->>Cube: 2号面电永磁线圈 20ms 脉冲充磁自锁 (35N+)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0233`)
> - **待复核原文**: “Cube-->>Agent: HTTP 200 OK ({"face_2_latch": true})”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0234`)
> - **待复核原文**: “Agent-->>Bailian: 上报 Tool Output (动作均成功完成)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0235`)
> - **待复核原文**: “Bailian->>Agent: 下发 CosyVoice 流式语音 PCM + 增量字幕: "灵方已完成向前翻滚与2号面强力磁吸！”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0236`)
> - **待复核原文**: “Agent->>Stick: WebSocket 下发 response.audio.delta + avatar.expression ("speaking")”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0237`)
> - **待复核原文**: “Stick->>Stick: Avatar 嘴型随振幅拟态开合，I2S 播报高拟真语音”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

### 7.2 场景 B：USB 串口 Hatch 控制与状态诊断

{==开发者在宿主机运行串口终端或调试脚本通过 `COM3` 控制 StickS3。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0238`)
> - **待复核原文**: “开发者在宿主机运行串口终端或调试脚本通过 `COM3` 控制 StickS3。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


```mermaid
sequenceDiagram
    autonumber
    actor Dev as 开发者 / 宿主脚本
    {==participant Port as 本地串口 (COM3, 115200)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==participant Parser as StickS3 (MuseConsoleParser)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==participant Canvas as PSRAM 显存 (LGFX_Sprite)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==participant Display as ST7789 物理屏幕==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}

    {==Dev->>Port: 发送 ">face=happy\n"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Port->>Parser: 硬件 UART 中断接收，写入 _rx_queue==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Parser->>Parser: loopTask 异步消费，解析为 FACE_SET("happy")==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Parser->>Canvas: 触发 AvatarState::HAPPY (星眸眯眼拟态)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Canvas->>Display: DMA 原子推送 (0 闪烁，0 撕裂)==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    {==Dev->>Port: 发送 ">chat+=灵方机器人\n"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Parser->>Parser: 累积分包文本: "灵方机器人"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Dev->>Port: 发送 ">chat=已就绪\n"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Parser->>Parser: 拼接完整消息: "灵方机器人已就绪"==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==Parser->>Port: 格式化回传: '@chat {"type": "sent", "bytes": 21}\n'==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    
    Dev->>Port: 发送 ">status\n"
    {==Parser->>Port: 回传 '@status {"board":"M5Stack StickS3","chat":true,"device":{"wifi":{"state":"connected","mode":"WiFi"},"fps":98.2}}\n'==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0239`)
> - **待复核原文**: “participant Port as 本地串口 (COM3, 115200)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0240`)
> - **待复核原文**: “participant Parser as StickS3 (MuseConsoleParser)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0241`)
> - **待复核原文**: “participant Canvas as PSRAM 显存 (LGFX_Sprite)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0242`)
> - **待复核原文**: “participant Display as ST7789 物理屏幕”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0243`)
> - **待复核原文**: “Dev->>Port: 发送 ">face=happy\n"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0244`)
> - **待复核原文**: “Port->>Parser: 硬件 UART 中断接收，写入 _rx_queue”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0245`)
> - **待复核原文**: “Parser->>Parser: loopTask 异步消费，解析为 FACE_SET("happy")”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0246`)
> - **待复核原文**: “Parser->>Canvas: 触发 AvatarState::HAPPY (星眸眯眼拟态)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0247`)
> - **待复核原文**: “Canvas->>Display: DMA 原子推送 (0 闪烁，0 撕裂)”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0248`)
> - **待复核原文**: “Dev->>Port: 发送 ">chat+=灵方机器人\n"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0249`)
> - **待复核原文**: “Parser->>Parser: 累积分包文本: "灵方机器人"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0250`)
> - **待复核原文**: “Dev->>Port: 发送 ">chat=已就绪\n"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0251`)
> - **待复核原文**: “Parser->>Parser: 拼接完整消息: "灵方机器人已就绪"”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0252`)
> - **待复核原文**: “Parser->>Port: 格式化回传: '@chat {"type": "sent", "bytes": 21}\n'”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0253`)
> - **待复核原文**: “Parser->>Port: 回传 '@status {"board":"M5Stack StickS3","chat":true,"device":{"wifi":{"state":"connected","mode":"WiFi"},"fps":98.2}}\n'”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 8. 墨菲定律防御与 FMEA 安全失效对策表

{==在将大模型与真实物理硬件、动力电机与强磁线圈连接时，系统必须具备工业级防御裕度，防止不可逆硬件损坏：==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0254`)
> - **待复核原文**: “在将大模型与真实物理硬件、动力电机与强磁线圈连接时，系统必须具备工业级防御裕度，防止不可逆硬件损坏：”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


{==| 故障失效模式 (Failure Mode) | 诱发根本原因 (Root Cause) | 严重度 (Severity) | 固件与 Agent 端防御对策与设计裕度 (Mitigation) |==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
| :--- | :--- | :---: | :--- |
{==| **母线跌落与棕变死机 (Brownout Reset)** | 动量轮急刹瞬态大电流或电芯内阻压降导致轨压跌破 3.20V | **Catastrophic (灾难性)** | **固件与 Agent 双重电压互锁**：硬件 TPS63805 Buck-Boost 稳压；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==固件与 Agent 在执行动量轮翻滚前检测 $V_{\text{bus}}$，若 $< 3.30\text{V}$ 立即拒绝做工，保护 CPU 与 NVS 不损坏。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
{==| **EPM 电永磁线圈过热烧毁** | 大模型陷入死循环或外部连续快速下发磁吸充磁指令 | **Critical (严重损坏)** | **硬件微分限幅 + 软件强制冷却窗**：硬件放电端配置 RC 微分电路限制最长导通 50ms；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==固件层与 Agent 设置 `100ms` 最小强制冷却窗，100ms 内拒绝连续脉冲。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
{==| **BLE/串口中断堆栈溢出 Panic** | 在底层蓝牙/串口回调中执行 JSON 解析或 NVS 写入（`BTC_TASK` 仅 3KB） | **Catastrophic (系统崩溃)** | **贯彻公理二**：中断仅在自旋锁内压入微队列（`< 32B` 栈），在 16KB 堆栈的 `loopTask` 中异步反序列化并调度。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
{==| **公网穿透断开导致脑裂重复执行** | 移动网络抖动导致 WebSocket/HTTP 连接断开，Agent 重试超时 | **Moderate (中度混乱)** | **幂等性请求指纹（req_id）**：所有动作指令携带唯一 `req_id`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}{==机器人本地维护最近 16 笔指令环形执行队列，重复 `req_id` 仅返回历史结果，不重复施加机械动作。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
{==| **屏幕物理撕裂与背光频闪** | 切换微表情时直接调用物理 LCD 控件或逐步清屏 | **Minor (体验劣化)** | **贯彻公理三**：开辟 64.8KB PSRAM Sprite 画布离线全量合成，通过 SPI DMA 单次原子写入，从物理上杜绝 15Hz 视觉闪烁。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
{==| **Unicode 断字引发协议崩溃** | 字符串分片或截断粗暴使用字节切片，破坏 UTF-8 变长字节结构 | **High (连接阻断)** | **贯彻公理六**：全栈统一使用 `safeTruncateUtf8` 算法，沿 1~4 字节合法字符边界截断，彻底避免 WebSocket 1007 协议违规。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
{==| **I2C 总线传感器争用死锁** | 音频 Codec、姿态传感器 BMI270 与 PMIC 跨 FreeRTOS 任务并发访问 I2C | **Critical (总线锁死)** | **贯彻公理五**：全局 I2C 互斥锁 `g_i2c_mutex` 严密保护每次通信事务，事务耗时超时强制释放，零总线死锁。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<} |
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0255`)
> - **待复核原文**: “| 故障失效模式 (Failure Mode) | 诱发根本原因 (Root Cause) | 严重度 (Severity) | 固件与 Agent 端防御对策与设计裕度 (Mitigation) |”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0256`)
> - **待复核原文**: “| **母线跌落与棕变死机 (Brownout Reset)** | 动量轮急刹瞬态大电流或电芯内阻压降导致轨压跌破 3.20V | **Catastrophic (灾难性)** | **固件与 Agent 双重电压互锁**：硬件 TPS63805 Buck-Boost 稳压；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0257`)
> - **待复核原文**: “固件与 Agent 在执行动量轮翻滚前检测 $V_{\text{bus}}$，若 $< 3.30\text{V}$ 立即拒绝做工，保护 CPU 与 NVS 不损坏。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0258`)
> - **待复核原文**: “| **EPM 电永磁线圈过热烧毁** | 大模型陷入死循环或外部连续快速下发磁吸充磁指令 | **Critical (严重损坏)** | **硬件微分限幅 + 软件强制冷却窗**：硬件放电端配置 RC 微分电路限制最长导通 50ms；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0259`)
> - **待复核原文**: “固件层与 Agent 设置 `100ms` 最小强制冷却窗，100ms 内拒绝连续脉冲。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0260`)
> - **待复核原文**: “| **BLE/串口中断堆栈溢出 Panic** | 在底层蓝牙/串口回调中执行 JSON 解析或 NVS 写入（`BTC_TASK` 仅 3KB） | **Catastrophic (系统崩溃)** | **贯彻公理二**：中断仅在自旋锁内压入微队列（`< 32B` 栈），在 16KB 堆栈的 `loopTask` 中异步反序列化并调度。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0261`)
> - **待复核原文**: “| **公网穿透断开导致脑裂重复执行** | 移动网络抖动导致 WebSocket/HTTP 连接断开，Agent 重试超时 | **Moderate (中度混乱)** | **幂等性请求指纹（req_id）**：所有动作指令携带唯一 `req_id`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0262`)
> - **待复核原文**: “机器人本地维护最近 16 笔指令环形执行队列，重复 `req_id` 仅返回历史结果，不重复施加机械动作。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0263`)
> - **待复核原文**: “| **屏幕物理撕裂与背光频闪** | 切换微表情时直接调用物理 LCD 控件或逐步清屏 | **Minor (体验劣化)** | **贯彻公理三**：开辟 64.8KB PSRAM Sprite 画布离线全量合成，通过 SPI DMA 单次原子写入，从物理上杜绝 15Hz 视觉闪烁。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0264`)
> - **待复核原文**: “| **Unicode 断字引发协议崩溃** | 字符串分片或截断粗暴使用字节切片，破坏 UTF-8 变长字节结构 | **High (连接阻断)** | **贯彻公理六**：全栈统一使用 `safeTruncateUtf8` 算法，沿 1~4 字节合法字符边界截断，彻底避免 WebSocket 1007 协议违规。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0265`)
> - **待复核原文**: “| **I2C 总线传感器争用死锁** | 音频 Codec、姿态传感器 BMI270 与 PMIC 跨 FreeRTOS 任务并发访问 I2C | **Critical (总线锁死)** | **贯彻公理五**：全局 I2C 互斥锁 `g_i2c_mutex` 严密保护每次通信事务，事务耗时超时强制释放，零总线死锁。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


---

## 9. 分阶段工程落地路线图 (Phase 1 ~ Phase 5)

```mermaid
flowchart LR
    {==P1["Phase 1: 架构设计与契约编制<br/>(当前阶段: Doc 32)"] --> P2["Phase 2: Cloud Agent 核心开发<br/>(BailianMuseCloudAgent & 测试)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==P2 --> P3["Phase 3: 固件协议栈升级<br/>(StickS3 混合模式 & COM3 烧录)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==P3 --> P4["Phase 4: 公网穿透与自适应端点<br/>(public-service-tunnel 联调)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
    {==P4 --> P5["Phase 5: 具身协同闭环验收<br/>(灵方+灵伴+百炼实机长跑)"]==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0266`)
> - **待复核原文**: “P1["Phase 1: 架构设计与契约编制<br/>(当前阶段: Doc 32)"] --> P2["Phase 2: Cloud Agent 核心开发<br/>(BailianMuseCloudAgent & 测试)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0267`)
> - **待复核原文**: “P2 --> P3["Phase 3: 固件协议栈升级<br/>(StickS3 混合模式 & COM3 烧录)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0268`)
> - **待复核原文**: “P3 --> P4["Phase 4: 公网穿透与自适应端点<br/>(public-service-tunnel 联调)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0269`)
> - **待复核原文**: “P4 --> P5["Phase 5: 具身协同闭环验收<br/>(灵方+灵伴+百炼实机长跑)"]”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### Phase 1：架构分析、百炼替代方案设计与标准契约编制（已达成）

{==- [x] 深入剖析 `external_repos/muse-gadget-sdk/esp32/` 与 `docs/31` 的架构细节；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [x] 完成阿里云百炼大模型矩阵（Qwen2.5 + DashScope Realtime + CosyVoice）平替设计；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [x] 制定 `BailianMuseCloudAgent` 本地服务架构与四向桥接设计（REST、WS、Serial Hatch、Skills）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [x] 制定集成 `public-service-tunnel` 的免登录公网 HTTPS 穿透与端点持久化策略；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [x] 制定 M5Stack StickS3 物理设备改造细节与六大工程公理贯彻规范；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [x] 编写并发布完整的系统架构设计文档：`docs/32_Meta_Muse_开源硬件阿里云百炼大模型适配与公网Agent实施方案.md`。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0270`)
> - **待复核原文**: “- [x] 深入剖析 `external_repos/muse-gadget-sdk/esp32/` 与 `docs/31` 的架构细节；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0271`)
> - **待复核原文**: “- [x] 完成阿里云百炼大模型矩阵（Qwen2.5 + DashScope Realtime + CosyVoice）平替设计；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0272`)
> - **待复核原文**: “- [x] 制定 `BailianMuseCloudAgent` 本地服务架构与四向桥接设计（REST、WS、Serial Hatch、Skills）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0273`)
> - **待复核原文**: “- [x] 制定集成 `public-service-tunnel` 的免登录公网 HTTPS 穿透与端点持久化策略；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0274`)
> - **待复核原文**: “- [x] 制定 M5Stack StickS3 物理设备改造细节与六大工程公理贯彻规范；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0275`)
> - **待复核原文**: “- [x] 编写并发布完整的系统架构设计文档：`docs/32_Meta_Muse_开源硬件阿里云百炼大模型适配与公网Agent实施方案.md`。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### Phase 2：BailianMuseCloudAgent 服务开发与单元测试验证

{==- [ ] 在 `simulation/bridge/` 或 `services/` 目录下实现 `bailian_muse_cloud_agent.py`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 实现兼容 Meta 契约的 FastAPI 路由（`/fetch_vms`, `/api/voice/dictation`, `/chat/stream`, `/chat/subscribe`）；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 集成 DashScope Realtime WebSocket 客户端与音频 PCM 转码器；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 挂载 `skills/gadget-lingcube-msrr` 与 `skills/gadget-lingmatrix-sim` 工具注册表；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 编写覆盖 100% 关键路径的自动化单元测试（`tests/test_bailian_muse_cloud_agent.py`）。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0276`)
> - **待复核原文**: “- [ ] 在 `simulation/bridge/` 或 `services/` 目录下实现 `bailian_muse_cloud_agent.py`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0277`)
> - **待复核原文**: “- [ ] 实现兼容 Meta 契约的 FastAPI 路由（`/fetch_vms`, `/api/voice/dictation`, `/chat/stream`, `/chat/subscribe`）；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0278`)
> - **待复核原文**: “- [ ] 集成 DashScope Realtime WebSocket 客户端与音频 PCM 转码器；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0279`)
> - **待复核原文**: “- [ ] 挂载 `skills/gadget-lingcube-msrr` 与 `skills/gadget-lingmatrix-sim` 工具注册表；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0280`)
> - **待复核原文**: “- [ ] 编写覆盖 100% 关键路径的自动化单元测试（`tests/test_bailian_muse_cloud_agent.py`）。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### Phase 3：StickS3 嵌入式固件混合协议栈升级与实机烧录（公理一）

{==- [ ] 在 `firmware/m5sticks3_buddy/src/main.cpp` 中完整引入 `muse_gadget_client.h`；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 挂接 Serial Hatch 控制台解析器与 `@chat` 响应输出；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- [ ] 联动 Avatar 12 种微表情与状态机；
- [ ] 按照公理一执行真实硬件编译与烧录：
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0281`)
> - **待复核原文**: “- [ ] 在 `firmware/m5sticks3_buddy/src/main.cpp` 中完整引入 `muse_gadget_client.h`；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0282`)
> - **待复核原文**: “- [ ] 挂接 Serial Hatch 控制台解析器与 `@chat` 响应输出；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


  ```powershell
  {==python -m platformio run -e m5sticks3_buddy -t upload==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
  ```
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0284`)
> - **待复核原文**: “python -m platformio run -e m5sticks3_buddy -t upload”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


{==- [ ] 触发 RTS/DTR 硬重启并捕获至少 15 秒真实串口运行诊断，验证零崩溃与稳定帧率。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0285`)
> - **待复核原文**: “- [ ] 触发 RTS/DTR 硬重启并捕获至少 15 秒真实串口运行诊断，验证零崩溃与稳定帧率。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### Phase 4：公网穿透自动化与端点自适应同步

{==- [ ] 联动 `skills/public-service-tunnel/scripts/tunnel_manager.py`，实现免登录 Cloudflare Quick Tunnel 秒级拉起；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 验证 `dist/public_preview_url.json` 持久化端点在不同网络环境下的可用性；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 验证 StickS3 在手机热点与远程公网模式下，通过持久化公网端点进行语音交互。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0286`)
> - **待复核原文**: “- [ ] 联动 `skills/public-service-tunnel/scripts/tunnel_manager.py`，实现免登录 Cloudflare Quick Tunnel 秒级拉起；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0287`)
> - **待复核原文**: “- [ ] 验证 `dist/public_preview_url.json` 持久化端点在不同网络环境下的可用性；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0288`)
> - **待复核原文**: “- [ ] 验证 StickS3 在手机热点与远程公网模式下，通过持久化公网端点进行语音交互。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.


### Phase 5：具身智能协同全链路闭环与长跑鲁棒性验收

{==- [ ] 开展自然语言复杂多步骤意图实测：“向前翻滚两步并开启3号面磁吸”；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
- [ ] 检验母线电压与 EPM 热保护机制；
{==- [ ] 联动 MuJoCo 数字孪生仿真器（LingMatrix）实现虚实镜像协同；==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
{==- [ ] 连续 1 小时长跑测试，验证内存零泄漏、I2C 零死锁、音频零断流。==}{>>[QUESTIONABLE] [MINOR] 依据: No DOI, standard, or empirical citation provided. | 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.<<}
> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0289`)
> - **待复核原文**: “- [ ] 开展自然语言复杂多步骤意图实测：“向前翻滚两步并开启3号面磁吸”；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0290`)
> - **待复核原文**: “- [ ] 联动 MuJoCo 数字孪生仿真器（LingMatrix）实现虚实镜像协同；”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.

> [!NOTE]
> **内容复核警示 [QUESTIONABLE] - 严重等级: MINOR** (Claim: `C0291`)
> - **待复核原文**: “- [ ] 连续 1 小时长跑测试，验证内存零泄漏、I2C 零死锁、音频零断流。”
> - **公理与事实推导**: 【出处核验差异】Claim makes empirical assertions without citing primary literature or standards.
> - **可验证出处与来源**: No DOI, standard, or empirical citation provided.
