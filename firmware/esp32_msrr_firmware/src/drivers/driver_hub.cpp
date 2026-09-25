/**
 * @file driver_hub.cpp
 * @brief Implementation of Dynamic Driver Registry and Hot-Pluggable Face Slot Hub.
 * @author microUnit Robotics Open Source Team
 */

#include "drivers/driver_hub.h"
#include <cstring>
#include <cstdio>

namespace microunit {

DriverHub& DriverHub::getInstance() {
    static DriverHub instance;
    return instance;
}

DriverHub::DriverHub() : _driver_count(0) {
    for (size_t i = 0; i < MAX_DRIVERS; ++i) {
        _drivers[i] = nullptr;
    }
    for (size_t i = 0; i < NUM_FACE_SLOTS; ++i) {
        _slots[i].slot_id = static_cast<FaceSlot>(i);
        _slots[i].is_occupied = false;
        _slots[i].attached_device_id = 0;
        _slots[i].payload_name[0] = '\0';
        _slot_drivers[i] = nullptr;
    }
}

bool DriverHub::registerDriver(IDeviceDriver* driver) {
    if (!driver || _driver_count >= MAX_DRIVERS) {
        return false;
    }

    // Check for duplicate ID
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->getDeviceId() == driver->getDeviceId()) {
            return false; // Already registered
        }
    }

    _drivers[_driver_count++] = driver;
    return true;
}

bool DriverHub::unregisterDriver(uint8_t device_id) {
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->getDeviceId() == device_id) {
            // If running, stop it first
            if (_drivers[i]->isRunning()) {
                _drivers[i]->stop();
            }
            // Shift remaining drivers
            for (size_t j = i; j < _driver_count - 1; ++j) {
                _drivers[j] = _drivers[j + 1];
            }
            _drivers[--_driver_count] = nullptr;
            return true;
        }
    }
    return false;
}

IDeviceDriver* DriverHub::getDriver(uint8_t device_id) {
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->getDeviceId() == device_id) {
            return _drivers[i];
        }
    }
    return nullptr;
}

IDeviceDriver* DriverHub::getDriverByType(DeviceType type) {
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->getType() == type) {
            return _drivers[i];
        }
    }
    return nullptr;
}

size_t DriverHub::getDriverCount() const {
    return _driver_count;
}

bool DriverHub::attachSlotDevice(FaceSlot slot, IDeviceDriver* driver) {
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACE_SLOTS || !driver) {
        return false;
    }

    // Register into general driver list if not already present
    if (!getDriver(driver->getDeviceId())) {
        registerDriver(driver);
    }

    _slots[idx].is_occupied = true;
    _slots[idx].attached_device_id = driver->getDeviceId();
    strncpy(_slots[idx].payload_name, driver->getName(), sizeof(_slots[idx].payload_name) - 1);
    _slots[idx].payload_name[sizeof(_slots[idx].payload_name) - 1] = '\0';
    _slot_drivers[idx] = driver;

    return true;
}

bool DriverHub::detachSlotDevice(FaceSlot slot) {
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACE_SLOTS || !_slots[idx].is_occupied) {
        return false;
    }

    if (_slot_drivers[idx] && _slot_drivers[idx]->isRunning()) {
        _slot_drivers[idx]->stop();
    }

    _slots[idx].is_occupied = false;
    _slots[idx].attached_device_id = 0;
    _slots[idx].payload_name[0] = '\0';
    _slot_drivers[idx] = nullptr;

    return true;
}

IDeviceDriver* DriverHub::getSlotDevice(FaceSlot slot) {
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACE_SLOTS) {
        return nullptr;
    }
    return _slot_drivers[idx];
}

bool DriverHub::isSlotOccupied(FaceSlot slot) const {
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACE_SLOTS) {
        return false;
    }
    return _slots[idx].is_occupied;
}

const SlotDescriptor& DriverHub::getSlotInfo(FaceSlot slot) const {
    static const SlotDescriptor empty = { FaceSlot::FACE_INTERNAL, false, 0, "" };
    uint8_t idx = static_cast<uint8_t>(slot);
    if (idx >= NUM_FACE_SLOTS) {
        return empty;
    }
    return _slots[idx];
}

bool DriverHub::initAll() {
    bool all_ok = true;
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i]) {
            if (!_drivers[i]->init()) {
                all_ok = false;
            }
        }
    }
    return all_ok;
}

bool DriverHub::startAll() {
    bool all_ok = true;
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i]) {
            if (!_drivers[i]->start()) {
                all_ok = false;
            }
        }
    }
    return all_ok;
}

void DriverHub::stopAll() {
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->isRunning()) {
            _drivers[i]->stop();
        }
    }
}

void DriverHub::updateAll(float dt_seconds) {
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->isRunning()) {
            _drivers[i]->update(dt_seconds);
        }
    }
}

bool DriverHub::selfTestAll(uint32_t* failed_driver_mask) {
    bool all_pass = true;
    uint32_t mask = 0;

    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i]) {
            if (!_drivers[i]->selfTest()) {
                all_pass = false;
                mask |= (1 << i);
            }
        }
    }

    if (failed_driver_mask) {
        *failed_driver_mask = mask;
    }
    return all_pass;
}

size_t DriverHub::getHealthyCount() const {
    size_t count = 0;
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->getHealth() == DriverHealth::HEALTHY) {
            count++;
        }
    }
    return count;
}

size_t DriverHub::getFaultedCount() const {
    size_t count = 0;
    for (size_t i = 0; i < _driver_count; ++i) {
        if (_drivers[i] && _drivers[i]->getHealth() == DriverHealth::FAULTED) {
            count++;
        }
    }
    return count;
}

} // namespace microunit
