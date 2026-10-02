"""
Cmq and center of pressure of the adapted SPIN-73 against the BRL MR 1833 free flight (7.62 NATO).

Completes the comparison that already existed for Magnus (`compare_magnus.py`) and for CNα
(group 762 in `../correction/flight_data.py`): now that XF (Cmq, with the F9 term) and XC
(center of pressure) have been read, both can be confronted with experiment.

Normalizations (see README.md): MR 1833 gives Cmq+Cmα̇ with q·d/V, SPIN-73 uses q·d/(2V), hence
the factor 2 already applied in `recalibrate_mr1833.table()`. The center of pressure comes
from the table itself through the identity CPN = (CNα·VCG − CMα)/CNα, in calibers from the
nose, which is the SPIN-73 convention.

ASSUMPTIONS, as in `compare_magnus.py`:
  - between points of the SPIN-73 Mach grid, linear interpolation;
  - the ogive radius of the 7.62 family is uncertain (the figure shows "30R" ≈ 9.74 cal). It
    enters the CPN through CCRT = VN²/OR − 0.48, so the sensitivity to this assumption is
    reported.

Cmq and CPN exist at all 17 points. The continuation card of XC15 was not printed in the
report (TRANSCRIPTION_NOTES.md, T6), and the nine cells from Mach 1.2 to 5.0 were DECIDED BY
THE MODEL from the 1973 tables (xc_read: RECOVERED and DECIDED_M437), as were some reading
corrections in the same range (CORRECTIONS). None came from free flight, so the comparison is
not circular, but the model's CPN above Mach 1.1 depends on them: the output lists the ones
that enter over the range of the rounds.

The experimental CPN is that of each round, VCG − CMα/CNα, with measured values only; the
fitted curve and the k(M) factor of the CPN do not use SPIN-73's CNα (the model's CNα has its
own bias, see `compare_cna.py`).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                       # noqa: E402,F401  (also makes the output UTF-8)

import recalibrate_mr1833 as r                     # noqa: E402
from cmq_spin73 import cmq as cmq_spin             # noqa: E402
from cpn_spin73 import cpn_cma, decided_cells      # noqa: E402

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
PROJECTILES = ["M-80", "M-59", "M-61", "M-62"]
OR_HYP = 9.74            # assumed ogive radius (calibers)
DM = 0.195


def table():
    """The rounds of `recalibrate_mr1833.table()` with the measured CPN, VCG − CMα/CNα."""
    rows = r.table()
    for l in rows:
        l["CPN"] = l["MNOSE"] / l["CNA"] if np.isfinite(l["MNOSE"]) and l["CNA"] else np.nan
    return rows


def cmq_curve(g):
    """SPIN-73 Cmq at the 17 Mach points, for geometry g."""
    return np.array([cmq_spin(g["VL"], g["VCG"], g["VB"], j) for j in range(17)])


def cpn_curve(g, OR=OR_HYP):
    """SPIN-73 CPN at the 17 points (NaN where DATA is missing)."""
    return np.array([cpn_cma(g["VL"], g["VN"], g["VB"], OR, DM, g["VCG"], j)[0]
                     for j in range(17)])


def per_round(rows, column, curve):
    """Bias per projectile: mean(model − experiment) against the spread of the experiment."""
    out = []
    for p in PROJECTILES:
        L = [l for l in rows if l["proj"] == p and l["M"] >= r.MMIN and np.isfinite(l[column])]
        if not L:
            continue
        g = r.GEO[p]
        y = np.array([l[column] for l in L])
        c = curve(g)
        m = np.array([np.interp(l["M"], MACH, c) for l in L])
        ok = np.isfinite(m)
        if not ok.any():
            continue
        out.append((p, len(y[ok]), float(np.mean(m[ok] - y[ok])), float(np.std(y[ok]))))
    return out


def against_fit(rows, column, curve, machs, model=None):
    """Model against the fitted experimental curve (least squares), at the requested grid points.

    `model` picks the reduced model from `r.MODELS` (default: the column's own)."""
    regs, projs, _ = r.MODELS[model or column]
    fit = r.lsq(rows, column, regs, projs)
    ev = r.evaluate(fit, machs)
    out_rows = []
    for p in PROJECTILES:
        g = r.GEO[p]
        c = curve(g)
        for i, M in enumerate(machs):
            exp = sum(ev[k][0][i] * reg({**g, "CXLL": g["VL"] - g["VN"] - g["VB"] - 2.15,
                                         "CLL": g["VL"] - 5.0, "CCG": g["VCG"] - 3.0,
                                         "CXCL": g["VL"] - g["VN"] - g["VB"] - 1.5})
                      for k, reg in regs.items())
            err = sum(ev[k][1][i] * abs(reg({**g, "CXLL": g["VL"] - g["VN"] - g["VB"] - 2.15,
                                             "CLL": g["VL"] - 5.0, "CCG": g["VCG"] - 3.0,
                                             "CXCL": g["VL"] - g["VN"] - g["VB"] - 1.5}))
                      for k, reg in regs.items())
            mod = np.interp(M, MACH, c)
            out_rows.append((p, M, exp, err, mod))
    return out_rows


def recalibration_factor(rows, column, curve, grid=np.array([1.2, 1.5, 2.0, 2.5, 3.0])):
    """Fits k(M) in  experiment ≈ k(M) · model, with k quadratic in (M − 2).

    It is the honest way to recalibrate here: with four nearly identical projectiles the
    individual constants (F1..F9) cannot be identified, but the scale factor comes out well
    determined. k = 1 means SPIN-73 gets the family right.
    """
    L = [l for l in rows if l["M"] >= r.MMIN and np.isfinite(l[column])]
    X, Y = [], []
    for l in L:
        mod = np.interp(l["M"], MACH, curve(r.GEO[l["proj"]]))
        if not np.isfinite(mod):
            continue
        X.append(mod * r.mach_basis(l["M"])[0])
        Y.append(l[column])
    X, Y = np.array(X), np.array(Y)
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta
    s2 = res @ res / (len(Y) - 3)
    cov = s2 * np.linalg.pinv(X.T @ X)
    B = r.mach_basis(grid)
    k = B @ beta
    sk = np.sqrt(np.einsum("ij,jk,ik->i", B, cov, B))
    return grid, k, sk, len(Y), np.sqrt(s2)


if __name__ == "__main__":
    rows = table()

    print("=" * 78)
    print("Cmq  (q·d/2V) -- complete model: XF1..XF9 read, long-body term F9")
    print("=" * 78)
    print(f"{'proj':6s} {'n':>3s} {'SPIN-73 bias':>16s} {'exp spread':>14s}")
    for p, n, bias, sd in per_round(rows, "CMQ", cmq_curve):
        mark = "  <-- bias larger than the spread" if abs(bias) > sd else ""
        print(f"{p:6s} {n:3d} {bias:+16.2f} {sd:14.2f}{mark}")
    ep, npairs = r.pure_error(rows, "CMQ", PROJECTILES)
    print(f"\npure error between repeated rounds: {ep:.2f} ({npairs} pairs)")
    print("\nAgainst the experimental curve fitted by least squares:")
    print(f"{'proj':6s} {'Mach':>5s} {'experiment':>13s} {'SPIN-73':>9s} {'diff':>8s}")
    for p, M, exp, err, mod in against_fit(rows, "CMQ", cmq_curve, np.array([1.2, 1.5, 2.0, 2.5])):
        print(f"{p:6s} {M:5.2f} {exp:8.2f}±{err:<4.2f} {mod:9.2f} {mod - exp:+8.2f}")

    print("\n" + "=" * 78)
    print("Center of pressure CPN (calibers from the nose) -- XC15 from Mach 1.2 to 5 decided")
    print("=" * 78)
    available = [f"{m:.2f}" for m, v in zip(MACH, cpn_curve(r.GEO["M-80"])) if np.isfinite(v)]
    print("Mach points covered by the adaptation:", ", ".join(available))
    rounds = {p: [l["M"] for l in rows if l["proj"] == p and l["M"] >= r.MMIN and np.isfinite(l["CPN"])]
              for p in PROJECTILES}
    cel = sorted({c for p in PROJECTILES for c in decided_cells(rounds[p], r.GEO[p]["VB"])},
                 key=lambda t: (t[1], t[0]))
    every = [m for ms in rounds.values() for m in ms]
    print("\nXC cells decided by the model (xc_read) that enter the CPN of the rounds")
    print(f"(Mach {min(every):.2f} to {max(every):.2f}, grid points used in the interpolation):")
    for j in sorted({j for _, j, _ in cel}):
        print(f"  Mach {MACH[j]:4.2f}: " + ", ".join(f"XC{l} ({reg})" for l, jj, reg in cel if jj == j))

    print(f"\n{'proj':6s} {'n':>3s} {'SPIN-73 bias':>16s} {'exp spread':>14s}")
    for p, n, bias, sd in per_round(rows, "CPN", cpn_curve):
        mark = "  <-- bias larger than the spread" if abs(bias) > sd else ""
        print(f"{p:6s} {n:3d} {bias:+16.2f} {sd:14.2f}{mark}")
    ep, npairs = r.pure_error(rows, "CPN", PROJECTILES)
    print(f"\npure error between repeated rounds: {ep:.3f} ({npairs} pairs)")

    # the experimental curve is fitted to the measured CPN, with the reduced model of CNα·CPN
    CPN_MODEL = "MNOSE"
    fit = r.lsq(rows, "CPN", *r.MODELS[CPN_MODEL][:2])
    print("\nAgainst the experimental curve fitted by least squares to the measured CPN (constant + CXLL,")
    print(f"quadratic in M − 2): n = {len(fit['L'])}, rms residual = {fit['s']:.3f}")
    print(f"{'proj':6s} {'Mach':>5s} {'CPN exp':>16s} {'CPN SPIN-73':>12s} {'diff':>7s}")
    for p, M, exp, err, mod in against_fit(rows, "CPN", cpn_curve, np.array([1.2, 1.5, 2.0, 2.5]),
                                           model=CPN_MODEL):
        print(f"{p:6s} {M:5.2f} {exp:11.3f}±{err:<4.3f} {mod:12.3f} {mod - exp:+7.3f}")

    print("\nSensitivity to the assumed ogive radius (M-80, Mach 2.0):")
    for orr in (8.0, 9.74, 12.0):
        v = cpn_curve(r.GEO["M-80"], orr)[12]
        print(f"  OR = {orr:5.2f} cal -> CPN = {v:.3f}")

    print("\n" + "=" * 78)
    print("RECALIBRATION: factor k(M) in  experiment ≈ k(M) · SPIN-73")
    print("=" * 78)
    for column, curve, name, fmt in (("CMQ", cmq_curve, "Cmq", ".2f"), ("CPN", cpn_curve, "CPN", ".3f")):
        grid, k, sk, n, s = recalibration_factor(rows, column, curve)
        print(f"\n{name}: n = {n} rounds, rms residual = {s:{fmt}}")
        print("  Mach:  " + "".join(f"{m:>12.2f}" for m in grid))
        print("  k:     " + "".join(f"{a:7.2f}±{b:<4.2f}" for a, b in zip(k, sk)))

    without_m62 = [l for l in rows if l["proj"] != "M-62"]
    variants = (("OR =  8.00 cal", rows, lambda g: cpn_curve(g, 8.0)),
                ("OR = 12.00 cal", rows, lambda g: cpn_curve(g, 12.0)),
                ("without M-62", without_m62, cpn_curve))
    print("\nk of the CPN with another assumed ogive radius, and without the M-62 (rounded base,")
    print("outside the SPIN-73 model):")
    print(f"  {'Mach:':16s}" + "".join(f"{m:>12.2f}" for m in grid))
    for label, L, curve in variants:
        grid, k, sk, n, s = recalibration_factor(L, "CPN", curve)
        print(f"  {label + ':':16s}" + "".join(f"{a:7.2f}±{b:<4.2f}" for a, b in zip(k, sk)))
    print(f"  without M-62: n = {n} rounds, rms residual = {s:.3f}")

    print("\nThe CPN k uses the CPN measured round by round (VCG − CMα/CNα, experiment only), not")
    print("SPIN-73's CNα. Above Mach 1.1, the model's CPN depends on the XC cells decided by")
    print("the 1973 tables, listed above; none came from free flight.")
