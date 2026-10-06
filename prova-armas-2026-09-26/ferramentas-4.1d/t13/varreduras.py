"""As varreduras da Tarefa 13 (a AWP na mão), para pôr na fila do servidor.py (cada uma num trabalho: `import varreduras
as V; V.mao_de_apoio_1()` etc., depois do `awp_pega.carregar()`). Cada linha RESUMO é uma pega; o JSON inteiro de cada
varredura vai para <TRABALHO>/<nome>.json. Os resultados estão no registro da Tarefa 13 no plano da 4.1d.

As pegas da mão de apoio são a LATERAL com a âncora da palma a partir do soquete `mao_e` (mm), as giradas em volta do X
(a inclinação), do Y (no plano da face: positiva leva as pontas para a frente) e do Z (a guinada: o dorso para o
jogador) e o lado do polegar 'baixo' (graus do −Z para o −Y); as da mão do gatilho, a direita da `rifle` com o polegar
pelo buraco do polegar, a âncora da MCP do indicador a partir do ponto do gatilho (mm), a diagonal e a altura do ponto
no gatilho. `sem_polegar=True` deixa o polegar no afastado da chegada (o furo leva 2 a 3 min por pega; os dedos, 5 s).
"""
import itertools
import json
import math

import awp_pega as A
from armas import empunhadura_pega as EP


def _esquerda(z, inc, gir, guin, lado=None):
    cfg = {'ancora': {'ponto': 'palma', 'de': 'soquete', 'mm': [0.0, 0.0, z]},
           'giros': [['X', inc], ['Y', gir], ['Z', guin]]}
    if lado is not None:
        a = math.radians(lado)
        cfg['polegar'] = {'lado': [0.0, -math.sin(a), -math.cos(a)], 'peso': 4.0}
    return cfg


def _direita(dx, dz, diagonal, altura=0.74, folga=1.0, giro=None, eixo=None):
    cfg = {'ancora': {'ponto': 'mcp_indicador', 'de': 'gatilho', 'mm': [dx, -40.0, dz]}, 'diagonal': diagonal,
           'gatilho': {'altura': altura, 'abertura': 20.0, 'raio': 8.0, 'folga': folga}}
    if giro is not None:
        cfg['giros'] = [['Z', giro]]
    if eixo is not None:
        cfg['polegar'] = {'furo': 'buracoPolegar', 'saida': [0.0, 1.0, 0.0], 'eixo': list(eixo)}
    return cfg


