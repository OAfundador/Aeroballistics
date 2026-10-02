# The original program, block by block

A description of the 1973 SPIN-73 in our own words and notation: what each piece of the
program computes, with which constants, where the reading came from, what could not be read
and where it is implemented in this adaptation. **It is not the original code**, which is
in the report (DTIC AD0915628, listing on pp. 79–86) and is not reproduced in this repository.

Generated from `src/aeroballistics/program.py` (`python -m aeroballistics.program --doc`); the evidence for
each reading is in [TRANSCRIPTION_NOTES.md](TRANSCRIPTION_NOTES.md).

Notation: VL, VN, VB, VCG, OR, DM, BD, BOOM, DIA, IX, IY, WGT, TWIST, DGUN and TEMP are the
card inputs; a1..a15, b1..b9, c1..c17, d1..d4, e1..e5, f1..f9 and g1 are the values of the
DATA blocks XA, XB, XC, XD, XE, XF and XG at the row's Mach. "Statements" is the sequential
numbering the compiler printed to the left of each listing line.

## 1. Input card and atmosphere

Reads the card (geometry in calibers; diameter, inertias and weight in English units) and computes the air density and the speed of sound from the temperature.

| | |
|---|---|
| Columns | — |
| Data | — |
| Listing statements | — |
| Pages | 76–77 (card); listing (atmosphere) |
| Source of the reading | Appendix B and code |
| Implementation | `aeroballistics.core.air_density` |

Formulas:

- ΔT = TEMP − 59 °F
- ρ = 0.002376 + (−4.784·ΔT + 0.01092·ΔT²)·10⁻⁶ slug/ft³
- a = 49.04·√(459.6 + TEMP) ft/s

Rules:

- on the original card, blank fields mean DM = 0, BD = 1.00 and TEMP = 0 °F; here the defaults are 0.12, 1.02 and 59 °F (pass zero to reproduce the blank card)

## 2. Axial force at zero yaw (CX)

A polynomial in the shape variables, plus three piecewise corrections: long ogive, long cylinder and long boattail.

| | |
|---|---|
| Columns | `CX` |
| Data | XA |
| Listing statements | C164–C174 |
| Pages | 83–84 |
| Source of the reading | code (from C164 on) and text |
| Implementation | `aeroballistics.core.cx` |

Formulas:

- u = min(VN, 3) − 2.5;   L = VL − VN − VB − 1.5;   R = VN²/OR − 0.40
- β = 0 if VB ≤ 0.2;  VB − 0.2 if VB < 0.65;  0.45 from then on
- CX = a1 + a2·u + a3·u² + a4·u³ + a5·min(L, 1.5) + a6·min(L, 1.5)² + a7·β + a8·R + a9·R² + a11·(BD − 1.02) + a12·(DM − 0.12)² − 0.01·(BOOM/1.36)² − Δ_bt − Δ_og + Δ_cyl

Rules:

- Δ_og, only with an ogive longer than 3 cal, in three continuous pieces: a13·(VN − 3) up to 3.48 cal; 0.48·a13 + a14·(VN − 3.48) up to 3.97; and 0.48·a13 + 0.49·a14 + a15·(VN − 3.97) above. The text only documents the first piece
- Δ_cyl = 0.010·(L − 1.5) when L > 1.5
- Δ_bt = a10·(VB − 0.65) when VB ≥ 0.65

What was not read:

- the start of the computation is on p. 83, which was not read: the Δ_bt term follows the report text, and the output warns when it is used

## 3. Normal force, center of pressure and pitching moment

Adds the normal force and moment of the body (ogive and cylinder) to those of the boattail; the center of pressure is the ratio of the two, and the moment about the CG comes from the arm to the CG.

