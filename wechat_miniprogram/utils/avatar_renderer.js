/**
 * wechat_miniprogram/utils/avatar_renderer.js
 * -------------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序原生 Canvas 2D 迪士尼灵动微表情引擎
 * - 纯矢量解算，零图片资源加载延迟
 * - 完整呈现迪士尼艺术审美 (Disney Artistic Animation Aesthetic)
 *   1. 水灵双高光大眼 (Disney Liquid Eyes)
 *   2. D型皓齿粉舌微笑 (Disney D-Mouth)
 *   3. 咀嚼动效与飞跃碎屑 (Bursting Crumbs)
 *   4. Pixie Dust 小仙子星芒粒子
 *   5. 睫毛上翘俏皮眨眼与微露虎牙
 *   6. 阿基米德旋涡与环绕轨道金星
 */

class AvatarRenderer {
  constructor() {
    this.blinkProgress = 0.0;
    this.isBlinking = false;
    this.lastBlink = Date.now();
  }

  render(ctx, width, height, petState) {
    const now = Date.now();
    ctx.clearRect(0, 0, width, height);

    ctx.save();
    // 自动自适应任意视口尺寸 (基于 M5StickS3 135x240 黄金基准微表情坐标系)
    const scaleX = (width && width > 0) ? (width / 135.0) : 1.0;
    const scaleY = (height && height > 0) ? (height / 240.0) : 1.0;
    ctx.scale(scaleX, scaleY);

    const baseW = 135;
    const baseH = 240;

    // 0. 深邃夜空纯黑底色
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, baseW, baseH);

