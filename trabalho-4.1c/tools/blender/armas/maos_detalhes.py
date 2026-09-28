# Detalhes da luva direita (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3.3; plano, Tarefa 4): as peças de jogo que fazem silhueta, cada uma assentada na malha base — o protetor de
# borracha moldada dos nós (um lóbulo com domo por nó, unidos pela ponte, tipo TPR), as almofadas de borracha nas costas
# das falanges proximal e média dos quatro dedos e a tira do punho com a borda saliente e o puxador. Os reforços de
# couro (a volta das pontas e a palma com a borda saliente) são a própria malha base estufada (maos_gaiola.py), sem
# triângulo a mais.
# Referências (moodboard, seção 15): luvas táticas com protetor de domos unidos e almofadas ovais nas falanges
# (QTG0–QTG3), o TPR moldado com um lóbulo por nó e guardas nas falanges (busca "mechanix m-pact glove knuckle"), a
# tira larga com o puxador no lado do mínimo (QTG1, QTG3).
# Cada peça é uma grade sobre a superfície: os pontos da base achados na malha base (raio de fora para dentro ou o
# ponto mais próximo), a face de cima a `altura` para fora pela normal suave dali, e as paredes descendo até 0,2 mm
# dentro da superfície (sem vão nem sobra); sem face de baixo, que ficaria escondida contra a luva. A quina entre o
# topo e a parede é marcada viva (a normal não se mistura).
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from .maos import DEDOS4
from .unidades import S

_DENTRO = 0.2  # a parede desce até 0,2 mm dentro da luva (mm)

# O protetor dos nós (mm). Contorno: a borda de trás a 24 mm da linha dos nós, sobre as costas da mão; na frente, um
# lóbulo elíptico por nó (meio eixo `lobulo` ao longo do dedo e de lado, centrado 1,5 mm além da MCP), e entre dois
# lóbulos a ponte para 3 mm antes dos nós — o vale onde a luva começa a descer para a dobra entre os dedos; dos lados,
# além do centro do mínimo e do indicador, com os cantos de trás arredondados (a borda de trás avança até `canto` mm
# nas pontas). Altura: a ponte e a borda (o chanfro em volta, em duas linhas da grade), e o domo de cada nó (meios
# eixos) com a altura da ficha (luva.protetor) no alto.
_PROTETOR = {'tras': -24.0, 'canto': 7.0, 'centro': 1.5, 'lobulo': (7.5, 10.8), 'vale': -3.0, 'lado_minimo': 9.5,
             'lado_indicador': 10.0, 'ponte': 3.0, 'borda': 0.8, 'chanfro': 2.0, 'domo': (8.0, 8.5),
             'colunas_do_domo': (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5),
             # frações de trás para a frente do contorno, mais juntas perto dos domos
             'linhas': (0.0, 0.21, 0.42, 0.575, 0.68, 0.79, 0.9, 1.0)}
# As almofadas (mm e graus): o comprimento em fração da falange, a meia abertura em volta das costas, o expoente da
# superelipse do contorno (4: retângulo de cantos redondos), a borda e a cúpula (a altura no meio sobre a da ficha,
# luva.almofada, que vale no anel de dentro).
_ALMOFADA = {'comprimento': 0.55, 'abertura': 38.0, 'expoente': 4.0, 'borda': 0.6, 'cupula': 0.4}
# A tira do punho (mm e graus): o centro no punho, a volta (do lado do polegar, onde é costurada, até a ponta solta do
# lado do mínimo), a espessura nas bordas salientes, no meio (um pouco rebaixado) e no bisel de fora, e o puxador na
# ponta solta — uma aba mais estreita que vai levantando da luva. A largura é a da ficha (luva.tira).
_TIRA = {'centro': -22.0, 'de': 100.0, 'ate': -80.0, 'passos': 16, 'aba': 1.5,
         'espessura': {'bisel': 1.6, 'borda': 2.6, 'meio': 2.2},
         'puxador': {'comprimento': 14.0, 'largura': 16.0, 'espessura': 2.0, 'levanta': 1.2}}


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


