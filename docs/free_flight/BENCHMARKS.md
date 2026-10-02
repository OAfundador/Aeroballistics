# Benchmarks: SPIN-73 against free flight

Here the question is **"does SPIN-73 get reality right?"**, not "does the adaptation reproduce SPIN-73?" (that one is in [../VERIFICATION.md](../VERIFICATION.md)). In every case, the adaptation runs with the source's geometry, and the result is compared with the spark-range measurements, round by round, after converting them to the SPIN-73 convention.

```
python scripts/free_flight/benchmarks/compare.py
```

| File | Source | Projectile | Source convention |
|---|---|---|---|
| `m101_karpov1964.csv` | Karpov et al., BRL MR 1582 (1964), DTIC AD0454925 | 155 mm M101, full scale, 64 rounds | modern: qd/V, pd/V → ×2 |
| `m483a1_whyte1991.csv` | Whyte, BRL-CR-659 (1991), DTIC ADA235620 | 155 mm M483A1, 65 shots in 19 groups | **the same as SPIN-73** (qd/2V, pd/2V) |
| `m33_mccoy1990.csv` | McCoy, BRL-MR-3810 (1990), DTIC ADA219106 | .50 Ball M33, 16 rounds | modern; **CLα** instead of CNα; CPN measured from the base |
| `nato556_mccoy1985.csv` | McCoy, BRL-MR-3476 (1985), DTIC ADA162133 | 5.56 NATO SS-109, M855, L110, M856, 35 rounds | same |
| `match762_mccoy1988.csv` | McCoy, BRL-MR-3733 (1988), DTIC ADA205633 | 7.62 match M118, 190 gr and 168 gr Sierra, 39 rounds | same |
| `xm788_mccoy1980.csv` | McCoy, ARBRL-MR-03019 (1980), DTIC ADA086096 | 30 mm XM788, 16 rounds | same (and Clp with pd/V) |
| `x30mm_mccoy1982.csv` | McCoy, ARBRL-TR-03432 (1982), DTIC ADA121258 | 30 mm XM788E1 and XM789, 43 rounds | same |
| `t203_karpov1955.csv` | Karpov et al., BRL MR 956 (1955), DTIC AD0086528 | 175 mm T203, 90 mm models with boattail and with square base, 35 rounds | BRL **K notation**, as printed |
| `xm617_brandon1969.csv` | Brandon, BRL MR 1998 (1969), DTIC AD0857512 | 152 mm XM617, cone-cylinder, full scale, 14 rounds | modern, with **CNα** (not CLα); CPN from the base |

The CSVs are in `data/free_flight/`, and the conversions in `src/aeroballistics/conventions.py`. Each CSV carries in its header the source's own definitions and the doubtful cells.

## Result: SPIN-73 / measured ratio (means per Mach range)

| Coefficient | Range | M101 | M483A1 | .50 M33 |
|---|---|---|---|---|
| CX0 / CD | subsonic | 1.13 | **1.25** | 0.86 |
| | supersonic | 1.02 | 1.07 | 0.90 |
| CNα (CLα for the .50) | subsonic | 1.07 | 0.99 | 0.89 |
| | supersonic | 0.99 | 1.05 | 1.10 |
| CMα | subsonic | 1.01 | 1.10 | 0.94 |
| | supersonic | **0.99** | **1.01** | **0.79** |
| Cmq + Cmα̇ | subsonic | 0.31 | 1.04 | (measured ≈ 0) |
| | supersonic | 0.93 | 0.92 | 1.05 |
| Magnus (moment) | subsonic | opposite sign | — | 0.1 |
| | supersonic | 1.08 | 0.59 | ≈ 7 |
| Clp | supersonic | — | 0.98 | — |

SPIN-73's own probable error, according to the report's Table 1 (p. 28), is 0.12 to 0.17 in CMα, 0.06 to 0.11 in CNα, 0.007 to 0.009 in CX, 3.0 in Cmq and 0.12 to 0.18 in Magnus.

## Reading

