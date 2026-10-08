#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_cadet_ren_pure_character_gifs.py
------------------------------------------------
Generates pure, complete-character cinema-grade animated GIFs for Cadet Ren (阿韧).
Every single frame renders a 100% complete character (ears to paws, tail, vest, pants),
completely eliminating rectangular background cutouts.

Features:
- Full Disney & Pixar 12 Principles (Squash & Stretch, Secondary Motion, Overlapping Action)
- 1:1 Color & Anatomy matching character_model_sheet.jpg & kungfu_cadet_concept.jpg
- Saves both transparent/clean-slate high-res GIFs and exact 135x240 device-canvas GIFs
"""

import os
import math
from PIL import Image, ImageDraw

# 调色板 (精准匹配 concept_hero.png 与 model_front.png)
C_FUR_AMBER = (205, 95, 38)     # #CD5F26 暖焦糖红熊猫毛色
C_FUR_DARK  = (135, 52, 22)     # #873416 深棕红暗部/泪痕/尾纹
C_FUR_WHITE = (248, 246, 242)   # #F8F6F2 象牙白面具/内耳白绒/白功夫衫裤
C_WHITE_SHD = (205, 202, 212)   # #CDCADA 白布料/白毛暗部
C_VEST_NAVY = (26, 38, 62)      # #1A263E 午夜海军蓝战术马甲/腰封
C_VEST_DARK = (16, 24, 40)      # #101828 马甲阴影
C_VEST_GOLD = (235, 185, 55)    # #EBB937 皇家香草亮金滚边与金爪印
C_WRAP_NAVY = (20, 30, 50)      # #141E32 紧固功夫绑带
C_EAR_TIP   = (55, 28, 18)      # #371C12 耳尖黑巧深斑
C_EYE_IRIS  = (115, 62, 30)     # #733E1E 琥珀深棕灵动虹膜
C_NOSE_DARK = (40, 22, 20)      # #281614 松露鼻头
C_PAD_PINK  = (250, 180, 170)   # #FAB4AA 樱粉肉垫
C_BG_DARK   = (15, 23, 42)      # #0F172A 优雅午夜蓝基底

def render_character_frame(
    width=270, height=480,
    body_offset_y=0.0,
    body_squash=1.0,
    leg_spread=18.0,
    l_arm_mode="fist_waist", # "fist_waist", "push_palm", "wave", "cloud_hand_up", "cloud_hand_down"
    r_arm_mode="push_palm",  # "push_palm", "dragon_punch", "fist_waist", "cloud_hand_down", "cloud_hand_up"
    l_arm_progress=0.0,
    r_arm_progress=0.0,
    ear_flop=0.0,
    tail_sway=0.0,
    sash_sway=0.0,
    eye_gaze=(0.0, 0.0),
    blink=0.0,
    mouth_open=0.0,
    action_label="",
    show_device_hud=True
):
    """
    Renders one full-body character frame with cinema-grade volumetric shading.
    Canvas resolution: width x height (default 270x480, 2x M5StickS3).
    """
    SS = 2
    W = width * SS
    H = height * SS
    scale = (width / 135.0) * SS

    def s(v): return int(v * scale)
    def sf(v): return float(v * scale)

    im = Image.new('RGBA', (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(im)

    bx = sf(67.5)
    by = sf(134.0 + body_offset_y)

    # 1. 地面接触软阴影 (悬浮与重心动态缩放)
    sh_w = sf(32.0 * body_squash)
    sh_y = sf(134.0 + 50.0)
    draw.ellipse([bx - sh_w, sh_y - sf(5.5), bx + sh_w, sh_y + sf(5.5)], fill=(6, 9, 16, 210))

    # 2. 蓬松红熊猫大尾巴 (Background: S-curve + 3 dark red-auburn bands + dynamic sway)
    tx_base = bx - sf(12.0)
    ty_base = by + sf(16.0)
    t_sw = tail_sway * sf(6.0)
    tail_segments = [
        (tx_base, ty_base, sf(11.0), sf(11.0), C_FUR_AMBER),
        (tx_base - sf(12) + t_sw * 0.2, ty_base - sf(2), sf(13.0), sf(13.0), C_FUR_DARK),
        (tx_base - sf(22) + t_sw * 0.5, ty_base - sf(8), sf(14.5), sf(14.5), C_FUR_AMBER),
        (tx_base - sf(30) + t_sw * 0.8, ty_base - sf(17), sf(15.0), sf(15.0), C_FUR_DARK),
        (tx_base - sf(35) + t_sw * 1.0, ty_base - sf(28), sf(14.0), sf(14.0), C_FUR_AMBER),
        (tx_base - sf(36) + t_sw * 1.2, ty_base - sf(38), sf(12.0), sf(13.0), C_FUR_DARK),
    ]
    for seg_x, seg_y, rx, ry, col in tail_segments:
        draw.ellipse([seg_x - rx, seg_y - ry, seg_x + rx, seg_y + ry], fill=col)

    # 3. 象牙白宽松丝绸灯笼裤 (Baggy Kung Fu Trousers)
    hip_y = by + sf(14.0)
    foot_ly = sf(134.0 + 48.0)
    foot_ry = sf(134.0 + 48.0)
    foot_lx = bx - sf(leg_spread)
    foot_rx = bx + sf(leg_spread)

    for flx, sgn in [(foot_lx, -1), (foot_rx, 1)]:
        knee_x = (bx + flx) * 0.5 + sgn * sf(6.0)
        knee_y = (hip_y + foot_ly) * 0.5 - sf(2.0)
        pts = [
            (bx + sgn * sf(3.0), hip_y),
            (bx + sgn * sf(18.0), hip_y + sf(4.0)),
            (knee_x + sgn * sf(8.0), knee_y),
            (flx + sgn * sf(6.0), foot_ly - sf(12.0)),
            (flx - sgn * sf(5.0), foot_ly - sf(12.0)),
            (knee_x - sgn * sf(6.0), knee_y + sf(4.0)),
            (bx, hip_y + sf(10.0))
        ]
        draw.polygon(pts, fill=C_FUR_WHITE)
        # 丝绸垂直垂坠阴影
        draw.line([(bx + sgn * sf(12.0), hip_y + sf(6.0)), (flx, foot_ly - sf(13.0))], fill=C_WHITE_SHD, width=s(2))
        draw.line([(knee_x, knee_y), (flx + sgn * sf(2.0), foot_ly - sf(12.0))], fill=C_WHITE_SHD, width=s(1))

    # 4. 紧固小腿与脚踝深蓝护踝 (Navy Shin Wraps)
    for fx in [foot_lx, foot_rx]:
        wx = fx - sf(1.0)
        wy = foot_ly - sf(12.0)
        draw.rectangle([wx - sf(6.0), wy, wx + sf(8.0), wy + sf(8.0)], fill=C_WRAP_NAVY)
        draw.line([wx - sf(6.0), wy, wx + sf(8.0), wy + sf(8.0)], fill=C_VEST_NAVY, width=s(1))
        draw.line([wx - sf(6.0), wy + sf(8.0), wx + sf(8.0), wy], fill=C_VEST_NAVY, width=s(1))
        draw.line([wx - sf(6.0), wy + sf(8.0), wx + sf(8.0), wy + sf(8.0)], fill=C_VEST_GOLD, width=s(1))

    # 5. 棕色肉感脚掌 (Paws)
    for fx in [foot_lx, foot_rx]:
        draw.ellipse([fx - sf(7.0), foot_ly - sf(3.0), fx + sf(7.0), foot_ly + sf(4.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)
        draw.ellipse([fx - sf(6.0), foot_ly, fx - sf(2.0), foot_ly + sf(4.0)], fill=C_FUR_AMBER)
        draw.ellipse([fx - sf(2.0), foot_ly + sf(1.0), fx + sf(2.0), foot_ly + sf(5.0)], fill=C_FUR_AMBER)
        draw.ellipse([fx + sf(2.0), foot_ly, fx + sf(6.0), foot_ly + sf(4.0)], fill=C_FUR_AMBER)

    # 6. 上半身：午夜海军蓝战术小马甲 + 象牙白功夫衫短袖
    sh_lx = bx - sf(18.0)
    sh_ly = by - sf(12.0)
    sh_rx = bx + sf(18.0)
    sh_ry = by - sf(12.0)

    vest_top = by - sf(16.0)
    vest_bot = by + sf(13.0)
    vest_w = sf(20.0)

    draw.polygon([
        (bx - sf(12.0), vest_top),
        (bx + sf(12.0), vest_top),
        (bx + vest_w, by),
        (bx + vest_w - sf(2.0), vest_bot),
        (bx - vest_w + sf(2.0), vest_bot),
        (bx - vest_w, by)
    ], fill=C_VEST_NAVY)

    # 马甲立领与金色镶边
    draw.polygon([
        (bx - sf(9.0), vest_top - sf(4.0)),
        (bx + sf(9.0), vest_top - sf(4.0)),
        (bx + sf(12.0), vest_top),
        (bx - sf(12.0), vest_top)
    ], fill=C_VEST_NAVY, outline=C_VEST_GOLD)
    draw.line([bx - sf(9.0), vest_top - sf(4.0), bx + sf(9.0), vest_top - sf(4.0)], fill=C_VEST_GOLD, width=s(2))
    draw.line([bx - vest_w, by, bx - vest_w + sf(2.0), vest_bot, bx + vest_w - sf(2.0), vest_bot, bx + vest_w, by], fill=C_VEST_GOLD, width=s(2))

    # 胸口金色爪印徽章
    badge_y = by - sf(4.0)
    draw.ellipse([bx - sf(4.5), badge_y - sf(2.0), bx + sf(4.5), badge_y + sf(4.5)], fill=C_VEST_GOLD)
    draw.ellipse([bx - sf(5.5), badge_y - sf(6.5), bx - sf(3.0), badge_y - sf(3.5)], fill=C_VEST_GOLD)
    draw.ellipse([bx - sf(2.0), badge_y - sf(8.5), bx + sf(0.2), badge_y - sf(5.5)], fill=C_VEST_GOLD)
    draw.ellipse([bx + sf(1.2), badge_y - sf(8.5), bx + sf(3.5), badge_y - sf(5.5)], fill=C_VEST_GOLD)
    draw.ellipse([bx + sf(4.2), badge_y - sf(6.5), bx + sf(6.8), badge_y - sf(3.5)], fill=C_VEST_GOLD)

    # 左右战术工装口袋
    draw.rectangle([bx - vest_w + sf(3.0), vest_bot - sf(8.0), bx - sf(8.0), vest_bot - sf(2.0)], fill=C_VEST_DARK, outline=C_VEST_GOLD)
    draw.rectangle([bx + sf(8.0), vest_bot - sf(8.0), bx + vest_w - sf(3.0), vest_bot - sf(2.0)], fill=C_VEST_DARK, outline=C_VEST_GOLD)

    # 7. 腰间功夫腰封与动态飘逸流苏
    sash_y = vest_bot + sf(2.0)
    draw.rectangle([bx - sf(16.0), sash_y - sf(2.5), bx + sf(16.0), sash_y + sf(2.5)], fill=C_VEST_NAVY, outline=C_VEST_GOLD)
    draw.rectangle([bx - sf(3.0), sash_y - sf(3.0), bx + sf(3.0), sash_y + sf(3.0)], fill=C_VEST_GOLD)

    r_sw = sash_sway * sf(5.0)
    draw.polygon([(bx - sf(3.5), sash_y + sf(3.0)), (bx - sf(7.5) + r_sw, sash_y + sf(17.0)), (bx - sf(2.5) + r_sw, sash_y + sf(15.5))], fill=C_VEST_NAVY)
    draw.line([(bx - sf(3.5), sash_y + sf(3.0)), (bx - sf(7.5) + r_sw, sash_y + sf(17.0))], fill=C_VEST_GOLD, width=s(1))
    draw.polygon([(bx + sf(1.0), sash_y + sf(3.0)), (bx + sf(5.0) + r_sw * 0.8, sash_y + sf(19.0)), (bx + sf(0.5) + r_sw * 0.8, sash_y + sf(17.0))], fill=C_VEST_NAVY)
    draw.line([(bx + sf(1.0), sash_y + sf(3.0)), (bx + sf(5.0) + r_sw * 0.8, sash_y + sf(19.0))], fill=C_VEST_GOLD, width=s(1))

    # 8. 手臂系统 (支持多种招式姿态)
    # 左臂绘制
    if l_arm_mode == "fist_waist":
        draw.line([sh_lx, sh_ly, bx - sf(25.0), by + sf(2.0)], fill=C_FUR_WHITE, width=s(9))
        draw.line([bx - sf(25.0), by + sf(2.0), bx - sf(23.0), by + sf(11.0)], fill=C_WRAP_NAVY, width=s(8))
        draw.ellipse([bx - sf(28.0), by + sf(10.0), bx - sf(20.0), by + sf(18.0)], fill=C_FUR_DARK, outline=C_EAR_TIP)
    elif l_arm_mode == "wave":
        wave_angle = math.sin(l_arm_progress * math.pi * 2) * 0.3
        w_hand_x = bx - sf(34.0) + math.sin(wave_angle) * sf(10.0)
        w_hand_y = by - sf(32.0) + math.cos(wave_angle) * sf(6.0)
        draw.line([sh_lx, sh_ly, bx - sf(28.0), by - sf(18.0)], fill=C_FUR_WHITE, width=s(9))
        draw.line([bx - sf(28.0), by - sf(18.0), w_hand_x, w_hand_y], fill=C_WRAP_NAVY, width=s(8))
        draw.ellipse([w_hand_x - sf(8.0), w_hand_y - sf(8.0), w_hand_x + sf(8.0), w_hand_y + sf(8.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)
        draw.ellipse([w_hand_x - sf(4.0), w_hand_y - sf(4.0), w_hand_x + sf(4.0), w_hand_y + sf(4.0)], fill=C_PAD_PINK)
    elif l_arm_mode == "cloud_hand_up":
        ch_x = bx - sf(12.0) + math.sin(l_arm_progress * math.pi * 2) * sf(16.0)
        ch_y = by - sf(20.0) + math.cos(l_arm_progress * math.pi * 2) * sf(10.0)
        draw.line([sh_lx, sh_ly, bx - sf(24.0), by - sf(8.0)], fill=C_FUR_WHITE, width=s(9))
        draw.line([bx - sf(24.0), by - sf(8.0), ch_x, ch_y], fill=C_WRAP_NAVY, width=s(8))
        draw.ellipse([ch_x - sf(7.0), ch_y - sf(6.0), ch_x + sf(7.0), ch_y + sf(6.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)
        draw.ellipse([ch_x - sf(3.0), ch_y - sf(3.0), ch_x + sf(3.0), ch_y + sf(3.0)], fill=C_PAD_PINK)
    else: # idle natural
        draw.polygon([(sh_lx - sf(4.0), sh_ly - sf(2.0)), (sh_lx + sf(4.0), sh_ly - sf(2.0)), (sh_lx - sf(10.0), by + sf(6.0)), (sh_lx - sf(4.0), by + sf(8.0))], fill=C_FUR_WHITE)
        draw.line([sh_lx - sf(7.0), by + sf(7.0), sh_lx - sf(10.0), by + sf(18.0)], fill=C_WRAP_NAVY, width=s(7))
        draw.ellipse([sh_lx - sf(15.0), by + sf(16.0), sh_lx - sf(6.0), by + sf(25.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)

    # 右臂绘制
    if r_arm_mode == "push_palm":
        draw.line([sh_rx, sh_ry, bx + sf(28.0), by - sf(7.0)], fill=C_FUR_WHITE, width=s(9))
        draw.line([bx + sf(28.0), by - sf(7.0), bx + sf(41.0), by - sf(3.0)], fill=C_WRAP_NAVY, width=s(8))
        prx = bx + sf(46.0)
        pry = by - sf(2.0)
        draw.ellipse([prx - sf(8.0), pry - sf(9.0), prx + sf(8.0), pry + sf(9.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)
        draw.ellipse([prx - sf(6.0), pry - sf(7.0), prx - sf(2.0), pry - sf(3.0)], fill=C_PAD_PINK)
        draw.ellipse([prx - sf(2.0), pry - sf(9.0), prx + sf(2.0), pry - sf(5.0)], fill=C_PAD_PINK)
        draw.ellipse([prx + sf(2.0), pry - sf(7.0), prx + sf(6.0), pry - sf(3.0)], fill=C_PAD_PINK)
        draw.ellipse([prx - sf(7.5), pry - sf(1.0), prx - sf(3.5), pry + sf(3.0)], fill=C_PAD_PINK)
    elif r_arm_mode == "dragon_punch":
        dp_prog = r_arm_progress
        fist_x = bx + sf(18.0) + dp_prog * sf(10.0)
        fist_y = by - sf(42.0) - dp_prog * sf(18.0)
        draw.line([sh_rx, sh_ry, bx + sf(24.0), by - sf(20.0)], fill=C_FUR_WHITE, width=s(9))
        draw.line([bx + sf(24.0), by - sf(20.0), fist_x, fist_y], fill=C_WRAP_NAVY, width=s(8))
        draw.ellipse([fist_x - sf(9.0), fist_y - sf(9.0), fist_x + sf(9.0), fist_y + sf(9.0)], fill=C_FUR_DARK, outline=C_EAR_TIP)
        # 火焰粒子气浪
        for fi in range(4):
            fp_x = fist_x - sf(8.0) + fi * sf(5.0)
            fp_y = fist_y + sf(12.0) + fi * sf(4.0)
            draw.ellipse([fp_x - sf(3.0), fp_y - sf(3.0), fp_x + sf(3.0), fp_y + sf(3.0)], fill=(245, 158, 11))
            draw.ellipse([fp_x - sf(1.5), fp_y - sf(1.5), fp_x + sf(1.5), fp_y + sf(1.5)], fill=(254, 240, 138))
    elif r_arm_mode == "cloud_hand_down":
        ch_x = bx + sf(16.0) - math.sin(r_arm_progress * math.pi * 2) * sf(16.0)
        ch_y = by + sf(6.0) - math.cos(r_arm_progress * math.pi * 2) * sf(10.0)
        draw.line([sh_rx, sh_ry, bx + sf(26.0), by + sf(2.0)], fill=C_FUR_WHITE, width=s(9))
        draw.line([bx + sf(26.0), by + sf(2.0), ch_x, ch_y], fill=C_WRAP_NAVY, width=s(8))
        draw.ellipse([ch_x - sf(7.0), ch_y - sf(6.0), ch_x + sf(7.0), ch_y + sf(6.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)
        draw.ellipse([ch_x - sf(3.0), ch_y - sf(3.0), ch_x + sf(3.0), ch_y + sf(3.0)], fill=C_PAD_PINK)
    else: # idle natural
        draw.polygon([(sh_rx - sf(4.0), sh_ry - sf(2.0)), (sh_rx + sf(4.0), sh_ry - sf(2.0)), (sh_rx + sf(10.0), by + sf(6.0)), (sh_rx + sf(4.0), by + sf(8.0))], fill=C_FUR_WHITE)
        draw.line([sh_rx + sf(7.0), by + sf(7.0), sh_rx + sf(10.0), by + sf(18.0)], fill=C_WRAP_NAVY, width=s(7))
        draw.ellipse([sh_rx + sf(6.0), by + sf(16.0), sh_rx + sf(15.0), by + sf(25.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)

    # 9. 头部与面容 (Red Panda Face Mask + Long Bunny Ears)
    hx = bx
    hy = by - sf(36.0)

    # (A) 超长立耳 (高耸入云，外焦糖内白绒，带物理惯性微晃)
    for ex, sgn in [(hx - sf(15.0), -1), (hx + sf(15.0), 1)]:
        ey = hy - sf(31.0) + ear_flop * sgn * sf(3.0)
        draw.ellipse([ex - sf(9.0), ey - sf(23.0), ex + sf(9.0), ey + sf(18.0)], fill=C_FUR_AMBER, outline=C_FUR_DARK)
        draw.ellipse([ex - sf(8.5), ey - sf(23.0), ex + sf(8.5), ey - sf(13.0)], fill=C_EAR_TIP)
        draw.ellipse([ex - sf(6.0), ey - sf(14.0), ex + sf(6.0), ey + sf(14.0)], fill=C_FUR_WHITE)
        draw.ellipse([ex - sf(3.0), ey - sf(6.0), ex + sf(3.0), ey + sf(9.0)], fill=(254, 215, 170, 180))
        draw.ellipse([ex - sf(6.5), ey + sf(13.0), ex + sf(6.5), ey + sf(19.0)], fill=C_FUR_WHITE)

    # (B) 头部基底 (红熊猫饱满圆脸)
    head_rx = sf(24.0)
    head_ry = sf(19.0)
    draw.ellipse([hx - head_rx, hy - head_ry, hx + head_rx, hy + head_ry], fill=C_FUR_AMBER)
    draw.polygon([(hx - sf(4.0), hy - head_ry), (hx, hy - head_ry - sf(5.0)), (hx + sf(4.0), hy - head_ry)], fill=C_FUR_AMBER)

    # (C) 标志性红熊猫面部花纹
    # 脸颊两侧白色圆润绒毛区
    draw.ellipse([hx - sf(25.0), hy - sf(2.0), hx - sf(7.0), hy + sf(16.0)], fill=C_FUR_WHITE)
    draw.ellipse([hx + sf(7.0), hy - sf(2.0), hx + sf(25.0), hy + sf(16.0)], fill=C_FUR_WHITE)
    # 颊侧毛尖
    draw.polygon([(hx - sf(22.0), hy + sf(3.0)), (hx - sf(29.0), hy + sf(7.0)), (hx - sf(20.0), hy + sf(11.0))], fill=C_FUR_WHITE)
    draw.polygon([(hx + sf(22.0), hy + sf(3.0)), (hx + sf(29.0), hy + sf(7.0)), (hx + sf(20.0), hy + sf(11.0))], fill=C_FUR_WHITE)

    # 吻部软糯白色区域
    snout_y = hy + sf(6.0)
    draw.ellipse([hx - sf(13.0), snout_y - sf(7.0), hx + sf(13.0), snout_y + sf(8.5)], fill=C_FUR_WHITE)

    # 眼睛上方白色泪滴眉斑
    draw.ellipse([hx - sf(12.0), hy - sf(12.0), hx - sf(5.5), hy - sf(6.5)], fill=C_FUR_WHITE)
    draw.ellipse([hx + sf(5.5), hy - sf(12.0), hx + sf(12.0), hy - sf(6.5)], fill=C_FUR_WHITE)

    # 眼角深红棕泪痕
    draw.line([hx - sf(16.0), hy - sf(1.0), hx - sf(11.0), hy + sf(7.5)], fill=C_FUR_DARK, width=s(2))
    draw.line([hx + sf(16.0), hy - sf(1.0), hx + sf(11.0), hy + sf(7.5)], fill=C_FUR_DARK, width=s(2))

    # (D) 五官与微笑
    nose_y = snout_y - sf(2.0)
    draw.polygon([(hx - sf(3.0), nose_y - sf(1.0)), (hx + sf(3.0), nose_y - sf(1.0)), (hx, nose_y + sf(3.0))], fill=C_NOSE_DARK)
    draw.point((int(hx - s(1)), int(nose_y)), fill=(255, 255, 255))

    draw.line([hx, nose_y + sf(3.0), hx, nose_y + sf(6.0)], fill=C_NOSE_DARK, width=s(1))
    draw.arc([hx - sf(5.5), nose_y + sf(4.0), hx, nose_y + sf(8.5)], 0, 180, fill=C_NOSE_DARK, width=s(1))
    draw.arc([hx, nose_y + sf(4.0), hx + sf(5.5), nose_y + sf(8.5)], 0, 180, fill=C_NOSE_DARK, width=s(1))
    draw.polygon([(hx + sf(1.5), nose_y + sf(6.0)), (hx + sf(4.5), nose_y + sf(6.0)), (hx + sf(2.5), nose_y + sf(9.0))], fill=(255, 255, 255))

    for i in [-1, 0, 1]:
        draw.line([hx - sf(14.0), snout_y + i * sf(2.0), hx - sf(26.0), snout_y + i * sf(3.8)], fill=(120, 80, 50, 180), width=s(1))
        draw.line([hx + sf(14.0), snout_y + i * sf(2.0), hx + sf(26.0), snout_y + i * sf(3.8)], fill=(120, 80, 50, 180), width=s(1))

    # (E) 水光大眼 (支持眨眼与视线追踪)
    eye_y = hy - sf(3.0)
    cur_eye_h = max(1.0, 6.0 * (1.0 - blink * 0.85))

    for ex in [hx - sf(9.5), hx + sf(9.5)]:
        if blink > 0.8:
            draw.arc([ex - sf(5.0), eye_y - sf(2.0), ex + sf(5.0), eye_y + sf(4.0)], 10, 170, fill=C_NOSE_DARK, width=s(2))
        else:
            draw.ellipse([ex - sf(5.0), eye_y - sf(cur_eye_h), ex + sf(5.0), eye_y + sf(cur_eye_h)], fill=(20, 15, 12))
            draw.ellipse([ex - sf(4.0) + sf(eye_gaze[0]), eye_y - sf(cur_eye_h * 0.7) + sf(eye_gaze[1]), ex + sf(4.0) + sf(eye_gaze[0]), eye_y + sf(cur_eye_h * 0.8) + sf(eye_gaze[1])], fill=C_EYE_IRIS)
            draw.ellipse([ex - sf(3.0), eye_y - sf(cur_eye_h * 0.7), ex - sf(0.8), eye_y - sf(cur_eye_h * 0.3)], fill=(255, 255, 255))
            draw.ellipse([ex + sf(1.2), eye_y + sf(cur_eye_h * 0.2), ex + sf(2.8), eye_y + sf(cur_eye_h * 0.5)], fill=(255, 255, 255))

    # 功夫英武剑眉
    if r_arm_mode in ["push_palm", "dragon_punch"]:
        draw.line([hx - sf(14.0), hy - sf(10.0), hx - sf(5.0), hy - sf(13.5)], fill=C_FUR_DARK, width=s(2))
        draw.line([hx + sf(5.0), hy - sf(13.5), hx + sf(14.0), hy - sf(10.0)], fill=C_FUR_DARK, width=s(2))
    else:
        draw.line([hx - sf(13.0), hy - sf(11.5), hx - sf(5.5), hy - sf(11.5)], fill=C_FUR_DARK, width=s(1))
        draw.line([hx + sf(5.5), hy - sf(11.5), hx + sf(13.0), hy - sf(11.5)], fill=C_FUR_DARK, width=s(1))

    # 10. 顶部状态栏与底部动作字幕 (HUD)
    if show_device_hud:
        draw.rectangle([0, 0, W, s(18)], fill=(15, 23, 42))
        draw.rectangle([s(6), s(4), s(48), s(14)], fill=(22, 101, 52))
        draw.rectangle([W - s(40), s(4), W - s(6), s(14)], fill=(51, 65, 85))

        draw.rectangle([0, H - s(22), W, H], fill=(15, 23, 42))
        draw.rectangle([s(16), H - s(18), W - s(16), H - s(4)], fill=C_VEST_DARK, outline=C_VEST_GOLD)

    return im.resize((width, height), Image.Resampling.LANCZOS)

def build_action_gif(action_name, num_frames=16, fps=12, width=135, height=240, out_path=""):
    frames = []
    for i in range(num_frames):
        t = i / float(num_frames)
        phase = t * 2.0 * math.pi

        if action_name == "kungfu":
            b_off = math.sin(phase) * 1.5
            b_sq = 1.0 + math.cos(phase) * 0.04
            t_sw = math.sin(phase)
            s_sw = math.sin(phase * 1.5)
            r_prog = 0.5 + 0.5 * math.sin(phase)
            blink = 1.0 if (i == 4 or i == 5) else 0.0
            gaze = (math.sin(phase) * 0.8, 0.0)
            f = render_character_frame(
                width=width, height=height,
                body_offset_y=b_off, body_squash=b_sq, leg_spread=18.0,
                l_arm_mode="fist_waist", r_arm_mode="push_palm",
                r_arm_progress=r_prog, ear_flop=math.sin(phase) * 0.3,
                tail_sway=t_sw, sash_sway=s_sw,
                eye_gaze=gaze, blink=blink,
                action_label="功夫起势推掌", show_device_hud=True
            )
        elif action_name == "taichi":
            b_off = math.sin(phase) * 2.0
            b_sq = 1.0
            t_sw = math.sin(phase * 0.8)
            s_sw = math.sin(phase)
            blink = 1.0 if (i == 8 or i == 9) else 0.0
            gaze = (math.sin(phase) * 1.2, math.cos(phase) * 0.5)
            f = render_character_frame(
                width=width, height=height,
                body_offset_y=b_off, body_squash=b_sq, leg_spread=15.0,
                l_arm_mode="cloud_hand_up", r_arm_mode="cloud_hand_down",
                l_arm_progress=t, r_arm_progress=t,
                ear_flop=math.sin(phase * 0.8) * 0.5,
                tail_sway=t_sw, sash_sway=s_sw,
                eye_gaze=gaze, blink=blink,
                action_label="太极云手随风", show_device_hud=True
            )
        elif action_name == "dragon_punch":
            # 升龙拳：蓄力 -> 飞天暴击 -> 落地
            if t < 0.3: # 蓄力蹲下
                b_off = (t / 0.3) * 6.0
                b_sq = 1.15
                dp_p = 0.0
                r_mode = "fist_waist"
            elif t < 0.7: # 飞天升龙
                jump_p = (t - 0.3) / 0.4
                b_off = 6.0 - math.sin(jump_p * math.pi) * 24.0
                b_sq = 0.90 # 拉伸
                dp_p = jump_p
                r_mode = "dragon_punch"
            else: # 缓冲着地
                land_p = (t - 0.7) / 0.3
                b_off = (1.0 - land_p) * 4.0
                b_sq = 1.05
                dp_p = 0.5 * (1.0 - land_p)
                r_mode = "push_palm"

            t_sw = math.sin(phase * 2.0)
            s_sw = math.sin(phase * 2.0)
            blink = 0.0
            gaze = (0.0, -1.5 if t >= 0.3 and t < 0.7 else 0.0)
            f = render_character_frame(
                width=width, height=height,
                body_offset_y=b_off, body_squash=b_sq, leg_spread=16.0,
                l_arm_mode="fist_waist", r_arm_mode=r_mode,
                r_arm_progress=dp_p, ear_flop=math.sin(phase) * 0.8,
                tail_sway=t_sw, sash_sway=s_sw,
                eye_gaze=gaze, blink=blink,
                action_label="升龙破空霸天", show_device_hud=True
            )
        elif action_name == "wave":
            b_off = math.sin(phase) * 1.0
            b_sq = 1.0
            t_sw = math.sin(phase * 1.5)
            s_sw = math.sin(phase)
            blink = 1.0 if (i == 3 or i == 4) else 0.0
            gaze = (0.5, 0.0)
            f = render_character_frame(
                width=width, height=height,
                body_offset_y=b_off, body_squash=b_sq, leg_spread=14.0,
                l_arm_mode="wave", r_arm_mode="idle",
                l_arm_progress=t * 2.0, ear_flop=math.sin(phase) * 0.4,
                tail_sway=t_sw, sash_sway=s_sw,
                eye_gaze=gaze, blink=blink,
                action_label="元气挥手问候", show_device_hud=True
            )
        elif action_name == "showcase":
            # 复合阅兵：连续展示 4 个经典功夫与萌态动作
            sub_step = int(t * 4) % 4
            sub_t = (t * 4) % 1.0
            sub_phase = sub_t * 2.0 * math.pi
            if sub_step == 0:
                l_m = "wave"; r_m = "idle"; lp = sub_t * 2; rp = 0; b_off = math.sin(sub_phase); label = "1. 元气挥手"
            elif sub_step == 1:
                l_m = "fist_waist"; r_m = "push_palm"; lp = 0; rp = math.sin(sub_phase); b_off = 2.0; label = "2. 功夫推掌"
            elif sub_step == 2:
                l_m = "cloud_hand_up"; r_m = "cloud_hand_down"; lp = sub_t; rp = sub_t; b_off = math.cos(sub_phase); label = "3. 太极云手"
            else:
                l_m = "fist_waist"; r_m = "dragon_punch"; lp = 0; rp = sub_t; b_off = -math.sin(sub_t * math.pi) * 16.0; label = "4. 升龙霸天"

            f = render_character_frame(
                width=width, height=height,
                body_offset_y=b_off, body_squash=1.0, leg_spread=16.0,
                l_arm_mode=l_m, r_arm_mode=r_m,
                l_arm_progress=lp, r_arm_progress=rp,
                ear_flop=math.sin(sub_phase) * 0.5,
                tail_sway=math.sin(sub_phase), sash_sway=math.sin(sub_phase),
                eye_gaze=(math.sin(sub_phase), 0.0), blink=(1.0 if int(sub_t * 10) == 3 else 0.0),
                action_label=label, show_device_hud=True
            )
        frames.append(f)

    # 转换为 256 色优化调色板并保存 GIF
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    palette_frames = [frm.convert('RGB').quantize(colors=128, method=Image.Resampling.LANCZOS) for frm in frames]
    duration_ms = int(1000.0 / fps)
    palette_frames[0].save(
        out_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )
    print(f"Generated {out_path} ({len(frames)} frames, {width}x{height}, {fps}fps)")

if __name__ == '__main__':
    targets = [
        ("kungfu", "cadet_ren_kungfu_action.gif"),
        ("taichi", "cadet_ren_taichi_zen.gif"),
        ("dragon_punch", "cadet_ren_dragon_punch.gif"),
        ("wave", "cadet_ren_wave_greeting.gif"),
        ("showcase", "cadet_ren_device_135x240_showcase.gif"),
    ]

    out_dirs = [
        "docs/assets/cadet_ren",
        "wechat_miniprogram/assets/cadet_ren"
    ]

    for act, fname in targets:
        for od in out_dirs:
            # 135x240 M5StickS3 原生屏幕尺寸
            dev_path = os.path.join(od, fname)
            build_action_gif(act, num_frames=16, fps=10, width=135, height=240, out_path=dev_path)

        # 高清大图版 (270x480) 留存在 docs
        hd_path = os.path.join("docs/assets/cadet_ren", fname.replace(".gif", "_hd.gif"))
        build_action_gif(act, num_frames=16, fps=10, width=270, height=480, out_path=hd_path)

    print("All pure character animated GIFs generated and archived successfully.")
