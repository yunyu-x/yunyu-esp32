@echo off
REM scripts/start_preview.bat
REM yunyu-esp32 (LingBuddy 灵宠伴侣) 一键启动桌面伴侣服务与公网在线预览隧道

cd /d "%~dp0\.."
echo ==========================================================
echo  [yunyu-esp32] 正在启动 LingBuddy 桌面伴侣服务与公网预览隧道...
echo ==========================================================
python scripts\preview_tunnel.py --tool auto --port 8000
pause

