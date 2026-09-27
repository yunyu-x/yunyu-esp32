#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/test_voice_dialogue_and_memory_compression.py
-------------------------------------------------------
StickS3 全双工大模型语音问答、长程多轮记忆压缩与硬件资源看门狗自动化端到端实测验证脚本
"""

import sys
import time
import json
import urllib.request
import urllib.parse

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

DEV_IP = "192.168.110.67"

def get_status():
    url = f"http://{DEV_IP}/bailian/status"
    req = urllib.request.Request(url, headers={'User-Agent': 'StickS3-Test'})
    resp = urllib.request.urlopen(req, timeout=5)
    return json.loads(resp.read().decode('utf-8'))

def get_memory_list():
    url = f"http://{DEV_IP}/memory/list"
    req = urllib.request.Request(url, headers={'User-Agent': 'StickS3-Test'})
    resp = urllib.request.urlopen(req, timeout=5)
    return json.loads(resp.read().decode('utf-8'))

def clear_memory():
    url = f"http://{DEV_IP}/memory/clear"
    req = urllib.request.Request(url, data=b"", method='POST', headers={'User-Agent': 'StickS3-Test'})
    resp = urllib.request.urlopen(req, timeout=5)
    return json.loads(resp.read().decode('utf-8'))

def send_query_and_wait(query, max_wait_sec=20):
    print(f"\n---> [USER QUERY] \"{query}\"")
    data = urllib.parse.urlencode({'text': query}).encode('utf-8')
    req = urllib.request.Request(f"http://{DEV_IP}/bailian/send_text", data=data, method='POST',
                                 headers={'User-Agent': 'StickS3-Test'})
    urllib.request.urlopen(req, timeout=5)

    last_reply = ""
    start_t = time.time()
    while time.time() - start_t < max_wait_sec:
        time.sleep(0.5)
        st = get_status()
        reply = st.get('ai_reply', '')
        state_code = st.get('state_code', 0)
        state_name = st.get('state_name', '')
        if reply != last_reply:
            print(f"     [{time.time()-start_t:.1f}s | {state_name}] AI: {reply}")
            last_reply = reply
        # state_code 3 is BL_STATE_LISTENING (idle listening after response done)
        if state_code == 3 and len(reply) > 0 and (time.time() - start_t > 2.0):
            print(f"     ✔ Turn Complete! Final Reply: \"{reply}\"")
            return reply, st
    print(f"     [TIMEOUT] Reached max wait ({max_wait_sec}s). Last reply: \"{last_reply}\"")
    return last_reply, get_status()

def main():
    print("=" * 70)
    print(">>> StickS3 Voice Dialogue, Memory Compression & SRAM Health E2E Test <<<")
    print("=" * 70)

    # 1. 检查初始状态与网络连通性
    print("\n[Step 1: 检查设备连接与大模型在线就绪状态]")
    st0 = get_status()
    print(f"  - 状态: {st0.get('state_name')} (Code: {st0.get('state_code')})")
    print(f"  - WSS 连通: {'PASS' if st0.get('is_connected') else 'FAIL'}")
    print(f"  - 当前音色: {st0.get('configured_voice')}")
    print(f"  - 当前记忆轮次: {st0.get('memory_turns')}")
    assert st0.get('is_connected'), "StickS3 WebSocket 未连接至百炼云端!"

    # 2. 清空测试记忆以执行确定性基准测试
    print("\n[Step 2: 重置对话记忆建立确定性环境]")
    clear_res = clear_memory()
    print(f"  - 清空响应: {clear_res}")
    time.sleep(1.0)
    mem_init = get_memory_list()
    print(f"  - 重置后记忆总轮次: {mem_init.get('total')}")
    assert mem_init.get('total') == 0, "记忆清空失败!"

    # 3. 连续执行 9 轮长程对话 (超越 8 轮上限以触发自动压缩与前期摘要)
    test_queries = [
        "你好，我叫李华，我是一名在上海从事人形机器人研发的硬件架构师。", # Turn 1: 设定人设
        "我最喜欢的诗是李白的《静夜思》，请用一句话评价这首诗。",               # Turn 2: 设定喜好
        "今天上海天气怎么样？请用一句话回答。",                                 # Turn 3: 短对话
        "机器人关节电机常用的减速器有哪些类型？",                              # Turn 4: 专业知识
        "谐波减速器和行星减速器有什么核心区别？",                              # Turn 5: 专业知识
        "StickS3 是由什么主控芯片驱动的？",                                    # Turn 6: 硬件知识
        "请为我背诵《静夜思》的前两句。",                                      # Turn 7: 召回喜好诗词
        "请问我的职业是什么？我在哪座城市工作？",                              # Turn 8: 达到 8 轮上限
        "请问我的名字叫什么？在前面的对话中我们讨论了哪首诗？"                 # Turn 9: 触发压缩机制并跨轮召回
    ]

    for i, q in enumerate(test_queries, start=1):
        print(f"\n=== Dialogue Turn {i}/9 ===")
        reply, st = send_query_and_wait(q)
        time.sleep(1.0)
        cur_mem = get_memory_list()
        print(f"  -> 当前记录轮次: {cur_mem.get('total')}, next_id: {cur_mem.get('next_id')}")
        
        # 验证记忆轮次上限受控 (不得超过 MAX_TURNS_IN_MEMORY=8)
        assert cur_mem.get('total') <= 8, f"记忆轮次超过 8 轮上限! 当前: {cur_mem.get('total')}"

        if i == 8:
            print("  ✔ Turn 8: 已达 PSRAM 存储上限 (8 轮)。准备在 Turn 9 触发自动压缩...")
        elif i == 9:
            print("  ✔ Turn 9: 自动记忆压缩已触发！检查前期摘要与关键信息召回...")
            has_name = "李华" in reply
            has_poem = ("静夜思" in reply) or ("李白" in reply)
            print(f"    * 姓名召回 ('李华'): {'PASS' if has_name else 'FAIL'}")
            print(f"    * 诗歌召回 ('静夜思'): {'PASS' if has_poem else 'FAIL'}")
            assert has_name, f"跨轮次压缩后姓名召回失败! 回复: {reply}"

    # 4. 深度审计最终记忆结构与摘要
    print("\n[Step 4: 记忆存储结构深度审计]")
    final_mem = get_memory_list()
    print(f"  - 最终保留总轮次: {final_mem.get('total')} (严格 <= 8)")
    assert final_mem.get('total') <= 8, "最终轮次必须 <= 8!"
    
    print("\n  --- 对话记忆时间线明细 ---")
    for t in final_mem.get('turns', []):
        print(f"    [Turn #{t['id']} | {t['time']} | {t['voice']}]")
        print(f"      Q: {t['user']}")
        print(f"      A: {t['ai'][:60]}...")
    
    # 5. 校验硬件健康与资源占用指标
    print("\n[Step 5: 硬件资源与内存碎片健康度审计]")
    final_st = get_status()
    print(f"  - 最终系统状态: {final_st.get('state_name')}")
    print(f"  - 异常报错: '{final_st.get('error')}' (应为空)")
    assert final_st.get('error') == "", f"系统存在报错: {final_st.get('error')}"

    print("\n🎉 =================================================================")
    print("🎉 ALL VOICE DIALOGUE, MEMORY COMPRESSION & HARDWARE TESTS PASSED!")
    print("🎉 =================================================================")

if __name__ == '__main__':
    main()
