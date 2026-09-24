"""Interface das correções e a etapa final que mantém as colunas coerentes.

Uma correção é qualquer objeto com

    nome: str
    aplicar(t: dict, p: Projetil, ctx: Contexto) -> dict

que recebe a tabela na convenção do SPIN-73 (um array de 17 valores por coluna, na grade
MACH_GRID) e devolve uma tabela nova. Correções se encadeiam na ordem dada; ao fim,
`finalizar` recalcula o que é derivado (CPN, CPF, CX2, estabilidade), para que nenhuma
correção precise saber das outras.

Para criar uma correção nova, herde de Correcao (ou só implemente os dois membros acima) e,
se quiser chamá-la por nome, registre-a em aeroballistics.correcoes.registrar().
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .. import nucleo as _n

REGIMES = (("subsônico", 0.0, 0.9), ("transônico", 0.9, 1.25), ("supersônico", 1.25, 9.0))


def regime(M: float) -> str:
    return next(n for n, a, b in REGIMES if a <= M < b)


@dataclass
class Contexto:
    """O que uma correção pode precisar além da geometria em calibres."""
    d_mm: float | None = None           # diâmetro real, mm (escala; o SPIN-73 não usa)

    def exigir_escala(self, quem: str) -> float:
        if self.d_mm is None or not self.d_mm > 0:
            raise ValueError(f"a correção '{quem}' depende do tamanho real: informe d_mm "
                             "ou o diâmetro no Projetil (DIA, em polegadas)")
        return self.d_mm


class Correcao:
    """Base opcional. Subclasses implementam `aplicar`."""
    nome = "correcao"
    descricao = ""

    def aplicar(self, t: dict, p: _n.Projetil, ctx: Contexto) -> dict:     # pragma: no cover
        raise NotImplementedError

    def __repr__(self):
        return f"<{type(self).__name__} {self.nome}>"


def copiar(t: dict) -> dict:
    return {k: np.array(v, float, copy=True) for k, v in t.items()}


def finalizar(t0: dict, t: dict, p: _n.Projetil) -> dict:
    """Recalcula as colunas derivadas depois das correções.

    CPN  = VCG − CMα/CNα                 (definição do momento em torno do CG)
    CPF1 = VCG − CNPA/CYPA, CPF5 idem    (idem, Magnus)
    CX2  = (CX2 + CNα)_original − CNα    (o arrasto de guinada CX2 + CNα não é corrigido)
    estabilidade: recalculada com os coeficientes corrigidos, se houver massa e passo.
    """
    t = copiar(t)
    mudou = lambda c: not np.allclose(t[c], t0[c], equal_nan=True)
    if mudou("CMA") or mudou("CNA"):
        t["CPN"] = p.VCG - t["CMA"] / t["CNA"]
    if mudou("CNA"):
        t["CX2"] = t0["CX2"] + t0["CNA"] - t["CNA"]
    if mudou("CNPA") or mudou("CYPA"):
        t["CPF1"] = p.VCG - t["CNPA"] / t["CYPA"]
    if mudou("CNPA5") or mudou("CYPA"):
        t["CPF5"] = p.VCG - t["CNPA5"] / t["CYPA"]
    if "GYRO" in t0:
        with np.errstate(invalid="ignore", divide="ignore"):
            t.update(_n.estabilidade(p, t["MACH"], t["CX"], t["CNA"], t["CMA"], t["CNPA"],
                                     t["CNPA5"], t["CMQ"], t["CLP"]))
    return t
