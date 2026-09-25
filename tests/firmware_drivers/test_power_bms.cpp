/**
 * @file test_power_bms.cpp
 * @brief TDD Unit tests for Power & Battery Management System (BMS) Driver.
 */

#include <cassert>
#include <cstdio>
#include <cmath>
#include "hal/mock_hal.h"
#include "drivers/power_bms.h"

using namespace microunit;

void test_bms_init_and_self_test() {
    printf("[TDD BMS] Running test_bms_init_and_self_test...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    // Normal battery voltage: 3.85V -> pin voltage = 3.85 / 2.0 = 1.925V
    hal.setAdcVoltage(11, 1.925f);

    PowerBmsDriver bms(11, 2.0f); // Pin 11, divider ratio 2.0
    assert(bms.getType() == DeviceType::SENSOR_POWER_BMS);
    assert(bms.getDeviceId() == 4);
    assert(bms.getHealth() == DriverHealth::UNINITIALIZED);

    assert(bms.init() == true);
    assert(bms.getHealth() == DriverHealth::HEALTHY);
    assert(bms.selfTest() == true);

    // Initial reading
    float vbat = bms.getBatteryVoltage();
    assert(std::abs(vbat - 3.85f) < 0.05f);

    printf("  -> PASS: BMS init, ADC sampling and self-test verified.\n");
}

void test_bms_soc_estimation() {
    printf("[TDD BMS] Running test_bms_soc_estimation...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    PowerBmsDriver bms(11, 2.0f);
    bms.init();
    bms.start();

    // 1. Full Charge (4.20V -> pin 2.10V)
    hal.setAdcVoltage(11, 2.10f);
    for (int i = 0; i < 20; ++i) bms.update(0.01f);
    assert(bms.getBatteryVoltage() >= 4.18f);
    assert(bms.getSocPercent() >= 98.0f);

    // 2. Nominal Plateau (3.75V -> pin 1.875V)
    hal.setAdcVoltage(11, 1.875f);
    for (int i = 0; i < 25; ++i) bms.update(0.01f);
    float soc_nom = bms.getSocPercent();
    assert(soc_nom >= 35.0f && soc_nom <= 55.0f);

    // 3. Low Battery (3.30V -> pin 1.65V)
    hal.setAdcVoltage(11, 1.65f);
    for (int i = 0; i < 25; ++i) bms.update(0.01f);
    assert(bms.getSocPercent() < 10.0f);

    printf("  -> PASS: BMS SOC non-linear look-up estimation verified.\n");
}

void test_bms_under_voltage_sag_alert() {
    printf("[TDD BMS] Running test_bms_under_voltage_sag_alert...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    PowerBmsDriver bms(11, 2.0f);
    bms.init();
    bms.start();

    // Inject deep under-voltage sag (2.85V -> pin 1.425V)
    hal.setAdcVoltage(11, 1.425f);
    for (int i = 0; i < 20; ++i) bms.update(0.01f);

    assert(bms.getHealth() == DriverHealth::FAULTED);
    assert(bms.getErrorCode() & static_cast<uint32_t>(DriverErrorCode::ERR_UNDER_VOLTAGE));
    assert(bms.isCriticalLow() == true);

    // Restore voltage to normal (3.80V) and recover
    hal.setAdcVoltage(11, 1.90f);
    for (int i = 0; i < 20; ++i) bms.update(0.01f);
    assert(bms.recover(static_cast<uint32_t>(DriverErrorCode::ERR_UNDER_VOLTAGE)) == true);
    assert(bms.getHealth() == DriverHealth::HEALTHY);

    printf("  -> PASS: BMS under-voltage sag alert and recovery verified.\n");
}

int main() {
    printf("====================================================\n");
    printf("  TDD Suite: Power & Battery Management System (BMS) \n");
    printf("====================================================\n");
    test_bms_init_and_self_test();
    test_bms_soc_estimation();
    test_bms_under_voltage_sag_alert();
    printf(">> ALL BMS TESTS PASSED SUCCESSFULLY! <<\n");
    return 0;
}
