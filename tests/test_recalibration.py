"""Least squares recovers known coefficients from synthetic data with the same design."""
import numpy as np
import recalibrate_mr1833 as r


def test_recovers_synthetic_coefficients():
    rows = r.table()
    rng = np.random.default_rng(1)
    truth = {"const": lambda M: 3.0 + 0.2 * (M - 2) - 0.1 * (M - 2) ** 2,
             "CXLL": lambda M: 0.5 - 0.05 * (M - 2)}
    for l in rows:
        l["SYNTH"] = truth["const"](l["M"]) + truth["CXLL"](l["M"]) * l["CXLL"] + rng.normal(0, 0.01)
    regs = {"const": lambda l: 1, "CXLL": lambda l: l["CXLL"]}
    fit = r.lsq(rows, "SYNTH", regs, ["M-80", "M-59", "M-61", "M-62"])
    ev = r.evaluate(fit, r.GRID)
    for k in regs:
        v, e = ev[k]
        assert np.all(np.abs(v - truth[k](r.GRID)) < 4 * e + 1e-3), k


def test_pure_error_and_residual_compatible():
    """No gross lack of fit: residual < 1.5x pure error in the family's fits."""
    rows = r.table()
    for y, (regs, projs, _) in r.MODELS.items():
        fit = r.lsq(rows, y, regs, projs)
        ep, _ = r.pure_error(rows, y, projs)
        assert fit["s"] < 1.5 * ep, y


def test_recalibration_factor_recovers_synthetic_k():
    """Generates data with a known k(M) from the model itself and checks that least squares recovers it."""
    import numpy as np
    import compare_cmq_cp as c

    k_truth = lambda M: 0.5 + 0.2 * (M - 2) - 0.05 * (M - 2) ** 2
    rows = r.table()
    rng = np.random.default_rng(3)
    for l in rows:
        mod = np.interp(l["M"], c.MACH, c.cmq_curve(r.GEO[l["proj"]]))
        l["SYNTH"] = k_truth(l["M"]) * mod + rng.normal(0, 0.5)
    grid, k, sk, n, s = c.recalibration_factor(rows, "SYNTH", c.cmq_curve)
    assert n >= 40
    assert np.all(np.abs(k - k_truth(grid)) < 4 * sk + 0.02), (k, k_truth(grid), sk)


def test_spin73_cmq_is_stronger_than_the_experiment():
    """Records the finding: k < 1 over the whole range with data (the model damps too much)."""
    import numpy as np
    import compare_cmq_cp as c

    grid, k, sk, n, s = c.recalibration_factor(r.table(), "CMQ", c.cmq_curve)
    assert np.all(k + 2 * sk < 1.0), dict(zip(grid.tolist(), k.tolist()))


def test_spin73_cpn_behind_the_experiment_from_mach_2_on():
    """Records the finding: k < 1 on the CPN at Mach 2.0 and 2.5 with any of the three assumed
    ogive radii; at 2.5, by more than two standard deviations (at 2.0, with OR = 8 cal, it is
    at the limit). The model's CPN there depends on the XC15 decided by the 1973 tables."""
    import compare_cmq_cp as c

    rows = c.table()
    for OR in (8.0, c.OR_HYP, 12.0):
        grid, k, sk, n, s = c.recalibration_factor(rows, "CPN", lambda g: c.cpn_curve(g, OR),
                                                   grid=np.array([2.0, 2.5]))
        assert n == 42
        assert np.all(k < 1.0) and k[1] + 2 * sk[1] < 1.0, (OR, k, sk)


def test_cna_of_the_m80_and_card_c205():
    """Records the CNα bias on the M-80 (+0.21) and that the +0.28 of the first comparison was
    the same computation without card C205."""
    import compare_cmq_cp as c
    import compare_cna as cn

    rows = r.table()
    with_c205 = {p: v for p, _, v, _ in c.per_round(rows, "CNA", cn.cna_curve)}
    without = {p: v for p, _, v, _ in c.per_round(rows, "CNA", lambda g: cn.cna_curve(g, c205=False))}
    assert abs(with_c205["M-80"] - 0.214) < 0.005 and abs(without["M-80"] - 0.276) < 0.005
    assert all(abs(with_c205[p]) < 0.12 for p in ("M-59", "M-61", "M-62")), with_c205
