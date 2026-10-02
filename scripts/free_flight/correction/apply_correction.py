"""SPIN-73 with the free-flight correction -- a shortcut to the library.

Applying the correction now lives in the library (aeroballistics.corrections.FreeFlight), so that it
can be used from a simulator; the fit and the validation stay here (fit_correction.py), which
write the result to src/aeroballistics/corrections/free_flight.json.

    import apply_correction
    t = apply_correction.corrected_table(p, d_mm=5.69)

is the same as

    aeroballistics.Aerodynamics(p, corrections="free_flight", d_mm=5.69).table
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import paths                                            # noqa: E402,F401

import aeroballistics as s                                      # noqa: E402
from aeroballistics.corrections.free_flight import FILE         # noqa: E402,F401


def corrected_table(p: s.Projectile, d_mm: float | None = None, model=None) -> dict:
    if d_mm is None and not p.DIA > 0:
        raise ValueError("give d_mm or p.DIA: the correction depends on the actual size")
    return s.Aerodynamics(p, model or "free_flight", d_mm=d_mm).table
