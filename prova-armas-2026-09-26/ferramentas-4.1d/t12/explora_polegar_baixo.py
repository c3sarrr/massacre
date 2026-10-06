# Tarefa 12 (a regra lateral): onde o polegar da mão de apoio consegue encostar por baixo do bloco do guarda-mão da AWP,
# numa pega da prova (provas_lateral.py) — a mão chega e fecha os dedos pelo caminho da pega, com o polegar parado no
# afastado (a espera da pega, sem resolver o polegar), e a grade dos seis graus do polegar (além do repouso) é varrida:
# para cada pose, a polpa (o ponto mais perto da arma, a distância e a normal da arma embaixo dele) e, nas que encostam
# por baixo (a normal a até 45° do −Z e a até 3 mm), se a pose cruza a arma ou a mão (o _cruza do solver). Imprime as
# melhores (sem cruzar, a polpa mais perto, por baixo) e a direção da falange distal delas. Só leitura: nada gravado.
#   blender -b --factory-startup -P explora_polegar_baixo.py -- <contexto das luvas> <altura>,<inclinação>,<girada>[,<guinada>]
import copy
import itertools
import json
import math
import os
import sys
import time

sys.path.insert(0, 'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender')

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import (empunhadura, empunhadura_arma as EA, empunhadura_pega,  # noqa: E402
                   empunhadura_polegar as polegar, empunhadura_regras as regras, pecas as P)

LARGURA, ALTURA, COMPRIMENTO, CHANFRO = 54.0, 56.0, 300.0, 3.0


def bloco():
    colecao = P.iniciar('jogo', 'bloco_lateral')
    mat = bpy.data.materials.new('bloco')
    corpo = P.caixa('guarda_mao', (-COMPRIMENTO / 2, -LARGURA / 2, -ALTURA / 2),
                    (COMPRIMENTO / 2, LARGURA / 2, ALTURA / 2), mat, 'corpo', chanfro=CHANFRO)
    P.finalizar(colecao)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(corpo.evaluated_get(dg))
    corpo.modifiers.clear()
    corpo.data = me
    return corpo


def principal():
    args = sys.argv[sys.argv.index('--') + 1:]
    with open(args[0], encoding='utf-8') as f:
        ctx = json.load(f)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    colecao = bpy.data.collections.new('prova_lateral')
    bpy.context.scene.collection.children.link(colecao)
    mao, bracos = empunhadura_pega.montar_luvas({'luvas': ctx}, colecao)
    corpo = bloco()
    soquete = bpy.data.objects.new('soquete_mao_e', None)
    colecao.objects.link(soquete)
    arma = EA.Arma([corpo])
    contexto = (mao, bracos, [corpo], arma, EA.Arma([corpo]), {'mao_e': soquete}, {'base': corpo}, {})
    for pega in args[1:]:
        explorar(mao, contexto, arma, pega)


