"""Interface para simuladores (6DOF): coeficientes em qualquer Mach.

    import aeroballistics
    p = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
    aero = aeroballistics.Aerodinamica(p)                               # o SPIN-73 de 1973
    aero = aeroballistics.Aerodinamica(p, correcoes="voo_livre")        # com a correção de voo livre
    aero = aeroballistics.Aerodinamica(p, convencao="moderna")          # pd/V, qd/V, CLα, CDδ²

    c = aero(2.3)            # Coeficientes: c.CX0, c["CNA"], ...  (floats)
    c = aero(mach_array)     # o mesmo, com arrays (vetorizado)
    aero.nomes               # colunas disponíveis na convenção escolhida

Toda a aerodinâmica é calculada uma vez, na grade de 17 Mach do programa, no construtor. Cada
chamada só interpola (linear em Mach, como o próprio SPIN-73 é tabelado), então pode ser
usada dentro do laço de integração.

Convenções (ver aeroballistics/convencoes.py):
  "spin73"   a do relatório: pd/2V e qd/2V, CX2 por sen²α, derivadas por sen α, CPN e CPF
             em calibres do nariz, momentos em torno do CG.
  "moderna"  pd/V e qd/V (Cmq, Clp e Magnus valem a METADE), CDδ² = CX2 + CNα, CLα = CNα − CX0.

Fora da grade (Mach < 0,01 ou > 5): fora_da_faixa = "limitar" (usa o extremo, padrão),
"nan" ou "erro".
"""
from __future__ import annotations

import numpy as np

from . import convencoes as _cv
from . import correcoes as _corr
from . import nucleo as _n

# Colunas aerodinâmicas na convenção do SPIN-73 (nome exposto -> coluna da tabela)
_SPIN73 = {
    "CX0": "CX",        # força axial a guinada zero
    "CX2": "CX2",       # força axial de guinada, por sen²α (arrasto de guinada = CX2 + CNA)
    "CNA": "CNA",       # força normal, por sen α
    "CMA": "CMA",       # momento de arfagem em torno do CG, por sen α (positivo tomba)
    "CPN": "CPN",       # centro de pressão da força normal, calibres do nariz
    "CYPA": "CYPA",     # força de Magnus, pd/2V, por sen α
    "CNPA": "CNPA",     # momento de Magnus a 1°, pd/2V, por sen α
    "CNPA5": "CNPA5",   # inclinação secante do momento de Magnus a 5°
    "CPF1": "CPF1",     # centro de pressão da força de Magnus a 1°, calibres do nariz
    "CPF5": "CPF5",     # idem a 5°
    "CMQ": "CMQ",       # amortecimento em arfagem (Cmq + Cmα̇), qd/2V
    "CLP": "CLP",       # amortecimento de rolamento, pd/2V
}


class Coeficientes(dict):
    """Dicionário com acesso por atributo: c.CX0 == c["CX0"]."""

    def __getattr__(self, nome):
        try:
            return self[nome]
        except KeyError:
            raise AttributeError(nome) from None


