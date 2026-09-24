"""Coeficientes para um simulador 6DOF: os sete da formulação de McCoy, em qualquer Mach e α.

    python examples/02_simulador_6dof.py
    python examples/02_simulador_6dof.py --entrada examples/entradas/5in38_navy.txt
    python examples/02_simulador_6dof.py --npz       # grava output/exemplos/<nome>_sete.npz
    python examples/02_simulador_6dof.py --csv       # grava output/exemplos/<nome>_sete.csv

``aeroballistics.Aerodinamica`` calcula a aerodinâmica uma vez, no construtor, na grade de 17 Mach do
programa; cada chamada só interpola em Mach, então ela pode ficar dentro do laço de integração.

A conversão para os sete é deste exemplo, não da biblioteca: cada simulador escreve as suas
equações de um jeito, e a conversão tem de ser conferida contra elas. Esta é a da forma vetorial
de McCoy (*Modern Exterior Ballistics*, cap. 2), em que cada força e cada momento é um
coeficiente vezes um vetor geométrico:

    termo                vetor nas equações      módulo        o coeficiente tem de ser
    arrasto              V                       V             o C_D(M, α) inteiro
    sustentação          V² x − V (V·x) V/V      V² sen α      C_L / sen α
    tombamento           V × x                   V sen α       por sen α
    força de Magnus      V × x                   V sen α       por sen α
    momento de Magnus    V − (V·x) x             V sen α       por sen α (a secante)

Com ``convencao="moderna"`` (pd/V e qd/V: Cmq, Clp e os dois Magnus valem a METADE dos do
relatório) e a força axial CX = CX0 + CX2·sen²α positiva para trás, CX2 = CDδ² − CNα:

    CD   = CX·cos α + CNα·sen²α     D = A cos α + N sen α (projeção exata)
    CLA  = CNα·cos α − CX           L/sen α, com L = N cos α − A sen α
    CYP  = CNpα                     força de Magnus
    CNP  = Cmpα(α)                  momento de Magnus: secante (1° e 5° do SPIN-73, entre eles
                                    interpolada em sen²α, fora deles constante), par em α
    CLP  = Clp                      amortecimento de rolamento
    CMA  = CMα                      momento de tombamento, em torno do CG (positivo tomba)
    CMQ  = Cmq + Cmα̇                amortecimento em arfagem

Para α pequeno, CD → CD0 + (CDδ² − CX0/2)·sen²α e CLA → CLα = CNα − CX0; a diferença para a
forma de pequena guinada cresce com α (a 8° e Mach 2, 1 % no CD e 4 % no CLA do 5"/38).

Sinais: CMα > 0 tomba, como em McCoy. A força de Magnus fica com o sinal do SPIN-73 (CNpα < 0):
nas equações de McCoy ela age ao longo de V × x, e assim aponta ao longo de x × V; conferido
voando o 155 mm M107 num código independente de outra formulação (RigidFlightLab), em que o
sinal trocado desloca o tempo de voo em 0,5 %. Se o seu simulador põe a força em x × V, use
|CNpα| (src/aeroballistics/convencoes.py, item 7).

Saídas:

- ``--npz``: a grade que um simulador lê direto — ``mach_grid`` (100 Mach de 0,01 a 5),
  ``alpha_grid`` (101 ângulos de −10° a +10°, em radianos), CD, CLA e CNP em (Mach × α) e os
  outros quatro só em Mach, com os nomes das colunas acima. Acima de 10° a formulação de
  pequena guinada deixa de valer.
- ``--csv``: a tabela plana (Mach e as sete colunas) nos 17 Mach, sem a dependência em α: CD é
  o CD0 e CNP é a inclinação a 1°. Serve para conferir; para voar, prefira a grade.
"""
from __future__ import annotations

import argparse
import csv

import numpy as np

from _bootstrap import SAIDA, preparar

preparar()

import aeroballistics  # noqa: E402
from aeroballistics import unidades  # noqa: E402

# 5,56 mm M855 (McCoy, BRL-MR-3476, 1985, Fig. 3 e Tabela 1): geometria em calibres, CG a
# 1,54 cal da base, diâmetro 5,69 mm. Meplat não cotado: fica o padrão do programa (0,12).
M855 = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9, BD=1.00,
                               DIA=5.69 / 25.4, nome="5,56 mm M855")

SETE = ("CD", "CLA", "CYP", "CNP", "CLP", "CMA", "CMQ")
DEPENDEM_DE_ALFA = ("CD", "CLA", "CNP")

