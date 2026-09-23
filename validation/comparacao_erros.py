"""
Quanto a reconstrução erra: o programa (só a geometria) contra TODAS as tabelas de 1973
transcritas até agora.

O erro de cada célula é medido em UNIDADES DA ÚLTIMA CASA IMPRESSA: numa coluna de 3
casas, 1 unidade = 0,001. Como o programa original arredondava para essa casa, até
±0,5 unidade o modelo é indistinguível dele; o critério do projeto é ±1,5 unidade.

Células em que algum DATA foi DECIDIDO usando a própria tabela (circulares) são contadas
à parte: elas mostram que a decisão é coerente, mas não validam nada.

    python validation/comparacao_erros.py        -> resumo + validation/erros_por_celula.csv
"""
import csv
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(AQUI, "..", "python")
for sub in ("", "reconstrucao_A", "reconstrucao_B", "reconstrucao_C", "reconstrucao_D",
            "reconstrucao_F"):
    sys.path.insert(0, os.path.join(PY, sub))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import spin73 as s                                          # noqa: E402
import magnus_clp as mc                                     # noqa: E402
import test_modelo_completo as tm                           # noqa: E402
from dados_cna import T as T_CNA                            # noqa: E402
from dados_cx import CX_538                                 # noqa: E402
from dados_cx2 import CX2_538, DECIDIDAS as CX2_DEC_538     # noqa: E402
from dados_cpn import CMA_538, CPN_538                      # noqa: E402
from xb_lidos import CORRECOES as XB_CORR                   # noqa: E402
from xd_lidos import DECIDIDOS as XD_DEC                    # noqa: E402

MACH = [round(float(m), 2) for m in s.MACH_GRID]
K = s.CoefAjuste.do_listing()
CASAS = {"SPIN": 1, "W1": 2, "W2": 2, "DELT": 4, **{c: 6 for c in ("L1", "L2", "L15", "L25")}}
linhas = []          # (tabela, coluna, Mach, impresso, modelo, independente)


def registra(tab, col, modelo, impresso, circulares=(), casas=None):
    for j, M in enumerate(MACH):
        imp = impresso[j]
        if imp is None or not np.isfinite(imp):
            continue
        linhas.append((tab, col, M, float(imp), float(modelo[j]),
                       j not in circulares, casas or CASAS.get(col, 3)))


# 1. 175 mm M437 inteiro (p. 65)
t437 = s.tabela(s.M437)
for col in tm.COLUNAS:
    circ = {j for j, M in enumerate(MACH) if (col, M) in tm.CIRCULARES}
    registra("175 mm M437", col, t437[col], tm.TAB[col], circ)

# 2. CNα em 10 tabelas: as 6 correções de XB foram decididas por elas
circ_xb = {j for (_, j) in XB_CORR}
for pag, (nome, VL, VN, VB, OR, cna) in T_CNA.items():
    if pag == 65:
        continue
    p = s.Projetil(VL=VL, VN=VN, VB=VB, VCG=VL / 2, OR=OR)
    modelo = [s.normal_e_momento(p, K, j)["CNA"] for j in range(17)]
    registra(f"{nome} (p. {pag})", "CNA", modelo, cna, circ_xb)

# 3. Magnus e Clp em 6 tabelas (XE e XG1 lidos). XE5 em Mach 1,5 e 1,75 veio das
#    tabelas de 7 e 9 calibres: circular nelas.
for nome, tb in mc.TABELAS.items():
    if "M437" in nome:
        continue
    p = s.Projetil(VL=tb["VL"], VN=tb["VN"], VB=tb["VB"], VCG=tb["VL"] / 2)
    mg = [s.magnus(p, K, j) for j in range(17)]
    circ = {10, 11} if tb["VL"] > 6 else set()
    registra(nome, "CYPA", [m["CYPA"] for m in mg], tb["CYPA"])
    registra(nome, "CPF1", [m["CPF1"] for m in mg], tb["CPF1"], circ)
    registra(nome, "CPF5", [m["CPF5"] for m in mg], tb["CPF5"], circ)
    if "CLP" in tb:
        registra(nome, "CLP", [s.clp(p, K, j) for j in range(17)], tb["CLP"])

