"""Os polígonos de uma peça em volta de um ponto na saída dos cortes de antes do chanfro (a arma sem o chanfro local, o
chanfro e os cortes finais desligados), com todos os vértices, a normal e as arestas a 180° (as das dobras); e, com
--cortes, a mesma conta tirando um corte de cada vez (os de antes do chanfro), para achar o corte que faz a dobra.
    blender -b --factory-startup -P agulha.py -- <arma> <nivel> <peça> <x> <y> <z> [raio] [--cortes]
"""
import importlib
import json
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import dobras, pecas  # noqa: E402
from armas import chanfro_local as CL  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL, PECA = a[0], a[1], a[2]
PONTO = Vector([float(c) for c in a[3:6]])
RAIO = float(a[6]) if len(a) > 6 and not a[6].startswith('--') else 1.0
pecas.chanfro_local = lambda: None
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


def r(v, k=3):
    return [round(c, k) for c in v]


M = Materiais()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)
ob = bpy.data.objects[PECA]
cortes = [m for m in ob.modifiers if m.name.startswith('corte') and not m.name.startswith('corte final')]
for m in ob.modifiers:
    if m not in cortes:
        m.show_viewport = False


def olhar(rotulo):
    bm = CL._malha_avaliada(ob)
    bm.transform(ob.matrix_world)
    bm.normal_update()
    faces = []
    for f in bm.faces:
        cs = [v.co / S for v in f.verts]
        if min((c - PONTO).length for c in cs) <= RAIO:
            faces.append({'n': len(cs), 'normal': r(f.normal), 'area': round(f.calc_area() / S / S, 4),
                          'vertices': [r(c) for c in cs]})
    viradas = sum(1 for _p, k in dobras.dobras(bm) if k == 'virada')
    bm.free()
    print(rotulo, json.dumps({'viradas': viradas, 'faces': faces}, ensure_ascii=False), flush=True)
    return viradas


print('CORTES', [(m.name, m.object.name if m.object else None) for m in cortes], flush=True)
olhar('TODOS')
if '--cortes' in a:
    for m in cortes:
        m.show_viewport = False
        bm = CL._malha_avaliada(ob)
        v = sum(1 for _p, k in dobras.dobras(bm) if k == 'virada')
        bm.free()
        print('SEM', m.name, m.object.name if m.object else None, 'viradas', v, flush=True)
        m.show_viewport = True
