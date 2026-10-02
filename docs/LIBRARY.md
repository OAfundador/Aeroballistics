# Using SPIN-73 as a library

## Installation

At the repository root:

```
pip install -e .
```

`-e` installs in editable mode: your code can see the `aeroballistics` package in `src/aeroballistics/`, and any change in the repository takes effect at once, without reinstalling. The only dependency is numpy.

## In a 6DOF simulator

```python
import numpy as np
import aeroballistics

p = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DM=0.12,
                      DIA=0.224, name="M855")          # calibers; DIA in inches

aero = aeroballistics.Aerodynamics(p,
                           corrections="free_flight",  # or None for the 1973 SPIN-73
                           convention="modern")        # or "spin73"

# inside the integration loop
c = aero(mach)                 # scalar or array
CD = c.CD0 + c.CDd2 * np.sin(alpha) ** 2  # small yaw; the exact projection is in examples/02
Cmpa = aero.magnus_moment(mach, alpha)   # secant Magnus, between 1° and 5°
```

The seven coefficients of McCoy's vector form, with CD and CLA projected exactly from body to
wind axes, and the (Mach × α) grid a simulator reads directly are in
[examples/02_6dof_simulator.py](../examples/02_6dof_simulator.py) (`--npz`).

The example uses the optional free-flight correction; without `corrections`, it is the 1973 program.

The aerodynamics is computed **once**, in the constructor, at the program's 17 Mach numbers. Each call only does linear interpolation in Mach (`numpy.interp`), so it is cheap enough for the integration loop. Outside 0.01 to 5, the default is to use the end value (`out_of_range="clamp"`); the alternatives are `"nan"` and `"error"`.

### Available coefficients

| `convention="spin73"` | `convention="modern"` | Meaning |
|---|---|---|
| `CX0` | `CD0` | zero-yaw drag |
| `CX2` | `CDd2` = CX2 + CNα | yaw drag, per sin²α |
| `CNA` | `CNa`, `CLa` = CNα − CD0 | normal force / lift, per sin α |
| `CMA` | `Cma` | pitching moment about the CG, per sin α (positive overturns) |
| `CPN` | `CP_nose`, `CP_base` | center of pressure, calibers |
| `CMQ` (qd/2V) | `Cmq_Cmad` (qd/V) = CMQ/2 | pitch damping, Cmq + Cmα̇ |
| `CLP` (pd/2V) | `Clp` (pd/V) = CLP/2 | roll damping |
| `CYPA` (pd/2V) | `CNpa` (pd/V) | Magnus force |
| `CNPA`, `CNPA5` (pd/2V) | `Cmpa`, `Cmpa_5deg` (pd/V) | Magnus moment at 1° and 5° (secant) |
| `CPF1`, `CPF5` | `CPmagnus_nose` | center of pressure of the Magnus force, calibers from the nose |

The moments are about the CG in the `Projectile` (`VCG`, in calibers from the nose). Details of the conversions in `src/aeroballistics/conventions.py`.

### Inputs in other units

The `Projectile` is the SPIN-73 card: calibers, inches, pounds, lb·in² and °F. `aeroballistics.units` builds the same card from metric units (exact conversion, nothing more):

```python
p = aeroballistics.units.projectile(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12,
                            D_MM=5.69, MASS_G=4.05, IX_GCM2=0.1426, IY_GCM2=1.150,
                            TWIST_IN=7, TEMP_C=15, CG_BASE=1.54)
```

| Key | Unit | Becomes |
|---|---|---|
| `D_MM` | mm | `DIA` |
| `MASS_G`, `MASS_KG` | g, kg | `WGT` |
| `IX_GCM2`, `IY_GCM2`, `IX_KGM2`, `IY_KGM2` | g·cm², kg·m² | `IX`, `IY` |
| `TWIST_MM`, `TWIST_IN` | one turn of the rifling, mm or inches | `TWIST` (calibers per turn) |
| `TEMP_C` | °C | `TEMP` |
| `CG_BASE` | CG from the **base**, calibers | `VCG` = VL − CG_BASE |
| `DGUN_MM` | mm | `DGUN` |

The same keys work in the command-line input file (`aeroballistics --input`), and each one has an option (`--d-mm`, `--mass-g`, `--cg-base`...).

### When the CG, mass or inertias are missing

`aeroballistics.mass` estimates what the card does not have, from the geometry. It never replaces a value that was given.

```python
p = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12)   # no VCG, weight, inertias
p = aeroballistics.mass.complete(p, "solid", mass_g=4.05, d_mm=5.69)       # fills in VCG, WGT, IX, IY
print(aeroballistics.mass.estimate(p, "solid", mass_g=4.05, d_mm=5.69))    # what was estimated
```

