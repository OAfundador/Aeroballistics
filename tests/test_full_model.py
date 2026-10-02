"""The whole program, starting ONLY from the geometry, against the printed table of the 175 mm M437.

Unlike test_m437.py, which recomputes the stability from the printed coefficients, here every
coefficient comes from the reconstructed DATA blocks. Each cell that does not close yet is
listed with the reason; when a pending item is resolved, the test flags it and it must leave
the list.
"""
import numpy as np
import pytest

import paths
import spin73 as s

TAB = s.read_table(paths.TABLES_1973 / "m437_table.csv")
T = s.table(s.M437)
MACH = [round(float(m), 2) for m in s.MACH_GRID]

# Mach numbers where some CPN DATA was DECIDED using this same table (xc_read.py):
# XC12 at 0.6 and 1.05; XC1 at 0.8 and 2.5; XC14 at 1.0; XC15 from 1.2 to 2.0 (M437 + 5"/38, or
# M437 only at 1.75) and from 2.5 to 5 (M437 only). At those Mach numbers the M437 CPN and
# everything that depends on CMα cannot validate anything.
_CIRC_CPN = (0.6, 0.8, 1.0, 1.05, 1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0)
_DEPENDS_ON_CMA = ("CPN", "CMA", "GYRO", "W1", "W2", "L1", "L2", "L15", "L25", "DELT", "DISP")
CIRCULAR = {(c, m) for c in _DEPENDS_ON_CMA for m in _CIRC_CPN}

# (column, Mach) -> reason. Cells outside the tolerance that are NOT circular.
PENDING = {
    ("CNA", 0.8): "reconstructed CNα 0.0018 high (test_cna.py, PENDING)",
    ("CNA", 1.05): "reconstructed CNα 0.0022 high (test_cna.py, PENDING)",
    ("CPF5", 1.1): "ambiguous printed cell 4.23? (NOTES, T2)",
    ("CPN", 0.95): "the reconstructed CNα (0.001 low) enters ~3x into the CPN; with the printed CNα "
                   "it closes at +0.0007 (test_cpn.py)",
    ("CX2", 0.8): "ambiguous printed cell (2.6?3); the DATA XD asks for 2.805 (NOTES, T9)",
    ("CX2", 1.1): "illegible printed cell; the DATA XD gives 5.002 (NOTES, T9)",
    ("CX2", 1.5): "residual of ~0.007 still open on the M437 (the 5\"/38 closes)",
    ("CX2", 1.75): "residual of ~0.009 still open on the M437 (the 5\"/38 closes)",
    ("CX2", 2.5): "residual of −0.030 on the M437; the XD2 decided by the 5\"/38 closes the XM380E5 "
                  "(same weight), and the M437 barely weighs on XD2 (test_cx2.py)",
    ("SBAR", 1.75): "at the limit of the rounding",
    # CNPA3 and CNPA5P: cells resolved by the identity CNPA3 + 0.1·CNPA5P = 3.75 (circular for the
    # formula) stay out; DELT and DISP at Mach 0.01 and 0.6 were resolved by the formula itself
    # (pairs 6/0 and 6/8).
}
CIRCULAR |= {("CNPA5P", 0.95), ("DELT", 0.01), ("DELT", 0.6)}
# CX2 subtracts the reconstructed CNα, so it inherits its error (up to 0.0022); larger tolerance.
# RECIP = 1/(s_d(2−s_d)) amplifies the error of s_d ~100x when s_d ~ −0.07 (Mach 0.01 and 0.6).
TOL = {"CMA": 0.004, "CX2": 0.0045, "SPIN": 0.15, "W1": 0.05, "W2": 0.05, "RECIP": 0.08,
       "RECIP5": 0.003, **{c: 1.5e-6 for c in ("L1", "L2", "L15", "L25")},
       "CNPA3": 0.0015, "CNPA5P": 0.004, "DELT": 0.00015, "DISP": 0.0015}
COLUMNS = ["CX", "CX2", "CNA", "CPN", "CMA", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CMQ", "CLP",
           "GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2", "L1", "L2", "L15", "L25",
           "CNPA3", "CNPA5P", "DELT", "DISP"]


@pytest.mark.parametrize("col", COLUMNS)
def test_column_reproduces_the_table(col):
    bad = []
    for j, M in enumerate(MACH):
        if (col, M) in PENDING or (col, M) in CIRCULAR:
            continue
        if not np.isfinite(TAB[col][j]):
            continue                       # illegible cell in the transcription
        d = T[col][j] - TAB[col][j]
        if not (np.isfinite(d) and abs(d) <= TOL.get(col, 0.0015)):
            bad.append((M, round(float(T[col][j]), 4), float(TAB[col][j])))
    assert not bad, f"{col}: (Mach, computed, printed) {bad}"


def test_pending_items_still_pending():
    """If a pending item started to close, it must leave the list."""
    resolved = []
    for (col, M), reason in PENDING.items():
        j = MACH.index(M)
        d = T[col][j] - TAB[col][j]
        if np.isfinite(d) and abs(d) <= TOL.get(col, 0.0015):
            resolved.append((col, M))
    assert not resolved, f"remove from PENDING: {resolved}"


def test_every_column_comes_out_filled():
    """With every DATA block reconstructed, no column comes out NaN."""
    for col in COLUMNS:
        assert np.all(np.isfinite(T[col])), col


def test_circular_cells_do_not_count_as_verified():
    """No circular cell may also appear as pending: either it is a test, or it is not."""
    assert not (set(PENDING) & CIRCULAR)
