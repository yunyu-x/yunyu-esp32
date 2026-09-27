/**
 * @file brain_cerebellum_protocol.h
 * @brief Microduck Brain-Cerebellum Protocol (BCP) C/C++ Header
 * Standardized Industrial-grade Binary Protocol for ESP32-S3 Firmware
 * 
 * Complies with ASSS v1.0 Standard and yunyu-esp32 architecture.
 */

#ifndef BRAIN_CEREBELLUM_PROTOCOL_H
#define BRAIN_CEREBELLUM_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BCP_PREAMBLE_B0 0xAA
#define BCP_PREAMBLE_B1 0x55
#define BCP_FRAME_TAIL   0x0D

typedef enum {
    BCP_MSG_MOTION_INTENT = 0x01,
    BCP_MSG_TELEMETRY     = 0x02,
    BCP_MSG_HEARTBEAT     = 0x03,
    BCP_MSG_CALIBRATE     = 0x04,
    BCP_MSG_ESTOP         = 0x05
} bcp_msg_type_t;

typedef enum {
    BCP_STATUS_IDLE        = 0x00,
    BCP_STATUS_WALKING     = 0x01,
    BCP_STATUS_FALLEN      = 0x02,
    BCP_STATUS_RECOVERING  = 0x03,
    BCP_STATUS_CALIBRATING = 0x04,
    BCP_STATUS_ESTOP       = 0x05
} bcp_system_status_t;

#pragma pack(push, 1)

/**
 * @brief Downlink Motion Intent Payload (36 Bytes)
 */
typedef struct {
    float cmd_vx;                   // Forward/backward velocity in m/s (-0.5 ~ +0.5)
    float cmd_vy;                   // Lateral translation velocity in m/s (-0.3 ~ +0.3)
    float cmd_vyaw;                 // Yaw angular velocity in rad/s (-1.5 ~ +1.5)
    float head_neck_pitch;          // Neck base pitch target in rad
    float head_pitch;               // Head independent pitch in rad
    float head_yaw;                 // Head yaw in rad
    float head_roll;                // Head roll in rad
    int8_t body_height_offset_mm;   // Height offset (-30 ~ +30 mm)
    int8_t body_roll_offset_deg;    // Roll tilt (-15 ~ +15 deg)
    int8_t body_pitch_offset_deg;   // Pitch tilt (-15 ~ +15 deg)
    uint8_t mouth_open_pct;         // Beak opening percentage (0~100)
    uint8_t locomotion_mode;        // 0=Adaptive, 1=In-place, 2=Rollers, 3=Crouch
    uint8_t flags;                  // bit0=Enable fall recovery, bit1=Jump allowed
    uint8_t reserved[2];            // Padding for alignment
} bcp_motion_intent_t;

/**
 * @brief Uplink Telemetry Payload (20 Bytes)
 */
typedef struct {
    int16_t quat_w;                 // Attitude quaternion W in Q15 format (* 32767)
    int16_t quat_x;                 // Attitude quaternion X in Q15 format (* 32767)
    int16_t quat_y;                 // Attitude quaternion Y in Q15 format (* 32767)
    int16_t quat_z;                 // Attitude quaternion Z in Q15 format (* 32767)
    int16_t gyro_x;                 // Gyro X in rad/s * 100
    int16_t gyro_y;                 // Gyro Y in rad/s * 100
    int16_t gyro_z;                 // Gyro Z in rad/s * 100
    uint8_t foot_contacts;          // bit0: Left foot, bit1: Right foot
    uint8_t system_state;           // Current state enum (bcp_system_status_t)
    uint16_t battery_mv;            // 2S battery pack voltage in mV
    uint8_t max_motor_temp_c;       // Hottest servo temperature in °C
    uint8_t max_motor_id;           // ID of the hottest servo
    uint16_t total_current_ma;      // Bus total current in mA
} bcp_telemetry_t;

/**
 * @brief Binary Frame Header (6 Bytes)
 */
typedef struct {
    uint8_t preamble[2];            // 0xAA, 0x55
    uint8_t msg_type;               // bcp_msg_type_t
    uint8_t seq_num;                // 0x00 ~ 0xFF
    uint8_t payload_len;            // Length of payload
    uint8_t status;                 // bcp_system_status_t
} bcp_frame_header_t;

/**
 * @brief Binary Frame Tail (3 Bytes)
 */
typedef struct {
    uint16_t crc16;                 // CRC16-CCITT
    uint8_t tail;                   // 0x0D
} bcp_frame_tail_t;

#pragma pack(pop)

/**
 * @brief Computes standard CRC16-CCITT checksum
 */
static inline uint16_t bcp_crc16_ccitt(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

#ifdef __cplusplus
}
#endif

#endif // BRAIN_CEREBELLUM_PROTOCOL_H
