/**
 * wechat_miniprogram/utils/sticks3_wifi.js
 * ----------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序局域网通信客户端
 * - 针对微信小程序的本地局域网限制进行了专门适配
 * - 支持 mDNS LocalServiceDiscovery 自动寻址与手动局域网 IP 指定
 * - 提供完整的拓麻歌子互动 RESTful API (隔空投喂、舒适梳毛、默契击掌、摸摸头)
 */

class StickS3HttpClient {
  constructor(defaultHost = "192.168.110.67") {
    this.host = defaultHost;
    this.isDiscoveryRunning = false;
  }

  setHost(host) {
    if (host && host.trim().length > 0) {
      this.host = host.trim();
    }
  }

  // 1. 查询灵宠实时状态与亲密值
  getPetStatus() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/pet/status`,
        method: "GET",
        timeout: 4000,
        enableHttp2: false,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`HTTP Status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] getPetStatus failed:", err);
          reject(err);
        }
      });
    });
  }

  // 2. 下发拓麻歌子互动指令 (隔空投喂 / 梳毛 / 击掌 / 抚摸 / 模式切换)
  sendPetAction(action, item = "") {
    return new Promise((resolve, reject) => {
      let data = `action=${encodeURIComponent(action)}`;
      if (item) {
        data += `&item=${encodeURIComponent(item)}`;
      }

      wx.request({
        url: `http://${this.host}/pet/action`,
        method: "POST",
        header: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        data: data,
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Action failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error(`[HTTP] sendPetAction (${action}) failed:`, err);
          reject(err);
        }
      });
    });
  }

  // 3. Wi-Fi / 手机热点一键配网连接 (POST /wifi/connect)
  connectWifiNetwork({ ssid, password, isHotspot = false, limitMb = 100, cutoff = true }) {
    return new Promise((resolve, reject) => {
      const data = `ssid=${encodeURIComponent(ssid)}&pass=${encodeURIComponent(password || "")}&is_hotspot=${isHotspot ? "1" : "0"}&limit_mb=${limitMb}&cutoff=${cutoff ? "1" : "0"}`;
      wx.request({
        url: `http://${this.host}/wifi/connect`,
        method: "POST",
        header: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        data: data,
        timeout: 5000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Connect failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] connectWifiNetwork failed:", err);
          reject(err);
        }
      });
    });
  }

  // 4. 获取手机热点流量遥测统计 (GET /hotspot/traffic)
  getHotspotTraffic() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/hotspot/traffic`,
        method: "GET",
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Get traffic failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] getHotspotTraffic failed:", err);
          reject(err);
        }
      });
    });
  }

  // 5. 在线设置手机热点上限与熔断策略 (POST /hotspot/config)
  setHotspotConfig({ isHotspot = true, limitMb = 100, cutoff = true }) {
    return new Promise((resolve, reject) => {
      const data = `is_hotspot=${isHotspot ? "1" : "0"}&limit_mb=${limitMb}&cutoff=${cutoff ? "1" : "0"}`;
      wx.request({
        url: `http://${this.host}/hotspot/config`,
        method: "POST",
        header: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        data: data,
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Config hotspot failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] setHotspotConfig failed:", err);
          reject(err);
        }
      });
    });
  }

  // 6. 重置手机热点流量统计计数器 (POST /hotspot/reset_traffic)
  resetHotspotTraffic() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/hotspot/reset_traffic`,
        method: "POST",
        header: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        data: "",
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Reset traffic failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] resetHotspotTraffic failed:", err);
          reject(err);
        }
      });
    });
  }

  // 7. 获取人机多轮历史对话记忆流 (GET /pet/memories)
  getMemories() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/pet/memories`,
        method: "GET",
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            const list = Array.isArray(res.data) ? res.data : (res.data.turns || res.data.memories || []);
            resolve(list);
          } else {
            resolve([]);
          }
        },
        fail: (err) => {
          console.warn("[HTTP] getMemories failed:", err);
          resolve([]);
        }
      });
    });
  }

  // 8. 查询设备端 Wi-Fi STA 联网状态 (GET /wifi/status)
  getWifiStatus() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/wifi/status`,
        method: "GET",
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Get wifi status failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.warn("[HTTP] getWifiStatus failed:", err);
          reject(err);
        }
      });
    });
  }

  // 9. 查询阿里云百炼实时大模型状态 (GET /bailian/status)
  getBailianStatus() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/bailian/status`,
        method: "GET",
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Get bailian status failed with status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.warn("[HTTP] getBailianStatus failed:", err);
          reject(err);
        }
      });
    });
  }

  // 10. 保存阿里云百炼大模型配置 (POST /bailian/config)
  saveBailianConfig({ key = "", model = "qwen3.8-omni-flash-realtime", voice = "Tina", prompt = "" }) {
    return new Promise((resolve, reject) => {
      let data = `model=${encodeURIComponent(model)}&voice=${encodeURIComponent(voice)}`;
      if (key && key.trim().length > 0) {
        data += `&key=${encodeURIComponent(key.trim())}`;
      }
      if (prompt && prompt.trim().length > 0) {
        data += `&prompt=${encodeURIComponent(prompt.trim())}`;
      }
      wx.request({
        url: `http://${this.host}/bailian/config`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: data,
        timeout: 5000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(res.data && res.data.message ? res.data.message : `Config failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] saveBailianConfig failed:", err);
          reject(err);
        }
      });
    });
  }

  // 11. 即时音色试听 (POST /bailian/preview_voice)
  previewVoice(voice = "Tina") {
    return new Promise((resolve, reject) => {
      const data = `voice=${encodeURIComponent(voice)}`;
      wx.request({
        url: `http://${this.host}/bailian/preview_voice`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: data,
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Preview voice failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] previewVoice failed:", err);
          reject(err);
        }
      });
    });
  }

  // 12. 查询离线唤醒词状态 (GET /wakeword/status)
  getWakewordStatus() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/wakeword/status`,
        method: "GET",
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Get wakeword status failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.warn("[HTTP] getWakewordStatus failed:", err);
          reject(err);
        }
      });
    });
  }

  // 13. 配置离线唤醒词 (POST /wakeword/config)
  saveWakewordConfig({ enabled = true, sensitivity = 75, timeoutSec = 8 }) {
    return new Promise((resolve, reject) => {
      const data = `enabled=${enabled ? "true" : "false"}&sensitivity=${sensitivity}&timeout_sec=${timeoutSec}`;
      wx.request({
        url: `http://${this.host}/wakeword/config`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: data,
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Wakeword config failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] saveWakewordConfig failed:", err);
          reject(err);
        }
      });
    });
  }

  // 14. 模拟离线唤醒词触发测试 (POST /wakeword/trigger)
  triggerWakeSim(confidence = 98.0) {
    return new Promise((resolve, reject) => {
      const data = `confidence=${confidence}`;
      wx.request({
        url: `http://${this.host}/wakeword/trigger`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: data,
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Trigger wake failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] triggerWakeSim failed:", err);
          reject(err);
        }
      });
    });
  }

  // 15. 清空设备端 Flash 对话记忆 (POST /memory/clear)
  clearDeviceMemory() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/memory/clear`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: "",
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Clear memory failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          console.error("[HTTP] clearDeviceMemory failed:", err);
          reject(err);
        }
      });
    });
  }

  // 16. 系统软重启 (POST /system/reboot)
  reboot() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/system/reboot`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: "",
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Reboot failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          // 设备重启可能瞬间断开连接，也视为发起成功
          console.warn("[HTTP] reboot request completed or disconnected:", err);
          resolve({ status: "ok", msg: "rebooting" });
        }
      });
    });
  }

  // 17. 恢复出厂设置 (POST /system/factory_reset)
  factoryReset() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/system/factory_reset`,
        method: "POST",
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: "",
        timeout: 4000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Factory reset failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          // 设备重启可能瞬间断开连接，视为发起成功
          console.warn("[HTTP] factoryReset request completed or disconnected:", err);
          resolve({ status: "ok", msg: "factory_reset" });
        }
      });
    });
  }

  // 18. 设置播音音量 (GET/POST 自适应容灾，零 CORS 预检阻断)
  setSpeakerVolume(volume) {
    const vol = parseInt(volume, 10);
    return new Promise((resolve, reject) => {
      // 优先简单 GET 请求 (避免模拟器/浏览器 CORS OPTIONS 阻断)
      wx.request({
        url: `http://${this.host}/audio/volume?volume=${vol}`,
        method: "GET",
        enableHttp2: false,
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            this._postSpeakerVolume(vol).then(resolve).catch(reject);
          }
        },
        fail: () => {
          this._postSpeakerVolume(vol).then(resolve).catch(reject);
        }
      });
    });
  }

  _postSpeakerVolume(vol) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/audio/volume`,
        method: "POST",
        enableHttp2: false,
        header: { "Content-Type": "application/x-www-form-urlencoded" },
        data: `volume=${vol}`,
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) resolve(res.data);
          else reject(new Error(`Set volume failed: ${res.statusCode}`));
        },
        fail: reject
      });
    });
  }

  // 18.1 试听当前播音音量 (GET/POST 自适应容灾)
  testSpeakerVolume() {
    return new Promise((resolve, reject) => {
      // 优先简单 GET 请求
      wx.request({
        url: `http://${this.host}/audio/test`,
        method: "GET",
        enableHttp2: false,
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data || { ok: true });
          } else {
            this._postTestVolume().then(resolve).catch(reject);
          }
        },
        fail: () => {
          this._postTestVolume().then(resolve).catch(reject);
        }
      });
    });
  }

  _postTestVolume() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/audio/test`,
        method: "POST",
        enableHttp2: false,
        timeout: 3000,
        success: (res) => resolve(res.data || { ok: true }),
        fail: reject
      });
    });
  }

  // 19. 获取播音音量 (GET /audio/volume)
  getSpeakerVolume() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://${this.host}/audio/volume`,
        method: "GET",
        timeout: 3000,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            resolve(res.data);
          } else {
            reject(new Error(`Get volume failed status ${res.statusCode}`));
          }
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  }

  // 3. 启动微信小程序 mDNS 本地局域网服务发现 (ZeroConf)
  startLocalDiscovery(onServiceFound, onError) {
    if (this.isDiscoveryRunning) return;

    wx.startLocalServiceDiscovery({
      serviceType: "_http._tcp.",
      success: () => {
        this.isDiscoveryRunning = true;
        console.log("[mDNS] Started local service discovery.");
        
        wx.onLocalServiceFound((service) => {
          console.log("[mDNS] Local service found:", service);
          if (service.serviceName && service.serviceName.includes("StickS3")) {
            this.setHost(service.ip);
            if (onServiceFound) onServiceFound(service);
          }
        });
      },
      fail: (err) => {
        console.warn("[mDNS] startLocalServiceDiscovery failed:", err);
        if (onError) onError(err);
      }
    });
  }

  stopLocalDiscovery() {
    if (!this.isDiscoveryRunning) return;
    wx.stopLocalServiceDiscovery({
      complete: () => {
        this.isDiscoveryRunning = false;
        console.log("[mDNS] Stopped discovery.");
      }
    });
  }
}

module.exports = {
  StickS3HttpClient
};
