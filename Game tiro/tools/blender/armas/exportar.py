# Exportação das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
# seção 4.5; plano da 4.1a, D1 e D2): a hierarquia do .glb — raiz `<id>`, os níveis `perto`, `mundo` e `longe` com as
# peças `<nivel>_<peca>` (origem no pivô), os soquetes `soquete_<nome>` dentro de `soquetes` —, a escala para u
# (1000/25,4) com a origem no pino do gatilho e o glTF binário com o Y para cima, as tangentes, as UV, as normais e os
# extras (o eixo das peças móveis), com a geometria comprimida pelo Draco (decisão do usuário de 2026-09-26: a AK cai de
# 1,22 para 0,29 MB; posição em 14 bits, normal em 10, UV e tangente em 12). As texturas já foram gravadas pelo assar;
# o relatório vai ao lado. As luvas (Fase 4.1b) têm a exportação delas, com skin (`exportar_luvas`).
import json
import os

import bpy
from mathutils import Matrix, Vector

from . import gravar, maos_rig
from .unidades import S, U_POR_M


def _vazio(nome, colecao, pai=None):
    ob = bpy.data.objects.new(nome, None)
    colecao.objects.link(ob)
    ob.parent = pai
    return ob


def _mover(ob, colecao):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    colecao.objects.link(ob)


def exportar(ctx, origem_mm, lods, soquetes_objs, pasta, pega=None):
    """Monta a hierarquia na escala do jogo e grava `<id>.glb`. `pega` = os objetos da pega das luvas
    (empunhadura_pega.objetos_da_saida: o vazio `pega`, os `pega_mao_*` e a armadura com a ação `empunhadura`), que
    entram debaixo da raiz com a animação (D1). Muda a cena: a .blend da conferência é gravada antes."""
    col = bpy.data.collections.new('exportar')
    bpy.context.scene.collection.children.link(col)
    origem = Vector((origem_mm[0] * S, 0.0, origem_mm[1] * S))
    escala = Matrix.Scale(U_POR_M, 4)
    raiz = _vazio(ctx['id'], col)
    selecionados = [raiz]
    for nome, partes in lods.items():
        grupo = _vazio(nome, col, raiz)
        selecionados.append(grupo)
        for peca, ob in partes.items():
            if peca.startswith('_'):
                continue
            ob.data.transform(escala)
            ob.location = (ob.location - origem) * U_POR_M
            _mover(ob, col)
            ob.parent = grupo
            selecionados.append(ob)
    pasta_soq = _vazio('soquetes', col, raiz)
    selecionados.append(pasta_soq)
    for s in soquetes_objs:
        s.location = (s.location - origem) * U_POR_M
        _mover(s, col)
        s.parent = pasta_soq
        selecionados.append(s)
    if pega:
        no_pega, *filhos = pega
        _mover(no_pega, col)
        no_pega.parent = raiz
        selecionados.append(no_pega)
        for ob in filhos:
            mundo = ob.matrix_world.copy()
            _mover(ob, col)
            ob.parent = no_pega
            if ob.type == 'ARMATURE':
                # a armadura em metros no referencial do Blender, levada à escala e à origem do jogo (o jogo só lê as
                # rotações dos ossos de dedo, que não mudam com isso)
                ob.matrix_world = Matrix.Scale(U_POR_M, 4) @ Matrix.Translation(-origem) @ mundo
            else:
                ob.matrix_world = Matrix.Translation((mundo.translation - origem) * U_POR_M) @ mundo.to_quaternion().to_matrix().to_4x4()
            selecionados.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for o in selecionados:
        o.select_set(True)
    bpy.context.view_layer.objects.active = raiz
    caminho = os.path.join(pasta, f"{ctx['id']}.glb")
    gravar.com_novas_tentativas(lambda: bpy.ops.export_scene.gltf(
        filepath=caminho, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
        export_texcoords=True, export_normals=True, export_tangents=True, export_materials='EXPORT',
        export_image_format='NONE', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=bool(pega), export_animation_mode='ACTIONS', export_force_sampling=True,
        export_frame_range=False, export_skins=bool(pega), export_morph=False, export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=12), caminho)
    return caminho


def exportar_luvas(pasta, bracos, marcas):
    """Grava `luvas.glb` (Fase 4.1b; plano, Tarefa 6, D3 e D4): a raiz `luvas` na escala do jogo (u por metro; dentro,
    a cena em metros) com a marca do rig de cada braço nos extras, e para cada braço (`bracos` = [(luva, rig)]) a
    armadura em repouso e a malha com skin — uma primitiva por zona, com o atributo `_VERTICE` (o índice do vértice no
    Blender: o jogo casa com ele o modelo das dobras e as amarras das peças, indexados pelos vértices do Blender, com os
    do glTF, que as costuras de UV duplicam e o Draco reordena) e as correções das dobras nos extras. O Draco com a
    quantização genérica em 16 bits: o `_VERTICE` sai em ponto flutuante, e em 12 bits o passo passava de 0,8 com uns
    3 400 vértices. Muda a cena: a .blend da conferência é gravada antes."""
    col = bpy.data.collections.new('exportar_luvas')
    bpy.context.scene.collection.children.link(col)
    raiz = _vazio('luvas', col)
    raiz.scale = (U_POR_M, U_POR_M, U_POR_M)
    raiz['marca'] = dict(marcas)
    selecionados = [raiz]
    for luva, rig in bracos:
        maos_rig.posar(rig, {})
        _mover(rig, col)
        rig.parent = raiz
        _mover(luva, col)
        luva.parent = rig
        me = luva.data
        vert = me.attributes.get('_VERTICE') or me.attributes.new('_VERTICE', 'FLOAT', 'POINT')
        vert.data.foreach_set('value', [float(i) for i in range(len(me.vertices))])
        selecionados += [rig, luva]
    bpy.ops.object.select_all(action='DESELECT')
    for o in selecionados:
        o.select_set(True)
    bpy.context.view_layer.objects.active = raiz
    caminho = os.path.join(pasta, 'luvas.glb')
    gravar.com_novas_tentativas(lambda: bpy.ops.export_scene.gltf(
        filepath=caminho, export_format='GLB', use_selection=True, export_yup=True, export_apply=False,
        export_texcoords=True, export_normals=True, export_tangents=True, export_materials='EXPORT',
        export_image_format='NONE', export_extras=True, export_attributes=True, export_cameras=False,
        export_lights=False, export_animations=False, export_skins=True, export_morph=False,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=16), caminho)
    return caminho


def gravar_relatorio(pasta, id_, relatorio):
    caminho = os.path.join(pasta, f'{id_}.relatorio.json')

    def escrever():
        with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=1)
            f.write('\n')
    gravar.com_novas_tentativas(escrever, caminho)
    return caminho
