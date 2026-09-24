"""Entrada em unidades métricas e estimativa de CG e inércias (duas adições opcionais).

    python examples/03_unidades_e_massa.py

O cartão do SPIN-73 pede calibres, polegadas, libras e lb·in², e recebe o CG e as inércias
como entrada. Aqui o 5,56 mm M855 entra em mm e gramas, sem CG nem inércias
(examples/entradas/m855_metrico.txt), e ``spin73.massa`` os estima pela geometria e pela
massa. O M855 tem CG e inércias medidos (McCoy, BRL-MR-3476, 1985, Tabela 1), então dá para
ver quanto a estimativa erra e o quanto isso muda o fator de estabilidade giroscópica.

A estimativa muda ENTRADAS, não o modelo; nada disso é aplicado sem ser pedido.
"""
from __future__ import annotations

from _bootstrap import ENTRADAS, preparar

preparar()

import spin73  # noqa: E402
from spin73 import massa, unidades  # noqa: E402

# Medido (McCoy 1985, Tabela 1): CG a partir da BASE em calibres; inércias em g·cm².
MEDIDO = dict(CG_BASE=1.54, IX_GCM2=0.1426, IY_GCM2=1.150)


def main() -> None:
    p, opcoes = unidades.ler_entrada(str(ENTRADAS / "m855_metrico.txt"))
    print(f"{p.nome}: DIA {p.DIA:.4f} pol, WGT {p.WGT:.5f} lb, TWIST {p.TWIST:.2f} cal/volta")
    print("falta no cartão:", ", ".join(massa.o_que_falta(p)))
    print("opções da estimativa no arquivo:", opcoes)

    ang_bt = opcoes.get("ANG_BT")                      # ângulo do boattail, graus
    print(f"\n{'método':8s} {'CG da base':>10s} {'Ix g·cm²':>9s} {'Iy g·cm²':>9s}   estimado/medido")
    print(f"{'medido':8s} {MEDIDO['CG_BASE']:10.3f} {MEDIDO['IX_GCM2']:9.4f} {MEDIDO['IY_GCM2']:9.3f}")
    for metodo in ("solido", "bala"):
        pm = massa.estimar(p, metodo, ang_bt=ang_bt)
        print(f"{metodo:8s} {pm.cg_base:10.3f} {pm.ix_gcm2:9.4f} {pm.iy_gcm2:9.3f}   "
              f"CG {pm.cg_base - MEDIDO['CG_BASE']:+.3f} cal, Ix ×{pm.ix_gcm2 / MEDIDO['IX_GCM2']:.3f}, "
              f"Iy ×{pm.iy_gcm2 / MEDIDO['IY_GCM2']:.3f}")
    print("\n" + str(massa.estimar(p, "solido", ang_bt=ang_bt)))

    # O cartão completado pela estimativa e o cartão com os valores medidos.
    estimado = massa.completar(p, "solido", ang_bt=ang_bt)
    medido = unidades.projetil(nome="M855 (medido)", VL=p.VL, VN=p.VN, VB=p.VB, OR=p.OR, DM=p.DM,
                               BD=p.BD, D_MM=5.69, MASSA_G=4.05, PASSO_POL=7, TEMP_C=15, **MEDIDO)
    t_est, t_med = spin73.tabela(estimado), spin73.tabela(medido)
    print("\nFator de estabilidade giroscópica s_g (GYRO):")
    print(f"  {'Mach':>5s} {'medido':>8s} {'estimado':>9s}")
    for j, M in enumerate(t_med["MACH"]):
        if M in (0.6, 1.0, 1.5, 2.0, 2.5, 3.0):
            print(f"  {M:5.2f} {t_med['GYRO'][j]:8.3f} {t_est['GYRO'][j]:9.3f}")


if __name__ == "__main__":
    main()
