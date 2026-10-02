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
    this.setData({
      wifiHost: settings.wifiHost || "192.168.110.67",
      wifiHostInput: settings.wifiHost || "192.168.110.67",
      wifiSsid: settings.savedSsid || "",
      vibrationEnabled: settings.vibrationEnabled !== false
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

    let modeName = "未连接";
    if (isBle) modeName = "BLE 专属通道";
    else if (isWifi) modeName = "Wi-Fi 局域网";
    else if (isSim) modeName = "离线仿真";

    this.setData({
      isConnected: isConn,
      isBleConnected: isBle,
      isWifiConnected: isWifi,
      isSimMode: isSim,
      connectionStatusText: evt.connectionStatusText || buddyService.connectionStatusText,
      currentModeName: modeName,
      petState: evt.petState || buddyService.petState,
      wifiHost: buddyService.httpClient.host
    });
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

  // 2. BLE 一键智能配网 (Smart Provisioning)
  onInputSsid(e) { this.setData({ wifiSsid: e.detail.value }); },
  onInputPwd(e)  { this.setData({ wifiPwd: e.detail.value }); },

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
    const { wifiSsid, wifiPwd } = this.data;
    if (!wifiSsid || !wifiSsid.trim()) {
      wx.showToast({ title: "请输入 Wi-Fi 名称", icon: "none" });
      return;
    }

    if (!buddyService.isBleMode || !buddyService.bleClient.isConnected) {
      wx.showModal({
        title: "需要先连接 BLE 蓝牙",
        content: "智能配网需要通过 0xFFB4 蓝牙特征值安全注入凭证。请先在上方连接 StickS3-Buddy。",
        showCancel: false
      });
      return;
    }

    this.setData({ isProvisioning: true });
    haptics.vibrate("medium");

    wx.showLoading({ title: "20字节安全分片注入中..." });

    try {
      await buddyService.provisionWifi(wifiSsid.trim(), wifiPwd);
      wx.hideLoading();
      this.setData({ isProvisioning: false });

      // 保存已配网 SSID
      StorageManager.saveSettings({ savedSsid: wifiSsid.trim() });

      haptics.levelUp();
      wx.showModal({
        title: "配网凭据已下发",
        content: `Wi-Fi [${wifiSsid}] 凭据已通过 20 字节安全切片写入 StickS3 固件。设备将自动连网，连网后可通过局域网 IP 高速直连。`,
        showCancel: false
      });
    } catch (e) {
      wx.hideLoading();
      this.setData({ isProvisioning: false });
      wx.showToast({ title: "配网下发异常，请重试", icon: "none" });
    }
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
