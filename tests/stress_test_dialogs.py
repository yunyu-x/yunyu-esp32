import serial
import time
import sys

def main():
    print("[TEST] Connecting to COM3 @ 115200...")
    ser = serial.Serial('COM3', 115200, timeout=1)
    
    # 触发硬件硬重启
    print("[TEST] Triggering RTS/DTR Hardware Reset...")
    ser.setDTR(False)
    ser.setRTS(True)
    time.sleep(0.1)
    ser.setRTS(False)
    time.sleep(0.2)

    print("[TEST] Reading Boot Diagnostics (10s)...")
    boot_start = time.time()
    while time.time() - boot_start < 10:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"  [BOOT] {line}")

    test_prompts = [
        "q:请用一句话介绍你自己",
        "q:中国的首都是哪里",
        "q:今天星期几",
        "q:给我讲一个五秒钟的幽默冷笑话",
        "q:你喜欢猫还是狗",
        "q:我们第一句聊了什么",
        "q:1加1等于几",
        "q:帮我总结一下我们刚刚聊过的所有内容"
    ]

    results = []

    for idx, prompt in enumerate(test_prompts, start=1):
        print(f"\n{'='*20} Round {idx} / {len(test_prompts)} {'='*20}")
        print(f"Sending prompt: {prompt}")
        ser.write((prompt + "\n").encode('utf-8'))
        
        round_start = time.time()
        round_success = False
        last_sys_line = ""
        
        while time.time() - round_start < 20:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if not line:
                continue
            print(f"  {line}")
            if "[StickS3-SYS]" in line:
                last_sys_line = line
            if "LLM response streaming complete" in line:
                round_success = True
                break
            if "rst:0x" in line or "Guru Meditation" in line or "PANIC" in line:
                print(f"  [ERROR] CRASH DETECTED IN ROUND {idx}!")
                round_success = False
                break
                
        results.append({
            "round": idx,
            "prompt": prompt,
            "success": round_success,
            "sys": last_sys_line
        })
        time.sleep(2.0)

    ser.close()

    print("\n" + "="*25 + " FINAL STRESS TEST REPORT " + "="*25)
    for r in results:
        status = "PASS [OK]" if r["success"] else "FAIL [CRASH]"
        print(f"Round {r['round']}: {status} | Prompt: {r['prompt']}")
        if r['sys']:
            print(f"         Hardware Telemetry -> {r['sys']}")
            
    all_pass = all(r["success"] for r in results)
    print("\n" + "="*60)
    if all_pass:
        print("[SUCCESS] ALL 8 ROUNDS PASSED WITH 100% STABILITY AND ZERO PANIC CRASH!")
        sys.exit(0)
    else:
        print("[FAILURE] STRESS TEST DETECTED INSTABILITY OR CRASH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
