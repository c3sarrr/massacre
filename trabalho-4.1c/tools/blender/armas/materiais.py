# Materiais de fábrica procedurais das armas realistas (Fase 4.1a; desenho, seções 4.1 e 4.4; vêm da prova de conceito):
# aço oxidado, aço polido, madeira envernizada, polímero/baquelite com ou sem quadriculado; e os das luvas (Fase 4.1b;
# desenho da 4.1b, seção 3.4): couro sintético, tecido elástico e borracha moldada. Servem ao modelo alto — as renders
# da conferência e o assar. Cada um tem três nós nomeados, lidos pelo assar.py:
#   canal_aspereza — variação de aspereza em torno de 0,5 (vira _m.g)
#   canal_cor      — variação de cor em torno de 0,5; o veio na madeira (vira _m.a)
#   canal_borda    — máscara de borda (1 na aresta) pelo nó Bevel (vira _m.b, o desgaste)
# As cores de fábrica vêm do contexto (a pintura de fábrica do registro, src/data/armasReais.js).
import math

import bpy

from . import texturas
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


def mat_madeira(nome, claro, escuro, veio):
    """Madeira envernizada (a goma-laca das coronhas da época) com o veio de uma madeira de verdade (revisão crítica da
    P1 da 4.1c): a luminância da lâmina de cerejeira CC0 (texturas.py, fontes.json), normalizada — 0,5 na média, os
    extremos a 2,5 desvios — e projetada em caixa no referencial do objeto com o veio ao longo de X (1 m de textura =
    1 m de peça, a medida dela), vai para o canal A (o veio no jogo, na cor da skin) e pinta o modelo alto com a mesma
    conta do jogo (`veio` de src/data/acabamentos.js: a mistura para a cor escura de `claro` a `escuro` no canal, até
    `peso`, e o brilho que acompanha o canal). Os veios escuros ficam um pouco mais ásperos (o poro). A peça cortada em
    outra direção gira o veio pelo atributo `giro_veio` da malha (radianos em volta do Y do Blender, nos vértices: o
    punho da AK, com o veio ao longo do eixo dele) — atributo da malha e não propriedade do objeto, que o assar perde ao
    juntar as fontes numa só. Antes eram anéis de onda a cada 4 mm em contraste alto: listras iguais de desenho
    animado."""
    m, n, l, b = novo_mat(nome)
    img, reg = texturas.imagem('cherry_veneer', 'cherry_veneer_diff_2k.jpg')
    media, desvio = texturas.luminancia(img)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1000.0 / reg['mm'][0], 1000.0 / reg['mm'][1], 1000.0 / reg['mm'][0])
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    giro = n.new('ShaderNodeAttribute')
    giro.attribute_type = 'GEOMETRY'
    giro.attribute_name = 'giro_veio'
    rot = n.new('ShaderNodeCombineXYZ')
    l.new(giro.outputs['Fac'], rot.inputs['Y'])
    l.new(rot.outputs['Vector'], mp.inputs['Rotation'])
    tx = n.new('ShaderNodeTexImage')
    tx.image = img
    tx.projection = 'BOX'
    tx.projection_blend = 0.25
    tx.interpolation = 'Cubic'
    l.new(mp.outputs['Vector'], tx.inputs['Vector'])
    bw = n.new('ShaderNodeRGBToBW')
    l.new(tx.outputs['Color'], bw.inputs['Color'])
    g = n.new('ShaderNodeMapRange')
    g.clamp = True
    g.inputs['From Min'].default_value = media - 2.5 * desvio
    g.inputs['From Max'].default_value = media + 2.5 * desvio
    l.new(bw.outputs['Val'], g.inputs['Value'])
    a = g.outputs['Result']
    escurece = n.new('ShaderNodeMapRange')
    escurece.interpolation_type = 'SMOOTHSTEP'
    escurece.inputs['From Min'].default_value = veio['escuro']
    escurece.inputs['From Max'].default_value = veio['claro']
    escurece.inputs['To Min'].default_value = veio['peso']
    escurece.inputs['To Max'].default_value = 0.0
    l.new(a, escurece.inputs['Value'])
    cor = mistura_cor(n, l, escurece.outputs['Result'], claro, escuro)
    brilho = n.new('ShaderNodeVectorMath')
    brilho.operation = 'SCALE'
    l.new(cor, brilho.inputs[0])
    l.new(faixa(n, l, a, 1.0 - veio['brilho'], 1.0 + veio['brilho']), sock(brilho.inputs, 'Scale', 'VALUE'))
    l.new(brilho.outputs['Vector'], b.inputs['Base Color'])
    # Verniz acetinado: com 0,6 de camada e rugosidade 0,18 a face de cima da coronha e dos guarda-mãos virava uma faixa
    # branca sob a luz principal do estúdio.
    b.inputs['Roughness'].default_value = 0.5
    b.inputs['Coat Weight'].default_value = 0.45
    b.inputs['Coat Roughness'].default_value = 0.3
    bev, borda_m = mascara_borda(n, l, 2.0)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', faixa(n, l, a, 0.8, 0.2))
    canal(n, l, 'canal_cor', a)
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_plastico(nome, cor, rug):
    """Polímero moldado (e as pinturas foscas e acetinadas; correções da P1 da 4.1c): a aspereza do acabamento com uma
    ondulação leve de 3 mm (o brilho do molde nunca é igual em tudo), a cor lisa com a variação larga e fraca do lote,
    e o grão fino do molde num relevo `fino` de 0,12 mm (só nas renders do modelo alto; no jogo é o padrão `molde`). A
    textura das regiões do punho (o pontilhado, o quadriculado) é o relevo moldado (relevo.py). Antes era um ruído de
    0,7 mm em relevo na peça inteira, com aspereza 0,65 igual em tudo: a lixa que lia como impressão 3D."""
    m, n, l, b = novo_mat(nome)
    r = ruido_mm(n, l, 40.0, 2.0)
    l.new(mistura_cor(n, l, faixa(n, l, r.outputs['Fac'], 0.0, 0.12), cor, tuple(c * 0.85 for c in cor)), b.inputs['Base Color'])
    ondulacao = ruido_mm(n, l, 3.0, 2.0)
    l.new(faixa(n, l, ondulacao.outputs['Fac'], rug - 0.035, rug + 0.035), b.inputs['Roughness'])
    bev, borda_m = mascara_borda(n, l, 1.2)
    grao = ruido_mm(n, l, 0.12, 1.0)
    l.new(_relevo(n, l, grao.outputs['Fac'], 0.1, 0.02, bev.outputs['Normal'], fino=True), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', ruido_mm(n, l, 6.0).outputs['Fac'])
    canal(n, l, 'canal_cor', r.outputs['Fac'])
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def escala_da_onda(periodo_mm):
    """Escala do nó Wave (bandas ao longo de um eixo) para o período dado: o Blender faz sen(20·escala·coordenada), então
    a onda repete a cada 2π/(20·escala) na coordenada (metros)."""
    return 2 * math.pi / (20.0 * periodo_mm * S)


def _relevo(n, l, altura, forca, distancia_mm, normal_de_baixo, fino=False):
    """Nó Bump sobre a normal arredondada da borda: `altura` (0–1) com a força e a distância (mm) dadas. `fino`: um
    relevo menor do que a textura assada guarda (período abaixo de uns 8 texels) — fica nas renders do modelo alto e
    sai do assar (assar.assar_grupos desliga os nós `fino`); no jogo ele vem do shader, procedural."""
    bp = n.new('ShaderNodeBump')
    if fino:
        bp.label = 'fino'
    bp.inputs['Strength'].default_value = forca
    bp.inputs['Distance'].default_value = distancia_mm * S
    l.new(altura, bp.inputs['Height'])
    l.new(normal_de_baixo, bp.inputs['Normal'])
    return bp.outputs['Normal']


def _no_atributo(n, nome):
    """A saída de um atributo de geometria do modelo alto (0 onde a malha não tem o atributo: a de jogo)."""
    a = n.new('ShaderNodeAttribute')
    a.attribute_type = 'GEOMETRY'
    a.attribute_name = nome
    return a.outputs['Fac']


def _conta(n, l, op, a, b=None, c=None):
    """Nó Math `op` com as entradas (números ou saídas); devolve a saída."""
    no = n.new('ShaderNodeMath')
    no.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            no.inputs[i].default_value = x
        else:
            l.new(x, no.inputs[i])
    return no.outputs['Value']


def _degrau(n, l, x, de, ate):
    """smoothstep(de, ate, x) pelo Map Range."""
    mr = n.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = de
    mr.inputs['From Max'].default_value = ate
    l.new(x, mr.inputs['Value'])
    return mr.outputs['Result']


def _gauss(n, l, x, centro, sigma):
    """exp(-((x - centro)/sigma)²)."""
    q = _conta(n, l, 'DIVIDE', _conta(n, l, 'SUBTRACT', x, centro), sigma)
    return _conta(n, l, 'EXPONENT', _conta(n, l, 'MULTIPLY', _conta(n, l, 'MULTIPLY', q, q), -1.0))


def costura(n, l):
    """O sulco e os pontos das costuras pelos atributos do modelo alto (maos_alto.py): `costura_d` (a distância à linha,
    mm), `costura_s` (o comprimento ao longo dela, mm) e `costura_ok` (1 no modelo alto). O sulco na linha (0,45 mm de
    meia largura) e uma fileira de pontos de cada lado a 1 mm, com o passo de 2,5 mm e o fio de 1,6 mm. Devolve (altura
    em 0–1 com 0,5 neutro, o sulco já multiplicado por `costura_ok`)."""
    d = _no_atributo(n, 'costura_d')
    s = _no_atributo(n, 'costura_s')
    ok = _no_atributo(n, 'costura_ok')
    sulco = _conta(n, l, 'MULTIPLY', _gauss(n, l, d, 0.0, 0.45), ok)
    fileira = _gauss(n, l, d, 1.0, 0.22)
    fase = _conta(n, l, 'FRACT', _conta(n, l, 'DIVIDE', s, 2.5))
    liga = _conta(n, l, 'MULTIPLY', _degrau(n, l, fase, 0.04, 0.12),
                  _conta(n, l, 'SUBTRACT', 1.0, _degrau(n, l, fase, 0.64, 0.72)))
    pontos = _conta(n, l, 'MULTIPLY', _conta(n, l, 'MULTIPLY', fileira, liga), ok)
    altura = _conta(n, l, 'ADD', _conta(n, l, 'SUBTRACT', _conta(n, l, 'MULTIPLY', pontos, 0.35),
                                          _conta(n, l, 'MULTIPLY', sulco, 0.45)), 0.5)
    return altura, sulco


def _pontinhos(n, l, periodo_mm, raio, plano=False):
    """Pontinhos em cúpula numa grade regular (Voronoi F1 sem aleatoriedade: a distância ao centro da célula), com o
    raio em fração do período: 1 no alto, 0 fora. `plano`: a grade no plano XY do objeto, projetada de baixo (a
    palma olha para -Z); a grade em 3D, fatiada por uma superfície curva, deixava faixas sem pontinho."""
    tc = n.new('ShaderNodeTexCoord')
    vor = n.new('ShaderNodeTexVoronoi')
    if plano:
        vor.voronoi_dimensions = '2D'
    vor.feature = 'F1'
    vor.inputs['Scale'].default_value = 1.0 / (periodo_mm * S)
    vor.inputs['Randomness'].default_value = 0.0
    l.new(tc.outputs['Object'], vor.inputs['Vector'])
    q = _conta(n, l, 'DIVIDE', sock(vor.outputs, 'Distance', 'VALUE'), raio)
    return _conta(n, l, 'MAXIMUM', _conta(n, l, 'SUBTRACT', 1.0, _conta(n, l, 'MULTIPLY', q, q)), 0.0)


def _escurecer_no_sulco(n, l, cor_saida, sulco):
    """A cor escurecida no sulco da costura (a sujeira que junta ali)."""
    return mistura_cor(n, l, _conta(n, l, 'MULTIPLY', sulco, 0.45), cor_saida, (0.0, 0.0, 0.0))


def mat_couro(nome, cor):
    """Couro sintético da palma e das pontas (tipo camurça sintética de luva tática): grão de poros de ~0,7 mm, manchas
    leves de tingimento, aspereza média com brilho leve."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    vor = n.new('ShaderNodeTexVoronoi')
    vor.feature = 'F1'
    vor.inputs['Scale'].default_value = 1.0 / (0.7 * S)
    vor.inputs['Randomness'].default_value = 0.9
    l.new(tc.outputs['Object'], vor.inputs['Vector'])
    fino = ruido_mm(n, l, 0.35, 2.0)
    grao = n.new('ShaderNodeMath')
    grao.operation = 'MULTIPLY_ADD'
    l.new(sock(vor.outputs, 'Distance', 'VALUE'), grao.inputs[0])
    grao.inputs[1].default_value = 0.8
    l.new(fino.outputs['Fac'], grao.inputs[2])
    mancha = ruido_mm(n, l, 18.0, 3.0)
    alt_costura, sulco = costura(n, l)
    base_cor = mistura_cor(n, l, faixa(n, l, mancha.outputs['Fac'], 0.0, 0.3), cor, tuple(c * 0.82 for c in cor))
    l.new(_escurecer_no_sulco(n, l, base_cor, sulco), b.inputs['Base Color'])
    asp = ruido_mm(n, l, 4.0)
    l.new(faixa(n, l, asp.outputs['Fac'], 0.49, 0.61), b.inputs['Roughness'])
    b.inputs['Sheen Weight'].default_value = 0.15
    bev, borda_m = mascara_borda(n, l, 0.8)
    normal = _relevo(n, l, grao.outputs['Value'], 0.3, 0.12, bev.outputs['Normal'], fino=True)
    # O painel de reforço da palma: pontinhos antiderrapantes de 0,3 mm num passo de 1,4 mm.
    anti = _conta(n, l, 'MULTIPLY', _pontinhos(n, l, 1.4, 0.3, plano=True), _no_atributo(n, 'antiderrapante'))
    normal = _relevo(n, l, anti, 0.8, 0.25, normal)
    l.new(_relevo(n, l, alt_costura, 1.0, 0.35, normal), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', asp.outputs['Fac'])
    canal(n, l, 'canal_cor', _conta(n, l, 'MULTIPLY', mancha.outputs['Fac'], _conta(n, l, 'SUBTRACT', 1.0,
                                                                                   _conta(n, l, 'MULTIPLY', sulco, 0.6))))
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_tecido(nome, cor):
    """Tecido elástico das costas e dos lados (malha de poliéster e elastano): as nervuras de 0,9 mm ao longo da mão
    cruzadas pelas carreiras de 0,6 mm, aspereza alta e o brilho de tecido (sheen) nos ângulos rasantes."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    ondas = []
    for eixo, periodo, torcer in (('X', 0.9, 1.5), ('Y', 0.6, 0.8)):
        w = n.new('ShaderNodeTexWave')
        w.wave_type = 'BANDS'
        w.bands_direction = eixo
        w.inputs['Scale'].default_value = escala_da_onda(periodo)
        w.inputs['Distortion'].default_value = torcer
        w.inputs['Detail'].default_value = 1.0
        l.new(tc.outputs['Object'], w.inputs['Vector'])
        ondas.append(w)
    malha = n.new('ShaderNodeMath')
    malha.operation = 'MULTIPLY'
    l.new(ondas[0].outputs['Fac'], malha.inputs[0])
    l.new(ondas[1].outputs['Fac'], malha.inputs[1])
    tinta = ruido_mm(n, l, 25.0, 3.0)
    alt_costura, sulco = costura(n, l)
    base_cor = mistura_cor(n, l, faixa(n, l, tinta.outputs['Fac'], 0.0, 0.2), cor, tuple(c * 0.85 for c in cor))
    l.new(_escurecer_no_sulco(n, l, base_cor, sulco), b.inputs['Base Color'])
    asp = ruido_mm(n, l, 5.0)
    l.new(faixa(n, l, asp.outputs['Fac'], 0.84, 0.93), b.inputs['Roughness'])
    # O brilho de tecido na cor da própria trama (um tom acima): com o branco, a malha marrom lia como pele.
    b.inputs['Sheen Weight'].default_value = 0.35
    b.inputs['Sheen Roughness'].default_value = 0.5
    b.inputs['Sheen Tint'].default_value = (*tuple(min(1.0, c * 1.3) for c in cor), 1)
    bev, borda_m = mascara_borda(n, l, 0.8)
    normal = _relevo(n, l, malha.outputs['Value'], 0.35, 0.15, bev.outputs['Normal'], fino=True)
    l.new(_relevo(n, l, alt_costura, 1.0, 0.35, normal), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', asp.outputs['Fac'])
    canal(n, l, 'canal_cor', _conta(n, l, 'MULTIPLY', tinta.outputs['Fac'], _conta(n, l, 'SUBTRACT', 1.0,
                                                                                  _conta(n, l, 'MULTIPLY', sulco, 0.6))))
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def mat_borracha(nome, cor):
    """Borracha moldada (TPR) do protetor, das almofadas e da tira: o pontilhado fino do molde (0,35 mm), aspereza de
    borracha e um brilho leve nas quinas gastas."""
    m, n, l, b = novo_mat(nome)
    pont = ruido_mm(n, l, 0.35, 1.0)
    manchas = ruido_mm(n, l, 22.0, 3.0)
    alt_costura, sulco = costura(n, l)
    base_cor = mistura_cor(n, l, faixa(n, l, manchas.outputs['Fac'], 0.0, 0.18), cor, tuple(c * 0.88 for c in cor))
    l.new(_escurecer_no_sulco(n, l, base_cor, sulco), b.inputs['Base Color'])
    asp = ruido_mm(n, l, 4.0)
    l.new(faixa(n, l, asp.outputs['Fac'], 0.58, 0.7), b.inputs['Roughness'])
    bev, borda_m = mascara_borda(n, l, 0.6)
    normal = _relevo(n, l, pont.outputs['Fac'], 0.22, 0.1, bev.outputs['Normal'], fino=True)
    # O puxador: o gancho do velcro, pontinhos densos de 0,15 mm num passo de 0,45 mm.
    gancho = _conta(n, l, 'MULTIPLY', _pontinhos(n, l, 0.45, 0.33), _no_atributo(n, 'velcro'))
    normal = _relevo(n, l, gancho, 0.9, 0.15, normal, fino=True)
    # A tira: nervuras moldadas em diagonal (passo de 3,2 mm), como a banda de TPR do fecho. A tira dá a volta no
    # punho (o eixo X): a diagonal é entre o X e o arco em volta dele (o ângulo vezes o raio do punho, ~33 mm).
    tc = n.new('ShaderNodeTexCoord')
    xyz = n.new('ShaderNodeSeparateXYZ')
    l.new(tc.outputs['Object'], xyz.inputs['Vector'])
    arco = _conta(n, l, 'MULTIPLY', _conta(n, l, 'ARCTAN2', xyz.outputs['Y'], xyz.outputs['Z']), 33.0 * S)
    diagonal = _conta(n, l, 'MULTIPLY', _conta(n, l, 'ADD', xyz.outputs['X'], arco), math.sqrt(0.5))
    onda = _conta(n, l, 'SINE', _conta(n, l, 'MULTIPLY', diagonal, 2 * math.pi / (3.2 * S)))
    nervuras = _conta(n, l, 'MULTIPLY', _degrau(n, l, onda, 0.35, 0.8), _no_atributo(n, 'tira'))
    normal = _relevo(n, l, nervuras, 0.8, 0.3, normal)
    l.new(_relevo(n, l, alt_costura, 1.0, 0.35, normal), b.inputs['Normal'])
    canal(n, l, 'canal_aspereza', asp.outputs['Fac'])
    canal(n, l, 'canal_cor', _conta(n, l, 'MULTIPLY', manchas.outputs['Fac'], _conta(n, l, 'SUBTRACT', 1.0,
                                                                                    _conta(n, l, 'MULTIPLY', sulco, 0.6))))
    canal(n, l, 'canal_borda', borda_m.outputs['Result'])
    return m


def materiais_das_luvas(pintura):
    """Os materiais das luvas a partir da pintura de uma facção (src/data/luvas.js), por zona, com o nome da zona: é
    ele que vai para o luvas.glb e que o jogo lê (o reforço é de borracha, mas a zona é `reforco`)."""
    z = pintura['zonas']
    return {
        'couro': mat_couro('couro', linear(z['couro']['cor'])),
        'tecido': mat_tecido('tecido', linear(z['tecido']['cor'])),
        'reforco': mat_borracha('reforco', linear(z['reforco']['cor'])),
    }


# Aspereza do material do Blender por acabamento de fábrica (os de src/data/acabamentos.js que as armas usam de fábrica).
ASPEREZA_DE_FABRICA = {'oxidado': 0.34, 'fosfatizado': 0.55, 'anodizado': 0.42, 'escovado': 0.22, 'cromado': 0.08}
# A aspereza dos não metálicos (a mesma de src/data/acabamentos.js): o polímero moldado acetinado desde as correções da
# P1 da 4.1c (era 0,65, com o pontilhado em relevo na peça inteira).
PLASTICOS = {'polimero': 0.45, 'borracha': 0.68, 'fosco': 0.85, 'acetinado': 0.5, 'cerakote': 0.7}


def material_de_zona(nome, z, veio):
    """O material do modelo alto de uma zona da pintura de fábrica, pelo acabamento dela: os metálicos pelo aço (com a
    aspereza do acabamento), os plásticos e as pinturas pelo polímero moldado, a madeira pela madeira (com a conta do
    `veio` do jogo, do contexto)."""
    a = z['acabamento']
    if a == 'madeira':
        return mat_madeira(nome, linear(z['cor']), linear(z.get('cor2') or z['cor']), veio)
    if a in PLASTICOS:
        return mat_plastico(nome, linear(z['cor']), PLASTICOS[a])
    rug = ASPEREZA_DE_FABRICA.get(a, 0.34)
    cor = linear(z['cor'])
    return mat_aco(nome, cor, rug, gasto=tuple(min(1.0, c * 1.1 + 0.3) for c in cor))


def materiais_de_fabrica(fabrica, veio):
    """Os materiais do modelo alto a partir da pintura de fábrica (zonas → cores do contexto): um por zona, com o nome
    da zona (M['corpo'], M['guarnicao']…, desde a 4.1c), e os nomes da AK (aço, madeira) quando as zonas dela existem."""
    z = fabrica['zonas']
    M = {zona: material_de_zona(f'{zona} de fábrica', d, veio) for zona, d in z.items()}
    if {'corpo', 'detalhes', 'carregador', 'interno', 'guarnicao'} <= set(z):
        M.update({
            'aco': mat_aco('aço oxidado', linear(z['corpo']['cor']), 0.34, gasto=(0.32, 0.32, 0.34)),
            'aco_detalhes': mat_aco('aço dos detalhes', linear(z['detalhes']['cor']), 0.34, gasto=(0.36, 0.36, 0.38)),
            'aco_carregador': mat_aco('aço do carregador', linear(z['carregador']['cor']), 0.34, gasto=(0.36, 0.37, 0.39)),
            'aco_polido': mat_aco('aço polido', linear(z['interno']['cor']), 0.22, gasto=(0.6, 0.6, 0.6)),
            'madeira': mat_madeira('madeira', linear(z['guarnicao']['cor']), linear(z['guarnicao'].get('cor2') or z['guarnicao']['cor']),
                                   veio),
        })
    return M
