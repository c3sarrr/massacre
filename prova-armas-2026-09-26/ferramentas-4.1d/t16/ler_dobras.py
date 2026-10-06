"""Lê as linhas DOBRAS de um log de dobras_peca.py e mostra o resumo.
    ler_dobras.py <log> [arestas por cruzamento]
"""
import json
import sys

N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for linha in open(sys.argv[1], encoding='utf-8', errors='replace'):
    if not linha.startswith('DOBRAS '):
        continue
    _, resto = linha.split(' ', 1)
    i = resto.index(' {')
    nome, d = resto[:i], json.loads(resto[i + 1:])
    print('==', nome, '| largura', d['larguraMM'], 'mm | cruzamentos com o chanfro sem os cortes finais:',
          d['comChanfro'])
    print('   pilha:', [m for m, _t in d['pilha']])
    print('   sem o chanfro:', [(s['meio'], s['segmentoMM']) for s in d['semChanfro']])
    for c in d['tudo']:
        print('   FINAL', c['meio'], '| segmento', c['segmentoMM'], 'mm | normais', c['normais'], '| áreas',
              c['areasMM2'], '| ao de antes', c['antesMaisPertoMM'], 'mm')
        for e in c['arestas'][:N]:
            print('       ', e)
