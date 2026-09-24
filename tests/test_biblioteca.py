"""A interface de biblioteca (aeroballistics.Aerodinamica e aeroballistics.correcoes)."""
import numpy as np
import pytest

import aeroballistics
from aeroballistics import correcoes

P556 = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DM=0.12, BD=1.00,
                       DIA=0.224, nome="M855")


def test_sem_correcao_e_o_programa_de_1973():
    a = aeroballistics.Aerodinamica(aeroballistics.M437)
    t = aeroballistics.tabela(aeroballistics.M437)
    for j, M in enumerate(aeroballistics.MACH_GRID):
        c = a(M)
        assert c.CX0 == pytest.approx(t["CX"][j]) and c["CMA"] == pytest.approx(t["CMA"][j])
    assert a.correcoes == []


def test_interpolacao_linear_e_vetorizada():
    a = aeroballistics.Aerodinamica(aeroballistics.M437)
    M = np.array([0.7, 1.5, 2.25, 4.5])
    v = a.coeficiente("CNA", M)
    assert v.shape == (4,)
    assert np.allclose(v, np.interp(M, aeroballistics.MACH_GRID, a.tabela["CNA"]))
    assert isinstance(a.coeficiente("CNA", 2.25), float)


def test_convencao_moderna():
    s73 = aeroballistics.Aerodinamica(aeroballistics.M437)(2.0)
    mod = aeroballistics.Aerodinamica(aeroballistics.M437, convencao="moderna")(2.0)
    assert mod.Cmq_Cmad == pytest.approx(s73.CMQ / 2)          # qd/2V -> qd/V
    assert mod.Clp == pytest.approx(s73.CLP / 2)
    assert mod.Cmpa == pytest.approx(s73.CNPA / 2)
    assert mod.CDd2 == pytest.approx(s73.CX2 + s73.CNA)
    assert mod.CLa == pytest.approx(s73.CNA - s73.CX0)


def test_fora_da_faixa():
    assert aeroballistics.Aerodinamica(aeroballistics.M437)(7.0).CX0 == pytest.approx(aeroballistics.tabela(aeroballistics.M437)["CX"][-1])
    assert np.isnan(aeroballistics.Aerodinamica(aeroballistics.M437, fora_da_faixa="nan")(7.0).CX0)
    with pytest.raises(ValueError):
        aeroballistics.Aerodinamica(aeroballistics.M437, fora_da_faixa="erro")(7.0)


def test_correcao_por_nome_igual_ao_experimental():
    import os
    import sys
    a = aeroballistics.Aerodinamica(P556, "voo_livre")
    assert [c.nome for c in a.correcoes] == ["voo_livre"]
    assert np.all(a.tabela["CX"] > a.tabela_original["CX"])        # bala pequena: mais atrito
    assert np.allclose(a.tabela["CPN"], P556.VCG - a.tabela["CMA"] / a.tabela["CNA"])


def test_escolher_so_um_coeficiente():
    a = aeroballistics.Aerodinamica(P556, "voo_livre:CX0")
    assert np.allclose(a.tabela["CNA"], a.tabela_original["CNA"])
    assert not np.allclose(a.tabela["CX"], a.tabela_original["CX"])


def test_correcao_de_escala_exige_diametro():
    p = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51)
    with pytest.raises(ValueError):
        aeroballistics.Aerodinamica(p, "voo_livre")
    assert aeroballistics.Aerodinamica(p, "voo_livre", d_mm=5.69).contexto.d_mm == 5.69


def test_correcao_do_usuario_e_registro():
    class CmaMais10(correcoes.Correcao):
        nome = "cma_mais_10"
        descricao = "CMα × 1,1 (exemplo)"

        def aplicar(self, t, p, ctx):
            out = correcoes.base.copiar(t)
            out["CMA"] = out["CMA"] * 1.1
            return out

    a = aeroballistics.Aerodinamica(aeroballistics.M437, CmaMais10())
    assert np.allclose(a.tabela["CMA"], 1.1 * a.tabela_original["CMA"])
    # derivados recalculados: CPN coerente e s_g inversamente proporcional ao CMα
    assert np.allclose(a.tabela["CPN"], aeroballistics.M437.VCG - a.tabela["CMA"] / a.tabela["CNA"])
    assert np.allclose(a.tabela["GYRO"], a.tabela_original["GYRO"] / 1.1)

    correcoes.registrar("cma_mais_10", CmaMais10)
    assert "cma_mais_10" in correcoes.disponiveis()
    b = aeroballistics.Aerodinamica(aeroballistics.M437, ["cma_mais_10"])
    assert np.allclose(b.tabela["CMA"], a.tabela["CMA"])
    with pytest.raises(KeyError):
        aeroballistics.Aerodinamica(aeroballistics.M437, "nao_existe")


def test_encadeamento_na_ordem_dada():
    a = aeroballistics.Aerodinamica(P556, ["voo_livre:CX0", "voo_livre:CNA"])
    b = aeroballistics.Aerodinamica(P556, "voo_livre")
    for col in ("CX", "CNA", "CPN"):
        assert np.allclose(a.tabela[col], b.tabela[col])


def test_dados_alternativos():
    k = aeroballistics.CoefAjuste.do_listing()
    k.a[0] = k.a[0] + 0.01                      # XA1 + 0,01 -> CX + 0,01 em todo Mach
    a = aeroballistics.Aerodinamica(aeroballistics.M437, dados=k)
    assert np.allclose(a.tabela["CX"], a.tabela_original["CX"])      # original = com os mesmos dados
    assert np.allclose(a.tabela["CX"], aeroballistics.tabela(aeroballistics.M437)["CX"] + 0.01)


def test_momento_magnus_entre_1_e_5_graus():
    a = aeroballistics.Aerodinamica(aeroballistics.M437)
    c = a(2.0)
    assert a.momento_magnus(2.0, np.radians(1.0)) == pytest.approx(c.CNPA)
    assert a.momento_magnus(2.0, np.radians(5.0)) == pytest.approx(c.CNPA5)
    assert a.momento_magnus(2.0, np.radians(10.0)) == pytest.approx(c.CNPA5)


def test_api_antiga_continua():
    """O que o módulo aeroballistics.py exportava continua acessível."""
    for nome in ("tabela", "formatar", "avisos", "Projetil", "CoefAjuste", "M437", "MACH_GRID",
                 "normal_e_momento", "estabilidade", "ler_entrada", "salvar_csv", "_main"):
        assert hasattr(aeroballistics, nome), nome