    // 1. 顶部状态栏 (0 ~ 18)
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, baseW, 18);
    ctx.fillStyle = "#f6d365";
    ctx.font = "bold 9px sans-serif";
    ctx.fillText(`${petState.name || "悄悄"} Lv.${petState.level || 1}`, 6, 12);

    ctx.fillStyle = "#34d399";
    ctx.textAlign = "right";
    const tags = ["就绪", "专注聆听", "歪头思考", "快乐说话", "心动开心", "眩晕转圈", "失重惊吓", "香甜好梦", "好奇探头", "傲娇得意", "大口咀嚼", "舒适梳毛", "默契放电"];
    ctx.fillText(tags[petState.mood] || "就绪", baseW - 6, 12);
    ctx.textAlign = "left";

    // 2. 双眼与面部基准参数
    const eye_y = 75;
    const eye_lx = 38;
    const eye_rx = 97;
    const eye_w = 28;
    const eye_h = 38;
    const mouth_x = 67;
    const mouth_y = 120;

    let eyeColor = "#38bdf8"; // 迪士尼灵动天青蓝
    if (petState.mood === 1) eyeColor = "#00f2fe"; // 专注青空蓝
    else if (petState.mood === 4 || petState.mood === 10) eyeColor = "#f472b6"; // 幸福甜心粉
    else if (petState.mood === 5) eyeColor = "#facc15"; // 晕眩星芒金
    else if (petState.mood === 2) eyeColor = "#fbbf24"; // 思考琥珀金
    else if (petState.mood === 11) eyeColor = "#22d3ee"; // 梳毛光晕青
    else if (petState.mood === 12) eyeColor = "#fde047"; // 击掌阳光金

    // 眨眼状态机
    if (!this.isBlinking && now - this.lastBlink > 2800) {
      this.isBlinking = true;
      this.lastBlink = now;
    }
    if (this.isBlinking) {
      const b_dur = now - this.lastBlink;
      if (b_dur < 100) this.blinkProgress = b_dur / 100.0;
      else if (b_dur < 200) this.blinkProgress = 1.0 - (b_dur - 100) / 100.0;
      else {
        this.isBlinking = false;
        this.blinkProgress = 0.0;
      }
    }

    // 绘制迪士尼水灵双高光大眼 (Disney Liquid Eyes)
    const drawDisneyEye = (cx, cy, w, h, pupilR, ox = 0, oy = 0, blink = 0) => {
      const cur_h = Math.max(3, h * (1.0 - blink * 0.9));
      ctx.fillStyle = eyeColor;
      this.drawRoundRect(ctx, cx - w / 2, cy - cur_h / 2, w, cur_h, 12);
      ctx.fill();

      if (cur_h > 12) {
        // 深邃黑瞳
        ctx.fillStyle = "#020617";
        ctx.beginPath();
        ctx.arc(cx + ox, cy + oy, pupilR, 0, Math.PI * 2);
        ctx.fill();

        // 迪士尼主高光 (右上纯白大高光 - Primary Catchlight)
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(cx + ox + 3.2, cy + oy - 3.2, 3.2, 0, Math.PI * 2);
        ctx.fill();

        // 迪士尼次高光 (左下微光 - Secondary Liquid Catchlight)
        ctx.fillStyle = "rgba(255, 255, 255, 0.72)";
        ctx.beginPath();
        ctx.arc(cx + ox - 2.8, cy + oy + 2.8, 1.6, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    // 绘制迪士尼 D-Mouth
    const drawDisneyDMouth = (mx, my, w, h) => {
      ctx.fillStyle = "#4c0519";
      ctx.beginPath();
      ctx.arc(mx, my - 2, w / 2, 0, Math.PI, false);
      ctx.closePath();
      ctx.fill();

      // 上排皓齿
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(mx - w / 3, my - 2, (w * 2) / 3, 3);

      // 下排粉舌
      ctx.fillStyle = "#fb7185";
      ctx.beginPath();
      ctx.arc(mx, my + 3, w / 3, 0, Math.PI, false);
      ctx.fill();
    };

    // 绘制粉嫩软弹腮红
    const drawCheeks = (bouncy = false) => {
      const r = bouncy ? (7.5 + Math.sin(now * 0.015) * 1.5) : 6.5;
      ctx.fillStyle = "rgba(244, 114, 182, 0.65)";
      ctx.beginPath(); ctx.arc(17, 92, r, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(118, 92, r, 0, Math.PI * 2); ctx.fill();
    };

    // 绘制五角金星
    const drawStar = (cx, cy, r) => {
      ctx.fillStyle = "#facc15";
      ctx.beginPath();
      for (let i = 0; i < 5; i++) {
        const a1 = (i * 72 - 90) * Math.PI / 180;
        const a2 = ((i * 72 + 36) - 90) * Math.PI / 180;
        if (i === 0) ctx.moveTo(cx + Math.cos(a1) * r, cy + Math.sin(a1) * r);
        else ctx.lineTo(cx + Math.cos(a1) * r, cy + Math.sin(a1) * r);
        ctx.lineTo(cx + Math.cos(a2) * (r * 0.45), cy + Math.sin(a2) * (r * 0.45));
      }
      ctx.closePath();
      ctx.fill();
    };

    // 表情分支解算
    if (petState.mood === 5) {
      // 🌀 晕眩：阿基米德旋涡 + 轨道金星
      const spin = now * 0.007;
      [eye_lx, eye_rx].forEach(x => {
        ctx.strokeStyle = eyeColor;
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        for (let a = 0; a < 4 * Math.PI; a += 0.25) {
          const r = 2.0 + a * 1.0;
          const px = x + Math.cos(a + spin) * r;
          const py = eye_y + Math.sin(a + spin) * r;
          if (a === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
      });

      for (let i = 0; i < 3; i++) {
        const st_ang = now * 0.005 + (i * 2.094);
        const sx = 67 + Math.cos(st_ang) * 44;
        const sy = 40 + Math.sin(st_ang) * 9;
        drawStar(sx, sy, 4.5);
      }

      ctx.strokeStyle = "#facc15";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(mouth_x - 10, mouth_y);
      ctx.quadraticCurveTo(mouth_x - 5, mouth_y - 4, mouth_x, mouth_y);
      ctx.quadraticCurveTo(mouth_x + 5, mouth_y + 4, mouth_x + 10, mouth_y);
      ctx.stroke();
    }
    else if (petState.mood === 7) {
      // 🌙 睡眠：安睡微垂弧线 + Zzz 气泡飘动
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 3.2;
      [eye_lx, eye_rx].forEach(x => {
        ctx.beginPath();
        ctx.arc(x, eye_y - 2, 12, 0.2 * Math.PI, 0.8 * Math.PI, false);
        ctx.stroke();
      });

      const z_prog = (now % 2400) / 2400;
      const zy1 = 58 - z_prog * 25;
      const zy2 = 48 - z_prog * 25;
      ctx.fillStyle = `rgba(56, 189, 248, ${1.0 - z_prog * 0.8})`;
      ctx.font = "bold 13px sans-serif";
      ctx.fillText("Z", 78 + Math.sin(now * 0.004) * 4, zy1);
      ctx.font = "bold 9px sans-serif";
      ctx.fillText("z", 90 + Math.sin(now * 0.004 + 1) * 3, zy2);

      ctx.fillStyle = "#475569";
      ctx.beginPath();
      ctx.arc(mouth_x, mouth_y, 3, 0, Math.PI * 2);
      ctx.fill();
    }
    else if (petState.mood === 10) {
      // 🍰 进食：笑眼弯弯 + 弹动咀嚼 D 嘴 + 飞跃金色蛋糕碎屑
      ctx.strokeStyle = eyeColor;
      ctx.lineWidth = 3.2;
      [eye_lx, eye_rx].forEach(x => {
        ctx.beginPath();
        ctx.arc(x, eye_y - 1, 13, 0.1 * Math.PI, 0.9 * Math.PI, true);
        ctx.stroke();
      });
      drawCheeks(true);

      const chew = Math.sin(now * 0.02);
      const cw = 20 + chew * 3;
      const ch = 12 + Math.abs(chew) * 6;
      drawDisneyDMouth(mouth_x, mouth_y, cw, ch);

      for (let i = 0; i < 4; i++) {
        const ca = (now * 0.008 + i * 1.57) % 6.28;
        const cr = 14 + (Math.sin(now * 0.01 + i) * 6);
        ctx.fillStyle = (i % 2 === 0) ? "#facc15" : "#fb7185";
        ctx.beginPath();
        ctx.arc(mouth_x + Math.cos(ca) * cr, mouth_y + Math.sin(ca) * (cr * 0.6) - 2, 2.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    else if (petState.mood === 11) {
      // ✨ 舒适梳毛：微弧笑眼 + Pixie Dust 闪耀四角星芒
      ctx.strokeStyle = eyeColor;
      ctx.lineWidth = 3.2;
      [eye_lx, eye_rx].forEach(x => {
        ctx.beginPath();
        ctx.arc(x, eye_y - 2, 13, 0.1 * Math.PI, 0.9 * Math.PI, true);
        ctx.stroke();
      });
      drawCheeks(true);

      const p1 = (now * 0.003) % 6.28;
      const p2 = (now * 0.003 + 2.1) % 6.28;
      const drawSparkle = (sx, sy, r, col) => {
        ctx.fillStyle = col;
        ctx.beginPath();
        ctx.moveTo(sx, sy - r);
        ctx.quadraticCurveTo(sx, sy, sx + r, sy);
        ctx.quadraticCurveTo(sx, sy, sx, sy + r);
        ctx.quadraticCurveTo(sx, sy, sx - r, sy);
        ctx.quadraticCurveTo(sx, sy, sx, sy - r);
        ctx.fill();
      };
      drawSparkle(22 + Math.sin(p1) * 6, 60 + Math.cos(p1) * 8, 5, "#facc15");
      drawSparkle(114 + Math.cos(p2) * 6, 62 + Math.sin(p2) * 8, 4.5, "#38bdf8");

      drawDisneyDMouth(mouth_x, mouth_y, 16, 8);
    }
    else if (petState.mood === 12) {
      // ✋ 默契击掌：左眼上翘飞扬睫毛眨眼，右眼灵动高光，微露小虎牙
      ctx.strokeStyle = eyeColor;
      ctx.lineWidth = 3.4;
      ctx.beginPath();
      ctx.arc(eye_lx, eye_y - 2, 13, 0.08 * Math.PI, 0.92 * Math.PI, true);
      ctx.stroke();
      // 上翘飞扬睫毛
      ctx.beginPath();
      ctx.moveTo(eye_lx + 12, eye_y - 2);
      ctx.quadraticCurveTo(eye_lx + 15, eye_y - 7, eye_lx + 17, eye_y - 8);
      ctx.stroke();

      drawDisneyEye(eye_rx, eye_y, eye_w, eye_h, petState.pupil_r || 7.0, 0, 0, 0);
      drawCheeks(true);

      drawDisneyDMouth(mouth_x, mouth_y, 22, 12);
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.moveTo(mouth_x - 3, mouth_y - 2);
      ctx.lineTo(mouth_x + 1, mouth_y - 2);
      ctx.lineTo(mouth_x - 1, mouth_y + 4);
      ctx.closePath();
      ctx.fill();
    }
    else if (petState.mood === 3 || petState.mood === 4) {
      // 🌸 快乐抚摸：月牙弯弯爱心眼 + D型大微笑
      ctx.strokeStyle = eyeColor;
      ctx.lineWidth = 3.2;
      [eye_lx, eye_rx].forEach(x => {
        ctx.beginPath();
        ctx.arc(x, eye_y - 2, 13, 0.08 * Math.PI, 0.92 * Math.PI, true);
        ctx.stroke();
      });
      drawCheeks(true);
      drawDisneyDMouth(mouth_x, mouth_y, 22, 13);
    }
    else {
      // 常态 / 专注聆听 / 歪头思考
      const ox = (petState.mood === 2) ? 4.5 : 0;
      const oy = (petState.mood === 2) ? -4.0 : 0;
      drawDisneyEye(eye_lx, eye_y, eye_w, eye_h, petState.pupil_r || 7.0, ox, oy, this.blinkProgress);
      drawDisneyEye(eye_rx, eye_y, eye_w, eye_h, petState.pupil_r || 7.0, ox, oy, this.blinkProgress);
      drawCheeks(false);

      ctx.strokeStyle = "#475569";
      ctx.lineWidth = 2.0;
      ctx.beginPath();
      ctx.arc(mouth_x, mouth_y - 2, 6, 0.15 * Math.PI, 0.85 * Math.PI, false);
      ctx.stroke();
    }

    // 4. 对话字幕气泡 (Y: 154 ~ 216)
    ctx.fillStyle = "#0f172a";
    this.drawRoundRect(ctx, 6, 158, 123, 62, 8);
    ctx.fill();
    ctx.strokeStyle = "#1e293b";
    ctx.stroke();

    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 10px sans-serif";
    ctx.fillText("微信小程序直连中", 12, 178);
    ctx.fillStyle = "#94a3b8";
    ctx.font = "10px sans-serif";
    ctx.fillText("隔空互动更有趣~", 12, 196);

    // 5. 底部亲密度与活力状态条 (Y: 220 ~ 240)
    ctx.fillStyle = "#f472b6";
    ctx.font = "bold 9px sans-serif";
    ctx.fillText(`♥ 亲密:${petState.xp || 15}% 活力:${petState.energy || 100}%`, 6, 232);

    ctx.restore();
  }

  drawRoundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
}

module.exports = {
  AvatarRenderer
};
