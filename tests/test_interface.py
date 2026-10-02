"""Command line, input reading and CSV writing."""
import csv

import numpy as np

import paths
import spin73 as s


def test_input_file_equal_to_the_example():
    p = s.read_card(paths.EXAMPLES / "inputs" / "m437.txt")
    for field in ("VL", "VN", "VB", "VCG", "DM", "BD", "OR", "DIA", "IX", "IY", "WGT", "TWIST"):
        assert getattr(p, field) == getattr(s.M437, field), field


def test_csv_has_every_column(tmp_path):
    t = s.table(s.M437)
    path = tmp_path / "m437.csv"
    s.save_csv(t, str(path))
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 17
    expected = ["MACH"] + [n for n, _ in s.AERO_COLUMNS] + [n for n, _ in s.STAB_COLUMNS]
    assert list(rows[0].keys()) == expected
    assert float(rows[8]["CX"]) == np.round(t["CX"][8], 6)


def test_command_line(capsys):
    s._main(["--VL", "5.0", "--VN", "2.0", "--VB", "0", "--VCG", "3.04", "--OR", "8"])
    out = capsys.readouterr().out
    assert "AERODYNAMIC COEFFICIENTS" in out
    assert "STABILITY ANALYSIS" not in out          # no inertias, no stability
    assert "WARNINGS" in out


def test_warnings_depend_on_the_geometry():
    short = s.Projectile(VL=5.0, VN=2.0, VB=0.0, VCG=3.0)
    long = s.Projectile(VL=9.0, VN=3.5, VB=1.2, VCG=5.0)
    assert len(s.geometry_warnings(long)) > len(s.geometry_warnings(short))
    assert any("Ogive > 3" in a for a in s.geometry_warnings(long))
