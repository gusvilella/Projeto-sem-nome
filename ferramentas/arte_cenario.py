"""Cena da região Casa: ilustração vertical em pixel art, câmera em 3/4,
paleta pastel inspirada nas cidades do Ragnarok.

Saídas (ver docs/gdd/05-direcao-de-arte.md#regiões-como-cenas-ilustradas):
- fundo.png: chão (grama, pedras, canteiros), sem objetos
- objetos separados (casa, árvores, postes, poço, banco) para ordenação por profundidade
- caminhavel.png: máscara (branco = o personagem pode andar)
- camadas dos marcos (flores, luzes)
"""

import math
import random

from PIL import Image, ImageDraw

from arte_base import (
    CONTORNO, T, Grade, capsula, colar, contorno, elipsoide, peca, pintar, rampa, ruido_suave,
)

W, H = 540, 1200

# --------------------------------------------------------------------------
# Layout da cena (coordenadas da cena; "pe" = ponto do objeto que toca o chão)
# --------------------------------------------------------------------------

CASA = {"pe": (270, 430), "ancora": (120, 246)}
ARVORES = [(70, 252, False), (168, 216, True), (372, 214, False), (470, 254, True),
           (34, 716, False), (508, 704, True), (30, 880, True), (60, 1120, False), (482, 1130, True)]
POSTES = [(196, 480), (344, 480), (80, 792), (460, 792)]
POCO = (270, 812)
BANCOS = [(428, 600), (112, 600)]
CANTEIROS = [(36, 476, 178, 542), (362, 476, 504, 542), (40, 962, 182, 1034), (358, 962, 500, 1034)]
BORBOLETAS = [(110, 500), (430, 500), (120, 990), (420, 990), (270, 700)]
INICIO = (270, 492)


def na_praca(x, y):
    if 150 <= x <= 390 and 408 <= y <= 472:
        return True
    if abs(x - 270) <= 80 and 408 <= y <= 650:
        return True
    if ((x - 270) / 215) ** 2 + ((y - 792) / 165) ** 2 <= 1:
        return True
    if abs(x - 270) <= 76 and y >= 900:
        return True
    return False


def no_canteiro(x, y, margem=0):
    return any(x0 - margem <= x <= x1 + margem and y0 - margem <= y <= y1 + margem for x0, y0, x1, y1 in CANTEIROS)


# --------------------------------------------------------------------------
# Chão
# --------------------------------------------------------------------------

GRAMA = [(118, 156, 96), (136, 174, 104), (152, 190, 114), (168, 202, 124), (184, 214, 138), (202, 226, 154)]
PEDRAS = [(228, 220, 208), (220, 214, 206), (234, 226, 212), (214, 208, 200)]
PEDRA_LUZ = (242, 238, 230)
PEDRA_SOMBRA = (196, 188, 178)
REJUNTE = (174, 166, 158)
MEIO_FIO = (160, 152, 146)
TERRA = (124, 98, 80)
TERRA_ESC = (102, 80, 66)
FOLHAS = [(74, 122, 82), (94, 148, 88), (120, 174, 100), (152, 200, 118)]


def _celula_pedra(rng_cache, i, j):
    chave = (i, j)
    if chave not in rng_cache:
        r = random.Random(i * 7919 + j * 104729)
        cx = i * 11 + (5.5 if j % 2 else 0) + r.uniform(-1.6, 1.6)
        cy = j * 8 + r.uniform(-1.2, 1.2)
        rng_cache[chave] = (cx, cy, PEDRAS[r.randrange(len(PEDRAS))])
    return rng_cache[chave]


