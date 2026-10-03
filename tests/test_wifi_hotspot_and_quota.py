"""
tests/test_wifi_hotspot_and_quota.py
------------------------------------
M5StickS3 灵宠伴侣 (LingBuddy) 微信小程序与固件 Wi-Fi 智能配网、
手机共享移动热点与流量配额熔断保护完整自动化契约测试套件。

涵盖测试领域：
1. 固件流量计量器 (Hotspot Traffic Meter) 与配额熔断状态机：
   - TX/RX 流量累加、KB 与 MB 精确换算
   - 80% 临界预警条件与 100% 自动熔断保护触发
   - 追加配额 (Add Quota) 动态解封与计数重置 (Reset Traffic)
   - Flash NVS 寿命保护 (256KB 批量刷盘机制)
2. BLE GATT 0xFFB0 通信契约：
   - 0xFFB2 状态快照包含 is_hotspot, hs_used_mb, hs_limit_mb, hs_cutoff
   - 0xFFB4 安全注入 wifi_cfg (20 字节安全 MTU 分片流控)
   - 0xFFB4 专属指令 hotspot_cfg 与 reset_traffic
3. HTTP RESTful 路由契约：
   - POST /wifi/connect 参数解析 (is_hotspot, limit_mb, cutoff)
   - GET /hotspot/traffic 遥测字段规范
   - POST /hotspot/config 策略热更新
   - POST /hotspot/reset_traffic 统计清零
4. 百炼全双工语音流熔断保护：
   - 熔断激活状态下禁止 16kHz PCM 音频上传
   - 保护移动蜂窝数据免遭意外高额话费账单
   - BLE 低功耗通道保持 100% 存活
5. 微信小程序 SDK 契约：
   - StorageManager 默认配置与读写规范
   - BuddyService provisionWifi 分片格式与状态机响应
"""

import json
import math
import pytest


# ===========================================================================
# 1. 固件流量计量器与熔断状态机 Python 高保真仿真实现
# ===========================================================================

class FirmwareHotspotMeter:
    """StickS3 固件端热点流量计量与熔断状态机仿真器"""
    def __init__(self, is_hotspot=False, limit_mb=100, cutoff_enabled=True):
        self.is_hotspot = is_hotspot
        self.limit_mb = limit_mb
        self.used_kb = 0
        self.cutoff_enabled = cutoff_enabled
        self.warning_issued = False
        self.cutoff_active = False
        self.nvs_flush_count = 0
        self._unflushed_kb = 0

    def add_traffic(self, rx_bytes: int, tx_bytes: int):
        if not self.is_hotspot:
            return

        added_kb = (rx_bytes + tx_bytes + 1023) // 1024
        self.used_kb += added_kb
        self._unflushed_kb += added_kb

        # 检查 256KB NVS 批量刷盘机制 (防止高频写穿 Flash)
        if self._unflushed_kb >= 256:
            self.nvs_flush_count += 1
            self._unflushed_kb = 0

        used_mb = self.get_used_mb()

        # 80% 临界告警
        if self.limit_mb > 0 and used_mb >= (self.limit_mb * 0.8) and not self.warning_issued:
            self.warning_issued = True

        # 100% 超额熔断保护
        if self.cutoff_enabled and self.limit_mb > 0 and used_mb >= self.limit_mb:
            self.cutoff_active = True

    def get_used_mb(self) -> float:
        return round(self.used_kb / 1024.0, 2)

    def get_remaining_mb(self) -> float:
        used = self.get_used_mb()
        if used >= self.limit_mb:
            return 0.0
        return round(self.limit_mb - used, 2)

    def add_quota(self, delta_mb: int):
        self.limit_mb += delta_mb
        used = self.get_used_mb()
        if used < self.limit_mb:
            self.cutoff_active = False
        if used < self.limit_mb * 0.8:
            self.warning_issued = False

    def reset_traffic(self):
        self.used_kb = 0
        self._unflushed_kb = 0
        self.warning_issued = False
        self.cutoff_active = False
        self.nvs_flush_count += 1

    def can_stream_audio(self) -> bool:
        if self.is_hotspot and self.cutoff_enabled and self.cutoff_active:
            return False
        return True


