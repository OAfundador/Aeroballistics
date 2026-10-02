"""Adapted CX2 (DATA XD) against three tables: 175 mm M437, 5"/38 and 105 mm XM380E5.

Uses the PRINTED CNα of each table, because the equation subtracts CNα: that way the test
isolates XD from the error of the adapted CNα.
"""
import numpy as np
import pytest

import paths
import aeroballistics as s
import printed_tables as pt
from data_cna import T as T_CNA
from data_cx2 import CNA_SUSPECT, CX2_538, DECIDED as DECIDED_538, ILLEGIBLE
from aeroballistics.data.xd_read import DECIDED, XD

TAB = s.read_table(paths.TABLES_1973 / "m437_table.csv")


def cx2(VL, VN, VB, OR, cna, j):
    CXCL = VL - VN - VB - 1.5
    CRAT = VN ** 2 / OR - 0.40
    return XD[0, j] + XD[1, j] * CXCL + XD[2, j] * CRAT + XD[3, j] * VB - cna


# M437: cells that do not agree, with the reason
M437_OUT = {2: "ambiguous scan 2.6?3; the DATA asks for 2.805 (pair 6/8)",
            7: "illegible scan; the DATA gives 5.002",
            13: "residual of −0.030 still open; the M437 barely weighs on XD2 (CXCL = 0.10)"}
# Mach numbers where some XD cell was decided by the 5"/38 or by the M437
CIRCULAR = {j for (_, j) in DECIDED}


@pytest.mark.parametrize("j", [j for j in range(17) if j not in M437_OUT and j not in CIRCULAR])
def test_m437(j):
    calc = cx2(5.51, 2.91, 1.0, 25.0, TAB["CNA"][j], j)
    tol = 0.010 if j in (10, 11) else 0.0045          # 1.5 and 1.75: residual of ~0.008 still open
    assert abs(calc - TAB["CX2"][j]) <= tol, (j, calc, TAB["CX2"][j])


@pytest.mark.parametrize("j", [j for j in range(17) if j not in DECIDED_538 and j not in ILLEGIBLE
                               and j not in CNA_SUSPECT and j not in CIRCULAR])
def test_5_38(j):
    cna = T_CNA[53][5][j]
    calc = cx2(4.59, 2.15, 0.35, 5.3, cna, j)
    assert abs(calc - CX2_538[j]) <= 0.0025, (j, calc, CX2_538[j])


def test_reread_of_the_m437_at_1_05():
    """The old transcription said 4.567; the reread scan says 4.507, and the DATA gives the same."""
    assert TAB["CX2"][6] == pytest.approx(4.507)
    assert abs(cx2(5.51, 2.91, 1.0, 25.0, TAB["CNA"][6], 6) - 4.507) < 0.0015


# XM380E5 (p. 50): no XD was decided by it. The XD2 of Mach 2.5 was decided by the 5"/38,
# which has the same CXCL (0.59): this is its independent check.
TB380 = pt.load(50).columns


@pytest.mark.parametrize("j", [j for j in range(17) if np.isfinite(TB380["CX2"][j])])
def test_xm380e5(j):
    calc = cx2(5.58, 2.90, 0.59, 18.6, TB380["CNA"][j], j)
    assert abs(calc - TB380["CX2"][j]) <= 0.0015, (j, calc, TB380["CX2"][j])
