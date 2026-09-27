import urllib.request
import urllib.parse
import json
import time

DEV_IP = "192.168.110.67"

def send_query(text):
    data = urllib.parse.urlencode({'text': text}).encode('utf-8')
    req = urllib.request.Request(f'http://{DEV_IP}/bailian/send_text', data=data, method='POST')
    urllib.request.urlopen(req, timeout=5)
    print(f"\n[QUERY SENT] \"{text}\"")

    # Poll status until reply is done
    last_reply = ""
    for i in range(25):
        time.sleep(0.6)
        st = json.loads(urllib.request.urlopen(f'http://{DEV_IP}/bailian/status', timeout=3).read().decode('utf-8'))
        reply = st.get('ai_reply', '')
        if reply != last_reply:
            print(f"  [{i*0.6:.1f}s] AI: {reply}")
            last_reply = reply
        if st.get('state_code') == 3 and len(reply) > 0:
            print(f"  ✔ Turn finished! Full reply: \"{reply}\"")
            return reply
    return last_reply

def main():
    print("=== Step 1: Query Current Memory ===")
    mem0 = json.loads(urllib.request.urlopen(f'http://{DEV_IP}/memory/list', timeout=3).read().decode('utf-8'))
    print(f"Initial Memory Turns: {mem0.get('total')}")

    print("\n=== Step 2: Dialogue Turn 1 (Establish Identity & Facts) ===")
    r1 = send_query("你好，我叫小明，我是一名在杭州工作的嵌入式算法工程师。")
    time.sleep(1.0)

    mem1 = json.loads(urllib.request.urlopen(f'http://{DEV_IP}/memory/list', timeout=3).read().decode('utf-8'))
    print(f"Memory turns after Turn 1: {mem1.get('total')}")
    assert mem1.get('total') >= 1, "Memory should record Turn 1!"

    print("\n=== Step 3: Dialogue Turn 2 (Recall Name and Profession) ===")
    r2 = send_query("请问我的名字叫什么？我的工作职业是什么？")
    time.sleep(1.0)

    print("Checking AI memory recall in Turn 2...")
    has_name = "小明" in r2
    has_job = ("嵌入式" in r2) or ("算法" in r2) or ("工程" in r2)
    print(f"  - Recalled Name ('小明'): {'PASS' if has_name else 'FAIL'}")
    print(f"  - Recalled Profession ('嵌入式/算法'): {'PASS' if has_job else 'FAIL'}")
    assert has_name, f"AI did not recall user name! Reply was: {r2}"

    print("\n=== Step 4: Hot-Switch Voice to Raymond & Preview ===")
    data = urllib.parse.urlencode({'voice': 'Raymond'}).encode('utf-8')
    req = urllib.request.Request(f'http://{DEV_IP}/bailian/config', data=data, method='POST')
    res = json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))
    print("Switch voice response:", res)
    assert res.get('voice') == 'Raymond', "Voice switch failed!"

    st = json.loads(urllib.request.urlopen(f'http://{DEV_IP}/bailian/status', timeout=3).read().decode('utf-8'))
    print(f"Status voice after switch: {st.get('configured_voice')}, Memory count: {st.get('memory_turns')}")

    print("\n=== Step 5: Dialogue Turn 3 (Cross-Voice Memory Recall) ===")
    r3 = send_query("请问我是在哪个城市工作？")
    time.sleep(1.0)

    has_city = "杭州" in r3
    print(f"  - Recalled City ('杭州') under new Raymond voice: {'PASS' if has_city else 'FAIL'}")
    assert has_city, f"AI did not recall city across voice switch! Reply was: {r3}"

    print("\n=== Step 6: Verify Final Memory Store Timeline ===")
    final_mem = json.loads(urllib.request.urlopen(f'http://{DEV_IP}/memory/list', timeout=3).read().decode('utf-8'))
    print(f"Total turns stored: {final_mem.get('total')}")
    for t in final_mem.get('turns', []):
        print(f"  Turn #{t['id']} [{t['voice']} at {t['time']}]: Q=\"{t['user']}\" -> A=\"{t['ai'][:30]}...\"")

    print("\n🎉 ALL FULL-DUPLEX MEMORY & VOICE SWITCHING TESTS PASSED PERFECTLY!")

if __name__ == '__main__':
    main()
