"""
SPIN-73 -- a didactic adaptation
================================

Source: R. H. Whyte, "SPIN-73, an Updated Version of the SPINNER Computer Program",
Picatinny Arsenal TR 4588, Nov. 1973 (DTIC AD0915628, Distribution A).

The program estimates the aerodynamic coefficients of a spin-stabilized projectile from its
geometry, at 17 Mach numbers, and performs the stability analysis.

Where the Fortran code was read (pp. 84-86 of the listing), the equations follow the CODE,
which is what produced the 1973 tables; where it was not, they follow the report text
(pp. 13-18). Each divergence between the two is marked where it occurs and recorded in
docs/TRANSCRIPTION_NOTES.md. A map of the original program, block by block and in our own
words, is in aeroballistics/program.py (and docs/ORIGINAL_PROGRAM.md).

This is the core: the 1973 program, with no corrections. The interface for simulators
(Aerodynamics, conventions, optional corrections) is in aeroballistics/aero.py.

Usage:
    import aeroballistics as s
    t = s.table(s.M437)                   # dictionary with every column
    print(s.format_table(t))              # table in the report's layout

Input units (those of the original program's card): lengths in calibers, diameter in
inches, Ix/Iy in lb·in², weight in lb, rifling twist in calibers per turn, temperature in °F.
"""

from __future__ import annotations

__all__ = [
    "MACH_GRID", "N_MACH", "J_SUPERSONIC", "G_FT", "K_STAB",
    "Projectile", "DataBlocks", "air_density", "speed_of_sound",
    "cx", "normal_and_moment", "cx2", "magnus", "magnus_polynomial_coefs", "cmq", "clp",
    "coefficients", "stability", "table",
    "AERO_COLUMNS", "STAB_COLUMNS", "format_table", "M437", "read_table", "geometry_warnings",
    "read_card", "save_csv",
]

from dataclasses import dataclass, field
import math

import numpy as np

MACH_GRID = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                      1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
N_MACH = MACH_GRID.size
J_SUPERSONIC = 4         # listing C189: supersonic exponent from the 5th Mach of the grid (0.95)

G_FT = 32.174            # ft/s², weight and inertia conversions
K_STAB = 1352.4          # constant of the gyroscopic factor in the listing (card C241)


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
@dataclass
class Projectile:
    """SPIN-73 input card (Appendix B)."""
    VL: float          # total length, calibers
    VN: float          # ogive length, calibers
    VB: float          # boattail length, calibers
    VCG: float | None = None  # CG from the nose, calibers (required by the computation; if
                              # missing, aeroballistics.mass.complete can estimate it -- optional)
    DIA: float = 0.0   # diameter, in (0 = no stability analysis)
    IX: float = 0.0    # axial moment of inertia, lb·in²
    IY: float = 0.0    # transverse moment of inertia, lb·in²
    WGT: float = 0.0   # weight, lb
    TWIST: float = 0.0 # rifling twist, calibers/turn
    DM: float = 0.12   # meplat diameter, calibers (listing default)
    BD: float = 1.02   # rotating band diameter, calibers (listing default)
    OR: float | None = None   # ogive radius, calibers (default: 2·VN²)
    BOOM: float = 0.0  # "boom length" (CX term)
    TEMP: float = 59.0 # air temperature, °F
    DGUN: float | None = None  # bore diameter, in (default: DIA)
    name: str = ""

    def __post_init__(self):
        if self.OR is None or self.OR <= 0:
            self.OR = 2.0 * self.VN * self.VN
        if self.BD <= 0:
            self.BD = 1.0
        if self.DGUN is None or self.DGUN <= 0:
            self.DGUN = self.DIA


# ---------------------------------------------------------------------------
# Atmosphere (listing, cards 92-93)
# ---------------------------------------------------------------------------
def air_density(temp_f: float) -> float:
    """RHO = .002376 + (-4.784*(T-59) + .01092*(T-59)**2) * 1e-6  [slug/ft³]."""
    dt = temp_f - 59.0
    return 0.002376 + (-4.784 * dt + 0.01092 * dt * dt) * 1.0e-6


def speed_of_sound(temp_f: float) -> float:
    """ASSO = 49.04*SQRT(459.6+TEMP)  [ft/s]."""
    return 49.04 * math.sqrt(459.6 + temp_f)


