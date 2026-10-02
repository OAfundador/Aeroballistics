# Transcription notes and discrepancies

Source: DTIC scan AD0915628 (JP2, 96 pages). Pages cited by the report's printed numbering.

## T — Decided readings (Table 14, 175 mm M437, p. 65)

The dot-matrix printout confuses pairs of glyphs (6/8, 1/3, 2/5, 0/6). In the cells below, the visual reading was ambiguous. The decision came from an identity **independent** of the column in question. All of them stay out of the comparisons in `test_m437.py` (the `DECIDED_READINGS` set) so the validation is not circular.

| Cell | Ambiguous reading | Decided | Evidence |
|---|---|---|---|
| CX, Mach 0.01 and 0.60 | 0.1?5 | 0.105 | the printed sd (−0.071) is only reproduced with 0.105 |
| SPIN, Mach 0.80 | 4?9.2 | 489.2 | p = Mach · a · 2π/(n·d) is exact in the other rows |
| CPF5, Mach 0.80 | 4.23? | 4.232 | CNPA5 = (VCG − CPF5)·CYPA |
| CPF5, Mach 0.95 | 4.0?6 | 4.086 | same |
| L1, Mach 0.80 | −.000?42 | −.000382 | L1+L2 = 2K(−CNα + k₂⁻²/2·Cmq), with no Magnus term |
| SBAR5, Mach 1.35 | 1.?01 | 1.201 | printed RECIP5 = 1/(sd(2−sd)) → 1.201 |
| L15, Mach 1.10 | −.00016? | −.000168 | L15+L25, as in L1 |
| RECIP5, Mach 1.05 | 1.06? | 1.068 | printed SBAR5 (1.253) |

Also decided in the same spirit, but still without a dedicated test: CMA at Mach 0.01 (4.384, via CPN), CMA at Mach 0.90 (5.708) and 1.10 (5.090), and CPN at Mach 1.10 (0.933).

## T2 — Magnus and Clp: identification from the tables (`magnus_clp.py`)

With the M437, the equations of CYPA, CPF1, CPF5 and CLP invert exactly at each Mach. The values obtained for E1, E2 and E4 fall within 0.002 of two-decimal numbers (E1 = −0.16 in the supersonic range; E2 rises from 1.80 to 3.05; E4 from 2.90 to 3.10). We adopted the round values as the hypothesis for the original DATA. G1 equals the M437's CLP column, because the reference VL of the formula (5.51) is the M437's own VL, and for that reason it is only known to 3 decimals.

**Prediction test:** applied to the 5"/38 and the 155 mm M101, these values reproduce CYPA, CPF1, CPF5 and CLP within 1 unit in the 3rd decimal in every row, except in the cells below. All of them are ambiguous glyph pairs.

| Table | Cell | Read | Predicted |
|---|---|---|---|
| M437 | CPF5, Mach 1.10 | 4.236 | 4.238 |
| 5"/38 | CPF1, Mach 0.90 | 2.747 | 2.742 |
| M101 | CPF1, Mach 0.95 | 3.004 | 3.006 |
| M101 | CPF1, Mach 1.00 | 3.170 | 3.128 |
| M101 | CPF1, Mach 1.05 | 3.294 | 3.254 |
| M101 | CPF5, Mach 0.80 | 3.404 | 3.406 |

M101 CPF1 at Mach 1.20 was reread under zoom: 3.388, not 3.368 as in the first reading; it agrees with the prediction.

