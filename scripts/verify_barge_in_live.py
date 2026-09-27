import urllib.request
import urllib.parse
import json
import time

DEV_IP = "192.168.110.67"

def get_status():
    url = f"http://{DEV_IP}/bailian/status"
    with urllib.request.urlopen(url, timeout=3) as r:
        return json.loads(r.read().decode("utf-8"))

def send_query(text):
    data = urllib.parse.urlencode({"text": text}).encode("utf-8")
    req = urllib.request.Request(f"http://{DEV_IP}/bailian/send_text", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        res = json.loads(r.read().decode("utf-8"))
        print(f"\n[QUERY SENT] \"{text}\" -> {res}")
        return res

def test_playback_and_interrupt():
    print("=== Step 1: Ensure LISTENING status ===")
    for _ in range(10):
        st = get_status()
        if st.get("state_code") == 3:
            break
        time.sleep(0.5)
    print(f"Current state: {st.get('state_name')} (code={st.get('state_code')}), interrupts={st.get('interrupts')}")
    init_interrupts = st.get("interrupts", 0)

    print("\n=== Step 2: Send Long Counting Query for Playback ===")
    send_query("请从1慢速数到50，每个数字之间用逗号隔开：1，2，3，4，5，6，7，8，9，10，11...")

    print("\n=== Step 3: Wait for SPEAKING and trigger Barge-In ===")
    interrupted = False
    for i in range(25):
        time.sleep(0.1)
        st = get_status()
        code = st.get("state_code")
        print(f"  [{i*0.1:.1f}s] code={code} ({st.get('state_name')}) | reply=\"{st.get('ai_reply')[:30]}\"")
        if code == 5: # SPEAKING
            print("  >>> AI is SPEAKING! Immediately triggering Barge-In! <<<")
            # 立即触发打断
            req = urllib.request.Request(f"http://{DEV_IP}/bailian/interrupt", data=b"", method="POST")
            with urllib.request.urlopen(req, timeout=3) as r:
                print("  Interrupt API response:", r.read().decode("utf-8"))
            interrupted = True
            break

    assert interrupted, "Should have reached SPEAKING state and triggered interrupt"

    # 验证打断状态
    time.sleep(0.05)
    st_post = get_status()
    print(f"\nImmediate post-interrupt: code={st_post.get('state_code')} ({st_post.get('state_name')}), interrupts={st_post.get('interrupts')}")
    assert st_post.get("interrupts") == init_interrupts + 1, "Interrupt counter should increment by 1"

    # 等待 150ms 验证极速自愈并恢复倾听
    time.sleep(0.2)
    st_rec = get_status()
    print(f"After 200ms recovery: code={st_rec.get('state_code')} ({st_rec.get('state_name')})")
    assert st_rec.get("state_code") == 3, "State should be LISTENING (3)"

    print("\n🎉 BARGE-IN TEST PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_playback_and_interrupt()
