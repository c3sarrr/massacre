# Correções das dobras das luvas (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 4; plano, Tarefa 5, Passo 4). O skin linear dos pesos (LBS) numa junta que fecha perde volume por fora (o nó
# afina: a média das duas matrizes encolhe o raio) e se atravessa por dentro (a palma da falange de baixo entra na de
# cima; no punho fechado, 6 mm). Depois do skin, cada junta corrige a malha, uma depois da outra, pela pose dela:
#  - por fora, os vértices da mistura dos pesos (nem só da parte parada nem só da que gira) voltam ao raio de repouso em
#    volta do eixo do giro da junta, pelo centro dela (o nó redondo, como a pele esticada sobre a cabeça do osso; o eixo
#    é o do giro inteiro da junta, então a abertura da MCP e a adução da CMC entram certas). Só do lado de fora da
#    dobra (as costas, u = eixo × normal apontando para dentro): inteiro a 2 mm para fora do plano do eixo, nada a 2 mm
#    para dentro, suave nos lados — por dentro, devolver o raio empurraria a pele da dobra contra o plano de contato;
#  - por dentro, a dobra: o plano de contato passa pelo eixo de flexão (preso ao osso de cima) e fica no meio entre a
#    direção reta da falange de cima e a do osso da junta — no repouso, a bissetriz do ângulo de repouso; na pose, a do
#    ângulo dela, com a abertura. Cada vértice é de um lado dele — o de lá se gira com a junta (os pesos), senão o de
#    cá; a base da falange, que no repouso fica atrás do plano da MCP, continua girando com o dedo e não entra na
#    palma —, empurrado pela normal do plano o quanto o softplus (escala 0,1 mm) da distância d a ele, menos a folga de
#    0,2 mm, cresceu desde o repouso (d₀): g(d − f) − g(d₀ − f), com g(x) = softplus(x) − x. Nada longe do plano; a pele
#    dos dois lados encostada a 0,2 mm dele sem as lâminas da dobra se sobreporem; nada no repouso; e, como o softplus
#    só empurra quem chega mais perto do plano do que estava, só do lado de dentro da dobra (por fora as duas partes se
#    afastam dele).
# Participam os vértices perto da junta — na faixa da largura dela ao longo do eixo e a até o alcance dela em volta do
# eixo (o raio da seção, mais a luva e 4 mm; na MCP, 22 mm, o coxim da palma diante dela; no pulso, a meia largura
# mais 6 mm) —, na proporção em que não são de outro dedo: a palma participa inteira de qualquer metacarpo (a diante da
# MCP do mínimo é do metacarpo do anelar) e a membrana entre dois dedos pela parte que é do dedo da junta.
# As peças de reforço seguem a base corrigida: cada vértice preso ao ponto mais próximo dela em repouso (o triângulo e
# as coordenadas baricêntricas), com o afastamento de repouso girado com a normal suave dali — o assentamento fica
# exato em qualquer pose (só o skin já tirava o protetor dos nós 0,6 mm do assento no punho fechado, com os pesos de
# três ossos nos nós).
# O jogo deforma as luvas pelo mesmo modelo, na CPU, a cada quadro (bracoLuva.js: o skin pelos ossos, as correções e
# as peças presas), com os parâmetros de cada junta e as amarras das peças nos `extras` do .glb (`parametros`); a
# validação e o solver de empunhadura avaliam a malha por aqui (`Modelo.avaliar`: o LBS em numpy, igual ao do Blender
# a 3e-5 mm, as correções e as peças). Um modelo analítico e não chaves de forma: exato em qualquer pose (as
# combinações de dedos vizinhos, a abertura), sem as dezenas de alvos de morph que as combinações pediriam; e na CPU,
# porque no shader um vértice não enxerga os da base em que a peça está presa. Depois das juntas e antes das peças, o
# afundamento da palma de uma pega (4.1c, a palma que cede: maos_palma.py). Unidades: mm; as malhas em metros no
# Blender.
import math

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

from . import maos_palma, maos_rig
from .maos import DEDOS4
from .unidades import S

