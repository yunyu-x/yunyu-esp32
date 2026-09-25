/**
 * @file optical_comm.cpp
 * @brief Optical Infrared Transceiver Implementation.
 */

#include "comm/optical_comm.h"

OpticalTransceiver::OpticalTransceiver(uint8_t robot_id)
    : _robot_id(robot_id), _tx_count(0), _rx_count(0), _rx_index(0) {}

void OpticalTransceiver::init() {
    pinMode(PIN_OPTICAL_TX, OUTPUT);
    pinMode(PIN_OPTICAL_RX, INPUT);
    digitalWrite(PIN_OPTICAL_TX, LOW);
}

uint8_t OpticalTransceiver::calculateCRC8(const uint8_t* data, size_t len) {
    uint8_t crc = 0x00;
    while (len--) {
        uint8_t extract = *data++;
        for (uint8_t tempI = 8; tempI; tempI--) {
            uint8_t sum = (crc ^ extract) & 0x01;
            crc >>= 1;
            if (sum) {
                crc ^= 0x8C; // Bit-reversed representation of polynomial 0x07
            }
            extract >>= 1;
        }
    }
    return crc;
}

void OpticalTransceiver::broadcastHeartbeat(uint8_t current_state, uint16_t vbat_mv) {
    OpticalPacket pkt;
    pkt.sync_byte1 = 0xAA;
    pkt.sync_byte2 = 0x55;
    pkt.sender_id = _robot_id;
    pkt.face_id = 0; // Default face
    pkt.state = current_state;
    pkt.vbat_mv = vbat_mv;
    pkt.crc8 = calculateCRC8((const uint8_t*)&pkt, sizeof(OpticalPacket) - 1);

    // Send packet via UART2 / bit-bang optical LED
    const uint8_t* raw = (const uint8_t*)&pkt;
    for (size_t i = 0; i < sizeof(OpticalPacket); i++) {
        // Toggle optical LED modulated pulse train
        for (int b = 0; b < 8; b++) {
            bool bit_val = (raw[i] >> b) & 0x01;
            digitalWrite(PIN_OPTICAL_TX, bit_val ? HIGH : LOW);
            delayMicroseconds(50); // 20 kbps baud
        }
    }
    digitalWrite(PIN_OPTICAL_TX, LOW);
    _tx_count++;
}

bool OpticalTransceiver::processIncomingByte(uint8_t byte, OpticalPacket* out_packet) {
    if (_rx_index == 0 && byte != 0xAA) return false;
    if (_rx_index == 1 && byte != 0x55) { _rx_index = 0; return false; }

    _rx_buffer[_rx_index++] = byte;

    if (_rx_index >= sizeof(OpticalPacket)) {
        _rx_index = 0;
        OpticalPacket* candidate = (OpticalPacket*)_rx_buffer;
        uint8_t expected_crc = calculateCRC8(_rx_buffer, sizeof(OpticalPacket) - 1);
        if (candidate->crc8 == expected_crc) {
            if (out_packet != nullptr) {
                memcpy(out_packet, candidate, sizeof(OpticalPacket));
            }
            _rx_count++;
            return true;
        }
    }
    return false;
}

void OpticalTransceiver::update(float dt) {
    // Background frame timeout / buffer flushing
}
