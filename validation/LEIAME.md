# Quanto a reconstrução erra

`python validation/comparacao_erros.py` roda o programa só a partir da geometria e compara cada célula com as tabelas de 1973 transcritas: o 175 mm M437 e o 105 mm XM380E5 inteiros, o CNα de 10 tabelas, o Magnus de 7, o Cmq de 5, e CX, CX2 e CPN do 5"/38. Saídas: `erros_por_celula.csv` (cada célula) e `resumo_erros.csv` (por coluna).

O erro é medido em **unidades da última casa impressa** — numa coluna de 3 casas, 1 unidade = 0,001. Como o programa original arredondava nessa casa, até ±0,5 unidade o modelo é indistinguível dele; o critério do projeto é ±1,5 unidade. Células em que algum DATA foi decidido usando a própria tabela (circulares) ficam fora da estatística, assim como as resolvidas por identidade entre colunas impressas.

## Resultado (23/09/2026)

1235 células; 997 independentes. Sem a tabela do 90 mm M71, cuja transcrição é sabidamente degradada: **88 % indistinguíveis do original, 94 % no critério, erro mediano de 0,26 unidade** (985 células). Na véspera, antes da terceira tabela com boattail, eram 85 % e 91 % em 798 células.

| Coluna | Tabelas | Células | ≤ 0,5 un. | ≤ 1,5 un. | Mediana | Comentário |
|---|---|---|---|---|---|---|
| CX | 3 | 49 | 92 % | 100 % | 0,26 | |
| CYPA, CNPA, CNPA5, CNPA3, CNPA5P | 2–7 | 248 | 97–100 % | 97–100 % | 0,2–0,35 | |
| CPF1, CPF5 | 7 | 229 | 97 % | 97 % | 0,1–0,2 | os desvios são células impressas ambíguas (NOTAS, T2) |
| CLP | 4 | 67 | 97 % | 100 % | 0,25 | |
| CMQ | 4 | 59 | 80 % | 100 % | 0,25 | o cartão ausente do XF7 explicava Mach 1,1 (T13) |
| CNA | 9 | 118 | 71 % | 86 % | 0,34 | sem o M71; com ele, 78 % |
| CX2 | 3 | 40 | 50 % | 62 % | 0,51 | herda o erro do CNα reconstruído (até 2,2 un.); com o CNα impresso fecha |
| CPN | 3 | 28 | 57 % | 79 % | 0,34 | XM380E5: 94 % no critério; os desvios são do 5"/38 (Mach 1,75 e 2,5 a 5, sistemático) |
| CMA | 3 | 27 | 63 % | 63 % | 0,33 | idem; no 5"/38 soma o CNα impresso 0,014 abaixo |
| Estabilidade (GYRO, SBAR, RECIP, SPIN, W, λ, DELT, DISP) | 1 | 120 | 87 % | 97 % | 0,23 | só o M437 tem esse bloco; as que dependem do CMα só têm 4 Mach independentes |

A tabela do XM380E5 (p. 50), que não decidiu nenhum DATA, é o teste mais limpo: 222 células independentes, 92 % indistinguíveis e 98 % no critério.

## Duas perguntas diferentes

Este resultado responde **"a reconstrução reproduz o SPIN-73 de 1973?"**. Nos blocos lidos diretamente do código e dos DATA, sim, no nível do arredondamento da impressão; o ponto fraco é o centro de pressão.

A outra pergunta — **"o SPIN-73 acerta a realidade?"** — está em `python/experimental/`. Contra voo livre da família 7,62 NATO, o modelo de 1973 superestima o Magnus (+0,3 a +0,5 em p·d/2V) e o amortecimento Cmq (2,5 vezes em Mach 1,2, 10 % em Mach 2 a 2,5) e erra o CNα do projétil mais curto (+0,28). Contra o Ball M2 do Hitchcock (calibre 0.30, Mach 2,5), o Cmq erra 3 %. Esses erros são do modelo original, não da reconstrução.
