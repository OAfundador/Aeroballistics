"""Hitchcock's caliber 0.30 (1947) against the SPIN-73 reconstruction (1973).

Three levels of validation, from the strongest to the weakest:
  1. Internal identities of the report itself (independent of SPIN-73): the geometry of each
     sketch closes by the sum of the parts, and the K_M of each firing series is consistent
     with the stability factor S, the velocity and the tabulated moments of inertia. A misread
     digit in any of those columns shows up here.
  2. Conversions between the BRL notation and the SPIN-73 one (conversions.py).
  3. Comparison of the model with the experiment: what is left after 1 and 2 is real disagreement.
"""
import math

import numpy as np
import pytest

import spin73 as s
from fit_B import regressors
from spin73.data.xb_read import XB
from cmq_spin73 import cmq
import conversions as cv
from data_cal030 import (A_SOUND, B_BALL_M1_HYPOTHESIS, DAMPING, GEOMETRY, PHYSICAL,
                         STABILITY)

GR = 7000.0                      # grains per pound
DIA = 0.300                      # inches
TWIST_CAL = 10.0 / DIA           # rifling twist of 10 inches, in calibers

# inertia used by the report to compute each K_M
INERTIA_OF_KM = {"Tracer M1": "Tracer M1 mean"}


def cma_from_stability_factor(name, S, V, mach=None, B=None):
    """Inverts s_g (the SPIN-73 formula) to get the CMα implied by the measured S.

    When the Mach is printed, the temperature of the series comes from a = V/M and gives the
    density; without it, the standard atmosphere (59 °F) is used and the uncertainty is a few
    percent.
    """
    f = PHYSICAL[INERTIA_OF_KM.get(name, name)]
    TF = (V / mach / 49.04) ** 2 - 459.6 if mach else 59.0
    rho = s.air_density(TF)
    d = DIA / 12
    Ix = f["A"] / GR / (s.G_FT * 144)
    Iy = (B or f["B"]) / GR / (s.G_FT * 144)
    P = V * 2 * math.pi / (TWIST_CAL * d)
    return 2 * Ix ** 2 * P ** 2 / (math.pi * rho * Iy * S * d ** 3 * V ** 2)


def km_ratio(row, B=None):
    name, _, _, V, M, S, K_M = row
    return cma_from_stability_factor(name, S, V, M, B) / cv.cma_from_km(K_M)


def curve(name, f):
    return [f(GEOMETRY[name], j, m) for j, m in enumerate(s.MACH_GRID)]


def cna_spin(name, M):
    return float(np.interp(M, s.MACH_GRID, curve(
        name, lambda g, j, m: np.array(regressors(g["VL"], g["VN"], g["VB"], g["OR"], m)) @ XB[:, j])))


def cmq_spin(name, M):
    vcg = GEOMETRY[name]["VL"] - PHYSICAL[name]["g"]
    return float(np.interp(M, s.MACH_GRID, curve(name, lambda g, j, m: cmq(g["VL"], vcg, g["VB"], j))))


def damping(name):
    return [l for l in DAMPING if l[0] == name][0]


# ------------------------------------------------------------ 1. identities of the source
@pytest.mark.parametrize("name", ["Ball M1", "Ball M2", "A.P. M2", "Tracer M1"])
def test_sketch_closes_by_the_sum_of_the_parts(name):
    g = GEOMETRY[name]
    assert abs(g["VB"] + g["cylinder"] + g["VN"] - g["VL"]) < 1e-9 or \
        abs(g["cylinder"] + g["VN"] - g["VL"]) < 1e-9


ROWS_OK = [l for l in STABILITY if l[0] in ("Ball M2", "Tracer M1", "Frangible M22")]


@pytest.mark.parametrize("row", ROWS_OK, ids=lambda l: l[0])
def test_km_consistent_with_s(row):
    """Verified reading: K_M, S, velocity and inertias close within ±3 %."""
    assert abs(km_ratio(row) - 1) < 0.03


def test_ap_m2_within_the_temperature_uncertainty():
    """4 %: the Mach is not printed, so the series' temperature is unknown; ±20 °F already
    explains it. It is not treated as a reading error."""
    row = [l for l in STABILITY if l[0] == "A.P. M2"][0]
    assert abs(km_ratio(row) - 1) < 0.06


