"""
scripts/preview_tunnel.py
-------------------------
yunyu-esp32 跨公网在线效果预览与内网穿透集成管理工具

功能特性:
1. 支持多种穿透方案:
   - ngrok: 使用官方 ngrok 隧道 (已预置工具 bin)
   - cloudflare: Cloudflare Quick Tunnel (零配置、免登录、即开即用、无并发冲突)
   - auto: 智能模式 (优先尝试 ngrok，若被其他实例占用则自动无缝降级至 cloudflare)
2. 自动化服务生命周期管理:
   - 自动检测 8000 端口服务是否已启动，未启动时自动拉起 scripts/lingbuddy_companion.py
3. 实时输出标准公网访问地址与功能导航:
   - LingBuddy 隔空投喂与 Web 伴侣控制台
   - 实时遥测与微表情交互
4. 将当前活动公网 URL 持久化输出至 dist/public_preview_url.txt
"""

import os
import sys
import time
import re
import json
import argparse
import subprocess
import urllib.request
import urllib.error

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_BIN_DIR = os.path.join(WORKSPACE_DIR, "tools", "bin")
NGROK_BIN = os.path.join(TOOLS_BIN_DIR, "ngrok.exe")
CLOUDFLARED_BIN = os.path.join(TOOLS_BIN_DIR, "cloudflared.exe")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "dist")
URL_FILE_TXT = os.path.join(OUTPUT_DIR, "public_preview_url.txt")
URL_FILE_JSON = os.path.join(OUTPUT_DIR, "public_preview_url.json")


def is_service_alive(port: int = 8000) -> bool:
    """检测本地指定端口的服务是否正常响应"""
    try:
        url = f"http://127.0.0.1:{port}"
        with urllib.request.urlopen(url, timeout=1.5) as res:
            return res.status in (200, 301, 302, 404)
    except Exception:
        return False


