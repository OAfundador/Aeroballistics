"""Base comum de dados de voo livre, na convenção do SPIN-73, para a correção empírica.

Junta as fontes de túnel balístico já transcritas e converte cada coeficiente para a
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
    762m  7,62 match, M118/190 Sierra/168 Sierra  BRL-MR-3733 (McCoy 1988)
    30    30 mm XM788, XM788E1 (TP), XM789      ARBRL-MR-03019 (McCoy 1980), ARBRL-TR-03432 (1982)
    t203  175 mm T203, modelo de 90 mm (só CX0)  BRL MR 956 (Karpov 1955)
    xm617 152 mm XM617, cone-cilindro            BRL MR 1998 (Brandon 1969)

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
    # 7,62 match (McCoy 1988): meplat cotado nos esboços
    "M118": dict(VL=4.19, VN=2.16, VB=0.74, VCG=4.19 - 1.80, DM=0.18, BD=1.00, OR=7.00),
    "190 Sierra": dict(VL=4.31, VN=2.09, VB=0.69, VCG=4.31 - 1.81, DM=0.21, BD=1.00, OR=8.80),
    "168 Sierra": dict(VL=3.98, VN=2.26, VB=0.51, VCG=3.98 - 1.54, DM=0.25, BD=1.00, OR=7.00),
    # 30 mm (McCoy 1982): ponta cônica de 17° + ogiva R 4,30, base arredondada (VB = 0).
    # Cintas não cotadas: BD = 1,02 (default do listing), decidido.
    "XM788E1": dict(VL=3.61, VN=1.85, VB=0.0, VCG=3.61 - 1.35, DM=0.26, BD=1.02, OR=4.30),
    "XM789": dict(VL=3.61, VN=1.85, VB=0.0, VCG=3.61 - 1.40, DM=0.26, BD=1.02, OR=4.30),
    "XM789 potted": dict(VL=3.61, VN=1.85, VB=0.0, VCG=3.61 - 1.41, DM=0.26, BD=1.02, OR=4.30),
    "XM788": dict(VL=3.49, VN=1.84, VB=0.0, VCG=3.49 - 1.25, DM=0.26, BD=1.02, OR=4.30),
    # T203 (Karpov 1955), modelo de 90 mm: L, ogiva e boattail cotados; OR, DM e BD NÃO cotados,
    # tomados do cartão do 175 mm M437 no SPIN-73 (p. 65), que tem as mesmas três cotas (decidido).
    # O OR muda o CMα do SPIN-73 em até 20 % nesta forma, mas o CX0 em ≤ 2 %: só o CX0 é usado.
    "T203 8BT": dict(VL=5.51, VN=2.91, VB=1.00, VCG=5.51 - 1.940, DM=0.079, BD=1.05, OR=25.0),
    # XM617: cone-cilindro; OR = 1000 é como o SPIN-73 descreve ogiva cônica (caso da p. 41)
    "XM617": dict(VL=3.151, VN=1.873, VB=0.0, VCG=3.151 - 1.066, DM=0.009, BD=1.019, OR=1000.0),
}
# Diâmetro de referência, mm: dá a escala (número de Reynolds por calibre ∝ d, no mesmo Mach),
# que o SPIN-73 não tem como entrada aerodinâmica.
DIAM_MM = {"SS-109": 5.69, "M855": 5.69, "L110": 5.69, "M856": 5.69, ".50 M33": 12.95,
           "M101": 155.0, "M483A1": 154.74, "M-80": 7.82, "M-59": 7.82, "M-61": 7.82, "M-62": 7.82,
           "M118": 7.82, "190 Sierra": 7.82, "168 Sierra": 7.82,
           "XM788E1": 29.92, "XM789": 29.92, "XM789 potted": 29.92, "XM788": 29.92,
           "T203 8BT": 90.0, "XM617": 152.0}
# CDδ² das fontes (por sen² da guinada): (supersônico, subsônico)
CDD2 = {"SS-109": (7.0, 9.8), "M855": (7.0, 9.8), "L110": (5.7, 6.4), "M856": (5.7, 6.4),
        "XM617": (6.57, 6.57)}          # XM617: constante média, "insufficient data" para a variação
# CDδ² lido de GRÁFICO da fonte: pontos (Mach, CDδ²), interpolação linear, constante fora.
#   7,62 match: Figs. 21-23 de McCoy 1988 (pontos dos grupos de Mach; o 0,9-0,95 marca o fim do
#   trecho plano subsônico da curva); 30 mm: Fig. 17 de McCoy 1982 (retas, tracejado de 1,0 a 1,2).
CDD2_CURVA = {
    "M118": [(0.80, 3.1), (1.10, 5.3), (1.40, 6.7), (1.80, 6.6), (2.20, 6.2)],
    "190 Sierra": [(0.70, 2.5), (0.90, 2.5), (1.10, 6.5), (1.40, 7.5), (1.80, 5.3), (2.20, 2.8)],
    "168 Sierra": [(0.78, 2.9), (0.95, 2.9), (1.12, 4.2), (1.40, 7.6), (1.80, 6.8), (2.20, 5.5)],
    "XM788E1": [(1.0, 10.0), (1.2, 14.0)],
    "XM789": [(1.0, 5.5), (1.2, 10.5)],
    "XM789 potted": [(1.0, 5.5), (1.2, 10.5)],
    "XM788": [(0.9, 7.9), (1.3, 12.2)],                  # Fig. 12 de McCoy 1980
}
# Rodadas com guinada grande demais para um coeficiente linear (o 13931 do 7,62 match voou a
# 18°, com CMα 18 % abaixo do de pequena guinada) ficam de fora nas fontes novas. O limite
# deixa passar todas as rodadas das fontes antigas (5,56: até 10,04°).
GUINADA_MAX = 10.5
# Com o CDδ² lido de gráfico (ou dado só como média), o CX0 só é tirado de rodadas com guinada
# pequena, onde a correção de guinada é pequena diante da incerteza dele.
GUINADA_MAX_CX0_GRAFICO = 5.0


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
    if nome in CDD2_CURVA:
        Mk, v = zip(*CDD2_CURVA[nome])
        return float(np.interp(M, Mk, v)) * sen2
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


def _mccoy(out, arquivo, grupo):
    """CSV no formato de McCoy (1982, 1988): CD na guinada da rodada, CLα, CMα, Magnus com pd/V,
    Cmq + Cmα̇ com qd/V, CPN da base. CDδ² de CDD2_CURVA (gráfico da fonte)."""
    arq = os.path.join(BENCH, arquivo)
    duv = _duvidosas(arq)
    for r in _csv(arq):
        nome = r["PROJETIL"]
        geo = GEO[nome]
        v = {c: (np.nan if (r["RD"], c) in duv else _f(r[c]))
             for c in ("MACH", "AT", "CD", "CMA", "CLA", "CMPA", "CMQ", "CPN")}
        M, at, cd = v["MACH"], v["AT"], v["CD"]
        if not (np.isfinite(M) and np.isfinite(at)) or at > GUINADA_MAX:
            continue
        sen2 = np.sin(np.radians(at)) ** 2
        cx0 = cd - _yaw_drag(nome, geo, M, sen2) if at <= GUINADA_MAX_CX0_GRAFICO else np.nan
        _add(out, grupo, nome, geo, M, CX0=cx0, CNA=v["CLA"] + cd, CPN=geo["VL"] - v["CPN"],
             CMA=v["CMA"], CMQ=2 * v["CMQ"], CNPA=2 * v["CMPA"])


def _match762(out):
    _mccoy(out, "match762_mccoy1988.csv", "762m")


def _x30(out):
    _mccoy(out, "xm788_mccoy1980.csv", "30")
    _mccoy(out, "x30mm_mccoy1982.csv", "30")


def _t203(out):
    """Só o CX0 do modelo com boattail (ver GEO). KDδ² da fonte: 0,0007/grau² (0,0006 acima de
    75 grau²); rodadas com guinada rms acima de 5° ficam de fora, porque aí a correção de guinada
    passa de 15 % do KD e a incerteza do KDδ² (0,0006 ou 0,0007) já pesa."""
    nome, geo = "T203 8BT", GEO["T203 8BT"]
    for r in _csv(os.path.join(BENCH, "t203_karpov1955.csv")):
        if r["PROJETIL"] != nome:
            continue
        M, d2, kd = _f(r["MACH"]), _f(r["D2"]), _f(r["KD"])
        if np.sqrt(d2) > GUINADA_MAX_CX0_GRAFICO:
            continue
        kdd2 = 0.0007 if d2 < 75 else 0.0006
        _add(out, "t203", nome, geo, M, CX0=(kd - kdd2 * d2) / (np.pi / 8))


def _xm617(out):
    """CNα direto (a fonte dá força normal); Cmq e Magnus com qd/V e pd/V."""
    nome, geo = "XM617", GEO["XM617"]
    for r in _csv(os.path.join(BENCH, "xm617_brandon1969.csv")):
        M, at, cd = _f(r["MACH"]), _f(r["AT"]), _f(r["CD"])
        if at > GUINADA_MAX:
            continue
        sen2 = np.sin(np.radians(at)) ** 2
        cx0 = cd - _yaw_drag(nome, geo, M, sen2) if at <= GUINADA_MAX_CX0_GRAFICO else np.nan
        _add(out, "xm617", nome, geo, M, CX0=cx0, CNA=_f(r["CNA"]), CPN=geo["VL"] - _f(r["CPN"]),
             CMA=_f(r["CMA"]), CMQ=2 * _f(r["CMQ"]), CNPA=2 * _f(r["CMPA"]))


def linhas():
    out = []
    for f in (_nato762, _nato556, _m33, _m101, _m483, _match762, _x30, _t203, _xm617):
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
        # m101 e m483: CPN derivado aqui mesmo; xm617: a fonte fecha com CG 0,022 cal atrás do
        # do esquema (ver o CSV), o que tira 4-7 % da identidade com o CG do esquema
        if all(c in d for c in ("CMA", "CPN", "CNA")) and d["CPN"]["grupo"] not in ("m101", "m483", "xm617"):
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
    for g in sorted({l["grupo"] for l in ls}):
        print(g, {c: sum(1 for l in ls if l["grupo"] == g and l["coef"] == c) for c in COEFS})
    n, ruins = identidade_cma(ls)
    print(f"identidade CMα = (VCG − CPN)·CNα: {n} rodadas, {len(ruins)} fora de 5 %", ruins)
