# Experimental data for the recalibration

Recalibration = the same SPINNER/SPIN-73 equations, with the constants refitted to free-flight data.
The result is NOT the original SPIN-73 and stays apart from the reconstruction: scripts in
`scripts/free_flight/` (this page: `mr1833/` and `hitchcock/`), data in `data/free_flight/`.

## Sources (both Distribution A)
- BRL MR 1833 (Piddington 1967, AD815788): 7.62 NATO family, 4 projectiles, 56 rounds.
  - `data/free_flight/mr1833_table2.csv` — Table II, in the report's normalization (not converted).
  - `data/free_flight/mr1833_geometry.csv` — geometry in calibers (SPIN-73 inputs), CG confirmed by identity.
- BRL Report 620 (Hitchcock 1947/52, AD-800 469): compendium of ~100 projectiles. Not extracted yet.

## Normalization conversions
| Quantity | MR 1833 | Hitchcock | SPIN-73 |
|---|---|---|---|
| Magnus | Cmpa, p·d/V | K_S | Cnpa, p·d/(2V) → ×2 |
| Damping | Cmq+Cmα̇, q·d/V | K_H | Cmq, q·d/(2V) → ×2 |
| Overturning moment | CMα | K_M | CMA = (8/π)·K_M |
| Center of pressure | in. from the base | h (cal. from the base) | calibers from the nose |

## First result (`compare_magnus.py`)
The reconstructed SPIN-73 Magnus overestimates that of the 7.62 by +0.3 to +0.5 (p·d/2V units)
in the supersonic range and does not reproduce the sign change below Mach ~1.5. The ordering by
length (M-80 < M-59 ≈ M-61 < M-62) is the same as in the experiment. Changing the
normalization factor (×1) or the sign worsens the agreement, so the bias does not come from the conversion.
The interpolation assumptions (in Mach and in yaw, without E3) are in the script's header.

## Least-squares recalibration on the 7.62 (`recalibrate_mr1833.py`, output in `docs/results/recalibration_mr1833.txt`)

**Identifiability limit.** Evaluated at the four geometries, SPIN-73's full regressor
matrices have rank 3 (CX, 11 constants), 3 (CNα, 9) and 4 (Cmq, 8), with the 3rd/4th
singular value already small. With this family only a REDUCED MODEL per coefficient can be fitted:
family constant + length term, each quadratic in Mach, in the supersonic range
(M ≥ 1.1). SPIN-73's individual constants (a_i, B_i, C_i, F_i) do not come out of this; that
needs the variety of shapes in Hitchcock.

**Quality.** In every fit the residual is of the order of the pure error, estimated from the
repeated rounds: CD0 0.009/0.009; CNα 0.23/0.27; CNα·CPN 0.55/0.63; Cmq 1.5/1.1.
There is no detectable lack of fit; the limit is the experimental noise.

**Recalibrated Magnus.** With E1 fixed at the reconstructed value, the effective E of the 7.62 comes out at
2.2–2.6 (±0.1), against 3.0–3.1 in SPIN-73. It is the bias seen in `compare_magnus.py`,
now quantified in the model's own constant.

**Assumptions to keep in mind.** Continuous piecewise yaw-drag law (the report only gives
the two values); the positive slope of CD0 with length (~5 % between M-80 and M-59)
is sensitive to this assumption, and the report describes the two as practically equal.
Transonic and subsonic (M-80 only) were not fitted.

## CNα against the experiment (`compare_cna.py`)

Output in `docs/results/cna_mr1833.txt`. Round-by-round bias (M ≥ 1.1, OR = 9.74 cal): +0.214 for the M-80, −0.033 for the M-59, −0.062 for the M-61 and −0.116 for the M-62, against an experimental scatter of 0.17 to 0.31 and a pure error of 0.27 between repeated rounds. Only the M-80's exceeds twice the standard error of the mean (pure error/√n = 0.071, 15 rounds). The assumed ogive radius does not weigh: from OR = 8 to 12 cal, the bias changes by at most 0.005. Against the fitted curve, the model gives practically the same CNα to the four projectiles (the M-80 curve sits at most 0.02 above the others between Mach 1.2 and 2.5), while the experiment grows with length: at Mach 2.0, 2.725 for the M-80, 2.98 to 2.99 for the M-59 and the M-61 and 3.178 for the M-62.

