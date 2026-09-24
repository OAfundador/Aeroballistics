"""
Cmq e centro de pressão do SPIN-73 reconstruído contra o voo livre do BRL MR 1833 (7,62 NATO).

Fecha a comparação que já existia para Magnus (`comparar_magnus.py`) e para CNα (grupo 762
em `../correcao/dados.py`):
agora que XF (Cmq, com o termo F9) e XC (centro de pressão) foram lidos, dá para confrontar
os dois com experimento.

Normalizações (ver README.md): o MR 1833 dá Cmq+Cmα̇ com q·d/V, o SPIN-73 usa q·d/(2V), daí
o fator 2 já aplicado em `recalibrar_mr1833.tabela()`. O centro de pressão sai da própria
tabela pela identidade CPN = (CNα·VCG − CMα)/CNα, em calibres a partir do nariz, que é a
convenção do SPIN-73.

HIPÓTESES, como em `comparar_magnus.py`:
  - entre pontos da grade de Mach do SPIN-73, interpola-se linearmente;
  - o raio de ogiva da família 7,62 é incerto (figura indica "30R" ≈ 9,74 cal). Ele entra no
    CPN por CCRT = VN²/OR − 0,48, então a sensibilidade a essa hipótese é reportada.

O Cmq e o CPN existem nos 17 pontos. O cartão de continuação de XC15 não foi impresso no
relatório (NOTAS_TRANSCRICAO.md, T6), e as nove células de Mach 1,2 a 5,0 foram DECIDIDAS
PELO MODELO a partir das tabelas de 1973 (xc_lidos: RECUPERADOS e DECIDIDOS_M437), como
algumas correções de leitura na mesma faixa (CORRECOES). Nenhuma saiu do voo livre, então a
comparação não é circular, mas o CPN do modelo acima de Mach 1,1 depende delas: a saída
lista as que entram na faixa das rodadas.

O CPN experimental é o de cada rodada, VCG − CMα/CNα, só com valores medidos; a curva
ajustada e o fator k(M) do CPN não usam o CNα do SPIN-73 (o CNα do modelo tem viés próprio,
ver `comparar_cna.py`).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import caminhos                                    # noqa: E402,F401  (também põe a saída em UTF-8)

import recalibrar_mr1833 as r                      # noqa: E402
from cmq_spin73 import cmq as cmq_spin             # noqa: E402
from cpn_spin73 import cpn_cma, decididas          # noqa: E402

MACH = np.array([0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0])
PROJETEIS = ["M-80", "M-59", "M-61", "M-62"]
OR_HIP = 9.74            # raio de ogiva suposto (calibres)
DM = 0.195


def tabela():
    """As rodadas de `recalibrar_mr1833.tabela()` com o CPN medido, VCG − CMα/CNα."""
    lin = r.tabela()
    for l in lin:
        l["CPN"] = l["MNARIZ"] / l["CNA"] if np.isfinite(l["MNARIZ"]) and l["CNA"] else np.nan
    return lin


def curva_cmq(g):
    """Cmq do SPIN-73 nos 17 pontos de Mach, para a geometria g."""
    return np.array([cmq_spin(g["VL"], g["VCG"], g["VB"], j) for j in range(17)])


def curva_cpn(g, OR=OR_HIP):
    """CPN do SPIN-73 nos 17 pontos (NaN onde falta o DATA)."""
    return np.array([cpn_cma(g["VL"], g["VN"], g["VB"], OR, DM, g["VCG"], j)[0]
                     for j in range(17)])


def por_rodada(linhas, coluna, curva):
    """Viés por projétil: média(modelo − experimento) contra a dispersão do experimento."""
    out = []
    for p in PROJETEIS:
        L = [l for l in linhas if l["proj"] == p and l["M"] >= r.MMIN and np.isfinite(l[coluna])]
        if not L:
            continue
        g = r.GEO[p]
        y = np.array([l[coluna] for l in L])
        c = curva(g)
        m = np.array([np.interp(l["M"], MACH, c) for l in L])
        ok = np.isfinite(m)
        if not ok.any():
            continue
        out.append((p, len(y[ok]), float(np.mean(m[ok] - y[ok])), float(np.std(y[ok]))))
    return out


def contra_ajuste(linhas, coluna, curva, machs, modelo=None):
    """Modelo contra a curva experimental ajustada (MMQ), nos pontos da grade pedidos.

    `modelo` escolhe o modelo reduzido de `r.MODELOS` (padrão: o da própria coluna)."""
    regs, projs, _ = r.MODELOS[modelo or coluna]
    fit = r.mmq(linhas, coluna, regs, projs)
    ev = r.avaliar(fit, machs)
    linhas_out = []
    for p in PROJETEIS:
        g = r.GEO[p]
        c = curva(g)
        for i, M in enumerate(machs):
            exp = sum(ev[k][0][i] * reg({**g, "CXLL": g["VL"] - g["VN"] - g["VB"] - 2.15,
                                         "CLL": g["VL"] - 5.0, "CCG": g["VCG"] - 3.0,
                                         "CXCL": g["VL"] - g["VN"] - g["VB"] - 1.5})
                      for k, reg in regs.items())
            err = sum(ev[k][1][i] * abs(reg({**g, "CXLL": g["VL"] - g["VN"] - g["VB"] - 2.15,
                                             "CLL": g["VL"] - 5.0, "CCG": g["VCG"] - 3.0,
                                             "CXCL": g["VL"] - g["VN"] - g["VB"] - 1.5}))
                      for k, reg in regs.items())
            mod = np.interp(M, MACH, c)
            linhas_out.append((p, M, exp, err, mod))
    return linhas_out


def fator_recalibracao(linhas, coluna, curva, grade=np.array([1.2, 1.5, 2.0, 2.5, 3.0])):
    """Ajusta k(M) em  experimento ≈ k(M) · modelo, com k quadrático em (M − 2).

    É a forma honesta de recalibrar aqui: com quatro projéteis quase iguais não se
    identificam as constantes individuais (F1..F9), mas o fator de escala sai bem
    determinado. k = 1 significa que o SPIN-73 acerta a família.
    """
    L = [l for l in linhas if l["M"] >= r.MMIN and np.isfinite(l[coluna])]
    X, Y = [], []
    for l in L:
        mod = np.interp(l["M"], MACH, curva(r.GEO[l["proj"]]))
        if not np.isfinite(mod):
            continue
        X.append(mod * r.base_mach(l["M"])[0])
        Y.append(l[coluna])
    X, Y = np.array(X), np.array(Y)
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta
    s2 = res @ res / (len(Y) - 3)
    cov = s2 * np.linalg.pinv(X.T @ X)
    B = r.base_mach(grade)
    k = B @ beta
    sk = np.sqrt(np.einsum("ij,jk,ik->i", B, cov, B))
    return grade, k, sk, len(Y), np.sqrt(s2)


if __name__ == "__main__":
    lin = tabela()

    print("=" * 78)
    print("Cmq  (q·d/2V) -- modelo completo: XF1..XF9 lidos, termo de corpo longo F9")
    print("=" * 78)
    print(f"{'proj':6s} {'n':>3s} {'viés do SPIN-73':>16s} {'dispersão exp':>14s}")
    for p, n, vies, sd in por_rodada(lin, "CMQ", curva_cmq):
        marca = "  <-- viés maior que a dispersão" if abs(vies) > sd else ""
        print(f"{p:6s} {n:3d} {vies:+16.2f} {sd:14.2f}{marca}")
    ep, npar = r.erro_puro(lin, "CMQ", PROJETEIS)
    print(f"\nerro puro entre rodadas repetidas: {ep:.2f} ({npar} pares)")
    print("\nContra a curva experimental ajustada por MMQ:")
    print(f"{'proj':6s} {'Mach':>5s} {'experimento':>13s} {'SPIN-73':>9s} {'dif':>8s}")
    for p, M, exp, err, mod in contra_ajuste(lin, "CMQ", curva_cmq, np.array([1.2, 1.5, 2.0, 2.5])):
        print(f"{p:6s} {M:5.2f} {exp:8.2f}±{err:<4.2f} {mod:9.2f} {mod - exp:+8.2f}")

    print("\n" + "=" * 78)
    print("Centro de pressão CPN (calibres do nariz) -- XC15 de Mach 1,2 a 5 decidido")
    print("=" * 78)
    disponivel = [f"{m:.2f}" for m, v in zip(MACH, curva_cpn(r.GEO["M-80"])) if np.isfinite(v)]
    print("pontos de Mach com reconstrução:", ", ".join(disponivel))
    rodadas ={p: [l["M"] for l in lin if l["proj"] == p and l["M"] >= r.MMIN and np.isfinite(l["CPN"])]
               for p in PROJETEIS}
    cel = sorted({c for p in PROJETEIS for c in decididas(rodadas[p], r.GEO[p]["VB"])},
                 key=lambda t: (t[1], t[0]))
    todas = [m for ms in rodadas.values() for m in ms]
    print("\nCélulas de XC decididas pelo modelo (xc_lidos) que entram no CPN das rodadas")
    print(f"(Mach {min(todas):.2f} a {max(todas):.2f}, pontos da grade usados na interpolação):")
    for j in sorted({j for _, j, _ in cel}):
        print(f"  Mach {MACH[j]:4.2f}: " + ", ".join(f"XC{l} ({reg})" for l, jj, reg in cel if jj == j))

    print(f"\n{'proj':6s} {'n':>3s} {'viés do SPIN-73':>16s} {'dispersão exp':>14s}")
    for p, n, vies, sd in por_rodada(lin, "CPN", curva_cpn):
        marca = "  <-- viés maior que a dispersão" if abs(vies) > sd else ""
        print(f"{p:6s} {n:3d} {vies:+16.2f} {sd:14.2f}{marca}")
    ep, npar = r.erro_puro(lin, "CPN", PROJETEIS)
    print(f"\nerro puro entre rodadas repetidas: {ep:.3f} ({npar} pares)")

    # a curva experimental é ajustada ao CPN medido, com o modelo reduzido do CNα·CPN
    MODELO_CPN = "MNARIZ"
    fit = r.mmq(lin, "CPN", *r.MODELOS[MODELO_CPN][:2])
    print("\nContra a curva experimental ajustada por MMQ ao CPN medido (constante + CXLL,")
    print(f"quadráticos em M − 2): n = {len(fit['L'])}, resíduo rms = {fit['s']:.3f}")
    print(f"{'proj':6s} {'Mach':>5s} {'CPN exp':>16s} {'CPN SPIN-73':>12s} {'dif':>7s}")
    for p, M, exp, err, mod in contra_ajuste(lin, "CPN", curva_cpn, np.array([1.2, 1.5, 2.0, 2.5]),
                                             modelo=MODELO_CPN):
        print(f"{p:6s} {M:5.2f} {exp:11.3f}±{err:<4.3f} {mod:12.3f} {mod - exp:+7.3f}")

    print("\nSensibilidade ao raio de ogiva suposto (M-80, Mach 2,0):")
    for orr in (8.0, 9.74, 12.0):
        v = curva_cpn(r.GEO["M-80"], orr)[12]
        print(f"  OR = {orr:5.2f} cal -> CPN = {v:.3f}")

    print("\n" + "=" * 78)
    print("RECALIBRAÇÃO: fator k(M) em  experimento ≈ k(M) · SPIN-73")
    print("=" * 78)
    for coluna, curva, nome, fmt in (("CMQ", curva_cmq, "Cmq", ".2f"), ("CPN", curva_cpn, "CPN", ".3f")):
        grade, k, sk, n, s = fator_recalibracao(lin, coluna, curva)
        print(f"\n{nome}: n = {n} rodadas, resíduo rms = {s:{fmt}}")
        print("  Mach:  " + "".join(f"{m:>12.2f}" for m in grade))
        print("  k:     " + "".join(f"{a:7.2f}±{b:<4.2f}" for a, b in zip(k, sk)))

    sem_m62 = [l for l in lin if l["proj"] != "M-62"]
    variantes = (("OR =  8.00 cal", lin, lambda g: curva_cpn(g, 8.0)),
                 ("OR = 12.00 cal", lin, lambda g: curva_cpn(g, 12.0)),
                 ("sem o M-62", sem_m62, curva_cpn))
    print("\nk do CPN com outro raio de ogiva suposto, e sem o M-62 (base arredondada, fora do")
    print("modelo do SPIN-73):")
    print(f"  {'Mach:':16s}" + "".join(f"{m:>12.2f}" for m in grade))
    for rotulo, L, curva in variantes:
        grade, k, sk, n, s = fator_recalibracao(L, "CPN", curva)
        print(f"  {rotulo + ':':16s}" + "".join(f"{a:7.2f}±{b:<4.2f}" for a, b in zip(k, sk)))
    print(f"  sem o M-62: n = {n} rodadas, resíduo rms = {s:.3f}")

    print("\nO k do CPN usa o CPN medido rodada a rodada (VCG − CMα/CNα, só experimento), não o")
    print("CNα do SPIN-73. Acima de Mach 1,1, o CPN do modelo depende das células de XC")
    print("decididas pelas tabelas de 1973, listadas acima; nenhuma saiu do voo livre.")
