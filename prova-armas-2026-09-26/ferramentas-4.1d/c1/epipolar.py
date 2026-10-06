# As retas epipolares entre as duas imagens do CS2 (o ícone e o quadro do vídeo): para cada ponto marcado numa imagem, o
# raio da câmera dela cortado nos planos de lado de LADO_MIN a LADO_MAX e projetado na outra, com as marcas do lado a cada
# 5 mm. Serve para achar o mesmo canto na outra imagem (o canto fica sobre a reta) e triangular. Só números nossos.
#   python epipolar.py <origem> <destino> <saida.json> "nome:u,v" ["nome:u,v" ...]
#   python epipolar.py triangular "nome:icone_u,icone_v:video_u,video_v" [...]
import json, sys
import numpy as np
from cameras import projetar, S
from volta import plano, triangular, CAMS

LADO_MIN, LADO_MAX = -25.0, 45.0
CORES = ['#ff00ff', '#00ffff', '#ffff00', '#ff8800', '#00ff00', '#ff4444', '#8888ff', '#ffffff']


def projetar_cam(cam, pts):
    c = CAMS[cam]
    X = np.array([[x * S, l * S, a * S] for x, a, l in pts])
    uv, _ = projetar(np.array(c['p']), X, c['W'], c['H'])
    return uv


def reta(origem, destino, u, v):
    pts, marcas = [], []
    for k, lado in enumerate(np.arange(LADO_MIN, LADO_MAX + 0.01, 1.0)):
        x, a = plano(origem, u, v, lado)
        pts.append((x, a, lado))
    uv = projetar_cam(destino, pts)
    for (x, a, lado), (uu, vv) in zip(pts, uv):
        if abs(lado % 5) < 1e-6:
            marcas.append([round(float(uu), 2), round(float(vv), 2), f'{lado:+.0f}'])
    return [[round(float(uu), 2), round(float(vv), 2)] for uu, vv in uv], marcas


if __name__ == '__main__':
    if sys.argv[1] == 'triangular':
        for arg in sys.argv[2:]:
            nome, a, b = arg.split(':')
            iu, iv = map(float, a.split(','))
            vu, vv = map(float, b.split(','))
            (x, alto, lado), dist = triangular([('icone', iu, iv), ('video', vu, vv)])
            pi = projetar_cam('icone', [(x, alto, lado)])[0]
            pv = projetar_cam('video', [(x, alto, lado)])[0]
            print(f'{nome:28s} x {x:8.1f}  alto {alto:7.1f}  lado {lado:6.1f}   desvio dos raios {dist[0]:.2f} / {dist[1]:.2f} mm'
                  f'   resíduo px ícone {np.hypot(*(pi - [iu, iv])):.2f} vídeo {np.hypot(*(pv - [vu, vv])):.2f}')
        sys.exit(0)
    origem, destino, saida = sys.argv[1], sys.argv[2], sys.argv[3]
    out = {'linhas': [], 'pontos': []}
    for k, arg in enumerate(sys.argv[4:]):
        nome, uv = arg.split(':')
        u, v = map(float, uv.split(','))
        cor = CORES[k % len(CORES)]
        pts, marcas = reta(origem, destino, u, v)
        out['linhas'].append({'cor': cor, 'pts': pts, 'fechar': False, 'nome': nome})
        for uu, vv, rot in marcas:
            out['pontos'].append([uu, vv, f'{nome} {rot}', cor])
    json.dump(out, open(saida, 'w'), ensure_ascii=False)
    print('ok', saida)
