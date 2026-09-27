# A mão na arma, do solver de empunhadura (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-
# empunhadura-design.md, seção 6.2): a arma como obstáculo, a luva posta no soquete e os dedos fechando nela.
#  - a arma: as peças do perto (as móveis em repouso) numa BVH em mm; a distância com sinal de um ponto (negativa
#    dentro) pela face mais próxima e a normal dela;
#  - a luva na arma: a luva de jogo pelo modelo das luvas (maos_correcoes.Modelo: o skin e as correções das dobras) na
#    pose, levada pela matriz do encaixe (o referencial da luva — o pulso na origem — no da arma, em mm). A penetração
#    é a dos vértices (a validação da seção 6.3), de um conjunto deles (os de um osso, os de um dedo) ou de todos;
#  - a chegada: a mão aberta (os dedos esticados, no mínimo da AAOS) transladada ao longo de uma direção — a normal da
#    palma, na pega — até os vértices do corpo da mão encostarem (bisseção até 0,02 mm);
#  - os dedos: fechando juntos em volta da arma, como no "autograsp" (Miller e Allen, GraspIt!): a MCP, a PIP e a DIP
#    avançam em passos, a DIP a 2/3 da PIP (o acoplamento natural do dedo); quando uma falange encosta, a junta dela e
#    as de cima param (não podem andar sem empurrar a falange para dentro) e as de baixo seguem; cada toque é achado
#    por bisseção (0,05° na junta que mais anda) e as juntas param nos limites da ficha. Fechar uma junta de cada vez,
#    da base para a ponta, parava o dedo esticado com a ponta na frente do punho e a falange proximal no ar;
#  - o dedo num alvo (o indicador no gatilho): a IK das três juntas mais a abertura pela cinemática da cadeia, e a
#    chegada pela normal do alvo até encostar, como o polegar (empunhadura_polegar.py).
# Unidades: mm e graus além do repouso; o Blender em metros.
import itertools
import math

import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

from . import empunhadura, maos_rig
from .empunhadura import CONTATO_MM, TOLERANCIA_GRAUS
from .maos import DEDOS4
from .maos_capsulas import mm
from .unidades import S

PERTO_DA_ARMA_MM = 6.0  # só os vértices a menos disso da arma entram na conta da penetração (o resto está fora)
PASSO_GRAUS = 3.0  # o passo do fechar em volta da arma (a junta que mais anda)
VELOCIDADES = (1.0, 1.0, 2.0 / 3.0)  # MCP, PIP, DIP: a DIP acompanha 2/3 da PIP
CHEGADA_MM = 40.0  # de onde a palma chega pela normal dela
ACIMA_MM = (4.0, 8.0, 14.0, 20.0)
ALEM = 0.5
GRADE_GRAUS = 10.0
PASSO_INICIAL = 4.0
PASSO_FINAL = 0.25
PESO_NORMAL_MM = 15.0
PESO_ARMA = 5.0
POLPA_T = 0.55


class Arma:
    """A malha de jogo da arma numa BVH em mm (referencial do Blender)."""

    def __init__(self, objetos):
        verts, polys = [], []
        for ob in objetos:
            mw = ob.matrix_world
            base = len(verts)
            verts += [(mw @ v.co) / S for v in ob.data.vertices]
            polys += [[base + i for i in p.vertices] for p in ob.data.polygons]
        self.bvh = BVHTree.FromPolygons(verts, polys)

    def distancia(self, p, limite=None):
        """Distância com sinal (mm) do ponto à superfície, negativa dentro; None além do `limite`."""
        r = self.bvh.find_nearest(p) if limite is None else self.bvh.find_nearest(p, limite)
        if r[0] is None:
            return None
        co, n, _i, d = r
        return -d if (Vector(p) - co).dot(n) < 0.0 else d

    def raio(self, origem, direcao, limite=1000.0):
        """(ponto, normal) da primeira face no raio, ou (None, None)."""
        co, n, _i, _d = self.bvh.ray_cast(origem, direcao, limite)
        return co, n


