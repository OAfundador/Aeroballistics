# python/

O programa reconstruído e seus testes. Visão geral e uso em [../README.md](../README.md).

## Programa

- `spin73.py` — as equações (seguindo o código Fortran onde ele foi transcrito), a análise de estabilidade, `tabela()`, `formatar()`, `avisos()` e a linha de comando.
- `dados_spin73.py` — reúne todos os blocos `DATA` e registra a situação de cada um.
- `exemplos/m437.txt` — arquivo de entrada do caso de validação.

## Blocos DATA reconstruídos

Cada diretório guarda a leitura do scan, as células decididas (com a evidência) e o teste contra as tabelas de 1973.

| Diretório | Bloco | Coluna |
|---|---|---|
| `reconstrucao_A/` | XA1..XA15 | CX |
| `reconstrucao_B/` | XB1..XB9 | CNα |
| `reconstrucao_C/` | XC1..XC17 | CPN, CMα |
| `reconstrucao_D/` | XD1..XD4 | CX2 |
| `reconstrucao_F/` | XE1..XE4, XF1..XF9, XG1 | Magnus, Cmq, Clp |

O XE5 (termo de corpo longo do Magnus) está em `dados_spin73.py`.

## Tabelas de 1973 transcritas

- `m437_tabela.csv` — a tabela completa do 175 mm M437 (p. 65).
- `reconstrucao_B/dados_cna.py` — a coluna CNA de 10 tabelas.
- `reconstrucao_*/dados_*.py` — colunas do 5"/38 (p. 53) usadas como segunda geometria.
- `geometria_decidida.csv`, `cabecalhos_tabelas.csv` — a geometria das 14 tabelas.
- `magnus_clp.py` — colunas de Magnus de 6 tabelas e a identificação original dos E.

## Testes

```
python -m pytest -q .
```

`test_modelo_completo.py` roda o programa inteiro a partir da geometria contra a tabela do M437; cada célula que não fecha está listada com o motivo, e as células decididas pela própria tabela ficam fora da validação.

## Outros

- `experimental/` — recalibração com dados de voo livre (separada da reconstrução).
- `relatorio/` — relatório HTML de comparação (fase anterior; não inclui os blocos lidos depois).
