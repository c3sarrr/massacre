"""Tarefa 12 (a regra lateral): a pose da câmera do viewmodel do CS2 pelo P3P (todas as soluções, varrendo a primeira
profundidade em uma dimensão) a partir de três pontos de tela medidos na arma (cs2.md: só números) e dos pontos 3D do
nosso modelo (o mesmo contorno do CS2, na escala da arma real); depois, o raio dos nós da luva de apoio cortado por
planos paralelos à face de apoio. Só números: nada do jogo é gravado.
    python p3p_cs2.py [awp]
O resultado (no registro da Tarefa 12, achado 7): as soluções só saem com a arma rolada (de pé), e o ajuste erra ~5 % da
largura da tela — a bola do ferrolho da nossa ficha é estimada (o lado direito não aparece na vista de lado do jogo).
A altura dos nós no quadro não sai desta conta: a comparação com o quadro do CS2 fica para a P2."""
import math
import sys

import numpy as np

FOV_H = 68.0  # o viewmodel_fov (horizontal, 4:3; os quadros são 4:3 esticados para 16:9: as frações são as mesmas)
F = 2.0 / math.tan(math.radians(FOV_H / 2))


def raio(fr):
    """A direção unitária (no referencial da câmera: x para a direita, y para baixo, z para a frente) da fração de
    tela (x da esquerda, y de cima)."""
    u, v = (fr[0] - 0.5) * 4.0, (fr[1] - 0.5) * 3.0
    d = np.array([u / F, v / F, 1.0])
    return d / np.linalg.norm(d)


def kabsch(A, B):
    """R, t com B ≈ R A + t (os pontos nas linhas)."""
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    U, _S, Vt = np.linalg.svd(H)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, cb - R @ ca


def p3p(telas, pontos):
    f = [raio(t) for t in telas]
    P = [np.asarray(p, dtype=float) for p in pontos]
    a, b, c = np.linalg.norm(P[1] - P[2]), np.linalg.norm(P[0] - P[2]), np.linalg.norm(P[0] - P[1])
    cg, cb_ = f[0] @ f[1], f[0] @ f[2]

    def ramos(s1):
        out = []
        dc, db = c * c - s1 * s1 * (1 - cg * cg), b * b - s1 * s1 * (1 - cb_ * cb_)
        if dc < 0 or db < 0:
            return out
        for s2 in (s1 * cg + math.sqrt(dc), s1 * cg - math.sqrt(dc)):
            for s3 in (s1 * cb_ + math.sqrt(db), s1 * cb_ - math.sqrt(db)):
                # todos os ramos ficam (o sinal da profundidade é conferido na raiz): pulando os negativos, o valor de
                # s1 inteiro saía, com o ramo certo dentro dele
                out.append((s2, s3, np.linalg.norm(s2 * f[1] - s3 * f[2]) - a))
        return out

    sols = []
    grade = np.linspace(1.0, 6000.0, 60001)
    for ramo in range(4):
        anterior = None
        for s1 in grade:
            r = ramos(s1)
            if len(r) != 4:
                anterior = None
                continue
            s2, s3, e = r[ramo]
            if anterior is not None and anterior[1] * e < 0:
                lo, hi = anterior[0], s1
                for _ in range(80):
                    mid = (lo + hi) / 2
                    rm = ramos(mid)
                    if len(rm) != 4:
                        break
                    if (ramos(lo)[ramo][2]) * rm[ramo][2] <= 0:
                        hi = mid
                    else:
                        lo = mid
                s1r = (lo + hi) / 2
                rr = ramos(s1r)
                if len(rr) == 4:
                    s2r, s3r, er = rr[ramo]
                    if abs(er) < 1e-3 and s2r > 0 and s3r > 0:
                        sols.append((s1r, s2r, s3r))
            anterior = (s1, e)
    resultado = []
    for s1, s2, s3 in sols:
        C = np.array([s1 * f[0], s2 * f[1], s3 * f[2]])  # os pontos no referencial da câmera
        R, t = kabsch(np.array(P), C)
        cam = R.T @ (-t)  # o centro da câmera no referencial do modelo
        if all(np.linalg.norm(cam - q[0]) > 1.0 for q in resultado):
            resultado.append((cam, R, t))
    return resultado


def principal(telas, pontos, nos, faces, nomes):
    for cam, R, t in p3p(telas, pontos):
        eixo = R[:, 0]  # o +X do modelo (para a boca) no referencial da câmera
        print(f'câmera no modelo (mm) {np.round(cam, 1)}; o eixo da arma na câmera {np.round(eixo, 3)}; '
              f'o alto da arma (+Z) na câmera {np.round(R[:, 2], 3)}')
        for nome, fr in nos.items():
            d = R.T @ raio(fr)  # o raio dos nós no referencial do modelo
            for y in faces:
                s = (y - cam[1]) / d[1]
                q = cam + s * d
                print(f'   {nome}: no plano y = {y:5.1f} mm: x = {q[0]:7.1f}, z = {q[2]:6.1f} (a {s:6.1f} mm da câmera)')


if __name__ == '__main__':
    arma = sys.argv[1] if len(sys.argv) > 1 else 'awp'
    if arma == 'awp':
        # as frações de tela da AWP em 8:32,0 (cs2.md, "Enquadramento na posição pronta"): a ponta da boca, o centro da
        # objetiva e a bola do ferrolho; os pontos do nosso modelo (mm, X para a boca, Y para a esquerda, Z para cima,
        # a ponta da boca na origem)
        principal([(0.574, 0.630), (0.761, 0.664), (0.791, 0.879)],
                  [(0.0, 0.0, 0.0), (-641.0, 0.0, 55.3), (-893.0, -46.0, -6.0)],
                  {'nós da luva de apoio': (0.604, 0.755)}, (27.0, 37.0, 47.0, 57.0),
                  ('boca', 'objetiva', 'bola'))
