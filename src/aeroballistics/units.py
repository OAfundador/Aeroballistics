"""Inputs in other units (OPTIONAL ADDITION: exact conversion only, changes no computation).

The SPIN-73 card (aeroballistics.Projectile) uses calibers, inches, pounds, lb·in² and °F. Here it can
also be built with the keys below, which become the card's keys:

    D_MM        diameter, mm                     -> DIA  (inches)
    MASS_G      mass, g    | MASS_KG, kg         -> WGT  (lb)
    IX_GCM2     axial inertia, g·cm² | IX_KGM2   -> IX   (lb·in²)
    IY_GCM2     transverse inertia   | IY_KGM2   -> IY   (lb·in²)
    TWIST_MM    length of one rifling turn, mm             -> TWIST (calibers per turn)
    TWIST_IN    the same in inches ("1:7" -> 7)            -> TWIST
    TEMP_C      temperature, °C                  -> TEMP (°F)
    CG_BASE     CG from the BASE, calibers       -> VCG = VL − CG_BASE
    DGUN_MM     bore diameter, mm                -> DGUN (inches)

And the options of the mass estimate (aeroballistics.mass), which are not on the card:

    ESTIMATE_MASS  solid | bullet | shell        DENSITY  kg/m³        MATERIAL  steel, lead...
    BT_ANGLE       boattail angle, degrees       DB       base diameter, calibers

Keys are case-insensitive. A quantity given in both forms (DIA and D_MM, for example) is an
error.
"""
from __future__ import annotations

from dataclasses import fields

from .core import Projectile

MM_IN = 25.4
G_LB = 453.59237
GCM2_LBIN2 = G_LB * 2.54 ** 2                  # 1 lb·in² = 2926.397 g·cm²
KGM2_LBIN2 = GCM2_LBIN2 * 1e-7

CANONICAL = [f.name for f in fields(Projectile)]  # VL, VN, VB, VCG, DIA, ..., name
MASS_OPTIONS = ("ESTIMATE_MASS", "DENSITY", "MATERIAL", "BT_ANGLE", "DB")
ALTERNATIVES = {  # key -> (card key, conversion)
    "D_MM": ("DIA", lambda v, c: v / MM_IN),
    "MASS_G": ("WGT", lambda v, c: v / G_LB),
    "MASS_KG": ("WGT", lambda v, c: v * 1000.0 / G_LB),
    "IX_GCM2": ("IX", lambda v, c: v / GCM2_LBIN2),
    "IY_GCM2": ("IY", lambda v, c: v / GCM2_LBIN2),
    "IX_KGM2": ("IX", lambda v, c: v / KGM2_LBIN2),
    "IY_KGM2": ("IY", lambda v, c: v / KGM2_LBIN2),
    "TEMP_C": ("TEMP", lambda v, c: v * 9.0 / 5.0 + 32.0),
    "DGUN_MM": ("DGUN", lambda v, c: v / MM_IN),
    "CG_BASE": ("VCG", lambda v, c: _require(c, "VL", "CG_BASE") - v),
    "TWIST_MM": ("TWIST", lambda v, c: v / (_require(c, "DIA", "TWIST_MM") * MM_IN)),
    "TWIST_IN": ("TWIST", lambda v, c: v / _require(c, "DIA", "TWIST_IN")),
}


def _require(c, key, who):
    if c.get(key) in (None, 0, 0.0):
        raise ValueError(f"{who} requires {key} (or its metric form)")
    return c[key]


def normalize(key: str) -> str:
    k = key.strip()
    return "name" if k.lower() == "name" else k.upper()


def split(fields_in: dict) -> tuple[dict, dict]:
    """(card fields, mass-estimate options), with the alternatives converted."""
    canon, alt, opt = {}, {}, {}
    for k, v in fields_in.items():
        if v is None or v == "":
            continue
        k = normalize(k)
        if k in CANONICAL:
            canon[k] = v if k == "name" else float(v)
        elif k in ALTERNATIVES:
            alt[k] = float(v)
        elif k in MASS_OPTIONS:
            opt[k] = v if k in ("ESTIMATE_MASS", "MATERIAL") else float(v)
        else:
            valid = CANONICAL + list(ALTERNATIVES) + list(MASS_OPTIONS)
            raise ValueError(f"unknown input: {k}. Valid: {', '.join(valid)}")
    # first the ones that do not depend on others (D_MM before TWIST_MM, for example)
    order = sorted(alt, key=lambda k: k in ("CG_BASE", "TWIST_MM", "TWIST_IN"))
    for k in order:
        target, conv = ALTERNATIVES[k]
        if target in canon:
            raise ValueError(f"{target} given twice ({target} and {k})")
        canon[target] = conv(alt[k], canon)
    return canon, opt


def projectile(**fields_in) -> Projectile:
    """Projectile from card keys and/or the alternatives above."""
    canon, opt = split(fields_in)
    if opt:
        raise ValueError(f"{', '.join(opt)} are options of aeroballistics.mass, not of the card")
    return Projectile(**canon)


def read_fields(path: str) -> dict:
    """'KEY = value' file (# comments) -> raw dictionary (nothing converted)."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if "=" not in line:
                raise ValueError(f"{path}:{n}: expected 'KEY = value'")
            key, value = (x.strip() for x in line.split("=", 1))
            out[key] = value
    return out


def read_input(path: str) -> tuple[Projectile, dict]:
    """Like aeroballistics.read_card, but also accepts the alternatives and the mass options.
    Returns (Projectile, mass-estimate options)."""
    canon, opt = split(read_fields(path))
    return Projectile(**canon), opt


__all__ = ["projectile", "split", "read_fields", "read_input", "ALTERNATIVES", "MASS_OPTIONS"]
