/**
 * @file hal_interface.h
 * @brief Hardware Abstraction Layer (HAL) interface for microUnit ESP32-S3 and Host Mock.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// GPIO Modes
typedef enum {
    HAL_PIN_INPUT = 0,
    HAL_PIN_OUTPUT = 1,
    HAL_PIN_INPUT_PULLUP = 2,
    HAL_PIN_INPUT_PULLDOWN = 3
} HalPinMode;

// GPIO State
typedef enum {
    HAL_LEVEL_LOW = 0,
    HAL_LEVEL_HIGH = 1
} HalPinLevel;

// Hardware Abstraction Layer Function Pointers Table
typedef struct {
    // GPIO Operations
    void (*pin_mode)(uint8_t pin, HalPinMode mode);
    void (*digital_write)(uint8_t pin, HalPinLevel level);
    HalPinLevel (*digital_read)(uint8_t pin);

    // PWM / LEDC Operations
    void (*pwm_setup)(uint8_t channel, uint32_t freq_hz, uint8_t resolution_bits);
    void (*pwm_attach_pin)(uint8_t pin, uint8_t channel);
    void (*pwm_write)(uint8_t channel, uint32_t duty);

    // I2C Master Operations
    bool (*i2c_write_reg)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t* data, size_t len);
    bool (*i2c_read_reg)(uint8_t dev_addr, uint8_t reg_addr, uint8_t* data, size_t len);
    bool (*i2c_check_bus_hang)(uint8_t sda_pin, uint8_t scl_pin);

    // Analog ADC Operations
    uint16_t (*adc_read_raw)(uint8_t pin);
    float (*adc_read_voltage)(uint8_t pin);

    // Timing & Delays
    uint32_t (*get_millis)(void);
    uint64_t (*get_micros)(void);
    void (*delay_ms)(uint32_t ms);
    void (*delay_us)(uint32_t us);
} HalInterface;

// Global HAL accessors
const HalInterface* get_hal(void);
void set_hal(const HalInterface* hal);

#ifdef __cplusplus
}
#endif
