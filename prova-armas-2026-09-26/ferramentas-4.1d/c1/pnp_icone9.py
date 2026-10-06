# O ícone do inventário e o das peles têm a MESMA câmera (os alfas batem pixel a pixel: IoU 1,0000). Os nove parafusos
# da face esquerda juntos (os sete do pnp_icone_p90 e os dois de cima da frente marcados na pele), e a curva do erro
# com a focal presa, para ver a ambiguidade focal x distância do ajuste por pontos quase num plano.
import json, sys
import numpy as np
from cameras import ajustar, rot, S, projetar
PTS = [
    ((-141.2, -80.5, 19.32), (195.0, 298.3)),
    ((-235.8, -75.7, 20.47), (283.3, 300.5)),
    ((-295.0, -79.6, 21.31), (333.0, 310.5)),
    ((-378.3, -59.5, 26.71), (400.5, 294.5)),
    ((-452.1, -67.0, 26.38), (450.8, 308.4)),
    ((-424.4, 14.6, 27.5), (437.0, 220.5)),
    ((-485.3, 10.2, 27.25), (476.9, 233.3)),
    ((-100.7, -28.1, 15.10), (155.0, 229.1)),
    ((-214.7, -27.3, 19.71), (267.1, 244.9)),
]
if __name__ == '__main__':
    e, p = ajustar(PTS, 512, 384, ((-0.4, 1.4), (0.2, 2.2), (-0.8, 1.0)), ((-0.45, 0.0), (-0.06, 0.06)), (300, 2500), 7, 300)
    R = rot(p[3:6])
    print('9 parafusos: rms', round(e, 3), 'f', round(p[6], 1), 'camera mm', np.round(p[:3] / S), 'frente', np.round(-R[:, 2], 3))
    P3 = np.array([[x * S, l * S, y * S] for (x, y, l), _ in PTS])
    uv, _ = projetar(p, P3, 512, 384)
    for ((x, y, l), m), q in zip(PTS, uv):
        print(f'  {x:7.1f} {y:6.1f} {l:5.1f}  marcado {m}  modelo ({q[0]:.1f}, {q[1]:.1f})  resíduo {np.hypot(*(q - m)):.2f}')
    json.dump({'p': [float(v) for v in p], 'W': 512, 'H': 384, 'rms': float(e)}, open('camera_icone9.json', 'w'), indent=1)
