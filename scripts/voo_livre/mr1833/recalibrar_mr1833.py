"""
Recalibração por mínimos quadrados com os dados de voo livre do BRL MR 1833 (7.62 NATO).

O que dá para ajustar com ESTES dados
-------------------------------------
Os quatro projéteis têm a mesma ogiva (VN = 1.80), o mesmo raio de ogiva e o mesmo
meplat. Três têm o mesmo boattail. M-59 e M-61 são quase idênticos. Na prática são
~3 formas distintas, que diferem sobretudo no comprimento do corpo. Por isso cada
equação do SPIN-73 colapsa num MODELO REDUZIDO: um termo constante (que absorve todos
os termos de ogiva, boattail, meplat e cinta, fixos na família) mais os termos de
comprimento. `identificabilidade()` mostra isso numericamente (posto da matriz de
regressores completa do SPIN-73 avaliada nas quatro geometrias).

Dependência em Mach: cada constante do modelo reduzido é um polinômio quadrático em
(M - 2), ajustado só no supersônico (M >= 1.1), onde há dados dos quatro projéteis.
Os valores são depois avaliados nos pontos da grade do SPIN-73.

Incerteza: MMQ ordinário; sigma estimado pelos resíduos; erro-padrão pela matriz
(X'X)^-1. O resíduo é comparado ao "erro puro" -- a dispersão entre rodadas repetidas
do mesmo projétil em Mach quase igual -- para testar falta de ajuste.
"""
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import caminhos  # noqa: E402
import magnus_clp as mc

ler = lambda f: list(csv.DictReader(l for l in open(caminhos.VOO_LIVRE / f, encoding="utf-8")
                                    if not l.startswith("#")))
GEO = {r["projetil"]: {k: float(r[k]) for k in ("VL", "VN", "VB", "VCG")} for r in ler("mr1833_geometria.csv")}
RAW = ler("mr1833_tabela2.csv")
GRADE = np.array([1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0])     # pontos do SPIN-73 dentro dos dados
MMIN = 1.1


def f(x):
    return float(x) if x not in ("", None) else np.nan


# --------------------------------------------------------------------------- dados
def tabela():
    """Linhas com as grandezas já na normalização do SPIN-73."""
    out = []
    for r in RAW:
        g = GEO[r["projetil"]]
        yaw = f(r["YAW_RMS_DEG"])
        yaw2 = np.radians(yaw) ** 2
        # redução do CD a guinada zero (relatório p. 20): CD_d2 = 6.0/rad^2 até a guinada de
        # separação (8 graus no M-80, 3 graus nos demais) e 2.7/rad^2 acima dela. Interpretado
        # como lei por partes CONTÍNUA (hipótese): 6.0*ys^2 + 2.7*(y^2 - ys^2) para y > ys.
        ys2 = np.radians(8.0 if r["projetil"] == "M-80" else 3.0) ** 2
        inc = 6.0 * yaw2 if yaw2 <= ys2 else 6.0 * ys2 + 2.7 * (yaw2 - ys2)
        cna, cma = f(r["CNA"]), f(r["CMA"])
        out.append(dict(
            proj=r["projetil"], M=f(r["MACH"]), yaw=yaw, **g,
            CXCL=g["VL"] - g["VN"] - g["VB"] - 1.5,        # variável de comprimento do CX
            CXLL=g["VL"] - g["VN"] - g["VB"] - 2.15,       # variável de comprimento do CNa/CP
            CLL=g["VL"] - 5.0, CCG=g["VCG"] - 3.0,          # variáveis do Cmq
            CD0=f(r["CD"]) - inc,
            CNA=cna, CMA=cma,
            MNARIZ=cna * g["VCG"] - cma,                    # CNa*CPN: momento em torno do nariz
            CMQ=2 * f(r["CMQ"]),                            # q*d/V -> q*d/(2V)
            CNPA=2 * f(r["CMPA"]),                          # p*d/V -> p*d/(2V)
        ))
    return out


# --------------------------------------------------------------------------- MMQ
def base_mach(M):
    x = np.asarray(M) - 2.0
    return np.c_[np.ones_like(x), x, x * x]


