"""Reconstructed CPN and CMα against three printed SPIN-73 tables with a boattail.

175 mm M437 (p. 65, 1.00 cal boattail), 5"/38 NAVY (p. 53, 0.35 cal) and 105 mm XM380E5
(p. 50, 0.59 cal). The geometries give very different weights to the boattail coefficients
(C12..C16), so a misreading in C1..C11 cannot disguise itself as an error in C12..C16, nor the
other way round. The XM380E5 decided no XC: it is a test at every Mach.

Uses the PRINTED CNα of each table (see cpn_spin73.cpn_cma): without it, the error of the
reconstructed CNα enters the CPN residual multiplied by ~3.
"""
import numpy as np
import pytest

import paths
import spin73 as s
import printed_tables as pt
from cpn_spin73 import cpn_cma
from data_cna import T as T_CNA
from data_cpn import CPN_538, BY_IDENTITY
from spin73.data.xc_read import CORRECTIONS, DECIDED_M437, RECOVERED

TAB437 = s.read_table(paths.TABLES_1973 / "m437_table.csv")
TAB380 = pt.load(50).columns
GEO = {  # (VL, VN, VB, OR, DM, VCG), printed CNα, printed CPN
    "M437": ((5.51, 2.91, 1.00, 25.0, 0.079, 3.50), TAB437["CNA"], TAB437["CPN"]),
    "5/38": ((4.59, 2.15, 0.35, 5.3, 0.100, 2.71), np.array(T_CNA[53][5], float),
             np.array([BY_IDENTITY.get(j, CPN_538[j]) for j in range(17)])),
    "XM380E5": ((5.58, 2.90, 0.59, 18.6, 0.130, 3.34), TAB380["CNA"], TAB380["CPN"]),
}

# Mach numbers where some XC was decided with the table itself (xc_read.py).
_BY = {"M437": set(), "5/38": set()}
for (_l, _j) in CORRECTIONS:
    _BY["M437"].add(_j)
    if (_l, _j) in {(12, 6), (1, 2), (12, 1), (12, 9), (12, 10)}:   # decided with both
        _BY["5/38"].add(_j)
for (_l, _j) in RECOVERED:
    _BY["M437"].add(_j); _BY["5/38"].add(_j)
for (_l, _j) in DECIDED_M437:
    _BY["M437"].add(_j)
CIRCULAR = {"M437": _BY["M437"], "5/38": _BY["5/38"], "XM380E5": set()}

PENDING = {
    "M437": {},
    "5/38": {
        # Mach 1.75 and 2.5 to 5 closed with card C205 (NOTES, T15).
        15: "Mach 4: +0.0023 with XC15 constant from 2.5 to 5 (the M437 asked for -0.9211 there)",
    },
    "XM380E5": {
        1: "Mach 0.6: +0.0019 (the M437 has +0.0044, circular); no single coefficient "
           "explains the three tables (NOTES, T13)",
    },
}


def _cpn(name, j):
    geo, cna, _ = GEO[name]
    return cpn_cma(*geo, j, printed_cna=cna[j])[0]


CASES = [(n, j) for n in GEO for j in range(17)
         if np.isfinite(GEO[n][2][j]) and j not in CIRCULAR[n] and j not in PENDING[n]]


@pytest.mark.parametrize("name,j", CASES)
def test_cpn(name, j):
    assert abs(_cpn(name, j) - GEO[name][2][j]) <= 0.0015


@pytest.mark.parametrize("name", ["5/38", "XM380E5"])
def test_pending_items_still_pending(name):
    resolved = [j for j in PENDING[name] if abs(_cpn(name, j) - GEO[name][2][j]) <= 0.0015]
    assert not resolved, (name, resolved)


def test_xm380e5_is_a_test_at_every_mach():
    """The third table decided no XC: it stays independent at 16 of the 17 Mach numbers."""
    assert sum(1 for n, _ in CASES if n == "XM380E5") == 16


def test_cma_of_the_m437():
    """CMα = (VCG − CPN)·CNα: closes where the CPN closes, with the 3-place rounding."""
    geo, cna, _ = GEO["M437"]
    for j in (n_j[1] for n_j in CASES if n_j[0] == "M437"):
        cma = cpn_cma(*geo, j, printed_cna=cna[j])[1]
        assert abs(cma - TAB437["CMA"][j]) <= 0.004, (j, cma, TAB437["CMA"][j])


def test_decisions_out_of_the_validation():
    """A value decided by a table cannot be 'validated' by it."""
    assert 6 in CIRCULAR["M437"] and 6 in CIRCULAR["5/38"]      # XC12 at Mach 1.05
    assert 13 in CIRCULAR["M437"] and 13 not in CIRCULAR["5/38"]  # XC1 at Mach 2.5
    assert 5 in CIRCULAR["M437"]                                  # XC14 at Mach 1.0


def test_recovered_xc15_reproduces_both_tables():
    """Where XC15 was recovered from the M437 and the 5"/38, both close."""
    for (_, j) in RECOVERED:
        for name in ("M437", "5/38"):
            assert abs(_cpn(name, j) - GEO[name][2][j]) <= 0.0015, (name, j)


def test_decided_cells_only_the_boattail_weighs_xc15():
    """The list of decided cells that enter the CPN follows the Mach interpolation and ignores
    the boattail block (XC12..XC16) when VB = 0."""
    from cpn_spin73 import decided_cells
    assert decided_cells(1.1, 0.5) == []                         # grid point with no decision
    assert decided_cells(1.2, 0.0) == []                         # XC15 has no weight on a flat base
    assert decided_cells(1.2, 0.5) == [(15, 8, "RECOVERED")]
    assert decided_cells(2.3, 0.0) == [(1, 13, "CORRECTIONS")]   # between 2.0 and 2.5
    assert {l for l, _, _ in decided_cells(2.3, 0.5)} == {1, 15}
