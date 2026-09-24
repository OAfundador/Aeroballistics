"""Entradas em outras unidades (ADIÇÃO OPCIONAL: só conversão exata, não muda nenhum cálculo).

O cartão do SPIN-73 (aeroballistics.Projetil) usa calibres, polegadas, libras, lb·in² e °F. Aqui ele
pode ser montado também com as chaves abaixo, que viram as do cartão:

    D_MM        diâmetro, mm                     -> DIA  (polegadas)
    MASSA_G     massa, g   | MASSA_KG, kg        -> WGT  (lb)
    IX_GCM2     inércia axial, g·cm² | IX_KGM2   -> IX   (lb·in²)
    IY_GCM2     inércia transversal  | IY_KGM2   -> IY   (lb·in²)
    PASSO_MM    comprimento de uma volta da raia, mm        -> TWIST (calibres por volta)
    PASSO_POL   o mesmo em polegadas ("1:7" -> 7)           -> TWIST
    TEMP_C      temperatura, °C                  -> TEMP (°F)
    CG_BASE     CG a partir da BASE, calibres    -> VCG = VL − CG_BASE
    DGUN_MM     diâmetro do tubo, mm             -> DGUN (polegadas)

E as opções da estimativa de massa (aeroballistics.massa), que não são do cartão:

    ESTIMAR_MASSA  solido | bala | granada       DENSIDADE  kg/m³      MATERIAL  aco, chumbo...
    ANG_BT         ângulo do boattail, graus     DB         diâmetro da base, calibres

As chaves não distinguem maiúsculas. Uma grandeza dada nas duas formas (DIA e D_MM, por
exemplo) é erro.
"""
from __future__ import annotations

from dataclasses import fields

from .nucleo import Projetil

MM_IN = 25.4
G_LB = 453.59237
GCM2_LBIN2 = G_LB * 2.54 ** 2                  # 1 lb·in² = 2926,397 g·cm²
KGM2_LBIN2 = GCM2_LBIN2 * 1e-7

CANONICAS = [f.name for f in fields(Projetil)]  # VL, VN, VB, VCG, DIA, ..., nome
OPCOES_MASSA = ("ESTIMAR_MASSA", "DENSIDADE", "MATERIAL", "ANG_BT", "DB")
ALTERNATIVAS = {  # chave -> (chave do cartão, conversão)
    "D_MM": ("DIA", lambda v, c: v / MM_IN),
    "MASSA_G": ("WGT", lambda v, c: v / G_LB),
    "MASSA_KG": ("WGT", lambda v, c: v * 1000.0 / G_LB),
    "IX_GCM2": ("IX", lambda v, c: v / GCM2_LBIN2),
    "IY_GCM2": ("IY", lambda v, c: v / GCM2_LBIN2),
    "IX_KGM2": ("IX", lambda v, c: v / KGM2_LBIN2),
    "IY_KGM2": ("IY", lambda v, c: v / KGM2_LBIN2),
    "TEMP_C": ("TEMP", lambda v, c: v * 9.0 / 5.0 + 32.0),
    "DGUN_MM": ("DGUN", lambda v, c: v / MM_IN),
    "CG_BASE": ("VCG", lambda v, c: _exige(c, "VL", "CG_BASE") - v),
    "PASSO_MM": ("TWIST", lambda v, c: v / (_exige(c, "DIA", "PASSO_MM") * MM_IN)),
    "PASSO_POL": ("TWIST", lambda v, c: v / _exige(c, "DIA", "PASSO_POL")),
}


def _exige(c, chave, quem):
    if c.get(chave) in (None, 0, 0.0):
        raise ValueError(f"{quem} exige {chave} (ou a forma métrica dele)")
    return c[chave]


def normalizar(chave: str) -> str:
    k = chave.strip()
    return "nome" if k.lower() == "nome" else k.upper()


def separar(campos: dict) -> tuple[dict, dict]:
    """(campos do cartão, opções da estimativa de massa), com as alternativas convertidas."""
    canon, alt, opc = {}, {}, {}
    for k, v in campos.items():
        if v is None or v == "":
            continue
        k = normalizar(k)
        if k in CANONICAS:
            canon[k] = v if k == "nome" else float(v)
        elif k in ALTERNATIVAS:
            alt[k] = float(v)
        elif k in OPCOES_MASSA:
            opc[k] = v if k in ("ESTIMAR_MASSA", "MATERIAL") else float(v)
        else:
            validas = CANONICAS + list(ALTERNATIVAS) + list(OPCOES_MASSA)
            raise ValueError(f"entrada desconhecida: {k}. Válidas: {', '.join(validas)}")
    # primeiro as que não dependem de outras (D_MM antes de PASSO_MM, por exemplo)
    ordem = sorted(alt, key=lambda k: k in ("CG_BASE", "PASSO_MM", "PASSO_POL"))
    for k in ordem:
        destino, conv = ALTERNATIVAS[k]
        if destino in canon:
            raise ValueError(f"{destino} informado duas vezes ({destino} e {k})")
        canon[destino] = conv(alt[k], canon)
    return canon, opc


def projetil(**campos) -> Projetil:
    """Projetil a partir de chaves do cartão e/ou das alternativas acima."""
    canon, opc = separar(campos)
    if opc:
        raise ValueError(f"{', '.join(opc)} são opções de aeroballistics.massa, não do cartão")
    return Projetil(**canon)


def ler_campos(caminho: str) -> dict:
    """Arquivo 'CHAVE = valor' (# comenta) -> dicionário cru (nada convertido)."""
    campos = {}
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            linha = linha.split("#", 1)[0].strip()
            if not linha:
                continue
            if "=" not in linha:
                raise ValueError(f"{caminho}:{n}: esperado 'CHAVE = valor'")
            chave, valor = (x.strip() for x in linha.split("=", 1))
            campos[chave] = valor
    return campos


def ler_entrada(caminho: str) -> tuple[Projetil, dict]:
    """Como aeroballistics.ler_entrada, mas aceita também as alternativas e as opções de massa.
    Devolve (Projetil, opções da estimativa de massa)."""
    canon, opc = separar(ler_campos(caminho))
    return Projetil(**canon), opc


__all__ = ["projetil", "separar", "ler_campos", "ler_entrada", "ALTERNATIVAS", "OPCOES_MASSA"]
