# Modelo alto da luva direita (Fase 4.1b; desenho em docs/superpowers/specs/2026-09-26-4.1b-luvas-e-empunhadura-design.md,
# seção 3.3; plano, Tarefa 4, Passo 2): a fonte do assar — o que vira relevo e máscaras nas texturas da luva de jogo.
#  - A base: a mesma gaiola ajustada ao limite, subdividida 4 níveis (a mesma superfície da de jogo, com vértices a
#    0,2–1,2 mm), com as rugas do tecido nas costas das juntas dos dedos e do polegar e no pulso, em deslocamento de
#    verdade.
#  - As costuras: as linhas onde os painéis se juntam (as costuras das UV e as fronteiras entre as zonas, que a
#    subdivisão leva da gaiola) viram atributos por vértice — `costura_d` (a distância à linha, mm) e `costura_s` (o
#    comprimento ao longo dela, mm), com `costura_ok` = 1 — e o relevo dos materiais (materiais.py) desenha o sulco na
#    linha e a fileira de pontos de 2,5 mm de cada lado, nítidos no pixel do assar. As peças levam a costura no
#    contorno (a linha é a borda delas).
#  - As máscaras dos padrões finos dos materiais: `antiderrapante` (o painel de reforço da palma, entre a primeira
#    estação e a da dobra do polegar), `velcro` (o puxador da tira) e `tira` (as nervuras moldadas da tira).
#  - As peças: as de jogo com a quina de cima vincada e subdivididas; os respiros (duas fendas por domo) e as nervuras
#    da ponte no protetor; três nervuras em cada almofada.
# Referências (moodboard, seção 15): QTG0–QTG3 e as fotos do TPR moldado (M-Pact) — costuras duplas nas bordas dos
# painéis, fendas nos domos, nervuras nas guardas dos dedos.
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import maos_gaiola
from .maos import DEDOS4
from .unidades import S

NIVEL_BASE = 4
_PASSO_AMOSTRA = 0.2  # mm entre as amostras das linhas de costura
# As rugas do tecido (mm): amplitude, período ao longo do dedo e a largura da faixa do pulso.
_RUGAS = {'amplitude': 0.22, 'periodo': 2.4, 'pulso': (-6.0, 7.0), 'amplitude_pulso': 0.16, 'periodo_pulso': 3.2}
# O protetor (mm): as fendas de cada domo (meio comprimento ao longo do dedo, meia largura, a distância entre as duas,
# a profundidade) e as nervuras da ponte (x a partir da linha dos nós, meia largura, altura).
_RESPIRO = {'meio_comp': 3.0, 'meia_larg': 0.85, 'afastamento': 2.6, 'fundo': 1.0, 'suave': 0.3}
_NERVURAS_PONTE = {'xs': (-19.0, -15.0, -11.0), 'meia_larg': 0.6, 'altura': 0.45}
# As almofadas: as nervuras (posições em fração do meio comprimento, meia largura e altura, mm).
_NERVURAS_ALMOFADA = {'us': (-0.45, 0.0, 0.45), 'meia_larg': 0.55, 'altura': 0.35}


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _atributo(me, nome, valores):
    at = me.attributes.get(nome) or me.attributes.new(nome, 'FLOAT', 'POINT')
    at.data.foreach_set('value', valores)


# ---------------------------------------------------------------------------------------------- linhas de costura
def _cadeias(pares):
    """As arestas (pares de índices) encadeadas em linhas: de ponta a ponta (vértices de grau ≠ 2) e os laços."""
    viz = {}
    for a, b in pares:
        viz.setdefault(a, []).append(b)
        viz.setdefault(b, []).append(a)
    usadas = set()
    cadeias = []

    def andar(inicio, prox):
        cadeia = [inicio, prox]
        usadas.add(frozenset((inicio, prox)))
        atual, antes = prox, inicio
        while len(viz[atual]) == 2:
            seguinte = viz[atual][0] if viz[atual][0] != antes else viz[atual][1]
            chave = frozenset((atual, seguinte))
            if chave in usadas:
                break
            usadas.add(chave)
            cadeia.append(seguinte)
            antes, atual = atual, seguinte
        return cadeia

    for v, vs in viz.items():
        if len(vs) != 2:
            for u in vs:
                if frozenset((v, u)) not in usadas:
                    cadeias.append(andar(v, u))
    for v, vs in viz.items():
        for u in vs:
            if frozenset((v, u)) not in usadas:
                cadeias.append(andar(v, u))
    return cadeias


