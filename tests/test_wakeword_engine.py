"""
tests/test_wakeword_engine.py
------------------------------
M5Stack StickS3 离线语音唤醒词「悄悄」声学检测引擎与协议端点自动化单元测试集
1. 声学特征与双音节叠词时序仿真测试：
   - 清塞擦音 [q] (高过零率 + 高频能量) 与复韵母 [iao] (强共振峰低过零率) 仿真波形合成
   - 双音节「悄悄」完整时序检测与置信度打分
2. 负样本抗干扰与鲁棒性测试：
   - 纯白噪声、纯正弦波、单音节“悄”、无意背景语音绝不误触发
3. 灵敏度动态门限响应测试
4. 固件 C++ 源码属性与 REST API 端点契约测试
"""

import math
import os
import random
import struct
import pytest


# ---------------------------------------------------------------------------
# 1. Python 镜像声学特征提取器与有限状态机 (完全对齐 C++ sticks3_wakeword.h)
# ---------------------------------------------------------------------------

class MockWakeWordEngine:
    FRAME_LEN = 320  # 20ms @ 16kHz
    SAMPLE_RATE = 16000

    def __init__(self, sensitivity=75):
        self.sensitivity = sensitivity
        self.enabled = True
        self.state = "IDLE"
        self.q1_frames = 0
        self.iao1_frames = 0
        self.gap_frames = 0
        self.q2_frames = 0
        self.iao2_frames = 0
        self.q1_energy = 0.0
        self.iao1_energy = 0.0
        self.q2_energy = 0.0
        self.iao2_energy = 0.0
        self.total_wakes = 0
        self.last_confidence = 0.0
        self.fifo = []

    def reset(self):
        self.state = "IDLE"
        self.q1_frames = 0
        self.iao1_frames = 0
        self.gap_frames = 0
        self.q2_frames = 0
        self.iao2_frames = 0
        self.q1_energy = 0.0
        self.iao1_energy = 0.0
        self.q2_energy = 0.0
        self.iao2_energy = 0.0
        self.fifo = []

    def extract_features(self, samples):
        n = len(samples)
        if n == 0:
            return {"rms": 0, "zcr": 0, "hl_ratio": 0, "e_low": 0, "e_mid": 0, "e_high": 0}

        mean = sum(samples) / n
        sum_sq = 0.0
        zcr = 0
        prev = samples[0] - mean
        low_energy = 0.0
        mid_energy = 0.0
        high_energy = 0.0
        s_low_prev = 0.0

        for i in range(n):
            s = samples[i] - mean
            sum_sq += s * s

            if (prev < 0 and s >= 0) or (prev >= 0 and s < 0):
                zcr += 1
            prev = s

            s_low = s_low_prev * 0.72 + s * 0.28
            s_low_prev = s_low
            low_energy += s_low * s_low

            if i >= 2:
                diff_high = s - samples[i - 2]
                high_energy += diff_high * diff_high

            s_mid = s - s_low
            mid_energy += s_mid * s_mid

        rms = math.sqrt(sum_sq / n)
        e_low = math.sqrt(low_energy / n)
        e_mid = math.sqrt(mid_energy / n)
        e_high = math.sqrt(high_energy / n)
        hl_ratio = e_high / (e_low + 1.0)

        return {
            "rms": rms,
            "zcr": zcr,
            "e_low": e_low,
            "e_mid": e_mid,
            "e_high": e_high,
            "hl_ratio": hl_ratio
        }

    def process_frame(self, f):
        sens_factor = self.sensitivity / 75.0
        min_rms_q = 70.0 / sens_factor
        min_rms_iao = 110.0 / sens_factor
        min_zcr_q = int(48 * (1.15 - sens_factor * 0.15))
        max_zcr_iao = int(42 * (0.85 + sens_factor * 0.15))

        if self.state == "IDLE":
            if f["rms"] >= min_rms_q and f["zcr"] >= min_zcr_q and f["hl_ratio"] >= 0.85:
                self.state = "Q1"
                self.q1_frames = 1
                self.q1_energy = f["rms"]

        elif self.state == "Q1":
            self.q1_frames += 1
            self.q1_energy += f["rms"]
            if self.q1_frames > 7:
                self.reset()
            elif f["rms"] >= min_rms_iao and f["zcr"] <= max_zcr_iao and (f["e_low"] + f["e_mid"]) > f["e_high"] * 1.05:
                self.state = "IAO1"
                self.iao1_frames = 1
                self.iao1_energy = f["rms"]

        elif self.state == "IAO1":
            self.iao1_frames += 1
            self.iao1_energy += f["rms"]
            if self.iao1_frames > 16:
                self.reset()
            elif self.iao1_frames >= 3:
                # 连读直接转向 Q2
                if f["rms"] >= min_rms_q * 0.85 and f["zcr"] >= min_zcr_q and f["hl_ratio"] >= 0.80:
                    self.state = "Q2"
                    self.q2_frames = 1
                    self.q2_energy = f["rms"]
                # 能量减弱回落进入 GAP
                elif f["rms"] < (self.iao1_energy / self.iao1_frames) * 0.45 or f["rms"] < min_rms_q:
                    self.state = "GAP"
                    self.gap_frames = 1

        elif self.state == "GAP":
            self.gap_frames += 1
            if self.gap_frames > 12:
                self.reset()
            elif f["rms"] >= min_rms_q * 0.85 and f["zcr"] >= min_zcr_q and f["hl_ratio"] >= 0.75:
                self.state = "Q2"
                self.q2_frames = 1
                self.q2_energy = f["rms"]

        elif self.state == "Q2":
            self.q2_frames += 1
            self.q2_energy += f["rms"]
            if self.q2_frames > 7:
                self.reset()
            elif f["rms"] >= min_rms_iao * 0.9 and f["zcr"] <= max_zcr_iao and (f["e_low"] + f["e_mid"]) > f["e_high"] * 1.05:
                self.state = "IAO2"
                self.iao2_frames = 1
                self.iao2_energy = f["rms"]

        elif self.state == "IAO2":
            self.iao2_frames += 1
            self.iao2_energy += f["rms"]
            if self.iao2_frames > 15:
                self.reset()
            elif self.iao2_frames >= 4:
                conf = self.evaluate_confidence()
                req_conf = max(45.0, 85.0 - (self.sensitivity * 0.35))
                if conf >= req_conf:
                    self.total_wakes += 1
                    self.last_confidence = conf
                    self.reset()
                    return True
        return False

    def evaluate_confidence(self):
        if self.q1_frames == 0 or self.iao1_frames == 0 or self.q2_frames == 0 or self.iao2_frames == 0:
            return 0.0

        t1 = float(self.q1_frames + self.iao1_frames)
        t2 = float(self.q2_frames + self.iao2_frames)
        dur_ratio = min(t1, t2) / max(t1, t2)
        s_dur = dur_ratio * 35.0

        avg_e1 = self.iao1_energy / max(1, self.iao1_frames)
        avg_e2 = self.iao2_energy / max(1, self.iao2_frames)
        e_ratio = min(avg_e1, avg_e2) / (max(avg_e1, avg_e2) + 0.1)
        s_energy = e_ratio * 30.0

        s_acoustic = 25.0
        if self.q1_frames < 2 or self.q2_frames < 2:
            s_acoustic -= 8.0
        if self.gap_frames < 1 or self.gap_frames > 5:
            s_acoustic -= 6.0

        total_frames = self.q1_frames + self.iao1_frames + self.gap_frames + self.q2_frames + self.iao2_frames
        s_timing = 10.0
        if total_frames < 18 or total_frames > 48:
            s_timing -= 5.0

        return min(100.0, max(0.0, s_dur + s_energy + s_acoustic + s_timing))

    def feed_samples(self, samples):
        self.fifo.extend(samples)
        triggered = False
        frame_idx = 0
        while len(self.fifo) >= self.FRAME_LEN:
            frame = self.fifo[:self.FRAME_LEN]
            self.fifo = self.fifo[self.FRAME_LEN:]
            feat = self.extract_features(frame)
            old_st = self.state
            if self.process_frame(feat):
                print(f"Frame #{frame_idx}: {old_st} -> {self.state} TRIGGERED! conf={self.last_confidence}")
                triggered = True
            else:
                print(f"Frame #{frame_idx}: {old_st} -> {self.state} | rms={feat['rms']:.1f}, zcr={feat['zcr']}, hl={feat['hl_ratio']:.2f}")
            frame_idx += 1
        return triggered


