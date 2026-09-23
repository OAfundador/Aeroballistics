"""Blocos DATA XC1..XC17 do SPIN-73, lidos no scan (p. 80 impressa = JP2 0083).

Leitura desta tarefa (A). Página girada -90 graus; grade de caracteres do listing:
    x(coluna) = 1158 + (coluna - 6) * 19,2 px      (coluna 6 = marca de continuação)
Cada statement ocupa 2 cartões. As divisões observadas são:
    XC1  : 11 + 6
    XC2..XC16 : 8 + 9
    XC17 : 10 + 7
Ordem dos 17 valores = grade de Mach XMACH.

DEFEITO DA IMPRESSÃO (achado desta tarefa): as linhas y=1867 e y=1900 da página girada
são a MESMA imagem (correlação de pixels 0,90 contra 0,65 da linha vizinha, que tem o
mesmo prefixo de texto) e ambas trazem o rótulo "XC16". O cartão de continuação de XC15
foi substituído por uma segunda cópia do primeiro cartão de XC16. Logo XC15[8:17]
(Mach 1,2 a 5,0) NÃO existe no listing impresso: fica como np.nan aqui.

'?' nos comentários = dígito duvidoso.
"""
import numpy as np

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])

_n = np.nan

# XC1..XC5: leitura anterior (python/reconstrucao_F/xc_parcial.py), reconferida aqui
# nos dígitos marcados como duvidosos (ver NOTAS_A.md).
XC = np.array([
 # XC1  (11+6) -- 2o, 9o, 14o, 15o eram duvidosos na leitura anterior
 [1.71, 1.70, 1.66, 1.63, 1.60, 1.58, 1.56, 1.55, 1.57, 1.63, 1.70, 1.79, 1.88, 1.90, 2.03, 2.00, 1.97],
 # XC2  (8+9)  -- continuação começa em .5614 (índice 8), divisão 8+9 CONFIRMADA
 [.6995, .6995, .6995, .7224, .7301, .7314, .5611, .5614, .5614, .5595, .5553, .5324, .5195, .4993, .4867, .4867, .4867],
 # XC3
 [-.4425, -.4425, -.4425, -.3199, -.2661, -.2174, .1353, .1304, .1214, .1094, .0992, .0996, .0844, .0880, .1376, .1376, .1376],
 # XC4  -- divisão 8+9 CONFIRMADA (continuação = .1044,.1044,.1044,.1188,...)
 [-.2241, -.2241, -.2241, -.2241, -.2241, -.2241, .1044, .1044, .1044, .1044, .1044, .1188, .1188, .1188, .1188, .1188, .1188],
 # XC5
 [.0136, .0136, .0136, .0172, .0190, .0207, .0542, .0514, .0466, .0377, .0295, .0216, .0170, .0078, -.0014, -.0014, -.0014],
 # XC6  -- 7o valor (Mach 1,05) duvidoso: 0.0001? ; 2o valor lido 0.0449 (=1o e 3o)
 [.0449, .0449, .0449, .0413, .0395, .0377, .0001, -.0001, -.0006, -.0014, -.0021, -.0065, -.0093, -.0150, -.0207, -.0207, -.0207],
 # XC7
 [-.0016, -.0016, -.0016, -.0016, -.0016, -.0016, .0033, .0033, .0033, .0033, .0033, .0036, .0036, .0036, .0036, .0036, .0036],
 # XC8  -- 9o valor (-.6601) decidido pela regularidade 253/254 das diferenças
 [-.5470, -.5470, -.5470, -.5793, -.5955, -.6117, -.6854, -.6770, -.6601, -.6348, -.6094, -.5742, -.5429, -.4804, -.4178, -.4178, -.4178],
 # XC9
 [-.1383, -.1383, -.1383, .0278, .1109, .1939, .4924, .4636, .4061, .3199, .2336, .1217, .0431, -.1142, -.2714, -.2714, -.2714],
 # XC10
 [-.7422, -.7422, -.7422, -.7422, -.7422, -.7422, -.6280, -.6280, -.6280, -.6280, -.6280, -.6031, -.6031, -.6031, -.6031, -.6031, -.6031],
 # XC11
 [-.4712, -.4712, -.4712, -.4712, -.4712, -.4712, -.6396, -.6257, -.5977, -.5557, -.5138, -.4768, -.4303, -.3332, -.2361, -.2361, -.2361],
 # XC12 -- linha muito desbotada; ver NOTAS_A.md (5 células duvidosas)
 [-3.650, -3.670, -3.897, -4.174, -4.203, -2.936, -2.646, -1.314, -1.162, -.8054, -.6033, -.3949, -.2274, .1794, .1794, .1794, .1794],
 # XC13
 [-.9349, -.9349, -.9349, -1.748, -1.748, -1.748, -1.933, -1.933, -1.474, -1.474, -1.427, -1.427, -.9122, -.6300, -.6300, -.6300, -.6300],
 # XC14
 [.3306, .3306, .3306, .3306, -.7872, -.7672, -.9731, -.9731, -.6906, -.6906, -.5391, -.5391, .0271, .2332, .2332, .2332, .2332],
 # XC15 -- cartão de continuação AUSENTE do listing (ver cabeçalho): 8 primeiros lidos
 [0.0, 0.0, 0.0, 0.0, .6954, .7100, 1.0097, 1.0043, _n, _n, _n, _n, _n, _n, _n, _n, _n],
 # XC16 -- 7o valor: 11.766 numa cópia, 11.768 na outra (mesmo cartão impresso 2x)
 [0.0, 0.0, 0.0, 0.0, 5.0334, 5.9629, 11.766, 11.457, 9.1476, 8.4991, 7.6084, 6.6724, 6.1030, 6.1493, 6.1493, 6.1493, 6.1493],
 # XC17 (10+7) -- só entra quando VN > 3 (DNX > 0): nas 14 tabelas, só o 175 SRC
 [.35, .35, .35, .35, .35, .37, .44, .44, .44, .42, .35, .30, .30, .28, .28, .28, .28],
])

