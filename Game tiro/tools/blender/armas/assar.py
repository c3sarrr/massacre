# Assar do modelo alto para o de jogo (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-realistas-design.md,
# seções 4.3 e 4.4; plano da 4.1a, D3): UV automático por peça com um empacotamento só (a mesma textura para a arma
# inteira), conferência de densidade de texel e de sobreposição, e o assar no Cycles na GPU — normal em espaço tangente
# (convenção OpenGL), sombra de contato com todas as peças juntas, e os canais dos materiais de fábrica por emissão
# (canal_aspereza, canal_borda, canal_cor). Empacota `_n` (RGB a normal, A o relevo moldado — correções da P1 da 4.1c:
# o tipo da textura do molde, 1 − 32·id/255, relevo.py) e `_m` (R sombra, G aspereza, B borda, A cor) e grava em WebP
# sem perdas (qualidade 100 no Blender = VP8L). As luvas (Fase 4.1b) desdobram pelas costuras (`uv_por_costuras`)
# e conferem a densidade por ilha de UV (`densidade_por_ilha`: são uma malha só, base e peças juntas).
import math

import bmesh
import bpy
import numpy as np

from . import canonica, estudio, gravar
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


def uv_por_costuras(objetos, lado_px, margem_px=8):
    """Desdobramento pelas costuras marcadas (Fase 4.1b: as ilhas seguem os painéis costurados da luva, e cada peça de
    reforço é as suas), pelo método de ângulos (ABF, conforme: sem cisalhar a trama do tecido e o grão do couro) e o
    empacotamento de sempre, com a margem exata."""
    for ob in objetos:
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name='UVMap')
    selecionar(objetos)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, margin_method='FRACTION',
                      margin=margem_px / lado_px)
    bpy.ops.object.mode_set(mode='OBJECT')
    _empacotar(objetos, lado_px, margem_px)