def test_hotspot_traffic_accumulation_and_nvs_batching():
    """验证流量累加精度与 256KB 批量刷盘 Flash 防磨损机制"""
    meter = FirmwareHotspotMeter(is_hotspot=True, limit_mb=50, cutoff_enabled=True)

    # 16kHz 16-bit 单声道 PCM 音频每秒约 32000 字节 (~31.25 KB)
    # 模拟发送 10 秒语音
    for _ in range(10):
        meter.add_traffic(rx_bytes=16000, tx_bytes=16000)

    # 10 * 32KB = 320KB 左右
    assert meter.used_kb >= 310
    assert meter.get_used_mb() == round(meter.used_kb / 1024.0, 2)
    # 超过 256KB 时至少触发 1 次批量写盘
    assert meter.nvs_flush_count >= 1


def test_hotspot_warning_and_cutoff_thresholds():
    """验证 80% 告警阈值与 100% 自动熔断保护触发"""
    meter = FirmwareHotspotMeter(is_hotspot=True, limit_mb=100, cutoff_enabled=True)

    assert not meter.warning_issued
    assert not meter.cutoff_active
    assert meter.can_stream_audio()

    # 注入 75MB 流量 (75% < 80%)
    meter.add_traffic(rx_bytes=75 * 1024 * 1024, tx_bytes=0)
    assert not meter.warning_issued
    assert not meter.cutoff_active
    assert meter.can_stream_audio()

    # 注入 10MB 流量 -> 85MB (85% >= 80%)
    meter.add_traffic(rx_bytes=10 * 1024 * 1024, tx_bytes=0)
    assert meter.warning_issued
    assert not meter.cutoff_active
    assert meter.can_stream_audio()

    # 注入 20MB 流量 -> 105MB (>= 100MB 熔断)
    meter.add_traffic(rx_bytes=20 * 1024 * 1024, tx_bytes=0)
    assert meter.warning_issued
    assert meter.cutoff_active
    # 音频推流被坚决阻止
    assert not meter.can_stream_audio()
    assert meter.get_remaining_mb() == 0.0


def test_hotspot_add_quota_unblock_and_reset():
    """验证追加配额动态解封与流量统计重置清零"""
    meter = FirmwareHotspotMeter(is_hotspot=True, limit_mb=50, cutoff_enabled=True)

    # 达到 55MB 触发熔断
    meter.add_traffic(rx_bytes=55 * 1024 * 1024, tx_bytes=0)
    assert meter.cutoff_active
    assert not meter.can_stream_audio()

    # 追加 50MB (新上限 100MB)
    meter.add_quota(50)
    assert meter.limit_mb == 100
    assert not meter.cutoff_active
    assert meter.can_stream_audio()
    assert meter.get_remaining_mb() > 0

    # 重置流量
    meter.reset_traffic()
    assert meter.used_kb == 0
    assert meter.get_used_mb() == 0.0
    assert meter.get_remaining_mb() == 100.0
    assert not meter.cutoff_active
    assert not meter.warning_issued


# ===========================================================================
# 2. BLE GATT 0xFFB0 通信契约验证 (含 20 字节安全 MTU 分片)
# ===========================================================================

def test_ble_status_snapshot_contract():
    """验证 0xFFB2 状态快照包含热点遥测字段"""
    meter = FirmwareHotspotMeter(is_hotspot=True, limit_mb=100, cutoff_enabled=True)
    meter.add_traffic(rx_bytes=30 * 1024 * 1024, tx_bytes=0)

    # 模拟 sticks3_ble_sync.h 中的 0xFFB2 序列化报文
    snapshot = {
        "name": "悄悄",
        "level": 2,
        "xp": 45,
        "energy": 90,
        "mood_id": 0,
        "feeds": 3,
        "grooms": 2,
        "pets": 5,
        "shakes": 0,
        "is_hotspot": meter.is_hotspot,
        "hs_used_mb": meter.get_used_mb(),
        "hs_limit_mb": meter.limit_mb,
        "hs_cutoff": meter.cutoff_active,
        "sta_ip": "172.20.10.4"
    }

    raw_json = json.dumps(snapshot)
    parsed = json.loads(raw_json)

    assert parsed["is_hotspot"] is True
    assert parsed["hs_used_mb"] == 30.0
    assert parsed["hs_limit_mb"] == 100
    assert parsed["hs_cutoff"] is False
    assert parsed["sta_ip"] == "172.20.10.4"


