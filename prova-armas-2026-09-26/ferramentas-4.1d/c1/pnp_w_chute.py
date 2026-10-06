# Chute inicial da câmera da W_p90_csgo.png (968 x 415): o PnP do pnp_icone_p90.py com cinco pontos grossos da silhueta
# (lidos no navegador pelo alfa; nada gravado). Só para partir o ajuste pela silhueta (ajuste.html).
import json, sys
import numpy as np
sys.path.insert(0, '..')
S = 0.001
W, H = 968, 415
PTS = [
    ((0.0, 0.0, 0.0), (958.0, 168.0)),          # o centro da ponta do quebra-chama
    ((-503.0, 39.8, 27.5), (38.0, 159.0)),      # a quina de cima atrás da coronha, lado de longe (esquerdo)
    ((-283.0, -101.2, -18.0), (465.0, 382.0)),  # o pé do punho, lado de perto (direito)
    ((-153.0, -102.0, -15.0), (707.0, 353.0)),  # o pé do lóbulo, lado de perto
    ((-450.0, -79.0, -16.0), (100.0, 393.0)),   # o fundo da coronha, lado de perto
]
P3 = np.array([[x * S, l * S, y * S] for (x, y, l), _ in PTS])
P2 = np.array([uv for _, uv in PTS])
def rot(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K
def projetar(p, X):
    c, r, f = p[:3], p[3:6], p[6]
    Xl = (X - c) @ rot(r)
    return np.stack([f * Xl[:, 0] / -Xl[:, 2] + W / 2, -f * Xl[:, 1] / -Xl[:, 2] + H / 2], 1), Xl[:, 2]
def residuo(p):
    uv, z = projetar(p, P3)
    return np.r_[(uv - P2).ravel(), np.where(z > 0, 1000.0, 0.0)]
def lm(p):
    lam = 1e-2
    for _ in range(300):
        r = residuo(p)
        J = np.zeros((len(r), len(p)))
        for i in range(len(p)):
            d = np.zeros(len(p)); d[i] = 1e-6 * max(1.0, abs(p[i]))
            J[:, i] = (residuo(p + d) - r) / d[i]
        A, g = J.T @ J, J.T @ r
        while True:
            dp = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), g)
            if (residuo(p + dp) ** 2).sum() < (r ** 2).sum():
                p = p + dp; lam = max(lam / 3, 1e-9); break
            lam *= 4
            if lam > 1e9:
                return p
    return p
def olhar(c, alvo, cima=np.array([0, 0, 1.0])):
    f = alvo - c; f /= np.linalg.norm(f)
    x = np.cross(f, cima); x /= np.linalg.norm(x)
    y = np.cross(x, f)
    R = np.stack([x, y, -f], 1)
    ang = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
    k = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(ang))
    return k * ang
melhor = None
rng = np.random.default_rng(3)
for _ in range(400):
    c = np.array([rng.uniform(-0.9, 0.4), rng.uniform(-2.0, -0.2), rng.uniform(0.0, 1.0)])
    alvo = np.array([rng.uniform(-0.4, -0.1), 0.0, rng.uniform(-0.05, 0.05)])
    p = lm(np.r_[c, olhar(c, alvo), rng.uniform(400, 3000)])
    e = np.sqrt((residuo(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
    if np.isfinite(e) and (melhor is None or e < melhor[0]):
        melhor = (e, p)
e, p = melhor
print('erro rms px', round(e, 2), 'f', round(p[6], 1))
print('P', json.dumps([float(v) for v in p]))
uv, _ = projetar(p, P3)
for a, b in zip(uv, P2):
    print('  ', np.round(a, 1), b)
