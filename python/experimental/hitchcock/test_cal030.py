"""Calibre 0.30 do Hitchcock (1947) contra a reconstrução do SPIN-73 (1973).

Três níveis de validação, do mais forte ao mais fraco:
  1. Identidades internas do próprio relatório (independem do SPIN-73): a geometria de
     cada esboço fecha pela soma das partes, e o K_M de cada série de tiro é coerente com
     o fator de estabilidade S, a velocidade e os momentos de inércia tabelados. Um dígito
     mal lido em qualquer dessas colunas aparece aqui.
  2. Conversões entre a notação do BRL e a do SPIN-73 (conversoes.py).
  3. Comparação do modelo com o experimento: o que sobra depois de 1 e 2 é desacordo real.
"""
import math
import os
import sys

import numpy as np
import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "..")
sys.path[:0] = [AQUI, RAIZ, os.path.join(RAIZ, "reconstrucao_B"), os.path.join(RAIZ, "reconstrucao_F")]

import spin73 as s                                    # noqa: E402
from ajustar_B import regressores                     # noqa: E402
from xb_lidos import XB                               # noqa: E402
from cmq_spin73 import cmq                            # noqa: E402
import conversoes as cv                               # noqa: E402
from dados_cal030 import (A_SOM, AMORTECIMENTO, B_BALL_M1_HIPOTESE, ESTABILIDADE,  # noqa: E402
                          FISICAS, GEOMETRIA)

GR = 7000.0                      # grains por libra
DIA = 0.300                      # polegadas
PASSO_CAL = 10.0 / DIA           # passo de raia de 10 polegadas, em calibres

# inércia usada pelo relatório para calcular cada K_M
INERCIA_DO_KM = {"Tracer M1": "Tracer M1 medio"}


def cma_do_fator_de_estabilidade(nome, S, V, mach=None, B=None):
    """Inverte s_g (fórmula do SPIN-73) para obter o CMα implicado pelo S medido.

    Quando o Mach é impresso, a temperatura da série sai de a = V/M e dá a densidade;
    sem ele, usa-se a atmosfera padrão (59 °F) e a incerteza é de alguns por cento.
    """
    f = FISICAS[INERCIA_DO_KM.get(nome, nome)]
    TF = (V / mach / 49.04) ** 2 - 459.6 if mach else 59.0
    rho = s.densidade_ar(TF)
    d = DIA / 12
    Ix = f["A"] / GR / (s.G_FT * 144)
    Iy = (B or f["B"]) / GR / (s.G_FT * 144)
    P = V * 2 * math.pi / (PASSO_CAL * d)
    return 2 * Ix ** 2 * P ** 2 / (math.pi * rho * Iy * S * d ** 3 * V ** 2)


def razao_km(linha, B=None):
    nome, _, _, V, M, S, K_M = linha
    return cma_do_fator_de_estabilidade(nome, S, V, M, B) / cv.cma_de_km(K_M)


def curva(nome, f):
    return [f(GEOMETRIA[nome], j, m) for j, m in enumerate(s.MACH_GRID)]


def cna_spin(nome, M):
    return float(np.interp(M, s.MACH_GRID, curva(
        nome, lambda g, j, m: np.array(regressores(g["VL"], g["VN"], g["VB"], g["OR"], m)) @ XB[:, j])))


def cmq_spin(nome, M):
    vcg = GEOMETRIA[nome]["VL"] - FISICAS[nome]["g"]
    return float(np.interp(M, s.MACH_GRID, curva(nome, lambda g, j, m: cmq(g["VL"], vcg, g["VB"], j))))


def amortecimento(nome):
    return [l for l in AMORTECIMENTO if l[0] == nome][0]


# ------------------------------------------------------------ 1. identidades da fonte
@pytest.mark.parametrize("nome", ["Ball M1", "Ball M2", "A.P. M2", "Tracer M1"])
def test_esboco_fecha_pela_soma_das_partes(nome):
    g = GEOMETRIA[nome]
    assert abs(g["VB"] + g["cilindro"] + g["VN"] - g["VL"]) < 1e-9 or \
        abs(g["cilindro"] + g["VN"] - g["VL"]) < 1e-9


LINHAS_OK = [l for l in ESTABILIDADE if l[0] in ("Ball M2", "Tracer M1", "Frangible M22")]


@pytest.mark.parametrize("linha", LINHAS_OK, ids=lambda l: l[0])
def test_km_coerente_com_s(linha):
    """Leitura verificada: K_M, S, velocidade e inércias fecham em ±3 %."""
    assert abs(razao_km(linha) - 1) < 0.03


