"""The free-flight correction (optional addition) against canonical SPIN-73.

    python examples/04_free_flight_correction.py

SPIN-73 works in calibers and does not know the projectile's actual size, so it does not see
the effect of the Reynolds number on drag, which weighs on small arms. The "free_flight"
correction was fitted to published free-flight measurements
(scripts/free_flight/correction/fit_correction.py) and only keeps what the cross-validation,
leaving one group of projectiles out at a time, accepted. It needs the actual diameter: from
the card's DIA or from ``d_mm``.

"free_flight" applies every accepted piece; "free_flight:CX0" only the drag one, the firmest.
Details in docs/free_flight/CORRECTION.md and docs/LIBRARY.md.
"""
from __future__ import annotations

from _bootstrap import prepare

prepare()

import aeroballistics  # noqa: E402
from aeroballistics.corrections.free_flight import FreeFlight  # noqa: E402

M855 = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9, BD=1.00,
                         DIA=5.69 / 25.4, name="5.56 mm M855")


def main() -> None:
    canonical = aeroballistics.Aerodynamics(M855)
    cx0_only = aeroballistics.Aerodynamics(M855, corrections="free_flight:CX0")
    everything = aeroballistics.Aerodynamics(M855, corrections="free_flight")
    print(everything.describe())

    print(f"\n{'Mach':>5s} {'CX0 1973':>9s} {'free_flight:CX0':>16s} {'diff.':>7s}   "
          f"{'CNA 1973':>9s} {'free_flight':>11s}")
    for M in (0.6, 0.8, 0.9, 1.1, 1.5, 2.0, 2.5, 3.0):
        a, b = canonical(M), cx0_only(M)
        c = everything(M)
        print(f"{M:5.2f} {a.CX0:9.4f} {b.CX0:16.4f} {100 * (b.CX0 / a.CX0 - 1):+6.1f}%   "
              f"{a.CNA:9.4f} {c.CNA:11.4f}")

    print("\nCross-validation (mean relative error on the left-out groups):")
    print(f"  {'coef.':5s} {'regime':12s} {'SPIN-73':>8s} {'corrected':>9s} {'improved':>9s} "
          f"{'worst ratio':>11s}  accepted?")
    for coef, regimes in FreeFlight().validation().items():
        for regime, v in regimes.items():
            print(f"  {coef:5s} {regime:12s} {v['spin73']:8.3f} {v['corrected']:9.3f} "
                  f"{v['groups_improved']:4d} of {v['groups']:<2d} {v['worst_ratio']:11.2f}  "
                  f"{'yes' if v['accepted'] else 'no'}")


if __name__ == "__main__":
    main()
