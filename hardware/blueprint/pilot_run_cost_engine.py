"""
hardware/blueprint/pilot_run_cost_engine.py
-------------------------------------------
microUnit 模块化自重构机器人阶梯制造经济学与降本模型引擎 (Blueprint Pilot Run Cost Engine)

核算阶段：
- 1-off: 手搓验证原型机 (MVP 打样, 3D打印 + 手工焊接 + 零售元器件)
- 50-off: 研发小批量试产 (Pilot Run, 简易铝模注塑 + SMT 贴片 + 气动针床 ATE)
- 200-off: 早期商业化与高校小批量交付 (量产钢模 + 批量卷带贴片 + 自动化灌封)
- 1000-off: 工业规模化量产 (高穴钢模 + 全自动飞叉绕线 + 全自动化流水线)
"""

import json
import os
from typing import Dict, Any


def compute_stepped_cost_model() -> Dict[str, Any]:
    # 模具与工装固定投入 (NRE - Non-Recurring Engineering)
    NRE = {
        "injection_mold_tooling": 12000.0,   # 1x2 穴铝模 (寿命 5,000 模次)
        "smt_steel_stencil": 300.0,          # 激光钢网与治具
        "ate_bed_of_nails_fixture": 3500.0   # 气动双侧针床测试治具
    }
    total_nre = sum(NRE.values()) # 15,800 元

    TIERS = [1, 50, 200, 1000]
    results = {}

    for qty in TIERS:
        # 1. 结构件成本 (外壳、内支架、视窗)
        if qty == 1:
            mech_housing = 38.0  # 高韧性 SLA Somos Taurus 3D 打印
            mech_internal = 18.0 # PA12 SLS 尼龙骨架
            mech_sealing = 5.0   # 手工硅胶密封垫与螺丝
            mech_mold_amort = 0.0
        elif qty <= 50:
            mech_housing = 10.5  # 注塑 PC/ABS 原料 + 调机费
            mech_internal = 4.5  # 模具注塑骨架
            mech_sealing = 2.0   # 模切硅胶与螺丝
            mech_mold_amort = NRE["injection_mold_tooling"] / qty # 12000 / 50 = 240 元/台
        elif qty <= 200:
            mech_housing = 6.8   # 批量注塑
            mech_internal = 3.2
            mech_sealing = 1.2
            mech_mold_amort = NRE["injection_mold_tooling"] / qty # 12000 / 200 = 60 元/台
        else: # 1000
            mech_housing = 4.2
            mech_internal = 2.1
            mech_sealing = 0.8
            mech_mold_amort = NRE["injection_mold_tooling"] / qty # 12 元/台

        mech_total = mech_housing + mech_internal + mech_sealing + mech_mold_amort

        # 2. 电子元器件与 PCBA 制造
        if qty == 1:
            pcb_fab = 20.0       # 嘉立创打样分摊 (含双面柔性板 FPC)
            smt_service = 45.0   # 手工焊接工时折算
            esp32 = 18.5         # 淘宝/立创散片零售
            power_ics = 14.0     # TPS63805 / SGM2205 / DW01A 零售
            drivers = 16.0       # DRV8833 + MOSFET 零售
            optics_sensors = 15.0# 6对红外发射接收管 + MPU-6050
            passives = 8.0       # POSCAP 钽电容、高精度阻容、连接器
            pcb_nre_amort = 0.0
        elif qty <= 50:
            pcb_fab = 6.5        # 2x3 拼板 4 层沉金 PCB 批量单价
            smt_service = 12.0   # SMT 贴片工程费与点数费分摊
            esp32 = 13.8         # 乐鑫原厂批量盘装订购
            power_ics = 7.5      # 卷带批量
            drivers = 8.2        # 卷带批量
            optics_sensors = 7.8 # 批量光电
            passives = 4.2       # 卷带电容电阻
            pcb_nre_amort = NRE["smt_steel_stencil"] / qty # 300 / 50 = 6 元/台
        elif qty <= 200:
            pcb_fab = 4.2
            smt_service = 7.5
            esp32 = 11.5
            power_ics = 5.2
            drivers = 6.0
            optics_sensors = 5.5
            passives = 2.8
            pcb_nre_amort = NRE["smt_steel_stencil"] / qty # 1.5 元/台
        else: # 1000
            pcb_fab = 2.8
            smt_service = 4.5
            esp32 = 9.8
            power_ics = 3.8
            drivers = 4.2
            optics_sensors = 3.9
            passives = 1.9
            pcb_nre_amort = NRE["smt_steel_stencil"] / qty # 0.3 元/台

        elec_total = (pcb_fab + smt_service + esp32 + power_ics + drivers +
                      optics_sensors + passives + pcb_nre_amort)

        # 3. 磁路与执行机构 (6面 EPM 永磁体 + 线圈 + 极靴)
        if qty == 1:
            mag_ndfeb = 18.0     # N52 定制磁钢零售 (6面 x 3元)
            mag_alnico = 15.0    # 铝镍钴 AlNiCo 5 零售 (6面 x 2.5元)
            mag_poles = 12.0     # DT4C 纯铁极靴 CNC 散件
            mag_wire = 5.0       # 0.15mm 漆包线与手工绕线
        elif qty <= 50:
            mag_ndfeb = 9.6      # 批发电镀磁钢 (6面 x 1.6元)
            mag_alnico = 8.4     # 批发
            mag_poles = 6.0      # 冲压成型极靴
            mag_wire = 2.5       # 骨架治具半自动绕线
        elif qty <= 200:
            mag_ndfeb = 7.2
            mag_alnico = 6.0
            mag_poles = 4.0
            mag_wire = 1.8
        else: # 1000
            mag_ndfeb = 5.4
            mag_alnico = 4.5
            mag_poles = 2.6
            mag_wire = 1.2

        mag_total = mag_ndfeb + mag_alnico + mag_poles + mag_wire

        # 4. 动力电池组
        if qty == 1:
            battery = 25.0       # 定制 383040 动力软包电芯单片样件
        elif qty <= 50:
            battery = 14.5       # 格氏原厂 50 片批量订购
        elif qty <= 200:
            battery = 10.8       # 批量电芯
        else:
            battery = 8.2

        # 5. 装配、测试与良率折损 (Assembly & ATE Testing)
        if qty == 1:
            labor_assembly = 60.0 # 单台手工 45 分钟组装调试
            ate_amort = 0.0
            yield_factor = 1.15   # 85% 良率，物料损耗 15%
        elif qty <= 50:
            labor_assembly = 12.0 # 工装流水线组装 4.5 分钟
            ate_amort = NRE["ate_bed_of_nails_fixture"] / qty # 3500 / 50 = 70 元/台
            yield_factor = 1.04   # 96% 良率，物料损耗 4%
        elif qty <= 200:
            labor_assembly = 6.0  # 熟练工装流水线
            ate_amort = NRE["ate_bed_of_nails_fixture"] / qty # 3500 / 200 = 17.5 元/台
            yield_factor = 1.025  # 97.5% 良率
        else:
            labor_assembly = 3.5  # 半自动化组装流水线
            ate_amort = NRE["ate_bed_of_nails_fixture"] / qty # 3.5 元/台
            yield_factor = 1.015  # 98.5% 良率

        # 直接边际制造 BOM (不含一次性固定模具工装全额摊销)
        marginal_bom_base = (mech_housing + mech_internal + mech_sealing) + (elec_total - pcb_nre_amort) + mag_total + battery
        marginal_unit_cost = (marginal_bom_base + labor_assembly) * yield_factor

        # 含一次性 NRE 摊销总成本
        bom_base = mech_total + elec_total + mag_total + battery
        total_unit_cost = (bom_base + labor_assembly + ate_amort) * yield_factor

        results[f"tier_{qty}_units"] = {
            "batch_size": qty,
            "cost_breakdown_cny": {
                "mechanical_structure": round(mech_total, 2),
                "pcba_and_electronics": round(elec_total, 2),
                "magnetics_and_actuation": round(mag_total, 2),
                "lipo_battery_pack": round(battery, 2),
                "labor_and_assembly": round(labor_assembly, 2),
                "ate_fixture_amortization": round(ate_amort, 2),
                "yield_scrap_multiplier": round(yield_factor, 3)
            },
            "marginal_bom_cost_cny": round(marginal_unit_cost, 2),
            "nre_absorbed_unit_cost_cny": round(total_unit_cost, 2),
            "marginal_deflation_pct": round((1.0 - marginal_unit_cost / (results.get("tier_1_units", {}).get("marginal_bom_cost_cny", marginal_unit_cost))) * 100.0, 1)
        }

    summary = {
        "project": "yunyu-microUnit",
        "nre_capital_expenditure_cny": NRE,
        "total_nre_cny": total_nre,
        "cost_tiers": results
    }
    return summary