The first comparison (`docs/TRANSCRIPTION_NOTES.md`, T5) gave +0.28 for the M-80 (+0.01, −0.01 and −0.08 for the others). It predates card C205 (NOTES, T15), which zeroes the boattail normal force when it comes out positive, which happens for the 7.62 in the supersonic range, with its short ogive. The output repeats the computation without the card and reproduces the old values (+0.276, +0.009, −0.011, −0.082).

## Cmq and center of pressure against the experiment (`compare_cmq_cp.py`)

Now that XF (Cmq, with the undocumented term F9) and XC (center of pressure) have been read, both enter the comparison. Output in `docs/results/cmq_cp_mr1833.txt`.

**Cmq: SPIN-73 damps too much.** The bias against the rounds is −2.2 (M-80) to −4.9 (M-62) in q·d/2V units, always larger than the experimental scatter (1.3 to 2.4) and than the pure error between repeated rounds (1.13). Against the fitted experimental curve, the difference is huge in the transonic range and vanishes in the high supersonic range:

| Mach | 1.2 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|
| k(M) = experiment / SPIN-73 | 0.40 ± 0.04 | 0.66 ± 0.03 | 0.90 ± 0.04 | 0.90 ± 0.03 |

In other words: at Mach 1.2 the model gives a damping 2.5 times larger than measured; at Mach 2 to 2.5 the error falls to 10 %. At Mach 1.2 the experimental curve itself is poorly determined (±4 to 5.5 units), because there are few rounds below 1.3 — the 0.40 factor there should be read with that caveat. The fit is of one scale factor per Mach, quadratic in (M − 2): with four nearly equal projectiles F1..F9 cannot be identified individually (rank 4), but the scale comes out well determined.

**Center of pressure: no round-by-round agreement.** The reconstruction of CPN now exists at all 17 Mach numbers. The continuation card of XC15 was not printed in the report, and the nine missing cells (Mach 1.2 to 5.0) were decided by the model from the 1973 tables, not read (`src/spin73/data/xc_read.py`; `docs/TRANSCRIPTION_NOTES.md`, T6.2 and T13): Mach 1.2, 1.35, 1.5 and 2.0 by the 175 mm M437 and the 5"/38 together (`RECOVERED`); Mach 1.75 and 2.5 to 5.0 by the M437 alone (`DECIDED_M437`; the 105 mm XM380E5, left out of the decision, closes at those Mach numbers, but carries little weight in XC15). In the same range, XC1 at Mach 2.5 (read 1.90, decided 1.99) and XC12 at Mach 1.35 and 1.5 (`CORRECTIONS`) were also decided. None of these values came from free flight, so the comparison is not circular, but the model's CPN above Mach 1.1 depends on them.

The output lists the model-decided XC cells that enter the CPN of the rounds (Mach 1.13 to 2.85): XC15 from Mach 1.2 to 3.0, XC12 at Mach 1.35 and 1.5 and XC1 at Mach 2.5.

Round by round (M ≥ 1.1), the model puts the center of pressure behind the measured one: +0.22 caliber for the M-80, +0.16 for the M-59 and +0.14 for the M-61, larger than the experimental scatter (0.07 to 0.08) and than the pure error between repeated rounds (0.085). For the M-62 the bias is −0.07, the size of the scatter (0.07); the script's "larger than the scatter" flag is decided in the third decimal place. The mean hides the Mach dependence, which the fitted curve and the k(M) factor show.

Against the fitted experimental curve, the measured CPN of each round (VCG − CMα/CNα, measured values only) is fitted directly, with the reduced model of CNα·CPN (constant + CXLL, quadratic in M − 2); the residual (0.084) is at the level of the pure error (0.085). The previous version of the script fitted CNα·CPN and divided by the **model's** CNα: SPIN-73's CNα bias (+0.21 for the M-80) passed to the experimental side, and the uncertainty of the curve, which came from that of CNα·CPN, came out much wider. Model minus curve, in calibers, with the uncertainty of the curve:

