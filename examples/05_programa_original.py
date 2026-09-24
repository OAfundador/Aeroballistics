"""O programa de 1973 como objetos: de onde vem cada coluna.

    python examples/05_programa_original.py              # o bloco do CMα
    python examples/05_programa_original.py CMQ GYRO     # os blocos dessas colunas

``aeroballistics.programa.SPIN73`` descreve o programa original bloco a bloco, com as nossas palavras
e a nossa notação: fórmulas, regras, blocos DATA usados, statements do listing em que a
leitura se baseou, o que não foi possível ler e a função que implementa cada bloco aqui. O
listing não é reproduzido; ele está no relatório (DTIC AD0915628). O programa inteiro, em
Markdown, está em docs/PROGRAMA_ORIGINAL.md (``aeroballistics --programa`` imprime o mesmo em texto).
"""
from __future__ import annotations

import argparse

import numpy as np

from _bootstrap import preparar

preparar()

import aeroballistics  # noqa: E402
from aeroballistics.programa import SPIN73  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("colunas", nargs="*", default=["CMA"], help="colunas de saída (CX, CNA, CMA, GYRO...)")
    args = ap.parse_args()

    print("Blocos, na ordem em que o programa calcula:")
    for b in SPIN73:
        print(f"  {b.chave:14s} {', '.join(b.colunas) or '—'}")

    for coluna in args.colunas:
        b = SPIN73.de_coluna(coluna)
        print("\n" + "-" * 90)
        print(b)
        valores = b.calcular(aeroballistics.M437)            # pelo programa inteiro, para o 175 mm M437
        print(f"\n  {coluna} do M437 nos 17 Mach:", np.round(valores[coluna], 4))


if __name__ == "__main__":
    main()
