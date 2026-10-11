#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/cadet_procedural_designer.py
====================================
Local High-Fidelity Procedural Character Designer for Cadet Ren (功夫学徒阿韧).
Renders all 15 procedural poses strictly aligned 1:1 with the official character
model sheet and the 7 gold-standard bitmap poses.

Features:
- Parametric 1:1 anatomy: Head-to-body ratio 1:1.1, total height 199px on 135x240 canvas.
- 16-color standard RGB565 palette matching cadet_ren concept artworks.
- True red panda x bunny features: Fluffy white cheek mask, teardrop brows, auburn tear stripes,
  glossy dual-star doe eyes, truffle nose, stand-collar tactical vest with gold paw emblem,
  flowing martial sash belt with dynamic ribbons, loose white silk lantern pants, navy shin wraps,
  and bushy ringed tail.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 16-Color RGB565 Standard Palette in RGB888
PALETTE = {
    "BG_OBSIDIAN": (11, 15, 25),        # 0x0862 Midnight Obsidian
    "FUR_AMBER": (205, 95, 38),          # 0xCAE4 #CD5F26 Warm Caramel Amber
    "FUR_KEYLIGHT": (230, 130, 60),      # 0xE407 Highlight
    "FUR_DARK": (135, 52, 22),           # 0x81A2 #873416 Auburn Shadow / Tear Stripes
    "CHOCOLATE": (43, 20, 14),           # 0x28A1 #2B140E Dark Chocolate Tips & Ink Line
    "FUR_WHITE": (250, 246, 238),        # 0xFFBD #FAF6EE Warm Ivory Cream
    "WHITE_SHD": (221, 216, 206),        # 0xDEF9 #DDD8CE Silk Fold Shadow
    "PANTS_WHITE": (240, 239, 234),      # 0xF77D #F0EFEA Martial Pants White
    "PANTS_SHD": (200, 196, 189),        # 0xCE37 #C8C4BD Pants Drape Shadow
    "VEST_NAVY": (26, 38, 62),           # 0x1927 #1A263E Midnight Navy Vest
    "VEST_DARK": (16, 24, 40),           # 0x10C5 Vest Crease Shadow
    "VEST_GOLD": (235, 185, 55),         # 0xEDB6 #EBB937 Imperial Gold Trim & Badge
    "WRAP_NAVY": (20, 30, 50),           # 0x10E6 Martial Wrist & Shin Wraps
    "EYE_IRIS": (115, 62, 30),           # 0x71E3 Amber Brown Iris
    "SPARKLE_WHITE": (255, 255, 255),    # 0xFFFF Double Star Sparkle
    "PAD_PINK": (250, 180, 170),         # 0xFDA5 Pink Paw Pads & Inner Ear Core
    "HUD_CYAN": (0, 255, 255),           # 0x07FF
    "HUD_GREEN": (0, 255, 0),            # 0x07E0
    "HUD_GOLD": (253, 224, 0),           # 0xFDE0
    "HUD_BG": (8, 65, 8),                # 0x0841
}

# The 15 Procedural Actions Metadata
PROCEDURAL_ACTIONS = [
    {"id": 3, "name": "sit", "name_cn": "萌萌坐下", "desc": "盘腿席地而坐，双手搭膝露粉嫩肉垫，端正双耳与水光大眼"},
    {"id": 4, "name": "stretch", "name_cn": "伸大懒腰", "desc": "双臂高举过头舒展脊椎，纵向拉伸身姿，舒适惬意表情"},
    {"id": 5, "name": "clap", "name_cn": "鼓掌拍手", "desc": "双爪在胸前欢快聚拢击掌，伴随星芒微粒子"},
    {"id": 6, "name": "cheer", "name_cn": "欢呼雀跃", "desc": "双臂V字高举扬起，雀跃微晃，欢欣鼓舞"},
    {"id": 7, "name": "jump", "name_cn": "弹性跳跃", "desc": "屈膝离地腾空跃起，双足悬空，腰带丝带飘扬"},
    {"id": 8, "name": "hands_up", "name_cn": "举手投降", "desc": "双爪高举两侧无辜投降状，耳朵微耷软萌"},
    {"id": 9, "name": "dance", "name_cn": "律动跳舞", "desc": "左右腰胯节奏摆动，手臂错落摆舞，经典迪斯尼律动"},
    {"id": 10, "name": "balance", "name_cn": "金鸡独立", "desc": "单脚独立支撑，另一足屈膝提起，双臂平展寻找重心平衡"},
    {"id": 11, "name": "lie", "name_cn": "趴地休息", "desc": "全身平趴伏地，头部贴近地面，四肢向外舒展放松"},
    {"id": 12, "name": "pushup", "name_cn": "俯卧撑", "desc": "双爪支撑地面呈平直俯卧姿态，上下起伏锻炼核心"},
    {"id": 17, "name": "moonwalk", "name_cn": "太空漫步", "desc": "滑步后撤身体前倾，脚底交替平滑后移"},
    {"id": 18, "name": "cyber_defense", "name_cn": "机甲护盾", "desc": "双手在胸前交叉架起，张开高能光子防护力场"},
    {"id": 19, "name": "turn_around", "name_cn": "转身秀尾", "desc": "180°背向镜头转体，展现战术马甲后背结构与蓬松大尾巴"},
    {"id": 20, "name": "spin", "name_cn": "华丽自旋", "desc": "360°芭蕾轴心连续自旋，四肢与丝带随离心力轻扬舒展"},
    {"id": 21, "name": "locked_try", "name_cn": "困惑挠头", "desc": "单爪挠头歪头思考，水光眼微歪，未解锁技能萌态反馈"},
]


