"""Extracts one page of a scanned PDF as an image, without depending on poppler.

The pages of these DTIC reports are CCITT G4 images stored inside the PDF. Instead of
rendering the page, the stream is wrapped in a minimal TIFF header, which Pillow decodes
directly.

    python scripts/reading/pdf_page.py 25 out.png [pdf_path]

Without the third argument, it uses sources/BRL620_Hitchcock.pdf (see sources/README.md).

The number is the PDF page, not the printed one. In BRL 620 (AD-800 469, Hitchcock) the
printed page is the PDF page minus 5.
"""
import io, os, re, struct, sys, zlib
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_PDF = os.path.join(ROOT, "sources", "BRL620_Hitchcock.pdf")
PDF = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PDF
d = open(PDF, "rb").read()
objs = {int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", d, re.S)}

def refs(body, key):
    m = re.search(key + rb"\s+(\d+)\s+0\s+R", body)
    return int(m.group(1)) if m else None

pages = [n for n, c in sorted(objs.items()) if re.search(rb"/Type\s*/Page[^s]", c)]

def image(ipage):
    c = objs[pages[ipage - 1]]
    xo = refs(c, rb"/XObject")
    target = objs[xo]
    for m in re.finditer(rb"/(\w+)\s+(\d+)\s+0\s+R", target):
        o = objs[int(m.group(2))]
        if b"/Image" not in o:
            continue
        w = int(re.search(rb"/Width\s+(\d+)", o).group(1))
        h = int(re.search(rb"/Height\s+(\d+)", o).group(1))
        k = re.search(rb"/K\s+(-?\d+)", o)
        k = int(k.group(1)) if k else 0
        black1 = b"/BlackIs1 true" in o
        s = re.search(rb"stream\r?\n", o)
        data = o[s.end():o.rfind(b"endstream")]
        return w, h, k, black1, data
    return None

def tiff(w, h, k, black1, data):
    """Minimal one-strip TIFF with CCITT compression (G4 if k<0, otherwise G3)."""
    tags = [(256, 3, 1, w), (257, 3, 1, h), (258, 3, 1, 1), (259, 3, 1, 4 if k < 0 else 3),
            (262, 3, 1, 1 if black1 else 0), (273, 4, 1, 8 + 2 + 12 * 9 + 4),
            (277, 3, 1, 1), (278, 4, 1, h), (279, 4, 1, len(data))]
    out = io.BytesIO()
    out.write(b"II*\x00" + struct.pack("<I", 8))
    out.write(struct.pack("<H", len(tags)))
    for tag, kind, n, val in sorted(tags):
        out.write(struct.pack("<HHI", tag, kind, n))
        out.write(struct.pack("<I", val) if kind == 4 else struct.pack("<HH", val, 0))
    out.write(struct.pack("<I", 0))
    out.write(data)
    return out.getvalue()

if __name__ == "__main__":
    ipage, out_path = int(sys.argv[1]), sys.argv[2]
    w, h, k, black1, data = image(ipage)
    print(f"page {ipage}: {w}x{h} px, K={k}, BlackIs1={black1}, {len(data)} bytes")
    im = Image.open(io.BytesIO(tiff(w, h, k, black1, data)))
    im.load()
    im.convert("L").save(out_path)
    print("->", out_path)
