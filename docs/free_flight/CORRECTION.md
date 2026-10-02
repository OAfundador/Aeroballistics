# Empirical correction of SPIN-73 with free flight

The reconstructed SPIN-73 reproduces the 1973 program, errors included. Here it is corrected with spark-range measurements, **without changing the program**: the correction starts from the SPIN-73 table and adjusts what the data show can be adjusted.

```
python scripts/free_flight/correction/fit_correction.py   # validates, fits and writes src/spin73/corrections/free_flight.json
```

The fit lives in `scripts/free_flight/correction/`; the application is in the library, as an optional correction (off by default):

```python
import spin73
aero = spin73.Aerodynamics(p, "free_flight", d_mm=5.69)        # everything that was accepted
aero = spin73.Aerodynamics(p, "free_flight:CX0", d_mm=5.69)    # only the drag (the robust piece)
```

`apply_correction.py` still exists as a shortcut (`apply_correction.corrected_table(p, d_mm)`).

## Data

`flight_data.py` gathers ten groups of projectiles, with 1391 measured values, all converted to the SPIN-73 convention (pd/2V, qd/2V, CNα and not CLα, CPN from the nose, CX0 at zero yaw):

| Group | Projectiles | Source | Diameter | Shape |
|---|---|---|---|---|
| 762 | M-80, M-59, M-61, M-62 | BRL MR 1833 (Piddington 1967) | 7.82 mm | ogive-cylinder-boattail |
| 556b | SS-109, M855 | BRL-MR-3476 (McCoy 1985) | 5.69 mm | same |
| 556t | L110, M856 (tracers not lit) | same | 5.69 mm | long, rounded base |
| 50 | .50 Ball M33 | BRL-MR-3810 (McCoy 1990) | 12.95 mm | long boattail |
| m101 | 155 mm M101 | BRL MR 1582 (Karpov 1964) | 155 mm | shell, rotating band |
| m483 | 155 mm M483A1 | BRL-CR-659 (Whyte 1991) | 154.7 mm | compound ogive |
| 762m | M118, 190 gr and 168 gr Sierra | BRL-MR-3733 (McCoy 1988) | 7.82 mm | match, boattail of 9.5° to 13° |
| 30 | XM788, XM788E1, XM789 | ARBRL-MR-03019 (McCoy 1980), ARBRL-TR-03432 (1982) | 29.92 mm | short (3.5 cal), conical tip, base without boattail |
| t203 | 175 mm T203, 90 mm model (CX0 only) | BRL MR 956 (Karpov 1955) | 90 mm | the shape of the M437 |
| xm617 | 152 mm XM617 | BRL MR 1998 (Brandon 1969) | 152 mm | **cone-cylinder**, square base |

**Check of the transcription and the conversions:** CMα = (VCG − CPN)·CNα closes in 152 of 154 rounds using measured values only (and the rounds of the 7.62 match and the 30 mm, within 2 %). This catches a CLα taken for CNα, a CPN measured from the base treated as from the nose, or a misread digit. The two exceptions are from the 7.62 NATO, which the source already gives with a scatter of 0.02 in. in the CG. The XM617 stays out of this count: the source itself closes with the CG 0.022 cal behind the CG of the sketch (see the CSV).

**Yaw drag:** it comes from the source in all the new groups — as a number (5.56; T203; XM617) or read from a plot (7.62 match, 30 mm). With CDδ² from a plot or only as a mean, CX0 is only taken from rounds with yaw up to 5°. For the .50 and the M101, it comes from SPIN-73 itself (CX2 + CNα).

**What was left out and why:** the square-base version of the T203 and the T203's CMα/CNα (ogive radius not dimensioned; the CX0 of the boattail model changes at most 2 % with it), rounds above 10.5° of yaw (the coefficient stops being linear), the .22 LR (stepped base), the 105 mm M1 (ogive not dimensioned) and the 20 mm Navy (plots only). Details in `sources/README.md` and in the CSV headers.

## What the correction may use

The choice was made before looking at the errors. **SPIN-73 already models the geometry**, and its constants were fitted for that. **What it lacks is scale:** a 5.56 mm bullet and a 155 mm shell with the same shape come out with the same coefficients, but the shell's Reynolds number is 25 times larger. Hence:

- **CX0:** the correction is the skin-friction law (Prandtl–Schlichting with van Driest compressibility, the same form as MC DRAG), with the wetted area computed from the geometry. The only parameter per regime is the reference length `L_ref`, embedded in SPIN-73's constants (`reynolds.py`).
- **CNα, CMα, Cmq and Magnus:** the correction can be a constant bias, a bias proportional to log d (scale) or none.
- **CPN:** not corrected separately. It comes from the corrected CMα and CNα, CPN = VCG − CMα/CNα, so that the three stay consistent.

## How it is decided what goes in

**Nested leave-one-group-out** cross-validation: the choice of the form is also made without the left-out group, so the measured error is that of a projectile the fit never saw. Each group weighs the same in the fit and in the metric.

