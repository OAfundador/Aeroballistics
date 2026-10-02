"""
CNα of the reconstructed SPIN-73 against the BRL MR 1833 free flight (7.62 NATO).

Bias per projectile, round by round (M ≥ 1.1), as in `compare_cmq_cp.py`: mean of
(model − experiment), with the model curve at the 17 grid points and linear interpolation in
Mach between them. The MR 1833 CNα is already in the SPIN-73 convention (per radian).

ASSUMPTIONS:
  - the ogive radius of the 7.62 family is uncertain (the figure shows "30R" ≈ 9.74 cal); the
    sensitivity to it is reported;
  - the M-62 has a rounded base, which SPIN-73 does not represent; it enters with an
    approximate VB.

The first comparison (TRANSCRIPTION_NOTES.md, T5) gave +0.28 on the M-80. It predates card
C205 (NOTES, T15), which zeroes the boattail normal force when it comes out positive; the
output repeats the computation without the card to show that the difference comes from it.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                       # noqa: E402,F401  (also makes the output UTF-8)

import recalibrate_mr1833 as r                     # noqa: E402
from fit_B import regressors                       # noqa: E402
from cna_spin73 import cna_j                       # noqa: E402
from compare_cmq_cp import MACH, OR_HYP, PROJECTILES, against_fit, per_round  # noqa: E402
from spin73.data.xb_read import XB                 # noqa: E402


def cna_curve(g, OR=OR_HYP, c205=True):
    """SPIN-73 CNα at the 17 points. `c205=False` turns card C205 off (the boattail part may
    again be positive), as in the reconstruction before it."""
    if c205:
        return np.array([cna_j(g["VL"], g["VN"], g["VB"], OR, j) for j in range(17)])
    return np.array([np.array(regressors(g["VL"], g["VN"], g["VB"], OR, M)) @ XB[:, j]
                     for j, M in enumerate(MACH)])


if __name__ == "__main__":
    rows = r.table()
    ep, npairs = r.pure_error(rows, "CNA", PROJECTILES)

    print("=" * 78)
    print(f"CNα (1/rad) -- reconstructed SPIN-73 against MR 1833, M ≥ {r.MMIN}, OR = {OR_HYP} cal")
    print("=" * 78)
    print(f"{'proj':6s} {'n':>3s} {'SPIN-73 bias':>16s} {'exp spread':>14s} {'pure err/√n':>13s}")
    for p, n, bias, sd in per_round(rows, "CNA", cna_curve):
        mark = "  <-- bias larger than the spread" if abs(bias) > sd else ""
        print(f"{p:6s} {n:3d} {bias:+16.3f} {sd:14.3f} {ep / np.sqrt(n):13.3f}{mark}")
    print(f"\npure error between repeated rounds: {ep:.3f} ({npairs} pairs)")

    print("\nBias with another assumed ogive radius, and without card C205:")
    print(f"  {'':16s}" + "".join(f"{p:>9s}" for p in PROJECTILES))
    for label, curve in (("OR =  8.00 cal", lambda g: cna_curve(g, 8.0)),
                         ("OR = 12.00 cal", lambda g: cna_curve(g, 12.0)),
                         ("without C205", lambda g: cna_curve(g, c205=False))):
        print(f"  {label + ':':16s}" + "".join(f"{v:+9.3f}" for _, _, v, _ in per_round(rows, "CNA", curve)))

    print("\nAgainst the experimental curve fitted by least squares (constant + CXLL, quadratic in")
    print("M − 2, the reduced model of recalibrate_mr1833.py):")
    print(f"{'proj':6s} {'Mach':>5s} {'experiment':>13s} {'SPIN-73':>9s} {'diff':>8s}")
    for p, M, exp, err, mod in against_fit(rows, "CNA", cna_curve, np.array([1.2, 1.5, 2.0, 2.5])):
        print(f"{p:6s} {M:5.2f} {exp:8.3f}±{err:<5.3f} {mod:8.3f} {mod - exp:+8.3f}")