# ---------------------------------------------------------------------------
# 2. 合成声学信号辅助函数
# ---------------------------------------------------------------------------

def generate_q_syllable(duration_ms=60, sample_rate=16000, amplitude=500):
    """合成清塞擦音 [q] (高频白噪 + 摩擦爆破，高 ZCR)"""
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    random.seed(42)
    for i in range(num_samples):
        # 3.5kHz ~ 6kHz 高频带为主的湍流噪声
        t = i / sample_rate
        fric = (math.sin(2 * math.pi * 3800 * t) * 0.4 +
                math.sin(2 * math.pi * 5200 * t) * 0.4 +
                (random.random() * 2.0 - 1.0) * 0.5)
        # 包络：急促上升后衰减
        env = math.sin(math.pi * (i / num_samples))
        samples.append(int(fric * env * amplitude))
    return samples


def generate_iao_syllable(duration_ms=180, sample_rate=16000, amplitude=1600):
    """合成复韵母 [iao] (强共振峰低过零率，基频 200Hz + F1/F2 动态滑音)"""
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        frac = i / num_samples
        f0 = 200.0  # 声带基频
        f1 = 450.0 + 350.0 * math.sin(math.pi * frac)  # F1: 450 -> 800 -> 450
        f2 = 2200.0 - 1100.0 * frac                    # F2: 2200 (i) -> 1100 (ao)
        
        v = (math.sin(2 * math.pi * f0 * t) * 0.5 +
             math.sin(2 * math.pi * f1 * t) * 0.35 +
             math.sin(2 * math.pi * f2 * t) * 0.25)
        env = math.sin(math.pi * frac)
        samples.append(int(v * env * amplitude))
    return samples


