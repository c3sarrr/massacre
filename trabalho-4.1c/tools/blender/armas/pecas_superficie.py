# Peças novas da biblioteca (Fase 4.1c; desenho em docs/superpowers/specs/2026-09-28-4.1c-glock-m4a4-m9-design.md,
# seção 3.4): o trilho Picatinny, o relevo de superfície (o quadriculado e a textura de punho, só no modelo alto), as
# ranhuras (a serrilha do ferrolho), os dentes de serra de um contorno (a serrilha do dorso da lâmina) e a lâmina com o
# gume. Mesmas convenções do pecas.py (mm no referencial da ficha; no Blender X = x, Z = y, o lado direito da arma em -Y);
# cada peça tem a prova de medida em provas_pecas.py (`npm run blender -- provar pecas`).
import math

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

from . import pecas as P
from .unidades import S, v3

# ------------------------------------------------------------------------------------------------ trilho Picatinny
# MIL-STD-1913 (AR), 3 de fevereiro de 1995, "Dimensioning of accessory mounting rail for small arms weapons" (Picatinny
# Arsenal; cópia no web.archive.org de quarterbore.com/library/pdf_files/mil-std-1913.pdf). Figura 1, o perfil: largura
# máxima 0,835" (-0,005); a largura de referência C, 0,748" (±0,002), medida nas duas linhas horizontais que distam 0,108"
# uma da outra, a de baixo a 0,164" (-0,020) do topo; flancos a 45° (2×, em cima e embaixo); pescoço de 0,617" (-0,010);
# do topo ao ombro da base, 0,367" no mínimo; quebra de canto de 0,002" a 0,012". Figura 2, a fenda de recuo: 0,206"
# (+0,008) de largura, 0,118" (+0,008) de fundo, passo de 0,394" entre centros. Daí, em mm, com o topo em v = 0:
POL = 25.4
PICATINNY = {
    'meiaTopo': (0.748 / 2 - (0.164 - 0.108)) * POL,        # 8,077: o flanco de cima a 45° chega ao topo
    'meiaMaxima': 0.835 / 2 * POL,                           # 10,605
    # Os dois flancos a 45° se encontrariam num vértice a 0,110" do topo, com meia-largura de 0,428"; a largura máxima
    # (0,835") o corta num patamar vertical de 0,021" de altura.
    'patamar': (0.164 - 0.108 / 2 - (0.748 / 2 + 0.108 / 2 - 0.835 / 2), 0.164 - 0.108 / 2 + (0.748 / 2 + 0.108 / 2 - 0.835 / 2)),
    'meiaPescoco': 0.617 / 2 * POL,                          # 7,836
    'fundoPescoco': (0.164 + (0.748 - 0.617) / 2) * POL,     # 5,829: o flanco de baixo chega ao pescoço
    'alturaMinima': 0.367 * POL,                             # 9,322
    'fenda': 0.206 * POL,                                    # 5,232
    'fundoFenda': 0.118 * POL,                               # 2,997
    'passo': 0.394 * POL,                                    # 10,008
}
PICATINNY['patamar'] = tuple(v * POL for v in PICATINNY['patamar'])  # 2,527 a 3,061 abaixo do topo


def perfil_picatinny(altura=None):
    """O perfil do trilho (u = lado a lado, v = para cima; o topo em v = 0), anti-horário, até `altura` mm abaixo do
    topo (no mínimo a da norma)."""
    t = PICATINNY
    h = max(altura or t['alturaMinima'], t['fundoPescoco'] + 0.5)
    a, m, n = t['meiaTopo'], t['meiaMaxima'], t['meiaPescoco']
    p0, p1 = t['patamar']
    lado = [(a, 0.0), (m, -p0), (m, -p1), (n, -t['fundoPescoco']), (n, -h)]
    return [(-u, v) for u, v in reversed(lado)] + lado


