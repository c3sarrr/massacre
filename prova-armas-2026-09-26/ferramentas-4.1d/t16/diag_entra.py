"""Onde uma luva "entra" numa arma com o chanfro local (as reprovações da Tarefa 16: a AK com 44,82 mm, a M4A4 com
25,31): a pega de um lado pelo banco (t14/pega_banco.py) sobre a .blend da conferência que o construir reprovado gravou,
e os vértices da luva que a distância com sinal dá dentro da arma, sem limite: o osso, a posição, a peça mais perto, o
ponto e a normal dela ali.
    blender -b --factory-startup -P diag_entra.py -- <arma> <categoria> <lado: d ou e> <pasta de trabalho>
"""
import json
import os
import sys

ARMA, CATEGORIA, LADO, TRABALHO = sys.argv[sys.argv.index('--') + 1:][:4]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402
from mathutils import Vector  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
# a .blend que o construir reprovado gravou já tem as luvas montadas (luva_d, rig_d...): o banco carrega dela direto
B.CFG['blend'] = os.path.join(B.RAIZ, 'tools', 'blender', 'conferencia', ARMA, f'{ARMA}.blend')
B.carregar()
s = B.mao(LADO)
f = B.C['ultima']['f']
col = f['col']
na = B.EA.NaArma(col, B.C['arma'], f['na'].encaixe, ceder=False, afundar=B.C['ultima']['afundar'])
pts = na.pontos(f['m'].pose())
dentro = []
for i, q in enumerate(pts):
    d = B.C['arma'].distancia(Vector(q), None)
    if d is not None and d < -0.3:
        dentro.append((d, i))
dentro.sort()
print('DIAG dentro mais de 0,3 mm:', len(dentro), flush=True)
pecas = {k: o for k, o in B.C['perto'].items() if not k.startswith('_')}
for d, i in dentro[:12]:
    q = Vector(pts[i])
    perto = []
    for nome, ob in pecas.items():
        dd = B.EA.Arma([ob]).distancia(q, 60.0)
        if dd is not None:
            perto.append((abs(dd), dd, nome))
    perto.sort()
    co, n, _k, dist = B.C['arma'].bvh.find_nearest(q)
    print('DIAG', json.dumps({'mm': round(d, 3), 'vertice': i, 'osso': col.dono[i], 'pos': [round(c, 1) for c in q],
                              'maisPerto': [(nome, round(dd, 2)) for _a, dd, nome in perto[:3]],
                              'ponto': [round(c, 2) for c in co], 'normal': [round(c, 3) for c in n],
                              'dist': round(dist, 2)}, ensure_ascii=False), flush=True)
