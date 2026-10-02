"""Optional input additions: mass estimate (spin73.mass) and units (spin73.units)."""
import math

import numpy as np
import pytest

import spin73
from spin73 import mass, units


def test_integrals_match_the_analytic_cone_cylinder():
    """Sharp cone + cylinder: closed formulas for volume, CG and inertias."""
    VN, Lc, R = 2.0, 1.5, 0.5
    p = spin73.Projectile(VL=VN + Lc, VN=VN, VB=0.0, OR=1000.0, DM=0.0)
    I, _ = mass.integrals(p)
    v1, v2 = math.pi * R * R * VN / 3, math.pi * R * R * Lc
    x1, x2 = 0.75 * VN, VN + Lc / 2
    V = v1 + v2
    xcg = (v1 * x1 + v2 * x2) / V
    Ix = 0.3 * v1 * R * R + 0.5 * v2 * R * R
    Iy = (v1 * (3 / 20 * R * R + 3 / 80 * VN * VN) + v1 * (x1 - xcg) ** 2
          + v2 * (3 * R * R + Lc * Lc) / 12 + v2 * (x2 - xcg) ** 2)
    for k, v in (("V", V), ("xcg", xcg), ("Jx", Ix), ("Jy", Iy)):
        assert I[k] == pytest.approx(v, rel=1e-6), k


def test_tangent_ogive_reaches_the_shoulder_without_a_corner():
    """With OR = VN² + 0.25 (tangent, no meplat), the arc reaches the shoulder with radius 0.5."""
    p = spin73.Projectile(VL=5.0, VN=2.0, VB=0.0, OR=2.0 ** 2 + 0.25, DM=0.0)
    pieces, notes = mass.contour(p)
    a, b, f = pieces[0]
    r = f(np.array([0.0, 1.0, 1.999, 2.0]))
    assert r[0] == pytest.approx(0.0, abs=1e-9) and r[-1] == pytest.approx(0.5, abs=1e-9)
    assert r[-2] == pytest.approx(0.5, abs=1e-6)          # tangent: almost 0.5 before the shoulder
    assert not notes


def test_hitchcock_formulas():
    p = spin73.Projectile(VL=4.0, VN=2.0, VB=0.4, OR=8.0)
    pm = mass.estimate(p, "bullet", mass_g=10.0, d_mm=7.82)
    m, d, L = 0.010, 7.82e-3, 4.0 * 7.82e-3
    assert pm.cg_base == pytest.approx(0.400 * 4.0)
    assert pm.ix == pytest.approx(0.115 * m * d * d)
    assert pm.iy == pytest.approx(0.5 * 0.115 * m * d * d + 0.0543 * m * L * L)
    pg = mass.estimate(p, "shell", mass_g=10.0, d_mm=7.82)
    assert pg.cg_base == pytest.approx(0.375 * 4.0) and pg.ix == pytest.approx(0.140 * m * d * d)
    with pytest.raises(ValueError):
        mass.estimate(p, "bullet", d_mm=7.82)                # no mass


def test_complete_does_not_replace_what_was_given():
    p = spin73.Projectile(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12, DIA=0.224, WGT=4.05 / 453.59237,
                          IX=1.0)                             # given IX (even an absurd one) stays
    q = mass.complete(p, "solid")
    assert q.IX == 1.0 and q.WGT == p.WGT
    assert q.VCG is not None and q.IY > 0
    assert mass.missing(q) == []


def test_cg_only_without_diameter_and_mass_from_density():
    p = spin73.Projectile(VL=4.05, VN=1.90, VB=0.40, OR=7.9)
    pm = mass.estimate(p)
    assert pm.mass_kg is None and 2.0 < pm.cg_nose < 3.0
    q = mass.complete(p)                                      # VCG only
    assert q.VCG == pytest.approx(pm.cg_nose) and q.WGT == 0 and q.DIA == 0
    r = mass.complete(p, material="lead", d_mm=5.69)          # mass from the density
    V = mass.integrals(p)[0]["V"] * (5.69e-3) ** 3
    assert r.WGT * 0.45359237 == pytest.approx(11340 * V)
    assert r.DIA == pytest.approx(5.69 / 25.4)


