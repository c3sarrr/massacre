"""Onde o desdobrar do chanfro local (chanfro_local.desdobrar) tira chanfro de uma arma (Tarefa 16, correção C4):
constrói a arma num nível como o construir faz e, em cada peça com o chanfro local, guarda os pesos das arestas antes
e depois do desdobrar (e o pedido, com os pesos de partida, antes do limite local), os defeitos que ele achou no
começo (os de dobras.dobras por tipo e os triângulos que se cruzam, tirados os que já havia sem o chanfro) e os
lugares em que o chanfro caiu: as arestas que perderam mais de 10% do peso, juntadas pela distância entre os meios
(até 2 mm), com o comprimento, a largura de antes e a de depois (mm, a maior de cada lugar).
Com --despejo <pasta>: um JSON por peça com todos os defeitos do começo e as arestas que perderam peso (as pontas, mm).
Com --sem-espelho: o desdobrar sem a redução espelhada pelo plano da arma.
Com --velho: o desdobrar de antes das arestas curtas primeiro e do espelho.
    blender -b --factory-startup -P perdas.py -- <arma> <nivel> [--despejo <pasta>]
"""
import importlib
import json
import os
import sys
import time

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import canonica, dobras, pecas  # noqa: E402
from armas import chanfro_local as CL  # noqa: E402
from armas.unidades import S  # noqa: E402

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, NIVEL = a[0], a[1]
DESPEJO = a[a.index('--despejo') + 1] if '--despejo' in a else None
mod = importlib.import_module(f'armas.{ARMA}')
ficha = json.load(open(rf'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\{ARMA}.json',
                       encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
original = CL.desdobrar
pedidos = {}  # nome da peça → o chanfro pedido (mm², a largura vezes o comprimento com os pesos de partida)
preparar_original, pesos_original = CL.preparar, CL.pesos
_atual = {}


def preparar(ob, largura_bu):
    _atual['ob'], _atual['largura'] = ob, largura_bu
    try:
        return preparar_original(ob, largura_bu)
    finally:
        _atual.clear()


def pesos(bm, t, por_peso, w=None, tetos=()):
    if w is None and 'ob' in _atual:
        bm.edges.index_update()
        bm.normal_update()
        base = CL._base(bm, por_peso)
        pedidos[_atual['ob'].name] = sum(b * e.calc_length() for b, e in zip(base, bm.edges)) / S * t / S
    return pesos_original(bm, t, por_peso, w, tetos)


CL.preparar, CL.pesos = preparar, pesos
if '--sem-espelho' in a:  # o desdobrar sem a redução espelhada (para medir a diferença dos dois lados)
    CL._espelhos = lambda ob, me: {}
if '--velho' in a:  # o desdobrar de antes das curtas e do espelho (CURTA 0: nenhuma aresta é curta)
    CL.CURTA, CL.PASSOS_DESDOBRAR = 0.0, 24
    CL._espelhos = lambda ob, me: {}
JUNTAR = 2.0  # mm
QUEDA = 0.1


def pesos_e_meios(ob):
    me = ob.data
    at = me.attributes.get(CL.CAMADA)
    w = [0.0] * len(me.edges)
    if at is not None:
        at.data.foreach_get('value', w)
    meios = [(ob.matrix_world @ ((me.vertices[e.vertices[0]].co + me.vertices[e.vertices[1]].co) / 2)) / S
             for e in me.edges]
    comps = [((me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length / S) for e in me.edges]
    return w, meios, comps


def tipos_dos_defeitos(ob, chanfro):
    """Os defeitos novos do chanfro antes de reduzir (como o desdobrar acha), contados por tipo."""
    finais = [m for m in ob.modifiers if m.name.startswith('corte final')]
    vistos = [m.show_viewport for m in finais]
    for m in finais:
        m.show_viewport = False

    def achar():
        me = canonica.avaliada(ob)
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        ds = [(Vector(p), k) for p, k in dobras.dobras(bm)]
        ds.extend((p, 'cruzam') for p in CL._cruzados(bm))
        bm.free()
        return ds
    chanfro.show_viewport = False
    antes = CL._arvore([p for p, _k in achar()])
    chanfro.show_viewport = True
    novos = [(p, k) for p, k in achar() if not CL._perto(antes, p, CL.COLISAO_ANTES * S)]
    for m, v in zip(finais, vistos):
        m.show_viewport = v
    contagem = {}
    for p, k in novos:
        contagem.setdefault(k, []).append([round(c / S, 3) for c in p])
    return contagem


def lugares(w0, w1, meios, comps, largura):
    caidas = [i for i in range(len(w0)) if w0[i] > 0.0 and w1[i] < (1.0 - QUEDA) * w0[i]]
    pai = {i: i for i in caidas}

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i
    for x, i in enumerate(caidas):
        for j in caidas[x + 1:]:
            if (meios[i] - meios[j]).length <= JUNTAR:
                pai[raiz(i)] = raiz(j)
    grupos = {}
    for i in caidas:
        grupos.setdefault(raiz(i), []).append(i)
    saida = []
    for g in grupos.values():
        centro = sum((meios[i] for i in g), Vector()) / len(g)
        perda = sum((w0[i] - w1[i]) * comps[i] for i in g) * largura
        saida.append({'centro': [round(c, 1) for c in centro], 'arestas': len(g),
                      'comprimento': round(sum(comps[i] for i in g), 2),
                      'antes': round(max(w0[i] for i in g) * largura, 3),
                      'depois': round(max(w1[i] for i in g) * largura, 3),
                      'menor': round(min(w1[i] / w0[i] for i in g), 3), 'perda': round(perda, 3)})
    saida.sort(key=lambda x: -x['perda'])
    return saida


def desdobrar(ob, chanfro):
    largura = chanfro.width / S
    w0, meios, comps = pesos_e_meios(ob)
    me = ob.data
    pontas = [[[round(c, 3) for c in (ob.matrix_world @ me.vertices[v].co) / S] for v in e.vertices] for e in me.edges]
    t0 = time.time()
    defeitos = tipos_dos_defeitos(ob, chanfro)
    t1 = time.time()
    sobra = original(ob, chanfro)
    t2 = time.time()
    w1, _m, _c = pesos_e_meios(ob)
    soma0 = sum(x * c for x, c in zip(w0, comps)) * largura
    soma1 = sum(x * c for x, c in zip(w1, comps)) * largura
    if DESPEJO and (defeitos or abs(soma1 - soma0) > 1e-9):
        os.makedirs(DESPEJO, exist_ok=True)
        with open(os.path.join(DESPEJO, f'{ARMA}_{NIVEL}_{ob.name}.json'), 'w', encoding='utf-8') as arq:
            json.dump({'peca': ob.name, 'largura': largura, 'defeitos': defeitos,
                       'arestas': [{'pontas': pontas[i], 'antes': w0[i], 'depois': w1[i]} for i in range(len(w0))
                                   if w0[i] > 0.0]}, arq, ensure_ascii=False)
    if defeitos or abs(soma1 - soma0) > 1e-9:
        print('PERDA', json.dumps({'peca': ob.name, 'largura': round(largura, 3),
                                   'pedido': round(pedidos.get(ob.name, 0.0), 3), 'antes': round(soma0, 3),
                                   'depois': round(soma1, 3), 'sobra': sobra,
                                   'defeitos': {k: [len(v), v[:6]] for k, v in defeitos.items()},
                                   'lugares': lugares(w0, w1, meios, comps, largura)[:12],
                                   'segundos': [round(t1 - t0, 1), round(t2 - t1, 1)]}, ensure_ascii=False),
              flush=True)
    # toda peça do chanfro local: o pedido, o do limite local e o que ficou (mm², a largura vezes o comprimento)
    print('CHANFRO', json.dumps({'peca': ob.name, 'largura': round(largura, 3),
                                 'pedido': round(pedidos.get(ob.name, 0.0), 3), 'local': round(soma0, 3),
                                 'final': round(soma1, 3)}, ensure_ascii=False), flush=True)
    return sobra


CL.desdobrar = desdobrar


class Materiais(dict):
    def __missing__(self, k):
        return self.setdefault(k, bpy.data.materials.new(k))


t = time.time()
col = pecas.iniciar(NIVEL, NIVEL)
mod.construir(ficha, Materiais())
pecas.finalizar(col)
print('FIM', ARMA, NIVEL, round(time.time() - t, 1), 's', flush=True)
