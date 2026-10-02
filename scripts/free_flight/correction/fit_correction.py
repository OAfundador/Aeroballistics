"""Empirical correction of SPIN-73 with free-flight data, validated by leaving one group out.

Form of the correction (one per coefficient and per Mach regime):

    relative  (CX0, CNα, Cmq):   c_corr = c_SPIN · (1 + a + b·f(geo))
    absolute  (CPN, Magnus):     c_corr = c_SPIN + a + b·f(geo)

What the correction may use is decided BEFORE looking at the error: SPIN-73 already models the
geometry (its constants were fitted precisely for that); what it does not have is SCALE. A
155 mm shell and a 5.56 mm bullet of the same shape come out with the same coefficients, but
the Reynolds number is 25 times larger on the shell. So:

  - CX0: skin-friction law with the Reynolds number (reynolds.py), one parameter per regime,
    the reference length L_ref embedded in the SPIN-73 constants;
  - the others: a constant bias (f = none) or one proportional to log d (scale), whichever the
    cross-validation picks, or nothing.

A variant that may also pick geometric attributes (ogive, cylinder, boattail) is in
GEOMETRIC_ATTRIBUTES (validate(..., geometric=True)). It does not improve CMα or the supersonic
CNα (the choice changes with each group left out) and gains little on the supersonic Cmq
(22.8 % → 21.2 %); the procedure adopted, fixed beforehand, is the scale one.

A correction only enters the final model if the nested cross-validation shows that it
generalizes: mean error below SPIN-73's, an improvement in more than half of the groups and no
group with its error more than doubled (see accepted()). CPN is not corrected separately: it
comes from the corrected CMα and CNα (CPN = VCG − CMα/CNα).

Validation: the projectile groups (flight_data.py) are left out one at a time. The CHOICE of
the attribute is also made without the left-out group (nested cross-validation), so the
measured prediction error is that of a projectile the fit has never seen. Each group weighs
the same in the fit and in the metric, so that the 45 rounds of the M101 do not dominate the
16 of the .50.

    python scripts/free_flight/correction/fit_correction.py
        -> results table + src/aeroballistics/corrections/free_flight.json
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                            # noqa: E402,F401

import flight_data                                      # noqa: E402
from aeroballistics.corrections import reynolds as rn           # noqa: E402
from aeroballistics.corrections.free_flight import FILE as JSON_FILE   # noqa: E402

REGIMES = [("subsonic", 0.0, 0.9), ("transonic", 0.9, 1.25), ("supersonic", 1.25, 9.0)]
GROUPS = ["762", "556b", "556t", "50", "m101", "m483", "762m", "30", "t203", "xm617"]
TYPE = {"CX0": "rel", "CNA": "rel", "CMA": "rel", "CMQ": "rel", "CNPA": "abs", "CPN": "abs"}
# Coefficients the correction applies. Not CPN: it comes from the corrected CMα and CNα
# (CPN = VCG − CMα/CNα), so that the three stay consistent; it is only validated, to show what
# happens to it.
APPLIED = ("CX0", "CNA", "CMA", "CMQ", "CNPA")

ATTRIBUTES = {
    "none": None,
    "log d": lambda l: np.log10(l["d_mm"] / 10.0),
}
GEOMETRIC_ATTRIBUTES = {
    "ogive": lambda l: l["geo"]["VN"],
    "cylinder": lambda l: l["geo"]["VL"] - l["geo"]["VN"] - l["geo"]["VB"],
    "boattail": lambda l: l["geo"]["VB"],
}
LREF_GRID = np.logspace(np.log10(0.02), np.log10(1.0), 61)     # m


def regime(M):
    return next(n for n, a, b in REGIMES if a <= M < b)


def target(l, kind):
    return l["meas"] / l["spin"] - 1.0 if kind == "rel" else l["meas"] - l["spin"]


def apply_coef(l, kind, coef):
    """Corrected value of one row with the coefficients (a, b, attribute)."""
    a, b, attr = coef
    if attr == "reynolds":                      # a = L_ref (m); additive correction on CX0
        g = l["geo"]
        return l["spin"] + rn.delta_cx0(l["M"], g["VL"], g["VN"], g["VB"], g["OR"], g["DM"],
                                        l["d_mm"], a)
    tab = {**ATTRIBUTES, **GEOMETRIC_ATTRIBUTES}
    f = tab[attr](l) if tab[attr] else 0.0
    d = a + b * f
    return l["spin"] * (1.0 + d) if kind == "rel" else l["spin"] + d


def fit(L, kind, attr):
    """Weighted least squares: each group weighs 1 in total."""
    if not L:
        return (0.0, 0.0, attr)
    n = {}
    for l in L:
        n[l["group"]] = n.get(l["group"], 0) + 1
    w = np.array([1.0 / n[l["group"]] for l in L])
    if attr == "reynolds":
        e = [np.sum(w * np.square([(l["meas"] - apply_coef(l, kind, (x, 0.0, attr))) / l["spin"] for l in L]))
             for x in LREF_GRID]
        return (float(LREF_GRID[int(np.argmin(e))]), 0.0, "reynolds")
    y = np.array([target(l, kind) for l in L])
    tab = {**ATTRIBUTES, **GEOMETRIC_ATTRIBUTES}
    if tab[attr] is None or len(n) < 3:
        return (float(np.sum(w * y) / np.sum(w)), 0.0, "none")
    X = np.c_[np.ones(len(L)), [tab[attr](l) for l in L]]
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    return (float(beta[0]), float(beta[1]), attr)


def group_error(L, kind, coef=None):
    """RMS of the error (relative or absolute) of a set of rows; coef=None = pure SPIN-73."""
    e = []
    for l in L:
        v = l["spin"] if coef is None else apply_coef(l, kind, coef)
        # relative to SPIN-73 (never zero; the measured Cmq reaches 0.0)
        e.append((l["meas"] - v) / abs(l["spin"]) if kind == "rel" else l["meas"] - v)
    return float(np.sqrt(np.mean(np.square(e)))) if e else np.nan


def logo(L, kind, attr, groups):
    """Mean error (per group) leaving each group out, with the attribute fixed."""
    errs = []
    for g in groups:
        tr = [l for l in L if l["group"] != g]
        te = [l for l in L if l["group"] == g]
        if te and len({l["group"] for l in tr}) >= 2:
            errs.append(group_error(te, kind, fit(tr, kind, attr)))
    return float(np.mean(errs)) if errs else np.inf


def candidates(coef_name, geometric=False):
    if coef_name == "CX0":
        return ["reynolds"]
    return list(ATTRIBUTES) + (list(GEOMETRIC_ATTRIBUTES) if geometric else [])


def choose(L, kind, groups, cand_names):
    """Attribute with the lowest cross-validation error; 'no correction' also competes."""
    base = np.mean([group_error([l for l in L if l["group"] == g], kind) for g in groups
                    if any(l["group"] == g for l in L)])
    cands = {attr: logo(L, kind, attr, groups) for attr in cand_names}
    best = min(cands, key=cands.get)
    return (None, cands) if base <= cands[best] else (best, cands)


def validate(ls, coef_name, geometric=False):
    """Nested cross-validation per regime. Returns {regime: (base, corrected, n groups, detail)}."""
    kind = TYPE[coef_name]
    cn = candidates(coef_name, geometric)
    out = {}
    for reg, a, b in REGIMES:
        L = [l for l in ls if l["coef"] == coef_name and a <= l["M"] < b]
        gs = [g for g in GROUPS if any(l["group"] == g for l in L)]
        base, corr, det = [], [], {}
        for g in gs:
            tr = [l for l in L if l["group"] != g]
            te = [l for l in L if l["group"] == g]
            others = [x for x in gs if x != g]
            attr, _ = choose(tr, kind, others, cn) if len(others) >= 3 else (None, {})
            c = fit(tr, kind, attr) if attr else None
            eb, ec = group_error(te, kind), group_error(te, kind, c)
            base.append(eb); corr.append(ec); det[g] = (eb, ec, attr)
        out[reg] = (float(np.mean(base)) if base else np.nan,
                    float(np.mean(corr)) if corr else np.nan, len(gs), det)
    return out


def accepted(base, corr, det):
    """Acceptance rule: it generalizes to unseen groups.

    (1) mean error below SPIN-73's; (2) improvement in more than half of the groups;
    (3) safety: no left-out group ends up with its error more than doubled.
    Criterion (3) was added after seeing the transonic Cmq, which passed (1) and (2) while
    worsening both 155 mm (M483A1: 35 % -> 126 %). Recorded here for transparency.
    """
    n = len(det)
    improved = sum(1 for eb, ec, _ in det.values() if ec < eb)
    safe = all(ec <= 2.0 * eb for eb, ec, _ in det.values())
    return bool(n >= 4 and corr < base and improved > n / 2 and safe), improved


def final_fit(ls, validation=None):
    """With every group: only (coefficient, regime) pairs accepted by the nested cross-validation;
    the attribute is chosen by cross-validation over all groups and the coefficients fitted on
    all of them. 'worst_ratio' records the margin: the largest corrected error/SPIN-73 error
    among the left-out groups (rule (3) cuts at 2)."""
    validation = validation or {c: validate(ls, c) for c in APPLIED}
    final = {}
    for c in APPLIED:
        kind = TYPE[c]
        final[c] = {}
        for reg, a, b in REGIMES:
            base, corr, n, det = validation[c][reg]
            ok, improved = accepted(base, corr, det) if n else (False, 0)
            L = [l for l in ls if l["coef"] == c and a <= l["M"] < b]
            gs = [g for g in GROUPS if any(l["group"] == g for l in L)]
            attr, cands = choose(L, kind, gs, candidates(c)) if ok else (None, {})
            worst = max((ec / eb for eb, ec, _ in det.values() if eb > 0), default=float("nan"))
            final[c][reg] = dict(type=kind, attribute=attr,
                                 coef=list(fit(L, kind, attr)) if attr else None,
                                 validation=dict(spin73=round(base, 4), corrected=round(corr, 4),
                                                 groups=n, groups_improved=improved, accepted=ok,
                                                 worst_ratio=round(worst, 3)))
    return final


def derived_cpn(ls, final):
    """CPN = VCG − CMα/CNα with the corrections ACCEPTED in the final model, refitted without each group."""
    out = {}
    for reg, a, b in REGIMES:
        base, corr, det = [], [], {}
        for g in GROUPS:
            tr = [l for l in ls if l["group"] != g and a <= l["M"] < b]
            coefs = {}
            for c in ("CNA", "CMA"):
                if final[c][reg]["coef"]:
                    L = [l for l in tr if l["coef"] == c]
                    gs = [x for x in GROUPS if x != g and any(l["group"] == x for l in L)]
                    attr, _ = choose(L, TYPE[c], gs, candidates(c))
                    coefs[c] = fit(L, TYPE[c], attr) if attr else None
            by = {}
            for l in ls:
                if l["group"] == g and a <= l["M"] < b:
                    by.setdefault(round(l["M"], 4), {})[l["coef"]] = l
            eb, ec = [], []
            for d in by.values():
                if "CPN" not in d:
                    continue
                lp = d["CPN"]
                m = flight_data._spin_at_mach(lp["proj"], lp["geo"], lp["M"])
                cna = apply_coef(dict(lp, spin=m["CNA"]), "rel", coefs["CNA"]) if coefs.get("CNA") else m["CNA"]
                cma = apply_coef(dict(lp, spin=m["CMA"]), "rel", coefs["CMA"]) if coefs.get("CMA") else m["CMA"]
                # base derived the same way (interpolated CMα/CNα), so as not to measure an interpolation artifact
                eb.append(lp["meas"] - (lp["geo"]["VCG"] - m["CMA"] / m["CNA"]))
                ec.append(lp["meas"] - (lp["geo"]["VCG"] - cma / cna))
            if eb:
                rb, rc = np.sqrt(np.mean(np.square(eb))), np.sqrt(np.mean(np.square(ec)))
                base.append(rb); corr.append(rc); det[g] = (rb, rc)
        det = {g: (rb, rc if abs(rc - rb) > 1e-9 else rb) for g, (rb, rc) in det.items()}
        out[reg] = (float(np.mean(base)), float(np.mean(corr)), len(det), det)
    return out


def derived_cma(ls, final=None, left_out=None):
    """CMα = (VCG − CPN)·CNα with corrected CPN and CNα, against the measured CMα.
    With left_out=g, the correction is fitted without group g (cross-validation)."""
    by = {}
    for l in ls:
        by.setdefault((l["proj"], round(l["M"], 4)), {})[l["coef"]] = l
    res = {}
    for (proj, M), d in by.items():
        if "CMA" not in d:
            continue
        l = d["CMA"]
        g = l["group"]
        if left_out is not None and g != left_out:
            continue
        reg = regime(M)
        fin = final[g] if isinstance(final, dict) and g in final else final
        cna_l = dict(l, coef="CNA", spin=d["CNA"]["spin"] if "CNA" in d else _spin(l, "CNA"))
        cpn_l = dict(l, coef="CPN", spin=d["CPN"]["spin"] if "CPN" in d else _spin(l, "CPN"))
        cna, cpn = cna_l["spin"], cpn_l["spin"]
        if fin:
            fc, fp = fin["CNA"][reg], fin["CPN"][reg]
            if fc["coef"]:
                cna = apply_coef(cna_l, "rel", tuple(fc["coef"]))
            if fp["coef"]:
                cpn = apply_coef(cpn_l, "abs", tuple(fp["coef"]))
        cma = (l["geo"]["VCG"] - cpn) * cna
        res.setdefault((g, reg), []).append(((l["meas"] - l["spin"]) / abs(l["meas"]),
                                             (l["meas"] - cma) / abs(l["meas"])))
    return res


def _spin(l, c):
    m = flight_data._spin_at_mach(l["proj"], l["geo"], l["M"])
    return {"CNA": m["CNA"], "CPN": m["CPN"]}[c]


def main():
    ls = flight_data.rows()
    print("Empirical correction of SPIN-73 — leave-one-group-out cross-validation (nested)")
    print("Error = RMS per group, mean over groups; relative to SPIN-73 (%) for CX0, CNα, CMα, Cmq;")
    print("absolute for Magnus (pd/2V) and CPN (cal). 'corrected' = prediction for the left-out")
    print("group, with attribute and coefficients fitted on the other groups only. 'worst' = largest")
    print("corrected/SPIN-73 ratio among the left-out groups (the rule rejects above 2).\n")
    val = {}
    for c, kind in TYPE.items():
        val[c] = validate(ls, c)
        scale = 100.0 if kind == "rel" else 1.0
        un = "%" if kind == "rel" else ("cal" if c == "CPN" else "")
        for reg, (b, cc, n, det) in val[c].items():
            if n == 0:
                continue
            ok, improved = accepted(b, cc, det)
            worst = max(ec / eb for eb, ec, _ in det.values() if eb > 0)
            mark = ("ACCEPTED" if ok else "rejected") if c in APPLIED else "(direct correction, not used)"
            print(f"{c:5s} {reg:12s} groups {n}  SPIN-73 {b * scale:7.2f}{un:3s} corrected {cc * scale:7.2f}{un:3s}"
                  f"  improves in {improved}/{n}  worst {worst:4.2f}  {mark}")
    final = final_fit(ls, {c: val[c] for c in APPLIED})
    print("\nDerived CPN (VCG − CMα/CNα, with the accepted corrections redone without the left-out group):")
    for reg, (b, cc, n, det) in derived_cpn(ls, final).items():
        print(f"CPN   {reg:12s} groups {n}  SPIN-73 {b:7.3f}cal corrected {cc:7.3f}cal  improves in "
              f"{sum(1 for eb, ec in det.values() if ec < eb)}/{n}")
    # the result goes to the library, which applies it (aeroballistics.corrections.FreeFlight)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=1)
    print("\nFinal model (all groups), applied by aeroballistics.Aerodynamics(..., corrections='free_flight'):")
    for c, regs in final.items():
        for reg, d in regs.items():
            if d["coef"]:
                a, b, attr = d["coef"]
                if attr == "reynolds":
                    print(f"  {c:5s} {reg:12s} skin friction, L_ref = {a:.3f} m")
                else:
                    print(f"  {c:5s} {reg:12s} {d['type']}: a = {a:+.4f}" + (f", b = {b:+.4f} · {attr}" if attr != "none" else ""))
            else:
                print(f"  {c:5s} {reg:12s} no correction")
    return val, final


if __name__ == "__main__":
    main()
