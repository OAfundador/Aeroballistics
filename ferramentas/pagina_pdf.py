"""Extrai uma página de PDF escaneado como imagem, sem depender do poppler.

As páginas destes relatórios da DTIC são imagens CCITT G4 guardadas dentro do PDF. Em
vez de renderizar a página, embrulha-se o stream num cabeçalho TIFF mínimo, que o
Pillow decodifica direto.

    python ferramentas/pagina_pdf.py 25 saida.png [caminho_do_pdf]

O número é a página do PDF, não a impressa. No BRL 620 (AD-800 469, Hitchcock) a
página impressa é a do PDF menos 5.
"""
import io, re, struct, sys, zlib
from PIL import Image

PDF_PADRAO = ("C:/Users/DELL/Downloads/"
              "pdfcoffee.com_aerodynamic-data-for-spinning-projectiles-pdf-pdf-free.pdf")
PDF = sys.argv[3] if len(sys.argv) > 3 else PDF_PADRAO
d = open(PDF, "rb").read()
objs = {int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", d, re.S)}

def refs(corpo, chave):
    m = re.search(chave + rb"\s+(\d+)\s+0\s+R", corpo)
    return int(m.group(1)) if m else None

paginas = [n for n, c in sorted(objs.items()) if re.search(rb"/Type\s*/Page[^s]", c)]

def imagem(ipag):
    c = objs[paginas[ipag - 1]]
    xo = refs(c, rb"/XObject")
    alvo = objs[xo]
    for m in re.finditer(rb"/(\w+)\s+(\d+)\s+0\s+R", alvo):
        o = objs[int(m.group(2))]
        if b"/Image" not in o:
            continue
        w = int(re.search(rb"/Width\s+(\d+)", o).group(1))
        h = int(re.search(rb"/Height\s+(\d+)", o).group(1))
        k = re.search(rb"/K\s+(-?\d+)", o)
        k = int(k.group(1)) if k else 0
        preto1 = b"/BlackIs1 true" in o
        s = re.search(rb"stream\r?\n", o)
        dados = o[s.end():o.rfind(b"endstream")]
        return w, h, k, preto1, dados
    return None

def tiff(w, h, k, preto1, dados):
    """TIFF minimo de uma tira com compressao CCITT (G4 se k<0, senao G3)."""
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

if __name__ == "__main__":
    ipag, saida = int(sys.argv[1]), sys.argv[2]
    w, h, k, preto1, dados = imagem(ipag)
    print(f"pagina {ipag}: {w}x{h} px, K={k}, BlackIs1={preto1}, {len(dados)} bytes")
    im = Image.open(io.BytesIO(tiff(w, h, k, preto1, dados)))
    im.load()
    im.convert("L").save(saida)
    print("->", saida)
