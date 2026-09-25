/**
 * @file attitude_ekf.cpp
 * @brief Quaternion-based Attitude Estimation Implementation.
 */

#include "filters/attitude_ekf.h"
#include <math.h>

#define CRITICAL_TILT_ANGLE_DEG 45.0f

AttitudeEstimator::AttitudeEstimator()
    : _q{1.0f, 0.0f, 0.0f, 0.0f},
      _euler{0.0f, 0.0f, 0.0f},
      _gy_filtered(0.0f),
      _beta(0.041f) {} // Optimized divergence parameter for 500Hz sampling

void AttitudeEstimator::init() {
    _q.w = 1.0f;
    _q.x = 0.0f;
    _q.y = 0.0f;
    _q.z = 0.0f;
    _euler.roll_deg = 0.0f;
    _euler.pitch_deg = 0.0f;
    _euler.yaw_deg = 0.0f;
    _gy_filtered = 0.0f;
}

void AttitudeEstimator::update(float ax, float ay, float az, float gx, float gy, float gz, float dt) {
    _gy_filtered = 0.9f * _gy_filtered + 0.1f * gy;

    // Normalize accelerometer measurement
    float recipNorm;
    float norm = sqrtf(ax * ax + ay * ay + az * az);
    if (norm <= 0.0f) return;
    recipNorm = 1.0f / norm;
    ax *= recipNorm;
    ay *= recipNorm;
    az *= recipNorm;

    // Rate of change of quaternion from gyroscope
    float qDot1 = 0.5f * (-_q.x * gx - _q.y * gy - _q.z * gz);
    float qDot2 = 0.5f * ( _q.w * gx + _q.y * gz - _q.z * gy);
    float qDot3 = 0.5f * ( _q.w * gy - _q.x * gz + _q.z * gx);
    float qDot4 = 0.5f * ( _q.w * gz + _q.x * gy - _q.y * gx);

    // Compute feedback only if accelerometer measurement valid
    float _2q0 = 2.0f * _q.w;
    float _2q1 = 2.0f * _q.x;
    float _2q2 = 2.0f * _q.y;
    float _2q3 = 2.0f * _q.z;
    float _4q0 = 4.0f * _q.w;
    float _4q1 = 4.0f * _q.x;
    float _4q2 = 4.0f * _q.y;
    float _8q1 = 8.0f * _q.x;
    float _8q2 = 8.0f * _q.y;
    float q0q0 = _q.w * _q.w;
    float q1q1 = _q.x * _q.x;
    float q2q2 = _q.y * _q.y;
    float q3q3 = _q.z * _q.z;

    // Gradient descent algorithm corrective step
    float s0 = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay;
    float s1 = _4q1 * q3q3 - _2q3 * ax + 4.0f * q0q0 * _q.x - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az;
    float s2 = 4.0f * q0q0 * _q.y + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az;
    float s3 = 4.0f * q1q1 * _q.z - _2q1 * ax + 4.0f * q2q2 * _q.z - _2q2 * ay;

    norm = sqrtf(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3);
    if (norm > 0.0f) {
        recipNorm = 1.0f / norm;
        s0 *= recipNorm;
        s1 *= recipNorm;
        s2 *= recipNorm;
        s3 *= recipNorm;

        // Apply feedback step
        qDot1 -= _beta * s0;
        qDot2 -= _beta * s1;
        qDot3 -= _beta * s2;
        qDot4 -= _beta * s3;
    }

    // Integrate rate of change of quaternion
    _q.w += qDot1 * dt;
    _q.x += qDot2 * dt;
    _q.y += qDot3 * dt;
    _q.z += qDot4 * dt;

    // Normalize quaternion
    norm = sqrtf(_q.w * _q.w + _q.x * _q.x + _q.y * _q.y + _q.z * _q.z);
    recipNorm = 1.0f / norm;
    _q.w *= recipNorm;
    _q.x *= recipNorm;
    _q.y *= recipNorm;
    _q.z *= recipNorm;

    computeEuler();
}

void AttitudeEstimator::computeEuler() {
    // Roll (x-axis rotation)
    float sinr_cosp = 2.0f * (_q.w * _q.x + _q.y * _q.z);
    float cosr_cosp = 1.0f - 2.0f * (_q.x * _q.x + _q.y * _q.y);
    _euler.roll_deg = atan2f(sinr_cosp, cosr_cosp) * (180.0f / 3.14159265f);

    // Pitch (y-axis rotation)
    float sinp = 2.0f * (_q.w * _q.y - _q.z * _q.x);
    if (fabsf(sinp) >= 1.0f)
        _euler.pitch_deg = copysignf(90.0f, sinp);
    else
        _euler.pitch_deg = asinf(sinp) * (180.0f / 3.14159265f);

    // Yaw (z-axis rotation)
    float siny_cosp = 2.0f * (_q.w * _q.z + _q.x * _q.y);
    float cosy_cosp = 1.0f - 2.0f * (_q.y * _q.y + _q.z * _q.z);
    _euler.yaw_deg = atan2f(siny_cosp, cosy_cosp) * (180.0f / 3.14159265f);
}
