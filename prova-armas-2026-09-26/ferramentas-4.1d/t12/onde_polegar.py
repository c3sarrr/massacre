# Tarefa 12 (a regra lateral): onde ficam a polpa e a ponta do polegar (e as pontas dos dedos) na pega da prova do bloco
# (provas_lateral.py), em mm no referencial do bloco (X para a boca, Y para a esquerda, Z para cima; o bloco vai de
# y −27 a +27 e de z −28 a +28): o ponto, a distância ao bloco e a normal dele embaixo. Sem as vistas; só leitura.
#   blender -b --factory-startup -P onde_polegar.py -- <contexto das luvas> <altura>,<inclinação>,<girada>,<polegar>,<guinada>
import os
import sys

ARMAS = 'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/armas'
sys.path.insert(0, os.path.dirname(ARMAS))

fonte = open(ARMAS + '/provas_lateral.py', encoding='utf-8').read().rstrip()
assert fonte.endswith('\nprincipal()')
g = {'__file__': ARMAS + '/provas_lateral.py', '__name__': 'onde_polegar'}
exec(compile(fonte[:-len('principal()')], ARMAS + '/provas_lateral.py', 'exec'), g)


def vistas(rig, f, pasta, fundo):
    """No lugar das vistas: a polpa e a ponta do polegar e as pontas dos dedos, no referencial do bloco."""
    import numpy as np
    from mathutils import Vector
    from armas import empunhadura_arma as EA, empunhadura_polegar as polegar
    na = f['na']
    pts = np.asarray(na.pontos(f['m'].pose()))
    cadeia = polegar.Cadeia(f['col'], g['mao_global'], {})
    lugares = {'polpa do polegar': cadeia.lado_da_polpa,
               'ponta do polegar': na.vertices(['polegar_3'])}
    for d in ('indicador', 'medio', 'anelar', 'minimo'):
        lugares[f'polpa do {d}'] = EA.CadeiaDedo(na, d, {}).lado_da_polpa
    for nome, idx in lugares.items():
        q = pts[idx]
        if nome.startswith('ponta'):
            # a ponta: o vértice da distal mais longe do meio da falange proximal posada
            base = pts[na.vertices(['polegar_2'])].mean(0)
            p = Vector(q[int(np.argmax(np.linalg.norm(q - base, axis=1)))])
        else:
            p = Vector(q.mean(0))
        co, n, _i, dist = na.arma.bvh.find_nearest(p)
        print(f'MASSACRE-ONDE {nome}: ({p.x:7.1f}, {p.y:6.1f}, {p.z:6.1f}) mm, a {dist:5.2f} mm do bloco, a normal '
              f'embaixo ({n.x:5.2f}, {n.y:5.2f}, {n.z:5.2f})', flush=True)


g['vistas'] = vistas
_montar = g['empunhadura_pega'].montar_luvas


def montar(*a, **k):
    mao, bracos = _montar(*a, **k)
    g['mao_global'] = mao
    return mao, bracos


g['empunhadura_pega'].montar_luvas = montar
g['principal']()
