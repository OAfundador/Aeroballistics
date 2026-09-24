"""Coluna CX2 do 5"/38 NAVY (p. 53), transcrita para dar uma segunda geometria ao teste do XD.

Leitura visual do scan (JP2 0056). As células com '?' na leitura foram decididas pelo DATA
XD, e por isso ficam fora da validação do próprio XD (DECIDIDAS).
"""
import numpy as np

_n = np.nan
CX2_538 = np.array([2.641, 2.64, 3.167, 3.694, _n, 4.626, 5.148, 5.716, 6.277,
                    5.691, 5.091, 4.518, 3.940, 3.225, 2.667, 2.19, 1.714])
DECIDIDAS = {3: "lido 3.6?4", 10: "lido 5.?91"}
ILEGIVEIS = {4: "lido 4.1??"}
# O CNα impresso do 5"/38 é suspeito de Mach 2,5 a 5 (NOTAS, T5): nessas linhas o CX2 não
# serve para testar o XD, porque a equação usa o CNα da própria tabela.
CNA_SUSPEITO = range(13, 17)
