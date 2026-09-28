# Prova de medida das peças novas da biblioteca (Fase 4.1c; plano em docs/superpowers/plans/2026-09-28-4.1c-glock-m4a4-
# m9.md, Tarefa 4). Roda no Blender sem janela, pelo lançador (`npm run blender -- provar pecas`):
#   blender -b --factory-startup --python-exit-code 1 -P tools/blender/armas/provas_pecas.py
# Cada peça de pecas_superficie.py é construída sozinha, acabada como no construir (chanfro, solda, arestas vivas,
# normais) e medida na malha avaliada — seções por planos, alturas do relevo, sulcos e dentes — contra os números da
# fonte (a MIL-STD-1913 no trilho) ou os pedidos. A linha MASSACRE-PROVAS traz as medidas; qualquer problema reprova
# com código 1 e a lista.
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import pecas as P  # noqa: E402
from armas import pecas_superficie as PS  # noqa: E402
from armas.unidades import S  # noqa: E402

PROBLEMAS = []
MEDIDAS = {}


def conferir(peca, nome, valor, alvo, tolerancia):
    """Guarda a medida e reprova quando sai da tolerância (mm, graus ou contagem)."""
    MEDIDAS.setdefault(peca, {})[nome] = round(valor, 4)
    if abs(valor - alvo) > tolerancia:
        PROBLEMAS.append(f'{peca}: {nome} = {valor:.4f} (alvo {alvo:.4f} ± {tolerancia})')


