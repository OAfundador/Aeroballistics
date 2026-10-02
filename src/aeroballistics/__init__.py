"""aeroballistics: aerodynamic coefficients of spin-stabilized projectiles, inspired by and adapted from SPIN-73 (Whyte, 1973).

CANONICAL -- the core that follows the 1973 program, with nothing added:

    aeroballistics.core         the equations, table(), stability(), the input card (Projectile)
    aeroballistics.data         the DATA blocks XA..XG, with the provenance of each value
    Aerodynamics(p)             with no options, it is the canonical table interpolated in Mach
    aeroballistics.program      the original program described as objects, block by block

OPTIONAL ADDITIONS -- none is applied unless asked for, and none changes the canonical output:

    aeroballistics.conventions  output in the modern convention (pd/V, qd/V, CLα...): exact conversion
    aeroballistics.units        input in mm, g, g·cm², °C, CG from the base: exact conversion
    aeroballistics.mass         estimates CG, mass and inertias missing from the card (homogeneous
                                solid or Hitchcock's formulas, BRL 620); changes INPUTS, not the model
    aeroballistics.corrections  corrections of the coefficients (free_flight, fitted to free-flight
                                measurements) and the interface for writing new ones; changes OUTPUTS

Typical use in a simulator:

    import aeroballistics
    p = aeroballistics.Projectile(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
    aero = aeroballistics.Aerodynamics(p, convention="modern")          # canonical
    c = aero(mach)            # c.CD0, c.CNa, c.Cma, c.Cmq_Cmad, c.Clp, c.Cmpa, ...

Everything aeroballistics.core exports is also available at the top level (table, format_table,
Projectile, M437...).
"""
from . import conventions, core, corrections, data, mass, program, units
from .aero import Aerodynamics, Coefficients
from .cli import main as _main
from .core import *                                     # noqa: F401,F403
from .core import __all__ as _core_all

__version__ = "0.6.0"

__all__ = ["Aerodynamics", "Coefficients", "conventions", "core", "corrections", "data",
           "mass", "program", "units",
           *_core_all]
