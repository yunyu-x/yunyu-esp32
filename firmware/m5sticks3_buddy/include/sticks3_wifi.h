/**
 * firmware/m5sticks3_buddy/include/sticks3_wifi.h
 * -----------------------------------------------
 * M5Stack StickS3 2.4GHz Wi-Fi (802.11 b/g/n) 全功能网络通信子系统：
 * 1. 射频模式：
 *    - WIFI_AP_STA 双模并行运行 (SoftAP 极速热点 + STA 真实局域网高速联网)
 *    - 运行在 ESP32-S3 双核架构下，与 BLE NUS 无缝时分复用共存
 * 2. 核心网络通道：
 *    - SoftAP: SSID="StickS3-Buddy", IP="192.168.4.1" (免密极速连接)
 *    - STA: 业界标准 Web 配网、环境 AP 列表扫描、NVS 持久化自动回连
 *    - HTTP Web Server: 监听端口 80，全功能响应式手机/电脑控制台
 *    - TCP Server: 监听端口 8080 (调试助手支持)
 *    - UDP Server: 监听端口 8080 (调试助手支持)
 * 3. 阿里云百炼 (Model Studio) 实时控制中枢：
 *    - 网页端配置 API Key、音色与大模型
 *    - 实时对话流式看板与中途打断 (Barge-In) 远程控制
 */

#pragma once

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <esp_wifi.h>
#include <functional>
#include "sticks3_audio.h"
#include "sticks3_wifi_config.h"
#include "sticks3_bailian_client.h"
#include "sticks3_memory_store.h"
#include "sticks3_i2c_mutex.h"
#include "sticks3_system_metrics.h"
#include "sticks3_wakeword.h"
#include "sticks3_avatar.h"