| | |
|---|---|
| Columns | `CNA`, `CPN`, `CMA` |
| Data | XB, XC |
| Listing statements | C175–C212 |
| Pages | 84–85 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.normal_and_moment` |

Formulas:

- v = min(VN, 3) − 2.47;   ℓ = VL − VN − VB − 2.15;   r = VN²/OR − 0.48;   m = DM − 0.17;   n = max(VN − 3, 0);   w = min(VB, 1)
- N_body = b1 + b2·v + b3·ℓ + b4·r + b5·v² + b6·ℓ²
- N_bt = b7·β_N + w·(b8·v + b9·ℓ)
- M_body = N_body·(c1 + c2·v + c3·v² + c4·v³ + c5·ℓ + c6·ℓ² + c7·ℓ³ + c8·r + c9·r² + c10·m + c11·r·v + c17·n)
- M_bt = (VL/4.7)·(c12·β_M + w·(c13·v + c14·ℓ + c15·r + c16·r·v))
- CNα = N_body + N_bt;   CPN = (M_body + M_bt)/CNα;   CMα = (VCG − CPN)·CNα

Rules:

- boattail exponents: β_N = VB and β_M = VB^0.8 below Mach 0.95; β_N = VB^1.5 and β_M = VB from Mach 0.95 on (the text does not give the threshold); β_N = β_M = √VB when VB > 1
- N_bt never adds: if it comes out positive, it is set to zero (a rule of the code, missing from the text; it only acts with a short ogive at supersonic speeds)
- if M_bt comes out positive, the whole boattail is discarded: CNα = N_body and M_bt = 0 (a rule of the code, missing from the text)
- the c11 term multiplies r·v; the text prints another variable there, a typographical error

What was not read:

- the continuation card of XC15 (Mach 1.2 to 5) was not printed: values recovered from the output tables
- the XC12 line is faded: cells decided by the tables

## 4. Yaw term of the axial force (CX2)

The term that, added to CNα, gives the yaw drag per sin² of the yaw.

| | |
|---|---|
| Columns | `CX2` |
| Data | XD |
| Listing statements | C213 |
| Pages | 85 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.cx2` |

Formulas:

- CX2 = d1 + d2·L + d3·R + d4·VB − CNα   (L and R as in the drag)

Rules:

- the yaw drag is CX2 + CNα, not CX2 (p. 15)

## 5. Magnus force and moment

The Magnus force and, for three angles of attack (1°, 2° and 5°), its center of pressure and the moment about the CG.

| | |
|---|---|
| Columns | `CYPA`, `CNPA`, `CPF1`, `CPF5`, `CNPA5` |
| Data | XE |
| Listing statements | C214–C231 |
| Pages | 85 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.magnus` |

Formulas:

- Y = e1·VL;   CYPA = Y − 0.1·VB
- for each angle, with e = e2 (1°), e3 (2°) or e4 (5°):   N = −Y·(e + 0.55·L + 0.8·(VN − 2.5)) + VL·VB/4.7
- CPF = −N/CYPA + Δ_lb;   moment = (VCG − CPF)·CYPA

Rules:

- Δ_lb = e5·(VL − 6) when VL > 6 (long-body term, missing from the text)
- at 1° come CPF1 and CNPA; at 5°, CPF5 and CNPA5; the value at 2° is computed and does not enter any printed column

What was not read:

- the first card of XE5 (Mach 0.01 to 1.75) was not printed: values recovered from the output tables

## 6. Magnus "polynomial coefficients" (CNPA3, CNPA5P)

Two printed columns that should fit a polynomial to the Magnus moment at three angles.

| | |
|---|---|
| Columns | `CNPA3`, `CNPA5P` |
| Data | — |
| Listing statements | C278–C281 |
| Pages | 86 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.magnus_polynomial_coefs` |

Formulas:

- D = CNPA(5°) − CNPA(1°)
- CNPA5P = ((D + 0.3) − 9·D)/0.0072
- CNPA3 = (D − 0.0001·CNPA5P)/0.01

Rules:

- the constants are those of a polynomial C1 + C3·δ² + C5·δ⁴ fitted at δ = 0.1 and 0.3, but the second point uses D + 0.3 instead of the value at 2°: the two columns carry a single degree of freedom and always obey CNPA3 + 0.1·CNPA5P = 3.75 (a defect of the original, reproduced)
- the program prints "CNPA5" for this column and "CNPA-5" for the moment at 5°; here they are CNPA5P and CNPA5

