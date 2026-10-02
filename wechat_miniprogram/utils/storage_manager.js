/**
 * wechat_miniprogram/utils/storage_manager.js
 * -------------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序离线持久化存储管理器
 * - 基于 wx.setStorageSync / wx.getStorageSync 实现零延迟本地沉淀
 * - 断开蓝牙与断网后仍可随时查看第一人称心声日记本与历史对话记忆
 * - 支持按情绪标签过滤、日记收藏与导出分享
 */

const STORAGE_KEY_DIARIES   = "lingbuddy_diaries_v1";
const STORAGE_KEY_MEMORIES  = "lingbuddy_memories_v1";
const STORAGE_KEY_PET_STATE = "lingbuddy_pet_state_v1";
const STORAGE_KEY_SETTINGS  = "lingbuddy_settings_v1";

const DEFAULT_DIARIES = [
  {
    id: "init_1",
    timestamp: Date.now() - 3600000 * 2,
    timeStr: "2小时前",
    content: "主人轻轻摸了摸我的小脑瓜，耳边的指示灯闪了闪，今天也是被爱意包围的一天！",
    mood: 4,
    moodTag: "🌸 抚摸",
    isFavorite: true
  },
  {
    id: "init_2",
    timestamp: Date.now() - 3600000 * 5,
    timeStr: "5小时前",
    content: "主人喂我吃了一块草莓奶油大福，吧唧吧唧超级满足，活力值瞬间回满 100%！",
    mood: 10,
    moodTag: "🍰 美食",
    isFavorite: false
  },
  {
    id: "init_3",
    timestamp: Date.now() - 3600000 * 24,
    timeStr: "昨天",
    content: "和主人默契击掌！小虎牙笑得合不拢嘴，我们今天的默契值突破天际啦！",
    mood: 12,
    moodTag: "✋ 击掌",
    isFavorite: true
  }
];

const DEFAULT_SETTINGS = {
  vibrationEnabled: true,
  wifiHost: "192.168.110.67",
  savedSsid: "",
  savedPwd: "",
  autoReconnect: true,
  screenAvatarMode: true
};

class StorageManager {
  // --- 1. 日记沉淀与检索 ---

  static getDiaries() {
    try {
      const data = wx.getStorageSync(STORAGE_KEY_DIARIES);
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    } catch (e) {
      console.warn("[Storage] getDiaries error:", e);
    }
    return DEFAULT_DIARIES;
  }

  static saveDiaryEntry(content, mood = 0, moodTag = "📖 心声") {
    if (!content || typeof content !== "string" || !content.trim()) return null;
    const cleanContent = content.trim();

    try {
      const diaries = this.getDiaries();

      // 去重防抖：若最后一条日记内容完全相同且时间差在 3 秒以内，不重复插入
      if (diaries.length > 0 && diaries[0].content === cleanContent && (Date.now() - diaries[0].timestamp < 3000)) {
        return diaries[0];
      }

      const now = Date.now();
      const newEntry = {
        id: "diary_" + now + "_" + Math.floor(Math.random() * 1000),
        timestamp: now,
        timeStr: this.formatTime(new Date(now)),
        content: cleanContent,
        mood: mood,
        moodTag: moodTag,
        isFavorite: false
      };

      diaries.unshift(newEntry);
      // 保留最近 100 条日记
      const trimmed = diaries.slice(0, 100);
      wx.setStorageSync(STORAGE_KEY_DIARIES, trimmed);
      return newEntry;
    } catch (e) {
      console.error("[Storage] saveDiaryEntry error:", e);
      return null;
    }
  }

  static toggleFavorite(id) {
    try {
      const diaries = this.getDiaries();
      const target = diaries.find(d => d.id === id);
      if (target) {
        target.isFavorite = !target.isFavorite;
        wx.setStorageSync(STORAGE_KEY_DIARIES, diaries);
        return target.isFavorite;
      }
    } catch (e) {
      console.error("[Storage] toggleFavorite error:", e);
    }
    return false;
  }

  static deleteDiary(id) {
    try {
      let diaries = this.getDiaries();
      diaries = diaries.filter(d => d.id !== id);
      wx.setStorageSync(STORAGE_KEY_DIARIES, diaries);
      return true;
    } catch (e) {
      console.error("[Storage] deleteDiary error:", e);
      return false;
    }
  }

  static clearAllDiaries() {
    try {
      wx.removeStorageSync(STORAGE_KEY_DIARIES);
      return true;
    } catch (e) {
      return false;
    }
  }

  // --- 2. 对话长程记忆流沉淀 ---

  static getMemories() {
    try {
      const mems = wx.getStorageSync(STORAGE_KEY_MEMORIES);
      if (Array.isArray(mems)) return mems;
    } catch (e) {}
    return [
      { user: "你好小木，今天天气怎么样？", ai: "今天阳光明媚，微风正好，最适合我们一起去散步啦！" }
    ];
  }

  static saveMemories(memories) {
    if (!Array.isArray(memories)) return;
    try {
      wx.setStorageSync(STORAGE_KEY_MEMORIES, memories.slice(-50));
    } catch (e) {
      console.error("[Storage] saveMemories error:", e);
    }
  }

  // --- 3. 灵宠核心快照 ---

  static getPetState() {
    try {
      const st = wx.getStorageSync(STORAGE_KEY_PET_STATE);
      if (st && typeof st === "object") return st;
    } catch (e) {}
    return {
      name: "小木",
      level: 1,
      xp: 15,
      energy: 100,
      mood: 0,
      feeds: 1,
      grooms: 0,
      pets: 0,
      shakes: 0,
      diary: "今天刚刚苏醒，期待和主人一起探索世界！"
    };
  }

  static savePetState(petState) {
    if (!petState) return;
    try {
      wx.setStorageSync(STORAGE_KEY_PET_STATE, petState);
    } catch (e) {
      console.error("[Storage] savePetState error:", e);
    }
  }

  // --- 4. 系统设置 ---

  static getSettings() {
    try {
      const s = wx.getStorageSync(STORAGE_KEY_SETTINGS);
      if (s && typeof s === "object") {
        return { ...DEFAULT_SETTINGS, ...s };
      }
    } catch (e) {}
    return { ...DEFAULT_SETTINGS };
  }

  static saveSettings(settings) {
    try {
      const current = this.getSettings();
      const updated = { ...current, ...settings };
      wx.setStorageSync(STORAGE_KEY_SETTINGS, updated);
      return updated;
    } catch (e) {
      console.error("[Storage] saveSettings error:", e);
      return DEFAULT_SETTINGS;
    }
  }

  // 格式化时间为友好字符串
  static formatTime(date) {
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}月${day}日 ${hours}:${minutes}`;
  }
}

module.exports = {
  StorageManager,
  STORAGE_KEY_DIARIES,
  STORAGE_KEY_MEMORIES,
  STORAGE_KEY_PET_STATE,
  STORAGE_KEY_SETTINGS
};
