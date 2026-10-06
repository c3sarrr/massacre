# A folha da P1 de cada arma: o lado, os três quartos da esquerda, a pose do ícone do CS2 e o perto, numa imagem só
# (as renders da conferência; nada do jogo). Uso: blender -b --factory-startup -P folha_p1.py -- <arma> <lado>
import os
import sys

import bpy
import numpy as np

ARMA, LADO = sys.argv[sys.argv.index('--') + 1:][:2]
PASTA = os.path.join(r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\conferencia', ARMA)
ALTURA = 675


def carregar(nome):
    img = bpy.data.images.load(os.path.join(PASTA, nome + '.png'))
    w, h = img.size
    img.scale(int(round(w * ALTURA / h)), ALTURA)
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[::-1, :, :3]  # linhas de cima para baixo


linhas = [[carregar(LADO), carregar('tres_esquerda')], [carregar('icone'), carregar('perto_esquerda')]]
largura = max(sum(i.shape[1] for i in linha) + 8 * (len(linha) - 1) for linha in linhas)
folha = np.full((ALTURA * 2 + 8, largura, 3), 0.12, np.float32)
for r, linha in enumerate(linhas):
    x = 0
    for img in linha:
        folha[r * (ALTURA + 8):r * (ALTURA + 8) + ALTURA, x:x + img.shape[1]] = img
        x += img.shape[1] + 8
saida = bpy.data.images.new('folha', largura, folha.shape[0], alpha=True)
rgba = np.concatenate([folha, np.ones(folha.shape[:2] + (1,), np.float32)], axis=2)[::-1]
saida.pixels.foreach_set(rgba.ravel())
saida.filepath_raw = os.path.join(PASTA, 'folha_p1.png')
saida.file_format = 'PNG'
saida.save()
print('folha', saida.filepath_raw, largura, folha.shape[0], flush=True)
