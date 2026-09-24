"""
Recortes do scan DTIC AD0915628 (SPIN-73) para leitura visual.

Numeração: página IMPRESSA do relatório; o arquivo JP2 é o índice página + 3
(p. 80 -> fontes/jp2/DTIC_AD0915628_0083.jp2).

Tabelas (pp. 29-68) e listing (pp. 79-86) estão impressos de lado: por padrão
essas páginas são giradas -90 graus (PIL rotate(-90, expand=True)). Todas recebem
ImageOps.autocontrast(cutoff=0.5). A página girada fica em cache em fontes/cache/.

Uso (coordenadas SEMPRE na página já girada):

  # visão geral com grade de frações (0,1 em 0,1) para localizar a região
  python scripts/leitura/recorte.py 80 --visao --saida recortes/p80_visao.png

  # recorte por frações da página (x0 y0 x1 y1), com zoom
  python scripts/leitura/recorte.py 80 --caixa 0.34 0.34 0.86 0.40 --zoom 1.2 --saida recortes/p80_xc6.png

  # recorte em pixels (valores > 1 são tratados como pixels)
  python scripts/leitura/recorte.py 65 --caixa 1350 850 3329 1130 --saida recortes/p65_cab.png

  # índice JP2 direto, sem conversão de página
  python scripts/leitura/recorte.py --jp2 83 --visao --saida recortes/jp2_0083.png

Opções: --girar {auto,0,-90,90}  --grade N (linhas a cada N px no recorte)  --largura-max L
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageOps

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP2 = os.path.join(RAIZ, "fontes", "jp2")
CACHE = os.path.join(RAIZ, "fontes", "cache")


def indice_jp2(pagina):
    return pagina + 3


def girar_padrao(pagina):
    if pagina is None:
        return 0
    return -90 if (29 <= pagina <= 68 or 79 <= pagina <= 86) else 0


def carregar(indice, giro):
    """Página girada e com autocontraste (em cache como PNG)."""
    os.makedirs(CACHE, exist_ok=True)
    cache = os.path.join(CACHE, f"jp2_{indice:04d}_g{giro:+d}.png")
    if os.path.exists(cache):
        return Image.open(cache)
    fonte = os.path.join(JP2, f"DTIC_AD0915628_{indice:04d}.jp2")
    if not os.path.exists(fonte):
        sys.exit(f"arquivo não encontrado: {fonte}")
    im = Image.open(fonte).convert("L")
    if giro:
        im = im.rotate(giro, expand=True)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    tmp = cache + f".{os.getpid()}.tmp.png"
    im.save(tmp)
    os.replace(tmp, cache)          # escrita atômica: vários agentes podem usar o cache
    return im


def caixa_em_pixels(caixa, w, h):
    if all(0.0 <= v <= 1.0 for v in caixa):
        x0, y0, x1, y1 = caixa[0] * w, caixa[1] * h, caixa[2] * w, caixa[3] * h
    else:
        x0, y0, x1, y1 = caixa
    x0, x1 = sorted((max(0, int(x0)), min(w, int(x1))))
    y0, y1 = sorted((max(0, int(y0)), min(h, int(y1))))
    return x0, y0, x1, y1


def visao(im, largura=1600):
    """Página inteira reduzida, com grade de frações rotulada."""
    w, h = im.size
    esc = largura / w
    v = im.resize((largura, int(h * esc)), Image.LANCZOS).convert("RGB")
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
    ap.add_argument("pagina", type=int, nargs="?", help="página impressa do relatório")
    ap.add_argument("--jp2", type=int, help="índice do arquivo JP2 (em vez da página)")
    ap.add_argument("--girar", default="auto", choices=["auto", "0", "-90", "90"])
    ap.add_argument("--visao", action="store_true", help="página inteira reduzida com grade de frações")
    ap.add_argument("--caixa", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--grade", type=int, default=0, help="linhas-guia a cada N px do recorte (0 = sem)")
    ap.add_argument("--largura-max", type=int, default=2400, help="reduz a saída se passar disso")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()

    if a.jp2 is None and a.pagina is None:
        ap.error("informe a página impressa ou --jp2")
    indice = a.jp2 if a.jp2 is not None else indice_jp2(a.pagina)
    pagina = a.pagina if a.jp2 is None else indice - 3
    giro = girar_padrao(pagina) if a.girar == "auto" else int(a.girar)
    im = carregar(indice, giro)
    w, h = im.size

    if a.visao:
        out = visao(im)
        info = f"visão geral {w}x{h} px (página girada {giro} graus)"
    else:
        if not a.caixa:
            ap.error("use --caixa ou --visao")
        x0, y0, x1, y1 = caixa_em_pixels(a.caixa, w, h)
        out = im.crop((x0, y0, x1, y1))
        if a.zoom != 1.0:
            out = out.resize((int(out.width * a.zoom), int(out.height * a.zoom)), Image.LANCZOS)
        if out.width > a.largura_max:
            f = a.largura_max / out.width
            out = out.resize((a.largura_max, int(out.height * f)), Image.LANCZOS)
        if a.grade:
            out = out.convert("RGB"); d = ImageDraw.Draw(out)
            sx = out.width / (x1 - x0)
            for gx in range(0, x1 - x0, a.grade):
                d.line([(gx * sx, 0), (gx * sx, out.height)], fill=(90, 160, 230), width=1)
                d.text((gx * sx + 2, 2), str(x0 + gx), fill=(20, 90, 200))
            for gy in range(0, y1 - y0, a.grade):
                d.line([(0, gy * sx), (out.width, gy * sx)], fill=(90, 160, 230), width=1)
                d.text((2, gy * sx + 2), str(y0 + gy), fill=(20, 90, 200))
        info = (f"recorte px ({x0},{y0})-({x1},{y1}) = frações ({x0 / w:.3f},{y0 / h:.3f})-({x1 / w:.3f},{y1 / h:.3f})"
                f" da página {w}x{h}; saída {out.width}x{out.height}")

    os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
    out.save(a.saida)
    print(f"p. {pagina} (JP2 {indice:04d}): {info} -> {a.saida}")


if __name__ == "__main__":
    main()
