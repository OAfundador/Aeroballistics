"""
SPIN-73 -- reconstrução didática
=================================

Fonte: R. H. Whyte, "SPIN-73, an Updated Version of the SPINNER Computer Program",
Picatinny Arsenal TR 4588, nov. 1973 (DTIC AD0915628, Distribution A).

O programa estima os coeficientes aerodinâmicos de um projétil estabilizado por
rotação a partir da geometria, em 17 números de Mach, e faz a análise de estabilidade.

Onde o código Fortran já foi transcrito (original/listing_p84-86.f), as equações seguem o
CÓDIGO, que é o que gerou as tabelas de 1973; onde ainda não foi, seguem o texto do
relatório (pp. 13-18). Cada divergência entre os dois está marcada no ponto em que ocorre
e registrada em docs/NOTAS_TRANSCRICAO.md.

Uso:
    import spin73 as s
    t = s.tabela(s.M437)                  # dicionário com todas as colunas
    print(s.formatar(t))                  # tabela no formato do relatório

Unidades de entrada (as do cartão do programa original): comprimentos em calibres,
diâmetro em polegadas, Ix/Iy em lb·in², peso em lb, passo de raia em calibres por volta,
temperatura em °F.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

MACH_GRID = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                      1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
N_MACH = MACH_GRID.size
J_SUPERSONICO = 4        # listing C189: IF(J.GE.5) com J a partir de 1 -> Mach 0,95

G_FT = 32.174            # ft/s², conversões de peso e inércia
K_ESTAB = 1352.4         # constante do fator giroscópico no listing (cartão C241)


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
    DIA: float = 0.0   # diâmetro, in (0 = sem análise de estabilidade)
    IX: float = 0.0    # momento axial de inércia, lb·in²
    IY: float = 0.0    # momento transversal de inércia, lb·in²
    WGT: float = 0.0   # peso, lb
    TWIST: float = 0.0 # passo de raia, calibres/volta
    DM: float = 0.12   # diâmetro do meplat, calibres (default do listing)
    BD: float = 1.02   # diâmetro da cinta, calibres (default do listing)
    OR: float | None = None   # raio da ogiva, calibres (default: 2·VN²)
    BOOM: float = 0.0  # "boom length" (termo do CX)
    TEMP: float = 59.0 # temperatura do ar, °F
    DGUN: float | None = None  # diâmetro do tubo, in (default: DIA)
    nome: str = ""

    def __post_init__(self):
        if self.OR is None or self.OR <= 0:
            self.OR = 2.0 * self.VN * self.VN
        if self.BD <= 0:
            self.BD = 1.0
        if self.DGUN is None or self.DGUN <= 0:
            self.DGUN = self.DIA


# ---------------------------------------------------------------------------
# Atmosfera (listing, cartões 92-93)
# ---------------------------------------------------------------------------
def densidade_ar(temp_f: float) -> float:
    """RHO = .002376 + (-4.784*(T-59) + .01092*(T-59)**2) * 1e-6  [slug/ft³]."""
    dt = temp_f - 59.0
    return 0.002376 + (-4.784 * dt + 0.01092 * dt * dt) * 1.0e-6


def vel_som(temp_f: float) -> float:
    """ASSO = 49.04*SQRT(459.6+TEMP)  [ft/s]."""
    return 49.04 * math.sqrt(459.6 + temp_f)


# ---------------------------------------------------------------------------
# Coeficientes de ajuste (blocos DATA)
# ---------------------------------------------------------------------------
def _nan(n):
    return field(default_factory=lambda: np.full((n, N_MACH), np.nan))


@dataclass
class CoefAjuste:
    """Blocos DATA por ponto de Mach, cada um com forma (n, 17)."""
    a: np.ndarray = _nan(15)   # XA1..XA15  (CX)
    B: np.ndarray = _nan(10)   # XB1..XB10  (CNα)
    C: np.ndarray = _nan(17)   # XC1..XC17  (CP normal)
    D: np.ndarray = _nan(4)    # XD1..XD4   (CX2)
    E: np.ndarray = _nan(5)    # XE1..XE5   (Magnus; XE5 = corpo longo)
    F: np.ndarray = _nan(9)    # XF1..XF9   (Cmq; XF9 = corpo longo)
    G: np.ndarray = _nan(1)    # XG1        (Clp)

    @classmethod
    def do_listing(cls) -> "CoefAjuste":
        """Os DATA reconstruídos (ver dados_spin73.py para a situação de cada bloco)."""
        import dados_spin73 as d
        return cls(a=d.XA.copy(), B=d.XB.copy(), C=d.XC.copy(), D=d.XD.copy(),
                   E=d.XE.copy(), F=d.XF.copy(), G=d.XG.copy())


# ---------------------------------------------------------------------------
# Equações empíricas, avaliadas no índice de Mach j
# ---------------------------------------------------------------------------
def cx(p: Projetil, k: CoefAjuste, j: int) -> float:
    """Força axial. Código: cartões C164-C174 (DXN em três trechos, com A13, A14 e A15,
    que o texto não documenta). Ramo do boattail (DXBT) ainda segue o texto: o cartão
    correspondente, na p. 83, não foi transcrito (NOTAS, item E6)."""
    a = k.a[:, j]
    CXCL = p.VL - p.VN - p.VB - 1.5
    CBD = p.BD - 1.02
    CDM = (p.DM - 0.12) ** 2
    CRAT = p.VN ** 2 / p.OR - 0.40

    if p.VN <= 3.0:
        VNX, DXN = p.VN, 0.0
    else:
        VNX = 3.0
        if p.VN <= 3.48:
            DXN = (p.VN - 3.0) * a[12]
        elif p.VN <= 3.97:
            DXN = 0.48 * a[12] + (p.VN - 3.48) * a[13]
        else:
            DXN = 0.48 * a[12] + 0.49 * a[13] + (p.VN - 3.97) * a[14]
    if CXCL <= 1.5:
        CXCLL, DXCL = CXCL, 0.0
    else:
        CXCLL, DXCL = 1.5, (CXCL - 1.5) * 0.010
    if p.VB <= 0.2:
        VBX, DXBT = 0.0, 0.0
    elif p.VB < 0.65:
        VBX, DXBT = p.VB - 0.2, 0.0
    else:
        VBX, DXBT = 0.45, (p.VB - 0.65) * a[9]

    c = VNX - 2.5
    return (a[0] + a[1] * c + a[2] * c ** 2 + a[3] * c ** 3
            + a[4] * CXCLL + a[5] * CXCLL ** 2 + a[6] * VBX
            + a[7] * CRAT + a[8] * CRAT ** 2
            + a[10] * CBD + a[11] * CDM
            - (p.BOOM / 1.36) ** 2 * 0.01
            - DXBT - DXN + DXCL)


def normal_e_momento(p: Projetil, k: CoefAjuste, j: int) -> dict:
    """CNα, CPN e CMα. Código: cartões C175-C212."""
    B, C = k.B[:, j], k.C[:, j]
    VBX, DNX = p.VB, 0.0
    VNX = p.VN
    if p.VN > 3.0:
        VNX, DNX = 3.0, p.VN - 3.0
    if p.VB > 1.0:
        VBX = 1.0
        VBNP = VBMP = p.VB ** 0.5
    elif j >= J_SUPERSONICO:
        VBNP, VBMP = p.VB ** 1.5, p.VB
    else:
        VBNP, VBMP = p.VB, p.VB ** 0.8

    CVNN = VNX - 2.47
    CXLL = p.VL - p.VN - p.VB - 2.15
    CDMM = p.DM - 0.17
    CCRT = p.VN ** 2 / p.OR - 0.48
    VBTT = p.VL / 4.7                       # texto: "VBTI"; código: VBTT = CVL/4.7

    CNAB = (B[0] + B[1] * CVNN + B[2] * CXLL + B[3] * CCRT
            + B[4] * CVNN ** 2 + B[5] * CXLL ** 2)
    CNBT = B[6] * VBNP + B[7] * VBX * CVNN + B[8] * VBX * CXLL
    CNAT = CNAB + CNBT

    AMOMSQ = CNAB * (C[0] + C[1] * CVNN + C[2] * CVNN ** 2 + C[3] * CVNN ** 3
                     + C[4] * CXLL + C[5] * CXLL ** 2 + C[6] * CXLL ** 3
                     + C[7] * CCRT + C[8] * CCRT ** 2 + C[9] * CDMM
                     + C[10] * CCRT * CVNN + C[16] * DNX)
    AMOMBT = VBTT * (C[11] * VBMP + C[12] * VBX * CVNN + C[13] * VBX * CXLL
                     + C[14] * VBX * CCRT + C[15] * VBX * CCRT * CVNN)
    # Cartões C209-C210, ausentes do texto: se o momento do boattail sair positivo,
    # o programa descarta toda a contribuição do boattail.
    if AMOMBT > 0.0:
        CNAT, AMOMBT = CNAB, 0.0
    CPN = (AMOMSQ + AMOMBT) / CNAT
    return dict(CNA=CNAT, CPN=CPN, CMA=(p.VCG - CPN) * CNAT)


def cx2(p: Projetil, k: CoefAjuste, j: int, CNA: float) -> float:
    """Força axial de guinada. Código: cartão C213."""
    D = k.D[:, j]
    CXCL = p.VL - p.VN - p.VB - 1.5
    CRAT = p.VN ** 2 / p.OR - 0.40
    return D[0] + D[1] * CXCL + D[2] * CRAT + D[3] * p.VB - CNA


def magnus(p: Projetil, k: CoefAjuste, j: int) -> dict:
    """Força e momento de Magnus a 1, 2 e 5 graus. Código: cartões C214-C231.

    O termo de corpo longo (XE5, ausente do texto) soma-se ao CPF quando VL > 6.
    """
    E = k.E[:, j]
    CVL, CVB = p.VL, p.VB
    CXCL = p.VL - p.VN - p.VB - 1.5
    CVN = p.VN - 2.5
    CYP = E[0] * CVL
    CYPA = CYP - 0.1 * CVB
    DCPF = (p.VL - 6.0) * E[4] if p.VL > 6.0 else 0.0
    out = dict(CYPA=CYPA)
    for tag, e in (("1", E[1]), ("2", E[2]), ("5", E[3])):
        CNPAN = -CYP * (e + 0.55 * CXCL + 0.8 * CVN) + 1.0 * CVL / 4.7 * CVB
        CPF = -CNPAN / CYPA + DCPF
        out["CPF" + tag] = CPF
        out["CNPA" + tag] = (p.VCG - CPF) * CYPA
    return out


def coef_polinomio_magnus(cnpa1: float, cnpa5: float) -> tuple[float, float]:
    """Colunas impressas CNPA3 e CNPA5 ("coeficientes do polinômio" de Magnus).

    Código, cartões C278-C281:
        XMAG1 = CNPAA5 - CNPA            (momento a 5° menos o a 1°)
        XMAG2 = CNPAA5 - CNPA + 0.3
        CNPA5 = (XMAG2 - 9.0*XMAG1)/0.0072
        CNPA3 = (XMAG1 - CNPA5*.0001)/0.01
    As constantes são as de um polinômio f(δ) = C1 + C3·δ² + C5·δ⁴ avaliado em δ = 0,1 e
    0,3. Mas o XMAG2 não usa o valor a 2° (CNPAA2, calculado nos cartões C224-C227 e nunca
    usado): é o XMAG1 mais uma constante. Por isso as duas colunas impressas carregam UM
    único grau de liberdade e obedecem a CNPA3 + 0,1·CNPA5 = 3,75 em qualquer projétil --
    identidade que as tabelas de 1973 confirmam linha a linha. Defeito do original,
    mantido. Nos arquivos, "CNPA5P" é esta coluna e "CNPA5" é o CNPA*5 (valor a 5°).
    """
    xmag1 = cnpa5 - cnpa1
    xmag2 = cnpa5 - cnpa1 + 0.3
    c5 = (xmag2 - 9.0 * xmag1) / 0.0072
    c3 = (xmag1 - c5 * 0.0001) / 0.01
    return c3, c5


def cmq(p: Projetil, k: CoefAjuste, j: int) -> float:
    """Amortecimento em arfagem. Código: cartões C232-C238 (F9, ausente do texto)."""
    F = k.F[:, j]
    CLL = p.VL - 5.0
    CCG = p.VCG - 3.0
    CVB = p.VB
    CKM = (F[0] + F[1] * CLL + F[2] * CLL ** 2 + F[3] * CCG
           + F[4] * CCG * CLL + F[5] * CCG * CLL ** 2 + F[6] * CCG * CVB + F[7] * CVB)
    DCMQ = (p.VL - 6.0) * F[8] if p.VL > 6.0 else 0.0
    return -5.093 * CKM - DCMQ


def clp(p: Projetil, k: CoefAjuste, j: int) -> float:
    """Amortecimento de rolamento. Código: cartão C239 (SFNG = 5,51, o VL do M437)."""
    return k.G[0, j] * (p.VL / 5.51)


def coeficientes(p: Projetil, k: CoefAjuste) -> dict:
    """Todas as colunas aerodinâmicas nos 17 pontos de Mach (NaN onde falta DATA)."""
    nomes = ("CX", "CX2", "CNA", "CMA", "CPN", "CYPA", "CNPA", "CPF1", "CPF2", "CNPA2",
             "CPF5", "CNPA5", "CNPA3", "CNPA5P", "CMQ", "CLP")
    cols = {n: np.empty(N_MACH) for n in nomes}
    for j in range(N_MACH):
        nm = normal_e_momento(p, k, j)
        mg = magnus(p, k, j)
        cols["CX"][j] = cx(p, k, j)
        cols["CNA"][j], cols["CMA"][j], cols["CPN"][j] = nm["CNA"], nm["CMA"], nm["CPN"]
        cols["CX2"][j] = cx2(p, k, j, nm["CNA"])
        cols["CYPA"][j] = mg["CYPA"]
        cols["CNPA"][j], cols["CPF1"][j] = mg["CNPA1"], mg["CPF1"]
        cols["CNPA2"][j], cols["CPF2"][j] = mg["CNPA2"], mg["CPF2"]
        cols["CNPA5"][j], cols["CPF5"][j] = mg["CNPA5"], mg["CPF5"]
        cols["CNPA3"][j], cols["CNPA5P"][j] = coef_polinomio_magnus(mg["CNPA1"], mg["CNPA5"])
        cols["CMQ"][j] = cmq(p, k, j)
        cols["CLP"][j] = clp(p, k, j)
    cols["MACH"] = MACH_GRID.copy()
    return cols


# ---------------------------------------------------------------------------
# Análise de estabilidade (pp. 17-18; código a partir do cartão C240)
# ---------------------------------------------------------------------------
def estabilidade(p: Projetil, MACH, CX, CNA, CMA, CNPA, CNPA5, CMQ, CLP,
                 rho: float | None = None) -> dict:
    """Colunas da seção "STABILITY ANALYSIS" a partir dos coeficientes (de qualquer fonte).

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
    passo_in = p.TWIST * p.DGUN                            # uma volta, em polegadas
    P = V * 2.0 * math.pi / (passo_in / 12.0)              # rad/s

    # Cartão C241: STAB = 1352.4*XY*TT/(IR*RHO*FC*CMA). Com Ix, Iy em lb·in² e
    # comprimentos em polegadas, é  s_g = 1352,4·Ix²/(ρ·Iy·CMα·passo²·d³).
    # A fórmula física com g = 32,174 daria 1349,8 no lugar de 1352,4: a diferença,
    # +0,19 %, é o "viés de s_g" que ficou em aberto até o código ser lido.
    sg = K_ESTAB * p.IX ** 2 / (rho * p.IY * CMA * passo_in ** 2 * p.DIA ** 3)

    k1 = m * d * d / Ix        # k1^-2 do relatório
    k2 = m * d * d / Iy        # k2^-2 do relatório

    def s_d(cnpa):
        return (2.0 * (CNA - CX + k1 / 2.0 * cnpa)
                / (CNA - CX - k2 / 2.0 * CMQ + k1 / 2.0 * CLP))

    sd, sd5 = s_d(CNPA), s_d(CNPA5)
    recip = 1.0 / (sd * (2.0 - sd))
    recip5 = 1.0 / (sd5 * (2.0 - sd5))

    sig = np.sqrt(1.0 - 1.0 / sg)
    W1 = P * Ix / (2.0 * Iy) * (1.0 + sig)
    W2 = P * Ix / (2.0 * Iy) * (1.0 - sig)

    K = rho * A / (4.0 * m)

    def lam(sinal, cnpa):
        # O texto (p. 18) imprime -CN*(1 +- 1/sigma); as tabelas só são reproduzidas
        # com -CN*(1 -+ 1/sigma). NOTAS_TRANSCRICAO.md, item E1.
        return K * (-CNA * (1.0 - sinal / sig)
                    + k2 / 2.0 * (1.0 + sinal / sig) * CMQ
                    + sinal * k1 / sig * cnpa)

    # Cartão C266: período de nutação dividido por 20 (passo de integração sugerido).
    DELT = 6.28 / (W1 * 20.0)
    # Cartão C256: DISP = ((CNAT-CX0)*TH*(W1-W2)*3.635)/(CMA*WGT*DIA*VEL), com TH = Iy em
    # lb·in². A referência 71 do relatório (Whyte 1970), que explicaria a grandeza, não
    # está disponível; a fórmula é reproduzida como está no código.
    DISP = (CNA - CX) * p.IY * (W1 - W2) * 3.635 / (CMA * p.WGT * p.DIA * V)

    out = dict(MACH=MACH, GYRO=sg, SBAR=sd, RECIP=recip, SBAR5=sd5,
               RECIP5=recip5, SPIN=P, W1=W1, W2=W2,
               L1=lam(+1, CNPA), L2=lam(-1, CNPA),
               L15=lam(+1, CNPA5), L25=lam(-1, CNPA5), DELT=DELT, DISP=DISP)
    # Cartões C249 e C287: com s_g < 1,001 o programa só imprime MACH e STAB (o projétil
    # é giroscopicamente instável e o resto da análise não faz sentido).
    instavel = np.asarray(sg) < 1.001
    for nome in out:
        if nome not in ("MACH", "GYRO"):
            out[nome] = np.where(instavel, np.nan, out[nome])
    return out


