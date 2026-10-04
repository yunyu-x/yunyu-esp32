/**
 * wechat_miniprogram/utils/buddy_service.js
 * -----------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序跨页面统一伴侣中枢服务 (Single Source of Truth)
 * - 维护跨页面常驻 BLE / Wi-Fi 连接态与灵宠状态树
 * - 集中处理 20 字节安全 MTU 分片、触觉震动分发与离线存储同步
 * - 完整支持硬件播音音量双通道同步、测试试听与大模型/网络状态联动
 */

const { StickS3BLEClient } = require("./sticks3_ble.js");
const { StickS3HttpClient } = require("./sticks3_wifi.js");
const { StorageManager } = require("./storage_manager.js");
const { haptics } = require("./haptics.js");

const SIM_ACTIONS = {
  feed:  { mood: 10, tag: "🍰 美食", xp: 10, energy: 20, feedInc: 1, text: (v) => `主人喂我吃了一块${v || "草莓大福"}，吧唧吧唧超级满足，活力满满！` },
  groom: { mood: 11, tag: "✨ 梳毛", xp: 12, energy: 0,  groomInc: 1, text: () => "主人用小梳子温柔地帮我梳理毛发，整只宠都舒服得想呼噜呼噜~" },
  play:  { mood: 12, tag: "✋ 击掌", xp: 15, energy: -10, text: () => "和主人默契击掌！小虎牙笑得合不拢嘴，我们也是元气满满的搭档！" },
  pet:   { mood: 4,  tag: "🌸 抚摸", xp: 5,  energy: 0,  petInc: 1,  text: () => "主人刚刚隔空温柔地摸了摸我，感觉心底暖洋洋的~" },
  shake: { mood: 5,  tag: "🌀 调皮", xp: 0,  energy: 0,  shakeInc: 1, text: () => "哎呀呀，调皮晃动让我脑袋转圈圈，眼睛里冒出好多小金星！" },
  sleep: { mood: 7,  tag: "🌙 晚安", xp: 0,  energy: 0,  text: () => "呼噜呼噜~ 灵宠进入梦乡打呼噜啦，晚安哦。" },
  wake:  { mood: 1,  tag: "📖 互动", xp: 0,  energy: 0,  text: () => "悄悄揉揉眼睛苏醒啦！今天也要元气满满哦！" }
};

class BuddyService {
  constructor() {
    this.bleClient = new StickS3BLEClient();
    this.httpClient = new StickS3HttpClient();

    const savedSettings = StorageManager.getSettings();
    haptics.setEnabled(savedSettings.vibrationEnabled !== false);
    this.httpClient.setHost(savedSettings.wifiHost || "192.168.110.67");

    this.petState = StorageManager.getPetState();
    this.petState.volume = Number(savedSettings.speakerVolume) || 70;
    this._lastUserVolumeSetTime = 0;
    this.memoryTurns = StorageManager.getMemories();
    this.diaries = StorageManager.getDiaries();

    this.hotspot = {
      isHotspot: Boolean(savedSettings.isHotspot),
      usedMb: 0,
      limitMb: Number(savedSettings.hotspotLimitMb) || 100,
      remainingMb: Number(savedSettings.hotspotLimitMb) || 100,
      cutoffActive: false,
      cutoffEnabled: savedSettings.hotspotCutoffEnabled !== false,
      warningIssued: false
    };

    this.deviceWifi = {
      sta_connected: false,
      sta_state: "idle",
      sta_ip: "0.0.0.0",
      sta_ssid: "",
      sta_rssi: 0
    };

    this.isConnected = false;
    this.isBleMode = false;
    this.isWifiMode = false;
    this.isSimMode = false;
    this.connectionStatusText = "未连接伴侣";

    this.wifiPollTimer = null;
    this._isWifiPolling = false;
    this.listeners = [];

    this._setupBleHandlers();
    this._autoProbeWifi();
  }

