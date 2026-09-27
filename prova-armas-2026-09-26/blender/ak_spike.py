# Prova de conceito (rascunho, fora do projeto): AKM modelada por script, com chanfros, materiais PBR e render Cycles.
# Uso: blender -b --factory-startup -P ak_spike.py -- <pasta_saida> [vistas...]
# Medidas em milímetros (convertidas para metros); X para a boca (boca em X = 0), Z para cima, -Y = lado direito.
import bpy, bmesh, math, sys, os
from mathutils import Vector

S = 0.001
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAIDA = ARGS[0] if ARGS else os.path.dirname(__file__)
VISTAS = ARGS[1:] or ['tres', 'lado', 'perto']


def v3(x, y, z):
    return (x * S, y * S, z * S)


# ---------------------------------------------------------------- materiais
def sock(sockets, nome, tipo):
    for s in sockets:
        if s.name == nome and s.type == tipo:
            return s
    raise KeyError(nome + ' ' + tipo)


def novo_mat(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes['Principled BSDF']


def mascara_borda(n, l, raio_mm, de=0.90, ate=0.995):
    bev = n.new('ShaderNodeBevel')
    bev.samples = 8
    bev.inputs['Radius'].default_value = raio_mm * S
    geo = n.new('ShaderNodeNewGeometry')
    dot = n.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    l.new(bev.outputs['Normal'], dot.inputs[0])
    l.new(geo.outputs['Normal'], dot.inputs[1])
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = de
    mr.inputs['From Max'].default_value = ate
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    l.new(sock(dot.outputs, 'Value', 'VALUE'), mr.inputs['Value'])
    return bev, mr


def ruido(n, escala, detalhe=6.0):
    t = n.new('ShaderNodeTexNoise')
    t.inputs['Scale'].default_value = escala
    t.inputs['Detail'].default_value = detalhe
    return t


def faixa(n, l, fonte, a, b):
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = a
    mr.inputs['To Max'].default_value = b
    l.new(fonte, mr.inputs['Value'])
    return mr.outputs['Result']


def mistura_cor(n, l, fator, a, b):
    mx = n.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    l.new(fator, sock(mx.inputs, 'Factor', 'VALUE'))
    ea, eb = sock(mx.inputs, 'A', 'RGBA'), sock(mx.inputs, 'B', 'RGBA')
    if isinstance(a, tuple):
        ea.default_value = (*a, 1)
    else:
        l.new(a, ea)
    if isinstance(b, tuple):
        eb.default_value = (*b, 1)
    else:
        l.new(b, eb)
    return sock(mx.outputs, 'Result', 'RGBA')


def mat_aco(nome, cor, rug, gasto=(0.30, 0.30, 0.31), borda=0.9):
    m, n, l, b = novo_mat(nome)
    b.inputs['Metallic'].default_value = 1.0
    r = ruido(n, 380.0, 8.0)
    l.new(faixa(n, l, r.outputs['Fac'], rug - 0.07, rug + 0.09), b.inputs['Roughness'])
    bev, borda_m = mascara_borda(n, l, borda)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    l.new(mistura_cor(n, l, borda_m.outputs['Result'], cor, gasto), b.inputs['Base Color'])
    return m


def mat_madeira(nome):
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.35, 5.0, 5.0)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    w = n.new('ShaderNodeTexWave')
    w.wave_type = 'RINGS'
    w.inputs['Scale'].default_value = 22.0
    w.inputs['Distortion'].default_value = 9.0
    w.inputs['Detail'].default_value = 3.0
    l.new(mp.outputs['Vector'], w.inputs['Vector'])
    rp = n.new('ShaderNodeValToRGB')
    rp.color_ramp.elements[0].position = 0.15
    rp.color_ramp.elements[0].color = (0.085, 0.022, 0.008, 1)
    rp.color_ramp.elements[1].position = 0.85
    rp.color_ramp.elements[1].color = (0.24, 0.07, 0.022, 1)
    l.new(w.outputs['Fac'], rp.inputs['Fac'])
    l.new(rp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.42
    b.inputs['Coat Weight'].default_value = 0.55
    b.inputs['Coat Roughness'].default_value = 0.18
    bev, _ = mascara_borda(n, l, 2.0)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_plastico(nome, cor, rug, relevo=0.0, escala=900.0):
    m, n, l, b = novo_mat(nome)
    b.inputs['Base Color'].default_value = (*cor, 1)
    r = ruido(n, 40.0, 4.0)
    l.new(mistura_cor(n, l, faixa(n, l, r.outputs['Fac'], 0.0, 0.35), cor, tuple(c * 0.7 for c in cor)), b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rug
    bev, _ = mascara_borda(n, l, 1.2)
    if relevo > 0:
        rr = ruido(n, escala, 2.0)
        bp = n.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = relevo
        bp.inputs['Distance'].default_value = 0.0004
        l.new(rr.outputs['Fac'], bp.inputs['Height'])
        l.new(bev.outputs['Normal'], bp.inputs['Normal'])
        l.new(bp.outputs['Normal'], b.inputs['Normal'])
    else:
        l.new(bev.outputs['Normal'], b.inputs['Normal'])
    return m


# ---------------------------------------------------------------- geometria
def objeto(nome, bm, mat):
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def acabar(ob, chanfro=0.8, seg=3, angulo=32.0):
    if chanfro > 0:
        m = ob.modifiers.new('chanfro', 'BEVEL')
        m.width = chanfro * S
        m.segments = seg
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(angulo)
        m.harden_normals = True
        m.miter_outer = 'MITER_ARC'
        m.use_clamp_overlap = True
    w = ob.modifiers.new('normais', 'WEIGHTED_NORMAL')
    w.keep_sharp = True
    return ob


def prisma(nome, pts, plano, a, b, mat, chanfro=0.8, seg=3):
    """Polígono 2D extrudado. plano 'XZ' (extrude em Y de a até b), 'YZ' (em X) ou 'XY' (em Z)."""
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
    desloc = {'XZ': (0, d, 0), 'YZ': (d, 0, 0), 'XY': (0, 0, d)}[plano]
    bmesh.ops.translate(bm, vec=desloc, verts=novos)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = objeto(nome, bm, mat)
    ob['chanfro'] = (chanfro, seg)
    return ob


def torno(nome, perfil, mat, seg=48, eixo='X', centro=(0, 0, 0), chanfro=0.5):
    """perfil: lista (posição ao longo do eixo, raio) em mm; gira em torno de X (ou Z)."""
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
    ob = objeto(nome, bm, mat)
    ob['chanfro'] = (chanfro, 2)
    return ob


def esfera(nome, centro, raio, escala, mat, u=24, v=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=raio * S)
    bmesh.ops.scale(bm, vec=escala, verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=v3(*centro), verts=bm.verts[:])
    ob = objeto(nome, bm, mat)
    ob['chanfro'] = (0, 0)
    return ob


def caixa(nome, minimo, maximo, mat, chanfro=0.6):
    x0, y0, z0 = minimo
    x1, y1, z1 = maximo
    return prisma(nome, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], 'XZ', y0, y1, mat, chanfro)


def cortar(alvo, cortador):
    m = alvo.modifiers.new('corte', 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    m.object = cortador
    m.solver = 'EXACT'
    cortador.hide_render = True
    cortador.hide_viewport = True
    cortador['cortador'] = True


def unir(alvo, outro):
    m = alvo.modifiers.new('uniao', 'BOOLEAN')
    m.operation = 'UNION'
    m.object = outro
    m.solver = 'EXACT'
    outro.hide_render = True
    outro.hide_viewport = True
    outro['cortador'] = True


def arco(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def rotacionar(ob, eixo, graus, pivo):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    from mathutils import Matrix
    bmesh.ops.rotate(bm, verts=bm.verts[:], cent=v3(*pivo), matrix=Matrix.Rotation(math.radians(graus), 3, eixo))
    bm.to_mesh(ob.data)
    bm.free()


# ---------------------------------------------------------------- a arma
def construir():
    aco = mat_aco('aço fosfatizado', (0.028, 0.028, 0.030), 0.42)
    aco_claro = mat_aco('aço polido', (0.42, 0.42, 0.43), 0.22, gasto=(0.6, 0.6, 0.6))
    madeira = mat_madeira('madeira laminada')
    baquelite = mat_plastico('baquelite ameixa', (0.20, 0.035, 0.018), 0.34)
    punho = mat_plastico('punho', (0.035, 0.022, 0.016), 0.55, relevo=0.35, escala=1400.0)

    # Receptor estampado (perfil lateral, 32 mm de largura)
    rec = prisma('receptor', [(-715, 6), (-472, 6), (-470, 3), (-470, -28), (-484, -38), (-700, -38), (-712, -33), (-715, -24)], 'XZ', -16, 16, aco, 0.7)
    # janela de ejeção no lado direito e o ferrolho polido aparecendo
    janela = caixa('janela', (-640, -30, -3), (-566, -13, 8), aco, 0)
    cortar(rec, janela)
    ferrolho = caixa('ferrolho', (-636, -13.5, -2), (-570, 8, 7), aco_claro, 0.4)
    # covinhas da AKM acima do alojamento do carregador (dos dois lados)
    for y in (-16.8, 16.8):
        cov = esfera('covinha', (-583, y * 0.99, -21), 5, (1.5, 0.3, 0.9), aco)
        cortar(rec, cov)
    # rebites dos munhões e pinos do grupo do gatilho
    rebites = [(-480, -8), (-480, -24), (-493, -16), (-506, -8), (-506, -24), (-707, -6), (-707, -22), (-656, -27), (-629, -27), (-611, -21)]
    for x, z in rebites:
        for y in (-16.2, 16.2):
            esfera('rebite', (x, y, z), 2.6, (1.0, 0.45, 1.0), aco, 16, 8)

    # Tampa do receptor (arco) com nervuras transversais e o botão da mola
    def arco_tampa(folga):
        pts = [(-17.0 - folga, 4)]
        for i in range(21):
            t = math.pi * i / 20
            pts.append((-(17.0 + folga) * math.cos(t), 11 + (11.5 + folga) * math.sin(t)))
        pts.append((17.0 + folga, 4))
        return pts
    tampa = prisma('tampa', arco_tampa(0), 'YZ', -704, -482, aco, 0.6)
    for i in range(7):
        x = -690 + i * 27
        prisma('nervura', arco_tampa(0.9), 'YZ', x, x + 3.2, aco, 0.5)
    torno('botão da mola', [(-712, 0), (-712, 5.5), (-703, 5.5), (-703, 0)], aco, 32, centro=(0, 0, 13), chanfro=0.8)

    # Munhão/base da alça de mira e alça de mira de folha
    base_alca = prisma('base da alça', [(-472, -14), (-418, -14), (-418, 16), (-430, 26), (-468, 26), (-472, 18)], 'XZ', -13, 13, aco, 0.8)
    folha = prisma('folha da alça', [(-462, 25), (-392, 29.5), (-392, 33), (-455, 30.5), (-462, 30)], 'XZ', -7.5, 7.5, aco, 0.4)
    entalhe = caixa('entalhe', (-466, -2, 26), (-455, 2, 40), aco, 0)
    cortar(folha, entalhe)
    caixa('cursor da alça', (-430, -9, 25.5), (-421, 9, 33), aco, 0.5)

    # Cano, bloco de gases, tubo de gases, massa de mira e quebra-chamas oblíquo
    torno('cano', [(-470, 0), (-470, 9.5), (-400, 9.2), (-250, 8.6), (-78, 8.1), (-30, 7.6), (-30, 0)], aco, 48)
    bloco = prisma('bloco de gases', [(-248, -12), (-218, -12), (-214, 6), (-224, 34), (-248, 34)], 'XZ', -11, 11, aco, 1.0)
    tubo = torno('tubo de gases', [(-292, 0), (-292, 10.5), (-246, 10.5), (-246, 0)], aco, 40, centro=(0, 0, 22))
    for x in (-287, -279, -271):
        furo = torno('respiro', [(-14, 0), (-14, 2.3), (14, 2.3), (14, 0)], aco, 20, eixo='Z', centro=(x, 0, 22))
        rotacionar(furo, 'X', 90, (x, 0, 22))
        cortar(tubo, furo)
    caixa('braçadeira', (-258, -23, -34), (-249, 23, 14), aco, 0.8)
    torno('luva da mira', [(-76, 0), (-76, 13), (-42, 13), (-42, 0)], aco, 40)
    prisma('torre da mira', [(-74, 8), (-44, 8), (-50, 36), (-66, 36)], 'XZ', -9, 9, aco, 0.9)
    for y in (-10.5, 8.0):
        prisma('orelha da mira', [(-66, 18), (-50, 18)] + arco(-58, 40, 8, 0, 180, 10), 'XZ', y, y + 2.5, aco, 0.6)
    torno('massa de mira', [(35, 0), (35, 1.3), (47, 1.3), (47, 0)], aco, 16, eixo='Z', centro=(-58, 0, 0))
    caixa('talão da baioneta', (-72, -4, -24), (-50, 4, -12), aco, 0.6)
    freio = torno('quebra-chamas', [(-36, 0), (-36, 11), (0, 11), (0, 0)], aco, 48)
    corte_obliquo = prisma('corte oblíquo', [(-9, 12), (5, 12), (5, -12), (0, -12)], 'XZ', -15, 15, aco, 0)
    cortar(freio, corte_obliquo)
    alma = torno('alma', [(-40, 0), (-40, 4.1), (6, 4.1), (6, 0)], aco, 24)
    cortar(freio, alma)
    torno('vareta', [(-265, 0), (-265, 3.1), (-60, 3.1), (-60, 0)], aco, 20, centro=(0, 0, -16))
    torno('cabeça da vareta', [(-62, 0), (-62, 4.5), (-54, 4.5), (-54, 0)], aco, 20, centro=(0, 0, -16))

    # Guarda-mão inferior com as abas da AKM e guarda-mão superior sobre o tubo
    gm = prisma('guarda-mão inferior', [(-420, 6), (-262, 6), (-262, -22), (-272, -34), (-300, -40), (-360, -41), (-398, -38), (-414, -30), (-420, -18)], 'XZ', -21, 21, madeira, 2.2)
    for vt in gm.data.vertices:
        t = min(1.0, max(0.0, (-vt.co.z / S - 8) / 30))
        vt.co.y *= 1.0 + 0.14 * t
    prisma('guarda-mão superior', [(-9, 12)] + arco(0, 22, 13.5, 200, -20, 16) + [(9, 12)], 'YZ', -419, -294, madeira, 1.6)

    # Carregador de baquelite curvo (arcos com o mesmo centro), com nervuras e a base de aço
    cx, cz = -150, -30
    costas = [(cx + 453 * math.cos(math.radians(a)), cz + 453 * math.sin(math.radians(a))) for a in [181 + i * 1.3 for i in range(21)]]
    frente = [(cx + 400 * math.cos(math.radians(a)), cz + 400 * math.sin(math.radians(a))) for a in [181.2 + i * 1.3 for i in range(21)]]
    prisma('carregador', costas + frente[::-1], 'XZ', -13.5, 13.5, baquelite, 1.2)
    for r in (416, 437):
        faixa_pts = [(cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))) for a in [183 + i * 1.1 for i in range(21)]]
        faixa_int = [(cx + (r - 3.2) * math.cos(math.radians(a)), cz + (r - 3.2) * math.sin(math.radians(a))) for a in [183 + i * 1.1 for i in range(21)]]
        for y0, y1 in ((-14.6, -13.2), (13.2, 14.6)):
            prisma('nervura do carregador', faixa_pts + faixa_int[::-1], 'XZ', y0, y1, baquelite, 0.5)
    a_fim = math.radians(181 + 20 * 1.3)
    b0 = (cx + 457 * math.cos(a_fim), cz + 457 * math.sin(a_fim))
    b1 = (cx + 396 * math.cos(a_fim + 0.003), cz + 396 * math.sin(a_fim + 0.003))
    tx, tz = -math.sin(a_fim), math.cos(a_fim)
    base_pts = [(b0[0] - tx, b0[1] - tz), (b1[0] - tx, b1[1] - tz), (b1[0] + tx * 6, b1[1] + tz * 6), (b0[0] + tx * 6, b0[1] + tz * 6)]
    prisma('base do carregador', base_pts, 'XZ', -15, 15, aco, 0.9)

    # Guarda-mato, gatilho, punho, seletor e alavanca de manejo
    guarda = [(-658, -36), (-652, -58), (-642, -64), (-606, -64), (-600, -36), (-605, -36), (-610, -59), (-640, -59), (-647, -55), (-652, -36)]
    prisma('guarda-mato', guarda, 'XZ', -5, 5, aco, 0.6)
    prisma('gatilho', [(-632, -37), (-626, -37), (-625, -44), (-629, -52), (-634, -55), (-632, -50), (-630, -45)], 'XZ', -3, 3, aco, 0.5)
    pg = prisma('punho', [(-672, -36), (-640, -36), (-648, -70), (-670, -128), (-684, -134), (-700, -128), (-694, -96)], 'XZ', -15, 15, punho, 5.0)
    prisma('retém do carregador', [(-606, -37), (-600, -37), (-603, -49), (-612, -58), (-616, -56), (-609, -48)], 'XZ', -7, 7, aco, 0.5)
    pg['chanfro'] = (5.0, 5)
    prisma('seletor', [(-697, 0), (-688, 7), (-560, 7), (-552, 2), (-556, -3), (-567, -1), (-575, -12), (-583, -12), (-583, -2), (-688, -4)], 'XZ', -18.8, -16.8, aco, 0.5)
    eixo_sel = torno('eixo do seletor', [(16.5, 0), (16.5, 5.5), (20.5, 5.5), (20.5, 0)], aco, 24, eixo='Z', centro=(-690, 0, 0))
    rotacionar(eixo_sel, 'X', 90, (-690, 0, 0))
    haste = torno('manejo', [(-2, 0), (-2, 3.6), (22, 3.6), (22, 0)], aco_claro, 20, eixo='Z', centro=(-515, 0, 9))
    rotacionar(haste, 'X', 90, (-515, 0, 9))
    esfera('bola do manejo', (-515, -35, 11), 6.2, (1.0, 1.0, 1.25), aco_claro)

    # Coronha de madeira com afinamento, soleira de aço com a tampa do compartimento
    coronha = prisma('coronha', [(-715, 8), (-715, -30), (-740, -46), (-874, -148), (-874, -26), (-760, -6)], 'XZ', -18, 18, madeira, 3.0)
    coronha['chanfro'] = (3.0, 4)
    for vt in coronha.data.vertices:
        t = min(1.0, max(0.0, (-vt.co.x / S - 715) / 159))
        vt.co.y *= 0.82 + 0.26 * t
    prisma('soleira', [(-882, -150), (-873, -150), (-873, -24), (-882, -24)], 'XZ', -21, 21, aco, 1.2)
    caixa('tampa da soleira', (-883, -12, -120), (-881, 12, -60), aco, 0.4)


def finalizar():
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.get('cortador'):
            continue
        c, s = ob.get('chanfro', (0.6, 3))
        acabar(ob, c, int(s))


# ---------------------------------------------------------------- estúdio
def estudio():
    sc = bpy.context.scene
    w = bpy.data.worlds.new('mundo')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.018, 0.017, 0.016, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    chao = bpy.data.materials.new('fundo')
    chao.use_nodes = True
    chao.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05, 0.048, 0.045, 1)
    chao.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3.0)
    bmesh.ops.translate(bm, vec=(-0.45, 0.2, -0.27), verts=bm.verts[:])
    objeto('fundo', bm, chao)

    def luz(nome, pos, alvo, tam, energia, cor):
        d = bpy.data.lights.new(nome, 'AREA')
        d.size = tam
        d.energy = energia
        d.color = cor
        o = bpy.data.objects.new(nome, d)
        sc.collection.objects.link(o)
        o.location = pos
        dirv = Vector(alvo) - Vector(pos)
        o.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
    luz('principal', (-0.2, -0.9, 0.9), (-0.45, 0, -0.05), 1.2, 30, (1.0, 0.9, 0.78))
    luz('preenchimento', (-0.9, -0.7, 0.2), (-0.45, 0, -0.05), 1.0, 9, (0.75, 0.85, 1.0))
    luz('recorte', (-0.5, 0.9, 0.5), (-0.45, 0, -0.05), 0.8, 22, (1.0, 1.0, 1.0))
    luz('topo', (-0.45, 0.0, 1.2), (-0.45, 0, 0), 1.8, 14, (1.0, 0.97, 0.92))


