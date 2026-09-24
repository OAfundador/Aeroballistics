"""Coeficientes para um simulador 6DOF: os sete da formulação de McCoy, em qualquer Mach.

    python examples/02_simulador_6dof.py
    python examples/02_simulador_6dof.py --csv       # grava também output/exemplos/m855_sete.csv

``spin73.Aerodinamica`` calcula a aerodinâmica uma vez, no construtor, na grade de 17 Mach do
programa; cada chamada só interpola em Mach, então ela pode ficar dentro do laço de integração.

Com ``convencao="moderna"`` as taxas são adimensionalizadas por pd/V e qd/V, como em McCoy
(*Modern Exterior Ballistics*, cap. 2): Cmq, Clp e os dois Magnus valem a METADE dos do
relatório, que usa pd/2V. Os sete coeficientes que as equações de McCoy leem saem assim:

    CD   = CD0 + CDδ²·sen²α     arrasto, eixos de vento
    CLA  = CLα = CNα − CX0      sustentação
    CYP  = CNpα                 força de Magnus
    CNP  = Cmpα(α)              momento de Magnus (secante: 1° e 5° do SPIN-73, entre eles
                                interpolado em sen²α, fora deles constante)
    CLP  = Clp                  amortecimento de rolamento
    CMA  = CMα                  momento de tombamento, em torno do CG (positivo tomba)
    CMQ  = Cmq + Cmα̇            amortecimento em arfagem

Sinais: CMα > 0 tomba, como em McCoy. O sinal do Magnus muda de uma fonte para outra;
confira a definição do seu simulador (src/spin73/convencoes.py, item 7).

A tabela plana do --csv (Mach e as sete colunas) não tem a dependência em α: nela, CD é o CD0
e CNP é a inclinação a 1°. Onde o simulador aceitar funções de (Mach, α), use ``cd`` e ``cnp``.
"""
from __future__ import annotations

import argparse
import csv

import numpy as np

from _bootstrap import SAIDA, preparar

preparar()

import spin73  # noqa: E402

# 5,56 mm M855 (McCoy, BRL-MR-3476, 1985, Fig. 3 e Tabela 1): geometria em calibres, CG a
# 1,54 cal da base, diâmetro 5,69 mm. Meplat não cotado: fica o padrão do programa (0,12).
M855 = spin73.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9, BD=1.00,
                       DIA=5.69 / 25.4, nome="5,56 mm M855")

SETE = ("CD", "CLA", "CYP", "CNP", "CLP", "CMA", "CMQ")


def sete(aero: spin73.Aerodinamica, mach, alfa_rad=0.0) -> dict:
    """Os sete coeficientes no(s) Mach pedido(s), no ângulo de ataque total α (radianos)."""
    c = aero(mach)
    return {
        "CD": c.CD0 + c.CDd2 * np.sin(alfa_rad) ** 2,
        "CLA": c.CLa,
        "CYP": c.CNpa,
        "CNP": aero.momento_magnus(mach, alfa_rad),
        "CLP": c.Clp,
        "CMA": c.Cma,
        "CMQ": c.Cmq_Cmad,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", action="store_true",
                    help="grava a tabela plana (Mach + sete colunas) em output/exemplos/m855_sete.csv")
    args = ap.parse_args()

    aero = spin73.Aerodinamica(M855, convencao="moderna")    # o canônico, só na convenção de McCoy
    print(aero.descrever())
    print("coeficientes disponíveis:", ", ".join(aero.nomes))

    # Num integrador, a cada passo: M = V/a e α = ângulo de ataque total.
    alfa = np.radians(2.0)
    print(f"\nOs sete a α = {np.degrees(alfa):.0f}°:")
    print("  Mach " + "".join(f"{n:>9s}" for n in SETE))
    for M in (0.6, 0.9, 1.1, 1.5, 2.0, 2.5, 3.0):
        k = sete(aero, M, alfa)
        print(f"  {M:4.2f} " + "".join(f"{k[n]:9.4f}" for n in SETE))

    # Vetorizado: arrays de Mach (e de α) de uma vez.
    machs = np.linspace(0.7, 2.8, 4)
    print("\nCMA vetorizado em", np.round(machs, 2), "->", np.round(aero.coeficiente("Cma", machs), 4))

    # Os dois que dependem de α, como funções de (Mach, α), para simuladores que as aceitam.
    def cd(M, a):
        return aero.coeficiente("CD0", M) + aero.coeficiente("CDd2", M) * np.sin(a) ** 2

    def cnp(M, a):
        return aero.momento_magnus(M, a)

    print(f"\nMach 2: CD a 0° = {cd(2.0, 0.0):.4f}, a 5° = {cd(2.0, np.radians(5)):.4f}; "
          f"CNP a 1° = {cnp(2.0, np.radians(1)):.4f}, a 5° = {cnp(2.0, np.radians(5)):.4f}")

    if args.csv:
        SAIDA.mkdir(parents=True, exist_ok=True)
        arquivo = SAIDA / "m855_sete.csv"
        grade = spin73.MACH_GRID
        k = sete(aero, grade, 0.0)
        k["CNP"] = aero.coeficiente("Cmpa", grade)             # inclinação a 1°
        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Mach", *SETE])
            for j, M in enumerate(grade):
                w.writerow([f"{M:g}", *(f"{k[n][j]:.6g}" for n in SETE)])
        print("\ngravado:", arquivo)


if __name__ == "__main__":
    main()
