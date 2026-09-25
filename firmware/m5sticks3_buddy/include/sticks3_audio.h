/**
 * firmware/m5sticks3_buddy/include/sticks3_audio.h
 * ------------------------------------------------
 * M5Stack StickS3 高保真音频子系统驱动 (ES8311 Mono Codec + AW8737 PA + MEMS 硅麦)
 * 1. 硬件引脚分配：
 *    - I2C 控制总线: Wire1 (SDA=G47, SCL=G48), ES8311 地址 0x18, PM1 地址 0x6E
 *    - PM1 GPIO3: AW8737 音频功放使能与供电门控 (推挽输出 HIGH)
 *    - I2S0 时钟与数据: MCLK=G18, BCLK=G17, LRCK=G15, DOUT=G14 (放音), DIN=G16 (录音)
 * 2. 软件特性：
 *    - 多通道 I2S 驱动：16kHz 16-bit Mono 全双工/互斥驱动
 *    - 软音源正弦波与旋律合成器 (开机和弦、按键嘀声、消息 Ding-Dong、高危报警)
 *    - 实时数字 MEMS 麦克风 PCM 采样与 RMS 能量解算 (0~100% VU Meter)
 *    - 电池过流保护安全上限 (默认限幅 <= 70%)
 */

#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <driver/i2s.h>
#include <cmath>

namespace sticks3 {

enum ChimeType {
    CHIME_STARTUP = 0, // 开机上扬和弦
    CHIME_CLICK,       // 按键清脆确认短音
    CHIME_NOTIFY,      // 微信/蓝牙消息 Ding-Dong
    CHIME_ALERT,       // 权限审批急促警报
    CHIME_SUCCESS      // 成功提示音
};

class StickS3Audio {
public:
    static constexpr uint8_t ES8311_ADDR = 0x18;
    static constexpr uint8_t PM1_ADDR = 0x6E;
    static constexpr int PIN_I2S_MCLK = 18;
    static constexpr int PIN_I2S_BCLK = 17;
    static constexpr int PIN_I2S_LRCK = 15;
    static constexpr int PIN_I2S_DOUT = 14;
    static constexpr int PIN_I2S_DIN  = 16;
    static constexpr int SAMPLE_RATE  = 16000;

    static constexpr size_t MAX_RECORD_SECONDS = 10;
    static constexpr size_t MAX_RECORD_PCM_BYTES = SAMPLE_RATE * 2 * MAX_RECORD_SECONDS; // 320,000 Bytes
    static constexpr size_t WAV_HEADER_SIZE = 44;
    static constexpr size_t MAX_RECORD_TOTAL_BYTES = WAV_HEADER_SIZE + MAX_RECORD_PCM_BYTES; // 320,044 Bytes
    static constexpr size_t MAX_UPLOAD_BYTES = 400000;

    StickS3Audio() 
        : _wire(&Wire1), _initialized(false), _speaker_powered(false),
          _last_mic_rms(0), _raw_rms(0.0f), _playing_sound(false),
          _record_buf(nullptr), _recorded_pcm_bytes(0), _is_recording(false),
          _record_start_ms(0), _record_max_ms(10000), _device_audio_id(0),
          _has_device_audio(false), _playback_ptr(nullptr),
          _playback_total_bytes(0), _playback_offset(0),
          _is_playing_stream(false), _playback_progress(0.0f) {}

    static StickS3Audio& getInstance() {
        static StickS3Audio instance;
        return instance;
    }

