/**
 * wechat_miniprogram/utils/buddy_service.js
 * -----------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序跨页面统一伴侣中枢服务 (Single Source of Truth)
 * - 维护跨页面常驻 BLE / Wi-Fi 连接态与灵宠状态树
 * - 集中处理 20 字节安全 MTU 分片、触觉震动分发与离线存储同步
 * - 支持各页面 (主页 / 投喂屋 / 日记本 / 设置) 订阅响应式状态变迁
 */

const { StickS3BLEClient } = require("./sticks3_ble.js");
const { StickS3HttpClient } = require("./sticks3_wifi.js");
const { StorageManager } = require("./storage_manager.js");
const { haptics } = require("./haptics.js");

class BuddyService {
  constructor() {
    this.bleClient = new StickS3BLEClient();
    this.httpClient = new StickS3HttpClient();

    // 默认或从本地存储恢复设置与状态
    const savedSettings = StorageManager.getSettings();
    haptics.setEnabled(savedSettings.vibrationEnabled);
    this.httpClient.setHost(savedSettings.wifiHost || "192.168.110.67");

    this.petState = StorageManager.getPetState();
    this.memoryTurns = StorageManager.getMemories();
    this.diaries = StorageManager.getDiaries();

    // 手机共享热点与流量配额状态
    this.hotspot = {
      isHotspot: Boolean(savedSettings.isHotspot),
      usedMb: 0,
      limitMb: Number(savedSettings.hotspotLimitMb) || 100,
      remainingMb: Number(savedSettings.hotspotLimitMb) || 100,
      cutoffActive: false,
      cutoffEnabled: savedSettings.hotspotCutoffEnabled !== false,
      warningIssued: false
    };

    this.isConnected = false;
    this.isBleMode = false;
    this.isWifiMode = false;
    this.isSimMode = false;
    this.connectionStatusText = "未连接伴侣";

    this.wifiPollTimer = null;
    this.listeners = [];

    this._setupBleHandlers();
  }

  _setupBleHandlers() {
    this.bleClient.onStatusUpdate = (st) => {
      this.updatePetState(st);
    };

    this.bleClient.onDiaryReceived = (diary) => {
      this.handleIncomingDiary(diary, "BLE 推送");
    };

    this.bleClient.onMemoryReceived = (mems) => {
      if (Array.isArray(mems)) {
        this.memoryTurns = mems;
        StorageManager.saveMemories(mems);
        this.notifyListeners("memory", mems);
      }
    };

    this.bleClient.onConnectionChange = (connected) => {
      this.isConnected = connected;
      this.isBleMode = connected;
      this.connectionStatusText = connected ? "BLE 在线" : "BLE 已断开";
      this.notifyListeners("connection", {
        isConnected: this.isConnected,
        isBleMode: this.isBleMode,
        isWifiMode: this.isWifiMode,
        isSimMode: this.isSimMode,
        statusText: this.connectionStatusText
      });
    };
  }

  // 状态订阅器
  subscribe(fn) {
    if (typeof fn === "function" && !this.listeners.includes(fn)) {
      this.listeners.push(fn);
      // 立即触发一次当前状态
      fn({
        type: "init",
        petState: this.petState,
        hotspot: this.hotspot,
        isConnected: this.isConnected,
        isBleMode: this.isBleMode,
        isWifiMode: this.isWifiMode,
        isSimMode: this.isSimMode,
        connectionStatusText: this.connectionStatusText
      });
    }
  }

  unsubscribe(fn) {
    this.listeners = this.listeners.filter(l => l !== fn);
  }

  notifyListeners(type, data) {
    this.listeners.forEach(fn => {
      try {
        fn({
          type,
          data,
          petState: this.petState,
          hotspot: this.hotspot,
          isConnected: this.isConnected,
          isBleMode: this.isBleMode,
          isWifiMode: this.isWifiMode,
          isSimMode: this.isSimMode,
          connectionStatusText: this.connectionStatusText
        });
      } catch (e) {
        console.error("[BuddyService] listener error:", e);
      }
    });
  }