class CadetProceduralRenderer:
    """High-Fidelity 1:1 Vector Character Renderer for Cadet Ren."""

    def __init__(self, width=135, height=240):
        self.w = width
        self.h = height

    def create_canvas(self):
        img = Image.new("RGB", (self.w, self.h), PALETTE["BG_OBSIDIAN"])
        draw = ImageDraw.Draw(img)
        return img, draw

    def draw_hud(self, draw, action_name, action_cn):
        # 1. Top status bar (0 ~ 18)
        draw.rectangle([0, 0, self.w, 18], fill=PALETTE["HUD_BG"])
        draw.text((4, 3), "VOL 75%", fill=PALETTE["HUD_CYAN"])
        # WiFi capsule
        draw.rectangle([94, 2, 131, 16], fill=PALETTE["HUD_GREEN"])
        draw.text((99, 3), "WiFi", fill=(0, 0, 0))

        # 2. Action banner pill (20 ~ 36)
        draw.rounded_rectangle([7, 20, 127, 36], radius=4, fill=PALETTE["HUD_BG"], outline=PALETTE["HUD_CYAN"])
        text = f"[ACT: {action_name}]"
        draw.text((67 - len(text) * 3, 23), text, fill=PALETTE["HUD_CYAN"])

        # 3. Bottom status bar (220 ~ 240)
        draw.rectangle([0, 220, self.w, 240], fill=(0, 0, 0))
        draw.text((3, 223), "Lv.5 Legend | 56300P | 83F", fill=PALETTE["HUD_GOLD"])
        # EXP progress bar
        draw.rounded_rectangle([3, 236, 131, 238], radius=2, fill=PALETTE["HUD_CYAN"])

    def draw_tail(self, draw, tx, ty, tr=9, flip_x=False, curve=-1):
        """Draws the signature 6-segment bushy red panda tail with alternating caramel and dark auburn rings."""
        segments = [
            (tx, ty, tr + 3),
            (tx + curve * 6, ty - 2, tr + 4),
            (tx + curve * 12, ty - 6, tr + 5),
            (tx + curve * 17, ty - 12, tr + 5),
            (tx + curve * 19, ty - 19, tr + 4),
            (tx + curve * 18, ty - 26, tr + 3),
        ]
        colors = [
            PALETTE["FUR_AMBER"],
            PALETTE["FUR_DARK"],
            PALETTE["FUR_AMBER"],
            PALETTE["FUR_DARK"],
            PALETTE["FUR_AMBER"],
            PALETTE["CHOCOLATE"],
        ]
        for i, (sx, sy, sr) in enumerate(segments):
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=colors[i], outline=PALETTE["CHOCOLATE"])

    def draw_ears(self, draw, cx, cy, ear_tilt=0, flop_l=0, flop_r=0, back_view=False):
        """Draws upright bunny ears with dark chocolate tips, ivory inner fluff, and pink core."""
        ear_configs = [
            (cx - 15, cy - 28 + flop_l, -6 + ear_tilt),  # Left ear
            (cx + 15, cy - 28 + flop_r, 6 + ear_tilt),   # Right ear
        ]
        for ex, ey, tilt in ear_configs:
            rx, ry = 9, 20
            # Outer ear caramel
            draw.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
            # Chocolate tip
            draw.ellipse([ex - 6, ey - ry, ex + 6, ey - ry + 12], fill=PALETTE["CHOCOLATE"])
            if not back_view:
                # Ivory inner fluff
                draw.ellipse([ex - 6, ey - ry + 7, ex + 6, ey + ry - 4], fill=PALETTE["FUR_WHITE"])
                # Peach-pink core
                draw.ellipse([ex - 3, ey - ry + 11, ex + 3, ey + ry - 8], fill=PALETTE["PAD_PINK"])
            else:
                # Back view ear furrow
                draw.line([ex, ey - ry + 4, ex, ey + ry - 4], fill=PALETTE["FUR_DARK"], width=1)

    def draw_head_and_face(self, draw, cx, cy, mood="normal", eye_gaze=(0, 0), mouth_open=False, back_view=False, head_tilt=0):
        """Draws the iconic Cadet Ren head with chubby cheek tufts, doe eyes, red panda mask, and truffle nose."""
        rx_head, ry_head = 27, 23

        if back_view:
            # Back view: Round head with cranial fur tufts
            draw.ellipse([cx - rx_head, cy - ry_head, cx + rx_head, cy + ry_head], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
            draw.line([cx - 4, cy - ry_head + 2, cx, cy - ry_head - 4], fill=PALETTE["CHOCOLATE"], width=1)
            draw.line([cx, cy - ry_head - 4, cx + 4, cy - ry_head + 2], fill=PALETTE["CHOCOLATE"], width=1)
            return

        # 1. Head base oval with warm caramel fur
        draw.ellipse([cx - rx_head, cy - ry_head, cx + rx_head, cy + ry_head], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
        # Forehead crown fluff
        draw.polygon([(cx - 4, cy - ry_head + 1), (cx, cy - ry_head - 5), (cx + 4, cy - ry_head + 1)], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])

        # 2. Signature Red Panda Cheek Tufts & Face Mask (Wide Ivory Cheeks with Soft Downward Tufts)
        # Left cheek patch & tuft
        draw.ellipse([cx - 26, cy - 1, cx - 2, cy + 18], fill=PALETTE["FUR_WHITE"], outline=PALETTE["CHOCOLATE"])
        draw.polygon([(cx - 24, cy + 5), (cx - 30, cy + 11), (cx - 20, cy + 16)], fill=PALETTE["FUR_WHITE"], outline=PALETTE["CHOCOLATE"])
        draw.polygon([(cx - 22, cy + 12), (cx - 27, cy + 17), (cx - 16, cy + 20)], fill=PALETTE["FUR_WHITE"], outline=PALETTE["CHOCOLATE"])
        # Right cheek patch & tuft
        draw.ellipse([cx + 2, cy - 1, cx + 26, cy + 18], fill=PALETTE["FUR_WHITE"], outline=PALETTE["CHOCOLATE"])
        draw.polygon([(cx + 24, cy + 5), (cx + 30, cy + 11), (cx + 20, cy + 16)], fill=PALETTE["FUR_WHITE"], outline=PALETTE["CHOCOLATE"])
        draw.polygon([(cx + 22, cy + 12), (cx + 27, cy + 17), (cx + 16, cy + 20)], fill=PALETTE["FUR_WHITE"], outline=PALETTE["CHOCOLATE"])

        # 3. Warm Ivory Muzzle / Snout (Centered, compact, soft smile)
        snout_y = cy + 8
        draw.ellipse([cx - 9, snout_y - 5, cx + 9, snout_y + 6], fill=PALETTE["FUR_WHITE"])
        # Truffle black button nose
        draw.ellipse([cx - 3, snout_y - 4, cx + 3, snout_y - 1], fill=PALETTE["CHOCOLATE"])
        draw.point((cx - 1, snout_y - 3), fill=(255, 255, 255))
        # Philtrum and sweet cat smile
        draw.line([cx, snout_y - 1, cx, snout_y + 2], fill=PALETTE["CHOCOLATE"], width=1)
        draw.arc([cx - 5, snout_y, cx, snout_y + 5], start=20, end=160, fill=PALETTE["CHOCOLATE"])
        draw.arc([cx, snout_y, cx + 5, snout_y + 5], start=20, end=160, fill=PALETTE["CHOCOLATE"])

        # 4. White Teardrop Eyebrows
        draw.ellipse([cx - 13, cy - 12, cx - 8, cy - 8], fill=PALETTE["FUR_WHITE"])
        draw.ellipse([cx + 8, cy - 12, cx + 13, cy - 8], fill=PALETTE["FUR_WHITE"])

        # 5. Auburn Tear Stripes (Eye to jawline)
        draw.line([cx - 15, cy - 1, cx - 11, cy + 9], fill=PALETTE["FUR_DARK"], width=2)
        draw.line([cx + 15, cy - 1, cx + 11, cy + 9], fill=PALETTE["FUR_DARK"], width=2)

        # 6. Pink Cheeks (Blush)
        draw.ellipse([cx - 21, cy + 7, cx - 14, cy + 13], fill=PALETTE["PAD_PINK"])
        draw.ellipse([cx + 14, cy + 7, cx + 21, cy + 13], fill=PALETTE["PAD_PINK"])

        # 7. Fine Whiskers
        draw.line([cx - 13, snout_y + 1, cx - 23, snout_y + 2], fill=PALETTE["CHOCOLATE"], width=1)
        draw.line([cx - 13, snout_y + 3, cx - 23, snout_y + 5], fill=PALETTE["CHOCOLATE"], width=1)
        draw.line([cx + 13, snout_y + 1, cx + 23, snout_y + 2], fill=PALETTE["CHOCOLATE"], width=1)
        draw.line([cx + 13, snout_y + 3, cx + 23, snout_y + 5], fill=PALETTE["CHOCOLATE"], width=1)

        # 8. High-Fidelity Doe Eyes (Dual-Star Anime Glossy Eyes)
        lx, ly = cx - 11, cy - 2
        rx, ry = cx + 11, cy - 2
        gx, gy = eye_gaze

        for ex, ey in [(lx, ly), (rx, ry)]:
            # Black glossy eye socket
            draw.rounded_rectangle([ex - 5, ey - 7, ex + 5, ey + 7], radius=4, fill=(15, 20, 30), outline=PALETTE["CHOCOLATE"])
            # Amber iris
            draw.ellipse([ex - 4 + gx, ey - 3 + gy, ex + 4 + gx, ey + 5 + gy], fill=PALETTE["EYE_IRIS"])
            # Primary star sparkle highlight
            draw.ellipse([ex - 3 + gx, ey - 4 + gy, ex + gx, ey - 1 + gy], fill=PALETTE["SPARKLE_WHITE"])
            # Secondary catchlight dot
            draw.point((ex + 2 + gx, ey + 2 + gy), fill=PALETTE["SPARKLE_WHITE"])
            # Eyelash upper line
            draw.line([ex - 5, ey - 8, ex + 5, ey - 8], fill=PALETTE["CHOCOLATE"], width=1)

    def draw_tactical_vest(self, draw, bx, by_top, by_bot, bw=23, back_view=False):
        """Draws the fitted Midnight Navy Tactical Vest seamlessly under the chin."""
        top_y = by_top
        bot_y = by_bot

        if back_view:
            # Back vest: Midnight navy with vertical center seam and gold back loop
            draw.rectangle([bx - bw, top_y, bx + bw, bot_y], fill=PALETTE["VEST_NAVY"], outline=PALETTE["CHOCOLATE"])
            draw.line([bx - bw, top_y, bx + bw, top_y], fill=PALETTE["VEST_GOLD"], width=2)
            draw.line([bx - bw, bot_y, bx + bw, bot_y], fill=PALETTE["VEST_GOLD"], width=2)
            draw.line([bx, top_y, bx, bot_y], fill=PALETTE["VEST_DARK"], width=1)
            # Tactical back loop harness
            draw.rounded_rectangle([bx - 3, top_y + 6, bx + 3, top_y + 24], radius=2, outline=PALETTE["VEST_GOLD"], width=1)
            return

        # Front vest: Fitted silhouette with slight waist taper
        draw.polygon([
            (bx - bw + 3, top_y), (bx + bw - 3, top_y),
            (bx + bw, bot_y), (bx - bw, bot_y)
        ], fill=PALETTE["VEST_NAVY"], outline=PALETTE["CHOCOLATE"])

        # Stand-up collar with gold border directly under chin
        draw.rectangle([bx - 9, top_y - 2, bx + 9, top_y + 3], fill=PALETTE["VEST_NAVY"], outline=PALETTE["CHOCOLATE"])
        draw.line([bx - 9, top_y - 2, bx + 9, top_y - 2], fill=PALETTE["VEST_GOLD"], width=1)

        # Gold piping on armhole lateral borders and bottom hem
        draw.line([bx - bw + 3, top_y, bx - bw, bot_y], fill=PALETTE["VEST_GOLD"], width=1)
        draw.line([bx + bw - 3, top_y, bx + bw, bot_y], fill=PALETTE["VEST_GOLD"], width=1)
        draw.line([bx - bw, bot_y, bx + bw, bot_y], fill=PALETTE["VEST_GOLD"], width=2)

        # Golden Paw Print Emblem on chest
        badge_y = top_y + 16
        draw.ellipse([bx - 5, badge_y - 3, bx + 5, badge_y + 4], fill=PALETTE["VEST_GOLD"])
        draw.point((bx - 4, badge_y - 5), fill=PALETTE["VEST_GOLD"])
        draw.point((bx - 1, badge_y - 6), fill=PALETTE["VEST_GOLD"])
        draw.point((bx + 1, badge_y - 6), fill=PALETTE["VEST_GOLD"])
        draw.point((bx + 4, badge_y - 5), fill=PALETTE["VEST_GOLD"])

        # Utility pockets
        draw.rectangle([bx - bw + 3, bot_y - 9, bx - bw + 9, bot_y - 3], outline=PALETTE["VEST_GOLD"], width=1)
        draw.rectangle([bx + bw - 9, bot_y - 9, bx + bw - 3, bot_y - 3], outline=PALETTE["VEST_GOLD"], width=1)

    def draw_sash_and_ribbons(self, draw, bx, by_bot, bw=23, ribbon_sway=0):
        """Draws the martial arts sash belt with gold buckle and dynamic hanging ribbons."""
        sash_y = by_bot
        draw.rectangle([bx - bw, sash_y - 2, bx + bw, sash_y + 4], fill=PALETTE["VEST_NAVY"], outline=PALETTE["CHOCOLATE"])
        draw.line([bx - bw, sash_y - 2, bx + bw, sash_y - 2], fill=PALETTE["VEST_GOLD"], width=1)
        # Gold square buckle
        draw.rectangle([bx - 4, sash_y - 3, bx + 4, sash_y + 4], fill=PALETTE["VEST_GOLD"])

        # Dynamic hanging ribbon tails
        r1_x = bx - 4 + int(ribbon_sway)
        r2_x = bx + 4 + int(ribbon_sway * 0.8)
        draw.polygon([(bx - 3, sash_y + 4), (r1_x, sash_y + 20), (bx, sash_y + 15)], fill=PALETTE["VEST_NAVY"], outline=PALETTE["CHOCOLATE"])
        draw.polygon([(bx + 1, sash_y + 4), (r2_x, sash_y + 19), (bx + 5, sash_y + 14)], fill=PALETTE["VEST_NAVY"], outline=PALETTE["CHOCOLATE"])

    def draw_lantern_pants(self, draw, bx, by, leg_l_xy, leg_r_xy, sitting=False):
        """Draws the baggy white silk kung fu lantern trousers with draped folds and shadow."""
        if sitting:
            # Sitting pose: Outward folded baggy pants exposing foot pads
            # Left leg folded
            draw.ellipse([bx - 26, by + 4, bx - 4, by + 22], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
            draw.line([bx - 20, by + 10, bx - 8, by + 16], fill=PALETTE["PANTS_SHD"], width=1)
            # Right leg folded
            draw.ellipse([bx + 4, by + 4, bx + 26, by + 22], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
            draw.line([bx + 20, by + 10, bx + 8, by + 16], fill=PALETTE["PANTS_SHD"], width=1)
            # Center groin drape
            draw.polygon([(bx - 8, by + 3), (bx, by + 12), (bx + 8, by + 3)], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
            return

        lx, ly = leg_l_xy
        rx, ry = leg_r_xy

        # Left baggy trouser leg
        draw.polygon([(bx - 14, by + 4), (lx - 8, ly - 8), (lx + 6, ly - 8), (bx - 2, by + 4)], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
        # Right baggy trouser leg
        draw.polygon([(bx + 2, by + 4), (rx - 6, ry - 8), (rx + 8, ry - 8), (bx + 14, by + 4)], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
        # Bulging knee volume
        draw.ellipse([bx - 18, (by + ly) // 2 - 8, bx - 2, (by + ly) // 2 + 8], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
        draw.ellipse([bx + 2, (by + ry) // 2 - 8, bx + 18, (by + ry) // 2 + 8], fill=PALETTE["PANTS_WHITE"], outline=PALETTE["CHOCOLATE"])
        # Silk fold shadows
        draw.line([bx - 10, by + 8, lx - 2, ly - 10], fill=PALETTE["PANTS_SHD"], width=1)
        draw.line([bx + 10, by + 8, rx + 2, ry - 10], fill=PALETTE["PANTS_SHD"], width=1)

    def draw_shin_wraps_and_foot(self, draw, fx, fy, sitting=False):
        """Draws midnight navy shin wraps with gold hem, amber paws, and pink pads."""
        if sitting:
            # Foot paws facing forward showing plump pink pads
            draw.ellipse([fx - 7, fy - 6, fx + 7, fy + 6], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
            # Pink pad center
            draw.ellipse([fx - 4, fy - 2, fx + 4, fy + 4], fill=PALETTE["PAD_PINK"])
            # 3 pink toe beans
            draw.point((fx - 4, fy - 4), fill=PALETTE["PAD_PINK"])
            draw.point((fx, fy - 5), fill=PALETTE["PAD_PINK"])
            draw.point((fx + 4, fy - 4), fill=PALETTE["PAD_PINK"])
            return

        # Standing / moving leg: Shin wraps
        draw.rectangle([fx - 6, fy - 14, fx + 6, fy - 3], fill=PALETTE["WRAP_NAVY"], outline=PALETTE["CHOCOLATE"])
        draw.line([fx - 6, fy - 3, fx + 6, fy - 3], fill=PALETTE["VEST_GOLD"], width=1)
        # Criss-cross wrap line
        draw.line([fx - 5, fy - 13, fx + 5, fy - 5], fill=PALETTE["VEST_NAVY"], width=1)

        # Foot paw
        draw.ellipse([fx - 7, fy - 4, fx + 7, fy + 4], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
        # Pink toe beans
        draw.point((fx - 3, fy + 1), fill=PALETTE["PAD_PINK"])
        draw.point((fx, fy + 2), fill=PALETTE["PAD_PINK"])
        draw.point((fx + 3, fy + 1), fill=PALETTE["PAD_PINK"])

    def draw_arm_and_paw(self, draw, sx, sy, px, py, is_punch=False):
        """Draws white sleeve upper arm, navy forearm wrap, amber paw, and pink pads."""
        # Midpoint elbow
        mx = (sx + px) // 2
        my = (sy + py) // 2

        # 1. White kung fu sleeve
        draw.line([sx, sy, mx, my], fill=PALETTE["PANTS_WHITE"], width=8)
        draw.line([sx, sy, mx, my], fill=PALETTE["CHOCOLATE"], width=1)
        # 2. Forearm navy wrap
        draw.line([mx, my, px, py], fill=PALETTE["WRAP_NAVY"], width=7)
        draw.line([mx, my, px, py], fill=PALETTE["CHOCOLATE"], width=1)

        # 3. Amber paw & pink pads
        if is_punch:
            # Clenched fist
            draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
            draw.line([px - 3, py, px + 3, py], fill=PALETTE["CHOCOLATE"], width=1)
        else:
            # Open palm / friendly paw
            draw.ellipse([px - 6, py - 5, px + 6, py + 5], fill=PALETTE["FUR_AMBER"], outline=PALETTE["CHOCOLATE"])
            draw.ellipse([px - 3, py - 2, px + 3, py + 3], fill=PALETTE["PAD_PINK"])
            draw.point((px - 3, py - 4), fill=PALETTE["PAD_PINK"])
            draw.point((px, py - 4), fill=PALETTE["PAD_PINK"])
            draw.point((px + 3, py - 4), fill=PALETTE["PAD_PINK"])

    def render_pose(self, action_id, action_name, action_cn):
        """Renders one complete 135x240 frame for a given procedural action."""
        img, draw = self.create_canvas()
        self.draw_hud(draw, action_name, action_cn)

        cx, cy = 67, 80     # Head center
    def render_pose(self, action_id, action_name, action_cn):
        """Renders one complete 135x240 frame for a given procedural action."""
        img, draw = self.create_canvas()
        self.draw_hud(draw, action_name, action_cn)

        # Baseline coordinates matching 00_idle.png
        cx, cy = 67, 78     # Head center
        bx = 67

        # Ground contact shadow
        draw.ellipse([bx - 26, 210, bx + 26, 218], fill=(20, 25, 38))

        if action_name == "sit":
            # 萌萌坐下: 席地盘腿，身姿整体下沉
            cy_sit = cy + 18
            v_top = cy_sit + 22
            v_bot = v_top + 38
            # 1. Background ringed tail
            self.draw_tail(draw, bx - 16, v_bot + 6, tr=9, curve=-1)
            # 2. Sitting lantern pants
            self.draw_lantern_pants(draw, bx, v_bot, None, None, sitting=True)
            # 3. Tactical vest & sash
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22, ribbon_sway=0)
            # 4. Arms resting on knees
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 20, v_bot + 12)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 20, v_bot + 12)
            # 5. Paw feet facing forward
            self.draw_shin_wraps_and_foot(draw, bx - 22, v_bot + 16, sitting=True)
            self.draw_shin_wraps_and_foot(draw, bx + 22, v_bot + 16, sitting=True)
            # 6. Ears & Head
            self.draw_ears(draw, cx, cy_sit)
            self.draw_head_and_face(draw, cx, cy_sit, mood="happy")

        elif action_name == "stretch":
            # 伸大懒腰: 双臂仰天高举，拉伸躯干
            cy_s = cy - 4
            v_top = cy_s + 22
            v_bot = v_top + 50
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=8, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=20)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=20, ribbon_sway=1)
            # Arms stretched high
            self.draw_arm_and_paw(draw, bx - 16, v_top + 6, bx - 18, cy_s - 42)
            self.draw_arm_and_paw(draw, bx + 16, v_top + 6, bx + 18, cy_s - 42)
            self.draw_ears(draw, cx, cy_s, ear_tilt=-2)
            self.draw_head_and_face(draw, cx, cy_s, mood="comfort", eye_gaze=(0, -1))

        elif action_name == "clap":
            # 鼓掌拍手: 双手在胸前聚拢
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22, ribbon_sway=0)
            # Arms clapping in front of chest
            self.draw_arm_and_paw(draw, bx - 18, v_top + 12, bx - 4, v_top + 28)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 12, bx + 4, v_top + 28)
            # Sparkle particles
            draw.point((bx, v_top + 26), fill=(255, 255, 255))
            draw.point((bx - 2, v_top + 24), fill=PALETTE["VEST_GOLD"])
            draw.point((bx + 2, v_top + 24), fill=PALETTE["VEST_GOLD"])
            self.draw_ears(draw, cx, cy)
            self.draw_head_and_face(draw, cx, cy, mood="happy")

        elif action_name == "cheer":
            # 欢呼雀跃: V字高举双手
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22, ribbon_sway=2)
            # Arms V-shape up
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 26, cy - 26)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 26, cy - 26)
            self.draw_ears(draw, cx, cy, ear_tilt=2)
            self.draw_head_and_face(draw, cx, cy, mood="happy")

        elif action_name == "jump":
            # 弹性跳跃: 腾空跃起
            cy_j = cy - 16
            v_top = cy_j + 22
            v_bot = v_top + 48
            # Ground shadow smaller
            draw.ellipse([bx - 16, 210, bx + 16, 216], fill=(20, 25, 38))
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            # Legs tucked
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 12, 196), (bx + 12, 196))
            self.draw_shin_wraps_and_foot(draw, bx - 12, 196)
            self.draw_shin_wraps_and_foot(draw, bx + 12, 196)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=21)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=21, ribbon_sway=4)
            # Arms raised with motion
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 24, cy_j - 20)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 24, cy_j - 20)
            self.draw_ears(draw, cx, cy_j)
            self.draw_head_and_face(draw, cx, cy_j, mood="energetic")

        elif action_name == "hands_up":
            # 举手投降
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22)
            # Hands up sideways
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 26, cy - 8)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 26, cy - 8)
            self.draw_ears(draw, cx, cy, flop_l=3, flop_r=3)
            self.draw_head_and_face(draw, cx, cy, mood="innocent")

        elif action_name == "dance":
            # 律动跳舞: 身体微侧，手臂错落
            bx_d = bx + 4
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx_d - 18, v_bot + 10, tr=9, curve=-1)
            self.draw_lantern_pants(draw, bx_d, v_bot, (bx_d - 16, 212), (bx_d + 12, 206))
            self.draw_shin_wraps_and_foot(draw, bx_d - 16, 212)
            self.draw_shin_wraps_and_foot(draw, bx_d + 12, 206)
            self.draw_tactical_vest(draw, bx_d, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx_d, v_bot, bw=22, ribbon_sway=3)
            # Asymmetrical arm swing
            self.draw_arm_and_paw(draw, bx_d - 18, v_top + 10, bx_d - 24, cy - 18)
            self.draw_arm_and_paw(draw, bx_d + 18, v_top + 10, bx_d + 22, v_top + 34)
            self.draw_ears(draw, cx + 4, cy, ear_tilt=-3)
            self.draw_head_and_face(draw, cx + 4, cy, mood="happy")

        elif action_name == "balance":
            # 金鸡独立: 单腿站立，一腿抬起
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            # Left leg lifted, right leg standing
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 16, 186), (bx + 12, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 16, 186)
            self.draw_shin_wraps_and_foot(draw, bx + 12, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22, ribbon_sway=-2)
            # Arms outstretched horizontally for balance
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 30, v_top + 8)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 30, v_top + 8)
            self.draw_ears(draw, cx, cy)
            self.draw_head_and_face(draw, cx, cy, mood="focused")

        elif action_name == "lie":
            # 趴地休息: 伏地舒展
            cy_l = 142
            v_top = cy_l + 20
            v_bot = v_top + 30
            draw.ellipse([bx - 32, 210, bx + 32, 218], fill=(20, 25, 38))
            self.draw_tail(draw, bx - 28, v_bot + 4, tr=8, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 22, 206), (bx + 22, 206))
            self.draw_shin_wraps_and_foot(draw, bx - 22, 206)
            self.draw_shin_wraps_and_foot(draw, bx + 22, 206)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=24)
            self.draw_arm_and_paw(draw, bx - 20, v_top + 6, bx - 28, v_bot + 4)
            self.draw_arm_and_paw(draw, bx + 20, v_top + 6, bx + 28, v_bot + 4)
            self.draw_ears(draw, cx, cy_l, flop_l=6, flop_r=6)
            self.draw_head_and_face(draw, cx, cy_l, mood="sleepy")

        elif action_name == "pushup":
            # 俯卧撑
            cy_p = 132
            v_top = cy_p + 20
            v_bot = v_top + 34
            draw.ellipse([bx - 30, 210, bx + 30, 218], fill=(20, 25, 38))
            self.draw_tail(draw, bx + 24, v_bot + 4, tr=7, curve=1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx + 18, 206), (bx + 26, 206))
            self.draw_shin_wraps_and_foot(draw, bx + 18, 206)
            self.draw_shin_wraps_and_foot(draw, bx + 26, 206)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=23)
            self.draw_arm_and_paw(draw, bx - 14, v_top + 6, bx - 18, v_bot + 12)
            self.draw_arm_and_paw(draw, bx + 14, v_top + 6, bx + 10, v_bot + 12)
            self.draw_ears(draw, cx - 10, cy_p)
            self.draw_head_and_face(draw, cx - 10, cy_p, mood="effort")

        elif action_name == "moonwalk":
            # 太空漫步: 滑步后撤身体前倾
            bx_m = bx - 6
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx_m + 18, v_bot + 10, tr=9, curve=1)
            self.draw_lantern_pants(draw, bx_m, v_bot, (bx_m - 12, 212), (bx_m + 16, 208))
            self.draw_shin_wraps_and_foot(draw, bx_m - 12, 212)
            self.draw_shin_wraps_and_foot(draw, bx_m + 16, 208)
            self.draw_tactical_vest(draw, bx_m, v_top, v_bot, bw=21)
            self.draw_sash_and_ribbons(draw, bx_m, v_bot, bw=21, ribbon_sway=-3)
            self.draw_arm_and_paw(draw, bx_m - 18, v_top + 10, bx_m - 22, v_top + 32)
            self.draw_arm_and_paw(draw, bx_m + 18, v_top + 10, bx_m + 22, cy - 10)
            self.draw_ears(draw, cx - 6, cy, ear_tilt=3)
            self.draw_head_and_face(draw, cx - 6, cy, mood="cool")

        elif action_name == "cyber_defense":
            # 机甲护盾: 双臂胸前交叉架起
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22)
            # Arms crossed at chest
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx + 10, v_top + 24, is_punch=True)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx - 10, v_top + 24, is_punch=True)
            # Energy shield ring
            draw.arc([bx - 32, v_top - 6, bx + 32, v_bot + 18], start=20, end=160, fill=PALETTE["HUD_CYAN"], width=2)
            draw.arc([bx - 35, v_top - 9, bx + 35, v_bot + 21], start=40, end=140, fill=PALETTE["HUD_GREEN"], width=1)
            self.draw_ears(draw, cx, cy)
            self.draw_head_and_face(draw, cx, cy, mood="determined")

        elif action_name == "turn_around":
            # 转身秀尾: 180°背向镜头
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22, back_view=True)
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 22, v_top + 34)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 22, v_top + 34)
            # Big fluffy tail in foreground
            self.draw_tail(draw, bx - 10, v_bot - 4, tr=10, curve=-1)
            self.draw_ears(draw, cx, cy, back_view=True)
            self.draw_head_and_face(draw, cx, cy, back_view=True)

        elif action_name == "spin":
            # 华丽自旋: 360°旋转 T 字平衡
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx + 16, v_bot + 10, tr=8, curve=1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 6, 212), (bx + 12, 204))
            self.draw_shin_wraps_and_foot(draw, bx - 6, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 12, 204)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=20)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=20, ribbon_sway=4)
            # T-arms outstretched
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 28, v_top + 6)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, bx + 28, v_top + 6)
            self.draw_ears(draw, cx, cy)
            self.draw_head_and_face(draw, cx, cy, mood="graceful")

        elif action_name == "locked_try":
            # 困惑挠头: 单爪挠头，歪头，问号特效
            v_top = cy + 22
            v_bot = v_top + 48
            self.draw_tail(draw, bx - 18, v_bot + 10, tr=9, curve=-1)
            self.draw_lantern_pants(draw, bx, v_bot, (bx - 14, 212), (bx + 14, 212))
            self.draw_shin_wraps_and_foot(draw, bx - 14, 212)
            self.draw_shin_wraps_and_foot(draw, bx + 14, 212)
            self.draw_tactical_vest(draw, bx, v_top, v_bot, bw=22)
            self.draw_sash_and_ribbons(draw, bx, v_bot, bw=22)
            # Left arm normal, right arm scratching head
            self.draw_arm_and_paw(draw, bx - 18, v_top + 10, bx - 20, v_top + 34)
            self.draw_arm_and_paw(draw, bx + 18, v_top + 10, cx + 18, cy - 14)
            self.draw_ears(draw, cx, cy, flop_r=5, ear_tilt=4)
            self.draw_head_and_face(draw, cx, cy, mood="confused")
            # Question mark effect
            draw.text((cx - 24, cy - 26), "?", fill=PALETTE["HUD_GOLD"])

        return img


def main():
    renderer = CadetProceduralRenderer()
    out_dir = os.path.abspath("docs/assets/cadet_procedural_redesign")
    raw_dir = os.path.join(out_dir, "135x240")
    hires_dir = os.path.join(out_dir, "hires_3x")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(hires_dir, exist_ok=True)

    print("==================================================")
    print("🎨 Cadet Ren 15套过程化动作高保真本地设计生成流水线")
    print(f"Output directory: {out_dir}")
    print("==================================================")

    for item in PROCEDURAL_ACTIONS:
        idx = item["id"]
        name = item["name"]
        name_cn = item["name_cn"]

        img = renderer.render_pose(idx, name, name_cn)
        raw_path = os.path.join(raw_dir, f"{idx:02d}_{name}.png")
        img.save(raw_path)

        hires_img = img.resize((135 * 3, 240 * 3), Image.NEAREST)
        hires_path = os.path.join(hires_dir, f"hires_{idx:02d}_{name}.png")
        hires_img.save(hires_path)

        print(f"[OK] #{idx:02d} {name_cn:<6} ({name:<14}) -> {os.path.basename(raw_path)}")

    print(f"\n🎉 15 套过程化动作本地设计图全部生成完毕！")


if __name__ == "__main__":
    main()
