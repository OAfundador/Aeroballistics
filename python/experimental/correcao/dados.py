"""Base comum de dados de voo livre, na convenção do SPIN-73, para a correção empírica.

Junta as seis fontes de túnel balístico já transcritas e converte cada coeficiente para a
normalização do SPIN-73 (python/convencoes.py): pd/2V e qd/2V, CNα (não CLα), CPN em
calibres do NARIZ, CX0 a guinada zero. Cada linha traz também o valor do SPIN-73
reconstruído no mesmo Mach, com a geometria da fonte.

Grupos (a unidade da validação cruzada: projéteis quase iguais ficam juntos, para que um
não "valide" o outro):
    762   7,62 NATO, M-80/M-59/M-61/M-62       BRL MR 1833 (Piddington 1967)
    556b  5,56 NATO Ball, SS-109/M855          BRL-MR-3476 (McCoy 1985)
    556t  5,56 NATO Tracer, L110/M856          idem
    50    .50 Ball M33                          BRL-MR-3810 (McCoy 1990)
    m101  155 mm M101                           BRL MR 1582 (Karpov 1964)
    m483  155 mm M483A1                         BRL-CR-659 (Whyte 1991)

    linhas() -> lista de dicts: grupo, proj, geo (Projetil), M, coef, med, spin
"""
import csv
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(AQUI, "..")
BENCH = os.path.join(EXP, "benchmarks")
sys.path[:0] = [os.path.join(EXP, ".."), EXP, BENCH]

import spin73 as s                                      # noqa: E402

COEFS = ("CX0", "CNA", "CPN", "CMA", "CMQ", "CNPA")


def _f(x):
    return float(x) if x not in ("", None) and str(x).strip() else np.nan