class NaArma:
    """Uma luva (o Colisor de empunhadura.py) na arma: a matriz do encaixe (mm, luva → arma) e as contas contra ela."""

    def __init__(self, col, arma, encaixe=None):
        self.col, self.arma = col, arma
        self.encaixe = encaixe or Matrix.Identity(4)
        self.por_osso = {}
        for i, dono in enumerate(col.dono):
            self.por_osso.setdefault(dono, []).append(i)

    def vertices(self, ossos):
        return [i for o in ossos for i in self.por_osso.get(o, ())]

    def pontos(self, pose, encaixe=None):
        """As posições (mm, numpy) da luva na pose, no referencial da arma."""
        e = np.array(encaixe or self.encaixe)
        p = self.col.modelo.avaliar(pose)
        return p @ e[:3, :3].T + e[:3, 3]

    def penetracao(self, pts, indices=None):
        """A maior entrada (mm, ≥ 0) dos vértices `indices` (todos, sem eles) na arma."""
        pior = 0.0
        for i in range(len(pts)) if indices is None else indices:
            d = self.arma.distancia(pts[i], PERTO_DA_ARMA_MM)
            if d is not None and -d > pior:
                pior = -d
        return pior

    def entrada_quadrada(self, pts, indices):
        """A soma dos quadrados das entradas (mm) dos vértices `indices` na arma: a conta suave da penetração, para as
        buscas."""
        soma = 0.0
        for i in indices:
            d = self.arma.distancia(pts[i], PERTO_DA_ARMA_MM)
            if d is not None and d < 0.0:
                soma += d * d
        return soma

    def encosto(self, pts, indices):
        """A menor distância (mm) dos vértices `indices` à superfície da arma (negativa: dentro)."""
        return min(self.arma.distancia(pts[i]) for i in indices)


def mao_aberta(mao, polegar):
    """A mão aberta para chegar na arma: os quatro dedos no mínimo da AAOS (esticados, sem abrir) e o polegar da pose
    `polegar` (afastado)."""
    lim, rep = mao.f['limites'], mao.rep
    m = polegar
    for d in DEDOS4:
        for i, j in ((1, 'mcp'), (2, 'pip'), (3, 'dip')):
            m = m.com(f'{d}_{i}', flexao=lim[j][0] - rep[j])
    return m


def encostar(na, m, direcao, encaixe, indices=None, chegada=CHEGADA_MM, alcance=None):
    """O encaixe transladado ao longo de `direcao` (unitária, no referencial da arma) do ponto de chegada, `chegada` mm
    para trás, até a luva na pose `m` (os vértices `indices`, ou todos) encostar na arma. Devolve (encaixe, quanto
    andou além do encaixe dado, em mm)."""
    pose = m.pose()
    p0 = na.pontos(pose, encaixe)

    def em(d):
        t = Matrix.Translation(direcao * (d - chegada))
        return t @ encaixe

    def cruza(d):
        desloc = np.array(direcao * (d - chegada))
        return na.penetracao(p0 + desloc, indices) > CONTATO_MM

    if cruza(0.0):
        raise RuntimeError(f'a mão cruza a arma já {chegada} mm antes do ponto de chegada')
    a, b = 0.0, chegada + (chegada if alcance is None else alcance)
    if not cruza(b):
        raise RuntimeError(f"a mão não encosta na arma em {b} mm de chegada")
    while b - a > 0.02:
        c = (a + b) / 2
        if cruza(c):
            b = c
        else:
            a = c
    return em(a), a - chegada


def agarrar(na, mao, m, dedo):
    """O dedo fechando em volta da arma (ver o cabeçalho) a partir da pose `m`. Uma falange encosta quando entra na arma
    mais que o contato além do que já entrava no começo (o dedo esticado da mão aberta pode começar raspando numa
    peça); só contam as falanges que alguma junta ativa ainda move. Devolve (pose, {osso: 'contato' | 'limite'})."""
    lim, rep = mao.f['limites'], mao.rep
    ossos = [f'{dedo}_{i}' for i in (1, 2, 3)]
    maximo = {ossos[0]: lim['mcp'][1] - rep['mcp'], ossos[1]: lim['pip'][1] - rep['pip'],
              ossos[2]: lim['dip'][1] - rep['dip']}
    segmentos = [na.vertices([o]) for o in ossos]
    pts0 = na.pontos(m.pose())
    base = [na.penetracao(pts0, s) for s in segmentos]
    ativos = [True, True, True]
    parou = {}

    def com_passo(de, s):
        r = de
        for k, osso in enumerate(ossos):
            if ativos[k]:
                r = r.com(osso, flexao=min(de.flexao.get(osso, 0.0) + s * VELOCIDADES[k], maximo[osso]))
        return r

    def encostados(pose_m):
        pts = na.pontos(pose_m.pose())
        movidos = [k for k in range(3) if any(ativos[:k + 1])]
        return [k for k in movidos if na.penetracao(pts, segmentos[k]) > base[k] + CONTATO_MM]

    while any(ativos):
        for k, osso in enumerate(ossos):
            if ativos[k] and m.flexao.get(osso, 0.0) >= maximo[osso] - 1e-6:
                ativos[k] = False
                parou[osso] = 'limite'
        if not any(ativos):
            break
        tentativa = com_passo(m, PASSO_GRAUS)
        tocam = encostados(tentativa)
        if not tocam:
            m = tentativa
            continue
        a, b = 0.0, PASSO_GRAUS
        while b - a > TOLERANCIA_GRAUS:
            c = (a + b) / 2
            if encostados(com_passo(m, c)):
                b = c
            else:
                a = c
        m = com_passo(m, a)
        # a falange mais perto da base que encostou: a junta dela e as de cima param (sempre há uma ativa entre elas,
        # pela conta de `encostados`, então cada volta para pelo menos uma junta)
        k = min(encostados(com_passo(m, b - a)) or tocam)
        for j in range(k + 1):
            if ativos[j]:
                ativos[j] = False
                parou[ossos[j]] = 'contato'
    return m, parou


