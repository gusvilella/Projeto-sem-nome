#!/usr/bin/env python3
"""Gera a arte provisória (placeholder) da Fase 0.

Tudo aqui é desenhado por código para testar o pipeline: tamanhos, camadas,
âncora de cabeça, troca de paleta e mundo desbotado. A arte definitiva deve
ser desenhada à mão (Aseprite, Pixelorama...) respeitando os mesmos formatos.

Formatos (ver docs/gdd/05-direcao-de-arte.md):
- Camadas de corpo (corpo, roupas, calçado): folha 6 x 3 de quadros 32 x 48.
  Colunas: 0-1 parado, 2-5 andar. Linhas: baixo, cima, lado (virado p/ direita).
- Camadas de cabeça (rosto, cabelo, chapéu): folha 3 x 1 (uma por direção),
  desenhadas sem deslocamento; o jogo aplica a âncora de cabeça.
- Cabelo da frente: folha 3 x 2. Linha 1 = versão recortada para chapéus
  com esconde_cabelo = "topo".
- Camadas recoloríveis usam 4 tons de cinza (51, 102, 153, 204) que o shader
  troca_paleta.gdshader substitui por contorno, sombra, base e luz.

Uso: python3 ferramentas/gerar_arte.py
"""

import random
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ARTE = RAIZ / "jogo" / "arte"

QW, QH = 32, 48  # quadro do personagem
DIRECOES = ("baixo", "cima", "lado")
COLUNAS = 6
# Deslocamento vertical de cabeça e tronco por coluna. Precisa bater com
# jogo/data/personagem/ancoras.json.
DESLOC = [0, 1, 0, -1, 0, -1]

T, O, S, B, L = 0, 1, 2, 3, 4  # transparente, contorno, sombra, base, luz
CINZA = {O: 51, S: 102, B: 153, L: 204}


# --------------------------------------------------------------------------
# Grade de pixels e primitivas
# --------------------------------------------------------------------------

class Grade:
    def __init__(self, w=QW, h=QH):
        self.w, self.h = w, h
        self.p = [[T] * w for _ in range(h)]

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.p[y][x]
        return T

    def set(self, x, y, v):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = v


def tom(nx, ny):
    """Tom pela posição normalizada no volume (luz vinda de cima-esquerda)."""
    d = nx * 0.6 + ny * 0.8
    if d > 0.45:
        return S
    if d < -0.55:
        return L
    return B


def elipse(g, cx, cy, rx, ry, recorte=None, valor=None):
    for y in range(g.h):
        for x in range(g.w):
            nx = (x + 0.5 - cx) / rx
            ny = (y + 0.5 - cy) / ry
            if nx * nx + ny * ny <= 1 and (recorte is None or recorte(x, y)):
                g.set(x, y, valor if valor is not None else tom(nx, ny))


def retangulo(g, x0, y0, x1, y1, valor=None, arredondado=False):
    """Retângulo com coordenadas inclusivas."""
    cx, cy = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
    rx, ry = (x1 - x0 + 1) / 2, (y1 - y0 + 1) / 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if arredondado and x in (x0, x1) and y in (y0, y1):
                continue
            g.set(x, y, valor if valor is not None else tom((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry))


def contorno(g, valor=O):
    novos = []
    for y in range(g.h):
        for x in range(g.w):
            if g.get(x, y) == T and any(
                g.get(x + dx, y + dy) != T for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            ):
                novos.append((x, y))
    for x, y in novos:
        g.set(x, y, valor)


def colar(dest, src, dx=0, dy=0):
    for y in range(src.h):
        for x in range(src.w):
            v = src.get(x, y)
            if v != T:
                dest.set(x + dx, y + dy, v)


def peca(desenho, w=QW, h=QH, contornar=True):
    """Desenha uma peça isolada e contorna; colar peças em ordem separa as partes."""
    g = Grade(w, h)
    desenho(g)
    if contornar:
        contorno(g)
    return g


def limpar(g, condicao):
    for y in range(g.h):
        for x in range(g.w):
            if condicao(x, y):
                g.set(x, y, T)


# --------------------------------------------------------------------------
# Exportação
# --------------------------------------------------------------------------

def cor_do_pixel(v, paleta):
    if v == T:
        return (0, 0, 0, 0)
    if isinstance(v, tuple):
        return v if len(v) == 4 else (*v, 255)
    if paleta is None:
        c = CINZA[v]
        return (c, c, c, 255)
    c = paleta[v]
    return c if len(c) == 4 else (*c, 255)


def folha(quadros, colunas, linhas, paleta=None, w=QW, h=QH):
    """quadros[linha][coluna] -> Grade. paleta=None exporta em cinza recolorível."""
    img = Image.new("RGBA", (w * colunas, h * linhas), (0, 0, 0, 0))
    px = img.load()
    for li in range(linhas):
        for co in range(colunas):
            g = quadros[li][co]
            for y in range(h):
                for x in range(w):
                    px[co * w + x, li * h + y] = cor_do_pixel(g.get(x, y), paleta)
    return img


def salvar(img, caminho):
    destino = ARTE / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino)
    print(f"  {destino.relative_to(RAIZ)}  {img.width}x{img.height}")


