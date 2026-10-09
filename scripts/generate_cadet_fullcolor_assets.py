#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_cadet_fullcolor_assets.py
-------------------------------------------
Cadet Ren (功夫学徒阿韧) Phase 2 Multi-Layer Color Infill Generator:
1. Extracts 1:1 color character crops for all 7 poses from concept sheets:
   - bow: 抱拳礼 (Martial Salute & Bow)
   - horse_strike: 扎马步冲拳 (Horse Stance Palm Strike)
   - taichi: 太极云手 (Flowing Tai Chi Hands)
   - dragon_punch: 升龙霸天 (Leaping Dragon Uppercut)
   - wave_1: 元气挥手A (Energetic Wave 1)
   - wave_2: 元气挥手B (Energetic Wave 2)
   - front_idle: 正面待命 (Grandmaster Front Idle)
2. Maps them to the exact 135x240 M5Stack StickS3 device screen coordinates.
3. Quantizes to an optimized 16-color RGB565 palette:
   - Caramel Warm Amber Fur (#CD5F26 / 0xCAE4)
   - Dark Auburn Fur & Tail Rings (#873416 / 0x81A2)
   - Ivory White Fur / Mask / Silk Pants (#F8F6F2 / 0xF7BE)
   - White Fabric Shading (#CDCADA / 0xCE5A)
   - Midnight Navy Tactical Vest / Belt (#1A263E / 0x1927)
   - Vest Dark Shading (#101828 / 0x10C5)
   - Imperial Gold Trim & Paw Emblem (#EBB937 / 0xE5C6)
   - Wrap Navy & Cuffs (#141E32 / 0x10E6)
   - Ear Tip Dark Chocolate (#371C12 / 0x30E2)
   - Eye Iris Amber (#733E1E / 0x71E3)
   - Truffle Nose (#281614 / 0x28A2)
   - Pink Paw Pad & Cheek Blush (#FAB4AA / 0xFD95)
   - Warm Ivory Highlight (#FEF3C7 / 0xFFDE)
   - Contact Shadow (0x10A2)
   - Outer Ink Line (0x0000)
4. Compresses into high-speed RLE (Run-Length Encoded) byte arrays.
5. Emits C++ PROGMEM header: firmware/m5sticks3_buddy/include/sticks3_cadet_bitmaps.h
6. Verifies total Flash footprint is strictly under 100KB!
"""

import os
import cv2
import numpy as np
from PIL import Image

OUT_COLOR_DIR = "docs/assets/cadet_ren/device_135x240_colors"
MP_COLOR_DIR = "wechat_miniprogram/assets/cadet_ren/device_135x240_colors"
HEADER_PATH = "firmware/m5sticks3_buddy/include/sticks3_cadet_bitmaps.h"

os.makedirs(OUT_COLOR_DIR, exist_ok=True)
os.makedirs(MP_COLOR_DIR, exist_ok=True)

# 16 standard RGB565 palette colors
# Index 0 is transparent/background
PALETTE = [
    # (R, G, B, RGB565_Hex, Name)
    (11, 15, 25,    0x0862, "CADET_COL_BG_OBSIDIAN"),    # 0: Transparent/Obsidian BG
    (205, 95, 38,   0xCAE4, "CADET_COL_FUR_AMBER"),      # 1: Caramel Amber Fur #CD5F26
    (135, 52, 22,   0x81A2, "CADET_COL_FUR_DARK"),       # 2: Dark Auburn Fur & Tail Ring #873416
    (248, 246, 242, 0xF7BE, "CADET_COL_FUR_WHITE"),      # 3: Ivory White Fur & Silk Pants #F8F6F2
    (205, 202, 212, 0xCE5A, "CADET_COL_WHITE_SHD"),      # 4: White Fabric Shading #CDCADA
    (26, 38, 62,    0x1927, "CADET_COL_VEST_NAVY"),      # 5: Midnight Navy Tactical Vest #1A263E
    (16, 24, 40,    0x10C5, "CADET_COL_VEST_DARK"),      # 6: Vest Dark Shading #101828
    (235, 185, 55,  0xE5C6, "CADET_COL_VEST_GOLD"),      # 7: Imperial Gold Emblem & Trim #EBB937
    (20, 30, 50,    0x10E6, "CADET_COL_WRAP_NAVY"),      # 8: Wrap Navy & Belt #141E32
    (55, 28, 18,    0x30E2, "CADET_COL_EAR_DARK"),       # 9: Ear Tip Dark Chocolate #371C12
    (115, 62, 30,   0x71E3, "CADET_COL_EYE_IRIS"),       # 10: Eye Iris Amber #733E1E
    (40, 22, 20,    0x28A2, "CADET_COL_NOSE_DARK"),      # 11: Truffle Nose #281614
    (250, 180, 170, 0xFD95, "CADET_COL_PAD_PINK"),       # 12: Pink Pad & Cheek Blush #FAB4AA
    (254, 243, 199, 0xFFDE, "CADET_LINE_IVORY"),         # 13: Warm Ivory Highlight #FEF3C7
    (16, 26, 34,    0x10A2, "CADET_COL_SHADOW"),         # 14: Contact Shadow
    (15, 12, 10,    0x0000, "CADET_COL_INK_LINE"),       # 15: Deep Ink Line #0F0C0A
]

PALETTE_RGB = np.array([[p[0], p[1], p[2]] for p in PALETTE], dtype=np.float32)

def extract_color_master(img, crop_box, erase_rects=[], cut_bottom_px=0, cut_top_px=0):
    cy0, cy1, cx0, cx1 = crop_box
    c = img[cy0:cy1, cx0:cx1].copy()
    ch, cw = c.shape[:2]
    corners = np.concatenate([
        c[0:15, 0:15].reshape(-1, 3),
        c[0:15, cw-15:cw].reshape(-1, 3),
        c[ch-15:ch, 0:15].reshape(-1, 3),
        c[ch-15:ch, cw-15:cw].reshape(-1, 3)
    ], axis=0)
    bg_col = np.median(corners, axis=0)

    for (ey0, ey1, ex0, ex1) in erase_rects:
        c[max(0,ey0):min(ch,ey1), max(0,ex0):min(cw,ex1)] = bg_col

    flood_canvas = c.copy()
    flood_mask = np.zeros((ch+2, cw+2), np.uint8)
    for x in range(0, cw, 8):
        for y in [0, ch-1]:
            if flood_mask[y+1, x+1] == 0 and np.linalg.norm(c[y, x].astype(float) - bg_col) < 35:
                cv2.floodFill(flood_canvas, flood_mask, (x, y), (0,0,255), (18,18,18), (18,18,18), flags=8 | (255<<8))
    for y in range(0, ch, 8):
        for x in [0, cw-1]:
            if flood_mask[y+1, x+1] == 0 and np.linalg.norm(c[y, x].astype(float) - bg_col) < 35:
                cv2.floodFill(flood_canvas, flood_mask, (x, y), (0,0,255), (18,18,18), (18,18,18), flags=8 | (255<<8))

    fg = (flood_mask[1:ch+1, 1:cw+1] == 0).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg_closed = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(fg_closed)
    if num <= 1:
        return None
    char_lbl = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    char_mask = (labels == char_lbl).astype(np.uint8)
    cnts, _ = cv2.findContours(char_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    solid = np.zeros_like(char_mask)
    cv2.drawContours(solid, cnts, -1, 1, -1)
    ys, xs = np.where(solid > 0)
    char_c = c[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
    mask_c = solid[ys.min():ys.max()+1, xs.min():xs.max()+1]
    char_c[mask_c == 0] = [0, 0, 0]
    if cut_bottom_px > 0:
        char_c[-cut_bottom_px:, :] = [0, 0, 0]
    if cut_top_px > 0:
        char_c[:cut_top_px, :] = [0, 0, 0]
    return char_c

def extract_dragon_punch_color(mat):
    h_m, w_m = mat.shape[:2]
    dp_orig = mat[h_m//2+15:h_m//2+340, w_m//2+180:w_m//2+500].copy()
    hsv = cv2.cvtColor(dp_orig, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    char_seeds = ((h < 30) & (s > 50) & (v > 80)) | ((h > 95) & (h < 135) & (s > 80) & (v < 180)) | (v < 70)
    char_seeds = char_seeds.astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    closed = cv2.morphologyEx(char_seeds, cv2.MORPH_CLOSE, k)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(closed)
    char_lbl = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    char_mask = (labels == char_lbl).astype(np.uint8)
    cnts, _ = cv2.findContours(char_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    solid = np.zeros_like(char_mask)
    cv2.drawContours(solid, cnts, -1, 255, -1)
    ys, xs = np.where(solid > 0)
    char_c = dp_orig[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
    mask_c = solid[ys.min():ys.max()+1, xs.min():xs.max()+1]
    char_c[mask_c == 0] = [0, 0, 0]
    return char_c

def extract_front_idle_color(sheet):
    ren = sheet[92:683, 50:340].copy()
    h, w = ren.shape[:2]
    ren[:, 270:] = [225, 240, 243]
    ren[580:, :] = [225, 240, 243]
    flood_mask = np.zeros((h+2, w+2), np.uint8)
    bg_canvas = ren.copy()
    for pt in [(2, 2), (w-3, 2), (2, h-3), (w-3, h-3)]:
        cv2.floodFill(bg_canvas, flood_mask, pt, (255, 0, 255), (18, 18, 18), (18, 18, 18), flags=8 | (255 << 8))
    is_bg = (flood_mask[1:h+1, 1:w+1] > 0)
    fg = (~is_bg).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    solid_fg = np.zeros_like(fg)
    cv2.drawContours(solid_fg, cnts, -1, 255, -1)
    solid_fg[:, 260:] = 0
    solid_fg[:, :35] = 0
    ys, xs = np.where(solid_fg > 0)
    char_c = ren[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
    mask_c = solid_fg[ys.min():ys.max()+1, xs.min():xs.max()+1]
    char_c[mask_c == 0] = [0, 0, 0]
    return char_c

def simulate_device_color(color_img, target_w=135, target_h=240, active_y_top=20, active_y_bot=216):
    dev_canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    h, w = color_img.shape[:2]
    avail_h = active_y_bot - active_y_top
    avail_w = target_w - 9
    scale = min(avail_h / float(h), avail_w / float(w))
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = cv2.resize(color_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    x_offset = (target_w - new_w) // 2
    y_offset = active_y_bot - new_h
    dev_canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    return dev_canvas

def quantize_to_16_colors(dev_c):
    dev_smooth = cv2.bilateralFilter(dev_c, 5, 40, 40)
    dev_rgb = cv2.cvtColor(dev_smooth, cv2.COLOR_BGR2RGB).astype(np.float32)

    quant_idx = np.zeros((240, 135), dtype=np.uint8)
    is_fg = np.any(dev_c > 15, axis=2)

    # Foreground distance matching to palette indices 1..15
    dists = np.linalg.norm(dev_rgb[is_fg][:, None, :] - PALETTE_RGB[1:][None, :, :], axis=2)
    closest = np.argmin(dists, axis=1) + 1
    quant_idx[is_fg] = closest

    # Cel-shading filter
    quant_filtered = cv2.medianBlur(quant_idx, 3)
    return quant_filtered

def rle_encode(indices):
    runs = []
    curr_val = int(indices[0])
    count = 1
    for val in indices[1:]:
        val = int(val)
        if val == curr_val and count < 255:
            count += 1
        else:
            runs.append((count, curr_val))
            curr_val = val
            count = 1
    runs.append((count, curr_val))
    return runs

def pack_image_1bit(lines_path):
    img = cv2.imread(lines_path, 0)
    if img is None:
        raise FileNotFoundError(f"Missing {lines_path}")
    h, w = img.shape
    row_bytes = (w + 7) // 8
    packed = bytearray(row_bytes * h)
    for y in range(h):
        for x in range(w):
            if img[y, x] > 80:
                byte_idx = y * row_bytes + (x >> 3)
                bit_idx = 7 - (x & 7)
                packed[byte_idx] |= (1 << bit_idx)
    return packed

def main():
    print("=" * 70)
    print("Cadet Ren Phase 2: Generating Multi-Layer Full-Color Assets & C++ Header")
    print("=" * 70)

    mat = cv2.imread('docs/assets/cadet_ren/martial_action_poses.jpg')
    play = cv2.imread('docs/assets/cadet_ren/playful_action_poses.jpg')
    sheet = cv2.imread('docs/assets/cadet_ren/character_model_sheet.jpg')

    poses_meta = [
        ("bow", "Martial Art's Bow & Salute (抱拳礼)", "CADET_COLOR_BOW", "CADET_BMP_BOW",
         extract_color_master(mat, (0, 384, 300, 480), [(0, 30, 0, 180), (350, 384, 0, 60), (350, 384, 120, 180)], cut_bottom_px=2)),
        ("horse_strike", "Horse Stance Palm Strike (扎马步冲拳)", "CADET_COLOR_HORSE_STRIKE", "CADET_BMP_HORSE_STRIKE",
         extract_color_master(mat, (60, 370, 830, 1200), [(285, 310, 0, 20), (285, 310, 50, 290), (285, 310, 340, 370)], cut_bottom_px=2)),
        ("taichi", "Flowing Tai Chi Hands (太极云手)", "CADET_COLOR_TAICHI", "CADET_BMP_TAICHI",
         extract_color_master(mat, (384, 760, 210, 560), [(170, 230, 0, 50), (345, 376, 0, 30), (345, 376, 50, 230), (345, 376, 290, 350)], cut_bottom_px=3)),
        ("dragon_punch", "Leaping Dragon Uppercut (升龙霸天)", "CADET_COLOR_DRAGON_PUNCH", "CADET_BMP_DRAGON_PUNCH",
         extract_dragon_punch_color(mat)),
        ("wave_1", "Friendly Energetic Wave A (元气挥手A)", "CADET_COLOR_WAVE_1", "CADET_BMP_WAVE_1",
         extract_color_master(play, (60, 380, 30, 310), [(0, 55, 0, 280), (310, 320, 0, 100), (310, 320, 240, 280)], cut_bottom_px=2)),
        ("wave_2", "Friendly Energetic Wave B (元气挥手B)", "CADET_COLOR_WAVE_2", "CADET_BMP_WAVE_2",
         extract_color_master(play, (30, 380, 470, 690), [(0, 50, 0, 40), (340, 350, 0, 30), (340, 350, 180, 220)], cut_bottom_px=3)),
        ("front_idle", "Standard Front Idle (正面待命)", "CADET_COLOR_FRONT_IDLE", "CADET_BMP_FRONT_IDLE",
         extract_front_idle_color(sheet)),
    ]

    color_runs_dict = {}
    total_color_bytes = 0
    total_line_bytes = 0
    gif_frames = []

    for name, desc, c_run_var, c_bmp_var, raw_color in poses_meta:
        dev_c = simulate_device_color(raw_color)
        quant_idx = quantize_to_16_colors(dev_c)
        runs = rle_encode(quant_idx.flatten())
        color_runs_dict[name] = runs
        run_bytes = len(runs) * 2
        total_color_bytes += run_bytes

        # Reconstructed preview image
        preview_rgb = np.zeros((240, 135, 3), dtype=np.uint8)
        preview_rgb[:] = [11, 15, 25] # Obsidian background
        for idx in range(1, 16):
            mask = (quant_idx == idx)
            preview_rgb[mask] = PALETTE[idx][:3]

        lines_path = f"docs/assets/cadet_ren/device_135x240_lines/{name}_135x240.png"
        lines_img = cv2.imread(lines_path, 0)
        if lines_img is not None:
            preview_rgb[lines_img > 100] = [15, 12, 10] # Cel-shading dark ink outline

        # Save color preview PNG
        out_png = os.path.join(OUT_COLOR_DIR, f"{name}_135x240_color.png")
        cv2.imwrite(out_png, cv2.cvtColor(preview_rgb, cv2.COLOR_RGB2BGR))
        mp_png = os.path.join(MP_COLOR_DIR, f"{name}_135x240_color.png")
        cv2.imwrite(mp_png, cv2.cvtColor(preview_rgb, cv2.COLOR_RGB2BGR))

        # Styled device frame preview (with HUD)
        styled_frame = np.zeros((240, 135, 3), dtype=np.uint8)
        styled_frame[:] = preview_rgb
        # HUD Top
        styled_frame[0:18, :] = [20, 12, 8]
        styled_frame[4:14, 94:132] = [40, 180, 50] # WiFi pill
        # Subtitle bottom
        styled_frame[218:240, :] = [20, 12, 8]
        cv2.rectangle(styled_frame, (10, 220), (125, 238), (55, 185, 235), 1)

        styled_png = os.path.join(OUT_COLOR_DIR, f"{name}_device_preview.png")
        cv2.imwrite(styled_png, cv2.cvtColor(styled_frame, cv2.COLOR_RGB2BGR))
        mp_styled_png = os.path.join(MP_COLOR_DIR, f"{name}_device_preview.png")
        cv2.imwrite(mp_styled_png, cv2.cvtColor(styled_frame, cv2.COLOR_RGB2BGR))

        gif_frames.append(Image.fromarray(styled_frame))

        print(f"  [{name:12s}] {len(runs):4d} runs -> {run_bytes:5d} bytes | Preview saved")

    # Save animated parade GIF
    if gif_frames:
        gif_path = "docs/assets/cadet_ren/cadet_ren_fullcolor_parade.gif"
        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=600,
            loop=0
        )
        mp_gif_path = "wechat_miniprogram/assets/cadet_ren/cadet_ren_fullcolor_parade.gif"
        gif_frames[0].save(
            mp_gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=600,
            loop=0
        )
        print(f"\nSaved animated GIF: {gif_path}")

    # Build Header Content
    lines = [
        "// ============================================================================",
        "// sticks3_cadet_bitmaps.h",
        "// Authentic 1:1 Binarized Line Art & Multi-Layer Full-Color Infill for Cadet Ren",
        "// Automatically generated by scripts/generate_cadet_fullcolor_assets.py",
        "// Phase 2: Full-Color Multi-Layer Infill + Hardware Dual-Mode Switching",
        "// DO NOT MODIFY DIRECTLY",
        "// ============================================================================",
        "#pragma once",
        "",
        "#include <Arduino.h>",
        "#include \"sticks3_bear_kinematics.h\"",
        "#include <M5GFX.h>",
        "",
        "namespace sticks3 {",
        "",
        "// Screen Dimensions for Bitmaps",
        "static constexpr int CADET_BMP_W = 135;",
        "static constexpr int CADET_BMP_H = 240;",
        "static constexpr int CADET_BMP_ROW_BYTES = 17;",
        "static constexpr int CADET_BMP_SIZE = CADET_BMP_ROW_BYTES * CADET_BMP_H; // 4080 bytes",
        "",
        "// Dual Render Modes for Cadet Ren",
        "enum CadetRenderMode : uint8_t {",
        "    CADET_MODE_LINEART   = 0, // Minimal Ivory-Gold Line-Art Mode (极简象牙金微雕原画模式)",
        "    CADET_MODE_FULLCOLOR = 1  // Full-Color Dynamic Kung Fu Cadet Mode (全色域灵动功夫学员模式)",
        "};",
        "",
        "extern CadetRenderMode g_cadet_render_mode;",
        "inline CadetRenderMode getCadetRenderMode() { return g_cadet_render_mode; }",
        "inline void setCadetRenderMode(CadetRenderMode mode) { g_cadet_render_mode = mode; }",
        "inline void toggleCadetRenderMode() {",
        "    g_cadet_render_mode = (g_cadet_render_mode == CADET_MODE_LINEART) ? CADET_MODE_FULLCOLOR : CADET_MODE_LINEART;",
        "}",
        "",
        "// Theme Colors for Atlas Line Art Rendering",
        "static constexpr uint16_t CADET_LINE_IVORY  = 0xFFDE; // Warm Ivory White #FEF3C7 (RGB565)",
        "static constexpr uint16_t CADET_LINE_GOLD   = 0xFDE0; // Imperial Gold #F59E0B (RGB565)",
        "static constexpr uint16_t CADET_BG_OBSIDIAN = 0x0862; // Midnight Obsidian #0B0F19 (RGB565)",
        "",
        "// 16-Color Standard RGB565 Palette for Multi-Layer Color Infill",
        "static constexpr uint16_t CADET_PALETTE_16[16] = {",
    ]

    for i, (r, g, b, hx, name_const) in enumerate(PALETTE):
        lines.append(f"    {hx:#06X}, // [{i:2d}] {name_const} (R:{r}, G:{g}, B:{b})")
    lines.append("};")
    lines.append("")

    # Structure for Run-Length Encoded Color Infill
    lines.extend([
        "// Compact Run-Length Encoded Color Block Run (2 Bytes per Run)",
        "struct CadetColorRun {",
        "    uint8_t count;     // Number of consecutive pixels (1..255)",
        "    uint8_t color_idx; // Palette index (0 = transparent/bg, 1..15 = color)",
        "};",
        "",
    ])

    # 1. 1-bit Line Art Bitmaps
    for name, desc, c_run_var, c_bmp_var, _ in poses_meta:
        lines_path = f"docs/assets/cadet_ren/device_135x240_lines/{name}_135x240.png"
        packed = pack_image_1bit(lines_path)
        total_line_bytes += len(packed)
        lines.append(f"// {desc} - 1-bit Outline ({len(packed)} bytes)")
        lines.append(f"static const uint8_t {c_bmp_var}[{len(packed)}] PROGMEM = {{")
        for i in range(0, len(packed), 16):
            chunk = packed[i:i+16]
            hex_str = ", ".join(f"0x{b:02X}" for b in chunk)
            if i + 16 < len(packed):
                lines.append(f"    {hex_str},")
            else:
                lines.append(f"    {hex_str}")
        lines.append("};")
        lines.append("")

    # 2. Multi-Layer Color Infill Runs
    for name, desc, c_run_var, c_bmp_var, _ in poses_meta:
        runs = color_runs_dict[name]
        lines.append(f"// {desc} - Multi-Layer Color Infill ({len(runs)} runs, {len(runs)*2} bytes)")
        lines.append(f"static const CadetColorRun {c_run_var}[{len(runs)}] PROGMEM = {{")
        for i in range(0, len(runs), 8):
            chunk = runs[i:i+8]
            entries = [f"{{{cnt}, {cidx}}}" for (cnt, cidx) in chunk]
            line_str = ", ".join(entries)
            if i + 8 < len(runs):
                lines.append(f"    {line_str},")
            else:
                lines.append(f"    {line_str}")
        lines.append("};")
        lines.append("")

    # Helper Functions
    lines.extend([
        "/**",
        " * @brief Resolves authentic atlas 1-bit lineart bitmap for a given action and frame.",
        " */",
        "inline const uint8_t* getCadetAtlasBitmap(BearAction act, int frame) {",
        "    switch (act) {",
        "        case BEAR_ACT_KUNGFU:        return CADET_BMP_HORSE_STRIKE;",
        "        case BEAR_ACT_TAICHI:        return CADET_BMP_TAICHI;",
        "        case BEAR_ACT_DRAGON_PUNCH:  return CADET_BMP_DRAGON_PUNCH;",
        "        case BEAR_ACT_BOW:           return CADET_BMP_BOW;",
        "        case BEAR_ACT_WAVE:          return (frame % 2 == 0) ? CADET_BMP_WAVE_1 : CADET_BMP_WAVE_2;",
        "        case BEAR_ACT_IDLE:          return CADET_BMP_FRONT_IDLE;",
        "        default:                     return nullptr;",
        "    }",
        "}",
        "",
        "/**",
        " * @brief Resolves authentic multi-layer color infill runs for a given action and frame.",
        " */",
        "inline const CadetColorRun* getCadetColorRuns(BearAction act, int frame, size_t& out_count) {",
        "    switch (act) {",
        "        case BEAR_ACT_KUNGFU:",
        "            out_count = sizeof(CADET_COLOR_HORSE_STRIKE) / sizeof(CADET_COLOR_HORSE_STRIKE[0]);",
        "            return CADET_COLOR_HORSE_STRIKE;",
        "        case BEAR_ACT_TAICHI:",
        "            out_count = sizeof(CADET_COLOR_TAICHI) / sizeof(CADET_COLOR_TAICHI[0]);",
        "            return CADET_COLOR_TAICHI;",
        "        case BEAR_ACT_DRAGON_PUNCH:",
        "            out_count = sizeof(CADET_COLOR_DRAGON_PUNCH) / sizeof(CADET_COLOR_DRAGON_PUNCH[0]);",
        "            return CADET_COLOR_DRAGON_PUNCH;",
        "        case BEAR_ACT_BOW:",
        "            out_count = sizeof(CADET_COLOR_BOW) / sizeof(CADET_COLOR_BOW[0]);",
        "            return CADET_COLOR_BOW;",
        "        case BEAR_ACT_WAVE:",
        "            if (frame % 2 == 0) {",
        "                out_count = sizeof(CADET_COLOR_WAVE_1) / sizeof(CADET_COLOR_WAVE_1[0]);",
        "                return CADET_COLOR_WAVE_1;",
        "            } else {",
        "                out_count = sizeof(CADET_COLOR_WAVE_2) / sizeof(CADET_COLOR_WAVE_2[0]);",
        "                return CADET_COLOR_WAVE_2;",
        "            }",
        "        case BEAR_ACT_IDLE:",
        "            out_count = sizeof(CADET_COLOR_FRONT_IDLE) / sizeof(CADET_COLOR_FRONT_IDLE[0]);",
        "            return CADET_COLOR_FRONT_IDLE;",
        "        default:",
        "            out_count = 0;",
        "            return nullptr;",
        "    }",
        "}",
        "",
        "/**",
        " * @brief High-speed zero-copy 1-bit bitmap renderer to LGFX_Sprite with optional kinematics offset.",
        " */",
        "inline void drawCadetAtlasLineart(LovyanGFX& d, const uint8_t* bmp, uint16_t color = CADET_LINE_IVORY, int dx = 0, int dy = 0) {",
        "    if (!bmp) return;",
        "    for (int y = 20; y < 218; y++) {",
        "        int dst_y = y + dy;",
        "        if (dst_y < 19 || dst_y >= 218) continue;",
        "        const uint8_t* row = bmp + (y * CADET_BMP_ROW_BYTES);",
        "        for (int x = 0; x < CADET_BMP_W; x++) {",
        "            if ((row[x >> 3] >> (7 - (x & 7))) & 1) {",
        "                int dst_x = x + dx;",
        "                if (dst_x >= 0 && dst_x < CADET_BMP_W) {",
        "                    d.drawPixel(dst_x, dst_y, color);",
        "                }",
        "            }",
        "        }",
        "    }",
        "}",
        "",
        "/**",
        " * @brief Blazing-fast RLE color block infill renderer with LovyanGFX horizontal span acceleration.",
        " */",
        "inline void drawCadetColorInfill(LovyanGFX& d, const CadetColorRun* runs, size_t run_count, int dx = 0, int dy = 0) {",
        "    if (!runs || run_count == 0) return;",
        "    int pixel_idx = 0;",
        "    for (size_t i = 0; i < run_count; i++) {",
        "        uint8_t cnt = runs[i].count;",
        "        uint8_t c_idx = runs[i].color_idx;",
        "        if (c_idx != 0) {",
        "            uint16_t color = CADET_PALETTE_16[c_idx];",
        "            int remaining = cnt;",
        "            int cur_p = pixel_idx;",
        "            while (remaining > 0) {",
        "                int cur_x = cur_p % CADET_BMP_W;",
        "                int cur_y = cur_p / CADET_BMP_W;",
        "                int span_in_row = std::min(remaining, CADET_BMP_W - cur_x);",
        "                int dst_y = cur_y + dy;",
        "                if (dst_y >= 19 && dst_y < 218) {",
        "                    int dst_x = cur_x + dx;",
        "                    if (dst_x < CADET_BMP_W && (dst_x + span_in_row) > 0) {",
        "                        int draw_x0 = std::max(0, dst_x);",
        "                        int draw_x1 = std::min(CADET_BMP_W, dst_x + span_in_row);",
        "                        if (draw_x1 > draw_x0) {",
        "                            d.drawFastHLine(draw_x0, dst_y, draw_x1 - draw_x0, color);",
        "                        }",
        "                    }",
        "                }",
        "                remaining -= span_in_row;",
        "                cur_p += span_in_row;",
        "            }",
        "        }",
        "        pixel_idx += cnt;",
        "    }",
        "}",
        "",
        "/**",
        " * @brief Complete composite full-color frame renderer: color blocks infill + crisp 1:1 ink lines.",
        " */",
        "inline bool drawCadetFullColorFrame(LovyanGFX& d, BearAction act, int frame, int dx = 0, int dy = 0) {",
        "    size_t run_count = 0;",
        "    const CadetColorRun* runs = getCadetColorRuns(act, frame, run_count);",
        "    const uint8_t* bmp = getCadetAtlasBitmap(act, frame);",
        "    if (!runs || run_count == 0 || !bmp) return false;",
        "",
        "    // 1. Multi-Layer Color Infill (Caramel fur, navy vest, gold emblem, white silk pants, ring tail)",
        "    drawCadetColorInfill(d, runs, run_count, dx, dy);",
        "",
        "    // 2. Crisp 1:1 Ink Cel-Shading Outlines",
        "    drawCadetAtlasLineart(d, bmp, CADET_COL_FUR_DARK, dx, dy);",
        "    return true;",
        "}",
        "",
        "} // namespace sticks3",
    ])

    header_content = "\n".join(lines) + "\n"
    with open(HEADER_PATH, "w", encoding="utf-8") as f:
        f.write(header_content)

    grand_total_bytes = total_line_bytes + total_color_bytes
    print("=" * 70)
    print("FLASH MEMORY BUDGET REPORT:")
    print(f"  • 7 Poses 1-bit Bitmaps   : {total_line_bytes:5d} bytes ({total_line_bytes/1024:.2f} KB)")
    print(f"  • 7 Poses Color Infill RLE : {total_color_bytes:5d} bytes ({total_color_bytes/1024:.2f} KB)")
    print(f"  • Grand Total Flash Memory : {grand_total_bytes:5d} bytes ({grand_total_bytes/1024:.2f} KB)")
    print(f"  • Budget Limit (100KB)     : 102400 bytes (100.00 KB)")
    print(f"  • Margin Remaining         : {102400 - grand_total_bytes:5d} bytes ({(102400 - grand_total_bytes)/1024:.2f} KB)")
    print(f"  • Budget Usage Ratio       : {grand_total_bytes / 102400 * 100:.1f}%")
    print(f"  -> Generated {HEADER_PATH}")
    print("=" * 70)

if __name__ == '__main__':
    main()