#: A grade do --npz.
GRADE_MACH = np.linspace(0.01, 5.0, 100)
GRADE_ALFA = np.radians(np.linspace(-10.0, 10.0, 101))


def sete(aero: aeroballistics.Aerodinamica, mach, alfa_rad=0.0) -> dict:
    """Os sete coeficientes no(s) Mach pedido(s), no ângulo de ataque total α (radianos).

    ``aero`` na convenção moderna. Mach e α podem ser arrays do mesmo formato (ou difundíveis).
    """
    if aero.convencao != "moderna":
        raise ValueError("sete() lê a convenção moderna: Aerodinamica(p, convencao='moderna')")
    c = aero(mach)
    s = np.sin(alfa_rad)
    cna = c.CNa
    axial = c.CD0 + (c.CDd2 - cna) * s * s          # CX0 + CX2·sen²α, positiva para trás
    return {
        "CD": axial * np.cos(alfa_rad) + cna * s * s,
        "CLA": cna * np.cos(alfa_rad) - axial,
        "CYP": c.CNpa,
        "CNP": aero.momento_magnus(mach, alfa_rad),
        "CLP": c.Clp,
        "CMA": c.Cma,
        "CMQ": c.Cmq_Cmad,
    }


def grade(aero: aeroballistics.Aerodinamica, mach=GRADE_MACH, alfa=GRADE_ALFA) -> dict:
    """Os sete numa grade: os três que dependem de α em (Mach × α), os outros só em Mach."""
    M, A = np.meshgrid(mach, alfa, indexing="ij")
    k2 = sete(aero, M, A)
    k1 = sete(aero, mach, 0.0)
    out = {"mach_grid": np.asarray(mach, float), "alpha_grid": np.asarray(alfa, float)}
    for n in SETE:
        out[n] = np.asarray(k2[n] if n in DEPENDEM_DE_ALFA else k1[n], float)
    return out


def _nome_arquivo(p) -> str:
    nome = (p.nome or "projetil").lower()
    return "".join(ch if ch.isalnum() else "_" for ch in nome).strip("_")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrada", help="cartão 'CHAVE = valor' (padrão: o 5,56 mm M855 deste exemplo)")
    ap.add_argument("--npz", action="store_true", help="grava a grade (Mach × α) em output/exemplos/")
    ap.add_argument("--csv", action="store_true", help="grava a tabela plana (Mach + sete colunas)")
    args = ap.parse_args(argv)

    p = unidades.ler_entrada(args.entrada)[0] if args.entrada else M855
    aero = aeroballistics.Aerodinamica(p, convencao="moderna")    # o canônico, na convenção de McCoy
    print(aero.descrever())
    print("coeficientes disponíveis:", ", ".join(aero.nomes))

    # Num integrador, a cada passo: M = V/a e α = ângulo de ataque total.
    for graus in (0.0, 2.0, 8.0):
        alfa = np.radians(graus)
        print(f"\nOs sete a α = {graus:.0f}°:")
        print("  Mach " + "".join(f"{n:>9s}" for n in SETE))
        for M in (0.6, 0.9, 1.1, 1.5, 2.0, 2.5, 3.0):
            k = sete(aero, M, alfa)
            print(f"  {M:4.2f} " + "".join(f"{float(k[n]):9.4f}" for n in SETE))

    # Vetorizado: arrays de Mach (e de α) de uma vez.
    machs = np.linspace(0.7, 2.8, 4)
    print("\nCMA vetorizado em", np.round(machs, 2), "->", np.round(aero.coeficiente("Cma", machs), 4))

    base = _nome_arquivo(p)
    if args.npz:
        SAIDA.mkdir(parents=True, exist_ok=True)
        arquivo = SAIDA / f"{base}_sete.npz"
        np.savez_compressed(arquivo, **grade(aero))
        print("\ngravado:", arquivo)

    if args.csv:
        SAIDA.mkdir(parents=True, exist_ok=True)
        arquivo = SAIDA / f"{base}_sete.csv"
        g = aeroballistics.MACH_GRID
        k = sete(aero, g, 0.0)
        k["CNP"] = aero.coeficiente("Cmpa", g)             # inclinação a 1°
        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Mach", *SETE])
            for j, M in enumerate(g):
                w.writerow([f"{M:g}", *(f"{float(k[n][j]):.6g}" for n in SETE)])
        print("\ngravado:", arquivo)


if __name__ == "__main__":
    main()
