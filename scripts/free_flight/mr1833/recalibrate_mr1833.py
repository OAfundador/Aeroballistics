"""
Least-squares recalibration with the free-flight data of BRL MR 1833 (7.62 NATO).

What can be fitted with THESE data
----------------------------------
The four projectiles have the same ogive (VN = 1.80), the same ogive radius and the same
meplat. Three have the same boattail. M-59 and M-61 are nearly identical. In practice they are
~3 distinct shapes, which differ mostly in body length. So each SPIN-73 equation collapses
into a REDUCED MODEL: a constant term (which absorbs all the ogive, boattail, meplat and band
terms, fixed in the family) plus the length terms. `identifiability()` shows this numerically
(rank of the complete SPIN-73 regressor matrix evaluated at the four geometries).

Mach dependence: each constant of the reduced model is a quadratic polynomial in (M - 2),
fitted only in the supersonic (M >= 1.1), where there are data for all four projectiles.
The values are then evaluated at the SPIN-73 grid points.

Uncertainty: ordinary least squares; sigma estimated from the residuals; standard error from
the (X'X)^-1 matrix. The residual is compared with the "pure error" -- the spread between
repeated rounds of the same projectile at nearly the same Mach -- to test for lack of fit.
"""
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths  # noqa: E402
import magnus_clp as mc

read_csv = lambda f: list(csv.DictReader(l for l in open(paths.FREE_FLIGHT / f, encoding="utf-8")
                                         if not l.startswith("#")))
GEO = {r["projectile"]: {k: float(r[k]) for k in ("VL", "VN", "VB", "VCG")} for r in read_csv("mr1833_geometry.csv")}
RAW = read_csv("mr1833_table2.csv")
GRID = np.array([1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0])     # SPIN-73 points inside the data
MMIN = 1.1


def f(x):
    return float(x) if x not in ("", None) else np.nan


# --------------------------------------------------------------------------- data
def table():
    """Rows with the quantities already in the SPIN-73 normalization."""
    out = []
    for r in RAW:
        g = GEO[r["projectile"]]
        yaw = f(r["YAW_RMS_DEG"])
        yaw2 = np.radians(yaw) ** 2
        # reduction of CD to zero yaw (report p. 20): CD_d2 = 6.0/rad^2 up to the separation yaw
        # (8 degrees on the M-80, 3 degrees on the others) and 2.7/rad^2 above it. Interpreted
        # as a CONTINUOUS piecewise law (assumption): 6.0*ys^2 + 2.7*(y^2 - ys^2) for y > ys.
        ys2 = np.radians(8.0 if r["projectile"] == "M-80" else 3.0) ** 2
        inc = 6.0 * yaw2 if yaw2 <= ys2 else 6.0 * ys2 + 2.7 * (yaw2 - ys2)
        cna, cma = f(r["CNA"]), f(r["CMA"])
        out.append(dict(
            proj=r["projectile"], M=f(r["MACH"]), yaw=yaw, **g,
            CXCL=g["VL"] - g["VN"] - g["VB"] - 1.5,        # CX length variable
            CXLL=g["VL"] - g["VN"] - g["VB"] - 2.15,       # CNa/CP length variable
            CLL=g["VL"] - 5.0, CCG=g["VCG"] - 3.0,          # Cmq variables
            CD0=f(r["CD"]) - inc,
            CNA=cna, CMA=cma,
            MNOSE=cna * g["VCG"] - cma,                     # CNa*CPN: moment about the nose
            CMQ=2 * f(r["CMQ"]),                            # q*d/V -> q*d/(2V)
            CNPA=2 * f(r["CMPA"]),                          # p*d/V -> p*d/(2V)
        ))
    return out


# --------------------------------------------------------------------------- least squares
def mach_basis(M):
    x = np.asarray(M) - 2.0
    return np.c_[np.ones_like(x), x, x * x]


def lsq(rows, y, regs, projs):
    """y(M, geo) = sum_k g_k(M) * reg_k(geo), with g_k quadratic in M."""
    L = [l for l in rows if l["proj"] in projs and l["M"] >= MMIN and np.isfinite(l[y])]
    B = mach_basis([l["M"] for l in L])
    R = np.array([[reg(l) for reg in regs.values()] for l in L])
    X = np.hstack([B * R[:, [k]] for k in range(R.shape[1])])
    Y = np.array([l[y] for l in L])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta
    dof = len(Y) - X.shape[1]
    s2 = res @ res / dof
    cov = s2 * np.linalg.pinv(X.T @ X)
    return dict(L=L, beta=beta, cov=cov, res=res, s=np.sqrt(s2), dof=dof, names=list(regs),
                cond=np.linalg.cond(X))


def evaluate(fit, M):
    """Each term of the reduced model at the requested Mach numbers, with its standard error."""
    B = mach_basis(M)
    out = {}
    for k, name in enumerate(fit["names"]):
        sl = slice(3 * k, 3 * k + 3)
        out[name] = (B @ fit["beta"][sl],
                     np.sqrt(np.einsum("ij,jk,ik->i", B, fit["cov"][sl, sl], B)))
    return out


