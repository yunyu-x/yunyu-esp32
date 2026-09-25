/**
 * @file roll_fsm.h
 * @brief 6-Phase Finite State Machine for Ground-Anchored Inertial Rolling Locomotion.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <Arduino.h>
#include "config.h"
#include "drivers/motor_mcpwm.h"
#include "drivers/epm_driver.h"
#include "filters/attitude_ekf.h"

enum RollState {
    FSM_IDLE,
    FSM_ANCHOR_PREPARE,
    FSM_SPINUP,
    FSM_IMPULSE_BRAKE,
    FSM_ROTATING,
    FSM_LATCH_LANDING
};

class RollFsmController {
public:
    RollFsmController(FlywheelMotorDriver* motor, EpmDriver* epm, AttitudeEstimator* imu);
    void init();
    bool triggerRollManeuver(int direction_sign = 1); // +1: Forward Roll, -1: Backward Roll
    void update(float dt);

    RollState getState() const { return _state; }
    const char* getStateName() const;
    int getSuccessfulRollCount() const { return _roll_count; }

private:
    RollState _state;
    FlywheelMotorDriver* _motor;
    EpmDriver* _epm;
    AttitudeEstimator* _imu;

    int _direction;
    float _state_timer_s;
    int _roll_count;

    void transitionTo(RollState next_state);
};
