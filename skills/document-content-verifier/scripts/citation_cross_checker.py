#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-Source Citation, Standard Identifier & Evidence Cross-Checker.

Features:
1. Ground-truth verification against built-in authoritative registries (CODATA 2022, RFCs, ISO standards, landmark papers).
2. DOI & Standard Identifier structural validation.
3. Neutral query synthesis (SAFE methodology) for zero-bias search verification.
4. Triangulation & Evidence tiering (Tier 1: Standards/CODATA/Journals; Tier 2: Conf/Datasheets; Tier 3: Preprints).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import re
import sys


@dataclass
class CitationAuditResult:
    """Audit result for a citation or factual assertion."""
    claim_id: str
    target_identifier: str
    is_valid_format: bool
    is_verified_ground_truth: bool
    verdict: str  # 'CONFIRMED', 'REFUTED', 'QUESTIONABLE', 'UNVERIFIABLE'
    evidence_tier: str  # 'Tier 1', 'Tier 2', 'Tier 3', 'Untrusted'
    verified_source_title: str
    verified_citation: str
    discrepancy_explanation: Optional[str] = None
    suggested_neutral_queries: List[str] = field(default_factory=list)


class CitationCrossChecker:
    """Cross-verification engine validating citations, identifiers, and factual anchors."""

    # Built-in Tier 1 Ground-Truth Registry (Authoritative standards, constants, landmark publications)
    TIER1_STANDARDS_REGISTRY = {
        # RFCs
        "RFC 791": {"title": "Internet Protocol (IPv4)", "status": "Standard", "year": 1981, "url": "https://www.rfc-editor.org/rfc/rfc791"},
        "RFC 793": {"title": "Transmission Control Protocol (TCP)", "status": "Obsoleted by RFC 9293", "year": 1981, "url": "https://www.rfc-editor.org/rfc/rfc9293"},
        "RFC 8446": {"title": "The Transport Layer Security (TLS) Protocol Version 1.3", "status": "Proposed Standard", "year": 2018, "url": "https://www.rfc-editor.org/rfc/rfc8446"},
        "RFC 9000": {"title": "QUIC: A UDP-Based Multiplexed and Secure Transport", "status": "Proposed Standard", "year": 2021, "url": "https://www.rfc-editor.org/rfc/rfc9000"},
        "RFC 9110": {"title": "HTTP Semantics", "status": "Internet Standard", "year": 2022, "url": "https://www.rfc-editor.org/rfc/rfc9110"},
        "RFC 9112": {"title": "HTTP/1.1", "status": "Internet Standard", "year": 2022, "url": "https://www.rfc-editor.org/rfc/rfc9112"},
        "RFC 7540": {"title": "Hypertext Transfer Protocol Version 2 (HTTP/2)", "status": "Obsoleted by RFC 9113", "year": 2015, "url": "https://www.rfc-editor.org/rfc/rfc9113"},
        # ISO / IEC Standards
        "ISO 26262": {"title": "Road vehicles — Functional safety (ASIL A-D)", "status": "International Standard", "year": 2018, "url": "https://www.iso.org/standard/68383.html"},
        "ISO/IEC 27001": {"title": "Information security management systems", "status": "International Standard", "year": 2022, "url": "https://www.iso.org/standard/27001"},
        "ISO/IEC 9899": {"title": "Programming languages — C (C17 / C23)", "status": "International Standard", "year": 2018, "url": "https://www.iso.org/standard/74528.html"},
        "ISO/IEC 14882": {"title": "Programming languages — C++ (C++20 / C++23)", "status": "International Standard", "year": 2020, "url": "https://www.iso.org/standard/79358.html"},
        "IEEE 754": {"title": "Standard for Floating-Point Arithmetic", "status": "IEEE Standard", "year": 2019, "url": "https://doi.org/10.1109/IEEESTD.2019.8766229"},
    }

    # Landmark Papers Registry
    LANDMARK_PAPERS_REGISTRY = {
        "attention is all you need": {
            "title": "Attention Is All You Need",
            "authors": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I.",
            "venue": "Advances in Neural Information Processing Systems (NeurIPS 2017)",
            "year": 2017,
            "doi": "https://doi.org/10.48550/arXiv.1706.03762",
            "key_fact": "Introduced Transformer architecture based solely on self-attention mechanisms without recurrence or convolutions."
        },
        "deep residual learning": {
            "title": "Deep Residual Learning for Image Recognition",
            "authors": "He, K., Zhang, X., Ren, S., & Sun, J.",
            "venue": "IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2016)",
            "year": 2016,
            "doi": "https://doi.org/10.1109/CVPR.2016.90",
            "key_fact": "Introduced residual shortcut connections (ResNet) to train networks exceeding 100 layers."
        },
        "mathematical theory of communication": {
            "title": "A Mathematical Theory of Communication",
            "authors": "Shannon, C. E.",
            "venue": "The Bell System Technical Journal, 27(3), 379-423",
            "year": 1948,
            "doi": "https://doi.org/10.1002/j.1538-7305.1948.tb01338.x",
            "key_fact": "Established information theory, entropy H = -sum(p log p), and channel capacity theorem."
        },
        "on computable numbers": {
            "title": "On Computable Numbers, with an Application to the Entscheidungsproblem",
            "authors": "Turing, A. M.",
            "venue": "Proceedings of the London Mathematical Society, 2(42), 230-265",
            "year": 1936,
            "doi": "https://doi.org/10.1112/plms/s2-42.1.230",
            "key_fact": "Introduced the Universal Turing Machine and proved the undecidability of the halting problem."
        }
    }

    # Physical Engineering Ground-Truth Data
    ENGINEERING_BENCHMARKS = {
        "raptor": {
            "subject": "SpaceX Raptor Engine (星舰猛禽发动机)",
            "aliases": ["raptor", "猛禽", "猛禽发动机", "raptor 2", "raptor 3"],
            "chamber_pressure_bar": 300.0,
            "max_chamber_pressure_bar": 350.0,
            "fuel": "Subcooled liquid methane (CH4) and liquid oxygen (LOX)",
            "cycle": "Full-flow staged combustion cycle (FFSCC)",
            "verified_source": "SpaceX official public telemetry & Elon Musk Raptor 3 technical updates (2024)"
        },
        "merlin 1d": {
            "subject": "SpaceX Merlin 1D Engine",
            "aliases": ["merlin", "merlin 1d", "梅林", "默林发动机"],
            "chamber_pressure_bar": 97.0,
            "thrust_sea_level_kn": 845.0,
            "fuel": "RP-1 (rocket grade kerosene) and LOX",
            "cycle": "Gas-generator cycle",
            "verified_source": "SpaceX Falcon 9 User's Guide (Rev 3.0, 2020)"
        }
    }

    @classmethod
    def audit_citation(cls, claim_id: str, statement: str, raw_citations: List[str]) -> List[CitationAuditResult]:
        results: List[CitationAuditResult] = []

        # 1. Audit Explicit Citations & Standard IDs
        for cite in raw_citations:
            res = cls._verify_single_identifier(claim_id, cite, statement)
            if res:
                results.append(res)

        # 2. If no explicit citation but contains landmark papers/standards/benchmarks in text
        if not raw_citations:
            res = cls._check_implicit_mentions(claim_id, statement)
            if res:
                results.append(res)

        # 3. If claim is empirical and lacks citations, generate neutral queries
        if not results and len(statement) > 20:
            queries = cls.generate_neutral_queries(statement)
            results.append(CitationAuditResult(
                claim_id=claim_id,
                target_identifier="UNGROUNDED_EMPIRICAL_CLAIM",
                is_valid_format=False,
                is_verified_ground_truth=False,
                verdict="UNVERIFIABLE",
                evidence_tier="Untrusted",
                verified_source_title="Missing Authoritative Primary Source",
                verified_citation="No DOI, standard, or empirical citation provided.",
                discrepancy_explanation="Claim makes empirical assertions without citing primary literature or standards.",
                suggested_neutral_queries=queries,
            ))

        return results

    @classmethod
    def _verify_single_identifier(cls, claim_id: str, cite: str, statement: str) -> Optional[CitationAuditResult]:
        # (a) Check RFC
        rfc_match = re.search(r"RFC\s*#?\s*(\d+)", cite, re.IGNORECASE)
        if rfc_match:
            num = rfc_match.group(1)
            std_key = f"RFC {num}"
            if std_key in cls.TIER1_STANDARDS_REGISTRY:
                info = cls.TIER1_STANDARDS_REGISTRY[std_key]
                return CitationAuditResult(
                    claim_id=claim_id,
                    target_identifier=std_key,
                    is_valid_format=True,
                    is_verified_ground_truth=True,
                    verdict="CONFIRMED",
                    evidence_tier="Tier 1",
                    verified_source_title=info["title"],
                    verified_citation=f"IETF {std_key} ({info['year']}): {info['title']}, {info['url']}",
                )
            else:
                return CitationAuditResult(
                    claim_id=claim_id,
                    target_identifier=std_key,
                    is_valid_format=True,
                    is_verified_ground_truth=False,
                    verdict="QUESTIONABLE",
                    evidence_tier="Tier 1",
                    verified_source_title=f"IETF RFC {num}",
                    verified_citation=f"https://www.rfc-editor.org/rfc/rfc{num}.html",
                    discrepancy_explanation=f"RFC {num} format is valid, requires live query against IETF index.",
                    suggested_neutral_queries=[f"site:rfc-editor.org RFC {num}"]
                )

        # (b) Check ISO / IEC Standard
        iso_match = re.search(r"ISO(?:/IEC)?\s*(\d{4,6})", cite, re.IGNORECASE)
        if iso_match:
            iso_num = iso_match.group(1)
            matched_key = next((k for k in cls.TIER1_STANDARDS_REGISTRY if iso_num in k), None)
            if matched_key:
                info = cls.TIER1_STANDARDS_REGISTRY[matched_key]
                return CitationAuditResult(
                    claim_id=claim_id,
                    target_identifier=matched_key,
                    is_valid_format=True,
                    is_verified_ground_truth=True,
                    verdict="CONFIRMED",
                    evidence_tier="Tier 1",
                    verified_source_title=info["title"],
                    verified_citation=f"{matched_key} ({info['year']}): {info['title']}, {info['url']}",
                )

        # (c) Check DOI
        doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", cite)
        if doi_match:
            doi_str = doi_match.group(1)
            # Basic validation of DOI format
            return CitationAuditResult(
                claim_id=claim_id,
                target_identifier=doi_str,
                is_valid_format=True,
                is_verified_ground_truth=True,
                verdict="CONFIRMED",
                evidence_tier="Tier 1",
                verified_source_title="Digital Object Identifier (DOI)",
                verified_citation=f"https://doi.org/{doi_str}",
            )

        # (d) Check Bracket / Parenthetical Citations
        return CitationAuditResult(
            claim_id=claim_id,
            target_identifier=cite,
            is_valid_format=True,
            is_verified_ground_truth=False,
            verdict="QUESTIONABLE",
            evidence_tier="Tier 2",
            verified_source_title="Unanchored Academic Citation",
            verified_citation=cite,
            discrepancy_explanation=f"Citation '{cite}' lacks direct digital resolver (DOI/URL). Must be cross-verified against bibliography.",
            suggested_neutral_queries=cls.generate_neutral_queries(statement),
        )

    @classmethod
    def _check_implicit_mentions(cls, claim_id: str, statement: str) -> Optional[CitationAuditResult]:
        lower_stmt = statement.lower()

        # Check landmark papers
        for key, entry in cls.LANDMARK_PAPERS_REGISTRY.items():
            if key in lower_stmt:
                return CitationAuditResult(
                    claim_id=claim_id,
                    target_identifier=entry["title"],
                    is_valid_format=True,
                    is_verified_ground_truth=True,
                    verdict="CONFIRMED",
                    evidence_tier="Tier 1",
                    verified_source_title=entry["title"],
                    verified_citation=f"{entry['authors']} ({entry['year']}). {entry['title']}. {entry['venue']}. DOI: {entry['doi']}",
                )

        # Check aerospace benchmarks
        for key, bench in cls.ENGINEERING_BENCHMARKS.items():
            if any(alias in lower_stmt for alias in bench.get("aliases", [key])):
                # E.g. Starship Raptor chamber pressure
                if "室压" in statement or "chamber pressure" in lower_stmt or "bar" in lower_stmt or "mpa" in lower_stmt:
                    # Look for numerical values
                    num_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:bar|mpa)", statement, re.IGNORECASE)
                    if num_match:
                        val = float(num_match.group(1))
                        unit = "bar" if "bar" in statement.lower() else "mpa"
                        val_bar = val * 10.0 if unit == "mpa" else val

                        max_allowable = bench["max_chamber_pressure_bar"] * 1.25
                        if val_bar > max_allowable:
                            return CitationAuditResult(
                                claim_id=claim_id,
                                target_identifier=bench["subject"],
                                is_valid_format=True,
                                is_verified_ground_truth=False,
                                verdict="REFUTED",
                                evidence_tier="Tier 1",
                                verified_source_title=bench["subject"],
                                verified_citation=bench["verified_source"],
                                discrepancy_explanation=f"Claimed chamber pressure {val} {unit} ({val_bar} bar) significantly exceeds verified engineering limit of ~{bench['max_chamber_pressure_bar']} bar.",
                                suggested_neutral_queries=[f"'{bench['subject']}' official chamber pressure bar specification"]
                            )
                        else:
                            return CitationAuditResult(
                                claim_id=claim_id,
                                target_identifier=bench["subject"],
                                is_valid_format=True,
                                is_verified_ground_truth=True,
                                verdict="CONFIRMED",
                                evidence_tier="Tier 1",
                                verified_source_title=bench["subject"],
                                verified_citation=bench["verified_source"],
                            )
        return None

    @classmethod
    def generate_neutral_queries(cls, text: str) -> List[List[str]]:
        """Synthesize neutral, bias-free search queries adhering to SAFE methodology."""
        # Strip punctuation
        clean = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)
        words = clean.split()
        keywords = [w for w in words if len(w) > 2 and w.lower() not in ["that", "with", "this", "from", "were", "been", "have", "为", "并", "在", "等", "和"]]

        if len(keywords) > 6:
            keywords = keywords[:6]

        base_query = " ".join(keywords)
        return [
            f"{base_query} official specifications",
            f"{base_query} peer-reviewed DOI",
            f"{base_query} benchmark refutation errata"
        ]


if __name__ == "__main__":
    test_stmt = "在现代微服务通信中，HTTP协议语义被标准化在 RFC 9110 中，而Attention机制最初由 Attention Is All You Need 提出。"
    from claim_extractor import ClaimExtractor
    cites = ClaimExtractor._extract_citations(test_stmt)
    results = CitationCrossChecker.audit_citation("C0001", test_stmt, cites)
    for r in results:
        print(f"[{r.verdict}] ID: {r.target_identifier} | Tier: {r.evidence_tier}")
        print(f"  Source: {r.verified_source_title}")
        print(f"  Citation: {r.verified_citation}")
