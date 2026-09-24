"""Convenções do SPIN-73 e conversão para as normalizações modernas.

O que o relatório define (Nomenclatura, pp. 7-8, e Apêndice B, p. 77)
---------------------------------------------------------------------
Estilo NACA/BRL clássico: pressão dinâmica q̄ = ½ρV², área de referência A = πd²/4,
comprimento de referência d (diâmetro do projétil). Momentos em torno do CG.

  CX     força axial,            F_X / q̄A                (a guinada zero: CX0 = CD0)
  CX2    força axial de guinada, por sen²ᾱ
  CNA    força normal,           d(F_N / q̄A) / d(sen ᾱ)
  CMA    momento de arfagem,     d(M_m / q̄Ad) / d(sen ᾱ), em torno do CG
  CPN    centro de pressão da força normal, calibres a partir do NARIZ
  CYPA   força de Magnus,        F_Yp / q̄A(pd/2V), por sen ᾱ
  CNPA   momento de Magnus,      M_np / q̄Ad(pd/2V), por sen ᾱ, em torno do CG
  CPF1/5 centro de pressão da força de Magnus a 1° e 5°, calibres a partir do nariz
  CMQ    amortecimento em arfagem, M_mq / q̄Ad(qd/2V)
  CLP    amortecimento de rolamento, M_lp / q̄Ad(pd/2V)
  VCG    CG em calibres a partir do nariz

Pontos que exigem conversão ao comparar com fontes modernas (McCoy, BRL/ARL depois de
~1970, PRODAS, CFD):

  1. Taxas adimensionais: o SPIN-73 usa pd/2V e qd/2V; as fontes modernas usam pd/V e
     qd/V. O valor moderno é METADE do SPIN-73: Cmq+Cmα̇ = CMQ/2, Clp = CLP/2,
     Cmpα = CNPA/2, CNpα = CYPA/2.
  2. O CMQ do SPIN-73 é o Cmq + Cmα̇ que o voo livre mede (não há Cmα̇ separado).
  3. CX2 NÃO é o arrasto de guinada. O próprio relatório (p. 15) diz que o arrasto de
     guinada é CX2 + CNα:  CDδ² = CX2 + CNA.
  4. Força de sustentação: CLα = CNα − CD0 (pequena guinada).
  5. Derivadas "por sen ᾱ" = "por radiano" na pequena guinada; o CNPA3/CNPA5P são por
     sen³ᾱ e sen⁵ᾱ (e sofrem do defeito do original, NOTAS T12: CNPA3 + 0,1·CNPA5P = 3,75).
  6. Posições do nariz, em calibres. Muitas fontes dão a partir da BASE (Hitchcock, BRL
     MR 1833, em polegadas): x_nariz = VL − x_base.
  7. Sinais: CMA > 0 é momento de tombamento (instabilizante), como em McCoy. O sinal do
     Magnus varia entre fontes (lado positivo da força, sentido do giro): conferir a
     definição de cada fonte antes de comparar.
  8. Coeficientes K do BRL antigo (Hitchcock, BRL 620): fator π/8, ver
     scripts/voo_livre/hitchcock/conversoes.py.

Nomes das colunas: o programa imprime "CNPA5" para o coeficiente QUÍNTICO e "CNPA-5"
para a inclinação secante a 5°. Aqui eles se chamam CNPA5P e CNPA5 (NOMES_IMPRESSOS).

Entradas em branco no cartão original (Apêndice B, nota B): BD = 0 vira 1,00; OR = 0 vira
ogiva secante (2·VN²); DGUN = 0 vira DIA; DM em branco fica 0; TEMP em branco é 0 °F (é o
que as tabelas sem propriedades de massa imprimem: densidade 0,00270). O `Projetil` deste
pacote usa por omissão DM = 0,12 e BD = 1,02 (os valores de NAUTO = 1, "dimensões
automáticas") e TEMP = 59 °F; para reproduzir um cartão com campos em branco, passe
DM=0, BD=0 e TEMP=0 explicitamente.
"""
import numpy as np

NOMES_IMPRESSOS = {"CNPA5P": "CNPA5 (quíntico, por sen⁵ᾱ)", "CNPA5": "CNPA-5 (secante a 5°)",
                   "CYPA": "CYP"}


def para_moderno(t: dict, VL: float | None = None) -> dict:
    """Colunas do SPIN-73 (dicionário de `aeroballistics.tabela`) na normalização moderna
    (pd/V, qd/V; CDδ², CLα). Posições em calibres; do nariz e, se VL for dado, da base."""
    g = {k: np.asarray(v, float) for k, v in t.items()}
    out = dict(
        MACH=g["MACH"],
        CD0=g["CX"],
        CDd2=g["CX2"] + g["CNA"],
        CNa=g["CNA"],
        CLa=g["CNA"] - g["CX"],
        Cma=g["CMA"],
        Cmq_Cmad=g["CMQ"] / 2.0,
        Clp=g["CLP"] / 2.0,
        CNpa=g["CYPA"] / 2.0,
        Cmpa=g["CNPA"] / 2.0,
        Cmpa_5graus=g["CNPA5"] / 2.0,
        CP_nariz=g["CPN"],
        CPmagnus_nariz=g["CPF1"],
    )
    if VL is not None:
        out["CP_base"] = VL - g["CPN"]
    return out


def de_moderno(m: dict) -> dict:
    """O inverso de `para_moderno`, para levar dados experimentais modernos à forma do
    SPIN-73. Aceita só as chaves presentes."""
    conv = {
        "CD0": ("CX", lambda x: x),
        "CNa": ("CNA", lambda x: x),
        "Cma": ("CMA", lambda x: x),
        "Cmq_Cmad": ("CMQ", lambda x: 2.0 * x),
        "Clp": ("CLP", lambda x: 2.0 * x),
        "CNpa": ("CYPA", lambda x: 2.0 * x),
        "Cmpa": ("CNPA", lambda x: 2.0 * x),
        "CP_nariz": ("CPN", lambda x: x),
    }
    out = {conv[k][0]: conv[k][1](np.asarray(v, float)) for k, v in m.items() if k in conv}
    if "CDd2" in m and "CNa" in m:
        out["CX2"] = np.asarray(m["CDd2"], float) - np.asarray(m["CNa"], float)
    return out


def cp_do_momento(VCG: float, CMA, CNA):
    """Centro de pressão do nariz a partir de CMα em torno do CG: CPN = VCG − CMα/CNα."""
    return VCG - np.asarray(CMA, float) / np.asarray(CNA, float)
