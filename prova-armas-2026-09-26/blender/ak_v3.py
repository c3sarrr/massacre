# Prova de conceito v3 (rascunho, fora do projeto): AK-47 tipo 3 (receptor fresado), 870 mm, nas medidas da foto
# "AK-47 assault rifle.jpg" (domínio público, Ickybicky), lida só no canvas da régua. mm no referencial da foto: boca do
# cano em x = 0, eixo do cano em y = 0. No Blender: X = x, Z = y, lado direito da arma = -Y.
# Uso: blender -b --factory-startup -P ak_v3.py -- <saida> [vistas: lado tres perto mascara]
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(AQUI, 'base_helpers.py'), encoding='utf-8').read())
_final = open(os.path.join(AQUI, 'base_final.py'), encoding='utf-8').read()
exec(_final[:_final.index('def main():')])
_v2 = open(os.path.join(AQUI, 'ak_v2.py'), encoding='utf-8').read()
exec(_v2[_v2.index('def mat_quadriculado'):_v2.index('def construir2')])
import math

CX, CZ = -435, -81  # centro das vistas (mm)


def suavizar(pts, it=2):
    """Chaikin em polígono fechado: tira o serrilhado de contorno lido de foto de baixa resolução."""
    for _ in range(it):
        novo = []
        for i, (ax, ay) in enumerate(pts):
            bx, by = pts[(i + 1) % len(pts)]
            novo += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        pts = novo
    return pts


def pino(nome, x, z, r, mat, lado=-1, de=16.0, ate=16.9):
    """Cabeça de pino/eixo no lado direito (lado=-1) ou esquerdo (+1): cilindro curto ao longo de Y."""
    ob = torno(nome, [(de, 0), (de, r), (ate, r), (ate, 0)], mat, 24, eixo='Z', centro=(x, 0, z))
    rotacionar(ob, 'X', 90 if lado < 0 else -90, (x, 0, z))
    return ob


