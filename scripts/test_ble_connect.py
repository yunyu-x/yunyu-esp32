import asyncio
from bleak import BleakClient

TARGET_MAC = "7C:E8:B1:E2:33:ED"
NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"

async def main():
    print(f"Attempting to connect to StickS3 BLE: {TARGET_MAC}...")
    async with BleakClient(TARGET_MAC, timeout=10.0) as client:
        connected = client.is_connected
        print(f"Connected: {connected}")
        print("Discovering services...")
        for service in client.services:
            print(f"  Service: {service.uuid} ({service.description})")
            for char in service.characteristics:
                print(f"    Char: {char.uuid} ({','.join(char.properties)})")
        print("Holding connection for 5 seconds to observe StickS3 screen...")
        await asyncio.sleep(5.0)
    print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
