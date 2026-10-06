"""As varreduras da Tarefa 14 (a Nova na mão), para pôr na fila do servidor (t13/servidor.py; cada uma num trabalho:
`import varreduras_nova as V; V.direita_dedos()` etc., depois do `pega_banco.carregar()`). Cada linha RESUMO é uma
pega; o JSON inteiro de cada varredura vai para <TRABALHO>/<nome>.json. Os resultados estão no registro da Tarefa 14 no
plano da 4.1d.

A mão de apoio é a LATERAL na bomba (o soquete `bomba`), com a âncora da palma a partir dele (mm) e as giradas em volta
do X (a inclinação), do Y (no plano da face: positiva leva as pontas para a frente e o lado do polegar para cima) e do
Z (a guinada: o dorso para o jogador); a mão do gatilho, a direita do fuzil no pescoço da coronha, com a âncora da MCP
do indicador a partir do ponto do gatilho (mm), a diagonal, o giro em volta do eixo do pescoço e a altura do ponto no
gatilho. `sem_polegar=True` deixa o polegar no afastado da chegada (o deitado leva de 20 s a 8 min por pega; os
dedos, segundos): a validação acusa "o polegar não deita", e o resto da pega vale. As varreduras do polegar 'borda'
da mão de apoio partem da base de prova `escopeta_borda` (pega_banco.base_da_prova): a regra escopeta ficou com o
'baixo'; as da mão do gatilho e as do 'baixo' trocam todas as chaves que a regra tem.
"""
import copy
import itertools
import json

import pega_banco as B
from armas import empunhadura_pega as EP
from armas import empunhadura_regras as ER


def esquerda(z, inc, gir, guin, x=0.0, polegar=None):
    cfg = {'ancora': {'ponto': 'palma', 'de': 'soquete', 'mm': [x, 0.0, z]},
           'giros': [['X', inc], ['Y', gir], ['Z', guin]]}
    if polegar is not None:
        cfg['polegar'] = polegar
    return cfg


def direita(dx, dz, diagonal, giro=0.0, altura=0.74, folga=1.0, dy=-40.0, afastado=True, polegar=None):
    cfg = {'ancora': {'ponto': 'mcp_indicador', 'de': 'gatilho', 'mm': [dx, dy, dz]}, 'diagonal': diagonal,
           'giros': [['Z', giro]], 'gatilho': {'altura': altura, 'abertura': 20.0, 'raio': 8.0, 'folga': folga},
           'polegar_afastado': afastado}
    if polegar is not None:
        cfg['polegar'] = polegar
    return cfg


def rodar(nome, lado, cfgs, sem_polegar=False, base=None):
    deitar = EP._deitar
    if sem_polegar:
        def _sem(col, na, mao, m, p, inicio=None, evitar=None, sobre=None, fixos=None):
            return m, {'erro': 'sem o polegar (a varredura dos dedos)'}
        EP._deitar = _sem
    res = []
    try:
        for chave, cfg in cfgs:
            s = B.mao(lado, cfg, base=base)
            res.append(s)
            ll = s.get('ladosLateral') or {}
            pol = s.get('polegar') or {}
            extra = {'medias': ll.get('mediasGraus'), 'polpas': ll.get('polpasMM'), 'direita': ll.get('direitaMM'),
                     'dorso': ll.get('dorsoGraus'), 'polegarGraus': ll.get('polegarGraus'),
                     'dorsoJog': s.get('dorsoAoJogadorGraus'), 'indicador': (s.get('indicador') or {}).get('graus'),
                     'polpaAlvo': (s.get('indicador') or {}).get('polpaAoAlvoMM'),
                     'polegar': {k: pol.get(k) for k in ('curvaGraus', 'desvioDoEixoGraus', 'coladoMM', 'polpaEncostaMM')},
                     'distal': s.get('distalDoPolegar'), 'ponta': s.get('pontaDoPolegar'),
                     'juntos': {k: v[0] for k, v in (s.get('juntosMM') or {}).items()},
                     'alto': s.get('altoDoDedoMM'), 'atravessa': (s.get('luva') or {}).get('atravessaMM')}
            print('RESUMO', json.dumps(chave), s.get('erro', '')[:160], json.dumps(extra, ensure_ascii=False),
                  'contatos', json.dumps(s.get('contatosMM')), 'pen', s.get('penetracaoMM'),
                  'problemas', json.dumps(s.get('problemas'), ensure_ascii=False)[:600], flush=True)
    finally:
        EP._deitar = deitar
    with open(f"{B.CFG['trabalho']}/{nome}.json", 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, default=str)


