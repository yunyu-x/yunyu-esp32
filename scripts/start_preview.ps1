# scripts/start_preview.ps1
# yunyu-esp32 (LingBuddy 灵宠伴侣) 一键启动桌面伴侣服务与公网在线预览隧道

param (
    [string]$Tool = "auto",
    [int]$Port = 8000
)

$PSScriptRoot_ = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Workspace = Split-Path -Parent $PSScriptRoot_

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 🚀 yunyu-esp32 一键启动 LingBuddy 伴侣服务与公网隧道" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

python "$Workspace\scripts\preview_tunnel.py" --tool $Tool --port $Port
