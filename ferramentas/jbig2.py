"""Decodificador JBIG2 mínimo (ITU-T T.88), em Python puro.

Os PDFs "MRC" da DTIC guardam o texto de cada página numa máscara JBIG2 (e o fundo numa imagem
JPEG de baixa resolução). Nem o Pillow nem o leitor de PDF do Windows decodificam essa máscara;
este módulo decodifica o que esses PDFs usam: dicionário de símbolos e região de texto com
codificação aritmética (com refinamento e agregação) e região genérica (aritmética ou MMR).
Não implementa Huffman, halftone nem regiões transpostas.

Foi escrito para ler os relatórios de voo livre de python/experimental/benchmarks/ (30 mm
XM788, 175 mm T203, 152 mm XM617). Uso: ver ferramentas/pdf_paginas.py.

    from jbig2 import decodificar, para_imagem
    pagina = decodificar(bytes_do_stream_jbig2)       # lista de linhas (bytearray, 1 = tinta)
"""
import re
import struct
import sys

QE = [
    (0x5601, 1, 1, 1), (0x3401, 2, 6, 0), (0x1801, 3, 9, 0), (0x0AC1, 4, 12, 0), (0x0521, 5, 29, 0),
    (0x0221, 38, 33, 0), (0x5601, 7, 6, 1), (0x5401, 8, 14, 0), (0x4801, 9, 14, 0), (0x3801, 10, 14, 0),
    (0x3001, 11, 17, 0), (0x2401, 12, 18, 0), (0x1C01, 13, 20, 0), (0x1601, 29, 21, 0), (0x5601, 15, 14, 1),
    (0x5401, 16, 14, 0), (0x5101, 17, 15, 0), (0x4801, 18, 16, 0), (0x3801, 19, 17, 0), (0x3401, 20, 18, 0),
    (0x3001, 21, 19, 0), (0x2801, 22, 19, 0), (0x2401, 23, 20, 0), (0x2201, 24, 21, 0), (0x1C01, 25, 22, 0),
    (0x1801, 26, 23, 0), (0x1601, 27, 24, 0), (0x1401, 28, 25, 0), (0x1201, 29, 26, 0), (0x1101, 30, 27, 0),
    (0x0AC1, 31, 28, 0), (0x09C1, 32, 29, 0), (0x08A1, 33, 30, 0), (0x0521, 34, 31, 0), (0x0441, 35, 32, 0),
    (0x02A1, 36, 33, 0), (0x0221, 37, 34, 0), (0x0141, 38, 35, 0), (0x0111, 39, 36, 0), (0x0085, 40, 37, 0),
    (0x0049, 41, 38, 0), (0x0025, 42, 39, 0), (0x0015, 43, 40, 0), (0x0009, 44, 41, 0), (0x0005, 45, 42, 0),
    (0x0001, 45, 43, 0), (0x5601, 46, 46, 0),
]


class Arit:
    def __init__(self, data, start, end):
        self.d, self.bp, self.end = data, start, end
        self.chigh = data[start]
        self.clow = 0
        self.ct = 0
        self.byte_in()
        self.chigh = ((self.chigh << 7) & 0xFFFF) | ((self.clow >> 9) & 0x7F)
        self.clow = (self.clow << 7) & 0xFFFF
        self.ct -= 7
        self.a = 0x8000

    def byte_in(self):
        d, bp = self.d, self.bp
        if d[bp] == 0xFF:
            if bp + 1 < len(d) and d[bp + 1] > 0x8F:
                self.clow += 0xFF00
                self.ct = 8
            else:
                bp += 1
                self.clow += d[bp] << 9
                self.ct = 7
                self.bp = bp
        else:
            bp += 1
            self.clow += (d[bp] << 8) if bp < self.end else 0xFF00
            self.ct = 8
            self.bp = bp
        if self.clow > 0xFFFF:
            self.chigh += self.clow >> 16
            self.clow &= 0xFFFF

    def bit(self, cx, pos):
        st = cx[pos]
        idx, mps = st >> 1, st & 1
        qe, nmps, nlps, sw = QE[idx]
        a = self.a - qe
        if self.chigh < qe:
            if a < qe:
                a = qe
                d = mps
                idx = nmps
            else:
                a = qe
                d = 1 ^ mps
                if sw:
                    mps = d
                idx = nlps
        else:
            self.chigh -= qe
            if a & 0x8000:
                self.a = a
                return mps
            if a < qe:
                d = 1 ^ mps
                if sw:
                    mps = d
                idx = nlps
            else:
                d = mps
                idx = nmps
        while True:
            if self.ct == 0:
                self.byte_in()
            a <<= 1
            self.chigh = ((self.chigh << 1) & 0xFFFF) | ((self.clow >> 15) & 1)
            self.clow = (self.clow << 1) & 0xFFFF
            self.ct -= 1
            if a & 0x8000:
                break
        self.a = a
        cx[pos] = (idx << 1) | mps
        return d