def mmq(linhas, y, regs, projs):
    """y(M, geo) = sum_k g_k(M) * reg_k(geo), com g_k quadrático em M."""
    L = [l for l in linhas if l["proj"] in projs and l["M"] >= MMIN and np.isfinite(l[y])]
    B = base_mach([l["M"] for l in L])
    R = np.array([[reg(l) for reg in regs.values()] for l in L])
    X = np.hstack([B * R[:, [k]] for k in range(R.shape[1])])
    Y = np.array([l[y] for l in L])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta
    dof = len(Y) - X.shape[1]
    s2 = res @ res / dof
    cov = s2 * np.linalg.pinv(X.T @ X)
    return dict(L=L, beta=beta, cov=cov, res=res, s=np.sqrt(s2), dof=dof, nomes=list(regs),
                cond=np.linalg.cond(X))


def avaliar(fit, M):
    """Cada termo do modelo reduzido nos Mach pedidos, com erro-padrão."""
    B = base_mach(M)
    out = {}
    for k, nome in enumerate(fit["nomes"]):
        sl = slice(3 * k, 3 * k + 3)
        out[nome] = (B @ fit["beta"][sl],
                     np.sqrt(np.einsum("ij,jk,ik->i", B, fit["cov"][sl, sl], B)))
    return out


def erro_puro(linhas, y, projs, dM=0.05):
    """Desvio-padrão entre rodadas do mesmo projétil com Mach a menos de dM."""
    d = []
    L = sorted([l for l in linhas if l["proj"] in projs and l["M"] >= MMIN and np.isfinite(l[y])],
               key=lambda l: (l["proj"], l["M"]))
    for a, b in zip(L, L[1:]):
        if a["proj"] == b["proj"] and abs(a["M"] - b["M"]) < dM:
            d.append(a[y] - b[y])
    return np.sqrt(np.mean(np.square(d)) / 2) if d else np.nan, len(d)


# --------------------------------------------------------------------------- análise
def identificabilidade():
    """Posto das matrizes de regressores COMPLETAS do SPIN-73 nas 4 geometrias."""
    P = ["M-80", "M-59", "M-61", "M-62"]
    out = {}
    for nome, cols in {
        "CX (a1..a12, sem a10)": lambda g: [1, 0, 0, 0,  # termos de VNX (constantes: VN fixo)
                                            g["VL"] - g["VN"] - g["VB"] - 1.5,
                                            (g["VL"] - g["VN"] - g["VB"] - 1.5) ** 2,
                                            g["VB"] - 0.2, 1, 1, 1, 1],
        "CNa (B1..B9)": lambda g: [1, 1, g["VL"] - g["VN"] - g["VB"] - 2.15, 1, 1,
                                   (g["VL"] - g["VN"] - g["VB"] - 2.15) ** 2,
                                   g["VB"] ** 1.5, g["VB"], g["VB"] * (g["VL"] - g["VN"] - g["VB"] - 2.15)],
        "Cmq (F1..F8)": lambda g: [1, g["VL"] - 5, (g["VL"] - 5) ** 2, g["VCG"] - 3,
                                   (g["VCG"] - 3) * (g["VL"] - 5), (g["VCG"] - 3) * (g["VL"] - 5) ** 2,
                                   (g["VCG"] - 3) * g["VB"], g["VB"]],
    }.items():
        A = np.array([cols(GEO[p]) for p in P], float)
        sv = np.linalg.svd(A, compute_uv=False)
        out[nome] = (A.shape[1], int(np.sum(sv > 1e-3 * sv[0])), sv / sv[0])
    return out


