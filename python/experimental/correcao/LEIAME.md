# Correção empírica do SPIN-73 com voo livre

O SPIN-73 reconstruído reproduz o programa de 1973, erros incluídos. Aqui ele é corrigido com medições de túnel balístico, **sem alterar o programa**: a correção parte da tabela do SPIN-73 e ajusta o que os dados mostram que dá para ajustar.

```
python experimental/correcao/ajuste.py      # valida, ajusta e grava correcao_ajustada.json
```

```python
import aplicar                                       # experimental/correcao/aplicar.py
t = aplicar.tabela_corrigida(p, d_mm=5.69)           # p: spin73.Projetil; d_mm: diâmetro real
```

## Dados

`dados.py` junta seis grupos de projéteis, com 810 valores medidos, todos convertidos para a convenção do SPIN-73 (pd/2V, qd/2V, CNα e não CLα, CPN a partir do nariz, CX0 a guinada zero):

| Grupo | Projéteis | Fonte | Diâmetro |
|---|---|---|---|
| 762 | M-80, M-59, M-61, M-62 | BRL MR 1833 (Piddington 1967) | 7,82 mm |
| 556b | SS-109, M855 | BRL-MR-3476 (McCoy 1985) | 5,69 mm |
| 556t | L110, M856 (traçantes apagados) | idem | 5,69 mm |
| 50 | .50 Ball M33 | BRL-MR-3810 (McCoy 1990) | 12,95 mm |
| m101 | 155 mm M101 | BRL MR 1582 (Karpov 1964) | 155 mm |
| m483 | 155 mm M483A1 | BRL-CR-659 (Whyte 1991) | 154,7 mm |

**Conferência da transcrição e das conversões:** CMα = (VCG − CPN)·CNα fecha em 74 de 76 rodadas usando só valores medidos. Isso pega um CLα tomado por CNα, um CPN medido da base tratado como do nariz ou um dígito mal lido. As duas exceções são da 7,62, que a fonte já dá com dispersão de 0,02 pol. no CG.

## O que a correção pode usar

A escolha foi feita antes de olhar os erros. **A geometria o SPIN-73 já modela**, e as constantes dele foram ajustadas para isso. **O que ele não tem é a escala:** uma bala de 5,56 mm e uma granada de 155 mm com a mesma forma saem com os mesmos coeficientes, mas o número de Reynolds da granada é 25 vezes maior. Por isso:

- **CX0:** a correção é a lei de atrito de parede (Prandtl–Schlichting com compressibilidade de van Driest, a mesma forma do MC DRAG), com a área molhada calculada da geometria. O único parâmetro por regime é o comprimento de referência `L_ref`, embutido nas constantes do SPIN-73 (`reynolds.py`).
- **CNα, CMα, Cmq e Magnus:** a correção pode ser um viés constante, um viés proporcional a log d (escala) ou nenhum.
- **CPN:** não é corrigido à parte. Sai de CMα e CNα corrigidos, CPN = VCG − CMα/CNα, para que os três fiquem coerentes.

## Como se decide o que entra

Validação cruzada **deixando um grupo de fora, aninhada**: a escolha da forma também é feita sem o grupo de fora, então o erro medido é o de um projétil que o ajuste nunca viu. Cada grupo pesa o mesmo no ajuste e na métrica.

Uma correção entra no modelo final só se, nos grupos deixados de fora, atender às três condições:

1. o erro médio fica menor que o do SPIN-73;
2. melhora mais da metade dos grupos;
3. nenhum grupo fica com o erro mais que dobrado.

O critério 3 foi acrescentado depois de ver o Cmq transônico. Ele passava em 1 e 2 (87 % → 75 %, 4 de 6 grupos), mas piorava os dois 155 mm (M483A1: 35 % → 126 %). Fica registrado por transparência.

## Resultado (`resultado_correcao.txt`)

Erro de predição em grupos **não vistos**: RMS por grupo, média entre grupos.

