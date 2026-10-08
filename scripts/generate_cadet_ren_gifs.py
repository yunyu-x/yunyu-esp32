#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cadet Ren (小仁 · 功夫巡警) 动作合成 GIF 自动生成脚本
将 2D 高清动作分镜与 1:1 设备端 135x240 屏幕动效合成输出为精美 GIF 动画并自动归档
"""

import os
import shutil
import math
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIRS = [
    r'docs/assets/cadet_ren',
    r'wechat_miniprogram/assets/cadet_ren'
]

for ad in ASSETS_DIRS:
    os.makedirs(ad, exist_ok=True)

MARTIAL_SHEET = r'docs/assets/cadet_ren/martial_action_poses.jpg'
PLAYFUL_SHEET = r'docs/assets/cadet_ren/playful_action_poses.jpg'

def get_font(size):
    try:
        return ImageFont.truetype('arial.ttf', size)
    except Exception:
        try:
            return ImageFont.truetype('msyh.ttc', size)
        except Exception:
            return ImageFont.load_default()

def create_action_gif(panel_crops, titles, subtitle_tags, out_filename, target_w=280, target_h=580, hold_frames=20, trans_frames=8, fps=24):
    """
    合成高保真动作流转 GIF，包含优雅 HUD 胶囊标牌与平滑交叉淡入淡出转场
    """
    num = len(panel_crops)
    # 统一尺寸
    resized_crops = []
    for c in panel_crops:
        # 裁剪并等比缩放
        w, h = c.size
        # 居中裁切角色主体
        c_res = c.resize((target_w, target_h), Image.Resampling.LANCZOS).convert('RGBA')
        resized_crops.append(c_res)

    font_title = get_font(18)
    font_sub = get_font(12)

    frames = []
    for i in range(num):
        cur_img = resized_crops[i]
        next_img = resized_crops[(i + 1) % num]
        cur_title = titles[i]
        next_title = titles[(i + 1) % num]
        cur_tag = subtitle_tags[i]
        next_tag = subtitle_tags[(i + 1) % num]

        # 定格帧
        base_f = cur_img.copy()
        draw = ImageDraw.Draw(base_f)
        # 绘制顶部 HUD 标识
        draw.rounded_rectangle([12, 12, target_w - 12, 44], radius=8, fill=(15, 23, 42, 225), outline=(254, 202, 87, 255), width=2)
        draw.text((target_w // 2, 28), cur_title, fill=(255, 255, 255, 255), anchor='mm', font=font_title)

        # 绘制底部动作法则标签
        draw.rounded_rectangle([16, target_h - 42, target_w - 16, target_h - 14], radius=6, fill=(30, 41, 59, 215), outline=(100, 116, 139, 200), width=1)
        draw.text((target_w // 2, target_h - 28), cur_tag, fill=(226, 232, 240, 255), anchor='mm', font=font_sub)

        f_rgb = base_f.convert('RGB')
        for _ in range(hold_frames):
            frames.append(f_rgb)

        # 渐变过渡帧
        for t in range(trans_frames):
            alpha = (t + 1) / (trans_frames + 1)
            blended = Image.blend(cur_img, next_img, alpha)
            draw_b = ImageDraw.Draw(blended)
            
            # 顶部 HUD 动态切换
            draw_b.rounded_rectangle([12, 12, target_w - 12, 44], radius=8, fill=(15, 23, 42, 225), outline=(254, 202, 87, 255), width=2)
            lbl = cur_title if alpha < 0.5 else next_title
            draw_b.text((target_w // 2, 28), lbl, fill=(255, 255, 255, 255), anchor='mm', font=font_title)

            # 底部标签
            draw_b.rounded_rectangle([16, target_h - 42, target_w - 16, target_h - 14], radius=6, fill=(30, 41, 59, 215), outline=(100, 116, 139, 200), width=1)
            tag = cur_tag if alpha < 0.5 else next_tag
            draw_b.text((target_w // 2, target_h - 28), tag, fill=(226, 232, 240, 255), anchor='mm', font=font_sub)

            frames.append(blended.convert('RGB'))

    # 量化压缩调色板并保存 GIF
    frame_dur = int(1000 / fps)
    # 使用统一自适应量化减少伪影
    opt_frames = [f.quantize(colors=128, method=Image.Resampling.LANCZOS) for f in frames]

    for ad in ASSETS_DIRS:
        out_p = os.path.join(ad, out_filename)
        opt_frames[0].save(out_p, save_all=True, append_images=opt_frames[1:], optimize=True, duration=frame_dur, loop=0)
        size_kb = os.path.getsize(out_p) / 1024
        print(f"Generated {out_p} ({len(frames)} frames, {size_kb:.1f} KB)")


def generate_device_screen_simulation_gif(out_filename="cadet_ren_device_135x240_showcase.gif", fps=25):
    """
    1:1 仿真 M5Stack StickS3 物理屏幕 (135x240) 的真实渲染循环
    包含状态栏、角色动力学骨骼、气浪特效与底部动作字幕
    """
    W, H = 135, 240
    # 模拟 5 个经典动作周期 (每个动作 1.6 秒 = 40 帧)
    actions = [
        {"name": "功夫推掌 (Horse Stance)", "act": "kungfu", "color": (254, 202, 87), "mood": "FOCUS"},
        {"name": "升龙拳 (Dragon Punch)", "act": "dragon", "color": (248, 113, 113), "mood": "HERO"},
        {"name": "太极云手 (Tai Chi)", "act": "taichi", "color": (96, 165, 250), "mood": "ZEN"},
        {"name": "元气挥手 (Energetic Wave)", "act": "wave", "color": (52, 211, 153), "mood": "HAPPY"},
        {"name": "金鸡独立 (Crane Balance)", "act": "balance", "color": (192, 132, 252), "mood": "FOCUS"}
    ]

    frames = []
    font_status = get_font(10)
    font_sub = get_font(10)

    total_steps_per_act = 32
    for act_idx, act_info in enumerate(actions):
        act_name = act_info["name"]
        act_key = act_info["act"]
        hud_col = act_info["color"]

        for step in range(total_steps_per_act):
            p = step / total_steps_per_act
            t = p * math.pi * 2

            im = Image.new('RGB', (W, H), (0, 0, 0))
            draw = ImageDraw.Draw(im)

            # 1. 顶部状态栏 (Y: 0 ~ 18)
            draw.rectangle([0, 0, W, 18], fill=(15, 23, 42))
            draw.text((6, 9), "WiFi 85fps", fill=(74, 222, 128), anchor='lm', font=font_status)
            draw.text((W - 6, 9), "4.1V 100%", fill=(226, 232, 240), anchor='rm', font=font_status)

            # 2. 角色动力学骨骼参数解算
            body_x = 67.5
            body_y = 135.0
            squash_x = 1.0
            squash_y = 1.0
            l_arm_ang = 35.0
            r_arm_ang = 35.0
            body_tilt = 0.0
            head_tilt = 0.0
            jump_y = 0.0

            if act_key == "kungfu":
                # 马步下沉 + 右掌推出
                body_y += 5.0
                squash_y = 0.94
                squash_x = 1.06
                r_arm_ang = 110.0 + math.sin(t) * 10.0
                l_arm_ang = 35.0
                body_tilt = -5.0
                head_tilt = 6.0
            elif act_key == "dragon":
                # 深蹲蓄力 -> 冲天飞起
                if p < 0.25:
                    jump_y = 8.0
                    squash_y = 0.85
                    squash_x = 1.15
                    r_arm_ang = 20.0
                else:
                    lp = (p - 0.25) / 0.75
                    jump_y = -math.sin(lp * math.pi) * 22.0
                    squash_y = 1.20
                    squash_x = 0.85
                    r_arm_ang = 165.0
                    l_arm_ang = 25.0
            elif act_key == "taichi":
                # 云手圆弧
                body_tilt = math.sin(t) * 6.0
                body_x += math.sin(t) * 5.0
                l_arm_ang = 80.0 + math.sin(t) * 35.0
                r_arm_ang = 80.0 + math.cos(t) * 35.0
            elif act_key == "wave":
                # 挥手
                body_tilt = math.sin(t * 2) * 3.0
                r_arm_ang = 125.0 + math.sin(t * 3) * 30.0
                head_tilt = math.sin(t * 2) * 5.0
            elif act_key == "balance":
                # 单脚站立
                body_tilt = math.sin(t * 2) * 4.0
                l_arm_ang = 90.0 + math.sin(t * 2) * 12.0
                r_arm_ang = 90.0 - math.sin(t * 2) * 12.0
                body_y -= 4.0

            by = body_y + jump_y
            bx = body_x

            # 3. 接触软阴影
            sh_w = 26 * squash_x * (0.6 if jump_y < -5 else 1.0)
            sh_y = 188.0 + (0 if jump_y >= 0 else jump_y * 0.1)
            draw.ellipse([bx - sh_w, sh_y - 4, bx + sh_w, sh_y + 4], fill=(30, 20, 15))

            # 4. 蓬松狐兔大尾巴 (背景层)
            tx = bx + 18
            ty = by + 12
            draw.ellipse([tx - 10, ty - 8, tx + 10, ty + 8], fill=(217, 130, 54))
            draw.ellipse([tx + 4, ty - 6, tx + 14, ty + 4], fill=(255, 247, 237)) # 奶白毛尖

            # 5. 下肢象牙白练功裤 + 深蓝护踝 + 焦糖萌脚
            hip_y = by + 14
            foot_ly = by + 42
            foot_ry = by + 42
            foot_lx = bx - 14
            foot_rx = bx + 14

            if act_key == "balance":
                foot_ly -= 15 # 左腿悬空提膝
                draw.line([bx - 10, hip_y, foot_lx - 6, hip_y + 12], fill=(255, 254, 254), width=10)
                draw.line([foot_lx - 6, hip_y + 12, foot_lx, foot_ly], fill=(255, 254, 254), width=8)
            else:
                draw.line([bx - 10, hip_y, foot_lx, foot_ly], fill=(255, 254, 254), width=9)
            draw.line([bx + 10, hip_y, foot_rx, foot_ry], fill=(255, 254, 254), width=9)

            # 护踝深蓝绑带
            draw.rectangle([foot_lx - 4, foot_ly - 5, foot_lx + 4, foot_ly], fill=(25, 73, 149), outline=(254, 202, 87))
            draw.rectangle([foot_rx - 4, foot_ry - 5, foot_rx + 4, foot_ry], fill=(25, 73, 149), outline=(254, 202, 87))

            # 焦糖脚掌与粉肉垫
            draw.ellipse([foot_lx - 6, foot_ly - 2, foot_lx + 6, foot_ly + 6], fill=(217, 130, 54), outline=(130, 34, 32))
            draw.ellipse([foot_rx - 6, foot_ry - 2, foot_rx + 6, foot_ry + 6], fill=(217, 130, 54), outline=(130, 34, 32))
            draw.ellipse([foot_lx - 3, foot_ly + 1, foot_lx + 3, foot_ly + 4], fill=(252, 187, 178))
            draw.ellipse([foot_rx - 3, foot_ry + 1, foot_rx + 3, foot_ry + 4], fill=(252, 187, 178))

            # 6. 躯干与疯狂动物城战术马甲 (午夜海军蓝 + 金边)
            bw = 20 * squash_x
            bh = 22 * squash_y
            draw.ellipse([bx - bw, by - bh * 0.7, bx + bw, by + bh], fill=(217, 130, 54))
            # 软糯香草腹部圆贴
            draw.ellipse([bx - bw * 0.65, by - bh * 0.3, bx + bw * 0.65, by + bh * 0.85], fill=(255, 247, 237))

            # 战术工装马甲 (午夜海军蓝 + 亮金滚边)
            vest_top = by - bh * 0.6
            vest_bot = by + bh * 0.2
            # 左翻襟
            draw.polygon([(bx - bw * 0.8, vest_top), (bx - 3, vest_top), (bx - 4, vest_bot), (bx - bw * 0.8, vest_bot)], fill=(25, 73, 149))
            draw.line([(bx - 3, vest_top), (bx - 4, vest_bot)], fill=(254, 202, 87), width=1)
            # 右翻襟
            draw.polygon([(bx + 3, vest_top), (bx + bw * 0.8, vest_top), (bx + bw * 0.8, vest_bot), (bx + 4, vest_bot)], fill=(25, 73, 149))
            draw.line([(bx + 3, vest_top), (bx + 4, vest_bot)], fill=(254, 202, 87), width=1)
            # 左胸巡警星徽
            draw.ellipse([bx - 9, vest_top + 4, bx - 3, vest_top + 10], fill=(254, 202, 87))

            # 功夫腰封与飘逸带饰
            sash_y = vest_bot + 4
            draw.rectangle([bx - bw * 0.7, sash_y - 2, bx + bw * 0.7, sash_y + 2], fill=(25, 73, 149), outline=(254, 202, 87))
            # 随风动态飘舞带饰
            ribbon_drift = math.sin(t * 1.5) * 3.5
            draw.polygon([(bx - 2, sash_y + 2), (bx - 6 + ribbon_drift, sash_y + 13), (bx - 1, sash_y + 11)], fill=(25, 73, 149))
            draw.line([(bx - 2, sash_y + 2), (bx - 6 + ribbon_drift, sash_y + 13)], fill=(254, 202, 87))

            # 7. 手臂与手腕编织护腕
            sh_lx = bx - bw * 0.85
            sh_ly = by - bh * 0.4
            sh_rx = bx + bw * 0.85
            sh_ry = by - bh * 0.4

            # 计算两臂末端
            rad_l = l_arm_ang * math.pi / 180.0
            rad_r = r_arm_ang * math.pi / 180.0
            arm_len = 25.0
            paw_lx = sh_lx - math.sin(rad_l) * arm_len
            paw_ly = sh_ly + math.cos(rad_l) * arm_len
            paw_rx = sh_rx + math.sin(rad_r) * arm_len
            paw_ry = sh_ry + math.cos(rad_r) * arm_len

            # 左手大臂小臂双弧
            el_lx = (sh_lx + paw_lx) * 0.5 - 3.0
            el_ly = (sh_ly + paw_ly) * 0.5 + 2.0
            draw.line([sh_lx, sh_ly, el_lx, el_ly], fill=(217, 130, 54), width=8)
            draw.line([el_lx, el_ly, paw_lx, paw_ly], fill=(217, 130, 54), width=6)
            # 护腕
            draw.ellipse([paw_lx - 3, paw_ly - 3, paw_lx + 3, paw_ly + 3], fill=(239, 213, 178), outline=(173, 133, 85))
            # 萌爪与肉垫
            draw.ellipse([paw_lx - 4, paw_ly - 4, paw_lx + 4, paw_ly + 4], fill=(217, 130, 54), outline=(130, 34, 32))
            draw.ellipse([paw_lx - 2, paw_ly - 2, paw_lx + 2, paw_ly + 2], fill=(252, 187, 178))

            # 右手
            el_rx = (sh_rx + paw_rx) * 0.5 + 3.0
            el_ry = (sh_ry + paw_ry) * 0.5 + 2.0
            draw.line([sh_rx, sh_ry, el_rx, el_ry], fill=(217, 130, 54), width=8)
            draw.line([el_rx, el_ry, paw_rx, paw_ry], fill=(217, 130, 54), width=6)
            # 护腕
            draw.ellipse([paw_rx - 3, paw_ry - 3, paw_rx + 3, paw_ry + 3], fill=(239, 213, 178), outline=(173, 133, 85))
            # 萌爪
            if act_key == "kungfu":
                # 功夫推掌 (开掌)
                draw.ellipse([paw_rx - 5, paw_ry - 7, paw_rx + 5, paw_ry + 7], fill=(217, 130, 54), outline=(130, 34, 32))
                draw.ellipse([paw_rx - 3, paw_ry - 4, paw_rx + 3, paw_ry + 4], fill=(252, 187, 178))
            else:
                draw.ellipse([paw_rx - 4, paw_ry - 4, paw_rx + 4, paw_ry + 4], fill=(217, 130, 54), outline=(130, 34, 32))
                draw.ellipse([paw_rx - 2, paw_ry - 2, paw_rx + 2, paw_ry + 2], fill=(252, 187, 178))

            # 升龙拳烈焰气浪粒子特效
            if act_key == "dragon" and p >= 0.25:
                for i in range(5):
                    spark_x = paw_rx + (i - 2) * 3
                    spark_y = paw_ry + 6 + i * 3
                    draw.ellipse([spark_x - 2, spark_y - 2, spark_x + 2, spark_y + 2], fill=(248, 113, 113))

            # 8. 头部与面容表情 (多层狐兔大耳 + 水光眼 + 软糯吻部)
            head_x = bx + math.sin(head_tilt * math.pi / 180.0) * 3.0
            head_y = by - bh * 0.85

            # 狐兔修长双耳 (焦糖外耳 + 樱粉内耳 + 黑巧尖端 + 白绒根部)
            ear_ly = head_y - 24
            ear_ry = head_y - 24
            # 外耳
            draw.ellipse([head_x - 20, ear_ly - 14, head_x - 6, ear_ly + 10], fill=(217, 130, 54), outline=(130, 34, 32))
            draw.ellipse([head_x + 6, ear_ry - 14, head_x + 20, ear_ry + 10], fill=(217, 130, 54), outline=(130, 34, 32))
            # 耳尖黑巧
            draw.ellipse([head_x - 17, ear_ly - 14, head_x - 9, ear_ly - 8], fill=(24, 18, 16))
            draw.ellipse([head_x + 9, ear_ry - 14, head_x + 17, ear_ry - 8], fill=(24, 18, 16))
            # 内耳樱粉
            draw.ellipse([head_x - 17, ear_ly - 8, head_x - 9, ear_ly + 6], fill=(253, 164, 175))
            draw.ellipse([head_x + 9, ear_ry - 8, head_x + 17, ear_ry + 6], fill=(253, 164, 175))
            # 耳根白绒
            draw.ellipse([head_x - 15, ear_ly + 6, head_x - 11, ear_ly + 11], fill=(255, 247, 237))
            draw.ellipse([head_x + 11, ear_ry + 6, head_x + 15, ear_ry + 11], fill=(255, 247, 237))

            # 头部主体
            draw.ellipse([head_x - 20, head_y - 15, head_x + 20, head_y + 15], fill=(217, 130, 54))
            # 颊侧毛簇
            draw.polygon([(head_x - 18, head_y), (head_x - 24, head_y + 3), (head_x - 18, head_y + 6)], fill=(217, 130, 54))
            draw.polygon([(head_x + 18, head_y), (head_x + 24, head_y + 3), (head_x + 18, head_y + 6)], fill=(217, 130, 54))

            # 腮红
            draw.ellipse([head_x - 14, head_y + 3, head_x - 8, head_y + 7], fill=(252, 187, 178))
            draw.ellipse([head_x + 8, head_y + 3, head_x + 14, head_y + 7], fill=(252, 187, 178))

            # 软糯奶白吻部
            draw.ellipse([head_x - 10, head_y + 1, head_x + 10, head_y + 11], fill=(255, 253, 250), outline=(206, 180, 150))
            # 黑松露纽扣鼻 + 水润高光
            draw.ellipse([head_x - 3, head_y + 2, head_x + 3, head_y + 6], fill=(16, 12, 10))
            draw.point((head_x - 1, head_y + 3), fill=(255, 255, 255))
            # ω 微笑弧与萌牙
            draw.arc([head_x - 4, head_y + 6, head_x, head_y + 10], 0, 180, fill=(16, 12, 10))
            draw.arc([head_x, head_y + 6, head_x + 4, head_y + 10], 0, 180, fill=(16, 12, 10))
            draw.point((head_x + 1, head_y + 8), fill=(255, 255, 255)) # 萌牙

            # 日漫双星水光眼
            eye_y = head_y - 4
            eye_lx = head_x - 9
            eye_rx = head_x + 9
            draw.ellipse([eye_lx - 4, eye_y - 5, eye_lx + 4, eye_y + 5], fill=(15, 23, 42))
            draw.ellipse([eye_rx - 4, eye_y - 5, eye_rx + 4, eye_y + 5], fill=(15, 23, 42))
            draw.ellipse([eye_lx - 2, eye_y, eye_lx + 2, eye_y + 4], fill=(53, 191, 255)) # 虹膜
            draw.ellipse([eye_rx - 2, eye_y, eye_rx + 2, eye_y + 4], fill=(53, 191, 255))
            draw.ellipse([eye_lx - 2, eye_y - 3, eye_lx, eye_y - 1], fill=(255, 255, 255)) # 主高光
            draw.ellipse([eye_rx - 2, eye_y - 3, eye_rx, eye_y - 1], fill=(255, 255, 255))
            draw.point((eye_lx + 2, eye_y + 2), fill=(255, 255, 255)) # 副星光
            draw.point((eye_rx + 2, eye_y + 2), fill=(255, 255, 255))

            # 眉毛 (功夫专注倾斜 vs 日常柔和)
            if act_key in ["kungfu", "dragon"]:
                draw.line([eye_lx - 4, eye_y - 7, eye_lx + 4, eye_y - 9], fill=(130, 34, 32), width=2)
                draw.line([eye_rx - 4, eye_y - 9, eye_rx + 4, eye_y - 7], fill=(130, 34, 32), width=2)
            else:
                draw.line([eye_lx - 4, eye_y - 8, eye_lx + 4, eye_y - 8], fill=(130, 34, 32), width=1)
                draw.line([eye_rx - 4, eye_y - 8, eye_rx + 4, eye_y - 8], fill=(130, 34, 32), width=1)

            # 9. 底部字幕栏 (Y: 218 ~ 240)
            draw.rectangle([0, 218, W, 240], fill=(15, 23, 42))
            draw.text((W // 2, 229), act_name, fill=hud_col, anchor='mm', font=font_sub)

            frames.append(im)

    frame_dur = int(1000 / fps)
    opt_frames = [f.quantize(colors=128, method=Image.Resampling.LANCZOS) for f in frames]

    for ad in ASSETS_DIRS:
        out_p = os.path.join(ad, out_filename)
        opt_frames[0].save(out_p, save_all=True, append_images=opt_frames[1:], optimize=True, duration=frame_dur, loop=0)
        size_kb = os.path.getsize(out_p) / 1024
        print(f"Generated {out_p} ({len(frames)} frames, {size_kb:.1f} KB)")


def main():
    print("=== Cadet Ren 动作 GIF 生成器启动 ===")

    im_m = Image.open(MARTIAL_SHEET)
    im_p = Image.open(PLAYFUL_SHEET)

    col_w = 344
    m_crops = [im_m.crop((i * col_w, 0, (i + 1) * col_w, 768)) for i in range(4)]
    p_crops = [im_p.crop((i * col_w, 0, (i + 1) * col_w, 768)) for i in range(4)]

    # 1. 功夫武术四式组合 GIF
    m_titles = [
        "1. 抱拳作揖礼 (Salute Bow)",
        "2. 马步推掌 (Horse Stance)",
        "3. 太极云手 (Cloud Hands)",
        "4. 升龙拳 (Dragon Uppercut)"
    ]
    m_tags = [
        "Lv.1 东方礼仪 · 屈膝前倾",
        "Lv.4 沉稳扎根 · 右掌蓄势",
        "Lv.4 行云流水 · 弧线圆融",
        "Lv.5 冲天飞跃 · 烈焰气浪"
    ]
    create_action_gif(m_crops, m_titles, m_tags, "cadet_ren_martial_combo.gif", target_w=280, target_h=580, hold_frames=20, trans_frames=8)

    # 2. 元气特技四式组合 GIF
    p_titles = [
        "1. 元气挥手 (Energetic Wave)",
        "2. 弹性跳跃 (Spring Jump)",
        "3. 金鸡独立 (Crane Balance)",
        "4. 华丽自旋 (360° Spin)"
    ]
    p_tags = [
        "Lv.1 三段圆弧 · 耳尖律动",
        "Lv.2 蓄力深蹲 · 腾空拉伸",
        "Lv.3 单腿支撑 · 核心微振",
        "Lv.5 3D 透视 · 秀尾转身"
    ]
    create_action_gif(p_crops, p_titles, p_tags, "cadet_ren_playful_stunts.gif", target_w=280, target_h=580, hold_frames=20, trans_frames=8)

    # 3. 八大影院级动作全景大阅兵 GIF
    all_crops = m_crops + p_crops
    all_titles = m_titles + p_titles
    all_tags = m_tags + p_tags
    create_action_gif(all_crops, all_titles, all_tags, "cadet_ren_all_actions_parade.gif", target_w=260, target_h=540, hold_frames=16, trans_frames=6)

    # 4. 1:1 设备端真机 135x240 屏幕渲染动效 GIF
    generate_device_screen_simulation_gif("cadet_ren_device_135x240_showcase.gif", fps=25)

    print("=== 全套动作 GIF 生成与归档圆满完成！ ===")

if __name__ == "__main__":
    main()
