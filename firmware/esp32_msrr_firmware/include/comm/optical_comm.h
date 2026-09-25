/**
 * @file optical_comm.h
 * @brief Inter-Module Optical Infrared Transceiver Protocol (50 Hz Heartbeat & Sync).
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <Arduino.h>
#include "config.h"

#pragma pack(push, 1)
struct OpticalPacket {
    uint8_t sync_byte1; // 0xAA
    uint8_t sync_byte2; // 0x55
    uint8_t sender_id;  // Robot ID (1-255)
    uint8_t face_id;    // Transmitting face (0-5: +X, -X, +Y, -Y, +Z, -Z)
    uint8_t state;      // Current FSM state
    uint16_t vbat_mv;   // Battery voltage in millivolts
    uint8_t crc8;       // Polynomial 0x07
};
#pragma pack(pop)

class OpticalTransceiver {
public:
    OpticalTransceiver(uint8_t robot_id);
    void init();
    void broadcastHeartbeat(uint8_t current_state, uint16_t vbat_mv);
    bool processIncomingByte(uint8_t byte, OpticalPacket* out_packet);
    void update(float dt);

    uint32_t getPacketsTransmitted() const { return _tx_count; }
    uint32_t getPacketsReceived() const { return _rx_count; }

private:
    uint8_t _robot_id;
    uint32_t _tx_count;
    uint32_t _rx_count;
    uint8_t _rx_buffer[sizeof(OpticalPacket)];
    uint8_t _rx_index;

    uint8_t calculateCRC8(const uint8_t* data, size_t len);
};
