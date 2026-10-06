# Recorta e amplia um pedaço de um PNG (para olhar de perto). Uso: blender -b -P recorte.py -- <png> x0 y0 x1 y1 escala <saida>
import sys
import bpy
import numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
png, x0, y0, x1, y1, k, saida = a[0], *map(int, a[1:6]), a[6]
img = bpy.data.images.load(png)
w, h = img.size
px = np.empty(w * h * 4, np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)[::-1]  # linhas de cima para baixo
r = px[y0:y1, x0:x1]
r = np.repeat(np.repeat(r, k, 0), k, 1)[::-1]
out = bpy.data.images.new('rec', r.shape[1], r.shape[0], alpha=True)
out.pixels.foreach_set(r.ravel())
out.filepath_raw = saida
out.file_format = 'PNG'
out.save()
