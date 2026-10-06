# O modelo alto de uma arma: as arestas abertas e soltas de cada peça avaliada (com os modificadores) e, desde a
# Tarefa 16 (correção C4), as dobras (armas/dobras.py: o contorno de um polígono cruzando com ele mesmo, os polígonos
# vizinhos virados), na forma canônica com a grade de 1 µm (a malha que o assar e a junção usam).
# Uso: blender -b --factory-startup -P arma_alto_abertas.py -- <arma>
import importlib
import json
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica, dobras, pecas  # noqa: E402
from armas.unidades import S  # noqa: E402

ARMA = sys.argv[sys.argv.index('--') + 1]
NIVEL = sys.argv[sys.argv.index('--') + 2] if len(sys.argv) > sys.argv.index('--') + 2 else 'alto'
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json', encoding='utf-8'))
t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
M = {z: bpy.data.materials.new(z) for z in ("corpo", "guarnicao", "carregador", "detalhes", "interno", "municao", "vidro")}
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)
print('construído', round(time.time() - t0, 1), flush=True)
dg = bpy.context.evaluated_depsgraph_get()
total = 0
dobradas = 0
for ob in sorted(col.objects, key=lambda o: o.name):
    if ob.type != 'MESH' or ob.get('cortador'):
        continue
    me = ob.evaluated_get(dg).to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    ab = [e for e in bm.edges if not e.is_manifold and e.link_faces]
    so = [e for e in bm.edges if not e.link_faces]
    if ab or so or not bm.faces:
        cs = [tuple(round(c / S, 2) for c in (e.verts[0].co + e.verts[1].co) / 2) for e in (ab + so)[:6]]
        print(f'  {ob.name}: abertas {len(ab)} soltas {len(so)} faces {len(bm.faces)} ex. {cs}', flush=True)
        total += len(ab) + len(so)
    bm.free()
    ob.evaluated_get(dg).to_mesh_clear()
    can = canonica.avaliada(ob)
    bm = bmesh.new()
    bm.from_mesh(can)
    bpy.data.meshes.remove(can)
    ds = [(p, k) for p, k in dobras.dobras(bm) if k != 'aberta']
    bm.free()
    if ds:
        cs = [tuple(round(c / S, 2) for c in p) for p, _k in ds[:6]]
        print(f'  {ob.name}: dobras {len(ds)} ({sorted({k for _p, k in ds})}) ex. {cs}', flush=True)
        dobradas += len(ds)
print('total', total, 'dobras', dobradas, 'em', round(time.time() - t0, 1), 's', flush=True)
