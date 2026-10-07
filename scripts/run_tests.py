#!/usr/bin/env python3
"""
scripts/run_tests.py
--------------------
yunyu-esp32 统一测试运行快捷入口 (自带进度与超时守护)
用法：
  python scripts/run_tests.py
  python scripts/run_tests.py --timeout 90
  python scripts/run_tests.py -k "kinematics or posture"
"""
import sys
import os

# 确保脚本目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_tests_with_progress import parse_args, run_tests_with_live_progress

if __name__ == "__main__":
    args = parse_args()
    code = run_tests_with_live_progress(
        target=args.target,
        total_timeout=args.timeout,
        freeze_timeout=args.freeze_timeout,
        filter_expr=args.filter
    )
    sys.exit(code)
