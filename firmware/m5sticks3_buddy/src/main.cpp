/**
 * firmware/m5sticks3_buddy/src/main.cpp
 * --------------------------------------
 * M5Stack StickS3 硬件深度标定与双模融合固件：
 * 1. 物理引脚精确定位：
 *    - PMIC (M5PM1 @ 0x6E): I2C SDA=G47, SCL=G48 (100kHz)
 *    - L3B LCD供电轨: PM1 GPIO2 输出高电平使能 (必选，否则屏幕0V不亮)
 *    - 显示屏 (ST7789P3 135x240): SPI3 (MOSI:G39, SCLK:G40, DC:G45, CS:G41, RST:G21, BL:G38)
 *    - 姿态传感 (BMI270 @ 0x68): I2C SDA=G47, SCL=G48
 *    - 物理按键: Btn A=G11, Btn B=G12 (内置上拉输入，低电平有效)
 * 2. 协议与交互：
 *    - Claude Desktop Buddy BLE Nordic UART Service (NUS)
 *    - 灵方自重构机器人地面调测与遥测流回显
 */

#include <Arduino.h>
#include <Wire.h>
#include <M5GFX.h>
#include <lgfx/v1/panel/Panel_ST7789.hpp>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <esp_bt.h>
#include <cmath>
#include <utility/imu/BMI270_config.inl>
#include "sticks3_hal.h"
#include "buddy_protocol.h"
#include "sticks3_audio.h"
#include "sticks3_wifi_config.h"
#include "sticks3_bailian_client.h"
#include "sticks3_wifi.h"
#include "gbk_to_utf8.h"
#include "sticks3_i2c_mutex.h"
#include "sticks3_system_metrics.h"
#include "sticks3_memory_store.h"
#include "sticks3_wakeword.h"

using namespace sticks3::protocol;

// 蓝牙 NUS UUIDs
#define SERVICE_UUID           "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define CHARACTERISTIC_UUID_RX "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
#define CHARACTERISTIC_UUID_TX "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

// 硬件常量
constexpr int PIN_BTN_A = 11; // 正面主键
constexpr int PIN_BTN_B = 12; // 侧面辅键
constexpr int PIN_I2C_SDA = 47;
constexpr int PIN_I2C_SCL = 48;
constexpr uint8_t PM1_ADDR = 0x6E;
constexpr uint8_t BMI270_ADDR = 0x68;

constexpr int SCREEN_W = 135;
constexpr int SCREEN_H = 240;

// 自定义 StickS3 显式硬件驱动架构 (基于 M5GFX / LovyanGFX)
class StickS3Display : public lgfx::LGFX_Device {
    lgfx::Panel_ST7789 _panel_instance;
    lgfx::Bus_SPI      _bus_instance;
    lgfx::Light_PWM    _light_instance;

public:
    StickS3Display() {
        {
            auto cfg = _bus_instance.config();
            cfg.spi_host   = SPI3_HOST;
            cfg.spi_mode   = 0;
            cfg.freq_write = 40000000;
            cfg.freq_read  = 16000000;
            cfg.spi_3wire  = true;
            cfg.use_lock   = true;
            cfg.pin_sclk   = GPIO_NUM_40;
            cfg.pin_mosi   = GPIO_NUM_39;
            cfg.pin_miso   = GPIO_NUM_NC;
            cfg.pin_dc     = GPIO_NUM_45;
            _bus_instance.config(cfg);
            _panel_instance.setBus(&_bus_instance);
        }
        {
            auto cfg = _panel_instance.config();
            cfg.pin_cs           = GPIO_NUM_41;
            cfg.pin_rst          = GPIO_NUM_21;
            cfg.pin_busy         = GPIO_NUM_NC;
            cfg.panel_width      = SCREEN_W;
            cfg.panel_height     = SCREEN_H;
            cfg.offset_x         = 52;
            cfg.offset_y         = 40;
            cfg.offset_rotation  = 0;
            cfg.dummy_read_pixel = 8;
            cfg.dummy_read_bits  = 1;
            cfg.readable         = true;
            cfg.invert           = true;
            cfg.rgb_order        = false;
            cfg.dlen_16bit       = false;
            cfg.bus_shared       = false;
            _panel_instance.config(cfg);
        }
        {
            auto cfg = _light_instance.config();
            cfg.pin_bl      = GPIO_NUM_38;
            cfg.invert      = false;
            cfg.freq        = 44100;
            cfg.pwm_channel = 7;
            _light_instance.config(cfg);
            _panel_instance.setLight(&_light_instance);
        }
        setPanel(&_panel_instance);
    }
};

static StickS3Display display;
static BLEServer* pServer = nullptr;
static BLECharacteristic* pTxCharacteristic = nullptr;
static bool device_connected = false;
static bool old_device_connected = false;

static BuddyProtocolEngine protocol_engine;

// 全局状态变量
static uint32_t last_heartbeat = 0;
static uint32_t last_anim_tick = 0;
static uint32_t last_serial_telem = 0;
static uint16_t theme_color = TFT_BLUE;
static uint32_t frame_count = 0;
static int anim_frame = 0;
static bool ext_5v_enabled = false;
static float battery_voltage = 4.10f;
static float imu_roll = 0.0f;
static float imu_pitch = 0.0f;
static float imu_ax = 0.0f;
static float imu_ay = 0.0f;
static float imu_az = 0.0f;
static uint8_t bmi270_actual_addr = 0x68;
static bool bmi270_online = false;

// 接收小程序/蓝牙文本消息缓冲区
static String latest_ble_msg = "";
static uint32_t last_ble_msg_time = 0;
static uint32_t total_ble_msgs_received = 0;
static bool has_new_ble_msg = false;

// 按键边沿检测
static bool btnA_prev = HIGH;
static bool btnB_prev = HIGH;
static bool btnA_clicked = false;
static bool btnB_clicked = false;

void sendToHost(const std::string& msg);

// 统一消息处理入口 (处理来自 BLE NUS, WiFi TCP 8080, WiFi UDP 8080, Web 80 与串口的全部文本/汉字)
void onNewTextMessage(const String& msg, const String& source) {
    if (msg.length() == 0) return;
    
    // 自动清洗与编码自适应归一化 (无论是 UTF-8、GBK/GB2312 还是 Hex 文本，均转为标准 UTF-8)
    String clean_msg = sanitizeAndConvertToUtf8((const uint8_t*)msg.c_str(), msg.length());
    clean_msg.trim();
    if (clean_msg.length() == 0) return;

    latest_ble_msg = clean_msg;
    total_ble_msgs_received++;
    last_ble_msg_time = millis();
    has_new_ble_msg = true;
    
    Serial.printf("\n[CHAT-RX] >>> [%s] (#%u): \"%s\"\n",
                  source.c_str(), (unsigned)total_ble_msgs_received, clean_msg.c_str());

    // 检查是否为控制指令
    if (clean_msg.equalsIgnoreCase("wifi") || clean_msg.equalsIgnoreCase("scan")) {
        sticks3::StickS3WiFi::getInstance().triggerScan();
        std::string wresp = sticks3::StickS3WiFi::getInstance().getScanResultsJSON().c_str();
        sendToHost(wresp + "\n");
        sticks3::StickS3Audio::getInstance().playChime(sticks3::CHIME_SUCCESS);
    } else if (clean_msg.equalsIgnoreCase("beep") || clean_msg.equalsIgnoreCase("play")) {
        sticks3::StickS3Audio::getInstance().playChime(sticks3::CHIME_NOTIFY);
    } else {
        // 普通文本（含汉字）：播放即时提示和弦音
        sticks3::StickS3Audio::getInstance().playChime(sticks3::CHIME_NOTIFY);
    }

    // 若当前为 BLE 连接模式，向手机回送即时轻量 ACK 确认帧 (避免超出 23 字节 MTU)
    if (device_connected && pTxCharacteristic) {
        std::string ack = "[StickS3 ACK #" + std::to_string(total_ble_msgs_received) + "]\n";
        pTxCharacteristic->setValue((uint8_t*)ack.c_str(), ack.length());
        pTxCharacteristic->notify();
    }
}

