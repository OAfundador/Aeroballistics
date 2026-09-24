"""O caso de validação do relatório: 175 mm M437 (Tabela 14, p. 65), só a partir da geometria.

    python examples/01_caso_m437.py
    python examples/01_caso_m437.py --csv        # grava também output/exemplos/m437.csv

É o mesmo que ``spin73 --exemplo``, pela biblioteca: o cartão de entrada impresso no relatório
(``spin73.M437``) passa pelo programa reconstruído, que devolve as 24 colunas nos 17 Mach da
grade, com a análise de estabilidade. A comparação célula a célula com a tabela impressa em
1973, separando o que é validação independente do que é circular, está em
tests/test_modelo_completo.py e em scripts/reconstrucao/comparacao_erros.py.
"""
from __future__ import annotations

import argparse

from _bootstrap import SAIDA, preparar

preparar()

import spin73  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", action="store_true", help="grava a tabela em output/exemplos/m437.csv")
    args = ap.parse_args()

    p = spin73.M437                      # VL, VN, VB, VCG... como no cartão impresso
    t = spin73.tabela(p)                 # {"MACH": array(17), "CX": array(17), ...}
    print(spin73.formatar(t, titulo=p.nome))
    print()
    for aviso in spin73.avisos(p):       # limitações da reconstrução que afetam este projétil
        print("aviso:", aviso)

    if args.csv:
        SAIDA.mkdir(parents=True, exist_ok=True)
        spin73.salvar_csv(t, str(SAIDA / "m437.csv"))
        print("\ngravado:", SAIDA / "m437.csv")


if __name__ == "__main__":
    main()
