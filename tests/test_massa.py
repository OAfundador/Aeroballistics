"""Adições opcionais de entrada: estimativa de massa (aeroballistics.massa) e unidades (aeroballistics.unidades)."""
import math

import numpy as np
import pytest

import aeroballistics
from aeroballistics import massa, unidades


def test_integrais_batem_com_cone_cilindro_analitico():
    """Cone de ponta aguda + cilindro: fórmulas fechadas de volume, CG e inércias."""
    VN, Lc, R = 2.0, 1.5, 0.5
    p = aeroballistics.Projetil(VL=VN + Lc, VN=VN, VB=0.0, OR=1000.0, DM=0.0)
    I, _ = massa.integrais(p)
    v1, v2 = math.pi * R * R * VN / 3, math.pi * R * R * Lc
    x1, x2 = 0.75 * VN, VN + Lc / 2
    V = v1 + v2
    xcg = (v1 * x1 + v2 * x2) / V
    Ix = 0.3 * v1 * R * R + 0.5 * v2 * R * R
    Iy = (v1 * (3 / 20 * R * R + 3 / 80 * VN * VN) + v1 * (x1 - xcg) ** 2
          + v2 * (3 * R * R + Lc * Lc) / 12 + v2 * (x2 - xcg) ** 2)
    for k, v in (("V", V), ("xcg", xcg), ("Jx", Ix), ("Jy", Iy)):
        assert I[k] == pytest.approx(v, rel=1e-6), k


def test_ogiva_tangente_passa_pelo_ombro_sem_quina():
    """Com OR = VN² + 0,25 (tangente, sem meplat), o arco chega ao ombro com raio 0,5."""
    p = aeroballistics.Projetil(VL=5.0, VN=2.0, VB=0.0, OR=2.0 ** 2 + 0.25, DM=0.0)
    trechos, obs = massa.contorno(p)
    a, b, f = trechos[0]
    r = f(np.array([0.0, 1.0, 1.999, 2.0]))
    assert r[0] == pytest.approx(0.0, abs=1e-9) and r[-1] == pytest.approx(0.5, abs=1e-9)
    assert r[-2] == pytest.approx(0.5, abs=1e-6)          # tangente: quase 0,5 antes do ombro
    assert not obs


def test_formulas_de_hitchcock():
    p = aeroballistics.Projetil(VL=4.0, VN=2.0, VB=0.4, OR=8.0)
    pm = massa.estimar(p, "bala", massa_g=10.0, d_mm=7.82)
    m, d, L = 0.010, 7.82e-3, 4.0 * 7.82e-3
    assert pm.cg_base == pytest.approx(0.400 * 4.0)
    assert pm.ix == pytest.approx(0.115 * m * d * d)
    assert pm.iy == pytest.approx(0.5 * 0.115 * m * d * d + 0.0543 * m * L * L)
    pg = massa.estimar(p, "granada", massa_g=10.0, d_mm=7.82)
    assert pg.cg_base == pytest.approx(0.375 * 4.0) and pg.ix == pytest.approx(0.140 * m * d * d)
    with pytest.raises(ValueError):
        massa.estimar(p, "bala", d_mm=7.82)                  # sem massa


def test_completar_nao_troca_o_que_foi_dado():
    p = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12, DIA=0.224, WGT=4.05 / 453.59237,
                        IX=1.0)                               # IX dado (mesmo absurdo) fica
    q = massa.completar(p, "solido")
    assert q.IX == 1.0 and q.WGT == p.WGT
    assert q.VCG is not None and q.IY > 0
    assert massa.o_que_falta(q) == []


def test_so_o_cg_sem_diametro_e_massa_pela_densidade():
    p = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, OR=7.9)
    pm = massa.estimar(p)
    assert pm.massa_kg is None and 2.0 < pm.cg_nariz < 3.0
    q = massa.completar(p)                                    # só o VCG
    assert q.VCG == pytest.approx(pm.cg_nariz) and q.WGT == 0 and q.DIA == 0
    r = massa.completar(p, material="chumbo", d_mm=5.69)      # massa pela densidade
    V = massa.integrais(p)[0]["V"] * (5.69e-3) ** 3
    assert r.WGT * 0.45359237 == pytest.approx(11340 * V)
    assert r.DIA == pytest.approx(5.69 / 25.4)


