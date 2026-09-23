# Dados experimentais para a recalibração

Recalibração = mesmas equações do SPINNER/SPIN-73, constantes reajustadas a dados de voo livre.
O resultado NÃO é o SPIN-73 original e fica separado da reconstrução (diretório pai).

## Fontes (ambas Distribution A)
- BRL MR 1833 (Piddington 1967, AD815788): família 7.62 NATO, 4 projéteis, 56 rodadas.
  - `mr1833_tabela2.csv` — Tabela II, na normalização do relatório (não convertida).
  - `mr1833_geometria.csv` — geometria em calibres (entradas do SPIN-73), CG confirmado por identidade.
- BRL Report 620 (Hitchcock 1947/52, AD-800 469): compêndio de ~100 projéteis. Ainda não extraído.

## Conversões de normalização
| Grandeza | MR 1833 | Hitchcock | SPIN-73 |
|---|---|---|---|
| Magnus | Cmpa, p·d/V | K_S | Cnpa, p·d/(2V) → ×2 |
| Amortecimento | Cmq+Cmα̇, q·d/V | K_H | Cmq, q·d/(2V) → ×2 |
| Momento de tombamento | CMα | K_M | CMA = (8/π)·K_M |
| Centro de pressão | pol. da base | h (cal. da base) | calibres do nariz |

## Primeiro resultado (`comparar_magnus.py`)
O Magnus reconstruído do SPIN-73 superestima o da 7.62 em +0,3 a +0,5 (unidades p·d/2V)
no supersônico e não reproduz a troca de sinal abaixo de Mach ~1,5. A ordenação por
comprimento (M-80 < M-59 ≈ M-61 < M-62) é a mesma do experimento. Trocar o fator de
normalização (×1) ou o sinal piora a concordância, então o viés não vem da conversão.
Hipóteses de interpolação (em Mach e em guinada, sem E3) estão no cabeçalho do script.

## Recalibração por MMQ na 7.62 (`recalibrar_mr1833.py`, saída em `resultado_recalibracao_mr1833.txt`)

**Limite de identificabilidade.** Avaliadas nas quatro geometrias, as matrizes de regressores
completas do SPIN-73 têm posto 3 (CX, 11 constantes), 3 (CNα, 9) e 4 (Cmq, 8), com o 3º/4º
valor singular já pequeno. Com esta família só se ajusta um MODELO REDUZIDO por coeficiente:
constante da família + termo de comprimento, cada um quadrático em Mach, no supersônico
(M ≥ 1,1). As constantes individuais do SPIN-73 (a_i, B_i, C_i, F_i) não saem daqui; isso
exige a variedade de formas do Hitchcock.

**Qualidade.** Em todos os ajustes o resíduo é da ordem do erro puro, estimado pelas
rodadas repetidas: CD0 0,009/0,009; CNα 0,23/0,27; CNα·CPN 0,55/0,63; Cmq 1,5/1,1.
Não há falta de ajuste detectável; o limite é o ruído experimental.

**Magnus recalibrado.** Com E1 fixo no valor reconstruído, o E efetivo da 7.62 fica em
2,2–2,6 (±0,1), contra 3,0–3,1 no SPIN-73. É o viés visto em `comparar_magnus.py`,
agora quantificado na própria constante do modelo.

**Hipóteses a lembrar.** Lei de arrasto de guinada por partes contínua (o relatório só dá
os dois valores); a inclinação positiva de CD0 com o comprimento (~5 % entre M-80 e M-59)
é sensível a essa hipótese, e o relatório descreve os dois como praticamente iguais.
Transônico e subsônico (só M-80) não foram ajustados.

## Cmq e centro de pressão contra o experimento (`comparar_cmq_cp.py`)

Agora que XF (Cmq, com o termo não documentado F9) e XC (centro de pressão) foram lidos, os dois entram na comparação. Saída em `resultado_cmq_cp_mr1833.txt`.

**Cmq: o SPIN-73 amortece demais.** O viés contra as rodadas é de −2,2 (M-80) a −4,9 (M-62) em unidades de q·d/2V, sempre maior que a dispersão experimental (1,3 a 2,4) e que o erro puro entre rodadas repetidas (1,13). Contra a curva experimental ajustada, a diferença é enorme no transônico e some no supersônico alto:

