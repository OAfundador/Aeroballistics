"""DATA blocks XC1..XC17 of SPIN-73, read from the scan (printed p. 80 = JP2 0083).

Reading from this task (A). Page rotated -90 degrees; character grid of the listing:
    x(column) = 1158 + (column - 6) * 19.2 px      (column 6 = continuation mark)
Each statement takes 2 cards. The observed splits are:
    XC1  : 11 + 6
    XC2..XC16 : 8 + 9
    XC17 : 10 + 7
Order of the 17 values = the XMACH Mach grid.

PRINTING DEFECT (a finding of this task): lines y=1867 and y=1900 of the rotated page are
the SAME image (pixel correlation 0.90 against 0.65 for the neighboring line, which has the
same text prefix) and both carry the label "XC16". The continuation card of XC15 was replaced
by a second copy of the first card of XC16. Hence XC15[8:17] (Mach 1.2 to 5.0) does NOT exist
in the printed listing: it comes from the tables (RECOVERED and DECIDED_M437, below).

'?' in comments = doubtful digit.
"""
import numpy as np

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])

_n = np.nan

# XC1..XC5: earlier reading (scripts/reconstruction/xc_partial.py), rechecked here on the
# digits marked as doubtful (see docs/TRANSCRIPTION_NOTES.md, T6).
XC = np.array([
 # XC1  (11+6) -- 2nd, 9th, 14th, 15th were doubtful in the earlier reading
 [1.71, 1.70, 1.66, 1.63, 1.60, 1.58, 1.56, 1.55, 1.57, 1.63, 1.70, 1.79, 1.88, 1.90, 2.03, 2.00, 1.97],
 # XC2  (8+9)  -- continuation starts at .5614 (index 8), 8+9 split CONFIRMED
 [.6995, .6995, .6995, .7224, .7301, .7314, .5611, .5614, .5614, .5595, .5553, .5324, .5195, .4993, .4867, .4867, .4867],
 # XC3
 [-.4425, -.4425, -.4425, -.3199, -.2661, -.2174, .1353, .1304, .1214, .1094, .0992, .0996, .0844, .0880, .1376, .1376, .1376],
 # XC4  -- 8+9 split CONFIRMED (continuation = .1044,.1044,.1044,.1188,...)
 [-.2241, -.2241, -.2241, -.2241, -.2241, -.2241, .1044, .1044, .1044, .1044, .1044, .1188, .1188, .1188, .1188, .1188, .1188],
 # XC5
 [.0136, .0136, .0136, .0172, .0190, .0207, .0542, .0514, .0466, .0377, .0295, .0216, .0170, .0078, -.0014, -.0014, -.0014],
 # XC6  -- 7th value (Mach 1.05) doubtful: 0.0001? ; 2nd value read 0.0449 (=1st and 3rd)
 [.0449, .0449, .0449, .0413, .0395, .0377, .0001, -.0001, -.0006, -.0014, -.0021, -.0065, -.0093, -.0150, -.0207, -.0207, -.0207],
 # XC7
 [-.0016, -.0016, -.0016, -.0016, -.0016, -.0016, .0033, .0033, .0033, .0033, .0033, .0036, .0036, .0036, .0036, .0036, .0036],
 # XC8  -- 9th value (-.6601) decided by the 253/254 regularity of the differences
 [-.5470, -.5470, -.5470, -.5793, -.5955, -.6117, -.6854, -.6770, -.6601, -.6348, -.6094, -.5742, -.5429, -.4804, -.4178, -.4178, -.4178],
 # XC9
 [-.1383, -.1383, -.1383, .0278, .1109, .1939, .4924, .4636, .4061, .3199, .2336, .1217, .0431, -.1142, -.2714, -.2714, -.2714],
 # XC10
 [-.7422, -.7422, -.7422, -.7422, -.7422, -.7422, -.6280, -.6280, -.6280, -.6280, -.6280, -.6031, -.6031, -.6031, -.6031, -.6031, -.6031],
 # XC11
 [-.4712, -.4712, -.4712, -.4712, -.4712, -.4712, -.6396, -.6257, -.5977, -.5557, -.5138, -.4768, -.4303, -.3332, -.2361, -.2361, -.2361],
 # XC12 -- very faded line; see docs/TRANSCRIPTION_NOTES.md, T6 (5 doubtful cells)
 [-3.650, -3.670, -3.897, -4.174, -4.203, -2.936, -2.646, -1.314, -1.162, -.8054, -.6033, -.3949, -.2274, .1794, .1794, .1794, .1794],
 # XC13
 [-.9349, -.9349, -.9349, -1.748, -1.748, -1.748, -1.933, -1.933, -1.474, -1.474, -1.427, -1.427, -.9122, -.6300, -.6300, -.6300, -.6300],
 # XC14
 [.3306, .3306, .3306, .3306, -.7872, -.7672, -.9731, -.9731, -.6906, -.6906, -.5391, -.5391, .0271, .2332, .2332, .2332, .2332],
 # XC15 -- continuation card MISSING from the listing (see header): first 8 read
 [0.0, 0.0, 0.0, 0.0, .6954, .7100, 1.0097, 1.0043, _n, _n, _n, _n, _n, _n, _n, _n, _n],
 # XC16 -- 7th value: 11.766 in one copy, 11.768 in the other (same card printed twice)
 [0.0, 0.0, 0.0, 0.0, 5.0334, 5.9629, 11.766, 11.457, 9.1476, 8.4991, 7.6084, 6.6724, 6.1030, 6.1493, 6.1493, 6.1493, 6.1493],
 # XC17 (10+7) -- only enters when VN > 3 (DNX > 0): of the 14 tables, only the 175 SRC
 [.35, .35, .35, .35, .35, .37, .44, .44, .44, .42, .35, .30, .30, .28, .28, .28, .28],
])

