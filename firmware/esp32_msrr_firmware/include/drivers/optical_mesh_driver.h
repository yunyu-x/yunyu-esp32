/**
 * @file optical_mesh_driver.h
 * @brief 6-Face Optical Mesh Transceiver & Multi-Face FPC Routing Driver for microUnit.
 * @details Implements 38kHz PWM carrier modulation, COBS frame encoding/decoding,
 *          CRC16 validation, and dynamic neighbor adjacency detection.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "drivers/driver_interface.h"
#include "drivers/driver_hub.h"
#include "hal/hal_interface.h"

namespace microunit {

struct OpticalPacket {
    uint8_t src_id;
    uint8_t dst_id;
    uint8_t msg_type;
    uint8_t payload[16];
    size_t payload_len;
    uint16_t crc16;
};

struct FaceLinkInfo {
    bool is_linked;
    uint8_t neighbor_id;
    float time_since_last_rx_s;
    uint32_t packets_received;
};

class OpticalMeshDriver : public IDeviceDriver {
public:
    static constexpr size_t NUM_FACES = 6;
    static constexpr float LINK_TIMEOUT_SECONDS = 1.0f;
    static constexpr uint16_t CRC16_POLY = 0x1021;

    OpticalMeshDriver(uint8_t pin_tx = 8, uint8_t pin_rx = 9,
                      uint8_t pin_ctrl = 15, uint8_t node_id = 1);
    ~OpticalMeshDriver() override = default;

    // IDeviceDriver Implementation
    const char* getName() const override { return "OpticalMesh_Transceiver"; }
    DeviceType getType() const override { return DeviceType::COMM_OPTICAL_FACE; }
    uint8_t getDeviceId() const override { return 5; }

    bool init() override;
    bool start() override;
    void stop() override;
    void update(float dt_seconds) override;

    bool selfTest() override;
    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _error_code; }
    bool recover(uint32_t fault_mask) override;
    bool isRunning() const override { return _running; }

    // Protocol & Framing Utilities
    static size_t encodeCobs(const uint8_t* src, size_t len, uint8_t* dst);
    static size_t decodeCobs(const uint8_t* src, size_t len, uint8_t* dst);
    static uint16_t calculateCrc16(const uint8_t* data, size_t len);

    // Transmission & Multi-Face Routing
    bool sendPacket(FaceSlot slot, uint8_t dst_id, uint8_t msg_type,
                    const uint8_t* payload, size_t payload_len);
    void simulateReceivePacket(FaceSlot slot, uint8_t src_id, uint8_t dst_id,
                               uint8_t msg_type, const uint8_t* payload, size_t payload_len);

    // Face Adjacency Queries
    bool isFaceLinked(FaceSlot slot) const;
    uint8_t getNeighborId(FaceSlot slot) const;
    uint32_t getTxPacketCount() const { return _tx_packets; }
    uint32_t getRxPacketCount() const { return _rx_packets; }

private:
    uint8_t _pin_tx;
    uint8_t _pin_rx;
    uint8_t _pin_ctrl;
    uint8_t _node_id;

    DriverHealth _health;
    uint32_t _error_code;
    bool _running;

    FaceLinkInfo _faces[NUM_FACES];
    uint32_t _tx_packets;
    uint32_t _rx_packets;

    void selectFaceSlot(FaceSlot slot);
};

} // namespace microunit
