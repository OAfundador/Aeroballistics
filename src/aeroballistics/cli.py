"""Command line: python -m aeroballistics (or the `aeroballistics` command, once installed).

With no addition options, the output is the CANONICAL one: the 1973 SPIN-73 with the given
card. The additions (--estimate-mass, --correction) are optional and show in the header when
used.
"""
from __future__ import annotations

import sys

from . import corrections as _corr
from . import mass as _mass
from . import units as _un
from .aero import Aerodynamics
from .core import M437, Projectile, format_table, geometry_warnings, save_csv

# (option, key, help); the SPIN-73 card ones first, then the alternatives
CARD = (
    ("--VL", "VL", "total length, cal"), ("--VN", "VN", "ogive length, cal"),
    ("--VB", "VB", "boattail length, cal (0 = flat base)"),
    ("--VCG", "VCG", "CG from the nose, cal"), ("--OR", "OR", "ogive radius, cal (1000 = cone)"),
    ("--DM", "DM", "meplat diameter, cal"), ("--BD", "BD", "rotating band diameter, cal"),
    ("--BOOM", "BOOM", "'boom length' of the original card, cal"),
    ("--DIA", "DIA", "diameter, in"), ("--IX", "IX", "axial inertia, lb·in²"),
    ("--IY", "IY", "transverse inertia, lb·in²"), ("--WGT", "WGT", "weight, lb"),
    ("--TWIST", "TWIST", "rifling twist, calibers per turn"),
    ("--TEMP", "TEMP", "air temperature, °F"), ("--DGUN", "DGUN", "bore diameter, in"),
)
ALTERNATIVES = (
    ("--d-mm", "D_MM", "diameter, mm (instead of --DIA)"),
    ("--mass-g", "MASS_G", "mass, g (instead of --WGT)"),
    ("--ix-gcm2", "IX_GCM2", "axial inertia, g·cm²"), ("--iy-gcm2", "IY_GCM2", "transverse inertia, g·cm²"),
    ("--twist-mm", "TWIST_MM", "one rifling turn, mm"), ("--twist-in", "TWIST_IN", "one rifling turn, in"),
    ("--temp-c", "TEMP_C", "temperature, °C"), ("--cg-base", "CG_BASE", "CG from the BASE, cal"),
    ("--dgun-mm", "DGUN_MM", "bore diameter, mm"),
)


