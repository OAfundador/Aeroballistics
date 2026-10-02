"""
CMα of the adapted SPIN-73 against Hitchcock's caliber 0.30 (BRL 620, printed p. 20).

Measured: CMα = (8/π)·K_M (conversions.py; the conversion was verified on the Ball M2, test_cal030.py).
Model: CMα = (VCG − CPN)·CNα of the adaptation (cpn_spin73.py), at the 17 grid points and
interpolated linearly in Mach. Mach: the one printed in the table when it exists; else V / A_SOUND.

ASSUMPTIONS:
  - DM (meplat) is not dimensioned in the sketches: DM = 0.12, the convention of the
    small-arms sources (../correction/flight_data.py); the output repeats the computation
    with 0.05 and 0.20;
  - A.P. M2: the 0.31 cal taper at the base is treated as a flat base (data_cal030.py);
    the output repeats the computation with VB = 0.31;
  - Tracer M1: the K_M is "apparent" (the report's note), computed with the mean inertia with
    and without the tracer composition; the mean CG is used (PHYSICAL["Tracer M1 mean"]), and
    the output repeats the computation with the CG of the full projectile;
  - Frangible M22: contour of the Ball M2, per the note on p. 18 (the sketch of the T44, p. 19,
    conflicts with that note and is still pending).
Left out: the Night Tracer M25 (no CG or inertia) and the A.P.I. T15 (no stability data).

CELLS DECIDED BY THE MODEL. Above Mach 1.1, the CPN uses the XC15 decided by the 1973 tables
(card not printed), which only weighs with a boattail, and, between Mach 2.0 and 3.0, the XC1
of Mach 2.5 (read 1.90, decided 1.99), which weighs on all of them. No cell came from
Hitchcock, so the comparison is not circular, but it depends on them: the output lists the
ones that enter each row and repeats the computation without the XC CORRECTIONS (XC15 has no
read value to replace it).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                       # noqa: E402,F401  (also makes the output UTF-8)

import conversions as cv                           # noqa: E402
from cpn_spin73 import cpn_cma, decided_cells      # noqa: E402
from data_cal030 import A_SOUND, GEOMETRY, PHYSICAL, STABILITY  # noqa: E402
from aeroballistics.data.xc_read import MACH, XC, XC_READ  # noqa: E402

DM = 0.12
CONTOUR = {"Frangible M22": "Ball M2"}              # note on p. 18
PHYSICS = {"Tracer M1": "Tracer M1 mean"}           # the inertia (and CG) of the apparent K_M
# Reading of the row by the K_M x S x inertias identity (test_cal030.py; RECALIBRATION_MR1833.md)
READING = {"Ball M1": "inconsistent in the source", "Ball M2": "verified",
           "A.P. M2": "temperature uncertainty", "Tracer M1": "verified (apparent K_M)",
           "Frangible M22": "verified"}


def rows():
    """Stability series that have geometry and CG: (name, Mach, geometry, VCG, measured CMα)."""
    out = []
    for name, _rep, _n, V, M, _S, K_M in STABILITY:
        g = GEOMETRY.get(CONTOUR.get(name, name))
        f = PHYSICAL.get(PHYSICS.get(name, name))
        if g is None or f is None:
            continue
        out.append((name, M or V / A_SOUND, g, g["VL"] - f["g"], cv.cma_from_km(K_M)))
    return out


def model(g, VCG, M, DM=DM, VB=None, XC=XC):
    """SPIN-73 CPN and CMα at Mach M, interpolated between the grid points."""
    VB = g["VB"] if VB is None else VB
    c = np.array([cpn_cma(g["VL"], g["VN"], VB, g["OR"], DM, VCG, j, XC=XC) for j in range(17)])
    return float(np.interp(M, MACH, c[:, 0])), float(np.interp(M, MACH, c[:, 1]))


if __name__ == "__main__":
    L = rows()
    print("=" * 78)
    print(f"CMα -- adapted SPIN-73 against Hitchcock's caliber 0.30 (DM = {DM} assumed)")
    print("=" * 78)
    print(f"{'projectile':14s} {'Mach':>6s} {'VCG':>6s} {'CPN mod':>8s} {'CMα mod':>8s} {'CMα meas':>8s}"
          f" {'mod/meas':>8s}  reading")
    for name, M, g, vcg, meas in L:
        cpn, cma = model(g, vcg, M)
        print(f"{name:14s} {M:6.3f} {vcg:6.3f} {cpn:8.3f} {cma:8.3f} {meas:8.3f} {cma / meas:8.3f}"
              f"  {READING[name]}")

    print("\nXC cells decided by the model (xc_read) that enter each row:")
    for name, M, g, _, _ in L:
        cel = [f"XC{l} at {MACH[j]:.2f} ({reg})" for l, j, reg in decided_cells(M, g["VB"])]
        print(f"  {name:14s} {M:5.3f}: " + ("\n" + " " * 24).join(cel or ["none"]))

    print("\nSensitivity: mod/meas with another assumed DM and without the XC CORRECTIONS:")
    print(f"  {'projectile':14s} {'Mach':>6s} {'DM 0.05':>8s} {'DM 0.20':>8s} {'XC read':>8s}")
    for name, M, g, vcg, meas in L:
        r = [model(g, vcg, M, DM=dm)[1] / meas for dm in (0.05, 0.20)]
        r.append(model(g, vcg, M, XC=XC_READ)[1] / meas)
        print(f"  {name:14s} {M:6.3f}" + "".join(f"{v:8.3f}" for v in r))

    print("\nGeometry variants:")
    for name, M, g, vcg, meas in L:
        if name == "A.P. M2":
            cma = model(g, vcg, M, VB=0.31)[1]
            print(f"  A.P. M2, base taper as a boattail (VB = 0.31): CMα = {cma:.3f}, "
                  f"mod/meas = {cma / meas:.3f}")
        if name == "Tracer M1":
            vcg_full = g["VL"] - PHYSICAL["Tracer M1"]["g"]
            cma = model(g, vcg_full, M)[1]
            print(f"  Tracer M1, CG of the full projectile (VCG = {vcg_full:.3f}): CMα = {cma:.3f}, "
                  f"mod/meas = {cma / meas:.3f}")