class Superficie:
    """A malha base (avaliada, em mm) numa BVH de triângulos, com as normais suaves interpoladas no ponto achado."""

    def __init__(self, ob):
        me = ob.data
        me.calc_loop_triangles()
        mw = ob.matrix_world
        self.co = [(mw @ v.co) / S for v in me.vertices]
        rot = mw.to_3x3().normalized()
        self.nv = [(rot @ v.normal).normalized() for v in me.vertices]
        self.tris = [tuple(t.vertices) for t in me.loop_triangles]
        self.bvh = BVHTree.FromPolygons(self.co, self.tris)

    def _normal(self, p, i):
        a, b, c = (self.co[k] for k in self.tris[i])
        v0, v1, v2 = b - a, c - a, p - a
        d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
        d20, d21 = v2.dot(v0), v2.dot(v1)
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-12:
            return self.nv[self.tris[i][0]]
        w1 = (d11 * d20 - d01 * d21) / den
        w2 = (d00 * d21 - d01 * d20) / den
        w0 = 1.0 - w1 - w2
        na, nb, nc = (self.nv[k] for k in self.tris[i])
        return (na * w0 + nb * w1 + nc * w2).normalized()

    def raio(self, origem, direcao):
        """(ponto, normal) onde o raio encontra a malha."""
        p, _n, i, _d = self.bvh.ray_cast(origem, direcao)
        if p is None:
            raise ValueError(f'detalhe da luva: o raio de {tuple(round(c, 1) for c in origem)} não achou a malha')
        return p, self._normal(p, i)

    def perto(self, ponto):
        """(ponto, normal) mais perto na malha."""
        p, _n, i, _d = self.bvh.find_nearest(ponto)
        return p, self._normal(p, i)

    def distancia(self, ponto):
        """Distância (mm) do ponto à malha."""
        return self.bvh.find_nearest(ponto)[3]


