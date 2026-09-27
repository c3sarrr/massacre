# Assar do modelo alto para o de jogo (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
# seções 4.3 e 4.4; plano da 4.1a, D3): UV automático por peça com um empacotamento só (a mesma textura para a arma
# inteira), conferência de densidade de texel e de sobreposição, e o assar no Cycles na GPU — normal em espaço tangente
# (convenção OpenGL), sombra de contato com todas as peças juntas, e os canais dos materiais de fábrica por emissão
# (canal_aspereza, canal_borda, canal_cor). Empacota `_n` (RGB) e `_m` (R sombra, G aspereza, B borda, A cor) e grava em
# WebP sem perdas (qualidade 100 no Blender = VP8L).
import math

import bmesh
import bpy
import numpy as np

from . import estudio
from .unidades import S


def selecionar(objetos, ativo=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objetos:
        o.select_set(True)
    bpy.context.view_layer.objects.active = ativo or objetos[0]


def _empacotar(objetos, lado_px, margem_px):
    """Um empacotamento só para todas as peças, com a margem exata em fração da textura."""
    selecionar(objetos)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margem_px / lado_px)
    bpy.ops.object.mode_set(mode='OBJECT')


def uv_automatico(objetos, lado_px, margem_px=8, tentativas=4):
    """Projeção por ângulo em cada peça e um empacotamento só para todas (margem em pixels do lado da textura). A
    projeção às vezes junta numa ilha faces viradas para o mesmo lado em alturas diferentes (na AK, o fundo do vão do
    transportador, o degrau do receptor e o alto dele), que caem umas sobre as outras na UV, e o empacotamento às vezes
    encosta duas ilhas: depois dele, a face que cair sobre outra vira uma ilha própria, projetada no plano dela na escala
    da arma, e tudo é empacotado de novo, até não sobrar nenhuma. (Baixar o limite para 45° também tirava as dobras, mas
    as ilhas a mais, cada uma com a sua margem, custavam 17 % da densidade de texel.)"""
    selecionar(objetos)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=margem_px / lado_px, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    _empacotar(objetos, lado_px, margem_px)
    for _ in range(tentativas):
        marcadas = _faces_sobrepostas(objetos)
        if not marcadas:
            return
        _cada_uma_no_seu_plano(objetos, marcadas)
        _empacotar(objetos, lado_px, margem_px)


