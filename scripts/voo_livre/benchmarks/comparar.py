"""SPIN-73 adaptado contra dados de voo livre de outras fontes (benchmarks).

Cada benchmark é um CSV com as convenções DA FONTE no cabeçalho. Aqui os dados são levados
à normalização do SPIN-73 (aeroballistics/convencoes.py) e o programa roda no Mach de cada rodada
(interpolação linear na grade de 17 pontos). Isto mede o SPIN-73 contra a realidade, não a
adaptação contra o SPIN-73 (isso está em docs/VERIFICACAO.md).

    python scripts/voo_livre/benchmarks/comparar.py
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import caminhos                                       # noqa: E402

import aeroballistics as s                                    # noqa: E402

DADOS = caminhos.VOO_LIVRE

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
            if c not in ("RD", "PROJETIL"):
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
    rows = ler(DADOS / "m101_karpov1964.csv")
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CNA": ("CNA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0)}      # qd/V e pd/V -> x2
    return comparar("155 mm M101 — Karpov 1964 (BRL MR 1582), protótipo em escala real", rows, p, conv)


def m483a1():
    # Ogiva composta: VN pela soma dos três trechos; OR pelo arco principal (57,77 in).
    p = s.Projetil(VL=5.80, VN=2.844, VB=0.255, VCG=3.64, DM=0.098, BD=1.018, OR=9.48,
                   nome="155 mm M483A1")
    rows = ler(DADOS / "m483a1_whyte1991.csv")
    conv = {c: (c, 1.0) for c in ("CX0", "CNA", "CMA", "CMQ", "CNPA", "CLP")}  # mesma convenção
    return comparar("155 mm M483A1 — Whyte 1991 (BRL-CR-659), 65 tiros em 19 grupos", rows, p, conv)


def m33():
    p = s.Projetil(VL=4.46, VN=2.56, VB=0.78, VCG=4.46 - 1.78, DM=0.18, BD=1.00, OR=8.77,
                   nome=".50 Ball M33")
    rows = ler(DADOS / "m33_mccoy1990.csv")
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
    return comparar(".50 Ball M33 — McCoy 1990 (BRL-MR-3810)", rows, p, conv)


NATO556 = {  # geometria das Figs. 2-3 e Tabela 1 de McCoy 1985 (CG da base -> do nariz)
    "SS-109": dict(VL=4.07, VN=2.00, VB=0.45, VCG=4.07 - 1.52, OR=8.4),
    "M855": dict(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9),
    "L110": dict(VL=5.13, VN=2.14, VB=0.26, VCG=5.13 - 2.52, OR=8.4),
    "M856": dict(VL=5.18, VN=2.00, VB=0.37, VCG=5.18 - 2.57, OR=9.7),
}


def nato556():
    todas = ler(DADOS / "nato556_mccoy1985.csv")
    out = []
    for nome, g in NATO556.items():
        p = s.Projetil(DM=0.12, BD=1.00, nome=nome, **g)
        rows = [r for r in todas if r["PROJETIL"] == nome]
        conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
                "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
        out.append(comparar(f"5,56 NATO {nome} — McCoy 1985 (BRL-MR-3476)", rows, p, conv))
    return out


MCCOY = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
         "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}


def _por_projetil(arquivo, geos, titulo):
    """CSV no formato McCoy com vários projéteis; geometria de correcao/dados.py (fonte no CSV)."""
    todas = ler(DADOS / arquivo)
    out = []
    for nome, g in geos.items():
        rows = [r for r in todas if r["PROJETIL"] == nome]
        if rows:
            out.append(comparar(f"{nome} — {titulo}", rows, s.Projetil(nome=nome, **g), MCCOY))
    return out


def _geo(*nomes):
    import dados
    return {n: dados.GEO[n] for n in nomes}


def match762():
    return _por_projetil("match762_mccoy1988.csv", _geo("M118", "190 Sierra", "168 Sierra"),
                         "McCoy 1988 (BRL-MR-3733), 7,62 match")


def x30():
    return (_por_projetil("xm788_mccoy1980.csv", _geo("XM788"), "McCoy 1980 (ARBRL-MR-03019), 30 mm")
            + _por_projetil("x30mm_mccoy1982.csv", _geo("XM788E1", "XM789", "XM789 potted"),
                            "McCoy 1982 (ARBRL-TR-03432), 30 mm"))


def t203():
    # OR, DM e BD não cotados: os do M437 (ver correcao/dados.py). CMα e CPN sensíveis a isso.
    todas = ler(DADOS / "t203_karpov1955.csv")
    rows = [r for r in todas if r["PROJETIL"] == "T203 8BT"]
    p = s.Projetil(nome="T203 8BT", **_geo("T203 8BT")["T203 8BT"])
    k = 8 / np.pi                                        # notação K do BRL -> C
    conv = {"KD": ("CD", k), "KN": ("CNA", k), "KM": ("CMA", k), "KH": ("CMQ", -2 * k)}
    return comparar("175 mm T203 8° B.T., modelo de 90 mm — Karpov 1955 (BRL MR 956)", rows, p, conv)


def xm617():
    # CG do esquema (1,066 da base); a fonte fecha CPN − CMα/CNα com 1,088 (ver o CSV)
    rows = ler(DADOS / "xm617_brandon1969.csv")
    p = s.Projetil(nome="XM617", **_geo("XM617")["XM617"])
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CNA": ("CNA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
    return comparar("152 mm XM617, cone-cilindro — Brandon 1969 (BRL MR 1998)", rows, p, conv)


if __name__ == "__main__":
    m101()
    m483a1()
    m33()
    nato556()
    match762()
    x30()
    t203()
    xm617()
