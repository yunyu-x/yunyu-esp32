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
#include "sticks3_i2c_mutex.h"

namespace sticks3 {

enum ChimeType {
    CHIME_STARTUP = 0, // 开机上扬和弦
    CHIME_CLICK,       // 按键清脆确认短音
    CHIME_NOTIFY,      // 微信/蓝牙消息 Ding-Dong
    CHIME_ALERT,       // 权限审批急促警报
    CHIME_SUCCESS      // 成功提示音
};

// PSRAM 环形流式音频缓冲区 (用于大模型下行 response.audio.delta 毫秒级边收边播，多核安全)
class AudioRingBuffer {
public:
    explicit AudioRingBuffer(size_t capacity)
        : _capacity(capacity), _head(0), _tail(0), _count(0), _buf(nullptr),
          _mux(portMUX_INITIALIZER_UNLOCKED) {
        if (psramFound()) {
            _buf = (uint8_t*)ps_malloc(capacity);
        } else {
            _buf = (uint8_t*)malloc(capacity);
        }
    }
    ~AudioRingBuffer() {
        if (_buf) free(_buf);
    }
    size_t write(const uint8_t* data, size_t len) {
        if (!_buf || len == 0) return 0;
        portENTER_CRITICAL(&_mux);
        size_t space = _capacity - _count;
        size_t to_write = (len < space) ? len : space;
        if (to_write == 0) {
            portEXIT_CRITICAL(&_mux);
            return 0;
        }

        size_t first_chunk = (_head + to_write <= _capacity) ? to_write : (_capacity - _head);
        memcpy(_buf + _head, data, first_chunk);
        if (to_write > first_chunk) {
            memcpy(_buf, data + first_chunk, to_write - first_chunk);
        }
        _head = (_head + to_write) % _capacity;
        _count += to_write;
        portEXIT_CRITICAL(&_mux);
        return to_write;
    }
    size_t read(uint8_t* dest, size_t len) {
        if (!_buf || len == 0) return 0;
        portENTER_CRITICAL(&_mux);
        if (_count == 0) {
            portEXIT_CRITICAL(&_mux);
            return 0;
        }
        size_t to_read = (len < _count) ? len : _count;
        size_t first_chunk = (_tail + to_read <= _capacity) ? to_read : (_capacity - _tail);
        memcpy(dest, _buf + _tail, first_chunk);
        if (to_read > first_chunk) {
            memcpy(dest + first_chunk, _buf, to_read - first_chunk);
        }
        _tail = (_tail + to_read) % _capacity;
        _count -= to_read;
        portEXIT_CRITICAL(&_mux);
        return to_read;
    }
    void clear() {
        portENTER_CRITICAL(&_mux);
        _head = 0;
        _tail = 0;
        _count = 0;
        portEXIT_CRITICAL(&_mux);
    }
    size_t available() {
        portENTER_CRITICAL(&_mux);
        size_t c = _count;
        portEXIT_CRITICAL(&_mux);
        return c;
    }
    size_t capacity() const { return _capacity; }
private:
    size_t _capacity;
    size_t _head;
    size_t _tail;
    volatile size_t _count;
    uint8_t* _buf;
    portMUX_TYPE _mux;
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
          _is_playing_stream(false), _playback_progress(0.0f),
          _stream_ring_buf(nullptr), _is_streaming_llm(false),
          _audio_task_handle(nullptr), _speaker_ref_rms(0.0f),
          _voice_consecutive_frames(0) {}

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

        // 4. 预先在 PSRAM 中初始化录音缓冲区与下行流式缓冲区
        ensureRecordBuffer();
        if (!_stream_ring_buf) {
            _stream_ring_buf = new AudioRingBuffer(256 * 1024); // 256KB PSRAM 环形流式缓冲区 (~8s PCM16)
            Serial.println("[AUDIO] Allocated 256KB PSRAM stream ring buffer for LLM playback");
        }

