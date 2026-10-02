"""Correction fitted to free-flight data (optional; the core does not depend on it).

The fit and the validation live in scripts/free_flight/correction/ (fit.py), which writes
free_flight.json next to this file. This module only applies the result. Only the
corrections accepted by the leave-one-group-of-projectiles-out cross-validation enter the
JSON; today:

    CX0  skin friction with the Reynolds number (ReynoldsFriction), in the three regimes
    CNα  bias in the subsonic and transonic (EmpiricalBias)
    Cmq  bias in the transonic (EmpiricalBias)

CX0 is the robust piece. The others passed close to the limit of the acceptance rule (see
validation(), field worst_ratio); FreeFlight(coefficients=("CX0",)) is the conservative choice.

The pieces are independent and can be used separately:

    FreeFlight()                          everything accepted
    FreeFlight(coefficients=("CX0",))     friction only
    ReynoldsFriction({"supersonic": 0.40})   with a hand-picked L_ref
"""
from __future__ import annotations

import json
import os

import numpy as np

from .base import REGIMES, Context, Correction, copy_table, regime
from . import reynolds as rn

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "free_flight.json")
_COL = {"CX0": "CX", "CNA": "CNA", "CMA": "CMA", "CMQ": "CMQ", "CNPA": "CNPA"}


class ReynoldsFriction(Correction):
    """ΔCX0 = [Cf(Re) − Cf(Re_ref)]·S_wet/S_ref, with L_ref (m) per Mach regime."""
    name = "reynolds_friction"
    description = "CX0: skin friction with the Reynolds number (projectile scale)"

    def __init__(self, l_ref: dict[str, float]):
        self.l_ref = dict(l_ref)

    def apply(self, t, p, ctx: Context):
        d_mm = ctx.require_scale(self.name)
        out = copy_table(t)
        for j, M in enumerate(t["MACH"]):
            L = self.l_ref.get(regime(M))
            if L:
                out["CX"][j] += rn.delta_cx0(M, p.VL, p.VN, p.VB, p.OR, p.DM, d_mm, L)
        return out


class EmpiricalBias(Correction):
    """c ← c·(1 + a + b·f) (relative) or c + a + b·f (absolute), within one Mach regime.
    f = 0 or log10(d_mm/10)."""

    def __init__(self, coef: str, regime_: str, kind: str, a: float, b: float = 0.0,
                 attribute: str = "none"):
        self.coef, self.regime, self.kind = coef, regime_, kind
        self.a, self.b, self.attribute = a, b, attribute
        self.name = f"bias_{coef}_{regime_}"
        self.description = f"{coef}, {regime_}: {kind} bias" + (f" in {attribute}" if attribute != "none" else "")

    def apply(self, t, p, ctx: Context):
        f = 0.0
        if self.attribute == "log d":
            f = np.log10(ctx.require_scale(self.name) / 10.0)
        elif self.attribute != "none":
            raise ValueError(f"unknown attribute: {self.attribute}")
        col = _COL[self.coef]
        out = copy_table(t)
        d = self.a + self.b * f
        for j, M in enumerate(t["MACH"]):
            if regime(M) == self.regime:
                out[col][j] = t[col][j] * (1 + d) if self.kind == "rel" else t[col][j] + d
        return out


class FreeFlight(Correction):
    """Every correction accepted in the free-flight fit (or only those of the requested coefficients)."""
    name = "free_flight"

    def __init__(self, file: str = FILE, coefficients: tuple[str, ...] | None = None):
        with open(file, encoding="utf-8") as f:
            self.model = json.load(f)
        self.components: list[Correction] = []
        l_ref = {}
        for c, regs in self.model.items():
            if coefficients is not None and c not in coefficients:
                continue
            for reg, d in regs.items():
                if not d["coef"]:
                    continue
                a, b, attr = d["coef"]
                if attr == "reynolds":
                    l_ref[reg] = a
                else:
                    self.components.append(EmpiricalBias(c, reg, d["type"], a, b, attr))
        if l_ref:
            self.components.insert(0, ReynoldsFriction(l_ref))
        self.description = "; ".join(x.description for x in self.components)

    def apply(self, t, p, ctx):
        for x in self.components:
            t = x.apply(t, p, ctx)
        return t

    def validation(self) -> dict:
        """Prediction error on unseen groups, by coefficient and regime (from the fit)."""
        return {c: {r: d["validation"] for r, d in regs.items()} for c, regs in self.model.items()}


__all__ = ["ReynoldsFriction", "EmpiricalBias", "FreeFlight", "FILE", "REGIMES"]
