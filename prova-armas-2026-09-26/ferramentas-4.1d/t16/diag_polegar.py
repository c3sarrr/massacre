"""Por que o polegar de uma mão cruza a arma (a reprovação da AK na Tarefa 16: na geometria nova, o polegar da solução
cruzava mesmo com a MCP e a IP abertas, a palma chegava de novo com a CMC aberta e parava 16,4 mm antes do ponto de
chegada, com o contato da palma a 1,49 mm): a pega de um lado pelo banco (t14/pega_banco.py) sobre uma .blend da
conferência com as luvas montadas, e em cada assentar do polegar na arma (empunhadura_polegar._assentar_na_arma) as
três partes do `_cruza` na solução da IK e com a MCP e a IP abertas — o polegar na própria mão, a dobra da pele da
tenar e a entrada na arma das falanges e da tenar —, com os vértices que mais entram (o osso, a posição, a peça mais
perto, o ponto e a normal dela). Também o alvo da polpa (empunhadura_polegar.alvo_na_arma), no referencial da arma, e,
em cada IK com a arma (empunhadura_polegar.resolver), o custo da solução (o das cápsulas com a dobra da tabela e o do
refino pela malha) e o dos graus de `--outros` (os totais de outra .blend, para comparar), com o `_cruza` deles.
    blender -b --factory-startup -P diag_polegar.py -- <arma> <categoria> <lado: d ou e> <.blend> <pasta>
        [--outros <json: lista de graus totais>]
"""
import json
import os
import sys

a = sys.argv[sys.argv.index('--') + 1:]
ARMA, CATEGORIA, LADO, BLEND, TRABALHO = a[:5]
OUTROS = json.loads(a[a.index('--outros') + 1]) if '--outros' in a else []
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 't14'))
import pega_banco as B  # noqa: E402
from mathutils import Vector  # noqa: E402

from armas import empunhadura  # noqa: E402

EPO = B.EPO
B.configurar(ARMA, CATEGORIA, trabalho=TRABALHO)
B.CFG['blend'] = BLEND
B.carregar()
por_peca = {k: B.EA.Arma([o]) for k, o in B.C['perto'].items() if not k.startswith('_')}


def mais_perto(q, n=2):
    perto = []
    for nome, arma in por_peca.items():
        dd = arma.distancia(q, 30.0)
        if dd is not None:
            perto.append((abs(dd), dd, nome))
    perto.sort()
    return [(nome, round(dd, 3)) for _a, dd, nome in perto[:n]]


def partes(col, m, livre, resto, na):
    pts = na.pontos(m.pose())
    mao = col.profundidade_nos_pontos(pts, livre, resto, empunhadura.PERTO_MM)
    dobra = EPO.dobra_da_tenar(col, pts)
    indices = na.vertices(EPO.LIVRE + EPO.TENAR)
    entram = []
    for i in indices:
        c = na._cede(i)
        d = na.arma.distancia(Vector(pts[i]), B.EA.PERTO_DA_ARMA_MM + c)
        if d is not None and -(d + c) > 0.0:
            entram.append((-(d + c), i))
    entram.sort(reverse=True)
    lista = []
    for e, i in entram[:6]:
        q = Vector(pts[i])
        co, n, _k, _d = na.arma.bvh.find_nearest(q)
        lista.append({'entra': round(e, 3), 'vertice': i, 'osso': col.dono[i], 'pos': [round(c, 2) for c in q],
                      'pecas': mais_perto(q), 'ponto': [round(c, 2) for c in co], 'normal': [round(c, 3) for c in n]})
    return {'naMao': round(mao, 3), 'dobraTenar': round(dobra, 3),
            'naArma': round(entram[0][0], 3) if entram else 0.0, 'vertices': lista}


original_assentar = EPO._assentar_na_arma
original_alvo = EPO.alvo_na_arma
assentos = []