def folha_corpo(desenhar, paleta=None):
    quadros = [[desenhar(d, c) for c in range(COLUNAS)] for d in DIRECOES]
    return folha(quadros, COLUNAS, 3, paleta)


def folha_cabeca(desenhar, paleta=None, recortes=False):
    linhas = [[desenhar(d, False) for d in DIRECOES]]
    if recortes:
        linhas.append([desenhar(d, True) for d in DIRECOES])
    return folha(linhas, 3, len(linhas), paleta)


# --------------------------------------------------------------------------
# Personagem — camadas de corpo (6 x 3)
# --------------------------------------------------------------------------

def pernas_shape(p, direcao, col, y_fim_max=44):
    passo = col in (3, 5)
    if direcao == "lado":
        if passo:
            retangulo(p, 12, 37, 14, min(43, y_fim_max))
            retangulo(p, 18, 37, 20, y_fim_max)
        else:
            retangulo(p, 14, 37, 17, y_fim_max)
    else:
        retangulo(p, 12, 37, 14, y_fim_max - (1 if col == 3 else 0))
        retangulo(p, 17, 37, 19, y_fim_max - (1 if col == 5 else 0))


def braco_lado(col):
    if col == 3:
        return 16, 18  # para frente
    if col == 5:
        return 13, 15  # para trás
    return 14, 16


def corpo(direcao, col):
    d = DESLOC[col]
    g = Grade()
    colar(g, peca(lambda p: pernas_shape(p, direcao, col)))

    def tronco(p):
        if direcao == "lado":
            retangulo(p, 12, 29 + d, 19, 38 + d)
        else:
            retangulo(p, 11, 29 + d, 20, 38 + d)
    colar(g, peca(tronco))

    def bracos(p):
        if direcao == "lado":
            x0, x1 = braco_lado(col)
            retangulo(p, x0, 30 + d, x1, 36 + d, arredondado=True)
        else:
            retangulo(p, 8, 30 + d, 9, 36 + d, arredondado=True)
            retangulo(p, 22, 30 + d, 23, 36 + d, arredondado=True)
    colar(g, peca(bracos))

    colar(g, peca(lambda p: elipse(p, 16, 21.5 + d, 8.4, 7.9)))
    return g


def camiseta(direcao, col, longa=False):
    d = DESLOC[col]
    barra = 39 if longa else 37
    manga = 36 if longa else 32
    g = Grade()

    def tronco(p):
        if direcao == "lado":
            retangulo(p, 11, 29 + d, 20, barra + d)
        else:
            retangulo(p, 10, 29 + d, 21, barra + d)
            retangulo(p, 8, 30 + d, 9, manga + d)
            retangulo(p, 22, 30 + d, 23, manga + d)
            if longa:  # zíper
                for y in range(30 + d, barra + d + 1):
                    p.set(16, y, S if direcao == "baixo" else p.get(16, y))
    colar(g, peca(tronco))

    if direcao == "lado":
        x0, x1 = braco_lado(col)
        colar(g, peca(lambda p: retangulo(p, x0, 30 + d, x1, manga + d)))
    return g


def calca(direcao, col):
    g = Grade()

    def forma(p):
        pernas_shape(p, direcao, col, y_fim_max=42)
        if direcao == "lado":
            retangulo(p, 12, 35, 19, 37)
        else:
            retangulo(p, 11, 35, 20, 37)
    colar(g, peca(forma))
    return g


