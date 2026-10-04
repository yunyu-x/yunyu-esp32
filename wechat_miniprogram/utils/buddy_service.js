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
    this.petState.volume = Number(savedSettings.speakerVolume) || 70;
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

    // 设备端 Wi-Fi STA 联网状态
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
    this.listeners = [];

    this._setupBleHandlers();
    this._autoProbeWifi();
  }

  _autoProbeWifi() {
    // 延迟异步探测，确保小程序框架与模拟器 WebView 完成基础握手
    setTimeout(() => {
      if (this.httpClient && this.httpClient.host) {
        this.httpClient.getPetStatus().then(st => {
          if (st) {
            this.isConnected = true;
            this.isWifiMode = true;
            this.connectionStatusText = "Wi-Fi 在线";
            this.updatePetState(st);
            this.notifyListeners("connection", {
              isConnected: true,
              isWifiMode: true,
              statusText: "Wi-Fi 在线"
            });
          }
        }).catch(() => {
          // 静默探测
        });
      }
    }, 1200);
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
        if (mems.length > 0) {
          const latest = mems[0];
          if (latest && (latest.ai || latest.user)) {
            this.petState.subtitle = latest.ai || latest.user;
          }
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
    if (st.subtitle) {
      cur.subtitle = st.subtitle;
    }

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

    // 同步 Wi-Fi / 网络遥测指标
    let wifiChanged = false;
    if (st.sta_connected !== undefined || st.sta_conn !== undefined) {
      this.deviceWifi.sta_connected = Boolean(st.sta_connected !== undefined ? st.sta_connected : st.sta_conn);
      wifiChanged = true;
    }
    if (st.sta_state || st.sta_st) {
      this.deviceWifi.sta_state = st.sta_state || st.sta_st;
      wifiChanged = true;
    }
    if (st.sta_ip && st.sta_ip !== "0.0.0.0") {
      this.deviceWifi.sta_ip = st.sta_ip;
      this.httpClient.setHost(st.sta_ip);
      wifiChanged = true;
    }
    if (st.sta_ssid) {
      this.deviceWifi.sta_ssid = st.sta_ssid;
      wifiChanged = true;
    }
    if (st.sta_rssi !== undefined) {
      this.deviceWifi.sta_rssi = Number(st.sta_rssi);
      wifiChanged = true;
    }

    this.petState = cur;
    StorageManager.savePetState(cur);

    // 派发单一聚合 sync 事件，杜绝单包三次触发引起界面频繁重绘与频闪
    this.notifyListeners("sync", {
      petState: this.petState,
      hotspot: this.hotspot,
      deviceWifi: this.deviceWifi,
      data: this.deviceWifi // 兼容 wifi_status
    });
  }

  // 接收并沉淀新日记
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

    // 1. BLE 模式优先直连
    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction(action, value);
        return { success: true, mode: "ble" };
      } catch (e) {
        console.warn("[BuddyService] BLE action write error, fallback to HTTP:", e);
      }
    }

    // 2. Wi-Fi RESTful 通道 (显式 Wi-Fi 模式或配置了局域网 Host 时自动发送)
    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        const res = await this.httpClient.sendPetAction(action, value);
        if (res) {
          if (!this.isWifiMode) {
            this.isWifiMode = true;
            this.isConnected = true;
            this.connectionStatusText = "Wi-Fi 在线";
            this.notifyListeners("connection", {
              isConnected: true,
              isWifiMode: true,
              statusText: "Wi-Fi 在线"
            });
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
      diaryContent = "悄悄揉揉眼睛苏醒啦！今天也要元气满满哦！";
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

    // 1. 若 BLE 已连接，采用安全 MTU 分片写入到 0xFFB4
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

  // --- 重置手机热点流量统计计数器 ---
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

  // --- 查询热点流量实时数据 (Wi-Fi HTTP 或 BLE 双通道) ---
  async fetchHotspotTraffic() {
    // 1. Wi-Fi 在线模式下通过 HTTP 端点获取
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

    // 2. BLE 模式下通过主动拉取特征值 0xFFB2
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

  // --- 历史人机对话多轮记忆同步与管理 (支持 BLE 分片流式拉取) ---
  async syncMemories() {
    // 1. 优先通过 Wi-Fi HTTP 端点获取
    if (this.isWifiMode) {
      try {
        const mems = await this.httpClient.getMemories();
        if (Array.isArray(mems) && mems.length > 0) {
          this.memoryTurns = mems;
          StorageManager.saveMemories(mems);
          const latest = mems[0];
          if (latest && (latest.ai || latest.user)) {
            this.petState.subtitle = latest.ai || latest.user;
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

    // 2. BLE 模式：注入 sync_memory 指令并异步等待分片接收完成
    if (this.isBleMode && this.bleClient.isConnected) {
      return new Promise(async (resolve) => {
        let timer = null;
        const originalOnMemory = this.bleClient.onMemoryReceived;

        const cleanup = (result) => {
          if (timer) clearTimeout(timer);
          this.bleClient.onMemoryReceived = originalOnMemory;
          if (Array.isArray(result) && result.length > 0) {
            const latest = result[0];
            if (latest && (latest.ai || latest.user)) {
              this.petState.subtitle = latest.ai || latest.user;
            }
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

        // 最多等待 2.5 秒超时兜底
        timer = setTimeout(() => {
          const local = StorageManager.getMemories();
          cleanup(local);
        }, 2500);

        try {
          await this.bleClient.injectAction("sync_memory", "");
        } catch (e) {
          console.warn("[BuddyService] BLE inject sync_memory error:", e);
          const local = StorageManager.getMemories();
          cleanup(local);
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

  // --- 主动查询设备端 Wi-Fi STA 联网状态 (BLE 或 HTTP 双通道) ---
  async checkDeviceNetworkStatus() {
    // 1. 优先通过 Wi-Fi HTTP 直接查询（仅当手机与设备在同一局域网时可用）
    try {
      const data = await this.httpClient.getWifiStatus();
      if (data && data.sta_state) {
        // 同步更新本地 Wi-Fi 连接状态
        const isDeviceOnline = (data.sta_state === 'connected');
        if (isDeviceOnline && data.sta_ip && data.sta_ip !== '0.0.0.0') {
          this.httpClient.setHost(data.sta_ip);
          StorageManager.saveSettings({ wifiHost: data.sta_ip });
        }
        // 同步热点遥测
        if (data.is_hotspot !== undefined) {
          this.hotspot.isHotspot = Boolean(data.is_hotspot);
          if (data.hs_used_mb !== undefined) this.hotspot.usedMb = Number(data.hs_used_mb);
          if (data.hs_limit_mb !== undefined) this.hotspot.limitMb = Number(data.hs_limit_mb);
          this.hotspot.remainingMb = Math.max(0, parseFloat((this.hotspot.limitMb - this.hotspot.usedMb).toFixed(2)));
          this.notifyListeners('hotspot', this.hotspot);
        }
        return data;
      }
    } catch (e) {
      console.warn('[BuddyService] HTTP getWifiStatus failed, trying BLE...', e);
    }

    // 2. 通过 BLE 查询设备 Wi-Fi 状态
    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction('query_wifi_status', '');
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
      } catch (e) {
        console.warn('[BuddyService] BLE query_wifi_status failed:', e);
      }
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

  // --- 配网后轮询验证设备网络连接状态 (最多轮询 maxAttempts 次，每次间隔 intervalMs) ---
  async pollDeviceNetworkUntilConnected({ maxAttempts = 15, intervalMs = 2000 } = {}) {
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, intervalMs));
      try {
        const status = await this.checkDeviceNetworkStatus();
        if (status && status.sta_state === 'connected' && status.sta_ip && status.sta_ip !== '0.0.0.0') {
          return { success: true, attempt: i + 1, ...status };
        }
      } catch (e) {
        // 继续轮询
      }
    }
    return { success: false, attempt: maxAttempts };
  }

  // --- 阿里云百炼大模型双通道统一配置 (BLE / HTTP) ---
  async setBailianConfig({ key, model, voice, prompt }) {
    // 1. 同步保存到本地 settings
    const settings = StorageManager.getSettings();
    if (key !== undefined && key.trim().length > 0) settings.bailianKey = key.trim();
    if (model) settings.bailianModel = model;
    if (voice) settings.bailianVoice = voice;
    if (prompt !== undefined) settings.bailianPrompt = prompt;
    StorageManager.saveSettings(settings);

    const payload = {
      action: "bailian_cfg",
      key: key || settings.bailianKey || "",
      model: model || settings.bailianModel || "qwen3.8-omni-flash-realtime",
      voice: voice || settings.bailianVoice || "Tina",
      prompt: prompt !== undefined ? prompt : (settings.bailianPrompt || "")
    };

    let bleOk = false;
    let wifiOk = false;

    // 2. 若 BLE 已连接，安全分片注入
    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("bailian_cfg", payload);
        bleOk = true;
      } catch (e) {
        console.warn("[BuddyService] BLE setBailianConfig failed:", e);
      }
    }

    // 3. 若 Wi-Fi 模式在线，通过 HTTP 下发
    if (this.isWifiMode) {
      try {
        await this.httpClient.saveBailianConfig(payload);
        wifiOk = true;
      } catch (e) {
        console.warn("[BuddyService] HTTP setBailianConfig failed:", e);
      }
    }

    if (!bleOk && !wifiOk && !this.isSimMode) {
      throw new Error("请先连接 StickS3 设备 (BLE 或 Wi-Fi) 后再保存大模型配置");
    }

    this.handleIncomingDiary(`[系统配置] 已成功更新阿里云百炼大模型配置：${payload.model}，音色 ${payload.voice}`, "🤖 模型");
    return { success: true, ...payload };
  }

  // --- 实时音色即时试听 (支持 BLE、Wi-Fi 局域网自适应多通道分发) ---
  async previewVoice(voice = "Tina") {
    let devSent = false;
    let mode = "offline";

    // 1. 若 BLE 已连接，优先通过 0xFFB4 注入
    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("preview_voice", { action: "preview_voice", voice });
        devSent = true;
        mode = "ble";
      } catch (e) {
        console.warn("[BuddyService] BLE preview_voice failed:", e);
      }
    }

    // 2. 若 Wi-Fi 通道在线或配置了有效 host，通过 HTTP 端点下发
    if (this.isWifiMode || (this.httpClient && this.httpClient.host)) {
      try {
        await this.httpClient.previewVoice(voice);
        devSent = true;
        mode = (mode === "ble") ? "dual" : "wifi";
      } catch (e) {
        // 若 BLE 已成功发送，忽略 HTTP 失败
        if (!devSent) {
          console.warn("[BuddyService] HTTP preview_voice failed:", e);
        }
      }
    }

    return { success: true, deviceTriggered: devSent, mode, voice };
  }

  // --- 伴侣播音音量调节 (支持 BLE、Wi-Fi 局域网自适应多通道分发与本地持久化) ---
  async setSpeakerVolume(volume) {
    let vol = parseInt(volume, 10);
    if (isNaN(vol)) vol = 70;
    if (vol < 10) vol = 10;
    if (vol > 100) vol = 100;

    // 1. 同步保存到本地 settings 与内存状态
    const settings = StorageManager.getSettings();
    settings.speakerVolume = vol;
    StorageManager.saveSettings(settings);

    if (this.petState) {
      this.petState.volume = vol;
      this._emit({ type: "state", data: this.petState });
    }

    let devSent = false;
    let lastError = null;

    // 2. BLE 下发 (无论当前是否标记为 isBleMode，只要 BLE 物理连接在线均实时推送)
    if (this.bleClient && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("volume", { action: "volume", volume: vol });
        devSent = true;
      } catch (e) {
        lastError = e;
        console.warn("[BuddyService] BLE setSpeakerVolume failed:", e);
      }
    }

    // 3. HTTP 下发 (如果处于 Wi-Fi 模式或已配置合法设备 host)
    const host = (this.httpClient && this.httpClient.host) || settings.wifiHost || "192.168.110.67";
    if (this.httpClient) {
      this.httpClient.setHost(host);
      try {
        await this.httpClient.setSpeakerVolume(vol);
        devSent = true;
      } catch (e) {
        if (!devSent) lastError = e;
        console.warn("[BuddyService] HTTP setSpeakerVolume failed:", e);
      }
    }

    return { success: devSent, volume: vol, deviceTriggered: devSent, error: lastError };
  }

  // --- 试听伴侣播音音量 (发送测试和弦/提示音，直观感受当前响度) ---
  async testSpeakerVolume(volume) {
    if (volume !== undefined) {
      await this.setSpeakerVolume(volume);
    }

    let devSent = false;
    let lastError = null;

    if (this.bleClient && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("test_volume", { action: "test_volume" });
        devSent = true;
      } catch (e) {
        lastError = e;
        console.warn("[BuddyService] BLE testSpeakerVolume failed:", e);
      }
    }

    const host = (this.httpClient && this.httpClient.host) || StorageManager.getSettings().wifiHost || "192.168.110.67";
    if (this.httpClient) {
      this.httpClient.setHost(host);
      try {
        await this.httpClient.testSpeakerVolume();
        devSent = true;
      } catch (e) {
        if (!devSent) lastError = e;
        console.warn("[BuddyService] HTTP testSpeakerVolume failed:", e);
      }
    }

    return { success: devSent, deviceTriggered: devSent, error: lastError };
  }

  // --- 查询百炼状态 ---
  async getBailianStatus() {
    if (this.isWifiMode) {
      try {
        return await this.httpClient.getBailianStatus();
      } catch (e) {
        console.warn("[BuddyService] getBailianStatus failed:", e);
      }
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

  // --- 离线唤醒词「悄悄」配置 ---
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
      } catch (e) {
        console.warn("[BuddyService] BLE setWakewordConfig failed:", e);
      }
    }

    if (this.isWifiMode) {
      try {
        await this.httpClient.saveWakewordConfig({
          enabled: payload.enabled,
          sensitivity: payload.sensitivity,
          timeoutSec: payload.timeout_sec
        });
        wifiOk = true;
      } catch (e) {
        console.warn("[BuddyService] HTTP setWakewordConfig failed:", e);
      }
    }

    if (!bleOk && !wifiOk && !this.isSimMode) {
      throw new Error("请先连接 StickS3 设备后再配置唤醒词");
    }

    this.handleIncomingDiary(`[系统配置] 离线唤醒词配置已生效：${payload.enabled ? "已开启" : "已关闭"}，灵敏度 ${payload.sensitivity}%`, "🗣️ 唤醒");
    return { success: true, ...payload };
  }

  // --- 模拟离线唤醒词触发测试 ---
  async triggerWakeSim(confidence = 98.0) {
    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("trigger_wake", { action: "trigger_wake", confidence });
      return { success: true, mode: "ble" };
    }
    if (this.isWifiMode) {
      await this.httpClient.triggerWakeSim(confidence);
      return { success: true, mode: "wifi" };
    }
    if (this.isSimMode) {
      this.handleIncomingDiary("[仿真测试] 唤醒词「悄悄」触发成功！", "🗣️ 唤醒");
      return { success: true, mode: "sim" };
    }
    throw new Error("请先连接设备后再进行唤醒模拟测试");
  }

  // --- 清空设备端与小程序端全部多轮对话记忆 ---
  async clearDeviceMemory() {
    this.clearMemories();

    let bleOk = false;
    let wifiOk = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("clear_memory", { action: "clear_memory" });
        bleOk = true;
      } catch (e) {
        console.warn("[BuddyService] BLE clear_memory failed:", e);
      }
    }

    if (this.isWifiMode) {
      try {
        await this.httpClient.clearDeviceMemory();
        wifiOk = true;
      } catch (e) {
        console.warn("[BuddyService] HTTP clearDeviceMemory failed:", e);
      }
    }

    this.handleIncomingDiary("已清空设备全部历史长程对话记忆。", "🗑️ 记忆");
    return { success: true, bleOk, wifiOk };
  }

  // --- 硬件设备软重启 ---
  async rebootDevice() {
    if (this.isBleMode && this.bleClient.isConnected) {
      await this.bleClient.injectAction("reboot", { action: "reboot" });
      return { success: true, mode: "ble" };
    }
    if (this.isWifiMode) {
      await this.httpClient.reboot();
      return { success: true, mode: "wifi" };
    }
    throw new Error("请先连接设备后再执行重启");
  }

  // --- 一键恢复出厂设置 ---
  async factoryResetDevice() {
    let bleOk = false;
    let wifiOk = false;

    if (this.isBleMode && this.bleClient.isConnected) {
      try {
        await this.bleClient.injectAction("factory_reset", { action: "factory_reset" });
        bleOk = true;
      } catch (e) {
        console.warn("[BuddyService] BLE factory_reset failed:", e);
      }
    }

    if (this.isWifiMode) {
      try {
        await this.httpClient.factoryReset();
        wifiOk = true;
      } catch (e) {
        console.warn("[BuddyService] HTTP factoryReset failed:", e);
      }
    }

    // 重置小程序本地全部缓存数据
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

// 单例模式全局服务
const buddyService = new BuddyService();

module.exports = {
  BuddyService,
  buddyService
};
