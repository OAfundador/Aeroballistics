"""The original program (SPIN-73, 1973), block by block, as objects.

This is not the 1973 code: it is a description of it, in our own words and notation, built
from the reading of the report (text, pp. 13-18; listing, pp. 79-86). Each block says what
the program computes, with which constants (DATA blocks), from which listing statements the
reading came (the sequential numbering the compiler printed on the left, "C164"...), what
could not be read and where it is implemented here. The listing is not reproduced in this
repository; it is in the report (DTIC AD0915628).

    from spin73.program import SPIN73
    print(SPIN73.describe())            # the whole program
    b = SPIN73.from_column("CMA")       # the block that computes CMα
    print(b)                            # formulas, rules, statements, implementation
    b.compute(spin73.M437)              # this block's columns for one projectile

Notation: VL, VN, VB, VCG, OR, DM, BD, BOOM, DIA, IX, IY, WGT, TWIST, DGUN, TEMP are the
card inputs; a1..a15, b1..b9, c1..c17, d1..d4, e1..e5, f1..f9 and g1 are the values of the
DATA blocks XA, XB, XC, XD, XE, XF and XG at the row's Mach.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass

from . import core


@dataclass(frozen=True)
class Block:
    """A piece of the original program: what it computes and where each part came from."""
    key: str
    title: str
    columns: tuple = ()             # output columns it produces
    data: tuple = ()                # DATA blocks it uses
    statements: tuple | None = None  # (first, last), the compiler's numbering
    pages: str = ""
    source: str = ""                # code, report text, or both
    description: str = ""
    formulas: tuple = ()            # in our notation
    rules: tuple = ()               # the program's conditions and decisions
    gaps: tuple = ()                # what was not read, and what was done
    implementation: str = ""        # where it is here, "module.function"

    def function(self):
        """The function that implements the block in this reconstruction."""
        module, name = self.implementation.rsplit(".", 1)
        return getattr(importlib.import_module(module), name)

    def compute(self, projectile) -> dict:
        """This block's columns for one projectile, at the 17 Mach numbers (via the whole program)."""
        if self.key == "input":
            return dict(RHO=core.air_density(projectile.TEMP),
                        A_SOUND=core.speed_of_sound(projectile.TEMP))
        t = core.table(projectile)
        if self.key == "output":
            return dict(TEXT=core.format_table(t))
        return {c: t[c] for c in self.columns if c in t}

    def _range(self) -> str:
        if self.statements is None:
            return "—"
        a, b = self.statements
        return f"C{a}" if a == b else f"C{a}–C{b}"

    def __str__(self) -> str:
        lines = [self.title,
                 f"  columns: {', '.join(self.columns) or '—'}",
                 f"  data: {', '.join(self.data) or '—'}",
                 f"  statements: {self._range()}; pages: {self.pages}; source: {self.source}",
                 f"  implementation: {self.implementation}",
                 "  " + self.description]
        lines += ["  = " + f for f in self.formulas]
        lines += ["  * " + r for r in self.rules]
        lines += ["  ! " + x for x in self.gaps]
        return "\n".join(lines)


class OriginalProgram:
    """The whole program, in the order the original computes it."""

    def __init__(self, blocks):
        self.blocks = tuple(blocks)

    def __iter__(self):
        return iter(self.blocks)

    def block(self, key: str) -> Block:
        for b in self.blocks:
            if b.key == key:
                return b
        raise KeyError(f"unknown block: {key}; there are {', '.join(b.key for b in self.blocks)}")

    def from_column(self, column: str) -> Block:
        """The block that produces an output column (CX, CMA, GYRO...)."""
        for b in self.blocks:
            if column in b.columns:
                return b
        raise KeyError(f"no block produces {column}")

    def describe(self, fmt: str = "text") -> str:
        if fmt == "text":
            return "\n\n".join(str(b) for b in self.blocks)
        if fmt != "markdown":
            raise ValueError("fmt: 'text' or 'markdown'")
        out = []
        for i, b in enumerate(self.blocks, 1):
            out.append(f"## {i}. {b.title}\n")
            out.append(b.description + "\n")
            out.append("| | |\n|---|---|")
            out.append(f"| Columns | {', '.join(f'`{c}`' for c in b.columns) or '—'} |")
            out.append(f"| Data | {', '.join(b.data) or '—'} |")
            out.append(f"| Listing statements | {b._range()} |")
            out.append(f"| Pages | {b.pages} |")
            out.append(f"| Source of the reading | {b.source} |")
            out.append(f"| Implementation | `{b.implementation}` |\n")
            if b.formulas:
                out.append("Formulas:\n")
                out += [f"- {f}" for f in b.formulas]
                out.append("")
            if b.rules:
                out.append("Rules:\n")
                out += [f"- {r}" for r in b.rules]
                out.append("")
            if b.gaps:
                out.append("What was not read:\n")
                out += [f"- {x}" for x in b.gaps]
                out.append("")
        return "\n".join(out).rstrip() + "\n"


