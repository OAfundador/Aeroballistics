"""Reconstructed SPIN-73 against free-flight data from other sources (benchmarks).

Each benchmark is a CSV with the SOURCE's conventions in the header. Here the data are
brought to the SPIN-73 normalization (spin73/conventions.py) and the program runs at each
round's Mach (linear interpolation on the 17-point grid). This measures SPIN-73 against
reality, not the reconstruction against SPIN-73 (that is in docs/VERIFICATION.md).

    python scripts/free_flight/benchmarks/compare.py
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                          # noqa: E402

import spin73 as s                                    # noqa: E402

DATA = paths.FREE_FLIGHT

# Mach ranges for the summary
RANGES = [("subsonic", 0.0, 0.9), ("transonic", 0.9, 1.2), ("supersonic", 1.2, 9.0)]


def read(path):
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    doubt = set()
    with open(path, encoding="utf-8") as f:
        for l in f:
            if l.startswith("# doubtful:"):
                rd, col = l.split(":", 1)[1].split()[:2]
                doubt.add((rd, col))
    rows = list(csv.DictReader(lines))
    for r in rows:
        for c in list(r):
            if c not in ("RD", "PROJECTILE"):
                r[c] = float(r[c]) if r[c].strip() else np.nan
        for (rd, col) in doubt:
            if r["RD"] == rd and col in r:
                r[col] = np.nan
    return rows


def model_at_mach(t, M):
    return {c: float(np.interp(M, s.MACH_GRID, v)) for c, v in t.items() if c != "MACH"}


def compare(name, rows, p, conv):
    """conv: source column -> (SPIN-73 column, factor that brings the source to SPIN-73)."""
    t = s.table(p)
    res = {}
    for r in rows:
        m = model_at_mach(t, r["MACH"])
        d2 = r.get("D2", np.nan)
        if not np.isfinite(d2) and np.isfinite(r.get("AT", np.nan)):
            d2 = r["AT"] ** 2                      # the round's total angle of attack, degrees
        sin2 = np.sin(np.radians(np.sqrt(d2))) ** 2 if np.isfinite(d2) else 0.0
        calc = dict(CD=m["CX"] + (m["CX2"] + m["CNA"]) * sin2, CX0=m["CX"], CMA=m["CMA"],
                    CNA=m["CNA"], CMQ=m["CMQ"], CMPA=m["CNPA"], CNPA=m["CNPA"], CPN=m["CPN"],
                    CLP=m["CLP"], CLA=m["CNA"] - m["CX"], CPN_BASE=p.VL - m["CPN"])
        for col, (target, factor) in conv.items():
            v = r.get(col, np.nan)
            if np.isfinite(v):
                res.setdefault(col, []).append((r["MACH"], v * factor, calc[target]))
    print(f"\n{name}")
    print(f"{'coef':6s} {'range':12s} {'n':>3s} {'measured':>9s} {'SPIN-73':>9s} {'SPIN/meas':>9s} {'meas. sd':>10s}")
    out = []
    for col, pts in res.items():
        a = np.array(pts)
        for rng, lo, hi in RANGES:
            k = (a[:, 0] >= lo) & (a[:, 0] < hi)
            if k.sum() == 0:
                continue
            meas, mod = a[k, 1], a[k, 2]
            ratio = np.mean(mod) / np.mean(meas) if abs(np.mean(meas)) > 1e-9 else np.nan
            sd = np.std(meas, ddof=1) if k.sum() > 1 else np.nan
            print(f"{col:6s} {rng:12s} {k.sum():3d} {np.mean(meas):9.3f} {np.mean(mod):9.3f} "
                  f"{ratio:9.2f} {sd:10.3f}")
            out.append((col, rng, int(k.sum()), np.mean(meas), np.mean(mod), ratio, sd))
    return out


# --------------------------------------------------------------------------- benchmarks
def m101():
    # Input as SPIN-73 itself ran the M101 (p. 59), with the CG from Karpov's Table I.
    p = s.Projectile(VL=4.51, VN=2.45, VB=0.45, VCG=2.96, DM=0.098, BD=1.026, OR=10.75,
                     name="155 mm M101")
    rows = read(DATA / "m101_karpov1964.csv")
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CNA": ("CNA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0)}      # qd/V and pd/V -> x2
    return compare("155 mm M101 — Karpov 1964 (BRL MR 1582), full-scale prototype", rows, p, conv)


def m483a1():
    # Composite ogive: VN as the sum of the three pieces; OR from the main arc (57.77 in).
    p = s.Projectile(VL=5.80, VN=2.844, VB=0.255, VCG=3.64, DM=0.098, BD=1.018, OR=9.48,
                     name="155 mm M483A1")
    rows = read(DATA / "m483a1_whyte1991.csv")
    conv = {c: (c, 1.0) for c in ("CX0", "CNA", "CMA", "CMQ", "CNPA", "CLP")}  # same convention
    return compare("155 mm M483A1 — Whyte 1991 (BRL-CR-659), 65 shots in 19 groups", rows, p, conv)


def m33():
    p = s.Projectile(VL=4.46, VN=2.56, VB=0.78, VCG=4.46 - 1.78, DM=0.18, BD=1.00, OR=8.77,
                     name=".50 Ball M33")
    rows = read(DATA / "m33_mccoy1990.csv")
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
    return compare(".50 Ball M33 — McCoy 1990 (BRL-MR-3810)", rows, p, conv)


NATO556 = {  # geometry from Figs. 2-3 and Table 1 of McCoy 1985 (CG from the base -> from the nose)
    "SS-109": dict(VL=4.07, VN=2.00, VB=0.45, VCG=4.07 - 1.52, OR=8.4),
    "M855": dict(VL=4.05, VN=1.90, VB=0.40, VCG=4.05 - 1.54, OR=7.9),
    "L110": dict(VL=5.13, VN=2.14, VB=0.26, VCG=5.13 - 2.52, OR=8.4),
    "M856": dict(VL=5.18, VN=2.00, VB=0.37, VCG=5.18 - 2.57, OR=9.7),
}


def nato556():
    every = read(DATA / "nato556_mccoy1985.csv")
    out = []
    for name, g in NATO556.items():
        p = s.Projectile(DM=0.12, BD=1.00, name=name, **g)
        rows = [r for r in every if r["PROJECTILE"] == name]
        conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
                "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
        out.append(compare(f"5.56 NATO {name} — McCoy 1985 (BRL-MR-3476)", rows, p, conv))
    return out


MCCOY = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CLA": ("CLA", 1.0),
         "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}


def _by_projectile(file, geos, title):
    """McCoy-format CSV with several projectiles; geometry from correction/flight_data.py (source in the CSV)."""
    every = read(DATA / file)
    out = []
    for name, g in geos.items():
        rows = [r for r in every if r["PROJECTILE"] == name]
        if rows:
            out.append(compare(f"{name} — {title}", rows, s.Projectile(name=name, **g), MCCOY))
    return out


def _geo(*names):
    import flight_data
    return {n: flight_data.GEO[n] for n in names}


def match762():
    return _by_projectile("match762_mccoy1988.csv", _geo("M118", "190 Sierra", "168 Sierra"),
                          "McCoy 1988 (BRL-MR-3733), 7.62 match")


def x30():
    return (_by_projectile("xm788_mccoy1980.csv", _geo("XM788"), "McCoy 1980 (ARBRL-MR-03019), 30 mm")
            + _by_projectile("x30mm_mccoy1982.csv", _geo("XM788E1", "XM789", "XM789 potted"),
                             "McCoy 1982 (ARBRL-TR-03432), 30 mm"))


def t203():
    # OR, DM and BD not dimensioned: those of the M437 (see correction/flight_data.py). CMα and CPN are sensitive to that.
    every = read(DATA / "t203_karpov1955.csv")
    rows = [r for r in every if r["PROJECTILE"] == "T203 8BT"]
    p = s.Projectile(name="T203 8BT", **_geo("T203 8BT")["T203 8BT"])
    k = 8 / np.pi                                        # BRL K notation -> C
    conv = {"KD": ("CD", k), "KN": ("CNA", k), "KM": ("CMA", k), "KH": ("CMQ", -2 * k)}
    return compare("175 mm T203 8° B.T., 90 mm model — Karpov 1955 (BRL MR 956)", rows, p, conv)


def xm617():
    # CG of the sketch (1.066 from the base); the source closes CPN − CMα/CNα with 1.088 (see the CSV)
    rows = read(DATA / "xm617_brandon1969.csv")
    p = s.Projectile(name="XM617", **_geo("XM617")["XM617"])
    conv = {"CD": ("CD", 1.0), "CMA": ("CMA", 1.0), "CNA": ("CNA", 1.0),
            "CMQ": ("CMQ", 2.0), "CMPA": ("CMPA", 2.0), "CPN": ("CPN_BASE", 1.0)}
    return compare("152 mm XM617, cone-cylinder — Brandon 1969 (BRL MR 1998)", rows, p, conv)


if __name__ == "__main__":
    m101()
    m483a1()
    m33()
    nato556()
    match762()
    x30()
    t203()
    xm617()
