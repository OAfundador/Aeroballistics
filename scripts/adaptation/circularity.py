"""Which cells of each printed table helped DECIDE some DATA value or some input.

Those cells validate nothing in that table: they only show that the decision is consistent.
The record comes from the decisions themselves (aeroballistics.data.xa_read ... xf_read, data_cna.py
and the "decide:" lines of the CSVs), so that there is no parallel list to go stale.

    circular(page, table=None) -> {(column, Mach): reason}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths                                                  # noqa: E402,F401

import aeroballistics as s                                            # noqa: E402
from data_cna import T as _T_CNA                              # noqa: E402
from aeroballistics.data.xa_read import DECIDED as _XA_DEC            # noqa: E402
from aeroballistics.data.xb_read import CORRECTIONS as _XB_CORR, DECIDED_BY as _XB_BY  # noqa: E402
from aeroballistics.data.xc_read import (CORRECTIONS as _XC_CORR, DECIDED_M437,  # noqa: E402
                                 RECOVERED as _XC_REC)
from aeroballistics.data.xd_read import DECIDED as _XD_DEC            # noqa: E402
from aeroballistics.data.xf_read import RECOVERED as _XF_REC          # noqa: E402

MACH = [round(float(m), 2) for m in s.MACH_GRID]

# The 6 XB corrections were decided by counting the cells that close in the 10 tables with
# the CNA column transcribed (NOTES, T5 and T7).
PAGES_XB = set(_T_CNA)
# The first 12 values of XE5 (card not printed) come from the long-body tables.
PAGES_XE5 = {35, 38, 41, 68}
# XC corrections decided by both tables (M437 and 5"/38); the others, by the M437 alone.
_XC_BOTH = {(12, 6), (1, 2), (12, 1), (12, 9), (12, 10)}
_DEPENDS_ON_CMA = ("CPN", "CMA", "GYRO", "W1", "W2", "L1", "L2", "L15", "L25", "DELT", "DISP")


def _mark(d, cols, js, reason):
    for c in cols:
        for j in js:
            d.setdefault((c, MACH[j]), reason)


def circular(page, table=None):
    d = {}
    if table is not None:
        for (col, M) in table.circular():
            var = [v for v, (_, _, c, _) in table.decide.items() if c == col]
            d[(col, M)] = (f"input {var[0]} decided by this column" if var else
                           "tied by an identity to a column that decided an input")
    for (b, j) in _XB_CORR:
        by = _XB_BY.get((b, j), PAGES_XB)
        if page in by:
            _mark(d, ["CNA"], [j], f"XB{b} decided with this table"
                  + (" (count over the 10 CNα tables)" if len(by) > 1 else ""))
    if page in PAGES_XE5:
        _mark(d, ["CPF1", "CPF5", "CNPA", "CNPA5"], range(12),
              "XE5 from Mach 0.01 to 1.75 (card not printed) identified from the long-body tables")
    if page in (53, 65):
        js = {j for (l, j) in _XC_CORR if page == 65 or (l, j) in _XC_BOTH}
        js |= {j for (_, j) in _XC_REC}
        if page == 65:
            js |= {j for (_, j) in DECIDED_M437}
        _mark(d, _DEPENDS_ON_CMA, sorted(js), "XC decided with this table")
        _mark(d, ["CX2"], sorted({j for (_, j) in _XD_DEC if page == 53 or j != 13}),
              "XD decided with this table")
        _mark(d, ["CX"], sorted({j for (_, j) in _XA_DEC}), "XA1/XA2 decided with this table")
    if page == 53:
        _mark(d, ["CMQ"], sorted({j for (_, j) in _XF_REC}), "missing XF7 card recovered from this table")
    return d


def circular_machs(page, column, table=None):
    return {M for (c, M) in circular(page, table) if c == column}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for page in map(int, sys.argv[1:]):
        for (c, M), m in sorted(circular(page).items()):
            print(page, c, M, m)
