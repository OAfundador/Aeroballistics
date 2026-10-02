"""Coefficients for a 6DOF simulator: the seven of McCoy's formulation, at any Mach.

    python examples/02_6dof_simulator.py
    python examples/02_6dof_simulator.py --csv       # also writes output/examples/m855_seven.csv

``spin73.Aerodynamics`` computes the aerodynamics once, in the constructor, on the program's
17-Mach grid; each call only interpolates in Mach, so it can sit inside the integration loop.

With ``convention="modern"`` the rates are nondimensionalized by pd/V and qd/V, as in McCoy
(*Modern Exterior Ballistics*, ch. 2): Cmq, Clp and both Magnus coefficients are HALF of the
report's, which uses pd/2V. The seven coefficients McCoy's equations read come out like this:

    CD   = CD0 + CDδ²·sin²α     drag, wind axes
    CLA  = CLα = CNα − CX0      lift
    CYP  = CNpα                 Magnus force
    CNP  = Cmpα(α)              Magnus moment (secant: SPIN-73's 1° and 5°, interpolated in
                                sin²α between them, constant outside)
    CLP  = Clp                  roll damping
    CMA  = CMα                  overturning moment, about the CG (positive overturns)
    CMQ  = Cmq + Cmα̇            pitch damping

Signs: CMα > 0 overturns, as in McCoy. The Magnus sign changes from one source to another;
check your simulator's definition (src/spin73/conventions.py, item 7).

The flat --csv table (Mach and the seven columns) has no α dependence: in it, CD is CD0 and CNP
is the slope at 1°. Where the simulator accepts functions of (Mach, α), use ``cd`` and ``cnp``.
"""
from __future__ import annotations

import argparse
import csv

import numpy as np

from _bootstrap import OUTPUT, prepare

prepare()

import spin73  # noqa: E402

# 5.56 mm M855 (McCoy, BRL-MR-3476, 1985, Fig. 3 and Table 1): geometry in calibers, CG at
# 1.54 cal from the base, diameter 5.69 mm. Meplat not dimensioned: the program default (0.12) stays.
M855 = spin73.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9, BD=1.00,
                         DIA=5.69 / 25.4, name="5.56 mm M855")

SEVEN = ("CD", "CLA", "CYP", "CNP", "CLP", "CMA", "CMQ")


def seven(aero: spin73.Aerodynamics, mach, alpha_rad=0.0) -> dict:
    """The seven coefficients at the requested Mach number(s), at the total angle of attack α (radians)."""
    c = aero(mach)
    return {
        "CD": c.CD0 + c.CDd2 * np.sin(alpha_rad) ** 2,
        "CLA": c.CLa,
        "CYP": c.CNpa,
        "CNP": aero.magnus_moment(mach, alpha_rad),
        "CLP": c.Clp,
        "CMA": c.Cma,
        "CMQ": c.Cmq_Cmad,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", action="store_true",
                    help="writes the flat table (Mach + seven columns) to output/examples/m855_seven.csv")
    args = ap.parse_args()

    aero = spin73.Aerodynamics(M855, convention="modern")    # the canonical one, in McCoy's convention only
    print(aero.describe())
    print("available coefficients:", ", ".join(aero.names))

    # In an integrator, at each step: M = V/a and α = total angle of attack.
    alpha = np.radians(2.0)
    print(f"\nThe seven at α = {np.degrees(alpha):.0f}°:")
    print("  Mach " + "".join(f"{n:>9s}" for n in SEVEN))
    for M in (0.6, 0.9, 1.1, 1.5, 2.0, 2.5, 3.0):
        k = seven(aero, M, alpha)
        print(f"  {M:4.2f} " + "".join(f"{k[n]:9.4f}" for n in SEVEN))

    # Vectorized: arrays of Mach (and of α) at once.
    machs = np.linspace(0.7, 2.8, 4)
    print("\nvectorized CMA at", np.round(machs, 2), "->", np.round(aero.coefficient("Cma", machs), 4))

    # The two that depend on α, as functions of (Mach, α), for simulators that accept them.
    def cd(M, a):
        return aero.coefficient("CD0", M) + aero.coefficient("CDd2", M) * np.sin(a) ** 2

    def cnp(M, a):
        return aero.magnus_moment(M, a)

    print(f"\nMach 2: CD at 0° = {cd(2.0, 0.0):.4f}, at 5° = {cd(2.0, np.radians(5)):.4f}; "
          f"CNP at 1° = {cnp(2.0, np.radians(1)):.4f}, at 5° = {cnp(2.0, np.radians(5)):.4f}")

    if args.csv:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT / "m855_seven.csv"
        grid = spin73.MACH_GRID
        k = seven(aero, grid, 0.0)
        k["CNP"] = aero.coefficient("Cmpa", grid)               # slope at 1°
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Mach", *SEVEN])
            for j, M in enumerate(grid):
                w.writerow([f"{M:g}", *(f"{k[n][j]:.6g}" for n in SEVEN)])
        print("\nwritten:", path)


if __name__ == "__main__":
    main()
