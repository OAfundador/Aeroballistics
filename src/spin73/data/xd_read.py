"""DATA XD1..XD4 (CX2, yaw axial force) read from the listing.

Source: end of p. 80 (XD1 and the first card of XD2, 3-card statements: 7 + 7 + 3 values)
and start of p. 81 (rest of XD2, XD3, XD4). JP2 0083-0084.

Equation (code, card C213; the same as the text on p. 15):
    CX2 = XD1 + XD2·CXCL + XD3·CRAT + XD4·VB − CNα
    CXCL = VL − VN − VB − 1.5      CRAT = VN²/OR − 0.40

Validation: two tables with very different weights for XD2 and XD3 — 175 mm M437 (0.10 and
−0.06) and 5"/38 (0.59 and 0.47). Holding XD1 and XD4, read with confidence, the two tables
give two equations per Mach for XD2 and XD3, and the solution returns the read values at
Mach 0.01 / 0.6 / 0.9 / 1.0 / 1.05 / 1.35 / 2.0. See TRANSCRIPTION_NOTES.md, section T9.
"""
import numpy as np

XD = np.array([
 # XD1: sharp; rises by 0.5 up to Mach 1.2 and falls by the same step
 [4.5, 4.5, 5., 5.5, 6., 6.5, 7., 7.5, 8., 7.5, 7., 6.5, 6., 5.5, 5., 4.5, 4.],
 # XD2: 1st card sharp (p. 80); 2nd card faded (p. 81)
 [.25, .25, .25, .25, .25, .3, .35, .4, .5, .5, .5, .5, .5, .5, .45, .4, .35],
 # XD3: faded in the first three values
 [.3, .3, .4, .5, .6, .7, .8, .9, 1., 1., 1., 1., 1., .8, .7, .6, .5],
 # XD4: regular sequence, in steps of 0.1
 [-1., -1., -1., -.9, -.8, -.7, -.6, -.5, -.4, -.3, -.2, -.1, 0., 0., 0., 0., 0.],
])

# Decided by the tables (1-based XD row, 0-based Mach index): (read, decided, evidence)
DECIDED = {
    (3, 2): (".?", .4, "5\"/38 (weight 0.47) asks for +0.0996; completes the sequence .3 .3 .4 .5 .6"),
    (2, 9): ("illegible", .5, "two tables: 0.501"),
    (2, 12): (".6?", .5, "two tables: 0.501 (XD3 = 0.998)"),
    (2, 13): (".6?", .5, "5\"/38 (weight 0.59) asks for 0.509; the row becomes .5 .5 .5 .5 .5 .5 .45 .4 .35. "
                         "The XM380E5 (same weight, outside the decision) asks for 0.500 (NOTES, T13)"),
}

# Still doubtful: none. The M437 (weight 0.10) keeps a residual of −0.030 at Mach 2.5.
DOUBTFUL = {}
