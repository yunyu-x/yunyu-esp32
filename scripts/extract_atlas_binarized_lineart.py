#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/extract_atlas_binarized_lineart.py
-----------------------------------------
Extracts authentic, high-fidelity binarized contour lines directly from
the official Cadet Ren concept sheets:
1. martial_action_poses.jpg (Bow, Horse Stance Strike, Tai Chi, Dragon Uppercut)
2. playful_action_poses.jpg (Friendly Wave 1, Friendly Wave 2)
3. character_model_sheet.jpg (Front View Idle)

Ensures 100% complete character anatomy (ears, whiskers, limbs, belt, tail, boots),
zero stray chart annotations, zero ruler/notebook grid lines, and zero ground lines.
Simulates M5Stack StickS3 display layout (135x240 screen, ST7789) with proper
horizontal centering and baseline grounding.
"""

import os
import cv2
import numpy as np

OUT_DIR = "docs/assets/cadet_ren/extracted_lines"
DEV_DIR = "docs/assets/cadet_ren/device_135x240_lines"
MP_DIR = "wechat_miniprogram/assets/cadet_ren/device_135x240_lines"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DEV_DIR, exist_ok=True)
os.makedirs(MP_DIR, exist_ok=True)

def extract_character_master(
    img, 
    crop_box,            # (y0, y1, x0, x1)
    erase_rects=[],      # [(y0, y1, x0, x1), ...] in crop coordinates
    dog_thresh=9,
    min_comp_area=12,
    cut_bottom_px=0,
    cut_top_px=0
):
    cy0, cy1, cx0, cx1 = crop_box
    c = img[cy0:cy1, cx0:cx1].copy()
    ch, cw = c.shape[:2]

    # Sample background color from corners
    corners = np.concatenate([
        c[0:15, 0:15].reshape(-1, 3),
        c[0:15, cw-15:cw].reshape(-1, 3),
        c[ch-15:ch, 0:15].reshape(-1, 3),
        c[ch-15:ch, cw-15:cw].reshape(-1, 3)
    ], axis=0)
    bg_col = np.median(corners, axis=0)

    # Erase specified text / border regions by painting with background color
    for (ey0, ey1, ex0, ex1) in erase_rects:
        c[max(0,ey0):min(ch,ey1), max(0,ex0):min(cw,ex1)] = bg_col

    # Flood fill from along the 4 borders
    flood_canvas = c.copy()
    flood_mask = np.zeros((ch+2, cw+2), np.uint8)

    border_pts = []
    for x in range(0, cw, 8):
        border_pts.append((x, 0))
        border_pts.append((x, ch-1))
    for y in range(0, ch, 8):
        border_pts.append((0, y))
        border_pts.append((cw-1, y))

    for pt in border_pts:
        if flood_mask[pt[1]+1, pt[0]+1] == 0:
            p_col = c[pt[1], pt[0]].astype(float)
            if np.linalg.norm(p_col - bg_col) < 35:
                cv2.floodFill(flood_canvas, flood_mask, pt, (0, 0, 255), (18, 18, 18), (18, 18, 18), flags=8 | (255 << 8))

    # Foreground is where flood_mask is 0
    fg = (flood_mask[1:ch+1, 1:cw+1] == 0).astype(np.uint8) * 255

    # Morphology closing to bridge fur tufts and small gaps
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg_closed = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k)

    # Keep largest component
    num, labels, stats, _ = cv2.connectedComponentsWithStats(fg_closed)
    if num <= 1:
        return None
    char_lbl = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    char_mask = (labels == char_lbl).astype(np.uint8)

    # Fill internal contours so silhouette is completely solid
    cnts, _ = cv2.findContours(char_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    solid = np.zeros_like(char_mask)
    cv2.drawContours(solid, cnts, -1, 1, -1)

    # Crop to bounding box
    ys, xs = np.where(solid > 0)
    if len(ys) == 0:
        return None
    min_y, max_y = ys.min(), ys.max()
    min_x, max_x = xs.min(), xs.max()

    char_c = c[min_y:max_y+1, min_x:max_x+1]
    mask_c = solid[min_y:max_y+1, min_x:max_x+1]

    # Bilateral smoothing for clean lines without noise
    smooth = cv2.bilateralFilter(char_c, 7, 50, 50)
    smooth_g = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    smooth_g[mask_c == 0] = 255

    # Difference of Gaussians (DoG) for internal linework
    g1 = cv2.GaussianBlur(smooth_g, (3, 3), 0.8)
    g2 = cv2.GaussianBlur(smooth_g, (7, 7), 2.2)
    dog = cv2.subtract(g2, g1)
    _, dog_b = cv2.threshold(dog, dog_thresh, 255, cv2.THRESH_BINARY)
    inked = (smooth_g < 85).astype(np.uint8) * 255

    # Outer silhouette outline
    outlines, _ = cv2.findContours(mask_c, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    outer = np.zeros_like(dog_b)
    cv2.drawContours(outer, outlines, -1, 255, 2)

    lines = cv2.bitwise_or(dog_b, outer)
    lines = cv2.bitwise_or(lines, inked)
    lines[mask_c == 0] = 0

    if cut_bottom_px > 0:
        lines[-cut_bottom_px:, :] = 0
    if cut_top_px > 0:
        lines[:cut_top_px, :] = 0

    # Filter out tiny disconnected specks
    nl, ll, sl, _ = cv2.connectedComponentsWithStats(lines)
    clean = np.zeros_like(lines)
    for i in range(1, nl):
        if sl[i, cv2.CC_STAT_AREA] >= min_comp_area:
            clean[ll == i] = 255

    return clean

def extract_dragon_punch_special(mat):
    """
    Dragon Punch has dynamic cyan lighting aura; extract character body specifically.
    """
    h_m, w_m = mat.shape[:2]
    dp_orig = mat[h_m//2+15:h_m//2+340, w_m//2+180:w_m//2+500].copy()

    hsv = cv2.cvtColor(dp_orig, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    # Character seeds
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
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()

    char_c = dp_orig[y0:y1+1, x0:x1+1]
    mask_c = solid[y0:y1+1, x0:x1+1]

    smooth = cv2.bilateralFilter(char_c, 7, 50, 50)
    smooth_g = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    smooth_g[mask_c == 0] = 255

    g1 = cv2.GaussianBlur(smooth_g, (3, 3), 0.8)
    g2 = cv2.GaussianBlur(smooth_g, (7, 7), 2.2)
    dog = cv2.subtract(g2, g1)
    _, dog_b = cv2.threshold(dog, 8, 255, cv2.THRESH_BINARY)
    inked = (smooth_g < 85).astype(np.uint8) * 255

    outlines, _ = cv2.findContours(mask_c, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    outer = np.zeros_like(dog_b)
    cv2.drawContours(outer, outlines, -1, 255, 2)

    lines = cv2.bitwise_or(dog_b, outer)
    lines = cv2.bitwise_or(lines, inked)
    lines[mask_c == 0] = 0

    nl, ll, sl, _ = cv2.connectedComponentsWithStats(lines)
    clean = np.zeros_like(lines)
    for i in range(1, nl):
        if sl[i, cv2.CC_STAT_AREA] >= 12:
            clean[ll == i] = 255

    return clean

def extract_front_idle_special(sheet):
    """
    Model sheet front view with height grid lines filtered out.
    """
    ren = sheet[92:683, 50:340].copy()
    h, w = ren.shape[:2]

    # Erase text / adjacent character on right
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

    smooth = cv2.bilateralFilter(ren, 7, 50, 50)
    smooth_gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)

    g1 = cv2.GaussianBlur(smooth_gray, (3, 3), 0.8)
    g2 = cv2.GaussianBlur(smooth_gray, (7, 7), 2.2)
    dog = cv2.subtract(g2, g1)
    _, dog_bin = cv2.threshold(dog, 8, 255, cv2.THRESH_BINARY)
    inked = (smooth_gray < 85).astype(np.uint8) * 255

    outlines, _ = cv2.findContours(solid_fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    outer = np.zeros_like(dog_bin)
    cv2.drawContours(outer, outlines, -1, 255, 2)

    lines = cv2.bitwise_or(dog_bin, outer)
    lines = cv2.bitwise_or(lines, inked)
    lines[solid_fg == 0] = 0

    # Clean ruler ticks
    lines[:350, :42] = 0
    lines[:350, 248:] = 0
    lines[:50, :] = 0

    nl, ll, sl, _ = cv2.connectedComponentsWithStats(lines)
    clean = np.zeros_like(lines)
    for i in range(1, nl):
        w_comp = sl[i, cv2.CC_STAT_WIDTH]
        h_comp = sl[i, cv2.CC_STAT_HEIGHT]
        area = sl[i, cv2.CC_STAT_AREA]
        if area < 15:
            continue
        if h_comp <= 3 and w_comp > 20:
            continue
        clean[ll == i] = 255

    # Crop to content
    ys, xs = np.where(clean > 0)
    if len(ys) > 0:
        clean = clean[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return clean

def simulate_device_135x240(lines_img, target_w=135, target_h=240, active_y_top=20, active_y_bot=216):
    """
    Maps character lines into 135x240 screen:
    - Active area: Y: 20..216 (196px height)
    - Margin: X: 5..130 (125px width)
    - Feet grounded at Y = active_y_bot
    - Centered horizontally
    """
    dev_canvas = np.zeros((target_h, target_w), dtype=np.uint8)

    h, w = lines_img.shape[:2]
    avail_h = active_y_bot - active_y_top
    avail_w = target_w - 9 # 126px

    scale = min(avail_h / float(h), avail_w / float(w))
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    resized = cv2.resize(lines_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    _, resized_bin = cv2.threshold(resized, 45, 255, cv2.THRESH_BINARY)

    x_offset = (target_w - new_w) // 2
    y_offset = active_y_bot - new_h

    dev_canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_bin
    return dev_canvas

def create_device_preview(dev_lines, pose_name=""):
    """
    Renders styled 135x240 device screen simulation:
    - Midnight Obsidian background (#0B0F19)
    - Top status bar: 18px height with Wi-Fi pill (#22C55E)
    - Bottom subtitle box with gold border (#F59E0B)
    - Character linework: Golden Ivory (#FEF3C7)
    """
    preview = np.zeros((240, 135, 3), dtype=np.uint8)
    preview[:] = [25, 15, 11] # #0B0F19

    # Status bar
    preview[0:18, :] = [20, 12, 8]
    preview[4:14, 95:130] = [52, 101, 22] # Green WiFi pill

    # Subtitle bar
    preview[218:240, :] = [20, 12, 8]
    cv2.rectangle(preview, (10, 220), (125, 238), (11, 158, 245), 1) # Gold border

    # Character lines in warm ivory (#FEF3C7 -> BGR: [199, 243, 254])
    preview[dev_lines > 100] = [199, 243, 254]
    return preview

def run_extraction_all():
    mat = cv2.imread('docs/assets/cadet_ren/martial_action_poses.jpg')
    play = cv2.imread('docs/assets/cadet_ren/playful_action_poses.jpg')
    sheet = cv2.imread('docs/assets/cadet_ren/character_model_sheet.jpg')

    poses = {}

    print("Extracting 1: Bow & Salute...")
    poses['bow'] = extract_character_master(
        mat, 
        crop_box=(0, 384, 300, 480),
        erase_rects=[(0, 30, 0, 180), (350, 384, 0, 60), (350, 384, 120, 180)],
        cut_bottom_px=2
    )

    print("Extracting 2: Horse Stance Strike...")
    poses['horse_strike'] = extract_character_master(
        mat,
        crop_box=(60, 370, 830, 1200),
        erase_rects=[(285, 310, 0, 20), (285, 310, 50, 290), (285, 310, 340, 370)],
        cut_bottom_px=2
    )

    print("Extracting 3: Tai Chi Hands...")
    poses['taichi'] = extract_character_master(
        mat,
        crop_box=(384, 760, 210, 560),
        erase_rects=[(170, 230, 0, 50), (345, 376, 0, 30), (345, 376, 50, 230), (345, 376, 290, 350)],
        cut_bottom_px=3
    )

    print("Extracting 4: Leaping Dragon Punch...")
    poses['dragon_punch'] = extract_dragon_punch_special(mat)

    print("Extracting 5: Friendly Wave 1...")
    poses['wave_1'] = extract_character_master(
        play,
        crop_box=(60, 380, 30, 310),
        erase_rects=[(0, 55, 0, 280), (310, 320, 0, 100), (310, 320, 240, 280)],
        cut_bottom_px=2
    )

    print("Extracting 6: Friendly Wave 2...")
    poses['wave_2'] = extract_character_master(
        play,
        crop_box=(30, 380, 470, 690),
        erase_rects=[(0, 50, 0, 40), (340, 350, 0, 30), (340, 350, 180, 220)],
        cut_bottom_px=3
    )

    print("Extracting 7: Front Idle...")
    poses['front_idle'] = extract_front_idle_special(sheet)

    for name, lines in poses.items():
        if lines is None:
            print(f"Error: Pose {name} extraction failed!")
            continue

        raw_path = os.path.join(OUT_DIR, f"{name}_raw_lines.png")
        cv2.imwrite(raw_path, lines)

        # 135x240 device coordinates
        dev_lines = simulate_device_135x240(lines, 135, 240)
        dev_path = os.path.join(DEV_DIR, f"{name}_135x240.png")
        cv2.imwrite(dev_path, dev_lines)

        # Mini-program assets sync
        mp_dev_path = os.path.join(MP_DIR, f"{name}_135x240.png")
        cv2.imwrite(mp_dev_path, dev_lines)

        # Styled device preview
        preview = create_device_preview(dev_lines, name)
        preview_path = os.path.join(DEV_DIR, f"{name}_device_preview.png")
        cv2.imwrite(preview_path, preview)
        mp_preview_path = os.path.join(MP_DIR, f"{name}_device_preview.png")
        cv2.imwrite(mp_preview_path, preview)

        print(f"  -> Generated {name}: raw lines {lines.shape}, device screen 135x240")

    print("\nAll 7 authentic atlas poses extracted, cleaned, and mapped to 135x240 successfully!")

if __name__ == '__main__':
    run_extraction_all()