    static void generateWavHeader(uint8_t* header, uint32_t pcm_len, uint32_t sample_rate = SAMPLE_RATE) {
        uint32_t total_size = pcm_len + 36;
        uint32_t byte_rate = sample_rate * 2; // 16-bit Mono = 2 bytes/sample
        uint16_t block_align = 2;

        // "RIFF"
        header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
        header[4] = (uint8_t)(total_size & 0xFF);
        header[5] = (uint8_t)((total_size >> 8) & 0xFF);
        header[6] = (uint8_t)((total_size >> 16) & 0xFF);
        header[7] = (uint8_t)((total_size >> 24) & 0xFF);

        // "WAVE"
        header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';

        // "fmt "
        header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
        header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0; // Subchunk1Size
        header[20] = 1; header[21] = 0; // AudioFormat = 1 (PCM)
        header[22] = 1; header[23] = 0; // NumChannels = 1 (Mono)

        // SampleRate
        header[24] = (uint8_t)(sample_rate & 0xFF);
        header[25] = (uint8_t)((sample_rate >> 8) & 0xFF);
        header[26] = (uint8_t)((sample_rate >> 16) & 0xFF);
        header[27] = (uint8_t)((sample_rate >> 24) & 0xFF);

        // ByteRate
        header[28] = (uint8_t)(byte_rate & 0xFF);
        header[29] = (uint8_t)((byte_rate >> 8) & 0xFF);
        header[30] = (uint8_t)((byte_rate >> 16) & 0xFF);
        header[31] = (uint8_t)((byte_rate >> 24) & 0xFF);

        // BlockAlign
        header[32] = (uint8_t)(block_align & 0xFF);
        header[33] = (uint8_t)((block_align >> 8) & 0xFF);

        // BitsPerSample
        header[34] = 16; header[35] = 0;

        // "data"
        header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
        header[40] = (uint8_t)(pcm_len & 0xFF);
        header[41] = (uint8_t)((pcm_len >> 8) & 0xFF);
        header[42] = (uint8_t)((pcm_len >> 16) & 0xFF);
        header[43] = (uint8_t)((pcm_len >> 24) & 0xFF);
    }

    bool begin(TwoWire* wire = &Wire1) {
        if (_initialized) return true;
        _wire = wire;

        Serial.println("[AUDIO] Initializing StickS3 Audio Subsystem...");

        // 1. 使能 M5PM1 GPIO3 功放供电轨 (AW8737 Power Gate)
        enablePA(true);

        // 2. 初始化 I2S0 外设驱动 (全双工 TX+RX，增大 DMA 缓冲至 128ms 防掉帧)
        i2s_config_t i2s_config = {
            .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_RX),
            .sample_rate = SAMPLE_RATE,
            .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
            .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT, // ES8311 Mono
            .communication_format = I2S_COMM_FORMAT_STAND_I2S,
            .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
            .dma_buf_count = 8,
            .dma_buf_len = 256,
            .use_apll = false,
            .tx_desc_auto_clear = true,
            .fixed_mclk = 0
        };

        i2s_pin_config_t pin_config = {
            .mck_io_num = PIN_I2S_MCLK,
            .bck_io_num = PIN_I2S_BCLK,
            .ws_io_num = PIN_I2S_LRCK,
            .data_out_num = PIN_I2S_DOUT,
            .data_in_num = PIN_I2S_DIN
        };

        esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
        if (err != ESP_OK) {
            Serial.printf("[AUDIO] I2S driver install failed: 0x%X\n", err);
            return false;
        }

        err = i2s_set_pin(I2S_NUM_0, &pin_config);
        if (err != ESP_OK) {
            Serial.printf("[AUDIO] I2S pin configure failed: 0x%X\n", err);
            return false;
        }

        // 3. 配置 ES8311 Codec 寄存器 (双通使能)
        initES8311();

        // 4. 预先在 PSRAM 中初始化录音缓冲区
        ensureRecordBuffer();

        _initialized = true;
        Serial.println("[AUDIO] ES8311 Codec & AW8737 PA & MEMS Mic ONLINE!");
        return true;
    }

    void enablePA(bool enable) {
        if (!_wire) return;
        // PM1 寄存器控制 GPIO3 (AW8737 供电门控)
        auto readPM1 = [this](uint8_t reg) -> uint8_t {
            _wire->beginTransmission(PM1_ADDR);
            _wire->write(reg);
            _wire->endTransmission(false);
            _wire->requestFrom(PM1_ADDR, (uint8_t)1);
            return _wire->available() ? _wire->read() : 0;
        };

        auto writePM1 = [this](uint8_t reg, uint8_t val) {
            _wire->beginTransmission(PM1_ADDR);
            _wire->write(reg);
            _wire->write(val);
            _wire->endTransmission();
        };

        uint8_t r16 = readPM1(0x16);
        writePM1(0x16, r16 & ~(1 << 3)); // GPIO3 普通功能

        uint8_t r10 = readPM1(0x10);
        writePM1(0x10, r10 | (1 << 3));  // GPIO3 输出方向

        uint8_t r13 = readPM1(0x13);
        writePM1(0x13, r13 & ~(1 << 3)); // GPIO3 推挽输出

        uint8_t r11 = readPM1(0x11);
        if (enable) {
            writePM1(0x11, r11 | (1 << 3)); // GPIO3 高电平 (PA ON)
            _speaker_powered = true;
        } else {
            writePM1(0x11, r11 & ~(1 << 3)); // GPIO3 低电平 (PA OFF)
            _speaker_powered = false;
        }
    }

