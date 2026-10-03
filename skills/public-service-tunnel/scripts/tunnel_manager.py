"""
skills/public-service-tunnel/scripts/tunnel_manager.py
-----------------------------------------------------
通用化多通道公网内网穿透管理引擎 (Universal Public Service Tunnel Manager)

核心特性:
1. 多后端无缝支持:
   - ngrok (已配置 Token, 专属静态/动态域名)
   - cloudflare (Cloudflare Quick Tunnel, 免注册免配置零冲突)
   - auto 智能自愈路由 (优先 ngrok, 遇到域名冲突 ERR_NGROK_334 或故障时秒级降级至 Cloudflare)
2. 零安装感知:
   - 启动时自动检查 ngrok/cloudflared 二进制，若未就绪自动触发静默下载与权限配置
3. 本地服务生命周期伴侣:
   - 支持通过 --cmd 伴随拉起本地服务 (FastAPI, Flask, Gradio, Streamlit, Three.js 等)
   - 进程守护与一键级联销毁，杜绝孤儿进程与端口悬挂
4. 结构化地址持久化与自检:
   - 输出公网 HTTPS URL、本地 URL 与健康自检报告
   - 自动生成 public_preview_url.txt / public_preview_url.json
"""

import os
import sys
import time
import re
import json
import signal
import argparse
import subprocess
import urllib.request
import urllib.error

# 相对路径定位
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
DEFAULT_TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools", "bin")


def get_binary_path(tool_name: str, tools_dir: str) -> str:
    ext = ".exe" if sys.platform == "win32" else ""
    local_bin = os.path.join(tools_dir, f"{tool_name}{ext}")
    if os.path.exists(local_bin):
        return local_bin
    # 检查系统 PATH
    import shutil
    sys_bin = shutil.which(f"{tool_name}{ext}") or shutil.which(tool_name)
    if sys_bin:
        return sys_bin
    return local_bin


def ensure_tool_installed(tool_name: str, tools_dir: str):
    bin_path = get_binary_path(tool_name, tools_dir)
    if os.path.exists(bin_path):
        return bin_path

    print(f"[!] 未检测到 {tool_name}，正在自动安装至 {tools_dir}...")
    install_script = os.path.join(CURRENT_DIR, "install_tools.py")
    res = subprocess.run([sys.executable, install_script, "--tool", tool_name, "--dest", tools_dir])
    if res.returncode != 0 or not os.path.exists(bin_path):
        raise FileNotFoundError(f"自动安装 {tool_name} 失败，请检查网络或权限。")
    return bin_path


def is_port_listening(port: int) -> bool:
    try:
        url = f"http://127.0.0.1:{port}"
        with urllib.request.urlopen(url, timeout=1.0) as res:
            return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False


def start_companion_service(cmd_str: str, port: int, cwd: str = None) -> subprocess.Popen:
    if is_port_listening(port):
        print(f"[✓] 检测到端口 {port} 已有服务在运行。")
        return None

    print(f"[i] 正在启动伴随服务: {cmd_str}")
    proc = subprocess.Popen(
        cmd_str,
        shell=True,
        cwd=cwd or PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 等待端口就绪
    for _ in range(30):
        time.sleep(0.5)
        if is_port_listening(port):
            print(f"[✓] 本地服务已成功就绪 (PID: {proc.pid})。")
            return proc

    print(f"[WARN] 等待服务端口 {port} 响应超时，继续启动公网隧道...")
    return proc


def configure_ngrok_token(ngrok_bin: str, authtoken: str):
    print(f"[i] 正在配置 ngrok Authtoken...")
    cmd = [ngrok_bin, "config", "add-authtoken", authtoken]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"配置 ngrok Authtoken 失败: {res.stderr}")
    print("[✓] ngrok Authtoken 配置成功。")


def run_ngrok_tunnel(ngrok_bin: str, port: int, timeout: int = 15):
    print(f"[i] 正在启动 ngrok 隧道 (目标: 127.0.0.1:{port})...")
    proc = subprocess.Popen(
        [ngrok_bin, "http", str(port), "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT
    )

    start_time = time.time()
    public_url = None

    while time.time() - start_time < timeout:
        ret = proc.poll()
        if ret is not None:
            stdout, stderr = proc.communicate()
            combined = (stdout or "") + (stderr or "")
            if "ERR_NGROK_334" in combined or "already online" in combined:
                raise RuntimeError("ERR_NGROK_334: 专属域名已被其他进程或设备占用")
            raise RuntimeError(f"ngrok 退出 (Code {ret}):\n{combined}")

        try:
            req = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=1.0)
            data = json.loads(req.read().decode("utf-8"))
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                u = t.get("public_url")
                if u and u.startswith("https://"):
                    public_url = u
                    break
            if not public_url and tunnels:
                public_url = tunnels[0].get("public_url")
            if public_url:
                break
        except Exception:
            pass

        time.sleep(0.5)

    if not public_url:
        proc.terminate()
        raise TimeoutError("从 ngrok 本地接口获取公网 URL 超时")

    return proc, public_url