| Mach | 1,2 | 1,5 | 2,0 | 2,5 |
|---|---|---|---|---|
| k(M) = experimento / SPIN-73 | 0,40 ± 0,04 | 0,66 ± 0,03 | 0,90 ± 0,04 | 0,90 ± 0,03 |

Ou seja: em Mach 1,2 o modelo dá um amortecimento 2,5 vezes maior que o medido; em Mach 2 a 2,5 o erro cai para 10 %. Em Mach 1,2 a própria curva experimental é mal determinada (±4 a 5,5 unidades), porque há poucas rodadas abaixo de 1,3 — o fator 0,40 ali deve ser lido com essa ressalva. O ajuste é de um fator de escala por Mach, quadrático em (M − 2): com quatro projéteis quase iguais não se identificam F1..F9 individualmente (posto 4), mas a escala sai bem determinada.

**Centro de pressão: concorda onde dá para comparar.** A reconstrução do CPN só existe em Mach 1,2 e 2,0 no supersônico, porque o cartão de continuação de XC15 não foi impresso no relatório (ver `docs/NOTAS_TRANSCRICAO.md`, T6.2). Em Mach 2,0 o modelo acerta o M-59 (1,691 contra 1,692 ± 0,171) e o M-61 (1,693 contra 1,704), e erra o M-62 em −0,25. O M-62 é o de base arredondada, que o modelo do SPIN-73 não representa — o mesmo projétil que já destoava no CNα. A sensibilidade ao raio de ogiva suposto (9,74 cal, incerto) é de ±0,06 calibre entre OR = 8 e 12, menor que o desvio do M-62.

**Ordem de grandeza dos três desvios já medidos nesta família:** Magnus +0,3 a +0,5 (superestima), CNα +0,28 só no M-80 (o mais curto), Cmq 2,5× no transônico e 10 % no supersônico (superestima). Todos apontam o mesmo sentido: o SPIN-73 foi calibrado em projéteis de artilharia, bem maiores que a 7,62.

## Compêndio do Hitchcock (BRL 620) — `hitchcock/`

O AD-800 469 (Hitchcock, *Aerodynamic Data for Spinning Projectiles*, 1947/1952) é o compêndio que faltava: ~100 projéteis agrupados por calibre, cada um com esboço cotado em calibres, tabela de características físicas (peso, CG, momentos de inércia) e tabelas de K_M (momento), K_L (força de vento cruzado), K_H (amortecimento) e K_I, com a velocidade de cada série de tiros. É a variedade de formas que a família 7,62 não tem.

O PDF é um scan com camada de OCR que **não** capturou os números — só a prosa. As páginas são imagens CCITT G4 dentro do PDF, e `ferramentas/pagina_pdf.py` as extrai embrulhando o stream num TIFF, sem depender de poppler. A impressão é tipografada e bem legível, ao contrário da matricial do SPIN-73.

### Conversões (`conversoes.py`), verificadas e não supostas

| Grandeza | BRL | SPIN-73 |
|---|---|---|
| Arrasto | K_D | CX = (8/π)·K_D |
| Momento de tombamento | K_M | CMα = (8/π)·K_M |
| Força de vento cruzado | K_L | CNα = (8/π)·K_L + CX |
| Amortecimento | K_H | Cmq = −(16/π)·K_H |
| Posições | g, h da base | VCG = VL − g, CPN = VL − h |

As duas últimas são as que costumam dar errado. Foram conferidas numericamente no calibre 0.30 Ball M2 (`test_cal030.py`):

- **K_M:** o CMα implicado pelo fator de estabilidade medido (S = 3,42), calculado com a fórmula de s_g do SPIN-73 e os momentos de inércia do próprio relatório, dá **1,286** contra **1,299** de (8/π)·0,51 — 1 % de diferença. Isso valida ao mesmo tempo a conversão e a fórmula de estabilidade reconstruída, contra uma fonte independente e 25 anos anterior.
- **K_H:** o Cmq reconstruído nessa geometria em Mach 2,49 é **−12,90** contra **−13,24** de −(16/π)·2,6 — 3 %. O fator 2 entre q·d/V e q·d/2V é necessário; sem ele sobraria quase o dobro.
- **K_L:** (8/π)·0,98 = 2,496 com CNα reconstruído de 2,918 implica CX = 0,42, e o gráfico de arrasto da mesma página dá CX ≈ 0,38.

