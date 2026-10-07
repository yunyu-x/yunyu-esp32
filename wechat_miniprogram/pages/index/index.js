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
    selectedJointAngle: 0,

    // 多体编队舞团状态
    isSwarmDancing: false,
    currentDanceTheme: "",

    // 17 套迪士尼影院级动作姿态点播与阅兵系统
    cinematicActions: [
      { id: 1,  act: "wave",          name: "元气挥手",     category: "萌初幼熊", minLvl: 1, icon: "👋", desc: "圆弧挥舞·侧首微偏" },
      { id: 2,  act: "bow",           name: "作揖鞠躬",     category: "萌初幼熊", minLvl: 1, icon: "🙇", desc: "前倾抱拳·行云流水" },
      { id: 3,  act: "sit",           name: "呆萌坐下",     category: "萌初幼熊", minLvl: 1, icon: "🧘", desc: "双腿外八·露出肉垫" },
      { id: 4,  act: "stretch",       name: "伸大懒腰",     category: "萌初幼熊", minLvl: 1, icon: "🙆", desc: "仰天高举·纵向拉伸" },
      { id: 5,  act: "clap",          name: "鼓掌拍手",     category: "灵趣欢腾", minLvl: 2, icon: "👏", desc: "对掌拍击·金星飞溅" },
      { id: 6,  act: "cheer",         name: "欢呼雀跃",     category: "灵趣欢腾", minLvl: 2, icon: "🎉", desc: "双手V举·欢欣鼓舞" },
      { id: 7,  act: "jump",          name: "弹性跳跃",     category: "灵趣欢腾", minLvl: 2, icon: "🦘", desc: "下蹲蓄力·果冻回弹" },
      { id: 8,  act: "dance",         name: "律动跳舞",     category: "律动体能", minLvl: 3, icon: "🕺", desc: "摇摆节拍·左右摆臀" },
      { id: 9,  act: "balance",       name: "金鸡独立",     category: "律动体能", minLvl: 3, icon: "🦩", desc: "单脚伫立·大鹏展翅" },
      { id: 10, act: "lie",           name: "趴地休息",     category: "律动体能", minLvl: 3, icon: "🛌", desc: "平趴地面·四肢舒展" },
      { id: 11, act: "pushup",        name: "俯卧撑",       category: "律动体能", minLvl: 3, icon: "💪", desc: "伏地推起·大屈双臂" },
      { id: 12, act: "kungfu",        name: "中国功夫",     category: "东方功夫", minLvl: 4, icon: "🥋", desc: "深蹲马步·右前推掌" },
      { id: 13, act: "taichi",        name: "太极云手",     category: "东方功夫", minLvl: 4, icon: "☯️", desc: "圆周运化·行云流水" },
      { id: 14, act: "wingchun",      name: "咏春快拳",     category: "东方功夫", minLvl: 4, icon: "🥊", desc: "日字连打·身躯反扭" },
      { id: 15, act: "dragon_punch",  name: "升龙霸天",     category: "机甲元尊", minLvl: 5, icon: "🐉", desc: "蓄力前摇·冲霄暴扣" },
      { id: 16, act: "moonwalk",      name: "太空漫步",     category: "机甲元尊", minLvl: 5, icon: "👟", desc: "滑步后撤·身躯前倾" },
      { id: 17, act: "cyber_defense", name: "机甲护盾",     category: "机甲元尊", minLvl: 5, icon: "🛡️", desc: "交叉双臂·能量力场" },
      { id: 18, act: "turn_around",   name: "转身秀尾",     category: "空间特技", minLvl: 2, icon: "🔄", desc: "180°转身·露小尾巴" },
      { id: 19, act: "spin",          name: "华丽自旋",     category: "空间特技", minLvl: 3, icon: "🩰", desc: "360°自旋·平衡平举" },
      { id: 20, act: "locked_try",    name: "困惑挠头",     category: "空间特技", minLvl: 1, icon: "🤔", desc: "右爪抓耳·萌态歪头" }
    ],
    currentActionAct: "idle",
    isDemoShowcaseActive: false
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

  // 7. 灵宠与灵方多体舞团编队控制
  handleTriggerSwarmDance(e) {
    const theme = (e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.theme) || "waltz";
    const themeNames = {
      waltz: "元气华尔兹",
      zen: "太极云手阵",
      moonwalk: "太空漫步秀",
      cyber: "机甲破晓舞"
    };
    const title = themeNames[theme] || "元气舞曲";
    this.setData({ isSwarmDancing: true, currentDanceTheme: theme });
    this.buddyService.triggerSwarmDance(theme);
    wx.showToast({ title: `🎭 启动舞曲: ${title}`, icon: "none" });
    setTimeout(() => {
      this.setData({ isSwarmDancing: false });
    }, 4500);
  },

  // 8. 技能解锁全屏庆典特技
  handleTriggerCeremony() {
    this.buddyService.triggerCeremony(0);
    wx.showToast({ title: "★ 触发技能解锁盛典!", icon: "none" });
  },

  // 9. 17 套迪士尼影院级动作姿态直接点播与阅兵
  handleSelectBearAction(e) {
    const act = (e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.act) || "wave";
    const minLvl = Number(e.currentTarget.dataset.minlvl) || 1;
    const curLvl = Number(this.data.petState.level) || 1;
    if (curLvl < minLvl) {
      haptics.vibrate("medium");
      wx.showModal({
        title: "动作尚未解锁",
        content: `该动作需要小熊达到 Lv.${minLvl} 解锁，当前为 Lv.${curLvl}。多与小熊互动对话可获得成长经验！`,
        showCancel: false
      });
      this.buddyService.triggerBearAction("locked_try");
      return;
    }
    this.setData({ currentActionAct: act });
    this.buddyService.triggerBearAction(act);
    const item = this.data.cinematicActions.find(a => a.act === act);
    wx.showToast({ title: `🎬 施展: ${item ? item.name : act}`, icon: "none" });
  },

  handleToggleDemoShowcase() {
    const nextState = !this.data.isDemoShowcaseActive;
    this.setData({ isDemoShowcaseActive: nextState });
    this.buddyService.triggerDemoShowcase(nextState);
    wx.showToast({ title: nextState ? "🎬 开启全套姿态自动巡礼" : "⏹ 已停止自动阅兵", icon: "none" });
  },

  handleNextPose() {
    this.buddyService.triggerNextPose();
    wx.showToast({ title: "⏭ 切换至下一个动作姿态", icon: "none" });
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
