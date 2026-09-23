"""SPIN-73 com a correção de voo livre -- atalho para a biblioteca.

A aplicação da correção agora vive na biblioteca (spin73.correcoes.VooLivre), para poder ser
usada de um simulador; aqui ficam o ajuste e a validação (ajuste.py), que gravam o
resultado em spin73/correcoes/voo_livre.json.

    import aplicar
    t = aplicar.tabela_corrigida(p, d_mm=5.69)

é o mesmo que

    spin73.Aerodinamica(p, correcoes="voo_livre", d_mm=5.69).tabela
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import spin73 as s                                      # noqa: E402
from spin73.correcoes.voo_livre import ARQUIVO          # noqa: E402,F401


def tabela_corrigida(p: s.Projetil, d_mm: float | None = None, modelo=None) -> dict:
    if d_mm is None and not p.DIA > 0:
        raise ValueError("informe d_mm ou p.DIA: a correção depende do tamanho real")
    return s.Aerodinamica(p, modelo or "voo_livre", d_mm=d_mm).tabela
