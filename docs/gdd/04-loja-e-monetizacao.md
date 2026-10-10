# 04 — Loja e monetização

## Modelo

- Jogo **100% gratuito**. Nenhuma funcionalidade, quest, região ou história fica atrás de pagamento.
- **Única monetização:** cosméticos para o personagem (e, futuramente, para o companheiro e a casa).
- **Todo item da loja pode ser obtido com Faíscas.** O dinheiro real só adianta o acesso.

## Regras éticas (inegociáveis)

O público do jogo está, por definição, em um momento vulnerável. Táticas comuns em jogos mobile — que já são questionáveis em geral — aqui seriam exploração. Por isso:

1. **Sem aleatoriedade.** Nada de caixas de recompensa (*loot boxes*), gacha, roletas ou baús surpresa. A pessoa sempre vê exatamente o item que vai comprar.
2. **Sem pressão de tempo.** Nada de "oferta termina em 02:59:59", itens que saem da loja para sempre ou pacotes "só hoje".
3. **Catálogo permanente.** Um item lançado nunca sai da loja. Itens sazonais (Natal, São João) voltam todo ano e podem ser comprados com Faíscas em qualquer momento.
4. **Preço claro, em reais.** Sem moeda premium intermediária (ver abaixo).
5. **Contexto emocional respeitado.** A loja **nunca** aparece, nem é sugerida, logo após um check-in de humor baixo, nem como "recompensa" para se sentir melhor. Nenhuma notificação fala da loja.
6. **Sem anúncios.** Nem banners, nem vídeos recompensados.
7. **Sem comparação social.** Nada de "X amigos já compraram", ranking de quem tem mais itens, etc.
8. **Itens de marcos não são vendidos.** Os cosméticos dos marcos de dias acesos e das jornadas não podem ser comprados — são símbolos de cuidado, não de dinheiro.

### Sem moeda premium

Muitos jogos vendem uma moeda (diamantes, gemas) em pacotes que nunca batem com o preço dos itens. Isso esconde o preço real e deixa "troco" que incentiva comprar mais. **Aqui, cada item tem um preço em reais e é comprado diretamente**, como alternativa ao preço em Faíscas.

## Tela de um item

```
┌───────────────────────────────┐
│     [ prévia no personagem ]  │
│                               │
│  Chapéu de Cogumelo  · Raro   │
│                               │
│  [ 1.200 Faíscas ]            │
│   Você tem 830 — faltam 370   │
│   (~6 dias no seu ritmo)      │
│                               │
│  ou  [ R$ 9,99 ]              │
└───────────────────────────────┘
```

- O botão de Faíscas vem **primeiro** e com mais destaque.
- Mostrar a estimativa de quanto falta "no seu ritmo" deixa claro que o item é alcançável sem pagar.
- A pessoa pode **experimentar** qualquer item no personagem antes de comprar.
- Lista de desejos: marcar um item e acompanhar o progresso de Faíscas até ele.

## Preços em dinheiro real (referência inicial)

| Raridade | Faíscas | R$ |
|----------|---------|----|
| Comum | 150 | 2,99 |
| Incomum | 400 | 4,99 |
| Raro | 1.200 | 9,99 |
| Épico | 3.000 | 14,99 |

Ajustar após pesquisa de mercado (preços de cosméticos no Finch e em jogos brasileiros) e de acordo com as faixas de preço permitidas pela Google Play.

## Pacote apoiador

Para quem quer apoiar o projeto sem necessariamente querer um item específico:

- Três faixas: **R$ 5, R$ 15 e R$ 30**.
- Todas dão o **mesmo** item simbólico (ex.: uma pequena lanterna que segue o personagem) e o nome nos créditos, se a pessoa quiser.
- Texto honesto: *"O jogo é gratuito e vai continuar sendo. Se ele te ajudou e você pode, isso ajuda a manter o projeto."*
- Aparece em uma aba própria, nunca em pop-up.

## Catálogo inicial (MVP)

Meta para o lançamento: **~30 itens na loja** além dos gratuitos.

| Categoria | Comum | Incomum | Raro | Épico |
|-----------|-------|---------|------|-------|
| Chapéus / acessórios de cabeça | 4 | 3 | 2 | 1 |
| Roupas | 4 | 3 | 2 | 1 |
| Acessórios (óculos, cachecol, mochila) | 3 | 2 | 1 | — |
| Cabelos especiais | 2 | 1 | 1 | — |

Os acessórios de cabeça são o carro-chefe (referência: *headgears* do Ragnarok) — e, tecnicamente, são os mais baratos de produzir (ver [05](05-direcao-de-arte.md#âncora-de-cabeça)).

## Expectativa de receita (realista)

- Em jogos gratuitos, tipicamente **2–5%** dos jogadores ativos gastam algum dinheiro.
- Com 10.000 jogadores ativos/mês, 3% pagantes e gasto médio de R$ 12/mês: **~R$ 3.600/mês** brutos, antes da taxa da loja (15% para os primeiros US$ 1 milhão/ano na Google Play) e impostos.
- Conclusão: viável como projeto independente que se sustenta aos poucos; não contar com isso como renda no curto prazo.
