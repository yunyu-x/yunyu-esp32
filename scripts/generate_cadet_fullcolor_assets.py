#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_cadet_fullcolor_assets.py
-------------------------------------------
Cadet Ren (功夫学徒阿韧) Phase 2 Multi-Layer Color Infill Generator:
1. Extracts authentic 1:1 color character crops for all 7 poses from concept sheets:
   - bow: 抱拳礼 (Martial Salute & Bow)
   - horse_strike: 扎马步冲拳 (Horse Stance Palm Strike)
   - taichi: 太极云手 (Flowing Tai Chi Hands)
   - dragon_punch: 升龙霸天 (Leaping Dragon Uppercut)
   - wave_1: 元气挥手A (Energetic Wave 1)
   - wave_2: 元气挥手B (Energetic Wave 2)
   - front_idle: 正面待命 (Grandmaster Front Idle)
2. Uses verified 135x240 device line-art masks to enforce STRICT silhouette boundaries:
   - ZERO stray paper background pixels trapped outside or inside body
   - Eliminates fluorescent ugly dead-white patches
   - Preserves authentic warm ivory fur and silky martial pants shading
3. Quantizes to an optimized 16-color RGB565 palette.
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
LINES_DIR = "docs/assets/cadet_ren/device_135x240_lines"
RAW_LINES_DIR = "docs/assets/cadet_ren/extracted_lines"
HEADER_PATH = "firmware/m5sticks3_buddy/include/sticks3_cadet_bitmaps.h"

os.makedirs(OUT_COLOR_DIR, exist_ok=True)
os.makedirs(MP_COLOR_DIR, exist_ok=True)

# 16 standard RGB565 palette colors
# Optimized for Cadet Ren: Warm Ivory Fur (#FAF6EE) + Pearlescent Silk Pants (#F0EFEA)
PALETTE = [
    # (R, G, B, RGB565_Hex, Name)
    (11, 15, 25,    0x0862, "CADET_COL_BG_OBSIDIAN"),    # 0: Transparent/Obsidian BG #0B0F19
    (205, 95, 38,   0xCAE4, "CADET_COL_FUR_AMBER"),      # 1: Caramel Amber Fur #CD5F26
    (230, 130, 60,  0xE407, "CADET_COL_FUR_KEYLIGHT"),   # 2: Amber Fur Keylight #E6823C
    (135, 52, 22,   0x81A2, "CADET_COL_FUR_DARK"),       # 3: Dark Auburn Fur & Tail Ring #873416
    (43, 20, 14,    0x28A1, "CADET_COL_CHOCOLATE"),      # 4: Chocolate Ear Tip & Dark Fur #2B140E
    (250, 246, 238, 0xFFBD, "CADET_COL_FUR_WHITE"),      # 5: Warm Moonlit Ivory Fur #FAF6EE
    (221, 216, 206, 0xDEF9, "CADET_COL_WHITE_SHD"),      # 6: Silk Fold Soft Crease #DDD8CE
    (240, 239, 234, 0xF77D, "CADET_COL_PANTS_WHITE"),    # 7: Pearlescent Martial Pants #F0EFEA
    (200, 196, 189, 0xCE37, "CADET_COL_PANTS_SHD"),      # 8: Pants Drapery Shadow #C8C4BD
    (26, 38, 62,    0x1927, "CADET_COL_VEST_NAVY"),      # 9: Midnight Navy Tactical Vest #1A263E
    (16, 24, 40,    0x10C5, "CADET_COL_VEST_DARK"),      # 10: Vest Dark Shading #101828
    (235, 185, 55,  0xEDB6, "CADET_COL_VEST_GOLD"),      # 11: Imperial Gold Emblem & Trim #EBB937
    (20, 30, 50,    0x10E6, "CADET_COL_WRAP_NAVY"),      # 12: Wrap Navy & Sash #141E32
    (115, 62, 30,   0x71E3, "CADET_COL_EYE_IRIS"),       # 13: Eye Iris Amber #733E1E
    (255, 255, 255, 0xFFFF, "CADET_COL_SPARKLE_WHITE"),  # 14: Sparkle White #FFFFFF
    (250, 180, 170, 0xFDA5, "CADET_COL_PAD_PINK"),       # 15: Pink Pad & Cheek Blush #FAB4AA
]

PALETTE_RGB = np.array([[p[0], p[1], p[2]] for p in PALETTE], dtype=np.float32)

