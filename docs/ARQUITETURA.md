# Arquitetura

Por que o código está dividido assim, e onde acrescentar coisas.

## Camadas

```
                     ┌───────────────────────────────────┐
   interfaces  ───▶  │  aero (Aerodinamica) · cli        │   simuladores e linha de comando
                     ├───────────────────────────────────┤
   opcionais   ───▶  │  convencoes · unidades · massa ·  │   mudam a apresentação, as entradas
                     │  correcoes                        │   ou as saídas, só quando pedidas
                     ├───────────────────────────────────┤
   canônico    ───▶  │  nucleo · dados  (+ programa)     │   o programa de 1973
                     └───────────────────────────────────┘
```

As dependências só apontam para baixo: as adições importam do núcleo, e o núcleo não importa nenhuma adição. Sem opções, `aeroballistics.Aerodinamica(p)` é a tabela canônica interpolada em Mach, e a linha de comando abre a saída com `Modo: canônico (SPIN-73 de 1973)`.

## O pacote, módulo a módulo

| Módulo | Papel | Depende de | Camada |
|---|---|---|---|
| `nucleo` | as equações, `tabela()`, `estabilidade()`, `formatar()`, `avisos()`, o cartão `Projetil` e o `M437` | `dados` | canônico |
| `dados/` | os blocos `DATA` XA … XG; cada `x?_lidos.py` guarda a leitura, as células decididas e a evidência | — | canônico |
| `programa` | o programa original descrito como objetos (`SPIN73`); gera `docs/PROGRAMA_ORIGINAL.md` | `nucleo` | documentação |
| `convencoes` | convenção do relatório ↔ convenção moderna (conversão exata) | — | adição |
| `unidades` | entradas em mm, g, g·cm², °C, CG a partir da base (conversão exata) | `nucleo` | adição |
| `massa` | estimativa de CG, massa e inércias que faltam no cartão | `nucleo` | adição |
| `correcoes/` | a interface `Correcao`, o registro por nome, `finalizar` (recalcula as colunas derivadas) e a correção `voo_livre`, que só lê o JSON gerado pelo ajuste | `nucleo` | adição |
| `aero` | `Aerodinamica`: aplica correções e convenção e interpola em Mach | `nucleo`, `convencoes`, `correcoes` | interface |
| `cli` | o comando `aeroballistics` | todos | interface |

## Um cálculo, do cartão ao simulador

```
entradas                 canônico                     saídas (opcional)              consulta
─────────────────────    ──────────────────────────   ────────────────────────────   ─────────────────────
unidades → Projetil  ─▶  nucleo.tabela(p)          ─▶ correções → finalizar       ─▶ convenção → Mach
massa (se faltar)        17 Mach × todas as colunas   (CPN, CPF, CX2, estabilidade)  Aerodinamica(mach)
```

`unidades` e `massa` agem **antes** do programa, nas entradas; `correcoes` age **depois**, nas saídas. Uma correção nunca precisa manter as colunas derivadas: `finalizar` as recalcula depois de todas.

## O repositório

```
src/aeroballistics/ o pacote (acima)
tests/             a suíte: python -m pytest (adaptação, tabelas de 1973, biblioteca, adições)
scripts/
  caminhos.py      os caminhos do repositório; põe src/ e as pastas de scripts no sys.path
  adaptacao/       como cada DATA foi decidido: análises por bloco, leitura e conferência das
                   tabelas de 1973, circularidade e comparacao_erros.py (VERIFICACAO.md)
  voo_livre/       o SPIN-73 contra medições: benchmarks/, correcao/ (gera o JSON da correção),
                   mr1833/ (7,62 NATO) e hitchcock/ (BRL 620)
  massa/           a validação da estimativa de massa (MASSA.md)
  leitura/         leitura do scan e dos PDFs: recortes, páginas de PDF, decodificador JBIG2
examples/          exemplos executáveis (examples/README.md) e cartões de entrada em entradas/
data/
  tabelas_1973/    as 13 tabelas de saída do relatório, transcritas; leituras/ tem a leitura bruta
  voo_livre/       medições de voo livre, rodada a rodada, na convenção de cada fonte
docs/              notas de transcrição, o programa original, verificação, biblioteca, massa,
                   voo_livre/ e resultados/ (saídas de referência dos scripts)
output/            o que os scripts e os exemplos gravam (fora do Git)
fontes/            PDFs e o scan (fora do Git; ver fontes/LEIAME.md)
```

## O que a estrutura protege

- **O canônico não muda por acidente.** Tudo o que altera resultados vive fora do núcleo e só entra quando pedido.
- **Nada decidido valida a si mesmo.** `scripts/adaptacao/circularidade.py` lê as decisões registradas em `aeroballistics.dados.x?_lidos`, em `dados_cna.py` e nas linhas `decidir:` dos CSV das tabelas, e marca as células circulares. Elas ficam fora das estatísticas dos testes e da verificação.
- **Dados separados do código.** As tabelas de 1973 e as medições ficam em `data/`, em CSV com a proveniência no cabeçalho. Scripts e testes as acham por `scripts/caminhos.py` (os testes, via `tests/conftest.py`).
- **Tudo roda de um clone, sem instalar.** Cada script começa pondo `scripts/` no `sys.path` e importando `caminhos`; os exemplos usam `examples/_bootstrap.py`. Com `pip install -e .`, esses caminhos só ficam redundantes.

## Onde acrescentar

- **Uma correção nova:** uma classe com `nome` e `aplicar(t, p, ctx)` ([BIBLIOTECA.md](BIBLIOTECA.md)), registrada com `aeroballistics.correcoes.registrar` para ser chamada pelo nome. Se ela for ajustada a dados, o ajuste fica em `scripts/` e o resultado num arquivo que a biblioteca só lê, como `correcoes/voo_livre.json`.
- **Uma medição de voo livre:** um CSV em `data/voo_livre/`, com as convenções da fonte no cabeçalho; o carregador em `scripts/voo_livre/correcao/dados.py`; o teste em `tests/`.
- **Uma releitura de `DATA`:** no `src/aeroballistics/dados/x?_lidos.py` do bloco, com a classe (verificado, decidido pelo modelo ou pendente) e a evidência. Se ela for decidida por alguma tabela, registre isso nas estruturas que `circularidade.py` lê (`DECIDIDOS`, `CORRECOES`, `RECUPERADOS`) e confira que as células usadas saem da validação.
- **Uma tabela de 1973 relida:** a leitura bruta em `data/tabelas_1973/leituras/`, o CSV gerado por `scripts/adaptacao/resolver_glifos.py` e conferido, sem o modelo, por `scripts/adaptacao/verificar_identidades.py`.
