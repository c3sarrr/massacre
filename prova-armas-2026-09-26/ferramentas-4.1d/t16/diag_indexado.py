"""Por que o indicador indexado da pistola desceu (a reprovação da Glock na Tarefa 16: a 0,11 mm abaixo do alto do
gatilho, com a abertura de −15,75° para −10,5°): a mão do gatilho pelo banco (t14/pega_banco.py) sobre uma .blend da
conferência com as luvas montadas e, no `indexar` (empunhadura_dedo.py), a mesma busca refeita aqui com o custo
separado por termo — a folga das falanges à lateral, a normal de frente para a face, a entrada na arma, as folgas do
ferrolho e do gatilho, a altura acima do gatilho, o eixo e a curva —, o melhor ponto da grade (a partida) e o raio
final, na solução e nos graus de `--outros` (os de outra .blend, para comparar), com a face mais perto de cada ponto
do eixo do dedo (a peça, o ponto e a normal).
    blender -b --factory-startup -P diag_indexado.py -- <arma> <categoria> <.blend> <pasta> [--outros <json dos graus>]
"""
import itertools
import json
import math
import os
import sys

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, BLEND, TRABALHO = a[:4]
OUTROS = json.loads(a[a.index('--outros') + 1]) if '--outros' in a else []
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import empunhadura_dedo as D  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
EA = B.EA
por_peca = {k: EA.Arma([o]) for k, o in B.C['perto'].items() if not k.startswith('_')}


def peca_de(q):
    melhor = None
    for nome, arma in por_peca.items():
        co, _n, _i, d = arma.bvh.find_nearest(q)
        if co is not None and (melhor is None or d < melhor[1]):
            melhor = (nome, d)
    return melhor[0]


original = D.indexar


def indexar(na, mao, m, dedo, face, eixo, raio, abertura, evitar=None, longe=None, acima=None):
    lim = EA.limites_do_dedo(mao, abertura)
    rep = mao.rep
    cadeia = EA.CadeiaDedo(na, dedo, m.pose())
    dedo_v = na.vertices(cadeia.ossos)

    def termos(g, r):
        ms = cadeia.matrizes(g)
        t = {'acima': 0.0, 'folga': 0.0, 'face': 0.0, 'arma': 0.0, 'ferrolho': 0.0, 'gatilho': 0.0, 'eixo': 0.0}
        pontos = D._pontos(cadeia, ms)
        if acima is not None:
            for q in pontos[len(D.PONTOS):]:
                falta = acima[0] + acima[1] - q.z
                if falta > 0.0:
                    t['acima'] += (D.PESO_LONGE * falta) ** 2
        faces = []
        for q in pontos:
            d, n = D._distancia(na.arma, q)
            f = d - r
            t['folga'] += f * f
            t['face'] += (D.PESO_FACE_MM * (1.0 - n.dot(face))) ** 2
            if f < 0.0:
                t['arma'] += (D.PESO_ARMA * f) ** 2
            for nome, peca in (('ferrolho', evitar), ('gatilho', longe)):
                if peca is not None:
                    falta = peca[1] + r + D.FERROLHO_MARGEM_MM - D._distancia(peca[0], q)[0]
                    if falta > 0.0:
                        t[nome] += (D.PESO_LONGE * falta) ** 2
            co, nn, _i, dd = na.arma.bvh.find_nearest(q)
            faces.append({'q': [round(c, 2) for c in q], 'd': round(d, 2), 'peca': peca_de(co),
                          'ponto': [round(c, 2) for c in co], 'normal': [round(c, 3) for c in nn]})
        for k in range(3):
            direcao = (ms[k].to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
            t['eixo'] += (D.PESO_EIXO_MM * (1.0 - direcao.dot(eixo))) ** 2
        curva = abs(g['pip'] + rep['pip']) + abs(g['dip'] + rep['dip'])
        t['curva'] = (D.PESO_CURVA_MM * curva) ** 2
        t = {k: round(v, 3) for k, v in t.items()}
        t['total'] = round(sum(t.values()), 3)
        altura = min(q.z for q in pontos[len(D.PONTOS):]) - acima[0] if acima is not None else None
        return t, faces, altura

    def custo_de(g, r):
        return termos(g, r)[0]['total']

    def valores(x, y):
        n = max(1, math.ceil((y - x) / D.GRADE_GRAUS))
        return [x + (y - x) * k / n for k in range(n + 1)]

    grade = sorted(((custo_de(dict(zip(EA.GRAUS_DO_DEDO, comb)), raio), comb)
                    for comb in itertools.product(*(valores(*lim[k]) for k in EA.GRAUS_DO_DEDO))))
    print('GRADE', json.dumps({'limites': {k: [round(v, 2) for v in lim[k]] for k in EA.GRAUS_DO_DEDO},
                               'melhores': [[round(c, 2), [round(v, 2) for v in comb]] for c, comb in grade[:8]]}),
          flush=True)
    m2, rel = original(na, mao, m, dedo, face, eixo, raio, abertura, evitar, longe, acima)
    g = {k: rel['graus'][k] for k in EA.GRAUS_DO_DEDO}
    for r in (raio, raio + D.RAIO_PASSO_MM, raio + 2 * D.RAIO_PASSO_MM):
        t, faces, altura = termos(g, r)
        print('SOLUCAO', json.dumps({'raio': r, 'graus': g, 'termos': t, 'acimaMM': round(altura, 2)}), flush=True)
    t, faces, altura = termos(g, raio)
    for f in faces:
        print('FACE', json.dumps(f, ensure_ascii=False), flush=True)
    for outro in OUTROS:
        go = {k: outro[k] for k in EA.GRAUS_DO_DEDO}
        t, faces, altura = termos(go, raio)
        print('OUTRO', json.dumps({'raio': raio, 'graus': go, 'termos': t, 'acimaMM': round(altura, 2)}), flush=True)
        for f in faces:
            print('FACE-OUTRO', json.dumps(f, ensure_ascii=False), flush=True)
    print('REL', json.dumps(rel, ensure_ascii=False), flush=True)
    return m2, rel


B.EP.dedo_indexado.indexar = indexar
s = B.mao('d')
print('FIM', flush=True)
