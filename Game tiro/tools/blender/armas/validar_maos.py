# Validação do rig das luvas nas poses de teste (Fase 4.1b; desenho em
# docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 4; plano, Tarefa 5, Passo 4): em cada pose
# (o repouso; o punho fechado, o apontar e a mesa de empunhadura.poses_de_teste, fechados até o contato; a mão aberta e o
# pulso a 60°) e em cada junta sozinha no limite da AAOS — as PIP, as DIP, as do polegar e o pulso; as MCP dobram juntas
# na mesa, porque uma MCP no fim com a vizinha esticada não existe (os tendões do médio, do anelar e do mínimo são
# ligados) —, a malha deformada pelo modelo das luvas (o skin e as correções das dobras, maos_correcoes.Modelo — o
# mesmo do shader do jogo) é conferida:
#  - nenhuma junta afina mais de 30 %: a espessura mínima da seção no anel do meio da junta (os vértices com os dois
#    ossos da junta entre 35 % e 65 %), medida em todas as direções perpendiculares à junta, pose sobre repouso; a
#    parede do punho (o forro até a face de fora) também;
#  - a malha não atravessa a si mesma mais de 0,3 mm: os pares de triângulos que se cruzam (fora os de uma mesma peça,
#    os da peça com a pegada dela e os de duas peças empilhadas desde o repouso), cada par com a penetração do vértice
#    mais fundo na superfície em volta do outro (maos_contato.py). A pegada de uma peça é onde ela se assenta: os
#    triângulos da luva que ela cruza no repouso (as paredes descem 0,2 mm para dentro) e os vizinhos deles, e os que
#    ficam a até 1,5 mm dos vértices dela;
#  - as peças de reforço continuam assentadas: a base das paredes delas a 0,2 ± 0,3 mm dentro da luva.
import math

import numpy as np
from mathutils import Quaternion
from mathutils.bvhtree import BVHTree

from . import maos_contato, maos_correcoes, maos_rig
from .maos import DEDOS4, METACARPO
from .unidades import S

AFINAMENTO_MAXIMO = 0.30
ATRAVESSA_MM = 0.3
ASSENTO_MM = 0.3
PEGADA_MM = 1.5  # os triângulos da luva a até 1,5 mm de uma peça em repouso são a pegada dela (onde ela se assenta)


def _componentes(n_tris, tris):
    """Componente conexa (pelos vértices) de cada triângulo."""
    pai = list(range(n_tris))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    dono = {}
    for k, t in enumerate(tris):
        for v in t:
            if v in dono:
                a, b = raiz(k), raiz(dono[v])
                if a != b:
                    pai[a] = b
            else:
                dono[v] = k
    return [raiz(k) for k in range(n_tris)]


class Topologia:
    """O que não muda entre as poses: os triângulos, as peças (componentes do reforço) e a pegada de cada uma, os anéis
    das juntas, a base das paredes das peças e o forro do punho."""

    def __init__(self, luva, reforco):
        me = luva.data
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.sup = maos_contato.Superficie(self.tris)
        poly = [t.polygon_index for t in me.loop_triangles]
        mats = np.empty(len(me.polygons), np.int32)
        me.polygons.foreach_get('material_index', mats)
        at = me.attributes.get('forro')
        forro = np.zeros(len(me.polygons), np.int32)
        if at is not None:
            at.data.foreach_get('value', forro)
        de_peca = [mats[p] == reforco for p in poly]
        comp = _componentes(nt, self.tris)
        self.peca = [comp[k] if de_peca[k] else -1 for k in range(nt)]
        self.base = [k for k in range(nt) if not de_peca[k]]
        self.fora = [k for k in self.base if not forro[poly[k]]]
        # a pegada de cada peça e as peças empilhadas (ver o cabeçalho)
        pts = [v.co / S for v in me.vertices]
        bvh_base = BVHTree.FromPolygons(pts, [self.tris[k] for k in self.base])
        self.pegada = {}
        for k in range(nt):
            if self.peca[k] >= 0:
                s = self.pegada.setdefault(self.peca[k], set())
                for v in self.tris[k]:
                    for *_r, j, _d in bvh_base.find_nearest_range(pts[v], PEGADA_MM):
                        s.add(self.base[j])
        tris_do_vertice = [[] for _ in me.vertices]
        for k, t in enumerate(self.tris):
            for v in t:
                tris_do_vertice[v].append(k)
        self.empilhadas = set()
        bvh = BVHTree.FromPolygons(pts, self.tris)
        for a, b in bvh.overlap(bvh):
            pa, pb = self.peca[a], self.peca[b]
            if pa >= 0 and pb >= 0 and pa != pb:
                self.empilhadas.add((pa, pb))
            elif pa >= 0 and pb < 0:
                self.pegada[pa].update(j for v in self.tris[b] for j in tris_do_vertice[v] if self.peca[j] < 0)
        # o forro: vértices só de faces do forro
        faces_do_vertice = [set() for _ in me.vertices]
        for p in me.polygons:
            for v in p.vertices:
                faces_do_vertice[v].add(bool(forro[p.index]))
        self.forro = [i for i, s in enumerate(faces_do_vertice) if s == {True}]
        self.juntas = _juntas(luva)
        at = me.attributes.get('assento')
        valores = [0.0] * len(me.vertices)
        if at is not None:
            at.data.foreach_get('value', valores)
        self.assento = [i for i, v in enumerate(valores) if v > 0.5]


