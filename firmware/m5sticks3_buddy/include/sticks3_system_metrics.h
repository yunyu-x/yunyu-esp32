#pragma once
#include <Arduino.h>
#include <esp_heap_caps.h>
#include "sticks3_i2c_mutex.h"

namespace sticks3 {

inline float& getSystemLoopFPS() {
    static float s_fps = 0.0f;
    return s_fps;
}

inline void updateSystemLoopFPS() {
    static uint32_t s_last_time = 0;
    static uint32_t s_frames = 0;
    s_frames++;
    uint32_t now = millis();
    if (now - s_last_time >= 1000) {
        getSystemLoopFPS() = (float)s_frames * 1000.0f / (float)(now - s_last_time);
        s_frames = 0;
        s_last_time = now;
    }
}

inline void printSystemDiagnostics() {
    static uint32_t s_last_diag = 0;
    if (millis() - s_last_diag >= 2000) {
        s_last_diag = millis();
        uint32_t free_sram = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
        uint32_t max_block = (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL);
        uint32_t free_psram = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        uint32_t stack_hwm = (uint32_t)uxTaskGetStackHighWaterMark(NULL);
        Serial.printf("[StickS3-SYS] FPS: %.1f | SRAM: free=%uKB, max_block=%uKB | PSRAM: %.2fMB | LoopStack: %uB | I2C_Tx: %lu (Fails: %lu)\n",
                      getSystemLoopFPS(),
                      (unsigned)(free_sram / 1024),
                      (unsigned)(max_block / 1024),
                      (float)free_psram / (1024.0f * 1024.0f),
                      (unsigned)stack_hwm,
                      (unsigned long)getI2CTransactionCount(),
                      (unsigned long)getI2CLockFailures());
    }
}

} // namespace sticks3
