"""Coefficients for a 6DOF simulator: the seven of McCoy's formulation, at any Mach and α.

    python examples/02_6dof_simulator.py
    python examples/02_6dof_simulator.py --input examples/inputs/5in38_navy.txt
    python examples/02_6dof_simulator.py --npz       # writes output/examples/<name>_seven.npz
    python examples/02_6dof_simulator.py --csv       # writes output/examples/<name>_seven.csv

``aeroballistics.Aerodynamics`` computes the aerodynamics once, in the constructor, on the
program's 17-Mach grid; each call only interpolates in Mach, so it can sit inside the
integration loop.

The conversion to the seven belongs to this example, not to the library: each simulator writes
its equations in its own way, and the conversion has to be checked against them. This one is
for McCoy's vector form (*Modern Exterior Ballistics*, ch. 2), in which each force and each
moment is a coefficient times a geometric vector:

    term                 vector in the equations   magnitude     the coefficient must be
    drag                 V                         V             the whole C_D(M, α)
    lift                 V² x − V (V·x) V/V        V² sin α      C_L / sin α
    overturning          V × x                     V sin α       per sin α
    Magnus force         V × x                     V sin α       per sin α
    Magnus moment        V − (V·x) x               V sin α       per sin α (the secant)

With ``convention="modern"`` (pd/V and qd/V: Cmq, Clp and both Magnus coefficients are HALF of
the report's) and the axial force CX = CX0 + CX2·sin²α positive rearward, CX2 = CDδ² − CNα:

    CD   = CX·cos α + CNα·sin²α     D = A cos α + N sin α (exact projection)
    CLA  = CNα·cos α − CX           L/sin α, with L = N cos α − A sin α
    CYP  = CNpα                     Magnus force
    CNP  = Cmpα(α)                  Magnus moment: secant (SPIN-73's 1° and 5°, interpolated in
                                    sin²α between them, constant outside), even in α
    CLP  = Clp                      roll damping
    CMA  = CMα                      overturning moment, about the CG (positive overturns)
    CMQ  = Cmq + Cmα̇                pitch damping

For small α, CD → CD0 + (CDδ² − CX0/2)·sin²α and CLA → CLα = CNα − CX0; the difference from the
small-yaw form grows with α (at 8° and Mach 2, 1 % in CD and 4 % in CLA for the 5"/38).

Signs: CMα > 0 overturns, as in McCoy. The Magnus force keeps the SPIN-73 sign (CNpα < 0): in
McCoy's equations it acts along V × x, and so it points along x × V; checked by flying the
155 mm M107 in an independent code with another formulation (RigidFlightLab), where the wrong
sign shifts the time of flight by 0.5 %. If your simulator puts the force along x × V, use
|CNpα| (src/aeroballistics/conventions.py, item 7).

Outputs:

- ``--npz``: the grid a simulator reads directly — ``mach_grid`` (100 Mach numbers from 0.01
  to 5), ``alpha_grid`` (101 angles from −10° to +10°, in radians), CD, CLA and CNP over
  (Mach × α) and the other four over Mach only, with the column names above. Above 10° the
  small-yaw formulation stops being valid.
- ``--csv``: the flat table (Mach and the seven columns) at the 17 Mach numbers, without the α
  dependence: CD is CD0 and CNP is the slope at 1°. It is for checking; for flying, prefer the
  grid.
"""
from __future__ import annotations

import argparse
import csv

import numpy as np

from _bootstrap import OUTPUT, prepare

prepare()

import aeroballistics  # noqa: E402
from aeroballistics import units  # noqa: E402

# 5.56 mm M855 (McCoy, BRL-MR-3476, 1985, Fig. 3 and Table 1): geometry in calibers, CG at
# 1.54 cal from the base, diameter 5.69 mm. Meplat not dimensioned: the program default (0.12) stays.
M855 = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9, BD=1.00,
                                 DIA=5.69 / 25.4, name="5.56 mm M855")

SEVEN = ("CD", "CLA", "CYP", "CNP", "CLP", "CMA", "CMQ")
DEPENDS_ON_ALPHA = ("CD", "CLA", "CNP")