# ---------------------------------------------------------------------------
# Fitted constants (DATA blocks)
# ---------------------------------------------------------------------------
def _nan(n):
    return field(default_factory=lambda: np.full((n, N_MACH), np.nan))


@dataclass
class DataBlocks:
    """DATA blocks per Mach point, each one with shape (n, 17)."""
    a: np.ndarray = _nan(15)   # XA1..XA15  (CX)
    B: np.ndarray = _nan(10)   # XB1..XB10  (CNα)
    C: np.ndarray = _nan(17)   # XC1..XC17  (normal-force CP)
    D: np.ndarray = _nan(4)    # XD1..XD4   (CX2)
    E: np.ndarray = _nan(5)    # XE1..XE5   (Magnus; XE5 = long body)
    F: np.ndarray = _nan(9)    # XF1..XF9   (Cmq; XF9 = long body)
    G: np.ndarray = _nan(1)    # XG1        (Clp)

    @classmethod
    def from_listing(cls) -> "DataBlocks":
        """The recovered DATA (see aeroballistics/data/ for the status of each block)."""
        from . import data as d
        return cls(a=d.XA.copy(), B=d.XB.copy(), C=d.XC.copy(), D=d.XD.copy(),
                   E=d.XE.copy(), F=d.XF.copy(), G=d.XG.copy())


# ---------------------------------------------------------------------------
# Empirical equations, evaluated at Mach index j
# ---------------------------------------------------------------------------
def cx(p: Projectile, k: DataBlocks, j: int) -> float:
    """Axial force. Code: cards C164-C174 (DXN in three pieces, with A13, A14 and A15,
    which the text does not document). The boattail branch (DXBT) still follows the text:
    the corresponding card, on p. 83, was not transcribed (NOTES, item E6)."""
    a = k.a[:, j]
    CXCL = p.VL - p.VN - p.VB - 1.5
    CBD = p.BD - 1.02
    CDM = (p.DM - 0.12) ** 2
    CRAT = p.VN ** 2 / p.OR - 0.40

    if p.VN <= 3.0:
        VNX, DXN = p.VN, 0.0
    else:
        VNX = 3.0
        if p.VN <= 3.48:
            DXN = (p.VN - 3.0) * a[12]
        elif p.VN <= 3.97:
            DXN = 0.48 * a[12] + (p.VN - 3.48) * a[13]
        else:
            DXN = 0.48 * a[12] + 0.49 * a[13] + (p.VN - 3.97) * a[14]
    if CXCL <= 1.5:
        CXCLL, DXCL = CXCL, 0.0
    else:
        CXCLL, DXCL = 1.5, (CXCL - 1.5) * 0.010
    if p.VB <= 0.2:
        VBX, DXBT = 0.0, 0.0
    elif p.VB < 0.65:
        VBX, DXBT = p.VB - 0.2, 0.0
    else:
        VBX, DXBT = 0.45, (p.VB - 0.65) * a[9]

    c = VNX - 2.5
    return (a[0] + a[1] * c + a[2] * c ** 2 + a[3] * c ** 3
            + a[4] * CXCLL + a[5] * CXCLL ** 2 + a[6] * VBX
            + a[7] * CRAT + a[8] * CRAT ** 2
            + a[10] * CBD + a[11] * CDM
            - (p.BOOM / 1.36) ** 2 * 0.01
            - DXBT - DXN + DXCL)


