"""Tarefa 13: a câmera do quadro pronto da AWP do CS2 (8:32,0 do Tigerfield; cs2.md, só números) ajustada aos pontos de
tela da arma — a boca, o centro da objetiva e a bola do ferrolho — com a arma de pé (sem rolar: a câmera sem giro em
volta do olhar, no referencial da arma), por mínimos quadrados (5 incógnitas: a posição da câmera e as duas direções
do olhar; 6 equações). Depois, onde os nós da luva de apoio da nossa pega cairiam nessa câmera, contra os do quadro.
Só números: nada do jogo é gravado.
    python camera_cs2.py
O P3P da Tarefa 12 (t12/p3p_cs2.py) só achava a arma rolada; aqui ela fica de pé e o resíduo diz o quanto os três
pontos discordam da nossa ficha (a bola do ferrolho é estimada: o lado direito não aparece na vista de lado do jogo)."""
import math

import numpy as np

FOV_H = 68.0  # o viewmodel_fov (horizontal, 4:3; o quadro 16:9 é o 4:3 esticado: as frações valem as mesmas)
F = 2.0 / math.tan(math.radians(FOV_H / 2))
# a arma (mm; X para a boca, Y para a esquerda, Z para cima; a ponta da boca na origem) e as frações do quadro
PONTOS = {'boca': ((0.0, 0.0, 0.0), (0.574, 0.630)),
          'objetiva': ((-641.0, 0.0, 55.3), (0.761, 0.664)),
          'bola': ((-893.0, -46.0, -6.0), (0.791, 0.879))}
NOS_CS2 = (0.604, 0.755)
# os nós da luva de apoio da pega da Tarefa 13 (a média das quatro MCPs, mm) e o dorso (unitário): o protetor fica
# ~10 mm por fora das juntas, pela normal do dorso
MCPS = np.array([(-619.7, 42.8, -45.5), (-599.4, 51.7, -51.1), (-579.2, 56.6, -59.8), (-560.3, 59.7, -69.6)])
DORSO = np.array((-0.339, 0.936, -0.099))
PROTETOR_MM = 10.0


def projetar(p, c, yaw, pitch):
    f = np.array((math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)))
    r = np.cross(f, (0.0, 0.0, 1.0))
    r /= np.linalg.norm(r)
    baixo = np.cross(f, r)
    q = np.asarray(p) - c
    x, y, z = q @ r, q @ baixo, q @ f
    return np.array((0.5 + x * F / (4.0 * z), 0.5 + y * F / (3.0 * z))), z


def residuos(v):
    c, yaw, pitch = v[:3], v[3], v[4]
    out = []
    for p, fr in PONTOS.values():
        uv, z = projetar(p, c, yaw, pitch)
        out += list(uv - np.array(fr)) if z > 50.0 else [10.0, 10.0]
    return np.array(out)


def ajustar(v):
    for _ in range(200):
        r = residuos(v)
        J = np.zeros((len(r), 5))
        for k in range(5):
            h = 1e-4 if k > 2 else 1e-2
            dv = np.zeros(5)
            dv[k] = h
            J[:, k] = (residuos(v + dv) - r) / h
        passo, *_ = np.linalg.lstsq(J, -r, rcond=None)
        v = v + passo
        if np.linalg.norm(passo) < 1e-9:
            break
    return v, float(np.sqrt((residuos(v) ** 2).mean()))


def principal():
    melhores = []
    for cx in (-1500.0, -1300.0, -1100.0):
        for cy in (-100.0, 50.0, 200.0, 350.0):
            for cz in (0.0, 100.0, 200.0):
                for yaw in (-0.6, -0.3, 0.0, 0.3):
                    v, erro = ajustar(np.array((cx, cy, cz, yaw, -0.1)))
                    if np.all(np.isfinite(v)):
                        melhores.append((erro, tuple(np.round(v, 4))))
    melhores.sort()
    vistos = []
    for erro, v in melhores:
        if any(np.linalg.norm(np.array(v[:3]) - np.array(w[:3])) < 5.0 for _e, w in vistos):
            continue
        vistos.append((erro, v))
        if len(vistos) == 3:
            break
    nos = MCPS.mean(0) + DORSO * PROTETOR_MM
    for erro, v in vistos:
        c, yaw, pitch = np.array(v[:3]), v[3], v[4]
        print(f'câmera (mm) {np.round(c, 1)}, guinada {math.degrees(yaw):.1f}°, arfagem {math.degrees(pitch):.1f}°: '
              f'o resíduo médio {erro * 100:.2f} % da tela')
        for nome, (p, fr) in PONTOS.items():
            uv, _z = projetar(p, c, yaw, pitch)
            print(f'   {nome}: {np.round(uv, 3)} (o quadro: {fr})')
        uv, z = projetar(nos, c, yaw, pitch)
        print(f'   os nós da nossa luva de apoio ({np.round(nos, 1)} mm): {np.round(uv, 3)} (o quadro: {NOS_CS2}); '
              f'a diferença {np.round((uv - np.array(NOS_CS2)) * 100, 1)} % (x da largura, y da altura), a {z:.0f} mm')


if __name__ == '__main__':
    principal()
