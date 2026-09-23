"""Blocos DATA do SPIN-73, reunidos num só lugar (spin73.dados).

Cada array tem forma (n, 17): linha i = coeficiente i+1, coluna j = MACH[j]. Os valores
vêm dos módulos de reconstrução, que guardam a leitura, as correções decididas e a
evidência de cada uma. Aqui só se monta o conjunto que o programa usa.

Situação de cada bloco (ver docs/NOTAS_TRANSCRICAO.md):

  XA1..XA15  arrasto CX            lidos (p. 79); 4 células decididas pelas tabelas;
                                   XA13..XA15 lidos mas sem tabela que os teste (VN > 3)
  XB1..XB10  força normal CNα      XB1..XB9 lidos (6 correções decididas); XB10 não
                                   aparece no código transcrito até agora
  XC1..XC17  centro de pressão     lidos; cartão de XC15 ausente no listing, recuperado
                                   pelas tabelas; 8 células decididas pelas tabelas
                                   (três tabelas com boattail: M437, 5"/38, XM380E5)
  XD1..XD4   CX2                   lidos; 4 células decididas pelas tabelas
  XE1..XE4   Magnus                lidos (iguais aos identificados pelas tabelas)
  XE5        Magnus, corpo longo   cartão final lido (Mach 2 a 5, confere com as tabelas);
                                   o primeiro cartão não foi impresso -> vem das tabelas
  XF1..XF9   Cmq                   lidos; 2º cartão do XF7 ausente no listing (Mach 1,1
                                   a 2,5), recuperado pelo 5"/38
  XG1        Clp                   lido
"""
import numpy as np

from .xa_lidos import XA as _XA
from .xb_lidos import XB as _XB
from .xc_lidos import XC as _XC
from .xd_lidos import XD as _XD
from .xf_lidos import XE as _XE, XF as _XF, XG1 as _XG1

XMACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                  1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
N = XMACH.size


def _nan(n):
    return np.full((n, N), np.nan)


XA = _XA.copy()

XB = np.vstack([_XB, _nan(1)])                       # XB10: sem uso identificado

XC = _XC.copy()

XD = _XD.copy()

# XE5: termo de corpo longo do Magnus, somado ao CPF quando VL > 6 (cartões C216-C222).
# Na p. 81 o cartão de continuação "1 0.3,0.3,0.27,0.25,0.20/" (Mach 2 a 5) aparece
# impresso duas vezes e o primeiro cartão (statement 57, Mach 0,01 a 1,75) falta -- o
# mesmo defeito de impressão do XC15. Os 5 valores impressos são exatamente os que as
# tabelas de 7, 9 e 10 calibres tinham identificado; os 12 primeiros vêm das tabelas.
_XE5 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .10, .20, .30, .30, .27, .25, .20])
XE = np.vstack([_XE, _XE5])

XF = _XF.copy()

XG = _XG1.reshape(1, N)

SITUACAO = {
    "XA": "lido (4 células decididas; XA13-15 sem teste)", "XB": "lido (XB10 sem uso)", "XC": "lido, XC15 incompleto",
    "XD": "lido (4 células decididas)", "XE": "lido (XE5 identificado pelas tabelas)",
    "XF": "lido", "XG": "lido",
}
