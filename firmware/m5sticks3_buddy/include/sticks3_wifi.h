/**
 * firmware/m5sticks3_buddy/include/sticks3_wifi.h
 * -----------------------------------------------
 * M5Stack StickS3 2.4GHz Wi-Fi (802.11 b/g/n) 全功能网络通信子系统：
 * 1. 射频模式：
 *    - WIFI_AP_STA 双模并行运行 (SoftAP 免密热点 + STA 后台环境 AP 嗅探)
 *    - 运行在 ESP32-S3 双核架构下，与 BLE NUS 无缝时分复用共存
 * 2. 核心通信通道：
 *    - SoftAP: SSID="StickS3-Buddy", IP="192.168.4.1" (免密极速连接)
 *    - TCP Server: 监听端口 8080，微信小程序“WiFi调试助手”/“TCP UDP助手”即连即发
 *    - UDP Server: 监听端口 8080，支持 UDP 调试报文与即时回显
 *    - HTTP Web Server: 监听端口 80，手机浏览器直连控制台（支持汉字提交与实时遥测）
 * 3. 消息统一分发：
 *    - 提供 setMessageCallback() 将来自 TCP / UDP / Web 的汉字指令统一交由主流程处理
 */

#pragma once

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <functional>
#include "sticks3_audio.h"

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
<title>StickS3 灵方双向音频与终端控制台</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 12px; }
.card { background: #1e293b; border-radius: 12px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border: 1px solid #334155; }
h1 { font-size: 16px; margin: 0 0 4px 0; color: #38bdf8; display: flex; align-items: center; gap: 6px; }
.sub { font-size: 12px; color: #94a3b8; margin-bottom: 10px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; }
.stat { background: #0f172a; padding: 8px 10px; border-radius: 8px; }
.stat-val { font-size: 14px; font-weight: bold; color: #4ade80; margin-top: 2px; }
input[type=text] { width: 100%; box-sizing: border-box; padding: 11px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; margin-bottom: 8px; }
.btn { display: block; width: 100%; box-sizing: border-box; padding: 12px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: 0.2s; text-align: center; text-decoration: none; }
.btn-primary { background: #0284c7; color: white; margin-bottom: 8px; }
.btn-primary:active { background: #0369a1; }
.btn-emerald { background: #059669; color: white; margin-bottom: 8px; }
.btn-emerald:active { background: #047857; }
.btn-sec { background: #334155; color: #cbd5e1; margin-bottom: 8px; }
.btn-sec:active { background: #1e293b; }
.btn-danger { background: #dc2626; color: white; margin-bottom: 8px; }
.tag-group { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.tag { background: #334155; color: #38bdf8; font-size: 12px; padding: 5px 9px; border-radius: 6px; cursor: pointer; }
.status-bar { font-size: 11px; color: #94a3b8; text-align: center; margin-top: 6px; }
.badge { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; background: #334155; color: #93c5fd; }
audio { width: 100%; height: 38px; border-radius: 8px; margin-top: 8px; outline: none; }
.section-title { font-weight: 600; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
</style>
</head>
<body>

<div class="card">
  <h1>🤖 StickS3 灵方双向音频控制台</h1>
  <div class="sub">WiFi热点: <b>StickS3-Buddy</b> | 终端IP: <b>192.168.4.1</b></div>
  <div class="grid">
    <div class="stat"><div>姿态俯仰 / 横滚</div><div class="stat-val" id="imu">0° / 0°</div></div>
    <div class="stat"><div>环境 Wi-Fi</div><div class="stat-val" id="wifi">扫描中...</div></div>
  </div>
</div>

<!-- 核心板块 1: 设备端录音回放 (StickS3 -> 网页) -->
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
  <div class="status-bar">💡 按 StickS3 正面主键 A 随时录制 10 秒内音频，网页端自动同步</div>
</div>

<!-- 核心板块 2: 网页端录音下发至设备播放 (网页 -> StickS3, 针对 iOS Safari 优化) -->
<div class="card" style="border-left: 4px solid #34d399;">
  <div class="section-title">
    <span>🎙️ 网页录音下发 StickS3 播放</span>
    <span class="badge" style="background:#064e3b;color:#6ee7b7">iOS/Android 双模</span>
  </div>
  
  <!-- 通用及 iOS Safari 专用音频文件通道 (去除 capture 属性，严禁调起相机) -->
  <label class="btn btn-emerald" style="cursor: pointer;">
    📁 选取音频文件 / 语音备忘录上传
    <input type="file" id="audioFileInput" accept="audio/*,.wav,.mp3,.m4a,.aac,.caf" style="display:none">
  </label>

  <!-- 现代浏览器实时麦克风录音通道 (Android / PC Chrome) -->
  <button class="btn btn-sec" id="btnLiveRec" onclick="toggleLiveRecord()">
    🎙️ 实时按住/点击录音 (最长 10 秒)
  </button>

  <!-- 一键测试和弦下发 (免麦克风授权极速验证喇叭发声) -->
  <button class="btn btn-sec" style="background:#1e293b;border:1px solid #059669;color:#6ee7b7;" onclick="sendTestAudio()">
    🎵 生成 16kHz 和弦测试音下发 (iPhone 免授权极速试听)
  </button>

  <div class="status-bar" id="audioStatusHint" style="color: #38bdf8; min-height: 16px;">准备就绪</div>
  <div class="status-bar">💡 iPhone 优先选取语音备忘录/音频文件；Android/PC 可直接点击实时录音</div>
</div>

<!-- 基础通信板块: 中文/汉字下发与测试 -->
<div class="card">
  <div class="section-title">💬 发送中文/信息到屏幕</div>
  <div class="tag-group">
    <span class="tag" onclick="fill('灵方机器人 就绪')">灵方机器人</span>
    <span class="tag" onclick="fill('双向音频测试通过')">音频测试</span>
    <span class="tag" onclick="fill('你好 StickS3')">你好StickS3</span>
    <span class="tag" onclick="fill('微信WiFi助手 连接成功')">微信连接</span>
  </div>
  <input type="text" id="msgInput" placeholder="输入任意汉字或指令...">
  <button class="btn btn-primary" onclick="sendMsg()">🚀 发送到 StickS3 屏幕</button>
  <button class="btn btn-sec" onclick="playBeep()">🔔 播放和弦提示音</button>
  <div class="status-bar" id="statusHint">支持微信小程序: WiFi调试助手 / TCP 192.168.4.1:8080</div>
</div>

<script>
// 音频重采样并转码为标准 16kHz 16-bit Mono WAV Blob (纯 JS，零外部依赖，100% 浏览器兼容)
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

// 上传 WAV 音频 Blob 到 StickS3 并触发喇叭回放
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

// 监听音频文件选择 (iOS 原生语音备忘录 / 本地音频文件上传)
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

// 生成 1 秒 16kHz 双频和弦测试 WAV 并上传 (C5 523Hz + E5 659Hz，免授权极速验证喇叭)
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
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // Mono
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

// 现代浏览器实时麦克风录音处理 (Android / PC Chrome)
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

  // 严禁在此调用 file input click，彻底杜绝 iOS 调起相机
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusHint.innerHTML = '<span style="color:#fbbf24">💡 提示: 苹果 iOS 限制普通 HTTP 页面访问麦克风。请点击上方【📁 选取音频文件/语音备忘录】或【🎵 和弦测试音】！</span>';
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
    statusHint.innerHTML = '<span style="color:#fbbf24">⚠️ 麦克风无法开启: ' + (err.message || err.name) + '，请使用上方文件选取或测试音</span>';
  });
}

// 设备端录音状态同步与控制
var lastDevAudioId = 0;
var devAudioPlayer = document.getElementById('deviceAudioPlayer');

devAudioPlayer.onerror = function() {
  var err = devAudioPlayer.error;
  var msg = '未知错误';
  if (err) {
    if (err.code === 1) msg = '播放被中断';
    else if (err.code === 2) msg = '网络加载错误';
    else if (err.code === 3) msg = '音频解码失败 (格式或损坏)';
    else if (err.code === 4) msg = '音频源不支持或无录音文件';
  }
  var devStatus = document.getElementById('devRecStatus');
  devStatus.innerHTML = '<span style="color:#ef4444;font-weight:600;">❌ 播放错误: ' + msg + ' (代码 ' + (err ? err.code : 0) + ')</span>';
};

function playDeviceAudio() {
  var player = document.getElementById('deviceAudioPlayer');
  var devStatus = document.getElementById('devRecStatus');
  if (!player.src || player.src === '' || player.src.indexOf('/audio/device_record.wav') === -1) {
    player.src = '/audio/device_record.wav?t=' + Date.now();
  }
  player.load();
  var playPromise = player.play();
  if (playPromise !== undefined) {
    playPromise.then(function() {
      devStatus.innerHTML = '<span style="color:#38bdf8;font-weight:600;">▶ 正在播放 StickS3 录音...</span>';
    }).catch(function(e) {
      console.warn("Audio play error:", e);
      devStatus.innerHTML = '<span style="color:#f87171;">⚠️ 播放失败: ' + (e.message || e) + ' (请先按键录音)</span>';
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
    document.getElementById('statusHint').innerText = '屏幕已更新: ' + t;
    document.getElementById('msgInput').value = '';
  }).catch(function() { document.getElementById('statusHint').innerText = '发送完成'; });
}
function playBeep() { fetch('/beep'); }

function fetchStatus() {
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
      devStatus.innerHTML = '<span style="color:#94a3b8">⚪ 暂无录音 (按 StickS3 正面主键 A 开始录音)</span>';
    }
  }).catch(function(){});

  fetch('/status').then(function(r) { return r.json(); }).then(function(d) {
    document.getElementById('imu').innerText = 'R:' + d.roll + ' P:' + d.pitch;
    document.getElementById('wifi').innerText = d.aps + ' 个AP';
  }).catch(function(){});
}

setInterval(fetchStatus, 1500);
fetchStatus();
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

        // 1. 设置 AP+STA 双模工作
        WiFi.mode(WIFI_AP_STA);
        delay(40);

        // 2. 启动 SoftAP 免密热点 (默认 IP: 192.168.4.1)
        bool ap_ok = WiFi.softAP("StickS3-Buddy", "", 1, 0, 4);
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

        _initialized = true;

        // 6. 启动首次环境 AP 异步扫描
        triggerScan();
        Serial.println("[WIFI] Wi-Fi Multi-Channel Subsystem ONLINE!");
    }

    // 触发非阻塞异步扫描
    void triggerScan() {
        if (!_initialized) return;
        if (_is_scanning) return;

        WiFi.scanNetworks(true, true);
        _is_scanning = true;
        _last_scan_time = millis();
    }

    // 周期性轮询与网络事件分发 (在 loop() 中高频调用)
    void update() {
        if (!_initialized) return;

        // A. 处理 Web Server 请求
        _web_server.handleClient();

        // B. 处理 TCP 客户端连接与收发 (微信小程序 WiFi/TCP 调试助手)
        handleTCP();

        // C. 处理 UDP 数据报文 (UDP 调试工具)
        handleUDP();

        // D. 轮询环境 AP 异步扫描状态
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
                int limit = _networks_found < 5 ? _networks_found : 5;
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
            if (millis() - _last_scan_time > _scan_interval_ms) {
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
        // 主页
        _web_server.on("/", HTTP_GET, [this]() {
            _web_server.send_P(200, "text/html; charset=utf-8", INDEX_HTML);
        });

        // ==========================================
        // 双向音频端点：设备录音流出与网页音频上传
        // ==========================================

        // 1. 获取设备端音频与录音状态
        _web_server.on("/audio/status", HTTP_GET, [this]() {
            auto& audio = StickS3Audio::getInstance();
            char json[256];
            snprintf(json, sizeof(json),
                     "{\"is_recording\":%s,\"rec_ms\":%u,\"has_device_audio\":%s,\"device_audio_id\":%u,"
                     "\"device_audio_bytes\":%u,\"device_audio_duration_sec\":%.1f,\"is_playing\":%s,\"play_progress\":%.2f}",
                     audio.isRecording() ? "true" : "false",
                     (unsigned)audio.getRecordDurationMs(),
                     audio.hasDeviceAudio() ? "true" : "false",
                     (unsigned)audio.getDeviceAudioId(),
                     (unsigned)audio.getWavSize(),
                     (float)audio.getRecordDurationMs() / 1000.0f,
                     audio.isPlayingStream() ? "true" : "false",
                     audio.getPlaybackProgress());
            _web_server.send(200, "application/json; charset=utf-8", json);
        });

        // 2. 下载并播放设备端 16kHz 16-bit Mono WAV 录音文件
        _web_server.on("/audio/device_record.wav", HTTP_GET, [this]() {
            auto& audio = StickS3Audio::getInstance();
            if (!audio.hasDeviceAudio() || audio.getWavSize() == 0) {
                _web_server.send(404, "text/plain", "No audio recorded on StickS3 yet");
                return;
            }
            // 关键修复：设置 Content-Length 告知底层 WebServer，避免 _prepareHeader 注入冲突的 Content-Length: 0
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

        // 3. 接收来自网页端上传的音频流并在 StickS3 上播放
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
                        Serial.printf("[WEB-AUDIO] Allocated %u bytes in PSRAM for upload\n",
                                      (unsigned)StickS3Audio::MAX_UPLOAD_BYTES);
                    } else {
                        _upload_audio_buf = (uint8_t*)malloc(StickS3Audio::MAX_UPLOAD_BYTES);
                        Serial.printf("[WEB-AUDIO] Allocated %u bytes in Heap for upload\n",
                                      (unsigned)StickS3Audio::MAX_UPLOAD_BYTES);
                    }
                }
                Serial.printf("[WEB-AUDIO] Upload starting: %s (Type: %s)\n",
                              upload.filename.c_str(), upload.type.c_str());
            } else if (upload.status == UPLOAD_FILE_WRITE) {
                if (_upload_audio_buf && _upload_audio_size + upload.currentSize <= StickS3Audio::MAX_UPLOAD_BYTES) {
                    memcpy(_upload_audio_buf + _upload_audio_size, upload.buf, upload.currentSize);
                    _upload_audio_size += upload.currentSize;
                }
            } else if (upload.status == UPLOAD_FILE_END) {
                Serial.printf("[WEB-AUDIO] Upload complete: %u bytes received.\n", (unsigned)_upload_audio_size);
            }
        });

        // 4. 远程控制设备录音触发 (开始/停止)
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
            if (_web_server.hasArg("msg")) {
                msg = _web_server.arg("msg");
            } else if (_web_server.hasArg("plain")) {
                msg = _web_server.arg("plain");
            }
            msg.trim();
            if (msg.length() > 0) {
                _msg_counter++;
                Serial.printf("[WEB-RX] Received text (#%u): \"%s\"\n", _msg_counter, msg.c_str());
                if (_on_message) {
                    _on_message(msg, "Web/HTTP");
                }
                _web_server.send(200, "application/json; charset=utf-8", "{\"status\":\"ok\",\"ack\":" + String(_msg_counter) + "}");
            } else {
                _web_server.send(400, "application/json", "{\"status\":\"empty\"}");
            }
        };
        _web_server.on("/send", HTTP_POST, handleSend);
        _web_server.on("/send", HTTP_GET, handleSend);

        // 播放提示音
        _web_server.on("/beep", HTTP_GET, [this]() {
            if (_on_message) {
                _on_message("beep", "Web/Beep");
            }
            _web_server.send(200, "application/json", "{\"status\":\"beep_triggered\"}");
        });

        // 实时遥测状态接口
        _web_server.on("/status", HTTP_GET, [this]() {
            char json[128];
            snprintf(json, sizeof(json), "{\"roll\":%.1f,\"pitch\":%.1f,\"aps\":%d,\"clients\":%d}",
                     _last_roll, _last_pitch, _networks_found, WiFi.softAPgetStationNum());
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
                Serial.printf("[TCP-RX] From %s (#%u): \"%s\"\n",
                              client.remoteIP().toString().c_str(), _msg_counter, rx.c_str());
                
                // 立即回传 ACK 报文，小程序对话框可即时查回收据
                client.printf("[StickS3 TCP ACK #%u]: %s\n", _msg_counter, rx.c_str());
                client.flush();

                if (_on_message) {
                    _on_message(rx, "TCP-8080");
                }
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
                    Serial.printf("[UDP-RX] From %s:%d (#%u): \"%s\"\n",
                                  _udp_server.remoteIP().toString().c_str(),
                                  _udp_server.remotePort(), _msg_counter, msg.c_str());

                    // 回送即时 ACK
                    _udp_server.beginPacket(_udp_server.remoteIP(), _udp_server.remotePort());
                    _udp_server.printf("[StickS3 UDP ACK #%u]: %s\n", _msg_counter, msg.c_str());
                    _udp_server.endPacket();

                    if (_on_message) {
                        _on_message(msg, "UDP-8080");
                    }
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
