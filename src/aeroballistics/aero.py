"""Interface for simulators (6DOF): coefficients at any Mach.

    import aeroballistics
    p = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
    aero = aeroballistics.Aerodynamics(p)                               # the 1973 SPIN-73
    aero = aeroballistics.Aerodynamics(p, corrections="free_flight")    # with the free-flight correction
    aero = aeroballistics.Aerodynamics(p, convention="modern")          # pd/V, qd/V, CLα, CDδ²

    c = aero(2.3)            # Coefficients: c.CX0, c["CNA"], ...  (floats)
    c = aero(mach_array)     # the same, with arrays (vectorized)
    aero.names               # columns available in the chosen convention

All the aerodynamics is computed once, on the program's 17-Mach grid, in the constructor.
Each call only interpolates (linear in Mach, as SPIN-73 itself is tabulated), so it can be
used inside the integration loop.

Conventions (see aeroballistics/conventions.py):
  "spin73"   the report's: pd/2V and qd/2V, CX2 per sin²α, derivatives per sin α, CPN and CPF
             in calibers from the nose, moments about the CG.
  "modern"   pd/V and qd/V (Cmq, Clp and Magnus are HALF), CDδ² = CX2 + CNα, CLα = CNα − CX0.

Outside the grid (Mach < 0.01 or > 5): out_of_range = "clamp" (uses the end value, default),
"nan" or "error".
"""
from __future__ import annotations

import numpy as np

from . import conventions as _cv
from . import corrections as _corr
from . import core as _c

# Aerodynamic columns in the SPIN-73 convention (exposed name -> table column)
_SPIN73 = {
    "CX0": "CX",        # axial force at zero yaw
    "CX2": "CX2",       # yaw axial force, per sin²α (yaw drag = CX2 + CNA)
    "CNA": "CNA",       # normal force, per sin α
    "CMA": "CMA",       # pitching moment about the CG, per sin α (positive overturns)
    "CPN": "CPN",       # center of pressure of the normal force, calibers from the nose
    "CYPA": "CYPA",     # Magnus force, pd/2V, per sin α
    "CNPA": "CNPA",     # Magnus moment at 1°, pd/2V, per sin α
    "CNPA5": "CNPA5",   # secant slope of the Magnus moment at 5°
    "CPF1": "CPF1",     # center of pressure of the Magnus force at 1°, calibers from the nose
    "CPF5": "CPF5",     # the same at 5°
    "CMQ": "CMQ",       # pitch damping (Cmq + Cmα̇), qd/2V
    "CLP": "CLP",       # roll damping, pd/2V
}


class Coefficients(dict):
    """Dictionary with attribute access: c.CX0 == c["CX0"]."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


class Aerodynamics:
    """Aerodynamic coefficients of a projectile, ready for a trajectory integrator.

    Parameters
    ----------
    projectile   aeroballistics.Projectile (geometry in calibers; DIA in inches, if any)
    corrections  None (default: pure SPIN-73), a registered name ("free_flight",
                 "free_flight:CX0"), a correction object or a list of them
    d_mm         actual diameter in mm; if omitted, taken from projectile.DIA. Only required
                 by corrections that depend on scale.
    data         alternative aeroballistics.DataBlocks (other DATA blocks); default: the listing's
    convention   "spin73" or "modern"
    out_of_range "clamp", "nan" or "error"
    """

    GRID = _c.MACH_GRID

    def __init__(self, projectile: _c.Projectile, corrections=None, *, d_mm: float | None = None,
                 data: _c.DataBlocks | None = None, convention: str = "spin73",
                 out_of_range: str = "clamp"):
        if convention not in ("spin73", "modern"):
            raise ValueError("convention must be 'spin73' or 'modern'")
        if out_of_range not in ("clamp", "nan", "error"):
            raise ValueError("out_of_range must be 'clamp', 'nan' or 'error'")
        self.projectile = projectile
        self.convention = convention
        self.out_of_range = out_of_range
        if d_mm is None and projectile.DIA > 0:
            d_mm = projectile.DIA * 25.4
        self.context = _corr.Context(d_mm=d_mm)
        self.corrections = _corr.resolve(corrections)
        self.original_table = _c.table(projectile, data)
        self.table = _corr.apply(self.original_table, projectile, self.corrections, self.context)
        self._grid = self._in_convention(self.table)

    # ------------------------------------------------------------------ queries
    def _in_convention(self, t: dict) -> dict:
        if self.convention == "spin73":
            return {k: np.asarray(t[c], float) for k, c in _SPIN73.items()}
        m = _cv.to_modern(t, VL=self.projectile.VL)
        m.pop("MACH")
        return m

    @property
    def names(self) -> list[str]:
        return list(self._grid)

    def _mach(self, mach):
        M = np.asarray(mach, float)
        outside = (M < self.GRID[0]) | (M > self.GRID[-1])
        if np.any(outside) and self.out_of_range == "error":
            raise ValueError(f"Mach outside the SPIN-73 grid ({self.GRID[0]} to {self.GRID[-1]})")
        return M, outside

    def coefficient(self, name: str, mach):
        """One coefficient at the requested Mach number(s)."""
        M, outside = self._mach(mach)
        v = np.interp(M, self.GRID, self._grid[name])
        if self.out_of_range == "nan" and np.any(outside):
            v = np.where(outside, np.nan, v)
        return float(v) if np.ndim(v) == 0 else v

    def __call__(self, mach) -> Coefficients:
        """Every coefficient at the requested Mach number(s)."""
        return Coefficients({k: self.coefficient(k, mach) for k in self._grid})

    def magnus_moment(self, mach, alpha_rad):
        """Magnus moment coefficient (secant) at the total angle of attack α.

        Linear interpolation in sin²α between the two secant slopes SPIN-73 computes (CNPA at
        1° and CNPA-5 at 5°); constant outside [1°, 5°]. It is a reading of the program's
        values, not one of its equations: the printed polynomial (CNPA3, CNPA5) has a defect
        in the original (TRANSCRIPTION_NOTES, T12) and is not used here.
        """
        c1 = self.coefficient("CNPA" if self.convention == "spin73" else "Cmpa", mach)
        c5 = self.coefficient("CNPA5" if self.convention == "spin73" else "Cmpa_5deg", mach)
        s1, s5 = np.sin(np.radians(1.0)) ** 2, np.sin(np.radians(5.0)) ** 2
        w = np.clip((np.sin(np.asarray(alpha_rad, float)) ** 2 - s1) / (s5 - s1), 0.0, 1.0)
        return c1 + w * (c5 - c1)

    # ------------------------------------------------------------------ description
    def describe(self) -> str:
        p = self.projectile
        lines = [f"aeroballistics (adapted from SPIN-73) — {p.name or 'projectile'} "
                 f"(VL {p.VL}, VN {p.VN}, VB {p.VB}, VCG {p.VCG} cal)", f"convention: {self.convention}"]
        if self.corrections:
            for c in self.corrections:
                lines.append(f"correction: {c.name} — {getattr(c, 'description', '')}")
        else:
            lines.append("no correction (the 1973 program)")
        if self.context.d_mm:
            lines.append(f"diameter: {self.context.d_mm:.2f} mm")
        return "\n".join(lines)

    def __repr__(self):
        return f"<Aerodynamics {self.projectile.name or 'projectile'} {self.convention} " \
               f"corrections={[c.name for c in self.corrections]}>"


__all__ = ["Aerodynamics", "Coefficients"]
