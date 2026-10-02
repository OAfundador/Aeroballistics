"""The whole program, starting only from the printed input, against each table of `data/tables_1973/`.

For each table, each legible cell is compared with the computed value. Left out:
  - cells resolved by an identity between printed columns (marked in the CSV);
  - circular: cells where some DATA value or input was decided using that same table
    (circularity.py);
  - PENDING: cells that do not close, each one with its reason. If one starts to close, the
    test flags it and it must leave the list.
"""
import numpy as np
import pytest

import circularity
import spin73 as s
import printed_tables as pt

MACH = [round(float(m), 2) for m in s.MACH_GRID]
TABLES = {tb.page: tb for tb in pt.all_tables()}

# The same tolerances as the M437 test: ±1.5 units in the last place; CMα and CX2 inherit the
# error of the reconstructed CNα (up to 0.002), amplified.
TOL = {"CMA": 0.004, "CX2": 0.0045}

CIRCULAR = {page: circularity.circular(page, tb) for page, tb in TABLES.items()}

PENDING = {
    29: {},
    32: {},
    35: {("CNA", 0.95): "reconstructed CNα 0.0019 high (test_cna.py, PENDING)"},
    38: {},
    41: {("CMA", 3.0): "0.0044: at the limit (the printed CMα closes the identity with the printed CPN and CNα)"},
    53: {
        # Mach 1.75 to 5 closed with card C205 (NOTES, T15).
        ("CPN", 4.0): "+0.0023 with XC15 constant from 2.5 to 5",
        ("CMA", 4.0): "follows the CPN",
    },
    # M1 (pp. 44/47, the same printout on both pages of the scan): Magnus, Cmq and Clp close with
    # the header geometry, but CX, CX2, CNα, CPN and CMα do not (CX +0.005 and CX2 up to +0.23,
    # systematic). No single change of OR, DM, BD, VN or VB closes the five columns.
    44: {(c, M): "the header geometry does not reproduce CX, CX2, CNα, CPN and CMα (NOTES, T14)"
         for c in ("CX", "CX2", "CNA", "CPN", "CMA") for M in MACH if (c, M) != ("CX", 0.01)},
    56: {("CNA", 1.0): "reconstructed CNα 0.0016 low"},
    59: {("CNA", 0.95): "reconstructed CNα 0.004 low (test_cna.py, PENDING)",
         **{("CMA", M): "M101 CMα 0.009 to 0.018 high: follows the reconstructed CNα and CPN"
            for M in (1.0, 1.05, 1.5, 2.0)},
         ("CPN", 1.2): "M101 CPN 0.007 low (0.45 cal boattail; NOTES, T14)"},
    62: {("CNA", 0.95): "reconstructed CNα 0.0018 low"},
    68: {("CNA", 1.05): "reconstructed CNα 0.0016 high",
         ("CPN", 1.5): "CPN 0.0025 high (XC17, ogive > 3 cal)"},
    50: {
        ("CNA", 0.95): "reconstructed CNα 0.0017 low (as on the M437 at 0.8 and 1.05)",
        ("CPN", 0.6): "the subsonic residual of Mach 0.6 (+0.0018; the M437 has +0.004): "
                      "no single coefficient explains the three tables (NOTES, T13); "
                      "the CMα stays within its tolerance",
    },
}

# A circular cell is already out of the validation: it does not need to (and cannot) be pending.
PENDING = {page: {k: v for k, v in p.items() if k not in CIRCULAR[page]} for page, p in PENDING.items()}


def _cells(page):
    tb = TABLES[page]
    t = s.table(tb.projectile())
    for col, v in tb.columns.items():
        if col == "MACH":
            continue
        for j, M in enumerate(MACH):
            if np.isfinite(v[j]) and (col, M) not in tb.identity:
                yield col, M, float(t[col][j]), float(v[j])


@pytest.mark.parametrize("page", sorted(TABLES))
def test_table_reproduced(page):
    bad = []
    for col, M, calc, printed in _cells(page):
        if (col, M) in CIRCULAR[page] or (col, M) in PENDING[page]:
            continue
        if not abs(calc - printed) <= TOL.get(col, 0.0015):
            bad.append((col, M, round(calc, 4), printed))
    assert not bad, f"p. {page}: (column, Mach, computed, printed) {bad}"


@pytest.mark.parametrize("page", sorted(TABLES))
def test_pending_items_still_pending(page):
    resolved = [(col, M) for col, M, calc, printed in _cells(page)
                if (col, M) in PENDING[page] and abs(calc - printed) <= TOL.get(col, 0.0015)]
    assert not resolved, f"p. {page}: remove from PENDING {resolved}"


def test_every_table_classified():
    assert set(TABLES) == set(PENDING)
    for page in TABLES:
        assert not set(CIRCULAR[page]) & set(PENDING[page])
