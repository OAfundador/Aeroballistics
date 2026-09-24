"""Quais células de cada tabela impressa ajudaram a DECIDIR algum DATA ou alguma entrada.

Essas células não validam nada naquela tabela: mostram só que a decisão é coerente. O
registro vem das próprias decisões (spin73.dados.xa_lidos ... xf_lidos, dados_cna.py e as
linhas "decidir:" dos CSVs), para não haver lista paralela que fique desatualizada.

    circulares(pagina, tabela=None) -> {(coluna, Mach): motivo}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caminhos                                               # noqa: E402,F401

import spin73 as s                                            # noqa: E402
from dados_cna import T as _T_CNA                             # noqa: E402
from spin73.dados.xa_lidos import DECIDIDOS as _XA_DEC        # noqa: E402
from spin73.dados.xb_lidos import CORRECOES as _XB_CORR, DECIDIDO_POR as _XB_POR  # noqa: E402
from spin73.dados.xc_lidos import (CORRECOES as _XC_CORR, DECIDIDOS_M437,  # noqa: E402
                                   RECUPERADOS as _XC_REC)
from spin73.dados.xd_lidos import DECIDIDOS as _XD_DEC        # noqa: E402
from spin73.dados.xf_lidos import RECUPERADOS as _XF_REC      # noqa: E402

MACH = [round(float(m), 2) for m in s.MACH_GRID]

# As 6 correções de XB foram decididas pela contagem de células que fecham nas 10 tabelas
# com a coluna CNA transcrita (NOTAS, T5 e T7).
PAGINAS_XB = set(_T_CNA)
# Os 12 primeiros valores do XE5 (cartão não impresso) vêm das tabelas de corpo longo.
PAGINAS_XE5 = {35, 38, 41, 68}
# Correções de XC decididas pelas duas tabelas (M437 e 5"/38); as demais, só pelo M437.
_XC_DUAS = {(12, 6), (1, 2), (12, 1), (12, 9), (12, 10)}
_DEPENDE_CMA = ("CPN", "CMA", "GYRO", "W1", "W2", "L1", "L2", "L15", "L25", "DELT", "DISP")


def _marca(d, cols, js, motivo):
    for c in cols:
        for j in js:
            d.setdefault((c, MACH[j]), motivo)


def circulares(pagina, tabela=None):
    d = {}
    if tabela is not None:
        for (col, M) in tabela.circulares():
            var = [v for v, (_, _, c, _) in tabela.decidir.items() if c == col]
            d[(col, M)] = (f"entrada {var[0]} decidida por esta coluna" if var else
                           "presa por identidade a uma coluna que decidiu uma entrada")
    for (b, j) in _XB_CORR:
        por = _XB_POR.get((b, j), PAGINAS_XB)
        if pagina in por:
            _marca(d, ["CNA"], [j], f"XB{b} decidido com esta tabela"
                   + (" (contagem nas 10 tabelas de CNα)" if len(por) > 1 else ""))
    if pagina in PAGINAS_XE5:
        _marca(d, ["CPF1", "CPF5", "CNPA", "CNPA5"], range(12),
               "XE5 de Mach 0,01 a 1,75 (cartão não impresso) identificado pelas tabelas de corpo longo")
    if pagina in (53, 65):
        js = {j for (l, j) in _XC_CORR if pagina == 65 or (l, j) in _XC_DUAS}
        js |= {j for (_, j) in _XC_REC}
        if pagina == 65:
            js |= {j for (_, j) in DECIDIDOS_M437}
        _marca(d, _DEPENDE_CMA, sorted(js), "XC decidido com esta tabela")
        _marca(d, ["CX2"], sorted({j for (_, j) in _XD_DEC if pagina == 53 or j != 13}),
               "XD decidido com esta tabela")
        _marca(d, ["CX"], sorted({j for (_, j) in _XA_DEC}), "XA1/XA2 decididos com esta tabela")
    if pagina == 53:
        _marca(d, ["CMQ"], sorted({j for (_, j) in _XF_REC}), "cartão ausente do XF7 recuperado por esta tabela")
    return d


def mach_circulares(pagina, coluna, tabela=None):
    return {M for (c, M) in circulares(pagina, tabela) if c == coluna}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for pag in map(int, sys.argv[1:]):
        for (c, M), m in sorted(circulares(pag).items()):
            print(pag, c, M, m)