class Aerodinamica:
    """Coeficientes aerodinâmicos de um projétil, prontos para um integrador de trajetória.

    Parâmetros
    ----------
    projetil     aeroballistics.Projetil (geometria em calibres; DIA em polegadas, se houver)
    correcoes    None (padrão: o SPIN-73 puro), um nome registrado ("voo_livre",
                 "voo_livre:CX0"), um objeto de correção ou uma lista deles
    d_mm         diâmetro real em mm; se omitido, sai de projetil.DIA. Só é exigido por
                 correções que dependem de escala.
    dados        aeroballistics.CoefAjuste alternativo (outros blocos DATA); padrão: os do listing
    convencao    "spin73" ou "moderna"
    fora_da_faixa  "limitar", "nan" ou "erro"
    """

    GRADE = _n.MACH_GRID

    def __init__(self, projetil: _n.Projetil, correcoes=None, *, d_mm: float | None = None,
                 dados: _n.CoefAjuste | None = None, convencao: str = "spin73",
                 fora_da_faixa: str = "limitar"):
        if convencao not in ("spin73", "moderna"):
            raise ValueError("convencao deve ser 'spin73' ou 'moderna'")
        if fora_da_faixa not in ("limitar", "nan", "erro"):
            raise ValueError("fora_da_faixa deve ser 'limitar', 'nan' ou 'erro'")
        self.projetil = projetil
        self.convencao = convencao
        self.fora_da_faixa = fora_da_faixa
        if d_mm is None and projetil.DIA > 0:
            d_mm = projetil.DIA * 25.4
        self.contexto = _corr.Contexto(d_mm=d_mm)
        self.correcoes = _corr.resolver(correcoes)
        self.tabela_original = _n.tabela(projetil, dados)
        self.tabela = _corr.aplicar(self.tabela_original, projetil, self.correcoes, self.contexto)
        self._grade = self._na_convencao(self.tabela)

    # ------------------------------------------------------------------ consulta
    def _na_convencao(self, t: dict) -> dict:
        if self.convencao == "spin73":
            return {k: np.asarray(t[c], float) for k, c in _SPIN73.items()}
        m = _cv.para_moderno(t, VL=self.projetil.VL)
        m.pop("MACH")
        return m

    @property
    def nomes(self) -> list[str]:
        return list(self._grade)

    def _mach(self, mach):
        M = np.asarray(mach, float)
        fora = (M < self.GRADE[0]) | (M > self.GRADE[-1])
        if np.any(fora) and self.fora_da_faixa == "erro":
            raise ValueError(f"Mach fora da grade do SPIN-73 ({self.GRADE[0]} a {self.GRADE[-1]})")
        return M, fora

    def coeficiente(self, nome: str, mach):
        """Um coeficiente no(s) Mach pedido(s)."""
        M, fora = self._mach(mach)
        v = np.interp(M, self.GRADE, self._grade[nome])
        if self.fora_da_faixa == "nan" and np.any(fora):
            v = np.where(fora, np.nan, v)
        return float(v) if np.ndim(v) == 0 else v

    def __call__(self, mach) -> Coeficientes:
        """Todos os coeficientes no(s) Mach pedido(s)."""
        return Coeficientes({k: self.coeficiente(k, mach) for k in self._grade})

    def momento_magnus(self, mach, alfa_rad):
        """Coeficiente do momento de Magnus (secante) no ângulo de ataque total α.

        Interpolação linear em sen²α entre as duas inclinações secantes que o SPIN-73
        calcula (CNPA a 1° e CNPA-5 a 5°); constante fora de [1°, 5°]. É uma leitura dos
        valores do programa, não uma equação dele: o polinômio impresso (CNPA3, CNPA5)
        tem um defeito no original (NOTAS_TRANSCRICAO, T12) e não é usado aqui.
        """
        c1 = self.coeficiente("CNPA" if self.convencao == "spin73" else "Cmpa", mach)
        c5 = self.coeficiente("CNPA5" if self.convencao == "spin73" else "Cmpa_5graus", mach)
        s1, s5 = np.sin(np.radians(1.0)) ** 2, np.sin(np.radians(5.0)) ** 2
        w = np.clip((np.sin(np.asarray(alfa_rad, float)) ** 2 - s1) / (s5 - s1), 0.0, 1.0)
        return c1 + w * (c5 - c1)

    # ------------------------------------------------------------------ descrição
    def descrever(self) -> str:
        p = self.projetil
        linhas = [f"aeroballistics (adaptado do SPIN-73) — {p.nome or 'projétil'} (VL {p.VL}, VN {p.VN}, VB {p.VB}, "
                  f"VCG {p.VCG} cal)", f"convenção: {self.convencao}"]
        if self.correcoes:
            for c in self.correcoes:
                linhas.append(f"correção: {c.nome} — {getattr(c, 'descricao', '')}")
        else:
            linhas.append("sem correção (programa de 1973)")
        if self.contexto.d_mm:
            linhas.append(f"diâmetro: {self.contexto.d_mm:.2f} mm")
        return "\n".join(linhas)

    def __repr__(self):
        return f"<Aerodinamica {self.projetil.nome or 'projétil'} {self.convencao} " \
               f"correcoes={[c.nome for c in self.correcoes]}>"


__all__ = ["Aerodinamica", "Coeficientes"]
