"""Personagem no estilo chibi do Ragnarok, em camadas (paper doll).

Formatos (ver docs/arte/briefing-artista.md):
- Camadas de corpo: folha 6 x 3 de quadros 64 x 80. Colunas 0-1 parado,
  2-5 andar. Linhas: baixo (frente), cima (costas), lado (virado p/ direita).
- Camadas de cabeça: quadros 96 x 112, um por direção. O centro da cabeça
  fica no ponto (48, 72) e o jogo o posiciona pela âncora de cada quadro.
"""

import math

from arte_base import (
    CONTORNO, T, Grade, capsula, clarear, colar, contorno, elipse_girada, elipsoide,
    escurecer, limpar, peca, retangulo, tronco_conico,
)

CW, CH = 64, 80
PES = (32, 76)
HW, HH = 96, 112
PONTO_CABECA = (48, 72)
DIRECOES = ("baixo", "cima", "lado")
COLUNAS = 6
BALANCO = [0, 1, 0, -1, 0, -1]  # sobe e desce do tronco e da cabeça por coluna


# --------------------------------------------------------------------------
# Pose
# --------------------------------------------------------------------------

class Pose:
    """Esqueleto simplificado de um quadro."""

    def __init__(self, direcao, col):
        self.direcao = direcao
        self.lado = direcao == "lado"
        self.b = BALANCO[col]
        fase = col - 2 if col >= 2 else None
        # pernas: (dx, dy) do tornozelo; braços: (dx, dy) da mão
        if fase is None:
            pe_a, pe_b, mao_a, mao_b = (0, 0), (0, 0), (0, 0), (0, 0)
        elif self.lado:
            # a = membro perto da câmera, b = membro longe
            pe_a, pe_b = [((5, 0), (-5, -1)), ((0, 0), (1, -3)), ((-5, -1), (5, 0)), ((1, -3), (0, 0))][fase]
            mao_a, mao_b = [((-3, 0), (3, 0)), ((0, 0), (0, 0)), ((3, 0), (-3, 0)), ((0, 0), (0, 0))][fase]
        else:
            # a = esquerda da tela, b = direita da tela
            pe_a, pe_b = [((0, 1), (0, -2)), ((0, 0), (0, 0)), ((0, -2), (0, 1)), ((0, 0), (0, 0))][fase]
            mao_a, mao_b = [((0, 1), (0, -1)), ((0, 0), (0, 0)), ((0, -1), (0, 1)), ((0, 0), (0, 0))][fase]
        self.pe_a, self.pe_b, self.mao_a, self.mao_b = pe_a, pe_b, mao_a, mao_b

        cx = 33 if self.lado else 32
        self.cabeca = (cx, 25 + self.b)
        if self.lado:
            self.quadril = [(33, 56), (31, 56)]
            self.ombro = [(33.5, 41 + self.b), (30.5, 41 + self.b)]
        else:
            self.quadril = [(29.2, 56), (34.8, 56)]
            self.ombro = [(24.3, 41 + self.b), (39.7, 41 + self.b)]
        pes = [pe_a, pe_b]
        maos = [mao_a, mao_b]
        afastar = [0, 0] if self.lado else [-0.8, 0.8]  # pés levemente para fora
        self.tornozelo = [(self.quadril[i][0] + pes[i][0] + afastar[i], 71.5 + pes[i][1]) for i in range(2)]
        if self.lado:
            self.mao = [(self.ombro[i][0] + maos[i][0], 53.5 + self.b + maos[i][1]) for i in range(2)]
        else:
            self.mao = [(self.ombro[i][0] + (-1.2 if i == 0 else 1.2) + maos[i][0], 53.5 + self.b + maos[i][1])
                        for i in range(2)]

    def ajuste(self, i):
        """Membro longe da câmera (vista de lado) fica mais escuro."""
        return -2 if self.lado and i == 1 else 0

    def ordem(self):
        """Índices dos membros: primeiro os de trás."""
        return [1, 0] if self.lado else [0, 1]


