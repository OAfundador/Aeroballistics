"""
Gera o relatório de comparação "SPIN-73 impresso (1973) x reconstrução" e as tabelas CSV.

Uso:  python gerar_relatorio.py          -> relatorio_spin73.html + CSVs nesta pasta
Tudo é recalculado a partir dos módulos do pacote; nada é copiado à mão para cá.
"""
import csv, io, os, sys
import numpy as np
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for p in (RAIZ, os.path.join(RAIZ, "reconstrucao_B"), os.path.join(RAIZ, "experimental")):
    sys.path.insert(0, p)

import spin73 as s
import magnus_clp as mc
from dados_cna import MACH, T as T_CNA
from ajustar_B import regressores
from xb_lidos import XB, XB_LIDO, CORRECOES
from cna_spin73 import cna as cna_spin
import comparar_magnus as cmag

TOL = 0.0015
INK, PAPER, GRID, RED, BLUE = "#1f2a36", "#ffffff", "#d9e3ea", "#b3261e", "#2b5d8a"
plt.rcParams.update({
    "svg.fonttype": "none", "font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 9,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": PAPER, "axes.facecolor": PAPER, "axes.formatter.use_locale": False,
})


def svg(fig):
    b = io.StringIO(); fig.savefig(b, format="svg", bbox_inches="tight"); plt.close(fig)
    t = b.getvalue(); return t[t.index("<svg"):]


def impresso(ax, x, y, **kw):
    ax.plot(x, y, "o", mfc="none", mec=INK, ms=4.2, mew=0.9, label=kw.pop("label", "SPIN-73 impresso (1973)"), **kw)


def reproducao(ax, x, y, **kw):
    ax.plot(x, y, "-", color=BLUE, lw=1.6, label=kw.pop("label", "reconstrução"), **kw)


