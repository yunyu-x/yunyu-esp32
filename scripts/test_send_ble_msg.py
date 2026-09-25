import asyncio
from bleak import BleakClient

TARGET_MAC = "7C:E8:B1:E2:33:ED"
NUS_RX_CHAR = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" # Write to device
NUS_TX_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" # Notify from device

async def main():
    print(f"Connecting to {TARGET_MAC}...")
    async with BleakClient(TARGET_MAC, timeout=10.0) as client:
        print(f"Connected: {client.is_connected}")
        
        received_ack = None
        def notification_handler(sender, data):
            nonlocal received_ack
            received_ack = data.decode('utf-8', errors='ignore')
            print(f"  [PHONE RX ACK]: {received_ack.strip()}")

        await client.start_notify(NUS_TX_CHAR, notification_handler)
        
        test_msg = "Hello StickS3!"
        print(f"Sending message: '{test_msg}'...")
        await client.write_gatt_char(NUS_RX_CHAR, test_msg.encode('utf-8'))
        await asyncio.sleep(2.0)
        
        test_msg2 = "灵方机器人收到"
        print(f"Sending Chinese message: '{test_msg2}'...")
        await client.write_gatt_char(NUS_RX_CHAR, test_msg2.encode('utf-8'))
        await asyncio.sleep(2.0)

        test_msg3 = "wifi"
        print(f"Sending Wi-Fi query command: '{test_msg3}'...")
        await client.write_gatt_char(NUS_RX_CHAR, test_msg3.encode('utf-8'))
        await asyncio.sleep(2.0)

        test_msg4 = "beep"
        print(f"Sending Beep tone command: '{test_msg4}'...")
        await client.write_gatt_char(NUS_RX_CHAR, test_msg4.encode('utf-8'))
        await asyncio.sleep(2.0)
        
        await client.stop_notify(NUS_TX_CHAR)
        
    print("Test complete. Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
