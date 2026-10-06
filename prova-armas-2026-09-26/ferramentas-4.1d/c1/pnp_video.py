# A câmera de furo do quadro da inspeção do CS2 (PC Gaming Videos, y1NSHUq7WOI, 108,6 s, 1920 x 1080) ajustada por
# Levenberg-Marquardt aos pontos do quadro marcados à mão no navegador sobre o quadro parado (nada gravado): o centro da
# ponta do quebra-chama, o botão esquerdo da alavanca e sete parafusos da face esquerda. Pontos 3D: (x, alto, lado) da
# ficha em mm, o lado da face do nosso modelo (modelo_perto.json).
import json
import numpy as np
S = 0.001
W, H = 1920, 1080
PTS = [
    ((0.0, 0.0, 0.0), (629.3, 635.6)),            # o centro da ponta do quebra-chama
    ((-90.3, -4.7, 21.0), (758.4, 632.2)),        # o botão esquerdo da alavanca (o centro do anel)
    ((-52.5, -29.2, 13.38), (700.6, 683.3)),      # parafuso da frente do lóbulo
    ((-100.7, -28.1, 15.10), (782.6, 694.4)),     # parafuso de trás do lóbulo
    ((-141.2, -80.5, 19.32), (822.9, 807.6)),     # parafuso do pé do lóbulo
    ((-378.3, -59.5, 26.71), (1366.1, 843.0)),    # coronha, embaixo na frente
    ((-424.4, 14.6, 27.5), (1511.0, 669.0)),      # coronha, em cima na frente
    ((-485.3, 10.2, 27.25), (1691.5, 700.7)),     # coronha, em cima atrás
    ((-452.1, -67.0, 26.38), (1580.2, 901.7)),    # coronha, embaixo atrás
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
    for _ in range(400):
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
if __name__ == '__main__':
    melhor = None
    rng = np.random.default_rng(7)
    for _ in range(400):
        c = np.array([rng.uniform(-0.9, 0.2), rng.uniform(0.05, 0.8), rng.uniform(-0.3, 0.4)])
        alvo = np.array([rng.uniform(-0.5, 0.0), 0.0, rng.uniform(-0.08, 0.05)])
        p = lm(np.r_[c, olhar(c, alvo), rng.uniform(500, 3000)])
        e = np.sqrt((residuo(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
        if np.isfinite(e) and (melhor is None or e < melhor[0]):
            melhor = (e, p)
    e, p = melhor
    uv, z = projetar(p, P3)
    R = rot(p[3:6])
    print('erro rms px', round(e, 2), 'f', round(p[6], 1), 'fov horizontal', round(np.degrees(2 * np.arctan(W / 2 / p[6])), 1))
    print('camera mm', np.round(p[:3] / S, 1), 'frente', np.round(-R[:, 2], 4), 'cima', np.round(R[:, 1], 4))
    print('P', json.dumps([float(v) for v in p]))
    for (q, _), a, b in zip(PTS, uv, P2):
        print('  ', q, np.round(a, 1), b, round(float(np.hypot(*(a - b))), 2))
