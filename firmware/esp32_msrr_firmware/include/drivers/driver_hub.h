/**
 * @file driver_hub.h
 * @brief Dynamic Driver Registry and Hot-Pluggable Face Slot Hub.
 * @details Supports dynamic driver registration, hot-pluggable face attachments,
 *          and capacity scaling for modular robotics expansion.
 * @author microUnit Robotics Open Source Team
 */

#pragma once

#include "driver_interface.h"
#include <vector>
#include <memory>
#include <functional>

namespace microunit {

enum class FaceSlot : uint8_t {
    FACE_POS_X = 0,  // +X Face (FPC J4)
    FACE_NEG_X = 1,  // -X Face (FPC J5)
    FACE_POS_Y = 2,  // +Y Face (FPC J6)
    FACE_NEG_Y = 3,  // -Y Face (FPC J7)
    FACE_POS_Z = 4,  // +Z Face (FPC J8)
    FACE_NEG_Z = 5,  // -Z Face (FPC J9)
    FACE_INTERNAL = 255 // Internal chassis device (not on outer face)
};

struct SlotDescriptor {
    FaceSlot slot_id;
    bool is_occupied;
    uint8_t attached_device_id;
    char payload_name[32];
};

class DriverHub {
public:
    static constexpr size_t MAX_DRIVERS = 32;
    static constexpr size_t NUM_FACE_SLOTS = 6;

    DriverHub();
    ~DriverHub() = default;

    // Singleton accessor for global hub
    static DriverHub& getInstance();

    // Driver Registration & Management (Extensibility & Scaling)
    bool registerDriver(IDeviceDriver* driver);
    bool unregisterDriver(uint8_t device_id);
    IDeviceDriver* getDriver(uint8_t device_id);
    IDeviceDriver* getDriverByType(DeviceType type);
    size_t getDriverCount() const;

    // Hot-Pluggable Face Slot Management (Plug & Play)
    bool attachSlotDevice(FaceSlot slot, IDeviceDriver* driver);
    bool detachSlotDevice(FaceSlot slot);
    IDeviceDriver* getSlotDevice(FaceSlot slot);
    bool isSlotOccupied(FaceSlot slot) const;
    const SlotDescriptor& getSlotInfo(FaceSlot slot) const;

    // Bulk Lifecycle & Dispatch
    bool initAll();
    bool startAll();
    void stopAll();
    void updateAll(float dt_seconds);
    bool selfTestAll(uint32_t* failed_driver_mask = nullptr);

    // Diagnostics & Inspection
    size_t getHealthyCount() const;
    size_t getFaultedCount() const;

private:
    IDeviceDriver* _drivers[MAX_DRIVERS];
    size_t _driver_count;

    SlotDescriptor _slots[NUM_FACE_SLOTS];
    IDeviceDriver* _slot_drivers[NUM_FACE_SLOTS];
};

} // namespace microunit