  // 灵宠状态快照更新
  updatePetState(st) {
    if (!st) return;
    const cur = { ...this.petState };
    if (st.name) cur.name = st.name;
    if (st.level !== undefined) cur.level = st.level;
    if (st.xp !== undefined) cur.xp = st.xp;
    if (st.energy !== undefined) cur.energy = st.energy;
    if (st.mood !== undefined) cur.mood = st.mood;
    if (st.mood_id !== undefined) cur.mood = st.mood_id;
    if (st.feeds !== undefined) cur.feeds = st.feeds;
    if (st.grooms !== undefined) cur.grooms = st.grooms;
    if (st.pets !== undefined) cur.pets = st.pets;
    if (st.shakes !== undefined) cur.shakes = st.shakes;
    if (st.diary) cur.diary = st.diary;

    // 同步热点遥测指标
    let hotspotChanged = false;
    if (st.is_hotspot !== undefined) {
      this.hotspot.isHotspot = Boolean(st.is_hotspot);
      hotspotChanged = true;
    }
    if (st.hs_used_mb !== undefined) {
      this.hotspot.usedMb = Number(st.hs_used_mb);
      hotspotChanged = true;
    }
    if (st.hs_limit_mb !== undefined) {
      this.hotspot.limitMb = Number(st.hs_limit_mb);
      hotspotChanged = true;
    }
    if (st.hs_cutoff !== undefined) {
      this.hotspot.cutoffActive = Boolean(st.hs_cutoff);
      hotspotChanged = true;
    }
    if (hotspotChanged) {
      this.hotspot.remainingMb = Math.max(0, parseFloat((this.hotspot.limitMb - this.hotspot.usedMb).toFixed(2)));
    }

    this.petState = cur;
    StorageManager.savePetState(cur);
    this.notifyListeners("state", this.petState);
    if (hotspotChanged) {
      this.notifyListeners("hotspot", this.hotspot);
    }
  }

  // 接收并沉淀新日记
  handleIncomingDiary(diaryText, tag = "📖 心声") {
    if (!diaryText) return;
    haptics.notification();
    this.petState.diary = diaryText;
    const entry = StorageManager.saveDiaryEntry(diaryText, this.petState.mood, tag);
    this.diaries = StorageManager.getDiaries();
    this.notifyListeners("diary", { entry, diaries: this.diaries, latest: diaryText });
  }

