"""Importar: a receita de uma arma vira a cena do Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

- uma coleção por grupo animável (`grupo:<nome>`), com o pivô como Empty (`pivo:<nome>`);
- `profile` vira curva 2D preenchida com extrusão e bisel; `lathe`, o meridiano com o modificador Parafuso em volta
  do X; `tube`, curva 3D com bisel e o raio em cada ponto; as outras formas, malhas geradas pelos parâmetros;
- cortes (`op: subtract`) em arame vermelho; âncoras como Empties (as de mão com a mão de massinha desenhada na pose
  da âncora, calculada pelo rig do jogo); a planta de referência numa coleção que não exporta;
- cada objeto guarda o que o jogo precisa em propriedades `massacre_*` (a peça original em JSON, a ordem): o
  exportador usa o guardado quando a geometria não mudou, então a ida e volta devolve os mesmos números.
Toda geometria fica no referencial da peça no jogo; a matriz do objeto é C · T(pos) · R(rot) · T(centro) (eixos.py):
nas peças definidas por pontos (perfil, torno, tubo, cápsula, cone arredondado) a origem do objeto fica no centro da
peça, então girar e escalar acontece no lugar, como quem modela espera.
"""

import json
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import eixos

COR_CORTE = (0.92, 0.12, 0.1, 1.0)
COR_PLANTA = '#F28F3B'
SEGMENTOS = 32


def rgba(hexcor, alfa=1.0):
    """'#RRGGBB' (sRGB) → cor linear do Blender."""
    h = hexcor.lstrip('#')
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), alfa)


def limpar_cena():
    """Cena dedicada à arma: tira objetos, coleções e o que ficou órfão."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for bloco in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(bloco):
            if d.users == 0:
                bloco.remove(d)


def material(nome, hexcor, rugosidade=0.7):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    m.diffuse_color = rgba(hexcor)
    m.roughness = rugosidade
    return m


# ---------------------------------------------------------------- malhas das formas (referencial da peça no jogo)

def _malha(nome, bm):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    return me


def malha_caixa(nome, size):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _malha(nome, bm)


def malha_cilindro(nome, r1, r2, h):
    """Cilindro (ou cone truncado) em volta do Y local, de y = −h (raio r1) a y = +h (raio r2)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=SEGMENTOS, radius1=r1, radius2=r2, depth=2 * h)
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(-math.pi / 2, 3, 'X'))
    return _malha(nome, bm)


def malha_esfera(nome, raios):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0)
    bmesh.ops.scale(bm, vec=Vector(raios), verts=bm.verts)
    return _malha(nome, bm)


def malha_toro(nome, R, r):
    """Toro no plano XZ local (eixo Y), como o do SDF."""
    bm = bmesh.new()
    nu, nv = SEGMENTOS, 16
    vs = []
    for i in range(nu):
        u = 2 * math.pi * i / nu
        for j in range(nv):
            v = 2 * math.pi * j / nv
            rr = R + r * math.cos(v)
            vs.append(bm.verts.new((rr * math.cos(u), r * math.sin(v), rr * math.sin(u))))
    for i in range(nu):
        for j in range(nv):
            a = vs[i * nv + j]
            b = vs[((i + 1) % nu) * nv + j]
            c = vs[((i + 1) % nu) * nv + (j + 1) % nv]
            d = vs[i * nv + (j + 1) % nv]
            bm.faces.new((a, d, c, b))
    return _malha(nome, bm)


