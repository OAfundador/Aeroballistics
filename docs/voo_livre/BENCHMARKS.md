# Benchmarks: o SPIN-73 contra voo livre

Aqui a pergunta é **"o SPIN-73 acerta a realidade?"**, não "a reconstrução reproduz o SPIN-73?" (esta está em [../VERIFICACAO.md](../VERIFICACAO.md)). Em todos os casos, a reconstrução roda com a geometria da fonte, e o resultado é comparado com as medições de túnel balístico (spark range), rodada a rodada, depois de convertidas para a convenção do SPIN-73.

```
python scripts/voo_livre/benchmarks/comparar.py
```

| Arquivo | Fonte | Projétil | Convenção da fonte |
|---|---|---|---|
| `m101_karpov1964.csv` | Karpov et al., BRL MR 1582 (1964), DTIC AD0454925 | 155 mm M101, escala real, 64 rodadas | moderna: qd/V, pd/V → ×2 |
| `m483a1_whyte1991.csv` | Whyte, BRL-CR-659 (1991), DTIC ADA235620 | 155 mm M483A1, 65 tiros em 19 grupos | **a mesma do SPIN-73** (qd/2V, pd/2V) |
| `m33_mccoy1990.csv` | McCoy, BRL-MR-3810 (1990), DTIC ADA219106 | .50 Ball M33, 16 rodadas | moderna; **CLα** em vez de CNα; CPN medido da base |
| `nato556_mccoy1985.csv` | McCoy, BRL-MR-3476 (1985), DTIC ADA162133 | 5,56 NATO SS-109, M855, L110, M856, 35 rodadas | idem |
| `match762_mccoy1988.csv` | McCoy, BRL-MR-3733 (1988), DTIC ADA205633 | 7,62 match M118, 190 gr e 168 gr Sierra, 39 rodadas | idem |
| `xm788_mccoy1980.csv` | McCoy, ARBRL-MR-03019 (1980), DTIC ADA086096 | 30 mm XM788, 16 rodadas | idem (e Clp com pd/V) |
| `x30mm_mccoy1982.csv` | McCoy, ARBRL-TR-03432 (1982), DTIC ADA121258 | 30 mm XM788E1 e XM789, 43 rodadas | idem |
| `t203_karpov1955.csv` | Karpov et al., BRL MR 956 (1955), DTIC AD0086528 | 175 mm T203, modelos de 90 mm com boattail e de base reta, 35 rodadas | **notação K** do BRL, como impressa |
| `xm617_brandon1969.csv` | Brandon, BRL MR 1998 (1969), DTIC AD0857512 | 152 mm XM617, cone-cilindro, escala real, 14 rodadas | moderna, com **CNα** (não CLα); CPN da base |

Os CSV estão em `data/voo_livre/`, e as conversões em `src/spin73/convencoes.py`. Cada CSV traz no cabeçalho as definições da própria fonte e as células duvidosas.

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

No supersônico, o SPIN-73 fica 4 a 7 % abaixo no CD e acerta o CMα a 1–10 %. No subsônico, subestima o CD em até 33 % (M855), no mesmo sentido da falta de escala (número de Reynolds) que aparece em todas as armas portáteis. A correção disso está em [CORRECAO.md](CORRECAO.md).

## 7,62 match, 30 mm, 175 mm T203 e 152 mm XM617

Os CSV guardam os valores como impressos. O CDδ², quando a fonte só o dá em gráfico, foi lido do gráfico e está no cabeçalho (7,62 match: Figs. 21–23; 30 mm: Figs. 12 e 17, retas por trecho).

- **7,62 match** (M118, 190 e 168 gr Sierra; 3,98 a 4,31 cal, boattails de 9,5° a 13°): CMα supersônico 9 a 14 % abaixo do medido, como já acontecia com a .50 — as formas de arma portátil de boattail longo são as que o SPIN-73 erra no momento. CD supersônico 5 a 10 % baixo; subsônico 9 a 19 % baixo.
- **30 mm** (3,49 e 3,61 cal, ponta cônica, cintas, base sem boattail): CMα e CPN a 0–7 % em todos os regimes, CLα a 2–15 %. O CD fica 6 % baixo no supersônico e **5 a 16 % baixo no subsônico**, de novo o sinal da escala (Reynolds).
- **175 mm T203, modelo de 90 mm** (é o M437 em desenvolvimento: as três cotas do esboço batem com o cartão do M437 no SPIN-73): **CD a 1 %** e **CMα supersônico a 1 %**. O raio de ogiva não está cotado. Com o OR do M437 (25 cal) o CMα fecha; com o 15,8 cal medido no desenho, ficaria 11 % abaixo em Mach 1,15. Por isso mesmo o CMα do T203 não entra no ajuste da correção (seria circular): só o CX0, que muda no máximo 2 % com o OR. O KN, tirado do desvio da trajetória com 12 % de erro-padrão, sai 27 % acima do SPIN-73 no supersônico — as rodadas que o têm voaram a 4,5–7,4° de guinada, onde a força normal já não é linear. A versão de base reta só está arquivada: com a ogiva de 3,97 cal e o raio não cotado, o CX0 do SPIN-73 muda 15 % conforme o OR.
- **152 mm XM617, cone-cilindro** (3,15 cal, cone de 14°, base reta, projétil leve): no supersônico, **CD, CMα, CNα e CPN a 0–2 %** do SPIN-73. No transônico, CMα 13 % alto e CD 9 % baixo, com dispersão grande nas próprias medições. Cmq supersônico 42 % mais amortecido no SPIN-73 que o medido. A fonte fecha CPN − CMα/CNα com o CG 0,022 cal atrás do CG do esquema; a comparação usa o do esquema.
- **Cmq e Magnus subsônicos** no 7,62 match e no 30 mm: a fonte mede Cmq positivo (instabilidade dinâmica a pequena guinada) e Magnus bem mais negativo que o SPIN-73. A fonte trata isso como não linearidade (coeficientes cúbicos). Nenhuma correção linear pega isso.