class Ctx:
    def __init__(self, dec):
        self.dec = dec
        self.c = {}

    def get(self, nome, n=1 << 17):
        if nome not in self.c:
            self.c[nome] = bytearray(n)
        return self.c[nome]


def dec_int(ctx, proc):
    cx, dec = ctx.get(proc, 512), ctx.dec
    prev = [1]

    def rb(n):
        v = 0
        for _ in range(n):
            b = dec.bit(cx, prev[0])
            p = prev[0]
            prev[0] = ((p << 1) | b) if p < 256 else ((((p << 1) | b) & 511) | 256)
            v = (v << 1) | b
        return v
    s = rb(1)
    if rb(1):
        if rb(1):
            if rb(1):
                if rb(1):
                    if rb(1):
                        v = rb(32) + 4436
                    else:
                        v = rb(12) + 340
                else:
                    v = rb(8) + 84
            else:
                v = rb(6) + 20
        else:
            v = rb(4) + 4
    else:
        v = rb(2)
    if s == 0:
        return v
    return -v if v > 0 else None


def dec_iaid(ctx, n):
    cx, dec = ctx.get("IAID", 1 << (n + 1)), ctx.dec
    prev = 1
    for _ in range(n):
        prev = (prev << 1) | dec.bit(cx, prev)
    return prev & ((1 << n) - 1)


def log2c(x):
    n, i = 1, 0
    while x > n:
        n <<= 1
        i += 1
    return i


GEN = [
    [(-1, -2), (0, -2), (1, -2), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (-4, 0), (-3, 0), (-2, 0), (-1, 0)],
    [(-1, -2), (0, -2), (1, -2), (2, -2), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (-3, 0), (-2, 0), (-1, 0)],
    [(-1, -2), (0, -2), (1, -2), (-2, -1), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0)],
    [(-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (-4, 0), (-3, 0), (-2, 0), (-1, 0)],
]


SLTP = [0x9B25, 0x0795, 0x00E5, 0x0195]


def dec_generic(ctx, w, h, tpl, at, tpgd=False):
    """Região genérica sem MMR. Contexto: pixels do molde ordenados por (y, x), o primeiro no
    bit mais alto (a ordem do pdf.js, que é a que dá os contextos SLTP da tabela acima)."""
    t = sorted(GEN[tpl] + list(at), key=lambda p: (p[1], p[0]))
    cx, dec = ctx.get("GB", 1 << 16), ctx.dec
    bm = []
    ltp = 0
    for i in range(h):
        if tpgd:
            ltp ^= dec.bit(cx, SLTP[tpl])
            if ltp:
                bm.append(bytearray(bm[-1]) if bm else bytearray(w))
                continue
        row = bytearray(w)
        bm.append(row)
        for j in range(w):
            c = 0
            for (x, y) in t:
                c <<= 1
                ii, jj = i + y, j + x
                if ii >= 0 and 0 <= jj < w and (ii < i or jj < j):
                    c |= bm[ii][jj]
            row[j] = dec.bit(cx, c)
    return bm


