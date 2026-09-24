"""Linha de comando: python -m aeroballistics (ou o comando `aeroballistics`, depois de instalado).

Sem opções de adição, a saída é a CANÔNICA: o SPIN-73 de 1973 com o cartão dado. As adições
(--estimar-massa, --correcao) são opcionais e aparecem no cabeçalho quando usadas.
"""
from __future__ import annotations

import sys

from . import correcoes as _corr
from . import massa as _massa
from . import unidades as _un
from .aero import Aerodinamica
from .nucleo import M437, Projetil, avisos, formatar, salvar_csv

# (opção, chave, ajuda); as do cartão do SPIN-73 primeiro, depois as alternativas
CARTAO = (
    ("--VL", "VL", "comprimento total, cal"), ("--VN", "VN", "comprimento da ogiva, cal"),
    ("--VB", "VB", "comprimento do boattail, cal (0 = base reta)"),
    ("--VCG", "VCG", "CG a partir do nariz, cal"), ("--OR", "OR", "raio da ogiva, cal (1000 = cone)"),
    ("--DM", "DM", "diâmetro do meplat, cal"), ("--BD", "BD", "diâmetro da cinta, cal"),
    ("--BOOM", "BOOM", "'boom length' do cartão original, cal"),
    ("--DIA", "DIA", "diâmetro, in"), ("--IX", "IX", "inércia axial, lb·in²"),
    ("--IY", "IY", "inércia transversal, lb·in²"), ("--WGT", "WGT", "peso, lb"),
    ("--TWIST", "TWIST", "passo de raia, calibres por volta"),
    ("--TEMP", "TEMP", "temperatura do ar, °F"), ("--DGUN", "DGUN", "diâmetro do tubo, in"),
)
ALTERNATIVAS = (
    ("--d-mm", "D_MM", "diâmetro, mm (no lugar de --DIA)"),
    ("--massa-g", "MASSA_G", "massa, g (no lugar de --WGT)"),
    ("--ix-gcm2", "IX_GCM2", "inércia axial, g·cm²"), ("--iy-gcm2", "IY_GCM2", "inércia transversal, g·cm²"),
    ("--passo-mm", "PASSO_MM", "uma volta da raia, mm"), ("--passo-pol", "PASSO_POL", "uma volta da raia, in"),
    ("--temp-c", "TEMP_C", "temperatura, °C"), ("--cg-base", "CG_BASE", "CG a partir da BASE, cal"),
    ("--dgun-mm", "DGUN_MM", "diâmetro do tubo, mm"),
)


