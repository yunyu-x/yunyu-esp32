#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/stress_test_miniprogram_30min.py
===========================================================================
Python launcher for WeChat Mini-Program 30-Minute Continuous Stress Test.
Spawns Node.js execution of stress_test_miniprogram_30min.js with real-time
unbuffered terminal streaming and exit code verification.
"""

import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="WeChat Mini-Program 30-Minute Continuous Stress Test Harness")
    parser.add_argument("--duration", type=int, default=1800, help="Test duration in seconds (default: 1800 = 30 min)")
    parser.add_argument("--output", type=str, default="dist/stress_test_mp_report_30m.json", help="Report output path")
    parser.add_argument("--host", type=str, default="192.168.110.67", help="Target hardware WiFi IP (default: 192.168.110.67)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    js_script = os.path.join(script_dir, "stress_test_miniprogram_30min.js")

    cmd = [
        "node",
        "--expose-gc",
        js_script,
        "--duration", str(args.duration),
        "--output", os.path.join(root_dir, args.output),
        "--host", args.host
    ]

    print(f"[LAUNCHER] Running Mini-Program stress test for {args.duration}s ({args.duration/60:.1f} mins)...")
    res = subprocess.run(cmd, cwd=root_dir)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
