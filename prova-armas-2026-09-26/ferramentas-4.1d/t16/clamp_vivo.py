"""O limite global do Blender ('clamp overlap') ainda age nas peças do chanfro local? (Tarefa 16, correção C4.) Constrói a
arma num nível como o construir (os pesos do chanfro local e o desdobrar de hoje) e, em cada peça com o chanfro por peso,
avalia a peça com o limite ligado (como sai hoje) e desligado: se a malha muda, o Blender reduziu o chanfro da peça
inteira pela menor folga dele (bmesh_bevel.cc, bevel_limit_offset), e a largura de verdade é menor que a dos pesos. Por
peça: a área da malha avaliada com e sem o limite, a maior distância entre vértices correspondentes (quando a contagem
bate) e o fator que o Blender aplicou (a razão das larguras medida nos vértices do chanfro, aproximada pela área).
    blender -b --factory-startup -P clamp_vivo.py -- <arma> <nivel>
"""
import importlib
import json
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import pecas  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL = a[0], a[1]
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


def medir(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    av = ob.evaluated_get(dg)
    me = av.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    area = sum(f.calc_area() for f in bm.faces) / S / S
    cos = [v.co.copy() for v in bm.verts]
    bm.free()
    av.to_mesh_clear()
    return area, cos


t = time.time()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, Materiais())
pecas.finalizar(col)
print('CONSTRUIDA', round(time.time() - t, 1), 's', flush=True)
agindo = 0
for ob in sorted(col.objects, key=lambda o: o.name):
    m = ob.modifiers.get('chanfro') if ob.type == 'MESH' else None
    if m is None or not ob.get('chanfro_peso') or m.limit_method != 'WEIGHT':
        continue
    m.use_clamp_overlap = True
    a1, c1 = medir(ob)
    m.use_clamp_overlap = False
    a2, c2 = medir(ob)
    m.use_clamp_overlap = True
    desloc = max(((p - q).length for p, q in zip(c1, c2)), default=0.0) / S if len(c1) == len(c2) else None
    if abs(a1 - a2) > 1e-6 * max(a2, 1.0) or (desloc is not None and desloc > 1e-5) or len(c1) != len(c2):
        agindo += 1
        print('AGINDO', json.dumps({'peca': ob.name, 'largura': round(m.width / S, 3), 'areaCom': round(a1, 3),
                                    'areaSem': round(a2, 3), 'vertices': [len(c1), len(c2)],
                                    'maiorDeslocamento': None if desloc is None else round(desloc, 4)},
                                   ensure_ascii=False), flush=True)
print('FIM', ARMA, NIVEL, 'peças com o limite global agindo:', agindo, flush=True)
