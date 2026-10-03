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

from . import canonica
from .contornos import (  # noqa: F401 (a API de sempre da biblioteca: P.simplificar, P.arco...)
    arco, faixa_poligono, reamostrar, ret_arredondado, simplificar, suavizar, suavizar_trecho,
)
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
    # a ordem canônica já ao nascer (ver finalizar): os cortes e as deformações que vêm depois (fatiar, deslocar)
    # partem da mesma malha em toda execução — partindo de outra ordem, o corte por planos dava vértices com outro
    # ruído de ponto flutuante na soleira e na coronha da AK
    canonica.canonizar(me, grade=False)
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
        # sem repetição e na ordem das faces: um `set` de elementos do bmesh sai na ordem dos endereços de memória, que
        # muda a cada execução — os vértices novos do corte saíam em outra ordem, e o booleano exato da soleira da AK
        # com os sulcos do alçapão (cortados por estes laços) às vezes devolvia a malha vazia
        geom = (list(dict.fromkeys(v for f in faces for v in f.verts))
                + list(dict.fromkeys(e for f in faces for e in f.edges)) + faces)
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


def esquadro_reto(ob):
    """O esquadro de fora do chanfro reto (MITER_SHARP) em vez do arco: o arco do Blender 5.2 deixa vértices sem posição
    calculada (lixo de memória, ~10³⁶ mm) onde dois chanfros chegam quase alinhados a um vértice com uma aresta que não
    chanfra — os cantos das fendas do quebra-chamas da M4A4 (4.1c, Tarefa 15)."""
    if ob is not None:
        ob['esquadro'] = 'MITER_SHARP'


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
    na pilha; o esquadro de fora é em arco, ou reto na peça marcada com esquadro_reto."""
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
        m.miter_outer = ob.get('esquadro', 'MITER_ARC')
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
    construir o nível, antes de iniciar o próximo. Antes, toda malha da coleção — as peças e os cortadores — vai para a
    ordem canônica, com as posições intactas (canonica.canonizar sem a grade): as operações do bmesh (a extrusão, as
    normais recalculadas, o corte por planos) devolvem as mesmas formas com os polígonos e os vértices em outra ordem a
    cada execução (153 das 270 peças da AK em duas construções), e o booleano exato, determinístico para a mesma
    entrada, muda com a ordem dela — a soleira da AK com os sulcos do alçapão saía vazia, e o quebra-chamas da M4A4 com
    arestas soltas, em parte das construções. Na grade de 1 µm (como nas saídas) as posições arredondadas punham faces
    no mesmo plano e o booleano errava em outras peças."""
    for ob in colecao.objects:
        if ob.type == 'MESH':
            canonica.canonizar(ob.data, grade=False)
    for ob in colecao.objects:
        if ob.type == 'MESH' and not ob.get('cortador'):
            acabar(ob)