def assentar(col, lim, m, cadeia, ik, livre, resto, na):
    aberto = dict(ik, mcp=lim['mcp'][0], ip=lim['ip'][0])
    saida = {'n': len(assentos), 'ik': EPO.totais(B.C['mao'], ik),
             'naIK': partes(col, EPO._com_graus(m, cadeia, ik), livre, resto, na),
             'aberto': partes(col, EPO._com_graus(m, cadeia, aberto), livre, resto, na)}
    try:
        r = original_assentar(col, lim, m, cadeia, ik, livre, resto, na)
        saida['resultado'] = 'assentou'
        return r
    except empunhadura.PolegarCruza as erro:
        saida['resultado'] = f'PolegarCruza: {erro}'
        raise
    finally:
        assentos.append(saida)
        print('ASSENTAR', json.dumps(saida, ensure_ascii=False), flush=True)


def alvo(cadeia, na, m, lim, lado, peso_lado):
    a, n = original_alvo(cadeia, na, m, lim, lado, peso_lado)
    print('ALVO', json.dumps({'ponto': [round(c, 2) for c in na.encaixe @ a],
                              'normal': [round(c, 3) for c in (na.encaixe.to_3x3() @ n).normalized()],
                              'pecas': mais_perto(na.encaixe @ a)}, ensure_ascii=False), flush=True)
    return a, n


original_resolver = EPO.resolver


def custos(cadeia, g, alvo_l, normal_l, lim, na, m, eixo):
    """(o custo das cápsulas com a dobra da tabela, o do refino pela malha) nos graus `g` (além do repouso)."""
    tabela = EPO.tabela_da_dobra(na.col, cadeia, lim)
    capsulas = EPO._custo(cadeia, g, alvo_l, normal_l, na, eixo)
    pts = na.pontos(EPO._com_graus(m, cadeia, g).pose())
    vertices = na.vertices(EPO.LIVRE + EPO.TENAR)
    entrada = na.entrada_quadrada(pts, vertices)
    dobra_t = EPO.dobra_da_tenar(na.col, pts)
    pele = EPO.dobra_da_pele(na.col, pts)
    malha = capsulas + EPO.PESO_MALHA ** 2 * (entrada + dobra_t ** 2) + EPO._custo_da_dobra(pele)
    return {'capsulas': round(capsulas, 3), 'tabela': round(EPO._custo_da_dobra(EPO._na_tabela(tabela, g)), 3),
            'malha': round(malha, 3), 'entradaQuadrada': round(entrada, 5), 'dobraTenar': round(dobra_t, 3),
            'dobraPele': round(pele, 3)}


def resolver(cadeia, alvo_l, normal_l, lim, inicio=None, na=None, m=None, eixo=None):
    g = original_resolver(cadeia, alvo_l, normal_l, lim, inicio, na, m, eixo)
    if na is not None:
        livre, resto = EPO._livre_e_resto(na.col)
        rep = B.C['mao'].rep
        print('IK', json.dumps({'graus': EPO.totais(B.C['mao'], g), 'inicio': inicio and EPO.totais(B.C['mao'], inicio),
                                'custos': custos(cadeia, g, alvo_l, normal_l, lim, na, m, eixo)}), flush=True)
        for t in OUTROS:
            go = {'abducao': t['abducao'] - rep['polegarAbducao'], 'cmc': t['cmc'], 'rotacao': t['rotacao'],
                  'mcp': t['mcp'] - rep['polegarMcp'], 'ip': t['ip'] - rep['polegarIp'], 'desvio': t['desvio']}
            print('IK-OUTRO', json.dumps({'graus': t, 'custos': custos(cadeia, go, alvo_l, normal_l, lim, na, m, eixo),
                                          'cruza': partes(na.col, EPO._com_graus(m, cadeia, go), livre, resto, na)},
                                         ensure_ascii=False), flush=True)
    return g


EPO._assentar_na_arma = assentar
EPO.alvo_na_arma = alvo
EPO.resolver = resolver
s = B.mao(LADO)
print('FIM', json.dumps({'assentos': len(assentos)}), flush=True)
