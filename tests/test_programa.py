"""aeroballistics.programa: o mapa orientado a objetos do programa original."""
import numpy as np
import pytest

import caminhos
import aeroballistics
from aeroballistics import nucleo
from aeroballistics.programa import SPIN73

DOC = caminhos.DOCS / "PROGRAMA_ORIGINAL.md"


def test_cada_coluna_impressa_tem_um_e_so_um_bloco():
    impressas = [n for n, _ in nucleo.COLUNAS_AERO + nucleo.COLUNAS_ESTAB]
    produzidas = [c for b in SPIN73 for c in b.colunas]
    assert sorted(produzidas) == sorted(impressas)
    for c in impressas:
        assert c in SPIN73.de_coluna(c).colunas


def test_implementacao_existe_e_statements_em_ordem():
    fim_anterior = 0
    for b in SPIN73:
        assert callable(b.funcao()), b.chave
        if b.statements and b.chave != "polinomio":      # C278-C281 vêm depois da estabilidade
            a, z = b.statements
            assert a <= z and a > fim_anterior, b.chave
            fim_anterior = z


def test_calcular_devolve_o_programa():
    t = aeroballistics.tabela(aeroballistics.M437)
    for b in SPIN73:
        if b.colunas:
            r = b.calcular(aeroballistics.M437)
            for c in b.colunas:
                assert np.allclose(r[c], t[c], equal_nan=True), (b.chave, c)


def test_regra_do_polinomio_de_magnus_vale_para_qualquer_projetil():
    """O bloco "polinomio" afirma CNPA3 + 0,1·CNPA5P = 3,75 sempre (defeito do original)."""
    for geo in (dict(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9),
                dict(VL=9.0, VN=2.0, VB=0.0, VCG=5.05, OR=8.0),
                dict(VL=5.51, VN=2.91, VB=1.0, VCG=3.5, OR=25.0)):
        t = aeroballistics.tabela(aeroballistics.Projetil(**geo))
        assert np.allclose(t["CNPA3"] + 0.1 * t["CNPA5P"], 3.75)


def test_documento_gerado_esta_em_dia():
    """docs/PROGRAMA_ORIGINAL.md é gerado de aeroballistics.programa (python -m aeroballistics.programa)."""
    from aeroballistics.programa import documento
    with open(DOC, encoding="utf-8") as f:
        assert f.read() == documento()


def test_bloco_desconhecido():
    with pytest.raises(KeyError):
        SPIN73.bloco("nao_existe")
    with pytest.raises(KeyError):
        SPIN73.de_coluna("XYZ")
