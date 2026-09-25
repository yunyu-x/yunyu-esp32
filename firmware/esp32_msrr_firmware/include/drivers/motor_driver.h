/**
 * @file motor_driver.h
 * @brief Professional DRV8833 Dual H-Bridge & Flywheel Driver for microUnit.
 * @details Implements soft-start PWM ramp, dynamic counter-electromotive braking,
 *          nFAULT hardware alert detection, and unified IDeviceDriver interface.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "drivers/driver_interface.h"
#include "hal/hal_interface.h"

namespace microunit {

enum class MotorState : uint8_t {
    MOTOR_IDLE = 0,
    MOTOR_SPINNING_UP,
    MOTOR_AT_SPEED,
    MOTOR_IMPULSE_BRAKING,
    MOTOR_COASTING,
    MOTOR_FAULT
};

class MotorDriver : public IDeviceDriver {
public:
    static constexpr float DEFAULT_MAX_RPM = 18000.0f;
    static constexpr float DEFAULT_RAMP_ACCEL = 15000.0f; // RPM/s
    static constexpr float ROTOR_INERTIA = 2.02e-6f;      // kg*m^2

    MotorDriver(uint8_t pin_in1 = 4, uint8_t pin_in2 = 5, uint8_t pin_nfault = 7,
                uint8_t pwm_ch1 = 0, uint8_t pwm_ch2 = 1);
    ~MotorDriver() override = default;

    // IDeviceDriver Implementation
    const char* getName() const override { return "DRV8833_MotorDriver"; }
    DeviceType getType() const override { return DeviceType::ACTUATOR_MOTOR; }
    uint8_t getDeviceId() const override { return 1; }

    bool init() override;
    bool start() override;
    void stop() override;
    void update(float dt_seconds) override;

    bool selfTest() override;
    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _error_code; }
    bool recover(uint32_t fault_mask) override;
    bool isRunning() const override { return _running; }

    // Actuation Methods
    void spinUp(float target_rpm);
    void triggerDynamicBrake(float torque_nm, float duration_ms);
    void stopCoast();

    // Telemetry & State
    float getCurrentRpm() const { return _current_rpm; }
    float getTargetRpm() const { return _target_rpm; }
    MotorState getState() const { return _state; }
    bool isBraking() const { return _state == MotorState::MOTOR_IMPULSE_BRAKING; }

private:
    uint8_t _pin_in1;
    uint8_t _pin_in2;
    uint8_t _pin_nfault;
    uint8_t _pwm_ch1;
    uint8_t _pwm_ch2;

    DriverHealth _health;
    uint32_t _error_code;
    bool _running;

    MotorState _state;
    float _target_rpm;
    float _current_rpm;
    float _brake_timer_ms;
    float _brake_duration_ms;
    float _brake_torque_nm;

    void setPwmDrive(uint32_t pwm1, uint32_t pwm2);
    void checkHardwareFault();
};

} // namespace microunit
