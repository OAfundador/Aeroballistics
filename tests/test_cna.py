"""Adapted CNa (DATA XB as read) against the CNA columns of 10 SPIN-73 tables.

Excluded: the table on p. 44 (90 mm M71, the most degraded transcription; residual at almost
every Mach) and the cells listed in PENDING, which still need rereading (table or DATA).
"""
import numpy as np
from data_cna import MACH, T
from fit_B import regressors
from aeroballistics.data.xb_read import XB, CORRECTIONS
from cna_spin73 import cna_j

# (32, 2.0): printed 2.?54, pair 6/8 (with 2.864 it would close). (38, 2.0) decided the XB3 of
# Mach 2.0 and is out because of circularity, not as pending (see CIRCULAR).
# The 5"/38 from Mach 1.75 to 5 closed with card C205 (positive CNBT zeroed; NOTES, T15).
PENDING = {(29, 0.95), (29, 1.2), (32, 0.9), (32, 2.0), (35, 0.95),
           (41, 1.35), (41, 1.5), (50, 0.95), (59, 0.95), (65, 0.8), (65, 1.05)}
CIRCULAR = {(38, 2.0)}


def test_cna_reproduces_tables():
    bad = []
    for p, (n, VL, VN, VB, OR, cna) in T.items():
        if p == 44:
            continue
        for j, M in enumerate(MACH):
            if (p, round(M, 2)) in PENDING | CIRCULAR or not np.isfinite(cna[j]):
                continue
            r = cna_j(VL, VN, VB, OR, j) - cna[j]
            if abs(r) > 0.0015:
                bad.append((p, M, round(r, 4)))
    assert not bad, bad


def test_few_corrections():
    """Six corrections decided by the count over the 10 tables and one (XB3, Mach 2.0) by a single
    table, with two others checking. A limit against fine-tuning the DATA."""
    assert len(CORRECTIONS) <= 7


def test_c205_closes_the_supersonic_5_38():
    """Without the rule of card C205, the 5"/38 sits 0.014 high from Mach 2.5 to 5."""
    n, VL, VN, VB, OR, cna = T[53]
    for j in (11, 13, 14, 15, 16):
        assert abs(cna_j(VL, VN, VB, OR, j) - cna[j]) <= 0.0015, j
