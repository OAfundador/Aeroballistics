"""Confere a transcrição de uma tabela SEM o modelo: identidades entre colunas impressas.

    CMA   = (VCG − CPN)·CNA          (definição do momento; cartão C212)
    CNPA  = CYPA·(VCG − CPF1)        (momento de Magnus a 1°)
    CNPA5 = CYPA·(VCG − CPF5)        (idem a 5°)
    CNPA3 + 0,1·CNPA5P = 3,75        (defeito do original, NOTAS T12)

Nenhuma usa DATA: uma linha que viola uma delas tem um dígito mal lido (ou uma entrada
VCG errada). A tolerância é a do arredondamento das colunas envolvidas.

    python tabelas/verificar_identidades.py 35
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import tabelas_impressas as ti      # noqa: E402


def violacoes(tb, vcg=None):
    c = tb.colunas
    vcg = tb.entrada.get("VCG") if vcg is None else vcg
    out = []
    for j, M in enumerate(c["MACH"]):
        def v(n):
            return c.get(n, np.full(17, np.nan))[j]
        testes = []
        if vcg is not None:
            testes += [
                ("CMA=(VCG-CPN)*CNA", v("CMA"), (vcg - v("CPN")) * v("CNA"),
                 0.0005 * (1 + v("CNA") + abs(vcg - v("CPN")))),
                ("CNPA=CYPA*(VCG-CPF1)", v("CNPA"), v("CYPA") * (vcg - v("CPF1")),
                 0.0005 * (1 + abs(v("CYPA")) + abs(vcg - v("CPF1")))),
                ("CNPA5=CYPA*(VCG-CPF5)", v("CNPA5"), v("CYPA") * (vcg - v("CPF5")),
                 0.0005 * (1 + abs(v("CYPA")) + abs(vcg - v("CPF5")))),
            ]
        testes.append(("CNPA3+0,1*CNPA5P=3,75", v("CNPA3") + 0.1 * v("CNPA5P"), 3.75, 0.0006))
        for nome, a, b, tol in testes:
            if np.isfinite(a) and np.isfinite(b) and abs(a - b) > tol:
                out.append((round(float(M), 2), nome, round(float(a), 4), round(float(b), 4)))
    return out


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for pag in map(int, sys.argv[1:]):
        tb = ti.carregar(pag)
        v = violacoes(tb)
        print(f"p. {pag} {tb.nome}: {len(v)} violação(ões)")
        for x in v:
            print("   Mach {:5} {:24s} {} x {}".format(*x))