def test_ball_m1_inconsistent_in_the_source():
    """The three series of the Ball M1 violate the identity in the SAME direction, with the
    cell B = 16.40 reread and unambiguous. It is an inconsistency of the report, not of the
    transcription. The hypothetical B of 18.40 reconciles the three series."""
    rows = [l for l in STABILITY if l[0] == "Ball M1"]
    printed = [km_ratio(l) for l in rows]
    hypothesis = [km_ratio(l, B=B_BALL_M1_HYPOTHESIS) for l in rows]
    assert all(1.08 < r < 1.13 for r in printed), printed
    assert all(abs(r - 1) < 0.035 for r in hypothesis), hypothesis


# ------------------------------------------------------------ 2 and 3. SPIN-73 x experiment
def test_cmq_ball_m2():
    """Flat base, Mach 2.49: 3 %. Also pins the factor 2 of −(16/π)·K_H."""
    name, _, V, _, K_H, _ = damping("Ball M2")
    r = cmq_spin(name, V / A_SOUND) / cv.cmq_from_kh(K_H)
    assert abs(r - 1) < 0.05, r
    assert abs(r * 2 - 1) > 0.8          # without the factor 2, it would miss by almost double


def test_cmq_tracer_m1():
    """Flat base, Mach 2.46: the model is 10 % below the measured value."""
    name, _, V, _, K_H, _ = damping("Tracer M1")
    r = cmq_spin(name, V / A_SOUND) / cv.cmq_from_kh(K_H)
    assert 0.85 < r < 0.95, r


def test_cmq_ball_m1_boattail_records_disagreement():
    """0.81 cal boattail: the model damps 25 % less than measured. The F8·VB term of SPIN-73
    takes ~7.5 units of Cmq off this projectile; without the boattail it would give ~−21."""
    name, _, V, _, K_H, _ = damping("Ball M1")
    r = cmq_spin(name, V / A_SOUND) / cv.cmq_from_kh(K_H)
    assert 0.70 < r < 0.80, r


def test_kl_ball_m2_implies_the_drag_of_the_plot():
    """K_L = (π/8)(CNα − CX): implied CX 0.42 against ~0.38 from the plot on p. 19."""
    name, _, V, K_L, _, _ = damping("Ball M2")
    cx = cna_spin(name, V / A_SOUND) - K_L / cv.PI_8
    assert 0.33 < cx < 0.48, cx


def test_kl_tracer_m1_low_drag():
    """Implied CX 0.19: low for a flat base, but in the expected direction for a tracer, whose
    burning at the base reduces the base drag. Recorded, not validated."""
    name, _, V, K_L, _, _ = damping("Tracer M1")
    cx = cna_spin(name, V / A_SOUND) - K_L / cv.PI_8
    assert 0.10 < cx < 0.30, cx


def test_kl_ball_m1_records_disagreement():
    """An implied CX of 0.91 is impossible at Mach 2.4: for the boattailed Ball M1, the SPIN-73
    CNα (2.87) is ~0.5 larger than the measured K_L allows. Together with the Cmq (−25 %) and the
    internal inconsistency of the source, the Ball M1 is the least reliable point of the section."""
    name, _, V, K_L, _, _ = damping("Ball M1")
    cx = cna_spin(name, V / A_SOUND) - K_L / cv.PI_8
    assert cx > 0.7, cx


def test_hitchcock_formula_close_to_the_measured_cp():
    """Ball M2: the 1947 formula and the CP implied by the experiment agree within ~0.06 cal."""
    row = [l for l in STABILITY if l[0] == "Ball M2"][0]
    name, _, _, V, _, S, _ = row
    g = GEOMETRY[name]
    vcg = g["VL"] - PHYSICAL[name]["g"]
    cpn_measured = vcg - cma_from_stability_factor(name, S, V) / cna_spin(name, V / A_SOUND)
    h = cv.h_hitchcock(0, 0, g["cylinder"], g["VN"], g["OR"])
    assert abs(cv.from_nose(g["VL"], h) - cpn_measured) < 0.10


def test_cma_records_disagreement():
    """Model CMα / (8/π)·K_M, with an assumed DM = 0.12: Frangible M22 −1 % (Mach 1.23, no
    decided XC cell), Tracer M1 +5 % (apparent K_M, mean CG), Ball M2 +20 %, A.P. M2 −34 %.
    Between Mach 2 and 3 the CPN uses the XC1 of Mach 2.5 decided by the 1973 tables."""
    import compare_cma_cal030 as ca

    r = {name: ca.model(g, vcg, M)[1] / meas for name, M, g, vcg, meas in ca.rows()
         if name != "Ball M1"}
    assert abs(r["Frangible M22"] - 1) < 0.03, r
    assert 1.0 < r["Tracer M1"] < 1.1, r
    assert 1.15 < r["Ball M2"] < 1.25, r
    assert 0.6 < r["A.P. M2"] < 0.7, r