def _livrar_cabeca(g, p):
    """Roupas não podem cobrir a cabeça (nem o contorno do queixo)."""
    cx, cy = p.cabeca
    limpar(g, lambda x, y: ((x + 0.5 - cx) / 13.4) ** 2 + ((y + 0.5 - cy) / 12.8) ** 2 <= 1)


def ancora(direcao, col):
    p = Pose(direcao, col)
    return [p.cabeca[0], p.cabeca[1]]


# --------------------------------------------------------------------------
# Camadas de corpo (64 x 80)
# --------------------------------------------------------------------------

def _tronco(p, g, folga=0.0, fim=None, ajuste=0):
    cx = p.cabeca[0]
    r_topo = (5.8 if p.lado else 7.6) + folga
    r_base = (5.2 if p.lado else 6.4) + folga
    capsula(g, cx, 40.5 + p.b, cx, 52.5 + p.b, r_topo, r_base, ajuste=ajuste,
            recorte=(lambda x, y: y <= fim + p.b) if fim else None)


def _braco(p, g, i, folga=0.0, ate=1.0, ajuste=0):
    ox, oy = p.ombro[i]
    mx, my = p.mao[i]
    x1, y1 = ox + (mx - ox) * ate, oy + (my - oy) * ate
    capsula(g, ox, oy, x1, y1, 2.5 + folga, 2.1 + folga * (0.8 if ate < 1 else 1), ajuste=ajuste + p.ajuste(i))


def _perna(p, g, i, folga=0.0, ate=1.0, ajuste=0):
    qx, qy = p.quadril[i]
    tx, ty = p.tornozelo[i]
    capsula(g, qx, qy, qx + (tx - qx) * ate, qy + (ty - qy) * ate, 2.7 + folga, 2.2 + folga,
            ajuste=ajuste + p.ajuste(i))


def corpo(direcao, col):
    p = Pose(direcao, col)
    g = Grade(CW, CH)
    for i in p.ordem():
        colar(g, peca(CW, CH, lambda q, i=i: _perna(p, q, i)))
    if p.lado:
        colar(g, peca(CW, CH, lambda q: _braco(p, q, 1)))
        colar(g, peca(CW, CH, lambda q: elipsoide(q, *p.mao[1], 2.3, 2.3, ajuste=-2)))
    colar(g, peca(CW, CH, lambda q: capsula(q, p.cabeca[0], 34 + p.b, p.cabeca[0], 40 + p.b, 2.6, ajuste=-2)))
    colar(g, peca(CW, CH, lambda q: _tronco(p, q)))
    for i in ([0] if p.lado else [0, 1]):
        colar(g, peca(CW, CH, lambda q, i=i: _braco(p, q, i)))
        colar(g, peca(CW, CH, lambda q, i=i: elipsoide(q, *p.mao[i], 2.3, 2.3, ajuste=p.ajuste(i))))
    colar(g, peca(CW, CH, lambda q: elipsoide(q, p.cabeca[0], p.cabeca[1], 12.2, 11.6)))
    return g


