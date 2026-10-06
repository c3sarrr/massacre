"""A população das faces opostas de uma arma (Tarefa 16, a escolha do limite das faces viradas): na .blend da
conferência, nas peças do nível de jogo e do modelo alto (a cópia avaliada na forma canônica) e nas malhas do perto
(já trianguladas), (1) os pares de polígonos vizinhos de normal confiável (dobras.ALTURA_MIN) com o cosseno entre as
normais abaixo de -0,9 (a aresta dá mais de 154° de volta), por faixa de graus que faltam para 180° e com o tipo (a
"cunha": o material entre as duas, como um fio; a "fresta": as duas voltadas uma para a outra; "misto": uma de cada
jeito); e (2) por polígono, a fração do contorno (pelo comprimento das arestas com vizinho confiável) que dá para
vizinhos opostos a -0,9, -0,95 e -0,99 — um polígono virado no meio dos vizinhos dá perto de 1.
    blender -b --factory-startup -P opostas.py -- <arma> [--sem-alto]
"""
import json
import math
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
LIMITES = (-0.9, -0.95, -0.99)
FAIXAS = (1, 2, 4, 8, 16, 26)  # graus que faltam para 180°


def longe(f, e):
    """O vértice de `f` mais longe da reta da aresta `e`."""
    p, q = e.verts[0].co, e.verts[1].co
    pq = q - p
    melhor, vm = -1.0, None
    for v in f.verts:
        if v in e.verts:
            continue
        t = (v.co - p).dot(pq) / pq.length_squared if pq.length_squared else 0.0
        d = (v.co - (p + pq * t)).length
        if d > melhor:
            melhor, vm = d, v
    return vm


def tipo(e, f, g):
    m = (e.verts[0].co + e.verts[1].co) / 2
    vf, vg = longe(f, e), longe(g, e)
    if vf is None or vg is None:
        return '?'
    lg, lf = f.normal.dot(vg.co - m), g.normal.dot(vf.co - m)
    return 'fresta' if lg > 0 and lf > 0 else ('cunha' if lg < 0 and lf < 0 else 'misto')


def olhar(bm, rotulo, nome):
    bm.normal_update()
    altura = dobras.ALTURA_MIN * S
    conf = {}
    for f in bm.faces:
        maior = max(e.calc_length() for e in f.edges)
        conf[f.index] = maior > 0.0 and f.calc_area() / maior > altura
    pares = {x: 0 for x in FAIXAS}
    exemplos = []
    contorno = {}  # face → [comprimento com vizinho confiável, comprimento oposto por limite]
    for e in bm.edges:
        fs = e.link_faces
        if len(fs) != 2:
            continue
        f, g = fs
        if not (conf[f.index] and conf[g.index]):
            continue
        c = f.normal.dot(g.normal)
        comp = e.calc_length()
        for h in (f, g):
            reg = contorno.setdefault(h.index, [0.0, [0.0] * len(LIMITES)])
            reg[0] += comp
            for i, lim in enumerate(LIMITES):
                if c < lim:
                    reg[1][i] += comp
        if c < LIMITES[0]:
            graus = 180.0 - math.degrees(math.acos(max(-1.0, min(1.0, c))))
            for x in FAIXAS:
                if graus < x:
                    pares[x] += 1
                    break
            m = (e.verts[0].co + e.verts[1].co) / 2 / S
            exemplos.append((graus, [round(v, 2) for v in m], tipo(e, f, g),
                             [round(h.calc_area() / S / S, 4) for h in (f, g)], round(comp / S, 3)))
    bm.faces.ensure_lookup_table()
    viradas = {lim: [] for lim in LIMITES}
    for fi, (tot, ops) in contorno.items():
        if tot <= 0.0:
            continue
        for i, lim in enumerate(LIMITES):
            if ops[i] / tot >= 0.5:
                f = bm.faces[fi]
                viradas[lim].append((round(ops[i] / tot, 3), [round(v, 2) for v in f.calc_center_median() / S],
                                     round(f.calc_area() / S / S, 4), len(f.verts)))
    if any(pares.values()) or any(viradas.values()):
        exemplos.sort()
        print('OPOSTAS', rotulo, nome, json.dumps({
            'pares': {f'<{x}°': n for x, n in pares.items() if n},
            'exemplos': [{'graus': round(gr, 3), 'ponto': p, 'tipo': t, 'areas': ar, 'aresta': cp}
                         for gr, p, t, ar, cp in exemplos[:10]],
            'tipos': {t: sum(1 for x in exemplos if x[2] == t) for t in ('cunha', 'fresta', 'misto', '?')},
            'faces': {str(lim): len(v) for lim, v in viradas.items()},
            'exemplosFaces': {str(lim): sorted(v, reverse=True)[:8] for lim, v in viradas.items() if v}},
            ensure_ascii=False), flush=True)
    return pares, {lim: len(v) for lim, v in viradas.items()}


def varrer(colecao, rotulo, avaliar):
    soma_p, soma_f = {x: 0 for x in FAIXAS}, {lim: 0 for lim in LIMITES}
    t0 = time.time()
    for ob in sorted(colecao.objects, key=lambda o: o.name):
        if ob.type != 'MESH' or ob.get('cortador') or (avaliar and ob.hide_render):
            continue
        bm = bmesh.new()
        if avaliar:
            me = canonica.avaliada(ob)
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
        else:
            bm.from_mesh(ob.data)
        bm.transform(ob.matrix_world)
        bm.faces.index_update()
        p, f = olhar(bm, rotulo, ob.name)
        bm.free()
        for x in FAIXAS:
            soma_p[x] += p[x]
        for lim in LIMITES:
            soma_f[lim] += f[lim]
    print('TOTAL', rotulo, json.dumps({'pares': {f'<{x}°': n for x, n in soma_p.items()},
                                       'faces': {str(lim): n for lim, n in soma_f.items()}}),
          round(time.time() - t0, 1), 's', flush=True)


varrer(bpy.data.collections['jogo'], 'jogo', True)
if '--sem-alto' not in a and 'alto' in bpy.data.collections:
    varrer(bpy.data.collections['alto'], 'alto', True)
varrer(bpy.data.collections['perto'], 'perto', False)
print('FIM', ARMA, flush=True)
