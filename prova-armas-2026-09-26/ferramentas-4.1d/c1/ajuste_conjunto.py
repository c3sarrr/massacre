# O ajuste conjunto (bundle adjustment) das duas câmeras do CS2 da C1: o ícone (que é o mesmo das peles: IoU 1,0000) e o
# quadro de 108,6 s do vídeo de inspeção. Os parafusos da face esquerda ficam presos nas posições da ficha (o quadro da
# P90 real, o nosso); os pontos de cima marcados nas duas imagens (as orelhas da mira da frente, as fendas do trilho, o
# botão da alavanca e os que vierem) ficam livres, e as duas câmeras se acertam juntas, o ícone com o ponto principal
# livre (o render do ícone pode ser um recorte). Só números; nada do jogo.
#   python ajuste_conjunto.py [--fixo-centro] [--sem pontos]
import json, sys
import numpy as np
from cameras import rot, S, projetar
import runpy

ICONE_PARAFUSOS = runpy.run_path('pnp_icone9.py', run_name='lib')['PTS']
VIDEO_PARAFUSOS = runpy.run_path('pnp_video.py', run_name='lib')['PTS'][2:]
# os pontos marcados nas duas (nome, (u, v) no ícone, (u, v) no vídeo, peso)
PARES = json.load(open('pares.json', encoding='utf-8')) if len(sys.argv) < 2 or '--sem' not in sys.argv else []
SIG_I, SIG_V = 0.6, 1.2  # o ruído da marcação (px)


def proj(p, X, W, H, pp=(0.0, 0.0)):
    uv, z = projetar(p, X, W, H)
    return uv + np.array(pp), z


def montar(ci, cv, pontos):
    return np.r_[ci, cv, np.array(pontos).ravel()]


def separar(q, n):
    ci, cv = q[:9], q[9:16]
    return ci, cv, q[16:].reshape(n, 3)


def residuos(q, n, fixo_centro):
    ci, cv, Xp = separar(q, n)
    pp = (0.0, 0.0) if fixo_centro else (ci[7], ci[8])
    r = []
    P3 = np.array([[x * S, l * S, a * S] for (x, a, l), _ in ICONE_PARAFUSOS])
    uv, _ = proj(ci[:7], P3, 512, 384, pp)
    r.append(((uv - np.array([m for _, m in ICONE_PARAFUSOS])) / SIG_I).ravel())
    P3 = np.array([[x * S, l * S, a * S] for (x, a, l), _ in VIDEO_PARAFUSOS])
    uv, _ = proj(cv, P3, 1920, 1080)
    r.append(((uv - np.array([m for _, m in VIDEO_PARAFUSOS])) / SIG_V).ravel())
    for k, par in enumerate(PARES):
        X = Xp[k:k + 1] * S
        w = par.get('peso', 1.0)
        uv, _ = proj(ci[:7], X, 512, 384, pp)
        r.append((uv[0] - par['icone']) / SIG_I * w)
        uv, _ = proj(cv, X, 1920, 1080)
        r.append((uv[0] - par['video']) / SIG_V * w)
    return np.concatenate(r)


def lm(q, n, fixo_centro, iters=200):
    lam = 1e-3
    for _ in range(iters):
        r = residuos(q, n, fixo_centro)
        J = np.zeros((len(r), len(q)))
        for i in range(len(q)):
            d = np.zeros(len(q)); d[i] = 1e-7 * max(1.0, abs(q[i])) if i < 16 else 1e-4
            J[:, i] = (residuos(q + d, n, fixo_centro) - r) / d[i]
        if fixo_centro:
            J[:, 7:9] = 0
        A, g = J.T @ J, J.T @ r
        ok = False
        while lam < 1e10:
            dq = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            if (residuos(q + dq, n, fixo_centro) ** 2).sum() < (r ** 2).sum():
                q = q + dq; lam = max(lam / 3, 1e-10); ok = True; break
            lam *= 4
        if not ok:
            break
    return q


def triangular(ci, cv, ui, uvv, pp):
    def raio(p, W, H, u, v, pp=(0, 0)):
        R = rot(p[3:6]); d = R @ np.array([(u - pp[0] - W / 2) / p[6], -(v - pp[1] - H / 2) / p[6], -1.0])
        return p[:3], d / np.linalg.norm(d)
    rs = [raio(ci[:7], 512, 384, *ui, pp), raio(cv, 1920, 1080, *uvv)]
    A, b = np.zeros((3, 3)), np.zeros(3)
    for C, d in rs:
        M = np.eye(3) - np.outer(d, d); A += M; b += M @ C
    X = np.linalg.solve(A, b)
    return np.array([X[0], X[2], X[1]]) / S  # (x, alto, lado)


if __name__ == '__main__':
    fixo = '--fixo-centro' in sys.argv
    cams = json.load(open('cameras.json'))
    ci0 = np.r_[json.load(open('camera_icone9.json'))['p'], 0.0, 0.0]
    cv0 = np.array(cams['video']['p'])
    pontos0 = [triangular(ci0, cv0, par['icone'], par['video'], (0, 0)) for par in PARES]
    pontos0 = [(x, a, l) for x, a, l in pontos0]
    # os pontos em mm na ordem (x, alto, lado) — dentro do vetor ficam em mm, convertidos na projeção
    q0 = np.r_[ci0, cv0, np.array([[x, l, a] for x, a, l in pontos0]).ravel()] if PARES else np.r_[ci0, cv0]
    # nota: Xp guarda (x, lado, alto) em mm, a ordem do Blender
    q = lm(q0, len(PARES), fixo)
    ci, cv, Xp = separar(q, len(PARES))
    r = residuos(q, len(PARES), fixo)
    ni, nv = len(ICONE_PARAFUSOS), len(VIDEO_PARAFUSOS)
    ri = r[:2 * ni].reshape(-1, 2) * SIG_I; rv = r[2 * ni:2 * ni + 2 * nv].reshape(-1, 2) * SIG_V
    print(f'ícone: f {ci[6]:.1f}  câmera mm {np.round(ci[:3] / S)}  ponto principal ({ci[7]:+.1f}, {ci[8]:+.1f})  parafusos rms {np.sqrt((ri ** 2).sum(1).mean()):.2f} px')
    print(f'vídeo: f {cv[6]:.1f}  câmera mm {np.round(cv[:3] / S)}  parafusos rms {np.sqrt((rv ** 2).sum(1).mean()):.2f} px')
    for k, par in enumerate(PARES):
        x, l, a = Xp[k]
        rr = r[2 * ni + 2 * nv + 4 * k: 2 * ni + 2 * nv + 4 * k + 4]
        w = par.get('peso', 1.0)
        print(f'  {par["nome"]:34s} x {x:7.1f}  alto {a:6.1f}  lado {l:5.1f}   resíduo ícone {np.hypot(*rr[:2]) * SIG_I / w:.2f} px  vídeo {np.hypot(*rr[2:]) * SIG_V / w:.2f} px')
    json.dump({'icone': {'p': [float(v) for v in ci[:7]], 'pp': [float(ci[7]), float(ci[8])], 'W': 512, 'H': 384},
               'video': {'p': [float(v) for v in cv], 'W': 1920, 'H': 1080},
               'pontos': {par['nome']: [float(Xp[k][0]), float(Xp[k][2]), float(Xp[k][1])] for k, par in enumerate(PARES)}},
              open('conjunto.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