def _juntas(luva):
    """{nome da junta: índices dos vértices do anel do meio dela} pelos pesos (os dois ossos entre 35 % e 65 %)."""
    nomes = {g.index: g.name[:-2] for g in luva.vertex_groups}
    pares = {'pulso': ('torcao', 'mao')}
    for d in DEDOS4:
        pares[f'{d}_mcp'] = (METACARPO.get(d, 'mao'), f'{d}_1')
        pares[f'{d}_pip'] = (f'{d}_1', f'{d}_2')
        pares[f'{d}_dip'] = (f'{d}_2', f'{d}_3')
    pares['polegar_mcp'] = ('polegar_1', 'polegar_2')
    pares['polegar_ip'] = ('polegar_2', 'polegar_3')
    aneis = {j: [] for j in pares}
    for v in luva.data.vertices:
        w = {nomes[g.group]: g.weight for g in v.groups}
        for j, (a, b) in pares.items():
            if 0.35 <= w.get(a, 0.0) <= 0.65 and 0.35 <= w.get(b, 0.0) <= 0.65:
                aneis[j].append(v.index)
    return {j: idx for j, idx in aneis.items() if len(idx) >= 6}


def _espessura_minima(pts):
    """A menor largura do conjunto de pontos entre as direções perpendiculares ao eixo principal dele (o anel da junta
    fica num plano; o eixo é a normal desse plano, pela menor variância)."""
    a = np.array([tuple(p) for p in pts])
    a -= a.mean(0)
    _, _, vt = np.linalg.svd(a, full_matrices=False)
    u, v = vt[0], vt[1]
    menor = math.inf
    for k in range(90):
        th = math.pi * k / 90
        d = u * math.cos(th) + v * math.sin(th)
        proj = a @ d
        menor = min(menor, proj.max() - proj.min())
    return menor


def atravessa(pts, topo):
    """(a maior penetração da malha nela mesma em mm, o ponto) — ver o cabeçalho."""
    tris = topo.tris
    medidor = maos_contato.Medidor(topo.sup, pts)
    pior, onde = 0.0, None
    for a, b in maos_contato.pares(pts, tris, list(range(len(tris)))):
        ta, tb = tris[a], tris[b]
        pa, pb = topo.peca[a], topo.peca[b]
        if pa >= 0 and (pa == pb or (pb < 0 and b in topo.pegada[pa]) or (pa, pb) in topo.empilhadas):
            continue
        if pb >= 0 and pa < 0 and a in topo.pegada[pb]:
            continue
        d = medidor.par(a, b)
        if d > pior:
            pior, onde = d, (pts[ta[0]] + pts[tb[0]]) / 2
    return pior, onde


def _assentamento(pts, topo):
    """O maior desvio (mm) da base das paredes das peças em relação aos 0,2 mm dentro da luva, na pose."""
    if not topo.assento:
        return 0.0
    bvh = BVHTree.FromPolygons(pts, [topo.tris[k] for k in topo.base])
    return max(abs(bvh.find_nearest(pts[i])[3] - 0.2) for i in topo.assento)


