/**
 * @file multi_unit_fsm.h
 * @brief Distributed Multi-Unit Cooperative Motion Controller (Climb, Leapfrog, Peristaltic Crawl)
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <stdint.h>
#include <stdbool.h>

#include "drivers/motor_mcpwm.h"
#include "drivers/epm_driver.h"
#include "filters/attitude_ekf.h"
#include "comm/optical_mesh_protocol.h"

enum MultiUnitRole {
    ROLE_STANDALONE = 0,
    ROLE_CLIMB_BASE = 1,
    ROLE_CLIMB_MOVER = 2,
    ROLE_LEAPFROG_ANCHOR = 3,
    ROLE_LEAPFROG_MOVER = 4,
    ROLE_CHAIN_NODE = 5
};

enum MultiUnitState {
    MU_STATE_IDLE = 0,
    MU_STATE_WAIT_TOKEN,
    MU_STATE_SYNC_SPINUP,
    MU_STATE_PREPARE_UNLATCH,
    MU_STATE_IMPULSE_EXECUTE,
    MU_STATE_APEX_DOCKING,
    MU_STATE_TOUCHDOWN_LOCK,
    MU_STATE_CYCLE_COMPLETE,
    MU_STATE_ABORT
};

class MultiUnitFSM {
public:
    MultiUnitFSM(
        uint8_t local_id,
        MotorMCPWM* motor,
        EPMDriver* epm,
        AttitudeEKF* ekf,
        OpticalMeshRouter* router,
        bool is_solid_state = true
    );

    void setRole(MultiUnitRole role, uint8_t chain_index = 0, uint8_t chain_length = 3);
    void triggerCooperativeMotion();
    void update(float dt);

    void onOpticalMessageReceived(const OpticalMeshMessage_t& msg);

    MultiUnitRole getRole() const { return _role; }
    MultiUnitState getState() const { return _state; }
    bool isCompleted() const { return _state == MU_STATE_CYCLE_COMPLETE; }
    bool isSolidState() const { return _is_solid_state; }

private:
    uint8_t _id;
    MultiUnitRole _role;
    MultiUnitState _state;
    uint8_t _chain_index;
    uint8_t _chain_length;
    bool _is_solid_state;

    float _timer_s;
    float _phase_duration_s;
    bool _has_token;

    MotorMCPWM* _motor;
    EPMDriver* _epm;
    AttitudeEKF* _ekf;
    OpticalMeshRouter* _router;

    void stepClimbBase(float dt);
    void stepClimbMover(float dt);
    void stepChainNode(float dt);
};
