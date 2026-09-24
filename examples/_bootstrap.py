"""Deixa o pacote ``spin73`` importável sem instalar o repositório.

Os exemplos rodam direto de um clone (``python examples/01_caso_m437.py``), então cada um
importa este módulo primeiro. Com o pacote instalado (``pip install -e .``), o caminho
acrescentado é só redundante.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
ENTRADAS = Path(__file__).resolve().parent / "entradas"   # cartões de entrada de exemplo
SAIDA = RAIZ / "output" / "exemplos"                       # o que os exemplos gravam (fora do Git)


def preparar() -> Path:
    """Põe ``src/`` no sys.path, deixa a saída em UTF-8 (necessário no Windows) e devolve a raiz."""
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    return RAIZ


__all__ = ["preparar", "RAIZ", "SRC", "ENTRADAS", "SAIDA"]