def _peca(nome, grade, colecao, material, zona):
    """A peça a partir da grade de (ponto na superfície, normal, altura): a face de cima e as paredes da borda até
    _DENTRO dentro da superfície. `grade[i][j]`: i ao longo, j de lado; as faces saem para fora."""
    bm = bmesh.new()
    nu, nv = len(grade), len(grade[0])
    topo = [[bm.verts.new(p + n * h) for (p, n, h) in linha] for linha in grade]
    for i in range(nu - 1):
        for j in range(nv - 1):
            bm.faces.new((topo[i][j], topo[i + 1][j], topo[i + 1][j + 1], topo[i][j + 1]))
    borda = ([(0, j) for j in range(nv)] + [(i, nv - 1) for i in range(1, nu)] + [(nu - 1, j) for j in range(nv - 2, -1, -1)]
             + [(i, 0) for i in range(nu - 2, 0, -1)])
    base = {(i, j): bm.verts.new(grade[i][j][0] - grade[i][j][1] * _DENTRO) for i, j in borda}
    for k in range(len(borda)):
        a, b = borda[k], borda[(k + 1) % len(borda)]
        bm.faces.new((topo[a[0]][a[1]], base[a], base[b], topo[b[0]][b[1]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # recalc_face_normals decide pelo volume, e a peça é aberta embaixo: garante que o topo aponte para fora da luva.
    i0, j0 = nu // 2, nv // 2
    do_topo = {x for linha in topo for x in linha}
    f0 = next(f for f in topo[i0][j0].link_faces if all(v in do_topo for v in f.verts))
    if f0.normal.dot(grade[i0][j0][1]) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    contorno = {topo[i][j] for i, j in borda}
    for e in bm.edges:
        e.smooth = not (e.verts[0] in contorno and e.verts[1] in contorno)
    bmesh.ops.scale(bm, vec=(S, S, S), verts=bm.verts[:])
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    # `assento` = 1 na base das paredes (0,2 mm dentro da luva): a conta do assentamento continua possível depois de a
    # peça ser juntada à luva (maos_rig.pesos).
    at = me.attributes.new('assento', 'FLOAT', 'POINT')
    at.data.foreach_set('value', [0.0] * (nu * nv) + [1.0] * (len(me.vertices) - nu * nv))
    ob = bpy.data.objects.new(nome, me)
    ob['zona'] = zona
    ob['vertices_do_topo'] = nu * nv  # os de depois são a base das paredes, 0,2 mm dentro da luva
    colecao.objects.link(ob)
    return ob


def _chanfro(i, j, nu, nv, alcance):
    """0 no contorno da grade, 1 a partir de `alcance` linhas/colunas para dentro (em índices)."""
    d = min(i, j, nu - 1 - i, nv - 1 - j)
    return _suave(d / alcance)


# ---------------------------------------------------------------------------------------------- protetor
def _x_mcp_na_coluna(mao, y):
    """O x da linha dos nós na posição y (entre os centros dos dedos, linear; fora deles, o do dedo da ponta)."""
    pts = sorted((mao.y_no[d], mao.dedos[d]['mcp'].x) for d in DEDOS4)
    if y <= pts[0][0]:
        return pts[0][1]
    if y >= pts[-1][0]:
        return pts[-1][1]
    for (y0, x0), (y1, x1) in zip(pts[:-1], pts[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return pts[-1][1]


def protetor(mao, sup, colecao, material):
    """O protetor de borracha dos nós: a placa sobre a linha dos nós com um lóbulo por nó na frente, a ponte entre
    eles e o domo de cada um, da altura da ficha no alto. A grade acompanha os lóbulos: as colunas se juntam em cada
    domo e as linhas vão, coluna a coluna, da borda de trás até a frente do contorno ali."""
    P = _PROTETOR
    rxl, ryl = P['lobulo']
    rx, ry = P['domo']
    h_domo = mao.f['luva']['protetor']
    ordem = list(reversed(DEDOS4))  # do mínimo ao indicador (y crescente)
    cols = [mao.y_no['minimo'] - P['lado_minimo']]
    for k, d in enumerate(ordem):
        cols += [mao.y_no[d] + dy for dy in P['colunas_do_domo']]
        if k < 3:
            cols.append((mao.y_no[d] + mao.y_no[ordem[k + 1]]) / 2)
    cols.append(mao.y_no['indicador'] + P['lado_indicador'])

    def frente(y):
        t = P['vale']
        for d in DEDOS4:
            s = (y - mao.y_no[d]) / ryl
            if abs(s) < 1.0:
                t = max(t, P['centro'] + rxl * math.sqrt(1.0 - s * s))
        return t

    meio_y, meia_l = (cols[0] + cols[-1]) / 2, (cols[-1] - cols[0]) / 2

    def tras(y):
        u = abs(y - meio_y) / meia_l
        return P['tras'] + P['canto'] * max(0.0, (u - 0.7) / 0.3) ** 2

    nu, nv = len(P['linhas']), len(cols)
    grade = []
    for i, f in enumerate(P['linhas']):
        linha = []
        for j, y in enumerate(cols):
            dx = tras(y) + (frente(y) - tras(y)) * f
            x = _x_mcp_na_coluna(mao, y) + dx
            p, n = sup.raio(Vector((x, y, 60.0)), Vector((0.0, 0.0, -1.0)))
            h = P['ponte']
            for d in DEDOS4:
                u = (dx - P['centro']) / rx if d == _dedo_da_coluna(mao, y) else 9.0
                v = (y - mao.y_no[d]) / ry
                s = 1.0 - u * u - v * v
                if s > 0:
                    h = max(h, P['ponte'] + (h_domo - P['ponte']) * s ** 0.6)
            k = _chanfro(i, j, nu, nv, P['chanfro'])
            linha.append((p, n, P['borda'] + (h - P['borda']) * k))
        grade.append(linha)
    return _peca('luva_d_protetor', grade, colecao, material, 'reforco')


def _dedo_da_coluna(mao, y):
    """O dedo com o centro mais perto de y."""
    return min(DEDOS4, key=lambda d: abs(mao.y_no[d] - y))


# ---------------------------------------------------------------------------------------------- almofadas
def _secao_estimada(mao, d, seg, t):
    """(meia largura, meia espessura) aproximadas do dedo no ponto t (0..1) da falange `seg` (para achar a superfície
    pelo ponto mais próximo: basta cair perto dela)."""
    dd = mao.dedos[d]
    luva = mao.luva
    (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
    base = (dd['larg_no'], ep * 1.12)
    a, b = (base, (lp, ep)) if seg == 0 else ((lp, ep), (ld, ed))
    return (a[0] + (b[0] - a[0]) * t) / 2 + luva, (a[1] + (b[1] - a[1]) * t) / 2 + luva


def _superelipse(u, v, expoente):
    """O ponto (u, v) do quadrado [-1, 1]² levado para a superelipse de mesmo "raio" (os meios dos lados ficam, os
    cantos entram)."""
    m = max(abs(u), abs(v))
    if m < 1e-9:
        return u, v
    r = m / (abs(u) ** expoente + abs(v) ** expoente) ** (1.0 / expoente)
    return u * r, v * r


def almofadas(mao, sup, colecao, material):
    """As almofadas de borracha nas costas das falanges proximal e média dos quatro dedos: uma superelipse sobre o meio
    de cada falange, só nas costas, com a espessura da ficha no anel de dentro e a cúpula no meio."""
    A = _ALMOFADA
    h = mao.f['luva']['almofada']
    us = (-1.0, -0.55, 0.0, 0.55, 1.0)  # ao longo da falange
    vs = (-1.0, -0.36, 0.36, 1.0)  # em volta das costas
    pecas = []
    for d in DEDOS4:
        dd = mao.dedos[d]
        for seg, (a, b) in enumerate((('mcp', 'pip'), ('pip', 'dip'))):
            comp = (dd[b] - dd[a]).length
            frente, costas = dd['dirs'][seg], dd['normais'][seg]
            radial = costas.cross(frente).normalized()
            meio = (dd[a] + dd[b]) / 2
            meio_comp = A['comprimento'] * comp / 2
            grade = []
            for i, u0 in enumerate(us):
                linha = []
                for j, v0 in enumerate(vs):
                    u, v = _superelipse(u0, v0, A['expoente'])
                    ml, me_ = _secao_estimada(mao, d, seg, 0.5 + u * A['comprimento'] / 2)
                    th = math.radians(v * A['abertura'])
                    alvo = meio + frente * (u * meio_comp) + costas * (me_ * math.cos(th)) + radial * (ml * math.sin(th))
                    p, n = sup.perto(alvo)
                    k = _chanfro(i, j, len(us), len(vs), 1.0)
                    cupula = A['cupula'] * (1.0 - u * u) * (1.0 - v * v)
                    linha.append((p, n, A['borda'] + (h + cupula - A['borda']) * k))
                grade.append(linha)
            ob = _peca(f'luva_d_almofada_{d}_{seg + 1}', grade, colecao, material, 'reforco')
            # O referencial da almofada, para as nervuras do modelo alto (maos_alto.py).
            ob['centro'], ob['frente'], ob['meio_comp'] = list(meio), list(frente), meio_comp
            pecas.append(ob)
    return pecas


# ---------------------------------------------------------------------------------------------- tira do punho
def tira(mao, sup, colecao, material):
    """A tira do punho (a largura da ficha, luva.tira): costurada do lado do polegar, passando pelas costas e fechando
    do lado do mínimo, onde a ponta solta tem o puxador (uma aba mais estreita que levanta da luva). De lado a lado: o
    bisel, a borda saliente, o meio um pouco rebaixado, a borda e o bisel."""
    T = _TIRA
    E = T['espessura']
    meia = mao.f['luva']['tira'] / 2
    c = T['centro']
    xs = (c - meia, c - meia + T['aba'], c, c + meia - T['aba'], c + meia)
    hs = (E['bisel'], E['borda'], E['meio'], E['borda'], E['bisel'])

    def na_volta(x, graus):
        th = math.radians(graus)
        direcao = Vector((0.0, math.sin(th), math.cos(th)))
        return sup.raio(Vector((x, 0.0, 0.0)) + direcao * 90.0, -direcao)

    grade = []
    for k in range(T['passos'] + 1):
        graus = T['de'] + (T['ate'] - T['de']) * k / T['passos']
        linha = []
        for x, hh in zip(xs, hs):
            p, n = na_volta(x, graus)
            # nas duas pontas da volta, o bisel também (a ponta costurada e a solta)
            linha.append((p, n, E['bisel'] if k in (0, T['passos']) else hh))
        grade.append(linha)
    pecas = [_peca('luva_d_tira', grade, colecao, material, 'reforco')]
    # O puxador: continua a volta além da ponta solta, mais estreito, e vai levantando da luva.
    X = T['puxador']
    raio_medio = sum((p.yz.length for p, _n, _h in grade[-1]), 0.0) / len(grade[-1])
    passo_graus = math.degrees(X['comprimento'] / raio_medio) / 2
    xs_p = (c - X['largura'] / 2, c, c + X['largura'] / 2)
    grade_p = []
    for k in range(3):
        graus = T['ate'] - passo_graus * k + (passo_graus * 0.35 if k == 0 else 0.0)
        linha = []
        for j, x in enumerate(xs_p):
            p, n = na_volta(x, graus)
            linha.append((p, n, X['espessura'] + X['levanta'] * k / 2 - (0.4 if j != 1 else 0.0)))
        grade_p.append(linha)
    pecas.append(_peca('luva_d_puxador', grade_p, colecao, material, 'reforco'))
    return pecas


def construir(mao, luva, colecao, material):
    """As peças de jogo da luva direita sobre a malha base `luva` (o objeto subdividido). Devolve (peças, o maior
    desvio em mm da base das paredes em relação aos 0,2 mm dentro da luva: o assentamento)."""
    sup = Superficie(luva)
    pecas = [protetor(mao, sup, colecao, material)]
    pecas += almofadas(mao, sup, colecao, material)
    pecas += tira(mao, sup, colecao, material)
    folga = 0.0
    for ob in pecas:
        mw = ob.matrix_world
        base = [(mw @ v.co) / S for v in ob.data.vertices[ob['vertices_do_topo']:]]
        folga = max(folga, max(abs(sup.distancia(p) - _DENTRO) for p in base))
    return pecas, folga
