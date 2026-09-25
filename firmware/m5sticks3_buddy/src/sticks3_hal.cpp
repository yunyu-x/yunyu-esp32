#include "sticks3_hal.h"
#include <cmath>
#include <sstream>
#include <iomanip>

namespace sticks3 {

// ==========================================
// 1. ButtonStateMachine 实现
// ==========================================

ButtonStateMachine::ButtonStateMachine(uint32_t debounce_ms, uint32_t long_press_ms)
    : _debounce_ms(debounce_ms),
      _long_press_ms(long_press_ms),
      _is_pressed(false),
      _long_press_triggered(false),
      _press_start_time(0),
      _last_change_time(0),
      _last_raw_state(false) {}

ButtonEvent ButtonStateMachine::update(uint32_t current_time_ms, bool is_physically_pressed) {
    ButtonEvent event = ButtonEvent::NONE;

    // 检测原始物理电平变化
    if (is_physically_pressed != _last_raw_state) {
        _last_change_time = current_time_ms;
        _last_raw_state = is_physically_pressed;
    }

    // 防抖判定
    if ((current_time_ms - _last_change_time) >= _debounce_ms) {
        if (is_physically_pressed && !_is_pressed) {
            // 确认按下
            _is_pressed = true;
            _press_start_time = current_time_ms;
            _long_press_triggered = false;
        } else if (!is_physically_pressed && _is_pressed) {
            // 确认释放
            _is_pressed = false;
            if (!_long_press_triggered) {
                event = ButtonEvent::CLICK;
            } else {
                event = ButtonEvent::RELEASE;
            }
        }
    }

    // 长按检测
    if (_is_pressed && !_long_press_triggered) {
        if ((current_time_ms - _press_start_time) >= _long_press_ms) {
            _long_press_triggered = true;
            event = ButtonEvent::LONG_PRESS;
        }
    }

    return event;
}

void ButtonStateMachine::reset() {
    _is_pressed = false;
    _long_press_triggered = false;
    _press_start_time = 0;
    _last_change_time = 0;
    _last_raw_state = false;
}

// ==========================================
// 2. PowerManager 实现
// ==========================================

PowerManager::PowerManager()
    : _ext_5v_enabled(false),
      _battery_voltage(3.85f) {}

void PowerManager::setExtOutput(bool enable) {
    _ext_5v_enabled = enable;
}

void PowerManager::updateBatteryVoltage(float v_bat) {
    if (v_bat < 0.0f) v_bat = 0.0f;
    if (v_bat > 4.35f) v_bat = 4.35f;
    _battery_voltage = v_bat;
}

uint8_t PowerManager::getBatteryPercentage() const {
    // 简易锂电池电压估算 (3.40V -> 0%, 4.20V -> 100%)
    if (_battery_voltage <= 3.40f) return 0;
    if (_battery_voltage >= 4.20f) return 100;
    float pct = (_battery_voltage - 3.40f) / (4.20f - 3.40f) * 100.0f;
    return static_cast<uint8_t>(pct);
}

// ==========================================
// 3. DisplayEngine 实现
// ==========================================

DisplayEngine::DisplayEngine(uint16_t width, uint16_t height)
    : _width(width),
      _height(height),
      _mode(ScreenMode::IDLE),
      _status_text("IDLE"),
      _prompt_tool(""),
      _prompt_command(""),
      _prompt_req_id(""),
      _telem_unit_id(""),
      _telem_roll(0.0f),
      _telem_pitch(0.0f),
      _telem_vbus(0.0f),
      _frame_count(0) {}

void DisplayEngine::setMode(ScreenMode mode) {
    _mode = mode;
}

void DisplayEngine::setPrompt(const std::string& tool, const std::string& cmd, const std::string& req_id) {
    _prompt_tool = tool;
    _prompt_command = cmd;
    _prompt_req_id = req_id;
    _mode = ScreenMode::PERMISSION_PROMPT;
}

void DisplayEngine::setTelemetry(const std::string& unit_id, float roll, float pitch, float v_bus) {
    _telem_unit_id = unit_id;
    _telem_roll = roll;
    _telem_pitch = pitch;
    _telem_vbus = v_bus;
    _mode = ScreenMode::ROBOT_TELEMETRY;
}

std::string DisplayEngine::renderFrame() {
    _frame_count++;
    std::ostringstream ss;
    ss << "[FRAME " << _frame_count << "] MODE=";
    switch (_mode) {
        case ScreenMode::IDLE:
            ss << "IDLE | STATUS=" << _status_text;
            break;
        case ScreenMode::WORKING:
            ss << "WORKING | STATUS=" << _status_text;
            break;
        case ScreenMode::PERMISSION_PROMPT:
            ss << "PERMISSION_PROMPT | ID=" << _prompt_req_id
               << " | TOOL=" << _prompt_tool
               << " | CMD=" << _prompt_command
               << " | [BTN A: APPROVE / BTN B: DENY]";
            break;
        case ScreenMode::ROBOT_TELEMETRY:
            ss << "ROBOT_TELEMETRY | UNIT=" << _telem_unit_id
               << " | ROLL=" << std::fixed << std::setprecision(1) << _telem_roll
               << " | PITCH=" << _telem_pitch
               << " | VBUS=" << std::setprecision(2) << _telem_vbus << "V";
            break;
    }
    return ss.str();
}

// ==========================================
// 4. StickS3HAL 全局中枢实现
// ==========================================

StickS3HAL::StickS3HAL()
    : btnA(20, 1000),
      btnB(20, 1000),
      power(),
      display(135, 240),
      _initialized(false),
      _ax(0.0f), _ay(0.0f), _az(1.0f),
      _gx(0.0f), _gy(0.0f), _gz(0.0f),
      _roll(0.0f), _pitch(0.0f) {}

bool StickS3HAL::init() {
    _initialized = true;
    display.setStatusText("READY");
    return true;
}

void StickS3HAL::updateIMU(float ax, float ay, float az, float gx, float gy, float gz) {
    _ax = ax; _ay = ay; _az = az;
    _gx = gx; _gy = gy; _gz = gz;
    // 简易重力倾角解析
    _roll = std::atan2(_ay, _az) * 180.0f / 3.14159265f;
    _pitch = std::atan2(-_ax, std::sqrt(_ay * _ay + _az * _az)) * 180.0f / 3.14159265f;
}

} // namespace sticks3
