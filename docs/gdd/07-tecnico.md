# 07 — Técnico

## Motor: Godot 4

**Por quê:**

- Gratuito e de código aberto, **sem royalties** nem taxa por instalação.
- Excelente para 2D e pixel art (escala inteira, *snap* de pixels, luzes 2D, partículas, shaders 2D simples).
- Exporta para Android e iOS.
- GDScript é fácil de aprender; projeto leve, abre em computador modesto.

**Alternativas consideradas:** Unity (mais pesado, histórico de mudanças de licença), Flutter + Flame (bom para app, mais trabalhoso para jogo), Defold (ótimo para mobile, comunidade menor).

## Plataformas

1. **Android primeiro.** Maioria do mercado brasileiro; publicação mais barata (taxa única da Google Play) e mais rápida.
2. **iOS depois.** Exige um Mac para compilar e conta de desenvolvedor Apple (anual).

## Configuração do projeto

- Resolução base **540 × 960**, retrato (ver [05](05-direcao-de-arte.md#medidas)).
- `display/window/stretch/mode = viewport`, `stretch/scale_mode = integer`.
- Filtro de textura padrão: **Nearest**.
- Câmera com *pixel snap* para evitar tremidas.

## Arquitetura (proposta)

```
res://
├── data/
│   ├── quests/          # Banco de quests (JSON ou Resources .tres)
│   ├── jornadas/
│   ├── itens/           # Catálogo de cosméticos
│   └── regioes/
├── sistemas/            # Autoloads (singletons)
│   ├── Jogador.gd       # Faíscas, itens, dias acesos
│   ├── Quests.gd        # Sorteio, conclusão, teto suave
│   ├── Mundo.gd         # Nível de vida das regiões
│   ├── Diario.gd        # Check-ins e humor × atividade
│   ├── Salvamento.gd    # Salvar/carregar local
│   └── Loja.gd          # Compras com Faíscas e dinheiro real
├── cenas/
│   ├── vale/            # Mapa e regiões
│   ├── personagem/      # Paper doll em camadas
│   └── ui/              # Check-in, quests, loja, diário, ajuda
├── shaders/
│   ├── dessaturacao.gdshader
│   └── troca_paleta.gdshader
└── arte/
```

**Princípio:** todo conteúdo (quests, itens, jornadas, textos) em **arquivos de dados**, não em código. Assim dá para revisar e adicionar conteúdo sem programar — inclusive quando um psicólogo for revisar as quests.

## Data e hora

- O "dia" do jogo vira às **4h da manhã** no horário local (quem dorme tarde não "perde" o dia à meia-noite).
- Mudar o relógio do celular para ganhar mais Faíscas é possível e **não deve ser combatido** agressivamente — não há competição nem dano a outros jogadores. No máximo, ignorar dias "no futuro".

## Salvamento

- Arquivo local (`user://`), em JSON versionado (`"versao": 1`) para facilitar migrações.
- Salvar a cada ação relevante (quest concluída, compra, check-in).
- Cópia de segurança automática do último save válido, para não perder progresso se o arquivo corromper.
- **Compras com dinheiro real** são restauradas pela própria Google Play (*restore purchases*), não dependem só do save local.

## Compras no app

- **Google Play Billing** via plugin oficial do Godot para Android.
- Cada item da loja = um produto **não consumível** na Google Play.
- Pacote apoiador = 3 produtos não consumíveis (ou consumíveis, se quiser permitir apoiar mais de uma vez).
- Validar a compra no aparelho no MVP; validação em servidor pode vir depois, se houver fraude relevante.

## Notificações

- Notificações locais agendadas pelo próprio aparelho (sem servidor de push).
- Desligadas por padrão; 1 por dia no máximo (ver [06](06-seguranca-etica-legal.md#notificações)).

## Acessibilidade

- Tamanho de texto ajustável.
- Fonte pixel **legível** com alternativa de fonte comum.
- Modo de alto contraste na interface.
- Opção de reduzir animações e tremidas de tela.
- Todas as ações de um toque, alcançáveis com o polegar na metade de baixo da tela.

## Desempenho

- Meta: rodar liso em celulares Android de entrada (2 GB de RAM).
- APK/AAB pequeno (meta < 80 MB).
- Sem necessidade de internet para jogar.
