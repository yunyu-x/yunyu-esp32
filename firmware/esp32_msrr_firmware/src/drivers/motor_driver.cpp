/**
 * @file motor_driver.cpp
 * @brief Implementation of DRV8833 Dual H-Bridge & Flywheel Driver.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/motor_driver.h"
#include <algorithm>
#include <cmath>

namespace microunit {

MotorDriver::MotorDriver(uint8_t pin_in1, uint8_t pin_in2, uint8_t pin_nfault,
                         uint8_t pwm_ch1, uint8_t pwm_ch2)
    : _pin_in1(pin_in1), _pin_in2(pin_in2), _pin_nfault(pin_nfault),
      _pwm_ch1(pwm_ch1), _pwm_ch2(pwm_ch2),
      _health(DriverHealth::UNINITIALIZED), _error_code(0), _running(false),
      _state(MotorState::MOTOR_IDLE), _target_rpm(0.0f), _current_rpm(0.0f),
      _brake_timer_ms(0.0f), _brake_duration_ms(0.0f), _brake_torque_nm(0.25f) {}

bool MotorDriver::init() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_INIT_FAILED);
        return false;
    }

    hal->pin_mode(_pin_in1, HAL_PIN_OUTPUT);
    hal->pin_mode(_pin_in2, HAL_PIN_OUTPUT);
    hal->pin_mode(_pin_nfault, HAL_PIN_INPUT_PULLUP);

    // 25 kHz, 10-bit PWM setup
    hal->pwm_setup(_pwm_ch1, 25000, 10);
    hal->pwm_setup(_pwm_ch2, 25000, 10);
    hal->pwm_attach_pin(_pin_in1, _pwm_ch1);
    hal->pwm_attach_pin(_pin_in2, _pwm_ch2);

    stopCoast();

    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool MotorDriver::start() {
    if (_health == DriverHealth::FAULTED) {
        return false;
    }
    _running = true;
    return true;
}

void MotorDriver::stop() {
    stopCoast();
    _running = false;
}

void MotorDriver::setPwmDrive(uint32_t pwm1, uint32_t pwm2) {
    const HalInterface* hal = get_hal();
    if (hal) {
        hal->pwm_write(_pwm_ch1, pwm1 > 1023 ? 1023 : pwm1);
        hal->pwm_write(_pwm_ch2, pwm2 > 1023 ? 1023 : pwm2);
    }
}

void MotorDriver::checkHardwareFault() {
    const HalInterface* hal = get_hal();
    if (!hal) return;

    // nFAULT pin is active LOW
    if (hal->digital_read(_pin_nfault) == HAL_LEVEL_LOW) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT);
        _state = MotorState::MOTOR_FAULT;
        setPwmDrive(0, 0); // Safety cutoff
    }
}

bool MotorDriver::selfTest() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        return false;
    }

    // Check nFAULT is high under normal idle
    if (hal->digital_read(_pin_nfault) == HAL_LEVEL_LOW) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT);
        return false;
    }

    _health = DriverHealth::HEALTHY;
    return true;
}

bool MotorDriver::recover(uint32_t fault_mask) {
    const HalInterface* hal = get_hal();
    if (!hal) return false;

    // If nFAULT is still LOW, hardware cannot be recovered
    if (hal->digital_read(_pin_nfault) == HAL_LEVEL_LOW) {
        return false;
    }

    _error_code &= ~fault_mask;
    if (_error_code == 0) {
        _health = DriverHealth::HEALTHY;
        _state = MotorState::MOTOR_IDLE;
        stopCoast();
        return true;
    }
    return false;
}

void MotorDriver::spinUp(float target_rpm) {
    if (_health == DriverHealth::FAULTED) return;
    _target_rpm = std::min(target_rpm, DEFAULT_MAX_RPM);
    _state = MotorState::MOTOR_SPINNING_UP;
}

void MotorDriver::triggerDynamicBrake(float torque_nm, float duration_ms) {
    if (_health == DriverHealth::FAULTED) return;

    _brake_torque_nm = torque_nm;
    _brake_duration_ms = duration_ms;
    _brake_timer_ms = 0.0f;
    _state = MotorState::MOTOR_IMPULSE_BRAKING;

    // Dynamic Braking: Both inputs HIGH (1023)
    setPwmDrive(1023, 1023);
}

void MotorDriver::stopCoast() {
    _target_rpm = 0.0f;
    _state = (_current_rpm > 0.0f) ? MotorState::MOTOR_COASTING : MotorState::MOTOR_IDLE;
    // Coast mode: Both inputs LOW
    setPwmDrive(0, 0);
}

void MotorDriver::update(float dt_seconds) {
    checkHardwareFault();
    if (_health == DriverHealth::FAULTED) {
        return;
    }

    switch (_state) {
        case MotorState::MOTOR_IDLE:
        case MotorState::MOTOR_COASTING:
            if (_current_rpm > 5.0f) {
                _current_rpm -= 500.0f * dt_seconds; // Aerodynamic & friction decay
                if (_current_rpm < 0.0f) _current_rpm = 0.0f;
            } else {
                _current_rpm = 0.0f;
                _state = MotorState::MOTOR_IDLE;
            }
            setPwmDrive(0, 0);
            break;

        case MotorState::MOTOR_SPINNING_UP: {
            _current_rpm += DEFAULT_RAMP_ACCEL * dt_seconds;
            if (_current_rpm >= _target_rpm) {
                _current_rpm = _target_rpm;
                _state = MotorState::MOTOR_AT_SPEED;
            }
            uint32_t pwm_val = static_cast<uint32_t>((_current_rpm / DEFAULT_MAX_RPM) * 1023.0f);
            setPwmDrive(pwm_val, 0);
            break;
        }

        case MotorState::MOTOR_AT_SPEED: {
            uint32_t pwm_val = static_cast<uint32_t>((_target_rpm / DEFAULT_MAX_RPM) * 850.0f);
            setPwmDrive(pwm_val, 0);
            break;
        }

        case MotorState::MOTOR_IMPULSE_BRAKING: {
            _brake_timer_ms += dt_seconds * 1000.0f;
            // Impulse counter-torque decel: d_rpm = (tau / J) * (60 / 2pi) * dt
            float decel_rpm_s = (_brake_torque_nm / ROTOR_INERTIA) * (60.0f / (2.0f * 3.14159265f));
            _current_rpm -= decel_rpm_s * dt_seconds;

            if (_current_rpm <= 0.0f || _brake_timer_ms >= _brake_duration_ms) {
                _current_rpm = 0.0f;
                stopCoast();
            } else {
                setPwmDrive(1023, 1023);
            }
            break;
        }

        case MotorState::MOTOR_FAULT:
            setPwmDrive(0, 0);
            break;
    }
}

} // namespace microunit
