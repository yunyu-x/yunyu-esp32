/**
 * @file driver_interface.h
 * @brief Unified Device Driver Interface for microUnit Robotics.
 * @details Implements extensible, hot-pluggable driver lifecycle and health diagnosis.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

namespace microunit {

enum class DeviceType : uint8_t {
    UNKNOWN = 0,
    ACTUATOR_MOTOR,       // Flywheel / Locomotion Actuator
    ACTUATOR_EPM,         // Electropermanent Magnet Clamp
    SENSOR_IMU,           // 6-DOF Attitude & Motion Sensor
    SENSOR_POWER_BMS,     // Battery & Power Management System
    COMM_OPTICAL_FACE,    // Multi-Face Optical Mesh Transceiver
    INDICATOR_LED,        // Status & Diagnostic Light
    EXTENSION_PAYLOAD     // Hot-pluggable Modular Add-on (ToF, Gripper, etc.)
};

#ifdef DISABLED
#undef DISABLED
#endif

enum class DriverHealth : uint8_t {
    UNINITIALIZED = 0,
    HEALTHY,
    DEGRADED,
    FAULTED,
    DISABLED
};

enum class DriverErrorCode : uint32_t {
    ERR_NONE = 0,
    ERR_INIT_FAILED         = (1 << 0),
    ERR_COMMUNICATION_TIMEOUT = (1 << 1),
    ERR_HARDWARE_FAULT      = (1 << 2),
    ERR_OVER_TEMPERATURE   = (1 << 3),
    ERR_OVER_CURRENT        = (1 << 4),
    ERR_UNDER_VOLTAGE       = (1 << 5),
    ERR_BUS_DEADLOCK        = (1 << 6),
    ERR_CONFIG_INVALID      = (1 << 7),
    ERR_SLOT_DISCONNECTED   = (1 << 8)
};

/**
 * @brief Unified interface that all microUnit hardware drivers must implement.
 */
class IDeviceDriver {
public:
    virtual ~IDeviceDriver() = default;

    // Identification
    virtual const char* getName() const = 0;
    virtual DeviceType getType() const = 0;
    virtual uint8_t getDeviceId() const = 0;

    // Lifecycle
    virtual bool init() = 0;
    virtual bool start() = 0;
    virtual void stop() = 0;
    virtual void update(float dt_seconds) = 0;

    // Self-Diagnosis & Fault Management
    virtual bool selfTest() = 0;
    virtual DriverHealth getHealth() const = 0;
    virtual uint32_t getErrorCode() const = 0;
    virtual bool recover(uint32_t fault_mask) = 0;

    // Status queries
    virtual bool isRunning() const = 0;
};

} // namespace microunit
