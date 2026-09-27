// pages/index/index.js
const { StickS3BLEClient } = require("../../utils/sticks3_ble.js");
const { StickS3HttpClient } = require("../../utils/sticks3_wifi.js");
const { AvatarRenderer } = require("../../utils/avatar_renderer.js");
const { CryptoGuard } = require("../../utils/crypto_guard.js");

Page({
  data: {
    isConnected: false,
    connectionStatusText: "未连接伴侣",
    isBleMode: false,
    isWifiMode: false,
    isSimMode: false,

    bleBtnText: "蓝牙连接",
    wifiBtnText: "Wi-Fi 局域网",
    simBtnText: "演示仿真",

    petState: {
      name: "小木",
      level: 1,
      xp: 15,
      energy: 100,
      mood: 0,
      feeds: 0,
      grooms: 0,
      pets: 0,
      shakes: 0,
      diary: "今天刚刚苏醒，期待和主人一起探索世界！"
    },

    snackOptions: [
      "🍓 草莓奶油大福 (+20活力, +10羁绊)",
      "🍰 鲜奶舒芙蕾蛋糕 (+20活力, +10羁绊)",
      "🍪 比利时巧脆曲奇 (+20活力, +10羁绊)",
      "🍩 彩虹熔岩甜甜圈 (+20活力, +10羁绊)",
      "🍿 香甜爆米花 (+20活力, +10羁绊)"
    ],
    selectedSnackIndex: 0,

    memoryTurns: [
      { user: "你好小木，今天天气怎么样？", ai: "今天阳光明媚，微风正好，最适合我们一起去散步啦！" }
    ]
  },

  onLoad() {
    this.bleClient = new StickS3BLEClient();
    this.httpClient = new StickS3HttpClient("192.168.110.67");
    this.avatarRenderer = new AvatarRenderer();
    this.wifiTimer = null;

    // 绑定 BLE 事件
    this.bleClient.onStatusUpdate = (st) => this.onBleStatusUpdate(st);
    this.bleClient.onDiaryReceived = (diary) => this.onBleDiaryReceived(diary);
    this.bleClient.onMemoryReceived = (mems) => this.onBleMemoryReceived(mems);
    this.bleClient.onConnectionChange = (connected) => {
      this.setData({
        isConnected: connected,
        isBleMode: connected,
        connectionStatusText: connected ? "BLE 在线" : "BLE 已断开",
        bleBtnText: connected ? "断开蓝牙" : "蓝牙连接"
      });
    };
  },

  onReady() {
    // 初始化 Canvas 2D 迪士尼灵动微表情渲染画布
    const query = wx.createSelectorQuery();
    query.select('#avatarCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res[0] || !res[0].node) return;
        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');
        const dpr = wx.getSystemInfoSync().pixelRatio;

        canvas.width = res[0].width * dpr;
        canvas.height = res[0].height * dpr;
        ctx.scale(dpr, dpr);

        this.canvas = canvas;
        this.ctx = ctx;
        this.canvasWidth = res[0].width;
        this.canvasHeight = res[0].height;

        this.startAvatarLoop();
      });
  },

  onUnload() {
    if (this.bleClient) this.bleClient.disconnect();
    if (this.wifiTimer) clearInterval(this.wifiTimer);
  },

  startAvatarLoop() {
    const loop = () => {
      if (this.ctx && this.canvas) {
        this.avatarRenderer.render(this.ctx, this.canvasWidth, this.canvasHeight, this.data.petState);
      }
      if (this.canvas && this.canvas.requestAnimationFrame) {
        this.canvas.requestAnimationFrame(loop);
      } else {
        setTimeout(loop, 33); // 30 FPS fallback
      }
    };
    loop();
  },

  // 1. 蓝牙连接切换
  handleToggleBle() {
    if (this.data.isBleMode) {
      this.bleClient.disconnect();
      this.setData({
        isConnected: false,
        isBleMode: false,
        connectionStatusText: "未连接伴侣",
        bleBtnText: "蓝牙连接"
      });
      wx.showToast({ title: "已断开蓝牙", icon: "none" });
      return;
    }

    wx.showLoading({ title: "正在搜索灵宠..." });
    this.bleClient.startScan((device) => {
      wx.hideLoading();
      this.bleClient.connect(device.deviceId, () => {
        wx.showToast({ title: "已连接 StickS3", icon: "success" });
        this.setData({
          isConnected: true,
          isBleMode: true,
          isWifiMode: false,
          isSimMode: false,
          connectionStatusText: "BLE 在线",
          bleBtnText: "断开蓝牙"
        });
      }, (err) => {
        wx.showToast({ title: "连接失败", icon: "none" });
      });
    }, (err) => {
      wx.hideLoading();
      wx.showToast({ title: "请开启手机蓝牙", icon: "none" });
    });
  },

  // 2. Wi-Fi 局域网连接切换
  handleToggleWifi() {
    if (this.data.isWifiMode) {
      if (this.wifiTimer) clearInterval(this.wifiTimer);
      this.setData({
        isConnected: false,
        isWifiMode: false,
        connectionStatusText: "未连接伴侣",
        wifiBtnText: "Wi-Fi 局域网"
      });
      wx.showToast({ title: "已断开 Wi-Fi", icon: "none" });
      return;
    }

    wx.showModal({
      title: "连接 StickS3 局域网",
      content: "当前默认目标 IP: 192.168.110.67，确认直连？",
      confirmText: "连接",
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: "正在连入局域网..." });
          this.httpClient.getPetStatus().then(st => {
            wx.hideLoading();
            this.updatePetState(st);
            this.setData({
              isConnected: true,
              isWifiMode: true,
              isBleMode: false,
              isSimMode: false,
              connectionStatusText: "Wi-Fi 在线",
              wifiBtnText: "断开 Wi-Fi"
            });
            wx.showToast({ title: "Wi-Fi 直连成功", icon: "success" });

            if (this.wifiTimer) clearInterval(this.wifiTimer);
            this.wifiTimer = setInterval(() => {
              this.httpClient.getPetStatus().then(d => this.updatePetState(d)).catch(()=>{});
            }, 1500);
          }).catch(err => {
            wx.hideLoading();
            wx.showModal({
              title: "连接失败",
              content: "无法访问 192.168.110.67，请确保手机与 StickS3 处于相同 Wi-Fi 或已开启微信局域网权限。",
              showCancel: false
            });
          });
        }
      }
    });
  },

  // 3. 仿真模式
  handleToggleSim() {
    const nextSim = !this.data.isSimMode;
    this.setData({
      isSimMode: nextSim,
      isConnected: nextSim,
      connectionStatusText: nextSim ? "演示仿真" : "未连接伴侣",
      simBtnText: nextSim ? "退出仿真" : "演示仿真"
    });
    wx.showToast({ title: nextSim ? "进入演示仿真模式" : "退出仿真", icon: "none" });
  },

  // 动作下发总路由 (附带微信触觉震动反馈)
  executeAction(action, value = "") {
    // 触发微信触觉马达震动 (Embodied Haptic Feedback)
    wx.vibrateShort({ type: "medium" });

    // 1. BLE 模式下发
    if (this.data.isBleMode) {
      this.bleClient.injectAction(action, value).then(() => {
        wx.showToast({ title: `指令已下发: ${action}`, icon: "none" });
      }).catch(err => {
        console.error("BLE inject error:", err);
      });
      return;
    }

    // 2. Wi-Fi 模式下发
    if (this.data.isWifiMode) {
      this.httpClient.sendPetAction(action, value).then(res => {
        this.updatePetState(res);
        wx.showToast({ title: `互动成功: ${action}`, icon: "none" });
      }).catch(err => {
        console.error("Wi-Fi action error:", err);
      });
      return;
    }

    // 3. 本地仿真模式
    this.handleLocalSimAction(action, value);
  },

  handleLocalSimAction(action, value) {
    const st = { ...this.data.petState };
    if (action === "feed") {
      st.mood = 10; // MOOD_EAT
      st.feeds += 1;
      st.energy = Math.min(100, st.energy + 20);
      st.xp += 10;
      st.diary = `主人喂我吃了一块${value || "小点心"}，吧唧吧唧超级满足，活力满满！`;
      setTimeout(() => { if (this.data.petState.mood === 10) this.setMood(0); }, 2500);
    } else if (action === "groom") {
      st.mood = 11; // MOOD_GROOM
      st.grooms += 1;
      st.xp += 12;
      st.diary = "主人用小梳子温柔地帮我梳理毛发，整只宠都舒服得想呼噜呼噜~";
      setTimeout(() => { if (this.data.petState.mood === 11) this.setMood(0); }, 2800);
    } else if (action === "play") {
      st.mood = 12; // MOOD_WINK
      st.xp += 15;
      st.energy = Math.max(10, st.energy - 10);
      st.diary = "和主人默契击掌！今天我们也是元气满满的搭档！";
      setTimeout(() => { if (this.data.petState.mood === 12) this.setMood(0); }, 2500);
    } else if (action === "pet") {
      st.mood = 4; // MOOD_HAPPY
      st.pets += 1;
      st.xp += 5;
      st.diary = "主人刚刚隔空温柔地摸了摸我，感觉心底暖洋洋的~";
      setTimeout(() => { if (this.data.petState.mood === 4) this.setMood(0); }, 2800);
    } else if (action === "shake") {
      st.mood = 5; // MOOD_DIZZY
      st.shakes += 1;
      st.diary = "哎呀呀，调皮晃动让我脑袋转圈圈，眼睛里冒出好多小星星！";
      setTimeout(() => { if (this.data.petState.mood === 5) this.setMood(0); }, 3500);
    } else if (action === "sleep") {
      st.mood = 7; // MOOD_SLEEP
      st.diary = "呼噜呼噜~ 灵宠进入梦乡打呼噜啦，晚安哦。";
    }

    if (st.xp >= 100 && st.level < 10) {
      st.level += 1;
      st.xp = 0;
      st.diary = `太棒啦！我和主人的羁绊提升到了 Lv.${st.level}！`;
    }

    this.setData({ petState: st });
  },

  setMood(mood) {
    this.setData({ ['petState.mood']: mood });
  },

  onSnackChange(e) {
    this.setData({ selectedSnackIndex: e.detail.value });
  },

  handleFeedAction() {
    const raw = this.data.snackOptions[this.data.selectedSnackIndex];
    const snackName = raw.split(" ")[1] || "草莓大福";
    this.executeAction("feed", snackName);
  },

  handleGroomAction() { this.executeAction("groom"); },
  handlePlayAction() { this.executeAction("play"); },
  handlePetAction() { this.executeAction("pet"); },
  handleShakeAction() { this.executeAction("shake"); },
  handleSleepAction() { this.executeAction("sleep"); },
  handleToggleAvatarMode() { this.executeAction("toggle_mode"); },

  // 数据同步更新
  updatePetState(st) {
    if (!st) return;
    const cur = { ...this.data.petState };
    if (st.name) cur.name = st.name;
    if (st.level !== undefined) cur.level = st.level;
    if (st.xp !== undefined) cur.xp = st.xp;
    if (st.energy !== undefined) cur.energy = st.energy;
    if (st.mood_id !== undefined) cur.mood = st.mood_id;
    if (st.feeds !== undefined) cur.feeds = st.feeds;
    if (st.grooms !== undefined) cur.grooms = st.grooms;
    if (st.pets !== undefined) cur.pets = st.pets;
    if (st.shakes !== undefined) cur.shakes = st.shakes;
    if (st.diary) cur.diary = st.diary;
    this.setData({ petState: cur });
  },

  onBleStatusUpdate(st) { this.updatePetState(st); },
  onBleDiaryReceived(diary) { this.setData({ ['petState.diary']: diary }); },
  onBleMemoryReceived(mems) {
    if (Array.isArray(mems)) {
      this.setData({ memoryTurns: mems });
    }
  }
});
