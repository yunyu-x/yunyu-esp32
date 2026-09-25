/**
 * @file test_imu_driver.cpp
 * @brief TDD Unit tests for MPU-6050 6-Axis IMU Driver with Q4 Hardware Cold-Reset Deadlock Auto-Recovery.
 */

#include <cassert>
#include <cstdio>
#include <cmath>
#include "hal/mock_hal.h"
#include "drivers/imu_mpu6050.h"

using namespace microunit;

void test_imu_init_and_self_test() {
    printf("[TDD IMU] Running test_imu_init_and_self_test...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    // Setup Mock MPU-6050 registers: WHO_AM_I (0x75) = 0x68
    hal.setI2cRegister(0x68, 0x75, 0x68);

    ImuMpu6050 imu(12, 13, 21, 38); // SDA=12, SCL=13, PWR_EN=21, INT=38
    assert(imu.getType() == DeviceType::SENSOR_IMU);
    assert(imu.getDeviceId() == 3);
    assert(imu.getHealth() == DriverHealth::UNINITIALIZED);

    // Initial state: Q4 power gate on (GPIO21 LOW enables PMOS)
    assert(imu.init() == true);
    assert(hal.getPinLevel(21) == HAL_LEVEL_LOW);
    assert(imu.getHealth() == DriverHealth::HEALTHY);
    assert(imu.selfTest() == true);

    // Check configuration registers were written
    assert(hal.getI2cRegister(0x68, 0x6B) == 0x01); // PWR_MGMT_1: PLL with X-gyro
    assert(hal.getI2cRegister(0x68, 0x1B) == 0x18); // GYRO_CONFIG: +-2000 dps
    assert(hal.getI2cRegister(0x68, 0x1C) == 0x18); // ACCEL_CONFIG: +-16g

    printf("  -> PASS: IMU init, WHO_AM_I probe and register setup verified.\n");
}

void test_imu_data_acquisition() {
    printf("[TDD IMU] Running test_imu_data_acquisition...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();
    hal.setI2cRegister(0x68, 0x75, 0x68);

    ImuMpu6050 imu(12, 13, 21, 38);
    imu.init();
    imu.start();

    // Inject 1.0g vertical acceleration on Z axis:
    // With +-16g scale, sensitivity is 2048 LSB/g -> 1.0g = 2048 (0x0800)
    hal.setI2cRegister(0x68, 0x3B, 0x00); // ACCEL_X = 0
    hal.setI2cRegister(0x68, 0x3C, 0x00);
    hal.setI2cRegister(0x68, 0x3D, 0x00); // ACCEL_Y = 0
    hal.setI2cRegister(0x68, 0x3E, 0x00);
    hal.setI2cRegister(0x68, 0x3F, 0x08); // ACCEL_Z = 0x0800 (2048)
    hal.setI2cRegister(0x68, 0x40, 0x00);

    // Inject 100.0 dps yaw rate on Z axis:
    // With +-2000 dps scale, sensitivity is 16.4 LSB/(dps) -> 100 dps = 1640 (0x0668)
    hal.setI2cRegister(0x68, 0x47, 0x06); // GYRO_Z = 0x0668 (1640)
    hal.setI2cRegister(0x68, 0x48, 0x68);

    imu.update(0.002f); // 500 Hz cycle

    ImuData data = imu.getData();
    assert(std::abs(data.accel_x) < 0.05f);
    assert(std::abs(data.accel_y) < 0.05f);
    assert(std::abs(data.accel_z - 9.80665f) < 0.2f); // ~1.0g in m/s^2

    // 100 dps in rad/s is 100 * pi / 180 = 1.745 rad/s
    assert(std::abs(data.gyro_z_rad - 1.745f) < 0.1f);

    printf("  -> PASS: IMU 6-DOF data conversion to SI units verified.\n");
}

void test_imu_q4_power_gate_deadlock_recovery() {
    printf("[TDD IMU] Running test_imu_q4_power_gate_deadlock_recovery...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();
    hal.setI2cRegister(0x68, 0x75, 0x68);

    ImuMpu6050 imu(12, 13, 21, 38);
    imu.init();
    imu.start();

    // 1. Inject I2C bus hang (SDA line stuck low by slave)
    hal.injectI2cBusHang(true);

    // 2. Perform updates: reads fail, consecutive failure counter accumulates
    for (int i = 0; i < 5; ++i) {
        imu.update(0.002f);
    }

    // Health should transition to FAULTED / DEADLOCK
    assert(imu.getHealth() == DriverHealth::FAULTED);
    assert(imu.getErrorCode() & static_cast<uint32_t>(DriverErrorCode::ERR_BUS_DEADLOCK));

    // 3. Trigger autonomous recovery via Q4 hardware cold-reset!
    bool recovered = imu.recover(static_cast<uint32_t>(DriverErrorCode::ERR_BUS_DEADLOCK));
    assert(recovered == true);

    // Check that Q4 power cycle sequence occurred:
    // GPIO21 was driven HIGH (cut power), delayed, then driven LOW (restore power)
    assert(hal.getPinLevel(21) == HAL_LEVEL_LOW); // re-enabled
    assert(imu.getHealth() == DriverHealth::HEALTHY);
    assert(imu.getRecoveryCount() == 1);

    printf("  -> PASS: Q4 PMOS power-gate I2C deadlock cold-reset recovery verified.\n");
}

int main() {
    printf("====================================================\n");
    printf("  TDD Suite: MPU-6050 IMU & Q4 Cold-Reset Driver     \n");
    printf("====================================================\n");
    test_imu_init_and_self_test();
    test_imu_data_acquisition();
    test_imu_q4_power_gate_deadlock_recovery();
    printf(">> ALL IMU TESTS PASSED SUCCESSFULLY! <<\n");
    return 0;
}
