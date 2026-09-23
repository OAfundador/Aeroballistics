# Fontes

- `jp2/` — scan em alta resolução do relatório (DTIC AD0915628, Distribution A): 96 páginas JP2 de ~2600×3400 px, `DTIC_AD0915628_0000.jp2` a `_0095.jp2`. Índice do arquivo = página impressa + 3. Extraído de `DTIC_AD0915628_jp2.zip`.
- `cache/` — páginas já giradas e com autocontraste, geradas por `ferramentas/recorte.py`. Pode ser apagado.

- `BRL620_Hitchcock.pdf` — Hitchcock, *Aerodynamic Data for Spinning Projectiles*, BRL Report 620 (AD-800 469), usado em `python/experimental/hitchcock/`. Páginas extraídas com `ferramentas/pagina_pdf.py`.
- `MR1833_Piddington.pdf` — BRL MR 1833 (AD815788), família 7,62 NATO, usado em `python/experimental/`.

Nenhum desses arquivos é versionado (ver `.gitignore`): são grandes e estão disponíveis na DTIC.