SUAVE_MM = 0.1  # a escala do softplus no plano de contato da dobra
FOLGA_MM = 0.2  # cada lado da dobra fica a esta distância do plano de contato
FAIXA_MM = 3.0  # a faixa da junta ao longo do eixo: a meia largura mais a luva e 3 mm, e mais 3 mm para sumir
FORA_MM = 2.0  # a restauração do raio vai de inteira (2 mm para fora do plano do eixo) a nada (2 mm para dentro)
RAIO_MCP_MM = 22.0  # o alcance da dobra da MCP em volta do eixo: o coxim da palma diante dela
GIRO_MINIMO = 1e-4  # radianos: abaixo disso a junta está em repouso


def juntas(mao):
    """[(junta, osso sem o lado, graus de repouso, graus máximos a partir do repouso, meia largura mm, alcance mm)] das
    juntas de flexão, na ordem em que as correções se aplicam: MCP, PIP e DIP dos quatro dedos (os limites da AAOS), a
    CMC, a MCP e a IP do polegar e o pulso."""
    lim = mao.f['limites']
    rep = mao.rep
    luva = mao.luva
    lista = []
    for d in DEDOS4:
        dd = mao.dedos[d]
        (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
        lista += [(f'{d}_mcp', f'{d}_1', rep['mcp'], lim['mcp'][1] - rep['mcp'], dd['larg_no'] / 2, RAIO_MCP_MM),
                  (f'{d}_pip', f'{d}_2', rep['pip'], lim['pip'][1] - rep['pip'], lp / 2, max(lp, ep) / 2 + luva + 4),
                  (f'{d}_dip', f'{d}_3', rep['dip'], lim['dip'][1] - rep['dip'], ld / 2, max(ld, ed) / 2 + luva + 4)]
    lp = lim['polegar']
    lip, eip = mao.polegar['ip_sec']
    # A CMC dobra a tenar contra a palma: a faixa é a largura da eminência tenar, ~1,5 × a da IP, e o alcance, o da MCP.
    lista += [('polegar_cmc', 'polegar_1', 0.0, lp['cmcFlexao'][1], lip * 0.75, RAIO_MCP_MM),
              ('polegar_mcp', 'polegar_2', rep['polegarMcp'], lp['mcp'][1] - rep['polegarMcp'], lip * 0.55,
               max(lip * 1.1, eip * 1.12) / 2 + luva + 4),
              ('polegar_ip', 'polegar_3', rep['polegarIp'], lp['ip'][1] - rep['polegarIp'], lip / 2,
               max(lip, eip) / 2 + luva + 4),
              ('pulso', 'mao', 0.0, lim['pulso']['flexao'], mao.pulso_larg / 2,
               max(mao.pulso_larg, mao.pulso_esp) / 2 + luva + 6)]
    return lista


def _digito(osso):
    """O dedo de um osso de falange (sem o lado) ou None (a palma: mão, metacarpos do anelar e do mínimo, antebraço)."""
    nome, _, i = osso.rpartition('_')
    if nome == 'polegar' or (nome in DEDOS4 and i in ('1', '2', '3')):
        return nome
    return None


def _suave(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _softplus_menos_x(x):
    return SUAVE_MM * np.logaddexp(0.0, -x / SUAVE_MM)


class _Junta:
    """Os dados de repouso de uma junta para a correção: o centro, o eixo de flexão, a normal do plano de contato e a
    direção reta da falange de cima, e por vértice o peso do lado que gira, a participação e a distância ao plano."""

    def __init__(self, malha, junta):
        self.nome, osso0, self.repouso, self.maximo, self.meia, self.alcance = junta
        self.osso = f'{osso0}_{malha.lado}'
        b = malha.rig.data.bones[self.osso]
        self.pai = b.parent.name if b.parent else None
        m = b.matrix_local
        self.c0 = np.array(b.head_local) / S
        self.a0 = np.array(m.col[0].xyz.normalized())
        y0 = m.col[1].xyz.normalized()
        a0 = Vector(self.a0)
        self.n0 = np.array(Quaternion(a0, math.radians(-self.repouso / 2)) @ y0)
        self.reto0 = np.array(Quaternion(a0, math.radians(-self.repouso)) @ y0)
        abaixo = {self.osso} | {c.name for c in b.children_recursive}
        self.abaixo = sorted(o[:-2] for o in abaixo)
        dedo = _digito(osso0)
        self.outros = sorted(o[:-2] for o in malha.ossos if _digito(o[:-2]) not in (None, dedo))
        idx = {o: i for i, o in enumerate(malha.ossos)}
        self.w_abaixo = malha.W[:, [idx[o] for o in abaixo]].sum(1)
        w_outro = malha.W[:, [idx[f'{o}_{malha.lado}'] for o in self.outros]].sum(1) if self.outros else 0.0
        rel0 = malha.p - self.c0
        raio0 = np.linalg.norm(rel0 - np.outer(rel0 @ self.a0, self.a0), axis=1)
        faixa = _suave((self.meia + malha.luva_mm + FAIXA_MM - np.abs(rel0 @ self.a0)) / FAIXA_MM)
        perto = _suave((self.alcance + FAIXA_MM - raio0) / FAIXA_MM)
        self.peso = faixa * perto * np.clip(1.0 - w_outro, 0.0, 1.0) * malha.base
        self.lado = np.where(self.w_abaixo >= 0.5, 1.0, -1.0)
        self.d0 = self.lado * (rel0 @ self.n0)
        u0 = np.cross(self.a0, self.n0)  # para dentro da dobra (o lado da palma)
        self.fora = _suave((FORA_MM - rel0 @ u0) / (2 * FORA_MM))
        self.mistura = (self.w_abaixo > 0.002) & (self.w_abaixo < 0.998) & (self.peso * self.fora > 0)
        self.rel0 = rel0

    def parametros(self):
        """Os números que o shader do jogo precisa (mm e unitários, no referencial do braço)."""
        return {'junta': self.nome, 'osso': self.osso[:-2], 'repouso': float(self.repouso),
                'meia': round(float(self.meia), 4), 'alcance': round(float(self.alcance), 4),
                'centro': [round(float(c), 5) for c in self.c0], 'eixo': [round(float(c), 6) for c in self.a0],
                'normal': [round(float(c), 6) for c in self.n0], 'reto': [round(float(c), 6) for c in self.reto0],
                'abaixo': self.abaixo, 'outros': self.outros}

    def aplicar(self, rig, alvo):
        """A correção desta junta na pose atual do rig, sobre `alvo` (mm, as posições depois do skin e das juntas
        anteriores)."""
        pb = rig.pose.bones[self.osso]
        q = pb.rotation_quaternion if pb.rotation_mode == 'QUATERNION' else pb.matrix_basis.to_quaternion()
        angulo = q.angle
        if angulo < GIRO_MINIMO:
            return alvo
        if self.pai:
            pp = rig.pose.bones[self.pai]
            P = np.array((pp.matrix @ rig.data.bones[self.pai].matrix_local.inverted()).to_3x3())
        else:
            P = np.eye(3)
        c = np.array(pb.head) / S
        a = P @ self.a0
        # por fora: o raio de repouso em volta do eixo do giro inteiro da junta (no referencial de repouso do braço)
        b = rig.data.bones[self.osso]
        e0 = np.array((b.matrix_local.to_3x3() @ q.axis).normalized())
        e = P @ e0
        m = self.mistura
        if m.any():
            r0 = np.linalg.norm(self.rel0[m] - np.outer(self.rel0[m] @ e0, e0), axis=1)
            rel = alvo[m] - c
            ax = rel @ e
            perp = rel - np.outer(ax, e)
            rp = np.linalg.norm(perp, axis=1)
            ok = (rp > 1.0) & (r0 > 1.0)
            novo = c + np.outer(ax, e) + perp * (r0 / np.maximum(rp, 1e-9))[:, None]
            alvo[m] += np.where(ok[:, None], (novo - alvo[m]) * (self.peso * self.fora)[m, None], 0.0)
        # por dentro: o plano de contato entre a direção reta de cima e a do osso da junta
        y = np.array(pb.matrix.col[1].xyz.normalized())
        n = y + P @ self.reto0
        n -= a * (n @ a)
        n /= max(np.linalg.norm(n), 1e-12)
        d = self.lado * ((alvo - c) @ n)
        empurra = np.maximum(_softplus_menos_x(d - FOLGA_MM) - _softplus_menos_x(self.d0 - FOLGA_MM), 0.0)
        alvo += np.outer(self.lado * empurra * self.peso, n)
        return alvo


def _normais_dos_vertices(p, tri):
    """Normais suaves (pela área) dos vértices dos triângulos."""
    fn = np.cross(p[tri[:, 1]] - p[tri[:, 0]], p[tri[:, 2]] - p[tri[:, 0]])
    vn = np.zeros_like(p)
    for k in range(3):
        np.add.at(vn, tri[:, k], fn)
    return vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)


def _girar(v, de, para):
    """Gira cada v pela rotação mínima que leva `de` a `para` (unitários), vetorizado."""
    k = np.cross(de, para)
    s = np.linalg.norm(k, axis=1)
    c = np.einsum('ij,ij->i', de, para)
    eixo = k / np.maximum(s, 1e-12)[:, None]
    kv = np.einsum('ij,ij->i', eixo, v)
    out = v * c[:, None] + np.cross(eixo, v) * s[:, None] + eixo * (kv * (1 - c))[:, None]
    return np.where((s > 1e-9)[:, None], out, v)


class Malha:
    """A luva ligada ao rig, em numpy (mm): o repouso, os pesos, a base (as faces fora do reforço) com as peças presas
    a ela, e o skin linear na pose atual do rig."""

    def __init__(self, luva, rig, luva_mm, reforco):
        for ob in (luva, rig):
            if any(abs(ob.matrix_world[i][j] - (i == j)) > 1e-9 for i in range(4) for j in range(4)):
                raise ValueError(f'{ob.name}: as correções pedem a luva e o rig na origem, sem escala nem giro')
        self.luva, self.rig, self.luva_mm = luva, rig, luva_mm
        self.lado = rig.name.rsplit('_', 1)[1]
        me = luva.data
        n = len(me.vertices)
        co = np.empty(n * 3)
        me.vertices.foreach_get('co', co)
        self.p = co.reshape(-1, 3) / S
        self.ossos = [b.name for b in rig.data.bones]
        idx = {nome: i for i, nome in enumerate(self.ossos)}
        grupo = {g.index: idx[g.name] for g in luva.vertex_groups if g.name in idx}
        W = np.zeros((n, len(self.ossos)))
        for v in me.vertices:
            for g in v.groups:
                if g.group in grupo:
                    W[v.index, grupo[g.group]] = g.weight
        self.W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        tri = np.empty(nt * 3, np.int32)
        me.loop_triangles.foreach_get('vertices', tri)
        poly = np.empty(nt, np.int32)
        me.loop_triangles.foreach_get('polygon_index', poly)
        mats = np.empty(len(me.polygons), np.int32)
        me.polygons.foreach_get('material_index', mats)
        self.tri_base = tri.reshape(-1, 3)[mats[poly] != reforco]
        self.base = np.zeros(n, bool)
        self.base[self.tri_base.ravel()] = True
        self._prender_pecas()

    def _prender_pecas(self):
        """Cada vértice de peça no ponto mais próximo da base em repouso: o triângulo, as coordenadas baricêntricas, o
        afastamento até ele e a normal suave dali."""
        pecas = np.nonzero(~self.base)[0]
        tb = self.tri_base
        bvh = BVHTree.FromPolygons(self.p.tolist(), tb.tolist())
        vn = _normais_dos_vertices(self.p, tb)
        self.pecas = pecas
        self.prende_tri = np.empty(len(pecas), np.int64)
        self.prende_bar = np.empty((len(pecas), 3))
        self.prende_off = np.empty((len(pecas), 3))
        for k, i in enumerate(pecas):
            co, _n, t, _d = bvh.find_nearest(Vector(self.p[i]))
            a, b, c = (self.p[j] for j in tb[t])
            v0, v1, v2 = b - a, c - a, np.array(co) - a
            d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
            d20, d21 = v2 @ v0, v2 @ v1
            den = d00 * d11 - d01 * d01
            bv = (d11 * d20 - d01 * d21) / den
            bw = (d00 * d21 - d01 * d20) / den
            self.prende_tri[k] = t
            self.prende_bar[k] = (1 - bv - bw, bv, bw)
            self.prende_off[k] = self.p[i] - np.array(co)
        ns = np.einsum('kj,kji->ki', self.prende_bar, vn[tb[self.prende_tri]])
        self.prende_ns = ns / np.maximum(np.linalg.norm(ns, axis=1, keepdims=True), 1e-12)

    def seguir_base(self, alvo):
        """Leva as peças para a base em `alvo` (as posições das peças são reescritas)."""
        tb = self.tri_base
        vn = _normais_dos_vertices(alvo, tb)
        cantos = tb[self.prende_tri]
        ponto = np.einsum('kj,kji->ki', self.prende_bar, alvo[cantos])
        ns = np.einsum('kj,kji->ki', self.prende_bar, vn[cantos])
        ns /= np.maximum(np.linalg.norm(ns, axis=1, keepdims=True), 1e-12)
        alvo[self.pecas] = ponto + _girar(self.prende_off, self.prende_ns, ns)
        return alvo

    def amarras(self):
        """As amarras das peças para o jogo: por vértice de peça, o vértice, os três da base, as baricêntricas, o
        afastamento e a normal de repouso (mm)."""
        return {'vertices': self.pecas.tolist(), 'base': self.tri_base[self.prende_tri].tolist(),
                'bar': np.round(self.prende_bar, 6).tolist(), 'afastamento': np.round(self.prende_off, 5).tolist(),
                'normal': np.round(self.prende_ns, 6).tolist()}

    def skin(self):
        """As posições pelo LBS (mm) na pose atual do rig."""
        nb = len(self.ossos)
        R = np.empty((nb, 3, 3))
        t = np.empty((nb, 3))
        for i, nome in enumerate(self.ossos):
            M = self.rig.pose.bones[nome].matrix @ self.rig.data.bones[nome].matrix_local.inverted()
            R[i] = np.array(M.to_3x3())
            t[i] = np.array(M.translation) / S
        B = np.einsum('vb,bij->vij', self.W, R)
        return np.einsum('vij,vj->vi', B, self.p) + self.W @ t


class Modelo:
    """O skin das luvas com as correções das dobras (ver o cabeçalho) e a palma que cede (maos_palma.py: `cede`, a
    capacidade de cada vértice; o afundamento de uma pega entra em `avaliar`)."""

    def __init__(self, luva, rig, mao, reforco):
        self.malha = Malha(luva, rig, mao.luva, reforco)
        self.juntas = [_Junta(self.malha, j) for j in juntas(mao)]
        self.cede = maos_palma.capacidade(self.malha, mao.f)

    def avaliar(self, pose=None, afundar=None):
        """As posições (mm, numpy) da luva na pose (ou na atual do rig), com o afundamento da palma de uma pega
        (`afundar`, maos_palma.aplicar) depois das juntas e antes das peças, que seguem a base."""
        if pose is not None:
            maos_rig.posar(self.malha.rig, pose)
        alvo = self.malha.skin()
        for j in self.juntas:
            alvo = j.aplicar(self.malha.rig, alvo)
        alvo = maos_palma.aplicar(alvo, self.malha.rig, self.malha.lado, afundar)
        return self.malha.seguir_base(alvo)

    def pontos(self, pose=None, afundar=None):
        """As posições como Vectors (mm), para as BVH."""
        return [Vector(p) for p in self.avaliar(pose, afundar)]

    def parametros(self):
        """Os parâmetros do modelo para o shader do jogo (os `extras` do .glb)."""
        return {'suaveMM': SUAVE_MM, 'folgaMM': FOLGA_MM, 'faixaMM': FAIXA_MM, 'foraMM': FORA_MM, 'giroMinimo': GIRO_MINIMO,
                'luvaMM': float(self.malha.luva_mm), 'juntas': [j.parametros() for j in self.juntas],
                'pecas': self.malha.amarras(), 'palma': maos_palma.parametros(self.cede)}

    def para_malha(self, nome, colecao, pose=None, afundar=None):
        """Um objeto com a malha da luva nas posições da pose (e do afundamento da palma), sem rig (para as vistas): a
        mesma topologia, os mesmos materiais."""
        me = self.malha.luva.data.copy()
        me.name = nome
        co = (self.avaliar(pose, afundar) * S).ravel()
        me.vertices.foreach_set('co', co)
        me.update()
        ob = bpy.data.objects.new(nome, me)
        ob.matrix_world = Matrix.Identity(4)
        colecao.objects.link(ob)
        return ob
