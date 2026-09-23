# Notas de transcrição e divergências

Fonte: scan DTIC AD0915628 (JP2, 96 páginas). Páginas citadas pela numeração impressa do relatório.

## T — Leituras decididas (Tabela 14, 175 mm M437, p. 65)

A impressão matricial confunde pares de glifos (6/8, 1/3, 2/5, 0/6). Nas células abaixo, a leitura visual era ambígua. A decisão veio de uma identidade **independente** da coluna em questão. Todas ficam fora das comparações em `test_m437.py` (conjunto `LEITURAS_DECIDIDAS`) para a validação não ser circular.

| Célula | Leitura ambígua | Decidido | Evidência |
|---|---|---|---|
| CX, Mach 0.01 e 0.60 | 0.1?5 | 0.105 | sd impresso (−0.071) só é reproduzido com 0.105 |
| SPIN, Mach 0.80 | 4?9.2 | 489.2 | p = Mach · a · 2π/(n·d) é exato nas demais linhas |
| CPF5, Mach 0.80 | 4.23? | 4.232 | CNPA5 = (VCG − CPF5)·CYPA |
| CPF5, Mach 0.95 | 4.0?6 | 4.086 | idem |
| L1, Mach 0.80 | −.000?42 | −.000382 | L1+L2 = 2K(−CNα + k₂⁻²/2·Cmq), sem termo de Magnus |
| SBAR5, Mach 1.35 | 1.?01 | 1.201 | RECIP5 impresso = 1/(sd(2−sd)) → 1.201 |
| L15, Mach 1.10 | −.00016? | −.000168 | L15+L25, como em L1 |
| RECIP5, Mach 1.05 | 1.06? | 1.068 | SBAR5 impresso (1.253) |

Também foram decididas no mesmo espírito, mas ainda sem teste dedicado: CMA em Mach 0.01 (4.384, via CPN), CMA em Mach 0.90 (5.708) e 1.10 (5.090), e CPN em Mach 1.10 (0.933).

## T2 — Magnus e Clp: identificação por tabelas (`magnus_clp.py`)

Com o M437, as equações de CYPA, CPF1, CPF5 e CLP se invertem exatamente por Mach. Os valores obtidos para E1, E2 e E4 caem a menos de 0,002 de números com duas casas (E1 = −0,16 no supersônico; E2 sobe de 1,80 a 3,05; E4 de 2,90 a 3,10). Adotamos os valores redondos como hipótese para os DATA originais. G1 fica igual à coluna CLP do M437, porque o VL de referência da fórmula (5,51) é o próprio VL do M437, e por isso só é conhecido com 3 casas.

**Teste de previsão:** aplicados ao 5"/38 e ao 155 mm M101, esses valores reproduzem CYPA, CPF1, CPF5 e CLP dentro de 1 unidade na 3ª casa em todas as linhas, exceto nas células abaixo. Todas são pares de glifos ambíguos.

| Tabela | Célula | Lido | Previsto |
|---|---|---|---|
| M437 | CPF5, Mach 1.10 | 4.236 | 4.238 |
| 5"/38 | CPF1, Mach 0.90 | 2.747 | 2.742 |
| M101 | CPF1, Mach 0.95 | 3.004 | 3.006 |
| M101 | CPF1, Mach 1.00 | 3.170 | 3.128 |
| M101 | CPF1, Mach 1.05 | 3.294 | 3.254 |
| M101 | CPF5, Mach 0.80 | 3.404 | 3.406 |

M101 CPF1 a Mach 1.20 foi relido com zoom: 3.388, e não 3.368 como na primeira leitura; confere com a previsão.

