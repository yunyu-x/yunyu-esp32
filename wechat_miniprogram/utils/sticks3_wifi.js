/**
 * wechat_miniprogram/utils/sticks3_wifi.js
 * ----------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序局域网通信客户端
 * - 提供完整的拓麻歌子互动、Wi-Fi/热点配网、大模型配置与音频音量控制 RESTful API
 * - 统一轻量化请求中枢 (_req)，支持超时控制与自适应 GET/POST 容灾
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

  _req(path, { method = "GET", data, contentType, timeout = 4000 } = {}) {
    return new Promise((resolve, reject) => {
      const header = contentType ? { "Content-Type": contentType } : undefined;
      wx.request({
        url: `http://${this.host}${path}`,
        method,
        header,
        data,
        timeout,
        enableHttp2: false,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data || {});
          } else {
            const msg = (res.data && (res.data.message || res.data.msg)) || `HTTP ${res.statusCode}`;
            reject(new Error(msg));
          }
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  }

  // 1. 查询灵宠实时状态与亲密值
  getPetStatus() {
    return this._req("/pet/status");
  }

  // 2. 下发拓麻歌子互动指令 (隔空投喂 / 梳毛 / 击掌 / 抚摸 / 模式切换)
  sendPetAction(action, item = "") {
    let data = `action=${encodeURIComponent(action)}`;
    if (item) data += `&item=${encodeURIComponent(item)}`;
    return this._req("/pet/action", { method: "POST", data, contentType: "application/x-www-form-urlencoded" });
  }

  // 3. Wi-Fi / 手机热点一键配网连接 (POST /wifi/connect)
  connectWifiNetwork({ ssid, password, isHotspot = false, limitMb = 100, cutoff = true }) {
    const data = `ssid=${encodeURIComponent(ssid)}&pass=${encodeURIComponent(password || "")}&is_hotspot=${isHotspot ? "1" : "0"}&limit_mb=${limitMb}&cutoff=${cutoff ? "1" : "0"}`;
    return this._req("/wifi/connect", { method: "POST", data, contentType: "application/x-www-form-urlencoded", timeout: 5000 });
  }

  // 4. 获取手机热点流量遥测统计 (GET /hotspot/traffic)
  getHotspotTraffic() {
    return this._req("/hotspot/traffic", { timeout: 3000 });
  }

  // 5. 在线设置手机热点上限与熔断策略 (POST /hotspot/config)
  setHotspotConfig({ isHotspot = true, limitMb = 100, cutoff = true }) {
    const data = `is_hotspot=${isHotspot ? "1" : "0"}&limit_mb=${limitMb}&cutoff=${cutoff ? "1" : "0"}`;
    return this._req("/hotspot/config", { method: "POST", data, contentType: "application/x-www-form-urlencoded" });
  }

  // 6. 重置手机热点流量统计计数器 (POST /hotspot/reset_traffic)
  resetHotspotTraffic() {
    return this._req("/hotspot/reset_traffic", { method: "POST", data: "", contentType: "application/x-www-form-urlencoded" });
  }

  // 7. 获取人机多轮历史对话记忆流 (GET /pet/memories)
  getMemories() {
    return this._req("/pet/memories").then(data => {
      return Array.isArray(data) ? data : (data.turns || data.memories || []);
    }).catch(() => []);
  }

  // 8. 查询设备端 Wi-Fi STA 联网状态 (GET /wifi/status)
  getWifiStatus() {
    return this._req("/wifi/status", { timeout: 3000 });
  }

  // 9. 查询阿里云百炼实时大模型状态 (GET /bailian/status)
  getBailianStatus() {
    return this._req("/bailian/status", { timeout: 3000 });
  }

  // 10. 保存阿里云百炼大模型配置 (POST /bailian/config)
  saveBailianConfig({ key = "", model = "qwen3.8-omni-flash-realtime", voice = "Tina", prompt = "", volume }) {
    let data = `model=${encodeURIComponent(model)}&voice=${encodeURIComponent(voice)}`;
    if (key && key.trim().length > 0) data += `&key=${encodeURIComponent(key.trim())}`;
    if (prompt && prompt.trim().length > 0) data += `&prompt=${encodeURIComponent(prompt.trim())}`;
    if (volume !== undefined) data += `&volume=${encodeURIComponent(volume)}`;
    return this._req("/bailian/config", { method: "POST", data, contentType: "application/x-www-form-urlencoded", timeout: 5000 });
  }

  // 11. 即时音色试听 (POST /bailian/preview_voice)
  previewVoice(voice = "Tina") {
    const data = `voice=${encodeURIComponent(voice)}`;
    return this._req("/bailian/preview_voice", { method: "POST", data, contentType: "application/x-www-form-urlencoded" });
  }

  // 12. 查询离线唤醒词状态 (GET /wakeword/status)
  getWakewordStatus() {
    return this._req("/wakeword/status", { timeout: 3000 });
  }

  // 13. 配置离线唤醒词 (POST /wakeword/config)
  saveWakewordConfig({ enabled = true, sensitivity = 75, timeoutSec = 8 }) {
    const data = `enabled=${enabled ? "true" : "false"}&sensitivity=${sensitivity}&timeout_sec=${timeoutSec}`;
    return this._req("/wakeword/config", { method: "POST", data, contentType: "application/x-www-form-urlencoded" });
  }

  // 14. 模拟离线唤醒词触发测试 (POST /wakeword/trigger)
  triggerWakeSim(confidence = 98.0) {
    const data = `confidence=${confidence}`;
    return this._req("/wakeword/trigger", { method: "POST", data, contentType: "application/x-www-form-urlencoded", timeout: 3000 });
  }

  // 15. 清空设备端 Flash 对话记忆 (POST /memory/clear)
  clearDeviceMemory() {
    return this._req("/memory/clear", { method: "POST", data: "", contentType: "application/x-www-form-urlencoded" });
  }

  // 16. 系统软重启 (POST /system/reboot)
  reboot() {
    return this._req("/system/reboot", { method: "POST", data: "", contentType: "application/x-www-form-urlencoded" })
      .catch(() => ({ status: "ok", msg: "rebooting" }));
  }

  // 17. 恢复出厂设置 (POST /system/factory_reset)
  factoryReset() {
    return this._req("/system/factory_reset", { method: "POST", data: "", contentType: "application/x-www-form-urlencoded" })
      .catch(() => ({ status: "ok", msg: "factory_reset" }));
  }

  // 18. 设置播音音量 (GET/POST 自适应容灾，零 CORS 预检阻断)
  setSpeakerVolume(volume) {
    const vol = parseInt(volume, 10);
    return this._req(`/audio/volume?volume=${vol}`, { timeout: 3000 })
      .catch(() => this._req("/audio/volume", {
        method: "POST",
        data: `volume=${vol}`,
        contentType: "application/x-www-form-urlencoded",
        timeout: 3000
      }));
  }

  // 18.1 试听当前播音音量 (GET/POST 自适应容灾，支持携带 volume)
  testSpeakerVolume(volume) {
    const query = (volume !== undefined && !isNaN(volume)) ? `?volume=${volume}` : "";
    return this._req(`/audio/test${query}`, { timeout: 2000 })
      .catch(() => this._req("/audio/test", {
        method: "POST",
        data: query ? `volume=${volume}` : "",
        contentType: "application/x-www-form-urlencoded",
        timeout: 2000
      }));
  }

  // 19. 获取播音音量 (GET /audio/volume)
  getSpeakerVolume() {
    return this._req("/audio/volume", { timeout: 3000 });
  }

  // 启动微信小程序 mDNS 本地局域网服务发现 (ZeroConf)
  startLocalDiscovery(onServiceFound, onError) {
    if (this.isDiscoveryRunning) return;
    wx.startLocalServiceDiscovery({
      serviceType: "_http._tcp.",
      success: () => {
        this.isDiscoveryRunning = true;
        wx.onLocalServiceFound((service) => {
          if (service.serviceName && service.serviceName.includes("StickS3")) {
            this.setHost(service.ip);
            if (onServiceFound) onServiceFound(service);
          }
        });
      },
      fail: (err) => {
        if (onError) onError(err);
      }
    });
  }

  stopLocalDiscovery() {
    if (!this.isDiscoveryRunning) return;
    wx.stopLocalServiceDiscovery({
      complete: () => {
        this.isDiscoveryRunning = false;
      }
    });
  }
}

module.exports = {
  StickS3HttpClient
};