REF = [
    ([(0, -1), (1, -1), (-1, 0)], [(0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]),
    ([(-1, -1), (0, -1), (1, -1), (-1, 0)], [(0, -1), (-1, 0), (0, 0), (1, 0), (0, 1), (1, 1)]),
]


def dec_refine(ctx, w, h, tpl, ref, dx, dy, at):
    cod, rfr = REF[tpl]
    if tpl == 0:
        cod, rfr = cod + [at[0]], rfr + [at[1]]
    rh, rw = len(ref), (len(ref[0]) if ref else 0)
    cx, dec = ctx.get("GR", 1 << 16), ctx.dec
    bm = []
    for i in range(h):
        row = bytearray(w)
        bm.append(row)
        for j in range(w):
            c = 0
            for (x, y) in cod:
                ii, jj = i + y, j + x
                c <<= 1
                if ii >= 0 and 0 <= jj < w and (ii < i or jj < j):
                    c |= bm[ii][jj]
            for (x, y) in rfr:
                ii, jj = i + y - dy, j + x - dx
                c <<= 1
                if 0 <= ii < rh and 0 <= jj < rw:
                    c |= ref[ii][jj]
            row[j] = dec.bit(cx, c)
    return bm


def dec_text(ctx, refine, w, h, defpix, ninst, strip, syms, codelen, transp, dsoff, refcorner, combop, rtpl, rat, logstrip):
    bm = [bytearray([1 if defpix else 0]) * w for _ in range(h)]
    stript = -dec_int(ctx, "IADT") * 1
    firsts = 0
    i = 0
    while i < ninst:
        stript += dec_int(ctx, "IADT")
        firsts += dec_int(ctx, "IAFS")
        curs = firsts
        while True:
            curt = dec_int(ctx, "IAIT") if strip > 1 else 0
            t = strip * stript + curt
            sid = dec_iaid(ctx, codelen)
            ari = refine and dec_int(ctx, "IARI")
            sb = syms[sid]
            sw, sh = (len(sb[0]) if sb else 0), len(sb)
            if ari:
                rdw, rdh = dec_int(ctx, "IARDW"), dec_int(ctx, "IARDH")
                rdx, rdy = dec_int(ctx, "IARDX"), dec_int(ctx, "IARDY")
                sw += rdw
                sh += rdh
                sb = dec_refine(ctx, sw, sh, rtpl, sb, (rdw >> 1) + rdx, (rdh >> 1) + rdy, rat)
            inc = 0
            if not transp:
                if refcorner > 1:
                    curs += sw - 1
                else:
                    inc = sw - 1
            elif not (refcorner & 1):
                curs += sh - 1
            else:
                inc = sh - 1
            if transp:
                raise NotImplementedError("transposto")
            ot = t - (0 if refcorner & 1 else sh - 1)
            os_ = curs - (sw - 1 if refcorner & 2 else 0)
            for t2 in range(sh):
                y = ot + t2
                if not 0 <= y < h:
                    continue
                row, srow = bm[y], sb[t2]
                for s2 in range(sw):
                    x = os_ + s2
                    if 0 <= x < w and srow[s2]:
                        if combop == 0:
                            row[x] |= 1
                        elif combop == 2:
                            row[x] ^= 1
                        elif combop == 1:
                            row[x] &= 1
                        else:
                            raise NotImplementedError(combop)
            i += 1
            ds = dec_int(ctx, "IADS")
            if ds is None:
                break
            curs += inc + ds + dsoff
    return bm


def at_pairs(b, n):
    return [(struct.unpack("b", b[2 * k:2 * k + 1])[0], struct.unpack("b", b[2 * k + 1:2 * k + 2])[0]) for k in range(n)]


def dec_symdict(d, ins):
    fl = struct.unpack(">H", d[0:2])[0]
    huff, refagg = fl & 1, (fl >> 1) & 1
    tpl, rtpl = (fl >> 10) & 3, (fl >> 12) & 1
    if huff:
        raise NotImplementedError("Huffman")
    p = 2
    nat = 4 if tpl == 0 else 1
    at = at_pairs(d[p:], nat)
    p += 2 * nat
    rat = []
    if refagg and rtpl == 0:
        rat = at_pairs(d[p:], 2)
        p += 4
    nex, nnew = struct.unpack(">II", d[p:p + 8])
    p += 8
    ctx = Ctx(Arit(d, p, len(d)))
    new = []
    ch = 0
    codelen = log2c(len(ins) + nnew)
    while len(new) < nnew:
        ch += dec_int(ctx, "IADH")
        cw = 0
        while True:
            dw = dec_int(ctx, "IADW")
            if dw is None:
                break
            cw += dw
            if refagg:
                n = dec_int(ctx, "IAAI")
                if n > 1:
                    bm = dec_text(ctx, True, cw, ch, 0, n, 1, ins + new, codelen, 0, 0, 1, 0, rtpl, rat, 0)
                else:
                    sid = dec_iaid(ctx, codelen)
                    rdx, rdy = dec_int(ctx, "IARDX"), dec_int(ctx, "IARDY")
                    ref = ins[sid] if sid < len(ins) else new[sid - len(ins)]
                    bm = dec_refine(ctx, cw, ch, rtpl, ref, rdx, rdy, rat)
            else:
                bm = dec_generic(ctx, cw, ch, tpl, at)
            new.append(bm)
    flags, cur = [], False
    tot = len(ins) + nnew
    while len(flags) < tot:
        r = dec_int(ctx, "IAEX")
        flags += [cur] * r
        cur = not cur
    todos = ins + new
    return [s for s, f in zip(todos, flags) if f]


def dec_textseg(d, syms):
    w, h, x, y, fl0 = struct.unpack(">IIIIB", d[0:17])
    fl = struct.unpack(">H", d[17:19])[0]
    p = 19
    huff, refine = fl & 1, (fl >> 1) & 1
    logstrip = (fl >> 2) & 3
    refcorner = (fl >> 4) & 3
    transp = (fl >> 6) & 1
    combop = (fl >> 7) & 3
    defpix = (fl >> 9) & 1
    dsoff = (fl >> 10) & 31
    if dsoff > 15:
        dsoff -= 32
    rtpl = (fl >> 15) & 1
    if huff:
        raise NotImplementedError("Huffman")
    rat = []
    if refine and rtpl == 0:
        rat = at_pairs(d[p:], 2)
        p += 4
    ninst = struct.unpack(">I", d[p:p + 4])[0]
    p += 4
    ctx = Ctx(Arit(d, p, len(d)))
    bm = dec_text(ctx, refine, w, h, defpix, ninst, 1 << logstrip, syms, log2c(len(syms)), transp, dsoff,
                  refcorner, combop, rtpl, rat, logstrip)
    return (x, y, w, h), bm


def dec_genseg(d):
    w, h, x, y, fl0 = struct.unpack(">IIIIB", d[0:17])
    fl = d[17]
    mmr, tpl, tpgd = fl & 1, (fl >> 1) & 3, (fl >> 3) & 1
    p = 18
    if mmr:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(tiff_g4(w, h, d[p:])))
        im = im.convert("1")
        bm = [bytearray(1 if v == 0 else 0 for v in im.crop((0, k, w, k + 1)).getdata()) for k in range(h)]
        return (x, y, w, h), bm, fl0 & 7
    nat = 4 if tpl == 0 else 1
    at = at_pairs(d[p:], nat)
    p += 2 * nat
    ctx = Ctx(Arit(d, p, len(d)))
    return (x, y, w, h), dec_generic(ctx, w, h, tpl, at, bool(tpgd)), fl0 & 7


