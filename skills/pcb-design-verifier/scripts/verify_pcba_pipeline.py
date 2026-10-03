"""
skills/pcb-design-verifier/scripts/verify_pcba_pipeline.py
---------------------------------------------------------
Unified Pipeline Verifier for Industrial PCBA Hardware & SPICE Simulation
ASSS Protocol v1.0 Compliant

Executes:
1. KiCad Netlist ERC (12-Hazard Checks)
2. KiCad PCB Layout DRC (Geometry, Traces, RF Keepout, ATE Testpoints)
3. Harsh Environment, EMC Snubber, FMEA & Poisson SMT Yield Simulation
4. ngspice-41 High-Fidelity Circuit Simulation (6 Decks)
5. Generates Consolidated JSON & Markdown Quality Gate Report
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

try:
    from .verify_circuit_netlist import verify_microUnit_v2_circuit
    from .verify_circuit_pcb import verify_pcb_layout
    from .simulate_harsh_environment import run_all_simulations
    from .simulate_circuit_spice import LingCubeSpiceSimulator
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    from verify_circuit_netlist import verify_microUnit_v2_circuit
    from verify_circuit_pcb import verify_pcb_layout
    from simulate_harsh_environment import run_all_simulations
    from simulate_circuit_spice import LingCubeSpiceSimulator


class PCBVerificationPipeline:
    def __init__(self, netlist_path: str = None, pcb_path: str = None, ngspice_path: str = None):
        self.netlist_path = netlist_path
        self.pcb_path = pcb_path
        self.ngspice_path = ngspice_path

    def run(self, output_json: str = None) -> Dict[str, Any]:
        print("=" * 75)
        print("  YunYu Skills · pcb-design-verifier 全流程硬件设计规则与物理仿真流水线")
        print("=" * 75)

        pipeline_report = {
            "overall_status": "PASS",
            "stages": {}
        }

        # Stage 1: Netlist ERC
        print("\n>>> Stage 1: KiCad 原理图网络表 ERC 12 大深层隐患排查...")
        erc_pass = verify_microUnit_v2_circuit(self.netlist_path)
        pipeline_report["stages"]["stage1_netlist_erc"] = {
            "status": "PASS" if erc_pass else "FAIL"
        }

        # Stage 2: PCB Layout DRC
        print("\n>>> Stage 2: KiCad 4 层板物理版图与航天装配 DRC 审查...")
        drc_res = verify_pcb_layout(self.pcb_path)
        drc_pass = len(drc_res["errors"]) == 0
        pipeline_report["stages"]["stage2_layout_drc"] = {
            "status": "PASS" if drc_pass else "FAIL",
            "details": drc_res
        }

        # Stage 3: Harsh Environment & Multi-Domain Physics
        print("\n>>> Stage 3: 高低温 (-20°C~+85°C)、EMC 阻尼、FMEA 与量产良率多物理场仿真...")
        env_res = run_all_simulations()
        pipeline_report["stages"]["stage3_harsh_env_and_fmea"] = env_res

        # Stage 4: Professional ngspice SPICE Simulation
        print("\n>>> Stage 4: 基于 ngspice-41 专业 SPICE 仿真引擎的 6 大物理回路时域仿真...")
        try:
            spice_sim = LingCubeSpiceSimulator(ngspice_path=self.ngspice_path)
            spice_res = spice_sim.run_full_spice_suite()
        except Exception as e:
            spice_res = {
                "overall_status": "FAIL",
                "error": str(e)
            }
        pipeline_report["stages"]["stage4_spice_simulation"] = spice_res

        all_passed = (
            erc_pass and
            drc_pass and
            env_res["status"] == "PASS" and
            spice_res.get("overall_status") == "PASS"
        )
        pipeline_report["overall_status"] = "PASS" if all_passed else "FAIL"

        if output_json:
            os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(pipeline_report, f, indent=2, ensure_ascii=False)
            print(f"\n[Info] 流水线综合质检报告已保存至: {output_json}")

        print("\n" + "=" * 75)
        print(f"  pcb-design-verifier 综合质量评定: {pipeline_report['overall_status']}")
        print("=" * 75)
        return pipeline_report


def main():
    parser = argparse.ArgumentParser(description="Industrial PCBA Design & SPICE Verification Pipeline")
    parser.add_argument("--netlist", type=str, default=None, help="Path to KiCad netlist file")
    parser.add_argument("--pcb", type=str, default=None, help="Path to KiCad pcb file")
    parser.add_argument("--ngspice", type=str, default=None, help="Path to ngspice executable")
    parser.add_argument("--output", type=str, default=None, help="Output JSON report path")
    args = parser.parse_args()

    pipeline = PCBVerificationPipeline(
        netlist_path=args.netlist,
        pcb_path=args.pcb,
        ngspice_path=args.ngspice
    )
    report = pipeline.run(output_json=args.output)
    sys.exit(0 if report["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