MODELOS = {
    # coeficiente: (regressores do modelo reduzido, projéteis usados, justificativa das exclusões)
    "CD0": ({"const": lambda l: 1, "CXCL": lambda l: l["CXCL"]}, ["M-80", "M-59"],
            "M-61 (2a ranhura, +10% de arrasto) e M-62 (base arredondada, traçante) fora"),
    "CNA": ({"const": lambda l: 1, "CXLL": lambda l: l["CXLL"]}, ["M-80", "M-59", "M-61", "M-62"], ""),
    "MNARIZ": ({"const": lambda l: 1, "CXLL": lambda l: l["CXLL"]}, ["M-80", "M-59", "M-61", "M-62"], ""),
    "CMQ": ({"const": lambda l: 1, "CLL": lambda l: l["CLL"]}, ["M-80", "M-59", "M-61", "M-62"], ""),
}


def ajuste_magnus(linhas):
    """Magnus na forma do SPIN-73, com E1 fixo no valor adaptado.
    Cnpa = VCG*CYPA + CNPAN, CNPAN = -E1*VL*(E + 0.55*CXCL + 0.8*CVN) + VB*VL/4.7,
    linear em E. Ajusta-se um E efetivo (na guinada média das rodadas) quadrático em M."""
    L = [l for l in linhas if l["M"] >= MMIN and np.isfinite(l["CNPA"])]
    X, Y = [], []
    for l in L:
        e1 = np.interp(l["M"], mc.MACH, mc.E1)
        VL, VB, VN, VCG = l["VL"], l["VB"], l["VN"], l["VCG"]
        cypa = e1 * VL - 0.1 * VB
        c0 = VCG * cypa - e1 * VL * (0.55 * l["CXCL"] + 0.8 * (VN - 2.5)) + VB * VL / 4.7
        X.append(-e1 * VL * base_mach(l["M"])[0]); Y.append(l["CNPA"] - c0)
    X, Y = np.array(X), np.array(Y)
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta
    s2 = res @ res / (len(Y) - 3)
    return dict(L=L, beta=beta, cov=s2 * np.linalg.inv(X.T @ X), res=res, s=np.sqrt(s2), nomes=["E"])


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True, linewidth=150)
    lin = tabela()

    print("=" * 78 + "\nIDENTIFICABILIDADE: equações completas do SPIN-73 nas 4 geometrias da 7.62\n" + "=" * 78)
    for nome, (n, posto, sv) in identificabilidade().items():
        print(f"  {nome:24s} {n} constantes -> posto {posto}   (valores singulares relativos {sv.round(3)})")

    for y, (regs, projs, obs) in MODELOS.items():
        fit = mmq(lin, y, regs, projs)
        ep, npar = erro_puro(lin, y, projs)
        print("\n" + "=" * 78 + f"\n{y}   modelo: " + " + ".join(f"g_{k}(M)*{k}" for k in regs)
              + f"\n  projéteis: {', '.join(projs)}" + (f"   ({obs})" if obs else ""))
        print(f"  n = {len(fit['L'])}, parâmetros = {len(fit['beta'])}, resíduo rms = {fit['s']:.3f}, "
              f"erro puro (repetições) = {ep:.3f} [{npar} pares], cond(X) = {fit['cond']:.0f}")
        ev = avaliar(fit, GRADE)
        print("  Mach:     " + "".join(f"{m:>12.2f}" for m in GRADE))
        for k, (v, e) in ev.items():
            print(f"  {k:9s} " + "".join(f"{a:7.3f}±{b:<4.3f}" for a, b in zip(v, e)))

    fit = ajuste_magnus(lin)
    ev = avaliar(fit, GRADE)["E"]
    print("\n" + "=" * 78 + "\nMAGNUS: E efetivo recalibrado (E1 fixo no valor adaptado)")
    print(f"  n = {len(fit['L'])}, resíduo rms em Cnpa = {fit['s']:.3f}")
    print("  Mach:        " + "".join(f"{m:>12.2f}" for m in GRADE))
    print("  E recalibr.  " + "".join(f"{a:7.2f}±{b:<4.2f}" for a, b in zip(*ev)))
    print("  E2 SPIN-73   " + "".join(f"{np.interp(m, mc.MACH, mc.E2):12.2f}" for m in GRADE))
    print("  E4 SPIN-73   " + "".join(f"{np.interp(m, mc.MACH, mc.E4):12.2f}" for m in GRADE))
