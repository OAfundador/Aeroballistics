"""Estimativa de CG, massa e momentos de inércia (ADIÇÃO OPCIONAL; não faz parte do SPIN-73).

O SPIN-73 recebe o CG, o peso e as inércias prontos, no cartão de entrada (Apêndice B). Quando
eles faltam, este módulo os estima a partir da geometria do mesmo cartão. Três métodos:

  "solido"   sólido de revolução homogêneo com o contorno das entradas: ogiva (arco de raio OR
             do meplat ao ombro; cone se OR >= 1000, como no SPIN-73), cilindro e boattail
             cônico. As integrais são exatas para esse contorno. O CG sai só da geometria; a
             massa, da densidade (ou do material); as inércias, da massa ou da densidade.
  "bala"     fórmulas empíricas do BRL para balas de calibre .30 e .50, comum e perfurante
             (Hitchcock, BRL Report 620, p. 9, citando o BRL X-113):
                 g·d = 0,400 L,   A = 0,115 m d²,   B = 0,5 A + 0,0543 m L²
  "granada"  as mesmas fórmulas para granadas explosivas:
                 g·d = 0,375 L,   A = 0,140 m d²,   B = 0,5 A + 0,0594 m L²

  (g = CG a partir da BASE, em calibres; A, B = inércias axial e transversal, esta em torno do
  CG; L = comprimento; d = diâmetro; m = massa.) "bala" e "granada" exigem a massa.

Quanto erram, contra 20 projéteis com massa, CG e inércias publicados (a massa medida entra
como dado; experimental/massa/):

  balas de chumbo e aço (5,56 a .50)   "solido": CG ±0,12 cal, Ix −5 a +3 %, Iy +3 a +20 %
                                       "bala":   CG ±0,12 cal, Ix +3 a +11 %, Iy +3 a +14 %
  granadas (30 a 175 mm)               "solido": Ix −27 a −19 % (a massa fica na parede)
                                       "granada": CG ±0,14 cal, Ix −11 a +3 %, Iy −2 a +38 %
  traçantes                            CG 0,2 a 0,45 cal atrás do real nos dois métodos (a
                                       composição traçante, na base, é leve)

Para balas, qualquer dos dois; para granadas ocas, "granada". O "solido" é o único que dá o CG
sem a massa, e a massa pela densidade.

O que o contorno não tem: cinta, canelura, cavidade, ponta arredondada, base arredondada (entra
como tronco de cone). O ângulo do boattail não é entrada do SPIN-73: o padrão é 8° (o mesmo da
correção de atrito); informe `ang_bt` ou o diâmetro da base `db` se souber.

    from spin73 import massa
    pm = massa.estimar(p, massa_g=4.0, d_mm=5.69)        # PropriedadesMassa
    p2 = massa.completar(p, massa_g=4.0)                  # Projetil com o que faltava preenchido
"""
from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass, replace

import numpy as np

from .nucleo import Projetil

LB_KG = 0.45359237
IN_M = 0.0254
LBIN2_KGM2 = LB_KG * IN_M ** 2             # 1 lb·in² em kg·m²
ANG_BT_PADRAO = 8.0                         # graus; o mesmo de correcoes/reynolds.py

# Densidades nominais, kg/m³ (latão varia de 8400 a 8730 conforme a liga)
MATERIAIS = {"aco": 7850.0, "chumbo": 11340.0, "cobre": 8960.0, "latao": 8500.0,
             "aluminio": 2700.0, "tungstenio": 19250.0}

# Hitchcock, BRL 620, p. 9: (g/L, A/(m d²), coeficiente de m L² em B)
_HITCHCOCK = {"bala": (0.400, 0.115, 0.0543), "granada": (0.375, 0.140, 0.0594)}
METODOS = ("solido", "bala", "granada")


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def densidade_do_material(material: str) -> float:
    chave = _sem_acento(material)
    if chave not in MATERIAIS:
        raise ValueError(f"material desconhecido: {material!r}; conhecidos: {', '.join(MATERIAIS)}")
    return MATERIAIS[chave]


