"""Optional corrections on top of the reconstructed SPIN-73 (spin73.corrections).

Nothing here is used by default: with no correction, the library returns the 1973 program.

    from spin73 import corrections
    corrections.available()                   # registered names
    corrections.resolve("free_flight")        # -> [FreeFlight()]
    corrections.resolve("free_flight:CX0")    # friction only
    corrections.register("mine", MyCorrection)   # to call it by name later

A new correction is any object with `name` and `apply(t, p, ctx) -> t` (see base.py).
"""
from __future__ import annotations

from typing import Callable, Iterable

from .base import REGIMES, Context, Correction, finalize, regime
from .free_flight import EmpiricalBias, FreeFlight, ReynoldsFriction

_REGISTRY: dict[str, Callable[..., Correction]] = {
    "free_flight": FreeFlight,
}


def register(name: str, factory: Callable[..., Correction]) -> None:
    """Associates a name with a correction factory (a class or a function with no required
    arguments). The ':A,B' suffix on the name, if any, becomes coefficients=('A','B')."""
    _REGISTRY[name] = factory


def available() -> list[str]:
    return sorted(_REGISTRY)


def resolve(spec) -> list[Correction]:
    """Accepts None, a name ('free_flight', 'free_flight:CX0,CNA'), a correction object or a
    list mixing both."""
    if spec is None or spec == () or spec == []:
        return []
    if isinstance(spec, str) or hasattr(spec, "apply"):
        spec = [spec]
    out = []
    for s in spec:
        if isinstance(s, str):
            name, _, coefs = s.partition(":")
            if name not in _REGISTRY:
                raise KeyError(f"correction '{name}' not registered; available: {available()}")
            fab = _REGISTRY[name]
            out.append(fab(coefficients=tuple(c.strip() for c in coefs.split(","))) if coefs else fab())
        elif hasattr(s, "apply"):
            out.append(s)
        else:
            raise TypeError(f"don't know how to apply {s!r} as a correction")
    return out


def apply(t: dict, p, corrections: Iterable[Correction], ctx: Context) -> dict:
    """Applies the chain of corrections and recomputes the derived columns."""
    corrections = list(corrections)
    t0 = t
    for c in corrections:
        t = c.apply(t, p, ctx)
    return finalize(t0, t, p) if corrections else t


__all__ = ["Context", "Correction", "REGIMES", "regime", "finalize", "ReynoldsFriction",
           "EmpiricalBias", "FreeFlight", "register", "available", "resolve", "apply"]