  _autoProbeWifi() {
    setTimeout(() => {
      if (this.httpClient && this.httpClient.host) {
        this.httpClient.getPetStatus().then(st => {
          if (st) {
            this.isConnected = true;
            this.isWifiMode = true;
            this.connectionStatusText = "Wi-Fi 在线";
            this.updatePetState(st);
            this._startWifiPolling();
            this.notifyListeners("connection", {
              isConnected: true,
              isWifiMode: true,
              statusText: "Wi-Fi 在线"
            });
          }
        }).catch(() => {});
      }
    }, 1200);
  }

  _setupBleHandlers() {
    this.bleClient.onStatusUpdate = (st) => this.updatePetState(st);
    this.bleClient.onDiaryReceived = (diary) => this.handleIncomingDiary(diary, "BLE 推送");
    this.bleClient.onMemoryReceived = (mems) => {
      if (Array.isArray(mems)) {
        this.memoryTurns = mems;
        StorageManager.saveMemories(mems);
        if (mems.length > 0 && (mems[0].ai || mems[0].user)) {
          this.petState.subtitle = mems[0].ai || mems[0].user;
        }
        this.notifyListeners("memory", mems);
        this.notifyListeners("sync", {
          petState: this.petState,
          hotspot: this.hotspot,
          deviceWifi: this.deviceWifi
        });
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

  subscribe(fn) {
    if (typeof fn === "function" && !this.listeners.includes(fn)) {
      this.listeners.push(fn);
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

  updatePetState(st) {
    if (!st) return;
    const cur = { ...this.petState };
    ["name", "level", "xp", "energy", "feeds", "grooms", "pets", "shakes"].forEach(k => {
      if (st[k] !== undefined) cur[k] = st[k];
    });
    if (st.mood !== undefined) cur.mood = st.mood;
    if (st.mood_id !== undefined) cur.mood = st.mood_id;

    const now = Date.now();
    const isVolumeProtected = this._lastUserVolumeSetTime && (now - this._lastUserVolumeSetTime < 3500);
    if (!isVolumeProtected) {
      if (st.speaker_volume !== undefined) cur.volume = Number(st.speaker_volume);
      else if (st.volume !== undefined) cur.volume = Number(st.volume);
    }

    if (st.diary) {
      let d = st.diary;
      if (typeof d === "string" && d.trim().startsWith("{") && d.trim().endsWith("}")) {
        try {
          const parsed = JSON.parse(d.trim());
          d = (parsed && (parsed.diary || parsed.text || parsed.content)) || d;
        } catch (e) {}
      }
      cur.diary = d;
      cur.subtitle = d;
    }
    if (st.subtitle) cur.subtitle = st.subtitle;

    let hotspotChanged = false;
    if (st.is_hotspot !== undefined) { this.hotspot.isHotspot = Boolean(st.is_hotspot); hotspotChanged = true; }
    if (st.hs_used_mb !== undefined) { this.hotspot.usedMb = Number(st.hs_used_mb); hotspotChanged = true; }
    if (st.hs_limit_mb !== undefined) { this.hotspot.limitMb = Number(st.hs_limit_mb); hotspotChanged = true; }
    if (st.hs_cutoff !== undefined) { this.hotspot.cutoffActive = Boolean(st.hs_cutoff); hotspotChanged = true; }
    if (hotspotChanged) {
      this.hotspot.remainingMb = Math.max(0, parseFloat((this.hotspot.limitMb - this.hotspot.usedMb).toFixed(2)));
    }

    if (st.sta_connected !== undefined || st.sta_conn !== undefined) {
      this.deviceWifi.sta_connected = Boolean(st.sta_connected !== undefined ? st.sta_connected : st.sta_conn);
    }
    if (st.sta_state || st.sta_st) this.deviceWifi.sta_state = st.sta_state || st.sta_st;
    if (st.sta_ip && st.sta_ip !== "0.0.0.0") {
      this.deviceWifi.sta_ip = st.sta_ip;
      this.httpClient.setHost(st.sta_ip);
    }
    if (st.sta_ssid) this.deviceWifi.sta_ssid = st.sta_ssid;
    if (st.sta_rssi !== undefined) this.deviceWifi.sta_rssi = Number(st.sta_rssi);

    this.petState = cur;
    StorageManager.savePetState(cur);

    this.notifyListeners("sync", {
      petState: this.petState,
      hotspot: this.hotspot,
      deviceWifi: this.deviceWifi,
      data: this.deviceWifi
    });
  }

  handleIncomingDiary(diaryText, tag = "📖 心声") {
    if (!diaryText) return;
    let cleanText = diaryText;
    if (typeof cleanText === "object" && cleanText !== null) {
      cleanText = cleanText.diary || cleanText.text || cleanText.content || JSON.stringify(cleanText);
    } else if (typeof cleanText === "string") {
      const trimmed = cleanText.trim();
      if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
        try {
          const parsed = JSON.parse(trimmed);
          cleanText = (parsed && (parsed.diary || parsed.text || parsed.content)) || cleanText;
        } catch (e) {}
      }
    }
    if (!cleanText || typeof cleanText !== "string" || !cleanText.trim()) return;
    cleanText = cleanText.trim();

    haptics.notification();
    this.petState.diary = cleanText;
    this.petState.subtitle = cleanText;
    const entry = StorageManager.saveDiaryEntry(cleanText, this.petState.mood, tag);
    this.diaries = StorageManager.getDiaries();
    this.notifyListeners("diary", { entry, diaries: this.diaries, latest: cleanText });
    this.notifyListeners("sync", {
      petState: this.petState,
      hotspot: this.hotspot,
      deviceWifi: this.deviceWifi
    });
  }

  async dispatchAction(action, value = "") {
    switch (action) {
      case "feed":  haptics.feed(); break;
      case "pet":   haptics.pet(); break;
      case "groom": haptics.groom(); break;
      case "play":  haptics.play(); break;
      default:      haptics.vibrate("medium"); break;
    }

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction(action, value);
        return { success: true, mode: "ble" };
      } catch (e) {
        console.warn("[BuddyService] BLE action write error, fallback to HTTP:", e);
      }
    }

    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        const res = await this.httpClient.sendPetAction(action, value);
        if (res) {
          if (!this.isWifiMode) {
            this.isWifiMode = true;
            this.isConnected = true;
            this.connectionStatusText = "Wi-Fi 在线";
            this.notifyListeners("connection", { isConnected: true, isWifiMode: true, statusText: "Wi-Fi 在线" });
          }
          this.updatePetState(res);
          if (res.diary) {
            this.handleIncomingDiary(res.diary, this.getActionMoodTag(action));
          }
          return { success: true, mode: "wifi", data: res };
        }
      } catch (e) {
        console.warn("[BuddyService] Wi-Fi action request failed, fallback to sim:", e);
      }
    }

    return this._runLocalSimAction(action, value);
  }

