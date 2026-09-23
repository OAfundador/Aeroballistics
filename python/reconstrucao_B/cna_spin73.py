"""CNa do SPIN-73 reconstruído: estrutura do texto (p. 14) + DATA XB1..XB9 lidos (com correções
decididas pelo modelo) + limiar dos expoentes do boattail em Mach 0.95 (confirmado pelas tabelas)."""
import numpy as np
from xb_lidos import XB
from dados_cna import MACH
from ajustar_B import regressores

def cna(VL, VN, VB, OR, M):
    """Interpola linearmente em Mach entre os pontos da grade (a grade é a do programa)."""
    vals = [np.array(regressores(VL, VN, VB, OR, m)) @ XB[:, j] for j, m in enumerate(MACH)]
    return float(np.interp(M, MACH, vals))
