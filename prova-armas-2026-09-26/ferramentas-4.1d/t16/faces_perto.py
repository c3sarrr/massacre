"""As peças de uma arma (com o chanfro como o construir faz, local quando a arma o liga) num nível, avaliadas com os
modificadores, e as faces a até 2 mm de um ponto (mm da arma): a peça, a normal da face e se ela aponta para fora da
peça (a paridade de um raio pela normal), e os cruzamentos da peça com ela mesma (pares de triângulos que se cortam).
    blender -b --factory-startup -P faces_perto.py -- <arma> <nivel> <x> <y> <z> [--todas]
"""
import importlib
import json
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from armas import pecas  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL = a[0], a[1]
PONTO = Vector([float(c) for c in a[2:5]])
TODAS = '--todas' in a  # os cruzamentos de todas as peças, não só das que têm face perto do ponto
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json', encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


M = Materiais()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)
dg = bpy.context.evaluated_depsgraph_get()
for ob in sorted(col.objects, key=lambda o: o.name):
    if ob.type != 'MESH' or ob.get('cortador'):
        continue
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ob.matrix_world
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(mw)
    bm.normal_update()
    vs = [v.co / S for v in bm.verts]
    bm.faces.ensure_lookup_table()
    tris = [[v.index for v in f.verts] for f in bm.faces]
    bvh = BVHTree.FromPolygons(vs, tris)
    perto = bvh.find_nearest_range(PONTO, 2.0)
    if perto or TODAS:
        saida = []
        for co, n, i, d in perto[:8]:
            # a paridade de um raio pela normal: um número par de cruzamentos adiante = a normal aponta para fora
            o = co + n * 0.01
            k, cruz = 0, 0
            while k < 200:
                h = bvh.ray_cast(o, n)
                if h[0] is None:
                    break
                cruz += 1
                o = h[0] + n * 0.01
                k += 1
            saida.append({'face': i, 'dist': round(d, 3), 'normal': [round(c, 3) for c in n],
                          'paraFora': cruz % 2 == 0, 'cruzamentosAdiante': cruz})
        pares = [(p, q) for p, q in bvh.overlap(bvh) if p < q and not set(tris[p]) & set(tris[q])]
        onde = [[round(c, 2) for c in sum((vs[k] for k in tris[p] + tris[q]), Vector()) / len(tris[p] + tris[q])]
                for p, q in pares[:6]]
        print('PERTO', ob.name, json.dumps({'faces': saida, 'paresQueSeCortam': len(pares), 'onde': onde},
                                           ensure_ascii=False), flush=True)
    ev.to_mesh_clear()
    bm.free()