def _amostras(pontos_das_cadeias):
    """KDTree das amostras (a cada _PASSO_AMOSTRA mm) das linhas, com o comprimento ao longo de cada uma."""
    amostras, ss = [], []
    for pts in pontos_das_cadeias:
        s = 0.0
        for a, b in zip(pts[:-1], pts[1:]):
            comp = (b - a).length
            n = max(1, int(math.ceil(comp / _PASSO_AMOSTRA)))
            for k in range(n):
                amostras.append(a.lerp(b, k / n))
                ss.append(s + comp * k / n)
            s += comp
        amostras.append(pts[-1])
        ss.append(s)
    kd = KDTree(len(amostras))
    for i, p in enumerate(amostras):
        kd.insert(p, i)
    kd.balance()
    return kd, ss


def _gravar_costura(ob, kd, ss):
    """Os atributos da costura nos vértices do objeto (mm, no referencial do mundo)."""
    me = ob.data
    mw = ob.matrix_world
    ds, sv = [], []
    for v in me.vertices:
        _co, i, dist = kd.find((mw @ v.co) / S)
        ds.append(dist)
        sv.append(ss[i])
    _atributo(me, 'costura_d', ds)
    _atributo(me, 'costura_s', sv)
    _atributo(me, 'costura_ok', [1.0] * len(me.vertices))


def costuras_da_base(ob):
    """As linhas de costura da base alta: as arestas marcadas como costura (as das UV, que a subdivisão leva da gaiola)
    e as fronteiras entre faces de zonas diferentes."""
    me = ob.data
    mw = ob.matrix_world
    zona_da_aresta = {}
    for p in me.polygons:
        for k in p.edge_keys:
            zona_da_aresta.setdefault(k, set()).add(p.material_index)
    pares = [tuple(e.vertices) for e in me.edges if e.use_seam or len(zona_da_aresta.get(e.key, ())) > 1]
    pts = [(mw @ v.co) / S for v in me.vertices]
    return [[pts[i] for i in c] for c in _cadeias(pares)]


# ---------------------------------------------------------------------------------------------- rugas e máscaras
def _pesos(ob):
    """[{osso: peso}] por vértice."""
    nomes = {g.index: g.name for g in ob.vertex_groups}
    return [{nomes[e.group]: e.weight for e in v.groups} for v in ob.data.vertices]


def _vertices_da_zona(me, zona):
    """Máscara (numpy, por vértice) dos vértices de alguma face da zona."""
    idx = maos_gaiola.ZONAS_BASE.index(zona)
    mats = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('material_index', mats)
    inicio = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('loop_start', inicio)
    total = np.empty(len(me.polygons), np.int32)
    me.polygons.foreach_get('loop_total', total)
    loops = np.empty(len(me.loops), np.int32)
    me.loops.foreach_get('vertex_index', loops)
    mask = np.zeros(len(me.vertices), bool)
    faces = np.nonzero(mats == idx)[0]
    for k in range(4):
        sel = faces[total[faces] > k]
        mask[loops[inicio[sel] + k]] = True
    return mask


