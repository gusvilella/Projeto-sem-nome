#!/usr/bin/env python3
"""Gera a arte provisória (placeholder) no estilo Ragnarok em tons pastel.

Tudo aqui é desenhado por código para testar o pipeline com as medidas e os
formatos definitivos. A arte final deve ser desenhada à mão seguindo os mesmos
formatos (ver docs/arte/briefing-artista.md).

Também gera os dados que dependem da arte:
- data/personagem/paletas.json (rampas de 8 tons a partir das cores-base abaixo)
- data/personagem/ancoras.json (posição da cabeça em cada quadro)
- data/regioes/casa.json (posição dos objetos e camadas da cena)

Uso: pip install pillow && python3 ferramentas/gerar_arte.py
"""

import json
import shutil
from pathlib import Path

from PIL import Image

import arte_cenario as C
import arte_personagem as P
from arte_base import folha, imagem, pintar, rampa, rgb_hex

RAIZ = Path(__file__).resolve().parent.parent
JOGO = RAIZ / "jogo"
ARTE = JOGO / "arte"

CORES_BASE = {
    "pele": [("Pele 1", "#fde2cc"), ("Pele 2", "#f6caa8"), ("Pele 3", "#e8ad86"),
             ("Pele 4", "#c98a62"), ("Pele 5", "#a0663f"), ("Pele 6", "#7a4e34")],
    "cabelo": [("Preto", "#5a5266"), ("Castanho escuro", "#7a5440"), ("Castanho", "#a87650"),
               ("Ruivo", "#d8744a"), ("Loiro", "#f0cc78"), ("Branco", "#e6e2ea"), ("Rosa", "#f09ab8"),
               ("Azul", "#7aa4e0"), ("Verde", "#7cc49a"), ("Roxo", "#a888d4")],
    "roupa": [("Coral", "#ec8f86"), ("Azul", "#7e94d0"), ("Verde", "#88c08a"), ("Amarelo", "#f0cc6a"),
              ("Roxo", "#b49ad4"), ("Cinza", "#a8a6b2"), ("Branco", "#f0ece8"), ("Preto", "#5a5664")],
}
CALCADO = "#9a6a4a"
MARCOS = [
    (25, "flores", "Flores brotam no jardim"),
    (50, "fumaca", "A chaminé volta a soltar fumaça"),
    (75, "luz", "As janelas e os postes se acendem"),
    (100, "borboletas", "Borboletas, folhas e luz dourada"),
]


def salvar(img, caminho):
    destino = ARTE / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino)
    print(f"  arte/{caminho}  {img.width}x{img.height}")


def salvar_json(dados, caminho):
    destino = JOGO / "data" / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
    print(f"  data/{caminho}")


def folha_corpo(desenhar, paleta=None):
    return folha([[desenhar(d, c) for c in range(P.COLUNAS)] for d in P.DIRECOES], paleta)


def gerar_personagem():
    print("Personagem — corpo (6 x 3 quadros de 64 x 80):")
    salvar(folha_corpo(P.corpo), "personagem/corpo/base.png")
    salvar(imagem(P.sombra()), "personagem/corpo/sombra.png")
    for estilo in ("camiseta", "moletom", "tunica"):
        salvar(folha_corpo(lambda d, c, e=estilo: P.camiseta(d, c, e)), f"personagem/roupa_cima/{estilo}.png")
    salvar(folha_corpo(P.calca), "personagem/roupa_baixo/calca.png")
    salvar(folha_corpo(P.saia), "personagem/roupa_baixo/saia.png")
    salvar(folha_corpo(P.botinha, rampa(CALCADO, 0.9)), "personagem/calcado/botinha.png")

    print("Personagem — cabeça (quadros de 96 x 112):")
    salvar(folha([[P.rosto(d) for d in P.DIRECOES]]), "personagem/rosto/padrao.png")
    for estilo in ("curto", "longo", "coque"):
        linhas = [[P.cabelo(estilo, d, recortado=r) for d in P.DIRECOES] for r in (False, True)]
        salvar(folha(linhas), f"personagem/cabelo/{estilo}_frente.png")
    salvar(folha([[P.cabelo("longo", d, parte="tras") for d in P.DIRECOES]]), "personagem/cabelo/longo_tras.png")
    for nome, (desenhar, cores) in P.CHAPEUS.items():
        rampas = {k: rampa(v) for k, v in cores.items()}
        salvar(folha([[pintar(desenhar(d), rampas) for d in P.DIRECOES]]), f"personagem/chapeu/{nome}.png")


