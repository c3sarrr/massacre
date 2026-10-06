"""As faces da `base` do perto em volta de um ponto (mm da arma) na .blend da conferência, e de que peça do nível de
jogo elas vêm: para cada peça da base com face a até RAIO mm do ponto, as faces dela ali (a normal, o meio) e se a
junção (soquetes.remover_escondidas) as tira por estarem dentro de outra peça da base — e de qual.
    blender -b --factory-startup -P diag_escondidas.py -- <arma> <x> <y> <z> [raio]
"""
import json
import os
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from armas import canonica, soquetes  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA = a[0]
PONTO = Vector([float(c) for c in a[1:4]])
RAIO = float(a[4]) if len(a) > 4 else 2.0
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', ARMA, f'{ARMA}.blend'))
print('COLECOES', json.dumps({c.name: len(c.objects) for c in bpy.data.collections}, ensure_ascii=False), flush=True)


def faces_perto(ob, me=None):
    """As faces (mm do mundo / S) a até RAIO do ponto: índice, meio, normal, área."""
    me = me or ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    vs = [v.co / S for v in bm.verts]
    polys = [[v.index for v in f.verts] for f in bm.faces]
    bvh = BVHTree.FromPolygons(vs, polys)
    saida = {}
    for co, n, i, d in bvh.find_nearest_range(PONTO, RAIO):
        if i in saida:
            continue
        f = bm.faces[i]
        saida[i] = {'face': i, 'dist': round(d, 3), 'normal': [round(c, 3) for c in n],
                    'meio': [round(c, 2) for c in f.calc_center_median() / S],
                    'areaMM2': round(f.calc_area() / S / S, 4)}
    bm.free()
    return sorted(saida.values(), key=lambda s: s['dist'])


perto = bpy.data.objects.get('perto_base')
print('PERTO_BASE', json.dumps(faces_perto(perto)[:12], ensure_ascii=False), flush=True)
# as peças da base no nível de jogo, como a junção as vê (as cópias avaliadas na forma canônica)
jogo = bpy.data.collections.get('jogo')
base = [o for o in jogo.objects if o.type == 'MESH' and not o.get('cortador') and not o.hide_render
        and o.get('peca', 'base') == 'base'] if jogo else []
print('JOGO_BASE', len(base), flush=True)
copias = {}
for ob in base:
    me = canonica.avaliada(ob)
    c = bpy.data.objects.new(f'diag.{ob.name}', me)
    c.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(c)
    copias[ob.name] = c
dg = bpy.context.evaluated_depsgraph_get()
arvores = {n: BVHTree.FromObject(c, dg, deform=False) for n, c in copias.items()}
for nome, c in copias.items():
    fs = faces_perto(c)
    if not fs:
        continue
    bm = bmesh.new()
    bm.from_mesh(c.data)
    bm.faces.ensure_lookup_table()
    for s in fs:
        f = bm.faces[s['face']]
        pontos = [c.matrix_world @ f.calc_center_median()] + [c.matrix_world @ v.co for v in f.verts]
        s['escondidaPor'] = [o for o, oc in copias.items() if oc is not c and soquetes._escondida(
            arvores[o], [oc.matrix_world.inverted() @ q for q in pontos], 0.02 * S)]
    bm.free()
    print('PECA', nome, json.dumps(fs[:10], ensure_ascii=False), flush=True)