SPIN73 = OriginalProgram((
    Block(
        key="input", title="Input card and atmosphere",
        pages="76–77 (card); listing (atmosphere)", source="Appendix B and code",
        description="Reads the card (geometry in calibers; diameter, inertias and weight in "
                    "English units) and computes the air density and the speed of sound from "
                    "the temperature.",
        formulas=("ΔT = TEMP − 59 °F",
                  "ρ = 0.002376 + (−4.784·ΔT + 0.01092·ΔT²)·10⁻⁶ slug/ft³",
                  "a = 49.04·√(459.6 + TEMP) ft/s"),
        rules=("on the original card, blank fields mean DM = 0, BD = 1.00 and TEMP = 0 °F; "
               "here the defaults are 0.12, 1.02 and 59 °F (pass zero to reproduce the blank "
               "card)",),
        implementation="spin73.core.air_density"),
    Block(
        key="drag", title="Axial force at zero yaw (CX)",
        columns=("CX",), data=("XA",), statements=(164, 174), pages="83–84",
        source="code (from C164 on) and text",
        description="A polynomial in the shape variables, plus three piecewise corrections: "
                    "long ogive, long cylinder and long boattail.",
        formulas=("u = min(VN, 3) − 2.5;   L = VL − VN − VB − 1.5;   R = VN²/OR − 0.40",
                  "β = 0 if VB ≤ 0.2;  VB − 0.2 if VB < 0.65;  0.45 from then on",
                  "CX = a1 + a2·u + a3·u² + a4·u³ + a5·min(L, 1.5) + a6·min(L, 1.5)² + a7·β "
                  "+ a8·R + a9·R² + a11·(BD − 1.02) + a12·(DM − 0.12)² − 0.01·(BOOM/1.36)² "
                  "− Δ_bt − Δ_og + Δ_cyl"),
        rules=("Δ_og, only with an ogive longer than 3 cal, in three continuous pieces: "
               "a13·(VN − 3) up to 3.48 cal; 0.48·a13 + a14·(VN − 3.48) up to 3.97; and "
               "0.48·a13 + 0.49·a14 + a15·(VN − 3.97) above. The text only documents the first "
               "piece",
               "Δ_cyl = 0.010·(L − 1.5) when L > 1.5",
               "Δ_bt = a10·(VB − 0.65) when VB ≥ 0.65"),
        gaps=("the start of the computation is on p. 83, which was not read: the Δ_bt term "
              "follows the report text, and the output warns when it is used",),
        implementation="spin73.core.cx"),
    Block(
        key="normal", title="Normal force, center of pressure and pitching moment",
        columns=("CNA", "CPN", "CMA"), data=("XB", "XC"), statements=(175, 212),
        pages="84–85", source="code",
        description="Adds the normal force and moment of the body (ogive and cylinder) to "
                    "those of the boattail; the center of pressure is the ratio of the two, "
                    "and the moment about the CG comes from the arm to the CG.",
        formulas=("v = min(VN, 3) − 2.47;   ℓ = VL − VN − VB − 2.15;   r = VN²/OR − 0.48;   "
                  "m = DM − 0.17;   n = max(VN − 3, 0);   w = min(VB, 1)",
                  "N_body = b1 + b2·v + b3·ℓ + b4·r + b5·v² + b6·ℓ²",
                  "N_bt = b7·β_N + w·(b8·v + b9·ℓ)",
                  "M_body = N_body·(c1 + c2·v + c3·v² + c4·v³ + c5·ℓ + c6·ℓ² + c7·ℓ³ + c8·r "
                  "+ c9·r² + c10·m + c11·r·v + c17·n)",
                  "M_bt = (VL/4.7)·(c12·β_M + w·(c13·v + c14·ℓ + c15·r + c16·r·v))",
                  "CNα = N_body + N_bt;   CPN = (M_body + M_bt)/CNα;   CMα = (VCG − CPN)·CNα"),
        rules=("boattail exponents: β_N = VB and β_M = VB^0.8 below Mach 0.95; β_N = VB^1.5 "
               "and β_M = VB from Mach 0.95 on (the text does not give the threshold); β_N = "
               "β_M = √VB when VB > 1",
               "N_bt never adds: if it comes out positive, it is set to zero (a rule of the "
               "code, missing from the text; it only acts with a short ogive at supersonic "
               "speeds)",
               "if M_bt comes out positive, the whole boattail is discarded: CNα = N_body and "
               "M_bt = 0 (a rule of the code, missing from the text)",
               "the c11 term multiplies r·v; the text prints another variable there, a "
               "typographical error"),
        gaps=("the continuation card of XC15 (Mach 1.2 to 5) was not printed: values "
              "recovered from the output tables",
              "the XC12 line is faded: cells decided by the tables"),
        implementation="spin73.core.normal_and_moment"),
    Block(
        key="yaw", title="Yaw term of the axial force (CX2)",
        columns=("CX2",), data=("XD",), statements=(213, 213), pages="85", source="code",
        description="The term that, added to CNα, gives the yaw drag per sin² of the yaw.",
        formulas=("CX2 = d1 + d2·L + d3·R + d4·VB − CNα   (L and R as in the drag)",),
        rules=("the yaw drag is CX2 + CNα, not CX2 (p. 15)",),
        implementation="spin73.core.cx2"),
    Block(
        key="magnus", title="Magnus force and moment",
        columns=("CYPA", "CNPA", "CPF1", "CPF5", "CNPA5"), data=("XE",),
        statements=(214, 231), pages="85", source="code",
        description="The Magnus force and, for three angles of attack (1°, 2° and 5°), its "
                    "center of pressure and the moment about the CG.",
        formulas=("Y = e1·VL;   CYPA = Y − 0.1·VB",
                  "for each angle, with e = e2 (1°), e3 (2°) or e4 (5°):   N = −Y·(e + 0.55·L "
                  "+ 0.8·(VN − 2.5)) + VL·VB/4.7",
                  "CPF = −N/CYPA + Δ_lb;   moment = (VCG − CPF)·CYPA"),
        rules=("Δ_lb = e5·(VL − 6) when VL > 6 (long-body term, missing from the text)",
               "at 1° come CPF1 and CNPA; at 5°, CPF5 and CNPA5; the value at 2° is computed "
               "and does not enter any printed column"),
        gaps=("the first card of XE5 (Mach 0.01 to 1.75) was not printed: values recovered "
              "from the output tables",),
        implementation="spin73.core.magnus"),
    Block(
        key="polynomial", title="Magnus \"polynomial coefficients\" (CNPA3, CNPA5P)",
        columns=("CNPA3", "CNPA5P"), statements=(278, 281), pages="86", source="code",
        description="Two printed columns that should fit a polynomial to the Magnus moment at "
                    "three angles.",
        formulas=("D = CNPA(5°) − CNPA(1°)",
                  "CNPA5P = ((D + 0.3) − 9·D)/0.0072",
                  "CNPA3 = (D − 0.0001·CNPA5P)/0.01"),
        rules=("the constants are those of a polynomial C1 + C3·δ² + C5·δ⁴ fitted at δ = 0.1 "
               "and 0.3, but the second point uses D + 0.3 instead of the value at 2°: the two "
               "columns carry a single degree of freedom and always obey CNPA3 + 0.1·CNPA5P = "
               "3.75 (a defect of the original, reproduced)",
               "the program prints \"CNPA5\" for this column and \"CNPA-5\" for the moment at "
               "5°; here they are CNPA5P and CNPA5"),
        implementation="spin73.core.magnus_polynomial_coefs"),
    Block(
        key="cmq", title="Pitch damping (CMQ)",
        columns=("CMQ",), data=("XF",), statements=(232, 238), pages="85", source="code",
        description="Cmq + Cmα̇ in the qd/2V convention.",
        formulas=("λ = VL − 5;   g = VCG − 3",
                  "K = f1 + f2·λ + f3·λ² + f4·g + f5·g·λ + f6·g·λ² + f7·g·VB + f8·VB",
                  "CMQ = −5.093·K − Δ_lb"),
        rules=("Δ_lb = f9·(VL − 6) when VL > 6 (long-body term, missing from the text)",),
        gaps=("the second card of XF7 (Mach 1.1 to 2.5) was not printed: values recovered "
              "from the 5\"/38 table",),
        implementation="spin73.core.cmq"),
    Block(
        key="clp", title="Roll damping (CLP)",
        columns=("CLP",), data=("XG",), statements=(239, 239), pages="85", source="code",
        description="Clp in the pd/2V convention, proportional to the length.",
        formulas=("CLP = g1·VL/5.51",),
        rules=("the divisor is a program constant that the text gives as 5.51, the length "
               "of the M437",),
        implementation="spin73.core.clp"),
    Block(
        key="stability", title="Stability analysis",
        columns=("GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2",
                 "L1", "L2", "L15", "L25", "DELT", "DISP"),
        statements=(240, 266), pages="85–86", source="code and text (pp. 17–18)",
        description="With diameter, mass, inertias and rifling twist: the spin, the gyroscopic "
                    "and dynamic stability factors, and the frequencies and damping rates of "
                    "the two yaw modes.",
        formulas=("V = Mach·a (ft/s);   twist = TWIST·DGUN (inches per turn);   "
                  "p = 2π·V/(twist/12) (rad/s)",
                  "s_g = 1352.4·IX²/(ρ·IY·CMα·twist²·DIA³)   (IX, IY in lb·in²; lengths "
                  "in inches)",
                  "m = WGT/32.174;   d = DIA/12;   Ix = IX/(32.174·144);   Iy = IY/(32.174·144)"
                  "   (foot and slug)",
                  "k₁ = m·d²/Ix;   k₂ = m·d²/Iy",
                  "s_d = 2·(CNα − CX + (k₁/2)·CNPA) / (CNα − CX − (k₂/2)·CMQ + (k₁/2)·CLP);   "
                  "RECIP = 1/(s_d·(2 − s_d))   (SBAR5 and RECIP5 with the moment at 5°)",
                  "σ = √(1 − 1/s_g);   ω₁,₂ = p·Ix/(2·Iy)·(1 ± σ)",
                  "λ₁,₂ = (ρ·A/(4m))·[−CNα·(1 ∓ 1/σ) + (k₂/2)·(1 ± 1/σ)·CMQ ± (k₁/σ)·CNPA],   "
                  "A = π·d²/4   (L15 and L25 with the moment at 5°)",
                  "DELT = 6.28/(20·ω₁)",
                  "DISP = (CNα − CX)·IY·(ω₁ − ω₂)·3.635/(CMα·WGT·DIA·V)"),
        rules=("with no diameter (DIA = 0), there is no stability analysis",
               "with s_g < 1.001, only the Mach and s_g are printed",
               "the constant 1352.4 is the code's; the physics with g = 32.174 would give 1349.8 "
               "(+0.19 %)",
               "the text (p. 18) prints the sign of the first term of λ swapped; the code and "
               "the tables use the sign above"),
        gaps=("DISP: the formula is the code's; the quantity depends on the report's "
              "reference 71 (Whyte 1970), unavailable",),
        implementation="spin73.core.stability"),
    Block(
        key="output", title="Printout", statements=(282, 294), pages="86", source="code",
        description="For each Mach, one line with the 14 aerodynamic coefficients and, with "
                    "mass and rifling, one line with the 14 stability columns.",
        implementation="spin73.core.format_table"),
))

