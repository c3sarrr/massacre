# Gaiola de quadriláteros da luva direita e a malha base (Fase 4.1b; desenho em
# docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md, seção 3.2). A palma em anéis de 20 vértices
# (costas do mínimo ao indicador, lado do polegar, palma do indicador ao mínimo, lado do mínimo) do pulso à linha dos
# nós, com as quatro portas dos dedos na linha dos nós e a do polegar no canto da palma do lado do indicador (a
# eminência tenar); os dedos em anéis elípticos, três em cada junta, e a ponta em cúpula; o punho da luva sobre o
# antebraço de massinha, com a borda dobrada para dentro.
# Cada vértice nasce num PONTO DE DESENHO. Os que carregam medida — as seções das juntas de Greiner, as pontas dos
# dedos, o pulso e o punho, o contorno da palma e os lados da linha dos nós, tudo com a espessura da luva — são
# âncoras: o ajuste ao limite move a gaiola até a superfície limite de Catmull-Clark (onde o modificador Subdivision
# Surface, com "Use Limit Surface", põe os vértices da malha subdividida) passar por eles, e as medidas da malha saem
# as da ficha sem fator de folga chutado. As junções (as portas dos dedos e do polegar, a tenar, a linha dos nós, as
# dobras entre os dedos, a estação antes dos nós) ficam livres, com a suavização natural da subdivisão: forçar a
# superfície por pontos tão próximos ali dobraria a malha. O modelo alto (3 níveis) é a mesma superfície do de jogo.
# Cada vértice leva os pesos dos ossos (a subdivisão interpola), cada face a zona (couro na palma, na face palmar dos
# dedos, nas pontas e entre o polegar e o indicador; tecido no resto) e as arestas das costuras ficam marcadas para as
# UV (lados, base de cada dedo, a porta do polegar, o pulso); as faces do forro do punho (a volta da borda para dentro)
# ficam no atributo de face `forro`. O ajuste ao limite está em maos_limite.py e as medidas em maos_medidas.py.
# Referencial e unidades: os de maos.py (mm).
import math

import bmesh
import bpy
from mathutils import Vector

from .maos import DEDOS4, METACARPO, meia_altura_no_contorno
from .maos_limite import ajustar_ao_limite
from .unidades import S

# Estações da palma (mm, sem a luva): x a partir do pulso, largura, costas e palma (z), raio do canto do retângulo
# arredondado, quanto a borda das costas desce (o arco transverso), a queda a mais do lado do mínimo (os metacarpos IV e
# V ficam mais baixos), o oco no meio da palma e a eminência hipotenar na borda do mínimo. A estação do pulso vem da
# ficha (retângulo arredondado de 61,9 × 38 com raio 18); a última fica a meio caminho entre a terceira e a linha dos
# nós, coluna a coluna (paralela aos nós). As três primeiras levam a porta do polegar: a terceira em x = 64, perto da
# dobra entre o polegar e o indicador de Greiner (69,1 × 189,3/194,5 = 67,3 mm).
_PALMA = (
    # x,    largura, costas, palma, raio, arco, queda, oco, hipotenar
    (21.0, 72.0, 17.0, -20.5, 16.0, 2.5, 1.0, 1.5, 3.0),
    (43.0, 80.0, 15.0, -21.5, 14.5, 3.0, 1.5, 3.5, 3.5),
    (64.0, 84.0, 13.5, -20.5, 13.0, 3.0, 2.0, 3.0, 2.5),
    (None, 85.0, 12.3, -19.0, 12.0, 2.5, 2.5, 1.5, 1.0),
)
_PORTA_POLEGAR = (1, 2, 3)  # anéis da palma com a porta do polegar, nos índices 10–12 (a palma do lado do indicador)
_X_PUNHO = (-12.0, -24.0, -36.0)  # anéis do punho antes da borda
_COS45 = math.sqrt(0.5)
_BOJO_JUNTA = 1.015  # o anel do centro de cada junta, um pouco mais largo que os vizinhos (o volume da junta)


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _entre(v, a, b):
    return _suave((v - a) / (b - a))


def _mistura(pesos):
    """Normaliza um dicionário osso → peso (tira os nulos)."""
    total = sum(w for w in pesos.values() if w > 0)
    return {k: w / total for k, w in pesos.items() if w > 1e-4}


