"""Primitivas de desenho da arte provisória: grade de pixels, volumes com luz,
contorno, rampas de cor de 8 tons e exportação.

Cada pixel da grade guarda:
- 0: transparente
- 1..8: um tom da rampa (1 = contorno, 2 = sombra mais funda ... 8 = luz)
- tupla RGBA: cor fixa
"""

import colorsys
import math
import random

from PIL import Image

T = 0
CONTORNO = 1
# Valores de cinza de cada tom nas camadas recoloríveis (R = G = B).
CINZAS = [28 * i for i in range(1, 9)]

_L = (-0.45, -0.65, 0.62)
_n = math.sqrt(sum(c * c for c in _L))
LUZ = tuple(c / _n for c in _L)  # vinda de cima-esquerda, de frente


class Grade:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[T] * w for _ in range(h)]

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.p[y][x]
        return T

    def set(self, x, y, v):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = v

    def pixels(self):
        for y in range(self.h):
            for x in range(self.w):
                v = self.p[y][x]
                if v != T:
                    yield x, y, v


def tom_da_normal(nx, ny, nz, ajuste=0):
    d = nx * LUZ[0] + ny * LUZ[1] + nz * LUZ[2]
    s = 0.5 + 0.5 * d
    return max(2, min(8, 2 + int(round(s * 6.0)) + ajuste))


def _caixa(g, x0, y0, x1, y1):
    return (max(0, int(math.floor(x0)) - 1), max(0, int(math.floor(y0)) - 1),
            min(g.w - 1, int(math.ceil(x1)) + 1), min(g.h - 1, int(math.ceil(y1)) + 1))


def elipsoide(g, cx, cy, rx, ry, ajuste=0, recorte=None, valor=None):
    """Volume arredondado com luz. recorte(x, y) -> bool limita a área."""
    xa, ya, xb, yb = _caixa(g, cx - rx, cy - ry, cx + rx, cy + ry)
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            nx = (x + 0.5 - cx) / rx
            ny = (y + 0.5 - cy) / ry
            r2 = nx * nx + ny * ny
            if r2 <= 1 and (recorte is None or recorte(x, y)):
                if valor is not None:
                    g.set(x, y, valor)
                else:
                    g.set(x, y, tom_da_normal(nx, ny, math.sqrt(1 - r2), ajuste))


def elipse_girada(g, cx, cy, rx, ry, angulo, ajuste=0, valor=None):
    c, s = math.cos(math.radians(angulo)), math.sin(math.radians(angulo))
    r = max(rx, ry)
    xa, ya, xb, yb = _caixa(g, cx - r, cy - r, cx + r, cy + r)
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u = (dx * c + dy * s) / rx
            v = (-dx * s + dy * c) / ry
            r2 = u * u + v * v
            if r2 <= 1:
                if valor is not None:
                    g.set(x, y, valor)
                else:
                    nx, ny = u * c - v * s, u * s + v * c
                    g.set(x, y, tom_da_normal(nx * 0.8, ny * 0.8, math.sqrt(1 - r2), ajuste))


def capsula(g, x0, y0, x1, y1, r0, r1=None, ajuste=0, recorte=None, valor=None):
    """Cilindro com pontas arredondadas, de raio r0 em (x0, y0) até r1 em (x1, y1)."""
    r1 = r0 if r1 is None else r1
    rmax = max(r0, r1)
    xa, ya, xb, yb = _caixa(g, min(x0, x1) - rmax, min(y0, y1) - rmax, max(x0, x1) + rmax, max(y0, y1) + rmax)
    vx, vy = x1 - x0, y1 - y0
    comp2 = vx * vx + vy * vy or 1e-9
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            px, py = x + 0.5, y + 0.5
            t = max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / comp2))
            r = r0 + (r1 - r0) * t
            cx, cy = x0 + vx * t, y0 + vy * t
            dx, dy = px - cx, py - cy
            d = math.hypot(dx, dy)
            if d <= r and (recorte is None or recorte(x, y)):
                if valor is not None:
                    g.set(x, y, valor)
                else:
                    nx, ny = dx / r, dy / r
                    g.set(x, y, tom_da_normal(nx, ny, math.sqrt(max(0.0, 1 - nx * nx - ny * ny)), ajuste))


def tronco_conico(g, cx, y0, y1, meia0, meia1, ajuste=0, recorte=None):
    """Forma de saia/tronco: largura varia de meia0 (no topo) a meia1 (embaixo), luz cilíndrica."""
    for y in range(int(y0), int(math.ceil(y1)) + 1):
        t = (y + 0.5 - y0) / max(1e-9, (y1 - y0))
        if t < 0 or t > 1:
            continue
        meia = meia0 + (meia1 - meia0) * t
        for x in range(int(cx - meia) - 1, int(cx + meia) + 2):
            nx = (x + 0.5 - cx) / meia
            if abs(nx) <= 1 and (recorte is None or recorte(x, y)):
                g.set(x, y, tom_da_normal(nx, -0.15 + 0.3 * t, math.sqrt(max(0.0, 1 - nx * nx)), ajuste))


def retangulo(g, x0, y0, x1, y1, valor):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            g.set(x, y, valor)