def _triangulo_na_grade(uv, tri, grade):
    """Texels (da grade de conferência) cobertos pelo triângulo: (y0, x0, máscara) ou None."""
    p = np.array([[uv[i].uv.x * grade, uv[i].uv.y * grade] for i in tri.loops])
    x0, y0 = np.floor(p.min(0)).astype(int)
    x1, y1 = np.ceil(p.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(grade, x1), min(grade, y1)
    if x1 <= x0 or y1 <= y0:
        return None
    xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    (ax, ay), (bx, by), (cx, cy) = p
    d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(d) < 1e-12:
        return None
    l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / d
    l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / d
    return y0, x0, (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)


def _faces_sobrepostas(objetos, grade=1024):
    """{nome da peça: índices das faces} que cobrem um texel coberto por outra face — a mesma conta da
    `sobreposicao_uv` (dois triângulos da mesma face não contam)."""
    dono = np.full((grade, grade), -1, np.int64)
    faces = []
    marcadas = set()
    for oi, ob in enumerate(objetos):
        me = ob.data
        uv = me.uv_layers.active.data
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
            r = _triangulo_na_grade(uv, tri, grade)
            if r is None:
                continue
            y0, x0, dentro = r
            chave = (oi, tri.polygon_index)
            if not faces or faces[-1] != chave:
                faces.append(chave)
            k = len(faces) - 1
            bloco = dono[y0:y0 + dentro.shape[0], x0:x0 + dentro.shape[1]]
            outros = np.unique(bloco[dentro & (bloco >= 0) & (bloco != k)])
            if outros.size:
                marcadas.add(k)
                marcadas.update(int(o) for o in outros)
            bloco[dentro & (bloco < 0)] = k
    res = {}
    for k in marcadas:
        oi, pi = faces[k]
        res.setdefault(objetos[oi].name, set()).add(pi)
    return res


def _cada_uma_no_seu_plano(objetos, marcadas):
    """Cada face marcada vira uma ilha própria, projetada no plano dela com a escala de UV por mm da arma inteira (a
    densidade de texel continua a mesma quando o empacotamento seguinte escala tudo junto)."""
    area_uv = area_3d = 0.0
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        for p in me.polygons:
            pts = [uv[i].uv for i in p.loop_indices]
            area_uv += abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
            area_3d += p.area
    k = math.sqrt(area_uv / area_3d)
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        for pi in marcadas.get(ob.name, ()):
            p = me.polygons[pi]
            cos = [me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
            eu = (cos[1] - cos[0]).normalized()
            ev = p.normal.cross(eu).normalized()
            for li, co in zip(p.loop_indices, cos):
                d = co - cos[0]
                uv[li].uv = (d.dot(eu) * k, d.dot(ev) * k)


def densidade_texel(objetos, lado_px):
    """Pixels por mm de cada peça (raiz da área em UV × lado² sobre a área em mm²), relativos à mediana."""
    valores = {}
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        area_mm = 0.0
        area_uv = 0.0
        for p in me.polygons:
            area_mm += p.area / (S * S)
            pts = [uv[i].uv for i in p.loop_indices]
            for k in range(1, len(pts) - 1):
                a, b, c = pts[0], pts[k], pts[k + 1]
                area_uv += abs((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) / 2
        if area_mm > 0:
            valores[ob.name] = math.sqrt(area_uv * lado_px * lado_px / area_mm)
    med = float(np.median(list(valores.values())))
    rel = {k: v / med for k, v in valores.items()}
    return {'medianaPxPorMm': round(med, 3), 'minimo': round(min(rel.values()), 3), 'maximo': round(max(rel.values()), 3)}


def sobreposicao_uv(objetos, grade=1024):
    """Texels (numa grade de conferência) cobertos por dois triângulos ou mais: ilhas encavaladas ou uma dobra dentro
    da ilha (face torcida)."""
    conta = np.zeros((grade, grade), np.int32)
    for ob in objetos:
        me = ob.data
        uv = me.uv_layers.active.data
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
            p = np.array([[uv[i].uv.x * grade, uv[i].uv.y * grade] for i in tri.loops])
            x0, y0 = np.floor(p.min(0)).astype(int)
            x1, y1 = np.ceil(p.max(0)).astype(int)
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(grade, x1), min(grade, y1)
            if x1 <= x0 or y1 <= y0:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
            (ax, ay), (bx, by), (cx, cy) = p
            d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(d) < 1e-12:
                continue
            l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / d
            l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / d
            dentro = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
            conta[y0:y1, x0:x1] += dentro
    return int((conta > 1).sum())


def _imagem(nome, lado, fundo=(0.0, 0.0, 0.0, 1.0)):
    """Imagem de ponto flutuante do assar, sem gestão de cor, com o `fundo` onde nenhuma ilha é assada: o valor neutro
    do canal, para os mipmaps de longe não puxarem as bordas das ilhas para o preto."""
    img = bpy.data.images.new(nome, lado, lado, alpha=False, float_buffer=True)
    img.generated_color = fundo
    img.colorspace_settings.name = 'Non-Color'
    return img


def _gravar_webp(pasta, nome, rgba, alfa):
    """Grava `rgba` (lado × lado × 4, de 0 a 1, na ordem de linhas do Blender) em WebP sem perdas por uma imagem de 8
    bits: a de ponto flutuante do Blender guarda o RGB multiplicado pelo alfa e divide ao gravar — o que estragava os
    canais de dados da `_m` (o alfa dela é a variação de cor, não transparência)."""
    lado = rgba.shape[0]
    img = bpy.data.images.new(nome, lado, lado, alpha=alfa, float_buffer=False)
    img.colorspace_settings.name = 'Non-Color'
    img.alpha_mode = 'STRAIGHT'
    img.pixels.foreach_set(np.clip(rgba, 0.0, 1.0).astype(np.float32).ravel())
    caminho = f'{pasta}/{nome}.webp'
    img.filepath_raw = caminho
    img.file_format = 'WEBP'
    img.save(filepath=caminho, quality=100)
    bpy.data.images.remove(img)
    return caminho


def _suavizar(canal):
    """Filtro binomial 5 × 5 (quase um gaussiano de 1 pixel): tira o ruído de amostragem da sombra de contato, que é
    larga por natureza, sem mudar a forma dela — o WebP sem perdas guarda ruído a peso de ouro."""
    k = np.array([1.0, 4.0, 6.0, 4.0, 1.0], np.float32) / 16.0
    altura, largura = canal.shape
    c = np.pad(canal, 2, mode='edge')
    c = sum(k[i] * c[:, i:i + largura] for i in range(5))
    return sum(k[i] * c[i:i + altura, :] for i in range(5))


def _juntar_copias(objetos, nome):
    """Uma cópia juntada das peças, com os modificadores aplicados (mantém as UVs e os materiais): o alvo único do assar
    (as peças de jogo) e a fonte única (o modelo alto — uma árvore de raios em vez de uma por peça)."""
    dg = bpy.context.evaluated_depsgraph_get()
    copias = []
    for ob in objetos:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        c = bpy.data.objects.new(f'{nome}.{ob.name}', me)
        c.matrix_world = ob.matrix_world.copy()
        bpy.context.scene.collection.objects.link(c)
        copias.append(c)
    selecionar(copias)
    if len(copias) > 1:
        bpy.ops.object.join()
    alvo = bpy.context.view_layer.objects.active
    alvo.name = nome
    return alvo


def _ligar_imagem(alvo, img):
    """Nó de imagem ativo em cada material do alvo (o Cycles assa no nó ativo)."""
    nos = []
    for slot in alvo.material_slots:
        nt = slot.material.node_tree
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = img
        nt.nodes.active = n
        nos.append((nt, n))
    return nos


def _emitir_canal(fontes, canal):
    """Liga o `canal` de cada material de fábrica das fontes numa emissão na saída; devolve como desfazer."""
    desfazer = []
    vistos = set()
    for ob in fontes:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in vistos:
                continue
            vistos.add(m.name)
            nt = m.node_tree
            saida = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
            antigo = saida.inputs['Surface'].links[0].from_socket if saida.inputs['Surface'].links else None
            em = nt.nodes.new('ShaderNodeEmission')
            no = nt.nodes.get(canal)
            if no is None:
                em.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1)
            else:
                nt.links.new(no.outputs[0], em.inputs['Color'])
            nt.links.new(em.outputs['Emission'], saida.inputs['Surface'])
            desfazer.append((nt, saida, antigo, em))
    return desfazer


def _desfazer(desfazer):
    for nt, saida, antigo, em in desfazer:
        if antigo is not None:
            nt.links.new(antigo, saida.inputs['Surface'])
        nt.nodes.remove(em)


def _pixels(img, lado):
    a = np.empty(lado * lado * 4, np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(lado, lado, 4)


def assar_conjunto(fontes, pecas_jogo, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16,
                   extrusao_mm=2.0):
    """Assa o conjunto de texturas de um nível: normal, sombra de contato e os três canais. Grava `_n` e `_m`. O relevo
    e os canais usam `amostras_aa` por pixel (antisserrilhado: o detalhe menor que o texel vira a média dele, não ruído);
    a sombra de contato, `amostras_ao`; a sombra e a aspereza passam pelo filtro binomial e os canais de dados são
    quantizados em degraus que não aparecem."""
    sc = bpy.context.scene
    estudio.gpu()
    sc.render.bake.use_selected_to_active = True
    # Sem limpar a imagem antes: o fundo neutro de cada canal fica onde nenhuma ilha é assada (limpar zerava tudo).
    sc.render.bake.use_clear = False
    sc.render.bake.cage_extrusion = extrusao_mm * S
    sc.render.bake.max_ray_distance = extrusao_mm * 2 * S
    sc.render.bake.margin = margem_px
    sc.render.bake.margin_type = 'EXTEND'
    alvo = _juntar_copias(pecas_jogo, f'alvo_{nome_n}')
    fonte = _juntar_copias(fontes, f'fonte_{nome_n}')
    for vis in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission', 'visible_volume_scatter'):
        setattr(alvo, vis, False)
    # Só a cópia do modelo alto faz sombra de contato: as peças (as do alto também), os LODs e o estúdio saem do assar.
    fora = [o for o in bpy.context.scene.objects if o is not fonte and o is not alvo and not o.hide_render]
    for o in fora:
        o.hide_render = True
    imgs = {}

    def assar(tipo, chave, fundo, amostras=1, canal=None):
        img = _imagem(f'{nome_n}_{chave}', lado_px, fundo=fundo)
        nos = _ligar_imagem(alvo, img)
        desfazer = _emitir_canal(fontes, canal) if canal else []
        sc.cycles.samples = amostras
        selecionar([fonte, alvo], ativo=alvo)
        if tipo == 'NORMAL':
            sc.render.bake.normal_space = 'TANGENT'
            sc.render.bake.normal_r, sc.render.bake.normal_g, sc.render.bake.normal_b = 'POS_X', 'POS_Y', 'POS_Z'
        bpy.ops.object.bake(type=tipo)
        _desfazer(desfazer)
        for nt, n in nos:
            nt.nodes.remove(n)
        imgs[chave] = img

    assar('NORMAL', 'normal', (0.5, 0.5, 1.0, 1.0), amostras_aa)
    assar('AO', 'ao', (1.0, 1.0, 1.0, 1.0), amostras_ao)
    for chave, canal, neutro in (('aspereza', 'canal_aspereza', 0.5), ('borda', 'canal_borda', 0.0), ('cor', 'canal_cor', 0.5)):
        assar('EMIT', chave, (neutro, neutro, neutro, 1.0), amostras_aa, canal)
    n = _pixels(imgs['normal'], lado_px)[..., :3]
    ao = _suavizar(_pixels(imgs['ao'], lado_px)[..., 0])
    aspereza = _suavizar(_pixels(imgs['aspereza'], lado_px)[..., 0])
    m = np.stack([ao, aspereza] + [_pixels(imgs[k], lado_px)[..., 0] for k in ('borda', 'cor')], axis=2)
    # Os canais de dados só modulam o material (no oxidado, ±16 % de aspereza e ±6 % de cor): degraus de 4/255 na
    # aspereza e na cor e de 2/255 na sombra de contato não aparecem no jogo e cortam cerca de 30 % do WebP sem perdas
    # (a `_m` da AK fica em 2,97 MB). A borda (o desgaste) fica inteira.
    for canal, passo in ((0, 2.0), (1, 4.0), (3, 4.0)):
        m[..., canal] = np.round(m[..., canal] * 255.0 / passo) * passo / 255.0
    # O WebP sem perdas pode trocar o RGB dos pixels de alfa 0: a variação de cor (o alfa) fica em 1/255 no mínimo.
    m[..., 3] = np.maximum(m[..., 3], 1.0 / 255.0)
    caminhos = {
        nome_n: _gravar_webp(pasta, nome_n, np.concatenate([n, np.ones((lado_px, lado_px, 1), np.float32)], axis=2), False),
        nome_m: _gravar_webp(pasta, nome_m, m, True),
    }
    bpy.data.objects.remove(alvo)
    bpy.data.objects.remove(fonte)
    for o in fora:
        o.hide_render = False
    for img in imgs.values():
        bpy.data.images.remove(img)
    return caminhos
