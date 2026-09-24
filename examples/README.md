# Examples

Every example runs straight from a fresh clone, with no installation step:

```bash
python examples/01_caso_m437.py
```

The scripts, their comments and their output are in Portuguese, like the rest of the code. Those with options accept `--help`. Anything they write goes to `output/exemplos/`, which is not versioned.

| Script | What it shows |
| --- | --- |
| `01_caso_m437.py` | The report's validation case, the 175 mm M437, from the geometry only: every column at the 17 Mach numbers, plus the stability analysis and the warnings that apply to this shape. The same as `spin73 --exemplo`. `--csv` saves the table. |
| `02_simulador_6dof.py` | The library inside a 6DOF simulator: the seven coefficients of McCoy's formulation (`CD`, `CLA`, `CYP`, `CNP`, `CLP`, `CMA`, `CMQ`, rates on pd/V) at any Mach number and angle of attack. `--csv` writes a flat `Mach` + seven-column table. |
| `03_unidades_e_massa.py` | Metric input from [entradas/m855_metrico.txt](entradas/m855_metrico.txt), with the optional CG and inertia estimate checked against the measured M855 values, and what the difference does to the gyroscopic stability factor. |
| `04_correcao_voo_livre.py` | The optional free-flight correction next to canonical SPIN-73, and the cross-validation that decided which of its pieces were accepted. |
| `05_programa_original.py` | The 1973 program as objects: which block produces each column, with its formulas, rules, `DATA` blocks and what could not be read. |

`entradas/` holds input cards in the `KEY = value` format that `spin73 --entrada` also reads: [m437.txt](entradas/m437.txt), the report's own card, and [m855_metrico.txt](entradas/m855_metrico.txt), in metric units with the mass estimate turned on.

**About the flat table from `02`.** It has no angle-of-attack dependence: `CD` is the zero-yaw drag and `CNP` is the Magnus moment slope at 1°. Where a simulator accepts functions of (Mach, α), use the `cd` and `cnp` functions shown in the script instead. The Magnus sign convention differs between sources, so check it against your simulator's definition.
