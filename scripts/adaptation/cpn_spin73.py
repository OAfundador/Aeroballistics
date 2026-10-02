"""Center of pressure (CPN) and overturning moment (CMα) of SPIN-73.

Structure: report p. 15 (AMOMSQ, AMOMBT, CPN), with the two text corrections already known
(TRANSCRIPTION_NOTES.md, items E2 and E3): "CYNN" is CVNN and "VBTI" is VBTT = VL/4.7.

    AMOMSQ = CNAB * (C1 + C2*CVNN + C3*CVNN^2 + C4*CVNN^3 + C5*CXLL + C6*CXLL^2
                     + C7*CXLL^3 + C8*CCRT + C9*CCRT^2 + C10*CDMM + C11*CCRT*CVNN + C17*DNX)
    AMOMBT = VBTT * (C12*VBMP + C13*VBX*CVNN + C14*VBX*CXLL + C15*VBX*CCRT
                     + C16*VBX*CCRT*CVNN)
    CPN    = (AMOMSQ + AMOMBT) / CNAT          CMA = (VCG - CPN) * CNAT

CNAB is the normal force of the body without the boattail (B1..B6) and CNAT the total one
(B1..B9); neither is printed separately, so both come from the adapted CNα
(cna_spin73.py).

Validation (test_cpn.py): on the 175 mm M437 the computation reproduces the printed CPN and
CMA within 0.0007 at Mach 0.01, 0.90 and 1.10 -- the three points where all twelve
coefficients are read without doubt. The others depend on the open items listed in
aeroballistics/data/xc_read.py (the faded XC12 line and the missing card of XC15). See
TRANSCRIPTION_NOTES.md, section T6.
"""
import numpy as np

from fit_B import regressors
from aeroballistics.data.xb_read import XB
from aeroballistics.data.xc_read import XC, MACH, CORRECTIONS, DECIDED_M437, RECOVERED

# Record of each XC cell decided by the model, read from the xc_read structures.
_DECIDED = {**{k: "RECOVERED" for k in RECOVERED},
            **{k: "DECIDED_M437" for k in DECIDED_M437},
            **{k: "CORRECTIONS" for k in CORRECTIONS}}


def geometry_terms(VL, VN, VB, OR, DM, M):
    """Variables of pp. 14-15. The sub/supersonic threshold is Mach 0.95 (NOTES, T5)."""
    A_exp, B_exp = (1.5, 1.0) if M >= 0.95 else (1.0, 0.8)
    VNX, DNX = (VN, 0.0) if VN < 3.0 else (3.0, VN - 3.0)
    if VB <= 0.0:
        VBNP = VBMP = VBX = 0.0
    elif VB < 1.0:
        VBNP, VBMP, VBX = VB ** A_exp, VB ** B_exp, VB
    else:
        VBX, VBNP, VBMP = 1.0, VB ** 0.5, VB ** 0.5
    return dict(CVNN=VNX - 2.47, CXLL=VL - VN - VB - 2.15, CCRT=VN ** 2 / OR - 0.48,
                CDMM=DM - 0.17, VBTT=VL / 4.7, VBX=VBX, VBMP=VBMP, DNX=DNX)


def cpn_cma(VL, VN, VB, OR, DM, VCG, j, XB=XB, XC=XC, printed_cna=None):
    """CPN and CMα at grid point j. Returns NaN where DATA is missing.

    `printed_cna` replaces the adapted CNα by the value printed in the table, and CNAB
    becomes CNα_printed − CNBT. That takes the CNα error out of the CPN residual (it reaches
    0.002 and, propagated, is worth up to 0.005 in the CPN) and should be used whenever the
    table's CNA column is transcribed.
    """
    g = geometry_terms(VL, VN, VB, OR, DM, MACH[j])
    x = np.array(regressors(VL, VN, VB, OR, MACH[j]))
    B, C = XB[:, j], XC[:, j]
    CNBT = min(x[6:] @ B[6:], 0.0)             # card C205: a positive CNBT is zeroed
    CNAB = x[:6] @ B[:6]                       # without boattail
    CNAT = CNAB + CNBT                         # total
    if printed_cna is not None:
        CNAT = printed_cna
        CNAB = CNAT - CNBT                     # CNAB = printed total - boattail
    AMOMSQ = CNAB * (C[0] + C[1] * g["CVNN"] + C[2] * g["CVNN"] ** 2 + C[3] * g["CVNN"] ** 3
                     + C[4] * g["CXLL"] + C[5] * g["CXLL"] ** 2 + C[6] * g["CXLL"] ** 3
                     + C[7] * g["CCRT"] + C[8] * g["CCRT"] ** 2 + C[9] * g["CDMM"]
                     + C[10] * g["CCRT"] * g["CVNN"] + C[16] * g["DNX"])
    AMOMBT = g["VBTT"] * (C[11] * g["VBMP"] + C[12] * g["VBX"] * g["CVNN"]
                          + C[13] * g["VBX"] * g["CXLL"] + C[14] * g["VBX"] * g["CCRT"]
                          + C[15] * g["VBX"] * g["CCRT"] * g["CVNN"])
    CPN = (AMOMSQ + AMOMBT) / CNAT
    return CPN, (VCG - CPN) * CNAT


def decided_cells(machs, VB):
    """XC cells decided by the model that enter the CPN at the requested Mach numbers.

    Counts the grid points used in the linear interpolation of each Mach. The boattail block
    (XC12 to XC16) only weighs with VB > 0. Returns [(XC row, Mach index, record in
    xc_read)], in Mach order.
    """
    js = set()
    for m in np.atleast_1d(machs):
        j = min(int(np.searchsorted(MACH, m)), len(MACH) - 1)
        js |= {j} if np.isclose(MACH[j], m) or j == 0 else {j - 1, j}
    return sorted(((l, j, reg) for (l, j), reg in _DECIDED.items()
                   if j in js and (not 12 <= l <= 16 or VB > 0.0)), key=lambda t: (t[1], t[0]))


def implied(coef, VL, VN, VB, OR, DM, VCG, j, printed_CPN):
    """Value of XC[coef] (1-based) that would reproduce the printed CPN, with the others held.

    Used to recover the cells lost in the printout. The result is a value DECIDED BY THE
    MODEL: it stays out of any validation done with the same table.
    """
    g = geometry_terms(VL, VN, VB, OR, DM, MACH[j])
    weight = {12: g["VBTT"] * g["VBMP"], 13: g["VBTT"] * g["VBX"] * g["CVNN"],
              14: g["VBTT"] * g["VBX"] * g["CXLL"], 15: g["VBTT"] * g["VBX"] * g["CCRT"],
              16: g["VBTT"] * g["VBX"] * g["CCRT"] * g["CVNN"]}[coef]
    XC0 = XC.copy()
    XC0[coef - 1, j] = 0.0
    x = np.array(regressors(VL, VN, VB, OR, MACH[j]))
    CNAT = x[:6] @ XB[:6, j] + min(x[6:] @ XB[6:, j], 0.0)
    CPN0, _ = cpn_cma(VL, VN, VB, OR, DM, VCG, j, XC=XC0)
    return (printed_CPN - CPN0) * CNAT / weight
