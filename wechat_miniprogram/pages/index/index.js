// pages/index/index.js
const { buddyService } = require("../../utils/buddy_service.js");
const { StorageManager } = require("../../utils/storage_manager.js");
const { haptics } = require("../../utils/haptics.js");

const MOOD_TAGS = [
  "就绪", "专注聆听", "歪头思考", "快乐说话", 
  "心动开心", "眩晕转圈", "失重惊吓", "香甜好梦", 
  "好奇探头", "傲娇得意", "大口咀嚼", "舒适梳毛", "默契放电"
];

Page({
  data: {
    isConnected: false,
    connectionStatusText: "未连接伴侣",
    isBleMode: false,
    isWifiMode: false,
    isSimMode: false,
    isDeviceWifiOnline: false,
    networkBadgeText: "网络离线",
    networkBadgeClass: "status-offline-red",

    bleBtnText: "蓝牙连接",
    wifiBtnText: "Wi-Fi 直连",
    simBtnText: "演示仿真",

    petState: {
      volume: 70,
      xp: 15,
      energy: 100,
      mood: 0,
      feeds: 0,
      grooms: 0,
      pets: 0,
      shakes: 0,
      diary: "今天刚刚苏醒，期待和主人一起探索世界！"
    },

    currentMoodTag: "就绪",
    diaryCount: 3,

    hotspot: {
      isHotspot: false,
      usedMb: 0,
      limitMb: 100,
      remainingMb: 100,
      cutoffActive: false
    },

    snackOptions: [
      "🍓 草莓奶油大福 (+20活力, +10羁绊)",
      "🍰 鲜奶舒芙蕾蛋糕 (+20活力, +10羁绊)",
      "🍪 比利时巧脆曲奇 (+20活力, +10羁绊)",
      "🍩 彩虹熔岩甜甜圈 (+20活力, +10羁绊)",
      "🍿 香甜爆米花 (+20活力, +10羁绊)"
    ],
    selectedSnackIndex: 0,

    memoryCount: 0,
    latestMemory: null,

    // 3D 姿态与关节动力学
    bearYaw: 0,
    imuBalanceEnabled: true,
    jointList: [
      { id: 8, name: "右臂肩关节 (R_Shoulder)" },
      { id: 11, name: "左臂肩关节 (L_Shoulder)" },
      { id: 9, name: "右肘关节 (R_Elbow)" },
      { id: 12, name: "左肘关节 (L_Elbow)" },
      { id: 1, name: "颈部头部 (Neck/Head)" },
      { id: 6, name: "脊柱胸腔 (Spine)" },
      { id: 15, name: "右膝关节 (R_Knee)" },
      { id: 18, name: "左膝关节 (L_Knee)" }
    ],
    jointNames: [
      "右臂肩关节 (R_Shoulder)",
      "左臂肩关节 (L_Shoulder)",
      "右肘关节 (R_Elbow)",
      "左肘关节 (L_Elbow)",
      "颈部头部 (Neck/Head)",
      "脊柱胸腔 (Spine)",
      "右膝关节 (R_Knee)",
      "左膝关节 (L_Knee)"
    ],
    selectedJointIndex: 0,
    selectedJointAngle: 0
  },

  onLoad() {
    this.buddyService = buddyService;

    // 订阅 BuddyService 统一状态机
    this.stateListener = (evt) => {
      this.syncFromService(evt);
      if (evt.type === "memory") {
        this.refreshMemories();
      } else if (evt.type === "diary") {
        this.refreshDiaryStats();
      }
    };
    this.buddyService.subscribe(this.stateListener);

    this.refreshDiaryStats();
    this.refreshMemories();
  },

  onShow() {
    // 每次切回主页刷新数据
    if (this.buddyService) {
      this.syncFromService({
        petState: this.buddyService.petState,
        isConnected: this.buddyService.isConnected,
        isBleMode: this.buddyService.isBleMode,
        isWifiMode: this.buddyService.isWifiMode,
        isSimMode: this.buddyService.isSimMode,
        connectionStatusText: this.buddyService.connectionStatusText
      });
    }
    this.refreshDiaryStats();
    this.refreshMemories();
  },

  onUnload() {
    if (this.buddyService && this.stateListener) {
      this.buddyService.unsubscribe(this.stateListener);
    }
  },

  onPullDownRefresh() {
    // 下拉刷新同步
    if (this.data.isWifiMode) {
      this.buddyService.httpClient.getPetStatus().then(st => {
        this.buddyService.updatePetState(st);
        wx.stopPullDownRefresh();
        wx.showToast({ title: "已刷新状态", icon: "none" });
      }).catch(() => {
        wx.stopPullDownRefresh();
      });
    } else {
      setTimeout(() => wx.stopPullDownRefresh(), 500);
    }
  },

  syncFromService(evt) {
    const st = evt.petState || this.buddyService.petState;
    const moodIdx = (st && st.mood) || 0;
    const moodTag = MOOD_TAGS[moodIdx] || "就绪";
    const hs = evt.hotspot || this.buddyService.hotspot || this.data.hotspot;
    const dw = this.buddyService.deviceWifi;

    const isDevOnline = Boolean(
      (dw && (dw.sta_connected || dw.sta_state === "connected")) ||
      this.buddyService.isWifiMode ||
      (this.buddyService.petState && this.buddyService.petState.sta_connected)
    );

    let badgeText = "网络离线";
    let badgeClass = "status-offline-red";
    if (isDevOnline) {
      if (hs && hs.isHotspot) {
        badgeText = "热点在线";
        badgeClass = "badge-hotspot-connected";
      } else {
        badgeText = "Wi-Fi 在线";
        badgeClass = "status-online";
      }
    }

    const patch = {};
    if (this.data.isDeviceWifiOnline !== isDevOnline) patch.isDeviceWifiOnline = isDevOnline;
    if (this.data.networkBadgeText !== badgeText) patch.networkBadgeText = badgeText;
    if (this.data.networkBadgeClass !== badgeClass) patch.networkBadgeClass = badgeClass;
    if (this.data.currentMoodTag !== moodTag) patch.currentMoodTag = moodTag;

    const isConn = evt.isConnected !== undefined ? evt.isConnected : this.buddyService.isConnected;
    const isBle = evt.isBleMode !== undefined ? evt.isBleMode : this.buddyService.isBleMode;
    const isWifi = evt.isWifiMode !== undefined ? evt.isWifiMode : this.buddyService.isWifiMode;
    const isSim = evt.isSimMode !== undefined ? evt.isSimMode : this.buddyService.isSimMode;

    if (this.data.isConnected !== isConn) patch.isConnected = isConn;
    if (this.data.isBleMode !== isBle) {
      patch.isBleMode = isBle;
      patch.bleBtnText = isBle ? "断开蓝牙" : "蓝牙连接";
    }
    if (this.data.isWifiMode !== isWifi) {
      patch.isWifiMode = isWifi;
      patch.wifiBtnText = isWifi ? "断开 Wi-Fi" : "Wi-Fi 直连";
    }
    if (this.data.isSimMode !== isSim) {
      patch.isSimMode = isSim;
      patch.simBtnText = isSim ? "退出仿真" : "演示仿真";
    }

    const connText = evt.connectionStatusText || this.buddyService.connectionStatusText;
    if (this.data.connectionStatusText !== connText) patch.connectionStatusText = connText;

    if (!this.data.petState || 
        this.data.petState.mood !== st.mood || 
        this.data.petState.level !== st.level || 
        this.data.petState.xp !== st.xp || 
        this.data.petState.energy !== st.energy ||
        this.data.petState.diary !== st.diary ||
        this.data.petState.subtitle !== st.subtitle ||
        this.data.petState.name !== st.name) {
      patch.petState = st;
    }

    if (!this.data.hotspot || this.data.hotspot.usedMb !== hs.usedMb || this.data.hotspot.isHotspot !== hs.isHotspot || this.data.hotspot.cutoffActive !== hs.cutoffActive) {
      patch.hotspot = { ...hs };
    }

    if (Object.keys(patch).length > 0) {
      this.setData(patch);
    }
  },

  refreshDiaryStats() {
    const diaries = StorageManager.getDiaries();
    this.setData({ diaryCount: diaries.length });
  },

  refreshMemories() {
    const mems = StorageManager.getMemories();
    const count = mems.length;
    let latest = null;
    if (count > 0) {
      // 兼容固件倒序 (mems[0] 最新) 与正序存储模式
      if (mems[0] && mems[0].id !== undefined && mems[count - 1] && mems[count - 1].id !== undefined) {
        latest = (mems[0].id >= mems[count - 1].id) ? mems[0] : mems[count - 1];
      } else {
        latest = mems[0] || mems[count - 1];
      }
    }
    this.setData({
      memoryCount: count,
      latestMemory: latest
    });
  },

  // 1. 触摸头像组件触发动作
  handleAvatarTouchAction(e) {
    const action = e.detail && e.detail.action ? e.detail.action : "pet";
    this.executeAction(action);
  },

  // 2. 核心具身动作下发
  async executeAction(action, value = "") {
    try {
      await this.buddyService.dispatchAction(action, value);
      this.refreshDiaryStats();
    } catch (e) {
      console.warn("[Index] executeAction error:", e);
      wx.showToast({ title: "指令发送异常", icon: "none" });
    }
  },

  // 按钮交互映射
  handlePetAction()   { this.executeAction("pet"); },
  handleGroomAction() { this.executeAction("groom"); },
  handlePlayAction()  { this.executeAction("play"); },
  handleShakeAction() { this.executeAction("shake"); },
  handleSleepAction() { this.executeAction("sleep"); },
  handleWakeAction()  { this.executeAction("wake"); },
  handleToggleAvatarMode() { this.executeAction("toggle_mode"); },

  onSnackChange(e) {
    this.setData({ selectedSnackIndex: e.detail.value });
  },

  handleFeedAction() {
    const raw = this.data.snackOptions[this.data.selectedSnackIndex];
    const snackName = raw.split(" ")[1] || "草莓大福";
    this.executeAction("feed", snackName);
  },

  // 3. 蓝牙开关切换
  handleToggleBle() {
    if (this.data.isBleMode) {
      this.buddyService.disconnectBLE();
      wx.showToast({ title: "已断开蓝牙", icon: "none" });
      return;
    }

    wx.showLoading({ title: "正在搜索灵宠..." });
    this.buddyService.bleClient.startScan((device) => {
      wx.hideLoading();
      this.buddyService.connectBLE(device.deviceId).then(() => {
        haptics.notification();
        wx.showToast({ title: "已连接 StickS3", icon: "success" });
      }).catch(() => {
        wx.showToast({ title: "连接握手失败", icon: "none" });
      });
    }, () => {
      wx.hideLoading();
      wx.showToast({ title: "请开启手机蓝牙", icon: "none" });
    });
  },

  // 4. Wi-Fi 开关切换
  handleToggleWifi() {
    if (this.data.isWifiMode) {
      this.buddyService.disconnectWifi();
      wx.showToast({ title: "已断开 Wi-Fi", icon: "none" });
      return;
    }

    const host = this.buddyService.httpClient.host;
    wx.showModal({
      title: "连接 StickS3 局域网",
      content: `目标设备 IP: ${host}，确认连接？`,
      confirmText: "连接",
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: "正在连入局域网..." });
          this.buddyService.connectWifi(host).then(() => {
            wx.hideLoading();
            haptics.notification();
            wx.showToast({ title: "Wi-Fi 直连成功", icon: "success" });
          }).catch(() => {
            wx.hideLoading();
            wx.showModal({
              title: "连接失败",
              content: `无法访问 ${host}，请确保手机与 StickS3 处于相同 Wi-Fi。可在“设备设置”中修改目标 IP。`,
              showCancel: false
            });
          });
        }
      }
    });
  },

  // 5. 仿真模式切换
  handleToggleSim() {
    const isSim = this.buddyService.toggleSim();
    haptics.vibrate("light");
    wx.showToast({ title: isSim ? "进入演示仿真模式" : "退出演示模式", icon: "none" });
  },

  // 6. 3D 姿态与关节动力学处理
  handleYawChange(e) {
    const yaw = Number(e.detail.value) || 0;
    this.setData({ bearYaw: yaw });
    this.buddyService.setBearYaw(yaw);
  },

  handleTurn180() {
    this.buddyService.triggerBearTurn(180);
    this.setData({ bearYaw: 180 });
    wx.showToast({ title: "小熊转身秀尾巴~", icon: "none" });
  },

  handleSpin360() {
    this.buddyService.triggerBearSpin();
    wx.showToast({ title: "360° 芭蕾自旋！", icon: "none" });
  },

  handleToggleImuBalance(e) {
    const en = Boolean(e.detail.value);
    this.setData({ imuBalanceEnabled: en });
    this.buddyService.setImuBalance(en);
    wx.showToast({ title: en ? "重力平衡已开启" : "重力平衡已关闭", icon: "none" });
  },

  handleJointSelect(e) {
    const idx = Number(e.detail.value) || 0;
    this.setData({ selectedJointIndex: idx, selectedJointAngle: 0 });
  },

  handleJointAngleChange(e) {
    const ang = Number(e.detail.value) || 0;
    this.setData({ selectedJointAngle: ang });
    const jId = this.data.jointList[this.data.selectedJointIndex].id;
    this.buddyService.setBearJoint(jId, ang);
  },

  handleClearJoints() {
    this.setData({ selectedJointAngle: 0 });
    this.buddyService.clearBearJoints();
    wx.showToast({ title: "全身姿态已复位", icon: "none" });
  },

  // Tab 页面跳转导航
  navigateToFeed() {
    wx.switchTab({ url: "/pages/feed/feed" });
  },

  navigateToDiary() {
    wx.switchTab({ url: "/pages/diary/diary" });
  },

  navigateToDialogueHistory() {
    buddyService.diaryTargetTab = "dialogue";
    wx.switchTab({ url: "/pages/diary/diary" });
  },

  navigateToSettings() {
    wx.switchTab({ url: "/pages/settings/settings" });
  }
});
