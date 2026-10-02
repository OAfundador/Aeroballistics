"""Reconstructed SPIN-73 Magnus (E1, E2, E4) against the BRL MR 1833 experiment.

Normalization conversion: SPIN-73 uses p*d/(2V); MR 1833 uses p*d/V.
So Cnpa(SPIN) = 2 * Cmpa(MR 1833). Same sign convention assumed (BRL/Murphy).
Yaw dependence: SPIN-73 gives Cnpa at 1, 2 and 5 degrees. E3 (2 degrees) has not been
identified yet, so we interpolate linearly in alpha between 1 and 5 degrees (ASSUMPTION).
Between points of the Mach grid, E is interpolated linearly (ASSUMPTION).
"""
import csv, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths  # noqa: E402
import magnus_clp as mc

read_csv = lambda f: list(csv.DictReader(l for l in open(paths.FREE_FLIGHT / f, encoding="utf-8")
                                         if not l.startswith("#")))
GEO = {r["projectile"]: {k: float(r[k]) for k in ("VL", "VN", "VB", "VCG")} for r in read_csv("mr1833_geometry.csv")}
EXP = read_csv("mr1833_table2.csv")


def cnpa_spin(g, mach, alpha_deg):
    e1 = np.interp(mach, mc.MACH, mc.E1)
    e2 = np.interp(mach, mc.MACH, mc.E2)
    e4 = np.interp(mach, mc.MACH, mc.E4)
    VL, VB, VN, VCG = g["VL"], g["VB"], g["VN"], g["VCG"]
    CXCL, CVN = VL - VN - VB - 1.5, VN - 2.5
    cypa = e1 * VL - 0.1 * VB
    def cnpa(e):
        cnpan = -e1 * VL * (e + 0.55 * CXCL + 0.8 * CVN) + VB * VL / 4.7
        return (VCG + cnpan / cypa) * cypa           # (VCG - CPF)*CYPA, CPF = -CNPAN/CYPA
    w = (np.clip(alpha_deg, 1, 5) - 1) / 4
    return (1 - w) * cnpa(e2) + w * cnpa(e4)


if __name__ == "__main__":
    print(f"{'proj':5s} {'Mach':>6s} {'yaw':>5s} {'exp*2':>7s} {'SPIN':>7s} {'diff':>7s}")
    res = {}
    for r in EXP:
        if not r["CMPA"]:
            continue
        M, yaw, exp2 = float(r["MACH"]), float(r["YAW_RMS_DEG"]), 2 * float(r["CMPA"])
        if M < 0.9:     # the SPIN-73 grid starts at 0.01/0.6; the M-80 subsonic data are very scattered
            pass
        p = cnpa_spin(GEO[r["projectile"]], M, yaw)
        res.setdefault(r["projectile"], []).append((M, exp2, p))
        print(f"{r['projectile']:5s} {M:6.3f} {yaw:5.1f} {exp2:7.2f} {p:7.2f} {p - exp2:7.2f}")
    print("\nSummary (supersonic, M > 1.2):")
    for k, v in res.items():
        v = np.array([x for x in v if x[0] > 1.2])
        print(f"  {k}: mean exp*2 {v[:,1].mean():+.2f}   mean SPIN {v[:,2].mean():+.2f}   "
              f"bias {np.mean(v[:,2]-v[:,1]):+.2f}   exp spread {v[:,1].std():.2f}")