# Correções decididas pelo modelo (linha XC 1-based, índice de Mach 0-based): (lido, decidido).
# Ficam FORA de qualquer validação feita com as tabelas que as decidiram.
CORRECOES = {
    # A linha XC12 está desbotada. Em Mach 1,05 o valor lido não reproduz o CPN impresso
    # de nenhuma das duas tabelas testadas. Um único número corrige as duas ao mesmo tempo:
    # 175 mm M437 (peso 0,623) e 5"/38 (peso 0,154) pedem Delta = 0,9598 e 0,9616, e com
    # -1,684 os resíduos caem para +0,0008 e -0,0001. Ver NOTAS_TRANSCRICAO.md, seção T6.
    (12, 6): (-2.646, -1.684),
}

# Células cuja leitura visual ficou duvidosa (linha XC 1-based, índice de Mach 0-based).
DUVIDOSAS = {
    (6, 6): "0.0001? (glifo central apagado)",
    (12, 1): "-3.670? (linha desbotada; 1o valor -3.650 e 2o poderiam ser iguais)",
    (12, 5): "-2.936?",
    (12, 6): "-2.646?",
    (12, 8): "-1.162?",
    (12, 9): "-.8054?",
    (12, 10): "-.6033?",
    (16, 6): "11.766 / 11.768 (as duas cópias do cartão discordam)",
}

AUSENTES = {15: list(range(8, 17))}  # XC15: cartão de continuação não impresso

# Células do cartão ausente recuperadas pelas tabelas impressas (decididas pelo modelo).
# Método: em cada Mach, XC12 e XC15 são as duas incógnitas do bloco de boattail; as colunas
# CPN do 175 mm M437 e do 5"/38 dão duas equações. Onde o XC12 resolvido coincide com o
# valor LIDO no listing, o sistema está consistente e o XC15 obtido é confiável:
#   Mach 1,2 : XC12 resolvido -1,1630 contra -1,1620 lido  -> XC15 = 1,437
#   Mach 2,0 : XC12 resolvido -0,2266 contra -0,2274 lido  -> XC15 = 0,208
# Nos demais Mach a solução não fecha: em 1,35/1,5/1,75 o próprio XC12 está entre as
# células duvidosas, e de 2,5 a 5,0 o CNα impresso do 5"/38 é o que está sob suspeita
# (desvio de +0,014, seção T5 das notas). Ver NOTAS_TRANSCRICAO.md, seção T6.2.
RECUPERADOS = {(15, 8): 1.4366, (15, 12): 0.2079}
for (_linha, _j), _v in RECUPERADOS.items():
    XC[_linha - 1, _j] = _v

XC_LIDO = XC.copy()
for (_linha, _j), (_lido, _dec) in CORRECOES.items():
    assert abs(XC[_linha - 1, _j] - _lido) < 1e-9, (_linha, _j)
    XC[_linha - 1, _j] = _dec
