"""Prévia do jogo no Blender (Fase 4.1; docs/phases/phase-4.md, seção 4.1, "Blender").

A malha que o jogo gera da receita (o SDF de verdade, uma malha por grupo no pivô), os braços de massinha nas âncoras
como no viewmodel parado e a câmera de primeira pessoa, lidos do que o tools/blender/previa.mjs gravou. Ficam numa
coleção que não exporta (cada objeto com `massacre_previa`): o `conferir` renderiza isso, e no Blender com janela o
botão "Prévia do jogo" refaz a prévia da cena editada (exporta para um temporário, valida e gera pelo jogo).
"""

import json
import os
import subprocess
import tempfile

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

from . import eixos
from .importar import material

COLECAO = 'prévia do jogo (não exporta)'


def _ler(dados, bloco, tipo):
    return np.frombuffer(dados, dtype=tipo, count=bloco['count'], offset=bloco['offset'])


def _malha(nome, dados, m, materiais):
    pos = _ler(dados, m['positions'], np.float32)
    nor = _ler(dados, m['normals'], np.float32)
    idx = _ler(dados, m['indices'], np.uint32).astype(np.int32)
    nv, nt = len(pos) // 3, len(idx) // 3
    me = bpy.data.meshes.new(nome)
    me.vertices.add(nv)
    me.vertices.foreach_set('co', pos)
    me.loops.add(nt * 3)
    me.loops.foreach_set('vertex_index', idx)
    me.polygons.add(nt)
    me.polygons.foreach_set('loop_start', np.arange(0, nt * 3, 3, dtype=np.int32))
    for mat in materiais:
        me.materials.append(mat)
    if 'massas' in m:
        me.polygons.foreach_set('material_index', _ler(dados, m['massas'], np.uint8).astype(np.int32))
    me.update(calc_edges=True)
    me.shade_smooth()
    me.normals_split_custom_set_from_vertices(nor.reshape(-1, 3))  # as normais do jogo (gradiente do SDF)
    return me


def remover():
    """Tira a prévia anterior (objetos, malhas e a coleção)."""
    col = bpy.data.collections.get(COLECAO)
    malhas = []
    for o in [o for o in bpy.data.objects if 'massacre_previa' in o]:
        if o.type == 'MESH':
            malhas.append(o.data)
        dados_cam = o.data if o.type == 'CAMERA' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if dados_cam and dados_cam.users == 0:
            bpy.data.cameras.remove(dados_cam)
    for me in malhas:
        if me.users == 0:
            bpy.data.meshes.remove(me)
    if col:
        bpy.data.collections.remove(col)


def carregar(caminho_json, visivel=True):
    """Monta a prévia gravada pelo previa.mjs. Devolve a coleção."""
    remover()
    with open(caminho_json, encoding='utf-8') as f:
        cab = json.load(f)
    with open(os.path.join(os.path.dirname(caminho_json), cab['bin']), 'rb') as f:
        dados = f.read()
    col = bpy.data.collections.new(COLECAO)
    bpy.context.scene.collection.children.link(col)
    mats = [bpy.data.materials.get(f'massa:{slot}') or material(f'massa:{slot}', '#8F959C') for slot in cab['materiais']]
    for g in cab['grupos']:
        o = bpy.data.objects.new(f"jogo:{g['nome']}", _malha(f"jogo:{g['nome']}", dados, g, mats))
        col.objects.link(o)
        o.matrix_world = eixos.matriz_blender(g['pivo'])
        o['massacre_previa'] = 'arma'
    mao = bpy.data.materials.get('massa:mao') or material('massa:mao', cab['corMao'])
    for m in cab['maos']:
        o = bpy.data.objects.new(f"jogo:braco-{m['lado']}", _malha(f"jogo:braco-{m['lado']}", dados, m, [mao]))
        col.objects.link(o)
        o.matrix_world = eixos.C.copy()
        o['massacre_previa'] = 'mao'
    c = cab['camera']
    cam_dados = bpy.data.cameras.new('jogo:primeira-pessoa')
    cam_dados.sensor_fit = 'VERTICAL'
    cam_dados.angle_y = np.radians(c['fovY'])
    cam_dados.clip_start = c['near']
    cam_dados.clip_end = c['far']
    cam = bpy.data.objects.new('jogo:primeira-pessoa', cam_dados)
    col.objects.link(cam)
    x, y, z, w = c['quat']
    cam.matrix_world = eixos.C @ Matrix.Translation(Vector(c['pos'])) @ Quaternion((w, x, y, z)).to_matrix().to_4x4()
    cam['massacre_previa'] = 'camera'
    for o in col.objects:
        o.hide_select = True
    camada = bpy.context.view_layer.layer_collection.children.get(COLECAO)
    if camada:
        camada.hide_viewport = not visivel
    return col


def atualizar(contexto, receita_js, visivel=True):
    """Refaz a prévia a partir de uma receita já validada (a do disco ou a cena exportada para um temporário): o jogo
    gera a malha num temporário e a prévia entra no lugar da anterior."""
    pasta = os.path.join(tempfile.gettempdir(), 'massacre-blender')
    os.makedirs(pasta, exist_ok=True)
    saida = os.path.join(pasta, os.path.splitext(os.path.basename(receita_js))[0] + '-previa-cena')
    res = subprocess.run(
        [contexto['node'], contexto['ferramenta'], 'previa', receita_js, saida],
        capture_output=True, text=True, encoding='utf-8', cwd=contexto['raiz'],
    )
    if res.returncode != 0:
        raise RuntimeError('o jogo não gerou a prévia:\n' + (res.stdout + res.stderr).strip())
    try:
        return carregar(saida + '.json', visivel)
    finally:
        for ext in ('.json', '.bin'):
            if os.path.exists(saida + ext):
                os.remove(saida + ext)