def test_validation_keeps_the_documented_ranges():
    """The error ranges written in spin73/mass.py come from scripts/mass/validate.py."""
    import validate
    res = validate.evaluate()
    bullets = [r for r in res if r["kind"] == "bullet"]
    shells = [r for r in res if r["kind"] == "shell"]
    assert len(bullets) == 6 and len(shells) == 6
    assert all(0.94 < r["solid"]["ix"] < 1.04 for r in bullets)
    assert all(abs(r["solid"]["cg"] - r["cg_meas"]) <= 0.125 for r in bullets)
    assert all(0.88 < r["hitchcock"]["ix"] < 1.04 for r in shells)
    assert all(r["solid"]["ix"] < 0.82 for r in shells)       # wall: the solid underestimates


def test_units_convert_to_the_card():
    p = units.projectile(VL=4.05, VN=1.90, VB=0.40, D_MM=5.69, MASS_G=4.05, IX_GCM2=0.1426,
                         IY_GCM2=1.150, TWIST_MM=177.8, TEMP_C=15.0, CG_BASE=1.54)
    assert p.DIA == pytest.approx(5.69 / 25.4)
    assert p.WGT == pytest.approx(4.05 / 453.59237)
    assert p.IX == pytest.approx(0.1426 / 2926.397, rel=1e-6)
    assert p.TWIST == pytest.approx(177.8 / 5.69)
    assert p.TEMP == pytest.approx(59.0)
    assert p.VCG == pytest.approx(4.05 - 1.54)
    q = units.projectile(vl=4.05, vn=1.9, vb=0.4, dia=0.224, twist_in=7)   # lower case
    assert q.TWIST == pytest.approx(7 / 0.224)
    with pytest.raises(ValueError):
        units.projectile(VL=4, VN=2, VB=0.4, DIA=0.224, D_MM=5.69)      # given twice
    with pytest.raises(ValueError):
        units.projectile(VL=4, VN=2, VB=0.4, XYZ=1)                      # unknown


def test_without_vcg_the_canonical_asks_for_the_cg():
    p = spin73.Projectile(VL=4.05, VN=1.90, VB=0.40)
    with pytest.raises(ValueError, match="VCG"):
        spin73.table(p)


def _cli(args, capsys):
    spin73.cli.main(args)
    return capsys.readouterr().out


def test_cli_canonical_and_with_additions(capsys, tmp_path):
    out = _cli(["--example"], capsys)
    assert "Mode: canonical (1973 SPIN-73)" in out and "STABILITY ANALYSIS" in out
    out = _cli(["--VL", "4.05", "--VN", "1.90", "--VB", "0.40", "--OR", "7.9", "--d-mm", "5.69",
                "--mass-g", "4.05", "--twist-mm", "177.8", "--estimate-mass"], capsys)
    assert "mass estimated (solid: VCG, IX, IY)" in out and "STABILITY ANALYSIS" in out
    path = tmp_path / "bullet.txt"
    path.write_text("VL = 4.05\nVN = 1.90\nVB = 0.40\nOR = 7.9\nD_MM = 5.69\nMASS_G = 4.05\n"
                    "TWIST_IN = 7\nESTIMATE_MASS = bullet\n", encoding="utf-8")
    out = _cli(["--input", str(path)], capsys)
    assert "mass estimated (bullet: VCG, IX, IY)" in out
    out = _cli(["--input", str(path), "--DIA", "0.2240"], capsys)   # the line replaces the file
    assert "mass estimated (bullet" in out


def test_cli_without_vcg_without_estimate_is_an_error(capsys):
    with pytest.raises(SystemExit):
        spin73.cli.main(["--VL", "4.05", "--VN", "1.90", "--VB", "0.40"])
    assert "--estimate-mass" in capsys.readouterr().err
