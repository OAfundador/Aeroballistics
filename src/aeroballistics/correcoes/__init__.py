"""Correções opcionais sobre o aeroballistics (aeroballistics.correcoes).

Nada aqui é usado por padrão: sem correção, a biblioteca devolve o programa de 1973.

    from aeroballistics import correcoes
    correcoes.disponiveis()                  # nomes registrados
    correcoes.resolver("voo_livre")          # -> [VooLivre()]
    correcoes.resolver("voo_livre:CX0")      # só o atrito
    correcoes.registrar("minha", MinhaCorrecao)   # para chamar por nome depois

Uma correção nova é qualquer objeto com `nome` e `aplicar(t, p, ctx) -> t` (ver base.py).
"""
from __future__ import annotations

from typing import Callable, Iterable

from .base import REGIMES, Contexto, Correcao, finalizar, regime
from .voo_livre import AtritoReynolds, ViesEmpirico, VooLivre

_REGISTRO: dict[str, Callable[..., Correcao]] = {
    "voo_livre": VooLivre,
}


def registrar(nome: str, fabrica: Callable[..., Correcao]) -> None:
    """Associa um nome a uma fábrica de correção (classe ou função sem argumentos
    obrigatórios). O sufixo ':A,B' no nome, se houver, vira coeficientes=('A','B')."""
    _REGISTRO[nome] = fabrica


def disponiveis() -> list[str]:
    return sorted(_REGISTRO)


def resolver(spec) -> list[Correcao]:
    """Aceita None, um nome ('voo_livre', 'voo_livre:CX0,CNA'), um objeto de correção ou
    uma lista misturando os dois."""
    if spec is None or spec == () or spec == []:
        return []
    if isinstance(spec, str) or hasattr(spec, "aplicar"):
        spec = [spec]
    out = []
    for s in spec:
        if isinstance(s, str):
            nome, _, coefs = s.partition(":")
            if nome not in _REGISTRO:
                raise KeyError(f"correção '{nome}' não registrada; disponíveis: {disponiveis()}")
            fab = _REGISTRO[nome]
            out.append(fab(coeficientes=tuple(c.strip() for c in coefs.split(","))) if coefs else fab())
        elif hasattr(s, "aplicar"):
            out.append(s)
        else:
            raise TypeError(f"não sei aplicar {s!r} como correção")
    return out


def aplicar(t: dict, p, correcoes: Iterable[Correcao], ctx: Contexto) -> dict:
    """Aplica a cadeia de correções e recalcula as colunas derivadas."""
    correcoes = list(correcoes)
    t0 = t
    for c in correcoes:
        t = c.aplicar(t, p, ctx)
    return finalizar(t0, t, p) if correcoes else t


__all__ = ["Contexto", "Correcao", "REGIMES", "regime", "finalizar", "AtritoReynolds",
           "ViesEmpirico", "VooLivre", "registrar", "disponiveis", "resolver", "aplicar"]
