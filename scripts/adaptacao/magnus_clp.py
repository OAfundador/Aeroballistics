"""
Identificação dos coeficientes E1, E2, E4 (Magnus) e G1 (Clp) a partir das
tabelas de saída do SPIN-73 -- primeira etapa da adaptação por tabelas.

Por que começar aqui: essas equações dependem só de VL, VN, VB e VCG, e os
coeficientes aparecem um por vez. Com UM projétil (175 mm M437) cada
coeficiente fica determinado exatamente por ponto de Mach. Os outros projéteis
servem de teste de PREVISÃO, não de ajuste.

Equações (relatório pp. 16-17):
  CYPA  = E1*VL - 0.1*VB
  CNPAN = -E1*VL*(Ek + 0.55*CXCL + 0.80*CVN) + VB*VL/4.7     (k = 2: 1 grau, 4: 5 graus)
  CPF   = -CNPAN/CYPA
  CLP   = G1*VL/5.51
com CXCL = VL - VN - VB - 1.5 e CVN = VN - 2.5.
"""
import numpy as np

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])

# ---------------------------------------------------------------------------
# Valores identificados. Os de E saíram "redondos" (2 casas) ao inverter a
# tabela do M437, o que sugere que são os próprios valores dos DATA. G1 só é
# conhecido com 3 casas (a precisão da coluna CLP impressa).
# ---------------------------------------------------------------------------
E1 = np.array([-.16, -.16, -.16, -.18, -.23, -.21, -.19, -.18] + [-.16] * 9)
E2 = np.array([1.80, 1.80, 2.00, 2.40, 2.70, 2.80, 2.90, 2.95, 2.98,
               3.00, 3.01, 3.02, 3.03, 3.04, 3.05, 3.05, 3.05])
E4 = np.array([2.90, 2.90, 3.00, 3.05] + [3.10] * 13)
# Termo de corpo longo, AUSENTE do texto do relatório, descoberto nas tabelas dos 20 mm
# 7 e 9 cal (ANSR), 10 cal (cone-cilindro) e 175 mm SRC: soma-se ao colchete de Magnus
# K_LONGO(M) * max(0, VL - 6). Verificado na razão 1 : 3 : 4 : 0,5 entre os quatro.
K_LONGO = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, .10, .20, .30, .30, .27, .25, .20])

G1 = np.array([-.036, -.036, -.035, -.029, -.025, -.024, -.024, -.024, -.023,
               -.023, -.023, -.022, -.022, -.021, -.020, -.019, -.019])

