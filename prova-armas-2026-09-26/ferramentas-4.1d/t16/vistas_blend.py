"""Vistas de perto de uma .blend do protótipo do chanfro (chanfro_v2.py --despejo): só a coleção `perto` (as peças
juntadas como o construir junta), no Workbench (a luz de estúdio, a cavidade, a sombra e o brilho), para comparar os
chanfros. As vistas em mm da arma (o referencial do Blender: +Y é a esquerda): o ponto olhado, a direção de onde a
câmera olha e a largura do quadro (ortográfica).
    blender -b --factory-startup -P vistas_blend.py -- <.blend> <vistas.json> <pasta de saída> <rótulo>
vistas.json: [{"nome": "coronha_frente", "alvo": [x, y, z], "de": [dx, dy, dz], "largura": mm}, ...]
"""
import json
import os
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
BLEND, VISTAS, SAIDA, ROTULO = a[0], json.load(open(a[1], encoding='utf-8')), a[2], a[3]
S = 0.001
os.makedirs(SAIDA, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BLEND)
cena = bpy.context.scene
perto = bpy.data.collections['perto']
for ob in cena.objects:
    ob.hide_render = ob.name not in perto.objects
cena.render.engine = 'BLENDER_WORKBENCH'
cena.display.shading.light = 'STUDIO'
cena.display.shading.color_type = 'SINGLE'
cena.display.shading.single_color = (0.55, 0.57, 0.6)
cena.display.shading.show_cavity = True
cena.display.shading.cavity_type = 'BOTH'
cena.display.shading.show_shadows = False
cena.display.shading.show_specular_highlight = True
cena.render.resolution_x = 1000
cena.render.resolution_y = 650
cena.render.film_transparent = False
cena.world = bpy.data.worlds.new('fundo')
cena.world.color = (0.16, 0.16, 0.18)
cam_dados = bpy.data.cameras.new('camera')
cam_dados.type = 'ORTHO'
cam = bpy.data.objects.new('camera', cam_dados)
cena.collection.objects.link(cam)
cena.camera = cam
for v in VISTAS:
    alvo = Vector(v['alvo']) * S
    de = Vector(v['de']).normalized()
    cam.location = alvo + de * 2.0
    cam.rotation_euler = (-de).to_track_quat('-Z', 'Z').to_euler()
    cam_dados.ortho_scale = v['largura'] * S
    cam_dados.clip_start = 0.001
    cam_dados.clip_end = 10.0
    cena.render.filepath = os.path.join(SAIDA, f"{v['nome']}_{ROTULO}.png")
    bpy.ops.render.render(write_still=True)
    print('VISTA', v['nome'], ROTULO, flush=True)
print('FIM', flush=True)
