#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atomic Claim & Axiom Extraction Engine.

Decomposes parsed document text blocks into atomic, independently verifiable claims:
- LOGICAL (Causality, implications, deductions)
- MATHEMATICAL (Formulas, asymptotic bounds, equalities/inequalities)
- PHYSICAL_AXIOMATIC (Physical laws, quantities with units, conservation)
- EMPIRICAL_FACTUAL (Experimental data, hardware specs, historical dates)
- CITATION_ATTRIBUTION (Academic papers, RFCs, ISO standards, URLs)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import re
import sys

from document_loader import TextBlock, LoadedDocument


@dataclass
class AtomicClaim:
    """An atomic statement isolated for formal/empirical verification."""
    claim_id: str
    block_id: str
    claim_type: str  # LOGICAL, MATHEMATICAL, PHYSICAL_AXIOMATIC, EMPIRICAL_FACTUAL, CITATION_ATTRIBUTION
    statement: str
    raw_span: str
    line_number: int = 1
    page_number: int = 1
    extracted_quantities: List[Dict[str, str]] = field(default_factory=list)
    extracted_equations: List[str] = field(default_factory=list)
    extracted_citations: List[str] = field(default_factory=list)
    context_heading: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClaimExtractor:
    """Heuristic and regex-based atomic claim segmentation engine."""

    # Common physical units pattern (SI & derived)
    UNIT_PATTERN = re.compile(
        r"(?<![a-zA-Z])(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*"
        r"(m/s\^?2|km/s|m/s|km/h|m\^?3|m\^?2|cm\^?3|mm|cm|km|m|μm|nm|"
        r"kg|g|mg|ton|t|N|kN|MN|J|kJ|MJ|GJ|W|kW|MW|GW|TW|"
        r"Pa|kPa|MPa|GPa|bar|mbar|atm|Torr|psi|"
        r"K|°C|degC|rad|deg|"
        r"A|mA|V|mV|kV|Ω|kΩ|MΩ|F|μF|nF|pF|H|mH|T|G|"
        r"Hz|kHz|MHz|GHz|THz|bps|kbps|Mbps|Gbps|Tbps|B|KB|MB|GB|TB|"
        r"mol|cd|dB|dBm)\b",
        re.IGNORECASE
    )

    # Complexity notation: O(N), O(N log N), Theta(N^2), Omega(N)
    COMPLEXITY_PATTERN = re.compile(
        r"(?:(?:O|Big-O|Theta|Θ|Omega|Ω)\s*\(\s*[^)]+\s*\))",
        re.IGNORECASE
    )

    # Citation patterns: [1], [1-3], (Author, Year), RFC 1234, ISO 12345, DOI: ...
    CITATION_PATTERNS = [
        re.compile(r"\[\d+(?:[,\s–-]+\d+)*\]"),
        re.compile(r"\((?:[A-Z][a-zA-Z\s&]+(?:et\s+al\.?)?,\s*(?:19|20)\d{2}[a-z]?)\)"),
        re.compile(r"\bRFC\s*#?\s*(\d{1,5})\b", re.IGNORECASE),
        re.compile(r"\bISO(?:/IEC)?\s*(\d{4,6}(?:-\d+)?(?::\d{4})?)\b", re.IGNORECASE),
        re.compile(r"\bIEEE\s*(?:Std\s*)?(\d{3,5}(?:\.\d+)?(?:-\d{4})?)\b", re.IGNORECASE),
        re.compile(r"\b(?:doi:\s*|https?://doi\.org/)(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b", re.IGNORECASE),
    ]

    # Logical causality connectors (Chinese & English)
    LOGICAL_CONNECTORS = [
        "因此", "所以", "推导得出", "由此可见", "必然导致", "充分必要条件", "前提是", "若且唯若",
        "therefore", "thus", "hence", "consequently", "implies", "leads to", "because",
        "if and only if", "as a result", "proves that", "contradicts"
    ]

    @classmethod
    def extract_from_document(cls, doc: LoadedDocument) -> List[AtomicClaim]:
        claims: List[AtomicClaim] = []
        claim_idx = 1

        for block in doc.blocks:
            if block.block_type == "heading":
                continue

            # If block is an explicit equation
            if block.block_type == "equation":
                claim = AtomicClaim(
                    claim_id=f"C{claim_idx:04d}",
                    block_id=block.block_id,
                    claim_type="MATHEMATICAL",
                    statement=f"Mathematical formulation: {block.text}",
                    raw_span=block.raw_content,
                    line_number=block.line_start,
                    page_number=block.page_num,
                    extracted_equations=[block.text],
                    context_heading=block.parent_heading,
                )
                claims.append(claim)
                claim_idx += 1
                continue

            # Split block text into sentence units
            sentences = cls._split_into_sentences(block.text)

            for sent in sentences:
                sent_clean = sent.strip()
                if len(sent_clean) < 10:  # Skip trivial fragments
                    continue

                extracted_units = cls._extract_quantities(sent_clean)
                extracted_eqs = cls._extract_inline_equations(sent_clean)
                extracted_cites = cls._extract_citations(sent_clean)
                has_complexity = bool(cls.COMPLEXITY_PATTERN.search(sent_clean))
                has_logical_connector = any(conn in sent_clean.lower() for conn in cls.LOGICAL_CONNECTORS)

                # Determine primary claim type
                claim_type = "EMPIRICAL_FACTUAL"

                if extracted_cites:
                    claim_type = "CITATION_ATTRIBUTION"
                elif extracted_units or any(w in sent_clean for w in ["守恒", "热力学", "卡诺", "动量", "速度", "加速度", "能量", "功率", "压强", "温度", "conservation", "energy", "velocity", "pressure", "force", "power"]):
                    claim_type = "PHYSICAL_AXIOMATIC"
                elif extracted_eqs or has_complexity or any(w in sent_clean for w in ["公式", "等式", "定理", "复杂度", "收敛", "equation", "theorem", "complexity", "bound", "integral", "derivative"]):
                    claim_type = "MATHEMATICAL"
                elif has_logical_connector:
                    claim_type = "LOGICAL"

                # Filter out pure narrative / meta sentences
                if claim_type != "EMPIRICAL_FACTUAL" or extracted_units or extracted_cites or len(sent_clean) > 30:
                    claims.append(AtomicClaim(
                        claim_id=f"C{claim_idx:04d}",
                        block_id=block.block_id,
                        claim_type=claim_type,
                        statement=sent_clean,
                        raw_span=sent_clean,
                        line_number=block.line_start,
                        page_number=block.page_num,
                        extracted_quantities=extracted_units,
                        extracted_equations=extracted_eqs,
                        extracted_citations=extracted_cites,
                        context_heading=block.parent_heading,
                    ))
                    claim_idx += 1

        return claims

    @classmethod
    def _split_into_sentences(cls, text: str) -> List[str]:
        # Split by Chinese and English punctuation marks: 。 ； ! ? . ; \n
        pattern = r"(?<=[。！？；\n])|(?<=[.!?])\s+"
        parts = re.split(pattern, text)
        return [p for p in parts if p and p.strip()]

    @classmethod
    def _extract_quantities(cls, text: str) -> List[Dict[str, str]]:
        matches = []
        for m in cls.UNIT_PATTERN.finditer(text):
            matches.append({
                "value": m.group(1),
                "unit": m.group(2),
                "matched_text": m.group(0),
            })
        return matches

    @classmethod
    def _extract_inline_equations(cls, text: str) -> List[str]:
        # Find $...$ inline math or equations with = or \approx
        math_inline = re.findall(r"\$([^$]+)\$", text)
        equations = []
        for m in math_inline:
            if "=" in m or "\\le" in m or "\\ge" in m or "<" in m or ">" in m or "\\approx" in m:
                equations.append(m.strip())

        # Also find plain text equalities like E = mc^2
        plain_eq = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*\s*=\s*[^,;。]+)", text)
        for pe in plain_eq:
            if len(pe.strip()) > 3 and not pe.strip().startswith("http"):
                equations.append(pe.strip())

        return list(set(equations))

    @classmethod
    def _extract_citations(cls, text: str) -> List[str]:
        citations = []
        for pattern in cls.CITATION_PATTERNS:
            for m in pattern.finditer(text):
                citations.append(m.group(0).strip())
        return list(set(citations))


if __name__ == "__main__":
    from document_loader import DocumentLoader
    if len(sys.argv) > 1:
        doc = DocumentLoader.load(sys.argv[1])
        claims = ClaimExtractor.extract_from_document(doc)
        print(f"Extracted {len(claims)} atomic claims from '{doc.title}':")
        for c in claims[:10]:
            print(f"[{c.claim_id}] ({c.claim_type}) {c.statement[:80]}...")
    else:
        print("Usage: python claim_extractor.py <path_to_document>")