## 7. Pitch damping (CMQ)

Cmq + Cmα̇ in the qd/2V convention.

| | |
|---|---|
| Columns | `CMQ` |
| Data | XF |
| Listing statements | C232–C238 |
| Pages | 85 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.cmq` |

Formulas:

- λ = VL − 5;   g = VCG − 3
- K = f1 + f2·λ + f3·λ² + f4·g + f5·g·λ + f6·g·λ² + f7·g·VB + f8·VB
- CMQ = −5.093·K − Δ_lb

Rules:

- Δ_lb = f9·(VL − 6) when VL > 6 (long-body term, missing from the text)

What was not read:

- the second card of XF7 (Mach 1.1 to 2.5) was not printed: values recovered from the 5"/38 table

## 8. Roll damping (CLP)

Clp in the pd/2V convention, proportional to the length.

| | |
|---|---|
| Columns | `CLP` |
| Data | XG |
| Listing statements | C239 |
| Pages | 85 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.clp` |

Formulas:

- CLP = g1·VL/5.51

Rules:

- the divisor is a program constant that the text gives as 5.51, the length of the M437

## 9. Stability analysis

With diameter, mass, inertias and rifling twist: the spin, the gyroscopic and dynamic stability factors, and the frequencies and damping rates of the two yaw modes.

| | |
|---|---|
| Columns | `GYRO`, `SBAR`, `RECIP`, `SBAR5`, `RECIP5`, `SPIN`, `W1`, `W2`, `L1`, `L2`, `L15`, `L25`, `DELT`, `DISP` |
| Data | — |
| Listing statements | C240–C266 |
| Pages | 85–86 |
| Source of the reading | code and text (pp. 17–18) |
| Implementation | `aeroballistics.core.stability` |

Formulas:

- V = Mach·a (ft/s);   twist = TWIST·DGUN (inches per turn);   p = 2π·V/(twist/12) (rad/s)
- s_g = 1352.4·IX²/(ρ·IY·CMα·twist²·DIA³)   (IX, IY in lb·in²; lengths in inches)
- m = WGT/32.174;   d = DIA/12;   Ix = IX/(32.174·144);   Iy = IY/(32.174·144)   (foot and slug)
- k₁ = m·d²/Ix;   k₂ = m·d²/Iy
- s_d = 2·(CNα − CX + (k₁/2)·CNPA) / (CNα − CX − (k₂/2)·CMQ + (k₁/2)·CLP);   RECIP = 1/(s_d·(2 − s_d))   (SBAR5 and RECIP5 with the moment at 5°)
- σ = √(1 − 1/s_g);   ω₁,₂ = p·Ix/(2·Iy)·(1 ± σ)
- λ₁,₂ = (ρ·A/(4m))·[−CNα·(1 ∓ 1/σ) + (k₂/2)·(1 ± 1/σ)·CMQ ± (k₁/σ)·CNPA],   A = π·d²/4   (L15 and L25 with the moment at 5°)
- DELT = 6.28/(20·ω₁)
- DISP = (CNα − CX)·IY·(ω₁ − ω₂)·3.635/(CMα·WGT·DIA·V)

Rules:

- with no diameter (DIA = 0), there is no stability analysis
- with s_g < 1.001, only the Mach and s_g are printed
- the constant 1352.4 is the code's; the physics with g = 32.174 would give 1349.8 (+0.19 %)
- the text (p. 18) prints the sign of the first term of λ swapped; the code and the tables use the sign above

What was not read:

- DISP: the formula is the code's; the quantity depends on the report's reference 71 (Whyte 1970), unavailable

## 10. Printout

For each Mach, one line with the 14 aerodynamic coefficients and, with mass and rifling, one line with the 14 stability columns.

| | |
|---|---|
| Columns | — |
| Data | — |
| Listing statements | C282–C294 |
| Pages | 86 |
| Source of the reading | code |
| Implementation | `aeroballistics.core.format_table` |
