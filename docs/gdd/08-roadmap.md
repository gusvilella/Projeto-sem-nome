# 08 — Roadmap

## Fase 0 — Protótipo de arte e sensação

**Objetivo:** ver se o estilo funciona num celular de verdade.

Protótipo em [`jogo/`](../../jogo/README.md), com arte provisória gerada por código já nas medidas da [direção de arte](05-direcao-de-arte.md).

- [ ] Escolher a paleta base (as atuais são provisórias)
- [x] Corpo base 64 × 80 (3 direções, parado + andar), cabeça 96 × 112 com âncora por quadro
- [x] 2 cabelos com troca de cor por paleta
- [x] 3 chapéus usando a âncora de cabeça
- [x] Região Casa como cena ilustrada em 3/4, com máscara de área caminhável
- [x] Shader de dessaturação funcionando (0% → 100%), com 4 marcos visuais
- [x] Projeto Godot configurado (540 × 960, retrato, escala inteira)
- [x] Personagem andando no mapa por toque
- [ ] Rodar num celular Android de verdade
- [x] Definir a direção de arte com referências (Ragnarok em tons pastel)
- [x] [Briefing para artista](../arte/briefing-artista.md)
- [ ] Pedir orçamentos e contratar o trabalho-teste
- [x] Ajustar o protótipo às novas medidas (64 × 80, cenas ilustradas, rampas de 8 tons)
- [ ] Trocar a arte provisória pela do trabalho-teste
- [ ] Escolher uma fonte pixel legível

## Fase 1 — MVP jogável

**Objetivo:** o loop principal completo, sem dinheiro real.

- [ ] Check-in de humor e energia
- [ ] Sorteio de 3 quests por energia, com troca
- [ ] Banco inicial de ~50 quests (revisado)
- [ ] Marcar quest como feita + "como você se sente agora?"
- [ ] Faíscas, Fogo do dia, semana acesa, teto suave
- [ ] 3 regiões ganhando cor (Casa, Horta, Trilha)
- [ ] Criação de personagem com itens gratuitos
- [ ] Loja com ~10 itens, **só Faíscas**
- [ ] Contador de dias acesos e 2 marcos
- [ ] 1 jornada completa
- [ ] Botão de recursos de ajuda + tela de aviso inicial
- [ ] Salvamento local

## Fase 2 — Playtest fechado

**Objetivo:** validar que o jogo ajuda e não faz mal.

- 10–20 pessoas, idealmente incluindo pessoas com sintomas depressivos (com consentimento e cuidado).
- Duração: 2–4 semanas de uso real.
- Coletar: o que motivou, o que gerou culpa ou frustração, quests favoritas e ignoradas, tempo até a primeira compra com Faíscas, se o épico parece alcançável.
- Entrevista curta no início e no fim. Questionário anônimo.
- Ajustar economia, quests e textos.

## Fase 3 — Pré-lançamento

- [ ] Todas as 7 regiões
- [ ] Catálogo de ~30 itens + pacote apoiador
- [ ] Google Play Billing integrado
- [ ] Diário de humor × atividade
- [ ] Notificações opcionais
- [ ] Opções de acessibilidade
- [ ] Política de privacidade e termos
- [ ] Revisão jurídica (LGPD, proteção de menores)
- [ ] Revisão por psicólogo
- [ ] Página na Google Play (textos, capturas, vídeo curto)

## Fase 4 — Lançamento (Android, Brasil)

- Acesso antecipado (*early access*) ou teste aberto na Google Play primeiro.
- Comunidade: Discord ou grupo para feedback.
- Divulgação: comunidades de pixel art, saúde mental, criadores de conteúdo sobre jogos indie e bem-estar.

## Depois do lançamento

- iOS
- Companheiro personalizável
- Personalização da casa
- Mais jornadas e capítulos de história
- Itens sazonais (São João, Natal...)
- Inglês e espanhol
- Backup opcional na nuvem
- [A Praça](09-praca.md): espaço compartilhado e seguro para ver outros jogadores, com reações positivas e presentes

## Perguntas em aberto

- [ ] **Nome do jogo.** E nomes finais para o Vale, as Faíscas, os níveis de energia.
- [ ] **Companheiro:** existe? Que forma tem (bicho, espírito, lanterna)? É a voz do jogo?
- [x] ~~**Personagem anda livremente pelo mapa?**~~ Cada região é uma cena ilustrada vertical em que o personagem anda (ver [05](05-direcao-de-arte.md#regiões-como-cenas-ilustradas)).
- [ ] **História:** qual é o mistério do Vale? Por que perdeu a cor? (cuidado para não virar metáfora pesada demais)
- [ ] **Quests personalizadas** no MVP ou só depois?
- [x] ~~Quem desenha a arte?~~ Artista freelancer de pixel art (ver [briefing](../arte/briefing-artista.md)).
- [ ] Faixas de preço finais em reais.
