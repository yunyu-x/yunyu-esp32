/**
 * @file attitude_ekf.h
 * @brief Quaternion-based Attitude Estimation Filter for 500 Hz MSRR Dynamics.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <Arduino.h>
#include "config.h"

#ifndef CRITICAL_TILT_ANGLE_DEG
#define CRITICAL_TILT_ANGLE_DEG 45.0f
#endif

struct Quaternion {
    float w, x, y, z;
};

struct EulerAngles {
    float roll_deg;
    float pitch_deg;
    float yaw_deg;
};

class AttitudeEstimator {
public:
    AttitudeEstimator();
    void init();
    void update(float ax, float ay, float az, float gx, float gy, float gz, float dt);

    Quaternion getQuaternion() const { return _q; }
    EulerAngles getEulerAngles() const { return _euler; }
    float getRollDeg() const { return _euler.roll_deg; }
    float getAngularVelocityY() const { return _gy_filtered; }
    bool hasCrossedCrest() const { return fabs(_euler.roll_deg) >= CRITICAL_TILT_ANGLE_DEG; }

private:
    Quaternion _q;
    EulerAngles _euler;
    float _gy_filtered;
    float _beta; // Filter gain (algorithm parameter)

    void computeEuler();
};
