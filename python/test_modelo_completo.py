"""O programa inteiro, partindo SÓ da geometria, contra a tabela impressa do 175 mm M437.

Diferente de test_m437.py, que recalcula a estabilidade a partir dos coeficientes
impressos, aqui todos os coeficientes saem dos blocos DATA reconstruídos. Cada célula
que ainda não fecha está listada com o motivo; quando uma pendência for resolvida, o
teste acusa e ela deve sair da lista.
"""
import os

import numpy as np
import pytest

import spin73 as s

AQUI = os.path.dirname(os.path.abspath(__file__))
TAB = s.ler_tabela(os.path.join(AQUI, "m437_tabela.csv"))
T = s.tabela(s.M437)
MACH = [round(float(m), 2) for m in s.MACH_GRID]

# Mach em que algum DATA do CPN foi DECIDIDO usando esta mesma tabela (xc_lidos.py):
# XC12 em 0,6 e 1,05; XC1 em 0,8; XC15 em 1,2 e 2,0 (M437 + 5"/38) e de 1,35 a 5 (só M437).
# Nesses Mach o CPN do M437 e tudo que depende do CMα não podem validar nada.
_CIRC_CPN = (0.6, 0.8, 1.05, 1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0)
_DEPENDE_CMA = ("CPN", "CMA", "GYRO", "W1", "W2", "L1", "L2", "L15", "L25")
CIRCULARES = {(c, m) for c in _DEPENDE_CMA for m in _CIRC_CPN}

# (coluna, Mach) -> motivo. Células fora da tolerância que NÃO são circulares.
PENDENTES = {
    ("CNA", 0.8): "CNα reconstruído 0,0018 acima (reconstrucao_B, PENDENTES)",
    ("CNA", 1.05): "CNα reconstruído 0,0022 acima (reconstrucao_B, PENDENTES)",
    ("CPF5", 1.1): "célula impressa ambígua 4,23? (NOTAS, T2)",
    ("CMQ", 1.1): "algum XF mal lido em Mach 1,1 (reconstrucao_F, PENDENTE_M11)",
    ("CPN", 0.95): "o CNα reconstruído (0,001 abaixo) entra ~3x no CPN; com o CNα impresso "
                   "fecha em +0,0007 (reconstrucao_C/test_cpn.py)",
    ("CPN", 1.0): "só o M437 erra (+0,008); o 5\"/38 fecha (NOTAS, T6.1)",
    ("CMA", 1.0): "segue o CPN",
    ("GYRO", 1.0): "segue o CMα",
    ("CX2", 0.8): "célula impressa ambígua (2,6?3); o DATA XD pede 2,805 (NOTAS, T9)",
    ("CX2", 1.1): "célula impressa ilegível; o DATA XD dá 5,002 (NOTAS, T9)",
    ("CX2", 1.5): "resíduo de ~0,007 em aberto no M437 (o 5\"/38 fecha)",
    ("CX2", 1.75): "resíduo de ~0,009 em aberto no M437 (o 5\"/38 fecha)",
    ("CX2", 2.5): "XD2 em Mach 2,5 duvidoso",
    ("SBAR", 1.1): "herda o Cmq de Mach 1,1", ("SBAR5", 1.1): "herda o Cmq de Mach 1,1",
    ("SBAR", 1.75): "no limite do arredondamento",
}
# O CX2 subtrai o CNα reconstruído, então herda o erro dele (até 0,0022); tolerância maior.
# O RECIP = 1/(s_d(2−s_d)) amplifica ~100x o erro de s_d quando s_d ~ −0,07 (Mach 0,01 e 0,6).
TOL = {"CMA": 0.004, "CX2": 0.0045, "SPIN": 0.15, "W1": 0.05, "W2": 0.05, "RECIP": 0.08,
       "RECIP5": 0.003, **{c: 1.5e-6 for c in ("L1", "L2", "L15", "L25")}}
COLUNAS = ["CX", "CX2", "CNA", "CPN", "CMA", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CMQ", "CLP",
           "GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2", "L1", "L2", "L15", "L25"]


@pytest.mark.parametrize("col", COLUNAS)
def test_coluna_reproduz_a_tabela(col):
    ruins = []
    for j, M in enumerate(MACH):
        if (col, M) in PENDENTES or (col, M) in CIRCULARES:
            continue
        d = T[col][j] - TAB[col][j]
        if not (np.isfinite(d) and abs(d) <= TOL.get(col, 0.0015)):
            ruins.append((M, round(float(T[col][j]), 4), float(TAB[col][j])))
    assert not ruins, f"{col}: (Mach, calculado, impresso) {ruins}"


def test_pendencias_ainda_pendentes():
    """Se uma pendência passou a fechar, ela tem de sair da lista."""
    resolvidas = []
    for (col, M), motivo in PENDENTES.items():
        j = MACH.index(M)
        d = T[col][j] - TAB[col][j]
        if np.isfinite(d) and abs(d) <= TOL.get(col, 0.0015):
            resolvidas.append((col, M))
    assert not resolvidas, f"remova de PENDENTES: {resolvidas}"


def test_todas_as_colunas_saem_preenchidas():
    """Com todos os blocos DATA reconstruídos, nenhuma coluna sai NaN."""
    for col in COLUNAS:
        assert np.all(np.isfinite(T[col])), col


def test_circulares_nao_contam_como_verificadas():
    """Nenhuma célula circular pode aparecer também como pendente: ou é teste, ou não é."""
    assert not (set(PENDENTES) & CIRCULARES)
