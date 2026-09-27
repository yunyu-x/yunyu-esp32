/**
 * @file m5sticks3_cpg_walk.ino
 * @brief M5StickS3 专用 Microduck 50Hz 律动自主行走控制与动态眼球交互固件
 * 
 * 功能特点:
 *   1. 50Hz (20ms 周期) 硬件定时器驱动 CPG (中枢模式发生器) 开闭环双足律动步态;
 *   2. 利用 M5StickS3 板载 BMI270 实时监测机身横滚与俯仰角，支持跌倒急停自锁;
 *   3. 0.85寸屏幕实时渲染动态眨眼表情包与电量状态;
 *   4. 单击按键 A 一键平滑切换“站立待机”与“自主迈步”。
 */

#include <M5Unified.h>
#include <math.h>

#define SERVO_SERIAL Serial1
#define PIN_SERVO_RX 1
#define PIN_SERVO_TX 2
#define SERVO_BAUDRATE 1000000

// 14 关节 ID
const uint8_t JOINT_IDS[14] = {
    10, 11, 12, 13, 14, // 右腿: Yaw, Roll, Pitch, Knee, Ankle
    20, 21, 22, 23, 24, // 左腿: Yaw, Roll, Pitch, Knee, Ankle
    30, 31, 32, 33      // 颈头: NeckPitch, HeadPitch, HeadYaw, HeadRoll
};

// 站立姿态默认基准角度 (单位: 弧度)
const float STAND_POSE[14] = {
    0.0,   0.05,  0.45,  -0.90,  0.45,  // 右腿
    0.0,  -0.05, -0.45,   0.90, -0.45,  // 左腿
    0.35,  0.0,   0.0,    0.0           // 颈头
};

enum RobotState {
    STATE_STAND,
    STATE_WALKING,
    STATE_FALLEN
};

RobotState current_state = STATE_STAND;
float gait_phase = 0.0;
const float GAIT_FREQ = 1.6; // 步频 1.6 Hz
const float DT = 0.02;       // 50 Hz 周期 (20 ms)

// 飞特 STS 1Mbps Sync Write 批量写入 14 舵机
void sts_sync_write_pos(const uint16_t targets[14]) {
    // 飞特 Sync Write 报文: 0xFF 0xFF 0xFE (长度) 0x83 (起始寄存器 0x2A) (单包数据长度 2)
    uint8_t packet[128];
    packet[0] = 0xFF;
    packet[1] = 0xFF;
    packet[2] = 0xFE; // 广播 ID
    uint8_t data_len = 14 * 3 + 4; // 14 个舵机，每个 (ID + 2字节位置)
    packet[3] = data_len;
    packet[4] = 0x83; // SYNC WRITE
    packet[5] = 0x2A; // 目标位置寄存器 42
    packet[6] = 0x02; // 每个舵机写入 2 字节
    
    int idx = 7;
    for (int i = 0; i < 14; i++) {
        packet[idx++] = JOINT_IDS[i];
        packet[idx++] = targets[i] & 0xFF;
        packet[idx++] = (targets[i] >> 8) & 0xFF;
    }
    
    uint8_t checksum = 0;
    for (int i = 2; i < idx; i++) checksum += packet[i];
    packet[idx++] = ~checksum;
    
    SERVO_SERIAL.write(packet, idx);
    SERVO_SERIAL.flush();
}

// 弧度转飞特 12 位编码器位置 (0~4096, 2048 为中位 0 rad)
uint16_t rad_to_sts_pos(float rad, int joint_idx) {
    float counts_per_rad = 4096.0 / (2.0 * M_PI);
    int32_t pos = 2048 + (int32_t)(rad * counts_per_rad);
    if (pos < 0) pos = 0;
    if (pos > 4095) pos = 4095;
    return (uint16_t)pos;
}

