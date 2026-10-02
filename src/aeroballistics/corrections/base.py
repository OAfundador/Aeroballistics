"""The corrections interface and the final step that keeps the columns consistent.

A correction is any object with

    name: str
    apply(t: dict, p: Projectile, ctx: Context) -> dict

which receives the table in the SPIN-73 convention (an array of 17 values per column, on the
MACH_GRID) and returns a new table. Corrections are chained in the given order; at the end,
`finalize` recomputes what is derived (CPN, CPF, CX2, stability), so that no correction needs
to know about the others.

To create a new correction, inherit from Correction (or just implement the two members above)
and, if you want to call it by name, register it with aeroballistics.corrections.register().
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .. import core as _c

REGIMES = (("subsonic", 0.0, 0.9), ("transonic", 0.9, 1.25), ("supersonic", 1.25, 9.0))


def regime(M: float) -> str:
    return next(n for n, a, b in REGIMES if a <= M < b)


@dataclass
class Context:
    """What a correction may need beyond the geometry in calibers."""
    d_mm: float | None = None           # actual diameter, mm (scale; SPIN-73 does not use it)

    def require_scale(self, who: str) -> float:
        if self.d_mm is None or not self.d_mm > 0:
            raise ValueError(f"the '{who}' correction depends on the actual size: give d_mm "
                             "or the diameter in the Projectile (DIA, in inches)")
        return self.d_mm


class Correction:
    """Optional base. Subclasses implement `apply`."""
    name = "correction"
    description = ""

    def apply(self, t: dict, p: _c.Projectile, ctx: Context) -> dict:     # pragma: no cover
        raise NotImplementedError

    def __repr__(self):
        return f"<{type(self).__name__} {self.name}>"


def copy_table(t: dict) -> dict:
    return {k: np.array(v, float, copy=True) for k, v in t.items()}


def finalize(t0: dict, t: dict, p: _c.Projectile) -> dict:
    """Recomputes the derived columns after the corrections.

    CPN  = VCG − CMα/CNα                 (definition of the moment about the CG)
    CPF1 = VCG − CNPA/CYPA, CPF5 alike   (the same, Magnus)
    CX2  = (CX2 + CNα)_original − CNα    (the yaw drag CX2 + CNα is not corrected)
    stability: recomputed with the corrected coefficients, if there are mass and twist.
    """
    t = copy_table(t)
    changed = lambda c: not np.allclose(t[c], t0[c], equal_nan=True)
    if changed("CMA") or changed("CNA"):
        t["CPN"] = p.VCG - t["CMA"] / t["CNA"]
    if changed("CNA"):
        t["CX2"] = t0["CX2"] + t0["CNA"] - t["CNA"]
    if changed("CNPA") or changed("CYPA"):
        t["CPF1"] = p.VCG - t["CNPA"] / t["CYPA"]
    if changed("CNPA5") or changed("CYPA"):
        t["CPF5"] = p.VCG - t["CNPA5"] / t["CYPA"]
    if "GYRO" in t0:
        with np.errstate(invalid="ignore", divide="ignore"):
            t.update(_c.stability(p, t["MACH"], t["CX"], t["CNA"], t["CMA"], t["CNPA"],
                                  t["CNPA5"], t["CMQ"], t["CLP"]))
    return t