// 专用汉字多行排版渲染引擎 (基于 LovyanGFX / M5GFX)
void drawChineseText(StickS3Display& d, const String& text, int start_x, int start_y, int max_w, int line_height, uint16_t color, uint16_t bg, const lgfx::U8g2font* font = &fonts::efontCN_12) {
    d.setFont(font);
    d.setTextDatum(TL_DATUM);
    d.setTextColor(color, bg);
    
    int cur_x = start_x;
    int cur_y = start_y;
    int max_y = start_y + line_height * 3; // 最多渲染 3 行
    
    const char* p = text.c_str();
    while (*p && cur_y < max_y) {
        if (*p == '\r') { p++; continue; }
        if (*p == '\n') {
            cur_x = start_x;
            cur_y += line_height;
            p++;
            continue;
        }
        
        // 解析 UTF-8 字符字节长度
        unsigned char c = (unsigned char)*p;
        int len = 1;
        if ((c & 0x80) == 0) len = 1;
        else if ((c & 0xE0) == 0xC0) len = 2;
        else if ((c & 0xF0) == 0xE0) len = 3;
        else if ((c & 0xF8) == 0xF0) len = 4;
        
        bool complete = true;
        char single_char[5] = {0};
        for (int i = 0; i < len; i++) {
            if (*p == '\0') {
                complete = false;
                break;
            }
            single_char[i] = *p++;
        }
        if (!complete) break; // 避免末尾截断字节被解析为非法字符而渲染出方块
        
        int char_w = d.textWidth(single_char, font);
        if (char_w <= 0) char_w = (len > 1) ? 12 : 6;
        
        // 行宽越界自动折行
        if (cur_x + char_w > start_x + max_w) {
            cur_x = start_x;
            cur_y += line_height;
            if (cur_y >= max_y) {
                d.drawString("...", cur_x, cur_y - line_height, font);
                break;
            }
        }
        
        d.drawString(single_char, cur_x, cur_y, font);
        cur_x += char_w;
    }
}

// BLE 异步接收多包重组与临界区同步变量 (原生二进制字节缓冲，杜绝零字节截断与编码损坏)
static std::vector<uint8_t> ble_accum_bytes;
static uint32_t last_ble_rx_tick = 0;
static bool ble_rx_pending = false;
static portMUX_TYPE ble_mux = portMUX_INITIALIZER_UNLOCKED;

// BLE 回调
class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override { device_connected = true; }
    void onDisconnect(BLEServer* pServer) override { device_connected = false; }
};

class RxCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) override {
        std::string rxValue = pCharacteristic->getValue();
        if (rxValue.length() > 0) {
            portENTER_CRITICAL(&ble_mux);
            const uint8_t* pdata = (const uint8_t*)rxValue.data();
            ble_accum_bytes.insert(ble_accum_bytes.end(), pdata, pdata + rxValue.length());
            last_ble_rx_tick = millis();
            ble_rx_pending = true;
            portEXIT_CRITICAL(&ble_mux);

            // 仍兼容协议引擎 (若为 Claude Buddy 权限审批帧则触发审批页)
            protocol_engine.feedBytes(rxValue.c_str(), rxValue.length());
        }
    }
};

void sendToHost(const std::string& msg) {
    if (device_connected && pTxCharacteristic) {
        pTxCharacteristic->setValue((uint8_t*)msg.c_str(), msg.length());
        pTxCharacteristic->notify();
    }
    Serial.print(msg.c_str());
}

// M5PM1 硬件供电激活 (关键：开启 L3B LCD 供电)
bool initM5PM1() {
    Wire1.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    delay(50);

    Wire1.beginTransmission(PM1_ADDR);
    Wire1.write(0x00);
    uint8_t err = Wire1.endTransmission();
    Serial.printf("[PM1-INIT] I2C Probe PM1 (0x%02X): %s (code %d)\n", PM1_ADDR, err == 0 ? "SUCCESS" : "FAILED", err);
    if (err != 0) return false;

    // 读取芯片 ID
    Wire1.requestFrom(PM1_ADDR, (uint8_t)2);
    uint16_t dev_id = 0;
    if (Wire1.available() >= 2) {
        dev_id = Wire1.read() | (Wire1.read() << 8);
    }
    Serial.printf("[PM1-INIT] PM1 Device ID: 0x%04X (Expected: 0x2050)\n", dev_id);

    auto writePM1 = [](uint8_t reg, uint8_t val) {
        Wire1.beginTransmission(PM1_ADDR);
        Wire1.write(reg);
        Wire1.write(val);
        Wire1.endTransmission();
    };

    auto readPM1 = [](uint8_t reg) -> uint8_t {
        Wire1.beginTransmission(PM1_ADDR);
        Wire1.write(reg);
        Wire1.endTransmission(false);
        Wire1.requestFrom(PM1_ADDR, (uint8_t)1);
        return Wire1.available() ? Wire1.read() : 0;
    };

    // 禁用 I2C 休眠 (0x09=0) 与看门狗 (0x0A=0)
    writePM1(0x09, 0x00);
    writePM1(0x0A, 0x00);

    // 使能电源通道 (LDO, DCDC, 充电, LED 控制)
    writePM1(0x06, 0x17);

    // 配置 PM1 GPIO2 为通用推挽输出并拉高，点亮 L3B LCD 3.3V 供电轨
    uint8_t r16 = readPM1(0x16);
    writePM1(0x16, r16 & ~(1 << 2)); // GPIO 功能

    uint8_t r10 = readPM1(0x10);
    writePM1(0x10, r10 | (1 << 2));  // 输出模式

    uint8_t r13 = readPM1(0x13);
    writePM1(0x13, r13 & ~(1 << 2)); // 推挽

    uint8_t r11 = readPM1(0x11);
    writePM1(0x11, r11 | (1 << 2));  // 输出高电平 (L3B ON!)

    Serial.println("[PM1-INIT] L3B Power Rail (LCD Power) successfully ENABLED!");

    // 配置 PM1 GPIO3 为通用推挽输出并拉高，使能 AW8737 喇叭功放供电轨
    writePM1(0x16, readPM1(0x16) & ~(1 << 3)); // GPIO3 功能
    writePM1(0x10, readPM1(0x10) | (1 << 3));  // 输出模式
    writePM1(0x13, readPM1(0x13) & ~(1 << 3)); // 推挽
    writePM1(0x11, readPM1(0x11) | (1 << 3));  // 输出高电平 (Speaker PA ON!)
    Serial.println("[PM1-INIT] Speaker PA Power Rail (GPIO3) successfully ENABLED!");
    delay(80);
    return true;
}

static uint8_t readI2CReg(uint8_t addr, uint8_t reg) {
    sticks3::I2CLockGuard guard(50);
    if (!guard.isAcquired()) return 0xFF;

    Wire1.beginTransmission(addr);
    Wire1.write(reg);
    if (Wire1.endTransmission(false) != 0) return 0xFF;
    if (Wire1.requestFrom(addr, (uint8_t)1) == 1) {
        return Wire1.read();
    }
    return 0xFF;
}

