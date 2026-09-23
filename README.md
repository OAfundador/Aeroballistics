# SPIN-73 — reconstrução didática

Reconstrução do programa **SPIN-73** (R. H. Whyte, Picatinny Arsenal TR 4588, 1973; DTIC AD0915628, Distribution A), que estima coeficientes aerodinâmicos de projéteis estabilizados por rotação a partir da geometria.

Duas fases, sempre separadas:

1. **Reconstrução fiel (baseline):** reproduzir as 14 tabelas de saída impressas em 1973 dentro do arredondamento da impressão. Bugs e termos não documentados do original são mantidos e documentados.
2. **Recalibração:** mesmas equações, constantes reajustadas a dados de voo livre. Fica em `python/experimental/` e nunca altera o baseline.

## Estrutura

| Diretório | Conteúdo |
|---|---|
| `docs/` | `CONTEXTO_CLAUDE_CODE.md` (resumo do projeto e das tarefas), `NOTAS_TRANSCRICAO.md` (decisões de leitura), `AVALIACAO_FASE8.md` (conferência do estado na fase 8) |
| `python/` | Reconstrução em Python e testes (`python -m pytest -q python`) |
| `original/` | Transcrição literal do listing Fortran (pp. 79–86) |
| `fortran/` | Versão compilável do listing |
| `julia/` | Port futuro |
| `validation/` | Comparações consolidadas com as tabelas de 1973 |
| `ferramentas/` | `recorte.py`: recortes girados e com zoom do scan, por número de página impressa |
| `fontes/` | Scan JP2 do relatório (não versionado; ver `fontes/LEIAME.md`) |
| `trabalho/` | Área temporária das tarefas A–F; o conteúdo é consolidado nos diretórios acima |

## Rodar

```
pip install numpy pytest pillow matplotlib
python -m pytest -q python
python ferramentas/recorte.py 80 --visao --saida recortes/p80.png
```

## Convenções

- Separar sempre o que é **verificado**, **decidido pelo modelo** e **pendente**. Dígito duvidoso fica marcado; nenhum dígito é inventado.
- Valores decididos pelo modelo ficam fora da validação que os decidiu.
- Tolerância padrão: ±0,0015 em colunas de 3 casas; ±1 no último dígito impresso nas demais.
- Idioma dos arquivos e comentários: português.