    // 播放指定频率正弦波
    void playTone(uint16_t freq_hz, uint16_t duration_ms, float volume = 0.55f) {
        if (!_initialized) return;
        if (volume > 0.75f) volume = 0.75f; // 电池放电保护限幅

        _playing_sound = true;
        setCodecSpeakerMode();

        const size_t buf_samples = 128;
        int16_t buf[buf_samples];
        float phase = 0.0f;
        float phase_inc = 2.0f * 3.14159265f * freq_hz / SAMPLE_RATE;
        float amp = volume * 32767.0f;

        uint32_t total_samples = (uint32_t)SAMPLE_RATE * duration_ms / 1000;
        uint32_t samples_generated = 0;

        while (samples_generated < total_samples) {
            size_t to_write = (total_samples - samples_generated < buf_samples)
                              ? (total_samples - samples_generated) : buf_samples;
            for (size_t i = 0; i < to_write; ++i) {
                // 平滑起振与释音 (消除突变爆音)
                float env = 1.0f;
                uint32_t cur = samples_generated + i;
                if (cur < 200) env = (float)cur / 200.0f;
                if (total_samples - cur < 200) env = (float)(total_samples - cur) / 200.0f;

                buf[i] = (int16_t)(std::sin(phase) * amp * env);
                phase += phase_inc;
                if (phase >= 2.0f * 3.14159265f) phase -= 2.0f * 3.14159265f;
            }

            size_t bytes_written = 0;
            i2s_write(I2S_NUM_0, buf, to_write * sizeof(int16_t), &bytes_written, portMAX_DELAY);
            samples_generated += to_write;
        }

        // 静音缓冲消除尾部直流偏置
        memset(buf, 0, sizeof(buf));
        size_t dummy = 0;
        i2s_write(I2S_NUM_0, buf, sizeof(buf), &dummy, portMAX_DELAY);

        setCodecMicMode();
        _playing_sound = false;
    }

    // 播放内置旋律预设
    void playChime(ChimeType type) {
        switch (type) {
            case CHIME_STARTUP:
                // 上扬 3 连和弦 (C5 -> E5 -> G5)
                playTone(523, 70, 0.45f);
                delay(20);
                playTone(659, 70, 0.50f);
                delay(20);
                playTone(784, 150, 0.55f);
                break;
            case CHIME_CLICK:
                // 清脆按键提示 (2200Hz 25ms)
                playTone(2200, 25, 0.40f);
                break;
            case CHIME_NOTIFY:
                // 微信/蓝牙消息到达 (Ding-Dong: 1046Hz -> 784Hz)
                playTone(1046, 100, 0.60f);
                delay(30);
                playTone(784, 220, 0.60f);
                break;
            case CHIME_ALERT:
                // 权限审批/异常双音急促警报
                for (int i = 0; i < 2; ++i) {
                    playTone(1300, 80, 0.65f);
                    delay(30);
                    playTone(850, 80, 0.65f);
                    delay(30);
                }
                break;
            case CHIME_SUCCESS:
                playTone(880, 80, 0.50f);
                delay(30);
                playTone(1760, 140, 0.55f);
                break;
        }
    }