# ---------------------------------------------------------------------------
# Programa completo: geometria -> tabela
# ---------------------------------------------------------------------------
def tabela(p: Projetil, k: CoefAjuste | None = None) -> dict:
    """Todas as colunas que o SPIN-73 imprime, para um projétil.

    As colunas cujo DATA ainda não foi reconstruído saem NaN (ver dados_spin73.py);
    a análise de estabilidade depende do CX e sai NaN enquanto o XA não for lido.
    """
    k = CoefAjuste.do_listing() if k is None else k
    t = coeficientes(p, k)
    if p.DIA > 0 and p.IX > 0 and p.IY > 0 and p.WGT > 0 and p.TWIST > 0:
        with np.errstate(invalid="ignore", divide="ignore"):
            t.update(estabilidade(p, t["MACH"], t["CX"], t["CNA"], t["CMA"],
                                  t["CNPA"], t["CNPA5"], t["CMQ"], t["CLP"]))
    return t


# Ordem e nomes das colunas impressas pelo programa (cartões C282 e C290).
COLUNAS_AERO = [("CX", 3), ("CX2", 3), ("CNA", 3), ("CMA", 3), ("CPN", 3), ("CYPA", 3),
                ("CNPA", 3), ("CNPA3", 3), ("CNPA5P", 3), ("CPF1", 3), ("CPF5", 3),
                ("CNPA5", 3), ("CMQ", 3), ("CLP", 3)]
