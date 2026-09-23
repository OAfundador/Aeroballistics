"""Redirecionamento: a lei de atrito agora vive em spin73/correcoes/reynolds.py."""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", ".."))
from spin73.correcoes.reynolds import *       # noqa: E402,F401,F403
from spin73.correcoes.reynolds import area_molhada, cf, delta_cx0  # noqa: E402,F401
