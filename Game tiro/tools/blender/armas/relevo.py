# Relevo moldado das armas realistas (correções da P1 da 4.1c; plano da 4.1c, P1.1): as texturas do molde — o
# pontilhado do punho da Glock, o quadriculado da frente e das costas dele, o losango do punho A2 da M4, o recartilhado
# do cabo da M9 — no lugar das folhas de geometria de pecas_superficie.relevo, que viravam escada nas curvas (a frente
# do punho da Glock, projetada por um eixo só numa grade de 0,1 mm), deixavam emendas nas pontas (o cabo da M9) e caíam
# em 2 a 4 texels no _n (serrilhado e ruído).
#
# O script da arma declara as regiões (`relevos(ficha)`): o tipo (src/data/acabamentos.js, RELEVOS_MOLDADOS, que o
# lançador passa no contexto), a zona de material em que vale (o molde é da peça: o corpo do carregador da Glock, dentro
# do punho, não leva o quadriculado dele), o polígono na vista de lado (x, y da ficha, mm), os polígonos que ficam de
# fora e as faces em que vale, pela maior componente da normal — 'lado' (±Y do Blender), 'frente' (±X: a frente e as costas),
# 'cima' (±Z), 'radial' (lado e cima: o cabo torneado em volta de X) ou 'frente_cima' (a frente curva de um punho, que
# passa a olhar mais para baixo nas ondas dos dedos). Daqui saem:
#   - a máscara: uma imagem de 8 bits no plano XZ do Blender, um canal por direção da normal (R lado, G frente, B
#     cima), com o tipo em degraus de 32/255 (rasterizada aqui, sem PIL: o Python do Blender não traz);
#   - em cada material de zona, os nós do relevo (o grupo `relevo_moldado`): o mesmo desenho do shader do jogo
#     (src/weapons/model/glsl/acabamentos.js) — as pirâmides com platô no plano da face, os grãos pelo Voronoi, o
#     recartilhado em volta de X com um número inteiro de períodos por volta —, num Bump `fino` (só nas renders do
#     modelo alto: o assar desliga os `fino`, e no jogo quem desenha é o shader), o fundo dos sulcos mais escuro, a região
#     mais áspera, e o canal `canal_relevo` (o alfa do _n: 1 − 32·id/255) que o assar grava.
import math

import bpy
import numpy as np

from .materiais import _conta, canal, sock
from .unidades import S

DEGRAU = 32
PX_MM = 0.1  # o lado do pixel da máscara (mm); cresce se a região passar de 4096 px
CANAIS = {'lado': (0,), 'frente': (1,), 'cima': (2,), 'radial': (0, 2), 'frente_cima': (1, 2)}
ESCURO_DO_SULCO = 0.32  # quanto o fundo do sulco escurece a cor (o mesmo do shader do jogo)
ASPEREZA_DA_REGIAO = 0.1  # quanto a região texturizada é mais áspera que a lisa (o mesmo do shader do jogo)


def _preencher(img, poligono, x0, z0, px, valor):
    """Preenche o polígono (mm, na vista de lado) na imagem (linhas de baixo para cima a partir de z0, colunas a partir
    de x0), pela varredura das linhas com a regra par-ímpar: o pixel entra quando o centro dele está dentro."""
    h, w = img.shape
    pts = np.asarray(poligono, float)
    xs = (pts[:, 0] - x0) / px
    zs = (pts[:, 1] - z0) / px
    n = len(pts)
    for linha in range(max(0, int(math.floor(zs.min()))), min(h, int(math.ceil(zs.max())) + 1)):
        zc = linha + 0.5
        cruz = []
        for k in range(n):
            za, zb = zs[k], zs[(k + 1) % n]
            if (za > zc) != (zb > zc):
                xa, xb = xs[k], xs[(k + 1) % n]
                cruz.append(xa + (zc - za) * (xb - xa) / (zb - za))
        cruz.sort()
        for a, b in zip(cruz[0::2], cruz[1::2]):
            c0, c1 = max(0, int(math.ceil(a - 0.5))), min(w, int(math.floor(b - 0.5)) + 1)
            if c1 > c0:
                img[linha, c0:c1] = valor