def test_ap_m2_dentro_da_incerteza_de_temperatura():
    """4 %: o Mach não está impresso, então a temperatura da série é desconhecida;
    ±20 °F já explicam. Não é tratado como erro de leitura."""
    linha = [l for l in ESTABILIDADE if l[0] == "A.P. M2"][0]
    assert abs(razao_km(linha) - 1) < 0.06


def test_ball_m1_inconsistente_na_fonte():
    """As três séries do Ball M1 violam a identidade na MESMA direção, com a célula
    B = 16,40 relida e inequívoca. É inconsistência do relatório, não da transcrição.
    O B hipotético de 18,40 concilia as três séries."""
    linhas = [l for l in ESTABILIDADE if l[0] == "Ball M1"]
    impresso = [razao_km(l) for l in linhas]
    hipotese = [razao_km(l, B=B_BALL_M1_HIPOTESE) for l in linhas]
    assert all(1.08 < r < 1.13 for r in impresso), impresso
    assert all(abs(r - 1) < 0.035 for r in hipotese), hipotese


# ------------------------------------------------------------ 2 e 3. SPIN-73 x experimento
def test_cmq_ball_m2():
    """Base reta, Mach 2,49: 3 %. Fixa também o fator 2 de −(16/π)·K_H."""
    nome, _, V, _, K_H, _ = amortecimento("Ball M2")
    r = cmq_spin(nome, V / A_SOM) / cv.cmq_de_kh(K_H)
    assert abs(r - 1) < 0.05, r
    assert abs(r * 2 - 1) > 0.8          # sem o fator 2, erraria por quase o dobro


def test_cmq_tracer_m1():
    """Base reta, Mach 2,46: o modelo fica 10 % abaixo do medido."""
    nome, _, V, _, K_H, _ = amortecimento("Tracer M1")
    r = cmq_spin(nome, V / A_SOM) / cv.cmq_de_kh(K_H)
    assert 0.85 < r < 0.95, r


def test_cmq_ball_m1_boattail_registra_desacordo():
    """Boattail de 0,81 cal: o modelo amortece 25 % menos que o medido. O termo F8·VB
    do SPIN-73 tira ~7,5 unidades de Cmq nesse projétil; sem boattail daria ~−21."""
    nome, _, V, _, K_H, _ = amortecimento("Ball M1")
    r = cmq_spin(nome, V / A_SOM) / cv.cmq_de_kh(K_H)
    assert 0.70 < r < 0.80, r


def test_kl_ball_m2_implica_arrasto_do_grafico():
    """K_L = (π/8)(CNα − CX): CX implicado 0,42 contra ~0,38 do gráfico da p. 19."""
    nome, _, V, K_L, _, _ = amortecimento("Ball M2")
    cx = cna_spin(nome, V / A_SOM) - K_L / cv.PI_8
    assert 0.33 < cx < 0.48, cx


def test_kl_tracer_m1_arrasto_baixo():
    """CX implicado 0,19: baixo para base reta, mas na direção esperada para um traçante,
    cuja queima na base reduz o arrasto de base. Registrado, não validado."""
    nome, _, V, K_L, _, _ = amortecimento("Tracer M1")
    cx = cna_spin(nome, V / A_SOM) - K_L / cv.PI_8
    assert 0.10 < cx < 0.30, cx


def test_kl_ball_m1_registra_desacordo():
    """CX implicado 0,91 é impossível em Mach 2,4: para o Ball M1 com boattail, o CNα do
    SPIN-73 (2,87) é ~0,5 maior que o que o K_L medido admite. Junto com o Cmq (−25 %)
    e a inconsistência interna da fonte, o Ball M1 é o ponto menos confiável da seção."""
    nome, _, V, K_L, _, _ = amortecimento("Ball M1")
    cx = cna_spin(nome, V / A_SOM) - K_L / cv.PI_8
    assert cx > 0.7, cx


def test_formula_do_hitchcock_perto_do_cp_medido():
    """Ball M2: a fórmula de 1947 e o CP implicado pelo experimento concordam em ~0,06 cal."""
    linha = [l for l in ESTABILIDADE if l[0] == "Ball M2"][0]
    nome, _, _, V, _, S, _ = linha
    g = GEOMETRIA[nome]
    vcg = g["VL"] - FISICAS[nome]["g"]
    cpn_medido = vcg - cma_do_fator_de_estabilidade(nome, S, V) / cna_spin(nome, V / A_SOM)
    h = cv.h_hitchcock(0, 0, g["cilindro"], g["VN"], g["OR"])
    assert abs(cv.do_nariz(g["VL"], h) - cpn_medido) < 0.10
