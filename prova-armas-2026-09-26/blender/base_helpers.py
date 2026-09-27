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


