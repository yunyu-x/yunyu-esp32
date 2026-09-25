/**
 * @file epm_driver.h
 * @brief Professional Electropermanent Magnet (EPM) Driver for microUnit.
 * @details Implements microsecond/millisecond pulse discharge timing, thermal cooldown
 *          guard, hardware RC watchdog defense, and unified IDeviceDriver interface.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "drivers/driver_interface.h"
#include "hal/hal_interface.h"

namespace microunit {

enum class EpmState : uint8_t {
    DETACHED = 0,
    PULSING_MAGNETIZE,
    PULSING_DEMAGNETIZE,
    ANCHORED,
    FAULTED
};

class EpmDriver : public IDeviceDriver {
public:
    static constexpr float DEFAULT_PULSE_MS = 5.0f;
    static constexpr float DEFAULT_HOLDING_FORCE_N = 32.5f; // 30N ~ 35N
    static constexpr float MIN_COOLDOWN_MS = 200.0f;        // 200ms thermal & battery protection

    explicit EpmDriver(uint8_t pin_trig = 6);
    ~EpmDriver() override = default;

    // IDeviceDriver Implementation
    const char* getName() const override { return "EPM_ActuatorDriver"; }
    DeviceType getType() const override { return DeviceType::ACTUATOR_EPM; }
    uint8_t getDeviceId() const override { return 2; }

    bool init() override;
    bool start() override;
    void stop() override;
    void update(float dt_seconds) override;

    bool selfTest() override;
    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _error_code; }
    bool recover(uint32_t fault_mask) override;
    bool isRunning() const override { return _running; }

    // Actuation Methods
    bool pulseMagnetize(float pulse_ms = DEFAULT_PULSE_MS);
    bool pulseDemagnetize(float pulse_ms = DEFAULT_PULSE_MS);

    // Queries & Telemetry
    bool isAnchored() const { return _state == EpmState::ANCHORED; }
    bool isPulsing() const {
        return _state == EpmState::PULSING_MAGNETIZE || _state == EpmState::PULSING_DEMAGNETIZE;
    }
    float getHoldingForceN() const { return isAnchored() ? _holding_force_n : 0.0f; }
    EpmState getState() const { return _state; }
    uint32_t getPulseCount() const { return _total_pulse_count; }

private:
    uint8_t _pin_trig;
    DriverHealth _health;
    uint32_t _error_code;
    bool _running;

    EpmState _state;
    float _holding_force_n;
    float _pulse_timer_ms;
    float _target_pulse_ms;
    float _cooldown_timer_ms;
    uint32_t _total_pulse_count;

    void setGate(HalPinLevel level);
};

} // namespace microunit
