# O chute da câmera da W_p90 com a lente fixa (o PnP de cinco pontos grossos não determina a lente sozinho).
import json, runpy
import numpy as np
g = runpy.run_path('pnp_w_chute.py', run_name='lib')  # reusa as funções (roda o ajuste livre também)
P3, P2, projetar, olhar, W, H = g['P3'], g['P2'], g['projetar'], g['olhar'], g['W'], g['H']
def res_f(q, f):
    p = np.r_[q, f]
    uv, z = projetar(p, P3)
    return np.r_[(uv - P2).ravel(), np.where(z > 0, 1000.0, 0.0)]
def lm(q, f):
    lam = 1e-2
    for _ in range(300):
        r = res_f(q, f)
        J = np.zeros((len(r), 6))
        for i in range(6):
            d = np.zeros(6); d[i] = 1e-6 * max(1.0, abs(q[i]))
            J[:, i] = (res_f(q + d, f) - r) / d[i]
        A, gg = J.T @ J, J.T @ r
        while True:
            dq = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), gg)
            if (res_f(q + dq, f) ** 2).sum() < (r ** 2).sum():
                q = q + dq; lam = max(lam / 3, 1e-9); break
            lam *= 4
            if lam > 1e9:
                return q
    return q
rng = np.random.default_rng(5)
for f in (500, 800, 1200, 1800, 2700, 4000):
    melhor = None
    for _ in range(150):
        c = np.array([rng.uniform(-0.9, 0.4), rng.uniform(-3.0, -0.2), rng.uniform(0.0, 1.5)])
        alvo = np.array([rng.uniform(-0.4, -0.1), 0.0, rng.uniform(-0.05, 0.05)])
        q = lm(np.r_[c, olhar(c, alvo)], f)
        e = np.sqrt((res_f(q, f)[:10] ** 2).reshape(-1, 2).sum(1).mean())
        if np.isfinite(e) and (melhor is None or e < melhor[0]):
            melhor = (e, q)
    e, q = melhor
    print(f, 'erro', round(e, 2), 'P', json.dumps([round(float(v), 6) for v in np.r_[q, f]]))