def contorno(g, valor=CONTORNO):
    novos = []
    for y in range(g.h):
        for x in range(g.w):
            if g.p[y][x] == T and (
                g.get(x + 1, y) != T or g.get(x - 1, y) != T or g.get(x, y + 1) != T or g.get(x, y - 1) != T
            ):
                novos.append((x, y))
    for x, y in novos:
        g.p[y][x] = valor


def colar(dest, src, dx=0, dy=0):
    for x, y, v in src.pixels():
        dest.set(x + dx, y + dy, v)


def peca(w, h, *desenhos, contornar=True):
    g = Grade(w, h)
    for d in desenhos:
        d(g)
    if contornar:
        contorno(g)
    return g


def limpar(g, condicao):
    for y in range(g.h):
        for x in range(g.w):
            if condicao(x, y):
                g.p[y][x] = T


def escurecer(g, condicao, passos=1):
    for y in range(g.h):
        for x in range(g.w):
            v = g.p[y][x]
            if isinstance(v, int) and v > CONTORNO and condicao(x, y):
                g.p[y][x] = max(2, v - passos)


def clarear(g, condicao, passos=1):
    for y in range(g.h):
        for x in range(g.w):
            v = g.p[y][x]
            if isinstance(v, int) and v > CONTORNO and condicao(x, y):
                g.p[y][x] = min(8, v + passos)


# --------------------------------------------------------------------------
# Cores
# --------------------------------------------------------------------------

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(c):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c[:3])


def _misturar_matiz(h, alvo, t):
    d = ((alvo - h + 0.5) % 1.0) - 0.5
    return (h + d * t) % 1.0


def rampa(base_hex, contraste=1.0):
    """8 tons a partir de uma cor-base (que vira o tom 6).
    Sombras puxam para o roxo, luzes para o amarelo, como na pixel art pastel."""
    r, g, b = (c / 255 for c in hex_rgb(base_hex))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    tons = []
    # tom: 1 contorno, 2..8 da sombra para a luz
    fatores_v = [0.42, 0.62, 0.72, 0.83, 0.92, 1.0, 1.07, 1.13]
    fatores_s = [1.25, 1.18, 1.12, 1.07, 1.03, 1.0, 0.86, 0.68]
    for i in range(8):
        fv = 1 + (fatores_v[i] - 1) * contraste
        vi = min(1.0, v * fv) if i < 6 else min(1.0, v + (1 - v) * (fatores_v[i] - 1) * 4 * contraste)
        si = max(0.0, min(1.0, s * fatores_s[i]))
        if i < 5:
            hi = _misturar_matiz(h, 0.75, 0.10 * (5 - i) / 5 * 1.6)
        elif i > 5:
            hi = _misturar_matiz(h, 0.13, 0.08 * (i - 5))
        else:
            hi = h
        if i == 0:
            si = min(1.0, s * 0.9 + 0.25)
        rr, gg, bb = colorsys.hsv_to_rgb(hi, si, vi)
        tons.append((round(rr * 255), round(gg * 255), round(bb * 255)))
    return tons


def pintar(g, rampas):
    """Converte tons (int -> rampa "base") e (material, tom) em cores fixas."""
    saida = Grade(g.w, g.h)
    for x, y, v in g.pixels():
        if isinstance(v, int):
            saida.p[y][x] = (*rampas["base"][v - 1], 255)
        elif isinstance(v[0], str):
            saida.p[y][x] = (*rampas[v[0]][v[1] - 1], 255)
        else:
            saida.p[y][x] = v
    return saida


def cor_do_pixel(v, paleta):
    if v == T:
        return (0, 0, 0, 0)
    if isinstance(v, tuple):
        return v if len(v) == 4 else (*v, 255)
    if paleta is None:
        c = CINZAS[v - 1]
        return (c, c, c, 255)
    c = paleta[v - 1]
    return c if len(c) == 4 else (*c, 255)


def imagem(g, paleta=None):
    img = Image.new("RGBA", (g.w, g.h), (0, 0, 0, 0))
    px = img.load()
    for x, y, v in g.pixels():
        px[x, y] = cor_do_pixel(v, paleta)
    return img


def folha(quadros, paleta=None):
    """quadros[linha][coluna] -> Grade (todas do mesmo tamanho)."""
    w, h = quadros[0][0].w, quadros[0][0].h
    img = Image.new("RGBA", (w * len(quadros[0]), h * len(quadros)), (0, 0, 0, 0))
    for li, linha in enumerate(quadros):
        for co, g in enumerate(linha):
            img.paste(imagem(g, paleta), (co * w, li * h))
    return img


def ruido_suave(w, h, passo, semente):
    """Ruído de valor interpolado (0..1), para variações grandes e suaves."""
    rng = random.Random(semente)
    gw, gh = w // passo + 2, h // passo + 2
    grade = [[rng.random() for _ in range(gw)] for _ in range(gh)]

    def amostra(x, y):
        fx, fy = x / passo, y / passo
        ix, iy = int(fx), int(fy)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = grade[iy][ix] * (1 - tx) + grade[iy][ix + 1] * tx
        b = grade[iy + 1][ix] * (1 - tx) + grade[iy + 1][ix + 1] * tx
        return a * (1 - ty) + b * ty
    return amostra