        // 5. 启动独立 FreeRTOS 音频流式播放任务 (Core 1, 优先级 3, 栈 4KB)
        if (!_audio_task_handle) {
            xTaskCreatePinnedToCore(audioTaskStatic, "audioTask", 4096, this, 3, &_audio_task_handle, 1);
            Serial.println("[AUDIO] FreeRTOS audioTask pinned to Core 1 (Prio: 3)");
        }

        _initialized = true;
        Serial.println("[AUDIO] ES8311 Codec & AW8737 PA & MEMS Mic ONLINE!");
        return true;
    }

    void enablePA(bool enable) {
        if (!_wire) return;
        I2CLockGuard guard(50);
        if (!guard.isAcquired()) return;

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
            i2s_write(I2S_NUM_0, buf, to_write * sizeof(int16_t), &bytes_written, 50 / portTICK_PERIOD_MS);
            samples_generated += to_write;
        }

        // 静音缓冲消除尾部直流偏置
        memset(buf, 0, sizeof(buf));
        size_t dummy = 0;
        i2s_write(I2S_NUM_0, buf, sizeof(buf), &dummy, 50 / portTICK_PERIOD_MS);

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
        if (!_initialized) return 0;
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

        // 解析 WAV 头以提取纯 PCM 数据体与采样率
        const uint8_t* pcm_start = data;
        size_t pcm_len = len;
        uint32_t wav_sr = SAMPLE_RATE;

        if (len >= 44 && memcmp(data, "RIFF", 4) == 0 && memcmp(data + 8, "WAVE", 4) == 0) {
            uint32_t header_sr = (uint32_t)data[24] |
                                 ((uint32_t)data[25] << 8) |
                                 ((uint32_t)data[26] << 16) |
                                 ((uint32_t)data[27] << 24);
            if (header_sr >= 8000 && header_sr <= 48000) {
                wav_sr = header_sr;
            }

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

        if (wav_sr != SAMPLE_RATE) {
            Serial.printf("[AUDIO] WAV custom sample rate %u Hz detected, dynamically switching I2S clock...\n", (unsigned)wav_sr);
            i2s_set_sample_rates(I2S_NUM_0, wav_sr);
        }

        _playback_ptr = pcm_start;
        _playback_total_bytes = pcm_len;
        _playback_offset = 0;
        _is_playing_stream = true;
        _playing_sound = true;

        enablePA(true);
        setCodecSpeakerMode();
        Serial.printf("[AUDIO] >>> Playback STARTED (%u PCM bytes, ~%u ms, Rate: %u Hz) <<<\n",
                      (unsigned)_playback_total_bytes,
                      (unsigned)((_playback_total_bytes * 1000) / (wav_sr * 2)),
                      (unsigned)wav_sr);
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

        // 恢复 I2S 硬件时钟为标准 16000 Hz
        i2s_set_sample_rates(I2S_NUM_0, SAMPLE_RATE);

        setCodecMicMode();
        _is_playing_stream = false;
        _playing_sound = false;
        _playback_ptr = nullptr;
        _playback_offset = 0;
        _playback_total_bytes = 0;
        _playback_progress = 0.0f;
        Serial.println("[AUDIO] >>> Playback FINISHED. Codec restored to Mic mode (16kHz). <<<");
    }

    bool isPlayingStream() const { return _is_playing_stream; }
    float getPlaybackProgress() const { return _playback_progress; }

    // ==========================================
    // 大模型实时下行流式音频播放与毫秒级中途打断
    // ==========================================

