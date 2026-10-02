"""The report's validation case: 175 mm M437 (Table 14, p. 65), from the geometry only.

    python examples/01_m437_case.py
    python examples/01_m437_case.py --csv        # also writes output/examples/m437.csv

It is the same as ``aeroballistics --example``, through the library: the input card printed in the
report (``aeroballistics.M437``) goes through the adapted program, which returns the 24 columns at
the 17 Mach numbers of the grid, with the stability analysis. The cell-by-cell comparison with
the table printed in 1973, separating independent validation from what is circular, is in
tests/test_full_model.py and in scripts/adaptation/error_comparison.py.
"""
from __future__ import annotations

import argparse

from _bootstrap import OUTPUT, prepare

prepare()

import aeroballistics  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", action="store_true", help="writes the table to output/examples/m437.csv")
    args = ap.parse_args()

    p = aeroballistics.M437                      # VL, VN, VB, VCG... as on the printed card
    t = aeroballistics.table(p)                  # {"MACH": array(17), "CX": array(17), ...}
    print(aeroballistics.format_table(t, title=p.name))
    print()
    for warning in aeroballistics.geometry_warnings(p):   # limitations of the adaptation for this projectile
        print("warning:", warning)

    if args.csv:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        aeroballistics.save_csv(t, str(OUTPUT / "m437.csv"))
        print("\nwritten:", OUTPUT / "m437.csv")


if __name__ == "__main__":
    main()
