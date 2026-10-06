"""As arestas abertas (sem duas faces) de uma peça do nível de jogo na .blend da conferência (a cópia avaliada na
forma canônica, como a validação e a junção a veem): onde ficam e os polígonos em volta delas (os vértices e a normal).
    blender -b --factory-startup -P abertas_peca.py -- <arma> <peça>
"""
import json
import os
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, PECA = a[0], a[1]
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', ARMA, f'{ARMA}.blend'))


def r(v, k=3):
    return [round(c, k) for c in v]


ob = bpy.data.objects[PECA]
print('PILHA', [(m.name, m.type, m.show_viewport) for m in ob.modifiers], flush=True)
me = canonica.avaliada(ob)
bm = bmesh.new()
bm.from_mesh(me)
bm.transform(ob.matrix_world)
bm.normal_update()
abertas = [e for e in bm.edges if len(e.link_faces) != 2]
saida = []
for e in abertas:
    faces = []
    for f in e.link_faces:
        faces.append({'normal': r(f.normal), 'vertices': [r(v.co / S) for v in f.verts][:12], 'n': len(f.verts),
                      'areaMM2': round(f.calc_area() / S / S, 5)})
    saida.append({'de': r(e.verts[0].co / S), 'a': r(e.verts[1].co / S), 'mm': round(e.calc_length() / S, 5),
                  'faces': faces})
print('ABERTAS', len(abertas), json.dumps(saida, ensure_ascii=False), flush=True)
bm.free()
