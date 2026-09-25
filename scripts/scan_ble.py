import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning BLE devices for 5 seconds...")
    devices = await BleakScanner.discover(timeout=5.0)
    print(f"Total {len(devices)} devices found:")
    for d in devices:
        print(f"  [{d.address}] Name: '{d.name}'")

if __name__ == "__main__":
    asyncio.run(main())
