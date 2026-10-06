# A terceira fonte da C1: os ícones das peles da P90 no CS2 (P90_Wash_me.png e as outras de 2024 a 2026, todas com a
# mesma câmera, 512 x 384, de frente e de cima pela esquerda), só lidos no navegador. A câmera de furo ajustada aos
# parafusos da face esquerda do quadro (as posições da ficha p90.json, o lado da face do nosso modelo), como o ícone do
# inventário e o quadro do vídeo. Só números.
import json, sys
import numpy as np
from cameras import ajustar, rot, S, projetar
# (x, alto, lado) da ficha <-> (u, v) no ícone da pele
PTS = [
    ((-100.7, -28.1, 15.10), (155.0, 229.1)),
    ((-141.2, -80.5, 19.32), (194.6, 298.9)),
    ((-214.7, -27.3, 19.71), (267.1, 244.9)),
    ((-235.8, -75.7, 20.47), (282.7, 300.6)),
    ((-295.0, -79.6, 21.31), (332.8, 310.8)),
    ((-378.3, -59.5, 26.71), (401.0, 294.4)),
    ((-452.1, -67.0, 26.38), (451.4, 308.7)),
]
if __name__ == '__main__':
    usar = PTS if len(sys.argv) < 2 else [PTS[int(i)] for i in sys.argv[1].split(',')]
    e, p = ajustar(usar, 512, 384, ((-0.4, 1.2), (0.2, 2.0), (0.05, 1.4)), ((-0.45, 0.0), (-0.06, 0.06)), (300, 2500), 5, 400)
    R = rot(p[3:6])
    print('rms', round(e, 3), 'f', round(p[6], 1), 'camera mm', np.round(p[:3] / S), 'frente', np.round(-R[:, 2], 3))
    P3 = np.array([[x * S, l * S, y * S] for (x, y, l), _ in PTS])
    uv, _ = projetar(p, P3, 512, 384)
    for ((x, y, l), m), q in zip(PTS, uv):
        print(f'  {x:7.1f} {y:6.1f} {l:5.1f}  marcado {m}  modelo ({q[0]:.1f}, {q[1]:.1f})  resíduo {np.hypot(*(q - m)):.2f}')
    json.dump({'p': [float(v) for v in p], 'W': 512, 'H': 384, 'rms': float(e)}, open('camera_pele.json', 'w'), indent=1)
