#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/bear_pose_director.py
-----------------------------
M5Stack StickS3 元气小熊姿态控制与动画导播台 (Bear Pose Director)
提供交互式全套动作点播、姿态自动阅兵巡礼、升级庆典以及三方多体舞步联动。
"""

import sys
import time
import threading
import argparse

try:
    import serial
except ImportError:
    print("错误: 需要 pyserial 库。请运行: pip install pyserial")
    sys.exit(1)

ACTIONS_MENU = [
    ("1",  "wave",          "元气挥手 (wave)"),
    ("2",  "bow",           "作揖鞠躬 (bow)"),
    ("3",  "cheer",         "欢呼雀跃 (cheer)"),
    ("4",  "clap",          "鼓掌拍手 (clap)"),
    ("5",  "stretch",       "伸大懒腰 (stretch)"),
    ("6",  "sit",           "呆萌坐下 (sit)"),
    ("7",  "jump",          "弹性跳跃 (jump)"),
    ("8",  "balance",       "金鸡独立 (balance)"),
    ("9",  "taichi",        "太极云手 (taichi)"),
    ("10", "wingchun",      "咏春快拳 (wingchun)"),
    ("11", "kungfu",        "中国功夫 (kungfu)"),
    ("12", "dragon_punch",  "升龙霸天 (dragon_punch)"),
    ("13", "moonwalk",      "太空漫步 (moonwalk)"),
    ("14", "cyber_defense", "机甲护盾 (cyber_defense)"),
    ("15", "turn_around",   "转身秀尾 (turn_around)"),
    ("16", "spin",          "华丽自旋 (spin)"),
    ("17", "locked_try",    "困惑挠头 (locked_try)"),
]

def print_banner():
    print("\n" + "=" * 66)
    print(" 🐻  M5StickS3 元气小熊姿态控制导播台 (Bear Pose Director)  🐻")
    print("=" * 66)
    for i in range(0, len(ACTIONS_MENU), 2):
        left = f" [{ACTIONS_MENU[i][0]:>2}] {ACTIONS_MENU[i][2]:<24}"
        right = ""
        if i + 1 < len(ACTIONS_MENU):
            right = f" [{ACTIONS_MENU[i+1][0]:>2}] {ACTIONS_MENU[i+1][2]:<24}"
        print(f"{left} {right}")
    print("-" * 66)
    print(" [D] 开启/停止姿态自动阅兵 (Auto Demo)    [N] 单步切换下一个动作 (Next)")
    print(" [L] 触发升级庆典 (Level Up)              [W] 编队元气华尔兹 (Waltz)")
    print(" [Z] 编队太极云手阵 (Zen)                 [Q] 退出导播台")
    print("=" * 66)

def serial_reader_thread(ser, stop_event):
    while not stop_event.is_set():
        try:
            line = ser.readline().decode("utf-8", errors="replace").strip()
            if line:
                if line.startswith("@action") or line.startswith("@demo") or line.startswith("@ceremony") or line.startswith("@dance_swarm"):
                    print(f"\n✨ [设备反馈] >>> {line}")
                elif "FPS:" in line or "[StickS3-SYS]" in line:
                    # 紧凑状态提示
                    print(f"📊 {line}")
        except Exception:
            break

def main():
    parser = argparse.ArgumentParser(description="StickS3 Bear Pose Director")
    parser.add_argument("--port", default="COM3", help="Serial port (default: COM3)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--demo", action="store_true", help="Launch directly into auto demo tour")
    args = parser.parse_args()

    print(f"正在连接 M5Stack StickS3 设备 ({args.port} @ {args.baud})...")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.2)
    except Exception as e:
        print(f"❌ 无法打开串口 {args.port}: {e}")
        print("请检查设备是否连接或是否被其他串口监视程序占用。")
        return 1

    time.sleep(0.3)
    stop_event = threading.Event()
    reader = threading.Thread(target=serial_reader_thread, args=(ser, stop_event), daemon=True)
    reader.start()

    print_banner()

    if args.demo:
        print("🚀 启动直接姿态阅兵模式...")
        ser.write(b">demo\n")

    act_dict = {key: cmd for key, cmd, _ in ACTIONS_MENU}

    try:
        while True:
            prompt = "\n🎮 请输入指令 (数字序号 / D / N / L / W / Z / Q): "
            user_input = input(prompt).strip().lower()
            if not user_input:
                continue

            if user_input in ("q", "quit", "exit"):
                print("正在退出导播台...")
                break
            elif user_input in ("d", "demo", "tour"):
                print("🔄 切换姿态自动阅兵巡礼模式...")
                ser.write(b">demo\n")
            elif user_input in ("n", "next", "step"):
                print("⏭ 切换至下一个动作姿态...")
                ser.write(b">next\n")
            elif user_input in ("l", "levelup", "ceremony"):
                print("🎉 触发技能解锁升级盛典...")
                ser.write(b">levelup\n")
            elif user_input in ("w", "waltz"):
                print("💃 触发三方编队元气华尔兹舞步...")
                ser.write(b">dance_swarm=waltz\n")
            elif user_input in ("z", "zen"):
                print("🥋 触发三方编队太极云手阵舞步...")
                ser.write(b">dance_swarm=zen\n")
            elif user_input in act_dict:
                act_name = act_dict[user_input]
                print(f"🎬 触发动作: {act_name}")
                cmd = f">action={act_name}\n"
                ser.write(cmd.encode("utf-8"))
            elif user_input.startswith(">"):
                # 原生透传指令
                cmd = f"{user_input}\n"
                ser.write(cmd.encode("utf-8"))
            else:
                # 尝试当作动作名称直接发送
                cmd = f">action={user_input}\n"
                ser.write(cmd.encode("utf-8"))

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n捕获中断信号，正在退出...")
    finally:
        stop_event.set()
        ser.close()
        print("串口已安全释放。")

    return 0

if __name__ == "__main__":
    sys.exit(main())