def gerar_fundo():
    img = Image.new("RGBA", (W, H))
    px = img.load()
    grande = ruido_suave(W, H, 46, 1)
    medio = ruido_suave(W, H, 11, 2)
    rng = random.Random(5)
    cache = {}
    for y in range(H):
        for x in range(W):
            if na_praca(x, y):
                borda = not (na_praca(x - 2, y) and na_praca(x + 2, y) and na_praca(x, y - 2) and na_praca(x, y + 3))
                if borda:
                    px[x, y] = (*MEIO_FIO, 255) if not na_praca(x, y + 3) else (*PEDRA_SOMBRA, 255)
                    continue
                i0, j0 = x // 11, y // 8
                melhor = segundo = 1e9
                escolhido = None
                for j in (j0 - 1, j0, j0 + 1):
                    for i in (i0 - 1, i0, i0 + 1):
                        cx, cy, cor = _celula_pedra(cache, i, j)
                        d = math.hypot((x + 0.5 - cx) / 1.0, (y + 0.5 - cy) / 0.72)
                        if d < melhor:
                            segundo, melhor, escolhido = melhor, d, (cx, cy, cor)
                        elif d < segundo:
                            segundo = d
                if segundo - melhor < 1.3:
                    px[x, y] = (*REJUNTE, 255)
                else:
                    cx, cy, cor = escolhido
                    dx, dy = (x + 0.5 - cx) / 5.5, (y + 0.5 - cy) / 4.0
                    if dx + dy < -0.75:
                        cor = PEDRA_LUZ
                    elif dx + dy > 0.55 or segundo - melhor < 2.2 and dy > 0:
                        cor = PEDRA_SOMBRA
                    px[x, y] = (*cor, 255)
            else:
                v = 0.55 * grande(x, y) + 0.45 * medio(x, y)
                k = 2 + int(v * 2.3)
                r = rng.random()
                if r < 0.025:
                    k += 1
                elif r < 0.05:
                    k -= 1
                px[x, y] = (*GRAMA[max(0, min(5, k))], 255)
    # tufos de grama
    for _ in range(900):
        x, y = rng.randrange(4, W - 4), rng.randrange(4, H - 4)
        if na_praca(x, y) or na_praca(x, y + 2):
            continue
        for dx, dy, c in ((0, 0, 0), (-1, -1, 1), (1, -1, 1), (0, -2, 4), (-2, -2, 3), (2, -3, 4)):
            px[x + dx, y + dy] = (*GRAMA[c], 255)
    # sombra suave da grama sobre a borda das pedras
    for x0, y0, x1, y1 in CANTEIROS:
        _canteiro(px, x0, y0, x1, y1, rng)
    return img


