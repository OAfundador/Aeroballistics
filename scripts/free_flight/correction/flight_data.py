"""Common base of free-flight data, in the SPIN-73 convention, for the empirical correction.

Gathers the spark-range sources already transcribed and converts each coefficient to the
SPIN-73 normalization (spin73/conventions.py): pd/2V and qd/2V, CNα (not CLα), CPN in calibers
from the NOSE, CX0 at zero yaw. Each row also carries the value of the reconstructed SPIN-73
at the same Mach, with the source's geometry.

Groups (the unit of the cross-validation: near-identical projectiles stay together, so that
one does not "validate" the other):
    762   7.62 NATO, M-80/M-59/M-61/M-62       BRL MR 1833 (Piddington 1967)
    556b  5.56 NATO Ball, SS-109/M855          BRL-MR-3476 (McCoy 1985)
    556t  5.56 NATO Tracer, L110/M856          same
    50    .50 Ball M33                          BRL-MR-3810 (McCoy 1990)
    m101  155 mm M101                           BRL MR 1582 (Karpov 1964)
    m483  155 mm M483A1                         BRL-CR-659 (Whyte 1991)
    762m  7.62 match, M118/190 Sierra/168 Sierra  BRL-MR-3733 (McCoy 1988)
    30    30 mm XM788, XM788E1 (TP), XM789      ARBRL-MR-03019 (McCoy 1980), ARBRL-TR-03432 (1982)
    t203  175 mm T203, 90 mm model (CX0 only)   BRL MR 956 (Karpov 1955)
    xm617 152 mm XM617, cone-cylinder           BRL MR 1998 (Brandon 1969)

    rows() -> list of dicts: group, proj, geo (Projectile), M, coef, meas, spin
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                            # noqa: E402

import spin73 as s                                      # noqa: E402

DATA = paths.FREE_FLIGHT

COEFS = ("CX0", "CNA", "CPN", "CMA", "CMQ", "CNPA")


def _f(x):
    return float(x) if x not in ("", None) and str(x).strip() else np.nan


def _csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def _doubtful(path):
    out = set()
    with open(path, encoding="utf-8") as f:
        for l in f:
            if l.startswith("# doubtful:"):
                rd, col = l.split(":", 1)[1].split()[:2]
                out.add((rd, col))
    return out


# Geometry of each projectile (SPIN-73 inputs). Sources in the CSV headers.
# DM and BD not dimensioned in the small-arms sources: DM = 0.12 and BD = 1.00 (no band).
GEO = {
    "SS-109": dict(VL=4.07, VN=2.00, VB=0.45, VCG=4.07 - 1.52, DM=0.12, BD=1.00, OR=8.4),
    "M855": dict(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, DM=0.12, BD=1.00, OR=7.9),
    "L110": dict(VL=5.13, VN=2.14, VB=0.26, VCG=5.13 - 2.52, DM=0.12, BD=1.00, OR=8.4),
    "M856": dict(VL=5.18, VN=2.00, VB=0.37, VCG=5.18 - 2.57, DM=0.12, BD=1.00, OR=9.7),
    ".50 M33": dict(VL=4.46, VN=2.56, VB=0.78, VCG=4.46 - 1.78, DM=0.18, BD=1.00, OR=8.77),
    "M101": dict(VL=4.51, VN=2.45, VB=0.45, VCG=2.96, DM=0.098, BD=1.026, OR=10.75),
    "M483A1": dict(VL=5.80, VN=2.844, VB=0.255, VCG=3.64, DM=0.098, BD=1.018, OR=9.48),
    # 7.62 match (McCoy 1988): meplat dimensioned in the sketches
    "M118": dict(VL=4.19, VN=2.16, VB=0.74, VCG=4.19 - 1.80, DM=0.18, BD=1.00, OR=7.00),
    "190 Sierra": dict(VL=4.31, VN=2.09, VB=0.69, VCG=4.31 - 1.81, DM=0.21, BD=1.00, OR=8.80),
    "168 Sierra": dict(VL=3.98, VN=2.26, VB=0.51, VCG=3.98 - 1.54, DM=0.25, BD=1.00, OR=7.00),
    # 30 mm (McCoy 1982): 17° conical tip + ogive R 4.30, rounded base (VB = 0).
    # Bands not dimensioned: BD = 1.02 (listing default), decided.
    "XM788E1": dict(VL=3.61, VN=1.85, VB=0.0, VCG=3.61 - 1.35, DM=0.26, BD=1.02, OR=4.30),
    "XM789": dict(VL=3.61, VN=1.85, VB=0.0, VCG=3.61 - 1.40, DM=0.26, BD=1.02, OR=4.30),
    "XM789 potted": dict(VL=3.61, VN=1.85, VB=0.0, VCG=3.61 - 1.41, DM=0.26, BD=1.02, OR=4.30),
    "XM788": dict(VL=3.49, VN=1.84, VB=0.0, VCG=3.49 - 1.25, DM=0.26, BD=1.02, OR=4.30),
    # T203 (Karpov 1955), 90 mm model: L, ogive and boattail dimensioned; OR, DM and BD NOT,
    # taken from the 175 mm M437 card in SPIN-73 (p. 65), which has the same three dimensions (decided).
    # OR changes the SPIN-73 CMα by up to 20 % for this shape, but CX0 by ≤ 2 %: only CX0 is used.
    "T203 8BT": dict(VL=5.51, VN=2.91, VB=1.00, VCG=5.51 - 1.940, DM=0.079, BD=1.05, OR=25.0),
    # XM617: cone-cylinder; OR = 1000 is how SPIN-73 describes a conical ogive (the p. 41 case)
    "XM617": dict(VL=3.151, VN=1.873, VB=0.0, VCG=3.151 - 1.066, DM=0.009, BD=1.019, OR=1000.0),
}
# Reference diameter, mm: gives the scale (Reynolds number per caliber ∝ d, at the same Mach),
# which SPIN-73 has no aerodynamic input for.
DIAM_MM = {"SS-109": 5.69, "M855": 5.69, "L110": 5.69, "M856": 5.69, ".50 M33": 12.95,
           "M101": 155.0, "M483A1": 154.74, "M-80": 7.82, "M-59": 7.82, "M-61": 7.82, "M-62": 7.82,
           "M118": 7.82, "190 Sierra": 7.82, "168 Sierra": 7.82,
           "XM788E1": 29.92, "XM789": 29.92, "XM789 potted": 29.92, "XM788": 29.92,
           "T203 8BT": 90.0, "XM617": 152.0}
# CDδ² from the sources (per sin² of the yaw): (supersonic, subsonic)
CDD2 = {"SS-109": (7.0, 9.8), "M855": (7.0, 9.8), "L110": (5.7, 6.4), "M856": (5.7, 6.4),
        "XM617": (6.57, 6.57)}          # XM617: mean constant, "insufficient data" for the variation
# CDδ² read from a PLOT of the source: points (Mach, CDδ²), linear interpolation, constant outside.
#   7.62 match: Figs. 21-23 of McCoy 1988 (points of the Mach groups; 0.9-0.95 marks the end of
#   the flat subsonic stretch of the curve); 30 mm: Fig. 17 of McCoy 1982 (lines, dashed from 1.0 to 1.2).
CDD2_CURVE = {
    "M118": [(0.80, 3.1), (1.10, 5.3), (1.40, 6.7), (1.80, 6.6), (2.20, 6.2)],
    "190 Sierra": [(0.70, 2.5), (0.90, 2.5), (1.10, 6.5), (1.40, 7.5), (1.80, 5.3), (2.20, 2.8)],
    "168 Sierra": [(0.78, 2.9), (0.95, 2.9), (1.12, 4.2), (1.40, 7.6), (1.80, 6.8), (2.20, 5.5)],
    "XM788E1": [(1.0, 10.0), (1.2, 14.0)],
    "XM789": [(1.0, 5.5), (1.2, 10.5)],
    "XM789 potted": [(1.0, 5.5), (1.2, 10.5)],
    "XM788": [(0.9, 7.9), (1.3, 12.2)],                  # Fig. 12 of McCoy 1980
}
# Rounds with too much yaw for a linear coefficient (round 13931 of the 7.62 match flew at
# 18°, with CMα 18 % below the small-yaw one) are left out of the new sources. The limit lets
# through every round of the old sources (5.56: up to 10.04°).
MAX_YAW = 10.5
# With CDδ² read from a plot (or given only as a mean), CX0 is taken only from rounds with small
# yaw, where the yaw correction is small next to its uncertainty.
MAX_YAW_CX0_PLOT = 5.0


class _Cache:
    tabs = {}

    @classmethod
    def spin(cls, name, geo):
        if name not in cls.tabs:
            cls.tabs[name] = s.table(s.Projectile(name=name, **geo))
        return cls.tabs[name]


def _spin_at_mach(name, geo, M):
    t = _Cache.spin(name, geo)
    return {c: float(np.interp(M, s.MACH_GRID, v)) for c, v in t.items() if c != "MACH"}


def _yaw_drag(name, geo, M, sin2):
    """CDδ²·sin²α: from the source when it gives it; otherwise SPIN-73's own (CX2 + CNα)."""
    if name in CDD2:
        sup, sub = CDD2[name]
        return (sup if M >= 1.0 else sub) * sin2
    if name in CDD2_CURVE:
        Mk, v = zip(*CDD2_CURVE[name])
        return float(np.interp(M, Mk, v)) * sin2
    m = _spin_at_mach(name, geo, M)
    return (m["CX2"] + m["CNA"]) * sin2


