/**
 * @file m5sticks3_servo_tool.ino
 * @brief M5StickS3 专用飞特 (Feetech) STS3215 舵机在线编址、零位标定与电压巡检工具
 * 
 * 硬件连接:
 *   - M5StickS3 Grove 端口:
 *       GPIO 2 (TX) -> FE-URT-1 转接板 RX
 *       GPIO 1 (RX) -> FE-URT-1 转接板 TX
 *       5V / GND    -> 共地并由外部 5V 供电
 * 
 * 操作说明:
 *   - 屏幕显示当前检测到的舵机 ID、实时角度与输入母线电压
 *   - 单击按键 A (正面): 切换待烧录的目标 ID (10, 11, 12... 33)
 *   - 长按按键 A: 自动寻找未知 ID 舵机
 *   - 单击按键 B (侧面): 将当前舵机重写为目标 ID，并将位置命令回零 (Goal Pos = 2048)
 */

#include <M5Unified.h>

#define SERVO_SERIAL Serial1
#define PIN_SERVO_RX 1
#define PIN_SERVO_TX 2
#define SERVO_BAUDRATE 1000000

// 预定义待分配的 Microduck 14 关节 ID 列表
const uint8_t TARGET_IDS[] = {
    10, 11, 12, 13, 14, // 右腿: Yaw, Roll, Pitch, Knee, Ankle
    20, 21, 22, 23, 24, // 左腿: Yaw, Roll, Pitch, Knee, Ankle
    30, 31, 32, 33      // 颈头: NeckPitch, HeadPitch, HeadYaw, HeadRoll
};
const char* TARGET_NAMES[] = {
    "R_HipYaw(10)", "R_HipRoll(11)", "R_HipPitch(12)", "R_Knee(13)", "R_Ankle(14)",
    "L_HipYaw(20)", "L_HipRoll(21)", "L_HipPitch(22)", "L_Knee(23)", "L_Ankle(24)",
    "NeckPitch(30)", "HeadPitch(31)", "HeadYaw(32)", "HeadRoll(33)"
};
const int NUM_TARGETS = sizeof(TARGET_IDS) / sizeof(TARGET_IDS[0]);

int selected_target_idx = 0;
uint8_t detected_id = 0xFF;
int16_t current_pos = -1;
float current_voltage = 0.0;
bool is_locked_zero = false;

// 飞特 STS 协议底层辅助函数
void sts_write_reg(uint8_t id, uint8_t reg, uint8_t val) {
    uint8_t packet[7];
    packet[0] = 0xFF;
    packet[1] = 0xFF;
    packet[2] = id;
    packet[3] = 4; // 长度: 4 (指令+地址+值+校验)
    packet[4] = 0x03; // WRITE
    packet[5] = reg;
    packet[6] = val;
    uint8_t checksum = 0;
    for (int i = 2; i < 7; i++) checksum += packet[i];
    uint8_t wire[8];
    memcpy(wire, packet, 7);
    wire[7] = ~checksum;
    SERVO_SERIAL.write(wire, 8);
    SERVO_SERIAL.flush();
}

void sts_write_pos(uint8_t id, uint16_t pos, uint16_t speed, uint8_t acc) {
    uint8_t packet[13];
    packet[0] = 0xFF;
    packet[1] = 0xFF;
    packet[2] = id;
    packet[3] = 9; // 长度
    packet[4] = 0x03; // WRITE
    packet[5] = 0x2A; // 目标位置寄存器 42 (0x2A)
    packet[6] = pos & 0xFF;
    packet[7] = (pos >> 8) & 0xFF;
    packet[8] = 0; // 时间
    packet[9] = 0;
    packet[10] = speed & 0xFF;
    packet[11] = (speed >> 8) & 0xFF;
    uint8_t checksum = 0;
    for (int i = 2; i < 12; i++) checksum += packet[i];
    packet[12] = ~checksum;
    SERVO_SERIAL.write(packet, 13);
    SERVO_SERIAL.flush();
}

