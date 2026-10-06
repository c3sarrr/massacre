# As peças candidatas da parte de cima do CS2 (candidato.json: cada peça um contorno de lado (x, alto) extrudado entre
# dois lados) projetadas pelas câmeras do ajuste conjunto (conjunto.json) no ícone e no quadro do vídeo, para conferir
# por cima das imagens (o ícone na grade.html `dados`; o vídeo pelo window.__linhas da aba). Só números nossos.
#   python sobrepor.py candidato.json
import json, sys
import numpy as np
from cameras import projetar, S

CONF = r'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/conferencia/p90'
cj = json.load(open('conjunto.json', encoding='utf-8'))
CAMS = {'icone': (np.array(cj['icone']['p']), 512, 384), 'video': (np.array(cj['video']['p']), 1920, 1080)}


def proj(cam, pts):
    p, W, H = CAMS[cam]
    X = np.array([[x * S, l * S, a * S] for x, a, l in pts])
    uv, _ = projetar(p, X, W, H)
    return [[round(float(u), 2), round(float(v), 2)] for u, v in uv]


def linhas(cand, cam):
    out = {'linhas': [], 'pontos': []}
    # o deslocamento de lado do grupo de cima no referencial das câmeras (o ajuste põe o grupo todo, as duas miras simétricas
    # em volta dele, ~3,9 mm à direita: o erro dos lados dos parafusos da face esquerda); o candidato fica centrado em 0
    d = cand.get('deslocamentoLado', 0.0)
    for peca in cand['pecas']:
        c = peca['contorno']
        cor = peca.get('cor', '#ff00ff')
        lados = [l + d for l in peca['lados']]
        for k, l in enumerate(lados):
            out['linhas'].append({'cor': cor if k == 0 else peca.get('corLonge', cor + '88'), 'pts': proj(cam, [(x, a, l) for x, a in c]),
                                  'fechar': peca.get('fechar', True), 'nome': f"{peca['nome']} {l:+.1f}"})
        if len(lados) == 2 and peca.get('arestas', False):
            for x, a in c:
                out['linhas'].append({'cor': peca.get('corLonge', cor + '88'), 'pts': proj(cam, [(x, a, lados[0]), (x, a, lados[1])]), 'fechar': False})
    for nome, (x, a, l), cor in cand.get('pontos', []):
        u, v = proj(cam, [(x, a, l + d)])[0]
        out['pontos'].append([u, v, nome, cor])
    return out


if __name__ == '__main__':
    cand = json.load(open(sys.argv[1], encoding='utf-8'))
    json.dump(linhas(cand, 'icone'), open(f'{CONF}/cand_icone.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(linhas(cand, 'video'), open(f'{CONF}/cand_video.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('ok')
