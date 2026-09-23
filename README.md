# SPIN-73 reconstruído

Reconstrução, em Python, do programa **SPIN-73** (R. H. Whyte, *SPIN-73, an Updated Version of the SPINNER Computer Program*, Picatinny Arsenal TR 4588, 1973; DTIC AD0915628, Distribution A — aprovado para divulgação pública).

O SPIN-73 estima os coeficientes aerodinâmicos de um projétil estabilizado por rotação só a partir da geometria, em 17 números de Mach (0,01 a 5), e faz a análise de estabilidade. O código original só existe como listing Fortran impresso num relatório escaneado. Aqui ele foi reconstruído lendo o scan — as equações, os blocos `DATA` com as constantes empíricas e o próprio código — e conferido contra as 13 tabelas de saída que o programa imprimiu em 1973.

**Resultado:** nas células que não participaram de nenhuma decisão de leitura, 89 % ficam indistinguíveis do original e 95 % dentro de ±1,5 unidade da última casa impressa (91 % e 97 % sem o caso M1, cuja página aparece duplicada no scan e cuja geometria não fecha).

## Sumário

1. [Como usar](#1-como-usar)
2. [Entradas e saídas](#2-entradas-e-saídas)
3. [O conceito da reprodução canônica](#3-o-conceito-da-reprodução-canônica)
4. [Verificações e resultados](#4-verificações-e-resultados)
5. [Documentos base e de onde lemos](#5-documentos-base-e-de-onde-lemos)
6. [O que não conseguimos ler](#6-o-que-não-conseguimos-ler)
7. [O que a reconstrução revelou](#7-o-que-a-reconstrução-revelou)
8. [O que fizemos de diferente](#8-o-que-fizemos-de-diferente)
9. [Adições opcionais](#9-adições-opcionais)
10. [O SPIN-73 contra medições de voo livre](#10-o-spin-73-contra-medições-de-voo-livre)
11. [Estrutura do repositório](#11-estrutura-do-repositório)
12. [Limitações](#12-limitações)
13. [Licença e fonte](#13-licença-e-fonte)

---

## 1. Como usar

### Instalação

Na raiz do repositório (Python 3.10 ou mais novo; a única dependência é o numpy):

```bash
pip install -e .
```

Sem instalar, dá para rodar de dentro de `python/` com `python -m spin73`.

### Linha de comando

O caso de validação do relatório (175 mm M437):

```bash
spin73 --exemplo
```

Um projétil seu, com o cartão do SPIN-73 (comprimentos em calibres, diâmetro em polegadas, inércias em lb·in², peso em lb, passo em calibres por volta):

```bash
spin73 --VL 5.0 --VN 2.0 --VB 0.4 --VCG 3.0 --OR 8 --DIA 1.0 --IX 0.5 --IY 4.0 --WGT 0.5 --TWIST 25 --csv saida.csv
```

O mesmo em unidades métricas, estimando o CG e as inércias que faltam (adição opcional):

```bash
spin73 --VL 4.05 --VN 1.90 --VB 0.40 --OR 7.9 --d-mm 5.69 --massa-g 4.05 --passo-pol 7 --estimar-massa
```

Ou num arquivo `CHAVE = valor` (modelos em [python/exemplos/](python/exemplos/)):

```bash
spin73 --entrada python/exemplos/m855_metrico.txt
```

A primeira linha da saída diz o modo: `Modo: canônico (SPIN-73 de 1973)` ou a lista das adições usadas. `spin73 --help` mostra todas as opções.

### Como biblioteca (por exemplo, num 6DOF)

```python
import spin73

p = spin73.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
aero = spin73.Aerodinamica(p, convencao="moderna")   # canônico, na convenção moderna
c = aero(mach)             # c.CD0, c.CDd2, c.CNa, c.Cma, c.Cmq_Cmad, c.Clp, c.Cmpa ... (escalar ou array)
```

A aerodinâmica é calculada uma vez, na construção; cada chamada só interpola em Mach. Guia completo, com as adições opcionais e como escrever uma correção nova: [docs/BIBLIOTECA.md](docs/BIBLIOTECA.md).

## 2. Entradas e saídas

### O cartão de entrada (Apêndice B do relatório)

Só as quatro primeiras são obrigatórias. Com elas sai a tabela aerodinâmica inteira; com as cinco de massa e raia, sai também a análise de estabilidade.

| Entrada | O que é | Unidade | Precisa? | Se omitir | O que ela muda |
|---|---|---|---|---|---|
| `VL` | comprimento total | calibres | **sim** | — | tudo |
| `VN` | comprimento da ogiva | calibres | **sim** | — | tudo |
| `VB` | comprimento do boattail (0 = base reta) | calibres | **sim** | — | tudo |
| `VCG` | CG a partir do **nariz** | calibres | **sim**¹ | — | CMα, momento de Magnus, Cmq |
| `OR` | raio da ogiva (1000 = nariz cônico) | calibres | recomendada | 2·VN² | CX, CNα, CPN, CMα |
| `DM` | diâmetro do meplat (ponta chata) | calibres | recomendada | 0,12 | CX, CNα, CPN, CMα |
| `BD` | diâmetro da cinta | calibres | opcional | 1,02 | CX |
| `BOOM` | "boom length" do cartão original | calibres | raramente | 0 | CX |
| `DIA` | diâmetro | polegadas | para estabilidade | 0 (sem estabilidade) | estabilidade |
| `IX`, `IY` | inércias axial e transversal | lb·in² | para estabilidade | — | estabilidade |
| `WGT` | peso | lb | para estabilidade | — | estabilidade |
| `TWIST` | passo de raia | calibres por volta | para estabilidade | — | estabilidade |
| `TEMP` | temperatura do ar | °F | opcional | 59 | só a estabilidade |
| `DGUN` | diâmetro do tubo | polegadas | opcional | = DIA | rotação, na estabilidade |

¹ Pode ser estimado pela geometria com a adição opcional de massa (seção 9).

Cada entrada tem uma forma em unidades métricas (`D_MM`, `MASSA_G`, `IX_GCM2`, `PASSO_MM` ou `PASSO_POL`, `TEMP_C`, `CG_BASE`...), no arquivo, na linha de comando e no Python. O Mach não é entrada: o programa sempre calcula os 17 Mach do relatório.

### O que sai

| Bloco | Colunas |
|---|---|
| Aerodinâmica (sempre) | `CX` arrasto a guinada zero · `CX2` termo de guinada · `CNA` força normal · `CMA` momento de arfagem em torno do CG · `CPN` centro de pressão (calibres do nariz) · `CYPA` força de Magnus · `CNPA`, `CNPA5` momento de Magnus a 1° e 5° · `CPF1`, `CPF5` centro do Magnus · `CNPA3`, `CNPA5P` polinômio de Magnus · `CMQ` amortecimento em arfagem · `CLP` amortecimento de rolamento |
| Estabilidade (com massa e raia) | `GYRO` (s_g) · `SBAR`, `SBAR5` (s_d) · `RECIP`, `RECIP5` · `SPIN` · `W1`, `W2` (frequências) · `L1`, `L2`, `L15`, `L25` (amortecimentos) · `DELT` · `DISP` |

**Convenção do relatório** (pp. 7–8), estilo NACA/BRL clássico: taxas adimensionais em **pd/2V e qd/2V**, derivadas por sen ᾱ, posições em calibres a partir do nariz, momentos em torno do CG. Fontes modernas (McCoy, PRODAS, CFD) usam pd/V e qd/V, e o valor delas é a **metade** do SPIN-73 para Cmq, Clp e Magnus. O arrasto de guinada é CX2 + CNα, não o CX2. `convencao="moderna"` faz as conversões (`python/spin73/convencoes.py`).

## 3. O conceito da reprodução canônica

A meta é reproduzir **o que o programa de 1973 imprimia**, erros e defeitos incluídos, e não melhorá-lo. Tudo o que muda resultados fica fora do núcleo, como adição opcional.

- **Três fontes dentro do relatório.** O texto dá as equações; o listing dá os blocos `DATA` com as constantes empíricas; o código mostra o que o programa fazia de fato. **Onde o texto e o código divergem, vale o código** — foi ele que gerou as tabelas.
- **Cada valor lido tem uma classe.** *Verificado*: leitura clara, ou confirmada por uma identidade independente. *Decidido pelo modelo*: escolhido porque reproduz as tabelas. *Pendente*: em aberto. A classe e a evidência de cada célula estão nos módulos `python/spin73/dados/x?_lidos.py`.
- **A impressão matricial confunde dígitos** (6/8, 1/3, 2/7, 4/9, 0/6, 5/9). Toda leitura ambígua foi decidida por uma identidade que não dependia dela. Nas tabelas de saída, as identidades são entre colunas **impressas**: CMα = (VCG − CPN)·CNα, CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5) e CNPA3 + 0,1·CNPA5P = 3,75.
- **Sem circularidade.** Um valor decidido usando uma tabela nunca é usado para validar essa mesma tabela. `python/circularidade.py` marca, célula a célula, o que ficou circular, e essas células saem da estatística.
- **Tolerância.** O erro é medido em unidades da última casa impressa. Até ±0,5 unidade, o resultado é indistinguível do original (ele arredondava nessa casa); o critério do projeto é ±1,5 unidade (±0,0015 nas colunas de 3 casas).

## 4. Verificações e resultados

### O caso de validação do relatório (175 mm M437, p. 65), partindo só da geometria

| Bloco | Colunas | Reproduz a tabela de 1973 |
|---|---|---|
| Força axial | CX | 17 de 17 Mach (e 17 de 17 no 5"/38) |
| Força axial de guinada | CX2 | 12 de 17 (2 células ilegíveis no scan; 3 com resíduo de 0,007 a 0,02) |
| Força normal | CNA | 15 de 17 |
| Magnus | CYPA, CNPA, CPF1, CPF5, CNPA5, CNPA3, CNPA5P | 16 ou 17 de 17 |
| Amortecimentos | CMQ, CLP | 17 de 17 |
| Centro de pressão | CPN, CMA | teste independente em só 4 Mach no M437 (ver abaixo) |
| Estabilidade | GYRO, SBAR, RECIP, SPIN, W1, W2, λ, DELT, DISP | 15 a 17 de 17; as que dependem do CMα só são independentes nos mesmos Mach |

O centro de pressão do M437 fecha em 14 de 17 Mach, mas em 13 deles o resultado é **circular**: o listing impresso perdeu um cartão de `DATA` (a continuação do XC15), e a tabela do M437 foi usada para recuperá-lo. A conferência independente vem de mais duas tabelas com boattail: o 5"/38 (p. 53) e o **105 mm XM380E5 (p. 50), transcrito por inteiro e sem ter decidido nenhum `DATA` do centro de pressão**: o programa reproduz 16 dos 17 Mach do CPN dele e 98 % de todas as suas células.

### Todos os casos do relatório

As 13 tabelas de saída (pp. 29 a 68) estão transcritas em `python/tabelas/`, e o programa roda com a entrada impressa de cada uma. São 2718 células legíveis: 1612 independentes, 779 circulares e 327 desambiguadas só por identidade.

| p. | Caso | Independentes | ≤ 0,5 un. | ≤ 1,5 un. | Observação |
|---|---|---|---|---|---|
| 29 | 20 mm M56A3 | 171 | 94 % | 99 % | meplat relido: 0,260 |
| 32 | 20 mm 5 cal ANSR | 189 | 85 % | 99 % | |
| 35 | 20 mm 7 cal ANSR | 153 | 94 % | 99 % | |
| 38 | 20 mm 9 cal ANSR | 177 | 94 % | 99 % | cabeçalho inteiro legível |
| 41 | 20 mm 10 cal cone-cilindro | 22 | 91 % | 100 % | VCG decidido pelas identidades de Magnus |
| 44/47 | M1 | 60 | 50 % | 50 % | página duplicada no scan (seção 6) |
| 50 | 105 mm XM380E5 | 217 | 93 % | 98 % | o teste mais limpo: quase nada circular |
| 53 | 5"/38 NAVY | 180 | 95 % | 98 % | fechou com o cartão C205 |
| 56 | 5"/54 NAVY | 22 | 91 % | 96 % | página muito degradada |
| 59 | 155 mm M101/107 | 32 | 78 % | 81 % | CPN e CMα fora de 0,007 a 0,018 |
| 62 | 155 mm M549 | 29 | 83 % | 93 % | ogiva relida: 2,99 |
| 65 | 175 mm M437 | 317 | 89 % | 95 % | o único com estabilidade |
| 68 | 175 mm SRC | 43 | 77 % | 95 % | ogiva de 5,5 cal: único teste de XA13–XA15 e XC17 |

Por coluna, sem o M1: Magnus, Cmq e Clp de 97 a 100 % dentro de ±0,5 unidade; CX 87 %; CNα 77 %; CPN 79 %; CMα 52 % (82 % no critério — ele acumula os erros do CNα e do CPN). Detalhe célula a célula em [validation/LEIAME.md](validation/LEIAME.md).

### Como rodar as verificações

A última linha confere as 12 transcrições de tabela sem usar o modelo, só pelas identidades entre colunas impressas; hoje, nenhuma violação.

```bash
python -m pytest -q python                  # 266 testes (e 3 pulados: colunas não transcritas)
python validation/comparacao_erros.py       # todos os casos, célula a célula
python python/tabelas/verificar_identidades.py 29 32 35 38 41 44 50 53 56 59 62 68
```

## 5. Documentos base e de onde lemos

### O relatório

Whyte, R. H. *SPIN-73, an Updated Version of the SPINNER Computer Program*. Technical Report 4588, Picatinny Arsenal, 1973 (DTIC AD0915628). O que foi lido de cada parte:

| Parte | Páginas | Onde está aqui |
|---|---|---|
| Nomenclatura e convenções | 7–8 | `python/spin73/convencoes.py` |
| Texto com as equações de cada coeficiente e da estabilidade | até a p. 18 | `python/spin73/nucleo.py` (divergências na seção 7) |
| Tabela 1: erro provável do SPIN-73 contra experimento | 28 | citada em `python/experimental/benchmarks/` |
| 13 tabelas de saída | 29–68 | `python/tabelas/` (leituras brutas em `leituras/`) |
| Apêndice B: o cartão de entrada | 76–77 | `spin73.Projetil` |
| `DIMENSION` e os blocos `DATA` XA … XG | 79–81 | `python/spin73/dados/` |
| O código | 84–86 transcritas literalmente | `original/listing_p84-86.f` |

**De onde a leitura veio.** Do scan em alta resolução da DTIC (96 páginas JP2 de cerca de 2600 × 3400 px; não versionado, ver [fontes/LEIAME.md](fontes/LEIAME.md)). Várias leituras antigas, feitas num scan de resolução menor, foram corrigidas nele (por exemplo, a ogiva do XM380E5: 2,400 → 2,900). As ferramentas estão em `ferramentas/`: `recorte.py` (recortes girados, com zoom e autocontraste), `pagina_pdf.py` (páginas CCITT de PDFs escaneados) e `pdf_paginas.py` com `jbig2.py` (PDFs "MRC" da DTIC, em que o texto fica numa máscara JBIG2; o decodificador é Python puro).

### Documentos de apoio (todos com liberação pública)

| Documento | Para quê |
|---|---|
| Hitchcock, *Aerodynamic Data for Spinning Projectiles*, BRL Report 620 (AD-800 469) | dados do calibre .30 e as fórmulas empíricas de inércia usadas na estimativa de massa |
| Piddington, BRL MR 1833, 1967 (AD815788) | família 7,62 NATO: primeira comparação com voo livre |
| Karpov 1955 e 1964; Brandon 1969; McCoy 1980, 1982, 1985, 1988 e 1990; Whyte 1991 | medições de voo livre (seção 10); lista completa, com os números DTIC, em [fontes/LEIAME.md](fontes/LEIAME.md) |

## 6. O que não conseguimos ler

| O quê | Por quê | O que foi feito |
|---|---|---|
| **Três cartões `DATA`**: a continuação do XC15 (centro de pressão, Mach 1,2 a 5), o primeiro cartão do XE5 (Magnus de corpo longo) e o segundo do XF7 (Cmq, Mach 1,1 a 2,5) | não foram impressos: em cada caso, a impressão repete um cartão vizinho no lugar | recuperados pelas tabelas de saída, marcados *decididos pelo modelo* e fora da validação |
| Células desbotadas ou ambíguas dos `DATA` | a linha do XC12, por exemplo, está desbotada | decididas pelas tabelas, com a evidência registrada: 4 no XA, 7 no XB, 7 no XC, 4 no XD |
| **Uma tabela de saída inteira** | as pp. 44 e 47 do scan são a mesma impressão (mesmo título, cabeçalho e artefatos): falta a tabela de uma delas (90 mm M71 ou 105 mm M1) | o caso "M1" fica registrado, fora da conclusão |
| Dígitos de cabeçalho | ilegíveis ou ambíguos em 10 dos 13 casos (a entrada decidida de cada um está em `validation/resumo_por_caso.csv`) | cada um decidido por uma coluna, que fica circular naquele caso |
| Páginas muito degradadas | 5"/54 (p. 56), M101 (p. 59), 20 mm 5 cal (p. 32) | poucas células independentes nelas |
| Código da p. 83 | ainda não transcrito; tem o ramo do boattail maior que 0,65 cal | segue o texto do relatório; a saída avisa quando esse ramo é usado |
| Referência 71 (Whyte 1970) | não disponível | a coluna `DISP` é reproduzida pela fórmula do código, sem interpretação física |
| `XB10` | declarado no `DIMENSION`, não encontrado no código transcrito | sem uso |

**Resíduos em aberto:** CPN em Mach 0,6 (0,002 a 0,004 cal), CPN do M101 em Mach 1,2 (0,007 cal), centro do Magnus do 175 mm SRC (+0,005) e CX2 do M437 em Mach 1,5, 1,75 e 2,5. Todas as leituras, com a evidência de cada uma, estão em [docs/NOTAS_TRANSCRICAO.md](docs/NOTAS_TRANSCRICAO.md).

## 7. O que a reconstrução revelou

Divergências entre o texto e o código, e termos que o texto não documenta:

- **Sinal trocado no texto** nas taxas de amortecimento λ (p. 18): o texto imprime −CNα(1 ± 1/σ); o código e as tabelas usam −CNα(1 ∓ 1/σ).
- **Constante do fator giroscópico**: o código usa 1352,4 onde a física com g = 32,174 dá 1349,8 (+0,19 %).
- **Termos de corpo longo** não documentados, ativos acima de 6 calibres: XE5 no Magnus e XF9 no amortecimento.
- **A13, A14 e A15** no arrasto: o termo de ogiva longa tem três trechos (quebras em 3,48 e 3,97 calibres); o texto só descreve o primeiro.
- **Descarte do boattail** no centro de pressão quando o momento do boattail sai positivo, e da força normal do boattail quando ela sai positiva (cartão C205, que só age com ogiva curta no supersônico).
- **CNPA3 e CNPA5**: os "coeficientes do polinômio de Magnus" não usam o valor calculado a 2°; o programa soma uma constante fixa, e as duas colunas obedecem a CNPA3 + 0,1·CNPA5 = 3,75 para qualquer projétil. Defeito do original, reproduzido.
- **O expoente supersônico do boattail** já vale em Mach 0,95 (o texto não diz o limiar; o código diz).

## 8. O que fizemos de diferente

O núcleo reproduz o comportamento do programa de 1973, inclusive os defeitos. As diferenças são de interface e estão documentadas:

- **Campos em branco no cartão.** No original, DM vazio vale 0, BD vazio vale 1,00 e TEMP vazio vale 0 °F. Aqui a omissão dá DM = 0,12 e BD = 1,02 (os valores de "dimensões automáticas" do próprio programa) e TEMP = 59 °F. Para reproduzir um cartão em branco, passe zero.
- **Nomes de coluna.** O programa imprime "CNPA5" para o coeficiente quíntico e "CNPA-5" para a inclinação secante a 5°; aqui são `CNPA5P` e `CNPA5`.
- **O CG pode faltar** no cartão: sem ele o programa pede o CG, ou a estimativa opcional de massa.
- **Saída** em tabela de texto, CSV ou objeto Python, em vez da impressora de linha; a regra do original de pular a análise dinâmica quando s_g < 1,001 é seguida.
- **Tudo o que muda resultados é opcional** e fica fora do núcleo (seção 9).

## 9. Adições opcionais

Nenhuma é aplicada sem ser pedida, e nenhuma altera o canônico.

| Adição | O que faz | Muda | Como pedir |
|---|---|---|---|
| Convenção moderna | pd/V, qd/V, CLα, CDδ² | só a apresentação (conversão exata) | `convencao="moderna"` |
| Unidades métricas | mm, g, g·cm², °C, CG a partir da base | só a entrada (conversão exata) | `spin73.unidades`, `--d-mm`, `--massa-g`... |
| Estimativa de massa | CG, massa e inércias que faltam no cartão, por sólido de revolução homogêneo ou pelas fórmulas de Hitchcock (BRL 620) | entradas que faltavam | `spin73.massa`, `--estimar-massa` |
| Correção de voo livre | arrasto ajustado ao tamanho do projétil (número de Reynolds), mais duas peças no limite da validação | coeficientes | `correcoes="voo_livre"` ou `"voo_livre:CX0"`, `--correcao` |
| Correções suas | qualquer objeto com `aplicar(tabela, projetil, contexto)` | coeficientes | [docs/BIBLIOTECA.md](docs/BIBLIOTECA.md) |

**Estimativa de massa, validada contra 20 projéteis com valores medidos** (a massa medida dada): em balas, o CG fica a ±0,12 calibre e a inércia axial de −5 % a +3 %. Em granadas, as fórmulas de Hitchcock ficam de −11 % a +3 %; o sólido homogêneo subestima em 20 a 27 %, porque a massa da granada fica na parede. Detalhes em [python/experimental/massa/LEIAME.md](python/experimental/massa/LEIAME.md).

## 10. O SPIN-73 contra medições de voo livre

A seção 4 responde se a reconstrução reproduz o SPIN-73. Esta responde **se o SPIN-73 acerta a realidade**. "Voo livre" é o ensaio em que o projétil é disparado de verdade numa pista instrumentada, e os coeficientes saem do movimento medido. Aqui não se atira nada: as medições são dos relatórios publicados, transcritas rodada a rodada.

- **Benchmarks** ([python/experimental/benchmarks/](python/experimental/benchmarks/LEIAME.md)): 155 mm M101 e M483A1, .50 M33, 5,56 NATO, 7,62 match, 30 mm XM788/XM788E1/XM789, 175 mm T203 (modelo de 90 mm) e 152 mm XM617 (cone-cilindro). No supersônico, o SPIN-73 acerta CMα, CNα e CX0 a poucos por cento nos projéteis de artilharia e no cone-cilindro, mas subestima o CMα das balas de boattail longo (.50: 21 %; 7,62 match: 9 a 14 %). No subsônico, o CX0 erra de −33 % a +25 % conforme a forma e o tamanho.
- **Correção empírica** ([python/experimental/correcao/](python/experimental/correcao/LEIAME.md)): dez grupos de projéteis e 1391 valores medidos. Uma correção só entra se reduzir o erro em projéteis que o ajuste não viu (validação cruzada deixando um grupo de fora). O arrasto é a peça firme: o erro supersônico cai de 6,6 % para 4,8 % e o subsônico de 19,3 % para 15,1 %, melhorando 7 de 9 ou 10 grupos. O CMα e o Magnus não melhoram com nenhuma forma simples e ficam como no SPIN-73.
- **Recalibração com a 7,62 NATO** (BRL MR 1833) e o compêndio de Hitchcock: [python/experimental/README.md](python/experimental/README.md).

Nada disso altera o programa reconstruído.

## 11. Estrutura do repositório

| Diretório | Conteúdo |
|---|---|
| `python/spin73/` | **A biblioteca** (tabela de módulos abaixo) |
| `python/tabelas/` | As 13 tabelas de saída de 1973, com a entrada impressa; leituras brutas com os glifos ambíguos em `leituras/` |
| `python/reconstrucao_*/` | A reconstrução de cada bloco `DATA`, com os testes e a análise que decidiram cada leitura |
| `python/exemplos/` | Arquivos de entrada de exemplo |
| `python/experimental/` | Comparações com medições: `benchmarks/`, `correcao/`, `massa/`, `hitchcock/` e a recalibração com a 7,62 NATO — **separado** da reconstrução |
| `validation/` | Todos os casos do relatório rodados e comparados, célula a célula |
| `original/` | Transcrição literal do listing Fortran (pp. 84–86) |
| `docs/` | Notas de transcrição (cada leitura, com a evidência) e o guia da biblioteca |
| `ferramentas/` | Leitura dos scans: recortes, páginas de PDF, decodificador JBIG2 |
| `fontes/` | Os PDFs e o scan (não versionados; ver `fontes/LEIAME.md`) |

| Módulo | Conteúdo | |
|---|---|---|
| `spin73.nucleo` | equações, `tabela()`, `estabilidade()`, o cartão `Projetil` | canônico |
| `spin73.dados` | blocos `DATA` XA…XG, com a proveniência de cada valor | canônico |
| `spin73.aero` | `Aerodinamica`: coeficientes em qualquer Mach, para simuladores | canônico sem opções |
| `spin73.convencoes` | convenção do relatório ↔ moderna | adição |
| `spin73.unidades` | entradas em unidades métricas | adição |
| `spin73.massa` | estimativa de CG, massa e inércias | adição |
| `spin73.correcoes` | correções da saída e a interface para escrever novas | adição |
| `spin73.cli` | linha de comando | — |

## 12. Limitações

A saída traz avisos específicos para cada geometria (`spin73.avisos(p)`). Os principais:

- **Centro de pressão de Mach 1,2 a 5**: depende do cartão do XC15, recuperado pelas tabelas. Três tabelas com boattail conferem (M437, 5"/38 e XM380E5, com até 0,0025 calibre de resíduo); o M101 ainda fica 0,007 calibre fora em Mach 1,2. As colunas de estabilidade herdam essas incertezas, porque dependem do CMα.
- **Boattail maior que 1 calibre**: ramo do código lido, mas sem nenhuma tabela de 1973 que o valide. O ramo de ogiva maior que 3 calibres tem uma só tabela (175 mm SRC).
- **Formas fora do modelo**: o SPIN-73 descreve ogiva (ou cone) com meplat, cilindro e boattail cônico ou base reta. Nariz arredondado, base com degrau ou base arredondada não têm representação; a base arredondada entra como tronco de cone.
- **Contra a realidade**, o erro é o do modelo de 1973: a Tabela 1 do relatório dá erro provável de 0,12 a 0,17 no CMα contra experimento (seção 10).

## 13. Licença e fonte

Código sob a licença MIT (ver [LICENSE](LICENSE)). O relatório original é de domínio público (Distribution A).

Whyte, R. H. *SPIN-73, an Updated Version of the SPINNER Computer Program*. Technical Report 4588, Picatinny Arsenal, Dover, NJ, novembro de 1973. DTIC AD0915628. Distribution A: approved for public release.
