"""Caminhos do repositório, para os scripts e os testes.

Importar este módulo põe no ``sys.path`` o pacote (``src/``) e as pastas de scripts cujos
módulos se importam uns aos outros; assim os scripts rodam de um clone sem instalação::

    python scripts/reconstrucao/comparacao_erros.py

Cada script só precisa achar esta pasta antes (``Path(__file__).parents[...]``).
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
SCRIPTS = RAIZ / "scripts"
TESTES = RAIZ / "tests"
DADOS = RAIZ / "data"
TABELAS_1973 = DADOS / "tabelas_1973"           # as 13 tabelas de saída do relatório
VOO_LIVRE = DADOS / "voo_livre"                 # medições de voo livre, rodada a rodada
DOCS = RAIZ / "docs"
EXEMPLOS = RAIZ / "examples"
SAIDA = RAIZ / "output"                          # resultados gerados (fora do Git)
FONTES = RAIZ / "fontes"                         # PDFs e scan (fora do Git)

PASTAS = [SRC, SCRIPTS / "reconstrucao", SCRIPTS / "voo_livre" / "benchmarks",
          SCRIPTS / "voo_livre" / "correcao", SCRIPTS / "voo_livre" / "hitchcock",
          SCRIPTS / "voo_livre" / "mr1833", SCRIPTS / "massa", SCRIPTS / "leitura", TESTES]


def preparar() -> None:
    """Põe as pastas de código no sys.path e deixa a saída em UTF-8 (necessário no Windows)."""
    for pasta in reversed(PASTAS):
        if str(pasta) not in sys.path:
            sys.path.insert(0, str(pasta))
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


preparar()
