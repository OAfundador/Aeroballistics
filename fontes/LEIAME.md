# Fontes

- `jp2/` — scan em alta resolução do relatório (DTIC AD0915628, Distribution A): 96 páginas JP2 de ~2600×3400 px, `DTIC_AD0915628_0000.jp2` a `_0095.jp2`. Índice do arquivo = página impressa + 3. Extraído de `DTIC_AD0915628_jp2.zip`.
- `cache/` — páginas já giradas e com autocontraste, geradas por `ferramentas/recorte.py`. Pode ser apagado.

- `BRL620_Hitchcock.pdf` — Hitchcock, *Aerodynamic Data for Spinning Projectiles*, BRL Report 620 (AD-800 469), usado em `python/experimental/hitchcock/` e nas fórmulas de inércia de `spin73.massa` (p. 9). Páginas extraídas com `ferramentas/pagina_pdf.py`.
- `MR1833_Piddington.pdf` — BRL MR 1833 (AD815788), família 7,62 NATO, usado em `python/experimental/`.

- Benchmarks de voo livre (archive.org, DTIC, todos com liberação pública), usados em `python/experimental/benchmarks/`:
  - `DTIC_AD0454925.pdf` — Karpov et al., 155 mm M101 (BRL MR 1582, 1964)
  - `DTIC_ADA235620.pdf` — Whyte, 155 mm M483A1 (BRL-CR-659, 1991)
  - `DTIC_ADA219106.pdf` — McCoy, .50 M33/M8/M20 (BRL-MR-3810, 1990)
  - `DTIC_ADA162133.pdf` — McCoy, 5,56 mm NATO (BRL-MR-3476, out. 1985)
  - `DTIC_ADA205633.pdf` — McCoy, 7,62 mm match: M118, 190 gr e 168 gr Sierra (BRL-MR-3733, dez. 1988)
  - `DTIC_ADA121258.pdf` — McCoy, 30 mm XM788E1 e XM789 (ARBRL-TR-03432, out. 1982)
  - `DTIC_ADA086096.pdf` — McCoy, 30 mm XM788 (ARBRL-MR-03019, maio 1980) *
  - `DTIC_AD0086528.pdf` — Karpov, Skeggs e Hull, 175 mm T203 e base reta, modelos de 90 mm (BRL MR 956, dez. 1955) *
  - `DTIC_AD0857512.pdf` — Brandon, 152 mm XM617 (BRL MR 1998, jul. 1969) *
  - Baixados e **não usados**:
    - `DTIC_ADA229713.pdf` — McCoy, .22 LR match (BRL-MR-3877, 1990): base com degrau ("heel") e nariz arredondado, fora do que a geometria do SPIN-73 descreve.
    - `DTIC_AD0078604.pdf` — Roecker, 105 mm M1 (BRL MR 929, 1955): o relatório só dá comprimento (≈4,7 cal) e boattail (0,5 cal, 9°); ogiva e raio não estão cotados, e a p. 47 do SPIN-73, que traria o cartão do M1, repete a p. 44 no scan.
    - `DTIC_AD0729238.pdf` — Regan e Schermerhorn, 20 mm Navy GP (NOLTR 71-95, 1971): só gráficos, sem tabela rodada a rodada.

  \* PDFs "MRC" da DTIC: o texto fica numa máscara JBIG2, que o Pillow não lê e o leitor de PDF do Windows também não. Foram lidos com `ferramentas/pdf_paginas.py`, que usa o decodificador JBIG2 em Python puro de `ferramentas/jbig2.py` (qualquer leitor de PDF baseado em PDFium ou pdf.js mostra as mesmas páginas).

Nenhum desses arquivos é versionado (ver `.gitignore`): são grandes e estão disponíveis na DTIC.