def _add(out, group, name, geo, M, **vals):
    m = _spin_at_mach(name, geo, M)
    spin = dict(CX0=m["CX"], CNA=m["CNA"], CPN=m["CPN"], CMA=m["CMA"], CMQ=m["CMQ"],
                CNPA=m["CNPA"])
    for c, v in vals.items():
        if np.isfinite(v):
            out.append(dict(group=group, proj=name, geo=geo, d_mm=DIAM_MM[name], M=M, coef=c,
                            meas=float(v), spin=spin[c]))


# --------------------------------------------------------------------------- sources
def _nato556(out):
    path = DATA / "nato556_mccoy1985.csv"
    doubt = _doubtful(path)
    for r in _csv(path):
        name = r["PROJECTILE"]
        geo = GEO[name]
        group = "556b" if name in ("SS-109", "M855") else "556t"
        M, at = _f(r["MACH"]), _f(r["AT"])
        cd = _f(r["CD"])
        cma = np.nan if (r["RD"], "CMA") in doubt else _f(r["CMA"])
        sin2 = np.sin(np.radians(at)) ** 2
        cna = _f(r["CLA"]) + cd
        cpn = geo["VL"] - _f(r["CPN"])
        _add(out, group, name, geo, M, CX0=cd - _yaw_drag(name, geo, M, sin2), CNA=cna, CPN=cpn,
             CMA=cma, CMQ=2 * _f(r["CMQ"]), CNPA=2 * _f(r["CMPA"]))


