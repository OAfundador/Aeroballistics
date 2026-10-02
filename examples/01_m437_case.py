"""The report's validation case: 175 mm M437 (Table 14, p. 65), from the geometry only.

    python examples/01_m437_case.py
    python examples/01_m437_case.py --csv        # also writes output/examples/m437.csv

It is the same as ``spin73 --example``, through the library: the input card printed in the
report (``spin73.M437``) goes through the reconstructed program, which returns the 24 columns at
the 17 Mach numbers of the grid, with the stability analysis. The cell-by-cell comparison with
the table printed in 1973, separating independent validation from what is circular, is in
tests/test_full_model.py and in scripts/reconstruction/error_comparison.py.
"""
from __future__ import annotations

import argparse

from _bootstrap import OUTPUT, prepare

prepare()

import spin73  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", action="store_true", help="writes the table to output/examples/m437.csv")
    args = ap.parse_args()

    p = spin73.M437                      # VL, VN, VB, VCG... as on the printed card
    t = spin73.table(p)                  # {"MACH": array(17), "CX": array(17), ...}
    print(spin73.format_table(t, title=p.name))
    print()
    for warning in spin73.geometry_warnings(p):   # limitations of the reconstruction for this projectile
        print("warning:", warning)

    if args.csv:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        spin73.save_csv(t, str(OUTPUT / "m437.csv"))
        print("\nwritten:", OUTPUT / "m437.csv")


if __name__ == "__main__":
    main()