def _target(key: str) -> str:
    """Card key that an input fills (itself, if it is already a card key)."""
    return _un.ALTERNATIVES[key][0] if key in _un.ALTERNATIVES else key


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="aeroballistics",
        description="aeroballistics, adapted from SPIN-73: aerodynamic coefficients and stability of a "
                    "spin-stabilized projectile, from its geometry. With no addition options, "
                    "the output is that of the 1973 program (canonical).")
    ap.add_argument("--input", help="'KEY = value' file (accepts the card keys, the metric "
                                    "alternatives and the mass options)")
    ap.add_argument("--example", action="store_true",
                    help="start from the report's validation case (175 mm M437)")
    g = ap.add_argument_group("SPIN-73 card (canonical)")
    for opt, key, hlp in CARD:
        g.add_argument(opt, dest=key, type=float, help=hlp)
    g.add_argument("--name", default=None)
    g = ap.add_argument_group("the same inputs in other units (exact conversion)")
    for opt, key, hlp in ALTERNATIVES:
        g.add_argument(opt, dest=key, type=float, help=hlp)
    g = ap.add_argument_group("optional addition: estimate missing CG, mass and inertias")
    g.add_argument("--estimate-mass", nargs="?", const="solid", choices=_mass.METHODS,
                   help="solid (default: homogeneous solid), bullet or shell (Hitchcock's "
                        "formulas, BRL 620); only fills in what the card lacks")
    g.add_argument("--density", type=float, help="kg/m³, for the solid method without mass")
    g.add_argument("--material", help=f"instead of the density: {', '.join(_mass.MATERIALS)}")
    g.add_argument("--bt-angle", type=float, help="boattail angle, degrees (default 8)")
    g.add_argument("--db", type=float, help="base diameter, cal (instead of the angle)")
    g = ap.add_argument_group("optional addition: output corrections")
    g.add_argument("--correction", action="append", default=[],
                   help=f"can be repeated ({', '.join(_corr.available())}; "
                        "'free_flight:CX0' for one coefficient only)")
    ap.add_argument("--csv", help="write every column to this CSV file")
    ap.add_argument("--program", action="store_true",
                    help="show the original program block by block (aeroballistics.program) and exit")
    a = ap.parse_args(argv)
    if a.program:
        from .program import SPIN73
        print(SPIN73.describe())
        return

    # layers, from the weakest to the strongest: --example, --input, command-line options. A
    # quantity given in one layer replaces the same quantity from the layers below, in any
    # unit (--d-mm on the line replaces DIA from the file, for example).
    layers = []
    if a.example:
        layers.append({k: getattr(M437, k) for k in _un.CANONICAL})
    try:
        if a.input:
            layers.append(_un.read_fields(a.input))
        line = {key: getattr(a, key) for _, key, _ in CARD + ALTERNATIVES
                if getattr(a, key) is not None}
        if a.name is not None:
            line["name"] = a.name
        layers.append(line)
        raw = {}
        for layer in layers:
            new = {_un.normalize(k): v for k, v in layer.items()}
            targets = {_target(k) for k in new}
            raw = {k: v for k, v in raw.items() if _target(k) not in targets}
            raw.update(new)
        fields, opt = _un.split(raw)
        lacking = [k for k in ("VL", "VN", "VB") if k not in fields]
        if lacking:
            ap.error("give --example, --input or at least --VL --VN --VB "
                     f"(missing: {', '.join(lacking)})")
        p = Projectile(**fields)
    except ValueError as e:
        ap.error(str(e))

    method = a.estimate_mass or opt.get("ESTIMATE_MASS")
    additions, mass_report = [], None
    if method:
        kw = dict(density=a.density if a.density is not None else opt.get("DENSITY"),
                  material=a.material or opt.get("MATERIAL"),
                  bt_angle=a.bt_angle if a.bt_angle is not None else opt.get("BT_ANGLE"),
                  db=a.db if a.db is not None else opt.get("DB"))
        lacking = _mass.missing(p)
        try:
            mass_report = _mass.estimate(p, method, **kw) if lacking else None
            p = _mass.complete(p, method, **kw)
        except ValueError as e:
            ap.error(str(e))
        filled = [c for c in lacking if c not in _mass.missing(p)]
        additions.append(f"mass estimated ({method}: {', '.join(filled) or 'nothing was missing'})")
    elif p.VCG is None:
        ap.error("VCG (CG from the nose) is missing. Give --VCG or --cg-base, or use "
                 "--estimate-mass to estimate it from the geometry (optional addition)")

    try:
        aero = Aerodynamics(p, a.correction or None)
    except ValueError as e:
        ap.error(str(e))
    additions += [f"correction {c.name}" for c in aero.corrections]
    t = aero.table
    title = f"aeroballistics (adapted from SPIN-73) -- {p.name or 'projectile'}"
    mode = "canonical (1973 SPIN-73)" if not additions else \
        "canonical + optional additions: " + "; ".join(additions)
    print(title)
    print(f"Mode: {mode}")
    if mass_report is not None:
        print()
        print("MASS ESTIMATE (optional addition; not part of SPIN-73)")
        for x in str(mass_report).splitlines():
            print("  " + x)
    print()
    print(format_table(t))
    print()
    print("WARNINGS (limitations of the adaptation for this geometry):")
    for x in geometry_warnings(p):
        print("  - " + x)
    if a.csv:
        save_csv(t, a.csv)
        print()
        print(f"CSV written to {a.csv}")


def _run():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
