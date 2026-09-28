# Validação que bloqueia a exportação das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/
# 2026-09-26-armas-realistas-design.md, seção 4.6): as medidas-chave dentro de ±1 % do alvo da ficha (desde a 4.1c, as
# da classe da arma, medidas pelo nome — a faca tem a lâmina e a espessura dela no lugar do cano e das miras); a silhueta de lado
# ≥ 98 % com a tolerância de 1 px da foto — a máscara renderizada pela câmera ortográfica que olha o lado direito contra
# o contorno da ficha, na mesma conta de tools/regua/geometria.js (rasterizar pelo centro da célula, dilatar por disco,
# IoU bruto e com tolerância), aqui em numpy; os orçamentos de triângulos e de texturas; os soquetes, as zonas e as peças
# com os nomes certos; as peças fechadas e sem faces degeneradas; a UV sem sobreposição. Grava a sobreposição da
# silhueta (cinza = as duas, verde = falta no modelo, magenta = sobra) e a máscara para a conferência.
import math
import os

import bmesh
import bpy
import numpy as np

from . import lod
from .unidades import S

MM_POR_PX = 0.5   # resolução da máscara de lado
MARGEM_MM = 20.0  # folga em volta do contorno da ficha


def rasterizar(aneis, x0, y1, passo, largura, altura):
    """Máscara (bool, linha 0 em cima) de um contorno com buracos: o centro da célula decide, pela paridade."""
    mascara = np.zeros((altura, largura), bool)
    for j in range(altura):
        y = y1 - (j + 0.5) * passo
        cruz = []
        for anel in aneis:
            n = len(anel)
            for k in range(n):
                ax, ay = anel[k]
                bx, by = anel[(k + 1) % n]
                if (ay > y) != (by > y):
                    cruz.append(ax + (y - ay) / (by - ay) * (bx - ax))
        cruz.sort()
        for k in range(0, len(cruz) - 1, 2):
            i0 = max(0, math.ceil((cruz[k] - x0) / passo - 0.5))
            i1 = min(largura - 1, math.floor((cruz[k + 1] - x0) / passo - 0.5))
            if i1 >= i0:
                mascara[j, i0:i1 + 1] = True
    return mascara


def dilatar(m, r):
    """Dilatação por um disco de raio r pixels."""
    if r <= 0:
        return m.copy()
    out = np.zeros_like(m)
    h, w = m.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            ys0, ys1 = max(0, -dy), min(h, h - dy)
            xs0, xs1 = max(0, -dx), min(w, w - dx)
            out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] |= m[ys0:ys1, xs0:xs1]
    return out


def iou(a, b, r=0):
    """IoU bruto e com tolerância r (a diferença a até r pixels da outra máscara não conta)."""
    da, db = (dilatar(a, r), dilatar(b, r)) if r > 0 else (a, b)
    inter = int((a & b).sum())
    so_a = a & ~b
    so_b = b & ~a
    conta = int((so_a & ~db).sum() + (so_b & ~da).sum())
    return {
        'iouBruto': inter / max(1, inter + int(so_a.sum()) + int(so_b.sum())),
        'iouTolerancia': inter / max(1, inter + conta),
    }


def _mascara_render(objetos, x0, y0, x1, y1, pasta):
    """Máscara (bool, linha 0 em cima) dos objetos vistos do lado direito, na área (mm) pedida, a MM_POR_PX."""
    sc = bpy.context.scene
    largura = int(round((x1 - x0) / MM_POR_PX))
    altura = int(round((y1 - y0) / MM_POR_PX))
    cam_d = bpy.data.cameras.new('camera_mascara')
    cam_d.type = 'ORTHO'
    cam_d.ortho_scale = (x1 - x0) * S
    cam_d.clip_start = 0.01
    cam_d.clip_end = 10.0
    cam = bpy.data.objects.new('camera_mascara', cam_d)
    sc.collection.objects.link(cam)
    cam.location = ((x0 + x1) / 2 * S, -3.0, (y0 + y1) / 2 * S)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)  # olha para +Y: o lado direito da arma, com a boca à direita
    escondidos = [o for o in sc.objects if o.type in {'MESH', 'CURVE', 'FONT'} and o not in objetos and not o.hide_render]
    for o in escondidos:
        o.hide_render = True
    antes = (sc.render.engine, sc.camera, sc.render.film_transparent, sc.render.resolution_x, sc.render.resolution_y,
             sc.render.resolution_percentage, sc.display.render_aa, sc.render.filepath)
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'FLAT'
    sc.display.shading.color_type = 'SINGLE'
    sc.display.shading.single_color = (1, 1, 1)
    sc.display.render_aa = 'OFF'
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = largura, altura, 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.camera = cam
    caminho = os.path.join(pasta, 'mascara_lado.png')
    sc.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(caminho, check_existing=False)
    px = np.empty(largura * altura * 4, np.float32)
    img.pixels.foreach_get(px)
    alfa = px.reshape(altura, largura, 4)[::-1, :, 3] > 0.5
    bpy.data.images.remove(img)
    (sc.render.engine, sc.camera, sc.render.film_transparent, sc.render.resolution_x, sc.render.resolution_y,
     sc.render.resolution_percentage, sc.display.render_aa, sc.render.filepath) = antes
    for o in escondidos:
        o.hide_render = False
    bpy.data.objects.remove(cam)
    bpy.data.cameras.remove(cam_d)
    return alfa


