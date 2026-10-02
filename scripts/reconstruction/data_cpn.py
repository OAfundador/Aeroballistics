"""CMA and CPN columns transcribed from the SPIN-73 output tables.

The 175 mm M437 (p. 65) is in `data/tables_1973/m437_table.csv`. Here is the 5"/38 NAVY (p. 53),
transcribed to give a SECOND geometry to the test of DATA XC: it is what makes it possible to
separate a reading error in C1..C11 from an error in C12..C16, because the weights of the two
blocks change a lot between a projectile with a 1.00 cal boattail (M437) and one with 0.35 cal
(5"/38).

Visual reading of the scan (JP2 0056), checked by the identity CMA = (VCG - CPN)·CNA with the
printed CNA (`data_cna.py`). Where the identity closes in both columns, the reading is
verified; what was left is in DOUBTFUL.
"""
import numpy as np

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
_n = np.nan

# 5"/38 NAVY, p. 53: VL 4.59  VN 2.15  VB 0.35  OR 5.3  VCG 2.710  DM 0.100
# Mach 1.05 and 4.0 reread by the identity with the printed CPN and CNα (data/tables_1973/p53_5in38_navy.csv):
# 3.749 -> 3.739 (pair 3/4) and 3.060 -> 3.066 (pair 0/6).
CMA_538 = np.array([3.474, 3.514, 3.690, 3.883, 4.135, 3.976, 3.739, 3.714, 3.653,
                    3.494, 3.569, 3.408, 3.331, 3.206, 3.071, 3.066, 3.043])
CPN_538 = np.array([_n, 0.757, 0.681, 0.638, _n, 0.851, 1.031, 1.074, 1.155,
                    1.296, 1.341, 1.454, 1.532, 1.624, _n, 1.626, 1.595])

# Cells still open (0-based Mach index).
DOUBTFUL = {
    0: "CPN: 0.769 or 0.779. With CMA 3.474 the identity gives 0.779; with CPN 0.769 the CMA "
       "would be 3.492. The model predicts 0.768. Reread both cells.",
    4: "CPN read as '?.464', incompatible with the CMA 4.135 and with the identity "
       "(which would give 0.688). Reread the whole line: there may be a printing artifact.",
    14: "CPN: last digit illegible (1.66?); CMA 3.071 gives 1.662 by the identity.",
}

# Values obtained by the identity, not read directly (they stay out of the validation of the
# identity itself, but they serve to test the model).
BY_IDENTITY = {5: 0.851, 14: 1.662}
