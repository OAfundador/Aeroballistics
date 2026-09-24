"""O programa inteiro, partindo SÓ da geometria, contra a tabela impressa do 175 mm M437.

Diferente de test_m437.py, que recalcula a estabilidade a partir dos coeficientes
impressos, aqui todos os coeficientes saem dos blocos DATA recuperados. Cada célula
que ainda não fecha está listada com o motivo; quando uma pendência for resolvida, o
teste acusa e ela deve sair da lista.
"""
import numpy as np
import pytest

import caminhos
import aeroballistics as s

TAB = s.ler_tabela(caminhos.TABELAS_1973 / "m437_tabela.csv")
T = s.tabela(s.M437)
MACH = [round(float(m), 2) for m in s.MACH_GRID]

# Mach em que algum DATA do CPN foi DECIDIDO usando esta mesma tabela (xc_lidos.py):
# XC12 em 0,6 e 1,05; XC1 em 0,8 e 2,5; XC14 em 1,0; XC15 em 1,2 a 2,0 (M437 + 5"/38, ou
# só M437 em 1,75) e de 2,5 a 5 (só M437). Nesses Mach o CPN do M437 e tudo que depende
# do CMα não podem validar nada.
_CIRC_CPN = (0.6, 0.8, 1.0, 1.05, 1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0)
_DEPENDE_CMA = ("CPN", "CMA", "GYRO", "W1", "W2", "L1", "L2", "L15", "L25", "DELT", "DISP")
CIRCULARES = {(c, m) for c in _DEPENDE_CMA for m in _CIRC_CPN}

# (coluna, Mach) -> motivo. Células fora da tolerância que NÃO são circulares.
PENDENTES = {
    ("CNA", 0.8): "CNα adaptado 0,0018 acima (test_cna.py, PENDENTES)",
    ("CNA", 1.05): "CNα adaptado 0,0022 acima (test_cna.py, PENDENTES)",
    ("CPF5", 1.1): "célula impressa ambígua 4,23? (NOTAS, T2)",
    ("CPN", 0.95): "o CNα adaptado (0,001 abaixo) entra ~3x no CPN; com o CNα impresso "
                   "fecha em +0,0007 (test_cpn.py)",
    ("CX2", 0.8): "célula impressa ambígua (2,6?3); o DATA XD pede 2,805 (NOTAS, T9)",
    ("CX2", 1.1): "célula impressa ilegível; o DATA XD dá 5,002 (NOTAS, T9)",
    ("CX2", 1.5): "resíduo de ~0,007 em aberto no M437 (o 5\"/38 fecha)",
    ("CX2", 1.75): "resíduo de ~0,009 em aberto no M437 (o 5\"/38 fecha)",
    ("CX2", 2.5): "resíduo de −0,030 no M437; o XD2 decidido pelo 5\"/38 fecha o XM380E5 "
                  "(mesmo peso), e o M437 quase não pesa no XD2 (test_cx2.py)",
    ("SBAR", 1.75): "no limite do arredondamento",
    # CNPA3 e CNPA5P: células resolvidas pela identidade CNPA3 + 0,1·CNPA5P = 3,75 (circulares
    # para a fórmula) ficam de fora; DELT e DISP em Mach 0,01 e 0,6 foram resolvidas pela
    # própria fórmula (pares 6/0 e 6/8).
}
CIRCULARES |= {("CNPA5P", 0.95), ("DELT", 0.01), ("DELT", 0.6)}
# O CX2 subtrai o CNα adaptado, então herda o erro dele (até 0,0022); tolerância maior.
# O RECIP = 1/(s_d(2−s_d)) amplifica ~100x o erro de s_d quando s_d ~ −0,07 (Mach 0,01 e 0,6).
TOL = {"CMA": 0.004, "CX2": 0.0045, "SPIN": 0.15, "W1": 0.05, "W2": 0.05, "RECIP": 0.08,
       "RECIP5": 0.003, **{c: 1.5e-6 for c in ("L1", "L2", "L15", "L25")},
       "CNPA3": 0.0015, "CNPA5P": 0.004, "DELT": 0.00015, "DISP": 0.0015}
COLUNAS = ["CX", "CX2", "CNA", "CPN", "CMA", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CMQ", "CLP",
           "GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2", "L1", "L2", "L15", "L25",
           "CNPA3", "CNPA5P", "DELT", "DISP"]


@pytest.mark.parametrize("col", COLUNAS)
def test_coluna_reproduz_a_tabela(col):
    ruins = []
    for j, M in enumerate(MACH):
        if (col, M) in PENDENTES or (col, M) in CIRCULARES:
            continue
        if not np.isfinite(TAB[col][j]):
            continue                       # célula ilegível na transcrição
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
    """Com todos os blocos DATA recuperados, nenhuma coluna sai NaN."""
    for col in COLUNAS:
        assert np.all(np.isfinite(T[col])), col


def test_circulares_nao_contam_como_verificadas():
    """Nenhuma célula circular pode aparecer também como pendente: ou é teste, ou não é."""
    assert not (set(PENDENTES) & CIRCULARES)
