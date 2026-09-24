"""aeroballistics: coeficientes aerodinâmicos de projéteis estabilizados por rotação, inspirado e adaptado do SPIN-73 (Whyte, 1973).

CANÔNICO -- o núcleo que segue o programa de 1973, sem nada acrescentado:

    aeroballistics.nucleo      as equações, tabela(), estabilidade(), o cartão de entrada (Projetil)
    aeroballistics.dados       os blocos DATA XA..XG, com a proveniência de cada valor
    Aerodinamica(p)            sem opções, é a tabela canônica interpolada em Mach
    aeroballistics.programa    o programa original descrito como objetos, bloco a bloco

ADIÇÕES OPCIONAIS -- nenhuma é aplicada sem ser pedida, e nenhuma altera o canônico:

    aeroballistics.convencoes  saída na convenção moderna (pd/V, qd/V, CLα...): conversão exata
    aeroballistics.unidades    entrada em mm, g, g·cm², °C, CG a partir da base: conversão exata
    aeroballistics.massa       estima CG, massa e inércias que faltam no cartão (sólido homogêneo ou
                               fórmulas de Hitchcock, BRL 620); muda ENTRADAS, não o modelo
    aeroballistics.correcoes   correções dos coeficientes (voo_livre, ajustada a medições de voo livre)
                               e a interface para escrever novas; muda SAÍDAS

Uso típico num simulador:

    import aeroballistics
    p = aeroballistics.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
    aero = aeroballistics.Aerodinamica(p, convencao="moderna")          # canônico
    c = aero(mach)            # c.CD0, c.CNa, c.Cma, c.Cmq_Cmad, c.Clp, c.Cmpa, ...

Tudo o que o antigo módulo único exportava continua disponível aqui (tabela, formatar,
Projetil, M437...), para não quebrar código existente.
"""
from . import convencoes, correcoes, dados, massa, nucleo, programa, unidades
from .aero import Aerodinamica, Coeficientes
from .cli import main as _main
from .nucleo import *                                   # noqa: F401,F403
from .nucleo import __all__ as _nucleo_all

__version__ = "0.5.0"

__all__ = ["Aerodinamica", "Coeficientes", "convencoes", "correcoes", "dados", "massa",
           "nucleo", "programa", "unidades",
           *_nucleo_all]
