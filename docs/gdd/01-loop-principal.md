# 01 — Loop principal

## O dia no jogo (2–5 minutos de tela)

```
 ┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐
 │ 1. Check-in  │ →  │ 2. Quests do dia│ →  │ 3. Vida real     │
 │ humor+energia│    │ 3 sugestões     │    │ (fora do app)    │
 └──────────────┘    └─────────────────┘    └────────┬─────────┘
        ↑                                            ↓
 ┌──────┴───────┐    ┌─────────────────┐    ┌──────────────────┐
 │ 6. Descanso  │ ←  │ 5. Mundo ganha  │ ←  │ 4. Marcar como   │
 │ (sem cobrança│    │ cor + Faíscas   │    │ feita (honra)    │
 └──────────────┘    └─────────────────┘    └──────────────────┘
```

### 1. Check-in

Ao abrir o app, duas perguntas rápidas (podem ser puladas):

- **Humor:** 5 opções com rostinhos em pixel art (de "muito mal" a "muito bem").
- **Energia:** 3 opções — **Brasa** (baixa), **Chama** (média), **Fogueira** (alta).

O check-in **nunca é obrigatório**. Pular leva direto às quests com energia "Chama".

### 2. Quests do dia

O jogo sugere **3 quests** adequadas à energia informada, puxando de regiões diferentes do mapa. A pessoa pode:

- trocar qualquer sugestão (sem limite e sem custo);
- escolher uma quest de outro nível de energia;
- criar uma quest própria (ver [02](02-quests.md#quests-personalizadas)).

Não há obrigação de fazer as três. **Uma quest já fecha o dia** (ver bônus "Fogo do dia" em [03](03-economia.md)).

### 3. Vida real

A pessoa sai do app e faz a coisa. O app não pede foto, não verifica, não usa sensor. **Sistema de honra** — mentir para o jogo não prejudica ninguém, e exigir prova adicionaria atrito e desconfiança.

### 4. Marcar como feita

Um toque. Opcionalmente, uma pergunta: *"Como você se sente agora?"* (melhor / igual / pior). Isso alimenta o diário de humor × atividade, que é a parte "monitorar" da Ativação Comportamental.

### 5. Recompensa

- **Faíscas** (moeda do jogo).
- A **região** ligada à quest ganha um pouco de cor e vida (ver abaixo).
- Animação curta de comemoração do personagem.

### 6. Descanso

Depois de ~5 quests no dia, o jogo sugere descanso de forma gentil (*"Você fez bastante hoje. Descansar também conta."*). As recompensas diminuem a partir daí para não incentivar compulsão (ver [03](03-economia.md#teto-suave)).

## O mundo que ganha cor

O jogo se passa no **Vale** (nome provisório), um vilarejo que perdeu a cor. Ele é dividido em regiões, cada uma ligada a uma área de autocuidado:

| Região | Área de autocuidado | Exemplos de quests |
|--------|---------------------|--------------------|
| **Casa** | Corpo e higiene | banho, escovar dentes, trocar de roupa |
| **Horta** | Alimentação e hidratação | beber água, comer algo, cozinhar |
| **Quarto** | Sono e descanso | horário de dormir, arrumar a cama |
| **Trilha** | Movimento e ar livre | alongar, caminhar, tomar sol |
| **Praça** | Conexão social | mandar mensagem, ligar, encontrar alguém |
| **Oficina** | Ambiente e organização | lavar louça, arrumar uma gaveta |
| **Biblioteca** | Mente, prazer e criatividade | ler, desenhar, ouvir música |

**Como a cor funciona:**

- Cada região tem um **nível de vida** de 0 a 100.
- Quests da região sobem o nível. O nível **nunca desce** (pilar "nunca punir").
- Em marcos (10, 25, 50, 75, 100), a região muda visualmente: flores aparecem, NPCs voltam, uma construção é restaurada, uma música nova toca.
- A dessaturação é feita por shader, então a arte é desenhada **uma vez só**, colorida (ver [05](05-direcao-de-arte.md#mundo-desbotado)).

Isso cria uma metáfora visual de recuperação sem precisar de texto nenhum — e mostra, de forma espacial, quais áreas da vida a pessoa tem cuidado e quais estão esquecidas.

## Voltar depois de sumir

Quando a pessoa volta após dias ou semanas sem abrir o app:

- Mensagem de boas-vindas acolhedora (*"Que bom te ver. O Vale guardou tudo do jeitinho que você deixou."*).
- **Nada foi perdido**: Faíscas, cores, itens — tudo igual.
- Primeira sugestão de quest sempre de energia Brasa.
- Nunca mencionar quantos dias a pessoa ficou fora.

## Progressão de longo prazo

- **Dias acesos:** contador **total** de dias em que a pessoa completou pelo menos 1 quest. Não precisa ser consecutivo; nunca zera.
- **Marcos de dias acesos** (7, 15, 30, 60, 100...) liberam cosméticos gratuitos e capítulos de história.
- **Capítulos de história** curtos, liberados por dias acesos, contando o que aconteceu com o Vale. Bom lugar para psicoeducação leve, contada pelos NPCs.
- **Diário:** tela que mostra humor ao longo do tempo e quais quests foram seguidas de "me sinto melhor". Linguagem de descoberta, nunca de cobrança (*"Parece que caminhar costuma te fazer bem"*).

## Companheiro (a decidir)

Ideia em aberto: um pequeno companheiro (bicho, espírito, lanterna) que acompanha o personagem, comenta as quests e é a "voz" do jogo. Ajuda a dar calor emocional e é mais um alvo de personalização. Ver [08](08-roadmap.md#perguntas-em-aberto).
