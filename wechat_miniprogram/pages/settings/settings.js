const { buddyService } = require("../../utils/buddy_service.js");
const { StorageManager } = require("../../utils/storage_manager.js");
const { haptics } = require("../../utils/haptics.js");
const { voicePreviewEngine } = require("../../utils/voice_preview.js");

Page({
  data: {
    isConnected: false,
    isBleConnected: false,
    isWifiConnected: false,
    isSimMode: false,
    connectionStatusText: "未连接伴侣",
    currentModeName: "未连接",

    wifiHost: "192.168.110.67",
    wifiHostInput: "192.168.110.67",
    wifiSsid: "",
    wifiPwd: "",
    showPwd: false,

    networkMode: "wifi",
    selectedPreset: 100,
    customLimitInput: "",
    hotspotLimitMb: 100,
    hotspotCutoffEnabled: true,
    hotspotWarningEnabled: true,

    hotspot: {
      isHotspot: false,
      usedMb: 0,
      limitMb: 100,
      remainingMb: 100,
      cutoffActive: false,
      cutoffEnabled: true,
      warningIssued: false
    },
    trafficPercent: 0,

    petState: { level: 1 },

    isScanning: false,
    devices: [],
    isDeviceListExpanded: false,
    connectedDeviceName: "StickS3-Buddy",
    showWifiFaq: false,
    connectingId: "",
    isProvisioning: false,
    isTestingWifi: false,

    isVerifyingNetwork: false,
    verifyProgress: "",
    deviceStaState: "",
    deviceStaIp: "",
    deviceStaSsid: "",
    deviceStaRssi: 0,
    showLanDirectConnect: false,

    vibrationEnabled: true,

    // 阿里云百炼大模型交互设置
    bailianKey: "",
    bailianKeyInput: "",
    showBailianKey: false,
    hasBailianKey: false,
    maskedBailianKey: "",

    modelOptions: [
      { id: "qwen3.8-omni-flash-realtime", label: "qwen3.8-omni-flash (极速端到端 推荐)" },
      { id: "qwen-omni-turbo-realtime", label: "qwen-omni-turbo (进阶强推理)" },
      { id: "qwen3-audio-realtime", label: "qwen3-audio (经典音频流)" }
    ],
    selectedModelIndex: 0,
    bailianModel: "qwen3.8-omni-flash-realtime",

    voiceOptions: [
      { id: "Tina", label: "Tina (甜美温暖 · 默认推荐)" },
      { id: "Serena", label: "Serena (温柔亲切知性)" },
      { id: "Cindy", label: "Cindy (知性活泼台湾腔)" },
      { id: "Raymond", label: "Raymond (清亮自然男声)" },
      { id: "Zane", label: "Zane (磁性沉稳男声)" },
      { id: "Katerina", label: "Katerina (成熟御姐)" },
      { id: "Mia", label: "Mia (温柔细腻)" },
      { id: "Chloe", label: "Chloe (活力俏皮)" }
    ],
    selectedVoiceIndex: 0,
    bailianVoice: "Tina",
    speakerVolume: 70,
    displayVolume: 70,

    bailianPrompt: "你是StickS3智能语音伴侣，请用简明生动的口语回答，每次回答控制在两句话以内。",
    promptPresets: [
      { name: "🐱 傲娇猫娘", prompt: "你是一只傲娇可爱的小猫咪，说话带喵，语气轻快活泼，回答简短在两句话内。" },
      { name: "🧠 效率管家", prompt: "你是专业高效的私人随身助手，条理清晰，回答精准凝练，每次回答在两句话内。" },
      { name: "🌸 治愈系伴侣", prompt: "你是温柔治愈的心灵物理伴侣，倾听并给予温暖情绪价值，回答简短在两句话内。" },
      { name: "🎓 百科学者", prompt: "你是学识渊博的随身导师，用通俗生动的比喻解答疑惑，回答控制在两句话内。" }
    ],

    isSavingBailian: false,
    isPreviewingVoice: false,

    // 离线唤醒词配置
    wakewordEnabled: true,
    wakewordSensitivity: 75,
    wakewordTimeoutSec: 8,
    timeoutOptions: [5, 8, 12, 15, 20],
    selectedTimeoutIndex: 1,

    isSavingWakeword: false,
    isTriggeringWake: false,

    // 运维操作
    isClearingMemory: false,
    isRebootingDevice: false,
    isFactoryResetting: false,

    // 伴侣与功夫学徒渲染设置
    activePet: "qiaoqiao",
    cadetRenderMode: "fullcolor"
  },

  onLoad() {
    const settings = StorageManager.getSettings();
    const isHs = Boolean(settings.isHotspot);
    const limit = Number(settings.hotspotLimitMb) || 100;
    const preset = [50, 100, 200, 500].includes(limit) ? limit : "custom";

    const blModel = settings.bailianModel || "qwen3.8-omni-flash-realtime";
    const blVoice = this.data.voiceOptions.some(v => v.id === settings.bailianVoice) ? settings.bailianVoice : "Tina";
    const modelIdx = Math.max(0, this.data.modelOptions.findIndex(m => m.id === blModel));
    const voiceIdx = Math.max(0, this.data.voiceOptions.findIndex(v => v.id === blVoice));
    const tout = Number(settings.wakewordTimeoutSec) || 8;
    const toutIdx = Math.max(0, this.data.timeoutOptions.indexOf(tout));
    const hasKey = Boolean(settings.bailianKey && settings.bailianKey.length > 10);
    const maskedKey = hasKey ? (settings.bailianKey.substring(0, 4) + "••••••••" + settings.bailianKey.slice(-4)) : "";
    const vol = Number(settings.speakerVolume) || 70;

    this.setData({
      wifiHost: settings.wifiHost || "192.168.110.67",
      wifiHostInput: settings.wifiHost || "192.168.110.67",
      wifiSsid: settings.savedSsid || settings.wifiSsid || "",
      vibrationEnabled: settings.vibrationEnabled !== false,
      networkMode: isHs ? "hotspot" : "wifi",
      hotspotLimitMb: limit,
      selectedPreset: preset,
      customLimitInput: preset === "custom" ? String(limit) : "",
      hotspotCutoffEnabled: settings.hotspotCutoffEnabled !== false,
      hotspotWarningEnabled: settings.hotspotWarningEnabled !== false,

      bailianKey: settings.bailianKey || "",
      bailianKeyInput: settings.bailianKey || "",
      hasBailianKey: hasKey,
      maskedBailianKey: maskedKey,
      bailianModel: blModel,
      selectedModelIndex: modelIdx >= 0 ? modelIdx : 0,
      bailianVoice: blVoice,
      selectedVoiceIndex: voiceIdx >= 0 ? voiceIdx : 0,
      speakerVolume: vol,
      displayVolume: vol,
      bailianPrompt: settings.bailianPrompt || "你是StickS3智能语音伴侣，请用简明生动的口语回答，每次回答控制在两句话以内。",

      wakewordEnabled: settings.wakewordEnabled !== false,
      wakewordSensitivity: Number(settings.wakewordSensitivity) || 75,
      wakewordTimeoutSec: tout,
      selectedTimeoutIndex: toutIdx >= 0 ? toutIdx : 1
    });

    this.stateListener = (evt) => this.syncState(evt);
    buddyService.subscribe(this.stateListener);

    this._lastUserVolumeSetTime = 0;
    this._isSliding = false;
    buddyService.getSpeakerVolume().then(liveVol => {
      const now = Date.now();
      if (!this._isSliding && (!this._lastUserVolumeSetTime || (now - this._lastUserVolumeSetTime > 3500))) {
        if (liveVol !== this.data.speakerVolume) {
          this.setData({ speakerVolume: liveVol, displayVolume: liveVol });
        }
      }
    }).catch(() => {});
  },

  onShow() {
    this.syncState({
      isConnected: buddyService.isConnected,
      isBleMode: buddyService.isBleMode,
      isWifiMode: buddyService.isWifiMode,
      isSimMode: buddyService.isSimMode,
      connectionStatusText: buddyService.connectionStatusText,
      petState: buddyService.petState
    });

    buddyService.getSpeakerVolume().then(liveVol => {
      const now = Date.now();
      if (!this._isSliding && (!this._lastUserVolumeSetTime || (now - this._lastUserVolumeSetTime > 3500))) {
        if (liveVol !== this.data.speakerVolume) {
          this.setData({ speakerVolume: liveVol, displayVolume: liveVol });
        }
      }
    }).catch(() => {});
  },

  onUnload() {
    voicePreviewEngine.stop();
    if (this.stateListener) {
      buddyService.unsubscribe(this.stateListener);
    }
  },

  onPullDownRefresh() {
    setTimeout(() => wx.stopPullDownRefresh(), 400);
  },

  syncState(evt = {}) {
    const isConn = evt.isConnected !== undefined ? evt.isConnected : buddyService.isConnected;
    const isBle = evt.isBleMode !== undefined ? evt.isBleMode : buddyService.isBleMode;
    const isWifi = evt.isWifiMode !== undefined ? evt.isWifiMode : buddyService.isWifiMode;
    const isSim = evt.isSimMode !== undefined ? evt.isSimMode : buddyService.isSimMode;
    const hs = evt.hotspot || buddyService.hotspot;
    const dw = evt.type === "wifi_status" ? evt.data : buddyService.deviceWifi;

    let modeName = "未连接";
    if (isBle) modeName = "BLE 专属通道";
    else if (isWifi) modeName = hs && hs.isHotspot ? "手机热点 Wi-Fi" : "Wi-Fi 局域网";
    else if (isSim) modeName = "离线仿真";

    const used = hs ? Number(hs.usedMb || 0) : 0;
    const limit = hs && hs.limitMb > 0 ? Number(hs.limitMb) : this.data.hotspotLimitMb;
    const percent = Math.min(100, Math.round((used / (limit || 1)) * 100));

    const patch = {};
    if (this.data.isConnected !== isConn) patch.isConnected = isConn;
    if (this.data.isBleConnected !== isBle) patch.isBleConnected = isBle;
    if (this.data.isSimMode !== isSim) patch.isSimMode = isSim;

    const connText = evt.connectionStatusText || buddyService.connectionStatusText;
    if (this.data.connectionStatusText !== connText) patch.connectionStatusText = connText;
    if (this.data.currentModeName !== modeName) patch.currentModeName = modeName;

    const devName = buddyService.connectedDeviceName || this.data.connectedDeviceName || "StickS3-Buddy";
    if (this.data.connectedDeviceName !== devName) patch.connectedDeviceName = devName;

    const host = buddyService.httpClient.host;
    if (this.data.wifiHost !== host && host && host !== "192.168.110.67") patch.wifiHost = host;

    if (hs) {
      if (!this.data.hotspot || this.data.hotspot.usedMb !== hs.usedMb || this.data.hotspot.isHotspot !== hs.isHotspot || this.data.hotspot.cutoffActive !== hs.cutoffActive || this.data.hotspot.limitMb !== hs.limitMb) {
        patch.hotspot = { ...hs };
      }
      if (this.data.trafficPercent !== percent) patch.trafficPercent = percent;
    }

    const st = evt.petState || buddyService.petState;
    if (st) {
      const activePet = st.active_pet || (st.name === "Meta Jollybot" ? "jollybot" : "qiaoqiao");
      if (this.data.activePet !== activePet) patch.activePet = activePet;
      if (st.cadet_mode && this.data.cadetRenderMode !== st.cadet_mode) patch.cadetRenderMode = st.cadet_mode;
    }

    if (dw) {
      const isOnline = Boolean(dw.sta_connected || dw.sta_state === "connected");
      const ip = dw.sta_ip && dw.sta_ip !== "0.0.0.0" ? dw.sta_ip : this.data.deviceStaIp;
      const targetState = dw.sta_state || (isOnline ? "connected" : this.data.deviceStaState);

      if (this.data.deviceStaState !== targetState) patch.deviceStaState = targetState;
      if (ip && this.data.deviceStaIp !== ip) {
        patch.deviceStaIp = ip;
        patch.wifiHost = ip;
        if (!this.data.wifiHostInput) patch.wifiHostInput = ip;
      }
      if (dw.sta_ssid && this.data.deviceStaSsid !== dw.sta_ssid) patch.deviceStaSsid = dw.sta_ssid;
      if (dw.sta_rssi && this.data.deviceStaRssi !== dw.sta_rssi) patch.deviceStaRssi = dw.sta_rssi;

      const combinedWifi = isOnline || isWifi;
      if (this.data.isWifiConnected !== combinedWifi) patch.isWifiConnected = combinedWifi;
    } else {
      if (this.data.isWifiConnected !== isWifi) patch.isWifiConnected = isWifi;
    }

    // 从设备状态同步当前播音音量 (如果用户未处于手动拖拽状态且不在防回弹冷却保护期内)
    const now = Date.now();
    const isVolumeProtected = this._isSliding || (this._lastUserVolumeSetTime && (now - this._lastUserVolumeSetTime < 3500));
    if (!isVolumeProtected) {
      const curVol = (evt.petState && evt.petState.volume !== undefined)
        ? evt.petState.volume
        : (buddyService.petState && buddyService.petState.volume);
      if (curVol !== undefined && curVol !== this.data.speakerVolume) {
        patch.speakerVolume = curVol;
        patch.displayVolume = curVol;
      }
    }

    if (Object.keys(patch).length > 0) {
      this.setData(patch);
    }
  },

  // 1. BLE 扫描与连接
  handleStartBleScan() {
    if (this.data.isScanning) return;
    this.setData({ isScanning: true, devices: [] });
    haptics.vibrate("light");

    buddyService.bleClient.startScan((device) => {
      let list = [...this.data.devices];
      const idx = list.findIndex(d => d.deviceId === device.deviceId);
      if (idx >= 0) list[idx] = device;
      else list.push(device);
      list.sort((a, b) => (b.isTarget ? 1 : 0) - (a.isTarget ? 1 : 0));
      this.setData({ devices: list });
    }, (err) => {
      this.setData({ isScanning: false });
      wx.showToast({ title: (err && err.errCode === 10001) ? "请开启手机蓝牙" : "请确保蓝牙与定位已开启", icon: "none" });
    });

    setTimeout(() => {
      if (this.data.isScanning) {
        buddyService.bleClient.stopScan();
        this.setData({ isScanning: false });
        if (this.data.devices.length === 0) {
          wx.showToast({ title: "未发现 StickS3，请将设备靠近手机并通电", icon: "none" });
        }
      }
    }, 12000);
  },

  onToggleDeviceListExpanded() {
    this.setData({ isDeviceListExpanded: !this.data.isDeviceListExpanded });
    haptics.vibrate("light");
  },

  onToggleWifiFaq() {
    this.setData({ showWifiFaq: !this.data.showWifiFaq });
    haptics.vibrate("light");
  },

  handleConnectDevice(e) {
    const devId = e.currentTarget.dataset.deviceId;
    if (!devId) return;

    const selectedDev = this.data.devices.find(d => d.deviceId === devId);
    const devName = (selectedDev && (selectedDev.name || selectedDev.localName)) || "StickS3-Buddy";

    this.setData({ connectingId: devId });
    haptics.vibrate("medium");

    buddyService.connectBLE(devId, devName).then(() => {
      this.setData({ 
        connectingId: "", 
        isScanning: false,
        isDeviceListExpanded: false,
        connectedDeviceName: devName
      });
      haptics.levelUp();
      wx.showToast({ title: "BLE 连接成功！", icon: "success" });
    }).catch(() => {
      this.setData({ connectingId: "" });
      wx.showToast({ title: "连接握手失败", icon: "none" });
    });
  },

  handleDisconnectBle() {
    buddyService.disconnectBLE();
    haptics.vibrate("light");
    this.setData({ isDeviceListExpanded: true });
    wx.showToast({ title: "已断开 BLE 蓝牙", icon: "none" });
  },

  // 2. Wi-Fi / 热点配网设置
  onInputSsid(e) { this.setData({ wifiSsid: e.detail.value }); },
  onInputPwd(e)  { this.setData({ wifiPwd: e.detail.value }); },
  onToggleShowPwd() { this.setData({ showPwd: !this.data.showPwd }); },

  onSelectNetworkMode(e) {
    const mode = e.currentTarget.dataset.mode;
    if (this.data.networkMode === mode) return;
    this.setData({ networkMode: mode });
    haptics.vibrate("light");

    const isHs = (mode === "hotspot");
    StorageManager.saveSettings({ isHotspot: isHs, networkMode: mode });
    buddyService.updateHotspotConfig({
      isHotspot: isHs,
      dataLimitMb: this.data.hotspotLimitMb,
      cutoffEnabled: this.data.hotspotCutoffEnabled
    }).catch(() => {});
  },

  onSelectPreset(e) {
    const p = e.currentTarget.dataset.preset;
    haptics.vibrate("light");
    if (p === "custom") {
      this.setData({ selectedPreset: "custom", customLimitInput: String(this.data.hotspotLimitMb) });
    } else {
      const mb = Number(p);
      this.setData({ selectedPreset: mb, hotspotLimitMb: mb });
    }
  },

  onInputCustomLimit(e) {
    const raw = e.detail.value;
    const val = parseInt(raw, 10);
    this.setData({ customLimitInput: raw });
    if (!isNaN(val) && val > 0) this.setData({ hotspotLimitMb: val });
  },

  onToggleCutoff(e) {
    const val = e.detail.value;
    this.setData({ hotspotCutoffEnabled: val });
    buddyService.updateHotspotConfig({ cutoffEnabled: val, dataLimitMb: this.data.hotspotLimitMb });
    haptics.vibrate("light");
  },

  onToggleWarning(e) {
    const val = e.detail.value;
    this.setData({ hotspotWarningEnabled: val });
    StorageManager.saveSettings({ hotspotWarningEnabled: val });
    haptics.vibrate("light");
  },

  handleGetConnectedWifi() {
    wx.startWifi({
      success: () => {
        wx.getConnectedWifi({
          success: (res) => {
            if (res.wifi && res.wifi.SSID) {
              this.setData({ wifiSsid: res.wifi.SSID });
              haptics.vibrate("light");
              wx.showToast({ title: `已填入: ${res.wifi.SSID}`, icon: "none" });
            }
          },
          fail: () => wx.showToast({ title: "请手动输入 Wi-Fi 名称", icon: "none" })
        });
      },
      fail: () => wx.showToast({ title: "无法获取当前 Wi-Fi，请手动输入", icon: "none" })
    });
  },

  async handleSmartProvision() {
    const { wifiSsid, wifiPwd, networkMode, hotspotLimitMb, hotspotCutoffEnabled } = this.data;
    if (!wifiSsid || !wifiSsid.trim()) {
      wx.showToast({ title: networkMode === "hotspot" ? "请输入热点名称" : "请输入 Wi-Fi 名称", icon: "none" });
      return;
    }

    if (!buddyService.isBleMode || !buddyService.bleClient.isConnected) {
      if (!buddyService.isWifiMode && !buddyService.isSimMode) {
        wx.showModal({
          title: "请先连接设备",
          content: "智能配网需要通过 0xFFB4 蓝牙特征值安全注入凭证。请在上方先连接 StickS3-Buddy。",
          showCancel: false
        });
        return;
      }
    }

    this.setData({ isProvisioning: true, verifyProgress: "正在通过蓝牙分片写入网络凭证..." });
    haptics.vibrate("medium");
    wx.showLoading({ title: "安全分片注入中..." });

    const isHs = networkMode === "hotspot";
    try {
      await buddyService.provisionWifi({
        ssid: wifiSsid.trim(),
        password: wifiPwd,
        isHotspot: isHs,
        dataLimitMb: isHs ? hotspotLimitMb : 0,
        cutoffEnabled: hotspotCutoffEnabled
      });

      wx.hideLoading();
      StorageManager.saveSettings({
        savedSsid: wifiSsid.trim(),
        isHotspot: isHs,
        hotspotLimitMb: hotspotLimitMb,
        hotspotCutoffEnabled: hotspotCutoffEnabled
      });

      this.setData({
        isProvisioning: false,
        isVerifyingNetwork: true,
        verifyProgress: "凭证已注入Flash，设备正在连接网络...",
        deviceStaState: "connecting",
        deviceStaIp: "",
        deviceStaSsid: wifiSsid.trim()
      });

      this._pollNetworkStatus(wifiSsid.trim(), isHs);
    } catch (e) {
      wx.hideLoading();
      this.setData({ isProvisioning: false, isVerifyingNetwork: false, verifyProgress: "" });
      wx.showToast({ title: "配网下发异常，请重试", icon: "none" });
    }
  },

  async _pollNetworkStatus(ssid, isHotspot) {
    const maxAttempts = 15;
    for (let i = 0; i < maxAttempts; i++) {
      this.setData({ verifyProgress: `正在验证设备联网状态... (${i + 1}/${maxAttempts} 轮)` });
      await new Promise(r => setTimeout(r, 2000));

      try {
        const status = await buddyService.checkDeviceNetworkStatus();
        if (status && (status.sta_connected || (status.sta_state === "connected" && status.sta_ip && status.sta_ip !== "0.0.0.0"))) {
          const ip = status.sta_ip && status.sta_ip !== "0.0.0.0" ? status.sta_ip : "已获取内网IP";
          this.setData({
            isVerifyingNetwork: false,
            verifyProgress: "",
            deviceStaState: "connected",
            deviceStaIp: ip,
            deviceStaSsid: status.sta_ssid || ssid,
            deviceStaRssi: status.sta_rssi || -50,
            wifiHostInput: ip,
            wifiHost: ip,
            showLanDirectConnect: !isHotspot,
            isWifiConnected: true
          });

          if (ip !== "已获取内网IP") {
            buddyService.httpClient.setHost(ip);
            StorageManager.saveSettings({ wifiHost: ip });
          }

          haptics.levelUp();
          wx.showModal({
            title: isHotspot ? "📱 手机热点连接成功！" : "🎉 Wi-Fi 联网成功！",
            content: `StickS3 硬件已成功连入 [${status.sta_ssid || ssid}]！\n• 设备 IP: ${ip}\n• 信号强度: ${status.sta_rssi || -50} dBm\n• 硬件屏幕: ${isHotspot ? "已点亮暖橙色 HOT 标志" : "已点亮亮绿色 WiFi 标志"}`,
            showCancel: false
          });
          return;
        } else if (status && status.sta_state === "failed") {
          this.setData({ isVerifyingNetwork: false, verifyProgress: "", deviceStaState: "failed", showLanDirectConnect: false });
          wx.showModal({
            title: "❌ 设备联网失败",
            content: `StickS3 无法连接到 [${ssid}]，请检查密码与2.4GHz频段。`,
            showCancel: false
          });
          return;
        }
      } catch (e) {}
    }

    this.setData({ isVerifyingNetwork: false, verifyProgress: "", deviceStaState: "timeout" });
    wx.showModal({
      title: "⏳ 联网确认超时",
      content: "已等待30秒尚未收到设备回执。如果屏幕已显示绿色 WiFi 标志，说明已连网，可点击刷新同步。",
      showCancel: false
    });
  },

  async handleCheckDeviceNetwork() {
    haptics.vibrate("light");
    this.setData({ isVerifyingNetwork: true, verifyProgress: "正在向设备查询最新网络状态..." });

    try {
      const status = await buddyService.checkDeviceNetworkStatus();
      if (status && (status.sta_connected || (status.sta_state === "connected" && status.sta_ip && status.sta_ip !== "0.0.0.0"))) {
        const ip = status.sta_ip && status.sta_ip !== "0.0.0.0" ? status.sta_ip : "已获取内网IP";
        this.setData({
          isVerifyingNetwork: false,
          verifyProgress: "",
          deviceStaState: "connected",
          deviceStaIp: ip,
          deviceStaSsid: status.sta_ssid || this.data.wifiSsid,
          deviceStaRssi: status.sta_rssi || -50,
          wifiHostInput: ip,
          wifiHost: ip,
          isWifiConnected: true
        });
        if (ip !== "已获取内网IP") {
          buddyService.httpClient.setHost(ip);
          StorageManager.saveSettings({ wifiHost: ip });
        }
        haptics.vibrate("medium");
        wx.showToast({ title: `设备已在线! IP: ${ip}`, icon: "success" });
      } else {
        this.setData({ isVerifyingNetwork: false, verifyProgress: "", deviceStaState: (status && status.sta_state) || "failed" });
        wx.showToast({ title: "设备当前未联网", icon: "none" });
      }
    } catch (e) {
      this.setData({ isVerifyingNetwork: false, verifyProgress: "" });
      wx.showToast({ title: "查询失败，请检查BLE", icon: "none" });
    }
  },

  async handleRefreshTraffic() {
    haptics.vibrate("light");
    wx.showLoading({ title: "刷新流量中..." });
    try {
      await buddyService.fetchHotspotTraffic();
      wx.hideLoading();
      wx.showToast({ title: "流量已刷新", icon: "success" });
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: "刷新失败", icon: "none" });
    }
  },

  async handleAddQuota() {
    const currentLimit = this.data.hotspot.limitMb || this.data.hotspotLimitMb || 100;
    const newLimit = currentLimit + 50;
    haptics.vibrate("medium");

    try {
      await buddyService.updateHotspotConfig({
        isHotspot: true,
        dataLimitMb: newLimit,
        cutoffEnabled: this.data.hotspotCutoffEnabled
      });
      this.setData({
        hotspotLimitMb: newLimit,
        selectedPreset: "custom",
        customLimitInput: String(newLimit)
      });
      haptics.levelUp();
      wx.showToast({ title: `已追加 50MB (新上限: ${newLimit}MB)`, icon: "none" });
    } catch (e) {
      wx.showToast({ title: "配额更新失败", icon: "none" });
    }
  },

  handleResetTraffic() {
    wx.showModal({
      title: "重置流量统计",
      content: "确定要将 StickS3 设备上的手机热点流量使用计数重置为 0 MB 吗？",
      confirmText: "确定重置",
      confirmColor: "#ef4444",
      success: async (res) => {
        if (res.confirm) {
          haptics.vibrate("medium");
          try {
            await buddyService.resetHotspotTraffic();
            wx.showToast({ title: "流量已清零", icon: "success" });
          } catch (e) {
            wx.showToast({ title: "重置失败", icon: "none" });
          }
        }
      }
    });
  },

  onInputHost(e) { this.setData({ wifiHostInput: e.detail.value }); },

  async handleTestWifiConnection() {
    const host = this.data.wifiHostInput.trim();
    if (!host) {
      wx.showToast({ title: "请输入目标 IP", icon: "none" });
      return;
    }

    this.setData({ isTestingWifi: true });
    haptics.vibrate("light");

    try {
      buddyService.httpClient.setHost(host);
      const res = await buddyService.httpClient.getPetStatus();
      this.setData({ isTestingWifi: false, wifiHost: host });
      StorageManager.saveSettings({ wifiHost: host });
      haptics.vibrate("medium");
      wx.showToast({ title: `连通正常! Lv.${res.level || 1}`, icon: "success" });
    } catch (e) {
      this.setData({ isTestingWifi: false });
      wx.showModal({
        title: "连通性测试未通过",
        content: `无法在局域网内访问 http://${host}/pet/status。请确保手机与 StickS3 在同一 Wi-Fi 下。`,
        showCancel: false
      });
    }
  },

  handleToggleWifiConnection() {
    if (this.data.isWifiConnected) {
      buddyService.disconnectWifi();
      wx.showToast({ title: "已断开 Wi-Fi 通道", icon: "none" });
    } else {
      const host = this.data.wifiHostInput.trim();
      buddyService.connectWifi(host).then(() => {
        haptics.levelUp();
        wx.showToast({ title: "Wi-Fi 直连成功", icon: "success" });
      }).catch(() => {
        wx.showToast({ title: "Wi-Fi 连接失败", icon: "none" });
      });
    }
  },

  onToggleVibration(e) {
    const val = e.detail.value;
    this.setData({ vibrationEnabled: val });
    haptics.setEnabled(val);
    StorageManager.saveSettings({ vibrationEnabled: val });
    if (val) haptics.vibrate("medium");
  },

  handleToggleAvatarMode() {
    haptics.vibrate("light");
    buddyService.dispatchAction("toggle_mode").then(() => {
      wx.showToast({ title: "已下发屏显切换指令", icon: "none" });
    }).catch(() => {
      wx.showToast({ title: "下发失败", icon: "none" });
    });
  },

  handleClearStorage() {
    wx.showModal({
      title: "清除离线日记缓存",
      content: "确定要清空手机本地沉淀的全部灵宠心声日记与对话记忆吗？",
      confirmText: "清空",
      confirmColor: "#ef4444",
      success: (res) => {
        if (res.confirm) {
          StorageManager.clearAllDiaries();
          haptics.vibrate("medium");
          wx.showToast({ title: "已清空本地日记", icon: "none" });
        }
      }
    });
  },

  // 3. 阿里云百炼大模型交互设置
  onInputBailianKey(e) {
    const val = e.detail.value;
    this.setData({
      bailianKeyInput: val,
      hasBailianKey: val.trim().length > 10,
      maskedBailianKey: val.trim().length > 10 ? (val.trim().substring(0, 4) + "••••••••" + val.trim().slice(-4)) : ""
    });
  },

  onToggleShowBailianKey() {
    this.setData({ showBailianKey: !this.data.showBailianKey });
    haptics.vibrate("light");
  },

  onModelChange(e) {
    const idx = Number(e.detail.value);
    const model = this.data.modelOptions[idx];
    if (model) {
      this.setData({ selectedModelIndex: idx, bailianModel: model.id });
      haptics.vibrate("light");
    }
  },

  onVoiceChange(e) {
    const idx = Number(e.detail.value);
    const voice = this.data.voiceOptions[idx];
    if (voice) {
      this.setData({ selectedVoiceIndex: idx, bailianVoice: voice.id });
      haptics.vibrate("light");
    }
  },

  onInputPrompt(e) { this.setData({ bailianPrompt: e.detail.value }); },

  handleApplyPromptPreset(e) {
    const preset = e.currentTarget.dataset.prompt;
    if (preset) {
      this.setData({ bailianPrompt: preset });
      haptics.vibrate("medium");
      wx.showToast({ title: "已填入预设人格", icon: "none" });
    }
  },

  async handleSaveBailianConfig() {
    const key = this.data.bailianKeyInput.trim();
    const model = this.data.bailianModel;
    const voice = this.data.bailianVoice;
    const prompt = this.data.bailianPrompt.trim();
    const volume = this.data.speakerVolume;

    if (!key && !this.data.bailianKey) {
      wx.showToast({ title: "请输入百炼 API Key", icon: "none" });
      return;
    }

    this.setData({ isSavingBailian: true });
    haptics.vibrate("light");

    try {
      await buddyService.setBailianConfig({
        key: key || this.data.bailianKey,
        model,
        voice,
        prompt,
        volume
      });
      this.setData({
        isSavingBailian: false,
        bailianKey: key || this.data.bailianKey,
        hasBailianKey: true
      });
      haptics.levelUp();
      wx.showToast({ title: "大模型与音量配置已生效", icon: "success" });
    } catch (e) {
      this.setData({ isSavingBailian: false });
      wx.showModal({
        title: "配置写入失败",
        content: e.message || "无法写入配置，请确保已连接 StickS3 设备",
        showCancel: false
      });
    }
  },

  async handlePreviewVoice() {
    const voice = this.data.bailianVoice;
    if (this.data.isPreviewingVoice) {
      voicePreviewEngine.stop();
      this.setData({ isPreviewingVoice: false });
      return;
    }

    this.setData({ isPreviewingVoice: true });
    haptics.vibrate("medium");

    voicePreviewEngine.playPreview(voice, () => {
      this.setData({ isPreviewingVoice: false });
    });

    try {
      const res = await buddyService.previewVoice(voice);
      if (res && res.deviceTriggered) {
        wx.showToast({ title: `正在试听: ${voice} (双端发声)`, icon: "none", duration: 1800 });
      } else {
        wx.showToast({ title: `正在试听: ${voice} (手机发声)`, icon: "none", duration: 1800 });
      }
    } catch (e) {
      wx.showToast({ title: `正在试听: ${voice}`, icon: "none", duration: 1500 });
    }
  },

  onVolumeChanging(e) {
    this._isSliding = true;
    this._lastUserVolumeSetTime = Date.now();
    const val = parseInt(e.detail.value, 10);
    if (!isNaN(val) && (val !== this.data.displayVolume || val !== this.data.speakerVolume)) {
      this.setData({ displayVolume: val, speakerVolume: val });
    }
  },

  async onVolumeChange(e) {
    this._isSliding = false;
    this._lastUserVolumeSetTime = Date.now();
    const val = parseInt(e.detail.value, 10);
    if (isNaN(val)) return;
    this.setData({ speakerVolume: val, displayVolume: val });
    haptics.selection();

    try {
      const res = await buddyService.setSpeakerVolume(val);
      if (res && res.deviceTriggered) {
        wx.showToast({ title: `🔊 设备音量: ${val}%`, icon: "none", duration: 1000 });
      } else {
        wx.showToast({
          title: `⚠️ 已设为 ${val}% (设备离线未同步)`,
          icon: "none",
          duration: 1500
        });
      }
    } catch (err) {
      wx.showToast({ title: `❌ 音量同步失败: ${err.message || "网络异常"}`, icon: "none", duration: 1500 });
    }
  },

  handleSetVolumePreset(e) {
    const val = parseInt(e.currentTarget.dataset.volume, 10);
    if (isNaN(val)) return;
    this._lastUserVolumeSetTime = Date.now();
    this.setData({ speakerVolume: val, displayVolume: val });
    haptics.selection();
    buddyService.setSpeakerVolume(val).then((res) => {
      if (res && res.deviceTriggered) {
        wx.showToast({ title: `🔊 设备音量: ${val}%`, icon: "none", duration: 1000 });
      }
    }).catch(() => {});
  },

  async handleTestVolume() {
    this._lastUserVolumeSetTime = Date.now();
    const vol = this.data.displayVolume || this.data.speakerVolume || 70;
    haptics.vibrate("medium");

    // 1. 手机端 WebAudio 零延迟立即和弦发声试听
    voicePreviewEngine.playVolumeChime(vol);

    // 2. 硬件设备端和弦发声试听 (并发下发，绝无阻塞)
    try {
      const res = await buddyService.testSpeakerVolume(vol);
      if (res && res.deviceTriggered) {
        wx.showToast({ title: `🔊 设备正在以 ${vol}% 试听发声`, icon: "none", duration: 1200 });
      } else {
        wx.showToast({ title: `🔊 正在试听 ${vol}% 音量 (手机发声)`, icon: "none", duration: 1200 });
      }
    } catch (e) {
      wx.showToast({ title: `🔊 正在试听 ${vol}% 音量 (手机发声)`, icon: "none", duration: 1200 });
    }
  },

  // 4. 离线唤醒词配置
  onToggleWakeword(e) {
    const val = e.detail.value;
    this.setData({ wakewordEnabled: val });
    haptics.vibrate("light");
  },

  onWakewordSensitivityChange(e) {
    this.setData({ wakewordSensitivity: Number(e.detail.value) });
  },

  onTimeoutChange(e) {
    const idx = Number(e.detail.value);
    const tout = this.data.timeoutOptions[idx];
    if (tout !== undefined) {
      this.setData({ selectedTimeoutIndex: idx, wakewordTimeoutSec: tout });
      haptics.vibrate("light");
    }
  },

  async handleSaveWakewordConfig() {
    this.setData({ isSavingWakeword: true });
    haptics.vibrate("light");

    try {
      await buddyService.setWakewordConfig({
        enabled: this.data.wakewordEnabled,
        sensitivity: this.data.wakewordSensitivity,
        timeoutSec: this.data.wakewordTimeoutSec
      });
      this.setData({ isSavingWakeword: false });
      haptics.levelUp();
      wx.showToast({ title: "唤醒词配置已保存", icon: "success" });
    } catch (e) {
      this.setData({ isSavingWakeword: false });
      wx.showModal({
        title: "唤醒词配置失败",
        content: e.message || "请确保已连接 StickS3 设备",
        showCancel: false
      });
    }
  },

  async handleTriggerWakeSim() {
    this.setData({ isTriggeringWake: true });
    haptics.vibrate("medium");

    try {
      await buddyService.triggerWakeSim(98.0);
      this.setData({ isTriggeringWake: false });
      wx.showToast({ title: "唤醒模拟成功！", icon: "success" });
    } catch (e) {
      this.setData({ isTriggeringWake: false });
      wx.showToast({ title: e.message || "模拟失败，请先连接伴侣", icon: "none" });
    }
  },

  // 5. 设备运维与重置
  handleClearDeviceMemory() {
    wx.showModal({
      title: "清空设备对话记忆",
      content: "确定要抹除 StickS3 硬件端保存的全部多轮对话记忆与心声回忆吗？此操作无法撤销。",
      confirmText: "确定清空",
      confirmColor: "#ef4444",
      success: async (res) => {
        if (res.confirm) {
          this.setData({ isClearingMemory: true });
          haptics.vibrate("medium");
          try {
            await buddyService.clearDeviceMemory();
            this.setData({ isClearingMemory: false });
            wx.showToast({ title: "硬件记忆已清空", icon: "success" });
          } catch (e) {
            this.setData({ isClearingMemory: false });
            wx.showToast({ title: "清空失败", icon: "none" });
          }
        }
      }
    });
  },

  handleDeviceReboot() {
    wx.showModal({
      title: "软重启设备",
      content: "即将向 StickS3 发送软重启指令，系统将在 300 毫秒后重新初始化。",
      confirmText: "立即重启",
      confirmColor: "#0A84FF",
      success: async (res) => {
        if (res.confirm) {
          this.setData({ isRebootingDevice: true });
          haptics.vibrate("medium");
          try {
            await buddyService.rebootDevice();
            setTimeout(() => {
              this.setData({ isRebootingDevice: false });
              wx.showToast({ title: "已下发重启指令", icon: "none" });
            }, 600);
          } catch (e) {
            this.setData({ isRebootingDevice: false });
            wx.showToast({ title: e.message || "重启指令下发失败", icon: "none" });
          }
        }
      }
    });
  },

  handleDeviceFactoryReset() {
    wx.showModal({
      title: "⚠️ 恢复出厂设置确认",
      content: "此操作将彻底抹除设备上的全部配置、Wi-Fi密码与记忆，并重启设备。确定要继续吗？",
      confirmText: "彻底清除",
      confirmColor: "#ef4444",
      success: (res1) => {
        if (res1.confirm) {
          wx.showModal({
            title: "二次确认 · 无法撤销",
            content: "恢复出厂后需要重新通过蓝牙配网。是否立即执行？",
            confirmText: "确认出厂重置",
            confirmColor: "#ef4444",
            success: async (res2) => {
              if (res2.confirm) {
                this.setData({ isFactoryResetting: true });
                haptics.vibrate("heavy");
                try {
                  await buddyService.factoryResetDevice();
                  this.setData({
                    isFactoryResetting: false,
                    bailianKey: "",
                    bailianKeyInput: "",
                    hasBailianKey: false,
                    maskedBailianKey: "",
                    wifiSsid: "",
                    wifiPwd: "",
                    deviceStaState: "",
                    deviceStaIp: ""
                  });
                  wx.showToast({ title: "设备已恢复出厂并重启", icon: "none", duration: 3000 });
                } catch (e) {
                  this.setData({ isFactoryResetting: false });
                  wx.showToast({ title: e.message || "出厂重置失败", icon: "none" });
                }
              }
            }
          });
        }
      }
    });
  },

  // 伴侣类型与功夫学徒渲染设置切换
  handleTogglePetTypeSettings() {
    haptics.selection();
    const nextPet = (this.data.activePet === "jollybot") ? "qiaoqiao" : "jollybot";
    this.setData({ activePet: nextPet });
    buddyService.setPetType(nextPet);
    wx.showToast({
      title: nextPet === "jollybot" ? "🥋 已切换为功夫学徒阿韧" : "🌸 已切换为灵伴悄悄",
      icon: "none"
    });
  },

  handleToggleCadetModeSettings() {
    haptics.selection();
    const nextMode = (this.data.cadetRenderMode === "fullcolor") ? "lineart" : "fullcolor";
    this.setData({ cadetRenderMode: nextMode });
    buddyService.setCadetRenderMode(nextMode);
    wx.showToast({
      title: nextMode === "fullcolor" ? "🎨 已切换为全色域彩绘" : "✍️ 已切换为象牙金微雕",
      icon: "none"
    });
  }
});
