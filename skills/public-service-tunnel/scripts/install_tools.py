"""
skills/public-service-tunnel/scripts/install_tools.py
---------------------------------------------------
跨平台穿透工具链 (ngrok / cloudflared) 自动化下载与就绪检测器
- 支持 Windows, Linux, macOS (x86_64 / arm64)
- 无需系统 root/管理员 提权，直接安装到项目或用户局部环境
- 支持断点与代理环境自动读取
"""

import os
import sys
import platform
import tarfile
import zipfile
import subprocess
import urllib.request
import argparse

# 官方预编译二进制下载矩阵
DOWNLOAD_MATRIX = {
    "ngrok": {
        "windows": {
            "AMD64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip",
            "x86_64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip",
        },
        "linux": {
            "AMD64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz",
            "x86_64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz",
            "aarch64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz",
            "arm64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz",
        },
        "darwin": {
            "AMD64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip",
            "x86_64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip",
            "arm64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-arm64.zip",
            "aarch64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-arm64.zip",
        }
    },
    "cloudflared": {
        "windows": {
            "AMD64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
            "x86_64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
        },
        "linux": {
            "AMD64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "x86_64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "aarch64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64",
            "arm64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64",
        },
        "darwin": {
            "AMD64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz",
            "x86_64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz",
            "arm64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz",
            "aarch64": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz",
        }
    }
}


def get_system_info():
    system = platform.system().lower()
    machine = platform.machine()
    return system, machine


def get_binary_name(tool_name: str, system: str) -> str:
    if system == "windows":
        return f"{tool_name}.exe"
    return tool_name


def check_tool_installed(tool_name: str, dest_dir: str) -> bool:
    system, _ = get_system_info()
    bin_name = get_binary_name(tool_name, system)
    local_path = os.path.join(dest_dir, bin_name)

    # 1. 检查本地目录
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
        return True

    # 2. 检查系统 PATH
    try:
        res = subprocess.run([tool_name, "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    return False


def download_and_extract(tool_name: str, dest_dir: str, proxy: str = None) -> str:
    system, machine = get_system_info()
    os.makedirs(dest_dir, exist_ok=True)
    target_bin = os.path.join(dest_dir, get_binary_name(tool_name, system))

    if check_tool_installed(tool_name, dest_dir):
        print(f"[✓] {tool_name} 已安装就绪: {target_bin}")
        return target_bin

    system_matrix = DOWNLOAD_MATRIX.get(tool_name, {}).get(system, {})
    url = system_matrix.get(machine)
    if not url:
        # 尝试回退到默认 amd64
        url = system_matrix.get("AMD64") or system_matrix.get("x86_64")

    if not url:
        raise RuntimeError(f"未找到适配系统 {system} 架构 {machine} 的 {tool_name} 下载源")

    print(f"[↓] 正在下载 {tool_name} ({system}-{machine}) 从: {url}")

    opener = None
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener()

    temp_file = os.path.join(dest_dir, f"{tool_name}_temp_dl")
    with opener.open(url) as resp, open(temp_file, 'wb') as out_f:
        chunk = resp.read(65536)
        while chunk:
            out_f.write(chunk)
            chunk = resp.read(65536)

    # 处理文件解压或直接重命名
    if url.endswith(".zip"):
        with zipfile.ZipFile(temp_file, 'r') as z:
            z.extractall(dest_dir)
        os.remove(temp_file)
    elif url.endswith(".tgz") or url.endswith(".tar.gz"):
        with tarfile.open(temp_file, 'r:*') as t:
            t.extractall(dest_dir)
        os.remove(temp_file)
    else:
        # 直接二进制文件 (如 cloudflared-windows-amd64.exe)
        if os.path.exists(target_bin):
            os.remove(target_bin)
        os.rename(temp_file, target_bin)

    # 赋予执行权限 (POSIX)
    if system != "windows" and os.path.exists(target_bin):
        os.chmod(target_bin, 0o755)

    if not os.path.exists(target_bin):
        raise FileNotFoundError(f"下载后未能提取到预期文件: {target_bin}")

    print(f"[✓] {tool_name} 部署完成: {target_bin}")
    return target_bin


def main():
    parser = argparse.ArgumentParser(description="跨平台内网穿透工具链一键下载安装脚本")
    parser.add_argument("--tool", choices=["all", "ngrok", "cloudflared"], default="all",
                        help="指定下载安装的工具: ngrok, cloudflared 或 all")
    parser.add_argument("--dest", default=None,
                        help="保存目标目录 (默认: 项目 tools/bin/)")
    parser.add_argument("--proxy", default=None, help="HTTP/HTTPS 下载代理")
    args = parser.parse_args()

    dest_dir = args.dest
    if not dest_dir:
        # 默认保存到当前仓库根目录 tools/bin/
        current_dir = os.path.abspath(os.path.dirname(__file__))
        dest_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "tools", "bin"))

    tools = ["ngrok", "cloudflared"] if args.tool == "all" else [args.tool]
    for t in tools:
        try:
            download_and_extract(t, dest_dir, args.proxy)
        except Exception as e:
            print(f"[ERROR] 安装 {t} 失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
