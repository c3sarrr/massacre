# Prova de conceito v2 (rascunho, fora do projeto): AKM nas medidas da foto do Armémuseum (lado direito, CC BY-SA 4.0),
# lida só no canvas da régua. Medidas em mm no referencial da foto: boca do cano em x = 0, eixo do cano em y = 0.
# No Blender: X = x, Z = y, lado direito da arma = -Y. Uso: blender -b --factory-startup -P ak_v2.py -- <saida> [vistas]
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(AQUI, 'base_helpers.py'), encoding='utf-8').read())
_final = open(os.path.join(AQUI, 'base_final.py'), encoding='utf-8').read()
exec(_final[:_final.index('def main():')])
from mathutils import Vector
import math


def mat_quadriculado(nome, cor, rug):
    """Baquelite com quadriculado (checkering) em relevo."""
    m, n, l, b = novo_mat(nome)
    r = ruido(n, 30.0, 4.0)
    l.new(mistura_cor(n, l, faixa(n, l, r.outputs['Fac'], 0.0, 0.45), cor, tuple(c * 0.62 for c in cor)), b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rug
    tc = n.new('ShaderNodeTexCoord')
    onda = []
    for ang in (45.0, -45.0):
        mp = n.new('ShaderNodeMapping')
        mp.inputs['Rotation'].default_value = (math.radians(90), math.radians(ang), 0)
        l.new(tc.outputs['Object'], mp.inputs['Vector'])
        w = n.new('ShaderNodeTexWave')
        w.wave_type = 'BANDS'
        w.inputs['Scale'].default_value = 420.0
        w.inputs['Distortion'].default_value = 0.0
        l.new(mp.outputs['Vector'], w.inputs['Vector'])
        onda.append(w)
    mul = n.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    l.new(onda[0].outputs['Fac'], mul.inputs[0])
    l.new(onda[1].outputs['Fac'], mul.inputs[1])
    bp = n.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = 0.55
    bp.inputs['Distance'].default_value = 0.0003
    l.new(mul.outputs['Value'], bp.inputs['Height'])
    bev, _ = mascara_borda(n, l, 1.6)
    l.new(bev.outputs['Normal'], bp.inputs['Normal'])
    l.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_madeira2(nome):
    """Madeira laminada envernizada: veio fino e alongado, contraste baixo, verniz."""
    m, n, l, b = novo_mat(nome)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.25, 7.0, 7.0)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    w = n.new('ShaderNodeTexWave')
    w.wave_type = 'RINGS'
    w.inputs['Scale'].default_value = 34.0
    w.inputs['Distortion'].default_value = 14.0
    w.inputs['Detail'].default_value = 6.0
    w.inputs['Detail Roughness'].default_value = 0.7
    l.new(mp.outputs['Vector'], w.inputs['Vector'])
    r = ruido(n, 60.0, 8.0)
    l.new(mp.outputs['Vector'], r.inputs['Vector'])
    mx = n.new('ShaderNodeMath')
    mx.operation = 'MULTIPLY_ADD'
    l.new(w.outputs['Fac'], mx.inputs[0])
    mx.inputs[1].default_value = 0.55
    l.new(r.outputs['Fac'], mx.inputs[2])
    rp = n.new('ShaderNodeValToRGB')
    rp.color_ramp.elements[0].position = 0.35
    rp.color_ramp.elements[0].color = (0.21, 0.035, 0.008, 1)
    rp.color_ramp.elements[1].position = 1.0
    rp.color_ramp.elements[1].color = (0.42, 0.095, 0.016, 1)
    l.new(mx.outputs['Value'], rp.inputs['Fac'])
    l.new(rp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.45
    b.inputs['Coat Weight'].default_value = 0.7
    b.inputs['Coat Roughness'].default_value = 0.22
    bev, _ = mascara_borda(n, l, 2.0)
    l.new(bev.outputs['Normal'], b.inputs['Normal'])
    return m


def reamostrar(poli, n):
    """Pontos igualmente espaçados ao longo de uma polilinha."""
    comp = [0.0]
    for (ax, ay), (bx, by) in zip(poli, poli[1:]):
        comp.append(comp[-1] + math.hypot(bx - ax, by - ay))
    out = []
    for i in range(n):
        alvo = comp[-1] * i / (n - 1)
        k = max(1, next((j for j, c in enumerate(comp) if c >= alvo), len(comp) - 1))
        t = (alvo - comp[k - 1]) / max(1e-9, comp[k] - comp[k - 1])
        (ax, ay), (bx, by) = poli[k - 1], poli[k]
        out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def faixa_poligono(linha, larg):
    """Tira de largura larg em volta de uma polilinha (para nervuras)."""
    esq, dir_ = [], []
    for i, (x, y) in enumerate(linha):
        a = linha[max(0, i - 1)]
        b = linha[min(len(linha) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / L * larg / 2, tx / L * larg / 2
        esq.append((x + nx, y + ny))
        dir_.append((x - nx, y - ny))
    return esq + dir_[::-1]


def afinar(ob, fn):
    for vt in ob.data.vertices:
        vt.co.y *= fn(vt.co.x / S, vt.co.z / S)


def construir2():
    aco = mat_aco('aço fosfatizado', (0.034, 0.035, 0.035), 0.45)
    aco_carr = mat_aco('aço do carregador', (0.11, 0.125, 0.135), 0.30, gasto=(0.40, 0.41, 0.43))
    aco_claro = mat_aco('aço polido', (0.42, 0.42, 0.43), 0.22, gasto=(0.6, 0.6, 0.6))
    madeira = mat_madeira2('madeira laminada')
    baquelite = mat_quadriculado('baquelite do punho', (0.34, 0.095, 0.016), 0.36)

    # Coronha (contorno da foto; o talão termina em -872 e a soleira de aço cobre o fim)
    coronha = prisma('coronha', [(-640, 6), (-648.4, 5.7), (-654.3, 3.9), (-663.9, 2), (-672.5, -0.2), (-677.9, -1.6), (-702.9, -7.9),
                                 (-714.3, -7.5), (-727, -3.4), (-815.1, -3.9), (-855.5, -3.4), (-869.1, -2.5), (-872, -3.6), (-872.5, -98.3),
                                 (-869.6, -98.8), (-862.7, -97.4), (-860.9, -100.6), (-855.9, -101), (-833.7, -94.2), (-787.8, -82.4),
                                 (-756.9, -74.7), (-731.5, -67.9), (-714.7, -63.3), (-696.6, -58.3), (-658.9, -48.8), (-640, -45)],
                     'XZ', -20.5, 20.5, madeira, 3.0)
    coronha['chanfro'] = (3.2, 4)
    afinar(coronha, lambda x, z: 0.70 + 0.30 * min(1.0, max(0.0, (-x - 650) / 220)))
    prisma('soleira', [(-871.5, -3.6), (-873.6, -3.9), (-875, -6.1), (-875.9, -45.2), (-880, -84.7), (-880, -93.8), (-879.1, -96.5),
                       (-877.7, -97.4), (-873.2, -97.4), (-872.3, -98.3), (-871.5, -98.3)], 'XZ', -21.3, 21.3, aco, 1.0)

    # Receptor estampado (30 mm), tampa (32 mm) com o degrau da janela, munhão dianteiro sob a alça
    rec = prisma('receptor', [(-644, 11), (-559, 11), (-556, 7.5), (-418, 7.5), (-418, 12), (-388, 12), (-388, -33), (-418.2, -35.6),
                              (-426.4, -37), (-431.4, -39.7), (-434.6, -40), (-520, -40), (-572, -40), (-630, -40), (-644, -38)],
                 'XZ', -15, 15, aco, 0.8)
    for y in (-15.8, 15.8):
        cov = esfera('covinha', (-470.5, y, -14), 1.0, (8.5, 2.0, 3.0), aco)
        cortar(rec, cov)
    janela = caixa('janela', (-505, -30, 0), (-446, -13, 8), aco, 0)
    cortar(rec, janela)
    caixa('ferrolho', (-503, -13.6, 0.5), (-448, 8, 7.4), aco_claro, 0.4)
    for x, z in [(-628, 2.4), (-604, -9.7), (-548, -12), (-531, -12), (-505, -3), (-449, -14), (-416, 3), (-401, 3), (-416, -20), (-401, -20)]:
        for y in (-15.3, 15.3):
            esfera('rebite', (x, y, z), 2.3, (1.0, 0.42, 1.0), aco, 16, 8)
    tampa = prisma('tampa', [(-418, 7.5), (-418, 33.4), (-612.5, 33.8), (-615.7, 32.5), (-619.4, 28.4), (-624.8, 23.8), (-629.3, 19.8),
                             (-633.9, 19.8), (-636, 17), (-636, 11), (-559, 11), (-556, 7.5)], 'XZ', -16, 16, aco, 4.0)
    tampa['chanfro'] = (4.5, 5)
    for i in range(5):
        x = -600 + i * 38
        nerv = prisma('nervura da tampa', [(x, 33.2), (x + 5, 33.2), (x + 5, 34.4), (x, 34.4)], 'XZ', -11, 11, aco, 0.5)
    torno('botão da mola', [(-641, 0), (-641, 3.6), (-633, 3.6), (-633, 0)], aco, 24, centro=(0, 0, 13.5), chanfro=0.6)

    # Punho de baquelite quadriculado e guarda-mato, gatilho e retém do carregador (contornos da foto)
    punho = prisma('punho', [(-632, -38), (-628.9, -44.7), (-625.3, -49.3), (-623.9, -57), (-639.8, -104.7), (-642.1, -111), (-644.3, -114.7),
                             (-643.9, -120.1), (-642.1, -124.6), (-639.8, -127.4), (-636.6, -128.7), (-624.4, -133.7), (-619.8, -136.4),
                             (-613.5, -138.3), (-608.9, -138.7), (-605.3, -136.4), (-603, -132.4), (-602.6, -122.4), (-600.3, -115.6),
                             (-598, -109.2), (-587.6, -78.8), (-583, -70.6), (-576.7, -64.7), (-574.5, -58), (-574, -38)],
                   'XZ', -15, 15, baquelite, 5.0)
    punho['chanfro'] = (5.5, 5)
    prisma('guarda-mato', [(-576, -40), (-574.4, -59.3), (-572.6, -62), (-569, -65.2), (-562.1, -67.4), (-539.4, -67.4), (-529, -66.5),
                           (-521.3, -63.3), (-520.4, -60.2), (-519.5, -40), (-521.7, -40), (-521.7, -57.9), (-524.5, -61.1), (-562.1, -63.3),
                           (-567.6, -62), (-570.3, -59.3), (-572.1, -56.1), (-572.6, -52.4), (-572.6, -40)], 'XZ', -5, 5, aco, 0.6)
    prisma('gatilho', [(-561.2, -39), (-561.2, -46.5), (-559.9, -49.7), (-554.4, -55.6), (-549.9, -57.9), (-545.8, -58.3), (-545.3, -56.5),
                       (-546.3, -55.2), (-550.8, -53.8), (-554.9, -50.2), (-555.8, -47.5), (-555.8, -39)], 'XZ', -3.5, 3.5, aco, 0.5)
    prisma('retém do carregador', [(-519, -39), (-497, -39), (-497.7, -55.6), (-500.8, -59.3), (-506.3, -58.8), (-509.5, -70.2), (-510.8, -70.2),
                                    (-510.8, -59.7), (-519.5, -59.3)], 'XZ', -7, 7, aco, 0.5)

    # Carregador de aço nervurado (contorno da foto), base e as 4 nervuras que seguem a curva
    trás = [(-489.9, -67.9), (-487.7, -74.2), (-485.4, -80.6), (-480.9, -92.4), (-468.6, -116.5), (-465.9, -121), (-463.6, -124.6),
            (-460.4, -129.6), (-456.8, -135.1), (-454.1, -138.7), (-451.4, -142.4), (-448.6, -146), (-443.6, -151.9), (-439.1, -156.9),
            (-428.6, -167.8), (-424.6, -170.5), (-419.6, -175.5), (-411.4, -182.3), (-407.3, -184.6), (-402.8, -187.8), (-398.7, -191.4),
            (-393.2, -194.6), (-391, -198.2)]
    frente = [(-434.6, -44.7), (-432.7, -52.9), (-430, -60.6), (-418.2, -83.8), (-413.2, -92), (-410.5, -96.9), (-407.3, -100.6),
              (-403.7, -105.1), (-400.5, -110.1), (-383.2, -126.9), (-373.3, -136), (-366, -140.5), (-360.1, -145.5), (-356.4, -146.4)]
    fundo = [(-388.2, -198.7), (-386, -196.4), (-382.3, -196.4), (-377.8, -192.3), (-373.7, -185.9), (-368.3, -177.8), (-364.2, -171.4),
             (-361.9, -166.4), (-361.9, -164.1), (-363.3, -161), (-356.4, -149.6)]
    carr = prisma('carregador', [(-494, -38), (-494, -53.8)] + trás + fundo + frente[::-1] + [(-434.6, -38)], 'XZ', -13.5, 13.5, aco_carr, 1.2)
    rt = reamostrar(trás, 40)
    fr = reamostrar(frente[::-1], 40)[::-1]
    for f in (0.2, 0.38, 0.56, 0.74):
        linha = [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) for a, b in zip(rt, fr)][3:36]
        for y0, y1 in ((-14.4, -13.3), (13.3, 14.4)):
            prisma('nervura do carregador', faixa_poligono(linha, 2.4), 'XZ', y0, y1, aco_carr, 0.4)
    b0, b1 = (-391, -198.7), (-356.4, -146.4)
    ex, ey = b1[0] - b0[0], b1[1] - b0[1]
    L = math.hypot(ex, ey)
    ex, ey = ex / L, ey / L
    nx, ny = -ey, ex
    prisma('base do carregador', [(b0[0] - ex * 1.5, b0[1] - ey * 1.5), (b1[0] + ex * 1.5, b1[1] + ey * 1.5),
                                  (b1[0] + ex * 1.5 + nx * 7, b1[1] + ey * 1.5 + ny * 7), (b0[0] - ex * 1.5 + nx * 7, b0[1] - ey * 1.5 + ny * 7)],
           'XZ', -15, 15, aco_carr, 1.0)

    # Seletor na posição de segurança, eixo, manejo com a bola
    prisma('seletor', [(-590, 1.6), (-500, 14.6), (-493, 12.5), (-492, 4.5), (-497, 2.5), (-503, 6.5), (-578, -9.5)], 'XZ', -17.6, -15.6, aco, 0.5)
    eixo = torno('eixo do seletor', [(15.3, 0), (15.3, 6), (18.2, 6), (18.2, 0)], aco, 28, eixo='Z', centro=(-584, 0, -4.4))
    rotacionar(eixo, 'X', 90, (-584, 0, -4.4))
    haste = torno('manejo', [(-2, 0), (-2, 3.2), (24, 3.2), (24, 0)], aco_claro, 20, eixo='Z', centro=(-416, 0, 19))
    rotacionar(haste, 'X', 90, (-416, 0, 19))
    esfera('bola do manejo', (-416, -26, 21), 5.2, (1.0, 1.0, 1.2), aco_claro)

    # Base da alça, folha com o entalhe e o cursor (contorno da foto)
    prisma('base da alça', [(-418, 12), (-418, 37), (-348, 37), (-348, 12)], 'XZ', -12.5, 12.5, aco, 0.9)
    prisma('folha da alça', [(-418.7, 36), (-418.7, 48.8), (-415.5, 48.4), (-415, 44.3), (-413.7, 44.3), (-412.8, 47.5), (-410.9, 48.4),
                             (-406.9, 47.9), (-405.9, 47), (-405.5, 44.3), (-378.2, 44.7), (-348.3, 44.3), (-347, 41.5), (-347, 36)],
           'XZ', -7, 7, aco, 0.5)
    prisma('cursor da alça', [(-378, 43), (-377.8, 45.6), (-369.2, 45.6), (-368.3, 47), (-364.2, 47), (-362.8, 45.6), (-362.4, 43)],
           'XZ', -9, 9, aco, 0.5)
    eixo_folha = torno('eixo da folha', [(-9.5, 0), (-9.5, 3.2), (9.5, 3.2), (9.5, 0)], aco, 20, eixo='Z', centro=(-355, 0, 41.5))
    rotacionar(eixo_folha, 'X', 90, (-355, 0, 41.5))

    # Guarda-mãos de madeira (contornos da foto) e a braçadeira dianteira
    sup = prisma('guarda-mão superior', [(-344.2, 18), (-344.2, 37.9), (-339.2, 39.3), (-332.4, 39.3), (-306.5, 38.4), (-254.3, 37.9),
                                          (-239.8, 37), (-236, 37.5), (-236, 18)], 'XZ', -14.5, 14.5, madeira, 5.5)
    sup['chanfro'] = (6.0, 5)
    inf = prisma('guarda-mão inferior', [(-388, 16.5), (-236, 16.5), (-236, -26.6), (-237.9, -27), (-334.7, -30.2), (-345.6, -32), (-355.5, -35.6),
                                          (-366, -37.9), (-373.3, -37.5), (-383.2, -35.2), (-388, -30)], 'XZ', -19.5, 19.5, madeira, 3.0)
    inf['chanfro'] = (3.5, 4)
    afinar(inf, lambda x, z: 1.0 + 0.16 * min(1.0, max(0.0, (-z - 5) / 30)))
    prisma('braçadeira', [(-237, -26), (-226, -22), (-226, 16), (-237, 16)], 'XZ', -21, 21, aco, 1.0)
    prisma('braçadeira do tubo', [(-237, 12), (-226, 12), (-226, 34.5), (-237, 36)], 'XZ', -12, 12, aco, 1.2)

    # Cano, tubo de gases com a cinta, bloco de gases, vareta, bloco da massa, orelhas, massa e quebra-chamas
    torno('cano', [(-412, 0), (-412, 7.4), (-160, 7.0), (-26, 6.8), (-26, 0)], aco, 48)
    torno('tubo de gases', [(-236, 0), (-236, 9.6), (-160, 9.6), (-160, 0)], aco, 40, centro=(0, 0, 22.95))
    torno('cinta do tubo', [(-180, 0), (-180, 10.4), (-173.5, 10.4), (-173.5, 0)], aco, 40, centro=(0, 0, 22.95))
    prisma('bloco de gases', [(-165, -18.4), (-143.9, -18.4), (-140.8, -19.8), (-128.5, -20.2), (-124.4, -18.8), (-122.6, -15.7),
                              (-122.6, 6.6), (-127.6, 6.6), (-128, 8.9), (-133, 9.3), (-142.1, 13.8), (-152.1, 25.7), (-154.8, 30.2),
                              (-155.3, 32.5), (-165, 32.5)], 'XZ', -11, 11, aco, 1.2)
    torno('vareta', [(-390, 0), (-390, 2.75), (-44, 2.75), (-44, 0)], aco, 20, centro=(0, 0, -12.75))
    prisma('base da massa', [(-57, -15.7), (-47.2, -16.1), (-43.6, -17), (-40.9, -18.8), (-34.1, -18.8), (-28.2, -16.1), (-26.3, -14.3),
                             (-26.3, -12), (-30, -8.9), (-30.9, 7.9), (-31.3, 12), (-34.5, 12.5), (-52, 12.5), (-57.2, 6.6)],
           'XZ', -12, 12, aco, 1.0)
    for y0 in (-8.8, 6.0):
        prisma('orelha da massa', [(-52, 12), (-51.3, 42), (-50.4, 44.7), (-48.1, 46.1), (-46.8, 48.8), (-45, 49.3), (-38.1, 48.8),
                                   (-36.8, 47), (-36.8, 38.8), (-34.5, 21.1), (-34.5, 12)], 'XZ', y0, y0 + 2.8, aco, 0.6)
    torno('massa de mira', [(12, 0), (12, 1.1), (44, 1.1), (44, 0)], aco, 16, eixo='Z', centro=(-44, 0, 0))
    freio = torno('quebra-chamas', [(-31, 0), (-31, 8.4), (0, 8.4), (0, 0)], aco, 48)
    obliquo = prisma('corte oblíquo', [(-15.5, 12), (-15.5, 8.2), (-14.1, 3.9), (-12.7, 2), (-4.5, -1.6), (0.6, -5.4), (6, -5.4), (6, 12)],
                     'XZ', -12, 12, aco, 0)
    cortar(freio, obliquo)
    alma = torno('alma', [(-35, 0), (-35, 4.1), (6, 4.1), (6, 0)], aco, 24)
    cortar(freio, alma)


def main2():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    construir2()
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
    cams = {
        'tres': camera('tres', (-0.17, -0.70, 0.21), (-0.43, 0.0, -0.075), 50),
        'lado': camera('lado', (-0.44, -1.5, -0.075), (-0.44, 0.0, -0.075), 50, orto=0.9),
        'perto': camera('perto', (-0.43, -0.24, 0.06), (-0.52, 0.0, -0.02), 55),
    }
    for nome in VISTAS:
        mascara = nome == 'mascara'
        sc.camera = cams['lado' if mascara else nome]
        if mascara:
            # silhueta pura (alfa) na mesma câmera ortográfica da vista de lado, para comparar com a foto
            sc.render.engine = 'BLENDER_WORKBENCH'
            sc.render.film_transparent = True
            sc.render.image_settings.color_mode = 'RGBA'
            bpy.data.objects['fundo'].hide_render = True
        sc.render.filepath = os.path.join(SAIDA, f'ak2_{nome}.png')
        bpy.ops.render.render(write_still=True)
        print('render', nome, dev)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, 'ak_v2.blend'))


main2()
