"""CX2 column of the 5"/38 NAVY (p. 53), transcribed to give a second geometry to the test of XD.

Visual reading of the scan (JP2 0056). The cells with '?' in the reading were decided by the
DATA XD, and so they stay out of the validation of XD itself (DECIDED).
"""
import numpy as np

_n = np.nan
CX2_538 = np.array([2.641, 2.64, 3.167, 3.694, _n, 4.626, 5.148, 5.716, 6.277,
                    5.691, 5.091, 4.518, 3.940, 3.225, 2.667, 2.19, 1.714])
DECIDED = {3: "read 3.6?4", 10: "read 5.?91"}
ILLEGIBLE = {4: "read 4.1??"}
# The printed CNα of the 5"/38 is suspect from Mach 2.5 to 5 (NOTES, T5): on those lines CX2
# does not serve to test XD, because the equation uses the table's own CNα.
CNA_SUSPECT = range(13, 17)
