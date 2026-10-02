"""aeroballistics.program: the object-oriented map of the original program."""
import numpy as np
import pytest

import paths
import aeroballistics
from aeroballistics import core
from aeroballistics.program import SPIN73

DOC = paths.DOCS / "ORIGINAL_PROGRAM.md"


def test_each_printed_column_has_one_and_only_one_block():
    printed = [n for n, _ in core.AERO_COLUMNS + core.STAB_COLUMNS]
    produced = [c for b in SPIN73 for c in b.columns]
    assert sorted(produced) == sorted(printed)
    for c in printed:
        assert c in SPIN73.from_column(c).columns


def test_implementation_exists_and_statements_in_order():
    previous_end = 0
    for b in SPIN73:
        assert callable(b.function()), b.key
        if b.statements and b.key != "polynomial":      # C278-C281 come after the stability
            a, z = b.statements
            assert a <= z and a > previous_end, b.key
            previous_end = z


def test_compute_returns_the_program():
    t = aeroballistics.table(aeroballistics.M437)
    for b in SPIN73:
        if b.columns:
            r = b.compute(aeroballistics.M437)
            for c in b.columns:
                assert np.allclose(r[c], t[c], equal_nan=True), (b.key, c)


def test_magnus_polynomial_rule_holds_for_any_projectile():
    """The "polynomial" block states CNPA3 + 0.1·CNPA5P = 3.75 always (a defect of the original)."""
    for geo in (dict(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9),
                dict(VL=9.0, VN=2.0, VB=0.0, VCG=5.05, OR=8.0),
                dict(VL=5.51, VN=2.91, VB=1.0, VCG=3.5, OR=25.0)):
        t = aeroballistics.table(aeroballistics.Projectile(**geo))
        assert np.allclose(t["CNPA3"] + 0.1 * t["CNPA5P"], 3.75)


def test_generated_document_is_up_to_date():
    """docs/ORIGINAL_PROGRAM.md is generated from aeroballistics.program
    (python -m aeroballistics.program --doc)."""
    from aeroballistics.program import document
    with open(DOC, encoding="utf-8") as f:
        assert f.read() == document()


def test_unknown_block():
    with pytest.raises(KeyError):
        SPIN73.block("does_not_exist")
    with pytest.raises(KeyError):
        SPIN73.from_column("XYZ")
