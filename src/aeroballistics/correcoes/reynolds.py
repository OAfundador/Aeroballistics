"""Efeito de escala (número de Reynolds) no arrasto: o que o SPIN-73 não tem como entrada.

O SPIN-73 trabalha só em calibres: um 5,56 mm e um 155 mm com a mesma forma têm o mesmo
CX0. Na realidade o atrito de parede depende do número de Reynolds, que no mesmo Mach é
proporcional ao tamanho. As constantes do SPIN-73 foram ajustadas a uma base dominada por
granadas de 90 a 175 mm e por 20 mm, e embutem o atrito dessa escala.

Correção (uma lei física, um parâmetro):

    ΔCX0 = [Cf(Re, M) − Cf(Re_ref, M)] · S_mol / S_ref
    Cf(Re, M) = 0,455 / (log10 Re)^2,58 · (1 + 0,144 M²)^−0,65   (Prandtl–Schlichting,
                                                                  compressibilidade de van Driest,
                                                                  a mesma forma do MC DRAG)
    Re = V·L/ν, com L o comprimento do projétil; Re_ref = V·L_ref/ν

L_ref, o único parâmetro, é o comprimento "típico" embutido nas constantes do SPIN-73.
S_mol/S_ref é a área molhada (ogiva em arco de círculo, cilindro, tronco do boattail)
sobre a área da seção, calculada da geometria de entrada.
"""
from functools import lru_cache

import numpy as np

A_SOM = 340.3          # m/s, atmosfera padrão ao nível do mar (59 °F, a do SPIN-73)
NU = 1.461e-5          # m²/s, viscosidade cinemática na mesma condição
ANG_BT = np.radians(8.0)   # ângulo do boattail (o SPIN-73 não recebe o ângulo; 7-10° nas fontes)


def cf(Re, M):
    Re = np.maximum(Re, 1e4)
    return 0.455 / np.log10(Re) ** 2.58 * (1.0 + 0.144 * M * M) ** -0.65


@lru_cache(maxsize=None)
def area_molhada(VL, VN, VB, OR, DM=0.0):
    """S_mol/S_ref, com S_ref = π d²/4; comprimentos em calibres (d = 1)."""
    R = max(OR, (VN * VN + 0.25) / 1.0 + 1e-9)       # não menor que o da ogiva tangente
    # arco que passa pela base da ogiva (x=0, r=0,5) e pela ponta (x=VN, r=DM/2)
    x1, r1, x2, r2 = 0.0, 0.5, VN, DM / 2.0
    mx, mr = (x1 + x2) / 2, (r1 + r2) / 2
    dx, dr = x2 - x1, r2 - r1
    q = np.hypot(dx, dr)
    h = np.sqrt(max(R * R - (q / 2) ** 2, 0.0))
    # centro do lado de dentro (abaixo da corda)
    xc, rc = mx + h * dr / q, mr - h * dx / q
    x = np.linspace(0.0, VN, 400)
    r = rc + np.sqrt(np.maximum(R * R - (x - xc) ** 2, 0.0))
    drdx = np.gradient(r, x)
    ogiva = np.trapezoid(2 * np.pi * r * np.sqrt(1 + drdx ** 2), x)
    cil = np.pi * 1.0 * max(VL - VN - VB, 0.0)
    rb = max(0.5 - VB * np.tan(ANG_BT), 0.2)
    bt = np.pi * (0.5 + rb) * VB / np.cos(ANG_BT)
    return (ogiva + cil + bt) / (np.pi / 4)


def delta_cx0(M, VL, VN, VB, OR, DM, d_mm, L_ref_m):
    """ΔCX0 de escala para um projétil de diâmetro d_mm no Mach M."""
    V = M * A_SOM
    L = VL * d_mm / 1000.0
    Re, Re_ref = V * L / NU, V * L_ref_m / NU
    return (cf(Re, M) - cf(Re_ref, M)) * area_molhada(VL, VN, VB, OR, DM)
