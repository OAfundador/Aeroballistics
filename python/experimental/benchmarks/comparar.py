"""SPIN-73 reconstruído contra dados de voo livre de outras fontes (benchmarks).

Cada benchmark é um CSV com as convenções DA FONTE no cabeçalho. Aqui os dados são levados
à normalização do SPIN-73 (python/convencoes.py) e o programa roda no Mach de cada rodada
(interpolação linear na grade de 17 pontos). Isto mede o SPIN-73 contra a realidade, não a
reconstrução contra o SPIN-73 (isso está em validation/).

    python experimental/benchmarks/comparar.py
"""
import csv
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", ".."))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import spin73 as s                                    # noqa: E402

# Faixas de Mach para o resumo
FAIXAS = [("subsônico", 0.0, 0.9), ("transônico", 0.9, 1.2), ("supersônico", 1.2, 9.0)]


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        linhas = [l for l in f if not l.startswith("#")]
    duv = set()
    with open(caminho, encoding="utf-8") as f:
        for l in f:
            if l.startswith("# duvidosa:"):
                rd, col = l.split(":", 1)[1].split()[:2]
                duv.add((rd, col))
    rows = list(csv.DictReader(linhas))
    for r in rows:
        for c in list(r):
            if c != "RD":
                r[c] = float(r[c]) if r[c].strip() else np.nan
        for (rd, col) in duv:
            if r["RD"] == rd and col in r:
                r[col] = np.nan
    return rows


def modelo_no_mach(t, M):
    return {c: float(np.interp(M, s.MACH_GRID, v)) for c, v in t.items() if c != "MACH"}


def comparar(nome, rows, p, conv):
    """conv: coluna da fonte -> (coluna do SPIN-73, fator para levar a fonte ao SPIN-73)."""
    t = s.tabela(p)
    res = {}
    for r in rows:
        m = modelo_no_mach(t, r["MACH"])
        d2 = r.get("D2", np.nan)
        if not np.isfinite(d2) and np.isfinite(r.get("AT", np.nan)):
            d2 = r["AT"] ** 2                      # ângulo de ataque total da rodada, graus
        sen2 = np.sin(np.radians(np.sqrt(d2))) ** 2 if np.isfinite(d2) else 0.0
        calc = dict(CD=m["CX"] + (m["CX2"] + m["CNA"]) * sen2, CX0=m["CX"], CMA=m["CMA"],
                    CNA=m["CNA"], CMQ=m["CMQ"], CMPA=m["CNPA"], CNPA=m["CNPA"], CPN=m["CPN"],
                    CLP=m["CLP"], CLA=m["CNA"] - m["CX"], CPN_BASE=p.VL - m["CPN"])
        for col, (alvo, fator) in conv.items():
            v = r.get(col, np.nan)
            if np.isfinite(v):
                res.setdefault(col, []).append((r["MACH"], v * fator, calc[alvo]))
    print(f"\n{nome}")
    print(f"{'coef':6s} {'faixa':12s} {'n':>3s} {'medido':>9s} {'SPIN-73':>9s} {'SPIN/med':>9s} {'disp. med.':>10s}")
    out = []
    for col, pts in res.items():
        a = np.array(pts)
        for fx, lo, hi in FAIXAS:
            k = (a[:, 0] >= lo) & (a[:, 0] < hi)
            if k.sum() == 0:
                continue
            med, mod = a[k, 1], a[k, 2]
            razao = np.mean(mod) / np.mean(med) if abs(np.mean(med)) > 1e-9 else np.nan
            disp = np.std(med, ddof=1) if k.sum() > 1 else np.nan
            print(f"{col:6s} {fx:12s} {k.sum():3d} {np.mean(med):9.3f} {np.mean(mod):9.3f} "
                  f"{razao:9.2f} {disp:10.3f}")
            out.append((col, fx, int(k.sum()), np.mean(med), np.mean(mod), razao, disp))
    return out


# --------------------------------------------------------------------------- benchmarks
def m101():
    # Entrada como o próprio SPIN-73 rodou o M101 (p. 59), com o CG da Tabela I de Karpov.
    p = s.Projetil(VL=4.51, VN=2.45, VB=0.45, VCG=2.96, DM=0.098, BD=1.026, OR=10.75,
                   nome="155 mm M101")
    rows = ler(os.path.join(AQUI, "m101_karpov1964.csv"))
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CNA": ("CNA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0)}      # qd/V e pd/V -> x2
    return comparar("155 mm M101 — Karpov 1964 (BRL MR 1582), protótipo em escala real", rows, p, conv)


def m483a1():
    # Ogiva composta: VN pela soma dos três trechos; OR pelo arco principal (57,77 in).
    p = s.Projetil(VL=5.80, VN=2.844, VB=0.255, VCG=3.64, DM=0.098, BD=1.018, OR=9.48,
                   nome="155 mm M483A1")
    rows = ler(os.path.join(AQUI, "m483a1_whyte1991.csv"))
    conv = {c: (c, 1.0) for c in ("CX0", "CNA", "CMA", "CMQ", "CNPA", "CLP")}  # mesma convenção
    return comparar("155 mm M483A1 — Whyte 1991 (BRL-CR-659), 65 tiros em 19 grupos", rows, p, conv)


def m33():
    p = s.Projetil(VL=4.46, VN=2.56, VB=0.78, VCG=4.46 - 1.78, DM=0.18, BD=1.00, OR=8.77,
                   nome=".50 Ball M33")
    rows = ler(os.path.join(AQUI, "m33_mccoy1990.csv"))
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
    return comparar(".50 Ball M33 — McCoy 1990 (BRL-MR-3810)", rows, p, conv)


if __name__ == "__main__":
    m101()
    m483a1()
    m33()