class CadeiaDedo:
    """A cadeia de um dedo (as três falanges) para a IK: as matrizes de repouso (mm) relativas, a mão posada (a matriz do
    pai da falange proximal, no referencial da arma) e a polpa no referencial do osso distal."""

    def __init__(self, na, dedo, pose_mao):
        col = na.col
        rig, lado = col.rig, col.lado
        self.dedo = dedo
        self.ossos = [f'{dedo}_{i}' for i in (1, 2, 3)]
        bs = [rig.data.bones[f'{o}_{lado}'] for o in self.ossos]
        rep = [mm(b.matrix_local) for b in bs]
        pai = bs[0].parent
        self.rel = [mm(pai.matrix_local).inverted() @ rep[0], rep[0].inverted() @ rep[1], rep[1].inverted() @ rep[2]]
        self.comp = [b.length / S for b in bs]
        maos_rig.posar(rig, pose_mao)
        self.pai = na.encaixe @ mm(rig.pose.bones[pai.name].matrix)
        maos_rig.posar(rig, {})
        # a polpa de repouso: do osso distal a 55 %, pelo lado da palma (+Z do osso), até a superfície da luva
        pts = col.modelo.pontos({})
        bvh = BVHTree.FromPolygons([tuple(p) for p in pts], col.tris)
        m3 = rep[2]
        dentro = m3 @ Vector((0.0, self.comp[2] * POLPA_T, 0.0))
        lado_polpa = (m3.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        co, _n, _i, _d = bvh.ray_cast(dentro, lado_polpa)
        self.polpa = m3.inverted() @ co
        para_local = m3.inverted()
        self.lado_da_polpa = [i for i, dono in enumerate(col.dono)
                              if dono == self.ossos[2] and (para_local @ pts[i]).z > 0.0]

    def matrizes(self, g):
        """As matrizes (mm, na arma) das três falanges com g = {'abertura', 'mcp', 'pip', 'dip'} além do repouso."""
        q = [empunhadura._flexao(g['mcp']) @ empunhadura._abertura(g['abertura']), empunhadura._flexao(g['pip']),
             empunhadura._flexao(g['dip'])]
        m, ms = self.pai, []
        for rel, qi in zip(self.rel, q):
            m = m @ rel @ qi.to_matrix().to_4x4()
            ms.append(m)
        return ms

    def polpa_em(self, g):
        m = self.matrizes(g)[2]
        return m @ self.polpa, (m.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()


GRAUS_DO_DEDO = ('abertura', 'mcp', 'pip', 'dip')


def limites_do_dedo(mao, abertura):
    lim, rep = mao.f['limites'], mao.rep
    return {'abertura': (-abertura, abertura), 'mcp': (lim['mcp'][0] - rep['mcp'], lim['mcp'][1] - rep['mcp']),
            'pip': (lim['pip'][0] - rep['pip'], lim['pip'][1] - rep['pip']),
            'dip': (lim['dip'][0] - rep['dip'], lim['dip'][1] - rep['dip'])}


def _eixo(cadeia, ms):
    """Os pontos do eixo das falanges (5 por osso): a conta rápida da entrada do dedo na arma, na IK."""
    pts = []
    for m, c in zip(ms, cadeia.comp):
        for t in (0.1, 0.3, 0.5, 0.7, 0.9):
            pts.append(m @ Vector((0.0, c * t, 0.0)))
    return pts


def _custo_dedo(cadeia, arma, g, alvo, normal, raio_mm):
    ms = cadeia.matrizes(g)
    p, lado = cadeia.polpa_em(g)
    entra = 0.0
    for q in _eixo(cadeia, ms):
        d = arma.distancia(q, raio_mm + 4.0)
        if d is not None and d < raio_mm:
            entra += (raio_mm - d) ** 2
    return (p - alvo).length_squared + (PESO_NORMAL_MM * (1.0 + lado.dot(normal))) ** 2 + PESO_ARMA ** 2 * entra


def ik_dedo(cadeia, arma, alvo, normal, lim, raio_mm, inicio=None):
    """Os graus do dedo (além do repouso) que põem a polpa no alvo, de frente para ele e com as falanges fora da arma
    (o eixo a `raio_mm` da superfície): a grade de 10° e a busca de padrão até 0,25° (só a busca, a partir de
    `inicio`)."""
    def valores(a, b):
        n = max(1, math.ceil((b - a) / GRADE_GRAUS))
        return [a + (b - a) * k / n for k in range(n + 1)]

    if inicio is not None:
        melhor = dict(inicio)
        custo = _custo_dedo(cadeia, arma, melhor, alvo, normal, raio_mm)
    else:
        melhor, custo = None, math.inf
        for comb in itertools.product(*(valores(*lim[k]) for k in GRAUS_DO_DEDO)):
            g = dict(zip(GRAUS_DO_DEDO, comb))
            c = _custo_dedo(cadeia, arma, g, alvo, normal, raio_mm)
            if c < custo:
                melhor, custo = g, c
    passo = PASSO_INICIAL
    while passo >= PASSO_FINAL:
        melhorou = False
        for grau in GRAUS_DO_DEDO:
            for s in (1.0, -1.0):
                g = dict(melhor)
                g[grau] = min(max(g[grau] + s * passo, lim[grau][0]), lim[grau][1])
                c = _custo_dedo(cadeia, arma, g, alvo, normal, raio_mm)
                if c < custo - 1e-9:
                    melhor, custo, melhorou = g, c, True
        if not melhorou:
            passo /= 2
    return melhor


def _com_dedo(m, dedo, g):
    return (m.com(f'{dedo}_1', flexao=g['mcp'], abertura=g['abertura']).com(f'{dedo}_2', flexao=g['pip'])
            .com(f'{dedo}_3', flexao=g['dip']))


def dedo_no_alvo(na, mao, m, dedo, alvo, normal, abertura_max, raio_mm, folga=None):
    """O dedo com a polpa no alvo (a normal para fora da superfície), chegando pela normal até encostar na arma.
    `folga(pts)`, se vier, é uma conta extra (mm) que tem de ficar ≥ 0 no caminho (o guarda-mato). Devolve (pose,
    relatório)."""
    lim = limites_do_dedo(mao, abertura_max)
    cadeia = CadeiaDedo(na, dedo, m.pose())
    ik = ik_dedo(cadeia, na.arma, alvo, normal, lim, raio_mm)
    dedo_v = na.vertices(cadeia.ossos)

    def cruza(g):
        pts = na.pontos(_com_dedo(m, dedo, g).pose())
        if na.penetracao(pts, dedo_v) > CONTATO_MM:
            return True
        return folga is not None and folga(pts) < 0.0

    for acima in ACIMA_MM:
        de = ik_dedo(cadeia, na.arma, alvo + normal * acima, normal, lim, raio_mm, inicio=ik)
        if not cruza(de):
            break
    else:
        raise RuntimeError(f'o {dedo} cruza a arma mesmo com a polpa {ACIMA_MM[-1]} mm acima do alvo')

    def em(s):
        return {k: min(max(de[k] + (ik[k] - de[k]) * s, lim[k][0]), lim[k][1]) for k in GRAUS_DO_DEDO}

    anda = max(abs(ik[k] - de[k]) for k in GRAUS_DO_DEDO)
    tol = TOLERANCIA_GRAUS / max(anda, 1e-6)
    a, b = 0.0, 1.0 + ALEM
    if cruza(em(b)):
        while b - a > tol:
            s = (a + b) / 2
            if cruza(em(s)):
                b = s
            else:
                a = s
        encostou = True
    else:
        a, encostou = b, False
    g = em(a)
    m = _com_dedo(m, dedo, g)
    pts = na.pontos(m.pose())
    polpa, _lado = cadeia.polpa_em(g)
    rel = {'graus': {k: round(v, 2) for k, v in g.items()}, 'encostou': encostou, 'chegouDeMM': acima,
           'polpaEncostaMM': round(na.encosto(pts, cadeia.lado_da_polpa), 2),
           'polpaAoAlvoMM': round((polpa - alvo).length, 2)}
    return m, rel, cadeia