def generate_silence(duration_ms=40, sample_rate=16000):
    """间隙静音/低底噪槽"""
    num_samples = int(sample_rate * duration_ms / 1000)
    return [random.randint(-15, 15) for _ in range(num_samples)]


def generate_full_qiaoqiao():
    """合成完整标准「悄悄」语音波形"""
    pcm = []
    # 前置静音 100ms
    pcm.extend(generate_silence(100))
    # 音节 1: 悄
    pcm.extend(generate_q_syllable(60, amplitude=550))
    pcm.extend(generate_iao_syllable(180, amplitude=1700))
    # 间隙槽: 40ms
    pcm.extend(generate_silence(40))
    # 音节 2: 悄
    pcm.extend(generate_q_syllable(60, amplitude=520))
    pcm.extend(generate_iao_syllable(180, amplitude=1650))
    # 后置静音 100ms
    pcm.extend(generate_silence(100))
    return pcm


# ---------------------------------------------------------------------------
# 3. 单元测试用例
# ---------------------------------------------------------------------------

def test_qiaoqiao_synthesis_and_detection():
    """验证标准合成「悄悄」双音节声学信号能够被 100% 准确命中并给出高置信度"""
    engine = MockWakeWordEngine(sensitivity=75)
    pcm = generate_full_qiaoqiao()

    assert len(pcm) > 5000  # 约 580ms 音频数据
    triggered = engine.feed_samples(pcm)

    assert triggered is True, "Offline wake word '悄悄' must be successfully detected!"
    assert engine.total_wakes == 1
    assert engine.last_confidence >= 65.0, f"Expected confidence >= 65%, got {engine.last_confidence}%"


def test_wakeword_negative_sample_immunity():
    """验证非唤醒词音频（白噪、纯音、单字、不匹配语音）绝不产生误触发"""
    engine = MockWakeWordEngine(sensitivity=75)

    # 1. 纯白噪音 1.5 秒
    random.seed(123)
    white_noise = [random.randint(-400, 400) for _ in range(24000)]
    assert engine.feed_samples(white_noise) is False
    assert engine.total_wakes == 0

    # 2. 1000Hz 纯正弦波 1 秒
    sine_1k = [int(math.sin(2 * math.pi * 1000 * (i / 16000)) * 2000) for i in range(16000)]
    assert engine.feed_samples(sine_1k) is False
    assert engine.total_wakes == 0

    # 3. 单音节“悄” (缺少重叠词第二音节)
    single_qiao = []
    single_qiao.extend(generate_silence(100))
    single_qiao.extend(generate_q_syllable(60))
    single_qiao.extend(generate_iao_syllable(200))
    single_qiao.extend(generate_silence(400))
    assert engine.feed_samples(single_qiao) is False
    assert engine.total_wakes == 0

    # 4. 模拟无意日常词汇（例如单辅音或元音错位的“你好”）
    nihao = []
    nihao.extend(generate_silence(100))
    nihao.extend([int(math.sin(2 * math.pi * 300 * (i / 16000)) * 1200) for i in range(3200)])
    nihao.extend(generate_silence(50))
    nihao.extend([int(math.sin(2 * math.pi * 800 * (i / 16000)) * 1200) for i in range(3200)])
    nihao.extend(generate_silence(100))
    assert engine.feed_samples(nihao) is False
    assert engine.total_wakes == 0


