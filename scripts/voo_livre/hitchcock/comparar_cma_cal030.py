"""
CMα do SPIN-73 reconstruído contra o calibre 0.30 do Hitchcock (BRL 620, p. 20 impressa).

Medido: CMα = (8/π)·K_M (conversoes.py; a conversão foi verificada no Ball M2, test_cal030.py).
Modelo: CMα = (VCG − CPN)·CNα da reconstrução (cpn_spin73.py), nos 17 pontos da grade e
interpolado linearmente em Mach. Mach: o impresso na tabela quando existe; senão V / A_SOM.

HIPÓTESES:
  - DM (meplat) não está cotado nos esboços: DM = 0,12, a convenção das fontes de armas
    portáteis (../correcao/dados.py); a saída repete a conta com 0,05 e 0,20;
  - A.P. M2: o afinamento de 0,31 cal na base é tratado como base reta (dados_cal030.py);
    a saída repete a conta com VB = 0,31;
  - Tracer M1: o K_M é "aparente" (nota do relatório), calculado com a inércia média com e
    sem a composição traçante; usa-se o CG médio (FISICAS["Tracer M1 medio"]), e a saída
    repete a conta com o CG do projétil cheio;
  - Frangible M22: contorno do Ball M2, pela nota da p. 18 (o esboço da T44, p. 19, conflita
    com essa nota e continua pendente).
Ficam fora o Night Tracer M25 (sem CG nem inércia) e o A.P.I. T15 (sem estabilidade).

CÉLULAS DECIDIDAS PELO MODELO. Acima de Mach 1,1, o CPN usa o XC15 decidido pelas tabelas de
1973 (cartão não impresso), que só pesa com boattail, e, entre Mach 2,0 e 3,0, o XC1 de Mach
2,5 (lido 1,90, decidido 1,99), que pesa em todos. Nenhuma célula saiu do Hitchcock, então a
comparação não é circular, mas depende delas: a saída lista as que entram em cada linha e
repete a conta sem as CORRECOES do XC (o XC15 não tem valor lido para substituí-lo).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import caminhos                                    # noqa: E402,F401  (também põe a saída em UTF-8)

import conversoes as cv                            # noqa: E402
from cpn_spin73 import cpn_cma, decididas          # noqa: E402
from dados_cal030 import A_SOM, ESTABILIDADE, FISICAS, GEOMETRIA  # noqa: E402
from spin73.dados.xc_lidos import MACH, XC, XC_LIDO  # noqa: E402

DM = 0.12
CONTORNO = {"Frangible M22": "Ball M2"}              # nota da p. 18
FISICA = {"Tracer M1": "Tracer M1 medio"}            # a inércia (e o CG) do K_M aparente
# Leitura da linha pela identidade K_M x S x inércias (test_cal030.py; RECALIBRACAO_MR1833.md)
LEITURA = {"Ball M1": "inconsistente na fonte", "Ball M2": "verificada",
           "A.P. M2": "incerteza de temperatura", "Tracer M1": "verificada (K_M aparente)",
           "Frangible M22": "verificada"}


def linhas():
    """Séries de estabilidade que têm geometria e CG: (nome, Mach, geometria, VCG, CMα medido)."""
    out = []
    for nome, _rel, _n, V, M, _S, K_M in ESTABILIDADE:
        g = GEOMETRIA.get(CONTORNO.get(nome, nome))
        f = FISICAS.get(FISICA.get(nome, nome))
        if g is None or f is None:
            continue
        out.append((nome, M or V / A_SOM, g, g["VL"] - f["g"], cv.cma_de_km(K_M)))
    return out


def modelo(g, VCG, M, DM=DM, VB=None, XC=XC):
    """CPN e CMα do SPIN-73 em Mach M, interpolados entre os pontos da grade."""
    VB = g["VB"] if VB is None else VB
    c = np.array([cpn_cma(g["VL"], g["VN"], VB, g["OR"], DM, VCG, j, XC=XC) for j in range(17)])
    return float(np.interp(M, MACH, c[:, 0])), float(np.interp(M, MACH, c[:, 1]))


if __name__ == "__main__":
    L = linhas()
    print("=" * 78)
    print(f"CMα -- SPIN-73 reconstruído contra o calibre 0.30 do Hitchcock (DM = {DM} suposto)")
    print("=" * 78)
    print(f"{'projétil':14s} {'Mach':>6s} {'VCG':>6s} {'CPN mod':>8s} {'CMα mod':>8s} {'CMα med':>8s}"
          f" {'mod/med':>8s}  leitura")
    for nome, M, g, vcg, med in L:
        cpn, cma = modelo(g, vcg, M)
        print(f"{nome:14s} {M:6.3f} {vcg:6.3f} {cpn:8.3f} {cma:8.3f} {med:8.3f} {cma / med:8.3f}"
              f"  {LEITURA[nome]}")

    print("\nCélulas de XC decididas pelo modelo (xc_lidos) que entram em cada linha:")
    for nome, M, g, _, _ in L:
        cel = [f"XC{l} em {MACH[j]:.2f} ({reg})" for l, j, reg in decididas(M, g["VB"])]
        print(f"  {nome:14s} {M:5.3f}: " + ("\n" + " " * 24).join(cel or ["nenhuma"]))

    print("\nSensibilidade: mod/med com outro DM suposto e sem as CORRECOES do XC:")
    print(f"  {'projétil':14s} {'Mach':>6s} {'DM 0,05':>8s} {'DM 0,20':>8s} {'XC lido':>8s}")
    for nome, M, g, vcg, med in L:
        r = [modelo(g, vcg, M, DM=dm)[1] / med for dm in (0.05, 0.20)]
        r.append(modelo(g, vcg, M, XC=XC_LIDO)[1] / med)
        print(f"  {nome:14s} {M:6.3f}" + "".join(f"{v:8.3f}" for v in r))

    print("\nVariantes de geometria:")
    for nome, M, g, vcg, med in L:
        if nome == "A.P. M2":
            cma = modelo(g, vcg, M, VB=0.31)[1]
            print(f"  A.P. M2, afinamento da base como boattail (VB = 0,31): CMα = {cma:.3f}, "
                  f"mod/med = {cma / med:.3f}")
        if nome == "Tracer M1":
            vcg_cheio = g["VL"] - FISICAS["Tracer M1"]["g"]
            cma = modelo(g, vcg_cheio, M)[1]
            print(f"  Tracer M1, CG do projétil cheio (VCG = {vcg_cheio:.3f}): CMα = {cma:.3f}, "
                  f"mod/med = {cma / med:.3f}")