# Corrections decided by the model (1-based XC row, 0-based Mach index): (read, decided).
# They stay OUT of any validation done with the tables that decided them.
CORRECTIONS = {
    # The XC12 line is faded. At Mach 1.05 the read value does not reproduce the printed CPN
    # of either of the two tables tested. A single number corrects both at the same time:
    # 175 mm M437 (weight 0.623) and 5"/38 (weight 0.154) ask for Delta = 0.9598 and 0.9616,
    # and with -1.684 the residuals drop to +0.0008 and -0.0001. See TRANSCRIPTION_NOTES.md, section T6.
    (12, 6): (-2.646, -1.684),
    # Mach 0.8: the only candidate compatible with both tables (NOTES, T6.1); the swap is the
    # 6/8 pair and it zeroes both residuals at the same time (M437 +0.036 -> −0.002;
    # 5"/38 +0.024 -> 0.000).
    (1, 2): (1.66, 1.68),
    # Mach 0.6: equal to the Mach 0.01 value, as in XC2..XC11. Improves both tables
    # (M437 +0.016 -> −0.004; 5"/38 +0.006 -> +0.001); the M437 residual is still open.
    (12, 1): (-3.670, -3.650),
    # --- Third table with a boattail: 105 mm XM380E5 (p. 50). See NOTES, section T13. ---
    # Mach 2.5: with XC15 constant from 2.5 to 5 (below), the M437 alone asks for XC1 = 1.9899.
    # The listing glyph is ambiguous between 0 and 9 and the row becomes 1.88 1.99 2.03 2.00 1.97.
    # Independent check: the XM380E5 CPN at Mach 2.5 goes from −0.080 to +0.0001, and the
    # 5"/38 one from −0.168 to +0.0004 (with card C205, NOTES T15).
    (1, 13): (1.90, 1.99),
    # Mach 1.35 and 1.5: the 3rd digit is erased (0 or 1) and the 4th is ambiguous (3 or 7). The
    # M437 and 5"/38 tables ask for −0.8157 and −0.6192; the only values compatible with the
    # glyph are −.8154 and −.6173. The XM380E5, which did not enter the decision, closes at
    # 0.0000 and −0.0009.
    (12, 9): (-.8054, -.8154),
    (12, 10): (-.6033, -.6173),
    # Mach 1.0: the M437 alone asks for −0.7867. With −.7872 (pair 6/8), XC14 repeats at
    # Mach 1.0 the value of Mach 0.95, as it does in pairs along the whole row (−.9731 −.9731
    # −.6906 −.6906 −.5391 −.5391). The 5"/38 and the XM380E5 barely weigh here (CXLL ≈ −0.06):
    # no check.
    (14, 5): (-.7672, -.7872),
}

