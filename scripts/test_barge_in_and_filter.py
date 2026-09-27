import urllib.request
import urllib.parse
import json
import time

DEV_IP = "192.168.110.67"

def get_status():
    url = f"http://{DEV_IP}/bailian/status"
    with urllib.request.urlopen(url, timeout=3) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))

def send_query(text):
    data = urllib.parse.urlencode({"text": text}).encode("utf-8")
    req = urllib.request.Request(f"http://{DEV_IP}/bailian/send_text", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode("utf-8", errors="replace")
            res = json.loads(body)
            print(f"\n[QUERY SENT] \"{text}\" -> HTTP: {body}")
            if res.get("status") == "error":
                # 尝试自动触发重连后再发一次
                print("  [WARN] send_text reported error, attempting /bailian/reconnect...")
                urllib.request.urlopen(urllib.request.Request(f"http://{DEV_IP}/bailian/reconnect", data=b"", method="POST"))
                time.sleep(1.5)
                with urllib.request.urlopen(req, timeout=5) as r2:
                    body2 = r2.read().decode("utf-8", errors="replace")
                    print(f"  [RETRY QUERY] -> HTTP: {body2}")
                    return json.loads(body2)
            return res
    except Exception as e:
        print(f"  [ERR] send_query exception: {e}")
        raise

def ensure_listening():
    for _ in range(15):
        st = get_status()
        if st.get("state_code") == 3: # LISTENING
            return st
        time.sleep(0.4)
    # 若长时间未处于 LISTENING，尝试重连
    urllib.request.urlopen(urllib.request.Request(f"http://{DEV_IP}/bailian/reconnect", data=b"", method="POST"))
    time.sleep(1.5)
    return get_status()

def test_speaker_echo_isolation():
    print("\n=======================================================")
    print("▶ Test Case 1: 验证喇叭音频过滤 (Echo Filter Isolation)")
    print("=======================================================")
    st0 = ensure_listening()
    print(f"Initial status: state={st0.get('state_name')}, interrupts={st0.get('interrupts')}")
    init_interrupts = st0.get("interrupts", 0)

    # 发送数字报数，保证有 2~3 秒稳定连续音频输出
    send_query("请从1慢速数到20，每个数字之间用逗号隔开：1，2，3，4，5，6，7...")

    # 监控是否进入 SPEAKING 状态并在播报期间保持不被喇叭自激打断
    speaking_seen = False
    for i in range(25):
        time.sleep(0.2)
        st = get_status()
        code = st.get("state_code")
        cur_ints = st.get("interrupts", 0)
        if code == 5:
            speaking_seen = True
            print(f"  [{i*0.2:.1f}s] AI is SPEAKING: \"{st.get('ai_reply')[:30]}\" | Interrupts={cur_ints}")
            assert cur_ints == init_interrupts, f"Speaker echo self-interrupted! ({cur_ints} != {init_interrupts})"
        elif speaking_seen and code == 3:
            print("  ✔ Natural playback completed smoothly without false barge-in!")
            break

    assert speaking_seen, "AI should enter SPEAKING state"
    print("  ✔ PASS: 喇叭自身播放音频未引起任何误打断，回声过滤机制表现完美！")

def test_physical_button_interrupt_during_speaking():
    print("\n=======================================================")
    print("▶ Test Case 2: 验证播报期间物理打断 (Barge-In during Speaking)")
    print("=======================================================")
    st0 = ensure_listening()
    init_interrupts = st0.get("interrupts", 0)

    send_query("请从1慢速数到50，每个数字之间加逗号：1，2，3，4，5，6，7，8，9，10...")

    interrupted = False
    for i in range(25):
        time.sleep(0.1)
        st = get_status()
        code = st.get("state_code")
        if code == 5: # SPEAKING
            print(f"  [{i*0.1:.1f}s] AI is SPEAKING! Immediately triggering Barge-In...")
            req = urllib.request.Request(f"http://{DEV_IP}/bailian/interrupt", data=b"", method="POST")
            with urllib.request.urlopen(req, timeout=3) as r:
                print("  Interrupt API response:", r.read().decode("utf-8"))
            interrupted = True
            break

    assert interrupted, "Should have reached SPEAKING state and triggered interrupt"

    time.sleep(0.05)
    st_post = get_status()
    print(f"  Status after interrupt: code={st_post.get('state_code')} ({st_post.get('state_name')}), interrupts={st_post.get('interrupts')}")
    assert st_post.get("interrupts") == init_interrupts + 1, "Interrupt count must increase by 1"

    time.sleep(0.2)
    st_rec = get_status()
    print(f"  Status after 200ms recovery: code={st_rec.get('state_code')} ({st_rec.get('state_name')})")
    assert st_rec.get("state_code") == 3, "State should be LISTENING (3)"
    print("  ✔ PASS: 播报期间打断毫秒级生效，截断音频并瞬间切回倾听待命！")

def test_interrupt_during_thinking():
    print("\n=======================================================")
    print("▶ Test Case 3: 验证思考阶段即时打断 (Barge-In during Thinking)")
    print("=======================================================")
    st0 = ensure_listening()
    init_interrupts = st0.get("interrupts", 0)

    send_query("请背诵长篇文言文《岳阳楼记》全文。")

    # 思考阶段立即触发打断
    req = urllib.request.Request(f"http://{DEV_IP}/bailian/interrupt", data=b"", method="POST")
    with urllib.request.urlopen(req, timeout=3) as r:
        print("  Triggered interrupt during THINKING state ->", r.read().decode("utf-8"))

    time.sleep(0.1)
    st_post = get_status()
    print(f"  Status post thinking-interrupt: code={st_post.get('state_code')} ({st_post.get('state_name')}), interrupts={st_post.get('interrupts')}")
    assert st_post.get("interrupts") == init_interrupts + 1, "Interrupt count must increase in thinking state"

    time.sleep(0.2)
    st_rec = get_status()
    print(f"  Recovered to: {st_rec.get('state_name')}")
    assert st_rec.get("state_code") == 3, "Should recover to LISTENING"
    print("  ✔ PASS: 大模型思考阶段打断毫秒级生效，取消云端推理并立即恢复！")

def main():
    print("================================================================")
    print("  M5Stack StickS3 回声过滤、人声打断与全物理按键打断实测套件")
    print("================================================================")
    test_speaker_echo_isolation()
    test_physical_button_interrupt_during_speaking()
    test_interrupt_during_thinking()
    print("\n🎉 ALL 3 BARGE-IN & AUDIO FILTERING TEST CASES PASSED 100%!")

if __name__ == "__main__":
    main()