def direita_dedos_1():
    """A mão do gatilho no pescoço: a âncora da MCP do indicador, a diagonal (sem o polegar)."""
    g = itertools.product((-35.0, -45.0, -55.0), (5.0, -5.0, -15.0), (0.0, 15.0, 30.0))
    rodar('nova_d1', 'd', [((dx, dz, d), direita(dx, dz, d)) for dx, dz, d in g], sem_polegar=True)


def esquerda_dedos_1():
    """A mão de apoio na bomba: a girada no plano da face (o lado do polegar para cima), a altura e a inclinação."""
    g = itertools.product((0.0, 30.0, 50.0, 70.0, 90.0), (-62.5, -50.0, -40.0, -30.0), (-12.5, 0.0))
    rodar('nova_e1', 'e', [((y, z, i), esquerda(z, i, y, 20.0)) for y, z, i in g], sem_polegar=True,
          base='escopeta_borda')


def direita_dedos_2():
    """A MCP do indicador mais alta (logo abaixo do receptor) e o giro da mão em volta do pescoço (sem o polegar)."""
    g = itertools.product((-38.0, -44.0, -50.0), (5.0, 10.0, 15.0), (0.0, 15.0), (0.0, -15.0))
    rodar('nova_d2', 'd', [((dx, dz, d, gi), direita(dx, dz, d, gi)) for dx, dz, d, gi in g], sem_polegar=True)


def esquerda_dedos_2():
    """A fina em volta da girada de 50° a 65° com a palma alta na face (sem o polegar)."""
    g = itertools.product((50.0, 55.0, 60.0, 65.0), (-25.0, -30.0, -35.0), (-12.5, -6.0, 0.0))
    rodar('nova_e2', 'e', [((y, z, i), esquerda(z, i, y, 20.0)) for y, z, i in g], sem_polegar=True,
          base='escopeta_borda')


def direita_dedos_3():
    """A luva comprimida no guarda-mato de 20 mm (a folga de −0,25 mm da M4A4) em volta da melhor âncora (sem o
    polegar)."""
    g = itertools.product((-45.0, -50.0, -55.0), (5.0, 10.0), (0.0, 8.0), (-15.0, -25.0))
    rodar('nova_d3', 'd', [((dx, dz, d, gi), direita(dx, dz, d, gi, folga=-0.25)) for dx, dz, d, gi in g],
          sem_polegar=True)


POLEGAR_PESCOCO = {'deitado': True, 'face': [0.0, 0.0, 1.0], 'eixo': [1.0, 0.0, 0.36]}


def direita_polegar_1():
    """Com o polegar deitado no pescoço (o eixo pela rampa de cima do pescoço, 20°): a âncora, a altura e o giro."""
    g = itertools.product((-52.5, -55.0, -57.5), (8.0, 12.0, 16.0), (-5.0, -15.0, -25.0))
    rodar('nova_dp1', 'd', [((dx, dz, gi), direita(dx, dz, 0.0, gi, folga=-0.25, polegar=POLEGAR_PESCOCO))
                            for dx, dz, gi in g])


def direita_polegar_2():
    """O giro positivo em volta do pescoço (a palma sobe por cima dele e a base do polegar fica no alto: com o giro
    negativo da direita_polegar_1, o polegar cruzava o alto na diagonal, a 41° a 60° da frente) e a diagonal."""
    g = itertools.product((-52.5, -57.5), (8.0, 16.0, 24.0), (5.0, 15.0, 25.0), (-10.0, 0.0, 10.0))
    rodar('nova_dp2', 'd', [((dx, dz, gi, d), direita(dx, dz, d, gi, folga=-0.25, polegar=POLEGAR_PESCOCO))
                            for dx, dz, gi, d in g])


def esquerda_borda_1(parte):
    """O polegar 'borda' (deitado na borda de cima, apontando para a boca) com a mão girada no plano da face até os
    dedos deitarem para a frente (de 50° a 65° o polegar cruzava a mão, 2,8 a 6,1 mm, ou apontava a 55° da frente): a
    girada, a altura da palma e a inclinação (positiva, a palma para baixo, por cima da quina de cima). `parte` 0 ou 1:
    a metade da grade (um servidor cada)."""
    g = list(itertools.product((80.0, 90.0, 100.0), (-20.0, -10.0), (-12.5, 15.0, 35.0)))[parte::2]
    rodar(f'nova_eb1_{parte}', 'e', [((y, z, i), esquerda(z, i, y, 20.0)) for y, z, i in g], base='escopeta_borda')


