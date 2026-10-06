# As miras da ficha da P90 (depois da C1) projetadas pelas câmeras do ajuste conjunto no ícone e no quadro do vídeo, para
# conferir por cima das imagens no navegador (grade.html `dados`; o vídeo pelo window.__linhas da aba). Só números nossos.
#   python conferir_miras.py
import json, math, sys
from sobrepor import linhas, CONF

sys.stdout.reconfigure(encoding='utf-8')
f = json.load(open(r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/refs/p90.json', encoding='utf-8'))
pc, mi = f['pecas'], f['pontos']['miras']


def circulo(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


meia = mi['baseMeia']
cand = {'pecas': [
    {'nome': 'base F', 'contorno': pc['baseMiraFrente'], 'lados': [meia, -meia], 'cor': '#ff8800', 'arestas': True},
    {'nome': 'base T', 'contorno': pc['baseMiraTras'], 'lados': [meia, -meia], 'cor': '#ff8800', 'arestas': True},
    {'nome': 'orelha F', 'contorno': pc['orelhaMiraFrente'], 'lados': mi['orelhasFrente'][::-1], 'cor': '#00ff00', 'arestas': True},
    {'nome': 'orelha T', 'contorno': pc['orelhaMiraTras'], 'lados': mi['orelhasTras'][::-1], 'cor': '#00ff00', 'arestas': True},
    {'nome': 'botão F', 'contorno': circulo(*mi['botoes']['frente'], mi['botoes']['raio']), 'lados': [mi['botoes']['lado'], meia], 'cor': '#ff4444', 'arestas': False},
    {'nome': 'botão T', 'contorno': circulo(*mi['botoes']['tras'], mi['botoes']['raio']), 'lados': [mi['botoes']['lado'], meia], 'cor': '#ff4444', 'arestas': False},
    {'nome': 'parafuso F', 'contorno': circulo(*mi['parafusos']['frente']['centro'], mi['parafusos']['frente']['raio']), 'lados': [meia + 0.9], 'cor': '#00ffff'},
    {'nome': 'parafuso T', 'contorno': circulo(*mi['parafusos']['tras']['centro'], mi['parafusos']['tras']['raio']), 'lados': [meia + 0.9], 'cor': '#00ffff'},
    {'nome': 'furos', 'contorno': circulo(*mi['furosOrelha']['centro'], mi['furosOrelha']['raio'], mi['furosOrelha']['n']), 'lados': [mi['orelhasTras'][1]],
     'cor': '#ffffff'},
], 'pontos': [['botão F', (*mi['botoes']['frente'], mi['botoes']['lado']), '#ff4444'],
              ['parafuso F', (*mi['parafusos']['frente']['centro'], meia + 0.9), '#00ffff'],
              ['botão T', (*mi['botoes']['tras'], mi['botoes']['lado']), '#ff4444'],
              ['parafuso T', (*mi['parafusos']['tras']['centro'], meia + 0.9), '#00ffff']],
    'deslocamentoLado': -3.9}
json.dump(linhas(cand, 'icone'), open(f'{CONF}/conf_icone.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(linhas(cand, 'video'), open(f'{CONF}/conf_video.json', 'w', encoding='utf-8'), ensure_ascii=False)
for cam in ('icone', 'video'):
    print(cam, [(n, round(u, 1), round(v, 1)) for u, v, n, _ in linhas(cand, cam)['pontos']])