def rugas(ob, mao):
    """As rugas do tecido: ondas de través nas costas de cada junta dos dedos (PIP e DIP) e do polegar (MCP e IP), num
    envelope de 3,5 mm em volta do centro da junta e só perto do eixo daquele dedo, e em volta do pulso, nas costas.
    Só no tecido (couro e reforços não enrugam assim). Em numpy, sobre todos os vértices de uma vez."""
    R = _RUGAS
    me = ob.data
    n_v = len(me.vertices)
    co = np.empty(n_v * 3)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3) / S
    nor = np.empty(n_v * 3)
    me.vertices.foreach_get('normal', nor)
    nor = nor.reshape(-1, 3)
    tecido = _vertices_da_zona(me, 'tecido')
    juntas = []
    for d in DEDOS4:
        dd = mao.dedos[d]
        (lp, ep), (ld, ed) = dd['pip_sec'], dd['dip_sec']
        juntas.append((dd['pip'], dd['dirs'][0] + dd['dirs'][1], dd['normais'][0] + dd['normais'][1], max(lp, ep) / 2))
        juntas.append((dd['dip'], dd['dirs'][1] + dd['dirs'][2], dd['normais'][1] + dd['normais'][2], max(ld, ed) / 2))
    p = mao.polegar
    lip, eip = p['ip_sec']
    juntas.append((p['mcp'], p['dirs'][0] + p['dirs'][1], p['normais'][0] + p['normais'][1], max(lip, eip) * 0.6))
    juntas.append((p['ip'], p['dirs'][1] + p['dirs'][2], p['normais'][1] + p['normais'][2], max(lip, eip) / 2))
    h = np.zeros(n_v)
    for ponto, frente, costas, raio in juntas:
        f = np.array(frente.normalized())
        c = np.array(costas.normalized())
        rel = co - np.array(ponto)
        t_ax = rel @ f
        lado = rel @ np.cross(c, f)
        radial = np.linalg.norm(rel - np.outer(t_ax, f), axis=1)
        costas_n = np.clip(nor @ c, 0.0, 1.0)
        env = np.exp(-(t_ax / 3.5) ** 2) * (radial < raio + mao.luva + 1.5)
        h += R['amplitude'] * env * costas_n ** 2 * np.sin(2 * np.pi * t_ax / R['periodo'] + 0.35 * np.sin(lado / 3.0))
    x0, x1 = R['pulso']
    no_pulso = (co[:, 0] > x0) & (co[:, 0] < x1) & (nor[:, 2] > 0.2)
    env = np.where(no_pulso, np.sin(np.pi * np.clip((co[:, 0] - x0) / (x1 - x0), 0, 1)) * nor[:, 2], 0.0)
    h += R['amplitude_pulso'] * env * np.sin(2 * np.pi * co[:, 0] / R['periodo_pulso'] + 0.5 * np.sin(co[:, 1] / 6.0))
    h *= tecido
    co += nor * h[:, None]
    me.vertices.foreach_set('co', (co * S).ravel())
    me.update()


def mascara_antiderrapante(ob, mao):
    """1 no painel de reforço da palma (a palma entre a primeira estação e a da dobra do polegar, fora dos dedos e do
    polegar), com a borda suave de 1,5 mm."""
    me = ob.data
    mw = ob.matrix_world
    couro = maos_gaiola.ZONAS_BASE.index('couro')
    no_couro = set()
    for p in me.polygons:
        if p.material_index == couro:
            no_couro.update(p.vertices)
    pesos = _pesos(ob)
    x0, x1 = maos_gaiola._PALMA[0][0], maos_gaiola._PALMA[2][0]
    valores = []
    for i, v in enumerate(me.vertices):
        co = (mw @ v.co) / S
        w = pesos[i]
        dedos = sum(p for o, p in w.items() if o.rsplit('_', 1)[0] in DEDOS4 and not o.endswith('_0'))
        pol = sum(p for o, p in w.items() if o.startswith('polegar_') and o != 'polegar_1')
        if i in no_couro and dedos < 0.3 and pol < 0.3 and co.z < 0:
            valores.append(_suave((co.x - x0) / 1.5) * _suave((x1 - co.x) / 1.5))
        else:
            valores.append(0.0)
    _atributo(me, 'antiderrapante', valores)


