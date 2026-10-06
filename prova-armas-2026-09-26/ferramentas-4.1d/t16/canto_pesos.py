"""A malha de entrada do chanfro de uma peça (depois do chanfro_local.preparar, com os pesos) em volta de um ponto,
construída como o construir faz, num nível: as arestas a até RAIO mm (os vértices, o peso, a largura do chanfro nela,
o ângulo entre as faces) e os polígonos (os vértices e a normal); e a saída do chanfro (a malha avaliada sem os cortes
finais) ali.
    blender -b --factory-startup -P canto_pesos.py -- <arma> <nivel> <peça> <x> <y> <z> [raio]
"""
import importlib
import json
import math
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import chanfro_local as CL  # noqa: E402
from armas import pecas  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL, PECA = a[0], a[1], a[2]
PONTO = Vector([float(c) for c in a[3:6]])
RAIO = float(a[6]) if len(a) > 6 else 3.0
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
ch = ob.modifiers.get('chanfro')
largura = ch.width / S
bm = bmesh.new()
bm.from_mesh(ob.data)
bm.transform(ob.matrix_world)
bm.normal_update()
camada = bm.edges.layers.float.get(CL.CAMADA)
arestas = []
for e in bm.edges:
    u, v = e.verts[0].co / S, e.verts[1].co / S
    q = PONTO
    ab = v - u
    k = 0.0 if ab.length_squared == 0 else max(0.0, min(1.0, (q - u).dot(ab) / ab.length_squared))
    if (q - (u + ab * k)).length <= RAIO:
        ang = math.degrees(e.calc_face_angle(0.0)) if len(e.link_faces) == 2 else None
        arestas.append({'aresta': e.index, 'de': r(u), 'a': r(v), 'mm': round(e.calc_length() / S, 3),
                        'peso': round(e[camada], 4), 'chanfroMM': round(e[camada] * largura, 4),
                        'angulo': None if ang is None else round(ang, 1)})
faces = []
for f in bm.faces:
    cs = [x.co / S for x in f.verts]
    if min((c - PONTO).length for c in cs) <= RAIO or any(x['aresta'] in {e.index for e in f.edges} for x in arestas):
        faces.append({'face': f.index, 'normal': r(f.normal), 'n': len(cs),
                      'vertices': [r(c) for c in cs] if len(cs) <= 8 else
                      [r(c) for c in cs if (c - PONTO).length <= RAIO * 2]})
bm.free()
print('ENTRADA', json.dumps({'largura': largura, 'arestas': arestas, 'faces': faces}, ensure_ascii=False), flush=True)
for m in ob.modifiers:
    if m.name.startswith('corte final'):
        m.show_viewport = False
sai = CL._malha_avaliada(ob)
sai.transform(ob.matrix_world)
sai.normal_update()
saida = []
for f in sai.faces:
    cs = [x.co / S for x in f.verts]
    if min((c - PONTO).length for c in cs) <= RAIO and len(cs) <= 12:
        saida.append({'face': f.index, 'normal': r(f.normal), 'vertices': [r(c) for c in cs]})
sai.free()
print('SAIDA', json.dumps(saida, ensure_ascii=False), flush=True)
# as contas de _respeitar nas arestas da entrada perto do ponto, com os pesos finais (o encontro de A, B e C)
bm = bmesh.new()
bm.from_mesh(ob.data)
bm.verts.index_update()
bm.edges.index_update()
bm.edges.ensure_lookup_table()
bm.normal_update()
camada = bm.edges.layers.float.get(CL.CAMADA)
w = [e[camada] for e in bm.edges]
t = ch.width
contas = []
for vb, ia, ib, ic, comp, s1, c1, s2, c2, des_a, des_c in CL._cantos(bm):
    e = bm.edges[ib]
    u, v = (ob.matrix_world @ e.verts[0].co) / S, (ob.matrix_world @ e.verts[1].co) / S
    meio = (u + v) / 2
    if (meio - PONTO).length > RAIO * 2:
        continue
    if w[ia] <= 0 and w[ib] <= 0 and w[ic] <= 0:
        continue
    soma = ((w[ia] + c1 * w[ib]) / s1 if s1 != 0.0 else 0.0) + ((w[ic] + c2 * w[ib]) / s2 if s2 != 0.0 else 0.0)
    contas.append({'B': ib, 'A': ia, 'C': ic, 'de': r(u), 'a': r(v), 'pesos': [round(w[i], 4) for i in (ia, ib, ic)],
                   'th1': round(math.degrees(math.atan2(s1, c1)), 2), 'th2': round(math.degrees(math.atan2(s2, c2)), 2),
                   'encontroMM': round(soma * t / S, 4), 'cabeMM': round(CL.MARGEM * comp / S, 4)})
bm.free()
print('CONTAS', json.dumps(contas, ensure_ascii=False), flush=True)
