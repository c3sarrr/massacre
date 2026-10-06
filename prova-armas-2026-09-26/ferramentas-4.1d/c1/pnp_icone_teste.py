# O ícone da P90: a câmera só pelos parafusos e a previsão da boca e do botão da alavanca.
import runpy
import numpy as np
g = runpy.run_path('../pnp_icone_p90.py', run_name='lib')
PTS, S, W, H, rot = g['PTS'], g['S'], g['W'], g['H'], g['rot']
def ajustar(idx, sementes=250):
    P3 = np.array([[PTS[i][0][0] * S, PTS[i][0][2] * S, PTS[i][0][1] * S] for i in idx])
    P2 = np.array([PTS[i][1] for i in idx])
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
    rng = np.random.default_rng(1)
    for _ in range(sementes):
        c = np.array([rng.uniform(-0.6, 1.5), rng.uniform(0.3, 2.5), rng.uniform(-1.0, 1.0)])
        alvo = np.array([rng.uniform(-0.9, -0.3), 0.0, rng.uniform(-0.1, 0.1)])
        p = lm(np.r_[c, g['olhar'](c, alvo), rng.uniform(300, 1500)])
        e = np.sqrt((res(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
        if np.isfinite(e) and (melhor is None or e < melhor[0]):
            melhor = (e, p)
    e, p = melhor
    todos = np.array([[q[0] * S, q[2] * S, q[1] * S] for q, _ in PTS])
    uv, _ = proj(p, todos)
    return e, p, [(round(float(uv[i][0] - PTS[i][1][0]), 1), round(float(uv[i][1] - PTS[i][1][1]), 1)) for i in range(len(PTS))]
for nome, idx in [('todos', list(range(9))), ('só parafusos', [2, 3, 4, 5, 6, 7, 8])]:
    e, p, r = ajustar(idx)
    print(nome, 'rms', round(e, 2), 'f', round(p[6]), 'resíduos (previsto - marcado)', r)
