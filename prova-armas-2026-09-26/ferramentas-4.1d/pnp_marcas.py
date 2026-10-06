# Projeta pontos do modelo pela câmera ajustada (pnp_icone_p90.py) e imprime a lista para as marcas no navegador.
import json, runpy, sys
import numpy as np
g = runpy.run_path('pnp_icone_p90.py')
p, projetar, S = g['p'], g['projetar'], g['S']
PONTOS = {
    'trilho frente +': (-34.7, 93.8, 10.6), 'trilho frente -': (-34.7, 93.8, -10.6),
    'trilho tras +': (-207.0, 93.8, 10.6), 'trilho tras -': (-207.0, 93.8, -10.6),
    'mira F topo frente +': (-46.06, 130.0, 8.2), 'mira F topo tras +': (-60.74, 130.0, 8.2),
    'mira T topo frente +': (-175.92, 129.3, 10.4), 'mira T topo tras +': (-183.5, 129.3, 10.4),
    'ponte frente topo': (-34.5, 91.8, 15.0), 'ponte pilar baixo': (-45.2, 10.9, 15.0),
    'coronha topo tras +': (-503.0, 39.8, 27.5), 'coronha baixo tras +': (-503.86, -78.84, 16.13),
    'carregador topo frente': (-92.7, 37.3, 22.5), 'carregador topo tras': (-372.0, 38.4, 22.5),
    'aba frente baixo': (-48.2, -63.0, 12.0), 'lobulo pe': (-153.0, -102.0, 15.0), 'punho pe': (-283.0, -101.2, 18.0),
    'oval frente': (-233.2, -36.0, 20.0), 'oval tras': (-302.2, -43.7, 21.0),
    'abertura frente': (-122.0, -47.2, 17.0), 'abertura tras': (-162.7, -38.0, 18.0),
}
out = []
for nome, (x, y, l) in PONTOS.items():
    uv, _ = projetar(p, np.array([[x * S, l * S, y * S]]))
    out.append([nome, round(float(uv[0, 0]), 1), round(float(uv[0, 1]), 1)])
print(json.dumps(out, ensure_ascii=False))