HEADER = """# The original program, block by block

A description of the 1973 SPIN-73 in our own words and notation: what each piece of the
program computes, with which constants, where the reading came from, what could not be read
and where it is implemented in this reconstruction. **It is not the original code**, which is
in the report (DTIC AD0915628, listing on pp. 79–86) and is not reproduced in this repository.

Generated from `src/spin73/program.py` (`python -m spin73.program --doc`); the evidence for
each reading is in [TRANSCRIPTION_NOTES.md](TRANSCRIPTION_NOTES.md).

Notation: VL, VN, VB, VCG, OR, DM, BD, BOOM, DIA, IX, IY, WGT, TWIST, DGUN and TEMP are the
card inputs; a1..a15, b1..b9, c1..c17, d1..d4, e1..e5, f1..f9 and g1 are the values of the
DATA blocks XA, XB, XC, XD, XE, XF and XG at the row's Mach. "Statements" is the sequential
numbering the compiler printed to the left of each listing line.

"""


def document() -> str:
    """The text of docs/ORIGINAL_PROGRAM.md."""
    return HEADER + SPIN73.describe("markdown")


__all__ = ["Block", "OriginalProgram", "SPIN73", "document"]


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--doc" in sys.argv:
        print(document(), end="")
    else:
        print(SPIN73.describe("markdown" if "--markdown" in sys.argv else "text"))