# --------------------------------------------------------------------------- contorno
def contorno(p: Projetil, ang_bt: float | None = None, db: float | None = None):
    """Trechos (x0, x1, r(x)) do contorno, em calibres, com x a partir do nariz.

    Devolve também a lista de observações sobre o que foi aproximado.
    """
    obs = []
    rm = max(p.DM, 0.0) / 2.0
    VN, VB, VL = p.VN, p.VB, p.VL
    if VN <= 0 or VL <= VN + VB:
        raise ValueError("geometria inválida: é preciso VN > 0 e VL > VN + VB")
    trechos = []
    if p.OR >= 999.0:                                         # convenção do SPIN-73: cone
        trechos.append((0.0, VN, lambda x: rm + (0.5 - rm) * x / VN))
    else:
        cx, cy = VN, 0.5 - rm                                 # corda do meplat ao ombro
        s = math.hypot(cx, cy)
        if p.OR < s / 2:
            raise ValueError(f"OR = {p.OR} é menor que meia corda da ogiva ({s / 2:.3f} cal)")
        h = math.sqrt(p.OR ** 2 - (s / 2) ** 2)
        Cx, Cy = cx / 2 + h * cy / s, rm + cy / 2 - h * cx / s
        if Cx < VN - 1e-9:
            obs.append("OR menor que o de uma ogiva tangente: o arco passaria do diâmetro e foi "
                       "limitado a ele")
        trechos.append((0.0, VN, lambda x, Cx=Cx, Cy=Cy, R=p.OR:
                        np.minimum(Cy + np.sqrt(np.maximum(R * R - (x - Cx) ** 2, 0.0)), 0.5)))
    x_bt = VL - VB
    trechos.append((VN, x_bt, lambda x: np.full_like(x, 0.5)))
    if VB > 0:
        if db is not None:
            rb = db / 2.0
        else:
            ang = ANG_BT_PADRAO if ang_bt is None else ang_bt
            rb = 0.5 - VB * math.tan(math.radians(ang))
            if ang_bt is None:
                obs.append(f"boattail cônico de {ANG_BT_PADRAO:g}° (ângulo não informado)")
        if rb <= 0:
            raise ValueError("boattail fecha antes da base: reduza o ângulo ou informe db")
        trechos.append((x_bt, VL, lambda x, x0=x_bt, rb=rb: 0.5 - (0.5 - rb) * (x - x0) / VB))
    return trechos, obs


def integrais(p: Projetil, ang_bt: float | None = None, db: float | None = None, n: int = 400):
    """Integrais do sólido homogêneo de densidade 1 e diâmetro 1 (Simpson, n par por trecho).

    V   volume (cal³);  xcg  CG a partir do nariz (cal);
    Jx  inércia axial / (ρ d⁵);  Jy  inércia transversal em torno do CG / (ρ d⁵).
    """
    trechos, obs = contorno(p, ang_bt, db)
    V = Sx = Jx = Jy0 = 0.0
    for a, b, f in trechos:
        if b <= a:
            continue
        x = np.linspace(a, b, n + 1)
        r = f(x)
        w = np.ones(n + 1)
        w[1:-1:2], w[2:-1:2] = 4.0, 2.0
        w *= (b - a) / (3.0 * n)
        a2, a4 = np.pi * r ** 2, np.pi * r ** 4
        V += w @ a2
        Sx += w @ (a2 * x)
        Jx += w @ (a4 / 2.0)
        Jy0 += w @ (a4 / 4.0 + a2 * x * x)
    xcg = Sx / V
    return dict(V=float(V), xcg=float(xcg), Jx=float(Jx), Jy=float(Jy0 - V * xcg * xcg)), obs


# --------------------------------------------------------------------------- resultado
@dataclass(frozen=True)
class PropriedadesMassa:
    """Resultado da estimativa. Posições em calibres; massa e inércias em SI e no cartão."""
    metodo: str
    cg_nariz: float                  # = VCG
    comprimento: float               # VL, calibres
    d_m: float | None = None
    massa_kg: float | None = None
    ix: float | None = None          # kg·m²
    iy: float | None = None          # kg·m², em torno do CG
    densidade: float | None = None   # kg/m³: a usada ("solido") ou a efetiva, massa/volume
    hipoteses: tuple = ()

    @property
    def cg_base(self) -> float:
        return self.comprimento - self.cg_nariz

    @property
    def massa_g(self):
        return None if self.massa_kg is None else self.massa_kg * 1000.0

    @property
    def WGT(self):                   # lb
        return None if self.massa_kg is None else self.massa_kg / LB_KG

    @property
    def IX(self):                    # lb·in²
        return None if self.ix is None else self.ix / LBIN2_KGM2

    @property
    def IY(self):
        return None if self.iy is None else self.iy / LBIN2_KGM2

    @property
    def ix_gcm2(self):
        return None if self.ix is None else self.ix * 1e7

    @property
    def iy_gcm2(self):
        return None if self.iy is None else self.iy * 1e7

    def __str__(self):
        linhas = [f"método: {self.metodo}",
                  f"CG: {self.cg_nariz:.3f} cal do nariz ({self.cg_base:.3f} da base)"]
        if self.massa_kg is not None:
            linhas.append(f"massa: {self.massa_g:.4g} g ({self.WGT:.5g} lb)")
        if self.ix is not None:
            linhas.append(f"Ix: {self.ix_gcm2:.4g} g·cm² ({self.IX:.5g} lb·in²)")
            linhas.append(f"Iy: {self.iy_gcm2:.4g} g·cm² ({self.IY:.5g} lb·in²)")
        if self.densidade is not None:
            linhas.append(f"densidade: {self.densidade:.0f} kg/m³")
        linhas += [f"hipótese: {h}" for h in self.hipoteses]
        return "\n".join(linhas)