def ensure_backend_service(port: int = 8000):
    """确保伴侣 Web 控制台服务运行中"""
    if is_service_alive(port):
        print(f"[✓] 检测到本地伴侣控制台服务已在端口 {port} 正常运行。")
        return None

    print(f"[!] 端口 {port} 未检测到服务，正在自动拉起 scripts/lingbuddy_companion.py...")
    server_script = os.path.join(WORKSPACE_DIR, "scripts", "lingbuddy_companion.py")
    proc = subprocess.Popen(
        [sys.executable, server_script],
        cwd=WORKSPACE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(20):
        time.sleep(0.5)
        if is_service_alive(port):
            print(f"[✓] 本地伴侣控制台服务器已成功启动 (PID: {proc.pid})。")
            return proc

    print("[WARN] 等待本地服务启动超时，继续尝试启动穿透隧道...")
    return proc


def save_public_url(public_url: str, tool: str, local_port: int):
    """保存公网地址至输出文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(URL_FILE_TXT, "w", encoding="utf-8") as f:
        f.write(public_url.strip() + "\n")

    info = {
        "tool": tool,
        "local_port": local_port,
        "public_url": public_url.strip(),
        "companion_url": f"{public_url.rstrip('/')}/",
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(URL_FILE_JSON, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)


def print_banner(public_url: str, tool: str, local_port: int):
    """打印公网预览控制台横幅"""
    sep = "=" * 70
    print("\n" + sep)
    print(f" 🚀 yunyu-esp32 灵伴·悄悄在线效果预览已就绪 [{tool.upper()}]")
    print(sep)
    print(f" ▶ 公网伴侣控制台:   {public_url}")
    print(f" ▶ 本地局域网地址:   http://127.0.0.1:{local_port}")
    print(f" ▶ 地址已保存至:     dist/public_preview_url.txt")
    print(sep)
    if tool == "ngrok":
        print(" 💡 提示: 首次通过浏览器访问 ngrok 免费域名时，可能会弹出一次")
        print("         ngrok 安全确认页面，点击 [Visit Site] 按钮即可正常进入。")
    print(sep + "\n")


def start_ngrok(port: int = 8000, timeout: int = 15):
    """启动 ngrok 隧道并捕获公网 URL"""
    if not os.path.exists(NGROK_BIN):
        raise FileNotFoundError(f"未找到 ngrok 可执行文件: {NGROK_BIN}")

    print(f"[i] 正在启动 ngrok 隧道 (本地映射: 127.0.0.1:{port})...")
    proc = subprocess.Popen(
        [NGROK_BIN, "http", str(port), "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=WORKSPACE_DIR
    )

    public_url = None
    start_time = time.time()

    while time.time() - start_time < timeout:
        ret = proc.poll()
        if ret is not None:
            stdout, stderr = proc.communicate()
            combined = (stdout or "") + (stderr or "")
            if "ERR_NGROK_334" in combined or "already online" in combined:
                raise RuntimeError("NGROK_ENDPOINT_OCCUPIED: 该账户专属域名当前已被其他进程/设备占用")
            raise RuntimeError(f"ngrok 启动失败退出 (Code {ret}):\n{combined}")

        try:
            req = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=1.0)
            data = json.loads(req.read().decode("utf-8"))
            tunnels = data.get("tunnels", [])
            if tunnels:
                for t in tunnels:
                    url = t.get("public_url")
                    if url and url.startswith("https://"):
                        public_url = url
                        break
                if not public_url and tunnels:
                    public_url = tunnels[0].get("public_url")
                if public_url:
                    break
        except Exception:
            pass

        time.sleep(0.5)

    if not public_url:
        proc.kill()
        raise TimeoutError("ngrok 在指定时间内未能建立隧道或未能获取公网 URL")

    return proc, public_url


def start_cloudflare(port: int = 8000, timeout: int = 25):
    """启动 Cloudflare Quick Tunnel 并捕获公网 URL"""
    if not os.path.exists(CLOUDFLARED_BIN):
        raise FileNotFoundError(f"未找到 cloudflared 可执行文件: {CLOUDFLARED_BIN}")

    print(f"[i] 正在启动 Cloudflare Quick Tunnel (本地映射: 127.0.0.1:{port})...")
    proc = subprocess.Popen(
        [CLOUDFLARED_BIN, "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=WORKSPACE_DIR
    )

    public_url = None
    start_time = time.time()
    url_pattern = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")

    while time.time() - start_time < timeout:
        ret = proc.poll()
        if ret is not None:
            output = proc.stdout.read()
            raise RuntimeError(f"cloudflared 进程异常退出 (Code {ret}):\n{output}")

        line = proc.stdout.readline()
        if line:
            match = url_pattern.search(line)
            if match:
                public_url = match.group(0)
                break

    if not public_url:
        proc.kill()
        raise TimeoutError("Cloudflare 隧道未能捕获到 trycloudflare.com 公网地址")

    return proc, public_url


def main():
    parser = argparse.ArgumentParser(description="yunyu-esp32 公网在线预览与内网穿透管理工具")
    parser.add_argument("--tool", choices=["auto", "ngrok", "cloudflare"], default="auto",
                        help="选择内网穿透工具 (默认: auto 优先尝试 ngrok，被占用则降级为 cloudflare)")
    parser.add_argument("--port", type=int, default=8000, help="本地服务端口 (默认: 8000)")
    parser.add_argument("--no-launch", action="store_true", help="不自动拉起后端伴侣服务")
    args = parser.parse_args()

    backend_proc = None
    if not args.no_launch:
        backend_proc = ensure_backend_service(args.port)

    tunnel_proc = None
    chosen_tool = None
    public_url = None

    try:
        if args.tool in ("auto", "ngrok"):
            try:
                tunnel_proc, public_url = start_ngrok(args.port)
                chosen_tool = "ngrok"
            except Exception as e:
                if args.tool == "ngrok":
                    raise e
                print(f"[!] ngrok 启动异常 ({e})，正在自动无缝降级至 Cloudflare Quick Tunnel...")

        if not public_url and args.tool in ("auto", "cloudflare"):
            tunnel_proc, public_url = start_cloudflare(args.port)
            chosen_tool = "cloudflare"

        if not public_url:
            print("[x] 启动穿透隧道失败，未能获取公网访问地址。")
            sys.exit(1)

        save_public_url(public_url, chosen_tool, args.port)
        print_banner(public_url, chosen_tool, args.port)

        print("[*] 隧道已稳定保持。按 Ctrl+C 可安全终止隧道并退出...")
        while True:
            time.sleep(1)
            if tunnel_proc and tunnel_proc.poll() is not None:
                print("[!] 穿透隧道进程意外终止。")
                break

    except KeyboardInterrupt:
        print("\n[*] 接收到用户中断信号 (Ctrl+C)，正在优雅退出...")
    finally:
        if tunnel_proc and tunnel_proc.poll() is None:
            print("[*] 正在关闭穿透隧道进程...")
            tunnel_proc.terminate()
            try:
                tunnel_proc.wait(timeout=3)
            except Exception:
                tunnel_proc.kill()

        if backend_proc and backend_proc.poll() is None:
            print("[*] 正在关闭伴侣后端服务...")
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=3)
            except Exception:
                backend_proc.kill()

        print("[✓] 清理完毕，已退出。")


if __name__ == "__main__":
    main()
