/**
 * @file imu_mpu6050.cpp
 * @brief Implementation of MPU-6050 6-DOF IMU Driver with Q4 Deadlock Auto-Recovery.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/imu_mpu6050.h"
#include <cstring>

namespace microunit {

// MPU-6050 Register Map
static constexpr uint8_t REG_SMPLRT_DIV   = 0x19;
static constexpr uint8_t REG_CONFIG       = 0x1A;
static constexpr uint8_t REG_GYRO_CONFIG  = 0x1B;
static constexpr uint8_t REG_ACCEL_CONFIG = 0x1C;
static constexpr uint8_t REG_ACCEL_XOUT_H = 0x3B;
static constexpr uint8_t REG_PWR_MGMT_1   = 0x6B;
static constexpr uint8_t REG_WHO_AM_I     = 0x75;

ImuMpu6050::ImuMpu6050(uint8_t pin_sda, uint8_t pin_scl,
                       uint8_t pin_pwr_en, uint8_t pin_int,
                       uint8_t i2c_addr)
    : _pin_sda(pin_sda), _pin_scl(pin_scl),
      _pin_pwr_en(pin_pwr_en), _pin_int(pin_int),
      _i2c_addr(i2c_addr),
      _health(DriverHealth::UNINITIALIZED), _error_code(0), _running(false),
      _consecutive_i2c_failures(0), _recovery_count(0) {
    std::memset(&_data, 0, sizeof(_data));
}

bool ImuMpu6050::writeRegister(uint8_t reg, uint8_t val) {
    const HalInterface* hal = get_hal();
    if (!hal) return false;
    return hal->i2c_write_reg(_i2c_addr, reg, &val, 1);
}

bool ImuMpu6050::readRegister(uint8_t reg, uint8_t* val) {
    const HalInterface* hal = get_hal();
    if (!hal) return false;
    return hal->i2c_read_reg(_i2c_addr, reg, val, 1);
}

bool ImuMpu6050::readRegisters(uint8_t reg, uint8_t* buffer, size_t len) {
    const HalInterface* hal = get_hal();
    if (!hal) return false;
    return hal->i2c_read_reg(_i2c_addr, reg, buffer, len);
}

bool ImuMpu6050::configureMpuRegisters() {
    // 1. Reset sleep mode, select PLL with X gyro reference
    if (!writeRegister(REG_PWR_MGMT_1, 0x01)) return false;
    // 2. Set sample rate divider (1kHz / (1 + 0) = 1kHz)
    if (!writeRegister(REG_SMPLRT_DIV, 0x00)) return false;
    // 3. Digital Low-Pass Filter (DLPF = 3, ~42Hz bandwidth)
    if (!writeRegister(REG_CONFIG, 0x03)) return false;
    // 4. Gyro range +-2000 dps (FS_SEL = 3 -> 0x18)
    if (!writeRegister(REG_GYRO_CONFIG, 0x18)) return false;
    // 5. Accel range +-16g (AFS_SEL = 3 -> 0x18)
    if (!writeRegister(REG_ACCEL_CONFIG, 0x18)) return false;

    return true;
}

bool ImuMpu6050::init() {
    const HalInterface* hal = get_hal();
    if (!hal) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_INIT_FAILED);
        return false;
    }

    // Configure Q4 power gate pin (Active LOW enables P-MOSFET)
    hal->pin_mode(_pin_pwr_en, HAL_PIN_OUTPUT);
    hal->digital_write(_pin_pwr_en, HAL_LEVEL_LOW); // Power ON
    hal->pin_mode(_pin_int, HAL_PIN_INPUT);

    // Probe WHO_AM_I
    uint8_t who_am_i = 0;
    if (!readRegister(REG_WHO_AM_I, &who_am_i) || (who_am_i != 0x68 && who_am_i != 0x69)) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_HARDWARE_FAULT);
        return false;
    }

    if (!configureMpuRegisters()) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_CONFIG_INVALID);
        return false;
    }

    _consecutive_i2c_failures = 0;
    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool ImuMpu6050::start() {
    if (_health == DriverHealth::FAULTED) return false;
    _running = true;
    return true;
}

void ImuMpu6050::stop() {
    _running = false;
}

bool ImuMpu6050::selfTest() {
    uint8_t who_am_i = 0;
    if (!readRegister(REG_WHO_AM_I, &who_am_i) || (who_am_i != 0x68 && who_am_i != 0x69)) {
        _health = DriverHealth::FAULTED;
        _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_COMMUNICATION_TIMEOUT);
        return false;
    }
    _health = DriverHealth::HEALTHY;
    return true;
}

bool ImuMpu6050::powerCycleImu() {
    const HalInterface* hal = get_hal();
    if (!hal) return false;

    // 1. Cut power to IMU via Q4 PMOS (HIGH = OFF)
    hal->digital_write(_pin_pwr_en, HAL_LEVEL_HIGH);
    hal->delay_ms(10); // Allow POSCAP and ceramic caps to discharge below 0.3V

    // 2. Clear any injected mock bus hang during power-off
    // (In hardware, cutting power releases SDA line)
    // 3. Restore power (LOW = ON) via soft-start R25/C15
    hal->digital_write(_pin_pwr_en, HAL_LEVEL_LOW);
    hal->delay_ms(15); // Wait for MPU POR reset settle

    // 4. Re-configure registers
    if (!configureMpuRegisters()) {
        return false;
    }

    _consecutive_i2c_failures = 0;
    _recovery_count++;
    _health = DriverHealth::HEALTHY;
    _error_code = 0;
    return true;
}

bool ImuMpu6050::recover(uint32_t fault_mask) {
    if (fault_mask & (static_cast<uint32_t>(DriverErrorCode::ERR_BUS_DEADLOCK) |
                      static_cast<uint32_t>(DriverErrorCode::ERR_COMMUNICATION_TIMEOUT))) {
        // If bus hang was injected, clear it upon power cycle
        // In real hardware, power-cycling releases the pull-down
        const HalInterface* hal = get_hal();
        if (hal && hal->i2c_check_bus_hang(_pin_sda, _pin_scl)) {
            // Power cycle will clear slave bus hang
        }
        return powerCycleImu();
    }

    _error_code &= ~fault_mask;
    if (_error_code == 0) {
        _health = DriverHealth::HEALTHY;
        return true;
    }
    return false;
}

void ImuMpu6050::update(float dt_seconds) {
    (void)dt_seconds;
    const HalInterface* hal = get_hal();
    if (!hal) return;

    // Check bus hang
    if (hal->i2c_check_bus_hang(_pin_sda, _pin_scl)) {
        _consecutive_i2c_failures++;
        if (_consecutive_i2c_failures >= 3) {
            _health = DriverHealth::FAULTED;
            _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_BUS_DEADLOCK);
        }
        return;
    }

    // Read 14 bytes: ACCEL (6), TEMP (2), GYRO (6)
    uint8_t raw[14];
    if (!readRegisters(REG_ACCEL_XOUT_H, raw, 14)) {
        _consecutive_i2c_failures++;
        if (_consecutive_i2c_failures >= 3) {
            _health = DriverHealth::FAULTED;
            _error_code |= static_cast<uint32_t>(DriverErrorCode::ERR_COMMUNICATION_TIMEOUT);
        }
        return;
    }

    // Reset failure counter on success
    _consecutive_i2c_failures = 0;

    int16_t raw_ax = static_cast<int16_t>((raw[0] << 8) | raw[1]);
    int16_t raw_ay = static_cast<int16_t>((raw[2] << 8) | raw[3]);
    int16_t raw_az = static_cast<int16_t>((raw[4] << 8) | raw[5]);
    int16_t raw_temp = static_cast<int16_t>((raw[6] << 8) | raw[7]);
    int16_t raw_gx = static_cast<int16_t>((raw[8] << 8) | raw[9]);
    int16_t raw_gy = static_cast<int16_t>((raw[10] << 8) | raw[11]);
    int16_t raw_gz = static_cast<int16_t>((raw[12] << 8) | raw[13]);

    // Conversion: +-16g -> 2048 LSB/g, 1g = 9.80665 m/s^2
    _data.accel_x = (raw_ax / 2048.0f) * GRAVITY_MSS;
    _data.accel_y = (raw_ay / 2048.0f) * GRAVITY_MSS;
    _data.accel_z = (raw_az / 2048.0f) * GRAVITY_MSS;

    // Conversion: +-2000 dps -> 16.4 LSB/(deg/s) -> convert to rad/s
    _data.gyro_x_rad = (raw_gx / 16.4f) * DEG_TO_RAD;
    _data.gyro_y_rad = (raw_gy / 16.4f) * DEG_TO_RAD;
    _data.gyro_z_rad = (raw_gz / 16.4f) * DEG_TO_RAD;

    // Temperature: Temp in degC = (TEMP_OUT / 340) + 36.53
    _data.temperature_c = (raw_temp / 340.0f) + 36.53f;
    _data.timestamp_ms = hal->get_millis();
}

} // namespace microunit
