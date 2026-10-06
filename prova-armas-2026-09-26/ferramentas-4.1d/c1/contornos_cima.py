# Os contornos de cima do grupo de cima da P90 do CS2 (a silhueta contra o céu no quadro de 108,6 s da inspeção e o alfa do
# ícone do inventário, lidos no navegador; só os números): a volta ao espaço da arma em vários lados e a comparação das
# duas fontes por trecho.
import json
import numpy as np
from volta import plano
SP = r'C:/Users/T-Gamer/AppData/Local/Temp/claude/C--Users-T-Gamer-Desktop-game-tiro/c7a63f39-8955-467e-9908-7a258f968380/scratchpad/c1'
VIDEO = json.load(open(SP + '/topo_video.json'))
ICONE = json.load(open(SP + '/topo_icone.json'))
def curva(fonte, pts, u0, u1, lado):
    out = []
    for u, v in pts:
        if v is None or not (u0 <= u <= u1):
            continue
        out.append(plano(fonte, u, v, lado))
    return np.array(out)
def comparar(nome, tv, ti, lados):
    print(f'--- {nome}')
    for L in lados:
        a = curva('video', VIDEO, *tv, L)
        b = curva('icone', ICONE, *ti, L)
        if not len(a) or not len(b):
            continue
        # alto no x comum (interpolado)
        x0, x1 = max(a[:, 0].min(), b[:, 0].min()), min(a[:, 0].max(), b[:, 0].max())
        xs = np.linspace(x0, x1, 7) if x1 > x0 else []
        ia = np.argsort(a[:, 0]); ib = np.argsort(b[:, 0])
        linhas = []
        for x in xs:
            ya = np.interp(x, a[ia, 0], a[ia, 1]); yb = np.interp(x, b[ib, 0], b[ib, 1])
            linhas.append(f'{x:7.1f}: {ya:6.1f} {yb:6.1f} ({ya - yb:+5.1f})')
        print(f' lado {L:5.1f}  video x {a[:, 0].min():7.1f}..{a[:, 0].max():7.1f}  icone x {b[:, 0].min():7.1f}..{b[:, 0].max():7.1f}')
        for l in linhas:
            print('    ', l)
if __name__ == '__main__':
    import sys
    comparar('trilho de cima (os dentes)', (852, 944), (163, 206), [6.0, 10.6, 14.0])
    comparar('mira da frente, orelha', (816, 850), (122, 146), [0.0, 4.0, 8.0])
    comparar('mira de trás, orelha', (964, 1008), (207, 239), [0.0, 4.0, 8.0, 10.4])
    comparar('frente da torre (a rampa)', (718, 780), (85, 107), [10.0, 15.1, 20.0])
    comparar('quebra-chama (o alto)', (646, 712), (36, 84), [0.0, 5.0, 10.9])
