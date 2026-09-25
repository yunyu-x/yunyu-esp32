/**
 * @file power_bms.cpp
 * @brief Implementation of Power & Battery Management System (BMS) Driver.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/power_bms.h"
#include <algorithm>

namespace microunit {

PowerBmsDriver::PowerBmsDriver(uint8_t pin_adc, float divider_ratio)
    : _pin_adc(pin_adc), _divider_ratio(divider_ratio),
      _health(DriverHealth::UNINITIALIZED), _error_code(0), _running(false),
      _filtered_voltage_v(3.80f), _soc_percent(55.0f), _filter_alpha(0.20f) {}

float PowerBmsDriver::sampleInstantVoltage() {
    const HalInterface* hal = get_hal();
    if (!hal) return 0.0f;

    float pin_voltage = hal->adc_read_voltage(_pin_adc);
    return pin_voltage * _divider_ratio;
}

float PowerBmsDriver::calculateSocFromVoltage(float vbat) {
    // 1S LiPo empirical OCV-SOC lookup table
    struct SocPoint {
        float voltage;
        float soc;
    };

    static const SocPoint lut[] = {
        { 4.20f, 100.0f },
        { 4.05f,  90.0f },
        { 3.90f,  75.0f },
        { 3.80f,  55.0f },
        { 3.70f,  30.0f },
        { 3.55f,  15.0f },
        { 3.40f,   5.0f },
        { 3.00f,   0.0f }
    };
    static const size_t n_points = sizeof(lut) / sizeof(lut[0]);

    if (vbat >= lut[0].voltage) return 100.0f;
    if (vbat <= lut[n_points - 1].voltage) return 0.0f;

    for (size_t i = 0; i < n_points - 1; ++i) {
        if (vbat <= lut[i].voltage && vbat >= lut[i + 1].voltage) {
            float frac = (vbat - lut[i + 1].voltage) / (lut[i].voltage - lut[i + 1].voltage);
            return lut[i + 1].soc + frac * (lut[i].soc - lut[i + 1].soc);
        }
    }
    return 0.0f;
}

bool PowerBmsDriver::init() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_INIT_FAILED);
        return false;
    }

    hal->pin_mode(_pin_adc, HAL_PIN_INPUT);

    // Initial instant reading
    float v0 = sampleInstantVoltage();
    if (v0 > 0.5f) {
        _filtered_voltage_v = v0;
    }
    _soc_percent = calculateSocFromVoltage(_filtered_voltage_v);

    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool PowerBmsDriver::start() {
    if (_health == DriverHealth::FAULTED) return false;
    _running = true;
    return true;
}

void PowerBmsDriver::stop() {
    _running = false;
}

bool PowerBmsDriver::selfTest() {
    float v = sampleInstantVoltage();
    // Valid 1S battery or bench supply range: 2.5V to 4.5V
    if (v < 2.5f || v > 4.5f) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT);
        return false;
    }
    _health = DriverHealth::HEALTHY;
    return true;
}

bool PowerBmsDriver::recover(uint32_t fault_mask) {
    _error_code &= ~fault_mask;
    if (_filtered_voltage_v >= UNDERVOLTAGE_THRESHOLD_V) {
        _health = DriverHealth::HEALTHY;
        return true;
    }
    return false;
}

void PowerBmsDriver::update(float dt_seconds) {
    (void)dt_seconds;
    float raw_v = sampleInstantVoltage();
    _filtered_voltage_v = _filter_alpha * raw_v + (1.0f - _filter_alpha) * _filtered_voltage_v;
    _soc_percent = calculateSocFromVoltage(_filtered_voltage_v);

    if (_filtered_voltage_v < UNDERVOLTAGE_THRESHOLD_V) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_UNDER_VOLTAGE);
    }
}

} // namespace microunit