static bool writeI2CReg(uint8_t addr, uint8_t reg, uint8_t val) {
    sticks3::I2CLockGuard guard(50);
    if (!guard.isAcquired()) return false;

    Wire1.beginTransmission(addr);
    Wire1.write(reg);
    Wire1.write(val);
    return (Wire1.endTransmission() == 0);
}

// 扫描 Wire1 (G47/G48) 总线上全部可用设备
void scanI2CBus() {
    Serial.println("\n--- [I2C-SCAN] Scanning Wire1 (SDA=G47, SCL=G48) ---");
    int count = 0;
    for (uint8_t addr = 1; addr < 127; addr++) {
        Wire1.beginTransmission(addr);
        if (Wire1.endTransmission() == 0) {
            Serial.printf("  [+] I2C device detected at 0x%02X\n", addr);
            count++;
        }
    }
    Serial.printf("--- [I2C-SCAN] Total %d devices discovered ---\n", count);
}

// 向 Bosch BMI270 上传官方微码固件 Blob
bool uploadBMI270Config(uint8_t addr) {
    Serial.printf("[BMI270] Uploading microcode configuration blob (%u bytes)...\n", (unsigned)sizeof(bmi270_config_file));
    
    // 1. 禁用初始化准备
    writeI2CReg(addr, 0x59, 0x00);
    delay(1);

    // 2. 分块写入 (每次 64 字节，满足 I2C FIFO 缓冲区深度限制)
    const size_t total_len = sizeof(bmi270_config_file);
    for (size_t offset = 0; offset < total_len; offset += 64) {
        size_t chunk_len = (total_len - offset < 64) ? (total_len - offset) : 64;
        
        // 16-bit 字地址偏移
        size_t word_idx = offset / 2;
        uint8_t addr_bytes[2] = {
            (uint8_t)(word_idx & 0x0F),
            (uint8_t)(word_idx >> 4)
        };
        
        // 写入 INIT_ADDR_0 (0x5B) 与 INIT_ADDR_1 (0x5C)
        Wire1.beginTransmission(addr);
        Wire1.write(0x5B);
        Wire1.write(addr_bytes[0]);
        Wire1.write(addr_bytes[1]);
        if (Wire1.endTransmission() != 0) {
            Serial.printf("[BMI270] Error writing chunk addr at offset %u\n", (unsigned)offset);
            return false;
        }
        
        // 写入 INIT_DATA (0x5E)
        Wire1.beginTransmission(addr);
        Wire1.write(0x5E);
        Wire1.write(&bmi270_config_file[offset], chunk_len);
        if (Wire1.endTransmission() != 0) {
            Serial.printf("[BMI270] Error writing chunk data at offset %u\n", (unsigned)offset);
            return false;
        }
    }
    
    // 3. 提交固件加载: INIT_CTRL = 0x01
    writeI2CReg(addr, 0x59, 0x01);
    delay(20);
    
    // 4. 轮询 INTERNAL_STATUS (0x21) 校验状态
    for (int retry = 0; retry < 50; retry++) {
        uint8_t status = readI2CReg(addr, 0x21);
        if (status == 0x01) {
            Serial.printf("[BMI270] Microcode load SUCCESS (INTERNAL_STATUS=0x01, retry=%d)\n", retry);
            return true;
        }
        delay(2);
    }
    uint8_t final_status = readI2CReg(addr, 0x21);
    Serial.printf("[BMI270] Microcode load final status: 0x%02X\n", final_status);
    return (final_status == 0x01);
}

// 自动探测并初始化 BMI270 姿态传感器
bool initBMI270() {
    uint8_t candidate_addrs[] = {0x68, 0x69};
    uint8_t found_addr = 0;
    
    for (uint8_t addr : candidate_addrs) {
        uint8_t id = readI2CReg(addr, 0x00);
        Serial.printf("[BMI270-PROBE] Addr 0x%02X -> Chip ID 0x%02X\n", addr, id);
        if (id == 0x24) {
            found_addr = addr;
            break;
        }
    }
    
    if (found_addr == 0) {
        Serial.println("[BMI270-PROBE] No BMI270 (ID 0x24) found on 0x68 or 0x69!");
        // 回退检查 MPU6886 (reg 0x75 == 0x19)
        uint8_t mpu_id = readI2CReg(0x68, 0x75);
        Serial.printf("[IMU-FALLBACK] Checking MPU6886 reg 0x75: 0x%02X\n", mpu_id);
        return false;
    }
    
    bmi270_actual_addr = found_addr;
    Serial.printf("[BMI270] Target BMI270 confirmed at 0x%02X. Initializing...\n", bmi270_actual_addr);
    
    // 1. 软件复位 (CMD = 0xB6)
    writeI2CReg(bmi270_actual_addr, 0x7E, 0xB6);
    delay(25);
    
    // 2. 禁用上电省电模式 (PWR_CONF = 0x00)
    writeI2CReg(bmi270_actual_addr, 0x7C, 0x00);
    delay(2);
    
    // 3. 上传微码配置
    bool upload_ok = uploadBMI270Config(bmi270_actual_addr);
    if (!upload_ok) {
        Serial.println("[BMI270] Warning: Config upload non-optimal, continuing bring-up...");
    }
    
    // 4. 电源门控: PWR_CONF=0x00, PWR_CTRL=0x0E (使能加速度计、陀螺仪与温度传感)
    writeI2CReg(bmi270_actual_addr, 0x7C, 0x00);
    delay(5);
    writeI2CReg(bmi270_actual_addr, 0x7D, 0x0E); // temp_en | acc_en | gyr_en
    delay(10);
    
    // 5. 传感器采样参数配置 (100Hz ODR, +/-8g 量程)
    writeI2CReg(bmi270_actual_addr, 0x40, 0xA8); // ACC_CONF: 100Hz ODR, normal filter, perf mode
    writeI2CReg(bmi270_actual_addr, 0x41, 0x02); // ACC_RANGE: +/-8g
    writeI2CReg(bmi270_actual_addr, 0x42, 0xA9); // GYR_CONF: 100Hz ODR, normal filter, perf mode
    writeI2CReg(bmi270_actual_addr, 0x43, 0x00); // GYR_RANGE: +/-2000 dps
    delay(20);
    
    Serial.println("[BMI270] Bring-up COMPLETE! Accelerometer stream ONLINE.");
    bmi270_online = true;
    return true;
}

// 读取当前 3 轴加速度并解算俯仰/横滚角
void readBMI270(float& roll, float& pitch) {
    if (!bmi270_online) return;

    sticks3::I2CLockGuard guard(25);
    if (!guard.isAcquired()) return;
    
    Wire1.beginTransmission(bmi270_actual_addr);
    Wire1.write(0x0C); // ACC_X_LSB
    if (Wire1.endTransmission(false) == 0) {
        if (Wire1.requestFrom(bmi270_actual_addr, (uint8_t)6) == 6) {
            int16_t x = (int16_t)(Wire1.read() | (Wire1.read() << 8));
            int16_t y = (int16_t)(Wire1.read() | (Wire1.read() << 8));
            int16_t z = (int16_t)(Wire1.read() | (Wire1.read() << 8));
            
            // 8g 量程对应 4096 LSB/g
            imu_ax = x * (8.0f / 32768.0f);
            imu_ay = y * (8.0f / 32768.0f);
            imu_az = z * (8.0f / 32768.0f);
            
            // 姿态角解算
            roll = std::atan2(imu_ay, imu_az) * 180.0f / 3.14159265f;
            pitch = std::atan2(-imu_ax, std::sqrt(imu_ay * imu_ay + imu_az * imu_az)) * 180.0f / 3.14159265f;
        }
    }
}

