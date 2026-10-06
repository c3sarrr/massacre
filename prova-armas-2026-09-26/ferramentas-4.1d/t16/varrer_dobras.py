"""As dobras (armas/dobras.py) das peças de uma arma na .blend da conferência: as do nível de jogo (a cópia avaliada na
forma canônica, como a validação e a junção a veem) e, com --alto, as do modelo alto; e os triângulos virados da
`perto_base` triangulada (o que o jogo e a validação da pega usam). Por peça: quantas de cada tipo e as primeiras.
    blender -b --factory-startup -P varrer_dobras.py -- <arma> [--alto]
"""
import json
import os
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica, dobras  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA = a[0]
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, 'tools', 'blender', 'conferencia', ARMA, f'{ARMA}.blend'))


def varrer(objetos, rotulo):
    total = {}
    for ob in sorted(objetos, key=lambda o: o.name):
        if ob.type != 'MESH' or ob.get('cortador') or ob.hide_render:
            continue
        me = canonica.avaliada(ob)
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.transform(ob.matrix_world)
        t0 = time.time()
        ds = dobras.dobras(bm)
        dt = time.time() - t0
        bm.free()
        bpy.data.meshes.remove(me)
        if ds:
            tipos = {}
            for p, k in ds:
                tipos.setdefault(k, []).append([round(c / S, 2) for c in p])
            for k, ps in tipos.items():
                total[k] = total.get(k, 0) + len(ps)
            print('DOBRA', rotulo, ob.name, json.dumps({k: [len(ps), ps[:24]] for k, ps in tipos.items()},
                                                        ensure_ascii=False), round(dt, 2), 's', flush=True)
    print('TOTAL', rotulo, json.dumps(total), flush=True)


varrer(bpy.data.collections['jogo'].objects, 'jogo')
if '--alto' in a:
    varrer(bpy.data.collections['alto'].objects, 'alto')
for ob in bpy.data.collections['perto'].objects:
    if ob.type != 'MESH':
        continue
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    # a junção tira as faces escondidas dentro de outra peça da base (soquetes.remover_escondidas): as abertas da perto
    # são as bordas desses buracos; contam as viradas
    ds = [(p, k) for p, k in dobras.dobras(bm) if k == 'virada']
    bm.free()
    print('PERTO', ob.name, len(ds), json.dumps([[round(c / S, 2) for c in p] for p, k in ds[:24]],
                                                 ensure_ascii=False), flush=True)
