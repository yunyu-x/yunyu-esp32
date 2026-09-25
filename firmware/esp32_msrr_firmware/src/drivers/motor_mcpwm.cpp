/**
 * @file motor_mcpwm.cpp
 * @brief DRV8833 H-Bridge Flywheel Motor Implementation with Dynamic Braking.
 */

#include "drivers/motor_mcpwm.h"

// MCPWM / LEDC configuration parameters
static const int LEDC_CH_IN1 = 0;
static const int LEDC_CH_IN2 = 1;
static const int LEDC_FREQ = 25000; // 25 kHz inaudible PWM
static const int LEDC_RES = 10;     // 10-bit resolution (0-1023)

FlywheelMotorDriver::FlywheelMotorDriver()
    : _state(MOTOR_IDLE), _target_rpm(0.0f), _current_rpm(0.0f),
      _brake_timer_ms(0.0f), _brake_duration_ms(0.0f) {}

void FlywheelMotorDriver::init() {
    pinMode(PIN_MOTOR_IN1, OUTPUT);
    pinMode(PIN_MOTOR_IN2, OUTPUT);

    // Initialize LEDC PWM channels
    ledcSetup(LEDC_CH_IN1, LEDC_FREQ, LEDC_RES);
    ledcSetup(LEDC_CH_IN2, LEDC_FREQ, LEDC_RES);
    ledcAttachPin(PIN_MOTOR_IN1, LEDC_CH_IN1);
    ledcAttachPin(PIN_MOTOR_IN2, LEDC_CH_IN2);

    stopCoast();
}

void FlywheelMotorDriver::setPwmDrive(int pwm_in1, int pwm_in2) {
    ledcWrite(LEDC_CH_IN1, constrain(pwm_in1, 0, 1023));
    ledcWrite(LEDC_CH_IN2, constrain(pwm_in2, 0, 1023));
}

void FlywheelMotorDriver::spinUp(float target_rpm) {
    _target_rpm = target_rpm;
    _state = MOTOR_SPINNING_UP;
}

void FlywheelMotorDriver::triggerDynamicBrake(float torque_nm, float duration_ms) {
    _brake_duration_ms = duration_ms;
    _brake_timer_ms = 0.0f;
    _state = MOTOR_IMPULSE_BRAKING;

    // DRV8833 Dynamic Brake Mode: Both IN1 and IN2 HIGH
    // This shorts the motor terminals through the low-side FETs,
    // producing immediate counter-electromotive braking torque.
    setPwmDrive(1023, 1023);
}

void FlywheelMotorDriver::stopCoast() {
    _state = MOTOR_COASTING;
    _target_rpm = 0.0f;
    // Coast mode: Both IN1 and IN2 LOW (High-Z)
    setPwmDrive(0, 0);
}

void FlywheelMotorDriver::update(float dt) {
    switch (_state) {
        case MOTOR_IDLE:
        case MOTOR_COASTING:
            if (_current_rpm > 10.0f) {
                _current_rpm -= 500.0f * dt; // Aerodynamic + bearing drag
                if (_current_rpm < 0.0f) _current_rpm = 0.0f;
            }
            break;

        case MOTOR_SPINNING_UP: {
            float ramp_accel = 15000.0f; // RPM/s ramp rate (soft start for battery protection)
            _current_rpm += ramp_accel * dt;
            if (_current_rpm >= _target_rpm) {
                _current_rpm = _target_rpm;
                _state = MOTOR_AT_SPEED;
            }
            // Proportional PWM throttle for spinup
            int pwm_val = (int)((_current_rpm / 14000.0f) * 1023.0f);
            setPwmDrive(pwm_val, 0);
            break;
        }

        case MOTOR_AT_SPEED: {
            // Steady state sustaining PWM
            int pwm_val = (int)((_target_rpm / 14000.0f) * 850.0f);
            setPwmDrive(pwm_val, 0);
            break;
        }

        case MOTOR_IMPULSE_BRAKING: {
            _brake_timer_ms += dt * 1000.0f;
            // Immediate deceleration curve
            float d_rpm = (BRAKE_TORQUE_MAX_NM / FLYWHEEL_ROTOR_INERTIA_YY) * (60.0f / (2.0f * 3.14159f)) * dt;
            _current_rpm -= d_rpm;
            if (_current_rpm <= 0.0f || _brake_timer_ms >= _brake_duration_ms) {
                _current_rpm = 0.0f;
                stopCoast();
            }
            break;
        }
    }
}
