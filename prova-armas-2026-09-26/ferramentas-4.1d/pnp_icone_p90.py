# Ajuste de uma câmera de furo aos pontos marcados no ícone do CS2 da P90 (512x384), por Levenberg-Marquardt com
# jacobiano numérico e vários pontos de partida. Pontos 3D no Blender (m): X a boca, Y a esquerda, Z o alto.
import numpy as np
S = 0.001
# (x, alto, lado) em mm da ficha, do modelo construído (p90_pontos.py)
PTS = [
    ((0.0, 0.0, 0.0), (29.0, 179.0)),            # A o centro da boca do quebra-chama
    ((-90.64, -4.7, 21.0), (150.5, 195.8)),      # B a face do botão da alavanca (o centro)
    ((-141.2, -80.5, 19.32), (195.0, 298.3)),    # C o parafuso do pé do lóbulo
    ((-235.8, -75.7, 20.47), (283.3, 300.5)),    # D o parafuso do punho, embaixo na frente
    ((-295.0, -79.6, 21.3), (333.0, 310.5)),     # E o parafuso do punho, embaixo atrás
    ((-378.3, -59.5, 26.7), (400.5, 294.5)),     # F o parafuso da coronha, embaixo na frente
    ((-452.1, -67.0, 26.49), (450.8, 308.4)),    # G o parafuso da coronha, embaixo atrás
    ((-424.4, 14.6, 27.5), (437.0, 220.5)),      # H o parafuso da coronha, em cima na frente
    ((-485.3, 10.2, 27.5), (476.9, 233.3)),      # I o parafuso da coronha, em cima atrás
]
P3 = np.array([[x * S, l * S, y * S] for (x, y, l), _ in PTS])
P2 = np.array([uv for _, uv in PTS])
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
# conferência: onde caem pontos que não entraram no ajuste
TESTE = [
    ('mira da frente, orelha perto, topo frente', (-46.06, 130.0, 8.2)),
    ('mira da frente, orelha perto, topo trás', (-60.74, 130.0, 8.2)),
    ('mira da frente, orelha longe, topo frente', (-46.06, 130.0, -8.2)),
    ('mira de trás, orelha perto, topo frente', (-175.92, 129.3, 10.4)),
    ('mira de trás, orelha perto, topo trás', (-183.5, 129.3, 10.4)),
    ('mira de trás, orelha longe, topo frente', (-175.92, 129.3, -10.4)),
    ('canto de baixo atrás da coronha', (-503.86, -78.84, 16.13)),
    ('pé do punho (lado 18)', (-283.0, -101.2, 18.0)),
    ('pé do lóbulo (lado 15)', (-153.0, -102.0, 15.0)),
]
X = np.array([[x * S, l * S, y * S] for _, (x, y, l) in TESTE])
uv, _ = projetar(p, X)
for (nome, _), q in zip(TESTE, uv):
    print(f'  {nome:45s} {np.round(q, 1)}')
