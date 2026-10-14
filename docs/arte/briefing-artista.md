# Briefing para artista — pixel art

> Documento para enviar a artistas e pedir orçamento. Junte a ele as imagens de referência (ver [Referências](#referências)).

## O projeto

Um RPG **gratuito para celular**, sobre saúde mental. O jogador cuida de si na vida real — beber água, abrir a janela, tomar banho, mandar mensagem para alguém — e, a cada pequeno passo, um vilarejo desbotado (o **Vale**) volta a ganhar cor e vida.

O jogo é para pessoas em um momento difícil, então o visual precisa passar **calma, aconchego e leveza**. Nada sombrio, nada agressivo.

A única fonte de receita são **cosméticos** do personagem (chapéus, roupas, cabelos). Por isso o personagem e os acessórios de cabeça são o centro da arte.

## Estilo

**Ragnarok Online em tons pastel**, num jogo para celular em pé.

- Personagens chibi, no espírito dos sprites do Ragnarok: cabeça grande, proporções fofas, sombreamento suave.
- Paleta **pastel, de baixo contraste**. Contorno fino e **colorido** (nunca preto puro).
- **Acessórios de cabeça com silhueta forte**, reconhecíveis de longe e mais saturados que o resto do personagem.
- Cenários como **ilustrações verticais em pixel art**, com câmera em 3/4 (como as cidades do Ragnarok).
- Luz quente de fim de tarde quando o lugar "revive".

Os itens e personagens precisam ser **criações originais**: as referências servem para clima e estilo, nada pode ser copiado de outros jogos.

### Referências

1. **Ragnarok Online — praça de Prontera com pouco movimento.** Estilo dos sprites, paleta, chão de pedra, canteiros de flores, densidade de pessoas.
2. **Ragnarok Online — multidão de jogadores.** Variedade e legibilidade dos chapéus: cada um é reconhecível no meio de todos.
3. **Ilustração de uma praça com fonte e luz dourada.** Só para a luz e o clima.

## Especificações técnicas

| Item | Especificação |
|------|---------------|
| Resolução base do jogo | 540 × 960 (exibida em 2×) |
| Quadro do corpo | **64 × 80 px**, personagem ocupando ~44 × 68, pés em y ≈ 76 |
| Quadro da cabeça | **96 × 112 px**, centro da cabeça no ponto (48, 72) |
| Direções | **3 desenhadas**: frente, costas, lado direito (o esquerdo é espelhado) |
| Bordas | Pixels opacos ou totalmente transparentes (sem *anti-aliasing* contra o fundo), exceto a sombra |
| Escala | Tudo na mesma escala de pixel; nada redimensionado ou rotacionado |
| Entrega | PNG por camada + arquivos-fonte (.aseprite ou equivalente) |

### Personagem em camadas

O personagem é montado em camadas sobrepostas, como uma boneca de papel: corpo, rosto, roupa de baixo, calçado, roupa de cima, cabelo (frente e trás), óculos, chapéu. Cada camada é uma folha de sprites separada, sempre com os quadros na mesma posição.

**Camadas de corpo** (corpo, roupas, calçado): folha de **6 colunas × 3 linhas** de quadros 64 × 80.

| | Col. 1–2 | Col. 3–6 |
|---|---|---|
| **Linha 1** | Frente, parado | Frente, andando |
| **Linha 2** | Costas, parado | Costas, andando |
| **Linha 3** | Lado direito, parado | Lado direito, andando |

Mais duas animações só de frente: **comemorar** (4 quadros) e **sentar** (2 quadros).

**Camadas de cabeça** (rosto, cabelo, óculos, chapéu): **um desenho por direção** (frente, costas, lado), em quadros de 96 × 112. O jogo posiciona esses desenhos seguindo a cabeça do corpo em cada quadro, então eles **não precisam ser animados**. Para isso, informe em uma tabela a posição do centro da cabeça em cada quadro do corpo.

**Cabelos:** além do desenho normal, uma versão **recortada** (sem o topo da cabeça), usada quando o personagem está de chapéu. Cabelos longos têm também uma parte de trás, que fica atrás do corpo.

### Cores trocáveis

Pele, cabelos e algumas roupas mudam de cor no jogo. Para isso, esses desenhos são entregues em **tons de cinza**, com no máximo **8 tons por material**, usando **exatamente** estes valores (R = G = B):

`28 · 56 · 84 · 112 · 140 · 168 · 196 · 224` (do mais escuro ao mais claro)

O jogo troca cada tom de cinza pela cor correspondente da paleta escolhida. Por favor, envie também uma prévia colorida de cada item, para mostrar como deve ficar.

Itens com cores fixas (a maioria dos chapéus, por exemplo) são entregues já coloridos.

### Cenas das regiões

- Ilustração vertical de **540 × ~1200 px**, em pixel art, câmera em 3/4.
- Separada em camadas: **fundo**, **objetos que o personagem pode contornar** (árvores, casa, postes — cada um separado, para o personagem passar por trás) e **elementos de marco** (veja abaixo).
- Um contorno simples indicando a área onde o personagem pode andar.
- A cena é entregue **totalmente colorida e viva**. O efeito de "desbotado" é feito pelo jogo.
- **Elementos de marco:** detalhes que aparecem conforme a região revive, como flores, fumaça na chaminé, janelas acesas, passarinhos ou um NPC. Cerca de 4 por cena, cada um em camada separada. Animações simples, de 2 a 4 quadros, quando fizer sentido.

## Lista de entregas — primeira versão jogável

### Etapa 1 — trabalho-teste (pago)

Para avaliar estilo e formato antes do resto:

| Entrega | Quadros |
|---------|---------|
| Corpo base: frente, costas e lado, parado e andando | 18 |
| 1 camiseta (em tons de cinza) | 18 |
| 1 cabelo: 3 direções + 3 recortados (em tons de cinza) | 6 |
| 1 chapéu (colorido) | 3 |
| Rosto (3 direções) | 3 |
| Proposta de paleta: 3 tons de pele, 3 cores de cabelo, 3 cores de roupa | — |

### Etapa 2 — personagem completo

| Entrega | Quantidade | Quadros (aprox.) |
|---------|------------|------------------|
| Corpo base: completar comemorar e sentar | 1 | 6 |
| Rosto: piscar e 2 expressões (feliz, cansado) | 1 | ~6 |
| Cabelos (3 curtos, 3 longos) | 6 | ~45 |
| Roupas de cima (ex.: camiseta, moletom, casaco, vestido) | 4 | 96 |
| Roupas de baixo (ex.: calça, short, saia) | 3 | 72 |
| Calçados | 2 | 48 |
| Chapéus e acessórios de cabeça | 10 | 30 |
| Óculos | 2 | 6 |
| **Total** | | **~310 quadros** |

Sugestão de 10 acessórios de cabeça, para dar o tom (a lista é aberta a ideias): gorro de pompom, boné, chapéu de cogumelo, coroa de flores, chapéu de palha, capuz de bichinho, fones de ouvido, laço grande, broto de planta na cabeça, nuvenzinha flutuante (este animado).

### Etapa 3 — cenas e interface

| Entrega | Quantidade |
|---------|------------|
| Cenas de região: Casa, Horta, Trilha | 3 |
| Elementos de marco (cerca de 4 por cena) | ~12 |
| Interface: moldura de painel e botões em formato que estica (*9-slice*) | 1 conjunto |
| Ícones (energia, humor, moeda, regiões, menu) | ~25 |
| Ícone do app | 1 |

### Opcional

- Arte de capa para a loja de apps e tela de abertura, **em pixel art, no mesmo estilo e escala do jogo**, usando os sprites e cenários reais.

## Direitos e créditos

> Pontos para combinar no contrato. Não é orientação jurídica: revise com um advogado antes de assinar.

- O jogo é comercial (gratuito com venda de cosméticos). Precisamos de **cessão dos direitos** ou de **licença exclusiva e permanente** para uso comercial, incluindo venda dos itens, atualizações, divulgação e versões futuras do jogo.
- Entrega dos **arquivos-fonte**.
- **Crédito** no jogo e na página da loja de apps.
- O artista pode mostrar o trabalho no portfólio (combinar quando, se for antes do lançamento).
- Pagamento **por etapa**, após aprovação de cada uma.

## O que pedimos no orçamento

1. **Portfólio** com sprites animados, de preferência personagens em camadas ou com troca de roupa.
2. **Preço e prazo para a Etapa 1** (trabalho-teste).
3. Estimativa de **preço e prazo para as Etapas 2 e 3**.
4. Preço por **item extra** depois do lançamento (chapéu, roupa, cabelo), já que a loja vai receber itens novos com frequência.
5. Se tem disponibilidade para uma parceria de longo prazo.