def _rodar(nome, lado, cfgs, sem_polegar=False):
    passar = EP.polegar_furo.passar
    if sem_polegar:
        EP.polegar_furo.passar = lambda col, mao, m, na, furo, saida, eixo, inicio=None: (m, {'semPolegar': True})
    res = []
    try:
        for chave, cfg in cfgs:
            s = A.mao(lado, cfg)
            res.append(s)
            if lado == 'e':
                ll = s.get('ladosLateral') or {}
                extra = {'medias': ll.get('mediasGraus'), 'polpas': ll.get('polpasMM'), 'polegar': ll.get('polegarGraus'),
                         'contatoPolegar': (s.get('contatosMM') or {}).get('polegar'),
                         'dorsoAoJogador': s.get('dorsoAoJogadorGraus'), 'distalAFrente': s.get('distalAFrenteGraus'),
                         'bipe': (s.get('folgasMM') or {}).get('bipe')}
            else:
                pol = s.get('polegar') or {}
                extra = {'indicador': (s.get('indicador') or {}).get('graus'),
                         'polpaAoAlvo': (s.get('indicador') or {}).get('polpaAoAlvoMM'),
                         'furo': s.get('polegarNoFuro'), 'polegar': pol.get('graus'), 'distal': s.get('distalDoPolegar'),
                         'juntos': {k: v[0] for k, v in (s.get('juntosMM') or {}).items()}}
            print('RESUMO', chave, s.get('erro', '')[:200], json.dumps(extra, ensure_ascii=False),
                  'contatos', s.get('contatosMM'), 'pen', s.get('penetracaoMM'), 'problemas', s.get('problemas'),
                  flush=True)
    finally:
        EP.polegar_furo.passar = passar
    with open(f'{A.TRABALHO}/{nome}.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, default=str)


def mao_de_apoio_1():
    """A primeira: a altura, a inclinação e a girada no plano da face (a guinada da regra, 20°)."""
    g = itertools.product((-62.5, -67.5, -72.5, -77.5), (-12.5, -7.5, -2.5), (0.0, 15.0))
    _rodar('varre_e1', 'e', [((z, i, y), _esquerda(z, i, y, 20.0)) for z, i, y in g])


def mao_de_apoio_2():
    """A grade com a guinada: 81 pegas."""
    g = itertools.product((-67.5, -72.5, -77.5), (-10.0, -7.5, -5.0), (0.0, 7.5, 15.0), (15.0, 20.0, 25.0))
    _rodar('varre_e2', 'e', [((z, i, y, w), _esquerda(z, i, y, w)) for z, i, y, w in g])


def mao_de_apoio_3():
    """A fina, em volta da regra."""
    g = itertools.product((-70.0, -72.5, -75.0), (-10.0, -8.75, -7.5), (5.0, 7.5, 10.0))
    _rodar('varre_e3', 'e', [((z, i, y), _esquerda(z, i, y, 20.0)) for z, i, y in g])


def mao_de_apoio_4():
    """O lado do polegar 'baixo' (20°, 40° e 50°; a regra, 30°)."""
    g = itertools.product((20.0, 40.0, 50.0), (-70.0, -72.5, -75.0), (5.0, 7.5))
    _rodar('varre_e4', 'e', [((lado, z, y), _esquerda(z, -8.75, y, 20.0, lado)) for lado, z, y in g])


def mao_do_gatilho_dedos():
    """Os dedos sem o polegar: a âncora, a diagonal e a altura do ponto no gatilho (a do fuzil, 60 %, e a da M4A4)."""
    g1 = itertools.product((-27.6, -32.0, -36.0), (-9.0, -5.0, -1.0, 3.0), (15.0, 25.0))
    g2 = itertools.product((-36.0, -42.0, -48.0), (-7.0, -12.0, -17.0), (0.6, 0.74), (1.0, -0.25))
    g3 = itertools.product((-50.0, -55.0, -60.0), (-4.0, -9.0, -14.0), (5.0, 15.0, 25.0))
    cfgs = ([((dx, dz, d, 0.6), _direita(dx, dz, d, 0.6)) for dx, dz, d in g1]
            + [((dx, dz, 15.0, a, f), _direita(dx, dz, 15.0, a, f)) for dx, dz, a, f in g2]
            + [((dx, dz, d), _direita(dx, dz, d)) for dx, dz, d in g3])
    _rodar('varre_d', 'd', cfgs, sem_polegar=True)


def mao_do_gatilho_polegar():
    """O polegar pelo buraco: o eixo dele e o giro da mão em volta do punho, e as vizinhas da regra."""
    eixos = ((1.0, 0.0, 0.0), (1.0, 0.0, -0.6), (1.0, 0.0, 0.6))
    cfgs = [((g, e), _direita(-50.0, -14.0, 5.0, giro=g, eixo=e)) for g in (0.0, -15.0, 15.0) for e in eixos]
    cfgs += [((dx, dz, d), _direita(dx, dz, d)) for dx, dz, d in (
        (-50.0, -13.0, 4.0), (-47.5, -13.0, 4.0), (-52.5, -13.0, 4.0), (-50.0, -11.0, 4.0), (-50.0, -15.0, 4.0),
        (-50.0, -13.0, 2.0), (-50.0, -13.0, 6.0))]
    _rodar('varre_d_polegar', 'd', cfgs)
