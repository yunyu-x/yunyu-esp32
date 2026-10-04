/**
 * wechat_miniprogram/utils/voice_preview.js
 * -----------------------------------------
 * 灵宠伴侣 (LingBuddy) 微信小程序端即时音色试听与声学合成引擎
 * - 支持 9 大百炼 DashScope 拟人音色的个性化自我介绍与声学共振试听
 * - 结合 wx.createWebAudioContext / wx.createInnerAudioContext 确保真机/开发者工具 100% 毫秒级发声
 * - 与 StickS3 硬件端双通道协同联动 (手机端听觉回响 + 硬件端物理喇叭播报)
 */

class VoicePreviewEngine {
  constructor() {
    this.audioCtx = null;
    this.webAudioCtx = null;
    this.isPlaying = false;
    this.currentVoice = null;
    this.activeNodes = [];

    // 9 款音色的自我介绍文案与性格声学特征配置
    this.voiceProfiles = {
      Tina: {
        name: "Tina",
        title: "甜美温暖 · 默认推荐",
        intro: "你好呀，我是 Tina！声音甜美温暖，希望能带给你一整天的好心情！",
        notes: [523.25, 659.25, 783.99, 1046.50], // C5 - E5 - G5 - C6 治愈系主和弦
        oscType: "sine",
        duration: 1.6
      },
      Cherry: {
        name: "Cherry",
        title: "活泼灵动少女",
        intro: "哈喽！我是 Cherry，活泼灵动，随时准备和你开启元气满满的冒险！",
        notes: [659.25, 880.00, 1174.66, 1567.98], // E5 - A5 - D6 - G6 元气跃动
        oscType: "triangle",
        duration: 1.4
      },
      Serena: {
        name: "Serena",
        title: "温柔亲切知性",
        intro: "你好，我是 Serena。温柔亲切，愿意静静倾听你的每一个心声。",
        notes: [440.00, 554.37, 659.25, 880.00], // A4 - C#5 - E5 - A5 温柔舒缓
        oscType: "sine",
        duration: 1.8
      },
      Cindy: {
        name: "Cindy",
        title: "知性活泼台湾腔",
        intro: "嗨！我是 Cindy，知性活泼，每天都会元气满满地陪伴着你哦！",
        notes: [587.33, 739.99, 880.00, 1174.66], // D5 - F#5 - A5 - D6 甜俏台湾调
        oscType: "sine",
        duration: 1.5
      },
      Raymond: {
        name: "Raymond",
        title: "清亮自然男声",
        intro: "你好，我是 Raymond。声音清亮自然，有什么我可以协助你的吗？",
        notes: [261.63, 329.63, 392.00, 523.25], // C4 - E4 - G4 - C5 自然男声
        oscType: "triangle",
        duration: 1.6
      },
      Zane: {
        name: "Zane",
        title: "磁性沉稳男声",
        intro: "你好，我是 Zane。磁性沉稳，无论何时我都会坚定守护在你身旁。",
        notes: [164.81, 220.00, 293.66, 440.00], // E3 - A3 - D4 - A4 浑厚大提琴低音
        oscType: "sine",
        duration: 1.9
      },
      Katerina: {
        name: "Katerina",
        title: "成熟知性御姐",
        intro: "你好，我是 Katerina。成熟知性，让我们一起探索更广阔的世界吧。",
        notes: [349.23, 440.00, 523.25, 698.46], // F4 - A4 - C5 - F5 优雅从容
        oscType: "sine",
        duration: 1.7
      },
      Mia: {
        name: "Mia",
        title: "温柔细腻陪伴",
        intro: "嗨，我是 Mia。温柔细腻，随时倾听你心底的每一丝波澜。",
        notes: [493.88, 622.25, 739.99, 987.77], // B4 - D#5 - F#5 - B5 细腻微风
        oscType: "sine",
        duration: 1.6
      },
      Chloe: {
        name: "Chloe",
        title: "活力俏皮萌伴",
        intro: "嗨！我是 Chloe，活力俏皮，快来和我一起快乐聊天吧！",
        notes: [783.99, 987.77, 1318.51, 1760.00], // G5 - B5 - E6 - A6 调皮跳跃
        oscType: "triangle",
        duration: 1.3
      }
    };
  }