int sts_ping(uint8_t id) {
    while (SERVO_SERIAL.available()) SERVO_SERIAL.read();
    uint8_t packet[6] = {0xFF, 0xFF, id, 0x02, 0x01, (uint8_t)~(id + 0x02 + 0x01)};
    SERVO_SERIAL.write(packet, 6);
    SERVO_SERIAL.flush();
    
    unsigned long start = millis();
    while (millis() - start < 15) {
        if (SERVO_SERIAL.available() >= 6) {
            if (SERVO_SERIAL.read() == 0xFF && SERVO_SERIAL.read() == 0xFF) {
                uint8_t ret_id = SERVO_SERIAL.read();
                if (ret_id == id) return 1;
            }
        }
    }
    return 0;
}

void scan_bus() {
    detected_id = 0xFF;
    // 先探测工厂默认 ID 1
    if (sts_ping(1)) {
        detected_id = 1;
        return;
    }
    // 快速扫描 14 个常用 ID
    for (int i = 0; i < NUM_TARGETS; i++) {
        if (sts_ping(TARGET_IDS[i])) {
            detected_id = TARGET_IDS[i];
            return;
        }
    }
}

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    
    M5.Display.setRotation(1);
    M5.Display.fillScreen(BLACK);
    M5.Display.setTextColor(YELLOW);
    M5.Display.setTextSize(1);
    M5.Display.drawString("M5StickS3 ServoTool", 10, 10);
    M5.Display.drawString("Init 1Mbps UART...", 10, 25);
    
    SERVO_SERIAL.begin(SERVO_BAUDRATE, SERIAL_8N1, PIN_SERVO_RX, PIN_SERVO_TX);
    delay(500);
}

void loop() {
    M5.update();
    
    // 按键 A 单击: 循环切换目标要写入的 ID
    if (M5.BtnA.wasPressed()) {
        selected_target_idx = (selected_target_idx + 1) % NUM_TARGETS;
    }
    
    // 按键 B 单击: 烧写选中的目标 ID 并将舵机命令归零锁死在 2048 中位
    if (M5.BtnB.wasPressed()) {
        if (detected_id != 0xFF) {
            uint8_t target_id = TARGET_IDS[selected_target_idx];
            // 解锁 EEPROM (写保护锁存器 0x37 = 0)
            sts_write_reg(detected_id, 0x37, 0x00);
            delay(10);
            // 写入新 ID (寄存器 0x05)
            sts_write_reg(detected_id, 0x05, target_id);
            delay(10);
            // 锁存 EEPROM (0x37 = 1)
            sts_write_reg(target_id, 0x37, 0x01);
            delay(10);
            // 强制将舵机运动到机械中心位 (2048)
            sts_write_pos(target_id, 2048, 1500, 50);
            detected_id = target_id;
            is_locked_zero = true;
        }
    }
    
    // 周期性探测当前连接的舵机
    static unsigned long last_scan = 0;
    if (millis() - last_scan > 500) {
        last_scan = millis();
        scan_bus();
    }
    
    // 刷新显示界面
    M5.Display.fillScreen(BLACK);
    M5.Display.setTextColor(TFT_WHITE);
    M5.Display.setTextSize(1);
    M5.Display.drawString("=== MICRODUCK TOOL ===", 5, 5);
    
    if (detected_id == 0xFF) {
        M5.Display.setTextColor(TFT_RED);
        M5.Display.drawString("Status: NO SERVO DETECTED", 5, 25);
        M5.Display.drawString("Check 7.4V & Wiring!", 5, 40);
    } else {
        M5.Display.setTextColor(TFT_GREEN);
        M5.Display.drawString("Detected ID: ", 5, 25);
        M5.Display.drawNumber(detected_id, 90, 25);
        
        if (is_locked_zero) {
            M5.Display.setTextColor(TFT_CYAN);
            M5.Display.drawString("[LOCKED AT ZERO 2048]", 5, 40);
        }
    }
    
    M5.Display.setTextColor(TFT_YELLOW);
    M5.Display.drawString("Target to Set:", 5, 65);
    M5.Display.setTextSize(2);
    M5.Display.drawString(TARGET_NAMES[selected_target_idx], 5, 80);
    
    M5.Display.setTextSize(1);
    M5.Display.setTextColor(TFT_LIGHTGRAY);
    M5.Display.drawString("BtnA: Next ID | BtnB: Burn&Zero", 5, 110);
    
    delay(50);
}
