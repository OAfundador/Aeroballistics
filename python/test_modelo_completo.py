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

# (coluna, Mach) -> motivo
PENDENTES = {
    ("CNA", 0.8): "CNα reconstruído 0,0018 acima (reconstrucao_B, PENDENTES)",
    ("CNA", 1.05): "CNα reconstruído 0,0022 acima (reconstrucao_B, PENDENTES)",
    ("CPF5", 1.1): "célula impressa ambígua 4,23? (NOTAS, T2)",
    ("CMQ", 1.1): "algum XF mal lido em Mach 1,1 (reconstrucao_F, PENDENTE_M11)",
    **{("CPN", m): "XC12 desbotado / XC15 sem cartão (NOTAS, T6)"
       for m in (0.6, 0.8, 0.95, 1.0, 1.35, 1.5, 1.75, 2.5, 3.0, 4.0, 5.0)},
    **{("CMA", m): "segue o CPN" for m in (0.6, 0.8, 1.0, 1.35, 1.5, 1.75, 2.5, 3.0, 4.0, 5.0)},
    ("CX2", 0.8): "célula impressa ambígua (2,6?3); o DATA XD pede 2,805 (NOTAS, T9)",
    ("CX2", 1.1): "célula impressa ilegível; o DATA XD dá 5,002 (NOTAS, T9)",
    ("CX2", 1.5): "resíduo de ~0,007 em aberto no M437 (o 5\"/38 fecha)",
    ("CX2", 1.75): "resíduo de ~0,009 em aberto no M437 (o 5\"/38 fecha)",
    ("CX2", 2.5): "XD2 em Mach 2,5 duvidoso",
}
# O CX2 subtrai o CNα reconstruído, então herda o erro dele (até 0,0022); tolerância maior.
TOL = {"CMA": 0.004, "CX2": 0.0045}
COLUNAS = ["CNA", "CPN", "CMA", "CX2", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CMQ", "CLP"]


@pytest.mark.parametrize("col", COLUNAS)
def test_coluna_reproduz_a_tabela(col):
    ruins = []
    for j, M in enumerate(MACH):
        if (col, M) in PENDENTES:
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


def test_colunas_sem_data_saem_nan():
    """O CX depende do XA, ainda não lido: o programa não inventa valor."""
    assert np.all(np.isnan(T["CX"]))
