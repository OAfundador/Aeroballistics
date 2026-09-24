"""Colunas CMA e CPN transcritas das tabelas de saída do SPIN-73.

O 175 mm M437 (p. 65) está em `data/tabelas_1973/m437_tabela.csv`. Aqui fica o 5"/38 NAVY (p. 53),
transcrito para dar uma SEGUNDA geometria ao teste do DATA XC: é o que permite separar
um erro de leitura em C1..C11 de um erro em C12..C16, porque os pesos dos dois blocos
mudam muito entre um projétil de boattail 1,00 cal (M437) e um de 0,35 cal (5"/38).

Leitura visual do scan (JP2 0056), conferida pela identidade CMA = (VCG - CPN)·CNA com
o CNA impresso (`dados_cna.py`). Onde a identidade fecha nas duas
colunas, a leitura está verificada; o que sobrou está em DUVIDOSAS.
"""
import numpy as np

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
_n = np.nan

# 5"/38 NAVY, p. 53: VL 4,59  VN 2,15  VB 0,35  OR 5,3  VCG 2,710  DM 0,100
# Mach 1,05 e 4,0 relidos pela identidade com CPN e CNα impressos (data/tabelas_1973/p53_5in38_navy.csv):
# 3.749 -> 3.739 (par 3/4) e 3.060 -> 3.066 (par 0/6).
CMA_538 = np.array([3.474, 3.514, 3.690, 3.883, 4.135, 3.976, 3.739, 3.714, 3.653,
                    3.494, 3.569, 3.408, 3.331, 3.206, 3.071, 3.066, 3.043])
CPN_538 = np.array([_n, 0.757, 0.681, 0.638, _n, 0.851, 1.031, 1.074, 1.155,
                    1.296, 1.341, 1.454, 1.532, 1.624, _n, 1.626, 1.595])

# Células ainda em aberto (índice de Mach 0-based).
DUVIDOSAS = {
    0: "CPN: 0.769 ou 0.779. Com CMA 3.474 a identidade dá 0.779; com CPN 0.769 o CMA "
       "seria 3.492. O modelo prevê 0.768. Reler as duas células.",
    4: "CPN lido como '?.464', incompatível com o CMA 4.135 e com a identidade "
       "(que daria 0.688). Reler a linha inteira: pode haver artefato de impressão.",
    14: "CPN: último dígito ilegível (1.66?); CMA 3.071 dá 1.662 pela identidade.",
}

# Valores obtidos pela identidade, não lidos diretamente (ficam fora da validação
# da própria identidade, mas servem para testar o modelo).
POR_IDENTIDADE = {5: 0.851, 14: 1.662}
