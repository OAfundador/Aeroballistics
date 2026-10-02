"""DATA XA1..XA15 (axial force CX) read from the listing, p. 79 (JP2 0082).

XA1..XA10: 2-line statements (9+8, 8+9 or 12+5 values); XA11 and XA12: 3 cards (7+7+3);
XA13..XA15: 2 lines (10+7). Counting up to 17 decides the number of leading zeros of XA4,
XA9, XA13, XA14 and XA15. '?' = doubtful digit.

XA13..XA15 only enter when the ogive is longer than 3 calibers (DXN, cards C164-C169);
none of the tables used in the validation has VN > 3, so they are read but not tested.
"""
import numpy as np

XA = np.array([
 # XA1   (first two faded: decided by the tables, see DECIDED)
 [.2014, .2014, .2034, .2195, .2732, .3675, .4129, .4084, .3938,
  .3747, .3563, .3285, .3054, .2677, .2410, .203, .181],
 # XA2   (7th value reread under zoom: -.0687; first two decided)
 [.0057, .0057, .0057, .0029, -.0141, -.0324, -.0687, -.0694,
  -.0764, -.0740, -.0723, -.0695, -.0633, -.0559, -.0463, -.0463, -.0463],
 # XA3
 [.0121, .0121, .0121, .0181, .0052, .0152, .0441, .0426, .0476,
  .0415, .0384, .0325, .0265, .0123, .0044, .0044, .0044],
 # XA4   (6 zeros: the count closes at 17)
 [0., 0., 0., 0., 0., 0., .0160, .0102, .0033,
  -.0082, -.0145, -.0251, -.0381, -.053, -.061, -.061, -.061],
 # XA5
 [-.0138, -.0138, -.0138, -.0367, -.0389, -.0399, -.0396, -.0349,
  -.0229, -.0192, -.0165, -.0138, -.0092, -.0106, -.0157, -.0157, -.0157],
 # XA6
 [.0128, .0128, .0128, .0382, .0410, .0379, .0293, .0262, .0182,
  .0157, .0132, .0099, .0059, .0043, .0043, .0043, .0043],
 # XA7
 [-.2295, -.2295, -.2295, -.2058, -.1944, -.1475, -.0892, -.0879,
  -.0828, -.0788, -.0749, -.0683, -.0652, -.0484, -.0330, -.0330, -.0330],
 # XA8
 [-.0071, -.0071, -.0071, -.0212, -.0197, -.042, -.0664, -.0586,
  -.0366, -.0240, -.0162, -.0034, .0103, .0261, .0370, .037, .037],
 # XA9   (3 zeros)
 [0., 0., 0., .0114, -.0016, .1216, .2278, .2253, .2023, .198,
  .1884, .1725, .1471, .1024, .0447, .0447, .0447],
 # XA10  (Mach 1.0 read as .02?)
 [.025, .025, .025, .04, .07, .02, .11, .10, .0963, .0967, .095, .09,
  .085, .070, .060, .050, .040],
 # XA11
 [.4, .4, .4, .55, .7, .725, .75, .8, .9, .85, .8, .745, .69, .65, .55, .55, .55],
 # XA12
 [.07, .07, .07, .11, .13, .15, .17, .21, .26, .37, .48, .73, .98, 1.45, 1.8, 1.8, 1.8],
 # XA13  (3 zeros)
 [0., 0., 0., .004, .006, .031, .050, .050, .044, .030,
  .025, .023, .018, .016, .015, .013, .012],
 # XA14  (5 zeros)
 [0., 0., 0., 0., 0., .040, .065, .060, .057, .053,
  .050, .047, .043, .040, .035, .027, .022],
 # XA15  (3 zeros)
 [0., 0., 0., .035, .040, .053, .055, .046, .030, .023,
  .020, .017, .010, .005, .004, .003, .002],
])

# Decided by the tables (1-based XA row, 0-based Mach index): (read, decided, evidence).
# The two tables (175 mm M437 and 5"/38) give weights of OPPOSITE SIGN to XA2 (VNX − 2.5 =
# +0.41 and −0.35) and the same weight 1 to XA1, which separates the two.
DECIDED = {
    (1, 0): (".2?? (faded)", .2014, "the CX at Mach 0.01 is 0.002 below the one at 0.8 in both "
                                    "tables: an equal step can only come from XA1"),
    (1, 1): (".2?? (faded)", .2014, "same (the tables have identical CX at 0.01 and 0.6)"),
    (2, 0): (".0157?", .0057, "equal to the 3rd value, as in the other XA; both tables ask for .0064"),
    (2, 1): (".0157?", .0057, "same"),
}
# Reread under zoom, confirmed by both tables (which asked for -.0688):
REREAD = {(2, 6): ("-.0487", -.0687)}
