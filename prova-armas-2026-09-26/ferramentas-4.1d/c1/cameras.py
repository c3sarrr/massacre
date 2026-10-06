# As duas câmeras do CS2 para a correção C1 (plano da 4.1d), ajustadas só nos parafusos da face esquerda do quadro (o
# quadro do CS2 é o da P90 real: os sete parafusos batem a 0,5 px no ícone): o ícone do inventário (512 x 384) e o
# quadro da inspeção de 108,6 s (1920 x 1080). Gravadas em cameras.json (só os parâmetros; nada do jogo).
import json, runpy
import numpy as np
S = 0.001
def rot(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K
def olhar(c, alvo, cima=np.array([0, 0, 1.0])):
    f = alvo - c; f /= np.linalg.norm(f)
    x = np.cross(f, cima); x /= np.linalg.norm(x)
    y = np.cross(x, f)
    R = np.stack([x, y, -f], 1)
    ang = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
    k = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(ang))
    return k * ang
def projetar(p, X, W, H):
    c, r, f = p[:3], p[3:6], p[6]
    Xl = (X - c) @ rot(r)
    return np.stack([f * Xl[:, 0] / -Xl[:, 2] + W / 2, -f * Xl[:, 1] / -Xl[:, 2] + H / 2], 1), Xl[:, 2]
def ajustar(pts, W, H, caixa_c, caixa_alvo, faixa_f, semente=1, sementes=300):
    P3 = np.array([[x * S, l * S, y * S] for (x, y, l), _ in pts])
    P2 = np.array([uv for _, uv in pts])
    def res(p):
        uv, z = projetar(p, P3, W, H)
        return np.r_[(uv - P2).ravel(), np.where(z > 0, 1000.0, 0.0)]
    def lm(p):
        lam = 1e-2
        for _ in range(300):
            r = res(p)
            J = np.zeros((len(r), len(p)))
            for i in range(len(p)):
                d = np.zeros(len(p)); d[i] = 1e-6 * max(1.0, abs(p[i]))
                J[:, i] = (res(p + d) - r) / d[i]
            A, g = J.T @ J, J.T @ r
            while True:
                dp = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), g)
                if (res(p + dp) ** 2).sum() < (r ** 2).sum():
                    p = p + dp; lam = max(lam / 3, 1e-9); break
                lam *= 4
                if lam > 1e9:
                    return p
        return p
    melhor = None
    rng = np.random.default_rng(semente)
    for _ in range(sementes):
        c = np.array([rng.uniform(*caixa_c[0]), rng.uniform(*caixa_c[1]), rng.uniform(*caixa_c[2])])
        alvo = np.array([rng.uniform(*caixa_alvo[0]), 0.0, rng.uniform(*caixa_alvo[1])])
        p = lm(np.r_[c, olhar(c, alvo), rng.uniform(*faixa_f)])
        e = np.sqrt((res(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
        if np.isfinite(e) and (melhor is None or e < melhor[0]):
            melhor = (e, p)
    return melhor
if __name__ == '__main__':
    ic = runpy.run_path('../pnp_icone_p90.py', run_name='lib')['PTS'][2:]
    vi = runpy.run_path('pnp_video.py', run_name='lib')['PTS'][2:]
    e1, p1 = ajustar(ic, 512, 384, ((-0.6, 1.5), (0.3, 2.5), (-1.0, 1.0)), ((-0.9, -0.3), (-0.1, 0.1)), (300, 1500), 1)
    e2, p2 = ajustar(vi, 1920, 1080, ((-0.9, 0.2), (0.05, 0.8), (-0.3, 0.4)), ((-0.5, 0.0), (-0.08, 0.05)), (500, 3000), 11)
    out = {'icone': {'p': [float(v) for v in p1], 'W': 512, 'H': 384, 'rms': float(e1)},
           'video': {'p': [float(v) for v in p2], 'W': 1920, 'H': 1080, 'rms': float(e2), 'tempo': 108.6}}
    json.dump(out, open('cameras.json', 'w'), indent=1)
    for k, v in out.items():
        R = rot(np.array(v['p'][3:6]))
        print(k, 'rms', round(v['rms'], 2), 'f', round(v['p'][6]), 'camera mm', np.round(np.array(v['p'][:3]) / S), 'frente', np.round(-R[:, 2], 3))