**The geometry of two headers was decided by the model** (see the `decided:` lines in the headers of `data/tables_1973/`). With the original visual readings (M101: VL 4.910, VN 2.490, VB 0.490; 5"/38: VL 4.593), the predictions missed systematically. The decided readings (4.510/2.450/0.450 and 4.590) are 9/5 and 3/0 pairs and make three independent columns match at the same time. For these two projectiles, the test validates the model and the reading together, not separately.

E3 (Magnus at 2°) does not appear directly in the tables. It should be recoverable from the CNPA3/CNPA5 columns, which seem to be the coefficients of the polynomial in sin α fitted to the three angles.

## E — Report text × behavior of the tables

**E1 (confirmed).** Damping rates λ₁,₂, p. 18. The text prints −C_Nα(1 ± 1/σ). The tables are only reproduced with **−C_Nα(1 ∓ 1/σ)**; the other terms stay as printed. With the text's sign, the error reaches ~3×10⁻⁴ 1/ft, of the order of the value itself. With the correction, the error stays below 10⁻⁶ in every validated row. The corrected sign is the physically expected one (compare with McCoy, *Modern Exterior Ballistics*, term 2T−H). The test `test_text_formula_does_not_reproduce` records the finding.

**E2.** Term C₁₁ of AMOMSQ: the text writes `CCRT · CYNN`. Treated as a typographical error for CVNN.

**E3.** AMOMBT uses `VBTT`, but the text defines `VBTI = CVL/4.7`, and CVL is only defined in the Magnus section (CVL = VL). Implemented as VL/4.7.

**E4.** Magnus at 5°: the bracket is misplaced in the text. The form used at 1° and 2° was followed.

**E5.** Boattail exponents A, B ("subsonic"/"supersonic"): the Mach threshold is not given. Mach ≥ 1.0 assumed as supersonic.

**E6.** DXBT: the text gives (VB − 0.65)·A₁₀. Line 308 of the listing seems to have another form (a10 multiplied by a constant, plus a term in VB − 1), not yet read reliably.

**E7.** a₁₀ does not appear in the main sum of CX, only in DXBT; a₁₃ appears only in DXN. It may be correct, but it is worth checking in the listing.

**E8.** The text's "IF"s use strict inequalities (0 < VN < 3). The treatment of the equalities was assumed.

## A — Open

**A1 (resolved, see T8).** The computed gyroscopic factor sg was systematically ~0.17 % below the printed one. It is a constant bias in every row, not noise. The implied ρ is ≈ 0.002372 slug/ft³, against 0.002376 from the listing's formula (line 92). Hypotheses: another conversion constant (g, 144), another value of ρ used in computing sg, or some digit of Ix. The frequencies W1/W2 inherit the residual via σ. The tests use a 0.3 % tolerance.

**A2.** DELT and DISP were not implemented. DELT seems to be 2π/(20·W1) (it matches at Mach ≥ 0.6, but not at 0.01). DISP depends on reference 71 (Whyte 1970), which we do not have.

**A3.** Fit coefficients: E1, E2, E4 and G1 identified from the tables (section T2). The others (a, B, C, D, E3, F) are still pending.

**A4.** The tables on pp. 44 (90 mm M71) and 47 (105 mm M1) have identical headers. It may be the same normalized geometry or a duplicated page; the bodies still need comparing.

## T3 — Geometry of the 14 tables and the long-body term in Magnus

**Geometry.** VL and VB come from CYPA in two regimes (E1 = −0.16 supersonic and −0.23 at Mach 0.95). VN comes from CPF1 and CPF5. The result is in the `decided:` lines of the table headers. The values of E1 in the transonic range are confirmed as exact multiples in every legible table.

**Term missing from the text (confirmed).** For projectiles with VL > 6, CPF1 and CPF5 sit above the prediction in the supersonic range, and the excess is the same in both columns. It fits exactly K(M)·max(0, VL − 6) added to the Magnus bracket, with K = 0.10 / 0.20 / 0.30 / 0.30 / 0.27 / 0.25 / 0.20 at Mach 1.5 / 1.75 / 2 / 2.5 / 3 / 4 / 5 and zero below. The ratio between 7 cal, 9 cal, 10 cal and 175 SRC is 1 : 3 : 4 : 0.5. With the term, the 5, 7 and 9 cal ANSR are reproduced exactly (`test_magnus.py`). The 175 SRC sits ~0.005 above: open.

**Duplicated page.** Pages 44 (90 mm M71) and 47 (105 mm M1) have identical bodies, with the same printing artifacts. The 105 mm M1 table is not in the scan.

## T4 — Attempt to reconstruct B1..B9 (CNα), in `scripts/reconstruction/cna_spin73.py`

With 10 tables of known OR, the system has 10 equations for 9 unknowns per Mach. The fit reaches a maximum residual of ~0.004, eight times the printout's rounding (0.0005). At Mach 0.95 the residual reaches 0.03. The matrix is ill-conditioned: the smallest singular value is 0.1 % of the largest. The B values obtained are not round and are not reliable. Fixing B8 and B9 at the values read in DATA XB8/XB9 (p. 80) WORSENS the fit, so that association is not confirmed.

Conclusion: with the current data, B is not reconstructed. Possible causes, in no order of probability: reading errors in CNA, terms missing from the text (the text defines CDMM, CBBD and DNX in the CNα section, but does not use them in CNAB) or the sub/supersonic threshold of the boattail exponents (E5).

## T5 — CNα reconstructed from the DATA blocks (overnight session)

**Program structure (DIMENSION, p. 79).** The listing declares XA1..XA15, XB1..XB10, XC1..XC17, XE1..XE4, XF1..XF9 and XG1. The report's text only describes a1..a13, B1..B9 and F1..F8. So there are at least A14, A15, B10 and F9 that the text does not document, which is consistent with the long-body Magnus term (T3). The Mach grid is in `DATA XMACH`: 0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.35, 1.5, 1.75, 2, 2.5, 3, 4, 5. Confirmed.

**XB1..XB9 read** (pp. 79–80, JP2). XB1 matches the B1 of the least-squares fit where it was stable (for example, 2.40 / 2.49 / 2.60 at Mach 1.2 / 1.35 / 1.5), which confirms XB ↔ B.

**Boattail exponent threshold:** the program already uses the supersonic exponent at Mach 0.95. With the threshold at 1.0, the four tables with a boattail missed by −0.15 in that row; with 0.95 the error vanishes. This resolves item E5.

**Result:** with the XB values as read, 65 % of the 170 cells (10 tables × 17 Mach) fall within the rounding (±0.0015). Six reading corrections raise that to 78 % (91 % within ±0.005). Each correction is a single number that zeroes the residual of 7 or more tables at the same time and corresponds to a confusable glyph pair (list in `src/spin73/data/xb_read.py`, `CORRECTIONS`). None was rechecked on the image.

**What is left:**

- The table on p. 44 (90 mm M71) misses at almost every Mach. Its transcription is the most degraded, and changing the geometry does not fix it.
- The 5"/38 sits +0.014 constant from Mach 2.5 to 5. Suspect: the reading of CNA (2.953 / 2.929 / 2.829 / 2.729).
- The Mach 2.0 row in the ANSR tables and some isolated cells are listed in `test_cna.py` (`PENDING`).

**Comparison with experiment (7.62 NATO, MR 1833, M ≥ 1.1; `scripts/free_flight/mr1833/compare_cna.py`, output in `docs/results/cna_mr1833.txt`).** The reconstructed CNα agrees with the M-59 (−0.03), M-61 (−0.06) and M-62 (−0.12); the experimental scatter is 0.17–0.31. For the M-80, the shortest, SPIN-73 overestimates by +0.21 (15 rounds; pure error/√n = 0.07): the model gives practically the same CNα to all four, and the experiment grows with length. The result does not depend on the ogive radius, which is uncertain for this family. The first version of this comparison gave +0.28 for the M-80 (+0.01, −0.01 and −0.08 for the others); it predates card C205 (T15), and the script reproduces those values without the card. It is a clear target for recalibrating the length term (B3/B6) on short bodies.

## T6 — DATA XC and the center of pressure (task A, with numerical validation)

**Reading.** XC1..XC17 read on p. 80 (`src/spin73/data/xc_read.py`). The character grid of the listing on the rotated page is x(column) = 1158 + (column − 6)·19.2 px. Split of the statements: XC1 into 11+6, XC2..XC16 into 8+9, XC17 into 10+7.

**Printing defect (finding).** Lines y = 1867 and y = 1900 of the rotated p. 80 are the same image (pixel correlation 0.90, against 0.65 for a neighboring line with the same prefix) and both carry the XC16 label: the continuation card of XC15 was replaced by a second copy of the first XC16 card. In other words, **XC15 from Mach 1.2 to 5.0 does not exist in the printed listing**. The two copies still disagree in one digit (11.766 and 11.768 in the 7th value of XC16), which shows the difference is in the printing, not in the content.

**Validation on the 175 mm M437 (p. 65).** With the equation on p. 15 and the CNα XBs, the computed CPN and CMα match the printed ones within 0.0007 at Mach 0.01, 0.90 and 1.10 — the three points where all twelve coefficients are read without doubt. This validates at the same time the structure of the equation (including the text corrections E2 and E3) and the reading of the coefficients.

**Open.** At the other Mach numbers the residual concentrates in the XC12 line, which is faded: Mach 0.6 (−0.016), 0.8 (−0.032), 0.95 (−0.003), 1.0 (−0.008) and 1.05 (−0.598). Attributing the whole residual to C12, the table would imply −3.6541 / −3.8644 / −4.1997 / −2.9249 / −1.6862. None is a clean one-digit swap, so it is not proven that the error is only in C12. At Mach ≥ 1.2 the same holds for XC15: solved from the M437 column, it would give 1.447 / 2.076 / 1.088 / 0.551 / 0.202 / −2.474 / −0.915 / −0.921 / −0.919, a sequence too irregular for a DATA line. All of these are values decided by the model and stay out of any validation done with the M437 itself. **What is needed to separate them: the CPN column of another table with a boattail** (5"/38 p. 53, M101 p. 59 or XM380E5 p. 50) and of one without a boattail (ANSR), which isolate C1..C11 from C12..C16.

## T7 — Glyph reading by templates (task D)

Method: on a listing line the printer has a fixed pitch (~19.2 px per column). By fitting origin and pitch, each character is cropped; the reliably read ones form, for each digit, an ink-probability template, and the doubtful glyph is compared with each candidate by a Bernoulli likelihood with fading (fading only removes ink; ink outside the candidate's template weighs against it).

Applied to the 10 disputed digits of the 6 XB corrections (section T5), the method agrees with the numerical decision in 8 and disagrees in 2 — precisely the ones with the worst error rate in the calibration.

| Correction | Template verdict | Numerical effect |
|---|---|---|
| B3 Mach 1.0: −.0155 → −.0305 | confirms both digits | kept |
| B2 Mach 1.2: −.0417 → −.0617 | confirms | kept |
| B7 Mach 1.5: −.1490 → −.1695 | confirms both digits | kept |
| B5 Mach 2.5: .0667 → .0609 | 3rd digit 0, but 4th digit 7, i.e. .0607 | difference of 0.0002: indifferent |
| B4 Mach 0.01: −.0856 → −.0898 | 3rd digit 9, but 4th digit 6 (6/8 template, the worst: 7 errors in 77) | the equality with Mach 0.6 still favors −.0898 |
| B3 Mach 1.2: −.0100 → −.0106 | keeps the 0 as read, but with a marginal margin | with −.0100, three tables (7, 9 and 10 cal) leave the rounding |

Count of CNα within ±0.0015, without p. 44 (153 cells): current XB 133, XB as read 111, XB by the glyph verdicts 130. Conclusion: the corrections B3@1.0, B2@1.2 and B7@1.5 now have an objective reading and numerical evidence; B5@2.5 becomes .0607; B4@0.01 and B3@1.2 remain decided by the model, with the template disagreeing within its own error margin.

## T6.1 — XC tested on a second table, and the XC12 cell at Mach 1.05

To separate a reading error in C1..C11 from an error in C12..C16, I transcribed the CMA and CPN columns of the **5"/38 NAVY (p. 53)**, which has a 0.35 cal boattail against the M437's 1.00 cal — the weights of the two blocks change a lot between the two. The data are in `scripts/reconstruction/data_cpn.py`; the reading was checked cell by cell by the identity CMA = (VCG − CPN)·CNα with the printed CNα, which resolved two of them (CPN at Mach 0.01 and CMA at Mach 0.90, the latter a 4/8 pair).

**Using the printed CNα instead of the reconstructed one.** The error of the reconstructed CNα (up to 0.002) enters CPN multiplied by about 3. With the printed CNα, the M437's CPN residual at Mach 0.95 falls from −0.0029 to +0.0007, that is, within the rounding. `cpn_spin73.cpn_cma` accepts `printed_cna` precisely for this.

**Result.** With the printed CNα, the computation closes within ±0.0015 at Mach 0.90, 0.95 and 1.10 for the M437 and at 0.90, 1.00 and 1.10 for the 5"/38 — two different geometries, the same seventeen coefficients. This validates the structure of the equation and the reading of XC at those points.

**XC12 at Mach 1.05 (decided by the model).** The value read, −2.646, reproduces neither table. Testing each coefficient as the single candidate — the Δ implied by one table has to equal the one implied by the other —, only XC12 gives a ratio of 1.00: the two ask for Δ = 0.9598 and 0.9616. With **XC12 = −1.684** the residuals fall to +0.0008 (M437) and −0.0001 (5"/38). The crop of the line in the listing is ambiguous in all three decimals (the line is faded), so the value is recorded as decided by the model in `xc_read.CORRECTIONS`, and Mach 1.05 leaves the validation in both tables.

**What remains open.** Mach 0.6 and 0.8: both tables miss, but no single coefficient explains both at the same time (the candidates with a ratio near 1 would require breaking the repetition of values in the line itself, like XC3 at 0.6, which is equal at indices 0, 1 and 2). Probably two wrong cells in the same column. Mach 1.0: only the M437 misses (+0.008); the 5"/38 closes. Mach 0.01: the M437 closes and the 5"/38 misses by +0.011, which depends on which of the two CPN readings is right (0.769 or 0.779). A third table without a boattail (ANSR) would resolve all three cases, because it zeroes the whole C12..C16 block.

## T6.2 — Two cells of the missing XC15 card recovered

At each Mach above 1.1, the boattail block of CPN has two unknowns: XC12 (faded line, with several doubtful cells) and XC15 (card not printed). The CPN columns of the M437 and the 5"/38 give two equations, so the pair comes out solved — and the **consistency test is XC12 itself**, which was read in the listing and did not enter the computation.

| Mach | XC12 read | XC12 solved | XC15 solved | Reading |
|---|---|---|---|---|
| 1.2 | −1.1620 | −1.1630 | **1.4366** | closes: XC15 reliable |
| 1.35 | −0.8054 | −0.8157 | 2.0042 | XC12 differs by 0.010: it is one of the doubtful cells |
| 1.5 | −0.6033 | −0.6192 | 0.9767 | same, differs by 0.016 |
| 1.75 | −0.3949 | −0.3867 | 0.6082 | differs by 0.008 |
| 2.0 | −0.2274 | −0.2266 | **0.2079** | closes: XC15 reliable |
| 2.5 | 0.1794 | 0.5642 | 0.2496 | does not close: the 5"/38's printed CNα is suspect from Mach 2.5 to 5 (section T5) |
| 3.0 | 0.1794 | — | — | 5"/38 CPN illegible |
| 4.0 / 5.0 | 0.1794 | 0.1938 / 0.1985 | −0.819 / −0.784 | same suspicion about CNα |

The two reliable values went into `xc_read.RECOVERED` and are applied to XC, marked as decided by the model; Mach 1.2 and 2.0 stay out of the validation because they are circular.

**How to close the rest.** A third table with a boattail (155 mm M101 p. 59, or 105 mm XM380E5 p. 50) gives three equations for the same two unknowns: one degree of freedom is left over to detect which cell is wrong, instead of just solving the system. It is the natural next step, together with rereading the 5"/38's CNα above Mach 2.5.

## T6.3 — A table without a boattail confirms the C1..C11 block

On the 20 mm 5 cal ANSR (p. 32) the boattail is zero, which zeroes C12..C16 and leaves CPN depending only on C1..C11. The page is very heavily inked and does not allow a 3-decimal reading, but at every legible Mach the computed CPN stays within the reading uncertainty (±0.02): 1.459 against 1.45 read at Mach 0.6; 1.419 against 1.43 at 0.8; 1.449 against 1.44 at 1.1. There is no gross error in C1..C11 — what remains of the residuals comes from the boattail block, as the faded XC12 line already indicated.

## T8 — What the code (pp. 84-85) resolved

What pp. 84–86 of the listing compute is described, in our own words and notation, in `src/spin73/program.py` (and in [ORIGINAL_PROGRAM.md](ORIGINAL_PROGRAM.md)); the listing itself is not reproduced in this repository. It carries no card number in columns 73-80 on almost every line; the numbering used here (Cnnn) is the compiler's statement sequence, printed on the left.

- **A1, s_g bias — resolved.** Card C241 computes, with Ix, Iy in lb·in² and lengths in inches, s_g = 1352.4·Ix²/(ρ·Iy·CMα·twist²·d³). The physical formula with g = 32.174 gives 1349.8 instead of 1352.4: the difference, +0.19 %, was the bias. With the code's constant, the M437's GYRO closes in every row (maximum error 0.0009, mean bias 0.017 %).
- **E5, boattail threshold — confirmed in the code.** Card C189 switches to the supersonic exponent from the 5th point of the Mach grid: it applies from Mach 0.95.
- **A13, A14, A15 — where they enter.** The DXN of CX has three pieces, with breaks at VN = 3.48 and 3.97: (VN − 3)·A13; 0.48·A13 + (VN − 3.48)·A14; 0.48·A13 + 0.49·A14 + (VN − 3.97)·A15. The coefficients 0.48 and 0.49 are exactly the widths of the previous pieces, which makes DXN continuous. The report's text only documents the first piece.
- **Long-body Magnus term = XE5.** Cards C216-C222: if VL > 6, the term e5·(VL − 6) is added to CPF after the bracket. The K values identified from the tables (section T3) are XE5. For VB = 0, adding to CPF or inside the bracket gives the same result — that is why the identification from the ANSR tables worked —, but with a boattail the two forms differ.
- **Boattail rule in CPN, missing from the text.** Cards C209-C210: if the boattail moment (AMOMBT) comes out positive, the program sets CNAT = CNAB and AMOMBT = 0, discarding the whole boattail contribution.
- **Cmq (C232-C238) and Clp (C239)** confirm the forms already used; Clp divides by SFNG, which in the text is 5.51.

Transcription doubt: card C205 is a condition whose variable names, as printed, match no variable in the section. The most likely reading is to zero the boattail normal force if it comes out positive; not implemented until it is reread.

## T9 — DATA XD (CX2) and the final XE5 card

**Reading.** XD1 and the first XD2 card at the foot of p. 80, sharp; the rest on p. 81, faded. The statements here are of three cards (7 + 7 + 3 values). XD1 rises in steps of 0.5 up to Mach 1.2 and falls by the same step; XD4 goes from −1 to 0 in steps of 0.1. Data in `src/spin73/data/xd_read.py`.

**Validation with two tables.** In the equation CX2 = XD1 + XD2·CXCL + XD3·CRAT + XD4·VB − CNα, the 175 mm M437 gives weights 0.10 and −0.06 to XD2 and XD3; the 5"/38, 0.59 and 0.47. Fixing XD1 and XD4, each Mach gives two equations for XD2 and XD3, and the solution returns the values read at 0.01 / 0.6 / 0.9 / 1.0 / 1.05 / 1.35 / 2.0. The PRINTED CNα of each table was used, to isolate XD from the error of the reconstructed CNα.

| Cell | Reading | Decision | Evidence |
|---|---|---|---|
| XD3, Mach 0.8 | .? | 0.4 | 5"/38 asks for +0.0996; completes .3 .3 .4 .5 .6 |
| XD2, Mach 1.35 | illegible | 0.5 | two tables: 0.501 |
| XD2, Mach 2.0 | .6? | 0.5 | two tables: 0.501 (with XD3 = 0.998) |
| XD2, Mach 2.5 | .6? | kept, doubtful | only the M437 is reliable there; residual +0.020 |

**Errors in the old M437 transcription (`m437_table.csv`), found through XD:**

| Cell | Transcribed | Scan reread | DATA XD | Status |
|---|---|---|---|---|
| CX2, Mach 1.05 | 4.567 | **4.507** | 4.506 | corrected by the rereading |
| CX2, Mach 0.8 | 2.603 | 2.6?3 (ambiguous) | 2.805 | stays as transcribed; out of the validation |
| CX2, Mach 1.1 | 5.132 | illegible | 5.002 | stays as transcribed; out of the validation |

Open: residual of 0.007 to 0.009 for the M437 at Mach 1.5 and 1.75, where the 5"/38 closes exactly.

**XE5.** On p. 81, between XE4 (statement 56) and XF1 (58), the continuation card `1 0.3,0.3,0.27,0.25,0.20/` appears printed twice and statement 57 is missing — the same defect as XC15 (section T6). The five printed values (Mach 2 to 5) are **exactly** those of the long-body term that the 7, 9 and 10 caliber tables had identified (section T3). The first 12 values, from the card that was not printed, still come from the tables.

## T10 — DATA XA (CX) and the complete program

**Reading** (p. 79, `src/spin73/data/xa_read.py`). XA1..XA10 in 2-line statements; XA11 and XA12 in 3 cards (7 + 7 + 3); XA13..XA15 in 2 lines (10 + 7). The count up to 17 decides the number of leading zeros of XA4 (6), XA9 (3), XA13 (3), XA14 (5) and XA15 (3). XA1 has the shape of a drag curve (0.20 subsonic, peak of 0.41 at Mach 1.05, 0.18 at Mach 5).

**Validation with two tables.** The 175 mm M437 and the 5"/38 give XA2 weights of opposite sign (VNX − 2.5 = +0.41 and −0.35) and XA7 very different weights (boattails of 1.00 and 0.35 cal). With the final reading, **CX closes at 17 of 17 Mach numbers in both tables** (maximum error 0.0011 and 0.0013). The 5"/38's CX column was transcribed in this session (`data_cx.py`).

| Cell | Reading | Decision | Evidence |
|---|---|---|---|
| XA2, Mach 1.05 | −.0487 (low zoom) | **−.0687**, reread under zoom | both tables asked for −.0688 (4/6 pair) |
| XA10, Mach 1.0 | .02 (seemed out of sequence) | kept | both tables close with .02 |
| XA1, Mach 0.01 and 0.6 | .2?? (faded) | .2014 | the CX at these Mach numbers sits 0.002 below that at 0.8 in both tables; an equal step can only come from XA1 (weight 1 in both) |
| XA2, Mach 0.01 and 0.6 | .0157? | .0057 | equal to the 3rd value, as in almost every XA; both tables ask for .0064 |

The M437's CX = 0.105 at Mach 0.01 and 0.6, which had been decided by the printed s_d (section T), matches the DATA — but those two rows stay out of the XA validation, because they decided XA1 and XA2 there.

XA13..XA15 (ogive longer than 3 calibers) are read but **not tested**: no transcribed table has VN > 3. The candidate is the 175 mm SRC (p. 68, VN = 5.5).

**The complete program.** With XA, `spin73.table()` runs from the geometry to the stability analysis. For the M437, 17 of 17 close: CX, CYPA, CNPA, CPF1, CNPA5, CLP, SPIN and RECIP5. The remaining failures (CPN, CMα and, as a consequence, s_g, ω and λ) are all at the Mach numbers where XC is not complete: the faded XC12 and the missing XC15 card.

## T11 — XC complete: final decisions and what stayed uncertain

With XA and XD reconstructed, XC was the last block with gaps. Decisions (`src/spin73/data/xc_read.py`):

| Cell | Reading | Decision | Evidence | Confidence |
|---|---|---|---|---|
| XC1, Mach 0.8 | 1.66 | **1.68** | the only candidate compatible with both tables; 6/8 pair; zeroes both residuals (M437 +0.036 → −0.002; 5"/38 +0.024 → 0.000) | high |
| XC12, Mach 0.6 | −3.670 | −3.650 | equal to the Mach 0.01 one, as in XC2..XC11; improves both tables | medium (M437 stays at −0.004) |
| XC15, Mach 1.35 / 1.5 / 1.75 / 4 / 5 | missing card | by the M437 | checked on the 5"/38 within 0.004–0.009 in CPN | medium |
| XC15, Mach 3 | missing card | by the M437 | no check (5"/38 CPN illegible) | low |
| XC15, Mach 2.5 | missing card | by the M437 | **the 5"/38 misses by 0.17**: there is another misread cell at this Mach | uncertain |

With this XC has no more NaN and the program produces the M437's 24 columns from the geometry. **But the M437's CPN stopped being a test at almost every Mach**, because it was used to decide XC: only Mach 0.01, 0.9, 0.95, 1.0 and 1.1 remain independent (`test_full_model.py`, the CIRCULAR set).

*(Updated in section T13: the third table, XM380E5, resolved Mach 2.5 — the error was in XC1 — and Mach 1.0, 1.35 and 1.5.)*

**To truly validate the boattail block of CPN**, a third table with a boattail is needed. The 155 mm M101 one (p. 59) was tried: it is the most heavily inked of all, and the identity CMα = (VCG − CPN)·CNα only closes row by row with a VCG oscillating between 2.956 and 2.965. It needs cell-by-cell reading; it stays as the next step, together with the 105 mm XM380E5 (p. 50).

## T12 — Page 86: CNPA3, CNPA5, DELT, DISP and the instability rule

Formula lines read under zoom (summarized in `src/spin73/program.py`). With them, the program produces **every column the original prints**.

**CNPA3 and CNPA5 (cards C278-C281) — a defect of the original.**

    D = CNPA(5°) − CNPA(1°)            (Magnus moment at 5° minus the one at 1°)
    CNPA5 = ((D + 0.3) − 9·D)/0.0072
    CNPA3 = (D − 0.0001·CNPA5)/0.01

The constants are those of a polynomial f(δ) = C1 + C3·δ² + C5·δ⁴ evaluated at δ = 0.1 and 0.3. But the second point does not use the value at 2°: that one is computed (cards C224-C227) and never used. The second point is D plus a constant. Consequence: the two printed columns carry **a single degree of freedom** and obey **CNPA3 + 0.1·CNPA5 = 3.75** for any projectile. The 17 rows of the M437 confirm the identity — for example 4.481 − 0.7311 = 3.7499 and 16.113 − 12.3633 = 3.7497 —, and the model reproduces both columns in the 16 legible rows. The "•" in the second line, ambiguous in the scan, is a "+": reading it as "·" misses by 7 % to 400 %. This is also where the factor of 1.34 comes from, which the hypothesis of a polynomial in sin α through 1°, 2° and 5° left unexplained: the code does not use those angles.

**DELT (C266)** = 6.28/(20·W1): the nutation period divided by 20. It closes at the M437's 17 Mach numbers. The old note "does not match at Mach 0.01" (item A2) was a reading issue: the printed value is 0.7049, not 0.7649 (6/0 pair).

**DISP (C256)** = (CNα − CX)·Iy·(W1 − W2)·3.635/(CMα·weight·diameter·V), with Iy in lb·in². It closes within ±1 in the last digit in the M437's 16 legible rows. The physical quantity remains unexplained: it depends on reference 71 (Whyte 1970), which we do not have. The formula is reproduced as it is in the code.

**Damping rates (C258-C261).** The code uses −CNAT·(1 − τ) with τ = 1/σ in root 1, which confirms in the code itself the sign the tables indicated (item E1).

**Instability rule (C249, C287).** If s_g < 1.001, the program skips the dynamic analysis and prints only MACH and STAB. The model follows the rule: the other stability columns come out empty in that case.

## T13 — Third table with a boattail: 105 mm XM380E5 (p. 50)

**Reading.** Page 50 is one of the sharpest in the report. All 15 columns were transcribed in full (`data/tables_1973/p50_105mm_xm380e5.csv`), without using the model to decide digits. Nine cells were resolved by identities between **printed** columns — CMα = (VCG − CPN)·CNα, CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5) and CNPA3 + 0.1·CNPA5P = 3.75 — and stay out of the counts. Seven remained illegible. The header confirms VN = 2.900: the old reading (2.400) came from the low-resolution scan.

**No DATA of XC, XD, XE or XF was decided by this table**: in those blocks it is a test in every cell. The exception is CNα, which entered, with that of the other nine tables, the count that decided the XB corrections (T5); at the five Mach numbers of those corrections it is circular. With the whole program, starting only from the printed input, 222 independent cells: **92 % indistinguishable from the original, 98 % within the criterion.** Magnus, Cmq and Clp close in every legible cell.

**What it resolved.** Where there were two tables for two unknowns, there are now three: one degree of freedom is left over to find which cell is wrong.

| Cell | Read | Decided | Decided by | Independent check |
|---|---|---|---|---|
| XC1, Mach 2.5 | 1.90 | **1.99** | M437 (1.9899), with XC15 constant from 2.5 to 5 | XM380E5: −0.080 → +0.0001 in CPN; 5"/38: −0.168 → −0.008 |
| XC15, Mach 2.5 to 5 | missing card | **−0.9184** (constant) | M437 at Mach 3, 4, 5 (−0.9152 / −0.9211 / −0.9190) | XM380E5 ≤ 0.0005 at all four Mach numbers (small weight on XC15) |
| XC12, Mach 1.35 | −.8054 | **−.8154** | M437 + 5"/38 (−0.8157) | XM380E5: 0.0000 |
| XC12, Mach 1.5 | −.6033 | **−.6173** | M437 + 5"/38 (−0.6192) | XM380E5: −0.0009 |
| XC15, Mach 1.35 / 1.5 | missing card | 2.0052 / 0.9839 | M437 + 5"/38, with XC12 corrected | XM380E5 asks for 2.0107 at 1.35 (all three agree) |
| XC14, Mach 1.0 | −.7672 | **−.7872** | M437 (−0.7867); 6/8 pair | none: the 5"/38 and XM380E5 have CXLL ≈ −0.06 |
| XF7, Mach 1.1 to 2.5 | missing card | −0.715 and −0.73 | 5"/38 | M437 and XM380E5: −0.7151 / −0.7150 at Mach 1.1 |
| XD2, Mach 2.5 | .6? | **.5** | 5"/38 (0.509) | XM380E5, same weight: 0.500 |

**XC1 at Mach 2.5.** The "0.17 cal error on the 5"/38" (T11) was not in XC15, but in XC1. The listing's glyph is ambiguous between 0 and 9. The decision followed the order that avoids circularity. First, XC15 from 2.5 to 5 is constant, like the last four values of the XC12, XC13, XC14 and XC16 lines in the listing, and the M437 fixes it at Mach 3, 4 and 5. Then the M437 at Mach 2.5 fixes XC1. The XM380E5, which has a high weight on XC1 and entered neither decision, now closes at Mach 2.5. The XC1 line becomes 1.79 1.88 1.99 2.03 2.00 1.97.

**One more missing card: XF7.** On p. 81, after the first card of DATA XF7 (7 values), come **two copies of the third card** ("−.73, −.73, −.73 /"). The second card (Mach 1.1 to 2.5) was not printed. It is the same defect as XC15 and XE5, the third case in the listing. The −0.73 used until now at these Mach numbers was an assumption. The 5"/38's CMQ column asks for −0.7146 at Mach 1.1 and −0.729 to −0.731 from 1.2 to 2.5. The M437 and the XM380E5, outside the decision, ask for −0.7151 and −0.7150. **This was the "DATA XF misread at Mach 1.1"**, which left the M437's Cmq 0.038 off. In the 155 mm M101 table, the Mach 1.1 cell read as −14.861 is probably −14.661 (6/8 pair): the model gives −14.662.

**Still open.**
- Mach 0.6: the computed CPN sits above the printed one in the three tables with a boattail (M437 +0.004; XM380E5 +0.002; 5"/38 −0.001). Several pairs of coefficients close all three at the same time, and none is a clean glyph swap. At Mach 0.8, the same happens only for the M437 (+0.002).
- ~~5"/38 from Mach 2.5 to 5: CPN 0.006 to 0.009 low and CNα 0.014 high~~ — resolved: it was card C205 (section T15).
- 5"/38 at Mach 1.75: asks for XC15 = 0.629, against the M437's 0.550.
- The M437's CX2 at Mach 1.5, 1.75 and 2.5 (−0.007 to −0.030): the 5"/38 and the XM380E5 close, which points to the transcription of those M437 cells or to a term that only weighs with a 1 cal boattail.

## T14 — Every table in the report transcribed

Each output table (pp. 29 to 68) is in `data/tables_1973/`, with the input header. The comparison with the program, case by case, is done by `scripts/reconstruction/error_comparison.py` (see [VERIFICATION.md](VERIFICATION.md)).

**Reading method.** In the dot-matrix printout, 6 and 8 come out almost the same, as do the pairs 1/3, 2/7, 4/9, 5/9 and 0/6. The raw reading (`data/tables_1973/readings/`) marks each ambiguous glyph as a class: `A` = 6 or 8, `[27]` = 2 or 7, `?` = illegible. Then `resolve_glyphs.py` tests every combination against the identities between **printed** columns: CMα = (VCG − CPN)·CNα, CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5) and CNPA3 + 0.1·CNPA5P = 3.75. A cell that comes out with the same value in every consistent combination is resolved, marked "identity" and kept out of the statistics. What remains ambiguous is left empty. No `DATA` and no model result enter this step. `check_identities.py` checks the finished tables: all 12 pass with no violation.

**Illegible inputs.** An illegible header digit is decided by a single column, within the range the glyph allows, and that column becomes circular in that case (`scripts/reconstruction/circularity.py`). Old header readings corrected at this stage:

| Table | Input | Before | Now | Evidence |
|---|---|---|---|---|
| 20 mm M56A3 (p. 29) | meplat DM | 0.200 | 0.260 | zoom 7: the 6 is filled, unlike the open 0 next to it; with 0.200 the CX was up to 0.024 off |
| 20 mm M56A3 (p. 29) | VCG | 2.?00 | 2.260 | Magnus identity with printed columns |
| 20 mm cone (p. 41) | VCG | ?.747 | 6.747 | only 6.747 closes CNPA5 = CYPA·(VCG − CPF5) |
| 155 mm M101 (p. 59) | BD | 1.026 | 1.021 (decided by CX) | with 1.026 the CX sat 0.0027 high at every Mach |
| 155 mm M549 (p. 62) | VN | ?.90? | 2.99? (zoom 8) → 2.991 | with 2.90 the CPF5 sat 0.02 low at every Mach |
| 155 mm M549 (p. 62) | OR | ?8.9 | 18.9 | with 8.9 the CX2 misses by 0.33 |
| 105 mm XM380E5 (p. 50) | VN | 2.400 | 2.900 | high-resolution reading (T13) |

**One `DATA` corrected: XB3 at Mach 2.0**, read 0.0059 and decided 0.0050 (9/0 pair). In the long-body tables, the Mach 2.0 CNα missed in proportion to CXLL (the weight of XB3): 7 cal −0.0027, 9 cal −0.0039, 10 cal −0.0047, and the short ones closed. The value was decided by the 9 cal alone. The 7 cal and the 10 cal, outside the decision, now close.

**Old readings corrected by the identities:** M56A3 CNA at Mach 1.35 (2.650 → 2.659); 5"/38 CMα at Mach 1.05 (3.749 → 3.739) and 4.0 (3.060 → 3.066); 5"/38 CPF1 at Mach 0.9 (2.747 → 2.742, already pointed out in T2).

**First validation of XA13–XA15 and XC17.** The 175 mm SRC (p. 68, 5.5 cal ogive) is the only table with VN > 3. With it, CX closes in the 9 legible cells and CPN in the 3, one of them within 0.0025. The long-ogive branches, until now only read, get a check.

**The M1 (pp. 44/47).** The two pages of the scan are the same printout (same title, "M1", same header, the same stroke cutting the Mach 1.75 row). One of the report's two tables is not in the scan. Magnus, Cmq and Clp close with the header geometry, but CX, CX2, CNα, CPN and CMα do not, and no single change of OR, DM, BD, VN or VB fixes it. It is recorded as an open case.

**M101 CPN.** With the page reread through the identities, the M101's CPN sits 0.007 low at Mach 1.2, and the CMα 0.009 to 0.018 high at Mach 1.0, 1.05, 1.5 and 2.0. It is the only geometry with a boattail where the center of pressure does not close. Its 0.45 cal boattail lies between that of the 5"/38 (0.35) and that of the XM380E5 (0.59), which close.

## T15 — Audit against the report's conventions; card C205

**Conventions (Nomenclature, pp. 7-8; Appendix B, pp. 76-77).** Classic NACA/BRL style: q̄ = ½ρV², A = πd²/4, reference d. CMα and Magnus about the CG; CPN, CPF1 and CPF5 in calibers from the nose; derivatives per sin ᾱ; Magnus, Cmq and Clp with **pd/2V and qd/2V** (modern sources use pd/V and qd/V, and give half). The yaw drag is CX2 + CNα (p. 15). All of this is in `src/spin73/conventions.py`, with tests.

**Card C205 was not implemented.** The line had been left as a transcription doubt (T8), because the variable names, as printed, did not exist in the section. In this printout B comes out as A or P: the line above carries "XA7" where the code is XB7. Reread that way, the names are those of the boattail normal force, and the condition says it cannot add (if it comes out positive, it is zero). It only acts when the ogive is short (CVNN < 0) in the supersonic range, which is exactly the 5"/38 from Mach 1.75 to 5:

| Table | CNα, CPN, CMα and CX2 within the criterion | |
|---|---|---|
| 5"/38 (p. 53) | 38 → **53** of 56 | the "CNα 0.014 high, systematic" (T5) and the "CPN 0.006 to 0.009 low" (T11) were this |
| the other 12 | no change | none gets worse |

With the rule, the Mach 1.75 XC15, decided by the M437 alone, is now confirmed by the 5"/38 as well (before, it seemed to ask for 0.629).

**Other differences between the original program and this reconstruction**, with no effect on the tables, now documented in `conventions.py`:

- Blank fields on the card: in the original, a blank DM is 0, a blank BD is 1.00, a blank OR is a secant ogive and **a blank TEMP is 0 °F**. The tables without mass properties print a density of 0.00270, which is that of 0 °F. `Projectile` defaults to DM = 0.12 and BD = 1.02 (the values of NAUTO = 1, "automatic dimensions") and TEMP = 59 °F. To reproduce a blank card, just pass zero.
- Names: the program prints "CNPA5" for the quintic coefficient and "CNPA-5" for the secant slope at 5°; here they are CNPA5P and CNPA5.