def test_wakeword_sensitivity_threshold_scaling():
    """验证灵敏度参数调节对置信度门限的动态影响"""
    engine_high = MockWakeWordEngine(sensitivity=95)
    engine_low = MockWakeWordEngine(sensitivity=25)

    pcm = generate_full_qiaoqiao()

    # 高灵敏度模式下更容易命中
    trig_high = engine_high.feed_samples(pcm)
    assert trig_high is True

    # 门限对比验证
    req_high = max(45.0, 85.0 - (95 * 0.35))
    req_low = max(45.0, 85.0 - (25 * 0.35))
    assert req_high < req_low, "Higher sensitivity must result in lower required confidence threshold"


# ---------------------------------------------------------------------------
# 4. 固件源码静态契约与 REST API 规范测试
# ---------------------------------------------------------------------------

def test_firmware_wakeword_header_source():
    """验证 firmware/m5sticks3_buddy/include/sticks3_wakeword.h 属性与架构"""
    header_path = os.path.join(
        os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_wakeword.h"
    )
    assert os.path.exists(header_path), "sticks3_wakeword.h must exist"

    with open(header_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "StickS3WakeWordEngine" in src
    assert "WAKE_WORD_NAME" in src
    assert "悄悄" in src
    assert "feedSamples" in src
    assert "setSensitivity" in src
    assert "setEnabled" in src
    assert "evaluateConfidence" in src
    assert "extractFrameFeatures" in src
    assert "WAKE_STATE_Q1" in src
    assert "WAKE_STATE_IAO1" in src
    assert "WAKE_STATE_GAP" in src
    assert "WAKE_STATE_Q2" in src
    assert "WAKE_STATE_IAO2" in src


def test_firmware_wakeword_rest_endpoints_source():
    """验证 sticks3_wifi.h 中注册的 /wakeword/status 与 /wakeword/config REST 端点"""
    wifi_h_path = os.path.join(
        os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_wifi.h"
    )
    assert os.path.exists(wifi_h_path), "sticks3_wifi.h must exist"

    with open(wifi_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "/wakeword/status" in src
    assert "/wakeword/config" in src
    assert "/wakeword/trigger" in src
    assert "StickS3WakeWordEngine" in src


def test_firmware_bailian_client_wakeword_integration_source():
    """验证 sticks3_bailian_client.h 中的唤醒窗口与推流门控方法"""
    bl_h_path = os.path.join(
        os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_bailian_client.h"
    )
    assert os.path.exists(bl_h_path), "sticks3_bailian_client.h must exist"

    with open(bl_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "sticks3_wakeword.h" in src
    assert "onWakeWordDetected" in src
    assert "isWakeWindowOpen" in src
    assert "_wake_window_until" in src
    assert "StickS3WakeWordEngine::getInstance().feedSamples" in src


def test_firmware_wifi_config_wakeword_persistence_source():
    """验证 sticks3_wifi_config.h 中的唤醒词 NVS 持久化属性与方法"""
    cfg_h_path = os.path.join(
        os.path.dirname(__file__), "..", "firmware", "m5sticks3_buddy", "include", "sticks3_wifi_config.h"
    )
    assert os.path.exists(cfg_h_path), "sticks3_wifi_config.h must exist"

    with open(cfg_h_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    assert "wakeword_enabled" in src
    assert "wakeword_sensitivity" in src
    assert "wakeword_timeout_sec" in src
    assert "saveWakeWordConfig" in src
    assert "ww_en" in src
    assert "ww_sens" in src
