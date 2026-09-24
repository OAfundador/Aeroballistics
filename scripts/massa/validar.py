"""Estimativa de CG e inércias (aeroballistics.massa) contra valores MEDIDOS e publicados.

A massa medida entra como dado (é o que quase sempre se sabe); o que se testa é a DISTRIBUIÇÃO
dela: CG, Ix e Iy. Para cada projétil: o método "solido" (sólido homogêneo com o contorno do
cartão do SPIN-73) e o de Hitchcock correspondente ("bala" ou "granada", BRL 620, p. 9).

    python scripts/massa/validar.py      -> tabela (a mesma de docs/resultados/massa.txt)

Fontes (geometria em calibres, dos esboços; massa e inércias das tabelas físicas):
  5,56 NATO    McCoy, BRL-MR-3476 (1985), Tabela 1 e Figs. 2-3   (data/voo_livre/nato556_mccoy1985.csv)
  7,62 match   McCoy, BRL-MR-3733 (1988), Tabela 1 e Figs. 3-5   (data/voo_livre/match762_mccoy1988.csv)
  .50 M33      McCoy, BRL-MR-3810 (1990), Tabela 1 e Fig. 4      (data/voo_livre/m33_mccoy1990.csv)
  cal .30      Hitchcock, BRL 620, pp. 16 e 18 impressas          (scripts/voo_livre/hitchcock/dados_cal030.py)
  30 mm        McCoy, ARBRL-MR-03019 (1980), Fig. 1; ARBRL-TR-03432 (1982), Tabela I
  M437         cartão de entrada do próprio SPIN-73 (p. 65)       (aeroballistics.M437)
  T203 90 mm   Karpov et al., BRL MR 956 (1955), Figs. 1          (data/voo_livre/t203_karpov1955.csv)
  XM617        Brandon, BRL MR 1998 (1969), Fig. 3                (data/voo_livre/xm617_brandon1969.csv)
  M101         Karpov et al., BRL MR 1582 (1964), Tabela I        (data/voo_livre/m101_karpov1964.csv)
  M483A1       Whyte, BRL-CR-659 (1991), Tabela 1                 (data/voo_livre/m483a1_whyte1991.csv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caminhos                                        # noqa: E402,F401

import numpy as np                                     # noqa: E402

import aeroballistics as s                                     # noqa: E402
from aeroballistics import massa                               # noqa: E402

G_LB = 453.59237
LBIN2_GCM2 = G_LB * 2.54 ** 2
GR_G = 0.06479891                                      # grain

# nome, grupo, tipo (bala/granada), geometria (cartão; OR, DM...), ang_bt (None = 8° padrão),
# CG medido a partir da BASE (cal), massa (g), Ix e Iy medidos (g·cm²), d (mm), observação
PROJETEIS = [
    ("SS-109", "5,56", "bala", dict(VL=4.07, VN=2.00, VB=0.45, OR=8.4, DM=0.12), 9.75,
     1.52, 4.03, 0.1425, 1.112, 5.69, "meplat não cotado (0,12)"),
    ("M855", "5,56", "bala", dict(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12), 8.5,
     1.54, 4.05, 0.1426, 1.150, 5.69, "penetrador de aço na frente; meplat não cotado"),
    ("L110", "5,56", "traçante", dict(VL=5.13, VN=2.14, VB=0.26, OR=8.4, DM=0.12), None,
     2.52, 4.09, 0.1573, 1.874, 5.69, "base arredondada como tronco de cone"),
    ("M856", "5,56", "traçante", dict(VL=5.18, VN=2.00, VB=0.37, OR=9.7, DM=0.12), None,
     2.57, 4.19, 0.1634, 1.987, 5.69, "base arredondada como tronco de cone"),
    ("M118", "7,62 match", "bala", dict(VL=4.19, VN=2.16, VB=0.74, OR=7.00, DM=0.18), 9.5,
     1.80, 11.27, 0.716, 6.78, 7.82, ""),
    ("190 Sierra", "7,62 match", "bala", dict(VL=4.31, VN=2.09, VB=0.69, OR=8.80, DM=0.21), 11.0,
     1.81, 12.27, 0.787, 7.68, 7.82, ""),
    ("168 Sierra", "7,62 match", "bala", dict(VL=3.98, VN=2.26, VB=0.51, OR=7.00, DM=0.25), 13.0,
     1.54, 10.89, 0.722, 5.38, 7.82, ""),
    (".50 M33", ".50", "bala", dict(VL=4.46, VN=2.56, VB=0.78, OR=8.77, DM=0.18), 9.0,
     1.78, 42.02, 7.85, 74.5, 12.95, ""),
    ("Ball M1", "cal .30 (Hitchcock)", "bala*", dict(VL=4.44, VN=2.43, VB=0.81, OR=7.00, DM=0.12),
     None, 1.827, 172 * GR_G, 1.751 * GR_G * 6.4516, 16.40 * GR_G * 6.4516, 7.82,
     "B impresso; a fonte suspeita de 18,40"),
    ("Ball M2", "cal .30 (Hitchcock)", "bala*", dict(VL=3.75, VN=2.43, VB=0.0, OR=7.00, DM=0.12),
     None, 1.455, 151 * GR_G, 1.332 * GR_G * 6.4516, 12.13 * GR_G * 6.4516, 7.82, ""),
    ("A.P. M2", "cal .30 (Hitchcock)", "bala*", dict(VL=4.57, VN=2.45, VB=0.0, OR=7.00, DM=0.12),
     None, 1.980, 167 * GR_G, 1.855 * GR_G * 6.4516, 20.15 * GR_G * 6.4516, 7.82,
     "afinamento de 0,31 cal na base, como base reta"),
    ("Tracer M1", "cal .30 (Hitchcock)", "traçante*", dict(VL=4.75, VN=2.45, VB=0.0, OR=7.00, DM=0.12),
     None, 2.097, 149 * GR_G, 1.777 * GR_G * 6.4516, 18.57 * GR_G * 6.4516, 7.82, ""),
    ("XM788", "30 mm", "granada", dict(VL=3.49, VN=1.84, VB=0.0, OR=4.30, DM=0.26), None,
     1.25, 232.8, 326.9, 1685.0, 29.92, "ponta cônica dentro da ogiva; cintas fora"),
    ("XM788E1", "30 mm", "granada", dict(VL=3.61, VN=1.85, VB=0.0, OR=4.30, DM=0.26), None,
     1.35, 239.0, 330.2, 1743.0, 29.92, "idem"),
    ("XM789", "30 mm", "granada", dict(VL=3.61, VN=1.85, VB=0.0, OR=4.30, DM=0.26), None,
     1.40, 234.6, 313.6, 1619.0, 29.92, "idem"),
    ("M437", "175 mm", "granada", dict(VL=5.51, VN=2.91, VB=1.00, OR=25.0, DM=0.079), None,
     5.51 - 3.50, 148 * G_LB, 954.1 * LBIN2_GCM2, 10850 * LBIN2_GCM2, 6.885 * 25.4,
     "ângulo do boattail não cotado (8°)"),
    ("T203 (modelo)", "175 mm", "modelo", dict(VL=5.51, VN=2.91, VB=1.00, OR=25.0, DM=0.079), 8.0,
     1.940, 21.82 * G_LB, 34.76 * LBIN2_GCM2, 246.9 * LBIN2_GCM2, 90.0,
     "slug balístico de 90 mm; OR do M437"),
    ("XM617", "152 mm", "especial", dict(VL=3.151, VN=1.873, VB=0.0, OR=1000.0, DM=0.009), None,
     1.066, 19060.0, 459.91e3, 1884.69e3, 152.0, "cone-cilindro de baixa densidade"),
    ("M101", "155 mm", "granada", dict(VL=4.51, VN=2.45, VB=0.45, OR=10.75, DM=0.098), 8.25,
     4.51 - 2.96, 95.2 * G_LB, None, None, 155.0, "inércias dadas como k1^-2 = 7,1 e k2^-2 = 0,81"),
    ("M483A1", "155 mm", "granada", dict(VL=5.80, VN=2.844, VB=0.255, OR=9.48, DM=0.098), 8.0,
     5.80 - 3.64, 46860.0, 0.1575e7, 1.687e7, 154.74, "ogiva composta como arco único; "
     "carrega submunições"),
]
# M101: Ix = m d²/7,1 e Iy = m d²/0,81 (k1^-2 e k2^-2 do relatório)
_M101 = PROJETEIS[-2]
_m, _d = _M101[6], _M101[9] / 10.0
PROJETEIS[-2] = _M101[:7] + (_m * _d * _d / 7.1, _m * _d * _d / 0.81) + _M101[9:]


def avaliar():
    out = []
    for nome, grupo, tipo, geo, ang, cg_base, m_g, ix, iy, d_mm, obs in PROJETEIS:
        p = s.Projetil(**geo)
        linha = dict(nome=nome, grupo=grupo, tipo=tipo, obs=obs, cg_med=cg_base)
        for metodo in ("solido", "bala" if tipo.startswith(("bala", "traç")) else "granada"):
            pm = massa.estimar(p, metodo, massa_g=m_g, d_mm=d_mm, ang_bt=ang)
            linha[metodo if metodo == "solido" else "hitchcock"] = dict(
                cg=pm.cg_base, ix=pm.ix_gcm2 / ix, iy=pm.iy_gcm2 / iy,
                sg=(pm.ix_gcm2 / ix) ** 2 / (pm.iy_gcm2 / iy), metodo=metodo,
                rho=pm.densidade)
        out.append(linha)
    return out


def main():
    res = avaliar()
    print(__doc__.split("\n\n")[0])
    print("\nRazão estimado/medido (a massa medida é dada). CG a partir da base, cal.")
    print("s_g ∝ Ix²/Iy: a última coluna é o erro que a estimativa leva ao fator giroscópico.")
    print("* = projéteis da mesma família dos que deram as fórmulas de Hitchcock (não independentes).\n")
    cab = (f"{'projétil':15s} {'tipo':10s} {'CG med':>7s} | {'CG sól':>7s} {'Ix':>6s} {'Iy':>6s} "
           f"{'s_g':>6s} {'ρ ef.':>6s} | {'Hitchcock':>9s} {'CG':>6s} {'Ix':>6s} {'Iy':>6s} {'s_g':>6s}")
    print(cab)
    print("-" * len(cab))
    for r in res:
        a, h = r["solido"], r["hitchcock"]
        print(f"{r['nome']:15s} {r['tipo']:10s} {r['cg_med']:7.3f} | {a['cg']:7.3f} {a['ix']:6.3f} "
              f"{a['iy']:6.3f} {a['sg']:6.3f} {a['rho'] / 1000:6.2f} | {h['metodo']:>9s} "
              f"{h['cg']:6.3f} {h['ix']:6.3f} {h['iy']:6.3f} {h['sg']:6.3f}")
    print("\nρ ef. = massa medida / volume do contorno, g/cm³.")
    for classe, filtro in (("balas (sem traçantes, sem *)", lambda r: r["tipo"] == "bala"),
                           ("granadas", lambda r: r["tipo"] == "granada")):
        sel = [r for r in res if filtro(r)]
        for met in ("solido", "hitchcock"):
            dcg = [abs(r[met]["cg"] - r["cg_med"]) for r in sel]
            ix = [r[met]["ix"] for r in sel]
            iy = [r[met]["iy"] for r in sel]
            print(f"{classe:28s} {met:9s}: |ΔCG| até {max(dcg):.2f} cal; Ix {min(ix):.2f}-{max(ix):.2f}; "
                  f"Iy {min(iy):.2f}-{max(iy):.2f}")
    return res


if __name__ == "__main__":
    main()
