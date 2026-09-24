"""Linha de comando, leitura de entrada e gravação de CSV."""
import csv

import numpy as np

import caminhos
import aeroballistics as s


def test_arquivo_de_entrada_igual_ao_exemplo():
    p = s.ler_entrada(caminhos.EXEMPLOS / "entradas" / "m437.txt")
    for campo in ("VL", "VN", "VB", "VCG", "DM", "BD", "OR", "DIA", "IX", "IY", "WGT", "TWIST"):
        assert getattr(p, campo) == getattr(s.M437, campo), campo


def test_csv_tem_todas_as_colunas(tmp_path):
    t = s.tabela(s.M437)
    arq = tmp_path / "m437.csv"
    s.salvar_csv(t, str(arq))
    with open(arq, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 17
    esperadas = ["MACH"] + [n for n, _ in s.COLUNAS_AERO] + [n for n, _ in s.COLUNAS_ESTAB]
    assert list(linhas[0].keys()) == esperadas
    assert float(linhas[8]["CX"]) == np.round(t["CX"][8], 6)


def test_linha_de_comando(capsys):
    s._main(["--VL", "5.0", "--VN", "2.0", "--VB", "0", "--VCG", "3.04", "--OR", "8"])
    saida = capsys.readouterr().out
    assert "AERODYNAMIC COEFFICIENTS" in saida
    assert "STABILITY ANALYSIS" not in saida          # sem inércias, sem estabilidade
    assert "AVISOS" in saida


def test_avisos_dependem_da_geometria():
    curto = s.Projetil(VL=5.0, VN=2.0, VB=0.0, VCG=3.0)
    longo = s.Projetil(VL=9.0, VN=3.5, VB=1.2, VCG=5.0)
    assert len(s.avisos(longo)) > len(s.avisos(curto))
    assert any("Ogiva > 3" in a for a in s.avisos(longo))
