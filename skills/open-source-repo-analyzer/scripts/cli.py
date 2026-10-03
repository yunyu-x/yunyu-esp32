#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified CLI for Polyglot Open-Source Repository Analyzer & Runner (cli.py)
Agentic Skills Standard Specification (ASSS v1.0) Compliant

Orchestrates:
1. Pack & Context Budgeting (repo_pack.py)
2. Polyglot AST & Dependency Topology (repo_analyze.py)
3. Dynamic Sandbox Simulation & Probes (repo_runner.py)
4. Cross-Project External Adapter & Integration (repo_adapter.py)
"""

import sys
import json
import argparse
from pathlib import Path

# Add current scripts directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from repo_pack import RepoPacker
from repo_analyze import RepoAnalyzer
from repo_runner import RepoRunner
from repo_adapter import RepoIntegrator

# Model context profile presets
MODEL_CONTEXT_PROFILES = {
    "deepseek-32k": {"budget": 28000, "skeleton": True, "format": "markdown"},
    "qwen-32k": {"budget": 28000, "skeleton": True, "format": "markdown"},
    "ollama-16k": {"budget": 14000, "skeleton": True, "format": "markdown"},
    "claude-200k": {"budget": 180000, "skeleton": False, "format": "xml"},
    "gemini-1m": {"budget": 800000, "skeleton": False, "format": "xml"},
    "default": {"budget": None, "skeleton": False, "format": "markdown"}
}


def cmd_pack(args):
    repo_path = Path(args.repo_path).resolve()
    print(f"[CLI] Packing repository context: {repo_path}")

    budget = args.token_budget
    skeleton = args.skeleton_only
    out_format = args.format

    if args.model_target and args.model_target in MODEL_CONTEXT_PROFILES:
        profile = MODEL_CONTEXT_PROFILES[args.model_target]
        budget = budget or profile["budget"]
        skeleton = skeleton or profile["skeleton"]
        out_format = out_format or profile["format"]
        print(f"[CLI] Applied Model Profile `{args.model_target}`: budget={budget}, skeleton={skeleton}, format={out_format}")

    packer = RepoPacker(repo_path, max_file_size_kb=args.max_size,
                        skeleton_only=skeleton, token_budget=budget)
    summary = packer.pack()

    if args.output:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        if out_format == "json" or out.suffix.lower() == ".json":
            out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        elif out_format == "xml" or out.suffix.lower() == ".xml":
            out.write_text(packer.to_xml(summary), encoding="utf-8")
        else:
            out.write_text(packer.to_markdown(summary), encoding="utf-8")
        print(f"[OK] Packed output saved to: {out}")
    else:
        print(f"[OK] Scanned {summary['file_count']} files, {summary['total_lines']} lines, ~{summary['estimated_tokens']} tokens.")


def cmd_analyze(args):
    repo_path = Path(args.repo_path).resolve()
    print(f"[CLI] Analyzing polyglot AST & dependency topology: {repo_path}")
    analyzer = RepoAnalyzer(repo_path)
    result = analyzer.analyze()

    if args.output:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.suffix.lower() == ".json":
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            out.write_text(analyzer.generate_markdown_report(result), encoding="utf-8")
        print(f"[OK] Analysis report saved to: {out}")
    else:
        print(f"[OK] Analyzed {result['module_count']} modules across languages.")


def cmd_run(args):
    repo_path = Path(args.repo_path).resolve()
    print(f"[CLI] Probing and simulating repository execution in sandbox: {repo_path}")
    runner = RepoRunner(repo_path, timeout_sec=args.timeout)
    results = runner.run_all()

    if args.output:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.suffix.lower() == ".json":
            out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            out.write_text(runner.generate_markdown_report(results), encoding="utf-8")
        print(f"[OK] Simulation report saved to: {out}")
    else:
        print(f"[OK] Health Status: {results['overall_health']}")


def cmd_integrate(args):
    workspace = SCRIPT_DIR.parent.parent.parent
    integrator = RepoIntegrator(workspace)
    print(f"[CLI] Fetching repository into external_repos/ from: {args.source}")
    repo_dest = integrator.fetch_repo(args.source, target_name=args.name)

    if args.polyglot:
        adapter_path = integrator.generate_polyglot_subprocess_adapter(
            repo_path=repo_dest,
            executable_name=args.target_class.lower(),
            commands=args.methods,
            output_file=Path(args.output_adapter) if args.output_adapter else None
        )
    else:
        adapter_path = integrator.generate_adapter(
            repo_path=repo_dest,
            module_name=args.module,
            target_class=args.target_class,
            methods=args.methods,
            output_file=Path(args.output_adapter) if args.output_adapter else None
        )

        integrator.generate_consumer_example(
            adapter_path=adapter_path,
            class_name=args.target_class,
            method_name=args.methods[0] if args.methods else "process"
        )
    print(f"[OK] Integration completed successfully!")


def cmd_workflow(args):
    print(f"\n==================================================================")
    print(f"  YunYu Skills: Polyglot Open-Source 4-Stage Learning Pipeline    ")
    print(f"==================================================================\n")

    workspace = SCRIPT_DIR.parent.parent.parent
    integrator = RepoIntegrator(workspace)

    # Stage 1: Fetch / Locate
    if args.source.startswith("http") or not Path(args.source).exists():
        repo_path = integrator.fetch_repo(args.source, target_name=args.name)
    else:
        repo_path = Path(args.source).resolve()

    out_dir = Path(args.output_dir).resolve() if args.output_dir else repo_path / "analysis_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Determine profile
    budget = args.token_budget
    skeleton = args.skeleton_only
    out_format = args.format

    if args.model_target and args.model_target in MODEL_CONTEXT_PROFILES:
        p = MODEL_CONTEXT_PROFILES[args.model_target]
        budget = budget or p["budget"]
        skeleton = skeleton or p["skeleton"]
        out_format = out_format or p["format"]

    # Stage 2: Pack
    print(f"\n--- [Stage 1/4] Packing & Context Budgeting ---")
    packer = RepoPacker(repo_path, skeleton_only=skeleton, token_budget=budget)
    pack_summary = packer.pack()
    pack_ext = ".xml" if out_format == "xml" else ".md"
    pack_file = out_dir / f"{repo_path.name}_context{pack_ext}"
    if out_format == "xml":
        pack_file.write_text(packer.to_xml(pack_summary), encoding="utf-8")
    else:
        pack_file.write_text(packer.to_markdown(pack_summary), encoding="utf-8")
    print(f"[OK] Digest written to: {pack_file} (~{pack_summary['estimated_tokens']} tokens)")

    # Stage 3: Polyglot AST & Dependency Analysis
    print(f"\n--- [Stage 2/4] Polyglot AST & Architecture Roadmap Analysis ---")
    analyzer = RepoAnalyzer(repo_path)
    analysis_res = analyzer.analyze()
    analysis_file = out_dir / f"{repo_path.name}_architecture.md"
    analysis_file.write_text(analyzer.generate_markdown_report(analysis_res), encoding="utf-8")
    print(f"[OK] Architecture report written to: {analysis_file}")

    # Stage 4: Simulation & Probing
    print(f"\n--- [Stage 3/4] Sanitized Sandbox Simulation & Probing ---")
    runner = RepoRunner(repo_path)
    run_res = runner.run_all()
    run_file = out_dir / f"{repo_path.name}_simulation.md"
    run_file.write_text(runner.generate_markdown_report(run_res), encoding="utf-8")
    print(f"[OK] Simulation audit written to: {run_file} (Health: {run_res['overall_health']})")

    # Stage 5: Adapter Generation
    if args.module and args.target_class:
        print(f"\n--- [Stage 4/4] Cross-Project Adapter & Invocation Wrapper ---")
        if args.polyglot:
            adapter_file = integrator.generate_polyglot_subprocess_adapter(
                repo_path=repo_path,
                executable_name=args.target_class.lower(),
                commands=args.methods,
                output_file=out_dir / f"{repo_path.name}_polyglot_adapter.py"
            )
        else:
            adapter_file = integrator.generate_adapter(
                repo_path=repo_path,
                module_name=args.module,
                target_class=args.target_class,
                methods=args.methods,
                output_file=out_dir / f"{repo_path.name}_adapter.py"
            )
            integrator.generate_consumer_example(
                adapter_path=adapter_file,
                class_name=args.target_class,
                method_name=args.methods[0] if args.methods else "process",
                output_file=out_dir / f"run_{repo_path.name}_consumer.py"
            )

    print(f"\n==================================================================")
    print(f"  All 4 Pipeline Stages Succeeded! Artifacts saved in: {out_dir}")
    print(f"==================================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Polyglot Open-Source Repository Learning, Analysis & Sandbox Runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # pack
    p_pack = subparsers.add_parser("pack", help="Pack and sanitize codebase into structured digest")
    p_pack.add_argument("repo_path", help="Path to repository")
    p_pack.add_argument("--output", "-o", help="Output file path")
    p_pack.add_argument("--max-size", type=int, default=300, help="Max file size in KB")
    p_pack.add_argument("--skeleton-only", action="store_true", help="Skeletonize function bodies")
    p_pack.add_argument("--token-budget", type=int, default=None, help="Token budget threshold")
    p_pack.add_argument("--model-target", choices=list(MODEL_CONTEXT_PROFILES.keys()), help="Model context preset")
    p_pack.add_argument("--format", choices=["markdown", "xml", "json"], default="markdown", help="Output format")
    p_pack.set_defaults(func=cmd_pack)

    # analyze
    p_ana = subparsers.add_parser("analyze", help="Perform polyglot AST analysis, complexity, and roadmap")
    p_ana.add_argument("repo_path", help="Path to repository")
    p_ana.add_argument("--output", "-o", help="Output file path (.md or .json)")
    p_ana.set_defaults(func=cmd_analyze)

    # run
    p_run = subparsers.add_parser("run", help="Run dynamic environment probes and simulated execution")
    p_run.add_argument("repo_path", help="Path to repository")
    p_run.add_argument("--timeout", type=int, default=15, help="Command timeout in seconds")
    p_run.add_argument("--output", "-o", help="Output file path (.md or .json)")
    p_run.set_defaults(func=cmd_run)

    # integrate
    p_int = subparsers.add_parser("integrate", help="Clone/copy into external_repos and generate adapter")
    p_int.add_argument("source", help="Git URL or local directory")
    p_int.add_argument("--name", help="Directory name in external_repos/")
    p_int.add_argument("--module", default="core", help="Target module name")
    p_int.add_argument("--target-class", default="Engine", help="Target class name")
    p_int.add_argument("--methods", nargs="*", default=["process"], help="Exposed methods")
    p_int.add_argument("--output-adapter", help="Custom output adapter file")
    p_int.add_argument("--polyglot", action="store_true", help="Generate polyglot CLI adapter")
    p_int.set_defaults(func=cmd_integrate)

    # workflow
    p_wf = subparsers.add_parser("workflow", help="Run complete 4-stage pipeline end-to-end")
    p_wf.add_argument("source", help="Git URL or local path to repository")
    p_wf.add_argument("--name", help="Repository identifier")
    p_wf.add_argument("--module", default=None, help="Target module name to adapt")
    p_wf.add_argument("--target-class", default=None, help="Target class name to adapt")
    p_wf.add_argument("--methods", nargs="*", default=["process"], help="Exposed methods")
    p_wf.add_argument("--polyglot", action="store_true", help="Generate polyglot CLI adapter")
    p_wf.add_argument("--skeleton-only", action="store_true", help="Skeletonize function bodies")
    p_wf.add_argument("--token-budget", type=int, default=None, help="Token budget threshold")
    p_wf.add_argument("--model-target", choices=list(MODEL_CONTEXT_PROFILES.keys()), help="Model context preset")
    p_wf.add_argument("--format", choices=["markdown", "xml", "json"], default="markdown", help="Output format")
    p_wf.add_argument("--output-dir", "-o", help="Output directory for all generated artifacts")
    p_wf.set_defaults(func=cmd_workflow)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