def _csv(caminho):
    with open(caminho, encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def _duvidosas(caminho):
    out = set()
    with open(caminho, encoding="utf-8") as f:
        for l in f:
            if l.startswith("# duvidosa:"):
                rd, col = l.split(":", 1)[1].split()[:2]
                out.add((rd, col))
    return out


# Geometria de cada projétil (entradas do SPIN-73). Fontes nos cabeçalhos dos CSV.
# DM e BD não cotados nas fontes de armas portáteis: DM = 0,12 e BD = 1,00 (sem cinta).
GEO = {
    "SS-109": dict(VL=4.07, VN=2.00, VB=0.45, VCG=4.07 - 1.52, DM=0.12, BD=1.00, OR=8.4),
    "M855": dict(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, DM=0.12, BD=1.00, OR=7.9),
    "L110": dict(VL=5.13, VN=2.14, VB=0.26, VCG=5.13 - 2.52, DM=0.12, BD=1.00, OR=8.4),
    "M856": dict(VL=5.18, VN=2.00, VB=0.37, VCG=5.18 - 2.57, DM=0.12, BD=1.00, OR=9.7),
    ".50 M33": dict(VL=4.46, VN=2.56, VB=0.78, VCG=4.46 - 1.78, DM=0.18, BD=1.00, OR=8.77),
    "M101": dict(VL=4.51, VN=2.45, VB=0.45, VCG=2.96, DM=0.098, BD=1.026, OR=10.75),
    "M483A1": dict(VL=5.80, VN=2.844, VB=0.255, VCG=3.64, DM=0.098, BD=1.018, OR=9.48),
}
# Diâmetro de referência, mm: dá a escala (número de Reynolds por calibre ∝ d, no mesmo Mach),
# que o SPIN-73 não tem como entrada aerodinâmica.
DIAM_MM = {"SS-109": 5.69, "M855": 5.69, "L110": 5.69, "M856": 5.69, ".50 M33": 12.95,
           "M101": 155.0, "M483A1": 154.74, "M-80": 7.82, "M-59": 7.82, "M-61": 7.82, "M-62": 7.82}
# CDδ² das fontes (por sen² da guinada): (supersônico, subsônico)
CDD2 = {"SS-109": (7.0, 9.8), "M855": (7.0, 9.8), "L110": (5.7, 6.4), "M856": (5.7, 6.4)}


class _Cache:
    tabs = {}

    @classmethod
    def spin(cls, nome, geo):
        if nome not in cls.tabs:
            cls.tabs[nome] = s.tabela(s.Projetil(nome=nome, **geo))
        return cls.tabs[nome]


def _spin_no_mach(nome, geo, M):
    t = _Cache.spin(nome, geo)
    return {c: float(np.interp(M, s.MACH_GRID, v)) for c, v in t.items() if c != "MACH"}


def _yaw_drag(nome, geo, M, sen2):
    """CDδ²·sen²α: da fonte quando ela dá; senão, o do próprio SPIN-73 (CX2 + CNα)."""
    if nome in CDD2:
        sup, sub = CDD2[nome]
        return (sup if M >= 1.0 else sub) * sen2
    m = _spin_no_mach(nome, geo, M)
    return (m["CX2"] + m["CNA"]) * sen2


def _add(out, grupo, nome, geo, M, **vals):
    m = _spin_no_mach(nome, geo, M)
    spin = dict(CX0=m["CX"], CNA=m["CNA"], CPN=m["CPN"], CMA=m["CMA"], CMQ=m["CMQ"],
                CNPA=m["CNPA"])
    for c, v in vals.items():
        if np.isfinite(v):
            out.append(dict(grupo=grupo, proj=nome, geo=geo, d_mm=DIAM_MM[nome], M=M, coef=c,
                            med=float(v), spin=spin[c]))


# --------------------------------------------------------------------------- fontes
def _nato556(out):
    arq = os.path.join(BENCH, "nato556_mccoy1985.csv")
    duv = _duvidosas(arq)
    for r in _csv(arq):
        nome = r["PROJETIL"]
        geo = GEO[nome]
        grupo = "556b" if nome in ("SS-109", "M855") else "556t"
        M, at = _f(r["MACH"]), _f(r["AT"])
        cd = _f(r["CD"])
        cma = np.nan if (r["RD"], "CMA") in duv else _f(r["CMA"])
        sen2 = np.sin(np.radians(at)) ** 2
        cna = _f(r["CLA"]) + cd
        cpn = geo["VL"] - _f(r["CPN"])
        _add(out, grupo, nome, geo, M, CX0=cd - _yaw_drag(nome, geo, M, sen2), CNA=cna, CPN=cpn,
             CMA=cma, CMQ=2 * _f(r["CMQ"]), CNPA=2 * _f(r["CMPA"]))


def _m33(out):
    nome, geo = ".50 M33", GEO[".50 M33"]
    for r in _csv(os.path.join(BENCH, "m33_mccoy1990.csv")):
        M, at, cd = _f(r["MACH"]), _f(r["AT"]), _f(r["CD"])
        sen2 = np.sin(np.radians(at)) ** 2
        _add(out, "50", nome, geo, M, CX0=cd - _yaw_drag(nome, geo, M, sen2),
             CNA=_f(r["CLA"]) + cd, CPN=geo["VL"] - _f(r["CPN"]), CMA=_f(r["CMA"]),
             CMQ=2 * _f(r["CMQ"]), CNPA=2 * _f(r["CMPA"]))


def _m101(out):
    nome, geo = "M101", GEO["M101"]
    arq = os.path.join(BENCH, "m101_karpov1964.csv")
    duv = _duvidosas(arq)
    for r in _csv(arq):
        M, d2 = _f(r["MACH"]), _f(r["D2"])
        cd, cna, cma = _f(r["CD"]), _f(r["CNA"]), _f(r["CMA"])
        cmq = np.nan if (r["RD"], "CMQ") in duv else _f(r["CMQ"])
        # CD de rodadas sem guinada medida só entra se o CD0 não depender dela: fora
        cx0 = cd - _yaw_drag(nome, geo, M, np.sin(np.radians(np.sqrt(d2))) ** 2) if np.isfinite(d2) else np.nan
        cpn = geo["VCG"] - cma / cna if np.isfinite(cma) and np.isfinite(cna) else np.nan
        _add(out, "m101", nome, geo, M, CX0=cx0, CNA=cna, CPN=cpn, CMA=cma,
             CMQ=2 * cmq, CNPA=2 * _f(r["CMPA"]))


def _m483(out):
    nome, geo = "M483A1", GEO["M483A1"]
    for r in _csv(os.path.join(BENCH, "m483a1_whyte1991.csv")):
        M = _f(r["MACH"])
        cna, cma = _f(r["CNA"]), _f(r["CMA"])
        # CX da fonte já é a guinada zero (CX2 ajustado à parte); mesma convenção do SPIN-73
        _add(out, "m483", nome, geo, M, CX0=_f(r["CX0"]), CNA=cna, CPN=geo["VCG"] - cma / cna,
             CMA=cma, CMQ=_f(r["CMQ"]), CNPA=_f(r["CNPA"]))


def _nato762(out):
    import recalibrar_mr1833 as r62
    geo62 = {r["projetil"]: r for r in _csv(os.path.join(EXP, "mr1833_geometria.csv"))}
    d_in = 0.308
    for l, r in zip(r62.tabela(), r62.RAW):
        g = geo62[l["proj"]]
        geo = dict(VL=_f(g["VL"]), VN=_f(g["VN"]), VB=_f(g["VB"]), VCG=_f(g["VCG"]),
                   DM=_f(g["DM"]), BD=_f(g["BD"]), OR=9.74)
        cpn = geo["VL"] - _f(r["CPN_IN"]) / d_in
        _add(out, "762", l["proj"], geo, l["M"], CX0=l["CD0"], CNA=l["CNA"], CPN=cpn,
             CMA=l["CMA"], CMQ=l["CMQ"], CNPA=l["CNPA"])


def linhas():
    out = []
    for f in (_nato762, _nato556, _m33, _m101, _m483):
        f(out)
    return out


def identidade_cma(ls=None, tol=0.05):
    """Conferência da transcrição e das convenções: CMα ≈ (VCG − CPN)·CNα com os valores
    MEDIDOS da mesma rodada (só onde a fonte dá os três). Devolve as rodadas que violam."""
    ls = linhas() if ls is None else ls
    por = {}
    for l in ls:
        por.setdefault((l["proj"], round(l["M"], 4)), {})[l["coef"]] = l
    ruins, n = [], 0
    for (proj, M), d in por.items():
        if all(c in d for c in ("CMA", "CPN", "CNA")) and d["CPN"]["grupo"] not in ("m101", "m483"):
            n += 1
            prev = (d["CMA"]["geo"]["VCG"] - d["CPN"]["med"]) * d["CNA"]["med"]
            if abs(prev - d["CMA"]["med"]) > tol * abs(d["CMA"]["med"]):
                ruins.append((proj, M, round(prev, 3), d["CMA"]["med"]))
    return n, ruins


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ls = linhas()
    print(f"{len(ls)} valores medidos")
    for g in ("762", "556b", "556t", "50", "m101", "m483"):
        print(g, {c: sum(1 for l in ls if l["grupo"] == g and l["coef"] == c) for c in COEFS})
    n, ruins = identidade_cma(ls)
    print(f"identidade CMα = (VCG − CPN)·CNα: {n} rodadas, {len(ruins)} fora de 5 %", ruins)
