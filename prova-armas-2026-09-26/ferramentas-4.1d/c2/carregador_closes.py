# Os closes do carregador da AWP para a revisão da C2 (nada do jogo: só o nosso modelo alto, da .blend que o construir
# grava). Na arma: de lado (a esquerda, o lado da primeira pessoa) e por baixo (a frente escondida rente à coronha, o
# vão do retém); só o carregador: de lado (os cartuchos pelas fendas), de cima (os lábios e o de cima entre eles), de
# três quartos por baixo (a frente escondida, a placa de fundo) e o lado direito.
#   S:\blender.exe -b <trabalho-4.1d>\tools\blender\conferencia\awp\awp.blend --factory-startup -P carregador_closes.py [-- <vista> ...]
# (só as vistas pedidas; as de baixo com uma luz de área por baixo)
import os
import sys

import bpy
from mathutils import Vector

RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))
from armas import estudio  # noqa: E402

PASTA = os.path.join(RAIZ, 'tools', 'blender', 'conferencia', 'awp')
sc = bpy.context.scene
alto = bpy.data.collections['alto']
for col in sc.collection.children:
    col.hide_render = col is not alto
pecas = {}
for ob in alto.all_objects:
    if ob.type == 'MESH' and not ob.get('cortador') and not ob.hide_render:
        pecas.setdefault(ob.get('peca', '?'), []).append(ob)
print('peças no alto:', {k: len(v) for k, v in pecas.items()}, flush=True)
carregador = pecas.get('carregador', [])
assert carregador, 'o carregador no alto'
outros = [ob for k, v in pecas.items() if k != 'carregador' for ob in v]

CENTRO = (-0.785, 0.0, -0.055)
fundo = estudio.montar(CENTRO)
estudio.render(1600, 900, 192)
# a luz de baixo só nas vistas de baixo (o estúdio ilumina de cima: por baixo a coronha e o carregador ficavam pretos)
d = bpy.data.lights.new('baixo', 'AREA')
d.size, d.energy, d.color = 0.9, 26, (1.0, 0.97, 0.92)
luz_baixo = bpy.data.objects.new('baixo', d)
sc.collection.objects.link(luz_baixo)
luz_baixo.location = (CENTRO[0] + 0.12, 0.18, CENTRO[2] - 0.45)
luz_baixo.rotation_euler = (Vector(CENTRO) - luz_baixo.location).to_track_quat('-Z', 'Y').to_euler()
SO = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
VISTAS = [
    # nome, só o carregador?, sem o chão?, posição, alvo, lente
    ('c2_lado_dentro', False, False, (-0.79, 0.34, -0.055), (-0.79, 0.0, -0.07), 70),
    ('c2_baixo_dentro', False, True, (-0.64, 0.19, -0.31), (-0.79, 0.0, -0.07), 45),
    ('c2_baixo_reto', False, True, (-0.78, 0.0, -0.42), (-0.78, 0.0, -0.07), 55),
    ('c2_so_lado', True, False, (-0.79, 0.30, -0.05), (-0.785, 0.0, -0.055), 60),
    ('c2_so_direita', True, False, (-0.79, -0.30, -0.05), (-0.785, 0.0, -0.055), 60),
    ('c2_so_cima', True, False, (-0.69, 0.10, 0.11), (-0.79, 0.0, -0.025), 60),
    ('c2_so_cima_perto', True, False, (-0.76, 0.05, 0.05), (-0.80, 0.0, -0.015), 70),
    ('c2_so_tres_baixo', True, True, (-0.63, 0.21, -0.20), (-0.785, 0.0, -0.055), 50),
]
for nome, so, sem_chao, pos, alvo, lente in VISTAS:
    if SO and nome not in SO:
        continue
    luz_baixo.hide_render = not sem_chao
    for ob in outros:
        ob.hide_render = so
    fundo.hide_render = sem_chao
    sc.camera = estudio.camera(nome, pos, alvo, lente)
    sc.render.filepath = os.path.join(PASTA, nome + '.png')
    bpy.ops.render.render(write_still=True)
    print('render', sc.render.filepath, flush=True)
