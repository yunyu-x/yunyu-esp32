/**
 * @file multi_unit_fsm.cpp
 * @brief Implementation of Distributed Multi-Unit Cooperative Motion State Machine.
 * @author microUnit Robotics Open Source Team
 */

#include "controllers/multi_unit_fsm.h"
#include <math.h>

MultiUnitFSM::MultiUnitFSM(
    uint8_t local_id,
    MotorMCPWM* motor,
    EPMDriver* epm,
    AttitudeEKF* ekf,
    OpticalMeshRouter* router,
    bool is_solid_state
) : _id(local_id),
    _role(ROLE_STANDALONE),
    _state(MU_STATE_IDLE),
    _chain_index(0),
    _chain_length(3),
    _is_solid_state(is_solid_state),
    _timer_s(0.0f),
    _phase_duration_s(0.166f),
    _has_token(false),
    _motor(motor),
    _epm(epm),
    _ekf(ekf),
    _router(router)
{
}

void MultiUnitFSM::setRole(MultiUnitRole role, uint8_t chain_index, uint8_t chain_length) {
    _role = role;
    _chain_index = chain_index;
    _chain_length = (chain_length > 0) ? chain_length : 3;
    _state = MU_STATE_IDLE;
    _timer_s = 0.0f;
}

void MultiUnitFSM::triggerCooperativeMotion() {
    _state = MU_STATE_WAIT_TOKEN;
    _timer_s = 0.0f;
}

void MultiUnitFSM::update(float dt) {
    _timer_s += dt;

    switch (_role) {
        case ROLE_CLIMB_BASE:
            stepClimbBase(dt);
            break;
        case ROLE_CLIMB_MOVER:
            stepClimbMover(dt);
            break;
        case ROLE_CHAIN_NODE:
            stepChainNode(dt);
            break;
        default:
            break;
    }
}

void MultiUnitFSM::stepClimbBase(float dt) {
    // Unit A (Base): Must keep bottom EPM securely anchored (30N) to cancel out reaction overturning torque
    switch (_state) {
        case MU_STATE_IDLE:
            break;

        case MU_STATE_WAIT_TOKEN:
            // Ensure ground EPM is clamped
            _epm->pulseGroundEPM(true);
            _state = MU_STATE_SYNC_SPINUP;
            break;

        case MU_STATE_SYNC_SPINUP:
            // Base module stays static, waiting for mover's momentum impulse
            if (_timer_s > 0.050f) {
                _state = MU_STATE_IMPULSE_EXECUTE;
            }
            break;

        case MU_STATE_IMPULSE_EXECUTE:
            // Monitor base pitch angle; if base tilts > 5.0 deg, trigger safety warning
            if (fabsf(_ekf->getPitchDeg()) > 5.0f) {
                _state = MU_STATE_ABORT;
            } else if (_timer_s > 0.150f) {
                // Prepare top face (+Z) EPM for receiving climber
                _state = MU_STATE_APEX_DOCKING;
            }
            break;

        case MU_STATE_APEX_DOCKING:
            // Top face EPM is energized to catch mover
            _epm->pulseFaceEPM(FACE_Z_POS, true);
            _state = MU_STATE_TOUCHDOWN_LOCK;
            break;

        case MU_STATE_TOUCHDOWN_LOCK:
            _state = MU_STATE_CYCLE_COMPLETE;
            break;

        case MU_STATE_CYCLE_COMPLETE:
        case MU_STATE_ABORT:
            break;
    }
}

