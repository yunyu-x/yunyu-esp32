"""
skills/public-service-tunnel/scripts/service_probe.py
---------------------------------------------------
公网预览服务健康检测与连通性探针
- 自动检测 HTTP 状态码与响应延迟 (RTT)
- 适配 ngrok 免费版跳过浏览器安全警告头 (ngrok-skip-browser-warning)
- 检测关键页面可用性 (主页、静态资源、API 文档等)
- 输出结构化自检报告
"""

import sys
import time
import json
import argparse
import urllib.request
import urllib.error


def probe_endpoint(url: str, timeout: float = 5.0, skip_ngrok_warning: bool = True) -> dict:
    start_t = time.time()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PublicTunnelProbe/1.0",
    }
    if skip_ngrok_warning:
        headers["ngrok-skip-browser-warning"] = "true"

    result = {
        "url": url,
        "alive": False,
        "status_code": 0,
        "latency_ms": 0.0,
        "content_length": 0,
        "title": "",
        "error": None
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as res:
            rtt = (time.time() - start_t) * 1000.0
            result["alive"] = (res.status in (200, 201, 204, 301, 302, 304))
            result["status_code"] = res.status
            result["latency_ms"] = round(rtt, 2)
            
            raw_body = res.read(2048).decode("utf-8", errors="ignore")
            result["content_length"] = len(raw_body)

            # 简易提取 HTML title
            if "<title>" in raw_body and "</title>" in raw_body:
                t_start = raw_body.index("<title>") + 7
                t_end = raw_body.index("</title>")
                result["title"] = raw_body[t_start:t_end].strip()

    except urllib.error.HTTPError as he:
        result["status_code"] = he.code
        result["error"] = f"HTTPError {he.code}: {he.reason}"
    except Exception as ex:
        result["error"] = str(ex)

    return result


def main():
    parser = argparse.ArgumentParser(description="公网/本地服务探针工具")
    parser.add_argument("url", help="待探测的 URL 地址 (如 http://127.0.0.1:8000 或 https://xxx.trycloudflare.com)")
    parser.add_argument("--timeout", type=float, default=5.0, help="请求超时时间 (秒)")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    args = parser.parse_args()

    res = probe_endpoint(args.url, timeout=args.timeout)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print(" 🛰️ 服务连通性探测结果")
        print("=" * 60)
        print(f"目标地址:   {res['url']}")
        print(f"存活状态:   {'[✓] 正常在线' if res['alive'] else '[✗] 无法访问'}")
        print(f"HTTP 状态:  {res['status_code']}")
        print(f"响应延迟:   {res['latency_ms']} ms")
        if res['title']:
            print(f"网页标题:   {res['title']}")
        if res['error']:
            print(f"错误详情:   {res['error']}")
        print("=" * 60)

    if not res["alive"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
