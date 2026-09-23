# python/

O programa reconstruído e seus testes. Visão geral e uso em [../README.pt-BR.md](../README.pt-BR.md) (em inglês: [../README.md](../README.md)).

## Programa: o pacote `spin73/`

Canônico (o programa de 1973):

- `spin73/nucleo.py` — as equações (seguindo o código Fortran onde ele foi transcrito), a análise de estabilidade, `tabela()`, `formatar()`, `avisos()` e o cartão de entrada `Projetil`.
- `spin73/dados/` — os blocos `DATA`, cada um com a leitura, as células decididas e a evidência (`xa_lidos.py` … `xf_lidos.py`); `__init__.py` monta o conjunto e registra a situação de cada bloco.

Adições opcionais (nenhuma é aplicada sem ser pedida):

- `spin73/convencoes.py` — conversões entre a convenção do relatório e a moderna.
- `spin73/unidades.py` — entradas em unidades métricas (mm, g, g·cm², °C, CG a partir da base).
- `spin73/massa.py` — estimativa de CG, massa e inércias que faltam no cartão.
- `spin73/correcoes/` — correções sobre a saída (interface, registro e a correção de voo livre).

Interfaces:

- `spin73/aero.py` — `Aerodinamica`, a interface para simuladores.
- `spin73/cli.py` — linha de comando (`python -m spin73`).
- `exemplos/m437.txt` — arquivo de entrada do caso de validação; `exemplos/m855_metrico.txt`, um cartão em unidades métricas com a estimativa de massa.

Os antigos `spin73.py`, `dados_spin73.py`, `convencoes.py` e `reconstrucao_*/x?_lidos.py` agora só redirecionam para o pacote, para que os scripts e testes de cada etapa continuem funcionando. Uso como biblioteca em [../docs/BIBLIOTECA.md](../docs/BIBLIOTECA.md).

## Blocos DATA reconstruídos

Cada diretório guarda a leitura do scan, as células decididas (com a evidência) e o teste contra as tabelas de 1973.

| Diretório | Bloco | Coluna |
|---|---|---|
| `reconstrucao_A/` | XA1..XA15 | CX |
| `reconstrucao_B/` | XB1..XB9 | CNα |
| `reconstrucao_C/` | XC1..XC17 | CPN, CMα |
| `reconstrucao_D/` | XD1..XD4 | CX2 |
| `reconstrucao_F/` | XE1..XE4, XF1..XF9, XG1 | Magnus, Cmq, Clp |

O XE5 (termo de corpo longo do Magnus) está em `spin73/dados/__init__.py`. Os blocos lidos ficam em `spin73/dados/`; cada diretório `reconstrucao_*` guarda os testes e a análise que os decidiram.

## Tabelas de 1973 transcritas

- `m437_tabela.csv` — a tabela completa do 175 mm M437 (p. 65).
- `tabelas/` — as 13 tabelas de saída do relatório, uma por arquivo, com a entrada impressa, as entradas decididas e as células desambiguadas por identidade ou ilegíveis. `tabelas/leituras/` guarda a leitura bruta com os glifos ambíguos marcados; `resolver_glifos.py` gera o CSV a partir dela e `verificar_identidades.py` confere a tabela pronta sem usar o modelo. Leitura com `tabelas_impressas.py`; teste em `test_tabelas_impressas.py`.
- `circularidade.py` — que células de cada tabela ajudaram a decidir algum `DATA` ou entrada (e por isso não validam nada ali).
- `reconstrucao_B/dados_cna.py` — a coluna CNA de 10 tabelas.
- `reconstrucao_*/dados_*.py` — colunas do 5"/38 (p. 53) usadas como segunda geometria.
- `geometria_decidida.csv`, `cabecalhos_tabelas.csv` — a geometria das 14 tabelas.
- `magnus_clp.py` — colunas de Magnus de 6 tabelas e a identificação original dos E.

## Testes

```
python -m pytest -q .
```

`test_modelo_completo.py` roda o programa inteiro a partir da geometria contra a tabela do M437; cada célula que não fecha está listada com o motivo, e as células decididas pela própria tabela ficam fora da validação. `test_biblioteca.py` e `test_massa.py` cobrem as interfaces e as adições opcionais.

## Outros

- `experimental/` — o que compara o SPIN-73 com medições, separado da reconstrução: `benchmarks/` (voo livre), `correcao/` (ajuste da correção de voo livre), `massa/` (validação da estimativa de massa), `hitchcock/` (compêndio BRL 620) e a recalibração com a 7,62 NATO (BRL MR 1833).
- `relatorio/` — relatório HTML de comparação (fase anterior; não inclui os blocos lidos depois).