def test_validacao_guarda_as_faixas_documentadas():
    """As faixas de erro escritas em aeroballistics/massa.py saem de scripts/massa/validar.py."""
    import validar
    res = validar.avaliar()
    balas = [r for r in res if r["tipo"] == "bala"]
    granadas = [r for r in res if r["tipo"] == "granada"]
    assert len(balas) == 6 and len(granadas) == 6
    assert all(0.94 < r["solido"]["ix"] < 1.04 for r in balas)
    assert all(abs(r["solido"]["cg"] - r["cg_med"]) <= 0.125 for r in balas)
    assert all(0.88 < r["hitchcock"]["ix"] < 1.04 for r in granadas)
    assert all(r["solido"]["ix"] < 0.82 for r in granadas)       # parede: sólido subestima


def test_unidades_convertem_para_o_cartao():
    p = unidades.projetil(VL=4.05, VN=1.90, VB=0.40, D_MM=5.69, MASSA_G=4.05, IX_GCM2=0.1426,
                          IY_GCM2=1.150, PASSO_MM=177.8, TEMP_C=15.0, CG_BASE=1.54)
    assert p.DIA == pytest.approx(5.69 / 25.4)
    assert p.WGT == pytest.approx(4.05 / 453.59237)
    assert p.IX == pytest.approx(0.1426 / 2926.397, rel=1e-6)
    assert p.TWIST == pytest.approx(177.8 / 5.69)
    assert p.TEMP == pytest.approx(59.0)
    assert p.VCG == pytest.approx(4.05 - 1.54)
    q = unidades.projetil(vl=4.05, vn=1.9, vb=0.4, dia=0.224, passo_pol=7)   # minúsculas
    assert q.TWIST == pytest.approx(7 / 0.224)
    with pytest.raises(ValueError):
        unidades.projetil(VL=4, VN=2, VB=0.4, DIA=0.224, D_MM=5.69)      # duas vezes
    with pytest.raises(ValueError):
        unidades.projetil(VL=4, VN=2, VB=0.4, XYZ=1)                      # desconhecida


def test_sem_vcg_o_canonico_pede_o_cg():
    p = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40)
    with pytest.raises(ValueError, match="VCG"):
        aeroballistics.tabela(p)


def _cli(args, capsys):
    aeroballistics.cli.main(args)
    return capsys.readouterr().out


def test_cli_canonico_e_com_adicoes(capsys, tmp_path):
    out = _cli(["--exemplo"], capsys)
    assert "Modo: canônico (SPIN-73 de 1973)" in out and "STABILITY ANALYSIS" in out
    out = _cli(["--VL", "4.05", "--VN", "1.90", "--VB", "0.40", "--OR", "7.9", "--d-mm", "5.69",
                "--massa-g", "4.05", "--passo-mm", "177.8", "--estimar-massa"], capsys)
    assert "massa estimada (solido: VCG, IX, IY)" in out and "STABILITY ANALYSIS" in out
    arq = tmp_path / "bala.txt"
    arq.write_text("VL = 4.05\nVN = 1.90\nVB = 0.40\nOR = 7.9\nD_MM = 5.69\nMASSA_G = 4.05\n"
                   "PASSO_POL = 7\nESTIMAR_MASSA = bala\n", encoding="utf-8")
    out = _cli(["--entrada", str(arq)], capsys)
    assert "massa estimada (bala: VCG, IX, IY)" in out
    out = _cli(["--entrada", str(arq), "--DIA", "0.2240"], capsys)   # a linha substitui o arquivo
    assert "massa estimada (bala" in out


def test_cli_sem_vcg_sem_estimativa_e_erro(capsys):
    with pytest.raises(SystemExit):
        aeroballistics.cli.main(["--VL", "4.05", "--VN", "1.90", "--VB", "0.40"])
    assert "--estimar-massa" in capsys.readouterr().err
