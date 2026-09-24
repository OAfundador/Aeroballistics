"""CNa do SPIN-73 reconstruído: estrutura do texto (p. 14) + DATA XB1..XB9 lidos (com correções
decididas pelo modelo) + limiar dos expoentes do boattail em Mach 0.95 (confirmado pelas tabelas)."""
import numpy as np
from spin73.dados.xb_lidos import XB
from dados_cna import MACH
from ajustar_B import regressores

def cna_j(VL, VN, VB, OR, j, XB=XB):
    """CNα no ponto j da grade. Cartão C205: a parcela do boattail (B7..B9) não pode ser
    positiva (se sair positiva, vale zero)."""
    x = np.array(regressores(VL, VN, VB, OR, MACH[j]))
    return float(x[:6] @ XB[:6, j] + min(x[6:] @ XB[6:, j], 0.0))


def cna(VL, VN, VB, OR, M):
    """Interpola linearmente em Mach entre os pontos da grade (a grade é a do programa)."""
    vals = [cna_j(VL, VN, VB, OR, j) for j in range(len(MACH))]
    return float(np.interp(M, MACH, vals))