Ou seja: no Mach 2,5 desse projétil, o Cmq do SPIN-73 erra 3 %. É coerente com o que a 7,62 mostrou (fator 0,90 em Mach 2 a 2,5) e reforça que o problema do Cmq está no transônico, não no supersônico.

### Fórmulas empíricas do próprio Hitchcock

A p. 11 do relatório traz os antecessores diretos das equações do SPIN-73, lineares nas mesmas variáveis geométricas (ângulo e comprimento do boattail, comprimento cilíndrico, ogiva, raio de ogiva) mas **sem dependência de Mach**:

    K_N = 0,020a − 0,748b + 0,1715c + 0,540d − 0,0266e
    h   = −0,0135a + 1,97b + 0,6276c + 0,4837d − 0,0233e

No Ball M2, a fórmula de h dá o centro de pressão a 0,06 calibre do valor implicado pelo experimento — o que também sustenta a leitura de XC que fizemos no baseline.

### Calibre 0.30 completo e validado (`dados_cal030.py`, `test_cal030.py`)

Lidos: os quatro esboços (p. 16), características físicas de 5 projéteis (p. 18), tabelas de estabilidade e de amortecimento (p. 20).

**Validação em três níveis.** O mais forte não depende do SPIN-73: são identidades do próprio relatório, que pegam qualquer dígito mal lido.

*Geometria.* Os quatro esboços fecham pela soma das partes: Ball M1 0,81 + 1,20 + 2,43 = 4,44; Ball M2 1,32 + 2,43 = 3,75; A.P. M2 2,12 + 2,45 = 4,57; Tracer M1 2,30 + 2,45 = 4,75.

*Estabilidade.* Para cada série de tiro, o K_M impresso tem de bater com o fator de estabilidade S, a velocidade e os momentos de inércia tabelados. Quando o Mach está impresso, a temperatura da série sai de a = V/M e corrige a densidade.

| Projétil | CMα do S / (8/π)·K_M | Leitura |
|---|---|---|
| Ball M2 | 0,990 | verificada |
| Tracer M1 (inércia média, como manda a nota) | 0,982 | verificada |
| Frangible M22 | 0,989 | verificada |
| A.P. M2 | 1,044 | dentro da incerteza de temperatura (Mach não impresso) |
| Ball M1 (três séries) | 1,094 / 1,090 / 1,122 | **inconsistência na fonte** |

O Ball M1 erra na mesma direção nas três séries. A célula suspeita, B = 16,40, foi relida em zoom e é tipografia inequívoca — não é erro de transcrição. Um B de 18,40 (par 6/8) conciliaria as três séries (0,97–1,00) e poria o Ball M1 no padrão da fórmula de inércia da p. 9, que os outros três seguem. Fica registrado como hipótese de erro tipográfico no original, sem alterar o valor impresso.

**SPIN-73 contra o experimento**, com as conversões já verificadas:

| Projétil | Base | Cmq modelo / medido | CX implicado pelo K_L |
|---|---|---|---|
| Ball M2 | reta | 0,97 | 0,42 (gráfico da p. 19: ≈ 0,38) |
| Tracer M1 | reta | 0,90 | 0,19 (baixo; o traçante reduz o arrasto de base) |
| Ball M1 | boattail 0,81 | 0,75 | 0,91 (impossível) |

Nos dois projéteis de base reta o modelo acerta o Cmq em 3–10 % e o CNα de forma coerente com o arrasto. No Ball M1, com boattail, erra 25 % no Cmq e cerca de 0,5 no CNα — mas é também o projétil cujos dados são internamente inconsistentes na fonte. **Não dá para concluir nada sobre os termos de boattail do SPIN-73 com um único ponto duvidoso**: é preciso boattails de outras seções de calibre.

O CMα do modelo não pôde ser comparado diretamente: nesses Mach (1,8 a 2,6), o CPN reconstruído não existe, por causa do cartão XC15 que não foi impresso (NOTAS_TRANSCRICAO.md, T6.2).

### Próximas fatias

Cada seção de calibre custa cerca de três páginas (esboços, características físicas, estabilidade e amortecimento). Prioridade: seções com **boattails** de dados consistentes, que é o que o calibre 0.30 deixou em aberto.
