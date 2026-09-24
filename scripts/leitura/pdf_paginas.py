"""Página de PDF escaneado -> imagem, sem poppler nem leitor de PDF.

Lê os três formatos que aparecem nos relatórios da DTIC usados neste projeto:

  - página inteira em CCITT G4 (a maioria dos scans antigos; o mesmo de pagina_pdf.py);
  - página em JPEG, com ou sem compressão Flate por cima;
  - página "MRC": fundo em JPEG de baixa resolução + máscara de texto em JBIG2, composta aqui
    na resolução da máscara (o texto fica nítido, os desenhos vêm do fundo).

    python scripts/leitura/pdf_paginas.py <pdf> <página> <saída.png> [giro]
    python scripts/leitura/pdf_paginas.py <pdf> folha <inicial> <final> <saída.png>

<página> é a do PDF (1 = primeira), não a impressa. [giro] em graus, anti-horário (90, -90, 180).
A folha de contato numera cada miniatura com a página do PDF. A decodificação JBIG2 é Python
puro: 1 a 30 s por página.
"""
import io
import os
import re
import struct
import sys
import zlib

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jbig2                                            # noqa: E402


def carregar(pdf):
    """(objetos do PDF por número, lista das páginas na ordem da árvore /Pages)."""
    d = open(pdf, "rb").read()
    objs = {int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", d, re.S)}

    def filhos(n):
        c = objs[n]
        if re.search(rb"/Type\s*/Page[^s]", c):
            return [n]
        k = re.search(rb"/Kids\s*\[(.*?)\]", c, re.S)
        out = []
        for m in re.finditer(rb"(\d+)\s+0\s+R", k.group(1)):
            out += filhos(int(m.group(1)))
        return out

    raiz = [n for n, c in objs.items() if re.search(rb"/Type\s*/Pages", c) and b"/Parent" not in c]
    pags = filhos(raiz[0]) if raiz else [n for n, c in sorted(objs.items())
                                         if re.search(rb"/Type\s*/Page[^s]", c)]
    return objs, pags


def _tiff_ccitt(w, h, k, preto1, dados):
    tags = [(256, 3, 1, w), (257, 3, 1, h), (258, 3, 1, 1), (259, 3, 1, 4 if k < 0 else 3),
            (262, 3, 1, 1 if preto1 else 0), (273, 4, 1, 8 + 2 + 12 * 9 + 4),
            (277, 3, 1, 1), (278, 4, 1, h), (279, 4, 1, len(dados))]
    out = io.BytesIO()
    out.write(b"II*\x00" + struct.pack("<I", 8))
    out.write(struct.pack("<H", len(tags)))
    for tag, tipo, n, val in sorted(tags):
        out.write(struct.pack("<HHI", tag, tipo, n))
        out.write(struct.pack("<I", val) if tipo == 4 else struct.pack("<HH", val, 0))
    out.write(struct.pack("<I", 0))
    out.write(dados)
    return out.getvalue()


def _stream(o):
    s = re.search(rb"stream\r?\n", o)
    return o[s.end():o.rfind(b"endstream")]


def _imagem_do_objeto(o):
    dados = _stream(o)
    w = int(re.search(rb"/Width\s+(\d+)", o).group(1))
    h = int(re.search(rb"/Height\s+(\d+)", o).group(1))
    if b"CCITT" in o:
        k = re.search(rb"/K\s+(-?\d+)", o)
        return Image.open(io.BytesIO(_tiff_ccitt(w, h, int(k.group(1)) if k else 0,
                                                 b"/BlackIs1 true" in o, dados)))
    if b"JBIG2" in o:
        return jbig2.para_imagem(jbig2.decodificar(dados))
    if b"FlateDecode" in o:
        dados = zlib.decompress(dados)
    if b"DCTDecode" in o or dados[:2] == b"\xff\xd8":
        return Image.open(io.BytesIO(dados))
    bpc = int(re.search(rb"/BitsPerComponent\s+(\d+)", o).group(1))
    modo = "RGB" if b"DeviceRGB" in o else ("1" if bpc == 1 else "L")
    return Image.frombytes(modo, (w, h), dados)


def _xobjetos(objs, pag):
    c = objs[pag]
    m = re.search(rb"/XObject\s*<<(.*?)>>", c, re.S)
    if not m:
        r = re.search(rb"/XObject\s+(\d+)\s+0\s+R", c)
        if not r:
            return []
        corpo = objs[int(r.group(1))]
    else:
        corpo = m.group(1)
    return [objs[int(mm.group(2))] for mm in re.finditer(rb"/(\w+)\s+(\d+)\s+0\s+R", corpo)
            if b"/Image" in objs[int(mm.group(2))]]


def pagina(pdf, i):
    """Imagem (tons de cinza) da página i do PDF, ou None se ela não tiver imagem."""
    objs, pags = carregar(pdf)
    imagens = _xobjetos(objs, pags[i - 1])
    fundo, masc = None, None
    for o in imagens:
        mk = re.search(rb"/Mask\s+(\d+)\s+0\s+R", o)
        if mk:                                           # MRC: o texto está na máscara
            masc = _imagem_do_objeto(objs[int(mk.group(1))]).convert("L")
        else:
            im = _imagem_do_objeto(o).convert("L")
            if fundo is None or im.size[0] * im.size[1] > fundo.size[0] * fundo.size[1]:
                fundo = im
    if masc is None:
        return fundo
    if fundo is None:
        return masc
    return ImageChops.darker(fundo.resize(masc.size), masc)


def folha(pdf, ini, fim, saida, larg=360, alt=470, colunas=6):
    ims = []
    for i in range(ini, fim + 1):
        try:
            im = pagina(pdf, i)
        except (IndexError, NotImplementedError) as e:
            print(f"p. {i}: {e}")
            im = None
        im = im or Image.new("L", (larg, alt), 200)
        im.thumbnail((larg, alt))
        ims.append((i, im))
    linhas = (len(ims) + colunas - 1) // colunas
    out = Image.new("L", (colunas * larg, linhas * alt), 255)
    dr = ImageDraw.Draw(out)
    for k, (i, im) in enumerate(ims):
        x, y = (k % colunas) * larg, (k // colunas) * alt
        out.paste(im, (x, y))
        dr.text((x + 5, y + 5), str(i), fill=0)
    out.save(saida)


if __name__ == "__main__":
    if len(sys.argv) >= 6 and sys.argv[2] == "folha":
        folha(sys.argv[1], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) >= 4:
        im = pagina(sys.argv[1], int(sys.argv[2]))
        if len(sys.argv) > 4:
            im = im.rotate(float(sys.argv[4]), expand=True)
        im.save(sys.argv[3])
        print(sys.argv[3], im.size)
    else:
        print(__doc__)
