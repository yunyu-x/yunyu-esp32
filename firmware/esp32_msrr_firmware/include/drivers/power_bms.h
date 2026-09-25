/**
 * @file power_bms.h
 * @brief Power & Battery Management System (BMS) Driver for microUnit.
 * @details Implements 12-bit ADC battery voltage measurement, EMA low-pass filtering,
 *          non-linear LiPo SOC estimation, and brownout under-voltage defense.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "drivers/driver_interface.h"
#include "hal/hal_interface.h"

namespace microunit {

class PowerBmsDriver : public IDeviceDriver {
public:
    static constexpr float DEFAULT_DIVIDER_RATIO = 2.0f; // 100k / 100k
    static constexpr float UNDERVOLTAGE_THRESHOLD_V = 3.00f;
    static constexpr float CRITICAL_LOW_V = 2.90f;

    explicit PowerBmsDriver(uint8_t pin_adc = 11, float divider_ratio = DEFAULT_DIVIDER_RATIO);
    ~PowerBmsDriver() override = default;

    // IDeviceDriver Implementation
    const char* getName() const override { return "PowerBMS_Driver"; }
    DeviceType getType() const override { return DeviceType::SENSOR_POWER_BMS; }
    uint8_t getDeviceId() const override { return 4; }

    bool init() override;
    bool start() override;
    void stop() override;
    void update(float dt_seconds) override;

    bool selfTest() override;
    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _error_code; }
    bool recover(uint32_t fault_mask) override;
    bool isRunning() const override { return _running; }

    // Telemetry & Status
    float getBatteryVoltage() const { return _filtered_voltage_v; }
    float getSocPercent() const { return _soc_percent; }
    bool isUnderVoltage() const { return _filtered_voltage_v < UNDERVOLTAGE_THRESHOLD_V; }
    bool isCriticalLow() const { return _filtered_voltage_v < CRITICAL_LOW_V; }

private:
    uint8_t _pin_adc;
    float _divider_ratio;

    DriverHealth _health;
    uint32_t _error_code;
    bool _running;

    float _filtered_voltage_v;
    float _soc_percent;
    float _filter_alpha;

    float sampleInstantVoltage();
    float calculateSocFromVoltage(float vbat);
};

} // namespace microunit
