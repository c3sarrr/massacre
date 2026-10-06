"""Onde a palma para na chegada (a reprovação da AK na Tarefa 16: o contato da palma a 1,49 mm da arma, com a palma
16,4 mm antes do ponto de chegada em vez de 11,3): a pega de um lado pelo banco (t14/pega_banco.py) sobre uma .blend
da conferência com as luvas montadas (a do construir, ou a cópia de antes, `.blend1`), e em cada chegada da palma
(empunhadura_arma.encostar) os vértices do corpo da luva que encostam primeiro: o osso, a posição, quanto entram, a
peça mais perto, o ponto e a normal dela ali. No fim, os vértices da palma (empunhadura_validacao: a mão, a tenar e a
hipotenar) mais perto da arma, com a peça.
    blender -b --factory-startup -P diag_chegada.py -- <arma> <categoria> <lado: d ou e> <.blend> <pasta>
"""
import json
import os
import sys

ARMA, CATEGORIA, LADO, BLEND, TRABALHO = sys.argv[sys.argv.index('--') + 1:][:5]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import numpy as np  # noqa: E402
import pega_banco as B  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import empunhadura_validacao as V  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
pecas = {k: o for k, o in B.C['perto'].items() if not k.startswith('_')}
por_peca = {k: B.EA.Arma([o]) for k, o in pecas.items()}


def mais_perto(q, n=3):
    perto = []
    for nome, arma in por_peca.items():
        dd = arma.distancia(q, 30.0)
        if dd is not None:
            perto.append((abs(dd), dd, nome))
    perto.sort()
    return [(nome, round(dd, 3)) for _a, dd, nome in perto[:n]]


original = B.EA.encostar
chamadas = []


def encostar(na, m, direcao, encaixe, indices=None, chegada=B.EA.CHEGADA_MM, alcance=None):
    enc, andou = original(na, m, direcao, encaixe, indices, chegada, alcance)
    a = andou + chegada
    pose = m.pose()
    p0 = na.pontos(pose, encaixe)
    linhas = []
    for passo in (0.03, 0.5, 2.0):
        pts = p0 + np.array(direcao * (a + passo - chegada))
        tocam = []
        for i in (range(len(pts)) if indices is None else indices):
            c = na._cede(i)
            d = na.arma.distancia(Vector(pts[i]), B.EA.PERTO_DA_ARMA_MM + c)
            if d is not None and -(d + c) > B.EA.CONTATO_MM:
                tocam.append((-(d + c), i))
        tocam.sort(reverse=True)
        ossos = {}
        for e, i in tocam:
            ossos.setdefault(na.col.dono[i], []).append((e, i))
        linhas.append({'alem': passo, 'vertices': len(tocam),
                       'porOsso': {o: [len(v), round(v[0][0], 3)] for o, v in ossos.items()}})
        if passo == 0.03:
            for e, i in tocam[:8]:
                q = Vector(pts[i])
                co, n, _k, dist = na.arma.bvh.find_nearest(q)
                print('CHEGADA-TOCA', json.dumps({'chamada': len(chamadas), 'entra': round(e, 3), 'vertice': i,
                                                  'osso': na.col.dono[i], 'pos': [round(c, 2) for c in q],
                                                  'pecas': mais_perto(q), 'ponto': [round(c, 3) for c in co],
                                                  'normal': [round(c, 3) for c in n]}, ensure_ascii=False),
                      flush=True)
    chamadas.append({'andouMM': round(andou, 3), 'direcao': [round(c, 4) for c in direcao], 'passos': linhas})
    print('CHEGADA', json.dumps(chamadas[-1], ensure_ascii=False), flush=True)
    return enc, andou


B.EA.encostar = encostar
s = B.mao(LADO)
f = B.C['ultima']['f']
col = f['col']
na = B.EA.NaArma(col, B.C['arma'], f['na'].encaixe, ceder=False, afundar=B.C['ultima']['afundar'])
pts = na.pontos(f['m'].pose())
palma = [i for i, o in enumerate(col.dono) if o in V.PALMA] if hasattr(V, 'PALMA') else []
dists = sorted((B.C['arma'].distancia(Vector(pts[i]), 40.0) or 40.0, i) for i in palma)
print('PALMA-VERTICES', len(palma), flush=True)
for d, i in dists[:10]:
    q = Vector(pts[i])
    print('PALMA', json.dumps({'mm': round(d, 3), 'vertice': i, 'osso': col.dono[i], 'pos': [round(c, 2) for c in q],
                               'pecas': mais_perto(q)}, ensure_ascii=False), flush=True)
print('FIM', json.dumps({'chegadas': len(chamadas)}), flush=True)