def normal_and_moment(p: Projectile, k: DataBlocks, j: int) -> dict:
    """CNα, CPN and CMα. Code: cards C175-C212."""
    B, C = k.B[:, j], k.C[:, j]
    VBX, DNX = p.VB, 0.0
    VNX = p.VN
    if p.VN > 3.0:
        VNX, DNX = 3.0, p.VN - 3.0
    if p.VB > 1.0:
        VBX = 1.0
        VBNP = VBMP = p.VB ** 0.5
    elif j >= J_SUPERSONIC:
        VBNP, VBMP = p.VB ** 1.5, p.VB
    else:
        VBNP, VBMP = p.VB, p.VB ** 0.8

    CVNN = VNX - 2.47
    CXLL = p.VL - p.VN - p.VB - 2.15
    CDMM = p.DM - 0.17
    CCRT = p.VN ** 2 / p.OR - 0.48
    VBTT = p.VL / 4.7                       # text: "VBTI"; code: VBTT = CVL/4.7

    CNAB = (B[0] + B[1] * CVNN + B[2] * CXLL + B[3] * CCRT
            + B[4] * CVNN ** 2 + B[5] * CXLL ** 2)
    CNBT = B[6] * VBNP + B[7] * VBX * CVNN + B[8] * VBX * CXLL
    # Card C205, missing from the text: the boattail normal force cannot add (if it comes
    # out positive, it is set to zero). In the scan, the names on this line come out with
    # the B read as A or P. It only acts with a short ogive (CVNN < 0) at supersonic
    # speeds; it is what kept the 5"/38 0.014 off in the CNα from Mach 1.75 to 5 (NOTES, T15).
    if CNBT > 0.0:
        CNBT = 0.0
    CNAT = CNAB + CNBT

    AMOMSQ = CNAB * (C[0] + C[1] * CVNN + C[2] * CVNN ** 2 + C[3] * CVNN ** 3
                     + C[4] * CXLL + C[5] * CXLL ** 2 + C[6] * CXLL ** 3
                     + C[7] * CCRT + C[8] * CCRT ** 2 + C[9] * CDMM
                     + C[10] * CCRT * CVNN + C[16] * DNX)
    AMOMBT = VBTT * (C[11] * VBMP + C[12] * VBX * CVNN + C[13] * VBX * CXLL
                     + C[14] * VBX * CCRT + C[15] * VBX * CCRT * CVNN)
    # Cards C209-C210, missing from the text: if the boattail moment comes out positive,
    # the program discards the whole boattail contribution.
    if AMOMBT > 0.0:
        CNAT, AMOMBT = CNAB, 0.0
    CPN = (AMOMSQ + AMOMBT) / CNAT
    return dict(CNA=CNAT, CPN=CPN, CMA=(p.VCG - CPN) * CNAT)


def cx2(p: Projectile, k: DataBlocks, j: int, CNA: float) -> float:
    """Yaw axial force. Code: card C213."""
    D = k.D[:, j]
    CXCL = p.VL - p.VN - p.VB - 1.5
    CRAT = p.VN ** 2 / p.OR - 0.40
    return D[0] + D[1] * CXCL + D[2] * CRAT + D[3] * p.VB - CNA


def magnus(p: Projectile, k: DataBlocks, j: int) -> dict:
    """Magnus force and moment at 1, 2 and 5 degrees. Code: cards C214-C231.

    The long-body term (XE5, missing from the text) is added to the CPF when VL > 6.
    """
    E = k.E[:, j]
    CVL, CVB = p.VL, p.VB
    CXCL = p.VL - p.VN - p.VB - 1.5
    CVN = p.VN - 2.5
    CYP = E[0] * CVL
    CYPA = CYP - 0.1 * CVB
    DCPF = (p.VL - 6.0) * E[4] if p.VL > 6.0 else 0.0
    out = dict(CYPA=CYPA)
    for tag, e in (("1", E[1]), ("2", E[2]), ("5", E[3])):
        CNPAN = -CYP * (e + 0.55 * CXCL + 0.8 * CVN) + 1.0 * CVL / 4.7 * CVB
        CPF = -CNPAN / CYPA + DCPF
        out["CPF" + tag] = CPF
        out["CNPA" + tag] = (p.VCG - CPF) * CYPA
    return out


def magnus_polynomial_coefs(cnpa1: float, cnpa5: float) -> tuple[float, float]:
    """Printed columns CNPA3 and CNPA5 (the Magnus "polynomial coefficients").

    Code, cards C278-C281. With D = CNPA(5°) − CNPA(1°):
        CNPA5P = ((D + 0.3) − 9·D)/0.0072
        CNPA3  = (D − 0.0001·CNPA5P)/0.01
    The constants are those of a polynomial f(δ) = C1 + C3·δ² + C5·δ⁴ evaluated at δ = 0.1
    and 0.3. But the second point does not use the value at 2° (computed in cards C224-C227
    and never used): it is D plus a constant. So the two printed columns carry ONE single
    degree of freedom and obey CNPA3 + 0.1·CNPA5 = 3.75 for any projectile -- an identity
    the 1973 tables confirm line by line. A defect of the original, kept. In the files,
    "CNPA5P" is this column and "CNPA5" is CNPA*5 (the value at 5°).
    """
    xmag1 = cnpa5 - cnpa1
    xmag2 = cnpa5 - cnpa1 + 0.3
    c5 = (xmag2 - 9.0 * xmag1) / 0.0072
    c3 = (xmag1 - c5 * 0.0001) / 0.01
    return c3, c5


