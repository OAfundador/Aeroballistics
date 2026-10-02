"""Adapted SPIN-73 Cmq: equation on p. 17 + DATA XF1..XF8 + UNDOCUMENTED term F9:
   Cmq = -5.093*[F1 + F2*CLL + F3*CLL^2 + F4*CCG + F5*CCG*CLL + F6*CCG*CLL^2 + F7*CCG*VB + F8*VB]
         - F9*max(0, VL - 6)
F9 identified from the 20 mm 9 cal table (deviation = 2.99*F9 with VL - 6 = 3)."""
import numpy as np
from aeroballistics.data.xf_read import XF

def cmq(VL, VCG, VB, j):
    F = XF[:, j]; CLL = VL - 5.0; CCG = VCG - 3.0
    s = (F[0] + F[1]*CLL + F[2]*CLL**2 + F[3]*CCG + F[4]*CCG*CLL + F[5]*CCG*CLL**2
         + F[6]*CCG*VB + F[7]*VB)
    return -5.093 * s - F[8] * max(0.0, VL - 6.0)