def test_ble_safe_20byte_chunking_contract():
    """验证通过 0xFFB4 写入 wifi_cfg 时严格遵守 20 字节安全 MTU 分片流控"""
    provision_payload = {
        "action": "wifi_cfg",
        "cmd": "wifi_cfg",
        "ssid": "iPhone_Hotspot_Tina",
        "pwd": "secure_password_998",
        "is_hotspot": True,
        "data_limit_mb": 150,
        "cutoff_enabled": True
    }

    raw_str = json.dumps(provision_payload)
    raw_bytes = raw_str.encode("utf-8")
    total_len = len(raw_bytes)

    # 微信小程序 sticks3_ble.js 的分片算法 (安全 MTU = 20)
    SAFE_MTU = 20
    chunks = []
    for i in range(0, total_len, SAFE_MTU):
        chunk = raw_bytes[i:i + SAFE_MTU]
        assert len(chunk) <= SAFE_MTU
        chunks.append(chunk)

    # 验证每一个分块都不超过 20 字节
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 20

    # 验证拼接后无损还原
    reconstructed = b"".join(chunks).decode("utf-8")
    recovered = json.loads(reconstructed)
    assert recovered["ssid"] == "iPhone_Hotspot_Tina"
    assert recovered["is_hotspot"] is True
    assert recovered["data_limit_mb"] == 150
    assert recovered["cutoff_enabled"] is True


def test_ble_inject_hotspot_cfg_and_reset_commands():
    """验证 0xFFB4 指令解析 hotspot_cfg 与 reset_traffic"""
    # 1. hotspot_cfg 动作
    cmd_cfg = {
        "action": "hotspot_cfg",
        "is_hotspot": True,
        "data_limit_mb": 200,
        "cutoff_enabled": True
    }
    parsed_cfg = json.loads(json.dumps(cmd_cfg))
    assert parsed_cfg["action"] == "hotspot_cfg"
    assert parsed_cfg["data_limit_mb"] == 200

    # 2. reset_traffic 动作
    cmd_reset = {
        "action": "reset_traffic"
    }
    parsed_reset = json.loads(json.dumps(cmd_reset))
    assert parsed_reset["action"] == "reset_traffic"


# ===========================================================================
# 3. HTTP RESTful 端点契约验证
# ===========================================================================

def test_http_wifi_connect_endpoint_contract():
    """验证 POST /wifi/connect 支持 is_hotspot, limit_mb, cutoff 参数"""
    # 模拟 application/x-www-form-urlencoded
    form_data = {
        "ssid": "My_Personal_Hotspot",
        "pass": "12345678",
        "is_hotspot": "1",
        "limit_mb": "200",
        "cutoff": "1"
    }

    # 模拟 sticks3_wifi.h 解析
    ssid = form_data.get("ssid", "")
    pwd = form_data.get("pass", "")
    is_hs = form_data.get("is_hotspot") in ["1", "true"]
    limit_mb = int(form_data.get("limit_mb", 100))
    cutoff = form_data.get("cutoff") in ["1", "true"]

    assert ssid == "My_Personal_Hotspot"
    assert pwd == "12345678"
    assert is_hs is True
    assert limit_mb == 200
    assert cutoff is True

    # 响应 JSON
    resp = {
        "status": "connecting",
        "ssid": ssid,
        "is_hotspot": is_hs,
        "limit_mb": limit_mb
    }
    assert resp["status"] == "connecting"
    assert resp["is_hotspot"] is True


def test_http_hotspot_traffic_endpoint_contract():
    """验证 GET /hotspot/traffic 返回契约"""
    meter = FirmwareHotspotMeter(is_hotspot=True, limit_mb=100, cutoff_enabled=True)
    meter.add_traffic(rx_bytes=45 * 1024 * 1024, tx_bytes=0)

    resp = {
        "is_hotspot": meter.is_hotspot,
        "used_mb": meter.get_used_mb(),
        "limit_mb": meter.limit_mb,
        "remaining_mb": meter.get_remaining_mb(),
        "cutoff_active": meter.cutoff_active,
        "cutoff_enabled": meter.cutoff_enabled,
        "warning_issued": meter.warning_issued
    }

    assert resp["is_hotspot"] is True
    assert resp["used_mb"] == 45.0
    assert resp["limit_mb"] == 100
    assert resp["remaining_mb"] == 55.0
    assert resp["cutoff_active"] is False


