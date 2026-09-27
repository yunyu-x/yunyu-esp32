// app.js
App({
  globalData: {
    deviceName: "StickS3-Buddy",
    petName: "小木",
    connectedDevice: null,
    isBleConnected: false,
    isWifiConnected: false,
    wifiHost: "192.168.110.67"
  },
  onLaunch() {
    console.log("[LingBuddy App] Launched successfully.");
  }
});
