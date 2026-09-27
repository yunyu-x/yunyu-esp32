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