# ---------------------------------------------------------------------------
# Colunas transcritas das tabelas (scan DTIC em alta resolução)
# ---------------------------------------------------------------------------
R = lambda *v: np.array(v, float)
TABELAS = {
    "175MM M437 (p.65)": dict(
        VL=5.510, VN=2.910, VB=1.000,
        CYPA=R(-.982, -.982, -.982, -1.092, -1.367, -1.257, -1.147, -1.092, *[-.982] * 9),
        CPF1=R(3.155, 3.155, 3.335, 3.602, 3.715, 3.862, 4.019, 4.101, 4.215, 4.233,
               4.242, 4.251, 4.260, 4.269, 4.278, 4.278, 4.278),
        CPF5=R(4.143, 4.143, 4.232, 4.192, 4.086, 4.139, 4.201, 4.236, *[4.322] * 9),
        CLP=R(-.036, -.036, -.035, -.029, -.025, -.024, -.024, -.024, -.023, -.023,
              -.023, -.022, -.022, -.021, -.020, -.019, -.019)),
    "5/38 NAVY (p.53)": dict(
        VL=4.590, VN=2.150, VB=0.350,
        CYPA=R(-.769, -.769, -.769, -.861, -1.091, -.999, -.907, -.861, *[-.769] * 9),
        CPF1=R(2.205, 2.205, 2.396, 2.747, 2.970, 3.087, 3.208, 3.270, 3.331, 3.350,
               3.360, 3.369, 3.379, 3.388, 3.398, 3.398, 3.398),
        CPF5=R(3.255, 3.255, 3.350, 3.366, 3.357, 3.377, 3.400, 3.414, *[3.446] * 9),
        CLP=R(-.030, -.030, -.029, -.024, -.021, -.020, -.020, -.020, -.019, -.019,
              -.019, -.019, -.018, -.017, -.017, -.016, -.016)),
    "20MM 5 CAL ANSR (p.32)": dict(
        VL=5.000, VN=2.000, VB=0.000,
        CYPA=R(-.800, -.800, -.800, -.900, -1.150, -1.050, -.950, -.900, *[-.800] * 9),
        CPF1=R(2.225, 2.225, 2.425, 2.825, 3.125, 3.225, 3.325, 3.375, 3.405, 3.425,
               3.435, 3.445, 3.455, 3.465, 3.475, 3.475, 3.475),
        CPF5=R(3.325, 3.325, 3.425, 3.475, *[3.525] * 13)),
    "20MM 7 CAL ANSR (p.35)": dict(
        VL=7.000, VN=2.000, VB=0.000,
        CYPA=R(-1.12, -1.12, -1.12, -1.26, -1.61, -1.47, -1.33, -1.26, *[-1.12] * 9),
        CPF1=R(3.325, 3.325, 3.525, 3.925, 4.225, 4.325, 4.425, 4.475, 4.505, 4.525,
               4.635, 4.745, 4.855, 4.865, 4.845, 4.825, 4.775),
        CPF5=R(4.425, 4.425, 4.525, 4.575, *[4.625] * 6, 4.725, 4.825, 4.925, 4.925, 4.895, 4.875, 4.825)),
    "20MM 9 CAL ANSR (p.38)": dict(
        VL=9.000, VN=2.000, VB=0.000,
        CYPA=R(-1.44, -1.44, -1.44, -1.62, -2.07, -1.89, -1.71, -1.62, *[-1.44] * 9),
        CPF1=R(4.425, 4.425, 4.625, 5.025, 5.325, 5.425, 5.525, 5.575, 5.605, 5.625,
               5.935, 6.245, 6.555, 6.565, 6.485, 6.425, 6.275),
        CPF5=R(5.525, 5.525, 5.625, 5.675, *[5.725] * 6, 6.025, 6.325, 6.625, 6.625, 6.535, 6.475, 6.325)),
    "155MM M101/107 (p.59)": dict(
        VL=4.510, VN=2.450, VB=0.450,
        CYPA=R(-.767, -.767, -.767, -.857, -1.082, -.992, -.902, -.857, *[-.767] * 9),
        CPF1=R(2.277, 2.277, 2.465, 2.797, 3.004, 3.170, 3.294, 3.318, 3.388, 3.406,
               3.416, 3.425, 3.435, 3.444, 3.454, 3.454, 3.454),
        CPF5=R(3.312, 3.312, 3.404, 3.413, 3.390, 3.414, 3.444, 3.461, *[3.501] * 9),
        CLP=R(-.030, -.030, -.028, -.024, -.021, -.020, -.019, -.019, -.019, -.019,
              -.019, -.018, -.018, -.017, -.016, -.016, -.016)),
}


def _geo(t):
    return t["VL"], t["VB"], t["VL"] - t["VN"] - t["VB"] - 1.5, t["VN"] - 2.5


def identificar(t):
    """Inverte as equações para um projétil: devolve E1, E2, E4, G1 por Mach."""
    VL, VB, CXCL, CVN = _geo(t)
    e1 = (t["CYPA"] + 0.1 * VB) / VL
    colchete = lambda cpf: (VB * VL / 4.7 + cpf * t["CYPA"]) / (e1 * VL) - 0.55 * CXCL - 0.8 * CVN
    return e1, colchete(t["CPF1"]), colchete(t["CPF5"]), t["CLP"] * 5.51 / VL


def prever(t, e1=E1, e2=E2, e4=E4, g1=G1):
    """Aplica as equações do SPIN-73 à geometria de um projétil."""
    VL, VB, CXCL, CVN = _geo(t)
    cypa = e1 * VL - 0.1 * VB
    ext = K_LONGO * max(0.0, VL - 6.0)
    cpf = lambda ek: (e1 * VL * (ek + 0.55 * CXCL + 0.8 * CVN + ext) - VB * VL / 4.7) / cypa
    return dict(CYPA=cypa, CPF1=cpf(e2), CPF5=cpf(e4), CLP=g1 * VL / 5.51)


if __name__ == "__main__":
    np.set_printoptions(precision=4, suppress=True, linewidth=150)
    t0 = TABELAS["175MM M437 (p.65)"]
    e1, e2, e4, g1 = identificar(t0)
    print("Inversão exata a partir do M437 (antes de arredondar):")
    for n, v in (("E1", e1), ("E2", e2), ("E4", e4), ("G1", g1)):
        print(f"  {n}: {v}")
    print("\nPrevisão com os valores identificados, comparada às tabelas impressas")
    print("(diferença após arredondar a previsão para 3 casas, como o programa imprimia):")
    for nome, t in TABELAS.items():
        p = prever(t)
        print(f"\n  {nome}")
        for c in ("CYPA", "CPF1", "CPF5", "CLP"):
            if c not in t:                      # coluna não transcrita nesta tabela
                continue
            d = np.round(p[c], 3) - t[c]
            fora = [(float(m), round(float(x), 3)) for m, x in zip(MACH, d) if abs(x) > 0.0015]
            print(f"    {c:5s} max|dif| = {np.abs(d).max():.3f}   linhas fora de ±0.001: {fora or 'nenhuma'}")