def calcado(direcao, col):
    g = Grade()

    def forma(p):
        if direcao == "lado":
            if col in (3, 5):
                retangulo(p, 11, 42, 14, 43, arredondado=True)
                retangulo(p, 18, 42, 21, 44, arredondado=True)
            else:
                retangulo(p, 14, 42, 18, 44, arredondado=True)
        else:
            sobe_e = 1 if col == 3 else 0
            sobe_d = 1 if col == 5 else 0
            retangulo(p, 11, 42 - sobe_e, 14, 44 - sobe_e, arredondado=True)
            retangulo(p, 17, 42 - sobe_d, 20, 44 - sobe_d, arredondado=True)
    colar(g, peca(forma))
    return g


# --------------------------------------------------------------------------
# Personagem — camadas de cabeça (3 x 1, sem deslocamento)
# --------------------------------------------------------------------------

OLHO = (52, 34, 54, 255)
BRILHO = (255, 255, 255, 255)
BOCHECHA = (236, 128, 140, 170)
BOCA = (130, 64, 70, 255)


def rosto(direcao, _recorte=False):
    g = Grade()
    if direcao == "baixo":
        for x0 in (11, 19):
            retangulo(g, x0, 21, x0 + 1, 23, valor=OLHO)
            g.set(x0, 21, BRILHO)
        for x in (10, 11, 20, 21):
            g.set(x, 25, BOCHECHA)
        g.set(15, 26, BOCA)
        g.set(16, 26, BOCA)
    elif direcao == "lado":
        retangulo(g, 19, 21, 20, 23, valor=OLHO)
        g.set(20, 21, BRILHO)
        g.set(18, 25, BOCHECHA)
        g.set(19, 25, BOCHECHA)
        g.set(22, 26, BOCA)
    return g


FRANJA = [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0]


def franja(p, x_ini, x_fim):
    for i, x in enumerate(range(x_ini, x_fim + 1)):
        fim = 19 + FRANJA[i % len(FRANJA)]
        for y in range(19, fim + 1):
            p.set(x, y, S if y == fim else B)


def cabelo_frente(estilo):
    def desenhar(direcao, recortado):
        def forma(p):
            if direcao == "baixo":
                elipse(p, 16, 21, 9, 8.6, recorte=lambda x, y: y <= 18)
                franja(p, 9, 22)
                if estilo == "longo":
                    retangulo(p, 6, 17, 9, 32, arredondado=True)
                    retangulo(p, 22, 17, 25, 32, arredondado=True)
                else:
                    retangulo(p, 7, 17, 9, 24, arredondado=True)
                    retangulo(p, 22, 17, 24, 24, arredondado=True)
            elif direcao == "cima":
                elipse(p, 16, 21, 9, 8.6, recorte=lambda x, y: y <= 26)
                if estilo == "longo":
                    retangulo(p, 8, 22, 23, 37, arredondado=True)
            else:  # lado, virado para a direita
                elipse(p, 16, 21, 9, 8.6, recorte=lambda x, y: y <= 18 or (x <= 14 and y <= 25))
                franja(p, 17, 23)
                if estilo == "longo":
                    retangulo(p, 6, 18, 13, 35, arredondado=True)
            if recortado:
                limpar(p, lambda x, y: y <= 19)
        return peca(forma)
    return desenhar


def cabelo_tras_longo(direcao, _recorte=False):
    def forma(p):
        if direcao == "baixo":
            retangulo(p, 6, 20, 25, 35, arredondado=True)
    return peca(forma)


def chapeu_bone(direcao, _recorte=False):
    g = Grade()
    colar(g, peca(lambda p: elipse(p, 16, 19, 9, 6.5, recorte=lambda x, y: y <= 18)))
    if direcao == "baixo":
        colar(g, peca(lambda p: retangulo(p, 7, 19, 24, 20, valor=S, arredondado=True)))
        g.set(16, 13, L)
    elif direcao == "cima":
        colar(g, peca(lambda p: retangulo(p, 9, 19, 22, 19, valor=S)))
    else:
        colar(g, peca(lambda p: retangulo(p, 16, 19, 27, 20, valor=S, arredondado=True)))
    return g


CREME = (238, 220, 186, 255)
CREME_ESCURO = (200, 176, 140, 255)
PINTA = (252, 246, 232, 255)