def gerar_cenario():
    print("Cenário — Casa (540 x 1200):")
    salvar(C.gerar_fundo(), "cenario/casa/fundo.png")
    salvar(C.gerar_flores_marco(), "cenario/casa/flores.png")
    salvar(C.gerar_caminhavel(), "cenario/casa/caminhavel.png")
    salvar(imagem(C.gerar_casa()), "cenario/casa/casa.png")
    salvar(C.gerar_casa_flores(), "cenario/casa/casa_flores.png")
    salvar(C.gerar_casa_luz(), "cenario/casa/casa_luz.png")
    salvar(imagem(C.gerar_arvore()), "cenario/casa/arvore.png")
    salvar(imagem(C.gerar_poste()), "cenario/casa/poste.png")
    salvar(C.gerar_poste_luz(), "cenario/casa/poste_luz.png")
    salvar(imagem(C.gerar_poco()), "cenario/casa/poco.png")
    salvar(imagem(C.gerar_banco()), "cenario/casa/banco.png")
    salvar(imagem(C.gerar_fumaca()), "cenario/comum/fumaca.png")
    salvar(C.gerar_borboleta(), "cenario/comum/borboleta.png")
    salvar(C.gerar_folha(), "cenario/comum/folha.png")


def gerar_dados():
    print("Dados:")
    paletas = {"descricao": (
        "Gerado por ferramentas/gerar_arte.py a partir de cores-base (edite lá). Cada paleta tem 8 tons, "
        "do contorno à luz, que substituem os cinzas 28, 56, 84, 112, 140, 168, 196 e 224 dos sprites "
        "recoloríveis (shaders/troca_paleta.gdshader).")}
    for grupo, lista in CORES_BASE.items():
        paletas[grupo] = [{"id": f"{grupo}_{i + 1}", "nome": nome, "base": base,
                           "cores": [rgb_hex(c) for c in rampa(base)]} for i, (nome, base) in enumerate(lista)]
    salvar_json(paletas, "personagem/paletas.json")

    salvar_json({
        "descricao": ("Gerado por ferramentas/gerar_arte.py. Posição (x, y) do centro da cabeça em cada quadro "
                      "do corpo, por direção e coluna. As camadas de cabeça (quadro 96 x 112) são desenhadas "
                      "com o centro da cabeça em 'ponto_cabeca' e posicionadas por estas âncoras."),
        "quadro_corpo": [P.CW, P.CH],
        "pes": list(P.PES),
        "quadro_cabeca": [P.HW, P.HH],
        "ponto_cabeca": list(P.PONTO_CABECA),
        "colunas": {"parado": [0, 1], "andar": [2, 3, 4, 5]},
        "cabeca": {d: [P.ancora(d, c) for c in range(P.COLUNAS)] for d in P.DIRECOES},
    }, "personagem/ancoras.json")

    cena = C.dados_da_cena()
    marcos = []
    for vida, elemento, descricao in MARCOS:
        marco = {"vida": vida, "elemento": elemento, "descricao": descricao}
        if elemento in ("flores", "luz"):
            marco["camadas"] = cena["marcos"][elemento]
        if elemento == "borboletas":
            marco["borboletas"] = cena["marcos"]["borboletas"]
        marcos.append(marco)
    del cena["marcos"]
    salvar_json({
        "descricao": "Gerado por ferramentas/gerar_arte.py (posições dos objetos vêm da arte).",
        "id": "casa",
        "nome": "Casa",
        "area": "Corpo e higiene",
        "cena": cena,
        "marcos": marcos,
    }, "regioes/casa.json")


def gerar_icone():
    tom_pele = rampa(CORES_BASE["pele"][1][1])
    tom_cabelo = rampa(CORES_BASE["cabelo"][2][1])
    img = Image.new("RGBA", (P.HW, P.HH + 40), (0, 0, 0, 0))
    ax, ay = P.ancora("baixo", 0)
    bx, by = P.PONTO_CABECA[0] - ax, P.PONTO_CABECA[1] - ay
    img.alpha_composite(imagem(P.corpo("baixo", 0), tom_pele), (bx, by))
    img.alpha_composite(imagem(P.camiseta("baixo", 0, "moletom"), rampa(CORES_BASE["roupa"][2][1])), (bx, by))
    img.alpha_composite(imagem(P.rosto("baixo")))
    img.alpha_composite(imagem(P.cabelo("curto", "baixo", recortado=True), tom_cabelo))
    nome, cores = "cogumelo", P.CHAPEUS["cogumelo"][1]
    img.alpha_composite(imagem(pintar(P.CHAPEUS[nome][0]("baixo"), {k: rampa(v) for k, v in cores.items()})))
    recorte = img.crop((14, 40, 82, 108))
    fundo = Image.new("RGBA", recorte.size, (250, 236, 206, 255))
    fundo.alpha_composite(recorte)
    fundo.resize((192, 192), Image.NEAREST).save(JOGO / "icon.png")
    print("  icon.png")


def main():
    if ARTE.exists():
        shutil.rmtree(ARTE)
    gerar_personagem()
    gerar_cenario()
    gerar_dados()
    gerar_icone()


if __name__ == "__main__":
    main()
