/**
 * @file config.h
 * @brief System hardware pin definitions and first-principles physical constants for microUnit ESP32-S3.
 * @author microUnit Robotics Open Source Team
 * @date 2026-09-23
 */

#pragma once

#include <stdint.h>

// ==========================================
// 1. ESP32-S3 GPIO PINOUT (Industrial 4-Layer PCBA v2.0 Baseline)
// ==========================================
#ifndef HARDWARE_VERSION_MVP

// Industrial PCBA v2.0 Pinout
#define PIN_MOTOR_IN1         4    // DRV8833 IN1 (MCPWM Channel A) - Flywheel Spinup
#define PIN_MOTOR_IN2         5    // DRV8833 IN2 (MCPWM Channel B) - Flywheel Dynamic Brake
#define PIN_EPM_TRIG          6    // AO3400A Gate (via R1=330R, C8=100nF, R6=47k RC watchdog)
#define PIN_DRV_FAULT         7    // DRV8833 nFAULT open-drain alert (pull-up R10=10k)
#define PIN_OPTICAL_TX        8    // Face Infrared LED Carrier Driver (38kHz hardware carrier)
#define PIN_OPTICAL_RX        9    // Face Infrared Demodulated Data Input
#define PIN_STATUS_LED        10   // Onboard Blue Status LED (D7 via R21=1k)
#define PIN_BATT_SENSE        11   // ADC1_CH0 Battery Voltage Divider (100k / 100k, Ratio = 2.0)
#define PIN_IMU_SDA           12   // MPU-6050 I2C Data (with 2.2k pull-up R3 + 33R damper R17)
#define PIN_IMU_SCL           13   // MPU-6050 I2C Clock (with 2.2k pull-up R4 + 33R damper R18)
#define PIN_FPC_FACE_CTRL     15   // 6-Face Modular FPC Multiplexer / Face Select
#define PIN_IMU_PWR_EN        21   // Q4 AO3401A P-MOSFET IMU Power Gate Cold-Reset (Active LOW)
#define PIN_IMU_INT           38   // MPU-6050 Motion Interrupt Line (TP25)
#define PIN_STATUS_WS2812     48   // Onboard RGB WS2812 status indicator

#else

// Legacy MVP Proto Pinout (Backward Compatibility)
#define PIN_MOTOR_IN1         4
#define PIN_MOTOR_IN2         5
#define PIN_EPM_TRIG          6
#define PIN_DRV_FAULT         7
#define PIN_IMU_SDA           8
#define PIN_IMU_SCL           9
#define PIN_OPTICAL_TX        15
#define PIN_OPTICAL_RX        16
#define PIN_BATT_SENSE        1
#define PIN_STATUS_LED        48
#define PIN_IMU_PWR_EN        21
#define PIN_IMU_INT           38

#endif

// ==========================================
// 2. FIRST-PRINCIPLES PHYSICAL CONSTANTS
// ==========================================
#define ROBOT_TOTAL_MASS_KG         0.085f    // Robot total mass: 85.0 grams
#define ROBOT_EDGE_LENGTH_M         0.050f    // Robot cubic envelope: 50.0 mm
#define FLYWHEEL_ROTOR_MASS_KG      0.022f    // Brass flywheel rotor mass: 22.0 grams
#define FLYWHEEL_ROTOR_INERTIA_YY   2.02e-6f  // J_rotor = 2.02 x 10^-6 kg*m^2
#define CHASSIS_PIVOT_INERTIA       1.417e-4f // J_pivot = 1.417 x 10^-4 kg*m^2
#define GRAVITY_BARRIER_JOULES      0.234f    // Potential energy barrier: m*g*R*(sqrt(2)-1)

// ==========================================
// 3. ACTUATION DYNAMICS & BRAKING PROFILE
// ==========================================
#define FLYWHEEL_TARGET_RPM         12000.0f  // Spinup speed: 1256.6 rad/s (Stored Ek0 = 1.60 J)
#define BRAKE_TORQUE_MAX_NM         0.25f     // Dynamic impulse counter-torque
#define BRAKE_PULSE_DURATION_MS     15.1f     // Time to transfer required barrier momentum
#define EPM_PULSE_DURATION_MS       5.0f      // Coil pulse width (AO3400A discharge)
#define EPM_HOLDING_FORCE_N         30.0f     // Ground EPM clamp force (SF = 1.61 vs slip)

// ==========================================
// 4. BATTERY & POWER SECURITY PARAMETERS
// ==========================================
#define BATT_ESR_OHMS               0.080f    // Internal cell resistance: 80 mOhm
#define BATT_MAX_VOLTAGE_V          4.20f     // 1S LiPo Full Charge
#define BATT_NOMINAL_VOLTAGE_V      3.70f     // 1S LiPo Nominal
#define BATT_CUTOFF_VOLTAGE_V       3.00f     // BMS Overdischarge threshold (DW01A: 2.8V with 150ms filter)
#define PEAK_BRAKE_CURRENT_A        13.88f    // Max transient dynamic brake current
#define SYSTEM_LDO_MIN_VIN_V        1.80f     // SGM2205 / TPS63805 dropout limit (Guaranteed 3.3V rail)

// ==========================================
// 5. FREERTOS TASK CYCLE TIMINGS (ms / Hz)
// ==========================================
#define FREQ_ATTITUDE_EKF_HZ        500       // Period = 2ms (Core 1, Priority 5)
#define FREQ_MOTOR_CONTROL_HZ       200       // Period = 5ms (Core 1, Priority 4)
#define FREQ_ROLL_FSM_HZ            50        // Period = 20ms (Core 0, Priority 3)
#define FREQ_OPTICAL_COMM_HZ        50        // Period = 20ms (Core 0, Priority 2)
#define FREQ_TELEMETRY_HZ           10        // Period = 100ms (Core 0, Priority 1)