def foto_do_contorno(ficha):
    """A foto que dá o contorno (Fase 4.1c, D2): a marcada com `contorno: true`, de qualquer lado; sem marca, a do lado
    direito (a ficha da AK). É a mesma regra de src/weapons/model/ficha.js (fotoDoContorno)."""
    fotos = ficha['fotos']
    return next((f for f in fotos if f.get('contorno') is True), None) or next(f for f in fotos if f['lado'] == 'direito')


def silhueta(objetos, ficha, pasta):
    """IoU da silhueta de lado (render × contorno da ficha), com a tolerância de 1 px da foto; grava a sobreposição."""
    os.makedirs(pasta, exist_ok=True)
    xs = [p[0] for p in ficha['contorno']]
    ys = [p[1] for p in ficha['contorno']]
    x0, x1 = min(xs) - MARGEM_MM, max(xs) + MARGEM_MM
    y0, y1 = min(ys) - MARGEM_MM, max(ys) + MARGEM_MM
    modelo = _mascara_render(objetos, x0, y0, x1, y1, pasta)
    altura, largura = modelo.shape
    foto = rasterizar([ficha['contorno'], *ficha.get('buracos', [])], x0, y1, MM_POR_PX, largura, altura)
    mm_px_foto = foto_do_contorno(ficha)['mmPorPixel']
    r = max(1, round(mm_px_foto / MM_POR_PX))
    res = iou(modelo, foto, r)
    rgba = np.zeros((altura, largura, 4), np.float32)
    rgba[..., 3] = 1.0
    rgba[modelo & foto] = (0.55, 0.55, 0.55, 1.0)
    rgba[foto & ~modelo] = (0.1, 0.85, 0.2, 1.0)
    rgba[modelo & ~foto] = (0.9, 0.1, 0.8, 1.0)
    img = bpy.data.images.new('sobreposicao', largura, altura, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    img.filepath_raw = os.path.join(pasta, 'sobreposicao.png')
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    return {'silhueta': {'iouBruto': round(res['iouBruto'], 5), 'iouTolerancia': round(res['iouTolerancia'], 5),
                         'raioToleranciaPx': r, 'mmPorPx': MM_POR_PX}}


def _peca(ob):
    """A peça de um objeto: a propriedade (peças separadas) ou o fim do nome `<nivel>_<peca>` (peças juntadas)."""
    return ob.get('peca') or ob.name.split('_', 1)[-1]


def _extremos(objetos):
    """Mínimo e máximo (mm, no referencial do Blender) dos vértices avaliados dos objetos."""
    dg = bpy.context.evaluated_depsgraph_get()
    lo = np.full(3, np.inf)
    hi = np.full(3, -np.inf)
    for ob in objetos:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        mw = np.array(ob.matrix_world)
        w = co @ mw[:3, :3].T + mw[:3, 3]
        lo = np.minimum(lo, w.min(0))
        hi = np.maximum(hi, w.max(0))
        ev.to_mesh_clear()
    return lo / S, hi / S


def _nome(ob):
    """O nome da peça sem o sufixo de cópia do Blender (`cano.001` → `cano`)."""
    return ob.name.split('.')[0]


# As medidas-chave por nome (desenho geral, seção 3.4; Fase 4.1c, D3 — as da classe vêm do contexto, `ctx['medidas']`).
# Cada uma recebe o perto (peças juntadas), as peças de jogo separadas (pelo nome) e os soquetes.
def _comprimento(perto, _pecas, _soq):
    lo, hi = _extremos(perto)
    return hi[0] - lo[0]


def _cano(_perto, pecas, _soq):
    lo, hi = _extremos([o for o in pecas if _nome(o) == 'cano'])
    return hi[0] - lo[0]


def _raio_de_mira(_perto, _pecas, soq):
    return abs(soq['mira_tras'][0] - soq['mira_frente'][0])


def _altura_sem_carregador(perto, _pecas, _soq):
    lo, hi = _extremos([o for o in perto if _peca(o) != 'carregador'])
    return hi[2] - lo[2]


def _altura_com_carregador(perto, _pecas, _soq):
    lo, hi = _extremos(perto)
    return hi[2] - lo[2]


def _lamina(perto, pecas, _soq):
    """Da face da frente da guarda à ponta da lâmina, ao longo do X (a faca)."""
    _lo, hi = _extremos(perto)
    _lo_g, hi_g = _extremos([o for o in pecas if _nome(o) == 'guarda'])
    return hi[0] - hi_g[0]


def _espessura_lamina(_perto, pecas, _soq):
    """A maior espessura da lâmina, de lado a lado (o Y do Blender)."""
    lo, hi = _extremos([o for o in pecas if _nome(o) == 'lamina'])
    return hi[1] - lo[1]


MEDIDAS = {
    'comprimento': _comprimento, 'cano': _cano, 'raioDeMira': _raio_de_mira,
    'alturaSemCarregador': _altura_sem_carregador, 'alturaComCarregador': _altura_com_carregador,
    'lamina': _lamina, 'espessuraLamina': _espessura_lamina,
}
MEDIDAS_DE_FOGO = ('comprimento', 'cano', 'raioDeMira', 'alturaSemCarregador', 'alturaComCarregador')


def medidas(perto, pecas, soquetes_def, ficha, nomes=MEDIDAS_DE_FOGO):
    """As medidas-chave `nomes` (mm) com o alvo da ficha e o erro relativo."""
    soq = {nome: xy for nome, xy, _lado, _rot in soquetes_def}
    saida = {}
    for nome in nomes:
        if nome not in MEDIDAS:
            raise ValueError(f'medida desconhecida: {nome} (tem: {", ".join(MEDIDAS)})')
        mm = float(MEDIDAS[nome](perto, pecas, soq))
        alvo = ficha['medidas'][nome]['mm']
        saida[nome] = {'mm': round(mm, 2), 'alvo': alvo, 'erro': round((mm - alvo) / alvo, 5)}
    return saida


def malha(objetos):
    """Peças fechadas (arestas que não são de exatamente duas faces) e sem faces degeneradas, com os modificadores."""
    dg = bpy.context.evaluated_depsgraph_get()
    abertas = 0
    degeneradas = 0
    nomes = []
    for ob in objetos:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        a = sum(1 for e in bm.edges if not e.is_manifold)
        d = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
        bm.free()
        ev.to_mesh_clear()
        abertas += a
        degeneradas += d
        if a or d:
            nomes.append(ob.name)
    return {'bordasAbertas': abertas, 'facesDegeneradas': degeneradas, 'pecasComProblema': nomes[:20]}


def relatorio_e_problemas(ctx, ficha, lods, soquetes_def, soquetes_nomes, pecas_jogo, lados, uv, densidade, pasta):
    """Tudo o que a seção 4.6 pede, num dicionário do relatório e na lista de problemas (vazia = aprovado)."""
    perto = [o for k, o in lods['perto'].items() if not k.startswith('_')]
    rel = {}
    rel.update(silhueta(perto, ficha, pasta))
    rel['medidas'] = medidas(perto, pecas_jogo, soquetes_def, ficha, ctx.get('medidas', MEDIDAS_DE_FOGO))
    rel['malha'] = malha(pecas_jogo)
    rel['malha']['facesNaoTrianguladas'] = sum(1 for o in perto for f in o.data.polygons if f.loop_total > 3)
    rel['lods'] = {nome: {'triangulos': lod.triangulos([o for k, o in partes.items() if not k.startswith('_')])}
                   for nome, partes in lods.items()}
    rel['uv'] = {'sobreposicao': uv, 'densidadeTexel': densidade}
    rel['soquetes'] = sorted(soquetes_nomes)
    rel['pecas'] = ['base', *ctx['pecas']]
    rel['zonas'] = list(ctx['zonas'])
    orc = ctx['orcamento']
    p = []
    if rel['silhueta']['iouTolerancia'] < 0.98:
        p.append(f"silhueta {rel['silhueta']['iouTolerancia']:.4f} com tolerância (mínimo 0,98)")
    for nome, d in rel['medidas'].items():
        if abs(d['erro']) > 0.01:
            p.append(f"medida {nome}: {d['mm']} mm contra {d['alvo']} mm ({d['erro'] * 100:+.2f} %)")
    if rel['malha']['bordasAbertas'] or rel['malha']['facesDegeneradas']:
        p.append(f"malha: {rel['malha']['bordasAbertas']} arestas abertas, {rel['malha']['facesDegeneradas']} faces degeneradas "
                 f"({', '.join(rel['malha']['pecasComProblema'])})")
    if rel['malha']['facesNaoTrianguladas']:
        p.append(f"perto: {rel['malha']['facesNaoTrianguladas']} faces com mais de três lados (o .glb sairia sem tangentes)")
    if uv:
        p.append(f'UV: {uv} texels sobrepostos (grade de conferência de 1024)')
    for nome, d in rel['lods'].items():
        if d['triangulos'] > orc['triangulos'][nome]:
            p.append(f"{nome}: {d['triangulos']} triângulos (orçamento {orc['triangulos'][nome]})")
    for nome, partes in lods.items():
        tem = {k for k in partes if not k.startswith('_')}
        for pc in rel['pecas']:
            if pc not in tem:
                p.append(f'{nome}: falta a peça {pc}')
    for s in ctx['soquetes']:
        if s not in soquetes_nomes:
            p.append(f'falta o soquete {s}')
    usadas = {slot.material.name for o in perto for slot in o.material_slots if slot.material}
    for z in ctx['zonas']:
        if z not in usadas:
            p.append(f'falta a zona {z}')
    for z in sorted(usadas - set(ctx['zonas'])):
        p.append(f'material fora das zonas: {z}')
    for nome, (lado, esperado) in lados.items():
        if lado != esperado:
            p.append(f'{nome}: textura de {lado} px (esperava {esperado})')
    return rel, p
