# As linhas da ficha da AWP (o contorno, os buracos e as peças de lado, cada um num plano de lado) projetadas pela câmera
# do ícone do CS2 (conferir.ICONE, a mesma do render `icone`) em pixels do ícone (512 x 384), no formato da grade.html
# (`dados=`): para ler no navegador onde o carregador do ícone fica em relação ao nosso. Só números nossos; o ícone só é
# lido no navegador.
#   python linhas_icone.py <saida.json> [<extra.json>]
#   <extra.json>: {"linhas": [{"cor", "lado": [..], "pts": [[x, alto], ...], "fechar"}], "pontos": [[x, alto, lado, rotulo, cor]]}
import json
import sys

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
RAIZ = r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d'
f = json.load(open(f'{RAIZ}/tools/blender/refs/awp.json', encoding='utf-8'))
xs = [p[0] for p in f['contorno']]
ys = [p[1] for p in f['contorno']]
c = np.array([(min(xs) + max(xs)) / 2, 0.0, (min(ys) + max(ys)) / 2])  # Blender em mm: x, lado, alto
I = {'frente': (-0.8549, -0.5180, 0.0271), 'cima': (0.0751, -0.0720, 0.9946), 'lente': 89.3, 'distancia': 1.7349,
     'mira': (0.0481, -0.0809, -0.0284), 'comprimento': 1.23}
ki = (max(xs) - min(xs)) / 1000 / I['comprimento']
mira = c + np.array(I['mira']) * 1000 * ki
F = np.array(I['frente'])
F = F / np.linalg.norm(F)
pos = mira - F * I['distancia'] * 1000 * ki
R = np.cross(F, np.array(I['cima']))
R /= np.linalg.norm(R)
U = np.cross(R, F)
FPX = I['lente'] / 36 * 512


def proj(x, alto, lado):
    d = np.array([x, lado, alto]) - pos
    z = d @ F
    return [round(256 + FPX * (d @ R) / z, 2), round(192 - FPX * (d @ U) / z, 2)]


L = f['vistaDeCima']['larguras']
linhas, pontos = [], []


def poligono(pts, lado, cor, fechar=True):
    linhas.append({'cor': cor, 'pts': [proj(x, y, lado) for x, y in pts], 'fechar': fechar})


# o contorno nas duas faces da coronha (a esquerda, que o ícone mostra, mais clara)
meia = L['coronha']['mm'] / 2
poligono(f['contorno'], meia, '#00ff66')
poligono(f['contorno'], -meia, 'rgba(0,255,102,0.35)')
# o guarda-mato e o buraco do polegar nas faces deles
for nome, pts in zip(f['buracosNomes'], f['buracos']):
    m = {'guardaMato': L['guardaMato']['mm'] / 2, 'buracoPolegar': L['punho']['mm'] / 2}.get(nome)
    if m:
        poligono(pts, m, '#00e5ff')
        poligono(pts, -m, 'rgba(0,229,255,0.35)')
# o carregador da ficha (as duas faces e as quinas de lado a lado)
mc = L['carregador']['mm'] / 2
car = f['pecas']['carregador']
poligono(car, mc, '#ffee00')
poligono(car, -mc, 'rgba(255,238,0,0.4)')
for x, y in car:
    linhas.append({'cor': 'rgba(255,238,0,0.6)', 'pts': [proj(x, y, mc), proj(x, y, -mc)]})
for x, y in car:
    pontos.append(proj(x, y, mc) + [f'{x:.0f},{y:.0f}', '#ffee00'])
if len(sys.argv) > 2:
    ex = json.load(open(sys.argv[2], encoding='utf-8'))
    for l in ex.get('linhas', []):
        for lado in l['lado']:
            poligono(l['pts'], lado, l['cor'], l.get('fechar', True))
    for x, y, lado, rot, cor in ex.get('pontos', []):
        pontos.append(proj(x, y, lado) + [rot, cor])
json.dump({'linhas': linhas, 'pontos': pontos}, open(sys.argv[1], 'w', encoding='utf-8'))
print('ok', len(linhas), 'linhas', len(pontos), 'pontos')
for x, y in [(-850.1, -76.6), (-843.2, -73.6), (-827.5, -72.6), (-754.9, -67.7), (-736.2, -66.8)]:
    print(f'contorno ({x}, {y}) lado +{meia}: {proj(x, y, meia)}')