| Coeficiente | Regime | SPIN-73 | Corrigido | Grupos que melhoram | Decisão |
|---|---|---|---|---|---|
| CX0 | subsônico | 19,5 % | **15,4 %** | 4/6 | aceita |
| CX0 | transônico | 12,7 % | **10,5 %** | 4/6 | aceita |
| CX0 | supersônico | 7,5 % | **6,0 %** | 4/6 | aceita |
| CNα | subsônico | 15,1 % | **10,2 %** | 4/6 | aceita |
| CNα | transônico | 9,3 % | **7,2 %** | 5/6 | aceita |
| CNα | supersônico | 8,7 % | 8,7 % | 0/6 | nenhuma forma ajuda |
| CPN (derivado) | subsônico | 0,36 cal | 0,30 cal | 2/5 | consequência |
| CPN (derivado) | transônico | 0,32 cal | **0,28 cal** | 5/6 | consequência |
| CMα | todos | 11–13 % | pior | 0/6 | rejeitada |
| Cmq | transônico | 87 % | 75 % | 4/6 | rejeitada (critério 3) |
| Cmq | sub, supersônico | — | pior | 0–1 | rejeitada |
| Magnus | todos | — | pior ou igual | ≤ 3/6 | rejeitada |

Modelo final, ajustado nos seis grupos:

- **CX0, comprimento de referência do atrito:** 0,10 m no subsônico, 0,33 m no transônico e 0,40 m no supersônico, entre os 20 mm e os 155 mm da base de dados do SPIN-73. Uma bala de 5,56 mm recebe cerca de +0,02 no CX0 em qualquer regime; uma granada de 155 mm, −0,017 no subsônico e −0,002 a −0,005 do transônico em diante.
- **CNα subsônico:** × (1 + 0,150 − 0,147·log₁₀(d/10 mm)), ou seja, +19 % a 5,56 mm e −2,5 % a 155 mm.
- **CNα transônico:** × 1,058.

## Leitura

- **O arrasto é onde a correção rende**, e por uma razão física identificável: o SPIN-73 não sabe o tamanho do projétil. Ele subestima o CX0 das armas portáteis em 10–20 % no subsônico e superestima o dos 155 mm, exatamente o sinal da lei de atrito.
- **CMα e Magnus não se corrigem com escala.** Os erros deles são próprios de cada forma: CMα da .50 +27 %, 7,62 subsônica −31 %. Com seis grupos, uma correção por forma não se distingue de ruído, e a validação cruzada mostra isso: todas as tentativas pioram os grupos não vistos. Corrigir essas colunas exige mais variedade de formas, não mais rodadas das mesmas.
- **O Cmq é dominado pela dispersão experimental** (o erro provável do próprio SPIN-73, na Tabela 1 do relatório, é de 3,0 unidades). No transônico, as armas portáteis pedem um amortecimento bem menor que o do SPIN-73, na mesma direção do fator 0,4 que a 7,62 já tinha dado. Os 155 mm discordam entre si.
- **O que continua fora:** o grupo .50 piora no CNα transônico (8,5 % → 16,4 %), e os traçantes de 5,56 mm pioram no CX0 subsônico (28 % → 34 %; a base arredondada deles não é o tronco de cone que o SPIN-73 supõe).

## Limites

- Seis grupos, quatro diâmetros distintos: a correção de escala foi ajustada entre 5,69 e 155 mm e não deve ser extrapolada fora disso.
- **Hipóteses nas entradas:** o meplat das balas de 5,56 mm (DM = 0,12) não está cotado; o raio de ogiva da 7,62 (9,74 cal) é incerto; os boattails arredondados dos traçantes entram como tronco de cone.
- **Arrasto de guinada:** para 5,56 mm vem da fonte; para .50 e M101, do próprio SPIN-73 (CX2 + CNα). Nas guinadas dessas rodadas, o efeito é de 1 a 3 % no CX0.
