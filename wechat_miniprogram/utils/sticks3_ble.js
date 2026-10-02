/**
 * wechat_miniprogram/utils/sticks3_ble.js
 * ---------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序原生 BLE 驱动 SDK
 * 特性：
 * 1. 跨平台兼容 (iOS / Android 统一广播识别，自适应 16位短UUID 与 128位完整UUID)
 * 2. 开放式无锁搜索机制 (杜绝因 31 字节广播限制导致的微信底层静默过滤)
 * 3. 严格遵循 20 字节安全 MTU 分片传输 (解决单包截断与硬件缓冲区溢出)
 * 4. 0xFFB1 记忆分块重组、0xFFB2 状态快照与 0xFFB3 第一人称日记监听
 * 5. 断线监听与指数退避自动重连自愈机制
 */

const SERVICE_UUID_FULL = "0000FFB0-0000-1000-8000-00805F9B34FB";
const CHAR_UUID_MEMORY  = "0000FFB1-0000-1000-8000-00805F9B34FB";
const CHAR_UUID_STATUS  = "0000FFB2-0000-1000-8000-00805F9B34FB";
const CHAR_UUID_DIARY   = "0000FFB3-0000-1000-8000-00805F9B34FB";
const CHAR_UUID_INJECT  = "0000FFB4-0000-1000-8000-00805F9B34FB";

class StickS3BLEClient {
  constructor() {
    this.deviceId = null;
    this.serviceId = null;
    this.characteristics = [];
    this.charInjectUuid = CHAR_UUID_INJECT;
    this.isConnected = false;
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.autoReconnect = true;
    this._deviceFoundHandler = null;

    // 回调事件
    this.onStatusUpdate = null;
    this.onDiaryReceived = null;
    this.onMemoryReceived = null;
    this.onConnectionChange = null;

    // 分块记忆重组缓冲区
    this.memoryChunks = [];
    this.expectedTotalChunks = 0;
  }

  // 初始化蓝牙适配器并启动搜索 (全频段高敏扫描 + 系统缓存直读)
  startScan(onDeviceFound, onError) {
    wx.openBluetoothAdapter({
      success: () => {
        // 1. 读取系统蓝牙堆栈已发现或已配对的设备
        wx.getBluetoothDevices({
          success: (res) => {
            if (res.devices && res.devices.length > 0) {
              res.devices.forEach(dev => this._checkAndReportDevice(dev, onDeviceFound));
            }
          }
        });

        // 2. 绑定新设备发现监听器 (先注销旧监听，防止重复绑定)
        if (this._deviceFoundHandler) {
          try { wx.offBluetoothDeviceFound(this._deviceFoundHandler); } catch (e) {}
        }
        this._deviceFoundHandler = (res) => {
          if (res.devices && res.devices.length > 0) {
            res.devices.forEach(dev => this._checkAndReportDevice(dev, onDeviceFound));
          }
        };
        wx.onBluetoothDeviceFound(this._deviceFoundHandler);

        // 3. 启动设备扫描：
        // 关键点：千万不可传 services: [SERVICE_UUID_FULL, "FFB0"]！
        // 固件主广播包在 31 字节物理限制下只携带 Nordic UART (6E400001) 与 "StickS3" 名称，
        // 传入 FFB0 会导致微信底层原生过滤规则将 M5StickS3 静默丢弃！
        wx.startBluetoothDevicesDiscovery({
          allowDuplicatesKey: false,
          powerLevel: "high",
          success: () => {
            console.log("[BLE] Started discovery for StickS3 devices (open scan mode)...");
            // 延时 800ms 再查一次已发现列表，兼容部分安卓机型初次发现慢的问题
            setTimeout(() => {
              wx.getBluetoothDevices({
                success: (res) => {
                  if (res.devices) {
                    res.devices.forEach(dev => this._checkAndReportDevice(dev, onDeviceFound));
                  }
                }
              });
            }, 800);
          },
          fail: (err) => {
            console.error("[BLE] startBluetoothDevicesDiscovery failed:", err);
            if (onError) onError(err);
          }
        });
      },
      fail: (err) => {
        console.error("[BLE] openBluetoothAdapter failed:", err);
        if (onError) onError(err);
      }
    });
  }

