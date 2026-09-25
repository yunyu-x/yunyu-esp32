/**
 * @file test_optical_driver.cpp
 * @brief TDD Unit tests for 6-Face Optical Mesh Transceiver & COBS Framing Driver.
 */

#include <cassert>
#include <cstdio>
#include <cstring>
#include "hal/mock_hal.h"
#include "drivers/optical_mesh_driver.h"

using namespace microunit;

void test_optical_init_and_self_test() {
    printf("[TDD Optical] Running test_optical_init_and_self_test...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    OpticalMeshDriver opt(8, 9, 15, 1); // TX=8, RX=9, CTRL=15, NodeID=1
    assert(opt.getType() == DeviceType::COMM_OPTICAL_FACE);
    assert(opt.getDeviceId() == 5);
    assert(opt.getHealth() == DriverHealth::UNINITIALIZED);

    assert(opt.init() == true);
    assert(opt.getHealth() == DriverHealth::HEALTHY);
    assert(opt.selfTest() == true);

    // Initial state: no neighbors linked on all 6 faces
    for (uint8_t f = 0; f < 6; ++f) {
        assert(opt.isFaceLinked(static_cast<FaceSlot>(f)) == false);
        assert(opt.getNeighborId(static_cast<FaceSlot>(f)) == 0);
    }

    printf("  -> PASS: Optical driver init and 6-face idle state verified.\n");
}

void test_cobs_framing_and_crc16() {
    printf("[TDD Optical] Running test_cobs_framing_and_crc16...\n");

    uint8_t payload[] = { 0x01, 0x00, 0x02, 0x55, 0x00, 0xAA };
    size_t payload_len = sizeof(payload);

    uint8_t encoded[32];
    size_t enc_len = OpticalMeshDriver::encodeCobs(payload, payload_len, encoded);

    // Assert: No 0x00 bytes inside the encoded stream
    for (size_t i = 0; i < enc_len; ++i) {
        assert(encoded[i] != 0x00);
    }

    // Decode and verify roundtrip identity
    uint8_t decoded[32];
    size_t dec_len = OpticalMeshDriver::decodeCobs(encoded, enc_len, decoded);
    assert(dec_len == payload_len);
    assert(memcmp(payload, decoded, payload_len) == 0);

    // CRC16 verification
    uint16_t crc1 = OpticalMeshDriver::calculateCrc16(payload, payload_len);
    uint16_t crc2 = OpticalMeshDriver::calculateCrc16(payload, payload_len);
    assert(crc1 == crc2 && crc1 != 0);

    // Corrupted payload must produce different CRC
    payload[1] = 0xFF;
    uint16_t crc_corrupt = OpticalMeshDriver::calculateCrc16(payload, payload_len);
    assert(crc_corrupt != crc1);

    printf("  -> PASS: COBS byte stuffing and CRC16 roundtrip verified.\n");
}

void test_optical_packet_transmission_and_reception() {
    printf("[TDD Optical] Running test_optical_packet_transmission_and_reception...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    OpticalMeshDriver opt1(8, 9, 15, 1); // Robot 1
    opt1.init();
    opt1.start();

    // Prepare a packet to broadcast on Face +X (Slot 0)
    uint8_t msg_data[] = { 0x10, 0x20, 0x30, 0x40 };
    bool sent = opt1.sendPacket(FaceSlot::FACE_POS_X, 2, 0x05, msg_data, sizeof(msg_data));
    assert(sent == true);
    assert(opt1.getTxPacketCount() == 1);

    // Simulate loopback or incoming peer beacon from Robot 2 on Face +X
    // Peer packet: [SRC=2, DST=1, TYPE=0x01 (Heartbeat), PAYLOAD={0x0A, 0x0B}]
    uint8_t peer_payload[] = { 0x0A, 0x0B };
    opt1.simulateReceivePacket(FaceSlot::FACE_POS_X, 2, 1, 0x01, peer_payload, sizeof(peer_payload));

    // Update driver to process RX queue
    opt1.update(0.01f);

    // Face +X should now be linked with neighbor ID 2!
    assert(opt1.isFaceLinked(FaceSlot::FACE_POS_X) == true);
    assert(opt1.getNeighborId(FaceSlot::FACE_POS_X) == 2);
    assert(opt1.getRxPacketCount() == 1);

    printf("  -> PASS: Optical packet TX/RX and neighbor link establishment verified.\n");
}

void test_optical_link_timeout_and_disconnect() {
    printf("[TDD Optical] Running test_optical_link_timeout_and_disconnect...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    OpticalMeshDriver opt(8, 9, 15, 1);
    opt.init();
    opt.start();

    // Establish link on Face -Y (Slot 3) with Robot 4
    uint8_t payload[] = { 0x01 };
    opt.simulateReceivePacket(FaceSlot::FACE_NEG_Y, 4, 1, 0x01, payload, 1);
    opt.update(0.01f);
    assert(opt.isFaceLinked(FaceSlot::FACE_NEG_Y) == true);

    // Advance time past heartbeat timeout (1.0s)
    opt.update(1.2f);

    // Link must automatically disconnect due to heartbeat loss!
    assert(opt.isFaceLinked(FaceSlot::FACE_NEG_Y) == false);
    assert(opt.getNeighborId(FaceSlot::FACE_NEG_Y) == 0);

    printf("  -> PASS: Optical link heartbeat timeout and auto-disconnect verified.\n");
}

int main() {
    printf("====================================================\n");
    printf("  TDD Suite: 6-Face Optical Mesh Transceiver Driver  \n");
    printf("====================================================\n");
    test_optical_init_and_self_test();
    test_cobs_framing_and_crc16();
    test_optical_packet_transmission_and_reception();
    test_optical_link_timeout_and_disconnect();
    printf(">> ALL OPTICAL TESTS PASSED SUCCESSFULLY! <<\n");
    return 0;
}
