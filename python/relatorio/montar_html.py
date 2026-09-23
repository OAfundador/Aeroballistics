"""Monta relatorio_spin73.html a partir das figuras e resultados gerados por gerar_relatorio.py."""
import json, os, html, datetime
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(AQUI, "resultados.json")))
F = [open(os.path.join(AQUI, f"fig{i}.svg")).read() for i in (1, 2, 3, 4)]
MACH = [0.01, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]
fmt = lambda x, n=3: f"{x:.{n}f}".replace(".", ",")
e = html.escape

c = R["st_cna"]
pct = lambda a, b: f"{100 * a / b:.0f} %"

# --- mapa de resíduos do CNa
mapa = ['<table class="gb mapa"><thead><tr><th>Tabela</th>' + "".join(f"<th>{fmt(m, 2)}</th>" for m in MACH) + "</tr></thead><tbody>"]
for p, n, g in R["grade"]:
    cel = []
    for x in g:
        if x is None: cel.append('<td class="na">—</td>')
        elif abs(x) <= 0.0015: cel.append('<td class="ok">·</td>')
        else: cel.append(f'<td class="bad">{x:+.3f}'.replace(".", ",") + "</td>")
    mapa.append(f"<tr><th>{e(n)} <span class='pg'>p. {p}</span></th>{''.join(cel)}</tr>")
mapa.append("</tbody></table>")

# --- Magnus
mag = ['<table class="gb"><thead><tr><th>Projétil</th><th>Coluna</th><th>Células reproduzidas (±0,001)</th></tr></thead><tbody>']
for n, col, ok, tot in R["st_mag"]:
    cls = "" if ok == tot else ' class="warn"'
    mag.append(f"<tr{cls}><td>{e(n)}</td><td>{col}</td><td class='num'>{ok} de {tot}</td></tr>")
mag.append("</tbody></table>")

# --- estabilidade
nomes = dict(GYRO="fator giroscópico s_g", SBAR="fator dinâmico s_d (1°)", SBAR5="fator dinâmico s_d (5°)",
             SPIN="rotação p (rad/s)", W1="nutação ω₁ (rad/s)", W2="precessão ω₂ (rad/s)",
             L1="amortecimento λ₁ (1°)", L2="amortecimento λ₂ (1°)", L15="amortecimento λ₁ (5°)", L25="amortecimento λ₂ (5°)")
est = ['<table class="gb"><thead><tr><th>Grandeza</th><th>Maior diferença</th><th>Diferença média</th></tr></thead><tbody>']
for col, mx, rel in R["st_est"]:
    v = f"{mx:.1e}".replace(".", ",") if mx < 1e-3 else fmt(mx, 3 if mx < 1 else 1)
    est.append(f"<tr><td>{nomes[col]}</td><td class='num'>{v}</td><td class='num'>{rel:+.2f} %".replace(".", ",") + "</td></tr>")
est.append("</tbody></table>")

# --- experimento
exp = ['<table class="gb"><thead><tr><th>Projétil</th><th>Coeficiente</th><th>Viés do SPIN-73</th><th>Dispersão do experimento</th><th>Rodadas</th></tr></thead><tbody>']
for proj, co, b, sd, n in R["st_exp"]:
    cls = ' class="warn"' if abs(b) > sd else ""
    exp.append(f"<tr{cls}><td>{proj}</td><td>{co}</td><td class='num'>{b:+.2f}</td><td class='num'>{sd:.2f}</td><td class='num'>{n}</td></tr>".replace(".", ","))
exp.append("</tbody></table>")

cor = "".join(f"<tr><td>B{b}</td><td class='num'>{fmt(m, 2)}</td><td class='num'>{l:+.4f}</td><td class='num'>{d:+.4f}</td></tr>".replace(".", ",") for b, m, l, d in R["correcoes"])

doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>SPIN-73 reconstruído: comparação com as tabelas de 1973</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root {{ box-sizing: border-box; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px);
  --bg:#f5f7f4; --ink:#1f2a36; --muted:#5b6875; --bar:#e2eee0; --rule:#c9d6c6; --blue:#2b5d8a; --red:#b3261e; --panel:#ffffff; --warn:#fbeae8; }}
html {{ scroll-padding-top: env(safe-area-inset-top, 0px); }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#141a1f; --ink:#e3e8ec; --muted:#9aa7b2; --bar:#1d2a22; --rule:#32443a; --blue:#8bb6dd; --red:#ef8a80; --panel:#ffffff; --warn:#3a2220; }} }}
:root[data-theme="dark"] {{ --bg:#141a1f; --ink:#e3e8ec; --muted:#9aa7b2; --bar:#1d2a22; --rule:#32443a; --blue:#8bb6dd; --red:#ef8a80; --panel:#ffffff; --warn:#3a2220; }}
*, *::before, *::after {{ box-sizing: inherit; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.6 "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 72rem; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }}
.prosa {{ max-width: 44rem; }}
h1 {{ font-size: clamp(1.9rem, 4vw, 2.7rem); line-height:1.15; margin:0 0 .6rem; font-weight:600; letter-spacing:-.01em; }}
h2 {{ font-size:1.45rem; margin:3.2rem 0 .6rem; font-weight:600; }}
p {{ margin:.6rem 0; }}
.sub {{ color:var(--muted); font-size:1.05rem; }}
.legenda {{ color:var(--muted); font-size:.92rem; }}
figure {{ margin:1.2rem 0; background:var(--panel); border:1px solid var(--rule); padding:.8rem; overflow-x:auto; }}
figure svg {{ max-width:100%; height:auto; display:block; min-width:640px; }}
.rolagem {{ overflow-x:auto; margin:1rem 0; }}
table.gb {{ border-collapse:collapse; font-family:"IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; font-size:.84rem; }}
table.gb th, table.gb td {{ padding:.28rem .6rem; text-align:left; border-bottom:1px solid var(--rule); }}
table.gb thead th {{ font-family:"IBM Plex Sans", sans-serif; font-weight:600; font-size:.85rem; border-bottom:2px solid var(--ink); }}
table.gb tbody tr:nth-child(even) {{ background:var(--bar); }}
table.gb td.num {{ text-align:right; }}
tr.warn td {{ background:var(--warn); }}
table.mapa td {{ text-align:center; min-width:3.4rem; }}
table.mapa td.ok {{ color:var(--muted); }}
table.mapa td.bad {{ color:var(--red); font-weight:500; }}
table.mapa td.na {{ color:var(--muted); }}
table.mapa tbody th {{ font-weight:400; white-space:nowrap; font-family:"IBM Plex Sans", sans-serif; }}
.pg {{ color:var(--muted); font-size:.8rem; }}
.placar td {{ font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.9rem; }}
a {{ color:var(--blue); }}
</style></head>
<body><main>
<header class="prosa">
<h1>SPIN-73 reconstruído, comparado com as tabelas impressas em 1973</h1>
<p class="sub">Whyte, <i>SPIN-73, an Updated Version of the SPINNER Computer Program</i>, Picatinny Arsenal TR 4588 (DTIC AD0915628, Distribution A). Cada gráfico põe os valores impressos pelo programa original (círculos) contra a reconstrução em Python (linha).</p>
</header>

<div class="rolagem"><table class="gb placar"><thead><tr><th>Parte do programa</th><th>Como foi obtida</th><th>Concordância com as tabelas de 1973</th></tr></thead><tbody>
<tr><td>Força normal CNα</td><td>DATA XB1..XB9 lidos do listing</td><td>{c['ok']} de {c['n']} células no arredondamento ({pct(c['ok'], c['n'])}); {pct(c['ok5'], c['n'])} dentro de ±0,005</td></tr>
<tr><td>Magnus (CYPA, CPF1, CPF5) e Clp</td><td>coeficientes identificados pelas tabelas + termo de corpo longo</td><td>6 projéteis; divergências só em pares de glifos ambíguos</td></tr>
<tr><td>Estabilidade (s_g, s_d, ω, λ)</td><td>equações do relatório, com o sinal de λ corrigido</td><td>175 mm M437 inteiro; s_g com viés de −0,17 % em aberto</td></tr>
<tr><td>Arrasto, centro de pressão, amortecimento Cmq</td><td>DATA XA, XC e XF ainda não lidos</td><td>não reproduzidos</td></tr>
</tbody></table></div>

<section class="prosa"><h2>Força normal CNα</h2>
<p>Dez tabelas de saída, 17 números de Mach cada. A reconstrução usa a equação da p. 14 do relatório com os valores de B1..B9 lidos dos blocos DATA. As próprias tabelas corrigiram duas coisas: uma de estrutura (o programa troca o expoente do boattail já em Mach 0,95) e uma de leitura minha (o 20 mm M56A3 tem CNα 2,106, e não 2,186, no subsônico).</p></section>
<figure>{F[0]}</figure>
<p class="legenda prosa">Mapa de diferenças (reconstrução − impresso). Um ponto indica concordância dentro do arredondamento da impressão (±0,0015). A tabela do 90 mm M71 é a transcrição mais degradada. No 5"/38, o desvio constante acima de Mach 2,5 sugere erro na minha leitura da coluna CNA.</p>
<div class="rolagem">{''.join(mapa)}</div>
<p class="legenda prosa">Seis valores de B foram decididos pelo modelo, e não pela leitura: cada um é o único número que zera a diferença de sete ou mais tabelas ao mesmo tempo. Ainda precisam ser reconferidos na imagem.</p>
<div class="rolagem"><table class="gb"><thead><tr><th>Coeficiente</th><th>Mach</th><th>Lido</th><th>Decidido</th></tr></thead><tbody>{cor}</tbody></table></div>

<section class="prosa"><h2>Magnus e centro de pressão de Magnus</h2>
<p>Os coeficientes E1, E2 e E4 saíram de uma única tabela (175 mm M437) e prevêem as outras. Nos projéteis com mais de 6 calibres aparece um termo que o texto do relatório não descreve; a linha pontilhada mostra o que a equação do texto daria sem ele.</p></section>
<figure>{F[1]}</figure>
<div class="rolagem">{''.join(mag)}</div>

<section class="prosa"><h2>Estabilidade do 175 mm M437</h2>
<p>Recalculada a partir dos coeficientes impressos na própria tabela, sem nenhum coeficiente de ajuste. A fórmula das taxas de amortecimento λ só reproduz a tabela com o sinal do termo de CNα trocado em relação ao texto da p. 18.</p></section>
<figure>{F[2]}</figure>
<div class="rolagem">{''.join(est)}</div>

<section class="prosa"><h2>Contra o experimento: 7,62 mm NATO</h2>
<p>Voo livre do BRL MR 1833 (Piddington, 1967), no supersônico. Os dados de Magnus foram convertidos para a normalização do SPIN-73 (p·d/2V). Linhas destacadas: viés maior que a dispersão do experimento.</p></section>
<figure>{F[3]}</figure>
<div class="rolagem">{''.join(exp)}</div>
<p class="prosa legenda">O CNα concorda com M-59, M-61 e M-62. No M-80, o mais curto, o SPIN-73 superestima: prevê CNα maior para o projétil mais curto, enquanto o experimento mostra o contrário. O Magnus é superestimado nos quatro; a troca de sinal que o experimento mostra abaixo de Mach 1,5 não aparece no modelo.</p>

<section class="prosa"><h2>Arquivos</h2>
<p>As tabelas completas estão no pacote, em <code>relatorio/</code>: <code>cna_impresso_x_reconstruido.csv</code>, <code>magnus_impresso_x_reconstruido.csv</code> e <code>estabilidade_m437_impresso_x_recalculado.csv</code>. Este relatório é gerado por <code>python gerar_relatorio.py && python montar_html.py</code>.</p>
<p class="legenda">Gerado em {datetime.date.today().strftime('%d/%m/%Y')}.</p></section>
</main></body></html>"""
open(os.path.join(AQUI, "relatorio_spin73.html"), "w", encoding="utf-8").write(doc)
print(len(doc))
