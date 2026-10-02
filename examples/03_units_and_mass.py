"""Input in metric units and estimate of CG and inertias (two optional additions).

    python examples/03_units_and_mass.py

The SPIN-73 card asks for calibers, inches, pounds and lb·in², and takes the CG and the
inertias as input. Here the 5.56 mm M855 comes in mm and grams, with no CG or inertias
(examples/inputs/m855_metric.txt), and ``spin73.mass`` estimates them from the geometry and the
mass. The M855 has measured CG and inertias (McCoy, BRL-MR-3476, 1985, Table 1), so one can see
how much the estimate misses and how much that changes the gyroscopic stability factor.

The estimate changes INPUTS, not the model; none of it is applied unless asked for.
"""
from __future__ import annotations

from _bootstrap import INPUTS, prepare

prepare()

import spin73  # noqa: E402
from spin73 import mass, units  # noqa: E402

# Measured (McCoy 1985, Table 1): CG from the BASE in calibers; inertias in g·cm².
MEASURED = dict(CG_BASE=1.54, IX_GCM2=0.1426, IY_GCM2=1.150)


def main() -> None:
    p, options = units.read_input(str(INPUTS / "m855_metric.txt"))
    print(f"{p.name}: DIA {p.DIA:.4f} in, WGT {p.WGT:.5f} lb, TWIST {p.TWIST:.2f} cal/turn")
    print("missing from the card:", ", ".join(mass.missing(p)))
    print("estimate options in the file:", options)

    bt_angle = options.get("BT_ANGLE")                  # boattail angle, degrees
    print(f"\n{'method':8s} {'CG base':>10s} {'Ix g·cm²':>9s} {'Iy g·cm²':>9s}   estimated/measured")
    print(f"{'measured':8s} {MEASURED['CG_BASE']:10.3f} {MEASURED['IX_GCM2']:9.4f} {MEASURED['IY_GCM2']:9.3f}")
    for method in ("solid", "bullet"):
        pm = mass.estimate(p, method, bt_angle=bt_angle)
        print(f"{method:8s} {pm.cg_base:10.3f} {pm.ix_gcm2:9.4f} {pm.iy_gcm2:9.3f}   "
              f"CG {pm.cg_base - MEASURED['CG_BASE']:+.3f} cal, Ix ×{pm.ix_gcm2 / MEASURED['IX_GCM2']:.3f}, "
              f"Iy ×{pm.iy_gcm2 / MEASURED['IY_GCM2']:.3f}")
    print("\n" + str(mass.estimate(p, "solid", bt_angle=bt_angle)))

    # The card completed by the estimate and the card with the measured values.
    estimated = mass.complete(p, "solid", bt_angle=bt_angle)
    measured = units.projectile(name="M855 (measured)", VL=p.VL, VN=p.VN, VB=p.VB, OR=p.OR, DM=p.DM,
                                BD=p.BD, D_MM=5.69, MASS_G=4.05, TWIST_IN=7, TEMP_C=15, **MEASURED)
    t_est, t_meas = spin73.table(estimated), spin73.table(measured)
    print("\nGyroscopic stability factor s_g (GYRO):")
    print(f"  {'Mach':>5s} {'measured':>8s} {'estimated':>9s}")
    for j, M in enumerate(t_meas["MACH"]):
        if M in (0.6, 1.0, 1.5, 2.0, 2.5, 3.0):
            print(f"  {M:5.2f} {t_meas['GYRO'][j]:8.3f} {t_est['GYRO'][j]:9.3f}")


if __name__ == "__main__":
    main()
