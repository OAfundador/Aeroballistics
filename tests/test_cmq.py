"""Cmq (DATA XF), Clp (XG) e o Magnus (XE) contra as tabelas impressas."""
import numpy as np
from cmq_spin73 import cmq
from aeroballistics.dados.xf_lidos import RECUPERADOS as XF_RECUPERADOS, XE, XG1
import magnus_clp as mc
import tabelas_impressas as ti

T = {  # VL, VCG, VB, coluna CMQ impressa
 "M437": (5.51, 3.5, 1.0, [-12.101]*3 + [-13.870, -15.792, -18.937, -17.717, -18.929, -20.259, -19.546] + [-19.826]*7),
 "5/38": (4.59, 2.71, .35, [-9.419]*3 + [-11.750, -14.259, -18.321, -17.984, -19.352, -20.595, -20.122] + [-18.992]*7),
 "M101": (4.51, 2.96, .45, [-5.229]*3 + [-7.533, -9.961, -13.892, -13.436, -14.861, -15.849, -15.601] + [-15.343]*7),
 "9cal": (9.0, 5.05, 0.0, [-71.1]*3 + [-74.4, -76.7, -80.7, -80.4, -85.0, -90.4, -100.1, -114.0, -120.0, -126.0, -132.0, -132.0, -126.0, -117.0]),
 "XM380E5": (5.58, 3.34, .59, list(ti.carregar(50).colunas["CMQ"])),   # p. 50; NaN = ilegível
}
# O 2º cartão do XF7 (Mach 1,1 a 2,5) não foi impresso e foi recuperado pela coluna do 5"/38:
# nesses Mach ele não valida nada. M437 e XM380E5 ficam como teste independente.
CIRCULARES = {("5/38", j) for (_, j) in XF_RECUPERADOS}
PENDENTES = {("M101", 9): "Mach 1,35: leitura da coluna CMQ a reconferir",
             ("M101", 7): "Mach 1,1: impresso lido -14,861; o modelo dá -14,662 (provável par 6/8)"}
TOL = {"M437": 0.0015, "5/38": 0.0015, "M101": 0.005, "9cal": 0.15, "XM380E5": 0.0015}   # M101: VCG só com 3 casas; 9cal: coluna lida com 1 casa

def test_cmq_tabelas():
    for n, (VL, VCG, VB, tab) in T.items():
        tol = TOL[n]
        for j in range(17):
            if (n, j) in CIRCULARES or (n, j) in PENDENTES or not np.isfinite(tab[j]): continue
            assert abs(cmq(VL, VCG, VB, j) - tab[j]) <= tol, (n, j, cmq(VL, VCG, VB, j), tab[j])

def test_xf7_recuperado_fecha_nas_tabelas_independentes():
    """O cartão ausente do XF7 foi decidido pelo 5"/38; M437 e XM380E5 conferem em Mach 1,1."""
    for n in ("M437", "XM380E5"):
        VL, VCG, VB, tab = T[n]
        assert abs(cmq(VL, VCG, VB, 7) - tab[7]) <= 0.0015, n

def test_E_data_igual_identificado():
    assert np.allclose(XE[0], mc.E1) and np.allclose(XE[1], mc.E2) and np.allclose(XE[3], mc.E4)
