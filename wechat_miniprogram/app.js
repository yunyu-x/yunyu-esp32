// app.js
const { buddyService } = require("./utils/buddy_service.js");
const { StorageManager } = require("./utils/storage_manager.js");
const { haptics } = require("./utils/haptics.js");

App({
  globalData: {
    deviceName: "StickS3-Buddy",
    petName: "悄悄",
    wifiHost: "192.168.110.67"
  },
  buddyService,
  storageManager: StorageManager,
  haptics,
  onLaunch() {
    console.log("[LingBuddy App] Launched successfully with 4-Tab Architecture & Embodied Haptics.");
  }
});
