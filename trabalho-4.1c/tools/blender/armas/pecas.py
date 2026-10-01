# Biblioteca de peças das armas realistas (Fase 4.1a; desenho, seção 4.1; vem da prova de conceito de 2026-09-26).
# Tudo em mm no referencial da ficha (unidades.py). Cada peça é um objeto de malha com as propriedades que o resto do
# pacote lê:
#   zona     — corpo, guarnicao, carregador, detalhes ou interno (zonas.py)
#   peca     — 'base' ou a peça móvel (soquetes.py junta por peça)
#   chanfro  — (largura em mm, segmentos no modelo alto); o de jogo usa 1 segmento (chanfro < 1 mm) ou 2
#   so_alto  — microdetalhe que só existe no modelo alto (vai para o relevo assado)
#   cortador — objeto usado só num booleano (escondido; nunca exportado)
# `iniciar` diz em que nível ('alto' ou 'jogo') e em que coleção as peças nascem; peça `so_alto` não nasce no de jogo.
import math

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

from .unidades import S, ficha, v3

_estado = {'nivel': 'alto', 'colecao': None}


def iniciar(nivel, nome_colecao):
    """Nível da construção ('alto' ou 'jogo') e a coleção onde as peças nascem (criada e ligada à cena)."""
    assert nivel in ('alto', 'jogo'), nivel
    col = bpy.data.collections.get(nome_colecao) or bpy.data.collections.new(nome_colecao)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    _estado['nivel'] = nivel
    _estado['colecao'] = col
    return col


def nivel():
    return _estado['nivel']


def _pula(so_alto):
    return so_alto and _estado['nivel'] == 'jogo'


def objeto(nome, bm, mat, zona, peca='base', so_alto=False, chanfro=(0.6, 3)):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    _estado['colecao'].objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    ob['zona'] = zona
    ob['peca'] = peca
    ob['so_alto'] = bool(so_alto)
    ob['chanfro'] = chanfro
    return ob


# ------------------------------------------------------------------------------------------------ contornos 2D
def suavizar(pts, it=2):
    """Chaikin em polígono fechado: tira o serrilhado de contorno lido de foto de baixa resolução."""
    for _ in range(it):
        novo = []
        for i, (ax, ay) in enumerate(pts):
            bx, by = pts[(i + 1) % len(pts)]
            novo += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        pts = novo
    return pts


def simplificar(pts, tol=0.15, minimo=0.6):
    """Tira a escada de pixels de um contorno traçado na foto sem arredondar as quinas de verdade (o Chaikin arredonda):
    Douglas-Peucker fechado com `tol` mm (1 px da foto) e depois junta no meio os lados mais curtos que `minimo` mm — a
    escada de 0,1-0,4 mm fazia o chanfro de 1 segmento sair com faces de área zero nas diagonais do punho."""
    def dp(seq):
        (ax, ay), (bx, by) = seq[0], seq[-1]
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy) or 1e-9
        pior, k = -1.0, 0
        for i in range(1, len(seq) - 1):
            d = abs((seq[i][0] - ax) * dy - (seq[i][1] - ay) * dx) / n
            if d > pior:
                pior, k = d, i
        if pior <= tol:
            return [seq[0], seq[-1]]
        return dp(seq[:k + 1])[:-1] + dp(seq[k:])
    pts = [tuple(p) for p in pts]
    # parte o anel no ponto mais longe do primeiro, para o Douglas-Peucker ter duas pontas fixas
    k = max(range(len(pts)), key=lambda i: math.dist(pts[0], pts[i]))
    anel = dp(pts[:k + 1])[:-1] + dp(pts[k:] + [pts[0]])[:-1]
    mudou = True
    while mudou and len(anel) > 3:
        mudou = False
        for i in range(len(anel)):
            a, b = anel[i], anel[(i + 1) % len(anel)]
            if math.dist(a, b) < minimo:
                anel[i] = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                del anel[(i + 1) % len(anel)]
                mudou = True
                break
    return anel


