"""Caliber 0.30: data from Hitchcock's compendium (BRL Report 620, AD-800 469, 1947/1952).

Source read with `scripts/reading/pdf_page.py` (PDF pages 21-25 = printed 16-20).
All dimensions in calibers; g and h are measured from the BASE, which is the report's
convention — SPIN-73 measures from the nose, so VCG = VL − g and CPN = VL − h.

The speed of sound used by the report itself comes from its table: 1990 ft/s = Mach 1.788
gives a = 1113 ft/s. That is the value that converts the velocities below into Mach.

'?' = doubtful digit in the reading.
"""

A_SOUND = 1990 / 1.788        # ft/s, implied by the stability table

# --- Physical characteristics (printed p. 18) -------------------------------------
# g in calibers from the base; A (axial) and B (transverse) in grain·in².
PHYSICAL = {
    "Ball M1":      dict(drawing="B 10986",  weight_gr=172, rounds=5,  g=1.827, A=1.751, B=16.40),
    "Ball M2":      dict(drawing="B 137545", weight_gr=151, rounds=5,  g=1.455, A=1.332, B=12.13),
    "A.P. M2":      dict(drawing="B 138195", weight_gr=167, rounds=10, g=1.980, A=1.855, B=20.15),
    "Tracer M1":    dict(drawing="B 16092",  weight_gr=149, rounds=5,  g=2.097, A=1.777, B=18.57),
    # mean with and without the tracer composition: it is with this that the report computes
    # the "apparent" K_M of the Tracer M1 (note on p. 20)
    "Tracer M1 mean": dict(drawing=None, weight_gr=142, rounds=None, g=2.30, A=1.667, B=17.60),
    "Frangible M22": dict(drawing=None,      weight_gr=107, rounds=5,  g=1.44,  A=1.043, B=9.06),
}

# --- Geometry of the sketches (printed p. 16; "ALL DIMENSIONS IN CALIBERS") --------
# The four sketches close by the sum of the parts, which is the reading check:
#   Ball M1   0.81 + 1.20 + 2.43 = 4.44    Ball M2   1.32 + 2.43 = 3.75
#   A.P. M2   2.12 + 2.45 = 4.57           Tracer M1 2.30 + 2.45 = 4.75
# The Ball M2 also appears on p. 19, where the label of the total was ambiguous (3.75 x 3.78);
# p. 16 confirms 3.75.
GEOMETRY = {
    "Ball M1": dict(VL=4.44, VN=2.43, VB=0.81, OR=7.00, cylinder=1.20,
                    notes="0.81 cal boattail; cannelure not modeled"),
    "Ball M2": dict(VL=3.75, VN=2.43, VB=0.0, OR=7.00, cylinder=1.32, notes="flat base"),
    "A.P. M2": dict(VL=4.57, VN=2.45, VB=0.0, OR=7.00, cylinder=2.12,
                    notes="0.31 cal taper at the base, with the angle marked but illegible; "
                          "treated as a flat base. The A.P. M2 only has K_M; compare_cma_cal030.py "
                          "repeats the CMα comparison with VB = 0.31"),
    "Tracer M1": dict(VL=4.75, VN=2.45, VB=0.0, OR=7.00, cylinder=2.30, notes="flat base"),
    "Frangible T44": dict(VL=3.94, VN=2.32, VB=0.0, OR=7.91, cylinder=1.62,
                          notes="p. 19, low zoom, to be rechecked; the note on p. 18 says the M22 "
                                "has the contour of the Ball M2, which conflicts with this sketch"),
}

# --- Inconsistency IN THE SOURCE (not a reading error) -----------------------------
# With the printed moments of inertia, the three firing series of the Ball M1 violate by
# 9-12 % the identity between the stability factor S and the report's own K_M; the other
# projectiles close within 1-4 %. The cell B = 16.40 was reread under zoom: it is clean,
# unambiguous type. A B of 18.40 would reconcile the three series (ratios 0.97-1.00) and
# would also put the Ball M1 in line with the empirical inertia formula of p. 9, which the
# other three follow with a ratio of 1.07-1.12. It stays as a HYPOTHESIS of a typo in the
# original; the printed value is not changed.
B_BALL_M1_HYPOTHESIS = 18.40

# --- Stability (printed p. 20; rifling twist 10 inches = 33.33 cal) ---------------
# (projectile, report, rounds, velocity ft/s, printed Mach, S, K_M)
STABILITY = [
    ("Ball M1", "BRL 276", 5, 1990, 1.788, 1.615, 1.24),
    ("Ball M1", "BRL 276", 7, 2672, 2.409, 1.901, 1.05),
    ("Ball M1", "BRL 276", 6, 2892, 2.571, 2.079, 0.96),
    ("Ball M2", "BRL 276", 5, 2574, None, 3.42, 0.51),
    ("A.P. M2", "BRL 276", 10, 2750, None, 1.42, 1.36),
    ("Tracer M1", "BRL 276", 10, 2528, None, 2.60, 0.73),   # "apparent" coefficient (the report's note)
    ("Night Tracer M25", "APG 471.4/490-1", None, 2600, None, 2.52, 1.12),
    ("Frangible M22", "FT 0.30AC-U-1", None, 1370, None, 1.61, 0.89),
]

# --- Drift and damping (printed p. 20) ---------------------------------------------
# (projectile, report, velocity ft/s, K_L, K_H, K_I)
DAMPING = [
    ("Ball M1", "BRL 276 and 357", 2656, 0.77, 3.6, -0.15),
    ("Ball M2", "BRL 276 and 357", 2770, 0.98, 2.6, -0.09),
    ("Tracer M1", "BRL 276 and 357", 2734, 1.07, 5.4, -0.22),
    ("Frangible M22", "FT 0.30 AC-U-1", 1370, 0.98, 1.96, -0.06),
]

# Notes of the report: the K_M of the Tracer M1 is an "apparent moment coefficient", computed
# from the observed stability factor with the mean of the moments of inertia with and without
# the tracer composition. The Night Tracer M25 has the same contour as the Tracer M1, and the
# Frangible M22 the same as the Ball M2 (note on p. 18).

PENDING = """Night Tracer M25 (same contour as the Tracer M1, no moments of inertia) and
A.P.I. T15 (no stability data) do not enter the comparisons. The geometry of the
Frangible T44 on p. 19 conflicts with the note on p. 18 and stays out until it is reread."""