def _avaliada(ob):
    """bmesh da malha avaliada (com a pilha de modificadores), em mm no mundo."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    ev.to_mesh_clear()
    bm.transform(ob.matrix_world)
    for v in bm.verts:
        v.co /= S
    return bm


def secao(ob, ponto, normal):
    """As arestas do corte da malha avaliada pelo plano (mm): [(a, b)] em Vector."""
    bm = _avaliada(ob)
    r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=Vector(ponto),
                               plane_no=Vector(normal))
    arestas = [(e.verts[0].co.copy(), e.verts[1].co.copy()) for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    bm.free()
    return arestas


def cruzamentos(arestas, eixo_fixo, valor, eixo_medido):
    """Onde as arestas cruzam a linha `eixo_fixo` = valor (eixos 0, 1, 2): os valores do `eixo_medido`, em ordem."""
    out = []
    for a, b in arestas:
        fa, fb = a[eixo_fixo] - valor, b[eixo_fixo] - valor
        if fa == fb or fa * fb > 0:
            continue
        t = fa / (fa - fb)
        out.append(a[eixo_medido] + (b[eixo_medido] - a[eixo_medido]) * t)
    return sorted(out)


# ------------------------------------------------------------------------------------------------ trilho Picatinny
def provar_trilho():
    t = PS.PICATINNY
    x0, x1 = 0.0, 100.0
    trilho, _corte = PS.trilho_picatinny('trilho de prova', x0, x1, None, 'corpo', altura=10.0)
    P.finalizar(trilho.users_collection[0])
    xs = trilho['fendas']
    x_cheio = (xs[0] + xs[1]) / 2  # entre duas fendas: o perfil inteiro
    s = secao(trilho, (x_cheio, 0, 0), (1, 0, 0))
    ys = [p.y for a, b in s for p in (a, b)]
    zs = [p.z for a, b in s for p in (a, b)]
    conferir('picatinny', 'larguraMaxima', max(ys) - min(ys), 0.835 * PS.POL, 0.05)
    conferir('picatinny', 'topo', max(zs), 0.0, 0.01)
    def meia(z):
        c = cruzamentos(s, 2, z, 1)
        return (c[-1] - c[0]) / 2
    conferir('picatinny', 'meiaLargura1mm', meia(-1.0), t['meiaTopo'] + 1.0, 0.05)
    conferir('picatinny', 'meiaLargura2mm', meia(-2.0), t['meiaTopo'] + 2.0, 0.05)
    conferir('picatinny', 'anguloFlancoDeCima', math.degrees(math.atan2(meia(-2.0) - meia(-1.0), 1.0)), 45.0, 0.5)
    conferir('picatinny', 'meiaLargura4_5mm', meia(-4.5), t['meiaMaxima'] - (4.5 - t['patamar'][1]), 0.05)
    conferir('picatinny', 'anguloFlancoDeBaixo', math.degrees(math.atan2(meia(-4.0) - meia(-5.0), 1.0)), 45.0, 0.5)
    conferir('picatinny', 'pescoco', 2 * meia(-7.5), 0.617 * PS.POL, 0.05)
    # As fendas: o corte a 1,5 mm do topo, pelo meio (y = 0): os vãos são as fendas.
    c = cruzamentos(secao(trilho, (0, 0, -1.5), (0, 0, 1)), 1, 0.0, 0)
    vaos = [(c[i], c[i + 1]) for i in range(1, len(c) - 1, 2)]
    conferir('picatinny', 'fendas', len(vaos), len(xs), 0)
    larguras = [b - a for a, b in vaos]
    conferir('picatinny', 'larguraDaFenda', sum(larguras) / len(larguras), 0.206 * PS.POL, 0.05)
    conferir('picatinny', 'larguraDaFendaPior', max(abs(w - 0.206 * PS.POL) for w in larguras), 0.0, 0.05)
    centros = [(a + b) / 2 for a, b in vaos]
    passos = [q - p for p, q in zip(centros, centros[1:])]
    conferir('picatinny', 'passo', sum(passos) / len(passos), 0.394 * PS.POL, 0.02)
    conferir('picatinny', 'passoPior', max(abs(p - 0.394 * PS.POL) for p in passos), 0.0, 0.02)
    fundo = secao(trilho, (xs[2], 0, 0), (1, 0, 0))
    # No meio da fenda o topo do corte é o fundo dela, uma aresta de um flanco ao outro.
    conferir('picatinny', 'fundoDaFenda', -max(p.z for a, b in fundo for p in (a, b)), 0.118 * PS.POL, 0.02)
    # Girado para o lado esquerdo (90°), o topo fica em +Y.
    lado, _c = PS.trilho_picatinny('trilho de prova girado', x0, x1, None, 'corpo', y=15.0, z=3.0, giro=90.0, altura=10.0)
    P.acabar(lado)
    s2 = secao(lado, (x_cheio, 0, 0), (1, 0, 0))
    conferir('picatinny', 'giradoTopoEmY', max(p.y for a, b in s2 for p in (a, b)), 15.0 - 0.0, 0.01)
    conferir('picatinny', 'giradoCentroZ', (max(p.z for a, b in s2 for p in (a, b)) + min(p.z for a, b in s2 for p in (a, b))) / 2, 3.0, 0.02)


# ------------------------------------------------------------------------------------------------ relevo
def _alturas(folha, plano_y):
    bm = _avaliada(folha)
    pts = [(v.co.x, v.co.z, v.co.y - plano_y) for v in bm.verts]
    bm.free()
    return pts


def provar_quadriculado():
    bloco = P.caixa('bloco do quadriculado', (-20, -5, -20), (20, 5, 20), None, 'guarnicao', chanfro=0)
    passo, prof, ang = 1.5, 0.6, 45.0
    folha = PS.relevo('quadriculado de prova', bloco, (-15, 15), (-15, 15), passo / 8,
                      lambda a, b: ((a, 30.0, b), (0, -1, 0)), PS.piramides(passo, prof, ang))
    pts = _alturas(folha, 5.0)
    conferir('quadriculado', 'alturaMaxima', max(h for _a, _b, h in pts), prof, 0.02)
    conferir('quadriculado', 'alturaMinima', min(h for _a, _b, h in pts), 0.0, 0.02)
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    topos = [(a, b) for a, b, h in pts if h > 0.97 * prof]
    desvio = 0.0
    for a, b in topos:
        p = (a * c + b * s) / passo
        q = (-a * s + b * c) / passo
        desvio = max(desvio, abs(p - math.floor(p) - 0.5), abs(q - math.floor(q) - 0.5))
    conferir('quadriculado', 'topoForaDoLugar', desvio, 0.0, 0.07)
    conferir('quadriculado', 'dentroDaRegiao', max(max(abs(a), abs(b)) for a, b, _h in pts), 15.0, 0.01)
    P.iniciar('jogo', 'provas_jogo')
    conferir('quadriculado', 'noModeloDeJogo', 0 if PS.relevo('não nasce', bloco, (-1, 1), (-1, 1), 0.5,
                                                               lambda a, b: ((a, 30.0, b), (0, -1, 0)), PS.piramides(1, 1)) is None else 1, 0, 0)
    P.iniciar('alto', 'provas_alto')


def provar_pontilhado():
    bloco = P.caixa('bloco do pontilhado', (-20, -5, -20), (20, 5, 20), None, 'guarnicao', chanfro=0)
    dens, raio, prof = 1.0, 0.3, 0.15
    folha = PS.relevo('pontilhado de prova', bloco, (-10, 10), (-10, 10), 0.05,
                      lambda a, b: ((a, 30.0, b), (0, -1, 0)), PS.pontilhado(dens, raio, prof))
    pts = _alturas(folha, 5.0)
    conferir('pontilhado', 'alturaMaxima', max(h for _a, _b, h in pts), prof, 0.01)
    # Os grãos: grupos de vértices acima de metade da altura, contados pela grade (vizinhos de 0,05 mm).
    altos = {(round(a / 0.05), round(b / 0.05)) for a, b, h in pts if h > prof * 0.5}
    grupos = 0
    vistos = set()
    for k in altos:
        if k in vistos:
            continue
        grupos += 1
        pilha = [k]
        vistos.add(k)
        while pilha:
            i, j = pilha.pop()
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (i + d[0], j + d[1])
                if n in altos and n not in vistos:
                    vistos.add(n)
                    pilha.append(n)
    conferir('pontilhado', 'graosPorMm2', grupos / 400.0, dens, 0.15 * dens)


# ------------------------------------------------------------------------------------------------ ranhuras e dentes
def provar_ranhuras():
    ferrolho = P.caixa('ferrolho de prova', (-60, -12.5, -15), (0, 12.5, 15), None, 'corpo', chanfro=0.5)
    centros = [-50.0 + 2.6 * i for i in range(9)]
    largura, prof = 1.2, 0.8
    PS.ranhuras('serrilha de prova', ferrolho, centros, largura, prof, (-60, 0), (-10, 10), -12.5, perfil='V')
    P.acabar(ferrolho)
    c = secao(ferrolho, (0, 0, 0), (0, 0, 1))
    # Na face direita (y = -12,5), o fundo de cada sulco em V é um vértice do corte mais para dentro que a face.
    # Só a faixa dos sulcos, longe do chanfro dos cantos da caixa (x = -60 e x = 0).
    fundos = sorted({round(p.x, 3): p for a, b in c for p in (a, b) if -12.45 < p.y < -11.0 and -56.0 < p.x < -4.0}.values(),
                    key=lambda p: p.x)
    conferir('ranhuras', 'sulcos', len(fundos), len(centros), 0)
    if len(fundos) > 1:
        passos = [q.x - p.x for p, q in zip(fundos, fundos[1:])]
        conferir('ranhuras', 'passo', sum(passos) / len(passos), 2.6, 0.02)
        conferir('ranhuras', 'profundidade', max(p.y for p in fundos) + 12.5, prof, 0.02)
    # A boca a 0,05 mm da face: a largura do V naquela profundidade.
    boca = [x for x in cruzamentos([(a, b) for a, b in c if a.y < 0 and b.y < 0], 1, -12.45, 0) if -56.0 < x < -4.0]
    bocas = [q - p for p, q in zip(boca[0::2], boca[1::2]) if q - p < 2.0]
    conferir('ranhuras', 'bocas', len(bocas), len(centros), 0)
    if bocas:
        conferir('ranhuras', 'boca', sum(bocas) / len(bocas), largura * (prof - 0.05) / prof, 0.03)


def provar_dentes():
    pts = PS.dentes([(0.0, 0.0), (50.0, 0.0)], 5.0, 2.0, frente=0.35)
    picos = [p for p in pts if p[1] > 1.99]
    conferir('dentes', 'dentes', len(picos), 10, 0)
    passos = [q[0] - p[0] for p, q in zip(picos, picos[1:])]
    conferir('dentes', 'passo', sum(passos) / len(passos), 5.0, 1e-6)
    conferir('dentes', 'altura', max(p[1] for p in pts), 2.0, 1e-6)
    conferir('dentes', 'nasPontas', abs(pts[0][0]) + abs(pts[-1][0] - 50.0), 0.0, 1e-6)


def provar_lamina():
    estacao = (0.0, 20.0, 19.4, 8.0, 0.0, 5.8, 0.6, 0.3)
    ests = [estacao, (60.0, 20.0, 19.4, 8.0, 0.0, 5.8, 0.6, 0.3), (100.0, 10.0)]
    faca = PS.lamina('lâmina de prova', ests, None, 'corpo')
    P.acabar(faca)
    s = secao(faca, (30, 0, 0), (1, 0, 0))
    def meia(z):
        c = cruzamentos(s, 2, z, 1)
        return (c[-1] - c[0]) / 2
    conferir('gume', 'espessura', 2 * meia(12.0), 5.8, 0.01)
    angulo = 2 * math.degrees(math.atan2(meia(6.0) - meia(2.0), 4.0))
    conferir('gume', 'angulo', angulo, PS.angulo_do_gume(estacao), 0.5)
    conferir('gume', 'anguloPedido', PS.angulo_do_gume(estacao), 2 * math.degrees(math.atan((5.8 - 0.3) / 2 / 8.0)), 1e-9)
    conferir('gume', 'fio', 2 * meia(0.05), 0.3 + (5.8 - 0.3) * 0.05 / 8.0, 0.02)
    bm = _avaliada(faca)
    abertas = sum(1 for e in bm.edges if not e.is_manifold)
    degeneradas = sum(1 for f in bm.faces if f.calc_area() < 1e-6)
    ponta = max(v.co.x for v in bm.verts)
    bm.free()
    conferir('gume', 'bordasAbertas', abertas, 0, 0)
    conferir('gume', 'facesDegeneradas', degeneradas, 0, 0)
    conferir('gume', 'ponta', ponta, 100.0, 1e-4)


def principal():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    P.iniciar('alto', 'provas_alto')
    for prova in (provar_trilho, provar_quadriculado, provar_pontilhado, provar_ranhuras, provar_dentes, provar_lamina):
        try:
            prova()
        except Exception as e:  # uma prova que quebra reprova com o motivo, e as outras continuam
            PROBLEMAS.append(f'{prova.__name__}: {type(e).__name__}: {e}')
    print('MASSACRE-PROVAS', json.dumps({'medidas': MEDIDAS, 'problemas': PROBLEMAS}, ensure_ascii=False))
    if PROBLEMAS:
        print('MASSACRE-REPROVADO', json.dumps(PROBLEMAS, ensure_ascii=False))
        sys.exit(1)


principal()