def camera(nome, pos, alvo, lente, orto=None):
    sc = bpy.context.scene
    d = bpy.data.cameras.new(nome)
    d.lens = lente
    d.clip_start = 0.005
    if orto:
        d.type = 'ORTHO'
        d.ortho_scale = orto
    o = bpy.data.objects.new(nome, d)
    sc.collection.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    return o


def gpu():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for tipo in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            achou = [d for d in prefs.devices if d.type == tipo]
            if achou:
                for d in prefs.devices:
                    d.use = d.type == tipo
                sc.cycles.device = 'GPU'
                return tipo
        except Exception:
            pass
    return 'CPU'


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    construir()
    finalizar()
    estudio()
    sc = bpy.context.scene
    dev = gpu()
    sc.cycles.samples = 160
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 900
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    cams = {
        'tres': camera('tres', (-0.16, -0.78, 0.26), (-0.44, 0.0, -0.06), 50),
        'lado': camera('lado', (-0.44, -1.5, -0.055), (-0.44, 0.0, -0.055), 50, orto=0.98),
        'perto': camera('perto', (-0.50, -0.26, 0.085), (-0.60, 0.0, -0.015), 55),
    }
    for nome in VISTAS:
        sc.camera = cams[nome]
        sc.render.filepath = os.path.join(SAIDA, f'ak_{nome}.png')
        bpy.ops.render.render(write_still=True)
        print('render', nome, dev)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, 'ak_spike.blend'))


main()