if __name__ == "__main__":
    cost_data = compute_stepped_cost_model()
    print("=" * 80)
    print("microUnit 阶梯制造经济学与小批量降本模型核算报告")
    print("=" * 80)
    print(f"一次性工程投入 (NRE): ¥{cost_data['total_nre_cny']:.2f}")
    for k, v in cost_data["nre_capital_expenditure_cny"].items():
        print(f"  - {k:<28s}: ¥{v:.2f}")

    print("\n单机阶梯成本演进 (Unit Cost Deflation Curve):")
    print("-" * 95)
    print(f"{'批次规模 (Units)':<15s} | {'结构注塑':<10s} | {'PCBA电气':<10s} | {'EPM磁路':<10s} | {'电芯':<8s} | {'直接BOM成本':<12s} | {'含NRE总成本':<12s} | {'直接降幅'}")
    print("-" * 95)
    for tier_k, tier in cost_data["cost_tiers"].items():
        cb = tier["cost_breakdown_cny"]
        print(f"{tier['batch_size']:<15d} | ¥{cb['mechanical_structure']:<9.1f} | ¥{cb['pcba_and_electronics']:<9.1f} | ¥{cb['magnetics_and_actuation']:<9.1f} | ¥{cb['lipo_battery_pack']:<7.1f} | ¥{tier['marginal_bom_cost_cny']:<11.2f} | ¥{tier['nre_absorbed_unit_cost_cny']:<11.2f} | -{tier['marginal_deflation_pct']}%")
    print("=" * 95)

    # 保存核算报告
    out_file = os.path.join(os.path.dirname(__file__), "pilot_run_cost_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cost_data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] 经济学分析报告已输出至: {out_file}")
