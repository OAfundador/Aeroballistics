"""O programa original (SPIN-73, 1973), bloco a bloco, como objetos.

Não é o código de 1973: é uma descrição dele, com as nossas palavras e a nossa notação, feita
a partir da leitura do relatório (texto, pp. 13-18; listing, pp. 79-86). Cada bloco diz o que
o programa calcula, com que constantes (blocos DATA), de que statements do listing veio a
leitura (a numeração sequencial que o compilador imprimiu à esquerda, "C164"...), o que não
foi possível ler e onde isso está implementado aqui. O listing não é reproduzido neste
repositório; ele está no relatório (DTIC AD0915628).

    from spin73.programa import SPIN73
    print(SPIN73.descrever())           # o programa inteiro
    b = SPIN73.de_coluna("CMA")         # o bloco que calcula o CMα
    print(b)                            # fórmulas, regras, statements, implementação
    b.calcular(spin73.M437)             # as colunas desse bloco para um projétil

Notação: VL, VN, VB, VCG, OR, DM, BD, BOOM, DIA, IX, IY, WGT, TWIST, DGUN, TEMP são as
entradas do cartão; a1..a15, b1..b9, c1..c17, d1..d4, e1..e5, f1..f9 e g1 são os valores
dos blocos DATA XA, XB, XC, XD, XE, XF e XG no Mach da linha.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass

from . import nucleo


@dataclass(frozen=True)
class Bloco:
    """Um trecho do programa original: o que calcula e de onde veio cada parte."""
    chave: str
    titulo: str
    colunas: tuple = ()             # colunas de saída que ele produz
    dados: tuple = ()               # blocos DATA que ele usa
    statements: tuple | None = None  # (primeiro, último), numeração do compilador
    paginas: str = ""
    fonte: str = ""                 # código, texto do relatório, ou os dois
    descricao: str = ""
    formulas: tuple = ()            # na nossa notação
    regras: tuple = ()              # condições e decisões do programa
    lacunas: tuple = ()             # o que não se leu, e o que foi feito
    implementacao: str = ""         # onde está aqui, "modulo.funcao"

    def funcao(self):
        """A função que implementa o bloco nesta reconstrução."""
        modulo, nome = self.implementacao.rsplit(".", 1)
        return getattr(importlib.import_module(modulo), nome)

    def calcular(self, projetil) -> dict:
        """As colunas deste bloco para um projétil, nos 17 Mach (pelo programa inteiro)."""
        if self.chave == "entrada":
            return dict(RHO=nucleo.densidade_ar(projetil.TEMP), A_SOM=nucleo.vel_som(projetil.TEMP))
        t = nucleo.tabela(projetil)
        if self.chave == "saida":
            return dict(TEXTO=nucleo.formatar(t))
        return {c: t[c] for c in self.colunas if c in t}

    def _faixa(self) -> str:
        if self.statements is None:
            return "—"
        a, b = self.statements
        return f"C{a}" if a == b else f"C{a}–C{b}"

    def __str__(self) -> str:
        linhas = [self.titulo,
                  f"  colunas: {', '.join(self.colunas) or '—'}",
                  f"  dados: {', '.join(self.dados) or '—'}",
                  f"  statements: {self._faixa()}; páginas: {self.paginas}; fonte: {self.fonte}",
                  f"  implementação: {self.implementacao}",
                  "  " + self.descricao]
        linhas += ["  = " + f for f in self.formulas]
        linhas += ["  * " + r for r in self.regras]
        linhas += ["  ! " + x for x in self.lacunas]
        return "\n".join(linhas)


class ProgramaOriginal:
    """O programa inteiro, na ordem em que o original calcula."""

    def __init__(self, blocos):
        self.blocos = tuple(blocos)

    def __iter__(self):
        return iter(self.blocos)

    def bloco(self, chave: str) -> Bloco:
        for b in self.blocos:
            if b.chave == chave:
                return b
        raise KeyError(f"bloco desconhecido: {chave}; há {', '.join(b.chave for b in self.blocos)}")

    def de_coluna(self, coluna: str) -> Bloco:
        """O bloco que produz uma coluna de saída (CX, CMA, GYRO...)."""
        for b in self.blocos:
            if coluna in b.colunas:
                return b
        raise KeyError(f"nenhum bloco produz {coluna}")

    def descrever(self, formato: str = "texto") -> str:
        if formato == "texto":
            return "\n\n".join(str(b) for b in self.blocos)
        if formato != "markdown":
            raise ValueError("formato: 'texto' ou 'markdown'")
        out = []
        for i, b in enumerate(self.blocos, 1):
            out.append(f"## {i}. {b.titulo}\n")
            out.append(b.descricao + "\n")
            out.append("| | |\n|---|---|")
            out.append(f"| Colunas | {', '.join(f'`{c}`' for c in b.colunas) or '—'} |")
            out.append(f"| Dados | {', '.join(b.dados) or '—'} |")
            out.append(f"| Statements do listing | {b._faixa()} |")
            out.append(f"| Páginas | {b.paginas} |")
            out.append(f"| Fonte da leitura | {b.fonte} |")
            out.append(f"| Implementação | `{b.implementacao}` |\n")
            if b.formulas:
                out.append("Fórmulas:\n")
                out += [f"- {f}" for f in b.formulas]
                out.append("")
            if b.regras:
                out.append("Regras:\n")
                out += [f"- {r}" for r in b.regras]
                out.append("")
            if b.lacunas:
                out.append("O que não se leu:\n")
                out += [f"- {x}" for x in b.lacunas]
                out.append("")
        return "\n".join(out).rstrip() + "\n"


SPIN73 = ProgramaOriginal((
    Bloco(
        chave="entrada", titulo="Cartão de entrada e atmosfera",
        paginas="76–77 (cartão); listing (atmosfera)", fonte="Apêndice B e código",
        descricao="Lê o cartão (geometria em calibres; diâmetro, inércias e peso em unidades "
                  "inglesas) e calcula a densidade do ar e a velocidade do som a partir da "
                  "temperatura.",
        formulas=("ΔT = TEMP − 59 °F",
                  "ρ = 0,002376 + (−4,784·ΔT + 0,01092·ΔT²)·10⁻⁶ slug/ft³",
                  "a = 49,04·√(459,6 + TEMP) ft/s"),
        regras=("no cartão original, campos em branco valem DM = 0, BD = 1,00 e TEMP = 0 °F; "
                "aqui os padrões são 0,12, 1,02 e 59 °F (passe zero para reproduzir o cartão "
                "em branco)",),
        implementacao="spin73.nucleo.densidade_ar"),
    Bloco(
        chave="arrasto", titulo="Força axial a guinada zero (CX)",
        colunas=("CX",), dados=("XA",), statements=(164, 174), paginas="83–84",
        fonte="código (a partir de C164) e texto",
        descricao="Um polinômio nas variáveis de forma, mais três correções por trecho: "
                  "ogiva longa, cilindro longo e boattail longo.",
        formulas=("u = min(VN, 3) − 2,5;   L = VL − VN − VB − 1,5;   R = VN²/OR − 0,40",
                  "β = 0 se VB ≤ 0,2;  VB − 0,2 se VB < 0,65;  0,45 daí em diante",
                  "CX = a1 + a2·u + a3·u² + a4·u³ + a5·min(L, 1,5) + a6·min(L, 1,5)² + a7·β "
                  "+ a8·R + a9·R² + a11·(BD − 1,02) + a12·(DM − 0,12)² − 0,01·(BOOM/1,36)² "
                  "− Δ_bt − Δ_og + Δ_cil"),
        regras=("Δ_og, só com ogiva acima de 3 cal, em três trechos contínuos: a13·(VN − 3) "
                "até 3,48 cal; 0,48·a13 + a14·(VN − 3,48) até 3,97; e 0,48·a13 + 0,49·a14 "
                "+ a15·(VN − 3,97) acima. O texto só documenta o primeiro trecho",
                "Δ_cil = 0,010·(L − 1,5) quando L > 1,5",
                "Δ_bt = a10·(VB − 0,65) quando VB ≥ 0,65"),
        lacunas=("o começo do cálculo está na p. 83, que não foi lida: o termo Δ_bt segue o "
                 "texto do relatório, e a saída avisa quando ele é usado",),
        implementacao="spin73.nucleo.cx"),
    Bloco(
        chave="normal", titulo="Força normal, centro de pressão e momento de arfagem",
        colunas=("CNA", "CPN", "CMA"), dados=("XB", "XC"), statements=(175, 212),
        paginas="84–85", fonte="código",
        descricao="Soma a força normal e o momento do corpo (ogiva e cilindro) com os do "
                  "boattail; o centro de pressão sai da razão entre os dois, e o momento em "
                  "torno do CG, do braço até o CG.",
        formulas=("v = min(VN, 3) − 2,47;   ℓ = VL − VN − VB − 2,15;   r = VN²/OR − 0,48;   "
                  "m = DM − 0,17;   n = max(VN − 3, 0);   w = min(VB, 1)",
                  "N_corpo = b1 + b2·v + b3·ℓ + b4·r + b5·v² + b6·ℓ²",
                  "N_bt = b7·β_N + w·(b8·v + b9·ℓ)",
                  "M_corpo = N_corpo·(c1 + c2·v + c3·v² + c4·v³ + c5·ℓ + c6·ℓ² + c7·ℓ³ + c8·r "
                  "+ c9·r² + c10·m + c11·r·v + c17·n)",
                  "M_bt = (VL/4,7)·(c12·β_M + w·(c13·v + c14·ℓ + c15·r + c16·r·v))",
                  "CNα = N_corpo + N_bt;   CPN = (M_corpo + M_bt)/CNα;   CMα = (VCG − CPN)·CNα"),
        regras=("expoentes do boattail: β_N = VB e β_M = VB^0,8 abaixo de Mach 0,95; β_N = "
                "VB^1,5 e β_M = VB a partir de Mach 0,95 (o texto não diz o limiar); β_N = "
                "β_M = √VB quando VB > 1",
                "N_bt nunca soma: se sair positiva, vale zero (regra do código, ausente do "
                "texto; só age com ogiva curta no supersônico)",
                "se M_bt sair positivo, o boattail inteiro é descartado: CNα = N_corpo e "
                "M_bt = 0 (regra do código, ausente do texto)",
                "o termo c11 multiplica r·v; o texto imprime outra variável ali, erro "
                "tipográfico"),
        lacunas=("o cartão de continuação do XC15 (Mach 1,2 a 5) não foi impresso: valores "
                 "recuperados pelas tabelas de saída",
                 "a linha do XC12 está desbotada: células decididas pelas tabelas"),
        implementacao="spin73.nucleo.normal_e_momento"),
    Bloco(
        chave="guinada", titulo="Termo de guinada da força axial (CX2)",
        colunas=("CX2",), dados=("XD",), statements=(213, 213), paginas="85", fonte="código",
        descricao="O termo que, somado ao CNα, dá o arrasto de guinada por sen² da guinada.",
        formulas=("CX2 = d1 + d2·L + d3·R + d4·VB − CNα   (L e R como no arrasto)",),
        regras=("o arrasto de guinada é CX2 + CNα, não o CX2 (p. 15)",),
        implementacao="spin73.nucleo.cx2"),
    Bloco(
        chave="magnus", titulo="Força e momento de Magnus",
        colunas=("CYPA", "CNPA", "CPF1", "CPF5", "CNPA5"), dados=("XE",),
        statements=(214, 231), paginas="85", fonte="código",
        descricao="A força de Magnus e, para três ângulos de ataque (1°, 2° e 5°), o centro "
                  "de pressão dela e o momento em torno do CG.",
        formulas=("Y = e1·VL;   CYPA = Y − 0,1·VB",
                  "para cada ângulo, com e = e2 (1°), e3 (2°) ou e4 (5°):   N = −Y·(e + 0,55·L "
                  "+ 0,8·(VN − 2,5)) + VL·VB/4,7",
                  "CPF = −N/CYPA + Δ_cl;   momento = (VCG − CPF)·CYPA"),
        regras=("Δ_cl = e5·(VL − 6) quando VL > 6 (termo de corpo longo, ausente do texto)",
                "a 1° saem CPF1 e CNPA; a 5°, CPF5 e CNPA5; o valor a 2° é calculado e não "
                "entra em nenhuma coluna impressa"),
        lacunas=("o primeiro cartão do XE5 (Mach 0,01 a 1,75) não foi impresso: valores "
                 "recuperados pelas tabelas de saída",),
        implementacao="spin73.nucleo.magnus"),
    Bloco(
        chave="polinomio", titulo="\"Coeficientes do polinômio\" de Magnus (CNPA3, CNPA5P)",
        colunas=("CNPA3", "CNPA5P"), statements=(278, 281), paginas="86", fonte="código",
        descricao="Duas colunas impressas que deveriam ajustar um polinômio ao momento de "
                  "Magnus em três ângulos.",
        formulas=("D = CNPA(5°) − CNPA(1°)",
                  "CNPA5P = ((D + 0,3) − 9·D)/0,0072",
                  "CNPA3 = (D − 0,0001·CNPA5P)/0,01"),
        regras=("as constantes são as de um polinômio C1 + C3·δ² + C5·δ⁴ ajustado em δ = 0,1 "
                "e 0,3, mas o segundo ponto usa D + 0,3 no lugar do valor a 2°: as duas "
                "colunas carregam um único grau de liberdade e sempre obedecem a CNPA3 + "
                "0,1·CNPA5P = 3,75 (defeito do original, reproduzido)",
                "o programa imprime \"CNPA5\" para esta coluna e \"CNPA-5\" para o momento a "
                "5°; aqui são CNPA5P e CNPA5"),
        implementacao="spin73.nucleo.coef_polinomio_magnus"),
    Bloco(
        chave="cmq", titulo="Amortecimento em arfagem (CMQ)",
        colunas=("CMQ",), dados=("XF",), statements=(232, 238), paginas="85", fonte="código",
        descricao="Cmq + Cmα̇ na convenção qd/2V.",
        formulas=("λ = VL − 5;   g = VCG − 3",
                  "K = f1 + f2·λ + f3·λ² + f4·g + f5·g·λ + f6·g·λ² + f7·g·VB + f8·VB",
                  "CMQ = −5,093·K − Δ_cl"),
        regras=("Δ_cl = f9·(VL − 6) quando VL > 6 (termo de corpo longo, ausente do texto)",),
        lacunas=("o segundo cartão do XF7 (Mach 1,1 a 2,5) não foi impresso: valores "
                 "recuperados pela tabela do 5\"/38",),
        implementacao="spin73.nucleo.cmq"),
    Bloco(
        chave="clp", titulo="Amortecimento de rolamento (CLP)",
        colunas=("CLP",), dados=("XG",), statements=(239, 239), paginas="85", fonte="código",
        descricao="Clp na convenção pd/2V, proporcional ao comprimento.",
        formulas=("CLP = g1·VL/5,51",),
        regras=("o divisor é uma constante do programa que o texto dá como 5,51, o "
                "comprimento do M437",),
        implementacao="spin73.nucleo.clp"),
    Bloco(
        chave="estabilidade", titulo="Análise de estabilidade",
        colunas=("GYRO", "SBAR", "RECIP", "SBAR5", "RECIP5", "SPIN", "W1", "W2",
                 "L1", "L2", "L15", "L25", "DELT", "DISP"),
        statements=(240, 266), paginas="85–86", fonte="código e texto (pp. 17–18)",
        descricao="Com diâmetro, massa, inércias e passo de raia: a rotação, os fatores de "
                  "estabilidade giroscópica e dinâmica, e as frequências e taxas de "
                  "amortecimento dos dois modos da guinada.",
        formulas=("V = Mach·a (ft/s);   passo = TWIST·DGUN (polegadas por volta);   "
                  "p = 2π·V/(passo/12) (rad/s)",
                  "s_g = 1352,4·IX²/(ρ·IY·CMα·passo²·DIA³)   (IX, IY em lb·in²; comprimentos "
                  "em polegadas)",
                  "m = WGT/32,174;   d = DIA/12;   Ix = IX/(32,174·144);   Iy = IY/(32,174·144)"
                  "   (pé e slug)",
                  "k₁ = m·d²/Ix;   k₂ = m·d²/Iy",
                  "s_d = 2·(CNα − CX + (k₁/2)·CNPA) / (CNα − CX − (k₂/2)·CMQ + (k₁/2)·CLP);   "
                  "RECIP = 1/(s_d·(2 − s_d))   (SBAR5 e RECIP5 com o momento a 5°)",
                  "σ = √(1 − 1/s_g);   ω₁,₂ = p·Ix/(2·Iy)·(1 ± σ)",
                  "λ₁,₂ = (ρ·A/(4m))·[−CNα·(1 ∓ 1/σ) + (k₂/2)·(1 ± 1/σ)·CMQ ± (k₁/σ)·CNPA],   "
                  "A = π·d²/4   (L15 e L25 com o momento a 5°)",
                  "DELT = 6,28/(20·ω₁)",
                  "DISP = (CNα − CX)·IY·(ω₁ − ω₂)·3,635/(CMα·WGT·DIA·V)"),
        regras=("sem diâmetro (DIA = 0), não há análise de estabilidade",
                "com s_g < 1,001, só o Mach e o s_g são impressos",
                "a constante 1352,4 é a do código; a física com g = 32,174 daria 1349,8 "
                "(+0,19 %)",
                "o texto (p. 18) imprime trocado o sinal do primeiro termo de λ; o código e "
                "as tabelas usam o sinal acima"),
        lacunas=("DISP: a fórmula é a do código; a grandeza depende da referência 71 do "
                 "relatório (Whyte 1970), indisponível",),
        implementacao="spin73.nucleo.estabilidade"),
    Bloco(
        chave="saida", titulo="Impressão", statements=(282, 294), paginas="86", fonte="código",
        descricao="Para cada Mach, uma linha com os 14 coeficientes aerodinâmicos e, com "
                  "massa e raia, uma linha com as 14 colunas de estabilidade.",
        implementacao="spin73.nucleo.formatar"),
))

CABECALHO = """# O programa original, bloco a bloco

