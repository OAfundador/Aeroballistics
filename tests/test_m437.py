"""Validation against Table 14 of SPIN-73 (175 mm M437).

Run:  python -m pytest -v tests/test_m437.py

Three levels of test:
  1. Internal consistency of the transcription (the table against itself).
  2. Stability analysis recomputed against the printed columns.
  3. Structure of the empirical equations (without the DATA, identities only).
"""
import numpy as np
import pytest

import paths
import aeroballistics as s

TAB = s.read_table(paths.TABLES_1973 / "m437_table.csv")
P = s.M437

# Readings where the scan was ambiguous (typically 6/8, 1/3, 2/5 in the dot-matrix printout)
# and that were decided by an independent identity -- see TRANSCRIPTION_NOTES.md, section T.
# They stay OUT of the comparisons so that the validation is not circular (the model cannot
# confirm what it helped decide).
DECIDED_READINGS = {
    ("CX", 0.01), ("CX", 0.60),        # 0.1?5 -> 0.105   (via SBAR)
    ("SPIN", 0.80),                    # 4?9.2 -> 489.2   (p proportional to Mach)
    ("CPF5", 0.80), ("CPF5", 0.95),    # 4.23?/4.0?6      (via CNPA5 and CYPA)
    ("L1", 0.80),                      # -.000?42 -> -.000382 (via L1+L2)
    ("SBAR5", 1.35),                   # 1.?01 -> 1.201   (via RECIP5)
    ("L15", 1.10),                     # -.00016? -> -.000168 (via L15+L25)
    ("RECIP5", 1.05),                  # 1.06? -> 1.068   (via SBAR5)
}


def _mask(*cols):
    return np.array([all((c, round(m, 2)) not in DECIDED_READINGS for c in cols)
                     for m in TAB["MACH"]])


def _compare(col, calc, atol=0.0, rtol=0.0, inputs=()):
    ok = _mask(col, *inputs)
    ref = TAB[col][ok]
    got = np.asarray(calc)[ok]
    err = np.abs(got - ref)
    lim = atol + rtol * np.abs(ref)
    bad = [(float(m), float(r), float(g)) for m, r, g, e, l in
           zip(TAB["MACH"][ok], ref, got, err, lim) if e > l]
    assert not bad, f"{col}: (Mach, table, computed) outside the tolerance: {bad}"


# ---------------------------------------------------------------- level 1
def test_cma_cpn_consistency():
    """CMA = (VCG - CPN) * CNA, with CPN printed to 3 places."""
    calc = (P.VCG - TAB["CPN"]) * TAB["CNA"]
    _compare("CMA", calc, atol=0.004, inputs=("CPN", "CNA"))


@pytest.mark.parametrize("cn, cp", [("CNPA", "CPF1"), ("CNPA5", "CPF5")])
def test_magnus_consistency(cn, cp):
    """Cnpa = (VCG - CPF) * CYPA."""
    calc = (P.VCG - TAB[cp]) * TAB["CYPA"]
    _compare(cn, calc, atol=0.002, inputs=(cp, "CYPA"))


@pytest.mark.parametrize("sb, rc", [("SBAR", "RECIP"), ("SBAR5", "RECIP5")])
def test_recip_consistency(sb, rc):
    """RECIP = 1/(sd(2-sd)): the s_g limit for stability."""
    sd = TAB[sb]
    ok = _mask(sb, rc)
    calc = 1.0 / (sd * (2.0 - sd))
    ref = TAB[rc]
    # a 3-place sd near 1 amplifies little; near 0 it amplifies a lot
    tol = 0.002 + 0.02 * np.abs(ref) * (np.abs(sd) < 0.3)
    assert np.all(np.abs(calc - ref)[ok] <= tol[ok])


# ---------------------------------------------------------------- level 2
@pytest.fixture(scope="module")
def stab():
    return s.stability(P, TAB["MACH"], TAB["CX"], TAB["CNA"], TAB["CMA"],
                       TAB["CNPA"], TAB["CNPA5"], TAB["CMQ"], TAB["CLP"])


STAB_INPUTS = ("CX", "CNA", "CMA", "CNPA", "CNPA5", "CMQ", "CLP")


def test_spin(stab):
    _compare("SPIN", stab["SPIN"], atol=0.15)


def test_gyro(stab):
    # With the constant 1352.4 of card C241 the −0.17 % bias disappears (item A1 of the NOTES,
    # resolved): only the rounding of the printout remains.
    _compare("GYRO", stab["GYRO"], atol=0.0015, inputs=STAB_INPUTS)


@pytest.mark.parametrize("col", ["SBAR", "SBAR5"])
def test_sd(stab, col):
    _compare(col, stab[col], atol=0.002, inputs=STAB_INPUTS)


@pytest.mark.parametrize("col", ["W1", "W2"])
def test_frequencies(stab, col):
    # propagates the s_g residual through sigma
    _compare(col, stab[col], atol=0.02, rtol=0.004, inputs=STAB_INPUTS)


@pytest.mark.parametrize("col", ["L1", "L2", "L15", "L25"])
def test_damping(stab, col):
    _compare(col, stab[col], atol=1.5e-6, inputs=STAB_INPUTS)


def test_text_formula_does_not_reproduce(stab):
    """Records finding E1: with the sign printed in the text, L1/L2 do not match."""
    d = P.DIA / 12; m = P.WGT / s.G_FT
    Ix = P.IX / (s.G_FT * 144); Iy = P.IY / (s.G_FT * 144)
    K = s.air_density(P.TEMP) * np.pi * d * d / 4 / (4 * m)
    sig = np.sqrt(1 - 1 / stab["GYRO"])
    k1, k2 = m * d * d / Ix, m * d * d / Iy
    L1_text = K * (-TAB["CNA"] * (1 + 1 / sig) + k2 / 2 * (1 + 1 / sig) * TAB["CMQ"]
                   + k1 / sig * TAB["CNPA"])
    ok = _mask("L1")
    assert np.max(np.abs(L1_text - TAB["L1"])[ok]) > 1e-4


# ---------------------------------------------------------------- level 3
def test_no_data_returns_nan():
    c = s.coefficients(P, s.DataBlocks())
    assert all(np.all(np.isnan(v)) for k, v in c.items() if k != "MACH")


def test_structural_identities():
    """With synthetic coefficients, the algebraic relations of the text hold."""
    rng = np.random.default_rng(0)
    k = s.DataBlocks(a=rng.normal(size=(15, 17)), B=rng.normal(size=(10, 17)) + 3,
                     C=rng.normal(size=(17, 17)), D=rng.normal(size=(4, 17)),
                     E=rng.normal(size=(5, 17)) - 1, F=rng.normal(size=(9, 17)),
                     G=rng.normal(size=(1, 17)))
    c = s.coefficients(P, k)
    assert np.allclose(c["CMA"], (P.VCG - c["CPN"]) * c["CNA"])
    assert np.allclose(c["CNPA"], (P.VCG - c["CPF1"]) * c["CYPA"])
    assert np.allclose(c["CYPA"], k.E[0] * P.VL - 0.1 * P.VB)
    assert np.allclose(c["CLP"], k.G[0] * P.VL / 5.51)
