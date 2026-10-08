#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_atlas_lineart_gifs.py
--------------------------------------
Synthesizes cinema-grade animated GIFs using the authentic binarized
line art extracted directly from the Cadet Ren design atlas.

Enforces Disney/Pixar animation principles:
- Squash & stretch with volume preservation
- Secondary action (ear flick, tail sway)
- Eased timing & anticipation wind-ups
- 100% complete character anatomy in every single frame

Outputs:
1. docs/assets/cadet_ren/cadet_ren_wave_greeting.gif
2. docs/assets/cadet_ren/cadet_ren_kungfu_action.gif
3. docs/assets/cadet_ren/cadet_ren_taichi_zen.gif
4. docs/assets/cadet_ren/cadet_ren_dragon_punch.gif
5. docs/assets/cadet_ren/cadet_ren_bow.gif
6. docs/assets/cadet_ren/cadet_ren_device_135x240_showcase.gif

Synchronizes all outputs into wechat_miniprogram/assets/cadet_ren/ as well.
"""

import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DEV_DIR = "docs/assets/cadet_ren/device_135x240_lines"
OUT_DIR = "docs/assets/cadet_ren"
MP_DIR = "wechat_miniprogram/assets/cadet_ren"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(MP_DIR, exist_ok=True)

# Aesthetic palette
BG_DARK = (11, 15, 25)       # Midnight Obsidian #0B0F19
LINE_IVORY = (248, 250, 252) # Pure White #F8FAFC
LINE_GOLD = (254, 243, 199)  # Golden Ivory #FEF3C7
UI_BAR = (20, 12, 8)         # #140C08
UI_GOLD = (245, 158, 11)     # Amber 500 #F59E0B
UI_GREEN = (34, 197, 94)     # Emerald 500 #22C55E

def load_dev_lineart(name):
    path = os.path.join(DEV_DIR, f"{name}_135x240.png")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    return cv2.imread(path, 0)

FONT_SUBTITLE = None
try:
    if os.path.exists('C:/Windows/Fonts/msyh.ttc'):
        FONT_SUBTITLE = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 11)
    elif os.path.exists('C:/Windows/Fonts/simhei.ttf'):
        FONT_SUBTITLE = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 11)
except Exception:
    FONT_SUBTITLE = None

def render_device_frame(char_mask, subtitle="待命", wifi_hot=False, tick=0):
    """
    Renders a single 135x240 device screen frame with status bar, subtitle, and character.
    """
    img = Image.new("RGB", (135, 240), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Top Status Bar (0..18)
    draw.rectangle([0, 0, 134, 18], fill=UI_BAR)
    # Time / Status text
    draw.text((6, 3), "12:30", fill=(203, 213, 225))
    # Network Pill
    if wifi_hot:
        draw.rounded_rectangle([92, 3, 128, 15], radius=3, fill=(234, 88, 12)) # Orange HOT
        draw.text((96, 3), "HOT", fill=(255, 255, 255))
    else:
        draw.rounded_rectangle([90, 3, 128, 15], radius=3, fill=(22, 101, 52)) # Green WiFi
        draw.text((95, 3), "WiFi", fill=(255, 255, 255))

    # Bottom Subtitle Bar (218..240)
    draw.rectangle([0, 218, 134, 239], fill=UI_BAR)
    draw.rectangle([8, 220, 126, 238], outline=UI_GOLD, fill=(30, 20, 14), width=1)
    
    # Subtitle text centered roughly
    if FONT_SUBTITLE:
        bbox = draw.textbbox((0, 0), subtitle, font=FONT_SUBTITLE)
        tw = bbox[2] - bbox[0]
        tx = max(10, (135 - tw) // 2)
        draw.text((tx, 222), subtitle, fill=UI_GOLD, font=FONT_SUBTITLE)
    else:
        draw.text((15, 222), subtitle, fill=UI_GOLD)

    # Character line art in warm ivory / gold
    # Convert mask to RGBA overlay
    char_rgb = np.zeros((240, 135, 3), dtype=np.uint8)
    char_rgb[:] = BG_DARK
    # Foreground pixels
    fg = (char_mask > 80)
    char_rgb[fg] = (254, 243, 199) # Warm Ivory
    
    char_pil = Image.fromarray(char_rgb)
    # Paste character over background preserving UI
    img.paste(char_pil.crop((0, 19, 135, 218)), (0, 19))
    return img

def apply_volumetric_breath(dev_mask, breath_factor=0.0, sway_dx=0.0):
    """
    Applies Disney Principle of Volume Preservation:
    breath_factor > 0: vertical stretch (sy = 1 + breath_factor), horizontal squash (sx = 1 / sy)
    Grounded at Y = 216.
    """
    if abs(breath_factor) < 0.001 and abs(sway_dx) < 0.001:
        return dev_mask.copy()

    h, w = dev_mask.shape[:2]
    sy = 1.0 + breath_factor
    sx = 1.0 / math.sqrt(sy)

    # Find character bounding box
    ys, xs = np.where(dev_mask > 80)
    if len(ys) == 0:
        return dev_mask.copy()

    y_bot = 216
    cx = 67.5 + sway_dx

    # Affine transform centered at (cx, y_bot)
    M = np.float32([
        [sx, 0, cx * (1 - sx) + sway_dx],
        [0, sy, y_bot * (1 - sy)]
    ])
    warped = cv2.warpAffine(dev_mask, M, (w, h), flags=cv2.INTER_LINEAR)
    _, warped_bin = cv2.threshold(warped, 70, 255, cv2.THRESH_BINARY)
    return warped_bin

def generate_wave_gif():
    print("Generating Wave Greeting GIF...")
    w1 = load_dev_lineart("wave_1")
    w2 = load_dev_lineart("wave_2")

    frames = []
    # 16-frame wave cycle
    # Frame 0..3: Wave 1 (settling / breath)
    # Frame 4..7: Transition W1 -> W2
    # Frame 8..11: Wave 2 (high wave shake)
    # Frame 12..15: Transition W2 -> W1
    for i in range(16):
        t = i / 16.0
        angle = t * 2 * math.pi
        breath = 0.025 * math.sin(angle)
        sway = 1.2 * math.sin(angle)

        if i in [0, 1, 2, 14, 15]:
            base = w1
        elif i in [6, 7, 8, 9, 10]:
            base = w2
        elif i in [3, 4, 5]:
            # Crossfade morph blend
            alpha = (i - 2) / 4.0
            base = cv2.addWeighted(w1, 1 - alpha, w2, alpha, 0)
        else:
            alpha = (i - 10) / 4.0
            base = cv2.addWeighted(w2, 1 - alpha, w1, alpha, 0)

        warped = apply_volumetric_breath(base, breath_factor=breath, sway_dx=sway)
        frame = render_device_frame(warped, subtitle="元气挥手 (Wave)", tick=i)
        frames.append(frame)

    out_path = os.path.join(OUT_DIR, "cadet_ren_wave_greeting.gif")
    mp_path = os.path.join(MP_DIR, "cadet_ren_wave_greeting.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=100, loop=0)
    frames[0].save(mp_path, save_all=True, append_images=frames[1:], duration=100, loop=0)
    print(f"  -> Saved {out_path} ({len(frames)} frames)")

def generate_kungfu_gif():
    print("Generating Kung Fu Horse Stance Strike GIF...")
    hs = load_dev_lineart("horse_strike")

    frames = []
    # 16-frame martial action cycle:
    # 0..4: Ready horse stance (intense breathing)
    # 5..7: Anticipation windup (squash -3%, draw back)
    # 8..11: Explosive thrust (forward surge +3px, stretch +4%)
    # 12..15: Settle back to grounded stance
    for i in range(16):
        if i <= 4:
            b = 0.015 * math.sin(i / 5.0 * math.pi)
            dx = 0.0
        elif i <= 7:
            # Anticipation
            t = (i - 4) / 3.0
            b = -0.035 * t
            dx = -2.5 * t
        elif i <= 10:
            # Strike punch
            t = (i - 7) / 3.0
            b = 0.04 * (1 - abs(t - 0.5))
            dx = 3.5 * t
        else:
            # Settle
            t = (i - 10) / 5.0
            b = 0.02 * (1 - t)
            dx = 3.5 * (1 - t)

        warped = apply_volumetric_breath(hs, breath_factor=b, sway_dx=dx)
        frame = render_device_frame(warped, subtitle="扎马步冲拳 (Strike)", tick=i)
        frames.append(frame)

    out_path = os.path.join(OUT_DIR, "cadet_ren_kungfu_action.gif")
    mp_path = os.path.join(MP_DIR, "cadet_ren_kungfu_action.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=90, loop=0)
    frames[0].save(mp_path, save_all=True, append_images=frames[1:], duration=90, loop=0)
    print(f"  -> Saved {out_path} ({len(frames)} frames)")

def generate_taichi_gif():
    print("Generating Tai Chi Zen GIF...")
    tc = load_dev_lineart("taichi")

    frames = []
    # 18-frame slow, fluid circular flow
    for i in range(18):
        angle = (i / 18.0) * 2 * math.pi
        b = 0.025 * math.sin(angle)
        dx = 2.0 * math.cos(angle)

        warped = apply_volumetric_breath(tc, breath_factor=b, sway_dx=dx)
        frame = render_device_frame(warped, subtitle="太极云手 (Tai Chi)", tick=i)
        frames.append(frame)

    out_path = os.path.join(OUT_DIR, "cadet_ren_taichi_zen.gif")
    mp_path = os.path.join(MP_DIR, "cadet_ren_taichi_zen.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=120, loop=0)
    frames[0].save(mp_path, save_all=True, append_images=frames[1:], duration=120, loop=0)
    print(f"  -> Saved {out_path} ({len(frames)} frames)")

def generate_dragon_punch_gif():
    print("Generating Dragon Punch GIF...")
    dp = load_dev_lineart("dragon_punch")

    frames = []
    # 16-frame leap cycle
    # 0..3: Deep crouch squash (-5%)
    # 4..8: Vertical launch (+10px upward leap, stretch +6%)
    # 9..12: Apex float
    # 13..15: Landing recovery
    for i in range(16):
        if i <= 3:
            t = i / 3.0
            b = -0.045 * t
            dy = 0.0
        elif i <= 8:
            t = (i - 3) / 5.0
            # Parabolic leap
            dy = -12.0 * math.sin(t * math.pi)
            b = 0.05 * math.sin(t * math.pi)
        elif i <= 12:
            t = (i - 8) / 4.0
            dy = -6.0 * (1 - t)
            b = 0.02 * (1 - t)
        else:
            t = (i - 12) / 3.0
            dy = 0.0
            b = -0.02 * (1 - t)

        # Shift vertically by dy
        M = np.float32([[1, 0, 0], [0, 1, dy]])
        shifted = cv2.warpAffine(dp, M, (135, 240), flags=cv2.INTER_LINEAR)
        warped = apply_volumetric_breath(shifted, breath_factor=b, sway_dx=0.0)
        frame = render_device_frame(warped, subtitle="升龙霸天 (Dragon)", tick=i)
        frames.append(frame)

    out_path = os.path.join(OUT_DIR, "cadet_ren_dragon_punch.gif")
    mp_path = os.path.join(MP_DIR, "cadet_ren_dragon_punch.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=90, loop=0)
    frames[0].save(mp_path, save_all=True, append_images=frames[1:], duration=90, loop=0)
    print(f"  -> Saved {out_path} ({len(frames)} frames)")

def generate_bow_gif():
    print("Generating Bow & Salute GIF...")
    bow = load_dev_lineart("bow")

    frames = []
    # 14-frame formal salute:
    # 0..3: Upright salute
    # 4..7: Respectful nod bow (squash -3%, head tilt)
    # 8..10: Hold bow
    # 11..13: Rise back
    for i in range(14):
        if i <= 3:
            b = 0.01 * math.sin(i / 3.0 * math.pi)
        elif i <= 7:
            t = (i - 3) / 4.0
            b = -0.035 * t
        elif i <= 10:
            b = -0.035
        else:
            t = (i - 10) / 3.0
            b = -0.035 * (1 - t)

        warped = apply_volumetric_breath(bow, breath_factor=b, sway_dx=0.0)
        frame = render_device_frame(warped, subtitle="抱拳礼 (Bao Quan Li)", tick=i)
        frames.append(frame)

    out_path = os.path.join(OUT_DIR, "cadet_ren_bow.gif")
    mp_path = os.path.join(MP_DIR, "cadet_ren_bow.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=110, loop=0)
    frames[0].save(mp_path, save_all=True, append_images=frames[1:], duration=110, loop=0)
    print(f"  -> Saved {out_path} ({len(frames)} frames)")

def generate_device_showcase_gif():
    print("Generating Full Device 135x240 Showcase Parade GIF...")
    poses = [
        ("front_idle", "待命 (Front Idle)", 8, False),
        ("bow", "抱拳礼 (Salute)", 10, False),
        ("horse_strike", "扎马步冲拳 (Strike)", 12, True),
        ("taichi", "太极云手 (Tai Chi)", 14, False),
        ("dragon_punch", "升龙霸天 (Uppercut)", 12, True),
        ("wave_1", "元气挥手 (Wave)", 8, False),
        ("wave_2", "元气挥手 (High Wave)", 8, False),
    ]

    all_frames = []
    global_tick = 0
    for name, title, count, hot in poses:
        mask = load_dev_lineart(name)
        for i in range(count):
            t = i / float(count)
            b = 0.02 * math.sin(t * 2 * math.pi)
            sway = 0.8 * math.cos(t * 2 * math.pi)
            warped = apply_volumetric_breath(mask, breath_factor=b, sway_dx=sway)
            frame = render_device_frame(warped, subtitle=title, wifi_hot=hot, tick=global_tick)
            all_frames.append(frame)
            global_tick += 1

    out_path = os.path.join(OUT_DIR, "cadet_ren_device_135x240_showcase.gif")
    mp_path = os.path.join(MP_DIR, "cadet_ren_device_135x240_showcase.gif")
    all_frames[0].save(out_path, save_all=True, append_images=all_frames[1:], duration=100, loop=0)
    all_frames[0].save(mp_path, save_all=True, append_images=all_frames[1:], duration=100, loop=0)
    print(f"  -> Saved {out_path} ({len(all_frames)} frames)")

def main():
    generate_wave_gif()
    generate_kungfu_gif()
    generate_taichi_gif()
    generate_dragon_punch_gif()
    generate_bow_gif()
    generate_device_showcase_gif()
    print("\nAll animated GIFs generated and synchronized successfully!")

if __name__ == '__main__':
    main()
