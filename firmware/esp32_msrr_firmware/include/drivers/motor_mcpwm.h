/**
 * @file motor_mcpwm.h
 * @brief DRV8833 H-Bridge & Maxon EC-16 Flywheel Driver with Hardware PWM and Dynamic Braking.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <Arduino.h>
#include "config.h"

enum MotorState {
    MOTOR_IDLE,
    MOTOR_SPINNING_UP,
    MOTOR_AT_SPEED,
    MOTOR_IMPULSE_BRAKING,
    MOTOR_COASTING
};

class FlywheelMotorDriver {
public:
    FlywheelMotorDriver();
    void init();
    void spinUp(float target_rpm);
    void triggerDynamicBrake(float torque_nm, float duration_ms);
    void stopCoast();
    void update(float dt);

    float getCurrentRpm() const { return _current_rpm; }
    MotorState getState() const { return _state; }
    bool isBraking() const { return _state == MOTOR_IMPULSE_BRAKING; }

private:
    MotorState _state;
    float _target_rpm;
    float _current_rpm;
    float _brake_timer_ms;
    float _brake_duration_ms;

    void setPwmDrive(int pwm_in1, int pwm_in2);
};