| Mach | 1.2 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|
| M-80 | +0.036 ± 0.173 | +0.135 ± 0.089 | +0.180 ± 0.113 | +0.345 ± 0.087 |
| M-59 | −0.103 ± 0.116 | −0.001 ± 0.060 | +0.064 ± 0.076 | +0.239 ± 0.059 |
| M-61 | −0.109 ± 0.113 | −0.007 ± 0.059 | +0.060 ± 0.075 | +0.234 ± 0.058 |
| M-62 | −0.257 ± 0.073 | −0.174 ± 0.039 | −0.082 ± 0.049 | +0.080 ± 0.038 |

The deviation grows with Mach for all four projectiles. From Mach 1.2 to 2.0, the model stays within the uncertainty for the M-59 and the M-61; the M-80 leaves it from Mach 1.5 on. At Mach 2.5, where CPN uses the XC15 decided by the M437 alone and the decided XC1, the M-80, the M-59 and the M-61 sit 0.23 to 0.35 caliber behind. The M-62, with a rounded base (which the SPIN-73 model does not represent), goes from −0.26 at Mach 1.2 to +0.08 at 2.5, outside the uncertainty at every point. The sensitivity to the assumed ogive radius (9.74 cal, uncertain) is −0.06/+0.05 caliber between OR = 8 and 12 (M-80, Mach 2.0).

**CPN k(M) factor.** With the model's CPN over the whole range, k(M) is computed like the Cmq one, on the same 42 rounds, with the measured CPN of each round. (The pair the script used to leave aside, the measured CNα·CPN against the model's CPN, would give a k of the order of CNα itself, meaningless as a scale factor.)

| Mach | 1.2 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|
| k(M) = experiment / SPIN-73 | 1.03 ± 0.03 | 0.99 ± 0.02 | 0.92 ± 0.02 | 0.87 ± 0.02 |

With the assumed OR (9.74 cal), the model gets the family right up to Mach 1.5; above that, it puts the center of pressure behind the measured one, by 8 % at Mach 2.0 and 13 % at 2.5. Three caveats, all in the output:

- The residual (0.138) is above the pure error (0.085): a single scale factor does not describe the M-62, which deviates in the opposite direction to the other three. Without it, the residual falls to 0.087 and k becomes 1.01 / 0.96 / 0.89 / 0.83.
- The assumed ogive radius weighs as much as the statistics: with OR = 8 cal, k = 1.10 / 1.04 / 0.96 / 0.90; with 12 cal, 0.98 / 0.95 / 0.89 / 0.84. With any of the three, k < 1 at Mach 2.0 and 2.5, but with OR = 8 cal at Mach 2.0 only by about two standard deviations (0.96 ± 0.02); at Mach 1.2 and 1.5, the side of 1 on which k falls depends on the OR.
- k inherits the XC cells decided by the 1973 tables. None came from free flight, so it is not circular, but it does not measure the listing's XC15 either, which was not printed.

**Order of magnitude of the deviations already measured in this family:** Magnus +0.3 to +0.5 (overestimates), CNα +0.21 only for the M-80 (the shortest), Cmq 2.5× in the transonic range and 10 % in the supersonic range (overestimates) and CPN right up to Mach 1.5 and 8 to 13 % behind the measured one at Mach 2.0 to 2.5 (k(M), with OR = 9.74 cal; on the mean of the rounds, 0.14 to 0.22 caliber behind for the M-80, the M-59 and the M-61 and −0.07 for the M-62), the latter dependent on the XC15 decided by the tables. The first three point the same way (SPIN-73 overestimates); the CPN one has no single sign. The explanation by scale — SPIN-73 was calibrated on artillery projectiles, much larger than the 7.62 — only partly holds: with ten groups ([CORRECTION.md](CORRECTION.md)), the scale correction is accepted for the transonic Cmq and rejected for the supersonic Cmq, for CNα above the subsonic range and for Magnus.

## Hitchcock's compendium (BRL 620) — `scripts/free_flight/hitchcock/`

AD-800 469 (Hitchcock, *Aerodynamic Data for Spinning Projectiles*, 1947/1952) is the missing compendium: ~100 projectiles grouped by caliber, each with a sketch dimensioned in calibers, a table of physical characteristics (weight, CG, moments of inertia) and tables of K_M (moment), K_L (cross-wind force), K_H (damping) and K_I, with the velocity of each firing series. It is the variety of shapes the 7.62 family lacks.

