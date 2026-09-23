"""Guarda das conversões de convenção nos benchmarks.

Não fixa o erro do SPIN-73 contra a realidade (isso é resultado, não requisito). Testa só
que as normalizações foram aplicadas: um fator 2 esquecido em qd/V ou pd/V deixaria a
razão SPIN-73/medido do Cmq supersônico perto de 0,5 ou 2, e não perto de 1 como nas três
fontes independentes.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import comparar as cp                                  # noqa: E402


def _razao(res, coef, faixa):
    return next(r[5] for r in res if r[0] == coef and r[1] == faixa)


def test_cmq_supersonico_nas_tres_fontes():
    for f in (cp.m101, cp.m483a1, cp.m33):
        assert 0.8 < _razao(f(), "CMQ", "supersônico") < 1.25, f.__name__


def test_cma_supersonico_m101_e_m483a1():
    """Os dois projéteis de artilharia: o CMα do SPIN-73 fica a poucos por cento."""
    for f in (cp.m101, cp.m483a1):
        assert 0.95 < _razao(f(), "CMA", "supersônico") < 1.05, f.__name__
