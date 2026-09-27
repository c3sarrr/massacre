# Exportação das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
# seção 4.5; plano da 4.1a, D1 e D2): a hierarquia do .glb — raiz `<id>`, os níveis `perto`, `mundo` e `longe` com as
# peças `<nivel>_<peca>` (origem no pivô), os soquetes `soquete_<nome>` dentro de `soquetes` —, a escala para u
# (1000/25,4) com a origem no pino do gatilho e o glTF binário com o Y para cima, as tangentes, as UV, as normais e os
# extras (o eixo das peças móveis), com a geometria comprimida pelo Draco (decisão do usuário de 2026-09-26: a AK cai de
# 1,22 para 0,29 MB; posição em 14 bits, normal em 10, UV e tangente em 12). As texturas já foram gravadas pelo assar;
# o relatório vai ao lado.
import json
import os

import bpy
from mathutils import Matrix, Vector

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


def exportar(ctx, origem_mm, lods, soquetes_objs, pasta):
    """Monta a hierarquia na escala do jogo e grava `<id>.glb`. Muda a cena: a .blend da conferência é gravada antes."""
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
    bpy.ops.object.select_all(action='DESELECT')
    for o in selecionados:
        o.select_set(True)
    bpy.context.view_layer.objects.active = raiz
    caminho = os.path.join(pasta, f"{ctx['id']}.glb")
    bpy.ops.export_scene.gltf(
        filepath=caminho, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
        export_texcoords=True, export_normals=True, export_tangents=True, export_materials='EXPORT',
        export_image_format='NONE', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_morph=False, export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=12)
    return caminho


def gravar_relatorio(pasta, id_, relatorio):
    caminho = os.path.join(pasta, f'{id_}.relatorio.json')
    with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return caminho
