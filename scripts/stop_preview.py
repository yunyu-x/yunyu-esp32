"""
scripts/stop_preview.py
-----------------------
一键停止 yunyu-esp32 相关的本地伴侣服务器与公网穿透服务 (ngrok, cloudflared)
"""

import os
import psutil

def stop_services():
    stopped = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = (p.info['name'] or '').lower()
            cmdline = ' '.join(p.info['cmdline'] or []).lower()
            
            # 停止穿透隧道进程
            if 'cloudflared' in name or 'ngrok' in name:
                p.kill()
                stopped.append(f"{p.info['name']} (PID: {p.info['pid']})")
            
            # 停止伴侣服务器与预览脚本
            elif 'python' in name and any(k in cmdline for k in ['lingbuddy_companion.py', 'preview_tunnel.py', 'simulation/server.py', 'simulation\\server.py']):
                p.kill()
                stopped.append(f"Python Service (PID: {p.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if stopped:
        print("[✓] 成功终止以下服务与隧道进程:")
        for item in stopped:
            print(f"    - {item}")
    else:
        print("[i] 当前没有正在运行的相关服务或穿透进程。")

    # 清理预览地址记录
    for rel_path in ["dist/public_preview_url.txt", "dist/public_preview_url.json", "web_preview/public_preview_url.txt", "web_preview/public_preview_url.json"]:
        url_file = os.path.join(os.path.dirname(__file__), "..", rel_path)
        if os.path.exists(url_file):
            try:
                os.remove(url_file)
                print(f"[✓] 已清理旧的 {rel_path}。")
            except Exception:
                pass

if __name__ == "__main__":
    stop_services()

