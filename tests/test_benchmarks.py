"""Guard of the convention conversions in the benchmarks.

It does not pin SPIN-73's error against reality (that is a result, not a requirement). It only
tests that the normalizations were applied: a forgotten factor 2 in qd/V or pd/V would leave
the SPIN-73/measured ratio of the supersonic Cmq near 0.5 or 2, and not near 1 as in the three
independent sources.
"""
import compare as cp


def _ratio(res, coef, rng):
    return next(r[5] for r in res if r[0] == coef and r[1] == rng)


def test_supersonic_cmq_in_the_three_sources():
    for f in (cp.m101, cp.m483a1, cp.m33):
        assert 0.8 < _ratio(f(), "CMQ", "supersonic") < 1.25, f.__name__


def test_supersonic_cma_m101_and_m483a1():
    """The two artillery projectiles: SPIN-73's CMα is within a few percent."""
    for f in (cp.m101, cp.m483a1):
        assert 0.95 < _ratio(f(), "CMA", "supersonic") < 1.05, f.__name__


def test_supersonic_cmq_in_the_new_sources():
    """The same guard for the 7.62 match and the 30 mm (McCoy, qd/V) and the T203 (K notation).
    Here the range is 0.8-1.6: there are groups with 3 rounds; a forgotten factor 2 would give
    0.5-0.7 or 1.9-2.9."""
    n = 0
    for res in cp.match762() + cp.x30():
        if any(r[0] == "CMQ" and r[1] == "supersonic" for r in res):
            assert 0.8 < _ratio(res, "CMQ", "supersonic") < 1.6
            n += 1
    assert n == 6
    assert 0.8 < _ratio(cp.t203(), "KH", "supersonic") < 1.3


def test_t203_drag_and_cma():
    """The T203 is the M437 under development: drag within 1 % and supersonic CMα within 1 % of
    SPIN-73, which was calibrated on that family (and with the M437's OR; see correction/flight_data.py)."""
    res = cp.t203()
    assert 0.97 < _ratio(res, "KD", "supersonic") < 1.03
    assert 0.95 < _ratio(res, "KM", "supersonic") < 1.05


def test_xm617_cone_cylinder_supersonic():
    """Full-scale cone-cylinder: at supersonic speeds SPIN-73 gets CD, CMα and CNα within a few %."""
    res = cp.xm617()
    for c in ("CD", "CMA", "CNA"):
        assert 0.95 < _ratio(res, c, "supersonic") < 1.05, c
