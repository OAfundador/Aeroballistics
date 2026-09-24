"""Conversões de convenção: ida e volta, e coerência com as já validadas em scripts/voo_livre/hitchcock/."""
import numpy as np

import aeroballistics as s
from aeroballistics import convencoes as cv


def test_ida_e_volta():
    t = s.tabela(s.M437)
    m = cv.para_moderno(t, VL=s.M437.VL)
    v = cv.de_moderno(m)
    for c in ("CX", "CX2", "CNA", "CMA", "CMQ", "CLP", "CYPA", "CNPA", "CPN"):
        assert np.allclose(v[c], t[c]), c


def test_fatores_de_normalizacao():
    """pd/2V e qd/2V do SPIN-73 contra pd/V e qd/V: o valor moderno é a metade.
    É o mesmo fator 2 validado no Hitchcock (K_H) e usado com o BRL MR 1833."""
    t = s.tabela(s.M437)
    m = cv.para_moderno(t)
    assert np.allclose(m["Cmq_Cmad"] * 2, t["CMQ"])
    assert np.allclose(m["Cmpa"] * 2, t["CNPA"])


def test_arrasto_de_guinada_e_cx2_mais_cna():
    """Relatório, p. 15: o arrasto de guinada é CX2 + CNα."""
    t = s.tabela(s.M437)
    assert np.allclose(cv.para_moderno(t)["CDd2"], t["CX2"] + t["CNA"])


def test_cp_do_momento_reproduz_cpn():
    t = s.tabela(s.M437)
    assert np.allclose(cv.cp_do_momento(s.M437.VCG, t["CMA"], t["CNA"]), t["CPN"])
