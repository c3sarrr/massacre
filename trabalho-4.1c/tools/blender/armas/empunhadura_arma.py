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
#  - os dedos juntos (a mão da frente, `juntar_dedos`): o de fora gira na MCP para o vizinho e fecha de novo, até os
#    dois se encostarem lado a lado; `folgas_entre_dedos` mede o que sobra entre eles (a validação da pega);
#  - o dedo num alvo (o indicador no gatilho): a IK das três juntas mais a abertura pela cinemática da cadeia, e a
#    chegada pela normal do alvo até encostar, como o polegar (empunhadura_polegar.py).
# Unidades: mm e graus além do repouso; o Blender em metros.
import itertools
import math

import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

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
# os dedos juntos: o de fora e o vizinho para onde ele gira, a partir do médio; a bisseção da abertura
JUNTAR = (('anelar', 'medio'), ('minimo', 'anelar'), ('indicador', 'medio'))
PASSO_JUNTAR_GRAUS = 0.25
JUNTAR_ATRAVESSA_MM = 0.15  # metade do limite da validação da luva (0,3 mm), com folga
PARES_VIZINHOS = (('indicador', 'medio'), ('medio', 'anelar'), ('anelar', 'minimo'))
QUINA_MM = 1e-3  # as faces em volta do ponto mais perto da arma (a pseudonormal de Arma.distancia)
# a paridade dos cruzamentos (Arma.distancia): três direções oblíquas, longe dos eixos das faces retas da arma
RAIOS_DA_PARIDADE = tuple(Vector(v).normalized() for v in ((0.36, 0.48, 0.8), (-0.6, 0.64, -0.48), (0.8, -0.36, -0.48)))


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
        """Distância com sinal (mm) do ponto à superfície, negativa dentro; None além do `limite`. O sinal sai da normal
        da face mais perto; mais longe que PERTO_DA_ARMA_MM (só sem o limite das buscas: a validação), de três votos —
        ela, a pseudonormal (a média das normais das faces em volta do ponto mais perto) e a paridade dos raios —, que
        erram em casos diferentes: a face, perto de uma quina (a do outro lado dela: o antebraço da mão da frente,
        24 mm abaixo de um friso do anel delta da M4A4, saía 24 mm dentro); a média, numa ponta fina; a paridade, nas
        peças que se sobrepõem (o cano dentro do guarda-mão)."""
        r = self.bvh.find_nearest(p) if limite is None else self.bvh.find_nearest(p, limite)
        if r[0] is None:
            return None
        co, n, _i, d = r
        para_fora = Vector(p) - co
        dentro = para_fora.dot(n) < 0.0
        if d > PERTO_DA_ARMA_MM:
            media = sum((f[1] for f in self.bvh.find_nearest_range(co, QUINA_MM)), Vector())
            pela_media = para_fora.dot(media) < 0.0 if media.length > 1e-9 else dentro
            dentro = dentro + pela_media + self._impar(p) >= 2
        return -d if dentro else d

    def _impar(self, p):
        """Se a maioria dos raios de RAIOS_DA_PARIDADE que saem do ponto cruza a malha um número ímpar de vezes."""
        impares = 0
        for direcao in RAIOS_DA_PARIDADE:
            k, o = 0, Vector(p)
            while k < 256:
                co = self.bvh.ray_cast(o, direcao)[0]
                if co is None:
                    break
                k += 1
                o = co + direcao * 1e-3
            impares += k % 2
        return 2 * impares > len(RAIOS_DA_PARIDADE)

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

    def penetracao(self, pts, indices=None, limite=PERTO_DA_ARMA_MM):
        """A maior entrada (mm, ≥ 0) dos vértices `indices` (todos, sem eles) na arma. Com o `limite` (o padrão, nas
        buscas do solver), só os vértices a até ele da superfície contam — rápido, mas um vértice mais fundo que isso
        dentro da arma passa despercebido; a validação da pega mede sem limite (`limite=None`)."""
        pior = 0.0
        for i in range(len(pts)) if indices is None else indices:
            d = self.arma.distancia(pts[i], limite)
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


