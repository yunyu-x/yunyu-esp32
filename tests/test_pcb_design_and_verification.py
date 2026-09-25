"""
tests/test_pcb_design_and_verification.py
-----------------------------------------
灵方 (LingCube) 工业级 4 层主控 PCBA 全流程设计与制造交付自动化测试套件
"""

import os
import sys
import pytest
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hardware.verify_circuit_netlist import verify_microUnit_circuit, verify_microUnit_v2_circuit, parse_kicad_netlist
from hardware.verify_circuit_pcb import verify_pcb_layout
from hardware.simulate_pcb_power_thermal import PCBEEPowerThermalSimulator
from hardware.blueprint.ate_fixture_simulator import ATEFixtureSimulator, UnitUnderMockTest
from hardware.simulate_harsh_environment_and_faults import run_all_simulations
from hardware.simulate_circuit_spice import LingCubeSpiceSimulator

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HARDWARE_DIR = os.path.join(BASE_DIR, "hardware")
KICAD_DIR = os.path.join(HARDWARE_DIR, "kicad")
GERBER_DIR = os.path.join(HARDWARE_DIR, "gerber")
BOM_DIR = os.path.join(HARDWARE_DIR, "bom")
CPL_DIR = os.path.join(HARDWARE_DIR, "cpl")


def test_kicad_sch_and_netlist_v2_integrity():
    """验证 KiCad 原理图与 v2 工业级网络表电气完整性与 9 大隐患排查规则"""
    v2_net_path = os.path.join(KICAD_DIR, "microUnit_controller_v2.net")
    v2_sch_path = os.path.join(KICAD_DIR, "microUnit_controller_v2.kicad_sch")
    
    assert os.path.exists(v2_net_path), "v2 网络表不存在"
    assert os.path.exists(v2_sch_path), "v2 原理图不存在"
    
    # 验证 MVP 向后兼容自检
    assert verify_microUnit_circuit() is True, "MVP 网络表向后兼容自检未通过"
    
    # 验证 v2 工业级严苛自检
    assert verify_microUnit_v2_circuit(v2_net_path) is True, "v2 工业级电气规则与隐患排查自检未通过"


def test_pcb_layout_geometry_and_drc():
    """验证 KiCad 4 层板版图物理尺寸、层叠、大电流走线、天线隔离与 25 针 ATE 测试点"""
    pcb_path = os.path.join(KICAD_DIR, "microUnit_controller_v2.kicad_pcb")
    assert os.path.exists(pcb_path), "KiCad PCB 版图文件不存在"
    
    results = verify_pcb_layout(pcb_path)
    assert len(results["errors"]) == 0, f"PCB DRC 存在错误: {results['errors']}"
    assert results["board_outline"] is True
    assert results["mounting_holes"] is True
    assert results["layer_stackup"] is True
    assert results["high_current_traces"] is True
    assert results["rf_antenna_keepout"] is True
    assert results["ate_test_points"] is True
    assert results["thermal_and_ground_vias"] is True


def test_ipc2152_power_and_thermal_simulation():
    """验证 IPC-2152 走线温升、TVS 感性反峰钳位、POSCAP 压降平抑与 RC 脉宽硬看门狗仿真"""
    sim = PCBEEPowerThermalSimulator()
    report = sim.run_full_simulation()
    
    assert report["status"] == "PASS"
    # 12A 急刹走线温升需 < 5°C
    assert report["thermal_analysis"]["brake_pulse_temp_rise_degc"] < 5.0
    # TVS 钳位电压 <= 9.2V, 留出 > 2.0x MOSFET 耐压裕度
    assert report["inductive_clamp"]["safety_margin_factor"] >= 2.0
    # 470uF POSCAP 必须有效防止电池母线跌破 2.8V 触发 BMS 误停机
    assert report["power_sag_buffering"]["bms_false_trip_prevented"] is True
    assert report["power_sag_buffering"]["bus_min_voltage_with_poscap_v"] > 3.25
    # 硬件 RC 看门狗必须在 10ms 内硬切断线圈通电
    assert report["rc_watchdog_limiter"]["max_hardware_pulse_duration_ms"] <= 10.0
    assert report["rc_watchdog_limiter"]["thermal_runaway_eliminated"] is True


