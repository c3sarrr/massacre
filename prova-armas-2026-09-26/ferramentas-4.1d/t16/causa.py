"""Para as arestas que mais perderam chanfro numa peça (o despejo do perdas.py): os defeitos do começo a até `raio` mm
dela, por tipo, com a distância e a posição ao longo da aresta (0 = uma ponta, 1 = a outra)."""
import json, sys
import numpy as np
d = json.load(open(sys.argv[1], encoding='utf-8'))
raio = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
L = d['largura']
pts, tipos = [], []
for k, v in d['defeitos'].items():
    for p in v:
        pts.append(p); tipos.append(k)
pts = np.array(pts) if pts else np.zeros((0, 3))
ar = sorted(d['arestas'], key=lambda e: -(e['antes'] - e['depois']) * np.linalg.norm(np.subtract(*e['pontas'])))
print(d['peca'], 'largura', L, 'defeitos', len(pts), {k: len(v) for k, v in d['defeitos'].items()})
for e in ar[:8]:
    a, b = np.array(e['pontas'][0]), np.array(e['pontas'][1])
    ab = b - a
    comp = np.linalg.norm(ab)
    t = np.clip(((pts - a) @ ab) / (comp * comp), 0, 1) if len(pts) else np.zeros(0)
    dist = np.linalg.norm(pts - (a + t[:, None] * ab), axis=1) if len(pts) else np.zeros(0)
    perto = np.nonzero(dist <= raio)[0]
    print(f"  aresta {e['pontas'][0]} -> {e['pontas'][1]} ({comp:.1f} mm): {e['antes'] * L:.3f} -> {e['depois'] * L:.3f} mm;"
          f" {len(perto)} defeitos a até {raio} mm")
    por = {}
    for i in perto:
        por.setdefault(tipos[i], []).append((round(float(dist[i]), 2), round(float(t[i]), 3), pts[i].round(2).tolist()))
    for k, v in por.items():
        v.sort()
        print(f"      {k}: {len(v)}; os mais perto {v[:4]}")
