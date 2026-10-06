"""A pega de uma arma construída num JSON (a base da comparação da Tarefa 16: os ângulos de cada osso a até 0,05°).
Lê o .glb (o bloco JSON e o binário do glTF) e o relatório: a rotação de cada osso de dedo no quadro do clipe
`empunhadura` (os 17 de cada mão da regra), o referencial do osso `mao` de cada mão (os nós `pega_mao_*`), as flexões
do relatório (`angulos`) e os graus do polegar.
    pega_json.py <arma> <saida.json>        (a arma em trabalho-4.1d/assets/armas/<arma>/)
    pega_json.py --comparar <antes.json> <depois.json>
"""
import json
import math
import struct
import sys

import numpy as np

RAIZ = r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\assets\armas'
TIPOS = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}
COMPONENTES = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
MM_POR_U = 25.4  # o .glb das armas em u (a polegada: 25,4 mm), como o jogo


def ler_glb(caminho):
    with open(caminho, 'rb') as f:
        dados = f.read()
    _magia, _versao, _total = struct.unpack_from('<III', dados, 0)
    i, js, binario = 12, None, None
    while i < len(dados):
        n, tipo = struct.unpack_from('<II', dados, i)
        bloco = dados[i + 8:i + 8 + n]
        if tipo == 0x4E4F534A:
            js = json.loads(bloco.decode('utf-8'))
        elif tipo == 0x004E4942:
            binario = bloco
        i += 8 + n
    return js, binario


def acessor(js, binario, k):
    a = js['accessors'][k]
    v = js['bufferViews'][a['bufferView']]
    tipo, comp = TIPOS[a['componentType']], COMPONENTES[a['type']]
    inicio = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    passo = v.get('byteStride')
    if passo and passo != np.dtype(tipo).itemsize * comp:
        raise ValueError('acessor intercalado')
    return np.frombuffer(binario, tipo, a['count'] * comp, inicio).reshape(a['count'], comp)


def extrair(arma):
    js, binario = ler_glb(f'{RAIZ}\\{arma}\\{arma}.glb')
    rel = json.load(open(f'{RAIZ}\\{arma}\\{arma}.relatorio.json', encoding='utf-8'))
    nos = js['nodes']
    clipe = next(a for a in js['animations'] if a['name'] == 'empunhadura')
    dedos = {}
    for canal in clipe['channels']:
        if canal['target']['path'] != 'rotation':
            continue
        nome = nos[canal['target']['node']]['name']
        q = acessor(js, binario, clipe['samplers'][canal['sampler']]['output'])[0]
        dedos[nome] = [float(c) for c in q]
    maos = {n['name']: {'posicao': n.get('translation', [0, 0, 0]), 'rotacao': n.get('rotation', [0, 0, 0, 1])}
            for n in nos if n['name'].startswith('pega_mao_')}
    emp = rel['empunhadura']
    return {'arma': arma, 'hash': rel['entradas']['hash'], 'dedos': dedos, 'maos': maos,
            'angulos': {l: emp[l].get('angulos') for l in emp['maos']},
            'polegar': {l: (emp[l].get('polegar') or {}).get('graus') for l in emp['maos']}}


def angulo(q1, q2):
    d = abs(sum(a * b for a, b in zip(q1, q2)))
    return math.degrees(2 * math.acos(min(1.0, d)))


def comparar(antes, depois):
    a, b = json.load(open(antes, encoding='utf-8')), json.load(open(depois, encoding='utf-8'))
    ossos = sorted(set(a['dedos']) & set(b['dedos']))
    difs = {o: round(angulo(a['dedos'][o], b['dedos'][o]), 4) for o in ossos}
    pior = max(difs.items(), key=lambda kv: kv[1])
    maos = {m: {'posicaoMM': round(MM_POR_U * math.dist(a['maos'][m]['posicao'], b['maos'][m]['posicao']), 4),
                'rotacaoGraus': round(angulo(a['maos'][m]['rotacao'], b['maos'][m]['rotacao']), 4)}
            for m in sorted(set(a['maos']) & set(b['maos']))}
    flex = {}
    for lado in a['angulos']:
        for osso, g in (a['angulos'][lado] or {}).items():
            flex[f'{osso}_{lado}'] = round(abs(g - (b['angulos'].get(lado) or {}).get(osso, float('nan'))), 3)
    print(json.dumps({'ossos': len(ossos), 'faltam': sorted(set(a['dedos']) ^ set(b['dedos'])), 'piorOsso': pior,
                      'acimaDe005': {o: d for o, d in difs.items() if d > 0.05}, 'maos': maos,
                      'flexoesPior': max(flex.items(), key=lambda kv: kv[1]) if flex else None,
                      'polegar': {'antes': a['polegar'], 'depois': b['polegar']}}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == '--comparar':
        comparar(sys.argv[2], sys.argv[3])
    else:
        json.dump(extrair(sys.argv[1]), open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('ok', sys.argv[1])
