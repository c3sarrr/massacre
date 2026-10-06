# A curva do erro dos parafusos com a focal presa (ícone: os nove parafusos; vídeo: os sete), e a altura que cada câmera
# dá para a orelha da mira da frente (o canto de cima da frente da orelha de perto) com x e lado fixos.
import json, sys
import numpy as np
from cameras import rot, S, projetar, olhar
import runpy
def ajustar_f(pts, W, H, f, p0):
    P3 = np.array([[x * S, l * S, y * S] for (x, y, l), _ in pts]); P2 = np.array([uv for _, uv in pts])
    def res(q):
        p = np.r_[q, f]; uv, z = projetar(p, P3, W, H)
        return np.r_[(uv - P2).ravel(), np.where(z > 0, 1000.0, 0.0)]
    q = np.array(p0[:6], float); lam = 1e-2
    for _ in range(400):
        r = res(q); J = np.zeros((len(r), 6))
        for i in range(6):
            d = np.zeros(6); d[i] = 1e-7 * max(1.0, abs(q[i])); J[:, i] = (res(q + d) - r) / d[i]
        A, g = J.T @ J, J.T @ r
        ok = False
        while lam < 1e9:
            dq = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            if (res(q + dq) ** 2).sum() < (r ** 2).sum(): q = q + dq; lam = max(lam / 3, 1e-9); ok = True; break
            lam *= 4
        if not ok: break
    e = np.sqrt((res(q)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
    return np.r_[q, f], e
def altura(p, W, H, u, v, x):
    R = rot(p[3:6]); C = p[:3]
    d = R @ np.array([(u - W / 2) / p[6], -(v - H / 2) / p[6], -1.0])
    t = (x * S - C[0]) / d[0]; X = C + t * d
    return X[2] / S, X[1] / S
ic = runpy.run_path('pnp_icone9.py', run_name='lib')['PTS']
vi = runpy.run_path('pnp_video.py', run_name='lib')['PTS'][2:]
cams = json.load(open('cameras.json'))
p_ic = np.array(json.load(open('camera_icone9.json'))['p']); p_vi = np.array(cams['video']['p'])
print('ícone (9 parafusos), focal presa:')
for f in (950, 1050, 1100, 1160, 1220, 1300, 1400):
    p, e = ajustar_f(ic, 512, 384, f, p_ic)
    a, l = altura(p, 512, 384, 132.2, 48.3, -73.7)
    print(f'  f {f:5d}  rms {e:5.2f} px  distância {np.linalg.norm(p[:3]) / S:6.0f} mm  orelha (x −73,7): alto {a:6.1f} lado {l:5.1f}')
print('vídeo (7 parafusos), focal presa:')
for f in (1000, 1100, 1180, 1244, 1320, 1450):
    p, e = ajustar_f(vi, 1920, 1080, f, p_vi)
    a, l = altura(p, 1920, 1080, 817.5, 443.0, -73.7)
    print(f'  f {f:5d}  rms {e:5.2f} px  distância {np.linalg.norm(p[:3]) / S:6.0f} mm  orelha (x −73,7): alto {a:6.1f} lado {l:5.1f}')
