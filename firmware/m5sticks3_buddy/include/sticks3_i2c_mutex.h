#pragma once
#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

namespace sticks3 {

// 全局 I2C 总线互斥锁句柄
inline SemaphoreHandle_t& getI2CMutex() {
    static SemaphoreHandle_t s_mutex = nullptr;
    if (!s_mutex) {
        s_mutex = xSemaphoreCreateMutex();
    }
    return s_mutex;
}

// 统计 I2C 锁竞争与冲突指标
inline volatile uint32_t& getI2CLockFailures() {
    static volatile uint32_t s_lock_fails = 0;
    return s_lock_fails;
}

inline volatile uint32_t& getI2CTransactionCount() {
    static volatile uint32_t s_tx_count = 0;
    return s_tx_count;
}

// RAII 风格 I2C 锁守卫
class I2CLockGuard {
public:
    explicit I2CLockGuard(uint32_t timeout_ms = 50) : _acquired(false) {
        SemaphoreHandle_t mux = getI2CMutex();
        if (mux) {
            if (xSemaphoreTake(mux, pdMS_TO_TICKS(timeout_ms)) == pdTRUE) {
                _acquired = true;
                getI2CTransactionCount()++;
            } else {
                getI2CLockFailures()++;
            }
        }
    }

    ~I2CLockGuard() {
        if (_acquired) {
            SemaphoreHandle_t mux = getI2CMutex();
            if (mux) {
                xSemaphoreGive(mux);
            }
        }
    }

    bool isAcquired() const { return _acquired; }

private:
    bool _acquired;
};

} // namespace sticks3
