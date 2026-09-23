"""DATA XD1..XD4 (CX2, força axial de guinada) lidos no listing.

Fonte: fim da p. 80 (XD1 e o primeiro cartão de XD2, statements de 3 cartões: 7 + 7 + 3
valores) e início da p. 81 (resto de XD2, XD3, XD4). JP2 0083-0084.

Equação (código, cartão C213; igual ao texto da p. 15):
    CX2 = XD1 + XD2·CXCL + XD3·CRAT + XD4·VB − CNα
    CXCL = VL − VN − VB − 1,5      CRAT = VN²/OR − 0,40

Validação: duas tabelas com pesos muito diferentes para XD2 e XD3 — 175 mm M437 (0,10 e
−0,06) e 5"/38 (0,59 e 0,47). Fixando XD1 e XD4, lidos com segurança, as duas tabelas
dão duas equações por Mach para XD2 e XD3, e a solução devolve os valores lidos em Mach
0,01 / 0,6 / 0,9 / 1,0 / 1,05 / 1,35 / 2,0. Ver NOTAS_TRANSCRICAO.md, seção T9.
"""
import numpy as np

XD = np.array([
 # XD1: nítido; sobe de 0,5 em 0,5 até Mach 1,2 e desce no mesmo passo
 [4.5, 4.5, 5., 5.5, 6., 6.5, 7., 7.5, 8., 7.5, 7., 6.5, 6., 5.5, 5., 4.5, 4.],
 # XD2: 1o cartão nítido (p. 80); 2o cartão desbotado (p. 81)
 [.25, .25, .25, .25, .25, .3, .35, .4, .5, .5, .5, .5, .5, .6, .45, .4, .35],
 # XD3: desbotado nos três primeiros valores
 [.3, .3, .4, .5, .6, .7, .8, .9, 1., 1., 1., 1., 1., .8, .7, .6, .5],
 # XD4: sequência regular, de 0,1 em 0,1
 [-1., -1., -1., -.9, -.8, -.7, -.6, -.5, -.4, -.3, -.2, -.1, 0., 0., 0., 0., 0.],
])

# Decididos pelas tabelas (linha XD 1-based, índice de Mach 0-based): (lido, decidido, evidência)
DECIDIDOS = {
    (3, 2): (".?", .4, "5\"/38 (peso 0,47) pede +0,0996; completa a sequência .3 .3 .4 .5 .6"),
    (2, 9): ("ilegível", .5, "duas tabelas: 0,501"),
    (2, 12): (".6?", .5, "duas tabelas: 0,501 (XD3 = 0,998)"),
}

# Ainda duvidosos
DUVIDOSOS = {
    (2, 13): ".6? — só o M437 é confiável em Mach 2,5 (o CNA do 5\"/38 é suspeito ali) "
             "e ele deixa resíduo de +0,020",
}