def chapeu_cogumelo(direcao, _recorte=False):
    g = Grade()

    def chapeu(p):
        elipse(p, 16, 16, 12.5, 10, recorte=lambda x, y: y <= 15)
        pintas = {
            "baixo": [(9, 10), (18, 7), (22, 12), (14, 13)],
            "cima": [(11, 8), (20, 10), (15, 12), (24, 13)],
            "lado": [(8, 12), (14, 8), (21, 11)],
        }[direcao]
        for x, y in pintas:
            retangulo(p, x, y, x + 1, y + 1, valor=PINTA)
    colar(g, peca(chapeu))

    def aba(p):
        retangulo(p, 7, 16, 24, 16, valor=CREME)
        retangulo(p, 8, 17, 23, 17, valor=CREME_ESCURO)
    colar(g, peca(aba))
    return g


POMPOM = (244, 236, 210, 255)


def chapeu_gorro(direcao, _recorte=False):
    g = Grade()

    def gorro(p):
        elipse(p, 16, 20, 9.2, 8.5, recorte=lambda x, y: y <= 19)
        for y in range(17, 20):
            for x in range(7, 25):
                if p.get(x, y) != T:
                    p.set(x, y, L if (x + y) % 2 == 0 else B)
    colar(g, peca(gorro))
    colar(g, peca(lambda p: elipse(p, 16, 10.5, 3, 2.6, valor=POMPOM)))
    return g


# --------------------------------------------------------------------------
# Paletas fixas (itens que não trocam de cor)
# --------------------------------------------------------------------------

def pal(contorno_, sombra, base, luz):
    return {O: contorno_, S: sombra, B: base, L: luz}


PAL_SAPATO = pal((52, 32, 28), (92, 58, 42), (128, 84, 58), (164, 114, 82))
PAL_BONE = pal((32, 42, 84), (52, 84, 152), (72, 122, 200), (122, 170, 234))
PAL_COGUMELO = pal((92, 26, 36), (170, 46, 56), (214, 72, 70), (244, 132, 120))
PAL_GORRO = pal((42, 72, 48), (72, 122, 72), (102, 160, 90), (152, 200, 130))

# Paletas de exemplo só para o ícone (as do jogo ficam em data/personagem/paletas.json)
PAL_PELE_ICONE = pal((110, 62, 52), (214, 146, 112), (240, 184, 146), (252, 214, 180))
PAL_CABELO_ICONE = pal((52, 30, 26), (96, 56, 40), (136, 84, 56), (176, 120, 80))
PAL_ROUPA_ICONE = pal((70, 40, 56), (180, 92, 100), (226, 128, 124), (246, 176, 156))
PAL_CALCA_ICONE = pal((34, 40, 66), (62, 76, 120), (86, 104, 156), (122, 140, 190))


# --------------------------------------------------------------------------
# Cenário — tiles 16 x 16 e decoração
# --------------------------------------------------------------------------

GRAMA = pal((78, 130, 58), (98, 152, 64), (124, 178, 74), (160, 202, 94))
TERRA = pal((140, 110, 82), (172, 134, 94), (198, 160, 112), (222, 190, 142))
AGUA = pal((52, 100, 170), (66, 122, 192), (88, 150, 214), (156, 204, 240))
MADEIRA = pal((82, 52, 36), (122, 78, 52), (170, 112, 72), (206, 152, 102))
PEDRA = pal((112, 106, 102), (142, 136, 128), (178, 170, 160), (206, 200, 190))


def tile_base(rng, paleta, escuros=16, claros=10):
    g = Grade(16, 16)
    for y in range(16):
        for x in range(16):
            g.set(x, y, paleta[B])
    for _ in range(escuros):
        g.set(rng.randrange(16), rng.randrange(16), paleta[S])
    for _ in range(claros):
        g.set(rng.randrange(16), rng.randrange(16), paleta[L])
    return g


def tufo(g, x, y):
    for dx, dy, c in ((0, 0, GRAMA[O]), (1, -1, GRAMA[S]), (2, 0, GRAMA[O]), (1, 0, GRAMA[S]), (1, -2, GRAMA[L])):
        g.set(x + dx, y + dy, c)


def florzinha(g, x, y, petala):
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        g.set(x + dx, y + dy, petala)
    g.set(x, y, (250, 214, 92))


