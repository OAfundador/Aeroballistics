# Usar o SPIN-73 como biblioteca

## Instalação

Na raiz do repositório:

```
pip install -e .
```

`-e` instala no modo editável: o seu código passa a enxergar o pacote `spin73` que está em `python/spin73/`, e qualquer mudança no repositório vale na hora, sem reinstalar. A única dependência é o numpy.

## Num simulador 6DOF

```python
import numpy as np
import spin73

p = spin73.Projetil(VL=4.05, VN=1.90, VB=0.40, VCG=2.51, OR=7.9, DM=0.12,
                    DIA=0.224, nome="M855")          # calibres; DIA em polegadas

aero = spin73.Aerodinamica(p,
                           correcoes="voo_livre",    # ou None para o SPIN-73 de 1973
                           convencao="moderna")      # ou "spin73"

# dentro do laço de integração
c = aero(mach)                 # escalar ou array
CD = c.CD0 + c.CDd2 * np.sin(alfa) ** 2
Cmpa = aero.momento_magnus(mach, alfa)   # Magnus secante, entre 1° e 5°
```

O exemplo usa a correção opcional de voo livre; sem `correcoes`, é o programa de 1973.

A aerodinâmica é calculada **uma vez**, no construtor, nos 17 Mach do programa. Cada chamada só faz interpolação linear em Mach (`numpy.interp`), então é barata o bastante para o laço de integração. Fora de 0,01 a 5, o padrão é usar o valor do extremo (`fora_da_faixa="limitar"`); as alternativas são `"nan"` e `"erro"`.

### Coeficientes disponíveis

| `convencao="spin73"` | `convencao="moderna"` | Significado |
|---|---|---|
| `CX0` | `CD0` | arrasto a guinada zero |
| `CX2` | `CDd2` = CX2 + CNα | arrasto de guinada, por sen²α |
| `CNA` | `CNa`, `CLa` = CNα − CD0 | força normal / sustentação, por sen α |
| `CMA` | `Cma` | momento de arfagem em torno do CG, por sen α (positivo tomba) |
| `CPN` | `CP_nariz`, `CP_base` | centro de pressão, calibres |
| `CMQ` (qd/2V) | `Cmq_Cmad` (qd/V) = CMQ/2 | amortecimento em arfagem, Cmq + Cmα̇ |
| `CLP` (pd/2V) | `Clp` (pd/V) = CLP/2 | amortecimento de rolamento |
| `CYPA` (pd/2V) | `CNpa` (pd/V) | força de Magnus |
| `CNPA`, `CNPA5` (pd/2V) | `Cmpa`, `Cmpa_5graus` (pd/V) | momento de Magnus a 1° e 5° (secante) |
| `CPF1`, `CPF5` | `CPmagnus_nariz` | centro de pressão do Magnus, calibres do nariz |

Os momentos são em torno do CG que está no `Projetil` (`VCG`, em calibres a partir do nariz). Detalhes das conversões em `python/spin73/convencoes.py`.

### Entradas em outras unidades

O `Projetil` é o cartão do SPIN-73: calibres, polegadas, libras, lb·in² e °F. `spin73.unidades` monta o mesmo cartão a partir de unidades métricas (conversão exata, nada mais):

```python
p = spin73.unidades.projetil(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12,
                             D_MM=5.69, MASSA_G=4.05, IX_GCM2=0.1426, IY_GCM2=1.150,
                             PASSO_POL=7, TEMP_C=15, CG_BASE=1.54)
```

| Chave | Unidade | Vira |
|---|---|---|
| `D_MM` | mm | `DIA` |
| `MASSA_G`, `MASSA_KG` | g, kg | `WGT` |
| `IX_GCM2`, `IY_GCM2`, `IX_KGM2`, `IY_KGM2` | g·cm², kg·m² | `IX`, `IY` |
| `PASSO_MM`, `PASSO_POL` | uma volta da raia, mm ou polegadas | `TWIST` (calibres por volta) |
| `TEMP_C` | °C | `TEMP` |
| `CG_BASE` | CG a partir da **base**, calibres | `VCG` = VL − CG_BASE |
| `DGUN_MM` | mm | `DGUN` |

As mesmas chaves valem no arquivo de entrada da linha de comando (`spin73 --entrada`), e cada uma tem uma opção (`--d-mm`, `--massa-g`, `--cg-base`...).

### Quando faltam CG, massa ou inércias

`spin73.massa` estima o que o cartão não tem, a partir da geometria. Nunca troca um valor informado.

```python
p = spin73.Projetil(VL=4.05, VN=1.90, VB=0.40, OR=7.9, DM=0.12)      # sem VCG, peso, inércias
p = spin73.massa.completar(p, "solido", massa_g=4.05, d_mm=5.69)     # preenche VCG, WGT, IX, IY
print(spin73.massa.estimar(p, "solido", massa_g=4.05, d_mm=5.69))   # o que foi estimado
```

