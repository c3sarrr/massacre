"""Conferir: renderiza as vistas da arma (Workbench, sem janela) — Fase 4.1; docs/phases/phase-4.md, seção 4.1,
"Blender". Fundo creme de papel, cor pelas massas, contorno fino.

O render mostra a prévia do jogo (previa.py): a malha que o jogo gera da receita, com costuras, cortes e bordas
arredondadas do SDF, não as peças de edição. As vistas da arma saem sem as mãos — a lateral com a planta de referência
por cima, de cima, de frente e 3/4, em câmera ortográfica enquadrando a arma —; depois os braços de massinha nas âncoras
(3/4) e a primeira pessoa (a câmera do viewmodel com o viewmodel_fov e os offsets padrão). A cena volta como estava.
"""

import os

import bpy
from mathutils import Matrix, Vector

from . import eixos
from .importar import rgba

# (nome, direção de onde a câmera olha no referencial do jogo, "para cima" no do Blender, com a planta, com as mãos)
VISTAS = (
    ('lado', (0.0, 0.0, 1.0), (0.0, 0.0, 1.0), True, False),
    ('cima', (0.0, 1.0, 0.0), (0.0, 1.0, 0.0), False, False),
    ('frente', (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), False, False),
    ('tres-quartos', (0.62, 0.42, 0.66), (0.0, 0.0, 1.0), False, False),
    ('maos', (0.62, 0.42, 0.66), (0.0, 0.0, 1.0), False, True),
)
PRIMEIRA_PESSOA = 'primeira-pessoa'
RESOLUCAO = (1600, 900)
FUNDO = '#F1E8D4'


def _caixa_mundo(objs):
    lo = Vector((float('inf'),) * 3)
    hi = Vector((float('-inf'),) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def _preparar_cena(cena):
    cena.render.engine = 'BLENDER_WORKBENCH'
    cena.render.resolution_x, cena.render.resolution_y = RESOLUCAO
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = 'PNG'
    cena.render.film_transparent = False
    sh = cena.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_object_outline = True
    sh.object_outline_color = (0.12, 0.1, 0.09)
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    if cena.world is None:
        cena.world = bpy.data.worlds.new('papel')
    cena.world.color = rgba(FUNDO)[:3]
    cena.view_settings.view_transform = 'Standard'


def _enquadrar(cam, cam_dados, lo, hi, olhar_jogo, cima):
    """Câmera ortográfica olhando de `olhar_jogo` para o centro da caixa, com a caixa inteira no quadro."""
    centro = (lo + hi) / 2
    raio = (hi - lo).length / 2 + 1.0
    d = eixos.ponto_blender(olhar_jogo).normalized()
    cam.matrix_world = Matrix.Translation(centro + d * (raio * 3)) @ _base_olhando(-d, Vector(cima))
    inv = cam.matrix_world.inverted()
    pts = [inv @ Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    largura = max(p.x for p in pts) - min(p.x for p in pts)
    altura = max(p.y for p in pts) - min(p.y for p in pts)
    cam_dados.ortho_scale = max(largura, altura * RESOLUCAO[0] / RESOLUCAO[1]) * 1.12
    cam_dados.clip_start = 0.1
    cam_dados.clip_end = raio * 8
    return d


def conferir(pasta):
    """Renderiza as vistas da prévia do jogo em `pasta` e devolve os caminhos dos PNGs."""
    cena = bpy.context.scene
    bpy.context.view_layer.update()
    arma = [o for o in bpy.data.objects if o.get('massacre_previa') == 'arma']
    if not arma:
        raise RuntimeError('sem a prévia do jogo: gere a prévia antes de conferir')
    maos = [o for o in bpy.data.objects if o.get('massacre_previa') == 'mao']
    olho = next((o for o in bpy.data.objects if o.get('massacre_previa') == 'camera'), None)
    edicao = [o for o in bpy.data.objects if 'massacre_parte' in o or 'massacre_proxy' in o]
    planta = next((o for o in bpy.data.objects if 'massacre_planta' in o), None)
    todos = [*arma, *maos, *edicao, *([planta] if planta else [])]
    estado = {o.name: o.hide_render for o in todos}
    matriz_planta = planta.matrix_world.copy() if planta else None
    camera_antes = cena.camera
    _preparar_cena(cena)
    cam_dados = bpy.data.cameras.new('conferencia')
    cam_dados.type = 'ORTHO'
    cam = bpy.data.objects.new('conferencia', cam_dados)
    cena.collection.objects.link(cam)
    os.makedirs(pasta, exist_ok=True)
    arquivos = []

    def render(nome):
        cena.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(cena.render.filepath)

    try:
        for o in edicao:
            o.hide_render = True
        for o in arma:
            o.hide_render = False
        lo_arma, hi_arma = _caixa_mundo(arma)
        lo_tudo, hi_tudo = _caixa_mundo([*arma, *maos])
        cena.camera = cam
        for nome, olhar_jogo, cima, com_planta, com_maos in VISTAS:
            if com_maos and not maos:
                continue
            for o in maos:
                o.hide_render = not com_maos
            lo, hi = (lo_tudo, hi_tudo) if com_maos else (lo_arma, hi_arma)
            d = _enquadrar(cam, cam_dados, lo, hi, olhar_jogo, cima)
            if planta:
                # A planta só na lateral, puxada para a frente da arma (a projeção ortográfica não muda).
                planta.hide_render = not com_planta
                planta.matrix_world = Matrix.Translation(d * (hi.y - lo.y)) @ matriz_planta
            render(nome)
        if olho and maos:
            for o in maos:
                o.hide_render = False
            if planta:
                planta.hide_render = True
            cena.camera = olho
            render(PRIMEIRA_PESSOA)
    finally:
        for o in todos:
            o.hide_render = estado[o.name]
        if planta:
            planta.matrix_world = matriz_planta
        cena.camera = camera_antes
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_dados)
    return arquivos


def _base_olhando(frente, cima):
    """Rotação de câmera (−Z para `frente`, +Y o mais perto de `cima`)."""
    z = -frente.normalized()
    x = cima.cross(z)
    if x.length < 1e-6:
        x = Vector((1.0, 0.0, 0.0)).cross(z)
    x.normalize()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed()
    return m.to_4x4()