A correction goes into the final model only if, on the left-out groups, it meets all three conditions:

1. the mean error is smaller than SPIN-73's;
2. it improves more than half of the groups;
3. no group has its error more than doubled.

Criterion 3 was added after seeing the transonic Cmq. It passed 1 and 2 (87 % → 75 %, 4 of 6 groups), but made both 155 mm shells worse (M483A1: 35 % → 126 %). It is recorded for transparency.

## Result (`docs/results/correction.txt`)

Prediction error on **unseen** groups: RMS per group, mean across groups. "Worst" is the largest ratio between the corrected error and SPIN-73's on a left-out group (criterion 3 rejects above 2).

| Coefficient | Regime | SPIN-73 | Corrected | Groups improved | Worst | Decision |
|---|---|---|---|---|---|---|
| CX0 | subsonic | 19.3 % | **15.1 %** | 7/9 | 1.46 | accepted |
| CX0 | transonic | 10.7 % | **8.2 %** | 7/10 | 1.43 | accepted |
| CX0 | supersonic | 6.6 % | **4.8 %** | 7/10 | 1.21 | accepted |
| CNα | subsonic | 13.2 % | 10.7 % | 5/9 | 1.97 | accepted, at the limit |
| CNα | transonic | 11.2 % | 9.8 % | 7/9 | 2.01 | rejected, at the limit |
| CNα | supersonic | 8.3 % | 8.8 % | 0/9 | | rejected |
| CMα | all | 10–12 % | worse | 0–3/9 | | rejected |
| Cmq | transonic | 90 % | 72 % | 6/9 | 1.41 | accepted |
| Cmq | sub, supersonic | 205 %, 24 % | worse | 0–1 | | rejected |
| Magnus | all | | worse in sub and supersonic | ≤ 5/9 | ≥ 1.7 | rejected |
| CPN (derived) | subsonic | 0.28 cal | 0.26 cal | 4/8 | | consequence |

Final model, fitted on the ten groups:

- **CX0, reference length of the friction:** 0.20 m subsonic, 0.68 m transonic and 0.82 m supersonic. A 5.56 mm bullet gets +0.020 to +0.027 in CX0; a 30 mm, +0.005 to +0.011; a 155 mm shell, −0.010 subsonic and practically nothing from the transonic range on.
- **Subsonic CNα:** × (1 + 0.121 − 0.116·log₁₀(d/10 mm)): +15 % at 5.69 mm, −2 % at 155 mm.
- **Transonic Cmq:** × (1 − 0.743 + 0.667·log₁₀(d/10 mm)): the damping falls to 10–20 % of SPIN-73's for small arms, to 57 % for the 30 mm and stays the same (+5 %) for the 155 mm.

## Reading

- **Drag is where the correction pays off, and it is the only firm piece.** SPIN-73 does not know the projectile's size: it underestimates the CX0 of small arms and of the 30 mm (subsonic, up to 16 % for the 30 mm, 19 % for the 7.62 match and 33 % for the M855) and overestimates that of the 155 mm shells, exactly the sign of the friction law. With the new groups, the correction went from improving 4 of 6 groups to 7 of 9–10, and no group gets worse by more than 1.5×.
- **The other pieces are at the limit of the rule.** With six groups, the sub- and transonic CNα were accepted; with eight, the subsonic one fell (the 7.62 match, of the same caliber as the 7.62 NATO and of another shape, doubled the error); with ten, it came back at 1.97× and the transonic one fell at 2.01×. The transonic Cmq was rejected with six groups and accepted with eight and with ten. The rule was not changed after seeing this; the margin is recorded in the JSON (`worst_ratio`), and `"free_flight:CX0"` is the conservative choice in the library.
- **CMα and Magnus are not corrected by scale.** The errors belong to each shape: in the supersonic range, CMα 9 to 14 % low for the 7.62 match and 21 % for the .50, and within 1–2 % for the 152 mm cone-cylinder and the T203. No scale correction helps, and more shapes (ten groups now) did not change that.
- **The subsonic Cmq and Magnus of the small arms and the 30 mm** are nonlinear in the source itself (Cmq measured positive at small yaw; cubic coefficients), something a linear coefficient does not represent.

## Limits

- Ten groups, seven distinct diameters: the scale correction was fitted between 5.69 and 155 mm and should not be extrapolated outside that.
- **Assumptions in the inputs:** the meplat of the 5.56 mm bullets (DM = 0.12) is not dimensioned; the ogive radius of the 7.62 (9.74 cal) is uncertain; the rounded boattails of the tracers go in as a cone frustum.
- **Assumptions in the inputs (new groups):** 30 mm with the 17° conical tip inside the ogive length (SPIN-73 only describes ogive + meplat) and rounded base as a square base; 30 mm rotating bands with BD = 1.02 (not dimensioned); T203 with the OR, DM and BD of the M437 card.
- **Yaw drag:** see "Data". For the .50 and the M101 it comes from SPIN-73 itself (CX2 + CNα); at the yaws of those rounds, the effect is 1 to 3 % in CX0.
