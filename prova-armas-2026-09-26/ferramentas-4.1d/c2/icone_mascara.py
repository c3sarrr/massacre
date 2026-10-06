# A máscara da AWP na pose do ícone do CS2 (a câmera ICONE do conferir.py, o mesmo quadro de 1600 x 1200 do render
# `icone`): o modelo alto da .blend que o construir grava, em Workbench chapado, sem luz, com o fundo transparente — o
# carregador em vermelho e o resto em branco. Só o nosso modelo: as bordas dela são comparadas, em números, com as do
# ícone lidas no navegador (grade.html, `__bordas`), sem gravar nada do jogo.
#   S:\blender.exe -b <trabalho-4.1d>\tools\blender\conferencia\awp\awp.blend --factory-startup -P icone_mascara.py
import json
import os
import sys

import bpy
from mathutils import Vector

RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
sys.path.insert(0, os.path.join(RAIZ, 'tools', 'blender'))
from armas import awp, conferir, estudio  # noqa: E402
from armas.unidades import S  # noqa: E402

PASTA = os.path.join(RAIZ, 'tools', 'blender', 'conferencia', 'awp')
ficha = json.load(open(os.path.join(RAIZ, 'tools', 'blender', 'refs', 'awp.json'), encoding='utf-8'))
sc = bpy.context.scene
alto = bpy.data.collections['alto']
for col in sc.collection.children:
    col.hide_render = col is not alto
for ob in alto.all_objects:
    if ob.type != 'MESH' or ob.get('cortador') or ob.hide_render:
        continue
    ob.color = (1.0, 0.0, 0.0, 1.0) if ob.get('peca') == 'carregador' else (1.0, 1.0, 1.0, 1.0)

# a câmera do ícone, como em conferir.vistas_da_arma
xs = [p[0] for p in ficha['contorno']]
ys = [p[1] for p in ficha['contorno']]
c = Vector(((min(xs) + max(xs)) / 2 * S, 0.0, (min(ys) + max(ys)) / 2 * S))
ic = getattr(awp, 'ICONE', conferir.ICONE)
ki = (max(xs) - min(xs)) * S / ic['comprimento']
mira = c + Vector(ic['mira']) * ki
pos = mira - Vector(ic['frente']) * ic['distancia'] * ki
sc.camera = estudio.camera('icone_mascara', tuple(pos), tuple(mira), ic['lente'], None, ic['cima'])

sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'FLAT'
sh.color_type = 'OBJECT'
sh.show_shadows = False
sh.show_cavity = False
sh.show_object_outline = False
sh.show_specular_highlight = False
sc.display_settings.display_device = 'sRGB'
sc.view_settings.view_transform = 'Standard'
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = ic['quadro']
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.render.filepath = os.path.join(PASTA, 'c2_icone_mascara.png')
bpy.ops.render.render(write_still=True)
print('render', sc.render.filepath, flush=True)