def _m33(out):
    name, geo = ".50 M33", GEO[".50 M33"]
    for r in _csv(DATA / "m33_mccoy1990.csv"):
        M, at, cd = _f(r["MACH"]), _f(r["AT"]), _f(r["CD"])
        sin2 = np.sin(np.radians(at)) ** 2
        _add(out, "50", name, geo, M, CX0=cd - _yaw_drag(name, geo, M, sin2),
             CNA=_f(r["CLA"]) + cd, CPN=geo["VL"] - _f(r["CPN"]), CMA=_f(r["CMA"]),
             CMQ=2 * _f(r["CMQ"]), CNPA=2 * _f(r["CMPA"]))


def _m101(out):
    name, geo = "M101", GEO["M101"]
    path = DATA / "m101_karpov1964.csv"
    doubt = _doubtful(path)
    for r in _csv(path):
        M, d2 = _f(r["MACH"]), _f(r["D2"])
        cd, cna, cma = _f(r["CD"]), _f(r["CNA"]), _f(r["CMA"])
        cmq = np.nan if (r["RD"], "CMQ") in doubt else _f(r["CMQ"])
        # CD of rounds with no measured yaw only enters if CD0 does not depend on it: out
        cx0 = cd - _yaw_drag(name, geo, M, np.sin(np.radians(np.sqrt(d2))) ** 2) if np.isfinite(d2) else np.nan
        cpn = geo["VCG"] - cma / cna if np.isfinite(cma) and np.isfinite(cna) else np.nan
        _add(out, "m101", name, geo, M, CX0=cx0, CNA=cna, CPN=cpn, CMA=cma,
             CMQ=2 * cmq, CNPA=2 * _f(r["CMPA"]))


