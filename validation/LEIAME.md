# Quanto a reconstrução erra

`python validation/comparacao_erros.py` roda o programa só a partir da geometria e compara cada célula com as tabelas de 1973 transcritas: o 175 mm M437 inteiro, o CNα de 10 tabelas, o Magnus de 6, o Cmq de 4, e CX, CX2 e CPN do 5"/38. Saídas: `erros_por_celula.csv` (cada célula) e `resumo_erros.csv` (por coluna).

O erro é medido em **unidades da última casa impressa** — numa coluna de 3 casas, 1 unidade = 0,001. Como o programa original arredondava nessa casa, até ±0,5 unidade o modelo é indistinguível dele; o critério do projeto é ±1,5 unidade. Células em que algum DATA foi decidido usando a própria tabela (circulares) ficam fora da estatística.

## Resultado (22/09/2026)

1030 células; 810 independentes. Sem a tabela do 90 mm M71, cuja transcrição é sabidamente degradada: **85 % indistinguíveis do original, 91 % no critério, erro mediano de 0,24 unidade.**

| Coluna | Tabelas | Células | ≤ 0,5 un. | ≤ 1,5 un. | Mediana | Comentário |
|---|---|---|---|---|---|---|
| CX | 2 | 32 | 88 % | 100 % | 0,25 | |
| CYPA, CNPA, CNPA5, CNPA3 | 1–6 | 150 | 100 % | 100 % | 0,05–0,35 | |
| CPF1, CPF5 | 6 | 196 | 96 % | 97 % | < 0,1 | os desvios são células impressas ambíguas (NOTAS, T2) |
| CLP | 3 | 51 | 96 % | 100 % | 0,24 | |
| CMQ | 3 | 51 | 73 % | 96 % | 0,30 | pior célula: Mach 1,1 (DATA XF mal lido) |
| CNA | 9 | 113 | 72 % | 85 % | 0,36 | sem o M71; com ele, 77 % |
| CX2 | 2 | 28 | 39 % | 46 % | 2,0 | herda o erro do CNα reconstruído (até 2,2 un.); com o CNα impresso fecha |
| CPN, CMA | 2 | 31 | 29–36 % | 35–43 % | 3–13 | o bloco mais fraco: cartão XC15 ausente; Mach 2,5 erra 0,17 cal no 5"/38 |
| Estabilidade (GYRO, SBAR, RECIP, SPIN, W, λ, DELT, DISP) | 1 | 5–17 cada | 20–100 % | 60–100 % | 0,1–1,2 | só o M437 tem esse bloco; as que dependem do CMα só têm 5 Mach independentes |

## Duas perguntas diferentes

Este resultado responde **"a reconstrução reproduz o SPIN-73 de 1973?"**. Nos blocos lidos diretamente do código e dos DATA, sim, no nível do arredondamento da impressão; o ponto fraco é o centro de pressão.

A outra pergunta — **"o SPIN-73 acerta a realidade?"** — está em `python/experimental/`. Contra voo livre da família 7,62 NATO, o modelo de 1973 superestima o Magnus (+0,3 a +0,5 em p·d/2V) e o amortecimento Cmq (2,5 vezes em Mach 1,2, 10 % em Mach 2 a 2,5) e erra o CNα do projétil mais curto (+0,28). Contra o Ball M2 do Hitchcock (calibre 0.30, Mach 2,5), o Cmq erra 3 %. Esses erros são do modelo original, não da reconstrução.
