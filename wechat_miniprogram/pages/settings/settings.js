// pages/settings/settings.js
const { buddyService } = require("../../utils/buddy_service.js");
const { StorageManager } = require("../../utils/storage_manager.js");
const { haptics } = require("../../utils/haptics.js");

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

    networkMode: "wifi", // 'wifi' | 'hotspot'
    selectedPreset: 100, // 50 | 100 | 200 | 500 | 'custom'
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

    petState: {
      level: 1
    },

    isScanning: false,
    devices: [],
    isDeviceListExpanded: false,
    connectedDeviceName: "StickS3-Buddy",
    showWifiFaq: false,
    connectingId: "",
    isProvisioning: false,
    isTestingWifi: false,

    // 配网后验证设备联网状态
    isVerifyingNetwork: false,
    verifyProgress: '',
    deviceStaState: '',
    deviceStaIp: '',
    deviceStaSsid: '',
    deviceStaRssi: 0,
    showLanDirectConnect: false,

    vibrationEnabled: true
  },

  onLoad() {
    const settings = StorageManager.getSettings();
    const isHs = Boolean(settings.isHotspot);
    const limit = Number(settings.hotspotLimitMb) || 100;
    const preset = [50, 100, 200, 500].includes(limit) ? limit : "custom";

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
      hotspotWarningEnabled: settings.hotspotWarningEnabled !== false
    });

    this.stateListener = (evt) => {
      this.syncState(evt);
    };
    buddyService.subscribe(this.stateListener);
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
  },

  onUnload() {
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

    // 合并批量 Patch，杜绝单帧多次调用 setData 引发全屏重绘频闪
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

    // 热点数据
    if (hs) {
      if (!this.data.hotspot || this.data.hotspot.usedMb !== hs.usedMb || this.data.hotspot.isHotspot !== hs.isHotspot || this.data.hotspot.cutoffActive !== hs.cutoffActive || this.data.hotspot.limitMb !== hs.limitMb) {
        patch.hotspot = { ...hs };
      }
      if (this.data.trafficPercent !== percent) patch.trafficPercent = percent;
    }

    // 硬件 Wi-Fi STA 联网状态
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

    if (Object.keys(patch).length > 0) {
      this.setData(patch);
    }
  },

  // 1. BLE 扫描
  handleStartBleScan() {
    if (this.data.isScanning) return;
    this.setData({ isScanning: true, devices: [] });
    haptics.vibrate("light");

    buddyService.bleClient.startScan((device) => {
      let list = [...this.data.devices];
      const idx = list.findIndex(d => d.deviceId === device.deviceId);
      if (idx >= 0) {
        list[idx] = device;
      } else {
        list.push(device);
      }
      // 优先将 StickS3 伴侣排在最前面
      list.sort((a, b) => (b.isTarget ? 1 : 0) - (a.isTarget ? 1 : 0));
      this.setData({ devices: list });
    }, (err) => {
      this.setData({ isScanning: false });
      let errMsg = "请确保手机蓝牙及定位已开启";
      if (err && err.errCode === 10001) {
        errMsg = "请在手机系统设置中开启蓝牙";
      }
      wx.showToast({ title: errMsg, icon: "none" });
    });

    // 扫描 12 秒后自动结束
    setTimeout(() => {
      if (this.data.isScanning) {
        buddyService.bleClient.stopScan();
        this.setData({ isScanning: false });
        if (this.data.devices.length === 0) {
          wx.showToast({ title: "未发现 StickS3，请将设备靠近手机并确保通电", icon: "none" });
        }
      }
    }, 12000);
  },

  // 切换扫描设备列表展开/折叠
  onToggleDeviceListExpanded() {
    this.setData({ isDeviceListExpanded: !this.data.isDeviceListExpanded });
    haptics.vibrate("light");
  },

  // 切换 Wi-Fi 配网避坑常见指南展开/折叠
  onToggleWifiFaq() {
    this.setData({ showWifiFaq: !this.data.showWifiFaq });
    haptics.vibrate("light");
  },

  // 连接选定 BLE 设备
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
        isDeviceListExpanded: false, // 连接成功后自动收起设备列表，保持界面清爽
        connectedDeviceName: devName
      });
      haptics.levelUp();
      wx.showToast({ title: "BLE 连接成功！", icon: "success" });
    }).catch(err => {
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

  // 2. Wi-Fi / 手机热点智能配网与流量保护交互
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
    }).then(() => {
      console.log(`[NETWORK-MODE] Synced mode '${mode}' (isHotspot=${isHs}) to device`);
    }).catch(err => {
      console.warn("[NETWORK-MODE] Sync mode failed:", err);
    });
  },

  onSelectPreset(e) {
    const p = e.currentTarget.dataset.preset;
    haptics.vibrate("light");
    if (p === "custom") {
      this.setData({
        selectedPreset: "custom",
        customLimitInput: String(this.data.hotspotLimitMb)
      });
    } else {
      const mb = Number(p);
      this.setData({
        selectedPreset: mb,
        hotspotLimitMb: mb
      });
    }
  },

  onInputCustomLimit(e) {
    const raw = e.detail.value;
    const val = parseInt(raw, 10);
    this.setData({ customLimitInput: raw });
    if (!isNaN(val) && val > 0) {
      this.setData({ hotspotLimitMb: val });
    }
  },

  onToggleCutoff(e) {
    const val = e.detail.value;
    this.setData({ hotspotCutoffEnabled: val });
    buddyService.updateHotspotConfig({
      cutoffEnabled: val,
      dataLimitMb: this.data.hotspotLimitMb
    });
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
          fail: () => {
            wx.showToast({ title: "请手动输入 Wi-Fi 名称", icon: "none" });
          }
        });
      },
      fail: () => {
        wx.showToast({ title: "无法获取当前 Wi-Fi，请手动输入", icon: "none" });
      }
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

    this.setData({
      isProvisioning: true,
      verifyProgress: "正在通过蓝牙分片写入网络凭证..."
    });
    haptics.vibrate("medium");
    wx.showLoading({ title: "20字节安全分片注入中..." });

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

      // 凭证写入成功，自动切入设备连网状态轮询阶段
      this.setData({
        isProvisioning: false,
        isVerifyingNetwork: true,
        verifyProgress: "凭证已注入Flash，设备正在连接网络...",
        deviceStaState: "connecting",
        deviceStaIp: "",
        deviceStaSsid: wifiSsid.trim()
      });

      haptics.vibrate("light");

      // 启动异步轮询校验设备是否连网成功
      this._pollNetworkStatus(wifiSsid.trim(), isHs);

    } catch (e) {
      wx.hideLoading();
      this.setData({ isProvisioning: false, isVerifyingNetwork: false, verifyProgress: "" });
      wx.showToast({ title: "配网下发异常，请重试", icon: "none" });
    }
  },

  // 轮询验证设备连网状态
  async _pollNetworkStatus(ssid, isHotspot) {
    const maxAttempts = 15;
    const intervalMs = 2000;

    for (let i = 0; i < maxAttempts; i++) {
      this.setData({
        verifyProgress: `正在验证设备联网状态... (${i + 1}/${maxAttempts} 轮)`
      });

      await new Promise(r => setTimeout(r, intervalMs));

      try {
        const status = await buddyService.checkDeviceNetworkStatus();
        if (status && (status.sta_connected || (status.sta_state === "connected" && status.sta_ip && status.sta_ip !== "0.0.0.0"))) {
          // 设备联网成功！
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
            content: `StickS3 硬件已成功连入 [${status.sta_ssid || ssid}]！\n• 设备 IP: ${ip}\n• 信号强度: ${status.sta_rssi || -50} dBm\n• 硬件屏幕: ${isHotspot ? "已点亮暖橙色 HOT 热点标志" : "已点亮亮绿色 WiFi 宽带标志"}\n\n${isHotspot ? "设备现已就绪，可直接对硬件说「悄悄」开启大模型语音对话！" : "可直接点击下方「直连局域网通道」建立高速全双工连接。"}`,
            showCancel: false
          });
          return;
        } else if (status && status.sta_state === "failed") {
          this.setData({
            isVerifyingNetwork: false,
            verifyProgress: "",
            deviceStaState: "failed",
            showLanDirectConnect: false
          });
          wx.showModal({
            title: "❌ 设备联网失败",
            content: `StickS3 无法连接到 [${ssid}]。\n\n请排查：\n1. 手机热点是否开启，且名称/密码输入正确\n2. 苹果 iPhone 需开启「最大化兼容性」\n3. 安卓手机需确保热点频段为「2.4GHz」\n4. 确认设备与手机距离在 3 米以内`,
            showCancel: false
          });
          return;
        }
      } catch (e) {
        // 继续轮询
      }
    }

    // 轮询超时
    this.setData({
      isVerifyingNetwork: false,
      verifyProgress: "",
      deviceStaState: "timeout"
    });
    wx.showModal({
      title: "⏳ 联网确认超时",
      content: `已等待 30 秒尚未收到设备联网回执。\n\n• 如果设备屏幕右上角已亮起绿色 Wi-Fi 标志，说明已经联网成功，可点击下方「刷新」按钮同步状态。\n• 如果设备屏幕 Wi-Fi 标志依然为红色，请检查热点或 Wi-Fi 密码。`,
      showCancel: false
    });
  },

  // 手动检测刷新设备网络状态
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
        this.setData({
          isVerifyingNetwork: false,
          verifyProgress: "",
          deviceStaState: (status && status.sta_state) || "failed"
        });
        wx.showToast({ title: "设备当前未联网", icon: "none" });
      }
    } catch (e) {
      this.setData({ isVerifyingNetwork: false, verifyProgress: "" });
      wx.showToast({ title: "查询失败，请检查BLE", icon: "none" });
    }
  },

  // 手机热点流量看板操作
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
      wx.showToast({ title: `已成功追加 50MB (新上限: ${newLimit}MB)`, icon: "none" });
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

  // 3. Wi-Fi 局域网高速通道配置
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
        content: `无法在局域网内访问 http://${host}/pet/status。请确保手机与 StickS3 在同一 Wi-Fi 下，且已在微信开发者工具或真机中允许局域网权限。`,
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

  // 4. 偏好与系统设置
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
  }
});