def tiff_g4(w, h, dados):
    tags = [(256, 3, 1, w), (257, 3, 1, h), (258, 3, 1, 1), (259, 3, 1, 4), (262, 3, 1, 0),
            (273, 4, 1, 8 + 2 + 12 * 9 + 4), (277, 3, 1, 1), (278, 4, 1, h), (279, 4, 1, len(dados))]
    out = bytearray(b"II*\x00" + struct.pack("<I", 8) + struct.pack("<H", len(tags)))
    for tag, tipo, n, val in sorted(tags):
        out += struct.pack("<HHI", tag, tipo, n)
        out += struct.pack("<I", val) if tipo == 4 else struct.pack("<HH", val, 0)
    out += struct.pack("<I", 0) + dados
    return bytes(out)


def combinar(pagina, bm, x, y, w, h, op):
    for k in range(h):
        if not 0 <= y + k < len(pagina):
            continue
        pr, br = pagina[y + k], bm[k]
        for c in range(w):
            xx = x + c
            if not 0 <= xx < len(pr):
                continue
            a, b = pr[xx], br[c]
            pr[xx] = (a | b) if op == 0 else (a & b) if op == 1 else (a ^ b) if op == 2 else                 (1 - (a ^ b)) if op == 3 else b


def segmentos(d):
    i, out = 0, []
    while i < len(d) - 6:
        num = struct.unpack(">I", d[i:i + 4])[0]
        fl = d[i + 4]
        typ, pa = fl & 63, (fl >> 6) & 1
        nref = d[i + 5] >> 5
        j = i + 6
        if nref == 7:
            raise NotImplementedError("muitas referências")
        tam = 1 if num <= 256 else (2 if num <= 65536 else 4)
        refs = []
        for _ in range(nref):
            refs.append(int.from_bytes(d[j:j + tam], "big"))
            j += tam
        j += 4 if pa else 1
        ln = struct.unpack(">I", d[j:j + 4])[0]
        j += 4
        out.append((num, typ, refs, d[j:j + ln]))
        i = j + ln
    return out


def decodificar(d, globais=b""):
    simb = {}
    pagina = None
    for num, typ, refs, dat in segmentos(globais) + segmentos(d):
        if typ == 48:
            pw, ph = struct.unpack(">II", dat[0:8])
            pagina = [bytearray(pw) for _ in range(ph)]
        elif typ == 0:
            ins = [s for r in refs for s in simb.get(r, [])]
            simb[num] = dec_symdict(dat, ins)
        elif typ in (6, 7):
            syms = [s for r in refs for s in simb.get(r, [])]
            (x, y, w, h), bm = dec_textseg(dat, syms)
            combinar(pagina, bm, x, y, w, h, dat[16] & 7)
        elif typ in (36, 38, 39):
            (x, y, w, h), bm, op = dec_genseg(dat)
            combinar(pagina, bm, x, y, w, h, op)
        elif typ in (49, 50, 51, 62):
            pass
        else:
            raise NotImplementedError(f"segmento tipo {typ}")
    return pagina


def para_imagem(pag):
    """Página decodificada -> imagem em tons de cinza do Pillow (tinta preta, fundo branco)."""
    from PIL import Image
    h, w = len(pag), len(pag[0])
    im = Image.frombytes("L", (w, h), b"".join(bytes(255 - 255 * v for v in r) for r in pag))
    return im
