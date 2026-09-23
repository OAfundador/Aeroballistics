"""Centro de pressão (CPN) e momento de tombamento (CMα) do SPIN-73.

Estrutura: relatório p. 15 (AMOMSQ, AMOMBT, CPN), com as duas correções de texto já
conhecidas (NOTAS_TRANSCRICAO.md, itens E2 e E3): "CYNN" é CVNN e "VBTI" é VBTT = VL/4,7.

    AMOMSQ = CNAB * (C1 + C2*CVNN + C3*CVNN^2 + C4*CVNN^3 + C5*CXLL + C6*CXLL^2
                     + C7*CXLL^3 + C8*CCRT + C9*CCRT^2 + C10*CDMM + C11*CCRT*CVNN + C17*DNX)
    AMOMBT = VBTT * (C12*VBMP + C13*VBX*CVNN + C14*VBX*CXLL + C15*VBX*CCRT
                     + C16*VBX*CCRT*CVNN)
    CPN    = (AMOMSQ + AMOMBT) / CNAT          CMA = (VCG - CPN) * CNAT

CNAB é a força normal do corpo sem o boattail (B1..B6) e CNAT a total (B1..B9); nenhuma
das duas é impressa separadamente, então ambas vêm do CNα reconstruído (reconstrucao_B).

Validação (test_cpn.py): no 175 mm M437 a conta reproduz o CPN e o CMA impressos dentro
de 0,0007 em Mach 0,01, 0,90 e 1,10 -- os três pontos em que todos os doze coeficientes
estão lidos sem dúvida. Os demais dependem das pendências listadas em xc_lidos.py
(linha XC12 desbotada e o cartão ausente de XC15). Ver NOTAS_TRANSCRICAO.md, seção T6.
"""
import os
import sys

import numpy as np

_AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_AQUI, "..", "reconstrucao_B"), os.path.join(_AQUI, "..")]

from ajustar_B import regressores          # noqa: E402
from xb_lidos import XB                    # noqa: E402
from xc_lidos import XC, MACH              # noqa: E402


def termos_geometria(VL, VN, VB, OR, DM, M):
    """Variáveis da p. 14-15. O limiar sub/supersônico é Mach 0,95 (NOTAS, T5)."""
    A_exp, B_exp = (1.5, 1.0) if M >= 0.95 else (1.0, 0.8)
    VNX, DNX = (VN, 0.0) if VN < 3.0 else (3.0, VN - 3.0)
    if VB <= 0.0:
        VBNP = VBMP = VBX = 0.0
    elif VB < 1.0:
        VBNP, VBMP, VBX = VB ** A_exp, VB ** B_exp, VB
    else:
        VBX, VBNP, VBMP = 1.0, VB ** 0.5, VB ** 0.5
    return dict(CVNN=VNX - 2.47, CXLL=VL - VN - VB - 2.15, CCRT=VN ** 2 / OR - 0.48,
                CDMM=DM - 0.17, VBTT=VL / 4.7, VBX=VBX, VBMP=VBMP, DNX=DNX)


def cpn_cma(VL, VN, VB, OR, DM, VCG, j, XB=XB, XC=XC, cna_impresso=None):
    """CPN e CMα no ponto j da grade de Mach. Devolve NaN onde o DATA falta.

    `cna_impresso` substitui o CNα reconstruído pelo valor impresso na tabela, e o
    CNAB passa a ser CNα_impresso − CNBT. Isso tira do resíduo do CPN o erro do CNα
    (que chega a 0,002 e, propagado, vale até 0,005 no CPN) e deve ser usado sempre
    que a coluna CNA da tabela estiver transcrita.
    """
    g = termos_geometria(VL, VN, VB, OR, DM, MACH[j])
    x = np.array(regressores(VL, VN, VB, OR, MACH[j]))
    B, C = XB[:, j], XC[:, j]
    CNBT = min(x[6:] @ B[6:], 0.0)             # cartão C205: CNBT positivo é zerado
    CNAB = x[:6] @ B[:6]                       # sem boattail
    CNAT = CNAB + CNBT                         # total
    if cna_impresso is not None:
        CNAT = cna_impresso
        CNAB = CNAT - CNBT                     # CNAB = total impresso - boattail
    AMOMSQ = CNAB * (C[0] + C[1] * g["CVNN"] + C[2] * g["CVNN"] ** 2 + C[3] * g["CVNN"] ** 3
                     + C[4] * g["CXLL"] + C[5] * g["CXLL"] ** 2 + C[6] * g["CXLL"] ** 3
                     + C[7] * g["CCRT"] + C[8] * g["CCRT"] ** 2 + C[9] * g["CDMM"]
                     + C[10] * g["CCRT"] * g["CVNN"] + C[16] * g["DNX"])
    AMOMBT = g["VBTT"] * (C[11] * g["VBMP"] + C[12] * g["VBX"] * g["CVNN"]
                          + C[13] * g["VBX"] * g["CXLL"] + C[14] * g["VBX"] * g["CCRT"]
                          + C[15] * g["VBX"] * g["CCRT"] * g["CVNN"])
    CPN = (AMOMSQ + AMOMBT) / CNAT
    return CPN, (VCG - CPN) * CNAT


def implicado(coef, VL, VN, VB, OR, DM, VCG, j, CPN_impresso):
    """Valor de XC[coef] (1-based) que reproduziria o CPN impresso, com os demais fixos.

    Usado para recuperar as células perdidas na impressão. O resultado é um valor
    DECIDIDO PELO MODELO: fica fora de qualquer validação feita com a mesma tabela.
    """
    g = termos_geometria(VL, VN, VB, OR, DM, MACH[j])
    peso = {12: g["VBTT"] * g["VBMP"], 13: g["VBTT"] * g["VBX"] * g["CVNN"],
            14: g["VBTT"] * g["VBX"] * g["CXLL"], 15: g["VBTT"] * g["VBX"] * g["CCRT"],
            16: g["VBTT"] * g["VBX"] * g["CCRT"] * g["CVNN"]}[coef]
    XC0 = XC.copy()
    XC0[coef - 1, j] = 0.0
    x = np.array(regressores(VL, VN, VB, OR, MACH[j]))
    CNAT = x[:6] @ XB[:6, j] + min(x[6:] @ XB[6:, j], 0.0)
    CPN0, _ = cpn_cma(VL, VN, VB, OR, DM, VCG, j, XC=XC0)
    return (CPN_impresso - CPN0) * CNAT / peso
