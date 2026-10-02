"""SPIN-73 DATA blocks, gathered in one place (spin73.data).

Each array has shape (n, 17): row i = coefficient i+1, column j = MACH[j]. The values come
from the reconstruction modules, which keep the reading, the decided corrections and the
evidence for each one. Here we only assemble the set the program uses.

Status of each block (see docs/TRANSCRIPTION_NOTES.md):

  XA1..XA15  drag CX               read (p. 79); 4 cells decided by the tables;
                                   XA13..XA15 read but with no table to test them (VN > 3)
  XB1..XB10  normal force CNα      XB1..XB9 read (6 corrections decided); XB10 does not
                                   appear in the code transcribed so far
  XC1..XC17  center of pressure    read; the XC15 card is missing from the listing,
                                   recovered from the tables; 8 cells decided by the tables
                                   (three tables with a boattail: M437, 5"/38, XM380E5)
  XD1..XD4   CX2                   read; 4 cells decided by the tables
  XE1..XE4   Magnus                read (equal to those identified from the tables)
  XE5        Magnus, long body     last card read (Mach 2 to 5, agrees with the tables);
                                   the first card was not printed -> comes from the tables
  XF1..XF9   Cmq                   read; the 2nd card of XF7 is missing from the listing
                                   (Mach 1.1 to 2.5), recovered from the 5"/38
  XG1        Clp                   read
"""
import numpy as np

from .xa_read import XA as _XA
from .xb_read import XB as _XB
from .xc_read import XC as _XC
from .xd_read import XD as _XD
from .xf_read import XE as _XE, XF as _XF, XG1 as _XG1

XMACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                  1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
N = XMACH.size


def _nan(n):
    return np.full((n, N), np.nan)


XA = _XA.copy()

XB = np.vstack([_XB, _nan(1)])                       # XB10: no identified use

XC = _XC.copy()

XD = _XD.copy()

# XE5: long-body Magnus term, added to the CPF when VL > 6 (cards C216-C222).
# On p. 81 the continuation card "1 0.3,0.3,0.27,0.25,0.20/" (Mach 2 to 5) is printed
# twice and the first card (statement 57, Mach 0.01 to 1.75) is missing -- the same
# printing defect as XC15. The 5 printed values are exactly the ones the 7, 9 and
# 10 caliber tables had identified; the first 12 come from the tables.
_XE5 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .10, .20, .30, .30, .27, .25, .20])
XE = np.vstack([_XE, _XE5])

XF = _XF.copy()

XG = _XG1.reshape(1, N)

STATUS = {
    "XA": "read (4 cells decided; XA13-15 untested)", "XB": "read (XB10 unused)",
    "XC": "read, XC15 incomplete",
    "XD": "read (4 cells decided)", "XE": "read (XE5 identified from the tables)",
    "XF": "read", "XG": "read",
}