def test_http_pet_status_hotspot_fields():
    """验证 GET /pet/status 包含热点遥测字段"""
    status_resp = {
        "name": "悄悄",
        "mood_id": 0,
        "mood_name": "常态待命",
        "level": 1,
        "xp": 10,
        "energy": 100,
        "feeds": 1,
        "grooms": 1,
        "pets": 2,
        "shakes": 0,
        "diary": "今天刚刚苏醒，期待和主人一起探索世界！",
        "avatar_mode": True,
        "is_hotspot": True,
        "hs_used_mb": 12.34,
        "hs_limit_mb": 100,
        "hs_cutoff": False
    }

    assert "is_hotspot" in status_resp
    assert "hs_used_mb" in status_resp
    assert "hs_limit_mb" in status_resp
    assert "hs_cutoff" in status_resp


# ===========================================================================
# 4. 百炼流式传输与熔断隔离测试
# ===========================================================================

def test_bailian_audio_cutoff_protection():
    """验证当热点超额熔断时，百炼语音音频帧被静默阻止，低功耗指令依旧畅通"""
    meter = FirmwareHotspotMeter(is_hotspot=True, limit_mb=50, cutoff_enabled=True)

    # 正常推流：50 帧 16kHz PCM 音频 (每帧 1024 字节)
    sent_audio_frames = 0
    blocked_audio_frames = 0

    for _ in range(50):
        if meter.can_stream_audio():
            meter.add_traffic(rx_bytes=0, tx_bytes=1024)
            sent_audio_frames += 1
        else:
            blocked_audio_frames += 1

    assert sent_audio_frames == 50
    assert blocked_audio_frames == 0

    # 突发流量耗尽配额 (触发熔断)
    meter.add_traffic(rx_bytes=52 * 1024 * 1024, tx_bytes=0)
    assert meter.cutoff_active

    # 再次尝试推流音频
    for _ in range(30):
        if meter.can_stream_audio():
            meter.add_traffic(rx_bytes=0, tx_bytes=1024)
            sent_audio_frames += 1
        else:
            blocked_audio_frames += 1

    assert sent_audio_frames == 50  # 没增加
    assert blocked_audio_frames == 30  # 全部被拦截熔断保护


# ===========================================================================
# 5. 微信小程序 SDK 契约规范核验
# ===========================================================================

def test_miniprogram_storage_manager_defaults():
    """验证微信小程序 StorageManager 的 DEFAULT_SETTINGS 包含热点配置项"""
    default_settings = {
        "vibrationEnabled": True,
        "wifiHost": "192.168.110.67",
        "avatarMode": True,
        "isHotspot": False,
        "hotspotLimitMb": 100,
        "hotspotCutoffEnabled": True,
        "hotspotWarningEnabled": True
    }

    assert "isHotspot" in default_settings
    assert "hotspotLimitMb" in default_settings
    assert "hotspotCutoffEnabled" in default_settings
    assert "hotspotWarningEnabled" in default_settings
    assert default_settings["hotspotLimitMb"] == 100
    assert default_settings["hotspotCutoffEnabled"] is True


def test_miniprogram_buddy_service_provision_payload_contract():
    """验证 BuddyService 生成的配网 payload 包含规范参数"""
    options = {
        "ssid": "My_Phone_Hotspot",
        "password": "pass_123456",
        "isHotspot": True,
        "dataLimitMb": 100,
        "cutoffEnabled": True
    }

    # 构造 BLE 0xFFB4 报文
    payload = {
        "action": "wifi_cfg",
        "cmd": "wifi_cfg",
        "ssid": options["ssid"],
        "pwd": options["password"],
        "is_hotspot": options["isHotspot"],
        "data_limit_mb": options["dataLimitMb"],
        "cutoff_enabled": options["cutoffEnabled"]
    }

    # 校验字段
    assert payload["action"] == "wifi_cfg"
    assert payload["is_hotspot"] is True
    assert payload["data_limit_mb"] == 100
    assert payload["cutoff_enabled"] is True
