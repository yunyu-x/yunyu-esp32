/**
 * wechat_miniprogram/components/avatar-canvas/avatar-canvas.js
 * -------------------------------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序原生 Canvas 2D 自适应微表情自定义组件
 * 特性：
 * 1. 严格适配 iOS / Android 各机型像素比 (DPR / pixelRatio)，杜绝视网膜屏模糊
 * 2. 纯矢量迪士尼动效解算 (水灵双高光、D型大笑皓齿、阿基米德金星、Pixie Dust 星芒)
 * 3. 具身触碰交互支持：轻触额头抚摸 (pet)、轻触嘴部投喂 (feed)、长按击掌 (play)
 * 4. 触觉微震动联觉与生命周期自动内存释放
 */

const { AvatarRenderer } = require("../../utils/avatar_renderer.js");
const { haptics } = require("../../utils/haptics.js");

Component({
  properties: {
    petState: {
      type: Object,
      value: {
        name: "悄悄",
        level: 1,
        xp: 15,
        energy: 100,
        mood: 0
      },
      observer(newVal) {
        // 外部状态变更响应
        this.currentPetState = newVal;
      }
    },
    widthRpx: {
      type: Number,
      value: 270
    },
    heightRpx: {
      type: Number,
      value: 480
    },
    interactive: {
      type: Boolean,
      value: true
    }
  },

  data: {
    showHint: false,
    hintText: ""
  },

  lifetimes: {
    attached() {
      this.renderer = new AvatarRenderer();
      this.currentPetState = this.data.petState;
      this.isRunning = false;
      this.canvas = null;
      this.ctx = null;
      this.animReqId = null;
      this.hintTimer = null;
    },

    ready() {
      this.initCanvas();
    },

    detached() {
      this.isRunning = false;
      if (this.canvas && this.canvas.cancelAnimationFrame && this.animReqId) {
        this.canvas.cancelAnimationFrame(this.animReqId);
      }
      if (this.hintTimer) clearTimeout(this.hintTimer);
      this.canvas = null;
      this.ctx = null;
    }
  },

  methods: {
    // 初始化自适应 Canvas 2D
    initCanvas() {
      const query = wx.createSelectorQuery().in(this);
      query.select("#avatarCanvas")
        .fields({ node: true, size: true })
        .exec((res) => {
          if (!res[0] || !res[0].node) return;

          const canvas = res[0].node;
          const ctx = canvas.getContext("2d");

          // 获取跨平台精确屏幕像素比 (DPR)
          let dpr = 2;
          try {
            if (typeof wx.getWindowInfo === "function") {
              dpr = wx.getWindowInfo().pixelRatio || 2;
            } else if (typeof wx.getSystemInfoSync === "function") {
              dpr = wx.getSystemInfoSync().pixelRatio || 2;
            }
          } catch (e) {
            dpr = 2;
          }

          // 设置物理画布分辨率与逻辑视口缩放
          const displayWidth = res[0].width;
          const displayHeight = res[0].height;

          canvas.width = Math.round(displayWidth * dpr);
          canvas.height = Math.round(displayHeight * dpr);
          ctx.scale(dpr, dpr);

          this.canvas = canvas;
          this.ctx = ctx;
          this.canvasWidth = displayWidth;
          this.canvasHeight = displayHeight;
          this.isRunning = true;

          this.startRenderLoop();
        });
    },

    // 60FPS 灵动微表情渲染心跳
    startRenderLoop() {
      const step = () => {
        if (!this.isRunning) return;

        if (this.ctx && this.canvas) {
          const st = this.currentPetState || this.data.petState;
          this.renderer.render(this.ctx, this.canvasWidth, this.canvasHeight, st);
        }

        if (this.canvas && typeof this.canvas.requestAnimationFrame === "function") {
          this.animReqId = this.canvas.requestAnimationFrame(step);
        } else {
          this.animReqId = setTimeout(step, 33);
        }
      };

      step();
    },

    // 触碰交互逻辑：轻触解算
    onCanvasTap(e) {
      if (!this.data.interactive) return;

      const touch = (e.detail && e.detail.y !== undefined) ? e.detail : (e.touches && e.touches[0]);
      let action = "pet";
      let hint = "🌸 摸摸小脑袋";

      if (touch && this.canvasHeight) {
        const relY = touch.y / this.canvasHeight;
        if (relY > 0.45 && relY < 0.70) {
          action = "feed";
          hint = "🍰 投喂小点心";
        } else if (relY <= 0.45) {
          action = "pet";
          hint = "🌸 摸摸小脑袋";
        } else {
          action = "groom";
          hint = "✨ 梳理软软毛发";
        }
      }

      this.showTouchHint(hint);
      this.triggerEvent("avataction", { action, source: "touch_tap" });
    },

    // 触碰交互逻辑：长按击掌
    onCanvasLongPress() {
      if (!this.data.interactive) return;
      this.showTouchHint("✋ 默契击掌！");
      this.triggerEvent("avataction", { action: "play", source: "long_press" });
    },

    showTouchHint(text) {
      if (this.hintTimer) clearTimeout(this.hintTimer);
      this.setData({ showHint: true, hintText: text });
      this.hintTimer = setTimeout(() => {
        this.setData({ showHint: false });
      }, 2000);
    }
  }
});
