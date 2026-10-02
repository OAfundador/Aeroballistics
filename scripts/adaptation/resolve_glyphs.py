"""Resolves ambiguous glyphs of a reading ONLY through the identities between printed columns.

In the reading (data/tables_1973/readings/pNN_*.txt), each cell is written as it was seen, with classes:
    A      = 6 or 8 (in the dot-matrix printout the two come out almost the same)
    [xy]   = one of the listed digits, for example [13] or [27]
    ?      = illegible digit (any one)
    empty  = illegible cell
Comment lines (#) with "input:", "decide:", "header:" etc. are copied.

For each Mach line, the cells linked by identities form groups
    (CNA, CMA, CPN)                       CMA = (VCG − CPN)·CNA
    (CYPA, CPF1, CNPA, CPF5, CNPA5)       CNPA = CYPA·(VCG − CPF1); CNPA5 = CYPA·(VCG − CPF5)
    (CNPA3, CNPA5P)                       CNPA3 + 0.1·CNPA5P = 3.75
and every combination of readings is tested. An ambiguous cell that comes out with the SAME
value in every consistent combination is resolved, and is marked "identity" (out of the
validation counts). No DATA and no model result enter here.

    python scripts/adaptation/resolve_glyphs.py 41   -> data/tables_1973/p41_*.csv
"""
import itertools
import os
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths                                                # noqa: E402

TABLES = paths.TABLES_1973
COLS = ["MACH", "CX", "CX2", "CNA", "CMA", "CPN", "CYPA", "CNPA", "CNPA3", "CNPA5P",
        "CPF1", "CPF5", "CNPA5", "CMQ", "CLP"]
GROUPS = [("CNA", "CMA", "CPN"), ("CYPA", "CPF1", "CNPA", "CPF5", "CNPA5"), ("CNPA3", "CNPA5P")]
LIMIT = 20000


def alternatives(cel):
    """Every possible reading of a cell (list of numeric strings)."""
    if not cel:
        return []
    parts = re.findall(r"\[[0-9]+\]|A|\?|.", cel)
    options = []
    for p in parts:
        if p == "A":
            options.append("68")
        elif p == "?":
            options.append("0123456789")
        elif p.startswith("["):
            options.append(p[1:-1])
        else:
            options.append(p)
    return ["".join(c) for c in itertools.product(*options)]


def _ok(v, vcg):
    """Identities of the group with the cells present (rounding tolerance)."""
    g = v.get
    if vcg is not None and all(k in v for k in ("CNA", "CMA", "CPN")):
        if abs(g("CMA") - (vcg - g("CPN")) * g("CNA")) > 0.0005 * (1 + g("CNA") + abs(vcg - g("CPN"))):
            return False
    for cpf, cn in (("CPF1", "CNPA"), ("CPF5", "CNPA5")):
        if vcg is not None and all(k in v for k in ("CYPA", cpf, cn)):
            if abs(g(cn) - g("CYPA") * (vcg - g(cpf))) > 0.0005 * (1 + abs(g("CYPA")) + abs(vcg - g(cpf))):
                return False
    if "CNPA3" in v and "CNPA5P" in v:
        if abs(g("CNPA3") + 0.1 * g("CNPA5P") - 3.75) > 0.0006:
            return False
    return True


def resolve(cells, vcg):
    """cells: {column: text read}. Returns {column: (value|None, 'read'|'identity'|reason)}."""
    out = {}
    for c, txt in cells.items():
        alts = alternatives(txt)
        if len(alts) == 1:
            out[c] = (float(alts[0]), "read")
    for group in GROUPS:
        amb = {c: alternatives(cells[c]) for c in group if cells.get(c) and len(alternatives(cells[c])) > 1}
        if not amb:
            continue
        fixed = {c: out[c][0] for c in group if c in out}
        n = int(np.prod([len(a) for a in amb.values()]))
        if n > LIMIT:
            for c in amb:
                out[c] = (None, f"ambiguous: {cells[c]}")
            continue
        valid = []
        for combo in itertools.product(*amb.values()):
            v = {**fixed, **{c: float(x) for c, x in zip(amb, combo)}}
            if _ok(v, vcg):
                valid.append(dict(zip(amb, combo)))
        for c in amb:
            values = {d[c] for d in valid}
            if len(values) == 1:
                out[c] = (float(values.pop()), f"identity: {cells[c]}")
            else:
                out[c] = (None, f"ambiguous: {cells[c]}" + (" (no reading closes the identities)"
                                                              if not valid else ""))
    for c, txt in cells.items():
        if c not in out and txt:
            out[c] = (None, f"ambiguous: {txt}")
    return out


def convert(page):
    (reading,) = [f for f in os.listdir(TABLES / "readings") if f.startswith(f"p{page:02d}_")]
    lines = open(TABLES / "readings" / reading, encoding="utf-8").read().splitlines()
    head = [l for l in lines if l.startswith("#")]
    vcg = None
    for l in head:
        m = re.search(r"(?:input:.*\b|decided: )VCG=([\d.]+)", l)
        if m:
            vcg = float(m.group(1))
    rows = [l for l in lines if l.strip() and not l.startswith("#")]
    assert rows[0].split(",") == COLS, rows[0]
    ident, doubt, table = [], [], []
    for l in rows[1:]:
        fields = [x.strip() for x in l.split(",")]
        mach = fields[0]
        res = resolve(dict(zip(COLS[1:], fields[1:])), vcg)
        line = [mach]
        for c in COLS[1:]:
            v, how = res.get(c, (None, ""))
            if v is None:
                line.append("")
                if how:
                    doubt.append(f"# doubtful: {c} {mach} {how.split(': ', 1)[1]} | not resolved by the identities")
            else:
                places = len(alternatives(fields[COLS.index(c)])[0].split(".")[-1])
                line.append(f"{v:.{places}f}")
                if how.startswith("identity"):
                    ident.append(f"# identity: {c} {mach} {how.split(': ', 1)[1]} -> {v:.{places}f} | "
                                 "the only reading that closes the identities between printed columns")
        table.append(",".join(line))
    out_path = TABLES / reading.replace(".txt", ".csv")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(head) + "\n#\n# Generated by resolve_glyphs.py from readings/" + reading + "\n#\n")
        f.write("\n".join(ident + ["#"] + doubt) + "\n")
        f.write(",".join(COLS) + "\n" + "\n".join(table) + "\n")
    return out_path, len(ident), len(doubt)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for page in map(int, sys.argv[1:]):
        print(convert(page))
