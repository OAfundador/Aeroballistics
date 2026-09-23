# O programa original, bloco a bloco

Descrição do SPIN-73 de 1973 com as nossas palavras e a nossa notação: o que cada trecho do
programa calcula, com que constantes, de onde veio a leitura, o que não foi possível ler e
onde está implementado nesta reconstrução. **Não é o código original**, que está no relatório
(DTIC AD0915628, listing nas pp. 79–86) e não é reproduzido neste repositório.

Gerado de `python/spin73/programa.py` (`python -m spin73.programa --doc`); a evidência de cada
leitura está em [NOTAS_TRANSCRICAO.md](NOTAS_TRANSCRICAO.md).

Notação: VL, VN, VB, VCG, OR, DM, BD, BOOM, DIA, IX, IY, WGT, TWIST, DGUN e TEMP são as
entradas do cartão; a1..a15, b1..b9, c1..c17, d1..d4, e1..e5, f1..f9 e g1 são os valores dos
blocos DATA XA, XB, XC, XD, XE, XF e XG no Mach da linha. "Statements" é a numeração
sequencial que o compilador imprimiu à esquerda de cada linha do listing.

## 1. Cartão de entrada e atmosfera

Lê o cartão (geometria em calibres; diâmetro, inércias e peso em unidades inglesas) e calcula a densidade do ar e a velocidade do som a partir da temperatura.

| | |
|---|---|
| Colunas | — |
| Dados | — |
| Statements do listing | — |
| Páginas | 76–77 (cartão); listing (atmosfera) |
| Fonte da leitura | Apêndice B e código |
| Implementação | `spin73.nucleo.densidade_ar` |

Fórmulas:

- ΔT = TEMP − 59 °F
- ρ = 0,002376 + (−4,784·ΔT + 0,01092·ΔT²)·10⁻⁶ slug/ft³
- a = 49,04·√(459,6 + TEMP) ft/s

Regras:

- no cartão original, campos em branco valem DM = 0, BD = 1,00 e TEMP = 0 °F; aqui os padrões são 0,12, 1,02 e 59 °F (passe zero para reproduzir o cartão em branco)

## 2. Força axial a guinada zero (CX)

Um polinômio nas variáveis de forma, mais três correções por trecho: ogiva longa, cilindro longo e boattail longo.

| | |
|---|---|
| Colunas | `CX` |
| Dados | XA |
| Statements do listing | C164–C174 |
| Páginas | 83–84 |
| Fonte da leitura | código (a partir de C164) e texto |
| Implementação | `spin73.nucleo.cx` |

Fórmulas:

- u = min(VN, 3) − 2,5;   L = VL − VN − VB − 1,5;   R = VN²/OR − 0,40
- β = 0 se VB ≤ 0,2;  VB − 0,2 se VB < 0,65;  0,45 daí em diante
- CX = a1 + a2·u + a3·u² + a4·u³ + a5·min(L, 1,5) + a6·min(L, 1,5)² + a7·β + a8·R + a9·R² + a11·(BD − 1,02) + a12·(DM − 0,12)² − 0,01·(BOOM/1,36)² − Δ_bt − Δ_og + Δ_cil

Regras:

- Δ_og, só com ogiva acima de 3 cal, em três trechos contínuos: a13·(VN − 3) até 3,48 cal; 0,48·a13 + a14·(VN − 3,48) até 3,97; e 0,48·a13 + 0,49·a14 + a15·(VN − 3,97) acima. O texto só documenta o primeiro trecho
- Δ_cil = 0,010·(L − 1,5) quando L > 1,5
- Δ_bt = a10·(VB − 0,65) quando VB ≥ 0,65

O que não se leu:

- o começo do cálculo está na p. 83, que não foi lida: o termo Δ_bt segue o texto do relatório, e a saída avisa quando ele é usado

## 3. Força normal, centro de pressão e momento de arfagem

Soma a força normal e o momento do corpo (ogiva e cilindro) com os do boattail; o centro de pressão sai da razão entre os dois, e o momento em torno do CG, do braço até o CG.

