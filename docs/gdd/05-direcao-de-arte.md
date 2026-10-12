# 05 — Direção de arte

## Resumo

**Ragnarok Online em tons pastel, num formato de celular em pé.**

- Personagens chibi no estilo dos sprites do Ragnarok: cabeça grande, proporção fofa, sombreamento suave, contorno fino e colorido.
- **Acessórios de cabeça como identidade**: silhueta forte, reconhecível de longe, mais saturados que o resto do personagem.
- Regiões do Vale como **cenas ilustradas em pixel art** (dioramas verticais), com câmera inclinada em 3/4, como as cidades do Ragnarok.
- Paleta **pastel e de baixo contraste** — calma, nostálgica, que não cansa a vista.
- Tom: **aconchegante, leve, gentil.** O mundo desbotado deve parecer "adormecido", não "morto".

## Referências

| Referência | O que pegar | O que **não** pegar |
|------------|-------------|---------------------|
| **Ragnarok Online — praça de Prontera, pouco movimento** | Sprites chibi, paleta pastel, chão de pedra claro, canteiros de flores, Poring passeando, **densidade de pessoas** (~20 na tela) | Interface antiga, nomes e chat sobre as cabeças |
| **Ragnarok Online — multidão de *headgears*** | Variedade e **legibilidade dos chapéus**: capacete amarelo, sol, globo, capuz de gato — todos reconhecíveis numa multidão | Densidade: aquilo sobrecarrega; nosso público precisa de calma |
| **Ilustração da praça com fonte, luz dourada** | **Luz quente de fim de tarde**, folhas caindo, sombra de árvores no chão — como recompensa quando uma região revive. Estilo para **arte promocional** (loja de apps, tela de abertura) | O nível de detalhe e a saturação dentro do jogo. Era uma imagem de inspiração (parece gerada por IA e imita personagens do Ragnarok): não usar como base de assets |
| **Stardew Valley** | Rotina acolhedora, interface de madeira e papel | Tiles 16 × 16 e personagens pequenos |

> Imagens de jogos de terceiros servem só como referência de clima e estilo. Nenhum asset, personagem ou elemento reconhecível do Ragnarok (Poring, chapéus específicos, roupas de classes) pode ser copiado. Os itens do nosso jogo precisam ser criações originais.

## Orientação de tela

**Retrato (vertical).** Apps de autocuidado são usados com uma mão, rapidamente, muitas vezes deitado.

## Medidas

| Elemento | Tamanho | Observação |
|----------|---------|------------|
| Resolução base | **540 × 960** | Escala inteira 2× → 1080 × 1920 (Full HD vertical) |
| Quadro do corpo | **64 × 80** | Personagem ocupa ~44 × 68; pés por volta de y = 76 |
| Quadro da cabeça | **96 × 112** | Ponto de âncora em (48, 72): sobram 72 px acima do centro da cabeça para chapéus altos, balões, orelhas, chamas |
| Cena de região | **540 × ~1200** | Ilustração vertical com rolagem curta; câmera em 3/4 |
| Ícones de interface | 24 × 24 e 32 × 32 | |
| Retratos de diálogo | 96 × 96 | Expressões do personagem e NPCs |

Sempre **escala inteira** e filtro *nearest neighbor*. Todo o jogo usa **a mesma escala de pixel** — nada de personagem num tamanho de pixel e cenário em outro (*mixels*).

Telas com proporção diferente de 9:16 (ex.: 20:9) mostram mais cena nas bordas, sem esticar pixels.

## Personagem em camadas (*paper doll*)

O personagem é montado empilhando sprites separados. Cada item novo é só uma camada a mais.

**Ordem das camadas (de baixo para cima):**

| # | Camada | Quadro | Pode trocar cor? |
|---|--------|--------|------------------|
| 1 | Sombra no chão | corpo | — |
| 2 | Cabelo (parte de trás) | cabeça | Sim |
| 3 | Corpo base | corpo | Tom de pele |
| 4 | Rosto (olhos, boca) | cabeça | Cor dos olhos |
| 5 | Roupa de baixo (calça, saia) | corpo | Algumas |
| 6 | Calçado | corpo | Algumas |
| 7 | Roupa de cima (camiseta, casaco) | corpo | Algumas |
| 8 | Acessório de corpo (cachecol, mochila) | corpo | — |
| 9 | Cabelo (parte da frente) | cabeça | Sim |
| 10 | Acessório de rosto (óculos) | cabeça | — |
| 11 | Chapéu / acessório de cabeça | cabeça | — |

**Chapéus × cabelo:** cada chapéu tem uma propriedade `esconde_cabelo` com valores `nenhum`, `topo` ou `total`. O jogo usa uma versão recortada do cabelo conforme o valor, evitando que o cabelo atravesse o chapéu.

