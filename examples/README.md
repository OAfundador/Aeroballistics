# Examples

Every example runs straight from a fresh clone, with no installation step:

```bash
python examples/01_m437_case.py
```

Those with options accept `--help`. Anything they write goes to `output/examples/`, which is not versioned.

| Script | What it shows |
| --- | --- |
| `01_m437_case.py` | The report's validation case, the 175 mm M437, from the geometry only: every column at the 17 Mach numbers, plus the stability analysis and the warnings that apply to this shape. The same as `aeroballistics --example`. `--csv` saves the table. |
| `02_6dof_simulator.py` | The library inside a 6DOF simulator: the seven coefficients of McCoy's vector formulation (`CD`, `CLA`, `CYP`, `CNP`, `CLP`, `CMA`, `CMQ`, rates on pd/V) at any Mach number and angle of attack, with `CD` and `CLA` projected exactly from body to wind axes. `--input` takes any card; `--npz` writes the (Mach × α) grid a simulator reads directly; `--csv` writes a flat `Mach` + seven-column table. |
| `03_units_and_mass.py` | Metric input from [inputs/m855_metric.txt](inputs/m855_metric.txt), with the optional CG and inertia estimate checked against the measured M855 values, and what the difference does to the gyroscopic stability factor. |
| `04_free_flight_correction.py` | The optional free-flight correction next to canonical SPIN-73, and the cross-validation that decided which of its pieces were accepted. |
| `05_original_program.py` | The 1973 program as objects: which block produces each column, with its formulas, rules, `DATA` blocks and what could not be read. |

`inputs/` holds input cards in the `KEY = value` format that `aeroballistics --input` also reads: [m437.txt](inputs/m437.txt), the report's own card, [5in38_navy.txt](inputs/5in38_navy.txt), the 5"/38 of Table 10, and [m855_metric.txt](inputs/m855_metric.txt), in metric units with the mass estimate turned on.

**About the outputs of `02`.** The `--npz` grid holds `mach_grid` (100 Mach numbers from 0.01 to 5), `alpha_grid` (101 angles from −10° to +10°, in radians), `CD`, `CLA` and `CNP` over (Mach × α) and the other four over Mach, under the names above — plain NumPy arrays that a simulator reading tabulated grids can load as they are. The flat `--csv` table has no angle-of-attack dependence: `CD` is the zero-yaw drag and `CNP` is the Magnus moment slope at 1°; it is for checking, not for flying. The conversion to the seven lives in the example, not in the library, because it depends on how the simulator writes its equations: the script's docstring derives it term by term, including the Magnus sign.
