# A forma canônica das malhas das armas (Fase 4.1c; a construção determinística, pedida pelo usuário na Tarefa 10 do
# plano da 4.1c): o booleano exato e os chanfros do Blender devolvem, a cada execução, os mesmos polígonos nas mesmas
# posições, mas em ordens diferentes — a dos vértices, a dos polígonos e o vértice de partida de cada polígono — e com
# um ruído de posição de até 0,12 µm. A triangulação BEAUTY, a dizimação e o desdobrar das UVs desempatam pela ordem:
# o perto da M4A4 mudava até 0,094 mm entre duas construções (a outra diagonal nos quadriláteros tortos), e a pega das
# luvas, que acha a pose por buscas sensíveis a décimos de milímetro, passava numa construção e não na outra. Aqui a
# malha é refeita na forma canônica: as posições na grade de GRADE_MM, os vértices na ordem lexicográfica delas, cada
# polígono começando no menor vértice (com a mesma orientação) e os polígonos na ordem lexicográfica dos vértices; os
# atributos de ponto, de aresta, de face e de canto (as UVs) passam junto, e as normais personalizadas, pelo valor de
# cada canto. As 68 peças da M4A4 (os modificadores aplicados) saíram idênticas em três construções seguidas, e os três
# níveis (o perto, o mundo dizimado e o longe) com as mesmas posições, polígonos e UVs. As normais personalizadas ainda
# vêm da pilha do Blender (o chanfro, a solda e as normais ponderadas, avaliados na ordem de cada execução) e mudam em
# menos de 0,5 % dos cantos — mais de 0,1° em menos de 0,1 %, todos em microfaces de chanfro (até 0,5 mm²): recalculadas
# depois de canonizar, sem as do chanfro, saíam iguais em toda execução, mas com os leques dos chanfros perdidos (até
# 124° de diferença no sombreado).
import numpy as np

from .unidades import S

GRADE_MM = 1e-3  # 1 µm: acima do ruído do booleano (0,12 µm) e abaixo do menor vão entre vértices distintos de uma peça
#                  (5,9 µm, no guarda-mão da M4A4)
# os atributos da topologia (refeita), as normais personalizadas (pelo valor de cada canto) e o estado de seleção e de
# esconder (da interface do Blender), que não passam como atributos
_FORA = {'position', '.edge_verts', '.corner_vert', '.corner_edge', 'custom_normal', '.uv_select_vert', '.uv_select_edge',
         '.uv_select_face', '.select_vert', '.select_edge', '.select_poly', '.hide_vert', '.hide_edge', '.hide_poly'}
# o campo, o número de componentes e o tipo numpy de cada tipo de atributo (foreach_get e foreach_set)
_CAMPOS = {'FLOAT': ('value', 1, np.float32), 'INT': ('value', 1, np.int32), 'BOOLEAN': ('value', 1, bool),
           'INT8': ('value', 1, np.int32), 'FLOAT_VECTOR': ('vector', 3, np.float32), 'FLOAT2': ('vector', 2, np.float32),
           'FLOAT_COLOR': ('color', 4, np.float32), 'BYTE_COLOR': ('color', 4, np.float32),
           'INT16_2D': ('value', 2, np.int32), 'INT32_2D': ('value', 2, np.int32), 'QUATERNION': ('value', 4, np.float32)}


def _ler(colecao, campo, n, tipo):
    valores = np.empty(len(colecao) * n, tipo)
    colecao.foreach_get(campo, valores)
    return valores.reshape(len(colecao), n) if n > 1 else valores


def canonizar(me):
    """Refaz a malha `me` na forma canônica (ver o cabeçalho), no mesmo bloco de dados (os materiais ficam). Devolve
    `me`. Uma aresta solta (fora de todo polígono) não teria de onde voltar: a malha que tiver uma é recusada."""
    n, nf, nl = len(me.vertices), len(me.polygons), len(me.loops)
    pos = _ler(me.vertices, 'co', 3, np.float32).astype(np.float64)
    inicio = _ler(me.polygons, 'loop_start', 1, np.int32).astype(np.int64)
    total = _ler(me.polygons, 'loop_total', 1, np.int32).astype(np.int64)
    canto_v = _ler(me.loops, 'vertex_index', 1, np.int32).astype(np.int64)
    arestas = _ler(me.edges, 'vertices', 2, np.int32).astype(np.int64)
    normais = _ler(me.corner_normals, 'vector', 3, np.float32) if me.has_custom_normals else None
    atributos = [(a.name, a.domain, a.data_type, _ler(a.data, *_CAMPOS[a.data_type])) for a in me.attributes
                 if a.name not in _FORA]
    uv_ativa = me.uv_layers.active.name if me.uv_layers.active else None
    uv_render = [uv.name for uv in me.uv_layers if uv.active_render]
    # os vértices: a grade, depois a posição exata e a ordem de antes (só para pontos repetidos, idênticos)
    chave = np.round(pos / (GRADE_MM * S)).astype(np.int64)
    ordem_v = np.lexsort((pos[:, 2], pos[:, 1], pos[:, 0], chave[:, 2], chave[:, 1], chave[:, 0]))
    novo = np.empty(n, np.int64)
    novo[ordem_v] = np.arange(n)
    # os polígonos: cada um começando no menor vértice (a orientação fica), em ordem lexicográfica
    faces = []
    for f in range(nf):
        s, t = int(inicio[f]), int(total[f])
        vs = novo[canto_v[s:s + t]]
        j = int(np.argmin(vs))
        cantos = list(range(s + j, s + t)) + list(range(s, s + j))
        faces.append((tuple(int(v) for v in novo[canto_v[cantos]]), cantos, f))
    faces.sort(key=lambda c: c[0])
    cantos = np.array([c for _vs, cs, _f in faces for c in cs], np.int64)
    ordem_f = np.array([f for _vs, _cs, f in faces], np.int64)
    me.clear_geometry()
    me.vertices.add(n)
    me.vertices.foreach_set('co', (chave[ordem_v] * (GRADE_MM * S)).astype(np.float32).ravel())
    me.loops.add(nl)
    me.loops.foreach_set('vertex_index', novo[canto_v[cantos]].astype(np.int32))
    me.polygons.add(nf)
    me.polygons.foreach_set('loop_start', np.cumsum([0] + [len(vs) for vs, _cs, _f in faces[:-1]]).astype(np.int32))
    me.update(calc_edges=True)
    novas = _ler(me.edges, 'vertices', 2, np.int32).astype(np.int64)
    if len(novas) != len(arestas):
        raise ValueError(f'canonizar {me.name}: {len(arestas)} arestas antes, {len(novas)} depois (aresta solta?)')
    linha = {(min(a, b), max(a, b)): i for i, (a, b) in enumerate(novo[arestas])}
    ordem_e = np.array([linha[(min(a, b), max(a, b))] for a, b in novas], np.int64)
    por_dominio = {'POINT': ordem_v, 'EDGE': ordem_e, 'FACE': ordem_f, 'CORNER': cantos}
    for nome, dominio, tipo, valores in atributos:
        campo, _n, _t = _CAMPOS[tipo]
        a = me.attributes.get(nome) or me.attributes.new(nome, tipo, dominio)
        a.data.foreach_set(campo, valores[por_dominio[dominio]].ravel())
    if uv_ativa:
        me.uv_layers.active = me.uv_layers[uv_ativa]
    for uv in me.uv_layers:
        uv.active_render = uv.name in uv_render
    if normais is not None:
        me.normals_split_custom_set(normais[cantos])
    return me