  // 设备指纹检测与智能过滤上报
  _checkAndReportDevice(dev, onDeviceFound) {
    if (!dev || !dev.deviceId) return;
    const name = (dev.name || dev.localName || "").trim();
    const uuids = (dev.advertisServiceUUIDs || []).map(u => u.toUpperCase());

    // 1. 匹配设备名称 (StickS3, StickS3-Buddy, LingBuddy, M5, ESP32 等)
    const isNameMatch = /StickS3|Buddy|LingBuddy|M5|ESP/i.test(name);

    // 2. 匹配广播服务 UUID (无论是 6E400001 还是 FFB0)
    const isUuidMatch = uuids.some(u => u.includes("6E400001") || u.includes("FFB0"));

    if (isNameMatch || isUuidMatch) {
      const cleanDev = {
        ...dev,
        name: name || "StickS3-Buddy",
        isTarget: true
      };
      if (onDeviceFound) onDeviceFound(cleanDev);
    } else if (name && name.length > 0) {
      // 允许展示有广播名的周边设备（方便用户在特殊固件名下也能连接）
      const candidateDev = {
        ...dev,
        name: name,
        isTarget: false
      };
      if (onDeviceFound) onDeviceFound(candidateDev);
    }
  }

  // 停止搜索
  stopScan() {
    if (this._deviceFoundHandler) {
      try { wx.offBluetoothDeviceFound(this._deviceFoundHandler); } catch (e) {}
      this._deviceFoundHandler = null;
    }
    wx.stopBluetoothDevicesDiscovery({
      complete: () => console.log("[BLE] Stopped discovery.")
    });
  }

  // 连接目标设备
  connect(deviceId, onSuccess, onFail) {
    this.deviceId = deviceId;
    this.stopScan();

    wx.createBLEConnection({
      deviceId: this.deviceId,
      timeout: 10000,
      success: () => {
        console.log("[BLE] Connected to device:", deviceId);
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.listenConnectionState();

        // 协商 MTU (Android 支持协商更大 MTU，iOS 系统自动管理)
        const sys = wx.getSystemInfoSync();
        if (sys.platform === "android") {
          wx.setBLEMTU({
            deviceId: this.deviceId,
            mtu: 247,
            complete: () => this.discoverServices(onSuccess, onFail)
          });
        } else {
          this.discoverServices(onSuccess, onFail);
        }
      },
      fail: (err) => {
        console.error("[BLE] createBLEConnection failed:", err);
        this.isConnected = false;
        if (onFail) onFail(err);
      }
    });
  }

  // 发现服务与特征值 (优先寻找 FFB0，兼容 16位/128位 UUID)
  discoverServices(onSuccess, onFail) {
    wx.getBLEDeviceServices({
      deviceId: this.deviceId,
      success: (res) => {
        console.log("[BLE] Services found on device:", res.services.map(s => s.uuid));
        let targetService = res.services.find(s => 
          s.uuid.toUpperCase().includes("FFB0") || s.uuid.toUpperCase() === SERVICE_UUID_FULL
        );
        if (!targetService && res.services.length > 0) {
          // 备选尝试 Nordic UART 服务
          targetService = res.services.find(s => s.uuid.toUpperCase().includes("6E400001")) || res.services[0];
        }

        if (!targetService) {
          if (onFail) onFail(new Error("LingBuddy service 0xFFB0 not found"));
          return;
        }

        this.serviceId = targetService.uuid;
        wx.getBLEDeviceCharacteristics({
          deviceId: this.deviceId,
          serviceId: this.serviceId,
          success: (cRes) => {
            console.log("[BLE] Characteristics discovered:", cRes.characteristics.map(c => c.uuid));
            this.characteristics = cRes.characteristics || [];
            this.setupSubscriptions();
            if (onSuccess) onSuccess();
          },
          fail: onFail
        });
      },
      fail: onFail
    });
  }

