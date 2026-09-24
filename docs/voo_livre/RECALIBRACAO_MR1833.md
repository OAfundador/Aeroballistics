# Dados experimentais para a recalibração

Recalibração = mesmas equações do SPINNER/SPIN-73, constantes reajustadas a dados de voo livre.
O resultado NÃO é o SPIN-73 original e fica separado da reconstrução: scripts em
`scripts/voo_livre/` (esta página: `mr1833/` e `hitchcock/`), dados em `data/voo_livre/`.

## Fontes (ambas Distribution A)
- BRL MR 1833 (Piddington 1967, AD815788): família 7.62 NATO, 4 projéteis, 56 rodadas.
  - `data/voo_livre/mr1833_tabela2.csv` — Tabela II, na normalização do relatório (não convertida).
  - `data/voo_livre/mr1833_geometria.csv` — geometria em calibres (entradas do SPIN-73), CG confirmado por identidade.
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

## Recalibração por MMQ na 7.62 (`recalibrar_mr1833.py`, saída em `docs/resultados/recalibracao_mr1833.txt`)

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

## CNα contra o experimento (`comparar_cna.py`)

Saída em `docs/resultados/cna_mr1833.txt`. Viés rodada a rodada (M ≥ 1,1, OR = 9,74 cal): +0,214 no M-80, −0,033 no M-59, −0,062 no M-61 e −0,116 no M-62, contra dispersão experimental de 0,17 a 0,31 e erro puro de 0,27 entre rodadas repetidas. Só o do M-80 passa de duas vezes o erro-padrão da média (erro puro/√n = 0,071, 15 rodadas). O raio de ogiva suposto não pesa: de OR = 8 a 12 cal, o viés muda no máximo 0,005. Contra a curva ajustada, o modelo dá praticamente o mesmo CNα aos quatro projéteis (a curva do M-80 fica no máximo 0,02 acima das outras entre Mach 1,2 e 2,5), enquanto o experimento cresce com o comprimento: em Mach 2,0, 2,725 no M-80, 2,98 a 2,99 no M-59 e no M-61 e 3,178 no M-62.

A primeira comparação (`docs/NOTAS_TRANSCRICAO.md`, T5) dava +0,28 no M-80 (+0,01, −0,01 e −0,08 nos outros). Ela é anterior ao cartão C205 (NOTAS, T15), que zera a força normal do boattail quando ela sai positiva, o que acontece na 7,62 no supersônico, de ogiva curta. A saída repete a conta sem o cartão e reproduz os valores antigos (+0,276, +0,009, −0,011, −0,082).

## Cmq e centro de pressão contra o experimento (`comparar_cmq_cp.py`)

Agora que XF (Cmq, com o termo não documentado F9) e XC (centro de pressão) foram lidos, os dois entram na comparação. Saída em `docs/resultados/cmq_cp_mr1833.txt`.

**Cmq: o SPIN-73 amortece demais.** O viés contra as rodadas é de −2,2 (M-80) a −4,9 (M-62) em unidades de q·d/2V, sempre maior que a dispersão experimental (1,3 a 2,4) e que o erro puro entre rodadas repetidas (1,13). Contra a curva experimental ajustada, a diferença é enorme no transônico e some no supersônico alto:

| Mach | 1,2 | 1,5 | 2,0 | 2,5 |
|---|---|---|---|---|
| k(M) = experimento / SPIN-73 | 0,40 ± 0,04 | 0,66 ± 0,03 | 0,90 ± 0,04 | 0,90 ± 0,03 |

Ou seja: em Mach 1,2 o modelo dá um amortecimento 2,5 vezes maior que o medido; em Mach 2 a 2,5 o erro cai para 10 %. Em Mach 1,2 a própria curva experimental é mal determinada (±4 a 5,5 unidades), porque há poucas rodadas abaixo de 1,3 — o fator 0,40 ali deve ser lido com essa ressalva. O ajuste é de um fator de escala por Mach, quadrático em (M − 2): com quatro projéteis quase iguais não se identificam F1..F9 individualmente (posto 4), mas a escala sai bem determinada.

