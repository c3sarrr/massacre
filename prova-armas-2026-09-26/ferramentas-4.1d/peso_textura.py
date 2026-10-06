# Onde pesa a textura assada de uma arma: o custo de cada texel pelo resíduo do preditor de gradiente (proxy do WebP sem
# perdas), atribuído às peças e aos materiais pela cobertura de UV do perto. Nada vai para o projeto.
# Uso: blender -b <conferencia>/<arma>.blend --factory-startup -P peso_textura.py -- <arma> <sufixo: n|m|mundo_n|mundo_m>
import os
import sys

import bpy
import numpy as np

ARMA, SUF = sys.argv[sys.argv.index('--') + 1:][:2]
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
caminho = os.path.join(RAIZ, 'assets', 'armas', ARMA, f'{ARMA}_{SUF}.webp')
img = bpy.data.images.load(caminho)
img.colorspace_settings.name = 'Non-Color'
lado = img.size[0]
a = np.empty(lado * lado * 4, np.float32)
img.pixels.foreach_get(a)
px = np.round(a.reshape(lado, lado, 4) * 255).astype(np.int32)
canais = 3 if SUF.endswith('n') else 4
custo = np.zeros((lado, lado), np.float64)
for c in range(canais):
    p = px[..., c]
    esq = np.pad(p, ((0, 0), (1, 0)), mode='edge')[:, :-1]
    cima = np.pad(p, ((1, 0), (0, 0)), mode='edge')[:-1, :]
    diag = np.pad(p, ((1, 0), (1, 0)), mode='edge')[:-1, :-1]
    pred = np.clip(esq + cima - diag, 0, 255)
    r = np.abs(p - pred)
    # o melhor de três preditores (o WebP escolhe por bloco)
    r = np.minimum(r, np.minimum(np.abs(p - esq), np.abs(p - cima)))
    custo += np.log2(1.0 + r)
print('textura', caminho, lado, 'bytes', os.path.getsize(caminho), 'custo total (bits proxy)', round(custo.sum()))

colecao = 'perto' if not SUF.startswith('mundo') else 'mundo'
dono = np.full((lado, lado), -1, np.int32)
nomes = []
for ob in bpy.data.collections[colecao].objects:
    if ob.type != 'MESH':
        continue
    me = ob.data
    uv = me.uv_layers.active.data
    me.calc_loop_triangles()
    mats = [s.material.name if s.material else '?' for s in ob.material_slots]
    for tri in me.loop_triangles:
        chave = f'{ob.name} | {mats[tri.material_index] if tri.material_index < len(mats) else "?"}'
        if chave not in nomes:
            nomes.append(chave)
        k = nomes.index(chave)
        pts = np.array([uv[l].uv[:] for l in tri.loops]) * lado
        x0, y0 = np.floor(pts.min(0)).astype(int)
        x1, y1 = np.ceil(pts.max(0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, lado), min(y1, lado)
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
        sub = dono[y0:y1, x0:x1]
        sub[dentro] = k
total = custo.sum()
linhas = []
for k, nome in enumerate(nomes):
    m = dono == k
    linhas.append((custo[m].sum(), m.sum(), nome))
fundo = dono < 0
linhas.append((custo[fundo].sum(), fundo.sum(), '(fora das ilhas: margem e fundo)'))
linhas.sort(reverse=True)
print(f'{"parte":60s} {"custo%":>7s} {"área%":>7s} {"bits/texel":>10s}')
for c, n, nome in linhas[:40]:
    print(f'{nome[:60]:60s} {100 * c / total:7.2f} {100 * n / lado / lado:7.2f} {c / max(n, 1):10.3f}')
# por material
por_mat = {}
for c, n, nome in linhas:
    mat = nome.split(' | ')[-1]
    a0 = por_mat.setdefault(mat, [0.0, 0])
    a0[0] += c
    a0[1] += n
print('por material')
for mat, (c, n) in sorted(por_mat.items(), key=lambda kv: -kv[1][0]):
    print(f'  {mat:30s} {100 * c / total:7.2f} {100 * n / lado / lado:7.2f} {c / max(n, 1):10.3f}')