def mascara(regioes, tipos, nome='mascara_relevo', margem=1.0):
    """A imagem da máscara (8 bits, empacotada na .blend: a conferência abre a .blend gravada) e a caixa dela em mm
    (x0, x1, z0, z1)."""
    pts = [p for r in regioes for p in r['poligono']]
    x0, x1 = min(p[0] for p in pts) - margem, max(p[0] for p in pts) + margem
    z0, z1 = min(p[1] for p in pts) - margem, max(p[1] for p in pts) + margem
    px = max(PX_MM, max(x1 - x0, z1 - z0) / 4096.0)
    w, h = int(math.ceil((x1 - x0) / px)), int(math.ceil((z1 - z0) / px))
    x1, z1 = x0 + w * px, z0 + h * px
    canais = np.zeros((3, h, w), np.float32)
    for r in regioes:
        valor = tipos[r['tipo']]['id'] * DEGRAU / 255.0
        for c in CANAIS[r['normal']]:
            _preencher(canais[c], r['poligono'], x0, z0, px, valor)
            for fora in r.get('excluir', ()):
                _preencher(canais[c], fora, x0, z0, px, 0.0)
    rgba = np.ones((h, w, 4), np.float32)
    rgba[..., :3] = np.moveaxis(canais, 0, -1)
    img = bpy.data.images.new(nome, w, h, alpha=True, float_buffer=False)
    img.colorspace_settings.name = 'Non-Color'
    img.pixels.foreach_set(rgba.ravel())
    img.pack()
    return img, (x0, x1, z0, z1)


def _soma(n, l, termos, base=0.0):
    """base + Σ a·b dos termos [(a, b)] (saídas ou números)."""
    total = base
    for a, b in termos:
        total = _conta(n, l, 'ADD', total, _conta(n, l, 'MULTIPLY', a, b))
    return total


def _misturar(n, l, a, b, t):
    """a + (b − a)·t."""
    return _conta(n, l, 'ADD', a, _conta(n, l, 'MULTIPLY', _conta(n, l, 'SUBTRACT', b, a), t))


def _maior_ou_igual(n, l, a, b):
    return _conta(n, l, 'SUBTRACT', 1.0, _conta(n, l, 'LESS_THAN', a, b))