namespace sticks3 {

struct WiFiScanResult {
    String ssid;
    int32_t rssi;
    uint8_t channel;
    wifi_auth_mode_t auth_mode;
};

using WiFiMessageCallback = std::function<void(const String& msg, const String& source)>;

// 嵌入式 Web 控制台 HTML 资源 (存储于 Flash PROGMEM，深度优化 iOS Safari 与 Android 移动端交互)
static const char INDEX_HTML[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>StickS3 灵方双向音频与大模型语音终端</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 12px; }
.card { background: #1e293b; border-radius: 12px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border: 1px solid #334155; }
h1 { font-size: 16px; margin: 0 0 4px 0; color: #38bdf8; display: flex; align-items: center; gap: 6px; }
.sub { font-size: 12px; color: #94a3b8; margin-bottom: 10px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; }
.stat { background: #0f172a; padding: 8px 10px; border-radius: 8px; }
.stat-val { font-size: 14px; font-weight: bold; color: #4ade80; margin-top: 2px; }
input[type=text], input[type=password] { width: 100%; box-sizing: border-box; padding: 10px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; margin-bottom: 8px; }
select { width: 100%; box-sizing: border-box; padding: 10px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 13px; margin-bottom: 8px; }
.btn { display: block; width: 100%; box-sizing: border-box; padding: 11px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: 0.2s; text-align: center; text-decoration: none; }
.btn-primary { background: #0284c7; color: white; margin-bottom: 8px; }
.btn-primary:active { background: #0369a1; }
.btn-emerald { background: #059669; color: white; margin-bottom: 8px; }
.btn-emerald:active { background: #047857; }
.btn-sec { background: #334155; color: #cbd5e1; margin-bottom: 8px; }
.btn-sec:active { background: #1e293b; }
.btn-danger { background: #dc2626; color: white; margin-bottom: 8px; }
.btn-danger:active { background: #b91c1c; }
.btn-purple { background: #6366f1; color: white; margin-bottom: 8px; }
.btn-amber { background: #d97706; color: white; margin-bottom: 8px; }
.tag-group { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.tag { background: #334155; color: #38bdf8; font-size: 12px; padding: 5px 9px; border-radius: 6px; cursor: pointer; }
.tag:hover { background: #475569; }
.status-bar { font-size: 11px; color: #94a3b8; text-align: center; margin-top: 6px; }
.badge { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; background: #334155; color: #93c5fd; }
audio { width: 100%; height: 38px; border-radius: 8px; margin-top: 8px; outline: none; }
.section-title { font-weight: 600; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
.pet-card { background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border-radius: 12px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(236,72,153,0.22); border: 1px solid #db2777; }
.pet-hud-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
.pet-bar-bg { background: #020617; border-radius: 999px; height: 8px; overflow: hidden; margin-top: 4px; border: 1px solid #1e293b; }
.pet-bar-fill { background: linear-gradient(90deg, #ec4899, #f43f5e); height: 100%; border-radius: 999px; transition: width 0.3s; }
.pet-energy-fill { background: linear-gradient(90deg, #06b6d4, #3b82f6); height: 100%; border-radius: 999px; transition: width 0.3s; }
.pet-action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
.btn-pet { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 10px; border-radius: 8px; border: none; font-weight: 600; font-size: 13px; cursor: pointer; transition: 0.15s; color: white; text-decoration: none; }
.btn-pet:active { transform: scale(0.97); }
.btn-feed { background: linear-gradient(135deg, #ec4899, #d946ef); }
.btn-groom { background: linear-gradient(135deg, #06b6d4, #0ea5e9); }
.btn-play { background: linear-gradient(135deg, #f59e0b, #eab308); }
.btn-caress { background: linear-gradient(135deg, #10b981, #059669); }
.pet-diary-box { background: #020617; border: 1px solid #334155; border-radius: 8px; padding: 9px 11px; margin-bottom: 10px; font-size: 12px; line-height: 1.5; color: #cbd5e1; }
</style>
</head>
<body>

<div class="card">
  <h1>🤖 StickS3 智能语音与双向音频终端</h1>
  <div class="sub">热点: <b>StickS3-Buddy (192.168.4.1)</b> | 局域网: <b id="lanIp">未联网</b></div>
  <div class="grid">
    <div class="stat"><div>姿态俯仰 / 横滚</div><div class="stat-val" id="imu">0° / 0°</div></div>
    <div class="stat"><div>百炼大模型状态</div><div class="stat-val" id="blStateHeader">未连接</div></div>
  </div>
</div>

<!-- 板块 P: 灵宠伴侣拓麻歌子互动与隔空投喂中心 -->
<div class="pet-card">
  <div class="section-title">
    <span style="display:flex;align-items:center;gap:6px;">
      <span style="font-size:18px;">🍰</span>
      <b style="color:#f472b6;">灵宠伴侣拓麻歌子与「隔空投喂」互动中心</b>
    </span>
    <span class="badge" id="petMoodBadge" style="background:#be185d;color:#fbcfe8;">常态待命</span>
  </div>

  <div style="font-size:12px;color:#cbd5e1;margin-bottom:8px;">
    基于迪士尼灵动艺术表情与物理具身动力学。支持隔空远程投喂、舒适梳毛、默契击掌与温柔抚摸。
  </div>

  <!-- 亲密度与能量状态条 -->
  <div class="pet-hud-grid">
    <div class="stat" style="background:#0f172a;">
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;">
        <span style="color:#f472b6;">⭐ 亲密羁绊</span>
        <b id="petLevelText" style="color:#fb7185;">Lv.1 (15/100 XP)</b>
      </div>
      <div class="pet-bar-bg">
        <div class="pet-bar-fill" id="petXpBar" style="width:15%;"></div>
      </div>
    </div>
    <div class="stat" style="background:#0f172a;">
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;">
        <span style="color:#38bdf8;">⚡ 活力充沛</span>
        <b id="petEnergyText" style="color:#38bdf8;">100%</b>
      </div>
      <div class="pet-bar-bg">
        <div class="pet-energy-fill" id="petEnergyBar" style="width:100%;"></div>
      </div>
    </div>
  </div>

  <!-- 灵宠第一人称心声日记 -->
  <div class="pet-diary-box">
    <div style="color:#94a3b8;font-size:11px;margin-bottom:3px;display:flex;justify-content:space-between;">
      <span>📖 <b id="petNameLabel">悄悄</b> 的即时心声日记:</span>
      <span id="petStatCounts" style="color:#64748b;">喂:0 梳:0 摸:0 晃:0</span>
    </div>
    <div id="petDiaryText" style="color:#e2e8f0;font-size:12px;">
      "今天刚刚苏醒，期待和主人一起探索世界！"
    </div>
  </div>

  <!-- 隔空投喂小点心菜单与动作快捷键 -->
  <div style="font-size:12px;color:#94a3b8;margin-bottom:6px;">🍰 选取精选点心进行「隔空投喂」:</div>
  <div style="display:flex;gap:6px;margin-bottom:8px;">
    <select id="feedItemSelect" style="flex:1;margin-bottom:0;">
      <option value="草莓奶油大福">🍓 草莓奶油大福 (+20活力, +10羁绊)</option>
      <option value="鲜奶舒芙蕾蛋糕">🍰 鲜奶舒芙蕾蛋糕 (+20活力, +10羁绊)</option>
      <option value="比利时巧脆曲奇">🍪 比利时巧脆曲奇 (+20活力, +10羁绊)</option>
      <option value="彩虹熔岩甜甜圈">🍩 彩虹熔岩甜甜圈 (+20活力, +10羁绊)</option>
      <option value="香甜爆米花">🍿 香甜爆米花 (+20活力, +10羁绊)</option>
    </select>
    <button class="btn-pet btn-feed" style="white-space:nowrap;padding:8px 14px;" onclick="triggerPetFeed()">
      🍰 立即投喂
    </button>
  </div>

  <div class="pet-action-grid">
    <button class="btn-pet btn-groom" onclick="triggerPetAction('groom')">
      <span>✨</span> <span>隔空舒适梳毛</span>
    </button>
    <button class="btn-pet btn-play" onclick="triggerPetAction('play')">
      <span>✋</span> <span>隔空默契击掌</span>
    </button>
    <button class="btn-pet btn-caress" onclick="triggerPetAction('pet')">
      <span>🌸</span> <span>隔空温柔抚摸</span>
    </button>
    <button class="btn-pet" style="background:#475569;" onclick="triggerPetAction('shake')">
      <span>🌀</span> <span>调皮转圈圈</span>
    </button>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px;">
    <button class="btn btn-sec" style="margin-bottom:0;font-size:12px;" onclick="triggerPetAction('toggle_mode')">
      🎨 <span id="avatarModeBtnText">屏显: 灵宠表情 (ON)</span>
    </button>
    <button class="btn btn-sec" style="background:#312e81;border:1px solid #6366f1;color:#a5b4fc;margin-bottom:0;font-size:12px;" onclick="triggerPetAction('sleep')">
      🌙 <span>灵宠晚安入睡</span>
    </button>
  </div>

  <div class="status-bar" id="petFeedback" style="margin-top:6px;color:#f472b6;">
    💡 投喂后屏幕实时呈现迪士尼咀嚼飞屑动效与好感度上扬！
  </div>
</div>

<!-- 板块 A: 业界标准 Wi-Fi 智能配网中心 -->
<div class="card" style="border-left: 4px solid #6366f1;">
  <div class="section-title">
    <span>📶 Wi-Fi 智能网页配网 (STA 局域网)</span>
    <span class="badge" id="staBadge" style="background:#312e81;color:#a5b4fc">检查中...</span>
  </div>
  <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 6px;" id="staStatusText">⚪ 正在读取 Wi-Fi 联网状态...</div>
  
  <div style="margin-bottom: 8px;">
    <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">周边 2.4GHz Wi-Fi (点击快速填入):</div>
    <div class="tag-group" id="apTags">
      <span class="tag" onclick="refreshAPs()">🔄 点击扫描周边 Wi-Fi</span>
    </div>
  </div>

  <input type="text" id="wifiSsidInput" placeholder="Wi-Fi 名称 (SSID)">
  <input type="password" id="wifiPassInput" placeholder="Wi-Fi 密码 (无密码留空)">
  <button class="btn btn-purple" onclick="connectWiFi()">⚡ 连接并保存真实 Wi-Fi (入网)</button>
  <div class="status-bar" id="wifiFeedback">💡 配网成功后 StickS3 自动加入局域网并具备公网访问能力</div>
</div>

<!-- 板块 B: 阿里云百炼 (Model Studio) 设置中心 -->
<div class="card" style="border-left: 4px solid #f59e0b;">
  <div class="section-title">
    <span>⚙️ 阿里云百炼大模型设置中心</span>
    <span class="badge" id="blBadge" style="background:#78350f;color:#fcd34d">未配置</span>
  </div>
  <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 6px;" id="blStatusText">⚪ 正在检查百炼大模型连接状态...</div>

  <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">百炼 DashScope API Key:</div>
  <input type="password" id="blKeyInput" placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx">
  
  <div class="grid" style="margin-bottom: 8px;">
    <div>
      <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">对话音色:</div>
      <div style="display:flex;gap:6px;align-items:center;">
        <select id="blVoiceSelect" style="flex:1;">
          <option value="Tina">Tina (甜美温暖 推荐)</option>
          <option value="Serena">Serena (知性自然)</option>
          <option value="Cindy">Cindy (活泼台湾腔)</option>
          <option value="Raymond">Raymond (清亮男声)</option>
          <option value="Zane">Zane (磁性男声)</option>
          <option value="Katerina">Katerina (成熟御姐)</option>
          <option value="Mia">Mia (温柔细腻)</option>
          <option value="Chloe">Chloe (活力俏皮)</option>
        </select>
        <button class="btn btn-purple" style="margin-bottom:0;padding:7px 11px;font-size:12px;white-space:nowrap;" onclick="previewSelectedVoice()">🔊 试听</button>
      </div>
    </div>
    <div>
      <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">实时大模型:</div>
      <select id="blModelSelect">
        <option value="qwen3.8-omni-flash-realtime">qwen3.8-omni-flash (极速推荐)</option>
        <option value="qwen-omni-turbo-realtime">qwen-omni-turbo</option>
      </select>
    </div>
  </div>

  <button class="btn btn-amber" onclick="saveBailianConfig()">💾 保存配置并连接百炼</button>
  <div class="status-bar" id="blFeedback">💡 密钥持久化加密保存于 StickS3 NVS 分区，重启不丢失</div>
</div>

<!-- 板块 C: 大模型实时流式对话与中途打断控制台 -->
<div class="card" style="border-left: 4px solid #ef4444;">
  <div class="section-title">
    <span>🎙️ 智能大模型问答流 (全双工 + 实时打断)</span>
    <span class="badge" id="chatStateBadge" style="background:#991b1b;color:#fca5a5">待命中</span>
  </div>
  
  <div style="background:#020617;border:1px solid #1e293b;border-radius:8px;padding:10px;margin-bottom:10px;min-height:70px;font-size:13px;line-height:1.5;">
    <div style="color:#38bdf8;margin-bottom:4px;" id="liveUserQuery">🗣️ 问话: 等待你对准 StickS3 麦克风讲话...</div>
    <div style="color:#4ade80;" id="liveAiReply">🤖 回复: 准备就绪，实时流式语音问答中...</div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
    <button class="btn btn-danger" style="margin-bottom:0;" onclick="triggerBargeIn()">⏹ 立即中途打断 (Barge-In)</button>
    <button class="btn btn-sec" style="margin-bottom:0;" onclick="resetChat()">🔄 开启新会话</button>
  </div>
  <div class="status-bar" style="margin-top:8px;">💡 说话过程中任何时候开口或按正面键 A，均可毫秒级打断 AI 播音</div>
</div>

<!-- 板块 M: 全双工实时对话记忆与历史存档 (Flash NVS + PSRAM) -->
<div class="card" style="border-left: 4px solid #10b981;">
  <div class="section-title">
    <span>🧠 全双工实时对话记忆与历史存档</span>
    <span class="badge" id="memCountBadge" style="background:#064e3b;color:#a7f3d0">0 轮记忆</span>
  </div>
  <div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">
    Flash NVS + PSRAM 实时持久化，支持跨会话与断电记忆回忆，多轮上下文自动注入大模型。
  </div>
  <div id="memoryTimeline" style="max-height: 220px; overflow-y: auto; background: #020617; border: 1px solid #1e293b; border-radius: 8px; padding: 8px; margin-bottom: 8px; font-size: 12px;">
    <div style="color: #64748b; text-align: center; padding: 12px;">暂无历史对话记忆</div>
  </div>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
    <button class="btn btn-sec" style="margin-bottom:0;" onclick="refreshMemoryList()">🔄 刷新记忆</button>
    <button class="btn btn-danger" style="margin-bottom:0;" onclick="clearMemory()">🗑️ 清空记忆</button>
  </div>
</div>

<!-- 板块 D: 设备端录音回放 (StickS3 -> 网页) -->
<div class="card" style="border-left: 4px solid #38bdf8;">
  <div class="section-title">
    <span>📻 设备端按键录音回放</span>
    <span class="badge" id="recBadge">10秒内单声道</span>
  </div>
  <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 6px;" id="devRecStatus">⚪ 正在检查设备端录音状态...</div>
  
  <audio id="deviceAudioPlayer" controls preload="none">
    您的浏览器不支持 HTML5 音频播放
  </audio>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
    <button class="btn btn-primary" onclick="playDeviceAudio()">▶ 播放 StickS3 录音</button>
    <button class="btn btn-sec" onclick="triggerDeviceRecord()">🔴 远程控制录音</button>
  </div>
</div>

<!-- 板块 E: 网页端录音下发至设备播放 (针对 iOS Safari 优化) -->
<div class="card" style="border-left: 4px solid #34d399;">
  <div class="section-title">
    <span>🎙️ 网页录音下发 StickS3 播放</span>
    <span class="badge" style="background:#064e3b;color:#6ee7b7">iOS/Android 双模</span>
  </div>
  
  <label class="btn btn-emerald" style="cursor: pointer;">
    📁 选取音频文件 / 语音备忘录上传
    <input type="file" id="audioFileInput" accept="audio/*,.wav,.mp3,.m4a,.aac,.caf" style="display:none">
  </label>

  <button class="btn btn-sec" id="btnLiveRec" onclick="toggleLiveRecord()">
    🎙️ 实时按住/点击录音 (最长 10 秒)
  </button>

  <button class="btn btn-sec" style="background:#1e293b;border:1px solid #059669;color:#6ee7b7;" onclick="sendTestAudio()">
    🎵 生成 16kHz 和弦测试音下发
  </button>

  <div class="status-bar" id="audioStatusHint" style="color: #38bdf8; min-height: 16px;">准备就绪</div>
</div>

<!-- 板块 W: 离线唤醒词【悄悄】管理 -->
<div class="card" style="border-left: 4px solid #f59e0b;">
  <div class="section-title">
    <span>🗣️ 离线唤醒词「悄悄」管理</span>
    <span class="badge" id="wwBadge" style="background:#065f46;color:#6ee7b7">待命中</span>
  </div>
  <div style="font-size:12px;color:#94a3b8;margin-bottom:8px;">
    对准 StickS3 麦克风呼唤 <b>“悄悄”</b>，本地极速离线识别唤醒并接入大模型问答。
  </div>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
    <span style="font-size:13px;color:#cbd5e1;">启用离线唤醒词:</span>
    <input type="checkbox" id="wwEnableCheck" checked onchange="saveWakeWordConfig()" style="width:20px;height:20px;accent-color:#f59e0b;cursor:pointer;">
  </div>
  <div style="margin-bottom:8px;">
    <div style="display:flex;justify-content:space-between;font-size:12px;color:#cbd5e1;margin-bottom:4px;">
      <span>声学识别灵敏度:</span>
      <span id="wwSensVal" style="color:#f59e0b;font-weight:bold;">75%</span>
    </div>
    <input type="range" id="wwSensRange" min="20" max="95" value="75" oninput="document.getElementById('wwSensVal').innerText=this.value+'%'" onchange="saveWakeWordConfig()" style="width:100%;">
  </div>
  <div style="display:flex;gap:8px;">
    <button class="btn btn-primary" onclick="triggerWakeWordSim()" style="background:#d97706;">⚡ 模拟发声唤醒【悄悄】</button>
  </div>
  <div id="wwFeedback" style="font-size:11px;color:#94a3b8;margin-top:6px;">状态: 待命中 (0 次唤醒)</div>
</div>

<!-- 板块 F: 基础通信: 中文/汉字下发 -->
<div class="card">
  <div class="section-title">💬 发送中文/指令到屏幕</div>
  <div class="tag-group">
    <span class="tag" onclick="fill('大模型流式问答就绪')">百炼问答</span>
    <span class="tag" onclick="fill('中途打断测试正常')">打断测试</span>
    <span class="tag" onclick="fill('你好 StickS3')">你好StickS3</span>
    <span class="tag" onclick="fill('WiFi 配网成功')">配网成功</span>
  </div>
  <input type="text" id="msgInput" placeholder="输入任意汉字或指令...">
  <button class="btn btn-primary" onclick="sendMsg()">🚀 发送到 StickS3 屏幕</button>
  <button class="btn btn-sec" onclick="playBeep()">🔔 播放和弦提示音</button>
</div>

<!-- 板块 R: 系统管理与出厂信息重置 -->
<div class="card" style="border-left: 4px solid #ef4444;">
  <div class="section-title">
    <span>⚙️ 系统管理与出厂重置</span>
    <span class="badge" style="background:#7f1d1d;color:#fca5a5;">危急操作区</span>
  </div>
  <div style="font-size: 12px; color: #94a3b8; margin-bottom: 10px;">
    若需要更换网络环境、转交他人或抹除敏感数据，可在此重置对话记忆或一键恢复出厂设置。
  </div>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
    <button class="btn btn-sec" style="margin-bottom:0;color:#fca5a5;border:1px solid #7f1d1d;" onclick="clearMemory()">🗑️ 清空记忆与心声</button>
    <button class="btn btn-danger" style="margin-bottom:0;background:#dc2626;" onclick="factoryReset()">⚠️ 一键恢复出厂设置 (抹除NVS)</button>
  </div>
</div>

<script>
// 音频重采样并转码为标准 16kHz 16-bit Mono WAV Blob
function audioBufferTo16kMonoWav(audioBuffer) {
  var targetSampleRate = 16000;
  var srcRate = audioBuffer.sampleRate;
  var ratio = srcRate / targetSampleRate;
  var inLen = audioBuffer.length;
  var outLen = Math.round(audioBuffer.duration * targetSampleRate);
  if (outLen <= 0) return null;

  var ch0 = audioBuffer.getChannelData(0);
  var ch1 = audioBuffer.numberOfChannels > 1 ? audioBuffer.getChannelData(1) : null;

  var pcmBytes = outLen * 2;
  var buffer = new ArrayBuffer(44 + pcmBytes);
  var view = new DataView(buffer);

  function writeStr(offset, str) {
    for (var i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  }

  writeStr(0, 'RIFF');
  view.setUint32(4, 36 + pcmBytes, true);
  writeStr(8, 'WAVE');
  writeStr(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // Mono
  view.setUint32(24, 16000, true);
  view.setUint32(28, 32000, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeStr(36, 'data');
  view.setUint32(40, pcmBytes, true);

  var offset = 44;
  for (var i = 0; i < outLen; i++) {
    var srcIdx = i * ratio;
    var i0 = Math.floor(srcIdx);
    var i1 = Math.min(i0 + 1, inLen - 1);
    var frac = srcIdx - i0;
    var s0 = ch0[i0];
    var s1 = ch0[i1];
    if (ch1) {
      s0 = (s0 + ch1[i0]) * 0.5;
      s1 = (s1 + ch1[i1]) * 0.5;
    }
    var sample = s0 + frac * (s1 - s0);
    sample = Math.max(-1, Math.min(1, sample));
    var val = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
    view.setInt16(offset, val, true);
    offset += 2;
  }
  return new Blob([view], { type: 'audio/wav' });
}

function uploadWavBlob(blob, filename) {
  var statusHint = document.getElementById('audioStatusHint');
  statusHint.innerText = '正在上传到 StickS3 播放 (' + Math.round(blob.size / 1024) + ' KB)...';
  var fd = new FormData();
  fd.append('audio', blob, filename || 'web_record_16k.wav');
  return fetch('/audio/upload', { method: 'POST', body: fd })
    .then(function(r) { return r.json(); })
    .then(function(res) {
      statusHint.innerText = '✔ 上传成功！StickS3 正在播放中...';
      setTimeout(function() { statusHint.innerText = '准备就绪'; }, 4000);
    })
    .catch(function(err) {
      statusHint.innerText = '❌ 上传失败: ' + err;
    });
}

document.getElementById('audioFileInput').addEventListener('change', function(e) {
  var file = e.target.files[0];
  if (!file) return;
  var statusHint = document.getElementById('audioStatusHint');
  statusHint.innerText = '正在读取音频文件 (' + file.name + ')...';
  var reader = new FileReader();
  reader.onload = function(evt) {
    var AudioCtx = window.AudioContext || window.webkitAudioContext;
    var ctx = new AudioCtx();
    ctx.decodeAudioData(evt.target.result, function(audioBuffer) {
      statusHint.innerText = '正在重采样为 16kHz WAV (' + audioBuffer.duration.toFixed(1) + 's)...';
      var wavBlob = audioBufferTo16kMonoWav(audioBuffer);
      if (wavBlob) {
        uploadWavBlob(wavBlob, file.name);
      } else {
        statusHint.innerText = '❌ 转码失败：音频长度过短';
      }
    }, function(err) {
      statusHint.innerText = '❌ 解码失败: 格式不支持或文件损坏';
    });
  };
  reader.readAsArrayBuffer(file);
});

function sendTestAudio() {
  var statusHint = document.getElementById('audioStatusHint');
  statusHint.innerText = '正在合成 16kHz 双频和弦测试音...';
  var sampleRate = 16000;
  var duration = 1.0;
  var numSamples = Math.round(sampleRate * duration);
  var pcmBytes = numSamples * 2;
  var buffer = new ArrayBuffer(44 + pcmBytes);
  var view = new DataView(buffer);

  function writeStr(offset, str) {
    for (var i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  }
  writeStr(0, 'RIFF');
  view.setUint32(4, 36 + pcmBytes, true);
  writeStr(8, 'WAVE');
  writeStr(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeStr(36, 'data');
  view.setUint32(40, pcmBytes, true);

  var offset = 44;
  for (var i = 0; i < numSamples; i++) {
    var t = i / sampleRate;
    var env = Math.exp(-2.5 * t);
    var s = (Math.sin(2 * Math.PI * 523.25 * t) * 0.5 + Math.sin(2 * Math.PI * 659.25 * t) * 0.5) * env;
    var val = Math.round(s * 28000);
    view.setInt16(offset, val, true);
    offset += 2;
  }
  var testBlob = new Blob([view], { type: 'audio/wav' });
  uploadWavBlob(testBlob, 'chord_test_16k.wav');
}

var mediaRecorder = null;
var audioChunks = [];
var recTimer = null;
var recSec = 0;

function toggleLiveRecord() {
  var btn = document.getElementById('btnLiveRec');
  var statusHint = document.getElementById('audioStatusHint');
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    btn.innerText = '🎙️ 实时按住/点击录音 (最长 10 秒)';
    btn.className = 'btn btn-sec';
    clearInterval(recTimer);
    return;
  }

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusHint.innerHTML = '<span style="color:#fbbf24">💡 提示: 苹果 iOS 限制普通 HTTP 页面访问麦克风。请点击上方【选取音频文件/语音备忘录】或【和弦测试音】！</span>';
    return;
  }

  navigator.mediaDevices.getUserMedia({ audio: true }).then(function(stream) {
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = function(e) {
      if (e.data.size > 0) audioChunks.push(e.data);
    };
    mediaRecorder.onstop = function() {
      stream.getTracks().forEach(function(t) { t.stop(); });
      var rawBlob = new Blob(audioChunks);
      statusHint.innerText = '正在转码 16kHz WAV 并发送...';
      rawBlob.arrayBuffer().then(function(ab) {
        var AudioCtx = window.AudioContext || window.webkitAudioContext;
        var ctx = new AudioCtx();
        ctx.decodeAudioData(ab, function(audioBuffer) {
          var wavBlob = audioBufferTo16kMonoWav(audioBuffer);
          if (wavBlob) uploadWavBlob(wavBlob, 'live_record.wav');
        });
      });
    };
    mediaRecorder.start();
    recSec = 0;
    btn.className = 'btn btn-danger';
    btn.innerText = '⏹ 录音中 (0.0s) 点击停止';
    recTimer = setInterval(function() {
      recSec += 0.5;
      btn.innerText = '⏹ 录音中 (' + recSec.toFixed(1) + 's / 10s) 点击停止';
      if (recSec >= 10.0) {
        toggleLiveRecord();
      }
    }, 500);
  }).catch(function(err) {
    statusHint.innerHTML = '<span style="color:#fbbf24">⚠️ 麦克风无法开启: ' + (err.message || err.name) + '</span>';
  });
}

// 设备端录音
var lastDevAudioId = 0;
var devAudioPlayer = document.getElementById('deviceAudioPlayer');

function playDeviceAudio() {
  var player = document.getElementById('deviceAudioPlayer');
  var devStatus = document.getElementById('devRecStatus');
  if (!player.src || player.src.indexOf('/audio/device_record.wav') === -1) {
    player.src = '/audio/device_record.wav?t=' + Date.now();
  }
  player.load();
  var playPromise = player.play();
  if (playPromise !== undefined) {
    playPromise.then(function() {
      devStatus.innerHTML = '<span style="color:#38bdf8;font-weight:600;">▶ 正在播放 StickS3 录音...</span>';
    }).catch(function(e) {
      devStatus.innerHTML = '<span style="color:#f87171;">⚠️ 播放失败: ' + (e.message || e) + '</span>';
    });
  }
}

function triggerDeviceRecord() {
  fetch('/audio/record_trigger', { method: 'POST', headers: {'Content-Type':'application/x-www-form-urlencoded'}, body: 'action=toggle' })
    .then(function(r) { return r.json(); })
    .then(function() { fetchStatus(); });
}

function fill(t) { document.getElementById('msgInput').value = t; }
function sendMsg() {
  var t = document.getElementById('msgInput').value.trim();
  if(!t) return;
  fetch('/send', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'msg=' + encodeURIComponent(t) })
  .then(function(r) { return r.json(); }).then(function(d) {
    document.getElementById('msgInput').value = '';
  });
}
function playBeep() { fetch('/beep'); }

// ==========================================
// 核心 A: Wi-Fi 智能配网交互逻辑
// ==========================================
function selectSSID(ssid) {
  document.getElementById('wifiSsidInput').value = ssid;
  document.getElementById('wifiPassInput').focus();
}

function refreshAPs() {
  var apBox = document.getElementById('apTags');
  apBox.innerHTML = '<span class="tag">⏳ 正在扫描周边 AP...</span>';
  fetch('/wifi/scan_list')
    .then(function(r) { return r.json(); })
    .then(function(aps) {
      if (!aps || aps.length === 0) {
        apBox.innerHTML = '<span class="tag" onclick="refreshAPs()">🔄 未发现 AP，点击重试</span>';
        return;
      }
      var html = '<span class="tag" onclick="refreshAPs()" style="background:#475569;">🔄 刷新</span>';
      for (var i = 0; i < aps.length; i++) {
        var ap = aps[i];
        html += '<span class="tag" onclick="selectSSID(\'' + ap.ssid + '\')">' + ap.ssid + ' (' + ap.rssi + 'dBm)</span>';
      }
      apBox.innerHTML = html;
    })
    .catch(function() {
      apBox.innerHTML = '<span class="tag" onclick="refreshAPs()">🔄 扫描失败，点击重试</span>';
    });
}

function connectWiFi() {
  var ssid = document.getElementById('wifiSsidInput').value.trim();
  var pass = document.getElementById('wifiPassInput').value;
  var fb = document.getElementById('wifiFeedback');
  if (!ssid) {
    fb.innerHTML = '<span style="color:#f87171">⚠️ 请输入或选择 Wi-Fi 名称</span>';
    return;
  }
  fb.innerHTML = '<span style="color:#38bdf8">⏳ 正在连接 "' + ssid + '"，请稍候约 5~10 秒...</span>';
  fetch('/wifi/connect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'ssid=' + encodeURIComponent(ssid) + '&pass=' + encodeURIComponent(pass)
  }).then(function(r) { return r.json(); })
    .then(function(res) {
      fb.innerHTML = '<span style="color:#4ade80">✔ 连接指令已下发！StickS3 正在握手中...</span>';
    })
    .catch(function(err) {
      fb.innerHTML = '<span style="color:#f87171">❌ 发送配网指令失败: ' + err + '</span>';
    });
}

// ==========================================
// 核心 B: 阿里云百炼配置交互逻辑与即时试听
// ==========================================
function saveBailianConfig() {
  var key = document.getElementById('blKeyInput').value.trim();
  var voice = document.getElementById('blVoiceSelect').value;
  var model = document.getElementById('blModelSelect').value;
  var fb = document.getElementById('blFeedback');

  fb.innerHTML = '<span style="color:#38bdf8">⏳ 正在保存配置并应用音色/模型设置...</span>';

  fetch('/bailian/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'key=' + encodeURIComponent(key) + '&voice=' + encodeURIComponent(voice) + '&model=' + encodeURIComponent(model)
  }).then(function(r) { return r.json(); })
    .then(function(res) {
      if (res.status === 'ok') {
        fb.innerHTML = '<span style="color:#4ade80">✔ 配置已生效！当前音色: <b>' + (res.voice || voice) + '</b>，正在同步会话...</span>';
      } else {
        fb.innerHTML = '<span style="color:#f87171">⚠️ ' + (res.message || '保存失败，请检查 API Key') + '</span>';
      }
    })
    .catch(function(err) {
      fb.innerHTML = '<span style="color:#f87171">❌ 保存百炼配置失败: ' + err + '</span>';
    });
}

function previewSelectedVoice() {
  var voice = document.getElementById('blVoiceSelect').value;
  var fb = document.getElementById('blFeedback');
  fb.innerHTML = '<span style="color:#38bdf8">🔊 正在请求 StickS3 以 <b>' + voice + '</b> 音色发声试听...</span>';
  fetch('/bailian/preview_voice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'voice=' + encodeURIComponent(voice)
  }).then(function(r) { return r.json(); })
    .then(function(d) {
      if (d.status === 'ok') {
        fb.innerHTML = '<span style="color:#4ade80">✔ 已触发 <b>' + voice + '</b> 音色自我介绍试听播报！请聆听音响。</span>';
      } else {
        fb.innerHTML = '<span style="color:#f87171">⚠️ 试听失败: ' + (d.message || '') + '</span>';
      }
    }).catch(function(e) {
      fb.innerHTML = '<span style="color:#f87171">❌ 试听网络错误: ' + e + '</span>';
    });
}

// ==========================================
// 核心 M: 全双工实时对话记忆与历史存档管理
// ==========================================
function refreshMemoryList() {
  fetch('/memory/list')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var badge = document.getElementById('memCountBadge');
      var tl = document.getElementById('memoryTimeline');
      if (!d.turns || d.turns.length === 0) {
        badge.innerText = '0 轮记忆';
        badge.style.background = '#334155';
        tl.innerHTML = '<div style="color: #64748b; text-align: center; padding: 12px;">暂无历史对话记忆</div>';
        return;
      }
      badge.innerText = d.total + ' 轮记忆';
      badge.style.background = '#064e3b';
      var html = '';
      for (var i = 0; i < d.turns.length; i++) {
        var t = d.turns[i];
        html += '<div style="background:#0f172a;border:1px solid #1e293b;border-radius:6px;padding:6px 8px;margin-bottom:6px;">' +
                '<div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:11px;margin-bottom:2px;">' +
                '<span><b>#' + t.id + '</b> [' + (t.voice || 'Tina') + ']</span><span>' + t.time + '</span>' +
                '</div>' +
                '<div style="color:#38bdf8;margin-bottom:2px;">🗣️ ' + t.user + '</div>' +
                '<div style="color:#4ade80;">🤖 ' + t.ai + '</div>' +
                '</div>';
      }
      tl.innerHTML = html;
    }).catch(function(){});
}

function clearMemory() {
  if (!confirm('确定清空 StickS3 当前全部对话记忆与 Flash 存档吗？')) return;
  fetch('/memory/clear', { method: 'POST' })
    .then(function() {
      refreshMemoryList();
    });
}

function factoryReset() {
  if (!confirm('⚠️ 警告：恢复出厂设置将彻底擦除设备保存的所有 Wi-Fi 密码、百炼 API-Key、唤醒词设定与所有历史对话记忆，并自动重启设备。\n\n确认要继续恢复出厂设置吗？')) return;
  fetch('/system/factory_reset', { method: 'POST' })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      alert('设备已成功执行恢复出厂设置并正在重启！\n请等待设备重启完成后，重新连接 "StickS3-Buddy" 初始热点进行配网。');
    })
    .catch(function(e) {
      alert('指令已发送，设备正在重启中...');
    });
}

// ==========================================
// 核心 W: 离线唤醒词「悄悄」设置
// ==========================================
function saveWakeWordConfig() {
  var en = document.getElementById('wwEnableCheck').checked;
  var sens = document.getElementById('wwSensRange').value;
  var fb = document.getElementById('wwFeedback');
  fb.innerText = '正在保存唤醒词设置...';
  fetch('/wakeword/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'enabled=' + (en ? 'true' : 'false') + '&sensitivity=' + sens + '&timeout_sec=8'
  }).then(function(r) { return r.json(); }).then(function() {
    fb.innerHTML = '<span style="color:#4ade80">✔ 唤醒词设置已更新并持久化</span>';
  }).catch(function(e) {
    fb.innerHTML = '<span style="color:#f87171">❌ 保存失败: ' + e + '</span>';
  });
}

function triggerWakeWordSim() {
  fetch('/wakeword/trigger', { method: 'POST' }).then(function() {
    var fb = document.getElementById('wwFeedback');
    fb.innerHTML = '<span style="color:#f59e0b">⚡ 已触发模拟唤醒词【悄悄】！</span>';
  });
}

// ==========================================
// 核心 C: 实时打断 (Barge-In) 与新会话控制
// ==========================================
function triggerBargeIn() {
  fetch('/bailian/interrupt', { method: 'POST' })
    .then(function(r) { return r.json(); })
    .then(function() {
      document.getElementById('chatStateBadge').innerText = '已打断';
      document.getElementById('chatStateBadge').style.background = '#ea580c';
    });
}

function resetChat() {
  fetch('/bailian/new_chat', { method: 'POST' });
}

// ==========================================
// 核心 P: 拓麻歌子「隔空投喂」与动作交互
// ==========================================
function triggerPetFeed() {
  var item = document.getElementById('feedItemSelect').value;
  triggerPetAction('feed', item);
}

function triggerPetAction(action, item) {
  var fb = document.getElementById('petFeedback');
  var body = 'action=' + encodeURIComponent(action);
  if (item) body += '&item=' + encodeURIComponent(item);

  if (action === 'feed') {
    fb.innerHTML = '<span style="color:#f472b6">🍰 正在隔空投喂【' + item + '】...</span>';
  } else if (action === 'groom') {
    fb.innerHTML = '<span style="color:#38bdf8">✨ 正在为灵宠梳理毛发 (Pixie Dust)...</span>';
  } else if (action === 'play') {
    fb.innerHTML = '<span style="color:#fbbf24">✋ 默契击掌！耶~</span>';
  } else if (action === 'pet') {
    fb.innerHTML = '<span style="color:#34d399">🌸 温柔抚摸中，心底暖洋洋~</span>';
  } else if (action === 'shake') {
    fb.innerHTML = '<span style="color:#f59e0b">🌀 调皮晃动！眼睛冒金星~</span>';
  } else if (action === 'sleep') {
    fb.innerHTML = '<span style="color:#a5b4fc">🌙 呼噜呼噜，晚安好梦~</span>';
  } else if (action === 'toggle_mode') {
    fb.innerHTML = '<span style="color:#38bdf8">🎨 正在切换屏幕显像模式...</span>';
  }

  fetch('/pet/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body
  }).then(function(r) { return r.json(); })
    .then(function(d) {
      if (d.status === 'ok') {
        fb.innerHTML = '<span style="color:#4ade80">✔ 互动成功！' + (d.diary || '') + '</span>';
        updatePetHud(d);
      }
    }).catch(function(e) {
      fb.innerHTML = '<span style="color:#f87171">❌ 互动失败: ' + e + '</span>';
    });
}

function updatePetHud(d) {
  if (d.level !== undefined) {
    document.getElementById('petLevelText').innerText = 'Lv.' + d.level + ' (' + d.xp + '/100 XP)';
    document.getElementById('petXpBar').style.width = Math.min(100, Math.max(0, d.xp)) + '%';
  }
  if (d.energy !== undefined) {
    document.getElementById('petEnergyText').innerText = d.energy + '%';
    document.getElementById('petEnergyBar').style.width = Math.min(100, Math.max(0, d.energy)) + '%';
  }
  if (d.name) {
    document.getElementById('petNameLabel').innerText = d.name;
  }
  if (d.diary) {
    document.getElementById('petDiaryText').innerText = '"' + d.diary + '"';
  }
  if (d.mood_name) {
    var b = document.getElementById('petMoodBadge');
    b.innerText = d.mood_name;
  }
  if (d.feeds !== undefined) {
    document.getElementById('petStatCounts').innerText = '喂:' + d.feeds + ' 梳:' + d.grooms + ' 摸:' + d.pets + ' 晃:' + d.shakes;
  }
  if (d.avatar_mode !== undefined) {
    document.getElementById('avatarModeBtnText').innerText = '屏显: ' + (d.avatar_mode ? '灵宠表情 (ON)' : '系统遥测 (OFF)');
  }
}

// ==========================================
// 周期性轮询与动态状态看板刷新
// ==========================================
function fetchStatus() {
  // 1. Wi-Fi STA 状态轮询
  fetch('/wifi/status').then(function(r) { return r.json(); }).then(function(d) {
    var staBadge = document.getElementById('staBadge');
    var staText = document.getElementById('staStatusText');
    var lanIp = document.getElementById('lanIp');

    var wfb = document.getElementById('wifiFeedback');
    if (d.sta_state === 'connected') {
      staBadge.innerText = '已联网 (' + d.sta_ip + ')';
      staBadge.style.background = '#065f46';
      staBadge.style.color = '#6ee7b7';
      staText.innerHTML = '<span style="color:#4ade80">🟢 已连接至 <b>' + d.sta_ssid + '</b> | IP: <b>' + d.sta_ip + '</b> | 信号: ' + d.sta_rssi + ' dBm</span>';
      lanIp.innerText = d.sta_ip;
      if (wfb && (wfb.innerText.indexOf('握手') !== -1 || wfb.innerText.indexOf('正在连接') !== -1)) {
        wfb.innerHTML = '<span style="color:#4ade80">✔ 已成功连入 ' + d.sta_ssid + '！局域网 IP: <b>' + d.sta_ip + '</b></span>';
      }
    } else if (d.sta_state === 'connecting') {
      staBadge.innerText = '连接中...';
      staBadge.style.background = '#854d0e';
      staBadge.style.color = '#fef08a';
      staText.innerHTML = '<span style="color:#facc15">🟡 正在连接 Wi-Fi: ' + d.sta_ssid + '...</span>';
    } else if (d.sta_state === 'failed') {
      staBadge.innerText = '未联网 (仅热点)';
      staBadge.style.background = '#7f1d1d';
      staBadge.style.color = '#fca5a5';
      staText.innerHTML = '<span style="color:#f87171">🔴 连接失败或密码错误，请重新选择配网</span>';
      lanIp.innerText = '未联网';
      if (wfb && (wfb.innerText.indexOf('握手') !== -1 || wfb.innerText.indexOf('正在连接') !== -1)) {
        wfb.innerHTML = '<span style="color:#f87171">❌ 连接失败或超时，请检查密码重新连接</span>';
      }
    } else {
      staBadge.innerText = '未配网';
      staBadge.style.background = '#334155';
      staBadge.style.color = '#94a3b8';
      staText.innerHTML = '<span style="color:#94a3b8">⚪ 尚未配置可用 Wi-Fi，请在下方选择 AP 配网</span>';
      lanIp.innerText = '未联网';
    }
  }).catch(function(){});

  // 2. 阿里云百炼大模型状态轮询
  fetch('/bailian/status').then(function(r) { return r.json(); }).then(function(d) {
    var blBadge = document.getElementById('blBadge');
    var blText = document.getElementById('blStatusText');
    var blHeader = document.getElementById('blStateHeader');
    var chatBadge = document.getElementById('chatStateBadge');

    blHeader.innerText = d.state_name;
    blBadge.innerText = d.state_name;

    if (d.state_code === 3) { // LISTENING
      blBadge.style.background = '#0284c7'; blBadge.style.color = '#fff';
      chatBadge.innerText = '● 正在聆听中'; chatBadge.style.background = '#0284c7';
    } else if (d.state_code === 4) { // THINKING
      blBadge.style.background = '#d97706'; blBadge.style.color = '#fff';
      chatBadge.innerText = '⚡ 思考推理中'; chatBadge.style.background = '#d97706';
    } else if (d.state_code === 5) { // SPEAKING
      blBadge.style.background = '#059669'; blBadge.style.color = '#fff';
      chatBadge.innerText = '▶ AI 回复中'; chatBadge.style.background = '#059669';
    } else if (d.state_code === 6) { // INTERRUPTED
      blBadge.style.background = '#dc2626'; blBadge.style.color = '#fff';
      chatBadge.innerText = '⏹ 中途打断'; chatBadge.style.background = '#dc2626';
    } else if (d.state_code === 2) { // CONNECTED_IDLE
      blBadge.style.background = '#15803d'; blBadge.style.color = '#fff';
      chatBadge.innerText = '待命中'; chatBadge.style.background = '#334155';
    } else {
      blBadge.style.background = '#334155'; blBadge.style.color = '#94a3b8';
      chatBadge.innerText = d.state_name; chatBadge.style.background = '#334155';
    }

    blText.innerHTML = '大模型状态: <b>' + d.state_name + '</b> | 当前音色: <b>' + (d.configured_voice || 'Tina') + '</b> | 累计打断: <b>' + d.interrupts + '</b> 次' + (d.state_code === 7 && d.error ? ' | 错误: <span style="color:#f87171">' + d.error + '</span>' : '');

    if (d.has_key && !document.getElementById('blKeyInput').placeholder.includes('已保存')) {
      document.getElementById('blKeyInput').placeholder = 'sk-•••••••••••••••• (已保存，留空保持不变)';
    }
    if (d.configured_voice && !window._voice_initialized) {
      window._voice_initialized = true;
      var sel = document.getElementById('blVoiceSelect');
      for (var i = 0; i < sel.options.length; i++) {
        if (sel.options[i].value === d.configured_voice) {
          sel.selectedIndex = i;
          break;
        }
      }
    }

    if (d.user_query) {
      document.getElementById('liveUserQuery').innerText = '🗣️ 问话: ' + d.user_query;
    }
    if (d.ai_reply) {
      document.getElementById('liveAiReply').innerText = '🤖 回复: ' + d.ai_reply;
    }
  }).catch(function(){});

  // 3. 原生音频与姿态遥测
  fetch('/audio/status').then(function(r) { return r.json(); }).then(function(d) {
    var devStatus = document.getElementById('devRecStatus');
    var player = document.getElementById('deviceAudioPlayer');
    if (d.is_recording) {
      devStatus.innerHTML = '<span style="color:#ef4444;font-weight:600;">🔴 StickS3 正在录音中 (' + (d.rec_ms / 1000).toFixed(1) + 's / 10s)...</span>';
    } else if (d.has_device_audio) {
      if (devStatus.innerText.indexOf('正在播放') === -1) {
        devStatus.innerHTML = '<span style="color:#4ade80;font-weight:600;">🟢 最新录音 #' + d.device_audio_id + ' (' + d.device_audio_duration_sec.toFixed(1) + '秒, ' + Math.round(d.device_audio_bytes / 1024) + ' KB)</span>';
      }
      if (d.device_audio_id !== lastDevAudioId) {
        lastDevAudioId = d.device_audio_id;
        player.src = '/audio/device_record.wav?id=' + d.device_audio_id;
        player.load();
      }
    } else {
      devStatus.innerHTML = '<span style="color:#94a3b8">⚪ 暂无本地录音</span>';
    }
  }).catch(function(){});

  fetch('/status').then(function(r) { return r.json(); }).then(function(d) {
    document.getElementById('imu').innerText = 'R:' + d.roll + '° P:' + d.pitch + '°';
  }).catch(function(){});

  // 4. 离线唤醒词状态轮询
  fetch('/wakeword/status').then(function(r) { return r.json(); }).then(function(d) {
    var b = document.getElementById('wwBadge');
    var fb = document.getElementById('wwFeedback');
    if (b) {
      b.innerText = d.enabled ? (d.wake_window_open ? '已唤醒 (推流中)' : '待命中') : '已关闭';
      b.style.background = d.enabled ? (d.wake_window_open ? '#d97706' : '#065f46') : '#334155';
    }
    if (fb && fb.innerText.indexOf('正在保存') === -1) {
      fb.innerHTML = '累计唤醒: <b>' + d.total_wakes + '</b> 次 | 灵敏度: ' + d.sensitivity + '% | 目标词: 「' + d.name + '」' + (d.wake_window_open ? ' <b style="color:#f59e0b">● 唤醒窗口剩余 ' + (d.remaining_ms / 1000).toFixed(1) + 's</b>' : '');
    }
  }).catch(function(){});

  // 5. 拓麻歌子灵宠状态轮询
  fetch('/pet/status').then(function(r) { return r.json(); }).then(function(d) {
    updatePetHud(d);
  }).catch(function(){});
}

setInterval(fetchStatus, 1200);
setInterval(refreshMemoryList, 3000);
fetchStatus();
refreshMemoryList();
refreshAPs();
</script>
</body>
</html>)rawliteral";

class StickS3WiFi {
public:
    StickS3WiFi() 
        : _initialized(false), _is_scanning(false), _last_scan_time(0),
          _scan_interval_ms(25000), _networks_found(0), _top_ssid("None"),
          _top_rssi(-100), _tcp_server(8080), _web_server(80),
          _msg_counter(0), _last_roll(0.0f), _last_pitch(0.0f),
          _upload_audio_buf(nullptr), _upload_audio_size(0) {}

    static StickS3WiFi& getInstance() {
        static StickS3WiFi instance;
        return instance;
    }

    void setMessageCallback(WiFiMessageCallback cb) {
        _on_message = cb;
    }

    void updateTelemetry(float roll, float pitch) {
        _last_roll = roll;
        _last_pitch = pitch;
    }

    void begin() {
        if (_initialized) return;
        Serial.println("[WIFI] Initializing AP+STA Concurrent Mode...");

        // 1. 设置 AP+STA 双模工作与自动重连 (遵循 BLE 共存机制)
        WiFi.mode(WIFI_AP_STA);
        WiFi.setAutoReconnect(true);
        delay(40);

        // 2. 启动 SoftAP 免密热点 (默认 IP: 192.168.4.1) 并设置最大发射功率 (+19.5dBm)
        bool ap_ok = WiFi.softAP("StickS3-Buddy", "", 1, 0, 4);
        WiFi.setTxPower(WIFI_POWER_19_5dBm);
        Serial.printf("[WIFI-AP] SoftAP 'StickS3-Buddy': %s (IP: %s)\n",
                      ap_ok ? "ONLINE" : "FAILED",
                      WiFi.softAPIP().toString().c_str());

        // 3. 启动 TCP 服务器 (Port 8080)
        _tcp_server.begin();
        _tcp_server.setNoDelay(true);
        Serial.println("[WIFI-TCP] TCP Server listening on 192.168.4.1:8080");

        // 4. 启动 UDP 服务器 (Port 8080)
        _udp_server.begin(8080);
        Serial.println("[WIFI-UDP] UDP Server listening on 192.168.4.1:8080");

        // 5. 配置并启动 HTTP Web Server (Port 80)
        setupWebServer();
        _web_server.begin();
        Serial.println("[WIFI-WEB] Mobile Web Console running on http://192.168.4.1:80");

        // 6. 初始化 NVS 配网与百炼客户端
        StickS3ConfigManager::getInstance().begin();
        StickS3BailianClient::getInstance().begin();

        _initialized = true;

        // 7. 启动首次环境 AP 异步扫描
        triggerScan();
        Serial.println("[WIFI] Wi-Fi Multi-Channel Subsystem ONLINE!");
    }

    void triggerScan() {
        if (!_initialized) return;
        if (_is_scanning) return;
        // 若百炼语音连接活跃，严格禁止执行 WiFi 扫描，避免 RF 离频导致 WebSocket 丢包中断与 errno=11
        if (StickS3BailianClient::getInstance().isConnected()) {
            return;
        }

        WiFi.scanNetworks(true, true);
        _is_scanning = true;
        _last_scan_time = millis();
    }

    void update() {
        if (!_initialized) return;

        // A. 处理 Web Server 请求
        _web_server.handleClient();

        // B. 处理 TCP 客户端连接与收发
        handleTCP();

        // C. 处理 UDP 数据报文
        handleUDP();

        // D. 更新 STA 配网状态机
        StickS3ConfigManager::getInstance().update();

        // E. 轮询环境 AP 异步扫描状态
        if (_is_scanning) {
            int16_t status = WiFi.scanComplete();
            if (status >= 0) {
                _networks_found = status;
                _is_scanning = false;
                _top_ssid = "None";
                _top_rssi = -120;

                for (int i = 0; i < _networks_found; ++i) {
                    int32_t rssi = WiFi.RSSI(i);
                    if (rssi > _top_rssi) {
                        _top_rssi = rssi;
                        _top_ssid = WiFi.SSID(i);
                    }
                }

                _cached_scan_json = "{\"type\":\"wifi_list\",\"count\":" + String(_networks_found) + ",\"networks\":[";
                int limit = _networks_found < 8 ? _networks_found : 8;
                for (int i = 0; i < limit; ++i) {
                    if (i > 0) _cached_scan_json += ",";
                    _cached_scan_json += "{\"ssid\":\"" + WiFi.SSID(i) + "\",\"rssi\":" + String(WiFi.RSSI(i)) + "}";
                }
                _cached_scan_json += "]}";

                Serial.printf("[WIFI] Scan complete! %d APs found. Top: \"%s\" (%ddBm)\n",
                              _networks_found, _top_ssid.c_str(), _top_rssi);
            } else if (status == WIFI_SCAN_FAILED) {
                _is_scanning = false;
            }
        } else {
            // 仅在 STA 尚未连接成功且百炼未在线时，才进行低频周期性 AP 扫描
            if (!StickS3ConfigManager::getInstance().isStaConnected() &&
                millis() - _last_scan_time > _scan_interval_ms) {
                triggerScan();
            }
        }
    }

    int getNetworkCount() const { return _networks_found; }
    bool isScanning() const { return _is_scanning; }
    String getTopSSID() const { return _top_ssid; }
    int getTopRSSI() const { return _top_rssi; }
    int getConnectedStations() const { return WiFi.softAPgetStationNum(); }
    String getApSSID() const { return "StickS3-Buddy"; }
    String getApIP() const { return WiFi.softAPIP().toString(); }

    String getScanResultsJSON() const {
        if (_cached_scan_json.length() > 0) {
            return _cached_scan_json;
        }
        return "{\"type\":\"wifi_list\",\"count\":" + String(_networks_found) + ",\"networks\":[]}";
    }

private:
    void setupWebServer() {
        // 允许 CORS 跨域通信 (全面消除微信小程序、开发工具模拟器与跨域控制台的 CORS 阻断)
        _web_server.enableCORS(true);

        _web_server.onNotFound([this]() {
            if (_web_server.method() == HTTP_OPTIONS) {
                _web_server.sendHeader("Access-Control-Allow-Origin", "*");
                _web_server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
                _web_server.sendHeader("Access-Control-Allow-Headers", "*");
                _web_server.send(204);
                return;
            }
            _web_server.send(404, "text/plain", "Not Found");
        });

        // 主页
        _web_server.on("/", HTTP_GET, [this]() {
            _web_server.send_P(200, "text/html; charset=utf-8", INDEX_HTML);
        });

        // ==========================================
        // 核心板块 1: 业界标准 Wi-Fi 智能配网端点
        // ==========================================

        // 获取 AP 扫描列表 (JSON Array)
        _web_server.on("/wifi/scan_list", HTTP_GET, [this]() {
            int n = WiFi.scanComplete();
            if (n < 0) {
                triggerScan();
                _web_server.send(200, "application/json", "[]");
                return;
            }
            String json = "[";
            int limit = (n > 10) ? 10 : n;
            for (int i = 0; i < limit; i++) {
                if (i > 0) json += ",";
                json += "{\"ssid\":\"" + WiFi.SSID(i) + "\",\"rssi\":" + String(WiFi.RSSI(i)) + "}";
            }
            json += "]";
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 提交 Wi-Fi 配网参数并触发连接 (支持手机共享热点与流量上限设置)
        _web_server.on("/wifi/connect", HTTP_POST, [this]() {
            String ssid = _web_server.hasArg("ssid") ? _web_server.arg("ssid") : "";
            String pass = _web_server.hasArg("pass") ? _web_server.arg("pass") : "";
            bool is_hs = _web_server.hasArg("is_hotspot") ? (_web_server.arg("is_hotspot") == "1" || _web_server.arg("is_hotspot") == "true") : false;
            uint32_t limit_mb = _web_server.hasArg("limit_mb") ? _web_server.arg("limit_mb").toInt() : 100;
            bool cutoff = _web_server.hasArg("cutoff") ? (_web_server.arg("cutoff") == "1" || _web_server.arg("cutoff") == "true") : true;

            ssid.trim();
            if (ssid.length() == 0) {
                _web_server.send(400, "application/json", "{\"status\":\"error\",\"msg\":\"empty_ssid\"}");
                return;
            }

            // 保存到 NVS 并启动异步连接
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            cfg_mgr.saveWiFiConfig(ssid, pass);
            cfg_mgr.saveHotspotConfig(is_hs, limit_mb, cutoff);
            cfg_mgr.startConnectSTA(ssid, pass);

            char json_resp[256];
            snprintf(json_resp, sizeof(json_resp),
                     "{\"status\":\"connecting\",\"ssid\":\"%s\",\"is_hotspot\":%s,\"limit_mb\":%u}",
                     ssid.c_str(), is_hs ? "true" : "false", (unsigned)limit_mb);
            _web_server.send(200, "application/json; charset=utf-8", json_resp);
        });

        // 手机共享热点数据流量遥测端点
        _web_server.on("/hotspot/traffic", HTTP_GET, [this]() {
            auto& cfg = StickS3ConfigManager::getInstance();
            char json[300];
            snprintf(json, sizeof(json),
                     "{\"is_hotspot\":%s,\"used_mb\":%.2f,\"limit_mb\":%u,\"remaining_mb\":%.2f,\"cutoff_active\":%s,\"cutoff_enabled\":%s,\"warning_issued\":%s}",
                     cfg.isHotspot() ? "true" : "false",
                     cfg.getHotspotUsedMB(),
                     (unsigned)cfg.getHotspotLimitMB(),
                     cfg.getHotspotRemainingMB(),
                     cfg.isHotspotCutoffActive() ? "true" : "false",
                     cfg.isHotspotCutoffEnabled() ? "true" : "false",
                     cfg.isHotspotWarningIssued() ? "true" : "false");
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 手机共享热点策略动态配置端点
        _web_server.on("/hotspot/config", HTTP_POST, [this]() {
            bool is_hs = _web_server.hasArg("is_hotspot") ? (_web_server.arg("is_hotspot") == "1" || _web_server.arg("is_hotspot") == "true") : true;
            uint32_t limit_mb = _web_server.hasArg("limit_mb") ? _web_server.arg("limit_mb").toInt() : 100;
            bool cutoff = _web_server.hasArg("cutoff") ? (_web_server.arg("cutoff") == "1" || _web_server.arg("cutoff") == "true") : true;

            StickS3ConfigManager::getInstance().saveHotspotConfig(is_hs, limit_mb, cutoff);
            _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"msg\":\"hotspot_configured\"}");
        });

        // 手机共享热点流量统计重置
        _web_server.on("/hotspot/reset_traffic", HTTP_POST, [this]() {
            StickS3ConfigManager::getInstance().resetHotspotTraffic();
            _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"msg\":\"traffic_reset\"}");
        });

        // 查询 Wi-Fi STA 联网状态
        _web_server.on("/wifi/status", HTTP_GET, [this]() {
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            String st = "idle";
            if (cfg_mgr.isStaConnected()) st = "connected";
            else if (cfg_mgr.getStaState() == STA_STATE_CONNECTING) st = "connecting";
            else if (cfg_mgr.getStaState() == STA_STATE_FAILED) st = "failed";

            char json[300];
            snprintf(json, sizeof(json),
                     "{\"sta_state\":\"%s\",\"sta_ip\":\"%s\",\"sta_ssid\":\"%s\",\"sta_rssi\":%d,\"is_hotspot\":%s,\"hs_used_mb\":%.2f,\"hs_limit_mb\":%u}",
                     st.c_str(), cfg_mgr.getStaIP().c_str(),
                     cfg_mgr.getConfig().wifi_ssid.c_str(), cfg_mgr.getStaRSSI(),
                     cfg_mgr.isHotspot() ? "true" : "false",
                     cfg_mgr.getHotspotUsedMB(),
                     (unsigned)cfg_mgr.getHotspotLimitMB());
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // ==========================================
        // 核心板块 2: 阿里云百炼大模型设置端点
        // ==========================================

        // 保存百炼配置 (支持在线热切换音色)
        _web_server.on("/bailian/config", HTTP_POST, [this]() {
            String key = _web_server.hasArg("key") ? _web_server.arg("key") : "";
            String voice = _web_server.hasArg("voice") ? _web_server.arg("voice") : "Tina";
            String model = _web_server.hasArg("model") ? _web_server.arg("model") : "qwen3.8-omni-flash-realtime";
            String prompt = _web_server.hasArg("prompt") ? _web_server.arg("prompt") : "";
            key.trim();

            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            if (key.length() == 0) {
                // 若前端留空，则复用 NVS 中已保存的 key
                key = cfg_mgr.getConfig().bailian_key;
            }

            if (key.length() > 0) {
                if (!StickS3ConfigManager::isVoiceSupported(voice)) {
                    voice = "Tina";
                }
                bool need_reconnect = false;
                if (key != cfg_mgr.getConfig().bailian_key || model != cfg_mgr.getConfig().bailian_model) {
                    need_reconnect = true;
                }
                cfg_mgr.saveBailianConfig(key, model, voice, "", prompt);

                int vol = -1;
                if (_web_server.hasArg("volume")) vol = _web_server.arg("volume").toInt();
                else if (_web_server.hasArg("speaker_volume")) vol = _web_server.arg("speaker_volume").toInt();
                else if (_web_server.hasArg("plain")) {
                    JsonDocument pdoc;
                    if (!deserializeJson(pdoc, _web_server.arg("plain"))) {
                        if (!pdoc["volume"].isNull()) vol = pdoc["volume"].as<int>();
                        else if (!pdoc["speaker_volume"].isNull()) vol = pdoc["speaker_volume"].as<int>();
                    }
                }
                if (vol >= 10 && vol <= 100) {
                    cfg_mgr.saveSpeakerVolume((uint8_t)vol);
                    sticks3::StickS3BLESync::getInstance().updateSnapshots();
                }

                auto& bl = StickS3BailianClient::getInstance();
                if (need_reconnect || !bl.isConnected()) {
                    if (cfg_mgr.isStaConnected() && cfg_mgr.hasBailianKey()) {
                        bl.connect();
                    }
                } else if (bl.isConnected()) {
                    // 在线热切换音色并清空旧文本
                    bl.switchVoice(voice, false);
                }
                _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"voice\":\"" + voice + "\"}");
            } else {
                _web_server.send(400, "application/json; charset=utf-8", "{\"status\":\"error\",\"message\":\"API Key 不能为空，请输入百炼 Key\"}");
            }
        });

        // 即时音色试听播报 (支持 application/x-www-form-urlencoded 与 application/json)
        _web_server.on("/bailian/preview_voice", HTTP_POST, [this]() {
            String voice = "";
            if (_web_server.hasArg("voice")) {
                voice = _web_server.arg("voice");
            } else if (_web_server.hasArg("plain")) {
                JsonDocument doc;
                DeserializationError err = deserializeJson(doc, _web_server.arg("plain"));
                if (!err) {
                    voice = doc["voice"] | (doc["value"] | "");
                }
            }
            if (voice.length() > 0 && StickS3ConfigManager::isVoiceSupported(voice)) {
                StickS3BailianClient::getInstance().switchVoice(voice, true);
                _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"voice\":\"" + voice + "\"}");
            } else {
                _web_server.send(400, "application/json; charset=utf-8", "{\"status\":\"error\",\"message\":\"不支持的音色\"}");
            }
        });

        // 对话记忆历史时间线列表
        _web_server.on("/memory/list", HTTP_GET, [this]() {
            String json = StickS3MemoryStore::getInstance().getHistoryJSON();
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 一键清空对话记忆
        _web_server.on("/memory/clear", HTTP_POST, [this]() {
            StickS3BailianClient::getInstance().clearMemory();
            _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"cleared\"}");
        });

        // 查询百炼大模型状态
        _web_server.on("/bailian/status", HTTP_GET, [this]() {
            auto& bl = StickS3BailianClient::getInstance();
            auto& cfg = StickS3ConfigManager::getInstance().getConfig();
            JsonDocument doc;
            doc["state_code"] = (int)bl.getState();
            doc["state_name"] = bl.getStateName();
            doc["user_query"] = bl.getUserQuery();
            doc["ai_reply"] = bl.getAiReply();
            doc["interrupts"] = bl.getTotalInterrupts();
            doc["error"] = bl.getLastError();
            doc["configured_voice"] = cfg.bailian_voice;
            doc["configured_model"] = cfg.bailian_model;
            doc["prompt"] = cfg.bailian_prompt;
            doc["has_key"] = (cfg.bailian_key.length() > 10);
            if (cfg.bailian_key.length() >= 8) {
                doc["masked_key"] = cfg.bailian_key.substring(0, 4) + "••••••••" + cfg.bailian_key.substring(cfg.bailian_key.length() - 4);
            } else if (cfg.bailian_key.length() > 0) {
                doc["masked_key"] = "••••••••";
            } else {
                doc["masked_key"] = "";
            }
            doc["is_connected"] = bl.isConnected();
            doc["memory_turns"] = StickS3MemoryStore::getInstance().getTurnCount();

            String json;
            serializeJson(doc, json);
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 远程触发中途打断 (Barge-In)
        _web_server.on("/bailian/interrupt", HTTP_POST, [this]() {
            StickS3BailianClient::getInstance().interrupt("Web-UI");
            _web_server.send(200, "application/json", "{\"status\":\"interrupted\"}");
        });

        // 开启新对话
        _web_server.on("/bailian/new_chat", HTTP_POST, [this]() {
            StickS3BailianClient::getInstance().startNewConversation();
            _web_server.send(200, "application/json", "{\"status\":\"ok\"}");
        });

        // 模拟/下发文本问答至百炼 (触发大模型实时语音回复，支持 JSON 与表单两种传参)
        _web_server.on("/bailian/send_text", HTTP_POST, [this]() {
            String text = "";
            if (_web_server.hasArg("text")) {
                text = _web_server.arg("text");
            } else if (_web_server.hasArg("plain")) {
                JsonDocument doc;
                if (!deserializeJson(doc, _web_server.arg("plain"))) {
                    text = doc["text"] | "";
                }
            }
            text.trim();
            if (text.length() > 0) {
                bool ok = StickS3BailianClient::getInstance().sendTextMessage(text);
                _web_server.send(200, "application/json; charset=utf-8",
                                 ok ? "{\"status\":\"ok\"}" : "{\"status\":\"error\",\"msg\":\"send_failed\"}");
            } else {
                _web_server.send(400, "application/json", "{\"status\":\"error\",\"msg\":\"empty_text\"}");
            }
        });

        // 重连百炼 WSS
        _web_server.on("/bailian/reconnect", HTTP_POST, [this]() {
            StickS3BailianClient::getInstance().connect();
            _web_server.send(200, "application/json", "{\"status\":\"reconnecting\"}");
        });

        // 查询离线唤醒词状态
        _web_server.on("/wakeword/status", HTTP_GET, [this]() {
            auto& ww = StickS3WakeWordEngine::getInstance();
            auto& bl = StickS3BailianClient::getInstance();
            auto& cfg = StickS3ConfigManager::getInstance().getConfig();

            JsonDocument doc;
            doc["enabled"] = ww.isEnabled();
            doc["name"] = StickS3WakeWordEngine::WAKE_WORD_NAME;
            doc["word"] = StickS3WakeWordEngine::WAKE_WORD_NAME;
            doc["sensitivity"] = ww.getSensitivity();
            doc["total_wakes"] = ww.getTotalWakeCount();
            doc["last_wake_ms"] = ww.getLastWakeTime();
            doc["last_confidence"] = ww.getLastConfidence();
            doc["timeout_sec"] = cfg.wakeword_timeout_sec;
            doc["wake_window_open"] = bl.isWakeWindowOpen();
            doc["window_open"] = bl.isWakeWindowOpen();
            doc["remaining_ms"] = bl.getWakeWindowRemainingMs();
            doc["window_remaining_ms"] = bl.getWakeWindowRemainingMs();

            String json;
            serializeJson(doc, json);
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 配置离线唤醒词
        _web_server.on("/wakeword/config", HTTP_POST, [this]() {
            auto& ww = StickS3WakeWordEngine::getInstance();
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            auto& cfg = cfg_mgr.getConfig();

            bool enabled = cfg.wakeword_enabled;
            if (_web_server.hasArg("enabled")) {
                String en_str = _web_server.arg("enabled");
                enabled = (en_str == "true" || en_str == "1" || en_str == "on");
            }

            uint8_t sens = cfg.wakeword_sensitivity;
            if (_web_server.hasArg("sensitivity")) {
                sens = (uint8_t)_web_server.arg("sensitivity").toInt();
            }

            uint16_t tout = cfg.wakeword_timeout_sec;
            if (_web_server.hasArg("timeout_sec")) {
                tout = (uint16_t)_web_server.arg("timeout_sec").toInt();
            } else if (_web_server.hasArg("timeout")) {
                tout = (uint16_t)_web_server.arg("timeout").toInt();
            }

            ww.setEnabled(enabled);
            ww.setSensitivity(sens);
            cfg_mgr.saveWakeWordConfig(enabled, sens, tout);

            JsonDocument res_doc;
            res_doc["status"] = "ok";
            res_doc["enabled"] = enabled;
            res_doc["sensitivity"] = sens;
            res_doc["timeout_sec"] = tout;
            String json_resp;
            serializeJson(res_doc, json_resp);
            _web_server.send(200, "application/json; charset=utf-8", json_resp);
        });

        // 软件模拟触发唤醒词
        _web_server.on("/wakeword/trigger", HTTP_POST, [this]() {
            float conf = 96.0f;
            if (_web_server.hasArg("confidence")) {
                conf = _web_server.arg("confidence").toFloat();
            }
            StickS3WakeWordEngine::getInstance().forceTrigger(conf);
            StickS3BailianClient::getInstance().onWakeWordDetected(conf, 650);
            _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"action\":\"triggered\"}");
        });

        // 系统全维度诊断指标监控 (CPU, 内存, I/O 总线, 任务堆栈)
        _web_server.on("/system/metrics", HTTP_GET, [this]() {
            auto& bl = StickS3BailianClient::getInstance();
            auto& audio = StickS3Audio::getInstance();

            JsonDocument doc;
            
            // 1. CPU & Task
            JsonObject cpu = doc["cpu"].to<JsonObject>();
            cpu["loop_fps"] = getSystemLoopFPS();
            cpu["audio_stack_hwm"] = audio.getAudioTaskStackHighWaterMark();

            // 2. Memory (Internal SRAM & PSRAM)
            JsonObject mem = doc["memory"].to<JsonObject>();
            mem["free_internal_heap"] = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
            mem["largest_internal_block"] = (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL);
            mem["min_free_heap"] = (uint32_t)esp_get_minimum_free_heap_size();
            mem["free_psram"] = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
            mem["largest_psram_block"] = (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);

            // 3. I/O & Bus
            JsonObject io = doc["io"].to<JsonObject>();
            io["i2c_tx_count"] = (uint32_t)getI2CTransactionCount();
            io["i2c_lock_failures"] = (uint32_t)getI2CLockFailures();
            io["audio_ring_avail"] = (uint32_t)audio.getStreamBufferAvailable();
            io["is_streaming_llm"] = audio.isStreamingLLM();
            io["mic_rms"] = audio.getRawRMS();

            // 4. Bailian State
            JsonObject bailian = doc["bailian"].to<JsonObject>();
            bailian["state_code"] = (int)bl.getState();
            bailian["state_name"] = bl.getStateName();
            bailian["interrupts"] = bl.getTotalInterrupts();
            bailian["user_query_len"] = bl.getUserQuery().length();
            bailian["ai_reply_len"] = bl.getAiReply().length();

            String json;
            serializeJson(doc, json);
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 5. 恢复出厂设置 (抹除全部 NVS 配置与记忆分区并软重启)
        _web_server.on("/system/factory_reset", HTTP_POST, [this]() {
            _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"msg\":\"Factory reset executed. Device rebooting...\"}");
            delay(150);
            StickS3ConfigManager::getInstance().clearAllConfig();
            StickS3MemoryStore::getInstance().clearMemory();
            Serial.println("[SYSTEM] Factory Reset complete! Restarting in 300ms...");
            delay(300);
            esp_restart();
        });

        // 6. 系统软重启 (保持 NVS 配置)
        _web_server.on("/system/reboot", HTTP_POST, [this]() {
            _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"msg\":\"Device rebooting...\"}");
            Serial.println("[SYSTEM] Remote reboot requested. Restarting in 300ms...");
            delay(300);
            esp_restart();
        });

        // ==========================================
        // 双向音频端点：设备录音流出与网页音频上传
        // ==========================================

        // 播音音量获取与动态设置 (支持 GET / POST 全动词与 CORS 跨域)
        auto handleVolumeReq = [this]() {
            _web_server.sendHeader("Access-Control-Allow-Origin", "*");
            _web_server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
            _web_server.sendHeader("Access-Control-Allow-Headers", "*");
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            int vol = -1;
            if (_web_server.hasArg("volume")) {
                vol = _web_server.arg("volume").toInt();
            } else if (_web_server.hasArg("val")) {
                vol = _web_server.arg("val").toInt();
            } else if (_web_server.hasArg("v")) {
                vol = _web_server.arg("v").toInt();
            } else if (_web_server.hasArg("plain")) {
                String plain = _web_server.arg("plain");
                plain.trim();
                if (plain.startsWith("{")) {
                    JsonDocument doc;
                    if (!deserializeJson(doc, plain)) {
                        if (!doc["volume"].isNull()) vol = doc["volume"].as<int>();
                        else if (!doc["value"].isNull()) vol = doc["value"].as<int>();
                    }
                } else if (plain.indexOf("volume=") >= 0) {
                    int idx = plain.indexOf("volume=");
                    vol = plain.substring(idx + 7).toInt();
                } else if (plain.toInt() > 0) {
                    vol = plain.toInt();
                }
            }
            if (vol >= 0 && vol <= 100) {
                cfg_mgr.saveSpeakerVolume((uint8_t)vol);
                StickS3Audio::getInstance().playTone(1200, 70, 0.50f);
                sticks3::StickS3BLESync::getInstance().updateSnapshots();
                _web_server.send(200, "application/json; charset=utf-8",
                                 "{\"ok\":true,\"volume\":" + String(vol) + "}");
            } else {
                _web_server.send(200, "application/json; charset=utf-8",
                                 "{\"ok\":true,\"volume\":" + String((unsigned)cfg_mgr.getSpeakerVolume()) + "}");
            }
        };

        _web_server.on("/audio/volume", HTTP_POST, handleVolumeReq);
        _web_server.on("/audio/volume", HTTP_GET, handleVolumeReq);

        // 播音音量即时试听 (支持 GET / POST，满足浏览器直测与小程序无阻调用)
        auto handleTestReq = [this]() {
            _web_server.sendHeader("Access-Control-Allow-Origin", "*");
            _web_server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
            _web_server.sendHeader("Access-Control-Allow-Headers", "*");
            if (_web_server.hasArg("volume")) {
                int v = _web_server.arg("volume").toInt();
                if (v >= 0 && v <= 100) {
                    StickS3ConfigManager::getInstance().saveSpeakerVolume((uint8_t)v);
                    sticks3::StickS3BLESync::getInstance().updateSnapshots();
                }
            }
            StickS3Audio::getInstance().playChime(CHIME_SUCCESS);
            _web_server.send(200, "application/json; charset=utf-8", "{\"ok\":true,\"msg\":\"chime_played\"}");
        };
        _web_server.on("/audio/test", HTTP_POST, handleTestReq);
        _web_server.on("/audio/test", HTTP_GET, handleTestReq);

        _web_server.on("/audio/status", HTTP_GET, [this]() {
            auto& audio = StickS3Audio::getInstance();
            auto& cfg_mgr = StickS3ConfigManager::getInstance();
            char json[280];
            snprintf(json, sizeof(json),
                     "{\"is_recording\":%s,\"rec_ms\":%u,\"has_device_audio\":%s,\"device_audio_id\":%u,"
                     "\"device_audio_bytes\":%u,\"device_audio_duration_sec\":%.1f,\"is_playing\":%s,\"play_progress\":%.2f,\"speaker_volume\":%u}",
                     audio.isRecording() ? "true" : "false",
                     (unsigned)audio.getRecordDurationMs(),
                     audio.hasDeviceAudio() ? "true" : "false",
                     (unsigned)audio.getDeviceAudioId(),
                     (unsigned)audio.getWavSize(),
                     (float)audio.getRecordDurationMs() / 1000.0f,
                     audio.isPlayingStream() ? "true" : "false",
                     audio.getPlaybackProgress(),
                     (unsigned)cfg_mgr.getSpeakerVolume());
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        _web_server.on("/audio/device_record.wav", HTTP_GET, [this]() {
            auto& audio = StickS3Audio::getInstance();
            if (!audio.hasDeviceAudio() || audio.getWavSize() == 0) {
                _web_server.send(404, "text/plain", "No audio recorded on StickS3 yet");
                return;
            }
            _web_server.setContentLength(audio.getWavSize());
            _web_server.sendHeader("Content-Disposition", "inline; filename=\"device_record.wav\"");
            _web_server.sendHeader("Accept-Ranges", "none");
            _web_server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
            _web_server.sendHeader("Pragma", "no-cache");
            _web_server.sendHeader("Expires", "0");
            _web_server.send(200, "audio/wav", "");
            
            WiFiClient client = _web_server.client();
            const uint8_t* p = audio.getWavData();
            size_t left = audio.getWavSize();
            while (left > 0 && client.connected()) {
                size_t ch = (left > 2048) ? 2048 : left;
                size_t w = client.write(p, ch);
                if (w == 0) break;
                p += w;
                left -= w;
            }
        });

        _web_server.on("/audio/upload", HTTP_POST, [this]() {
            if (_upload_audio_size > 44) {
                Serial.printf("[WEB-AUDIO] Upload finished! %u bytes. Triggering StickS3 speaker playback...\n",
                              (unsigned)_upload_audio_size);
                StickS3Audio::getInstance().startPlayback(_upload_audio_buf, _upload_audio_size);
                _web_server.send(200, "application/json; charset=utf-8",
                                 "{\"status\":\"ok\",\"size\":" + String(_upload_audio_size) + "}");
            } else {
                _web_server.send(400, "application/json", "{\"status\":\"error\",\"msg\":\"audio_too_short\"}");
            }
        }, [this]() {
            HTTPUpload& upload = _web_server.upload();
            if (upload.status == UPLOAD_FILE_START) {
                _upload_audio_size = 0;
                if (!_upload_audio_buf) {
                    if (psramFound()) {
                        _upload_audio_buf = (uint8_t*)ps_malloc(StickS3Audio::MAX_UPLOAD_BYTES);
                    } else {
                        _upload_audio_buf = (uint8_t*)malloc(StickS3Audio::MAX_UPLOAD_BYTES);
                    }
                }
            } else if (upload.status == UPLOAD_FILE_WRITE) {
                if (_upload_audio_buf && _upload_audio_size + upload.currentSize <= StickS3Audio::MAX_UPLOAD_BYTES) {
                    memcpy(_upload_audio_buf + _upload_audio_size, upload.buf, upload.currentSize);
                    _upload_audio_size += upload.currentSize;
                }
            }
        });

        _web_server.on("/audio/record_trigger", HTTP_POST, [this]() {
            String act = _web_server.hasArg("action") ? _web_server.arg("action") : "toggle";
            auto& audio = StickS3Audio::getInstance();
            if (act == "start" || (act == "toggle" && !audio.isRecording())) {
                audio.startRecording(10000);
                _web_server.send(200, "application/json", "{\"status\":\"recording_started\"}");
            } else if (act == "stop" || (act == "toggle" && audio.isRecording())) {
                audio.stopRecording();
                _web_server.send(200, "application/json", "{\"status\":\"recording_stopped\",\"audio_id\":" + String(audio.getDeviceAudioId()) + "}");
            } else {
                _web_server.send(400, "application/json", "{\"status\":\"unknown_action\"}");
            }
        });

        // 接收汉字/文本发送上屏
        auto handleSend = [this]() {
            String msg = "";
            if (_web_server.hasArg("msg")) msg = _web_server.arg("msg");
            else if (_web_server.hasArg("plain")) msg = _web_server.arg("plain");
            msg.trim();
            if (msg.length() > 0) {
                _msg_counter++;
                if (_on_message) _on_message(msg, "Web/HTTP");
                _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"ack\":" + String(_msg_counter) + "}");
            } else {
                _web_server.send(400, "application/json", "{\"status\":\"empty\"}");
            }
        };
        _web_server.on("/send", HTTP_POST, handleSend);
        _web_server.on("/send", HTTP_GET, handleSend);

        _web_server.on("/beep", HTTP_GET, [this]() {
            if (_on_message) _on_message("beep", "Web/Beep");
            _web_server.send(200, "application/json", "{\"status\":\"beep_triggered\"}");
        });

        _web_server.on("/status", HTTP_GET, [this]() {
            char json[128];
            snprintf(json, sizeof(json), "{\"roll\":%.1f,\"pitch\":%.1f,\"aps\":%d,\"clients\":%d}",
                     _last_roll, _last_pitch, _networks_found, WiFi.softAPgetStationNum());
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // ==========================================
        // 核心板块 P: 灵宠伴侣拓麻歌子互动与隔空投喂端点
        // ==========================================
        _web_server.on("/pet/status", HTTP_GET, [this]() {
            auto& avatar = StickS3Avatar::getInstance();
            const auto& st = avatar.getStats();
            AvatarMood m = avatar.getMood();
            String mood_name = "常态待命";
            if (m == MOOD_LISTEN) mood_name = "聆听中";
            else if (m == MOOD_THINK) mood_name = "思考中";
            else if (m == MOOD_SPEAK) mood_name = "解答中";
            else if (m == MOOD_HAPPY) mood_name = "开心";
            else if (m == MOOD_DIZZY) mood_name = "晕眩";
            else if (m == MOOD_SHOCK) mood_name = "惊吓";
            else if (m == MOOD_SLEEP) mood_name = "呼噜入睡";
            else if (m == MOOD_CURIOUS) mood_name = "好奇";
            else if (m == MOOD_PROUD) mood_name = "傲娇";
            else if (m == MOOD_EAT) mood_name = "进食中";
            else if (m == MOOD_GROOM) mood_name = "梳毛中";
            else if (m == MOOD_WINK) mood_name = "击掌中";

            String json = "{";
            json += "\"name\":\"" + st.pet_name + "\",";
            json += "\"mood_id\":" + String((int)m) + ",";
            json += "\"mood_name\":\"" + mood_name + "\",";
            json += "\"level\":" + String(st.intimacy_level) + ",";
            json += "\"xp\":" + String(st.intimacy_xp) + ",";
            json += "\"energy\":" + String(st.energy) + ",";
            json += "\"feeds\":" + String(st.total_feeds) + ",";
            json += "\"grooms\":" + String(st.total_grooms) + ",";
            json += "\"pets\":" + String(st.total_pets) + ",";
            json += "\"shakes\":" + String(st.total_shakes) + ",";
            auto& cfg = StickS3ConfigManager::getInstance();
            json += "\"diary\":\"" + st.current_diary + "\",";
            json += "\"avatar_mode\":" + String(avatar.isAvatarMode() ? "true" : "false") + ",";
            json += "\"speaker_volume\":" + String((unsigned)cfg.getSpeakerVolume()) + ",";
            json += "\"is_hotspot\":" + String(cfg.isHotspot() ? "true" : "false") + ",";
            json += "\"hs_used_mb\":" + String(cfg.getHotspotUsedMB(), 2) + ",";
            json += "\"hs_limit_mb\":" + String(cfg.getHotspotLimitMB()) + ",";
            json += "\"hs_cutoff\":" + String(cfg.isHotspotCutoffActive() ? "true" : "false");
            json += "}";
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        _web_server.on("/pet/memories", HTTP_GET, [this]() {
            String json = StickS3MemoryStore::getInstance().getHistoryJSON();
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        _web_server.on("/pet/action", HTTP_POST, [this]() {
            String act = _web_server.hasArg("action") ? _web_server.arg("action") : "";
            String item = _web_server.hasArg("item") ? _web_server.arg("item") : "";
            act.toLowerCase();
            act.trim();

            auto& avatar = StickS3Avatar::getInstance();
            auto& audio = StickS3Audio::getInstance();

            if (act == "feed") {
                if (item.length() == 0) item = "草莓奶油大福";
                avatar.feed(item);
                audio.playChime(CHIME_SUCCESS);
            } else if (act == "groom") {
                avatar.groom();
                audio.playChime(CHIME_SUCCESS);
            } else if (act == "play") {
                avatar.play();
                audio.playTone(1800, 40, 0.45f);
            } else if (act == "pet") {
                avatar.pet();
                audio.playChime(CHIME_SUCCESS);
            } else if (act == "shake") {
                avatar.shake();
                audio.playTone(800, 60, 0.35f);
            } else if (act == "sleep") {
                avatar.sleep();
            } else if (act == "wake") {
                avatar.wake();
                audio.playTone(1200, 50, 0.45f);
            } else if (act == "toggle_mode" || act == "mode") {
                avatar.toggleAvatarMode();
                audio.playTone(1500, 25, 0.40f);
            } else if (act == "mood") {
                String m_str = _web_server.hasArg("mood") ? _web_server.arg("mood") : "";
                String clean;
                AvatarMood m = avatar.parseEmotionTag("[E:" + m_str + "]", clean);
                avatar.setMood(m);
            }

            const auto& st = avatar.getStats();
            String json = "{\"status\":\"ok\",\"action\":\"" + act + "\",\"level\":" + String(st.intimacy_level) +
                          ",\"xp\":" + String(st.intimacy_xp) + ",\"energy\":" + String(st.energy) +
                          ",\"diary\":\"" + st.current_diary + "\",\"avatar_mode\":" + String(avatar.isAvatarMode() ? "true" : "false") + "}";
            _web_server.send(200, "application/json; charset=utf-8", json);
        });
    }

    void handleTCP() {
        WiFiClient client = _tcp_server.available();
        if (client) {
            String rx = "";
            uint32_t t0 = millis();
            while (client.connected() && millis() - t0 < 80) {
                while (client.available()) {
                    char c = client.read();
                    rx += c;
                }
                if (rx.length() > 0) break;
                delay(2);
            }
            rx.trim();
            if (rx.length() > 0) {
                _msg_counter++;
                client.printf("[StickS3 TCP ACK #%u]: %s\n", _msg_counter, rx.c_str());
                client.flush();
                if (_on_message) _on_message(rx, "TCP-8080");
            }
            client.stop();
        }
    }

    void handleUDP() {
        int packetSize = _udp_server.parsePacket();
        if (packetSize > 0) {
            char buf[256];
            int len = _udp_server.read(buf, sizeof(buf) - 1);
            if (len > 0) {
                buf[len] = '\0';
                String msg = String(buf);
                msg.trim();
                if (msg.length() > 0) {
                    _msg_counter++;
                    _udp_server.beginPacket(_udp_server.remoteIP(), _udp_server.remotePort());
                    _udp_server.printf("[StickS3 UDP ACK #%u]: %s\n", _msg_counter, msg.c_str());
                    _udp_server.endPacket();
                    if (_on_message) _on_message(msg, "UDP-8080");
                }
            }
        }
    }

    bool _initialized;
    bool _is_scanning;
    uint32_t _last_scan_time;
    uint32_t _scan_interval_ms;
    int _networks_found;
    String _top_ssid;
    int _top_rssi;
    String _cached_scan_json;

    WiFiServer _tcp_server;
    WiFiUDP _udp_server;
    WebServer _web_server;
    WiFiMessageCallback _on_message;
    uint32_t _msg_counter;
    float _last_roll;
    float _last_pitch;

    uint8_t* _upload_audio_buf;
    size_t _upload_audio_size;
};

} // namespace sticks3