| Method | What it is | When to use it |
|---|---|---|
| `"solid"` | homogeneous solid of revolution with the card's geometry | bullets; the only one that gives the CG without the mass, and the mass from the density (`density=` in kg/m³ or `material="lead"`) |
| `"bullet"` | Hitchcock's empirical formulas (BRL 620) for .30 and .50 bullets | bullets, with the mass |
| `"shell"` | the same, for high-explosive shells | hollow shells, with the mass |

Against 20 projectiles with measured values, given the measured mass: for bullets, the CG lands within ±0.12 caliber and the axial inertia within −5 % to +3 % (`solid`). For shells, `shell` lands within −11 % to +3 %; `solid` underestimates by 20 to 27 %, because a shell's mass is in the wall. Tracers miss the CG by 0.2 to 0.45 caliber. Details in [MASS.md](MASS.md).

## Choosing the model

| What changes | How |
|---|---|
| Nothing: the 1973 program | `Aerodynamics(p)` |
| Full free-flight correction | `corrections="free_flight"` |
| Only part of it | `corrections="free_flight:CX0"` or `"free_flight:CX0,CNA"` |
| A correction of your own | `corrections=MyCorrection()` or a list, applied in order |
| Other `DATA` blocks | `data=DataBlocks(...)` (for example, recalibrated constants) |

`aero.describe()` says what was applied; `aero.original_table` keeps the uncorrected output, for comparison.

Not every piece of the free-flight correction is equally firm. `corrections.FreeFlight().validation()` returns, per coefficient and regime, the error on the left-out projectile groups and `worst_ratio`, how much the most harmed group got worse (the acceptance rule cuts at 2). **CX0** is the robust piece: it improves 7 of 9–10 groups in all three regimes and none gets worse by more than 1.5×. The other accepted pieces passed close to the limit, which is why `"free_flight:CX0"` is the conservative choice.

## Writing a new correction

A correction is any object with `name` and `apply(t, p, ctx)`. `t` is the table in the SPIN-73 convention: an array of 17 values per column, with the columns of `aeroballistics.table`. `ctx.d_mm` is the actual diameter, when there is one.

```python
from aeroballistics import corrections

class SmallerMagnus(corrections.Correction):
    name = "smaller_magnus"
    description = "Magnus moment × 0.8 in the supersonic range"

    def apply(self, t, p, ctx):
        out = corrections.base.copy_table(t)
        sup = t["MACH"] >= 1.25
        out["CNPA"][sup] *= 0.8
        out["CNPA5"][sup] *= 0.8
        return out

corrections.register("smaller_magnus", SmallerMagnus)     # optional: call it by name
aero = aeroballistics.Aerodynamics(p, ["free_flight", "smaller_magnus"])
```

The correction does not need to take care of the derived columns. After all the corrections, the library recomputes:

- CPN = VCG − CMα/CNα;
- CPF1 and CPF5 from the Magnus;
- CX2, preserving the yaw drag CX2 + CNα;
- the stability analysis, if the projectile has mass and rifling twist.

## What is what

| Module | Contents | Canonical or addition |
|---|---|---|
| `aeroballistics.core` | equations, `table()`, `stability()`, the `Projectile` card | **canonical**: it is the program |
| `aeroballistics.data` | `DATA` blocks XA..XG, with the provenance of each value | **canonical**: it is the program |
| `aeroballistics.aero` | `Aerodynamics`, the interface for simulators | with no options, canonical |
| `aeroballistics.program` | the original program as objects (`SPIN73.from_column("CMA")`, `block.compute(p)`) | documentation |
| `aeroballistics.conventions` | output in the modern convention | addition: exact conversion |
| `aeroballistics.units` | input in metric units | addition: exact conversion |
| `aeroballistics.mass` | estimate of CG, mass and inertias | addition: changes inputs that were missing |
| `aeroballistics.corrections` | corrections of the coefficients and the interface for writing new ones | addition: changes outputs, only if asked for |
| `aeroballistics.cli` | command line | says in the header whether the output is canonical or has additions |

The corrections are **fitted** in `scripts/free_flight/correction/`, with cross-validation leaving one group of projectiles out (see [free_flight/CORRECTION.md](free_flight/CORRECTION.md)). The fit writes `src/aeroballistics/corrections/free_flight.json`, which the library only reads. To redo the fit after adding data:

```
python scripts/free_flight/correction/fit_correction.py
```
