# SPIN-73 — reconstrução didática (fase 1: equações do relatório)

Reimplementação em Python do SPIN-73 (R. H. Whyte, Picatinny Arsenal TR 4588, 1973; DTIC AD0915628, Distribution A). O programa estima coeficientes aerodinâmicos de projéteis estabilizados por rotação a partir da geometria.

## Arquivos

- `spin73.py` — atmosfera do listing, as equações empíricas das pp. 13–17 e a análise de estabilidade das pp. 17–18.
- `magnus_clp.py` / `test_magnus.py` — identificação de E1, E2, E4 e G1 pelas tabelas, com teste de previsão em outros projéteis.
- `cabecalhos_tabelas.csv` — geometria das 14 tabelas, com grau de confiança.
- `reconstrucao_B/` — XB1..XB9 lidos dos DATA, CNα reconstruído, diagnóstico por célula e testes.
- `reconstrucao_F/` — XE, XF1..XF9 e XG1 lidos dos DATA, Cmq reconstruído com o termo F9, XC1..XC5 (parcial).
- `geometria_decidida.csv` — geometria das 14 tabelas, decidida pelas colunas de Magnus.
- `experimental/` — dados de voo livre (MR 1833) e recalibração por MMQ.
- `relatorio/` — relatório HTML de comparação com as tabelas de 1973.
- `m437_tabela.csv` — transcrição da Tabela 14 (175 mm M437), o caso de validação.
- `test_m437.py` — testes com pytest.
- `../docs/NOTAS_TRANSCRICAO.md` — leituras decididas, divergências entre o texto e as tabelas, e pendências.

## Rodar

```
pip install numpy pytest
python spin73.py                 # compara estabilidade calculada x tabela
python -m pytest -v test_m437.py
```

## Estado

| Parte | Situação |
|---|---|
| Análise de estabilidade (sg, sd, 1/(sd(2−sd)), spin, ω₁,₂, λ₁,₂ a 1° e 5°) | **Validada** contra a Tabela 14, 15 linhas de Mach |
| Estrutura das equações empíricas (CX, CNα, CMα, CPN, CX2, Magnus, Cmq, Clp) | Implementada; só as identidades algébricas são testadas |
| Magnus (E1, E2, E4) e Clp (G1) | **Identificados** no M437; prevêem 5"/38 e M101 a ±0,001 |
| CNα (B1..B9) | **Reconstruído** dos DATA XB: 78 % das células de 10 tabelas no arredondamento (`reconstrucao_B/`) |
| Demais coeficientes (a, C, D, E3, F, e os não documentados A14, A15, B10, F9) | Pendentes; valores estão nos DATA, pp. 79–81 |
| DELT, DISP | Não implementados |

Erros máximos nas linhas validadas: sd < 0,0014; λ < 1×10⁻⁶ 1/ft; spin < 0,1 rad/s; sg com viés sistemático de −0,17 % (item A1 das notas).

Achado principal até aqui: a fórmula das taxas de amortecimento impressa no texto tem um sinal trocado no termo de C_Nα. As tabelas de 1973 foram geradas com o sinal fisicamente correto (item E1).
