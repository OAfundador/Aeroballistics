"""Tabelas de saída do SPIN-73 transcritas do relatório, uma por arquivo em `tabelas/`.

Cada CSV traz, em linhas de comentário, a entrada impressa no cabeçalho da tabela e as
células que exigiram decisão:

    # entrada: VL=5.580 VN=2.900 ...                   geometria e massa (argumentos de Projetil)
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

import spin73 as s

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tabelas")


@dataclass
class TabelaImpressa:
    pagina: int
    nome: str
    arquivo: str
    entrada: dict
    colunas: dict
    identidade: dict = field(default_factory=dict)    # (coluna, Mach) -> texto
    duvidosas: dict = field(default_factory=dict)     # (coluna, Mach) -> texto

    def projetil(self, **mudancas) -> s.Projetil:
        return s.Projetil(nome=self.nome, **{**self.entrada, **mudancas})


def _chave(col, mach):
    return col, round(float(mach), 2)


def ler(caminho: str) -> TabelaImpressa:
    entrada, ident, duv, dados, nome = {}, {}, {}, [], ""
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
            elif txt.startswith("identidade:") or txt.startswith("duvidosa:"):
                corpo = txt.split(":", 1)[1].strip()
                col, mach = corpo.split()[:2]
                (ident if txt.startswith("identidade") else duv)[_chave(col, mach)] = corpo
    rd = csv.DictReader(dados)
    linhas = list(rd)
    colunas = {c: np.array([float(r[c]) if r[c].strip() else np.nan for r in linhas])
               for c in rd.fieldnames}
    pagina = int(re.match(r"p(\d+)", os.path.basename(caminho)).group(1))
    return TabelaImpressa(pagina, nome, caminho, entrada, colunas, ident, duv)


def carregar(pagina: int) -> TabelaImpressa:
    (arq,) = glob.glob(os.path.join(DIR, f"p{pagina:02d}_*.csv"))
    return ler(arq)


def todas() -> list:
    return [ler(a) for a in sorted(glob.glob(os.path.join(DIR, "p*.csv")))]