def camiseta(direcao, col, estilo="camiseta"):
    p = Pose(direcao, col)
    g = Grade(CW, CH)
    cx = p.cabeca[0]
    longa = estilo in ("moletom",)
    manga = 1.0 if longa else 0.42
    if estilo == "moletom" and direcao != "cima":
        # capuz caído atrás do pescoço
        colar(g, peca(CW, CH, lambda q: elipsoide(q, cx - (2 if p.lado else 0), 38.5 + p.b, 8.5 if not p.lado else 6, 4.5,
                                                    ajuste=-1)))
    if p.lado:
        colar(g, peca(CW, CH, lambda q: _braco(p, q, 1, folga=0.9, ate=manga)))

    fim = {"camiseta": 55.5, "moletom": 58, "tunica": 54}[estilo]

    def tronco(q):
        _tronco(p, q, folga=1.1, fim=fim)
        if estilo == "tunica":
            meia = 6.6 if p.lado else 8.2
            tronco_conico(q, cx, 53.5 + p.b, 63 + p.b, meia, meia + 3.2)
        if estilo == "moletom" and direcao == "cima":
            elipsoide(q, cx, 44 + p.b, 6.5, 6, ajuste=-1)  # capuz nas costas
    tr = peca(CW, CH, tronco)
    if estilo == "moletom" and direcao == "baixo":
        # bolso canguru e cordões
        for x in range(cx - 5, cx + 6):
            tr.set(x, 50 + p.b, 3)
        for y in range(50 + p.b, 55 + p.b):
            tr.set(cx - 5, y, 3)
            tr.set(cx + 5, y, 3)
        for y in range(41 + p.b, 46 + p.b):
            tr.set(cx - 2, y, 8)
            tr.set(cx + 2, y, 8)
    if estilo == "tunica":
        for x in range(0, CW):
            if tr.get(x, 53 + p.b) not in (T, CONTORNO):
                tr.set(x, 53 + p.b, 2)
                tr.set(x, 54 + p.b, 3)
        if direcao == "baixo":
            tr.set(cx, 53 + p.b, (232, 196, 96, 255))
            tr.set(cx - 1, 53 + p.b, (196, 150, 64, 255))
            for k in range(4):  # gola em V
                tr.set(cx - 1 - k // 2, 40 + p.b + k, 3)
                tr.set(cx + 1 + k // 2, 40 + p.b + k, 3)
            for x in (cx - 4, cx + 4):  # pregas da saia
                for y in range(57 + p.b, 63 + p.b):
                    if tr.get(x, y) not in (T, CONTORNO):
                        tr.set(x, y, 4)
    colar(g, tr)

    for i in ([0] if p.lado else [0, 1]):
        colar(g, peca(CW, CH, lambda q, i=i: _braco(p, q, i, folga=0.9, ate=manga)))
    if longa:  # punhos
        escurecer(g, lambda x, y: any(math.hypot(x + 0.5 - p.mao[i][0], y + 0.5 - p.mao[i][1] + 2.2) < 1.6
                                      for i in range(2)), 2)
    _livrar_cabeca(g, p)
    return g


def calca(direcao, col):
    p = Pose(direcao, col)
    g = Grade(CW, CH)
    for i in p.ordem():
        colar(g, peca(CW, CH, lambda q, i=i: _perna(p, q, i, folga=0.8, ate=0.94)))
    cx = p.cabeca[0]
    colar(g, peca(CW, CH, lambda q: capsula(q, cx - (1 if p.lado else 3.6), 54.5, cx + (1 if p.lado else 3.6), 54.5,
                                             4.3 if p.lado else 4.0)))
    return g


def saia(direcao, col):
    p = Pose(direcao, col)
    cx = p.cabeca[0]
    meia = 6.0 if p.lado else 7.4
    sa = peca(CW, CH, lambda q: tronco_conico(q, cx, 51.5 + p.b, 62.5, meia, meia + 4))
    for k, x in enumerate(range(cx - 8, cx + 9, 4)):
        for y in range(55 + p.b, 63):
            if sa.get(x, y) not in (T, CONTORNO):
                sa.set(x, y, max(2, sa.get(x, y) - 2))
    return sa


def botinha(direcao, col):
    p = Pose(direcao, col)
    g = Grade(CW, CH)
    for i in p.ordem():
        tx, ty = p.tornozelo[i]
        if p.lado:
            colar(g, peca(CW, CH, lambda q, tx=tx, ty=ty, i=i: (
                capsula(q, tx - 0.5, ty - 1.5, tx, ty + 1, 2.8, ajuste=p.ajuste(i)),
                elipsoide(q, tx + 1.6, ty + 2.6, 4.0, 2.3, ajuste=p.ajuste(i)))))
        else:
            colar(g, peca(CW, CH, lambda q, tx=tx, ty=ty: (
                capsula(q, tx, ty - 1.5, tx, ty + 1, 2.9),
                elipsoide(q, tx, ty + 2.4, 3.4, 2.3))))
    return g


def sombra():
    g = Grade(CW, CH)
    elipsoide(g, 32, 76.5, 12, 3.4, valor=(70, 56, 72, 70))
    return g


# --------------------------------------------------------------------------
# Camadas de cabeça (96 x 112, centro da cabeça em (48, 72))
# --------------------------------------------------------------------------

HX, HY = PONTO_CABECA


def _zigue(x, periodo=6, fase=0):
    """0..1..0 a cada período: pontas de mechas."""
    t = ((x + fase) % periodo) / periodo
    return 1 - abs(t * 2 - 1)


CILIOS = (62, 38, 52, 255)
IRIS_ESC = (112, 70, 62, 255)
IRIS_CLARA = (178, 120, 88, 255)
BRILHO = (255, 255, 255, 255)
BOCA = (184, 98, 98, 255)
BOCHECHA = (240, 140, 150, 120)

OLHO = [
    "KKKK",
    "WWIK",
    "WIII",
    "IIMI",
    "MMMM",
    ".MM.",
]
CORES_OLHO = {"K": CILIOS, "W": BRILHO, "I": IRIS_ESC, "M": IRIS_CLARA}


def _olho(g, x0, y0, espelhar=False, largura=4):
    for dy, linha in enumerate(OLHO):
        linha = linha[:largura] if not espelhar else linha[:largura][::-1]
        for dx, c in enumerate(linha):
            if c != ".":
                g.set(x0 + dx, y0 + dy, CORES_OLHO[c])
    # cílio externo
    g.set(x0 - 1 if not espelhar else x0 + largura, y0, CILIOS)


def rosto(direcao):
    g = Grade(HW, HH)
    if direcao == "baixo":
        _olho(g, HX - 8, HY, espelhar=False)
        _olho(g, HX + 4, HY, espelhar=True)
        g.set(HX - 1, HY + 9, BOCA)
        g.set(HX, HY + 9, BOCA)
        for x in (HX - 10, HX - 9, HX - 8, HX + 7, HX + 8, HX + 9):
            g.set(x, HY + 8, BOCHECHA)
    elif direcao == "lado":
        _olho(g, HX + 5, HY, espelhar=True, largura=3)
        g.set(HX + 9, HY + 9, BOCA)
        for x in (HX + 3, HX + 4, HX + 5):
            g.set(x, HY + 8, BOCHECHA)
    return g


def _textura_cabelo(g, coroa):
    """Mechas: linhas escuras saindo do topo da cabeça e um brilho em arco."""
    cx, cy = coroa
    for x, y, v in list(g.pixels()):
        if not isinstance(v, int) or v == CONTORNO:
            continue
        a = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
        d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
        if (a * 9 / math.pi) % 1 < 0.16 and d > 4:
            g.set(x, y, max(2, v - 2))
        if abs(d - 8.5) < 0.9 and a < -0.5 and a > -2.8 and (x + y) % 3 != 0:
            g.set(x, y, 8)


def cabelo(estilo, direcao, recortado=False, parte="frente"):
    g = Grade(HW, HH)
    if parte == "tras":
        if estilo == "longo" and direcao == "baixo":
            colar(g, peca(HW, HH, lambda q: capsula(q, HX, HY + 2, HX, HY + 27, 15.5, 11, ajuste=-2,
                                                     recorte=lambda x, y: y >= HY - 2 and (y < HY + 26 + 3 * _zigue(x, 5)))))
        return g

    def volume(q):
        if direcao == "baixo":
            def manter(x, y):
                if y <= HY - 5 + 5 * _zigue(x, 6, 1):  # franja
                    return True
                return abs(x + 0.5 - HX) >= 10.5 and y <= HY + 8 + 2 * _zigue(x, 4)
            elipsoide(q, HX, HY - 2.5, 14.2, 13.2, recorte=manter)
            capsula(q, HX - 12.5, HY - 4, HX - 12.8, HY + 8, 2.6, 1.6, recorte=lambda x, y: x < HX - 9)
            capsula(q, HX + 12.5, HY - 4, HX + 12.8, HY + 8, 2.6, 1.6, recorte=lambda x, y: x > HX + 9)
        elif direcao == "cima":
            elipsoide(q, HX, HY - 2, 14.2, 13.6, recorte=lambda x, y: y <= HY + 9 + 3 * _zigue(x, 5))
        else:
            def manter(x, y):
                if x + 0.5 < HX - 4:  # nuca
                    return y <= HY + 9 + 2 * _zigue(y, 4)
                if x + 0.5 < HX - 1:  # costeleta, na frente da orelha
                    return y <= HY + 3
                return y <= HY - 5 + 5 * _zigue(x, 5, 2)  # franja
            elipsoide(q, HX - 1, HY - 2.5, 14.2, 13.2, recorte=manter)

    pecas = [peca(HW, HH, volume, contornar=False)]
    if estilo == "longo":
        if direcao == "baixo":
            for lado in (-1, 1):
                pecas.append(peca(HW, HH, lambda q, s=lado: capsula(q, HX + s * 12.5, HY - 2, HX + s * 13.5, HY + 26, 3.6, 1.3),
                                  contornar=False))
        elif direcao == "cima":
            pecas.append(peca(HW, HH, lambda q: capsula(q, HX, HY + 2, HX, HY + 28, 15.0, 10.5,
                                                         recorte=lambda x, y: y < HY + 27 + 3 * _zigue(x, 5)),
                              contornar=False))
        else:
            pecas.append(peca(HW, HH, lambda q: capsula(q, HX - 9, HY, HX - 10, HY + 27, 7, 3.5), contornar=False))
    g = Grade(HW, HH)
    for pc in pecas:
        colar(g, pc)
    _textura_cabelo(g, (HX - (2 if direcao == "lado" else 0), HY - 14))
    if recortado:
        limpar(g, lambda x, y: y <= HY - 7)
    contorno(g)

    if estilo == "coque" and not recortado:
        bx = HX - 5 if direcao == "lado" else HX
        coque = peca(HW, HH, lambda q: elipsoide(q, bx, HY - 17, 6.8, 6.2))
        _textura_cabelo(coque, (bx, HY - 23))
        contorno(coque)
        if direcao == "cima":
            colar(g, coque)
        else:
            colar(coque, g)
            g = coque
    return g


def _pinta(g, cx, cy, r, cor):
    elipsoide(g, cx, cy, r, r * 0.85, valor=cor)


# Chapéus: cada um devolve (grades por direção, rampas por "material")

def chapeu_gorro(direcao):
    g = Grade(HW, HH)
    gorro = peca(HW, HH, lambda q: elipsoide(q, HX, HY - 5, 15.6, 13.2, recorte=lambda x, y: y <= HY - 4))
    for x, y, v in list(gorro.pixels()):
        if v != CONTORNO and y >= HY - 8:
            gorro.set(x, y, ("faixa", 7 if x % 2 == 0 else 5))
    colar(g, gorro)
    pompom = peca(HW, HH, lambda q: elipsoide(q, HX + (-2 if direcao == "lado" else 0), HY - 20, 5.2, 4.9))
    for x, y, v in list(pompom.pixels()):
        pompom.set(x, y, ("faixa", v))
    colar(g, pompom)
    return g


def chapeu_cogumelo(direcao):
    g = Grade(HW, HH)
    pintas = {
        "baixo": [(HX - 9, HY - 17, 3), (HX + 5, HY - 21, 2.6), (HX + 13, HY - 13, 2.2), (HX - 16, HY - 11, 2),
                  (HX + 1, HY - 12, 2.2)],
        "cima": [(HX - 5, HY - 20, 2.8), (HX + 9, HY - 16, 2.6), (HX - 14, HY - 13, 2.2), (HX + 3, HY - 11, 2)],
        "lado": [(HX - 11, HY - 16, 2.8), (HX + 3, HY - 20, 2.4), (HX + 12, HY - 12, 2.2), (HX - 2, HY - 11, 2)],
    }[direcao]

    def chapeu(q):
        elipsoide(q, HX, HY - 8.5, 21, 15, recorte=lambda x, y: y <= HY - 9)
        for px, py, r in pintas:
            elipsoide(q, px, py, r, r * 0.85, recorte=lambda x, y: q.get(x, y) != T)
    c = peca(HW, HH, chapeu)
    # pintas em creme: repinta os pixels dentro das pintas
    for px, py, r in pintas:
        for x, y, v in list(c.pixels()):
            if v != CONTORNO and math.hypot((x + 0.5 - px) / r, (y + 0.5 - py) / (r * 0.85)) <= 1:
                c.set(x, y, ("creme", min(8, v + 1)))
    aba = peca(HW, HH, lambda q: elipsoide(q, HX, HY - 8.5, 18, 2.6))
    for x, y, v in list(aba.pixels()):
        aba.set(x, y, ("creme", v if v == CONTORNO else (4 if x % 3 == 0 else 6)))
    colar(g, aba)
    colar(g, c)
    return g


def chapeu_broto(direcao):
    g = Grade(HW, HH)
    s = 1 if direcao != "lado" else 0
    colar(g, peca(HW, HH, lambda q: capsula(q, HX, HY - 10, HX + (0 if s else -1), HY - 21, 1.3, 1.1)))
    folhas = [(HX - 6.5, HY - 23, 6.2, 2.9, -28), (HX + 6.5, HY - 25.5, 6.8, 3.1, 24)]
    if direcao == "lado":
        folhas = [(HX - 4, HY - 23, 6.0, 2.6, -40), (HX + 4.5, HY - 25, 6.5, 3.0, 18)]
    for fx, fy, rx, ry, ang in folhas:
        f = peca(HW, HH, lambda q, a=(fx, fy, rx, ry, ang): elipse_girada(q, *a))
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for k in range(-int(rx) + 2, int(rx) - 1):  # nervura
            x, y = int(fx + k * c), int(fy + k * sn)
            if f.get(x, y) not in (T, CONTORNO):
                f.set(x, y, max(2, f.get(x, y) - 2))
        colar(g, f)
    return g


NUVEM_ROSTO = (90, 96, 130, 255)


def chapeu_nuvem(direcao):
    g = Grade(HW, HH)
    dx = 2 if direcao == "lado" else 0

    def nuvem(q):
        for cx, cy, rx, ry in ((HX - 7, HY - 34, 7.5, 6), (HX + 1, HY - 38, 8.6, 7.4), (HX + 9, HY - 33.5, 6.6, 5.4),
                               (HX + 1, HY - 31.5, 10, 5)):
            elipsoide(q, cx, cy, rx, ry, recorte=lambda x, y: y <= HY - 28)
    n = peca(HW, HH, nuvem)
    colar(g, n)
    if direcao != "cima":
        for ox in (-3, 4):
            g.set(HX + ox + dx, HY - 34, NUVEM_ROSTO)
            g.set(HX + ox + dx, HY - 33, NUVEM_ROSTO)
        g.set(HX + dx, HY - 31, NUVEM_ROSTO)
        g.set(HX + 1 + dx, HY - 31, NUVEM_ROSTO)
        for ox in (-6, -5, 7, 8):
            g.set(HX + ox + dx, HY - 32, (246, 168, 184, 255))
    return g


FLORES = [((246, 150, 176), (220, 104, 140)), ((250, 214, 110), (222, 170, 70)),
          ((252, 250, 244), (206, 200, 210)), ((200, 168, 236), (156, 120, 204))]


def chapeu_coroa(direcao):
    g = Grade(HW, HH)
    cx = HX - (1 if direcao == "lado" else 0)
    rx, ry, cy = 15.2, 4.6, HY - 8
    ramo = Grade(HW, HH)
    for k in range(0, 181):
        t = math.radians(k)
        x, y = cx + rx * math.cos(t), cy + ry * math.sin(t)
        ramo.set(int(x), int(y), 4)
    angulos = [10, 38, 66, 90, 114, 142, 170] if direcao != "lado" else [20, 55, 90, 125, 160]
    if direcao == "cima":
        angulos = [18, 50, 90, 130, 162]
    for i, a in enumerate(angulos):
        t = math.radians(a)
        fx, fy = int(cx + rx * math.cos(t)), int(cy + ry * math.sin(t))
        for lx, ly in ((fx - 3, fy + 1), (fx + 3, fy)):
            ramo.set(lx, ly, 5)
    contorno(ramo)
    colar(g, ramo)
    for i, a in enumerate(angulos):
        t = math.radians(a)
        fx, fy = int(cx + rx * math.cos(t)), int(cy + ry * math.sin(t)) - 1
        clara, escura = FLORES[i % len(FLORES)]
        flor = Grade(HW, HH)
        for ox, oy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1)):
            flor.set(fx + ox, fy + oy, (*clara, 255) if oy <= 0 else (*escura, 255))
        flor.set(fx, fy, (250, 210, 90, 255))
        contorno(flor, valor=(126, 70, 90, 255))
        colar(g, flor)
    return g


