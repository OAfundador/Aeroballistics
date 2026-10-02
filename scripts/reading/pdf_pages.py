"""Scanned PDF page -> image, with no poppler and no PDF reader.

Reads the three formats that appear in the DTIC reports used in this project:

  - whole page in CCITT G4 (most of the old scans; the same as pdf_page.py);
  - page in JPEG, with or without Flate compression on top;
  - "MRC" page: low-resolution JPEG background + text mask in JBIG2, composed here at the
    resolution of the mask (the text is sharp, the drawings come from the background).

    python scripts/reading/pdf_pages.py <pdf> <page> <out.png> [rotation]
    python scripts/reading/pdf_pages.py <pdf> sheet <first> <last> <out.png>

<page> is the PDF page (1 = first), not the printed one. [rotation] in degrees,
counterclockwise (90, -90, 180). The contact sheet labels each thumbnail with its PDF page. The
JBIG2 decoding is pure Python: 1 to 30 s per page.
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


def load(pdf):
    """(PDF objects by number, list of the pages in the order of the /Pages tree)."""
    d = open(pdf, "rb").read()
    objs = {int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", d, re.S)}

    def children(n):
        c = objs[n]
        if re.search(rb"/Type\s*/Page[^s]", c):
            return [n]
        k = re.search(rb"/Kids\s*\[(.*?)\]", c, re.S)
        out = []
        for m in re.finditer(rb"(\d+)\s+0\s+R", k.group(1)):
            out += children(int(m.group(1)))
        return out

    root = [n for n, c in objs.items() if re.search(rb"/Type\s*/Pages", c) and b"/Parent" not in c]
    pages = children(root[0]) if root else [n for n, c in sorted(objs.items())
                                            if re.search(rb"/Type\s*/Page[^s]", c)]
    return objs, pages


def _tiff_ccitt(w, h, k, black1, data):
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


def _stream(o):
    s = re.search(rb"stream\r?\n", o)
    return o[s.end():o.rfind(b"endstream")]


def _object_image(o):
    data = _stream(o)
    w = int(re.search(rb"/Width\s+(\d+)", o).group(1))
    h = int(re.search(rb"/Height\s+(\d+)", o).group(1))
    if b"CCITT" in o:
        k = re.search(rb"/K\s+(-?\d+)", o)
        return Image.open(io.BytesIO(_tiff_ccitt(w, h, int(k.group(1)) if k else 0,
                                                 b"/BlackIs1 true" in o, data)))
    if b"JBIG2" in o:
        return jbig2.to_image(jbig2.decode(data))
    if b"FlateDecode" in o:
        data = zlib.decompress(data)
    if b"DCTDecode" in o or data[:2] == b"\xff\xd8":
        return Image.open(io.BytesIO(data))
    bpc = int(re.search(rb"/BitsPerComponent\s+(\d+)", o).group(1))
    mode = "RGB" if b"DeviceRGB" in o else ("1" if bpc == 1 else "L")
    return Image.frombytes(mode, (w, h), data)


def _xobjects(objs, page):
    c = objs[page]
    m = re.search(rb"/XObject\s*<<(.*?)>>", c, re.S)
    if not m:
        r = re.search(rb"/XObject\s+(\d+)\s+0\s+R", c)
        if not r:
            return []
        body = objs[int(r.group(1))]
    else:
        body = m.group(1)
    return [objs[int(mm.group(2))] for mm in re.finditer(rb"/(\w+)\s+(\d+)\s+0\s+R", body)
            if b"/Image" in objs[int(mm.group(2))]]


def page(pdf, i):
    """Image (grayscale) of page i of the PDF, or None if it has no image."""
    objs, pages = load(pdf)
    images = _xobjects(objs, pages[i - 1])
    background, mask = None, None
    for o in images:
        mk = re.search(rb"/Mask\s+(\d+)\s+0\s+R", o)
        if mk:                                           # MRC: the text is in the mask
            mask = _object_image(objs[int(mk.group(1))]).convert("L")
        else:
            im = _object_image(o).convert("L")
            if background is None or im.size[0] * im.size[1] > background.size[0] * background.size[1]:
                background = im
    if mask is None:
        return background
    if background is None:
        return mask
    return ImageChops.darker(background.resize(mask.size), mask)


def sheet(pdf, first, last, out_path, width=360, height=470, columns=6):
    ims = []
    for i in range(first, last + 1):
        try:
            im = page(pdf, i)
        except (IndexError, NotImplementedError) as e:
            print(f"p. {i}: {e}")
            im = None
        im = im or Image.new("L", (width, height), 200)
        im.thumbnail((width, height))
        ims.append((i, im))
    rows = (len(ims) + columns - 1) // columns
    out = Image.new("L", (columns * width, rows * height), 255)
    dr = ImageDraw.Draw(out)
    for k, (i, im) in enumerate(ims):
        x, y = (k % columns) * width, (k // columns) * height
        out.paste(im, (x, y))
        dr.text((x + 5, y + 5), str(i), fill=0)
    out.save(out_path)


if __name__ == "__main__":
    if len(sys.argv) >= 6 and sys.argv[2] == "sheet":
        sheet(sys.argv[1], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) >= 4:
        im = page(sys.argv[1], int(sys.argv[2]))
        if len(sys.argv) > 4:
            im = im.rotate(float(sys.argv[4]), expand=True)
        im.save(sys.argv[3])
        print(sys.argv[3], im.size)
    else:
        print(__doc__)
