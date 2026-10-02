"""The 1973 program as objects: where each column comes from.

    python examples/05_original_program.py              # the CMα block
    python examples/05_original_program.py CMQ GYRO     # the blocks of those columns

``aeroballistics.program.SPIN73`` describes the original program block by block, in our own words and
notation: formulas, rules, DATA blocks used, the listing statements the reading was based on,
what could not be read and the function that implements each block here. The listing is not
reproduced; it is in the report (DTIC AD0915628). The whole program, in Markdown, is in
docs/ORIGINAL_PROGRAM.md (``aeroballistics --program`` prints the same as text).
"""
from __future__ import annotations

import argparse

import numpy as np

from _bootstrap import prepare

prepare()

import aeroballistics  # noqa: E402
from aeroballistics.program import SPIN73  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("columns", nargs="*", default=["CMA"], help="output columns (CX, CNA, CMA, GYRO...)")
    args = ap.parse_args()

    print("Blocks, in the order the program computes them:")
    for b in SPIN73:
        print(f"  {b.key:14s} {', '.join(b.columns) or '—'}")

    for column in args.columns:
        b = SPIN73.from_column(column)
        print("\n" + "-" * 90)
        print(b)
        values = b.compute(aeroballistics.M437)               # through the whole program, for the 175 mm M437
        print(f"\n  {column} of the M437 at the 17 Mach numbers:", np.round(values[column], 4))


if __name__ == "__main__":
    main()
