**English** | [Português](README.pt-BR.md)

# SPIN-73 reconstructed

A Python reconstruction of **SPIN-73** (R. H. Whyte, *SPIN-73, an Updated Version of the SPINNER Computer Program*, Picatinny Arsenal TR 4588, 1973; DTIC AD0915628, Distribution A — approved for public release).

SPIN-73 estimates the aerodynamic coefficients of a spin-stabilized projectile from its geometry alone, at 17 Mach numbers (0.01 to 5), and runs a stability analysis. The original code survives only as a Fortran listing printed in a scanned report. It was reconstructed here by reading the scan — the equations, the `DATA` blocks with the empirical constants, and the code itself — and checked against the 13 output tables the program printed in 1973.

**Result:** among the cells that took no part in any reading decision, 89 % are indistinguishable from the original and 95 % fall within ±1.5 units of the last printed digit (91 % and 97 % without the M1 case, whose page is duplicated in the scan and whose geometry does not close).

The code, its comments and the detailed notes are in Portuguese. Names that come from the 1973 program (input card fields, output columns) are kept as in the original.

## Contents

1. [How to use](#1-how-to-use)
2. [Inputs and outputs](#2-inputs-and-outputs)
3. [The canonical reproduction](#3-the-canonical-reproduction)
4. [Checks and results](#4-checks-and-results)
5. [Source documents and what was read](#5-source-documents-and-what-was-read)
6. [What could not be read](#6-what-could-not-be-read)
7. [What the reconstruction revealed](#7-what-the-reconstruction-revealed)
8. [What we do differently](#8-what-we-do-differently)
9. [Optional additions](#9-optional-additions)
10. [SPIN-73 against free-flight measurements](#10-spin-73-against-free-flight-measurements)
11. [Repository layout](#11-repository-layout)
12. [Limitations](#12-limitations)
13. [License and source](#13-license-and-source)

---

## 1. How to use

### Installation

From the repository root (Python 3.10 or newer; the only dependency is numpy):

```bash
pip install -e .
```

Without installing, run `python -m spin73` from inside `python/`.

### Command line

The report's validation case (175 mm M437):

```bash
spin73 --exemplo
```

Your own projectile, with the SPIN-73 input card (lengths in calibers, diameter in inches, inertias in lb·in², weight in lb, twist in calibers per turn):

```bash
spin73 --VL 5.0 --VN 2.0 --VB 0.4 --VCG 3.0 --OR 8 --DIA 1.0 --IX 0.5 --IY 4.0 --WGT 0.5 --TWIST 25 --csv output.csv
```

The same in metric units, estimating the missing CG and inertias (an optional addition):

```bash
spin73 --VL 4.05 --VN 1.90 --VB 0.40 --OR 7.9 --d-mm 5.69 --massa-g 4.05 --passo-pol 7 --estimar-massa
```

Or from a `KEY = value` file (examples in [python/exemplos/](python/exemplos/)):

```bash
spin73 --entrada python/exemplos/m855_metrico.txt
```

The first line of the output states the mode: `Modo: canônico (SPIN-73 de 1973)` (the canonical 1973 program) or the list of additions in use. `spin73 --help` lists every option. The option names are in Portuguese: `--entrada` input file, `--exemplo` example, `--massa-g` mass in grams, `--passo-pol` twist length in inches, `--estimar-massa` estimate mass properties, `--correcao` correction.

### As a library (for example, in a 6DOF simulator)

```python
import spin73

p = spin73.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
aero = spin73.Aerodinamica(p, convencao="moderna")   # canonical, in the modern convention
c = aero(mach)             # c.CD0, c.CDd2, c.CNa, c.Cma, c.Cmq_Cmad, c.Clp, c.Cmpa ... (scalar or array)
```

The aerodynamics is computed once, at construction; each call only interpolates in Mach. The full guide, with the optional additions and how to write a new correction, is [docs/BIBLIOTECA.md](docs/BIBLIOTECA.md) (in Portuguese).

## 2. Inputs and outputs

### The input card (Appendix B of the report)

Only the first four inputs are required. With them the full aerodynamic table is produced; with the five mass and twist inputs, the stability analysis too.

| Input | What it is | Unit | Needed? | Default | Affects |
|---|---|---|---|---|---|
| `VL` | overall length | calibers | **yes** | — | everything |
| `VN` | ogive (nose) length | calibers | **yes** | — | everything |
| `VB` | boattail length (0 = flat base) | calibers | **yes** | — | everything |
| `VCG` | CG measured from the **nose** | calibers | **yes**¹ | — | CMα, Magnus moment, Cmq |
| `OR` | ogive radius (1000 = conical nose) | calibers | recommended | 2·VN² | CX, CNα, CPN, CMα |
| `DM` | meplat (flat tip) diameter | calibers | recommended | 0.12 | CX, CNα, CPN, CMα |
| `BD` | rotating band diameter | calibers | optional | 1.02 | CX |
| `BOOM` | "boom length" of the original card | calibers | rarely | 0 | CX |
| `DIA` | diameter | inches | for stability | 0 (no stability) | stability |
| `IX`, `IY` | axial and transverse moments of inertia | lb·in² | for stability | — | stability |
| `WGT` | weight | lb | for stability | — | stability |
| `TWIST` | rifling twist | calibers per turn | for stability | — | stability |
| `TEMP` | air temperature | °F | optional | 59 | stability only |
| `DGUN` | bore diameter | inches | optional | = DIA | spin rate, in the stability analysis |

¹ Can be estimated from the geometry with the optional mass-property addition (section 9).

Every input also has a metric form (`D_MM`, `MASSA_G` in grams, `IX_GCM2`, `PASSO_MM` or `PASSO_POL` for the twist length per turn, `TEMP_C`, `CG_BASE` for the CG measured from the base...), in the input file, on the command line and in Python. Mach is not an input: the program always computes the report's 17 Mach numbers.

### Outputs

| Block | Columns |
|---|---|
| Aerodynamics (always) | `CX` zero-yaw axial force · `CX2` yaw term · `CNA` normal force · `CMA` pitching moment about the CG · `CPN` center of pressure (calibers from the nose) · `CYPA` Magnus force · `CNPA`, `CNPA5` Magnus moment at 1° and 5° · `CPF1`, `CPF5` Magnus center of pressure · `CNPA3`, `CNPA5P` Magnus polynomial · `CMQ` pitch damping · `CLP` roll damping |
| Stability (with mass and twist) | `GYRO` (s_g) · `SBAR`, `SBAR5` (s_d) · `RECIP`, `RECIP5` · `SPIN` · `W1`, `W2` (frequencies) · `L1`, `L2`, `L15`, `L25` (damping rates) · `DELT` · `DISP` |

**The report's convention** (pp. 7–8), in the classic NACA/BRL style: nondimensional rates **pd/2V and qd/2V**, derivatives per sin ᾱ, positions in calibers from the nose, moments about the CG. Modern sources (McCoy, PRODAS, CFD) use pd/V and qd/V, and their values are **half** of SPIN-73's for Cmq, Clp and Magnus. The yaw drag is CX2 + CNα, not CX2. `convencao="moderna"` performs the conversions (`python/spin73/convencoes.py`).

## 3. The canonical reproduction

The goal is to reproduce **what the 1973 program printed**, errors and defects included, not to improve it. Everything that changes results lives outside the core, as an optional addition.

- **Three sources inside the report.** The text gives the equations; the listing gives the `DATA` blocks with the empirical constants; the code shows what the program actually did. **Where text and code disagree, the code wins**: it is what generated the tables.
- **Every value read has a class.** *Verified*: a clear reading, or one confirmed by an independent identity. *Decided by the model*: chosen because it reproduces the tables. *Pending*: still open. The class and the evidence for each cell are in the modules `python/spin73/dados/x?_lidos.py`.
- **The dot-matrix printout confuses digits** (6/8, 1/3, 2/7, 4/9, 0/6, 5/9). Every ambiguous reading was decided by an identity that did not depend on it. In the output tables the identities are between **printed** columns: CMα = (VCG − CPN)·CNα, CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5) and CNPA3 + 0.1·CNPA5P = 3.75.
- **No circularity.** A value decided from a table is never used to validate that same table. `python/circularidade.py` flags, cell by cell, what became circular, and those cells are left out of the statistics.
- **Tolerance.** Errors are measured in units of the last printed digit. Within ±0.5 unit the result is indistinguishable from the original (which rounded at that digit); the project criterion is ±1.5 units (±0.0015 for 3-decimal columns).

## 4. Checks and results

### The report's validation case (175 mm M437, p. 65), starting from the geometry only

| Block | Columns | Reproduces the 1973 table |
|---|---|---|
| Axial force | CX | 17 of 17 Mach numbers (and 17 of 17 for the 5"/38) |
| Yaw axial force | CX2 | 12 of 17 (2 cells illegible in the scan; 3 with residuals of 0.007 to 0.02) |
| Normal force | CNA | 15 of 17 |
| Magnus | CYPA, CNPA, CPF1, CPF5, CNPA5, CNPA3, CNPA5P | 16 or 17 of 17 |
| Damping | CMQ, CLP | 17 of 17 |
| Center of pressure | CPN, CMA | independent test at only 4 Mach numbers for the M437 (see below) |
| Stability | GYRO, SBAR, RECIP, SPIN, W1, W2, λ, DELT, DISP | 15 to 17 of 17; the columns that depend on CMα are independent only at the same Mach numbers |

The M437 center of pressure matches at 14 of 17 Mach numbers, but at 13 of them the result is **circular**: the printed listing lost a `DATA` card (the continuation of XC15), and the M437 table was used to recover it. The independent check comes from two more tables with a boattail: the 5"/38 (p. 53) and the **105 mm XM380E5 (p. 50), transcribed in full and not used to decide any center-of-pressure `DATA`**. The program reproduces 16 of its 17 CPN values and 98 % of all its cells.

### Every case in the report

The 13 output tables (pp. 29 to 68) are transcribed in `python/tabelas/`, and the program runs with each table's printed input. There are 2718 legible cells: 1612 independent, 779 circular and 327 disambiguated by identities only.

| p. | Case | Independent | ≤ 0.5 unit | ≤ 1.5 units | Note |
|---|---|---|---|---|---|
| 29 | 20 mm M56A3 | 171 | 94 % | 99 % | meplat re-read: 0.260 |
| 32 | 20 mm 5 cal ANSR | 189 | 85 % | 99 % | |
| 35 | 20 mm 7 cal ANSR | 153 | 94 % | 99 % | |
| 38 | 20 mm 9 cal ANSR | 177 | 94 % | 99 % | header fully legible |
| 41 | 20 mm 10 cal cone-cylinder | 22 | 91 % | 100 % | VCG decided by the Magnus identities |
| 44/47 | M1 | 60 | 50 % | 50 % | page duplicated in the scan (section 6) |
| 50 | 105 mm XM380E5 | 217 | 93 % | 98 % | the cleanest test: almost nothing circular |
| 53 | 5"/38 NAVY | 180 | 95 % | 98 % | matched once card C205 was implemented |
| 56 | 5"/54 NAVY | 22 | 91 % | 96 % | heavily degraded page |
| 59 | 155 mm M101/107 | 32 | 78 % | 81 % | CPN and CMα off by 0.007 to 0.018 |
| 62 | 155 mm M549 | 29 | 83 % | 93 % | ogive re-read: 2.99 |
| 65 | 175 mm M437 | 317 | 89 % | 95 % | the only case with a stability analysis |
| 68 | 175 mm SRC | 43 | 77 % | 95 % | 5.5-caliber ogive: the only test of XA13–XA15 and XC17 |

By column, without the M1: Magnus, Cmq and Clp 97 to 100 % within ±0.5 unit; CX 87 %; CNα 77 %; CPN 79 %; CMα 52 % (82 % within the criterion — it accumulates the errors of CNα and CPN). Cell-by-cell detail in [validation/LEIAME.md](validation/LEIAME.md) (in Portuguese).

### Running the checks

The last line checks the 12 table transcriptions without the model, using only the identities between printed columns; it currently finds no violations.

```bash
python -m pytest -q python                  # 266 tests (and 3 skipped: columns not transcribed)
python validation/comparacao_erros.py       # every case, cell by cell
python python/tabelas/verificar_identidades.py 29 32 35 38 41 44 50 53 56 59 62 68
```

## 5. Source documents and what was read

### The report

Whyte, R. H. *SPIN-73, an Updated Version of the SPINNER Computer Program*. Technical Report 4588, Picatinny Arsenal, 1973 (DTIC AD0915628). What was read from each part:

| Part | Pages | Where it lives here |
|---|---|---|
| Nomenclature and conventions | 7–8 | `python/spin73/convencoes.py` |
| Text with the equations for each coefficient and for the stability analysis | up to p. 18 | `python/spin73/nucleo.py` (differences in section 7) |
| Table 1: probable error of SPIN-73 against experiment | 28 | cited in `python/experimental/benchmarks/` |
| 13 output tables | 29–68 | `python/tabelas/` (raw readings in `leituras/`) |
| Appendix B: the input card | 76–77 | `spin73.Projetil` |
| `DIMENSION` and the `DATA` blocks XA … XG | 79–81 | `python/spin73/dados/` |
| The code | 84–86, transcribed verbatim | `original/listing_p84-86.f` |

**Where the readings came from.** DTIC's high-resolution scan (96 JP2 pages of about 2600 × 3400 px; not versioned, see [fontes/LEIAME.md](fontes/LEIAME.md)). Several earlier readings, made from a lower-resolution scan, were corrected on it (for example, the XM380E5 ogive: 2.400 → 2.900). The tools are in `ferramentas/`: `recorte.py` (rotated crops with zoom and autocontrast), `pagina_pdf.py` (CCITT pages from scanned PDFs) and `pdf_paginas.py` with `jbig2.py` (DTIC "MRC" PDFs, which store the text in a JBIG2 mask; the decoder is pure Python).

### Supporting documents (all approved for public release)

| Document | Used for |
|---|---|
| Hitchcock, *Aerodynamic Data for Spinning Projectiles*, BRL Report 620 (AD-800 469) | cal .30 data, and the empirical inertia formulas used in the mass estimate |
| Piddington, BRL MR 1833, 1967 (AD815788) | the 7.62 NATO family: the first comparison with free flight |
| Karpov 1955 and 1964; Brandon 1969; McCoy 1980, 1982, 1985, 1988 and 1990; Whyte 1991 | free-flight measurements (section 10); the full list, with DTIC numbers, is in [fontes/LEIAME.md](fontes/LEIAME.md) |

## 6. What could not be read

| What | Why | What was done |
|---|---|---|
| **Three `DATA` cards**: the continuation of XC15 (center of pressure, Mach 1.2 to 5), the first card of XE5 (long-body Magnus) and the second card of XF7 (Cmq, Mach 1.1 to 2.5) | never printed: in each case the printout repeats a neighboring card in their place | recovered from the output tables, flagged *decided by the model* and left out of the validation |
| Faded or ambiguous `DATA` cells | the XC12 row, for example, is faded | decided from the tables, with the evidence recorded: 4 in XA, 7 in XB, 7 in XC, 4 in XD |
| **One whole output table** | pp. 44 and 47 of the scan are the same printout (same title, header and artifacts): the table of one of them (90 mm M71 or 105 mm M1) is missing | the "M1" case is recorded but kept out of the conclusions |
| Header digits | illegible or ambiguous in 10 of the 13 cases (the decided input for each is in `validation/resumo_por_caso.csv`) | each decided by a single column, which becomes circular for that case |
| Heavily degraded pages | 5"/54 (p. 56), M101 (p. 59), 20 mm 5 cal (p. 32) | few independent cells in them |
| The code on p. 83 | not yet transcribed; it holds the branch for boattails longer than 0.65 caliber | follows the report text; the output warns when that branch is used |
| Reference 71 (Whyte 1970) | not available | the `DISP` column is reproduced from the code's formula, without a physical interpretation |
| `XB10` | declared in `DIMENSION`, not found in the transcribed code | unused |

**Open residuals:** CPN at Mach 0.6 (0.002 to 0.004 caliber), the M101 CPN at Mach 1.2 (0.007 caliber), the Magnus center of pressure of the 175 mm SRC (+0.005) and the M437 CX2 at Mach 1.5, 1.75 and 2.5. Every reading, with its evidence, is in [docs/NOTAS_TRANSCRICAO.md](docs/NOTAS_TRANSCRICAO.md) (in Portuguese).

## 7. What the reconstruction revealed

Differences between the text and the code, and terms the text does not document:

- **A sign error in the text** for the damping rates λ (p. 18): the text prints −CNα(1 ± 1/σ); the code and the tables use −CNα(1 ∓ 1/σ).
- **The gyroscopic stability constant**: the code uses 1352.4 where the physics with g = 32.174 gives 1349.8 (+0.19 %).
- **Undocumented long-body terms**, active above 6 calibers: XE5 in the Magnus terms and XF9 in the pitch damping.
- **A13, A14 and A15** in the drag: the long-ogive term has three segments (breaks at 3.48 and 3.97 calibers); the text describes only the first.
- **The boattail is discarded** in the center of pressure when the boattail moment comes out positive, and the boattail normal force is discarded when it comes out positive (card C205, which only acts on short ogives at supersonic speeds).
- **CNPA3 and CNPA5**: the "Magnus polynomial coefficients" do not use the value computed at 2°; the program adds a fixed constant instead, so the two columns satisfy CNPA3 + 0.1·CNPA5 = 3.75 for any projectile. A defect of the original, reproduced.
- **The supersonic boattail exponent** already applies at Mach 0.95 (the text does not give the threshold; the code does).

## 8. What we do differently

The core reproduces the behavior of the 1973 program, defects included. The differences are in the interface, and they are documented:

- **Blank card fields.** In the original, a blank DM is 0, a blank BD is 1.00 and a blank TEMP is 0 °F. Here the defaults are DM = 0.12 and BD = 1.02 (the program's own "automatic dimensions" values) and TEMP = 59 °F. To reproduce a blank card, pass zero.
- **Column names.** The program prints "CNPA5" for the quintic coefficient and "CNPA-5" for the secant slope at 5°; here they are `CNPA5P` and `CNPA5`.
- **The CG may be missing** from the card: without it, the program asks for the CG or for the optional mass estimate.
- **Output** as a text table, a CSV file or a Python object, instead of a line printer. The original's rule of skipping the dynamic analysis when s_g < 1.001 is kept.
- **Everything that changes results is optional** and lives outside the core (section 9).

## 9. Optional additions

None is applied unless requested, and none changes the canonical output.

| Addition | What it does | What it changes | How to request it |
|---|---|---|---|
| Modern convention | pd/V, qd/V, CLα, CDδ² | presentation only (exact conversion) | `convencao="moderna"` |
| Metric units | mm, g, g·cm², °C, CG from the base | input only (exact conversion) | `spin73.unidades`, `--d-mm`, `--massa-g`... |
| Mass-property estimate | CG, mass and inertias missing from the card, from a homogeneous solid of revolution or from Hitchcock's formulas (BRL 620) | inputs that were missing | `spin73.massa`, `--estimar-massa` |
| Free-flight correction | drag adjusted for projectile size (Reynolds number), plus two pieces at the edge of the validation rule | coefficients | `correcoes="voo_livre"` or `"voo_livre:CX0"`, `--correcao` |
| Your own corrections | any object with `aplicar(table, projectile, context)` | coefficients | [docs/BIBLIOTECA.md](docs/BIBLIOTECA.md) |

**The mass-property estimate, validated against 20 projectiles with measured values** (with the measured mass given): for bullets, the CG is within ±0.12 caliber and the axial inertia within −5 % to +3 %. For shells, Hitchcock's formulas are within −11 % to +3 %, while the homogeneous solid underestimates by 20 to 27 %, because a shell's mass sits in its wall. Details in [python/experimental/massa/LEIAME.md](python/experimental/massa/LEIAME.md) (in Portuguese).

## 10. SPIN-73 against free-flight measurements

Section 4 asks whether the reconstruction reproduces SPIN-73. This section asks **whether SPIN-73 matches reality**. "Free flight" is the test in which the projectile is actually fired through an instrumented aeroballistic range, and the coefficients are extracted from its measured motion. Nothing is fired here: the measurements come from published reports, transcribed round by round.

- **Benchmarks** ([python/experimental/benchmarks/](python/experimental/benchmarks/LEIAME.md)): 155 mm M101 and M483A1, .50 M33, 5.56 NATO, 7.62 match, 30 mm XM788/XM788E1/XM789, 175 mm T203 (90 mm model) and 152 mm XM617 (a cone-cylinder). At supersonic speeds, SPIN-73 gets CMα, CNα and CX0 within a few percent for the artillery projectiles and the cone-cylinder, but underestimates CMα for bullets with long boattails (.50: 21 %; 7.62 match: 9 to 14 %). At subsonic speeds, CX0 is off by −33 % to +25 %, depending on shape and size.
- **Empirical correction** ([python/experimental/correcao/](python/experimental/correcao/LEIAME.md)): ten projectile groups and 1391 measured values. A correction is accepted only if it reduces the error on projectiles the fit has not seen (leave-one-group-out cross-validation). Drag is the robust piece: the supersonic error drops from 6.6 % to 4.8 % and the subsonic error from 19.3 % to 15.1 %, improving 7 of 9 or 10 groups. CMα and Magnus do not improve with any simple form and are left as in SPIN-73.
- **Recalibration with the 7.62 NATO family** (BRL MR 1833) and Hitchcock's compendium: [python/experimental/README.md](python/experimental/README.md).

None of this changes the reconstructed program.

## 11. Repository layout

| Directory | Contents |
|---|---|
| `python/spin73/` | **The library** (module table below) |
| `python/tabelas/` | The 13 output tables from 1973, with their printed input; raw readings with the ambiguous glyphs marked in `leituras/` |
| `python/reconstrucao_*/` | The reconstruction of each `DATA` block, with the tests and analyses that decided each reading |
| `python/exemplos/` | Example input files |
| `python/experimental/` | Comparisons with measurements: `benchmarks/`, `correcao/`, `massa/`, `hitchcock/` and the 7.62 NATO recalibration — **kept separate** from the reconstruction |
| `validation/` | Every case in the report, run and compared cell by cell |
| `original/` | Verbatim transcription of the Fortran listing (pp. 84–86) |
| `docs/` | Transcription notes (every reading, with its evidence) and the library guide |
| `ferramentas/` | Scan-reading tools: crops, PDF pages, JBIG2 decoder |
| `fontes/` | The PDFs and the scan (not versioned; see `fontes/LEIAME.md`) |

| Module | Contents | |
|---|---|---|
| `spin73.nucleo` | the equations, `tabela()`, `estabilidade()`, the `Projetil` input card | canonical |
| `spin73.dados` | the `DATA` blocks XA…XG, with the provenance of each value | canonical |
| `spin73.aero` | `Aerodinamica`: coefficients at any Mach number, for simulators | canonical without options |
| `spin73.convencoes` | report convention ↔ modern convention | addition |
| `spin73.unidades` | inputs in metric units | addition |
| `spin73.massa` | CG, mass and inertia estimate | addition |
| `spin73.correcoes` | output corrections and the interface for writing new ones | addition |
| `spin73.cli` | command line | — |

## 12. Limitations

The output carries warnings specific to each geometry (`spin73.avisos(p)`). The main ones:

- **Center of pressure from Mach 1.2 to 5**: it depends on the XC15 card, recovered from the tables. Three tables with a boattail agree (M437, 5"/38 and XM380E5, with residuals up to 0.0025 caliber); the M101 is still 0.007 caliber off at Mach 1.2. The stability columns inherit these uncertainties, because they depend on CMα.
- **Boattails longer than 1 caliber**: that branch of the code has been read, but no 1973 table validates it. The branch for ogives longer than 3 calibers has a single table (175 mm SRC).
- **Shapes outside the model**: SPIN-73 describes an ogive (or cone) with a meplat, a cylinder, and a conical boattail or a flat base. A rounded nose, a stepped (heel) base or a rounded base cannot be represented; a rounded base is entered as a conical frustum.
- **Against reality**, the error is that of the 1973 model: Table 1 of the report gives a probable error of 0.12 to 0.17 in CMα against experiment (section 10).

## 13. License and source

The code in this repository is under the MIT license (see [LICENSE](LICENSE)). The original report was written by the Armament Systems Department of General Electric under U.S. Army contract DAAA21-73-C-0033, for Picatinny Arsenal, and was approved for public release, distribution unlimited (Distribution A), by ARDEC in 2010. This repository does not redistribute the report; it is available from DTIC. This is an independent reconstruction for research purposes, not affiliated with or endorsed by the U.S. Army or General Electric.

Whyte, R. H. *SPIN-73, an Updated Version of the SPINNER Computer Program*. Technical Report 4588, Picatinny Arsenal, Dover, NJ, November 1973. DTIC AD0915628. Distribution A: approved for public release.