# ---------------------------------------------------------------------------------------------- peças
def _peca_alta(ob_jogo, colecao, nivel):
    """A peça de jogo copiada, com a quina de cima vincada (o contorno do topo), subdividida `nivel` níveis na superfície
    limite. Devolve o objeto e o índice dos vértices do contorno do topo (para a linha de costura)."""
    me = ob_jogo.data.copy()
    ob = bpy.data.objects.new(ob_jogo.name + '_alto', me)
    for k in ('zona', 'centro', 'frente', 'meio_comp'):
        if k in ob_jogo:
            ob[k] = ob_jogo[k]
    colecao.objects.link(ob)
    n_topo = ob_jogo['vertices_do_topo']
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    base = {v for v in bm.verts if v.index >= n_topo}
    contorno = {v for v in bm.verts if v.index < n_topo and any(e.other_vert(v) in base for e in v.link_edges)}
    vinco = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    for e in bm.edges:
        if e.verts[0] in contorno and e.verts[1] in contorno:
            e[vinco] = 0.75
        elif e.verts[0] in base and e.verts[1] in base:
            e[vinco] = 1.0
    bm.to_mesh(me)
    bm.free()
    m = ob.modifiers.new('subdividir', 'SUBSURF')
    m.levels = m.render_levels = nivel
    m.use_limit_surface = True
    m.quality = 6
    m.boundary_smooth = 'ALL'
    m.use_creases = True
    with bpy.context.temp_override(object=ob, active_object=ob):
        bpy.ops.object.modifier_apply(modifier=m.name)
    return ob


def _contorno_do_topo(ob_jogo):
    """A quina de cima da peça de jogo (os vértices do topo que tocam a base das paredes), encadeada em linha, em mm: a
    linha da costura do contorno (a peça alta arredonda a quina a menos de 0,3 mm dela)."""
    me = ob_jogo.data
    mw = ob_jogo.matrix_world
    n_topo = ob_jogo['vertices_do_topo']
    contorno = set()
    for e in me.edges:
        a, b = e.vertices
        if (a < n_topo) != (b < n_topo):
            contorno.add(a if a < n_topo else b)
    pares = [tuple(e.vertices) for e in me.edges if e.vertices[0] in contorno and e.vertices[1] in contorno]
    pts = [(mw @ v.co) / S for v in me.vertices]
    return [[pts[i] for i in c] for c in _cadeias(pares)]


def _deslocar_topo(ob, sup, altura_em):
    """Desloca os vértices do topo da peça (os virados para fora da luva, acima da borda) pela normal da luva embaixo
    deles: `altura_em(p)` em mm (negativa afunda). A normal da luva é a mesma para os vértices vizinhos; a do próprio
    vértice gira nas paredes de uma fenda e amassava a malha."""
    me = ob.data
    mw = ob.matrix_world
    rot = mw.to_3x3().normalized()
    inv = rot.inverted()
    novos = []
    for v in me.vertices:
        p = (mw @ v.co) / S
        _q, n_sup = sup.perto(p)
        n = (rot @ v.normal).normalized()
        if n.dot(n_sup) < 0.6 or sup.distancia(p) < 0.6:
            continue
        h = altura_em(p)
        if h:
            novos.append((v, inv @ (n_sup * (h * S))))
    for v, d in novos:
        v.co += d


def _faixa(d, meia, suave=0.25):
    """1 dentro de |d| < meia, 0 fora, com a transição de `suave` mm."""
    return _suave((meia + suave - abs(d)) / (2 * suave))


