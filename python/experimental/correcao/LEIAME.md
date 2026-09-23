# Correção empírica do SPIN-73 com voo livre

O SPIN-73 reconstruído reproduz o programa de 1973, erros incluídos. Aqui ele é corrigido com medições de túnel balístico, **sem alterar o programa**: a correção parte da tabela do SPIN-73 e ajusta o que os dados mostram que dá para ajustar.

```
python experimental/correcao/ajuste.py      # valida, ajusta e grava python/spin73/correcoes/voo_livre.json
```

O ajuste fica aqui; a aplicação está na biblioteca, como correção opcional (desligada por padrão):

```python
import spin73
aero = spin73.Aerodinamica(p, "voo_livre", d_mm=5.69)        # tudo o que foi aceito
aero = spin73.Aerodinamica(p, "voo_livre:CX0", d_mm=5.69)    # só o arrasto (a peça robusta)
```

`aplicar.py` continua existindo como atalho (`aplicar.tabela_corrigida(p, d_mm)`).

## Dados

`dados.py` junta dez grupos de projéteis, com 1391 valores medidos, todos convertidos para a convenção do SPIN-73 (pd/2V, qd/2V, CNα e não CLα, CPN a partir do nariz, CX0 a guinada zero):

| Grupo | Projéteis | Fonte | Diâmetro | Forma |
|---|---|---|---|---|
| 762 | M-80, M-59, M-61, M-62 | BRL MR 1833 (Piddington 1967) | 7,82 mm | ogiva-cilindro-boattail |
| 556b | SS-109, M855 | BRL-MR-3476 (McCoy 1985) | 5,69 mm | idem |
| 556t | L110, M856 (traçantes apagados) | idem | 5,69 mm | longos, base arredondada |
| 50 | .50 Ball M33 | BRL-MR-3810 (McCoy 1990) | 12,95 mm | boattail longo |
| m101 | 155 mm M101 | BRL MR 1582 (Karpov 1964) | 155 mm | granada, cinta |
| m483 | 155 mm M483A1 | BRL-CR-659 (Whyte 1991) | 154,7 mm | ogiva composta |
| 762m | M118, 190 gr e 168 gr Sierra | BRL-MR-3733 (McCoy 1988) | 7,82 mm | match, boattail de 9,5° a 13° |
| 30 | XM788, XM788E1, XM789 | ARBRL-MR-03019 (McCoy 1980), ARBRL-TR-03432 (1982) | 29,92 mm | curtos (3,5 cal), ponta cônica, base sem boattail |
| t203 | 175 mm T203, modelo de 90 mm (só CX0) | BRL MR 956 (Karpov 1955) | 90 mm | a forma do M437 |
| xm617 | 152 mm XM617 | BRL MR 1998 (Brandon 1969) | 152 mm | **cone-cilindro**, base reta |

**Conferência da transcrição e das conversões:** CMα = (VCG − CPN)·CNα fecha em 152 de 154 rodadas usando só valores medidos (e as rodadas do 7,62 match e do 30 mm, a 2 %). Isso pega um CLα tomado por CNα, um CPN medido da base tratado como do nariz ou um dígito mal lido. As duas exceções são da 7,62 NATO, que a fonte já dá com dispersão de 0,02 pol. no CG. O XM617 fica fora dessa conta: a própria fonte fecha com o CG 0,022 cal atrás do CG do esquema (ver o CSV).

**Arrasto de guinada:** vem da fonte em todos os grupos novos — como número (5,56; T203; XM617) ou lido de gráfico (7,62 match, 30 mm). Com CDδ² de gráfico ou só médio, o CX0 só é tirado de rodadas com guinada até 5°. Na .50 e no M101, vem do próprio SPIN-73 (CX2 + CNα).

**O que ficou de fora e por quê:** a versão de base reta do T203 e o CMα/CNα do T203 (raio de ogiva não cotado; o CX0 do modelo com boattail muda no máximo 2 % com ele), rodadas acima de 10,5° de guinada (o coeficiente deixa de ser linear), o .22 LR (base com degrau), o 105 mm M1 (ogiva não cotada) e o 20 mm Navy (só gráficos). Detalhes em `fontes/LEIAME.md` e nos cabeçalhos dos CSV.

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

Erro de predição em grupos **não vistos**: RMS por grupo, média entre grupos. "Pior" é a maior razão entre o erro corrigido e o do SPIN-73 num grupo deixado de fora (o critério 3 rejeita acima de 2).

