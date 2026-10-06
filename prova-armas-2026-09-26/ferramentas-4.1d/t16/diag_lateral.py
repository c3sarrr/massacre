"""A falange média da mão lateral contra a face (a reprovação da AWP na Tarefa 16: a do médio a 67,2° da face esquerda,
com a pose dos dedos a menos de 1° da de antes): a mão esquerda pelo banco (t14/pega_banco.py) sobre uma .blend da
conferência com as luvas montadas e, para cada dedo, o vértice da falange média mais perto da arma (a distância, a
posição), o ponto mais perto e a normal da face que a BVH devolve (a da medida, empunhadura_lateral.medir), a
pseudonormal da arma ali (empunhadura_arma.Arma.pseudonormal: as faces a até 0,05 mm, pesadas pelo ângulo) e as faces a
até 1 mm do ponto (a normal, o ângulo com a face esquerda, a área e a distância), com a mesma conta para os 5 vértices
mais perto — onde a quina de cima da peça fica para a falange. E a medida pelo eixo do osso (EIXO): o ponto do eixo da
falange média (da cabeça à cauda do osso posado) mais perto da arma, o ponto da superfície mais perto dele e o ângulo
entre a direção de um para o outro e a normal da face (0° ao lado da face, 90° por cima da peça; a bissetriz da quina
a 45°), que não depende de que face a malha devolve na quina. E o lugar do polegar (POLEGAR): o centro do lado da
polpa, o ponto mais perto, a normal da face devolvida (a medida, `polegarGraus`), a pseudonormal, as faces a até 1 mm
e o ângulo pela direção do eixo da distal (o osso posado) até a superfície, contra a direção do lugar.
    blender -b --factory-startup -P diag_lateral.py -- <arma> <categoria> <.blend> <pasta> [--direita]
"""
import json
import math
import os
import sys

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, BLEND, TRABALHO = a[:4]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import numpy as np  # noqa: E402
import pega_banco as B  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import empunhadura_lateral as L  # noqa: E402

B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
if '--direita' in a:
    B.mao('d')
s = B.mao('e')
f, afundar = B.C['ultima']['f'], B.C['ultima']['afundar']
arma = B.C['arma']
na = B.EA.NaArma(f['col'], arma, f['na'].encaixe, ceder=False, afundar=afundar)
pts = np.asarray(na.pontos(f['m'].pose()))
face = Vector(f['r']['lateral']['face']).normalized()


def angulo(n):
    return round(math.degrees(math.acos(max(-1.0, min(1.0, Vector(n).normalized().dot(face))))), 2)


for d in ('indicador', 'medio', 'anelar', 'minimo'):
    idx = na.vertices([f'{d}_2'])
    dist = sorted((arma.distancia(Vector(pts[i])), i) for i in idx)
    for k, (dd, i) in enumerate(dist[:5]):
        q = Vector(pts[i])
        co, n, fi, _d = arma.bvh.find_nearest(q)
        pn = arma.pseudonormal(co)
        perto = []
        for c2, n2, i2, d2 in arma.bvh.find_nearest_range(co, 1.0):
            vs = [arma.verts[j] for j in arma.polys[i2]]
            area = 0.5 * (vs[1] - vs[0]).cross(vs[2] - vs[0]).length if len(vs) >= 3 else 0.0
            perto.append((round(d2, 3), angulo(n2), round(area, 3), [round(c, 3) for c in n2]))
        perto.sort()
        print('MEDIA', json.dumps({'dedo': d, 'k': k, 'vertice': i, 'mm': round(dd, 3), 'pos': [round(c, 2) for c in q],
                                   'ponto': [round(c, 3) for c in co], 'normal': [round(c, 3) for c in n],
                                   'graus': angulo(n), 'pseudo': angulo(pn) if pn.length > 1e-9 else None,
                                   'facesAte1mm': perto[:10]}, ensure_ascii=False), flush=True)
luva, rig = B.C['bracos'][B.C['ultima']['lado']]
B.maos_rig.posar(rig, f['m'].pose())
B.bpy.context.view_layer.update()
e = f['na'].encaixe
for d in ('indicador', 'medio', 'anelar', 'minimo'):
    pb = rig.pose.bones[f"{d}_2_{B.C['ultima']['lado']}"]
    cabeca, cauda = e @ (pb.head / B.S), e @ (pb.tail / B.S)
    melhor = None
    for k in range(21):
        q = cabeca.lerp(cauda, k / 20)
        co, n, _i, dist = arma.bvh.find_nearest(q)
        if melhor is None or dist < melhor[0]:
            melhor = (dist, k / 20, q, co)
    dist, t, q, co = melhor
    print('EIXO', json.dumps({'dedo': d, 't': t, 'distMM': round(dist, 2), 'eixo': [round(c, 2) for c in q],
                              'ponto': [round(c, 2) for c in co], 'graus': angulo(q - co)}), flush=True)
pb = rig.pose.bones[f"polegar_3_{B.C['ultima']['lado']}"]
cabeca, cauda = e @ (pb.head / B.S), e @ (pb.tail / B.S)
melhor = None
for k in range(21):
    q = cabeca.lerp(cauda, k / 20)
    co, n, _i, dist = arma.bvh.find_nearest(q)
    if melhor is None or dist < melhor[0]:
        melhor = (dist, k / 20, q, co)
B.maos_rig.posar(rig, {})
lugar = L.direcao_do_lugar(f['r']['lateral'])


def ang(a_, b_):
    return round(math.degrees(math.acos(max(-1.0, min(1.0, Vector(a_).normalized().dot(Vector(b_).normalized()))))), 2)


polpa = Vector(pts[B.EPO.Cadeia(f['col'], B.C['mao'], {}).lado_da_polpa].mean(0))
co, n, _i, dd = arma.bvh.find_nearest(polpa)
pn = arma.pseudonormal(co)
faces = []
for c2, n2, i2, d2 in arma.bvh.find_nearest_range(co, 1.0):
    faces.append((round(d2, 3), ang(n2, lugar), [round(c, 3) for c in n2]))
faces.sort()
dist, t, q, co2 = melhor
print('POLEGAR', json.dumps({'polpa': [round(c, 2) for c in polpa], 'distMM': round(dd, 3),
                             'ponto': [round(c, 2) for c in co], 'normal': [round(c, 3) for c in n],
                             'graus': ang(n, lugar), 'pseudo': ang(pn, lugar) if pn.length > 1e-9 else None,
                             'facesAte1mm': faces[:10], 'eixoDistal': {'t': t, 'distMM': round(dist, 2),
                                                                       'graus': ang(q - co2, -lugar)}},
                            ensure_ascii=False), flush=True)
print('LADOS', json.dumps(L.medir(f['col'], na, B.C['mao'], pts, f['r']), ensure_ascii=False), flush=True)
print('FIM', flush=True)
