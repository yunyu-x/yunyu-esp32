/**
 * wechat_miniprogram/utils/sticks3_ble.js
 * ---------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序原生 BLE 驱动 SDK
 * 特性：
 * 1. 跨平台兼容 (iOS / Android 统一识别服务 0xFFB0 与名称过滤)
 * 2. 严格遵循 20 字节安全 MTU 分片传输 (解决低版本蓝牙与微信单包截断)
 * 3. 0xFFB1 记忆分块重组、0xFFB2 状态快照与 0xFFB3 第一人称日记监听
 * 4. 断线监听与指数退避自动重连自愈机制
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
    this.isConnected = false;
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.autoReconnect = true;

    // 回调事件
    this.onStatusUpdate = null;
    this.onDiaryReceived = null;
    this.onMemoryReceived = null;
    this.onConnectionChange = null;

    // 分块记忆重组缓冲区
    this.memoryChunks = [];
    this.expectedTotalChunks = 0;
  }

  // 初始化蓝牙适配器并启动搜索
  startScan(onDeviceFound, onError) {
    wx.openBluetoothAdapter({
      success: () => {
        wx.onBluetoothDeviceFound((res) => {
          res.devices.forEach((dev) => {
            const name = dev.name || dev.localName || "";
            if (name.includes("StickS3") || name.includes("LingBuddy")) {
              if (onDeviceFound) onDeviceFound(dev);
            }
          });
        });

        wx.startBluetoothDevicesDiscovery({
          services: [SERVICE_UUID_FULL, "FFB0"],
          allowDuplicatesKey: false,
          success: () => {
            console.log("[BLE] Started discovery for StickS3 devices...");
          },
          fail: (err) => {
            // 某些安卓设备传入 services 无法过滤广播，退回无参数全量发现
            wx.startBluetoothDevicesDiscovery({
              allowDuplicatesKey: false,
              success: () => console.log("[BLE] Fallback scan without service filter started."),
              fail: onError
            });
          }
        });
      },
      fail: (err) => {
        console.error("[BLE] openBluetoothAdapter failed:", err);
        if (onError) onError(err);
      }
    });
  }

  // 停止搜索
  stopScan() {
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

        // 协商 MTU (Android 支持 512，iOS 默认自动管理)
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

  // 发现服务与特征值
  discoverServices(onSuccess, onFail) {
    wx.getBLEDeviceServices({
      deviceId: this.deviceId,
      success: (res) => {
        let targetService = res.services.find(s => 
          s.uuid.toUpperCase().includes("FFB0") || s.uuid.toUpperCase() === SERVICE_UUID_FULL
        );
        if (!targetService && res.services.length > 0) {
          targetService = res.services[0];
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
            console.log("[BLE] Characteristics discovered:", cRes.characteristics);
            this.setupSubscriptions();
            if (onSuccess) onSuccess();
          },
          fail: onFail
        });
      },
      fail: onFail
    });
  }

  // 订阅特征值通知 (0xFFB1, 0xFFB2, 0xFFB3)
  setupSubscriptions() {
    const notifyUUIDs = [CHAR_UUID_MEMORY, CHAR_UUID_STATUS, CHAR_UUID_DIARY];
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

  // 处理 0xFFB1 分片记忆还原算法
  handleMemoryChunk(chunk) {
    // 格式: [C:idx:total]payload
    if (!chunk.startsWith("[C:")) return;
    const endHeader = chunk.indexOf("]");
    if (endHeader < 0) return;

    const header = chunk.substring(3, endHeader);
    const parts = header.split(":");
    const idx = parseInt(parts[0], 10);
    const total = parseInt(parts[1], 10);
    const payload = chunk.substring(endHeader + 1);

    if (idx === 0) {
      this.memoryChunks = new Array(total);
      this.expectedTotalChunks = total;
    }
    this.memoryChunks[idx] = payload;

    // 检查是否所有分片接收完毕
    const receivedCount = this.memoryChunks.filter(c => c !== undefined).length;
    if (receivedCount === this.expectedTotalChunks && this.expectedTotalChunks > 0) {
      const fullJson = this.memoryChunks.join("");
      this.memoryChunks = [];
      this.expectedTotalChunks = 0;
      try {
        const memData = JSON.parse(fullJson);
        if (this.onMemoryReceived) this.onMemoryReceived(memData);
      } catch (e) {
        console.error("[BLE] Reassemble memory JSON error:", e);
      }
    }
  }

  // 向 0xFFB4 写入控制指令 (采用 20 字节安全 MTU 分包写入)
  async injectAction(action, value = null) {
    if (!this.isConnected || !this.deviceId || !this.serviceId) {
      throw new Error("Device not connected");
    }

    const payloadObj = { action, value };
    const payloadStr = JSON.stringify(payloadObj);
    const ab = this.str2ab(payloadStr);

    return this.writeInChunks(this.deviceId, this.serviceId, CHAR_UUID_INJECT, ab, 20);
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
            // 延时 20ms 避免 BLE 缓冲区溢出
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