def construir3():
    aco = mat_aco('aço oxidado', (0.030, 0.031, 0.036), 0.34, gasto=(0.32, 0.32, 0.34))
    aco_carr = mat_aco('aço do carregador', (0.075, 0.080, 0.088), 0.34, gasto=(0.36, 0.37, 0.39))
    aco_claro = mat_aco('aço polido', (0.42, 0.42, 0.43), 0.22, gasto=(0.6, 0.6, 0.6))
    madeira = mat_madeira2('madeira da AK-47')
    for el, cor in zip(madeira.node_tree.nodes['Color Ramp'].color_ramp.elements, ((0.19, 0.055, 0.018, 1), (0.37, 0.135, 0.05, 1))):
        el.color = cor

    # Coronha (contorno da foto) e soleira de aço inclinada
    bunda = [(-869, -29.5), (-870, -41.7), (-865.9, -58), (-865.9, -65.1), (-858.8, -99.7), (-857.8, -112.9), (-856.8, -117), (-853.7, -120.1)]
    bunda_in = [(x + 5, y) for x, y in bunda]
    coronha = prisma('coronha', suavizar([(-636, 0), (-642.1, -1), (-642.1, -3.1), (-708.2, -16.3), (-716.4, -16.3), (-728.6, -11.2), (-742.8, -11.2),
                                 (-781.5, -17.3), (-805.9, -19.3), (-812, -21.4), (-858.8, -26.5), (-864, -28.7)] + bunda_in[1:]
                     + [(-838.5, -119.1), (-830.3, -115), (-824.2, -112.9), (-788.6, -101.8), (-771.3, -95.6), (-759.1, -91.6), (-743.8, -86.5),
                        (-692.9, -69.2), (-680.7, -65.1), (-669.5, -60), (-663.4, -58), (-632.9, -48.8), (-627.8, -46.8), (-627.8, -44), (-636, -44)]),
                     'XZ', -21, 21, madeira, 3.0)
    coronha['chanfro'] = (3.4, 4)
    afinar(coronha, lambda x, z: 0.70 + 0.30 * min(1.0, max(0.0, (-x - 645) / 215)))
    prisma('soleira', bunda + bunda_in[::-1], 'XZ', -21.6, 21.6, aco, 1.0)

    # Receptor fresado: recorte de alívio acima do carregador, janela de ejeção com o ferrolho, pinos e o eixo do seletor
    rec = prisma('receptor', [(-638, 13), (-478, 13), (-474, 9), (-399, 9), (-399, 12), (-368, 12), (-368, -33.6), (-376.5, -32.6),
                              (-423.3, -35.6), (-424.3, -40.7), (-560, -40.7), (-564, -44), (-630, -44), (-642.1, -42), (-642.1, -1),
                              (-638, 2)], 'XZ', -16, 16, aco, 0.9)
    for y0, y1 in ((-22, -14), (14, 22)):
        cortar(rec, caixa('recorte de alívio', (-462, y0, -26.8), (-377, y1, -10.6), aco, 0))
    cortar(rec, caixa('janela', (-474, -30, 4.5), (-405, -13, 19), aco, 0))
    caixa('ferrolho', (-472, -13.6, 9.5), (-407, 10, 18.5), aco_claro, 0.5)
    for x, z in [(-551, -33), (-532, -29.4), (-511, -24.4), (-496.5, -29.7), (-485.6, -31.2)]:
        pino('pino', x, z, 2.4, aco, -1)
        pino('pino', x, z, 2.4, aco, +1)
    pino('eixo do seletor', -575, -13.2, 6.5, aco, -1, 16.0, 18.6)

    # Tampa lisa (a AK-47 não tem nervuras), com o degrau da janela
    tampa = prisma('tampa', [(-399, 18.8), (-399, 34.6), (-547.4, 33.6), (-607.5, 31.5), (-614.6, 28.5), (-627.8, 16.3), (-632.9, 16.3),
                             (-634, 13), (-478, 13), (-474, 18.8)], 'XZ', -16.5, 16.5, aco, 4.5)
    tampa['chanfro'] = (4.8, 5)
    prisma('botão da mola', [(-642.1, 2), (-638, 2), (-638, 7.1), (-632.9, 13), (-642.1, 13)], 'XZ', -7, 7, aco, 1.0)

    # Punho de madeira com o calombo, guarda-mato, gatilho e retém (contornos da foto)
    punho = prisma('punho', suavizar([(-627.8, -44), (-626.8, -54.9), (-619.7, -65.1), (-618.7, -72.2), (-623.8, -88.5), (-626.8, -92.6), (-628.8, -101.8),
                             (-631.9, -105.8), (-632.9, -111.9), (-638, -122.1), (-638, -132.3), (-629.9, -142.5), (-616.6, -147.5),
                             (-602.4, -147.5), (-596.3, -143.5), (-595.3, -126.2), (-593.2, -124.1), (-589.2, -109.9), (-586.1, -105.8),
                             (-579, -85.5), (-574.9, -79.4), (-573.9, -74.3), (-570.8, -71.2), (-566, -69), (-564, -44)]), 'XZ', -15, 15, madeira, 6.0)
    punho['chanfro'] = (6.5, 5)
    prisma('guarda-mato', [(-566, -44), (-564.7, -68.2), (-563.7, -71.2), (-556.6, -76.3), (-520, -75.8), (-511.8, -74.8), (-508.5, -72.2),
                           (-508.5, -44), (-511.5, -44), (-511, -61.1), (-511, -68.2), (-514, -72.4), (-542.4, -73.4), (-553.5, -73.4),
                           (-559.6, -71.7), (-561.2, -65.1), (-561.5, -44)], 'XZ', -5, 5, aco, 0.6)
    prisma('gatilho', [(-555.5, -40), (-554.6, -44.8), (-551.5, -46.8), (-552.5, -51.9), (-549.5, -61.1), (-543.4, -66.1), (-537.3, -67.2),
                       (-546.4, -58), (-546.4, -47.8), (-540, -40)], 'XZ', -3.5, 3.5, aco, 0.5)
    prisma('retém do carregador', [(-506, -44), (-496, -44), (-494.5, -64.1), (-495.5, -77.3), (-497.6, -80.4), (-499.6, -79.4), (-499.6, -68.2),
                                   (-501.6, -66.1), (-507.8, -66.1)], 'XZ', -7, 7, aco, 0.5)

    # Carregador (contorno da foto), base e nervuras: três perto das costas e uma perto da frente
    trás = [(-489.4, -56), (-486.4, -76.3), (-481.3, -91.6), (-478.2, -95.6), (-476.2, -104.8), (-470.1, -115), (-468.1, -119.1), (-465, -128.2),
            (-462, -133.3), (-455.9, -140.4), (-452.8, -145.5), (-448.7, -153.6), (-441.6, -160.8), (-436.5, -167.9), (-407, -199.4),
            (-405, -199.4), (-396.8, -208.6), (-392.8, -209.6), (-388.7, -213.7)]
    fundo = [(-382.6, -213.7), (-380.6, -211.6), (-376.5, -211.6), (-376.5, -208.6), (-371.4, -204.5), (-370.4, -200.5), (-368.4, -199.4),
             (-356.1, -181.1), (-352.1, -175), (-349, -169.9), (-344.9, -161.8)]
    frente = [(-424.3, -46.8), (-420.2, -63.1), (-415.2, -74.3), (-413.1, -82.4), (-406, -96.7), (-404, -97.7), (-401.9, -103.8), (-391.8, -117),
              (-387.7, -122.1), (-381.6, -129.2), (-362.2, -149.6), (-360.2, -149.6), (-357.2, -153.6), (-352.1, -155.7)]
    prisma('carregador', suavizar([(-490, -40)] + trás + fundo + frente[::-1] + [(-424.5, -40)], 1), 'XZ', -14, 14, aco_carr, 1.2)
    rt = reamostrar(trás, 44)
    fr = reamostrar(frente, 44)
    for f in (0.16, 0.28, 0.40, 0.82):
        linha = [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) for a, b in zip(rt, fr)][4:39]
        for y0, y1 in ((-14.9, -13.8), (13.8, 14.9)):
            prisma('nervura do carregador', faixa_poligono(linha, 2.6), 'XZ', y0, y1, aco_carr, 0.4)
    b0, b1 = (-388.7, -213.7), (-344.9, -161.8)
    ex, ey = b1[0] - b0[0], b1[1] - b0[1]
    L = math.hypot(ex, ey)
    ex, ey = ex / L, ey / L
    nx, ny = -ey, ex
    prisma('base do carregador', [(b0[0] - ex * 1.5, b0[1] - ey * 1.5), (b1[0] + ex * 1.5, b1[1] + ey * 1.5),
                                  (b1[0] + ex * 1.5 + nx * 7, b1[1] + ey * 1.5 + ny * 7), (b0[0] - ex * 1.5 + nx * 7, b0[1] - ey * 1.5 + ny * 7)],
           'XZ', -15.5, 15.5, aco_carr, 1.0)

    # Seletor (posição de segurança), manejo com a bola
    prisma('seletor', [(-582, -8), (-487, 9.5), (-481, 8), (-480, 1), (-486, -1), (-491, 3), (-571, -20)], 'XZ', -18.6, -16.6, aco, 0.5)
    haste = torno('manejo', [(-2, 0), (-2, 3.2), (26, 3.2), (26, 0)], aco_claro, 20, eixo='Z', centro=(-402, 0, 12))
    rotacionar(haste, 'X', 90, (-402, 0, 12))
    esfera('bola do manejo', (-402, -28, 13.5), 5.2, (1.0, 1.0, 1.2), aco_claro)

    # Base da alça, folha com o entalhe e os dentes, cursor (contorno da foto)
    prisma('base da alça', [(-401.9, 12), (-401.9, 36.6), (-331.7, 36.6), (-331.7, 12)], 'XZ', -12.5, 12.5, aco, 0.9)
    prisma('folha da alça', [(-401.9, 36), (-401.9, 46.8), (-398.3, 46.2), (-397, 41), (-393, 41.5), (-389.7, 46.8), (-383.6, 45.8),
                             (-382.6, 42.7), (-340, 43.8), (-333.8, 43.8), (-331.7, 40.7), (-331.7, 36)], 'XZ', -7, 7, aco, 0.5)
    for x in (-380.5, -375.5, -370.5, -365.5):
        prisma('dente da folha', [(x, 42.5), (x + 2, 42.5), (x + 2, 44.6), (x, 44.6)], 'XZ', -7.4, -5, aco, 0.3)
    prisma('cursor da alça', [(-357, 42), (-356.1, 45.8), (-350, 45.8), (-349, 42)], 'XZ', -9, 9, aco, 0.5)

    # Guarda-mãos (com a fresta entre eles) e as braçadeiras
    sup = prisma('guarda-mão superior', [(-328.7, 14), (-328.7, 34.6), (-326.6, 39.7), (-322.6, 40.7), (-252.4, 40.7), (-223.9, 39.7),
                                          (-217.8, 38.7), (-216.7, 34.6), (-216.7, 14)], 'XZ', -15, 15, madeira, 6.0)
    sup['chanfro'] = (6.5, 5)
    inf = prisma('guarda-mão inferior', [(-368, 10.3), (-222.6, 10.3), (-222.6, -25.4), (-225.9, -25.4), (-320.5, -27.5), (-340.9, -33.6),
                                          (-351.1, -39.7), (-362.2, -39.7), (-368, -34)], 'XZ', -20, 20, madeira, 3.2)
    inf['chanfro'] = (3.6, 4)
    afinar(inf, lambda x, z: 1.0 + 0.10 * min(1.0, max(0.0, (-z - 5) / 30)))
    prisma('braçadeira', [(-225, -24), (-214, -22.4), (-214, 12), (-225, 12)], 'XZ', -21, 21, aco, 1.0)
    prisma('braçadeira do tubo', [(-225, 12), (-214, 12), (-214, 36), (-225, 36)], 'XZ', -12.5, 12.5, aco, 1.2)

    # Cano, tubo de gases com a fenda de respiro, bloco de gases, vareta, massa de mira e a porca da boca
    torno('cano', [(-399, 0), (-399, 7.6), (-150, 7.4), (-11, 7.1), (-11, 0)], aco, 48)
    tubo = torno('tubo de gases', [(-216, 0), (-216, 9.7), (-148, 9.7), (-148, 0)], aco, 40, centro=(0, 0, 23.9))
    cortar(tubo, esfera('fenda', (-191, -9.4, 21.5), 1.0, (12.5, 4.2, 2.4), aco))
    prisma('bloco de gases', [(-150, -12), (-150, 33.6), (-139.4, 33.6), (-135.3, 24.4), (-127.2, 15.3), (-115, 9.2), (-108.9, 9.2),
                              (-108.9, -9), (-130, -9), (-134, -12)], 'XZ', -11, 11, aco, 1.2)
    prisma('guia da vareta', [(-146, -20), (-136, -20), (-136, -10), (-146, -10)], 'XZ', -6, 6, aco, 0.8)
    torno('vareta', [(-368, 0), (-368, 2.9), (-19.3, 2.9), (-19.3, 0)], aco, 20, centro=(0, 0, -15.1))
    prisma('base da massa', [(-47.8, 7.1), (-44, 13.2), (-15.3, 13.2), (-11.2, 13.2), (-10.2, 9.2), (-10.2, -9), (-14.2, -8.1),
                             (-15.3, -14.2), (-18.3, -15.3), (-19.3, -12), (-47.8, -9)], 'XZ', -11, 11, aco, 1.0)
    torre = prisma('torre da massa', [(-47.8, 7.1), (-44.8, 18.3), (-35.6, 36.6), (-35.6, 46.8), (-33.6, 49.9), (-27.5, 51.9), (-18.3, 51.9),
                                      (-15.3, 48.8), (-15.3, 13.2)], 'XZ', -4.5, 4.5, aco, 0.8)
    cortar(torre, prisma('janela da torre', [(-37, 21), (-23, 21), (-23, 38), (-31, 38)], 'XZ', -10, 10, aco, 0))
    for y0 in (-8.8, 6.0):
        prisma('orelha da massa', [(-35.6, 30), (-35.6, 46.8), (-33.6, 49.9), (-27.5, 51.9), (-18.3, 51.9), (-15.3, 48.8), (-15.3, 30)],
               'XZ', y0, y0 + 2.8, aco, 0.6)
    torno('massa de mira', [(13, 0), (13, 1.1), (47, 1.1), (47, 0)], aco, 16, eixo='Z', centro=(-25, 0, 0))
    torno('porca da boca', [(-11, 0), (-11, 8.4), (-2.2, 8.4), (-1, 7.2), (-1, 0)], aco, 48, chanfro=0.4)
    alma = torno('alma', [(-8, 0), (-8, 3.9), (3, 3.9), (3, 0)], aco, 24)
    cortar(bpy.data.objects['porca da boca'], alma)


def main3():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    construir3()
    finalizar()
    estudio()
    sc = bpy.context.scene
    dev = gpu()
    sc.cycles.samples = 160
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 900
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    c = (CX / 1000, CZ / 1000)
    cams = {
        'tres': camera('tres', (-0.17, -0.70, 0.21), (-0.43, 0.0, -0.08), 50),
        'lado': camera('lado', (c[0], -1.5, c[1]), (c[0], 0.0, c[1]), 50, orto=0.9),
        'perto': camera('perto', (-0.42, -0.24, 0.06), (-0.52, 0.0, -0.03), 55),
    }
    for nome in VISTAS:
        mascara = nome == 'mascara'
        sc.camera = cams['lado' if mascara else nome]
        if mascara:
            sc.render.engine = 'BLENDER_WORKBENCH'
            sc.render.film_transparent = True
            sc.render.image_settings.color_mode = 'RGBA'
            bpy.data.objects['fundo'].hide_render = True
        sc.render.filepath = os.path.join(SAIDA, f'ak3_{nome}.png')
        bpy.ops.render.render(write_still=True)
        print('render', nome, dev)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, 'ak_v3.blend'))


main3()
