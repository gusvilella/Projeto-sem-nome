#!/usr/bin/env python3
"""Importa sprites gerados por IA (ou prints de tela) para o formato do jogo.

Pega uma imagem com um ou mais personagens lado a lado sobre fundo claro e:
1. remove o fundo (preenchimento a partir das bordas, então o branco dos olhos fica);
2. separa cada personagem pelas colunas vazias entre eles;
3. reduz para a escala real de pixel, com o personagem em ~68 px de altura;
4. limpa as cores (quantização) e reforça o contorno;
5. alinha cada um num quadro de 64 x 80 com os pés em y = 76.

Funciona com prints (imagem borrada ou em escala quebrada), mas a imagem
original baixada da ferramenta sempre dá resultado melhor.

Uso:
  python3 ferramentas/importar_sprite.py entrada.png saida.png [--altura 68] [--cores 28] [--previa previa.png]
"""

import argparse
from collections import deque

from PIL import Image

QW, QH = 64, 80
PES_Y = 76


def _e_fundo(c, limiar_luz=200, limiar_sat=40):
    r, g, b = c[:3]
    return min(r, g, b) >= limiar_luz - 30 and max(r, g, b) - min(r, g, b) <= limiar_sat and (r + g + b) / 3 >= limiar_luz


def remover_fundo(img):
    """Torna transparente o fundo claro e pouco saturado ligado às bordas."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    visto = bytearray(w * h)
    fila = deque()
    for x in range(w):
        fila.extend(((x, 0), (x, h - 1)))
    for y in range(h):
        fila.extend(((0, y), (w - 1, y)))
    while fila:
        x, y = fila.popleft()
        i = y * w + x
        if visto[i]:
            continue
        visto[i] = 1
        if not _e_fundo(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not visto[ny * w + nx]:
                fila.append((nx, ny))
    return img


def separar(img, folga=4):
    """Divide pelos trechos de colunas sem nenhum pixel visível."""
    w, h = img.size
    a = img.getchannel("A").load()
    cheias = [any(a[x, y] > 0 for y in range(h)) for x in range(w)]
    grupos, inicio = [], None
    for x, c in enumerate(cheias + [False]):
        if c and inicio is None:
            inicio = x
        elif not c and inicio is not None:
            if x - inicio > 8:
                grupos.append((inicio, x))
            inicio = None
    # junta pedaços muito próximos (ex.: braço solto do corpo)
    unidos = []
    for g in grupos:
        if unidos and g[0] - unidos[-1][1] <= folga:
            unidos[-1] = (unidos[-1][0], g[1])
        else:
            unidos.append(g)
    figuras = []
    for x0, x1 in unidos:
        recorte = img.crop((x0, 0, x1, h))
        caixa = recorte.getbbox()
        if caixa:
            figuras.append(recorte.crop(caixa))
    return figuras


def _contorno(img, cor=(70, 44, 52, 255)):
    """Pixels da borda da silhueta ficam escuros, como na pixel art."""
    w, h = img.size
    px = img.load()
    borda = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if not (0 <= nx < w and 0 <= ny < h) or px[nx, ny][3] == 0:
                    borda.append((x, y))
                    break
    for x, y in borda:
        r, g, b, _ = px[x, y]
        if (r + g + b) / 3 > 90:  # só escurece o que ficou claro demais
            px[x, y] = cor


def reduzir(figura, altura, cores):
    escala = altura / figura.height
    w = max(1, round(figura.width * escala))
    pequeno = figura.resize((w, altura), Image.BOX)
    # transparência dura: ou o pixel existe, ou não existe
    alfa = pequeno.getchannel("A").point(lambda v: 255 if v >= 110 else 0)
    rgb = pequeno.convert("RGB")
    rgb = rgb.quantize(colors=cores, method=Image.Quantize.MEDIANCUT).convert("RGB")
    saida = rgb.convert("RGBA")
    saida.putalpha(alfa)
    _contorno(saida)
    return saida


def no_quadro(sprite):
    quadro = Image.new("RGBA", (QW, QH), (0, 0, 0, 0))
    x = (QW - sprite.width) // 2
    y = PES_Y - sprite.height + 1
    quadro.alpha_composite(sprite, (max(0, x), max(0, y)))
    return quadro


def importar(entrada, altura=68, cores=28):
    img = remover_fundo(Image.open(entrada))
    figuras = separar(img)
    # sombras no chão costumam sair como figura achatada: descarta o que for baixo demais
    maior = max(f.height for f in figuras)
    figuras = [f for f in figuras if f.height > maior * 0.5]
    return [no_quadro(reduzir(f, altura, cores)) for f in figuras]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("entrada")
    p.add_argument("saida")
    p.add_argument("--altura", type=int, default=68, help="altura do personagem em pixels (padrão 68)")
    p.add_argument("--cores", type=int, default=28, help="máximo de cores (padrão 28)")
    p.add_argument("--previa", help="salva também uma prévia ampliada 4x")
    a = p.parse_args()

    quadros = importar(a.entrada, a.altura, a.cores)
    folha = Image.new("RGBA", (QW * len(quadros), QH), (0, 0, 0, 0))
    for i, q in enumerate(quadros):
        folha.alpha_composite(q, (i * QW, 0))
    folha.save(a.saida)
    print(f"{len(quadros)} quadro(s) de {QW}x{QH} salvos em {a.saida}")
    if a.previa:
        fundo = Image.new("RGBA", folha.size, (244, 232, 206, 255))
        fundo.alpha_composite(folha)
        fundo.resize((folha.width * 4, folha.height * 4), Image.NEAREST).save(a.previa)


if __name__ == "__main__":
    main()
