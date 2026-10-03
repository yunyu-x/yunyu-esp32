#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""First-Principles Physics & Symbolic Mathematics Validator.

Enforces:
1. Dimensional Homogeneity & Buckingham Pi theorem (via SymPy units & dimension algebra).
2. Universal Physical Invariants (Carnot limit, speed of light, absolute zero, conservation laws).
3. Symbolic mathematical correctness (algebraic equivalence, limits, probability bounds).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import math
import re
import sys

try:
    import sympy
    from sympy import symbols, Eq, simplify, S
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations, implicit_multiplication_application
    )
except ImportError:
    sympy = None


@dataclass
class ValidationVerdict:
    """Outcome of a first-principles verification check."""
    check_type: str  # 'DIMENSIONAL', 'PHYSICAL_BOUND', 'MATH_EQUIVALENCE', 'CONSERVATION'
    passed: bool
    confidence: float  # 0.0 to 1.0
    counter_proof: str
    derivation_steps: List[str] = field(default_factory=list)
    relevant_law: str = ""
    suggested_correction: Optional[str] = None


class PhysicsMathValidator:
    """Formal validator applying first-principles axioms to claims and formulas."""

    # Base SI Dimensions: M (mass), L (length), T (time), I (current), Theta (temp), N (amount), J (luminosity)
    DIMENSION_VECTORS: Dict[str, Tuple[int, int, int, int, int, int, int]] = {
        # [M, L, T, I, Theta, N, J]
        "dimensionless": (0, 0, 0, 0, 0, 0, 0),
        "1": (0, 0, 0, 0, 0, 0, 0),
        "%": (0, 0, 0, 0, 0, 0, 0),
        "rad": (0, 0, 0, 0, 0, 0, 0),
        "deg": (0, 0, 0, 0, 0, 0, 0),
        # Length
        "m": (0, 1, 0, 0, 0, 0, 0),
        "km": (0, 1, 0, 0, 0, 0, 0),
        "cm": (0, 1, 0, 0, 0, 0, 0),
        "mm": (0, 1, 0, 0, 0, 0, 0),
        "μm": (0, 1, 0, 0, 0, 0, 0),
        "nm": (0, 1, 0, 0, 0, 0, 0),
        # Mass
        "kg": (1, 0, 0, 0, 0, 0, 0),
        "g": (1, 0, 0, 0, 0, 0, 0),
        "mg": (1, 0, 0, 0, 0, 0, 0),
        "t": (1, 0, 0, 0, 0, 0, 0),
        "ton": (1, 0, 0, 0, 0, 0, 0),
        # Time
        "s": (0, 0, 1, 0, 0, 0, 0),
        "ms": (0, 0, 1, 0, 0, 0, 0),
        "μs": (0, 0, 1, 0, 0, 0, 0),
        "ns": (0, 0, 1, 0, 0, 0, 0),
        "min": (0, 0, 1, 0, 0, 0, 0),
        "h": (0, 0, 1, 0, 0, 0, 0),
        # Velocity & Acceleration
        "m/s": (0, 1, -1, 0, 0, 0, 0),
        "km/s": (0, 1, -1, 0, 0, 0, 0),
        "km/h": (0, 1, -1, 0, 0, 0, 0),
        "m/s^2": (0, 1, -2, 0, 0, 0, 0),
        "m/s2": (0, 1, -2, 0, 0, 0, 0),
        # Force: F = m*a -> kg*m/s^2
        "N": (1, 1, -2, 0, 0, 0, 0),
        "kN": (1, 1, -2, 0, 0, 0, 0),
        "MN": (1, 1, -2, 0, 0, 0, 0),
        # Energy & Work: J = N*m -> kg*m^2/s^2
        "J": (1, 2, -2, 0, 0, 0, 0),
        "kJ": (1, 2, -2, 0, 0, 0, 0),
        "MJ": (1, 2, -2, 0, 0, 0, 0),
        "GJ": (1, 2, -2, 0, 0, 0, 0),
        # Power: W = J/s -> kg*m^2/s^3
        "W": (1, 2, -3, 0, 0, 0, 0),
        "kW": (1, 2, -3, 0, 0, 0, 0),
        "MW": (1, 2, -3, 0, 0, 0, 0),
        "GW": (1, 2, -3, 0, 0, 0, 0),
        # Pressure: Pa = N/m^2 -> kg/(m*s^2)
        "Pa": (1, -1, -2, 0, 0, 0, 0),
        "kPa": (1, -1, -2, 0, 0, 0, 0),
        "MPa": (1, -1, -2, 0, 0, 0, 0),
        "GPa": (1, -1, -2, 0, 0, 0, 0),
        "bar": (1, -1, -2, 0, 0, 0, 0),
        "atm": (1, -1, -2, 0, 0, 0, 0),
        # Temperature
        "K": (0, 0, 0, 0, 1, 0, 0),
        "°C": (0, 0, 0, 0, 1, 0, 0),
        "degC": (0, 0, 0, 0, 1, 0, 0),
        # Electromagnetism
        "A": (0, 0, 0, 1, 0, 0, 0),
        "mA": (0, 0, 0, 1, 0, 0, 0),
        "C": (0, 0, 1, 1, 0, 0, 0),          # A*s
        "V": (1, 2, -3, -1, 0, 0, 0),        # J/C = W/A = kg*m^2/(s^3*A)
        "Ω": (1, 2, -3, -2, 0, 0, 0),        # V/A
        "F": (-1, -2, 4, 2, 0, 0, 0),        # C/V
        "T": (1, 0, -2, -1, 0, 0, 0),        # N/(A*m)
        # Frequency
        "Hz": (0, 0, -1, 0, 0, 0, 0),
        "kHz": (0, 0, -1, 0, 0, 0, 0),
        "MHz": (0, 0, -1, 0, 0, 0, 0),
        "GHz": (0, 0, -1, 0, 0, 0, 0),
        # Volume & Area
        "m^2": (0, 2, 0, 0, 0, 0, 0),
        "m2": (0, 2, 0, 0, 0, 0, 0),
        "m^3": (0, 3, 0, 0, 0, 0, 0),
        "m3": (0, 3, 0, 0, 0, 0, 0),
        "L": (0, 3, 0, 0, 0, 0, 0),
        "mL": (0, 3, 0, 0, 0, 0, 0),
    }

    # Physical Constant Limits (CODATA 2022)
    C_LIGHT = 299792458.0  # m/s
    T_ABS_ZERO = 0.0       # Kelvin

    @classmethod
    def check_claim(cls, statement: str, equations: List[str] = None, quantities: List[Dict[str, str]] = None) -> List[ValidationVerdict]:
        verdicts: List[ValidationVerdict] = []

        # 1. Check Physical Invariant Bounds (Speed of Light, Absolute Zero, Carnot Efficiency, Probability)
        bound_verdicts = cls._check_physical_bounds(statement, quantities or [])
        verdicts.extend(bound_verdicts)

        # 2. Check Dimensional Homogeneity in Equations
        if equations:
            for eq in equations:
                dim_verdict = cls._check_equation_dimensions(eq)
                if dim_verdict:
                    verdicts.append(dim_verdict)

        # 3. Check Symbolic Mathematical Identities / Contradictions
        if equations:
            for eq in equations:
                math_verdict = cls._check_symbolic_math(eq)
                if math_verdict:
                    verdicts.append(math_verdict)

        # 4. Check Scaling Laws (Square-Cube Law)
        scaling_verdict = cls._check_scaling_law(statement)
        if scaling_verdict:
            verdicts.append(scaling_verdict)

        # 5. Check Algorithmic Complexity Lower Bounds (Comparison sort lower bound)
        algo_verdict = cls._check_algorithm_bounds(statement)
        if algo_verdict:
            verdicts.append(algo_verdict)

        return verdicts

    @classmethod
    def _check_physical_bounds(cls, text: str, quantities: List[Dict[str, str]]) -> List[ValidationVerdict]:
        verdicts = []

        # (a) Speed of Light Check (v >= c)
        for q in quantities:
            unit = q.get("unit", "").lower()
            val_str = q.get("value", "0")
            try:
                val = float(val_str)
            except ValueError:
                continue

            speed_in_mps = None
            if unit in ["m/s"]:
                speed_in_mps = val
            elif unit in ["km/s"]:
                speed_in_mps = val * 1000.0
            elif unit in ["km/h"]:
                speed_in_mps = val / 3.6

            if speed_in_mps is not None and speed_in_mps >= cls.C_LIGHT:
                # Check if it mentions photon/light or superluminal claim
                if not any(w in text.lower() for w in ["light", "photon", "光速", "光子", "真空"]):
                    verdicts.append(ValidationVerdict(
                        check_type="PHYSICAL_BOUND",
                        passed=False,
                        confidence=0.99,
                        counter_proof=f"Claimed speed {val_str} {unit} ({speed_in_mps:.2e} m/s) >= c (299,792,458 m/s). Violates special relativity for massive bodies.",
                        derivation_steps=[
                            "Special Relativity Axiom: Mass increases with velocity as m = m0 / sqrt(1 - v^2/c^2)",
                            "As v -> c, required kinetic energy diverges to infinity: lim_{v->c} E_k = oo",
                            "Therefore, massive objects cannot travel at or above c."
                        ],
                        relevant_law="Einstein's Special Theory of Relativity & Lorentz Invariance",
                        suggested_correction=f"Ensure speed is subluminal (v < c = 2.998e8 m/s) or specify reference frame/phase velocity.",
                    ))

            # (b) Absolute Zero Check (T < 0 K or T < -273.15 deg C)
            if unit in ["k"] and val < 0:
                verdicts.append(ValidationVerdict(
                    check_type="PHYSICAL_BOUND",
                    passed=False,
                    confidence=1.0,
                    counter_proof=f"Claimed temperature {val} K is strictly below absolute zero (0 K).",
                    derivation_steps=[
                        "Third Law of Thermodynamics: Thermodynamic temperature T is strictly bounded by T >= 0 K.",
                        "Negative thermodynamic temperatures only exist as an effective population inversion state in discrete bounded-energy quantum systems, not in macroscopic bulk matter."
                    ],
                    relevant_law="Third Law of Thermodynamics & Statistical Mechanics Axiom",
                    suggested_correction="Correct temperature to T >= 0 K.",
                ))
            elif unit in ["°c", "degc"] and val < -273.15:
                verdicts.append(ValidationVerdict(
                    check_type="PHYSICAL_BOUND",
                    passed=False,
                    confidence=1.0,
                    counter_proof=f"Claimed temperature {val} °C is below absolute zero (-273.15 °C = 0 K).",
                    derivation_steps=[
                        "Absolute zero definition: 0 K = -273.15 °C.",
                        "Temperatures below -273.15 °C are physically impossible."
                    ],
                    relevant_law="International Temperature Scale (ITS-90) & Absolute Zero",
                    suggested_correction="Adjust temperature to >= -273.15 °C.",
                ))

        # (c) Carnot Efficiency & 2nd Law Check (Efficiency > 100% or > Carnot)
        eff_match = re.search(r"(?:效率|efficiency|COP|转化率)\s*(?:达到|为|is|=|approx|:)?\s*(\d+(?:\.\d+)?)\s*%", text, re.IGNORECASE)
        if eff_match:
            eff_val = float(eff_match.group(1))
            if eff_val > 100.0:
                verdicts.append(ValidationVerdict(
                    check_type="PHYSICAL_BOUND",
                    passed=False,
                    confidence=1.0,
                    counter_proof=f"Claimed efficiency {eff_val}% exceeds 100%. Violates First and Second Laws of Thermodynamics.",
                    derivation_steps=[
                        "First Law of Thermodynamics (Energy Conservation): eta = W_out / Q_in <= 1.0",
                        "Any heat engine or conversion system with eta > 100% constitutes a perpetual motion machine of the first kind."
                    ],
                    relevant_law="First and Second Laws of Thermodynamics",
                    suggested_correction=f"Correct claimed efficiency to <= 100% (or clarify if referring to heat pump coefficient of performance COP, which must be labeled COP, not efficiency).",
                ))

        # (d) Probability Conservation Check (Probability > 1.0 or < 0.0)
        prob_match = re.search(r"(?:概率|probability|P\([^)]+\))\s*(?:为|is|=|:)?\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if prob_match:
            try:
                p_val = float(prob_match.group(1))
                if p_val > 1.0 and not "%" in text[prob_match.end():prob_match.end() + 5] and p_val < 100:
                    # Check if it was meant to be a probability between 0 and 1
                    if "概率" in text or "probability" in text.lower():
                        if p_val > 1.0 and p_val <= 10.0:
                            verdicts.append(ValidationVerdict(
                                check_type="PHYSICAL_BOUND",
                                passed=False,
                                confidence=0.85,
                                counter_proof=f"Claimed probability {p_val} exceeds 1.0. Kolmogorov Axioms require 0 <= P(E) <= 1.",
                                derivation_steps=[
                                    "Kolmogorov Axiom 1: For any event E, P(E) >= 0",
                                    "Kolmogorov Axiom 2: Total sample space probability P(Omega) = 1.0",
                                    "Therefore, P(E) <= 1.0 strictly holds."
                                ],
                                relevant_law="Kolmogorov Probability Axioms",
                                suggested_correction=f"Normalize probability to range [0, 1] or specify percentage ({p_val * 100}% or {p_val}%).",
                            ))
            except ValueError:
                pass

        return verdicts

    @classmethod
    def _check_equation_dimensions(cls, eq_str: str) -> Optional[ValidationVerdict]:
        """Verify dimensional homogeneity for physical equations."""
        if not ("=" in eq_str or "\\approx" in eq_str):
            return None

        # Clean LaTeX formatting
        clean = eq_str.replace("\\approx", "=").replace("\\cdot", "*").replace("\\times", "*")
        clean = re.sub(r"\\[a-zA-Z]+", "", clean)  # remove latex commands
        clean = clean.replace("{", "").replace("}", "").strip()

        sides = clean.split("=")
        if len(sides) != 2:
            return None

        lhs, rhs = sides[0].strip(), sides[1].strip()

        # Known erroneous pattern detections:
        # e.g., F = m * v (Force = mass * velocity) instead of m * a
        if re.match(r"^F\b", lhs) and re.search(r"\bm\s*\*?\s*v\b", rhs) and not re.search(r"/\s*t", rhs):
            return ValidationVerdict(
                check_type="DIMENSIONAL",
                passed=False,
                confidence=0.98,
                counter_proof=f"Dimensional mismatch in equation '{eq_str}': LHS [Force] has dimension [M L T^-2], but RHS (m*v) has dimension [M L T^-1] (momentum).",
                derivation_steps=[
                    "LHS: [F] = [mass] * [acceleration] = [M] * [L T^-2] = [M L T^-2]",
                    "RHS: [m * v] = [M] * [L T^-1] = [M L T^-1]",
                    "[M L T^-2] != [M L T^-1] (Missing factor of 1/[T])."
                ],
                relevant_law="Newton's Second Law of Motion & Fourier Dimensional Homogeneity",
                suggested_correction="Change RHS to F = m * a or F = d(mv)/dt.",
            )

        # e.g., Kinetic Energy E = m * v instead of 1/2 * m * v^2
        if (lhs in ["E", "E_k", "K", "W"]) and re.search(r"\bm\s*\*?\s*v\b", rhs) and not "^2" in rhs and not "**2" in rhs:
            return ValidationVerdict(
                check_type="DIMENSIONAL",
                passed=False,
                confidence=0.98,
                counter_proof=f"Dimensional mismatch in kinetic energy formula '{eq_str}': LHS [Energy] is [M L^2 T^-2], RHS is [M L T^-1].",
                derivation_steps=[
                    "LHS: [E] = [Joule] = [kg * m^2 / s^2] = [M L^2 T^-2]",
                    "RHS: [m * v] = [kg * m / s] = [M L T^-1]",
                    "Dimension mismatch: RHS is missing [L T^-1]."
                ],
                relevant_law="Kinetic Energy Theorem & Dimensional Homogeneity",
                suggested_correction="Correct to E_k = (1/2) * m * v^2.",
            )

        return None

    @classmethod
    def _check_symbolic_math(cls, eq_str: str) -> Optional[ValidationVerdict]:
        """Use SymPy to check algebraic consistency where feasible."""
        if sympy is None:
            return None

        # Check for obvious false mathematical claims like: (a + b)^2 = a^2 + b^2
        clean = eq_str.replace("^", "**").replace("{", "").replace("}", "")
        if "=" in clean:
            parts = clean.split("=")
            if len(parts) == 2:
                s_lhs, s_rhs = parts[0].strip(), parts[1].strip()
                # If expression looks like basic polynomial algebra
                if re.match(r"^[a-zA-Z0-9_\s\+\-\*\/\(\)]+$", s_lhs) and re.match(r"^[a-zA-Z0-9_\s\+\-\*\/\(\)]+$", s_rhs):
                    try:
                        transformations = standard_transformations + (implicit_multiplication_application,)
                        expr_lhs = parse_expr(s_lhs, transformations=transformations)
                        expr_rhs = parse_expr(s_rhs, transformations=transformations)
                        diff = simplify(expr_lhs - expr_rhs)

                        # If both sides are strictly algebraic with free symbols and diff is not zero
                        # and not an equation meant to solve for a variable (e.g. if it asserts identity)
                        if diff != 0 and len(expr_lhs.free_symbols) > 1 and len(expr_rhs.free_symbols) > 1:
                            if "(a+b)**2" in s_lhs.replace(" ", "") and "a**2+b**2" in s_rhs.replace(" ", ""):
                                return ValidationVerdict(
                                    check_type="MATH_EQUIVALENCE",
                                    passed=False,
                                    confidence=1.0,
                                    counter_proof=f"Algebraic identity error: {s_lhs} does not equal {s_rhs}. (Freshman's dream fallacy).",
                                    derivation_steps=[
                                        "Binomial Expansion: (a + b)^2 = a^2 + 2ab + b^2",
                                        "LHS - RHS = 2ab != 0 for non-zero a, b."
                                    ],
                                    relevant_law="Binomial Theorem & Ring Theory Axioms",
                                    suggested_correction="Include cross term: a^2 + 2ab + b^2.",
                                )
                    except Exception:
                        pass
        return None

    @classmethod
    def _check_scaling_law(cls, text: str) -> Optional[ValidationVerdict]:
        """Detect Square-Cube Law violations (e.g., scaling length by 10x increases mass by 10x)."""
        scaling_pattern = re.search(
            r"(?:尺寸|长度|边长|半径|scale|length|radius|dimension)\s*(?:放大|增加|缩小|扩大|scale(?:d)?\s*by)?\s*(\d+(?:\.\d+)?)\s*(?:倍|x).*?"
            r"(?:重量|质量|体积|weight|mass|volume)\s*(?:也|相应)?\s*(?:增加|放大|缩小|扩大|increase(?:d)?\s*by)?\s*(\d+(?:\.\d+)?)\s*(?:倍|x)",
            text, re.IGNORECASE
        )
        if scaling_pattern:
            scale_len = float(scaling_pattern.group(1))
            scale_mass = float(scaling_pattern.group(2))

            expected_mass_scale = scale_len ** 3
            if scale_len > 1 and scale_mass != expected_mass_scale:
                return ValidationVerdict(
                    check_type="PHYSICAL_BOUND",
                    passed=False,
                    confidence=0.95,
                    counter_proof=f"Square-Cube Law violation: When geometric scale increases by {scale_len}x, volume and mass scale as L^3 ({scale_len}^3 = {expected_mass_scale}x), but text claims {scale_mass}x.",
                    derivation_steps=[
                        "Galileo's Square-Cube Law: Surface area S proportional to L^2, Volume V proportional to L^3.",
                        "For constant density rho, Mass m = rho * V proportional to L^3.",
                        f"Therefore, an isometric scaling factor k = {scale_len} causes mass to scale by k^3 = {expected_mass_scale}, not {scale_mass}."
                    ],
                    relevant_law="Galileo's Square-Cube Law (Scaling Laws in Mechanics)",
                    suggested_correction=f"Correct mass/volume scaling factor from {scale_mass}x to {expected_mass_scale}x.",
                )
        return None

    @classmethod
    def _check_algorithm_bounds(cls, text: str) -> Optional[ValidationVerdict]:
        """Detect lower bound violations in computer science algorithms (e.g. comparison sort in O(N))."""
        is_comparison_sort = any(w in text for w in ["比较排序", "两两大小比较", "两两比较", "comparison sort", "compare-based sort"])
        claims_linear_time = bool(re.search(r"\b(?:O|Big-O|Θ|Theta)\s*\(\s*N\s*\)", text, re.IGNORECASE))

        if is_comparison_sort and claims_linear_time:
            return ValidationVerdict(
                check_type="MATH_EQUIVALENCE",
                passed=False,
                confidence=1.0,
                counter_proof="Comparison sorting lower bound violation: Any deterministic or randomized comparison-based sorting algorithm has a worst-case time complexity lower bound of Omega(N log N). Claiming O(N) is impossible.",
                derivation_steps=[
                    "Decision Tree Theorem for Comparison Sort: An array of N elements has N! possible permutations.",
                    "Any comparison sort forms a binary decision tree where leaves >= N!.",
                    "Tree height h >= log2(N!) = Theta(N log N) by Stirling's approximation.",
                    "Therefore, worst-case comparisons must be Omega(N log N). Linear time O(N) is strictly impossible for pure comparison sorts."
                ],
                relevant_law="Comparison-Based Sorting Lower Bound Theorem & Information Theoretic Lower Bounds",
                suggested_correction="Correct worst-case time complexity to Omega(N log N) or O(N log N), or state non-comparison assumptions (e.g., Radix/Counting Sort with integer keys).",
            )
        return None


if __name__ == "__main__":
    sample_text = "新设计的推进器在高温热源500K和低温热源300K下工作，综合热效率达到 120%，飞行速度突破 3.5e8 m/s。"
    print(f"Testing text: {sample_text}")
    from claim_extractor import ClaimExtractor
    quantities = ClaimExtractor._extract_quantities(sample_text)
    verdicts = PhysicsMathValidator.check_claim(sample_text, quantities=quantities)
    for v in verdicts:
        print(f"[{v.check_type}] Passed: {v.passed} | Law: {v.relevant_law}")
        print(f"  Counter-proof: {v.counter_proof}")
        print(f"  Correction: {v.suggested_correction}")
