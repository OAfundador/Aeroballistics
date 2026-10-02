"""Reconstructed CX (DATA XA) against two tables: 175 mm M437 and 5"/38.

The two geometries give XA2 weights of opposite sign (VNX − 2.5 = +0.41 and −0.35) and XA7
very different weights (boattail 1.00 and 0.35 cal), which separates the coefficients.
Mach 0.01 and 0.6 are left out: they are the ones that decided XA1 and XA2 at those points.
"""
import pytest

import paths
import spin73 as s
from data_cx import CX_538
from spin73.data.xa_read import DECIDED, XA

TAB = s.read_table(paths.TABLES_1973 / "m437_table.csv")
K = s.DataBlocks(a=XA)
P538 = s.Projectile(VL=4.59, VN=2.15, VB=0.35, VCG=2.71, DM=0.100, BD=1.040, OR=5.3)
CIRCULAR = {j for (_, j) in DECIDED}


@pytest.mark.parametrize("j", [j for j in range(17) if j not in CIRCULAR])
def test_m437(j):
    assert abs(s.cx(s.M437, K, j) - TAB["CX"][j]) <= 0.0015


@pytest.mark.parametrize("j", [j for j in range(17) if j not in CIRCULAR])
def test_5_38(j):
    assert abs(s.cx(P538, K, j) - CX_538[j]) <= 0.0015


def test_xa2_reread_at_mach_1_05():
    """−.0487 at first sight; −.0687 under zoom; both tables asked for −.0688."""
    assert XA[1, 6] == pytest.approx(-.0687)
