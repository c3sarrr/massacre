"""O "Loop Slide" do chanfro e as dobras (Tarefa 16, correção C4): constrói uma arma num nível como o construir faz e
conta as dobras (armas/dobras.py) de cada peça na cópia avaliada na forma canônica (como a junção e a validação a
veem). --sem-deslize: desliga o deslize (loop_slide) no chanfro das peças com o chanfro local e refaz o desdobrar e o
conserto dos cortes finais delas. --sem-chanfro: as dobras de antes do chanfro (o modificador desligado em todas).
--global: a arma sem o chanfro local (pecas.chanfro_local sem efeito: o limite global do Blender, como na 4.1c).
--velho: o desdobrar e o conserto dos cortes finais como eram antes da correção (só os triângulos que se cortam).
Por peça com o chanfro local, a soma do peso vezes o comprimento das arestas chanfradas (PESOS: o tanto de chanfro).
    blender -b --factory-startup -P experimento_deslize.py -- <arma> <nivel> [--sem-deslize] [--sem-chanfro]
        [--global] [--velho]
"""
import importlib
import json
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402

from armas import canonica, dobras, pecas  # noqa: E402
from armas import chanfro_local as CL  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL = a[0], a[1]
SEM = '--sem-deslize' in a
if '--global' in a:
    pecas.chanfro_local = lambda: None
if '--velho' in a:
    CL._defeitos = CL._colisoes
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


t0 = time.time()
M = Materiais()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, M)
pecas.finalizar(col)
print('CONSTRUIDA', round(time.time() - t0, 1), 's', flush=True)
locais = [o for o in col.objects if o.type == 'MESH' and not o.get('cortador') and o.get('chanfro_peso')
          and o.modifiers.get('chanfro') and o.modifiers.get('solda do chanfro')]
if SEM:
    t1 = time.time()
    for ob in locais:
        m = ob.modifiers['chanfro']
        m.loop_slide = False
        sobra = CL.desdobrar(ob, m)
        if sobra:
            print(f'chanfro local: {ob.name} ainda com {sobra} vértices em dobras do chanfro', flush=True)
        CL.consertar_cortes_finais(ob)
    print('SEM_DESLIZE', len(locais), 'peças', round(time.time() - t1, 1), 's', flush=True)
if '--sem-chanfro' in a:
    for ob in col.objects:
        if ob.type == 'MESH' and ob.modifiers.get('chanfro'):
            ob.modifiers['chanfro'].show_viewport = False
for ob in sorted(locais, key=lambda o: o.name):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    camada = bm.edges.layers.float.get(CL.CAMADA)
    soma = sum(e[camada] * e.calc_length() for e in bm.edges) / S if camada else 0.0
    n = sum(1 for e in bm.edges if camada and e[camada] > 0.0)
    bm.free()
    print('PESOS', json.dumps([ob.name, round(soma, 3), n], ensure_ascii=False), flush=True)
total = {}
for ob in sorted(col.objects, key=lambda o: o.name):
    if ob.type != 'MESH' or ob.get('cortador'):
        continue
    me = canonica.avaliada(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)
    ds = dobras.dobras(bm)
    bm.free()
    bpy.data.meshes.remove(me)
    if ds:
        tipos = {}
        for p, k in ds:
            tipos.setdefault(k, []).append([round(c / S, 2) for c in p])
        for k, ps in tipos.items():
            total[k] = total.get(k, 0) + len(ps)
        print('DOBRA', ob.name, json.dumps({k: [len(ps), ps[:12]] for k, ps in tipos.items()}, ensure_ascii=False),
              flush=True)
modo = [k for k in ('--sem-deslize', '--sem-chanfro', '--global', '--velho') if k in a]
print('TOTAL', ARMA, NIVEL, ' '.join(modo) or 'como o construir', json.dumps(total), flush=True)
