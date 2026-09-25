#!/usr/bin/env python3
"""
scripts/test_ble_encoding.py
Connects to StickS3-Buddy over BLE, sends Chinese text in GBK and UTF-8,
and monitors serial logs and BLE ACKs.
"""

import asyncio
import serial
import time
from bleak import BleakClient

RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
ADDR = "7C:E8:B1:E2:33:ED"

async def main():
    s = serial.Serial("COM3", 115200, timeout=0.2)
    time.sleep(0.3)
    s.read(s.in_waiting)
    
    print("[TEST] Connecting to StickS3-Buddy BLE (7C:E8:B1:E2:33:ED)...")
    async with BleakClient(ADDR) as client:
        print(f"[TEST] BLE Connected: {client.is_connected}")
        
        def handle_ack(sender, data):
            ack_str = data.decode("utf-8", errors="replace").strip()
            print(f"  [BLE ACK From StickS3] => {ack_str}")
            
        await client.start_notify(TX_UUID, handle_ack)
        await asyncio.sleep(0.5)
        
        # 1. Send Chinese in GBK encoding
        print("\n--- Test 1: Sending Chinese in GBK encoding ('蓝牙国标汉字测试') ---")
        gbk_payload = "蓝牙国标汉字测试\n".encode("gbk")
        await client.write_gatt_char(RX_UUID, gbk_payload, response=False)
        await asyncio.sleep(1.0)
        
        # 2. Send Chinese in UTF-8 encoding
        print("\n--- Test 2: Sending Chinese in UTF-8 encoding ('蓝牙UTF8汉字测试') ---")
        utf8_payload = "蓝牙UTF8汉字测试\n".encode("utf-8")
        await client.write_gatt_char(RX_UUID, utf8_payload, response=False)
        await asyncio.sleep(1.0)
        
        # 3. Send Chinese in Hex string
        print("\n--- Test 3: Sending Chinese in Hex string ('e4bda0e5a5bd' -> '你好') ---")
        await client.write_gatt_char(RX_UUID, b"e4bda0e5a5bd\n", response=False)
        await asyncio.sleep(1.0)
        
        # Read COM3 serial logs
        logs = s.read(s.in_waiting).decode("utf-8", errors="replace")
        print("\n--- Hardware Serial Output during BLE test ---")
        for line in logs.splitlines():
            if "[CHAT-RX]" in line or "StickS3-ONLINE" in line:
                print(" ", line)
                
        s.close()
    print("\n[TEST] BLE Encoding Verification Finished Successfully!")

if __name__ == "__main__":
    asyncio.run(main())