    // 读取当前环境音频能量 RMS (0 ~ 100%)
    uint8_t readMicRMS() {
        if (!_initialized || _playing_sound) return _last_mic_rms;
        if (_is_recording) return _last_mic_rms; // 录音中直接由 processRecording 实时解算能量

        const size_t SAMPLES_COUNT = 64;
        int16_t sample_buf[SAMPLES_COUNT];
        size_t bytes_read = 0;

        esp_err_t res = i2s_read(I2S_NUM_0, sample_buf, sizeof(sample_buf), &bytes_read, 10 / portTICK_PERIOD_MS);
        if (res != ESP_OK || bytes_read == 0) return _last_mic_rms;

        size_t samples = bytes_read / sizeof(int16_t);
        if (samples == 0) return _last_mic_rms;

        // 消除 DC 偏置并解算交流信号能量
        int32_t mean = 0;
        for (size_t i = 0; i < samples; ++i) mean += sample_buf[i];
        mean /= (int32_t)samples;

        int64_t sum_sq = 0;
        for (size_t i = 0; i < samples; ++i) {
            int32_t diff = sample_buf[i] - mean;
            sum_sq += (diff * diff);
        }

        _raw_rms = std::sqrt((float)(sum_sq / samples));

        // 动态灵敏度映射 (环境安静约 50~100, 说话声 300~1500)
        int pct = 0;
        if (_raw_rms > 60.0f) {
            pct = static_cast<int>(((_raw_rms - 60.0f) / 1000.0f) * 100.0f);
        }
        if (pct < 0) pct = 0;
        if (pct > 100) pct = 100;

        // 专业 VU 表弹跳质感 (快冲慢放)
        if (pct > _last_mic_rms) {
            _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 2 + pct * 8) / 10);
        } else {
            _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 8 + pct * 2) / 10);
        }
        return _last_mic_rms;
    }

    // ==========================================
    // 设备端按键录音管理 (PSRAM + 16kHz WAV 封包)
    // ==========================================

    bool startRecording(uint32_t max_ms = 10000) {
        if (!_initialized) return false;
        ensureRecordBuffer();
        if (!_record_buf) {
            Serial.println("[AUDIO] Error: Failed to allocate record buffer!");
            return false;
        }

        if (_is_playing_stream || _playing_sound) {
            stopPlayback();
        }

        setCodecMicMode();
        _recorded_pcm_bytes = 0;
        _record_start_ms = millis();
        _record_max_ms = (max_ms > 10000) ? 10000 : max_ms;
        _is_recording = true;
        Serial.printf("[AUDIO] >>> Recording STARTED (max %u ms) <<<\n", (unsigned)_record_max_ms);
        return true;
    }

    void stopRecording() {
        if (!_is_recording) return;
        _is_recording = false;
        // 在缓冲区头部构建 44 字节标准 RIFF WAV 头
        generateWavHeader(_record_buf, _recorded_pcm_bytes, SAMPLE_RATE);
        _has_device_audio = true;
        _device_audio_id++;
        uint32_t duration_ms = (_recorded_pcm_bytes * 1000) / (SAMPLE_RATE * 2);
        Serial.printf("[AUDIO] >>> Recording STOPPED. ID #%u, PCM %u bytes (~%u ms), WAV total %u bytes <<<\n",
                      (unsigned)_device_audio_id, (unsigned)_recorded_pcm_bytes,
                      (unsigned)duration_ms, (unsigned)(WAV_HEADER_SIZE + _recorded_pcm_bytes));
    }

    void processRecording() {
        if (!_is_recording || !_record_buf) return;

        // 达到最大录音时长自动截止
        if (millis() - _record_start_ms >= _record_max_ms) {
            stopRecording();
            return;
        }

        // 批量清空 DMA 缓冲以实现真实 1:1 速率采集
        const size_t READ_CHUNK = 512;
        uint8_t temp_buf[READ_CHUNK];
        size_t bytes_read = 0;
        
        while (_is_recording && _recorded_pcm_bytes < MAX_RECORD_PCM_BYTES) {
            esp_err_t res = i2s_read(I2S_NUM_0, temp_buf, READ_CHUNK, &bytes_read, 0);
            if (res != ESP_OK || bytes_read == 0) break;

            size_t space_left = MAX_RECORD_PCM_BYTES - _recorded_pcm_bytes;
            size_t to_copy = (bytes_read < space_left) ? bytes_read : space_left;
            if (to_copy > 0) {
                memcpy(_record_buf + WAV_HEADER_SIZE + _recorded_pcm_bytes, temp_buf, to_copy);
                _recorded_pcm_bytes += to_copy;
            }

            // 实时计算录音期间麦克风能量，驱动屏幕 VU 表高频跳动
            size_t samples = bytes_read / sizeof(int16_t);
            int16_t* s_ptr = (int16_t*)temp_buf;
            int64_t sum_sq = 0;
            for (size_t i = 0; i < samples; i++) {
                sum_sq += ((int32_t)s_ptr[i] * (int32_t)s_ptr[i]);
            }
            if (samples > 0) {
                float rms = std::sqrt((float)(sum_sq / samples));
                _raw_rms = rms;
                int pct = (rms > 60.0f) ? static_cast<int>(((rms - 60.0f) / 1000.0f) * 100.0f) : 0;
                if (pct > 100) pct = 100;
                if (pct < 0) pct = 0;
                if (pct > _last_mic_rms) {
                    _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 2 + pct * 8) / 10);
                } else {
                    _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 8 + pct * 2) / 10);
                }
            }

            if (_recorded_pcm_bytes >= MAX_RECORD_PCM_BYTES) {
                stopRecording();
                break;
            }

            // 若读出的数据小于请求块，说明 DMA 队列已完全清空
            if (bytes_read < READ_CHUNK) break;
        }
    }

    bool isRecording() const { return _is_recording; }
    uint32_t getRecordDurationMs() const {
        if (_is_recording) {
            return millis() - _record_start_ms;
        }
        return (_recorded_pcm_bytes * 1000) / (SAMPLE_RATE * 2);
    }
    const uint8_t* getWavData() const { return _record_buf; }
    size_t getWavSize() const { return _has_device_audio ? (WAV_HEADER_SIZE + _recorded_pcm_bytes) : 0; }
    uint32_t getDeviceAudioId() const { return _device_audio_id; }
    bool hasDeviceAudio() const { return _has_device_audio; }

    // ==========================================
    // 网页端下发音频流播放 (AW8737 PA + I2S0 DOUT)
    // ==========================================

    bool startPlayback(const uint8_t* data, size_t len) {
        if (!_initialized || !data || len == 0) return false;

        if (_is_recording) {
            stopRecording();
        }

        // 解析 WAV 头以提取纯 PCM 数据体
        const uint8_t* pcm_start = data;
        size_t pcm_len = len;

        if (len >= 44 && memcmp(data, "RIFF", 4) == 0 && memcmp(data + 8, "WAVE", 4) == 0) {
            size_t offset = 12;
            while (offset + 8 <= len) {
                if (memcmp(data + offset, "data", 4) == 0) {
                    uint32_t sub_size = (uint32_t)data[offset + 4] |
                                        ((uint32_t)data[offset + 5] << 8) |
                                        ((uint32_t)data[offset + 6] << 16) |
                                        ((uint32_t)data[offset + 7] << 24);
                    pcm_start = data + offset + 8;
                    pcm_len = (offset + 8 + sub_size <= len) ? sub_size : (len - (offset + 8));
                    break;
                }
                uint32_t ch_size = (uint32_t)data[offset + 4] |
                                   ((uint32_t)data[offset + 5] << 8) |
                                   ((uint32_t)data[offset + 6] << 16) |
                                   ((uint32_t)data[offset + 7] << 24);
                offset += 8 + ch_size;
            }
        }

        if (pcm_len == 0) {
            Serial.println("[AUDIO] Playback error: No PCM data payload found in stream");
            return false;
        }

        _playback_ptr = pcm_start;
        _playback_total_bytes = pcm_len;
        _playback_offset = 0;
        _is_playing_stream = true;
        _playing_sound = true;

        enablePA(true);
        setCodecSpeakerMode();
        Serial.printf("[AUDIO] >>> Playback STARTED (%u PCM bytes, ~%u ms) <<<\n",
                      (unsigned)_playback_total_bytes,
                      (unsigned)((_playback_total_bytes * 1000) / (SAMPLE_RATE * 2)));
        return true;
    }

    void processPlayback() {
        if (!_is_playing_stream || !_playback_ptr) return;

        const size_t WRITE_CHUNK = 512;
        while (_is_playing_stream && _playback_offset < _playback_total_bytes) {
            size_t remaining = _playback_total_bytes - _playback_offset;
            size_t to_write = (remaining < WRITE_CHUNK) ? remaining : WRITE_CHUNK;
            size_t bytes_written = 0;
            esp_err_t res = i2s_write(I2S_NUM_0, _playback_ptr + _playback_offset, to_write, &bytes_written, 0);
            if (res != ESP_OK || bytes_written == 0) break; // DMA 缓冲满，下一帧继续填充
            _playback_offset += bytes_written;
            _playback_progress = (float)_playback_offset / (float)_playback_total_bytes;
        }

        if (_playback_offset >= _playback_total_bytes) {
            stopPlayback();
        }
    }

    void stopPlayback() {
        if (!_is_playing_stream) return;
        // 写入轻量静音段消除直流残余爆音
        int16_t silence[64] = {0};
        size_t dummy = 0;
        i2s_write(I2S_NUM_0, silence, sizeof(silence), &dummy, 10 / portTICK_PERIOD_MS);

        setCodecMicMode();
        _is_playing_stream = false;
        _playing_sound = false;
        _playback_ptr = nullptr;
        _playback_offset = 0;
        _playback_total_bytes = 0;
        _playback_progress = 0.0f;
        Serial.println("[AUDIO] >>> Playback FINISHED. Codec restored to Mic mode. <<<");
    }

    bool isPlayingStream() const { return _is_playing_stream; }
    float getPlaybackProgress() const { return _playback_progress; }

    // 主线程周期性处理切片
    void update() {
        if (_is_recording) {
            processRecording();
        } else if (_is_playing_stream) {
            processPlayback();
        }
    }

    float getRawRMS() const { return _raw_rms; }
    bool isPlaying() const { return _playing_sound || _is_playing_stream; }

