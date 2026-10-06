import runpy, json
import numpy as np
g = runpy.run_path('pnp_video.py', run_name='lib')
PTS, S = g['PTS'], g['S']
def ajustar(idx, sem_f=None, sementes=250):
    P3 = np.array([[PTS[i][0][0] * S, PTS[i][0][2] * S, PTS[i][0][1] * S] for i in idx])
    P2 = np.array([PTS[i][1] for i in idx])
    rot, W, H = g['rot'], g['W'], g['H']
    def proj(p, X):
        c, r, f = p[:3], p[3:6], p[6]
        Xl = (X - c) @ rot(r)
        return np.stack([f * Xl[:, 0] / -Xl[:, 2] + W / 2, -f * Xl[:, 1] / -Xl[:, 2] + H / 2], 1), Xl[:, 2]
    def res(p):
        uv, z = proj(p, P3)
        return np.r_[(uv - P2).ravel(), np.where(z > 0, 1000.0, 0.0)]
    def lm(p):
        lam = 1e-2
        for _ in range(300):
            r = res(p)
            J = np.zeros((len(r), len(p)))
            for i in range(len(p)):
                d = np.zeros(len(p)); d[i] = 1e-6 * max(1.0, abs(p[i]))
                J[:, i] = (res(p + d) - r) / d[i]
            A, gg = J.T @ J, J.T @ r
            while True:
                dp = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), gg)
                if (res(p + dp) ** 2).sum() < (r ** 2).sum():
                    p = p + dp; lam = max(lam / 3, 1e-9); break
                lam *= 4
                if lam > 1e9:
                    return p
        return p
    melhor = None
    rng = np.random.default_rng(11)
    for _ in range(sementes):
        c = np.array([rng.uniform(-0.9, 0.2), rng.uniform(0.05, 0.8), rng.uniform(-0.3, 0.4)])
        alvo = np.array([rng.uniform(-0.5, 0.0), 0.0, rng.uniform(-0.08, 0.05)])
        p = lm(np.r_[c, g['olhar'](c, alvo), rng.uniform(500, 3000)])
        e = np.sqrt((res(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
        if np.isfinite(e) and (melhor is None or e < melhor[0]):
            melhor = (e, p)
    e, p = melhor
    # os pontos de fora do ajuste
    todos = np.array([[q[0] * S, q[2] * S, q[1] * S] for q, _ in PTS])
    uv, _ = proj(p, todos)
    return e, p, [round(float(np.hypot(*(uv[i] - np.array(PTS[i][1])))), 1) for i in range(len(PTS))]
for nome, idx in [('só parafusos', [2, 3, 4, 5, 6, 7, 8]), ('sem a boca', [1, 2, 3, 4, 5, 6, 7, 8]), ('sem a alavanca', [0, 2, 3, 4, 5, 6, 7, 8])]:
    e, p, r = ajustar(idx)
    print(nome, 'rms', round(e, 2), 'f', round(p[6]), 'resíduos', r)
