/**
 * @file optical_mesh_protocol.h
 * @brief High-Speed 6-Face Optical Infrared Mesh & Leased-Token Protocol
 * @author microUnit Robotics Open Source Team
 * 
 * Provides:
 * - Distributed face-to-face packet routing across all 6 faces (+X, -X, +Y, -Y, +Z, -Z)
 * - COBS (Consistent Overhead Byte Stuffing) zero-delimiter framing
 * - CCITT CRC-16 data integrity verification
 * - Hardware-synchronized motion tokens with microsecond precision
 */

#pragma once

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Packet Type Identifiers
#define OPT_MSG_DISCOVERY_PING     0x01
#define OPT_MSG_DISCOVERY_ACK      0x02
#define OPT_MSG_TOKEN_REQUEST      0x03
#define OPT_MSG_TOKEN_GRANT        0x04
#define OPT_MSG_MOTION_PREPARE     0x05
#define OPT_MSG_MOTION_SYNC_TRIG   0x06
#define OPT_MSG_EPM_LATCH_CONFIRM  0x07
#define OPT_MSG_EMERGENCY_STOP     0x0F

#pragma pack(push, 1)
typedef struct {
    uint8_t  msg_type;          // One of OPT_MSG_*
    uint8_t  src_node_id;       // Sending Robot ID (1-255)
    uint8_t  dst_node_id;       // Target Robot ID (0xFF for broadcast)
    uint8_t  src_face_id;       // Transmitting face (0-5)
    uint8_t  seq_num;           // Rolling sequence counter
    uint32_t sync_timestamp_us; // Hardware microsecond timestamp for phased motion
    uint8_t  payload[8];        // Mode-specific arguments (gait phase, torque, etc.)
    uint16_t crc16;             // CCITT-16 checksum
} OpticalMeshMessage_t;
#pragma pack(pop)

// COBS Framing functions
size_t cobs_encode(const uint8_t* from, size_t len, uint8_t* to);
size_t cobs_decode(const uint8_t* from, size_t len, uint8_t* to);
uint16_t optical_crc16(const uint8_t* data, size_t length);

#ifdef __cplusplus
}

class OpticalMeshRouter {
public:
    OpticalMeshRouter(uint8_t local_node_id);
    void init();
    
    // Packet Transmission
    bool sendMotionPrepare(uint8_t face_id, uint8_t target_node, uint8_t mode, uint32_t fire_in_us);
    bool broadcastSyncTrigger(uint8_t face_id, uint32_t exact_fire_time_us);
    bool sendTokenGrant(uint8_t face_id, uint8_t target_node, uint32_t lease_duration_ms);
    bool sendEPMLatchConfirm(uint8_t face_id, bool latched);

    // Packet Reception
    bool parseIncomingByte(uint8_t face_id, uint8_t byte, OpticalMeshMessage_t* out_msg);

    // Diagnostics
    uint32_t getTxCount() const { return _tx_count; }
    uint32_t getRxCount() const { return _rx_count; }
    uint32_t getCrcErrorCount() const { return _crc_errors; }

private:
    uint8_t _node_id;
    uint8_t _seq;
    uint32_t _tx_count;
    uint32_t _rx_count;
    uint32_t _crc_errors;

    uint8_t _rx_raw_buf[6][sizeof(OpticalMeshMessage_t) + 4];
    uint8_t _rx_raw_idx[6];
};

#endif
