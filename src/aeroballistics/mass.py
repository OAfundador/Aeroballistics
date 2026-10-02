"""Estimate of CG, mass and moments of inertia (OPTIONAL ADDITION; not part of SPIN-73).

SPIN-73 receives the CG, the weight and the inertias ready-made, on the input card
(Appendix B). When they are missing, this module estimates them from the geometry on the same
card. Three methods:

  "solid"    homogeneous solid of revolution with the contour of the inputs: ogive (arc of
             radius OR from the meplat to the shoulder; a cone if OR >= 1000, as in SPIN-73),
             cylinder and conical boattail. The integrals are exact for that contour. The CG
             comes from the geometry alone; the mass, from the density (or the material); the
             inertias, from the mass or the density.
  "bullet"   empirical BRL formulas for caliber .30 and .50 ball and armor-piercing bullets
             (Hitchcock, BRL Report 620, p. 9, citing BRL X-113):
                 g·d = 0.400 L,   A = 0.115 m d²,   B = 0.5 A + 0.0543 m L²
  "shell"    the same formulas for high-explosive shells:
                 g·d = 0.375 L,   A = 0.140 m d²,   B = 0.5 A + 0.0594 m L²

  (g = CG from the BASE, in calibers; A, B = axial and transverse inertias, the latter about
  the CG; L = length; d = diameter; m = mass.) "bullet" and "shell" require the mass.

How much they miss, against 20 projectiles with published mass, CG and inertias (the
measured mass enters as data; scripts/mass/validate.py and docs/MASS.md):

  lead and steel bullets (5.56 to .50)  "solid":  CG ±0.12 cal, Ix −5 to +3 %, Iy +3 to +20 %
                                        "bullet": CG ±0.12 cal, Ix +3 to +11 %, Iy +3 to +14 %
  shells (30 to 175 mm)                 "solid":  Ix −27 to −19 % (the mass sits in the wall)
                                        "shell":  CG ±0.14 cal, Ix −11 to +3 %, Iy −2 to +38 %
  tracers                               CG 0.2 to 0.45 cal behind the real one in both methods
                                        (the tracer composition, at the base, is light)

For bullets, either method; for hollow shells, "shell". "solid" is the only one that gives
the CG without the mass, and the mass from the density.

What the contour does not have: rotating band, cannelure, cavity, rounded tip, rounded base
(it enters as a frustum). The boattail angle is not a SPIN-73 input: the default is 8° (the
same as the friction correction); give `bt_angle` or the base diameter `db` if you know it.

    from aeroballistics import mass
    pm = mass.estimate(p, mass_g=4.0, d_mm=5.69)        # MassProperties
    p2 = mass.complete(p, mass_g=4.0)                   # Projectile with what was missing filled in
"""
from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass, replace

import numpy as np

from .core import Projectile

LB_KG = 0.45359237
IN_M = 0.0254
LBIN2_KGM2 = LB_KG * IN_M ** 2             # 1 lb·in² in kg·m²
DEFAULT_BT_ANGLE = 8.0                      # degrees; the same as corrections/reynolds.py

# Nominal densities, kg/m³ (brass varies from 8400 to 8730 depending on the alloy)
MATERIALS = {"steel": 7850.0, "lead": 11340.0, "copper": 8960.0, "brass": 8500.0,
             "aluminum": 2700.0, "tungsten": 19250.0}

# Hitchcock, BRL 620, p. 9: (g/L, A/(m d²), coefficient of m L² in B)
_HITCHCOCK = {"bullet": (0.400, 0.115, 0.0543), "shell": (0.375, 0.140, 0.0594)}
METHODS = ("solid", "bullet", "shell")


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def material_density(material: str) -> float:
    key = _strip_accents(material)
    if key not in MATERIALS:
        raise ValueError(f"unknown material: {material!r}; known: {', '.join(MATERIALS)}")
    return MATERIALS[key]