def _m483(out):
    name, geo = "M483A1", GEO["M483A1"]
    for r in _csv(DATA / "m483a1_whyte1991.csv"):
        M = _f(r["MACH"])
        cna, cma = _f(r["CNA"]), _f(r["CMA"])
        # the source's CX is already at zero yaw (CX2 fitted separately); same convention as SPIN-73
        _add(out, "m483", name, geo, M, CX0=_f(r["CX0"]), CNA=cna, CPN=geo["VCG"] - cma / cna,
             CMA=cma, CMQ=_f(r["CMQ"]), CNPA=_f(r["CNPA"]))


def _nato762(out):
    import recalibrate_mr1833 as r62
    geo62 = {r["projectile"]: r for r in _csv(DATA / "mr1833_geometry.csv")}
    d_in = 0.308
    for l, r in zip(r62.table(), r62.RAW):
        g = geo62[l["proj"]]
        geo = dict(VL=_f(g["VL"]), VN=_f(g["VN"]), VB=_f(g["VB"]), VCG=_f(g["VCG"]),
                   DM=_f(g["DM"]), BD=_f(g["BD"]), OR=9.74)
        cpn = geo["VL"] - _f(r["CPN_IN"]) / d_in
        _add(out, "762", l["proj"], geo, l["M"], CX0=l["CD0"], CNA=l["CNA"], CPN=cpn,
             CMA=l["CMA"], CMQ=l["CMQ"], CNPA=l["CNPA"])


def _mccoy(out, file, group):
    """CSV in McCoy's format (1982, 1988): CD at the round's yaw, CLα, CMα, Magnus with pd/V,
    Cmq + Cmα̇ with qd/V, CPN from the base. CDδ² from CDD2_CURVE (the source's plot)."""
    path = DATA / file
    doubt = _doubtful(path)
    for r in _csv(path):
        name = r["PROJECTILE"]
        geo = GEO[name]
        v = {c: (np.nan if (r["RD"], c) in doubt else _f(r[c]))
             for c in ("MACH", "AT", "CD", "CMA", "CLA", "CMPA", "CMQ", "CPN")}
        M, at, cd = v["MACH"], v["AT"], v["CD"]
        if not (np.isfinite(M) and np.isfinite(at)) or at > MAX_YAW:
            continue
        sin2 = np.sin(np.radians(at)) ** 2
        cx0 = cd - _yaw_drag(name, geo, M, sin2) if at <= MAX_YAW_CX0_PLOT else np.nan
        _add(out, group, name, geo, M, CX0=cx0, CNA=v["CLA"] + cd, CPN=geo["VL"] - v["CPN"],
             CMA=v["CMA"], CMQ=2 * v["CMQ"], CNPA=2 * v["CMPA"])