void MultiUnitFSM::stepClimbMover(float dt) {
    // Unit B (Mover): Executes push-pull couple or spin-up, unlatches from base face, and rolls onto top
    switch (_state) {
        case MU_STATE_IDLE:
            break;

        case MU_STATE_WAIT_TOKEN:
            if (_is_solid_state) {
                // 方案 B 纯电磁：无起旋过程，直接对接触面执行退磁脉冲 (2ms)
                _epm->pulseFaceEPM(FACE_X_NEG, false);
                _state = MU_STATE_PREPARE_UNLATCH;
                _timer_s = 0.0f;
            } else {
                // 方案 A 混合模式：起旋飞轮至 16,000 RPM
                if (_motor) {
                    _motor->setBrake(false);
                    _motor->setDuty(0.85f);
                }
                _state = MU_STATE_SYNC_SPINUP;
                _timer_s = 0.0f;
            }
            break;

        case MU_STATE_SYNC_SPINUP:
            if (_timer_s >= 0.050f) {
                // Send demag pulse to interface face (-X)
                _epm->pulseFaceEPM(FACE_X_NEG, false);
                _state = MU_STATE_PREPARE_UNLATCH;
            }
            break;

        case MU_STATE_PREPARE_UNLATCH:
            if (_is_solid_state) {
                // 方案 B 纯电磁：端面边缘微线圈脉冲力偶喷发 (2.5A, 20ms, 80 mN*m)
                _epm->pulseFaceEPM(FACE_X_NEG, true);
                _state = MU_STATE_IMPULSE_EXECUTE;
                _timer_s = 0.0f;
            } else {
                // 方案 A: Execute 15ms rapid brake pulse (0.22 N*m)
                if (_motor) _motor->setBrake(true);
                _state = MU_STATE_IMPULSE_EXECUTE;
                _timer_s = 0.0f;
            }
            break;

        case MU_STATE_IMPULSE_EXECUTE:
            if (_is_solid_state) {
                if (_timer_s >= 0.020f) {
                    _state = MU_STATE_APEX_DOCKING;
                }
            } else {
                if (_timer_s >= 0.015f) {
                    // Momentum dumped; entering ballistic over
                    if (_motor) {
                        _motor->setBrake(false);
                        _motor->setDuty(0.0f);
                    }
                    _state = MU_STATE_APEX_DOCKING;
                }
            }
            break;

        case MU_STATE_APEX_DOCKING:
            // Detect near 90 deg pitch via EKF
            if (_ekf->getPitchDeg() >= 75.0f) {
                // Fire bottom face (-Z) EPM to clamp onto base's +Z face
                _epm->pulseFaceEPM(FACE_Z_NEG, true);
                _state = MU_STATE_TOUCHDOWN_LOCK;
            }
            break;

        case MU_STATE_TOUCHDOWN_LOCK:
            _state = MU_STATE_CYCLE_COMPLETE;
            break;

        case MU_STATE_CYCLE_COMPLETE:
        case MU_STATE_ABORT:
            break;
    }
}

void MultiUnitFSM::stepChainNode(float dt) {
    // Multi-unit chain peristaltic wave progression
    float phase_start = (float)_chain_index * _phase_duration_s;
    float phase_end = phase_start + _phase_duration_s;
    float cycle_time = fmodf(_timer_s, _phase_duration_s * (float)_chain_length);

    if (cycle_time >= phase_start && cycle_time < phase_end) {
        // Our active motion phase: unlock bottom EPM and shift forward
        _epm->pulseGroundEPM(false);
        if (_is_solid_state) {
            // 纯电磁面面微动推拉
            _epm->pulseFaceEPM(FACE_X_POS, true);
        } else {
            if (_motor) _motor->setDuty(0.35f);
        }
    } else {
        // Stationary anchoring phase: clamp bottom EPM (30N) to act as rigid anchor
        _epm->pulseGroundEPM(true);
        if (_motor) _motor->setDuty(0.0f);
    }
}

void MultiUnitFSM::onOpticalMessageReceived(const OpticalMeshMessage_t& msg) {
    if (msg.msg_type == OPT_MSG_MOTION_SYNC_TRIG) {
        if (_role == ROLE_CLIMB_MOVER && _state == MU_STATE_SYNC_SPINUP) {
            _state = MU_STATE_PREPARE_UNLATCH;
            _timer_s = 0.0f;
        }
    } else if (msg.msg_type == OPT_MSG_EMERGENCY_STOP) {
        _state = MU_STATE_ABORT;
        _motor->setDuty(0.0f);
        _motor->setBrake(false);
    }
}
