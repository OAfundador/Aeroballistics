"""Linha de comando: python -m spin73 (ou o comando `spin73`, depois de instalado)."""
from __future__ import annotations

import sys

from . import correcoes as _corr
from .aero import Aerodinamica
from .nucleo import M437, Projetil, avisos, formatar, ler_entrada, salvar_csv


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="spin73",
        description="SPIN-73 reconstruído: coeficientes aerodinâmicos e estabilidade de um "
                    "projétil estabilizado por rotação, a partir da geometria.")
    ap.add_argument("--entrada", help="arquivo 'CHAVE = valor' com o cartão de entrada")
    ap.add_argument("--exemplo", action="store_true",
                    help="roda o caso de validação do relatório (175 mm M437)")
    for nome, ajuda in (("VL", "comprimento total, cal"), ("VN", "ogiva, cal"),
                        ("VB", "boattail, cal"), ("VCG", "CG a partir do nariz, cal"),
                        ("DIA", "diâmetro, in"), ("IX", "inércia axial, lb·in²"),
                        ("IY", "inércia transversal, lb·in²"), ("WGT", "peso, lb"),
                        ("TWIST", "passo de raia, cal/volta"), ("DM", "meplat, cal"),
                        ("BD", "cinta, cal"), ("OR", "raio da ogiva, cal"),
                        ("TEMP", "temperatura, °F")):
        ap.add_argument(f"--{nome}", type=float, help=ajuda)
    ap.add_argument("--nome", default="")
    ap.add_argument("--correcao", action="append", default=[],
                    help=f"correção opcional, pode repetir ({', '.join(_corr.disponiveis())}; "
                         "'voo_livre:CX0' para só um coeficiente)")
    ap.add_argument("--d-mm", type=float, dest="d_mm",
                    help="diâmetro real em mm (exigido por correções de escala, se não houver --DIA)")
    ap.add_argument("--csv", help="grava todas as colunas neste arquivo CSV")
    a = ap.parse_args(argv)

    if a.exemplo:
        p = M437
    elif a.entrada:
        p = ler_entrada(a.entrada)
    else:
        campos = {k: v for k, v in vars(a).items()
                  if k not in ("entrada", "exemplo", "csv", "correcao", "d_mm") and v not in (None, "")}
        faltam = [k for k in ("VL", "VN", "VB", "VCG") if k not in campos]
        if faltam:
            ap.error("informe --exemplo, --entrada ou pelo menos --VL --VN --VB --VCG "
                     f"(faltam: {', '.join(faltam)})")
        p = Projetil(**campos)

    aero = Aerodinamica(p, a.correcao or None, d_mm=a.d_mm)
    t = aero.tabela
    titulo = f"SPIN-73 reconstruído -- {p.nome or 'projétil'}"
    if aero.correcoes:
        titulo += " -- COM CORREÇÃO: " + ", ".join(c.nome for c in aero.correcoes)
    print(formatar(t, titulo))
    print()
    print("AVISOS (limitações da reconstrução para esta geometria):")
    for x in avisos(p):
        print("  - " + x)
    if a.csv:
        salvar_csv(t, a.csv)
        print()
        print(f"CSV gravado em {a.csv}")


def _executar():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
