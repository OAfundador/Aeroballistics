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
    35: {("CNA", 0.95): "CNα reconstruído 0,0019 acima (test_cna.py, PENDENTES)"},
    38: {},
    41: {("CMA", 3.0): "0,0044: no limite (CMα impresso fecha a identidade com CPN e CNα impressos)"},
    53: {
        # Mach 1,75 a 5 fecharam com o cartão C205 (NOTAS, T15).
        ("CPN", 4.0): "+0,0023 com o XC15 constante de 2,5 a 5",
        ("CMA", 4.0): "segue o CPN",
    },
    # M1 (pp. 44/47, a mesma impressão nas duas páginas do scan): Magnus, Cmq e Clp fecham com
    # a geometria do cabeçalho, mas CX, CX2, CNα, CPN e CMα não (CX +0,005 e CX2 até +0,23,
    # sistemáticos). Nenhuma mudança isolada de OR, DM, BD, VN ou VB fecha as cinco colunas.
    44: {(c, M): "a geometria do cabeçalho não reproduz CX, CX2, CNα, CPN e CMα (NOTAS, T14)"
         for c in ("CX", "CX2", "CNA", "CPN", "CMA") for M in MACH if (c, M) != ("CX", 0.01)},
    56: {("CNA", 1.0): "CNα reconstruído 0,0016 abaixo"},
    59: {("CNA", 0.95): "CNα reconstruído 0,004 abaixo (test_cna.py, PENDENTES)",
         **{("CMA", M): "CMα do M101 0,009 a 0,018 acima: segue o CNα e o CPN reconstruídos"
            for M in (1.0, 1.05, 1.5, 2.0)},
         ("CPN", 1.2): "CPN do M101 0,007 abaixo (boattail de 0,45 cal; NOTAS, T14)"},
    62: {("CNA", 0.95): "CNα reconstruído 0,0018 abaixo"},
    68: {("CNA", 1.05): "CNα reconstruído 0,0016 acima",
         ("CPN", 1.5): "CPN 0,0025 acima (XC17, ogiva > 3 cal)"},
    50: {
        ("CNA", 0.95): "CNα reconstruído 0,0017 abaixo (como no M437 em 0,8 e 1,05)",
        ("CPN", 0.6): "o resíduo subsônico de Mach 0,6 (+0,0018; o M437 tem +0,004): "
                      "nenhum coeficiente isolado explica as três tabelas (NOTAS, T13); "
                      "o CMα fica dentro da tolerância dele",
    },
}

# Uma célula circular já está fora da validação: não precisa (nem pode) ser pendência.
PENDENTES = {pag: {k: v for k, v in p.items() if k not in CIRCULARES[pag]} for pag, p in PENDENTES.items()}


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
