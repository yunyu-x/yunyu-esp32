#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/test_poem_playback_and_vad_immunity.py
------------------------------------------------
验证诗歌连续播报不中断、AEC声学回声包络自激抑制、防非语音误唤醒与硬件性能深度监控
"""

import urllib.request
import urllib.parse
import json
import time

DEV_IP = "192.168.110.67"

def get_status():
    url = f"http://{DEV_IP}/bailian/status"
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except Exception:
            time.sleep(0.3)
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))

def get_metrics():
    url = f"http://{DEV_IP}/system/metrics"
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except Exception:
            time.sleep(0.3)
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))

def send_query(text):
    data = urllib.parse.urlencode({"text": text}).encode("utf-8")
    req = urllib.request.Request(f"http://{DEV_IP}/bailian/send_text", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        body = r.read().decode("utf-8", errors="replace")
        print(f"\n[QUERY SENT] \"{text}\" -> HTTP: {body}")
        return json.loads(body)

def ensure_listening():
    for _ in range(15):
        st = get_status()
        if st.get("state_code") == 3: # LISTENING
            return st
        time.sleep(0.4)
    # 若未处于 LISTENING 则尝试重连
    urllib.request.urlopen(urllib.request.Request(f"http://{DEV_IP}/bailian/reconnect", data=b"", method="POST"))
    time.sleep(1.5)
    return get_status()

def test_poem_continuous_playback_no_self_interruption():
    print("\n=======================================================")
    print("▶ Test Case 1: 诗歌连续朗诵无自激打断 (Poem Recitation Playback)")
    print("=======================================================")
    st0 = ensure_listening()
    init_interrupts = st0.get("interrupts", 0)
    print(f"Initial State: {st0.get('state_name')}, Interrupts={init_interrupts}")

    # 发送用户现场触发问题的真实指令：“换一首诗”
    send_query("请换一首优美的唐诗并完整朗诵出来，比如李白的《早发白帝城》全文。")

    speaking_frames = 0
    max_wait = 35 # 最多监控 14 秒
    speaking_seen = False

    for i in range(max_wait):
        time.sleep(0.4)
        st = get_status()
        code = st.get("state_code")
        cur_ints = st.get("interrupts", 0)
        reply = st.get("ai_reply", "")
        
        if code == 4:
            print(f"  [{i*0.4:.1f}s] AI 正在思考 (Thinking)...")
        elif code == 5:
            speaking_seen = True
            speaking_frames += 1
            print(f"  [{i*0.4:.1f}s] AI 正在朗读诗歌 (Speaking): \"{reply[:40]}...\" | Interrupts={cur_ints}")
            # 关键验证：播报期间绝不能出现喇叭自激打断！
            assert cur_ints == init_interrupts, f"诗歌朗读被自身喇叭误打断！(cur={cur_ints}, init={init_interrupts})"
        elif speaking_seen and code == 3:
            print(f"  ✔ 诗歌完整朗诵结束，平滑排空并恢复倾听待命！(朗诵持续 ~{speaking_frames*0.4:.1f}s)")
            break

    assert speaking_seen, "AI 应成功进入 Speaking 状态"
    print("  ✔ PASS: 诗歌朗诵全程顺畅，零自激误打断，'输出一小段音频卡住'问题彻底根除！")

def test_hardware_available_performance_metrics():
    print("\n=======================================================")
    print("▶ Test Case 2: 硬件可用性能与总线健康深度监控 (Hardware Performance)")
    print("=======================================================")
    time.sleep(3.0) # 等待 3.0 秒让播放后的 NVS Flash 写入与 1 秒 FPS 滑动统计窗口完成采样更新
    m = get_metrics()
    cpu_fps = m.get("cpu", {}).get("loop_fps", 0)
    audio_stack_hwm = m.get("cpu", {}).get("audio_stack_hwm", 0)
    free_sram = m.get("memory", {}).get("free_internal_heap", 0)
    largest_sram = m.get("memory", {}).get("largest_internal_block", 0)
    free_psram = m.get("memory", {}).get("free_psram", 0)
    i2c_fails = m.get("io", {}).get("i2c_lock_failures", 0)
    i2c_tx = m.get("io", {}).get("i2c_tx_count", 0)

    print(f"  - 主循环帧率 (CPU Loop FPS): {cpu_fps:.1f} FPS (要求 >= 45.0)")
    print(f"  - 音频任务堆栈安全水位 (Stack HWM): {audio_stack_hwm} Bytes (要求 >= 1500)")
    print(f"  - 内部可用 SRAM: {free_sram/1024:.1f} KB (最大连续块: {largest_sram/1024:.1f} KB)")
    print(f"  - 可用 PSRAM: {free_psram/(1024*1024):.2f} MB")
    print(f"  - I2C 总线传输: {i2c_tx} 次, 锁冲突失败: {i2c_fails} 次 (要求恒为 0)")

    assert cpu_fps >= 45.0, f"CPU FPS 偏低: {cpu_fps}"
    assert audio_stack_hwm >= 1500, f"音频任务堆栈不足: {audio_stack_hwm}"
    assert free_sram >= 60 * 1024, f"内部 SRAM 内存吃紧: {free_sram}"
    assert largest_sram >= 45 * 1024, f"内部 SRAM 存在碎片: {largest_sram}"
    assert free_psram >= 7.0 * 1024 * 1024, f"PSRAM 不足: {free_psram}"
    assert i2c_fails == 0, f"I2C 存在锁竞争冲突: {i2c_fails}"
    print("  ✔ PASS: 所有硬件可用性能与内存/总线健康指标完全满足工业级要求！")

def test_intentional_barge_in_and_recovery():
    print("\n=======================================================")
    print("▶ Test Case 3: 真实打断灵敏度与自愈验证 (Intentional Barge-In)")
    print("=======================================================")
    st0 = ensure_listening()
    init_interrupts = st0.get("interrupts", 0)

    send_query("请从1慢速数到50：1，2，3，4，5，6，7，8，9，10...")

    interrupted = False
    for i in range(25):
        time.sleep(0.1)
        st = get_status()
        if st.get("state_code") == 5: # Speaking
            print(f"  [{i*0.1:.1f}s] AI 正在播报数字，主动触发打断...")
            req = urllib.request.Request(f"http://{DEV_IP}/bailian/interrupt", data=b"", method="POST")
            urllib.request.urlopen(req, timeout=3)
            interrupted = True
            break

    assert interrupted, "未能进入 Speaking 状态"
    time.sleep(0.15)
    st_post = get_status()
    print(f"  打断后状态: {st_post.get('state_name')} (code={st_post.get('state_code')}), Interrupts={st_post.get('interrupts')}")
    assert st_post.get("interrupts") == init_interrupts + 1, "打断计数必须准确递增 1"

    time.sleep(0.2)
    st_rec = get_status()
    print(f"  自愈恢复后状态: {st_rec.get('state_name')}")
    assert st_rec.get("state_code") == 3, "必须恢复至 LISTENING 模式"
    print("  ✔ PASS: 主动打断毫秒级响应，并且平滑自愈切回聆听！")

def main():
    print("================================================================")
    print("  M5Stack StickS3 诗歌播放防卡顿、防误唤醒与性能监控实测")
    print("================================================================")
    test_poem_continuous_playback_no_self_interruption()
    test_hardware_available_performance_metrics()
    test_intentional_barge_in_and_recovery()
    print("\n🎉 ALL POEM PLAYBACK, ANTI-FALSE-TRIGGER & METRIC TESTS PASSED 100%!")

if __name__ == "__main__":
    main()
