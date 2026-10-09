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

  // 特征值消息解码分发 (遵循公理六：自适应协议与防截断编码公理)
  handleCharacteristicValueChange(res) {
    if (!res || !res.characteristicId || !res.value) return;
    const charId = res.characteristicId.toUpperCase();

    // 1. 记忆流切片通知 (0xFFB1)
    // 关键修复：直接传递原始 ArrayBuffer，严禁在分片边界前提前做字符串转换，杜绝多字节 UTF-8 中文撕裂乱码
    if (charId.includes("FFB1")) {
      this.handleMemoryChunk(res.value);
      return;
    }

    const str = this.ab2str(res.value);

    // 2. 灵宠状态快照通知 (0xFFB2)
    if (charId.includes("FFB2")) {
      try {
        const status = JSON.parse(str);
        if (this.onStatusUpdate) this.onStatusUpdate(status);
      } catch (e) {
        console.error("[BLE] Parse FFB2 status JSON error:", e);
      }
    }
    // 3. 灵宠心声日记通知 (0xFFB3)
    else if (charId.includes("FFB3")) {
      let diaryText = str;
      try {
        const dDoc = JSON.parse(str);
        if (dDoc && typeof dDoc === "object") {
          diaryText = dDoc.diary || dDoc.text || dDoc.content || str;
        }
      } catch (e) {
        // 非 JSON 则直接作为纯文本日记
      }
      if (this.onDiaryReceived) this.onDiaryReceived(diaryText);
    }
  }

  // 处理 0xFFB1 分片记忆还原算法 (原生二进制 Uint8Array 级分片聚合，全片到达后单次 UTF-8 整体解码)
  handleMemoryChunk(chunk) {
    if (!chunk) return;

    // 兼容二进制 ArrayBuffer / Uint8Array 及字符串入参
    let bytes;
    if (typeof chunk === "string") {
      bytes = new Uint8Array(this.str2ab(chunk));
    } else if (chunk instanceof Uint8Array) {
      bytes = chunk;
    } else if (chunk instanceof ArrayBuffer) {
      bytes = new Uint8Array(chunk);
    } else {
      return;
    }

    if (bytes.length === 0) return;

    // 检查是否包含 [C:cur/total] 协议分片帧 (ASCII: '['=0x5B, 'C'=0x43, ':'=0x3A, ']'=0x5D)
    if (bytes.length >= 7 && bytes[0] === 0x5B && bytes[1] === 0x43 && bytes[2] === 0x3A) {
      let endHeader = -1;
      for (let i = 3; i < bytes.length && i < 32; i++) {
        if (bytes[i] === 0x5D) { // ']'
          endHeader = i;
          break;
        }
      }

      if (endHeader > 3) {
        let headerStr = "";
        for (let i = 3; i < endHeader; i++) {
          headerStr += String.fromCharCode(bytes[i]);
        }
        const parts = headerStr.includes("/") ? headerStr.split("/") : headerStr.split(":");
        if (parts.length >= 2) {
          const cur = parseInt(parts[0], 10);
          const total = parseInt(parts[1], 10);
          const payloadBytes = bytes.subarray(endHeader + 1);

          if (!isNaN(cur) && !isNaN(total) && total > 0) {
            // 新流开始或总片数不匹配时重置
            if (!this.memoryRawChunks || this.expectedTotalChunks !== total || cur === 1) {
              this.memoryRawChunks = new Array(total);
              this.expectedTotalChunks = total;
              if (this.memoryChunkTimer) clearTimeout(this.memoryChunkTimer);
              // 设置 3 秒超时熔断，防止丢包悬挂
              this.memoryChunkTimer = setTimeout(() => {
                this.memoryRawChunks = null;
                this.expectedTotalChunks = 0;
              }, 3000);
            }

            // 0-based 槽位存储 (固件 1..total 映射到 0..total-1)
            const slotIdx = cur >= 1 ? (cur - 1) : cur;
            this.memoryRawChunks[slotIdx] = payloadBytes;

            const receivedCount = this.memoryRawChunks.filter(c => c !== undefined).length;
            if (receivedCount === this.expectedTotalChunks) {
              if (this.memoryChunkTimer) clearTimeout(this.memoryChunkTimer);
              
              // 聚合全部原始二进制分片切片
              const totalBytes = this.memoryRawChunks.reduce((acc, c) => acc + (c ? c.length : 0), 0);
              const merged = new Uint8Array(totalBytes);
              let offset = 0;
              for (let i = 0; i < this.expectedTotalChunks; i++) {
                const c = this.memoryRawChunks[i];
                if (c) {
                  merged.set(c, offset);
                  offset += c.length;
                }
              }
              this.memoryRawChunks = null;
              this.expectedTotalChunks = 0;

              // 整体执行一次完整的 UTF-8 解码，100% 杜绝跨包中文字节被撕裂破坏
              const fullJson = this.ab2str(merged);
              try {
                const memData = JSON.parse(fullJson);
                const list = Array.isArray(memData) ? memData : (memData.turns || memData.memories || []);
                if (this.onMemoryReceived) this.onMemoryReceived(list);
              } catch (e) {
                console.error("[BLE] Reassemble memory JSON error:", e, "raw:", fullJson);
              }
            }
            return;
          }
        }
      }
    }

    // 非分片格式：可能是单包直推的有效 JSON (例如以 '{' 或 '[' 开头)
    const directJson = this.ab2str(bytes);
    if (directJson && (directJson.startsWith("{") || directJson.startsWith("["))) {
      try {
        const memData = JSON.parse(directJson);
        const list = Array.isArray(memData) ? memData : (memData.turns || memData.memories || []);
        if (this.onMemoryReceived) this.onMemoryReceived(list);
      } catch (e) {
        console.warn("[BLE] Parse direct memory JSON error:", e);
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

  // 公理六【自适应协议与防截断编码】：UTF-8 字符级边界保护安全切片器
  splitIntoSafeChunks(text, maxBytes = 20) {
    if (!text) return [];
    const chunks = [];
    let cur = "";
    for (const char of text) {
      const candidate = cur + char;
      const byteLen = this.str2ab(candidate).byteLength;
      if (byteLen > maxBytes) {
        if (cur.length > 0) chunks.push(cur);
        cur = char;
      } else {
        cur = candidate;
      }
    }
    if (cur.length > 0) chunks.push(cur);
    return chunks;
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

  // 工具函数: ArrayBuffer <-> String (自适应 UTF-8 多字节保护，杜绝汉字与 Emoji 乱码)
  ab2str(buf) {
    if (!buf) return "";
    const uint8 = (buf instanceof Uint8Array) ? buf : new Uint8Array(buf);
    if (typeof TextDecoder !== "undefined") {
      try {
        return new TextDecoder("utf-8").decode(uint8);
      } catch (e) {}
    }

    // 纯 JS 原生 UTF-8 解码状态机 (完美处理 1~4 字节 Unicode 字符与 Emoji)
    let out = "";
    let i = 0;
    const len = uint8.length;
    while (i < len) {
      const b0 = uint8[i++];
      if (b0 < 0x80) {
        out += String.fromCharCode(b0);
      } else if ((b0 & 0xE0) === 0xC0) {
        if (i < len) {
          const b1 = uint8[i++];
          out += String.fromCharCode(((b0 & 0x1F) << 6) | (b1 & 0x3F));
        }
      } else if ((b0 & 0xF0) === 0xE0) {
        if (i + 1 < len) {
          const b1 = uint8[i++];
          const b2 = uint8[i++];
          out += String.fromCharCode(((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F));
        }
      } else if ((b0 & 0xF8) === 0xF0) {
        if (i + 2 < len) {
          const b1 = uint8[i++];
          const b2 = uint8[i++];
          const b3 = uint8[i++];
          let cp = ((b0 & 0x07) << 18) | ((b1 & 0x3F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
          if (cp > 0xFFFF) {
            cp -= 0x10000;
            out += String.fromCharCode(0xD800 + (cp >> 10));
            out += String.fromCharCode(0xDC00 + (cp & 0x3FF));
          } else {
            out += String.fromCharCode(cp);
          }
        }
      }
    }
    return out;
  }

  str2ab(str) {
    if (!str) return new ArrayBuffer(0);
    if (typeof TextEncoder !== "undefined") {
      try {
        return new TextEncoder().encode(str).buffer;
      } catch (e) {}
    }
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
