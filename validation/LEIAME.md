# Todos os casos do relatório

`python validation/comparacao_erros.py` roda o programa reconstruído com a **entrada impressa de cada tabela de 1973** e compara cada saída legível com a impressa. São 13 casos: todas as tabelas de saída do relatório (pp. 29 a 68). As pp. 44 e 47 do scan trazem a mesma impressão, então contam como um caso só.

Saídas:

| Arquivo | Conteúdo |
|---|---|
| `casos/pNN_*.csv` | um caso por arquivo, célula a célula: impresso, calculado, erro e situação |
| `resumo_por_caso.csv` | uma linha por caso |
| `resumo_erros.csv` | uma linha por coluna, com todos os casos juntos |
| `erros_por_celula.csv` | todas as células |

As transcrições estão em `python/tabelas/` (uma por página, com o cabeçalho) e as leituras brutas, com os glifos ambíguos marcados, em `python/tabelas/leituras/`.

## Como cada célula é classificada

O erro é medido em **unidades da última casa impressa**: numa coluna de 3 casas, 1 unidade = 0,001. Como o programa original arredondava nessa casa, até ±0,5 unidade o resultado é indistinguível dele. O critério do projeto é ±1,5 unidade.

- **independente**: entra na estatística.
- **circular**: algum `DATA` ou alguma entrada do cabeçalho foi decidido usando esta célula (`python/circularidade.py`). Mostra só que a decisão é coerente.
- **identidade**: a célula era ambígua no scan e foi desambiguada só por identidades entre colunas impressas, como CMα = (VCG − CPN)·CNα e CNPA = CYPA·(VCG − CPF1). Nenhum `DATA` entra nessa conta, mas a célula fica fora da estatística.

**Entradas ilegíveis.** Quando um dígito do cabeçalho não se lê, a entrada é decidida por uma única coluna, declarada no CSV e dentro da faixa que o glifo permite. Essa coluna fica circular naquele caso. Se ela é de Magnus, as outras seis também ficam, porque são funções umas das outras. É por isso que casos como o 20 mm cone-cilindro têm poucas células independentes.

## Resultado (23/09/2026)

2718 células legíveis: 1612 independentes, 779 circulares, 327 desambiguadas por identidade.

**Independentes: 88 % indistinguíveis do original, 95 % no critério, erro mediano de 0,26 unidade.** Sem o M1, cuja geometria do cabeçalho não fecha (abaixo): 90 % e 96 %.

| p. | Caso | Legíveis | Independentes | ≤ 0,5 un. | ≤ 1,5 un. | Mediana | Observação |
|---|---|---|---|---|---|---|---|
| 29 | 20 mm M56A3 | 209 | 171 | 94 % | 99 % | 0,20 | meplat relido: 0,260 (a leitura antiga, 0,200, deixava o CX fora) |
| 32 | 20 mm 5 cal ANSR | 227 | 189 | 85 % | 99 % | 0,25 | |
| 35 | 20 mm 7 cal ANSR | 224 | 153 | 94 % | 99 % | 0,22 | |
| 38 | 20 mm 9 cal ANSR | 234 | 177 | 94 % | 99 % | 0,25 | cabeçalho inteiro legível |
| 41 | 20 mm 10 cal cone-cilindro | 143 | 22 | 91 % | 100 % | 0,18 | VCG 6,747, decidido pelas identidades de Magnus (cabeçalho ?.747) |
| 44/47 | M1 | 159 | 60 | 50 % | 50 % | 1,61 | Magnus, Cmq e Clp fecham; CX, CX2, CNα, CPN e CMα não |
| 50 | 105 mm XM380E5 | 231 | 217 | 93 % | 98 % | 0,33 | quase nada circular: o teste mais limpo |
| 53 | 5"/38 NAVY | 226 | 180 | 88 % | 91 % | 0,33 | CNα 0,014 abaixo de Mach 1,75 a 5 |
| 56 | 5"/54 NAVY | 94 | 22 | 91 % | 96 % | 0,24 | página muito degradada |
| 59 | 155 mm M101/107 | 153 | 32 | 78 % | 81 % | 0,32 | CPN e CMα fora de 0,007 a 0,018 |
| 62 | 155 mm M549 | 174 | 29 | 83 % | 93 % | 0,32 | ogiva relida: 2,99 (e não 2,90); raio da ogiva 18,9 |
| 65 | 175 mm M437 | 473 | 317 | 89 % | 95 % | 0,27 | o único com estabilidade |
| 68 | 175 mm SRC | 171 | 43 | 77 % | 95 % | 0,39 | ogiva de 5,5 cal: **primeiro teste de XA13–XA15 e XC17** |

Por coluna, com todos os casos juntos (sem o M1):

| Coluna | Casos | Células | ≤ 0,5 un. | ≤ 1,5 un. | Mediana | Comentário |
|---|---|---|---|---|---|---|
| CX | 8 | 119 | 87 % | 100 % | 0,26 | |
| CYPA, CNPA, CPF1, CPF5, CNPA5, CNPA3, CNPA5P | 7 | 714 | 97–100 % | 99–100 % | 0,2–0,33 | Magnus |
| CMQ | 4 | 50 | 100 % | 100 % | 0,21 | |
| CLP | 12 | 200 | 100 % | 100 % | 0,24 | |
| CNA | 9 | 86 | 72 % | 86 % | 0,32 | |
| CX2 | 11 | 95 | 68 % | 87 % | 0,36 | subtrai o CNα: herda o erro dele |
| CPN | 10 | 81 | 75 % | 90 % | 0,24 | |
| CMA | 10 | 87 | 48 % | 77 % | 0,56 | = (VCG − CPN)·CNα: soma os erros do CNα e do CPN, ampliados pelo braço |
| Estabilidade (GYRO … DISP) | 1 | 4–17 cada | 25–100 % | 75–100 % | 0,06–1,15 | só o M437 tem esse bloco |

**O M1 (pp. 44/47).** As duas páginas do scan são a mesma impressão: o título, o cabeçalho e um traço que atravessa a linha de Mach 1,75 são idênticos. Uma das duas tabelas do relatório (90 mm M71 ou 105 mm M1) está ausente do scan. Com a geometria do cabeçalho, Magnus, Cmq e Clp fecham, o que confirma VL, VN, VB e VCG. CX, CX2, CNα, CPN e CMα não fecham: o CX fica 0,005 acima em todo Mach e o CX2 chega a 0,23 de diferença. Nenhuma mudança isolada de OR, DM, BD, VN ou VB fecha as cinco colunas. O caso fica registrado, mas fora da conclusão.

## Duas perguntas diferentes

Este resultado responde **"a reconstrução reproduz o SPIN-73 de 1973?"**. Nos blocos lidos diretamente do código e dos DATA, sim, no nível do arredondamento da impressão, em doze dos treze casos. O ponto mais fraco é o CMα, que acumula os erros do CNα e do centro de pressão.

A outra pergunta — **"o SPIN-73 acerta a realidade?"** — está em `python/experimental/`. Contra voo livre da família 7,62 NATO, o modelo de 1973 superestima o Magnus (+0,3 a +0,5 em p·d/2V) e o amortecimento Cmq (2,5 vezes em Mach 1,2, 10 % em Mach 2 a 2,5) e erra o CNα do projétil mais curto (+0,28). Contra o Ball M2 do Hitchcock (calibre 0.30, Mach 2,5), o Cmq erra 3 %. Esses erros são do modelo original, não da reconstrução.
