# Volta do pixel do ícone ao plano de lado (Y do Blender = lado) pela câmera ajustada: (x, alto) em mm da ficha.
import runpy
import numpy as np
g = runpy.run_path('pnp_icone_p90.py')
p, rot, S, W, H = g['p'], g['rot'], g['S'], g['W'], g['H']
C, R, f = p[:3], rot(p[3:6]), p[6]
def volta(u, v, lado):
    dl = np.array([(u - W / 2) / f, -(v - H / 2) / f, -1.0])
    d = R @ dl
    t = (lado * S - C[1]) / d[1]
    X = C + t * d
    return round(X[0] / S, 1), round(X[2] / S, 1)
for nome, (u, v), lado in [
    ('trilho, dente', (163, 101), 10.6), ('trilho, dente', (175, 104), 10.6), ('trilho, dente', (184, 106), 10.6),
    ('trilho, dente', (194, 108), 10.6), ('trilho, dente', (203, 110), 10.6),
    ('mira F orelha perto, topo frente', (132, 48), 8.2), ('mira F orelha perto, topo trás', (138, 49), 8.2),
    ('mira F orelha longe, topo', (122, 52), -8.2), ('mira F orelha longe, topo trás', (131, 52), -8.2),
    ('mira T orelha perto, topo frente', (226.5, 70), 10.4), ('mira T orelha perto, topo trás', (235, 70), 10.4),
    ('mira T orelha longe, topo frente', (210, 75), -10.4), ('mira T orelha longe, topo trás', (225, 73), -10.4),
]:
    print(f'{nome:38s} {(u, v)} lado {lado:6.1f} -> x, alto {volta(u, v, lado)}')