def gerar_tiles():
    rng = random.Random(7)
    tiles = []

    tiles.append(tile_base(rng, GRAMA))  # 0 grama

    g = tile_base(rng, GRAMA)  # 1 grama com tufos
    tufo(g, 3, 6)
    tufo(g, 10, 12)
    tiles.append(g)

    g = tile_base(rng, GRAMA)  # 2 grama com flores
    florzinha(g, 4, 4, (240, 134, 166))
    florzinha(g, 11, 7, (248, 244, 232))
    florzinha(g, 6, 12, (250, 206, 96))
    tiles.append(g)

    g = tile_base(rng, TERRA, escuros=14, claros=12)  # 3 caminho
    for x, y in ((3, 4), (11, 9), (6, 13)):
        g.set(x, y, TERRA[O])
        g.set(x + 1, y, TERRA[S])
    tiles.append(g)

    g = tile_base(rng, AGUA, escuros=10, claros=0)  # 4 água
    for x, y in ((2, 3), (9, 7), (4, 12)):
        for dx in range(4):
            g.set(x + dx, y, AGUA[L])
    tiles.append(g)

    g = tile_base(rng, GRAMA)  # 5 cerca
    cerca = Grade(16, 16)
    retangulo(cerca, 0, 5, 15, 6)
    retangulo(cerca, 0, 10, 15, 11)
    retangulo(cerca, 2, 3, 4, 14, arredondado=True)
    retangulo(cerca, 11, 3, 13, 14, arredondado=True)
    contorno(cerca)
    for y in range(16):
        for x in range(16):
            v = cerca.get(x, y)
            if v != T:
                g.set(x, y, MADEIRA[v])
    tiles.append(g)

    g = tile_base(rng, GRAMA)  # 7 cerca vertical
    cerca = Grade(16, 16)
    retangulo(cerca, 7, 0, 8, 15)
    retangulo(cerca, 5, 2, 10, 5, arredondado=True)
    retangulo(cerca, 5, 10, 10, 13, arredondado=True)
    contorno(cerca)
    tile_cerca_vertical = g
    for y in range(16):
        for x in range(16):
            v = cerca.get(x, y)
            if v != T:
                g.set(x, y, MADEIRA[v])

    g = tile_base(rng, PEDRA, escuros=6, claros=6)  # 6 piso de pedra
    for i in range(16):
        g.set(i, 7, PEDRA[S])
        g.set(7, i if i < 7 else 0, PEDRA[S])
        g.set(12, i if i > 7 else 8, PEDRA[S])
    tiles.append(g)
    tiles.append(tile_cerca_vertical)

    img = Image.new("RGBA", (16 * len(tiles), 16))
    for i, t in enumerate(tiles):
        img.paste(folha([[t]], 1, 1, w=16, h=16), (i * 16, 0))
    return img


COPA = pal((40, 82, 52), (62, 122, 62), (88, 158, 74), (138, 196, 96))
TRONCO = pal((70, 46, 36), (104, 70, 50), (140, 96, 66), (170, 126, 86))


def gerar_arvore():
    g = Grade(32, 48)
    tronco = peca(lambda p: (retangulo(p, 13, 30, 18, 44), retangulo(p, 12, 43, 19, 44)), 32, 48)
    colar(g, tronco)

    def copa(p):
        elipse(p, 16, 18, 14, 13)
        elipse(p, 8, 25, 7, 6)
        elipse(p, 24, 25, 7, 6)
    copa_g = peca(copa, 32, 48)
    rng = random.Random(3)
    for _ in range(14):
        x, y = rng.randrange(6, 22), rng.randrange(8, 20)
        if copa_g.get(x, y) == B:
            copa_g.set(x, y, L)
            copa_g.set(x + 1, y, L)
    colar(g, copa_g)

    img_tronco = folha([[tronco]], 1, 1, TRONCO, 32, 48)
    img_copa = folha([[copa_g]], 1, 1, COPA, 32, 48)
    img_tronco.alpha_composite(img_copa)
    return img_tronco


