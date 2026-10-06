# A volta dos pixels das duas imagens do CS2 ao espaço da arma (mm da ficha: x, alto, lado), pelas câmeras de cameras.json:
# `plano(cam, u, v, lado)` corta o raio no plano do lado; `triangular([(cam, u, v), ...])` o ponto mais perto dos raios.
import json
import numpy as np
from cameras import rot, S
CAMS = json.load(open('cameras_conjunto.json'))
def raio(cam, u, v):
    c = CAMS[cam]
    p, W, H = np.array(c['p']), c['W'], c['H']
    C, R, f = p[:3], rot(p[3:6]), p[6]
    d = R @ np.array([(u - W / 2) / f, -(v - H / 2) / f, -1.0])
    return C, d / np.linalg.norm(d)
def plano(cam, u, v, lado):
    C, d = raio(cam, u, v)
    t = (lado * S - C[1]) / d[1]
    X = (C + t * d) / S
    return float(X[0]), float(X[2])
def triangular(obs):
    A, b = np.zeros((3, 3)), np.zeros(3)
    raios = [raio(*o) for o in obs]
    for C, d in raios:
        M = np.eye(3) - np.outer(d, d)
        A += M; b += M @ C
    X = np.linalg.solve(A, b)
    dist = [float(np.linalg.norm((np.eye(3) - np.outer(d, d)) @ (X - C)) / S) for C, d in raios]
    return (float(X[0] / S), float(X[2] / S), float(X[1] / S)), dist
