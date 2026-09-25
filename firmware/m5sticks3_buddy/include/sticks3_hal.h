#ifndef STICKS3_HAL_H
#define STICKS3_HAL_H

#include <stdint.h>
#include <string>
#include <vector>

namespace sticks3 {

// 按键物理与事件状态
enum class ButtonEvent {
    NONE = 0,
    CLICK,
    DOUBLE_CLICK,
    LONG_PRESS,
    RELEASE
};

// 按钮防抖与长按状态机
class ButtonStateMachine {
public:
    ButtonStateMachine(uint32_t debounce_ms = 20, uint32_t long_press_ms = 1000);

    // 周期性轮询（入参：当前时间戳与物理电平状态 0:按下, 1:释放）
    ButtonEvent update(uint32_t current_time_ms, bool is_physically_pressed);

    bool isPressed() const { return _is_pressed; }
    bool isLongPressed() const { return _long_press_triggered; }
    void reset();

private:
    uint32_t _debounce_ms;
    uint32_t _long_press_ms;
    bool _is_pressed;
    bool _long_press_triggered;
    uint32_t _press_start_time;
    uint32_t _last_change_time;
    bool _last_raw_state;
};

// M5PM1 电源门控与电量管理
class PowerManager {
public:
    PowerManager();

    void setExtOutput(bool enable);
    bool getExtOutput() const { return _ext_5v_enabled; }

    void updateBatteryVoltage(float v_bat);
    float getBatteryVoltage() const { return _battery_voltage; }
    uint8_t getBatteryPercentage() const;
    bool isLowBattery() const { return _battery_voltage < 3.40f; }

private:
    bool _ext_5v_enabled;
    float _battery_voltage;
};

// 屏幕渲染模式
enum class ScreenMode {
    IDLE = 0,
    WORKING,
    PERMISSION_PROMPT,
    ROBOT_TELEMETRY
};

// ST7789 显存双缓冲与页面渲染引擎
class DisplayEngine {
public:
    DisplayEngine(uint16_t width = 135, uint16_t height = 240);

    void setMode(ScreenMode mode);
    ScreenMode getMode() const { return _mode; }

    void setStatusText(const std::string& status) { _status_text = status; }
    const std::string& getStatusText() const { return _status_text; }

    void setPrompt(const std::string& tool, const std::string& cmd, const std::string& req_id);
    const std::string& getPromptTool() const { return _prompt_tool; }
    const std::string& getPromptCommand() const { return _prompt_command; }
    const std::string& getPromptReqId() const { return _prompt_req_id; }

    void setTelemetry(const std::string& unit_id, float roll, float pitch, float v_bus);
    const std::string& getTelemetryUnitId() const { return _telem_unit_id; }

    // 渲染一帧数据并返回渲染特征摘要 (用于断言测试与实机传输)
    std::string renderFrame();

private:
    uint16_t _width;
    uint16_t _height;
    ScreenMode _mode;
    std::string _status_text;
    std::string _prompt_tool;
    std::string _prompt_command;
    std::string _prompt_req_id;
    std::string _telem_unit_id;
    float _telem_roll;
    float _telem_pitch;
    float _telem_vbus;
    uint32_t _frame_count;
};

// StickS3 全局硬件抽象中枢
class StickS3HAL {
public:
    StickS3HAL();
    bool init();

    ButtonStateMachine btnA; // 正面主键 (G21)
    ButtonStateMachine btnB; // 侧面副键 (G38/G0)
    PowerManager power;
    DisplayEngine display;

    // 6轴姿态数据更新
    void updateIMU(float ax, float ay, float az, float gx, float gy, float gz);
    float getRoll() const { return _roll; }
    float getPitch() const { return _pitch; }

private:
    bool _initialized;
    float _ax, _ay, _az;
    float _gx, _gy, _gz;
    float _roll, _pitch;
};

} // namespace sticks3

#endif // STICKS3_HAL_H
