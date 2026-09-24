"""O MMQ recupera coeficientes conhecidos a partir de dados sintéticos com o mesmo desenho."""
import numpy as np
import recalibrar_mr1833 as r


def test_recupera_coeficientes_sinteticos():
    lin = r.tabela()
    rng = np.random.default_rng(1)
    verdade = {"const": lambda M: 3.0 + 0.2 * (M - 2) - 0.1 * (M - 2) ** 2,
               "CXLL": lambda M: 0.5 - 0.05 * (M - 2)}
    for l in lin:
        l["SINT"] = verdade["const"](l["M"]) + verdade["CXLL"](l["M"]) * l["CXLL"] + rng.normal(0, 0.01)
    regs = {"const": lambda l: 1, "CXLL": lambda l: l["CXLL"]}
    fit = r.mmq(lin, "SINT", regs, ["M-80", "M-59", "M-61", "M-62"])
    ev = r.avaliar(fit, r.GRADE)
    for k in regs:
        v, e = ev[k]
        assert np.all(np.abs(v - verdade[k](r.GRADE)) < 4 * e + 1e-3), k


def test_erro_puro_e_residuo_compativeis():
    """Sem falta de ajuste grosseira: resíduo < 1.5x erro puro nos ajustes da família."""
    lin = r.tabela()
    for y, (regs, projs, _) in r.MODELOS.items():
        fit = r.mmq(lin, y, regs, projs)
        ep, _ = r.erro_puro(lin, y, projs)
        assert fit["s"] < 1.5 * ep, y


def test_fator_recalibracao_recupera_k_sintetico():
    """Gera dados com k(M) conhecido a partir do próprio modelo e vê se o MMQ o recupera."""
    import numpy as np
    import comparar_cmq_cp as c

    k_verdade = lambda M: 0.5 + 0.2 * (M - 2) - 0.05 * (M - 2) ** 2
    lin = r.tabela()
    rng = np.random.default_rng(3)
    for l in lin:
        mod = np.interp(l["M"], c.MACH, c.curva_cmq(r.GEO[l["proj"]]))
        l["SINT"] = k_verdade(l["M"]) * mod + rng.normal(0, 0.5)
    grade, k, sk, n, s = c.fator_recalibracao(lin, "SINT", c.curva_cmq)
    assert n >= 40
    assert np.all(np.abs(k - k_verdade(grade)) < 4 * sk + 0.02), (k, k_verdade(grade), sk)


def test_cmq_do_spin73_e_mais_forte_que_o_experimento():
    """Registra o achado: k < 1 em toda a faixa com dados (o modelo amortece demais)."""
    import numpy as np
    import comparar_cmq_cp as c

    grade, k, sk, n, s = c.fator_recalibracao(r.tabela(), "CMQ", c.curva_cmq)
    assert np.all(k + 2 * sk < 1.0), dict(zip(grade.tolist(), k.tolist()))


def test_cpn_do_spin73_atras_do_experimento_de_mach_2_em_diante():
    """Registra o achado: k < 1 no CPN em Mach 2,0 e 2,5 com qualquer dos três raios de
    ogiva supostos; em 2,5, por mais de dois desvios-padrão (em 2,0, com OR = 8 cal, fica
    no limite). O CPN do modelo ali depende do XC15 decidido pelas tabelas de 1973."""
    import comparar_cmq_cp as c

    lin = c.tabela()
    for OR in (8.0, c.OR_HIP, 12.0):
        grade, k, sk, n, s = c.fator_recalibracao(lin, "CPN", lambda g: c.curva_cpn(g, OR),
                                                  grade=np.array([2.0, 2.5]))
        assert n == 42
        assert np.all(k < 1.0) and k[1] + 2 * sk[1] < 1.0, (OR, k, sk)


def test_cna_do_m80_e_o_cartao_c205():
    """Registra o viés do CNα no M-80 (+0,21) e que o +0,28 da primeira comparação era a
    mesma conta sem o cartão C205."""
    import comparar_cmq_cp as c
    import comparar_cna as cn

    lin = r.tabela()
    com = {p: v for p, _, v, _ in c.por_rodada(lin, "CNA", cn.curva_cna)}
    sem = {p: v for p, _, v, _ in c.por_rodada(lin, "CNA", lambda g: cn.curva_cna(g, c205=False))}
    assert abs(com["M-80"] - 0.214) < 0.005 and abs(sem["M-80"] - 0.276) < 0.005
    assert all(abs(com[p]) < 0.12 for p in ("M-59", "M-61", "M-62")), com
