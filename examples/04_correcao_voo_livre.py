"""A correção de voo livre (adição opcional) contra o SPIN-73 canônico.

    python examples/04_correcao_voo_livre.py

O SPIN-73 trabalha em calibres e não sabe o tamanho real do projétil, então não vê o efeito
do número de Reynolds no arrasto, que pesa nas armas portáteis. A correção "voo_livre" foi
ajustada a medições de voo livre publicadas (scripts/voo_livre/correcao/ajuste.py) e só
guarda o que a validação cruzada, deixando um grupo de projéteis de fora de cada vez,
aceitou. Ela precisa do diâmetro real: do DIA do cartão ou de ``d_mm``.

"voo_livre" aplica todas as peças aceitas; "voo_livre:CX0" só a do arrasto, a mais firme.
Detalhes em docs/voo_livre/CORRECAO.md e docs/BIBLIOTECA.md.
"""
from __future__ import annotations

from _bootstrap import preparar

preparar()

import aeroballistics  # noqa: E402
from aeroballistics.correcoes.voo_livre import VooLivre  # noqa: E402

M855 = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9, BD=1.00,
                       DIA=5.69 / 25.4, nome="5,56 mm M855")


def main() -> None:
    canonico = aeroballistics.Aerodinamica(M855)
    so_cx0 = aeroballistics.Aerodinamica(M855, correcoes="voo_livre:CX0")
    tudo = aeroballistics.Aerodinamica(M855, correcoes="voo_livre")
    print(tudo.descrever())

    print(f"\n{'Mach':>5s} {'CX0 1973':>9s} {'voo_livre:CX0':>14s} {'dif.':>7s}   "
          f"{'CNA 1973':>9s} {'voo_livre':>10s}")
    for M in (0.6, 0.8, 0.9, 1.1, 1.5, 2.0, 2.5, 3.0):
        a, b = canonico(M), so_cx0(M)
        c = tudo(M)
        print(f"{M:5.2f} {a.CX0:9.4f} {b.CX0:14.4f} {100 * (b.CX0 / a.CX0 - 1):+6.1f}%   "
              f"{a.CNA:9.4f} {c.CNA:10.4f}")

    print("\nValidação cruzada (erro relativo médio nos grupos deixados de fora):")
    print(f"  {'coef.':5s} {'regime':12s} {'SPIN-73':>8s} {'corrigido':>9s} {'melhoram':>9s} "
          f"{'pior razão':>10s}  aceita?")
    for coef, regimes in VooLivre().validacao().items():
        for regime, v in regimes.items():
            print(f"  {coef:5s} {regime:12s} {v['spin73']:8.3f} {v['corrigido']:9.3f} "
                  f"{v['grupos_que_melhoram']:4d} de {v['grupos']:<2d} {v['pior_razao']:10.2f}  "
                  f"{'sim' if v['aceita'] else 'não'}")


if __name__ == "__main__":
    main()