**Centro de pressão: não concorda rodada a rodada.** A reconstrução do CPN existe hoje nos 17 Mach. O cartão de continuação de XC15 não foi impresso no relatório, e as nove células que faltavam (Mach 1,2 a 5,0) foram decididas pelo modelo a partir das tabelas de 1973, não lidas (`src/spin73/dados/xc_lidos.py`; `docs/NOTAS_TRANSCRICAO.md`, T6.2 e T13): Mach 1,2, 1,35, 1,5 e 2,0 pelo 175 mm M437 e pelo 5"/38 juntos (`RECUPERADOS`); Mach 1,75 e 2,5 a 5,0 só pelo M437 (`DECIDIDOS_M437`; o 105 mm XM380E5, fora da decisão, fecha nesses Mach, mas pesa pouco no XC15). Na mesma faixa também foram decididos o XC1 de Mach 2,5 (lido 1,90, decidido 1,99) e o XC12 de Mach 1,35 e 1,5 (`CORRECOES`). Nenhum desses valores saiu do voo livre, então a comparação não é circular, mas o CPN do modelo acima de Mach 1,1 depende deles.

A saída lista as células de XC decididas pelo modelo que entram no CPN das rodadas (Mach 1,13 a 2,85): o XC15 de Mach 1,2 a 3,0, o XC12 de Mach 1,35 e 1,5 e o XC1 de Mach 2,5.

Rodada a rodada (M ≥ 1,1), o modelo põe o centro de pressão atrás do medido: +0,22 calibre no M-80, +0,16 no M-59 e +0,14 no M-61, maiores que a dispersão experimental (0,07 a 0,08) e que o erro puro entre rodadas repetidas (0,085). No M-62 o viés é −0,07, do tamanho da dispersão (0,07); a marca "maior que a dispersão" do script se decide na terceira casa. A média esconde a dependência em Mach, que a curva ajustada e o fator k(M) mostram.

Contra a curva experimental ajustada, o CPN medido de cada rodada (VCG − CMα/CNα, só valores medidos) é ajustado diretamente, com o modelo reduzido do CNα·CPN (constante + CXLL, quadráticos em M − 2); o resíduo (0,084) fica no nível do erro puro (0,085). A versão anterior do script ajustava o CNα·CPN e dividia pelo CNα **do modelo**: o viés de CNα do SPIN-73 (+0,21 no M-80) passava para o lado experimental, e a incerteza da curva, que vinha da do CNα·CPN, saía bem mais larga. Modelo menos curva, em calibres, com a incerteza da curva:

| Mach | 1,2 | 1,5 | 2,0 | 2,5 |
|---|---|---|---|---|
| M-80 | +0,036 ± 0,173 | +0,135 ± 0,089 | +0,180 ± 0,113 | +0,345 ± 0,087 |
| M-59 | −0,103 ± 0,116 | −0,001 ± 0,060 | +0,064 ± 0,076 | +0,239 ± 0,059 |
| M-61 | −0,109 ± 0,113 | −0,007 ± 0,059 | +0,060 ± 0,075 | +0,234 ± 0,058 |
| M-62 | −0,257 ± 0,073 | −0,174 ± 0,039 | −0,082 ± 0,049 | +0,080 ± 0,038 |

O desvio cresce com o Mach nos quatro projéteis. De Mach 1,2 a 2,0, o modelo fica dentro da incerteza no M-59 e no M-61; o M-80 sai dela a partir de Mach 1,5. Em Mach 2,5, onde o CPN usa o XC15 decidido só pelo M437 e o XC1 decidido, o M-80, o M-59 e o M-61 ficam 0,23 a 0,35 calibre atrás. O M-62, de base arredondada (que o modelo do SPIN-73 não representa), vai de −0,26 em Mach 1,2 a +0,08 em 2,5, fora da incerteza em todos os pontos. A sensibilidade ao raio de ogiva suposto (9,74 cal, incerto) é de −0,06/+0,05 calibre entre OR = 8 e 12 (M-80, Mach 2,0).

**Fator k(M) do CPN.** Com o CPN do modelo em toda a faixa, o k(M) é calculado como o do Cmq, nas mesmas 42 rodadas, com o CPN medido de cada rodada. (O par que o script deixava de lado, o CNα·CPN medido contra o CPN do modelo, daria um k da ordem do próprio CNα, sem sentido como fator de escala.)

| Mach | 1,2 | 1,5 | 2,0 | 2,5 |
|---|---|---|---|---|
| k(M) = experimento / SPIN-73 | 1,03 ± 0,03 | 0,99 ± 0,02 | 0,92 ± 0,02 | 0,87 ± 0,02 |

Com o OR suposto (9,74 cal), o modelo acerta a família até Mach 1,5; acima, põe o centro de pressão atrás do medido, 8 % em Mach 2,0 e 13 % em 2,5. Três ressalvas, todas na saída:

- O resíduo (0,138) fica acima do erro puro (0,085): um fator de escala único não descreve o M-62, que desvia no sentido oposto aos outros três. Sem ele, o resíduo cai para 0,087 e o k fica em 1,01 / 0,96 / 0,89 / 0,83.
- O raio de ogiva suposto pesa tanto quanto a estatística: com OR = 8 cal, k = 1,10 / 1,04 / 0,96 / 0,90; com 12 cal, 0,98 / 0,95 / 0,89 / 0,84. Com qualquer dos três, k < 1 em Mach 2,0 e 2,5, mas com OR = 8 cal em Mach 2,0 só por cerca de dois desvios-padrão (0,96 ± 0,02); em Mach 1,2 e 1,5, o lado de 1 em que o k cai depende do OR.
- O k herda as células de XC decididas pelas tabelas de 1973. Nenhuma saiu do voo livre, então ele não é circular, mas também não mede o XC15 do listing, que não foi impresso.

**Ordem de grandeza dos desvios já medidos nesta família:** Magnus +0,3 a +0,5 (superestima), CNα +0,21 só no M-80 (o mais curto), Cmq 2,5× no transônico e 10 % no supersônico (superestima) e CPN certo até Mach 1,5 e 8 a 13 % atrás do medido em Mach 2,0 a 2,5 (k(M), com OR = 9,74 cal; na média das rodadas, 0,14 a 0,22 calibre atrás no M-80, no M-59 e no M-61 e −0,07 no M-62), este dependente do XC15 decidido pelas tabelas. Os três primeiros apontam o mesmo sentido (o SPIN-73 superestima); o do CPN não tem sinal único. A explicação pela escala — o SPIN-73 foi calibrado em projéteis de artilharia, bem maiores que a 7,62 — só se sustenta em parte: com dez grupos ([CORRECAO.md](CORRECAO.md)), a correção por escala é aceita no Cmq transônico e rejeitada no Cmq supersônico, no CNα acima do subsônico e no Magnus.

## Compêndio do Hitchcock (BRL 620) — `scripts/voo_livre/hitchcock/`

O AD-800 469 (Hitchcock, *Aerodynamic Data for Spinning Projectiles*, 1947/1952) é o compêndio que faltava: ~100 projéteis agrupados por calibre, cada um com esboço cotado em calibres, tabela de características físicas (peso, CG, momentos de inércia) e tabelas de K_M (momento), K_L (força de vento cruzado), K_H (amortecimento) e K_I, com a velocidade de cada série de tiros. É a variedade de formas que a família 7,62 não tem.

O PDF é um scan com camada de OCR que **não** capturou os números — só a prosa. As páginas são imagens CCITT G4 dentro do PDF, e `scripts/leitura/pagina_pdf.py` as extrai embrulhando o stream num TIFF, sem depender de poppler. A impressão é tipografada e bem legível, ao contrário da matricial do SPIN-73.

### Conversões (`conversoes.py`), verificadas e não supostas

| Grandeza | BRL | SPIN-73 |
|---|---|---|
| Arrasto | K_D | CX = (8/π)·K_D |
| Momento de tombamento | K_M | CMα = (8/π)·K_M |
| Força de vento cruzado | K_L | CNα = (8/π)·K_L + CX |
| Amortecimento | K_H | Cmq = −(16/π)·K_H |
| Posições | g, h da base | VCG = VL − g, CPN = VL − h |

As duas últimas são as que costumam dar errado. Foram conferidas numericamente no calibre 0.30 Ball M2 (`tests/test_cal030.py`):

- **K_M:** o CMα implicado pelo fator de estabilidade medido (S = 3,42), calculado com a fórmula de s_g do SPIN-73 e os momentos de inércia do próprio relatório, dá **1,286** contra **1,299** de (8/π)·0,51 — 1 % de diferença. Isso valida ao mesmo tempo a conversão e a fórmula de estabilidade reconstruída, contra uma fonte independente e 25 anos anterior.
- **K_H:** o Cmq reconstruído nessa geometria em Mach 2,49 é **−12,90** contra **−13,24** de −(16/π)·2,6 — 3 %. O fator 2 entre q·d/V e q·d/2V é necessário; sem ele sobraria quase o dobro.
- **K_L:** (8/π)·0,98 = 2,496 com CNα reconstruído de 2,918 implica CX = 0,42, e o gráfico de arrasto da mesma página dá CX ≈ 0,38.

Ou seja: no Mach 2,5 desse projétil, o Cmq do SPIN-73 erra 3 %. É coerente com o que a 7,62 mostrou (fator 0,90 em Mach 2 a 2,5) e reforça que o problema do Cmq está no transônico, não no supersônico.

### Fórmulas empíricas do próprio Hitchcock