    // 压入来自 WebSocket response.audio.delta 的 PCM 数据 (支持 16kHz 与 24kHz 自适应下采样)
    void feedStreamPCM(const uint8_t* pcm_data, size_t len, uint32_t src_sample_rate = 16000) {
        if (!_initialized || !pcm_data || len == 0 || !_stream_ring_buf) return;
        
        // 若上游因模型差异或未生效下发 24kHz 音频，就地执行 3:2 快速线性插值降采样为 16kHz
        if (src_sample_rate == 24000 && len >= 6) {
            static int16_t* s_resample_buf = nullptr;
            if (!s_resample_buf) {
                s_resample_buf = (int16_t*)ps_malloc(32768);
            }
            if (s_resample_buf) {
                const int16_t* in_ptr = (const int16_t*)pcm_data;
                size_t in_samples = len / sizeof(int16_t);
                size_t out_idx = 0;
                size_t i = 0;
                // 3 个输入点对应 2 个输出点 (24000 * 2 / 3 = 16000)
                for (; i + 2 < in_samples && out_idx + 1 < 16384; i += 3) {
                    s_resample_buf[out_idx++] = in_ptr[i];
                    s_resample_buf[out_idx++] = (int16_t)(((int32_t)in_ptr[i + 1] + (int32_t)in_ptr[i + 2]) >> 1);
                }
                // 处理末尾剩余 1~2 个孤立采样点
                for (; i < in_samples && out_idx < 16384; ++i) {
                    s_resample_buf[out_idx++] = in_ptr[i];
                }
                _stream_ring_buf->write((const uint8_t*)s_resample_buf, out_idx * sizeof(int16_t));
            } else {
                _stream_ring_buf->write(pcm_data, len);
            }
        } else {
            // 原生 16kHz 直通写入 PSRAM 环形队列
            _stream_ring_buf->write(pcm_data, len);
        }

        if (!_is_streaming_llm) {
            _is_streaming_llm = true;
            _playing_sound = true;
            _speaker_ref_rms = 0.0f;
            _voice_consecutive_frames = 0;
            enablePA(true);
            setCodecFullDuplexMode(); // 全双工时钟保活，保证麦克风在放音时持续采集
            Serial.printf("[AUDIO] >>> LLM Full-Duplex Stream Playback STARTED (Src: %uHz, Buffered %u bytes) <<<\n",
                          (unsigned)src_sample_rate, (unsigned)_stream_ring_buf->available());
        }
    }

    static void audioTaskStatic(void* arg) {
        StickS3Audio* self = static_cast<StickS3Audio*>(arg);
        self->audioTaskLoop();
    }

    void audioTaskLoop() {
        const size_t WRITE_CHUNK = 512;
        uint8_t chunk[WRITE_CHUNK];

        while (true) {
            if (_is_streaming_llm && _stream_ring_buf && _stream_ring_buf->available() > 0) {
                size_t to_read = (_stream_ring_buf->available() < WRITE_CHUNK) ? _stream_ring_buf->available() : WRITE_CHUNK;
                size_t n = _stream_ring_buf->read(chunk, to_read);
                if (n > 0) {
                    size_t bytes_written = 0;
                    i2s_write(I2S_NUM_0, chunk, n, &bytes_written, 25 / portTICK_PERIOD_MS);

                    // 实时解算喇叭写入能量，采用 Fast Attack & Slow Decay 包络跟踪
                    // 补偿 I2S DMA 128ms 硬件延迟，防止因物理声学滞后导致参考信号过低
                    size_t spk_samples = bytes_written / sizeof(int16_t);
                    if (spk_samples > 0) {
                        int16_t* spk_ptr = (int16_t*)chunk;
                        int64_t spk_sum_sq = 0;
                        for (size_t i = 0; i < spk_samples; ++i) {
                            int32_t val = spk_ptr[i];
                            spk_sum_sq += val * val;
                        }
                        float cur_spk_rms = std::sqrt((float)(spk_sum_sq / spk_samples));
                        if (cur_spk_rms > _speaker_ref_rms) {
                            _speaker_ref_rms = cur_spk_rms; // 瞬时吸收峰值 (Fast Attack)
                        } else {
                            _speaker_ref_rms = (_speaker_ref_rms * 0.94f) + (cur_spk_rms * 0.06f); // 慢释音衰减 (~180ms Slow Decay)
                        }
                    }
                }
                vTaskDelay(pdMS_TO_TICKS(1)); // 主动交出 CPU 调度权，防止独占 Core 1 导致 TWDT 触发或 loopTask 饥饿
            } else {
                vTaskDelay(pdMS_TO_TICKS(4));
            }
        }
    }