# Cells whose visual reading stayed doubtful (1-based XC row, 0-based Mach index).
DOUBTFUL = {
    (1, 13): "1.9? (0 or 9)",
    (6, 6): "0.0001? (middle glyph erased)",
    (12, 1): "-3.670? (faded line; the 1st value -3.650 and the 2nd could be equal)",
    (12, 5): "-2.936?",
    (12, 6): "-2.646?",
    (12, 8): "-1.162?",
    (12, 9): "-.8?54? (3rd digit erased)",
    (12, 10): "-.6??3 (3rd and 4th digits erased)",
    (14, 5): "-.7?72 (6 or 8)",
    (16, 6): "11.766 / 11.768 (the two copies of the card disagree)",
}

MISSING = {15: list(range(8, 17))}  # XC15: continuation card not printed

# Cells of the missing card recovered from the printed tables (decided by the model).
# Method: at each Mach, XC12 and XC15 are the two unknowns of the boattail block; the CPN
# columns of the 175 mm M437 and the 5"/38 give two equations. Where the solved XC12 matches
# the value READ in the listing, the system is consistent and the XC15 obtained is reliable:
#   Mach 1.2 : XC12 solved -1.1630 against -1.1620 read  -> XC15 = 1.437
#   Mach 2.0 : XC12 solved -0.2266 against -0.2274 read  -> XC15 = 0.208
#   Mach 1.35: with XC12 corrected to −.8154 (CORRECTIONS), M437 and 5"/38 ask for 2.0061 and
#              2.0035 -> 2.0052 (least squares); the XM380E5 asks for 2.0107 (small weight)
#   Mach 1.5 : with XC12 = −.6173, M437 and 5"/38 ask for 0.9904 and 0.9717 -> 0.9839
# See TRANSCRIPTION_NOTES.md, sections T6.2 and T13.
RECOVERED = {(15, 8): 1.4366, (15, 9): 2.0052, (15, 10): 0.9839, (15, 12): 0.2079}

# Mach 1.75: decided ONLY by the M437 (0.5500). The XM380E5 closes (+0.0003) and, after card
# C205 (NOTES, T15), so does the 5"/38 (−0.0002), which earlier seemed to ask for 0.629.
#
# Mach 2.5 to 5: in rows XC12, XC13, XC14 and XC16 the last four listing values are equal;
# XC15 follows the same pattern. The M437 asks for −0.9152, −0.9211 and −0.9190 at Mach 3, 4
# and 5, equal within the print resolution (±0.008): the mean holds, −0.9184. At Mach 2.5 it
# asks for −0.9167 after XC1 is corrected (CORRECTIONS). The XM380E5 closes at all four Mach
# numbers (residual ≤ 0.0005), but weighs little on XC15 (CCRT ≈ 0). The 5"/38 sits 0.006 to
# 0.009 low at 2.5, 4 and 5: it was card C205, which was missing (NOTES, T15); with it the
# 5"/38 closes at 2.5 and 5 and sits at +0.0023 at 4.
DECIDED_M437 = {(15, 11): 0.5500, **{(15, j): -0.9184 for j in (13, 14, 15, 16)}}
UNCERTAIN = {}

for (_row, _j), _v in {**RECOVERED, **DECIDED_M437}.items():
    XC[_row - 1, _j] = _v

XC_READ = XC.copy()
for (_row, _j), (_read, _dec) in CORRECTIONS.items():
    assert abs(XC[_row - 1, _j] - _read) < 1e-9, (_row, _j)
    XC[_row - 1, _j] = _dec