# --------------------------------------------------------------------------- contour
def contour(p: Projectile, bt_angle: float | None = None, db: float | None = None):
    """Pieces (x0, x1, r(x)) of the contour, in calibers, with x measured from the nose.

    Also returns the list of notes on what was approximated.
    """
    notes = []
    rm = max(p.DM, 0.0) / 2.0
    VN, VB, VL = p.VN, p.VB, p.VL
    if VN <= 0 or VL <= VN + VB:
        raise ValueError("invalid geometry: VN > 0 and VL > VN + VB are required")
    pieces = []
    if p.OR >= 999.0:                                         # SPIN-73 convention: cone
        pieces.append((0.0, VN, lambda x: rm + (0.5 - rm) * x / VN))
    else:
        cx, cy = VN, 0.5 - rm                                 # chord from the meplat to the shoulder
        s = math.hypot(cx, cy)
        if p.OR < s / 2:
            raise ValueError(f"OR = {p.OR} is smaller than half the ogive chord ({s / 2:.3f} cal)")
        h = math.sqrt(p.OR ** 2 - (s / 2) ** 2)
        Cx, Cy = cx / 2 + h * cy / s, rm + cy / 2 - h * cx / s
        if Cx < VN - 1e-9:
            notes.append("OR smaller than a tangent ogive's: the arc would exceed the diameter "
                         "and was limited to it")
        pieces.append((0.0, VN, lambda x, Cx=Cx, Cy=Cy, R=p.OR:
                       np.minimum(Cy + np.sqrt(np.maximum(R * R - (x - Cx) ** 2, 0.0)), 0.5)))
    x_bt = VL - VB
    pieces.append((VN, x_bt, lambda x: np.full_like(x, 0.5)))
    if VB > 0:
        if db is not None:
            rb = db / 2.0
        else:
            ang = DEFAULT_BT_ANGLE if bt_angle is None else bt_angle
            rb = 0.5 - VB * math.tan(math.radians(ang))
            if bt_angle is None:
                notes.append(f"conical boattail of {DEFAULT_BT_ANGLE:g}° (angle not given)")
        if rb <= 0:
            raise ValueError("the boattail closes before the base: reduce the angle or give db")
        pieces.append((x_bt, VL, lambda x, x0=x_bt, rb=rb: 0.5 - (0.5 - rb) * (x - x0) / VB))
    return pieces, notes


def integrals(p: Projectile, bt_angle: float | None = None, db: float | None = None, n: int = 400):
    """Integrals of the homogeneous solid of density 1 and diameter 1 (Simpson, even n per piece).

    V   volume (cal³);  xcg  CG from the nose (cal);
    Jx  axial inertia / (ρ d⁵);  Jy  transverse inertia about the CG / (ρ d⁵).
    """
    pieces, notes = contour(p, bt_angle, db)
    V = Sx = Jx = Jy0 = 0.0
    for a, b, f in pieces:
        if b <= a:
            continue
        x = np.linspace(a, b, n + 1)
        r = f(x)
        w = np.ones(n + 1)
        w[1:-1:2], w[2:-1:2] = 4.0, 2.0
        w *= (b - a) / (3.0 * n)
        a2, a4 = np.pi * r ** 2, np.pi * r ** 4
        V += w @ a2
        Sx += w @ (a2 * x)
        Jx += w @ (a4 / 2.0)
        Jy0 += w @ (a4 / 4.0 + a2 * x * x)
    xcg = Sx / V
    return dict(V=float(V), xcg=float(xcg), Jx=float(Jx), Jy=float(Jy0 - V * xcg * xcg)), notes


# --------------------------------------------------------------------------- result
@dataclass(frozen=True)
class MassProperties:
    """Result of the estimate. Positions in calibers; mass and inertias in SI and card units."""
    method: str
    cg_nose: float                   # = VCG
    length: float                    # VL, calibers
    d_m: float | None = None
    mass_kg: float | None = None
    ix: float | None = None          # kg·m²
    iy: float | None = None          # kg·m², about the CG
    density: float | None = None     # kg/m³: the one used ("solid") or the effective one, mass/volume
    assumptions: tuple = ()

    @property
    def cg_base(self) -> float:
        return self.length - self.cg_nose

    @property
    def mass_g(self):
        return None if self.mass_kg is None else self.mass_kg * 1000.0

    @property
    def WGT(self):                   # lb
        return None if self.mass_kg is None else self.mass_kg / LB_KG

    @property
    def IX(self):                    # lb·in²
        return None if self.ix is None else self.ix / LBIN2_KGM2

    @property
    def IY(self):
        return None if self.iy is None else self.iy / LBIN2_KGM2

    @property
    def ix_gcm2(self):
        return None if self.ix is None else self.ix * 1e7

    @property
    def iy_gcm2(self):
        return None if self.iy is None else self.iy * 1e7

    def __str__(self):
        lines = [f"method: {self.method}",
                 f"CG: {self.cg_nose:.3f} cal from the nose ({self.cg_base:.3f} from the base)"]
        if self.mass_kg is not None:
            lines.append(f"mass: {self.mass_g:.4g} g ({self.WGT:.5g} lb)")
        if self.ix is not None:
            lines.append(f"Ix: {self.ix_gcm2:.4g} g·cm² ({self.IX:.5g} lb·in²)")
            lines.append(f"Iy: {self.iy_gcm2:.4g} g·cm² ({self.IY:.5g} lb·in²)")
        if self.density is not None:
            lines.append(f"density: {self.density:.0f} kg/m³")
        lines += [f"assumption: {h}" for h in self.assumptions]
        return "\n".join(lines)