def _match762(out):
    _mccoy(out, "match762_mccoy1988.csv", "762m")


def _x30(out):
    _mccoy(out, "xm788_mccoy1980.csv", "30")
    _mccoy(out, "x30mm_mccoy1982.csv", "30")


def _t203(out):
    """Only the CX0 of the boattail model (see GEO). KDδ² from the source: 0.0007/degree² (0.0006
    above 75 degree²); rounds with rms yaw above 5° are left out, because there the yaw correction
    exceeds 15 % of KD and the uncertainty of KDδ² (0.0006 or 0.0007) already weighs."""
    name, geo = "T203 8BT", GEO["T203 8BT"]
    for r in _csv(DATA / "t203_karpov1955.csv"):
        if r["PROJECTILE"] != name:
            continue
        M, d2, kd = _f(r["MACH"]), _f(r["D2"]), _f(r["KD"])
        if np.sqrt(d2) > MAX_YAW_CX0_PLOT:
            continue
        kdd2 = 0.0007 if d2 < 75 else 0.0006
        _add(out, "t203", name, geo, M, CX0=(kd - kdd2 * d2) / (np.pi / 8))


def _xm617(out):
    """Direct CNα (the source gives the normal force); Cmq and Magnus with qd/V and pd/V."""
    name, geo = "XM617", GEO["XM617"]
    for r in _csv(DATA / "xm617_brandon1969.csv"):
        M, at, cd = _f(r["MACH"]), _f(r["AT"]), _f(r["CD"])
        if at > MAX_YAW:
            continue
        sin2 = np.sin(np.radians(at)) ** 2
        cx0 = cd - _yaw_drag(name, geo, M, sin2) if at <= MAX_YAW_CX0_PLOT else np.nan
        _add(out, "xm617", name, geo, M, CX0=cx0, CNA=_f(r["CNA"]), CPN=geo["VL"] - _f(r["CPN"]),
             CMA=_f(r["CMA"]), CMQ=2 * _f(r["CMQ"]), CNPA=2 * _f(r["CMPA"]))


def rows():
    out = []
    for f in (_nato762, _nato556, _m33, _m101, _m483, _match762, _x30, _t203, _xm617):
        f(out)
    return out


def cma_identity(ls=None, tol=0.05):
    """Check of the transcription and of the conventions: CMα ≈ (VCG − CPN)·CNα with the MEASURED
    values of the same round (only where the source gives all three). Returns the rounds that
    violate it."""
    ls = rows() if ls is None else ls
    by = {}
    for l in ls:
        by.setdefault((l["proj"], round(l["M"], 4)), {})[l["coef"]] = l
    bad, n = [], 0
    for (proj, M), d in by.items():
        # m101 and m483: CPN derived right here; xm617: the source closes with the CG 0.022 cal
        # behind the sketch's (see the CSV), which takes 4-7 % off the identity with the sketch CG
        if all(c in d for c in ("CMA", "CPN", "CNA")) and d["CPN"]["group"] not in ("m101", "m483", "xm617"):
            n += 1
            pred = (d["CMA"]["geo"]["VCG"] - d["CPN"]["meas"]) * d["CNA"]["meas"]
            if abs(pred - d["CMA"]["meas"]) > tol * abs(d["CMA"]["meas"]):
                bad.append((proj, M, round(pred, 3), d["CMA"]["meas"]))
    return n, bad


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ls = rows()
    print(f"{len(ls)} measured values")
    for g in sorted({l["group"] for l in ls}):
        print(g, {c: sum(1 for l in ls if l["group"] == g and l["coef"] == c) for c in COEFS})
    n, bad = cma_identity(ls)
    print(f"identity CMα = (VCG − CPN)·CNα: {n} rounds, {len(bad)} off by more than 5 %", bad)
