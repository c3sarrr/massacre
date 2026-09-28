# Renders da conferência das armas realistas (Fase 4.1a; desenho, seção 4.7): lado, cima, frente, 3/4 dos dois lados,
# perto do receptor e a vista aproximada da primeira pessoa (a câmera no olho do boneco com o FOV do viewmodel — 60
# horizontais em 4:3 = 75,2° em 16:9 — e a arma na posição da categoria `rifle`), no modelo alto com os materiais de
# fábrica, em tools/blender/conferencia/<id>/ (fora do git). A sobreposição da silhueta com a foto (sobreposicao.png)
# sai do validar.py. Desde a 4.1b, as luvas na pega (a luva de jogo pelo modelo das luvas, na pose e no encaixe que o
# construir guardou nos rigs): as vistas de perto de cada mão pelos dois lados, por baixo e por trás, e a primeira
# pessoa com as luvas (seção 6.3 do desenho da 4.1b).
import json
import os

import bpy
from mathutils import Matrix, Vector

from . import estudio, luvas, maos, maos_correcoes, maos_rig
from .unidades import S


def conferir(ctx, pasta, amostras=160):
    sc = bpy.context.scene
    alto = bpy.data.collections['alto']
    for col in sc.collection.children:
        col.hide_render = col is not alto
    xs = [p[0] for p in ctx['ficha']['contorno']]
    ys = [p[1] for p in ctx['ficha']['contorno']]
    cx, cy = (min(xs) + max(xs)) / 2 * S, (min(ys) + max(ys)) / 2 * S
    comp = (max(xs) - min(xs)) * S
    fundo = estudio.montar((cx, 0.0, cy))
    dispositivo = estudio.render(1600, 900, amostras)
    c = (cx, 0.0, cy)
    receptor = (-0.50, 0.0, -0.01)
    olho = (-0.78, 0.114, 0.079)  # 9 u atrás, 4,5 u à esquerda e 3,1 u acima da origem (o pino do gatilho)
    vistas = {
        'lado': estudio.camera('lado', (cx, -1.5, cy), c, orto=comp * 1.04),
        'cima': estudio.camera('cima', (cx, 0.0, cy + 1.5), c, orto=comp * 1.04),
        'frente': estudio.camera('frente', (0.9, 0.0, cy), (0.0, 0.0, cy), orto=0.45),
        'tres_direita': estudio.camera('tres_direita', (cx + 0.27, -0.72, cy + 0.29), c, 50),
        'tres_esquerda': estudio.camera('tres_esquerda', (cx + 0.27, 0.72, cy + 0.29), c, 50),
        'perto': estudio.camera('perto', (receptor[0] + 0.08, -0.24, receptor[2] + 0.07), receptor, 55),
        'primeira_pessoa': estudio.camera('primeira_pessoa', olho, (olho[0] + 1.0, olho[1] - 0.02, olho[2] - 0.03), 23.4),
    }
    arquivos = []
    for nome, cam in vistas.items():
        sc.camera = cam
        sc.render.filepath = os.path.join(pasta, f'{nome}.png')
        bpy.ops.render.render(write_still=True)
        arquivos.append(sc.render.filepath)
    arquivos += _maos(ctx, pasta, sc, fundo)
    for col in sc.collection.children:
        col.hide_render = False
    return arquivos, dispositivo


def _maos(ctx, pasta, sc, fundo):
    """As luvas na pega: as malhas posadas (sem rig, como no jogo) e as vistas de perto de cada mão (as de baixo sem o
    chão do estúdio, que fica entre a câmera e a mão)."""
    rigs = [bpy.data.objects.get(f'rig_{lado}') for lado in ('d', 'e')]
    if not all(r is not None and 'pega' in r for r in rigs):
        return []
    col = bpy.data.collections.new('maos_da_pega')
    sc.collection.children.link(col)
    mao = maos.Mao(ctx['luvas']['ficha'])
    for lado, rig in zip(('d', 'e'), rigs):
        dados = json.loads(rig['pega'])
        luva = bpy.data.objects[f'luva_{lado}']
        modelo = maos_correcoes.Modelo(luva, rig, mao, luvas.REFORCO)
        ob = modelo.para_malha(f'pega_{lado}', col, maos_rig.pose_de_json(dados['pose']))
        e = Matrix(dados['encaixe'])
        e.translation = e.translation * S
        ob.matrix_world = e
        ob.hide_render = False
    maos_rig.posar(rigs[0], {})
    maos_rig.posar(rigs[1], {})
    arquivos = []
    for lado, nome in (('d', 'direita'), ('e', 'esquerda')):
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
    olho = (-0.78, 0.114, 0.079)
    sc.camera = estudio.camera('primeira_pessoa_luvas', olho, (olho[0] + 1.0, olho[1] - 0.02, olho[2] - 0.03), 23.4)
    sc.render.filepath = os.path.join(pasta, 'primeira_pessoa_luvas.png')
    bpy.ops.render.render(write_still=True)
    arquivos.append(sc.render.filepath)
    return arquivos
