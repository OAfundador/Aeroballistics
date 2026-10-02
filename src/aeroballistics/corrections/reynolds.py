"""Scale effect (Reynolds number) on drag: what SPIN-73 has no input for.

SPIN-73 works in calibers only: a 5.56 mm and a 155 mm projectile of the same shape have the
same CX0. In reality skin friction depends on the Reynolds number, which at the same Mach is
proportional to size. The SPIN-73 constants were fitted to a database dominated by 90 to
175 mm shells and by 20 mm, and they embed the friction of that scale.

Correction (one physical law, one parameter):

    ΔCX0 = [Cf(Re, M) − Cf(Re_ref, M)] · S_wet / S_ref
    Cf(Re, M) = 0.455 / (log10 Re)^2.58 · (1 + 0.144 M²)^−0.65   (Prandtl–Schlichting,
                                                                  van Driest compressibility,
                                                                  the same form as MC DRAG)
    Re = V·L/ν, with L the projectile length; Re_ref = V·L_ref/ν

L_ref, the only parameter, is the "typical" length embedded in the SPIN-73 constants.
S_wet/S_ref is the wetted area (circular-arc ogive, cylinder, boattail frustum) over the
cross-section area, computed from the input geometry.
"""
from functools import lru_cache

import numpy as np

A_SOUND = 340.3        # m/s, standard atmosphere at sea level (59 °F, the SPIN-73 one)
NU = 1.461e-5          # m²/s, kinematic viscosity at the same condition
BT_ANGLE = np.radians(8.0)   # boattail angle (SPIN-73 does not take the angle; 7-10° in the sources)


def cf(Re, M):
    Re = np.maximum(Re, 1e4)
    return 0.455 / np.log10(Re) ** 2.58 * (1.0 + 0.144 * M * M) ** -0.65


@lru_cache(maxsize=None)
def wetted_area(VL, VN, VB, OR, DM=0.0):
    """S_wet/S_ref, with S_ref = π d²/4; lengths in calibers (d = 1)."""
    R = max(OR, (VN * VN + 0.25) / 1.0 + 1e-9)       # not smaller than the tangent ogive's
    # arc through the base of the ogive (x=0, r=0.5) and the tip (x=VN, r=DM/2)
    x1, r1, x2, r2 = 0.0, 0.5, VN, DM / 2.0
    mx, mr = (x1 + x2) / 2, (r1 + r2) / 2
    dx, dr = x2 - x1, r2 - r1
    q = np.hypot(dx, dr)
    h = np.sqrt(max(R * R - (q / 2) ** 2, 0.0))
    # center on the inner side (below the chord)
    xc, rc = mx + h * dr / q, mr - h * dx / q
    x = np.linspace(0.0, VN, 400)
    r = rc + np.sqrt(np.maximum(R * R - (x - xc) ** 2, 0.0))
    drdx = np.gradient(r, x)
    ogive = np.trapezoid(2 * np.pi * r * np.sqrt(1 + drdx ** 2), x)
    cyl = np.pi * 1.0 * max(VL - VN - VB, 0.0)
    rb = max(0.5 - VB * np.tan(BT_ANGLE), 0.2)
    bt = np.pi * (0.5 + rb) * VB / np.cos(BT_ANGLE)
    return (ogive + cyl + bt) / (np.pi / 4)


def delta_cx0(M, VL, VN, VB, OR, DM, d_mm, L_ref_m):
    """Scale ΔCX0 for a projectile of diameter d_mm at Mach M."""
    V = M * A_SOUND
    L = VL * d_mm / 1000.0
    Re, Re_ref = V * L / NU, V * L_ref_m / NU
    return (cf(Re, M) - cf(Re_ref, M)) * wetted_area(VL, VN, VB, OR, DM)
