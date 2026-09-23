# SPIN-73 reconstruído

Reconstrução, em Python, do programa **SPIN-73** (R. H. Whyte, *SPIN-73, an Updated Version of the SPINNER Computer Program*, Picatinny Arsenal TR 4588, 1973; DTIC AD0915628, Distribution A — aprovado para divulgação pública). O programa estima os coeficientes aerodinâmicos de um projétil estabilizado por rotação a partir da geometria, em 17 números de Mach (0,01 a 5), e faz a análise de estabilidade.

O código-fonte original só existe como listing Fortran impresso num relatório escaneado. Esta reconstrução foi feita lendo o scan — as equações, os blocos `DATA` com as constantes empíricas e o próprio código — e conferindo cada leitura contra as tabelas de saída que o programa imprimiu em 1973.

## Situação

**O programa reconstruído produz todas as 28 colunas que o original imprime.** No caso de validação do relatório, o 175 mm M437, partindo só da geometria:

| Bloco | Colunas | Reproduz a tabela de 1973 |
|---|---|---|
| Força axial | CX | 17 de 17 Mach (e 17 de 17 no 5"/38) |
| Força axial de guinada | CX2 | 12 de 17 (2 células ilegíveis no scan; 3 com resíduo de 0,007 a 0,02) |
| Força normal | CNA | 15 de 17 |
| Magnus | CYPA, CNPA, CPF1, CPF5, CNPA5, CNPA3, CNPA5P | 16 ou 17 de 17 |
| Amortecimentos | CMQ, CLP | 17 de 17 |
| Centro de pressão | CPN, CMA | teste independente em só 4 Mach no M437; ver a terceira tabela abaixo |
| Estabilidade | GYRO, SBAR, RECIP, SPIN, W1, W2, λ, DELT, DISP | 15 a 17 de 17; as que dependem do CMα só são independentes nos mesmos 5 Mach |

O centro de pressão do M437 fecha em 14 de 17 Mach, mas em 13 deles o resultado é **circular**: o listing impresso perdeu um cartão de `DATA` (a continuação do XC15), e a própria tabela do M437 foi usada para recuperá-lo. Nesses Mach, ela não pode mais servir de teste. A conferência independente vem de mais duas tabelas com boattail: o 5"/38 (p. 53) e o **105 mm XM380E5 (p. 50), transcrito por inteiro e que não decidiu nenhum `DATA`**. O programa reproduz 16 dos 17 Mach do CPN dele, e 98 % de todas as suas células (ver `python/tabelas/`).

Tolerância: ±0,0015 nas colunas de 3 casas (o arredondamento da impressão); ±1 no último dígito nas demais. `python -m pytest -q python` roda 196 testes.

**Tamanho do erro** em todas as tabelas de 1973 transcritas (1235 células, 985 independentes): 88 % indistinguíveis do original, 94 % no critério, erro mediano de 0,26 unidade na última casa impressa. Detalhe por coluna em [validation/LEIAME.md](validation/LEIAME.md).

## Uso rápido

```
pip install -r requirements.txt
python python/spin73.py --exemplo
```

Para um projétil seu, direto na linha de comando (comprimentos em calibres, diâmetro em polegadas, inércias em lb·in², peso em lb, passo em calibres por volta):

```
python python/spin73.py --VL 5.0 --VN 2.0 --VB 0.4 --VCG 3.0 --OR 8 --DIA 1.0 --IX 0.5 --IY 4.0 --WGT 0.5 --TWIST 25 --csv saida.csv
```

ou num arquivo `CHAVE = valor` (modelo em [python/exemplos/m437.txt](python/exemplos/m437.txt)):

```
python python/spin73.py --entrada meu_projetil.txt
```

Em Python:

```python
import spin73 as s
p = s.Projetil(VL=5.0, VN=2.0, VB=0.4, VCG=3.0, OR=8.0)
t = s.tabela(p)            # dicionário: uma array de 17 valores por coluna
print(s.formatar(t))
print(s.avisos(p))         # limitações que afetam ESTA geometria
```

Sem diâmetro, inércias, peso e passo de raia, o programa calcula só os coeficientes aerodinâmicos, como o original.

## O que a reconstrução revelou

Onde o texto do relatório e o código divergem, vale o código — foi ele que gerou as tabelas. Divergências e termos não documentados encontrados:

- **Sinal trocado no texto** nas taxas de amortecimento λ (p. 18): o texto imprime −CNα(1 ± 1/σ); o código e as tabelas usam −CNα(1 ∓ 1/σ).
- **Constante do fator giroscópico**: o código usa 1352,4 onde a física com g = 32,174 dá 1349,8 (+0,19 %).
- **Termos de corpo longo** não documentados, ativos quando o projétil passa de 6 calibres: XE5 no Magnus e XF9 no amortecimento.
- **A13, A14 e A15** no arrasto: o termo de ogiva longa tem três trechos (quebras em 3,48 e 3,97 calibres); o texto só descreve o primeiro.
- **Descarte do boattail** no centro de pressão quando o momento do boattail sai positivo.
- **CNPA3 e CNPA5**: os "coeficientes do polinômio de Magnus" não usam o valor calculado a 2°; o programa soma uma constante fixa e as duas colunas obedecem a CNPA3 + 0,1·CNPA5 = 3,75 para qualquer projétil. Defeito do original, reproduzido.
- **Três cartões `DATA` faltando no listing impresso** (continuação do XC15, primeiro cartão do XE5 e segundo cartão do XF7), cada um substituído por uma cópia de um cartão vizinho. Foram recuperados pelas tabelas de saída. O do XF7 explicava o Cmq de Mach 1,1 que não fechava.

Detalhes, com a evidência de cada leitura, em [docs/NOTAS_TRANSCRICAO.md](docs/NOTAS_TRANSCRICAO.md).

## Limitações conhecidas

O programa imprime avisos específicos para cada geometria (`s.avisos(p)`). Os principais:

- **Centro de pressão de Mach 1,2 a 5**: o cartão do XC15 não foi impresso e foi recuperado pelas tabelas. O XM380E5 confere em todos esses Mach, mas o 5"/38 fica 0,004 a 0,009 calibre fora em Mach 1,75 e de 2,5 a 5. Em Mach 0,6 resta um resíduo de 0,002 a 0,004 calibre. As colunas de estabilidade herdam essas incertezas, porque dependem do CMα.
- **Ogiva maior que 3 calibres, boattail maior que 1 calibre**: ramos do código lidos, mas sem nenhuma tabela de 1973 que os valide.

## Como cada número foi validado

Cada valor lido no scan é classificado como **verificado** (leitura clara, ou confirmada por uma identidade independente), **decidido pelo modelo** (escolhido porque reproduz as tabelas) ou **pendente**. Um valor decidido por uma tabela nunca é usado para validar a si mesmo: os testes separam explicitamente o que é verificação independente do que é circular. A impressão matricial confunde pares de dígitos (6/8, 1/3, 2/5, 0/6, 4/9…); toda leitura ambígua foi decidida por uma identidade que não dependia dela, e está registrada com a evidência.

## Estrutura

| Diretório | Conteúdo |
|---|---|
| `python/` | O programa (`spin73.py`), os blocos `DATA` (`dados_spin73.py` e `reconstrucao_*/`) e os testes |
| `python/tabelas/` | Tabelas de saída de 1973 transcritas por inteiro, com a entrada impressa |
| `python/experimental/` | Recalibração com dados de voo livre (BRL MR 1833, 7,62 NATO; compêndio de Hitchcock, BRL 620) — **separada** da reconstrução |
| `original/` | Transcrição literal do listing Fortran (parcial: pp. 84–86) |
| `validation/` | Comparação do erro contra todas as tabelas de 1973 transcritas |
| `docs/` | Notas de transcrição: cada leitura do scan, com a evidência que a decidiu |
| `ferramentas/` | Leitura do scan: recortes girados e com zoom; extração de páginas de PDF escaneado |
| `fontes/` | O scan do relatório (não versionado; ver `fontes/LEIAME.md`) |

## Recalibração

A reconstrução reproduz o SPIN-73 como ele era, erros incluídos. Contra dados de voo livre da família 7,62 NATO, o modelo de 1973 superestima o Magnus (+0,3 a +0,5) e o amortecimento Cmq (2,5 vezes no transônico, 10 % no supersônico). Ajustes a dados experimentais ficam em `python/experimental/` e nunca alteram o programa reconstruído.

## Licença

Código sob a licença MIT (ver [LICENSE](LICENSE)). O relatório original é de domínio público (Distribution A).

## Fonte

Whyte, R. H. *SPIN-73, an Updated Version of the SPINNER Computer Program*. Technical Report 4588, Picatinny Arsenal, Dover, NJ, novembro de 1973. DTIC AD0915628. Distribution A: approved for public release.
