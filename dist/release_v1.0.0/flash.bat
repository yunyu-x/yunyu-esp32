@echo off
setlocal enabledelayedexpansion

echo ============================================================================
echo   M5Stack StickS3 Voice Buddy OS v1.0.0-stable 一键固件烧录工具
echo ============================================================================

set PORT=%1
if "%PORT%"=="" (
    echo [*] 未指定串口，正在自动扫描 ESP32-S3 串口设备...
    for /f "tokens=1" %%i in ('powershell -Command "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports() if p.device.upper() ne 'COM1']" 2^>nul') do (
        set PORT=%%i
    )
)

if "%PORT%"=="" (
    set /p PORT="[-] 未能自动检测到串口，请输入设备 COM 端口 (例如 COM3): "
)

if "%PORT%"=="" (
    echo [ERROR] 未提供有效端口，烧录退出。
    pause
    exit /b 1
)

echo [+] 目标端口: %PORT%
if not exist "firmware.bin" (
    echo.
    echo [-] 未在当前目录下检测到完整固件镜像 (firmware.bin / bootloader.bin / partitions.bin)。
    echo [*] 固件获取方式:
    echo     1. 前往 GitHub Releases (https://github.com/yunyu-x/yunyu-esp32/releases) 下载 release_v1.0.0 固件压缩包，解压后放置于本目录；
    echo     2. 或在项目根目录下直接运行本地编译烧录命令: python -m platformio run -e m5sticks3_buddy -t upload
    pause
    exit /b 1
)
echo [*] 开始极速烧录 (1,500,000 Baud)...
echo     - 0x0000: bootloader.bin
echo     - 0x8000: partitions.bin
echo     - 0x10000: firmware.bin

python -m esptool --chip esp32s3 --port %PORT% --baud 1500000 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin

if %errorlevel% neq 0 (
    echo.
    echo [-] 极速烧录失败，尝试以保守波特率 (460,800 Baud) 降速重试...
    python -m esptool --chip esp32s3 --port %PORT% --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin
)

if %errorlevel% equ 0 (
    echo.
    echo ============================================================================
    echo   [SUCCESS] 固件烧录成功！设备已自动重启。
    echo   配网指引:
    echo     1. 手机/电脑搜索并连接 Wi-Fi 热点: StickS3-Buddy
    echo     2. 浏览器打开: http://192.168.4.1
    echo     3. 选择家庭/办公 Wi-Fi，输入阿里云百炼 API-Key 即可开启全双工语音！
    echo ============================================================================
) else (
    echo.
    echo [ERROR] 烧录失败，请检查 USB 数据线是否连接稳固，或长按电源键复位重试。
)

pause
