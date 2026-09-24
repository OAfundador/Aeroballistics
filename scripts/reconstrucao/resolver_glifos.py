"""Resolve glifos ambíguos de uma leitura SÓ pelas identidades entre colunas impressas.

Na leitura (data/tabelas_1973/leituras/pNN_*.txt), cada célula é escrita como foi vista, com classes:
    A      = 6 ou 8 (na impressão matricial os dois saem quase iguais)
    [xy]   = um dos dígitos listados, por exemplo [13] ou [27]
    ?      = dígito ilegível (qualquer um)
    vazio  = célula ilegível
Linhas de comentário (#) com "entrada:", "decidir:", "cabecalho:" etc. são copiadas.

Para cada linha de Mach, as células ligadas por identidades formam grupos
    (CNA, CMA, CPN)                       CMA = (VCG − CPN)·CNA
    (CYPA, CPF1, CNPA, CPF5, CNPA5)       CNPA = CYPA·(VCG − CPF1); CNPA5 = CYPA·(VCG − CPF5)
    (CNPA3, CNPA5P)                       CNPA3 + 0,1·CNPA5P = 3,75
e todas as combinações de leitura são testadas. Uma célula ambígua que sai com o MESMO
valor em todas as combinações consistentes fica resolvida, e é marcada "identidade" (fora
das contagens de validação). Nenhum DATA e nenhum resultado do modelo entram aqui.

    python scripts/reconstrucao/resolver_glifos.py 41   -> data/tabelas_1973/p41_*.csv
"""
import itertools
import os
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caminhos                                             # noqa: E402

TABELAS = caminhos.TABELAS_1973
COLS = ["MACH", "CX", "CX2", "CNA", "CMA", "CPN", "CYPA", "CNPA", "CNPA3", "CNPA5P",
        "CPF1", "CPF5", "CNPA5", "CMQ", "CLP"]
GRUPOS = [("CNA", "CMA", "CPN"), ("CYPA", "CPF1", "CNPA", "CPF5", "CNPA5"), ("CNPA3", "CNPA5P")]
LIMITE = 20000


def alternativas(cel):
    """Todas as leituras possíveis de uma célula (lista de strings numéricas)."""
    if not cel:
        return []
    partes = re.findall(r"\[[0-9]+\]|A|\?|.", cel)
    opcoes = []
    for p in partes:
        if p == "A":
            opcoes.append("68")
        elif p == "?":
            opcoes.append("0123456789")
        elif p.startswith("["):
            opcoes.append(p[1:-1])
        else:
            opcoes.append(p)
    return ["".join(c) for c in itertools.product(*opcoes)]


def _ok(v, vcg):
    """Identidades do grupo com as células presentes (tolerância de arredondamento)."""
    g = v.get
    if vcg is not None and all(k in v for k in ("CNA", "CMA", "CPN")):
        if abs(g("CMA") - (vcg - g("CPN")) * g("CNA")) > 0.0005 * (1 + g("CNA") + abs(vcg - g("CPN"))):
            return False
    for cpf, cn in (("CPF1", "CNPA"), ("CPF5", "CNPA5")):
        if vcg is not None and all(k in v for k in ("CYPA", cpf, cn)):
            if abs(g(cn) - g("CYPA") * (vcg - g(cpf))) > 0.0005 * (1 + abs(g("CYPA")) + abs(vcg - g(cpf))):
                return False
    if "CNPA3" in v and "CNPA5P" in v:
        if abs(g("CNPA3") + 0.1 * g("CNPA5P") - 3.75) > 0.0006:
            return False
    return True


def resolver(celulas, vcg):
    """celulas: {coluna: texto lido}. Devolve {coluna: (valor|None, 'lido'|'identidade'|motivo)}."""
    out = {}
    for c, txt in celulas.items():
        alts = alternativas(txt)
        if len(alts) == 1:
            out[c] = (float(alts[0]), "lido")
    for grupo in GRUPOS:
        amb = {c: alternativas(celulas[c]) for c in grupo if celulas.get(c) and len(alternativas(celulas[c])) > 1}
        if not amb:
            continue
        fixos = {c: out[c][0] for c in grupo if c in out}
        n = int(np.prod([len(a) for a in amb.values()]))
        if n > LIMITE:
            for c in amb:
                out[c] = (None, f"ambíguo: {celulas[c]}")
            continue
        validas = []
        for combo in itertools.product(*amb.values()):
            v = {**fixos, **{c: float(x) for c, x in zip(amb, combo)}}
            if _ok(v, vcg):
                validas.append(dict(zip(amb, combo)))
        for c in amb:
            valores = {d[c] for d in validas}
            if len(valores) == 1:
                out[c] = (float(valores.pop()), f"identidade: {celulas[c]}")
            else:
                out[c] = (None, f"ambíguo: {celulas[c]}" + (" (nenhuma leitura fecha as identidades)"
                                                              if not validas else ""))
    for c, txt in celulas.items():
        if c not in out and txt:
            out[c] = (None, f"ambíguo: {txt}")
    return out


def converter(pagina):
    (leitura,) = [f for f in os.listdir(TABELAS / "leituras") if f.startswith(f"p{pagina:02d}_")]
    linhas = open(TABELAS / "leituras" / leitura, encoding="utf-8").read().splitlines()
    cabeca = [l for l in linhas if l.startswith("#")]
    vcg = None
    for l in cabeca:
        m = re.search(r"(?:entrada:.*\b|decidido: )VCG=([\d.]+)", l)
        if m:
            vcg = float(m.group(1))
    dados = [l for l in linhas if l.strip() and not l.startswith("#")]
    assert dados[0].split(",") == COLS, dados[0]
    ident, duv, tabela = [], [], []
    for l in dados[1:]:
        campos = [x.strip() for x in l.split(",")]
        mach = campos[0]
        res = resolver(dict(zip(COLS[1:], campos[1:])), vcg)
        linha = [mach]
        for c in COLS[1:]:
            v, como = res.get(c, (None, ""))
            if v is None:
                linha.append("")
                if como:
                    duv.append(f"# duvidosa: {c} {mach} {como.split(': ', 1)[1]} | não resolvido pelas identidades")
            else:
                casas = len(alternativas(campos[COLS.index(c)])[0].split(".")[-1])
                linha.append(f"{v:.{casas}f}")
                if como.startswith("identidade"):
                    ident.append(f"# identidade: {c} {mach} {como.split(': ', 1)[1]} -> {v:.{casas}f} | "
                                 "única leitura que fecha as identidades entre colunas impressas")
        tabela.append(",".join(linha))
    saida = TABELAS / leitura.replace(".txt", ".csv")
    with open(saida, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(cabeca) + "\n#\n# Gerado por resolver_glifos.py a partir de leituras/" + leitura + "\n#\n")
        f.write("\n".join(ident + ["#"] + duv) + "\n")
        f.write(",".join(COLS) + "\n" + "\n".join(tabela) + "\n")
    return saida, len(ident), len(duv)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for pag in map(int, sys.argv[1:]):
        print(converter(pag))
