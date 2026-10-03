"""
skills/public-service-tunnel/examples/quick_start.py
----------------------------------------------------
在任何 Python 项目中嵌入公网预览功能的极简示例
"""

import os
import sys

# 导入 skill 脚本模块
SKILL_SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, SKILL_SCRIPTS)

from tunnel_manager import ensure_tool_installed, run_cloudflared_tunnel, print_banner

def main():
    port = 8000
    tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "bin"))
    
    print(f"[1/2] 确保穿透工具可用...")
    cf_bin = ensure_tool_installed("cloudflared", tools_dir)

    print(f"[2/2] 启动 Cloudflare Quick Tunnel 映射至端口 {port}...")
    proc, public_url = run_cloudflared_tunnel(cf_bin, port)
    
    print_banner(public_url, "cloudflare", port, ".")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("已退出")

if __name__ == "__main__":
    main()
