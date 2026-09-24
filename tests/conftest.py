"""Configuração comum dos testes: o pacote (src/) e os scripts de análise no sys.path.

Os testes rodam de um clone sem instalação (``python -m pytest``). Os caminhos dos dados
ficam em ``scripts/caminhos.py`` (``caminhos.TABELAS_1973``, ``caminhos.VOO_LIVRE``...).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import caminhos  # noqa: E402,F401  (prepara o sys.path)
