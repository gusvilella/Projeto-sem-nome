# 05 — Direção de arte

## Resumo

**Estrutura do Stardew Valley com a alma visual do Ragnarok.**

- Visão top-down, mundo em tiles, 4 direções de movimento (estrutura Stardew).
- Personagens chibi, com cabeça grande e expressiva, e acessórios de cabeça como destaque (alma Ragnarok).
- Pixel art 16-bit ou acima: paleta rica, sombreamento suave, sem limitações de hardware antigo.
- Tom: **aconchegante, quente, gentil.** Nada sombrio ou melancólico demais — o mundo desbotado deve parecer "adormecido", não "morto".

## Orientação de tela

**Retrato (vertical).** Apps de autocuidado são usados com uma mão, rapidamente, muitas vezes deitado. O jogo deve funcionar bem assim.

## Resoluções (a validar no protótipo)

| Elemento | Tamanho | Observação |
|----------|---------|------------|
| Resolução base | **360 × 640** | Escala inteira 3× → 1080 × 1920 (Full HD vertical) |
| Tile | **16 × 16** | ~22 tiles de largura na tela |
| Frame do personagem | **32 × 48** | O corpo ocupa ~24 × 40; o resto é folga para chapéus altos e acessórios |
| Ícones de interface | 16 × 16 e 24 × 24 | |
| Retratos de diálogo | 64 × 64 | Expressões do personagem e NPCs |

Telas com proporção diferente de 9:16 (ex.: 20:9) mostram mais mundo nas bordas, sem esticar pixels. Sempre **escala inteira** e filtro *nearest neighbor* — nunca pixels borrados ou de tamanhos diferentes.

## Personagem em camadas (*paper doll*)

O personagem é montado empilhando sprites separados, todos com o mesmo frame de 32 × 48 e alinhados na mesma posição. Cada item novo é só uma camada a mais.

**Ordem das camadas (de baixo para cima):**

| # | Camada | Pode trocar cor? |
|---|--------|------------------|
| 1 | Sombra no chão | — |
| 2 | Cabelo (parte de trás) | Sim |
| 3 | Corpo base | Tom de pele |
| 4 | Rosto (olhos, boca) | Cor dos olhos |
| 5 | Roupa de baixo (calça, saia) | Algumas |
| 6 | Calçado | Algumas |
| 7 | Roupa de cima (camiseta, casaco) | Algumas |
| 8 | Acessório de corpo (cachecol, mochila) | — |
| 9 | Cabelo (parte da frente) | Sim |
| 10 | Acessório de rosto (óculos) | — |
| 11 | Chapéu / acessório de cabeça | — |

**Chapéus × cabelo:** cada chapéu tem uma propriedade `esconde_cabelo` com valores `nenhum`, `topo` ou `total`. O jogo usa uma versão recortada do cabelo conforme o valor, evitando que o cabelo atravesse o chapéu.

**Cores por paleta:** cabelos, peles e algumas roupas são desenhados em **tons de cinza indexados** e coloridos por shader com uma paleta (*palette swap*). Um único desenho de cabelo vira 10 cores sem custo extra de arte.

## Animações

| Animação | Direções | Frames | Uso |
|----------|----------|--------|-----|
| Parado (*idle*) | baixo, cima, lado | 2 | Respiração sutil |
| Andar | baixo, cima, lado | 4 | Movimento no mapa |
| Comemorar | baixo | 4 | Ao completar uma quest |
| Sentar / descansar | baixo | 2 | Tela de descanso |

O lado esquerdo é o direito **espelhado**. Total por camada de roupa/corpo: **3 × (2 + 4) + 4 + 2 = 24 frames**.

### Âncora de cabeça

Chapéus, acessórios de rosto e cabelos **não precisam ser desenhados frame a frame**. Cada frame do corpo base guarda um ponto de âncora (posição da cabeça). Os itens de cabeça são desenhados **uma vez por direção (3 desenhos)** e o jogo os desloca seguindo a âncora.

| Tipo de item | Desenhos necessários |
|--------------|----------------------|
| Chapéu / acessório de cabeça | **3** |
| Óculos | **3** (ou 2: lado e frente; costas não mostra) |
| Roupa de cima / de baixo | **24** |
| Calçado | **24** (ou menos, se ficar escondido no parado) |

Isso é o que torna os acessórios de cabeça o carro-chefe da loja: são os itens mais desejáveis **e** os mais baratos de produzir.

## Mundo desbotado

- Todo o cenário é desenhado **colorido, uma vez só**.
- Um shader controla a saturação (e um leve tom azulado/acinzentado) por região, de acordo com o nível de vida dela (0–100).
- Nos marcos de cada região, além da cor, entram **elementos novos**: flores, NPCs, fumaça na chaminé, passarinhos, luz nas janelas.
- O personagem do jogador **sempre** está colorido — ele é a fonte de cor que volta ao Vale.

## Paleta

- Paleta base de **~48 cores**, quentes, com verdes e amarelos suaves (luz de fim de tarde).
- Sugestões de paletas abertas para testar no protótipo: *Resurrect 64*, *Endesga 64*, *Sweetie 16* (para interface). Recortar e adaptar.
- Contorno: **escuro colorido** (marrom ou roxo escuro), não preto puro — fica mais suave e mais "Stardew".
- Interface: madeira, papel, tecido — materiais aconchegantes, cantos arredondados em pixel.

## Ferramentas sugeridas

- **Aseprite** — padrão da indústria para pixel art e animação (pago, mas barato; o código-fonte é aberto e pode ser compilado).
- **LibreSprite** ou **Pixelorama** — alternativas gratuitas.
- Exportar de cada camada uma *sprite sheet* com os 24 frames na mesma ordem, para o motor montar automaticamente.

## Primeiros testes de arte

1. Corpo base em 32 × 48 nas 3 direções, parado e andando.
2. 2 cabelos (curto e longo) com troca de cor por paleta.
3. 3 chapéus usando a âncora de cabeça (um baixo, um alto, um que esconde o cabelo todo).
4. Um pedaço de cenário (a Casa e arredores) em 16 × 16, nas versões 0% e 100% de cor.
5. Ver tudo rodando em um celular de verdade, segurando com uma mão.