  // 动作下发主路由
  async dispatchAction(action, value = "") {
    // 触发触觉反馈
    switch (action) {
      case "feed":  haptics.feed(); break;
      case "pet":   haptics.pet(); break;
      case "groom": haptics.groom(); break;
      case "play":  haptics.play(); break;
      default:      haptics.vibrate("medium"); break;
    }

    // 1. BLE 模式
    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction(action, value);
        return { success: true, mode: "ble" };
      } catch (e) {
        console.error("[BuddyService] BLE action error:", e);
        throw e;
      }
    }

    // 2. Wi-Fi 模式
    if (this.isWifiMode) {
      try {
        const res = await this.httpClient.sendPetAction(action, value);
        this.updatePetState(res);
        if (res.diary) {
          this.handleIncomingDiary(res.diary, this.getActionMoodTag(action));
        }
        return { success: true, mode: "wifi", data: res };
      } catch (e) {
        console.error("[BuddyService] Wi-Fi action error:", e);
        throw e;
      }
    }

    // 3. 本地仿真模式 (离线或无硬件演示)
    return this._runLocalSimAction(action, value);
  }

  _runLocalSimAction(action, value) {
    const st = { ...this.petState };
    let diaryContent = "";
    let moodTag = "📖 互动";

    if (action === "feed") {
      st.mood = 10; // MOOD_EAT
      st.feeds += 1;
      st.energy = Math.min(100, st.energy + 20);
      st.xp += 10;
      moodTag = "🍰 美食";
      diaryContent = `主人喂我吃了一块${value || "草莓大福"}，吧唧吧唧超级满足，活力满满！`;
      setTimeout(() => { if (this.petState.mood === 10) this.setMood(0); }, 3000);
    } else if (action === "groom") {
      st.mood = 11; // MOOD_GROOM
      st.grooms += 1;
      st.xp += 12;
      moodTag = "✨ 梳毛";
      diaryContent = "主人用小梳子温柔地帮我梳理毛发，整只宠都舒服得想呼噜呼噜~";
      setTimeout(() => { if (this.petState.mood === 11) this.setMood(0); }, 3000);
    } else if (action === "play") {
      st.mood = 12; // MOOD_WINK
      st.xp += 15;
      st.energy = Math.max(10, st.energy - 10);
      moodTag = "✋ 击掌";
      diaryContent = "和主人默契击掌！小虎牙笑得合不拢嘴，我们也是元气满满的搭档！";
      setTimeout(() => { if (this.petState.mood === 12) this.setMood(0); }, 3000);
    } else if (action === "pet") {
      st.mood = 4; // MOOD_HAPPY
      st.pets += 1;
      st.xp += 5;
      moodTag = "🌸 抚摸";
      diaryContent = "主人刚刚隔空温柔地摸了摸我，感觉心底暖洋洋的~";
      setTimeout(() => { if (this.petState.mood === 4) this.setMood(0); }, 2800);
    } else if (action === "shake") {
      st.mood = 5; // MOOD_DIZZY
      st.shakes += 1;
      moodTag = "🌀 调皮";
      diaryContent = "哎呀呀，调皮晃动让我脑袋转圈圈，眼睛里冒出好多小金星！";
      setTimeout(() => { if (this.petState.mood === 5) this.setMood(0); }, 3500);
    } else if (action === "sleep") {
      st.mood = 7; // MOOD_SLEEP
      moodTag = "🌙 晚安";
      diaryContent = "呼噜呼噜~ 灵宠进入梦乡打呼噜啦，晚安哦。";
    } else if (action === "wake") {
      st.mood = 1; // MOOD_LISTEN
      diaryContent = "小木揉揉眼睛苏醒啦！今天也要元气满满哦！";
    }

    // 等级成长与突破
    if (st.xp >= 100 && st.level < 10) {
      st.level += 1;
      st.xp = st.xp - 100;
      diaryContent = `太棒啦！我和主人的羁绊提升到了 Lv.${st.level}，解锁了更多陪伴默契！`;
      haptics.levelUp();
    }

    st.diary = diaryContent;
    this.updatePetState(st);
    if (diaryContent) {
      this.handleIncomingDiary(diaryContent, moodTag);
    }

    return { success: true, mode: "sim" };
  }

  getActionMoodTag(action) {
    const map = {
      feed: "🍰 美食",
      groom: "✨ 梳毛",
      play: "✋ 击掌",
      pet: "🌸 抚摸",
      shake: "🌀 调皮",
      sleep: "🌙 晚安"
    };
    return map[action] || "📖 互动";
  }

  setMood(mood) {
    this.petState.mood = mood;
    this.notifyListeners("state", this.petState);
  }

  // --- 连接管理 ---

  async connectBLE(deviceId, name = "") {
    this.connectedDeviceName = name || "StickS3-Buddy";
    return new Promise((resolve, reject) => {
      this.bleClient.connect(deviceId, () => {
        this.isConnected = true;
        this.isBleMode = true;
        this.isWifiMode = false;
        this.isSimMode = false;
        this.connectionStatusText = "BLE 在线";
        this.notifyListeners("connection", {
          isConnected: true,
          isBleMode: true,
          statusText: "BLE 在线",
          deviceName: this.connectedDeviceName
        });
        resolve();
      }, reject);
    });
  }

  disconnectBLE() {
    this.bleClient.disconnect();
    this.isConnected = false;
    this.isBleMode = false;
    this.connectionStatusText = "未连接伴侣";
    this.notifyListeners("connection", {
      isConnected: false,
      isBleMode: false,
      statusText: "未连接伴侣"
    });
  }

  async connectWifi(host) {
    if (host) this.httpClient.setHost(host);
    const st = await this.httpClient.getPetStatus();
    this.updatePetState(st);

    this.isConnected = true;
    this.isWifiMode = true;
    this.isBleMode = false;
    this.isSimMode = false;
    this.connectionStatusText = "Wi-Fi 在线";

    if (this.wifiPollTimer) clearInterval(this.wifiPollTimer);
    this.wifiPollTimer = setInterval(async () => {
      try {
        const live = await this.httpClient.getPetStatus();
        this.updatePetState(live);
      } catch (e) {}
    }, 2000);

    this.notifyListeners("connection", {
      isConnected: true,
      isWifiMode: true,
      statusText: "Wi-Fi 在线"
    });
    return st;
  }

  disconnectWifi() {
    if (this.wifiPollTimer) clearInterval(this.wifiPollTimer);
    this.isConnected = false;
    this.isWifiMode = false;
    this.connectionStatusText = "未连接伴侣";
    this.notifyListeners("connection", {
      isConnected: false,
      isWifiMode: false,
      statusText: "未连接伴侣"
    });
  }

  toggleSim() {
    this.isSimMode = !this.isSimMode;
    this.isConnected = this.isSimMode;
    if (this.isSimMode) {
      this.isBleMode = false;
      this.isWifiMode = false;
      this.connectionStatusText = "演示仿真";
    } else {
      this.connectionStatusText = "未连接伴侣";
    }
    this.notifyListeners("connection", {
      isConnected: this.isConnected,
      isSimMode: this.isSimMode,
      statusText: this.connectionStatusText
    });
    return this.isSimMode;
  }

  // --- Wi-Fi / 手机热点智能配网 (Smart Wi-Fi / Mobile Hotspot Provisioning via 0xFFB4 20-byte safe chunks or HTTP) ---
  async provisionWifi(arg1, arg2, arg3 = {}) {
    let ssid = "";
    let password = "";
    let isHotspot = false;
    let dataLimitMb = 100;
    let cutoffEnabled = true;

    if (typeof arg1 === "object" && arg1 !== null) {
      ssid = arg1.ssid || "";
      password = arg1.password || arg1.pwd || "";
      isHotspot = Boolean(arg1.isHotspot);
      dataLimitMb = Number(arg1.dataLimitMb !== undefined ? arg1.dataLimitMb : (arg1.limitMb || 100));
      cutoffEnabled = arg1.cutoffEnabled !== undefined ? Boolean(arg1.cutoffEnabled) : true;
    } else {
      ssid = arg1 || "";
      password = arg2 || "";
      isHotspot = Boolean(arg3.isHotspot);
      dataLimitMb = Number(arg3.dataLimitMb !== undefined ? arg3.dataLimitMb : 100);
      cutoffEnabled = arg3.cutoffEnabled !== undefined ? Boolean(arg3.cutoffEnabled) : true;
    }

    if (!ssid || ssid.trim().length === 0) {
      throw new Error("SSID 不能为空");
    }

    // 更新本地 settings 存储
    const currentSettings = StorageManager.getSettings();
    currentSettings.wifiSsid = ssid;
    currentSettings.isHotspot = isHotspot;
    currentSettings.hotspotLimitMb = dataLimitMb;
    currentSettings.hotspotCutoffEnabled = cutoffEnabled;
    StorageManager.saveSettings(currentSettings);

    this.hotspot.isHotspot = isHotspot;
    this.hotspot.limitMb = dataLimitMb;
    this.hotspot.cutoffEnabled = cutoffEnabled;
    this.hotspot.remainingMb = Math.max(0, parseFloat((this.hotspot.limitMb - this.hotspot.usedMb).toFixed(2)));

    // 1. 若 BLE 已连接，采用 20 字节安全 MTU 分片写入到 0xFFB4
    if (this.isBleMode && this.bleClient.isConnected) {
      const payload = {
        action: "wifi_cfg",
        cmd: "wifi_cfg",
        ssid: ssid,
        pwd: password,
        is_hotspot: isHotspot,
        data_limit_mb: dataLimitMb,
        cutoff_enabled: cutoffEnabled
      };
      await this.bleClient.injectAction("wifi_cfg", JSON.stringify(payload));
      this.notifyListeners("hotspot", this.hotspot);
      return { status: "provisioned", mode: "ble", ssid, isHotspot, dataLimitMb };
    }

    // 2. 若 Wi-Fi 模式在线，通过 RESTful API 下发
    if (this.isWifiMode) {
      const res = await this.httpClient.connectWifiNetwork({
        ssid,
        password,
        isHotspot,
        limitMb: dataLimitMb,
        cutoff: cutoffEnabled
      });
      this.notifyListeners("hotspot", this.hotspot);
      return { status: "provisioned", mode: "wifi", data: res, ssid, isHotspot, dataLimitMb };
    }

    // 3. 仿真演示模式
    if (this.isSimMode) {
      this.handleIncomingDiary(`[仿真配网] 成功配置 ${isHotspot ? "手机移动热点" : "Wi-Fi网络"}: ${ssid}，流量上限 ${dataLimitMb}MB`, "📶 网络");
      this.notifyListeners("hotspot", this.hotspot);
      return { status: "provisioned", mode: "sim", ssid, isHotspot, dataLimitMb };
    }

    throw new Error("请先通过 BLE 蓝牙或 Wi-Fi 连接 StickS3 设备后再执行配网");
  }

  // --- 手机热点流量配额与熔断策略在线配置 ---
  async updateHotspotConfig({ isHotspot = true, dataLimitMb, cutoffEnabled }) {
    if (dataLimitMb !== undefined) this.hotspot.limitMb = Number(dataLimitMb);
    if (isHotspot !== undefined) this.hotspot.isHotspot = Boolean(isHotspot);
    if (cutoffEnabled !== undefined) this.hotspot.cutoffEnabled = Boolean(cutoffEnabled);
    this.hotspot.remainingMb = Math.max(0, parseFloat((this.hotspot.limitMb - this.hotspot.usedMb).toFixed(2)));

    const currentSettings = StorageManager.getSettings();
    currentSettings.isHotspot = this.hotspot.isHotspot;
    currentSettings.hotspotLimitMb = this.hotspot.limitMb;
    currentSettings.hotspotCutoffEnabled = this.hotspot.cutoffEnabled;
    StorageManager.saveSettings(currentSettings);

    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("hotspot_cfg", JSON.stringify({
        action: "hotspot_cfg",
        is_hotspot: this.hotspot.isHotspot,
        data_limit_mb: this.hotspot.limitMb,
        cutoff_enabled: this.hotspot.cutoffEnabled
      }));
    } else if (this.isWifiMode) {
      await this.httpClient.setHotspotConfig({
        isHotspot: this.hotspot.isHotspot,
        limitMb: this.hotspot.limitMb,
        cutoff: this.hotspot.cutoffEnabled
      });
    }

    this.notifyListeners("hotspot", this.hotspot);
    return { success: true, hotspot: this.hotspot };
  }

  // --- 重置手机热点流量统计计数器 ---
  async resetHotspotTraffic() {
    this.hotspot.usedMb = 0;
    this.hotspot.remainingMb = this.hotspot.limitMb;
    this.hotspot.cutoffActive = false;
    this.hotspot.warningIssued = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("reset_traffic", JSON.stringify({ action: "reset_traffic" }));
    } else if (this.isWifiMode) {
      await this.httpClient.resetHotspotTraffic();
    }

    this.notifyListeners("hotspot", this.hotspot);
    return { success: true, hotspot: this.hotspot };
  }

  // --- 查询热点流量实时数据 (针对 Wi-Fi 在线模式主动轮询) ---
  async fetchHotspotTraffic() {
    if (this.isWifiMode) {
      try {
        const data = await this.httpClient.getHotspotTraffic();
        if (data) {
          if (data.is_hotspot !== undefined) this.hotspot.isHotspot = Boolean(data.is_hotspot);
          if (data.used_mb !== undefined) this.hotspot.usedMb = Number(data.used_mb);
          if (data.limit_mb !== undefined) this.hotspot.limitMb = Number(data.limit_mb);
          if (data.remaining_mb !== undefined) this.hotspot.remainingMb = Number(data.remaining_mb);
          if (data.cutoff_active !== undefined) this.hotspot.cutoffActive = Boolean(data.cutoff_active);
          if (data.cutoff_enabled !== undefined) this.hotspot.cutoffEnabled = Boolean(data.cutoff_enabled);
          if (data.warning_issued !== undefined) this.hotspot.warningIssued = Boolean(data.warning_issued);
          this.notifyListeners("hotspot", this.hotspot);
        }
      } catch (e) {
        console.warn("[BuddyService] fetchHotspotTraffic error:", e);
      }
    }
    return this.hotspot;
  }

  // --- 历史人机对话多轮记忆同步与管理 ---
  async syncMemories() {
    if (this.isWifiMode) {
      try {
        const mems = await this.httpClient.getMemories();
        if (Array.isArray(mems) && mems.length > 0) {
          this.memoryTurns = mems;
          StorageManager.saveMemories(mems);
          this.notifyListeners("memory", mems);
          return mems;
        }
      } catch (e) {
        console.warn("[BuddyService] syncMemories HTTP error:", e);
      }
    }
    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("sync_memory", "");
    }
    const local = StorageManager.getMemories();
    this.memoryTurns = local;
    return local;
  }

  clearMemories() {
    this.memoryTurns = [];
    StorageManager.saveMemories([]);
    this.notifyListeners("memory", []);
  }
}

// 单例模式全局服务
const buddyService = new BuddyService();

module.exports = {
  BuddyService,
  buddyService
};