  // 订阅特征值通知 (0xFFB1, 0xFFB2, 0xFFB3 动态匹配)
  setupSubscriptions() {
    if (!this.characteristics || this.characteristics.length === 0) return;

    const findChar = (suffix) => {
      const match = this.characteristics.find(c => c.uuid.toUpperCase().includes(suffix));
      return match ? match.uuid : null;
    };

    const charMemory = findChar("FFB1") || CHAR_UUID_MEMORY;
    const charStatus = findChar("FFB2") || CHAR_UUID_STATUS;
    const charDiary  = findChar("FFB3") || CHAR_UUID_DIARY;
    this.charStatusUuid = charStatus;
    this.charInjectUuid = findChar("FFB4") || CHAR_UUID_INJECT;

    // 尝试协商大 MTU (提升到 256 字节，加速长 JSON 分发)
    if (wx.setBLEMTU) {
      wx.setBLEMTU({
        deviceId: this.deviceId,
        mtu: 256,
        success: (res) => {
          console.log("[BLE] MTU negotiated:", res.mtu);
          this.negotiatedMtu = res.mtu || 256;
        },
        fail: () => {
          this.negotiatedMtu = 23;
        }
      });
    }

    const notifyUUIDs = [charMemory, charStatus, charDiary];
    notifyUUIDs.forEach(uuid => {
      wx.notifyBLECharacteristicValueChange({
        deviceId: this.deviceId,
        serviceId: this.serviceId,
        characteristicId: uuid,
        state: true,
        success: () => console.log(`[BLE] Subscribed to notify: ${uuid}`),
        fail: (e) => console.warn(`[BLE] Failed to subscribe ${uuid}:`, e)
      });
    });

    wx.onBLECharacteristicValueChange((res) => {
      this.handleCharacteristicValueChange(res);
    });
  }

  // 特征值消息解码分发
  handleCharacteristicValueChange(res) {
    const charId = res.characteristicId.toUpperCase();
    const str = this.ab2str(res.value);

    // 1. 灵宠状态快照通知 (0xFFB2)
    if (charId.includes("FFB2")) {
      try {
        const status = JSON.parse(str);
        if (this.onStatusUpdate) this.onStatusUpdate(status);
      } catch (e) {
        console.error("[BLE] Parse FFB2 status JSON error:", e);
      }
    }
    // 2. 灵宠心声日记通知 (0xFFB3)
    else if (charId.includes("FFB3")) {
      if (this.onDiaryReceived) this.onDiaryReceived(str);
    }
    // 3. 记忆流切片通知 (0xFFB1)
    else if (charId.includes("FFB1")) {
      this.handleMemoryChunk(str);
    }
  }

  // 处理 0xFFB1 分片记忆还原算法 (兼容 "/" 与 ":" 分隔符及 1-based 序号)
  handleMemoryChunk(chunk) {
    if (!chunk || !chunk.startsWith("[C:")) return;
    const endHeader = chunk.indexOf("]");
    if (endHeader < 0) return;

    const header = chunk.substring(3, endHeader);
    const parts = header.includes("/") ? header.split("/") : header.split(":");
    if (parts.length < 2) return;

    const cur = parseInt(parts[0], 10);
    const total = parseInt(parts[1], 10);
    const payload = chunk.substring(endHeader + 1);

    if (isNaN(cur) || isNaN(total) || total <= 0) return;

    if (!this.memoryChunks || this.expectedTotalChunks !== total || cur === 1) {
      this.memoryChunks = new Array(total);
      this.expectedTotalChunks = total;
    }

    // 0-based 槽位存储 (固件 i+1 发送 1..total)
    const slotIdx = cur >= 1 ? (cur - 1) : cur;
    this.memoryChunks[slotIdx] = payload;

    const receivedCount = this.memoryChunks.filter(c => c !== undefined).length;
    if (receivedCount === this.expectedTotalChunks) {
      const fullJson = this.memoryChunks.join("");
      this.memoryChunks = [];
      this.expectedTotalChunks = 0;
      try {
        const memData = JSON.parse(fullJson);
        const list = Array.isArray(memData) ? memData : (memData.turns || memData.memories || []);
        if (this.onMemoryReceived) this.onMemoryReceived(list);
      } catch (e) {
        console.error("[BLE] Reassemble memory JSON error:", e, "raw:", fullJson);
      }
    }
  }