COLUNAS_ESTAB = [("GYRO", 3), ("SBAR", 3), ("RECIP", 3), ("SBAR5", 3), ("RECIP5", 3),
                 ("SPIN", 1), ("W1", 2), ("W2", 2), ("L1", 6), ("L2", 6), ("L15", 6), ("L25", 6),
                 ("DELT", 4), ("DISP", 3)]


def formatar(t: dict, titulo: str = "") -> str:
    """Tabela em texto, no arranjo do relatório (colunas NaN aparecem como '--')."""
    def bloco(colunas, cab):
        linhas = [cab, "MACH  " + "".join(f"{n:>10s}" for n, _ in colunas)]
        for i, M in enumerate(t["MACH"]):
            campos = []
            for n, casas in colunas:
                v = t.get(n, np.full(N_MACH, np.nan))[i]
                campos.append(f"{v:10.{casas}f}" if np.isfinite(v) else f"{'--':>10s}")
            linhas.append(f"{M:5.3f}" + "".join(campos))
        return "\n".join(linhas)
    partes = [titulo] if titulo else []
    partes.append(bloco(COLUNAS_AERO, "AERODYNAMIC COEFFICIENTS"))
    if "GYRO" in t:
        partes.append(bloco(COLUNAS_ESTAB, "STABILITY ANALYSIS"))
    return "\n\n".join(partes)


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
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(formatar(tabela(M437), f"SPIN-73 reconstruído -- {M437.nome}"))