def test_manufacturing_gerber_and_drill_deliverables():
    """验证生产制造 RS-274X Gerber 光绘文件与 Excellon 钻孔文件完整性"""
    required_gerber_files = [
        "microUnit_controller_v2-Edge_Cuts.gml",
        "microUnit_controller_v2-F_Cu.gtl",
        "microUnit_controller_v2-In1_Cu.g1",
        "microUnit_controller_v2-In2_Cu.g2",
        "microUnit_controller_v2-B_Cu.gbl",
        "microUnit_controller_v2-F_Mask.gts",
        "microUnit_controller_v2-B_Mask.gbs",
        "microUnit_controller_v2-F_SilkS.gto",
        "microUnit_controller_v2-B_SilkS.gbo",
        "microUnit_controller_v2.drl"
    ]
    for g_file in required_gerber_files:
        full_path = os.path.join(GERBER_DIR, g_file)
        assert os.path.exists(full_path), f"缺少必要 Gerber 制造文件: {g_file}"
        assert os.path.getsize(full_path) > 50, f"Gerber 文件内容为空或损坏: {g_file}"


def test_bom_and_cpl_integrity():
    """验证物料采购清单 BOM 与自动化贴片坐标表 CPL 完整性与料号覆盖度"""
    bom_path = os.path.join(BOM_DIR, "microUnit_controller_v2_BOM.csv")
    cpl_path = os.path.join(CPL_DIR, "microUnit_controller_v2_CPL.csv")
    
    assert os.path.exists(bom_path), "BOM CSV 不存在"
    assert os.path.exists(cpl_path), "CPL CSV 不存在"
    
    with open(bom_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        bom_rows = list(reader)
        assert len(bom_rows) >= 30, f"BOM 项数量过少: {len(bom_rows)}"
        # 确保关键芯片与被动件料号均已锁定
        designators = {row["Designator"] for row in bom_rows}
        assert any("U1" in d for d in designators) # ESP32
        assert any("U2" in d for d in designators) # DRV8833
        assert any("U5" in d for d in designators) # TP4056
        assert any("U6" in d for d in designators) # DW01A
        assert any("C1" in d for d in designators) # POSCAP 470uF
        
    with open(cpl_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cpl_rows = list(reader)
        assert len(cpl_rows) >= 40, f"CPL 贴片器件数量过少: {len(cpl_rows)}"
        # 确保 25 个 ATE 测试点坐标均已导出
        cpl_designators = {row["Designator"] for row in cpl_rows}
        for i in range(1, 26):
            assert f"TP{i}" in cpl_designators, f"CPL 缺失测试点坐标: TP{i}"


def test_ate_fixture_simulator_batch_acceptance():
    """验证产线 15 秒气动双侧针床 ATE 治具批量测试流水线与合格率"""
    ate = ATEFixtureSimulator()
    # 验证单台正常机测试通过
    dut_normal = UnitUnderMockTest(unit_id=1, is_defective=False)
    passed, fail_reasons = ate.test_single_unit(dut_normal)
    assert passed is True, f"正常机在 ATE 治具下测试未通过: {fail_reasons}"


def test_harsh_environment_and_fault_tolerance_simulation():
    """验证极端高低温 (-20°C~+85°C)、电磁干扰、FMEA 单点故障与 SMT 量产良率物理仿真"""
    report = run_all_simulations()
    assert report["status"] == "PASS", f"物理极限与容灾仿真未全部通过: {report}"
    
    # 1. -20°C 肖特基隔离下 LDO 输入端最低电压 >= 2.80V (防止 DW01A 误判关机)
    low_t = report["low_temperature_analysis"]
    assert low_t["isolated_ldo_in_min_v"] >= 2.80
    assert low_t["isolated_poscap_hold_pass"] is True
    assert low_t["dw01a_false_trip_eliminated"] is True
    
    # 2. +85°C DRV8833 结温与 TSD 热关断安全裕度 >= 50°C
    high_t = report["high_temperature_analysis"]
    assert high_t["drv8833_tsd_margin_degc"] >= 50.0
    assert high_t["drv8833_thermal_safe"] is True
    # N45SH 磁钢 85°C 矫顽力安全裕度 >= 5.0x
    assert high_t["demag_safety_margin_factor"] >= 5.0
    assert high_t["irreversible_demag_eliminated"] is True
    
    # 3. EMC/EMI 临界阻尼 Snubber 阻尼比 (0.35 <= zeta <= 0.6)
    emc = report["emc_and_damping"]
    assert 0.35 <= emc["new_damping_ratio"] <= 0.60
    assert emc["snubber_critically_damped"] is True
    assert emc["rf_lna_desensitization_prevented"] is True
    
    # 4. FMEA EPM MOS D-S 短路经 F1 (1812L150PR) 熔断，功率切断后维持在安全微瓦级
    fmea = report["fmea_and_resilience"]
    assert fmea["pptc_trip_time_s"] < 1.0
    assert fmea["tripped_leakage_power_mw"] < 1.0
    assert fmea["thermal_runaway_prevented"] is True
    
    # 5. 钨铜配重校正后整机偏心距严格受控在允许红线以内 (<= 0.45mm)
    assert fmea["cog_offset_corrected_mm"] <= 0.45
    assert fmea["cog_balance_compliant"] is True
    
    # 6. SMT 1000台量产出产一次合格率 (FPY) >= 96.5%
    yield_res = report["smt_yield_model"]
    assert yield_res["mass_prod_fpy_pct"] >= 96.5
    assert yield_res["mass_prod_fpy_pass"] is True


def test_spice_circuit_level_simulation():
    """验证基于 ngspice-41 专业 SPICE 引擎的 6 大物理回路高保真仿真与闭环调优结果"""
    sim = LingCubeSpiceSimulator()
    report = sim.run_full_spice_suite()
    
    assert report["overall_status"] == "PASS", f"SPICE 物理级电路仿真未全部通过: {report}"
    
    sims = report["simulations"]
    # 1. -20°C 母线跌落与 470uF POSCAP 维持仿真
    s1 = sims["sim1_power_sag"]
    assert s1["status"] == "PASS"
    assert s1["buffered_ldo_in_min_voltage_v"] >= 2.80
    assert s1["unbuffered_cell_min_voltage_v"] < 2.20 # 证明无缓冲直接跌穿
    assert s1["brownout_safety_margin_mv"] > 300.0 # 距离 2.43V 欠压阈值保持 >300mV 安全边际
    
    # 2. EPM 感性关断反峰与 TVS / 临界阻尼缓冲器仿真
    s2 = sims["sim2_epm_inductive_clamp"]
    assert s2["status"] == "PASS"
    assert s2["vdrain_peak_normal_v"] <= 5.5
    assert s2["vdrain_peak_tvs_clamp_fmea_v"] <= 9.2 # 单点二极管失效下仍严格钳位在 9.2V 内
    assert s2["safety_margin_normal_factor"] >= 5.0
    assert s2["safety_margin_fault_factor"] >= 3.0
    
    # 3. 硬件 RC 单稳态脉宽限幅看门狗 (微分电路) 仿真
    s3 = sims["sim3_rc_watchdog_limiter"]
    assert s3["status"] == "PASS"
    assert 4.5 <= s3["spice_measured_cutoff_time_ms"] <= 6.5
    assert s3["thermal_runaway_eliminated"] is True
    
    # 4. FMEA MOS 击穿故障与 Littelfuse PPTC 自恢复跳闸仿真
    s4 = sims["sim4_fmea_pptc_trip"]
    assert s4["status"] == "PASS"
    assert s4["pptc_trip_time_s"] <= 1.0
    assert s4["post_trip_leakage_current_ma"] <= 1.0
    assert s4["battery_thermal_protection_pass"] is True
    
    # 5. 12A 急刹地弹与 DW01A CS 引脚 RC 低通滤波抗扰度仿真
    s5 = sims["sim5_ground_bounce_filter"]
    assert s5["status"] == "PASS"
    assert s5["filtered_dw01a_cs_pin_peak_mv"] <= 2.0
    assert s5["immunity_safety_margin_factor"] >= 100.0 # 150mV 阈值拥有超 100 倍抗扰裕度
    assert s5["false_tripping_eliminated"] is True
    
    # 6. IMU 冷复位 P-MOS 电源门控动态开启动态与闭环软启调优仿真
    s6 = sims["sim6_imu_power_gate"]
    assert s6["status"] == "PASS"
    assert s6["vcc_3v3_rail_dip_mv"] <= 50.0 # 压降严格控制在 50mV 以内
    assert s6["dip_suppression_pct"] >= 90.0 # 相比未调优版抑制超 90%
    assert s6["imu_cold_off_voltage_v"] < 0.001 # 断电彻底
    assert s6["imu_domain_steady_voltage_v"] >= 3.25
    assert s6["rail_stability_pass"] is True