def _canteiro(px, x0, y0, x1, y1, rng):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            canto = (x in (x0, x1)) and (y in (y0, y1))
            if canto:
                continue
            if y >= y1 - 4:  # face da frente do murinho
                cor = (196, 186, 174) if (x + (0 if (y - y1) % 2 else 3)) % 7 else (168, 158, 148)
                if y == y1 - 4:
                    cor = (214, 206, 196)
            elif y <= y0 + 2 or x <= x0 + 2 or x >= x1 - 2:  # topo do murinho
                cor = (236, 228, 216) if y <= y0 + 1 or x <= x0 + 1 else (216, 208, 198)
            else:
                cor = TERRA if (x * 3 + y * 5) % 11 else TERRA_ESC
            px[x, y] = (*cor, 255)
    # folhagem
    for _ in range((x1 - x0) * (y1 - y0) // 14):
        fx, fy = rng.uniform(x0 + 5, x1 - 5), rng.uniform(y0 + 4, y1 - 8)
        for yy in range(int(fy) - 2, int(fy) + 3):
            for xx in range(int(fx) - 3, int(fx) + 4):
                d = ((xx + 0.5 - fx) / 3.4) ** 2 + ((yy + 0.5 - fy) / 2.4) ** 2
                if d <= 1 and x0 + 3 <= xx <= x1 - 3 and y0 + 3 <= yy <= y1 - 6:
                    k = 3 if (xx - fx) + (yy - fy) < -1.5 else 2 if d < 0.6 else 1
                    px[xx, yy] = (*FOLHAS[k], 255)
    # poucas flores (o marco de 25% traz o resto)
    for _ in range((x1 - x0) * (y1 - y0) // 900):
        fx, fy = rng.randrange(x0 + 6, x1 - 6), rng.randrange(y0 + 5, y1 - 9)
        _flor(px, fx, fy, rng.choice(CORES_FLOR))


CORES_FLOR = [((244, 150, 176), (214, 104, 138)), ((250, 214, 110), (220, 170, 70)),
              ((252, 248, 240), (204, 198, 210)), ((206, 170, 236), (160, 122, 204)),
              ((240, 120, 110), (200, 84, 84))]


def _flor(px, x, y, cores):
    clara, escura = cores
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        px[x + dx, y + dy] = (*(clara if dy <= 0 else escura), 255)
    px[x, y] = (250, 206, 90, 255)


def gerar_flores_marco():
    """Camada do marco de 25%: canteiros floridos e flores soltas na grama."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    rng = random.Random(25)
    for x0, y0, x1, y1 in CANTEIROS:
        for _ in range((x1 - x0) * (y1 - y0) // 60):
            _flor(px, rng.randrange(x0 + 5, x1 - 5), rng.randrange(y0 + 4, y1 - 8), rng.choice(CORES_FLOR))
    for _ in range(140):
        x, y = rng.randrange(8, W - 8), rng.randrange(260, H - 8)
        if not na_praca(x, y) and not no_canteiro(x, y, 4) and not na_praca(x, y + 3):
            _flor(px, x, y, rng.choice(CORES_FLOR))
            if rng.random() < 0.5:
                _flor(px, x + 3, y + 2, rng.choice(CORES_FLOR))
    return img


# --------------------------------------------------------------------------
# Objetos
# --------------------------------------------------------------------------

def _rgba(c, a=255):
    return (*c, a)


TELHA = rampa("#d98466")
REBOCO = [(198, 180, 160), (226, 210, 188), (238, 226, 206), (246, 238, 222)]
MADEIRA = rampa("#9c6a4c", 0.9)
PEDRA_R = rampa("#d8d0c4", 0.7)
VIDRO = [(120, 150, 180), (146, 176, 202), (178, 204, 224), (214, 230, 242)]
VENEZIANA = rampa("#7fb8a8", 0.9)
CONTORNO_CASA = (100, 70, 60, 255)


def gerar_casa():
    w, h = 240, 250
    g = Grade(w, h)
    ruido = ruido_suave(w, h, 6, 9)
    # paredes
    for y in range(120, 228):
        for x in range(22, 219):
            k = 2 if ruido(x, y) > 0.5 else 1
            if y < 134:
                k = 0  # sombra do beiral
            if x < 30 and y > 140:
                k = min(k + 1, 3)
            g.set(x, y, _rgba(REBOCO[k]))
    # madeiramento
    def viga(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                borda_luz = x == x0 or y == y0
                g.set(x, y, _rgba(MADEIRA[6 if borda_luz else 4]))
    for x in (22, 84, 154, 214):
        viga(x, 124, x + 4, 226)
    viga(22, 124, 218, 128)
    for (ax, ay, bx, by) in ((89, 130, 101, 152), (152, 130, 140, 152), (27, 200, 38, 222), (213, 200, 202, 222)):
        n = max(abs(bx - ax), abs(by - ay))
        for k in range(n + 1):
            x, y = round(ax + (bx - ax) * k / n), round(ay + (by - ay) * k / n)
            for d in range(3):
                g.set(x + d, y, _rgba(MADEIRA[4 if d else 6]))
    # base de pedra
    for y in range(226, 247):
        linha = (y - 226) // 7
        for x in range(18, 223):
            junta = (y - 226) % 7 == 6 or (x + linha * 9) % 18 == 0
            if junta:
                c = PEDRA_R[2]
            else:
                c = PEDRA_R[6] if (y - 226) % 7 < 2 else PEDRA_R[5]
            g.set(x, y, _rgba(c))
    # porta em arco
    for y in range(150, 228):
        for x in range(98, 143):
            dx = x + 0.5 - 120.5
            topo = 170 - math.sqrt(max(0, 22 ** 2 - dx * dx))
            if y + 0.5 >= topo:
                dentro = y + 0.5 >= topo + 3 and 102 <= x <= 138
                if not dentro:
                    g.set(x, y, _rgba(PEDRA_R[6] if x < 120 else PEDRA_R[5]))
                else:
                    c = MADEIRA[3] if (x - 102) % 6 == 0 else MADEIRA[5] if x < 112 else MADEIRA[4]
                    g.set(x, y, _rgba(c))
    for x, y in ((131, 192), (132, 192), (131, 193), (132, 193)):
        g.set(x, y, (236, 196, 96, 255))
    for x in range(106, 136):  # dobradiças
        if x < 112 or x > 129:
            g.set(x, 176, _rgba(MADEIRA[1]))
            g.set(x, 210, _rgba(MADEIRA[1]))
    # janelas
    for jx in (38, 170):
        _janela(g, jx, 142)
    # arbustos nos cantos
    arb = Grade(w, h)
    for cx in (14, 226):
        for bx, by, r in ((cx, 236, 13), (cx + (8 if cx < 100 else -8), 240, 9), (cx - (6 if cx < 100 else -6), 228, 8)):
            elipsoide(arb, bx, by, r, r * 0.78)
    contorno(arb)
    arb = pintar(arb, {"base": rampa("#7fba6c")})
    # telhado
    tel = Grade(w, h)
    for y in range(12, 128):
        meia = 68 + (y - 12) / 106 * 50
        x0, x1 = 120 - meia, 120 + meia
        linha = (y - 12) // 8
        dy = (y - 12) % 8
        for x in range(int(x0), int(x1) + 1):
            fx = (x + (6 if linha % 2 else 0)) % 12
            curva = abs(fx - 6) / 6
            fundo = dy >= 6 or (dy == 5 and curva > 0.6)
            lado = (x - 120) / meia
            t = 6 - (2 if fundo else 0) + (1 if dy <= 1 else 0) - (1 if lado > 0.35 else 0) + (1 if lado < -0.45 else 0)
            if y >= 120:
                t = 2 if y >= 124 else 3
            tel.set(x, y, max(2, min(8, t)))
    for x in range(52, 189):  # cumeeira
        for y in range(9, 15):
            tel.set(x, y, 4 if y >= 13 else 7 if y == 9 else 5)
    tel = pintar(tel, {"base": TELHA})
    # chaminé
    cham = Grade(w, h)
    for y in range(0, 44):
        for x in range(160, 183):
            if y < 6:
                c = (150, 140, 140) if y > 1 else (186, 176, 176)
            else:
                junta = (y - 6) % 5 == 4 or (x + ((y - 6) // 5) * 4) % 8 == 0
                c = (164, 104, 88) if junta else (204, 136, 112) if x < 170 else (186, 120, 100)
            cham.set(x, y, (*c, 255))

    final = Grade(w, h)
    colar(final, g)
    colar(final, tel)
    colar(final, cham)
    contorno(final, valor=CONTORNO_CASA)
    colar(final, arb)
    return final


def _janela(g, x0, y0):
    jw, jh = 34, 50
    for y in range(y0, y0 + jh):
        for x in range(x0, x0 + jw):
            moldura = x < x0 + 3 or x >= x0 + jw - 3 or y < y0 + 3 or y >= y0 + jh - 3
            cruz = abs(x - (x0 + jw // 2)) <= 1 or abs(y - (y0 + jh // 2 - 4)) <= 1
            if moldura or cruz:
                g.set(x, y, (246, 240, 228, 255) if not (moldura and (x >= x0 + jw - 2 or y >= y0 + jh - 2)) else (214, 206, 194, 255))
            else:
                t = (x - x0) / jw + (y - y0) / jh
                k = 3 if t < 0.5 else 2 if t < 0.9 else 1
                if (x - x0) + (y - y0) in (16, 17, 26):
                    k = 3
                g.set(x, y, _rgba(VIDRO[k]))
    for sx in (x0 - 10, x0 + jw):  # venezianas
        for y in range(y0, y0 + jh):
            for x in range(sx, sx + 10):
                k = 4 if (y - y0) % 4 == 3 else 6 if x == sx else 5
                g.set(x, y, _rgba(VENEZIANA[k]))
    for y in range(y0 + jh, y0 + jh + 8):  # floreira
        for x in range(x0 - 4, x0 + jw + 4):
            g.set(x, y, _rgba(MADEIRA[5 if y < y0 + jh + 2 else 3]))


def gerar_casa_flores():
    img = Image.new("RGBA", (240, 250), (0, 0, 0, 0))
    px = img.load()
    rng = random.Random(4)
    for jx in (38, 170):
        for x in range(jx - 2, jx + 36, 4):
            for dx, dy in ((0, 0), (1, 0), (0, 1), (2, 1)):
                px[x + dx, 190 + dy] = (*FOLHAS[2], 255)
            _flor(px, x + 1, 188 - rng.randrange(0, 3), rng.choice(CORES_FLOR))
    for cx in (12, 228):
        for _ in range(6):
            _flor(px, cx + rng.randrange(-10, 10), 232 + rng.randrange(-6, 8), rng.choice(CORES_FLOR))
    return img


def gerar_casa_luz():
    img = Image.new("RGBA", (240, 250), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for jx in (38, 170):
        d.rectangle((jx - 4, 138, jx + 37, 195), fill=(255, 210, 130, 50))
        for y in range(145, 189):
            for x in range(jx + 3, jx + 31):
                if abs(x - (jx + 17)) > 1 and abs(y - (142 + 21)) > 1:
                    img.putpixel((x, y), (255, 214, 128, 225))
    return img


def gerar_arvore(semente=1):
    w, h = 112, 140
    rng = random.Random(semente)
    sombra = Grade(w, h)
    elipsoide(sombra, 56, 131, 34, 8, valor=(70, 104, 70, 80))

    tronco = peca(w, h, lambda q: (capsula(q, 56, 96, 56, 128, 5.5, 6.5),
                                   capsula(q, 48, 129, 64, 129, 3, 3)))
    tronco = pintar(tronco, {"base": rampa("#a07a5a", 0.9)})

    blocos = [(56, 60, 44, 38), (30, 78, 24, 19), (82, 78, 24, 19), (56, 90, 32, 16), (38, 40, 22, 18), (74, 38, 22, 18)]
    copa = Grade(w, h)
    for bx, by, rx, ry in blocos:
        elipsoide(copa, bx, by, rx, ry)
    # borda recortada em tufos
    for _ in range(46):
        a = rng.uniform(0, math.tau)
        bx, by, rx, ry = rng.choice(blocos)
        px, py = bx + math.cos(a) * rx * 0.92, by + math.sin(a) * ry * 0.92
        elipsoide(copa, px, py, 6, 5)
    # tufos internos de luz
    for _ in range(70):
        px, py = rng.uniform(16, 96), rng.uniform(12, 100)
        if copa.get(int(px), int(py)) != T:
            lado = (px - 56) / 50 + (py - 60) / 45
            ajuste = 1 if lado < -0.3 else -1 if lado > 0.5 else 0
            elipsoide(copa, px, py, 4.5, 3.6, ajuste=ajuste,
                      recorte=lambda x, y: copa.get(x, y) != T)
    contorno(copa)
    copa = pintar(copa, {"base": rampa("#88c272")})

    final = Grade(w, h)
    colar(final, sombra)
    colar(final, tronco)
    colar(final, copa)
    return final


FERRO = rampa("#6e7690", 0.8)


def gerar_poste():
    w, h = 28, 96
    g = peca(w, h, lambda q: (capsula(q, 14, 22, 14, 86, 1.8),
                             capsula(q, 9, 89, 19, 89, 3.2),
                             elipsoide(q, 14, 4, 8, 3.5)))
    g = pintar(g, {"base": FERRO})
    for y in range(7, 24):  # lanterna
        for x in range(6, 23):
            moldura = x in (6, 22) or y in (7, 23) or x == 14
            g.set(x, y, (*FERRO[3], 255) if moldura else (220, 228, 230, 255) if y < 15 else (200, 210, 216, 255))
    contorno(g, valor=(*FERRO[0], 255))
    return g


def gerar_poste_luz():
    img = Image.new("RGBA", (28, 96), (0, 0, 0, 0))
    for y in range(0, 30):
        for x in range(0, 28):
            d = math.hypot(x + 0.5 - 14, y + 0.5 - 15)
            if 7 <= x <= 21 and 8 <= y <= 22 and x != 14:
                img.putpixel((x, y), (255, 222, 140, 240))
            elif d < 14:
                img.putpixel((x, y), (255, 214, 130, int(70 * (1 - d / 14))))
    return img


def gerar_poco():
    w, h = 80, 92
    g = Grade(w, h)
    pedra = rampa("#cfc6b8", 0.8)
    # cilindro de pedra
    cil = Grade(w, h)
    for y in range(56, 86):
        for x in range(9, 72):
            nx = (x + 0.5 - 40.5) / 31
            base = 80 + 6 * math.sqrt(max(0, 1 - nx * nx))
            if abs(nx) <= 1 and y + 0.5 <= base:
                linha = (y - 56) // 6
                junta = (y - 56) % 6 == 5 or (x + linha * 5) % 10 == 0
                t = 2 if junta else (6 if nx < -0.4 else 4 if nx > 0.5 else 5)
                cil.set(x, y, t)
    elipsoide(cil, 40.5, 57, 31, 11, recorte=lambda x, y: True)
    for x, y, v in list(cil.pixels()):
        if ((x + 0.5 - 40.5) / 31) ** 2 + ((y + 0.5 - 57) / 11) ** 2 <= 1:
            dentro = ((x + 0.5 - 40.5) / 24) ** 2 + ((y + 0.5 - 58) / 7.5) ** 2 <= 1
            cil.set(x, y, ("agua", 3 if y < 58 else 2) if dentro else 7)
    contorno(cil)
    colar(g, pintar(cil, {"base": pedra, "agua": rampa("#5a7c9c")}))
    # postes e telhadinho
    madeira = peca(w, h, lambda q: (capsula(q, 15, 20, 15, 58, 2.2), capsula(q, 66, 20, 66, 58, 2.2),
                                     capsula(q, 15, 26, 66, 26, 1.4)))
    colar(g, pintar(madeira, {"base": MADEIRA}))
    corda = Grade(w, h)
    for y in range(27, 40):
        corda.set(40, y, (220, 200, 160, 255))
    colar(g, corda)
    balde = peca(w, h, lambda q: capsula(q, 40, 41, 40, 45, 3.2))
    colar(g, pintar(balde, {"base": rampa("#8a96a8", 0.8)}))
    telhado = Grade(w, h)
    for y in range(2, 22):
        meia = 14 + (y - 2) * 1.35
        for x in range(int(40.5 - meia), int(40.5 + meia) + 1):
            dy = (y - 2) % 5
            t = 3 if dy == 4 else (7 if x < 40 else 5)
            telhado.set(x, y, t)
    contorno(telhado)
    colar(g, pintar(telhado, {"base": TELHA}))
    return g


def gerar_banco():
    w, h = 64, 40
    g = Grade(w, h)
    pes = peca(w, h, lambda q: (capsula(q, 10, 18, 10, 36, 1.6), capsula(q, 54, 18, 54, 36, 1.6)))
    colar(g, pintar(pes, {"base": FERRO}))
    assento = Grade(w, h)
    for y, (y0, y1) in enumerate(((3, 6), (8, 11), (15, 21))):
        for yy in range(y0, y1 + 1):
            for x in range(4, 61):
                assento.set(x, yy, 7 if yy == y0 else 4 if yy == y1 else 6)
    contorno(assento)
    colar(g, pintar(assento, {"base": MADEIRA}))
    return g


def gerar_borboleta():
    asa, asa2, corpo_ = (250, 196, 120, 255), (246, 160, 170, 255), (80, 56, 70, 255)
    img = Image.new("RGBA", (20, 8), (0, 0, 0, 0))
    for quadro, aberta in enumerate((True, False)):
        ox = quadro * 10
        for y in range(1, 7):
            img.putpixel((ox + 5, y), corpo_)
        if aberta:
            for x0 in (1, 6):
                for y in range(1, 4):
                    for x in range(x0, x0 + 3):
                        img.putpixel((ox + x, y), asa)
                for x in range(x0, x0 + 2):
                    img.putpixel((ox + x + (1 if x0 == 1 else 0), 4), asa2)
                    img.putpixel((ox + x + (1 if x0 == 1 else 0), 5), asa2)
        else:
            for y in range(1, 5):
                img.putpixel((ox + 4, y), asa)
                img.putpixel((ox + 6, y), asa)
    return img


def gerar_fumaca():
    g = Grade(16, 16)
    elipsoide(g, 8, 9, 5.5, 4.5, valor=(240, 238, 242, 210))
    elipsoide(g, 5.5, 7, 3, 2.6, valor=(250, 250, 252, 225))
    contorno(g, valor=(206, 204, 214, 150))
    return g


def gerar_folha():
    img = Image.new("RGBA", (6, 5), (0, 0, 0, 0))
    for x, y, c in ((1, 1, (156, 196, 96)), (2, 1, (176, 210, 110)), (3, 2, (176, 210, 110)), (2, 2, (140, 182, 88)),
                    (1, 2, (140, 182, 88)), (3, 1, (196, 222, 126)), (4, 3, (120, 160, 80)), (2, 3, (120, 160, 80))):
        img.putpixel((x, y), (*c, 255))
    return img


# --------------------------------------------------------------------------
# Máscara caminhável
# --------------------------------------------------------------------------

def gerar_caminhavel():
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    d.rectangle((12, 262, W - 13, H - 10), fill=255)
    preto = 0
    d.rectangle((140, 296, 400, 436), fill=preto)  # casa
    for x, y, _ in ARVORES:
        d.ellipse((x - 16, y - 9, x + 16, y + 6), fill=preto)
    for x, y in POSTES:
        d.ellipse((x - 9, y - 6, x + 9, y + 5), fill=preto)
    d.ellipse((POCO[0] - 38, POCO[1] - 34, POCO[0] + 38, POCO[1] + 6), fill=preto)
    for x, y in BANCOS:
        d.rectangle((x - 34, y - 26, x + 34, y + 4), fill=preto)
    for x0, y0, x1, y1 in CANTEIROS:
        d.rectangle((x0 - 6, y0 - 6, x1 + 6, y1 + 4), fill=preto)
    return img


def dados_da_cena(base="res://arte/cenario/casa/"):
    objetos = [{"textura": base + "casa.png", "pe": list(CASA["pe"]), "ancora": list(CASA["ancora"])}]
    for x, y, espelhar in ARVORES:
        objetos.append({"textura": base + "arvore.png", "pe": [x, y], "ancora": [56, 132], "espelhar": espelhar})
    for x, y in POSTES:
        objetos.append({"textura": base + "poste.png", "pe": [x, y], "ancora": [14, 92]})
    objetos.append({"textura": base + "poco.png", "pe": list(POCO), "ancora": [40, 86]})
    for x, y in BANCOS:
        objetos.append({"textura": base + "banco.png", "pe": [x, y], "ancora": [32, 36]})
    cx, cy = CASA["pe"]
    ax, ay = CASA["ancora"]
    luzes = [{"textura": base + "casa_luz.png", "pe": [cx, cy], "ancora": [ax, ay], "acima_de": 0}]
    for i, (x, y) in enumerate(POSTES):
        luzes.append({"textura": base + "poste_luz.png", "pe": [x, y], "ancora": [14, 92], "acima_de": 1 + len(ARVORES) + i})
    return {
        "tamanho": [W, H],
        "fundo": base + "fundo.png",
        "caminhavel": base + "caminhavel.png",
        "inicio": list(INICIO),
        "chamine": [cx - ax + 171, cy - ay + 2],
        "objetos": objetos,
        "marcos": {
            "flores": [
                {"textura": base + "flores.png", "pe": [0, 0], "ancora": [0, 0], "chao": True},
                {"textura": base + "casa_flores.png", "pe": [cx, cy], "ancora": [ax, ay], "acima_de": 0},
            ],
            "luz": luzes,
            "borboletas": [list(b) for b in BORBOLETAS],
        },
    }