class _Gaiola:
    """A gaiola em construção: vértices com pesos, faces com zona, arestas de costura."""

    def __init__(self):
        self.bm = bmesh.new()
        self.pesos = {}  # vértice → {osso: peso}
        self.zonas = {}  # face → zona
        self.costuras = set()  # pares de vértices
        self.livres = set()  # vértices das junções, fora do ajuste ao limite
        self.estufar = {}  # vértice → mm para fora (os reforços de couro por cima da luva)
        self.forro = set()  # faces da volta da borda do punho para dentro (a parede de dentro)

    def v(self, co, pesos):
        vert = self.bm.verts.new(co)
        self.pesos[vert] = _mistura(pesos)
        return vert

    def face(self, verts, zona):
        f = self.bm.faces.new(verts)
        self.zonas[f] = zona
        return f

    def costura(self, a, b):
        self.costuras.add(frozenset((a, b)))

    def faixa(self, anel_a, anel_b, zonas):
        """Quadriláteros entre dois anéis fechados do mesmo tamanho; `zonas[i]` é a zona da face que começa no vértice i."""
        n = len(anel_a)
        return [self.face((anel_a[i], anel_a[(i + 1) % n], anel_b[(i + 1) % n], anel_b[i]), zonas[i]) for i in range(n)]


# ---------------------------------------------------------------------------------------------- seções
def _colunas(mao):
    """As 9 colunas da linha dos nós (y, do mínimo ao indicador: a borda, o centro de cada dedo e as fronteiras) e o dedo
    de cada coluna (a fronteira entre dois dedos fica com o de fora, o do lado do mínimo)."""
    fr = list(reversed(mao.y_fronteira))
    centros = [mao.y_no[d] for d in reversed(DEDOS4)]
    ys = []
    for i in range(4):
        ys += [fr[i], centros[i]]
    ys.append(fr[4])
    dedos = [d for d in reversed(DEDOS4) for _ in (0, 1)] + ['indicador']
    return ys, dedos


def _secao_palma(mao, ys_nos, largura, costas, palma, raio, arco, queda, oco, hipo):
    """Os 20 pontos (y, z) de uma estação da palma, na ordem do anel. O contorno é o retângulo arredondado com a luva;
    as bordas das costas e da palma ficam no canto (a 45°), o lado no extremo da largura (a meia largura mais a luva, por
    onde a superfície final passa), e as colunas de dentro na proporção das colunas dos nós."""
    luva = mao.luva
    meia_l = largura / 2 + luva
    meia_a = (costas - palma) / 2 + luva
    zc = (costas + palma) / 2
    r = raio + luva
    k = (meia_l - r * (1 - _COS45)) / (mao.largura / 2)
    cols = []
    for y0 in ys_nos:
        y = y0 * k
        u = y / meia_l
        h = meia_altura_no_contorno(y, meia_l, meia_a, r)
        zd = zc + h - arco * u * u - queda * max(0.0, -u) ** 2
        zp = zc - h + oco * (1 - u * u) ** 2 - hipo * math.exp(-((u + 0.62) / 0.3) ** 2)
        cols.append((y, zd, zp))
    anel = [(y, zd) for y, zd, _ in cols]
    anel.append((meia_l, (cols[8][1] + cols[8][2]) / 2))
    anel += [(y, zp) for y, _, zp in reversed(cols)]
    anel.append((-meia_l, (cols[0][1] + cols[0][2]) / 2))
    return anel


def _pontos_elipticos(centro, frente, costas, meia_l, meia_e):
    """Oito pontos em volta de `centro`, no plano perpendicular a `frente`: a partir de costas-ulnar (-45°) girando
    para o lado do polegar (a ordem canônica dos anéis; as zonas e a calota contam com ela)."""
    radial = costas.cross(frente).normalized()
    costas = frente.cross(radial).normalized()
    pts = []
    for k in range(8):
        th = math.radians(-45.0 + 45.0 * k)
        pts.append(centro + costas * (meia_e * math.cos(th)) + radial * (meia_l * math.sin(th)))
    return pts


def _casar_porta(porta, pontos):
    """A porta (8 vértices da palma) reordenada para casar com o primeiro anel na ordem canônica: o giro e o sentido
    de menor distância somada. Sem isso a faixa entre os dois torceria."""
    melhor = None
    n = len(porta)
    for sentido in (1, -1):
        for s in range(n):
            perm = [(s + sentido * i) % n for i in range(n)]
            dist = sum((porta[perm[i]].co - pontos[i]).length for i in range(n))
            if melhor is None or dist < melhor[0]:
                melhor = (dist, perm)
    return [porta[i] for i in melhor[1]]


def _referencial(dd, seg):
    """(frente, costas) de um anel: o do segmento `seg`, ou a bissetriz de dois segmentos (o anel do centro de uma
    junta dobrada fica no meio do ângulo, senão belisca o lado de dentro da dobra)."""
    if isinstance(seg, tuple):
        a, b = seg
        return (dd['dirs'][a] + dd['dirs'][b]).normalized(), (dd['normais'][a] + dd['normais'][b]).normalized()
    return dd['dirs'][seg], dd['normais'][seg]