def suavizar_trecho(pts, dentro, sigma=1.5, passo=0.25):
    """O contorno fechado com os vértices do trecho em que `dentro(x, y)` dá 1 (de 0 a 1: a transição sem quina) levados
    para a média gaussiana de `sigma` mm da borda em volta deles (a borda reamostrada a cada `passo` mm, só para a
    conta) — tira o zigue-zague de 0,3 a 0,6 mm dos pixels da foto, que o `simplificar` deixa nas curvas e que, com o
    chanfro, vira uma fileira de facetas brilhando (o degrau de impressão 3D da frente do punho da Glock, nas correções
    da P1 da 4.1c). Os vértices de fora do trecho ficam exatamente onde estão (as quinas de verdade, e os planos que os
    cortes da peça encontram); passe o resultado pelo `simplificar`."""
    pts = [tuple(p) for p in pts]
    anel = pts + [pts[0]]
    comp = [0.0]
    for a, b in zip(anel, anel[1:]):
        comp.append(comp[-1] + math.dist(a, b))
    total = comp[-1]
    n = max(8, int(total / passo))
    amostras, k = [], 0
    for i in range(n):
        alvo = total * i / n
        while comp[k + 1] < alvo:
            k += 1
        t = (alvo - comp[k]) / max(comp[k + 1] - comp[k], 1e-9)
        (ax, ay), (bx, by) = anel[k], anel[k + 1]
        amostras.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    d = total / n
    largura = int(math.ceil(3 * sigma / d))
    out = []
    for i, (x, y) in enumerate(pts):
        w = max(0.0, min(1.0, dentro(x, y)))
        if w <= 0.0:
            out.append((x, y))
            continue
        centro = comp[i] / d
        soma = mx = my = 0.0
        for j in range(int(math.floor(centro)) - largura, int(math.ceil(centro)) + largura + 1):
            p = math.exp(-0.5 * ((j - centro) * d / sigma) ** 2)
            ax, ay = amostras[j % n]
            soma += p
            mx += p * ax
            my += p * ay
        out.append((x + (mx / soma - x) * w, y + (my / soma - y) * w))
    return out


def reamostrar(poli, n):
    """n pontos igualmente espaçados ao longo de uma polilinha."""
    comp = [0.0]
    for (ax, ay), (bx, by) in zip(poli, poli[1:]):
        comp.append(comp[-1] + math.hypot(bx - ax, by - ay))
    out = []
    for i in range(n):
        alvo = comp[-1] * i / (n - 1)
        k = max(1, next((j for j, c in enumerate(comp) if c >= alvo), len(comp) - 1))
        t = (alvo - comp[k - 1]) / max(1e-9, comp[k] - comp[k - 1])
        (ax, ay), (bx, by) = poli[k - 1], poli[k]
        out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def faixa_poligono(linha, larg):
    """Contorno de uma tira de largura `larg` em volta de uma polilinha (nervuras, frisos)."""
    esq, dir_ = [], []
    for i, (x, y) in enumerate(linha):
        a = linha[max(0, i - 1)]
        b = linha[min(len(linha) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / L * larg / 2, tx / L * larg / 2
        esq.append((x + nx, y + ny))
        dir_.append((x - nx, y - ny))
    return esq + dir_[::-1]


def arco(cx, cy, r, a0, a1, n):
    """n + 1 pontos de um arco (graus) em volta de (cx, cy)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# ------------------------------------------------------------------------------------------------ sólidos
def prisma(nome, pts, plano, a, b, mat, zona, peca='base', chanfro=0.8, seg=3, so_alto=False):
    """Polígono 2D extrudado. plano 'XZ' (extrude em Y de a até b, mm), 'YZ' (em X) ou 'XY' (em Z)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()

    def p3(u, v, w):
        if plano == 'XZ':
            return v3(u, w, v)
        if plano == 'YZ':
            return v3(w, u, v)
        return v3(u, v, w)
    vs = [bm.verts.new(p3(u, v, a)) for u, v in pts]
    f = bm.faces.new(vs)
    ret = bmesh.ops.extrude_face_region(bm, geom=[f])
    novos = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    d = (b - a) * S
    bmesh.ops.translate(bm, vec={'XZ': (0, d, 0), 'YZ': (d, 0, 0), 'XY': (0, 0, d)}[plano], verts=novos)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (chanfro, seg))


def perfil_suave(nome, pts, plano, a, b, mat, zona, peca='base', chanfro=0.8, seg=3, it=2, so_alto=False):
    """Prisma de um contorno lido de foto, suavizado por Chaikin antes (it iterações)."""
    return prisma(nome, suavizar(pts, it), plano, a, b, mat, zona, peca, chanfro, seg, so_alto)


def caixa(nome, minimo, maximo, mat, zona, peca='base', chanfro=0.6, so_alto=False):
    """Caixa alinhada aos eixos do Blender (mm): mínimo e máximo (x, y, z)."""
    x0, y0, z0 = minimo
    x1, y1, z1 = maximo
    return prisma(nome, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], 'XZ', y0, y1, mat, zona, peca, chanfro, 3, so_alto)


