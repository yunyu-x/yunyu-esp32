/**
 * @file neuromorphic_reflex.cpp
 * @brief Implementation of Embedded Neuromorphic Reflex & Safety Governor for ESP32.
 * @author microUnit Robotics Open Source Team
 */

#include "controllers/neuromorphic_reflex.h"

namespace microunit {

EmbeddedSafetyGovernor::EmbeddedSafetyGovernor(const NeuromorphicConfig& cfg)
    : _cfg(cfg), _prev_fx(0.0f), _prev_fy(0.0f) {}

void EmbeddedSafetyGovernor::reset() {
    _prev_fx = 0.0f;
    _prev_fy = 0.0f;
}

void EmbeddedSafetyGovernor::filter(float in_fx, float in_fy, float px, float py,
                                    float battery_pct, float dt,
                                    float& out_fx, float& out_fy) {
    float fx = in_fx;
    float fy = in_fy;

    // 1. Slew-Rate Limiting
    float max_step = _cfg.slew_rate_n_per_s * (dt > 1e-4f ? dt : 1e-4f);
    float dfx = fx - _prev_fx;
    float dfy = fy - _prev_fy;
    float diff_mag = sqrtf(dfx * dfx + dfy * dfy);
    if (diff_mag > max_step) {
        float ratio = max_step / diff_mag;
        fx = _prev_fx + dfx * ratio;
        fy = _prev_fy + dfy * ratio;
    }

    // 2. Battery Voltage Sag Throttle
    if (battery_pct < _cfg.min_battery_pct) {
        float scale = battery_pct / _cfg.min_battery_pct;
        if (scale < 0.25f) scale = 0.25f;
        fx *= scale;
        fy *= scale;
    }

    // 3. Soft Geofence Braking
    float dist = sqrtf(px * px + py * py);
    float fence_inner = _cfg.geofence_radius - 0.25f;
    if (dist > fence_inner && dist > 1e-4f) {
        float rx = px / dist;
        float ry = py / dist;
        float outward = fx * rx + fy * ry;
        if (outward > 0.0f) {
            fx -= outward * rx;
            fy -= outward * ry;
            float brake_factor = (dist - fence_inner) / 0.25f;
            if (brake_factor > 1.0f) brake_factor = 1.0f;
            fx -= rx * brake_factor * 0.8f;
            fy -= ry * brake_factor * 0.8f;
        }
    }

    // 4. Maximum Force Saturation Clamping
    float f_mag = sqrtf(fx * fx + fy * fy);
    if (f_mag > _cfg.force_max) {
        float clamp_ratio = _cfg.force_max / f_mag;
        fx *= clamp_ratio;
        fy *= clamp_ratio;
    }

    _prev_fx = fx;
    _prev_fy = fy;
    out_fx = fx;
    out_fy = fy;
}

NeuromorphicReflex::NeuromorphicReflex(uint8_t agent_id, const NeuromorphicConfig& cfg)
    : _agent_id(agent_id), _cfg(cfg), _governor(cfg),
      _v_hs_l(0.0f), _v_hs_r(0.0f), _v_vs(0.0f), _v_gf(0.0f),
      _v_dnp03_l(0.0f), _v_dnp03_r(0.0f), _v_pvlp_inh(0.0f),
      _spike_gf(false), _spike_dnp03_l(false), _spike_dnp03_r(false),
      _looming_max(0.0f) {}

void NeuromorphicReflex::reset() {
    _governor.reset();
    _v_hs_l = 0.0f;
    _v_hs_r = 0.0f;
    _v_vs = 0.0f;
    _v_gf = 0.0f;
    _v_dnp03_l = 0.0f;
    _v_dnp03_r = 0.0f;
    _v_pvlp_inh = 0.0f;
    _spike_gf = false;
    _spike_dnp03_l = false;
    _spike_dnp03_r = false;
    _looming_max = 0.0f;
}

void NeuromorphicReflex::update(float left_flow, float right_flow,
                                float looming_l, float looming_r,
                                float gyro_z,
                                float target_dx, float target_dy,
                                float current_vx, float current_vy,
                                float px, float py,
                                float battery_pct,
                                float dt,
                                float& out_fx, float& out_fy) {
    // 1. LIF Membrane Potential Decay
    float decay = expf(-dt * 1000.0f / _cfg.tau_membrane_ms);
    _v_hs_l *= decay;
    _v_hs_r *= decay;
    _v_vs *= decay;
    _v_gf *= decay;
    _v_dnp03_l *= decay;
    _v_dnp03_r *= decay;
    _v_pvlp_inh *= decay;

    _spike_gf = false;
    _spike_dnp03_l = false;
    _spike_dnp03_r = false;

    float speed = sqrtf(current_vx * current_vx + current_vy * current_vy);
    float heading = (speed > 1e-3f) ? atan2f(current_vy, current_vx) : 0.0f;

    _looming_max = (looming_l > looming_r) ? looming_l : looming_r;

    // 2. Giant Fiber (DNp01) Emergency Escape Accumulator
    _v_gf += _looming_max * 2.5f * dt;
    float f_escape_x = 0.0f;
    float f_escape_y = 0.0f;
    if (_v_gf >= _cfg.gf_looming_thresh) {
        _spike_gf = true;
        _v_gf = _cfg.v_reset;
        // Escape burst opposite to current heading
        f_escape_x = -cosf(heading) * _cfg.gf_escape_impulse;
        f_escape_y = -sinf(heading) * _cfg.gf_escape_impulse;
    }

    // 3. DNp03 Bilateral Looming Saccade Reflex (with mutual inhibition)
    float drive_l = (looming_l > _v_pvlp_inh) ? (looming_l - _v_pvlp_inh) : 0.0f;
    float drive_r = (looming_r > _v_pvlp_inh) ? (looming_r - _v_pvlp_inh) : 0.0f;
    _v_dnp03_l += drive_l * 2.5f * dt;
    _v_dnp03_r += drive_r * 2.5f * dt;

    float f_saccade_x = 0.0f;
    float f_saccade_y = 0.0f;
    if (_v_dnp03_l >= _cfg.saccade_thresh) {
        _spike_dnp03_l = true;
        _v_dnp03_l = _cfg.v_reset;
        _v_pvlp_inh = 0.8f; // suppress opposite side
        // Turn right (clockwise saccade away from left threat)
        f_saccade_x = sinf(heading) * _cfg.saccade_gain;
        f_saccade_y = -cosf(heading) * _cfg.saccade_gain;
    } else if (_v_dnp03_r >= _cfg.saccade_thresh) {
        _spike_dnp03_r = true;
        _v_dnp03_r = _cfg.v_reset;
        _v_pvlp_inh = 0.8f;
        // Turn left (counter-clockwise saccade away from right threat)
        f_saccade_x = -sinf(heading) * _cfg.saccade_gain;
        f_saccade_y = cosf(heading) * _cfg.saccade_gain;
    }

    // 4. Haltere Gyroscopic Angular Damping Reflex
    float f_haltere_x = 0.0f;
    float f_haltere_y = 0.0f;
    if (fabsf(gyro_z) > 1e-4f) {
        float damp_mag = -_cfg.haltere_damping * gyro_z;
        f_haltere_x = -sinf(heading) * damp_mag;
        f_haltere_y = cosf(heading) * damp_mag;
    }

    // 5. HS / VS Target Guidance Reflex with LPi Antagonistic Inhibition
    float f_guidance_x = 0.0f;
    float f_guidance_y = 0.0f;
    float dist_target = sqrtf(target_dx * target_dx + target_dy * target_dy);
    if (dist_target > 1e-4f) {
        float target_angle = atan2f(target_dy, target_dx);
        float angle_diff = atan2f(sinf(target_angle - heading), cosf(target_angle - heading));
        if (angle_diff > 0.0f) {
            _v_hs_l += fabsf(angle_diff) * _cfg.hs_gain * dt;
            _v_hs_r *= 0.5f;
        } else {
            _v_hs_r += fabsf(angle_diff) * _cfg.hs_gain * dt;
            _v_hs_l *= 0.5f;
        }
        _v_vs += (dist_target < 1.0f ? dist_target : 1.0f) * _cfg.vs_gain * dt;

        float k_p = (dist_target < 0.04f) ? 26.0f : 18.0f;
        float c_d = 3.8f;
        f_guidance_x = target_dx * k_p - current_vx * c_d;
        f_guidance_y = target_dy * k_p - current_vy * c_d;
    }

    // Sum unconstrained forces
    float raw_fx = f_guidance_x + f_escape_x + f_saccade_x + f_haltere_x;
    float raw_fy = f_guidance_y + f_escape_y + f_saccade_y + f_haltere_y;

    // 6. Pass through Hardware Safety Governor
    _governor.filter(raw_fx, raw_fy, px, py, battery_pct, dt, out_fx, out_fy);
}

} // namespace microunit
