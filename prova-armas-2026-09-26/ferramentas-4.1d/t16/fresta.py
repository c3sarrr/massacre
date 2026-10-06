"""Os pares de polígonos vizinhos quase opostos de uma peça (na .blend da conferência, a cópia avaliada na forma
canônica, como a junção a vê), a até RAIO mm de um ponto: o ângulo entre as normais (de 180°), e de que lado de cada
um fica o outro — a "fresta" (as duas faces voltadas uma para a outra: o vértice de longe de cada uma na frente da
outra, uma dobra) ou a "cunha" (material entre elas: atrás) —, as normais e os cantos (até oito).
    blender -b --factory-startup -P fresta.py -- <arma> <peça> <x> <y> <z> [raio] [cosseno máximo]
"""
import json
import math
import os
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import canonica  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, PECA = a[0], a[1]
PONTO = Vector([float(c) for c in a[2:5]])
RAIO = float(a[5]) if len(a) > 5 else 1.0
COS = float(a[6]) if len(a) > 6 else -0.99
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', ARMA, f'{ARMA}.blend'))
ob = bpy.data.objects[PECA]
me = canonica.avaliada(ob)
bm = bmesh.new()
bm.from_mesh(me)
bpy.data.meshes.remove(me)
bm.transform(ob.matrix_world)
bm.normal_update()


def longe(f, e):
    """A distância (mm, com sinal pela normal de `g`) do vértice de `f` mais longe da aresta `e`."""
    a, b = e.verts[0].co, e.verts[1].co
    ab = b - a
    melhor, vm = -1.0, None
    for v in f.verts:
        if v in e.verts:
            continue
        t = (v.co - a).dot(ab) / ab.length_squared if ab.length_squared else 0.0
        d = (v.co - (a + ab * t)).length
        if d > melhor:
            melhor, vm = d, v
    return vm


saida = []
for e in bm.edges:
    if len(e.link_faces) != 2:
        continue
    m = (e.verts[0].co + e.verts[1].co) / 2
    if (m / S - PONTO).length > RAIO:
        continue
    f, g = e.link_faces
    c = f.normal.dot(g.normal)
    if c > COS:
        continue
    vf, vg = longe(f, e), longe(g, e)
    lado_g = f.normal.dot(vg.co - m) / S if vg else None  # o vértice de longe de g na frente de f (>0) ou atrás
    lado_f = g.normal.dot(vf.co - m) / S if vf else None
    saida.append({'aresta': [[round(x / S, 3) for x in v.co] for v in e.verts], 'graus': round(180 - math.degrees(
        math.acos(max(-1.0, min(1.0, c)))), 3), 'cos': round(c, 5), 'ladoDeG': round(lado_g, 5),
        'ladoDeF': round(lado_f, 5), 'areas': [round(x.calc_area() / S / S, 5) for x in (f, g)],
        'tipo': 'fresta' if lado_g > 0 and lado_f > 0 else ('cunha' if lado_g < 0 and lado_f < 0 else 'misto'),
        'normais': [[round(c, 4) for c in x.normal] for x in (f, g)],
        'cantos': [[[round(c / S, 2) for c in v.co] for v in x.verts] if len(x.verts) <= 8 else len(x.verts)
                   for x in (f, g)]})
bm.free()
print('FRESTA', json.dumps(saida, ensure_ascii=False), flush=True)
