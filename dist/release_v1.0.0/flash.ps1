param (
    [string]$Port = ""
)

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  M5Stack StickS3 Voice Buddy OS v1.0.0-stable 一键固件烧录工具 (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

if (-not $Port) {
    Write-Host "[*] 正在扫描系统 ESP32 串口..." -ForegroundColor Yellow
    $detected = python -c "import serial.tools.list_ports; ports=[p.device for p in serial.tools.list_ports.comports() if p.device.upper() != 'COM1']; print(ports[0] if ports else '')" 2>$null
    if ($detected) {
        $Port = $detected.Trim()
    }
}

if (-not $Port) {
    $Port = Read-Host "[-] 未能自动检测到串口，请输入设备 COM 端口 (例如 COM3)"
}

if (-not $Port) {
    Write-Error "未提供有效端口，退出。"
    exit 1
}

Write-Host "[+] 目标端口: $Port" -ForegroundColor Green
Write-Host "[*] 开始高速烧录 (1,500,000 Baud)..." -ForegroundColor Yellow

$flashCmd = "python -m esptool --chip esp32s3 --port $Port --baud 1500000 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin"
Invoke-Expression $flashCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[-] 极速烧录失败，尝试降速至 460800 Baud 重试..." -ForegroundColor Yellow
    $retryCmd = "python -m esptool --chip esp32s3 --port $Port --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin"
    Invoke-Expression $retryCmd
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================================================" -ForegroundColor Green
    Write-Host "  [SUCCESS] 固件烧录成功！设备已自动重启。" -ForegroundColor Green
    Write-Host "  配网指引:" -ForegroundColor Green
    Write-Host "    1. 手机/电脑搜索并连接 Wi-Fi 热点: StickS3-Buddy" -ForegroundColor Green
    Write-Host "    2. 浏览器打开: http://192.168.4.1" -ForegroundColor Green
    Write-Host "    3. 输入 Wi-Fi 密码与阿里云百炼 API-Key 即可开启全双工语音！" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] 烧录失败，请检查硬件连接与驱动。" -ForegroundColor Red
}