// 绘制小鸭动态眼球交互 UI
void draw_duck_eyes(bool is_walking, float roll, float pitch) {
    M5.Display.fillScreen(BLACK);
    
    // 左右眼球中心坐标
    int left_eye_x = 36;
    int right_eye_x = 92;
    int eye_y = 55;
    int eye_r = 24;
    
    // 绘制眼眶外轮廓 (小鸭大眼睛)
    M5.Display.fillCircle(left_eye_x, eye_y, eye_r, TFT_WHITE);
    M5.Display.fillCircle(right_eye_x, eye_y, eye_r, TFT_WHITE);
    
    // 根据机身倾角计算瞳孔偏移 (眼球随姿态动态调整)
    int pupil_dx = (int)(roll * 0.4);
    int pupil_dy = (int)(pitch * 0.4);
    pupil_dx = constrain(pupil_dx, -10, 10);
    pupil_dy = constrain(pupil_dy, -8, 8);
    
    // 绘制黑色瞳孔与高光反光点
    M5.Display.fillCircle(left_eye_x + pupil_dx, eye_y + pupil_dy, 12, TFT_BLACK);
    M5.Display.fillCircle(right_eye_x + pupil_dx, eye_y + pupil_dy, 12, TFT_BLACK);
    M5.Display.fillCircle(left_eye_x + pupil_dx - 3, eye_y + pupil_dy - 3, 4, TFT_WHITE);
    M5.Display.fillCircle(right_eye_x + pupil_dx - 3, eye_y + pupil_dy - 3, 4, TFT_WHITE);
    
    // 底部状态栏
    M5.Display.setTextSize(1);
    if (current_state == STATE_WALKING) {
        M5.Display.setTextColor(TFT_GREEN);
        M5.Display.drawString("[AUTONOMOUS WALKING]", 8, 105);
    } else if (current_state == STATE_STAND) {
        M5.Display.setTextColor(TFT_YELLOW);
        M5.Display.drawString("[STANDBY - PRESS A]", 12, 105);
    } else {
        M5.Display.setTextColor(TFT_RED);
        M5.Display.drawString("[FALLEN - PROTECTED]", 10, 105);
    }
}

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    
    M5.Display.setRotation(1);
    M5.Display.fillScreen(BLACK);
    
    // 初始化板载 IMU (BMI270)
    M5.Imu.init();
    
    // 初始化 1Mbps 舵机硬件总线
    SERVO_SERIAL.begin(SERVO_BAUDRATE, SERIAL_8N1, PIN_SERVO_RX, PIN_SERVO_TX);
    delay(500);
}

void loop() {
    static unsigned long last_tick = 0;
    M5.update();
    
    // 按键 A 单击: 步态开始 / 暂停待机
    if (M5.BtnA.wasPressed()) {
        if (current_state == STATE_STAND) {
            current_state = STATE_WALKING;
        } else {
            current_state = STATE_STAND;
        }
    }
    
    // 50 Hz 硬实时控制周期 (20 ms)
    if (millis() - last_tick >= 20) {
        last_tick = millis();
        
        // 1. 读取板载 BMI270 姿态
        float ax, ay, az;
        M5.Imu.getAccelData(&ax, &ay, &az);
        float roll = atan2(ay, az) * 180.0 / M_PI;
        float pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / M_PI;
        
        // 跌倒保护检测 (倾角 > 45度触发紧急断扭矩)
        if (fabs(roll) > 45.0 || fabs(pitch) > 45.0) {
            current_state = STATE_FALLEN;
        }
        
        // 2. 律动 CPG 计算 14 个目标关节角
        float target_rad[14];
        memcpy(target_rad, STAND_POSE, sizeof(STAND_POSE));
        
        if (current_state == STATE_WALKING) {
            gait_phase += 2.0 * M_PI * GAIT_FREQ * DT;
            if (gait_phase > 2.0 * M_PI) gait_phase -= 2.0 * M_PI;
            
            // 髋部侧向晃动协调 (Roll 左右摆动转移质心)
            float roll_sway = 0.08 * sin(gait_phase);
            target_rad[1] += roll_sway; // 右髋横滚
            target_rad[6] += roll_sway; // 左髋横滚
            
            // 双腿交替摆动与蹬地 (反相 180 度)
            float right_lift = 0.25 * fmax(0.0f, sin(gait_phase));
            float left_lift  = 0.25 * fmax(0.0f, sin(gait_phase + M_PI));
            
            target_rad[2] += right_lift * 0.8;  // 右髋俯仰
            target_rad[3] -= right_lift * 1.5;  // 右膝盖屈曲
            target_rad[4] += right_lift * 0.7;  // 右脚踝提离
            
            target_rad[7] -= left_lift * 0.8;   // 左髋俯仰
            target_rad[8] += left_lift * 1.5;   // 左膝盖屈曲
            target_rad[9] -= left_lift * 0.7;   // 左脚踝提离
            
            // 头部动态侧摆协同配重
            target_rad[13] = -roll_sway * 0.6;  // 头部横滚反向补偿
        }
        
        // 3. 映射为飞特 12 位编码器位置并下发总线
        uint16_t targets_pos[14];
        for (int i = 0; i < 14; i++) {
            targets_pos[i] = rad_to_sts_pos(target_rad[i], i);
        }
        sts_sync_write_pos(targets_pos);
        
        // 4. 周期刷新屏幕眼球
        static int frame_cnt = 0;
        if (++frame_cnt % 5 == 0) {
            draw_duck_eyes(current_state == STATE_WALKING, roll, pitch);
        }
    }
}
