# As linhas da parte de cima do nosso modelo (os contornos da ficha p90.json, cada um no lado da face de perto) projetadas
# pelas câmeras do CS2 (cameras.json), para sobrepor no ícone (grade.html, `dados`) e no quadro do vídeo. Só números nossos.
import json, sys
import numpy as np
from cameras import projetar, S
FICHA = r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/refs/p90.json'
CONF = r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/conferencia/p90'
f = json.load(open(FICHA, encoding='utf-8'))
cams = json.load(open('cameras_conjunto.json'))
L = {k: v['mm'] / 2 for k, v in f['vistaDeCima']['larguras'].items()}
pc = f['pecas']
# (nome, polígono (x, alto), lado, cor)
LINHAS = [
    ('ponte', pc['ponte'], L['ponte'], '#ff00ff'),
    ('ponte (corpo)', pc['ponte'], L['ponteTrilhos'], '#ff66ff'),
    ('trilho de cima', pc['trilhoCima'], L['trilhoCima'], '#00ffff'),
    ('trilho lateral', pc['trilhoLateral'], L['trilhoLateral'], '#ffff00'),
    ('mira de trás', pc['rebativelTras'], 10.4, '#ff8800'),
    ('mira da frente', pc['rebativelFrente'], 8.2, '#ff8800'),
    ('quebra-chama', pc['quebraChama'], 10.9, '#00ff00'),
    ('receptor', pc['receptor'], L['receptor'], '#8888ff'),
    ('carregador', pc['carregador'], L['carregador'], '#ff4444'),
]
def para(cam, extra=()):
    c = cams[cam]
    p, W, H = np.array(c['p']), c['W'], c['H']
    out = {'linhas': [], 'pontos': []}
    for nome, poli, lado, cor in LINHAS:
        X = np.array([[x * S, lado * S, y * S] for x, y in poli])
        uv, _ = projetar(p, X, W, H)
        out['linhas'].append({'cor': cor, 'pts': [[round(float(u), 2), round(float(v), 2)] for u, v in uv], 'fechar': True, 'nome': nome})
    for nome, (x, y, l), cor in extra:
        uv, _ = projetar(p, np.array([[x * S, l * S, y * S]]), W, H)
        out['pontos'].append([round(float(uv[0, 0]), 2), round(float(uv[0, 1]), 2), nome, cor])
    return out
if __name__ == '__main__':
    extra = [('boca', (0.0, 0.0, 0.0), '#00ff00'), ('alavanca', (-90.3, -4.7, 21.0), '#00ff00')]
    for cam in ('icone', 'video'):
        json.dump(para(cam, extra), open(f'{CONF}/linhas_{cam}.json', 'w'))
    print('ok')
