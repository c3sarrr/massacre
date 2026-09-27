# Materiais de fábrica procedurais das armas realistas (Fase 4.1a; desenho, seções 4.1 e 4.4; vêm da prova de conceito):
# aço oxidado, aço polido, madeira envernizada, polímero/baquelite com ou sem quadriculado. Servem ao modelo alto — as
# renders da conferência e o assar. Cada um tem três nós nomeados, lidos pelo assar.py:
#   canal_aspereza — variação de aspereza em torno de 0,5 (vira _m.g)
#   canal_cor      — variação de cor em torno de 0,5; o veio na madeira (vira _m.a)
#   canal_borda    — máscara de borda (1 na aresta) pelo nó Bevel (vira _m.b, o desgaste)
# As cores de fábrica vêm do contexto (a pintura de fábrica do registro, src/data/armasReais.js).
import math

import bpy

from .unidades import S


def linear(hexa):
    """'#RRGGBB' → (r, g, b) linear."""
    h = hexa.lstrip('#')
    def canal(v):
        c = int(v, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (canal(h[0:2]), canal(h[2:4]), canal(h[4:6]))


def sock(sockets, nome, tipo):
    for s in sockets:
        if s.name == nome and s.type == tipo:
            return s
    raise KeyError(f'{nome} {tipo}')


def novo_mat(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes['Principled BSDF']


def mascara_borda(n, l, raio_mm, de=0.90, ate=0.995):
    """Nó Bevel (normal arredondada) e a máscara de borda: 1 onde a normal arredondada se afasta da geométrica."""
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
    """Ruído nas coordenadas que o nó receber (o veio da madeira liga as dele, esticadas ao longo de X)."""
    t = n.new('ShaderNodeTexNoise')
    t.inputs['Scale'].default_value = escala
    t.inputs['Detail'].default_value = detalhe
    return t


def ruido_mm(n, l, periodo_mm, detalhe=2.0):
    """Ruído no referencial do objeto (as peças nascem com a origem na do mundo, em metros), com o período em mm. A
    variação assada tem de ser maior que o texel (≈ 0,34 mm na textura de 2048 do fuzil): abaixo disso vira ruído de
    pixel — caro de guardar sem perdas e sem sentido no jogo, onde o grão fino é o padrão do acabamento, no shader."""
    tc = n.new('ShaderNodeTexCoord')
    t = ruido(n, 1.0 / (periodo_mm * S), detalhe)
    l.new(tc.outputs['Object'], t.inputs['Vector'])
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


def canal(n, l, nome, fonte=None, valor=0.5):
    """Nó nomeado de um canal assado: um Map Range 0–1 ligado à fonte (ou constante em `valor`)."""
    mr = n.new('ShaderNodeMapRange')
    mr.name = nome
    mr.label = nome
    if fonte is None:
        mr.inputs['Value'].default_value = valor
        mr.inputs['From Min'].default_value = 0.0
        mr.inputs['From Max'].default_value = 1.0
    else:
        l.new(fonte, mr.inputs['Value'])
    return mr


def mat_aco(nome, cor, rug, gasto=(0.30, 0.30, 0.31), borda=0.9):
    """Aço (oxidado, polido, do carregador): aspereza com ruído fino, borda gasta clara, relevo arredondado."""
    m, n, l, b = novo_mat(nome)
    b.inputs['Metallic'].default_value = 1.0
    r = ruido_mm(n, l, 6.0)
    l.new(faixa(n, l, r.outputs['Fac'], rug - 0.07, rug + 0.09), b.inputs['Roughness'])
    bev, borda_m = mascara_borda(n, l, borda)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    rc = ruido_mm(n, l, 30.0, 3.0)
    base = mistura_cor(n, l, faixa(n, l, rc.outputs['Fac'], 0.0, 0.25), cor, tuple(c * 0.8 for c in cor))
    l.new(mistura_cor(n, l, borda_m.outputs['Result'], base, gasto), b.inputs['Base Color'])
    canal(n, l, 'canal_aspereza', r.outputs['Fac'])
    canal(n, l, 'canal_cor', rc.outputs['Fac'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_madeira(nome, claro, escuro):
    """Madeira laminada envernizada: veio fino e alongado ao longo de X, contraste baixo, verniz."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.25, 7.0, 7.0)
    # O centro dos anéis fica longe das peças, embaixo e à direita (a tora de onde a tábua saiu): nas faces o veio corre
    # ao longo do comprimento, em linhas quase retas. Com o centro no eixo do cano (a origem), perto dele o veio virava
    # listras em pé nos lados do guarda-mão e manchas derretidas nas faces de cima.
    mp.inputs['Location'].default_value = (0.0, 1.3, 1.9)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    w = n.new('ShaderNodeTexWave')
    w.wave_type = 'RINGS'
    w.rings_direction = 'X'
    w.inputs['Scale'].default_value = 34.0
    w.inputs['Distortion'].default_value = 14.0
    w.inputs['Detail'].default_value = 3.0
    w.inputs['Detail Roughness'].default_value = 0.7
    l.new(mp.outputs['Vector'], w.inputs['Vector'])
    r = ruido(n, 60.0, 3.0)
    l.new(mp.outputs['Vector'], r.inputs['Vector'])
    mx = n.new('ShaderNodeMath')
    mx.operation = 'MULTIPLY_ADD'
    l.new(w.outputs['Fac'], mx.inputs[0])
    mx.inputs[1].default_value = 0.55
    l.new(r.outputs['Fac'], mx.inputs[2])
    rp = n.new('ShaderNodeValToRGB')
    rp.color_ramp.elements[0].position = 0.35
    rp.color_ramp.elements[0].color = (*escuro, 1)
    rp.color_ramp.elements[1].position = 1.0
    rp.color_ramp.elements[1].color = (*claro, 1)
    l.new(mx.outputs['Value'], rp.inputs['Fac'])
    l.new(rp.outputs['Color'], b.inputs['Base Color'])
    # Verniz acetinado (goma-laca das coronhas da época): com 0,6 de camada e rugosidade 0,18 a face de cima da coronha e
    # dos guarda-mãos virava uma faixa branca sob a luz principal do estúdio.
    b.inputs['Roughness'].default_value = 0.5
    b.inputs['Coat Weight'].default_value = 0.45
    b.inputs['Coat Roughness'].default_value = 0.3
    bev, borda_m = mascara_borda(n, l, 2.0)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    rr = ruido_mm(n, l, 8.0)
    canal(n, l, 'canal_aspereza', rr.outputs['Fac'])
    veio = n.new('ShaderNodeMath')
    veio.operation = 'MULTIPLY'
    l.new(mx.outputs['Value'], veio.inputs[0])
    veio.inputs[1].default_value = 1 / 1.55
    canal(n, l, 'canal_cor', veio.outputs['Value'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_plastico(nome, cor, rug, relevo=0.0, pontilhado_mm=0.7, quadriculado=False):
    """Polímero/baquelite: pontilhado em relevo (relevo > 0, grão de `pontilhado_mm`) ou quadriculado a 45°
    (quadriculado=True)."""
    m, n, l, b = novo_mat(nome)
    r = ruido_mm(n, l, 25.0, 3.0)
    l.new(mistura_cor(n, l, faixa(n, l, r.outputs['Fac'], 0.0, 0.35), cor, tuple(c * 0.7 for c in cor)), b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rug
    bev, borda_m = mascara_borda(n, l, 1.2)
    altura = None
    if quadriculado:
        tc = n.new('ShaderNodeTexCoord')
        onda = []
        for ang in (45.0, -45.0):
            mp = n.new('ShaderNodeMapping')
            mp.inputs['Rotation'].default_value = (math.radians(90), math.radians(ang), 0)
            l.new(tc.outputs['Object'], mp.inputs['Vector'])
            w = n.new('ShaderNodeTexWave')
            w.wave_type = 'BANDS'
            w.inputs['Scale'].default_value = 420.0
            w.inputs['Distortion'].default_value = 0.0
            l.new(mp.outputs['Vector'], w.inputs['Vector'])
            onda.append(w)
        mul = n.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        l.new(onda[0].outputs['Fac'], mul.inputs[0])
        l.new(onda[1].outputs['Fac'], mul.inputs[1])
        altura = mul.outputs['Value']
    elif relevo > 0:
        altura = ruido_mm(n, l, pontilhado_mm).outputs['Fac']
    if altura is not None:
        bp = n.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = 0.55 if quadriculado else relevo
        bp.inputs['Distance'].default_value = 0.0003 if quadriculado else 0.0004
        l.new(altura, bp.inputs['Height'])
        l.new(bev.outputs['Normal'], bp.inputs['Normal'])
        l.new(bp.outputs['Normal'], b.inputs['Normal'])
    else:
        l.new(bev.outputs['Normal'], b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', ruido_mm(n, l, 6.0).outputs['Fac'])
    canal(n, l, 'canal_cor', r.outputs['Fac'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def materiais_de_fabrica(fabrica):
    """Os materiais do modelo alto a partir da pintura de fábrica (zonas → cores do contexto)."""
    z = fabrica['zonas']
    aco = linear(z['corpo']['cor'])
    return {
        'aco': mat_aco('aço oxidado', aco, 0.34, gasto=(0.32, 0.32, 0.34)),
        'aco_detalhes': mat_aco('aço dos detalhes', linear(z['detalhes']['cor']), 0.34, gasto=(0.36, 0.36, 0.38)),
        'aco_carregador': mat_aco('aço do carregador', linear(z['carregador']['cor']), 0.34, gasto=(0.36, 0.37, 0.39)),
        'aco_polido': mat_aco('aço polido', linear(z['interno']['cor']), 0.22, gasto=(0.6, 0.6, 0.6)),
        'madeira': mat_madeira('madeira', linear(z['guarnicao']['cor']), linear(z['guarnicao'].get('cor2') or z['guarnicao']['cor'])),
    }
