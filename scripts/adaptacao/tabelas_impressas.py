"""Tabelas de saída do SPIN-73 transcritas do relatório, uma por arquivo em `data/tabelas_1973/`.

Cada CSV traz, em linhas de comentário, a entrada impressa no cabeçalho da tabela e as
células que exigiram decisão:

    # entrada: VL=5.580 VN=2.900 ...                   geometria e massa (argumentos de Projetil)
    # decidir: VN 1.40 2.00 CNA | motivo                entrada ilegível: decidida pela coluna
                                                        indicada, dentro do intervalo; essa coluna
                                                        fica CIRCULAR nesta tabela
    # identidade: COLUNA MACH leitura -> valor | motivo   resolvida por identidade entre
                                                        colunas impressas (fora das contagens)
    # duvidosa: COLUNA MACH leitura | motivo            deixada vazia no CSV

    tb = carregar(50)
    tb.projetil()          # Projetil com a entrada impressa
    tb.colunas["CPN"]      # array de 17 valores (NaN = ilegível)
"""
import csv
import glob
import os
import re
from dataclasses import dataclass, field

import numpy as np

import caminhos
import aeroballistics as s

DIR = str(caminhos.TABELAS_1973)


@dataclass
class TabelaImpressa:
    pagina: int
    nome: str
    arquivo: str
    entrada: dict
    colunas: dict
    identidade: dict = field(default_factory=dict)    # (coluna, Mach) -> texto
    duvidosas: dict = field(default_factory=dict)     # (coluna, Mach) -> texto
    decidir: dict = field(default_factory=dict)       # entrada -> (min, max, coluna, texto)
    _decididas: dict = field(default=None, repr=False)

    def decididas(self) -> dict:
        """Entradas ilegíveis decididas pelo modelo: {nome: valor}, com 3 casas (as do cabeçalho)."""
        if self._decididas is None:
            self._decididas = _decidir(self) if self.decidir else {}
        return self._decididas

    def projetil(self, **mudancas) -> s.Projetil:
        return s.Projetil(nome=self.nome, **{**self.entrada, **self.decididas(), **mudancas})

    def circulares(self) -> set:
        """(coluna, Mach) usadas para decidir entradas: não validam nada nesta tabela.
        Colunas presas a elas por identidade (as de Magnus) vão junto."""
        cols = {c for (_, _, c, _) in self.decidir.values()}
        for c in list(cols):
            cols |= LIGADAS.get(c, set())
        return {(c, round(float(m), 2)) for c in cols for m in s.MACH_GRID}


# Colunas que são função direta de outra: decidir uma entrada por uma delas tira as demais
# da validação. CNPA = CYPA·(VCG − CPF1), CNPA5 = CYPA·(VCG − CPF5), e CNPA3/CNPA5P saem
# de CNPA e CNPA5 (NOTAS, T12).
_MAGNUS = {"CYPA", "CPF1", "CPF5", "CNPA", "CNPA5", "CNPA3", "CNPA5P"}
LIGADAS = {c: _MAGNUS for c in _MAGNUS}


def _decidir(tb, voltas=3):
    """Cada entrada ilegível é ajustada à SUA coluna (mínimo desvio absoluto nas células
    legíveis), com as demais fixas; repete algumas voltas porque elas interagem."""
    atual = {v: 0.5 * (lo + hi) for v, (lo, hi, _, _) in tb.decidir.items()}

    def custo(var, x):
        col = tb.decidir[var][2]
        p = s.Projetil(nome=tb.nome, **{**tb.entrada, **atual, var: x})
        calc = s.tabela(p)[col]
        imp = tb.colunas[col]
        # células resolvidas por identidade também valem aqui: são valores impressos,
        # desambiguados sem modelo (só ficam fora das contagens de validação)
        ok = [j for j in range(len(s.MACH_GRID)) if np.isfinite(imp[j])]
        return float(np.sum(np.abs(calc[ok] - imp[ok])))       # L1: robusto a uma célula ruim

    fixos = {v: lo for v, (lo, hi, _, _) in tb.decidir.items() if lo == hi}
    atual.update(fixos)
    atual = {v: x for v, x in atual.items() if "#" not in v}
    for _ in range(voltas):
        for var, (lo, hi, _, _) in tb.decidir.items():
            if lo == hi:
                continue
            grade = np.linspace(lo, hi, 81)
            k = int(np.argmin([custo(var, x) for x in grade]))
            a, b = grade[max(k - 1, 0)], grade[min(k + 1, 80)]
            for _ in range(40):                           # seção áurea no intervalo vizinho
                c, d = b - 0.618 * (b - a), a + 0.618 * (b - a)
                if custo(var, c) < custo(var, d):
                    b = d
                else:
                    a = c
            atual[var] = 0.5 * (a + b)
    return {v: round(x, 3) for v, x in atual.items()}


def _chave(col, mach):
    return col, round(float(mach), 2)


def ler(caminho: str) -> TabelaImpressa:
    entrada, ident, duv, dec, dados, nome = {}, {}, {}, {}, [], ""
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if not linha.startswith("#"):
                dados.append(linha)
                continue
            txt = linha[1:].strip()
            if not nome:
                nome = txt.split(" -- ")[0].strip()
            if txt.startswith("entrada:"):
                for k, v in re.findall(r"(\w+)=([-\d.]+)", txt):
                    entrada[k] = float(v)
            elif txt.startswith("decidir:"):
                var, lo, hi, col = txt.split(":", 1)[1].split("|")[0].split()
                dec[var] = (float(lo), float(hi), col, txt.split("|", 1)[-1].strip())
            elif txt.startswith("decidido:"):
                # valor já decidido em outra etapa, pelas colunas listadas (circulares aqui)
                atrib, cols = txt.split(":", 1)[1].split("|")[0].split()
                var, val = atrib.split("=")
                for i, col in enumerate(cols.split(",")):
                    dec[var if i == 0 else f"{var}#{i}"] = (float(val), float(val), col,
                                                            txt.split("|", 1)[-1].strip())
            elif txt.startswith("identidade:") or txt.startswith("duvidosa:"):
                corpo = txt.split(":", 1)[1].strip()
                col, mach = corpo.split()[:2]
                (ident if txt.startswith("identidade") else duv)[_chave(col, mach)] = corpo
    rd = csv.DictReader(dados)
    linhas = list(rd)
    colunas = {c: np.array([float(r[c]) if r[c].strip() else np.nan for r in linhas])
               for c in rd.fieldnames}
    pagina = int(re.match(r"p(\d+)", os.path.basename(caminho)).group(1))
    return TabelaImpressa(pagina, nome, caminho, entrada, colunas, ident, duv, dec)


def carregar(pagina: int) -> TabelaImpressa:
    (arq,) = glob.glob(os.path.join(DIR, f"p{pagina:02d}_*.csv"))
    return ler(arq)


def todas() -> list:
    return [ler(a) for a in sorted(glob.glob(os.path.join(DIR, "p*.csv")))]