**Cores por paleta:** cabelos, peles e algumas roupas são desenhados em **rampas de tons de cinza** e coloridos por shader (*palette swap*). Um único desenho de cabelo vira todas as cores sem custo extra de arte. Cada material recolorível usa até **8 tons**, com estes valores exatos de cinza: **28, 56, 84, 112, 140, 168, 196, 224** (do mais escuro ao mais claro).

### Regras de legibilidade dos acessórios de cabeça

1. **Silhueta primeiro.** O chapéu precisa ser reconhecível só pelo contorno, em tamanho real (1×), no meio de outros personagens.
2. **Mais saturado que o corpo.** Corpo e roupas em tons pastel; o chapéu é onde a cor "estoura".
3. **Pode crescer para cima.** O quadro da cabeça tem espaço para itens que flutuam ou sobem bem acima da cabeça.
4. **Itens épicos podem ser animados** (2–4 quadros: brilho, chama, balão balançando). Os comuns são estáticos.

## Animações

| Animação | Direções | Quadros | Uso |
|----------|----------|---------|-----|
| Parado (*idle*) | baixo, cima, lado | 2 | Respiração sutil |
| Andar | baixo, cima, lado | 4 | Movimento na cena |
| Comemorar | baixo | 4 | Ao completar uma quest |
| Sentar / descansar | baixo | 2 | Tela de descanso |

**4 direções, 3 desenhadas:** o lado esquerdo é o direito **espelhado**. O Ragnarok usa 8 direções, mas isso dobraria o custo de cada cosmético.

Total por camada de corpo: **3 × (2 + 4) + 4 + 2 = 24 quadros**.

### Âncora de cabeça

Chapéus, rosto, cabelos e óculos **não precisam ser desenhados quadro a quadro**. Cada quadro do corpo base guarda a posição da cabeça (x, y). Os itens de cabeça são desenhados **uma vez por direção (3 desenhos)** e o jogo os posiciona seguindo a âncora.

| Tipo de item | Desenhos necessários |
|--------------|----------------------|
| Chapéu / acessório de cabeça | **3** |
| Óculos | **3** (ou 2: costas não mostra) |
| Cabelo | **6–8** (3 inteiros + 3 recortados + parte de trás se for longo) |
| Roupa de cima / de baixo | **24** |
| Calçado | **24** (ou menos, se ficar escondido) |

Isso é o que torna os acessórios de cabeça o carro-chefe da loja: são os itens mais desejáveis **e** os mais baratos de produzir.

## Regiões como cenas ilustradas

Cada região do Vale (Casa, Horta, Quarto, Trilha, Praça, Oficina, Biblioteca) é **uma cena vertical pintada em pixel art**, como um diorama, e não um mapa grande de tiles.

- Câmera em **3/4 inclinada**, como as cidades do Ragnarok.
- O personagem anda dentro de uma **área caminhável** definida por um contorno (o resto é cenário).
- Objetos que o personagem pode passar por trás (árvores, casa, poste) ficam em **camadas separadas** para a ordenação por profundidade.
- **Elementos de marco** (flores, fumaça, janelas acesas, passarinhos, NPCs) ficam em camadas separadas, para aparecer quando a região alcança 25 / 50 / 75 / 100% de vida.

Por que cenas e não tiles: o visual fica muito mais próximo das referências, combina com a tela em pé, e 7 cenas costumam custar menos que um tileset completo com todas as transições.

## Mundo desbotado e luz

- Toda a cena é desenhada **colorida, uma vez só**.
- Um shader tira a cor de acordo com a vida da região (0–100), com um leve tom azulado.
- Conforme a região revive, a **iluminação esquenta**: de uma luz fria e difusa para a **luz dourada de fim de tarde** da ilustração de referência, com sombra de folhas no chão e folhas caindo (partículas).
- O personagem do jogador **sempre** está colorido — ele é a fonte de cor que volta ao Vale.

## Paleta

- **Pastel, baixo contraste**, como o Ragnarok: chão de pedra claro, verdes suaves, telhados terracota, céu azul-claro.
- Contorno **fino e colorido** (marrom, vinho, azul-escuro), nunca preto puro.
- Sem bordas com transparência parcial (*anti-aliasing* contra o fundo): pixels opacos ou totalmente transparentes. Sombra no chão é a exceção.
- Interface: madeira clara, papel, tecido — materiais aconchegantes, cantos arredondados em pixel.

## Arte promocional

Para a loja de apps, a tela de abertura e redes sociais, pode-se encomendar **ilustrações** no estilo da imagem de referência da praça com luz dourada (mais detalhadas e cinematográficas que o jogo). Pode ser outro artista.

## Ferramentas sugeridas

- **Aseprite** — padrão da indústria para pixel art e animação (pago, mas barato; o código-fonte é aberto).
- **LibreSprite** ou **Pixelorama** — alternativas gratuitas.
- Exportar de cada camada uma *sprite sheet* com os quadros sempre na mesma ordem, para o motor montar automaticamente.

## Primeiros testes de arte

Ver o trabalho-teste no [briefing para artista](../arte/briefing-artista.md#etapa-1--trabalho-teste-pago).