The PDF is a scan with an OCR layer that did **not** capture the numbers — only the prose. The pages are CCITT G4 images inside the PDF, and `scripts/reading/pdf_page.py` extracts them by wrapping the stream in a TIFF, without depending on poppler. The print is typeset and very legible, unlike SPIN-73's dot-matrix one.

### Conversions (`conversions.py`), verified and not assumed

| Quantity | BRL | SPIN-73 |
|---|---|---|
| Drag | K_D | CX = (8/π)·K_D |
| Overturning moment | K_M | CMα = (8/π)·K_M |
| Cross-wind force | K_L | CNα = (8/π)·K_L + CX |
| Damping | K_H | Cmq = −(16/π)·K_H |
| Positions | g, h from the base | VCG = VL − g, CPN = VL − h |

The last two are the ones that usually go wrong. They were checked numerically on the caliber .30 Ball M2 (`tests/test_cal030.py`):

- **K_M:** the CMα implied by the measured stability factor (S = 3.42), computed with SPIN-73's s_g formula and the moments of inertia from the report itself, gives **1.286** against **1.299** from (8/π)·0.51 — a 1 % difference. This validates at the same time the conversion and the reconstructed stability formula, against an independent source 25 years older.
- **K_H:** the reconstructed Cmq at this geometry at Mach 2.49 is **−12.90** against **−13.24** from −(16/π)·2.6 — 3 %. The factor of 2 between q·d/V and q·d/2V is needed; without it almost double would be left over.
- **K_L:** (8/π)·0.98 = 2.496 with a reconstructed CNα of 2.918 implies CX = 0.42, and the drag plot on the same page gives CX ≈ 0.38.

That is: at Mach 2.5 for this projectile, SPIN-73's Cmq misses by 3 %. It is consistent with what the 7.62 showed (factor 0.90 at Mach 2 to 2.5) and reinforces that the Cmq problem is in the transonic range, not the supersonic one.

### Hitchcock's own empirical formulas

Page 11 of the report has the direct predecessors of SPIN-73's equations, linear in the same geometric variables (boattail angle and length, cylinder length, ogive, ogive radius) but **with no Mach dependence**:

    K_N = 0.020a − 0.748b + 0.1715c + 0.540d − 0.0266e
    h   = −0.0135a + 1.97b + 0.6276c + 0.4837d − 0.0233e

For the Ball M2, the h formula gives the center of pressure within 0.06 caliber of the value implied by the experiment — which also supports the reading of XC we made in the baseline.

### Caliber .30 complete and validated (`data_cal030.py`, `tests/test_cal030.py`)

Read: the four sketches (p. 16), physical characteristics of 5 projectiles (p. 18), stability and damping tables (p. 20).

**Validation at three levels.** The strongest does not depend on SPIN-73: they are identities of the report itself, which catch any misread digit.

*Geometry.* The four sketches close by the sum of the parts: Ball M1 0.81 + 1.20 + 2.43 = 4.44; Ball M2 1.32 + 2.43 = 3.75; A.P. M2 2.12 + 2.45 = 4.57; Tracer M1 2.30 + 2.45 = 4.75.

*Stability.* For each firing series, the printed K_M has to match the stability factor S, the velocity and the tabulated moments of inertia. When the Mach number is printed, the series temperature comes from a = V/M and corrects the density.

| Projectile | CMα from S / (8/π)·K_M | Reading |
|---|---|---|
| Ball M2 | 0.990 | verified |
| Tracer M1 (mean inertia, as the note says) | 0.982 | verified |
| Frangible M22 | 0.989 | verified |
| A.P. M2 | 1.044 | within the temperature uncertainty (Mach not printed) |
| Ball M1 (three series) | 1.094 / 1.090 / 1.122 | **inconsistency in the source** |

The Ball M1 misses in the same direction in all three series. The suspect cell, B = 16.40, was reread under zoom and is unambiguous typography — it is not a transcription error. A B of 18.40 (6/8 pair) would reconcile the three series (0.97–1.00) and put the Ball M1 in line with the inertia formula on p. 9, which the other three follow. It is recorded as a hypothesis of a typographical error in the original, without changing the printed value.

**SPIN-73 against the experiment**, with the conversions already verified:

