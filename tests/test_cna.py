"""CNa adaptado (DATA XB lidos) contra as colunas CNA de 10 tabelas do SPIN-73.

Excluídas: a tabela da p. 44 (90 mm M71, transcrição mais degradada; resíduo em quase todo Mach)
e as células listadas em PENDENTES, que ainda precisam de releitura (tabela ou DATA).
"""
import numpy as np
from dados_cna import MACH, T
from ajustar_B import regressores
from aeroballistics.dados.xb_lidos import XB, CORRECOES
from cna_spin73 import cna_j

# (32, 2.0): impresso 2.?54, par 6/8 (com 2.864 fecharia). (38, 2.0) decidiu o XB3 de Mach
# 2,0 e sai por circularidade, não por pendência (ver CIRCULARES).
# O 5"/38 de Mach 1,75 a 5 fechou com o cartão C205 (CNBT positivo zerado; NOTAS, T15).
PENDENTES = {(29, 0.95), (29, 1.2), (32, 0.9), (32, 2.0), (35, 0.95),
             (41, 1.35), (41, 1.5), (50, 0.95), (59, 0.95), (65, 0.8), (65, 1.05)}
CIRCULARES = {(38, 2.0)}


def test_cna_reproduz_tabelas():
    ruins = []
    for p, (n, VL, VN, VB, OR, cna) in T.items():
        if p == 44:
            continue
        for j, M in enumerate(MACH):
            if (p, round(M, 2)) in PENDENTES | CIRCULARES or not np.isfinite(cna[j]):
                continue
            r = cna_j(VL, VN, VB, OR, j) - cna[j]
            if abs(r) > 0.0015:
                ruins.append((p, M, round(r, 4)))
    assert not ruins, ruins


def test_poucas_correcoes():
    """Seis correções decididas pela contagem nas 10 tabelas e uma (XB3, Mach 2,0) por uma
    tabela só, com duas outras conferindo. Um limite contra o ajuste fino de DATA."""
    assert len(CORRECOES) <= 7


def test_c205_fecha_o_5_38_supersonico():
    """Sem a regra do cartão C205, o 5"/38 fica 0,014 acima de Mach 2,5 a 5."""
    n, VL, VN, VB, OR, cna = T[53]
    for j in (11, 13, 14, 15, 16):
        assert abs(cna_j(VL, VN, VB, OR, j) - cna[j]) <= 0.0015, j
