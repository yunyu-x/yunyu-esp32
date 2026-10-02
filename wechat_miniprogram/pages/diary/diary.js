// pages/diary/diary.js
const { StorageManager } = require("../../utils/storage_manager.js");
const { buddyService } = require("../../utils/buddy_service.js");
const { haptics } = require("../../utils/haptics.js");

const FILTERS = [
  { key: "all",   label: "全部" },
  { key: "fav",   label: "❤️ 收藏" },
  { key: "feed",  label: "🍰 美食" },
  { key: "pet",   label: "🌸 抚摸" },
  { key: "groom", label: "✨ 梳毛" },
  { key: "play",  label: "✋ 击掌" },
  { key: "shake", label: "🌀 调皮" },
  { key: "sleep", label: "🌙 晚安" }
];

Page({
  data: {
    activeSection: "diary", // 'diary' | 'dialogue'
    petName: "小木",
    petLevel: 1,
    diaries: [],
    filteredDiaries: [],
    favoriteCount: 0,
    filterList: FILTERS,
    selectedFilter: "all",

    // 历史人机对话多轮记忆
    memories: [],
    isSyncingMemories: false,

    showShareModal: false,
    sharingDiary: null
  },

  onLoad(options) {
    if (options && options.tab === "dialogue") {
      this.setData({ activeSection: "dialogue" });
    }
    this.loadDiaries();
    this.loadMemories();

    // 监听实时日记与记忆更新
    this.stateListener = (evt) => {
      if (evt.type === "diary") {
        this.loadDiaries();
      } else if (evt.type === "memory") {
        this.loadMemories();
      }
    };
    buddyService.subscribe(this.stateListener);
  },

  onShow() {
    if (buddyService.diaryTargetTab) {
      this.setData({ activeSection: buddyService.diaryTargetTab });
      buddyService.diaryTargetTab = null;
    }
    this.loadDiaries();
    this.loadMemories();
  },

  onUnload() {
    if (this.stateListener) {
      buddyService.unsubscribe(this.stateListener);
    }
  },

  onPullDownRefresh() {
    if (this.data.activeSection === "dialogue") {
      this.handleSyncMemories(true);
    } else {
      this.loadDiaries();
      setTimeout(() => {
        wx.stopPullDownRefresh();
        wx.showToast({ title: "已同步最新日记", icon: "none" });
      }, 400);
    }
  },

  onSwitchSection(e) {
    const sec = e.currentTarget.dataset.section;
    if (sec && sec !== this.data.activeSection) {
      this.setData({ activeSection: sec });
      haptics.vibrate("light");
    }
  },

  loadMemories() {
    const mems = StorageManager.getMemories();
    this.setData({ memories: mems });
  },

  async handleSyncMemories(isPullDown = false) {
    this.setData({ isSyncingMemories: true });
    haptics.vibrate("medium");
    if (!isPullDown) {
      wx.showLoading({ title: "正在同步硬件记忆..." });
    }

    try {
      const list = await buddyService.syncMemories();
      this.setData({ 
        memories: list || [],
        isSyncingMemories: false 
      });
      if (!isPullDown) wx.hideLoading();
      else wx.stopPullDownRefresh();

      haptics.levelUp();
      wx.showToast({ title: `已同步 ${list.length} 条记忆`, icon: "success" });
    } catch (e) {
      this.setData({ isSyncingMemories: false });
      if (!isPullDown) wx.hideLoading();
      else wx.stopPullDownRefresh();
      wx.showToast({ title: "记忆同步失败", icon: "none" });
    }
  },

  handleClearMemories() {
    wx.showModal({
      title: "清空历史对话记忆",
      content: "确定要清空与小木的全部历史对话记忆吗？",
      confirmText: "清空",
      confirmColor: "#ef4444",
      success: (res) => {
        if (res.confirm) {
          buddyService.clearMemories();
          this.setData({ memories: [] });
          haptics.vibrate("medium");
          wx.showToast({ title: "记忆已清空", icon: "none" });
        }
      }
    });
  },

  handleCopyMemory(e) {
    const text = e.currentTarget.dataset.text;
    if (!text) return;
    wx.setClipboardData({
      data: text,
      success: () => {
        haptics.vibrate("light");
        wx.showToast({ title: "对话已复制", icon: "success" });
      }
    });
  },

  loadDiaries() {
    const list = StorageManager.getDiaries();
    const st = buddyService.petState || StorageManager.getPetState();
    const favCount = list.filter(d => d.isFavorite).length;

    this.setData({
      petName: st.name || "小木",
      petLevel: st.level || 1,
      diaries: list,
      favoriteCount: favCount
    });

    this.applyFilter(this.data.selectedFilter);
  },

  onSelectFilter(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({ selectedFilter: key });
    this.applyFilter(key);
    haptics.vibrate("light");
  },

  applyFilter(filterKey) {
    const all = this.data.diaries;
    if (filterKey === "all") {
      this.setData({ filteredDiaries: all });
      return;
    }
    if (filterKey === "fav") {
      this.setData({ filteredDiaries: all.filter(d => d.isFavorite) });
      return;
    }

    const keywordMap = {
      feed: ["美食", "喂", "大福", "吃", "舒芙蕾", "曲奇", "甜甜圈", "蛋糕"],
      pet: ["抚摸", "摸了摸", "摸摸", "温暖", "软洋洋"],
      groom: ["梳毛", "毛发", "小梳子", "舒适"],
      play: ["击掌", "默契", "搭档", "虎牙"],
      shake: ["调皮", "转圈", "眩晕", "星星", "晃动"],
      sleep: ["晚安", "入睡", "梦乡", "呼噜"]
    };

    const keywords = keywordMap[filterKey] || [];
    const filtered = all.filter(d => {
      const tagMatch = d.moodTag && keywords.some(k => d.moodTag.includes(k));
      const contentMatch = keywords.some(k => d.content.includes(k));
      return tagMatch || contentMatch;
    });

    this.setData({ filteredDiaries: filtered });
  },

  handleToggleFavorite(e) {
    const id = e.currentTarget.dataset.id;
    const isFav = StorageManager.toggleFavorite(id);
    haptics.vibrate(isFav ? "medium" : "light");
    this.loadDiaries();
  },

  handleDeleteDiary(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: "删除日记",
      content: "确定要永久抹去这条心声日记吗？",
      confirmText: "删除",
      confirmColor: "#ef4444",
      success: (res) => {
        if (res.confirm) {
          StorageManager.deleteDiary(id);
          this.loadDiaries();
          wx.showToast({ title: "已删除", icon: "none" });
        }
      }
    });
  },

  handleCopyDiary(e) {
    const content = e.currentTarget.dataset.content;
    if (!content) return;
    wx.setClipboardData({
      data: content,
      success: () => {
        haptics.vibrate("light");
        wx.showToast({ title: "已复制心声", icon: "success" });
      }
    });
  },

  handleOpenShareModal(e) {
    const diary = e.currentTarget.dataset.diary;
    if (!diary) return;
    haptics.vibrate("medium");
    this.setData({
      showShareModal: true,
      sharingDiary: diary
    });
  },

  handleCloseShareModal() {
    this.setData({ showShareModal: false, sharingDiary: null });
  },

  stopPropagation() {},

  handleCopyPosterText() {
    if (!this.data.sharingDiary) return;
    const text = `【LingBuddy · ${this.data.petName}的心声】\n“${this.data.sharingDiary.content}”\n—— 记录于 M5StickS3 灵宠伴侣`;
    wx.setClipboardData({
      data: text,
      success: () => {
        haptics.vibrate("light");
        wx.showToast({ title: "图文已复制", icon: "success" });
      }
    });
  },

  onShareAppMessage() {
    const content = this.data.sharingDiary ? this.data.sharingDiary.content : "我的灵宠小木今天又偷偷写日记啦！";
    return {
      title: `【小木的心声日记】"${content}"`,
      path: "/pages/index/index"
    };
  }
});