private:
    TwoWire* _wire;
    bool _initialized;
    bool _speaker_powered;
    uint8_t _last_mic_rms;
    float _raw_rms;
    volatile bool _playing_sound;

    // 录音状态与 PSRAM 缓冲
    uint8_t* _record_buf;
    size_t _recorded_pcm_bytes;
    bool _is_recording;
    uint32_t _record_start_ms;
    uint32_t _record_max_ms;
    uint32_t _device_audio_id;
    bool _has_device_audio;

    // 播放状态
    const uint8_t* _playback_ptr;
    size_t _playback_total_bytes;
    size_t _playback_offset;
    bool _is_playing_stream;
    float _playback_progress;

    void ensureRecordBuffer() {
        if (!_record_buf) {
            if (psramFound()) {
                _record_buf = (uint8_t*)ps_malloc(MAX_RECORD_TOTAL_BYTES);
                Serial.printf("[AUDIO] Allocated %u bytes in PSRAM for recording\n", (unsigned)MAX_RECORD_TOTAL_BYTES);
            } else {
                _record_buf = (uint8_t*)malloc(MAX_RECORD_TOTAL_BYTES);
                Serial.printf("[AUDIO] Allocated %u bytes in Heap for recording\n", (unsigned)MAX_RECORD_TOTAL_BYTES);
            }
        }
    }

    bool writeESReg(uint8_t reg, uint8_t val) {
        _wire->beginTransmission(ES8311_ADDR);
        _wire->write(reg);
        _wire->write(val);
        return (_wire->endTransmission() == 0);
    }

    void initES8311() {
        // ES8311 标准通用配置序列
        writeESReg(0x00, 0x80); // CSM Power On
        delay(5);
        writeESReg(0x01, 0xBA); // MCLK = BCLK (Slave Mode)
        writeESReg(0x02, 0x18); // Multiplier Prescaler = 3
        writeESReg(0x0D, 0x01); // Power Up Analog Circuitry
        writeESReg(0x0E, 0x02); // Enable Analog PGA & ADC Modulator
        writeESReg(0x12, 0x00); // Power Up DAC
        writeESReg(0x13, 0x10); // Enable Output to HP/PA
        writeESReg(0x14, 0x10); // Mic1p-Mic1n Differential Input
        writeESReg(0x16, 0x03); // ADC PGA Gain (+18dB)
        writeESReg(0x17, 0xDF); // ADC Volume (+10dB)
        writeESReg(0x1C, 0x6A); // ADC Equalizer Bypass & DC Offset Cancel
        writeESReg(0x32, 0xBF); // DAC Volume (0dB)
        writeESReg(0x37, 0x08); // Bypass DAC Equalizer
    }

    void setCodecSpeakerMode() {
        // 优化 DAC 放音时钟与通道
        writeESReg(0x01, 0xB5);
        writeESReg(0x12, 0x00);
        writeESReg(0x13, 0x10);
        writeESReg(0x32, 0xBF);
    }

    void setCodecMicMode() {
        // 切回 ADC 录音拾音时钟与增益
        writeESReg(0x01, 0xBA);
        writeESReg(0x0E, 0x02);
        writeESReg(0x14, 0x10);
        writeESReg(0x16, 0x03);
        writeESReg(0x17, 0xDF);
    }
};

} // namespace sticks3