def _capsula(bm, a, b, ra, rb, lados=16):
    """Cone arredondado de a até b (duas esferas e o tronco entre elas), direto num bmesh."""
    va, vb = Vector(a), Vector(b)
    eixo = vb - va
    comprimento = eixo.length
    for centro, raio in ((va, ra), (vb, rb)):
        m = Matrix.Translation(centro)
        bmesh.ops.create_uvsphere(bm, u_segments=lados, v_segments=max(6, lados // 2), radius=raio, matrix=m)
    if comprimento > 1e-6:
        z = eixo.normalized()
        rot = z.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        m = Matrix.Translation((va + vb) / 2) @ rot
        bmesh.ops.create_cone(bm, cap_ends=False, segments=lados, radius1=ra, radius2=rb, depth=comprimento, matrix=m)


def malha_capsula(nome, a, b, ra, rb):
    bm = bmesh.new()
    _capsula(bm, a, b, ra, rb)
    return _malha(nome, bm)


def malha_mao(nome, segmentos):
    """A mão de massinha como proxy: uma cápsula por osso (cabeça, ponta, raio) no referencial da mão."""
    bm = bmesh.new()
    for s in segmentos:
        _capsula(bm, s['head'], s['tail'], s['radius'], s['radius'] * 0.96, lados=10)
    return _malha(nome, bm)


# ---------------------------------------------------------------- curvas

def curva_perfil(nome, pontos, h, arredondado):
    """Perfil recortado: curva 2D preenchida; extrusão + bisel com o deslocamento que mantém o contorno no lugar."""
    cu = bpy.data.curves.new(nome, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    rd = min(arredondado, h)
    cu.extrude = h - rd
    cu.bevel_depth = rd
    cu.bevel_resolution = 3
    cu.offset = -rd
    sp = cu.splines.new('POLY')
    sp.points.add(len(pontos) - 1)
    for pt, (x, y) in zip(sp.points, pontos):
        pt.co = (x, y, 0.0, 1.0)
    sp.use_cyclic_u = True
    return cu


def malha_torno(nome, pontos, fechado):
    """Meridiano (x, ρ) no plano XY local; o Parafuso gira em volta do X."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, rho, 0.0)) for x, rho in pontos]
    for i in range(len(vs) - 1):
        bm.edges.new((vs[i], vs[i + 1]))
    if fechado:
        bm.edges.new((vs[-1], vs[0]))
    return _malha(nome, bm)


def curva_tubo(nome, pontos, raios):
    cu = bpy.data.curves.new(nome, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pontos) - 1)
    for pt, p, r in zip(sp.points, pontos, raios):
        pt.co = (p[0], p[1], p[2], 1.0)
        pt.radius = r
    return cu


# ---------------------------------------------------------------- peças

# Formas definidas por pontos no referencial da peça: a origem do objeto vai para o centro delas.
LIVRES = ('profile', 'lathe', 'tube', 'capsule', 'roundCone')


def centro_local(p):
    """Centro da peça no referencial dela (a origem do objeto no Blender): o meio da caixa dos pontos; no torno, só
    em X (o giro é em volta do X da peça); nas formas centradas por definição, a origem."""
    s = p['shape']
    if s == 'profile':
        xs, ys = [q[0] for q in p['points']], [q[1] for q in p['points']]
        return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0.0))
    if s == 'lathe':
        xs = [q[0] for q in p['points']]
        return Vector(((min(xs) + max(xs)) / 2, 0.0, 0.0))
    if s == 'tube':
        return Vector([(min(q[i] for q in p['points']) + max(q[i] for q in p['points'])) / 2 for i in range(3)])
    if s in ('capsule', 'roundCone'):
        return (Vector(p['a']) + Vector(p['b'])) / 2
    return Vector((0.0, 0.0, 0.0))


def no_centro(p):
    """A peça com os pontos relativos ao centro (o que vai nos dados do objeto)."""
    c = centro_local(p)
    q = dict(p)
    s = p['shape']
    if s == 'profile':
        q['points'] = [[x - c.x, y - c.y] for x, y in p['points']]
    elif s == 'lathe':
        q['points'] = [[x - c.x, r] for x, r in p['points']]
    elif s == 'tube':
        q['points'] = [[x - c.x, y - c.y, z - c.z] for x, y, z in p['points']]
    elif s in ('capsule', 'roundCone'):
        q['a'] = list(Vector(p['a']) - c)
        q['b'] = list(Vector(p['b']) - c)
    return q


def matriz_peca(p):
    """matrix_world do objeto de uma peça: o referencial dela no jogo, com a origem no centro."""
    return eixos.matriz_blender(p.get('pos'), p.get('rot')) @ Matrix.Translation(centro_local(p))


def criar_peca(p):
    """Objeto do Blender de uma peça da receita (sem matriz: quem chama põe na coleção e posiciona com matriz_peca)."""
    p = no_centro(p)
    s = p['shape']
    nome = p['name']
    mods = []
    if s == 'profile':
        dados = curva_perfil(nome, p['points'], p['h'], p.get('round', 0))
    elif s == 'lathe':
        dados = malha_torno(nome, p['points'], p.get('closed', False))
        mods.append(('PARAFUSO', None))
    elif s == 'tube':
        raios = p['radii'] if 'radii' in p else [p['r']] * len(p['points'])
        dados = curva_tubo(nome, p['points'], raios)
    elif s == 'roundBox':
        dados = malha_caixa(nome, p['size'])
        if p.get('r', 0) > 0:
            mods.append(('BISEL', p['r']))
    elif s == 'cylinder':
        dados = malha_cilindro(nome, p['r'], p['r'], p['h'])
        if p.get('round', 0) > 0:
            mods.append(('BISEL', p['round']))
    elif s == 'cone':
        dados = malha_cilindro(nome, p['r1'], p['r2'], p['h'])
    elif s == 'sphere':
        dados = malha_esfera(nome, (p['r'],) * 3)
    elif s == 'ellipsoid':
        dados = malha_esfera(nome, p['radii'])
    elif s == 'torus':
        dados = malha_toro(nome, p['R'], p['r'])
    elif s == 'capsule':
        dados = malha_capsula(nome, p['a'], p['b'], p['r'], p['r'])
    elif s == 'roundCone':
        dados = malha_capsula(nome, p['a'], p['b'], p['ra'], p['rb'])
    else:
        raise ValueError(f'forma desconhecida: {s}')
    obj = bpy.data.objects.new(nome, dados)
    for tipo, valor in mods:
        if tipo == 'BISEL':
            m = obj.modifiers.new('bisel', 'BEVEL')
            m.width = valor
            m.segments = 3
            m.limit_method = 'NONE'
        elif tipo == 'PARAFUSO':
            m = obj.modifiers.new('parafuso', 'SCREW')
            m.axis = 'X'
            m.angle = 2 * math.pi
            m.steps = SEGMENTOS
            m.render_steps = SEGMENTOS
            m.use_merge_vertices = True
            m.merge_threshold = 1e-4
            m.use_normal_calculate = True
    return obj


def importar(receita, cabecalho, contexto):
    """Monta a cena da receita. Devolve a coleção raiz."""
    limpar_cena()
    cena = bpy.context.scene
    cena['massacre_contexto'] = json.dumps(contexto)
    raiz = bpy.data.collections.new(f"MASSACRE {receita['id']}")
    cena.collection.children.link(raiz)
    topo = {k: receita[k] for k in ('id', 'version', 'refs', 'materials', 'soft') if k in receita}
    raiz['massacre'] = json.dumps({**topo, 'cabecalho': cabecalho, 'ordemAncoras': list(receita['anchors'].keys())})

    faccao = contexto['faccao']
    mats = {}
    for slot, massa in receita['materials'].items():
        if massa in ('acento', 'acento2'):
            m = material(f'massa:{slot}', contexto['acentos'][faccao][massa], 0.6)
        else:
            clay = contexto['massas'][massa]
            m = material(f'massa:{slot}', clay['color'], clay.get('roughness', 0.7))
        m['massacre_massa'] = massa
        mats[slot] = m

    grupos = {}
    for ordem, (g, definicao) in enumerate(receita['groups'].items()):
        col = bpy.data.collections.new(f'grupo:{g}')
        raiz.children.link(col)
        col['massacre_ordem'] = ordem
        grupos[g] = col
        pivo = bpy.data.objects.new(f'pivo:{g}', None)
        pivo.empty_display_type = 'SPHERE'
        pivo.empty_display_size = 0.35
        pivo.matrix_world = eixos.matriz_blender(definicao.get('pivot'))
        pivo['massacre_grupo'] = json.dumps(definicao)
        col.objects.link(pivo)

    for ordem, p in enumerate(receita['parts']):
        obj = criar_peca(p)
        grupos[p['group']].objects.link(obj)
        obj.matrix_world = matriz_peca(p)
        obj.data.materials.append(mats[p['mat']])
        obj['massacre_parte'] = json.dumps(p)
        obj['massacre_ordem'] = float(ordem)
        if p.get('op') == 'subtract':
            obj.display_type = 'WIRE'
            obj.color = COR_CORTE
            obj.show_in_front = True

    ancoras = bpy.data.collections.new('ancoras')
    raiz.children.link(ancoras)
    mao_mat = material('massa:mao', contexto.get('corMao', '#C8553D'))
    for nome, a in receita['anchors'].items():
        e = bpy.data.objects.new(f'ancora:{nome}', None)
        e.empty_display_type = 'ARROWS'
        e.empty_display_size = 1.6
        ancoras.objects.link(e)
        e.matrix_world = eixos.matriz_blender(a['pos'], a.get('rot'))
        e['massacre_ancora'] = json.dumps(a)
        if 'pose' in a:
            e['pose'] = a['pose']  # editável no painel de propriedades (as poses de src/data/hands.js)
        lado = {'maoDireita': 'direita', 'maoEsquerda': 'esquerda'}.get(nome)
        if lado and a.get('pose') in contexto['maos'][lado]:
            proxy = bpy.data.objects.new(f'mao:{nome}', malha_mao(f'mao:{nome}', contexto['maos'][lado][a['pose']]))
            proxy.data.materials.append(mao_mat)
            ancoras.objects.link(proxy)
            proxy.parent = e
            proxy.matrix_parent_inverse = Matrix.Identity(4)
            proxy.hide_select = True
            proxy['massacre_proxy'] = True

    planta = contexto.get('planta')
    if planta:
        col = bpy.data.collections.new('planta (não exporta)')
        raiz.children.link(col)
        boca = receita['anchors'].get('boca', {}).get('pos', [0, 0, 0])
        cu = bpy.data.curves.new('planta', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.05
        cu.bevel_resolution = 2
        for anel in [planta['points'], *planta.get('holes', [])]:
            sp = cu.splines.new('POLY')
            sp.points.add(len(anel) - 1)
            for pt, (x, y) in zip(sp.points, anel):
                pt.co = (x + boca[0], y + boca[1], 0.0, 1.0)
            sp.use_cyclic_u = True
        obj = bpy.data.objects.new('planta', cu)
        obj.data.materials.append(material('planta', COR_PLANTA, 0.9))
        obj.matrix_world = eixos.C.copy()
        obj.hide_select = True
        obj['massacre_planta'] = True
        col.objects.link(obj)
    return raiz
