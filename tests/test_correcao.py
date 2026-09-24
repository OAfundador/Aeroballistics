"""Correção empírica: dados, validação e aplicação."""
import json

import numpy as np
import pytest

import ajuste as aj
import aplicar
import dados
from aeroballistics.correcoes import reynolds as rn
from aeroballistics.correcoes.voo_livre import ARQUIVO
import aeroballistics as s


@pytest.fixture(scope="module")
def ls():
    return dados.linhas()


def test_identidade_confere_transcricao_e_convencoes(ls):
    """CMα = (VCG − CPN)·CNα com os valores MEDIDOS da mesma rodada. Pega um CLα tomado por CNα,
    um CPN tomado do nariz em vez da base ou um dígito mal lido."""
    n, ruins = dados.identidade_cma(ls)
    assert n >= 70 and len(ruins) <= 2, ruins


def test_grupos_em_cada_coeficiente(ls):
    """Todos os grupos no CX0; o T203 (OR não cotado) só no CX0."""
    assert {l["grupo"] for l in ls if l["coef"] == "CX0"} == set(aj.GRUPOS)
    for c in ("CNA", "CMA"):
        assert {l["grupo"] for l in ls if l["coef"] == c} == set(aj.GRUPOS) - {"t203"}


def test_fontes_novas_pela_identidade():
    """7,62 match e 30 mm: CMα = (CPN − CG)·(CLα + CD) com os valores de cada rodada, a 2 %.
    Pega dígito mal lido e CG trocado entre projéteis."""
    por = {}
    for l in dados.linhas():
        if l["grupo"] in ("762m", "30"):
            por.setdefault((l["proj"], round(l["M"], 4)), {})[l["coef"]] = l
    n = 0
    for d in por.values():
        if all(c in d for c in ("CMA", "CPN", "CNA")):
            n += 1
            prev = (d["CMA"]["geo"]["VCG"] - d["CPN"]["med"]) * d["CNA"]["med"]
            assert abs(prev / d["CMA"]["med"] - 1) < 0.02, d["CMA"]["proj"]
    assert n >= 70


def test_t203_cx0_perto_do_spin73(ls):
    """O T203 é o M437 em desenvolvimento, e o SPIN-73 foi calibrado nessa família: CX0 a 5 %."""
    L = [l for l in ls if l["grupo"] == "t203"]
    assert len(L) >= 12 and all(abs(l["med"] / l["spin"] - 1) < 0.05 for l in L)


def test_reynolds_nulo_na_escala_de_referencia():
    """Com o projétil do tamanho de referência, a correção de atrito é zero."""
    VL, d_mm = 5.0, 60.0
    assert abs(rn.delta_cx0(2.0, VL, 2.5, 0.4, 8.0, 0.12, d_mm, VL * d_mm / 1000)) < 1e-12


def test_reynolds_sinal():
    """Menor que a referência -> mais atrito (ΔCX0 > 0); maior -> menos."""
    assert rn.delta_cx0(2.0, 4.0, 2.0, 0.4, 8.0, 0.12, 5.56, 0.3) > 0
    assert rn.delta_cx0(2.0, 4.5, 2.4, 0.4, 10.0, 0.1, 155.0, 0.3) < 0


def test_correcao_do_cx0_generaliza(ls):
    """Validação cruzada aninhada: nos três regimes o erro em grupos não vistos cai."""
    for reg, (b, c, n, det) in aj.validar(ls, "CX0").items():
        assert c < b, reg


def test_json_reproduz_o_ajuste(ls):
    with open(ARQUIVO, encoding="utf-8") as f:
        salvo = json.load(f)
    novo = aj.ajuste_final(ls)
    for c in aj.APLICADOS:
        for reg, d in novo[c].items():
            assert (d["coef"] is None) == (salvo[c][reg]["coef"] is None), (c, reg)
            if d["coef"]:
                assert np.allclose(d["coef"][:2], salvo[c][reg]["coef"][:2]), (c, reg)


def test_so_entra_o_que_foi_aceito():
    with open(ARQUIVO, encoding="utf-8") as f:
        salvo = json.load(f)
    for c, regs in salvo.items():
        for reg, d in regs.items():
            assert (d["coef"] is not None) == d["validacao"]["aceita"], (c, reg)


def test_tabela_corrigida_coerente():
    p = s.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DM=0.12, BD=1.00)
    t, c = s.tabela(p), aplicar.tabela_corrigida(p, d_mm=5.69)
    assert np.allclose(c["CMA"], t["CMA"])                     # CMα não é corrigido
    assert np.allclose(c["CPN"], p.VCG - c["CMA"] / c["CNA"])  # CPN coerente
    assert np.allclose(c["CX2"] + c["CNA"], t["CX2"] + t["CNA"])   # arrasto de guinada intacto
    assert np.all(c["CX"] > t["CX"])                           # bala pequena: mais atrito


def test_tabela_corrigida_exige_escala():
    p = s.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51)
    with pytest.raises(ValueError):
        aplicar.tabela_corrigida(p)


def test_estabilidade_recalculada():
    c = aplicar.tabela_corrigida(s.M437)
    t = s.tabela(s.M437)
    assert "GYRO" in c and np.all(np.isfinite(c["GYRO"]))
    assert np.allclose(c["GYRO"], t["GYRO"] * t["CMA"] / c["CMA"])   # s_g ∝ 1/CMα
