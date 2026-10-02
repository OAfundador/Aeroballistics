"""Common test configuration: the package (src/) and the analysis scripts on sys.path.

The tests run from a clone without installation (``python -m pytest``). The data paths live
in ``scripts/paths.py`` (``paths.TABLES_1973``, ``paths.FREE_FLIGHT``...).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import paths  # noqa: E402,F401  (prepares sys.path)
