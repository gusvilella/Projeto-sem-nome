#!/usr/bin/env python3
"""Monta a folha 6 x 3 do jogo a partir de um personagem gerado por IA.

Entradas (já importadas com importar_sprite.py, quadros de 64 x 80):
- parado: 3 quadros com as vistas de frente, lado e costas (a ordem é configurável)
- andar: 4 quadros andando de lado (virado para a direita)

Frente e costas não têm animação própria de andar ainda: usam o quadro parado
com o balanço de corpo (sobe 1 px na passagem), igual ao das camadas.

Uso:
  python3 ferramentas/montar_personagem_ia.py parado.png andar.png saida.png [--ordem frente,lado,costas]
"""

import argparse

from PIL import Image

QW, QH = 64, 80
BALANCO = [0, 1, 0, -1, 0, -1]  # mesmo de ferramentas/arte_personagem.py


def quadros(caminho):
    img = Image.open(caminho).convert("RGBA")
    return [img.crop((i * QW, 0, (i + 1) * QW, QH)) for i in range(img.width // QW)]


def deslocado(q, dy):
    saida = Image.new("RGBA", (QW, QH), (0, 0, 0, 0))
    saida.alpha_composite(q, (0, dy))
    return saida


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("parado")
    p.add_argument("andar")
    p.add_argument("saida")
    p.add_argument("--ordem", default="frente,lado,costas", help="ordem das vistas na imagem parada")
    a = p.parse_args()

    vistas = dict(zip(a.ordem.split(","), quadros(a.parado)))
    andar = quadros(a.andar)
    folha = Image.new("RGBA", (QW * 6, QH * 3), (0, 0, 0, 0))
    for linha, vista in enumerate(("frente", "costas", "lado")):
        for coluna in range(6):
            if vista == "lado" and coluna >= 2:
                q = andar[(coluna - 2) % len(andar)]
            else:
                q = deslocado(vistas[vista], BALANCO[coluna])
            folha.alpha_composite(q, (coluna * QW, linha * QH))
    folha.save(a.saida)
    print(f"folha 6 x 3 salva em {a.saida}")


if __name__ == "__main__":
    main()