A p. 11 do relatório traz os antecessores diretos das equações do SPIN-73, lineares nas mesmas variáveis geométricas (ângulo e comprimento do boattail, comprimento cilíndrico, ogiva, raio de ogiva) mas **sem dependência de Mach**:

    K_N = 0,020a − 0,748b + 0,1715c + 0,540d − 0,0266e
    h   = −0,0135a + 1,97b + 0,6276c + 0,4837d − 0,0233e

No Ball M2, a fórmula de h dá o centro de pressão a 0,06 calibre do valor implicado pelo experimento — o que também sustenta a leitura de XC que fizemos no baseline.

### Calibre 0.30 completo e validado (`dados_cal030.py`, `tests/test_cal030.py`)

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

**CMα contra o experimento** (`comparar_cma_cal030.py`, saída em `docs/resultados/cma_cal030.txt`). Com o XC15 de Mach 1,2 a 5 decidido pelas tabelas de 1973, o CPN reconstruído existe em toda a faixa, e o CMα do modelo, (VCG − CPN)·CNα, pode ser comparado com (8/π)·K_M. Hipóteses: DM = 0,12 (não cotado nos esboços; é a convenção das fontes de armas portáteis em `correcao/dados.py`), Mach impresso ou V/a com a = 1113 ft/s, a Frangible M22 com o contorno do Ball M2 (nota da p. 18) e, no Tracer M1, o CG médio, com que o relatório calcula o K_M aparente.

| Projétil | Mach | CMα modelo / medido | Leitura da linha |
|---|---|---|---|
| Frangible M22 | 1,23 | 0,986 | verificada |
| Tracer M1 | 2,27 | 1,054 (1,367 com o CG do projétil cheio) | verificada (K_M aparente) |
| Ball M2 | 2,31 | 1,197 | verificada |
| A.P. M2 | 2,47 | 0,658 (0,683 com o afinamento da base como boattail) | incerteza de temperatura |
| Ball M1 | 1,79 / 2,41 / 2,57 | 0,812 / 1,005 / 1,097 | inconsistente na fonte |

Nos três de base reta com leitura verificada, o modelo fica a −1 %, +5 % e +20 % do medido; o do Tracer M1 depende do CG adotado para o K_M aparente. O A.P. M2 fica um terço abaixo, e tratar o afinamento da base como boattail quase não muda isso. No Ball M1, de boattail, o medido cai de 3,158 para 2,445 entre Mach 1,79 e 2,57 e o modelo quase não varia (2,563 a 2,686), mas a fonte é inconsistente nesse projétil.

Além da leitura, pesam duas coisas. O DM suposto: com 0,05 e 0,20, a razão do Ball M2 vai de 1,104 a 1,304. E, entre Mach 2 e 3, o XC1 de Mach 2,5, decidido pelo modelo (lido 1,90, decidido 1,99): com o valor lido, as razões sobem para 1,324 no Ball M2, 1,130 no Tracer M1 e 0,730 no A.P. M2. O XC15 decidido só entra no Ball M1, o único com boattail; nos de base reta ele não tem peso, e a Frangible M22 (Mach 1,23) não usa nenhuma célula decidida. Nenhuma dessas células saiu do Hitchcock, então a comparação não é circular.

### Próximas fatias

Cada seção de calibre custa cerca de três páginas (esboços, características físicas, estabilidade e amortecimento). Prioridade: seções com **boattails** de dados consistentes, que é o que o calibre 0.30 deixou em aberto.

## Correção empírica com voo livre (`scripts/voo_livre/correcao/`)

Dez grupos de projéteis (7,62 NATO, 5,56 NATO em dois grupos, .50, 7,62 match, 30 mm, 155 mm M101 e M483A1, 175 mm T203 em modelo de 90 mm e 152 mm XM617), 1391 valores medidos na convenção do SPIN-73. A correção só usa o que o SPIN-73 não tem, a escala (número de Reynolds no CX0, log do diâmetro nos demais), e só entra o que a validação cruzada aninhada deixando um grupo de fora aceita. Resultado, em erro de predição nos grupos não vistos: CX0 corrigido nos três regimes (supersônico 6,6 % → 4,8 %, transônico 10,7 % → 8,2 %, subsônico 19,3 % → 15,1 %, melhorando 7 de 9 ou 10 grupos), CNα só no subsônico (13,2 % → 10,7 %, no limite da regra: o pior grupo fica 1,97 vez pior, com o limite em 2) e Cmq só no transônico (90 % → 72 %). O CNα transônico foi rejeitado por pouco (2,01), e CMα e Magnus não se deixam corrigir. O arrasto é a peça firme; `"voo_livre:CX0"` é a escolha conservadora. Detalhes em [CORRECAO.md](CORRECAO.md).
