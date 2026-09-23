"""SPIN-73 com a correção empírica de voo livre (correcao_ajustada.json, gerado por ajuste.py).

    import aplicar
    t = aplicar.tabela_corrigida(p, d_mm=5.69)     # p: spin73.Projetil; d_mm: diâmetro real

A correção NÃO altera o programa reconstruído: parte da tabela do SPIN-73 e ajusta, ponto a
ponto da grade de Mach, só o que a validação cruzada aceitou (ver ajuste.py e LEIAME.md):

    CX0          atrito de parede com o número de Reynolds (o SPIN-73 não tem escala)
    CNα          sub e transônico
    CPN          recalculado de CMα e CNα:  CPN = VCG − CMα/CNα
    estabilidade recalculada com os coeficientes corrigidos (se houver massa e passo de raia)

CMα, Cmq, Magnus e o que não foi aceito saem como no SPIN-73. O diâmetro precisa ser dado (d_mm
ou p.DIA, em polegadas): é a escala que o SPIN-73 não usa e que a correção acrescenta.
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, "..", "..")]

import spin73 as s                                      # noqa: E402
import reynolds as rn                                   # noqa: E402

REGIMES = [("subsônico", 0.0, 0.9), ("transônico", 0.9, 1.25), ("supersônico", 1.25, 9.0)]
_COL = {"CX0": "CX", "CNA": "CNA", "CMA": "CMA", "CMQ": "CMQ", "CNPA": "CNPA"}


def carregar(caminho=os.path.join(AQUI, "correcao_ajustada.json")):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _regime(M):
    return next(n for n, a, b in REGIMES if a <= M < b)


def tabela_corrigida(p: s.Projetil, d_mm: float | None = None, modelo: dict | None = None) -> dict:
    """Tabela do SPIN-73 com a correção aplicada. Devolve as mesmas colunas de spin73.tabela."""
    if d_mm is None:
        if not p.DIA > 0:
            raise ValueError("informe d_mm ou p.DIA: a correção depende do tamanho real")
        d_mm = p.DIA * 25.4
    modelo = modelo or carregar()
    t = s.tabela(p)
    out = {k: np.array(v, float) for k, v in t.items()}
    logd = np.log10(d_mm / 10.0)
    for j, M in enumerate(t["MACH"]):
        reg = _regime(M)
        for c, col in _COL.items():
            d = modelo[c][reg]
            if not d["coef"]:
                continue
            a, b, atr = d["coef"]
            v = t[col][j]
            if atr == "reynolds":
                out[col][j] = v + rn.delta_cx0(M, p.VL, p.VN, p.VB, p.OR, p.DM, d_mm, a)
            else:
                f = logd if atr == "log d" else 0.0
                out[col][j] = v * (1 + a + b * f) if d["tipo"] == "rel" else v + a + b * f
    out["CPN"] = p.VCG - out["CMA"] / out["CNA"]
    # CX2 subtrai o CNα no SPIN-73 (CX2 + CNα = arrasto de guinada, que não é corrigido)
    out["CX2"] = t["CX2"] + t["CNA"] - out["CNA"]
    if "GYRO" in t:
        with np.errstate(invalid="ignore", divide="ignore"):
            out.update(s.estabilidade(p, out["MACH"], out["CX"], out["CNA"], out["CMA"],
                                      out["CNPA"], out["CNPA5"], out["CMQ"], out["CLP"]))
    return out
