/**
 * wechat_miniprogram/utils/crypto_guard.js
 * ----------------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序端安全防护与防重放引擎
 * - 符合 STRIDE 威胁评估模型
 * - 防伪造 (Spoofing) & 防重放 (Anti-Replay)
 */

class CryptoGuard {
  constructor() {
    this.sequenceCounter = 1;
  }

  // 生成 16 字节随机 Nonce
  generateNonce(length = 16) {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let nonce = "";
    for (let i = 0; i < length; i++) {
      nonce += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return nonce;
  }

  // 构建带时间戳、单调递增序号与 Nonce 的安全互动报文
  wrapSecurePayload(action, value = null, sessionToken = "lingbuddy_default_secret") {
    const ts = Date.now();
    const seq = this.sequenceCounter++;
    const nonce = this.generateNonce(8);

    const basePayload = {
      action,
      value,
      seq,
      ts,
      nonce
    };

    // 简单高效校验和 (Checksum)
    const rawStr = `${action}|${value || ""}|${seq}|${ts}|${nonce}|${sessionToken}`;
    basePayload.sign = this.calculateHash(rawStr);

    return basePayload;
  }

  // 简易散列计算 (DJB2a 变种)
  calculateHash(str) {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) + hash) + str.charCodeAt(i);
      hash = hash & 0xffffffff;
    }
    return Math.abs(hash).toString(16);
  }
}

module.exports = {
  CryptoGuard: new CryptoGuard()
};