    uint32_t getAudioTaskStackHighWaterMark() const {
        return _audio_task_handle ? (uint32_t)uxTaskGetStackHighWaterMark(_audio_task_handle) : 0;
    }

    void processStreamingPlayback() {
        // 由独立 FreeRTOS audioTask 持续异步接管，保持该方法以兼容旧接口
    }

    // 毫秒级中途打断 (Barge-In) 核心方法
    void interruptPlayback() {
        if (!_is_streaming_llm && !_is_playing_stream && !_playing_sound) return;

        Serial.println("[AUDIO] >>> Playback INTERRUPTED (Barge-In)! Immediate mute & buffer clear <<<");
        if (_stream_ring_buf) {
            _stream_ring_buf->clear();
        }

        // 写入轻量静音段消除直流残余爆音
        int16_t silence[128] = {0};
        size_t dummy = 0;
        i2s_write(I2S_NUM_0, silence, sizeof(silence), &dummy, 10 / portTICK_PERIOD_MS);

        setCodecMicMode();
        _is_streaming_llm = false;
        _is_playing_stream = false;
        _playing_sound = false;
        _speaker_ref_rms = 0.0f;
        _voice_consecutive_frames = 0;
        _playback_ptr = nullptr;
        _playback_offset = 0;
        _playback_total_bytes = 0;
        _playback_progress = 0.0f;
    }

    void finishStreamPlayback() {
        if (!_is_streaming_llm && !_playing_sound) return;

        // 写入轻量静音段消除直流残余爆音
        int16_t silence[64] = {0};
        size_t dummy = 0;
        i2s_write(I2S_NUM_0, silence, sizeof(silence), &dummy, 10 / portTICK_PERIOD_MS);

        setCodecMicMode();
        _is_streaming_llm = false;
        _is_playing_stream = false;
        _playing_sound = false;
        _speaker_ref_rms = 0.0f;
        _voice_consecutive_frames = 0;
        Serial.println("[AUDIO] >>> LLM Stream Playback FINISHED. Codec restored to Mic mode. <<<");
    }

