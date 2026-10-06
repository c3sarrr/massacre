# Quanto pesa a margem das ilhas no WebP sem perdas: regrava a textura assada como está e com a margem refeita de outros
# jeitos (só a margem muda; as ilhas ficam iguais). Nada vai para o projeto.
# Uso: blender -b <conferencia>/<arma>.blend --factory-startup -P margem_teste.py -- <arma> <sufixo n|m> <margem px>
import os
import sys

import bpy
import numpy as np

ARMA, SUF, MARGEM = sys.argv[sys.argv.index('--') + 1:][:3]
MARGEM = int(MARGEM)
RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d'
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'margem')
os.makedirs(SAIDA, exist_ok=True)
img = bpy.data.images.load(os.path.join(RAIZ, 'assets', 'armas', ARMA, f'{ARMA}_{SUF}.webp'))
img.colorspace_settings.name = 'Non-Color'
lado = img.size[0]
a = np.empty(lado * lado * 4, np.float32)
img.pixels.foreach_get(a)
a = a.reshape(lado, lado, 4)
fundo = {'n': (0.5, 0.5, 1.0, 1.0), 'm': None}[SUF]


def cobertura(colecao):
    cob = np.zeros((lado, lado), bool)
    for ob in bpy.data.collections[colecao].objects:
        if ob.type != 'MESH':
            continue
        me = ob.data
        uv = me.uv_layers.active.data
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
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
            cob[y0:y1, x0:x1] |= dentro
    return cob


def gravar(nome, rgba):
    im = bpy.data.images.new(nome, lado, lado, alpha=True, float_buffer=False)
    im.colorspace_settings.name = 'Non-Color'
    im.alpha_mode = 'STRAIGHT'
    im.pixels.foreach_set(np.clip(rgba, 0, 1).astype(np.float32).ravel())
    caminho = os.path.join(SAIDA, f'{nome}.webp')
    im.filepath_raw = caminho
    im.file_format = 'WEBP'
    im.save(filepath=caminho, quality=100)
    bpy.data.images.remove(im)
    return os.path.getsize(caminho)


def media(img, cob, passos):
    """o _estender do assar.py: a média dos vizinhos cobertos, `passos` vezes"""
    img, cob = img.copy(), cob.copy()
    for _ in range(passos):
        soma = np.zeros_like(img)
        conta = np.zeros(cob.shape, np.float32)
        cp = np.pad(cob, 1)
        ip = np.pad(img, ((1, 1), (1, 1), (0, 0)))
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                if dy == 1 and dx == 1:
                    continue
                c = cp[dy:dy + cob.shape[0], dx:dx + cob.shape[1]]
                soma += ip[dy:dy + cob.shape[0], dx:dx + cob.shape[1]] * c[..., None]
                conta += c
        novo = ~cob & (conta > 0)
        img[novo] = soma[novo] / conta[novo][:, None]
        cob |= novo
    return img


def vizinho(img, cob, passos):
    """a margem pelo texel coberto mais perto: a cada passo, o texel novo copia o primeiro vizinho coberto na ordem
    (os 4 de lado antes das diagonais), sem média"""
    img, cob = img.copy(), cob.copy()
    ordem = [(0, 1), (1, 0), (1, 2), (2, 1), (0, 0), (0, 2), (2, 0), (2, 2)]
    for _ in range(passos):
        cp = np.pad(cob, 1)
        ip = np.pad(img, ((1, 1), (1, 1), (0, 0)))
        novo_img = img.copy()
        feito = cob.copy()
        for dy, dx in ordem:
            c = cp[dy:dy + cob.shape[0], dx:dx + cob.shape[1]] & ~feito
            novo_img[c] = ip[dy:dy + cob.shape[0], dx:dx + cob.shape[1]][c]
            feito |= c
        img, cob = novo_img, feito
    return img


cob = cobertura('perto')
print('cobertura', round(cob.mean(), 4))
base = a.copy()
# o fundo onde nem a margem chega: o do assar (no _m, cada canal com o seu neutro: o valor mais comum fora)
if fundo is None:
    fora = ~media(np.zeros((lado, lado, 1), np.float32), cob, MARGEM).astype(bool)[..., 0]
fora_margem = ~np.pad(cob, 0)
print('original', os.path.getsize(os.path.join(RAIZ, 'assets', 'armas', ARMA, f'{ARMA}_{SUF}.webp')))
print('regravada', gravar(f'{ARMA}_{SUF}_regravada', base))
# a margem refeita: o fundo de volta onde não é ilha e a extensão de novo
alcance = media(cob[..., None].astype(np.float32), cob, MARGEM)[..., 0] > 0
neutro = np.array(fundo if fundo else [np.median(base[~alcance][:, c]) for c in range(4)], np.float32)
limpa = base.copy()
limpa[~cob] = neutro
print('neutro', neutro)
print('media', MARGEM, gravar(f'{ARMA}_{SUF}_media{MARGEM}', media(limpa, cob, MARGEM)))
print('vizinho', MARGEM, gravar(f'{ARMA}_{SUF}_vizinho{MARGEM}', vizinho(limpa, cob, MARGEM)))
print('sem margem', gravar(f'{ARMA}_{SUF}_sem', limpa))
