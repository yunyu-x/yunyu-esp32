#!/usr/bin/env python3
"""
scripts/run_tests_with_progress.py
-----------------------------------
yunyu-esp32 统一自动化测试运行器 (实时进度展示 + 双重超时熔断守护)

功能特性：
1. 实时流式进度反馈：无缓冲逐行解析 pytest 输出，实时展示 [当前进度/总数 | 百分比]、测试名与耗时。
2. 双重超时熔断机制：
   - 全局执行超时 (默认 120 秒，可通过 --timeout 设置)
   - 单测试卡死/无响应检测 (默认 20 秒无日志即判定为 Freeze 并安全终止)
3. 遵循 Constitutional Axiom 5 (Non-Regression Law)：全量回归测试必须 100% 绿色通过。
"""

import sys
import os
import time
import re
import argparse
import subprocess
from datetime import datetime

# 保证当前标准输出不被缓冲
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)


def parse_args():
    parser = argparse.ArgumentParser(description="yunyu-esp32 统一自动化测试运行器 (实时进度 + 超时熔断)")
    parser.add_argument("--timeout", type=int, default=120, help="全量测试最大执行超时时间 (秒)，默认 120s")
    parser.add_argument("--freeze-timeout", type=int, default=25, help="单测试最大静默/卡死判定超时 (秒)，默认 25s")
    parser.add_argument("--target", type=str, default="tests/", help="目标测试路径或文件，默认 tests/")
    parser.add_argument("-k", "--filter", type=str, default="", help="pytest -k 过滤表达式")
    return parser.parse_args()


def format_progress_bar(pct, length=24):
    filled = int(length * pct / 100)
    bar = "█" * filled + "░" * (length - filled)
    return bar


def run_tests_with_live_progress(target="tests/", total_timeout=120, freeze_timeout=25, filter_expr=""):
    print("=" * 72)
    print("🧪  yunyu-esp32 统一测试运行中枢 (实时进度 + 超时守护)")
    print(f"⏱️   全局超时设定: {total_timeout}s | 防卡死守护: {freeze_timeout}s | 目标目录: {target}")
    print(f"📅  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)
    sys.stdout.flush()

    cmd = [sys.executable, "-u", "-m", "pytest", target, "-v", "--durations=10"]
    if filter_expr:
        cmd.extend(["-k", filter_expr])

    start_time = time.time()
    last_output_time = time.time()

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    total_collected = 0
    passed_count = 0
    failed_count = 0
    skipped_count = 0
    current_index = 0

    re_collected = re.compile(r"collected (\d+) items?")
    re_test_line = re.compile(r"^(tests/[^:\s]+::[^\s]+)\s+(PASSED|FAILED|SKIPPED|XFAIL|XPASS)\s+\[\s*(\d+)%\]")
    re_failure_start = re.compile(r"^=+ FAILURES =+")

    failure_log_buffer = []
    in_failure_section = False

    while True:
        # 1. 检查全局超时
        elapsed = time.time() - start_time
        if elapsed > total_timeout:
            process.kill()
            print(f"\n❌ [FATAL TIMEOUT] 全量测试执行超过全局限定时间 ({total_timeout}s)，已安全终止进程！")
            sys.stdout.flush()
            return 124

        # 2. 检查单测试卡死 (无日志超时)
        silent_time = time.time() - last_output_time
        if silent_time > freeze_timeout:
            process.kill()
            print(f"\n❌ [FREEZE DETECTED] 测试管道连续 {freeze_timeout}s 无任何日志输出，判定为挂起死锁，已安全终止！")
            sys.stdout.flush()
            return 125

        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            time.sleep(0.05)
            continue

        last_output_time = time.time()
        line_clean = line.strip()

        # 解析搜集到的测试项总数
        m_coll = re_collected.search(line_clean)
        if m_coll:
            total_collected = int(m_coll.group(1))
            print(f"📦 已发现并载入 {total_collected} 个自动化测试用例，开始逐项执行...\n")
            sys.stdout.flush()
            continue

        # 解析单个测试通过/失败行
        m_test = re_test_line.search(line_clean)
        if m_test:
            test_node = m_test.group(1)
            status = m_test.group(2)
            pct = int(m_test.group(3))
            current_index += 1

            if status == "PASSED":
                passed_count += 1
                status_icon = "✅ PASS"
            elif status == "FAILED":
                failed_count += 1
                status_icon = "❌ FAIL"
            else:
                skipped_count += 1
                status_icon = "⚠️ SKIP"

            bar = format_progress_bar(pct, length=20)
            elapsed_cur = time.time() - start_time
            print(f"[{bar} {pct:3d}% | {current_index:3d}/{total_collected or '?'}] {status_icon} | {test_node} (+{elapsed_cur:.1f}s)")
            sys.stdout.flush()
            continue

        # 捕获失败堆栈段
        if re_failure_start.search(line_clean):
            in_failure_section = True

        if in_failure_section:
            failure_log_buffer.append(line_clean)

    process.wait()
    total_duration = time.time() - start_time

    print("\n" + "=" * 72)
    print("📊  测试执行汇总报告")
    print(f"• 耗时: {total_duration:.2f} 秒 (全局限额: {total_timeout}s)")
    print(f"• 总计发现: {total_collected} 项")
    print(f"• 成功通过: {passed_count} 项")
    if failed_count > 0:
        print(f"• 失败用例: {failed_count} 项 ❌")
    if skipped_count > 0:
        print(f"• 略过用例: {skipped_count} 项")

    pass_rate = (passed_count / total_collected * 100.0) if total_collected > 0 else 0.0
    print(f"• 测试通过率: {pass_rate:.1f}%")
    print("=" * 72)
    sys.stdout.flush()

    if failed_count > 0:
        print("\n💥  [失败用例错误详情]:")
        for f_line in failure_log_buffer[:80]:
            print("  ", f_line)
        if len(failure_log_buffer) > 80:
            print("   ... (更多失败详情已省略)")
        sys.stdout.flush()
        return 1

    if process.returncode == 0:
        print("🎉  [验收通过] 100% 自动化测试全绿通过，完全符合公理五零功能回退法则！")
        sys.stdout.flush()
        return 0
    else:
        print(f"⚠️  测试子进程退出码非零: {process.returncode}")
        sys.stdout.flush()
        return process.returncode


if __name__ == "__main__":
    args = parse_args()
    code = run_tests_with_live_progress(
        target=args.target,
        total_timeout=args.timeout,
        freeze_timeout=args.freeze_timeout,
        filter_expr=args.filter
    )
    sys.exit(code)
