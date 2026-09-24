"""
Todos os casos do relatório: o programa reconstruído roda com a entrada impressa de cada
tabela de 1973 e cada saída legível é comparada com a impressa.

Casos: o 175 mm M437 (m437_tabela.csv, com estabilidade) e as demais tabelas completas,
uma por página, todas em data/tabelas_1973/. Entradas ilegíveis no cabeçalho foram decididas, cada uma,
por uma coluna declarada no CSV; essa coluna fica circular naquele caso.

O erro de cada célula é medido em UNIDADES DA ÚLTIMA CASA IMPRESSA: numa coluna de 3
casas, 1 unidade = 0,001. Como o programa original arredondava para essa casa, até
±0,5 unidade o modelo é indistinguível dele; o critério do projeto é ±1,5 unidade.

Ficam fora das estatísticas (mas no CSV de cada caso, com o motivo):
  - circular: algum DATA ou entrada foi decidido usando esta célula (circularidade.py);
  - identidade: célula ambígua no scan, desambiguada por identidade entre colunas impressas
    (no M437, as três células que a transcrição marcou como ambíguas).

    python scripts/reconstrucao/comparacao_erros.py
      -> output/verificacao/casos/pNN_*.csv         cada caso, célula a célula
      -> output/verificacao/resumo_por_caso.csv     uma linha por caso
      -> output/verificacao/resumo_erros.csv        uma linha por coluna
      -> output/verificacao/erros_por_celula.csv    todas as células

O resumo impresso na tela é o de docs/VERIFICACAO.md.
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caminhos                                             # noqa: E402

import circularidade                                        # noqa: E402
import spin73 as s                                          # noqa: E402
import tabelas_impressas as ti                              # noqa: E402
import test_modelo_completo as tm                           # noqa: E402

SAIDA = caminhos.SAIDA / "verificacao"

MACH = [round(float(m), 2) for m in s.MACH_GRID]
CASAS = {"SPIN": 1, "W1": 2, "W2": 2, "DELT": 4, **{c: 6 for c in ("L1", "L2", "L15", "L25")}}
ORDEM = ["CX", "CX2", "CNA", "CPN", "CMA", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CNPA3",
         "CNPA5P", "CMQ", "CLP", "GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2",
         "L1", "L2", "L15", "L25", "DELT", "DISP"]


def casos():
    """(página, nome, entrada decidida, tabela calculada, colunas impressas, circulares, identidade)."""
    circ437 = {**{k: "decidido com esta tabela (test_modelo_completo.CIRCULARES)"
                  for k in tm.CIRCULARES}, **circularidade.circulares(65)}
    # células que a transcrição antiga marcou como ambíguas no scan (não são erro do modelo)
    amb437 = {k: v for k, v in tm.PENDENTES.items() if "célula impressa" in v}
    out = [(65, "175 mm M437", {}, s.tabela(s.M437), tm.TAB, circ437, amb437)]
    for tb in ti.todas():
        out.append((tb.pagina, tb.nome, tb.decididas(), s.tabela(tb.projetil()), tb.colunas,
                    circularidade.circulares(tb.pagina, tb), tb.identidade))
    return sorted(out, key=lambda c: c[0])


def celulas(caso):
    pag, nome, _, calc, imp, circ, ident = caso
    for col in ORDEM:
        if col not in imp or col not in calc:
            continue
        for j, M in enumerate(MACH):
            v = imp[col][j]
            if not np.isfinite(v):
                continue
            casas = CASAS.get(col, 3)
            m = float(calc[col][j])
            un = abs(m - v) * 10 ** casas if np.isfinite(m) else np.inf
            if (col, M) in ident:
                st = "identidade"
            elif (col, M) in circ:
                st = "circular"
            else:
                st = "independente"
            yield dict(pagina=pag, caso=nome, coluna=col, mach=M, impresso=float(v),
                       modelo=round(m, 7), erro_em_unidades=round(un, 2), situacao=st,
                       motivo=circ.get((col, M), "") if st == "circular" else "")


def estat(u):
    u = np.asarray(u, float)
    if not u.size:
        return dict(n=0, ate_05=np.nan, ate_15=np.nan, mediana=np.nan, maximo=np.nan)
    return dict(n=u.size, ate_05=100 * np.mean(u <= 0.5), ate_15=100 * np.mean(u <= 1.5),
                mediana=float(np.median(u)), maximo=float(u.max()))


def _slug(nome):
    return re.sub(r"[^a-z0-9]+", "_", nome.lower()).strip("_")


def main():
    (SAIDA / "casos").mkdir(parents=True, exist_ok=True)
    todas, por_caso = [], []
    campos = ["pagina", "caso", "coluna", "mach", "impresso", "modelo", "erro_em_unidades",
              "situacao", "motivo"]
    for caso in casos():
        cel = list(celulas(caso))
        todas += cel
        pag, nome, decididas = caso[:3]
        with open(SAIDA / "casos" / f"p{pag:02d}_{_slug(nome)}.csv", "w", newline="",
                  encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(cel)
        ind = [c["erro_em_unidades"] for c in cel if c["situacao"] == "independente"]
        e = estat(ind)
        pior = max((c for c in cel if c["situacao"] == "independente"),
                   key=lambda c: c["erro_em_unidades"], default=None)
        por_caso.append(dict(
            pagina=pag, caso=nome, celulas_legiveis=len(cel), independentes=e["n"],
            circulares=sum(c["situacao"] == "circular" for c in cel),
            por_identidade=sum(c["situacao"] == "identidade" for c in cel),
            pct_ate_05=round(e["ate_05"], 1), pct_ate_15=round(e["ate_15"], 1),
            mediana_un=round(e["mediana"], 2),
            pior=(f"{pior['coluna']} Mach {pior['mach']:g}: impresso {pior['impresso']:.{CASAS.get(pior['coluna'], 3)}f}, "
                  f"modelo {pior['modelo']:.{CASAS.get(pior['coluna'], 3) + 1}f}" if pior else ""),
            entradas_decididas=" ".join(f"{k}={v:g}" for k, v in decididas.items() if "#" not in k)))

    with open(SAIDA / "erros_por_celula.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(todas)
    with open(SAIDA / "resumo_por_caso.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(por_caso[0]))
        w.writeheader()
        w.writerows(por_caso)

    ind = [c for c in todas if c["situacao"] == "independente"]
    e = estat([c["erro_em_unidades"] for c in ind])
    sem_m1 = estat([c["erro_em_unidades"] for c in ind if c["pagina"] != 44])
    print(f"{len(por_caso)} casos, {len(todas)} células legíveis: {len(ind)} independentes, "
          f"{sum(c['situacao'] == 'circular' for c in todas)} circulares, "
          f"{sum(c['situacao'] == 'identidade' for c in todas)} desambiguadas por identidade")
    print(f"Independentes: {e['ate_05']:.0f} % indistinguíveis do original (±0,5 unidade), "
          f"{e['ate_15']:.0f} % no critério (±1,5), mediana {e['mediana']:.2f} unidade")
    print(f"Sem o M1 (pp. 44/47, geometria do cabeçalho não fecha): {sem_m1['n']} células, "
          f"{sem_m1['ate_05']:.0f} % / {sem_m1['ate_15']:.0f} %, mediana {sem_m1['mediana']:.2f}\n")

    print(f"{'p.':>3s} {'caso':24s} {'legív.':>6s} {'indep.':>6s} {'<=0,5':>6s} {'<=1,5':>6s} "
          f"{'mediana':>7s}  pior célula independente")
    for r in por_caso:
        print(f"{r['pagina']:3d} {r['caso'][:24]:24s} {r['celulas_legiveis']:6d} {r['independentes']:6d} "
              f"{r['pct_ate_05']:5.0f}% {r['pct_ate_15']:5.0f}% {r['mediana_un']:7.2f}  {r['pior']}")

    print(f"\n{'coluna':8s} {'casos':>5s} {'células':>7s} {'<=0,5':>6s} {'<=1,5':>6s} {'mediana':>8s}")
    resumo = []
    for col in ORDEM:
        c = [x for x in ind if x["coluna"] == col and x["pagina"] != 44]
        if not c:
            continue
        e = estat([x["erro_em_unidades"] for x in c])
        ncasos = len({x["pagina"] for x in c})
        resumo.append((col, ncasos, e))
        print(f"{col:8s} {ncasos:5d} {e['n']:7d} {e['ate_05']:5.0f}% {e['ate_15']:5.0f}% {e['mediana']:8.2f}")
    with open(SAIDA / "resumo_erros.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["coluna", "casos", "celulas_independentes", "pct_ate_0.5_unidade",
                    "pct_ate_1.5_unidade", "mediana_unidades", "max_unidades"])
        for col, n, e in resumo:
            w.writerow([col, n, e["n"], round(e["ate_05"], 1), round(e["ate_15"], 1),
                        round(e["mediana"], 2), round(e["maximo"], 1)])


if __name__ == "__main__":
    main()
