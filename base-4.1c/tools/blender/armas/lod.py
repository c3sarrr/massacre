# Níveis de detalhe das armas realistas (Fase 4.1a; desenho, seções 4.3 e 5.1): o LOD1 (`mundo`) sai das peças de jogo
# sem as pequenas e sem chanfro, juntado por peça, dizimado até caber no orçamento e com UV próprio (assado de novo em
# 512/256); o LOD2 (`longe`) sai de uma cópia do LOD1 (as mesmas UVs, então as mesmas texturas) sem as ilhas pequenas da
# base e dizimado. Nenhuma peça móvel some: sem ela o nó não existiria e o jogo perderia a animação.
import bmesh
import bpy

from . import soquetes
from .unidades import S


def diagonal_mm(ob):
    d = [ob.dimensions.x, ob.dimensions.y, ob.dimensions.z]
    return (d[0] ** 2 + d[1] ** 2 + d[2] ** 2) ** 0.5 / S


def triangulos(objetos):
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for ob in objetos:
        me = ob.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        ob.evaluated_get(dg).to_mesh_clear()
    return total


def dizimar_ate(objetos, orcamento, margem=0.95, piso=12):
    """Mesma razão de dizimação em todas as peças, por bisseção, até caber em `orcamento` × `margem`; aplica. Peça
    pequena não desce de `piso` triângulos: a razão comum achatava o cão e o gatilho do longe em dois triângulos colados
    (a mesma face de frente e de costas), que o Draco reduz a um ao exportar."""
    antes = {ob.name: triangulos([ob]) for ob in objetos}
    for ob in objetos:
        m = ob.modifiers.new('dizimar', 'DECIMATE')
        m.decimate_type = 'COLLAPSE'
        m.use_collapse_triangulate = True

    def razao(ob, r):
        return min(1.0, max(r, piso / max(1, antes[ob.name])))
    lo, hi = 0.01, 1.0
    for _ in range(18):
        meio = (lo + hi) / 2
        for ob in objetos:
            ob.modifiers['dizimar'].ratio = razao(ob, meio)
        if triangulos(objetos) <= orcamento * margem:
            lo = meio
        else:
            hi = meio
    for ob in objetos:
        ob.modifiers['dizimar'].ratio = razao(ob, lo)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier='dizimar')
        _sem_degeneradas(ob)
        w = ob.modifiers.new('normais', 'WEIGHTED_NORMAL')
        w.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier='normais')
    return lo


def _sem_degeneradas(ob, distancia_mm=0.06):
    """Tira as arestas mais curtas que `distancia_mm`, as faces de área zero e as repetidas que a dizimação deixa: o
    Draco (posição em 14 bits, ~0,05 mm na arma inteira) as descarta ao exportar, e a contagem do relatório deixaria de
    bater com a do .glb."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.dissolve_degenerate(bm, dist=distancia_mm * S, edges=bm.edges[:])
    # A mesma face duas vezes (de frente e de costas): o Draco guarda uma só.
    bm.verts.index_update()
    vistas, repetidas = set(), []
    for f in bm.faces:
        chave = tuple(sorted(v.index for v in f.verts))
        if chave in vistas:
            repetidas.append(f)
        vistas.add(chave)
    if repetidas:
        bmesh.ops.delete(bm, geom=repetidas, context='FACES_ONLY')
    bm.to_mesh(ob.data)
    bm.free()


def lod_mundo(col_jogo, col_destino, pivos, orcamento, menor_mm=8.0):
    """LOD1 a partir das peças de jogo: some a peça da base menor que `menor_mm`; tira o chanfro; junta; dizima."""
    removidos = []
    for ob in col_jogo.objects:
        m = ob.modifiers.get('chanfro')
        if m is not None:
            m.show_render = False
            m.show_viewport = False
            removidos.append(m)
    filtro = lambda ob: ob.get('peca', 'base') != 'base' or diagonal_mm(ob) >= menor_mm
    partes = soquetes.juntar_pecas(col_jogo, col_destino, 'mundo', pivos, filtro)
    for m in removidos:
        m.show_render = True
        m.show_viewport = True
    objs = [partes[p] for p in pivos]
    razao = dizimar_ate(objs, orcamento)
    return partes, razao


def lod_longe(partes_mundo, col_destino, pivos, orcamento, menor_mm=25.0):
    """LOD2 a partir de cópias do LOD1 (mesmas UVs): some a ilha da base menor que `menor_mm`; dizima."""
    partes = {}
    for peca, ob in partes_mundo.items():
        if peca.startswith('_'):
            continue
        c = ob.copy()
        c.data = ob.data.copy()
        c.name = f'longe_{peca}'
        c.data.name = c.name
        col_destino.objects.link(c)
        if peca == 'base':
            bm = bmesh.new()
            bm.from_mesh(c.data)
            vistos = set()
            tirar = []
            for f in bm.faces:
                if f.index in vistos:
                    continue
                ilha, pilha = [], [f]
                vistos.add(f.index)
                while pilha:
                    g = pilha.pop()
                    ilha.append(g)
                    for e in g.edges:
                        for h in e.link_faces:
                            if h.index not in vistos:
                                vistos.add(h.index)
                                pilha.append(h)
                xs = [v.co for g in ilha for v in g.verts]
                dx = max(v.x for v in xs) - min(v.x for v in xs)
                dy = max(v.y for v in xs) - min(v.y for v in xs)
                dz = max(v.z for v in xs) - min(v.z for v in xs)
                if (dx * dx + dy * dy + dz * dz) ** 0.5 / S < menor_mm:
                    tirar.extend(ilha)
            if tirar:
                bmesh.ops.delete(bm, geom=list(set(tirar)), context='FACES')
            bm.to_mesh(c.data)
            bm.free()
        partes[peca] = c
    razao = dizimar_ate([partes[p] for p in pivos], orcamento)
    return partes, razao
