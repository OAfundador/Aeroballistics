"""DATA XA1..XA15 (força axial CX) lidos no listing, p. 79 (JP2 0082).

XA1..XA10: statements de 2 linhas (9+8, 8+9 ou 12+5 valores); XA11 e XA12: 3 cartões
(7+7+3); XA13..XA15: 2 linhas (10+7). A contagem até 17 decide o número de zeros
iniciais de XA4, XA9, XA13, XA14 e XA15. '?' = dígito duvidoso.

XA13..XA15 só entram quando a ogiva passa de 3 calibres (DXN, cartões C164-C169);
nenhuma das tabelas usadas na validação tem VN > 3, então eles estão lidos mas não
testados.
"""
import numpy as np

XA = np.array([
 # XA1   (dois primeiros desbotados: decididos pelas tabelas, ver DECIDIDOS)
 [.2014, .2014, .2034, .2195, .2732, .3675, .4129, .4084, .3938,
  .3747, .3563, .3285, .3054, .2677, .2410, .203, .181],
 # XA2   (7o valor relido em zoom: -.0687; dois primeiros decididos)
 [.0057, .0057, .0057, .0029, -.0141, -.0324, -.0687, -.0694,
  -.0764, -.0740, -.0723, -.0695, -.0633, -.0559, -.0463, -.0463, -.0463],
 # XA3
 [.0121, .0121, .0121, .0181, .0052, .0152, .0441, .0426, .0476,
  .0415, .0384, .0325, .0265, .0123, .0044, .0044, .0044],
 # XA4   (6 zeros: a contagem fecha em 17)
 [0., 0., 0., 0., 0., 0., .0160, .0102, .0033,
  -.0082, -.0145, -.0251, -.0381, -.053, -.061, -.061, -.061],
 # XA5
 [-.0138, -.0138, -.0138, -.0367, -.0389, -.0399, -.0396, -.0349,
  -.0229, -.0192, -.0165, -.0138, -.0092, -.0106, -.0157, -.0157, -.0157],
 # XA6
 [.0128, .0128, .0128, .0382, .0410, .0379, .0293, .0262, .0182,
  .0157, .0132, .0099, .0059, .0043, .0043, .0043, .0043],
 # XA7
 [-.2295, -.2295, -.2295, -.2058, -.1944, -.1475, -.0892, -.0879,
  -.0828, -.0788, -.0749, -.0683, -.0652, -.0484, -.0330, -.0330, -.0330],
 # XA8
 [-.0071, -.0071, -.0071, -.0212, -.0197, -.042, -.0664, -.0586,
  -.0366, -.0240, -.0162, -.0034, .0103, .0261, .0370, .037, .037],
 # XA9   (3 zeros)
 [0., 0., 0., .0114, -.0016, .1216, .2278, .2253, .2023, .198,
  .1884, .1725, .1471, .1024, .0447, .0447, .0447],
 # XA10  (Mach 1,0 lido .02?)
 [.025, .025, .025, .04, .07, .02, .11, .10, .0963, .0967, .095, .09,
  .085, .070, .060, .050, .040],
 # XA11
 [.4, .4, .4, .55, .7, .725, .75, .8, .9, .85, .8, .745, .69, .65, .55, .55, .55],
 # XA12
 [.07, .07, .07, .11, .13, .15, .17, .21, .26, .37, .48, .73, .98, 1.45, 1.8, 1.8, 1.8],
 # XA13  (3 zeros)
 [0., 0., 0., .004, .006, .031, .050, .050, .044, .030,
  .025, .023, .018, .016, .015, .013, .012],
 # XA14  (5 zeros)
 [0., 0., 0., 0., 0., .040, .065, .060, .057, .053,
  .050, .047, .043, .040, .035, .027, .022],
 # XA15  (3 zeros)
 [0., 0., 0., .035, .040, .053, .055, .046, .030, .023,
  .020, .017, .010, .005, .004, .003, .002],
])

# Decididos pelas tabelas (linha XA 1-based, índice de Mach 0-based): (lido, decidido, evidência).
# As duas tabelas (175 mm M437 e 5"/38) dão pesos de SINAL OPOSTO ao XA2 (VNX − 2,5 = +0,41 e
# −0,35) e o mesmo peso 1 ao XA1, o que separa os dois.
DECIDIDOS = {
    (1, 0): (".2?? (desbotado)", .2014, "o CX de Mach 0,01 fica 0,002 abaixo do de 0,8 nas duas "
                                        "tabelas: degrau igual só pode vir do XA1"),
    (1, 1): (".2?? (desbotado)", .2014, "idem (as tabelas têm CX idêntico em 0,01 e 0,6)"),
    (2, 0): (".0157?", .0057, "igual ao 3o valor, como nos demais XA; as duas tabelas pedem .0064"),
    (2, 1): (".0157?", .0057, "idem"),
}
# Relido em zoom, confirmado pelas duas tabelas (que pediam -.0688):
RELIDOS = {(2, 6): ("-.0487", -.0687)}
