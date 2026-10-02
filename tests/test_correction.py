"""Empirical correction: data, validation and application."""
import json

import numpy as np
import pytest

import fit_correction as fc
import apply_correction
import flight_data
from spin73.corrections import reynolds as rn
from spin73.corrections.free_flight import FILE
import spin73 as s


@pytest.fixture(scope="module")
def ls():
    return flight_data.rows()


def test_identity_checks_transcription_and_conventions(ls):
    """CMα = (VCG − CPN)·CNα with the MEASURED values of the same round. Catches a CLα taken for
    CNα, a CPN taken from the nose instead of the base, or a misread digit."""
    n, bad = flight_data.cma_identity(ls)
    assert n >= 70 and len(bad) <= 2, bad


def test_groups_in_each_coefficient(ls):
    """Every group in CX0; the T203 (OR not dimensioned) only in CX0."""
    assert {l["group"] for l in ls if l["coef"] == "CX0"} == set(fc.GROUPS)
    for c in ("CNA", "CMA"):
        assert {l["group"] for l in ls if l["coef"] == c} == set(fc.GROUPS) - {"t203"}


def test_new_sources_by_the_identity():
    """7.62 match and 30 mm: CMα = (CPN − CG)·(CLα + CD) with each round's values, within 2 %.
    Catches a misread digit and a CG swapped between projectiles."""
    by = {}
    for l in flight_data.rows():
        if l["group"] in ("762m", "30"):
            by.setdefault((l["proj"], round(l["M"], 4)), {})[l["coef"]] = l
    n = 0
    for d in by.values():
        if all(c in d for c in ("CMA", "CPN", "CNA")):
            n += 1
            pred = (d["CMA"]["geo"]["VCG"] - d["CPN"]["meas"]) * d["CNA"]["meas"]
            assert abs(pred / d["CMA"]["meas"] - 1) < 0.02, d["CMA"]["proj"]
    assert n >= 70


def test_t203_cx0_close_to_spin73(ls):
    """The T203 is the M437 under development, and SPIN-73 was calibrated on that family: CX0 within 5 %."""
    L = [l for l in ls if l["group"] == "t203"]
    assert len(L) >= 12 and all(abs(l["meas"] / l["spin"] - 1) < 0.05 for l in L)


def test_reynolds_zero_at_the_reference_scale():
    """With the projectile at the reference size, the friction correction is zero."""
    VL, d_mm = 5.0, 60.0
    assert abs(rn.delta_cx0(2.0, VL, 2.5, 0.4, 8.0, 0.12, d_mm, VL * d_mm / 1000)) < 1e-12


def test_reynolds_sign():
    """Smaller than the reference -> more friction (ΔCX0 > 0); larger -> less."""
    assert rn.delta_cx0(2.0, 4.0, 2.0, 0.4, 8.0, 0.12, 5.56, 0.3) > 0
    assert rn.delta_cx0(2.0, 4.5, 2.4, 0.4, 10.0, 0.1, 155.0, 0.3) < 0


def test_cx0_correction_generalizes(ls):
    """Nested cross-validation: in the three regimes the error on unseen groups drops."""
    for reg, (b, c, n, det) in fc.validate(ls, "CX0").items():
        assert c < b, reg


def test_json_reproduces_the_fit(ls):
    with open(FILE, encoding="utf-8") as f:
        saved = json.load(f)
    new = fc.final_fit(ls)
    for c in fc.APPLIED:
        for reg, d in new[c].items():
            assert (d["coef"] is None) == (saved[c][reg]["coef"] is None), (c, reg)
            if d["coef"]:
                assert np.allclose(d["coef"][:2], saved[c][reg]["coef"][:2]), (c, reg)


def test_only_what_was_accepted_enters():
    with open(FILE, encoding="utf-8") as f:
        saved = json.load(f)
    for c, regs in saved.items():
        for reg, d in regs.items():
            assert (d["coef"] is not None) == d["validation"]["accepted"], (c, reg)


def test_corrected_table_consistent():
    p = s.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DM=0.12, BD=1.00)
    t, c = s.table(p), apply_correction.corrected_table(p, d_mm=5.69)
    assert np.allclose(c["CMA"], t["CMA"])                     # CMα is not corrected
    assert np.allclose(c["CPN"], p.VCG - c["CMA"] / c["CNA"])  # consistent CPN
    assert np.allclose(c["CX2"] + c["CNA"], t["CX2"] + t["CNA"])   # yaw drag untouched
    assert np.all(c["CX"] > t["CX"])                           # small bullet: more friction


def test_corrected_table_requires_scale():
    p = s.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51)
    with pytest.raises(ValueError):
        apply_correction.corrected_table(p)


def test_stability_recomputed():
    c = apply_correction.corrected_table(s.M437)
    t = s.table(s.M437)
    assert "GYRO" in c and np.all(np.isfinite(c["GYRO"]))
    assert np.allclose(c["GYRO"], t["GYRO"] * t["CMA"] / c["CMA"])   # s_g ∝ 1/CMα
