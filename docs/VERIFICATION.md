# Every case in the report

`python scripts/reconstruction/error_comparison.py` runs the reconstructed program with the **printed input of each 1973 table** and compares each legible output with the printed one. There are 13 cases: every output table in the report (pp. 29 to 68). Pages 44 and 47 of the scan carry the same printout, so they count as a single case.

Outputs, in `output/verification/` (generated, outside Git):

| File | Contents |
|---|---|
| `cases/pNN_*.csv` | one case per file, cell by cell: printed, computed, error and status |
| `summary_by_case.csv` | one line per case |
| `error_summary.csv` | one line per column, with all the cases together |
| `errors_by_cell.csv` | every cell |

The transcriptions are in `data/tables_1973/` (one per page, with the header) and the raw readings, with the ambiguous glyphs marked, in `data/tables_1973/readings/`.

## How each cell is classified

The error is measured in **units of the last printed digit**: in a 3-decimal column, 1 unit = 0.001. Since the original program rounded at that digit, up to ±0.5 unit the result is indistinguishable from it. The project's criterion is ±1.5 units.

- **independent**: goes into the statistics.
- **circular**: some `DATA` value or some header input was decided using this cell (`scripts/reconstruction/circularity.py`). It only shows that the decision is consistent.
- **identity**: the cell was ambiguous in the scan and was disambiguated only by identities between printed columns, such as CMα = (VCG − CPN)·CNα and CNPA = CYPA·(VCG − CPF1). No `DATA` enters that computation, but the cell stays out of the statistics.

**Illegible inputs.** When a header digit cannot be read, the input is decided by a single column, declared in the CSV and within the range the glyph allows. That column becomes circular in that case. If it is a Magnus column, the other six do too, because they are functions of one another. That is why cases like the 20 mm cone-cylinder have few independent cells.

## Result (2026-09-23)

2718 legible cells: 1612 independent, 779 circular, 327 disambiguated by identity.

**Independent: 89 % indistinguishable from the original, 95 % within the criterion, median error of 0.26 unit.** Without the M1, whose header geometry does not close (below): 91 % and 97 %.

| p. | Case | Legible | Independent | ≤ 0.5 u. | ≤ 1.5 u. | Median | Note |
|---|---|---|---|---|---|---|---|
| 29 | 20 mm M56A3 | 209 | 171 | 94 % | 99 % | 0.20 | meplat reread: 0.260 (the old reading, 0.200, left CX out) |
| 32 | 20 mm 5 cal ANSR | 227 | 189 | 85 % | 99 % | 0.25 | |
| 35 | 20 mm 7 cal ANSR | 224 | 153 | 94 % | 99 % | 0.22 | |
| 38 | 20 mm 9 cal ANSR | 234 | 177 | 94 % | 99 % | 0.25 | whole header legible |
| 41 | 20 mm 10 cal cone-cylinder | 143 | 22 | 91 % | 100 % | 0.18 | VCG 6.747, decided by the Magnus identities (header ?.747) |
| 44/47 | M1 | 159 | 60 | 50 % | 50 % | 1.99 | Magnus, Cmq and Clp close; CX, CX2, CNα, CPN and CMα do not |
| 50 | 105 mm XM380E5 | 231 | 217 | 93 % | 98 % | 0.33 | almost nothing circular: the cleanest test |
| 53 | 5"/38 NAVY | 226 | 180 | 95 % | 98 % | 0.33 | closed with card C205 (NOTES, T15) |
| 56 | 5"/54 NAVY | 94 | 22 | 91 % | 96 % | 0.24 | very degraded page |
| 59 | 155 mm M101/107 | 153 | 32 | 78 % | 81 % | 0.32 | CPN and CMα off by 0.007 to 0.018 |
| 62 | 155 mm M549 | 174 | 29 | 83 % | 93 % | 0.32 | ogive reread: 2.99 (not 2.90); ogive radius 18.9 |
| 65 | 175 mm M437 | 473 | 317 | 89 % | 95 % | 0.27 | the only one with stability |
| 68 | 175 mm SRC | 171 | 43 | 77 % | 95 % | 0.39 | 5.5 cal ogive: **first test of XA13–XA15 and XC17** |