void setup() {
    // 提升主循环 loopTask 优先级至 4 (高于 audioTask 3 与 websocket_task 1，确保控制流指令与打断必定优先执行，彻底杜绝互斥锁垄断与饥饿)
    vTaskPrioritySet(NULL, 4);

    Serial.begin(115200);
    delay(200);
    Serial.println("\n=======================================================");
    Serial.println(">>> [StickS3-BOOT] Starting Hardware Bring-Up (loopTask Prio: 4)...");
    Serial.println("=======================================================");

    // 1. 初始化按键引脚
    pinMode(PIN_BTN_A, INPUT_PULLUP);
    pinMode(PIN_BTN_B, INPUT_PULLUP);
    Serial.println("[BOOT] Buttons G11/G12 initialized.");

    // 2. 激活 M5PM1 硬件供电 (开启 LCD L3B 供电轨)
    bool pm1_ok = initM5PM1();
    Serial.printf("[BOOT] PMIC Init: %s\n", pm1_ok ? "OK" : "BYPASSED");

    // 2.1 扫描 Wire1 I2C 总线并初始化 BMI270 姿态传感器
    scanI2CBus();
    bool imu_ok = initBMI270();
    Serial.printf("[BOOT] IMU Init: %s\n", imu_ok ? "ONLINE" : "FAILED");

    // 3. 硬件复位 ST7789 LCD
    pinMode(21, OUTPUT);
    digitalWrite(21, LOW);
    delay(20);
    digitalWrite(21, HIGH);
    delay(50);
    Serial.println("[BOOT] LCD HW Reset toggled (G21).");

    // 4. 初始化 ST7789 显示屏与背光
    Serial.println("[BOOT] Initializing ST7789 Display via SPI3...");
    display.init();
    display.setRotation(0); // 竖屏 135x240
    display.setBrightness(200); // 高亮模式 (200/255)
    Serial.printf("[BOOT] Display initialized: %d x %d\n", display.width(), display.height());

    // 5. 绘制启动 7 色彩虹校色条 (验证屏幕物理点亮与中文字库自检)
    Serial.println("[BOOT] Drawing Rainbow Test Strip & Chinese Font Test...");
    display.startWrite();
    display.fillScreen(TFT_BLACK);
    uint16_t test_colors[] = {TFT_RED, TFT_GREEN, TFT_BLUE, TFT_YELLOW, TFT_CYAN, TFT_MAGENTA, TFT_WHITE};
    int band_h = 12;
    for (int i = 0; i < 7; ++i) {
        display.fillRect(0, i * band_h, SCREEN_W, band_h, test_colors[i]);
    }
    display.setTextColor(TFT_WHITE, TFT_BLACK);
    display.setTextDatum(MC_DATUM);
    display.drawString("M5StickS3", SCREEN_W / 2, 105);
    display.drawString("灵方终端 就绪", SCREEN_W / 2, 125, &fonts::efontCN_14);
    display.endWrite();
    delay(500);

    // 6. 初始化 BLE Nordic UART Service (严格遵循 31 字节限制，确保 iPhone CoreBluetooth 瞬间发现)
    Serial.println("[BOOT] Initializing BLE Nordic UART Service...");
    BLEDevice::init("StickS3-Buddy");
    BLEDevice::setMTU(517); // 开启大包传输协商，防止 20 字节分包切断 UTF-8 汉字

    // 提高蓝牙发射功率至最大 (+9dBm)，大幅增强手机搜寻距离与灵敏度
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, ESP_PWR_LVL_P9);
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_DEFAULT, ESP_PWR_LVL_P9);

    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());

    BLEService* pService = pServer->createService(SERVICE_UUID);
    pTxCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID_TX,
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pTxCharacteristic->addDescriptor(new BLE2902());

    BLECharacteristic* pRxCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID_RX,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    pRxCharacteristic->setCallbacks(new RxCallbacks());

    pService->start();

    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();

    // 主广播包 (30 字节 <= 31 字节物理上限)：
    // Flags (3B) + 128位 Nordic UART Service UUID (18B) + 完整名称 "StickS3" (9B) = 30 字节！
    // iOS 系统微信小程序无论是根据服务过滤还是扫描设备名称均可一次性命中！
    BLEAdvertisementData advData;
    advData.setFlags(0x06); // General Discoverable, BR/EDR Not Supported
    advData.setCompleteServices(BLEUUID(SERVICE_UUID));
    advData.setName("StickS3");
    pAdvertising->setAdvertisementData(advData);

    // 扫描响应包 (15 字节 <= 31 字节物理上限)：
    // 包含扩展全称 "StickS3-Buddy"
    BLEAdvertisementData scanRespData;
    scanRespData.setName("StickS3-Buddy");
    pAdvertising->setScanResponseData(scanRespData);

    pAdvertising->setScanResponse(true);
    pAdvertising->setMinInterval(0x20); // 20ms - 40ms 高频广播
    pAdvertising->setMaxInterval(0x40);
    pAdvertising->setMinPreferred(0x06);
    BLEDevice::startAdvertising();

    Serial.printf("[BOOT] BLE Online! Name: StickS3 (Buddy) | UUID: %s | MAC: %s\n",
                  SERVICE_UUID, BLEDevice::getAddress().toString().c_str());

    // 6.5 初始化全双工对话记忆与持久化存储子系统 (Flash NVS + PSRAM)
    sticks3::StickS3MemoryStore::getInstance().begin();

    // 7. 初始化 2.4GHz Wi-Fi (SoftAP + TCP 8080 + UDP 8080 + WebPortal 80 + 环境 AP 嗅探)
    sticks3::StickS3WiFi::getInstance().setMessageCallback([](const String& msg, const String& source) {
        onNewTextMessage(msg, source);
    });
    sticks3::StickS3WiFi::getInstance().begin();

    // 8. 初始化 ES8311 音频子系统 (I2S0 全双工 + AW8737 功放 + MEMS 硅麦)
    bool audio_ok = sticks3::StickS3Audio::getInstance().begin(&Wire1);
    Serial.printf("[BOOT] Audio Subsystem: %s\n", audio_ok ? "ONLINE" : "FAILED");

    // 8.5 初始化离线语音唤醒词「悄悄」引擎
    sticks3::StickS3WakeWordEngine::getInstance().begin();
    auto& cfg = sticks3::StickS3ConfigManager::getInstance().getConfig();
    sticks3::StickS3WakeWordEngine::getInstance().setEnabled(cfg.wakeword_enabled);
    sticks3::StickS3WakeWordEngine::getInstance().setSensitivity(cfg.wakeword_sensitivity);
    sticks3::StickS3WakeWordEngine::getInstance().setWakeCallback([](float conf, uint32_t dur_ms) {
        sticks3::StickS3BailianClient::getInstance().onWakeWordDetected(conf, dur_ms);
    });

    // 播放开机上扬和弦音
    if (audio_ok) {
        sticks3::StickS3Audio::getInstance().playChime(sticks3::CHIME_STARTUP);
    }

    Serial.println("[BOOT] StickS3 Ready! Bringing up Dual-Mode Dashboard.");
}