  _runLocalSimAction(action, value) {
    const st = { ...this.petState };
    const rule = SIM_ACTIONS[action];
    let diaryContent = "";
    let moodTag = "📖 互动";

    if (rule) {
      st.mood = rule.mood;
      if (rule.xp) st.xp += rule.xp;
      if (rule.energy) st.energy = Math.max(10, Math.min(100, st.energy + rule.energy));
      if (rule.feedInc) st.feeds += rule.feedInc;
      if (rule.groomInc) st.grooms += rule.groomInc;
      if (rule.petInc) st.pets += rule.petInc;
      if (rule.shakeInc) st.shakes += rule.shakeInc;
      diaryContent = rule.text(value);
      moodTag = rule.tag;
      if ([4, 5, 10, 11, 12].includes(rule.mood)) {
        setTimeout(() => { if (this.petState.mood === rule.mood) this.setMood(0); }, 3000);
      }
    }

    if (st.xp >= 100 && st.level < 10) {
      st.level += 1;
      st.xp = st.xp - 100;
      diaryContent = `太棒啦！我和主人的羁绊提升到了 Lv.${st.level}，解锁了更多陪伴默契！`;
      haptics.levelUp();
    }

    st.diary = diaryContent;
    this.updatePetState(st);
    if (diaryContent) this.handleIncomingDiary(diaryContent, moodTag);

    return { success: true, mode: "sim" };
  }

