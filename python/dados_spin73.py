"""Blocos DATA do SPIN-73, reunidos num só lugar.

Cada array tem forma (n, 17): linha i = coeficiente i+1, coluna j = MACH[j]. Os valores
vêm dos módulos de reconstrução, que guardam a leitura, as correções decididas e a
evidência de cada uma. Aqui só se monta o conjunto que o programa usa.

Situação de cada bloco (ver docs/NOTAS_TRANSCRICAO.md):

  XA1..XA15  arrasto CX            NÃO LIDO (p. 79)                    -> NaN
  XB1..XB10  força normal CNα      XB1..XB9 lidos (6 correções decididas); XB10 não
                                   aparece no código transcrito até agora
  XC1..XC17  centro de pressão     lidos; cartão de XC15 ausente no listing, com
                                   Mach 1,2 e 2,0 recuperados pelas tabelas; XC12
                                   em Mach 1,05 decidido pelo modelo
  XD1..XD4   CX2                   NÃO LIDO (pp. 80-81)                -> NaN
  XE1..XE4   Magnus                lidos (iguais aos identificados pelas tabelas)
  XE5        Magnus, corpo longo   usado no código (cartão C218); valores IDENTIFICADOS
                                   pelas tabelas, o DATA ainda não foi lido
  XF1..XF9   Cmq                   lidos
  XG1        Clp                   lido
"""
import os
import sys

import numpy as np

_AQUI = os.path.dirname(os.path.abspath(__file__))
for _sub in ("reconstrucao_B", "reconstrucao_C", "reconstrucao_F"):
    _p = os.path.join(_AQUI, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from xb_lidos import XB as _XB                      # noqa: E402
from xc_lidos import XC as _XC                      # noqa: E402
from xf_lidos import XE as _XE, XF as _XF, XG1 as _XG1   # noqa: E402

XMACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                  1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
N = XMACH.size


def _nan(n):
    return np.full((n, N), np.nan)


XA = _nan(15)

XB = np.vstack([_XB, _nan(1)])                       # XB10: sem uso identificado

XC = _XC.copy()

XD = _nan(4)

# XE5: termo de corpo longo do Magnus, somado ao CPF quando VL > 6 (cartões C216-C222).
# Os valores foram identificados pelas tabelas de 7, 9 e 10 calibres antes de o código
# ser lido (magnus_clp.K_LONGO); o bloco DATA correspondente ainda não foi transcrito.
_XE5 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .10, .20, .30, .30, .27, .25, .20])
XE = np.vstack([_XE, _XE5])

XF = _XF.copy()

XG = _XG1.reshape(1, N)

SITUACAO = {
    "XA": "não lido", "XB": "lido (XB10 sem uso)", "XC": "lido, XC15 incompleto",
    "XD": "não lido", "XE": "lido (XE5 identificado pelas tabelas)",
    "XF": "lido", "XG": "lido",
}
