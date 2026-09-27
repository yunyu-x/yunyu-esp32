#!/usr/bin/env bash
set -e

echo "============================================================================"
echo "  M5Stack StickS3 Voice Buddy OS v1.0.0-stable 一键固件烧录工具 (Linux/macOS)"
echo "============================================================================"

PORT="${1}"
if [ -z "$PORT" ]; then
    echo "[*] 未指定串口，正在自动扫描 ESP32-S3 设备..."
    PORT=$(python3 -c "import serial.tools.list_ports; ports=[p.device for p in serial.tools.list_ports.comports() if 'usb' in p.device.lower() or 'ttyacm' in p.device.lower()]; print(ports[0] if ports else '')" 2>/dev/null || true)
fi

if [ -z "$PORT" ]; then
    read -p "[-] 请输入串口设备路径 (例如 /dev/ttyACM0 或 /dev/tty.usbmodem1101): " PORT
fi

if [ -z "$PORT" ]; then
    echo "[ERROR] 未指定串口，退出。"
    exit 1
fi

echo "[+] 目标端口: $PORT"
echo "[*] 开始极速烧录 (1,500,000 Baud)..."

python3 -m esptool --chip esp32s3 --port "$PORT" --baud 1500000 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin || \
python3 -m esptool --chip esp32s3 --port "$PORT" --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin

echo "============================================================================"
echo "  [SUCCESS] 固件烧录成功！设备已自动重启。"
echo "  配网指引:"
echo "    1. 连接 Wi-Fi: StickS3-Buddy"
echo "    2. 访问: http://192.168.4.1"
echo "============================================================================"