def chapeu_capuz(direcao):
    g = Grade(HW, HH)
    if direcao == "baixo":
        orelhas = [(HX - 13, HY - 15), (HX + 13, HY - 15)]
        abertura = (HX, HY + 4.5, 11.6, 9.8)
        centro = HX
    elif direcao == "cima":
        orelhas = [(HX - 13, HY - 15), (HX + 13, HY - 15)]
        abertura = None
        centro = HX
    else:
        orelhas = [(HX - 8, HY - 17), (HX + 5, HY - 17.5)]
        abertura = (HX + 9, HY + 4.5, 7.2, 9.8)
        centro = HX - 1
    for i, (ox, oy) in enumerate(orelhas):
        orelha = peca(HW, HH, lambda q, ox=ox, oy=oy, i=i: elipsoide(q, ox, oy, 5.6, 5.4,
                                                                    ajuste=-1 if direcao == "lado" and i == 0 else 0))
        if direcao != "cima" and not (direcao == "lado" and i == 0):
            for x, y, v in list(orelha.pixels()):
                if v != CONTORNO and math.hypot(x + 0.5 - ox, y + 0.5 - oy - 0.5) < 3.0:
                    orelha.set(x, y, ("dentro", 6))
        colar(g, orelha)

    def capuz(q):
        def fora_da_abertura(x, y):
            if abertura is None:
                return True
            ax, ay, arx, ary = abertura
            return ((x + 0.5 - ax) / arx) ** 2 + ((y + 0.5 - ay) / ary) ** 2 > 1
        elipsoide(q, centro, HY - 1, 17, 16, recorte=fora_da_abertura)
        capsula(q, centro - 8, HY + 14, centro + 8, HY + 14, 4.4, recorte=fora_da_abertura, ajuste=-1)
    colar(g, peca(HW, HH, capuz))
    return g


CHAPEUS = {
    "gorro": (chapeu_gorro, {"base": "#e8737a", "faixa": "#f6ead6"}),
    "cogumelo": (chapeu_cogumelo, {"base": "#e2585e", "creme": "#f4e8d2"}),
    "broto": (chapeu_broto, {"base": "#7cc66a"}),
    "nuvem": (chapeu_nuvem, {"base": "#e4ecfa"}),
    "coroa": (chapeu_coroa, {"base": "#6fae62"}),
    "capuz": (chapeu_capuz, {"base": "#c79a70", "dentro": "#f2a8a4"}),
}