def salvar_csv(nome, cab, linhas):
    with open(os.path.join(AQUI, nome), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(cab); w.writerows(linhas)


# ------------------------------------------------------------------ 1. CNa
def secao_cna():
    P = list(T_CNA)
    rep = {p: np.array([np.array(regressores(*T_CNA[p][1:5], M)) @ XB[:, j] for j, M in enumerate(MACH)]) for p in P}
    rep_lido = {p: np.array([np.array(regressores(*T_CNA[p][1:5], M)) @ XB_LIDO[:, j] for j, M in enumerate(MACH)]) for p in P}
    fig, axs = plt.subplots(2, 5, figsize=(11.5, 4.6), sharex=True)
    for ax, p in zip(axs.flat, P):
        imp = np.array(T_CNA[p][5], float)
        impresso(ax, MACH, imp); reproducao(ax, MACH, rep[p])
        ruim = np.abs(rep[p] - imp) > TOL
        ax.plot(MACH[ruim], imp[ruim], "o", ms=7, mfc="none", mec=RED, mew=1.2)
        ax.set_title(f"{T_CNA[p][0]}  (p. {p})", fontsize=8.5, color=INK)
        ax.set_xlim(0.5, 5.2); ax.set_xticks([0.6, 1, 2, 3, 4, 5])
    for ax in axs[1]: ax.set_xlabel("Mach")
    for ax in axs[:, 0]: ax.set_ylabel("CNα (1/rad)")
    h, l = axs.flat[0].get_legend_handles_labels()
    h.append(plt.Line2D([], [], ls="", marker="o", ms=7, mfc="none", mec=RED, mew=1.2)); l.append("fora do arredondamento (±0,0015)")
    fig.legend(h, l, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout()
    linhas, grade = [], []
    for p in P:
        imp = np.array(T_CNA[p][5], float)
        for j, M in enumerate(MACH):
            linhas.append([p, T_CNA[p][0], M, imp[j], round(rep[p][j], 4), round(rep[p][j] - imp[j], 4)])
        grade.append((p, T_CNA[p][0], rep[p] - imp))
    salvar_csv("cna_impresso_x_reconstruido.csv",
               ["pagina", "projetil", "mach", "cna_impresso", "cna_reconstruido", "diferenca"], linhas)
    todos = np.concatenate([g[2] for g in grade]); f = np.isfinite(todos)
    todos_lido = np.concatenate([rep_lido[p] - np.array(T_CNA[p][5], float) for p in P])
    stats = dict(n=int(f.sum()), ok=int((np.abs(todos[f]) <= TOL).sum()),
                 ok_lido=int((np.abs(todos_lido[f]) <= TOL).sum()), ok5=int((np.abs(todos[f]) <= 0.005).sum()))
    return svg(fig), grade, stats


# ------------------------------------------------------------------ 2. Magnus
def secao_magnus():
    nomes = list(mc.TABELAS)
    fig, axs = plt.subplots(2, 3, figsize=(11.5, 5.6), sharex=True)
    linhas, stats = [], []
    for ax, n in zip(axs.flat, nomes):
        t = mc.TABELAS[n]; pr = mc.prever(t)
        sem = mc.prever(t) if t["VL"] <= 6 else None
        for col, mk in (("CPF1", "o"), ("CPF5", "s")):
            ax.plot(mc.MACH, t[col], mk, mfc="none", mec=INK, ms=4, mew=0.9,
                    label=f"{col} impresso")
            ax.plot(mc.MACH, np.round(pr[col], 3), "-", color=BLUE if col == "CPF1" else "#5b8fb9", lw=1.5,
                    label=f"{col} reconstruído")
        if t["VL"] > 6:
            k0 = mc.K_LONGO.copy(); mc.K_LONGO[:] = 0
            p0 = mc.prever(t); mc.K_LONGO[:] = k0
            ax.plot(mc.MACH, p0["CPF1"], ":", color=RED, lw=1.3, label="sem o termo de corpo longo")
        ax.set_title(n, fontsize=8.5); ax.set_xlim(0.5, 5.2); ax.set_xticks([0.6, 1, 2, 3, 4, 5])
        for col in ("CYPA", "CPF1", "CPF5", "CLP"):
            if col in t:
                d = np.round(pr[col], 3) - t[col]
                stats.append((n, col, int((np.abs(d) <= 0.0011).sum()), len(d)))
                for M, a, b in zip(mc.MACH, t[col], pr[col]):
                    linhas.append([n, col, M, a, round(b, 4), round(b - a, 4)])
    for ax in axs[1]: ax.set_xlabel("Mach")
    for ax in axs[:, 0]: ax.set_ylabel("centro de pressão de Magnus (cal.)")
    hs, ls = [], []
    for ax in axs.flat:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in ls: hs.append(h); ls.append(l)
    fig.legend(hs, ls, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 1.05), fontsize=8)
    fig.tight_layout()
    salvar_csv("magnus_impresso_x_reconstruido.csv", ["projetil", "coluna", "mach", "impresso", "reconstruido", "diferenca"], linhas)
    return svg(fig), stats


# ------------------------------------------------------------------ 3. Estabilidade M437
def secao_estab():
    tab = s.ler_tabela(os.path.join(RAIZ, "m437_tabela.csv"))
    e = s.estabilidade(s.M437, tab["MACH"], tab["CX"], tab["CNA"], tab["CMA"], tab["CNPA"], tab["CNPA5"], tab["CMQ"], tab["CLP"])
    fig, axs = plt.subplots(1, 4, figsize=(11.5, 3.0))
    pares = [("GYRO", "fator giroscópico s_g", 1), ("SBAR", "fator dinâmico s_d (1°)", 1),
             ("W1", "nutação ω₁ (rad/s)", 1), ("L2", "amortecimento λ₂ (10⁻⁴/ft)", 1e4)]
    for ax, (c, rot, esc) in zip(axs, pares):
        impresso(ax, tab["MACH"], tab[c] * esc); reproducao(ax, tab["MACH"], e[c] * esc)
        ax.set_title(rot, fontsize=8.5); ax.set_xlabel("Mach")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.1))
    fig.tight_layout()
    linhas = []
    cols = ["GYRO", "SBAR", "SBAR5", "SPIN", "W1", "W2", "L1", "L2", "L15", "L25"]
    for i, M in enumerate(tab["MACH"]):
        for c in cols:
            linhas.append([M, c, tab[c][i], float(e[c][i]), float(e[c][i] - tab[c][i])])
    salvar_csv("estabilidade_m437_impresso_x_recalculado.csv", ["mach", "coluna", "impresso", "recalculado", "diferenca"], linhas)
    resumo = []
    for c in cols:
        d = (e[c] - tab[c])[2:]; resumo.append((c, float(np.max(np.abs(d))), float(np.mean(d / tab[c][2:])) * 100))
    return svg(fig), resumo


