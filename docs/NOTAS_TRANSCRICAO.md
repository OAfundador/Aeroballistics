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

**A1.** O fator giroscópico sg calculado fica sistematicamente ~0,17 % abaixo do impresso. É um viés constante em todas as linhas, não ruído. O ρ implícito é ≈ 0.002372 slug/ft³, contra 0.002376 da fórmula do listing (linha 92). Hipóteses: outra constante de conversão (g, 144), outro valor de ρ usado no cálculo de sg, ou algum dígito de Ix. As frequências W1/W2 herdam o resíduo via σ. Os testes usam tolerância de 0,3 %.

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
