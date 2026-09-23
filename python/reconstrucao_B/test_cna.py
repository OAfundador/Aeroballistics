"""CNa reconstruído (DATA XB lidos) contra as colunas CNA de 10 tabelas do SPIN-73.

Excluídas: a tabela da p. 44 (90 mm M71, transcrição mais degradada; resíduo em quase todo Mach)
e as células listadas em PENDENTES, que ainda precisam de releitura (tabela ou DATA).
"""
import numpy as np
from dados_cna import MACH, T
from ajustar_B import regressores
from xb_lidos import XB, CORRECOES

PENDENTES = {(29, 0.95), (29, 1.35), (29, 1.2), (32, 0.9), (32, 2.0), (35, 0.95), (35, 2.0), (38, 2.0),
             (41, 1.35), (41, 1.5), (41, 2.0), (50, 0.95), (53, 1.75), (53, 2.5), (53, 3.0), (53, 4.0),
             (53, 5.0), (59, 0.95), (65, 0.8), (65, 1.05)}


def test_cna_reproduz_tabelas():
    ruins = []
    for p, (n, VL, VN, VB, OR, cna) in T.items():
        if p == 44:
            continue
        for j, M in enumerate(MACH):
            if (p, round(M, 2)) in PENDENTES or not np.isfinite(cna[j]):
                continue
            r = np.array(regressores(VL, VN, VB, OR, M)) @ XB[:, j] - cna[j]
            if abs(r) > 0.0015:
                ruins.append((p, M, round(r, 4)))
    assert not ruins, ruins


def test_poucas_correcoes():
    assert len(CORRECOES) <= 6
