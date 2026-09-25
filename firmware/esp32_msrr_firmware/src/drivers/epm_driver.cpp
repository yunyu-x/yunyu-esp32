/**
 * @file epm_driver.cpp
 * @brief Implementation of Professional Electropermanent Magnet (EPM) Driver.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/epm_driver.h"

namespace microunit {

EpmDriver::EpmDriver(uint8_t pin_trig)
    : _pin_trig(pin_trig), _health(DriverHealth::UNINITIALIZED), _error_code(0),
      _running(false), _state(EpmState::DETACHED),
      _holding_force_n(DEFAULT_HOLDING_FORCE_N),
      _pulse_timer_ms(0.0f), _target_pulse_ms(DEFAULT_PULSE_MS),
      _cooldown_timer_ms(MIN_COOLDOWN_MS), _total_pulse_count(0) {}

bool EpmDriver::init() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_INIT_FAILED);
        return false;
    }

    hal->pin_mode(_pin_trig, HAL_PIN_OUTPUT);
    setGate(HAL_LEVEL_LOW);

    _state = EpmState::DETACHED;
    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool EpmDriver::start() {
    if (_health == DriverHealth::FAULTED) return false;
    _running = true;
    return true;
}

void EpmDriver::stop() {
    setGate(HAL_LEVEL_LOW);
    _running = false;
}

void EpmDriver::setGate(HalPinLevel level) {
    const HalInterface* hal = get_hal();
    if (hal) {
        hal->digital_write(_pin_trig, level);
    }
}

bool EpmDriver::selfTest() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        return false;
    }
    // Verify gate pin is low at idle
    if (hal->digital_read(_pin_trig) != HAL_LEVEL_LOW) {
        setGate(HAL_LEVEL_LOW);
    }
    _health = DriverHealth::HEALTHY;
    return true;
}

bool EpmDriver::recover(uint32_t fault_mask) {
    _error_code &= ~fault_mask;
    setGate(HAL_LEVEL_LOW);
    _state = EpmState::DETACHED;
    _health = DriverHealth::HEALTHY;
    return true;
}

bool EpmDriver::pulseMagnetize(float pulse_ms) {
    if (_health == DriverHealth::FAULTED || isPulsing()) {
        return false;
    }
    if (_cooldown_timer_ms < MIN_COOLDOWN_MS) {
        return false; // Thermal / PPTC cooldown lock
    }

    _target_pulse_ms = pulse_ms;
    _pulse_timer_ms = 0.0f;
    _cooldown_timer_ms = 0.0f;
    _state = EpmState::PULSING_MAGNETIZE;
    _total_pulse_count++;

    setGate(HAL_LEVEL_HIGH);
    return true;
}

bool EpmDriver::pulseDemagnetize(float pulse_ms) {
    if (_health == DriverHealth::FAULTED || isPulsing()) {
        return false;
    }
    if (_cooldown_timer_ms < MIN_COOLDOWN_MS) {
        return false; // Thermal / PPTC cooldown lock
    }

    _target_pulse_ms = pulse_ms;
    _pulse_timer_ms = 0.0f;
    _cooldown_timer_ms = 0.0f;
    _state = EpmState::PULSING_DEMAGNETIZE;
    _total_pulse_count++;

    setGate(HAL_LEVEL_HIGH);
    return true;
}

void EpmDriver::update(float dt_seconds) {
    float dt_ms = dt_seconds * 1000.0f;
    _cooldown_timer_ms += dt_ms;

    if (isPulsing()) {
        _pulse_timer_ms += dt_ms;
        if (_pulse_timer_ms >= _target_pulse_ms) {
            setGate(HAL_LEVEL_LOW);
            if (_state == EpmState::PULSING_MAGNETIZE) {
                _state = EpmState::ANCHORED;
            } else if (_state == EpmState::PULSING_DEMAGNETIZE) {
                _state = EpmState::DETACHED;
            }
        }
    }
}

} // namespace microunit