def _destino(chave: str) -> str:
    """Chave do cartão que uma entrada preenche (ela mesma, se já for do cartão)."""
    return _un.ALTERNATIVAS[chave][0] if chave in _un.ALTERNATIVAS else chave


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="aeroballistics",
        description="aeroballistics, adaptado do SPIN-73: coeficientes aerodinâmicos e estabilidade de um "
                    "projétil estabilizado por rotação, a partir da geometria. Sem opções de "
                    "adição, a saída é a do programa de 1973 (canônica).")
    ap.add_argument("--entrada", help="arquivo 'CHAVE = valor' (aceita as chaves do cartão, as "
                                      "alternativas métricas e as opções de massa)")
    ap.add_argument("--exemplo", action="store_true",
                    help="parte do caso de validação do relatório (175 mm M437)")
    g = ap.add_argument_group("cartão do SPIN-73 (canônico)")
    for opt, chave, ajuda in CARTAO:
        g.add_argument(opt, dest=chave, type=float, help=ajuda)
    g.add_argument("--nome", default=None)
    g = ap.add_argument_group("as mesmas entradas em outras unidades (conversão exata)")
    for opt, chave, ajuda in ALTERNATIVAS:
        g.add_argument(opt, dest=chave, type=float, help=ajuda)
    g = ap.add_argument_group("adição opcional: estimar CG, massa e inércias que faltam")
    g.add_argument("--estimar-massa", nargs="?", const="solido", choices=_massa.METODOS,
                   help="solido (padrão: sólido homogêneo), bala ou granada (fórmulas de "
                        "Hitchcock, BRL 620); só preenche o que o cartão não tem")
    g.add_argument("--densidade", type=float, help="kg/m³, para o método solido sem massa")
    g.add_argument("--material", help=f"no lugar da densidade: {', '.join(_massa.MATERIAIS)}")
    g.add_argument("--ang-bt", type=float, help="ângulo do boattail, graus (padrão 8)")
    g.add_argument("--db", type=float, help="diâmetro da base, cal (no lugar do ângulo)")
    g = ap.add_argument_group("adição opcional: correções da saída")
    g.add_argument("--correcao", action="append", default=[],
                   help=f"pode repetir ({', '.join(_corr.disponiveis())}; "
                        "'voo_livre:CX0' para só um coeficiente)")
    ap.add_argument("--csv", help="grava todas as colunas neste arquivo CSV")
    ap.add_argument("--programa", action="store_true",
                    help="mostra o programa original bloco a bloco (aeroballistics.programa) e sai")
    a = ap.parse_args(argv)
    if a.programa:
        from .programa import SPIN73
        print(SPIN73.descrever())
        return

    # camadas, da mais fraca para a mais forte: --exemplo, --entrada, opções da linha de
    # comando. Uma grandeza dada numa camada substitui a mesma grandeza das de baixo, em
    # qualquer unidade (--d-mm na linha substitui DIA do arquivo, por exemplo).
    camadas = []
    if a.exemplo:
        camadas.append({k: getattr(M437, k) for k in _un.CANONICAS})
    try:
        if a.entrada:
            camadas.append(_un.ler_campos(a.entrada))
        linha = {chave: getattr(a, chave) for _, chave, _ in CARTAO + ALTERNATIVAS
                 if getattr(a, chave) is not None}
        if a.nome is not None:
            linha["nome"] = a.nome
        camadas.append(linha)
        brutos = {}
        for camada in camadas:
            novos = {_un.normalizar(k): v for k, v in camada.items()}
            destinos = {_destino(k) for k in novos}
            brutos = {k: v for k, v in brutos.items() if _destino(k) not in destinos}
            brutos.update(novos)
        campos, opc = _un.separar(brutos)
        faltam = [k for k in ("VL", "VN", "VB") if k not in campos]
        if faltam:
            ap.error("informe --exemplo, --entrada ou pelo menos --VL --VN --VB "
                     f"(faltam: {', '.join(faltam)})")
        p = Projetil(**campos)
    except ValueError as e:
        ap.error(str(e))

    metodo = a.estimar_massa or opc.get("ESTIMAR_MASSA")
    adicoes, relatorio_massa = [], None
    if metodo:
        kw = dict(densidade=a.densidade if a.densidade is not None else opc.get("DENSIDADE"),
                  material=a.material or opc.get("MATERIAL"),
                  ang_bt=a.ang_bt if a.ang_bt is not None else opc.get("ANG_BT"),
                  db=a.db if a.db is not None else opc.get("DB"))
        falta = _massa.o_que_falta(p)
        try:
            relatorio_massa = _massa.estimar(p, metodo, **kw) if falta else None
            p = _massa.completar(p, metodo, **kw)
        except ValueError as e:
            ap.error(str(e))
        preenchidos = [c for c in falta if c not in _massa.o_que_falta(p)]
        adicoes.append(f"massa estimada ({metodo}: {', '.join(preenchidos) or 'nada faltava'})")
    elif p.VCG is None:
        ap.error("falta o VCG (CG a partir do nariz). Informe --VCG ou --cg-base, ou use "
                 "--estimar-massa para estimá-lo pela geometria (adição opcional)")

    try:
        aero = Aerodinamica(p, a.correcao or None)
    except ValueError as e:
        ap.error(str(e))
    adicoes += [f"correção {c.nome}" for c in aero.correcoes]
    t = aero.tabela
    titulo = f"aeroballistics (adaptado do SPIN-73) -- {p.nome or 'projétil'}"
    modo = "canônico (SPIN-73 de 1973)" if not adicoes else \
        "canônico + adições opcionais: " + "; ".join(adicoes)
    print(titulo)
    print(f"Modo: {modo}")
    if relatorio_massa is not None:
        print()
        print("ESTIMATIVA DE MASSA (adição opcional; não é do SPIN-73)")
        for x in str(relatorio_massa).splitlines():
            print("  " + x)
    print()
    print(formatar(t))
    print()
    print("AVISOS (limitações da adaptação para esta geometria):")
    for x in avisos(p):
        print("  - " + x)
    if a.csv:
        salvar_csv(t, a.csv)
        print()
        print(f"CSV gravado em {a.csv}")


def _executar():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
