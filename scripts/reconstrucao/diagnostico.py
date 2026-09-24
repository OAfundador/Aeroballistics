import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caminhos  # noqa: E402,F401
import numpy as np, itertools
from dados_cna import MACH, T
from ajustar_B import regressores
from spin73.dados.xb_lidos import XB
np.set_printoptions(precision=4, suppress=True, linewidth=180)
P=list(T)
def resid(XB):
    R=np.zeros((len(MACH),len(P)))
    X=np.zeros((len(MACH),len(P),9))
    for j,M in enumerate(MACH):
        for i,p in enumerate(P):
            n,VL,VN,VB,OR,cna=T[p]; x=np.array(regressores(VL,VN,VB,OR,M)); X[j,i]=x; R[j,i]=x@XB[:,j]-cna[j]
    return R,X
if __name__ == "__main__":
  R,X=resid(XB)
  print("Mach   "+" ".join(f"{p:>7d}" for p in P))
  for j,M in enumerate(MACH): print(f"{M:4.2f}  "+" ".join(f"{r:+7.3f}" for r in R[j]))
  print("\nCorreções de UM coeficiente por Mach que zeram o resíduo (|r| > 0.0015):")
  for j,M in enumerate(MACH):
      r=R[j]; ok=np.isfinite(r)
      if np.nanmax(np.abs(r))<0.0015: continue
      best=[]
      for k in range(9):
          x=X[j,ok,k]
          if np.allclose(x,0): continue
          d=-(x@r[ok])/(x@x); rr=r[ok]+d*x; best.append((np.abs(rr).max(),k+1,d,XB[k,j],XB[k,j]+d))
      for k2 in itertools.combinations(range(9),2):
          A=X[j][np.ix_(ok,list(k2))]
          if np.linalg.matrix_rank(A)<2: continue
          d,*_=np.linalg.lstsq(A,-r[ok],rcond=None); rr=r[ok]+A@d
          best.append((np.abs(rr).max(),tuple(k+1 for k in k2),tuple(np.round(d,4)),tuple(XB[list(k2),j]),tuple(np.round(XB[list(k2),j]+d,4))))
      best.sort(key=lambda t:t[0])
      print(f"M={M:4.2f} resid max {np.nanmax(np.abs(r)):.3f} ->", best[:3])
