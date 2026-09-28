# Soquetes e peças móveis das armas realistas (Fase 4.1a; desenho, seção 4.2). Soquete = vazio `soquete_<nome>` com
# posição e orientação. Peça móvel = as peças marcadas com o mesmo `peca`, com os modificadores aplicados, juntadas num
# objeto `<nivel>_<peca>` triangulado, com a origem no pivô real (o eixo de giro ou a linha de deslize); `base` é o resto
# da arma. As
# faces da base que ficam inteiras dentro de outra peça da base (cano dentro do munhão, espiga da coronha dentro do
# receptor) saem no modelo de jogo — só a face com todos os cantos e o centro dentro da outra peça e longe da superfície
# dela, para nenhuma face em parte visível sumir; as das peças móveis ficam, porque aparecem quando a peça se mexe.
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from .unidades import S, ficha


def soquete(colecao, nome, x, y, lado=0.0, rot=(0.0, 0.0, 0.0)):
    """Vazio `soquete_<nome>` no ponto (x, y) da ficha, com `lado` = Y do Blender (mm) e a rotação XYZ em graus."""
    ob = bpy.data.objects.new(f'soquete_{nome}', None)
    ob.empty_display_type = 'ARROWS'
    ob.empty_display_size = 0.02
    ob.location = ficha(x, y, lado)
    ob.rotation_euler = [math.radians(a) for a in rot]
    colecao.objects.link(ob)
    return ob


def _aplicadas(objetos, colecao, nome):
    """Cópias das peças com os modificadores aplicados (normais personalizadas preservadas), cada uma só com o material
    da zona dela: o booleano deixa na lista da malha avaliada o material do cortador, sem face nenhuma."""
    dg = bpy.context.evaluated_depsgraph_get()
    copias = []
    for ob in objetos:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        zona = ob.data.materials[0]
        me.materials.clear()
        me.materials.append(zona)
        me.polygons.foreach_set('material_index', [0] * len(me.polygons))
        c = bpy.data.objects.new(f'{nome}.{ob.name}', me)
        c.matrix_world = ob.matrix_world.copy()
        colecao.objects.link(c)
        copias.append(c)
    return copias


_DIRECOES = (Vector((0.577, 0.577, 0.577)), Vector((-0.267, 0.534, -0.802)), Vector((0.832, -0.555, 0.0)))


def _dentro(bvh, p):
    """Ponto dentro de uma malha fechada: paridade dos cruzamentos de um raio, em três direções (a maioria decide; um
    raio que raspa uma aresta conta um cruzamento a mais)."""
    votos = 0
    for direcao in _DIRECOES:
        n = 0
        origem = p.copy()
        for _ in range(64):
            hit, _nrm, _i, _d = bvh.ray_cast(origem, direcao)
            if hit is None:
                break
            n += 1
            origem = hit + direcao * 1e-6
        votos += n % 2
    return votos >= 2


def _escondida(bvh, pontos, folga):
    """Todos os pontos dentro da malha fechada e a mais de `folga` (m) da superfície dela: ponto na superfície (peças
    que só se encostam) não esconde nada."""
    for p in pontos:
        _co, _nrm, _i, dist = bvh.find_nearest(p)
        if dist is None or dist < folga or not _dentro(bvh, p):
            return False
    return True


def remover_escondidas(copias, folga_mm=0.02):
    """Tira das cópias da base as faces inteiras dentro de outra cópia da base (malhas fechadas): os cantos e o centro
    da face dentro dela e a mais de `folga_mm` da superfície."""
    dg = bpy.context.evaluated_depsgraph_get()
    arvores = {c.name: BVHTree.FromObject(c, dg, deform=False) for c in copias}
    mundos = {c.name: c.matrix_world for c in copias}
    caixas = {}
    for c in copias:
        pts = [c.matrix_world @ Vector(v) for v in c.bound_box]
        caixas[c.name] = (Vector((min(q.x for q in pts), min(q.y for q in pts), min(q.z for q in pts))),
                          Vector((max(q.x for q in pts), max(q.y for q in pts), max(q.z for q in pts))))
    removidas = 0
    for c in copias:
        bm = bmesh.new()
        bm.from_mesh(c.data)
        tirar = []
        for f in bm.faces:
            pontos = [mundos[c.name] @ f.calc_center_median()] + [mundos[c.name] @ v.co for v in f.verts]
            for outra in copias:
                if outra is c:
                    continue
                lo, hi = caixas[outra.name]
                if not all(lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y and lo.z <= q.z <= hi.z for q in pontos):
                    continue
                inversa = mundos[outra.name].inverted()
                if _escondida(arvores[outra.name], [inversa @ q for q in pontos], folga_mm * S):
                    tirar.append(f)
                    break
        if tirar:
            bmesh.ops.delete(bm, geom=tirar, context='FACES')
            removidas += len(tirar)
            bm.to_mesh(c.data)
        bm.free()
    return removidas


def juntar_pecas(colecao_origem, colecao_destino, prefixo, pivos, filtro=None):
    """Um objeto `<prefixo>_<peca>` por peça (base e móveis), com a origem no pivô (mm da ficha).
    `filtro(ob)` decide que peças entram (o LOD tira as pequenas). Devolve {peca: objeto, '_removidas': n}."""
    grupos = {}
    for ob in colecao_origem.objects:
        if ob.type != 'MESH' or ob.get('cortador') or ob.hide_render:
            continue
        if filtro and not filtro(ob):
            continue
        grupos.setdefault(ob.get('peca', 'base'), []).append(ob)
    faltando = [p for p in pivos if p not in grupos]
    if faltando:
        raise ValueError(f'peças sem nenhum objeto: {", ".join(faltando)}')
    saida = {'_removidas': 0}
    for peca, objetos in grupos.items():
        nome = f'{prefixo}_{peca}'
        copias = _aplicadas(objetos, colecao_destino, nome)
        if peca == 'base':
            saida['_removidas'] = remover_escondidas(copias)
        bpy.ops.object.select_all(action='DESELECT')
        for c in copias:
            c.select_set(True)
        bpy.context.view_layer.objects.active = copias[0]
        if len(copias) > 1:
            bpy.ops.object.join()
        alvo = bpy.context.view_layer.objects.active
        alvo.name = nome
        alvo.data.name = nome
        # Triangulado (desenho, seção 4.3): o exportador só calcula as tangentes (MikkTSpace) em triângulos e
        # quadriláteros e pula sem aviso a malha com n-gonos; triangulada aqui, o assar e o .glb usam o mesmo
        # referencial do relevo. As normais personalizadas (chanfros duros, normais ponderadas) ficam.
        tri = alvo.modifiers.new('triangular', 'TRIANGULATE')
        tri.quad_method = 'BEAUTY'
        tri.ngon_method = 'BEAUTY'
        tri.keep_custom_normals = True
        with bpy.context.temp_override(object=alvo, active_object=alvo):
            bpy.ops.object.modifier_apply(modifier='triangular')
        # o pivô é (x, y) da ficha ou (x, y, lado): a dobradiça da tampa da janela da M4 fica na face direita
        pivo, extras = pivos[peca]
        bpy.context.scene.cursor.location = ficha(*pivo)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        for chave in list(alvo.keys()):
            del alvo[chave]
        for chave, valor in extras.items():
            alvo[chave] = valor
        saida[peca] = alvo
    return saida