# 4. 5"/38 NAVY (p. 53): CX, CX2, CPN, CMα
p538 = s.Projetil(VL=4.59, VN=2.15, VB=0.35, VCG=2.71, DM=0.100, BD=1.040, OR=5.3)
t538 = s.tabela(p538)
registra('5"/38 NAVY (p. 53)', "CX", t538["CX"], CX_538, {0, 1})
registra('5"/38 NAVY (p. 53)', "CX2", t538["CX2"], CX2_538,
         {j for (_, j) in XD_DEC} | set(CX2_DEC_538))
circ_cpn_538 = {1, 2, 6, 8, 12}          # XC decidido com o 5"/38 + M437 nesses Mach
registra('5"/38 NAVY (p. 53)', "CPN", t538["CPN"], CPN_538, circ_cpn_538)
registra('5"/38 NAVY (p. 53)', "CMA", t538["CMA"], CMA_538, circ_cpn_538)

# 5. Cmq em mais três tabelas (reconstrucao_F/test_cmq.py). O VCG do M101 foi decidido
#    pela coluna CMQ: circular inteiro. A coluna do 9 cal foi lida com 1 casa.
import test_cmq as tc                                       # noqa: E402
for nome, (VL, VCG, VB, col) in tc.T.items():
    if nome == "M437":
        continue
    p = s.Projetil(VL=VL, VN=2.0, VB=VB, VCG=VCG)
    circ = set(range(17)) if nome == "M101" else set()
    registra(f"Cmq {nome}", "CMQ", [s.cmq(p, K, j) for j in range(17)], col, circ,
             casas=1 if nome == "9cal" else 3)


# ------------------------------------------------------------------ resumo
def unidades(l):
    return abs(l[4] - l[3]) * 10 ** l[6]


with open(os.path.join(AQUI, "erros_por_celula.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["tabela", "coluna", "mach", "impresso", "modelo", "erro", "erro_em_unidades",
                "independente"])
    for l in linhas:
        w.writerow([l[0], l[1], l[2], l[3], round(l[4], 7), round(l[4] - l[3], 7),
                    round(unidades(l), 2), "sim" if l[5] else "circular"])

ind = [l for l in linhas if l[5]]
u = np.array([unidades(l) for l in ind])
print(f"Células comparadas: {len(linhas)}  (independentes: {len(ind)}, "
      f"circulares: {len(linhas) - len(ind)})")
print(f"Nas independentes: {100 * np.mean(u <= 0.5):.0f} % indistinguíveis do original (±0,5 unidade), "
      f"{100 * np.mean(u <= 1.5):.0f} % no critério do projeto (±1,5), "
      f"mediana {np.median(u):.2f} unidade\n")

print(f"{'coluna':8s} {'tabelas':>7s} {'células':>7s} {'<=0,5':>6s} {'<=1,5':>6s} {'mediana':>8s} "
      f"{'máx (un.)':>10s}  pior célula")
ordem = ["CX", "CX2", "CNA", "CPN", "CMA", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CNPA3",
         "CNPA5P", "CMQ", "CLP", "GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2",
         "L1", "L2", "L15", "L25", "DELT", "DISP"]
resumo = []
for col in ordem:
    c = [l for l in ind if l[1] == col]
    if not c:
        continue
    uu = np.array([unidades(l) for l in c])
    pior = c[int(np.argmax(uu))]
    ntab = len({l[0] for l in c})
    resumo.append((col, ntab, len(c), 100 * np.mean(uu <= 0.5), 100 * np.mean(uu <= 1.5),
                   np.median(uu), uu.max(), pior))
    print(f"{col:8s} {ntab:7d} {len(c):7d} {100 * np.mean(uu <= 0.5):5.0f}% {100 * np.mean(uu <= 1.5):5.0f}% "
          f"{np.median(uu):8.2f} {uu.max():10.1f}  {pior[0]}, Mach {pior[2]:g}: "
          f"{pior[3]:g} impresso x {pior[4]:.4g} modelo")

with open(os.path.join(AQUI, "resumo_erros.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["coluna", "tabelas", "celulas_independentes", "pct_ate_0.5_unidade",
                "pct_ate_1.5_unidade", "mediana_unidades", "max_unidades"])
    for r in resumo:
        w.writerow([r[0], r[1], r[2], round(r[3], 1), round(r[4], 1), round(r[5], 2), round(r[6], 1)])
