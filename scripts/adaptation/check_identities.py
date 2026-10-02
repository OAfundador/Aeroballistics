"""Checks the transcription of a table WITHOUT the model: identities between printed columns.

    CMA   = (VCG − CPN)·CNA          (definition of the moment; card C212)
    CNPA  = CYPA·(VCG − CPF1)        (Magnus moment at 1°)
    CNPA5 = CYPA·(VCG − CPF5)        (the same at 5°)
    CNPA3 + 0.1·CNPA5P = 3.75        (a defect of the original, NOTES T12)

None of them uses DATA: a line that violates one of them has a misread digit (or a wrong VCG
input). The tolerance is the rounding of the columns involved.

    python scripts/adaptation/check_identities.py 35
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths                        # noqa: E402,F401
import printed_tables as pt         # noqa: E402


def violations(tb, vcg=None):
    c = tb.columns
    vcg = tb.inputs.get("VCG") if vcg is None else vcg
    out = []
    for j, M in enumerate(c["MACH"]):
        def v(n):
            return c.get(n, np.full(17, np.nan))[j]
        tests = []
        if vcg is not None:
            tests += [
                ("CMA=(VCG-CPN)*CNA", v("CMA"), (vcg - v("CPN")) * v("CNA"),
                 0.0005 * (1 + v("CNA") + abs(vcg - v("CPN")))),
                ("CNPA=CYPA*(VCG-CPF1)", v("CNPA"), v("CYPA") * (vcg - v("CPF1")),
                 0.0005 * (1 + abs(v("CYPA")) + abs(vcg - v("CPF1")))),
                ("CNPA5=CYPA*(VCG-CPF5)", v("CNPA5"), v("CYPA") * (vcg - v("CPF5")),
                 0.0005 * (1 + abs(v("CYPA")) + abs(vcg - v("CPF5")))),
            ]
        tests.append(("CNPA3+0.1*CNPA5P=3.75", v("CNPA3") + 0.1 * v("CNPA5P"), 3.75, 0.0006))
        for name, a, b, tol in tests:
            if np.isfinite(a) and np.isfinite(b) and abs(a - b) > tol:
                out.append((round(float(M), 2), name, round(float(a), 4), round(float(b), 4)))
    return out


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for page in map(int, sys.argv[1:]):
        tb = pt.load(page)
        v = violations(tb)
        print(f"p. {page} {tb.name}: {len(v)} violation(s)")
        for x in v:
            print("   Mach {:5} {:24s} {} x {}".format(*x))
