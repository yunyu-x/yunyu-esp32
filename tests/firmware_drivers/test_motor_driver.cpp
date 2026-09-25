/**
 * @file test_motor_driver.cpp
 * @brief TDD Unit tests for DRV8833 Flywheel Motor Driver.
 */

#include <cassert>
#include <cstdio>
#include "hal/mock_hal.h"
#include "drivers/motor_driver.h"

using namespace microunit;

void test_motor_init_and_self_test() {
    printf("[TDD Motor] Running test_motor_init_and_self_test...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    // Default: nFAULT is pulled high (normal operation)
    hal.setPinLevel(7, HAL_LEVEL_HIGH);

    MotorDriver motor(4, 5, 7, 0, 1);
    assert(motor.getType() == DeviceType::ACTUATOR_MOTOR);
    assert(motor.getDeviceId() == 1);
    assert(motor.getHealth() == DriverHealth::UNINITIALIZED);

    assert(motor.init() == true);
    assert(motor.getHealth() == DriverHealth::HEALTHY);
    assert(motor.selfTest() == true);

    // Initial state should be idle and stopped
    assert(motor.isRunning() == false);
    assert(motor.getCurrentRpm() == 0.0f);
    assert(motor.getState() == MotorState::MOTOR_IDLE);

    printf("  -> PASS: Motor init and self-test verified.\n");
}

void test_motor_spinup_ramp_and_steady() {
    printf("[TDD Motor] Running test_motor_spinup_ramp_and_steady...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();
    hal.setPinLevel(7, HAL_LEVEL_HIGH);

    MotorDriver motor(4, 5, 7, 0, 1);
    motor.init();
    motor.start();
    assert(motor.isRunning() == true);

    // Spin up to 15,000 RPM
    motor.spinUp(15000.0f);
    assert(motor.getState() == MotorState::MOTOR_SPINNING_UP);

    // Update for 0.5s -> at 15,000 RPM/s ramp, should be around 7500 RPM
    motor.update(0.5f);
    float rpm_mid = motor.getCurrentRpm();
    assert(rpm_mid >= 7000.0f && rpm_mid <= 8000.0f);
    assert(motor.getState() == MotorState::MOTOR_SPINNING_UP);

    // Update for another 0.6s -> should reach 15,000 RPM and transition to MOTOR_AT_SPEED
    motor.update(0.6f);
    assert(motor.getCurrentRpm() == 15000.0f);
    assert(motor.getState() == MotorState::MOTOR_AT_SPEED);

    printf("  -> PASS: Motor soft-start ramp to 15,000 RPM verified.\n");
}

void test_motor_dynamic_braking() {
    printf("[TDD Motor] Running test_motor_dynamic_braking...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();
    hal.setPinLevel(7, HAL_LEVEL_HIGH);

    MotorDriver motor(4, 5, 7, 0, 1);
    motor.init();
    motor.start();
    motor.spinUp(12000.0f);
    motor.update(1.0f); // Reach target speed
    assert(motor.getCurrentRpm() == 12000.0f);

    // Trigger Dynamic Braking for 15.1 ms
    motor.triggerDynamicBrake(0.25f, 15.1f);
    assert(motor.getState() == MotorState::MOTOR_IMPULSE_BRAKING);
    assert(motor.isBraking() == true);

    // Both IN1 and IN2 must be 1023 (low-side FETs shorted for regenerative counter-torque)
    assert(hal.getPwmDuty(0) == 1023);
    assert(hal.getPwmDuty(1) == 1023);

    // Advance time past brake duration
    motor.update(0.016f);
    assert(motor.getCurrentRpm() == 0.0f);
    assert(motor.getState() == MotorState::MOTOR_COASTING || motor.getState() == MotorState::MOTOR_IDLE);

    printf("  -> PASS: Motor dynamic braking short-circuit verified.\n");
}

void test_motor_fault_protection_and_recovery() {
    printf("[TDD Motor] Running test_motor_fault_protection_and_recovery...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();
    hal.setPinLevel(7, HAL_LEVEL_HIGH);

    MotorDriver motor(4, 5, 7, 0, 1);
    motor.init();
    motor.start();
    motor.spinUp(10000.0f);
    motor.update(0.1f);

    // Inject hardware nFAULT (active-low overcurrent/overtemperature alert from DRV8833)
    hal.setPinLevel(7, HAL_LEVEL_LOW);
    motor.update(0.005f); // 5ms update cycle

    // Motor should catch fault, cut PWM immediately, and enter FAULTED state
    assert(motor.getHealth() == DriverHealth::FAULTED);
    assert(hal.getPwmDuty(0) == 0);
    assert(hal.getPwmDuty(1) == 0);
    assert(motor.getErrorCode() & static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT));

    // Restore nFAULT to normal and attempt recovery
    hal.setPinLevel(7, HAL_LEVEL_HIGH);
    bool recovered = motor.recover(static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT));
    assert(recovered == true);
    assert(motor.getHealth() == DriverHealth::HEALTHY);

    printf("  -> PASS: DRV8833 nFAULT detection and recovery verified.\n");
}

int main() {
    printf("====================================================\n");
    printf("  TDD Suite: DRV8833 Flywheel Motor Driver           \n");
    printf("====================================================\n");
    test_motor_init_and_self_test();
    test_motor_spinup_ramp_and_steady();
    test_motor_dynamic_braking();
    test_motor_fault_protection_and_recovery();
    printf(">> ALL MOTOR TESTS PASSED SUCCESSFULLY! <<\n");
    return 0;
}
