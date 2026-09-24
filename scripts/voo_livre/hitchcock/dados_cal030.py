"""Calibre 0.30: dados do compêndio de Hitchcock (BRL Report 620, AD-800 469, 1947/1952).

Fonte lida com `scripts/leitura/pagina_pdf.py` (páginas do PDF 21-25 = impressas 16-20).
Todas as dimensões em calibres; g e h são medidos a partir da BASE, que é a convenção do
relatório — o SPIN-73 mede do nariz, então VCG = VL − g e CPN = VL − h.

A velocidade do som usada pelo próprio relatório sai da sua tabela: 1990 ft/s = Mach 1,788
dá a = 1113 ft/s. É esse valor que converte as velocidades abaixo em Mach.

'?' = dígito duvidoso na leitura.
"""

A_SOM = 1990 / 1.788          # ft/s, implícita na tabela de estabilidade

# --- Características físicas (p. 18 impressa) -------------------------------------
# g em calibres da base; A (axial) e B (transversal) em grain·in².
FISICAS = {
    "Ball M1":      dict(desenho="B 10986",  peso_gr=172, rodadas=5,  g=1.827, A=1.751, B=16.40),
    "Ball M2":      dict(desenho="B 137545", peso_gr=151, rodadas=5,  g=1.455, A=1.332, B=12.13),
    "A.P. M2":      dict(desenho="B 138195", peso_gr=167, rodadas=10, g=1.980, A=1.855, B=20.15),
    "Tracer M1":    dict(desenho="B 16092",  peso_gr=149, rodadas=5,  g=2.097, A=1.777, B=18.57),
    # média com e sem a composição traçante: é com ela que o relatório calcula o K_M
    # "aparente" do Tracer M1 (nota da p. 20)
    "Tracer M1 medio": dict(desenho=None, peso_gr=142, rodadas=None, g=2.30, A=1.667, B=17.60),
    "Frangible M22": dict(desenho=None,      peso_gr=107, rodadas=5,  g=1.44,  A=1.043, B=9.06),
}

# --- Geometria dos esboços (p. 16 impressa; "ALL DIMENSIONS IN CALIBERS") ---------
# Os quatro esboços fecham pela soma das partes, que é a verificação de leitura:
#   Ball M1   0,81 + 1,20 + 2,43 = 4,44    Ball M2   1,32 + 2,43 = 3,75
#   A.P. M2   2,12 + 2,45 = 4,57           Tracer M1 2,30 + 2,45 = 4,75
# O Ball M2 aparece também na p. 19, onde o rótulo do total era ambíguo (3,75 x 3,78);
# a p. 16 confirma 3,75.
GEOMETRIA = {
    "Ball M1": dict(VL=4.44, VN=2.43, VB=0.81, OR=7.00, cilindro=1.20,
                    obs="boattail de 0,81 cal; canelura não modelada"),
    "Ball M2": dict(VL=3.75, VN=2.43, VB=0.0, OR=7.00, cilindro=1.32, obs="base reta"),
    "A.P. M2": dict(VL=4.57, VN=2.45, VB=0.0, OR=7.00, cilindro=2.12,
                    obs="afinamento de 0,31 cal na base, com ângulo marcado mas ilegível; "
                        "tratado como base reta. O A.P. M2 só tem K_M; comparar_cma_cal030.py "
                        "repete a comparação do CMα com VB = 0,31"),
    "Tracer M1": dict(VL=4.75, VN=2.45, VB=0.0, OR=7.00, cilindro=2.30, obs="base reta"),
    "Frangible T44": dict(VL=3.94, VN=2.32, VB=0.0, OR=7.91, cilindro=1.62,
                          obs="p. 19, zoom baixo, a reconferir; a nota da p. 18 diz que a M22 "
                              "tem o contorno do Ball M2, o que conflita com este esboço"),
}

# --- Inconsistência NA FONTE (não é erro de leitura) ------------------------------
# Com os momentos de inércia impressos, as três séries de tiro do Ball M1 violam em
# 9-12 % a identidade entre o fator de estabilidade S e o K_M do próprio relatório; os
# demais projéteis fecham em 1-4 %. A célula B = 16,40 foi relida em zoom: é tipografia
# limpa e inequívoca. Um B de 18,40 conciliaria as três séries (razões 0,97-1,00) e
# também poria o Ball M1 no padrão da fórmula empírica de inércia da p. 9, que os outros
# três seguem com razão 1,07-1,12. Fica como HIPÓTESE de erro tipográfico no original;
# o valor impresso não é alterado.
B_BALL_M1_HIPOTESE = 18.40

# --- Estabilidade (p. 20 impressa; passo de raia 10 polegadas = 33,33 cal) --------
# (projétil, relatório, rodadas, velocidade ft/s, Mach impresso, S, K_M)
ESTABILIDADE = [
    ("Ball M1", "BRL 276", 5, 1990, 1.788, 1.615, 1.24),
    ("Ball M1", "BRL 276", 7, 2672, 2.409, 1.901, 1.05),
    ("Ball M1", "BRL 276", 6, 2892, 2.571, 2.079, 0.96),
    ("Ball M2", "BRL 276", 5, 2574, None, 3.42, 0.51),
    ("A.P. M2", "BRL 276", 10, 2750, None, 1.42, 1.36),
    ("Tracer M1", "BRL 276", 10, 2528, None, 2.60, 0.73),   # coeficiente "aparente" (nota do relatório)
    ("Night Tracer M25", "APG 471.4/490-1", None, 2600, None, 2.52, 1.12),
    ("Frangible M22", "FT 0.30AC-U-1", None, 1370, None, 1.61, 0.89),
]

# --- Deriva e amortecimento (p. 20 impressa) -------------------------------------
# (projétil, relatório, velocidade ft/s, K_L, K_H, K_I)
AMORTECIMENTO = [
    ("Ball M1", "BRL 276 e 357", 2656, 0.77, 3.6, -0.15),
    ("Ball M2", "BRL 276 e 357", 2770, 0.98, 2.6, -0.09),
    ("Tracer M1", "BRL 276 e 357", 2734, 1.07, 5.4, -0.22),
    ("Frangible M22", "FT 0.30 AC-U-1", 1370, 0.98, 1.96, -0.06),
]

# Notas do relatório: o K_M do Tracer M1 é um "coeficiente de momento aparente", calculado
# do fator de estabilidade observado com a média dos momentos de inércia com e sem a
# composição traçante. O Night Tracer M25 tem o mesmo contorno do Tracer M1, e a
# Frangible M22 o mesmo do Ball M2 (nota da p. 18).

PENDENTE = """Night Tracer M25 (mesmo contorno do Tracer M1, sem momentos de inércia) e
A.P.I. T15 (sem dados de estabilidade) não entram nas comparações. A geometria da
Frangible T44 da p. 19 conflita com a nota da p. 18 e fica fora até ser relida."""
