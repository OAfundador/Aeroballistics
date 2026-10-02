"""Adapted SPIN-73 CNa: structure from the text (p. 14) + DATA XB1..XB9 as read (with
corrections decided by the model) + boattail exponent threshold at Mach 0.95 (confirmed by the tables)."""
import numpy as np
from aeroballistics.data.xb_read import XB
from data_cna import MACH
from fit_B import regressors

def cna_j(VL, VN, VB, OR, j, XB=XB):
    """CNα at grid point j. Card C205: the boattail part (B7..B9) cannot be positive (if it
    comes out positive, it is set to zero)."""
    x = np.array(regressors(VL, VN, VB, OR, MACH[j]))
    return float(x[:6] @ XB[:6, j] + min(x[6:] @ XB[6:, j], 0.0))


def cna(VL, VN, VB, OR, M):
    """Interpolates linearly in Mach between the grid points (the grid is the program's)."""
    vals = [cna_j(VL, VN, VB, OR, j) for j in range(len(MACH))]
    return float(np.interp(M, MACH, vals))