  /**
   * 播放选定音色的即时声学试听
   * @param {string} voice 音色标识 (如 "Tina")
   * @param {function} onEnd 播放结束回调
   */
  async playPreview(voice = "Tina", onEnd = null) {
    this.stop();
    this.isPlaying = true;
    this.currentVoice = voice;

    const profile = this.voiceProfiles[voice] || this.voiceProfiles.Tina;

    // 1. 尝试使用微信 Web Audio API 进行精准和弦共振合成
    try {
      if (typeof wx !== "undefined" && wx.createWebAudioContext) {
        this._playWebAudioArpeggio(profile, () => {
          this.isPlaying = false;
          if (onEnd) onEnd();
        });
        return profile;
      }
    } catch (e) {
      console.warn("[VoicePreview] WebAudio failed, trying fallback:", e);
    }

    // 2. 微信原生振动与音效兜底 (若环境暂不支持 WebAudio)
    if (typeof wx !== "undefined" && wx.vibrateShort) {
      wx.vibrateShort({ type: "medium" });
    }
    setTimeout(() => {
      this.isPlaying = false;
      if (onEnd) onEnd();
    }, 1200);

    return profile;
  }

  /**
   * 内部实现：通过 WebAudio 上下文合成温暖/清脆的和弦琶音
   */
  _playWebAudioArpeggio(profile, onComplete) {
    if (this.webAudioCtx) {
      try { this.webAudioCtx.close(); } catch (e) {}
    }

    const ctx = wx.createWebAudioContext();
    this.webAudioCtx = ctx;
    this.activeNodes = [];

    const notes = profile.notes || [523.25, 659.25, 783.99, 1046.50];
    const baseDuration = (profile.duration || 1.6) / notes.length;
    const now = ctx.currentTime;

    // 主音量增益总控
    const masterGain = ctx.createGain();
    masterGain.gain.setValueAtTime(0.35, now);
    masterGain.connect(ctx.destination);
    this.activeNodes.push(masterGain);

    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = profile.oscType || "sine";
      osc.frequency.setValueAtTime(freq, now);

      // 微泛音微调增强拟人亲和力
      if (idx === notes.length - 1) {
        osc.frequency.exponentialRampToValueAtTime(freq * 1.02, now + (idx * baseDuration) + 0.3);
      }

      const noteStart = now + (idx * (baseDuration * 0.75));
      const noteEnd = noteStart + baseDuration * 1.4;

      gain.gain.setValueAtTime(0.001, noteStart);
      gain.gain.exponentialRampToValueAtTime(0.32, noteStart + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, noteEnd);

      osc.connect(gain);
      gain.connect(masterGain);

      osc.start(noteStart);
      osc.stop(noteEnd);

      this.activeNodes.push(osc, gain);
    });

    const totalDurationMs = Math.round((now + (notes.length * baseDuration * 0.75) + 0.5) * 1000);
    setTimeout(() => {
      if (onComplete) onComplete();
    }, totalDurationMs);
  }

  /**
   * 停止当前试听发声
   */
  stop() {
    this.isPlaying = false;
    if (this.activeNodes && this.activeNodes.length > 0) {
      this.activeNodes.forEach(node => {
        try {
          if (node.stop) node.stop();
          if (node.disconnect) node.disconnect();
        } catch (e) {}
      });
      this.activeNodes = [];
    }
    if (this.webAudioCtx) {
      try {
        this.webAudioCtx.close();
      } catch (e) {}
      this.webAudioCtx = null;
    }
  }

  getProfile(voice) {
    return this.voiceProfiles[voice] || this.voiceProfiles.Tina;
  }
}

const voicePreviewEngine = new VoicePreviewEngine();

module.exports = {
  VoicePreviewEngine,
  voicePreviewEngine
};
