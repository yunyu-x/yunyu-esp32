/**
 * @file mock_hal.cpp
 * @brief Implementation of Mock Hardware Abstraction Layer.
 * @author microUnit Robotics Open Source Team
 */

#include "hal/mock_hal.h"
#include <cstring>

namespace microunit {

static MockHal* s_mock_instance = nullptr;

// Static wrapper functions conforming to HalInterface function pointers
static void mock_pin_mode(uint8_t pin, HalPinMode mode) {
    if (s_mock_instance) {
        // Just store mode
    }
}

static void mock_digital_write(uint8_t pin, HalPinLevel level) {
    if (s_mock_instance) {
        s_mock_instance->setPinLevel(pin, level);
    }
}

static HalPinLevel mock_digital_read(uint8_t pin) {
    if (s_mock_instance) {
        return s_mock_instance->getPinLevel(pin);
    }
    return HAL_LEVEL_LOW;
}

static void mock_pwm_setup(uint8_t channel, uint32_t freq_hz, uint8_t resolution_bits) {
    (void)resolution_bits;
    // mock pwm setup
}

static void mock_pwm_attach_pin(uint8_t pin, uint8_t channel) {
    (void)pin;
    (void)channel;
}

static void mock_pwm_write(uint8_t channel, uint32_t duty) {
    if (s_mock_instance) {
        // We can expose an internal method or record it directly
        // Let's use setPinLevel or store pwm
    }
}

static bool mock_i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, const uint8_t* data, size_t len) {
    if (!s_mock_instance || s_mock_instance->isI2cBusHanged()) {
        return false;
    }
    for (size_t i = 0; i < len; ++i) {
        s_mock_instance->setI2cRegister(dev_addr, reg_addr + i, data[i]);
    }
    return true;
}

static bool mock_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t* data, size_t len) {
    if (!s_mock_instance || s_mock_instance->isI2cBusHanged()) {
        return false;
    }
    for (size_t i = 0; i < len; ++i) {
        data[i] = s_mock_instance->getI2cRegister(dev_addr, reg_addr + i);
    }
    return true;
}

static bool mock_i2c_check_bus_hang(uint8_t sda_pin, uint8_t scl_pin) {
    (void)sda_pin;
    (void)scl_pin;
    if (s_mock_instance) {
        return s_mock_instance->isI2cBusHanged();
    }
    return false;
}

static uint16_t mock_adc_read_raw(uint8_t pin) {
    if (!s_mock_instance) return 0;
    float volts = s_mock_instance->getAdcVoltage(pin);
    // 3.3V reference, 12-bit (0..4095)
    int raw = (int)((volts / 3.3f) * 4095.0f);
    if (raw < 0) raw = 0;
    if (raw > 4095) raw = 4095;
    return static_cast<uint16_t>(raw);
}

static float mock_adc_read_voltage(uint8_t pin) {
    if (!s_mock_instance) return 0.0f;
    return s_mock_instance->getAdcVoltage(pin);
}

static uint32_t mock_get_millis(void) {
    if (!s_mock_instance) return 0;
    return s_mock_instance->getMillis();
}

static uint64_t mock_get_micros(void) {
    if (!s_mock_instance) return 0;
    return s_mock_instance->getMicros();
}

static void mock_delay_ms(uint32_t ms) {
    if (s_mock_instance) {
        s_mock_instance->advanceTimeMs(ms);
    }
}

static void mock_delay_us(uint32_t us) {
    if (s_mock_instance) {
        s_mock_instance->advanceTimeUs(us);
    }
}

MockHal& MockHal::getInstance() {
    static MockHal instance;
    s_mock_instance = &instance;
    return instance;
}

