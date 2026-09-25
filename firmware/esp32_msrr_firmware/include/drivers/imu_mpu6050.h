/**
 * @file imu_mpu6050.h
 * @brief InvenSense MPU-6050 6-DOF IMU Driver with Q4 Hardware Power-Gate Cold-Reset.
 * @details Implements 400kHz Fast-Mode I2C register configuration, 6-axis acceleration
 *          and angular rate acquisition, and autonomous I2C deadlock recovery.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "drivers/driver_interface.h"
#include "hal/hal_interface.h"

namespace microunit {

struct ImuData {
    float accel_x;     // m/s^2
    float accel_y;     // m/s^2
    float accel_z;     // m/s^2
    float gyro_x_rad;  // rad/s
    float gyro_y_rad;  // rad/s
    float gyro_z_rad;  // rad/s
    float temperature_c; // deg C
    uint32_t timestamp_ms;
};

class ImuMpu6050 : public IDeviceDriver {
public:
    static constexpr uint8_t MPU6050_DEFAULT_ADDR = 0x68;
    static constexpr float GRAVITY_MSS = 9.80665f;
    static constexpr float DEG_TO_RAD = 0.017453292519943295f;

    ImuMpu6050(uint8_t pin_sda = 12, uint8_t pin_scl = 13,
               uint8_t pin_pwr_en = 21, uint8_t pin_int = 38,
               uint8_t i2c_addr = MPU6050_DEFAULT_ADDR);
    ~ImuMpu6050() override = default;

    // IDeviceDriver Implementation
    const char* getName() const override { return "MPU6050_ImuDriver"; }
    DeviceType getType() const override { return DeviceType::SENSOR_IMU; }
    uint8_t getDeviceId() const override { return 3; }

    bool init() override;
    bool start() override;
    void stop() override;
    void update(float dt_seconds) override;

    bool selfTest() override;
    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _error_code; }
    bool recover(uint32_t fault_mask) override;
    bool isRunning() const override { return _running; }

    // Sensor Readings & Calibration
    const ImuData& getData() const { return _data; }
    uint32_t getRecoveryCount() const { return _recovery_count; }

    // Active Hardware Cold-Reset via Q4 PMOS Gate
    bool powerCycleImu();

private:
    uint8_t _pin_sda;
    uint8_t _pin_scl;
    uint8_t _pin_pwr_en;
    uint8_t _pin_int;
    uint8_t _i2c_addr;

    DriverHealth _health;
    uint32_t _error_code;
    bool _running;

    ImuData _data;
    uint32_t _consecutive_i2c_failures;
    uint32_t _recovery_count;

    bool writeRegister(uint8_t reg, uint8_t val);
    bool readRegister(uint8_t reg, uint8_t* val);
    bool readRegisters(uint8_t reg, uint8_t* buffer, size_t len);
    bool configureMpuRegisters();
};

} // namespace microunit
