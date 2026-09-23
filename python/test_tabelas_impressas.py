"""O programa inteiro, partindo só da entrada impressa, contra cada tabela de `tabelas/`.

Para cada tabela, cada célula legível é comparada com o valor calculado. Ficam de fora:
  - células resolvidas por identidade entre colunas impressas (marcadas no CSV);
  - circulares: células em que algum DATA ou entrada foi decidido usando essa mesma
    tabela (circularidade.py);
  - PENDENTES: células que não fecham, cada uma com o motivo. Se uma passar a fechar,
    o teste acusa e ela deve sair da lista.
"""
import numpy as np
import pytest

import circularidade
import spin73 as s
import tabelas_impressas as ti

MACH = [round(float(m), 2) for m in s.MACH_GRID]
TABELAS = {tb.pagina: tb for tb in ti.todas()}

# Mesmas tolerâncias do teste do M437: ±1,5 unidade na última casa; o CMα e o CX2 herdam
# o erro do CNα reconstruído (até 0,002), ampliado.
TOL = {"CMA": 0.004, "CX2": 0.0045}

CIRCULARES = {pag: circularidade.circulares(pag, tb) for pag, tb in TABELAS.items()}

PENDENTES = {
    29: {},
    32: {},
    35: {("CNA", 0.95): "CNα reconstruído 0,0019 acima (reconstrucao_B, PENDENTES)"},
    38: {},
    50: {
        ("CNA", 0.95): "CNα reconstruído 0,0017 abaixo (como no M437 em 0,8 e 1,05)",
        ("CPN", 0.6): "o resíduo subsônico de Mach 0,6 (+0,0018; o M437 tem +0,004): "
                      "nenhum coeficiente isolado explica as três tabelas (NOTAS, T13); "
                      "o CMα fica dentro da tolerância dele",
    },
}


def _celulas(pag):
    tb = TABELAS[pag]
    t = s.tabela(tb.projetil())
    for col, v in tb.colunas.items():
        if col == "MACH":
            continue
        for j, M in enumerate(MACH):
            if np.isfinite(v[j]) and (col, M) not in tb.identidade:
                yield col, M, float(t[col][j]), float(v[j])


@pytest.mark.parametrize("pag", sorted(TABELAS))
def test_tabela_reproduzida(pag):
    ruins = []
    for col, M, calc, imp in _celulas(pag):
        if (col, M) in CIRCULARES[pag] or (col, M) in PENDENTES[pag]:
            continue
        if not abs(calc - imp) <= TOL.get(col, 0.0015):
            ruins.append((col, M, round(calc, 4), imp))
    assert not ruins, f"p. {pag}: (coluna, Mach, calculado, impresso) {ruins}"


@pytest.mark.parametrize("pag", sorted(TABELAS))
def test_pendencias_ainda_pendentes(pag):
    resolvidas = [(col, M) for col, M, calc, imp in _celulas(pag)
                  if (col, M) in PENDENTES[pag] and abs(calc - imp) <= TOL.get(col, 0.0015)]
    assert not resolvidas, f"p. {pag}: remova de PENDENTES {resolvidas}"


def test_toda_tabela_classificada():
    assert set(TABELAS) == set(PENDENTES)
    for pag in TABELAS:
        assert not set(CIRCULARES[pag]) & set(PENDENTES[pag])
