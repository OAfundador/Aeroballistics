"""SPIN-73 conventions and conversion to the modern normalizations.

What the report defines (Nomenclature, pp. 7-8, and Appendix B, p. 77)
-----------------------------------------------------------------------
Classic NACA/BRL style: dynamic pressure q̄ = ½ρV², reference area A = πd²/4, reference
length d (projectile diameter). Moments about the CG.

  CX     axial force,            F_X / q̄A                (at zero yaw: CX0 = CD0)
  CX2    yaw axial force,        per sin²ᾱ
  CNA    normal force,           d(F_N / q̄A) / d(sin ᾱ)
  CMA    pitching moment,        d(M_m / q̄Ad) / d(sin ᾱ), about the CG
  CPN    center of pressure of the normal force, calibers from the NOSE
  CYPA   Magnus force,           F_Yp / q̄A(pd/2V), per sin ᾱ
  CNPA   Magnus moment,          M_np / q̄Ad(pd/2V), per sin ᾱ, about the CG
  CPF1/5 center of pressure of the Magnus force at 1° and 5°, calibers from the nose
  CMQ    pitch damping,          M_mq / q̄Ad(qd/2V)
  CLP    roll damping,           M_lp / q̄Ad(pd/2V)
  VCG    CG in calibers from the nose

Points that need conversion when comparing with modern sources (McCoy, BRL/ARL after ~1970,
PRODAS, CFD):

  1. Nondimensional rates: SPIN-73 uses pd/2V and qd/2V; modern sources use pd/V and qd/V.
     The modern value is HALF of SPIN-73's: Cmq+Cmα̇ = CMQ/2, Clp = CLP/2, Cmpα = CNPA/2,
     CNpα = CYPA/2.
  2. The SPIN-73 CMQ is the Cmq + Cmα̇ that free flight measures (there is no separate Cmα̇).
  3. CX2 is NOT the yaw drag. The report itself (p. 15) says the yaw drag is CX2 + CNα:
     CDδ² = CX2 + CNA.
  4. Lift force: CLα = CNα − CD0 (small yaw).
  5. Derivatives "per sin ᾱ" = "per radian" at small yaw; CNPA3/CNPA5P are per sin³ᾱ and
     sin⁵ᾱ (and suffer from the original's defect, NOTES T12: CNPA3 + 0.1·CNPA5P = 3.75).
  6. Positions from the nose, in calibers. Many sources give them from the BASE (Hitchcock,
     BRL MR 1833, in inches): x_nose = VL − x_base.
  7. Signs: CMA > 0 is an overturning (destabilizing) moment, as in McCoy. The Magnus sign
     varies between sources (positive side of the force, direction of spin): check each
     source's definition before comparing.
  8. Old BRL K coefficients (Hitchcock, BRL 620): factor π/8, see
     scripts/free_flight/hitchcock/conversions.py.

Column names: the program prints "CNPA5" for the QUINTIC coefficient and "CNPA-5" for the
secant slope at 5°. Here they are called CNPA5P and CNPA5 (PRINTED_NAMES).

Blank inputs on the original card (Appendix B, note B): BD = 0 becomes 1.00; OR = 0 becomes
a secant ogive (2·VN²); DGUN = 0 becomes DIA; a blank DM stays 0; a blank TEMP is 0 °F (that
is what the tables without mass properties print: density 0.00270). This package's
`Projectile` defaults to DM = 0.12 and BD = 1.02 (the NAUTO = 1 "automatic dimensions"
values) and TEMP = 59 °F; to reproduce a card with blank fields, pass DM=0, BD=0 and TEMP=0
explicitly.
"""
import numpy as np

PRINTED_NAMES = {"CNPA5P": "CNPA5 (quintic, per sin⁵ᾱ)", "CNPA5": "CNPA-5 (secant at 5°)",
                 "CYPA": "CYP"}


def to_modern(t: dict, VL: float | None = None) -> dict:
    """SPIN-73 columns (dictionary from `aeroballistics.table`) in the modern normalization
    (pd/V, qd/V; CDδ², CLα). Positions in calibers; from the nose and, if VL is given, from
    the base."""
    g = {k: np.asarray(v, float) for k, v in t.items()}
    out = dict(
        MACH=g["MACH"],
        CD0=g["CX"],
        CDd2=g["CX2"] + g["CNA"],
        CNa=g["CNA"],
        CLa=g["CNA"] - g["CX"],
        Cma=g["CMA"],
        Cmq_Cmad=g["CMQ"] / 2.0,
        Clp=g["CLP"] / 2.0,
        CNpa=g["CYPA"] / 2.0,
        Cmpa=g["CNPA"] / 2.0,
        Cmpa_5deg=g["CNPA5"] / 2.0,
        CP_nose=g["CPN"],
        CPmagnus_nose=g["CPF1"],
    )
    if VL is not None:
        out["CP_base"] = VL - g["CPN"]
    return out


def from_modern(m: dict) -> dict:
    """The inverse of `to_modern`, to bring modern experimental data into the SPIN-73 form.
    Accepts only the keys present."""
    conv = {
        "CD0": ("CX", lambda x: x),
        "CNa": ("CNA", lambda x: x),
        "Cma": ("CMA", lambda x: x),
        "Cmq_Cmad": ("CMQ", lambda x: 2.0 * x),
        "Clp": ("CLP", lambda x: 2.0 * x),
        "CNpa": ("CYPA", lambda x: 2.0 * x),
        "Cmpa": ("CNPA", lambda x: 2.0 * x),
        "CP_nose": ("CPN", lambda x: x),
    }
    out = {conv[k][0]: conv[k][1](np.asarray(v, float)) for k, v in m.items() if k in conv}
    if "CDd2" in m and "CNa" in m:
        out["CX2"] = np.asarray(m["CDd2"], float) - np.asarray(m["CNa"], float)
    return out


def cp_from_moment(VCG: float, CMA, CNA):
    """Center of pressure from the nose given CMα about the CG: CPN = VCG − CMα/CNα."""
    return VCG - np.asarray(CMA, float) / np.asarray(CNA, float)
