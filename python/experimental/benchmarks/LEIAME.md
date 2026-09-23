# Benchmarks: o SPIN-73 contra voo livre

Aqui a pergunta é **"o SPIN-73 acerta a realidade?"**, não "a reconstrução reproduz o SPIN-73?" (esta está em `validation/`). Nos três casos, a reconstrução roda com a geometria da fonte, e o resultado é comparado com as medições de túnel balístico (spark range), rodada a rodada, depois de convertidas para a convenção do SPIN-73.

```
python experimental/benchmarks/comparar.py
```

| Arquivo | Fonte | Projétil | Convenção da fonte |
|---|---|---|---|
| `m101_karpov1964.csv` | Karpov et al., BRL MR 1582 (1964), DTIC AD0454925 | 155 mm M101, escala real, 64 rodadas | moderna: qd/V, pd/V → ×2 |
| `m483a1_whyte1991.csv` | Whyte, BRL-CR-659 (1991), DTIC ADA235620 | 155 mm M483A1, 65 tiros em 19 grupos | **a mesma do SPIN-73** (qd/2V, pd/2V) |
| `m33_mccoy1990.csv` | McCoy, BRL-MR-3810 (1990), DTIC ADA219106 | .50 Ball M33, 16 rodadas | moderna; **CLα** em vez de CNα; CPN medido da base |
| `nato556_mccoy1985.csv` | McCoy, BRL-MR-3476 (1985), DTIC ADA162133 | 5,56 NATO SS-109, M855, L110, M856, 35 rodadas | idem |

As conversões estão em `python/convencoes.py`; cada CSV traz no cabeçalho as definições da própria fonte e as células duvidosas.

## Resultado: razão SPIN-73 / medido (médias por faixa de Mach)

| Coeficiente | Faixa | M101 | M483A1 | .50 M33 |
|---|---|---|---|---|
| CX0 / CD | subsônico | 1,13 | **1,25** | 0,86 |
| | supersônico | 1,02 | 1,07 | 0,90 |
| CNα (CLα na .50) | subsônico | 1,07 | 0,99 | 0,89 |
| | supersônico | 0,99 | 1,05 | 1,10 |
| CMα | subsônico | 1,01 | 1,10 | 0,94 |
| | supersônico | **0,99** | **1,01** | **0,79** |
| Cmq + Cmα̇ | subsônico | 0,31 | 1,04 | (medido ≈ 0) |
| | supersônico | 0,93 | 0,92 | 1,05 |
| Magnus (momento) | subsônico | sinal oposto | — | 0,1 |
| | supersônico | 1,08 | 0,59 | ≈ 7 |
| Clp | supersônico | — | 0,98 | — |

O erro provável do próprio SPIN-73, segundo a Tabela 1 do relatório (p. 28), é de 0,12 a 0,17 no CMα, 0,06 a 0,11 no CNα, 0,007 a 0,009 no CX, 3,0 no Cmq e 0,12 a 0,18 no Magnus.

## Leitura

- **Supersônico, artilharia:** CMα, CNα, CX0 e Cmq a menos de 8 % nos dois 155 mm, dentro do erro provável que o próprio relatório declara. O M101 foi um dos projéteis da base de dados do SPIN-73 (referência 35 do relatório). O M483A1, de 1975, não foi.
- **.50 M33:** CMα 21 % baixo no supersônico, com o centro de pressão 0,36 cal atrás do medido. É uma forma fora do padrão dos projéteis de artilharia: cilindro de 1,1 cal, boattail de 0,78 cal e meplat de 0,18. Em Mach 1,2, a regra do cartão C209 (momento do boattail positivo) descarta o boattail inteiro.
- **Subsônico:** o CX0 do SPIN-73 erra de −14 % a +25 % conforme a forma. No M483A1, os +20 % não dependem do raio de ogiva adotado (0,182 a 0,193 para OR de 3,6 a 12).
- **Cmq subsônico e Magnus:** a dispersão das próprias medições é do tamanho do valor. O relatório do M101 mostra que o amortecimento subsônico muda de sinal entre modelo em escala e escala real. Não servem para calibrar nada.

Em nenhum dos três casos a reconstrução se afasta do que o SPIN-73 de 1973 imprimiria. No M101, com a mesma entrada da p. 59, ela reproduz a tabela do relatório. Os desvios acima são do modelo original.

## 5,56 mm NATO (`nato556_mccoy1985.csv`)

McCoy, BRL-MR-3476 (1985), DTIC ADA162133: SS-109, M855 e os traçantes L110 e M856, com 35 rodadas. A convenção é a mesma do .50: CLα, pd/V, qd/V, CPN a partir da base. Os comprimentos, 4,1 a 5,2 calibres, estão **dentro** da faixa do SPIN-73.

No supersônico, o SPIN-73 fica 4 a 7 % abaixo no CD e acerta o CMα a 1–10 %. No subsônico, subestima o CD em até 33 % (M855), no mesmo sentido da falta de escala (número de Reynolds) que aparece em todas as armas portáteis. A correção disso está em `../correcao/`.
