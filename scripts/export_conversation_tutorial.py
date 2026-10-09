#!/usr/bin/env python3
"""
scripts/export_conversation_tutorial.py
Parses transcript_full.jsonl and generates a comprehensive, pedagogical,
and complete markdown documentation of the entire interaction history.
"""

import json
import os
import re

TRANSCRIPT_PATH = r"C:\Users\Administrator\.gemini\antigravity\brain\e0938fcb-98fe-42be-a914-c7e004761638\.system_generated\logs\transcript_full.jsonl"
OUTPUT_PATH = r"d:\workspace\code\microUnit\doc\27_StickS3物理伴侣全流程对话开发实录与教学手册.md"

def clean_user_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    # Strip <CONTEXT_SUMMARY>...</CONTEXT_SUMMARY>
    if "<CONTEXT_SUMMARY>" in raw_text and "</CONTEXT_SUMMARY>" in raw_text:
        raw_text = re.sub(r"<CONTEXT_SUMMARY>.*?</CONTEXT_SUMMARY>", "", raw_text, flags=re.DOTALL)
    # Extract from <USER_REQUEST> if present
    if "<USER_REQUEST>" in raw_text:
        m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", raw_text, re.DOTALL)
        if m:
            raw_text = m.group(1)
    # Strip <ADDITIONAL_METADATA>...</ADDITIONAL_METADATA>
    raw_text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", raw_text, flags=re.DOTALL)
    return raw_text.strip()

def clean_agent_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    # Strip system messages
    raw_text = re.sub(r"<SYSTEM_MESSAGE>.*?</SYSTEM_MESSAGE>", "", raw_text, flags=re.DOTALL)
    return raw_text.strip()

def parse_transcript():
    turns = []
    current_turn = None
    turn_counter = 0

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            src = data.get("source")
            tp = data.get("type")
            content = data.get("content", "")

            if src == "USER_EXPLICIT" or tp == "USER_INPUT":
                user_msg = clean_user_text(content)
                if not user_msg:
                    continue
                if current_turn:
                    turns.append(current_turn)
                turn_counter += 1
                current_turn = {
                    "turn_id": turn_counter,
                    "created_at": data.get("created_at", ""),
                    "user_input": user_msg,
                    "responses": [],
                    "tool_summaries": []
                }
            elif current_turn and src == "MODEL" and tp == "PLANNER_RESPONSE":
                cleaned_resp = clean_agent_text(content)
                if cleaned_resp:
                    current_turn["responses"].append(cleaned_resp)
                
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    name = tc.get("name", "")
                    params = tc.get("parameters", {})
                    summary = params.get("toolSummary") or params.get("toolAction") or name
                    current_turn["tool_summaries"].append(f"`{name}`: {summary}")

    if current_turn:
        turns.append(current_turn)

    return turns

