// pages/feed/feed.js
const { buddyService } = require("../../utils/buddy_service.js");
const { haptics } = require("../../utils/haptics.js");

const SNACK_LIST = [
  {
    id: "snack_1",
    name: "草莓奶油大福",
    icon: "🍓",
    desc: "软糯Q弹的大福皮包裹着饱满甜草莓与丝滑奶油",
    energy: 20,
    xp: 10
  },
  {
    id: "snack_2",
    name: "鲜奶舒芙蕾蛋糕",
    icon: "🍰",
    desc: "空气感十足的轻盈云朵舒芙蕾，入口即化",
    energy: 25,
    xp: 12
  },
  {
    id: "snack_3",
    name: "比利时巧脆曲奇",
    icon: "🍪",
    desc: "浓郁黑巧豆融入酥脆黄油曲奇，香醇满溢",
    energy: 15,
    xp: 8
  },
  {
    id: "snack_4",
    name: "彩虹熔岩甜甜圈",
    icon: "🍩",
    desc: "七彩糖粒与微暖草莓熔岩流心，治愈系甜品王牌",
    energy: 30,
    xp: 15
  },
  {
    id: "snack_5",
    name: "焦糖香甜爆米花",
    icon: "🍿",
    desc: "电影院同款浓郁焦糖裹衣，嘎吱嘎吱脆脆响",
    energy: 15,
    xp: 8
  },
  {
    id: "snack_6",
    name: "宇治特调抹茶冰淇淋",
    icon: "🍵",
    desc: "微苦回甘的京都石磨抹茶，带来清凉夏日舒畅",
    energy: 20,
    xp: 12
  }
];

Page({
  data: {
    petState: {
      name: "悄悄",
      level: 1,
      xp: 15,
      energy: 100,
      mood: 0,
      feeds: 1
    },
    snackList: SNACK_LIST,
    isFeeding: false,
    currentSnack: null,
    latestFoodDiary: "主人喂我吃了一块草莓奶油大福，吧唧吧唧超级满足，活力满满！"
  },

  onLoad() {
    this.buddyService = buddyService;

    this.stateListener = (evt) => {
      const st = evt.petState || this.buddyService.petState;
      this.setData({
        petState: st
      });
      if (st.diary && (st.diary.includes("喂") || st.diary.includes("吃") || st.diary.includes("大福") || st.diary.includes("蛋糕"))) {
        this.setData({ latestFoodDiary: st.diary });
      }
    };

    this.buddyService.subscribe(this.stateListener);
  },

  onShow() {
    if (this.buddyService) {
      const st = this.buddyService.petState;
      this.setData({ petState: st });
      if (st.diary && (st.diary.includes("喂") || st.diary.includes("吃") || st.diary.includes("大福") || st.diary.includes("蛋糕"))) {
        this.setData({ latestFoodDiary: st.diary });
      }
    }
  },

  onUnload() {
    if (this.buddyService && this.stateListener) {
      this.buddyService.unsubscribe(this.stateListener);
    }
  },

  onPullDownRefresh() {
    setTimeout(() => wx.stopPullDownRefresh(), 500);
  },

  // 隔空投喂甜点核心逻辑
  async handleFeedSnack(e) {
    if (this.data.isFeeding) return;

    const snack = e.currentTarget.dataset.snack;
    if (!snack) return;

    this.setData({ isFeeding: true, currentSnack: snack });

    // 触发微信中度震感 (Embodied Haptic)
    haptics.feed();

    try {
      await this.buddyService.dispatchAction("feed", snack.name);
      
      const newDiary = `主人喂我吃了一块${snack.name}，吧唧吧唧超级满足，活力值回升！`;
      this.setData({
        latestFoodDiary: newDiary
      });

      wx.showToast({
        title: `已隔空投喂: ${snack.name}`,
        icon: "none",
        duration: 2000
      });
    } catch (err) {
      console.error("[Feed] feed error:", err);
      wx.showToast({ title: "投喂下发异常", icon: "none" });
    } finally {
      setTimeout(() => {
        this.setData({ isFeeding: false, currentSnack: null });
      }, 1200);
    }
  }
});