| | |
|---|---|
| Colunas | `CNA`, `CPN`, `CMA` |
| Dados | XB, XC |
| Statements do listing | C175–C212 |
| Páginas | 84–85 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.normal_e_momento` |

Fórmulas:

- v = min(VN, 3) − 2,47;   ℓ = VL − VN − VB − 2,15;   r = VN²/OR − 0,48;   m = DM − 0,17;   n = max(VN − 3, 0);   w = min(VB, 1)
- N_corpo = b1 + b2·v + b3·ℓ + b4·r + b5·v² + b6·ℓ²
- N_bt = b7·β_N + w·(b8·v + b9·ℓ)
- M_corpo = N_corpo·(c1 + c2·v + c3·v² + c4·v³ + c5·ℓ + c6·ℓ² + c7·ℓ³ + c8·r + c9·r² + c10·m + c11·r·v + c17·n)
- M_bt = (VL/4,7)·(c12·β_M + w·(c13·v + c14·ℓ + c15·r + c16·r·v))
- CNα = N_corpo + N_bt;   CPN = (M_corpo + M_bt)/CNα;   CMα = (VCG − CPN)·CNα

Regras:

- expoentes do boattail: β_N = VB e β_M = VB^0,8 abaixo de Mach 0,95; β_N = VB^1,5 e β_M = VB a partir de Mach 0,95 (o texto não diz o limiar); β_N = β_M = √VB quando VB > 1
- N_bt nunca soma: se sair positiva, vale zero (regra do código, ausente do texto; só age com ogiva curta no supersônico)
- se M_bt sair positivo, o boattail inteiro é descartado: CNα = N_corpo e M_bt = 0 (regra do código, ausente do texto)
- o termo c11 multiplica r·v; o texto imprime outra variável ali, erro tipográfico

O que não se leu:

- o cartão de continuação do XC15 (Mach 1,2 a 5) não foi impresso: valores recuperados pelas tabelas de saída
- a linha do XC12 está desbotada: células decididas pelas tabelas

## 4. Termo de guinada da força axial (CX2)

O termo que, somado ao CNα, dá o arrasto de guinada por sen² da guinada.

| | |
|---|---|
| Colunas | `CX2` |
| Dados | XD |
| Statements do listing | C213 |
| Páginas | 85 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.cx2` |

Fórmulas:

- CX2 = d1 + d2·L + d3·R + d4·VB − CNα   (L e R como no arrasto)

Regras:

- o arrasto de guinada é CX2 + CNα, não o CX2 (p. 15)

## 5. Força e momento de Magnus

A força de Magnus e, para três ângulos de ataque (1°, 2° e 5°), o centro de pressão dela e o momento em torno do CG.

| | |
|---|---|
| Colunas | `CYPA`, `CNPA`, `CPF1`, `CPF5`, `CNPA5` |
| Dados | XE |
| Statements do listing | C214–C231 |
| Páginas | 85 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.magnus` |

Fórmulas:

- Y = e1·VL;   CYPA = Y − 0,1·VB
- para cada ângulo, com e = e2 (1°), e3 (2°) ou e4 (5°):   N = −Y·(e + 0,55·L + 0,8·(VN − 2,5)) + VL·VB/4,7
- CPF = −N/CYPA + Δ_cl;   momento = (VCG − CPF)·CYPA

Regras:

- Δ_cl = e5·(VL − 6) quando VL > 6 (termo de corpo longo, ausente do texto)
- a 1° saem CPF1 e CNPA; a 5°, CPF5 e CNPA5; o valor a 2° é calculado e não entra em nenhuma coluna impressa

O que não se leu:

- o primeiro cartão do XE5 (Mach 0,01 a 1,75) não foi impresso: valores recuperados pelas tabelas de saída

## 6. "Coeficientes do polinômio" de Magnus (CNPA3, CNPA5P)

Duas colunas impressas que deveriam ajustar um polinômio ao momento de Magnus em três ângulos.

| | |
|---|---|
| Colunas | `CNPA3`, `CNPA5P` |
| Dados | — |
| Statements do listing | C278–C281 |
| Páginas | 86 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.coef_polinomio_magnus` |

Fórmulas:

- D = CNPA(5°) − CNPA(1°)
- CNPA5P = ((D + 0,3) − 9·D)/0,0072
- CNPA3 = (D − 0,0001·CNPA5P)/0,01

Regras:

- as constantes são as de um polinômio C1 + C3·δ² + C5·δ⁴ ajustado em δ = 0,1 e 0,3, mas o segundo ponto usa D + 0,3 no lugar do valor a 2°: as duas colunas carregam um único grau de liberdade e sempre obedecem a CNPA3 + 0,1·CNPA5P = 3,75 (defeito do original, reproduzido)
- o programa imprime "CNPA5" para esta coluna e "CNPA-5" para o momento a 5°; aqui são CNPA5P e CNPA5