def cmq(p: Projectile, k: DataBlocks, j: int) -> float:
    """Pitch damping. Code: cards C232-C238 (F9, missing from the text)."""
    F = k.F[:, j]
    CLL = p.VL - 5.0
    CCG = p.VCG - 3.0
    CVB = p.VB
    CKM = (F[0] + F[1] * CLL + F[2] * CLL ** 2 + F[3] * CCG
           + F[4] * CCG * CLL + F[5] * CCG * CLL ** 2 + F[6] * CCG * CVB + F[7] * CVB)
    DCMQ = (p.VL - 6.0) * F[8] if p.VL > 6.0 else 0.0
    return -5.093 * CKM - DCMQ


def clp(p: Projectile, k: DataBlocks, j: int) -> float:
    """Roll damping. Code: card C239 (SFNG = 5.51, the VL of the M437)."""
    return k.G[0, j] * (p.VL / 5.51)


def coefficients(p: Projectile, k: DataBlocks) -> dict:
    """Every aerodynamic column at the 17 Mach points (NaN where DATA is missing)."""
    if p.VCG is None:
        raise ValueError("VCG (CG from the nose, calibers) not given. Give it, or estimate "
                         "it with aeroballistics.mass.complete(p) (optional addition; "
                         "--estimate-mass on the command line).")
    names = ("CX", "CX2", "CNA", "CMA", "CPN", "CYPA", "CNPA", "CPF1", "CPF2", "CNPA2",
             "CPF5", "CNPA5", "CNPA3", "CNPA5P", "CMQ", "CLP")
    cols = {n: np.empty(N_MACH) for n in names}
    for j in range(N_MACH):
        nm = normal_and_moment(p, k, j)
        mg = magnus(p, k, j)
        cols["CX"][j] = cx(p, k, j)
        cols["CNA"][j], cols["CMA"][j], cols["CPN"][j] = nm["CNA"], nm["CMA"], nm["CPN"]
        cols["CX2"][j] = cx2(p, k, j, nm["CNA"])
        cols["CYPA"][j] = mg["CYPA"]
        cols["CNPA"][j], cols["CPF1"][j] = mg["CNPA1"], mg["CPF1"]
        cols["CNPA2"][j], cols["CPF2"][j] = mg["CNPA2"], mg["CPF2"]
        cols["CNPA5"][j], cols["CPF5"][j] = mg["CNPA5"], mg["CPF5"]
        cols["CNPA3"][j], cols["CNPA5P"][j] = magnus_polynomial_coefs(mg["CNPA1"], mg["CNPA5"])
        cols["CMQ"][j] = cmq(p, k, j)
        cols["CLP"][j] = clp(p, k, j)
    cols["MACH"] = MACH_GRID.copy()
    return cols


