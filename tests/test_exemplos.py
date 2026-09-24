"""Os exemplos de examples/ rodam do começo ao fim, de um clone sem instalação."""
import subprocess
import sys

import pytest

import caminhos

EXEMPLOS = sorted(caminhos.EXEMPLOS.glob("[0-9][0-9]_*.py"))


def test_ha_exemplos():
    assert len(EXEMPLOS) >= 5


@pytest.mark.parametrize("exemplo", EXEMPLOS, ids=lambda p: p.name)
def test_exemplo_roda(exemplo):
    r = subprocess.run([sys.executable, str(exemplo)], capture_output=True, text=True,
                       encoding="utf-8", timeout=300, cwd=caminhos.RAIZ)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