- **Supersonic, artillery:** CMα, CNα, CX0 and Cmq within 8 % for both 155 mm shells, inside the probable error the report itself declares. The M101 was one of the projectiles in SPIN-73's database (reference 35 of the report). The M483A1, from 1975, was not.
- **.50 M33:** CMα 21 % low in the supersonic range, with the center of pressure 0.36 cal behind the measured one. It is a shape outside the pattern of artillery projectiles: a 1.1 cal cylinder, a 0.78 cal boattail and a 0.18 meplat. At Mach 1.2, the rule of card C209 (positive boattail moment) discards the whole boattail.
- **Subsonic:** SPIN-73's CX0 misses by −14 % to +25 % depending on the shape. For the M483A1, the +20 % does not depend on the ogive radius adopted (0.182 to 0.193 for OR from 3.6 to 12).
- **Subsonic Cmq and Magnus:** the scatter of the measurements themselves is as large as the value. The M101 report shows that the subsonic damping changes sign between the scale model and full scale. They are no use for calibrating anything.

In none of the three cases does the adaptation depart from what the 1973 SPIN-73 would print. For the M101, with the same input as p. 59, it reproduces the report's table. The deviations above belong to the original model.

## 5.56 mm NATO (`nato556_mccoy1985.csv`)

McCoy, BRL-MR-3476 (1985), DTIC ADA162133: SS-109, M855 and the L110 and M856 tracers, with 35 rounds. The convention is the same as for the .50: CLα, pd/V, qd/V, CPN from the base. The lengths, 4.1 to 5.2 calibers, are **inside** SPIN-73's range.

In the supersonic range, SPIN-73 is 4 to 7 % low in CD and gets CMα within 1–10 %. In the subsonic range, it underestimates CD by up to 33 % (M855), in the same direction as the missing scale (Reynolds number) effect that shows up in every small arm. The correction for that is in [CORRECTION.md](CORRECTION.md).

## 7.62 match, 30 mm, 175 mm T203 and 152 mm XM617

The CSVs keep the values as printed. CDδ², when the source only gives it in a plot, was read from the plot and is in the header (7.62 match: Figs. 21–23; 30 mm: Figs. 12 and 17, piecewise straight lines).

- **7.62 match** (M118, 190 and 168 gr Sierra; 3.98 to 4.31 cal, boattails of 9.5° to 13°): supersonic CMα 9 to 14 % below the measured value, as already happened with the .50 — long-boattail small-arms shapes are the ones SPIN-73 gets wrong in the moment. Supersonic CD 5 to 10 % low; subsonic 9 to 19 % low.
- **30 mm** (3.49 and 3.61 cal, conical tip, rotating bands, base without boattail): CMα and CPN within 0–7 % in every regime, CLα within 2–15 %. CD is 6 % low in the supersonic range and **5 to 16 % low in the subsonic range**, again the sign of scale (Reynolds).
- **175 mm T203, 90 mm model** (it is the M437 under development: the three dimensions of the sketch match the M437 card in SPIN-73): **CD within 1 %** and **supersonic CMα within 1 %**. The ogive radius is not dimensioned. With the M437's OR (25 cal) the CMα closes; with the 15.8 cal measured on the drawing, it would be 11 % low at Mach 1.15. That is exactly why the T203's CMα does not enter the correction fit (it would be circular): only CX0, which changes at most 2 % with the OR. The KN, taken from the trajectory deflection with a 12 % standard error, comes out 27 % above SPIN-73 in the supersonic range — the rounds that have it flew at 4.5–7.4° of yaw, where the normal force is no longer linear. The square-base version is only archived: with the 3.97 cal ogive and the radius not dimensioned, SPIN-73's CX0 changes by 15 % depending on the OR.
- **152 mm XM617, cone-cylinder** (3.15 cal, 14° cone, square base, light projectile): in the supersonic range, **CD, CMα, CNα and CPN within 0–2 %** of SPIN-73. In the transonic range, CMα 13 % high and CD 9 % low, with large scatter in the measurements themselves. Supersonic Cmq 42 % more damped in SPIN-73 than measured. The source closes CPN − CMα/CNα with the CG 0.022 cal behind the CG of the sketch; the comparison uses the sketch's.
- **Subsonic Cmq and Magnus** for the 7.62 match and the 30 mm: the source measures positive Cmq (dynamic instability at small yaw) and Magnus much more negative than SPIN-73. The source treats this as nonlinearity (cubic coefficients). No linear correction captures it.
