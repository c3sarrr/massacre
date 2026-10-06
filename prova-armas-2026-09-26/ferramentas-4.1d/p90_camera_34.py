# A câmera da foto de três quartos da FN (FN P90 LV with Tri Rail Muzzle View.jpg, 2175 x 2063, CC BY 2.0) ajustada a
# pontos de medida conhecida da ficha: a boca, os quatro cantos de cima das pontas do trilho de cima e os dois parafusos
# da coronha (na face de 55 mm). Pinhole (com a focal) por Levenberg-Marquardt, vários pontos de partida.
import numpy as np
P3 = np.array([
    [0.0, 0.0, 0.0],               # A o centro da boca do quebra-chama
    [-0.0347, 0.0106, 0.0928],     # B a frente do trilho de cima, canto de cima, lado esquerdo
    [-0.0347, -0.0106, 0.0928],    # C idem, lado direito
    [-0.206, 0.0106, 0.0938],      # D a traseira do trilho de cima, canto de cima, lado esquerdo
    [-0.206, -0.0106, 0.0938],     # E idem, lado direito
    [-0.4244, 0.0275, 0.0146],     # F o parafuso da coronha da frente (face de 55)
    [-0.4853, 0.0275, 0.0102],     # G o parafuso da coronha de trás
])
P2 = np.array([[177.2, 1475.1], [303.0, 642.6], [153.3, 652.4], [933.0, 311.0], [795.0, 312.0], [1841.9, 495.0], [2046.0, 423.2]])
W, H = 2175, 2063


def rot(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


def projetar(p, X):
    c, r, f = p[:3], p[3:6], p[6]
    R = rot(r)
    Xl = (X - c) @ R
    x = f * Xl[:, 0] / -Xl[:, 2] + W / 2
    y = -f * Xl[:, 1] / -Xl[:, 2] + H / 2
    return np.stack([x, y], 1), Xl[:, 2]


def residuo(p):
    uv, z = projetar(p, P3)
    return np.r_[(uv - P2).ravel(), np.where(z > 0, 1000.0, 0.0)]


def lm(p, res=residuo):
    lam = 1e-2
    for _ in range(500):
        r = res(p)
        J = np.zeros((len(r), len(p)))
        for i in range(len(p)):
            d = np.zeros(len(p)); d[i] = 1e-6 * max(1.0, abs(p[i]))
            J[:, i] = (res(p + d) - r) / d[i]
        A = J.T @ J
        g = J.T @ r
        while True:
            dp = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), g)
            if (res(p + dp) ** 2).sum() < (r ** 2).sum():
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
    if ang < 1e-9:
        return np.zeros(3)
    k = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(ang))
    return k * ang


melhor = None
rng = np.random.default_rng(3)
for _ in range(400):
    d = rng.uniform(0.8, 6.0)
    az = rng.uniform(0, 2 * np.pi)
    el = rng.uniform(-0.3, 1.2)
    c = np.array([-0.25 + d * np.cos(el) * np.cos(az), d * np.cos(el) * np.sin(az), d * np.sin(el)])
    alvo = np.array([-0.25, 0.0, 0.0])
    p0 = np.r_[c, olhar(c, alvo), rng.uniform(2000, 40000)]
    p = lm(p0)
    e = np.sqrt((residuo(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
    if np.isfinite(e) and (melhor is None or e < melhor[0]):
        melhor = (e, p)
e, p = melhor
uv, z = projetar(p, P3)
R = rot(p[3:6])
print('erro rms px', round(e, 2))
print('camera m', np.round(p[:3], 4), 'dist', round(float(np.linalg.norm(p[:3] - np.array([-0.25, 0, 0]))), 3), 'f px', round(p[6], 1))
print('frente', np.round(-R[:, 2], 4), 'cima', np.round(R[:, 1], 4))
fr = -R[:, 2]
print('guinada (do lado esquerdo, graus)', round(float(np.degrees(np.arctan2(-fr[0], -fr[1]))), 2), 'arfagem (graus)', round(float(np.degrees(np.arcsin(-fr[2]))), 2))
for a, b in zip(uv, P2):
    print('  ', np.round(a, 1), b)
np.save(__file__.replace('.py', '.npy'), p)