def direita_polegar_3():
    """Entre o giro de −15° (o polegar cruzando o alto do pescoço na diagonal, a ponta no ar à esquerda) e o de −25° (o
    polegar para a frente, mas pelo lado direito, e o indicador a 14 mm do gatilho), com a mão mais alta."""
    g = itertools.product((-52.5, -55.0, -57.5), (12.0, 16.0, 20.0), (-17.5, -20.0, -22.5))
    rodar('nova_dp3', 'd', [((dx, dz, gi), direita(dx, dz, 0.0, gi, folga=-0.25, polegar=POLEGAR_PESCOCO))
                            for dx, dz, gi in g])


# o polegar por baixo da bomba, escondido (o 'baixo' da LATERAL, como na AWP): a B1 da prova (a palma 62,5 mm abaixo do
# soquete, sem girada no plano da face) passou em todas as validações, com o polegar a 67,5° do limite de 70°
BAIXO = {'lateral': {**ER.LATERAL['lateral'], 'polegar': 'baixo'}, 'polegar': copy.deepcopy(ER.LATERAL['polegar'])}


def esquerda_baixo_1():
    """A fina em volta da B1 (o polegar 'baixo'): a altura da palma, a inclinação, a girada no plano da face e a
    guinada."""
    g = itertools.product((-65.0, -62.5, -60.0), (-15.0, -10.0), (-5.0, 0.0, 5.0), (15.0, 25.0))
    rodar('nova_eb2', 'e', [((z, i, y, gu), {**esquerda(z, i, y, gu), **BAIXO}) for z, i, y, gu in g])


def direita_polegar_4():
    """O polegar deitado na metade direita do alto do pescoço (a face pedida inclinada para a direita, 15° e 25°: no
    alto inteiro ele cruzava na diagonal, a 39° a 56° da frente), com o giro de −10° a −20°."""
    faces = ((0.0, -0.2588, 0.9659), (0.0, -0.4226, 0.9063))
    g = itertools.product(faces, (-52.5, -55.0), (12.0, 16.0), (-10.0, -15.0, -20.0))
    rodar('nova_dp4', 'd', [((f[1], dx, dz, gi), direita(dx, dz, 0.0, gi, folga=-0.25,
                                                         polegar={**POLEGAR_PESCOCO, 'face': list(f)}))
                            for f, dx, dz, gi in g])


def direita_polegar_5():
    """A fina em volta da (−55, 16, −5) da direita_polegar_1, a única que passou em tudo (o polegar deitado por cima
    do pescoço na diagonal, a 46° da frente; a luva 0,25 mm dentro da arma, perto do limite de 0,3)."""
    g = itertools.product((-54.0, -55.0, -56.0), (14.0, 16.0, 18.0), (-2.5, -5.0, -7.5))
    rodar('nova_dp5', 'd', [((dx, dz, gi), direita(dx, dz, 0.0, gi, folga=-0.25, polegar=POLEGAR_PESCOCO))
                            for dx, dz, gi in g])


def esquerda_baixo_2():
    """A grade fina em volta da B1 (a altura, a inclinação e a guinada a ±1,25 mm, ±1,25° e ±2,5°): na esquerda_baixo_1
    as reprovadas caem em degraus — a falange média que sobe para a faceta de 52,5° da quina de cima da bomba (a de
    37,5° passa), o mínimo que desce para a de baixo (90°) e a luva que atravessa a si mesma (~2 mm)."""
    g = itertools.product((-63.75, -62.5, -61.25), (-13.75, -12.5, -11.25), (17.5, 20.0, 22.5))
    rodar('nova_eb3', 'e', [((z, i, gu), {**esquerda(z, i, 0.0, gu), **BAIXO}) for z, i, gu in g])


def esquerda_por_cima():
    """A mão de apoio "por cima": girada 180° no plano da face (os dedos para baixo, o polegar da mão esquerda para a
    frente), com a palma subindo para a quina de cima (a inclinação) — a única família em que o polegar deitado na borda
    de cima aponta para a boca sem cruzar a mão (com a palma na face e os dedos para cima, ele aponta para trás)."""
    g = itertools.product((0.0, 15.0), (0.0, -25.0, -45.0))
    rodar('nova_ec', 'e', [((z, i), esquerda(z, i, 180.0, 20.0)) for z, i in g], base='escopeta_borda')