TELHADO = pal((92, 36, 36), (150, 60, 56), (190, 86, 70), (226, 126, 100))
PAREDE = pal((96, 64, 48), (196, 156, 110), (226, 192, 142), (244, 220, 176))
TIJOLO = pal((80, 40, 36), (128, 72, 64), (156, 92, 80), (186, 120, 102))
VIDRO = (70, 88, 122, 255)
REFLEXO = (150, 180, 212, 255)
MOLDURA = (246, 236, 214, 255)
PORTA = pal((64, 38, 28), (100, 62, 42), (124, 78, 52), (150, 100, 68))

JANELAS = ((12, 42, 25, 55), (54, 42, 67, 55))


def gerar_casa():
    w, h = 80, 72
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def camada(desenho, paleta):
        img.alpha_composite(folha([[peca(desenho, w, h)]], 1, 1, paleta, w, h))

    def chamine(p):
        retangulo(p, 57, 1, 64, 18)
        for y in range(3, 18, 3):
            for x in range(57 + (y // 3 % 2) * 2, 65, 4):
                p.set(x, y, S)
    camada(chamine, TIJOLO)

    def parede(p):
        retangulo(p, 6, 32, 73, 69)
        for y in range(36, 70, 5):
            for x in range(6, 74):
                p.set(x, y, S)
    camada(parede, PAREDE)

    def telhado(p):
        for y in range(8, 35):
            t = (y - 8) / 26
            x0 = round(14 - 13 * t)
            x1 = round(65 + 13 * t)
            for x in range(x0, x1 + 1):
                linha = (y - 8) % 5 == 4
                desloc = ((y - 8) // 5) % 2 * 3
                junta = (x + desloc) % 6 == 0
                if linha or junta:
                    p.set(x, y, S)
                else:
                    p.set(x, y, L if y < 12 else B)
    camada(telhado, TELHADO)

    def porta(p):
        retangulo(p, 33, 46, 46, 69)
        for x in (37, 42):
            for y in range(48, 69):
                p.set(x, y, S)
        p.set(44, 58, (232, 200, 92, 255))
        p.set(44, 59, (190, 150, 60, 255))
    camada(porta, PORTA)

    def janelas(p):
        for x0, y0, x1, y1 in JANELAS:
            retangulo(p, x0, y0, x1, y1, valor=MOLDURA)
            retangulo(p, x0 + 1, y0 + 1, x1 - 1, y1 - 1, valor=VIDRO)
            for i in range(4):
                p.set(x0 + 2 + i, y0 + 5 - i, REFLEXO)
            for y in range(y0, y1 + 1):
                p.set((x0 + x1) // 2, y, MOLDURA)
            for x in range(x0, x1 + 1):
                p.set(x, (y0 + y1) // 2, MOLDURA)
    camada(janelas, PAREDE)

    def degrau(p):
        retangulo(p, 30, 69, 49, 71, arredondado=True)
    camada(degrau, PEDRA)
    return img


def gerar_casa_luz():
    img = Image.new("RGBA", (80, 72), (0, 0, 0, 0))
    px = img.load()
    for x0, y0, x1, y1 in JANELAS:
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                if x != (x0 + x1) // 2 and y != (y0 + y1) // 2:
                    px[x, y] = (255, 214, 120, 200)
    return img


def gerar_fumaca():
    g = Grade(16, 16)
    elipse(g, 8, 9, 5.5, 4.5, valor=(236, 236, 240, 210))
    elipse(g, 5.5, 7, 3, 2.6, valor=(248, 248, 250, 220))
    contorno(g, valor=(196, 196, 206, 160))
    return folha([[g]], 1, 1, None, 16, 16)


def gerar_borboleta():
    asa, asa_luz, corpo_ = (246, 160, 70, 255), (252, 214, 120, 255), (60, 40, 50, 255)
    quadros = []
    for aberta in (True, False):
        g = Grade(8, 8)
        for y in range(2, 7):
            g.set(4, y, corpo_)
        if aberta:
            retangulo(g, 0, 1, 3, 4, valor=asa, arredondado=True)
            retangulo(g, 5, 1, 7, 4, valor=asa, arredondado=True)
            retangulo(g, 1, 5, 3, 6, valor=asa_luz, arredondado=True)
            retangulo(g, 5, 5, 6, 6, valor=asa_luz, arredondado=True)
        else:
            retangulo(g, 2, 1, 3, 5, valor=asa)
            retangulo(g, 5, 1, 6, 5, valor=asa)
        quadros.append(g)
    return folha([quadros], 2, 1, None, 8, 8)


def gerar_flores_altas():
    g = Grade(16, 16)
    caule = (70, 132, 62, 255)
    for x, topo, cor in ((3, 6, (240, 128, 164, 255)), (8, 3, (250, 244, 228, 255)), (12, 7, (250, 200, 90, 255))):
        for y in range(topo + 2, 15):
            g.set(x, y, caule)
        retangulo(g, x - 1, topo, x + 1, topo + 2, valor=cor, arredondado=True)
        g.set(x, topo + 1, (250, 214, 92, 255))
    g.set(5, 12, (96, 160, 74, 255))
    g.set(10, 11, (96, 160, 74, 255))
    contorno(g, valor=(54, 92, 50, 255))
    return folha([[g]], 1, 1, None, 16, 16)


# --------------------------------------------------------------------------
# Ícone (composição do personagem)
# --------------------------------------------------------------------------

def gerar_icone():
    img = Image.new("RGBA", (QW, QH), (0, 0, 0, 0))
    for desenhar, paleta in (
        (corpo, PAL_PELE_ICONE),
        (calca, PAL_CALCA_ICONE),
        (calcado, PAL_SAPATO),
        (camiseta, PAL_ROUPA_ICONE),
    ):
        img.alpha_composite(folha([[desenhar("baixo", 0)]], 1, 1, paleta))
    for desenhar, paleta in (
        (rosto, None),
        (lambda d, r: cabelo_frente("curto")(d, True), PAL_CABELO_ICONE),
        (chapeu_cogumelo, PAL_COGUMELO),
    ):
        img.alpha_composite(folha([[desenhar("baixo", False)]], 1, 1, paleta))
    quadrado = Image.new("RGBA", (40, 40), (252, 236, 200, 255))
    quadrado.alpha_composite(img.crop((0, 2, 32, 42)).resize((32, 40)), (4, 0))
    return quadrado.resize((160, 160), Image.NEAREST)


# --------------------------------------------------------------------------

def main():
    print("Personagem — corpo (6 x 3):")
    salvar(folha_corpo(corpo), "personagem/corpo/base.png")
    salvar(folha_corpo(camiseta), "personagem/roupa_cima/camiseta.png")
    salvar(folha_corpo(lambda d, c: camiseta(d, c, longa=True)), "personagem/roupa_cima/casaco.png")
    salvar(folha_corpo(calca), "personagem/roupa_baixo/calca.png")
    salvar(folha_corpo(calcado, PAL_SAPATO), "personagem/calcado/botinha.png")

    sombra = Grade()
    elipse(sombra, 16, 45, 7.5, 2.2, valor=(40, 30, 44, 90))
    salvar(folha([[sombra]], 1, 1), "personagem/corpo/sombra.png")

    print("Personagem — cabeça (3 x 1 / 3 x 2):")
    salvar(folha_cabeca(rosto), "personagem/rosto/padrao.png")
    salvar(folha_cabeca(cabelo_frente("curto"), recortes=True), "personagem/cabelo/curto_frente.png")
    salvar(folha_cabeca(cabelo_frente("longo"), recortes=True), "personagem/cabelo/longo_frente.png")
    salvar(folha_cabeca(cabelo_tras_longo), "personagem/cabelo/longo_tras.png")
    salvar(folha_cabeca(chapeu_bone, PAL_BONE), "personagem/chapeu/bone.png")
    salvar(folha_cabeca(chapeu_cogumelo, PAL_COGUMELO), "personagem/chapeu/cogumelo.png")
    salvar(folha_cabeca(chapeu_gorro, PAL_GORRO), "personagem/chapeu/gorro.png")

    print("Cenário:")
    salvar(gerar_tiles(), "cenario/tiles.png")
    salvar(gerar_arvore(), "cenario/arvore.png")
    salvar(gerar_casa(), "cenario/casa.png")
    salvar(gerar_casa_luz(), "cenario/casa_luz.png")
    salvar(gerar_fumaca(), "cenario/fumaca.png")
    salvar(gerar_borboleta(), "cenario/borboleta.png")
    salvar(gerar_flores_altas(), "cenario/flores_altas.png")

    print("Ícone:")
    icone = gerar_icone()
    icone.save(RAIZ / "jogo" / "icon.png")
    print("  jogo/icon.png")


if __name__ == "__main__":
    main()