| Método | O que é | Quando usar |
|---|---|---|
| `"solido"` | sólido de revolução homogêneo com a geometria do cartão | balas; é o único que dá o CG sem a massa e a massa pela densidade (`densidade=` em kg/m³ ou `material="chumbo"`) |
| `"bala"` | fórmulas empíricas de Hitchcock (BRL 620) para balas .30 e .50 | balas, com a massa |
| `"granada"` | as mesmas, para granadas explosivas | granadas ocas, com a massa |

Contra 20 projéteis com valores medidos, com a massa medida dada: em balas, o CG fica a ±0,12 calibre e a inércia axial de −5 % a +3 % (`solido`). Em granadas, o `granada` fica de −11 % a +3 %; o `solido` subestima em 20 a 27 %, porque a massa da granada está na parede. Traçantes erram o CG em 0,2 a 0,45 calibre. Detalhes em `python/experimental/massa/LEIAME.md`.

## Escolher o modelo

| O que muda | Como |
|---|---|
| Nada: o programa de 1973 | `Aerodinamica(p)` |
| Correção de voo livre completa | `correcoes="voo_livre"` |
| Só parte dela | `correcoes="voo_livre:CX0"` ou `"voo_livre:CX0,CNA"` |
| Uma correção sua | `correcoes=MinhaCorrecao()` ou uma lista, aplicada na ordem |
| Outros blocos `DATA` | `dados=CoefAjuste(...)` (por exemplo, constantes recalibradas) |

`aero.descrever()` diz o que foi aplicado; `aero.tabela_original` guarda a saída sem correção, para comparar.

Nem toda peça da correção de voo livre é igualmente firme. `correcoes.VooLivre().validacao()` devolve, por coeficiente e regime, o erro nos grupos de projéteis deixados de fora e `pior_razao`, o quanto o grupo mais prejudicado piorou (a regra de aceitação corta em 2). O **CX0** é a peça robusta: melhora 7 de 9–10 grupos nos três regimes e nenhum piora mais que 1,5×. As outras peças aceitas passaram perto do limite, e por isso `"voo_livre:CX0"` é a escolha conservadora.

## Escrever uma correção nova

Uma correção é qualquer objeto com `nome` e `aplicar(t, p, ctx)`. `t` é a tabela na convenção do SPIN-73: um array de 17 valores por coluna, nas colunas de `spin73.tabela`. `ctx.d_mm` é o diâmetro real, quando existir.

```python
from spin73 import correcoes

class MagnusMenor(correcoes.Correcao):
    nome = "magnus_menor"
    descricao = "momento de Magnus × 0,8 no supersônico"

    def aplicar(self, t, p, ctx):
        out = correcoes.base.copiar(t)
        sup = t["MACH"] >= 1.25
        out["CNPA"][sup] *= 0.8
        out["CNPA5"][sup] *= 0.8
        return out

correcoes.registrar("magnus_menor", MagnusMenor)     # opcional: chamar pelo nome
aero = spin73.Aerodinamica(p, ["voo_livre", "magnus_menor"])
```

A correção não precisa cuidar das colunas derivadas. Depois de todas as correções, a biblioteca recalcula:

- CPN = VCG − CMα/CNα;
- CPF1 e CPF5 a partir do Magnus;
- o CX2, preservando o arrasto de guinada CX2 + CNα;
- a análise de estabilidade, se o projétil tiver massa e passo de raia.

## O que é o quê

| Módulo | Conteúdo | Canônico ou adição |
|---|---|---|
| `spin73.nucleo` | equações, `tabela()`, `estabilidade()`, o cartão `Projetil` | **canônico**: é o programa |
| `spin73.dados` | blocos `DATA` XA..XG, com a proveniência de cada valor | **canônico**: é o programa |
| `spin73.aero` | `Aerodinamica`, a interface para simuladores | sem opções, canônico |
| `spin73.convencoes` | saída na convenção moderna | adição: conversão exata |
| `spin73.unidades` | entrada em unidades métricas | adição: conversão exata |
| `spin73.massa` | estimativa de CG, massa e inércias | adição: muda entradas que faltavam |
| `spin73.correcoes` | correções dos coeficientes e a interface para escrever novas | adição: muda saídas, só se pedidas |
| `spin73.cli` | linha de comando | diz no cabeçalho se a saída é canônica ou tem adições |

As correções são **ajustadas** em `python/experimental/correcao/`, com validação cruzada deixando um grupo de projéteis de fora (ver o LEIAME de lá). O ajuste grava `spin73/correcoes/voo_livre.json`, que a biblioteca só lê. Para refazer o ajuste depois de acrescentar dados:

```
python python/experimental/correcao/ajuste.py
```
