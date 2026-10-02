# Mass estimate: validation

SPIN-73 takes the CG, the weight and the inertias as input. `aeroballistics.mass` is an **optional addition** that estimates them when they are missing. `scripts/mass/validate.py` measures how much the estimate misses, against projectiles with measured and published mass, CG and inertias.

```
python scripts/mass/validate.py      # full table; copy in docs/results/mass.txt
```

## Methods

| Method | What it is | Needs |
|---|---|---|
| `solid` | homogeneous solid of revolution with the card's contour (ogive of radius OR with meplat, cylinder, conical boattail), integrated numerically | only the geometry for the CG; mass or density for the rest |
| `bullet` | BRL empirical formulas for .30 and .50 bullets (Hitchcock, BRL 620, p. 9, citing BRL X-113): CG at 0.400 L from the base, A = 0.115 m d², B = 0.5 A + 0.0543 m L² | mass |
| `shell` | the same for high-explosive shells: 0.375 L, A = 0.140 m d², B = 0.5 A + 0.0594 m L² | mass |

A = axial inertia; B = transverse, about the CG; L = length; d = diameter; m = mass.

## Data

Twenty projectiles, from 5.56 mm to 175 mm, with the sources in the header of `validate.py`. The measured mass goes in as data: it is what is almost always known. What is tested is its **distribution**.

Three groups need care when reading:

- **Tracers** (L110, M856, Tracer M1): the tracer composition at the base is light, and the actual CG sits 0.2 to 0.45 cal ahead of a homogeneous solid's. No method based on the geometry alone gets this right.
- **Hitchcock's cal .30** (marked with `*`): they are from the same family of bullets the `bullet` formulas came from. For that method, they are not an independent test.
- **Special cases**: the XM617 is a low-density projectile, and the T203 is a 90 mm ballistic *slug* with its mass concentrated at the center. Neither is a typical shell.

## Result

Estimated/measured ratio, with the measured mass as data:

| Class | Method | CG (error) | Ix | Iy | s_g (∝ Ix²/Iy) |
|---|---|---|---|---|---|
| bullets (SS-109, M855, M118, 190 and 168 Sierra, .50 M33) | `solid` | ±0.12 cal | 0.95–1.03 | 1.03–1.20 | 0.83–1.03 |
| | `bullet` | ±0.12 cal | 1.03–1.11 | 1.03–1.14 | 0.99–1.19 |
| shells (30 mm ×3, M437, M101, M483A1) | `solid` | up to 0.20 cal | 0.73–0.81 | 0.90–1.32 | 0.50–0.66 |
| | `shell` | up to 0.14 cal | 0.89–1.03 | 0.98–1.38 | 0.72–0.95 |

## Reading

- **For bullets, both methods work**, and `solid` has the advantage of giving the CG without the mass and the mass from the density. The effective density of the measured jacketed bullets lies between 9.3 and 10.3 g/cm³ (the .50 M33 is at 7.7).
- **For shells, use `shell`.** A shell is hollow: the mass is in the wall, and the homogeneous solid underestimates the axial inertia by 20 to 27 %. Since the gyroscopic factor goes with Ix², the error in it reaches 50 %.
- **Iy is the least reliable**, above all in long projectiles with an internal payload (M483A1, which carries submunitions: +32 % with the solid and +38 % with Hitchcock).

## Limits

The contour has no rotating band, cannelure, cavity, or rounded tip or base (a rounded base goes in as a cone frustum). The boattail angle is not a SPIN-73 input: the default is 8°, and it can be given (`bt_angle`) or replaced by the base diameter (`db`). When measured CG and inertias exist, they should be used: the estimate only fills in what the card does not have.
