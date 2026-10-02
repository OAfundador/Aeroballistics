"""DATA XE1..XE4, XF1..XF9 and XG1 read from the listing (p. 81 of the report, high-resolution JP2).
This page is printed in columns and is much more legible than pp. 79-80."""
import numpy as np
XE = np.array([
 [-.16,-.16,-.16,-.18,-.23,-.21,-.19,-.18,-.16,-.16,-.16,-.16,-.16,-.16,-.16,-.16,-.16],
 [1.8,1.8,2.0,2.4,2.7,2.8,2.9,2.95,2.98,3.00,3.01,3.02,3.03,3.04,3.05,3.05,3.05],
 [2.5,2.5,2.6,2.75,2.9,3.0,3.06,3.07,3.08,3.08,3.08,3.09,3.09,3.09,3.09,3.09,3.09],   # E3 (2 degrees): 3rd value doubtful
 [2.9,2.9,3.0,3.05,3.1,3.1,3.1,3.1,3.1,3.1,3.1,3.1,3.1,3.1,3.1,3.1,3.1],
])
XF = np.array([
 [1.72,1.72,1.72,2.31,2.88,3.79,3.84,4.24,4.64,4.93,5.21,5.21,5.21,5.21,5.21,5.21,5.21],
 [3.18]*7 + [3.29,3.4,3.4,3.4,3.4,3.4,3.4,3.40,3.40,3.40],
 [1.06,1.06,1.06,1.05,1.04,1.03,1.02,1.01,1.,1.,1.,1.,1.,1.,1.,1.,1.],
 [-3.3,-3.3,-3.3,-3.2,-3.18,-3.16,-3.13,-3.10,-3.00,-2.50,-1.59,-1.59,-1.59,-1.59,-1.59,-1.59,-1.59],
 [-1.3]*7 + [-1.28,-1.26,-1.26,-1.26,-1.26,-1.26,-1.26,-1.26,-1.26,-1.26],
 [0.]*17,
 [-.7]*7 + [-.715] + [-.73]*9,                                                     # 2nd card missing: see MISSING
 [1.09,1.09,1.09,.8,.6,.3,-.002,-.23,-.47,-1.15,-1.83,-1.83,-1.83,-1.83,-1.83,-1.83,-1.83],
 [0.]*9 + [1.0,2.0,4.0,6.0,8.0,8.0,6.0,3.0],                                       # F9: undocumented; number of zeros inferred (17 in total)
])

# PRINTING DEFECT in XF7 (the same as in XC15 and XE5): after the 1st card (7 values,
# Mach 0.01 to 1.05) come TWO copies of the 3rd card, "-.73, -.73, -.73 /". The 2nd card (7
# values, Mach 1.1 to 2.5) was not printed. The last 3 (Mach 3 to 5) are the printed ones.
# Recovered from the CMQ column of the 5"/38 (weight of XF7 = −5.093·(VCG−3)·VB = +0.52), which
# asks for −0.7146 at Mach 1.1 and −0.729 to −0.731 from 1.2 to 2.5. The M437 (weight −2.55)
# and the XM380E5 (−1.02), which did not enter the decision, ask for −0.7151 / −0.7150 and
# −0.7300 / −0.7298. It was the "misread XF at Mach 1.1" that kept the M437 Cmq 0.038 off
# (NOTES, section T13).
MISSING = {7: list(range(7, 14))}
RECOVERED = {(7, 7): -.715, **{(7, j): -.73 for j in range(8, 14)}}

XG1 = np.array([-.0364,-.0364,-.0346,-.0292,-.0254,-.0240,-.0238,-.0236,-.0234,-.0232,-.0230,-.0225,-.0220,-.0210,-.0200,-.0195,-.0190])
