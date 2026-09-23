"""
SPIN-73 -- reconstrução didática a partir das equações do relatório
=====================================================================

Fonte: R. H. Whyte, "SPIN-73, an Updated Version of the SPINNER Computer
Program", Picatinny Arsenal TR 4588, nov. 1973 (DTIC AD0915628,
Distribution A -- approved for public release).

Este módulo implementa:

  1. Atmosfera e conversões de unidade, como no listing (linhas 92-93).
  2. As equações empíricas das pp. 13-17 do relatório (CX, CNa/CMa/CPN, CX2,
     Magnus, CMq, Clp). Os VALORES dos coeficientes de ajuste
     (a_i, B_i, C_i, D_i, E_i, F_i, G1) ficam nos blocos DATA do listing e
     ainda NÃO foram transcritos. Eles entram pela classe `CoefAjuste`. Sem
     eles, essas funções retornam NaN.
  3. A análise de estabilidade da p. 17-18 (sg, sd, frequências e taxas
     de amortecimento), que NÃO depende dos coeficientes de ajuste. Ela é
     validada numericamente contra a Tabela 14 (175 mm M437) em test_m437.py.

Os nomes das variáveis seguem o relatório e o listing Fortran de propósito,
para facilitar a rastreabilidade. Divergências entre o texto do relatório e
as tabelas impressas estão em NOTAS_TRANSCRICAO.md; onde há conflito, o
comportamento das tabelas prevalece.

Unidades de entrada (as do cartão de entrada do programa original):
  comprimentos em calibres, diâmetro em polegadas, Ix/Iy em lb*in^2,
  peso em lb, passo de raia em calibres/volta, temperatura em graus F.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

# Grade de Mach em que o programa original imprime os resultados.
# As 14 tabelas do relatório usam exatamente estes 17 pontos. Os arrays
# DATA do listing parecem ter 17 valores (confirmado só para XC1).
MACH_GRID = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                      1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
N_MACH = MACH_GRID.size

G_FT = 32.174          # ft/s^2 (conversão lb -> slug e lb*in^2 -> slug*ft^2)


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------
@dataclass
class Projetil:
    """Cartão de entrada do SPIN-73 (Apêndice B)."""
    VL: float          # comprimento total, calibres
    VN: float          # comprimento da ogiva, calibres
    VB: float          # comprimento do boattail, calibres
    VCG: float         # CG a partir do nariz, calibres
    DIA: float         # diâmetro, in
    IX: float          # momento axial de inércia, lb*in^2
    IY: float          # momento transversal de inércia, lb*in^2
    WGT: float         # peso, lb
    TWIST: float       # passo de raia, calibres/volta
    DM: float = 0.12   # diâmetro do meplat, calibres (default do listing, l. 90)
    BD: float = 1.02   # diâmetro da cinta, calibres (default do listing, l. 89)
    OR: float | None = None   # raio da ogiva, calibres (default: VN^2*2, l. 91)
    BOOM: float = 0.0  # "boom length" (termo do CX)
    TEMP: float = 59.0 # temperatura do ar, graus F
    DGUN: float | None = None  # diâmetro do tubo, in (default: DIA)
    nome: str = ""

    def __post_init__(self):
        if self.OR is None or self.OR <= 0:
            self.OR = 2.0 * self.VN * self.VN          # listing, linhas 91/103
        if self.BD <= 0:
            self.BD = 1.0                               # listing, linha 101
        if self.DGUN is None or self.DGUN <= 0:
            self.DGUN = self.DIA                        # listing, linha 96


# ---------------------------------------------------------------------------
# Atmosfera (listing, linhas 92-93)
# ---------------------------------------------------------------------------
def densidade_ar(temp_f: float) -> float:
    """RHO = .002376 + (-4.784*(T-59) + .01092*(T-59)**2) * 1e-6  [slug/ft^3]."""
    dt = temp_f - 59.0
    return 0.002376 + (-4.784 * dt + 0.01092 * dt * dt) * 1.0e-6


def vel_som(temp_f: float) -> float:
    """ASSO = 49.04*SQRT(459.6+TEMP)  [ft/s]."""
    return 49.04 * math.sqrt(459.6 + temp_f)


# ---------------------------------------------------------------------------
# Coeficientes de ajuste (blocos DATA do listing) -- AINDA NÃO TRANSCRITOS
# ---------------------------------------------------------------------------
def _nan(n):
    return field(default_factory=lambda: np.full((n, N_MACH), np.nan))


@dataclass
class CoefAjuste:
    """Coeficientes empíricos por ponto de Mach.

    Cada array tem forma (n_coef, 17): linha i = coeficiente i+1 do
    relatório, coluna j = MACH_GRID[j]. Preencher a partir dos DATA do
    listing (XA*, XB*, XC*, ...) quando a transcrição existir.
    """
    a: np.ndarray = _nan(13)   # a1..a13  (CX)
    B: np.ndarray = _nan(9)    # B1..B9   (CNa)
    C: np.ndarray = _nan(17)   # C1..C17  (CP normal)
    D: np.ndarray = _nan(4)    # D1..D4   (CX2)
    E: np.ndarray = _nan(4)    # E1..E4   (Magnus)
    F: np.ndarray = _nan(8)    # F1..F8   (CMq)
    G: np.ndarray = _nan(1)    # G1       (Clp)


# ---------------------------------------------------------------------------
# Equações empíricas (relatório, pp. 13-17), avaliadas no índice de Mach j
# ---------------------------------------------------------------------------
def cx(p: Projetil, k: CoefAjuste, j: int) -> float:
    """Coeficiente de força axial, p. 13."""
    a = k.a[:, j]
    CXCL = p.VL - p.VN - p.VB - 1.5
    CBD = p.BD - 1.02
    CDM = (p.DM - 0.12) ** 2
    CRAT = p.VN ** 2 / p.OR - 0.40

    if p.VN < 3.0:
        VNX, DXN = p.VN, 0.0
    else:
        VNX, DXN = 3.0, (p.VN - 3.0) * a[12]          # A13
    if CXCL < 1.5:
        CXCLL, DXCL = CXCL, 0.0
    else:
        CXCLL, DXCL = 1.5, (CXCL - 1.5) * 0.01
    if p.VB <= 0.2:
        VBX, DXBT = 0.0, 0.0
    elif p.VB < 0.65:
        VBX, DXBT = p.VB - 0.2, 0.0
    else:
        VBX, DXBT = 0.45, (p.VB - 0.65) * a[9]         # A10 (ver NOTAS: listing l.308)

    c = VNX - 2.5
    return (a[0] + a[1] * c + a[2] * c**2 + a[3] * c**3
            + a[4] * CXCLL + a[5] * CXCLL**2 + a[6] * VBX
            + a[7] * CRAT + a[8] * CRAT**2
            + a[10] * CBD + a[11] * CDM
            - (p.BOOM / 1.36) ** 2 * 0.01
            - DXBT - DXN + DXCL)


def normal_e_momento(p: Projetil, k: CoefAjuste, j: int) -> dict:
    """CNa, CMa e CPN, pp. 14-15."""
    B = k.B[:, j]
    C = k.C[:, j]
    supersonico = MACH_GRID[j] >= 1.0      # ver NOTAS: limiar não explícito
    A_exp, B_exp = (1.5, 1.0) if supersonico else (1.0, 0.8)

    if p.VN < 3.0:
        VNX, DNX = p.VN, 0.0
    else:
        VNX, DNX = 3.0, p.VN - 3.0
    if p.VB <= 0.0:
        VBNP = VBMP = VBX = 0.0
    elif p.VB < 1.0:
        VBNP, VBMP, VBX = p.VB ** A_exp, p.VB ** B_exp, p.VB
    else:
        VBX, VBNP, VBMP = 1.0, p.VB ** 0.5, p.VB ** 0.5

    CVNN = VNX - 2.47
    CXLL = p.VL - p.VN - p.VB - 2.15
    CDMM = p.DM - 0.17
    CCRT = p.VN ** 2 / p.OR - 0.48
    VBTT = p.VL / 4.7                      # texto: "VBTI = CVL/4.7", CVL = VL

    CNAB = (B[0] + B[1] * CVNN + B[2] * CXLL + B[3] * CCRT
            + B[4] * CVNN**2 + B[5] * CXLL**2)
    CNBT = B[6] * VBNP + B[7] * VBX * CVNN + B[8] * VBX * CXLL
    CNAT = CNAB + CNBT

    AMOMSQ = CNAB * (C[0] + C[1] * CVNN + C[2] * CVNN**2 + C[3] * CVNN**3
                     + C[4] * CXLL + C[5] * CXLL**2 + C[6] * CXLL**3
                     + C[7] * CCRT + C[8] * CCRT**2 + C[9] * CDMM
                     + C[10] * CCRT * CVNN      # texto: "CYNN" (erro tipográfico)
                     + C[16] * DNX)
    AMOMBT = VBTT * (C[11] * VBMP + C[12] * VBX * CVNN + C[13] * VBX * CXLL
                     + C[14] * VBX * CCRT + C[15] * VBX * CCRT * CVNN)
    CPN = (AMOMSQ + AMOMBT) / CNAT
    return dict(CNA=CNAT, CPN=CPN, CMA=(p.VCG - CPN) * CNAT)


def cx2(p: Projetil, k: CoefAjuste, j: int, CNA: float) -> float:
    """Coeficiente de força axial de guinada (derivada em sin^2 a), p. 15."""
    D = k.D[:, j]
    CXCL = p.VL - p.VN - p.VB - 1.5
    CRAT = p.VN ** 2 / p.OR - 0.40
    return D[0] + D[1] * CXCL + D[2] * CRAT + D[3] * p.VB - CNA


def magnus(p: Projetil, k: CoefAjuste, j: int) -> dict:
    """Força e momento de Magnus a 1, 2 e 5 graus, pp. 16-17."""
    E = k.E[:, j]
    CVL, CVB = p.VL, p.VB
    CXCL = p.VL - p.VN - p.VB - 1.5
    CVN = p.VN - 2.5
    CYPA = E[0] * CVL - 0.1 * CVB
    out = dict(CYPA=CYPA)
    for tag, e in (("1", E[1]), ("2", E[2]), ("5", E[3])):
        # a 5 graus o texto tem um colchete fora de lugar; segue-se a forma de 1 e 2 graus
        CNPAN = -E[0] * CVL * (e + 0.55 * CXCL + 0.80 * CVN) + CVB * (CVL / 4.7)
        CPF = -CNPAN / CYPA
        out["CPF" + tag] = CPF
        out["CNPA" + tag] = (p.VCG - CPF) * CYPA
    return out


def cmq(p: Projetil, k: CoefAjuste, j: int) -> float:
    """Coeficiente de amortecimento em arfagem, p. 17."""
    F = k.F[:, j]
    CLL = p.VL - 5.0
    CCG = p.VCG - 3.0
    CVB = p.VB
    return -5.093 * (F[0] + F[1] * CLL + F[2] * CLL**2 + F[3] * CCG
                     + F[4] * CCG * CLL + F[5] * CCG * CLL**2
                     + F[6] * CCG * CVB + F[7] * CVB)


def clp(p: Projetil, k: CoefAjuste, j: int) -> float:
    """Coeficiente de amortecimento de rolamento, p. 17."""
    return k.G[0, j] * (p.VL / 5.51)


def coeficientes(p: Projetil, k: CoefAjuste) -> dict:
    """Todos os coeficientes nos 17 pontos de Mach (NaN onde faltam DATA)."""
    cols = {n: np.empty(N_MACH) for n in
            ("CX", "CX2", "CNA", "CMA", "CPN", "CYPA", "CNPA", "CPF1", "CPF5",
             "CNPA5", "CMQ", "CLP")}
    for j in range(N_MACH):
        nm = normal_e_momento(p, k, j)
        mg = magnus(p, k, j)
        cols["CX"][j] = cx(p, k, j)
        cols["CNA"][j], cols["CMA"][j], cols["CPN"][j] = nm["CNA"], nm["CMA"], nm["CPN"]
        cols["CX2"][j] = cx2(p, k, j, nm["CNA"])
        cols["CYPA"][j] = mg["CYPA"]
        cols["CNPA"][j], cols["CPF1"][j] = mg["CNPA1"], mg["CPF1"]
        cols["CNPA5"][j], cols["CPF5"][j] = mg["CNPA5"], mg["CPF5"]
        cols["CMQ"][j] = cmq(p, k, j)
        cols["CLP"][j] = clp(p, k, j)
    cols["MACH"] = MACH_GRID.copy()
    return cols


# ---------------------------------------------------------------------------
# Análise de estabilidade (pp. 17-18) -- independe dos coeficientes de ajuste
# ---------------------------------------------------------------------------
def estabilidade(p: Projetil, MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP,
                 rho: float | None = None) -> dict:
    """Recebe os coeficientes aerodinâmicos (de qualquer fonte) e devolve as
    colunas da seção "STABILITY ANALYSIS" das tabelas do SPIN-73.

    Unidades de saída: SPIN, W1, W2 em rad/s; L1, L2 em 1/ft.
    """
    MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP = map(
        np.asarray, (MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP))
    rho = densidade_ar(p.TEMP) if rho is None else rho
    d = p.DIA / 12.0
    m = p.WGT / G_FT
    Ix = p.IX / (G_FT * 144.0)
    Iy = p.IY / (G_FT * 144.0)
    A = math.pi * d * d / 4.0

    V = MACH * vel_som(p.TEMP)
    spin_por_ft = 2.0 * math.pi / (p.TWIST * p.DGUN / 12.0)   # rad/ft
    P = V * spin_por_ft                                        # rad/s

    sg = 2.0 * Ix**2 * P**2 / (math.pi * rho * Iy * CMA * d**3 * V**2)

    k1 = m * d * d / Ix        # k1^-2 do relatório
    k2 = m * d * d / Iy        # k2^-2 do relatório

    def s_d(cnpa):
        return (2.0 * (CNA - CX + k1 / 2.0 * cnpa)
                / (CNA - CX - k2 / 2.0 * CMQ + k1 / 2.0 * CLP))

    sd, sd5 = s_d(CNPA), s_d(CNPA5)
    recip = 1.0 / (sd * (2.0 - sd))        # critério: estável se sg > RECIP
    recip5 = 1.0 / (sd5 * (2.0 - sd5))

    sig = np.sqrt(1.0 - 1.0 / sg)
    W1 = P * Ix / (2.0 * Iy) * (1.0 + sig)
    W2 = P * Ix / (2.0 * Iy) * (1.0 - sig)

    K = rho * A / (4.0 * m)

    def lam(sinal, cnpa):
        # ATENÇÃO: o texto (p. 18) imprime -CN*(1 +- 1/sigma). As tabelas só são
        # reproduzidas com -CN*(1 -+ 1/sigma). Ver NOTAS_TRANSCRICAO.md, item E1.
        return K * (-CNA * (1.0 - sinal / sig)
                    + k2 / 2.0 * (1.0 + sinal / sig) * CMQ
                    + sinal * k1 / sig * cnpa)

    return dict(MACH=MACH, GYRO=sg, SBAR=sd, RECIP=recip, SBAR5=sd5,
                RECIP5=recip5, SPIN=P, W1=W1, W2=W2,
                L1=lam(+1, CNPA), L2=lam(-1, CNPA),
                L15=lam(+1, CNPA5), L25=lam(-1, CNPA5))


# ---------------------------------------------------------------------------
# Caso de validação: 175 mm M437 (Tabela 14, p. 65)
# ---------------------------------------------------------------------------
M437 = Projetil(VL=5.510, VN=2.910, VB=1.000, VCG=3.500, DM=0.079, BD=1.050,
                OR=25.0, BOOM=0.0, DIA=6.885, IX=954.1, IY=10850.0,
                WGT=148.0, TWIST=20.0, TEMP=59.0, nome="175MM M437")


def ler_tabela(caminho: str) -> dict:
    """Lê uma tabela transcrita (CSV com linhas de comentário '#')."""
    import csv
    with open(caminho, newline="", encoding="utf-8") as f:
        linhas = [l for l in f if not l.startswith("#")]
    rd = csv.DictReader(linhas)
    rows = list(rd)
    return {c: np.array([float(r[c]) for r in rows]) for c in rd.fieldnames}


if __name__ == "__main__":
    import os
    tab = ler_tabela(os.path.join(os.path.dirname(__file__), "m437_tabela.csv"))
    est = estabilidade(M437, tab["MACH"], tab["CX"], tab["CNA"], tab["CMA"],
                       tab["CNPA"], tab["CNPA5"], tab["CMQ"], tab["CLP"])
    print(f"{M437.nome}: estabilidade recalculada x Tabela 14 do relatório\n")
    cols = ["GYRO", "SBAR", "SBAR5", "SPIN", "W1", "W2", "L1", "L2", "L15", "L25"]
    print("MACH  " + "".join(f"{c:>18s}" for c in cols))
    for i, M in enumerate(tab["MACH"]):
        s = f"{M:5.2f} "
        for c in cols:
            s += f"  {est[c][i]:8.4g}|{tab[c][i]:<7.4g}"
        print(s)
    print("\n(cada célula: calculado|tabela)")
    print("\nCoeficientes empíricos sem DATA transcritos (esperado: NaN):")
    print({k: v[-1] for k, v in coeficientes(M437, CoefAjuste()).items()})