Per column, with all the cases together (without the M1):

| Column | Cases | Cells | ≤ 0.5 u. | ≤ 1.5 u. | Median | Comment |
|---|---|---|---|---|---|---|
| CX | 8 | 119 | 87 % | 100 % | 0.26 | |
| CYPA, CNPA, CPF1, CPF5, CNPA5, CNPA3, CNPA5P | 7 | 714 | 97–100 % | 99–100 % | 0.2–0.33 | Magnus |
| CMQ | 4 | 50 | 100 % | 100 % | 0.21 | |
| CLP | 12 | 200 | 100 % | 100 % | 0.24 | |
| CNA | 9 | 86 | 77 % | 91 % | 0.28 | |
| CX2 | 11 | 95 | 72 % | 91 % | 0.35 | subtracts CNα: inherits its error |
| CPN | 10 | 81 | 79 % | 94 % | 0.22 | |
| CMA | 10 | 87 | 52 % | 82 % | 0.49 | = (VCG − CPN)·CNα: amplifies the CNα and CPN errors 2 to 3 times (below) |
| Stability (GYRO … DISP) | 1 | 4–17 each | 25–100 % | 75–100 % | 0.06–1.15 | only the M437 has this block |

**The M1 (pp. 44/47).** The two pages of the scan are the same printout: the title, the header and a stroke crossing the Mach 1.75 row are identical. One of the report's two tables (90 mm M71 or 105 mm M1) is missing from the scan. With the header geometry, Magnus, Cmq and Clp close, which confirms VL, VN, VB and VCG. CX, CX2, CNα, CPN and CMα do not close: CX sits 0.005 above at every Mach and CX2 reaches a 0.23 difference. No single change of OR, DM, BD, VN or VB closes all five columns. The case is recorded, but left out of the conclusion.

**Is the CMα error ours or SPINNER's?** Against the 1973 tables, the error is ours and small (median 0.0005). The printed table is consistent with itself (CMα = (VCG − CPN)·CNα closes within 0.002), and the error of our CMα comes, half and half, from the CNα error (multiplied by the arm VCG − CPN ≈ 2 cal) and from the CPN error (multiplied by CNα ≈ 2.6). In the 65 rows where CNα and CPN are both within the criterion, CMα is also within ±0.004. The largest deviation (supersonic 5"/38) was card C205, which was missing from the reconstruction (NOTES, T15). SPIN-73's own error against reality is another order of magnitude: the report's Table 1 (p. 28) gives a probable error of 0.12 to 0.17 in CMα against experiment.

## Two different questions

This result answers **"does the reconstruction reproduce the 1973 SPIN-73?"**. In the blocks read directly from the code and the DATA, yes, at the level of the printout's rounding, in twelve of the thirteen cases. The weakest point is CMα, which accumulates the errors of CNα and of the center of pressure.

The other question — **"does SPIN-73 get reality right?"** — is in [free_flight/BENCHMARKS.md](free_flight/BENCHMARKS.md) and [free_flight/RECALIBRATION_MR1833.md](free_flight/RECALIBRATION_MR1833.md). Against free flight of the 7.62 NATO family, the 1973 model overestimates Magnus (+0.3 to +0.5 in p·d/2V) and the Cmq damping (2.5 times at Mach 1.2, 10 % at Mach 2 to 2.5), misses the CNα of the shortest projectile (+0.21) and, from Mach 2.0 to 2.5, puts the center of pressure 8 to 13 % behind the measured one. Against Hitchcock's Ball M2 (caliber .30, Mach 2.5), Cmq misses by 3 %; CMα, by 20 % (Mach 2.3, with the assumed meplat). These errors belong to the original model, not to the reconstruction; for the center of pressure and CMα, with the caveat that part of XC above Mach 1.1 (XC15 from Mach 1.2 to 5.0, XC12 at 1.35 and 1.5 and XC1 at 2.5) was decided by the 1973 tables, not read.