MockHal::MockHal() : _i2c_bus_hung(false), _current_micros(0) {
    s_mock_instance = this;

    _hal_vtable.pin_mode = mock_pin_mode;
    _hal_vtable.digital_write = mock_digital_write;
    _hal_vtable.digital_read = mock_digital_read;
    _hal_vtable.pwm_setup = mock_pwm_setup;
    _hal_vtable.pwm_attach_pin = mock_pwm_attach_pin;
    _hal_vtable.pwm_write = [](uint8_t channel, uint32_t duty) {
        if (s_mock_instance) {
            s_mock_instance->_pwm_duty[channel] = duty;
        }
    };
    _hal_vtable.i2c_write_reg = mock_i2c_write_reg;
    _hal_vtable.i2c_read_reg = mock_i2c_read_reg;
    _hal_vtable.i2c_check_bus_hang = mock_i2c_check_bus_hang;
    _hal_vtable.adc_read_raw = mock_adc_read_raw;
    _hal_vtable.adc_read_voltage = mock_adc_read_voltage;
    _hal_vtable.get_millis = mock_get_millis;
    _hal_vtable.get_micros = mock_get_micros;
    _hal_vtable.delay_ms = mock_delay_ms;
    _hal_vtable.delay_us = mock_delay_us;

    set_hal(&_hal_vtable);
}

void MockHal::reset() {
    _pins.clear();
    _pin_modes.clear();
    _pwm_duty.clear();
    _pwm_freq.clear();
    _i2c_mem.clear();
    _adc_volts.clear();
    _i2c_bus_hung = false;
    _current_micros = 0;
}

void MockHal::setPinLevel(uint8_t pin, HalPinLevel level) {
    _pins[pin] = level;
    if (pin == 21 && level == HAL_LEVEL_HIGH) {
        // Cutting power to IMU via Q4 PMOS releases slave pull-down on I2C bus
        _i2c_bus_hung = false;
    }
}

HalPinLevel MockHal::getPinLevel(uint8_t pin) const {
    auto it = _pins.find(pin);
    if (it != _pins.end()) {
        return it->second;
    }
    return HAL_LEVEL_LOW;
}

HalPinMode MockHal::getPinMode(uint8_t pin) const {
    auto it = _pin_modes.find(pin);
    if (it != _pin_modes.end()) {
        return it->second;
    }
    return HAL_PIN_INPUT;
}

uint32_t MockHal::getPwmDuty(uint8_t channel) const {
    auto it = _pwm_duty.find(channel);
    if (it != _pwm_duty.end()) {
        return it->second;
    }
    return 0;
}

uint32_t MockHal::getPwmFreq(uint8_t channel) const {
    auto it = _pwm_freq.find(channel);
    if (it != _pwm_freq.end()) {
        return it->second;
    }
    return 0;
}

void MockHal::setI2cRegister(uint8_t dev_addr, uint8_t reg_addr, uint8_t val) {
    uint16_t key = (static_cast<uint16_t>(dev_addr) << 8) | reg_addr;
    _i2c_mem[key] = val;
}

uint8_t MockHal::getI2cRegister(uint8_t dev_addr, uint8_t reg_addr) const {
    uint16_t key = (static_cast<uint16_t>(dev_addr) << 8) | reg_addr;
    auto it = _i2c_mem.find(key);
    if (it != _i2c_mem.end()) {
        return it->second;
    }
    return 0;
}

void MockHal::injectI2cBusHang(bool hang) {
    _i2c_bus_hung = hang;
}

bool MockHal::isI2cBusHanged() const {
    return _i2c_bus_hung;
}

void MockHal::setAdcVoltage(uint8_t pin, float volts) {
    _adc_volts[pin] = volts;
}

float MockHal::getAdcVoltage(uint8_t pin) const {
    auto it = _adc_volts.find(pin);
    if (it != _adc_volts.end()) {
        return it->second;
    }
    return 0.0f;
}

void MockHal::advanceTimeMs(uint32_t ms) {
    _current_micros += static_cast<uint64_t>(ms) * 1000ULL;
}

void MockHal::advanceTimeUs(uint32_t us) {
    _current_micros += static_cast<uint64_t>(us);
}

uint32_t MockHal::getMillis() const {
    return static_cast<uint32_t>(_current_micros / 1000ULL);
}

uint64_t MockHal::getMicros() const {
    return _current_micros;
}

const HalInterface* MockHal::getInterface() {
    return &_hal_vtable;
}

} // namespace microunit

// Global accessor definitions
static const HalInterface* g_current_hal = nullptr;

extern "C" {
const HalInterface* get_hal(void) {
    if (!g_current_hal) {
        return microunit::MockHal::getInstance().getInterface();
    }
    return g_current_hal;
}

void set_hal(const HalInterface* hal) {
    g_current_hal = hal;
}
}