  getActionMoodTag(action) {
    return (SIM_ACTIONS[action] && SIM_ACTIONS[action].tag) || "📖 互动";
  }

  setMood(mood) {
    this.petState.mood = mood;
    this.notifyListeners("state", this.petState);
  }

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

  _startWifiPolling() {
    if (this.wifiPollTimer) {
      clearInterval(this.wifiPollTimer);
      this.wifiPollTimer = null;
    }

    const pollInterval = (this.hotspot && this.hotspot.isHotspot) ? 6000 : 2500;
    let consecutiveFailures = 0;

    const runPoll = async () => {
      if (this._isWifiPolling || !this.isWifiMode || !this.httpClient) return;
      // 手机热点下若连续失败两次，暂停激进请求，信赖 BLE 广播通道
      if (this.hotspot && this.hotspot.isHotspot && consecutiveFailures >= 2) {
        return;
      }
      this._isWifiPolling = true;
      try {
        const live = await this.httpClient.getPetStatus();
        consecutiveFailures = 0;
        this.updatePetState(live);
      } catch (e) {
        consecutiveFailures++;
      } finally {
        this._isWifiPolling = false;
      }
    };

    this.wifiPollTimer = setInterval(runPoll, pollInterval);
  }

  _stopWifiPolling() {
    if (this.wifiPollTimer) {
      clearInterval(this.wifiPollTimer);
      this.wifiPollTimer = null;
    }
    this._isWifiPolling = false;
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

    this._startWifiPolling();

    this.notifyListeners("connection", {
      isConnected: true,
      isWifiMode: true,
      statusText: "Wi-Fi 在线"
    });
    return st;
  }

  disconnectWifi() {
    this._stopWifiPolling();
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
      await this.bleClient.injectAction("wifi_cfg", payload);
      this.notifyListeners("hotspot", this.hotspot);
      return { status: "provisioned", mode: "ble", ssid, isHotspot, dataLimitMb };
    }

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

    if (this.isSimMode) {
      this.handleIncomingDiary(`[仿真配网] 成功配置 ${isHotspot ? "手机移动热点" : "Wi-Fi网络"}: ${ssid}，流量上限 ${dataLimitMb}MB`, "📶 网络");
      this.notifyListeners("hotspot", this.hotspot);
      return { status: "provisioned", mode: "sim", ssid, isHotspot, dataLimitMb };
    }