#: The --npz grid.
GRID_MACH = np.linspace(0.01, 5.0, 100)
GRID_ALPHA = np.radians(np.linspace(-10.0, 10.0, 101))


def seven(aero: aeroballistics.Aerodynamics, mach, alpha_rad=0.0) -> dict:
    """The seven coefficients at the requested Mach number(s), at the total angle of attack α (radians).

    ``aero`` in the modern convention. Mach and α may be arrays of the same shape (or broadcastable).
    """
    if aero.convention != "modern":
        raise ValueError("seven() reads the modern convention: Aerodynamics(p, convention='modern')")
    c = aero(mach)
    s = np.sin(alpha_rad)
    cna = c.CNa
    axial = c.CD0 + (c.CDd2 - cna) * s * s          # CX0 + CX2·sin²α, positive rearward
    return {
        "CD": axial * np.cos(alpha_rad) + cna * s * s,
        "CLA": cna * np.cos(alpha_rad) - axial,
        "CYP": c.CNpa,
        "CNP": aero.magnus_moment(mach, alpha_rad),
        "CLP": c.Clp,
        "CMA": c.Cma,
        "CMQ": c.Cmq_Cmad,
    }


def grid(aero: aeroballistics.Aerodynamics, mach=GRID_MACH, alpha=GRID_ALPHA) -> dict:
    """The seven on a grid: the three that depend on α over (Mach × α), the others over Mach only."""
    M, A = np.meshgrid(mach, alpha, indexing="ij")
    k2 = seven(aero, M, A)
    k1 = seven(aero, mach, 0.0)
    out = {"mach_grid": np.asarray(mach, float), "alpha_grid": np.asarray(alpha, float)}
    for n in SEVEN:
        out[n] = np.asarray(k2[n] if n in DEPENDS_ON_ALPHA else k1[n], float)
    return out


def _file_name(p) -> str:
    name = (p.name or "projectile").lower()
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", help="'KEY = value' card (default: this example's 5.56 mm M855)")
    ap.add_argument("--npz", action="store_true", help="writes the (Mach × α) grid to output/examples/")
    ap.add_argument("--csv", action="store_true", help="writes the flat table (Mach + seven columns)")
    args = ap.parse_args(argv)

    p = units.read_input(args.input)[0] if args.input else M855
    aero = aeroballistics.Aerodynamics(p, convention="modern")    # the canonical one, in McCoy's convention
    print(aero.describe())
    print("available coefficients:", ", ".join(aero.names))

    # In an integrator, at each step: M = V/a and α = total angle of attack.
    for degrees in (0.0, 2.0, 8.0):
        alpha = np.radians(degrees)
        print(f"\nThe seven at α = {degrees:.0f}°:")
        print("  Mach " + "".join(f"{n:>9s}" for n in SEVEN))
        for M in (0.6, 0.9, 1.1, 1.5, 2.0, 2.5, 3.0):
            k = seven(aero, M, alpha)
            print(f"  {M:4.2f} " + "".join(f"{float(k[n]):9.4f}" for n in SEVEN))

    # Vectorized: arrays of Mach (and of α) at once.
    machs = np.linspace(0.7, 2.8, 4)
    print("\nvectorized CMA at", np.round(machs, 2), "->", np.round(aero.coefficient("Cma", machs), 4))

    base = _file_name(p)
    if args.npz:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT / f"{base}_seven.npz"
        np.savez_compressed(path, **grid(aero))
        print("\nwritten:", path)

    if args.csv:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        path = OUTPUT / f"{base}_seven.csv"
        g = aeroballistics.MACH_GRID
        k = seven(aero, g, 0.0)
        k["CNP"] = aero.coefficient("Cmpa", g)               # slope at 1°
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Mach", *SEVEN])
            for j, M in enumerate(g):
                w.writerow([f"{M:g}", *(f"{float(k[n][j]):.6g}" for n in SEVEN)])
        print("\nwritten:", path)


if __name__ == "__main__":
    main()
