#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified First-Principles Document Content Verification Pipeline.

CLI Entrypoint:
    python verify_pipeline.py --input <path_to_doc> [--mode audit|revise|all] [--output-dir <dir>]

Supported Document Formats:
    .md, .markdown, .pdf, .docx, .tex, .py, .ipynb, .json, .yaml, .txt
"""

import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import json
import sys
import time

from document_loader import DocumentLoader, LoadedDocument
from claim_extractor import ClaimExtractor, AtomicClaim
from physics_math_validator import PhysicsMathValidator
from citation_cross_checker import CitationCrossChecker
from annotator_and_reviser import DocumentAnnotatorAndReviser, AuditEntry


def run_pipeline(input_path: str | Path, mode: str = "all", output_dir: Optional[Path] = None) -> Dict[str, Any]:
    start_time = time.time()
    path = Path(input_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Input document not found: {path}")

    out_dir = output_dir if output_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = path.stem

    print(f"\n========================================================")
    print(f"🚀 第一性原理与公理化文档内容交叉复核流水线 (Pipeline)")
    print(f"========================================================")
    print(f"📄 目标文档: {path.name} ({path.suffix})")
    print(f"⚙️ 运行模式: {mode.upper()}")
    print(f"📁 输出目录: {out_dir}")

    # Stage 1: Document Ingestion
    print(f"\n[1/5] 正在解析文档结构...")
    doc = DocumentLoader.load(path)
    print(f"  ✓ 文档类型: {doc.file_type} | 解析段落/块数: {len(doc.blocks)} | 字数: {doc.total_words}")

    # Stage 2: Claim Extraction
    print(f"\n[2/5] 正在解构原子命题与物理/数学表述...")
    claims = ClaimExtractor.extract_from_document(doc)
    print(f"  ✓ 成功提取原子命题数: {len(claims)}")

    # Stage 3: First-Principles Axiomatic & Physical Law Validation
    print(f"\n[3/5] 正在执行第一性原理、量纲齐次性与物理守恒校验 (SymPy)...")
    math_phys_results = {}
    axiom_violations = 0
    for c in claims:
        verdicts = PhysicsMathValidator.check_claim(
            statement=c.statement,
            equations=c.extracted_equations,
            quantities=c.extracted_quantities
        )
        if verdicts:
            math_phys_results[c.claim_id] = verdicts
            for v in verdicts:
                if not v.passed:
                    axiom_violations += 1
                    print(f"    ⚠️ [公理违背] {c.claim_id}: {v.counter_proof[:90]}...")
    print(f"  ✓ 完成公理与物理校验，发现公理违背: {axiom_violations} 处")

    # Stage 4: Multi-Source Citation & Standard Identifier Cross-Checking
    print(f"\n[4/5] 正在执行三元交叉验证、DOI/RFC权威引文溯源...")
    citation_results = {}
    fact_violations = 0
    for c in claims:
        c_res = CitationCrossChecker.audit_citation(
            claim_id=c.claim_id,
            statement=c.statement,
            raw_citations=c.extracted_citations
        )
        if c_res:
            citation_results[c.claim_id] = c_res
            for cr in c_res:
                if cr.verdict == "REFUTED":
                    fact_violations += 1
                    print(f"    ❌ [事实错误] {c.claim_id}: {cr.discrepancy_explanation[:90]}...")
    print(f"  ✓ 完成权威文献检索与核验，发现事实偏差: {fact_violations} 处")

    # Stage 5: Compile Audit Matrix & Generate Outputs
    print(f"\n[5/5] 正在合成审计矩阵与双模态产物...")
    audit_entries = DocumentAnnotatorAndReviser.compile_audit_entries(
        claims=claims,
        math_phys_results=math_phys_results,
        citation_results=citation_results,
    )

    generated_files = {}

    # Mode A Outputs: Annotation
    if mode in ["audit", "all"]:
        # 1. Annotated Document (CriticMarkup & Callouts)
        annotated_text = DocumentAnnotatorAndReviser.generate_annotated_markdown(doc, audit_entries)
        annotated_path = out_dir / f"{stem}_annotated.md"
        annotated_path.write_text(annotated_text, encoding="utf-8")
        generated_files["annotated_markdown"] = str(annotated_path)

        # 2. Comprehensive Audit Report
        audit_report_text = DocumentAnnotatorAndReviser.generate_audit_report(doc, audit_entries)
        report_path = out_dir / f"{stem}_audit_report.md"
        report_path.write_text(audit_report_text, encoding="utf-8")
        generated_files["audit_report"] = str(report_path)

        # 3. JSON Structured Output
        json_path = out_dir / f"{stem}_audit.json"
        json_data = {
            "document": doc.to_dict(),
            "audit_entries": [e.to_dict() for e in audit_entries],
            "stats": {
                "total_claims": len(claims),
                "axiom_violations": axiom_violations,
                "fact_violations": fact_violations,
                "pass_count": sum(1 for e in audit_entries if e.verdict == "PASS")
            }
        }
        json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
        generated_files["audit_json"] = str(json_path)

    # Mode B Outputs: Revision & Ledger
    if mode in ["revise", "all"]:
        revised_text, ledger_items, diff_str = DocumentAnnotatorAndReviser.generate_revision_and_ledger(
            doc, audit_entries
        )
        revised_suffix = path.suffix if path.suffix in [".md", ".txt", ".tex", ".py"] else ".md"
        revised_path = out_dir / f"{stem}_revised{revised_suffix}"
        revised_path.write_text(revised_text, encoding="utf-8")
        generated_files["revised_document"] = str(revised_path)

        # Revision Ledger
        ledger_text = DocumentAnnotatorAndReviser.format_revision_ledger_markdown(ledger_items)
        ledger_path = out_dir / f"{stem}_revision_ledger.md"
        ledger_path.write_text(ledger_text, encoding="utf-8")
        generated_files["revision_ledger"] = str(ledger_path)

        # Diff Patch
        if diff_str:
            diff_path = out_dir / f"{stem}.diff"
            diff_path.write_text(diff_str, encoding="utf-8")
            generated_files["diff_patch"] = str(diff_path)

    elapsed = time.time() - start_time
    print(f"\n✨ 复核完成! 耗时: {elapsed:.2f} 秒")
    print(f"📊 生成产物列表:")
    for k, fpath in generated_files.items():
        print(f"  - [{k}]: {fpath}")

    return {
        "status": "success",
        "elapsed_seconds": elapsed,
        "claims_count": len(claims),
        "axiom_violations": axiom_violations,
        "fact_violations": fact_violations,
        "generated_files": generated_files
    }


def main():
    parser = argparse.ArgumentParser(
        description="First-Principles Document Content Verifier CLI"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Path to input document (md, pdf, docx, tex, etc.)"
    )
    parser.add_argument(
        "--mode", "-m", choices=["audit", "revise", "all"], default="all",
        help="Execution mode: 'audit' (Mode A: annotation & report), 'revise' (Mode B: revised text & ledger), or 'all' (default)"
    )
    parser.add_argument(
        "--output-dir", "-o", default=None,
        help="Directory to store outputs (defaults to same folder as input)"
    )

    args = parser.parse_args()
    out_dir = Path(args.output_dir) if args.output_dir else None
    run_pipeline(args.input, mode=args.mode, output_dir=out_dir)


if __name__ == "__main__":
    main()