def _caixas(nome, caixas, mat, zona, peca='base', so_alto=False):
    """Um objeto só com várias caixas (mm, mínimo e máximo em x, y, z do Blender): um cortador para muitas fendas num
    booleano só."""
    if so_alto and P.nivel() == 'jogo':
        return None
    bm = bmesh.new()
    for (x0, y0, z0), (x1, y1, z1) in caixas:
        vs = [bm.verts.new(v3(x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
        for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return P.objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def _no_lugar(ob, giro, y, z):
    """Leva uma peça feita no referencial do trilho (o topo em Y = Z = 0 do Blender, subindo por +Z) para o lugar: gira
    `giro` graus em volta de X (0 = para cima, 90 = para o lado esquerdo, -90 = para o direito) e move para (y, z) mm."""
    if ob is None:
        return
    P.rotacionar(ob, 'X', -giro, (0.0, 0.0, 0.0))  # +Z (o topo) vai para +Y (a esquerda) com giro = 90
    P.deslocar(ob, lambda _x, _y, _z: (0.0, y, z))


def fendas_picatinny(x0, x1, margem=None):
    """Os centros das fendas de um trilho de x0 a x1 (mm), no passo da norma, centrados no comprimento, com pelo menos
    `margem` mm de trilho cheio em cada ponta (sem ela, meio passo)."""
    t = PICATINNY
    margem = t['passo'] / 2 if margem is None else margem
    util = (x1 - x0) - 2 * margem - t['fenda']
    n = max(0, int(math.floor(util / t['passo'] + 1e-6)) + 1)
    meio = (x0 + x1) / 2
    return [meio + (i - (n - 1) / 2) * t['passo'] for i in range(n)]


def trilho_picatinny(nome, x0, x1, mat, zona, peca='base', y=0.0, z=0.0, giro=0.0, altura=None, fendas=None,
                     chanfro=0.2, so_alto=False):
    """Trilho MIL-STD-1913 ao longo de X (mm, de x0 a x1): o perfil da Figura 1 com o topo no ponto (y, z) do Blender,
    virado para `giro` (graus em volta de X: 0 = para cima), descendo `altura` mm até a base (a peça em que ele nasce), e
    as fendas de recuo da Figura 2 (`fendas` = os centros em x; sem ela, fendas_picatinny) cortadas depois do chanfro
    (aresta viva de fresa). Devolve (trilho, cortador das fendas)."""
    t = PICATINNY
    trilho = P.prisma(nome, perfil_picatinny(altura), 'YZ', x0, x1, mat, zona, peca, chanfro=chanfro, seg=2, so_alto=so_alto)
    xs = fendas_picatinny(x0, x1) if fendas is None else fendas
    meia = t['fenda'] / 2
    corte = _caixas(f'{nome}: fendas', [((xc - meia, -t['meiaMaxima'] - 2.0, -t['fundoFenda']), (xc + meia, t['meiaMaxima'] + 2.0, 2.0))
                                        for xc in xs], mat, zona, peca, so_alto) if xs else None
    for ob in (trilho, corte):
        _no_lugar(ob, giro, y, z)
    if trilho is not None and corte is not None:
        P.cortar(trilho, corte, depois_do_chanfro=True)
        trilho['fendas'] = list(xs)
    return trilho, corte


# ------------------------------------------------------------------------------------------------ relevo de superfície
def _bvh_do(alvo):
    """Árvore de raios da malha avaliada do alvo (com os cortes já na pilha), no referencial do mundo."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = alvo.evaluated_get(dg)
    me = ev.to_mesh()
    mw = alvo.matrix_world
    vs = [mw @ v.co for v in me.vertices]
    fs = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs)


def relevo(nome, alvo, u, v, passo, raio, altura, mat=None, zona=None, peca=None):
    """Folha de relevo colada na superfície do `alvo` (só no modelo alto: vai para o relevo assado — o quadriculado, a
    textura de punho). A grade (u0, u1, passo) × (v0, v1, passo) em mm é levada à superfície por `raio(a, b)` → (origem,
    direção) em mm no Blender: o raio que acha a superfície para o ponto (a, b) da grade; cada vértice fica no ponto
    achado mais `altura(a, b)` mm pela normal. Os pontos que não acham a superfície (fora da peça) ficam de fora com as
    faces deles. Devolve o objeto (ou None no modelo de jogo)."""
    if P.nivel() == 'jogo' or alvo is None:
        return None
    arvore = _bvh_do(alvo)
    (u0, u1), (v0, v1) = u, v
    nu = max(1, int(round((u1 - u0) / passo)))
    nv = max(1, int(round((v1 - v0) / passo)))
    bm = bmesh.new()
    grade = {}
    for i in range(nu + 1):
        a = u0 + (u1 - u0) * i / nu
        for j in range(nv + 1):
            b = v0 + (v1 - v0) * j / nv
            origem, direcao = raio(a, b)
            o = Vector(v3(*origem))
            d = Vector(direcao).normalized()
            ponto, normal, _i, _dist = arvore.ray_cast(o, d)
            if ponto is None:
                continue
            if normal.dot(d) > 0:
                normal = -normal
            grade[i, j] = bm.verts.new(ponto + normal * (altura(a, b) * S))
    for i in range(nu):
        for j in range(nv):
            q = [grade.get(k) for k in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            if all(q):
                bm.faces.new(q)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
    ob = P.objeto(nome, bm, mat if mat is not None else (alvo.data.materials[0] if alvo.data.materials else None),
                  zona or alvo.get('zona'), peca or alvo.get('peca', 'base'), True, (0, 0))
    ob['relevo'] = True
    return ob


def piramides(passo, profundidade, angulo=45.0, plato=0.0):
    """Altura do quadriculado (a grade de pirâmides) no ponto (a, b) da grade, em mm: 0 no fundo dos sulcos e
    `profundidade` no topo de cada pirâmide; as linhas dos sulcos a `angulo` graus do eixo a (45° = losangos); `plato`
    (0 a 1) achata o topo (o quadriculado gasto)."""
    c, s = math.cos(math.radians(angulo)), math.sin(math.radians(angulo))

    def h(a, b):
        p = (a * c + b * s) / passo
        q = (-a * s + b * c) / passo
        dp = abs(p - math.floor(p) - 0.5) * 2.0  # 0 no meio da pirâmide, 1 no sulco
        dq = abs(q - math.floor(q) - 0.5) * 2.0
        return profundidade * min(1.0, (1.0 - max(dp, dq)) / max(1e-6, 1.0 - plato))
    return h


def pontilhado(densidade, raio, profundidade, semente=7):
    """Altura da textura de punho (grãos em relevo, espalhados como a textura moldada do polímero) no ponto (a, b), em
    mm: `densidade` grãos por mm² de `raio` mm e `profundidade` mm, sem se sobrepor (uma grade de células com um grão
    sorteado por célula)."""
    lado = 1.0 / math.sqrt(densidade)

    def sorteio(i, j, k):
        x = math.sin(i * 127.1 + j * 311.7 + k * 74.7 + semente * 17.3) * 43758.5453
        return x - math.floor(x)

    def h(a, b):
        ci, cj = math.floor(a / lado), math.floor(b / lado)
        melhor = 0.0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i, j = ci + di, cj + dj
                cx = (i + 0.2 + 0.6 * sorteio(i, j, 1)) * lado
                cy = (j + 0.2 + 0.6 * sorteio(i, j, 2)) * lado
                d = math.hypot(a - cx, b - cy) / raio
                if d < 1.0:
                    melhor = max(melhor, profundidade * math.sqrt(1.0 - d * d))
        return melhor
    return h


# ------------------------------------------------------------------------------------------------ ranhuras e dentes
def ranhuras(nome, alvo, centros, largura, profundidade, x_de, z_de, lado, mat=None, zona=None, peca=None, perfil='V',
             inclinacao=0.0):
    """Serrilha de ranhuras paralelas (a do ferrolho da pistola) cortada no `alvo` depois do chanfro: uma ranhura por
    centro (x mm, na altura z0 da faixa), de `largura` mm na boca e `profundidade` mm, subindo de z0 a z1 (z_de, mm), na
    face `lado` (o Y do Blender em mm do plano da face: negativo = lado direito). `perfil` 'V' (sulco em V) ou 'U' (fundo
    reto, 60 % da boca); `inclinacao` em graus (a ranhura deitada para trás subindo, positivo). Os centros fora de `x_de`
    = (x0, x1) ficam de fora. Devolve o cortador (ou None sem alvo)."""
    if alvo is None:
        return None
    (x0, x1), (z0, z1) = x_de, z_de
    sinal = -1.0 if lado < 0 else 1.0
    fora = 2.0  # o cortador passa 2 mm para fora da face
    meia = largura / 2
    k = math.tan(math.radians(inclinacao))
    if perfil == 'V':
        fundo = [(0.0, -profundidade)]
    else:
        fundo = [(meia * 0.6, -profundidade), (-meia * 0.6, -profundidade)]
    # (deslocamento em x, profundidade para dentro): a boca fora da face, a boca na face e o fundo.
    secao = [(-meia, fora), (meia, fora), (meia, 0.0), *fundo, (-meia, 0.0)]
    bm = bmesh.new()
    n = len(secao)
    for xc in centros:
        if not x0 <= xc <= x1:
            continue
        aneis = [[bm.verts.new(v3(xc + k * (z - z0) + dx, lado + sinal * p, z)) for dx, p in secao] for z in (z0, z1)]
        bm.faces.new(aneis[0])
        bm.faces.new(aneis[1][::-1])
        for i in range(n):
            bm.faces.new((aneis[0][i], aneis[0][(i + 1) % n], aneis[1][(i + 1) % n], aneis[1][i]))
    if not bm.faces:
        bm.free()
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    corte = P.objeto(nome, bm, mat if mat is not None else (alvo.data.materials[0] if alvo.data.materials else None),
                     zona or alvo.get('zona'), peca or alvo.get('peca', 'base'), False, (0, 0))
    P.cortar(alvo, corte, depois_do_chanfro=True)
    return corte


def dentes(linha, passo, altura, frente=0.35, fundo=0.0):
    """Dentes de serra ao longo de uma polilinha 2D (o dorso da lâmina, da guarda para a ponta): a cada `passo` mm, um
    dente de `altura` mm para fora da linha (à esquerda de quem anda nela), com a face da frente ocupando a fração
    `frente` do passo e um fundo reto de `fundo` do passo entre os dentes. Devolve os pontos do contorno serrilhado, do
    começo ao fim da linha."""
    comp = [0.0]
    for (ax, ay), (bx, by) in zip(linha, linha[1:]):
        comp.append(comp[-1] + math.hypot(bx - ax, by - ay))
    total = comp[-1]

    def em(s):
        s = max(0.0, min(total, s))
        k = max(1, next((i for i, c in enumerate(comp) if c >= s), len(comp) - 1))
        (ax, ay), (bx, by) = linha[k - 1], linha[k]
        f = (s - comp[k - 1]) / max(1e-9, comp[k] - comp[k - 1])
        tx, ty = bx - ax, by - ay
        L = math.hypot(tx, ty) or 1.0
        return (ax + tx * f, ay + ty * f), (-ty / L, tx / L)
    n = int(total / passo)
    sobra = (total - n * passo) / 2
    pts = [em(0.0)[0]]
    for i in range(n):
        s0 = sobra + i * passo
        (p0, _n0) = em(s0)
        pico_s = s0 + passo * (1.0 - frente - fundo)
        (pp, npico) = em(pico_s)
        (p1, _n1) = em(s0 + passo * (1.0 - fundo))
        pts += [p0, (pp[0] + npico[0] * altura, pp[1] + npico[1] * altura), p1]
    pts.append(em(total)[0])
    limpos = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - limpos[-1][0], p[1] - limpos[-1][1]) > 1e-4:
            limpos.append(p)
    return limpos


# ------------------------------------------------------------------------------------------------ lâmina com o gume
def lamina(nome, estacoes, mat, zona, peca='base', chanfro=(0.0, 0), so_alto=False):
    """A lâmina de faca por seções ao longo de X (mm), cada uma um octógono simétrico no Y do Blender (a espessura):
    estacoes = [(x, z_dorso, z_bisel_dorso, z_bisel, z_fio, espessura, fio_dorso, fio)] — no alto, o dorso (largura
    `fio_dorso`: o contrafio do clip, afiado, ou o dorso de quina quebrada), a linha do bisel de cima (onde a lâmina
    chega à espessura toda), a linha do bisel do gume (o fio sobe a partir dela) e o fio (`fio` mm de largura). O gume
    de ângulo θ tem 2·atan((espessura - fio) / 2 / (z_bisel - z_fio)) (angulo_do_gume). A primeira seção fecha a peça
    com uma tampa; a última, a ponta, é um ponto só (x, z) — `(x, z)` no lugar da estação — e fecha em leque."""
    if so_alto and P.nivel() == 'jogo':
        return None
    bm = bmesh.new()
    aneis = []
    for x, zd, zbd, zb, zf, e, fd, ff in estacoes[:-1]:
        meia, md, mf = e / 2, fd / 2, ff / 2
        pts = [(x, md, zd), (x, meia, zbd), (x, meia, zb), (x, mf, zf), (x, -mf, zf), (x, -meia, zb), (x, -meia, zbd), (x, -md, zd)]
        aneis.append([bm.verts.new(v3(*p)) for p in pts])
    xp, zp = estacoes[-1]
    ponta = bm.verts.new(v3(xp, 0.0, zp))
    n = 8
    bm.faces.new(aneis[0][::-1])
    for r0, r1 in zip(aneis, aneis[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    for k in range(n):
        bm.faces.new((aneis[-1][k], aneis[-1][(k + 1) % n], ponta))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return P.objeto(nome, bm, mat, zona, peca, so_alto, chanfro)


def angulo_do_gume(estacao):
    """O ângulo do gume (graus) de uma estação da lâmina: 2·atan((espessura - fio) / 2 / altura do bisel)."""
    _x, _zd, _zbd, zb, zf, e, _fd, ff = estacao
    return math.degrees(2.0 * math.atan((e - ff) / 2.0 / max(1e-9, zb - zf)))
