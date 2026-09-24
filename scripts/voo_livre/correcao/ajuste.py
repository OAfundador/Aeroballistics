"""Correção empírica do SPIN-73 com dados de voo livre, validada deixando um grupo de fora.

Forma da correção (uma por coeficiente e por regime de Mach):

    relativa  (CX0, CNα, Cmq):   c_corr = c_SPIN · (1 + a + b·f(geo))
    absoluta  (CPN, Magnus):     c_corr = c_SPIN + a + b·f(geo)

O que a correção pode usar é decidido ANTES de olhar o erro: a geometria o SPIN-73 já modela
(as constantes dele foram ajustadas justamente para isso); o que ele não tem é a ESCALA. Uma
granada de 155 mm e uma bala de 5,56 mm com a mesma forma saem com os mesmos coeficientes,
mas o número de Reynolds é 25 vezes maior na granada. Então:

  - CX0: lei de atrito de parede com o número de Reynolds (reynolds.py), um parâmetro por
    regime, o comprimento de referência L_ref embutido nas constantes do SPIN-73;
  - demais: viés constante (f = nenhum) ou proporcional a log d (escala), o que a validação
    cruzada escolher, ou nada.

Uma variante que também deixa escolher atributos geométricos (ogiva, cilindro, boattail) fica
em ATRIBUTOS_GEOMETRICOS (validar(..., geometricos=True)). Ela não melhora o CMα nem o CNα
supersônico (a escolha muda a cada grupo deixado de fora) e ganha pouco no Cmq supersônico
(22,8 % → 21,2 %); o procedimento adotado, fixado antes, é o de escala.

Uma correção só entra no modelo final se a validação cruzada aninhada mostrar que ela
generaliza: erro médio menor que o do SPIN-73, melhora em mais da metade dos grupos e nenhum
grupo com o erro mais que dobrado (ver aceita()). O CPN
não é corrigido à parte: sai de CMα e CNα corrigidos (CPN = VCG − CMα/CNα).

Validação: os grupos de projéteis (dados.py) são deixados de fora um de cada vez. A
ESCOLHA do atributo também é feita sem o grupo de fora (validação cruzada aninhada), então
o erro de predição medido é o de um projétil que o ajuste nunca viu. Cada grupo pesa o
mesmo no ajuste e na métrica, para que as 45 rodadas do M101 não dominem as 16 da .50.

    python scripts/voo_livre/correcao/ajuste.py   -> tabela de resultados + src/spin73/correcoes/voo_livre.json
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import caminhos                                         # noqa: E402,F401

import dados                                            # noqa: E402
from spin73.correcoes import reynolds as rn             # noqa: E402
from spin73.correcoes.voo_livre import ARQUIVO as ARQUIVO_JSON   # noqa: E402

REGIMES = [("subsônico", 0.0, 0.9), ("transônico", 0.9, 1.25), ("supersônico", 1.25, 9.0)]
GRUPOS = ["762", "556b", "556t", "50", "m101", "m483", "762m", "30", "t203", "xm617"]
TIPO = {"CX0": "rel", "CNA": "rel", "CMA": "rel", "CMQ": "rel", "CNPA": "abs", "CPN": "abs"}
# Coeficientes que a correção aplica. O CPN não: sai de CMα e CNα corrigidos (CPN = VCG − CMα/CNα),
# para que os três fiquem coerentes; ele só é validado, para mostrar o que acontece com ele.
APLICADOS = ("CX0", "CNA", "CMA", "CMQ", "CNPA")

ATRIBUTOS = {
    "nenhum": None,
    "log d": lambda l: np.log10(l["d_mm"] / 10.0),
}
ATRIBUTOS_GEOMETRICOS = {
    "ogiva": lambda l: l["geo"]["VN"],
    "cilindro": lambda l: l["geo"]["VL"] - l["geo"]["VN"] - l["geo"]["VB"],
    "boattail": lambda l: l["geo"]["VB"],
}
GRADE_LREF = np.logspace(np.log10(0.02), np.log10(1.0), 61)     # m


def regime(M):
    return next(n for n, a, b in REGIMES if a <= M < b)


def alvo(l, tipo):
    return l["med"] / l["spin"] - 1.0 if tipo == "rel" else l["med"] - l["spin"]


def aplicar(l, tipo, coef):
    """Valor corrigido de uma linha com os coeficientes (a, b, atributo)."""
    a, b, atr = coef
    if atr == "reynolds":                       # a = L_ref (m); correção aditiva no CX0
        g = l["geo"]
        return l["spin"] + rn.delta_cx0(l["M"], g["VL"], g["VN"], g["VB"], g["OR"], g["DM"],
                                        l["d_mm"], a)
    tab = {**ATRIBUTOS, **ATRIBUTOS_GEOMETRICOS}
    f = tab[atr](l) if tab[atr] else 0.0
    d = a + b * f
    return l["spin"] * (1.0 + d) if tipo == "rel" else l["spin"] + d


def ajustar(L, tipo, atr):
    """MMQ ponderado: cada grupo pesa 1 no total."""
    if not L:
        return (0.0, 0.0, atr)
    n = {}
    for l in L:
        n[l["grupo"]] = n.get(l["grupo"], 0) + 1
    w = np.array([1.0 / n[l["grupo"]] for l in L])
    if atr == "reynolds":
        e = [np.sum(w * np.square([(l["med"] - aplicar(l, tipo, (x, 0.0, atr))) / l["spin"] for l in L]))
             for x in GRADE_LREF]
        return (float(GRADE_LREF[int(np.argmin(e))]), 0.0, "reynolds")
    y = np.array([alvo(l, tipo) for l in L])
    tab = {**ATRIBUTOS, **ATRIBUTOS_GEOMETRICOS}
    if tab[atr] is None or len(n) < 3:
        return (float(np.sum(w * y) / np.sum(w)), 0.0, "nenhum")
    X = np.c_[np.ones(len(L)), [tab[atr](l) for l in L]]
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    return (float(beta[0]), float(beta[1]), atr)


def erro_grupo(L, tipo, coef=None):
    """RMS do erro (relativo ou absoluto) de um conjunto de linhas; coef=None = SPIN-73 puro."""
    e = []
    for l in L:
        v = l["spin"] if coef is None else aplicar(l, tipo, coef)
        # relativo ao SPIN-73 (nunca zero; o Cmq medido chega a 0,0)
        e.append((l["med"] - v) / abs(l["spin"]) if tipo == "rel" else l["med"] - v)
    return float(np.sqrt(np.mean(np.square(e)))) if e else np.nan


def logo(L, tipo, atr, grupos):
    """Erro médio (por grupo) deixando cada grupo de fora, com o atributo fixo."""
    errs = []
    for g in grupos:
        tr = [l for l in L if l["grupo"] != g]
        te = [l for l in L if l["grupo"] == g]
        if te and len({l["grupo"] for l in tr}) >= 2:
            errs.append(erro_grupo(te, tipo, ajustar(tr, tipo, atr)))
    return float(np.mean(errs)) if errs else np.inf


def candidatos(coef_nome, geometricos=False):
    if coef_nome == "CX0":
        return ["reynolds"]
    return list(ATRIBUTOS) + (list(ATRIBUTOS_GEOMETRICOS) if geometricos else [])


def escolher(L, tipo, grupos, cands_nomes):
    """Atributo com menor erro de validação cruzada; 'sem correção' também concorre."""
    base = np.mean([erro_grupo([l for l in L if l["grupo"] == g], tipo) for g in grupos
                    if any(l["grupo"] == g for l in L)])
    cands = {atr: logo(L, tipo, atr, grupos) for atr in cands_nomes}
    melhor = min(cands, key=cands.get)
    return (None, cands) if base <= cands[melhor] else (melhor, cands)


def validar(ls, coef_nome, geometricos=False):
    """Validação cruzada aninhada por regime. Devolve {regime: (base, corrigido, n grupos, detalhe)}."""
    tipo = TIPO[coef_nome]
    cn = candidatos(coef_nome, geometricos)
    out = {}
    for reg, a, b in REGIMES:
        L = [l for l in ls if l["coef"] == coef_nome and a <= l["M"] < b]
        gs = [g for g in GRUPOS if any(l["grupo"] == g for l in L)]
        base, corr, det = [], [], {}
        for g in gs:
            tr = [l for l in L if l["grupo"] != g]
            te = [l for l in L if l["grupo"] == g]
            outros = [x for x in gs if x != g]
            atr, _ = escolher(tr, tipo, outros, cn) if len(outros) >= 3 else (None, {})
            c = ajustar(tr, tipo, atr) if atr else None
            eb, ec = erro_grupo(te, tipo), erro_grupo(te, tipo, c)
            base.append(eb); corr.append(ec); det[g] = (eb, ec, atr)
        out[reg] = (float(np.mean(base)) if base else np.nan,
                    float(np.mean(corr)) if corr else np.nan, len(gs), det)
    return out


def aceita(base, corr, det):
    """Regra de aceitação: generaliza para grupos não vistos.

    (1) erro médio menor que o do SPIN-73; (2) melhora em mais da metade dos grupos;
    (3) segurança: nenhum grupo deixado de fora fica com o erro mais que dobrado.
    O critério (3) foi acrescentado depois de ver o Cmq transônico, que passava em (1) e (2)
    piorando os dois 155 mm (M483A1: 35 % -> 126 %). Registrado aqui por transparência.
    """
    n = len(det)
    melhora = sum(1 for eb, ec, _ in det.values() if ec < eb)
    seguro = all(ec <= 2.0 * eb for eb, ec, _ in det.values())
    return bool(n >= 4 and corr < base and melhora > n / 2 and seguro), melhora


def ajuste_final(ls, validacao=None):
    """Com todos os grupos: só (coeficiente, regime) aceitos pela validação cruzada aninhada;
    o atributo é escolhido por validação cruzada em todos os grupos e os coeficientes, ajustados
    em todos. 'pior_razao' registra a margem: o maior erro corrigido/erro do SPIN-73 entre os
    grupos deixados de fora (a regra (3) corta em 2)."""
    validacao = validacao or {c: validar(ls, c) for c in APLICADOS}
    final = {}
    for c in APLICADOS:
        tipo = TIPO[c]
        final[c] = {}
        for reg, a, b in REGIMES:
            base, corr, n, det = validacao[c][reg]
            ok, melhora = aceita(base, corr, det) if n else (False, 0)
            L = [l for l in ls if l["coef"] == c and a <= l["M"] < b]
            gs = [g for g in GRUPOS if any(l["grupo"] == g for l in L)]
            atr, cands = escolher(L, tipo, gs, candidatos(c)) if ok else (None, {})
            pior = max((ec / eb for eb, ec, _ in det.values() if eb > 0), default=float("nan"))
            final[c][reg] = dict(tipo=tipo, atributo=atr,
                                 coef=list(ajustar(L, tipo, atr)) if atr else None,
                                 validacao=dict(spin73=round(base, 4), corrigido=round(corr, 4),
                                                grupos=n, grupos_que_melhoram=melhora, aceita=ok,
                                                pior_razao=round(pior, 3)))
    return final


def cpn_derivado(ls, final):
    """CPN = VCG − CMα/CNα com as correções ACEITAS no modelo final, reajustadas sem cada grupo."""
    out = {}
    for reg, a, b in REGIMES:
        base, corr, det = [], [], {}
        for g in GRUPOS:
            tr = [l for l in ls if l["grupo"] != g and a <= l["M"] < b]
            coefs = {}
            for c in ("CNA", "CMA"):
                if final[c][reg]["coef"]:
                    L = [l for l in tr if l["coef"] == c]
                    gs = [x for x in GRUPOS if x != g and any(l["grupo"] == x for l in L)]
                    atr, _ = escolher(L, TIPO[c], gs, candidatos(c))
                    coefs[c] = ajustar(L, TIPO[c], atr) if atr else None
            por = {}
            for l in ls:
                if l["grupo"] == g and a <= l["M"] < b:
                    por.setdefault(round(l["M"], 4), {})[l["coef"]] = l
            eb, ec = [], []
            for d in por.values():
                if "CPN" not in d:
                    continue
                lp = d["CPN"]
                m = dados._spin_no_mach(lp["proj"], lp["geo"], lp["M"])
                cna = aplicar(dict(lp, spin=m["CNA"]), "rel", coefs["CNA"]) if coefs.get("CNA") else m["CNA"]
                cma = aplicar(dict(lp, spin=m["CMA"]), "rel", coefs["CMA"]) if coefs.get("CMA") else m["CMA"]
                # base derivada do mesmo jeito (CMα/CNα interpolados), para não medir artefato de interpolação
                eb.append(lp["med"] - (lp["geo"]["VCG"] - m["CMA"] / m["CNA"]))
                ec.append(lp["med"] - (lp["geo"]["VCG"] - cma / cna))
            if eb:
                rb, rc = np.sqrt(np.mean(np.square(eb))), np.sqrt(np.mean(np.square(ec)))
                base.append(rb); corr.append(rc); det[g] = (rb, rc)
        det = {g: (rb, rc if abs(rc - rb) > 1e-9 else rb) for g, (rb, rc) in det.items()}
        out[reg] = (float(np.mean(base)), float(np.mean(corr)), len(det), det)
    return out


def cma_derivado(ls, final=None, fora=None):
    """CMα = (VCG − CPN)·CNα com CPN e CNα corrigidos, contra o CMα medido.
    Com fora=g, a correção é ajustada sem o grupo g (validação cruzada)."""
    por = {}
    for l in ls:
        por.setdefault((l["proj"], round(l["M"], 4)), {})[l["coef"]] = l
    res = {}
    for (proj, M), d in por.items():
        if "CMA" not in d:
            continue
        l = d["CMA"]
        g = l["grupo"]
        if fora is not None and g != fora:
            continue
        reg = regime(M)
        fin = final[g] if isinstance(final, dict) and g in final else final
        cna_l = dict(l, coef="CNA", spin=d["CNA"]["spin"] if "CNA" in d else _spin(l, "CNA"))
        cpn_l = dict(l, coef="CPN", spin=d["CPN"]["spin"] if "CPN" in d else _spin(l, "CPN"))
        cna, cpn = cna_l["spin"], cpn_l["spin"]
        if fin:
            fc, fp = fin["CNA"][reg], fin["CPN"][reg]
            if fc["coef"]:
                cna = aplicar(cna_l, "rel", tuple(fc["coef"]))
            if fp["coef"]:
                cpn = aplicar(cpn_l, "abs", tuple(fp["coef"]))
        cma = (l["geo"]["VCG"] - cpn) * cna
        res.setdefault((g, reg), []).append(((l["med"] - l["spin"]) / abs(l["med"]),
                                             (l["med"] - cma) / abs(l["med"])))
    return res


def _spin(l, c):
    m = dados._spin_no_mach(l["proj"], l["geo"], l["M"])
    return {"CNA": m["CNA"], "CPN": m["CPN"]}[c]


def main():
    ls = dados.linhas()
    print("Correção empírica do SPIN-73 — validação cruzada deixando um grupo de fora (aninhada)")
    print("Erro = RMS por grupo, média entre grupos; relativo ao SPIN-73 (%) para CX0, CNα, CMα, Cmq;")
    print("absoluto para Magnus (pd/2V) e CPN (cal). 'corrigido' = predição para o grupo deixado de")
    print("fora, com atributo e coeficientes ajustados só nos outros grupos. 'pior' = maior razão")
    print("corrigido/SPIN-73 entre os grupos deixados de fora (a regra rejeita acima de 2).\n")
    val = {}
    for c, tipo in TIPO.items():
        val[c] = validar(ls, c)
        esc = 100.0 if tipo == "rel" else 1.0
        un = "%" if tipo == "rel" else ("cal" if c == "CPN" else "")
        for reg, (b, cc, n, det) in val[c].items():
            if n == 0:
                continue
            ok, melhora = aceita(b, cc, det)
            pior = max(ec / eb for eb, ec, _ in det.values() if eb > 0)
            marca = ("ACEITA" if ok else "rejeitada") if c in APLICADOS else "(correção direta, não usada)"
            print(f"{c:5s} {reg:12s} grupos {n}  SPIN-73 {b * esc:7.2f}{un:3s} corrigido {cc * esc:7.2f}{un:3s}"
                  f"  melhora em {melhora}/{n}  pior {pior:4.2f}  {marca}")
    final = ajuste_final(ls, {c: val[c] for c in APLICADOS})
    print("\nCPN derivado (VCG − CMα/CNα, com as correções aceitas refeitas sem o grupo de fora):")
    for reg, (b, cc, n, det) in cpn_derivado(ls, final).items():
        print(f"CPN   {reg:12s} grupos {n}  SPIN-73 {b:7.3f}cal corrigido {cc:7.3f}cal  melhora em "
              f"{sum(1 for eb, ec in det.values() if ec < eb)}/{n}")
    # o resultado vai para a biblioteca, que o aplica (spin73.correcoes.VooLivre)
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=1)
    print("\nModelo final (todos os grupos), aplicado por spin73.Aerodinamica(..., correcoes='voo_livre'):")
    for c, regs in final.items():
        for reg, d in regs.items():
            if d["coef"]:
                a, b, atr = d["coef"]
                if atr == "reynolds":
                    print(f"  {c:5s} {reg:12s} atrito de parede, L_ref = {a:.3f} m")
                else:
                    print(f"  {c:5s} {reg:12s} {d['tipo']}: a = {a:+.4f}" + (f", b = {b:+.4f} · {atr}" if atr != "nenhum" else ""))
            else:
                print(f"  {c:5s} {reg:12s} sem correção")
    return val, final


if __name__ == "__main__":
    main()
