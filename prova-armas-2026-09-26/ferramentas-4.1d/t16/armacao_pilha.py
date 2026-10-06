"""Onde a malha de uma peça abre na preparação do chanfro local (chanfro_local.preparar): a arma construída sem o
chanfro local (a pilha intacta: os cortes como modificadores) e, na peça, as arestas abertas da malha avaliada sem o
chanfro e sem os cortes finais; depois de aplicar a pilha de antes do chanfro (aplicar_pilha); depois de desfazer as
arestas e as faces mortas (dissolve_degenerate, DEGENERADO); e depois da forma canônica sem a grade.
    blender -b --factory-startup -P armacao_pilha.py -- <arma> <nivel> <peça>
"""
import importlib
import json
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica, pecas  # noqa: E402
from armas import chanfro_local as CL  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL, PECA = a[0], a[1], a[2]
pecas.chanfro_local = lambda: None  # a pilha fica como os modificadores (sem o preparar)
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
ob = bpy.data.objects[PECA]


def abertas(bm, mw):
    return [[round(c / S, 3) for c in mw @ v.co] for e in bm.edges if not e.is_manifold for v in e.verts]


print('PILHA', [(m.name, m.type) for m in ob.modifiers], flush=True)
# os modificadores depois dos cortes de antes do chanfro saem da avaliação
for m in ob.modifiers:
    if not m.name.startswith('corte') or m.name.startswith('corte final'):
        m.show_viewport = False
bm = CL._malha_avaliada(ob)
print('AVALIADA', json.dumps(abertas(bm, ob.matrix_world)), flush=True)
bm.free()
for m in ob.modifiers:
    m.show_viewport = True
CL.aplicar_pilha(ob)
bm = bmesh.new()
bm.from_mesh(ob.data)
print('APLICADA', json.dumps(abertas(bm, ob.matrix_world)), flush=True)
bmesh.ops.dissolve_degenerate(bm, dist=CL.DEGENERADO * S, edges=bm.edges[:])
print('DISSOLVIDA', json.dumps(abertas(bm, ob.matrix_world)), flush=True)
bm.to_mesh(ob.data)
bm.free()
canonica.canonizar(ob.data, grade=False)
bm = bmesh.new()
bm.from_mesh(ob.data)
print('CANONICA', json.dumps(abertas(bm, ob.matrix_world)), flush=True)
bm.free()