# ---------------------------------------------------------------------------
# Stability analysis (pp. 17-18; code from card C240 on)
# ---------------------------------------------------------------------------
def stability(p: Projectile, MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP,
              rho: float | None = None) -> dict:
    """Columns of the "STABILITY ANALYSIS" section, from the coefficients (of any source).

    Output units: SPIN, W1, W2 in rad/s; L1, L2 in 1/ft.
    """
    MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP = map(
        np.asarray, (MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP))
    rho = air_density(p.TEMP) if rho is None else rho
    d = p.DIA / 12.0
    m = p.WGT / G_FT
    Ix = p.IX / (G_FT * 144.0)
    Iy = p.IY / (G_FT * 144.0)
    A = math.pi * d * d / 4.0

    V = MACH * speed_of_sound(p.TEMP)
    twist_in = p.TWIST * p.DGUN                            # one turn, in inches
    P = V * 2.0 * math.pi / (twist_in / 12.0)              # rad/s

    # Card C241: with Ix, Iy in lb·in² and lengths in inches, the code computes
    #   s_g = 1352.4·Ix²/(ρ·Iy·CMα·twist²·d³).
    # The physical formula with g = 32.174 would give 1349.8 instead of 1352.4: the
    # difference, +0.19 %, is the "s_g bias" that stayed open until the code was read.
    sg = K_STAB * p.IX ** 2 / (rho * p.IY * CMA * twist_in ** 2 * p.DIA ** 3)

    k1 = m * d * d / Ix        # the report's k1^-2
    k2 = m * d * d / Iy        # the report's k2^-2

    def s_d(cnpa):
        return (2.0 * (CNA - CX + k1 / 2.0 * cnpa)
                / (CNA - CX - k2 / 2.0 * CMQ + k1 / 2.0 * CLP))

    sd, sd5 = s_d(CNPA), s_d(CNPA5)
    recip = 1.0 / (sd * (2.0 - sd))
    recip5 = 1.0 / (sd5 * (2.0 - sd5))

    sig = np.sqrt(1.0 - 1.0 / sg)
    W1 = P * Ix / (2.0 * Iy) * (1.0 + sig)
    W2 = P * Ix / (2.0 * Iy) * (1.0 - sig)

    K = rho * A / (4.0 * m)

    def lam(sign, cnpa):
        # The text (p. 18) prints -CN*(1 +- 1/sigma); the tables are only reproduced
        # with -CN*(1 -+ 1/sigma). TRANSCRIPTION_NOTES.md, item E1.
        return K * (-CNA * (1.0 - sign / sig)
                    + k2 / 2.0 * (1.0 + sign / sig) * CMQ
                    + sign * k1 / sig * cnpa)

    # Card C266: nutation period divided by 20 (suggested integration step).
    DELT = 6.28 / (W1 * 20.0)
    # Card C256: DISP = (CNα − CX)·Iy·(ω₁ − ω₂)·3.635/(CMα·weight·diameter·V), with Iy in
    # lb·in². The report's reference 71 (Whyte 1970), which would explain the quantity, is
    # not available; the formula is the code's.
    DISP = (CNA - CX) * p.IY * (W1 - W2) * 3.635 / (CMA * p.WGT * p.DIA * V)

    out = dict(MACH=MACH, GYRO=sg, SBAR=sd, RECIP=recip, SBAR5=sd5,
               RECIP5=recip5, SPIN=P, W1=W1, W2=W2,
               L1=lam(+1, CNPA), L2=lam(-1, CNPA),
               L15=lam(+1, CNPA5), L25=lam(-1, CNPA5), DELT=DELT, DISP=DISP)
    # Cards C249 and C287: with s_g < 1.001 the program only prints MACH and STAB (the
    # projectile is gyroscopically unstable and the rest of the analysis makes no sense).
    unstable = np.asarray(sg) < 1.001
    for name in out:
        if name not in ("MACH", "GYRO"):
            out[name] = np.where(unstable, np.nan, out[name])
    return out


# ---------------------------------------------------------------------------
# Complete program: geometry -> table
# ---------------------------------------------------------------------------
def table(p: Projectile, k: DataBlocks | None = None) -> dict:
    """Every column SPIN-73 prints, for one projectile.

    Columns whose DATA has not been recovered yet come out NaN (see aeroballistics/data/);
    the stability analysis depends on CX and comes out NaN while XA is not read.
    """
    k = DataBlocks.from_listing() if k is None else k
    t = coefficients(p, k)
    if p.DIA > 0 and p.IX > 0 and p.IY > 0 and p.WGT > 0 and p.TWIST > 0:
        with np.errstate(invalid="ignore", divide="ignore"):
            t.update(stability(p, t["MACH"], t["CX"], t["CNA"], t["CMA"],
                               t["CNPA"], t["CNPA5"], t["CMQ"], t["CLP"]))
    return t


# Order and names of the columns printed by the program (cards C282 and C290).
AERO_COLUMNS = [("CX", 3), ("CX2", 3), ("CNA", 3), ("CMA", 3), ("CPN", 3), ("CYPA", 3),
                ("CNPA", 3), ("CNPA3", 3), ("CNPA5P", 3), ("CPF1", 3), ("CPF5", 3),
                ("CNPA5", 3), ("CMQ", 3), ("CLP", 3)]
STAB_COLUMNS = [("GYRO", 3), ("SBAR", 3), ("RECIP", 3), ("SBAR5", 3), ("RECIP5", 3),
                ("SPIN", 1), ("W1", 2), ("W2", 2), ("L1", 6), ("L2", 6), ("L15", 6), ("L25", 6),
                ("DELT", 4), ("DISP", 3)]


