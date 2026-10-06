# Pontos do modelo da P90 (mm da ficha: x a boca, y o alto, z = lado, + esquerda) para o ajuste da câmera do ícone.
import bpy
import numpy as np
S = 0.001
def verts(nome):
    ob = bpy.data.objects[nome]
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    M = np.array(ob.matrix_world)
    v = np.array([(M @ np.r_[np.array(p.co), 1.0])[:3] for p in me.vertices]) / S
    return np.c_[v[:, 0], v[:, 2], v[:, 1]]  # x, y (alto), lado
print([o.name for o in bpy.data.collections['perto'].objects])
for nome in ('perto_base', 'perto_rebativel_frente', 'perto_rebativel_tras', 'perto_alavanca'):
    v = verts(nome)
    print(nome, 'x', v[:, 0].min().round(1), v[:, 0].max().round(1), 'y', v[:, 1].min().round(1), v[:, 1].max().round(1), 'lado', v[:, 2].min().round(1), v[:, 2].max().round(1))
b = verts('perto_base')
# as orelhas das miras (na base?) : vértices acima de y = 115
for x0, x1, rot in ((-70, -38, 'frente'), (-200, -168, 'tras')):
    m = (b[:, 0] > x0) & (b[:, 0] < x1) & (b[:, 1] > 110)
    w = b[m]
    if len(w):
        print('orelhas', rot, len(w), 'lado', np.unique(np.round(w[:, 2], 1))[:40])
        for lado_sinal in (1, -1):
            q = w[w[:, 2] * lado_sinal > 0]
            if len(q):
                top = q[q[:, 1] > q[:, 1].max() - 0.6]
                print('  lado', lado_sinal, 'topo y', q[:, 1].max().round(2), 'x do topo', top[:, 0].min().round(2), top[:, 0].max().round(2), 'lado', top[:, 2].min().round(2), top[:, 2].max().round(2))
# o botão da alavanca: a face de fora (lado máximo)
a = verts('perto_alavanca')
f = a[a[:, 2] > a[:, 2].max() - 0.3]
print('alavanca face', a[:, 2].max().round(2), 'centro', f[:, 0].mean().round(2), f[:, 1].mean().round(2), 'x', f[:, 0].min().round(1), f[:, 0].max().round(1), 'y', f[:, 1].min().round(1), f[:, 1].max().round(1))
# a coronha: a face esquerda na altura dos parafusos
for (x, y) in ((-485.3, 10.2), (-424.4, 14.6), (-452.1, -67.0), (-378.3, -59.5), (-295.0, -79.6), (-235.8, -75.7), (-214.7, -27.3), (-141.2, -80.5), (-100.7, -28.1), (-52.5, -29.2)):
    m = (np.abs(b[:, 0] - x) < 4) & (np.abs(b[:, 1] - y) < 4) & (b[:, 2] > 0)
    print('parafuso', (x, y), 'lado máx perto', b[m][:, 2].max().round(2) if m.any() else None)
# o canto de baixo atrás da coronha (lado +)
m = (b[:, 0] < -500) & (b[:, 1] < -70) & (b[:, 2] > 0)
print('canto de baixo atras', b[m][np.argmin(b[m][:, 0] + b[m][:, 1])].round(2) if m.any() else None)
