"""Os polígonos de uma peça do nível de jogo (a cópia avaliada na forma canônica, como a junção usa) a até RAIO mm de um
ponto, na .blend da conferência: os vértices de cada um, a normal (Newell), a planaridade (o maior afastamento do plano)
e a triangulação BEAUTY dele (a do modificador da junção), com a normal de cada triângulo e se ela vira contra a do
polígono; e os triângulos da `perto_base` ali.
    blender -b --factory-startup -P poligonos_canto.py -- <arma> <peça do jogo> <x> <y> <z> [raio]
"""
import json
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
RAIO = float(a[5]) if len(a) > 5 else 2.0
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', ARMA, f'{ARMA}.blend'))


def r(v, k=3):
    return [round(c, k) for c in v]


def descrever(bm, mw, so_perto=True):
    bm.transform(mw)
    bm.normal_update()
    saida = []
    for f in bm.faces:
        cs = [v.co / S for v in f.verts]
        if so_perto and min((c - PONTO).length for c in cs) > RAIO:
            continue
        n = f.normal
        centro = f.calc_center_median() / S
        plano = max(abs((c - centro).dot(n)) for c in cs)
        saida.append({'face': f.index, 'vertices': [r(c, 3) for c in cs], 'normal': r(n), 'planaridadeMM': round(plano, 5),
                      'areaMM2': round(f.calc_area() / S / S, 5)})
    return saida


ob = bpy.data.objects[PECA]
me = canonica.avaliada(ob)
bm = bmesh.new()
bm.from_mesh(me)
pols = descrever(bm, ob.matrix_world)
# a triangulação BEAUTY de cada polígono (a do modificador 'triangular' da junção: soquetes.juntar_pecas)
indices = {p['face'] for p in pols}
bm.faces.ensure_lookup_table()
normais = {p['face']: Vector(p['normal']) for p in pols}
alvo = [bm.faces[i] for i in indices if len(bm.faces[i].verts) > 3]
res = bmesh.ops.triangulate(bm, faces=alvo, quad_method='BEAUTY', ngon_method='BEAUTY')
bm.normal_update()
mapa = res['face_map']
tris = {}
for t, origem in mapa.items():
    tris.setdefault(origem.index if origem.is_valid else -1, []).append(t)
for p in pols:
    ts = tris.get(p['face'], [])
    p['triangulos'] = [{'normal': r(t.normal), 'areaMM2': round(t.calc_area() / S / S, 5),
                        'vira': t.normal.dot(normais[p['face']]) < 0.0} for t in ts]
print('POLIGONOS', json.dumps(pols, ensure_ascii=False), flush=True)
bm.free()
perto = bpy.data.objects['perto_base']
bm = bmesh.new()
bm.from_mesh(perto.data)
print('PERTO', json.dumps(descrever(bm, perto.matrix_world), ensure_ascii=False), flush=True)
bm.free()
