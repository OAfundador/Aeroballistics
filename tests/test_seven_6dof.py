"""The seven coefficients of examples/02_6dof_simulator.py (McCoy's vector formulation)."""
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

import paths
import aeroballistics


@pytest.fixture(scope="module")
def ex02():
    sys.path.insert(0, str(paths.EXAMPLES))
    spec = importlib.util.spec_from_file_location("ex02", paths.EXAMPLES / "02_6dof_simulator.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def aero():
    p = aeroballistics.units.read_input(str(paths.EXAMPLES / "inputs" / "5in38_navy.txt"))[0]
    return aeroballistics.Aerodynamics(p, convention="modern")


def test_at_zero_alpha_they_are_the_modern_convention(ex02, aero):
    g = aeroballistics.MACH_GRID
    k = ex02.seven(aero, g, 0.0)
    pairs = {"CD": "CD0", "CLA": "CLa", "CYP": "CNpa", "CNP": "Cmpa", "CLP": "Clp", "CMA": "Cma", "CMQ": "Cmq_Cmad"}
    for n, m in pairs.items():
        np.testing.assert_allclose(k[n], aero.coefficient(m, g), rtol=1e-12, atol=1e-15, err_msg=n)


def test_exact_projection_from_body_to_wind_axes(ex02, aero):
    g = aeroballistics.MACH_GRID
    cx, cna = aero.coefficient("CD0", g), aero.coefficient("CNa", g)
    cx2 = aero.coefficient("CDd2", g) - cna
    for degrees in (2.0, 6.0, 10.0):
        a = np.radians(degrees)
        s2 = np.sin(a) ** 2
        k = ex02.seven(aero, g, a)
        np.testing.assert_allclose(k["CD"], (cx + cx2 * s2) * np.cos(a) + cna * s2, rtol=1e-12)
        np.testing.assert_allclose(k["CLA"], cna * np.cos(a) - (cx + cx2 * s2), rtol=1e-12)
    # yaw adds drag and takes slope away from the lift
    assert np.all(ex02.seven(aero, g, np.radians(5))["CD"] > ex02.seven(aero, g, 0.0)["CD"])
    assert np.all(ex02.seven(aero, g, np.radians(5))["CLA"] < ex02.seven(aero, g, 0.0)["CLA"])


def test_even_in_alpha(ex02, aero):
    for degrees in (0.6, 3.0, 8.0):
        a = np.radians(degrees)
        plus, minus = ex02.seven(aero, 1.5, a), ex02.seven(aero, 1.5, -a)
        for n in ("CD", "CLA", "CNP"):
            assert float(plus[n]) == pytest.approx(float(minus[n]), rel=1e-12)


def test_grid_has_the_shape_of_coefficient_grids(ex02, aero):
    g = ex02.grid(aero)
    assert g["mach_grid"].shape == (100,) and g["alpha_grid"].shape == (101,)
    assert g["alpha_grid"][0] == pytest.approx(-np.radians(10)) and g["alpha_grid"][50] == 0.0
    for n in ex02.SEVEN:
        shape = (100, 101) if n in ex02.DEPENDS_ON_ALPHA else (100,)
        assert g[n].shape == shape, n


def test_npz_written(tmp_path):
    r = subprocess.run([sys.executable, str(paths.EXAMPLES / "02_6dof_simulator.py"),
                        "--input", str(paths.EXAMPLES / "inputs" / "5in38_navy.txt"), "--npz"],
                       capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=paths.ROOT)
    assert r.returncode == 0, r.stderr
    path = paths.ROOT / "output" / "examples" / "5_38_navy_seven.npz"
    with np.load(path) as d:
        assert set(d.files) == {"mach_grid", "alpha_grid", "CD", "CLA", "CYP", "CNP", "CLP", "CMA", "CMQ"}
