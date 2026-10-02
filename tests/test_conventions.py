"""Convention conversions: round trip, and consistency with the ones already validated in scripts/free_flight/hitchcock/."""
import numpy as np

import spin73 as s
from spin73 import conventions as cv


def test_round_trip():
    t = s.table(s.M437)
    m = cv.to_modern(t, VL=s.M437.VL)
    v = cv.from_modern(m)
    for c in ("CX", "CX2", "CNA", "CMA", "CMQ", "CLP", "CYPA", "CNPA", "CPN"):
        assert np.allclose(v[c], t[c]), c


def test_normalization_factors():
    """SPIN-73's pd/2V and qd/2V against pd/V and qd/V: the modern value is half.
    It is the same factor 2 validated on Hitchcock (K_H) and used with BRL MR 1833."""
    t = s.table(s.M437)
    m = cv.to_modern(t)
    assert np.allclose(m["Cmq_Cmad"] * 2, t["CMQ"])
    assert np.allclose(m["Cmpa"] * 2, t["CNPA"])


def test_yaw_drag_is_cx2_plus_cna():
    """Report, p. 15: the yaw drag is CX2 + CNα."""
    t = s.table(s.M437)
    assert np.allclose(cv.to_modern(t)["CDd2"], t["CX2"] + t["CNA"])


def test_cp_from_moment_reproduces_cpn():
    t = s.table(s.M437)
    assert np.allclose(cv.cp_from_moment(s.M437.VCG, t["CMA"], t["CNA"]), t["CPN"])