def generate_markdown(turns):
    doc = []
    doc.append("# 27_StickS3 物理伴侣全流程对话开发实录与教学手册")
    doc.append("")
    doc.append("> [!NOTE]")
    doc.append("> **教学手册导读 (Educational Purpose & Scope)**：")
    doc.append("> 本文档完整归档了 M5Stack StickS3 智能终端全生命周期的**真实人机协作开发对话过程**。")
    doc.append("> 覆盖从**淘宝产品采购调研**、**三种工程方案技术选型**、**全自主无人化烧录 Agent 研制**，到**屏幕点亮黑屏排查**、**6 轴 IMU 唤醒**、**BLE 广播包超限修复**、**多通道 Wi-Fi/音频并发**、**全集 GBK-Unicode Flash 映射表解决手机方格子乱码**，以及最终**建立代码提交与继续开发提示词标准**的全部 21 轮交互节点。")
    doc.append("> 旨在为具身智能、嵌入式物联网（IoT）及大模型 Agent 开发者提供第一手、免踩坑、具有高度工业实战价值的学习与复现指南。")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 目录导航 (Table of Contents)")
    doc.append("")
    doc.append("- [一、 交互全景脉络与学习路线图](#一-交互全景脉络与学习路线图)")
    doc.append("- [二、 21 轮人机协作实录与深度解析](#二-21-轮人机协作实录与深度解析)")
    for t in turns:
        tid = t["turn_id"]
        # Extract first line or short title
        title_line = t["user_input"].splitlines()[0]
        if len(title_line) > 35:
            title_line = title_line[:35] + "..."
        doc.append(f"  - [第 {tid} 轮：{title_line}](#第-{tid}-轮{title_line})")
    doc.append("- [三、 嵌入式 + AI Agent 核心方法论与避坑宝典](#三-嵌入式--ai-agent-核心方法论与避坑宝典)")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 一、 交互全景脉络与学习路线图")
    doc.append("")
    doc.append("整个开发生命周期经历了 4 大关键演进阶段：")
    doc.append("")
    doc.append("```mermaid")
    doc.append("flowchart TD")
    doc.append("    subgraph Phase1 [第一阶段：产品选型与方案制定]")
    doc.append("        T1[第1~3轮: 淘宝商品拆解与三大方案论证]\n        T2[方案1: M5Burner零代码 / 方案2: PlatformIO驱动 / 方案3: Claude Buddy伴侣]")
    doc.append("    end")
    doc.append("")
    doc.append("    subgraph Phase2 [第二阶段：全自主 Agent 烧录流水线研制]")
    doc.append("        T3[第4~8轮: 消除人工干预，研制 autonomous_bringup_agent.py]\n        T4[端口热捕获 -> 芯片引导握手 -> 极速编译烧录 -> 看门狗自愈复位 -> 进度可视化]")
    doc.append("    end")
    doc.append("")
    doc.append("    subgraph Phase3 [第三阶段：硬件攻坚与全功能多通道互联]")
    doc.append("        T5[第9~13轮: 点亮屏幕M5PM1 L3B电源门控]\n        T6[BMI270休眠唤醒 + BLE 31B广播包合规化 + 2.4G WiFi SoftAP/TCP/UDP/Web + ES8311音频]")
    doc.append("    end")
    doc.append("")
    doc.append("    subgraph Phase4 [第四阶段：真机协议抗干扰与全编码解决方格子乱码]")
    doc.append("        T7[第14~16轮: 临界区异步缓冲解耦防I2C冲突]\n        T8[构建23940条目全集GBK-Unicode Flash映射表，彻底消灭微信BLE方格子乱码]")
    doc.append("        T9[第17~21轮: 输出全流程工作交接文档，固化后续会话继续开发提示词标准，版本入库]")
    doc.append("    end")
    doc.append("")
    doc.append("    Phase1 --> Phase2 --> Phase3 --> Phase4")
    doc.append("```")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 二、 21 轮人机协作实录与深度解析")
    doc.append("")

    for t in turns:
        tid = t["turn_id"]
        created = t["created_at"]
        user_in = t["user_input"]
        responses = t["responses"]
        tools = t["tool_summaries"]

        doc.append(f"### 第 {tid} 轮：{user_in.splitlines()[0][:50]}")
        doc.append("")
        doc.append(f"> **交互时间**：`{created}`  ")
        doc.append(f"> **用户原始指令**：")
        doc.append("> ```text")
        for line in user_in.splitlines():
            doc.append(f"> {line}")
        doc.append("> ```")
        doc.append("")
        
        # Key Technical Actions
        if tools:
            doc.append("#### 🛠️ Agent 关键执行动作与工具链调用")
            doc.append("<details><summary>展开查看此轮次调用的关键工具链与操作 (" + str(len(tools)) + " 项)</summary>")
            doc.append("")
            # Group unique tools
            seen = set()
            for ts in tools[:25]:
                if ts not in seen:
                    doc.append(f"- {ts}")
                    seen.add(ts)
            if len(tools) > 25:
                doc.append(f"- *... 以及其余 {len(tools) - 25} 项自动化工具调用*")
            doc.append("")
            doc.append("</details>")
            doc.append("")

        # Agent Final Output
        doc.append("#### 💬 Agent 最终交付汇报与技术解析")
        if responses:
            # Use the last comprehensive response
            final_resp = responses[-1]
            doc.append(final_resp)
        else:
            doc.append("*（此轮次主要执行了后台自动化任务与工具流，结果已同步更新至对应工程与配置文件中）*")
        doc.append("")
        doc.append("---")
        doc.append("")

    doc.append("## 三、 嵌入式 + AI Agent 核心方法论与避坑宝典")
    doc.append("")
    doc.append("本项目的成功实践为未来大模型 Agent 自主开发嵌入式系统沉淀了如下宝贵工程法则：")
    doc.append("")
    doc.append("### 1. 硬件电源管理的第一性原理（隐蔽门控陷阱）")
    doc.append("- **陷阱**：现代 IoT 模块为降低功耗，常将屏幕背光、逻辑供电、音频功放等挂载在 PMIC（如 M5PM1）的 GPIO 门控上，而非直连 3.3V。")
    doc.append("- **法则**：屏幕黑屏、喇叭不响绝不能盲目修改驱动代码，第一步必须查验 I2C PMIC 寄存器配置（如本案必须将 M5PM1 GPIO2/3 配置为推挽输出并拉高）。")
    doc.append("")
    doc.append("### 2. 低功耗蓝牙协议栈的物理硬限制（31 字节铁律）")
    doc.append("- **陷阱**：BLE 4.x/5.0 Legacy Advertising 广播包物理上限**严格锁死 31 字节**，将 128 位 UUID 与长设备名一起塞入会导致 ESP-IDF 静默抛弃广播，iPhone 彻底搜不到。")
    doc.append("- **法则**：主广播包（advData）严控在 31B 以内（如 3B Flags + 18B UUID + 9B 缩写名 = 30B），长设备名必须拆分至扫描响应包（scanRespData）。")
    doc.append("")
    doc.append("### 3. 多任务并发下的 I2C 总线碰撞防范")
    doc.append("- **陷阱**：在蓝牙或 Wi-Fi 接收中断回调中直接执行耗时操作（如音频播放、I2C 功放寄存器配置），与主循环 40Hz IMU 姿态读取在同一 I2C 总线上竞争，导致总线锁死与蓝牙消息“仅能接收一次”。")
    doc.append("- **法则**：中断回调只做 < 2μs 的加锁缓冲转移（`std::vector<uint8_t>`），主循环通过 pending 标志异步安全分发，彻底解耦通信与外设。")
    doc.append("")
    doc.append("### 4. 异构编码冲突的第一性原理解决之道（自适应转码）")
    doc.append("- **陷阱**：国内微信小程序蓝牙助手默认按 GBK/GB2312 发送字节流，而屏幕字库（LovyanGFX）仅支持 UTF-8 Unicode 索引，导致解码失败渲染出方格子（□）。")
    doc.append("- **法则**：在 Flash 中固化 47KB 全集 GBK-Unicode 映射表（23,940 条目，O(1) 查表），构建 `sanitizeAndConvertToUtf8()` 自动清洗流水线（BOM剔除 -> Hex解码 -> UTF8校验 -> GBK无损映射），实现真机零乱码。")
    doc.append("")
    doc.append("### 5. 跨会话 Agent 协作的持续交付标准（交接红线）")
    doc.append("- **法则**：每次提交代码后，强制附带标准化继续开发提示词描述（`docs/AGENT_CONTINUATION_PROMPTS.md`），保证后续新对话中的 Agent 零提示漂移、无缝承接。")
    doc.append("")

    return "\n".join(doc)

def main():
    print(f"Reading transcript from: {TRANSCRIPT_PATH}")
    turns = parse_transcript()
    print(f"Extracted {len(turns)} conversation turns.")
    md_content = generate_markdown(turns)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Generated {OUTPUT_PATH} ({len(md_content)} characters, {os.path.getsize(OUTPUT_PATH)} bytes).")

if __name__ == "__main__":
    main()
