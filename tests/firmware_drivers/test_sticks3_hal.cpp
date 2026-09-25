#include "../../firmware/m5sticks3_buddy/include/sticks3_hal.h"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace sticks3;

void test_button_state_machine() {
    std::cout << "[RUNNING] test_button_state_machine..." << std::endl;
    ButtonStateMachine btn(20, 1000); // 20ms debounce, 1000ms long press

    // 初始状态
    assert(!btn.isPressed());
    assert(!btn.isLongPressed());

    // 1. 模拟短抖动 (< 20ms)，不应触发按下
    ButtonEvent ev = btn.update(10, true);
    assert(ev == ButtonEvent::NONE);
    assert(!btn.isPressed());

    // 2. 持续按下超过 20ms -> 确认为按下
    ev = btn.update(30, true);
    assert(ev == ButtonEvent::NONE);
    assert(btn.isPressed());

    // 3. 持续按下 200ms 后释放 -> 持续稳定超过防抖阈值 (20ms) 触发单击 (CLICK)
    ev = btn.update(200, true);
    assert(ev == ButtonEvent::NONE);
    btn.update(230, false); // 电平变反开始计时
    ev = btn.update(260, false); // 30ms > 20ms 防抖完成确认释放
    assert(ev == ButtonEvent::CLICK);
    assert(!btn.isPressed());

    // 4. 模拟长按 (> 1000ms)
    btn.reset();
    btn.update(1000, true);
    btn.update(1030, true); // 确认按下
    assert(btn.isPressed());

    ev = btn.update(1500, true); // 500ms
    assert(ev == ButtonEvent::NONE);
    assert(!btn.isLongPressed());

    ev = btn.update(2050, true); // 超过 1000ms 触发长按
    assert(ev == ButtonEvent::LONG_PRESS);
    assert(btn.isLongPressed());

    // 释放长按
    btn.update(2100, false);
    ev = btn.update(2130, false);
    assert(ev == ButtonEvent::RELEASE);
    assert(!btn.isPressed());

    std::cout << "  -> Button debounce, click, and long-press verified!" << std::endl;
}

void test_power_manager() {
    std::cout << "[RUNNING] test_power_manager..." << std::endl;
    PowerManager pwr;

    // 默认外部 5V 关闭
    assert(pwr.getExtOutput() == false);

    // 打开 5V 使能
    pwr.setExtOutput(true);
    assert(pwr.getExtOutput() == true);

    // 电池电量与低电量报警
    pwr.updateBatteryVoltage(4.20f);
    assert(pwr.getBatteryPercentage() == 100);
    assert(!pwr.isLowBattery());

    pwr.updateBatteryVoltage(3.80f);
    assert(pwr.getBatteryPercentage() == 50);

    pwr.updateBatteryVoltage(3.35f);
    assert(pwr.getBatteryPercentage() == 0);
    assert(pwr.isLowBattery());

    std::cout << "  -> PowerManager M5PM1 5V gate & battery SOC verified!" << std::endl;
}

void test_display_engine() {
    std::cout << "[RUNNING] test_display_engine..." << std::endl;
    DisplayEngine disp;

    // IDLE
    disp.setStatusText("WAITING_BLE");
    std::string frame1 = disp.renderFrame();
    assert(frame1.find("WAITING_BLE") != std::string::npos);

    // PERMISSION PROMPT
    disp.setPrompt("Bash", "git push --force", "req_42");
    assert(disp.getMode() == ScreenMode::PERMISSION_PROMPT);
    std::string frame2 = disp.renderFrame();
    assert(frame2.find("req_42") != std::string::npos);
    assert(frame2.find("git push --force") != std::string::npos);
    assert(frame2.find("[BTN A: APPROVE / BTN B: DENY]") != std::string::npos);

    // TELEMETRY
    disp.setTelemetry("LingCube_01", 45.0f, -12.5f, 3.88f);
    assert(disp.getMode() == ScreenMode::ROBOT_TELEMETRY);
    std::string frame3 = disp.renderFrame();
    assert(frame3.find("LingCube_01") != std::string::npos);
    assert(frame3.find("ROLL=45.0") != std::string::npos);
    assert(frame3.find("3.88V") != std::string::npos);

    std::cout << "  -> DisplayEngine ST7789 screen contexts and frame synthesis verified!" << std::endl;
}

void test_imu_orientation() {
    std::cout << "[RUNNING] test_imu_orientation..." << std::endl;
    StickS3HAL hal;
    hal.init();

    // 模拟水平静止 (az=1g)
    hal.updateIMU(0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f);
    assert(std::abs(hal.getRoll()) < 0.1f);
    assert(std::abs(hal.getPitch()) < 0.1f);

    // 模拟侧倾 90度 (ay=1g, az=0g)
    hal.updateIMU(0.0f, 1.0f, 0.0f, 0.0f, 0.0f, 0.0f);
    assert(std::abs(hal.getRoll() - 90.0f) < 0.5f);

    std::cout << "  -> IMU attitude pitch/roll trigonometric tracking verified!" << std::endl;
}

int main() {
    std::cout << "==========================================================" << std::endl;
    std::cout << ">>> [SCHEME 2 VERIFICATION] StickS3 Embedded HAL Suite" << std::endl;
    std::cout << "==========================================================" << std::endl;

    test_button_state_machine();
    test_power_manager();
    test_display_engine();
    test_imu_orientation();

    std::cout << "\n[SUCCESS] Scheme 2 (PlatformIO & Driver Suite) PASSED 100%!\n" << std::endl;
    return 0;
}
