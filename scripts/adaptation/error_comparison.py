"""
Every case of the report: the adapted program runs with the printed input of each 1973
table and each legible output is compared with the printed one.

Cases: the 175 mm M437 (m437_table.csv, with stability) and the other complete tables, one
per page, all in data/tables_1973/. Illegible inputs in the header were each decided by a
column declared in the CSV; that column becomes circular in that case.

The error of each cell is measured in UNITS OF THE LAST PRINTED PLACE: in a 3-place column,
1 unit = 0.001. Since the original program rounded to that place, up to ±0.5 unit the model is
indistinguishable from it; the project's criterion is ±1.5 units.

Kept out of the statistics (but in each case's CSV, with the reason):
  - circular: some DATA value or input was decided using this cell (circularity.py);
  - identity: a cell ambiguous in the scan, disambiguated by an identity between printed
    columns (in the M437, the three cells the transcription marked as ambiguous).

    python scripts/adaptation/error_comparison.py
      -> output/verification/cases/pNN_*.csv          each case, cell by cell
      -> output/verification/summary_by_case.csv      one line per case
      -> output/verification/error_summary.csv        one line per column
      -> output/verification/errors_by_cell.csv       every cell

The summary printed on screen is the one in docs/VERIFICATION.md.
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths                                                # noqa: E402

import circularity                                          # noqa: E402
import aeroballistics as s                                          # noqa: E402
import printed_tables as pt                                 # noqa: E402
import test_full_model as tm                                # noqa: E402

OUT = paths.OUTPUT / "verification"

MACH = [round(float(m), 2) for m in s.MACH_GRID]
PLACES = {"SPIN": 1, "W1": 2, "W2": 2, "DELT": 4, **{c: 6 for c in ("L1", "L2", "L15", "L25")}}
ORDER = ["CX", "CX2", "CNA", "CPN", "CMA", "CYPA", "CNPA", "CPF1", "CPF5", "CNPA5", "CNPA3",
         "CNPA5P", "CMQ", "CLP", "GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2",
         "L1", "L2", "L15", "L25", "DELT", "DISP"]


def cases():
    """(page, name, decided inputs, computed table, printed columns, circular, identity)."""
    circ437 = {**{k: "decided with this table (test_full_model.CIRCULAR)"
                  for k in tm.CIRCULAR}, **circularity.circular(65)}
    # cells the old transcription marked as ambiguous in the scan (not a model error)
    amb437 = {k: v for k, v in tm.PENDING.items() if "printed cell" in v}
    out = [(65, "175 mm M437", {}, s.table(s.M437), tm.TAB, circ437, amb437)]
    for tb in pt.all_tables():
        out.append((tb.page, tb.name, tb.decided(), s.table(tb.projectile()), tb.columns,
                    circularity.circular(tb.page, tb), tb.identity))
    return sorted(out, key=lambda c: c[0])


def cells(case):
    page, name, _, calc, printed, circ, ident = case
    for col in ORDER:
        if col not in printed or col not in calc:
            continue
        for j, M in enumerate(MACH):
            v = printed[col][j]
            if not np.isfinite(v):
                continue
            places = PLACES.get(col, 3)
            m = float(calc[col][j])
            un = abs(m - v) * 10 ** places if np.isfinite(m) else np.inf
            if (col, M) in ident:
                st = "identity"
            elif (col, M) in circ:
                st = "circular"
            else:
                st = "independent"
            yield dict(page=page, case=name, column=col, mach=M, printed=float(v),
                       model=round(m, 7), error_in_units=round(un, 2), status=st,
                       reason=circ.get((col, M), "") if st == "circular" else "")


def stats(u):
    u = np.asarray(u, float)
    if not u.size:
        return dict(n=0, upto_05=np.nan, upto_15=np.nan, median=np.nan, maximum=np.nan)
    return dict(n=u.size, upto_05=100 * np.mean(u <= 0.5), upto_15=100 * np.mean(u <= 1.5),
                median=float(np.median(u)), maximum=float(u.max()))


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    (OUT / "cases").mkdir(parents=True, exist_ok=True)
    every, by_case = [], []
    fields = ["page", "case", "column", "mach", "printed", "model", "error_in_units",
              "status", "reason"]
    for case in cases():
        cel = list(cells(case))
        every += cel
        page, name, decided = case[:3]
        with open(OUT / "cases" / f"p{page:02d}_{_slug(name)}.csv", "w", newline="",
                  encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(cel)
        ind = [c["error_in_units"] for c in cel if c["status"] == "independent"]
        e = stats(ind)
        worst = max((c for c in cel if c["status"] == "independent"),
                    key=lambda c: c["error_in_units"], default=None)
        by_case.append(dict(
            page=page, case=name, legible_cells=len(cel), independent=e["n"],
            circular=sum(c["status"] == "circular" for c in cel),
            by_identity=sum(c["status"] == "identity" for c in cel),
            pct_upto_05=round(e["upto_05"], 1), pct_upto_15=round(e["upto_15"], 1),
            median_units=round(e["median"], 2),
            worst=(f"{worst['column']} Mach {worst['mach']:g}: printed {worst['printed']:.{PLACES.get(worst['column'], 3)}f}, "
                   f"model {worst['model']:.{PLACES.get(worst['column'], 3) + 1}f}" if worst else ""),
            decided_inputs=" ".join(f"{k}={v:g}" for k, v in decided.items() if "#" not in k)))

    with open(OUT / "errors_by_cell.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(every)
    with open(OUT / "summary_by_case.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(by_case[0]))
        w.writeheader()
        w.writerows(by_case)

    ind = [c for c in every if c["status"] == "independent"]
    e = stats([c["error_in_units"] for c in ind])
    no_m1 = stats([c["error_in_units"] for c in ind if c["page"] != 44])
    print(f"{len(by_case)} cases, {len(every)} legible cells: {len(ind)} independent, "
          f"{sum(c['status'] == 'circular' for c in every)} circular, "
          f"{sum(c['status'] == 'identity' for c in every)} disambiguated by identity")
    print(f"Independent: {e['upto_05']:.0f} % indistinguishable from the original (±0.5 unit), "
          f"{e['upto_15']:.0f} % within the criterion (±1.5), median {e['median']:.2f} unit")
    print(f"Without the M1 (pp. 44/47, header geometry does not close): {no_m1['n']} cells, "
          f"{no_m1['upto_05']:.0f} % / {no_m1['upto_15']:.0f} %, median {no_m1['median']:.2f}\n")

    print(f"{'p.':>3s} {'case':24s} {'legib.':>6s} {'indep.':>6s} {'<=0.5':>6s} {'<=1.5':>6s} "
          f"{'median':>7s}  worst independent cell")
    for r in by_case:
        print(f"{r['page']:3d} {r['case'][:24]:24s} {r['legible_cells']:6d} {r['independent']:6d} "
              f"{r['pct_upto_05']:5.0f}% {r['pct_upto_15']:5.0f}% {r['median_units']:7.2f}  {r['worst']}")

    print(f"\n{'column':8s} {'cases':>5s} {'cells':>7s} {'<=0.5':>6s} {'<=1.5':>6s} {'median':>8s}")
    summary = []
    for col in ORDER:
        c = [x for x in ind if x["column"] == col and x["page"] != 44]
        if not c:
            continue
        e = stats([x["error_in_units"] for x in c])
        ncases = len({x["page"] for x in c})
        summary.append((col, ncases, e))
        print(f"{col:8s} {ncases:5d} {e['n']:7d} {e['upto_05']:5.0f}% {e['upto_15']:5.0f}% {e['median']:8.2f}")
    with open(OUT / "error_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["column", "cases", "independent_cells", "pct_upto_0.5_unit",
                    "pct_upto_1.5_unit", "median_units", "max_units"])
        for col, n, e in summary:
            w.writerow([col, n, e["n"], round(e["upto_05"], 1), round(e["upto_15"], 1),
                        round(e["median"], 2), round(e["maximum"], 1)])


if __name__ == "__main__":
    main()
