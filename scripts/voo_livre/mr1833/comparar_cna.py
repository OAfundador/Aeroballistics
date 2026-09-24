"""
CNα do SPIN-73 adaptado contra o voo livre do BRL MR 1833 (7,62 NATO).

Viés por projétil, rodada a rodada (M ≥ 1,1), como em `comparar_cmq_cp.py`: média de
(modelo − experimento), com a curva do modelo nos 17 pontos da grade e interpolação linear
em Mach entre eles. O CNα do MR 1833 já está na convenção do SPIN-73 (por radiano).

HIPÓTESES:
  - o raio de ogiva da família 7,62 é incerto (figura indica "30R" ≈ 9,74 cal); a
    sensibilidade a ele é reportada;
  - o M-62 tem base arredondada, que o SPIN-73 não representa; entra com VB aproximado.

A primeira comparação (NOTAS_TRANSCRICAO.md, T5) dava +0,28 no M-80. Ela é anterior ao
cartão C205 (NOTAS, T15), que zera a força normal do boattail quando ela sai positiva; a
saída repete a conta sem o cartão para mostrar que a diferença vem dele.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import caminhos                                    # noqa: E402,F401  (também põe a saída em UTF-8)

import recalibrar_mr1833 as r                      # noqa: E402
from ajustar_B import regressores                  # noqa: E402
from cna_spin73 import cna_j                       # noqa: E402
from comparar_cmq_cp import MACH, OR_HIP, PROJETEIS, contra_ajuste, por_rodada  # noqa: E402
from aeroballistics.dados.xb_lidos import XB               # noqa: E402


def curva_cna(g, OR=OR_HIP, c205=True):
    """CNα do SPIN-73 nos 17 pontos. `c205=False` desliga o cartão C205 (a parcela do
    boattail volta a poder ser positiva), como na adaptação anterior a ele."""
    if c205:
        return np.array([cna_j(g["VL"], g["VN"], g["VB"], OR, j) for j in range(17)])
    return np.array([np.array(regressores(g["VL"], g["VN"], g["VB"], OR, M)) @ XB[:, j]
                     for j, M in enumerate(MACH)])


if __name__ == "__main__":
    lin = r.tabela()
    ep, npar = r.erro_puro(lin, "CNA", PROJETEIS)

    print("=" * 78)
    print(f"CNα (1/rad) -- SPIN-73 adaptado contra o MR 1833, M ≥ {r.MMIN}, OR = {OR_HIP} cal")
    print("=" * 78)
    print(f"{'proj':6s} {'n':>3s} {'viés do SPIN-73':>16s} {'dispersão exp':>14s} {'erro puro/√n':>13s}")
    for p, n, vies, sd in por_rodada(lin, "CNA", curva_cna):
        marca = "  <-- viés maior que a dispersão" if abs(vies) > sd else ""
        print(f"{p:6s} {n:3d} {vies:+16.3f} {sd:14.3f} {ep / np.sqrt(n):13.3f}{marca}")
    print(f"\nerro puro entre rodadas repetidas: {ep:.3f} ({npar} pares)")

    print("\nViés com outro raio de ogiva suposto, e sem o cartão C205:")
    print(f"  {'':16s}" + "".join(f"{p:>9s}" for p in PROJETEIS))
    for rotulo, curva in (("OR =  8.00 cal", lambda g: curva_cna(g, 8.0)),
                          ("OR = 12.00 cal", lambda g: curva_cna(g, 12.0)),
                          ("sem o C205", lambda g: curva_cna(g, c205=False))):
        print(f"  {rotulo + ':':16s}" + "".join(f"{v:+9.3f}" for _, _, v, _ in por_rodada(lin, "CNA", curva)))

    print("\nContra a curva experimental ajustada por MMQ (constante + CXLL, quadráticos em")
    print("M − 2, o modelo reduzido de recalibrar_mr1833.py):")
    print(f"{'proj':6s} {'Mach':>5s} {'experimento':>13s} {'SPIN-73':>9s} {'dif':>8s}")
    for p, M, exp, err, mod in contra_ajuste(lin, "CNA", curva_cna, np.array([1.2, 1.5, 2.0, 2.5])):
        print(f"{p:6s} {M:5.2f} {exp:8.3f}±{err:<5.3f} {mod:8.3f} {mod - exp:+8.3f}")
