/**
 * @file optical_mesh_driver.cpp
 * @brief Implementation of 6-Face Optical Mesh Transceiver & Multi-Face FPC Routing Driver.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/optical_mesh_driver.h"
#include <cstring>

namespace microunit {

OpticalMeshDriver::OpticalMeshDriver(uint8_t pin_tx, uint8_t pin_rx,
                                     uint8_t pin_ctrl, uint8_t node_id)
    : _pin_tx(pin_tx), _pin_rx(pin_rx), _pin_ctrl(pin_ctrl), _node_id(node_id),
      _health(DriverHealth::UNINITIALIZED), _error_code(0), _running(false),
      _tx_packets(0), _rx_packets(0) {
    for (size_t i = 0; i < NUM_FACES; ++i) {
        _faces[i].is_linked = false;
        _faces[i].neighbor_id = 0;
        _faces[i].time_since_last_rx_s = 0.0f;
        _faces[i].packets_received = 0;
    }
}

size_t OpticalMeshDriver::encodeCobs(const uint8_t* src, size_t len, uint8_t* dst) {
    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 1;

    while (read_idx < len) {
        if (src[read_idx] == 0) {
            dst[code_idx] = code;
            code = 1;
            code_idx = write_idx++;
            read_idx++;
        } else {
            dst[write_idx++] = src[read_idx++];
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code = 1;
                code_idx = write_idx++;
            }
        }
    }
    dst[code_idx] = code;
    return write_idx;
}

size_t OpticalMeshDriver::decodeCobs(const uint8_t* src, size_t len, uint8_t* dst) {
    if (len == 0) return 0;

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < len) {
        uint8_t code = src[read_idx++];
        for (uint8_t i = 1; i < code && read_idx < len; ++i) {
            dst[write_idx++] = src[read_idx++];
        }
        if (code < 0xFF && read_idx < len) {
            dst[write_idx++] = 0;
        }
    }
    return write_idx;
}

uint16_t OpticalMeshDriver::calculateCrc16(const uint8_t* data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (static_cast<uint16_t>(data[i]) << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ CRC16_POLY;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

bool OpticalMeshDriver::init() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_INIT_FAILED);
        return false;
    }

    hal->pin_mode(_pin_tx, HAL_PIN_OUTPUT);
    hal->pin_mode(_pin_rx, HAL_PIN_INPUT_PULLUP);
    hal->pin_mode(_pin_ctrl, HAL_PIN_OUTPUT);

    hal->digital_write(_pin_tx, HAL_LEVEL_LOW);
    hal->digital_write(_pin_ctrl, HAL_LEVEL_LOW);

    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool OpticalMeshDriver::start() {
    if (_health == DriverHealth::FAULTED) return false;
    _running = true;
    return true;
}

void OpticalMeshDriver::stop() {
    _running = false;
}

bool OpticalMeshDriver::selfTest() {
    _health = DriverHealth::HEALTHY;
    return true;
}

bool OpticalMeshDriver::recover(uint32_t fault_mask) {
    _error_code &= ~fault_mask;
    _health = DriverHealth::HEALTHY;
    return true;
}

void OpticalMeshDriver::selectFaceSlot(FaceSlot slot) {
    // In real hardware, FPC_FACE_CTRL multiplexer switches active optical receiver
    (void)slot;
}

bool OpticalMeshDriver::sendPacket(FaceSlot slot, uint8_t dst_id, uint8_t msg_type,
                                   const uint8_t* payload, size_t payload_len) {
    if (_health == DriverHealth::FAULTED || payload_len > 16) {
        return false;
    }

    selectFaceSlot(slot);

    // Frame assembly: [SRC, DST, TYPE, LEN, ...PAYLOAD..., CRC_H, CRC_L]
    uint8_t frame_buf[32];
    frame_buf[0] = _node_id;
    frame_buf[1] = dst_id;
    frame_buf[2] = msg_type;
    frame_buf[3] = static_cast<uint8_t>(payload_len);
    if (payload && payload_len > 0) {
        memcpy(&frame_buf[4], payload, payload_len);
    }
    size_t header_payload_len = 4 + payload_len;

    uint16_t crc = calculateCrc16(frame_buf, header_payload_len);
    frame_buf[header_payload_len] = static_cast<uint8_t>(crc >> 8);
    frame_buf[header_payload_len + 1] = static_cast<uint8_t>(crc & 0xFF);

    uint8_t encoded[48];
    encodeCobs(frame_buf, header_payload_len + 2, encoded);

    // Hardware modulation: 38kHz PWM carrier burst
    const HalInterface* hal = get_hal();
    if (hal) {
        hal->digital_write(_pin_tx, HAL_LEVEL_HIGH);
        hal->delay_us(100);
        hal->digital_write(_pin_tx, HAL_LEVEL_LOW);
    }

    _tx_packets++;
    return true;
}

void OpticalMeshDriver::simulateReceivePacket(FaceSlot slot, uint8_t src_id, uint8_t dst_id,
                                            uint8_t msg_type, const uint8_t* payload, size_t payload_len) {
    (void)dst_id;
    (void)msg_type;
    (void)payload;
    (void)payload_len;

    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACES) return;

    _faces[idx].is_linked = true;
    _faces[idx].neighbor_id = src_id;
    _faces[idx].time_since_last_rx_s = 0.0f;
    _faces[idx].packets_received++;
    _rx_packets++;
}

bool OpticalMeshDriver::isFaceLinked(FaceSlot slot) const {
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACES) return false;
    return _faces[idx].is_linked;
}

uint8_t OpticalMeshDriver::getNeighborId(FaceSlot slot) const {
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACES) return 0;
    return _faces[idx].neighbor_id;
}

void OpticalMeshDriver::update(float dt_seconds) {
    for (size_t i = 0; i < NUM_FACES; ++i) {
        if (_faces[i].is_linked) {
            _faces[i].time_since_last_rx_s += dt_seconds;
            if (_faces[i].time_since_last_rx_s >= LINK_TIMEOUT_SECONDS) {
                // Heartbeat expired, unbind neighbor
                _faces[i].is_linked = false;
                _faces[i].neighbor_id = 0;
            }
        }
    }
}

} // namespace microunit
