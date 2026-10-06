import runpy
import numpy as np
g = runpy.run_path('pnp_icone_p90.py')
p, rot, projetar, P3, P2, S, W = g['p'], g['rot'], g['projetar'], g['P3'], g['P2'], g['S'], g['W']
R = rot(p[3:6]); C = p[:3]
F = -R[:, 2]; U = R[:, 1]
c = np.array([(-505.0 + 0.0) / 2 * S, 0.0, (-102.0 + 130.0) / 2 * S])
D = float((c - C) @ F)
M = C + F * D - c
uv, _ = projetar(p, P3)
e = np.sqrt(((uv - P2) ** 2).sum(1))
print('erro medio px', round(e.mean(), 2), 'max', round(e.max(), 2), 'rms', round(np.sqrt((e ** 2).mean()), 2))
print("'frente':", tuple(np.round(F, 4)), "'cima':", tuple(np.round(U, 4)), "'lente':", round(p[6] * 36 / W, 1))
print("'distancia':", round(D, 4), "'mira':", tuple(np.round(M, 4)), "'comprimento': 0.505")
print('camera', np.round(C, 4), 'elevacao graus', round(np.degrees(np.arcsin(F[2])), 2), 'guinada', round(np.degrees(np.arctan2(-F[1], -F[0])), 1))
# conferência: a posição que o conferir.py monta
pos = c + M - F * D
print('pos', np.round(pos, 4), 'igual a C', np.allclose(pos, C, atol=1e-4))