    // ==========================================
    // 极轻量级人声采集打断触发器 (Voice Barge-In)
    // 1. 动态过滤喇叭播放音频耦合 (Acoustic Echo Filtering)
    // 2. 时域过零率 (Zero Crossing Rate) 人声频带鉴别 (排除低频撞击与高频白噪)
    // 3. 连续帧平滑鉴别 (32ms~48ms 持续开口)，杜绝单点爆音误触
    // ==========================================
    bool checkVoiceBargeInTrigger() {
        if (!_initialized || !_is_streaming_llm) return false;

        const size_t CHUNK_SAMPLES = 256; // 16ms 采样窗
        int16_t mic_buf[CHUNK_SAMPLES];
        size_t bytes_read = 0;
        esp_err_t res = i2s_read(I2S_NUM_0, mic_buf, sizeof(mic_buf), &bytes_read, 0);
        if (res != ESP_OK || bytes_read < 64) return false;

        size_t samples = bytes_read / sizeof(int16_t);
        if (samples == 0) return false;

        // 1. 提取直流偏置与计算麦克风总能量
        int32_t mean = 0;
        for (size_t i = 0; i < samples; ++i) mean += mic_buf[i];
        mean /= (int32_t)samples;

        int64_t sum_sq = 0;
        int zero_crossings = 0;
        int16_t prev_s = mic_buf[0] - mean;

        for (size_t i = 0; i < samples; ++i) {
            int16_t s = mic_buf[i] - mean;
            sum_sq += (int32_t)s * (int32_t)s;
            // 计算时域过零点 (Zero Crossing)
            if ((prev_s < 0 && s >= 0) || (prev_s >= 0 && s < 0)) {
                zero_crossings++;
            }
            prev_s = s;
        }

        float mic_raw_rms = std::sqrt((float)(sum_sq / samples));
        int norm_zcr = (int)((float)zero_crossings * 256.0f / (float)samples);

        // 2. 声学回声能量动态解耦 (结合 StickS3 腔体物理耦合标定与 DMA 滞后保护)
        float echo_est = _speaker_ref_rms * 0.78f;
        if (echo_est < 60.0f && _speaker_ref_rms > 30.0f) {
            echo_est = 60.0f;
        }
        float clean_voice_rms = mic_raw_rms - echo_est;
        if (clean_voice_rms < 0.0f) clean_voice_rms = 0.0f;

        // 3. 映射到 0~100% 相对音量百分比
        int clean_pct = (clean_voice_rms > 50.0f) ? static_cast<int>(((clean_voice_rms - 50.0f) / 800.0f) * 100.0f) : 0;
        if (clean_pct > 100) clean_pct = 100;

        // 同步更新屏幕 VU 能量
        if (clean_pct > _last_mic_rms) {
            _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 2 + clean_pct * 8) / 10);
        } else {
            _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 8 + clean_pct * 2) / 10);
        }

        // 4. 严谨灵敏人声特征判决 (声学自激抑制 + 灵敏人声响应)：
        // a) 净人声音量显著高于喇叭回声: clean_pct >= 10% 且 clean_voice_rms >= 110.0f
        // b) 总麦克风能量需超越喇叭回声门限: mic_raw_rms > (echo_est * 1.06f + 70.0f)
        // c) 时域归一化过零率处于人类声学频段 [8, 145] (覆盖男低音80Hz至女高音与摩擦辅音)
        bool frame_is_voice = (clean_pct >= 10) && (clean_voice_rms >= 110.0f) &&
                              (norm_zcr >= 8 && norm_zcr <= 145) &&
                              (mic_raw_rms > (echo_est * 1.06f + 70.0f));

        if (frame_is_voice) {
            _voice_consecutive_frames++;
            if (_voice_consecutive_frames >= 2) { // 连续 2 帧 (~32ms) 确认为稳定人类开口说话，响应灵敏
                _voice_consecutive_frames = 0;
                Serial.printf("[AUDIO-VAD] True voice barge-in fired! MicRMS=%.1f, EchoEst=%.1f, CleanRMS=%.1f (Pct=%d%%), NormZCR=%d\n",
                              mic_raw_rms, echo_est, clean_voice_rms, clean_pct, norm_zcr);
                return true;
            }
        } else {
            if (_voice_consecutive_frames > 0) {
                _voice_consecutive_frames--;
            }
        }

        return false;
    }

    // 智能本地人声活动判定 (过滤键盘敲击、碰桌子、呼吸声等非语音杂音)
    // 返回: 是否处于真实稳定人声发音区间
    bool isHumanVocalActivity(const int16_t* samples, size_t count) {
        if (!samples || count < 128) return false;

        int32_t mean = 0;
        for (size_t i = 0; i < count; ++i) mean += samples[i];
        mean /= (int32_t)count;

        int64_t sum_sq = 0;
        int zero_crossings = 0;
        int16_t prev = samples[0] - mean;
        for (size_t i = 0; i < count; ++i) {
            int16_t s = samples[i] - mean;
            sum_sq += (int32_t)s * (int32_t)s;
            if ((prev < 0 && s >= 0) || (prev >= 0 && s < 0)) {
                zero_crossings++;
            }
            prev = s;
        }

        float rms = std::sqrt((float)(sum_sq / count));
        int norm_zcr = (int)((float)zero_crossings * 256.0f / (float)count);

        // 真实人声特征灵敏标定：
        // RMS >= 75.0f (约 2%~5% 音量，完全覆盖正常室内 30~50cm 正常人声发音，杜绝过高门槛将用户说话误杀)
        // 且归一化过零率处于人类声学频段 [6, 150] (排除 <6 机械低频颠簸 与 >150 清脆高频爆破杂音)
        return (rms >= 75.0f && norm_zcr >= 6 && norm_zcr <= 150);
    }

    bool isStreamingLLM() const { return _is_streaming_llm; }
    size_t getStreamBufferAvailable() const { return _stream_ring_buf ? _stream_ring_buf->available() : 0; }

    // 全双工麦克风非阻塞采样读取 (用于大模型上行 input_audio_buffer.append)
    bool readMicSamples(int16_t* dest, size_t max_samples, size_t& samples_read) {
        samples_read = 0;
        if (!_initialized || !dest || max_samples == 0) return false;

        size_t bytes_read = 0;
        esp_err_t res = i2s_read(I2S_NUM_0, dest, max_samples * sizeof(int16_t), &bytes_read, 0);
        if (res == ESP_OK && bytes_read > 0) {
            samples_read = bytes_read / sizeof(int16_t);
            // 同步解算麦克风实时能量 RMS 驱动屏幕 VU 表和本地 VAD
            int32_t mean = 0;
            for (size_t i = 0; i < samples_read; ++i) mean += dest[i];
            mean /= (int32_t)samples_read;
            int64_t sum_sq = 0;
            for (size_t i = 0; i < samples_read; ++i) {
                int32_t diff = dest[i] - mean;
                sum_sq += (diff * diff);
            }
            _raw_rms = std::sqrt((float)(sum_sq / samples_read));
            int pct = 0;
            if (_raw_rms > 60.0f) {
                pct = static_cast<int>(((_raw_rms - 60.0f) / 1000.0f) * 100.0f);
            }
            if (pct < 0) pct = 0;
            if (pct > 100) pct = 100;
            if (pct > _last_mic_rms) {
                _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 2 + pct * 8) / 10);
            } else {
                _last_mic_rms = static_cast<uint8_t>((_last_mic_rms * 8 + pct * 2) / 10);
            }
            return true;
        }
        return false;
    }

    // 主线程周期性处理切片
    void update() {
        if (_is_recording) {
            processRecording();
        } else if (_is_playing_stream) {
            processPlayback();
        }
    }

    float getRawRMS() const { return _raw_rms; }
    bool isPlaying() const { return _playing_sound || _is_playing_stream || _is_streaming_llm; }

