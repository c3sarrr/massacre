# O candidato da parte de cima da P90 do CS2 (a C1), com os números medidos nas duas imagens (o ícone e o quadro de 108,6 s
# do vídeo de inspeção) pelo ajuste conjunto: cada peça um contorno de lado (x, alto) extrudado entre dois lados, para o
# sobrepor.py projetar nas duas e conferir por cima delas. Só números nossos; nada do jogo.
#   python candidato.py && python sobrepor.py candidato.json
import json, math

PONTE = [(-212.5, 67.2), (-216.5, 60.0), (-220.0, 50.0), (-224.0, 43.5), (-227.5, 39.3), (-214.1, 39.3), (-217.7, 29.3), (-219.2, 23.0),
         (-221.0, 1.3), (-186.0, 1.3), (-184.5, 23.5), (-179.2, 37.8), (-177.5, 39.3), (-172.5, 51.3), (-155.5, 49.5), (-132.5, 44.8),
         (-101.0, 40.8), (-96.0, 38.8), (-82.2, 38.8), (-82.2, 36.3), (-79.0, 35.8), (-77.5, 33.8), (-78.0, 29.5), (-80.7, 27.3),
         (-80.7, 16.8), (-82.2, 14.3), (-82.2, 1.3), (-47.5, 1.3), (-47.5, 11.8), (-48.6, 26.5), (-49.6, 38.4), (-51.5, 47.9),
         (-68.4, 65.6), (-69.5, 67.2)]
TRILHO = {'x': (-205.7, -69.5), 'topo': 76.6, 'base': 67.2}
JANELA = [(-86.0, 50.0), (-196.0, 57.0), (-196.0, 63.8), (-86.0, 63.8)]
JANELA_TORRE = [(-71.0, 14.0), (-52.0, 14.0), (-52.0, 33.0), (-71.0, 33.0)]
FRENTE_BASE = [(-69.5, 67.2), (-69.5, 83.4), (-74.5, 88.6), (-92.0, 88.6), (-105.0, 77.2), (-105.0, 70.0), (-73.0, 70.0), (-73.0, 67.2)]
FRENTE_ORELHA = [(-77.8, 88.6), (-74.6, 108.0), (-75.0, 111.5), (-77.5, 114.2), (-84.0, 114.3), (-86.5, 112.7), (-87.6, 108.8),
                 (-88.0, 88.6)]
TRAS_BASE = [(-160.0, 70.0), (-160.0, 86.0), (-165.0, 91.0), (-184.0, 91.0), (-199.0, 77.0), (-199.0, 70.0)]
TRAS_ORELHA = [(-163.5, 91.0), (-163.8, 105.0), (-165.6, 109.6), (-167.8, 114.8), (-169.5, 117.3), (-172.7, 118.0), (-175.0, 117.4),
               (-176.6, 115.3), (-178.4, 112.4), (-180.2, 109.1), (-182.2, 105.2), (-182.5, 91.0)]


def circulo(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


x0, x1 = TRILHO['x']
cand = {'pecas': [
    {'nome': 'ponte', 'contorno': PONTE, 'lados': [16.0, -16.0], 'cor': '#ff00ff', 'arestas': True},
    {'nome': 'trilho (topo)', 'contorno': [(x0, TRILHO['topo']), (x1, TRILHO['topo'])], 'lados': [8.08, -8.08], 'cor': '#00ffff',
     'fechar': False, 'arestas': True},
    {'nome': 'trilho (largura máxima)', 'contorno': [(x0, TRILHO['topo'] - 2.53), (x1, TRILHO['topo'] - 2.53)], 'lados': [10.6, -10.6],
     'cor': '#00aaff', 'fechar': False},
    {'nome': 'trilho (pontas)', 'contorno': [(x0, TRILHO['base']), (x0, TRILHO['topo']), (x1, TRILHO['topo']), (x1, TRILHO['base'])],
     'lados': [10.6], 'cor': '#00ffff', 'fechar': False},
    {'nome': 'janela', 'contorno': JANELA, 'lados': [16.0, -16.0], 'cor': '#ffff00'},
    {'nome': 'janela da torre', 'contorno': JANELA_TORRE, 'lados': [16.0], 'cor': '#ffff00'},
    {'nome': 'base da frente', 'contorno': FRENTE_BASE, 'lados': [12.2, -12.2], 'cor': '#ff8800', 'arestas': True},
    {'nome': 'orelha da frente', 'contorno': FRENTE_ORELHA, 'lados': [8.0, 5.5], 'cor': '#00ff00', 'arestas': True},
    {'nome': 'orelha da frente (longe)', 'contorno': FRENTE_ORELHA, 'lados': [-5.5, -8.0], 'cor': '#008800'},
    {'nome': 'base de trás', 'contorno': TRAS_BASE, 'lados': [12.2, -12.2], 'cor': '#ff8800', 'arestas': True},
    {'nome': 'orelha de trás', 'contorno': TRAS_ORELHA, 'lados': [11.25, 8.75], 'cor': '#00ff00', 'arestas': True},
    {'nome': 'orelha de trás (longe)', 'contorno': TRAS_ORELHA, 'lados': [-8.75, -11.25], 'cor': '#008800'},
    {'nome': 'botão da frente', 'contorno': circulo(-80.0, 80.9, 6.5), 'lados': [20.0, 12.2], 'cor': '#ff4444', 'arestas': False},
    {'nome': 'botão de trás', 'contorno': circulo(-173.5, 80.6, 6.5), 'lados': [20.0, 12.2], 'cor': '#ff4444', 'arestas': False},
    {'nome': 'anel de trás', 'contorno': circulo(-173.0, 112.2, 5.0), 'lados': [1.0], 'cor': '#ffffff'},
    {'nome': 'buracos da orelha', 'contorno': circulo(-172.8, 106.0, 5.0, 7), 'lados': [11.25], 'cor': '#ffffff', 'fechar': False},
],
    'pontos': [['poste', (-81.1, 112.2, 0.0), '#ffffff'], ['tambor', (-186.0, 100.0, 0.0), '#ffffff'],
               ['orelha frente-topo', (-72.6, 114.6, 4.0), '#ffff00'], ['canto do trilho', (-205.7, 76.0, 6.9), '#ffff00']]}
cand['deslocamentoLado'] = -3.9
json.dump(cand, open('candidato.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok')
