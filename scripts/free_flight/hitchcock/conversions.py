"""Conversion of the BRL (Hitchcock) K coefficients to the SPIN-73 normalization.

The BRL K coefficients define the forces and moments as K·ρ·d²·u²·δ (and the corresponding
powers of d for the moments). The modern coefficients use ½ρV²·(πd²/4), which gives the factor
π/8 between the two families:

    K_D = (π/8)·CX              CX  = (8/π)·K_D
    K_M = (π/8)·CMα             CMα = (8/π)·K_M
    K_L = (π/8)·(CNα − CX)      ->  CNα = (8/π)·K_L + CX
    K_H = (π/16)·|Cmq|          Cmq = −(16/π)·K_H   (SPIN-73 uses q·d/2V; the BRL, q·d/V)

The last two are the ones that usually go wrong, and so they were VERIFIED numerically
against the caliber 0.30 Ball M2 (see test_cal030.py):

  - K_M: the CMα implied by the measured stability factor S (3.42), computed with the
    SPIN-73 s_g formula and the report's own moments of inertia, gives 1.286, against
    1.299 from (8/π)·0.51. A 1 % difference, within the rounding of the data. This
    validates the conversion AND the reconstructed stability formula, against an
    independent source older than SPIN-73.
  - K_H: the reconstructed Cmq for this geometry at Mach 2.49 is −12.90, against −13.24 from
    −(16/π)·2.6. The factor 2 between q·d/V and q·d/2V is needed; without it a factor of
    1.95 would remain.
  - K_L: (8/π)·0.98 = 2.496 and the reconstructed CNα is 2.918, which implies CX = 0.42; the
    drag plot on p. 19 of the report gives K_D ≈ 0.15 at Mach 2.5, i.e. CX ≈ 0.38.
    Compatible within the reading of the plot.

Positions: g (CG) and h (center of pressure) are given in calibers from the BASE.
SPIN-73 measures from the nose: VCG = VL − g and CPN = VL − h.
"""
import math

PI_8 = math.pi / 8


def cx_from_kd(K_D):
    return K_D / PI_8


def cma_from_km(K_M):
    return K_M / PI_8


def cmq_from_kh(K_H):
    """Cmq in the SPIN-73 normalization (q·d/2V), negative by convention."""
    return -2 * K_H / PI_8


def cna_from_kl(K_L, CX):
    """K_L is the crosswind force: (π/8)(CNα − CX)."""
    return K_L / PI_8 + CX


def from_nose(VL, distance_from_base):
    return VL - distance_from_base


# --- Hitchcock's own empirical formulas (printed p. 11) ---------------------------
# Direct predecessors of the SPIN-73 equations: the same idea, the same geometric
# variables, but WITHOUT Mach dependence.
def kn_hitchcock(bt_angle, bt_length, cylinder, ogive, ogive_radius):
    """K_N (normal force) for projectiles with an ogival ogive."""
    return (0.020 * bt_angle - 0.748 * bt_length + 0.1715 * cylinder
            + 0.540 * ogive - 0.0266 * ogive_radius)


def h_hitchcock(bt_angle, bt_length, cylinder, ogive, ogive_radius):
    """Center of pressure in calibers from the base."""
    return (-0.0135 * bt_angle + 1.97 * bt_length + 0.6276 * cylinder
            + 0.4837 * ogive - 0.0233 * ogive_radius)
