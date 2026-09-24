"""Guarda das conversões de convenção nos benchmarks.

Não fixa o erro do SPIN-73 contra a realidade (isso é resultado, não requisito). Testa só
que as normalizações foram aplicadas: um fator 2 esquecido em qd/V ou pd/V deixaria a
razão SPIN-73/medido do Cmq supersônico perto de 0,5 ou 2, e não perto de 1 como nas três
fontes independentes.
"""
import comparar as cp


def _razao(res, coef, faixa):
    return next(r[5] for r in res if r[0] == coef and r[1] == faixa)


def test_cmq_supersonico_nas_tres_fontes():
    for f in (cp.m101, cp.m483a1, cp.m33):
        assert 0.8 < _razao(f(), "CMQ", "supersônico") < 1.25, f.__name__


def test_cma_supersonico_m101_e_m483a1():
    """Os dois projéteis de artilharia: o CMα do SPIN-73 fica a poucos por cento."""
    for f in (cp.m101, cp.m483a1):
        assert 0.95 < _razao(f(), "CMA", "supersônico") < 1.05, f.__name__


def test_cmq_supersonico_nas_fontes_novas():
    """Mesma guarda para o 7,62 match e o 30 mm (McCoy, qd/V) e o T203 (notação K). Aqui a
    faixa é 0,8-1,6: há grupos com 3 rodadas; um fator 2 esquecido daria 0,5-0,7 ou 1,9-2,9."""
    n = 0
    for res in cp.match762() + cp.x30():
        if any(r[0] == "CMQ" and r[1] == "supersônico" for r in res):
            assert 0.8 < _razao(res, "CMQ", "supersônico") < 1.6
            n += 1
    assert n == 6
    assert 0.8 < _razao(cp.t203(), "KH", "supersônico") < 1.3


def test_t203_arrasto_e_cma():
    """O T203 é o M437 em desenvolvimento: arrasto a 1 % e CMα supersônico a 1 % do SPIN-73,
    que foi calibrado nessa família (e com o OR do M437; ver correcao/dados.py)."""
    res = cp.t203()
    assert 0.97 < _razao(res, "KD", "supersônico") < 1.03
    assert 0.95 < _razao(res, "KM", "supersônico") < 1.05


def test_xm617_cone_cilindro_supersonico():
    """Cone-cilindro em escala real: no supersônico o SPIN-73 acerta CD, CMα e CNα a poucos %."""
    res = cp.xm617()
    for c in ("CD", "CMA", "CNA"):
        assert 0.95 < _razao(res, c, "supersônico") < 1.05, c
