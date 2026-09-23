import numpy as np, itertools
from diagnostico import resid, XB, MACH, P
R,X=resid(XB)
TOL=0.0012
out={}
for j,M in enumerate(MACH):
    r=R[j]; idx=[i for i in range(len(P)) if np.isfinite(r[i])]
    if max(abs(r[i]) for i in idx)<=TOL: continue
    sols=[]
    for nout in (0,1,2):
        for outl in itertools.combinations(idx,nout):
            keep=[i for i in idx if i not in outl]
            if max(abs(r[i]) for i in keep)<=TOL: sols.append((nout,0,(),(),[P[o] for o in outl])); continue
            for ncoef in (1,2):
                for ks in itertools.combinations(range(9),ncoef):
                    A=X[j][np.ix_(keep,list(ks))]
                    if np.linalg.matrix_rank(A)<ncoef: continue
                    d,*_=np.linalg.lstsq(A,-r[keep],rcond=None)
                    if np.abs(r[keep]+A@d).max()<=TOL:
                        sols.append((nout,ncoef,tuple(k+1 for k in ks),tuple(np.round(XB[list(ks),j]+d,4)),[P[o] for o in outl]))
        if sols: break
    sols.sort(key=lambda s:(s[0],s[1]))
    print(f"M={M:4.2f}:", sols[:6] if sols else "nenhuma solução simples")
