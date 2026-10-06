# Uma cópia reduzida da textura assada (para olhar) e a cobertura das ilhas de UV do perto por cima. Nada vai para o projeto.
import os, sys
import bpy
import numpy as np
ARMA, SUF, LADO = sys.argv[sys.argv.index('--') + 1:][:3]
LADO = int(LADO)
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textura')
os.makedirs(SAIDA, exist_ok=True)
img = bpy.data.images.load(os.path.join(RAIZ, 'assets', 'armas', ARMA, f'{ARMA}_{SUF}.webp'))
img.colorspace_settings.name = 'Non-Color'
lado = img.size[0]
a = np.empty(lado * lado * 4, np.float32)
img.pixels.foreach_get(a)
a = a.reshape(lado, lado, 4)
f = lado // LADO
red = a.reshape(LADO, f, LADO, f, 4).mean((1, 3))
red[..., 3] = 1.0
out = bpy.data.images.new('red', LADO, LADO, alpha=True)
out.colorspace_settings.name = 'Non-Color'
out.pixels.foreach_set(red.ravel())
out.filepath_raw = os.path.join(SAIDA, f'{ARMA}_{SUF}_{LADO}.png')
out.file_format = 'PNG'
out.save()
# cobertura das ilhas (branco) em cima do cinza
cob = np.zeros((LADO, LADO), np.float32)
for ob in bpy.data.collections['perto' if not SUF.startswith('mundo') else 'mundo'].objects:
    if ob.type != 'MESH':
        continue
    me = ob.data
    uv = me.uv_layers.active.data
    me.calc_loop_triangles()
    for tri in me.loop_triangles:
        pts = np.array([uv[l].uv[:] for l in tri.loops]) * LADO
        x0, y0 = np.floor(pts.min(0)).astype(int); x1, y1 = np.ceil(pts.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, LADO), min(y1, LADO)
        if x1 <= x0 or y1 <= y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        (ax, ay), (bx, by), (cx, cy) = pts
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-12:
            continue
        l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / d
        l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / d
        dentro = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
        cob[y0:y1, x0:x1][dentro] = 1.0
print('cobertura', cob.mean())
mask = np.stack([cob, cob, cob, np.ones_like(cob)], 2)
out2 = bpy.data.images.new('cob', LADO, LADO, alpha=True)
out2.colorspace_settings.name = 'Non-Color'
out2.pixels.foreach_set(mask.ravel())
out2.filepath_raw = os.path.join(SAIDA, f'{ARMA}_{SUF}_cob_{LADO}.png')
out2.file_format = 'PNG'
out2.save()
