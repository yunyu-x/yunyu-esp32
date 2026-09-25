/**
 * @file led_driver.h
 * @brief Status and Diagnostic LED Indicator Driver for microUnit.
 * @details Implements heartbeat pulsing, error blink codes, and unified IDeviceDriver interface.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "drivers/driver_interface.h"
#include "hal/hal_interface.h"

namespace microunit {

enum class LedMode : uint8_t {
    OFF = 0,
    ON,
    HEARTBEAT_NORMAL,
    HEARTBEAT_FAST,
    BLINK_ERROR_CODE
};

class LedIndicatorDriver : public IDeviceDriver {
public:
    explicit LedIndicatorDriver(uint8_t pin_led = 10);
    ~LedIndicatorDriver() override = default;

    // IDeviceDriver Implementation
    const char* getName() const override { return "LED_IndicatorDriver"; }
    DeviceType getType() const override { return DeviceType::INDICATOR_LED; }
    uint8_t getDeviceId() const override { return 6; }

    bool init() override;
    bool start() override;
    void stop() override;
    void update(float dt_seconds) override;

    bool selfTest() override;
    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _error_code; }
    bool recover(uint32_t fault_mask) override;
    bool isRunning() const override { return _running; }

    // LED Pattern Controls
    void setMode(LedMode mode);
    void setErrorBlinkCode(uint8_t count);
    LedMode getMode() const { return _mode; }
    bool isLedOn() const { return _led_state; }

private:
    uint8_t _pin_led;
    DriverHealth _health;
    uint32_t _error_code;
    bool _running;

    LedMode _mode;
    bool _led_state;
    float _timer_ms;
    uint8_t _error_code_blinks;
    uint8_t _current_blink_count;

    void writeLed(bool on);
};

} // namespace microunit
