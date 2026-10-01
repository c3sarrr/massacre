# Renders da conferência das armas realistas (Fase 4.1a; desenho, seção 4.7): lado, cima, frente, 3/4 dos dois lados,
# perto do receptor e a primeira pessoa (a câmera no olho do boneco com o FOV do viewmodel — 60 horizontais em 4:3 =
# 75,2° em 16:9 — e a arma na pose do jogo: a posição da categoria com os offsets padrão, que o contexto traz desde as
# correções da P1 da 4.1c; antes, um olho fixo em cada script, que não acompanhava a categoria — a faca saía de
# ponta-cabeça); desde a 4.1c, pelo tamanho de cada arma (vistas_da_arma), com o lado esquerdo e o de perto pelos dois
# lados, no modelo alto com os materiais de fábrica, em tools/blender/conferencia/<id>/ (fora do git). A sobreposição da
# silhueta com a foto (sobreposicao.png) sai do validar.py. Desde a 4.1b, as luvas na pega (a luva de jogo pelo modelo
# das luvas, na pose e no encaixe que o construir guardou nos rigs): as vistas de perto de cada mão pelos dois lados,
# por baixo e por trás, e a primeira pessoa com as luvas (seção 6.3 do desenho da 4.1b).
import json
import math
import os

import bpy
from mathutils import Matrix, Vector

from . import estudio, luvas, maos, maos_correcoes, maos_rig
from .unidades import S, U_POR_M


def primeira_pessoa(ctx, arma):
    """A câmera da primeira pessoa com a pose do jogo: (olho, alvo a 1 m, alto) no Blender (m) e a lente do FOV vertical
    do viewmodel no quadro de 16:9. O contexto traz a câmera no referencial da arma no jogo (u; +X a boca, +Y o alto, +Z
    o lado direito, a origem no ORIGEM_MM do script — placement.cameraInWeaponFrame); no Blender, Z é o alto e −Y o lado
    direito."""
    pp = ctx['primeiraPessoa']
    ox, oy = arma.ORIGEM_MM

    def no_blender(v):
        return Vector((v[0], -v[2], v[1]))

    olho = Vector((ox * S, 0.0, oy * S)) + no_blender(pp['olho']) / U_POR_M
    meia_largura = math.tan(math.radians(pp['fovVertical']) / 2) * 16 / 9
    return olho, olho + no_blender(pp['frente']), no_blender(pp['cima']), 18.0 / meia_largura


def vistas_da_arma(ctx, arma):
    """As câmeras da conferência pelo tamanho da arma (desde a 4.1c; eram as da AK): lado (a direita, a boca à direita) e
    o lado esquerdo (a boca à esquerda, o lado que a primeira pessoa mostra), cima e frente ortográficas pela caixa do
    contorno da ficha, os três quartos dos dois lados na distância proporcional ao comprimento, a de perto no ponto
    `PERTO_MM` do script da arma (x, y da ficha; sem ele, o da AK) e a primeira pessoa com a pose do jogo
    (primeira_pessoa). Cada uma: (nome, posição, alvo, lente, largura ortográfica, alto)."""
    xs = [p[0] for p in ctx['ficha']['contorno']]
    ys = [p[1] for p in ctx['ficha']['contorno']]
    cx, cy = (min(xs) + max(xs)) / 2 * S, (min(ys) + max(ys)) / 2 * S
    comp = (max(xs) - min(xs)) * S
    alt = (max(ys) - min(ys)) * S
    c = (cx, 0.0, cy)
    k = comp / 0.87  # a escala da AK (870 mm), em que as distâncias foram acertadas na 4.1a
    # numa arma curta e alta (a pistola) a altura manda: os três quartos pela maior das duas e a de perto com um mínimo
    # (a 55 mm da AK, a pistola ficava a 6 cm da serrilha)
    kt = max(comp, alt * 2.4) / 0.87
    kp = max(k, 0.45)
    px, py = getattr(arma, 'PERTO_MM', (-500.0, -10.0))
    perto = (px * S, 0.0, py * S)
    olho, alvo, cima, lente = primeira_pessoa(ctx, arma)
    # a janela ortográfica de lado cobre o comprimento e a altura (a pistola é mais alta que 9/16 do comprimento)
    orto = max(comp, alt * 1600 / 900) * 1.04
    return c, comp, {
        'lado': ('lado', (cx, -1.5, cy), c, None, orto, None),
        'lado_esquerdo': ('lado_esquerdo', (cx, 1.5, cy), c, None, orto, None),
        'cima': ('cima', (cx, 0.0, cy + 1.5), c, None, comp * 1.04, None),
        'frente': ('frente', (max(xs) * S + 0.9, 0.0, cy), (0.0, 0.0, cy), None, max(alt, comp * 0.3) * 1.5, None),
        'tres_direita': ('tres_direita', (cx + 0.27 * kt, -0.72 * kt, cy + 0.29 * kt), c, 50, None, None),
        'tres_esquerda': ('tres_esquerda', (cx + 0.27 * kt, 0.72 * kt, cy + 0.29 * kt), c, 50, None, None),
        'perto': ('perto', (perto[0] + 0.08 * kp, -0.24 * kp, perto[2] + 0.07 * kp), perto, 55, None, None),
        'perto_esquerda': ('perto_esquerda', (perto[0] + 0.08 * kp, 0.24 * kp, perto[2] + 0.07 * kp), perto, 55, None, None),
        'primeira_pessoa': ('primeira_pessoa', tuple(olho), tuple(alvo), lente, None, tuple(cima)),
    }


