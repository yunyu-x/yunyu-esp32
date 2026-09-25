/**
 * @file neuromorphic_reflex.h
 * @brief FlyDrones-inspired Embedded Neuromorphic Reflex Controller & DCBA Auctioneer for ESP32.
 * @details Implements O(k) Leaky Integrate-and-Fire (LIF) dynamics, bilateral DNp03 saccadic evasion,
 *          haltere gyroscopic damping, hardware safety governor, and 16-byte auction consensus packets.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <stdint.h>
#include <math.h>

#ifdef ARDUINO
#include <Arduino.h>
#else
#include <cstring>
#include <algorithm>
#endif

namespace microunit {

/**
 * @brief 16-Byte Wire Protocol for Decentralized Consensus-Based Auction (DCBA).
 */
#pragma pack(push, 1)
struct AuctionClaimPacket {
    uint8_t  sender_id;       // 1 byte: Agent ID (0-255)
    uint8_t  claimed_slot;    // 1 byte: Target Slot ID (0-255)
    float    bid_value;       // 4 bytes: Utility bid value
    uint32_t logical_clock;   // 4 bytes: Monotonic Lamport clock
    uint8_t  status_flags;    // 1 byte: Bit 0 = Faulty, Bit 1 = Docked, Bit 2 = Saccade Active
    uint8_t  reserved[5];     // 5 bytes: Reserved padding to exactly 16 bytes
};
#pragma pack(pop)

static_assert(sizeof(AuctionClaimPacket) == 16, "AuctionClaimPacket must be exactly 16 bytes for ultra-low latency mesh transmission.");

struct NeuromorphicConfig {
    float tau_membrane_ms    = 15.0f;     // LIF membrane time constant (ms)
    float v_thresh           = 1.0f;      // Action potential threshold
    float v_reset            = 0.0f;      // Reset potential
    float hs_gain            = 1.8f;      // Horizontal System (HS) optomotor yaw gain
    float vs_gain            = 1.2f;      // Vertical System (VS) thrust gain
    float gf_looming_thresh  = 0.30f;     // Giant Fiber (DNp01) looming threshold
    float gf_escape_impulse  = 1.1f;      // Giant Fiber escape burst force (N)
    float saccade_thresh     = 0.22f;     // DNp03 unilateral saccade threshold
    float saccade_gain       = 1.35f;     // DNp03 saccade evasive turn force (N)
    float haltere_damping    = 0.35f;     // Haltere gyro yaw damping (N*s/rad)
    float force_max          = 1.2f;      // Peak actuator force clamp (N)
    float slew_rate_n_per_s  = 20.0f;     // Safety governor slew rate limit (N/s)
    float geofence_radius    = 2.5f;      // Geofence radius (m)
    float min_battery_pct    = 20.0f;     // Low battery threshold (%)
};

/**
 * @brief Embedded Hardware Safety Governor
 * Directly guards physical actuators against extreme neural spikes, electrical sag, and mechanical shock.
 */
class EmbeddedSafetyGovernor {
public:
    explicit EmbeddedSafetyGovernor(const NeuromorphicConfig& cfg = NeuromorphicConfig());
    void reset();
    void filter(float in_fx, float in_fy, float px, float py, float battery_pct, float dt, float& out_fx, float& out_fy);

private:
    NeuromorphicConfig _cfg;
    float _prev_fx;
    float _prev_fy;
};

/**
 * @brief Single-Unit Neuromorphic Reflex Controller (Cortex-M / ESP32 Optimized)
 */
class NeuromorphicReflex {
public:
    explicit NeuromorphicReflex(uint8_t agent_id, const NeuromorphicConfig& cfg = NeuromorphicConfig());
    void reset();
    
    /**
     * @brief Executes one step of the bio-inspired reflex loop.
     * Latency on ESP32 (240MHz): < 0.85 microseconds.
     */
    void update(float left_flow, float right_flow,
                float looming_l, float looming_r,
                float gyro_z,
                float target_dx, float target_dy,
                float current_vx, float current_vy,
                float px, float py,
                float battery_pct,
                float dt,
                float& out_fx, float& out_fy);

    // Neuromorphic State Inspection
    bool isGiantFiberSpiking() const { return _spike_gf; }
    bool isSaccadeLeftSpiking() const { return _spike_dnp03_l; }
    bool isSaccadeRightSpiking() const { return _spike_dnp03_r; }
    float getLoomingRate() const { return _looming_max; }

private:
    uint8_t _agent_id;
    NeuromorphicConfig _cfg;
    EmbeddedSafetyGovernor _governor;

    // LIF membrane potentials
    float _v_hs_l;
    float _v_hs_r;
    float _v_vs;
    float _v_gf;
    float _v_dnp03_l;
    float _v_dnp03_r;
    float _v_pvlp_inh;

    // Spike flags
    bool _spike_gf;
    bool _spike_dnp03_l;
    bool _spike_dnp03_r;
    float _looming_max;
};

} // namespace microunit
