# Renders da conferência das armas realistas (Fase 4.1a; desenho, seção 4.7): lado, cima, frente, 3/4 dos dois lados,
# perto do receptor e a vista aproximada da primeira pessoa (sem as luvas até a 4.1b; a câmera no olho do boneco com o
# FOV do viewmodel — 60 horizontais em 4:3 = 75,2° em 16:9 — e a arma na posição da categoria `rifle`), no modelo alto
# com os materiais de fábrica, em tools/blender/conferencia/<id>/ (fora do git). A sobreposição da silhueta com a foto
# (sobreposicao.png) sai do validar.py.
import os

import bpy

from . import estudio
from .unidades import S


def conferir(ctx, pasta, amostras=160):
    sc = bpy.context.scene
    alto = bpy.data.collections['alto']
    for col in sc.collection.children:
        col.hide_render = col is not alto
    xs = [p[0] for p in ctx['ficha']['contorno']]
    ys = [p[1] for p in ctx['ficha']['contorno']]
    cx, cy = (min(xs) + max(xs)) / 2 * S, (min(ys) + max(ys)) / 2 * S
    comp = (max(xs) - min(xs)) * S
    estudio.montar((cx, 0.0, cy))
    dispositivo = estudio.render(1600, 900, amostras)
    c = (cx, 0.0, cy)
    receptor = (-0.50, 0.0, -0.01)
    olho = (-0.78, 0.114, 0.079)  # 9 u atrás, 4,5 u à esquerda e 3,1 u acima da origem (o pino do gatilho)
    vistas = {
        'lado': estudio.camera('lado', (cx, -1.5, cy), c, orto=comp * 1.04),
        'cima': estudio.camera('cima', (cx, 0.0, cy + 1.5), c, orto=comp * 1.04),
        'frente': estudio.camera('frente', (0.9, 0.0, cy), (0.0, 0.0, cy), orto=0.45),
        'tres_direita': estudio.camera('tres_direita', (cx + 0.27, -0.72, cy + 0.29), c, 50),
        'tres_esquerda': estudio.camera('tres_esquerda', (cx + 0.27, 0.72, cy + 0.29), c, 50),
        'perto': estudio.camera('perto', (receptor[0] + 0.08, -0.24, receptor[2] + 0.07), receptor, 55),
        'primeira_pessoa': estudio.camera('primeira_pessoa', olho, (olho[0] + 1.0, olho[1] - 0.02, olho[2] - 0.03), 23.4),
    }
    arquivos = []
    for nome, cam in vistas.items():
        sc.camera = cam
        sc.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(sc.render.filepath)
    for col in sc.collection.children:
        col.hide_render = False
    return arquivos, dispositivo