def densidade_por_ilha(ob, lado_px):
    """A densidade de texel (pixels por mm) de cada ilha de UV de uma malha — as faces ligadas por arestas que não são
    costura e em que as UV dos dois lados batem —, relativa à mediana das ilhas; e a das faces (percentis 1 e 99), que
    mostra a distorção de área dentro das ilhas."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uv = bm.loops.layers.uv.active
    bm.faces.ensure_lookup_table()
    pai = list(range(len(bm.faces)))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for e in bm.edges:
        if e.seam or len(e.link_faces) != 2:
            continue
        la, lb = e.link_loops
        # a UV de cada ponta da aresta nos dois lados (pelo vértice, qualquer que seja o sentido das faces)
        ua = {la.vert: la[uv].uv, la.link_loop_next.vert: la.link_loop_next[uv].uv}
        ub = {lb.vert: lb[uv].uv, lb.link_loop_next.vert: lb.link_loop_next[uv].uv}
        if all((ua[v] - ub[v]).length < 1e-6 for v in e.verts):
            pai[raiz(la.face.index)] = raiz(lb.face.index)
    area_mm, area_uv = {}, {}
    faces = []
    for f in bm.faces:
        pts = [l[uv].uv for l in f.loops]
        auv = abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
        amm = f.calc_area() / (S * S)
        r = raiz(f.index)
        area_mm[r] = area_mm.get(r, 0.0) + amm
        area_uv[r] = area_uv.get(r, 0.0) + auv
        if amm > 1e-9:
            faces.append(math.sqrt(auv * lado_px * lado_px / amm))
    bm.free()
    ilhas = {r: math.sqrt(area_uv[r] * lado_px * lado_px / area_mm[r]) for r in area_mm if area_mm[r] > 1e-9}
    med = float(np.median(list(ilhas.values())))
    rel = [v / med for v in ilhas.values()]
    f1, f99 = np.percentile(np.array(faces) / med, [1, 99])
    return {'ilhas': len(ilhas), 'medianaPxPorMm': round(med, 3), 'minimo': round(min(rel), 3),
            'maximo': round(max(rel), 3), 'faces1': round(float(f1), 3), 'faces99': round(float(f99), 3)}


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
    gravar.com_novas_tentativas(lambda: img.save(filepath=caminho, quality=100), caminho)
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
    """Uma cópia juntada das peças, com os modificadores aplicados (mantém as UVs e os materiais) e na forma canônica
    (canonica.avaliada: o Cycles triangula cada polígono pela ordem dos cantos; a avaliação ruim do booleano é refeita):
    o alvo único do assar (as peças de jogo) e a fonte única (o modelo alto — uma árvore de raios em vez de uma por
    peça)."""
    copias = []
    for ob in objetos:
        me = canonica.avaliada(ob)
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


def _emitir_canal(fontes, canal, neutro=0.5):
    """Liga o `canal` de cada material de fábrica das fontes numa emissão na saída (o `neutro` no material que não tem o
    canal: 1 no relevo, o liso); devolve como desfazer."""
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
                em.inputs['Color'].default_value = (neutro, neutro, neutro, 1)
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


def _desligar_finos(fontes):
    """Zera a força dos relevos `fino` dos materiais das fontes (materiais._relevo): os que a textura não guarda. Devolve
    como religar."""
    religar = []
    vistos = set()
    for ob in fontes:
        for slot in ob.material_slots:
            m = slot.material
            if m is None or m.name in vistos or not m.use_nodes:
                continue
            vistos.add(m.name)
            for no in m.node_tree.nodes:
                if no.type == 'BUMP' and no.label == 'fino':
                    religar.append((no, no.inputs['Strength'].default_value))
                    no.inputs['Strength'].default_value = 0.0
    return religar


def _pixels(img, lado):
    a = np.empty(lado * lado * 4, np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(lado, lado, 4)


def _cobertura(alvo, lado):
    """Os texels (linhas de baixo para cima, como os pixels do Blender) com o centro dentro de algum triângulo da UV."""
    cob = np.zeros((lado, lado), bool)
    me = alvo.data
    uv = me.uv_layers.active.data
    me.calc_loop_triangles()
    for tri in me.loop_triangles:
        r = _triangulo_na_grade(uv, tri, lado)
        if r is not None:
            y0, x0, dentro = r
            cob[y0:y0 + dentro.shape[0], x0:x0 + dentro.shape[1]] |= dentro
    return cob


def _estender(img, coberto, passos):
    """A margem das ilhas: cada texel fora delas, vizinho de um coberto, recebe a média dos vizinhos cobertos, `passos`
    vezes (o EXTEND do Blender, feito aqui para compor imagens assadas em grupos)."""
    img, cob = img.copy(), coberto.copy()
    for _ in range(passos):
        soma = np.zeros_like(img)
        conta = np.zeros(cob.shape, np.float32)
        cp = np.pad(cob, 1)
        ip = np.pad(img, ((1, 1), (1, 1), (0, 0)))
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                if dy == 1 and dx == 1:
                    continue
                c = cp[dy:dy + cob.shape[0], dx:dx + cob.shape[1]]
                soma += ip[dy:dy + cob.shape[0], dx:dx + cob.shape[1]] * c[..., None]
                conta += c
        novo = ~cob & (conta > 0)
        img[novo] = soma[novo] / conta[novo][:, None]
        cob |= novo
    return img


def assar_conjunto(fontes, pecas_jogo, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16,
                   extrusao_mm=2.0):
    """O conjunto de texturas de um nível de uma arma: um grupo só (as fontes para as peças de jogo, a gaiola de
    `extrusao_mm` e o raio do dobro). Ver assar_grupos."""
    return assar_grupos([(fontes, pecas_jogo, extrusao_mm, 2 * extrusao_mm)], lado_px, margem_px, pasta, nome_n, nome_m,
                        amostras_ao, amostras_aa)


def assar_grupos(grupos, lado_px, margem_px, pasta, nome_n, nome_m, amostras_ao=64, amostras_aa=16):
    """Assa o conjunto de texturas: normal, sombra de contato e os três canais, e grava `_n` e `_m`. `grupos` =
    [(fontes, alvos, extrusão da gaiola em mm, raio em mm)]: cada grupo casa os alvos (malhas de jogo) só com as fontes
    dele (o modelo alto), na sua imagem, e as imagens são compostas pela cobertura de UV de cada grupo, com a margem
    estendida depois (a margem de um grupo assada pelo Blender invadiria as ilhas do outro). A sombra de contato vê
    todas as fontes (as peças fazem sombra na base). As luvas assam a base e as peças separadas: as bordas das peças
    altas são arredondadas 1,6 mm para dentro das de jogo, e com tudo junto o raio da borda da peça atravessava e
    pegava a base embaixo (manchas tortas nos cantos). O relevo e os canais usam `amostras_aa` por pixel
    (antisserrilhado: o detalhe menor que o texel vira a média dele, não ruído); a sombra de contato, `amostras_ao`; a
    sombra e a aspereza passam pelo filtro binomial e os canais de dados são quantizados em degraus que não aparecem.
    Os relevos `fino` das fontes (o grão, a trama, o pontilhado das luvas, o relevo moldado das armas) ficam fora: com
    um período de poucos texels, viravam moiré e ruído no WebP; no jogo eles vêm do shader — o do molde pelo tipo que o
    canal `canal_relevo` grava no alfa do _n."""
    sc = bpy.context.scene
    estudio.gpu()
    sc.render.bake.use_selected_to_active = True
    # Sem limpar a imagem antes: o fundo neutro de cada canal fica onde nenhuma ilha é assada (limpar zerava tudo).
    sc.render.bake.use_clear = False
    sc.render.bake.margin = 2  # só para não sobrar texel de borda sem valor; a margem de verdade é a composta
    sc.render.bake.margin_type = 'EXTEND'
    pares = []
    for k, (fontes, alvos, extrusao_mm, raio_mm) in enumerate(grupos):
        alvo = _juntar_copias(alvos, f'alvo_{nome_n}_{k}')
        fonte = _juntar_copias(fontes, f'fonte_{nome_n}_{k}')
        for vis in ('visible_diffuse', 'visible_glossy', 'visible_shadow', 'visible_transmission',
                    'visible_volume_scatter'):
            setattr(alvo, vis, False)
        pares.append((fonte, alvo, extrusao_mm, raio_mm, _cobertura(alvo, lado_px)))
    todas_as_fontes = [f for g in grupos for f in g[0]]
    # Só as cópias do modelo alto fazem sombra de contato: os originais, os LODs e o estúdio saem do assar.
    nossos = {o for par in pares for o in par[:2]}
    fora = [o for o in sc.objects if o not in nossos and not o.hide_render]
    for o in fora:
        o.hide_render = True
    religar = _desligar_finos([par[0] for par in pares])
    coberto = np.zeros((lado_px, lado_px), bool)
    for par in pares:
        coberto |= par[4]
    arrays = {}

    def assar(tipo, chave, fundo, amostras=1, canal=None):
        desfazer = _emitir_canal(todas_as_fontes, canal, fundo[0]) if canal else []
        sc.cycles.samples = amostras
        if tipo == 'NORMAL':
            sc.render.bake.normal_space = 'TANGENT'
            sc.render.bake.normal_r, sc.render.bake.normal_g, sc.render.bake.normal_b = 'POS_X', 'POS_Y', 'POS_Z'
        final = np.empty((lado_px, lado_px, 4), np.float32)
        final[...] = fundo
        for k, (fonte, alvo, extrusao_mm, raio_mm, cob) in enumerate(pares):
            img = _imagem(f'{nome_n}_{chave}_{k}', lado_px, fundo=fundo)
            nos = _ligar_imagem(alvo, img)
            sc.render.bake.cage_extrusion = extrusao_mm * S
            sc.render.bake.max_ray_distance = raio_mm * S
            selecionar([fonte, alvo], ativo=alvo)
            bpy.ops.object.bake(type=tipo)
            for nt, n in nos:
                nt.nodes.remove(n)
            final[cob] = _pixels(img, lado_px)[cob]
            bpy.data.images.remove(img)
        _desfazer(desfazer)
        arrays[chave] = _estender(final, coberto, margem_px)

    assar('NORMAL', 'normal', (0.5, 0.5, 1.0, 1.0), amostras_aa)
    assar('AO', 'ao', (1.0, 1.0, 1.0, 1.0), amostras_ao)
    for chave, canal, neutro in (('aspereza', 'canal_aspereza', 0.5), ('borda', 'canal_borda', 0.0), ('cor', 'canal_cor', 0.5),
                                 ('relevo', 'canal_relevo', 1.0)):
        assar('EMIT', chave, (neutro, neutro, neutro, 1.0), amostras_aa, canal)
    n = arrays['normal'][..., :3]
    ao = _suavizar(arrays['ao'][..., 0])
    aspereza = _suavizar(arrays['aspereza'][..., 0])
    m = np.stack([ao, aspereza] + [arrays[k][..., 0] for k in ('borda', 'cor')], axis=2)
    # Os canais de dados só modulam o material (no oxidado, ±16 % de aspereza e ±6 % de cor): degraus de 4/255 na
    # aspereza e na cor e de 2/255 na sombra de contato não aparecem no jogo e cortam cerca de 30 % do WebP sem perdas
    # (a `_m` da AK fica em 2,97 MB). A borda (o desgaste) também em degraus de 4/255 desde a 4.1c: é a rampa larga do
    # gasto nas quinas, que o shader corta pelo desgaste da skin; inteira, os dentes dos trilhos da M4 a punham em 1,13
    # MB (a `_m` da M4 de 3,29 para 2,61 MB).
    for canal, passo in ((0, 2.0), (1, 4.0), (2, 4.0), (3, 4.0)):
        m[..., canal] = np.round(m[..., canal] * 255.0 / passo) * passo / 255.0
    # O WebP sem perdas pode trocar o RGB dos pixels de alfa 0: a variação de cor (o alfa) fica em 1/255 no mínimo.
    m[..., 3] = np.maximum(m[..., 3], 1.0 / 255.0)
    # O relevo moldado no alfa do _n: o tipo (1 − 32·id/255) nunca chega a 0, então o RGB da normal fica intacto no WebP.
    relevo = np.clip(arrays['relevo'][..., :1], 0.5, 1.0)
    caminhos = {
        nome_n: _gravar_webp(pasta, nome_n, np.concatenate([n, relevo], axis=2), True),
        nome_m: _gravar_webp(pasta, nome_m, m, True),
    }
    for no, forca in religar:
        no.inputs['Strength'].default_value = forca
    for fonte, alvo, *_ in pares:
        bpy.data.objects.remove(alvo)
        bpy.data.objects.remove(fonte)
    for o in fora:
        o.hide_render = False
    return caminhos
