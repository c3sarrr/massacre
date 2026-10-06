# Só o quadro da P90 (o p90_quadro.quadro, com o chanfro local) nos dois níveis: malha fechada, triângulos, cruzamentos
# e o close do buraco do polegar e da abertura da frente com as normais de verdade. Nada vai para o projeto.
# Uso: blender -b --factory-startup -P quadro_teste.py -- <rotulo>
import json
import math
import os
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import chanfro_local as CL  # noqa: E402
from armas import p90_quadro as Q  # noqa: E402
from armas import pecas as P  # noqa: E402
from armas.unidades import S  # noqa: E402

ROT = sys.argv[sys.argv.index('--') + 1]
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'close')
os.makedirs(SAIDA, exist_ok=True)
ficha = json.load(open(r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\p90.json', encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
M = {z: bpy.data.materials.new(z) for z in ("corpo", "guarnicao", "carregador", "detalhes", "interno", "municao", "vidro")}
quadros = {}
for nivel in ('alto', 'jogo'):
    t0 = time.time()
    col = P.iniciar(nivel, nivel)
    P.chanfro_local()
    q = Q.quadro(ficha, M)
    P.finalizar(col)
    quadros[nivel] = q
    bm = CL._malha_avaliada(q)
    abertas = sum(1 for e in bm.edges if not e.is_manifold)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    bm.free()
    col_pares = CL._colisoes(q)
    print(f'{nivel}: {round(time.time() - t0, 1)} s, triângulos {tris}, arestas abertas {abertas}, vértices em cruzamentos {len(col_pares)}', flush=True)

# o close do modelo alto pelos dois buracos, pelo lado esquerdo (+Y)
sc = bpy.context.scene
alvo = quadros['alto']
for o in sc.objects:
    o.hide_render = o is not alvo
cam_d = bpy.data.cameras.new('cam')
cam_d.type = 'ORTHO'
cam = bpy.data.objects.new('cam', cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'SINGLE'
sc.display.shading.single_color = (0.6, 0.6, 0.62)
sc.display.shading.show_specular_highlight = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 1000
for nome, (x, y, larg) in {'oval': (-265.0, -55.0, 120.0), 'abertura': (-145.0, -50.0, 110.0), 'quadro': (-252.0, -30.0, 520.0)}.items():
    cam_d.ortho_scale = larg * S
    cam.location = Vector((x * S, 0.5, y * S))
    cam.rotation_euler = (math.radians(90), 0, math.radians(180))
    sc.render.filepath = os.path.join(SAIDA, f'{ROT}_{nome}.png')
    bpy.ops.render.render(write_still=True)
print('fim', flush=True)
