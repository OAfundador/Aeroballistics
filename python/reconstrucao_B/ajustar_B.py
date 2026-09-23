import numpy as np
from dados_cna import MACH, T

def regressores(VL, VN, VB, OR, M):
    sup = M >= 0.95                                  # limiar confirmado pelas tabelas (Mach 0.95 usa o expoente supersônico)
    A, _ = (1.5, 1.0) if sup else (1.0, 0.8)
    VNX = min(VN, 3.0)
    if VB <= 0: VBNP = VBX = 0.0
    elif VB < 1.0: VBNP, VBX = VB ** A, VB
    else: VBNP, VBX = VB ** 0.5, 1.0
    CVNN = VNX - 2.47; CXLL = VL - VN - VB - 2.15; CCRT = VN ** 2 / OR - 0.48
    return [1, CVNN, CXLL, CCRT, CVNN**2, CXLL**2, VBNP, VBX*CVNN, VBX*CXLL]

if __name__ == "__main__":
  np.set_printoptions(precision=4, suppress=True, linewidth=170)
  print("Mach  n posto  resid_max   B1..B9")
  for j, M in enumerate(MACH):
      X, Y, P = [], [], []
      for p, (n, VL, VN, VB, OR, cna) in T.items():
          if np.isfinite(cna[j]):
              X.append(regressores(VL, VN, VB, OR, M)); Y.append(cna[j]); P.append(p)
      X, Y = np.array(X), np.array(Y)
      b, *_ = np.linalg.lstsq(X, Y, rcond=None)
      r = Y - X @ b
      print(f"{M:4.2f} {len(Y):2d} {np.linalg.matrix_rank(X,1e-6):2d}  {np.abs(r).max():.4f}  {b}")
      if M in (0.6, 2.0):
          sv = np.linalg.svd(X, compute_uv=False); print("      val. sing. rel.:", (sv/sv[0]).round(4))
          print("      resíduos:", dict(zip(P, r.round(4))))
