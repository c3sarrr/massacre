# Ajuste de uma câmera de furo aos pontos marcados no ícone do CS2 da AWP (512x384), por Levenberg-Marquardt com
# jacobiano numérico e vários pontos de partida. Pontos 3D no Blender (m): X a boca, Y a esquerda, Z o alto.
import numpy as np
P3 = np.array([
    [0.0, 0.0, 0.0],             # A a boca (centro)
    [-0.1293, 0.0, -0.0293],     # B a ponta da tampa do tubo
    [-0.6522, 0.006, -0.0751],   # C o fundo do guarda-mato, atrás (lado esquerdo)
    [-0.9733, 0.023, -0.1676],   # D o bico da soleira (lado esquerdo)
    [-0.988, 0.022, -0.042],     # E o calcanhar da soleira (lado esquerdo)
    [-0.6297, 0.0, 0.023],       # F o centro do ghost ring
    [-0.042, 0.0, 0.0272],       # G o alto da massa de mira
])
P3_AWP = np.array([
    [0.0, 0.0, 0.0],            # A boca (face do freio)
    [-0.637, 0.0, 0.0553],      # B borda da objetiva
    [-0.796, 0.0, 0.0923],      # C topo da torre de elevação
    [-0.9766, 0.026, -0.0703],  # D buraco do polegar (face esquerda)
    [-1.213, 0.023, -0.1276],   # E pé da soleira (canto esquerdo)
    [-0.938, 0.017, -0.1374],   # F pé do punho
    [-0.9534, 0.0, 0.0553],     # G borda da ocular
])
P2 = np.array([[17.03, 94.31], [133.55, 157.0], [393.5, 241.8], [484.45, 308.35], [489.2, 241.3], [384.4, 171.3], [57.97, 71.97]])
P2_AWP = np.array([[28.4, 99.9], [340.2, 125.8], [387.7, 109.7], [438.3, 226.7], [489.9, 268.1], [428.0, 269.0], [435.6, 147.7]])
W, H = 512, 384

def rot(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K

def projetar(p, X):
    # p: [cx, cy, cz, rx, ry, rz, f]; câmera olhando por -Z local (Blender), Y local para cima
    c, r, f = p[:3], p[3:6], p[6]
    R = rot(r)                  # do local da câmera para o mundo
    Xl = (X - c) @ R            # mundo -> local
    x = f * Xl[:, 0] / -Xl[:, 2] + W / 2
    y = -f * Xl[:, 1] / -Xl[:, 2] + H / 2
    return np.stack([x, y], 1), Xl[:, 2]

def residuo(p):
    uv, z = projetar(p, P3)
    r = (uv - P2).ravel()
    pen = np.where(z > 0, 1000.0, 0.0)  # pontos atrás da câmera
    return np.r_[r, pen]

def lm(p):
    lam = 1e-2
    for _ in range(400):
        r = residuo(p)
        J = np.zeros((len(r), len(p)))
        for i in range(len(p)):
            d = np.zeros(len(p)); d[i] = 1e-6 * max(1.0, abs(p[i]))
            J[:, i] = (residuo(p + d) - r) / d[i]
        A = J.T @ J
        g = J.T @ r
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
    R = np.stack([x, y, -f], 1)  # colunas: eixos locais no mundo
    # matriz de rotação -> eixo-ângulo
    ang = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
    if ang < 1e-9:
        return np.zeros(3)
    k = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(ang))
    return k * ang

melhor = None
rng = np.random.default_rng(1)
for _ in range(300):
    c = np.array([rng.uniform(-0.6, 1.5), rng.uniform(0.3, 2.5), rng.uniform(-1.0, 1.0)])
    alvo = np.array([rng.uniform(-0.9, -0.3), 0.0, rng.uniform(-0.1, 0.1)])
    p0 = np.r_[c, olhar(c, alvo), rng.uniform(300, 1500)]
    p = lm(p0)
    e = np.sqrt((residuo(p)[:2 * len(P3)] ** 2).reshape(-1, 2).sum(1).mean())
    if np.isfinite(e) and (melhor is None or e < melhor[0]):
        melhor = (e, p)
e, p = melhor
uv, z = projetar(p, P3)
R = rot(p[3:6])
print('erro rms px', round(e, 2))
print('camera m', np.round(p[:3], 4), 'f px', round(p[6], 1), 'lente 36mm', round(p[6] * 36 / W, 1))
print('frente', np.round(-R[:, 2], 4), 'cima', np.round(R[:, 1], 4))
for a, b in zip(uv, P2):
    print('  ', np.round(a, 1), b)
