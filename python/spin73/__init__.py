"""SPIN-73 reconstruído, como biblioteca.

Camadas (cada uma pode ser usada sem as de cima):

    spin73.nucleo      o programa de 1973: equações, blocos DATA, tabela(), estabilidade()
    spin73.dados       os blocos DATA XA..XG, com a proveniência de cada valor
    spin73.convencoes  convenção do relatório (pd/2V, qd/2V...) <-> moderna (pd/V, qd/V...)
    spin73.correcoes   correções OPCIONAIS (nenhuma é aplicada por padrão) e a interface
                       para escrever novas
    spin73.aero        Aerodinamica: coeficientes em qualquer Mach, para um 6DOF

Uso típico num simulador:

    import spin73
    p = spin73.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DIA=0.224)
    aero = spin73.Aerodinamica(p, correcoes="voo_livre", convencao="moderna")
    c = aero(mach)            # c.CD0, c.CNa, c.Cma, c.Cmq_Cmad, c.Clp, c.Cmpa, ...

Tudo o que o módulo antigo `spin73.py` exportava continua disponível aqui (tabela, formatar,
Projetil, M437...), para não quebrar código existente.
"""
from . import convencoes, correcoes, dados, nucleo
from .aero import Aerodinamica, Coeficientes
from .cli import main as _main
from .nucleo import *                                   # noqa: F401,F403
from .nucleo import __all__ as _nucleo_all

__version__ = "0.2.0"

__all__ = ["Aerodinamica", "Coeficientes", "convencoes", "correcoes", "dados", "nucleo",
           *_nucleo_all]
