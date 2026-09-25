/**
 * @file roll_fsm.cpp
 * @brief 6-Phase Finite State Machine Implementation for Inertial Rolling.
 */

#include "controllers/roll_fsm.h"

RollFsmController::RollFsmController(FlywheelMotorDriver* motor, EpmDriver* epm, AttitudeEstimator* imu)
    : _state(FSM_IDLE), _motor(motor), _epm(epm), _imu(imu),
      _direction(1), _state_timer_s(0.0f), _roll_count(0) {}

void RollFsmController::init() {
    _state = FSM_IDLE;
    _state_timer_s = 0.0f;
    _roll_count = 0;
}

const char* RollFsmController::getStateName() const {
    switch (_state) {
        case FSM_IDLE: return "IDLE";
        case FSM_ANCHOR_PREPARE: return "ANCHOR_PREPARE";
        case FSM_SPINUP: return "SPINUP";
        case FSM_IMPULSE_BRAKE: return "IMPULSE_BRAKE";
        case FSM_ROTATING: return "ROTATING";
        case FSM_LATCH_LANDING: return "LATCH_LANDING";
        default: return "UNKNOWN";
    }
}

void RollFsmController::transitionTo(RollState next_state) {
    _state = next_state;
    _state_timer_s = 0.0f;
}

bool RollFsmController::triggerRollManeuver(int direction_sign) {
    if (_state != FSM_IDLE) {
        return false; // Busy executing maneuver
    }
    _direction = (direction_sign >= 0) ? 1 : -1;
    transitionTo(FSM_ANCHOR_PREPARE);
    return true;
}

void RollFsmController::update(float dt) {
    _state_timer_s += dt;

    switch (_state) {
        case FSM_IDLE:
            // Standby mode
            break;

        case FSM_ANCHOR_PREPARE:
            // Phase 1: Activate ground EPM to eliminate contact slip (SF = 1.61)
            if (!_epm->isAnchored()) {
                _epm->pulseMagnetize(EPM_PULSE_DURATION_MS);
            }
            if (_state_timer_s >= (EPM_PULSE_DURATION_MS / 1000.0f) + 0.010f) {
                transitionTo(FSM_SPINUP);
            }
            break;

        case FSM_SPINUP:
            // Phase 2: Ramp flywheel to 12,000 RPM storing 1.60 J kinetic energy
            if (_motor->getState() != MOTOR_SPINNING_UP && _motor->getState() != MOTOR_AT_SPEED) {
                _motor->spinUp(FLYWHEEL_TARGET_RPM);
            }
            if (_motor->getState() == MOTOR_AT_SPEED || _state_timer_s >= 1.20f) {
                transitionTo(FSM_IMPULSE_BRAKE);
            }
            break;

        case FSM_IMPULSE_BRAKE:
            // Phase 3: Deliver 15.1ms dynamic braking pulse (0.25 N*m)
            if (!_motor->isBraking()) {
                _motor->triggerDynamicBrake(BRAKE_TORQUE_MAX_NM, BRAKE_PULSE_DURATION_MS);
            }
            if (_state_timer_s >= (BRAKE_PULSE_DURATION_MS / 1000.0f) + 0.005f) {
                transitionTo(FSM_ROTATING);
            }
            break;

        case FSM_ROTATING: {
            // Phase 4: Chassis rolls around pivot edge; check 45 deg crest crossing
            float current_roll = fabsf(_imu->getRollDeg());
            if (current_roll >= CRITICAL_TILT_ANGLE_DEG || _state_timer_s >= 0.120f) {
                // Crest cleared; demagnetize ground anchor to prevent pinning
                if (_epm->isAnchored()) {
                    _epm->pulseDemagnetize(EPM_PULSE_DURATION_MS);
                }
            }
            // Settle or full 90 deg rotation detection
            if (current_roll >= 85.0f || _state_timer_s >= 0.280f) {
                transitionTo(FSM_LATCH_LANDING);
            }
            break;
        }

        case FSM_LATCH_LANDING:
            // Phase 5: Settle on newly grounded face and lock landing anchor
            if (_state_timer_s >= 0.050f && !_epm->isAnchored()) {
                _epm->pulseMagnetize(EPM_PULSE_DURATION_MS);
            }
            if (_state_timer_s >= 0.150f) {
                _roll_count++;
                _motor->stopCoast();
                transitionTo(FSM_IDLE);
            }
            break;
    }
}
