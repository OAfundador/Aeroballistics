"""SPIN-73 output tables transcribed from the report, one per file in `data/tables_1973/`.

Each CSV carries, in comment lines, the input printed in the table header and the cells that
required a decision:

    # input: VL=5.580 VN=2.900 ...                     geometry and mass (Projectile arguments)
    # decide: VN 1.40 2.00 CNA | reason                 illegible input: decided by the column
                                                        given, within the interval; that column
                                                        becomes CIRCULAR in this table
    # identity: COLUMN MACH reading -> value | reason   resolved by an identity between printed
                                                        columns (out of the counts)
    # doubtful: COLUMN MACH reading | reason            left empty in the CSV

    tb = load(50)
    tb.projectile()        # Projectile with the printed input
    tb.columns["CPN"]      # array of 17 values (NaN = illegible)
"""
import csv
import glob
import os
import re
from dataclasses import dataclass, field

import numpy as np

import paths
import aeroballistics as s

DIR = str(paths.TABLES_1973)


@dataclass
class PrintedTable:
    page: int
    name: str
    file: str
    inputs: dict
    columns: dict
    identity: dict = field(default_factory=dict)     # (column, Mach) -> text
    doubtful: dict = field(default_factory=dict)     # (column, Mach) -> text
    decide: dict = field(default_factory=dict)       # input -> (min, max, column, text)
    _decided: dict = field(default=None, repr=False)

    def decided(self) -> dict:
        """Illegible inputs decided by the model: {name: value}, with 3 places (those of the header)."""
        if self._decided is None:
            self._decided = _decide(self) if self.decide else {}
        return self._decided

    def projectile(self, **changes) -> s.Projectile:
        return s.Projectile(name=self.name, **{**self.inputs, **self.decided(), **changes})

    def circular(self) -> set:
        """(column, Mach) used to decide inputs: they validate nothing in this table.
        Columns tied to them by an identity (the Magnus ones) go along."""
        cols = {c for (_, _, c, _) in self.decide.values()}
        for c in list(cols):
            cols |= LINKED.get(c, set())
        return {(c, round(float(m), 2)) for c in cols for m in s.MACH_GRID}


# Columns that are a direct function of another: deciding an input by one of them takes the
# others out of the validation. CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5), and
# CNPA3/CNPA5P come from CNPA and CNPA5 (NOTES, T12).
_MAGNUS = {"CYPA", "CPF1", "CPF5", "CNPA", "CNPA5", "CNPA3", "CNPA5P"}
LINKED = {c: _MAGNUS for c in _MAGNUS}


def _decide(tb, rounds=3):
    """Each illegible input is fitted to ITS column (minimum absolute deviation over the
    legible cells), with the others held; repeats a few rounds because they interact."""
    current = {v: 0.5 * (lo + hi) for v, (lo, hi, _, _) in tb.decide.items()}

    def cost(var, x):
        col = tb.decide[var][2]
        p = s.Projectile(name=tb.name, **{**tb.inputs, **current, var: x})
        calc = s.table(p)[col]
        printed = tb.columns[col]
        # cells resolved by an identity also count here: they are printed values,
        # disambiguated without the model (they only stay out of the validation counts)
        ok = [j for j in range(len(s.MACH_GRID)) if np.isfinite(printed[j])]
        return float(np.sum(np.abs(calc[ok] - printed[ok])))      # L1: robust to one bad cell

    fixed = {v: lo for v, (lo, hi, _, _) in tb.decide.items() if lo == hi}
    current.update(fixed)
    current = {v: x for v, x in current.items() if "#" not in v}
    for _ in range(rounds):
        for var, (lo, hi, _, _) in tb.decide.items():
            if lo == hi:
                continue
            grid = np.linspace(lo, hi, 81)
            k = int(np.argmin([cost(var, x) for x in grid]))
            a, b = grid[max(k - 1, 0)], grid[min(k + 1, 80)]
            for _ in range(40):                           # golden section in the neighboring interval
                c, d = b - 0.618 * (b - a), a + 0.618 * (b - a)
                if cost(var, c) < cost(var, d):
                    b = d
                else:
                    a = c
            current[var] = 0.5 * (a + b)
    return {v: round(x, 3) for v, x in current.items()}


def _key(col, mach):
    return col, round(float(mach), 2)


def read(path: str) -> PrintedTable:
    inputs, ident, doubt, dec, rows, name = {}, {}, {}, {}, [], ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                rows.append(line)
                continue
            txt = line[1:].strip()
            if not name:
                name = txt.split(" -- ")[0].strip()
            if txt.startswith("input:"):
                for k, v in re.findall(r"(\w+)=([-\d.]+)", txt):
                    inputs[k] = float(v)
            elif txt.startswith("decide:"):
                var, lo, hi, col = txt.split(":", 1)[1].split("|")[0].split()
                dec[var] = (float(lo), float(hi), col, txt.split("|", 1)[-1].strip())
            elif txt.startswith("decided:"):
                # value already decided in another step, by the listed columns (circular here)
                assign, cols = txt.split(":", 1)[1].split("|")[0].split()
                var, val = assign.split("=")
                for i, col in enumerate(cols.split(",")):
                    dec[var if i == 0 else f"{var}#{i}"] = (float(val), float(val), col,
                                                            txt.split("|", 1)[-1].strip())
            elif txt.startswith("identity:") or txt.startswith("doubtful:"):
                body = txt.split(":", 1)[1].strip()
                col, mach = body.split()[:2]
                (ident if txt.startswith("identity") else doubt)[_key(col, mach)] = body
    rd = csv.DictReader(rows)
    lines = list(rd)
    columns = {c: np.array([float(r[c]) if r[c].strip() else np.nan for r in lines])
               for c in rd.fieldnames}
    page = int(re.match(r"p(\d+)", os.path.basename(path)).group(1))
    return PrintedTable(page, name, path, inputs, columns, ident, doubt, dec)


def load(page: int) -> PrintedTable:
    (path,) = glob.glob(os.path.join(DIR, f"p{page:02d}_*.csv"))
    return read(path)


def all_tables() -> list:
    return [read(a) for a in sorted(glob.glob(os.path.join(DIR, "p*.csv")))]
