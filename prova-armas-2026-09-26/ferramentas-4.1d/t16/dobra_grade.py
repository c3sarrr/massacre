"""As dobras de uma peça construída como o construir faz, na malha avaliada sem a grade e na forma canônica com a grade
de 1 µm (canonica.avaliada, a que a junção usa): se uma dobra nasce do arredondamento à grade. --cru: o desdobrar
do chanfro local procurando os defeitos na malha sem a grade (como na primeira versão da correção). --sem-finais: as
dobras sem os cortes finais (a malha que o desdobrar examina).
    blender -b --factory-startup -P dobra_grade.py -- <arma> <nivel> <peça> [<peça> ...] [--cru] [--sem-finais]
"""
import importlib
import json
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica, dobras, pecas  # noqa: E402
from armas import chanfro_local as CL  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL, NOMES = a[0], a[1], [n for n in a[2:] if not n.startswith('--')]
if '--cru' in a:
    from mathutils import Vector  # noqa: E402

    def _defeitos_cru(ob):
        bm = CL._malha_avaliada(ob)
        pontos = [Vector(p) for p, _tipo in dobras.dobras(bm)]
        pontos.extend(CL._cruzados(bm))
        bm.free()
        return pontos
    CL._defeitos = _defeitos_cru
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


M = Materiais()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)


def contar(me, mw):
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(mw)
    ds = dobras.dobras(bm)
    bm.free()
    return [[k] + [round(c / S, 3) for c in p] for p, k in ds]


for nome in NOMES:
    ob = bpy.data.objects[nome]
    if '--sem-finais' in a:
        for m in ob.modifiers:
            if m.name.startswith('corte final'):
                m.show_viewport = False
    dg = bpy.context.evaluated_depsgraph_get()
    cru = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), depsgraph=dg)
    sem_grade = contar(cru, ob.matrix_world)
    bpy.data.meshes.remove(cru)
    can = canonica.avaliada(ob)
    com_grade = contar(can, ob.matrix_world)
    bpy.data.meshes.remove(can)
    print('GRADE', nome, json.dumps({'semGrade': sem_grade[:30], 'comGrade': com_grade[:30],
                                     'n': [len(sem_grade), len(com_grade)]}, ensure_ascii=False), flush=True)