def _parede_do_punho(pts, topo):
    """As distâncias (mm) de cada vértice do forro à face de fora da luva."""
    bvh = BVHTree.FromPolygons(pts, [topo.tris[k] for k in topo.fora])
    return np.array([bvh.find_nearest(pts[i])[3] for i in topo.forro])


class _Repouso:
    def __init__(self, modelo, topo):
        pts = modelo.pontos({})
        self.espessuras = {j: _espessura_minima([pts[i] for i in idx]) for j, idx in topo.juntas.items()}
        self.parede = _parede_do_punho(pts, topo) if topo.forro else None


def conferir_pose(modelo, topo, repouso, nome, pose, juntas=None):
    """{juntas: razão da espessura, pior junta, parede do punho, atravessa, assentamento} de uma pose e os problemas."""
    pts = modelo.pontos(pose)
    aneis = {j: idx for j, idx in topo.juntas.items() if juntas is None or j in juntas}
    razoes = {j: round(_espessura_minima([pts[i] for i in idx]) / repouso.espessuras[j], 4) for j, idx in aneis.items()}
    prof, onde = atravessa(pts, topo)
    assento = _assentamento(pts, topo)
    rel = {'juntas': razoes, 'atravessaMM': round(prof, 3), 'assentamentoMM': round(assento, 3)}
    problemas = []
    if razoes:
        pior = min(razoes, key=razoes.get)
        rel['piorJunta'] = [pior, razoes[pior]]
        if razoes[pior] < 1 - AFINAMENTO_MAXIMO:
            problemas.append(f'pose {nome}: a junta {pior} afina {(1 - razoes[pior]) * 100:.1f} % (máximo 30 %)')
    if repouso.parede is not None:
        parede = float((_parede_do_punho(pts, topo) / np.maximum(repouso.parede, 1e-6)).min())
        rel['paredeDoPunho'] = round(parede, 4)
        if parede < 1 - AFINAMENTO_MAXIMO:
            problemas.append(f'pose {nome}: a parede do punho afina {(1 - parede) * 100:.1f} % (máximo 30 %)')
    if onde is not None:
        rel['ondeAtravessa'] = [round(c, 2) for c in onde]
    if prof > ATRAVESSA_MM:
        problemas.append(f'pose {nome}: a luva atravessa a si mesma {prof:.2f} mm (máximo {ATRAVESSA_MM} mm)')
    if assento > ASSENTO_MM:
        problemas.append(f'pose {nome}: uma peça sai do assento {assento:.2f} mm (máximo {ASSENTO_MM} mm)')
    return rel, problemas


def validar_poses(luva, rig, mao, reforco, poses):
    """As poses de teste ({nome: pose}) e cada junta de flexão sozinha no limite da AAOS: (relatório, problemas)."""
    topo = Topologia(luva, reforco)
    modelo = maos_correcoes.Modelo(luva, rig, mao, reforco)
    repouso = _Repouso(modelo, topo)
    rel, problemas = {}, []
    for nome, pose in poses.items():
        rel[nome], p = conferir_pose(modelo, topo, repouso, nome, pose)
        problemas += p
    no_limite = {}
    for junta, osso, _rep, maximo, _meia, _alcance in maos_correcoes.juntas(mao):
        if junta.endswith('_mcp') and not junta.startswith('polegar'):
            continue
        r, p = conferir_pose(modelo, topo, repouso, f'{junta} no limite',
                             {osso: Quaternion((1.0, 0.0, 0.0), math.radians(maximo))}, juntas={junta})
        no_limite[junta] = {k: r[k] for k in ('atravessaMM', 'assentamentoMM') if k in r}
        no_limite[junta]['espessura'] = r['juntas'].get(junta)
        problemas += p
    rel['juntasNoLimite'] = no_limite
    maos_rig.posar(rig, {})
    return rel, problemas


def conferir_uma(modelo, luva, reforco, nome, pose):
    """Uma pose avulsa (a pega das armas, empunhadura_pega.py) nas mesmas contas das poses de teste: (relatório,
    problemas)."""
    topo = Topologia(luva, reforco)
    return conferir_pose(modelo, topo, _Repouso(modelo, topo), nome, pose)
