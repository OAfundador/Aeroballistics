"""Validação contra a Tabela 14 do SPIN-73 (175 mm M437).

Rodar:  python -m pytest -v test_m437.py

Três níveis de teste:
  1. Consistência interna da transcrição (a tabela contra ela mesma).
  2. Análise de estabilidade recalculada contra as colunas impressas.
  3. Estrutura das equações empíricas (sem os DATA, só identidades).
"""
import os

import numpy as np
import pytest

import spin73 as s

AQUI = os.path.dirname(os.path.abspath(__file__))
TAB = s.ler_tabela(os.path.join(AQUI, "m437_tabela.csv"))
P = s.M437

# Leituras em que o scan era ambíguo (tipicamente 6/8, 1/3, 2/5 na impressão
# matricial) e que foram decididas por uma identidade independente -- ver
# NOTAS_TRANSCRICAO.md, seção T. Elas ficam FORA das comparações para que a
# validação não seja circular (o modelo não pode confirmar o que ajudou a decidir).
LEITURAS_DECIDIDAS = {
    ("CX", 0.01), ("CX", 0.60),        # 0.1?5 -> 0.105   (via SBAR)
    ("SPIN", 0.80),                    # 4?9.2 -> 489.2   (p proporcional a Mach)
    ("CPF5", 0.80), ("CPF5", 0.95),    # 4.23?/4.0?6      (via CNPA5 e CYPA)
    ("L1", 0.80),                      # -.000?42 -> -.000382 (via L1+L2)
    ("SBAR5", 1.35),                   # 1.?01 -> 1.201   (via RECIP5)
    ("L15", 1.10),                     # -.00016? -> -.000168 (via L15+L25)
    ("RECIP5", 1.05),                  # 1.06? -> 1.068   (via SBAR5)
}


def _mascara(*cols):
    return np.array([all((c, round(m, 2)) not in LEITURAS_DECIDIDAS for c in cols)
                     for m in TAB["MACH"]])


def _comparar(col, calc, atol=0.0, rtol=0.0, entradas=()):
    ok = _mascara(col, *entradas)
    ref = TAB[col][ok]
    got = np.asarray(calc)[ok]
    err = np.abs(got - ref)
    lim = atol + rtol * np.abs(ref)
    ruins = [(float(m), float(r), float(g)) for m, r, g, e, l in
             zip(TAB["MACH"][ok], ref, got, err, lim) if e > l]
    assert not ruins, f"{col}: (Mach, tabela, calculado) fora da tolerância: {ruins}"


# ---------------------------------------------------------------- nível 1
def test_consistencia_cma_cpn():
    """CMA = (VCG - CPN) * CNA, com CPN impresso em 3 casas."""
    calc = (P.VCG - TAB["CPN"]) * TAB["CNA"]
    _comparar("CMA", calc, atol=0.004, entradas=("CPN", "CNA"))


@pytest.mark.parametrize("cn, cp", [("CNPA", "CPF1"), ("CNPA5", "CPF5")])
def test_consistencia_magnus(cn, cp):
    """Cnpa = (VCG - CPF) * CYPA."""
    calc = (P.VCG - TAB[cp]) * TAB["CYPA"]
    _comparar(cn, calc, atol=0.002, entradas=(cp, "CYPA"))


@pytest.mark.parametrize("sb, rc", [("SBAR", "RECIP"), ("SBAR5", "RECIP5")])
def test_consistencia_recip(sb, rc):
    """RECIP = 1/(sd(2-sd)): limite de sg para estabilidade."""
    sd = TAB[sb]
    ok = _mascara(sb, rc)
    calc = 1.0 / (sd * (2.0 - sd))
    ref = TAB[rc]
    # sd com 3 casas perto de 1 amplifica pouco; perto de 0 amplifica muito
    tol = 0.002 + 0.02 * np.abs(ref) * (np.abs(sd) < 0.3)
    assert np.all(np.abs(calc - ref)[ok] <= tol[ok])


# ---------------------------------------------------------------- nível 2
@pytest.fixture(scope="module")
def est():
    return s.estabilidade(P, TAB["MACH"], TAB["CX"], TAB["CNA"], TAB["CMA"],
                          TAB["CNPA"], TAB["CNPA5"], TAB["CMQ"], TAB["CLP"])


ENTRADAS_EST = ("CX", "CNA", "CMA", "CNPA", "CNPA5", "CMQ", "CLP")


def test_spin(est):
    _comparar("SPIN", est["SPIN"], atol=0.15)


def test_gyro(est):
    # Resíduo sistemático de ~0,15 % (item A1 das NOTAS); tolerância cobre isso.
    _comparar("GYRO", est["GYRO"], atol=0.0015, rtol=0.003, entradas=ENTRADAS_EST)


@pytest.mark.parametrize("col", ["SBAR", "SBAR5"])
def test_sd(est, col):
    _comparar(col, est[col], atol=0.002, entradas=ENTRADAS_EST)


@pytest.mark.parametrize("col", ["W1", "W2"])
def test_frequencias(est, col):
    # propaga o resíduo de sg via sigma
    _comparar(col, est[col], atol=0.02, rtol=0.004, entradas=ENTRADAS_EST)


@pytest.mark.parametrize("col", ["L1", "L2", "L15", "L25"])
def test_amortecimento(est, col):
    _comparar(col, est[col], atol=1.5e-6, entradas=ENTRADAS_EST)


def test_formula_do_texto_nao_reproduz(est):
    """Registra o achado E1: com o sinal impresso no texto, L1/L2 não batem."""
    d = P.DIA / 12; m = P.WGT / s.G_FT
    Ix = P.IX / (s.G_FT * 144); Iy = P.IY / (s.G_FT * 144)
    K = s.densidade_ar(P.TEMP) * np.pi * d * d / 4 / (4 * m)
    sig = np.sqrt(1 - 1 / est["GYRO"])
    k1, k2 = m * d * d / Ix, m * d * d / Iy
    L1_texto = K * (-TAB["CNA"] * (1 + 1 / sig) + k2 / 2 * (1 + 1 / sig) * TAB["CMQ"]
                    + k1 / sig * TAB["CNPA"])
    ok = _mascara("L1")
    assert np.max(np.abs(L1_texto - TAB["L1"])[ok]) > 1e-4


# ---------------------------------------------------------------- nível 3
def test_sem_data_retorna_nan():
    c = s.coeficientes(P, s.CoefAjuste())
    assert all(np.all(np.isnan(v)) for k, v in c.items() if k != "MACH")


def test_identidades_estruturais():
    """Com coeficientes sintéticos, as relações algébricas do texto valem."""
    rng = np.random.default_rng(0)
    k = s.CoefAjuste(a=rng.normal(size=(13, 17)), B=rng.normal(size=(9, 17)) + 3,
                     C=rng.normal(size=(17, 17)), D=rng.normal(size=(4, 17)),
                     E=rng.normal(size=(4, 17)) - 1, F=rng.normal(size=(8, 17)),
                     G=rng.normal(size=(1, 17)))
    c = s.coeficientes(P, k)
    assert np.allclose(c["CMA"], (P.VCG - c["CPN"]) * c["CNA"])
    assert np.allclose(c["CNPA"], (P.VCG - c["CPF1"]) * c["CYPA"])
    assert np.allclose(c["CYPA"], k.E[0] * P.VL - 0.1 * P.VB)
    assert np.allclose(c["CLP"], k.G[0] * P.VL / 5.51)