void loop() {
    frame_count++;

    // 0.0 处理 BLE 异步接收包 (支持多包拼帧与半包重组，在主线程安全触发音频与汉字渲染)
    if (ble_rx_pending && (millis() - last_ble_rx_tick >= 45 || (!ble_accum_bytes.empty() && ble_accum_bytes.back() == '\n'))) {
        std::vector<uint8_t> raw_copy;
        portENTER_CRITICAL(&ble_mux);
        raw_copy = ble_accum_bytes;
        ble_accum_bytes.clear();
        ble_rx_pending = false;
        portEXIT_CRITICAL(&ble_mux);

        if (!raw_copy.empty()) {
            String full_msg = sanitizeAndConvertToUtf8(raw_copy.data(), raw_copy.size());
            full_msg.trim();
            if (full_msg.length() > 0) {
                onNewTextMessage(full_msg, "BLE-NUS");
            }
        }
    }

    // 0. 系统全维度性能与健康度指标更新 (CPU Loop FPS, 内存与I/O监控)
    sticks3::updateSystemLoopFPS();
    sticks3::printSystemDiagnostics();

    // 0.1 更新 Wi-Fi 遥测、后台扫描与多通道网络服务
    sticks3::StickS3WiFi::getInstance().updateTelemetry(imu_roll, imu_pitch);
    sticks3::StickS3WiFi::getInstance().update();
    sticks3::StickS3Audio::getInstance().update();
    uint8_t mic_rms = sticks3::StickS3Audio::getInstance().readMicRMS();

    // 1. 扫描按键事件 (Btn A: G11, Btn B: G12)
    bool curA = digitalRead(PIN_BTN_A);
    bool curB = digitalRead(PIN_BTN_B);
    btnA_clicked = (btnA_prev == HIGH && curA == LOW);
    btnB_clicked = (btnB_prev == HIGH && curB == LOW);
    btnA_prev = curA;
    btnB_prev = curB;

    // 2. 串口输入行缓冲 (支持下发汉字直接显示上屏，支持 UTF-8 / GBK / Hex 自动识别)
    static std::vector<uint8_t> serial_rx_bytes;
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\r') continue;
        if (c == '\n') {
            if (!serial_rx_bytes.empty()) {
                String cmd_or_msg = sanitizeAndConvertToUtf8(serial_rx_bytes.data(), serial_rx_bytes.size());
                cmd_or_msg.trim();
                if (cmd_or_msg.length() > 0) {
                    if (cmd_or_msg == "?" || cmd_or_msg == "p" || cmd_or_msg == "P") {
                        Serial.printf("{\"type\":\"pong\",\"device\":\"M5StickS3\",\"status\":\"online\",\"tick\":%lu}\n", (unsigned long)frame_count);
                    } else if (cmd_or_msg == "b" || cmd_or_msg == "B") {
                        sticks3::StickS3Audio::getInstance().playTone(1200, 100, 0.5f);
                        Serial.println("{\"type\":\"beep_ack\",\"status\":\"ok\"}");
                    } else if (cmd_or_msg == "r" || cmd_or_msg == "R") {
                        auto& audio = sticks3::StickS3Audio::getInstance();
                        if (audio.isRecording()) {
                            audio.stopRecording();
                            Serial.printf("{\"type\":\"record_ack\",\"status\":\"stopped\",\"audio_id\":%u,\"bytes\":%u}\n",
                                          (unsigned)audio.getDeviceAudioId(), (unsigned)audio.getWavSize());
                        } else {
                            audio.startRecording(10000);
                            Serial.println("{\"type\":\"record_ack\",\"status\":\"started\"}");
                        }
                    } else if (cmd_or_msg == "a" || cmd_or_msg == "A") {
                        auto& audio = sticks3::StickS3Audio::getInstance();
                        Serial.printf("{\"type\":\"audio_status\",\"is_recording\":%s,\"rec_ms\":%u,\"has_audio\":%s,\"audio_id\":%u,\"wav_bytes\":%u}\n",
                                      audio.isRecording() ? "true" : "false",
                                      (unsigned)audio.getRecordDurationMs(),
                                      audio.hasDeviceAudio() ? "true" : "false",
                                      (unsigned)audio.getDeviceAudioId(),
                                      (unsigned)audio.getWavSize());
                    } else if (cmd_or_msg == "w" || cmd_or_msg == "W") {
                        sticks3::StickS3WiFi::getInstance().triggerScan();
                        Serial.println(sticks3::StickS3WiFi::getInstance().getScanResultsJSON().c_str());
                    } else if (cmd_or_msg == "m" || cmd_or_msg == "M") {
                        Serial.printf("{\"type\":\"mic_level\",\"rms_percent\":%d}\n", mic_rms);
                    } else if (cmd_or_msg == "btn_a" || cmd_or_msg == "BTN_A") {
                        btnA_clicked = true;
                        Serial.println("{\"type\":\"btn_sim\",\"button\":\"A\"}");
                    } else if (cmd_or_msg == "btn_b" || cmd_or_msg == "BTN_B") {
                        btnB_clicked = true;
                        Serial.println("{\"type\":\"btn_sim\",\"button\":\"B\"}");
                    } else if (cmd_or_msg == "i" || cmd_or_msg == "I") {
                        sticks3::StickS3BailianClient::getInstance().interrupt("Serial-I-Key");
                        Serial.println("{\"type\":\"interrupt_ack\",\"status\":\"ok\"}");
                    } else if (cmd_or_msg == "k" || cmd_or_msg == "K" || cmd_or_msg == "wake") {
                        sticks3::StickS3WakeWordEngine::getInstance().forceTrigger(98.0f);
                        sticks3::StickS3BailianClient::getInstance().onWakeWordDetected(98.0f, 650);
                        Serial.println("{\"type\":\"wakeword_sim\",\"word\":\"悄悄\",\"status\":\"triggered\"}");
                    } else if (cmd_or_msg.startsWith("q:") || cmd_or_msg.startsWith("Q:") ||
                               cmd_or_msg.startsWith("chat:") || cmd_or_msg.startsWith("CHAT:")) {
                        int colon_idx = cmd_or_msg.indexOf(':');
                        String query_text = cmd_or_msg.substring(colon_idx + 1);
                        query_text.trim();
                        if (query_text.length() > 0) {
                            sticks3::StickS3BailianClient::getInstance().sendTextMessage(query_text);
                        }
                    } else {
                        // 接收串口任意测试文本（支持 UTF-8 和 GBK 中文！）并显示上屏
                        onNewTextMessage(cmd_or_msg, "Serial");
                    }
                }
                serial_rx_bytes.clear();
            }
        } else {
            serial_rx_bytes.push_back((uint8_t)c);
        }
        protocol_engine.feedBytes(&c, 1);
    }

    // 3. 采集姿态数据 (BMI270)
    readBMI270(imu_roll, imu_pitch);

    // 4. 按键处理与页面模式
    if (protocol_engine.hasPendingPermission()) {
        const auto& perm = protocol_engine.getPendingPermission();

        if (btnA_clicked) {
            std::string resp = BuddyProtocolEngine::serializeAction(perm.id, true);
            sendToHost(resp);
            protocol_engine.clearPendingPermission();
        } else if (btnB_clicked) {
            std::string resp = BuddyProtocolEngine::serializeAction(perm.id, false);
            sendToHost(resp);
            protocol_engine.clearPendingPermission();
        }

        // 渲染审批警报页面 (红黄高亮)
        display.startWrite();
        display.fillScreen(TFT_MAROON);
        display.fillRect(0, 0, SCREEN_W, 26, TFT_RED);
        display.setTextColor(TFT_WHITE, TFT_RED);
        display.setTextDatum(MC_DATUM);
        display.drawString("! APPROVAL !", SCREEN_W / 2, 13);

        display.setTextColor(TFT_YELLOW, TFT_MAROON);
        display.setTextDatum(ML_DATUM);
        display.drawString("Tool: " + String(perm.tool.c_str()), 6, 38);

        display.setTextColor(TFT_WHITE, TFT_MAROON);
        display.drawString("Cmd: " + String(perm.command.c_str()), 6, 58);

        display.fillRect(0, 185, SCREEN_W, 55, TFT_BLACK);
        display.setTextColor(TFT_GREEN, TFT_BLACK);
        display.drawString("[A] Approve", 10, 198);
        display.setTextColor(TFT_RED, TFT_BLACK);
        display.drawString("[B] Deny", 10, 220);
        display.endWrite();
    } else {
        auto& bl = sticks3::StickS3BailianClient::getInstance();
        auto& audio = sticks3::StickS3Audio::getInstance();

        bool is_ai_busy = (bl.getState() == sticks3::BL_STATE_SPEAKING || 
                           bl.getState() == sticks3::BL_STATE_THINKING || 
                           audio.isPlaying());

        // 核心打断拦截：大模型说话、大模型思考或音频流播放中，按下【正面按键 A】或【侧面按键 B】均可毫秒级物理打断！
        if (is_ai_busy && (btnA_clicked || btnB_clicked)) {
            const char* btn_src = btnA_clicked ? "Physical-Btn-A(Front)" : "Physical-Btn-B(Side)";
            bl.interrupt(btn_src);
            audio.playTone(2200, 20, 0.45f);
            Serial.printf("[PHYSICAL-INTERRUPT] Successfully triggered by %s!\n", btn_src);
        } else if (btnA_clicked) {
            // 按键 A: 空闲时发起新会话 / 未连云端时触发 10s 本地录音控制
            if (bl.isConnected()) {
                bl.startNewConversation();
                audio.playTone(1600, 30, 0.40f);
                Serial.println("[EVENT] Btn A clicked -> Started new conversation");
            } else {
                if (audio.isRecording()) {
                    audio.stopRecording();
                    audio.playChime(sticks3::CHIME_SUCCESS);
                    Serial.printf("[AUDIO-EVENT] Btn A clicked -> Stopped recording. Total %u ms, WAV ID #%u\n",
                                  (unsigned)audio.getRecordDurationMs(), (unsigned)audio.getDeviceAudioId());
                } else {
                    audio.startRecording(10000);
                    audio.playTone(1800, 40, 0.45f);
                    Serial.println("[AUDIO-EVENT] Btn A clicked -> Started 10s recording");
                }
            }
        } else if (btnB_clicked) {
            // 按键 B: 空闲时切换 Grove 5V 或触发 Wi-Fi 深度扫描
            ext_5v_enabled = !ext_5v_enabled;
            audio.playTone(1500, 25, 0.40f);
            sticks3::StickS3WiFi::getInstance().triggerScan();
            Serial.printf("[EVENT] Btn B clicked -> Grove 5V: %s | WiFi Scan Triggered\n", ext_5v_enabled ? "ON" : "OFF");
        }

        // 自动连接百炼 WebSocket
        auto& bl_client = sticks3::StickS3BailianClient::getInstance();
        auto& cfg_mgr = sticks3::StickS3ConfigManager::getInstance();
        if (cfg_mgr.isStaConnected() && cfg_mgr.hasBailianKey() && bl_client.getState() == sticks3::BL_STATE_DISCONNECTED) {
            static uint32_t last_bl_try = 0;
            if (millis() - last_bl_try > 8000) {
                last_bl_try = millis();
                Serial.println("[AUTO-CONNECT] STA Online & Key present -> Connecting to Bailian...");
                bl_client.connect();
            }
        }

        // 刷新渲染双模仪表盘 (最高 15 FPS / 66ms，为后台 FreeRTOS 音频与网络任务释放 CPU)
        static uint32_t last_display_draw = 0;
        if (millis() - last_display_draw >= 66) {
            last_display_draw = millis();
            display.startWrite();

        // 1. 顶部标题栏 (0 ~ 24)
        display.fillRect(0, 0, SCREEN_W, 24, theme_color);
        display.setTextColor(TFT_WHITE, theme_color);
        display.setTextDatum(MC_DATUM);
        if (cfg_mgr.isStaConnected()) {
            display.drawString("StickS3 | " + cfg_mgr.getStaIP(), SCREEN_W / 2, 12);
        } else {
            display.drawString("M5StickS3 Buddy", SCREEN_W / 2, 12);
        }

        // 2. 信息卡片区 (26 ~ 68)
        display.fillRect(0, 26, SCREEN_W, 42, TFT_DARKGREY);
        display.setTextColor(TFT_YELLOW, TFT_DARKGREY);
        display.setTextDatum(ML_DATUM);

        char buf[40];
        snprintf(buf, sizeof(buf), "Vbat: %.2fV", battery_voltage);
        display.drawString(buf, 4, 35);

        // 显示百炼大模型状态
        String bl_str = "BL: " + bl_client.getStateName();
        uint16_t bl_color = TFT_LIGHTGREY;
        if (bl_client.getState() == sticks3::BL_STATE_SPEAKING) bl_color = TFT_GREEN;
        else if (bl_client.getState() == sticks3::BL_STATE_LISTENING) bl_color = TFT_CYAN;
        else if (bl_client.getState() == sticks3::BL_STATE_THINKING) bl_color = TFT_YELLOW;
        else if (bl_client.getState() == sticks3::BL_STATE_INTERRUPTED) bl_color = TFT_RED;
        else if (bl_client.isConnected()) bl_color = TFT_GREENYELLOW;
        display.setTextColor(bl_color, TFT_DARKGREY);
        display.drawString(bl_str.substring(0, 10), 66, 35);

        // 显示 Wi-Fi 状态
        if (cfg_mgr.isStaConnected()) {
            snprintf(buf, sizeof(buf), "STA: %ddBm", cfg_mgr.getStaRSSI());
            display.setTextColor(TFT_GREENYELLOW, TFT_DARKGREY);
        } else if (cfg_mgr.getStaState() == sticks3::STA_STATE_CONNECTING) {
            snprintf(buf, sizeof(buf), "STA: Conn...");
            display.setTextColor(TFT_YELLOW, TFT_DARKGREY);
        } else {
            int wf_cnt = sticks3::StickS3WiFi::getInstance().getNetworkCount();
            snprintf(buf, sizeof(buf), "WiFi: %d AP", wf_cnt);
            display.setTextColor(TFT_LIGHTGREY, TFT_DARKGREY);
        }
        display.drawString(buf, 4, 53);

        snprintf(buf, sizeof(buf), "W:%lu I:%lu",
                 (unsigned long)sticks3::StickS3WakeWordEngine::getInstance().getTotalWakeCount(),
                 (unsigned long)bl_client.getTotalInterrupts());
        display.setTextColor(TFT_WHITE, TFT_DARKGREY);
        display.drawString(buf, 66, 53);

        // 3. 手机蓝牙/WiFi多通道消息与大模型语音交互展示区 (70 ~ 138)
        auto& audio_inst = sticks3::StickS3Audio::getInstance();
        bool is_recording = audio_inst.isRecording();
        bool is_playing_stream = audio_inst.isPlayingStream();

        // 优先级 1: 百炼大模型交互状态 (已就绪、正在聆听、思考或播报中)
        if (bl_client.getState() != sticks3::BL_STATE_DISCONNECTED && bl_client.getState() != sticks3::BL_STATE_CONNECTING) {
            uint16_t hdr_bg = 0x0284;
            String hdr_txt = "● 正在聆听中 (请讲话)";
            if (bl_client.getState() == sticks3::BL_STATE_SPEAKING) {
                hdr_bg = TFT_DARKGREEN;
                hdr_txt = "▶ AI回复中 [按A打断]";
            } else if (bl_client.getState() == sticks3::BL_STATE_THINKING) {
                hdr_bg = 0xD4A0; // Amber
                hdr_txt = "⚡ 思考推理中...";
            } else if (bl_client.getState() == sticks3::BL_STATE_INTERRUPTED) {
                hdr_bg = TFT_RED;
                hdr_txt = "⏹ 已中途打断!";
            } else if (bl_client.getState() == sticks3::BL_STATE_CONNECTED_IDLE) {
                hdr_bg = TFT_NAVY;
                hdr_txt = "✔ 百炼就绪 说“悄悄”";
            } else if (bl_client.getState() == sticks3::BL_STATE_ERROR) {
                hdr_bg = TFT_RED;
                hdr_txt = "✖ 连接异常 重连中";
            } else if (bl_client.getState() == sticks3::BL_STATE_LISTENING) {
                auto& cfg_ww = sticks3::StickS3ConfigManager::getInstance().getConfig();
                if (cfg_ww.wakeword_enabled) {
                    if (bl_client.isWakeWindowOpen()) {
                        hdr_bg = 0xD980; // Amber-gold
                        hdr_txt = "⚡ [悄悄已唤醒] 聆听中";
                    } else {
                        hdr_bg = 0x0284;
                        hdr_txt = "● 待命中 (说“悄悄”)";
                    }
                } else {
                    hdr_bg = 0x0284;
                    hdr_txt = "● 正在聆听中 (请讲话)";
                }
            }

            display.fillRect(0, 70, SCREEN_W, 16, hdr_bg);
            display.setTextColor(TFT_WHITE, hdr_bg);
            display.setTextDatum(MC_DATUM);
            display.drawString(hdr_txt, SCREEN_W / 2, 78);

            display.fillRect(0, 86, SCREEN_W, 52, TFT_BLACK);
            display.drawRect(0, 86, SCREEN_W, 52, hdr_bg);

            // 实时流式渲染大模型问答汉字
            if (bl_client.getState() == sticks3::BL_STATE_ERROR) {
                String err_str = "异常: " + bl_client.getLastError();
                drawChineseText(display, err_str, 6, 90, SCREEN_W - 12, 14, TFT_RED, TFT_BLACK, &fonts::efontCN_12);
            } else if (bl_client.getAiReply().length() > 0) {
                String reply_str = "AI: " + bl_client.getAiReply();
                drawChineseText(display, reply_str, 6, 90, SCREEN_W - 12, 14, TFT_YELLOW, TFT_BLACK, &fonts::efontCN_12);
            } else if (bl_client.getUserQuery().length() > 0) {
                String query_str = "你: " + bl_client.getUserQuery();
                drawChineseText(display, query_str, 6, 90, SCREEN_W - 12, 14, TFT_CYAN, TFT_BLACK, &fonts::efontCN_12);
            } else {
                auto& cfg_ww = sticks3::StickS3ConfigManager::getInstance().getConfig();
                if (cfg_ww.wakeword_enabled && !bl_client.isWakeWindowOpen()) {
                    drawChineseText(display, "呼唤【悄悄】唤醒\n随时打断与流式问答\n离线声学匹配引擎", 6, 90, SCREEN_W - 12, 14, TFT_LIGHTGREY, TFT_BLACK, &fonts::efontCN_12);
                } else {
                    drawChineseText(display, "对准硅麦讲话\n支持全双工交互\n随时开口即可打断", 6, 90, SCREEN_W - 12, 14, TFT_LIGHTGREY, TFT_BLACK, &fonts::efontCN_12);
                }
            }
        } else if (is_recording) {
            // 录音状态专用高亮卡片 (红底 + 倒计时 + 能量动态)
            display.fillRect(0, 70, SCREEN_W, 16, TFT_RED);
            display.setTextColor(TFT_WHITE, TFT_RED);
            display.setTextDatum(MC_DATUM);
            display.drawString("● 正在录音 (REC)", SCREEN_W / 2, 78);

            display.fillRect(0, 86, SCREEN_W, 52, TFT_BLACK);
            display.drawRect(0, 86, SCREEN_W, 52, TFT_RED);

            char rec_str[32];
            snprintf(rec_str, sizeof(rec_str), "%.1fs / 10.0s", (float)audio_inst.getRecordDurationMs() / 1000.0f);
            display.setTextColor(TFT_YELLOW, TFT_BLACK);
            display.setTextDatum(MC_DATUM);
            display.drawString(rec_str, SCREEN_W / 2, 98);

            drawChineseText(display, "对准硅麦讲话\n按[A]键提前保存", 6, 110, SCREEN_W - 12, 14, TFT_WHITE, TFT_BLACK, &fonts::efontCN_12);
        } else if (is_playing_stream) {
            // 播放网页下发音频专用卡片 (青蓝底)
            display.fillRect(0, 70, SCREEN_W, 16, 0x0320);
            display.setTextColor(TFT_WHITE, 0x0320);
            display.setTextDatum(MC_DATUM);
            display.drawString("▶ 正在播放网页音频", SCREEN_W / 2, 78);

            display.fillRect(0, 86, SCREEN_W, 52, TFT_BLACK);
            display.drawRect(0, 86, SCREEN_W, 52, TFT_CYAN);

            int p_fill = static_cast<int>(audio_inst.getPlaybackProgress() * (SCREEN_W - 20));
            if (p_fill < 0) p_fill = 0;
            if (p_fill > SCREEN_W - 20) p_fill = SCREEN_W - 20;
            display.drawRect(10, 96, SCREEN_W - 20, 8, TFT_DARKGREY);
            if (p_fill > 0) display.fillRect(10, 96, p_fill, 8, TFT_CYAN);

            drawChineseText(display, "AW8737 功放输出\n高保真回放中...", 6, 110, SCREEN_W - 12, 14, TFT_CYAN, TFT_BLACK, &fonts::efontCN_12);
        } else {
            bool is_recent = (millis() - last_ble_msg_time < 8000) && (total_ble_msgs_received > 0);
            uint16_t card_border = is_recent ? TFT_YELLOW : (device_connected ? TFT_CYAN : (sticks3::StickS3WiFi::getInstance().getConnectedStations() > 0 ? TFT_GREENYELLOW : TFT_DARKGREY));

            display.fillRect(0, 70, SCREEN_W, 16, is_recent ? TFT_YELLOW : (device_connected ? TFT_NAVY : (sticks3::StickS3WiFi::getInstance().getConnectedStations() > 0 ? 0x0320 : TFT_BLACK)));
            display.setTextColor(is_recent ? TFT_BLACK : TFT_CYAN, is_recent ? TFT_YELLOW : (device_connected ? TFT_NAVY : (sticks3::StickS3WiFi::getInstance().getConnectedStations() > 0 ? 0x0320 : TFT_BLACK)));
            display.setTextDatum(MC_DATUM);
            if (total_ble_msgs_received > 0) {
                snprintf(buf, sizeof(buf), is_recent ? "* 新消息 (#%lu) *" : "消息回显 (#%lu):", (unsigned long)total_ble_msgs_received);
                display.drawString(buf, SCREEN_W / 2, 78);
            } else if (device_connected) {
                display.drawString("BLE 已就绪", SCREEN_W / 2, 78);
            } else if (sticks3::StickS3WiFi::getInstance().getConnectedStations() > 0) {
                display.drawString("WiFi 已连接", SCREEN_W / 2, 78);
            } else {
                display.drawString("等待手机连接...", SCREEN_W / 2, 78);
            }

            display.fillRect(0, 86, SCREEN_W, 52, TFT_BLACK);
            display.drawRect(0, 86, SCREEN_W, 52, card_border);

            if (total_ble_msgs_received > 0 && latest_ble_msg.length() > 0) {
                drawChineseText(display, latest_ble_msg, 6, 90, SCREEN_W - 12, 14, is_recent ? TFT_YELLOW : TFT_WHITE, TFT_BLACK, &fonts::efontCN_12);
            } else if (audio_inst.hasDeviceAudio()) {
                char dev_aud_str[64];
                snprintf(dev_aud_str, sizeof(dev_aud_str), "已录音 #%u (%.1fs)\n网页端可直接播放\nIP: 192.168.4.1",
                         (unsigned)audio_inst.getDeviceAudioId(), (float)audio_inst.getRecordDurationMs() / 1000.0f);
                drawChineseText(display, dev_aud_str, 6, 90, SCREEN_W - 12, 14, TFT_GREEN, TFT_BLACK, &fonts::efontCN_12);
            } else if (device_connected) {
                drawChineseText(display, "BLE 已连接!\n在手机小程序中\n发送任意汉字", 6, 90, SCREEN_W - 12, 14, TFT_GREEN, TFT_BLACK, &fonts::efontCN_12);
            } else if (sticks3::StickS3WiFi::getInstance().getConnectedStations() > 0) {
                drawChineseText(display, "手机已连热点!\n小程序/网页发汉字\nIP: 192.168.4.1", 6, 90, SCREEN_W - 12, 14, TFT_GREENYELLOW, TFT_BLACK, &fonts::efontCN_12);
            } else {
                drawChineseText(display, "WiFi: StickS3-Buddy\n网页配网/百炼\nIP: 192.168.4.1", 6, 90, SCREEN_W - 12, 14, TFT_LIGHTGREY, TFT_BLACK, &fonts::efontCN_12);
            }
        }
        display.setFont(nullptr);

        // 4. 中下部：IMU 动态姿态水准仪 (140 ~ 194)
        display.fillRect(0, 140, SCREEN_W, 54, TFT_BLACK);
        display.drawRect(2, 140, SCREEN_W - 4, 54, TFT_DARKGREY);
        display.drawLine(SCREEN_W / 2, 142, SCREEN_W / 2, 192, 0x18C3); // 浅灰十字交叉线
        display.drawLine(4, 166, SCREEN_W - 4, 166, 0x18C3);

        // 水准球映射 (Y基准 166)
        int ball_x = SCREEN_W / 2 + static_cast<int>(imu_roll * 1.0f);
        int ball_y = 166 + static_cast<int>(imu_pitch * 0.7f);
        if (ball_x < 8) ball_x = 8;
        if (ball_x > SCREEN_W - 8) ball_x = SCREEN_W - 8;
        if (ball_y < 146) ball_y = 146;
        if (ball_y > 186) ball_y = 186;

        display.fillCircle(ball_x, ball_y, 5, TFT_RED);
        display.drawCircle(ball_x, ball_y, 5, TFT_WHITE);

        // 实时姿态角数值
        char ang_buf[32];
        snprintf(ang_buf, sizeof(ang_buf), "R:%+.0f P:%+.0f", imu_roll, imu_pitch);
        display.setTextColor(TFT_YELLOW, TFT_BLACK);
        display.setTextDatum(MR_DATUM);
        display.drawString(ang_buf, SCREEN_W - 6, 186);

        // 5. 底部按键指引与麦克风实时 VU Meter (196 ~ 240)
        display.fillRect(0, 196, SCREEN_W, 20, TFT_NAVY);
        display.setTextColor(TFT_WHITE, TFT_NAVY);
        display.setTextDatum(MC_DATUM);
        if (bl_client.getState() == sticks3::BL_STATE_SPEAKING) {
            display.drawString("[A] 立即打断  [B] 5V/扫描", SCREEN_W / 2, 206);
        } else if (bl_client.isConnected()) {
            display.drawString("[A] 新问答  [B] 5V/扫描", SCREEN_W / 2, 206);
        } else if (audio_inst.isRecording()) {
            display.drawString("[A] 停止保存  [B] 5V/WiFi", SCREEN_W / 2, 206);
        } else {
            display.drawString("[A] 问答/录音  [B] 5V/WiFi", SCREEN_W / 2, 206);
        }

        // 动态麦克风音量能量条 (218 ~ 238)
        display.fillRect(0, 218, SCREEN_W, 22, TFT_BLACK);
        display.setTextColor(TFT_CYAN, TFT_BLACK);
        display.setTextDatum(ML_DATUM);
        display.drawString("MIC", 4, 228);

        // 动态音量柱外框与动态填充
        display.drawRect(26, 223, 72, 11, TFT_DARKGREY);
        int bar_fill = (mic_rms * 68) / 100;
        if (bar_fill > 68) bar_fill = 68;
        uint16_t vu_color = TFT_GREEN;
        if (mic_rms > 70) vu_color = TFT_RED;
        else if (mic_rms > 40) vu_color = TFT_YELLOW;

        if (bar_fill > 0) {
            display.fillRect(28, 225, bar_fill, 7, vu_color);
        }
        if (bar_fill < 68) {
            display.fillRect(28 + bar_fill, 225, 68 - bar_fill, 7, TFT_BLACK);
        }

        snprintf(buf, sizeof(buf), "%2d%%", mic_rms);
        display.setTextColor(vu_color, TFT_BLACK);
        display.setTextDatum(MR_DATUM);
        display.drawString(buf, SCREEN_W - 4, 228);

        display.endWrite();
        }
    }

    // 动画定时器 (每 600ms 切帧)
    if (millis() - last_anim_tick > 600) {
        last_anim_tick = millis();
        anim_frame++;
    }

    // 周期性向上位机输出硬件遥测流 (每 1000ms 输出一次)
    if (millis() - last_serial_telem > 1000) {
        last_serial_telem = millis();
        Serial.printf("[StickS3-ONLINE] Tick=%lu | Vbat=%.2fV | BLE=%s | WiFi=%d APs (\"%s\",%ddBm) | MicRMS=%d%% | Roll=%+.1f Pitch=%+.1f | Acc=(%+.2f,%+.2f,%+.2f)g | BtnA=%d BtnB=%d\n",
                      (unsigned long)frame_count, battery_voltage,
                      device_connected ? "CONNECTED" : "WAITING",
                      sticks3::StickS3WiFi::getInstance().getNetworkCount(),
                      sticks3::StickS3WiFi::getInstance().getTopSSID().c_str(),
                      sticks3::StickS3WiFi::getInstance().getTopRSSI(),
                      mic_rms,
                      imu_roll, imu_pitch,
                      imu_ax, imu_ay, imu_az,
                      digitalRead(PIN_BTN_A), digitalRead(PIN_BTN_B));
    }

    // BLE 掉线重连
    if (!device_connected && old_device_connected) {
        delay(500);
        pServer->startAdvertising();
        old_device_connected = device_connected;
    }
    if (device_connected && !old_device_connected) {
        old_device_connected = device_connected;
    }

    delay(5);
}
