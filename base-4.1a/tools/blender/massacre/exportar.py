"""Exportar: a cena do Blender volta a ser a receita (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

Lê a coleção `MASSACRE <id>`: as peças de cada `grupo:<nome>` (na ordem guardada; cópias entram depois da original),
os pivôs, as âncoras e as massas. Converte os eixos (Blender → jogo), dobra a escala dos objetos nos parâmetros da forma
e usa o valor guardado na importação sempre que o novo é o mesmo (dentro de 5·10⁻⁵ u): sem edição, a receita volta
idêntica. Nas peças definidas por pontos a origem do objeto é o centro da peça (importar.centro_local): mover e escalar
mexem nos pontos e o `pos` guardado fica; girar leva a peça para o referencial do objeto. A validação completa é a do jogo (tools/blender.mjs valida antes de gravar por cima da receita).
"""

import json

import bpy
from mathutils import Vector

from . import eixos
from .importar import LIVRES, centro_local

TOL = 5e-5
GEOMETRIA = ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT')


def _perto(a, b, tol=TOL):
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_perto(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= tol
    return a == b


def _manter(guardado, novo):
    """O guardado se o novo é o mesmo; senão o novo (o formato canônico arredonda na gravação)."""
    return guardado if guardado is not None and _perto(guardado, novo) else novo


def raiz_da_cena():
    for c in bpy.data.collections:
        if c.name.startswith('MASSACRE ') and 'massacre' in c:
            return c
    raise RuntimeError('a cena não tem uma arma importada (coleção "MASSACRE <id>")')


def grupo_de(obj):
    for c in obj.users_collection:
        if c.name.startswith('grupo:'):
            return c.name[len('grupo:'):]
    return None


def _massa_de(obj):
    for slot in obj.material_slots:
        if slot.material and slot.material.name.startswith('massa:'):
            return slot.material.name[len('massa:'):]
    return None


def _caixa_local(obj):
    """Caixa dos vértices da malha (sem modificadores), no referencial da peça."""
    vs = [v.co for v in obj.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    return lo, hi


def _bisel(obj):
    m = obj.modifiers.get('bisel')
    return m.width if m else 0.0


def _ordem_das_arestas(me):
    """Vértices do meridiano na ordem das arestas, a partir do vértice 0 (o torno volta na ordem em que foi feito)."""
    viz = {v.index: [] for v in me.vertices}
    for e in me.edges:
        a, b = e.vertices
        viz[a].append(b)
        viz[b].append(a)
    ordem, anterior, atual = [0], None, 0
    while True:
        prox = [n for n in viz[atual] if n != anterior and n not in ordem]
        if not prox:
            break
        anterior, atual = atual, prox[0]
        ordem.append(atual)
    return [me.vertices[i].co for i in ordem]


def _pos(p, p0, pos):
    """`pos` na peça: ausente se era ausente e continua na origem; o guardado se não mudou."""
    if 'pos' not in p0 and _perto(list(pos), [0.0, 0.0, 0.0]):
        p.pop('pos', None)
    else:
        p['pos'] = _manter(p0.get('pos'), list(pos))


def _exportar_livre(obj, p0, p, loc, rot3, esc):
    """Peça definida por pontos (a origem do objeto no centro dela, importar.centro_local). Sem giro, o referencial
    guardado fica: a translação e a escala voltam aos pontos (o que o ponto não leva — o Z do perfil, o Y/Z do torno —
    vai para `pos`). Com giro, o referencial passa a ser o do objeto."""
    s = p0['shape']
    c = centro_local(p0)
    S = esc
    if eixos.mesma_rotacao(rot3, p0.get('rot')):
        R = eixos.rot_jogo(p0.get('rot'))
        pos = Vector(p0.get('pos', (0.0, 0.0, 0.0)))
        desl = c + R.transposed() @ (loc - (pos + R @ c))  # onde o centro foi parar, no referencial guardado
    else:
        R = rot3
        desl = Vector((S.x * c.x, S.y * c.y, S.z * c.z))
        pos = loc - R @ desl
        p['rot'] = eixos.euler_jogo(R)
    resto = Vector((0.0, 0.0, desl.z)) if s == 'profile' else Vector((0.0, desl.y, desl.z)) if s == 'lathe' else Vector()
    _pos(p, p0, pos + R @ resto)
    desl = desl - resto
    media = (S.x + S.y + S.z) / 3
    if s == 'profile':
        cu = obj.data
        pts = [[pt.co.x * S.x + desl.x, pt.co.y * S.y + desl.y] for pt in cu.splines[0].points]
        p['points'] = _manter(p0['points'], pts)
        rd = cu.bevel_depth
        p['h'] = _manter(p0['h'], (cu.extrude + rd) * S.z)
        if 'round' in p0 or rd > 0:
            # A importação limita o bisel à meia-espessura (como o SDF): o guardado vale se o limite bate.
            novo = rd * min(S.x, S.y, S.z)
            limitado = min(p0.get('round', 0), p0['h'])
            p['round'] = p0['round'] if 'round' in p0 and _perto(limitado, novo) else novo
    elif s == 'lathe':
        pts = [[v.x * S.x + desl.x, v.y * (S.y + S.z) / 2] for v in _ordem_das_arestas(obj.data)]
        p['points'] = _manter(p0['points'], pts)
    elif s == 'tube':
        sp = obj.data.splines[0]
        pts = [[pt.co.x * S.x + desl.x, pt.co.y * S.y + desl.y, pt.co.z * S.z + desl.z] for pt in sp.points]
        raios = [pt.radius * obj.data.bevel_depth * media for pt in sp.points]
        p['points'] = _manter(p0['points'], pts)
        if 'r' in p0 and all(abs(r - raios[0]) <= TOL for r in raios):
            p['r'] = _manter(p0['r'], raios[0])
        else:
            p.pop('r', None)
            p['radii'] = _manter(p0.get('radii'), raios)
    else:  # capsule, roundCone: as pontas saem da peça guardada (a malha é só o desenho)
        for k in ('a', 'b'):
            v = Vector(p0[k]) - c
            p[k] = _manter(p0[k], [v.x * S.x + desl.x, v.y * S.y + desl.y, v.z * S.z + desl.z])
        for k in (('r',) if s == 'capsule' else ('ra', 'rb')):
            p[k] = _manter(p0[k], p0[k] * media)


def exportar_peca(obj, p0):
    """A peça de um objeto: transformação, grupo e massa do Blender; parâmetros da forma com a escala dobrada."""
    loc, rot3, esc = eixos.para_jogo(obj.matrix_world)
    p = dict(p0)
    p['name'] = obj.name
    p['group'] = grupo_de(obj) or p0['group']
    p['mat'] = _massa_de(obj) or p0['mat']
    s = p0['shape']
    if s in LIVRES:
        _exportar_livre(obj, p0, p, loc, rot3, esc)
        return p
    # Formas centradas (malhas geradas pelos parâmetros): o centro da caixa dos vértices (se a malha foi mexida no
    # modo de edição) entra na posição; a escala entra nos parâmetros.
    sx, sy, sz = esc.x, esc.y, esc.z
    media_xz = (sx + sz) / 2
    lo, hi = _caixa_local(obj)
    meia = (hi - lo) / 2
    c = (hi + lo) / 2
    centro = Vector((c.x * sx, c.y * sy, c.z * sz)) if c.length > TOL else Vector((0.0, 0.0, 0.0))
    _pos(p, p0, loc + rot3 @ centro)
    if not eixos.mesma_rotacao(rot3, p0.get('rot')):
        p['rot'] = eixos.euler_jogo(rot3)
    if s == 'roundBox':
        p['size'] = _manter(p0['size'], [meia.x * sx, meia.y * sy, meia.z * sz])
        r = _bisel(obj) * min(sx, sy, sz)
        if 'r' in p0 or r > 0:
            p['r'] = _manter(p0.get('r'), r)
    elif s == 'cylinder':
        p['r'] = _manter(p0['r'], (meia.x + meia.z) / 2 * media_xz)
        p['h'] = _manter(p0['h'], meia.y * sy)
        rd = _bisel(obj) * min(sx, sy, sz)
        if 'round' in p0 or rd > 0:
            p['round'] = _manter(p0.get('round'), rd)
    elif s == 'cone':
        vs = [v.co for v in obj.data.vertices]
        y0 = min(v.y for v in vs)
        y1 = max(v.y for v in vs)
        raio = lambda y: max((Vector((v.x, v.z)).length for v in vs if abs(v.y - y) < 1e-4), default=0.0)
        p['h'] = _manter(p0['h'], (y1 - y0) / 2 * sy)
        p['r1'] = _manter(p0['r1'], raio(y0) * media_xz)
        p['r2'] = _manter(p0['r2'], raio(y1) * media_xz)
    elif s == 'sphere':
        p['r'] = _manter(p0['r'], (meia.x * sx + meia.y * sy + meia.z * sz) / 3)
    elif s == 'ellipsoid':
        p['radii'] = _manter(p0['radii'], [meia.x * sx, meia.y * sy, meia.z * sz])
    elif s == 'torus':
        r = meia.y * sy
        p['r'] = _manter(p0['r'], r)
        p['R'] = _manter(p0['R'], (meia.x * sx + meia.z * sz) / 2 - r)
    return p


def exportar():
    """Lê a cena e devolve (receita, cabecalho)."""
    bpy.context.view_layer.update()  # matrizes do mundo em dia (num script, mexer em location não as recalcula)
    raiz = raiz_da_cena()
    topo = json.loads(raiz['massacre'])
    cabecalho = topo.pop('cabecalho')
    ordem_ancoras = topo.pop('ordemAncoras')
    materials = dict(topo['materials'])
    for m in bpy.data.materials:
        if m.name.startswith('massa:') and 'massacre_massa' in m and m.users > 0:
            materials.setdefault(m.name[len('massa:'):], m['massacre_massa'])

    colecoes = sorted((c for c in raiz.children if c.name.startswith('grupo:')), key=lambda c: c.get('massacre_ordem', 99))
    groups = {}
    for c in colecoes:
        g = c.name[len('grupo:'):]
        pivo = bpy.data.objects.get(f'pivo:{g}')
        d0 = json.loads(pivo['massacre_grupo']) if pivo and 'massacre_grupo' in pivo else {}
        d = dict(d0)
        if pivo:
            loc, _, _ = eixos.para_jogo(pivo.matrix_world)
            d['pivot'] = _manter(d0.get('pivot'), list(loc))
        groups[g] = d

    # Objeto de geometria sem a peça guardada não tem forma do jogo: nada some calado na exportação.
    soltos = sorted(o.name for o in bpy.data.objects if o.type in GEOMETRIA and o.users_collection
                    and not any(k in o for k in ('massacre_parte', 'massacre_proxy', 'massacre_planta', 'massacre_previa')))
    if soltos:
        raise RuntimeError('objetos sem receita: ' + ', '.join(soltos) + ' — peça nova é cópia de uma peça da mesma '
                           'forma (Shift+D); o resto, apague')
    objetos = []
    for c in colecoes:
        for obj in c.objects:
            if 'massacre_parte' in obj:
                objetos.append(obj)
    objetos.sort(key=lambda o: (o['massacre_ordem'], o.name))
    parts = [exportar_peca(o, json.loads(o['massacre_parte'])) for o in objetos]

    anchors = {}
    empties = {o.name[len('ancora:'):]: o for o in bpy.data.objects if o.name.startswith('ancora:') and 'massacre_ancora' in o}
    for nome in [n for n in ordem_ancoras if n in empties] + sorted(n for n in empties if n not in ordem_ancoras):
        e = empties[nome]
        a0 = json.loads(e['massacre_ancora'])
        a = dict(a0)
        loc, rot3, _ = eixos.para_jogo(e.matrix_world)
        a['pos'] = _manter(a0['pos'], list(loc))
        if not eixos.mesma_rotacao(rot3, a0.get('rot')):
            a['rot'] = eixos.euler_jogo(rot3)
        if 'pose' in e:
            a['pose'] = e['pose']
        anchors[nome] = a

    receita = {**{k: topo[k] for k in ('id', 'version', 'refs') if k in topo}, 'materials': materials}
    if topo.get('soft'):
        receita['soft'] = topo['soft']
    receita.update({'groups': groups, 'anchors': anchors, 'parts': parts})
    return receita, cabecalho
