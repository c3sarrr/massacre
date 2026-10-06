"""Tarefa 15: a câmera do quadro pronto da P90 do CS2 (5:27,5 do Tigerfield; cs2.md, só números) ajustada aos pontos
de tela da arma — o topo do poste da mira da frente, o centro do anel da mira de trás e a ponta do quebra-chama —, com
a arma de pé, como a da AWP (t13/camera_cs2.py: 5 incógnitas, 6 equações). Depois, onde os nós das luvas das pegas das
varreduras (os JSON de varreduras_p90) cairiam nessa câmera, contra os do quadro (o do gatilho em 0,742; 0,937 e o de
apoio em 0,653; 0,858). Só números: nada do jogo é gravado.
    python camera_p90.py [json...]
"""
import glob
import json
import math
import os
import sys

import numpy as np

FOV_H = 68.0  # o viewmodel_fov (horizontal, 4:3; o quadro 16:9 é o 4:3 esticado: as frações valem as mesmas)
F = 2.0 / math.tan(math.radians(FOV_H / 2))
# a arma (mm; X para a boca, Y para a esquerda, Z para cima; a ponta da boca na origem: o referencial da ficha) e as
# frações do quadro
PONTOS = {'miraFrente': ((-81.1, 0.0, 112.2), (0.688, 0.495)),
          'miraTras': ((-173.0, 0.0, 112.2), (0.727, 0.499)),
          'boca': ((0.0, 0.0, 0.0), (0.657, 0.737))}
NOS_CS2 = {'d': (0.742, 0.937), 'e': (0.653, 0.858)}
PROTETOR_MM = 10.0  # o protetor dos nós ~10 mm por fora das juntas, pela normal do dorso


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


def cameras():
    melhores = []
    for cx in (-900.0, -700.0, -500.0):
        for cy in (-250.0, -100.0, 50.0):
            for cz in (0.0, 150.0, 300.0):
                for yaw in (-0.3, 0.0, 0.3):
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
    return vistos


def nos_da_luva(s):
    """O protetor dos nós de uma pega (o resumo de pega_banco.mao): a média das quatro MCPs mais 10 mm pelo dorso (a
    cena do Blender está no referencial da ficha, em mm: o soquete mao_d no `pescoco` da ficha)."""
    mcps = np.array([s['nos'][f'{d}_1'] for d in ('indicador', 'medio', 'anelar', 'minimo')])
    return mcps.mean(0) + np.array(s['dorso']) * PROTETOR_MM


def principal(arquivos):
    vistos = cameras()
    erro, v = vistos[0]
    c, yaw, pitch = np.array(v[:3]), v[3], v[4]
    for e2, v2 in vistos:
        print(f'câmera (mm) {np.round(v2[:3], 1)}, guinada {math.degrees(v2[3]):.1f}°, arfagem {math.degrees(v2[4]):.1f}°: '
              f'o resíduo médio {e2 * 100:.2f} % da tela')
    for nome, (p, fr) in PONTOS.items():
        uv, _z = projetar(p, c, yaw, pitch)
        print(f'   {nome}: {np.round(uv, 3)} (o quadro: {fr})')
    for arq in arquivos:
        for s in json.load(open(arq, encoding='utf-8')):
            if s.get('erro') or 'nos' not in s:
                continue
            p = nos_da_luva(s)
            uv, z = projetar(p, c, yaw, pitch)
            alvo = np.array(NOS_CS2[s['lado']])
            d = (uv - alvo) * 100
            cfg = s['correcoes']
            print(os.path.basename(arq), json.dumps([cfg.get('ancora', {}).get('mm'), cfg.get('giros'), cfg.get('diagonal')]),
                  'nós', np.round(p, 1), 'tela', np.round(uv, 3), 'dif %', np.round(d, 1), round(float(np.hypot(*d)), 1))


if __name__ == '__main__':
    principal([a for p in sys.argv[1:] for a in glob.glob(p)])
