"""CPN e CMα reconstruídos contra três tabelas impressas do SPIN-73 com boattail.

175 mm M437 (p. 65, boattail 1,00 cal), 5"/38 NAVY (p. 53, 0,35 cal) e 105 mm XM380E5
(p. 50, 0,59 cal). As geometrias dão pesos bem diferentes aos coeficientes de boattail
(C12..C16), então uma leitura errada em C1..C11 não pode se disfarçar de erro em
C12..C16, nem o contrário. O XM380E5 não decidiu nenhum XC: é teste em todos os Mach.

Usa o CNα IMPRESSO de cada tabela (ver cpn_spin73.cpn_cma): sem isso, o erro do CNα
reconstruído entra no resíduo do CPN multiplicado por ~3.
"""
import os
import sys

import numpy as np
import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, ".."), os.path.join(AQUI, "..", "reconstrucao_B")]

import spin73 as s                                        # noqa: E402
import tabelas_impressas as ti                            # noqa: E402
from cpn_spin73 import cpn_cma                            # noqa: E402
from dados_cna import T as T_CNA                          # noqa: E402
from dados_cpn import CPN_538, POR_IDENTIDADE             # noqa: E402
from xc_lidos import CORRECOES, DECIDIDOS_M437, RECUPERADOS  # noqa: E402

TAB437 = s.ler_tabela(os.path.join(AQUI, "..", "m437_tabela.csv"))
TAB380 = ti.carregar(50).colunas
GEO = {  # (VL, VN, VB, OR, DM, VCG), CNα impresso, CPN impresso
    "M437": ((5.51, 2.91, 1.00, 25.0, 0.079, 3.50), TAB437["CNA"], TAB437["CPN"]),
    "5/38": ((4.59, 2.15, 0.35, 5.3, 0.100, 2.71), np.array(T_CNA[53][5], float),
             np.array([POR_IDENTIDADE.get(j, CPN_538[j]) for j in range(17)])),
    "XM380E5": ((5.58, 2.90, 0.59, 18.6, 0.130, 3.34), TAB380["CNA"], TAB380["CPN"]),
}

# Mach em que algum XC foi decidido com a própria tabela (xc_lidos.py).
_POR = {"M437": set(), "5/38": set()}
for (_l, _j) in CORRECOES:
    _POR["M437"].add(_j)
    if (_l, _j) in {(12, 6), (1, 2), (12, 1), (12, 9), (12, 10)}:   # decididas com as duas
        _POR["5/38"].add(_j)
for (_l, _j) in RECUPERADOS:
    _POR["M437"].add(_j); _POR["5/38"].add(_j)
for (_l, _j) in DECIDIDOS_M437:
    _POR["M437"].add(_j)
CIRCULARES = {"M437": _POR["M437"], "5/38": _POR["5/38"], "XM380E5": set()}

PENDENTES = {
    "M437": {},
    "5/38": {
        # Mach 1,75 e 2,5 a 5 fecharam com o cartão C205 (NOTAS, T15).
        15: "Mach 4: +0,0023 com o XC15 constante de 2,5 a 5 (o M437 pedia -0,9211 ali)",
    },
    "XM380E5": {
        1: "Mach 0,6: +0,0019 (o M437 tem +0,0044, circular); nenhum coeficiente isolado "
           "explica as três tabelas (NOTAS, T13)",
    },
}


def _cpn(nome, j):
    geo, cna, _ = GEO[nome]
    return cpn_cma(*geo, j, cna_impresso=cna[j])[0]


CASOS = [(n, j) for n in GEO for j in range(17)
         if np.isfinite(GEO[n][2][j]) and j not in CIRCULARES[n] and j not in PENDENTES[n]]


@pytest.mark.parametrize("nome,j", CASOS)
def test_cpn(nome, j):
    assert abs(_cpn(nome, j) - GEO[nome][2][j]) <= 0.0015


@pytest.mark.parametrize("nome", ["5/38", "XM380E5"])
def test_pendencias_ainda_pendentes(nome):
    resolvidas = [j for j in PENDENTES[nome] if abs(_cpn(nome, j) - GEO[nome][2][j]) <= 0.0015]
    assert not resolvidas, (nome, resolvidas)


def test_xm380e5_e_teste_em_todo_mach():
    """A terceira tabela não decidiu nenhum XC: fica independente em 16 dos 17 Mach."""
    assert sum(1 for n, _ in CASOS if n == "XM380E5") == 16


def test_cma_do_m437():
    """CMα = (VCG − CPN)·CNα: fecha onde o CPN fecha, com o arredondamento de 3 casas."""
    geo, cna, _ = GEO["M437"]
    for j in (n_j[1] for n_j in CASOS if n_j[0] == "M437"):
        cma = cpn_cma(*geo, j, cna_impresso=cna[j])[1]
        assert abs(cma - TAB437["CMA"][j]) <= 0.004, (j, cma, TAB437["CMA"][j])


def test_decisoes_fora_da_validacao():
    """Um valor decidido por uma tabela não pode ser 'validado' por ela."""
    assert 6 in CIRCULARES["M437"] and 6 in CIRCULARES["5/38"]      # XC12 em Mach 1,05
    assert 13 in CIRCULARES["M437"] and 13 not in CIRCULARES["5/38"]  # XC1 em Mach 2,5
    assert 5 in CIRCULARES["M437"]                                    # XC14 em Mach 1,0


def test_xc15_recuperado_reproduz_as_duas_tabelas():
    """Onde o XC15 foi recuperado pelo M437 e pelo 5"/38, as duas fecham."""
    for (_, j) in RECUPERADOS:
        for nome in ("M437", "5/38"):
            assert abs(_cpn(nome, j) - GEO[nome][2][j]) <= 0.0015, (nome, j)