def juntar_dedos(col, na, mao, m, aberta, dedos, atravessa):
    """Os dedos lado a lado, como numa mão fechada de verdade: dobrados, os dedos convergem para a palma. Fechando cada
    um sozinho na arma a partir da abertura do repouso, os da mão da frente saíam em leque (na AK, a ponta de um a 12 a
    17 mm da do vizinho). A partir do médio, o de fora gira na MCP para o vizinho (a abertura, até a ABERTURA_MAXIMA
    além do repouso) e fecha de novo na arma a partir da mão aberta (`aberta`); fica a maior abertura (bisseção de
    PASSO_JUNTAR_GRAUS) em que ele não atravessa o vizinho nem entra na arma e em que a luva inteira não se atravessa
    mais que JUNTAR_ATRAVESSA_MM (`atravessa(pontos)`: a conta da validação, validar_maos.atravessa — a membrana entre
    dois dedos, perto das MCP, amassa quando eles se juntam). Devolve (pose, {dedo: graus girados})."""
    girou = {}
    for dedo, vizinho in JUNTAR:
        if dedo not in dedos or vizinho not in dedos:
            continue
        osso = f'{dedo}_1'
        # a pele entre os dois, perto das MCP, é a membrana entre eles (como em separar_vizinhos)
        longe = (osso, f'{vizinho}_1')
        A = col.triangulos(empunhadura._falanges(dedo), longe)
        B = col.triangulos(empunhadura._falanges(vizinho), longe)
        vertices = na.vertices(empunhadura._falanges(dedo))
        sinal = -empunhadura.para_fora(dedo, col.lado)  # para o vizinho
        ab0 = m.aberturas.get(osso, 0.0)
        inicio = m
        for i in (1, 2, 3):
            o = f'{dedo}_{i}'
            inicio = inicio.com(o, flexao=aberta.flexao.get(o, 0.0))

        def fechado(g, inicio=inicio, osso=osso, ab0=ab0, sinal=sinal, dedo=dedo):
            return agarrar(na, mao, inicio.com(osso, abertura=ab0 + sinal * g), dedo)[0]

        def cabe(p, A=A, B=B, vertices=vertices):
            pose = p.pose()
            return (col.profundidade(pose, A, B) <= CONTATO_MM
                    and na.penetracao(na.pontos(pose), vertices, limite=None) <= CONTATO_MM
                    and atravessa(col.modelo.pontos(pose)) <= JUNTAR_ATRAVESSA_MM)

        a, b = 0.0, empunhadura.ABERTURA_MAXIMA - abs(ab0)
        if cabe(fechado(b)):
            a = b
        else:
            while b - a > PASSO_JUNTAR_GRAUS:
                c = (a + b) / 2
                if cabe(fechado(c)):
                    a = c
                else:
                    b = c
        if a > 0.0:
            m = fechado(a)
            girou[dedo] = round(sinal * a, 2)
    return m, girou


def folgas_entre_dedos(col, pose, dedos):
    """A folga (mm) entre cada par de dedos vizinhos, na falange média e na distal: a menor distância entre os vértices
    de uma e os da mesma falange do vizinho, na luva posada (no referencial dela). {'indicador-medio': [média,
    distal], ...}."""
    pts = np.asarray(col.modelo.pontos(pose))
    por = {}
    for i, dono in enumerate(col.dono):
        por.setdefault(dono, []).append(i)
    folgas = {}
    for a, b in PARES_VIZINHOS:
        if a not in dedos or b not in dedos:
            continue
        par = []
        for f in (2, 3):
            ia, ib = por.get(f'{a}_{f}', []), por.get(f'{b}_{f}', [])
            kd = KDTree(len(ib))
            for k, i in enumerate(ib):
                kd.insert(Vector(pts[i]), k)
            kd.balance()
            par.append(round(min(kd.find(Vector(pts[i]))[2] for i in ia), 2))
        folgas[f'{a}-{b}'] = par
    return folgas


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


def dedo_no_alvo(na, mao, m, dedo, alvo, normal, abertura_max, raio_mm, folga=None, aperto=0.0, alvo_arma=None):
    """O dedo com a polpa no alvo (a normal para fora da superfície), chegando pela normal até encostar na arma.
    `folga(pts)`, se vier, é uma conta extra (mm) que tem de ficar ≥ 0 no caminho (o guarda-mato). Com o `aperto` (mm),
    a luva pode entrar até isso a mais na arma no caminho — a luva apertada num guarda-mato mais estreito que o dedo,
    como a da M4A4 —, menos na peça do alvo (`alvo_arma`, o gatilho), em que a polpa só encosta. Devolve (pose,
    relatório)."""
    lim = limites_do_dedo(mao, abertura_max)
    cadeia = CadeiaDedo(na, dedo, m.pose())
    ik = ik_dedo(cadeia, na.arma, alvo, normal, lim, raio_mm)
    dedo_v = na.vertices(cadeia.ossos)
    no_alvo = NaArma(na.col, alvo_arma) if aperto and alvo_arma is not None else None

    def cruza(g):
        pts = na.pontos(_com_dedo(m, dedo, g).pose())
        if na.penetracao(pts, dedo_v) > CONTATO_MM + aperto:
            return True
        if no_alvo is not None and no_alvo.penetracao(pts, dedo_v) > CONTATO_MM:
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