def grupo(img, caixa, tipos, nome='relevo_moldado'):
    """O grupo de nós do relevo moldado: saídas Altura (mm), Alfa (o canal do _n), Peso (1 na região) e Fundo (0 no
    alto do relevo, 1 no fundo do sulco)."""
    g = bpy.data.node_groups.new(nome, 'ShaderNodeTree')
    for nome in ('Altura', 'Alfa', 'Peso', 'Fundo'):
        g.interface.new_socket(nome, in_out='OUTPUT', socket_type='NodeSocketFloat')
    n, l = g.nodes, g.links
    saida = n.new('NodeGroupOutput')
    tc = n.new('ShaderNodeTexCoord')
    xyz = n.new('ShaderNodeSeparateXYZ')
    l.new(tc.outputs['Object'], xyz.inputs['Vector'])
    X, Y, Z = (_conta(n, l, 'DIVIDE', xyz.outputs[e], S) for e in 'XYZ')
    # a máscara na vista de lado, sem filtrar (o tipo não se mistura) e vazia fora da caixa
    x0, x1, z0, z1 = caixa
    uv = n.new('ShaderNodeCombineXYZ')
    l.new(_conta(n, l, 'DIVIDE', _conta(n, l, 'SUBTRACT', X, x0), x1 - x0), uv.inputs['X'])
    l.new(_conta(n, l, 'DIVIDE', _conta(n, l, 'SUBTRACT', Z, z0), z1 - z0), uv.inputs['Y'])
    tx = n.new('ShaderNodeTexImage')
    tx.image = img
    tx.interpolation = 'Closest'
    tx.extension = 'CLIP'
    l.new(uv.outputs['Vector'], tx.inputs['Vector'])
    rgb = n.new('ShaderNodeSeparateColor')
    l.new(tx.outputs['Color'], rgb.inputs['Color'])
    # o canal pela maior componente da normal (a mesma regra do shader do jogo)
    geo = n.new('ShaderNodeNewGeometry')
    nrm = n.new('ShaderNodeSeparateXYZ')
    l.new(geo.outputs['Normal'], nrm.inputs['Vector'])
    ax, ay, az = (_conta(n, l, 'ABSOLUTE', nrm.outputs[e]) for e in 'XYZ')
    lado = _conta(n, l, 'MULTIPLY', _maior_ou_igual(n, l, ay, ax), _maior_ou_igual(n, l, ay, az))
    frente = _conta(n, l, 'MULTIPLY', _conta(n, l, 'SUBTRACT', 1.0, lado), _maior_ou_igual(n, l, ax, az))
    cima = _conta(n, l, 'SUBTRACT', _conta(n, l, 'SUBTRACT', 1.0, lado), frente)
    valor = _soma(n, l, [(rgb.outputs['Red'], lado), (rgb.outputs['Green'], frente), (rgb.outputs['Blue'], cima)])
    ident = _conta(n, l, 'ROUND', _conta(n, l, 'MULTIPLY', valor, 255.0 / DEGRAU))
    peso = _conta(n, l, 'GREATER_THAN', ident, 0.5)
    # os parâmetros do tipo (a soma das bandeiras de cada id; 1 mm de passo onde não há relevo, para não dividir por 0)
    bandeira = {nome: _conta(n, l, 'COMPARE', ident, t['id'], 0.25) for nome, t in tipos.items()}

    def par(chave, padrao=0.0):
        return _soma(n, l, [(bandeira[nome], float(t.get(chave, padrao) or 0.0)) for nome, t in tipos.items()])
    passo = _conta(n, l, 'ADD', par('passo'), _conta(n, l, 'SUBTRACT', 1.0, peso))
    altura, raio, plato = par('altura'), par('raio'), par('plato')
    ang = _soma(n, l, [(bandeira[nome], math.radians(t.get('angulo', 0) or 0)) for nome, t in tipos.items()])
    graos = _soma(n, l, [(bandeira[nome], 1.0) for nome, t in tipos.items() if t['forma'] == 'graos'])
    cil = _soma(n, l, [(bandeira[nome], 1.0) for nome, t in tipos.items() if t['projecao'] == 'cilindrica'])
    # as coordenadas no plano da face (lado: X, Z; frente: Y, Z; cima: X, Y) ou em volta de X (a volta com o número
    # inteiro e fixo de períodos do tipo, as `voltas` da tabela: sem emenda e sem o salto entre as facetas do torno)
    a_pl = _conta(n, l, 'ADD', _conta(n, l, 'MULTIPLY', X, _conta(n, l, 'ADD', lado, cima)), _conta(n, l, 'MULTIPLY', Y, frente))
    b_pl = _conta(n, l, 'ADD', _conta(n, l, 'MULTIPLY', Z, _conta(n, l, 'ADD', lado, frente)), _conta(n, l, 'MULTIPLY', Y, cima))
    c, s = _conta(n, l, 'COSINE', ang), _conta(n, l, 'SINE', ang)
    th = _conta(n, l, 'ARCTAN2', Z, Y)
    periodo = _conta(n, l, 'DIVIDE', passo, _conta(n, l, 'MAXIMUM', _conta(n, l, 'ABSOLUTE', c), _conta(n, l, 'ABSOLUTE', s)))
    voltas = par('voltas')
    b_cil = _conta(n, l, 'MULTIPLY', _conta(n, l, 'DIVIDE', th, 2 * math.pi), _conta(n, l, 'MULTIPLY', voltas, periodo))
    a = _misturar(n, l, a_pl, X, cil)
    b = _misturar(n, l, b_pl, b_cil, cil)
    # pirâmides com platô: a distância ao sulco pela maior das duas direções da grade girada
    ra = _conta(n, l, 'DIVIDE', _conta(n, l, 'ADD', _conta(n, l, 'MULTIPLY', a, c), _conta(n, l, 'MULTIPLY', b, s)), passo)
    rb = _conta(n, l, 'DIVIDE', _conta(n, l, 'SUBTRACT', _conta(n, l, 'MULTIPLY', b, c), _conta(n, l, 'MULTIPLY', a, s)), passo)

    def ao_sulco(q):
        return _conta(n, l, 'MULTIPLY', _conta(n, l, 'ABSOLUTE', _conta(n, l, 'SUBTRACT', _conta(n, l, 'FRACT', q), 0.5)), 2.0)
    m = _conta(n, l, 'MAXIMUM', ao_sulco(ra), ao_sulco(rb))
    t = _conta(n, l, 'DIVIDE', _conta(n, l, 'SUBTRACT', 1.0, m), _conta(n, l, 'MAXIMUM', _conta(n, l, 'SUBTRACT', 1.0, plato), 0.05))
    h_pir = _conta(n, l, 'MULTIPLY', altura, _conta(n, l, 'MINIMUM', _conta(n, l, 'MAXIMUM', t, 0.0), 1.0))
    # grãos: o ponto do Voronoi mais perto (uma cúpula por célula, o tamanho sorteado pela cor da célula)
    vor = n.new('ShaderNodeTexVoronoi')
    vor.voronoi_dimensions = '2D'
    vor.feature = 'F1'
    vor.inputs['Randomness'].default_value = 0.5
    ab = n.new('ShaderNodeCombineXYZ')
    l.new(a, ab.inputs['X'])
    l.new(b, ab.inputs['Y'])
    l.new(ab.outputs['Vector'], vor.inputs['Vector'])
    l.new(_conta(n, l, 'DIVIDE', 1.0, passo), vor.inputs['Scale'])
    cor_celula = n.new('ShaderNodeSeparateColor')
    l.new(vor.outputs['Color'], cor_celula.inputs['Color'])
    rr = _conta(n, l, 'MULTIPLY', raio, _conta(n, l, 'ADD', 0.8, _conta(n, l, 'MULTIPLY', cor_celula.outputs['Red'], 0.4)))
    q = _conta(n, l, 'DIVIDE', _conta(n, l, 'MULTIPLY', sock(vor.outputs, 'Distance', 'VALUE'), passo), _conta(n, l, 'MAXIMUM', rr, 0.01))
    k = _conta(n, l, 'MAXIMUM', _conta(n, l, 'SUBTRACT', 1.0, _conta(n, l, 'MULTIPLY', q, q)), 0.0)
    h_gr = _conta(n, l, 'MULTIPLY', altura, _conta(n, l, 'MULTIPLY', k, k))
    h = _conta(n, l, 'MULTIPLY', _misturar(n, l, h_pir, h_gr, graos), peso)
    l.new(h, saida.inputs['Altura'])
    l.new(_conta(n, l, 'SUBTRACT', 1.0, valor), saida.inputs['Alfa'])
    l.new(peso, saida.inputs['Peso'])
    l.new(_conta(n, l, 'SUBTRACT', 1.0, _conta(n, l, 'DIVIDE', h, _conta(n, l, 'MAXIMUM', altura, 0.01))), saida.inputs['Fundo'])
    return g