def _fator_cupula(t_anel, t_a, t_ponta):
    """Seção relativa de um anel da cúpula da ponta, no perfil de elipse que vai do anel `t_a` (seção inteira) à ponta."""
    s = (t_anel - t_a) / (t_ponta - t_a)
    return math.sqrt(max(0.0, 1.0 - s * s))


# ---------------------------------------------------------------------------------------------- gaiola
def gerar_gaiola(mao):
    """A gaiola da luva direita (bmesh em mm) com os pontos de desenho, os pesos, as zonas e as costuras."""
    g = _Gaiola()
    luva = mao.luva
    ys_nos, dedo_da_coluna = _colunas(mao)
    mcp = {d: mao.dedos[d]['mcp'] for d in DEDOS4}
    cmc4 = mao.dedos['anelar']['cmc'].x

    def pesos_palma(x, y):
        w = {'mao': 1.0}
        if x < 12.0:
            t = _entre(x, -8.0, 12.0)
            w = {'mao': t, 'torcao': 1.0 - t}
        # A borda do mínimo e do anelar fecha em concha com os metacarpos deles.
        tx = _entre(x, cmc4 + 5.0, cmc4 + 35.0)
        w5 = tx * _entre(-y, 18.0, 36.0)
        w4 = tx * max(0.0, 1.0 - abs(y - mao.y_no['anelar']) / 14.0) * 0.6
        if w5 > 0:
            w['minimo_0'] = w5
        if w4 > 0:
            w['anelar_0'] = w4
        w['mao'] = max(0.0, w.get('mao', 0.0) - w5 - w4)
        return w

    # ---------------------------------------------------------------- a linha dos nós (os pontos antes dos anéis)
    # Costas: o alto de cada nó (centro do dedo) e os vales entre eles; as bordas de fora no canto do retângulo
    # arredondado da mão nos nós (85 × 29 com raio 12, da ficha). Palma: a almofada na base de cada dedo e as pregas
    # entre eles. Lados: no extremo da largura da mão (a borda da MCP II e da V), por onde passa a largura da ficha.
    r_nos = mao.raio_mao + luva
    meia_l_nos = mao.largura / 2 + luva
    y_canto = meia_l_nos - r_nos * (1 - _COS45)

    def topo_fundo(d):
        return (mcp[d].z + mao.esp_mao * 0.38 + luva, mcp[d].z - mao.esp_mao * 0.62 - luva)

    nos_costas, nos_palma = [], []
    for j in range(9):
        if j in (0, 8):
            d = dedo_da_coluna[j]
            topo, fundo = topo_fundo(d)
            zc, meia_a = (topo + fundo) / 2, (topo - fundo) / 2
            y = y_canto if j == 8 else -y_canto
            h = meia_altura_no_contorno(y, meia_l_nos, meia_a, r_nos)
            nos_costas.append(Vector((mcp[d].x - 2.0, y, zc + h)))
            nos_palma.append(Vector((mcp[d].x + 9.0, y, zc - h)))
        elif j % 2 == 1:
            d = dedo_da_coluna[j]
            topo, fundo = topo_fundo(d)
            nos_costas.append(Vector((mcp[d].x + 1.5, ys_nos[j], topo + 1.2)))
            nos_palma.append(Vector((mcp[d].x + 15.0, ys_nos[j], fundo)))
        else:  # vale entre dois dedos: a média dos dois
            a, b = dedo_da_coluna[j - 1], dedo_da_coluna[j + 1]
            ta, fa = topo_fundo(a)
            tb, fb = topo_fundo(b)
            x = (mcp[a].x + mcp[b].x) / 2
            nos_costas.append(Vector((x - 2.0, ys_nos[j], (ta + tb) / 2 - 1.5)))
            nos_palma.append(Vector((x + 9.0, ys_nos[j], (fa + fb) / 2 + 2.0)))
    lados_nos = {}
    for lado, d in (('polegar', 'indicador'), ('minimo', 'minimo')):
        topo, fundo = topo_fundo(d)
        lados_nos[lado] = Vector((mcp[d].x + 2.0, meia_l_nos if lado == 'polegar' else -meia_l_nos, (topo + fundo) / 2))

    # ---------------------------------------------------------------- anéis da palma
    def anel_de(pts_yz, xs):
        """Vértices de um anel a partir dos (y, z) e do x de cada um."""
        return [g.v(Vector((x, y, z)), pesos_palma(x, y)) for (y, z), x in zip(pts_yz, xs)]

    aneis = []
    sec0 = _secao_palma(mao, ys_nos, mao.pulso_larg, mao.pulso_esp / 2, -mao.pulso_esp / 2, mao.pulso_raio,
                        0.0, 0.0, 0.0, 0.0)
    aneis.append(anel_de(sec0, [0.0] * 20))
    for est in _PALMA[:3]:
        aneis.append(anel_de(_secao_palma(mao, ys_nos, *est[1:]), [est[0]] * 20))
    x3 = _PALMA[2][0]
    xs4 = ([(x3 + p.x) / 2 for p in nos_costas] + [(x3 + lados_nos['polegar'].x) / 2]
           + [(x3 + p.x) / 2 for p in reversed(nos_palma)] + [(x3 + lados_nos['minimo'].x) / 2])
    aneis.append(anel_de(_secao_palma(mao, ys_nos, *_PALMA[3][1:]), xs4))
    nos_pts = nos_costas + [lados_nos['polegar']] + list(reversed(nos_palma)) + [lados_nos['minimo']]
    nos = []
    for i, p in enumerate(nos_pts):
        if i == 9:
            w = {'mao': 0.7, 'indicador_1': 0.3}
        elif i == 19:
            w = {'minimo_0': 0.6, 'mao': 0.2, 'minimo_1': 0.2}
        else:
            # Costas: 55 % no metacarpo e 45 % na falange; palma, o contrário. Um vale divide entre os dois dedos.
            j = i if i < 9 else 18 - i
            vizinhos = [dedo_da_coluna[j]] if j % 2 == 1 or j in (0, 8) else [dedo_da_coluna[j - 1], dedo_da_coluna[j + 1]]
            no_meta, na_falange = (0.55, 0.45) if i < 9 else (0.45, 0.55)
            w = {}
            for d in vizinhos:
                base = METACARPO.get(d, 'mao')
                w[base] = w.get(base, 0.0) + no_meta / len(vizinhos)
                w[f'{d}_1'] = w.get(f'{d}_1', 0.0) + na_falange / len(vizinhos)
        nos.append(g.v(p, w))
    aneis.append(nos)
    # Zonas da palma: a metade da palma, de um lado ao outro (as faces que começam nos índices 9..18), é couro; as
    # costas, tecido.
    zonas = ['tecido'] * 9 + ['couro'] * 10 + ['tecido']
    for a, b in zip(aneis[:-1], aneis[1:]):
        g.faixa(a, b, zonas)

    # ---------------------------------------------------------------- tampa: portas dos dedos e as dobras entre eles
    dobras = mao.f['juntas']['dobras']
    x_web = [dobras['anelarMinimo'], dobras['medioAnelar'], dobras['indicadorMedio']]
    meio = {0: nos[19], 8: nos[9]}
    for j, xw in zip((2, 4, 6), x_web):
        a, b = dedo_da_coluna[j - 1], dedo_da_coluna[j + 1]
        z = (mcp[a].z + mcp[b].z) / 2 - 3.5
        meio[j] = g.v(Vector((xw * mao.esc_c, ys_nos[j], z)), {f'{a}_1': 0.35, f'{b}_1': 0.35, 'mao': 0.3})
    costas = nos[0:9]
    palma = [nos[18 - j] for j in range(9)]  # palma[j] na coluna j (do mínimo ao indicador)
    portas = {}
    for k, d in enumerate(reversed(DEDOS4)):
        j0 = 2 * k
        portas[d] = [costas[j0], costas[j0 + 1], costas[j0 + 2], meio[j0 + 2], palma[j0 + 2], palma[j0 + 1], palma[j0],
                     meio[j0]]
    for d in DEDOS4:
        _dedo(g, mao, d, portas[d])

    # ---------------------------------------------------------------- polegar: porta no canto da palma (a tenar)
    r1, r2, r3 = (aneis[i] for i in _PORTA_POLEGAR)
    dentro = {r1[10], r1[11], r1[12], r2[10], r2[11], r2[12], r3[10], r3[11], r3[12]}
    for f in list(g.bm.faces):
        if set(f.verts) <= dentro:
            del g.zonas[f]
            g.bm.faces.remove(f)
    g.bm.verts.remove(r2[11])
    del g.pesos[r2[11]]
    porta_pol = [r1[10], r1[11], r1[12], r2[12], r3[12], r3[11], r3[10], r2[10]]
    for v in porta_pol:
        g.pesos[v] = _mistura({**g.pesos[v], 'polegar_1': 0.8 * sum(g.pesos[v].values())})
    aneis_pol = _polegar(g, mao, porta_pol)
    # A palma em volta da tenar acompanha o metacarpo do polegar, pela distância a ele.
    pol = mao.polegar
    seg_a, seg_b = pol['cmc'], pol['mcp']
    no_polegar = set(porta_pol).union(*aneis_pol)
    for anel in aneis[:5]:
        for v in anel:
            if not v.is_valid or v in no_polegar:
                continue
            ab = seg_b - seg_a
            t = max(0.0, min(1.0, (v.co - seg_a).dot(ab) / ab.length_squared))
            dist = (v.co - (seg_a + ab * t)).length
            w_pol = 0.3 * (1.0 - _suave(dist / 32.0))
            if w_pol > 0.01:
                total = sum(g.pesos[v].values())
                g.pesos[v] = _mistura({**{k: w * (1 - w_pol) / total for k, w in g.pesos[v].items()},
                                        'polegar_1': w_pol})

    # Livres: a linha dos nós (menos os dois lados, que dão a largura), a estação antes dela, as dobras entre os dedos,
    # a porta do polegar e a palma em volta dela.
    g.livres.update(v for i, v in enumerate(nos) if i not in (9, 19))
    g.livres.update(aneis[4])
    g.livres.update(meio[j] for j in (2, 4, 6))
    g.livres.update(porta_pol)
    for r in (r1, r2, r3):
        g.livres.update((r[9], r[13]))
    g.livres.update(aneis[0][i] for i in (10, 11, 12))
    # O reforço da palma: uma segunda camada de couro sobre a palma, da base da mão até a linha da dobra do polegar
    # (a terceira estação, x = 64), com a borda saliente atravessando a palma do polegar ao mínimo; continua na tenar
    # e na volta entre o polegar e o indicador, e dobra um pouco para os lados.
    couro = mao.f['luva']['couro']
    for r, k in ((r1, 1.0), (r2, 1.0), (r3, 1.8)):
        for i in range(10, 19):
            if r[i].is_valid:
                g.estufar[r[i]] = couro * k
        for i in (9, 19):
            g.estufar[r[i]] = couro * 0.5
    for v in aneis_pol[0]:
        g.estufar[v] = couro

    # ---------------------------------------------------------------- punho e borda
    # O punho veste o antebraço de massinha (o perfil da ficha) com a folga crescendo do pulso (0) até a boca
    # (folgaPunho); por fora, mais a espessura do tecido. A borda dobra para dentro num lábio e volta 8 mm por dentro
    # (o forro), sem parede de espessura zero.
    punho_mm = mao.f['luva']['punho']
    folga_boca = mao.f['luva']['folgaPunho']
    base = aneis[0]
    meia_l0, meia_a0 = mao.pulso_larg / 2 + luva, mao.pulso_esp / 2 + luva

    def folga(x):
        return folga_boca * min(1.0, -x / punho_mm)

    def anel_punho(x, desloc):
        largura, espessura, _ = mao.secao_antebraco(x)
        sy = (largura / 2 + desloc) / meia_l0
        sz = (espessura / 2 + desloc) / meia_a0
        return [g.v(Vector((x, v.co.y * sy, v.co.z * sz)), {'torcao': 1.0}) for v in base]

    punho = [base]
    for x in _X_PUNHO:
        punho.append(anel_punho(x, luva + folga(x)))
    x_borda = -punho_mm + 0.6
    punho.append(anel_punho(x_borda, luva + folga(x_borda)))
    labio = anel_punho(-punho_mm, luva / 2 + folga(-punho_mm))
    dentro_borda = anel_punho(x_borda, folga(x_borda))
    x_forro = -punho_mm + 8.0
    forro = anel_punho(x_forro, folga(x_forro))
    for a, b in zip(punho[:-1], punho[1:]):
        g.faixa(b, a, ['tecido'] * 20)
    g.faixa(labio, punho[-1], ['tecido'] * 20)
    g.forro.update(g.faixa(dentro_borda, labio, ['tecido'] * 20))
    g.forro.update(g.faixa(forro, dentro_borda, ['tecido'] * 20))

    # ---------------------------------------------------------------- costuras das UV
    for i in range(20):
        g.costura(aneis[0][i], aneis[0][(i + 1) % 20])
    for a, b in zip(aneis[:-1], aneis[1:]):
        g.costura(a[19], b[19])  # lado do mínimo
        g.costura(a[9], b[9])  # lado do polegar
    for a, b in zip(punho[:-1] + [punho[-1], labio, dentro_borda], punho[1:] + [labio, dentro_borda, forro]):
        g.costura(a[19], b[19])
    # O reforço da palma é um painel costurado: as bordas dele na primeira estação e na da dobra do polegar (a borda
    # saliente), de um lado da palma ao outro.
    for r in (r1, r3):
        for i in range(9, 19):
            if r[i].is_valid and r[i + 1].is_valid:
                g.costura(r[i], r[i + 1])
    bmesh.ops.recalc_face_normals(g.bm, faces=g.bm.faces[:])
    return g