| Coeficiente | Regime | SPIN-73 | Corrigido | Grupos que melhoram | Pior | Decisão |
|---|---|---|---|---|---|---|
| CX0 | subsônico | 19,3 % | **15,1 %** | 7/9 | 1,46 | aceita |
| CX0 | transônico | 10,7 % | **8,2 %** | 7/10 | 1,43 | aceita |
| CX0 | supersônico | 6,6 % | **4,8 %** | 7/10 | 1,21 | aceita |
| CNα | subsônico | 13,2 % | 10,7 % | 5/9 | 1,97 | aceita, no limite |
| CNα | transônico | 11,2 % | 9,8 % | 7/9 | 2,01 | rejeitada, no limite |
| CNα | supersônico | 8,3 % | 8,8 % | 0/9 | | rejeitada |
| CMα | todos | 10–12 % | pior | 0–3/9 | | rejeitada |
| Cmq | transônico | 90 % | 72 % | 6/9 | 1,41 | aceita |
| Cmq | sub, supersônico | 205 %, 24 % | pior | 0–1 | | rejeitada |
| Magnus | todos | | pior no sub e no supersônico | ≤ 5/9 | ≥ 1,7 | rejeitada |
| CPN (derivado) | subsônico | 0,28 cal | 0,26 cal | 4/8 | | consequência |

Modelo final, ajustado nos dez grupos:

- **CX0, comprimento de referência do atrito:** 0,20 m no subsônico, 0,68 m no transônico e 0,82 m no supersônico. Uma bala de 5,56 mm recebe +0,020 a +0,027 no CX0; um 30 mm, +0,005 a +0,011; uma granada de 155 mm, −0,010 no subsônico e praticamente nada do transônico em diante.
- **CNα subsônico:** × (1 + 0,121 − 0,116·log₁₀(d/10 mm)): +15 % a 5,69 mm, −2 % a 155 mm.
- **Cmq transônico:** × (1 − 0,743 + 0,667·log₁₀(d/10 mm)): o amortecimento cai a 10–20 % do SPIN-73 nas armas portáteis, a 57 % no 30 mm e fica igual (+5 %) no 155 mm.

## Leitura

- **O arrasto é onde a correção rende, e é a única peça firme.** O SPIN-73 não sabe o tamanho do projétil: subestima o CX0 das armas portáteis e do 30 mm (no subsônico, até 16 % no 30 mm, 19 % no 7,62 match e 33 % no M855) e superestima o dos 155 mm, exatamente o sinal da lei de atrito. Com os grupos novos, a correção passou de melhorar 4 de 6 grupos para 7 de 9–10, e nenhum grupo piora mais que 1,5×.
- **As outras peças estão no limite da regra.** Com seis grupos, o CNα sub e transônico eram aceitos; com oito, o subsônico caiu (o 7,62 match, do mesmo calibre do 7,62 NATO e de outra forma, dobrava o erro); com dez, voltou por 1,97× e o transônico caiu por 2,01×. O Cmq transônico foi rejeitado com seis grupos e aceito com oito e com dez. A regra não foi mudada depois de ver isso; a margem fica registrada no JSON (`pior_razao`), e `"voo_livre:CX0"` é a escolha conservadora na biblioteca.
- **CMα e Magnus não se corrigem com escala.** Os erros são próprios de cada forma: no supersônico, CMα 9 a 14 % baixo no 7,62 match e 21 % na .50, e a 1–2 % no 152 mm cone-cilindro e no T203. Nenhuma correção por escala ajuda, e mais formas (dez grupos agora) não mudaram isso.
- **O Cmq e o Magnus subsônicos das armas portáteis e do 30 mm** são não lineares na própria fonte (Cmq medido positivo a pequena guinada; coeficientes cúbicos), algo que um coeficiente linear não representa.

## Limites

- Dez grupos, sete diâmetros distintos: a correção de escala foi ajustada entre 5,69 e 155 mm e não deve ser extrapolada fora disso.
- **Hipóteses nas entradas:** o meplat das balas de 5,56 mm (DM = 0,12) não está cotado; o raio de ogiva da 7,62 (9,74 cal) é incerto; os boattails arredondados dos traçantes entram como tronco de cone.
- **Hipóteses nas entradas (grupos novos):** 30 mm com a ponta cônica de 17° dentro do comprimento de ogiva (o SPIN-73 só descreve ogiva + meplat) e base arredondada como base reta; cintas do 30 mm com BD = 1,02 (não cotadas); T203 com OR, DM e BD do cartão do M437.
- **Arrasto de guinada:** ver "Dados". Na .50 e no M101 vem do próprio SPIN-73 (CX2 + CNα); nas guinadas dessas rodadas, o efeito é de 1 a 3 % no CX0.
