import requests
import serial
import threading
import time

DEV_IP = "192.168.110.67"
API_KEY = "sk-ws-H.EPHMIMH.PqIK.MEQCIHgyLDXLvnwi_PGoocOu5C-Azgxc8ISga2Mrz3n-DTdxAiBsI8cGPSo2p6JA4WbyHX0YWN8KeBoDZ86Puoqt7YVLug"

logs = []
stop_flag = False

def ts():
    now = time.time()
    return f"{time.strftime('%H:%M:%S', time.localtime(now))}.{int((now % 1) * 1000):03d}"

def serial_reader():
    try:
        # Non-resetting open if possible
        s = serial.Serial()
        s.port = 'COM3'
        s.baudrate = 115200
        s.timeout = 0.5
        s.dtr = False
        s.rts = False
        s.open()
        while not stop_flag:
            line = s.readline().decode('utf-8', errors='ignore').strip()
            if line:
                t_str = ts()
                logs.append((t_str, line))
                print(f"[{t_str}] [COM3] {line}")
        s.close()
    except Exception as e:
        print(f"[{ts()}] Serial exception: {e}")

if __name__ == "__main__":
    t_start = time.time()
    print(f"[{ts()}] [STAGE 0: Start Serial Monitoring]")
    th = threading.Thread(target=serial_reader, daemon=True)
    th.start()
    time.sleep(1.0)

    # 1. Query Wi-Fi status
    print(f"[{ts()}] [STAGE 1: Querying Wi-Fi Status via LAN HTTP]")
    t0 = time.time()
    r = requests.get(f"http://{DEV_IP}/wifi/status", timeout=5)
    t1 = time.time()
    print(f"[{ts()}] [STAGE 1: Wi-Fi Status OK] Latency: {(t1-t0)*1000:.1f}ms | Data: {r.json()}")

    # 2. Post Bailian Config
    print(f"[{ts()}] [STAGE 2: Posting Bailian Key & Model Configuration to StickS3]")
    t2 = time.time()
    payload = {
        "key": API_KEY,
        "model": "qwen-omni-turbo-realtime",
        "voice": "cherry"
    }
    r2 = requests.post(f"http://{DEV_IP}/bailian/config", data=payload, timeout=5)
    t3 = time.time()
    print(f"[{ts()}] [STAGE 2: Bailian Config Saved] Latency: {(t3-t2)*1000:.1f}ms | Response: {r2.json()}")

    # 3. Monitor StickS3 COM3 logs for WSS connection & session handshake
    print(f"[{ts()}] [STAGE 3: Waiting for StickS3 WSS Handshake & Session Creation...]")
    time.sleep(6.0)

    # 4. Query Bailian Status
    print(f"[{ts()}] [STAGE 4: Querying StickS3 Bailian Status via HTTP]")
    t4 = time.time()
    r3 = requests.get(f"http://{DEV_IP}/bailian/status", timeout=5)
    t5 = time.time()
    print(f"[{ts()}] [STAGE 4: Bailian Status] Latency: {(t5-t4)*1000:.1f}ms | Data: {r3.json()}")

    # 5. Test Remote Barge-In Endpoint
    print(f"[{ts()}] [STAGE 5: Testing Remote Barge-In API]")
    t6 = time.time()
    r4 = requests.post(f"http://{DEV_IP}/bailian/interrupt", timeout=5)
    t7 = time.time()
    print(f"[{ts()}] [STAGE 5: Barge-In Triggered] Latency: {(t7-t6)*1000:.1f}ms | Response: {r4.json()}")

    time.sleep(3.0)
    stop_flag = True
    th.join(timeout=2.0)
    print(f"[{ts()}] [ALL STAGES COMPLETE] Total Elapsed: {time.time()-t_start:.2f}s")