def pure_error(rows, y, projs, dM=0.05):
    """Standard deviation between rounds of the same projectile with Mach less than dM apart."""
    d = []
    L = sorted([l for l in rows if l["proj"] in projs and l["M"] >= MMIN and np.isfinite(l[y])],
               key=lambda l: (l["proj"], l["M"]))
    for a, b in zip(L, L[1:]):
        if a["proj"] == b["proj"] and abs(a["M"] - b["M"]) < dM:
            d.append(a[y] - b[y])
    return np.sqrt(np.mean(np.square(d)) / 2) if d else np.nan, len(d)


# --------------------------------------------------------------------------- analysis
def identifiability():
    """Rank of the COMPLETE SPIN-73 regressor matrices at the 4 geometries."""
    P = ["M-80", "M-59", "M-61", "M-62"]
    out = {}
    for name, cols in {
        "CX (a1..a12, no a10)": lambda g: [1, 0, 0, 0,   # VNX terms (constants: VN fixed)
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
        out[name] = (A.shape[1], int(np.sum(sv > 1e-3 * sv[0])), sv / sv[0])
    return out


MODELS = {
    # coefficient: (regressors of the reduced model, projectiles used, reason for the exclusions)
    "CD0": ({"const": lambda l: 1, "CXCL": lambda l: l["CXCL"]}, ["M-80", "M-59"],
            "M-61 (2nd knurl, +10% drag) and M-62 (rounded base, tracer) out"),
    "CNA": ({"const": lambda l: 1, "CXLL": lambda l: l["CXLL"]}, ["M-80", "M-59", "M-61", "M-62"], ""),
    "MNOSE": ({"const": lambda l: 1, "CXLL": lambda l: l["CXLL"]}, ["M-80", "M-59", "M-61", "M-62"], ""),
    "CMQ": ({"const": lambda l: 1, "CLL": lambda l: l["CLL"]}, ["M-80", "M-59", "M-61", "M-62"], ""),
}


def magnus_fit(rows):
    """Magnus in the SPIN-73 form, with E1 fixed at the reconstructed value.
    Cnpa = VCG*CYPA + CNPAN, CNPAN = -E1*VL*(E + 0.55*CXCL + 0.8*CVN) + VB*VL/4.7,
    linear in E. An effective E (at the rounds' mean yaw), quadratic in M, is fitted."""
    L = [l for l in rows if l["M"] >= MMIN and np.isfinite(l["CNPA"])]
    X, Y = [], []
    for l in L:
        e1 = np.interp(l["M"], mc.MACH, mc.E1)
        VL, VB, VN, VCG = l["VL"], l["VB"], l["VN"], l["VCG"]
        cypa = e1 * VL - 0.1 * VB
        c0 = VCG * cypa - e1 * VL * (0.55 * l["CXCL"] + 0.8 * (VN - 2.5)) + VB * VL / 4.7
        X.append(-e1 * VL * mach_basis(l["M"])[0]); Y.append(l["CNPA"] - c0)
    X, Y = np.array(X), np.array(Y)
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta
    s2 = res @ res / (len(Y) - 3)
    return dict(L=L, beta=beta, cov=s2 * np.linalg.inv(X.T @ X), res=res, s=np.sqrt(s2), names=["E"])


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True, linewidth=150)
    rows = table()

    print("=" * 78 + "\nIDENTIFIABILITY: complete SPIN-73 equations at the 4 geometries of the 7.62\n" + "=" * 78)
    for name, (n, rank, sv) in identifiability().items():
        print(f"  {name:24s} {n} constants -> rank {rank}   (relative singular values {sv.round(3)})")

    for y, (regs, projs, note) in MODELS.items():
        fit = lsq(rows, y, regs, projs)
        ep, npairs = pure_error(rows, y, projs)
        print("\n" + "=" * 78 + f"\n{y}   model: " + " + ".join(f"g_{k}(M)*{k}" for k in regs)
              + f"\n  projectiles: {', '.join(projs)}" + (f"   ({note})" if note else ""))
        print(f"  n = {len(fit['L'])}, parameters = {len(fit['beta'])}, rms residual = {fit['s']:.3f}, "
              f"pure error (repeats) = {ep:.3f} [{npairs} pairs], cond(X) = {fit['cond']:.0f}")
        ev = evaluate(fit, GRID)
        print("  Mach:     " + "".join(f"{m:>12.2f}" for m in GRID))
        for k, (v, e) in ev.items():
            print(f"  {k:9s} " + "".join(f"{a:7.3f}±{b:<4.3f}" for a, b in zip(v, e)))

    fit = magnus_fit(rows)
    ev = evaluate(fit, GRID)["E"]
    print("\n" + "=" * 78 + "\nMAGNUS: recalibrated effective E (E1 fixed at the reconstructed value)")
    print(f"  n = {len(fit['L'])}, rms residual in Cnpa = {fit['s']:.3f}")
    print("  Mach:        " + "".join(f"{m:>12.2f}" for m in GRID))
    print("  E recalibr.  " + "".join(f"{a:7.2f}±{b:<4.2f}" for a, b in zip(*ev)))
    print("  E2 SPIN-73   " + "".join(f"{np.interp(m, mc.MACH, mc.E2):12.2f}" for m in GRID))
    print("  E4 SPIN-73   " + "".join(f"{np.interp(m, mc.MACH, mc.E4):12.2f}" for m in GRID))