    throw new Error("请先通过 BLE 蓝牙或 Wi-Fi 连接 StickS3 设备后再执行配网");
  }

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
      await this.bleClient.injectAction("hotspot_cfg", {
        action: "hotspot_cfg",
        is_hotspot: this.hotspot.isHotspot,
        data_limit_mb: this.hotspot.limitMb,
        cutoff_enabled: this.hotspot.cutoffEnabled
      });
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

  async resetHotspotTraffic() {
    this.hotspot.usedMb = 0;
    this.hotspot.remainingMb = this.hotspot.limitMb;
    this.hotspot.cutoffActive = false;
    this.hotspot.warningIssued = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("reset_traffic", { action: "reset_traffic" });
    } else if (this.isWifiMode) {
      await this.httpClient.resetHotspotTraffic();
    }

    this.notifyListeners("hotspot", this.hotspot);
    return { success: true, hotspot: this.hotspot };
  }

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
          return this.hotspot;
        }
      } catch (e) {
        console.warn("[BuddyService] fetchHotspotTraffic HTTP error:", e);
      }
    }

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("get_status", "");
        await this.bleClient.readStatus();
        await new Promise(r => setTimeout(r, 200));
        this.notifyListeners("hotspot", this.hotspot);
        return this.hotspot;
      } catch (e) {
        console.warn("[BuddyService] fetchHotspotTraffic BLE error:", e);
      }
    }

    return this.hotspot;
  }

  async syncMemories() {
    if (this.isWifiMode) {
      try {
        const mems = await this.httpClient.getMemories();
        if (Array.isArray(mems) && mems.length > 0) {
          this.memoryTurns = mems;
          StorageManager.saveMemories(mems);
          if (mems[0] && (mems[0].ai || mems[0].user)) {
            this.petState.subtitle = mems[0].ai || mems[0].user;
          }
          this.notifyListeners("memory", mems);
          this.notifyListeners("sync", {
            petState: this.petState,
            hotspot: this.hotspot,
            deviceWifi: this.deviceWifi
          });
          return mems;
        }
      } catch (e) {
        console.warn("[BuddyService] syncMemories HTTP error:", e);
      }
    }

    if (this.isBleMode && this.bleClient.isConnected) {
      return new Promise(async (resolve) => {
        let timer = null;
        const originalOnMemory = this.bleClient.onMemoryReceived;

        const cleanup = (result) => {
          if (timer) clearTimeout(timer);
          this.bleClient.onMemoryReceived = originalOnMemory;
          if (Array.isArray(result) && result.length > 0 && (result[0].ai || result[0].user)) {
            this.petState.subtitle = result[0].ai || result[0].user;
            this.notifyListeners("sync", {
              petState: this.petState,
              hotspot: this.hotspot,
              deviceWifi: this.deviceWifi
            });
          }
          resolve(result);
        };

        this.bleClient.onMemoryReceived = (mems) => {
          if (originalOnMemory) originalOnMemory(mems);
          cleanup(mems);
        };

        timer = setTimeout(() => cleanup(StorageManager.getMemories()), 2500);

        try {
          await this.bleClient.injectAction("sync_memory", "");
        } catch (e) {
          cleanup(StorageManager.getMemories());
        }
      });
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

  async checkDeviceNetworkStatus() {
    try {
      const data = await this.httpClient.getWifiStatus();
      if (data && data.sta_state) {
        const isDeviceOnline = (data.sta_state === "connected");
        if (isDeviceOnline && data.sta_ip && data.sta_ip !== "0.0.0.0") {
          this.httpClient.setHost(data.sta_ip);
          StorageManager.saveSettings({ wifiHost: data.sta_ip });
        }
        if (data.is_hotspot !== undefined) {
          this.hotspot.isHotspot = Boolean(data.is_hotspot);
          if (data.hs_used_mb !== undefined) this.hotspot.usedMb = Number(data.hs_used_mb);
          if (data.hs_limit_mb !== undefined) this.hotspot.limitMb = Number(data.hs_limit_mb);
          this.hotspot.remainingMb = Math.max(0, parseFloat((this.hotspot.limitMb - this.hotspot.usedMb).toFixed(2)));
          this.notifyListeners("hotspot", this.hotspot);
        }
        return data;
      }
    } catch (e) {}

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("query_wifi_status", "");
        await this.bleClient.readStatus();
        await new Promise(r => setTimeout(r, 250));
        return {
          sta_state: this.deviceWifi.sta_state,
          sta_ip: this.deviceWifi.sta_ip,
          sta_ssid: this.deviceWifi.sta_ssid,
          sta_rssi: this.deviceWifi.sta_rssi,
          sta_connected: this.deviceWifi.sta_connected,
          is_hotspot: this.hotspot.isHotspot,
          hs_used_mb: this.hotspot.usedMb,
          hs_limit_mb: this.hotspot.limitMb
        };
      } catch (e) {}
    }

    return this.deviceWifi ? {
      sta_state: this.deviceWifi.sta_state,
      sta_ip: this.deviceWifi.sta_ip,
      sta_ssid: this.deviceWifi.sta_ssid,
      sta_rssi: this.deviceWifi.sta_rssi,
      sta_connected: this.deviceWifi.sta_connected,
      is_hotspot: this.hotspot.isHotspot,
      hs_used_mb: this.hotspot.usedMb,
      hs_limit_mb: this.hotspot.limitMb
    } : null;
  }

  async pollDeviceNetworkUntilConnected({ maxAttempts = 15, intervalMs = 2000 } = {}) {
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, intervalMs));
      try {
        const status = await this.checkDeviceNetworkStatus();
        if (status && status.sta_state === "connected" && status.sta_ip && status.sta_ip !== "0.0.0.0") {
          return { success: true, attempt: i + 1, ...status };
        }
      } catch (e) {}
    }
    return { success: false, attempt: maxAttempts };
  }

  async setBailianConfig({ key, model, voice, prompt, volume }) {
    const settings = StorageManager.getSettings();
    if (key !== undefined && key.trim().length > 0) settings.bailianKey = key.trim();
    if (model) settings.bailianModel = model;
    if (voice) settings.bailianVoice = voice;
    if (prompt !== undefined) settings.bailianPrompt = prompt;
    if (volume !== undefined) settings.speakerVolume = Number(volume);
    StorageManager.saveSettings(settings);

    const payload = {
      action: "bailian_cfg",
      key: key || settings.bailianKey || "",
      model: model || settings.bailianModel || "qwen3.8-omni-flash-realtime",
      voice: voice || settings.bailianVoice || "Tina",
      prompt: prompt !== undefined ? prompt : (settings.bailianPrompt || "")
    };
    if (volume !== undefined) {
      payload.volume = Number(volume);
      this.petState.volume = Number(volume);
    }

    let bleOk = false;
    let wifiOk = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("bailian_cfg", payload);
        bleOk = true;
      } catch (e) {
        console.warn("[BuddyService] BLE setBailianConfig failed:", e);
      }
    }

    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        await this.httpClient.saveBailianConfig(payload);
        wifiOk = true;
      } catch (e) {
        console.warn("[BuddyService] HTTP setBailianConfig failed:", e);
      }
    }

    if (volume !== undefined) {
      this.setSpeakerVolume(volume).catch(() => {});
    }

    if (!bleOk && !wifiOk && !this.isSimMode) {
      throw new Error("请先连接 StickS3 设备 (BLE 或 Wi-Fi) 后再保存大模型配置");
    }

    this.handleIncomingDiary(`[系统配置] 已更新百炼配置：${payload.model}，音色 ${payload.voice}` + (volume !== undefined ? `，音量 ${volume}%` : ""), "🤖 模型");
    return { success: true, ...payload };
  }

  async previewVoice(voice = "Tina") {
    let devSent = false;
    let mode = "offline";

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("preview_voice", { action: "preview_voice", voice });
        devSent = true;
        mode = "ble";
      } catch (e) {}
    }

    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        await this.httpClient.previewVoice(voice);
        devSent = true;
        mode = (mode === "ble") ? "dual" : "wifi";
      } catch (e) {
        if (!devSent) console.warn("[BuddyService] HTTP preview_voice failed:", e);
      }
    }

    return { success: true, deviceTriggered: devSent, mode, voice };
  }

  async setSpeakerVolume(volume) {
    let vol = parseInt(volume, 10);
    if (isNaN(vol)) vol = 70;
    vol = Math.max(10, Math.min(100, vol));

    this._lastUserVolumeSetTime = Date.now();
    const settings = StorageManager.getSettings();
    settings.speakerVolume = vol;
    StorageManager.saveSettings(settings);

    if (this.petState) {
      this.petState.volume = vol;
      this.notifyListeners("sync", {
        petState: this.petState,
        hotspot: this.hotspot,
        deviceWifi: this.deviceWifi
      });
      this.notifyListeners("state", this.petState);
    }

    let devSent = false;
    let lastError = null;

    // 1. 若 BLE 已连接，优先走 BLE 毫秒级极速通道 (仅耗时 15~25ms)
    if (this.bleClient && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("volume", { action: "volume", volume: vol });
        devSent = true;
      } catch (e) {
        lastError = e;
        console.warn("[BuddyService] BLE setSpeakerVolume failed:", e);
      }
    }

    // 2. HTTP 通道自适应：
    // 若 BLE 未连接，或非移动热点环境，则通过 HTTP 同步
    // 在手机热点模式下，由于 iOS 系统级拦截本机 App 对热点客户端的 HTTP 访问，绝不在此同步阻塞等待
    const isHotspotMode = Boolean(this.hotspot && this.hotspot.isHotspot);
    const host = (this.httpClient && this.httpClient.host) || settings.wifiHost || "192.168.110.67";

    if (this.httpClient && host) {
      this.httpClient.setHost(host);
      if (!devSent) {
        // BLE 未发送成功，必须等待 HTTP 响应
        try {
          await this.httpClient.setSpeakerVolume(vol);
          devSent = true;
        } catch (e) {
          lastError = e;
          console.warn("[BuddyService] HTTP setSpeakerVolume failed:", e);
        }
      } else if (!isHotspotMode) {
        // BLE 已发送成功且为常规局域网，后台异步通知 HTTP 无需阻塞等待
        this.httpClient.setSpeakerVolume(vol).catch(() => {});
      }
    }

    return { success: true, volume: vol, deviceTriggered: devSent, error: lastError };
  }

  async testSpeakerVolume(volume) {
    const vol = (volume !== undefined) ? parseInt(volume, 10) : (this.petState && this.petState.volume);
    this._lastUserVolumeSetTime = Date.now();
    if (!isNaN(vol)) {
      this.petState.volume = vol;
      const settings = StorageManager.getSettings();
      settings.speakerVolume = vol;
      StorageManager.saveSettings(settings);
    }

    let devSent = false;
    let lastError = null;

    // 1. 若 BLE 已连接，优先走 BLE 毫秒级极速通道触发试听发声 (彻底消灭 3.5s 等待与卡顿)
    if (this.bleClient && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("test_volume", { action: "test_volume", volume: vol });
        devSent = true;
      } catch (e) {
        lastError = e;
        console.warn("[BuddyService] BLE test_volume failed:", e);
      }
    }

    // 2. HTTP 通道自适应
    const isHotspotMode = Boolean(this.hotspot && this.hotspot.isHotspot);
    const host = (this.httpClient && this.httpClient.host) || StorageManager.getSettings().wifiHost || "192.168.110.67";

    if (this.httpClient && host) {
      this.httpClient.setHost(host);
      if (!devSent) {
        // BLE 未连接，通过 HTTP 同步触发试听
        try {
          await this.httpClient.testSpeakerVolume(vol);
          devSent = true;
        } catch (e) {
          lastError = e;
          console.warn("[BuddyService] HTTP test_volume failed:", e);
        }
      } else if (!isHotspotMode) {
        // BLE 已触发，常规 Wi-Fi 宽带模式下后台轻量同步，不阻塞 UI 渲染
        this.httpClient.testSpeakerVolume(vol).catch(() => {});
      }
    }

    return { success: true, deviceTriggered: devSent, error: lastError };
  }

  // 主动读取硬件真实播音音量 (自适应 HTTP / BLE 双通道)
  async getSpeakerVolume() {
    let vol = null;
    const settings = StorageManager.getSettings();
    const host = (this.httpClient && this.httpClient.host) || settings.wifiHost || "192.168.110.67";

    // 1. 优先尝试 HTTP 直读设备当前物理音量
    if (this.httpClient) {
      this.httpClient.setHost(host);
      try {
        const res = await this.httpClient.getSpeakerVolume();
        if (res && res.volume !== undefined) {
          vol = parseInt(res.volume, 10);
        }
      } catch (e) {}
    }

    // 2. 若 HTTP 失败且 BLE 已连接，尝试 BLE 特征值快照
    if ((vol === null || isNaN(vol)) && this.bleClient && this.bleClient.isConnected) {
      try {
        await this.bleClient.readStatus();
        if (this.petState && this.petState.volume !== undefined) {
          vol = this.petState.volume;
        }
      } catch (e) {}
    }

    if (vol !== null && !isNaN(vol)) {
      vol = Math.max(10, Math.min(100, vol));
      if (this.petState) this.petState.volume = vol;
      settings.speakerVolume = vol;
      StorageManager.saveSettings(settings);
      return vol;
    }

    return (this.petState && this.petState.volume) || Number(settings.speakerVolume) || 70;
  }

  async getBailianStatus() {
    if (this.isWifiMode) {
      try {
        return await this.httpClient.getBailianStatus();
      } catch (e) {}
    }
    const settings = StorageManager.getSettings();
    return {
      configured_voice: settings.bailianVoice || "Tina",
      configured_model: settings.bailianModel || "qwen3.8-omni-flash-realtime",
      prompt: settings.bailianPrompt || "",
      has_key: Boolean(settings.bailianKey && settings.bailianKey.length > 10),
      masked_key: settings.bailianKey ? (settings.bailianKey.substring(0, 4) + "••••••••" + settings.bailianKey.slice(-4)) : ""
    };
  }

  async setWakewordConfig({ enabled = true, sensitivity = 75, timeoutSec = 8 }) {
    const settings = StorageManager.getSettings();
    settings.wakewordEnabled = Boolean(enabled);
    settings.wakewordSensitivity = Number(sensitivity);
    settings.wakewordTimeoutSec = Number(timeoutSec);
    StorageManager.saveSettings(settings);

    const payload = {
      action: "wakeword_cfg",
      enabled: settings.wakewordEnabled,
      sensitivity: settings.wakewordSensitivity,
      timeout_sec: settings.wakewordTimeoutSec
    };

    let bleOk = false;
    let wifiOk = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("wakeword_cfg", payload);
        bleOk = true;
      } catch (e) {}
    }

    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        await this.httpClient.saveWakewordConfig({
          enabled: payload.enabled,
          sensitivity: payload.sensitivity,
          timeoutSec: payload.timeout_sec
        });
        wifiOk = true;
      } catch (e) {}
    }

    if (!bleOk && !wifiOk && !this.isSimMode) {
      throw new Error("请先连接 StickS3 设备后再配置唤醒词");
    }

    this.handleIncomingDiary(`[系统配置] 离线唤醒词：${payload.enabled ? "已开启" : "已关闭"}，灵敏度 ${payload.sensitivity}%`, "🗣️ 唤醒");
    return { success: true, ...payload };
  }

  async triggerWakeSim(confidence = 98.0) {
    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("trigger_wake", { action: "trigger_wake", confidence });
      return { success: true, mode: "ble" };
    }
    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      await this.httpClient.triggerWakeSim(confidence);
      return { success: true, mode: "wifi" };
    }
    if (this.isSimMode) {
      this.handleIncomingDiary("[仿真测试] 唤醒词「悄悄」触发成功！", "🗣️ 唤醒");
      return { success: true, mode: "sim" };
    }
    throw new Error("请先连接设备后再进行唤醒模拟测试");
  }

  async clearDeviceMemory() {
    this.clearMemories();
    let bleOk = false;
    let wifiOk = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("clear_memory", { action: "clear_memory" });
        bleOk = true;
      } catch (e) {}
    }

    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        await this.httpClient.clearDeviceMemory();
        wifiOk = true;
      } catch (e) {}
    }

    this.handleIncomingDiary("已清空设备全部历史长程对话记忆。", "🗑️ 记忆");
    return { success: true, bleOk, wifiOk };
  }

  async rebootDevice() {
    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("reboot", { action: "reboot" });
      return { success: true, mode: "ble" };
    }
    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      await this.httpClient.reboot();
      return { success: true, mode: "wifi" };
    }
    throw new Error("请先连接设备后再执行重启");
  }

  async factoryResetDevice() {
    let bleOk = false;
    let wifiOk = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("factory_reset", { action: "factory_reset" });
        bleOk = true;
      } catch (e) {}
    }

    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        await this.httpClient.factoryReset();
        wifiOk = true;
      } catch (e) {}
    }

    StorageManager.resetAllData();
    this.memoryTurns = [];
    this.diaries = [];
    this.hotspot = {
      isHotspot: false,
      usedMb: 0,
      limitMb: 100,
      remainingMb: 100,
      cutoffActive: false,
      cutoffEnabled: true,
      warningIssued: false
    };

    this.notifyListeners("memory", []);
    this.notifyListeners("hotspot", this.hotspot);
    this.notifyListeners("sync", {
      petState: this.petState,
      hotspot: this.hotspot,
      deviceWifi: this.deviceWifi
    });

    return { success: true, bleOk, wifiOk };
  }
}

const buddyService = new BuddyService();

module.exports = {
  BuddyService,
  buddyService
};
