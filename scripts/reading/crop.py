"""
Crops of the DTIC AD0915628 scan (SPIN-73) for visual reading.

Numbering: PRINTED page of the report; the JP2 file is index page + 3
(p. 80 -> sources/jp2/DTIC_AD0915628_0083.jp2).

Tables (pp. 29-68) and listing (pp. 79-86) are printed sideways: by default those pages
are rotated -90 degrees (PIL rotate(-90, expand=True)). All of them get
ImageOps.autocontrast(cutoff=0.5). The rotated page is cached in sources/cache/.

Usage (coordinates ALWAYS on the already rotated page):

  # overview with a fraction grid (0.1 by 0.1) to locate the region
  python scripts/reading/crop.py 80 --overview --out crops/p80_overview.png

  # crop by fractions of the page (x0 y0 x1 y1), with zoom
  python scripts/reading/crop.py 80 --box 0.34 0.34 0.86 0.40 --zoom 1.2 --out crops/p80_xc6.png

  # crop in pixels (values > 1 are treated as pixels)
  python scripts/reading/crop.py 65 --box 1350 850 3329 1130 --out crops/p65_head.png

  # JP2 index directly, without page conversion
  python scripts/reading/crop.py --jp2 83 --overview --out crops/jp2_0083.png

Options: --rotate {auto,0,-90,90}  --grid N (lines every N px in the crop)  --max-width W
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP2 = os.path.join(ROOT, "sources", "jp2")
CACHE = os.path.join(ROOT, "sources", "cache")


def jp2_index(page):
    return page + 3


def default_rotation(page):
    if page is None:
        return 0
    return -90 if (29 <= page <= 68 or 79 <= page <= 86) else 0


def load(index, rotation):
    """Rotated page with autocontrast (cached as PNG)."""
    os.makedirs(CACHE, exist_ok=True)
    cache = os.path.join(CACHE, f"jp2_{index:04d}_g{rotation:+d}.png")
    if os.path.exists(cache):
        return Image.open(cache)
    source = os.path.join(JP2, f"DTIC_AD0915628_{index:04d}.jp2")
    if not os.path.exists(source):
        sys.exit(f"file not found: {source}")
    im = Image.open(source).convert("L")
    if rotation:
        im = im.rotate(rotation, expand=True)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    tmp = cache + f".{os.getpid()}.tmp.png"
    im.save(tmp)
    os.replace(tmp, cache)          # atomic write: several agents may use the cache
    return im


def box_in_pixels(box, w, h):
    if all(0.0 <= v <= 1.0 for v in box):
        x0, y0, x1, y1 = box[0] * w, box[1] * h, box[2] * w, box[3] * h
    else:
        x0, y0, x1, y1 = box
    x0, x1 = sorted((max(0, int(x0)), min(w, int(x1))))
    y0, y1 = sorted((max(0, int(y0)), min(h, int(y1))))
    return x0, y0, x1, y1


def overview(im, width=1600):
    """Whole page reduced, with a labeled fraction grid."""
    w, h = im.size
    scale = width / w
    v = im.resize((width, int(h * scale)), Image.LANCZOS).convert("RGB")
    d = ImageDraw.Draw(v)
    for k in range(1, 10):
        x = int(k / 10 * v.width); y = int(k / 10 * v.height)
        d.line([(x, 0), (x, v.height)], fill=(220, 60, 60), width=1)
        d.line([(0, y), (v.width, y)], fill=(220, 60, 60), width=1)
        d.text((x + 3, 3), f"{k / 10:.1f}", fill=(200, 0, 0))
        d.text((3, y + 3), f"{k / 10:.1f}", fill=(200, 0, 0))
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", type=int, nargs="?", help="printed page of the report")
    ap.add_argument("--jp2", type=int, help="JP2 file index (instead of the page)")
    ap.add_argument("--rotate", default="auto", choices=["auto", "0", "-90", "90"])
    ap.add_argument("--overview", action="store_true", help="whole page reduced, with a fraction grid")
    ap.add_argument("--box", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--grid", type=int, default=0, help="guide lines every N px of the crop (0 = none)")
    ap.add_argument("--max-width", type=int, default=2400, help="shrinks the output above this")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.jp2 is None and a.page is None:
        ap.error("give the printed page or --jp2")
    index = a.jp2 if a.jp2 is not None else jp2_index(a.page)
    page = a.page if a.jp2 is None else index - 3
    rotation = default_rotation(page) if a.rotate == "auto" else int(a.rotate)
    im = load(index, rotation)
    w, h = im.size

    if a.overview:
        out = overview(im)
        info = f"overview {w}x{h} px (page rotated {rotation} degrees)"
    else:
        if not a.box:
            ap.error("use --box or --overview")
        x0, y0, x1, y1 = box_in_pixels(a.box, w, h)
        out = im.crop((x0, y0, x1, y1))
        if a.zoom != 1.0:
            out = out.resize((int(out.width * a.zoom), int(out.height * a.zoom)), Image.LANCZOS)
        if out.width > a.max_width:
            f = a.max_width / out.width
            out = out.resize((a.max_width, int(out.height * f)), Image.LANCZOS)
        if a.grid:
            out = out.convert("RGB"); d = ImageDraw.Draw(out)
            sx = out.width / (x1 - x0)
            for gx in range(0, x1 - x0, a.grid):
                d.line([(gx * sx, 0), (gx * sx, out.height)], fill=(90, 160, 230), width=1)
                d.text((gx * sx + 2, 2), str(x0 + gx), fill=(20, 90, 200))
            for gy in range(0, y1 - y0, a.grid):
                d.line([(0, gy * sx), (out.width, gy * sx)], fill=(90, 160, 230), width=1)
                d.text((2, gy * sx + 2), str(y0 + gy), fill=(20, 90, 200))
        info = (f"crop px ({x0},{y0})-({x1},{y1}) = fractions ({x0 / w:.3f},{y0 / h:.3f})-({x1 / w:.3f},{y1 / h:.3f})"
                f" of the {w}x{h} page; output {out.width}x{out.height}")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    out.save(a.out)
    print(f"p. {page} (JP2 {index:04d}): {info} -> {a.out}")


if __name__ == "__main__":
    main()
