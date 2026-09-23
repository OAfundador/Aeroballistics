"""CX2 reconstruído (DATA XD) contra duas tabelas: 175 mm M437 e 5"/38.

Usa o CNα IMPRESSO de cada tabela, porque a equação subtrai o CNα: assim o teste isola
o XD do erro do CNα reconstruído.
"""
import os
import sys

import numpy as np
import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, ".."), os.path.join(AQUI, "..", "reconstrucao_B")]

import spin73 as s                                             # noqa: E402
from dados_cna import T as T_CNA                               # noqa: E402
from dados_cx2 import CNA_SUSPEITO, CX2_538, DECIDIDAS, ILEGIVEIS   # noqa: E402
from xd_lidos import DECIDIDOS, XD                             # noqa: E402

TAB = s.ler_tabela(os.path.join(AQUI, "..", "m437_tabela.csv"))


def cx2(VL, VN, VB, OR, cna, j):
    CXCL = VL - VN - VB - 1.5
    CRAT = VN ** 2 / OR - 0.40
    return XD[0, j] + XD[1, j] * CXCL + XD[2, j] * CRAT + XD[3, j] * VB - cna


# M437: células que não conferem, com o motivo
M437_FORA = {2: "scan ambíguo 2,6?3; o DATA pede 2,805 (par 6/8)",
             7: "scan ilegível; o DATA dá 5,002",
             13: "XD2 em Mach 2,5 duvidoso (resíduo +0,020)"}
# Mach em que alguma célula do XD foi decidida pela própria tabela
CIRCULARES = {j for (_, j) in DECIDIDOS}


@pytest.mark.parametrize("j", [j for j in range(17) if j not in M437_FORA and j not in CIRCULARES])
def test_m437(j):
    calc = cx2(5.51, 2.91, 1.0, 25.0, TAB["CNA"][j], j)
    tol = 0.010 if j in (10, 11) else 0.0045          # 1,5 e 1,75: resíduo de ~0,008 em aberto
    assert abs(calc - TAB["CX2"][j]) <= tol, (j, calc, TAB["CX2"][j])


@pytest.mark.parametrize("j", [j for j in range(17) if j not in DECIDIDAS and j not in ILEGIVEIS
                               and j not in CNA_SUSPEITO and j not in CIRCULARES])
def test_5_38(j):
    cna = T_CNA[53][5][j]
    calc = cx2(4.59, 2.15, 0.35, 5.3, cna, j)
    assert abs(calc - CX2_538[j]) <= 0.0025, (j, calc, CX2_538[j])


def test_releitura_do_m437_em_1_05():
    """A transcrição antiga dizia 4,567; o scan relido diz 4,507, e o DATA dá o mesmo."""
    assert TAB["CX2"][6] == pytest.approx(4.507)
    assert abs(cx2(5.51, 2.91, 1.0, 25.0, TAB["CNA"][6], 6) - 4.507) < 0.0015