## 7. Amortecimento em arfagem (CMQ)

Cmq + Cmα̇ na convenção qd/2V.

| | |
|---|---|
| Colunas | `CMQ` |
| Dados | XF |
| Statements do listing | C232–C238 |
| Páginas | 85 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.cmq` |

Fórmulas:

- λ = VL − 5;   g = VCG − 3
- K = f1 + f2·λ + f3·λ² + f4·g + f5·g·λ + f6·g·λ² + f7·g·VB + f8·VB
- CMQ = −5,093·K − Δ_cl

Regras:

- Δ_cl = f9·(VL − 6) quando VL > 6 (termo de corpo longo, ausente do texto)

O que não se leu:

- o segundo cartão do XF7 (Mach 1,1 a 2,5) não foi impresso: valores recuperados pela tabela do 5"/38

## 8. Amortecimento de rolamento (CLP)

Clp na convenção pd/2V, proporcional ao comprimento.

| | |
|---|---|
| Colunas | `CLP` |
| Dados | XG |
| Statements do listing | C239 |
| Páginas | 85 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.clp` |

Fórmulas:

- CLP = g1·VL/5,51

Regras:

- o divisor é uma constante do programa que o texto dá como 5,51, o comprimento do M437

## 9. Análise de estabilidade

Com diâmetro, massa, inércias e passo de raia: a rotação, os fatores de estabilidade giroscópica e dinâmica, e as frequências e taxas de amortecimento dos dois modos da guinada.

| | |
|---|---|
| Colunas | `GYRO`, `SBAR`, `RECIP`, `SBAR5`, `RECIP5`, `SPIN`, `W1`, `W2`, `L1`, `L2`, `L15`, `L25`, `DELT`, `DISP` |
| Dados | — |
| Statements do listing | C240–C266 |
| Páginas | 85–86 |
| Fonte da leitura | código e texto (pp. 17–18) |
| Implementação | `spin73.nucleo.estabilidade` |

Fórmulas:

- V = Mach·a (ft/s);   passo = TWIST·DGUN (polegadas por volta);   p = 2π·V/(passo/12) (rad/s)
- s_g = 1352,4·IX²/(ρ·IY·CMα·passo²·DIA³)   (IX, IY em lb·in²; comprimentos em polegadas)
- m = WGT/32,174;   d = DIA/12;   Ix = IX/(32,174·144);   Iy = IY/(32,174·144)   (pé e slug)
- k₁ = m·d²/Ix;   k₂ = m·d²/Iy
- s_d = 2·(CNα − CX + (k₁/2)·CNPA) / (CNα − CX − (k₂/2)·CMQ + (k₁/2)·CLP);   RECIP = 1/(s_d·(2 − s_d))   (SBAR5 e RECIP5 com o momento a 5°)
- σ = √(1 − 1/s_g);   ω₁,₂ = p·Ix/(2·Iy)·(1 ± σ)
- λ₁,₂ = (ρ·A/(4m))·[−CNα·(1 ∓ 1/σ) + (k₂/2)·(1 ± 1/σ)·CMQ ± (k₁/σ)·CNPA],   A = π·d²/4   (L15 e L25 com o momento a 5°)
- DELT = 6,28/(20·ω₁)
- DISP = (CNα − CX)·IY·(ω₁ − ω₂)·3,635/(CMα·WGT·DIA·V)

Regras:

- sem diâmetro (DIA = 0), não há análise de estabilidade
- com s_g < 1,001, só o Mach e o s_g são impressos
- a constante 1352,4 é a do código; a física com g = 32,174 daria 1349,8 (+0,19 %)
- o texto (p. 18) imprime trocado o sinal do primeiro termo de λ; o código e as tabelas usam o sinal acima

O que não se leu:

- DISP: a fórmula é a do código; a grandeza depende da referência 71 do relatório (Whyte 1970), indisponível

## 10. Impressão

Para cada Mach, uma linha com os 14 coeficientes aerodinâmicos e, com massa e raia, uma linha com as 14 colunas de estabilidade.

| | |
|---|---|
| Colunas | — |
| Dados | — |
| Statements do listing | C282–C294 |
| Páginas | 86 |
| Fonte da leitura | código |
| Implementação | `spin73.nucleo.formatar` |
