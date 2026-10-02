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
    connectingId: "",
    isProvisioning: false,
    isTestingWifi: false,

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

  syncState(evt) {
    const isConn = evt.isConnected !== undefined ? evt.isConnected : buddyService.isConnected;
    const isBle = evt.isBleMode !== undefined ? evt.isBleMode : buddyService.isBleMode;
    const isWifi = evt.isWifiMode !== undefined ? evt.isWifiMode : buddyService.isWifiMode;
    const isSim = evt.isSimMode !== undefined ? evt.isSimMode : buddyService.isSimMode;
    const hs = evt.hotspot || buddyService.hotspot;

    let modeName = "未连接";
    if (isBle) modeName = "BLE 专属通道";
    else if (isWifi) modeName = hs && hs.isHotspot ? "手机热点 Wi-Fi" : "Wi-Fi 局域网";
    else if (isSim) modeName = "离线仿真";

    const used = hs ? Number(hs.usedMb || 0) : 0;
    const limit = hs && hs.limitMb > 0 ? Number(hs.limitMb) : this.data.hotspotLimitMb;
    const percent = Math.min(100, Math.round((used / (limit || 1)) * 100));

    this.setData({
      isConnected: isConn,
      isBleConnected: isBle,
      isWifiConnected: isWifi,
      isSimMode: isSim,
      connectionStatusText: evt.connectionStatusText || buddyService.connectionStatusText,
      currentModeName: modeName,
      petState: evt.petState || buddyService.petState,
      wifiHost: buddyService.httpClient.host,
      hotspot: hs || this.data.hotspot,
      trafficPercent: percent
    });

    if (hs && hs.isHotspot && this.data.networkMode !== "hotspot") {
      this.setData({ networkMode: "hotspot" });
    }
  },

  // 1. BLE 扫描
  handleStartBleScan() {
    if (this.data.isScanning) return;
    this.setData({ isScanning: true, devices: [] });
    haptics.vibrate("light");

    buddyService.bleClient.startScan((device) => {
      const list = this.data.devices;
      if (!list.some(d => d.deviceId === device.deviceId)) {
        list.push(device);
        this.setData({ devices: list });
      }
    }, (err) => {
      this.setData({ isScanning: false });
      wx.showToast({ title: "请确保手机蓝牙已开启", icon: "none" });
    });

    // 扫描 8 秒后自动结束
    setTimeout(() => {
      if (this.data.isScanning) {
        buddyService.bleClient.stopScan();
        this.setData({ isScanning: false });
        if (this.data.devices.length === 0) {
          wx.showToast({ title: "未发现 StickS3，请将设备靠近手机", icon: "none" });
        }
      }
    }, 8000);
  },

  // 连接选定 BLE 设备
  handleConnectDevice(e) {
    const devId = e.currentTarget.dataset.deviceId;
    if (!devId) return;

    this.setData({ connectingId: devId });
    haptics.vibrate("medium");

    buddyService.connectBLE(devId).then(() => {
      this.setData({ connectingId: "", isScanning: false });
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
    wx.showToast({ title: "已断开 BLE 蓝牙", icon: "none" });
  },

  // 2. Wi-Fi / 手机热点智能配网与流量保护交互
  onInputSsid(e) { this.setData({ wifiSsid: e.detail.value }); },
  onInputPwd(e)  { this.setData({ wifiPwd: e.detail.value }); },
  onToggleShowPwd() { this.setData({ showPwd: !this.data.showPwd }); },

  onSelectNetworkMode(e) {
    const mode = e.currentTarget.dataset.mode;
    this.setData({ networkMode: mode });
    haptics.vibrate("light");
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

    this.setData({ isProvisioning: true });
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
      this.setData({ isProvisioning: false });
      StorageManager.saveSettings({
        savedSsid: wifiSsid.trim(),
        isHotspot: isHs,
        hotspotLimitMb: hotspotLimitMb,
        hotspotCutoffEnabled: hotspotCutoffEnabled
      });

      haptics.levelUp();
      wx.showModal({
        title: isHs ? "📱 移动热点凭证已下发" : "🏠 Wi-Fi 凭据已下发",
        content: `网络 [${wifiSsid}] 已通过 20 字节安全切片写入设备。${isHs ? `已启用流量上限: ${hotspotLimitMb}MB，超额自动熔断保护: ${hotspotCutoffEnabled ? "开启" : "关闭"}。` : "设备将自动连网，连网后可通过局域网 IP 高速直连。"}`,
        showCancel: false
      });
    } catch (e) {
      wx.hideLoading();
      this.setData({ isProvisioning: false });
      wx.showToast({ title: "配网下发异常，请重试", icon: "none" });
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