def _entrada_ou_valor(nt, entrada):
    """A saída ligada numa entrada do BSDF (desligando) ou o valor dela."""
    if entrada.links:
        s = entrada.links[0].from_socket
        nt.links.remove(entrada.links[0])
        return s
    v = entrada.default_value
    return tuple(v) if hasattr(v, '__len__') else v


def ligar(material, g):
    """Os nós do relevo moldado num material de fábrica: o Bump `fino` sobre a normal que ele já tem, a cor mais escura no
    fundo dos sulcos, a região mais áspera e o canal `canal_relevo` do assar."""
    nt = material.node_tree
    n, l = nt.nodes, nt.links
    b = next(x for x in n if x.type == 'BSDF_PRINCIPLED')
    no = n.new('ShaderNodeGroup')
    no.node_tree = g
    bump = n.new('ShaderNodeBump')
    bump.label = 'fino'
    bump.inputs['Strength'].default_value = 1.0
    bump.inputs['Distance'].default_value = S
    l.new(no.outputs['Altura'], bump.inputs['Height'])
    normal = _entrada_ou_valor(nt, b.inputs['Normal'])
    if not isinstance(normal, (tuple, float)):
        l.new(normal, bump.inputs['Normal'])
    l.new(bump.outputs['Normal'], b.inputs['Normal'])
    asp = _entrada_ou_valor(nt, b.inputs['Roughness'])
    l.new(_conta(n, l, 'MINIMUM', _conta(n, l, 'ADD', asp, _conta(n, l, 'MULTIPLY', no.outputs['Peso'], ASPEREZA_DA_REGIAO)), 1.0),
          b.inputs['Roughness'])
    cor = _entrada_ou_valor(nt, b.inputs['Base Color'])
    escuro = _conta(n, l, 'SUBTRACT', 1.0, _conta(n, l, 'MULTIPLY', _conta(n, l, 'MULTIPLY', no.outputs['Peso'], no.outputs['Fundo']),
                                                 ESCURO_DO_SULCO))
    mx = n.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.blend_type = 'MULTIPLY'
    sock(mx.inputs, 'Factor', 'VALUE').default_value = 1.0
    if isinstance(cor, tuple):
        sock(mx.inputs, 'A', 'RGBA').default_value = cor
    else:
        l.new(cor, sock(mx.inputs, 'A', 'RGBA'))
    cinza = n.new('ShaderNodeCombineColor')
    for e in ('Red', 'Green', 'Blue'):
        l.new(escuro, cinza.inputs[e])
    l.new(cinza.outputs['Color'], sock(mx.inputs, 'B', 'RGBA'))
    l.new(sock(mx.outputs, 'Result', 'RGBA'), b.inputs['Base Color'])
    canal(n, l, 'canal_relevo', no.outputs['Alfa'])


