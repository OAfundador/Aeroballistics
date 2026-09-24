# Estimativa de massa: validação

O SPIN-73 recebe o CG, o peso e as inércias como entrada. `spin73.massa` é uma **adição opcional** que os estima quando faltam. `scripts/massa/validar.py` mede quanto a estimativa erra, contra projéteis com massa, CG e inércias medidos e publicados.

```
python scripts/massa/validar.py      # tabela completa; cópia em docs/resultados/massa.txt
```

## Métodos

| Método | O que é | Precisa |
|---|---|---|
| `solido` | sólido de revolução homogêneo com o contorno do cartão (ogiva de raio OR com meplat, cilindro, boattail cônico), integrado numericamente | só a geometria para o CG; massa ou densidade para o resto |
| `bala` | fórmulas empíricas do BRL para balas .30 e .50 (Hitchcock, BRL 620, p. 9, citando o BRL X-113): CG a 0,400 L da base, A = 0,115 m d², B = 0,5 A + 0,0543 m L² | massa |
| `granada` | as mesmas para granadas explosivas: 0,375 L, A = 0,140 m d², B = 0,5 A + 0,0594 m L² | massa |

A = inércia axial; B = transversal, em torno do CG; L = comprimento; d = diâmetro; m = massa.

## Dados

Vinte projéteis, de 5,56 mm a 175 mm, com as fontes no cabeçalho de `validar.py`. A massa medida entra como dado: é o que quase sempre se sabe. O que se testa é a **distribuição** dela.

Três grupos pedem cuidado ao ler:

- **Traçantes** (L110, M856, Tracer M1): a composição traçante na base é leve, e o CG real fica 0,2 a 0,45 cal à frente do de um sólido homogêneo. Nenhum método baseado só na geometria acerta isso.
- **Cal .30 de Hitchcock** (marcados com `*`): são da mesma família de balas de onde saíram as fórmulas `bala`. Para esse método, não são teste independente.
- **Especiais**: o XM617 é um projétil de baixa densidade, e o T203 é um *slug* balístico de 90 mm com a massa concentrada no centro. Nenhum dos dois é granada típica.

## Resultado

Razão estimado/medido, com a massa medida como dado:

| Classe | Método | CG (erro) | Ix | Iy | s_g (∝ Ix²/Iy) |
|---|---|---|---|---|---|
| balas (SS-109, M855, M118, 190 e 168 Sierra, .50 M33) | `solido` | ±0,12 cal | 0,95–1,03 | 1,03–1,20 | 0,83–1,03 |
| | `bala` | ±0,12 cal | 1,03–1,11 | 1,03–1,14 | 0,99–1,19 |
| granadas (30 mm ×3, M437, M101, M483A1) | `solido` | até 0,20 cal | 0,73–0,81 | 0,90–1,32 | 0,50–0,66 |
| | `granada` | até 0,14 cal | 0,89–1,03 | 0,98–1,38 | 0,72–0,95 |

## Leitura

- **Para balas, os dois métodos servem**, e o `solido` tem a vantagem de dar o CG sem a massa e a massa pela densidade. A densidade efetiva das balas encamisadas medidas fica entre 9,3 e 10,3 g/cm³ (a .50 M33 fica em 7,7).
- **Para granadas, use `granada`.** A granada é oca: a massa fica na parede, e o sólido homogêneo subestima a inércia axial em 20 a 27 %. Como o fator giroscópico vai com Ix², o erro chega a 50 % nele.
- **O Iy é o menos confiável**, sobretudo em projéteis longos com carga interna (M483A1, que leva submunições: +32 % no sólido e +38 % em Hitchcock).

## Limites

O contorno não tem cinta, canelura, cavidade nem ponta ou base arredondadas (a base arredondada entra como tronco de cone). O ângulo do boattail não é entrada do SPIN-73: o padrão é 8°, e pode ser informado (`ang_bt`) ou trocado pelo diâmetro da base (`db`). Quando o CG e as inércias medidos existirem, eles devem ser usados: a estimativa só preenche o que o cartão não tem.
