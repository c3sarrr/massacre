# A abertura da frente da P90 em volta do gatilho e do seletor, nos dois níveis: os pontos, as folgas até o gatilho (a
# parte abaixo da borda de cima) e até o disco do seletor (com o chanfro de 0,5 mm da borda dele) e se o laço se cruza.
# Nada vai para o projeto. Uso: blender -b --factory-startup -P abertura_teste.py
import json
import math
import sys

sys.path.insert(0, r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender')
from armas import p90_mecanica as MEC  # noqa: E402
from armas import p90_quadro as Q  # noqa: E402
from armas import pecas as P  # noqa: E402

ficha = json.load(open(r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\refs\p90.json', encoding='utf-8'))


def dentro(pts, x, y):
    c = False
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            c = not c
    return c


def dist_seg(p, a, b):
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy or 1e-12)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def dist_laco(p, laco):
    return min(dist_seg(p, a, b) for a, b in zip(laco, laco[1:] + laco[:1]))


def amostras(poli, passo=0.05):
    out = []
    for a, b in zip(poli, poli[1:] + poli[:1]):
        n = max(1, int(math.dist(a, b) / passo))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out


def cruza(laco):
    segs = list(zip(laco, laco[1:] + laco[:1]))

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    n = 0
    for i in range(len(segs)):
        for j in range(i + 2, len(segs)):
            if i == 0 and j == len(segs) - 1:
                continue
            (a, b), (c, d) = segs[i], segs[j]
            if ori(a, b, c) * ori(a, b, d) < 0 and ori(c, d, a) * ori(c, d, b) < 0:
                n += 1
    return n


print('borda crua:', [(round(x, 2), round(y, 2)) for x, y in Q.abertura_da_frente(ficha)[-14:]])
topo = max(y for _, y in ficha['buracos'][ficha['buracosNomes'].index('aberturaFrente')])
# o gatilho abaixo da borda de cima; o disco de lado com o chanfro de 0,5 mm na borda e a lingueta
g = [p for p in amostras(MEC.contorno_do_gatilho(ficha)) if p[1] < topo - 1.0]  # a 1 mm da borda de cima (ali a lâmina entra na fenda)
sl = ficha['pontos']['seletor']
cx, r = sl['centro'][0], sl['raio']
ys = [y for _, y in ficha['pecas']['seletor']]
y0, y1 = min(ys), max(ys)
disco = [(cx - r + 0.5, y0), (cx + r - 0.5, y0), (cx + r, y0 + 0.5), (cx + r, y1 - 0.5), (cx + r - 0.5, y1), (cx - r + 0.5, y1),
         (cx - r, y1 - 0.5), (cx - r, y0 + 0.5)]
lx = max(x for x, _ in ficha['pecas']['seletor'])
ly = sorted(y for x, y in ficha['pecas']['seletor'] if x > -160.6 and y not in (y0, y1))
lingueta = [(cx + r - 0.5, ly[0]), (lx, ly[0]), (lx, ly[-1]), (cx + r - 0.5, ly[-1])]
for nivel in ('alto', 'jogo'):
    P.iniciar(nivel, nivel)
    laco = Q._furo(ficha, 'aberturaFrente')
    res = {}
    for nome, pts in (('gatilho', g), ('disco', amostras(disco)), ('lingueta', amostras(lingueta))):
        fora = sum(1 for p in pts if not dentro(laco, *p))
        res[nome] = (fora, round(min(dist_laco(p, laco) for p in pts), 3))
    print(nivel, len(laco), 'pontos; cruzamentos', cruza(laco), '; (fora, folga mínima mm):', res, flush=True)
    print('  atrás de x = -149:', [(round(x, 2), round(y, 2)) for x, y in laco if x < -149.0], flush=True)
