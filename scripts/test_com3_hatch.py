"""
scripts/test_com3_hatch.py
--------------------------
Tests physical StickS3 COM3 hardware reset, boot telemetry, and Meta Muse Hatch protocol.
"""
import time
import serial

def main():
    print("[COM3] Opening serial port COM3 @ 115200...")
    ser = serial.Serial('COM3', 115200, timeout=0.5)

    # Hardware hard reset via RTS/DTR
    print("[COM3] Triggering RTS/DTR hardware reset...")
    ser.setDTR(False)
    ser.setRTS(True)
    time.sleep(0.1)
    ser.setRTS(False)
    time.sleep(0.3)

    start_time = time.time()
    hatch_status_sent = False
    hatch_face_sent = False

    while time.time() - start_time < 12:
        line_bytes = ser.readline()
        if line_bytes:
            line = line_bytes.decode('utf-8', errors='replace').strip()
            if line:
                print(f"[RECV] {line}")

        elapsed = time.time() - start_time
        if elapsed > 4.0 and not hatch_status_sent:
            print("[SEND] >status")
            ser.write(b">status\n")
            hatch_status_sent = True

        if elapsed > 7.0 and not hatch_face_sent:
            print("[SEND] >face=happy")
            ser.write(b">face=happy\n")
            hatch_face_sent = True

    ser.close()
    print("[COM3] Finished diagnostic session.")

if __name__ == '__main__':
    main()