  // 向 0xFFB4 写入控制指令 (自适应 MTU 安全切片 + \n 帧定界)
  async injectAction(action, value = null) {
    if (!this.isConnected || !this.deviceId || !this.serviceId) {
      throw new Error("Device not connected");
    }

    let payloadObj;
    if (typeof action === "object" && action !== null) {
      payloadObj = action;
    } else if (typeof value === "object" && value !== null) {
      payloadObj = { action, ...value };
    } else {
      payloadObj = { action, value };
    }

    const payloadStr = JSON.stringify(payloadObj) + "\n";
    const ab = this.str2ab(payloadStr);

    const targetChar = this.charInjectUuid || CHAR_UUID_INJECT;
    const chunkSize = Math.max(20, Math.min(240, (this.negotiatedMtu || 23) - 3));
    return this.writeInChunks(this.deviceId, this.serviceId, targetChar, ab, chunkSize);
  }

  // 主动读取 0xFFB2 状态特征值
  readStatus() {
    return new Promise((resolve, reject) => {
      if (!this.isConnected || !this.deviceId || !this.serviceId) {
        return reject(new Error("BLE not connected"));
      }
      const targetChar = this.charStatusUuid || CHAR_UUID_STATUS;
      wx.readBLECharacteristicValue({
        deviceId: this.deviceId,
        serviceId: this.serviceId,
        characteristicId: targetChar,
        success: () => {
          resolve(true);
        },
        fail: (err) => {
          console.warn("[BLE] readStatus failed:", err);
          reject(err);
        }
      });
    });
  }

  // 20 字节切片安全写入器
  writeInChunks(deviceId, serviceId, characteristicId, arrayBuffer, chunkSize = 20) {
    return new Promise((resolve, reject) => {
      const totalLen = arrayBuffer.byteLength;
      let offset = 0;

      const sendNext = () => {
        if (offset >= totalLen) {
          resolve();
          return;
        }

        const currentChunkSize = Math.min(chunkSize, totalLen - offset);
        const chunk = arrayBuffer.slice(offset, offset + currentChunkSize);

        wx.writeBLECharacteristicValue({
          deviceId,
          serviceId,
          characteristicId,
          value: chunk,
          success: () => {
            offset += currentChunkSize;
            setTimeout(sendNext, 20);
          },
          fail: (err) => {
            console.error("[BLE] Write chunk error at offset", offset, err);
            reject(err);
          }
        });
      };

      sendNext();
    });
  }

  // 监听连接状态并执行指数退避重连
  listenConnectionState() {
    wx.onBLEConnectionStateChange((res) => {
      console.log(`[BLE] Connection state changed: connected=${res.connected}`);
      this.isConnected = res.connected;
      if (this.onConnectionChange) this.onConnectionChange(res.connected);

      if (!res.connected && this.autoReconnect) {
        this.attemptReconnect();
      }
    });
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn("[BLE] Max reconnect attempts reached.");
      return;
    }

    this.reconnectAttempts++;
    const delayMs = Math.min(1000 * Math.pow(1.8, this.reconnectAttempts), 12000);
    console.log(`[BLE] Reconnecting in ${delayMs}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      if (!this.isConnected && this.deviceId) {
        this.connect(this.deviceId, () => {
          console.log("[BLE] Reconnected successfully!");
        }, () => {
          this.attemptReconnect();
        });
      }
    }, delayMs);
  }

  // 主动断开连接
  disconnect() {
    this.autoReconnect = false;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.deviceId) {
      wx.closeBLEConnection({
        deviceId: this.deviceId,
        complete: () => {
          this.isConnected = false;
          this.deviceId = null;
        }
      });
    }
  }

  // 工具函数: ArrayBuffer <-> String
  ab2str(buf) {
    const uint8 = new Uint8Array(buf);
    let str = "";
    for (let i = 0; i < uint8.length; i++) {
      str += String.fromCharCode(uint8[i]);
    }
    try {
      return decodeURIComponent(escape(str));
    } catch (e) {
      return str;
    }
  }

  str2ab(str) {
    const utf8Str = unescape(encodeURIComponent(str));
    const buf = new ArrayBuffer(utf8Str.length);
    const bufView = new Uint8Array(buf);
    for (let i = 0; i < utf8Str.length; i++) {
      bufView[i] = utf8Str.charCodeAt(i);
    }
    return buf;
  }
}

module.exports = {
  StickS3BLEClient,
  SERVICE_UUID_FULL,
  CHAR_UUID_MEMORY,
  CHAR_UUID_STATUS,
  CHAR_UUID_DIARY,
  CHAR_UUID_INJECT
};