**A geometria de dois cabeçalhos foi decidida pelo modelo** (ver `cabecalhos_tabelas.csv`). Com as leituras visuais originais (M101: VL 4.910, VN 2.490, VB 0.490; 5"/38: VL 4.593), as previsões erravam de forma sistemática. As leituras decididas (4.510/2.450/0.450 e 4.590) são pares 9/5 e 3/0 e fazem três colunas independentes baterem ao mesmo tempo. Nesses dois projéteis, o teste valida o modelo e a leitura juntos, não separadamente.

E3 (Magnus a 2°) não aparece diretamente nas tabelas. Deve ser recuperável das colunas CNPA3/CNPA5, que parecem ser os coeficientes do polinômio em sin α ajustado aos três ângulos.

## E — Texto do relatório × comportamento das tabelas

**E1 (confirmado).** Taxas de amortecimento λ₁,₂, p. 18. O texto imprime −C_Nα(1 ± 1/σ). As tabelas só são reproduzidas com **−C_Nα(1 ∓ 1/σ)**; os demais termos ficam como impressos. Com o sinal do texto, o erro chega a ~3×10⁻⁴ 1/ft, da ordem do próprio valor. Com a correção, o erro fica abaixo de 10⁻⁶ em todas as linhas validadas. O sinal corrigido é o fisicamente esperado (compare com McCoy, *Modern Exterior Ballistics*, termo 2T−H). O teste `test_formula_do_texto_nao_reproduz` registra o achado.

**E2.** Termo C₁₁ de AMOMSQ: o texto escreve `CCRT · CYNN`. Tratado como erro tipográfico de CVNN.

**E3.** AMOMBT usa `VBTT`, mas o texto define `VBTI = CVL/4.7`, e CVL só é definido na seção de Magnus (CVL = VL). Implementado como VL/4.7.

**E4.** Magnus a 5°: o colchete está fora de lugar no texto. Seguida a forma usada a 1° e 2°.

**E5.** Expoentes A, B do boattail ("subsonic"/"supersonic"): o limiar de Mach não é dado. Assumido Mach ≥ 1.0 como supersônico.

**E6.** DXBT: o texto dá (VB − 0.65)·A₁₀. A linha 308 do listing parece ter outra forma (`XA10(J)*0.35 + (VB-1.0)*...`), ainda não lida com segurança.

**E7.** a₁₀ não aparece na soma principal de CX, só em DXBT; a₁₃ aparece só em DXN. Pode estar correto, mas vale conferir no listing.

**E8.** Os "IF" do texto usam desigualdades estritas (0 < VN < 3). O tratamento das igualdades foi assumido.

## A — Em aberto

**A1 (resolvido, ver T8).** O fator giroscópico sg calculado ficava sistematicamente ~0,17 % abaixo do impresso. É um viés constante em todas as linhas, não ruído. O ρ implícito é ≈ 0.002372 slug/ft³, contra 0.002376 da fórmula do listing (linha 92). Hipóteses: outra constante de conversão (g, 144), outro valor de ρ usado no cálculo de sg, ou algum dígito de Ix. As frequências W1/W2 herdam o resíduo via σ. Os testes usam tolerância de 0,3 %.

**A2.** DELT e DISP não foram implementados. DELT parece ser 2π/(20·W1) (bate em Mach ≥ 0.6, mas não em 0.01). DISP depende da referência 71 (Whyte 1970), que não temos.

**A3.** Coeficientes de ajuste: E1, E2, E4 e G1 identificados por tabelas (seção T2). Os demais (a, B, C, D, E3, F) seguem pendentes.

**A4.** As tabelas das pp. 44 (90 mm M71) e 47 (105 mm M1) têm cabeçalhos idênticos. Pode ser a mesma geometria normalizada ou uma página duplicada; falta comparar os corpos.

## T3 — Geometria das 14 tabelas e termo de corpo longo no Magnus

**Geometria.** VL e VB saem do CYPA em dois regimes (E1 = −0,16 supersônico e −0,23 a Mach 0,95). VN sai de CPF1 e CPF5. Resultado em `geometria_decidida.csv`. Os valores de E1 no transônico se confirmam como múltiplos exatos em todas as tabelas legíveis.

**Termo ausente do texto (confirmado).** Nos projéteis com VL > 6, CPF1 e CPF5 ficam acima do previsto no supersônico, e o excesso é o mesmo nas duas colunas. Ele se ajusta exatamente a K(M)·max(0, VL − 6) somado ao colchete de Magnus, com K = 0,10 / 0,20 / 0,30 / 0,30 / 0,27 / 0,25 / 0,20 em Mach 1,5 / 1,75 / 2 / 2,5 / 3 / 4 / 5 e zero abaixo. A razão entre 7 cal, 9 cal, 10 cal e 175 SRC é 1 : 3 : 4 : 0,5. Com o termo, 5, 7 e 9 cal ANSR são reproduzidos exatamente (`test_magnus.py`). O 175 SRC fica ~0,005 acima: em aberto.

**Página duplicada.** As pp. 44 (90 mm M71) e 47 (105 mm M1) têm corpos idênticos, com os mesmos artefatos de impressão. A tabela do 105 mm M1 não está no scan.

## T4 — Tentativa de reconstruir B1..B9 (CNα), em `reconstrucao_B/`

Com 10 tabelas de OR conhecido, o sistema tem 10 equações para 9 incógnitas por Mach. O ajuste atinge resíduo máximo de ~0,004, oito vezes o arredondamento da impressão (0,0005). Em Mach 0,95 o resíduo chega a 0,03. A matriz é mal condicionada: o menor valor singular é 0,1 % do maior. Os B obtidos não são redondos e não são confiáveis. Fixar B8 e B9 com os valores lidos no DATA XB8/XB9 (p. 80) PIORA o ajuste, então essa associação não está confirmada.

Conclusão: com os dados atuais, B não está reconstruído. As causas possíveis, sem ordem de probabilidade: erros de leitura no CNA, termos ausentes do texto (o texto define CDMM, CBBD e DNX na seção de CNα, mas não os usa em CNAB) ou o limiar sub/supersônico dos expoentes do boattail (E5).

## T5 — CNα reconstruído a partir dos blocos DATA (sessão noturna)

**Estrutura do programa (DIMENSION, p. 79).** O listing declara XA1..XA15, XB1..XB10, XC1..XC17, XE1..XE4, XF1..XF9 e XG1. O texto do relatório só descreve a1..a13, B1..B9 e F1..F8. Existem, portanto, pelo menos A14, A15, B10 e F9 que o texto não documenta, o que é coerente com o termo de corpo longo do Magnus (T3). A grade de Mach está em `DATA XMACH`: 0,01, 0,6, 0,8, 0,9, 0,95, 1,0, 1,05, 1,1, 1,2, 1,35, 1,5, 1,75, 2, 2,5, 3, 4, 5. Confirmado.

**XB1..XB9 lidos** (pp. 79–80, JP2). XB1 bate com os B1 do ajuste por MMQ onde ele era estável (por exemplo, 2,40 / 2,49 / 2,60 em Mach 1,2 / 1,35 / 1,5), o que confirma XB ↔ B.

**Limiar do expoente do boattail:** o programa já usa o expoente supersônico em Mach 0,95. Com o limiar em 1,0, as quatro tabelas com boattail erravam −0,15 nessa linha; com 0,95 o erro some. Isso resolve o item E5.

**Resultado:** com os XB lidos, 65 % das 170 células (10 tabelas × 17 Mach) ficam dentro do arredondamento (±0,0015). Seis correções de leitura sobem esse número para 78 % (91 % dentro de ±0,005). Cada correção é um único número que zera o resíduo de 7 ou mais tabelas ao mesmo tempo e corresponde a um par de glifos confundível (lista em `reconstrucao_B/xb_lidos.py`, `CORRECOES`). Nenhuma foi reconferida na imagem.

**O que sobra:**

- A tabela da p. 44 (90 mm M71) erra em quase todo Mach. A transcrição dela é a mais degradada, e mudar a geometria não resolve.
- O 5"/38 fica +0,014 constante de Mach 2,5 a 5. Suspeita: leitura do CNA (2,953 / 2,929 / 2,829 / 2,729).
- A linha de Mach 2,0 nos ANSR e algumas células isoladas estão listadas em `test_cna.py` (`PENDENTES`).

**Primeira comparação com experimento (7,62 NATO, MR 1833, M ≥ 1,1).** O CNα reconstruído concorda com M-59 (+0,01), M-61 (−0,01) e M-62 (−0,08); a dispersão experimental é de 0,2–0,3. No M-80, o mais curto, o SPIN-73 superestima em +0,28: ele prevê CNα maior para o projétil mais curto, e o experimento mostra o contrário. O resultado não depende do raio de ogiva, que é incerto nessa família. É um alvo claro para a recalibração do termo de comprimento (B3/B6) em corpos curtos.

## T6 — DATA XC e o centro de pressão (tarefa A, com validação numérica)

**Leitura.** XC1..XC17 lidos na p. 80 (`python/reconstrucao_C/xc_lidos.py`). A grade de caracteres do listing na página girada é x(coluna) = 1158 + (coluna − 6)·19,2 px. Divisão dos statements: XC1 em 11+6, XC2..XC16 em 8+9, XC17 em 10+7.

**Defeito da impressão (achado).** As linhas y = 1867 e y = 1900 da p. 80 girada são a mesma imagem (correlação de pixels 0,90, contra 0,65 de uma linha vizinha com o mesmo prefixo) e ambas trazem o rótulo XC16: o cartão de continuação de XC15 foi substituído por uma segunda cópia do primeiro cartão de XC16. Ou seja, **XC15 de Mach 1,2 a 5,0 não existe no listing impresso**. As duas cópias ainda discordam num dígito (11.766 e 11.768 no 7º valor de XC16), o que mostra que a diferença é de impressão, não de conteúdo.

**Validação no 175 mm M437 (p. 65).** Com a equação da p. 15 e os XB do CNα, o CPN e o CMα calculados batem com os impressos dentro de 0,0007 em Mach 0,01, 0,90 e 1,10 — os três pontos em que os doze coeficientes estão lidos sem dúvida. Isso valida ao mesmo tempo a estrutura da equação (inclusive as correções E2 e E3 de texto) e a leitura dos coeficientes.

**Em aberto.** Nos demais Mach o resíduo se concentra na linha XC12, que está desbotada: Mach 0,6 (−0,016), 0,8 (−0,032), 0,95 (−0,003), 1,0 (−0,008) e 1,05 (−0,598). Atribuindo todo o resíduo a C12, a tabela implicaria −3,6541 / −3,8644 / −4,1997 / −2,9249 / −1,6862. Nenhum é troca limpa de um dígito, então não está provado que o erro é só de C12. Em Mach ≥ 1,2 vale o mesmo para XC15: resolvido pela coluna do M437, daria 1,447 / 2,076 / 1,088 / 0,551 / 0,202 / −2,474 / −0,915 / −0,921 / −0,919, sequência irregular demais para uma linha de DATA. Todos esses são valores decididos pelo modelo e ficam fora de qualquer validação feita com o próprio M437. **O que falta para separar: a coluna CPN de outra tabela com boattail** (5"/38 p. 53, M101 p. 59 ou XM380E5 p. 50) e de uma sem boattail (ANSR), que isolam C1..C11 de C12..C16.

## T7 — Leitura de glifo por moldes (tarefa D)

Método: na linha do listing a impressora tem passo fixo (~19,2 px por coluna). Ajustando origem e passo, cada caractere é recortado; os de leitura segura formam, para cada dígito, um molde de probabilidade de tinta, e o glifo duvidoso é comparado com cada candidato por verossimilhança de Bernoulli com desbotamento (desbotamento só remove tinta; tinta fora do molde do candidato pesa contra ele).

Aplicado aos 10 dígitos em disputa das 6 correções de XB (seção T5), o método concorda com a decisão numérica em 8 e discorda em 2 — justamente os de pior taxa de erro na calibração.

| Correção | Veredito do molde | Efeito numérico |
|---|---|---|
| B3 Mach 1,0: −.0155 → −.0305 | confirma os dois dígitos | mantém |
| B2 Mach 1,2: −.0417 → −.0617 | confirma | mantém |
| B7 Mach 1,5: −.1490 → −.1695 | confirma os dois dígitos | mantém |
| B5 Mach 2,5: .0667 → .0609 | 3º dígito 0, mas 4º dígito 7, ou seja .0607 | diferença de 0,0002: indiferente |
| B4 Mach 0,01: −.0856 → −.0898 | 3º dígito 9, mas 4º dígito 6 (molde 6/8, o pior: 7 erros em 77) | a igualdade com Mach 0,6 continua favorecendo −.0898 |
| B3 Mach 1,2: −.0100 → −.0106 | mantém o 0 lido, mas com margem marginal | com −.0100, três tabelas (7, 9 e 10 cal) saem do arredondamento |

Contagem de CNα dentro de ±0,0015, sem a p. 44 (153 células): XB atual 133, XB como lido 111, XB pelos vereditos de glifo 130. Conclusão: as correções B3@1,0, B2@1,2 e B7@1,5 passam a ter leitura objetiva e evidência numérica; B5@2,5 vira .0607; B4@0,01 e B3@1,2 seguem decididas pelo modelo, com o molde discordando dentro da sua própria margem de erro.

## T6.1 — XC testado numa segunda tabela, e a célula XC12 em Mach 1,05

Para separar um erro de leitura em C1..C11 de um erro em C12..C16, transcrevi as colunas CMA e CPN do **5"/38 NAVY (p. 53)**, que tem boattail de 0,35 cal contra 1,00 cal do M437 — os pesos dos dois blocos mudam muito entre os dois. Os dados estão em `python/reconstrucao_C/dados_cpn.py`; a leitura foi conferida célula a célula pela identidade CMA = (VCG − CPN)·CNα com o CNα impresso, que resolveu duas delas (CPN de Mach 0,01 e CMA de Mach 0,90, este último um par 4/8).

**Usar o CNα impresso em vez do reconstruído.** O erro do CNα reconstruído (até 0,002) entra no CPN multiplicado por cerca de 3. Com o CNα impresso, o resíduo do CPN em Mach 0,95 do M437 cai de −0,0029 para +0,0007, ou seja, dentro do arredondamento. `cpn_spin73.cpn_cma` aceita `cna_impresso` justamente para isso.

**Resultado.** Com o CNα impresso, a conta fecha dentro de ±0,0015 em Mach 0,90, 0,95 e 1,10 no M437 e em 0,90, 1,00 e 1,10 no 5"/38 — duas geometrias diferentes, os mesmos dezessete coeficientes. Isso valida a estrutura da equação e a leitura de XC nesses pontos.

**XC12 em Mach 1,05 (decidido pelo modelo).** O valor lido, −2,646, não reproduz nenhuma das duas tabelas. Testando cada coeficiente como candidato único — o Δ implicado por uma tabela tem de ser igual ao implicado pela outra —, só XC12 dá razão 1,00: as duas pedem Δ = 0,9598 e 0,9616. Com **XC12 = −1,684** os resíduos caem para +0,0008 (M437) e −0,0001 (5"/38). O recorte da linha no listing é ambíguo nos três decimais (a linha está desbotada), então o valor fica registrado como decidido pelo modelo em `xc_lidos.CORRECOES`, e Mach 1,05 sai da validação nas duas tabelas.

**O que continua aberto.** Mach 0,6 e 0,8: as duas tabelas erram, mas nenhum coeficiente isolado explica as duas ao mesmo tempo (os candidatos com razão perto de 1 exigiriam quebrar a repetição de valores da própria linha, como XC3 em 0,6, que é igual nos índices 0, 1 e 2). Provavelmente são duas células erradas na mesma coluna. Mach 1,0: só o M437 erra (+0,008); o 5"/38 fecha. Mach 0,01: o M437 fecha e o 5"/38 erra +0,011, o que depende de qual das duas leituras do CPN está certa (0,769 ou 0,779). Uma terceira tabela sem boattail (ANSR) resolveria os três casos, porque zera todo o bloco C12..C16.

## T6.2 — Duas células do cartão ausente de XC15 recuperadas

Em cada Mach acima de 1,1, o bloco de boattail do CPN tem duas incógnitas: XC12 (linha desbotada, com várias células duvidosas) e XC15 (cartão não impresso). As colunas CPN do M437 e do 5"/38 dão duas equações, então o par sai resolvido — e o **teste de consistência é o próprio XC12**, que foi lido no listing e não entrou na conta.

| Mach | XC12 lido | XC12 resolvido | XC15 resolvido | Leitura |
|---|---|---|---|---|
| 1,2 | −1,1620 | −1,1630 | **1,4366** | fecha: XC15 confiável |
| 1,35 | −0,8054 | −0,8157 | 2,0042 | XC12 difere 0,010: é uma das células duvidosas |
| 1,5 | −0,6033 | −0,6192 | 0,9767 | idem, difere 0,016 |
| 1,75 | −0,3949 | −0,3867 | 0,6082 | difere 0,008 |
| 2,0 | −0,2274 | −0,2266 | **0,2079** | fecha: XC15 confiável |
| 2,5 | 0,1794 | 0,5642 | 0,2496 | não fecha: o CNα impresso do 5"/38 é suspeito de Mach 2,5 a 5 (seção T5) |
| 3,0 | 0,1794 | — | — | CPN do 5"/38 ilegível |
| 4,0 / 5,0 | 0,1794 | 0,1938 / 0,1985 | −0,819 / −0,784 | mesma suspeita do CNα |

Os dois valores confiáveis entraram em `xc_lidos.RECUPERADOS` e são aplicados a XC, marcados como decididos pelo modelo; Mach 1,2 e 2,0 ficam fora da validação por serem circulares.

**Como fechar o resto.** Uma terceira tabela com boattail (155 mm M101 p. 59, ou 105 mm XM380E5 p. 50) dá três equações para as mesmas duas incógnitas: sobra um grau de liberdade para detectar qual célula está errada, em vez de só resolver o sistema. É o próximo passo natural, junto com a releitura do CNα do 5"/38 acima de Mach 2,5.

## T6.3 — Tabela sem boattail confirma o bloco C1..C11

No 20 mm 5 cal ANSR (p. 32) o boattail é zero, o que zera C12..C16 e deixa o CPN dependendo só de C1..C11. A página está muito carregada de tinta e não permite leitura de 3 casas, mas em todos os Mach legíveis o CPN calculado fica dentro da incerteza da leitura (±0,02): 1,459 contra 1,45 lido em Mach 0,6; 1,419 contra 1,43 em 0,8; 1,449 contra 1,44 em 1,1. Não há erro grosseiro em C1..C11 — o que resta dos resíduos vem do bloco de boattail, como a linha XC12 desbotada já indicava.

## T8 — O que o código (pp. 84-85) resolveu

Transcrição parcial em `original/listing_p84-86.f`. O listing não traz número de cartão nas colunas 73-80 em quase todas as linhas; a numeração usada aqui (Cnnn) é a sequência de statements do compilador, impressa à esquerda.

- **A1, viés de s_g — resolvido.** O cartão C241 calcula `STAB = 1352.4*XY*TT/(IR*RHO*FC*CMA)`. Com Ix, Iy em lb·in² e comprimentos em polegadas, isso é s_g = 1352,4·Ix²/(ρ·Iy·CMα·passo²·d³). A fórmula física com g = 32,174 dá 1349,8 no lugar de 1352,4: a diferença, +0,19 %, era o viés. Com a constante do código, o GYRO do M437 fecha em todas as linhas (erro máximo 0,0009, viés médio 0,017 %).
- **E5, limiar do boattail — confirmado no código.** `IF(J.GE.5)` no cartão C189, com J a partir de 1: o expoente supersônico vale desde Mach 0,95.
- **A13, A14, A15 — onde entram.** O DXN do CX tem três trechos, com quebras em VN = 3,48 e 3,97: (VN − 3)·A13; 0,48·A13 + (VN − 3,48)·A14; 0,48·A13 + 0,49·A14 + (VN − 3,97)·A15. Os coeficientes 0,48 e 0,49 são exatamente as larguras dos trechos anteriores, o que torna o DXN contínuo. O texto do relatório só documenta o primeiro trecho.
- **Termo de corpo longo do Magnus = XE5.** Cartões C216-C222: se VL > 6, `DCPF = (VL−6)*XE5(J)` soma-se ao CPF depois do colchete. Os valores de K identificados pelas tabelas (seção T3) são o XE5. Para VB = 0, somar ao CPF ou dentro do colchete dá o mesmo resultado — por isso a identificação pelas tabelas ANSR funcionou —, mas com boattail as duas formas diferem.
- **Regra do boattail no CPN, ausente do texto.** Cartões C209-C210: se o momento do boattail (AMOMBT) sair positivo, o programa faz CNAT = CNAB e AMOMBT = 0, descartando toda a contribuição do boattail.
- **Cmq (C232-C238) e Clp (C239)** confirmam as formas já usadas; o Clp divide por SFNG, que no texto é 5,51.

Dúvida de transcrição: o cartão C205 foi lido `IF(CART.GT.0.0) CNPT=0.0`. A leitura mais provável é `IF(CNBT.GT.0.0) CNBT=0.0` (zerar a força normal do boattail se ela sair positiva), mas os nomes não conferem com nenhuma variável do trecho; não foi implementado até a releitura.

## T9 — DATA XD (CX2) e o cartão final do XE5

**Leitura.** XD1 e o primeiro cartão de XD2 no pé da p. 80, nítidos; o resto na p. 81, desbotado. Os statements aqui são de três cartões (7 + 7 + 3 valores). XD1 sobe de 0,5 em 0,5 até Mach 1,2 e desce no mesmo passo; XD4 vai de −1 a 0 de 0,1 em 0,1. Dados em `python/reconstrucao_D/xd_lidos.py`.

**Validação com duas tabelas.** Na equação CX2 = XD1 + XD2·CXCL + XD3·CRAT + XD4·VB − CNα, o 175 mm M437 dá pesos 0,10 e −0,06 a XD2 e XD3; o 5"/38, 0,59 e 0,47. Fixando XD1 e XD4, cada Mach dá duas equações para XD2 e XD3, e a solução devolve os valores lidos em 0,01 / 0,6 / 0,9 / 1,0 / 1,05 / 1,35 / 2,0. Usou-se o CNα IMPRESSO de cada tabela, para isolar o XD do erro do CNα reconstruído.

| Célula | Leitura | Decisão | Evidência |
|---|---|---|---|
| XD3, Mach 0,8 | .? | 0,4 | 5"/38 pede +0,0996; completa .3 .3 .4 .5 .6 |
| XD2, Mach 1,35 | ilegível | 0,5 | duas tabelas: 0,501 |
| XD2, Mach 2,0 | .6? | 0,5 | duas tabelas: 0,501 (com XD3 = 0,998) |
| XD2, Mach 2,5 | .6? | mantido, duvidoso | só o M437 é confiável ali; resíduo +0,020 |

**Erros na transcrição antiga do M437 (`m437_tabela.csv`), achados pelo XD:**

| Célula | Transcrito | Scan relido | DATA XD | Situação |
|---|---|---|---|---|
| CX2, Mach 1,05 | 4,567 | **4,507** | 4,506 | corrigido pela releitura |
| CX2, Mach 0,8 | 2,603 | 2,6?3 (ambíguo) | 2,805 | fica como transcrito; fora da validação |
| CX2, Mach 1,1 | 5,132 | ilegível | 5,002 | fica como transcrito; fora da validação |

Em aberto: resíduo de 0,007 a 0,009 no M437 em Mach 1,5 e 1,75, onde o 5"/38 fecha exato.

**XE5.** Na p. 81, entre o XE4 (statement 56) e o XF1 (58), o cartão de continuação `1 0.3,0.3,0.27,0.25,0.20/` aparece impresso duas vezes e o statement 57 falta — o mesmo defeito do XC15 (seção T6). Os cinco valores impressos (Mach 2 a 5) são **exatamente** os do termo de corpo longo que as tabelas de 7, 9 e 10 calibres tinham identificado (seção T3). Os 12 primeiros valores, do cartão que não foi impresso, continuam vindo das tabelas.

## T10 — DATA XA (CX) e o programa completo

**Leitura** (p. 79, `python/reconstrucao_A/xa_lidos.py`). XA1..XA10 em statements de 2 linhas; XA11 e XA12 em 3 cartões (7 + 7 + 3); XA13..XA15 em 2 linhas (10 + 7). A contagem até 17 decide o número de zeros iniciais de XA4 (6), XA9 (3), XA13 (3), XA14 (5) e XA15 (3). XA1 tem forma de curva de arrasto (0,20 subsônico, pico de 0,41 em Mach 1,05, 0,18 em Mach 5).

**Validação com duas tabelas.** O 175 mm M437 e o 5"/38 dão ao XA2 pesos de sinal oposto (VNX − 2,5 = +0,41 e −0,35) e ao XA7 pesos bem diferentes (boattail de 1,00 e 0,35 cal). Com a leitura final, **o CX fecha em 17 de 17 Mach nas duas tabelas** (erro máximo 0,0011 e 0,0013). A coluna CX do 5"/38 foi transcrita nesta sessão (`dados_cx.py`).

| Célula | Leitura | Decisão | Evidência |
|---|---|---|---|
| XA2, Mach 1,05 | −,0487 (zoom baixo) | **−,0687**, relido em zoom | as duas tabelas pediam −,0688 (par 4/6) |
| XA10, Mach 1,0 | ,02 (parecia fora da sequência) | mantido | as duas tabelas fecham com ,02 |
| XA1, Mach 0,01 e 0,6 | ,2?? (desbotado) | ,2014 | o CX desses Mach fica 0,002 abaixo do de 0,8 nas duas tabelas; degrau igual só pode vir do XA1 (peso 1 em ambas) |
| XA2, Mach 0,01 e 0,6 | ,0157? | ,0057 | igual ao 3º valor, como em quase todos os XA; as duas tabelas pedem ,0064 |

O CX = 0,105 do M437 em Mach 0,01 e 0,6, que tinha sido decidido pelo s_d impresso (seção T), bate com o DATA — mas essas duas linhas ficam fora da validação do XA, porque decidiram XA1 e XA2 ali.

XA13..XA15 (ogiva maior que 3 calibres) estão lidos mas **não testados**: nenhuma tabela transcrita tem VN > 3. O candidato é o 175 mm SRC (p. 68, VN = 5,5).

**O programa completo.** Com o XA, `spin73.tabela()` roda da geometria até a análise de estabilidade. No M437 fecham 17 de 17: CX, CYPA, CNPA, CPF1, CNPA5, CLP, SPIN e RECIP5. As falhas restantes (CPN, CMα e, por consequência, s_g, ω e λ) estão todas nos Mach em que o XC não está completo: o XC12 desbotado e o cartão ausente do XC15.

## T11 — XC completo: decisões finais e o que ficou incerto

Com XA e XD reconstruídos, o XC era o último bloco com lacunas. Decisões (`python/reconstrucao_C/xc_lidos.py`):

| Célula | Leitura | Decisão | Evidência | Confiança |
|---|---|---|---|---|
| XC1, Mach 0,8 | 1,66 | **1,68** | único candidato compatível com as duas tabelas; par 6/8; zera os dois resíduos (M437 +0,036 → −0,002; 5"/38 +0,024 → 0,000) | alta |
| XC12, Mach 0,6 | −3,670 | −3,650 | igual ao de Mach 0,01, como em XC2..XC11; melhora as duas tabelas | média (M437 fica a −0,004) |
| XC15, Mach 1,35 / 1,5 / 1,75 / 4 / 5 | cartão ausente | pelo M437 | conferido no 5"/38 a 0,004–0,009 no CPN | média |
| XC15, Mach 3 | cartão ausente | pelo M437 | sem conferência (CPN do 5"/38 ilegível) | baixa |
| XC15, Mach 2,5 | cartão ausente | pelo M437 | **o 5"/38 erra 0,17**: há outra célula mal lida nesse Mach | incerta |

Com isso o XC não tem mais NaN e o programa produz as 24 colunas do M437 a partir da geometria. **Mas o CPN do M437 deixou de ser teste em quase todos os Mach**, porque foi usado para decidir o XC: só Mach 0,01, 0,9, 0,95, 1,0 e 1,1 continuam independentes (`test_modelo_completo.py`, conjunto CIRCULARES).

*(Atualizado na seção T13: a terceira tabela, XM380E5, resolveu Mach 2,5 — o erro era do XC1 — e Mach 1,0, 1,35 e 1,5.)*

**Para validar de verdade o bloco de boattail do CPN**, falta uma terceira tabela com boattail. A do 155 mm M101 (p. 59) foi tentada: é a mais carregada de tinta de todas, e a identidade CMα = (VCG − CPN)·CNα só fecha linha a linha com um VCG que oscila entre 2,956 e 2,965. Ela pede leitura célula a célula; fica como próximo passo, junto com o 105 mm XM380E5 (p. 50).

## T12 — A p. 86: CNPA3, CNPA5, DELT, DISP e a regra de instabilidade

Linhas das fórmulas lidas em zoom e acrescentadas a `original/listing_p84-86.f`. Com elas, o programa produz **todas as colunas que o original imprime**.

**CNPA3 e CNPA5 (cartões C278-C281) — um defeito do original.**

    XMAG1 = CNPAA5 − CNPA              (momento de Magnus a 5° menos o a 1°)
    XMAG2 = CNPAA5 − CNPA + 0.3
    CNPA5 = (XMAG2 − 9.0·XMAG1)/0.0072
    CNPA3 = (XMAG1 − CNPA5·.0001)/0.01

As constantes são as de um polinômio f(δ) = C1 + C3·δ² + C5·δ⁴ avaliado em δ = 0,1 e 0,3. Mas o XMAG2 não usa o valor a 2°: o CNPAA2 é calculado (cartões C224-C227) e nunca usado. O XMAG2 é o XMAG1 mais uma constante. Consequência: as duas colunas impressas carregam **um único grau de liberdade** e obedecem a **CNPA3 + 0,1·CNPA5 = 3,75** para qualquer projétil. As 17 linhas do M437 confirmam a identidade — por exemplo 4,481 − 0,7311 = 3,7499 e 16,113 − 12,3633 = 3,7497 —, e o modelo reproduz as duas colunas nas 16 linhas legíveis. O "•" da segunda linha, ambíguo no scan, é um "+": a leitura como "·" erra por 7 % a 400 %. Vem daqui também o fator de 1,34 que a hipótese de um polinômio em sen α passando por 1°, 2° e 5° deixava sem explicação: o código não usa esses ângulos.

**DELT (C266)** = 6,28/(20·W1): o período de nutação dividido por 20. Fecha nos 17 Mach do M437. A nota antiga "não bate em Mach 0,01" (item A2) era leitura: o impresso é 0,7049, não 0,7649 (par 6/0).

**DISP (C256)** = (CNα − CX)·Iy·(W1 − W2)·3,635/(CMα·peso·diâmetro·V), com Iy em lb·in². Fecha em ±1 no último dígito nas 16 linhas legíveis do M437. A grandeza física continua sem explicação: depende da referência 71 (Whyte 1970), que não temos. Reproduz-se a fórmula como está no código.

**Taxas de amortecimento (C258-C261).** O código usa −CNAT·(1 − τ) com τ = 1/σ na raiz 1, o que confirma no próprio código o sinal que as tabelas indicavam (item E1).

**Regra de instabilidade (C249, C287).** Se s_g < 1,001, o programa pula a análise dinâmica e imprime só MACH e STAB. O modelo segue a regra: as demais colunas de estabilidade saem vazias nesse caso.

## T13 — Terceira tabela com boattail: 105 mm XM380E5 (p. 50)

**Leitura.** A p. 50 é das mais nítidas do relatório. As 15 colunas foram transcritas por inteiro (`python/tabelas/p50_105mm_xm380e5.csv`), sem usar o modelo para decidir dígitos. Nove células foram resolvidas por identidades entre colunas **impressas** — CMα = (VCG − CPN)·CNα, CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5) e CNPA3 + 0,1·CNPA5P = 3,75 — e ficam fora das contagens. Sete ficaram ilegíveis. O cabeçalho confirma VN = 2,900: a leitura antiga (2,400) vinha do scan de baixa resolução.

**Nenhum DATA foi decidido por esta tabela**: ela é teste em todas as células. Com o programa inteiro, partindo só da entrada impressa, 222 células independentes: **92 % indistinguíveis do original, 98 % no critério.** Magnus, Cmq e Clp fecham em todas as células legíveis.

**O que ela resolveu.** Onde havia duas tabelas para duas incógnitas, agora há três: sobra um grau de liberdade para achar qual célula está errada.

| Célula | Lido | Decidido | Decidido por | Conferência independente |
|---|---|---|---|---|
| XC1, Mach 2,5 | 1,90 | **1,99** | M437 (1,9899), com XC15 constante de 2,5 a 5 | XM380E5: −0,080 → +0,0001 no CPN; 5"/38: −0,168 → −0,008 |
| XC15, Mach 2,5 a 5 | cartão ausente | **−0,9184** (constante) | M437 em Mach 3, 4, 5 (−0,9152 / −0,9211 / −0,9190) | XM380E5 ≤ 0,0005 nos quatro Mach (peso pequeno no XC15) |
| XC12, Mach 1,35 | −,8054 | **−,8154** | M437 + 5"/38 (−0,8157) | XM380E5: 0,0000 |
| XC12, Mach 1,5 | −,6033 | **−,6173** | M437 + 5"/38 (−0,6192) | XM380E5: −0,0009 |
| XC15, Mach 1,35 / 1,5 | cartão ausente | 2,0052 / 0,9839 | M437 + 5"/38, com o XC12 corrigido | XM380E5 pede 2,0107 em 1,35 (as três concordam) |
| XC14, Mach 1,0 | −,7672 | **−,7872** | M437 (−0,7867); par 6/8 | nenhuma: 5"/38 e XM380E5 têm CXLL ≈ −0,06 |
| XF7, Mach 1,1 a 2,5 | cartão ausente | −0,715 e −0,73 | 5"/38 | M437 e XM380E5: −0,7151 / −0,7150 em Mach 1,1 |
| XD2, Mach 2,5 | ,6? | **,5** | 5"/38 (0,509) | XM380E5, mesmo peso: 0,500 |

**XC1 em Mach 2,5.** O "0,17 cal de erro no 5"/38" (T11) não era do XC15, e sim do XC1. O glifo do listing é ambíguo entre 0 e 9. A decisão seguiu a ordem que evita circularidade. Primeiro, o XC15 de 2,5 a 5 é constante, como os quatro últimos valores das linhas XC12, XC13, XC14 e XC16 no listing, e o M437 o fixa em Mach 3, 4 e 5. Depois, o M437 em Mach 2,5 fixa o XC1. O XM380E5, que tem peso alto no XC1 e não entrou em nenhuma das duas decisões, passa a fechar em Mach 2,5. A linha do XC1 fica 1,79 1,88 1,99 2,03 2,00 1,97.

**Mais um cartão ausente: o XF7.** Na p. 81, depois do primeiro cartão do DATA XF7 (7 valores), vêm **duas cópias do terceiro cartão** ("−.73, −.73, −.73 /"). O segundo cartão (Mach 1,1 a 2,5) não foi impresso. É o mesmo defeito do XC15 e do XE5, o terceiro caso no listing. O −0,73 usado até agora nesses Mach era suposição. A coluna CMQ do 5"/38 pede −0,7146 em Mach 1,1 e −0,729 a −0,731 de 1,2 a 2,5. O M437 e o XM380E5, fora da decisão, pedem −0,7151 e −0,7150. **Era esse o "DATA XF mal lido em Mach 1,1"**, que deixava o Cmq do M437 0,038 fora. Na tabela do 155 mm M101, a célula de Mach 1,1 lida como −14,861 é provavelmente −14,661 (par 6/8): o modelo dá −14,662.

**Continua em aberto.**
- Mach 0,6: o CPN calculado fica acima do impresso nas três tabelas com boattail (M437 +0,004; XM380E5 +0,002; 5"/38 −0,001). Vários pares de coeficientes fecham as três ao mesmo tempo, e nenhum é uma troca limpa de glifo. Em Mach 0,8, o mesmo acontece só no M437 (+0,002).
- 5"/38 de Mach 2,5 a 5: o CPN fica 0,006 a 0,009 abaixo, e o CNα impresso 0,014 abaixo do reconstruído. O desvio é sistemático e aparece só nessa geometria, com as duas outras fechando: o mais provável é um coeficiente de XB/XC com peso alto só no 5"/38, ou a própria transcrição dessas linhas.
- 5"/38 em Mach 1,75: pede XC15 = 0,629, contra 0,550 do M437.
- CX2 do M437 em Mach 1,5, 1,75 e 2,5 (−0,007 a −0,030): o 5"/38 e o XM380E5 fecham, o que aponta para a transcrição dessas células do M437 ou para um termo que só pesa com boattail de 1 cal.