Descrição do SPIN-73 de 1973 com as nossas palavras e a nossa notação: o que cada trecho do
programa calcula, com que constantes, de onde veio a leitura, o que não foi possível ler e
onde está implementado nesta reconstrução. **Não é o código original**, que está no relatório
(DTIC AD0915628, listing nas pp. 79–86) e não é reproduzido neste repositório.

Gerado de `src/spin73/programa.py` (`python -m spin73.programa --doc`); a evidência de cada
leitura está em [NOTAS_TRANSCRICAO.md](NOTAS_TRANSCRICAO.md).

Notação: VL, VN, VB, VCG, OR, DM, BD, BOOM, DIA, IX, IY, WGT, TWIST, DGUN e TEMP são as
entradas do cartão; a1..a15, b1..b9, c1..c17, d1..d4, e1..e5, f1..f9 e g1 são os valores dos
blocos DATA XA, XB, XC, XD, XE, XF e XG no Mach da linha. "Statements" é a numeração
sequencial que o compilador imprimiu à esquerda de cada linha do listing.

"""


def documento() -> str:
    """O texto de docs/PROGRAMA_ORIGINAL.md."""
    return CABECALHO + SPIN73.descrever("markdown")


__all__ = ["Bloco", "ProgramaOriginal", "SPIN73", "documento"]


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--doc" in sys.argv:
        print(documento(), end="")
    else:
        print(SPIN73.descrever("markdown" if "--markdown" in sys.argv else "texto"))