# ------------------------------------------------------------------ 4. Experimento (7,62 NATO)
def secao_exp():
    rows = cmag.EXP; geo = cmag.GEO
    fig, axs = plt.subplots(2, 4, figsize=(11.5, 5.2), sharex=True)
    Mg = np.linspace(1.1, 2.9, 60)
    viés = []
    for k, proj in enumerate(["M-80", "M-59", "M-61", "M-62"]):
        g = geo[proj]; R = [r for r in rows if r["projetil"] == proj and float(r["MACH"]) >= 1.1]
        ax = axs[0, k]
        m = [float(r["MACH"]) for r in R if r["CNA"]]; y = [float(r["CNA"]) for r in R if r["CNA"]]
        ax.plot(m, y, "^", mfc="none", mec="#6b4c9a", ms=5, label="voo livre (MR 1833)")
        c = [cna_spin(g["VL"], g["VN"], g["VB"], 9.74, M) for M in Mg]
        reproducao(ax, Mg, c, label="SPIN-73 reconstruído")
        ax.set_title(f"{proj}: CNα", fontsize=8.5); ax.set_ylim(1.5, 4)
        pc = [cna_spin(g["VL"], g["VN"], g["VB"], 9.74, M) for M in m]
        viés.append((proj, "CNα", float(np.mean(np.array(pc) - np.array(y))), float(np.std(y)), len(y)))
        ax = axs[1, k]
        m = [float(r["MACH"]) for r in R if r["CMPA"]]; y = [2 * float(r["CMPA"]) for r in R if r["CMPA"]]
        ax.plot(m, y, "^", mfc="none", mec="#6b4c9a", ms=5, label="voo livre (MR 1833)")
        yaw = np.mean([float(r["YAW_RMS_DEG"]) for r in R if r["CMPA"]])
        reproducao(ax, Mg, [cmag.cnpa_spin(g, M, yaw) for M in Mg], label="SPIN-73 reconstruído")
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_title(f"{proj}: Magnus Cnpα (p·d/2V)", fontsize=8.5); ax.set_xlabel("Mach")
        pc = [cmag.cnpa_spin(g, float(r["MACH"]), float(r["YAW_RMS_DEG"])) for r in R if r["CMPA"]]
        viés.append((proj, "Cnpα", float(np.mean(np.array(pc) - np.array(y))), float(np.std(y)), len(y)))
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout()
    return svg(fig), viés


if __name__ == "__main__":
    import json
    f1, grade, st_cna = secao_cna()
    f2, st_mag = secao_magnus()
    f3, st_est = secao_estab()
    f4, st_exp = secao_exp()
    json.dump(dict(st_cna=st_cna, st_mag=st_mag, st_est=st_est, st_exp=st_exp,
                   grade=[(p, n, [None if not np.isfinite(x) else round(float(x), 4) for x in g]) for p, n, g in grade],
                   correcoes=[(b, float(MACH[j]), l, d) for (b, j), (l, d) in CORRECOES.items()]),
              open(os.path.join(AQUI, "resultados.json"), "w"), ensure_ascii=False, indent=1)
    for i, f in enumerate((f1, f2, f3, f4), 1):
        open(os.path.join(AQUI, f"fig{i}.svg"), "w").write(f)
    print("ok", st_cna, len(st_mag), st_exp)
