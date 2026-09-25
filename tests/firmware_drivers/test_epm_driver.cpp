/**
 * @file test_epm_driver.cpp
 * @brief TDD Unit tests for Electropermanent Magnet (EPM) Actuator Driver.
 */

#include <cassert>
#include <cstdio>
#include "hal/mock_hal.h"
#include "drivers/epm_driver.h"

using namespace microunit;

void test_epm_init_and_self_test() {
    printf("[TDD EPM] Running test_epm_init_and_self_test...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    EpmDriver epm(6); // GPIO6
    assert(epm.getType() == DeviceType::ACTUATOR_EPM);
    assert(epm.getDeviceId() == 2);
    assert(epm.getHealth() == DriverHealth::UNINITIALIZED);

    assert(epm.init() == true);
    assert(epm.getHealth() == DriverHealth::HEALTHY);
    assert(epm.selfTest() == true);

    // Initial state: gate pin must be LOW, detached
    assert(hal.getPinLevel(6) == HAL_LEVEL_LOW);
    assert(epm.isAnchored() == false);
    assert(epm.getHoldingForceN() == 0.0f);

    printf("  -> PASS: EPM init and self-test verified.\n");
}

void test_epm_magnetize_pulse_timing() {
    printf("[TDD EPM] Running test_epm_magnetize_pulse_timing...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    EpmDriver epm(6);
    epm.init();
    epm.start();

    // Trigger magnetization pulse (5.0 ms default)
    assert(epm.pulseMagnetize(5.0f) == true);
    assert(epm.isPulsing() == true);
    assert(hal.getPinLevel(6) == HAL_LEVEL_HIGH);

    // Advance 2ms (mid-pulse)
    epm.update(0.002f);
    assert(epm.isPulsing() == true);
    assert(hal.getPinLevel(6) == HAL_LEVEL_HIGH);

    // Advance another 3.5ms (total 5.5ms, past pulse duration)
    epm.update(0.0035f);
    assert(epm.isPulsing() == false);
    assert(hal.getPinLevel(6) == HAL_LEVEL_LOW);

    // Now state should be ANCHORED with holding force >= 30.0 N
    assert(epm.isAnchored() == true);
    assert(epm.getHoldingForceN() >= 30.0f);

    printf("  -> PASS: EPM 5.0ms magnetization pulse verified.\n");
}

void test_epm_demagnetize_pulse() {
    printf("[TDD EPM] Running test_epm_demagnetize_pulse...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    EpmDriver epm(6);
    epm.init();
    epm.start();

    // Pre-condition: anchored
    epm.pulseMagnetize(5.0f);
    epm.update(0.006f);
    assert(epm.isAnchored() == true);

    // Advance 250ms past thermal cooldown period
    epm.update(0.250f);

    // Trigger demagnetization pulse
    assert(epm.pulseDemagnetize(5.0f) == true);
    assert(epm.isPulsing() == true);
    assert(hal.getPinLevel(6) == HAL_LEVEL_HIGH);

    // Complete pulse
    epm.update(0.006f);
    assert(epm.isPulsing() == false);
    assert(hal.getPinLevel(6) == HAL_LEVEL_LOW);

    // Now detached, force = 0N
    assert(epm.isAnchored() == false);
    assert(epm.getHoldingForceN() == 0.0f);

    printf("  -> PASS: EPM demagnetization verified.\n");
}

void test_epm_thermal_cooldown_and_watchdog() {
    printf("[TDD EPM] Running test_epm_thermal_cooldown_and_watchdog...\n");
    MockHal& hal = MockHal::getInstance();
    hal.reset();

    EpmDriver epm(6);
    epm.init();
    epm.start();

    // Pulse 1
    epm.pulseMagnetize(5.0f);
    epm.update(0.006f);

    // Attempting to pulse immediately within cooldown window (e.g. 50ms) must be rejected
    epm.update(0.050f); // only 50ms elapsed, cooldown requires 200ms
    assert(epm.pulseDemagnetize(5.0f) == false);

    // Advance past remaining cooldown
    epm.update(0.160f); // 50ms + 160ms = 210ms > 200ms
    assert(epm.pulseDemagnetize(5.0f) == true);

    printf("  -> PASS: EPM thermal cooldown rate limiting verified.\n");
}

int main() {
    printf("====================================================\n");
    printf("  TDD Suite: Electropermanent Magnet (EPM) Driver    \n");
    printf("====================================================\n");
    test_epm_init_and_self_test();
    test_epm_magnetize_pulse_timing();
    test_epm_demagnetize_pulse();
    test_epm_thermal_cooldown_and_watchdog();
    printf(">> ALL EPM TESTS PASSED SUCCESSFULLY! <<\n");
    return 0;
}
