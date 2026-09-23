"""Magnus reconstruído do SPIN-73 (E1, E2, E4) contra o experimento do BRL MR 1833.

Conversão de normalização: o SPIN-73 usa p*d/(2V); o MR 1833 usa p*d/V.
Logo Cnpa(SPIN) = 2 * Cmpa(MR 1833). Convenção de sinal assumida igual (BRL/Murphy).
Dependência com a guinada: o SPIN-73 dá Cnpa a 1, 2 e 5 graus. E3 (2 graus) ainda não
foi identificado, então interpolamos linearmente em alfa entre 1 e 5 graus (HIPÓTESE).
Entre pontos da grade de Mach, E é interpolado linearmente (HIPÓTESE).
"""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import magnus_clp as mc

AQUI = os.path.dirname(os.path.abspath(__file__))
ler = lambda f: list(csv.DictReader(l for l in open(os.path.join(AQUI, f)) if not l.startswith("#")))
GEO = {r["projetil"]: {k: float(r[k]) for k in ("VL", "VN", "VB", "VCG")} for r in ler("mr1833_geometria.csv")}
EXP = ler("mr1833_tabela2.csv")


def cnpa_spin(g, mach, alfa_deg):
    e1 = np.interp(mach, mc.MACH, mc.E1)
    e2 = np.interp(mach, mc.MACH, mc.E2)
    e4 = np.interp(mach, mc.MACH, mc.E4)
    VL, VB, VN, VCG = g["VL"], g["VB"], g["VN"], g["VCG"]
    CXCL, CVN = VL - VN - VB - 1.5, VN - 2.5
    cypa = e1 * VL - 0.1 * VB
    def cnpa(e):
        cnpan = -e1 * VL * (e + 0.55 * CXCL + 0.8 * CVN) + VB * VL / 4.7
        return (VCG + cnpan / cypa) * cypa           # (VCG - CPF)*CYPA, CPF = -CNPAN/CYPA
    w = (np.clip(alfa_deg, 1, 5) - 1) / 4
    return (1 - w) * cnpa(e2) + w * cnpa(e4)


if __name__ == "__main__":
    print(f"{'proj':5s} {'Mach':>6s} {'yaw':>5s} {'exp*2':>7s} {'SPIN':>7s} {'dif':>7s}")
    res = {}
    for r in EXP:
        if not r["CMPA"]:
            continue
        M, yaw, exp2 = float(r["MACH"]), float(r["YAW_RMS_DEG"]), 2 * float(r["CMPA"])
        if M < 0.9:     # grade do SPIN-73 começa em 0.01/0.6; subsônico do M-80 tem dados muito dispersos
            pass
        p = cnpa_spin(GEO[r["projetil"]], M, yaw)
        res.setdefault(r["projetil"], []).append((M, exp2, p))
        print(f"{r['projetil']:5s} {M:6.3f} {yaw:5.1f} {exp2:7.2f} {p:7.2f} {p - exp2:7.2f}")
    print("\nResumo (supersônico, M > 1.2):")
    for k, v in res.items():
        v = np.array([x for x in v if x[0] > 1.2])
        print(f"  {k}: exp*2 médio {v[:,1].mean():+.2f}   SPIN médio {v[:,2].mean():+.2f}   "
              f"viés {np.mean(v[:,2]-v[:,1]):+.2f}   dispersão exp {v[:,1].std():.2f}")