def _dedo(g, mao, d, porta):
    """Os anéis de um dedo a partir da porta dele: meio da falange proximal, a PIP em três anéis, o meio da média, a
    DIP em três anéis, a polpa e a cúpula da ponta em dois anéis e o centro — a ponta de desenho no comprimento do osso
    mais a polpa e a luva (a ponta do médio dá o comprimento da mão)."""
    dd = mao.dedos[d]
    luva = mao.luva
    (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
    base_sec = (dd['larg_no'] + 2 * luva, ep * 1.12 + 2 * luva)
    pip_sec = (lp + 2 * luva, ep + 2 * luva)
    dip_sec = (ld + 2 * luva, ed + 2 * luva)
    polpa_sec = (ld * 0.97 + 2 * luva, ed * 0.95 + 2 * luva)
    osso = [f'{d}_1', f'{d}_2', f'{d}_3']
    aneis = [porta]

    def anel(ponto, seg, sec, pesos, palmar=0.0):
        frente, costas = _referencial(dd, seg)
        pts = _pontos_elipticos(ponto - costas * palmar, frente, costas, sec[0] / 2, sec[1] / 2)
        if len(aneis) == 1:
            aneis[0] = _casar_porta(aneis[0], pts)
        a = [g.v(p, pesos) for p in pts]
        aneis.append(a)
        return a

    def vezes(sec, k):
        return sec[0] * k, sec[1] * k

    comp1 = (dd['pip'] - dd['mcp']).length
    comp2 = (dd['dip'] - dd['pip']).length
    comp3 = (dd['ponta'] - dd['dip']).length
    meio1 = ((base_sec[0] + pip_sec[0]) / 2 * 0.97, (base_sec[1] + pip_sec[1]) / 2 * 0.95)
    anel(dd['mcp'] + dd['dirs'][0] * comp1 * 0.5, 0, meio1, {osso[0]: 1.0})
    e = 4.0
    anel(dd['pip'] - dd['dirs'][0] * e, 0, pip_sec, {osso[0]: 0.85, osso[1]: 0.15})
    anel(dd['pip'], (0, 1), vezes(pip_sec, _BOJO_JUNTA), {osso[0]: 0.5, osso[1]: 0.5})
    anel(dd['pip'] + dd['dirs'][1] * e, 1, pip_sec, {osso[0]: 0.15, osso[1]: 0.85})
    meio2 = ((pip_sec[0] + dip_sec[0]) / 2 * 0.97, (pip_sec[1] + dip_sec[1]) / 2 * 0.95)
    anel(dd['pip'] + dd['dirs'][1] * comp2 * 0.5, 1, meio2, {osso[1]: 1.0})
    e = 3.0
    anel(dd['dip'] - dd['dirs'][1] * e, 1, dip_sec, {osso[1]: 0.85, osso[2]: 0.15})
    anel(dd['dip'], (1, 2), vezes(dip_sec, _BOJO_JUNTA), {osso[1]: 0.5, osso[2]: 0.5})
    anel(dd['dip'] + dd['dirs'][2] * e, 2, dip_sec, {osso[1]: 0.15, osso[2]: 0.85})
    ponta_t = comp3 + luva
    anel(dd['dip'] + dd['dirs'][2] * comp3 * 0.45, 2, polpa_sec, {osso[2]: 1.0}, ed * 0.04)
    anel(dd['dip'] + dd['dirs'][2] * comp3 * 0.76, 2, vezes(polpa_sec, 0.9), {osso[2]: 1.0}, ed * 0.08)
    k = 0.9 * _fator_cupula(comp3 * 0.93, comp3 * 0.76, ponta_t)
    ponta = anel(dd['dip'] + dd['dirs'][2] * comp3 * 0.93, 2, vezes(polpa_sec, k), {osso[2]: 1.0}, ed * 0.12)
    _soltar_dentro_das_juntas(g, aneis)
    _reforco_da_ponta(g, mao, aneis)
    # Zonas: couro na metade palmar do dedo inteiro (de um lado ao outro) e em volta da ponta (da polpa em diante);
    # tecido nas costas.
    for i, (a, b) in enumerate(zip(aneis[:-1], aneis[1:])):
        zonas = ['couro' if (i >= 9 or 3 <= k2 <= 6) else 'tecido' for k2 in range(8)]
        g.faixa(a, b, zonas)
        g.costura(a[7], b[7])  # lado de fora do dedo (para o mínimo)
    porta = aneis[0]
    for k2 in range(8):
        g.costura(porta[k2], porta[(k2 + 1) % 8])
    centro = dd['dip'] + dd['dirs'][2] * ponta_t - dd['normais'][2] * ed * 0.12
    c = g.v(centro, {osso[2]: 1.0})
    g.estufar[c] = mao.f['luva']['couro']
    for k2 in (0, 2, 4, 6):
        g.face((ponta[k2], ponta[k2 + 1], ponta[(k2 + 2) % 8], c), 'couro')
    g.costura(ponta[7], ponta[0])
    g.costura(ponta[0], c)


def _soltar_dentro_das_juntas(g, aneis):
    """Solta do ajuste ao limite o lado da palma (os pontos 4, 5 e 6) dos anéis de antes e de depois de cada junta
    (os anéis 2, 4, 6 e 8 a partir da porta, nos dedos e no polegar). No repouso a junta já dobra (PIP 20°, DIP 10°) e,
    por dentro, esses anéis ficam a 2,5 mm do anel do centro: forçar a superfície limite pelos três pontos tão juntos no
    lado côncavo cruzava a gaiola (o anel de antes passava à frente do de depois) e a malha dobrava sobre si mesma. O
    anel do centro, com a seção medida da junta, continua âncora."""
    for i in (2, 4, 6, 8):
        g.livres.update(aneis[i][k] for k in (4, 5, 6))


def _reforco_da_ponta(g, mao, aneis):
    """O reforço de couro da ponta (a volta da unha até a polpa): a camada de couro por cima do tecido, dos anéis da
    cúpula em diante, com a borda no anel da polpa (meia espessura: o degrau da borda)."""
    couro = mao.f['luva']['couro']
    for v in aneis[9]:
        g.estufar[v] = couro * 0.5
    for anel in aneis[10:12]:
        for v in anel:
            g.estufar[v] = couro


def _polegar(g, mao, porta):
    """Os anéis do polegar a partir da porta na palma: a tenar (um anel de transição entre a porta e a MCP, estufado para
    o lado da palma — o metacarpo do polegar some dentro da eminência tenar, só o que passa da MCP é "o dedo"), a MCP
    em três anéis, o meio da falange proximal, a IP em três anéis, a polpa e a cúpula da ponta. Devolve os anéis (sem
    a porta)."""
    p = mao.polegar
    luva = mao.luva
    lip, eip = p['ip_sec']
    fr = p['dirs'][0]
    mcp_sec = (lip * 1.10 + 2 * luva, eip * 1.12 + 2 * luva)
    ip_sec = (lip + 2 * luva, eip + 2 * luva)
    polpa_sec = (lip * 0.95 + 2 * luva, eip * 0.92 + 2 * luva)
    aneis = [porta]

    def anel(ponto, seg, sec, pesos, palmar=0.0):
        frente, costas = _referencial(p, seg)
        pts = _pontos_elipticos(ponto - costas * palmar, frente, costas, sec[0] / 2, sec[1] / 2)
        a = [g.v(q, pesos) for q in pts]
        aneis.append(a)
        return a

    def vezes(sec, k):
        return sec[0] * k, sec[1] * k

    comp2 = (p['ip'] - p['mcp']).length
    comp3 = (p['ponta'] - p['ip']).length
    e = 4.5
    # A tenar: a porta casada com o primeiro anel da MCP e o anel do meio entre os dois, estufado para fora — mais do
    # lado da palma (-Z), onde ficam os músculos da tenar, e pouco do lado das costas do metacarpo.
    mcp_menos = _pontos_elipticos(p['mcp'] - fr * e, fr, p['normais'][0], mcp_sec[0] / 2, mcp_sec[1] / 2)
    aneis[0] = _casar_porta(porta, mcp_menos)
    centro = sum((v.co for v in aneis[0]), Vector()).lerp(sum(mcp_menos, Vector()), 0.5) / 8.0
    tenar = []
    for v, q in zip(aneis[0], mcp_menos):
        meio = v.co.lerp(q, 0.5)
        fora = (meio - centro).normalized()
        tenar.append(g.v(meio + fora * (1.5 + 3.5 * max(0.0, -fora.z)), {'polegar_1': 0.75, 'mao': 0.25}))
    aneis.append(tenar)
    g.livres.update(tenar)
    anel(p['mcp'] - fr * e, 0, mcp_sec, {'polegar_1': 0.85, 'polegar_2': 0.15})
    anel(p['mcp'], (0, 1), vezes(mcp_sec, _BOJO_JUNTA), {'polegar_1': 0.5, 'polegar_2': 0.5})
    anel(p['mcp'] + p['dirs'][1] * e, 1, mcp_sec, {'polegar_1': 0.15, 'polegar_2': 0.85})
    meio = ((mcp_sec[0] + ip_sec[0]) / 2 * 0.97, (mcp_sec[1] + ip_sec[1]) / 2 * 0.95)
    anel(p['mcp'] + p['dirs'][1] * comp2 * 0.5, 1, meio, {'polegar_2': 1.0})
    e = 4.0
    anel(p['ip'] - p['dirs'][1] * e, 1, ip_sec, {'polegar_2': 0.85, 'polegar_3': 0.15})
    anel(p['ip'], (1, 2), vezes(ip_sec, _BOJO_JUNTA), {'polegar_2': 0.5, 'polegar_3': 0.5})
    anel(p['ip'] + p['dirs'][2] * e, 2, ip_sec, {'polegar_2': 0.15, 'polegar_3': 0.85})
    ponta_t = comp3 + luva
    anel(p['ip'] + p['dirs'][2] * comp3 * 0.45, 2, polpa_sec, {'polegar_3': 1.0}, eip * 0.04)
    anel(p['ip'] + p['dirs'][2] * comp3 * 0.76, 2, vezes(polpa_sec, 0.9), {'polegar_3': 1.0}, eip * 0.08)
    k = 0.9 * _fator_cupula(comp3 * 0.93, comp3 * 0.76, ponta_t)
    ponta = anel(p['ip'] + p['dirs'][2] * comp3 * 0.93, 2, vezes(polpa_sec, k), {'polegar_3': 1.0}, eip * 0.12)
    _soltar_dentro_das_juntas(g, aneis)
    _reforco_da_ponta(g, mao, aneis)
    # Zonas: couro na metade palmar (de um lado ao outro) e na ponta; a tenar é couro inteira (a palma continua nela).
    for i, (a, b) in enumerate(zip(aneis[:-1], aneis[1:])):
        zonas = ['couro' if (i <= 1 or i >= 9 or 3 <= k2 <= 6) else 'tecido' for k2 in range(8)]
        g.faixa(a, b, zonas)
        g.costura(a[7], b[7])
    porta = aneis[0]
    for k2 in range(8):
        g.costura(porta[k2], porta[(k2 + 1) % 8])
    c = g.v(p['ip'] + p['dirs'][2] * ponta_t - p['normais'][2] * eip * 0.12, {'polegar_3': 1.0})
    g.estufar[c] = mao.f['luva']['couro']
    for k2 in (0, 2, 4, 6):
        g.face((ponta[k2], ponta[k2 + 1], ponta[(k2 + 2) % 8], c), 'couro')
    g.costura(ponta[7], ponta[0])
    g.costura(ponta[0], c)
    return aneis[1:] + [[c]]


# ---------------------------------------------------------------------------------------------- malha
ZONAS_BASE = ('couro', 'tecido')


def malha_base(mao, colecao, materiais, nome='luva_d', subdividir=1):
    """O objeto da luva direita (metros): a gaiola ajustada ao limite, com os grupos de vértices dos ossos, as zonas em
    materiais, as costuras marcadas e a subdivisão aplicada (`subdividir` níveis, os vértices na superfície limite).
    `materiais` = {zona: material}. Devolve (objeto, maior resíduo do ajuste em mm)."""
    g = gerar_gaiola(mao)
    bm = g.bm
    bm.normal_update()
    for v, mm in g.estufar.items():
        v.co += v.normal * mm
    residuo = ajustar_ao_limite(bm, g.livres)
    bmesh.ops.scale(bm, vec=(S, S, S), verts=bm.verts[:])
    for e in bm.edges:
        e.seam = frozenset(e.verts) in g.costuras
    idx_zona = {z: i for i, z in enumerate(ZONAS_BASE)}
    bm.verts.index_update()
    pesos = [(v.index, g.pesos[v]) for v in bm.verts]
    # Os dicionários da gaiola têm as faces como chave e uma camada nova invalida as referências a elas: tudo que é
    # lido deles vem antes, pela ordem das faces (que a camada não muda).
    faces = [(idx_zona[g.zonas[f]], int(f in g.forro)) for f in bm.faces]
    camada_forro = bm.faces.layers.int.new('forro')
    for f, (zona, forro) in zip(bm.faces, faces):
        f.material_index = zona
        f.smooth = True
        f[camada_forro] = forro
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    colecao.objects.link(ob)
    for z in ZONAS_BASE:
        me.materials.append(materiais[z])
    grupos = {}
    for i, w in pesos:
        for osso, peso in w.items():
            if osso not in grupos:
                grupos[osso] = ob.vertex_groups.new(name=osso)
            grupos[osso].add([i], peso, 'REPLACE')
    if subdividir:
        m = ob.modifiers.new('subdividir', 'SUBSURF')
        m.levels = subdividir
        m.render_levels = subdividir
        m.use_limit_surface = True
        m.quality = 6
        m.uv_smooth = 'PRESERVE_BOUNDARIES'
        m.boundary_smooth = 'ALL'
        with bpy.context.temp_override(object=ob, active_object=ob):
            bpy.ops.object.modifier_apply(modifier=m.name)
    return ob, residuo
