/**
 * @file led_driver.cpp
 * @brief Implementation of Status and Diagnostic LED Indicator Driver.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/led_driver.h"

namespace microunit {

LedIndicatorDriver::LedIndicatorDriver(uint8_t pin_led)
    : _pin_led(pin_led), _health(DriverHealth::UNINITIALIZED), _error_code(0),
      _running(false), _mode(LedMode::OFF), _led_state(false),
      _timer_ms(0.0f), _error_code_blinks(0), _current_blink_count(0) {}

void LedIndicatorDriver::writeLed(bool on) {
    _led_state = on;
    const HalInterface* hal = get_hal();
    if (hal) {
        hal->digital_write(_pin_led, on ? HAL_LEVEL_HIGH : HAL_LEVEL_LOW);
    }
}

bool LedIndicatorDriver::init() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_INIT_FAILED);
        return false;
    }

    hal->pin_mode(_pin_led, HAL_PIN_OUTPUT);
    writeLed(false);

    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool LedIndicatorDriver::start() {
    if (_health == DriverHealth::FAULTED) return false;
    _running = true;
    setMode(LedMode::HEARTBEAT_NORMAL);
    return true;
}

void LedIndicatorDriver::stop() {
    writeLed(false);
    _running = false;
    _mode = LedMode::OFF;
}

bool LedIndicatorDriver::selfTest() {
    _health = DriverHealth::HEALTHY;
    return true;
}

bool LedIndicatorDriver::recover(uint32_t fault_mask) {
    _error_code &= ~fault_mask;
    _health = DriverHealth::HEALTHY;
    return true;
}

void LedIndicatorDriver::setMode(LedMode mode) {
    _mode = mode;
    _timer_ms = 0.0f;
    _current_blink_count = 0;
    if (_mode == LedMode::OFF) {
        writeLed(false);
    } else if (_mode == LedMode::ON) {
        writeLed(true);
    }
}

void LedIndicatorDriver::setErrorBlinkCode(uint8_t count) {
    _error_code_blinks = count;
    setMode(LedMode::BLINK_ERROR_CODE);
}

void LedIndicatorDriver::update(float dt_seconds) {
    float dt_ms = dt_seconds * 1000.0f;
    _timer_ms += dt_ms;

    switch (_mode) {
        case LedMode::OFF:
            writeLed(false);
            break;

        case LedMode::ON:
            writeLed(true);
            break;

        case LedMode::HEARTBEAT_NORMAL:
            // 1 Hz cycle: 100ms ON, 900ms OFF
            if (_timer_ms < 100.0f) {
                writeLed(true);
            } else if (_timer_ms < 1000.0f) {
                writeLed(false);
            } else {
                _timer_ms = 0.0f;
            }
            break;

        case LedMode::HEARTBEAT_FAST:
            // 4 Hz cycle: 125ms ON, 125ms OFF
            if (_timer_ms < 125.0f) {
                writeLed(true);
            } else if (_timer_ms < 250.0f) {
                writeLed(false);
            } else {
                _timer_ms = 0.0f;
            }
            break;

        case LedMode::BLINK_ERROR_CODE:
            // Flash N times (150ms ON, 150ms OFF), then 1000ms pause
            float cycle_len = 300.0f;
            float total_burst = _error_code_blinks * cycle_len;
            if (_timer_ms < total_burst) {
                float in_cycle = _timer_ms - static_cast<int>(_timer_ms / cycle_len) * cycle_len;
                writeLed(in_cycle < 150.0f);
            } else if (_timer_ms < total_burst + 1000.0f) {
                writeLed(false);
            } else {
                _timer_ms = 0.0f;
            }
            break;
    }
}

} // namespace microunit
