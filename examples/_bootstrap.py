"""Makes the ``spin73`` package importable without installing the repository.

The examples run straight from a clone (``python examples/01_m437_case.py``), so each one
imports this module first. With the package installed (``pip install -e .``), the added path is
just redundant.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
INPUTS = Path(__file__).resolve().parent / "inputs"       # example input cards
OUTPUT = ROOT / "output" / "examples"                     # what the examples write (outside Git)


def prepare() -> Path:
    """Puts ``src/`` on sys.path, makes the output UTF-8 (needed on Windows) and returns the root."""
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    return ROOT


__all__ = ["prepare", "ROOT", "SRC", "INPUTS", "OUTPUT"]