| Projectile | Base | Cmq model / measured | CX implied by K_L |
|---|---|---|---|
| Ball M2 | square | 0.97 | 0.42 (plot on p. 19: ≈ 0.38) |
| Tracer M1 | square | 0.90 | 0.19 (low; the tracer reduces base drag) |
| Ball M1 | boattail 0.81 | 0.75 | 0.91 (impossible) |

For the two square-base projectiles the model gets Cmq within 3–10 % and CNα consistently with the drag. For the Ball M1, with a boattail, it misses Cmq by 25 % and CNα by about 0.5 — but it is also the projectile whose data are internally inconsistent in the source. **Nothing can be concluded about SPIN-73's boattail terms from a single doubtful point**: boattails from other caliber sections are needed.

**CMα against the experiment** (`compare_cma_cal030.py`, output in `docs/results/cma_cal030.txt`). With XC15 from Mach 1.2 to 5 decided by the 1973 tables, the reconstructed CPN exists over the whole range, and the model's CMα, (VCG − CPN)·CNα, can be compared with (8/π)·K_M. Assumptions: DM = 0.12 (not dimensioned in the sketches; it is the convention of the small-arms sources in `correction/flight_data.py`), printed Mach or V/a with a = 1113 ft/s, the Frangible M22 with the contour of the Ball M2 (note on p. 18) and, for the Tracer M1, the mean CG, with which the report computes the apparent K_M.

| Projectile | Mach | CMα model / measured | Reading of the row |
|---|---|---|---|
| Frangible M22 | 1.23 | 0.986 | verified |
| Tracer M1 | 2.27 | 1.054 (1.367 with the CG of the full projectile) | verified (apparent K_M) |
| Ball M2 | 2.31 | 1.197 | verified |
| A.P. M2 | 2.47 | 0.658 (0.683 with the base taper as a boattail) | temperature uncertainty |
| Ball M1 | 1.79 / 2.41 / 2.57 | 0.812 / 1.005 / 1.097 | inconsistent in the source |

For the three square-base projectiles with a verified reading, the model sits at −1 %, +5 % and +20 % of the measured value; the Tracer M1's depends on the CG adopted for the apparent K_M. The A.P. M2 sits a third below, and treating the base taper as a boattail barely changes that. For the Ball M1, with a boattail, the measured value falls from 3.158 to 2.445 between Mach 1.79 and 2.57 and the model barely varies (2.563 to 2.686), but the source is inconsistent for this projectile.

Besides the reading, two things weigh. The assumed DM: with 0.05 and 0.20, the Ball M2 ratio goes from 1.104 to 1.304. And, between Mach 2 and 3, XC1 at Mach 2.5, decided by the model (read 1.90, decided 1.99): with the read value, the ratios rise to 1.324 for the Ball M2, 1.130 for the Tracer M1 and 0.730 for the A.P. M2. The decided XC15 only enters the Ball M1, the only one with a boattail; for the square-base ones it carries no weight, and the Frangible M22 (Mach 1.23) uses no decided cell. None of these cells came from Hitchcock, so the comparison is not circular.

### Next slices

Each caliber section costs about three pages (sketches, physical characteristics, stability and damping). Priority: sections with **boattails** with consistent data, which is what the caliber .30 left open.

## Empirical correction with free flight (`scripts/free_flight/correction/`)

Ten groups of projectiles (7.62 NATO, 5.56 NATO in two groups, .50, 7.62 match, 30 mm, 155 mm M101 and M483A1, 175 mm T203 as a 90 mm model and 152 mm XM617), 1391 measured values in the SPIN-73 convention. The correction only uses what SPIN-73 lacks, scale (Reynolds number in CX0, log of the diameter in the others), and only what the nested leave-one-group-out cross-validation accepts goes in. Result, as prediction error on the unseen groups: CX0 corrected in all three regimes (supersonic 6.6 % → 4.8 %, transonic 10.7 % → 8.2 %, subsonic 19.3 % → 15.1 %, improving 7 of 9 or 10 groups), CNα only in the subsonic range (13.2 % → 10.7 %, at the limit of the rule: the worst group gets 1.97 times worse, with the limit at 2) and Cmq only in the transonic range (90 % → 72 %). The transonic CNα was rejected by a small margin (2.01), and CMα and Magnus cannot be corrected. Drag is the firm piece; `"free_flight:CX0"` is the conservative choice. Details in [CORRECTION.md](CORRECTION.md).