def _diameter_m(p: Projectile, d_mm):
    if d_mm:
        return d_mm / 1000.0
    return p.DIA * IN_M if p.DIA > 0 else None


def estimate(p: Projectile, method: str = "solid", *, mass_g: float | None = None,
             density: float | None = None, material: str | None = None,
             d_mm: float | None = None, bt_angle: float | None = None,
             db: float | None = None) -> MassProperties:
    """Estimates CG, mass and inertias. The mass comes from `mass_g`, or from p.WGT, or (only in
    "solid") from the density/material; the diameter, from `d_mm` or from p.DIA. With no
    diameter, only the CG."""
    if method not in METHODS:
        raise ValueError(f"unknown method: {method!r}; use {', '.join(METHODS)}")
    if density is None and material is not None:
        density = material_density(material)
    d = _diameter_m(p, d_mm)
    m = mass_g / 1000.0 if mass_g else (p.WGT * LB_KG if p.WGT > 0 else None)

    if method == "solid":
        I, notes = integrals(p, bt_angle, db)
        hyp = ["homogeneous solid: no rotating band, cannelure or cavity"] + notes
        if d is None:
            return MassProperties(method, I["xcg"], p.VL, assumptions=tuple(hyp))
        if m is None and density is not None:
            m = density * I["V"] * d ** 3
        if m is None:
            return MassProperties(method, I["xcg"], p.VL, d, assumptions=tuple(
                hyp + ["no mass or density: CG only"]))
        rho = m / (I["V"] * d ** 3)
        return MassProperties(method, I["xcg"], p.VL, d, m, rho * I["Jx"] * d ** 5,
                              rho * I["Jy"] * d ** 5, rho, tuple(hyp))

    g, a, b = _HITCHCOCK[method]
    hyp = [f"Hitchcock's empirical formulas (BRL 620, p. 9) for "
           f"{'.30 and .50 bullets' if method == 'bullet' else 'high-explosive shells'}"]
    cg = p.VL - g * p.VL
    if m is None:
        raise ValueError(f"method {method!r} requires the mass (mass_g or WGT)")
    if d is None:
        return MassProperties(method, cg, p.VL, None, m, assumptions=tuple(
            hyp + ["no diameter: CG and mass only"]))
    A = a * m * d * d
    B = 0.5 * A + b * m * (p.VL * d) ** 2
    return MassProperties(method, cg, p.VL, d, m, A, B, assumptions=tuple(hyp))


def missing(p: Projectile) -> list[str]:
    """Mass inputs the card does not have (the ones `complete` would fill in)."""
    out = []
    if p.VCG is None or p.VCG <= 0:
        out.append("VCG")
    for c in ("WGT", "IX", "IY"):
        if getattr(p, c) <= 0:
            out.append(c)
    return out


def complete(p: Projectile, method: str = "solid", **kw) -> Projectile:
    """New Projectile with VCG, WGT, IX and IY filled in where they were missing. What the card
    already has is never replaced. With `d_mm` and no DIA, DIA is filled in too (in inches)."""
    lacking = missing(p)
    change = {}
    d_mm = kw.get("d_mm")
    if d_mm and p.DIA <= 0:
        change["DIA"] = d_mm / 25.4
    if not lacking:
        return replace(p, **change) if change else p
    pm = estimate(p, method, **kw)
    if "VCG" in lacking:
        change["VCG"] = pm.cg_nose
    if "WGT" in lacking and pm.mass_kg is not None:
        change["WGT"] = pm.WGT
    if "IX" in lacking and pm.ix is not None:
        change["IX"] = pm.IX
    if "IY" in lacking and pm.iy is not None:
        change["IY"] = pm.IY
    return replace(p, **change)


__all__ = ["MassProperties", "estimate", "complete", "missing", "contour", "integrals",
           "MATERIALS", "METHODS", "material_density"]
