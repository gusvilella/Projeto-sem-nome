# Jogo — protótipo da Fase 0

Projeto Godot 4.4 para testar as bases técnicas descritas no [GDD](../docs/gdd/). **Toda a arte é provisória**: é gerada por código para validar formatos e deve ser substituída por arte desenhada à mão.

> **Medidas antigas.** O protótipo usa personagem de 32 × 48 e mapa em tiles 16 × 16. A [direção de arte](../docs/gdd/05-direcao-de-arte.md) mudou depois dele (personagem 64 × 80, regiões como cenas ilustradas, rampas de 8 tons). Ele será ajustado quando chegar a arte do trabalho-teste do [briefing](../docs/arte/briefing-artista.md).

| Vida 0% | Vida 50% | Vida 100% |
|---|---|---|
| ![](../docs/prototipo/vida_000.png) | ![](../docs/prototipo/vida_050.png) | ![](../docs/prototipo/vida_100.png) |

![Vitrine de personagens](../docs/prototipo/vitrine.png)

## O que o protótipo tem

- **Personagem em camadas** (9 camadas) com animação parado/andar nas 3 direções; o lado esquerdo é o direito espelhado.
- **Âncora de cabeça:** cabelos, rosto e chapéus têm só 3 desenhos e acompanham o balanço do corpo.
- **Troca de paleta:** pele, cabelo e roupas são desenhados em cinza e coloridos por shader. 6 tons de pele, 10 cores de cabelo, 8 cores de roupa.
- **Chapéus que escondem o cabelo:** `esconde_cabelo = "topo"` usa o cabelo recortado; `"total"` esconde o cabelo inteiro.
- **Região Casa do Vale** em tiles 16 × 16, com ordenação por Y (o personagem passa atrás da casa e das árvores).
- **Toque para andar** com caminho em grade (A*), desviando de cerca, lago, árvores e casa.
- **Mundo desbotado** por shader, com 4 marcos de vida: flores (25%), fumaça na chaminé (50%), janelas acesas (75%), borboletas (100%).
- **Painel de testes:** controle deslizante de vida da região e um provador para trocar aparência.

> O controle deslizante deixa a vida **descer** só para testes. No jogo, a vida de uma região nunca diminui (pilar "nunca punir").

## Como abrir

1. Instale o [Godot 4.4](https://godotengine.org/download) (versão padrão, não a .NET).
2. No gerenciador de projetos: **Importar** → selecione `jogo/project.godot`.
3. Aperte **F5** para rodar. No computador, o clique faz o papel do toque.

## Rodar no celular Android

1. No Godot: **Editor → Gerenciar modelos de exportação** → baixar.
2. Instale o Android SDK e configure em **Editor → Configurações do editor → Exportar → Android** ([guia oficial](https://docs.godotengine.org/pt-br/4.x/tutorials/export/exporting_for_android.html)).
3. **Projeto → Exportar → Adicionar → Android**. Em *Recursos*, inclua `*.json` em "Filtros para exportar arquivos que não são recursos".
4. Com o celular ligado por USB e a depuração USB ativada, use o botão de **implantação com um clique** (ícone do Android no canto superior direito).

## Estrutura

```
jogo/
├── arte/            # PNGs (gerados por ferramentas/gerar_arte.py)
├── cenas/
│   ├── personagem/  # Personagem em camadas
│   ├── vale/        # Região, tiles, caminhos, marcos
│   ├── ui/          # Painel de testes do protótipo
│   └── principal.*  # Cena principal
├── data/            # Todo o conteúdo em JSON (paletas, itens, mapas, regiões)
├── shaders/         # troca_paleta e dessaturacao
├── sistemas/        # Autoload "Dados"
└── testes/          # Testes automáticos e capturas de tela
```

Conteúdo fica em `data/`, não no código: dá para mudar paletas, preços, marcos e o mapa sem programar. O mapa (`data/mapas/casa.json`) é desenhado com caracteres; a legenda está no próprio arquivo.

## Testes

```bash
# Testes automáticos (sem janela)
godot --headless --path jogo res://testes/teste_prototipo.tscn

# Capturas de tela em docs/prototipo/ (precisa de tela; em servidor use xvfb-run)
godot --path jogo res://testes/captura.tscn
```

## Arte provisória

```bash
pip install pillow
python3 ferramentas/gerar_arte.py
```

O script documenta os formatos que a arte definitiva precisa seguir (tamanho dos quadros, ordem das colunas e linhas, tons de cinza para troca de paleta). Ao trocar pela arte desenhada à mão, mantenha esses formatos e o jogo continua funcionando sem mudar código.

## Limitações conhecidas

- Fonte padrão do Godot (não é pixel art) — escolher uma fonte pixel legível com acentos.
- Lago e caminho sem bordas de transição (falta *autotile*).
- Arte gerada por código: proporções e tons servem de referência, não de resultado final.
- Ainda não foi testado num celular de verdade.
