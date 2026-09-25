/**
 * @file optical_mesh_protocol.cpp
 * @brief Implementation of Optical Mesh COBS framing, CRC16, and token router.
 * @author microUnit Robotics Open Source Team
 */

#include "comm/optical_mesh_protocol.h"
#include <string.h>

// Standard CCITT CRC-16 (Polynomial: 0x1021, Initial: 0xFFFF)
uint16_t optical_crc16(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; ++j) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

// COBS byte stuffing encode
size_t cobs_encode(const uint8_t* from, size_t len, uint8_t* to) {
    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 1;

    while (read_idx < len) {
        if (from[read_idx] == 0) {
            to[code_idx] = code;
            code = 1;
            code_idx = write_idx++;
            read_idx++;
        } else {
            to[write_idx++] = from[read_idx++];
            code++;
            if (code == 0xFF) {
                to[code_idx] = code;
                code = 1;
                code_idx = write_idx++;
            }
        }
    }
    to[code_idx] = code;
    return write_idx;
}

// COBS byte stuffing decode
size_t cobs_decode(const uint8_t* from, size_t len, uint8_t* to) {
    if (len == 0) return 0;
    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < len) {
        uint8_t code = from[read_idx++];
        for (uint8_t i = 1; i < code; ++i) {
            if (read_idx >= len) return 0;
            to[write_idx++] = from[read_idx++];
        }
        if (code < 0xFF && read_idx < len) {
            to[write_idx++] = 0;
        }
    }
    return write_idx;
}

// OpticalMeshRouter implementation
OpticalMeshRouter::OpticalMeshRouter(uint8_t local_node_id)
    : _node_id(local_node_id), _seq(0), _tx_count(0), _rx_count(0), _crc_errors(0)
{
    memset(_rx_raw_idx, 0, sizeof(_rx_raw_idx));
}

void OpticalMeshRouter::init() {
    _tx_count = 0;
    _rx_count = 0;
    _crc_errors = 0;
    memset(_rx_raw_idx, 0, sizeof(_rx_raw_idx));
}

bool OpticalMeshRouter::sendMotionPrepare(uint8_t face_id, uint8_t target_node, uint8_t mode, uint32_t fire_in_us) {
    OpticalMeshMessage_t msg;
    msg.msg_type = OPT_MSG_MOTION_PREPARE;
    msg.src_node_id = _node_id;
    msg.dst_node_id = target_node;
    msg.src_face_id = face_id;
    msg.seq_num = _seq++;
    msg.sync_timestamp_us = fire_in_us;
    memset(msg.payload, 0, sizeof(msg.payload));
    msg.payload[0] = mode;
    msg.crc16 = optical_crc16((const uint8_t*)&msg, sizeof(OpticalMeshMessage_t) - 2);

    _tx_count++;
    // In production firmware, encoded packet is pushed into UART DMA ring buffer for the specified face
    return true;
}

bool OpticalMeshRouter::broadcastSyncTrigger(uint8_t face_id, uint32_t exact_fire_time_us) {
    OpticalMeshMessage_t msg;
    msg.msg_type = OPT_MSG_MOTION_SYNC_TRIG;
    msg.src_node_id = _node_id;
    msg.dst_node_id = 0xFF; // Broadcast
    msg.src_face_id = face_id;
    msg.seq_num = _seq++;
    msg.sync_timestamp_us = exact_fire_time_us;
    memset(msg.payload, 0, sizeof(msg.payload));
    msg.crc16 = optical_crc16((const uint8_t*)&msg, sizeof(OpticalMeshMessage_t) - 2);

    _tx_count++;
    return true;
}

bool OpticalMeshRouter::sendTokenGrant(uint8_t face_id, uint8_t target_node, uint32_t lease_duration_ms) {
    OpticalMeshMessage_t msg;
    msg.msg_type = OPT_MSG_TOKEN_GRANT;
    msg.src_node_id = _node_id;
    msg.dst_node_id = target_node;
    msg.src_face_id = face_id;
    msg.seq_num = _seq++;
    msg.sync_timestamp_us = lease_duration_ms;
    memset(msg.payload, 0, sizeof(msg.payload));
    msg.crc16 = optical_crc16((const uint8_t*)&msg, sizeof(OpticalMeshMessage_t) - 2);

    _tx_count++;
    return true;
}

bool OpticalMeshRouter::sendEPMLatchConfirm(uint8_t face_id, bool latched) {
    OpticalMeshMessage_t msg;
    msg.msg_type = OPT_MSG_EPM_LATCH_CONFIRM;
    msg.src_node_id = _node_id;
    msg.dst_node_id = 0xFF;
    msg.src_face_id = face_id;
    msg.seq_num = _seq++;
    msg.sync_timestamp_us = 0;
    memset(msg.payload, 0, sizeof(msg.payload));
    msg.payload[0] = latched ? 1 : 0;
    msg.crc16 = optical_crc16((const uint8_t*)&msg, sizeof(OpticalMeshMessage_t) - 2);

    _tx_count++;
    return true;
}

bool OpticalMeshRouter::parseIncomingByte(uint8_t face_id, uint8_t byte, OpticalMeshMessage_t* out_msg) {
    if (face_id >= 6) return false;

    // Zero byte is the COBS frame delimiter
    if (byte == 0x00) {
        if (_rx_raw_idx[face_id] >= sizeof(OpticalMeshMessage_t)) {
            uint8_t decoded_buf[sizeof(OpticalMeshMessage_t) + 4];
            size_t decoded_len = cobs_decode(_rx_raw_buf[face_id], _rx_raw_idx[face_id], decoded_buf);
            _rx_raw_idx[face_id] = 0;

            if (decoded_len == sizeof(OpticalMeshMessage_t)) {
                OpticalMeshMessage_t* candidate = (OpticalMeshMessage_t*)decoded_buf;
                uint16_t expected_crc = optical_crc16(decoded_buf, sizeof(OpticalMeshMessage_t) - 2);
                if (candidate->crc16 == expected_crc) {
                    _rx_count++;
                    memcpy(out_msg, candidate, sizeof(OpticalMeshMessage_t));
                    return true;
                } else {
                    _crc_errors++;
                }
            }
        }
        _rx_raw_idx[face_id] = 0;
        return false;
    }

    if (_rx_raw_idx[face_id] < sizeof(_rx_raw_buf[face_id])) {
        _rx_raw_buf[face_id][_rx_raw_idx[face_id]++] = byte;
    } else {
        // Buffer overflow, drop frame
        _rx_raw_idx[face_id] = 0;
    }
    return false;
}
