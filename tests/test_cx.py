"""CX adaptado (DATA XA) contra duas tabelas: 175 mm M437 e 5"/38.

As duas geometrias dão ao XA2 pesos de sinal oposto (VNX − 2,5 = +0,41 e −0,35) e ao
XA7 pesos muito diferentes (boattail 1,00 e 0,35 cal), o que separa os coeficientes.
Mach 0,01 e 0,6 ficam fora: foram eles que decidiram XA1 e XA2 nesses pontos.
"""
import pytest

import caminhos
import aeroballistics as s
from dados_cx import CX_538
from aeroballistics.dados.xa_lidos import DECIDIDOS, XA

TAB = s.ler_tabela(caminhos.TABELAS_1973 / "m437_tabela.csv")
K = s.CoefAjuste(a=XA)
P538 = s.Projetil(VL=4.59, VN=2.15, VB=0.35, VCG=2.71, DM=0.100, BD=1.040, OR=5.3)
CIRCULARES = {j for (_, j) in DECIDIDOS}


@pytest.mark.parametrize("j", [j for j in range(17) if j not in CIRCULARES])
def test_m437(j):
    assert abs(s.cx(s.M437, K, j) - TAB["CX"][j]) <= 0.0015


@pytest.mark.parametrize("j", [j for j in range(17) if j not in CIRCULARES])
def test_5_38(j):
    assert abs(s.cx(P538, K, j) - CX_538[j]) <= 0.0015


def test_xa2_relido_em_mach_1_05():
    """−,0487 à primeira vista; −,0687 no zoom; as duas tabelas pediam −,0688."""
    assert XA[1, 6] == pytest.approx(-.0687)