def torno(nome, perfil, mat, zona, peca='base', seg=48, eixo='X', centro=(0, 0, 0), chanfro=0.5, so_alto=False):
    """Perfil (posição ao longo do eixo, raio) em mm girado em volta de X (ou de Z) e posto no centro (mm)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    if eixo == 'X':
        vs = [bm.verts.new(v3(x, 0, r)) for x, r in perfil]
        ax = (1, 0, 0)
    else:
        vs = [bm.verts.new(v3(r, 0, z)) for z, r in perfil]
        ax = (0, 0, 1)
    es = [bm.edges.new((p, q)) for p, q in zip(vs, vs[1:])]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=ax, angle=math.tau, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.00001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.translate(bm, vec=v3(*centro), verts=bm.verts[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (chanfro, 2))


def esfera(nome, centro, raio, escala, mat, zona, peca='base', u=24, v=12, so_alto=False):
    """Esfera (mm) achatada por `escala` (x, y, z)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=raio * S)
    bmesh.ops.scale(bm, vec=escala, verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=v3(*centro), verts=bm.verts[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def _referenciais(P, fechado):
    """Tangente e os dois eixos do perfil em cada ponto da polilinha, por transporte paralelo: o perfil não gira de
    repente onde a tangente cruza um eixo fixo (o que torcia as faces em "gravata-borboleta"). No caminho fechado, a
    torção que sobra na emenda é repartida ao longo da volta."""
    n = len(P)
    if fechado:
        tang = [(P[(i + 1) % n] - P[(i - 1) % n]).normalized() for i in range(n)]
    else:
        tang = [(P[min(n - 1, i + 1)] - P[max(0, i - 1)]).normalized() for i in range(n)]
    ref = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
    us = [tang[0].cross(ref).normalized()]
    for i in range(1, n):
        u = tang[i - 1].rotation_difference(tang[i]) @ us[-1]
        us.append((u - tang[i] * u.dot(tang[i])).normalized())
    if fechado:
        u = tang[-1].rotation_difference(tang[0]) @ us[-1]
        u = (u - tang[0] * u.dot(tang[0])).normalized()
        sobra = math.atan2(tang[0].dot(u.cross(us[0])), u.dot(us[0]))
        us = [Quaternion(tang[i], sobra * i / n) @ us[i] for i in range(n)]
    return [(t, u, t.cross(u).normalized()) for t, u in zip(tang, us)]


def varrer(nome, perfil, caminho, mat, zona, peca='base', fechar_pontas=True, so_alto=False):
    """Perfil 2D (mm, no plano perpendicular ao caminho) varrido ao longo de uma polilinha 3D (mm, Blender x, y, z).
    Caminho que volta ao primeiro ponto (argolas) fecha em anel, sem tampas."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    P = [Vector(v3(*p)) for p in caminho]
    fechado = len(P) > 3 and (P[0] - P[-1]).length < 1e-7
    if fechado:
        P = P[:-1]
    aneis = [[bm.verts.new(p + (u * a + w * b) * S) for a, b in perfil] for p, (_t, u, w) in zip(P, _referenciais(P, fechado))]
    n = len(perfil)
    pares = list(zip(aneis, aneis[1:])) + ([(aneis[-1], aneis[0])] if fechado else [])
    for r0, r1 in pares:
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    if fechar_pontas and not fechado:
        bm.faces.new(aneis[0][::-1])
        bm.faces.new(aneis[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def tubo(nome, caminho, raio, mat, zona, peca='base', seg=12, so_alto=False):
    """Tubo de raio constante (mm) ao longo de uma polilinha 3D: molas, varetas, arames, argolas."""
    circulo = [(raio * math.cos(k * math.tau / seg), raio * math.sin(k * math.tau / seg)) for k in range(seg)]
    return varrer(nome, circulo, caminho, mat, zona, peca, True, so_alto)


def mola(nome, x0, x1, centro_yz, raio, fio, espiras, mat, zona, peca='base', passos=16, so_alto=False):
    """Mola helicoidal ao longo de X (mm): de x0 a x1, centro (y, z) do Blender, raio da hélice e do fio."""
    n = max(2, int(espiras * passos))
    pts = []
    for i in range(n + 1):
        f = i / n
        ang = f * espiras * math.tau
        pts.append((x0 + (x1 - x0) * f, centro_yz[0] + raio * math.cos(ang), centro_yz[1] + raio * math.sin(ang)))
    return tubo(nome, pts, fio, mat, zona, peca, 8, so_alto)


def rosca(nome, x0, x1, raio, passo, profundidade, mat, zona, peca='base', seg=24, centro=(0, 0), so_alto=False):
    """Filete de rosca em hélice ao longo de X (mm): um dente triangular de base `passo` girado de x0 até x1 sobre o
    raio (o núcleo é um torno à parte, de raio `raio - profundidade`). Sólido fechado: o dente é uma face extrudada."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    cy, cz = centro
    vs = [bm.verts.new(v3(x0, cy, cz + raio - profundidade)), bm.verts.new(v3(x0 + passo / 2, cy, cz + raio)),
          bm.verts.new(v3(x0 + passo, cy, cz + raio - profundidade))]
    f = bm.faces.new(vs)
    voltas = max(1, int((x1 - x0 - passo) / passo))
    bmesh.ops.spin(bm, geom=[f] + vs + list(f.edges), cent=v3(x0, cy, cz), axis=(1, 0, 0), dvec=(passo * S / seg, 0, 0),
                   angle=math.tau * voltas, steps=seg * voltas, use_duplicate=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, (0, 0))


def tira(nome, linha, largura, plano, a, b, mat, zona, peca='base', chanfro=0.4, seg=2, so_alto=False):
    """Prisma de uma tira de `largura` mm em volta de uma polilinha (nervuras de carregador, frisos)."""
    return prisma(nome, faixa_poligono(linha, largura), plano, a, b, mat, zona, peca, chanfro, seg, so_alto)


def ret_arredondado(u0, u1, v0, v1, raio, n=4):
    """Contorno 2D (anti-horário) de um retângulo de cantos arredondados, com n segmentos por canto (os anéis de um
    lofting). O raio fica limitado à metade do lado menor."""
    r = max(0.0, min(raio, (u1 - u0) / 2 - 1e-4, (v1 - v0) / 2 - 1e-4))
    cantos = ((u1 - r, v0 + r, -90.0), (u1 - r, v1 - r, 0.0), (u0 + r, v1 - r, 90.0), (u0 + r, v0 + r, 180.0))
    pts = []
    for cu, cv, a0 in cantos:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def lofting(nome, aneis, mat, zona, peca='base', so_alto=False, chanfro=(0, 0)):
    """Malha fechada a partir de anéis de pontos 3D (mm, Blender x, y, z), todos com o mesmo número de pontos e na
    mesma ordem: cada anel ligado ao próximo por quads e as duas pontas fechadas por n-gons (a alavanca de manejo
    afinando até a ponta)."""
    if _pula(so_alto):
        return None
    bm = bmesh.new()
    vs = [[bm.verts.new(v3(*p)) for p in anel] for anel in aneis]
    n = len(aneis[0])
    for r0, r1 in zip(vs, vs[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    bm.faces.new(vs[0][::-1])
    bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return objeto(nome, bm, mat, zona, peca, so_alto, chanfro)


def pino(nome, x, y, r, mat, zona, peca='base', lado=-1, de=16.0, ate=16.9, so_alto=False):
    """Cabeça de pino ou de eixo aflorando na lateral: cilindro curto ao longo de Y no lado direito (lado=-1) ou
    esquerdo (+1), com o centro em (x, y) da ficha e a face de `de` a `ate` mm do plano do meio."""
    ob = torno(nome, [(de, 0), (de, r), (ate, r), (ate, 0)], mat, zona, peca, 24, eixo='Z', centro=(x, 0, y), so_alto=so_alto)
    if ob:
        rotacionar(ob, 'X', 90 if lado < 0 else -90, (x, 0, y))
    return ob


def fileira(fabrica, n, passo):
    """n peças feitas por `fabrica(i, dx, dy)` com `passo` = (dx, dy) mm entre uma e a próxima (rebites, parafusos,
    nervuras, dentes de trilho, serrilhas). Devolve os objetos."""
    return [fabrica(i, passo[0] * i, passo[1] * i) for i in range(n)]


# O А cirílico da fonte do Blender (Bfont) tem contornos que se cruzam: a malha dele sai aberta e o booleano exato corta
# errado (o "АВ" do seletor virava "–В"). O A latino tem o mesmo desenho; as outras letras usadas saem inteiras.
HOMOGLIFOS = str.maketrans({'А': 'A'})


def _malha_do_texto(fonte, nome):
    """Malha fechada do texto: solda as tampas nas paredes (o texto convertido sai com as costuras abertas) e recusa
    letra quebrada — com um cortador aberto o booleano exato corta errado sem avisar."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(fonte.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
    abertas = sum(1 for e in bm.edges if not e.is_manifold)
    bm.to_mesh(me)
    bm.free()
    if abertas:
        raise ValueError(f'gravação "{nome}": a fonte gerou {abertas} arestas abertas (letra com contornos cruzados); '
                         'troque a letra por uma de mesmo desenho em HOMOGLIFOS')
    return me


def gravacao(nome, texto, x, y, altura, face, plano_mm, profundidade, alvo, rotacao=0.0):
    """Marcação estampada (letras do seletor, número de série, graduação da alça, marca de controle): o texto vira um
    cortador de `profundidade` mm na peça `alvo`, só no modelo alto (vai para o relevo assado). (x, y) = canto de baixo à
    esquerda na ficha (na face de cima, x e o Y do Blender); `face` 'direita', 'esquerda' ou 'cima'; `plano_mm` = Y do
    Blender da face (direita/esquerda) ou Z da face de cima; `altura` das letras em mm; `rotacao` em graus no plano da
    face (na de cima, -90 deixa a leitura de quem olha de trás da arma)."""
    if _estado['nivel'] == 'jogo' or alvo is None:
        return None
    cu = bpy.data.curves.new(nome, 'FONT')
    cu.body = texto.translate(HOMOGLIFOS)
    cu.size = altura * S
    cu.extrude = profundidade * S
    fonte = bpy.data.objects.new(nome, cu)
    _estado['colecao'].objects.link(fonte)
    if face == 'cima':
        fonte.location = v3(x, y, plano_mm)
        fonte.rotation_euler = (0.0, 0.0, math.radians(rotacao))
    else:
        fonte.location = ficha(x, y, plano_mm)
        # A face de texto (XY local) vira o plano XZ; na direita a leitura é de fora, na esquerda espelha pelo Z.
        fonte.rotation_euler = (math.radians(90), 0.0, 0.0) if face == 'direita' else (math.radians(90), 0.0, math.radians(180))
        fonte.rotation_euler[1] = math.radians(rotacao)
    me = _malha_do_texto(fonte, nome)
    corte = bpy.data.objects.new(f'{nome}.corte', me)
    corte.matrix_world = fonte.matrix_world.copy()
    _estado['colecao'].objects.link(corte)
    bpy.data.objects.remove(fonte)
    bpy.data.curves.remove(cu)
    corte['zona'] = alvo.get('zona')
    corte['peca'] = alvo.get('peca')
    cortar(alvo, corte)
    return corte


# ------------------------------------------------------------------------------------------------ operações
def cortar(alvo, cortador, depois_do_chanfro=False):
    """Booleano exato de diferença; o cortador fica escondido e fora da exportação. Sem cortador (peça só do modelo
    alto, no nível de jogo) não faz nada. `depois_do_chanfro`: o corte vem depois do chanfro na pilha (acabar), com a
    aresta viva — o entalhe da tampa, que não pode herdar o arredondado grande dos ombros."""
    if alvo is None or cortador is None:
        return
    m = alvo.modifiers.new('corte final' if depois_do_chanfro else 'corte', 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    m.object = cortador
    m.solver = 'EXACT'
    cortador.hide_render = True
    cortador.hide_viewport = True
    cortador['cortador'] = True


def unir(alvo, outro):
    """Booleano exato de união; o outro objeto fica escondido e fora da exportação."""
    if alvo is None or outro is None:
        return
    m = alvo.modifiers.new('uniao', 'BOOLEAN')
    m.operation = 'UNION'
    m.object = outro
    m.solver = 'EXACT'
    outro.hide_render = True
    outro.hide_viewport = True
    outro['cortador'] = True


def rotacionar(ob, eixo, graus, pivo):
    """Gira a malha em volta de um eixo ('X', 'Y', 'Z') passando pelo pivô (mm)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.rotate(bm, verts=bm.verts[:], cent=v3(*pivo), matrix=Matrix.Rotation(math.radians(graus), 3, eixo))
    bm.to_mesh(ob.data)
    bm.free()


def afinar(ob, fn):
    """Escala a espessura (Y) de cada vértice por fn(x_mm, z_mm): coronhas e guarda-mãos que afinam."""
    if ob is None:
        return
    for vt in ob.data.vertices:
        vt.co.y *= fn(vt.co.x / S, vt.co.z / S)


def fatiar(ob, eixo, valores, onde=None):
    """Corta a malha por planos perpendiculares ao eixo ('X', 'Y' ou 'Z') nas posições (mm): laços novos no meio das
    faces, onde uma deformação depois (a soleira curva vista de cima, a aba dobrada do seletor) precisa de vértices.
    `onde(x, y, z)` (mm, o centro da face) limita o corte às faces escolhidas — só a traseira da coronha, sem gastar
    triângulos no resto; a face vizinha que não entra ganha o vértice novo na aresta comum (sem rachadura)."""
    if ob is None:
        return
    i = 'XYZ'.index(eixo)
    normal = [0.0, 0.0, 0.0]
    normal[i] = 1.0
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for valor in valores:
        ponto = [0.0, 0.0, 0.0]
        ponto[i] = valor * S
        faces = [f for f in bm.faces if onde is None or onde(*(c / S for c in f.calc_center_median()))]
        geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=ponto, plane_no=normal)
    bm.to_mesh(ob.data)
    bm.free()


def deslocar(ob, fn):
    """Move cada vértice por fn(x, y, z) → (dx, dy, dz), tudo em mm no referencial do Blender: curvaturas e dobras
    (a face de trás da soleira, a aba do seletor)."""
    if ob is None:
        return
    for vt in ob.data.vertices:
        dx, dy, dz = fn(vt.co.x / S, vt.co.y / S, vt.co.z / S)
        vt.co.x += dx * S
        vt.co.y += dy * S
        vt.co.z += dz * S


def marcar_chanfro(ob, pred):
    """Chanfro só nas arestas em que pred(a, b) é verdadeiro — a e b são os dois vértices em mm (x, y, z) do Blender:
    a tampa arredonda os ombros de cima sem arredondar as pontas. Liga o limite por peso no acabamento (acabar)."""
    if ob is None:
        return
    me = ob.data
    peso = me.attributes.get('bevel_weight_edge') or me.attributes.new('bevel_weight_edge', 'FLOAT', 'EDGE')
    vs = me.vertices
    mm = lambda i: tuple(c / S for c in vs[i].co)
    valores = [1.0 if pred(mm(e.vertices[0]), mm(e.vertices[1])) else 0.0 for e in me.edges]
    peso.data.foreach_set('value', valores)
    ob['chanfro_peso'] = True


ANGULO_VIVO = 40.0  # graus entre as faces a partir dos quais a aresta fica viva no sombreado (arestas_vivas)


def _grupo_arestas_vivas():
    """Grupo de Geometry Nodes que marca como vivas (sharp_edge) as arestas com mais de ANGULO_VIVO graus entre as faces
    — o "Smooth by Angle" do Blender, feito aqui para não depender do asset. Sem ele o sombreado liso vazava pela borda
    dos cortes feitos depois do chanfro (o entalhe da tampa, as estrias do tubo) e pelas quinas sem chanfro, e a borda
    parecia amassada. Os passos de cilindro (até 36° com 10 segmentos) e de chanfro continuam lisos."""
    nome = f'arestas vivas {ANGULO_VIVO:g}°'
    g = bpy.data.node_groups.get(nome)
    if g is not None:
        return g
    g = bpy.data.node_groups.new(nome, 'GeometryNodeTree')
    g.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    g.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    n, l = g.nodes, g.links
    entrada, saida = n.new('NodeGroupInput'), n.new('NodeGroupOutput')
    angulo = n.new('GeometryNodeInputMeshEdgeAngle')
    liso = n.new('FunctionNodeCompare')
    liso.data_type = 'FLOAT'
    liso.operation = 'LESS_EQUAL'
    liso.inputs[1].default_value = math.radians(ANGULO_VIVO)
    l.new(angulo.outputs['Unsigned Angle'], liso.inputs[0])
    sombreado = n.new('GeometryNodeSetShadeSmooth')
    sombreado.domain = 'EDGE'
    l.new(entrada.outputs[0], sombreado.inputs['Mesh'])
    l.new(liso.outputs['Result'], sombreado.inputs['Shade Smooth'])
    l.new(sombreado.outputs['Mesh'], saida.inputs[0])
    return g


def acabar(ob):
    """Chanfro, solda e normais pelo nível: o alto usa os segmentos da peça (no mínimo 3); o de jogo, 1 segmento nos
    chanfros finos (< 1 mm) e 2 nos outros. A solda (0,005 mm) junta os vértices repetidos que os chanfros deixam onde se
    encontram numa parede fina (cabeça de pino) ou tocam as faces de um booleano — sem ela sobram faces de área zero; na
    armação da Glock (4.1c) o chanfro deixava, nas quinas dos rebaixos, remendos de 0,6 a 1,1 µm, que 0,001 mm não pegava.
    Arestas vivas acima de ANGULO_VIVO e normais ponderadas por área, mantendo as vivas. Peça com `chanfro_peso`
    (marcar_chanfro) chanfra só as arestas marcadas; os cortes feitos com `depois_do_chanfro` vão para depois do chanfro
    na pilha."""
    largura, seg = ob.get('chanfro', (0.6, 3))
    if largura > 0:
        m = ob.modifiers.new('chanfro', 'BEVEL')
        m.width = largura * S
        m.segments = max(3, int(seg)) if _estado['nivel'] == 'alto' else (1 if largura < 1.0 else 2)
        if ob.get('chanfro_peso'):
            m.limit_method = 'WEIGHT'
        else:
            m.limit_method = 'ANGLE'
            m.angle_limit = math.radians(32.0)
        m.harden_normals = True
        m.miter_outer = 'MITER_ARC'
        m.use_clamp_overlap = True
        for nome in [md.name for md in ob.modifiers if md.name.startswith('corte final')]:
            ob.modifiers.move(ob.modifiers.find(nome), len(ob.modifiers) - 1)
    s = ob.modifiers.new('solda', 'WELD')
    s.mode = 'ALL'
    s.merge_threshold = 0.005 * S
    vivas = ob.modifiers.new('arestas vivas', 'NODES')
    vivas.node_group = _grupo_arestas_vivas()
    w = ob.modifiers.new('normais', 'WEIGHTED_NORMAL')
    w.keep_sharp = True
    return ob


def finalizar(colecao):
    """Chanfro, solda e normais em todas as peças da coleção (os cortadores ficam de fora). Chamar logo depois de
    construir o nível, antes de iniciar o próximo."""
    for ob in colecao.objects:
        if ob.type == 'MESH' and not ob.get('cortador'):
            acabar(ob)
