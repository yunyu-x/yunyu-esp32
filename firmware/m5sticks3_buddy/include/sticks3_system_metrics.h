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

inline float getChipTemperature() {
    return temperatureRead();
}

inline void printSystemDiagnostics() {
    static uint32_t s_last_diag = 0;
    if (millis() - s_last_diag >= 2000) {
        s_last_diag = millis();
        uint32_t free_sram = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
        uint32_t free_psram = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        uint32_t total_sram = (uint32_t)heap_caps_get_total_size(MALLOC_CAP_INTERNAL);
        uint32_t total_psram = (uint32_t)heap_caps_get_total_size(MALLOC_CAP_SPIRAM);

        // 1. 全局复合物理内存池负荷率 (8MB PSRAM + 320KB SRAM)
        float total_ram_mb = (float)(total_sram + total_psram) / (1024.0f * 1024.0f);
        float free_ram_mb = (float)(free_sram + free_psram) / (1024.0f * 1024.0f);
        float ram_overall_load = (total_ram_mb > 0) ? (1.0f - free_ram_mb / total_ram_mb) * 100.0f : 0.0f;

        // 2. 内部 SRAM 用户堆动态负荷率 (基于开机稳定基准堆)
        static uint32_t s_initial_free_sram = 0;
        if (s_initial_free_sram == 0 && free_sram > 0) {
            s_initial_free_sram = free_sram;
        }
        float sram_dyn_load = (s_initial_free_sram > 0) ? 
            ((float)(s_initial_free_sram - free_sram) / (float)s_initial_free_sram) * 100.0f : 0.0f;
        if (sram_dyn_load < 0.0f) sram_dyn_load = 0.0f;

        // 3. FreeRTOS 主循环任务栈负荷率 (8KB 栈)
        uint32_t max_block = (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL);
        uint32_t stack_hwm = (uint32_t)uxTaskGetStackHighWaterMark(NULL);
        float stack_load = (8192 > stack_hwm) ? ((float)(8192 - stack_hwm) / 8192.0f) * 100.0f : 0.0f;
        float chip_temp = temperatureRead();

        Serial.printf("[StickS3-SYS] FPS: %.1f | Temp: %.1fC | RAM: free=%.2fMB (Load: %.1f%%) | SRAM: free=%uKB, max_block=%uKB (DynLoad: %.1f%%) | Stack: free=%uB (Load: %.1f%%) | I2C_Tx: %lu (Fails: %lu)\n",
                      getSystemLoopFPS(),
                      chip_temp,
                      free_ram_mb,
                      ram_overall_load,
                      (unsigned)(free_sram / 1024),
                      (unsigned)(max_block / 1024),
                      sram_dyn_load,
                      (unsigned)stack_hwm,
                      stack_load,
                      (unsigned long)getI2CTransactionCount(),
                      (unsigned long)getI2CLockFailures());
    }
}

} // namespace sticks3
