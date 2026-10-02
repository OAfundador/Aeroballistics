"""Magnus and Clp: coefficients identified on the M437 predict the other projectiles.

Run:  python -m pytest -v tests/test_magnus.py
"""
import numpy as np
import pytest

import magnus_clp as mc

# Cells with an ambiguous glyph whose reading diverges from the prediction (NOTES, section T2).
AMBIGUOUS = {
    ("175MM M437 (p.65)", "CPF5", 1.10),       # 4.23?  read 4.236, predicted 4.238
    ("5/38 NAVY (p.53)", "CPF1", 0.90),        # 2.74?  read 2.747, predicted 2.742
    ("155MM M101/107 (p.59)", "CPF1", 0.95),   # 3.00?  read 3.004, predicted 3.006
    ("155MM M101/107 (p.59)", "CPF1", 1.00),   # 3.1?8  read 3.170, predicted 3.128
    ("155MM M101/107 (p.59)", "CPF1", 1.05),   # 3.2?4  read 3.294, predicted 3.254
    ("155MM M101/107 (p.59)", "CPF5", 0.80),   # 3.40?  read 3.404, predicted 3.406
    ("20MM 7 CAL ANSR (p.35)", "CPF5", 5.00),  # 4.82?  read 4.823, predicted 4.825
}


@pytest.mark.parametrize("name", list(mc.TABLES))
@pytest.mark.parametrize("col", ["CYPA", "CPF1", "CPF5", "CLP"])
def test_prediction(name, col):
    t = mc.TABLES[name]
    if col not in t:
        pytest.skip("column not transcribed")
    p = np.round(mc.predict(t)[col], 3)
    ok = np.array([(name, col, round(m, 2)) not in AMBIGUOUS for m in mc.MACH])
    # allows 1 unit in the 3rd place (rounding of the printout; G1 has only 3 places)
    tol = 0.0011
    assert np.all(np.abs(p - t[col])[ok] <= tol)


def test_inversion_is_round():
    """The exact inversion of the M437 lands near 2-place values.
    (The largest deviation, ~0.0018 in E4 at Mach 1.1, comes from the ambiguous CPF5 cell.)"""
    e1, e2, e4, _ = mc.identify(mc.TABLES["175MM M437 (p.65)"])
    for v, r in ((e1, mc.E1), (e2, mc.E2), (e4, mc.E4)):
        assert np.max(np.abs(v - r)) < 2e-3
