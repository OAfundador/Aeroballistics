"""CPN e CMα reconstruídos contra duas tabelas impressas do SPIN-73.

175 mm M437 (p. 65, boattail 1,00 cal) e 5"/38 NAVY (p. 53, boattail 0,35 cal). As duas
geometrias dão pesos bem diferentes aos coeficientes de boattail (C12..C16), então uma
leitura errada em C1..C11 não pode se disfarçar de erro em C12..C16, nem o contrário.

Usa o CNα IMPRESSO das duas tabelas (ver cpn_spin73.cpn_cma): sem isso, o erro do CNα
reconstruído entra no resíduo do CPN multiplicado por ~3.
"""
import os
import sys

import numpy as np
import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, ".."), os.path.join(AQUI, "..", "reconstrucao_B")]

import spin73 as s                                        # noqa: E402
from cpn_spin73 import cpn_cma                            # noqa: E402
from dados_cna import T as T_CNA                          # noqa: E402
from dados_cpn import CPN_538, POR_IDENTIDADE             # noqa: E402
from xc_lidos import AUSENTES, CORRECOES, RECUPERADOS     # noqa: E402

TAB437 = s.ler_tabela(os.path.join(AQUI, "..", "m437_tabela.csv"))
G437 = (s.M437.VL, s.M437.VN, s.M437.VB, s.M437.OR, s.M437.DM, s.M437.VCG)
G538 = (4.59, 2.15, 0.35, 5.3, 0.100, 2.710)
CNA437 = TAB437["CNA"]
CNA538 = np.array(T_CNA[53][5], float)

# Mach em que a conta fecha, por tabela. Mach 1,05 (índice 6) fica fora das duas: foi ele
# que decidiu o valor de XC12, então validá-lo aqui seria circular.
VER_437 = {0, 3, 4, 7}
VER_538 = {3, 5, 7}

PENDENTES = {
    0: 'XC12 ou a leitura do CPN do 5"/38 em Mach 0,01 (0,769 x 0,779): M437 fecha, 5"/38 erra +0,011',
    1: "XC12 em Mach 0,6 (linha desbotada): sem candidato único nas duas tabelas",
    2: "XC12 ou XC1 em Mach 0,8 (linha desbotada): sem candidato único",
    4: '5"/38: linha de Mach 0,95 ilegível na coluna CPN (o M437 fecha)',
    5: 'Mach 1,0: só o M437 erra (+0,008); o 5"/38 fecha. Algum coeficiente com peso alto '
       "só no boattail de 1,00 cal, ou a célula impressa do M437",
    6: "Mach 1,05: usado para decidir XC12 (circular por construção)",
    **{j: ("Mach recuperado pelas duas tabelas (XC15 decidido pelo modelo): circular"
           if (15, j) in RECUPERADOS else "XC15 sem cartão de continuação no listing")
       for j in AUSENTES[15]},
}


def _cpn(geo, cna, j):
    return cpn_cma(*geo, j, cna_impresso=cna[j])[0]


@pytest.mark.parametrize("j", sorted(VER_437))
def test_m437(j):
    assert abs(_cpn(G437, CNA437, j) - TAB437["CPN"][j]) <= 0.0015


@pytest.mark.parametrize("j", sorted(VER_538))
def test_5_38(j):
    ref = CPN_538[j] if np.isfinite(CPN_538[j]) else POR_IDENTIDADE[j]
    assert abs(_cpn(G538, CNA538, j) - ref) <= 0.0015


def test_cma_do_m437():
    """CMα = (VCG − CPN)·CNα: fecha onde o CPN fecha, com o arredondamento de 3 casas."""
    for j in sorted(VER_437):
        cma = cpn_cma(*G437, j, cna_impresso=CNA437[j])[1]
        assert abs(cma - TAB437["CMA"][j]) <= 0.004, (j, cma, TAB437["CMA"][j])


def test_xc12_decidido_fora_da_validacao():
    """O valor decidido em Mach 1,05 não pode ser 'validado' pelas tabelas que o decidiram."""
    assert (12, 6) in CORRECOES
    assert 6 in PENDENTES and 6 not in VER_437 and 6 not in VER_538


def test_xc15_recuperado_reproduz_as_duas_tabelas():
    """Onde o XC15 foi recuperado, as duas tabelas fecham (é o que define o valor)."""
    for (_, j) in RECUPERADOS:
        assert abs(_cpn(G437, CNA437, j) - TAB437["CPN"][j]) <= 0.0015, j
        assert abs(_cpn(G538, CNA538, j) - CPN_538[j]) <= 0.0015, j


def test_todo_mach_esta_classificado():
    for j in range(17):
        assert j in VER_437 or j in VER_538 or j in PENDENTES, j
