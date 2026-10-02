"""Repository paths, for the scripts and the tests.

Importing this module puts on ``sys.path`` the package (``src/``) and the script folders whose
modules import each other; that way the scripts run from a clone without installation::

    python scripts/adaptation/error_comparison.py

Each script only needs to find this folder first (``Path(__file__).parents[...]``).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests"
DATA = ROOT / "data"
TABLES_1973 = DATA / "tables_1973"              # the report's 13 output tables
FREE_FLIGHT = DATA / "free_flight"              # free-flight measurements, round by round
DOCS = ROOT / "docs"
EXAMPLES = ROOT / "examples"
OUTPUT = ROOT / "output"                        # generated results (outside Git)
SOURCES = ROOT / "sources"                      # PDFs and the scan (outside Git)

FOLDERS = [SRC, SCRIPTS / "adaptation", SCRIPTS / "free_flight" / "benchmarks",
           SCRIPTS / "free_flight" / "correction", SCRIPTS / "free_flight" / "hitchcock",
           SCRIPTS / "free_flight" / "mr1833", SCRIPTS / "mass", SCRIPTS / "reading", TESTS]


def prepare() -> None:
    """Puts the code folders on sys.path and makes the output UTF-8 (needed on Windows)."""
    for folder in reversed(FOLDERS):
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


prepare()