def conferir(ctx, pasta, arma, amostras=160):
    sc = bpy.context.scene
    alto = bpy.data.collections['alto']
    for col in sc.collection.children:
        col.hide_render = col is not alto
    c, _comp, defs = vistas_da_arma(ctx, arma)
    fundo = estudio.montar(c)
    dispositivo = estudio.render(1600, 900, amostras)
    vistas = {nome: estudio.camera(n, pos, alvo, lente or 50, orto=orto, cima=cima)
              for nome, (n, pos, alvo, lente, orto, cima) in defs.items()}
    # A área em mm da ficha de cada vista ortográfica de lado (a régua sobrepõe o render à foto por ela: ?janela=).
    janelas = {}
    for nome in ('lado', 'lado_esquerdo'):
        _n, pos, _alvo, _lente, orto, _cima = defs[nome]
        meia_l, meia_a = orto / 2 / S, orto * 900 / 1600 / 2 / S
        janelas[nome] = [pos[0] / S - meia_l, pos[0] / S + meia_l, pos[2] / S - meia_a, pos[2] / S + meia_a]
    with open(os.path.join(pasta, 'vistas.json'), 'w', encoding='utf-8') as f:
        json.dump({'janelas': janelas, 'espelhada': {'lado': False, 'lado_esquerdo': True}}, f, indent=1)
    arquivos = []
    for nome, cam in vistas.items():
        sc.camera = cam
        sc.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(sc.render.filepath)
    arquivos += _maos(ctx, pasta, sc, fundo, defs['primeira_pessoa'])
    for col in sc.collection.children:
        col.hide_render = False
    return arquivos, dispositivo


def _maos(ctx, pasta, sc, fundo, primeira):
    """As luvas na pega: as malhas posadas (sem rig, como no jogo), as vistas de perto de cada mão (as de baixo sem o
    chão do estúdio, que fica entre a câmera e a mão) e a primeira pessoa com elas (`primeira`, a câmera da vista
    `primeira_pessoa` de vistas_da_arma)."""
    # as mãos que a pega tem (as duas, ou só a direita na faca: 4.1c)
    rigs = {lado: bpy.data.objects.get(f'rig_{lado}') for lado in ('d', 'e')}
    rigs = {lado: r for lado, r in rigs.items() if r is not None and 'pega' in r}
    if 'd' not in rigs:
        return []
    col = bpy.data.collections.new('maos_da_pega')
    sc.collection.children.link(col)
    mao = maos.Mao(ctx['luvas']['ficha'])
    for lado, rig in rigs.items():
        dados = json.loads(rig['pega'])
        luva = bpy.data.objects[f'luva_{lado}']
        modelo = maos_correcoes.Modelo(luva, rig, mao, luvas.REFORCO)
        ob = modelo.para_malha(f'pega_{lado}', col, maos_rig.pose_de_json(dados['pose']))
        e = Matrix(dados['encaixe'])
        e.translation = e.translation * S
        ob.matrix_world = e
        ob.hide_render = False
    for rig in rigs.values():
        maos_rig.posar(rig, {})
    arquivos = []
    for lado, nome in (('d', 'direita'), ('e', 'esquerda')):
        if lado not in rigs:
            continue
        c = bpy.data.objects[f'soquete_mao_{lado}'].matrix_world.translation.copy()
        # A de trás vem de trás, de fora (−Y é a direita da arma) e de cima, como o atirador vê a própria mão: bem atrás
        # e no eixo, a coronha tapava a mão direita e o receptor, metade da esquerda; a da direita sobe mais (na altura
        # do antebraço, a câmera olhava para dentro do punho da luva, que no Blender não tem o braço de massinha).
        atras = {'d': (-0.18, -0.12, 0.18), 'e': (-0.24, 0.13, 0.05)}[lado]
        for vista, desloc in (('dir', (0.0, -0.3, 0.02)), ('esq', (0.0, 0.3, 0.02)), ('baixo', (0.04, -0.06, -0.3)),
                              ('tras', atras)):
            fundo.hide_render = vista == 'baixo'
            sc.camera = estudio.camera(f'mao_{nome}_{vista}', c + Vector(desloc), c, 45)
            sc.render.filepath = os.path.join(pasta, f'mao_{nome}_{vista}.png')
            bpy.ops.render.render(write_still=True)
            arquivos.append(sc.render.filepath)
    fundo.hide_render = False
    _n, olho, alvo, lente, _orto, cima = primeira
    sc.camera = estudio.camera('primeira_pessoa_luvas', olho, alvo, lente, cima=cima)
    sc.render.filepath = os.path.join(pasta, 'primeira_pessoa_luvas.png')
    bpy.ops.render.render(write_still=True)
    arquivos.append(sc.render.filepath)
    return arquivos
