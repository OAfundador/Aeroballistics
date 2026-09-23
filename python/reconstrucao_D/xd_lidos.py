"""Redirecionamento: o bloco DATA agora vive em spin73/dados/xd_lidos.py (pacote da biblioteca)."""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
from spin73.dados.xd_lidos import *            # noqa: E402,F401,F403