def montar(materiais, regioes, tipos):
    """As máscaras das regiões da arma, uma por zona de material, e os nós no material de cada zona com regiões (nas
    outras, nada: o assar grava o alfa do _n liso, 1). Devolve {zona: caixa da máscara em mm}."""
    for nome, t in tipos.items():
        voltas = t.get('voltas')
        if t['projecao'] == 'cilindrica' and (not isinstance(voltas, int) or voltas < 8):
            raise ValueError(f"o relevo cilíndrico {nome} precisa das voltas inteiras (≥ 8) da tabela: {voltas}")
    por_zona = {}
    for r in regioes:
        if r['tipo'] not in tipos:
            raise ValueError(f"relevo moldado desconhecido: {r['tipo']} (tem: {', '.join(tipos)})")
        if r['normal'] not in CANAIS:
            raise ValueError(f"normal do relevo desconhecida: {r['normal']} (use {', '.join(CANAIS)})")
        if r.get('zona') not in materiais:
            raise ValueError(f"zona do relevo desconhecida: {r.get('zona')} (tem: {', '.join(materiais)})")
        por_zona.setdefault(r['zona'], []).append(r)
    caixas = {}
    for zona, rs in por_zona.items():
        img, caixas[zona] = mascara(rs, tipos, f'mascara_relevo_{zona}')
        ligar(materiais[zona], grupo(img, caixas[zona], tipos, f'relevo_moldado_{zona}'))
    return caixas
