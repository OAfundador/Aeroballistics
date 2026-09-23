"""Correção ajustada a dados de voo livre (opcional; o núcleo não depende dela).

O ajuste e a validação ficam em python/experimental/correcao/ (ajuste.py), que grava
voo_livre.json aqui ao lado. Este módulo só aplica o resultado. Só entram no JSON as
correções que a validação cruzada deixando um grupo de projéteis de fora aceitou; hoje:

    CX0  atrito de parede com o número de Reynolds (AtritoReynolds), nos três regimes
    CNα  viés no sub e no transônico (ViesEmpirico)

As peças são independentes e podem ser usadas separadas:

    VooLivre()                          tudo o que foi aceito
    VooLivre(coeficientes=("CX0",))     só o atrito
    AtritoReynolds({"supersônico": 0.40})   com um L_ref escolhido à mão
"""
from __future__ import annotations

import json
import os

import numpy as np

from .base import REGIMES, Contexto, Correcao, copiar, regime
from . import reynolds as rn

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voo_livre.json")
_COL = {"CX0": "CX", "CNA": "CNA", "CMA": "CMA", "CMQ": "CMQ", "CNPA": "CNPA"}


class AtritoReynolds(Correcao):
    """ΔCX0 = [Cf(Re) − Cf(Re_ref)]·S_mol/S_ref, com L_ref (m) por regime de Mach."""
    nome = "atrito_reynolds"
    descricao = "CX0: atrito de parede com o número de Reynolds (escala do projétil)"

    def __init__(self, l_ref: dict[str, float]):
        self.l_ref = dict(l_ref)

    def aplicar(self, t, p, ctx: Contexto):
        d_mm = ctx.exigir_escala(self.nome)
        out = copiar(t)
        for j, M in enumerate(t["MACH"]):
            L = self.l_ref.get(regime(M))
            if L:
                out["CX"][j] += rn.delta_cx0(M, p.VL, p.VN, p.VB, p.OR, p.DM, d_mm, L)
        return out


class ViesEmpirico(Correcao):
    """c ← c·(1 + a + b·f) (relativo) ou c + a + b·f (absoluto), num regime de Mach.
    f = 0 ou log10(d_mm/10)."""

    def __init__(self, coef: str, regime_: str, tipo: str, a: float, b: float = 0.0,
                 atributo: str = "nenhum"):
        self.coef, self.regime, self.tipo = coef, regime_, tipo
        self.a, self.b, self.atributo = a, b, atributo
        self.nome = f"vies_{coef}_{regime_}"
        self.descricao = f"{coef}, {regime_}: viés {tipo}" + (f" em {atributo}" if atributo != "nenhum" else "")

    def aplicar(self, t, p, ctx: Contexto):
        f = 0.0
        if self.atributo == "log d":
            f = np.log10(ctx.exigir_escala(self.nome) / 10.0)
        elif self.atributo != "nenhum":
            raise ValueError(f"atributo desconhecido: {self.atributo}")
        col = _COL[self.coef]
        out = copiar(t)
        d = self.a + self.b * f
        for j, M in enumerate(t["MACH"]):
            if regime(M) == self.regime:
                out[col][j] = t[col][j] * (1 + d) if self.tipo == "rel" else t[col][j] + d
        return out


class VooLivre(Correcao):
    """Todas as correções aceitas no ajuste de voo livre (ou só as dos coeficientes pedidos)."""
    nome = "voo_livre"

    def __init__(self, arquivo: str = ARQUIVO, coeficientes: tuple[str, ...] | None = None):
        with open(arquivo, encoding="utf-8") as f:
            self.modelo = json.load(f)
        self.componentes: list[Correcao] = []
        l_ref = {}
        for c, regs in self.modelo.items():
            if coeficientes is not None and c not in coeficientes:
                continue
            for reg, d in regs.items():
                if not d["coef"]:
                    continue
                a, b, atr = d["coef"]
                if atr == "reynolds":
                    l_ref[reg] = a
                else:
                    self.componentes.append(ViesEmpirico(c, reg, d["tipo"], a, b, atr))
        if l_ref:
            self.componentes.insert(0, AtritoReynolds(l_ref))
        self.descricao = "; ".join(x.descricao for x in self.componentes)

    def aplicar(self, t, p, ctx):
        for x in self.componentes:
            t = x.aplicar(t, p, ctx)
        return t

    def validacao(self) -> dict:
        """Erro de predição em grupos não vistos, por coeficiente e regime (do ajuste)."""
        return {c: {r: d["validacao"] for r, d in regs.items()} for c, regs in self.modelo.items()}


__all__ = ["AtritoReynolds", "ViesEmpirico", "VooLivre", "ARQUIVO", "REGIMES"]
