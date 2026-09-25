/**
 * @file mock_hal.h
 * @brief High-fidelity Mock Hardware Abstraction Layer for white-box TDD and SIL simulation.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "hal/hal_interface.h"
#include <map>
#include <vector>

namespace microunit {

class MockHal {
public:
    static MockHal& getInstance();

    void reset();

    // Direct Inspection & Fault Injection
    void setPinLevel(uint8_t pin, HalPinLevel level);
    HalPinLevel getPinLevel(uint8_t pin) const;
    HalPinMode getPinMode(uint8_t pin) const;

    uint32_t getPwmDuty(uint8_t channel) const;
    uint32_t getPwmFreq(uint8_t channel) const;

    // I2C Virtual Memory & Fault Injection
    void setI2cRegister(uint8_t dev_addr, uint8_t reg_addr, uint8_t val);
    uint8_t getI2cRegister(uint8_t dev_addr, uint8_t reg_addr) const;
    void injectI2cBusHang(bool hang);
    bool isI2cBusHanged() const;

    // ADC Injection
    void setAdcVoltage(uint8_t pin, float volts);
    float getAdcVoltage(uint8_t pin) const;

    // Time Simulation
    void advanceTimeMs(uint32_t ms);
    void advanceTimeUs(uint32_t us);
    uint32_t getMillis() const;
    uint64_t getMicros() const;

    // Returns C-compatible HalInterface
    const HalInterface* getInterface();

private:
    MockHal();

    std::map<uint8_t, HalPinLevel> _pins;
    std::map<uint8_t, HalPinMode> _pin_modes;
    std::map<uint8_t, uint32_t> _pwm_duty;
    std::map<uint8_t, uint32_t> _pwm_freq;
    std::map<uint16_t, uint8_t> _i2c_mem; // key = (dev_addr << 8) | reg_addr
    std::map<uint8_t, float> _adc_volts;

    bool _i2c_bus_hung;
    uint64_t _current_micros;
    HalInterface _hal_vtable;
};

} // namespace microunit
