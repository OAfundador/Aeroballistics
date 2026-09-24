"""O caso de validação do relatório: 175 mm M437 (Tabela 14, p. 65), só a partir da geometria.

    python examples/01_caso_m437.py
    python examples/01_caso_m437.py --csv        # grava também output/exemplos/m437.csv

É o mesmo que ``aeroballistics --exemplo``, pela biblioteca: o cartão de entrada impresso no relatório
(``aeroballistics.M437``) passa pelo programa adaptado, que devolve as 24 colunas nos 17 Mach da
grade, com a análise de estabilidade. A comparação célula a célula com a tabela impressa em
1973, separando o que é validação independente do que é circular, está em
tests/test_modelo_completo.py e em scripts/adaptacao/comparacao_erros.py.
"""
from __future__ import annotations

import argparse

from _bootstrap import SAIDA, preparar

preparar()

import aeroballistics  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", action="store_true", help="grava a tabela em output/exemplos/m437.csv")
    args = ap.parse_args()

    p = aeroballistics.M437                      # VL, VN, VB, VCG... como no cartão impresso
    t = aeroballistics.tabela(p)                 # {"MACH": array(17), "CX": array(17), ...}
    print(aeroballistics.formatar(t, titulo=p.nome))
    print()
    for aviso in aeroballistics.avisos(p):       # limitações da adaptação que afetam este projétil
        print("aviso:", aviso)

    if args.csv:
        SAIDA.mkdir(parents=True, exist_ok=True)
        aeroballistics.salvar_csv(t, str(SAIDA / "m437.csv"))
        print("\ngravado:", SAIDA / "m437.csv")


if __name__ == "__main__":
    main()