def explorar(mao, contexto, arma, pega):
    v = [float(x) for x in pega.split(',')] + [0.0]
    altura, inclinacao, girada, guinada = v[:4]
    lim = polegar.limites(mao)
    regra = copy.deepcopy(regras.LATERAL)
    regra['ancora'] = dict(regra['ancora'], mm=(0.0, 0.0, altura))
    regra['giros'] = (('X', inclinacao), ('Y', girada), ('Z', guinada))
    # o polegar parado no afastado (a espera da pega): a palma chega e os dedos fecham sem resolver o polegar
    espera = {'abducao': lim['abducao'][0], 'cmc': lim['cmc'][0], 'rotacao': 0.0, 'mcp': lim['mcp'][0], 'ip': lim['ip'][0]}
    regra['polegar'] = {'sobre_luva': True, 'espera': espera}
    regra.pop('polegar_afastado', None)
    t0 = time.time()
    f = empunhadura_pega._uma_mao(contexto, 'e', regra, {})
    col, m = f['col'], f['m']
    na = EA.NaArma(col, arma, f['na'].encaixe, ceder=False)
    cadeia = polegar.Cadeia(col, mao, {o: q for o, q in m.pose().items() if not o.startswith('polegar')})
    livre, resto = polegar._livre_e_resto(col)
    polpa = cadeia.lado_da_polpa
    print('pega', pega, 'a mão em', round(time.time() - t0, 1), 's; os limites', lim, flush=True)
    grade = {k: np.linspace(lim[k][0], lim[k][1], n) for k, n in
             (('abducao', 6), ('cmc', 4), ('rotacao', 2), ('mcp', 5), ('ip', 5), ('desvio', 3))}
    candidatas = []
    vistas = 0
    t0 = time.time()
    # onde fica a base do polegar (a cabeça da proximal, a MCP, e a do metacarpo, a CMC) no referencial do bloco
    base = na.pontos(m.pose())
    for osso in ('polegar_1', 'polegar_2', 'polegar_3'):
        idx = na.vertices([osso])
        c = base[idx].mean(0)
        print(f'  {osso}: o centro dos vértices em {tuple(round(x, 1) for x in c)} (mm, no bloco)')
    por_baixo, cruzam, melhor, menos = 0, 0, (1e9, None), (1e9, 0.0, 0.0, 0.0, None)
    for valores in itertools.product(*grade.values()):
        g = dict(zip(grade.keys(), (float(x) for x in valores)))
        mm = polegar._com_graus(m, cadeia, g)
        pts = na.pontos(mm.pose())
        dist = {i: na.arma.distancia(pts[i]) for i in polpa}
        i = min(dist, key=dist.get)
        vistas += 1
        _co, n, _k, _d = na.arma.bvh.find_nearest(Vector(pts[i]))
        embaixo = n.angle(Vector((0.0, 0.0, -1.0))) <= math.radians(45.0)
        if embaixo and dist[i] < melhor[0]:
            melhor = (dist[i], g)
        if dist[i] > 3.0 or not embaixo:
            continue
        por_baixo += 1
        if polegar._cruza(col, mm, livre, resto, na):
            cruzam += 1
            # o que cruza: a arma (o polegar e a tenar dentro do bloco) ou a mão (as falanges livres na luva, a dobra)
            na_arma = na.penetracao(pts, na.vertices(list(polegar.LIVRE + polegar.TENAR)))
            na_mao = max(col.profundidade(mm.pose(), livre, resto, empunhadura.PERTO_MM),
                         polegar.dobra_da_tenar(col, pts))
            if max(na_arma, na_mao) < menos[0]:
                menos = (max(na_arma, na_mao), na_arma, na_mao, dist[i], g)
            continue
        ms = cadeia.matrizes(g)
        distal = (na.encaixe.to_3x3() @ (ms[2].to_3x3() @ Vector((0.0, 1.0, 0.0)))).normalized()
        candidatas.append((dist[i], g, tuple(round(c, 1) for c in pts[i]), tuple(round(c, 2) for c in distal)))
    candidatas.sort(key=lambda c: c[0])
    print('vistas', vistas, 'candidatas (polpa por baixo, sem cruzar)', len(candidatas), round(time.time() - t0, 1), 's')
    print('  por baixo a até 3 mm:', por_baixo, '; delas cruzam:', cruzam, '; a polpa mais perto por baixo (com ou sem '
          'cruzar):', round(melhor[0], 2), 'mm, graus', {k: round(x, 1) for k, x in (melhor[1] or {}).items()})
    print('  a que menos cruza: a arma', round(menos[1], 2), 'mm, a mão', round(menos[2], 2), 'mm; a polpa a',
          round(menos[3], 2), 'mm; graus', {k: round(x, 1) for k, x in (menos[4] or {}).items()})
    for d, g, p, distal in candidatas[:15]:
        print(f'  polpa a {d:.2f} mm em {p}; a distal aponta {distal}; graus {({k: round(x, 1) for k, x in g.items()})}')


principal()
