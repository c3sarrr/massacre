import os
import bpy
from mathutils import Vector
import pega_banco as B


def vistas_arma(nome, centro_mm, vistas):
    """Renders da arma sozinha (o perto, cinza) em volta de `centro_mm` (x, y, z da arma): {vista: (posição relativa em
    m, lente)}."""
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'OBJECT'
    sc.display.shading.show_cavity = True
    sc.render.resolution_x, sc.render.resolution_y = 960, 720
    col = B.colecao('maos_da_prova')
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in bpy.context.scene.collection.children:
        c.hide_render = c.name not in ('perto',)
    for k, o in B.C['perto'].items():
        o.color = (0.55, 0.57, 0.6, 1.0) if k not in ('gatilho', 'seletor') else (0.15, 0.15, 0.17, 1.0)
        o.hide_render = False
    c = Vector(centro_mm) * 0.001
    for vista, (pos, lente) in vistas.items():
        cam = bpy.data.objects.get(f'cam_{vista}')
        if cam is None:
            cam = bpy.data.objects.new(f'cam_{vista}', bpy.data.cameras.new(f'cam_{vista}'))
            sc.collection.objects.link(cam)
        p = c + Vector(pos)
        cam.location = p
        cam.rotation_euler = (c - p).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lente
        cam.data.clip_start = 0.002
        sc.camera = cam
        sc.render.filepath = os.path.join(B.CFG['renders'], f'{nome}_{vista}.png')
        bpy.ops.render.render(write_still=True)
    print('VISTAS', nome, list(vistas))