private:
    TaskHandle_t _audio_task_handle;
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

    // 流式大模型下行缓冲
    AudioRingBuffer* _stream_ring_buf;
    bool _is_streaming_llm;
    volatile float _speaker_ref_rms;
    volatile uint8_t _voice_consecutive_frames;

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
        if (!_wire) return false;
        I2CLockGuard guard(50);
        if (!guard.isAcquired()) return false;

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

    void setCodecFullDuplexMode() {
        // 全双工模式：同时开启 ADC 拾音与 DAC 放音，保证麦克风硬件时钟与放大器持续工作
        writeESReg(0x01, 0xBF); // CLKADC_ON=1 & CLKDAC_ON=1 (同时保持 ADC 和 DAC 时钟)
        writeESReg(0x0E, 0x02); // Enable Analog PGA & ADC Modulator
        writeESReg(0x14, 0x10); // Mic1p-Mic1n Differential Input
        writeESReg(0x16, 0x03); // ADC PGA Gain (+18dB)
        writeESReg(0x17, 0xDF); // ADC Volume (+10dB)
        writeESReg(0x1C, 0x6A); // ADC Equalizer Bypass & DC Offset Cancel
        writeESReg(0x12, 0x00); // Power Up DAC
        writeESReg(0x13, 0x10); // Enable Output to HP/PA
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
