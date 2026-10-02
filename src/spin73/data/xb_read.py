"""DATA blocks XB1..XB9 read from the JP2 scan (pp. 79-80 of the report). '?' in a comment = doubtful digit."""
import numpy as np
XB = np.array([
 [2.2,2.2,2.22,2.25,2.27,2.295,2.32,2.34,2.40,2.49,2.60,2.70,2.80,2.90,2.85,2.75,2.65],               # XB1
 [.0767,.0767,.0767,.0450,.0261,.0123,-.0553,-.0575,-.0417,-.0680,-.0744,-.0596,-.0647,-.0744,-.0841,-.0841,-.0841],  # XB2 (.0123?, -.0553?, -.0417?)
 [-.0255,-.0255,-.0255,-.0280,-.0292,-.0155,-.0126,-.0119,-.0100,-.0084,-.0061,.0006,.0059,.0136,.0226,.0226,.0226],  # XB3 (-.0155?, -.0100?)
 [-.0856,-.0898,-.0898,-.0996,-.1029,-.1073,-.1824,-.1698,-.1446,-.1065,-.0690,-.0435,-.0091,.0599,.1288,.1288,.1288], # XB4 (1st value?)
 [-.0606,-.0606,-.0606,-.0047,.0233,.0512,.1492,.1433,.1349,.1149,.0965,.1145,.0966,.0667,.0249,.0249,.0249],        # XB5 (1.2/1.35 ?)
 [.0185,.0185,.0185,.0185,.0185,.0185,.0119,.0119,.0119,.0119,.0119,.0110,.0110,.0110,.0110,.0110,.0110],             # XB6
 [-1.022,-1.022,-1.022,-.9861,-1.050,-.7489,-.4567,-.3710,-.3040,-.2256,-.1490,-.1340,-.1012,.0029,.0029,.0029,.0029], # XB7 (1.2..1.5 ?)
 [-.1801,-.1801,-.1801,-.1801,-.2870,-.2870,-.3125,-.3125,-.2857,-.2857,-.2854,-.2854,-.1940,-.1280,-.1280,-.1280,-.1280], # XB8
 [-.0450,-.0450,-.0450,-.0450,-.2747,-.2747,-.2083,-.2083,-.1646,-.1646,-.1110,-.1110,.0081,.0252,.0252,.0252,.0252],   # XB9
])

# Corrections decided by the model: each one is ONE number that zeroes the residual of >= 7
# tables at the same time, and matches a pair of glyphs that the printout confuses. Not
# rechecked on the image.
CORRECTIONS = {  # (B row, Mach index): (read, decided)
    (4, 0): (-.0856, -.0898),   # M 0.01: equal to M 0.6 (the tables have identical CNa at 0.01 and 0.6)
    (3, 5): (-.0155, -.0305),   # M 1.00
    (2, 8): (-.0417, -.0617),   # M 1.20
    (3, 8): (-.0100, -.0106),   # M 1.20
    (7, 10): (-.1490, -.1695),  # M 1.50
    (5, 13): (.0667, .0609),    # M 2.50
    # M 2.0: read .0059 (the last glyph looks like a 9). The long-body tables miss in
    # proportion to CXLL (the weight of XB3): 7 cal -0.0027 (CXLL 2.85), 9 cal -0.0039 (4.85),
    # 10 cal -0.0047 (5.01), and the short ones close. Decided ONLY by the 9 cal (p. 38), which
    # asks for 0.0051 +- 0.0003; with .0050 (pair 9/0) the 7 cal and the 10 cal, outside the
    # decision, close.
    (3, 12): (.0059, .0050),
}
# Table(s) that decided each correction; no entry = decided by the count over the 10 tables.
DECIDED_BY = {(3, 12): {38}}
XB_READ = XB.copy()
for (b, j), (read, dec) in CORRECTIONS.items():
    assert abs(XB[b - 1, j] - read) < 1e-9, (b, j)
    XB[b - 1, j] = dec