def protetor_alto(ob_jogo, mao, sup, colecao):
    # Nível 4: as fendas dos domos têm 1,7 mm de largura (vértices a ~0,2 mm; no nível 3 a borda delas serrilhava).
    ob = _peca_alta(ob_jogo, colecao, 4)
    Rp, N = _RESPIRO, _NERVURAS_PONTE

    def x_mcp(y):
        pts = sorted((mao.y_no[d], mao.dedos[d]['mcp'].x) for d in DEDOS4)
        if y <= pts[0][0]:
            return pts[0][1]
        if y >= pts[-1][0]:
            return pts[-1][1]
        for (y0, x0), (y1, x1) in zip(pts[:-1], pts[1:]):
            if y0 <= y <= y1:
                return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
        return pts[-1][1]

    y_min, y_max = mao.y_no['minimo'] - 5.0, mao.y_no['indicador'] + 5.0

    def altura(p):
        fenda = 0.0
        for d in DEDOS4:
            cx, cy = mao.dedos[d]['mcp'].x + 1.5, mao.y_no[d]
            for lado in (-1, 1):
                dy = p.y - (cy + lado * Rp['afastamento'])
                dx = max(0.0, abs(p.x - cx) - (Rp['meio_comp'] - Rp['meia_larg']))
                fenda = max(fenda, _faixa(math.hypot(dx, dy), Rp['meia_larg'], Rp['suave']))
        nervura = 0.0
        if y_min < p.y < y_max:
            dx = p.x - x_mcp(p.y)
            nervura = max(_faixa(dx - xn, N['meia_larg'], 0.25) for xn in N['xs'])
        return N['altura'] * nervura - Rp['fundo'] * fenda

    _deslocar_topo(ob, sup, altura)
    return ob


def almofada_alta(ob_jogo, sup, colecao):
    ob = _peca_alta(ob_jogo, colecao, 3)
    Na = _NERVURAS_ALMOFADA
    centro, frente, meio = Vector(ob['centro']), Vector(ob['frente']), ob['meio_comp']

    def altura(p):
        t = (p - centro).dot(frente) / meio
        return max(Na['altura'] * _faixa((t - u) * meio, Na['meia_larg'], 0.25) for u in Na['us'])

    _deslocar_topo(ob, sup, altura)
    return ob


def construir(mao, materiais, pecas_jogo, colecao, etapa=lambda nome: None):
    """O modelo alto da luva direita na coleção `colecao`: a base (nível 4, rugas, costuras e máscaras) e as peças
    altas (com as costuras no contorno). `materiais` = {zona: material}; `pecas_jogo` = as peças de maos_detalhes.
    Devolve a lista dos objetos."""
    base, _ = maos_gaiola.malha_base(mao, colecao, {z: materiais[z] for z in maos_gaiola.ZONAS_BASE}, 'luva_d_alto',
                                     subdividir=NIVEL_BASE)
    etapa('alto: base no nível 4')
    kd, ss = _amostras(costuras_da_base(base))
    _gravar_costura(base, kd, ss)
    etapa('alto: costuras da base')
    mascara_antiderrapante(base, mao)
    _atributo(base.data, 'velcro', [0.0] * len(base.data.vertices))
    _atributo(base.data, 'tira', [0.0] * len(base.data.vertices))
    etapa('alto: máscaras')
    rugas(base, mao)
    etapa('alto: rugas')
    from .maos_detalhes import Superficie
    sup = Superficie(base)
    altos = [base]
    for ob_jogo in pecas_jogo:
        nome = ob_jogo.name
        if nome.endswith('_protetor'):
            ob = protetor_alto(ob_jogo, mao, sup, colecao)
        elif '_almofada_' in nome:
            ob = almofada_alta(ob_jogo, sup, colecao)
        else:
            ob = _peca_alta(ob_jogo, colecao, 2)
        kd_p, ss_p = _amostras(_contorno_do_topo(ob_jogo))
        _gravar_costura(ob, kd_p, ss_p)
        _atributo(ob.data, 'antiderrapante', [0.0] * len(ob.data.vertices))
        _atributo(ob.data, 'velcro', [1.0 if nome.endswith('_puxador') else 0.0] * len(ob.data.vertices))
        _atributo(ob.data, 'tira', [1.0 if nome.endswith('_tira') else 0.0] * len(ob.data.vertices))
        ob.data.materials.clear()
        ob.data.materials.append(materiais[ob['zona']])
        altos.append(ob)
    etapa('alto: peças')
    return altos
