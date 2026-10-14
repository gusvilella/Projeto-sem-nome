#!/usr/bin/env python3
"""Extrai acessórios de cabeça de uma grade de personagens gerada por IA.

A grade mostra o MESMO personagem várias vezes, cada vez com um acessório. O
script compara cada figura com o personagem sem acessório (quadro de frente da
folha importada) e guarda só o que mudou: o acessório. O resultado é uma camada
de cabeça (96 x 112, centro da cabeça em (48, 72)) que o jogo encaixa pela âncora.

Por enquanto só a vista de frente; costas e lado ficam vazios até serem gerados.

Uso:
  python3 ferramentas/extrair_chapeus.py grade.png base_64.png pasta_saida \\
      --linhas 2 --colunas 5 --nomes gorro,cogumelo,broto,...
"""

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image

from importar_sprite import QH, QW, _contorno, _limpar_pontos, remover_fundo, separar_em

HW, HH = 96, 112
PONTO_CABECA = (48, 72)
MARGEM_TOPO = 40  # espaço acima do quadro do corpo para acessórios altos


def _camisa(c):
    """Cor coral da camiseta do personagem de referência."""
    r, g, b, a = c
    return a > 0 and r > 190 and r - g > 95 and r - b > 100


def medidas(img):
    """(base dos pés, topo da camiseta, centro x da camiseta) de uma figura."""
    w, h = img.size
    px = img.load()
    pes = max(y for y in range(h) for x in range(w) if px[x, y][3] > 0)
    # só procura a camiseta na parte de baixo (acessórios vermelhos ficam em cima)
    inicio = int(h * 0.4)
    linhas_camisa = [y for y in range(inicio, h) if sum(1 for x in range(w) if _camisa(px[x, y])) >= max(3, w // 10)]
    topo = min(linhas_camisa)
    xs = [x for x in range(w) for y in range(topo, topo + max(3, (pes - topo) // 6)) if _camisa(px[x, y])]
    return pes, topo, (min(xs) + max(xs)) / 2


def separar_grade(img, linhas, colunas):
    w, h = img.size
    a = img.getchannel("A").load()
    ocupacao = [sum(1 for x in range(w) if a[x, y] > 0) for y in range(h)]
    caixa = img.getbbox()
    altura = (caixa[3] - caixa[1]) / linhas
    cortes = [caixa[1]]
    for k in range(1, linhas):
        alvo = caixa[1] + k * altura
        faixa = range(int(alvo - altura * 0.3), int(alvo + altura * 0.3))
        cortes.append(min(faixa, key=lambda y: (ocupacao[y], abs(y - alvo))))
    cortes.append(caixa[3])
    figuras = []
    for y0, y1 in zip(cortes, cortes[1:]):
        figuras.extend(separar_em(img.crop((0, y0, w, y1)), colunas))
    return figuras


def reduzir_alinhado(figura, base_med, escala, cores=32):
    """Reduz a figura na escala dada e alinha pés e camiseta com a base."""
    pes, topo, cx = medidas(figura)
    b_pes, b_topo, b_cx = base_med
    w, h = max(1, round(figura.width * escala)), max(1, round(figura.height * escala))
    pequeno = figura.resize((w, h), Image.BOX)
    alfa = pequeno.getchannel("A").point(lambda v: 255 if v >= 110 else 0)
    rgb = pequeno.convert("RGB").quantize(colors=cores, method=Image.Quantize.MEDIANCUT).convert("RGB")
    pequeno = rgb.convert("RGBA")
    pequeno.putalpha(alfa)
    _limpar_pontos(pequeno)
    _contorno(pequeno)
    tela = Image.new("RGBA", (QW, QH + MARGEM_TOPO), (0, 0, 0, 0))
    dx = round(b_cx - cx * escala)
    dy = round(b_pes - pes * escala) + MARGEM_TOPO
    tela.alpha_composite(pequeno, (dx, dy)) if dx >= 0 and dy >= 0 else tela.paste(pequeno, (dx, dy), pequeno)
    return tela


def diferenca(com, sem, limite_y, tolerancia=70):
    """Pixels de 'com' que não existem ou são bem diferentes em 'sem', acima de limite_y."""
    w, h = com.size
    pc, ps = com.load(), sem.load()
    saida = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    po = saida.load()
    for y in range(min(h, limite_y)):
        for x in range(w):
            c = pc[x, y]
            if c[3] == 0:
                continue
            s = ps[x, y]
            if s[3] == 0 or sum(abs(c[i] - s[i]) for i in range(3)) > tolerancia:
                po[x, y] = c
    _limpar_pontos(saida, minimo=12)
    return saida


def ancora_da_base(base):
    """Centro da cabeça no quadro do corpo: meio entre o topo do cabelo e o topo da camiseta."""
    caixa = base.getbbox()
    _, topo, cx = medidas(base)
    return round(cx), round((caixa[1] + topo) / 2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("grade")
    p.add_argument("base", help="folha importada do personagem sem acessório (1º quadro = frente)")
    p.add_argument("saida")
    p.add_argument("--linhas", type=int, default=1)
    p.add_argument("--colunas", type=int, required=True)
    p.add_argument("--nomes", required=True, help="nomes dos acessórios, separados por vírgula, na ordem da grade")
    p.add_argument("--previa")
    a = p.parse_args()

    base = Image.open(a.base).convert("RGBA").crop((0, 0, QW, QH))
    base_med = medidas(base)
    ax, ay = ancora_da_base(base)
    base_alta = Image.new("RGBA", (QW, QH + MARGEM_TOPO), (0, 0, 0, 0))
    base_alta.alpha_composite(base, (0, MARGEM_TOPO))

    # limiar baixo: o contorno azulado de itens brancos (nuvem) não pode virar fundo
    figuras = separar_grade(remover_fundo(Image.open(a.grade), limiar_sat=22), a.linhas, a.colunas)
    nomes = a.nomes.split(",")
    pasta = Path(a.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    # todas as figuras da grade têm o mesmo tamanho: uma escala só (mediana) é mais estável
    corpos = sorted(m[0] - m[1] for m in map(medidas, figuras))
    escala = (base_med[0] - base_med[1]) / corpos[len(corpos) // 2]
    print(f"escala {escala:.4f}")
    previa = []
    for nome, fig in zip(nomes, figuras):
        com = reduzir_alinhado(fig, base_med, escala)
        chapeu = diferenca(com, base_alta, base_med[1] + MARGEM_TOPO)
        # do quadro "alto" do corpo para o quadro da cabeça
        cabeca = Image.new("RGBA", (HW * 3, HH), (0, 0, 0, 0))
        ox = PONTO_CABECA[0] - ax
        oy = PONTO_CABECA[1] - (ay + MARGEM_TOPO)
        cabeca.alpha_composite(chapeu, (ox, oy)) if oy >= 0 else cabeca.paste(chapeu, (ox, oy), chapeu)
        cabeca.save(pasta / f"{nome}.png")
        previa.append((com, chapeu))
        print(f"  {pasta / (nome + '.png')}")

    print(json.dumps({"ancora_frente": [ax, ay]}))
    if a.previa:
        img = Image.new("RGBA", (QW * len(previa), (QH + MARGEM_TOPO) * 2), (244, 232, 206, 255))
        for i, (com, chapeu) in enumerate(previa):
            img.alpha_composite(com, (i * QW, 0))
            img.alpha_composite(base_alta, (i * QW, QH + MARGEM_TOPO))
            img.alpha_composite(chapeu, (i * QW, QH + MARGEM_TOPO))
        img.resize((img.width * 3, img.height * 3), Image.NEAREST).save(a.previa)


if __name__ == "__main__":
    main()
