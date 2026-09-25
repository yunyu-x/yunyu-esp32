/**
 * @file test_driver_hub.cpp
 * @brief TDD Unit tests for DriverHub and Dynamic Hot-Pluggable Registry.
 */

#include <cassert>
#include <cstdio>
#include <cstring>
#include "drivers/driver_hub.h"

using namespace microunit;

class MockTestDriver : public IDeviceDriver {
public:
    MockTestDriver(uint8_t id, DeviceType type, const char* name)
        : _id(id), _type(type), _name(name), _health(DriverHealth::UNINITIALIZED),
          _running(false), _init_calls(0), _start_calls(0), _stop_calls(0),
          _update_calls(0), _self_test_calls(0), _should_fail_self_test(false) {}

    const char* getName() const override { return _name; }
    DeviceType getType() const override { return _type; }
    uint8_t getDeviceId() const override { return _id; }

    bool init() override {
        _init_calls++;
        _health = DriverHealth::HEALTHY;
        return true;
    }

    bool start() override {
        _start_calls++;
        _running = true;
        return true;
    }

    void stop() override {
        _stop_calls++;
        _running = false;
    }

    void update(float dt_seconds) override {
        (void)dt_seconds;
        _update_calls++;
    }

    bool selfTest() override {
        _self_test_calls++;
        if (_should_fail_self_test) {
            _health = DriverHealth::FAULTED;
            return false;
        }
        _health = DriverHealth::HEALTHY;
        return true;
    }

    DriverHealth getHealth() const override { return _health; }
    uint32_t getErrorCode() const override { return _health == DriverHealth::FAULTED ? 1 : 0; }
    bool recover(uint32_t fault_mask) override {
        (void)fault_mask;
        _health = DriverHealth::HEALTHY;
        return true;
    }
    bool isRunning() const override { return _running; }

    void setFailSelfTest(bool fail) { _should_fail_self_test = fail; }
    int getInitCalls() const { return _init_calls; }
    int getUpdateCalls() const { return _update_calls; }

private:
    uint8_t _id;
    DeviceType _type;
    const char* _name;
    DriverHealth _health;
    bool _running;
    int _init_calls;
    int _start_calls;
    int _stop_calls;
    int _update_calls;
    int _self_test_calls;
    bool _should_fail_self_test;
};

void test_driver_registration_and_lookup() {
    printf("[TDD Hub] Running test_driver_registration_and_lookup...\n");
    DriverHub hub;

    MockTestDriver drv1(10, DeviceType::ACTUATOR_MOTOR, "MockMotor");
    MockTestDriver drv2(11, DeviceType::ACTUATOR_EPM, "MockEpm");

    assert(hub.getDriverCount() == 0);
    assert(hub.registerDriver(&drv1) == true);
    assert(hub.registerDriver(&drv2) == true);
    assert(hub.getDriverCount() == 2);

    // Duplicate registration should be rejected
    assert(hub.registerDriver(&drv1) == false);

    // Query by ID
    IDeviceDriver* found = hub.getDriver(10);
    assert(found != nullptr);
    assert(strcmp(found->getName(), "MockMotor") == 0);

    // Query by Type
    IDeviceDriver* found_type = hub.getDriverByType(DeviceType::ACTUATOR_EPM);
    assert(found_type != nullptr);
    assert(found_type->getDeviceId() == 11);

    // Unregister
    assert(hub.unregisterDriver(10) == true);
    assert(hub.getDriverCount() == 1);
    assert(hub.getDriver(10) == nullptr);
    printf("  -> PASS: Registration and lookup verified.\n");
}

void test_hot_pluggable_face_slots() {
    printf("[TDD Hub] Running test_hot_pluggable_face_slots...\n");
    DriverHub hub;

    MockTestDriver faceXPos(1, DeviceType::COMM_OPTICAL_FACE, "OpticalFace_PosX");
    MockTestDriver faceYNeg(2, DeviceType::COMM_OPTICAL_FACE, "OpticalFace_NegY");

    assert(hub.isSlotOccupied(FaceSlot::FACE_POS_X) == false);

    // Attach to +X slot
    assert(hub.attachSlotDevice(FaceSlot::FACE_POS_X, &faceXPos) == true);
    assert(hub.isSlotOccupied(FaceSlot::FACE_POS_X) == true);
    assert(hub.getSlotDevice(FaceSlot::FACE_POS_X) == &faceXPos);

    // Attach to -Y slot
    assert(hub.attachSlotDevice(FaceSlot::FACE_NEG_Y, &faceYNeg) == true);
    assert(hub.isSlotOccupied(FaceSlot::FACE_NEG_Y) == true);

    // Detach from +X slot
    assert(hub.detachSlotDevice(FaceSlot::FACE_POS_X) == true);
    assert(hub.isSlotOccupied(FaceSlot::FACE_POS_X) == false);
    assert(hub.getSlotDevice(FaceSlot::FACE_POS_X) == nullptr);
    printf("  -> PASS: Hot-pluggable face slots attach/detach verified.\n");
}

void test_bulk_lifecycle_and_diagnostics() {
    printf("[TDD Hub] Running test_bulk_lifecycle_and_diagnostics...\n");
    DriverHub hub;

    MockTestDriver drv1(10, DeviceType::ACTUATOR_MOTOR, "MockMotor");
    MockTestDriver drv2(11, DeviceType::SENSOR_IMU, "MockImu");
    hub.registerDriver(&drv1);
    hub.registerDriver(&drv2);

    // Bulk init
    assert(hub.initAll() == true);
    assert(drv1.getInitCalls() == 1);
    assert(drv2.getInitCalls() == 1);

    // Bulk start
    assert(hub.startAll() == true);
    assert(drv1.isRunning() == true);
    assert(drv2.isRunning() == true);

    // Bulk update
    hub.updateAll(0.01f);
    assert(drv1.getUpdateCalls() == 1);
    assert(drv2.getUpdateCalls() == 1);

    // Self test all pass
    uint32_t failed_mask = 0;
    assert(hub.selfTestAll(&failed_mask) == true);
    assert(failed_mask == 0);
    assert(hub.getHealthyCount() == 2);
    assert(hub.getFaultedCount() == 0);

    // Simulate fault injection
    drv2.setFailSelfTest(true);
    assert(hub.selfTestAll(&failed_mask) == false);
    assert(hub.getFaultedCount() == 1);
    assert(hub.getHealthyCount() == 1);

    // Stop all
    hub.stopAll();
    assert(drv1.isRunning() == false);
    assert(drv2.isRunning() == false);
    printf("  -> PASS: Bulk lifecycle and diagnostic self-test verified.\n");
}

int main() {
    printf("====================================================\n");
    printf("  TDD Suite: DriverHub & Hot-Pluggable Architecture  \n");
    printf("====================================================\n");
    test_driver_registration_and_lookup();
    test_hot_pluggable_face_slots();
    test_bulk_lifecycle_and_diagnostics();
    printf(">> ALL HUB TESTS PASSED SUCCESSFULLY! <<\n");
    return 0;
}