def run_cloudflared_tunnel(cf_bin: str, port: int, timeout: int = 25):
    print(f"[i] 正在启动 Cloudflare Quick Tunnel (目标: 127.0.0.1:{port})...")
    proc = subprocess.Popen(
        [cf_bin, "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT
    )

    start_time = time.time()
    public_url = None

    while time.time() - start_time < timeout:
        ret = proc.poll()
        if ret is not None:
            stdout, stderr = proc.communicate()
            raise RuntimeError(f"cloudflared 异常退出 (Code {ret}):\n{stderr}")

        line = proc.stderr.readline()
        if line:
            m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if m:
                public_url = m.group(0)
                break
        else:
            time.sleep(0.2)

    if not public_url:
        proc.terminate()
        raise TimeoutError("从 cloudflared 输出获取公网 URL 超时")

    return proc, public_url


def save_endpoints(out_dir: str, public_url: str, tool: str, port: int):
    os.makedirs(out_dir, exist_ok=True)
    txt_path = os.path.join(out_dir, "public_preview_url.txt")
    json_path = os.path.join(out_dir, "public_preview_url.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(public_url.strip() + "\n")

    info = {
        "tool": tool,
        "local_port": port,
        "public_url": public_url.strip(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)


def print_banner(public_url: str, tool: str, port: int, out_dir: str):
    sep = "=" * 72
    print("\n" + sep)
    print(f"  🌐 通用公网服务预览已就绪 (Unified Service Tunnel Online)")
    print(sep)
    print(f"  ▶ 穿透引擎:      {tool.upper()}")
    print(f"  ▶ 公网访问地址:  {public_url}")
    print(f"  ▶ 本地服务地址:  http://127.0.0.1:{port}")
    print(f"  ▶ 地址记录文件:  {os.path.join(out_dir, 'public_preview_url.txt')}")
    print(sep)
    if tool == "ngrok":
        print("  💡 提示: 浏览器首次访问 ngrok 免费域名时，点击 [Visit Site] 即可进入。")
    elif tool == "cloudflare":
        print("  ⚡ 提示: Cloudflare Quick Tunnel 全球 CDN 直连，免登录免证书警告。")
    print(sep + "\n")


def main():
    parser = argparse.ArgumentParser(description="通用多通道公网内网穿透管理引擎")
    parser.add_argument("--tool", choices=["auto", "ngrok", "cloudflare"], default="auto",
                        help="穿透工具选型: auto (智能自愈降级), ngrok, cloudflare")
    parser.add_argument("--port", type=int, default=8000, help="映射的本地服务端口 (默认: 8000)")
    parser.add_argument("--cmd", type=str, default=None, help="伴随启动本地服务的命令行 (可选)")
    parser.add_argument("--token", type=str, default=None, help="指定配置 ngrok authtoken (可选)")
    parser.add_argument("--tools-dir", type=str, default=DEFAULT_TOOLS_DIR, help="工具链存储目录")
    parser.add_argument("--out-dir", type=str, default=os.path.join(PROJECT_ROOT, "simulation", "outputs"),
                        help="公网 URL 输出记录目录")
    args = parser.parse_args()

    # 1. 确保工具已就绪
    tools_dir = os.path.abspath(args.tools_dir)
    os.makedirs(tools_dir, exist_ok=True)

    # 2. 如果提供了 ngrok token，执行配置
    if args.token:
        ngrok_bin = ensure_tool_installed("ngrok", tools_dir)
        configure_ngrok_token(ngrok_bin, args.token)

    # 3. 伴随启动本地服务
    service_proc = None
    if args.cmd:
        service_proc = start_companion_service(args.cmd, args.port)

    # 4. 启动穿透隧道
    tunnel_proc = None
    public_url = None
    chosen_tool = None

    if args.tool == "ngrok":
        ngrok_bin = ensure_tool_installed("ngrok", tools_dir)
        tunnel_proc, public_url = run_ngrok_tunnel(ngrok_bin, args.port)
        chosen_tool = "ngrok"
    elif args.tool == "cloudflare":
        cf_bin = ensure_tool_installed("cloudflared", tools_dir)
        tunnel_proc, public_url = run_cloudflared_tunnel(cf_bin, args.port)
        chosen_tool = "cloudflare"
    else:  # auto 模式
        print("[i] 自动模式: 优先尝试拉起 ngrok 专属域名隧道...")
        try:
            ngrok_bin = ensure_tool_installed("ngrok", tools_dir)
            tunnel_proc, public_url = run_ngrok_tunnel(ngrok_bin, args.port, timeout=8)
            chosen_tool = "ngrok"
        except Exception as e:
            print(f"[!] ngrok 未能建立连接 ({e})")
            print("[i] 正在无缝降级到 Cloudflare Quick Tunnel (零冲突高可用)...")
            cf_bin = ensure_tool_installed("cloudflared", tools_dir)
            tunnel_proc, public_url = run_cloudflared_tunnel(cf_bin, args.port)
            chosen_tool = "cloudflare"

    # 5. 持久化并打印信息
    save_endpoints(args.out_dir, public_url, chosen_tool, args.port)
    print_banner(public_url, chosen_tool, args.port, args.out_dir)

    # 6. 进程守护与优雅退出
    def cleanup():
        print("\n[*] 正在安全关闭公网隧道与伴随服务...")
        if tunnel_proc and tunnel_proc.poll() is None:
            tunnel_proc.terminate()
            try:
                tunnel_proc.wait(timeout=3)
            except Exception:
                tunnel_proc.kill()
        if service_proc and service_proc.poll() is None:
            service_proc.terminate()
            try:
                service_proc.wait(timeout=3)
            except Exception:
                service_proc.kill()
        print("[✓] 清理完成。")

    try:
        print("[*] 隧道保持运行中 (按 Ctrl+C 安全退出)...")
        while True:
            time.sleep(1)
            if tunnel_proc.poll() is not None:
                print("[!] 隧道已断开")
                break
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