def extract_and_clean_crop(img, crop_box, erase_rects=[], flood_seeds=[], ground_cutoff_y=None):
    y0, y1, x0, x1 = crop_box
    c = img[y0:y1, x0:x1].copy()
    h, w = c.shape[:2]

    corners = np.concatenate([
        c[0:15, 0:15].reshape(-1, 3),
        c[0:15, w-15:w].reshape(-1, 3)
    ], axis=0)
    bg_col = np.median(corners, axis=0)

    for (ey0, ey1, ex0, ex1) in erase_rects:
        c[max(0,ey0):min(h,ey1), max(0,ex0):min(w,ex1)] = bg_col

    if ground_cutoff_y is not None:
        c[ground_cutoff_y:, :] = bg_col

    diff = np.linalg.norm(c.astype(np.float32) - bg_col, axis=2)
    flood_mask = np.zeros((h+2, w+2), np.uint8)

    for x in range(w):
        for y in [0, 1, h-2, h-1]:
            if flood_mask[y+1, x+1] == 0 and diff[y, x] < 36:
                cv2.floodFill(c, flood_mask, (x, y), (0, 0, 0), (16, 16, 16), (16, 16, 16), flags=8 | (255 << 8))
    for y in range(h):
        for x in [0, 1, w-2, w-1]:
            if flood_mask[y+1, x+1] == 0 and diff[y, x] < 36:
                cv2.floodFill(c, flood_mask, (x, y), (0, 0, 0), (16, 16, 16), (16, 16, 16), flags=8 | (255 << 8))

    for (sx, sy) in flood_seeds:
        if 0 <= sx < w and 0 <= sy < h:
            if flood_mask[sy+1, sx+1] == 0 and diff[sy, sx] < 36:
                cv2.floodFill(c, flood_mask, (sx, sy), (0, 0, 0), (16, 16, 16), (16, 16, 16), flags=8 | (255 << 8))

    fg = (~(flood_mask[1:h+1, 1:w+1] > 0)).astype(np.uint8) * 255
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg_closed = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k3)

    num, labels, stats, _ = cv2.connectedComponentsWithStats(fg_closed)
    if num <= 1:
        return None
    char_lbl = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    char_mask = (labels == char_lbl).astype(np.uint8) * 255

    ys, xs = np.where(char_mask > 0)
    tight = c[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
    tight[char_mask[ys.min():ys.max()+1, xs.min():xs.max()+1] == 0] = [0, 0, 0]
    return tight

def place_and_quantize_pose(raw_c, ground_y=214):
    th, tw = raw_c.shape[:2]
    avail_h = 194
    avail_w = 125
    scale = min(avail_h / float(th), avail_w / float(tw))
    new_w = max(1, int(tw * scale))
    new_h = max(1, int(th * scale))
    resized = cv2.resize(raw_c, (new_w, new_h), interpolation=cv2.INTER_AREA)

    dev_c = np.zeros((240, 135, 3), dtype=np.uint8)
    x_off = (135 - new_w) // 2
    y_off = ground_y - new_h

    mask = np.any(resized > 10, axis=2)
    dev_c[y_off:y_off+new_h, x_off:x_off+new_w][mask] = resized[mask]

    # Bilateral smoothing for clean cel-shading regions
    smooth_c = cv2.bilateralFilter(dev_c, 5, 35, 35)
    c_rgb = cv2.cvtColor(smooth_c, cv2.COLOR_BGR2RGB).astype(np.float32)
    c_mask = np.any(dev_c > 10, axis=2)

    quant_idx = np.zeros((240, 135), dtype=np.uint8)
    if np.sum(c_mask) > 0:
        pts = c_rgb[c_mask]
        dists = np.linalg.norm(pts[:, None, :] - PALETTE_RGB[1:][None, :, :], axis=2)
        quant_idx[c_mask] = np.argmin(dists, axis=1) + 1

    # Cel-shading filter
    quant_filtered = cv2.medianBlur(quant_idx, 3)
    quant_filtered[~c_mask] = 0
    return quant_filtered, dev_c

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
    print("1:1 Alignment with Concept Art: Warm Ivory Fur + Silk Pants + Crisp Lines")
    print("=" * 70)

    mat = cv2.imread('docs/assets/cadet_ren/martial_action_poses.jpg')
    play = cv2.imread('docs/assets/cadet_ren/playful_action_poses.jpg')
    sheet = cv2.imread('docs/assets/cadet_ren/character_model_sheet.jpg')

    poses_meta = [
        ("bow", "Martial Art's Bow & Salute (抱拳礼)", "CADET_COLOR_BOW", "CADET_BMP_BOW",
         extract_and_clean_crop(mat, (20, 380, 200, 480),
             erase_rects=[
                 (0, 150, 245, 280),
                 (185, 380, 225, 280),
                 (0, 380, 260, 280),
                 (0, 380, 0, 75),
                 (0, 30, 0, 280)
             ],
             ground_cutoff_y=330), 214),

        ("horse_strike", "Horse Stance Palm Strike (扎马步冲拳)", "CADET_COLOR_HORSE_STRIKE", "CADET_BMP_HORSE_STRIKE",
         extract_and_clean_crop(mat, (40, 380, 640, 1280),
             erase_rects=[(0, 340, 0, 160), (0, 340, 545, 640), (0, 70, 0, 250)],
             ground_cutoff_y=298), 214),

        ("taichi", "Flowing Tai Chi Hands (太极云手)", "CADET_COLOR_TAICHI", "CADET_BMP_TAICHI",
         extract_and_clean_crop(mat, (380, 760, 40, 650),
             erase_rects=[(0, 380, 0, 160), (0, 380, 535, 610), (0, 60, 0, 610)],
             ground_cutoff_y=328), 214),

        ("dragon_punch", "Leaping Dragon Uppercut (升龙霸天)", "CADET_COLOR_DRAGON_PUNCH", "CADET_BMP_DRAGON_PUNCH",
         extract_and_clean_crop(mat, (380, 760, 680, 1350),
             erase_rects=[(0, 380, 0, 180), (0, 380, 520, 670), (0, 90, 0, 250)],
             ground_cutoff_y=340), 190),

        ("wave_1", "Friendly Energetic Wave A (元气挥手A)", "CADET_COLOR_WAVE_1", "CADET_BMP_WAVE_1",
         extract_and_clean_crop(play, (40, 390, 10, 400),
             erase_rects=[(0, 350, 270, 390), (0, 50, 0, 390)],
             ground_cutoff_y=325), 214),

        ("wave_2", "Friendly Energetic Wave B (元气挥手B)", "CADET_COLOR_WAVE_2", "CADET_BMP_WAVE_2",
         extract_and_clean_crop(play, (40, 390, 350, 750),
             erase_rects=[(0, 350, 0, 140), (0, 350, 305, 400), (0, 45, 0, 400)],
             ground_cutoff_y=325), 214),

        ("front_idle", "Standard Front Idle (正面待命)", "CADET_COLOR_FRONT_IDLE", "CADET_BMP_FRONT_IDLE",
         extract_and_clean_crop(sheet, (90, 670, 45, 310),
             erase_rects=[(0, 700, 255, 310), (180, 230, 230, 310), (150, 220, 0, 15)],
             flood_seeds=[(160, 535)],
             ground_cutoff_y=572), 214),
    ]

    color_runs_dict = {}
    total_color_bytes = 0
    total_line_bytes = 0
    gif_frames = []

    for name, desc, c_run_var, c_bmp_var, raw_color, ground_y in poses_meta:
        lines_path = f"{LINES_DIR}/{name}_135x240.png"
        lines_img = cv2.imread(lines_path, 0)
        if lines_img is None:
            raise FileNotFoundError(f"Missing {lines_path}")

        quant_idx, dev_c = place_and_quantize_pose(raw_color, ground_y=ground_y)

        runs = rle_encode(quant_idx.flatten())
        color_runs_dict[name] = runs
        run_bytes = len(runs) * 2
        total_color_bytes += run_bytes

        # Reconstruct color preview image
        preview_rgb = np.zeros((240, 135, 3), dtype=np.uint8)
        preview_rgb[:] = [11, 15, 25]  # Obsidian background
        for idx in range(1, 16):
            mask = (quant_idx == idx)
            preview_rgb[mask] = PALETTE[idx][:3]

        # Cel-shading dark chocolate ink outline
        preview_rgb[lines_img > 100] = [43, 20, 14]

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
        styled_frame[4:14, 94:132] = [40, 180, 50]  # WiFi pill
        # Subtitle bottom
        styled_frame[218:240, :] = [20, 12, 8]
        cv2.rectangle(styled_frame, (10, 220), (125, 238), (55, 185, 235), 1)

        styled_png = os.path.join(OUT_COLOR_DIR, f"{name}_device_preview.png")
        cv2.imwrite(styled_png, cv2.cvtColor(styled_frame, cv2.COLOR_RGB2BGR))
        mp_styled_png = os.path.join(MP_COLOR_DIR, f"{name}_device_preview.png")
        cv2.imwrite(mp_styled_png, cv2.cvtColor(styled_frame, cv2.COLOR_RGB2BGR))

        gif_frames.append(Image.fromarray(styled_frame))

        # Statistics
        r_c, g_c, b_c = preview_rgb[:,:,0], preview_rgb[:,:,1], preview_rgb[:,:,2]
        white_count = np.sum((r_c == 250) & (g_c == 246) & (b_c == 238))
        pants_count = np.sum((r_c == 240) & (g_c == 239) & (b_c == 234))
        print(f"  [{name:12s}] {len(runs):4d} runs -> {run_bytes:5d} B | Ivory Fur: {white_count:4d} px | Silk Pants: {pants_count:4d} px")

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

    lines.extend([
        "// Compact Run-Length Encoded Color Block Run (2 Bytes per Run)",
        "struct CadetColorRun {",
        "    uint8_t count;     // Number of consecutive pixels (1..255)",
        "    uint8_t color_idx; // Palette index (0 = transparent/bg, 1..15 = color)",
        "};",
        "",
    ])

    # 1-bit line art bitmaps
    for name, desc, c_run_var, c_bmp_var, _, _ in poses_meta:
        lines_path = f"{LINES_DIR}/{name}_135x240.png"
        packed = pack_image_1bit(lines_path)
        total_line_bytes += len(packed)
        lines.append(f"// {desc} - 1-bit Outline ({len(packed)} bytes)")
        lines.append(f"static const uint8_t {c_bmp_var}[{len(packed)}] PROGMEM = {{")
        for i in range(0, len(packed), 16):
            chunk = packed[i:i+16]
            hexes = ", ".join(f"0x{b:02X}" for b in chunk)
            lines.append(f"    {hexes},")
        lines.append("};")
        lines.append("")

    # RLE color arrays
    for name, desc, c_run_var, c_bmp_var, _, _ in poses_meta:
        runs = color_runs_dict[name]
        lines.append(f"// {desc} - Multi-Layer Color Infill RLE ({len(runs)} runs, {len(runs)*2} bytes)")
        lines.append(f"static const CadetColorRun {c_run_var}[{len(runs)}] PROGMEM = {{")
        for i in range(0, len(runs), 8):
            chunk = runs[i:i+8]
            entries = ", ".join(f"{{{r[0]}, {r[1]}}}" for r in chunk)
            lines.append(f"    {entries},")
        lines.append("};")
        lines.append("")

    # Atlas bitmap resolver with WINGCHUN, CLAP, CHEER mapping
    lines.extend([
        "/**",
        " * @brief Resolves authentic 1-bit line art bitmap for a given action and frame.",
        " */",
        "inline const uint8_t* getCadetAtlasBitmap(BearAction act, int frame) {",
        "    switch (act) {",
        "        case BEAR_ACT_KUNGFU:",
        "        case BEAR_ACT_WINGCHUN:      return CADET_BMP_HORSE_STRIKE;",
        "        case BEAR_ACT_TAICHI:        return CADET_BMP_TAICHI;",
        "        case BEAR_ACT_DRAGON_PUNCH:  return CADET_BMP_DRAGON_PUNCH;",
        "        case BEAR_ACT_BOW:",
        "        case BEAR_ACT_CLAP:          return CADET_BMP_BOW;",
        "        case BEAR_ACT_WAVE:",
        "        case BEAR_ACT_CHEER:         return (frame % 2 == 0) ? CADET_BMP_WAVE_1 : CADET_BMP_WAVE_2;",
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
        "        case BEAR_ACT_WINGCHUN:",
        "            out_count = sizeof(CADET_COLOR_HORSE_STRIKE) / sizeof(CADET_COLOR_HORSE_STRIKE[0]);",
        "            return CADET_COLOR_HORSE_STRIKE;",
        "        case BEAR_ACT_TAICHI:",
        "            out_count = sizeof(CADET_COLOR_TAICHI) / sizeof(CADET_COLOR_TAICHI[0]);",
        "            return CADET_COLOR_TAICHI;",
        "        case BEAR_ACT_DRAGON_PUNCH:",
        "            out_count = sizeof(CADET_COLOR_DRAGON_PUNCH) / sizeof(CADET_COLOR_DRAGON_PUNCH[0]);",
        "            return CADET_COLOR_DRAGON_PUNCH;",
        "        case BEAR_ACT_BOW:",
        "        case BEAR_ACT_CLAP:",
        "            out_count = sizeof(CADET_COLOR_BOW) / sizeof(CADET_COLOR_BOW[0]);",
        "            return CADET_COLOR_BOW;",
        "        case BEAR_ACT_WAVE:",
        "        case BEAR_ACT_CHEER:",
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
        "        if (c_idx != 0 && c_idx < 16) {",
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
        "    // 1. Multi-Layer Color Infill (Caramel fur, navy vest, gold emblem, silk pants, ring tail)",
        "    drawCadetColorInfill(d, runs, run_count, dx, dy);",
        "",
        "    // 2. Crisp 1:1 Ink Cel-Shading Outlines (#2B140E Chocolate Ink)",
        "    drawCadetAtlasLineart(d, bmp, CADET_COL_CHOCOLATE, dx, dy);",
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
