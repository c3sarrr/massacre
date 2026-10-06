"""O antes e o depois de uma arma (Tarefa 16, correção C4: o chanfro local nas da 4.1c): os dois .glb importados,
cada um sozinho, e as mesmas vistas renderizadas no Workbench (a luz de estúdio, a cavidade e a sombra, a cor de cada
material), para comparar a forma dos chanfros; só o nível perto (o grupo `perto` do .glb). As vistas são dadas em mm
da arma (o referencial do Blender: +Y é a esquerda): o ponto olhado, a direção de onde a câmera olha e a largura do
quadro (ortográfica); o .glb está em u (25,4 mm) com a origem no pino do gatilho (`origemMM` do relatório).
    blender -b --factory-startup -P antes_depois.py -- <antes.glb> <depois.glb> <pasta de saída> <vistas.json>
        <origem x> <origem y>
vistas.json: [{"nome": "receptor_canto", "alvo": [x, y, z], "de": [dx, dy, dz], "largura": mm}, ...]
"""
import json
import os
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
ANTES, DEPOIS, SAIDA, VISTAS = a[0], a[1], a[2], json.load(open(a[3], encoding='utf-8'))
ORIGEM = Vector((float(a[4]), 0.0, float(a[5])))
MM_POR_U = 25.4
os.makedirs(SAIDA, exist_ok=True)


def limpar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cena = bpy.context.scene
    cena.render.engine = 'BLENDER_WORKBENCH'
    cena.display.shading.light = 'STUDIO'
    cena.display.shading.color_type = 'MATERIAL'
    cena.display.shading.show_cavity = True
    cena.display.shading.cavity_type = 'BOTH'
    cena.display.shading.show_shadows = True
    cena.display.shading.show_specular_highlight = True
    cena.render.resolution_x = 900
    cena.render.resolution_y = 600
    cena.render.film_transparent = False
    cena.world = bpy.data.worlds.new('fundo')
    cena.world.color = (0.18, 0.18, 0.2)
    return cena


def renderizar(glb, rotulo):
    cena = limpar()
    bpy.ops.import_scene.gltf(filepath=glb)
    # só o nível perto: as malhas debaixo dos grupos `mundo` e `longe` ficam fora
    for ob in list(cena.objects):
        pai = ob.parent
        while pai is not None:
            if pai.name.split('.')[0] in ('mundo', 'longe'):
                ob.hide_render = True
                break
            pai = pai.parent
    cam_dados = bpy.data.cameras.new('camera')
    cam_dados.type = 'ORTHO'
    cam = bpy.data.objects.new('camera', cam_dados)
    cena.collection.objects.link(cam)
    cena.camera = cam
    # o glTF é Y para cima e o importador põe Z para cima: a arma volta ao referencial do Blender, em u
    for v in VISTAS:
        alvo = (Vector(v['alvo']) - ORIGEM) / MM_POR_U
        de = Vector(v['de']).normalized()
        cam.location = alvo + de * 80.0
        frente = -de
        cam.rotation_euler = frente.to_track_quat('-Z', 'Z').to_euler()
        cam_dados.ortho_scale = v['largura'] / MM_POR_U
        cam_dados.clip_start = 0.01
        cam_dados.clip_end = 400.0
        cena.render.filepath = os.path.join(SAIDA, f"{v['nome']}_{rotulo}.png")
        bpy.ops.render.render(write_still=True)
        print('VISTA', v['nome'], rotulo, flush=True)


renderizar(ANTES, 'antes')
renderizar(DEPOIS, 'depois')
print('FIM', len(VISTAS), 'vistas', flush=True)