def _diametro_m(p: Projetil, d_mm):
    if d_mm:
        return d_mm / 1000.0
    return p.DIA * IN_M if p.DIA > 0 else None


def estimar(p: Projetil, metodo: str = "solido", *, massa_g: float | None = None,
            densidade: float | None = None, material: str | None = None,
            d_mm: float | None = None, ang_bt: float | None = None,
            db: float | None = None) -> PropriedadesMassa:
    """Estima CG, massa e inércias. A massa vem de `massa_g`, ou do p.WGT, ou (só no "solido")
    da densidade/material; o diâmetro, de `d_mm` ou do p.DIA. Sem diâmetro, só o CG."""
    if metodo not in METODOS:
        raise ValueError(f"método desconhecido: {metodo!r}; use {', '.join(METODOS)}")
    if densidade is None and material is not None:
        densidade = densidade_do_material(material)
    d = _diametro_m(p, d_mm)
    m = massa_g / 1000.0 if massa_g else (p.WGT * LB_KG if p.WGT > 0 else None)

    if metodo == "solido":
        I, obs = integrais(p, ang_bt, db)
        hip = ["sólido homogêneo: sem cinta, canelura nem cavidade"] + obs
        if d is None:
            return PropriedadesMassa(metodo, I["xcg"], p.VL, hipoteses=tuple(hip))
        if m is None and densidade is not None:
            m = densidade * I["V"] * d ** 3
        if m is None:
            return PropriedadesMassa(metodo, I["xcg"], p.VL, d, hipoteses=tuple(
                hip + ["sem massa nem densidade: só o CG"]))
        rho = m / (I["V"] * d ** 3)
        return PropriedadesMassa(metodo, I["xcg"], p.VL, d, m, rho * I["Jx"] * d ** 5,
                                 rho * I["Jy"] * d ** 5, rho, tuple(hip))

    g, a, b = _HITCHCOCK[metodo]
    hip = [f"fórmulas empíricas de Hitchcock (BRL 620, p. 9) para "
           f"{'balas .30 e .50' if metodo == 'bala' else 'granadas explosivas'}"]
    cg = p.VL - g * p.VL
    if m is None:
        raise ValueError(f"o método {metodo!r} exige a massa (massa_g ou WGT)")
    if d is None:
        return PropriedadesMassa(metodo, cg, p.VL, None, m, hipoteses=tuple(
            hip + ["sem diâmetro: só o CG e a massa"]))
    A = a * m * d * d
    B = 0.5 * A + b * m * (p.VL * d) ** 2
    return PropriedadesMassa(metodo, cg, p.VL, d, m, A, B, hipoteses=tuple(hip))


def o_que_falta(p: Projetil) -> list[str]:
    """Entradas de massa que o cartão não tem (as que `completar` preencheria)."""
    falta = []
    if p.VCG is None or p.VCG <= 0:
        falta.append("VCG")
    for c in ("WGT", "IX", "IY"):
        if getattr(p, c) <= 0:
            falta.append(c)
    return falta


def completar(p: Projetil, metodo: str = "solido", **kw) -> Projetil:
    """Novo Projetil com VCG, WGT, IX e IY preenchidos onde faltavam. O que o cartão já tem
    nunca é trocado. Com `d_mm` e sem DIA, o DIA também é preenchido (em polegadas)."""
    falta = o_que_falta(p)
    muda = {}
    d_mm = kw.get("d_mm")
    if d_mm and p.DIA <= 0:
        muda["DIA"] = d_mm / 25.4
    if not falta:
        return replace(p, **muda) if muda else p
    pm = estimar(p, metodo, **kw)
    if "VCG" in falta:
        muda["VCG"] = pm.cg_nariz
    if "WGT" in falta and pm.massa_kg is not None:
        muda["WGT"] = pm.WGT
    if "IX" in falta and pm.ix is not None:
        muda["IX"] = pm.IX
    if "IY" in falta and pm.iy is not None:
        muda["IY"] = pm.IY
    return replace(p, **muda)


__all__ = ["PropriedadesMassa", "estimar", "completar", "o_que_falta", "contorno", "integrais",
           "MATERIAIS", "METODOS", "densidade_do_material"]