def format_table(t: dict, title: str = "") -> str:
    """Table as text, in the report's arrangement (NaN columns show as '--')."""
    def block(columns, header):
        lines = [header, "MACH  " + "".join(f"{n:>10s}" for n, _ in columns)]
        for i, M in enumerate(t["MACH"]):
            fields = []
            for n, places in columns:
                v = t.get(n, np.full(N_MACH, np.nan))[i]
                fields.append(f"{v:10.{places}f}" if np.isfinite(v) else f"{'--':>10s}")
            lines.append(f"{M:5.3f}" + "".join(fields))
        return "\n".join(lines)
    parts = [title] if title else []
    parts.append(block(AERO_COLUMNS, "AERODYNAMIC COEFFICIENTS"))
    if "GYRO" in t:
        parts.append(block(STAB_COLUMNS, "STABILITY ANALYSIS"))
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Validation case: 175 mm M437 (Table 14, p. 65)
# ---------------------------------------------------------------------------
M437 = Projectile(VL=5.510, VN=2.910, VB=1.000, VCG=3.500, DM=0.079, BD=1.050,
                  OR=25.0, BOOM=0.0, DIA=6.885, IX=954.1, IY=10850.0,
                  WGT=148.0, TWIST=20.0, TEMP=59.0, name="175MM M437")


def read_table(path: str) -> dict:
    """Reads a transcribed table (CSV with '#' comment lines)."""
    import csv
    with open(path, newline="", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    rd = csv.DictReader(lines)
    rows = list(rd)
    return {c: np.array([float(r[c]) for r in rows]) for c in rd.fieldnames}


# ---------------------------------------------------------------------------
# Warnings: where the adaptation is least reliable for a given geometry
# ---------------------------------------------------------------------------
def geometry_warnings(p: Projectile) -> list[str]:
    """Limitations of the adaptation that affect THIS projectile (docs/TRANSCRIPTION_NOTES.md)."""
    a = [
        "CPN and CMα from Mach 1.2 to 5: card XC15 was not printed in the report and was "
        "recovered from the tables (M437, 5\"/38 and XM380E5 agree, with residuals up to "
        "0.0025 cal; T11, T13, T15). The 155 mm M101 is still 0.007 cal off at Mach 1.2 (T14).",
        "CPN and CMα at Mach 0.6: a residual of 0.002 to 0.004 cal is still open (T13).",
    ]
    if p.VN > 3.0:
        a.append("Ogive > 3 cal: CX uses XA13..XA15 and CPN uses XC17, checked against a single "
                 "table (175 mm SRC, 5.5 cal ogive; T14).")
    if p.VL > 6.0:
        a.append("Body > 6 cal: long-body terms XE5 (Magnus; the first 12 values come from "
                 "the tables) and XF9 (Cmq; validated only on the 20 mm 9 cal).")
    if p.VB > 1.0:
        a.append("Boattail > 1 cal: code branch (VB**0.5) with no validation table at all.")
    if 0.65 <= p.VB:
        a.append("Boattail >= 0.65 cal: the DXBT term of CX follows the report text; the code "
                 "card (p. 83) has not been transcribed yet (E6).")
    if p.DIA > 0:
        a.append("s_g, ω, λ, DELT and DISP depend on CMα and inherit its uncertainties.")
    return a


def read_card(path: str) -> Projectile:
    """Reads a projectile from a text file with 'KEY = value' lines (# comments).

    Keys: those of the input card (VL, VN, VB, VCG, DIA, IX, IY, WGT, TWIST, DM, BD,
    OR, BOOM, TEMP, DGUN) and 'name'.
    """
    fields = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            key, value = (x.strip() for x in line.split("=", 1))
            fields[key] = value if key == "name" else float(value)
    return Projectile(**fields)


def save_csv(t: dict, path: str) -> None:
    """Every column, one row per Mach."""
    import csv
    cols = ["MACH"] + [n for n, _ in AERO_COLUMNS] + [n for n, _ in STAB_COLUMNS if n in t]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i in range(N_MACH):
            w.writerow([f"{t[c][i]:.6g}" if np.isfinite(t[c][i]) else "" for c in cols])
