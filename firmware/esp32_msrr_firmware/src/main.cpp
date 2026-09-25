/**
 * @file main.cpp
 * @brief microUnit ESP32-S3 FreeRTOS Modular Self-Reconfigurable Robot Firmware.
 * @author microUnit Robotics Open Source Team
 * @date 2026-09-13
 */

#include <Arduino.h>
#include <Wire.h>
#include "config.h"
#include "drivers/motor_mcpwm.h"
#include "drivers/epm_driver.h"
#include "filters/attitude_ekf.h"
#include "controllers/roll_fsm.h"
#include "comm/optical_comm.h"

// Hardware driver and algorithm singletons
static FlywheelMotorDriver motor_driver;
static EpmDriver epm_driver;
static AttitudeEstimator attitude_estimator;
static RollFsmController roll_controller(&motor_driver, &epm_driver, &attitude_estimator);
static OpticalTransceiver optical_transceiver(1); // Robot ID = 1

// Telemetry & Sensor State
static volatile float g_batt_voltage = 3.85f;
static volatile float g_accel_x = 0.0f, g_accel_y = 0.0f, g_accel_z = 1.0f;
static volatile float g_gyro_x = 0.0f, g_gyro_y = 0.0f, g_gyro_z = 0.0f;

// Mutex for thread-safe telemetry access
static SemaphoreHandle_t xTelemetryMutex = NULL;

// ==========================================
// 1. CORE 1 HIGH-FREQUENCY RTOS TASKS
// ==========================================

/**
 * @brief Attitude estimation task running at 500 Hz (2ms period) on Core 1.
 */
void Task_Attitude_EKF(void* pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(2); // 500 Hz

    attitude_estimator.init();

    for (;;) {
        // Read simulated/real IMU data (In production, replace with Wire.requestFrom / MPU6050 FIFO)
        float ax = g_accel_x;
        float ay = g_accel_y;
        float az = g_accel_z;
        float gx = g_gyro_x;
        float gy = g_gyro_y;
        float gz = g_gyro_z;

        attitude_estimator.update(ax, ay, az, gx, gy, gz, 0.002f);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

/**
 * @brief Motor control & dynamic braking task running at 200 Hz (5ms period) on Core 1.
 */
void Task_Motor_Control(void* pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(5); // 200 Hz

    motor_driver.init();
    epm_driver.init();

    for (;;) {
        motor_driver.update(0.005f);
        epm_driver.update(0.005f);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

// ==========================================
// 2. CORE 0 SUPERVISORY & TELEMETRY TASKS
// ==========================================

/**
 * @brief Roll locomotion finite state machine running at 50 Hz (20ms period) on Core 0.
 */
void Task_Roll_FSM(void* pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(20); // 50 Hz

    roll_controller.init();

    for (;;) {
        roll_controller.update(0.020f);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

/**
 * @brief Optical face heartbeat broadcasting at 50 Hz (20ms period) on Core 0.
 */
void Task_Optical_Heartbeat(void* pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(20); // 50 Hz

    optical_transceiver.init();

    for (;;) {
        uint16_t vbat_mv = (uint16_t)(g_batt_voltage * 1000.0f);
        optical_transceiver.broadcastHeartbeat((uint8_t)roll_controller.getState(), vbat_mv);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

/**
 * @brief Telemetry streaming task running at 10 Hz (100ms period) on Core 0.
 */
void Task_Telemetry_Stream(void* pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(100); // 10 Hz

    for (;;) {
        // Read Battery ADC (GPIO1)
        int raw_adc = analogRead(PIN_BATT_SENSE);
        // Voltage divider 100k:100k -> 2.0x, ADC reference 3.3V / 4095
        float sensed_vbat = (raw_adc / 4095.0f) * 3.3f * 2.0f;
        if (sensed_vbat > 2.0f && sensed_vbat < 4.5f) {
            g_batt_voltage = 0.95f * g_batt_voltage + 0.05f * sensed_vbat;
        }

        // Output JSON Telemetry over USB Serial
        Serial.printf("{\"state\":\"%s\",\"roll\":%.2f,\"rpm\":%.1f,\"epm\":%d,\"vbat\":%.3f,\"rolls\":%d}\r\n",
            roll_controller.getStateName(),
            attitude_estimator.getRollDeg(),
            motor_driver.getCurrentRpm(),
            epm_driver.isAnchored() ? 1 : 0,
            g_batt_voltage,
            roll_controller.getSuccessfulRollCount()
        );

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

// ==========================================
// 3. SYSTEM INITIALIZATION & DISPATCH
// ==========================================

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\r\n=======================================================");
    Serial.println("  microUnit MSRR First-Principles Firmware Booting...  ");
    Serial.println("  Dual-Core ESP32-S3 (240MHz) | FreeRTOS Preemptive     ");
    Serial.println("=======================================================");

    // Initialize I2C bus for MPU-6050
    Wire.begin(PIN_IMU_SDA, PIN_IMU_SCL, 400000); // 400 kHz Fast-Mode

    // Initialize Mutex
    xTelemetryMutex = xSemaphoreCreateMutex();

    // Spawn Core 1 Real-Time Tasks
    xTaskCreatePinnedToCore(
        Task_Attitude_EKF,
        "AttitudeEKF",
        4096,
        NULL,
        5, // Highest Priority
        NULL,
        1  // Core 1
    );

    xTaskCreatePinnedToCore(
        Task_Motor_Control,
        "MotorCtrl",
        4096,
        NULL,
        4, // High Priority
        NULL,
        1  // Core 1
    );

    // Spawn Core 0 Supervisory Tasks
    xTaskCreatePinnedToCore(
        Task_Roll_FSM,
        "RollFSM",
        4096,
        NULL,
        3, // Normal Priority
        NULL,
        0  // Core 0
    );

    xTaskCreatePinnedToCore(
        Task_Optical_Heartbeat,
        "OpticalComm",
        2048,
        NULL,
        2, // Low Priority
        NULL,
        0  // Core 0
    );

    xTaskCreatePinnedToCore(
        Task_Telemetry_Stream,
        "Telemetry",
        4096,
        NULL,
        1, // Lowest Priority
        NULL,
        0  // Core 0
    );

    Serial.println("[BOOT] All 5 FreeRTOS tasks successfully spawned across dual cores.");
}

void loop() {
    // Check for user command over Serial (e.g., 'R' for Roll Trigger)
    if (Serial.available()) {
        char cmd = (char)Serial.read();
        if (cmd == 'R' || cmd == 'r') {
            Serial.println("[CMD] Received Roll Command! Dispatching to Roll FSM...");
            roll_controller.triggerRollManeuver(1);
        }
    }
    vTaskDelay(pdMS_TO_TICKS(50));
}
