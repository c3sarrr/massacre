"""A diferença entre os dois lados da arma no chanfro depois do desdobrar (os despejos do perdas.py): para cada aresta
chanfrada com a do outro lado (o meio espelhado em y = 0 a até 5 µm), a largura de cada lado; soma |diferença| vezes o
comprimento e lista os maiores pares."""
import json, sys, os, glob
import numpy as np
pasta = sys.argv[1]
for arq in sorted(glob.glob(os.path.join(pasta, '*.json'))):
    d = json.load(open(arq, encoding='utf-8'))
    L = d['largura']
    ar = d['arestas']
    meios = np.array([np.mean(e['pontas'], axis=0) for e in ar]) if ar else np.zeros((0, 3))
    comps = np.array([np.linalg.norm(np.subtract(*e['pontas'])) for e in ar]) if ar else np.zeros(0)
    tot, lista = 0.0, []
    for i, e in enumerate(ar):
        if meios[i][1] <= 0.003:
            continue
        alvo = meios[i] * np.array([1, -1, 1])
        dist = np.linalg.norm(meios - alvo, axis=1)
        j = int(np.argmin(dist))
        if dist[j] > 0.005 or abs(comps[j] - comps[i]) > 0.005:
            continue
        dif = abs(e['depois'] - ar[j]['depois']) * L
        tot += dif * comps[i]
        if dif > 0.05:
            lista.append((round(dif * comps[i], 1), round(comps[i], 1), meios[i].round(1).tolist(), round(e['depois'] * L, 3), round(ar[j]['depois'] * L, 3)))
    lista.sort(reverse=True)
    print(os.path.basename(arq)[:-5], 'assimetria', round(tot, 1), 'mm²', lista[:4])
