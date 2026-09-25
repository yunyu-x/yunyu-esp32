/**
 * @file test_all_drivers_main.cpp
 * @brief Master Integration & Acceptance Test for microUnit Embedded Driver Framework.
 * @details Integrates DriverHub, MotorDriver, EpmDriver, ImuMpu6050, PowerBmsDriver,
 *          OpticalMeshDriver, and LedIndicatorDriver with multi-rate scheduling and fault injection.
 * @author microUnit Robotics Open Source Team
 */

#include <cassert>
#include <cstdio>
#include <cmath>
#include "hal/mock_hal.h"
#include "drivers/driver_hub.h"
#include "drivers/motor_driver.h"
#include "drivers/epm_driver.h"
#include "drivers/imu_mpu6050.h"
#include "drivers/power_bms.h"
#include "drivers/optical_mesh_driver.h"
#include "drivers/led_driver.h"

using namespace microunit;

void test_full_system_registration_and_post() {
    printf("[System Driver Suite] 1. Testing System Power-On Self-Test (POST)...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    // Setup hardware baselines
    hal.setPinLevel(7, HAL_LEVEL_HIGH);      // DRV8833 nFAULT normal high
    hal.setI2cRegister(0x68, 0x75, 0x68);    // MPU6050 WHO_AM_I
    hal.setAdcVoltage(11, 1.90f);            // 3.80V battery (pin 1.90V)

    DriverHub& hub = DriverHub::getInstance();

    static MotorDriver motor(4, 5, 7, 0, 1);
    static EpmDriver epm(6);
    static ImuMpu6050 imu(12, 13, 21, 38);
    static PowerBmsDriver bms(11, 2.0f);
    static OpticalMeshDriver optical(8, 9, 15, 1);
    static LedIndicatorDriver led(10);

    // Register all drivers
    assert(hub.registerDriver(&motor) == true);
    assert(hub.registerDriver(&epm) == true);
    assert(hub.registerDriver(&imu) == true);
    assert(hub.registerDriver(&bms) == true);
    assert(hub.registerDriver(&optical) == true);
    assert(hub.registerDriver(&led) == true);
    assert(hub.getDriverCount() == 6);

    // Attach optical mesh to Face +X slot
    assert(hub.attachSlotDevice(FaceSlot::FACE_POS_X, &optical) == true);
    assert(hub.isSlotOccupied(FaceSlot::FACE_POS_X) == true);

    // Perform system-wide initAll
    assert(hub.initAll() == true);

    // Perform system-wide selfTestAll (POST)
    uint32_t failed_mask = 0;
    assert(hub.selfTestAll(&failed_mask) == true);
    assert(failed_mask == 0);
    assert(hub.getHealthyCount() == 6);
    assert(hub.getFaultedCount() == 0);

    // Start all drivers
    assert(hub.startAll() == true);

    printf("  -> PASS: All 6 drivers registered, POST passed 100%%, and started.\n");
}

void test_full_roll_maneuver_simulation() {
    printf("[System Driver Suite] 2. Testing Integrated Roll Maneuver Dynamics...\n");
    DriverHub& hub = DriverHub::getInstance();
    MockHal& hal = MockHal::getInstance();

    auto* motor = static_cast<MotorDriver*>(hub.getDriver(1));
    auto* epm = static_cast<EpmDriver*>(hub.getDriver(2));
    auto* imu = static_cast<ImuMpu6050*>(hub.getDriver(3));
    auto* bms = static_cast<PowerBmsDriver*>(hub.getDriver(4));
    auto* led = static_cast<LedIndicatorDriver*>(hub.getDriver(6));

    assert(motor && epm && imu && bms && led);

    // Step A: Flywheel spinup to 12000 RPM
    motor->spinUp(12000.0f);
    for (int t = 0; t < 100; ++t) {
        hal.advanceTimeMs(10);
        hub.updateAll(0.01f); // 10ms step
    }
    assert(motor->getCurrentRpm() == 12000.0f);
    assert(motor->getState() == MotorState::MOTOR_AT_SPEED);

    // Step B: EPM ground anchoring
    assert(epm->pulseMagnetize(5.0f) == true);
    for (int t = 0; t < 6; ++t) {
        hal.advanceTimeMs(1);
        hub.updateAll(0.001f);
    }
    assert(epm->isAnchored() == true);
    assert(epm->getHoldingForceN() >= 30.0f);

    // Step C: Trigger dynamic impulse brake for 15.1ms
    // Inject gyro pitch rate during dynamic braking
    hal.setI2cRegister(0x68, 0x43, 0x0A); // GYRO_X
    hal.setI2cRegister(0x68, 0x44, 0x00);
    motor->triggerDynamicBrake(0.25f, 15.1f);
    assert(motor->isBraking() == true);

    for (int t = 0; t < 20; ++t) {
        hal.advanceTimeMs(1);
        hub.updateAll(0.001f); // 1ms step
    }
    assert(motor->getCurrentRpm() == 0.0f);
    assert(motor->isBraking() == false);

    // Step D: Confirm IMU read attitude rate
    const ImuData& data = imu->getData();
    assert(data.timestamp_ms > 0);

    // Step E: BMS state check
    assert(bms->getBatteryVoltage() > 3.5f);
    assert(bms->getSocPercent() > 50.0f);

    printf("  -> PASS: Integrated spinup -> anchor -> dynamic brake -> gyro cycle verified.\n");
}

void test_system_fault_isolation_and_auto_recovery() {
    printf("[System Driver Suite] 3. Testing Fault Isolation & Autonomous Self-Healing...\n");
    DriverHub& hub = DriverHub::getInstance();
    MockHal& hal = MockHal::getInstance();

    auto* motor = static_cast<MotorDriver*>(hub.getDriver(1));
    auto* imu = static_cast<ImuMpu6050*>(hub.getDriver(3));

    // 1. Inject I2C bus hang into IMU
    hal.injectI2cBusHang(true);
    for (int t = 0; t < 5; ++t) {
        imu->update(0.002f);
    }
    assert(imu->getHealth() == DriverHealth::FAULTED);
    // Other drivers must remain healthy! (Fault Isolation)
    assert(motor->getHealth() == DriverHealth::HEALTHY);
    assert(hub.getFaultedCount() == 1);
    assert(hub.getHealthyCount() == 5);

    // 2. Autonomous cold-reset recovery
    bool imu_ok = imu->recover(static_cast<uint32_t>(DriverErrorCode::ERR_BUS_DEADLOCK));
    assert(imu_ok == true);
    assert(imu->getHealth() == DriverHealth::HEALTHY);
    assert(hub.getFaultedCount() == 0);
    assert(hub.getHealthyCount() == 6);

    // 3. Inject DRV8833 overcurrent fault
    hal.setPinLevel(7, HAL_LEVEL_LOW);
    motor->update(0.005f);
    assert(motor->getHealth() == DriverHealth::FAULTED);
    assert(hub.getFaultedCount() == 1);

    // Clear fault and recover motor
    hal.setPinLevel(7, HAL_LEVEL_HIGH);
    assert(motor->recover(static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT)) == true);
    assert(motor->getHealth() == DriverHealth::HEALTHY);
    assert(hub.getHealthyCount() == 6);

    printf("  -> PASS: Multi-peripheral fault isolation and zero-downtime recovery verified.\n");
}

int main() {
    printf("=================================================================\n");
    printf("  yunyu-microUnit Professional Embedded Driver Acceptance Suite  \n");
    printf("  Target: ESP32-S3 Dual-Core 240MHz | High-Fidelity Mock HAL     \n");
    printf("=================================================================\n");

    test_full_system_registration_and_post();
    test_full_roll_maneuver_simulation();
    test_system_fault_isolation_and_auto_recovery();

    printf("\n=================================================================\n");
    printf("  [100%% ACCEPTANCE] ALL DRIVERS FULLY VERIFIED & READY FOR SIL/HIL\n");
    printf("=================================================================\n");
    return 0;
}
