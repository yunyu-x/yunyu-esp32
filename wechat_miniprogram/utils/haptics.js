/**
 * wechat_miniprogram/utils/haptics.js
 * -----------------------------------
 * M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序真机触觉反馈引擎
 * - 针对 iOS Taptic Engine 与 Android 线性马达进行细腻触觉调优
 * - 支持 'light' (轻触抚摸/梳毛), 'medium' (隔空投喂/日记到达), 'heavy' (默契击掌/等级跃迁)
 * - 具备环境异常保护 (开发者工具/无震动马达设备静默捕获，避免抛出未捕获异常)
 */

class HapticEngine {
  constructor() {
    this.enabled = true;
  }

  setEnabled(enable) {
    this.enabled = !!enable;
  }

  isEnabled() {
    return this.enabled;
  }

  /**
   * 触发短震动触觉反馈
   * @param {'light' | 'medium' | 'heavy'} type 震动强度类型
   */
  vibrate(type = "medium") {
    if (!this.enabled) return;

    try {
      if (typeof wx !== "undefined" && typeof wx.vibrateShort === "function") {
        wx.vibrateShort({
          type: type,
          fail: (err) => {
            // 某些老旧安卓系统或模拟器可能不支持 type 字段，退回默认短震动
            try {
              wx.vibrateShort();
            } catch (e) {
              // 忽略模拟器或无震动硬件的静默报错
            }
          }
        });
      }
    } catch (e) {
      // 容错处理
    }
  }

  // 快捷具身交互语义触觉
  feed() {
    // 隔空投喂：清脆饱满中度震感
    this.vibrate("medium");
  }

  pet() {
    // 温柔抚摸：细腻柔和轻度震感
    this.vibrate("light");
  }

  groom() {
    // 舒适梳毛：微风轻拂轻度震感
    this.vibrate("light");
  }

  play() {
    // 默契击掌：强烈笃定冲击震感
    this.vibrate("heavy");
  }

  levelUp() {
    // 亲密等级升级：连续双重震感
    this.vibrate("heavy");
    setTimeout(() => this.vibrate("medium"), 120);
  }

  notification() {
    // 硬件主动推送日记
    this.vibrate("medium");
  }
}

const haptics = new HapticEngine();

module.exports = {
  HapticEngine,
  haptics
};
