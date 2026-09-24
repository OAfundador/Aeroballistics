"""Os sete coeficientes do examples/02_simulador_6dof.py (formulação vetorial de McCoy)."""
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

import caminhos
import aeroballistics


@pytest.fixture(scope="module")
def ex02():
    sys.path.insert(0, str(caminhos.EXEMPLOS))
    spec = importlib.util.spec_from_file_location("ex02", caminhos.EXEMPLOS / "02_simulador_6dof.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def aero():
    p = aeroballistics.unidades.ler_entrada(str(caminhos.EXEMPLOS / "entradas" / "5in38_navy.txt"))[0]
    return aeroballistics.Aerodinamica(p, convencao="moderna")


def test_em_alfa_zero_sao_os_da_convencao_moderna(ex02, aero):
    g = aeroballistics.MACH_GRID
    k = ex02.sete(aero, g, 0.0)
    pares = {"CD": "CD0", "CLA": "CLa", "CYP": "CNpa", "CNP": "Cmpa", "CLP": "Clp", "CMA": "Cma", "CMQ": "Cmq_Cmad"}
    for n, m in pares.items():
        np.testing.assert_allclose(k[n], aero.coeficiente(m, g), rtol=1e-12, atol=1e-15, err_msg=n)


def test_projecao_exata_dos_eixos_do_corpo_para_os_do_vento(ex02, aero):
    g = aeroballistics.MACH_GRID
    cx, cna = aero.coeficiente("CD0", g), aero.coeficiente("CNa", g)
    cx2 = aero.coeficiente("CDd2", g) - cna
    for graus in (2.0, 6.0, 10.0):
        a = np.radians(graus)
        s2 = np.sin(a) ** 2
        k = ex02.sete(aero, g, a)
        np.testing.assert_allclose(k["CD"], (cx + cx2 * s2) * np.cos(a) + cna * s2, rtol=1e-12)
        np.testing.assert_allclose(k["CLA"], cna * np.cos(a) - (cx + cx2 * s2), rtol=1e-12)
    # a guinada soma arrasto e tira inclinação da sustentação
    assert np.all(ex02.sete(aero, g, np.radians(5))["CD"] > ex02.sete(aero, g, 0.0)["CD"])
    assert np.all(ex02.sete(aero, g, np.radians(5))["CLA"] < ex02.sete(aero, g, 0.0)["CLA"])


def test_par_em_alfa(ex02, aero):
    for graus in (0.6, 3.0, 8.0):
        a = np.radians(graus)
        mais, menos = ex02.sete(aero, 1.5, a), ex02.sete(aero, 1.5, -a)
        for n in ("CD", "CLA", "CNP"):
            assert float(mais[n]) == pytest.approx(float(menos[n]), rel=1e-12)


def test_grade_tem_o_formato_das_grades_de_coeficientes(ex02, aero):
    g = ex02.grade(aero)
    assert g["mach_grid"].shape == (100,) and g["alpha_grid"].shape == (101,)
    assert g["alpha_grid"][0] == pytest.approx(-np.radians(10)) and g["alpha_grid"][50] == 0.0
    for n in ex02.SETE:
        forma = (100, 101) if n in ex02.DEPENDEM_DE_ALFA else (100,)
        assert g[n].shape == forma, n


def test_npz_gravado(tmp_path):
    r = subprocess.run([sys.executable, str(caminhos.EXEMPLOS / "02_simulador_6dof.py"),
                        "--entrada", str(caminhos.EXEMPLOS / "entradas" / "5in38_navy.txt"), "--npz"],
                       capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=caminhos.RAIZ)
    assert r.returncode == 0, r.stderr
    arquivo = caminhos.RAIZ / "output" / "exemplos" / "5_38_navy_sete.npz"
    with np.load(arquivo) as d:
        assert set(d.files) == {"mach_grid", "alpha_grid", "CD", "CLA", "CYP", "CNP", "CLP", "CMA", "CMQ"}
