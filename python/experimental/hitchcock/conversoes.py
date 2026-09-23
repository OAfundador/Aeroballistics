"""Conversão dos coeficientes K do BRL (Hitchcock) para a normalização do SPIN-73.

Os coeficientes K do BRL definem as forças e momentos como K·ρ·d²·u²·δ (e potências
correspondentes de d para os momentos). Os coeficientes modernos usam ½ρV²·(πd²/4), o
que dá o fator π/8 entre as duas famílias:

    K_D = (π/8)·CX              CX  = (8/π)·K_D
    K_M = (π/8)·CMα             CMα = (8/π)·K_M
    K_L = (π/8)·(CNα − CX)      ->  CNα = (8/π)·K_L + CX
    K_H = (π/16)·|Cmq|          Cmq = −(16/π)·K_H   (o SPIN-73 usa q·d/2V; o BRL, q·d/V)

Os dois últimos são os que costumam dar errado, e por isso foram VERIFICADOS
numericamente contra o calibre 0.30 Ball M2 (ver test_cal030.py):

  - K_M: o CMα implicado pelo fator de estabilidade S medido (3,42), calculado com a
    fórmula de s_g do SPIN-73 e os momentos de inércia do próprio relatório, dá 1,286,
    contra 1,299 de (8/π)·0,51. Diferença de 1 %, dentro do arredondamento dos dados.
    Isso valida a conversão E a fórmula de estabilidade reconstruída, contra uma fonte
    independente e anterior ao SPIN-73.
  - K_H: o Cmq reconstruído nessa geometria em Mach 2,49 é −12,90, contra −13,24 de
    −(16/π)·2,6. O fator 2 entre q·d/V e q·d/2V é necessário; sem ele sobraria um fator
    de 1,95.
  - K_L: (8/π)·0,98 = 2,496 e o CNα reconstruído é 2,918, o que implica CX = 0,42; o
    gráfico de arrasto da p. 19 do relatório dá K_D ≈ 0,15 em Mach 2,5, ou seja CX ≈ 0,38.
    Compatível dentro da leitura do gráfico.

Posições: g (CG) e h (centro de pressão) são dados em calibres a partir da BASE.
O SPIN-73 mede do nariz: VCG = VL − g e CPN = VL − h.
"""
import math

PI_8 = math.pi / 8


def cx_de_kd(K_D):
    return K_D / PI_8


def cma_de_km(K_M):
    return K_M / PI_8


def cmq_de_kh(K_H):
    """Cmq na normalização do SPIN-73 (q·d/2V), negativo por convenção."""
    return -2 * K_H / PI_8


def cna_de_kl(K_L, CX):
    """K_L é força de vento cruzado: (π/8)(CNα − CX)."""
    return K_L / PI_8 + CX


def do_nariz(VL, distancia_da_base):
    return VL - distancia_da_base


# --- Fórmulas empíricas do próprio Hitchcock (p. 11 impressa) ---------------------
# Antecessoras diretas das equações do SPIN-73: mesma ideia, mesmas variáveis
# geométricas, mas SEM dependência de Mach.
def kn_hitchcock(ang_bt, len_bt, cilindro, ogiva, raio_ogiva):
    """K_N (força normal) para projéteis de ogiva ogival."""
    return (0.020 * ang_bt - 0.748 * len_bt + 0.1715 * cilindro
            + 0.540 * ogiva - 0.0266 * raio_ogiva)


def h_hitchcock(ang_bt, len_bt, cilindro, ogiva, raio_ogiva):
    """Centro de pressão em calibres a partir da base."""
    return (-0.0135 * ang_bt + 1.97 * len_bt + 0.6276 * cilindro
            + 0.4837 * ogiva - 0.0233 * raio_ogiva)
